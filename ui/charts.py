"""All plotly chart builders for the Foresight Analyse tab.

Import from this module in ui/analyse.py to keep chart logic separate.
Every function returns a go.Figure; none call st.* directly except chart_card().
"""

import plotly.graph_objects as go
import streamlit as st

# ── Colour palette ────────────────────────────────────────────────────────────
_PLOT_BG  = "#12121a"
_PAPER_BG = "#12121a"
_GRID_CLR = "rgba(255,255,255,0.05)"
_FONT_CLR = "#f0f0f0"
_GREEN    = "#00e676"
_YELLOW   = "#ffd740"
_RED      = "#ff5252"
_BLUE     = "#42a5f5"

SECTOR_COLORS = {
    "Defence":    "#5c6bc0",
    "Railways":   "#26a69a",
    "EPC":        "#ef5350",
    "EMS":        "#ab47bc",
    "Power":      "#ffa726",
    "Solar/Wind": "#66bb6a",
}


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
    return "128,128,128"


def base_layout(**extra) -> dict:
    """Base plotly layout dict shared by all Foresight charts."""
    layout = dict(
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_PLOT_BG,
        font=dict(color=_FONT_CLR, family="DM Sans, sans-serif", size=11),
        margin=dict(l=40, r=20, t=36, b=36),
        xaxis=dict(gridcolor=_GRID_CLR, linecolor=_GRID_CLR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=_GRID_CLR, linecolor=_GRID_CLR, tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        height=280,
    )
    layout.update(extra)
    return layout


def chart_card(title: str, sector: str, fig: go.Figure, col) -> None:
    """Render a plotly chart inside a sector-coloured card header."""
    color = SECTOR_COLORS.get(sector, "#5c6bc0")
    col.markdown(
        f'<div style="border-top:3px solid {color};background:#12121a;'
        f'border-radius:0 0 8px 8px;padding:10px 14px 0;margin-bottom:4px">'
        f'<div style="font-size:0.72em;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.07em;color:{color}">{title}</div></div>',
        unsafe_allow_html=True,
    )
    col.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 6 Analytics cards ─────────────────────────────────────────────────────────

def chart_order_backlog(row: dict, qd: dict) -> go.Figure:
    """Card 1 — OB/Revenue donut chart."""
    ob_rev   = float(row.get("orderBookRev") or 2.0)
    pending  = max(0.0, ob_rev - 1.0)
    fig = go.Figure(go.Pie(
        labels=["Executed (Annual Rev)", "Pending Pipeline"],
        values=[1.0, pending],
        hole=0.62,
        marker=dict(colors=[_GREEN, _BLUE]),
        textinfo="label+percent",
        textfont=dict(size=10, color=_FONT_CLR),
        hovertemplate="%{label}: %{value:.1f}x<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{ob_rev:.1f}x</b><br>OB/Rev",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=_GREEN))
    fig.update_layout(**base_layout(
        title=dict(text="Order Backlog Ratio", font=dict(size=11)),
        showlegend=True, legend=dict(orientation="h", y=-0.1),
    ))
    return fig


def chart_revenue_cagr(row: dict, qd: dict) -> go.Figure:
    """Card 2 — Revenue bar chart with CAGR annotation."""
    quarters = qd.get("quarters", [])
    revenue  = qd.get("revenue", [])
    if not revenue or len(revenue) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Quarterly data loading…", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=12, color=_FONT_CLR))
        fig.update_layout(**base_layout())
        return fig
    colors = [_GREEN if i == 0 or (revenue[i] or 0) >= (revenue[i-1] or 0) else _RED
              for i in range(len(revenue))]
    fig = go.Figure(go.Bar(
        x=quarters or list(range(len(revenue))), y=revenue,
        name="Revenue (₹ Cr)", marker=dict(color=colors, opacity=0.85),
        hovertemplate="₹%{y:,.0f} Cr<extra></extra>",
    ))
    if row.get("revcagr"):
        fig.add_annotation(text=f"3Y CAGR: {row['revcagr']:.1f}%",
                           x=0.98, y=1.05, xref="paper", yref="paper",
                           showarrow=False, font=dict(size=11, color=_GREEN), align="right")
    fig.update_layout(**base_layout(
        title=dict(text="Revenue Trend (₹ Cr)", font=dict(size=11)), yaxis_title="₹ Cr"))
    return fig


def chart_margin_profile(row: dict, qd: dict) -> go.Figure:
    """Card 3 — Margin profile donut chart."""
    gross_m  = float(row.get("roe") or 15) * 0.6
    ebitda_m = float(row.get("roce") or 12) * 0.5
    margins  = qd.get("operating_margin", [])
    valid_m  = [m for m in margins if m is not None]
    pat_m    = valid_m[-1] if valid_m else ebitda_m * 0.65

    fig = go.Figure(go.Pie(
        labels=["Gross Margin", "EBITDA Margin", "PAT Margin"],
        values=[max(0, gross_m), max(0, ebitda_m - pat_m), max(0, pat_m)],
        hole=0.62,
        marker=dict(colors=[_GREEN, _BLUE, _YELLOW]),
        textinfo="label+percent", textfont=dict(size=10, color=_FONT_CLR),
    ))
    fig.add_annotation(text=f"<b>{pat_m:.1f}%</b><br>PAT Margin",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=13, color=_YELLOW))
    fig.update_layout(**base_layout(
        title=dict(text="Margin Profile", font=dict(size=11)),
        showlegend=True, legend=dict(orientation="h", y=-0.1),
    ))
    return fig


