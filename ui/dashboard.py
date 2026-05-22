"""Tab 1 — Discover: metric strip, alert banner, ranked table, inline deep dive."""

import pandas as pd
import streamlit as st

from ai.analyzer import analyze_company
from ai.cagr_calculator import compute_upside_downside
from ai.expectations import compute_guidance_reliability
from ai.fvs import fvs_band, fvs_emoji
from ai.risk_reward import compute_risk_reward_score
from data.guidance_history import load_ticker
from data.report_repository import get_freshness, load_valuation
from ui.company_card import render_company_deep_dive
from ui.filters import add_signal_column, apply_filters, render_horizontal_filters

_TECH_ICONS = {
    "STRONG_UPTREND": "🚀", "UPTREND": "📈", "MIXED": "↔️",
    "WEAK": "📉", "DOWNTREND": "🔻", "UNKNOWN": "—",
}
_EXP_ICONS = {"BEAT": "✅", "MISS": "❌", "MIXED": "🔶", "UNKNOWN": "—"}

_COL_HELP = {
    "FVS":       "Future Visibility Score (0-100): AI composite of 16 growth signals. ≥80 = Strong Buy, 60-79 = Watch.",
    "OB/Rev":    "Order Book to Revenue ratio — multiples of annual revenue locked in as future work.",
    "Exp":       "Expectation Signal: whether the last reported quarter BEAT, MISSED, or was MIXED vs management guidance.",
    "GRS %":     "Guidance Reliability Score: % of past quarters where management met its own guidance targets.",
    "Base CAGR": "Expected annualised return under the base-case scenario from your stored Valuation Model.",
    "Bear ↓":    "Downside in the bear-case scenario from your stored Valuation Model.",
    "R/R":       "Risk-Reward Score (0-100): upside potential weighted against downside risk from Valuation Model.",
    "Tech":      "Technical trend: alignment of price vs 20/50/100/200-day moving averages.",
    "Conviction":"AI Conviction Score (0-10): overall quality of the investment case across all signals.",
    "200DMA":    "Whether the current price is above or below the 200-day moving average.",
    "OB Trend":  "Order book trajectory: whether new order inflows are accelerating, stable, or declining.",
}


def _fmt_mcap(v):
    if v is None or pd.isna(v):
        return "N/A"
    return f"₹{v / 1e7:,.0f} Cr"


def _enrich_with_repo_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    g_rel, base_cagrs, bear_downs, rr_scores, freshnesses = [], [], [], [], []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        price  = float(row.get("price") or 0)

        history = load_ticker(ticker)
        gr = round(compute_guidance_reliability(history), 0) if history else None
        g_rel.append(gr)

        model = load_valuation(ticker)
        if model and price > 0:
            years    = int(model.get("years") or 3)
            ups      = compute_upside_downside(model, price)
            base_tp  = float((model.get("base") or {}).get("targetPrice") or 0)
            base_cagr = round(((base_tp / price) ** (1 / years) - 1) * 100, 1) if base_tp > 0 else None
            bear_down = ups.get("bearDownside")
            if base_tp > 0:
                bull_tp   = float((model.get("bull") or {}).get("targetPrice") or 0)
                bear_tp   = float((model.get("bear") or {}).get("targetPrice") or 0)
                bear_cagr = round(((bear_tp / price) ** (1 / years) - 1) * 100, 1) if bear_tp > 0 else None
                bull_cagr = round(((bull_tp / price) ** (1 / years) - 1) * 100, 1) if bull_tp > 0 else None
                rr = compute_risk_reward_score(bull_cagr, base_cagr, bear_cagr)
            else:
                bear_cagr = None
                rr = None
        else:
            base_cagr = bear_down = rr = None

        base_cagrs.append(base_cagr)
        bear_downs.append(bear_down)
        rr_scores.append(rr)
        freshnesses.append(get_freshness(ticker))

    df["guidanceReliability"] = g_rel
    df["baseCagr"]            = base_cagrs
    df["bearDownside"]        = bear_downs
    df["rrScore"]             = rr_scores
    df["reportFreshness"]     = freshnesses
    return df


