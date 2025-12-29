import sys
from typing import List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag

from scraper_utils import parse_relative_time, normalize_url, build_article_dict
import urllib


BASE_URL = "https://www.coindesk.com"
BASE_URL_TEMPLATE = "https://www.coindesk.com/tag/{}"

CATEGORIES = [
	"ethereum", "bitcoin", "xrp", "solana"
]

CATEGORY_SYMBOL_MAP = {
	"ethereum": "ETH",
	"bitcoin": "BTC",
	"xrp": "XRP",
	"solana": "SOL",
}

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

def parse_article_element(container: Tag, symbol: str) -> Optional[dict]:
	div = container.find("div")

	anchor = div.find_all("a")[1]

	if not anchor:
		return None

	link = f"{BASE_URL}{anchor.get('href')}"
	title = anchor.text

	p = container.select("div p span")
	date = p[2].text

	img = container.find("img")
	href = None
	if img and img.get("src"):
		href = urllib.parse.unquote(img.get("src"))
		href = href.split("?")[1].split("=")[1]

	return build_article_dict(
		title=title,
		link=link,
		date=date,
		symbols=[symbol],
		img_src=href
	)

def scrape_articles(html: str, category: str) -> List[dict]:
	soup = BeautifulSoup(html, "html.parser")
	articles = []
	items = soup.select("div.w-full.shrink.justify-between")
	symbol = CATEGORY_SYMBOL_MAP[category] or None
	for item in items:
		article = parse_article_element(item, symbol)
		if article:
			articles.append(article)

	return articles

def scrape_category(category_url: str, category: str) -> List[dict]:
	html = fetch_html(category_url)

	articles = scrape_articles(html, category)

	return articles

def scrape_coindesk_news(light_mode = False) -> pd.DataFrame:
	"""
	scrape cryptocurrency news from coindesk news.
	"""
	all_data = []

	for cat in CATEGORIES:
		print(f"Scraping {cat}...")
		url = BASE_URL_TEMPLATE.format(cat)
		articles = scrape_category(url, cat)
		all_data.extend(articles)

	df = pd.DataFrame(all_data)

	print("Scraping complete")
	return df


df = scrape_coindesk_news()
df.to_csv('example.csv', index=False)
