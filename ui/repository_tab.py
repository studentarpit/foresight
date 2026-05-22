"""Tab 7 — Research Repository.

Section 13 of research spec — pre-generated company research reports browser.
Users can generate full AI reports, store them, and browse with freshness tracking.
"""

import pandas as pd
import streamlit as st

from ai.analyzer import analyze_company, generate_full_report
from data.order_history import load_ticker_orders, total_order_value
from data.report_repository import (
    get_freshness,
    list_all_reports,
    list_all_valuations,
    load_report,
    load_valuation,
    save_report,
)
from universe.stocks import STOCK_UNIVERSE, get_stock_meta

_FRESHNESS_COLORS = {
    "Fresh":         "#28a745",
    "Needs Refresh": "#fd7e14",
    "Stale":         "#dc3545",
    "No Report":     "#6c757d",
}
_FRESHNESS_ICONS = {
    "Fresh":         "🟢",
    "Needs Refresh": "🟡",
    "Stale":         "🔴",
    "No Report":     "—",
}


def render_repository_tab() -> None:
    st.markdown("### Research Repository")
    st.caption(
        "Pre-generated AI research reports for all tracked companies. "
        "Reports are stored locally and refresh automatically on demand. "
        "**Fresh** = generated within 7 days · **Needs Refresh** = 8-30 days · **Stale** = >30 days."
    )

    _render_repository_index()
    st.markdown("---")
    _render_report_generator()
    st.markdown("---")
    _render_report_viewer()


# ── Repository index table ────────────────────────────────────────────────────

def _render_repository_index() -> None:
    st.markdown("#### Repository Status")
    all_tickers = [s["ticker"] for s in STOCK_UNIVERSE]
    rows = []
    freshness_counts = {"Fresh": 0, "Needs Refresh": 0, "Stale": 0, "No Report": 0}
    for ticker in all_tickers:
        freshness = get_freshness(ticker)
        freshness_counts[freshness] += 1
        report = load_report(ticker)
        val_model = load_valuation(ticker)
        meta = get_stock_meta(ticker)
        rows.append({
            "Ticker":       ticker,
            "Company":      meta.get("name", ticker),
            "Sector":       meta.get("sector", "—"),
            "Report":       _FRESHNESS_ICONS.get(freshness, "—") + " " + freshness,
            "Generated":    report.get("generatedDate", "—") if report else "—",
            "Valuation":    "✅" if val_model else "—",
            "Base CAGR %":  f"{(val_model.get('base',{}).get('cagr') or 0):.0f}%" if val_model else "—",
            "AI View":      (report.get("aiView", "")[:100] + "…") if report and len(report.get("aiView","")) > 100 else (report.get("aiView","") if report else "—"),
        })

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fresh Reports",    freshness_counts["Fresh"])
    c2.metric("Needs Refresh",    freshness_counts["Needs Refresh"])
    c3.metric("Stale / Missing",  freshness_counts["Stale"] + freshness_counts["No Report"])
    c4.metric("With Valuation",   sum(1 for r in rows if r["Valuation"] == "✅"))

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── Report generator panel ────────────────────────────────────────────────────

def _render_report_generator() -> None:
    st.markdown("#### Generate / Refresh Reports")
    scan_df = st.session_state.get("scan_results")
    scan_tickers = list(scan_df["ticker"]) if scan_df is not None and not scan_df.empty else []
    all_t = [s["ticker"] for s in STOCK_UNIVERSE]

    col_sel, col_btn1, col_btn2 = st.columns([3, 1, 1])
    gen_ticker = col_sel.selectbox(
        "Company",
        all_t,
        format_func=lambda t: f"{t} — {get_stock_meta(t).get('name', t)}",
        key="repo_gen_ticker",
    )

    if col_btn1.button("Generate Report", use_container_width=True, key="gen_one"):
        _generate_and_save(gen_ticker, scan_df)

    gen_all = col_btn2.button("Generate All Scanned", use_container_width=True, key="gen_all")
    if gen_all:
        if not scan_tickers:
            st.warning("Run an AI Scan first to populate the company list.")
        else:
            prog = st.progress(0)
            for i, t in enumerate(scan_tickers):
                _generate_and_save(t, scan_df, silent=True)
                prog.progress(int((i + 1) / len(scan_tickers) * 100))
            st.success(f"Generated reports for {len(scan_tickers)} companies.")
            st.rerun()


def _generate_and_save(ticker: str, scan_df, silent: bool = False) -> None:
    """Generate full report for one ticker and persist it."""
    meta = get_stock_meta(ticker)
    name = meta.get("name", ticker)
    with st.spinner(f"Generating report for {name}…"):
        # Build company dict
        company_row = {}
        if scan_df is not None and not scan_df.empty:
            row = scan_df[scan_df["ticker"] == ticker]
            if not row.empty:
                company_row = row.iloc[0].to_dict()
        if not company_row:
            company_row = {"ticker": ticker, "name": name, "sector": meta.get("sector", "—")}
        # Order summary
        orders = load_ticker_orders(ticker)
        if orders:
            total = total_order_value(ticker)
            order_summary = f"{len(orders)} orders tracked; cumulative value ₹{total:,.0f} Cr. " if total else f"{len(orders)} orders tracked. "
            latest = orders[:3]
            order_summary += " | ".join(o.get("description", "")[:80] for o in latest)
        else:
            order_summary = ""
        concall_text = company_row.get("concallText", "")
        report = generate_full_report(company_row, order_summary, concall_text)
        save_report(ticker, report)
    if not silent:
        st.success(f"Report generated for {name}.")
        st.rerun()


