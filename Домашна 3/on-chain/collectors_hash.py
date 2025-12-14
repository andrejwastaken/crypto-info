import os
import re
import pandas as pd
from datetime import datetime, timedelta
from coinmetrics.api_client import CoinMetricsClient
import psycopg2
from dotenv import load_dotenv

load_dotenv()

POW_COINS = {'btc', 'doge', 'ltc', 'bch', 'kda', 'etc', 'xmr', 'rvn'}
POS_COINS = {'eth', 'sol', 'bnb', 'sui', 'avax', 'ada', 'algo', 'xtz', 'pol', 'atom'}

def clean_ticker(ticker):
    if not ticker: return None
    base = ticker.replace("-USD", "").replace("-usd", "")
    base = re.sub(r'\d+', '', base)
    return base.lower()

def get_symbols_from_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "crypto_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT unnest(symbols) FROM news_sentiment;")
        symbols = [row[0] for row in cursor.fetchall()]
        conn.close()
        return [s for s in symbols if s and s != 'None']
    except Exception:
        return []

def fetch_security_data(assets):
    if not assets: 
        return

    client = CoinMetricsClient()
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    clean_assets = list(set([clean_ticker(s) for s in assets]))
    results = []

    print(f"\nProcessing {len(clean_assets)} assets using Free Tier metrics...\n")

    for asset in clean_assets:
        try:
            if asset in POW_COINS:
                print(f"Fetching Hashrate for {asset.upper()}...", end=" ")
                df = client.get_asset_metrics(
                    assets=[asset], metrics="HashRate", frequency="1d", start_time=start_date
                ).to_dataframe()
                
                if not df.empty:
                    df.rename(columns={'HashRate': 'Security_Value'}, inplace=True)
                    df['Metric_Name'] = 'Hashrate (TH/s)'
                    df['Security_Value'] = df['Security_Value'].astype(float) / 1_000_000_000_000
                    results.append(df)
                    print("Done")
                else:
                    print("No Data")

            elif asset in POS_COINS:
                print(f"Fetching Market Cap (Security Proxy) for {asset.upper()}...", end=" ")
                df = client.get_asset_metrics(
                    assets=[asset], metrics="CapMrktCurUSD", frequency="1d", start_time=start_date
                ).to_dataframe()

                if not df.empty:
                    df.rename(columns={'CapMrktCurUSD': 'Security_Value'}, inplace=True)
                    df['Metric_Name'] = 'PoS Economic Security ($USD)'
                    results.append(df)
                    print("Done")
                else:
                    print("No Data")

            else:
                print(f"Fetching Market Cap for {asset.upper()}...", end=" ")
                try:
                    df = client.get_asset_metrics(
                        assets=[asset], metrics="CapMrktCurUSD", frequency="1d", start_time=start_date
                    ).to_dataframe()
                
                    if not df.empty:
                        df.rename(columns={'CapMrktCurUSD': 'Security_Value'}, inplace=True)
                        df['Metric_Name'] = 'Market Cap ($USD)'
                        results.append(df)
                        print("Done")
                    else:
                        print("No data")
                except:
                    print("Skipped")

        except Exception as e:
            print(f"Error on {asset}: {e}")

    if results:
        final_df = pd.concat(results)
        final_df = final_df[['time', 'asset', 'Metric_Name', 'Security_Value']]
        return final_df
    else:
        print("\nNo data found.")
        return pd.DataFrame()

if __name__ == "__main__":
    symbols = get_symbols_from_db()
    if symbols:
        df = fetch_security_data(symbols)
        if not df.empty:
            df.to_csv("network_security_final.csv", index=False)
            print("Saved to network_security_final.csv")