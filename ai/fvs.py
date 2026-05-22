"""Future Visibility Score (FVS) composite scoring engine.

FVS is a 0-100 weighted score representing how confidently visible a
company's future growth is. Primary KPI replacing convictionScore.

Spec: WIGA Enhanced Intelligence Spec v2.0, Section 4.
"""

from typing import Optional


# Signal weights per spec section 4.1 (all non-penalty weights sum to 1.08, see note)
# Signals map: S01=obRev, S02=inflowAccel, S03=execution, S04=mgmtConsistency,
#              S05=capex, S07=sectorTailwind, S08=promoter, S11=govtPolicy,
#              S13=marginExpansion, S15=workingCapitalStress(penalty)
# Remaining 16% across S06, S09, S10, S12, S14, S16
_W = {
    "s01": 0.15, "s02": 0.10, "s03": 0.10, "s04": 0.10,
    "s05": 0.08, "s07": 0.08, "s08": 0.08, "s11": 0.07,
    "s13": 0.08, "s15": -0.08,
    # remaining 0.16 split 6 ways
    "s06": 0.0267, "s09": 0.0267, "s10": 0.0267,
    "s12": 0.0267, "s14": 0.0267, "s16": 0.0267,
}

_BANDS = [
    (80, "Strong Buy", "green"),
    (60, "Watch Closely", "yellow"),
    (40, "Neutral", "orange"),
    (0,  "Avoid", "red"),
]


def fvs_band(score: float) -> tuple[str, str]:
    """Return (label, color) for a FVS score."""
    for threshold, label, color in _BANDS:
        if score >= threshold:
            return label, color
    return "Avoid", "red"


def fvs_emoji(score: float) -> str:
    """Return traffic-light emoji for a FVS score."""
    _, color = fvs_band(score)
    return {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}.get(color, "⚪")


def compute_fvs_from_scan(row: dict) -> float:
    """Compute FVS estimate from score_universe output.

    Uses signals available from batch scoring:
    S01 (orderBookRev), S02 (inflowAcceleration), S07 (sectorTailwind),
    S08 (promoter — default neutral), S11 (govtPolicy), S15 (concentration).
    Existing scores (growthScore, visibilityScore, convictionScore) proxy S03, S13, S04.
    """
    # If Claude already returned an fvs field, trust it
    if row.get("fvs") is not None:
        return float(row["fvs"])

    # S01: order book / revenue ratio → 0-10 (≥3x=10, 2x=7, 1.5x=5, <1=2)
    ob_rev = float(row.get("orderBookRev") or 0)
    s01 = min(10.0, ob_rev / 0.3) if ob_rev > 0 else 5.0

    # S02: order inflow acceleration
    s02 = 8.0 if row.get("orderInflowAcceleration") else 5.0

    # S03: execution efficiency → proxy via visibilityScore
    s03 = float(row.get("visibilityScore") or 5.0)

    # S04: management consistency → proxy via convictionScore
    s04 = float(row.get("convictionScore") or 5.0)

    # S05: capex — unknown at scan stage → neutral 5
    s05 = 5.0

    # S07: sector tailwind
    s07 = float(row.get("sectorTailwindScore") or 6.0)

    # S08: promoter → neutral default
    s08 = 6.0

    # S11: govt policy tailwind
    s11 = 8.0 if row.get("govtPolicyTailwind") else 5.0

    # S13: margin expansion → proxy via growthScore
    s13 = float(row.get("growthScore") or 5.0)

    # S15: working capital / concentration penalty (0 or 10 — penalised if concentration flag)
    s15 = 10.0 if row.get("concentrationFlag") else 0.0

    # Remaining signals → neutral 5
    s06 = s09 = s10 = s12 = s16 = 5.0
    # S14: customer concentration (higher = riskier; invert for scoring)
    s14 = 8.0 if not row.get("concentrationFlag") else 3.0

    weighted = (
        _W["s01"] * s01 + _W["s02"] * s02 + _W["s03"] * s03 + _W["s04"] * s04
        + _W["s05"] * s05 + _W["s07"] * s07 + _W["s08"] * s08 + _W["s11"] * s11
        + _W["s13"] * s13 + _W["s15"] * s15  # negative weight = penalty
        + _W["s06"] * s06 + _W["s09"] * s09 + _W["s10"] * s10
        + _W["s12"] * s12 + _W["s14"] * s14 + _W["s16"] * s16
    )
    # Scale 0-10 weighted sum → 0-100
    return round(min(100.0, max(0.0, weighted * 10)), 1)


def _expectation_delta(signal: str) -> float:
    """Map expectation signal to FVS delta points."""
    return {"BEAT": 6.0, "MIXED": 0.0, "MISS": -8.0, "UNKNOWN": 0.0}.get(signal, 0.0)


def compute_fvs_full(scan_row: dict, analysis: dict) -> float:
    """Compute refined FVS combining scan row and full deep-dive analysis.

    Replaces signal proxies with actual values from analyze_company output.
    """
    # Start from scan estimate
    base = compute_fvs_from_scan(scan_row)
    delta = 0.0

    # S04: replace proxy with actual management consistency score
    mc = analysis.get("managementConsistencyScore")
    if mc is not None:
        old_s04 = float(scan_row.get("convictionScore") or 5.0)
        delta += (float(mc) - old_s04) * _W["s04"] * 10

    # S05: capex expansion detected
    if analysis.get("capexExpansionDetected"):
        delta += _W["s05"] * 10 * 0.4  # partial credit

    # S08: promoter behaviour
    pb_scores = {"buying": 9.0, "neutral": 6.0, "selling": 3.0, "pledging": 1.0}
    pb = analysis.get("promoterBehaviour", "neutral")
    pb_actual = pb_scores.get(pb, 6.0)
    delta += (pb_actual - 6.0) * _W["s08"] * 10  # delta from default 6

    # S09: institutional accumulation
    if analysis.get("institutionalAccumulation"):
        delta += _W["s09"] * 10 * 0.5

    # S12: export opportunity
    if analysis.get("exportOpportunity"):
        delta += _W["s12"] * 10 * 0.6

    # S15: working capital stress additional penalty
    if analysis.get("workingCapitalStress"):
        delta += _W["s15"] * 10 * 0.5  # extra penalty (already partially in base)

    # S16: concall sentiment
    cs_deltas = {"positive": 1.5, "neutral": 0.0, "cautious": -1.0, "defensive": -2.5}
    cs = analysis.get("concallSentiment", "neutral")
    delta += cs_deltas.get(cs, 0.0) * _W["s16"] * 10

    # Expectation signal bonus/penalty (v3 spec)
    exp_sig = analysis.get("expectationSignal") or scan_row.get("expectationSignal", "UNKNOWN")
    delta += _expectation_delta(exp_sig)

    return round(min(100.0, max(0.0, base + delta)), 1)
