"""Sidebar filter rendering and DataFrame filtering helpers for the Foresight dashboard."""

from typing import List, Optional
import pandas as pd
import streamlit as st

_SECTORS     = ["Defence", "Railways", "EPC", "EMS", "Power", "Solar/Wind"]
_MCAP_CATS   = ["Small", "Mid", "Large"]
_OB_TRENDS   = ["All", "ACCELERATING", "STABLE", "DECLINING"]
_TECH_TRENDS = ["All", "STRONG_UPTREND", "UPTREND", "MIXED", "WEAK", "DOWNTREND"]
_EXP_SIGNALS = ["All", "BEAT", "MIXED", "MISS"]
_FRESHNESS   = ["Fresh", "Needs Refresh", "Stale", "No Report"]


def render_horizontal_filters() -> dict:
    """Render inline horizontal filter bar. All widgets use keyed session state."""
    # ── Primary filter row ────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 1.5, 1.5, 1.2])
    with c1:
        sectors = st.multiselect(
            "Sector", _SECTORS, default=st.session_state.get("hf_sectors", _SECTORS),
            key="hf_sectors", placeholder="All Sectors",
        )
    with c2:
        mcap_cats = st.multiselect(
            "Market Cap", _MCAP_CATS,
            default=st.session_state.get("hf_mcap", ["Small", "Mid"]),
            key="hf_mcap", placeholder="All Caps",
        )
    with c3:
        ob_trend = st.selectbox(
            "Order Book", _OB_TRENDS,
            index=_OB_TRENDS.index(st.session_state.get("hf_ob_trend", "All")),
            key="hf_ob_trend",
        )
    with c4:
        exp_signal = st.selectbox(
            "Expectation", _EXP_SIGNALS,
            index=_EXP_SIGNALS.index(st.session_state.get("hf_exp_signal", "All")),
            key="hf_exp_signal",
        )
    with c5:
        min_fvs = st.slider(
            "Min FVS", 0, 100,
            value=st.session_state.get("hf_min_fvs", 0),
            step=5, key="hf_min_fvs",
        )

    # ── Toggle row ────────────────────────────────────────────────────────────
    t1, t2, _spacer = st.columns([1.5, 1.8, 6])
    with t1:
        above_dma = st.toggle(
            "Above 200 DMA only",
            value=st.session_state.get("hf_above_dma", False),
            key="hf_above_dma",
        )
    with t2:
        ob_accel = st.toggle(
            "OB Accelerating only",
            value=st.session_state.get("hf_ob_accel", False),
            key="hf_ob_accel",
        )

    # ── Advanced filters (collapsed) ──────────────────────────────────────────
    min_base_cagr = 0
    max_bear_down = -60
    min_grs       = 0
    freshness_filter: list = []
    with st.expander("⚙️ Advanced Filters"):
        ca1, ca2, ca3, ca4 = st.columns(4)
        with ca1:
            min_base_cagr = st.slider("Min Base CAGR %",     0,   50,  0, 5,   key="hf_min_base_cagr")
        with ca2:
            max_bear_down = st.slider("Max Bear Downside %", -60,  0, -60, 5,  key="hf_max_bear_down")
        with ca3:
            min_grs = st.slider("Min GRS %",                 0,  100,  0,  10, key="hf_min_grs")
        with ca4:
            freshness_filter = st.multiselect(
                "Report Freshness", _FRESHNESS, default=[], key="hf_freshness",
            )

    return {
        "sectors":           sectors or _SECTORS,
        "mcap_cats":         mcap_cats or _MCAP_CATS,
        "min_conviction":    0.0,
        "min_fvs":           min_fvs,
        "ob_trend":          ob_trend,
        "exp_signal":        exp_signal,
        "tech_trend":        "All",
        "above_200dma":      above_dma,
        "ob_accelerating":   ob_accel,
        "min_base_cagr":     min_base_cagr,
        "max_bear_downside": max_bear_down,
        "min_grs":           min_grs,
        "freshness_filter":  freshness_filter,
    }


