"""Alert Engine — detects transition signals across DMA crossovers, guidance,
FVS bands, order inflow, and expectation gaps.

Spec: Foresight v3, Section 3.5 and 5.5.

Alerts are generated from the current scan DataFrame and optionally compared
against a previous snapshot stored in data/alerts_history.json.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "alerts_history.json")

# Alert type → (icon, priority 1=high)
_ALERT_META = {
    "DMA200_CROSS_UP":      ("📈", 1, "Crossed above 200 DMA — potential trend reversal"),
    "DMA200_CROSS_DOWN":    ("📉", 1, "Fell below 200 DMA — downtrend warning"),
    "DMA50_CROSS_UP":       ("📈", 2, "Crossed above 50 DMA — momentum improving"),
    "STRONG_UPTREND":       ("🚀", 1, "Price above all DMAs — strong institutional uptrend"),
    "DOWNTREND":            ("⚠️", 1, "Price below all DMAs — avoid until trend recovers"),
    "EXPECTATION_BEAT":     ("✅", 1, "Company beating market expectations"),
    "EXPECTATION_MISS":     ("❌", 1, "Company missing market expectations"),
    "ORDER_ACCELERATION":   ("📦", 2, "Order inflow accelerating — growth visibility improving"),
    "ORDER_DECELERATION":   ("📦", 2, "Order inflow decelerating — watch closely"),
    "CONCENTRATION_RISK":   ("⚠️", 1, "High customer/scheme concentration detected"),
    "FVS_STRONG_BUY":       ("🟢", 1, "FVS crossed into Strong Buy zone (≥80)"),
    "FVS_DROPPED_WATCH":    ("🟡", 2, "FVS dropped from Strong Buy to Watch zone"),
    "ACCUMULATING":         ("📊", 2, "Volume accumulation detected — institutional buying"),
    "DISTRIBUTING":         ("📊", 2, "Volume distribution detected — possible selling"),
    "GUIDANCE_DOWNGRADE":   ("📉", 1, "Management guidance credibility concern"),
}


def detect_alerts(
    current_df: pd.DataFrame,
    previous_snapshot: Optional[dict] = None,
) -> list[dict]:
    """Scan current DataFrame and return list of alert dicts.

    Each alert: {ticker, name, type, icon, priority, message, ts}
    previous_snapshot: {ticker: {fvs, above200dma, orderInflowAcceleration, ...}}
    """
    alerts: list[dict] = []
    prev = previous_snapshot or {}

    for _, row in current_df.iterrows():
        ticker = row.get("ticker", "")
        name   = row.get("name", ticker)
        p      = prev.get(ticker, {})

        def _alert(atype: str, extra: str = ""):
            meta = _ALERT_META.get(atype, ("ℹ️", 3, atype))
            icon, priority, default_msg = meta
            alerts.append({
                "ticker":   ticker,
                "name":     name,
                "type":     atype,
                "icon":     icon,
                "priority": priority,
                "message":  extra or default_msg,
                "ts":       datetime.now().isoformat(timespec="seconds"),
            })

        # ── Technical DMA alerts ─────────────────────────────────────────────
        trend = row.get("technicalTrend", "")
        prev_above200 = p.get("above200dma")
        curr_above200 = row.get("above200dma", False)

        if trend == "STRONG_UPTREND":
            _alert("STRONG_UPTREND")
        elif trend == "DOWNTREND":
            _alert("DOWNTREND")

        if prev_above200 is not None:
            if not prev_above200 and curr_above200:
                _alert("DMA200_CROSS_UP", f"{name} crossed above 200 DMA")
            elif prev_above200 and not curr_above200:
                _alert("DMA200_CROSS_DOWN", f"{name} fell below 200 DMA — monitor closely")

        # ── Volume trend alerts ──────────────────────────────────────────────
        vol_trend = row.get("volumeTrend", "")
        if vol_trend == "ACCUMULATING":
            _alert("ACCUMULATING")
        elif vol_trend == "DISTRIBUTING":
            _alert("DISTRIBUTING")

        # ── Expectation signal alerts ────────────────────────────────────────
        exp_sig = row.get("expectationSignal", "UNKNOWN")
        if exp_sig == "BEAT":
            _alert("EXPECTATION_BEAT")
        elif exp_sig == "MISS":
            _alert("EXPECTATION_MISS")

        # ── Order book alerts ────────────────────────────────────────────────
        if row.get("orderInflowAcceleration"):
            _alert("ORDER_ACCELERATION")
        prev_accel = p.get("orderInflowAcceleration")
        if prev_accel and not row.get("orderInflowAcceleration"):
            _alert("ORDER_DECELERATION", f"{name} order inflow no longer accelerating")

        # ── Concentration risk ───────────────────────────────────────────────
        if row.get("concentrationFlag"):
            _alert("CONCENTRATION_RISK")

        # ── FVS transition alerts ────────────────────────────────────────────
        fvs     = float(row.get("fvs") or 0)
        prev_fvs = float(p.get("fvs") or 0)
        if fvs >= 80 and prev_fvs < 80:
            _alert("FVS_STRONG_BUY", f"{name} FVS reached {fvs:.0f} — entering Strong Buy zone")
        elif prev_fvs >= 80 and fvs < 80:
            _alert("FVS_DROPPED_WATCH", f"{name} FVS dropped to {fvs:.0f} — moved out of Strong Buy")

    # Sort by priority then ticker
    alerts.sort(key=lambda a: (a["priority"], a["ticker"]))
    return alerts


# ── Spec 07: Smart Money Accumulation alerts ──────────────────────────────────

def detect_smart_money_alerts(scan_df: pd.DataFrame) -> list[dict]:
    """Return SMART_MONEY_ACCUMULATION alerts from cache — no new HTTP calls.

    Fires when FII has been accumulating for 2+ consecutive quarters AND a
    FII/DII BUY bulk deal for the same stock exists within the last 30 days.
    """
    from datetime import date, timedelta
    from data.fii_dii_engine import detect_accumulation_distribution, fetch_bulk_block_deals

    alerts: list[dict] = []
    cutoff = (date.today() - timedelta(days=30)).isoformat()

    for _, row in scan_df.iterrows():
        ticker = row.get("ticker", "")
        if not ticker:
            continue
        try:
            accum = detect_accumulation_distribution(ticker)
        except Exception:
            continue

        if accum.get("fii_trend") != "INCREASING":
            continue
        if (accum.get("duration_quarters") or 0) < 2:
            continue

        try:
            deals = fetch_bulk_block_deals(ticker)
        except Exception:
            deals = []

        recent_buy = None
        for deal in deals:
            if deal.get("side") != "BUY":
                continue
            if deal.get("entity_type") not in ("FII", "DII"):
                continue
            if (deal.get("date") or "") >= cutoff:
                recent_buy = deal
                break

        if recent_buy is None:
            continue

        duration  = accum.get("duration_quarters", 0)
        fii_qoq   = accum.get("fii_last_qoq")
        entity    = recent_buy.get("client", "")
        value_cr  = recent_buy.get("value_cr", 0)
        deal_date = recent_buy.get("date", "")

        alerts.append({
            "ticker":            ticker,
            "name":              row.get("name", ticker),
            "type":              "SMART_MONEY_ACCUMULATION",
            "icon":              "🚨",
            "priority":          1,
            "message":           (
                f"FII accumulating {duration}Q · "
                f"{entity} bought ₹{value_cr:.0f} Cr on {deal_date}"
            ),
            "fii_change_pct":    fii_qoq,
            "duration_quarters": duration,
            "deal_entity":       entity,
            "deal_value_cr":     value_cr,
            "deal_date":         deal_date,
            "ts":                datetime.now().isoformat(timespec="seconds"),
        })

    return alerts


# ── Snapshot persistence ──────────────────────────────────────────────────────

def save_snapshot(df: pd.DataFrame) -> None:
    """Persist key fields from current scan for next-run comparison."""
    snap = {}
    for _, row in df.iterrows():
        ticker = row.get("ticker", "")
        if ticker:
            snap[ticker] = {
                "fvs":                    float(row.get("fvs") or 0),
                "above200dma":            bool(row.get("above200dma", False)),
                "above50dma":             bool(row.get("above50dma", False)),
                "orderInflowAcceleration": bool(row.get("orderInflowAcceleration", False)),
                "expectationSignal":      row.get("expectationSignal", "UNKNOWN"),
                "technicalTrend":         row.get("technicalTrend", "UNKNOWN"),
            }
    try:
        with open(_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.now().isoformat(), "snapshot": snap}, f, indent=2)
    except OSError as exc:
        logger.warning("Alert snapshot save failed: %s", exc)


def load_snapshot() -> Optional[dict]:
    """Load the previous scan snapshot for comparison. Returns None if absent."""
    if not os.path.exists(_HISTORY_PATH):
        return None
    try:
        with open(_HISTORY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("snapshot")
    except (OSError, json.JSONDecodeError):
        return None
