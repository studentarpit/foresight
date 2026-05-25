"""Shared UI utilities — colors, formatters, and HTML helpers used across tabs."""

import pandas as pd

SECTOR_COLORS = {
    "Defence":    "#5c6bc0",
    "Railways":   "#26a69a",
    "EPC":        "#ef5350",
    "EMS":        "#ab47bc",
    "Power":      "#ffa726",
    "Solar/Wind": "#66bb6a",
}

SIGNAL_BORDER = {
    "🟢 Strong Buy": "#00e676",
    "🟡 Watch":      "#ffd740",
    "🟠 Neutral":    "#ff9800",
    "🔴 Avoid":      "#ff5252",
}


def hex_to_rgb(hex_color: str) -> str:
    """Convert '#rrggbb' to 'r,g,b' string for CSS rgba()."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"
    return "128,128,128"


def fmt_mcap(v) -> str:
    """Format a raw INR market-cap value as '₹X,XX,XXX Cr'."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "N/A"
    return f"₹{v / 1e7:,.0f} Cr"


def fmt_pct(v, decimals: int = 1) -> str:
    """Format a numeric value as a percentage string, or '—' if missing."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{float(v):.{decimals}f}%"


# ── Spec 07: Smart Money Signal card (used on company cards in Discover tab) ──

def smart_money_card_html(accum: dict, flow_score: int) -> str:
    """Return HTML for the Smart Money Signal card for a company card."""
    pattern   = accum.get("pattern", "NEUTRAL")
    fii_trend = accum.get("fii_trend", "STABLE")
    dii_trend = accum.get("dii_trend", "STABLE")
    fii_qoq   = accum.get("fii_last_qoq")
    dii_qoq   = accum.get("dii_last_qoq")
    duration  = accum.get("duration_quarters", 0)
    combined  = accum.get("combined_signal", "NEUTRAL")
    verdict   = accum.get("smart_money_verdict", "No clear institutional trend.")

    pat_color = {
        "ACCUMULATING": "#00e676",
        "DISTRIBUTING": "#ff5252",
        "NEUTRAL":      "#aaa",
    }.get(pattern, "#aaa")

    def _qoq_str(v, label: str) -> str:
        if v is None:
            return f"{label}: —"
        arrow = "📈" if v > 0 else "📉" if v < 0 else "➡️"
        sign  = "+" if v >= 0 else ""
        dur   = f" ({duration}Q)" if duration else ""
        return f"{label}: {arrow} {sign}{v:.2f}%{dur}"

    if flow_score is None:
        score_bg = "#1e1e2e"
    else:
        score_bg = "#1a2e1a" if flow_score >= 60 else "#2e1a1a" if flow_score <= 40 else "#1e1e2e"
    score_label = flow_score if flow_score is not None else "N/A"

    return (
        f'<div style="background:{score_bg};border:1px solid {pat_color};'
        f'border-radius:8px;padding:10px 12px;margin-top:8px;font-size:0.78rem">'
        f'<div style="font-weight:700;color:{pat_color};margin-bottom:4px">'
        f'🏦 Smart Money · Flow Score: {score_label}</div>'
        f'<div style="opacity:0.85">{_qoq_str(fii_qoq, "FII")}</div>'
        f'<div style="opacity:0.85">{_qoq_str(dii_qoq, "DII")}</div>'
        f'<div style="margin-top:4px;font-weight:600;color:{pat_color}">'
        f'{pattern}</div>'
        f'<div style="opacity:0.7;margin-top:2px">{verdict[:80]}{"…" if len(verdict) > 80 else ""}</div>'
        f'</div>'
    )
