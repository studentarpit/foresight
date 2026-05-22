"""Pre-generated company research report + valuation model store with freshness tracking.

Section 13 of research spec — local prototype using JSON files.
"""

import json
import os
from datetime import datetime
from typing import Optional

_REPORTS_DIR = os.path.join(os.path.dirname(__file__), "company_reports")
_MODELS_DIR  = os.path.join(os.path.dirname(__file__), "valuation_models")


def _report_path(ticker: str) -> str:
    return os.path.join(_REPORTS_DIR, f"{ticker}.json")


def _model_path(ticker: str) -> str:
    return os.path.join(_MODELS_DIR, f"{ticker}.json")


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(ticker: str, report: dict) -> None:
    """Persist a pre-generated research report for a ticker."""
    os.makedirs(_REPORTS_DIR, exist_ok=True)
    report["generatedDate"] = datetime.now().strftime("%Y-%m-%d")
    report["ticker"] = ticker
    with open(_report_path(ticker), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def load_report(ticker: str) -> Optional[dict]:
    """Return stored report for a ticker, or None if not found."""
    try:
        with open(_report_path(ticker), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_freshness(ticker: str) -> str:
    """Return 'Fresh' / 'Needs Refresh' / 'Stale' / 'No Report'."""
    path = _report_path(ticker)
    if not os.path.exists(path):
        return "No Report"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        generated = datetime.strptime(data.get("generatedDate", "2000-01-01"), "%Y-%m-%d")
        age = (datetime.now() - generated).days
        if age <= 7:
            return "Fresh"
        if age <= 30:
            return "Needs Refresh"
        return "Stale"
    except Exception:
        return "Stale"


def list_all_reports() -> list:
    """Return metadata list for all stored reports, newest first."""
    results = []
    try:
        for fname in os.listdir(_REPORTS_DIR):
            if not fname.endswith(".json"):
                continue
            ticker = fname[:-5]
            report = load_report(ticker)
            if report:
                results.append({
                    "ticker": ticker,
                    "generatedDate": report.get("generatedDate", ""),
                    "freshness": get_freshness(ticker),
                    "aiView": (report.get("aiView") or "")[:120],
                })
    except OSError:
        pass
    return sorted(results, key=lambda x: x["generatedDate"], reverse=True)


# ── Valuation models ──────────────────────────────────────────────────────────

def save_valuation(ticker: str, model: dict, years: int, current_price: float) -> None:
    """Persist a 3-scenario valuation model for a ticker."""
    os.makedirs(_MODELS_DIR, exist_ok=True)
    model = dict(model)
    model["savedDate"]    = datetime.now().strftime("%Y-%m-%d")
    model["ticker"]       = ticker
    model["years"]        = years
    model["currentPrice"] = current_price
    with open(_model_path(ticker), "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)


def load_valuation(ticker: str) -> Optional[dict]:
    """Return stored valuation model for a ticker, or None."""
    try:
        with open(_model_path(ticker), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_all_valuations() -> list:
    """Return metadata list for all stored valuation models."""
    results = []
    try:
        for fname in os.listdir(_MODELS_DIR):
            if not fname.endswith(".json"):
                continue
            ticker = fname[:-5]
            model = load_valuation(ticker)
            if model:
                base_cagr = (model.get("base") or {}).get("cagr")
                results.append({
                    "ticker": ticker,
                    "savedDate": model.get("savedDate", ""),
                    "years": model.get("years", 3),
                    "currentPrice": model.get("currentPrice", 0),
                    "baseCagr": base_cagr,
                })
    except OSError:
        pass
    return sorted(results, key=lambda x: x["savedDate"], reverse=True)
