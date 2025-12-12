import torch
import torch.nn as nn
import torch.optim as optim

import importlib.util
import os
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler

load_dotenv()

BASE_DIR = Path(__file__).parent
HISTORY_LIMIT_DAYS = 3 * 365
LOOKBACK_DAYS = 30  # Lookback period for LSTM

def get_engine():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_port, db_name]):
        raise RuntimeError("Database credentials are missing in environment variables")

    encoded_password = quote_plus(db_password)
    connection_str = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_str)

def fetch_ohlcv():
    engine = get_engine()
    query = f"""
        SELECT symbol, date, open, high, low, close, volume
        FROM ohlcv_data
        WHERE symbol IN (SELECT symbol FROM coins_metadata)
          AND date >= CURRENT_DATE - INTERVAL '{HISTORY_LIMIT_DAYS} days'
        ORDER BY symbol, date ASC
    """
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset=["symbol", "date"], keep="last")
    df = df.sort_values(["symbol", "date"])
    return df

def main():
    pass

if __name__ == "__main__":
    main()
