"""Claude-powered analysis functions: batch scoring, deep dive, valuation, tracker, MF."""

import json
import logging
import os
import time
from typing import Optional, Union

import anthropic
import pandas as pd

from ai.fvs import compute_fvs_from_scan, compute_fvs_full
from ai.prompts import (
    DEEP_ANALYSIS_PROMPT,
    FULL_REPORT_PROMPT,
    MASTER_TRACKER_PROMPT,
    MF_ANALYSIS_PROMPT,
    ORDER_EXTRACTION_PROMPT,
    SCAN_PROMPT,
    VALUATION_PROMPT,
)
from ai.token_logger import record, session_summary  # noqa: F401

logger = logging.getLogger(__name__)
_MODEL = "claude-sonnet-4-6"
_BATCH_SIZE = 10  # companies per Claude call to stay within token limits


def _get_client() -> anthropic.Anthropic:
    """Return an Anthropic client using ANTHROPIC_API_KEY from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(prompt: str, max_tokens: int = 2048, label: str = "") -> Optional[str]:
    """Call Claude and return response text. Returns None on any error."""
    try:
        client = _get_client()
        msg = client.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        record(label, msg.usage.input_tokens, msg.usage.output_tokens)
        return msg.content[0].text
    except Exception as exc:
        logger.warning("Claude API call failed: %s", exc)
        return None


def _parse_json(text: Optional[str], fallback: dict) -> dict:
    """Parse JSON from Claude response, return fallback on failure."""
    if not text:
        return fallback
    try:
        clean = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("JSON parse failed: %s | text=%s", exc, text[:200])
        return fallback


def score_universe(df: pd.DataFrame) -> pd.DataFrame:
    """Batch-score all filtered companies with Claude FVS and conviction scores.

    Processes in batches of _BATCH_SIZE. Adds FVS and score columns to df.
    """
    all_scores: list[dict] = []
    rows = df.to_dict(orient="records")

    for i in range(0, min(len(rows), 30), _BATCH_SIZE):
        batch = rows[i: i + _BATCH_SIZE]
        prompt = SCAN_PROMPT.format(companies_json=json.dumps(batch))
        text = _call_claude(prompt, max_tokens=1500, label=f"scan_batch_{i // _BATCH_SIZE}")
        parsed = _parse_json(text, [])
        if isinstance(parsed, list):
            all_scores.extend(parsed)
        time.sleep(0.5)

    if not all_scores:
        # Heuristic fallback when API unavailable
        for row in rows:
            roe = float(row.get("roe") or 0)
            cagr = float(row.get("revcagr") or 0)
            debt = float(row.get("debtEq") or 1)
            gs = round(min(10, cagr / 5), 1)
            rs = round(min(10, debt * 3 + 2), 1)
            vs = round(min(10, roe / 3), 1)
            cs = round(min(10, (roe / 20 + cagr / 30) * 10), 1)
            all_scores.append({
                "ticker": row["ticker"],
                "growthScore": gs,
                "riskScore": rs,
                "visibilityScore": vs,
                "convictionScore": cs,
                "concentrationFlag": False,
                "sectorTailwindScore": 6.0,
                "govtPolicyTailwind": False,
                "orderInflowAcceleration": False,
                "fvs": None,
                "oneLineThesis": "",
                "expectationSignal": "UNKNOWN",
                "aiExplanation": "",
            })

    scores_df = pd.DataFrame(all_scores)

    # Ensure all expected columns exist
    _defaults = {
        "growthScore": 5.0, "riskScore": 5.0, "visibilityScore": 5.0,
        "convictionScore": 5.0, "concentrationFlag": False,
        "sectorTailwindScore": 6.0, "govtPolicyTailwind": False,
        "orderInflowAcceleration": False, "fvs": None, "oneLineThesis": "",
        "expectationSignal": "UNKNOWN", "aiExplanation": "",
    }
    for col, default in _defaults.items():
        if col not in scores_df.columns:
            scores_df[col] = default

    merge_cols = list(_defaults.keys()) + ["ticker"]
    merge_cols = [c for c in merge_cols if c in scores_df.columns]
    merged = df.merge(scores_df[merge_cols], on="ticker", how="left")

    # Compute FVS for any row where Claude didn't return one
    def _fvs(r):
        v = r.get("fvs")
        if v is not None and not (isinstance(v, float) and pd.isna(v)):
            return float(v)
        return compute_fvs_from_scan(r)

    merged["fvs"] = merged.apply(_fvs, axis=1)

    from ai.heat_engine import compute_heat_score
    merged["heatScore"] = merged.apply(
        lambda r: compute_heat_score({}, r.to_dict()), axis=1
    )

    # Spec 07: add FII/DII Flow Score (non-blocking; None when data unavailable)
    try:
        from data.fii_dii_engine import compute_flow_score
        merged["flowScore"] = merged["ticker"].apply(
            lambda t: _safe_flow_score(t, compute_flow_score)
        )
    except Exception:
        merged["flowScore"] = None

    return merged


def _safe_flow_score(ticker: str, fn):
    """Call compute_flow_score; returns None (not 50) when data is unavailable."""
    try:
        return fn(ticker)
    except Exception:
        return None


def analyze_company(company: Union[pd.Series, dict]) -> dict:
    """Full deep-dive AI analysis for one company. Returns enriched dict on success."""
    data = company.to_dict() if isinstance(company, pd.Series) else company
    prompt = DEEP_ANALYSIS_PROMPT.format(company_json=json.dumps(data))
    ticker = data.get("ticker", "??")
    text = _call_claude(prompt, max_tokens=2000, label=f"deep_{ticker}")
    fallback = {
        "growthScore": data.get("growthScore", 5.0),
        "riskScore": data.get("riskScore", 5.0),
        "visibilityScore": data.get("visibilityScore", 5.0),
        "convictionScore": data.get("convictionScore", 5.0),
        "thesis": f"{data.get('name', 'Company')} operates in a high-growth sector with order book visibility.",
        "bullCase": "Sector tailwinds and strong order inflows drive re-rating.",
        "baseCase": "Steady execution with moderate growth in line with guidance.",
        "bearCase": "Execution delays and margin pressure weigh on earnings.",
        "risks": ["Execution risk on large orders", "Working capital pressure", "Competitive intensity"],
        "orderBookInsight": "Order book trend is " + data.get("orderBookTrend", "STABLE") + ".",
        "technicalView": "Price is " + ("above" if data.get("above200dma") else "below") + " the 200 DMA.",
        "catalysts": ["New order announcements", "Quarterly earnings beat"],
        "concentrationRisk": {"flag": data.get("concentrationFlag", False), "detail": "Unknown", "severity": "MEDIUM"},
        "managementConsistencyScore": 6.0,
        "managementConsistencyEvidence": [],
        "capexExpansionDetected": False,
        "capexKeywords": [],
        "exportOpportunity": False,
        "exportCommentary": "Primarily domestic focused.",
        "workingCapitalStress": False,
        "workingCapitalFlags": [],
        "promoterBehaviour": "neutral",
        "institutionalAccumulation": False,
        "institutionalTrend": "Insufficient data.",
        "concallSentiment": "neutral",
        "concallToneKeywords": [],
        "expectationSignal": "UNKNOWN",
        "expectationGapSummary": "Insufficient data to assess expectation gap.",
        "guidanceReliabilityAssessment": "Track record not yet established in this tool.",
        "aiExplanation": f"Selected because {data.get('name', ticker)} shows growth momentum in {data.get('sector', 'its sector')}.",
    }
    result = _parse_json(text, fallback)
    result["fvsRefined"] = compute_fvs_full(data, result)
    return result


def build_valuation_model(company: Union[pd.Series, dict], assumptions: dict) -> dict:
    """Generate 3-scenario DCF/PE valuation model via Claude."""
    data = company.to_dict() if isinstance(company, pd.Series) else company
    prompt = VALUATION_PROMPT.format(
        company_json=json.dumps(data),
        assumptions_json=json.dumps(assumptions),
    )
    ticker = data.get("ticker", "??")
    text = _call_claude(prompt, max_tokens=1500, label=f"valuation_{ticker}")
    price = float(data.get("price") or 100)
    rev = float(data.get("mcap") or 1000) / 1e7
    years = int(assumptions.get("years", 3))
    pe = float(assumptions.get("peMultiple", 25))
    fallback = {"operatingLeverageDetected": False, "marginTrend": "stable",
                "valuationCommentary": "Based on guidance vs actual metrics."}
    for label, factor in [("bull", 1.3), ("base", 1.0), ("bear", 0.7)]:
        g = float(assumptions.get("revenueGrowth", 0.2)) * factor
        m = 0.12 * (1 + float(assumptions.get("marginExpansion", 0.02)) * factor)
        revenues, profits = [], []
        r = rev
        for _ in range(years):
            r *= (1 + g)
            revenues.append(round(r, 1))
            profits.append(round(r * m, 1))
        tp = round(profits[-1] * pe, 1)
        fallback[label] = {
            "revenue": revenues, "profit": profits,
            "targetPrice": tp,
            "cagr": round(((tp / price) ** (1 / years) - 1) * 100, 1),
        }
    return _parse_json(text, fallback)


def update_master_tracker(company: dict, quarterly_data: dict) -> dict:
    """Score thesis integrity by comparing guidance vs actuals via Claude."""
    prompt = MASTER_TRACKER_PROMPT.format(
        company_json=json.dumps(company),
        quarterly_json=json.dumps(quarterly_data),
    )
    text = _call_claude(prompt, max_tokens=512, label=f"tracker_{company.get('ticker','??')}")
    guided_rev = float(quarterly_data.get("guidedRevenue") or 0)
    actual_rev = float(quarterly_data.get("actualRevenue") or 0)
    guided_m = float(quarterly_data.get("guidedMargin") or 0)
    actual_m = float(quarterly_data.get("actualMargin") or 0)
    scores = []
    if guided_rev > 0:
        scores.append(min(1.0, actual_rev / guided_rev))
    if guided_m > 0:
        scores.append(min(1.0, actual_m / guided_m))
    acc = round(sum(scores) / len(scores) * 100, 1) if scores else 50.0
    if acc >= 85:
        status, color, action = "ON_TRACK", "green", "HOLD"
    elif acc >= 60:
        status, color, action = "WATCH", "yellow", "REVIEW"
    else:
        status, color, action = "BROKEN", "red", "EXIT"
    fallback = {
        "thesisStatus": status, "thesisColor": color,
        "guidanceAccuracy": acc,
        "commentary": "Based on guidance vs actual metrics.",
        "action": action,
    }
    return _parse_json(text, fallback)


def extract_order_from_announcement(ticker: str, company_name: str, announcement_text: str) -> dict:
    """Use Claude to extract structured order data from a corporate announcement."""
    prompt = ORDER_EXTRACTION_PROMPT.format(
        ticker=ticker,
        company_name=company_name,
        announcement_text=announcement_text[:1000],
    )
    text = _call_claude(prompt, max_tokens=512, label=f"order_{ticker}")
    fallback = {
        "order_value_cr": None,
        "customer": "Undisclosed",
        "customer_type": "unknown",
        "order_type": "domestic",
        "segment": None,
        "execution_period": None,
        "is_repeat_order": False,
        "description": announcement_text[:200],
        "significance": "MEDIUM",
        "confidence": 0.4,
    }
    return _parse_json(text, fallback)


def generate_full_report(company: dict, order_summary: str = "", concall_text: str = "") -> dict:
    """Generate a comprehensive pre-built research report for a company via Claude."""
    data = company.to_dict() if hasattr(company, "to_dict") else company
    prompt = FULL_REPORT_PROMPT.format(
        company_json=json.dumps(data),
        order_summary=order_summary[:800] if order_summary else "No recent order data available.",
        concall_text=concall_text[:600] if concall_text else "No concall transcript available.",
    )
    ticker = data.get("ticker", "??")
    text = _call_claude(prompt, max_tokens=2500, label=f"report_{ticker}")
    name = data.get("name", ticker)
    sector = data.get("sector", "Capital Goods")
    fallback = {
        "companyOverview": f"{name} is a listed Indian company operating in the {sector} sector.",
        "businessModel": "Revenue is generated through order-based project execution and product sales.",
        "revenueSegments": [sector],
        "sectorOpportunity": f"The {sector} sector benefits from domestic infrastructure spending and policy tailwinds.",
        "recentDevelopments": "Latest developments available from quarterly results and exchange filings.",
        "orderWinsAnalysis": order_summary[:200] if order_summary else "Order history not yet available in this tool.",
        "financialSummary": f"Revenue CAGR: {data.get('revcagr','—')}%, ROE: {data.get('roe','—')}%.",
        "marginTrend": "stable",
        "managementQuality": "Management track record requires deeper analysis.",
        "growthTriggers": ["Order inflow acceleration", "Sector tailwinds", "Capacity expansion"],
        "risks": ["Execution risk", "Working capital pressure", "Competitive intensity"],
        "bullCase": "Strong order pipeline and sector tailwinds drive re-rating.",
        "baseCase": "Steady execution with moderate growth in line with guidance.",
        "bearCase": "Execution delays and margin pressure weigh on earnings.",
        "expectedBaseCagr": None,
        "riskRewardAssessment": "Risk-reward requires valuation model for full assessment.",
        "aiView": f"{name} is a {sector} company with moderate long-term investment appeal.",
        "reportSections": ["companyOverview", "orderWins", "financials", "risks"],
    }
    return _parse_json(text, fallback)


def analyze_mf(fund: dict) -> dict:
    """Score a mutual fund for long-term consistency via Claude."""
    prompt = MF_ANALYSIS_PROMPT.format(fund_json=json.dumps(fund))
    text = _call_claude(prompt, max_tokens=512, label=f"mf_{fund.get('name','??')[:20]}")
    consistency = float(fund.get("consistencyScore") or 5)
    drawdown = float(fund.get("maxDrawdown") or 20)
    r10 = float(fund.get("return10yr") or 0)
    rec = "STRONG" if r10 > 14 and drawdown < 30 else "MODERATE" if r10 > 10 else "AVOID"
    fallback = {
        "consistencyScore": consistency,
        "drawdownRisk": round(drawdown / 10, 1),
        "recommendation": rec,
        "reasoning": "Based on historical NAV performance.",
    }
    return _parse_json(text, fallback)
