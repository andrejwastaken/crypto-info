import time
import concurrent.futures
from typing import List
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from scraper_utils import parse_relative_time, extract_symbols_from_text, build_article_dict

BASE_URL = "https://www.binance.com"
BASE_URL_TEMPLATE = "https://www.binance.com/en/square/news/{}"

# category keys for scraping
CATEGORIES = [
    "doge-news", "ethereum-news", "bnb-news", 
    "whale-alert", "pepe-news", "shib-news", 
    "xrp-news", "solana-news", "bitcoin-news"
]

# mapping of category keys to mandatory symbols
CATEGORY_SYMBOL_MAP = {
    "doge-news": "DOGE",
    "ethereum-news": "ETH",
    "bnb-news": "BNB",
    "pepe-news": "PEPE",
    "shib-news": "SHIB",
    "xrp-news": "XRP",
    "solana-news": "SOL",
    "bitcoin-news": "BTC"
}

def init_driver() -> webdriver.Chrome:
    """initializes headless chrome driver with proper configuration."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )


def scroll_page(driver: webdriver.Chrome, num_scrolls: int = 3, delay: float = 2.0):
    for i in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"\tScrolled {i+1}/{num_scrolls}...")
        time.sleep(delay)


def filter_valid_articles(soup: BeautifulSoup) -> List:
    potential_articles = soup.find_all('div', class_=lambda x: x and 'css-' in x)
    
    valid_articles = []
    for art in potential_articles:
        link_tag = art.find('a', href=True)
        if link_tag and ('/square/news/' in link_tag['href'] or '/square/post/' in link_tag['href']):
            if len(art.get_text()) > 20:  
                valid_articles.append(art)
    
    # remove duplicates
    return list(set(valid_articles))


def extract_article_date(article_element) -> datetime:
    all_text_nodes = article_element.stripped_strings
    date_indicators = ['ago', 'min', 'hour', 'day', 'Dec', 'Jan', 'Feb', 'Mar', 
                      'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    
    for text in all_text_nodes:
        if any(indicator in text for indicator in date_indicators):
            parsed = parse_relative_time(text)
            if parsed:
                return parsed
    
    return datetime.now()


def extract_symbols(article_element, category: str) -> List[str]:
    """
    extract cryptocurrency symbols from article text.
    includes category-based mandatory symbol if applicable.
    """
    text_content = article_element.get_text()
    
    # extract symbols using regex pattern from utils
    symbols = extract_symbols_from_text(text_content)
    
    # add mandatory symbol for non-whale-alert categories
    if category != "whale-alert" and category in CATEGORY_SYMBOL_MAP:
        mandatory_symbol = CATEGORY_SYMBOL_MAP[category]
        if mandatory_symbol not in symbols:
            symbols.insert(0, mandatory_symbol)
    
    return symbols


def parse_article_element(article_element, category: str) -> dict:
    """Parse a single article element into structured dict."""
    # extract title
    title_tag = article_element.find(['h3', 'h2'])
    if not title_tag:
        link_tag = article_element.find('a', href=True)
        title = link_tag.get_text(strip=True) if link_tag else "No Title"
    else:
        title = title_tag.get_text(strip=True)
    
    # extract link
    link_tag = article_element.find('a', href=True)
    link = f"{BASE_URL}{link_tag['href']}" if link_tag else "No Link"
    
    # extract date
    date_obj = extract_article_date(article_element)
    
    # extract symbols
    symbols = extract_symbols(article_element, category)
    
    return build_article_dict(
        title=title,
        link=link,
        date=date_obj,
        symbols=symbols,
        img_src=None
    )


def scrape_category(category: str, light_mode: bool = False) -> List[dict]:
    driver = init_driver()
    
    try:
        url = BASE_URL_TEMPLATE.format(category)
        print(f"Processing: {category}")
        
        driver.get(url)
        time.sleep(3)  # wait for initial page load
        
        if not light_mode:
            scroll_page(driver, num_scrolls=3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        valid_articles = filter_valid_articles(soup)
        
        print(f"\t{category} found {len(valid_articles)} articles")
        
        articles = []
        for art in valid_articles:
            try:
                article_data = parse_article_element(art, category)
                articles.append(article_data)
            except Exception as e:
                print(f"\tError parsing article: {e}")
                continue
        
        return articles
        
    except Exception as e:
        print(f"Error processing {category}: {e}")
        return []
    finally:
        driver.quit()


def scrape_binance_news(light_mode: bool = False) -> pd.DataFrame:
    """
    scrape cryptocurrency news from all binance categories.
    """
    all_data = []

    max_workers = 4 
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        func = lambda cat: scrape_category(cat, light_mode=light_mode)
        results = executor.map(func, CATEGORIES)
        for res in results:
            all_data.extend(res)

    df = pd.DataFrame(all_data)
    
    if not df.empty:
        df = df.drop_duplicates(subset=['link'])
    
    print("Scraping complete")
    return df


def main():
    print("This script exposes scrape_binance_news(). Run scrapers_aggregator.py to execute.")


if __name__ == "__main__":
    main()
