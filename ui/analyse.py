"""Tab 2 — Analyse: company header, 6-chart grid, scenario analysis,
management credibility, peer comparison, risk register, Section 8 financial health,
Section 9 valuation model with user assumptions.
"""

import pandas as pd
import streamlit as st

from ai.analyzer import analyze_company, build_valuation_model
from ai.fvs import fvs_band, fvs_emoji
from ai.heat_engine import compute_heat_score, heat_level
from data.quarterly_fetcher import fetch_quarterly_data
from data.fii_dii_engine import compute_flow_score, flow_score_label
from ui.charts import (
    chart_card,
    chart_conviction_scorecard,
    chart_key_financials,
    chart_margin_profile,
    chart_operating_margin_trend,
    chart_order_backlog,
    chart_order_inflow_vs_execution,
    chart_revenue_cagr,
    chart_revenue_profit_qoq,
    chart_revenue_quality_heatmap,
    chart_shareholding_pattern,
)


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    return "128,128,128"


# ── Section helpers ────────────────────────────────────────────────────────────

def _render_company_header(row: dict, analysis: dict) -> None:
    """Section 1 — Company header bar."""
    name   = row.get("name", row.get("ticker", ""))
    ticker = row.get("ticker", "")
    sector = row.get("sector", "")
    cap    = row.get("capClass", "")
    price  = row.get("price")
    fvs    = float(analysis.get("fvsRefined") or row.get("fvs") or 0)
    signal = row.get("Signal", "🟠 Neutral")

    _, fvs_color = fvs_band(fvs)
    fvs_hex = {"green": "#00e676", "yellow": "#ffd740",
               "orange": "#ff9800", "red": "#ff5252"}.get(fvs_color, "#f0f0f0")
    price_str = f"₹{price:,.2f}" if price else "—"

    try:
        _fs_score          = compute_flow_score(ticker)
        _fs_label, _fs_clr = flow_score_label(_fs_score)
        _fs_color_hex = {"green": "#00e676", "grey": "rgba(255,255,255,0.35)",
                         "yellow": "#ffd740", "red": "#ff5252"}.get(_fs_clr, "rgba(255,255,255,0.35)")
        flow_badge = (f'<span style="color:{_fs_color_hex};font-size:0.88em;'
                      f'font-family:\'DM Mono\',monospace">⚡ Flow {_fs_label}</span>')
    except Exception:
        flow_badge = ""

    st.markdown(
        f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.09);'
        f'border-radius:10px;padding:18px 22px;margin-bottom:16px">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;'
        f'flex-wrap:wrap;gap:12px">'
        f'<div>'
        f'<div style="font-family:\'DM Serif Display\',serif;font-size:1.7em;color:#f0f0f0">'
        f'{name}</div>'
        f'<div style="font-size:0.8em;color:rgba(255,255,255,0.4);margin-top:4px;'
        f'font-family:\'DM Mono\',monospace">{ticker} · {sector} · {cap} Cap</div>'
        f'</div>'
        f'<div style="text-align:right">'
        f'<div style="font-size:1.6em;font-weight:700;font-family:\'DM Mono\',monospace;'
        f'color:#f0f0f0">{price_str}</div>'
        f'<div style="margin-top:6px;display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap">'
        f'<span style="color:{fvs_hex};font-weight:700">{fvs_emoji(fvs)} FVS {fvs:.0f}</span>'
        f'{flow_badge}'
        f'<span style="color:rgba(255,255,255,0.5)">{signal}</span>'
        f'</div></div></div></div>',
        unsafe_allow_html=True,
    )


def _render_ai_summary(row: dict, analysis: dict) -> None:
    """Section 2 — Green-bordered AI thesis box."""
    thesis = analysis.get("thesis", "")
    if not thesis:
        thesis = (f"{row.get('name', row.get('ticker',''))} operates in the "
                  f"{row.get('sector','')} sector with strong order book visibility "
                  f"and attractive growth metrics.")
    st.markdown(
        f'<div style="border:1px solid rgba(0,230,118,0.25);background:rgba(0,230,118,0.05);'
        f'border-radius:10px;padding:16px 20px;margin-bottom:16px">'
        f'<div style="font-size:0.68em;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:#00e676;margin-bottom:8px">'
        f'Why Foresight selected this company</div>'
        f'<div style="font-size:0.9em;line-height:1.7;color:rgba(255,255,255,0.8)">'
        f'{thesis}</div></div>',
        unsafe_allow_html=True,
    )


