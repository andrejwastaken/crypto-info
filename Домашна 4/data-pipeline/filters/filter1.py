import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .base_filter import Filter
from .data_utils import parse_numeric_suffix


BASE_URL = "https://finance.yahoo.com/markets/crypto/all/"
TOTAL_COINS = 1300
BATCH_SIZE = 100
MAX_WORKERS = 13

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/108.0.0.0 Safari/537.36"
}

VALID_QUOTE_CURRENCIES = {"USDT", "USDC", "USD", "BTC", "ETH"}

# Filter thresholds
MIN_VOLUME = 100_000
MIN_CHANGE_52W = -95
MAX_CHANGE_52W = 2000


class Filter1(Filter):
    """
    Филтер 1: Автоматски преземете jа листата на наjвредните 1000 активни
    крипто валути
    
    Filters applied:
    - Valid quote currency (USDT, USDC, USD, BTC, ETH)
    - 24h volume >= 100,000
    - Circulating supply > 0
    - 52-week change between -95% and 2000%
    """
    
    order = 1

    def __init__(self):
        self.coins = []

    def fetch_page(self, start: int, count: int) -> str:
        params = {"start": start, "count": count}
        
        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page start={start}: {e}")
            return None

    def parse_table_row(self, row) -> Dict:
        cols = row.find_all("td")
        if len(cols) < 10:
            return None
        
        try:
            # extract symbol and validate quote currency
            symbol_text = cols[0].text.strip()
            symbol_parts = symbol_text.split("  ")
            if len(symbol_parts) < 2:
                return None
            
            symbol = symbol_parts[1]
            quote = symbol.split("-")[-1]
            
            if quote not in VALID_QUOTE_CURRENCIES:
                return None
            
            # extract basic info
            name = cols[1].text.strip()
            market_cap = parse_numeric_suffix(cols[6].text.strip())
            volume = parse_numeric_suffix(cols[8].text.strip())
            circ_supply = parse_numeric_suffix(cols[-3].text.strip())
            
            # extract 52w change percentage
            change_52w_text = cols[-2].text.strip().replace("%", "")
            if change_52w_text and change_52w_text != "--":
                change_52w = float(change_52w_text)
            else:
                return None
            
            # apply filters
            if volume < MIN_VOLUME:
                return None
            
            if circ_supply <= 0:
                return None
            
            if not (MIN_CHANGE_52W < change_52w < MAX_CHANGE_52W):
                return None
            
            return {
                "symbol": symbol,
                "name": name,
                "change_52w": change_52w,
                "circulating_supply": circ_supply,
                "volume": volume,
                "market_cap": market_cap,
            }
            
        except (ValueError, IndexError, AttributeError):
            return None

    def parse_html(self, html_content: str) -> List[Dict]:
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            table = soup.find("table")
            
            if not table:
                return []
            
            rows = table.find_all("tr")[1:]  # Skip header row
            if not rows:
                return []
            
            extracted = []
            for row in rows:
                coin_data = self.parse_table_row(row)
                if coin_data:
                    extracted.append(coin_data)
            
            return extracted
            
        except Exception as e:
            print(f"Parse failed: {e}")
            return []

    def process_batch(self, start_index: int) -> List[Dict]:
        html = self.fetch_page(start_index, BATCH_SIZE)
        return self.parse_html(html) if html else []

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the filter to scrape and filter cryptocurrencies.
        """
        print("Starting Filter 1: Scraping cryptocurrencies...")
        start_time = time.time()
        
        start_indices = range(0, TOTAL_COINS, BATCH_SIZE)
        
        # fetch batches in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.process_batch, start) 
                for start in start_indices
            ]
            
            for future in as_completed(futures):
                try:
                    batch_coins = future.result()
                    if batch_coins:
                        self.coins.extend(batch_coins)
                except Exception as e:
                    print(f"Batch processing failed: {e}")
        
        elapsed = time.time() - start_time
        print(f"Filter 1 complete: {len(self.coins)} coins after filtering")
        print(f"Execution time: {elapsed:.2f} seconds")
        
        return pd.DataFrame(self.coins)
