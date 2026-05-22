"""Persistence layer for multi-quarter guidance vs actual history.

Stores and retrieves per-ticker quarterly entries used by the
Expectation Intelligence Engine.

File: data/guidance_history.json
Schema:
  {
    "BEL": [
      {
        "quarter": "Q3FY24",
        "guidedRevGrowth": 22.0,   actualRevGrowth: 24.5,
        "guidedMargin": 22.0,      actualMargin: 23.1,
        "guidedPATGrowth": 20.0,   actualPATGrowth: 26.3,
        "notes": "Strong order execution"
      }, ...
    ]
  }
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_PATH = os.path.join(os.path.dirname(__file__), "guidance_history.json")


def load_all() -> dict:
    """Return full guidance history dict keyed by ticker."""
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("guidance_history load failed: %s", exc)
        return {}


def load_ticker(ticker: str) -> list[dict]:
    """Return history list for one ticker (empty list if none)."""
    return load_all().get(ticker, [])


def save_entry(ticker: str, entry: dict) -> None:
    """Append or update a quarterly entry for a ticker.

    If an entry with the same `quarter` key already exists it is replaced.
    """
    all_data = load_all()
    history = all_data.setdefault(ticker, [])
    quarter = entry.get("quarter", "")
    # Replace existing entry for same quarter
    existing = next((i for i, e in enumerate(history) if e.get("quarter") == quarter), None)
    if existing is not None:
        history[existing] = entry
    else:
        history.append(entry)
    # Keep chronological order by quarter string
    all_data[ticker] = sorted(history, key=lambda e: e.get("quarter", ""))
    _write(all_data)


def delete_entry(ticker: str, quarter: str) -> bool:
    """Remove a specific quarter entry. Returns True if found and deleted."""
    all_data = load_all()
    history = all_data.get(ticker, [])
    new_history = [e for e in history if e.get("quarter") != quarter]
    if len(new_history) == len(history):
        return False
    all_data[ticker] = new_history
    _write(all_data)
    return True


def all_tickers() -> list[str]:
    """Return sorted list of tickers that have any guidance history."""
    return sorted(load_all().keys())


def _write(data: dict) -> None:
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        logger.warning("guidance_history write failed: %s", exc)
