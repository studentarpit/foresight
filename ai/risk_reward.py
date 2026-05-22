"""Risk-Reward scoring engine — Section 12 of research spec."""

from typing import Optional


def compute_risk_reward_ratio(
    base_upside_pct: Optional[float],
    bear_downside_pct: Optional[float],
) -> Optional[float]:
    """Return risk-reward ratio: base_upside / |bear_downside|.

    3.0 = 3x upside for every 1x downside. Returns None when inputs are missing.
    """
    if base_upside_pct is None or bear_downside_pct is None:
        return None
    if bear_downside_pct >= 0:
        return None
    return round(abs(base_upside_pct) / abs(bear_downside_pct), 2)


def compute_risk_reward_score(
    bull_cagr: Optional[float],
    base_cagr: Optional[float],
    bear_cagr: Optional[float],
) -> float:
    """Return a 0-100 risk-reward score combining base CAGR and downside protection."""
    if base_cagr is None:
        return 0.0
    score = 0.0
    # Base CAGR component — max 50 pts
    if base_cagr >= 30:
        score += 50
    elif base_cagr >= 25:
        score += 42
    elif base_cagr >= 20:
        score += 35
    elif base_cagr >= 15:
        score += 25
    elif base_cagr >= 10:
        score += 15
    else:
        score += max(0.0, base_cagr)
    # Downside protection component — max 30 pts
    if bear_cagr is not None:
        if bear_cagr >= -5:
            score += 30
        elif bear_cagr >= -10:
            score += 22
        elif bear_cagr >= -20:
            score += 12
        elif bear_cagr >= -30:
            score += 5
    else:
        score += 15  # neutral when bear data absent
    # Bull upside bonus — max 20 pts
    if bull_cagr is not None:
        if bull_cagr >= 40:
            score += 20
        elif bull_cagr >= 30:
            score += 14
        elif bull_cagr >= 20:
            score += 8
        else:
            score += 4
    return min(100.0, round(score, 1))


def risk_reward_label(score: float) -> tuple:
    """Return (label, color) for a risk-reward score."""
    if score >= 75:
        return "Excellent", "#28a745"
    if score >= 55:
        return "Attractive", "#5cb85c"
    if score >= 35:
        return "Moderate", "#fd7e14"
    return "Poor", "#dc3545"
