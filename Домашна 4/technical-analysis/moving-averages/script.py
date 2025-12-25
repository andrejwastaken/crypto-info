import numpy as np
import pandas as pd
import ta
from tqdm import tqdm


HISTORY_LIMIT_DAYS = 3 * 365
VOLUME_BOOST = 1.2
VOLUME_DAMPEN = 0.8
METRIC_COLUMNS = ["SMA_20", "EMA_20", "WMA_20", "BB_MID", "VOL_SMA_20", "volume_multiplier"]


def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample OHLCV data to a different timeframe."""
    agg_dict = {
        "Symbol": "first",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    return df.resample(timeframe).agg(agg_dict)


def compute_raw_score(row: pd.Series) -> int:
    """Calculate raw moving average score based on price position relative to MAs."""
    close = row["Close"]
    score = 0
    
    # Price above MA = bullish, below = bearish
    if pd.notna(row.get("SMA_20")):
        score += 1 if close > row["SMA_20"] else -1
    if pd.notna(row.get("EMA_20")):
        score += 1 if close > row["EMA_20"] else -1
    if pd.notna(row.get("WMA_20")):
        score += 1 if close > row["WMA_20"] else -1
    if pd.notna(row.get("BB_MID")):
        score += 1 if close > row["BB_MID"] else -1
    
    return score


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all moving average indicators and raw score."""
    if len(df) < 20:
        return pd.DataFrame()

    close = df["Close"]
    volume = df["Volume"]

    try:
        # Calculate moving averages
        sma_20 = ta.trend.sma_indicator(close, window=20)
        ema_20 = ta.trend.ema_indicator(close, window=20)
        wma_20 = ta.trend.wma_indicator(close, window=20)
        vol_sma_20 = ta.trend.sma_indicator(volume, window=20)
        
        # Bollinger Bands middle line
        bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
        bb_mid = bb.bollinger_mavg()

        # Build result dataframe with all metrics
        result = pd.DataFrame(index=df.index)
        result["Close"] = close
        result["SMA_20"] = sma_20
        result["EMA_20"] = ema_20
        result["WMA_20"] = wma_20
        result["BB_MID"] = bb_mid
        result["VOL_SMA_20"] = vol_sma_20
        result["Volume"] = volume
        
        # Calculate volume multiplier
        result["volume_multiplier"] = np.where(volume > vol_sma_20, VOLUME_BOOST, VOLUME_DAMPEN)
        
        # Calculate raw score
        result["raw_score_ma"] = result.apply(compute_raw_score, axis=1)
        
        # Keep only relevant columns
        columns_to_keep = [col for col in METRIC_COLUMNS if col in result.columns] + ["raw_score_ma"]
        result = result[columns_to_keep]
        
    except Exception:
        return pd.DataFrame()

    return result


def process_timeframe(df_coin: pd.DataFrame, symbol: str, timeframe: str = None) -> pd.DataFrame:
    """Process a single coin for a specific timeframe."""
    try:
        # Resample if needed
        if timeframe:
            df_coin = resample_data(df_coin, timeframe)
            if df_coin.empty or len(df_coin) < 20:
                return pd.DataFrame()
        
        # Compute indicators
        processed = compute_indicators(df_coin)
        if processed.empty:
            return pd.DataFrame()
        
        # Add symbol and reset index
        processed["Symbol"] = symbol
        processed = processed.reset_index().rename(columns={"index": "Date"})
        processed = processed.sort_values("Date")
        
        # Return only the latest row
        return processed.tail(1)
    except Exception:
        return pd.DataFrame()


def compute_moving_average_frames(df_all: pd.DataFrame) -> dict:
    """
    Compute moving average indicators for all coins across multiple timeframes.
    
    Returns dict with keys '1d', '1w', '1m' containing DataFrames with all metrics.
    """
    results = {"1d": [], "1w": [], "1m": []}
    grouped = df_all.groupby("Symbol")

    for symbol, df_coin in tqdm(grouped, desc="Moving Averages"):
        # Daily
        daily_result = process_timeframe(df_coin.copy(), symbol)
        if not daily_result.empty:
            results["1d"].append(daily_result)
        
        # Weekly
        weekly_result = process_timeframe(df_coin.copy(), symbol, "W")
        if not weekly_result.empty:
            results["1w"].append(weekly_result)
        
        # Monthly
        monthly_result = process_timeframe(df_coin.copy(), symbol, "ME")
        if not monthly_result.empty:
            results["1m"].append(monthly_result)

    return {
        tf: (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()) 
        for tf, frames in results.items()
    }


def main():
    print(
        "This module now only exposes helpers. Use combine_signals.py to run the full pipeline."
    )


if __name__ == "__main__":
    main()
    