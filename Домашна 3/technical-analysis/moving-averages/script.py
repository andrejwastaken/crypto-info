import numpy as np
import pandas as pd
import ta
from tqdm import tqdm


HISTORY_LIMIT_DAYS = 3 * 365
VOLUME_BOOST = 1.2
VOLUME_DAMPEN = 0.8


def compute_moving_average_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 20:
        return df

    close = df["Close"]
    volume = df["Volume"]

    # simple moving average
    sma_20 = ta.trend.sma_indicator(close, window=20)
    # exponential moving average
    ema_20 = ta.trend.ema_indicator(close, window=20)
    # weighted moving average
    wma_20 = ta.trend.wma_indicator(close, window=20)
    # volume moving average
    vol_sma_20 = ta.trend.sma_indicator(volume, window=20)
    # bollinger bonds
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    bb_mid = bb.bollinger_mavg()

    df = df.copy()

    raw_score = pd.Series(0, index=df.index)
    raw_score += np.where(close > sma_20, 1, -1)
    raw_score += np.where(close > ema_20, 1, -1)
    raw_score += np.where(close > wma_20, 1, -1)
    raw_score += np.where(close > bb_mid, 1, -1)

    volume_multiplier = np.where(volume > vol_sma_20, VOLUME_BOOST, VOLUME_DAMPEN)

    df["raw_score_ma"] = raw_score
    df["volume_multiplier_hint"] = volume_multiplier

    return df[["raw_score_ma", "volume_multiplier_hint"]]


def resample_coin(df_coin: pd.DataFrame, rule: str) -> pd.DataFrame:
    agg_logic = {
        "Symbol": "first",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    return df_coin.resample(rule).agg(agg_logic)


def compute_moving_average_frames(df_all: pd.DataFrame) -> dict:
    results = {"1d": [], "1w": [], "1m": []}
    grouped = df_all.groupby("Symbol")

    for symbol, df_coin in tqdm(grouped, desc="moving-avg"):
        d_daily = df_coin.copy()
        if len(d_daily) >= 20:
            processed_daily = compute_moving_average_metrics(d_daily)
            processed_daily["Symbol"] = symbol
            processed_daily = processed_daily.reset_index().sort_values("Date")
            results["1d"].append(processed_daily.tail(1))

        d_weekly = resample_coin(df_coin, "W")
        if len(d_weekly) >= 20:
            processed_weekly = compute_moving_average_metrics(d_weekly)
            processed_weekly["Symbol"] = symbol
            processed_weekly = processed_weekly.reset_index().sort_values("Date")
            results["1w"].append(processed_weekly.tail(1))

        d_monthly = resample_coin(df_coin, "ME")
        if len(d_monthly) >= 20:
            processed_monthly = compute_moving_average_metrics(d_monthly)
            processed_monthly["Symbol"] = symbol
            processed_monthly = processed_monthly.reset_index().sort_values("Date")
            results["1m"].append(processed_monthly.tail(1))

    return {tf: (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()) for tf, frames in results.items()}


def main():
    print(
        "This module now only exposes helpers. Use combine_signals.py to run the full pipeline."
    )


if __name__ == "__main__":
    main()
    