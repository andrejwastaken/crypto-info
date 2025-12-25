import importlib.util
import os
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

BASE_DIR = Path(__file__).parent
OSC_PATH = BASE_DIR / "oscilators" / "script.py"
MA_PATH = BASE_DIR / "moving-averages" / "script.py"

HISTORY_LIMIT_DAYS = 3 * 365
MAX_OSC_SCORE = 5
MAX_MA_SCORE = 4


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def standardize_columns(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    if df.empty:
        return df
    
    rename_map = {}
    if "date" in df.columns:
        rename_map["date"] = "Date"
    if "symbol" in df.columns:
        rename_map["symbol"] = "Symbol"
    
    df = df.rename(columns=rename_map)
    
    # add prefix to all columns except Date and Symbol
    df = df.rename(columns={
        c: f"{prefix}{c}" 
        for c in df.columns 
        if c not in ["Date", "Symbol"]
    })
    
    return df


def calculate_normalized_score(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    
    df = df.copy()
    
    # get raw scores, defaulting to 0 if missing
    raw_osc = df.get("osc_raw_score_osc", 0).fillna(0)
    raw_ma = df.get("ma_raw_score_ma", 0).fillna(0)
    
    # get volume multiplier, defaulting to 1.0
    volume_mult = df.get("ma_volume_multiplier", 1.0).fillna(1.0)
    volume_mult = volume_mult.replace(0, 1.0)  # Avoid division by zero
    
    combined_raw = raw_osc + raw_ma
    
    max_possible = (MAX_OSC_SCORE + MAX_MA_SCORE) * volume_mult
    
    normalized = combined_raw / max_possible.replace(0, np.nan)
    normalized = normalized.clip(-1, 1).fillna(0).round(3)
    
    df["normalized_score"] = normalized
    
    return df


def fetch_ohlcv() -> pd.DataFrame:
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


def build_frames() -> dict[str, pd.DataFrame]:
    osc_module = load_module("oscillators_module", OSC_PATH)
    ma_module = load_module("ma_module", MA_PATH)

    raw_df = fetch_ohlcv()

    osc_df = raw_df.copy().set_index("date")

    ma_df = raw_df.rename(columns={
        "symbol": "Symbol",
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }).set_index("Date")

    osc_frames = osc_module.compute_oscillator_frames(osc_df)
    ma_frames = ma_module.compute_moving_average_frames(ma_df)

    # merge and normalize for each timeframe
    merged_frames = {}
    for tf in ["1d", "1w", "1m"]:
        osc_tf = standardize_columns(osc_frames.get(tf, pd.DataFrame()), "osc_")
        ma_tf = standardize_columns(ma_frames.get(tf, pd.DataFrame()), "ma_")
        
        merged = pd.merge(osc_tf, ma_tf, on=["Date", "Symbol"], how="outer")
        
        merged = calculate_normalized_score(merged)
        merged = merged.sort_values(["Symbol", "Date"])
        
        merged_frames[tf] = merged

    return merged_frames


def save_outputs(frames: dict[str, pd.DataFrame]):
    engine = get_engine()
    
    period_map = {"1d": "DAY", "1w": "WEEK", "1m": "MONTH"}
    
    all_frames = []
    for tf, df in frames.items():
        if df.empty:
            print(f"Skipping {tf}: No data to save")
            continue
        
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        
        df["period"] = period_map[tf]
        
        df.columns = [c.lower() for c in df.columns]
        
        all_frames.append(df)
    
    if not all_frames:
        print("No data to save.")
        return
    
    combined_df = pd.concat(all_frames, ignore_index=True)
    combined_df.drop(columns=['osc_raw_score_osc', 'ma_raw_score_ma', 'ma_volume_multiplier'], 
                     inplace=True, errors='ignore')
    combined_df.insert(0, "id", range(1, len(combined_df) + 1))
    
    combined_df.to_sql("technical_analysis", engine, if_exists="replace", index=False, chunksize=10000)
    
    print(f"Saved {len(combined_df)} rows with {len(combined_df.columns)} columns to 'technical_analysis'")
    print(f"  - DAY: {len(combined_df[combined_df['period'] == 'DAY'])} rows")
    print(f"  - WEEK: {len(combined_df[combined_df['period'] == 'WEEK'])} rows")
    print(f"  - MONTH: {len(combined_df[combined_df['period'] == 'MONTH'])} rows")


def main():
    print("Building technical analysis frames...")
    frames = build_frames()
    
    print("\nSaving to database...")
    save_outputs(frames)


if __name__ == "__main__":
    main()
