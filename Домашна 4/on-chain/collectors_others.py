import os
import math
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import pandas as pd
import requests
import san
from sqlalchemy import create_engine, Engine
from dotenv import load_dotenv

# Logging allows us to track the flow and issues
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    API_KEY = os.getenv("API_KEY")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    SANTIMENT_URL = "https://api.santiment.net/graphql"
    TOTAL_DAYS = 365
    WINDOW_DAYS = 30
    IGNORE_TICKERS = {"SUI20947-USD", "HBAR-USD"}
    MISSING_COLUMNS_THRESHOLD = 2

class DatabaseManager:
    _engine: Optional[Engine] = None

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is not None:
            return cls._engine

        if not all([Config.DB_USER, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME]):
            raise RuntimeError("Database credentials are missing.")

        encoded_password = quote_plus(Config.DB_PASSWORD)
        connection_str = f"postgresql://{Config.DB_USER}:{encoded_password}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
        
        cls._engine = create_engine(connection_str, pool_size=10, max_overflow=20)
        return cls._engine

class SantimentFacade:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Apikey {api_key}",
            "Content-Type": "application/json"
        }

    def _execute_query(self, query: str, variables: Dict) -> Optional[Dict]:
        attempts = 0
        while attempts < 3:
            try:
                response = requests.post(
                    Config.SANTIMENT_URL, 
                    headers=self.headers, 
                    json={"query": query, "variables": variables}
                )
                
                if response.status_code == 429:
                    logger.warning("Rate limit hit. Sleeping 60s...")
                    time.sleep(60)
                    attempts += 1
                    continue
                
                if response.status_code != 200:
                    logger.warning(f"API returned status {response.status_code}. Retrying...")
                    attempts += 1
                    time.sleep(10)
                    continue

                return response.json().get("data", {})
            except Exception as e:
                logger.error(f"Exception during API call: {e}")
                attempts += 1
                time.sleep(5)
        return None

    def _extract_timeseries(self, data: Dict, metric_name: str) -> List[Dict]:
        metric_data = data.get(metric_name)
        return metric_data.get("timeseriesData", []) if metric_data else []

    def fetch_metrics_for_slug(self, slug: str) -> Optional[pd.DataFrame]:
        today = datetime.now(timezone.utc)
        start_date = today - timedelta(days=Config.TOTAL_DAYS)
        num_windows = math.ceil(Config.TOTAL_DAYS / Config.WINDOW_DAYS)
        
        dfs = []

        query = """
        query($slug: String!, $from: DateTime!, $to: DateTime!) {
          active_addresses: getMetric(metric: "daily_active_addresses") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          transactions_count: getMetric(metric: "transactions_count") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          exchange_inflow: getMetric(metric: "exchange_inflow") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          exchange_outflow: getMetric(metric: "exchange_outflow") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          whale_transactions: getMetric(metric: "whale_transaction_count_100k_usd_to_inf") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          nvt_ratio: getMetric(metric: "nvt") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
          mvrv_ratio: getMetric(metric: "mvrv_usd") {
            timeseriesData(slug: $slug, from: $from, to: $to, interval: "1d") { datetime, value }
          }
        }
        """

        for i in range(num_windows):
            window_start = start_date + timedelta(days=i * Config.WINDOW_DAYS)
            window_end = window_start + timedelta(days=Config.WINDOW_DAYS - 1)
            
            # Ensure we don't go into the future
            if window_end > today:
                window_end = today
            if window_start >= today:
                break

            variables = {
                "slug": slug,
                "from": window_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "to": window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            data = self._execute_query(query, variables)
            if not data:
                continue

            # Process data into DataFrame
            base_metric = self._extract_timeseries(data, "active_addresses") or \
                          self._extract_timeseries(data, "transactions_count")
            
            if base_metric:
                dates = [x["datetime"] for x in base_metric]
                
                def get_vals(key):
                    raw = self._extract_timeseries(data, key)
                    lookup = {item['datetime']: item['value'] for item in raw}
                    return [lookup.get(d, None) for d in dates]

                df_window = pd.DataFrame({
                    "datetime": dates,
                    "active_addresses": get_vals("active_addresses"),
                    "transactions": get_vals("transactions_count"),
                    "exchange_inflow": get_vals("exchange_inflow"),
                    "exchange_outflow": get_vals("exchange_outflow"),
                    "whale_transactions": get_vals("whale_transactions"),
                    "nvt_ratio": get_vals("nvt_ratio"),
                    "mvrv_ratio": get_vals("mvrv_ratio")
                })
                dfs.append(df_window)
            
            # Respect API limits
            time.sleep(1) # Small delay between windows

        if not dfs:
            return None

        all_data = pd.concat(dfs, ignore_index=True)
        all_data.drop_duplicates(subset=['datetime'], inplace=True)
        all_data.sort_values('datetime', inplace=True)
        return all_data

class OnChainDataService:
    def __init__(self):
        self.api = SantimentFacade(Config.API_KEY)
        self.db = DatabaseManager.get_engine()

    def get_target_tickers(self) -> List[str]:
        query = "SELECT symbols FROM news_sentiment"
        with self.db.connect() as conn:
            df = pd.read_sql(query, conn)

        tickers = set()
        for symbols_array in df["symbols"]:
            if symbols_array:
                for symbol in symbols_array:
                    if symbol not in Config.IGNORE_TICKERS:
                        tickers.add(symbol)
        
        logger.info(f"Found {len(tickers)} unique tickers.")
        return sorted(list(tickers))

    def _map_tickers_to_slugs(self, tickers: List[str]) -> Dict[str, str]:
        # Fetch all projects once
        df_projects = san.get("projects/all")
        
        tickers_to_slugs = {}
        for ticker in tickers:
            symbol = ticker.split("-")[0]
            # Find matching project with non-zero activity
            match = df_projects[
                (df_projects["ticker"] == symbol) & 
                df_projects.iloc[:, -1].notna() & 
                (df_projects.iloc[:, -1] != 0)
            ]
            
            if match.empty:
                logger.warning(f"Could not find valid slug for {ticker}")
                continue
            
            tickers_to_slugs[ticker] = match.iloc[0]["slug"]
        
        return tickers_to_slugs

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["exchange_inflow"] = pd.to_numeric(df["exchange_inflow"], errors='coerce')
        df["exchange_outflow"] = pd.to_numeric(df["exchange_outflow"], errors='coerce')
        df["net_flow"] = df["exchange_inflow"].fillna(0) - df["exchange_outflow"].fillna(0)
        
        # Check for too many missing columns
        missing_cols = df.isna().sum()
        if sum(missing_cols > 0) > Config.MISSING_COLUMNS_THRESHOLD:
            raise ValueError("Too many missing columns")

        df.fillna(0, inplace=True)
        return df

    def run(self):
        tickers = self.get_target_tickers()
        ticker_map = self._map_tickers_to_slugs(tickers)
        
        all_results = []
        
        for ticker, slug in ticker_map.items():
            logger.info(f"Fetching data for {ticker} ({slug})...")
            raw_df = self.api.fetch_metrics_for_slug(slug)
            
            if raw_df is not None:
                try:
                    clean_df = self.process_data(raw_df)
                    clean_df['ticker'] = ticker
                    all_results.append(clean_df)
                except ValueError as e:
                    logger.warning(f"Skipping {slug}: {e}")
            
            time.sleep(2) # Respect generic rate limits

        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            final_df.sort_values(['ticker', 'datetime'], inplace=True)
            final_df.to_csv("onchain_all.csv", index=False)
            logger.info(f"Successfully saved {len(final_df)} rows to onchain_all.csv")
        else:
            logger.info("No data collected.")
        
    def fetch_data_as_dataframe(self) -> pd.DataFrame:
        tickers = self.get_target_tickers()
        ticker_map = self._map_tickers_to_slugs(tickers)
        all_results = []
        
        for ticker, slug in ticker_map.items():
            logger.info(f"Fetching data for {ticker}...")
            raw_df = self.api.fetch_metrics_for_slug(slug)
            if raw_df is not None:
                try:
                    clean_df = self.process_data(raw_df)
                    clean_df['ticker'] = ticker
                    all_results.append(clean_df)
                except ValueError:
                    continue
        
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            return final_df
        return pd.DataFrame()

if __name__ == "__main__":
    service = OnChainDataService()
    service.run()