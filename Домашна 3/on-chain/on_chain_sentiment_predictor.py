import pandas as pd
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import ast
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

_db_engine = None

def get_engine():
    global _db_engine
    if _db_engine is not None:
        return _db_engine

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_port, db_name]):
        raise RuntimeError("Database credentials are missing.")

    encoded_password = quote_plus(db_password)
    connection_str = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
    _db_engine = create_engine(connection_str, pool_size=10, max_overflow=20)
    return _db_engine

def init_db():
    engine = get_engine()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS on_chain_sentiment_predictions (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        date DATE NOT NULL,
        predicted_close NUMERIC,
        predicted_change_pct NUMERIC
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("Database table checked/created.")

def get_sentiment_analysis():
    print("Fetching news sentiment data...")
    engine = get_engine()
    query = "SELECT * FROM news_sentiment"
    df = pd.read_sql(query, engine, parse_dates=['date'])
    
    if 'symbols' in df.columns:
        def clean_parse(x):
            if isinstance(x, list): 
                return x
            try:
                return ast.literal_eval(x)
            except (ValueError, SyntaxError):
                return [] 

        df['symbols'] = df['symbols'].apply(clean_parse)
        
        df = df.explode('symbols')
        
        df = df.rename(columns={'symbols': 'symbol'})
        
        df = df.dropna(subset=['symbol'])
        df['symbol'] = df['symbol'].astype(str).str.strip()

    return df

def get_on_chain_metrics():
    print("Fetching on-chain metrics...")
    engine = get_engine()
    query = "SELECT * FROM onchain_metrics"
    df = pd.read_sql(query, engine, parse_dates=['date'])

    return df

def merge_dfs(sentiment_df, on_chain_df, close_df):
    print("Merging datasets...")
    sentiment_subset = sentiment_df[['symbol', 'date', 'sentiment_score']]

    merged_step_1 = pd.merge(
        on_chain_df, 
        sentiment_subset, 
        on=['symbol', 'date'], 
        how='inner'
    )

    final_merged_df = pd.merge(
        merged_step_1, 
        close_df, 
        on=['symbol', 'date'], 
        how='inner'
    )

    return final_merged_df

def get_close():
    engine=get_engine()
    query='SELECT close,symbol,date from ohlcv_data'
    df=pd.read_sql(query, engine, parse_dates=['date'])
    return df
    
def predict(df):
    print(f"Starting prediction pipeline with {len(df)} rows...")
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['symbol', 'date'])
    df['target_next_close'] = df.groupby('symbol')['close'].shift(-1)

    EXCLUDE_COLS = {
        'id',
        'symbol',
        'date',
        'target_next_close'
        
    }

    feature_cols = [
        c for c in df.columns
        if c not in EXCLUDE_COLS 
    ]

    train_df = df.dropna(subset=['target_next_close'])
    latest_df = (
        df[df['target_next_close'].isna()]
        .groupby('symbol')
        .tail(1)
    )

    if train_df.empty or latest_df.empty:
        print("Not enough data to train or predict.")
        return

    X_train = train_df[feature_cols]
    y_train = train_df['target_next_close']

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )

    cv_scores = cross_val_score(
        model,
        X_train_scaled,
        y_train,
        cv=tscv,
        scoring='r2'
    )

    print(f"CV R² scores: {cv_scores}")
    print(f"Mean CV R²: {cv_scores.mean():.4f}")

    model.fit(X_train_scaled, y_train)

    X_latest = latest_df[feature_cols]
    X_latest_scaled = scaler.transform(X_latest)

    latest_df = latest_df.copy()
    latest_df['predicted_close'] = model.predict(X_latest_scaled)

    latest_df['predicted_change_pct'] = (
        (latest_df['predicted_close'] - latest_df['close'])
        / latest_df['close']
    ) * 100

    latest_df['date'] = latest_df['date'] + pd.Timedelta(days=1)

    db_output = latest_df[
        ['symbol', 'date', 'predicted_close', 'predicted_change_pct']
    ]

    try:
        engine = get_engine()
        db_output.to_sql(
            'onchain_sentiment_predictions',
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
       
    except Exception as e:
        print(f"Exception")


if __name__ == "__main__":
    load_dotenv()

    try:
        init_db()
        sentiment_df = get_sentiment_analysis()
        on_chain_df = get_on_chain_metrics()
        close_df=get_close()
        if not sentiment_df.empty and not on_chain_df.empty:
            training_data = merge_dfs(sentiment_df, on_chain_df,close_df)
            
            if not training_data.empty:
                predict(training_data)
            else:
                print("Df is empty")
        else:
            print("Error")

    except Exception as e:
        print(f"An error occurred: {e}")