def chart_key_financials(row: dict) -> go.Figure:
    """Card 4 — Key financials bar chart."""
    roe  = float(row.get("roe")    or 0)
    roce = float(row.get("roce")   or 0)
    de   = float(row.get("debtEq") or 0)
    cagr = float(row.get("revcagr") or 0)
    fig = go.Figure(go.Bar(
        x=["ROE %", "ROCE %", "D/E ratio", "Rev CAGR %"],
        y=[roe, roce, de * 10, cagr],
        marker=dict(color=[_GREEN, _BLUE, (_RED if de > 0.5 else _GREEN), _YELLOW], opacity=0.85),
        hovertemplate="%{x}: %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        title=dict(text="Key Financials", font=dict(size=11)), yaxis_title="Value"))
    return fig


def chart_order_inflow_vs_execution(row: dict, qd: dict) -> go.Figure:
    """Card 5 — Order inflow vs execution grouped bars."""
    quarters = qd.get("quarters", [])
    revenue  = qd.get("revenue", [])
    n = min(4, len(revenue))
    if n < 1:
        fig = go.Figure()
        fig.add_annotation(text="Quarterly data loading…", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=12, color=_FONT_CLR))
        fig.update_layout(**base_layout())
        return fig
    q_labels  = quarters[-n:]
    execution = revenue[-n:]
    ob_rev    = float(row.get("orderBookRev") or 2.0)
    ob_trend  = row.get("orderBookTrend", "STABLE")
    factor    = 1.15 if ob_trend == "ACCELERATING" else 0.9 if ob_trend == "DECLINING" else 1.0
    inflow    = [e * ob_rev * factor / 4 if e else None for e in execution]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=q_labels, y=inflow, name="New Orders Won",
                         marker=dict(color=_BLUE, opacity=0.85),
                         hovertemplate="₹%{y:,.0f} Cr<extra></extra>"))
    fig.add_trace(go.Bar(x=q_labels, y=execution, name="Revenue Executed",
                         marker=dict(color=_GREEN, opacity=0.75),
                         hovertemplate="₹%{y:,.0f} Cr<extra></extra>"))
    if ob_trend == "ACCELERATING":
        fig.add_annotation(text="ACCELERATING", x=0.5, y=1.05, xref="paper", yref="paper",
                           showarrow=False, font=dict(size=11, color=_GREEN))
    fig.update_layout(**base_layout(
        title=dict(text="Order Inflow vs Execution", font=dict(size=11)),
        barmode="group", yaxis_title="₹ Cr",
    ))
    return fig


