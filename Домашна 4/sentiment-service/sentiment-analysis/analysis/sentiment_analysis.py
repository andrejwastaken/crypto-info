import os
import sys
import ast
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from difflib import get_close_matches

import pandas as pd
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
from psycopg2 import extras
from sqlalchemy import text
sys.path.append(str(Path(__file__).parent.parent.parent))
from database.database import DatabaseManager

sys.path.append(str(Path(__file__).parent.parent / "scrapers"))
try:
    from scrapers_aggregator import scrape_all_news
except ImportError:
    pass 


load_dotenv()



class Config:


    CONFIDENCE_THRESHOLD = 0.5 
    SIMILARITY_THRESHOLD = 0.85
    MIN_ARTICLES_THRESHOLD = 5
    SYMBOL_MATCH_CUTOFF = 0.6
    
    MODEL_NAME = "ProsusAI/finbert"

# Strategy interface
class PipelineStep(ABC):
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class SentimentModelSingleton:
   
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentModelSingleton, cls).__new__(cls)
            cls._pipeline = pipeline(
                "sentiment-analysis", 
                model=Config.MODEL_NAME, 
                top_k=None,
                device=-1 
            )
        return cls._instance

    def get_pipeline(self):
        return self._pipeline



class DataIngestion(PipelineStep):
    def __init__(self, light_mode: bool = False):
        self.light_mode = light_mode

    def process(self, df: pd.DataFrame = None) -> pd.DataFrame:
        print("Ingesting Data...")
      
        if df is not None and not df.empty:
            return df
        
        try:
            df = scrape_all_news(light_mode=self.light_mode)
        except NameError:
            print("Scraper module not found.")
            return pd.DataFrame()
        except TypeError:
            print("scrape_all_news does not support light_mode. Running default.")
            df = scrape_all_news()

        if df.empty:
            print("Error: No news data collected.")
            return pd.DataFrame()
            
        df['title'] = df['title'].astype(str)
        print(f"Successfully loaded {len(df)} rows.")
        return df

class SentimentAnalysis(PipelineStep):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        print("Running Sentiment Analysis...")
        
        model = SentimentModelSingleton().get_pipeline()
        
        def get_sentiment(text):
            try:
                result = model(str(text)[:512])[0]
                scores = {item['label']: item['score'] for item in result}
                pos = scores.get('positive', 0)
                neg = scores.get('negative', 0)
                return pd.Series([max(scores, key=scores.get), pos - neg])
            except Exception:
                return pd.Series(["error", 0.0])

        tqdm.pandas(desc="Analyzing")
        df[['sentiment_label', 'sentiment_score']] = df['title'].progress_apply(get_sentiment)
        return df

class ConfidenceFilter(PipelineStep):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        print("Filtering by Confidence...")
        initial_count = len(df)
        
        df_filtered = df[(df['sentiment_score'].abs() > Config.CONFIDENCE_THRESHOLD) | (df['symbols'] == '[]')].copy()
        print(f"Dropped {initial_count - len(df_filtered)} rows.")
        return df_filtered

