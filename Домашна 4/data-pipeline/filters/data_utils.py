"""Shared utilities for data fetching and processing."""

import logging
import time
from datetime import date
from typing import Dict, Literal

import pandas as pd
import yfinance as yf

# Silence yfinance logger
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

INTERVALS = ["1d", "5d", "1wk", "1mo"]
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0


def parse_numeric_suffix(text: str) -> float:
    """
    Parse numeric strings with B/M/T/K suffixes (e.g., '131.179B', '51.205M').
    """
    if not text or text == "--":
        return 0.0

    text = text.strip().upper()
    
    # determine multiplier based on suffix
    if text.endswith("T"):
        multiplier = 1_000_000_000_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]
    elif text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("K"):
        multiplier = 1_000
        text = text[:-1]
    else:
        multiplier = 1

    try:
        return float(text) * multiplier
    except ValueError:
        return 0.0


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    standardize dataframe column names to lowercase.
    handles multi-index columns and duplicate names.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    rename_map = {
        "Open": "open", 
        "High": "high", 
        "Low": "low",
        "Close": "close", 
        "Volume": "volume",
    }
    df = df.rename(columns=rename_map)
    
    # handle duplicate columns
    if len(df.columns) != len(set(df.columns)):
        seen = {}
        new_cols = []
        for col in df.columns:
            if col in seen:
                new_cols.append(f"{col}_{seen[col]}")
                seen[col] += 1
            else:
                new_cols.append(col)
                seen[col] = 1
        df.columns = new_cols
    
    return df


def filter_by_update_date(df: pd.DataFrame, updated_at) -> pd.DataFrame:
    """
    filter dataframe to only include rows after the last update date.
    """
    if pd.isna(updated_at):
        return df
    
    # normalize updated_at to date object
    if isinstance(updated_at, str):
        try:
            updated_at = pd.to_datetime(updated_at).date()
        except:
            return df
    elif isinstance(updated_at, pd.Timestamp):
        updated_at = updated_at.date()
    
    if isinstance(updated_at, date) and "date" in df.columns:
        return df[df["date"] > updated_at]
    
    return df


def download_ohlcv_data(coin: Dict, period: Literal["max", "1mo"] = "max") -> pd.DataFrame:
    """
    download OHLCV data for a single cryptocurrency.
    """
    ticker = coin["symbol"]
    name = coin["name"]
    updated_at = coin.get("updated_at")
    
    # try multiple times with different intervals
    for attempt in range(RETRY_ATTEMPTS):
        for interval in INTERVALS:
            try:
                # fetch data from yfinance
                ticker_obj = yf.Ticker(ticker)
                data = ticker_obj.history(
                    period=period,
                    interval=interval,
                    auto_adjust=False,
                    actions=False
                )
                
                if data.empty:
                    continue
                
                df = data.copy()
                
                df = normalize_column_names(df)
                
                df = df.reset_index()
                if "Date" in df.columns:
                    df["date"] = df["Date"].dt.date
                    df = df.drop(columns=["Date"])
                
                df = filter_by_update_date(df, updated_at)
                
                desired_columns = ["date", "open", "high", "low", "close", "volume"]
                existing_columns = [c for c in desired_columns if c in df.columns]
                df = df[existing_columns]
                
                # metadata
                df["symbol"] = ticker
                df["name"] = name
                
                # clean up data
                if "volume" in df.columns:
                    df["volume"] = df["volume"].fillna(0).astype("int64")
                
                df = df.drop_duplicates(subset=["date"])
                df = df.sort_values("date").dropna(subset=["open", "high", "low", "close"])
                df = df.reset_index(drop=True)
                
                # ensure date is proper type
                df["date"] = pd.to_datetime(df["date"]).dt.date
                
                return df
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # handle specific errors
                if "401" in error_msg and attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    break
                    
                if "max must be" in error_msg or "invalid interval" in error_msg:
                    continue
    
    return pd.DataFrame()
