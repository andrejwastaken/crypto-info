import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import List, Dict

import pandas as pd

from .base_filter import Filter
from .data_utils import download_ohlcv_data


OUTPUT_DIR = "data"
MAX_WORKERS = 10
COINS_PER_THREAD = 100
DOWNLOAD_DELAY = 0.15

os.makedirs(OUTPUT_DIR, exist_ok=True)

class Filter3(Filter):
    """
    Филтер 3: Пополнете ги податоците што недостасуваат
    
    For coins updated recently (< 30 days), only fetches 1 month of data.
    For others, fetches maximum available history.
    """
    
    order = 3

    def determine_period(self, updated_at) -> str:
        """Determine optimal period to fetch based on last update date."""
        if pd.isna(updated_at):
            return "max"
        
        # normalize to date object
        if isinstance(updated_at, str):
            try:
                updated_at = pd.to_datetime(updated_at).date()
            except:
                return "max"
        elif isinstance(updated_at, pd.Timestamp):
            updated_at = updated_at.date()
        
        # if recent update, only fetch 1 month
        if isinstance(updated_at, date):
            days_since_update = (date.today() - updated_at).days
            return "1mo" if days_since_update < 30 else "max"
        
        return "max"

    def process_group(self, group_idx: int, coins: List[Dict]) -> pd.DataFrame:
        """Download data for a group of coins with appropriate periods."""
        group_dfs = []
        
        for coin in coins:
            period = self.determine_period(coin.get('updated_at'))
            df = download_ohlcv_data(coin, period=period)
            
            if not df.empty:
                group_dfs.append(df)
            
            time.sleep(DOWNLOAD_DELAY)
        
        return pd.concat(group_dfs, ignore_index=True) if group_dfs else pd.DataFrame()

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Update coins with recent data.
        """
        print("Starting Filter 3: Updating coin data...")
        start_time = time.time()
        
        today = date.today()
        
        # find coins that need updating (not updated today)
        if 'updated_at' not in df.columns:
            coins_to_update = df.copy()
        else:
            coins_to_update = df[df['updated_at'] != today]
        
        if coins_to_update.empty:
            print("All coins are up to date. Skipping Filter 3.")
            return df
        
        print(f"Updating data for {len(coins_to_update)} coins...")
        
        # split into chunks for parallel processing
        data_list = coins_to_update.to_dict(orient="records")
        chunk_size = COINS_PER_THREAD
        chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]
        chunks = chunks[:MAX_WORKERS] 
        
        # download in parallel
        all_dfs = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.process_group, idx, grp) 
                for idx, grp in enumerate(chunks)
            ]
            
            for future in as_completed(futures):
                result = future.result()
                if not result.empty:
                    all_dfs.append(result)
        
        # append to existing data file
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            output_path = os.path.join(OUTPUT_DIR, "data_to_add.csv")
            
            # append with header only if file doesn't exist
            write_header = not os.path.exists(output_path)
            final_df.to_csv(output_path, mode='a', header=write_header, index=False)
            
            # update metadata for successfully processed coins
            processed_symbols = final_df['symbol'].unique()
            df.loc[df['symbol'].isin(processed_symbols), 'updated_at'] = today
            
            print(f"Updated data for {len(processed_symbols)} coins")
        else:
            print("No data downloaded in Filter 3.")
        
        elapsed = time.time() - start_time
        print(f"Filter 3 complete. Execution time: {elapsed:.2f} seconds")
        
        return df
