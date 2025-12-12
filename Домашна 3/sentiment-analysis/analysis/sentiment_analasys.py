import pandas as pd
import numpy as np
from transformers import pipeline
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
# Strategy 3: Drop if score is between -0.2 and 0.2 (Weak signal)
CONFIDENCE_THRESHOLD = 0.7 

# Strategy 2: Drop if similarity is > 0.85 (85% similar)
SIMILARITY_THRESHOLD = 0.85

# --- PART 1: LOAD DATA ---
try:
    df = pd.read_csv("news.csv")
    # Ensure title is string to avoid vectorizer errors
    df['title'] = df['title'].astype(str)
    print(f"Successfully loaded {len(df)} rows.")
except FileNotFoundError:
    print("Error: 'news.csv' not found.")
    exit()

# --- PART 2: SETUP FINBERT ---
print("Loading FinBERT model...")
sentiment_pipe = pipeline(
    "sentiment-analysis", 
    model="ProsusAI/finbert", 
    top_k=None,
    device=-1 
)

# --- PART 3: DEFINE ANALYSIS LOGIC ---
def get_sentiment(text):
    try:
        result = sentiment_pipe(str(text)[:512])[0]
        scores = {item['label']: item['score'] for item in result}
        
        pos = scores.get('positive', 0)
        neg = scores.get('negative', 0)
        
        # Compound Score: -1 (Bearish) to +1 (Bullish)
        compound_score = pos - neg
        max_label = max(scores, key=scores.get)
        
        return pd.Series([max_label, compound_score])
    except Exception as e:
        return pd.Series(["error", 0.0])

# --- PART 4: RUN ANALYSIS ---
tqdm.pandas(desc="Analyzing Sentiment")
print("Running Sentiment Analysis...")
df[['sentiment_label', 'sentiment_score']] = df['title'].progress_apply(get_sentiment)


# ==========================================
# IMPLEMENTING YOUR REQUESTED STRATEGIES
# ==========================================

print(f"\n--- Applying Filters (Start Rows: {len(df)}) ---")

# --- STRATEGY 3: CONFIDENCE FILTER ---
# "Drop the ones where the model isnt sure ie it has near 0 score"
# We keep rows where the absolute score is GREATER than the threshold.
initial_count = len(df)
df = df[df['sentiment_score'].abs() > CONFIDENCE_THRESHOLD].copy()
dropped_conf = initial_count - len(df)
print(f"Strategy 3 (Confidence > {CONFIDENCE_THRESHOLD}): Dropped {dropped_conf} weak/neutral rows.")


# --- STRATEGY 2: COSINE SIMILARITY FILTER ---
# "If 2 news are very similar drop one"
print("Strategy 2 (Cosine Similarity): Calculating similarity matrix...")

# 1. Reset index to ensure alignment
df = df.reset_index(drop=True)

if len(df) > 0:
    # 2. Vectorize the titles (Convert text to numbers)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['title'])

    # 3. Calculate Cosine Similarity Matrix
    # Note: This can be memory intensive for very large datasets (>10k rows)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 4. Identify duplicates
    # We create a set to store indices of rows to drop
    indices_to_drop = set()

    # Loop through the upper triangle of the matrix to avoid checking (A,B) and (B,A)
    # We only check i vs j where j > i
    for i in range(len(df)):
        if i in indices_to_drop: continue # Skip if already marked for deletion

        for j in range(i + 1, len(df)):
            if j in indices_to_drop: continue # Skip if already marked

            # If similarity is higher than threshold, mark 'j' for deletion
            if cosine_sim[i, j] > SIMILARITY_THRESHOLD:
                indices_to_drop.add(j)
                # Optional: Print what is being dropped to verify
                # print(f"Dropping duplicate: '{df.iloc[j]['title']}' (Similar to: '{df.iloc[i]['title']}')")

    # 5. Drop the rows
    rows_before_sim = len(df)
    df = df.drop(list(indices_to_drop))
    print(f"Strategy 2: Dropped {len(indices_to_drop)} near-duplicate rows.")

else:
    print("Strategy 2: Skipped (No data left after confidence filter).")

# ==========================================
# FINAL OUTPUT
# ==========================================

# --- PART 5: SAVE RESULTS ---
output_filename = "news_filtered_sim_conf.csv"
df.to_csv(output_filename, index=False)

print("\nAnalysis & Filtering Complete!")
print(f"Final Row Count: {len(df)}")
print(f"Saved to {output_filename}")
print("-" * 30)
if not df.empty:
    print(df[['title', 'sentiment_label', 'sentiment_score']].head())