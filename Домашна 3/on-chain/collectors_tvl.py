import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import time
import re

load_dotenv()

DEFILLAMA_CHAINS_URL = "https://api.llama.fi/v2/chains"
DEFILLAMA_HISTORICAL_TVL_URL = "https://api.llama.fi/v2/historicalChainTvl"

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
        
        cleaned = []
        for s in symbols:
            if s and s != 'None':
               
                base = s.replace("-USD", "").replace("-usd", "")
                base = re.sub(r'\d+', '', base)
                cleaned.append(base.upper())
        return list(set(cleaned))
    except Exception as e:
        print(f"Error fetching from DB: {e}")
        return []

def build_dynamic_chain_map():
    print("Fetching global chain list from DefiLlama")
    try:
        response = requests.get(DEFILLAMA_CHAINS_URL, timeout=15)
        response.raise_for_status()
        all_chains = response.json()
        
        token_to_chain = {}
    
        for chain in all_chains:
            chain_name = chain.get('name')
            token_symbol = chain.get('tokenSymbol')
            
            if chain_name and token_symbol:
                token_symbol = token_symbol.upper()
                
                if token_symbol in token_to_chain:
                   
                    if chain_name.upper() == token_symbol:
                        token_to_chain[token_symbol] = chain_name
                else:
                    token_to_chain[token_symbol] = chain_name
                    
        return token_to_chain
        
    except Exception as e:
        print(f"Error building chain map: {e}")
        return {}

def fetch_historical_tvl(chain_name):
    url = f"{DEFILLAMA_HISTORICAL_TVL_URL}/{chain_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        data = response.json()
        df = pd.DataFrame(data)
        
        if df.empty: return df
        
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df.rename(columns={'tvl': 'tvl_usd'}, inplace=True)
        
        cutoff = datetime.now() - timedelta(days=365)
        df = df[df['date'] >= cutoff].copy()
        return df
    except Exception:
        return pd.DataFrame()

def get_tvl_data():
    symbols = get_symbols_from_db()
    if not symbols: return pd.DataFrame()
    
    dynamic_map = build_dynamic_chain_map()
   
    matched_chains = {}
    for sym in symbols:
        if sym in dynamic_map:
            chain_name = dynamic_map[sym]
            matched_chains[sym] = chain_name
       
    final_rows = []
    unique_chains = set(matched_chains.values())
    chain_cache = {}

    print(f"\nFetching TVL for {len(unique_chains)} chains")
    
    for chain in unique_chains:
        df = fetch_historical_tvl(chain)
        if not df.empty:
            chain_cache[chain] = df
            print(f"found {len(df)} records.")
        else:
            print("no data")
        time.sleep(0.5)
        
    for sym, chain in matched_chains.items():
        if chain in chain_cache:
            df = chain_cache[chain].copy()
            df['symbol'] = sym
            df['chain'] = chain
            final_rows.append(df)

    if final_rows:
        final_df = pd.concat(final_rows, ignore_index=True)
        final_df = final_df[['date', 'symbol', 'chain', 'tvl_usd']]
        final_df.sort_values(by=['symbol', 'date'], inplace=True)
        
        return final_df
    else:
        print("\nNo data found.")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_tvl_data()
    if not df.empty:
        output_file = "tvl_auto_mapped.csv"
        df.to_csv(output_file, index=False)
        print(f"\nData saved to {output_file}")