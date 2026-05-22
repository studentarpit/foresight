"""Expected CAGR computation from valuation scenarios — Section 11 of research spec."""

from typing import Optional


def compute_cagr(current_price: float, target_price: float, years: int) -> Optional[float]:
    """Return expected CAGR % given current price, target price, and horizon."""
    if current_price <= 0 or target_price <= 0 or years <= 0:
        return None
    return round(((target_price / current_price) ** (1 / years) - 1) * 100, 1)


def compute_scenario_cagrs(model: dict, current_price: float, years: int) -> dict:
    """Return dict with bull/base/bear expected CAGR % from a valuation model.

    Keys: 'bull', 'base', 'bear' — each is float % or None.
    """
    result = {}
    for scenario in ("bull", "base", "bear"):
        tp = float((model.get(scenario) or {}).get("targetPrice") or 0)
        result[scenario] = compute_cagr(current_price, tp, years) if tp > 0 else None
    return result


def compute_upside_downside(model: dict, current_price: float) -> dict:
    """Return base upside %, bear downside %, and bull upside % from a valuation model."""
    result = {"bullUpside": None, "baseUpside": None, "bearDownside": None}
    if current_price <= 0:
        return result
    for label, key in [("bullUpside", "bull"), ("baseUpside", "base"), ("bearDownside", "bear")]:
        tp = float((model.get(key) or {}).get("targetPrice") or 0)
        if tp > 0:
            result[label] = round(((tp / current_price) - 1) * 100, 1)
    return result
