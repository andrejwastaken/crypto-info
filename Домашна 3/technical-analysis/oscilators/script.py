import pandas as pd
import pandas_ta as ta
from tqdm import tqdm


HISTORY_LIMIT_DAYS = 3 * 365


def force_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.duplicated()]


def resample_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
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
    score = 0
    try:
        if row.get("RSI") is not None:
            if row["RSI"] < 30:
                score += 1
            elif row["RSI"] > 70:
                score -= 1
    except Exception:
        pass

    try:
        k = row.get("STOCHk_14_3_3", 50)
        if k < 20:
            score += 1
        elif k > 80:
            score -= 1
    except Exception:
        pass

    try:
        c = row.get("CCI")
        if c is not None:
            if c < -100:
                score += 1
            elif c > 100:
                score -= 1
    except Exception:
        pass

    try:
        if row.get("MACD_12_26_9") is not None and row.get("MACDs_12_26_9") is not None:
            if row["MACD_12_26_9"] > row["MACDs_12_26_9"]:
                score += 1
            else:
                score -= 1
    except Exception:
        pass

    try:
        if row.get("DMP_14") is not None and row.get("DMN_14") is not None:
            if row["DMP_14"] > row["DMN_14"]:
                score += 1
            else:
                score -= 1
    except Exception:
        pass

    return score


def process_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, ~df.columns.duplicated()]
    if not df.index.is_unique:
        df = df[~df.index.duplicated(keep="last")]
    if len(df) < 30:
        return df

    try:
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
        df["raw_score_osc"] = df.apply(compute_raw_score, axis=1)
        df = df[["raw_score_osc"]]
    except Exception:
        pass

    return force_unique_columns(df)


def compute_oscillator_frames(df: pd.DataFrame) -> dict:
    results = {"1d": [], "1w": [], "1m": []}
    unique_symbols = df["symbol"].unique()

    for symbol in tqdm(unique_symbols):
        try:
            coin_df = df[df["symbol"] == symbol].copy().sort_index()

            # Daily
            d_df = process_indicators(coin_df.copy())
            d_df["symbol"] = symbol
            d_df = d_df.reset_index().rename(columns={"index": "date"})
            d_df = d_df.sort_values("date")
            if "raw_score_osc" in d_df.columns and not d_df.empty:
                results["1d"].append(d_df.tail(1))

            # Weekly
            w_df = resample_data(coin_df, "W")
            w_df = process_indicators(w_df)
            w_df["symbol"] = symbol
            w_df = w_df.reset_index().rename(columns={"index": "date"})
            w_df = w_df.sort_values("date")
            if "raw_score_osc" in w_df.columns and not w_df.empty:
                results["1w"].append(w_df.tail(1))

            # Monthly
            m_df = resample_data(coin_df, "ME")
            m_df = process_indicators(m_df)
            m_df["symbol"] = symbol
            m_df = m_df.reset_index().rename(columns={"index": "date"})
            m_df = m_df.sort_values("date")
            if "raw_score_osc" in m_df.columns and not m_df.empty:
                results["1m"].append(m_df.tail(1))
        except Exception:
            pass

    return {tf: (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()) for tf, frames in results.items()}


def main():
    print(
        "This script now exposes functions. Use combine_signals.py to orchestrate DB access, scoring, and outputs."
    )


if __name__ == "__main__":
    main()