import os
import ast
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    PREDICTION_TABLE = 'on_chain_sentiment_predictions'

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

class DataRepository:
    def __init__(self):
        self.engine = DatabaseManager.get_engine()

    def init_table(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {Config.PREDICTION_TABLE} (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            predicted_close NUMERIC,
            predicted_change_pct NUMERIC
        );
        """
        with self.engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

    def fetch_sentiment(self) -> pd.DataFrame:
        logger.info("Fetching news sentiment data...")
        df = pd.read_sql("SELECT * FROM news_sentiment", self.engine, parse_dates=['date'])
        
        if 'symbols' in df.columns:
            def clean_parse(x):
                if isinstance(x, list): return x
                try: return ast.literal_eval(x)
                except (ValueError, SyntaxError): return []
            
            df['symbols'] = df['symbols'].apply(clean_parse)
            df = df.explode('symbols').rename(columns={'symbols': 'symbol'})
            df.dropna(subset=['symbol'], inplace=True)
            df['symbol'] = df['symbol'].astype(str).str.strip()
        return df

    def fetch_onchain(self) -> pd.DataFrame:
        logger.info("Fetching on-chain metrics...")
        return pd.read_sql("SELECT * FROM onchain_metrics", self.engine, parse_dates=['date'])

    def fetch_ohlcv(self) -> pd.DataFrame:
        logger.info("Fetching OHLCV data...")
        return pd.read_sql("SELECT close, symbol, date FROM ohlcv_data", self.engine, parse_dates=['date'])

    def save_predictions(self, df: pd.DataFrame):
        logger.info(f"Saving {len(df)} predictions to DB...")
        try:
            df.to_sql(Config.PREDICTION_TABLE, self.engine, if_exists='append', index=False, method='multi')
            logger.info("Saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save predictions: {e}")

class PredictionStrategy(ABC):

    @abstractmethod
    def train_and_predict(self, train_df: pd.DataFrame, latest_df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        pass

class RandomForestStrategy(PredictionStrategy):
    def __init__(self, n_estimators=300):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        self.scaler = StandardScaler()

    def train_and_predict(self, train_df: pd.DataFrame, latest_df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        X_train = train_df[feature_cols]
        y_train = train_df['target_next_close']
        
        X_scaled = self.scaler.fit_transform(X_train)
        tscv = TimeSeriesSplit(n_splits=5)
        scores = cross_val_score(self.model, X_scaled, y_train, cv=tscv, scoring='r2')
        logger.info(f"Model CV R²: {scores.mean():.4f}")

        self.model.fit(X_scaled, y_train)

        X_latest = latest_df[feature_cols]
        X_latest_scaled = self.scaler.transform(X_latest)
        
        predictions = latest_df.copy()
        predictions['predicted_close'] = self.model.predict(X_latest_scaled)
        
        return predictions

class PredictionService:
    def __init__(self, strategy: PredictionStrategy):
        self.repo = DataRepository()
        self.strategy = strategy

    def prepare_data(self) -> Optional[pd.DataFrame]:
        sent_df = self.repo.fetch_sentiment()
        chain_df = self.repo.fetch_onchain()
        price_df = self.repo.fetch_ohlcv()

        if sent_df.empty or chain_df.empty:
            logger.warning("Missing input data.")
            return None

        logger.info("Merging datasets...")
        merged = pd.merge(chain_df, sent_df[['symbol', 'date', 'sentiment_score']], on=['symbol', 'date'], how='inner')
        final_df = pd.merge(merged, price_df, on=['symbol', 'date'], how='inner')
        
        final_df = final_df.sort_values(['symbol', 'date'])
        final_df['target_next_close'] = final_df.groupby('symbol')['close'].shift(-1)
        
        return final_df

    def run_pipeline(self):
        self.repo.init_table()
        df = self.prepare_data()
        
        if df is None or df.empty:
            logger.warning("No data available for prediction.")
            return

        train_df = df.dropna(subset=['target_next_close'])
        latest_df = df[df['target_next_close'].isna()].groupby('symbol').tail(1)

        if train_df.empty or latest_df.empty:
            logger.warning("Not enough data to train.")
            return

        exclude = {'id', 'symbol', 'date', 'target_next_close'}
        features = [c for c in df.columns if c not in exclude]

        result_df = self.strategy.train_and_predict(train_df, latest_df, features)

        result_df['predicted_change_pct'] = (
            (result_df['predicted_close'] - result_df['close']) / result_df['close']
        ) * 100
        
        # Shift date to tomorrow (since we predicted the NEXT close)
        result_df['date'] = result_df['date'] + pd.Timedelta(days=1)
        
        output = result_df[['symbol', 'date', 'predicted_close', 'predicted_change_pct']]
        self.repo.save_predictions(output)

if __name__ == "__main__":
    strategy = RandomForestStrategy() 
    service = PredictionService(strategy)
    service.run_pipeline()