def render_sidebar_filters() -> dict:
    """Render all sidebar filter widgets and return active filter state dict."""
    st.sidebar.markdown(
        '<p style="font-size:0.68em;text-transform:uppercase;letter-spacing:0.1em;'
        'color:rgba(255,255,255,0.35);font-family:\'DM Mono\',monospace;margin-bottom:4px">Filters</p>',
        unsafe_allow_html=True,
    )

    sectors   = st.sidebar.multiselect("Sector", _SECTORS, default=_SECTORS)
    mcap_cats = st.sidebar.multiselect("Market Cap", _MCAP_CATS, default=["Small", "Mid"])
    min_fvs   = st.sidebar.slider("Min FVS Score", 0, 100, 0, 5)
    ob_trend  = st.sidebar.selectbox("Order Book Trend", _OB_TRENDS)
    exp_signal = st.sidebar.selectbox("Expectation Signal", _EXP_SIGNALS)
    above_dma  = st.sidebar.toggle("Above 200 DMA only", value=False)
    ob_accel   = st.sidebar.toggle("Order book accelerating only", value=False)

    st.sidebar.markdown(
        '<p style="font-size:0.66em;text-transform:uppercase;letter-spacing:0.1em;'
        'color:rgba(255,255,255,0.25);font-family:\'DM Mono\',monospace;margin:14px 0 4px 0">'
        'Valuation</p>', unsafe_allow_html=True,
    )
    min_base_cagr = st.sidebar.slider("Min Base CAGR %", 0, 50, 0, 5)
    max_bear_down = st.sidebar.slider("Max Bear Downside %", -60, 0, -60, 5)

    st.sidebar.markdown(
        '<p style="font-size:0.66em;text-transform:uppercase;letter-spacing:0.1em;'
        'color:rgba(255,255,255,0.25);font-family:\'DM Mono\',monospace;margin:14px 0 4px 0">'
        'Quality</p>', unsafe_allow_html=True,
    )
    min_grs = st.sidebar.slider("Min Guidance Reliability %", 0, 100, 0, 10)
    freshness_filter = st.sidebar.multiselect("Report Freshness", _FRESHNESS, default=[])

    return {
        "sectors":           sectors,
        "mcap_cats":         mcap_cats,
        "min_conviction":    0.0,
        "min_fvs":           min_fvs,
        "ob_trend":          ob_trend,
        "exp_signal":        exp_signal,
        "tech_trend":        "All",
        "above_200dma":      above_dma,
        "ob_accelerating":   ob_accel,
        "min_base_cagr":     min_base_cagr,
        "max_bear_downside": max_bear_down,
        "min_grs":           min_grs,
        "freshness_filter":  freshness_filter,
    }


def market_cap_category(value: Optional[float]) -> str:
    """Categorise market cap into Small / Mid / Large buckets."""
    if value is None:
        return "Unknown"
    if value < 200_000_000_000:
        return "Small"
    if value < 1_000_000_000_000:
        return "Mid"
    return "Large"


def apply_filters(
    df: pd.DataFrame,
    sectors: List[str],
    cap_categories: List[str],
    min_conviction: float,
    ob_trend: str,
    above_200dma: bool,
    min_fvs: float = 0.0,
    tech_trend: str = "All",
    min_base_cagr: float = 0.0,
    max_bear_downside: float = -100.0,
    min_grs: float = 0.0,
    freshness_filter: Optional[List[str]] = None,
    exp_signal: str = "All",
    ob_accelerating: bool = False,
) -> pd.DataFrame:
    """Return a filtered DataFrame for the dashboard view."""
    result = df.copy()
    if sectors:
        result = result[result["sector"].isin(sectors)]
    if cap_categories:
        result = result[result["mcap"].apply(market_cap_category).isin(cap_categories)]
    if min_fvs and min_fvs > 0 and "fvs" in result.columns:
        result = result[result["fvs"] >= min_fvs]
    elif min_conviction and min_conviction > 0:
        result = result[result["convictionScore"] >= min_conviction]
    if ob_trend and ob_trend != "All":
        result = result[result["orderBookTrend"] == ob_trend]
    if ob_accelerating and "orderBookTrend" in result.columns:
        result = result[result["orderBookTrend"] == "ACCELERATING"]
    if exp_signal and exp_signal != "All" and "expectationSignal" in result.columns:
        result = result[result["expectationSignal"] == exp_signal]
    if tech_trend and tech_trend != "All" and "technicalTrend" in result.columns:
        result = result[result["technicalTrend"] == tech_trend]
    if above_200dma:
        result = result[result["above200dma"] == True]  # noqa: E712
    if min_base_cagr > 0 and "baseCagr" in result.columns:
        result = result[result["baseCagr"].apply(lambda x: x >= min_base_cagr if x is not None else True)]
    if max_bear_downside > -100 and "bearDownside" in result.columns:
        result = result[result["bearDownside"].apply(lambda x: x >= max_bear_downside if x is not None else True)]
    if min_grs > 0 and "guidanceReliability" in result.columns:
        result = result[result["guidanceReliability"].apply(lambda x: x >= min_grs if x is not None else True)]
    if freshness_filter and "reportFreshness" in result.columns:
        result = result[result["reportFreshness"].isin(freshness_filter)]
    return result


def add_signal_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 4-band buy/watch/neutral/avoid signal column based on FVS."""
    def _signal(row) -> str:
        fvs = row.get("fvs") if isinstance(row, dict) else getattr(row, "fvs", None)
        if fvs is not None and not (isinstance(fvs, float) and pd.isna(fvs)):
            score = float(fvs)
        else:
            cs = (row.get("convictionScore") if isinstance(row, dict)
                  else getattr(row, "convictionScore", 5))
            score = float(cs or 5) * 10
        if score >= 80:
            return "🟢 Strong Buy"
        if score >= 60:
            return "🟡 Watch"
        if score >= 40:
            return "🟠 Neutral"
        return "🔴 Avoid"

    result = df.copy()
    result["Signal"] = result.apply(_signal, axis=1)
    return result
