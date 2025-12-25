import os
import re
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from pathlib import Path
from dotenv import load_dotenv


sys.path.append(str(Path(__file__).parent.parent))
from database.database import DatabaseManager


from collectors_hash import SecurityDataCollector

load_dotenv()


class Config:
    DEFILLAMA_CHAINS_URL = "https://api.llama.fi/v2/chains"
    DEFILLAMA_HISTORICAL_TVL_URL = "https://api.llama.fi/v2/historicalChainTvl"
    TIMEOUT = 15


# Template
class DataCollector(ABC):
  
    def collect(self, symbols: List[str]) -> pd.DataFrame:
        if not symbols:
            return pd.DataFrame()
        
        data = self._fetch_data(symbols)
        return data

    @abstractmethod
    def _fetch_data(self, symbols: List[str]) -> pd.DataFrame:
        pass


class TVLCollector(DataCollector):
    def _fetch_data(self, symbols: List[str]) -> pd.DataFrame:
        dynamic_map = self._build_dynamic_chain_map()
        
        cleaned_symbols = self._clean_symbols(symbols)
        
        matched_chains = {}
        for sym in cleaned_symbols:
            if sym in dynamic_map:
                matched_chains[sym] = dynamic_map[sym]
        
        unique_chains = set(matched_chains.values())
        chain_cache = {}
        
        print(f"Fetching TVL for {len(unique_chains)} chains")
        
        for chain in unique_chains:
            df = self._fetch_historical_tvl(chain)
            if not df.empty:
                chain_cache[chain] = df
            else:
                print(f"No data for {chain}.")
            time.sleep(0.5) 
            
        final_rows = []
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
        
        return pd.DataFrame()

    def _clean_symbols(self, symbols: List[str]) -> List[str]:
        cleaned = []
        for s in symbols:
            if s and s != 'None':
                base = s.replace("-USD", "").replace("-usd", "")
                base = re.sub(r'\d+', '', base)
                cleaned.append(base.upper())
        return list(set(cleaned))

    def _build_dynamic_chain_map(self) -> Dict[str, str]:
        try:
            response = requests.get(Config.DEFILLAMA_CHAINS_URL, timeout=Config.TIMEOUT)
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
            return {}

    def _fetch_historical_tvl(self, chain_name: str) -> pd.DataFrame:
        url = f"{Config.DEFILLAMA_HISTORICAL_TVL_URL}/{chain_name}"
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


# Adapter pattern
class SecurityCollectorAdapter(DataCollector):
   
    def __init__(self):
        self.collector = SecurityDataCollector()

    def _fetch_data(self, symbols: List[str]) -> pd.DataFrame:
        return self.collector.fetch_data(symbols)

# Facade for data aggregation
class CryptoDataAggregator:
   
    def __init__(self):
        self.tvl_collector = TVLCollector()
        self.security_collector = SecurityCollectorAdapter()

    def get_symbols_from_db(self) -> List[str]:
        try:
            engine = DatabaseManager.get_engine()
            with engine.connect() as conn:
                df = pd.read_sql("SELECT DISTINCT unnest(symbols) as symbol FROM news_sentiment", conn)
                symbols = df['symbol'].dropna().tolist()
                return [s for s in symbols if s != 'None']
        except Exception as e:
            print(f"Database Error: {e}")
            return []

    def aggregate(self) -> pd.DataFrame:
        symbols = self.get_symbols_from_db()
        if not symbols:
            print("No symbols found in database.")
            return pd.DataFrame()

        df_tvl = self.tvl_collector.collect(symbols)
        df_security = self.security_collector.collect(symbols)

       
        if df_tvl.empty:
            print("No TVL data found.")
            return pd.DataFrame()

      
        if df_security.empty:
            df_security = pd.DataFrame(columns=['time', 'asset', 'Metric_Name', 'Security_Value'])
        else:
            df_security['time'] = pd.to_datetime(df_security['time'])
            df_security['join_date'] = df_security['time'].dt.date
            df_security['join_symbol'] = df_security['asset'].str.upper()

    
        df_tvl['date'] = pd.to_datetime(df_tvl['date'])
        df_tvl['join_date'] = df_tvl['date'].dt.date
        df_tvl['join_symbol'] = df_tvl['symbol'].str.upper()


        if not df_security.empty:
            merged_df = pd.merge(
                df_tvl,
                df_security,
                on=['join_date', 'join_symbol'],
                how='left'
            )
        else:
            merged_df = df_tvl.copy()
            merged_df['Metric_Name'] = None
            merged_df['Security_Value'] = None

        final_columns = [
            'join_date', 'join_symbol', 'chain', 'tvl_usd', 'Metric_Name', 'Security_Value'
        ]
        
        for col in final_columns:
            if col not in merged_df.columns:
                merged_df[col] = None

        final_df = merged_df[final_columns].copy()
        final_df.rename(columns={
            'join_date': 'date',
            'join_symbol': 'symbol',
            'Metric_Name': 'security_metric',
            'Security_Value': 'security_value'
        }, inplace=True)

        final_df = final_df.fillna(0)
        final_df['symbol'] = final_df['symbol'].apply(lambda x: f"{x}-USD" if not str(x).endswith("-USD") else x)
        final_df.sort_values(by=['symbol', 'date'], inplace=True)

        return final_df

if __name__ == "__main__":
    aggregator = CryptoDataAggregator()
    df = aggregator.aggregate()
    
    if not df.empty:
        output_file = "joined_crypto_data.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSaved to {output_file}")
