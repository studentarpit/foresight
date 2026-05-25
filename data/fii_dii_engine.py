"""FII/DII Flow Intelligence Engine.

Data sources (all free):
  - NSE fiidiiTradeReact  : market-wide FII/DII daily net flows
  - screener.in           : quarterly shareholding pattern (FII%, DII%, Promoter%, Public%)
  - NSE bulk deals page   : bulk/block deal activity (fallback: empty list, APIs return 404)
"""

import logging
import random
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

from data.cache import get as cache_get, put as cache_put

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def _ua() -> str:
    return random.choice(_USER_AGENTS)


def _screener_slug(symbol: str) -> str:
    """Map NSE ticker to screener.in slug (handles common mismatches)."""
    _MAP = {
        "STERLINWILS": "SWSOLAR",
        "MAZDOCK":     "MAZDOCK",
        "WAAREEENER":  "WAAREEENER",
    }
    return _MAP.get(symbol.upper(), symbol.upper())


# ── Market-wide FII/DII daily data ───────────────────────────────────────────

def fetch_fii_dii_daily() -> dict:
    """Fetch today's market-wide FII/DII net buy/sell from NSE. Cached 1 h."""
    cached = cache_get("global", "fii_dii_daily")
    if cached is not None:
        return cached

    ua = _ua()
    session = requests.Session()
    empty: dict = {}
    try:
        session.get(
            "https://www.nseindia.com",
            headers={"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9"},
            timeout=10,
        )
        time.sleep(1.2)
        resp = session.get(
            "https://www.nseindia.com/api/fiidiiTradeReact",
            headers={"User-Agent": ua, "Referer": "https://www.nseindia.com/"},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.debug("FII/DII daily API status %s", resp.status_code)
            return empty

        raw = resp.json()
        result = _parse_fii_dii_daily(raw)
        cache_put("global", "fii_dii_daily", result)
        return result
    except Exception as exc:
        logger.debug("fetch_fii_dii_daily failed: %s", exc)
        return empty


def _parse_fii_dii_daily(raw) -> dict:
    """Parse NSE fiidiiTradeReact response. Fields: buyValue, sellValue, netValue, category."""
    result: dict = {}
    for entry in raw if isinstance(raw, list) else []:
        cat = (entry.get("category") or "").upper()
        def _f(key: str) -> float:
            try:
                return float(str(entry.get(key) or "0").replace(",", ""))
            except ValueError:
                return 0.0

        row = {
            "gross_buy":  _f("buyValue"),
            "gross_sell": _f("sellValue"),
            "net":        _f("netValue"),
            "date":       entry.get("date", ""),
        }
        if "FII" in cat or "FPI" in cat:
            result["fii"] = row
        elif "DII" in cat:
            result["dii"] = row

    # Derive market_sentiment
    fii_net = result.get("fii", {}).get("net", 0.0)
    dii_net = result.get("dii", {}).get("net", 0.0)
    combined = fii_net + dii_net
    if combined > 500:
        sentiment = "RISK_ON"
    elif combined < -500:
        sentiment = "RISK_OFF"
    else:
        sentiment = "NEUTRAL"
    result["market_sentiment"] = sentiment
    return result


# ── Shareholding pattern from screener.in ─────────────────────────────────────

def fetch_shareholding_pattern(symbol: str) -> list[dict]:
    """Fetch quarterly shareholding pattern from screener.in. Returns last 8 quarters."""
    slug = _screener_slug(symbol)
    cached = cache_get(symbol, "shareholding")
    if cached is not None:
        return cached

    url = f"https://www.screener.in/company/{slug}/consolidated/"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": _ua()},
            timeout=15,
        )
        if resp.status_code != 200:
            url = f"https://www.screener.in/company/{slug}/"
            resp = requests.get(url, headers={"User-Agent": _ua()}, timeout=15)
        if resp.status_code != 200:
            return []
        result = _parse_shareholding_html(resp.text)
        if result:
            cache_put(symbol, "shareholding", result)
        return result
    except Exception as exc:
        logger.debug("fetch_shareholding_pattern %s failed: %s", symbol, exc)
        return []


