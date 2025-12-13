import pandas as pd
import os
from join_collectors_hash_tvl import join_csvs as get_tvl_security_data
from collectors_others import get_santiment_data
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
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

_db_engine=None
load_dotenv()

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




def combine_all_onchain_data():



    df_tvl_security = get_tvl_security_data()
    

    df_santiment = get_santiment_data()

   


    if not df_tvl_security.empty:
        df_tvl_security['date'] = pd.to_datetime(df_tvl_security['date'])
        df_tvl_security['join_date'] = df_tvl_security['date'].dt.date
        df_tvl_security['join_symbol'] = df_tvl_security['symbol'].str.upper()

    
    if not df_santiment.empty:
        df_santiment['datetime'] = pd.to_datetime(df_santiment['datetime'])
        df_santiment['join_date'] = df_santiment['datetime'].dt.date
        df_santiment['join_symbol'] = df_santiment['ticker'].str.upper()



    
    
    print("\nMerging datasets")
    

    merged_df = pd.merge(
        df_tvl_security,
        df_santiment,
        on=['join_date', 'join_symbol'],
        how='inner'
    )

    
   
    merged_df['final_date'] = merged_df['date'].combine_first(merged_df['datetime'])
    merged_df['final_symbol'] = merged_df['symbol'].combine_first(merged_df['ticker'])
    
    
    cols_to_drop = ['join_date', 'join_symbol', 'date', 'symbol', 'datetime', 'ticker','chain','security_metric']
    merged_df.drop(columns=[c for c in cols_to_drop if c in merged_df.columns], inplace=True)
    
    
    merged_df.rename(columns={
        'final_date': 'date',
        'final_symbol': 'symbol'
    }, inplace=True)

 
    merged_df = merged_df.fillna(0)


    merged_df.sort_values(by=['symbol', 'date'], inplace=True)

    
    cols = ['date', 'symbol'] + [c for c in merged_df.columns if c not in ['date', 'symbol']]
    merged_df = merged_df[cols]


    return merged_df




def save_to_db(df):
   
    engine = get_engine()
    

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS onchain_metrics (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            active_addresses BIGINT,
            transactions BIGINT,
            exchange_inflow NUMERIC,
            exchange_outflow NUMERIC,
            whale_transactions NUMERIC,
            nvt_ratio NUMERIC,
            mvrv_ratio NUMERIC,
            net_flow NUMERIC,
            security_value NUMERIC,
            tvl_usd BIGINT
        );
    """


    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()

    if df.empty:
        print("DataFrame is empty. No data to save.")
        return
    
    try:
        df.to_sql(
            name='onchain_metrics',
            con=engine,
            if_exists='append',  # Add to existing data
            index=False,         # Do not create a column for the DataFrame index
            method='multi',      # Pass multiple rows in one SQL statement (faster)
            chunksize=1000       # Split into batches to save memory
        )
        
        
    except Exception as e:
        print(f"Error")

if __name__ == "__main__":
    final_df = combine_all_onchain_data() 
    save_to_db(final_df)
