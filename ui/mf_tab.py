"""Tab 4 — Mutual Fund Screener: filter, rank, and AI-score Indian equity funds."""

import pandas as pd
import plotly.express as px
import streamlit as st

from ai.analyzer import analyze_mf


def render_mf_tab(mf_df: pd.DataFrame) -> None:
    """Render the MF Screener tab with filters, table, and per-fund AI analysis."""
    st.markdown("### 🏦 Mutual Fund Screener")
    st.caption("Discover Indian equity funds with institutional-quality long-term consistency.")

    if mf_df is None or mf_df.empty:
        st.info("Click **Load MF Data** in the sidebar (or wait for the first load).")
        return

    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("**MF Screener Filters**")
    categories = sorted(mf_df["category"].dropna().unique().tolist()) if "category" in mf_df.columns else []
    sel_cats = st.sidebar.multiselect("Fund Category", categories, default=categories)
    min_10yr = st.sidebar.slider("Min 10yr Return (%)", 0.0, 30.0, 8.0)
    max_dd = st.sidebar.slider("Max Drawdown (%)", 0.0, 60.0, 40.0)
    min_cons = st.sidebar.slider("Min Consistency Score", 0.0, 10.0, 5.0)

    filtered = mf_df.copy()
    if sel_cats:
        filtered = filtered[filtered["category"].isin(sel_cats)]
    if "return10yr" in filtered.columns:
        filtered = filtered[filtered["return10yr"].fillna(0) >= min_10yr]
    if "maxDrawdown" in filtered.columns:
        filtered = filtered[filtered["maxDrawdown"].fillna(100) <= max_dd]
    if "consistencyScore" in filtered.columns:
        filtered = filtered[filtered["consistencyScore"].fillna(0) >= min_cons]

    if filtered.empty:
        st.warning("No funds match the current filters.")
        return

    # Main table
    disp_cols = ["name", "category", "return1yr", "return3yr", "return5yr",
                 "return10yr", "maxDrawdown", "consistencyScore"]
    present = [c for c in disp_cols if c in filtered.columns]
    disp = filtered[present].rename(columns={
        "name": "Fund Name", "category": "Category",
        "return1yr": "1yr %", "return3yr": "3yr %",
        "return5yr": "5yr %", "return10yr": "10yr %",
        "maxDrawdown": "Max DD %", "consistencyScore": "Consistency",
    }).reset_index(drop=True)
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Per-fund deep dive
    fund_names = filtered["name"].tolist()
    selected_fund = st.selectbox("Select fund for AI analysis", fund_names)
    if not selected_fund:
        return

    fund_row = filtered[filtered["name"] == selected_fund].iloc[0].to_dict()
    cache_key = f"mf_{selected_fund}"
    mf_cache = st.session_state.setdefault("mf_analyses", {})
    if cache_key not in mf_cache:
        with st.spinner(f"Analysing {selected_fund}…"):
            mf_cache[cache_key] = analyze_mf(fund_row)

    analysis = mf_cache[cache_key]
    rec = analysis.get("recommendation", "MODERATE")
    badge = {"STRONG": "🟢 STRONG", "MODERATE": "🟡 MODERATE", "AVOID": "🔴 AVOID"}.get(rec, rec)

    c1, c2, c3 = st.columns(3)
    c1.metric("Recommendation", badge)
    c2.metric("Consistency Score", f"{analysis.get('consistencyScore', 0):.1f} / 10")
    c3.metric("Drawdown Risk", f"{analysis.get('drawdownRisk', 0):.1f} / 10")
    st.markdown(f"**AI Reasoning:** {analysis.get('reasoning', '—')}")

    # Return bar chart
    return_cols = {"1yr %": "return1yr", "3yr %": "return3yr", "5yr %": "return5yr", "10yr %": "return10yr"}
    ret_data = {label: float(fund_row.get(col) or 0) for label, col in return_cols.items()}
    fig = px.bar(
        x=list(ret_data.keys()), y=list(ret_data.values()),
        labels={"x": "Period", "y": "Return %"},
        title="Historical Returns",
        color_discrete_sequence=["#007bff"],
    )
    fig.update_layout(height=300, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)
