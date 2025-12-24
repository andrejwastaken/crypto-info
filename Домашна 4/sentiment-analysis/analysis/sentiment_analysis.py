import pandas as pd
import numpy as np
from transformers import pipeline
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
from pathlib import Path
import ast
from difflib import get_close_matches
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import os

# Add scrapers directory to path
sys.path.append(str(Path(__file__).parent.parent / "scrapers"))

#Import the scraper aggregator
try:
    from scrapers_aggregator import scrape_all_news
except ImportError:
    print("Error: Could not import scrape_all_news. Make sure scrapers-aggregator.py exists.")
    exit()


CONFIDENCE_THRESHOLD = 0.7 
SIMILARITY_THRESHOLD = 0.85
MIN_ARTICLES_THRESHOLD = 5
SYMBOL_MATCH_CUTOFF = 0.6



df = scrape_all_news()


if df.empty:
    print("Error: No news data collected.")
    exit()

df['title'] = df['title'].astype(str)
print(f"Successfully loaded {len(df)} rows.")

# Finbert model config
sentiment_pipe = pipeline(
    "sentiment-analysis", 
    model="ProsusAI/finbert", 
    top_k=None,
    device=-1 
)

# Analysis logic
def get_sentiment(text):
    try:
        result = sentiment_pipe(str(text)[:512])[0]
        scores = {item['label']: item['score'] for item in result}
        
        pos = scores.get('positive', 0)
        neg = scores.get('negative', 0)
        
        compound_score = pos - neg
        max_label = max(scores, key=scores.get)
        
        return pd.Series([max_label, compound_score])
    except Exception as e:
        return pd.Series(["error", 0.0])


tqdm.pandas(desc="Analyzing Sentiment")
print("Running Sentiment Analysis...")
df[['sentiment_label', 'sentiment_score']] = df['title'].progress_apply(get_sentiment)

# Confidence filter
initial_count = len(df)
# Keep rows with high confidence OR rows that are "general news" (empty symbols)
df = df[(df['sentiment_score'].abs() > CONFIDENCE_THRESHOLD) | (df['symbols'] == '[]')].copy()
dropped_conf = initial_count - len(df)
print(f"Confidence Filter: Dropped {dropped_conf} rows with score <= {CONFIDENCE_THRESHOLD} (kept general news). Remaining: {len(df)}")

# Similarity filter
df = df.reset_index(drop=True)

if len(df) > 0:
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['title'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    indices_to_drop = set()
    
    for i in range(len(df)):
        if i in indices_to_drop: continue
        
        for j in range(i + 1, len(df)):
            if j in indices_to_drop: continue
            
            if cosine_sim[i, j] > SIMILARITY_THRESHOLD:
                indices_to_drop.add(j)
    
    rows_before_sim = len(df)
    df = df.drop(list(indices_to_drop))
    print(f"Similarity Filter: Dropped {len(indices_to_drop)} near-duplicate rows.")
else:
    print("Similarity Filter: Skipped (No data left after confidence filter).")



#Symbol mapping and db matching 

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "crypto_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT symbol FROM ohlcv_data;")
    db_symbols = set([row[0] for row in cursor.fetchall()])
    cursor.close()
    conn.close()
    
  
except Exception as e:
    
    db_symbols = set()

