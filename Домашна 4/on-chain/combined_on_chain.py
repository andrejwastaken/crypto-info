import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict
from urllib.parse import quote_plus
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text, Engine
from collectors_hash_tvl import CryptoDataAggregator
from collectors_others import OnChainDataService 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    TABLE_NAME = 'onchain_metrics'

class DatabaseManager:
    _engine: Optional[Engine] = None

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is not None:
            return cls._engine

        if not all([Config.DB_USER, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME]):
            raise RuntimeError("Database credentials are missing.")

        encoded_password = quote_plus(Config.DB_PASSWORD)
        connection_str = f"postgresql://{Config.DB_USER}:{encoded_password}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
        
        cls._engine = create_engine(connection_str, pool_size=10, max_overflow=20)
        return cls._engine

class ETLPipeline(ABC):
    def run(self):
        logger.info("Starting ETL Pipeline...")
        
        raw_data = self.extract()
        if not raw_data:
            logger.warning("Extraction returned no data. Aborting.")
            return

        transformed_data = self.transform(raw_data)
        if transformed_data.empty:
            logger.warning("Transformation resulted in empty dataset. Aborting.")
            return

        self.load(transformed_data)
        logger.info("ETL Pipeline finished successfully.")

    @abstractmethod
    def extract(self) -> Dict[str, pd.DataFrame]:
        """Step 1: Retrieve data from sources."""
        pass

    @abstractmethod
    def transform(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Step 2: Clean and merge data."""
        pass

    @abstractmethod
    def load(self, df: pd.DataFrame):
        """Step 3: Save data to storage."""
        pass

class OnChainMergerPipeline(ETLPipeline):
    def extract(self) -> Dict[str, pd.DataFrame]:
        logger.info("Extracting data from sources...")
        data = {}
        try:
            aggregator = CryptoDataAggregator()
            data['tvl_security'] = aggregator.aggregate()
        except Exception as e:
            logger.error(f"Failed to get TVL data: {e}")

        if OnChainDataService:
            try:
                service = OnChainDataService()
                data['santiment'] = service.fetch_data_as_dataframe() 
            except Exception as e:
                logger.error(f"Failed to get Santiment data from service: {e}")
        
        return data

    def transform(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        logger.info("Transforming and merging datasets...")
        df_tvl_sec = data.get("tvl_security", pd.DataFrame())
        df_santiment = data.get("santiment", pd.DataFrame())

        if not df_tvl_sec.empty:
            df_tvl_sec['date'] = pd.to_datetime(df_tvl_sec['date'])
            df_tvl_sec['join_date'] = df_tvl_sec['date'].dt.date
            df_tvl_sec['join_symbol'] = df_tvl_sec['symbol'].str.upper()

        # Pre-processing Santiment Data
        if not df_santiment.empty:
            df_santiment['datetime'] = pd.to_datetime(df_santiment['datetime'])
            df_santiment['join_date'] = df_santiment['datetime'].dt.date
            df_santiment['join_symbol'] = df_santiment['ticker'].str.upper()

        # Merge
        merged_df = pd.merge(
            df_tvl_sec,
            df_santiment,
            on=['join_date', 'join_symbol'],
            how='inner'
        )

        if merged_df.empty:
            return pd.DataFrame()

        # Clean up columns
        merged_df['final_date'] = merged_df['date'].combine_first(merged_df['datetime'])
        merged_df['final_symbol'] = merged_df['symbol'].combine_first(merged_df['ticker'])

        cols_to_drop = ['join_date', 'join_symbol', 'date', 'symbol', 'datetime', 'ticker', 'chain', 'Metric_name', 'metric_name']
        merged_df.drop(columns=[c for c in cols_to_drop if c in merged_df.columns], inplace=True)
        
        merged_df.rename(columns={'final_date': 'date', 'final_symbol': 'symbol'}, inplace=True)
        merged_df.fillna(0, inplace=True)
        
        # Ensure integer types for BIGINT columns
        int_cols = ['active_addresses', 'transactions', 'tvl_usd']
        for col in int_cols:
            if col in merged_df.columns:
                merged_df[col] = merged_df[col].astype(int)
                
        merged_df.sort_values(by=['symbol', 'date'], inplace=True)

        # Reorder columns to ensure date/symbol are first
        cols = ['date', 'symbol'] + [c for c in merged_df.columns if c not in ['date', 'symbol']]
        return merged_df[cols]

    def load(self, df: pd.DataFrame):
        engine = DatabaseManager.get_engine()
        
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {Config.TABLE_NAME} (
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
        
        try:
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()

            logger.info(f"Loading {len(df)} rows into database '{Config.TABLE_NAME}'...")
            print(df.head())
            df.to_sql(
                name=Config.TABLE_NAME,
                con=engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            logger.info("Data load complete.")
            
        except Exception as e:
            logger.error(f"Database error during load: {e}")

if __name__ == "__main__":
    pipeline = OnChainMergerPipeline()
    pipeline.run()

    