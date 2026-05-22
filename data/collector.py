"""Fetches and filters financial data for the WIGA stock universe and mutual funds."""

import time
import logging
from typing import Callable, Optional
import pandas as pd
import requests
import yfinance as yf
from universe.stocks import STOCK_UNIVERSE
from data.scraper import fetch_screener_data, fetch_concall_text

logger = logging.getLogger(__name__)

# 500 Cr in INR = 5,000,000,000 (yfinance returns raw INR)
_MCAP_MIN_INR = 5_000_000_000


def _tech_trend_label(price: float, dmas: dict) -> str:
    """Return a STRONG_UPTREND/UPTREND/MIXED/WEAK/DOWNTREND label from DMA positions."""
    above = sum(1 for d in dmas.values() if d and price > d)
    total = sum(1 for d in dmas.values() if d)
    if total == 0:
        return "UNKNOWN"
    if above == total:
        return "STRONG_UPTREND"
    if above >= 3 and dmas.get("dma200") and price > dmas["dma200"]:
        return "UPTREND"
    if above >= 2 and dmas.get("dma200") and price > dmas["dma200"]:
        return "UPTREND"
    if above == 0:
        return "DOWNTREND"
    if dmas.get("dma200") and price < dmas["dma200"]:
        return "WEAK"
    return "MIXED"


def _fetch_yfinance_data(ticker: str) -> dict:
    """Fetch price, MCap, PE, all DMAs, relative strength, and volume trend. Raises on failure."""
    symbol = f"{ticker}.NS"
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y", interval="1d")
    if hist.empty:
        raise ValueError(f"No history for {ticker}")
    info = stock.fast_info
    close = hist["Close"]
    price = float(close.iloc[-1])
    mcap = getattr(info, "market_cap", None)
    pe = getattr(info, "pe_forward", None) or getattr(info, "pe_trailing", None)

    def _dma(n: int):
        return float(close.rolling(n).mean().iloc[-1]) if len(close) >= n else None

    dma20  = _dma(20)
    dma50  = _dma(50)
    dma100 = _dma(100)
    dma200 = _dma(200)

    # Relative strength: price vs 52-week high and low
    high52 = float(close.max())
    low52  = float(close.min())
    rs_pct = round((price - low52) / (high52 - low52) * 100, 1) if high52 != low52 else 50.0

    # Volume trend: avg last 20d vs avg prior 20d (proxy for accumulation)
    vol = hist["Volume"]
    vol_recent = float(vol.iloc[-20:].mean()) if len(vol) >= 20 else None
    vol_prior  = float(vol.iloc[-40:-20].mean()) if len(vol) >= 40 else None
    vol_trend  = "ACCUMULATING" if (vol_recent and vol_prior and vol_recent > vol_prior * 1.1) \
                 else "DISTRIBUTING" if (vol_recent and vol_prior and vol_recent < vol_prior * 0.9) \
                 else "NEUTRAL"

    dmas = {"dma20": dma20, "dma50": dma50, "dma100": dma100, "dma200": dma200}
    return {
        "price": price,
        "mcap": float(mcap) if mcap else None,
        "pe": float(pe) if pe else None,
        "dma20": dma20, "dma50": dma50, "dma100": dma100, "dma200": dma200,
        "above200dma": (price > dma200) if dma200 else False,
        "above100dma": (price > dma100) if dma100 else False,
        "above50dma":  (price > dma50)  if dma50  else False,
        "above20dma":  (price > dma20)  if dma20  else False,
        "relativeStrength": rs_pct,
        "volumeTrend": vol_trend,
        "technicalTrend": _tech_trend_label(price, dmas),
    }


def _compute_ob_trend(inflow: float, execution: float) -> str:
    """Return order book trend label from inflow vs execution rates."""
    if inflow > execution * 1.1:
        return "ACCELERATING"
    if inflow < execution * 0.9:
        return "DECLINING"
    return "STABLE"


def _passes_stage1(row: dict) -> bool:
    """Return True if a stock row passes all Stage 1 financial filter thresholds.

    Stage 1 gates:
      ROE > 12% | Rev CAGR > 15% | D/E < 1.0 | MCap > 500 Cr
      Order Book / Revenue > 1.5x  (revenue visibility floor — 18+ months won)
    """
    ob_rev = row.get("orderBookRev")
    ob_ok = (ob_rev is None) or (ob_rev >= 1.5)  # pass through if data unavailable
    return (
        (row.get("roe") or 0) > 12
        and (row.get("revcagr") or 0) > 15
        and (row.get("debtEq") or 99) < 1.0
        and (row.get("mcap") or 0) > _MCAP_MIN_INR
        and ob_ok
    )


