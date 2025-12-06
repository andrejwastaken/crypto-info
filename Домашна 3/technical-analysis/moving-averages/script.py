import pandas as pd
import ta
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()


# fetch 3 years to ensure montly timeframe has enough data (>= 20 months) to calculate indicators and provide a year of signals
HISTORY_LIMIT_DAYS = 3 * 365 

def generate_signals(df):
    """
    Calculates a 'Signal Strength' score (-1 to 1) based on a voting system.
    """
    close = df['Close']
    volume = df['Volume']
    
    # step 1. calculate indicators
    sma_20 = ta.trend.sma_indicator(close, window=20)
    ema_20 = ta.trend.ema_indicator(close, window=20)
    wma_20 = ta.trend.wma_indicator(close, window=20)
    vol_sma_20 = ta.trend.sma_indicator(volume, window=20)
    
    # 1.1 Bollinger Bands
    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    bb_mid = bb.bollinger_mavg() # Middle band is essentially an SMA
    
    # step 2. the voting system
    
    # start with 0 for each row
    score = pd.Series(0.0, index=df.index)

    # voter 1: SMA Trend - benchmark: Is price above 20-day simple average?
    # Yes (+1), If No (-1)
    score += np.where(close > sma_20, 1, -1)
    
    # voter 2: EMA Trend - benchmark: Is price above 20-day exponential average?
    # Yes (+1), If No (-1)
    score += np.where(close > ema_20, 1, -1)
    
    # voter 3: WMA Trend - benchmark: Is price above 20-day weighted average?
    # Yes (+1), If No (-1)
    score += np.where(close > wma_20, 1, -1)
    
    # voter 4: Bollinger Mid - benchmark: Is price in the upper half of the bands?
    # Yes (+1), If No (-1)
    score += np.where(close > bb_mid, 1, -1)
    
    # step 2.1 volume confimation
    # If Volume is high (above average), the move is "confirmed".
    # If Volume is low, the signal is weak.
    # benchmark: If Vol > Avg, multiply score by 1.2 (Boost); If Vol < Avg, multiply by 0.8 (Dampen).
    vol_multiplier = np.where(volume > vol_sma_20, 1.2, 0.8)
    score = score * vol_multiplier
    
    # step 4. normalize to [-1,1] range
    # maximum possible raw score is 4 (4 voters * 1.0). 
    # with volume boost, max is 4.8. divide by 5 to keep it roughly within -1 to 1.
    
    df['Signal_Strength'] = score / 5.0
    
    # clip values to ensure they stay strictly between -1 and 1
    df['Signal_Strength'] = df['Signal_Strength'].clip(-1, 1)

    # step 5. generate labels from scores
    conditions = [
        df['Signal_Strength'] >= 0.5,   # Strong Buy
        df['Signal_Strength'] <= -0.5   # Strong Sell
    ]
    choices = ['BUY', 'SELL']
    
    df['Signal'] = np.select(conditions, choices, default='HOLD')
    
    return df[['Symbol', 'Close', 'Signal', 'Signal_Strength']]

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

print("Fetching data from database...")

query = f"""
    SELECT symbol, date, open, high, low, close, volume
    FROM ohlcv_data
    WHERE date >= CURRENT_DATE - INTERVAL '{HISTORY_LIMIT_DAYS} days'
    ORDER BY symbol, date ASC
"""

df_all = pd.read_sql(query, engine)

df_all.columns = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
df_all['Date'] = pd.to_datetime(df_all['Date'])
df_all.set_index('Date', inplace=True)

print(f"Loaded {len(df_all)} rows of data for {df_all['Symbol'].nunique()} symbols.")

results_daily = []
results_weekly = []
results_monthly = []

grouped = df_all.groupby('Symbol')

for symbol, df_coin in grouped:
    # daily
    d_daily = df_coin.copy()
    if len(d_daily) < 20: continue # skip if not enough data
    
    processed_daily = generate_signals(d_daily)
    # results_daily.append(processed_daily)
    # TODO: decide whether to store just last day of data or all historic data
    # results_daily.append(processed_daily) 
    results_daily.append(processed_daily.iloc[-1:]) 
    
    agg_logic = {
        'Symbol': 'first', 
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }
    
    # weekly
    d_weekly = df_coin.resample('W').agg(agg_logic)
    if len(d_weekly) >= 20:
        processed_weekly = generate_signals(d_weekly)
        # TODO: decide whether to store just last day of data or all historic data
        # results_weekly.append(processed_weekly)
        results_weekly.append(processed_weekly.iloc[-1:])


    # monthly ('ME' is Month End)
    d_monthly = df_coin.resample('ME').agg(agg_logic)
    if len(d_monthly) >= 20:
        processed_monthly = generate_signals(d_monthly)
        # TODO: decide whether to store just last day of data or all historic data
        # results_monthly.append(processed_monthly)
        results_monthly.append(processed_monthly.iloc[-1:])

print("Saving results...")

# TODO: write in DB

DAY_FILENAME = 'signals-1d-only-last.csv'
WEEK_FILENAME = 'signals-1w-only-last.csv'
MONTH_FILENAME = 'signals-1m-only-last.csv'

if results_daily:
    pd.concat(results_daily).to_csv(DAY_FILENAME)
    print(f"{DAY_FILENAME} saved")

if results_weekly:
    pd.concat(results_weekly).to_csv(WEEK_FILENAME)
    print(f"{WEEK_FILENAME} saved")

if results_monthly:
    pd.concat(results_monthly).to_csv(MONTH_FILENAME)
    print(f"{MONTH_FILENAME} saved")
    