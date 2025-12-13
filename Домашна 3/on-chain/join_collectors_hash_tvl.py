import pandas as pd
import os
from collectors_tvl import get_tvl_data
from collectors_hash import fetch_security_data, get_symbols_from_db

def join_csvs():
    output_file = "joined_crypto_data.csv"

    print("Fetching TVL Data")
    df_tvl = get_tvl_data()
    
    print("\nFetching Security Data")
    
    symbols = get_symbols_from_db()
    df_security = fetch_security_data(symbols)

    if df_tvl.empty:
        print("No TVL data found.")
        return

    if df_security.empty:
        
        
        df_security = pd.DataFrame(columns=['time', 'asset', 'Metric_Name', 'Security_Value'])

   
    
    if not df_security.empty:
        df_security['time'] = pd.to_datetime(df_security['time'])
        
        df_security['join_date'] = df_security['time'].dt.date
        df_security['join_symbol'] = df_security['asset'].str.upper()
    
    df_tvl['date'] = pd.to_datetime(df_tvl['date'])
    df_tvl['join_date'] = df_tvl['date'].dt.date
    df_tvl['join_symbol'] = df_tvl['symbol'].str.upper()

   
    
    if not df_security.empty:
        
        merged_df = pd.merge(
            df_tvl,
            df_security,
            on=['join_date', 'join_symbol'],
            how='left'
        )
    else:
        merged_df = df_tvl.copy()
        merged_df['Metric_Name'] = None
        merged_df['Security_Value'] = None

  
    final_columns = [
        'join_date',          
        'join_symbol',        
        'chain',              
        'tvl_usd',            
        'Metric_Name',        
        'Security_Value'      
    ]
    
   
    for col in final_columns:
        if col not in merged_df.columns:
            merged_df[col] = None

    final_df = merged_df[final_columns].copy()
    
 
    final_df.rename(columns={
        'join_date': 'date',
        'join_symbol': 'symbol',
        'Metric_Name': 'security_metric',
        'Security_Value': 'security_value'
    }, inplace=True)

    
    final_df = final_df.fillna(0)

  
    final_df.sort_values(by=['symbol', 'date'], inplace=True)

 
    final_df.to_csv(output_file, index=False)
    
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    join_csvs()
