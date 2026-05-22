"""Fetch and parse BSE/NSE corporate order announcements — Section 6 of research spec.

Uses NSE corporate announcements API (same session pattern as scraper.py).
Filters announcements by order-related keywords and extracts structured data.
"""

import logging
import random
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

from data.cache import get as cache_get, put as cache_put

logger = logging.getLogger(__name__)

_NSE_BASE = "https://www.nseindia.com"
_ANNOUNCE_API = _NSE_BASE + "/api/corporate-announcements?index=equities&symbol={symbol}"

_ORDER_KEYWORDS = [
    "order received", "work order", "letter of award", "letter of intent",
    "contract awarded", "purchase order", "epc contract", "project awarded",
    "supply order", "agreement signed", "repeat order", "export order",
    "turnkey contract", "order win", "new order", "secured order",
    "bagged order", "contract secured", "received order", "order of",
    "awarded contract", "new contract", "contract value", "receipt of order",
]

_VALUE_RE = re.compile(
    r"(?:rs\.?|inr|rupees?|₹|value\s+of)[:\s]+(?:approximately\s+)?([₹\$]?\s*[\d,]+(?:\.\d+)?)\s*"
    r"(crore|cr\.?|lakh|lac|million|billion|mn|bn)?",
    re.IGNORECASE,
)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]


def _nse_session() -> requests.Session:
    """Return a warmed-up NSE requests session with cookies."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(_USER_AGENTS),
        "Referer": _NSE_BASE,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        session.get(_NSE_BASE, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
    except Exception as exc:
        logger.debug("NSE warmup failed: %s", exc)
    return session


def fetch_order_announcements(ticker: str, days: int = 180) -> list:
    """Fetch order-related corporate announcements from NSE for a ticker.

    Checks 24h cache. Returns list of structured order dicts.
    Never raises.
    """
    cached = cache_get(ticker, "orders")
    if cached is not None:
        return cached

    session = _nse_session()
    url = _ANNOUNCE_API.format(symbol=ticker)
    try:
        resp = session.get(url, timeout=15)
        time.sleep(random.uniform(2.0, 3.5))
        if resp.status_code != 200:
            logger.warning("NSE announcements returned %s for %s", resp.status_code, ticker)
            return []
        raw = resp.json()
        items = raw if isinstance(raw, list) else raw.get("data", [])
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        orders = []
        for ann in items:
            desc = (str(ann.get("desc", "")) + " " + str(ann.get("subject", ""))).lower()
            if not any(kw in desc for kw in _ORDER_KEYWORDS):
                continue
            parsed = _parse_announcement(ann)
            if parsed and parsed.get("announcement_date", "9999") >= cutoff_date:
                orders.append(parsed)
        cache_put(ticker, "orders", orders)
        logger.info("Fetched %d order announcements for %s", len(orders), ticker)
        return orders
    except Exception as exc:
        logger.warning("NSE order fetch failed for %s: %s", ticker, exc)
        return []


def _parse_announcement(ann: dict) -> Optional[dict]:
    """Extract structured order data from a raw NSE announcement record."""
    desc = str(ann.get("desc", "") or ann.get("subject", ""))
    date_raw = str(ann.get("sort_date", "") or ann.get("dt", ""))
    date_str = date_raw[:10] if date_raw else ""
    pdf_name = str(ann.get("attchmntFile", "") or "")
    pdf_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{pdf_name}" if pdf_name else ""

    order_value_cr = _extract_value(desc)
    desc_lower = desc.lower()
    order_type = (
        "export"
        if any(w in desc_lower for w in ["export", "foreign", "overseas", "international", "global"])
        else "domestic"
    )
    is_repeat = any(w in desc_lower for w in ["repeat", "additional", "extension", "follow-on", "follow on"])
    uid = f"{date_str}_{abs(hash(desc[:60])) % 99999}"

    return {
        "id": uid,
        "announcement_date": date_str,
        "description": desc[:500],
        "order_value_cr": order_value_cr,
        "order_type": order_type,
        "is_repeat_order": is_repeat,
        "pdf_url": pdf_url,
        "confidence": 0.80 if order_value_cr else 0.50,
    }


def _extract_value(text: str) -> Optional[float]:
    """Parse the first monetary value in Cr from announcement text."""
    match = _VALUE_RE.search(text)
    if not match:
        return None
    try:
        raw = match.group(1).replace(",", "").replace("₹", "").replace("$", "").strip()
        val = float(raw)
        unit = (match.group(2) or "").lower()
        if "lakh" in unit or "lac" in unit:
            return round(val / 100, 2)
        if "million" in unit or "mn" in unit:
            return round(val / 10, 2)
        if "billion" in unit or "bn" in unit:
            return round(val * 100, 2)
        return val
    except ValueError:
        return None
