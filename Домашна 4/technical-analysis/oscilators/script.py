import pandas as pd
import pandas_ta as ta
from tqdm import tqdm


HISTORY_LIMIT_DAYS = 3 * 365
METRIC_COLUMNS = ["RSI", "MACD_LINE", "MACD_SIGNAL", "STOCH_K", "STOCH_D", "DMI_PLUS", "DMI_MINUS", "ADX", "CCI"]

# mapping from pandas_ta generated column names to readable names
COLUMN_RENAME_MAP = {
    "MACD_12_26_9": "MACD_LINE",
    "MACDs_12_26_9": "MACD_SIGNAL",
    "STOCHk_14_3_3": "STOCH_K",
    "STOCHd_14_3_3": "STOCH_D",
    "DMP_14": "DMI_PLUS",
    "DMN_14": "DMI_MINUS",
    "ADX_14": "ADX",
}


def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """resample OHLCV data to a different timeframe."""
    agg_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    try:
        resampled = df.resample(timeframe).agg(agg_dict)
        return resampled.dropna()
    except Exception:
        return df


def compute_raw_score(row: pd.Series) -> int:
    """calculate raw oscillator score based on technical indicator thresholds."""
    score = 0
    
    # RSI: oversold (<30) = bullish, overbought (>70) = bearish
    if pd.notna(row.get("RSI")):
        if row["RSI"] < 30:
            score += 1
        elif row["RSI"] > 70:
            score -= 1
    
    # stochastic: oversold (<20) = bullish, overbought (>80) = bearish
    stoch_k = row.get("STOCH_K")
    if pd.notna(stoch_k):
        if stoch_k < 20:
            score += 1
        elif stoch_k > 80:
            score -= 1
    
    # CCI: oversold (<-100) = bullish, overbought (>100) = bearish
    cci = row.get("CCI")
    if pd.notna(cci):
        if cci < -100:
            score += 1
        elif cci > 100:
            score -= 1
    
    # MACD: MACD above signal = bullish, below = bearish
    macd = row.get("MACD_LINE")
    macd_signal = row.get("MACD_SIGNAL")
    if pd.notna(macd) and pd.notna(macd_signal):
        score += 1 if macd > macd_signal else -1
    
    # DMI: DI+ above DI- = bullish, below = bearish
    dmp = row.get("DMI_PLUS")
    dmn = row.get("DMI_MINUS")
    if pd.notna(dmp) and pd.notna(dmn):
        score += 1 if dmp > dmn else -1
    
    return score


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all oscillator indicators and raw score."""
    df = df.loc[:, ~df.columns.duplicated()]
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep="last")]
    if len(df) < 30:
        return pd.DataFrame()
    
    try:
        # calculate indicators
        df["RSI"] = df.ta.rsi(length=14)
        
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        
        stoch = df.ta.stoch(k=14, d=3, smooth_k=3)
        if stoch is not None:
            df = pd.concat([df, stoch], axis=1)
        
        adx = df.ta.adx(length=14)
        if adx is not None:
            df = pd.concat([df, adx], axis=1)
        
        df["CCI"] = df.ta.cci(length=20)
        
        # rename columns to readable names
        df = df.rename(columns=COLUMN_RENAME_MAP)
        
        # calculate raw score
        df["raw_score_osc"] = df.apply(compute_raw_score, axis=1)
        
        # keep only relevant columns
        columns_to_keep = [col for col in METRIC_COLUMNS if col in df.columns] + ["raw_score_osc"]
        df = df[columns_to_keep]
        
    except Exception:
        return pd.DataFrame()
    
    return df.loc[:, ~df.columns.duplicated()]


def process_timeframe(coin_df: pd.DataFrame, symbol: str, timeframe: str = None) -> pd.DataFrame:
    """process a single coin for a specific timeframe."""
    try:
        if timeframe:
            coin_df = resample_data(coin_df, timeframe)
            if coin_df.empty:
                return pd.DataFrame()
        
        processed = compute_indicators(coin_df)
        if processed.empty:
            return pd.DataFrame()
        
        processed["symbol"] = symbol
        processed = processed.reset_index().rename(columns={"index": "date"})
        processed = processed.sort_values("date")
        
        # Return only the latest row
        return processed.tail(1)
    except Exception:
        return pd.DataFrame()


def compute_oscillator_frames(df: pd.DataFrame) -> dict:
    """
    compute oscillator indicators for all coins across multiple timeframes.
    """
    results = {"1d": [], "1w": [], "1m": []}
    unique_symbols = df["symbol"].unique()

    for symbol in tqdm(unique_symbols, desc="Oscillators"):
        coin_df = df[df["symbol"] == symbol].copy().sort_index()
        
        # Daily
        daily_result = process_timeframe(coin_df.copy(), symbol)
        if not daily_result.empty:
            results["1d"].append(daily_result)
        
        # Weekly
        weekly_result = process_timeframe(coin_df.copy(), symbol, "W")
        if not weekly_result.empty:
            results["1w"].append(weekly_result)
        
        # Monthly
        monthly_result = process_timeframe(coin_df.copy(), symbol, "ME")
        if not monthly_result.empty:
            results["1m"].append(monthly_result)

    return {
        tf: (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()) 
        for tf, frames in results.items()
    }


def main():
    print(
        "This script exposes compute_oscillator_frames(). Run combine_signals.py to execute."
    )


if __name__ == "__main__":
    main()