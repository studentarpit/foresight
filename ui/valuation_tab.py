"""Valuation Model — 3-scenario projections with Indian number formatting, coloured rows, R/R score."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai.analyzer import build_valuation_model
from ai.cagr_calculator import compute_scenario_cagrs, compute_upside_downside
from ai.risk_reward import compute_risk_reward_score, risk_reward_label
from data.report_repository import load_valuation, save_valuation


# ── Formatting helpers ────────────────────────────────────────────────────────

def _inr_cr(value) -> str:
    """Format a Crore value in Indian numbering: ₹1,23,456 Cr."""
    if value is None or value == "" or value == "—":
        return "—"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if val == 0:
        return "—"
    neg = val < 0
    s = str(int(round(abs(val))))
    if len(s) <= 3:
        result = s
    else:
        result = s[-3:]
        s = s[:-3]
        while len(s) > 2:
            result = s[-2:] + "," + result
            s = s[:-2]
        result = s + "," + result
    return f"₹{'-' if neg else ''}{result} Cr"


def _pct(value) -> str:
    if value is None or value == "—":
        return "—"
    try:
        return f"{float(value):+.1f}%"
    except (TypeError, ValueError):
        return "—"


def _cagr_from_tp(tp, price, years) -> float | None:
    """Compute annualised CAGR from target price."""
    try:
        tp, price, years = float(tp), float(price), int(years)
        if tp > 0 and price > 0 and years > 0:
            return round(((tp / price) ** (1 / years) - 1) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return None


def _upside_from_tp(tp, price) -> float | None:
    try:
        tp, price = float(tp), float(price)
        if price > 0:
            return round((tp / price - 1) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return None


# ── Row colouring ─────────────────────────────────────────────────────────────

_SCENARIO_STYLES = {
    "Bull": "background-color: rgba(0,230,118,0.12); color: #00e676",
    "Base": "background-color: rgba(255,215,64,0.12); color: #ffd740",
    "Bear": "background-color: rgba(255,82,82,0.12);  color: #ff5252",
}


def _colour_rows(row):
    for key, style in _SCENARIO_STYLES.items():
        if key in str(row.get("Scenario", "")):
            return [style] * len(row)
    return [""] * len(row)


# ── Main render ───────────────────────────────────────────────────────────────

def render_valuation_tab(df: pd.DataFrame) -> None:
    st.caption("Build 3-scenario projections without Excel. Models are saved to the Research Repository.")

    if df is None or df.empty:
        st.info("Run AI Scan first to populate the company list.")
        return

    left, right = st.columns([1, 2])

    with left:
        ticker_options = df["ticker"].tolist()
        names = df.set_index("ticker")["name"].to_dict()
        selected = st.selectbox(
            "Select Company",
            ticker_options,
            format_func=lambda t: f"{t} — {names.get(t, t)}",
            key="val_company_select",
        )
        stored_model = load_valuation(selected) if selected else None
        if stored_model:
            st.caption(f"Stored model loaded ({stored_model.get('savedDate', '?')})")

        st.markdown("**Assumptions**")
        rev_growth  = st.number_input("Revenue Growth (%)", 5.0, 100.0, 25.0, step=1.0)
        margin_exp  = st.number_input("Margin Expansion (%)", 0.0, 20.0, 2.0, step=0.5)
        pe_multiple = st.number_input("Exit PE Multiple", 5.0, 100.0, 30.0, step=1.0)
        years       = st.slider("Projection Years", 1, 5, 3)
        generate    = st.button("Generate Model", use_container_width=True)

    if generate and selected:
        company = df[df["ticker"] == selected].iloc[0].to_dict()
        with st.spinner("Building valuation model…"):
            model = build_valuation_model(company, {
                "revenueGrowth": rev_growth / 100,
                "marginExpansion": margin_exp / 100,
                "peMultiple": pe_multiple,
                "years": years,
            })
        price = float(company.get("price") or 0)
        save_valuation(selected, model, years, price)
        st.session_state[f"valuation_{selected}"] = {
            "model": model, "company": company, "years": years,
        }
        st.success("Model generated and saved.")

    cached_key = f"valuation_{selected}" if selected else None
    cached     = st.session_state.get(cached_key) if cached_key else None
    if not cached and stored_model and selected:
        company_row = df[df["ticker"] == selected].iloc[0].to_dict() if not df.empty else {}
        cached = {"model": stored_model, "company": company_row, "years": stored_model.get("years", 3)}

    with right:
        if not cached:
            st.info("Enter assumptions and click **Generate Model**.")
        else:
            _render_model_output(cached["model"], cached["company"], cached["years"])


def _render_model_output(model: dict, company: dict, years: int) -> None:
    price = float(company.get("price") or 0)

    # ── Summary table (one row per scenario) ──────────────────────────────────
    summary_rows = []
    for scenario, icon in [("bull", "🐂 Bull"), ("base", "📊 Base"), ("bear", "🐻 Bear")]:
        s      = model.get(scenario, {})
        rev    = (s.get("revenue") or [0] * years)
        prf    = (s.get("profit")  or [0] * years)
        tp     = float(s.get("targetPrice") or 0)
        cagr   = _cagr_from_tp(tp, price, years)
        upside = _upside_from_tp(tp, price)

        final_rev = rev[-1] if rev else 0
        final_prf = prf[-1] if prf else 0

        summary_rows.append({
            "Scenario":       icon,
            "Final Revenue":  _inr_cr(final_rev),
            "Final PAT":      _inr_cr(final_prf),
            "Target Price":   f"₹{tp:,.0f}" if tp else "—",
            "CAGR %":         _pct(cagr),
            "Upside %":       _pct(upside),
        })

    df_sum = pd.DataFrame(summary_rows)
    styled = df_sum.style.apply(_colour_rows, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Year-by-year detail (collapsible) ─────────────────────────────────────
    with st.expander("Year-by-year projection detail"):
        yr_labels = [f"Year {i + 1}" for i in range(years)]
        detail_rows = []
        for scenario, icon in [("bull", "🐂 Bull"), ("base", "📊 Base"), ("bear", "🐻 Bear")]:
            s       = model.get(scenario, {})
            rev_lst = s.get("revenue", [0] * years)
            prf_lst = s.get("profit",  [0] * years)
            tp      = float(s.get("targetPrice") or 0)
            cagr    = _cagr_from_tp(tp, price, years)
            upside  = _upside_from_tp(tp, price)
            for i in range(min(years, len(rev_lst))):
                is_final = (i == years - 1)
                detail_rows.append({
                    "Scenario":    icon,
                    "Year":        yr_labels[i],
                    "Revenue":     _inr_cr(rev_lst[i]),
                    "PAT":         _inr_cr(prf_lst[i]),
                    "Target Price": f"₹{tp:,.0f}" if (tp and is_final) else "—",
                    "CAGR %":      _pct(cagr)   if is_final else "—",
                    "Upside %":    _pct(upside)  if is_final else "—",
                })
        df_det = pd.DataFrame(detail_rows)
        st.dataframe(
            df_det.style.apply(_colour_rows, axis=1),
            use_container_width=True, hide_index=True,
        )

    # ── R/R score panel ───────────────────────────────────────────────────────
    cagrs    = compute_scenario_cagrs(model, price, years)
    ups      = compute_upside_downside(model, price)
    rr_score = compute_risk_reward_score(cagrs.get("bull"), cagrs.get("base"), cagrs.get("bear"))
    rr_lbl, rr_col = risk_reward_label(rr_score)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Base CAGR",    f"{cagrs.get('base') or 0:.0f}%")
    r2.metric("Bear Downside", f"{ups.get('bearDownside') or 0:+.0f}%")
    r3.metric("Bull Upside",   f"{ups.get('bullUpside') or 0:+.0f}%")
    r4.markdown(
        f'<div style="text-align:center;padding-top:8px">'
        f'<div style="font-size:1.6em;font-weight:800;color:{rr_col};font-family:\'DM Mono\',monospace">'
        f'{rr_score:.0f}</div>'
        f'<div style="font-size:0.78em;color:{rr_col};font-weight:600">R/R: {rr_lbl}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if model.get("valuationCommentary"):
        st.caption(model["valuationCommentary"])

    # ── Target price bar chart ────────────────────────────────────────────────
    scenarios     = ["bull", "base", "bear"]
    target_prices = [float(model.get(s, {}).get("targetPrice") or 0) for s in scenarios]
    fig = go.Figure(go.Bar(
        x=["Bull", "Base", "Bear"],
        y=target_prices,
        marker_color=["#00e676", "#ffd740", "#ff5252"],
        text=[f"₹{tp:,.0f}" for tp in target_prices],
        textposition="outside",
        textfont=dict(color="#f0f0f0"),
    ))
    if price:
        fig.add_hline(
            y=price, line_dash="dot", line_color="rgba(255,255,255,0.4)",
            annotation_text=f"Current ₹{price:,.0f}",
            annotation_font_color="rgba(255,255,255,0.5)",
        )
    fig.update_layout(
        title=dict(text="Target Price by Scenario", font=dict(color="#f0f0f0", size=13)),
        paper_bgcolor="#12121a",
        plot_bgcolor="#12121a",
        yaxis=dict(title="Price (₹)", color="rgba(255,255,255,0.4)",
                   gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(color="rgba(255,255,255,0.6)"),
        height=320,
        margin=dict(t=40, b=20, l=10, r=10),
        font=dict(family="DM Sans", color="#f0f0f0"),
    )
    st.plotly_chart(fig, use_container_width=True)
