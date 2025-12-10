from math import nan
import time
import pandas as pd
import numpy as np
import dateparser
import re  # Added for regex
import concurrent.futures
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL_TEMPLATE = "https://www.binance.com/en/square/news/{}"
KEYS = [
    "doge-news", "ethereum-news", "bnb-news", 
    "whale-alert", "pepe-news", "shib-news", 
    "xrp-news", "solana-news", "bitcoin-news"
]

KEY_TO_SYMBOL_MAP = {
    "doge-news": "DOGE",
    "ethereum-news": "ETH",
    "bnb-news": "BNB",
    "pepe-news": "PEPE",
    "shib-news": "SHIB",
    "xrp-news": "XRP",
    "solana-news": "SOL",
    "bitcoin-news": "BTC"
}

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def parse_relative_time(time_str):
    if not time_str:
        return datetime.now()
    time_str = time_str.strip()
    dt = dateparser.parse(time_str)
    return dt if dt else datetime.now()

def scrape_category(key):
    driver = init_driver()
    try:
        url = BASE_URL_TEMPLATE.format(key)
        print(f"processing: {key}")
        driver.get(url)
        
        time.sleep(3) 
        
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"\t{key} scrolled {i+1}/3...")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles_data = []
        
        potential_articles = soup.find_all('div', class_=lambda x: x and 'css-' in x) 
        
        valid_articles = []
        for art in potential_articles:
            link_tag = art.find('a', href=True)
            if link_tag and ('/square/news/' in link_tag['href'] or '/square/post/' in link_tag['href']):
                if len(art.get_text()) > 20: 
                    valid_articles.append(art)

        valid_articles = list(set(valid_articles))
        print(f"\t{key} found {len(valid_articles)} potential articles.")

        for art in valid_articles:
            try:
                # get title
                title_tag = art.find(['h3', 'h2'])
                if not title_tag:
                    link_tag = art.find('a', href=True)
                    title = link_tag.get_text(strip=True) if link_tag else "No Title"
                else:
                    title = title_tag.get_text(strip=True)
                
                # get link
                link_tag = art.find('a', href=True)
                link = "https://www.binance.com" + link_tag['href'] if link_tag else "No Link"
                
                # get date
                all_text_nodes = art.stripped_strings
                date_obj = datetime.now()
                for text in all_text_nodes:
                    if any(x in text for x in ['ago', 'min', 'hour', 'day', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']):
                        parsed = parse_relative_time(text)
                        if parsed:
                            date_obj = parsed
                            break
                
                symbols = []
                text_content = art.get_text()
                
                # Regex Explanation:
                # \$          -> Matches the literal '$' character
                # (?![0-9])   -> Negative Lookahead: Asserts that what follows is NOT a number (Filters out $4000)
                # ([A-Za-z]{2,10}) -> Captures 2 to 10 letters (e.g., BTC, DOGE).
                # \b          -> Word boundary (Ensures we don't capture partial words)
                
                found_matches = re.findall(r'\$(?![0-9])([A-Za-z]{2,10})\b', text_content)
                
                # uppercase and unique
                for sym in found_matches:
                    symbols.append(sym.upper())
                
                # add key from category used in url
                if key != "whale-alert" and key in KEY_TO_SYMBOL_MAP:
                    mandatory_symbol = KEY_TO_SYMBOL_MAP[key]
                    if mandatory_symbol not in symbols:
                        symbols.insert(0, mandatory_symbol)
                
                symbols = list(set(symbols))

                articles_data.append({
                    "title": title,
                    "symbols": symbols,
                    "date": date_obj,
                    "link": link,
                    "img_src": np.nan
                })
                
            except Exception as e:
                print(f"Error parsing article: {e}") 
                continue

        return articles_data
    except Exception as e:
        print(f"Error processing {key}: {e}")
        return []
    finally:
        driver.quit()

def scrape_binance_news():
    all_data = []

    max_workers = 4 
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scrape_category, KEYS)
        for res in results:
            all_data.extend(res)

    df = pd.DataFrame(all_data)
    
    if not df.empty:
        df = df.drop_duplicates(subset=['link'])
    
    print("scraping complete")
    return df

def main():
    print("This script exposes scrape_binance_news(). Run scrapers-aggregator.py to execute.")

if __name__ == "__main__":
    main()