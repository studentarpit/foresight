"""TTL-based JSON file cache for Foresight data fetches."""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

# TTL in seconds per source type (per spec section 6.2)
_TTL = {
    "screener": 86_400,      # 24 h
    "filing": 604_800,       # 7 d
    "concall": 7_776_000,    # 90 d (one quarter)
    "pres": 2_592_000,       # 30 d
    "orders": 86_400,        # 24 h (order announcements)
}


def _latest_file(ticker: str, source: str) -> Optional[str]:
    """Return path to the most recent cache file for ticker+source, or None."""
    try:
        prefix = f"{ticker}_{source}_"
        files = [
            os.path.join(_CACHE_DIR, f)
            for f in os.listdir(_CACHE_DIR)
            if f.startswith(prefix) and f.endswith(".json")
        ]
    except OSError:
        return None
    return max(files, key=os.path.getmtime) if files else None


def get(ticker: str, source: str) -> Optional[Any]:
    """Return cached data if a file within TTL exists, else None."""
    path = _latest_file(ticker, source)
    if not path:
        return None
    ttl = _TTL.get(source, 86_400)
    try:
        age = time.time() - os.path.getmtime(path)
        if age > ttl:
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.debug("Cache read failed %s: %s", path, exc)
        return None


def put(ticker: str, source: str, data: Any) -> None:
    """Write data to a dated cache file. Silently ignores write errors."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    path = os.path.join(_CACHE_DIR, f"{ticker}_{source}_{date_str}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError as exc:
        logger.debug("Cache write failed %s: %s", path, exc)


def clear_ticker(ticker: str) -> int:
    """Remove all cache files for a ticker. Returns number of files deleted."""
    deleted = 0
    try:
        for fname in os.listdir(_CACHE_DIR):
            if fname.startswith(f"{ticker}_") and fname.endswith(".json"):
                os.remove(os.path.join(_CACHE_DIR, fname))
                deleted += 1
    except OSError:
        pass
    return deleted
