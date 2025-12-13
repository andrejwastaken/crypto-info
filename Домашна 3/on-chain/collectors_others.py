import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import timedelta, datetime
import math
import time
import san
from sqlalchemy import create_engine, text

url = "https://api.santiment.net/graphql"
API_KEY = os.getenv("API_KEY")
load_dotenv()

_db_engine = None

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

def init_db():
    engine = get_engine()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS on_chain_sentiment_predictions (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        date DATE NOT NULL,
        predicted_close NUMERIC,
        predicted_change_pct NUMERIC
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("Database table 'on_chain_sentiment_predictions' checked/created.")

df = san.get("projects/all")

def get_all_tickers():
    engine = get_engine()
    query = "SELECT symbols FROM news_sentiment"

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    tickers = set()

    for symbols_array in df["symbols"]:
        if symbols_array is None:
            continue
        tickers.update(symbols_array)

    return sorted(tickers)

tickers_to_slugs = {}

for ticker in get_all_tickers():
    symbol = ticker.split("-")[0]

    match = df[
        (df["ticker"] == symbol) &
        df.iloc[:, -1].notna() &
        (df.iloc[:, -1] != 0)
    ]

    if match.empty:
        print(f"Warning: Could not find valid slug for {ticker}")
        continue

    tickers_to_slugs[ticker] = match.iloc[0]["slug"]

slugs = list(tickers_to_slugs.values())
slug_to_ticker = {v: k for k, v in tickers_to_slugs.items()}

print(f"Fetching data for: {slugs}")

total_days = 365 # API limit lookback 
window_days = 30 # days per request (to avoid overload)
num_windows = math.ceil(total_days / window_days) # number of windows needed

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

def safe_extract_metric(data, metric_name):
    metric = data.get(metric_name)
    if not metric:
        return []

    ts = metric.get("timeseriesData")
    if not ts:
        return []

    return ts

for ticker, slug in tickers_to_slugs.items():
    slug_dfs = []
    print(f"--- Processing {slug} ({ticker}) ---")
    
    today = datetime.utcnow()
    # hard stop date, because api only allows last 365 - 30 days
    cutoff_date = today - timedelta(days=30)
    start_date = cutoff_date - timedelta(days=total_days)

    for i in range(num_windows):
        window_start = start_date + timedelta(days=i * window_days)
        window_end = window_start + timedelta(days=window_days - 1)

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
                    print(f"Rate Limit hit. Sleeping for 60 seconds...")
                    time.sleep(60) # Must be long for Santiment free tier
                    attempts += 1
                    continue
                
                if response.status_code != 200:
                    print(f"HTTP Error: {response.status_code}")
                    break # Fatal error
                
                result = response.json()
            
                data = result.get("data", {})
                if not data:
                    print("No data returned.")
                    break

                base_metric = safe_extract_metric(data, "active_addresses")
                if not base_metric:
                     base_metric = safe_extract_metric(data, "transactions_count")
                
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
                        "whale_transactions": get_vals("whale_transactions")
                    })

                    df["nvt_ratio"] = get_vals("nvt_ratio")
                    df["mvrv_ratio"] = get_vals("mvrv_ratio")
                    df["net_flow"] = df.apply(lambda r: (r["exchange_inflow"] or 0) - (r["exchange_outflow"] or 0), axis=1)
                    
                    slug_dfs.append(df)
                    success = True
                    print(f"Window {i} done ({len(df)} rows)")
                else:
                    success = True 
            
            except Exception as e:
                print(f"Exception: {e}")
                attempts += 1
                time.sleep(5)

        time.sleep(2)

    if slug_dfs:
        all_data = pd.concat(slug_dfs, ignore_index=True)
        all_data.drop_duplicates(subset=['datetime'], inplace=True)
        all_data.sort_values('datetime', inplace=True)
        
        filename = f"{ticker}_onchain.csv"
        all_data.to_csv(filename, index=False)
        print(f"Saved {filename} ({len(all_data)} rows)")
    else:
        print(f"No data saved for {slug}")