def chart_conviction_scorecard(analysis: dict) -> go.Figure:
    """Card 6 — Conviction sub-scores as a bar chart."""
    scores = {
        "Order Pipeline":   float(analysis.get("visibilityScore") or 5) * 10,
        "Revenue Quality":  float(analysis.get("growthScore") or 5) * 10,
        "Mgmt Credibility": float(analysis.get("managementConsistencyScore") or 5) * 10,
        "Tech Momentum":    float(analysis.get("riskScore") or 5) * 10,
    }
    def _clr(v):
        return _GREEN if v >= 70 else _YELLOW if v >= 50 else _RED
    fig = go.Figure()
    for name, val in scores.items():
        fig.add_trace(go.Bar(
            name=name, x=[name], y=[val],
            marker=dict(color=_clr(val), opacity=0.85),
            text=[f"{val:.0f}"], textposition="outside",
            textfont=dict(size=11, color=_FONT_CLR),
            hovertemplate=f"{name}: %{{y:.0f}}/100<extra></extra>",
        ))
    fig.update_layout(**base_layout(
        title=dict(text="Conviction Scorecard (0-100)", font=dict(size=11)),
        yaxis=dict(range=[0, 110], gridcolor=_GRID_CLR),
        barmode="group", showlegend=False,
    ))
    return fig


# ── Section 8: Financial Health charts ────────────────────────────────────────

def chart_operating_margin_trend(qd: dict) -> go.Figure:
    """Section 8A — Operating margin line chart (8 quarters)."""
    quarters = qd.get("quarters", [])
    margins  = qd.get("operating_margin", [])
    valid    = [m for m in margins if m is not None]
    if len(valid) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient margin data", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=12, color=_FONT_CLR))
        fig.update_layout(**base_layout(height=320))
        return fig
    color = _GREEN if valid[-1] > valid[0] else _RED
    fig = go.Figure(go.Scatter(
        x=quarters or list(range(len(margins))),
        y=margins,
        mode="lines+markers",
        name="Operating Margin %",
        line=dict(color=color, width=2.5),
        marker=dict(size=6, color=color),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_to_rgb(color)},0.08)",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    peak_idx   = margins.index(max(valid))
    trough_idx = margins.index(min(valid))
    for idx, label, ann_color in [(peak_idx, "Peak", _GREEN), (trough_idx, "Trough", _RED)]:
        if 0 <= idx < len(quarters):
            fig.add_annotation(
                x=quarters[idx], y=margins[idx],
                text=f"{label}<br>{margins[idx]:.1f}%",
                showarrow=True, arrowhead=2,
                font=dict(size=9, color=ann_color),
                bgcolor="rgba(18,18,26,0.9)",
            )
    fig.update_layout(**base_layout(
        title=dict(text="Operating Margin Trend (8 Quarters)", font=dict(size=12)),
        yaxis_title="Margin %", height=320,
    ))
    return fig


def chart_revenue_profit_qoq(qd: dict) -> go.Figure:
    """Section 8B — Revenue + PAT grouped bars with QoQ labels."""
    quarters = qd.get("quarters", [])
    revenue  = qd.get("revenue", [])
    pat      = qd.get("pat", [])
    rev_qoq  = qd.get("revenue_qoq_growth", [])
    pat_qoq  = qd.get("pat_qoq_growth", [])
    if not revenue or len(revenue) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Quarterly revenue data loading…", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=12, color=_FONT_CLR))
        fig.update_layout(**base_layout(height=320))
        return fig
    rev_text = [
        f"+{rev_qoq[i]:.0f}%" if i < len(rev_qoq) and rev_qoq[i] is not None and rev_qoq[i] > 0
        else f"{rev_qoq[i]:.0f}%" if i < len(rev_qoq) and rev_qoq[i] is not None
        else "" for i in range(len(revenue))
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quarters or list(range(len(revenue))), y=revenue,
        name="Revenue (₹ Cr)", marker=dict(color=_BLUE, opacity=0.85),
        text=rev_text, textposition="outside",
        textfont=dict(size=9, color=_FONT_CLR),
        hovertemplate="Revenue ₹%{y:,.0f} Cr<extra></extra>",
    ))
    if pat and len([p for p in pat if p is not None]) >= 2:
        pat_text = [
            f"+{pat_qoq[i]:.0f}%" if pat_qoq and i < len(pat_qoq) and pat_qoq[i] is not None and pat_qoq[i] > 0
            else f"{pat_qoq[i]:.0f}%" if pat_qoq and i < len(pat_qoq) and pat_qoq[i] is not None
            else "" for i in range(len(pat))
        ]
        fig.add_trace(go.Bar(
            x=quarters or list(range(len(pat))), y=pat,
            name="PAT (₹ Cr)", marker=dict(color=_GREEN, opacity=0.75),
            text=pat_text, textposition="outside",
            textfont=dict(size=9, color=_FONT_CLR),
            hovertemplate="PAT ₹%{y:,.0f} Cr<extra></extra>",
        ))
    fig.update_layout(**base_layout(
        title=dict(text="Revenue & Profit Growth QoQ", font=dict(size=12)),
        barmode="group", yaxis_title="₹ Cr", height=320,
    ))
    return fig


