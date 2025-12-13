import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import timedelta, datetime
import math
import time
from sqlalchemy import create_engine, text
import san

load_dotenv()
API_KEY = os.getenv("API_KEY")
url = "https://api.santiment.net/graphql"

_db_engine = None
TOTAL_DAYS = 365
WINDOW_DAYS = 30

def get_engine():
    global _db_engine
    if _db_engine is not None:
        return _db_engine

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_port, db_name]):
        raise RuntimeError("Database credentials are missing.")

    encoded_password = quote_plus(db_password)
    connection_str = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    _db_engine = create_engine(connection_str, pool_size=10, max_overflow=20)
    return _db_engine



def get_all_tickers():
    engine = get_engine()
    query = "SELECT symbols FROM news_sentiment"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    tickers = set()
    for symbols_array in df["symbols"]:
        if symbols_array:
            tickers.update(symbols_array)
    return sorted(tickers)

def map_tickers_to_slugs(tickers, df_projects):
    tickers_to_slugs = {}
    for ticker in tickers:
        symbol = ticker.split("-")[0]
        match = df_projects[(df_projects["ticker"] == symbol) & df_projects.iloc[:, -1].notna() & (df_projects.iloc[:, -1] != 0)]
        if match.empty:
            print(f"Warning: Could not find valid slug for {ticker}")
            continue
        tickers_to_slugs[ticker] = match.iloc[0]["slug"]
    return tickers_to_slugs

def safe_extract_metric(data, metric_name):
    metric = data.get(metric_name)
    if not metric:
        return []
    ts = metric.get("timeseriesData")
    return ts if ts else []

def fetch_slug_data(slug):
    slug_dfs = []
    today = datetime.utcnow()
    cutoff_date = today - timedelta(days=30)
    start_date = cutoff_date - timedelta(days=TOTAL_DAYS)
    num_windows = math.ceil(TOTAL_DAYS / WINDOW_DAYS)

    headers = {
        "Authorization": f"Apikey {API_KEY}",
        "Content-Type": "application/json"
    }

    query_full = """
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
        window_start = start_date + timedelta(days=i * WINDOW_DAYS)
        window_end = window_start + timedelta(days=WINDOW_DAYS - 1)
        if window_end > cutoff_date:
            window_end = cutoff_date
        if window_start >= cutoff_date:
            break

        variables = {
            "slug": slug,
            "from": window_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                response = requests.post(url, headers=headers, json={"query": query_full, "variables": variables})
                if response.status_code == 429:
                    print(f"Rate limit hit. Sleeping 60s...")
                    time.sleep(60)
                    attempts += 1
                    continue
                if response.status_code != 200:
                    print(f"HTTP Error: {response.status_code}")
                    break
                data = response.json().get("data", {})
                base_metric = safe_extract_metric(data, "active_addresses") or safe_extract_metric(data, "transactions_count")
                if base_metric:
                    dates = [x["datetime"] for x in base_metric]
                    def get_vals(key):
                        raw = safe_extract_metric(data, key)
                        lookup = {item['datetime']: item['value'] for item in raw}
                        return [lookup.get(d, None) for d in dates]

                    df = pd.DataFrame({
                        "datetime": dates,
                        "active_addresses": get_vals("active_addresses"),
                        "transactions": get_vals("transactions_count"),
                        "exchange_inflow": get_vals("exchange_inflow"),
                        "exchange_outflow": get_vals("exchange_outflow"),
                        "whale_transactions": get_vals("whale_transactions"),
                        "nvt_ratio": get_vals("nvt_ratio"),
                        "mvrv_ratio": get_vals("mvrv_ratio")
                    })
                    df["net_flow"] = df["exchange_inflow"].fillna(0) - df["exchange_outflow"].fillna(0)

                    slug_dfs.append(df)
                success = True
            except Exception as e:
                print(f"Exception: {e}")
                attempts += 1
                time.sleep(5)
        time.sleep(2)

    if not slug_dfs:
        return None

    all_data = pd.concat(slug_dfs, ignore_index=True)
    all_data.drop_duplicates(subset=['datetime'], inplace=True)
    # Filter to cutoff date (last 30 days) just in case
    all_data = all_data[all_data['datetime'] <= cutoff_date.strftime("%Y-%m-%dT%H:%M:%SZ")]
    all_data.sort_values('datetime', inplace=True)

    # Check missing data columns
    missing_cols = all_data.isna().sum()
    if sum(missing_cols > 0) > 2:
        print(f"Skipping slug {slug} due to >2 columns missing data")
        return None

    all_data.fillna(0, inplace=True)
    return all_data

def get_santiment_data():
    df_projects = san.get("projects/all")
    tickers = get_all_tickers()
    tickers_to_slugs = map_tickers_to_slugs(tickers, df_projects)

    all_results = []
    for ticker, slug in tickers_to_slugs.items():
        print(f"Fetching data for {ticker} ({slug})")
        df = fetch_slug_data(slug)
        if df is not None:
            df['ticker'] = ticker
            all_results.append(df)

    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        final_df.sort_values(['ticker', 'datetime'], inplace=True)
        return final_df
    else:
        print("No data to save.")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_santiment_data()
    if not df.empty:
        df.to_csv("onchain_all.csv", index=False)
        print(f"Saved combined CSV with {len(df)} rows")
