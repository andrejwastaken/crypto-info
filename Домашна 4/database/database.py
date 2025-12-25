import os
from typing import Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine

load_dotenv()

class Config:
    API_KEY = os.getenv("API_KEY")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    SANTIMENT_URL = "https://api.santiment.net/graphql"
    TOTAL_DAYS = 365
    WINDOW_DAYS = 30
    IGNORE_TICKERS = {"SUI20947-USD", "HBAR-USD"}
    MISSING_COLUMNS_THRESHOLD = 2

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