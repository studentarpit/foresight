"""Company deep-dive panel — FVS banner, scores, thesis, bull/base/bear,
Signal Intelligence Grid, multi-DMA technical view, Expectation Intelligence section."""

import streamlit as st

from ai.fvs import fvs_band, fvs_emoji

# ── HTML helpers ──────────────────────────────────────────────────────────────

def _pill(value, true_label, false_label, true_color="#28a745", false_color="#6c757d"):
    color = true_color if value else false_color
    label = true_label if value else false_label
    return (f'<span style="background:{color};color:#fff;padding:2px 8px;'
            f'border-radius:12px;font-size:0.78em;font-weight:600">{label}</span>')


def _badge(label: str, color: str) -> str:
    return (f'<span style="background:{color};color:#fff;padding:2px 8px;'
            f'border-radius:12px;font-size:0.78em;font-weight:600">{label}</span>')


_SENTIMENT_COLORS = {
    "positive": "#00e676", "neutral": "rgba(255,255,255,0.3)",
    "cautious": "#ff9800", "defensive": "#ff5252",
}
_PROMOTER_COLORS = {
    "buying": "#00e676", "neutral": "rgba(255,255,255,0.3)",
    "selling": "#ff9800", "pledging": "#ff5252",
}
_EXP_COLORS = {"BEAT": "#00e676", "MISS": "#ff5252", "MIXED": "#ffd740", "UNKNOWN": "rgba(255,255,255,0.3)"}
_TECH_COLORS = {
    "STRONG_UPTREND": "#00e676", "UPTREND": "#69f0ae",
    "MIXED": "#ffd740", "WEAK": "#ff9800", "DOWNTREND": "#ff5252", "UNKNOWN": "rgba(255,255,255,0.3)",
}


# ── Main render ───────────────────────────────────────────────────────────────