def _render_scenario_analysis(analysis: dict) -> None:
    """Section 4 — Bull / Base / Bear scenario cards."""
    st.markdown('<div class="section-lbl">SCENARIO ANALYSIS</div>', unsafe_allow_html=True)
    c_bull, c_base, c_bear = st.columns(3)
    for col, title, icon, color, key in [
        (c_bull, "BULL CASE", "🐂", "#00e676", "bullCase"),
        (c_base, "BASE CASE", "📊", "#ffd740", "baseCase"),
        (c_bear, "BEAR CASE", "🐻", "#ff5252", "bearCase"),
    ]:
        text = analysis.get(key, "Analysis pending — run AI scan for full scenario detail.")
        col.markdown(
            f'<div style="border-top:3px solid {color};background:rgba(18,18,26,0.9);'
            f'border:1px solid rgba(255,255,255,0.07);border-top:3px solid {color};'
            f'border-radius:0 0 8px 8px;padding:16px;min-height:180px">'
            f'<div style="font-weight:700;font-size:0.78em;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:{color};margin-bottom:10px">{icon} {title}</div>'
            f'<div style="font-size:0.86em;line-height:1.65;color:rgba(255,255,255,0.75)">'
            f'{text}</div></div>',
            unsafe_allow_html=True,
        )


