import pandas as pd
from sqlalchemy import create_engine
import pandas_ta as ta
import os
import sys
from urllib.parse import quote_plus
from tqdm import tqdm
from dotenv import load_dotenv 


load_dotenv() 

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')



encoded_password = quote_plus(db_password)
connection_str = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
db_connection = create_engine(connection_str)

query = """
SELECT symbol, date, open, high, low, close, volume
FROM ohlcv_data
WHERE symbol IN (SELECT symbol FROM coins_metadata) 
ORDER BY symbol, date ASC
"""

# Loading data from database
df = pd.read_sql(query, db_connection)
df['date'] = pd.to_datetime(df['date'])
df = df.drop_duplicates(subset=['symbol', 'date'], keep='last')
df.set_index('date', inplace=True)
print(f"Loaded {len(df)} rows.")


#Helper functions
def force_unique_columns(df):
    return df.loc[:, ~df.columns.duplicated()]

def resample_data(df, timeframe):
    agg_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}
    try:
        resampled = df.resample(timeframe).agg(agg_dict)
        return resampled.dropna()
    except:
        return df

def process_indicators(df):
    df = df.loc[:, ~df.columns.duplicated()]
    if not df.index.is_unique: df = df[~df.index.duplicated(keep='last')]
    if len(df) < 30: return df
    
    try:
        #Calculating oscilators
        df['RSI'] = df.ta.rsi(length=14)
        
        macd = df.ta.macd(fast=12, slow=26, signal=9)
        if macd is not None: df = pd.concat([df, macd], axis=1)
        
        stoch = df.ta.stoch(k=14, d=3, smooth_k=3)
        if stoch is not None: df = pd.concat([df, stoch], axis=1)
        
        df['CCI'] = df.ta.cci(length=20)

        #Signal strength
        def get_signal_data(row):
            score = 0
            
            
            try:
                if row['RSI'] < 30: score += 1      
                elif row['RSI'] > 70: score -= 1    
            except: pass

            try:
                k = row.get('STOCHk_14_3_3', 50)
                if k < 20: score += 1
                elif k > 80: score -= 1
            except: pass

            try:
                c = row['CCI']
                if c < -100: score += 1
                elif c > 100: score -= 1
            except: pass

            try:
                if row['MACD_12_26_9'] > row['MACDs_12_26_9']: score += 1
               
                else: 
                    score -= 1
            except: pass

            strength = score / 4.0

            if strength >= 0.5: label = "BUY"
            elif strength <= -0.5: label = "SELL"
            else: label = "HOLD"

            return pd.Series([label, strength])

        df[['Signal', 'Signal_Strength']] = df.apply(get_signal_data, axis=1)
        
    except Exception:
        pass
    
    return force_unique_columns(df)

#Processing oscilators

all_daily = []
all_weekly = []
all_monthly = []

unique_symbols = df['symbol'].unique()

for symbol in tqdm(unique_symbols):
    try:
        coin_df = df[df['symbol'] == symbol].copy().sort_index()

        #Daily
        d_df = process_indicators(coin_df.copy())
        d_df['symbol'] = symbol
        d_df = d_df.reset_index()
        if 'Signal' in d_df.columns:
            all_daily.append(d_df[['date', 'symbol', 'close', 'Signal', 'Signal_Strength']])

        #Weekly
        w_df = resample_data(coin_df, 'W')
        w_df = process_indicators(w_df)
        w_df['symbol'] = symbol
        w_df = w_df.reset_index()
        if 'Signal' in w_df.columns:
            all_weekly.append(w_df[['date', 'symbol', 'close', 'Signal', 'Signal_Strength']])

        #Monthly
        m_df = resample_data(coin_df, 'ME')
        m_df = process_indicators(m_df)
        m_df['symbol'] = symbol
        m_df = m_df.reset_index()
        if 'Signal' in m_df.columns:
            all_monthly.append(m_df[['date', 'symbol', 'close', 'Signal', 'Signal_Strength']])

    except: pass



output_folder = "crypto_final_csvs"
os.makedirs(output_folder, exist_ok=True)

def save_formatted_csv(data_list, filename):
    if not data_list: return
    
    final_df = pd.concat(data_list, ignore_index=True)
    final_df = final_df.dropna(subset=['Signal_Strength'])
    final_df = final_df.sort_values(by=['date', 'symbol'])
    final_df.columns = ['Date', 'Symbol', 'Close', 'Signal', 'Signal_Strength']
    
    path = os.path.join(output_folder, filename)
    final_df.to_csv(path, index=False)
    print(f"Saved {filename} ({len(final_df)} rows)")

save_formatted_csv(all_daily, "daily_signals.csv")
save_formatted_csv(all_weekly, "weekly_signals.csv")
save_formatted_csv(all_monthly, "monthly_signals.csv")

print("Done! Check 'crypto_final_csvs' folder.")