import os
import re
import sys
import pandas as pd
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Optional
from coinmetrics.api_client import CoinMetricsClient
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.database import DatabaseManager

load_dotenv()


# Strategy interface
class MetricStrategy(ABC):
  
    @abstractmethod
    def collect(self, client: CoinMetricsClient, asset: str, start_date: str) -> Optional[pd.DataFrame]:
        pass

class PoWHashrateStrategy(MetricStrategy):
    def collect(self, client: CoinMetricsClient, asset: str, start_date: str) -> Optional[pd.DataFrame]:
        print(f"Fetching Hashrate for {asset.upper()}...", end=" ")
        try:
            df = client.get_asset_metrics(
                assets=[asset], metrics="HashRate", frequency="1d", start_time=start_date
            ).to_dataframe()
            
            if not df.empty:
                df.rename(columns={'HashRate': 'Security_Value'}, inplace=True)
                df['Metric_Name'] = 'Hashrate (TH/s)'
                # Convert to TH/s
                df['Security_Value'] = df['Security_Value'].astype(float) / 1_000_000_000_000
                print("Done")
                return df
        except Exception:
            pass
       
        return None

class PoSMarketCapStrategy(MetricStrategy):
    def collect(self, client: CoinMetricsClient, asset: str, start_date: str) -> Optional[pd.DataFrame]:
        print(f"Fetching PoS Security (Market Cap) for {asset.upper()}...", end=" ")
        try:
            df = client.get_asset_metrics(
                assets=[asset], metrics="CapMrktCurUSD", frequency="1d", start_time=start_date
            ).to_dataframe()

            if not df.empty:
                df.rename(columns={'CapMrktCurUSD': 'Security_Value'}, inplace=True)
                df['Metric_Name'] = 'PoS Economic Security ($USD)'
                print("Done")
                return df
        except Exception:
            pass
      
        return None

class DefaultMarketCapStrategy(MetricStrategy):
    def collect(self, client: CoinMetricsClient, asset: str, start_date: str) -> Optional[pd.DataFrame]:
        print(f"Fetching Market Cap for {asset.upper()}...", end=" ")
        try:
            df = client.get_asset_metrics(
                assets=[asset], metrics="CapMrktCurUSD", frequency="1d", start_time=start_date
            ).to_dataframe()
        
            if not df.empty:
                df.rename(columns={'CapMrktCurUSD': 'Security_Value'}, inplace=True)
                df['Metric_Name'] = 'Market Cap ($USD)'
                print("Done")
                return df
        except Exception:
            pass
      
        return None



class StrategyFactory:
    POW_COINS = {'btc', 'doge', 'ltc', 'bch', 'kda', 'etc', 'xmr', 'rvn'}
    POS_COINS = {'eth', 'sol', 'bnb', 'sui', 'avax', 'ada', 'algo', 'xtz', 'pol', 'atom'}

    @staticmethod
    def get_strategy(asset: str) -> MetricStrategy:
        if asset in StrategyFactory.POW_COINS:
            return PoWHashrateStrategy()
        elif asset in StrategyFactory.POS_COINS:
            return PoSMarketCapStrategy()
        else:
            return DefaultMarketCapStrategy()


# Fascade
class SecurityDataCollector:
    
    def __init__(self):
        self.client = CoinMetricsClient()
        self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    def _clean_ticker(self, ticker: str) -> Optional[str]:
        if not ticker: return None
        base = ticker.replace("-USD", "").replace("-usd", "")
        base = re.sub(r'\d+', '', base)
        return base.lower()

    def fetch_data(self, raw_assets: List[str]) -> pd.DataFrame:
        if not raw_assets:
            return pd.DataFrame()

        clean_assets = list(set([self._clean_ticker(s) for s in raw_assets if self._clean_ticker(s)]))
        results = []

       

        for asset in clean_assets:
            strategy = StrategyFactory.get_strategy(asset)
            df = strategy.collect(self.client, asset, self.start_date)
            if df is not None:
                results.append(df)

        if results:
            final_df = pd.concat(results)
         
            return final_df[['time', 'asset', 'Metric_Name', 'Security_Value']]
        else:
            print("\nNo data found.")
            return pd.DataFrame()



def get_symbols_from_db() -> List[str]:
    try:
       
        engine = DatabaseManager.get_engine()
        with engine.connect() as conn:
           
            df = pd.read_sql("SELECT DISTINCT unnest(symbols) as symbol FROM news_sentiment", conn)
            symbols = df['symbol'].dropna().tolist()
            return [s for s in symbols if s != 'None']
    except Exception as e:
        print(f"Database Error: {e}")
        return []

if __name__ == "__main__":
    symbols = get_symbols_from_db()
    if symbols:
        collector = SecurityDataCollector()
        df = collector.fetch_data(symbols)
        
        if not df.empty:
            output_file = "network_security_final.csv"
            df.to_csv(output_file, index=False)
            print(f"Saved to {output_file}")
