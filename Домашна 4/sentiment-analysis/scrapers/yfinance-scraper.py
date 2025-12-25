import sys
from typing import List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag

from scraper_utils import parse_relative_time, normalize_url, build_article_dict


BASE_URL = "https://finance.yahoo.com"
TARGET_PATH = "/topic/crypto/"


def fetch_html(url: str) -> str:
	headers = {
		"User-Agent": (
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
			"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
		)
	}
	resp = requests.get(url, headers=headers, timeout=15)
	resp.raise_for_status()
	return resp.text


def extract_tickers(li: Tag) -> List[str]:
	tickers = []
	taxonomy = li.find("div", class_="taxonomy-links")
	
	if not taxonomy:
		return tickers

	for span in taxonomy.find_all("span", class_="ticker-wrapper"):
		name_div = span.find("div", class_="name")
		if not name_div:
			continue
		
		name_span = name_div.find("span")
		if name_span and name_span.text:
			tickers.append(name_span.text.strip())
	
	return tickers


def parse_article_element(li: Tag) -> Optional[dict]:
	anchor = li.find("a")
	if not anchor:
		return None

	# extract basic info
	href = anchor.get("href")
	title = anchor.get("title")
	
	# extract image
	img = anchor.find("img")
	img_src = img.get("src") if img else None

	# normalize URLs
	href = normalize_url(href, BASE_URL)
	img_src = normalize_url(img_src, BASE_URL) if img_src else None

	# extract symbols
	symbols = extract_tickers(li)

	# extract publication date
	published_at = None
	publishing_div = li.find("div", class_="publishing")
	if publishing_div:
		time_element = publishing_div.find("i")
		if time_element:
			published_at = parse_relative_time(time_element.get_text())

	return build_article_dict(
		title=title or "No Title",
		link=href,
		date=published_at,
		symbols=symbols,
		img_src=img_src
	)


def scrape_articles(html: str, limit: Optional[int] = None) -> List[dict]:
	soup = BeautifulSoup(html, "html.parser")
	articles = []

	items = soup.find_all("li", class_=["stream-item", "story-item"])
	if limit:
		items = items[:limit]

	for li in items:
		article = parse_article_element(li)
		if article:
			articles.append(article)

	return articles


def scrape_yfinance_news(light_mode: bool = False) -> pd.DataFrame:
	"""
	scrape cryptocurrency news from yahoo finance news.
	"""
	url = f"{BASE_URL}{TARGET_PATH}"
	html = fetch_html(url)
	
	# Arbitrary limit for light mode
	limit = 5 if light_mode else None
	articles = scrape_articles(html, limit=limit)
	
	return pd.DataFrame(articles)


def main() -> None:
	print("This script exposes scrape_yfinance_news(). Run scrapers_aggregator.py to execute.")


if __name__ == "__main__":
	try:
		main()
	except Exception as exc:
		sys.stderr.write(f"Error: {exc}\n")
		sys.exit(1)
