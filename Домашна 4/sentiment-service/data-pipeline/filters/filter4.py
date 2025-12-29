"""Filter 4: Save data to database."""

import time

import pandas as pd

from .base_filter import Filter


class Filter4(Filter):
    """
    Филтер 4: Пополни база на податоци    
    
    Saves metadata to 'coins_metadata' table and OHLCV data to 'ohlcv_data' table.
    """
    
    order = 4

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Save data to database tables.
        """
        print("Starting Filter 4: Saving to database...")
        start_time = time.time()
        
        # import database utilities here to avoid circular imports
        from database_utils import save_df_to_db, save_csv_to_db
        
        save_df_to_db(df, "coins_metadata")
        
        save_csv_to_db("data/data_to_add.csv", "ohlcv_data", replace=False)
        
        elapsed = time.time() - start_time
        print(f"Filter 4 complete. Execution time: {elapsed:.2f} seconds")
        
        return df
