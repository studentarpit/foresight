"""Scrapes screener.in, NSE filings, and concall transcripts for fundamental data.

Rate-limit mitigations per spec section 6.1:
- Random 3-5 second delay between requests
- Rotating user-agent headers
- Per-source TTL cache to skip re-fetching (screener 24h, filings 7d, concall 90d)
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup

from data.cache import get as cache_get, put as cache_put

logger = logging.getLogger(__name__)

_SCREENER_BASE = "https://www.screener.in/company"

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]


def fetch_screener_data(ticker: str) -> dict:
    """Scrape screener.in for ROE, ROCE, revenue CAGR, D/E for a ticker.

    Checks 24h cache before hitting the network.
    Returns partial dict — missing keys omitted, never raises.
    """
    cached = cache_get(ticker, "screener")
    if cached is not None:
        logger.debug("Cache hit: screener/%s", ticker)
        return cached

    url = f"{_SCREENER_BASE}/{ticker}/"
    headers = {"User-Agent": random.choice(_USER_AGENTS)}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        time.sleep(random.uniform(3.0, 5.0))
        if resp.status_code != 200:
            logger.warning("screener.in returned %s for %s", resp.status_code, ticker)
            return {}
        data = _parse_screener_html(resp.text, ticker)
        if data:
            cache_put(ticker, "screener", data)
        return data
    except Exception as exc:
        logger.warning("screener.in scrape failed for %s: %s", ticker, exc)
        return {}


def _parse_screener_html(html: str, ticker: str) -> dict:
    """Extract ROE, ROCE, CAGR, D/E, and order book proxy from screener.in HTML."""
    soup = BeautifulSoup(html, "html.parser")
    result = {"screenerUrl": f"{_SCREENER_BASE}/{ticker}/"}

    # Ratios section — key-value li items
    for li in soup.select("#top-ratios li"):
        label = li.select_one(".name")
        value = li.select_one(".number")
        if not label or not value:
            continue
        name = label.get_text(strip=True).lower()
        val_text = value.get_text(strip=True).replace(",", "").replace("%", "").strip()
        try:
            val = float(val_text)
        except ValueError:
            continue
        if "return on equity" in name:
            result["roe"] = val
        elif "return on capital" in name:
            result["roce"] = val
        elif "debt" in name and "equity" in name:
            result["debtEq"] = val

    # Compounded sales growth table
    for table in soup.select("section#growth table"):
        header = table.select_one("thead tr th")
        if header and "compounded sales growth" in header.get_text("", strip=True).lower():
            for row in table.select("tbody tr"):
                cells = row.find_all("td")
                if len(cells) >= 2 and "3 years" in cells[0].get_text(strip=True).lower():
                    try:
                        result["revcagr"] = float(cells[1].get_text(strip=True).replace("%", "").strip())
                    except ValueError:
                        pass

    # Profit CAGR
    for table in soup.select("section#growth table"):
        header = table.select_one("thead tr th")
        if header and "compounded profit growth" in header.get_text("", strip=True).lower():
            for row in table.select("tbody tr"):
                cells = row.find_all("td")
                if len(cells) >= 2 and "3 years" in cells[0].get_text(strip=True).lower():
                    try:
                        result["profitcagr"] = float(cells[1].get_text(strip=True).replace("%", "").strip())
                    except ValueError:
                        pass

    return result


def fetch_concall_text(ticker: str) -> str:
    """Fetch the most recent earnings call transcript excerpt for a ticker.

    Checks 90-day cache first. Tries NSE corporate announcements API to find
    a concall PDF, extracts relevant text, and caches the result.
    Returns up to 3 000 chars of concall text, or '' if unavailable.
    """
    cached = cache_get(ticker, "concall")
    if cached is not None:
        logger.debug("Cache hit: concall/%s", ticker)
        return cached.get("text", "")

    text = _fetch_nse_concall(ticker) or ""
    cache_put(ticker, "concall", {"text": text})
    return text


def _fetch_nse_concall(ticker: str) -> Optional[str]:
    """Search NSE corporate announcements for a concall PDF and extract its text."""
    from data.pdf_extractor import extract_concall_text  # local import to avoid circular

    session = requests.Session()
    ua = random.choice(_USER_AGENTS)
    try:
        # Warm up the NSE session (required for the API to return data)
        session.get(
            "https://www.nseindia.com",
            headers={"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9"},
            timeout=12,
        )
        time.sleep(1.0)

        from_date = (datetime.now() - timedelta(days=120)).strftime("%d-%m-%Y")
        to_date = datetime.now().strftime("%d-%m-%Y")
        api_url = (
            f"https://www.nseindia.com/api/corporate-announcements"
            f"?index=equities&symbol={ticker}&from_date={from_date}&to_date={to_date}"
        )
        resp = session.get(
            api_url,
            headers={"User-Agent": ua, "Referer": "https://www.nseindia.com/"},
            timeout=12,
        )
        if resp.status_code != 200:
            return None

        announcements = resp.json()
        concall_kw = {"concall", "conference call", "earnings call", "investor call", "transcript"}
        for ann in announcements:
            subject = (ann.get("subject") or ann.get("desc") or "").lower()
            if any(kw in subject for kw in concall_kw):
                # NSE attachment links vary; try common keys
                pdf_url = ann.get("attchmnt") or ann.get("attachment") or ann.get("pdf")
                if pdf_url and pdf_url.endswith(".pdf"):
                    text = extract_concall_text(pdf_url)
                    if text:
                        return text
        return None
    except Exception as exc:
        logger.debug("NSE concall search failed for %s: %s", ticker, exc)
        return None


def fetch_nse_filings(ticker: str) -> dict:
    """Fetch recent NSE corporate announcements for order wins and PDF links.

    Checks 7-day cache before hitting the network. Returns partial dict, never raises.
    """
    cached = cache_get(ticker, "filing")
    if cached is not None:
        logger.debug("Cache hit: filing/%s", ticker)
        return cached

    url = (
        f"https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        f"?symbol={ticker}"
    )
    headers = {"User-Agent": random.choice(_USER_AGENTS)}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        pdf_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if a["href"].endswith(".pdf")
        ]
        data = {"investor_presentation_urls": pdf_links[:3]}
        if data["investor_presentation_urls"]:
            cache_put(ticker, "filing", data)
        return data
    except Exception as exc:
        logger.warning("NSE filings fetch failed for %s: %s", ticker, exc)
        return {}
