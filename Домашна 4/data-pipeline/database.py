import io
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "crypto_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", "5432")

# threshold for using COPY vs standard insert
LARGE_DATASET_THRESHOLD = 700_000


def get_engine():
    """create and return SQLAlchemy engine for database connection."""
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_string)


def save_df_to_db(
    df: pd.DataFrame, 
    table_name: str, 
    replace: bool = True, 
    add_id: bool = True
):
    """
    save dataframe to database table with optimized bulk loading.
    
    for large datasets (>700k rows), uses postgres COPY for efficiency.
    for smaller datasets, uses standard sqlalchemy to_sql.
    """
    if df.empty:
        print(f"DataFrame is empty. Skipping save to '{table_name}'.")
        return
    
    engine = get_engine()
    
    try:
        print(f"Saving {len(df)} rows to table '{table_name}'...")
        
        # add auto-incrementing ID column if requested
        if add_id and 'id' not in df.columns:
            df = df.copy()
            df.insert(0, 'id', range(1, len(df) + 1))
        
        # use postgres COPY for large datasets
        if len(df) > LARGE_DATASET_THRESHOLD:
            _save_large_dataset(df, table_name, engine, replace)
        else:
            _save_standard(df, table_name, engine, replace)
        
        print(f"Successfully saved to '{table_name}'")
        
    except Exception as e:
        print(f"Error saving to database: {e}")


def _save_large_dataset(df: pd.DataFrame, table_name: str, engine, replace: bool):
    """Use PostgreSQL COPY for efficient bulk loading of large datasets."""
    # Create table structure first
    if replace:
        df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
    else:
        df.head(0).to_sql(table_name, engine, if_exists='append', index=False)
    
    # Use COPY for bulk insert
    output = io.StringIO()
    df.to_csv(output, index=False, header=False)
    output.seek(0)
    
    with engine.connect() as connection:
        dbapi_conn = connection.connection
        with dbapi_conn.cursor() as cursor:
            cursor.copy_expert(
                f"COPY {table_name} FROM STDIN WITH (FORMAT CSV)", 
                output
            )
        dbapi_conn.commit()


def _save_standard(df: pd.DataFrame, table_name: str, engine, replace: bool):
    """Use standard SQLAlchemy to_sql for smaller datasets."""
    if_exists = "replace" if replace else "append"
    df.to_sql(table_name, engine, if_exists=if_exists, index=False, chunksize=10000)


def save_csv_to_db(csv_path: str, table_name: str, replace: bool = True):
    """
    load csv file and save to database.
    """
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
    
    try:
        df = pd.read_csv(csv_path)
        save_df_to_db(df, table_name, replace=replace)
    except Exception as e:
        print(f"Error processing CSV: {e}")


def check_and_update_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    check database for existing metadata and update dataframe.
    adds 'updated_at' column with last update date for each coin symbol.
    """
    engine = get_engine()
    inspector = inspect(engine)
    
    if not inspector.has_table("coins_metadata"):
        df['updated_at'] = None
        return df
    
    try:
        query = "SELECT symbol, updated_at FROM coins_metadata"
        db_df = pd.read_sql(query, engine)
        
        # create mapping of symbol to updated_at
        db_map = dict(zip(db_df['symbol'], db_df['updated_at']))
        
        # map to input DataFrame
        df['updated_at'] = df['symbol'].map(db_map)
        
        return df
        
    except Exception as e:
        print(f"Error checking metadata: {e}")
        df['updated_at'] = None
        return df