def _parse_shareholding_html(html: str) -> list[dict]:
    """Parse screener.in #shareholding section into list of quarter dicts."""
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find("section", id="shareholding")
    if not section:
        return []

    table = section.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    if not rows:
        return []

    # First row = headers (quarter labels)
    header_cells = rows[0].find_all(["th", "td"])
    quarters = [c.get_text(strip=True) for c in header_cells][1:]  # skip label col

    data: dict[str, list] = {}
    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if not cells:
            continue
        label = cells[0].get_text(strip=True).lower().rstrip("+").strip()
        values = []
        for c in cells[1:]:
            raw = c.get_text(strip=True).replace("%", "").replace(",", "").strip()
            try:
                values.append(float(raw))
            except ValueError:
                values.append(None)
        # Normalize label
        if "promoter" in label:
            data["promoter"] = values
        elif "fii" in label or "fpi" in label:
            data["fii"] = values
        elif "dii" in label:
            data["dii"] = values
        elif "public" in label or "retail" in label or "other" in label:
            data["public"] = values

    if not quarters or not data:
        return []

    # Take last 8 quarters (most recent)
    n = min(8, len(quarters))
    quarters = quarters[-n:]
    for key in data:
        data[key] = data[key][-n:]

    result = []
    for i, q in enumerate(quarters):
        def _qoq(key: str, idx: int) -> Optional[float]:
            vals = data.get(key, [])
            if idx == 0 or idx >= len(vals):
                return None
            curr = vals[idx]
            prev = vals[idx - 1]
            if curr is None or prev is None:
                return None
            return round(curr - prev, 2)

        result.append({
            "quarter":            q,
            "fii_pct":            (data.get("fii") or [None] * (i + 1))[i],
            "dii_pct":            (data.get("dii") or [None] * (i + 1))[i],
            "promoter_pct":       (data.get("promoter") or [None] * (i + 1))[i],
            "public_pct":         (data.get("public") or [None] * (i + 1))[i],
            "fii_change_qoq":     _qoq("fii", i),
            "dii_change_qoq":     _qoq("dii", i),
            "promoter_change_qoq": _qoq("promoter", i),
            "public_change_qoq":  _qoq("public", i),
        })

    return result


# ── Bulk/block deals ─────────────────────────────────────────────────────────

def fetch_bulk_block_deals(symbol: str) -> list[dict]:
    """Fetch bulk/block deals for symbol. NSE API returns 404; returns market-wide fallback."""
    cached = cache_get(symbol, "bulk_block")
    if cached is not None:
        return cached

    # NSE bulk/block APIs return 404; use market-wide bulk deals and filter
    market_deals = _fetch_market_bulk_deals()
    symbol_deals = [d for d in market_deals if d.get("ticker", "").upper() == symbol.upper()]

    cache_put(symbol, "bulk_block", symbol_deals)
    return symbol_deals


def _fetch_market_bulk_deals() -> list[dict]:
    """Fetch market-wide bulk deals from NSE (cached 1 h)."""
    cached = cache_get("global", "bulk_deals_raw")
    if cached is not None:
        return cached

    ua = _ua()
    session = requests.Session()
    try:
        session.get(
            "https://www.nseindia.com",
            headers={"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9"},
            timeout=10,
        )
        time.sleep(1.0)
        # Try bulk deals
        resp = session.get(
            "https://www.nseindia.com/api/bulkdeals",
            headers={"User-Agent": ua, "Referer": "https://www.nseindia.com/"},
            timeout=10,
        )
        if resp.status_code == 200:
            raw = resp.json()
            deals = raw if isinstance(raw, list) else raw.get("data", [])
            result = [_normalise_deal(d) for d in deals[:50]]
            cache_put("global", "bulk_deals_raw", result)
            return result
    except Exception as exc:
        logger.debug("_fetch_market_bulk_deals failed: %s", exc)

    cache_put("global", "bulk_deals_raw", [])
    return []


def _normalise_deal(d: dict) -> dict:
    """Normalise NSE bulk deal entry to standard schema."""
    qty = d.get("quantityTraded") or d.get("quantity") or 0
    price = d.get("tradePrice") or d.get("price") or 0.0
    try:
        value_cr = round(int(qty) * float(price) / 1e7, 2)
    except (ValueError, TypeError):
        value_cr = 0.0

    client = (d.get("clientName") or d.get("client") or "").strip()
    entity_type = _classify_entity(client)

    return {
        "ticker":      (d.get("symbol") or d.get("ticker") or "").upper(),
        "date":        d.get("date", ""),
        "deal_type":   "BULK",
        "client":      client,
        "side":        (d.get("buySell") or d.get("side") or "").upper(),
        "quantity":    qty,
        "price":       price,
        "value_cr":    value_cr,
        "entity_type": entity_type,
    }