if db_symbols:
    # Parse symbols and count occurrences
    def parse_symbols(x):
        # Convert to string first to handle any type
        x_str = str(x) if x is not None else ''
        
        # Check for NaN string representation
        if x_str in ['nan', 'None', '']:
            return []
        
        # Check for empty list
        if x_str in ['[]', '']:
            return []
        
        # Try to parse as Python literal
        try:
            result = ast.literal_eval(x_str)
            # Ensure it's a list
            if isinstance(result, list):
                return result
            return [result] if result else []
        except:
            return []
    
    df['symbols_list'] = df['symbols'].apply(parse_symbols)
    df_exploded = df.explode('symbols_list')
    coin_counts = df_exploded[df_exploded['symbols_list'] != '']['symbols_list'].value_counts()
    
    # Get symbols from news
    news_symbols = set(coin_counts.index)
    
    # Find matches and non-matches
    matched = news_symbols.intersection(db_symbols)
    not_matched = news_symbols - db_symbols
    

    print(f"Total unique symbols in news: {len(news_symbols)}")
    print(f"Already matched with DB: {len(matched)}")
    print(f"Not matched with DB: {len(not_matched)}\n")
    
    # Create symbol mapping
    symbol_mapping = {}
    

    
    for news_symbol in sorted(not_matched):
        # Check if coin has less than MIN_ARTICLES_THRESHOLD articles
        if coin_counts[news_symbol] < MIN_ARTICLES_THRESHOLD:
            symbol_mapping[news_symbol] = None
            print(f"  {news_symbol} → REMOVED (only {coin_counts[news_symbol]} articles, < {MIN_ARTICLES_THRESHOLD} threshold)")
        else:
            closest = get_close_matches(news_symbol, db_symbols, n=1, cutoff=SYMBOL_MATCH_CUTOFF)
            
            if closest:
                symbol_mapping[news_symbol] = closest[0]
                print(f"  {news_symbol} → {closest[0]} (mapped)")
            else:
                symbol_mapping[news_symbol] = None
                print(f"  {news_symbol} → REMOVED (no close match found)")
    

    
    def map_symbols(symbols_str):
        """Replace symbols with their closest matches or remove unmatched ones"""
        # Convert to string first to handle any type
        x_str = str(symbols_str) if symbols_str is not None else ''
        
        # Check for NaN string representation
        if x_str in ['nan', 'None', '']:
            return []
            
        # Keep empty symbol lists (for general news)
        if x_str in ['[]', '']:
            return []
        
        try:
            symbols = ast.literal_eval(x_str) if isinstance(x_str, str) else x_str
        except:
            return []
        
       
        mapped_symbols = []
        for symbol in symbols:
            if symbol in matched:
                # Already in DB, keep as is
                mapped_symbols.append(symbol)
            elif symbol in symbol_mapping and symbol_mapping[symbol] is not None:
                # Has a close match, replace it
                mapped_symbols.append(symbol_mapping[symbol])
            # If no match or < MIN_ARTICLES_THRESHOLD articles skip it
        
        return mapped_symbols
    
    # Apply mapping
    initial_count = len(df)
    df['symbols_mapped'] = df['symbols'].apply(map_symbols)
    
    # Keep articles with at least one valid symbol or general news
    df_final = df[(df['symbols_mapped'].apply(len) > 0) | (df['symbols'].isin(['[]', '']))].copy()
    
    # Remove duplicates within each article's symbol list
    df_final['symbols_mapped'] = df_final['symbols_mapped'].apply(lambda x: list(set(x)))
    
    # Convert back to string format
    df_final['symbols'] = df_final['symbols_mapped'].apply(str)
    df_final = df_final.drop(columns=['symbols_mapped', 'symbols_list'])
    
    print(f"\nArticles before mapping: {initial_count}")
    print(f"Articles after mapping: {len(df_final)}")
    print(f"Articles dropped (no valid symbols): {initial_count - len(df_final)}")
    
    # Final verification
    df_final['symbols_list'] = df_final['symbols'].apply(parse_symbols)
    df_final_with_symbols = df_final[df_final['symbols_list'].apply(len) > 0]
    df_final_exploded = df_final_with_symbols.explode('symbols_list')
    final_coin_counts = df_final_exploded['symbols_list'].value_counts()
    
    general_news_count = len(df_final[df_final['symbols'] == '[]'])
    
    print(f"\n\nFINAL STATISTICS:")
    print("=" * 60)
    print(f"Total articles: {len(df_final)}")
    print(f"  - Articles with symbols: {len(df_final_with_symbols)}")
    print(f"  - General news (empty symbols '[]'): {general_news_count}")
    print(f"\nUnique coins: {len(final_coin_counts)}")
    print(f"All coins in database: {all(coin in db_symbols for coin in final_coin_counts.index) if len(final_coin_counts) > 0 else True}")
    
    print(f"\n\nFINAL COIN DISTRIBUTION:")
    print("=" * 60)
    for coin, count in final_coin_counts.items():
        print(f"  {coin}: {count} articles")
    
    # Clean up temporary column
    df_final = df_final.drop(columns=['symbols_list'])
    df = df_final
else:
    print("Skipping symbol mapping (no database connection)")


print("\n" + "=" * 60)
print("ANALYSIS & FILTERING COMPLETE!")
print("=" * 60)
print(f"Final Row Count: {len(df)}")
print("-" * 60)
if not df.empty:
    print(df[['title', 'symbols', 'sentiment_label', 'sentiment_score']].head())

#Store to DB


try:
    # Prepare data for database insertion
    df_to_insert = df.copy()
    
    # Convert symbols from list string to list for ARRAY column
    def format_symbols_for_db(symbols_str):
        if pd.isna(symbols_str) or symbols_str in ['[]', '']:
            return []
        try:
            symbols_list = ast.literal_eval(symbols_str)
            if isinstance(symbols_list, list):
                return symbols_list
            return []
        except:
            return []
    
    df_to_insert['symbols'] = df_to_insert['symbols'].apply(format_symbols_for_db)
    
    # Convert date to proper format if needed
    df_to_insert['date'] = pd.to_datetime(df_to_insert['date'], errors='coerce')
    
    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "crypto_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS news_sentiment (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL UNIQUE,
        symbols TEXT[],
        date TIMESTAMP,
        link TEXT,
        img_src TEXT,
        sentiment_label VARCHAR(20),
        sentiment_score FLOAT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    
    # Insert data using execute_values for cleaner and faster insertion
    insert_query = """
    INSERT INTO news_sentiment (title, symbols, date, link, img_src, sentiment_label, sentiment_score)
    VALUES %s
    """
    
    data_to_insert = []
    for _, row in df_to_insert.iterrows():
        data_to_insert.append((
            row['title'],
            row['symbols'],
            row['date'] if pd.notna(row['date']) else None,
            row.get('link', None),
            row.get('img_src', None),
            row['sentiment_label'],
            float(row['sentiment_score'])
        ))
        
    extras.execute_values(cursor, insert_query, data_to_insert)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Successfully inserted {len(data_to_insert)} articles into database")
    print(f"✓ Table: news_sentiment")
    
    # Show sample of formatted data
    print(f"\n\nSAMPLE OF STORED DATA:")
    print("=" * 60)
    print(df_to_insert[['title', 'symbols', 'sentiment_label', 'sentiment_score']].head(10))
    
except Exception as e:
    print(f"✗ Error storing data to database: {e}")
    print("Data was not saved to database.")

print("\n" + "=" * 60)
print("PROCESS COMPLETE!")
print("=" * 60)
    