def chart_revenue_quality_heatmap(qd: dict) -> go.Figure:
    """Section 8C — Calendar-style heatmap (quarters × 4 metrics)."""
    quarters = qd.get("quarters", [])
    margins  = qd.get("operating_margin", [])
    rev_qoq  = qd.get("revenue_qoq_growth", [])
    pat_qoq  = qd.get("pat_qoq_growth", [])
    if not quarters or len(quarters) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Quarterly data loading…", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=12, color=_FONT_CLR))
        fig.update_layout(**base_layout(height=220))
        return fig
    n = len(quarters)
    metrics = ["Revenue Growth", "PAT Growth", "Op Margin", "Beat/Miss"]
    def _norm(series):
        valid = [v for v in series if v is not None]
        if not valid:
            return [0.5] * n
        mn, mx = min(valid), max(valid)
        rng = mx - mn if mx != mn else 1
        return [(v - mn) / rng if v is not None else 0.5 for v in series[:n]]
    beat_scores = [0.8 if s is not None and s > 0 else 0.3 if s is not None and s < -5 else 0.5
                   for s in rev_qoq[:n]]
    z    = [_norm(rev_qoq), _norm(pat_qoq), _norm(margins), beat_scores]
    text = [
        [f"{rev_qoq[i]:+.0f}%" if i < len(rev_qoq) and rev_qoq[i] is not None else "—" for i in range(n)],
        [f"{pat_qoq[i]:+.0f}%" if i < len(pat_qoq) and pat_qoq[i] is not None else "—" for i in range(n)],
        [f"{margins[i]:.1f}%" if i < len(margins) and margins[i] is not None else "—" for i in range(n)],
        ["✅" if beat_scores[i] >= 0.7 else "❌" if beat_scores[i] <= 0.35 else "🟡" for i in range(n)],
    ]
    fig = go.Figure(go.Heatmap(
        z=z, x=quarters[:n], y=metrics,
        text=text, texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        colorscale=[[0, "#ff5252"], [0.4, "#ffd740"], [0.7, "#69f0ae"], [1.0, "#00e676"]],
        showscale=False,
        hovertemplate="%{y} — %{x}: %{text}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        title=dict(text="Revenue Quality Heatmap (8 Quarters × 4 Metrics)", font=dict(size=12)),
        height=220, margin=dict(l=100, r=20, t=40, b=40),
    ))
    return fig


# ── Spec 07: Shareholding pattern stacked area chart ─────────────────────────

def chart_shareholding_pattern(quarters: list[dict]) -> go.Figure:
    """Stacked area chart of FII / DII / Promoter / Public % over last 8 quarters."""
    if not quarters:
        fig = go.Figure()
        fig.update_layout(**base_layout(
            title=dict(text="Shareholding Pattern — No Data", font=dict(size=12)),
            height=260,
        ))
        return fig

    labels    = [q.get("quarter", "") for q in quarters]
    fii_vals  = [q.get("fii_pct") or 0 for q in quarters]
    dii_vals  = [q.get("dii_pct") or 0 for q in quarters]
    prom_vals = [q.get("promoter_pct") or 0 for q in quarters]
    pub_vals  = [q.get("public_pct") or 0 for q in quarters]

    fig = go.Figure()
    for name, vals, color in [
        ("FII",      fii_vals,  "#2196f3"),
        ("DII",      dii_vals,  "#00e676"),
        ("Promoter", prom_vals, "#ff9800"),
        ("Public",   pub_vals,  "#9e9e9e"),
    ]:
        fig.add_trace(go.Scatter(
            x=labels, y=vals, name=name,
            mode="lines", stackgroup="one",
            line=dict(color=color, width=1.5),
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.25)" if color.startswith("#") else color,
            hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(**base_layout(
        title=dict(text="Shareholding Pattern — Last 8 Quarters (%)", font=dict(size=12)),
        height=260, margin=dict(l=40, r=20, t=40, b=40),
    ))
    fig.update_yaxes(range=[0, 100])
    return fig
