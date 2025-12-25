from datetime import datetime
from typing import List
from urllib.parse import urljoin

import dateparser


def parse_relative_time(time_str: str) -> datetime:
    """
    parse relative time strings (e.g., "2 hours ago") into datetime objects.
    """
    if not time_str:
        return datetime.now()
    
    time_str = time_str.strip()
    dt = dateparser.parse(time_str)
    
    return dt if dt else datetime.now()


def normalize_url(url: str, base_url: str) -> str:
    """
    convert relative URLs to absolute URLs.
    """
    if not url:
        return ""
    
    return urljoin(base_url, url)


def extract_symbols_from_text(text: str, pattern: str = r'\$(?![0-9])([A-Za-z]{2,10})\b') -> List[str]:
    import re
    
    matches = re.findall(pattern, text)
    return list(set(sym.upper() for sym in matches))


def build_article_dict(title: str, link: str, date: datetime, symbols: List[str], img_src: str = None) -> dict:
    return {
        "title": title,
        "link": link,
        "date": date,
        "symbols": symbols,
        "img_src": img_src or "",
    }