# ── Report viewer ─────────────────────────────────────────────────────────────

def _render_report_viewer() -> None:
    st.markdown("#### View Stored Report")
    stored = [r["ticker"] for r in list_all_reports()]
    if not stored:
        st.info("No reports generated yet. Use the panel above to generate a report.")
        return

    selected = st.selectbox(
        "Select company",
        stored,
        format_func=lambda t: f"{t} — {get_stock_meta(t).get('name', t)}",
        key="repo_view_ticker",
    )
    if not selected:
        return

    report = load_report(selected)
    if not report:
        return

    freshness = get_freshness(selected)
    color = _FRESHNESS_COLORS.get(freshness, "#6c757d")
    st.markdown(
        f'<span style="background:{color};color:#fff;padding:3px 10px;border-radius:12px;'
        f'font-size:0.8em;font-weight:600">{_FRESHNESS_ICONS.get(freshness,"")} {freshness}</span>'
        f'&nbsp;&nbsp;<span style="color:#888;font-size:0.85em">Generated: {report.get("generatedDate","—")}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    # AI View — highlighted block
    ai_view = report.get("aiView", "")
    if ai_view:
        st.markdown(
            f'<div style="border-left:4px solid #28a745;padding:12px 16px;background:#f0fff4;'
            f'border-radius:4px;margin-bottom:12px"><strong>AI View</strong><br>{ai_view}</div>',
            unsafe_allow_html=True,
        )

    tab_ov, tab_order, tab_fin, tab_risk, tab_val = st.tabs([
        "Overview", "Order Wins", "Financials", "Risks", "Valuation"
    ])

    with tab_ov:
        st.markdown("**Company Overview**")
        st.write(report.get("companyOverview", "—"))
        st.markdown("**Business Model**")
        st.write(report.get("businessModel", "—"))
        st.markdown("**Sector Opportunity**")
        st.write(report.get("sectorOpportunity", "—"))
        st.markdown("**Recent Developments**")
        st.write(report.get("recentDevelopments", "—"))
        segs = report.get("revenueSegments", [])
        if segs:
            st.markdown("**Revenue Segments:** " + " · ".join(segs))

    with tab_order:
        st.markdown("**Order Wins Analysis**")
        st.write(report.get("orderWinsAnalysis", "—"))
        orders = load_ticker_orders(selected)
        if orders:
            st.markdown(f"**Saved Orders:** {len(orders)}")

    with tab_fin:
        st.markdown("**Financial Summary**")
        st.write(report.get("financialSummary", "—"))
        st.markdown("**Margin Trend:** " + report.get("marginTrend", "—").title())
        st.markdown("**Management Quality**")
        st.write(report.get("managementQuality", "—"))

        bc, mc, br = st.columns(3)
        with bc:
            st.markdown("#### 🟢 Bull Case")
            st.write(report.get("bullCase", "—"))
        with mc:
            st.markdown("#### 🟡 Base Case")
            st.write(report.get("baseCase", "—"))
        with br:
            st.markdown("#### 🔴 Bear Case")
            st.write(report.get("bearCase", "—"))

    with tab_risk:
        st.markdown("**Key Risks**")
        for r in report.get("risks", []):
            st.markdown(f"- {r}")
        st.markdown("**Growth Triggers**")
        for t in report.get("growthTriggers", []):
            st.markdown(f"- {t}")

    with tab_val:
        val_model = load_valuation(selected)
        if val_model:
            _render_stored_valuation(val_model, report)
        else:
            base_cagr = report.get("expectedBaseCagr")
            rr = report.get("riskRewardAssessment", "")
            if base_cagr:
                st.metric("AI Estimated Base CAGR", f"{base_cagr:.0f}%")
            if rr:
                st.caption(rr)
            st.info("Generate a Valuation Model in the Valuation tab to see full scenario analysis here.")


def _render_stored_valuation(model: dict, report: dict) -> None:
    """Render stored valuation model summary inside the repository viewer."""
    price = float(model.get("currentPrice") or 0)
    years = int(model.get("years") or 3)
    cols = st.columns(3)
    for col, (label, key, color) in zip(cols, [
        ("🟢 Bull", "bull", "#28a745"),
        ("🟡 Base", "base", "#ffc107"),
        ("🔴 Bear", "bear", "#dc3545"),
    ]):
        s = model.get(key, {})
        tp = float(s.get("targetPrice") or 0)
        cagr = float(s.get("cagr") or 0)
        upside = round(((tp / price) - 1) * 100, 1) if price and tp else None
        col.markdown(
            f'<div style="border:1px solid {color};padding:10px;border-radius:8px;text-align:center">'
            f'<div style="font-size:1.3em;font-weight:700;color:{color}">₹{tp:,.0f}</div>'
            f'<div style="font-size:0.85em">Target ({label})</div>'
            f'<div style="font-weight:600">{cagr:+.0f}% CAGR</div>'
            f'{"<div style=\\'font-size:0.8em\\'>" + (f"{upside:+.0f}% upside" if upside else "") + "</div>" if upside else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )
    rr = report.get("riskRewardAssessment", "")
    if rr:
        st.caption(rr)
