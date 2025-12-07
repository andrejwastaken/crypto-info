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
BUY_THRESHOLD = 0.4
SELL_THRESHOLD = -0.4


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


def standardize_frame(df: pd.DataFrame, raw_col: str, prefix: str) -> pd.DataFrame:
    if df.empty:
        return df

    rename_map: dict[str, str] = {}
    if "date" in df.columns:
        rename_map["date"] = "Date"
    if "Date" in df.columns:
        rename_map["Date"] = "Date"
    if "symbol" in df.columns:
        rename_map["symbol"] = "Symbol"

    if raw_col in df.columns:
        rename_map[raw_col] = "raw_score"

    df = df.rename(columns=rename_map)
    df = df.rename(columns={c: f"{prefix}{c}" for c in df.columns if c not in ["Date", "Symbol"]})
    return df


def compute_target(score: float) -> str:
    if score >= BUY_THRESHOLD:
        return "BUY"
    if score <= SELL_THRESHOLD:
        return "SELL"
    return "HOLD"


def normalize_scores(df: pd.DataFrame, volume_boost: float, volume_dampen: float) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["raw_score_osc"] = df.get("osc_raw_score", 0).fillna(0)
    df["raw_score_ma"] = df.get("ma_raw_score", 0).fillna(0)

    df["volume_multiplier"] = df.get("ma_volume_multiplier_hint", 1.0).fillna(1.0)
    df.loc[df["volume_multiplier"] <= 0, "volume_multiplier"] = 1.0

    max_possible = (MAX_OSC_SCORE + MAX_MA_SCORE) * df["volume_multiplier"]
    df["combined_raw_score"] = df["raw_score_osc"] + df["raw_score_ma"]

    df["normalized_score"] = df["combined_raw_score"] / max_possible.replace(0, np.nan)
    df["normalized_score"] = df["normalized_score"].clip(-1, 1).fillna(0)
    df["target"] = df["normalized_score"].apply(compute_target)

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

    osc_df = raw_df.copy()
    osc_df = osc_df.set_index("date")

    ma_df = raw_df.rename(
        columns={
            "symbol": "Symbol",
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )
    ma_df = ma_df.set_index("Date")

    osc_frames = osc_module.compute_oscillator_frames(osc_df)
    ma_frames = ma_module.compute_moving_average_frames(ma_df)

    merged_frames: dict[str, pd.DataFrame] = {}
    for tf in ["1d", "1w", "1m"]:
        osc_tf = standardize_frame(osc_frames.get(tf, pd.DataFrame()), "raw_score_osc", "osc_")
        ma_tf = standardize_frame(ma_frames.get(tf, pd.DataFrame()), "raw_score_ma", "ma_")

        merged = pd.merge(osc_tf, ma_tf, on=["Date", "Symbol"], how="outer")
        merged = normalize_scores(merged, ma_module.VOLUME_BOOST, ma_module.VOLUME_DAMPEN)
        merged = merged.sort_values(["Symbol", "Date"])
        merged_frames[tf] = merged

    return merged_frames


def save_outputs(frames: dict[str, pd.DataFrame]):
    engine = get_engine()
    table_names = {"1d": "technical_analysis_1d", "1w": "technical_analysis_1w", "1m": "technical_analysis_1m"}
    for tf, df in frames.items():
        if df.empty:
            continue
        df = df[df.isna().sum(axis=1) < 7]
        cols = ["Date", "Symbol", "normalized_score", "target"]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            # skip saving if required columns are not present
            print(f"Skipping {tf} due to missing columns: {missing}")
            continue
        df = df[cols].copy()
        df.columns = [c.lower() for c in df.columns]
        table_name = table_names[tf]
        df.to_sql(table_name, engine, if_exists="replace", index=False, chunksize=10000)
        print(f"Saved {len(df)} rows to table '{table_name}'")


def main():
    frames = build_frames()
    save_outputs(frames)


if __name__ == "__main__":
    main()
