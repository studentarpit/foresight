"""Expectation Intelligence Engine — core computation module.

Transforms raw guided-vs-actual quarterly data into:
- Per-quarter Expectation Gaps (revenue, margin, profit)
- Beat / Miss / Mixed signal with colour
- Guidance Reliability Score (rolling %)
- Expectation trend (improving / deteriorating)

Spec: Foresight v3 — Expectation Intelligence Engine, Section 4.
"""

from typing import Optional


# ── Per-quarter gap computation ───────────────────────────────────────────────

def compute_expectation_gap(entry: dict) -> dict:
    """Compute expectation gaps for a single quarter entry.

    entry keys (all optional, treated as 0 if absent):
      guidedRevGrowth, actualRevGrowth   — YoY revenue growth %
      guidedMargin, actualMargin         — EBITDA/PAT margin %
      guidedPATGrowth, actualPATGrowth   — YoY PAT growth %

    Returns dict with revGap, marginGap, patGap, signal, color, summary.
    """
    rev_gap    = _gap(entry, "actualRevGrowth",  "guidedRevGrowth")
    margin_gap = _gap(entry, "actualMargin",      "guidedMargin")
    pat_gap    = _gap(entry, "actualPATGrowth",   "guidedPATGrowth")

    beats = sum([
        rev_gap    is not None and rev_gap    > 0,
        margin_gap is not None and margin_gap > 0,
        pat_gap    is not None and pat_gap    > 0,
    ])
    tracked = sum([rev_gap is not None, margin_gap is not None, pat_gap is not None])

    if tracked == 0:
        signal, color = "UNKNOWN", "grey"
    elif beats == tracked:
        signal, color = "BEAT", "green"
    elif beats == 0:
        signal, color = "MISS", "red"
    else:
        signal, color = "MIXED", "yellow"

    summary = _build_summary(rev_gap, margin_gap, pat_gap, signal)

    return {
        "revGap":    round(rev_gap,    1) if rev_gap    is not None else None,
        "marginGap": round(margin_gap, 2) if margin_gap is not None else None,
        "patGap":    round(pat_gap,    1) if pat_gap    is not None else None,
        "signal":    signal,
        "color":     color,
        "summary":   summary,
    }


def _gap(entry: dict, actual_key: str, guided_key: str) -> Optional[float]:
    """Return actual - guided if both present, else None."""
    a = entry.get(actual_key)
    g = entry.get(guided_key)
    if a is None or g is None:
        return None
    return float(a) - float(g)


def _build_summary(rev_gap, margin_gap, pat_gap, signal: str) -> str:
    parts = []
    if rev_gap is not None:
        direction = "beat" if rev_gap > 0 else "missed"
        parts.append(f"Revenue {direction} guidance by {abs(rev_gap):.1f}pp")
    if margin_gap is not None:
        direction = "expanded" if margin_gap > 0 else "compressed"
        parts.append(f"margin {direction} {abs(margin_gap):.2f}pp vs guided")
    if pat_gap is not None:
        direction = "beat" if pat_gap > 0 else "missed"
        parts.append(f"PAT {direction} by {abs(pat_gap):.1f}pp")
    if not parts:
        return "Insufficient data."
    return "; ".join(parts) + "."


# ── Multi-quarter Guidance Reliability Score ──────────────────────────────────

def compute_guidance_reliability(history: list[dict]) -> float:
    """Return guidance reliability % from a list of quarterly entries.

    Each entry that has at least one guided+actual pair contributes.
    Score = fraction of individual metric comparisons where actual >= guided.
    """
    hits = 0
    total = 0
    for entry in history:
        for actual_key, guided_key in [
            ("actualRevGrowth",  "guidedRevGrowth"),
            ("actualMargin",     "guidedMargin"),
            ("actualPATGrowth",  "guidedPATGrowth"),
        ]:
            a = entry.get(actual_key)
            g = entry.get(guided_key)
            if a is not None and g is not None:
                total += 1
                if float(a) >= float(g):
                    hits += 1
    return round(hits / total * 100, 1) if total > 0 else 50.0


def reliability_label(score: float) -> tuple[str, str]:
    """Return (label, color) for a guidance reliability score."""
    if score >= 80:
        return "High Credibility", "green"
    if score >= 55:
        return "Moderate Credibility", "orange"
    return "Low Credibility", "red"


# ── Expectation trend (improving / deteriorating) ─────────────────────────────

def expectation_trend(history: list[dict]) -> str:
    """Return IMPROVING / DETERIORATING / STABLE based on last 3 quarters."""
    if len(history) < 2:
        return "INSUFFICIENT_DATA"
    recent = history[-3:] if len(history) >= 3 else history
    signals = []
    for entry in recent:
        gap = compute_expectation_gap(entry)
        signals.append(gap["signal"])

    beats  = signals.count("BEAT")
    misses = signals.count("MISS")
    if beats > misses:
        return "IMPROVING"
    if misses > beats:
        return "DETERIORATING"
    return "STABLE"


# ── Aggregate company expectation score (0-100) ───────────────────────────────

def company_expectation_score(history: list[dict]) -> float:
    """Combine guidance reliability + recent expectation trend into 0-100 score."""
    reliability = compute_guidance_reliability(history)
    trend = expectation_trend(history)
    trend_bonus = {"IMPROVING": 10.0, "STABLE": 0.0,
                   "DETERIORATING": -15.0, "INSUFFICIENT_DATA": 0.0}
    return round(min(100.0, max(0.0, reliability + trend_bonus.get(trend, 0.0))), 1)