def _metric_card(label: str, value: str, sub: str, color_cls: str) -> str:
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value {color_cls}">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>'
    )


def _render_metric_strip(df_all: pd.DataFrame, df_filtered: pd.DataFrame) -> None:
    fvs_s    = df_filtered.get("fvs", pd.Series(dtype=float)) if not df_filtered.empty else pd.Series(dtype=float)
    n_strong = int((fvs_s >= 80).sum())
    avg_fvs  = fvs_s.mean() if not df_filtered.empty else None
    avg_conv = f"{avg_fvs / 10:.1f} / 10" if avg_fvs is not None else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_metric_card("Universe Scanned",  str(len(df_all)),      "companies",       "mv-white"),  unsafe_allow_html=True)
    c2.markdown(_metric_card("Passed Filter",     str(len(df_filtered)), "companies",       "mv-white"),  unsafe_allow_html=True)
    c3.markdown(_metric_card("Strong Buys",       str(n_strong),         "FVS ≥ 80",        "mv-green"),  unsafe_allow_html=True)
    c4.markdown(_metric_card("Avg Conviction",    avg_conv,              "across filtered", "mv-yellow"), unsafe_allow_html=True)


def _render_alert_banner(alerts: list) -> None:
    if not alerts:
        return
    high = [a for a in alerts if a["priority"] == 1]
    with st.expander(f"🔔  **{len(alerts)} Alerts** — {len(high)} high priority", expanded=bool(high)):
        for a in alerts[:30]:
            cls = "alert-high" if a["priority"] == 1 else "alert-med"
            dot = "🔴" if a["priority"] == 1 else "🟡"
            st.markdown(
                f'<div class="alert-row {cls}">'
                f'<span>{dot}</span>'
                f'<span style="font-weight:600;font-family:\'DM Mono\',monospace;min-width:84px">{a["ticker"]}</span>'
                f'<span style="color:rgba(255,255,255,0.72)">{a["icon"]} {a["message"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_how_it_works() -> None:
    is_first = not st.session_state.get("_hiw_seen", False)
    with st.expander("ℹ️ How it works", expanded=is_first):
        st.session_state["_hiw_seen"] = True
        c1, c2, c3, c4 = st.columns(4)
        steps = [
            ("01", "Scans 20 curated stocks",
             "Pulls live financials, NSE filings, concall transcripts, and order book announcements"),
            ("02", "Filters weak companies",
             "ROE > 12% · Rev CAGR > 15% · Debt/Equity < 1.0 · MCap > ₹500 Cr"),
            ("03", "Ranks by future visibility",
             "16-signal FVS engine scores each company 0–100 using AI analysis"),
            ("04", "You pick conviction bets",
             "Deep-dive into bull/base/bear, order book momentum, and guidance reliability"),
        ]
        for col, (num, title, desc) in zip([c1, c2, c3, c4], steps):
            col.markdown(
                f'<div style="padding:14px 12px;background:rgba(255,255,255,0.03);'
                f'border-radius:8px;border:1px solid rgba(255,255,255,0.06);height:100%">'
                f'<div style="font-family:\'DM Serif Display\',serif;font-size:1.7em;font-weight:400;'
                f'color:#00e676;line-height:1;margin-bottom:8px">{num}</div>'
                f'<div style="font-weight:600;font-size:0.9em;margin-bottom:4px">{title}</div>'
                f'<div style="font-size:0.78em;color:rgba(255,255,255,0.45);line-height:1.5">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_hero_scan_cta() -> None:
    """Shown when displaying demo/sample data — prompts user to run a real scan."""
    st.markdown(
        '<div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.2);'
        'border-radius:10px;padding:14px 20px;margin-bottom:18px;'
        'display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">'
        '<div>'
        '<div style="font-weight:600;font-size:0.92em">Showing sample data</div>'
        '<div style="font-size:0.78em;color:rgba(255,255,255,0.45);margin-top:2px">'
        'Click <strong style="color:#00e676">⚡ Run AI Scan</strong> in the header '
        'to fetch live results for real companies — takes ~60 seconds</div>'
        '</div>'
        '<div style="font-size:0.75em;font-family:\'DM Mono\',monospace;'
        'color:rgba(0,230,118,0.6);white-space:nowrap">DEMO DATA</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_no_results_state() -> None:
    """Empty state when filters exclude all companies."""
    st.markdown(
        '<div style="text-align:center;padding:60px 20px">'
        '<div style="font-size:3em;margin-bottom:14px">🔭</div>'
        '<div style="font-family:\'DM Serif Display\',serif;font-size:1.5em;margin-bottom:8px">'
        'Discover Your Next Compounder</div>'
        '<div style="font-size:0.88em;color:rgba(255,255,255,0.4);max-width:440px;'
        'margin:0 auto 20px;line-height:1.6">'
        'No companies match your current filters. Try widening the sector or market cap selection, '
        'or lower the minimum FVS score to see more results.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_market_radar(filters: dict = None) -> None:
    """Backward-compat alias."""
    return render_discover_tab()


def render_discover_tab() -> None:
    _render_how_it_works()

    # Horizontal filter bar — renders above alerts, returns filter dict
    st.markdown('<div class="section-lbl">FILTERS</div>', unsafe_allow_html=True)
    filters = render_horizontal_filters()
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0 14px'>", unsafe_allow_html=True)

    df = st.session_state.get("scan_results")
    is_demo = st.session_state.get("demo_mode") or st.session_state.get("_auto_demo_done")

    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        st.markdown(
            '<div style="text-align:center;padding:72px 20px;color:rgba(255,255,255,0.25)">'
            '<div style="font-size:3.2em;margin-bottom:14px">📡</div>'
            '<div style="font-family:\'DM Serif Display\',serif;font-size:1.5em;'
            'margin-bottom:8px;color:rgba(255,255,255,0.5)">Discover Your Next Compounder</div>'
            '<div style="font-size:0.88em;max-width:420px;margin:0 auto 24px;line-height:1.6">'
            'Foresight scans 20 curated Indian equities, filters by financial quality, '
            'and ranks them by AI-computed Future Visibility Score.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    if is_demo:
        _render_hero_scan_cta()

    df = _enrich_with_repo_data(df)
    _render_alert_banner(st.session_state.get("alerts", []))

    filtered = apply_filters(
        df,
        sectors=filters.get("sectors", []),
        cap_categories=filters.get("mcap_cats", []),
        min_conviction=filters.get("min_conviction", 0.0),
        ob_trend=filters.get("ob_trend", "All"),
        above_200dma=filters.get("above_200dma", False),
        min_fvs=filters.get("min_fvs", 0.0),
        tech_trend=filters.get("tech_trend", "All"),
        min_base_cagr=filters.get("min_base_cagr", 0.0),
        max_bear_downside=filters.get("max_bear_downside", -100.0),
        min_grs=filters.get("min_grs", 0.0),
        freshness_filter=filters.get("freshness_filter") or None,
        exp_signal=filters.get("exp_signal", "All"),
        ob_accelerating=filters.get("ob_accelerating", False),
    )
    filtered = add_signal_column(filtered)
    sort_col = "fvs" if "fvs" in filtered.columns else "convictionScore"
    filtered = filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)

    _render_metric_strip(df, filtered)

    if filtered.empty:
        _render_no_results_state()
        return

    # ── Ranked company table ───────────────────────────────────────────────────
    st.markdown('<div class="section-lbl">RANKED COMPANIES</div>', unsafe_allow_html=True)

    disp = filtered.copy()
    disp.insert(0, "Rank", range(1, len(disp) + 1))
    disp["MCap"]     = disp["mcap"].map(_fmt_mcap)
    disp["ROE"]      = disp["roe"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "—")
    disp["Rev CAGR"] = disp["revcagr"].map(lambda v: f"{v:.1f}%" if pd.notna(v) else "—")
    disp["OB Trend"] = disp["orderBookTrend"].map(
        lambda t: {"ACCELERATING": "📈", "DECLINING": "📉"}.get(t, "➡️") + " " + str(t)
    )
    disp["200DMA"] = disp["above200dma"].map({True: "🟢 Above", False: "🔴 Below"})
    if "fvs" in disp.columns:
        disp["FVS"] = disp["fvs"].map(
            lambda v: f"{fvs_emoji(float(v))} {float(v):.0f}" if pd.notna(v) else "—"
        )
    if "convictionScore" in disp.columns:
        disp["Conviction"] = disp["convictionScore"].map(
            lambda v: f"{float(v):.1f}" if pd.notna(v) else "—"
        )
    if "technicalTrend" in disp.columns:
        disp["Tech"] = disp["technicalTrend"].map(
            lambda t: f"{_TECH_ICONS.get(t, '—')} {str(t).replace('_', ' ').title()}"
        )
    if "expectationSignal" in disp.columns:
        disp["Exp"] = disp["expectationSignal"].map(
            lambda s: f"{_EXP_ICONS.get(s, '—')} {s}"
        )
    if "guidanceReliability" in disp.columns:
        disp["GRS %"] = disp["guidanceReliability"].map(
            lambda v: f"{v:.0f}%" if v is not None else "—"
        )
    if "baseCagr" in disp.columns:
        disp["Base CAGR"] = disp["baseCagr"].map(
            lambda v: f"{v:+.0f}%" if v is not None else "—"
        )
    if "bearDownside" in disp.columns:
        disp["Bear ↓"] = disp["bearDownside"].map(
            lambda v: f"{v:+.0f}%" if v is not None else "—"
        )
    if "rrScore" in disp.columns:
        disp["R/R"] = disp["rrScore"].map(
            lambda v: f"{v:.0f}" if v is not None else "—"
        )

    col_order = [
        "Rank", "ticker", "name", "sector", "MCap", "ROE", "Rev CAGR",
        "orderBookRev", "OB Trend", "200DMA", "FVS", "Conviction",
        "Exp", "GRS %", "Base CAGR", "Bear ↓", "R/R", "Signal",
    ]
    present = [c for c in col_order if c in disp.columns]
    disp = disp[present].rename(columns={
        "ticker": "Ticker", "name": "Company", "sector": "Sector",
        "orderBookRev": "OB/Rev",
    })

    # Build column_config with tooltips for key columns
    col_cfg = {
        col: st.column_config.TextColumn(col, help=_COL_HELP[col])
        for col in _COL_HELP if col in disp.columns
    }

    st.dataframe(disp, use_container_width=True, hide_index=True, height=400, column_config=col_cfg)
    st.caption(
        "**FVS:** 🟢≥80 Strong Buy · 🟡60-79 Watch · 🟠40-59 Neutral · 🔴<40 Avoid  |  "
        "**Exp:** ✅ Beat · ❌ Miss · 🔶 Mixed  |  "
        "**GRS** = Guidance Reliability Score  |  **R/R** = Risk-Reward (0-100)  |  "
        "Hover column headers for definitions"
    )

    # ── Inline company deep dive ───────────────────────────────────────────────
    st.markdown('<div class="section-lbl">COMPANY DEEP DIVE</div>', unsafe_allow_html=True)

    selected = st.selectbox(
        "company_selector",
        options=filtered["ticker"].tolist(),
        format_func=lambda t: (
            f"{t}  —  {filtered.loc[filtered['ticker'] == t, 'name'].values[0]}"
        ),
        label_visibility="collapsed",
    )

    if selected:
        company_row = filtered[filtered["ticker"] == selected].iloc[0].to_dict()
        cache = st.session_state.setdefault("company_analyses", {})
        if selected not in cache:
            with st.spinner(f"Analysing {selected}…"):
                cache[selected] = analyze_company(company_row)

        st.markdown('<div class="dd-wrap">', unsafe_allow_html=True)
        render_company_deep_dive(company_row, cache[selected])
        st.markdown('</div>', unsafe_allow_html=True)
