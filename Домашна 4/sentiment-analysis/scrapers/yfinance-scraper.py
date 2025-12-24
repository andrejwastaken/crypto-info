import sys
from typing import List, Optional
from urllib.parse import urljoin
import dateparser
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd


BASE_URL = "https://finance.yahoo.com"
TARGET_PATH = "/topic/crypto/"
CSV_PATH = "yfinance-news.csv"


def parse_relative_time(time_str: str) -> datetime:
	if not time_str:
		return datetime.now()
	time_str = time_str.strip()
	dt = dateparser.parse(time_str)
	return dt if dt else datetime.now()


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


def extract_first_anchor(li: Tag) -> Optional[Tag]:
	return li.find("a")


def extract_taxonomy_tickers(li: Tag) -> List[str]:
	"""get ticker names"""
	tickers: List[str] = []
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


def scrape_items(html: str) -> List[dict]:
	soup = BeautifulSoup(html, "html.parser")
	items: List[dict] = []

	for li in soup.find_all("li", class_=["stream-item", "story-item"]):
		anchor = extract_first_anchor(li)
		if not anchor:
			continue

		href = anchor.get("href")
		title = anchor.get("title")
		img_src = None

		img = anchor.find("img")
		if img:
			img_src = img.get("src")

		# normalize relative links to absolute.
		if href:
			href = urljoin(BASE_URL, href)
		if img_src:
			img_src = urljoin(BASE_URL, img_src)

		tickers = extract_taxonomy_tickers(li)

		published_at = None
		publishing_div = li.find("div", class_="publishing")
		if publishing_div:
			time_element = publishing_div.find("i")
			if time_element:
				published_at = parse_relative_time(time_element.get_text())

		items.append(
			{
				"link": href,
				"title": title,
				"img_src": img_src,
				"symbols": tickers,
				"date": published_at,
			}
		)

	return items


def scrape_yfinance_news() -> pd.DataFrame:
	url = urljoin(BASE_URL, TARGET_PATH)
	html = fetch_html(url)
	data = scrape_items(html)

	df = pd.DataFrame(data)
	return df


def main() -> None:
	print("This script exposes scrape_yfinance_news(). Run scrapers-aggregator.py to execute.")


if __name__ == "__main__":
	try:
		main()
	except Exception as exc:  
		sys.stderr.write(f"Error: {exc}\n")
		sys.exit(1)
