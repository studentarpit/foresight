"""Per-company order announcement history — JSON file persistence."""

import json
import os
from typing import Optional

_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "order_data.json")


def _load_all() -> dict:
    try:
        with open(_HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_all(data: dict) -> None:
    os.makedirs(os.path.dirname(_HISTORY_FILE), exist_ok=True)
    with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _order_key(order: dict) -> str:
    return order.get("id") or f"{order.get('announcement_date','')}_{hash(order.get('description','')[:50]) % 99999}"


def load_ticker_orders(ticker: str) -> list:
    """Return all saved orders for a ticker, sorted by date descending."""
    orders = _load_all().get(ticker, [])
    return sorted(orders, key=lambda x: x.get("announcement_date", ""), reverse=True)


def save_orders(ticker: str, orders: list) -> int:
    """Merge new orders for a ticker, deduplicating by id. Returns count added."""
    all_data = _load_all()
    existing = {_order_key(o): o for o in all_data.get(ticker, [])}
    before = len(existing)
    for order in orders:
        existing[_order_key(order)] = order
    all_data[ticker] = list(existing.values())
    _save_all(all_data)
    return len(existing) - before


def delete_order(ticker: str, order_id: str) -> bool:
    """Remove an order entry by id. Returns True if found and removed."""
    all_data = _load_all()
    orders = all_data.get(ticker, [])
    new = [o for o in orders if _order_key(o) != order_id]
    if len(new) < len(orders):
        all_data[ticker] = new
        _save_all(all_data)
        return True
    return False


def all_tickers_with_orders() -> list:
    """Return sorted list of tickers that have order data."""
    return sorted(_load_all().keys())


def total_order_value(ticker: str) -> Optional[float]:
    """Return sum of order_value_cr for all saved orders for a ticker, or None."""
    orders = load_ticker_orders(ticker)
    values = [o["order_value_cr"] for o in orders if o.get("order_value_cr")]
    return round(sum(values), 1) if values else None