class SimilarityFilter(PipelineStep):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        print("Filtering Duplicates...")
        
        df = df.reset_index(drop=True)
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df['title'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        indices_to_drop = set()
        for i in range(len(df)):
            if i in indices_to_drop: continue
            for j in range(i + 1, len(df)):
                if j in indices_to_drop: continue
                if cosine_sim[i, j] > Config.SIMILARITY_THRESHOLD:
                    indices_to_drop.add(j)
        
        df_filtered = df.drop(list(indices_to_drop))
        
        return df_filtered

class SymbolMapping(PipelineStep):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        print("Mapping Symbols...")
        
       
        try:
            engine = DatabaseManager.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT DISTINCT symbol FROM ohlcv_data;"))
                db_symbols = set([row[0] for row in result])
        except Exception as e:
            print(f"DB Connection failed: {e}")
            return df 

        if not db_symbols:
            return df

        # Helper to parse string lists
        def parse_symbols(x):
           
            if isinstance(x, list): return x
            if isinstance(x, np.ndarray): return x.tolist()
            
            if pd.isna(x) or x in ['[]', '', 'nan', 'None']: return []
            try:
                res = ast.literal_eval(str(x))
                return res if isinstance(res, list) else []
            except: return []

        df['symbols_list'] = df['symbols'].apply(parse_symbols)
        
        
        df_exploded = df.explode('symbols_list')
        coin_counts = df_exploded[df_exploded['symbols_list'].astype(bool)]['symbols_list'].value_counts()
        
       
        news_symbols = set(coin_counts.index)
        not_matched = news_symbols - db_symbols
        matched = news_symbols.intersection(db_symbols)
        symbol_mapping = {}

        for sym in not_matched:
            if coin_counts[sym] < Config.MIN_ARTICLES_THRESHOLD:
                symbol_mapping[sym] = None
            else:
                closest = get_close_matches(sym, db_symbols, n=1, cutoff=Config.SYMBOL_MATCH_CUTOFF)
                symbol_mapping[sym] = closest[0] if closest else None

        
        def map_row(symbols):
            mapped = []
            for s in symbols:
                if s in matched: mapped.append(s)
                elif s in symbol_mapping and symbol_mapping[s]: mapped.append(symbol_mapping[s])
            return list(set(mapped))

        df['symbols_mapped'] = df['symbols_list'].apply(map_row)
        
        
        df_final = df[(df['symbols_mapped'].apply(len) > 0) | (df['symbols'] == '[]')].copy()
        df_final['symbols'] = df_final['symbols_mapped'].apply(str)
        
        return df_final.drop(columns=['symbols_list', 'symbols_mapped'])

class DatabaseStorage(PipelineStep):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        print("Storing to Database...")
        
        try:
            
            engine=DatabaseManager.get_engine()
            
            create_table_sql="""
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
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
                
                
                try:
                    conn.execute(text("ALTER TABLE news_sentiment ADD CONSTRAINT news_sentiment_title_key UNIQUE (title);"))
                    conn.commit()
                except Exception:
                    pass 

            # Prepare data
            def format_sym(x):
                try: return ast.literal_eval(x) if isinstance(x, str) else []
                except: return []

            data_to_insert = []
            for _, row in df.iterrows():
                data_to_insert.append((
                    row['title'],
                    format_sym(row['symbols']),
                    pd.to_datetime(row['date']) if pd.notna(row['date']) else None,
                    row.get('link'),
                    row.get('img_src'),
                    row['sentiment_label'],
                    float(row['sentiment_score'])
                ))

            raw_conn = engine.raw_connection()
            try:
                cursor = raw_conn.cursor()
                insert_query = """
                INSERT INTO news_sentiment (title, symbols, date, link, img_src, sentiment_label, sentiment_score)
                VALUES %s
                ON CONFLICT (title) DO NOTHING
                """

             
                extras.execute_values(cursor, insert_query, data_to_insert, page_size=500)
                raw_conn.commit()
                print(f"Stored {len(data_to_insert)} articles.")
            finally:
                raw_conn.close()
        except Exception as e:
            print(f"Storage failed: {e}")
            
        return df


class SentimentPipeline:
   
    def __init__(self):
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep):
        self.steps.append(step)

    def run(self):
        data = None
        for step in self.steps:
            data = step.process(data)
            if data is not None and data.empty and not isinstance(step, DataIngestion):
                print("Dataframe is empty.")
                break
        print("Pipeline execution finished.")
        return data

def run_pipeline(light_mode: bool = False):
    pipeline = SentimentPipeline()
    
    pipeline.add_step(DataIngestion(light_mode=light_mode))
    pipeline.add_step(SentimentAnalysis())
    pipeline.add_step(ConfidenceFilter())
    pipeline.add_step(SimilarityFilter())
    pipeline.add_step(SymbolMapping())
    pipeline.add_step(DatabaseStorage())
    
    return pipeline.run()

def main():
    run_pipeline()

if __name__ == "__main__":
    main()
