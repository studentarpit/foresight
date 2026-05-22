"""Tab 5 — Expectation Intelligence Engine.

Tracks guided vs actual quarterly delivery per company and surfaces:
- Per-quarter Expectation Gap (Revenue / Margin / PAT)
- Beat / Miss / Mixed signal with colour coding
- Guidance Reliability Score (rolling %)
- Expectation trend over time (Improving / Deteriorating / Stable)
- Top Beats and Top Misses from the last scan
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai.expectations import (
    company_expectation_score,
    compute_expectation_gap,
    compute_guidance_reliability,
    expectation_trend,
    reliability_label,
)
from data.guidance_history import (
    all_tickers,
    delete_entry,
    load_all,
    load_ticker,
    save_entry,
)

_SIG_COLORS = {"BEAT": "#28a745", "MISS": "#dc3545", "MIXED": "#fd7e14", "UNKNOWN": "#6c757d"}
_SIG_ICONS  = {"BEAT": "✅", "MISS": "❌", "MIXED": "🔶", "UNKNOWN": "—"}


# ── Main render ───────────────────────────────────────────────────────────────

def render_expectation_tab() -> None:
    st.markdown("### Expectation Intelligence Engine")
    st.caption(
        "Track what management guided vs what was actually delivered. "
        "The market reacts to expectation gaps — not just absolute numbers."
    )

    scan_df = st.session_state.get("scan_results")
    _render_scan_summary(scan_df)

    st.markdown("---")

    # Company selector — merge scan tickers + history tickers
    scan_tickers = list(scan_df["ticker"]) if scan_df is not None and not scan_df.empty else []
    hist_tickers = all_tickers()
    all_t = sorted(set(scan_tickers + hist_tickers))

    if not all_t:
        st.info("Run an AI Scan first, or add quarterly data manually below.")
        all_t = ["—"]

    selected = st.selectbox("Select company", all_t if all_t[0] != "—" else ["—"])
    if selected == "—":
        return

    # Company name lookup
    company_name = selected
    if scan_df is not None and not scan_df.empty:
        row = scan_df[scan_df["ticker"] == selected]
        if not row.empty:
            company_name = row.iloc[0].get("name", selected)

    history = load_ticker(selected)

    # ── Metrics row ───────────────────────────────────────────────────────────
    reliability = compute_guidance_reliability(history)
    exp_score   = company_expectation_score(history)
    trend       = expectation_trend(history)
    r_label, r_color = reliability_label(reliability)
    trend_icons = {"IMPROVING": "📈", "DETERIORATING": "📉", "STABLE": "↔️", "INSUFFICIENT_DATA": "—"}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quarters Tracked", len(history))
    c2.metric("Guidance Reliability", f"{reliability:.0f}%", help=r_label)
    c3.metric("Expectation Score", f"{exp_score:.0f} / 100")
    c4.metric("Trend", trend_icons.get(trend, "—") + " " + trend.replace("_", " ").title())

    if history:
        _render_history_table(history, company_name)
        _render_gap_chart(history, company_name)

    st.markdown("---")
    _render_add_quarter_form(selected, company_name)

    if history:
        st.markdown("---")
        _render_delete_form(selected, history)


# ── Scan summary — Top Beats and Misses ──────────────────────────────────────

def _render_scan_summary(scan_df) -> None:
    if scan_df is None or (isinstance(scan_df, pd.DataFrame) and scan_df.empty):
        return
    if "expectationSignal" not in scan_df.columns:
        return

    beats  = scan_df[scan_df["expectationSignal"] == "BEAT"].sort_values("fvs", ascending=False)
    misses = scan_df[scan_df["expectationSignal"] == "MISS"].sort_values("fvs", ascending=False)
    mixed  = scan_df[scan_df["expectationSignal"] == "MIXED"].sort_values("fvs", ascending=False)

    b_col, m_col, x_col = st.columns(3)
    with b_col:
        st.markdown("##### ✅ Top Beats")
        if beats.empty:
            st.caption("No beats in current scan")
        for _, r in beats.head(4).iterrows():
            fvs = float(r.get("fvs") or 0)
            st.markdown(f"**{r['ticker']}** — {r.get('name','')}  `FVS {fvs:.0f}`")
            if r.get("oneLineThesis"):
                st.caption(r["oneLineThesis"])

    with m_col:
        st.markdown("##### ❌ Top Misses")
        if misses.empty:
            st.caption("No misses in current scan")
        for _, r in misses.head(4).iterrows():
            fvs = float(r.get("fvs") or 0)
            st.markdown(f"**{r['ticker']}** — {r.get('name','')}  `FVS {fvs:.0f}`")
            if r.get("oneLineThesis"):
                st.caption(r["oneLineThesis"])

    with x_col:
        st.markdown("##### 🔶 Mixed Results")
        if mixed.empty:
            st.caption("No mixed signals in current scan")
        for _, r in mixed.head(4).iterrows():
            fvs = float(r.get("fvs") or 0)
            st.markdown(f"**{r['ticker']}** — {r.get('name','')}  `FVS {fvs:.0f}`")


# ── History table ─────────────────────────────────────────────────────────────

def _render_history_table(history: list[dict], name: str) -> None:
    st.markdown(f"#### Quarterly Delivery — {name}")
    rows = []
    for entry in history:
        gap = compute_expectation_gap(entry)
        sig = gap["signal"]
        rows.append({
            "Quarter":     entry.get("quarter", "—"),
            "Signal":      f"{_SIG_ICONS[sig]} {sig}",
            "Rev Gap (pp)":  _fmt_gap(gap["revGap"]),
            "Margin Gap (pp)": _fmt_gap(gap["marginGap"]),
            "PAT Gap (pp)": _fmt_gap(gap["patGap"]),
            "Guided Rev%": entry.get("guidedRevGrowth", "—"),
            "Actual Rev%": entry.get("actualRevGrowth", "—"),
            "Guided Mgn%": entry.get("guidedMargin", "—"),
            "Actual Mgn%": entry.get("actualMargin", "—"),
            "Notes":       entry.get("notes", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _fmt_gap(val) -> str:
    if val is None:
        return "—"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.1f}"


# ── Gap chart ─────────────────────────────────────────────────────────────────

def _render_gap_chart(history: list[dict], name: str) -> None:
    quarters, rev_gaps, margin_gaps, pat_gaps = [], [], [], []
    for entry in history:
        gap = compute_expectation_gap(entry)
        quarters.append(entry.get("quarter", "?"))
        rev_gaps.append(gap["revGap"])
        margin_gaps.append(gap["marginGap"])
        pat_gaps.append(gap["patGap"])

    fig = go.Figure()
    if any(v is not None for v in rev_gaps):
        fig.add_trace(go.Bar(name="Revenue Gap", x=quarters,
                             y=[v or 0 for v in rev_gaps],
                             marker_color=["#28a745" if (v or 0) > 0 else "#dc3545"
                                           for v in rev_gaps]))
    if any(v is not None for v in margin_gaps):
        fig.add_trace(go.Scatter(name="Margin Gap", x=quarters,
                                 y=[v or 0 for v in margin_gaps],
                                 mode="lines+markers", line=dict(color="#fd7e14", width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color="grey", line_width=1)
    fig.update_layout(
        title=f"{name} — Expectation Gaps by Quarter",
        xaxis_title="Quarter", yaxis_title="Gap (pp)",
        barmode="group", height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Add quarter form ──────────────────────────────────────────────────────────

def _render_add_quarter_form(ticker: str, name: str) -> None:
    with st.expander(f"+ Add / Update Quarterly Data for {name}", expanded=False):
        with st.form(f"add_q_{ticker}"):
            quarter = st.text_input("Quarter (e.g. Q4FY25)", placeholder="Q4FY25")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Revenue Growth %**")
                guided_rev = st.number_input("Guided Rev Growth", value=0.0, step=0.5,
                                             key=f"gr_{ticker}", format="%.1f")
                actual_rev = st.number_input("Actual Rev Growth", value=0.0, step=0.5,
                                             key=f"ar_{ticker}", format="%.1f")
            with c2:
                st.markdown("**EBITDA / PAT Margin %**")
                guided_m = st.number_input("Guided Margin", value=0.0, step=0.1,
                                           key=f"gm_{ticker}", format="%.1f")
                actual_m = st.number_input("Actual Margin", value=0.0, step=0.1,
                                           key=f"am_{ticker}", format="%.1f")
            c3, c4 = st.columns(2)
            with c3:
                guided_pat = st.number_input("Guided PAT Growth %", value=0.0, step=0.5,
                                             key=f"gp_{ticker}", format="%.1f")
            with c4:
                actual_pat = st.number_input("Actual PAT Growth %", value=0.0, step=0.5,
                                             key=f"ap_{ticker}", format="%.1f")
            notes = st.text_input("Notes (optional)")
            submitted = st.form_submit_button("Save Quarter")

        if submitted:
            if not quarter.strip():
                st.error("Quarter field is required (e.g. Q4FY25)")
            else:
                entry = {
                    "quarter": quarter.strip(),
                    "guidedRevGrowth": guided_rev,  "actualRevGrowth": actual_rev,
                    "guidedMargin": guided_m,        "actualMargin": actual_m,
                    "guidedPATGrowth": guided_pat,   "actualPATGrowth": actual_pat,
                    "notes": notes,
                }
                save_entry(ticker, entry)
                gap = compute_expectation_gap(entry)
                st.success(f"Saved {quarter} — Signal: {_SIG_ICONS[gap['signal']]} {gap['signal']}. "
                           f"{gap['summary']}")
                st.rerun()


# ── Delete form ───────────────────────────────────────────────────────────────

def _render_delete_form(ticker: str, history: list[dict]) -> None:
    quarters = [e.get("quarter", "?") for e in history]
    with st.expander("Remove a quarter entry", expanded=False):
        to_delete = st.selectbox("Quarter to remove", quarters, key=f"del_{ticker}")
        if st.button("Delete", key=f"delbtn_{ticker}"):
            if delete_entry(ticker, to_delete):
                st.success(f"Removed {to_delete}")
                st.rerun()
