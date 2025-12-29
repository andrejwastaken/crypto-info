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
from coinmetrics.api_client import CoinMetricsClient

sys.path.append(str(Path(__file__).parent.parent))
from database.database import DatabaseManager

load_dotenv()

POW_COINS = {'btc', 'doge', 'ltc', 'bch', 'kda', 'etc', 'xmr', 'rvn'}
POS_COINS = {'eth', 'sol', 'bnb', 'sui', 'avax', 'ada', 'algo', 'xtz', 'pol', 'atom'}

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
        
    
        
        for chain in unique_chains:
            df = self._fetch_historical_tvl(chain)
            if not df.empty:
                chain_cache[chain] = df
                print(f"Found {len(df)} records for {chain}.")
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


# Strategy
class MetricStrategy(ABC):
  
    def __init__(self, client: CoinMetricsClient):
        self.client = client

    @abstractmethod
    def fetch_metric(self, asset: str, start_date: str) -> pd.DataFrame:
        pass

class HashRateStrategy(MetricStrategy):
    
    def fetch_metric(self, asset: str, start_date: str) -> pd.DataFrame:
        try:
            data = self.client.get_asset_metrics(
                assets=asset,
                metrics="HashRate",
                frequency="1d",
                start_time=start_date
            ).to_dataframe()
            if not data.empty:
                data.rename(columns={'HashRate': 'security_value'}, inplace=True)
                data['metric_name'] = 'Hashrate (TH/s)'
               
                data['security_value'] = data['security_value'].astype(float) / 1_000_000_000_000
            return data
        except Exception:
            return pd.DataFrame()

class PoSMarketCapStrategy(MetricStrategy):
    
    def fetch_metric(self, asset: str, start_date: str) -> pd.DataFrame:
        try:
            data = self.client.get_asset_metrics(
                assets=asset,
                metrics="CapMrktCurUSD",
                frequency="1d",
                start_time=start_date
            ).to_dataframe()
            if not data.empty:
                data.rename(columns={'CapMrktCurUSD': 'security_value'}, inplace=True)
                data['metric_name'] = 'PoS Economic Security ($USD)'
            return data
        except Exception:
            return pd.DataFrame()

class DefaultMarketCapStrategy(MetricStrategy):
   
    def fetch_metric(self, asset: str, start_date: str) -> pd.DataFrame:
        try:
            data = self.client.get_asset_metrics(
                assets=asset,
                metrics="CapMrktCurUSD",
                frequency="1d",
                start_time=start_date
            ).to_dataframe()
            if not data.empty:
                data.rename(columns={'CapMrktCurUSD': 'security_value'}, inplace=True)
                data['metric_name'] = 'Market Cap ($USD)'
            return data
        except Exception:
            return pd.DataFrame()

# Factory 

class StrategyFactory:
   
    def __init__(self, client: CoinMetricsClient):
        self.client = client

    def get_strategy(self, asset: str) -> MetricStrategy:
        asset_lower = asset.lower()
        if asset_lower in POW_COINS:
            return HashRateStrategy(self.client)
        elif asset_lower in POS_COINS:
            return PoSMarketCapStrategy(self.client)
        else:
            
            return DefaultMarketCapStrategy(self.client)



# Fascade
class SecurityDataCollector:
   
    def __init__(self):
        self.client = CoinMetricsClient()
        self.factory = StrategyFactory(self.client)

    def _clean_ticker(self, ticker: str) -> Optional[str]:
        if not ticker: return None
        base = ticker.replace("-USD", "").replace("-usd", "")
        base = re.sub(r'\d+', '', base)
        return base.lower()

    def fetch_data(self, raw_symbols: List[str]) -> pd.DataFrame:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        clean_assets = list(set([self._clean_ticker(s) for s in raw_symbols if self._clean_ticker(s)]))
        
        results = []
        print(f"Fetching security data for {len(clean_assets)} assets...")

        for asset in clean_assets:
            strategy = self.factory.get_strategy(asset)
            
            try:
                df = strategy.fetch_metric(asset, start_date)
                if not df.empty:
                    results.append(df)
            except Exception as e:
                print(f"Error fetching data for {asset}: {e}")

        if results:
            final_df = pd.concat(results, ignore_index=True)
        
            if 'time' in final_df.columns:
                final_df['time'] = pd.to_datetime(final_df['time'])
            return final_df
        
        return pd.DataFrame()

# Adapter
class SecurityCollectorAdapter(DataCollector):
  
    def __init__(self):
        self.collector = SecurityDataCollector()

    def _fetch_data(self, symbols: List[str]) -> pd.DataFrame:
        return self.collector.fetch_data(symbols)


# Fascade
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

        if df_tvl.empty and df_security.empty:
            print("No data found from either source.")
            return pd.DataFrame()

        if not df_security.empty:
            df_security['time'] = pd.to_datetime(df_security['time'])
            df_security['join_date'] = df_security['time'].dt.date
            df_security['join_symbol'] = df_security['asset'].str.upper()

        if not df_tvl.empty:
            df_tvl['date'] = pd.to_datetime(df_tvl['date'])
            df_tvl['join_date'] = df_tvl['date'].dt.date
            df_tvl['join_symbol'] = df_tvl['symbol'].str.upper()

        if not df_tvl.empty and not df_security.empty:
            merged_df = pd.merge(
                df_tvl,
                df_security,
                on=['join_date', 'join_symbol'],
                how='outer'
            )
            merged_df['date'] = merged_df['date'].fillna(merged_df['time'])
            merged_df['symbol'] = merged_df['symbol'].fillna(merged_df['asset'])
            
        elif not df_tvl.empty:
            merged_df = df_tvl.copy()
            merged_df['metric_name'] = None
            merged_df['security_value'] = None
        else: 
            merged_df = df_security.copy()
            merged_df['date'] = merged_df['time']
            merged_df['symbol'] = merged_df['asset']
            merged_df['chain'] = None
            merged_df['tvl_usd'] = None

        
        final_columns = [
            'join_date', 'join_symbol', 'chain', 'tvl_usd', 'metric_name', 'security_value'
        ]
        
        for col in final_columns:
            if col not in merged_df.columns:
                merged_df[col] = None

        final_df = merged_df[final_columns].copy()
        final_df.rename(columns={
            'join_date': 'date',
            'join_symbol': 'symbol',
            
        }, inplace=True)

        
        final_df['tvl_usd'] = final_df['tvl_usd'].fillna(0)
        final_df['security_value'] = final_df['security_value'].fillna(0)

    
        final_df['symbol'] = final_df['symbol'].apply(lambda x: f"{x}-USD" if x and not str(x).endswith("-USD") else x)
        
        
        final_df.dropna(subset=['date', 'symbol'], inplace=True)
        
        final_df.sort_values(by=['symbol', 'date'], inplace=True)

        return final_df

if __name__ == "__main__":
    aggregator = CryptoDataAggregator()
    df = aggregator.aggregate()
    
    if not df.empty:
        output_file = "joined_crypto_data.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSaved to {output_file}")