def _classify_entity(name: str) -> str:
    """Classify a deal client name into entity type."""
    n = name.lower()
    if any(k in n for k in ["blackrock", "vanguard", "goldman", "morgan", "fidelity",
                              "templeton", "aberdeen", "jpmorgan", "merrill", "ubs",
                              "societe", "nomura", "macquarie", "barclays", "fii", "fpi"]):
        return "FII"
    if any(k in n for k in ["lic", "sbi", "life insurance", "general insurance",
                              "nps", "epfo", "uti", "psu", "nippon", "mirae",
                              "hdfc mf", "icici mf", "kotak mf", "dii"]):
        return "DII"
    if any(k in n for k in ["mutual fund", "mf ", " mf", "asset management", "amc"]):
        return "DII"
    if any(k in n for k in ["hni", "promoter", "family office"]):
        return "HNI"
    return "UNKNOWN"


# ── Accumulation / Distribution detection ─────────────────────────────────────

def detect_accumulation_distribution(symbol: str) -> dict:
    """Analyze FII/DII shareholding trend for accumulation or distribution signal."""
    cached = cache_get(symbol, "accum_dist")
    if cached is not None:
        return cached

    quarters = fetch_shareholding_pattern(symbol)
    if len(quarters) < 2:
        return _empty_accum()

    # Compute trend over last 4 quarters (or all if fewer)
    recent = quarters[-4:] if len(quarters) >= 4 else quarters

    fii_changes = [q["fii_change_qoq"] for q in recent if q.get("fii_change_qoq") is not None]
    dii_changes = [q["dii_change_qoq"] for q in recent if q.get("dii_change_qoq") is not None]

    fii_trend = _trend_direction(fii_changes)
    dii_trend = _trend_direction(dii_changes)

    # Count consecutive quarters of accumulation
    duration = _count_consecutive_direction(quarters)

    # Combined signal
    if fii_trend == "INCREASING" and dii_trend == "INCREASING":
        pattern = "ACCUMULATING"
        strength = "HIGH"
        verdict = "Both FII and DII are increasing stakes — strongest institutional conviction signal."
        combined = "STRONG_BUY"
    elif fii_trend == "INCREASING" and dii_trend != "DECREASING":
        pattern = "ACCUMULATING"
        strength = "MEDIUM"
        verdict = "FII accumulating; DII stable. Foreign conviction with domestic holding."
        combined = "BUY"
    elif dii_trend == "INCREASING" and fii_trend != "DECREASING":
        pattern = "ACCUMULATING"
        strength = "MEDIUM"
        verdict = "DII accumulating; FII stable. Domestic confidence, watch for FII re-entry."
        combined = "BUY"
    elif fii_trend == "DECREASING" and dii_trend == "DECREASING":
        pattern = "DISTRIBUTING"
        strength = "HIGH"
        verdict = "Both FII and DII reducing stakes — strong institutional exit signal."
        combined = "STRONG_SELL"
    elif fii_trend == "DECREASING" and dii_trend != "INCREASING":
        pattern = "DISTRIBUTING"
        strength = "MEDIUM"
        verdict = "FII distributing; DII not absorbing. Foreign exit without domestic support."
        combined = "SELL"
    elif dii_trend == "DECREASING" and fii_trend != "INCREASING":
        pattern = "DISTRIBUTING"
        strength = "MEDIUM"
        verdict = "DII reducing; FII not compensating. Domestic caution."
        combined = "NEUTRAL"
    else:
        pattern = "NEUTRAL"
        strength = "LOW"
        verdict = "No clear institutional trend. Monitor next quarter."
        combined = "NEUTRAL"

    result = {
        "pattern":          pattern,
        "pattern_strength": strength,
        "duration_quarters": duration,
        "fii_trend":        fii_trend,
        "dii_trend":        dii_trend,
        "combined_signal":  combined,
        "smart_money_verdict": verdict,
        "fii_last_qoq":     fii_changes[-1] if fii_changes else None,
        "dii_last_qoq":     dii_changes[-1] if dii_changes else None,
    }
    cache_put(symbol, "accum_dist", result)
    return result


def _empty_accum() -> dict:
    return {
        "pattern": "NEUTRAL", "pattern_strength": "LOW",
        "duration_quarters": 0, "fii_trend": "STABLE", "dii_trend": "STABLE",
        "combined_signal": "NEUTRAL", "smart_money_verdict": "Insufficient data.",
        "fii_last_qoq": None, "dii_last_qoq": None,
    }


def _trend_direction(changes: list) -> str:
    """Return INCREASING / DECREASING / STABLE based on sum of QoQ changes."""
    if not changes:
        return "STABLE"
    total = sum(c for c in changes if c is not None)
    if total > 0.5:
        return "INCREASING"
    if total < -0.5:
        return "DECREASING"
    return "STABLE"