def render_company_deep_dive(company: dict, analysis: dict) -> None:
    if "error" in analysis:
        st.warning(f"Analysis unavailable: {analysis['error']}")
        return

    name   = company.get("name", company.get("ticker", ""))
    ticker = company.get("ticker", "")
    st.markdown(f"## {name} `{ticker}`")

    # ── FVS headline banner ───────────────────────────────────────────────────
    fvs = float(analysis.get("fvsRefined") or company.get("fvs") or 0)
    label, color = fvs_band(fvs)
    emoji = fvs_emoji(fvs)
    # Dark-theme semi-transparent backgrounds
    band_bg = {
        "green":  ("rgba(0,230,118,0.1)",  "#00e676"),
        "yellow": ("rgba(255,215,64,0.1)", "#ffd740"),
        "orange": ("rgba(255,152,0,0.1)",  "#ff9800"),
        "red":    ("rgba(255,82,82,0.1)",  "#ff5252"),
    }
    bg, fg = band_bg.get(color, ("rgba(255,255,255,0.05)", "#f0f0f0"))
    st.markdown(
        f'<div class="fvs-block" style="background:{bg}">'
        f'<span class="fvs-num" style="color:{fg}">{emoji} {fvs:.0f}</span>'
        f'<span style="font-size:1em;color:rgba(255,255,255,0.75)">'
        f'<strong>Future Visibility Score</strong> — {label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Expectation signal badge ──────────────────────────────────────────────
    exp_sig  = analysis.get("expectationSignal", company.get("expectationSignal", "UNKNOWN"))
    exp_clr  = _EXP_COLORS.get(exp_sig, "#6c757d")
    exp_icons = {"BEAT": "✅", "MISS": "❌", "MIXED": "🔶", "UNKNOWN": "—"}
    ai_exp   = analysis.get("aiExplanation", company.get("aiExplanation", ""))
    ai_exp_html = (
        f'<span style="font-size:0.84em;color:rgba(255,255,255,0.55);margin-left:4px">{ai_exp}</span>'
        if ai_exp else ""
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap">'
        f'{_badge(exp_icons.get(exp_sig,"") + " Expectation: " + exp_sig, exp_clr)}'
        f'{ai_exp_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── 4 score bars ─────────────────────────────────────────────────────────
    scores = [
        ("Growth",     analysis.get("growthScore",     0)),
        ("Risk",       analysis.get("riskScore",       0)),
        ("Visibility", analysis.get("visibilityScore", 0)),
        ("Conviction", analysis.get("convictionScore", 0)),
    ]
    cols = st.columns(4)
    for col, (lbl, val) in zip(cols, scores):
        col.metric(lbl, f"{float(val):.1f} / 10")
        col.progress(int(min(max(float(val), 0), 10) * 10))

    st.markdown("---")

    # ── Investment thesis ─────────────────────────────────────────────────────
    thesis = analysis.get("thesis", "")
    if thesis:
        st.markdown(
            f'<div class="thesis-box">'
            f'<div style="font-weight:700;margin-bottom:6px;font-size:0.78em;'
            f'text-transform:uppercase;letter-spacing:0.07em;color:#00e676">Investment Thesis</div>'
            f'{thesis}</div>',
            unsafe_allow_html=True,
        )

    # ── Bull / Base / Bear ────────────────────────────────────────────────────
    bc, mc2, br = st.columns(3)
    with bc:
        st.markdown(
            f'<div class="case-card case-bull">'
            f'<div class="case-hdr" style="color:#00e676">🐂 Bull Case</div>'
            f'{analysis.get("bullCase", "—")}</div>',
            unsafe_allow_html=True,
        )
    with mc2:
        st.markdown(
            f'<div class="case-card case-base">'
            f'<div class="case-hdr" style="color:#ffd740">📊 Base Case</div>'
            f'{analysis.get("baseCase", "—")}</div>',
            unsafe_allow_html=True,
        )
    with br:
        st.markdown(
            f'<div class="case-card case-bear">'
            f'<div class="case-hdr" style="color:#ff5252">🐻 Bear Case</div>'
            f'{analysis.get("bearCase", "—")}</div>',
            unsafe_allow_html=True,
        )

    # ── Concentration risk banner ─────────────────────────────────────────────
    conc = analysis.get("concentrationRisk", {})
    if isinstance(conc, dict) and conc.get("flag"):
        sev = conc.get("severity", "MEDIUM")
        detail = conc.get("detail", "")
        c_b = {
            "HIGH":   ("#ff5252", "rgba(255,82,82,0.07)"),
            "MEDIUM": ("#ff9800", "rgba(255,152,0,0.07)"),
            "LOW":    ("#ffd740", "rgba(255,215,64,0.07)"),
        }
        border, cbg = c_b.get(sev, ("#ff9800", "rgba(255,152,0,0.07)"))
        st.markdown(
            f'<div style="border-left:3px solid {border};padding:10px 16px;'
            f'background:{cbg};border-radius:0 8px 8px 0;margin-bottom:12px">'
            f'<strong style="color:{border}">Concentration Risk — {sev}</strong><br>'
            f'<span style="font-size:0.87em">{detail}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Multi-DMA Technical Confirmation ─────────────────────────────────────
    _render_technical_section(company, analysis)

    st.markdown("---")

    # ── Expectation Intelligence section ─────────────────────────────────────
    _render_expectation_section(analysis)

    st.markdown("---")

    # ── Signal Intelligence Grid ──────────────────────────────────────────────
    st.markdown("#### Signal Intelligence")
    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown("**Management & Execution**")
        mc = analysis.get("managementConsistencyScore")
        if mc is not None:
            st.metric("Management Consistency", f"{float(mc):.1f} / 10")
        for ev in analysis.get("managementConsistencyEvidence", [])[:2]:
            st.caption(f"• {ev}")
        st.markdown("**Concall Sentiment**")
        cs = analysis.get("concallSentiment", "neutral")
        st.markdown(_badge(cs.title(), _SENTIMENT_COLORS.get(cs, "#6c757d")),
                    unsafe_allow_html=True)
        tone_kw = analysis.get("concallToneKeywords", [])
        if tone_kw:
            st.caption(", ".join(tone_kw[:4]))

    with s2:
        st.markdown("**Growth Signals**")
        capex  = analysis.get("capexExpansionDetected", False)
        export = analysis.get("exportOpportunity", False)
        st.markdown(
            _pill(capex, "Capex Expansion", "No Capex Signal") + "&nbsp;&nbsp;" +
            _pill(export, "Export Opp.", "Domestic Focus"),
            unsafe_allow_html=True,
        )
        if analysis.get("capexKeywords"):
            st.caption("Keywords: " + ", ".join(analysis["capexKeywords"][:3]))
        if analysis.get("exportCommentary"):
            st.caption(analysis["exportCommentary"])

    with s3:
        st.markdown("**Ownership Signals**")
        pb = analysis.get("promoterBehaviour", "neutral")
        st.markdown("Promoter: " + _badge(pb.title(), _PROMOTER_COLORS.get(pb, "#6c757d")),
                    unsafe_allow_html=True)
        inst = analysis.get("institutionalAccumulation", False)
        st.markdown("Institutional: " + _pill(inst, "Accumulating", "Not Accumulating"),
                    unsafe_allow_html=True)
        if analysis.get("institutionalTrend"):
            st.caption(analysis["institutionalTrend"])

    st.markdown("---")

    # ── Risks + insights ──────────────────────────────────────────────────────
    left, right = st.columns(2)
    with left:
        st.markdown("**Key Risks**")
        for risk in analysis.get("risks", []):
            st.markdown(f"- {risk}")
        if analysis.get("workingCapitalStress") and analysis.get("workingCapitalFlags"):
            st.markdown("**Working Capital Stress**")
            for flag in analysis["workingCapitalFlags"]:
                st.markdown(f"- {flag}")
        st.markdown("**Order Book Insight**")
        st.write(analysis.get("orderBookInsight", "—"))
    with right:
        st.markdown("**Technical View**")
        st.write(analysis.get("technicalView", "—"))
        st.markdown("**Key Catalysts**")
        for cat in analysis.get("catalysts", []):
            st.markdown(f"- {cat}")


# ── Technical confirmation section ───────────────────────────────────────────

def _render_technical_section(company: dict, analysis: dict) -> None:
    st.markdown("#### Technical Confirmation")
    trend = company.get("technicalTrend", "UNKNOWN")
    trend_color = _TECH_COLORS.get(trend, "#6c757d")
    trend_label = trend.replace("_", " ").title()
    st.markdown(
        f'<div style="display:inline-block;background:{trend_color};color:#fff;'
        f'padding:4px 14px;border-radius:20px;font-weight:700;margin-bottom:10px">'
        f'{trend_label}</div>',
        unsafe_allow_html=True,
    )

    price = float(company.get("price") or 0)
    dma_cols = st.columns(4)
    for col, (label, key) in zip(dma_cols, [
        ("20 DMA", "dma20"), ("50 DMA", "dma50"),
        ("100 DMA", "dma100"), ("200 DMA", "dma200"),
    ]):
        dma_val = company.get(key)
        above_key = "above" + key.replace("dma", "") + "dma"
        above = company.get(above_key, False)
        if dma_val:
            delta = round(((price / dma_val) - 1) * 100, 1)
            col.metric(
                label,
                f"₹{dma_val:.0f}",
                delta=f"{delta:+.1f}%",
                delta_color="normal" if above else "inverse",
            )
        else:
            col.metric(label, "N/A")

    rs = company.get("relativeStrength")
    vol_trend = company.get("volumeTrend", "NEUTRAL")
    vol_colors = {"ACCUMULATING": "#28a745", "DISTRIBUTING": "#dc3545", "NEUTRAL": "#6c757d"}
    if rs is not None:
        c1, c2 = st.columns(2)
        c1.metric("52-Week Relative Strength", f"{rs:.0f}%",
                  help="0% = 52-week low, 100% = 52-week high")
        c2.markdown(
            f"**Volume Trend:** " +
            _badge(vol_trend, vol_colors.get(vol_trend, "#6c757d")),
            unsafe_allow_html=True,
        )

    # Technical summary sentence
    tech_view = analysis.get("technicalView", "")
    if tech_view:
        st.caption(tech_view)


# ── Expectation Intelligence section ─────────────────────────────────────────

def _render_expectation_section(analysis: dict) -> None:
    st.markdown("#### Expectation Intelligence")
    exp_sig  = analysis.get("expectationSignal", "UNKNOWN")
    exp_clr  = _EXP_COLORS.get(exp_sig, "#6c757d")
    exp_icons = {"BEAT": "✅", "MISS": "❌", "MIXED": "🔶", "UNKNOWN": "—"}

    left, right = st.columns(2)
    with left:
        st.markdown(
            f'**Market Expectation Signal:** '
            f'{_badge(exp_icons.get(exp_sig,"") + " " + exp_sig, exp_clr)}',
            unsafe_allow_html=True,
        )
        gap_summary = analysis.get("expectationGapSummary", "")
        if gap_summary:
            st.caption(gap_summary)

    with right:
        gr_assessment = analysis.get("guidanceReliabilityAssessment", "")
        if gr_assessment:
            st.markdown("**Guidance Reliability**")
            st.caption(gr_assessment)
