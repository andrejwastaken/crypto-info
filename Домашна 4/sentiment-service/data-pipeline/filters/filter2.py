import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import List, Dict

import pandas as pd

from .base_filter import Filter
from .data_utils import download_ohlcv_data


OUTPUT_DIR = "data"
MAX_WORKERS = 70
DOWNLOAD_DELAY = 0.15

os.makedirs(OUTPUT_DIR, exist_ok=True)


class Filter2(Filter):
    """
    Филтер 2: Проверете го последниот датум на достапни податоци
    
    Downloads full history (period="max") for new coins.
    """
    
    order = 2

    def split_into_chunks(self, data: List[Dict], num_chunks: int) -> List[List[Dict]]:
        if not data:
            return []
        
        chunk_size = max(1, (len(data) + num_chunks - 1) // num_chunks)
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    def process_group(self, group_idx: int, coins: List[Dict]) -> pd.DataFrame:
        group_dfs = []
        
        for coin in coins:
            df = download_ohlcv_data(coin, period="max")
            if not df.empty:
                group_dfs.append(df)
            time.sleep(DOWNLOAD_DELAY)
        
        return pd.concat(group_dfs, ignore_index=True) if group_dfs else pd.DataFrame()

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Download historical data for new coins.
        """
        print("Starting Filter 2: Downloading historical data...")
        start_time = time.time()
        
        # ensure updated_at column exists
        if 'updated_at' not in df.columns:
            df['updated_at'] = None
        
        # import database utility here to avoid circular imports
        from database_utils import check_and_update_metadata
        df = check_and_update_metadata(df)
        
        # only fetch data for coins NOT in database
        coins_to_download = df[df['updated_at'].isna()]
        
        if coins_to_download.empty:
            print("All coins already have data. Skipping Filter 2.")
            return df
        
        print(f"Fetching historical data for {len(coins_to_download)} coins...")
        
        # split into groups for parallel processing
        data_list = coins_to_download.to_dict(orient="records")
        groups = self.split_into_chunks(data_list, MAX_WORKERS)
        
        # download in parallel
        all_dfs = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.process_group, idx, grp) 
                for idx, grp in enumerate(groups)
            ]
            
            for future in as_completed(futures):
                result = future.result()
                if not result.empty:
                    all_dfs.append(result)
        
        # save downloaded data
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            output_path = os.path.join(OUTPUT_DIR, "data_to_add.csv")
            final_df.to_csv(output_path, index=False)
            
            # update metadata for successfully downloaded coins
            successful_symbols = final_df['symbol'].unique()
            df.loc[df['symbol'].isin(successful_symbols), 'updated_at'] = date.today()
            
            print(f"Downloaded data for {len(successful_symbols)} coins")
        else:
            print("No new data downloaded.")
        
        elapsed = time.time() - start_time
        print(f"Filter 2 complete. Execution time: {elapsed:.2f} seconds")
        
        return df