def _count_consecutive_direction(quarters: list) -> int:
    """Count consecutive quarters of same FII direction from most recent backwards."""
    if len(quarters) < 2:
        return 0
    changes = [q["fii_change_qoq"] for q in quarters if q.get("fii_change_qoq") is not None]
    if not changes:
        return 0
    last_sign = 1 if changes[-1] >= 0 else -1
    count = 0
    for c in reversed(changes):
        if (1 if c >= 0 else -1) == last_sign:
            count += 1
        else:
            break
    return count


# ── Flow Score ────────────────────────────────────────────────────────────────

def compute_flow_score(symbol: str) -> Optional[int]:
    """Compute FII/DII Flow Score 0-100 for a stock, or None when data is unavailable.

    Returns None (not 50) when shareholding data cannot be fetched — None is displayed
    as N/A on cards and excluded from heatmap ranking to avoid false neutral signals.

    Components (from spec):
      FII trend direction  30%
      DII trend direction  25%
      Duration of pattern  20%
      Bulk/block activity  15%
      Signal strength      10%
    """
    cached = cache_get(symbol, "flow_score")
    if cached is not None:
        return cached

    accum = detect_accumulation_distribution(symbol)

    # If no shareholding data at all, return None rather than a placeholder 50
    quarters = fetch_shareholding_pattern(symbol)
    if not quarters:
        return None

    bulk  = fetch_bulk_block_deals(symbol)

    # FII trend score (0-30)
    fii_trend = accum.get("fii_trend", "STABLE")
    fii_pts = {"INCREASING": 30, "STABLE": 15, "DECREASING": 0}.get(fii_trend, 15)

    # DII trend score (0-25)
    dii_trend = accum.get("dii_trend", "STABLE")
    dii_pts = {"INCREASING": 25, "STABLE": 12, "DECREASING": 0}.get(dii_trend, 12)

    # Duration score (0-20): capped at 4 quarters = full score
    duration = min(accum.get("duration_quarters", 0), 4)
    dur_pts = int(duration / 4 * 20)
    if accum.get("pattern") == "DISTRIBUTING":
        dur_pts = 20 - dur_pts  # penalise long distribution streaks

    # Bulk/block deal score (0-15) — only FII, DII, MF; UNKNOWN excluded (no signal)
    _KNOWN = {"FII", "DII", "MF"}
    known_bulk   = [d for d in bulk if d.get("entity_type", "") in _KNOWN]
    recent_buys  = sum(1 for d in known_bulk if d.get("side", "").upper() in ("B", "BUY"))
    recent_sells = sum(1 for d in known_bulk if d.get("side", "").upper() in ("S", "SELL"))
    if recent_buys + recent_sells == 0:
        bulk_pts = 7  # neutral when no known-entity deals
    else:
        buy_ratio = recent_buys / (recent_buys + recent_sells)
        bulk_pts = int(buy_ratio * 15)

    # Strength score (0-10)
    strength_map = {"HIGH": 10, "MEDIUM": 5, "LOW": 0}
    strength_pts = strength_map.get(accum.get("pattern_strength", "LOW"), 0)
    if accum.get("pattern") == "DISTRIBUTING":
        strength_pts = 10 - strength_pts

    score = fii_pts + dii_pts + dur_pts + bulk_pts + strength_pts
    score = max(0, min(100, score))

    cache_put(symbol, "flow_score", score)
    return score


def prefetch_flow_data_batch(symbols: list[str], max_workers: int = 4) -> None:
    """Pre-fetch shareholding + accumulation signal for a list of symbols in parallel.

    Uses up to 4 workers with a 0.5s stagger to avoid rate-limiting screener.in.
    Results are written to the TTL cache; subsequent per-stock calls are instant.
    Already-cached symbols are skipped.
    """
    needed = [s for s in symbols if cache_get(s, "shareholding") is None]
    if not needed:
        return

    def _fetch_one(symbol: str) -> None:
        fetch_shareholding_pattern(symbol)
        detect_accumulation_distribution(symbol)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for i, symbol in enumerate(needed):
            if i > 0:
                time.sleep(0.5)  # stagger to avoid screener.in rate-limit
            futures[executor.submit(_fetch_one, symbol)] = symbol

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                future.result()
            except Exception as exc:
                logger.debug("prefetch_flow_data_batch %s failed: %s", symbol, exc)


def flow_score_label(score: Optional[int]) -> tuple[str, str]:
    """Return (emoji_label, colour_class) for a flow score. Handles None as N/A."""
    if score is None:
        return "N/A", "grey"
    if score >= 80:
        return "Strong Accumulation", "green"
    if score >= 60:
        return "Mild Accumulation", "yellow"
    if score >= 40:
        return "Neutral", "grey"
    if score >= 20:
        return "Distribution Beginning", "orange"
    return "Heavy Distribution", "red"