def collect_all(progress_cb: Optional[Callable[[int, int], None]] = None) -> pd.DataFrame:
    """Scan curated universe, merge sources, apply Stage 1 filter, return DataFrame.

    progress_cb(current, total) is called after each ticker if provided.
    Bad tickers are skipped silently. Never raises.
    """
    rows = []
    total = len(STOCK_UNIVERSE)
    for idx, stock in enumerate(STOCK_UNIVERSE, start=1):
        ticker = stock["ticker"]
        if progress_cb:
            progress_cb(idx, total)
        try:
            base = _fetch_yfinance_data(ticker)
        except Exception as exc:
            logger.warning("yfinance failed for %s: %s", ticker, exc)
            continue

        screener = fetch_screener_data(ticker)
        concall_text = fetch_concall_text(ticker)  # S16: '' when unavailable
        # Fallback: use yfinance for any missing fundamentals
        row = {
            "ticker": ticker,
            "name": stock["name"],
            "sector": stock["sector"],
            "mcap": base["mcap"],
            "roe": screener.get("roe"),
            "roce": screener.get("roce"),
            "revcagr": screener.get("revcagr"),
            "profitcagr": screener.get("profitcagr"),
            "debtEq": screener.get("debtEq"),
            "orderBookRev": screener.get("orderBookRev"),
            "orderBookTrend": screener.get("orderBookTrend", "STABLE"),
            "price": base["price"],
            "pe": base["pe"],
            "above200dma":  base["above200dma"],
            "above100dma":  base.get("above100dma", False),
            "above50dma":   base.get("above50dma", False),
            "above20dma":   base.get("above20dma", False),
            "dma20":        base.get("dma20"),
            "dma50":        base.get("dma50"),
            "dma100":       base.get("dma100"),
            "dma200":       base.get("dma200"),
            "relativeStrength": base.get("relativeStrength", 50.0),
            "volumeTrend":  base.get("volumeTrend", "NEUTRAL"),
            "technicalTrend": base.get("technicalTrend", "UNKNOWN"),
            "screenerUrl":  screener.get("screenerUrl", f"https://www.screener.in/company/{ticker}/"),
            "concallText":  concall_text,
        }
        rows.append(row)
        time.sleep(0.3)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    for col in ["mcap", "roe", "revcagr", "debtEq", "pe", "price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["above200dma"] = df["above200dma"].fillna(False)

    filtered = df[df.apply(_passes_stage1, axis=1)].copy()
    filtered = filtered.sort_values("mcap", ascending=False).reset_index(drop=True)
    return filtered


def fetch_mf_data() -> pd.DataFrame:
    """Fetch top Indian mutual funds from mfapi.in and compute return/risk metrics.

    Skips funds with < 3yr NAV history. Never raises.
    """
    empty = pd.DataFrame(columns=["schemeCode", "name", "category", "return1yr",
                                   "return3yr", "return5yr", "return10yr",
                                   "maxDrawdown", "consistencyScore"])
    try:
        resp = requests.get("https://api.mfapi.in/mf", timeout=15)
        if resp.status_code != 200:
            return empty
        all_funds = resp.json()
    except Exception as exc:
        logger.warning("mfapi.in list fetch failed: %s", exc)
        return empty

    # Sample diversified categories; pick first 80 schemes
    sampled = [f for f in all_funds if any(
        kw in f.get("schemeName", "").lower()
        for kw in ["small cap", "mid cap", "flexi", "multi cap", "sectoral", "large cap"]
    )][:80]

    rows = []
    for fund in sampled:
        code = fund.get("schemeCode")
        name = fund.get("schemeName", "")
        row = _fetch_mf_nav_stats(code, name)
        if row:
            rows.append(row)

    return pd.DataFrame(rows) if rows else empty


def _fetch_mf_nav_stats(code: int, name: str) -> Optional[dict]:
    """Fetch NAV history for a scheme and compute return/risk stats.

    Returns None if insufficient history (< 3yr).
    """
    try:
        resp = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        navs = data.get("data", [])
        if len(navs) < 756:  # ~3 years of trading days
            return None

        # NAV list is newest-first; reverse for chronological order
        nav_series = pd.Series(
            [float(n["nav"]) for n in reversed(navs)],
            dtype=float
        )
        meta = data.get("meta", {})
        category = _infer_category(name, meta.get("scheme_type", ""))

        r1 = _cagr(nav_series, 252)
        r3 = _cagr(nav_series, 756)
        r5 = _cagr(nav_series, 1260) if len(nav_series) >= 1260 else None
        r10 = _cagr(nav_series, 2520) if len(nav_series) >= 2520 else None
        max_dd = _max_drawdown(nav_series)
        consistency = _consistency_score(nav_series)

        return {
            "schemeCode": code,
            "name": name[:80],
            "category": category,
            "return1yr": round(r1, 2) if r1 is not None else None,
            "return3yr": round(r3, 2) if r3 is not None else None,
            "return5yr": round(r5, 2) if r5 is not None else None,
            "return10yr": round(r10, 2) if r10 is not None else None,
            "maxDrawdown": round(max_dd, 2),
            "consistencyScore": round(consistency, 1),
        }
    except Exception as exc:
        logger.warning("NAV stats failed for %s: %s", code, exc)
        return None


def _cagr(nav: pd.Series, days: int) -> Optional[float]:
    """Compute CAGR over last `days` trading days from NAV series."""
    if len(nav) < days:
        return None
    start, end = nav.iloc[-days], nav.iloc[-1]
    if start <= 0:
        return None
    years = days / 252
    return ((end / start) ** (1 / years) - 1) * 100


def _max_drawdown(nav: pd.Series) -> float:
    """Compute maximum peak-to-trough drawdown percentage from NAV series."""
    peak = nav.cummax()
    drawdown = (nav - peak) / peak
    return abs(float(drawdown.min())) * 100


def _consistency_score(nav: pd.Series) -> float:
    """Score 0-10 based on fraction of calendar years with positive returns."""
    if len(nav) < 252:
        return 0.0
    annual_returns = nav.pct_change(252).dropna()
    if annual_returns.empty:
        return 0.0
    positive = (annual_returns > 0).sum()
    return round(10 * positive / len(annual_returns), 1)


def _infer_category(name: str, scheme_type: str) -> str:
    """Infer fund category from name and scheme_type string."""
    name_lower = name.lower()
    if "small cap" in name_lower:
        return "Small Cap"
    if "mid cap" in name_lower:
        return "Mid Cap"
    if "large cap" in name_lower:
        return "Large Cap"
    if "flexi" in name_lower or "multi cap" in name_lower:
        return "Flexi Cap"
    if "sectoral" in name_lower or "sector" in name_lower or "theme" in name_lower:
        return "Sectoral"
    return scheme_type or "Other"