def _render_management_credibility(row: dict, analysis: dict) -> None:
    """Section 5 — Management credibility table and AI summary."""
    st.markdown('<div class="section-lbl">MANAGEMENT CREDIBILITY</div>', unsafe_allow_html=True)
    mc_score = float(analysis.get("managementConsistencyScore") or 5)
    evidence = analysis.get("managementConsistencyEvidence", [])

    table_html = (
        '<table style="width:100%;border-collapse:collapse;font-size:0.82em">'
        '<thead><tr>'
    )
    for h in ["Quarter", "Guided Rev", "Actual Rev", "Guided Margin", "Actual Margin", "Beat/Miss"]:
        table_html += (
            f'<th style="text-align:left;padding:8px 12px;'
            f'border-bottom:1px solid rgba(255,255,255,0.08);'
            f'color:rgba(255,255,255,0.4);font-weight:600;font-size:0.85em">{h}</th>'
        )
    table_html += "</tr></thead><tbody>"

    for i, q in enumerate(["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]):
        ev   = evidence[i] if i < len(evidence) else None
        beat = "BEAT" if (ev and "beat" in ev.lower()) else \
               "MISS" if (ev and "miss" in ev.lower()) else "—"
        color  = {"BEAT": "#00e676", "MISS": "#ff5252"}.get(beat, "rgba(255,255,255,0.3)")
        row_bg = "rgba(0,230,118,0.03)" if beat == "BEAT" else \
                 "rgba(255,82,82,0.03)"  if beat == "MISS" else "transparent"
        cells  = [q, "—", "—", "—", "—", beat]
        table_html += f'<tr style="background:{row_bg}">'
        for j, cell in enumerate(cells):
            c = color if j == 5 else "rgba(255,255,255,0.7)"
            table_html += (
                f'<td style="padding:7px 12px;'
                f'border-bottom:1px solid rgba(255,255,255,0.04);color:{c}">{cell}</td>'
            )
        table_html += "</tr>"
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    beats  = sum(1 for ev in evidence if ev and "beat" in ev.lower())
    rating = "HIGH" if mc_score >= 7 else "MEDIUM" if mc_score >= 5 else "LOW"
    rating_color = {"HIGH": "#00e676", "MEDIUM": "#ffd740", "LOW": "#ff5252"}[rating]
    st.markdown(
        f'<div style="margin-top:10px;font-size:0.84em;color:rgba(255,255,255,0.55)">'
        f'Management credibility score: '
        f'<strong style="color:{rating_color}">{mc_score:.1f}/10 — {rating}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_peer_comparison(row: dict, df_all: pd.DataFrame) -> None:
    """Section 6 — Peer comparison table within the same sector."""
    st.markdown('<div class="section-lbl">PEER COMPARISON</div>', unsafe_allow_html=True)
    sector = row.get("sector", "")
    ticker = row.get("ticker", "")
    peers  = df_all[df_all["sector"] == sector].head(4) if not df_all.empty else pd.DataFrame()
    if peers.empty:
        st.caption("No peer data available in this scan.")
        return

    headers = ["Company", "FVS", "ROE %", "Rev CAGR %", "OB/Rev", "PE"]
    table_html = '<table style="width:100%;border-collapse:collapse;font-size:0.82em"><thead><tr>'
    for h in headers:
        table_html += (
            f'<th style="text-align:left;padding:8px 12px;'
            f'border-bottom:1px solid rgba(255,255,255,0.08);'
            f'color:rgba(255,255,255,0.4)">{h}</th>'
        )
    table_html += "</tr></thead><tbody>"
    for _, p in peers.iterrows():
        is_self = p["ticker"] == ticker
        cells   = [
            p.get("name", p["ticker"])[:25] + (" ←" if is_self else ""),
            f"{float(p.get('fvs') or 0):.0f}",
            f"{p['roe']:.1f}%"  if p.get("roe")       else "—",
            f"{p['revcagr']:.1f}%" if p.get("revcagr") else "—",
            f"{p['orderBookRev']:.1f}x" if p.get("orderBookRev") else "—",
            f"{p['pe']:.0f}x"   if p.get("pe")        else "—",
        ]
        style = "background:rgba(0,230,118,0.04);font-weight:600" if is_self else ""
        table_html += f'<tr style="{style}">'
        for cell in cells:
            table_html += (
                f'<td style="padding:7px 12px;'
                f'border-bottom:1px solid rgba(255,255,255,0.04);'
                f'color:rgba(255,255,255,0.8)">{cell}</td>'
            )
        table_html += "</tr>"
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)


def _render_risk_register(analysis: dict) -> None:
    """Section 7 — Numbered risk register with severity badges."""
    st.markdown('<div class="section-lbl">RISK REGISTER</div>', unsafe_allow_html=True)
    risks = analysis.get("risks", []) or [
        "Execution risk on large orders",
        "Working capital pressure",
        "Competitive intensity",
    ]
    for i, risk in enumerate(risks[:7], 1):
        sev = ("HIGH"   if any(w in str(risk).lower() for w in ["delay", "debt", "fraud", "customer"])
               else "MEDIUM" if any(w in str(risk).lower() for w in ["compet", "margin", "regul"])
               else "LOW")
        sev_color = {"HIGH": "#ff5252", "MEDIUM": "#ffd740", "LOW": "#66bb6a"}[sev]
        st.markdown(
            f'<div style="display:flex;align-items:flex-start;gap:12px;padding:8px 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<div style="min-width:22px;font-weight:700;color:rgba(255,255,255,0.3)">{i}.</div>'
            f'<div style="flex:1;font-size:0.87em;line-height:1.5">{risk}</div>'
            f'<div style="min-width:60px;text-align:right">'
            f'<span style="background:rgba(0,0,0,0.3);border:1px solid {sev_color};'
            f'color:{sev_color};padding:1px 7px;border-radius:4px;'
            f'font-size:0.72em;font-weight:700">{sev}</span></div></div>',
            unsafe_allow_html=True,
        )


def _render_financial_health_section(row: dict, qd: dict) -> None:
    """Section 8 — Financial Health Dashboard (Spec 05)."""
    st.markdown(
        '<div class="section-lbl">📊 SECTION 8 — FINANCIAL HEALTH DASHBOARD</div>',
        unsafe_allow_html=True,
    )

    # 8A — Operating Margin Trend
    st.markdown("**A. Operating Margin Trend (8 Quarters)**")
    st.plotly_chart(chart_operating_margin_trend(qd), use_container_width=True,
                    config={"displayModeBar": False})
    margins = qd.get("operating_margin", [])
    valid_m = [m for m in margins if m is not None]
    if len(valid_m) >= 2:
        bps       = round((valid_m[-1] - valid_m[0]) * 100)
        direction = "expanded" if bps > 0 else "contracted"
        st.caption(f"📌 Margin {direction} {abs(bps):+d} bps over {len(valid_m)} quarters "
                   f"— from {valid_m[0]:.1f}% to {valid_m[-1]:.1f}%")

    st.markdown("---")

    # 8B — Revenue & Profit QoQ
    st.markdown("**B. Revenue & Profit Growth QoQ**")
    st.plotly_chart(chart_revenue_profit_qoq(qd), use_container_width=True,
                    config={"displayModeBar": False})
    pat_qoq = [g for g in qd.get("pat_qoq_growth", []) if g is not None]
    if len(pat_qoq) >= 3:
        accel = all(pat_qoq[i] > pat_qoq[i - 1] for i in range(-3, 0) if i + len(pat_qoq) > 0)
        msg = ("Profit growth accelerating for 3 consecutive quarters"
               if accel else "Profit growth trend mixed — watch guidance delivery")
        st.caption(f"📌 {msg}")

    st.markdown("---")

    # 8C — Revenue Quality Heatmap
    st.markdown("**C. Revenue Quality Heatmap**")
    st.plotly_chart(chart_revenue_quality_heatmap(qd), use_container_width=True,
                    config={"displayModeBar": False})

    st.markdown("---")

    # 8D — YoY Comparison Cards
    st.markdown("**D. YoY Comparison Cards**")
    _yoy_comparison_cards(qd, row)


def _yoy_comparison_cards(qd: dict, row: dict) -> None:
    """Section 8D — 4 YoY metric cards in a row."""
    margins = qd.get("operating_margin", [])
    rev_qoq = qd.get("revenue_qoq_growth", [])
    pat_qoq = qd.get("pat_qoq_growth", [])

    def _latest(s):
        valid = [v for v in s if v is not None]
        return valid[-1] if valid else None

    def _prev(s):
        valid = [v for v in s if v is not None]
        return valid[-2] if len(valid) >= 2 else None

    def _card(title, curr, prev, unit="%") -> str:
        if curr is None:
            return (f'<div class="yoy-card"><div class="yoy-title">{title}</div>'
                    f'<div class="yoy-value">—</div></div>')
        delta  = curr - prev if prev is not None else None
        color  = "#00e676" if (delta is None or delta >= 0) else "#ff5252"
        arrow  = "↑" if (delta is not None and delta >= 0) else "↓"
        d_str  = f"{arrow} {abs(delta):.1f}{unit}" if delta is not None else ""
        bar    = min(100, max(0, int(curr)))
        prev_s = (f'<div style="color:rgba(255,255,255,0.35);font-size:0.75em">'
                  f'vs {prev:.1f}{unit} last year</div>') if prev else ""
        return (
            f'<div class="yoy-card" style="border-left:3px solid {color}">'
            f'<div class="yoy-title">{title}</div>'
            f'<div class="yoy-value" style="color:{color}">'
            f'{curr:.1f}{unit} <span style="font-size:0.7em;color:{color}">{d_str}</span></div>'
            f'{prev_s}'
            f'<div style="height:3px;background:rgba(255,255,255,0.07);'
            f'border-radius:2px;margin-top:8px">'
            f'<div style="width:{bar}%;height:3px;background:{color};border-radius:2px">'
            f'</div></div></div>'
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_card("Operating Margin",   _latest(margins), _prev(margins)), unsafe_allow_html=True)
    c2.markdown(_card("Revenue Growth QoQ", _latest(rev_qoq), _prev(rev_qoq)), unsafe_allow_html=True)
    c3.markdown(_card("PAT Growth QoQ",     _latest(pat_qoq), _prev(pat_qoq)), unsafe_allow_html=True)
    ob_rev = float(row.get("orderBookRev") or 0)
    c4.markdown(_card("Order Book Ratio",   ob_rev, None, "x"), unsafe_allow_html=True)


def _render_valuation_model(row: dict, selected: str) -> None:
    """Section 9 — 3-scenario valuation model with user-input assumptions."""
    st.markdown('<div class="section-lbl">VALUATION MODEL</div>', unsafe_allow_html=True)

    with st.expander("Build 3-Scenario Valuation Model", expanded=False):
        col_in, col_out = st.columns([1, 2])
        with col_in:
            rev_growth  = st.number_input("Revenue Growth %", 5.0, 100.0, 25.0, step=1.0,
                                          key=f"vg_{selected}")
            margin_exp  = st.number_input("Margin Expansion %", 0.0, 20.0, 2.0, step=0.5,
                                          key=f"me_{selected}")
            pe_multiple = st.number_input("Exit PE Multiple", 5.0, 100.0, 30.0, step=1.0,
                                          key=f"pe_{selected}")
            years       = st.slider("Projection Years", 1, 5, 3, key=f"yr_{selected}")
            build_btn   = st.button("Generate Model", use_container_width=True,
                                    key=f"vbuild_{selected}")

        with col_out:
            val_key = f"valuation_{selected}"
            if build_btn:
                with st.spinner("Building valuation model…"):
                    model = build_valuation_model(row, {
                        "revenueGrowth": rev_growth / 100,
                        "marginExpansion": margin_exp / 100,
                        "peMultiple": pe_multiple,
                        "years": years,
                    })
                st.session_state[val_key] = {"model": model, "years": years}

            val_data = st.session_state.get(val_key)
            if val_data:
                _render_valuation_output(val_data["model"], row, val_data["years"])
            else:
                st.caption("Enter assumptions and click **Generate Model**.")


def _render_valuation_output(model: dict, company: dict, years: int) -> None:
    """Display scenario summary table and target-price bar chart."""
    import plotly.graph_objects as go
    price = float(company.get("price") or 0)

    def _cagr(tp):
        try:
            return round(((float(tp) / price) ** (1 / years) - 1) * 100, 1) if price > 0 and float(tp) > 0 else None
        except Exception:
            return None

    def _upside(tp):
        try:
            return round((float(tp) / price - 1) * 100, 1) if price > 0 else None
        except Exception:
            return None

    rows = []
    for scenario, icon in [("bull", "🐂 Bull"), ("base", "📊 Base"), ("bear", "🐻 Bear")]:
        s    = model.get(scenario, {})
        tp   = float(s.get("targetPrice") or 0)
        rev  = s.get("revenue") or []
        prf  = s.get("profit")  or []
        rows.append({
            "Scenario":      icon,
            "Final Revenue": f"₹{rev[-1]:,.0f} Cr" if rev else "—",
            "Final PAT":     f"₹{prf[-1]:,.0f} Cr" if prf else "—",
            "Target Price":  f"₹{tp:,.0f}" if tp else "—",
            "CAGR":          f"{_cagr(tp):+.1f}%"   if _cagr(tp) is not None  else "—",
            "Upside":        f"{_upside(tp):+.1f}%"  if _upside(tp) is not None else "—",
        })

    import pandas as pd
    df_sum = pd.DataFrame(rows)

    def _colour(row):
        clr = {"Bull": "rgba(0,230,118,0.12)", "Base": "rgba(255,215,64,0.12)",
               "Bear": "rgba(255,82,82,0.12)"}
        for k, bg in clr.items():
            if k in str(row.get("Scenario", "")):
                return [f"background-color:{bg}"] * len(row)
        return [""] * len(row)

    st.dataframe(df_sum.style.apply(_colour, axis=1), use_container_width=True, hide_index=True)

    # Target-price bar chart
    tps = [float(model.get(s, {}).get("targetPrice") or 0) for s in ["bull", "base", "bear"]]
    fig = go.Figure(go.Bar(
        x=["Bull", "Base", "Bear"], y=tps,
        marker_color=["#00e676", "#ffd740", "#ff5252"],
        text=[f"₹{tp:,.0f}" for tp in tps], textposition="outside",
        textfont=dict(color="#f0f0f0"),
    ))
    if price:
        fig.add_hline(y=price, line_dash="dot", line_color="rgba(255,255,255,0.4)",
                      annotation_text=f"Current ₹{price:,.0f}",
                      annotation_font_color="rgba(255,255,255,0.5)")
    fig.update_layout(
        paper_bgcolor="#12121a", plot_bgcolor="#12121a",
        yaxis=dict(title="Price (₹)", gridcolor="rgba(255,255,255,0.05)",
                   color="rgba(255,255,255,0.4)"),
        xaxis=dict(color="rgba(255,255,255,0.6)"),
        font=dict(family="DM Sans", color="#f0f0f0"),
        height=300, margin=dict(t=30, b=20, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if model.get("valuationCommentary"):
        st.caption(model["valuationCommentary"])


# ── Main render ────────────────────────────────────────────────────────────────

def render_analyse_tab() -> None:
    """Render the full Analyse tab."""
    df_all = st.session_state.get("scan_results", pd.DataFrame())
    if isinstance(df_all, pd.DataFrame) and not df_all.empty:
        if "capClass" not in df_all.columns:
            from universe.stocks import compute_cap_class
            df_all["capClass"] = df_all.apply(
                lambda r: compute_cap_class(r.get("mcap") or 0, r.get("price") or 0), axis=1
            )
        from ui.filters import add_signal_column
        df_all = add_signal_column(df_all)

    tickers = list(df_all["ticker"].tolist()) if not df_all.empty else []
    pre     = st.session_state.get("analyse_ticker")
    st.session_state.pop("analyse_tab_switch", None)

    if not tickers:
        st.info("Run an AI Scan first to load companies.")
        return

    selected = st.selectbox(
        "Select Company",
        options=tickers,
        format_func=lambda t: (
            f"{t}  —  {df_all.loc[df_all['ticker']==t,'name'].values[0]}"
            if not df_all.empty and t in df_all["ticker"].values else t
        ),
        index=tickers.index(pre) if pre and pre in tickers else 0,
        key="analyse_selectbox",
    )
    if not selected:
        return

    row = df_all[df_all["ticker"] == selected].iloc[0].to_dict() if not df_all.empty else {}

    # Load AI analysis (cached per company)
    analysis_cache = st.session_state.setdefault("company_analyses", {})
    if selected not in analysis_cache:
        with st.spinner(f"Running AI deep dive on {selected}…"):
            analysis_cache[selected] = analyze_company(row)
    analysis = analysis_cache[selected]

    # Load quarterly data (cached per company)
    qd_cache = st.session_state.setdefault("quarterly_cache", {})
    if selected not in qd_cache:
        with st.spinner(f"Loading quarterly data for {selected}…"):
            qd_cache[selected] = fetch_quarterly_data(selected)
    qd = qd_cache[selected]

    # ── Section 1: Company Header ──────────────────────────────────────────────
    _render_company_header(row, analysis)

    if st.button("← Back to Discover", key="back_to_discover"):
        st.session_state["analyse_ticker"] = None
        st.rerun()

    st.markdown("---")

    # ── Section 2: AI Summary ──────────────────────────────────────────────────
    _render_ai_summary(row, analysis)

    # ── Section 3: 6-Card Analytics Grid ──────────────────────────────────────
    st.markdown('<div class="section-lbl">ANALYTICS GRID</div>', unsafe_allow_html=True)
    sector = row.get("sector", "")

    r1c1, r1c2 = st.columns(2)
    chart_card("Order Backlog",           sector, chart_order_backlog(row, qd),           r1c1)
    chart_card("Revenue CAGR",            sector, chart_revenue_cagr(row, qd),            r1c2)

    r2c1, r2c2 = st.columns(2)
    chart_card("Margin Profile",          sector, chart_margin_profile(row, qd),          r2c1)
    chart_card("Key Financials",          sector, chart_key_financials(row),              r2c2)

    r3c1, r3c2 = st.columns(2)
    chart_card("Order Inflow vs Execution", sector, chart_order_inflow_vs_execution(row, qd), r3c1)
    chart_card("Conviction Scorecard",    sector, chart_conviction_scorecard(analysis),   r3c2)

    st.markdown("---")

    # ── Section 4: Scenario Analysis ──────────────────────────────────────────
    _render_scenario_analysis(analysis)

    st.markdown("---")

    # ── Section 5: Management Credibility ─────────────────────────────────────
    _render_management_credibility(row, analysis)

    st.markdown("---")

    # ── Section 6: Peer Comparison ────────────────────────────────────────────
    _render_peer_comparison(row, df_all if not df_all.empty else pd.DataFrame())

    st.markdown("---")

    # ── Section 7: Risk Register ───────────────────────────────────────────────
    _render_risk_register(analysis)

    st.markdown("---")

    # ── Section 8: Financial Health Dashboard ─────────────────────────────────
    _render_financial_health_section(row, qd)

    st.markdown("---")

    # ── Section 9: Valuation Model ────────────────────────────────────────────
    _render_valuation_model(row, selected)

    st.markdown("---")

    # ── Section 10: Shareholding Pattern (Spec 07) ────────────────────────────
    _render_shareholding_section(ticker)

    st.markdown("---")

    # ── Section 11: Historical Smart Money Intelligence (Spec 07) ─────────────
    _render_smart_money_history(ticker, row)


# ── Spec 07 helper: Shareholding Pattern section ──────────────────────────────

def _render_shareholding_section(ticker: str) -> None:
    """Section 10 — Shareholding pattern chart + QoQ table."""
    st.subheader("📊 Shareholding Pattern")

    try:
        from data.fii_dii_engine import fetch_shareholding_pattern, detect_accumulation_distribution
        quarters = fetch_shareholding_pattern(ticker)
        accum    = detect_accumulation_distribution(ticker)
    except Exception as exc:
        st.warning(f"Shareholding data unavailable: {exc}")
        return

    if not quarters:
        st.info("No shareholding data available for this company.")
        return

    # Stacked area chart
    fig = chart_shareholding_pattern(quarters)
    st.plotly_chart(fig, use_container_width=True)

    # Accumulation signal banner
    pattern   = accum.get("pattern", "NEUTRAL")
    strength  = accum.get("pattern_strength", "LOW")
    verdict   = accum.get("smart_money_verdict", "")
    combined  = accum.get("combined_signal", "NEUTRAL")
    pat_color = {"ACCUMULATING": "#00e676", "DISTRIBUTING": "#ff5252", "NEUTRAL": "#aaa"}.get(pattern, "#aaa")

    st.markdown(
        f"""<div style="background:#12121a;border:1px solid {pat_color};border-radius:8px;
            padding:12px 16px;margin:8px 0">
          <span style="color:{pat_color};font-weight:700">{pattern} · {strength} CONVICTION</span>
          &nbsp;·&nbsp;<span style="opacity:0.7">{combined}</span><br>
          <span style="font-size:0.85rem;opacity:0.9">{verdict}</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # QoQ change table
    st.markdown("**Quarter-on-Quarter Change (%)**")
    table_rows = []
    for q in quarters:
        def _cell(val) -> str:
            if val is None:
                return "—"
            sign = "+" if val >= 0 else ""
            color = "#00e676" if val > 0.05 else "#ff5252" if val < -0.05 else "#aaa"
            return f'<span style="color:{color}">{sign}{val:.2f}%</span>'

        table_rows.append(
            f"<tr>"
            f"<td style='padding:4px 8px'>{q.get('quarter','')}</td>"
            f"<td style='padding:4px 8px'>{_cell(q.get('fii_change_qoq'))}</td>"
            f"<td style='padding:4px 8px'>{_cell(q.get('dii_change_qoq'))}</td>"
            f"<td style='padding:4px 8px'>{_cell(q.get('promoter_change_qoq'))}</td>"
            f"<td style='padding:4px 8px'>{_cell(q.get('public_change_qoq'))}</td>"
            f"</tr>"
        )

    table_html = (
        "<table style='width:100%;border-collapse:collapse;font-size:0.82rem'>"
        "<thead><tr style='opacity:0.6'>"
        "<th style='padding:4px 8px;text-align:left'>Quarter</th>"
        "<th style='padding:4px 8px'>FII Δ</th>"
        "<th style='padding:4px 8px'>DII Δ</th>"
        "<th style='padding:4px 8px'>Promoter Δ</th>"
        "<th style='padding:4px 8px'>Public Δ</th>"
        "</tr></thead><tbody>"
        + "".join(table_rows)
        + "</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ── Spec 07 helper: Historical Smart Money Intelligence section ───────────────

def _render_smart_money_history(ticker: str, row: dict) -> None:
    """Section 11 — AI-powered historical FII/DII pattern intelligence."""
    st.subheader("🧠 Smart Money Intelligence")

    try:
        from data.fii_dii_engine import (
            fetch_shareholding_pattern,
            fetch_bulk_block_deals,
            detect_accumulation_distribution,
        )
        from ai.prompts import FII_DII_PATTERN_PROMPT
        import json, os, re
        import anthropic

        quarters  = fetch_shareholding_pattern(ticker)
        bulk      = fetch_bulk_block_deals(ticker)
        accum     = detect_accumulation_distribution(ticker)

        if not quarters:
            st.info("Shareholding data required for smart money analysis.")
            return

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key.startswith("sk-ant-..."):
            _render_smart_money_fallback(accum, bulk)
            return

        prompt = FII_DII_PATTERN_PROMPT.format(
            symbol=ticker,
            shareholding_json=json.dumps(quarters[-8:]),
            bulk_deals_json=json.dumps(bulk[:10]),
            accum_signal_json=json.dumps(accum),
        )

        from data.cache import get as cache_get, put as cache_put
        cached = cache_get(ticker, "fii_ai_analysis")
        if cached:
            insight = cached
        else:
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text
            clean = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            try:
                insight = json.loads(clean)
            except Exception:
                insight = {}
            if insight:
                cache_put(ticker, "fii_ai_analysis", insight)

        _render_smart_money_card(insight, accum)

    except Exception as exc:
        st.warning(f"Smart money analysis unavailable: {exc}")


def _render_smart_money_fallback(accum: dict, bulk: list) -> None:
    """Show rule-based smart money card when Claude API is not configured."""
    pattern  = accum.get("pattern", "NEUTRAL")
    strength = accum.get("pattern_strength", "LOW")
    verdict  = accum.get("smart_money_verdict", "No clear signal.")
    fii_qoq  = accum.get("fii_last_qoq")
    dii_qoq  = accum.get("dii_last_qoq")

    def _sign(v) -> str:
        if v is None:
            return "—"
        return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

    pat_color = {"ACCUMULATING": "#00e676", "DISTRIBUTING": "#ff5252"}.get(pattern, "#aaa")
    st.markdown(
        f"""<div style="background:#12121a;border:1px solid {pat_color};border-radius:10px;padding:16px">
          <div style="font-weight:700;color:{pat_color};font-size:1rem">🏦 Smart Money Signal</div>
          <div style="margin:8px 0;font-size:0.9rem">
            FII last QoQ: <b>{_sign(fii_qoq)}</b> &nbsp;|&nbsp;
            DII last QoQ: <b>{_sign(dii_qoq)}</b>
          </div>
          <div style="opacity:0.85;font-size:0.85rem">{verdict}</div>
          <div style="margin-top:8px;font-size:0.75rem;opacity:0.5">
            Enable Claude API key for AI-powered historical pattern intelligence.
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_smart_money_card(insight: dict, accum: dict) -> None:
    """Render the full AI insight card for smart money section."""
    combined  = insight.get("combined_signal", accum.get("combined_signal", "NEUTRAL"))
    verdict   = insight.get("smart_money_verdict", accum.get("smart_money_verdict", ""))
    hist      = insight.get("historical_insight", "")
    price_pred= insight.get("price_impact_prediction", "")
    conf      = insight.get("confidence", 0)
    positional= insight.get("positional_opportunity", False)
    reasoning = insight.get("reasoning", "")

    sig_color = {
        "STRONG_BUY": "#00e676", "BUY": "#69f0ae",
        "NEUTRAL": "#aaa",
        "SELL": "#ff8a65", "STRONG_SELL": "#ff5252",
    }.get(combined, "#aaa")

    st.markdown(
        f"""<div style="background:#12121a;border:1px solid {sig_color};border-radius:10px;padding:16px">
          <div style="font-weight:700;color:{sig_color};font-size:1rem">
            🧠 Smart Money — {combined.replace("_"," ")} &nbsp;
            <span style="font-size:0.75rem;opacity:0.6">Confidence: {conf}%</span>
          </div>
          <div style="margin:8px 0;font-size:0.88rem">{verdict}</div>
          {"<div style='margin:8px 0;font-size:0.85rem;opacity:0.85'><b>Historical pattern:</b> " + hist + "</div>" if hist else ""}
          {"<div style='font-size:0.85rem;opacity:0.85'><b>Price implication:</b> " + price_pred + "</div>" if price_pred else ""}
          {"<div style='margin-top:10px;padding:8px;background:#1a2a1a;border-radius:6px;font-size:0.82rem;color:#00e676'>⚡ Positional opportunity detected</div>" if positional else ""}
          {"<div style='margin-top:8px;font-size:0.78rem;opacity:0.55'>" + reasoning + "</div>" if reasoning else ""}
        </div>""",
        unsafe_allow_html=True,
    )
