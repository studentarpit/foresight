"""Tab 4 — Sentiment & Geopolitical Intelligence Dashboard (Spec 06)."""

import time
from datetime import datetime

import pandas as pd
import streamlit as st

from data.sentiment_engine import fetch_global_cues, fetch_news_headlines, fetch_fii_dii_data
from ai.sentiment_analyzer import (
    analyze_headlines,
    compute_stock_sentiment_scores,
    detect_positional_opportunities,
)

_SECTORS = ["Defence", "Railways", "EPC", "EMS", "Power", "Solar/Wind"]

_SENTIMENT_COLORS = {
    "BULLISH": "#00e676",
    "BEARISH": "#ff5252",
    "NEUTRAL": "#90a4ae",
}

_TIMELINE_COLORS = {
    "NEAR": "#ff9800",
    "MID":  "#ffd740",
    "LONG": "#90a4ae",
}

_SIGNAL_ICONS = {
    "POLICY":    "🏛️",
    "POLITICAL": "👤",
    "MARKET":    "📊",
    "GLOBAL":    "🌐",
    "WAR":       "⚔️",
    "COMMODITY": "🪨",
    "MISC":      "📰",
}

_SCORE_COLOR = {
    (75, 101): "#00e676",  # Strong Tailwind
    (50,  75): "#69f0ae",  # Mild Tailwind
    (40,  50): "#90a4ae",  # Neutral
    (25,  40): "#ff9800",  # Mild Headwind
    (0,   25): "#ff5252",  # Strong Headwind
}

_SCORE_LABEL = {
    (75, 101): "🟢 Tailwind",
    (50,  75): "🟡 Mild +",
    (40,  50): "⚪ Neutral",
    (25,  40): "🟠 Headwind",
    (0,   25): "🔴 Risk",
}


def _score_color(score: float) -> str:
    for (lo, hi), color in _SCORE_COLOR.items():
        if lo <= score < hi:
            return color
    return "#90a4ae"


def _score_label(score: float) -> str:
    for (lo, hi), label in _SCORE_LABEL.items():
        if lo <= score < hi:
            return label
    return "⚪ Neutral"


# ── Positional alert banner ───────────────────────────────────────────────────

def _render_positional_alerts(opportunities: list[dict]) -> None:
    """Full-width red banner per positional opportunity."""
    for opp in opportunities:
        ticker = opp.get("ticker", "?")
        direction = opp.get("direction", "LONG")
        entry_l = opp.get("entry_low", "—")
        entry_h = opp.get("entry_high", "—")
        target  = opp.get("target", "—")
        sl      = opp.get("stoploss", "—")
        days    = opp.get("timeframe_days", "?")
        conf    = opp.get("confidence", "?")
        trigger = opp.get("trigger_signal", "")[:80]
        disc    = opp.get("disclaimer", "Not investment advice. DYOR.")

        st.markdown(
            f'<div style="background:rgba(255,82,82,0.1);border:1.5px solid #ff5252;'
            f'border-radius:12px;padding:18px 24px;margin-bottom:16px">'
            f'<div style="font-size:1em;font-weight:700;color:#ff5252;margin-bottom:8px">'
            f'🚨 POSITIONAL OPPORTUNITY — {ticker}</div>'
            f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;'
            f'font-family:\'DM Mono\',monospace;font-size:0.82em;margin-bottom:10px">'
            f'<div><div style="color:rgba(255,255,255,0.4)">Direction</div>'
            f'<div style="color:#ff5252;font-weight:700">{direction}</div></div>'
            f'<div><div style="color:rgba(255,255,255,0.4)">Entry Zone</div>'
            f'<div style="color:#f0f0f0">₹{entry_l}–{entry_h}</div></div>'
            f'<div><div style="color:rgba(255,255,255,0.4)">Target</div>'
            f'<div style="color:#00e676;font-weight:700">₹{target}</div></div>'
            f'<div><div style="color:rgba(255,255,255,0.4)">Stop Loss</div>'
            f'<div style="color:#ff9800">₹{sl}</div></div>'
            f'<div><div style="color:rgba(255,255,255,0.4)">Timeframe</div>'
            f'<div style="color:#f0f0f0">{days}d · {conf}% conf</div></div>'
            f'</div>'
            f'<div style="font-size:0.78em;color:rgba(255,255,255,0.5);margin-bottom:4px">'
            f'Trigger: {trigger}</div>'
            f'<div style="font-size:0.72em;color:rgba(255,255,255,0.3)">{disc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Global cues strip ─────────────────────────────────────────────────────────

def _render_global_cues(cues: dict) -> None:
    """Horizontal strip of real-time global market indicators."""
    fetched = cues.pop("_fetched_at", "—")
    st.markdown(
        f'<div style="font-size:0.7em;color:rgba(255,255,255,0.3);'
        f'margin-bottom:4px">GLOBAL CUES · updated {fetched}</div>',
        unsafe_allow_html=True,
    )

    pills_html = '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px">'
    for key, data in cues.items():
        if not isinstance(data, dict):
            continue
        val    = data.get("value", 0)
        chg    = data.get("change_pct", 0)
        label  = data.get("label", key)
        icon   = data.get("icon", "")
        prefix = data.get("prefix", "")
        suffix = data.get("suffix", "")
        color  = "#00e676" if chg >= 0 else "#ff5252"
        arrow  = "▲" if chg >= 0 else "▼"

        # Format value based on magnitude
        if val >= 10_000:
            val_str = f"{val:,.0f}"
        elif val >= 100:
            val_str = f"{val:,.1f}"
        else:
            val_str = f"{val:.2f}"

        pills_html += (
            f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.08);'
            f'border-radius:8px;padding:8px 14px;min-width:110px">'
            f'<div style="font-size:0.72em;color:rgba(255,255,255,0.4)">{icon} {label}</div>'
            f'<div style="font-size:0.95em;font-weight:700;color:#f0f0f0;'
            f'font-family:\'DM Mono\',monospace">{prefix}{val_str}{suffix}</div>'
            f'<div style="font-size:0.72em;color:{color}">{arrow} {abs(chg):.2f}%</div>'
            f'</div>'
        )
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)


# ── FII / DII strip ───────────────────────────────────────────────────────────

def _render_fii_dii(fii_data: dict) -> None:
    fii = fii_data.get("fii_net")
    dii = fii_data.get("dii_net")
    if fii is None and dii is None:
        return

    def _pill(label: str, val: Optional[float]) -> str:
        if val is None:
            return ""
        color  = "#00e676" if val >= 0 else "#ff5252"
        arrow  = "▲ Net Buy" if val >= 0 else "▼ Net Sell"
        return (
            f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.08);'
            f'border-radius:8px;padding:8px 16px">'
            f'<div style="font-size:0.72em;color:rgba(255,255,255,0.4)">{label}</div>'
            f'<div style="font-size:0.9em;font-weight:700;color:{color};'
            f'font-family:\'DM Mono\',monospace">₹{abs(val):,.0f} Cr</div>'
            f'<div style="font-size:0.72em;color:{color}">{arrow}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div style="display:flex;gap:10px;margin-bottom:20px">'
        f'{_pill("FII / FPI Today", fii)}{_pill("DII Today", dii)}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Sentiment heatmap ─────────────────────────────────────────────────────────

def _render_heatmap(scores: dict[str, float]) -> None:
    """Grid of all stocks colored by sentiment score."""
    st.markdown('<div style="font-size:0.7em;color:rgba(255,255,255,0.35);'
                'letter-spacing:0.1em;margin-bottom:8px">SENTIMENT HEATMAP</div>',
                unsafe_allow_html=True)

    tickers = sorted(scores.keys())
    cols = st.columns(5)
    for i, ticker in enumerate(tickers):
        score = scores[ticker]
        color = _score_color(score)
        label = _score_label(score)
        with cols[i % 5]:
            st.markdown(
                f'<div style="background:rgba({_hex_rgb(color)},0.12);'
                f'border:1px solid {color}40;border-radius:8px;'
                f'padding:10px 8px;text-align:center;margin-bottom:8px">'
                f'<div style="font-weight:700;font-size:0.82em;'
                f'font-family:\'DM Mono\',monospace;color:#f0f0f0">{ticker}</div>'
                f'<div style="font-size:1.1em;font-weight:700;color:{color}">{score:.0f}</div>'
                f'<div style="font-size:0.65em;color:{color}">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _hex_rgb(hex_color: str) -> str:
    """Convert #rrggbb to 'r,g,b' string for rgba()."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"
    return "255,255,255"


# ── Signal feed ───────────────────────────────────────────────────────────────

def _render_signal_feed(signals: list[dict], filter_sector: str, filter_sentiment: str) -> None:
    """Chronological feed of detected signals with filters."""
    filtered = signals
    if filter_sector != "All":
        filtered = [s for s in filtered if filter_sector in s.get("affected_sectors", [])]
    if filter_sentiment != "All":
        filtered = [s for s in filtered if s.get("sentiment") == filter_sentiment]

    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:40px;color:rgba(255,255,255,0.3)">'
            'No signals match the current filters</div>',
            unsafe_allow_html=True,
        )
        return

    for sig in filtered[:25]:
        s_type   = sig.get("signal_type", "MISC")
        headline = sig.get("headline", "")[:120]
        sentiment= sig.get("sentiment", "NEUTRAL")
        timeline = sig.get("impact_timeline", "MID")
        magnitude= sig.get("impact_magnitude", "LOW")
        conf     = sig.get("confidence", 0)
        sectors  = sig.get("affected_sectors", [])
        stocks   = sig.get("affected_stocks", [])
        source   = sig.get("source", "")
        reasoning= sig.get("reasoning", "")[:160]

        s_color  = _SENTIMENT_COLORS.get(sentiment, "#90a4ae")
        t_color  = _TIMELINE_COLORS.get(timeline, "#90a4ae")
        icon     = _SIGNAL_ICONS.get(s_type, "📰")
        mag_star = "●●●" if magnitude == "HIGH" else "●●○" if magnitude == "MEDIUM" else "●○○"
        stocks_html = "".join(
            f'<span style="background:rgba(0,230,118,0.1);color:#00e676;'
            f'border-radius:4px;padding:1px 6px;font-size:0.72em;'
            f'font-family:\'DM Mono\',monospace;margin-right:4px">{t}</span>'
            for t in stocks[:6]
        )

        st.markdown(
            f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.06);'
            f'border-left:3px solid {s_color};border-radius:8px;'
            f'padding:14px 16px;margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:flex-start;margin-bottom:8px">'
            f'<div style="font-size:0.9em;font-weight:600;color:#f0f0f0;flex:1">'
            f'{icon} {headline}</div>'
            f'<div style="display:flex;gap:6px;margin-left:12px;flex-shrink:0">'
            f'<span style="background:{s_color}22;color:{s_color};'
            f'border-radius:4px;padding:2px 8px;font-size:0.72em">{sentiment}</span>'
            f'<span style="background:{t_color}22;color:{t_color};'
            f'border-radius:4px;padding:2px 8px;font-size:0.72em">{timeline}</span>'
            f'<span style="color:rgba(255,255,255,0.3);font-size:0.72em">{mag_star}</span>'
            f'</div></div>'
            f'<div style="margin-bottom:6px">{stocks_html}</div>'
            f'<div style="font-size:0.78em;color:rgba(255,255,255,0.4);margin-bottom:4px">'
            f'{reasoning}</div>'
            f'<div style="font-size:0.7em;color:rgba(255,255,255,0.25)">'
            f'{source} · {conf}% confidence</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Sector sentiment summary ──────────────────────────────────────────────────

def _render_sector_summary(signals: list[dict]) -> None:
    """6 sector cards with aggregated sentiment."""
    sector_data: dict[str, dict] = {s: {"bull": 0, "bear": 0, "top": "", "risk": ""} for s in _SECTORS}

    for sig in signals:
        sent = sig.get("sentiment", "NEUTRAL")
        headline = sig.get("headline", "")
        for sector in sig.get("affected_sectors", []):
            if sector not in sector_data:
                continue
            if sent == "BULLISH":
                sector_data[sector]["bull"] += 1
                if not sector_data[sector]["top"]:
                    sector_data[sector]["top"] = headline[:70]
            elif sent == "BEARISH":
                sector_data[sector]["bear"] += 1
                if not sector_data[sector]["risk"]:
                    sector_data[sector]["risk"] = headline[:70]

    cols = st.columns(3)
    for i, sector in enumerate(_SECTORS):
        d = sector_data[sector]
        bull, bear = d["bull"], d["bear"]
        total = bull + bear
        score = round((bull / total) * 100) if total else 50
        color = _score_color(score)
        label = _score_label(score)

        with cols[i % 3]:
            st.markdown(
                f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.06);'
                f'border-top:2px solid {color};border-radius:8px;padding:14px;margin-bottom:12px">'
                f'<div style="font-weight:700;font-size:0.85em;color:#f0f0f0;'
                f'margin-bottom:4px">{sector}</div>'
                f'<div style="font-size:1.3em;font-weight:700;color:{color}">{score}</div>'
                f'<div style="font-size:0.72em;color:{color};margin-bottom:8px">{label}</div>'
                f'<div style="font-size:0.72em;color:rgba(255,255,255,0.35);margin-bottom:4px">'
                f'🟢 {bull} bullish · 🔴 {bear} bearish signals</div>'
                + (f'<div style="font-size:0.7em;color:rgba(255,255,255,0.4);margin-top:6px">'
                   f'↑ {d["top"][:60]}</div>' if d["top"] else "")
                + (f'<div style="font-size:0.7em;color:#ff5252;margin-top:4px">'
                   f'⚠ {d["risk"][:60]}</div>' if d["risk"] else "")
                + f'</div>',
                unsafe_allow_html=True,
            )


# ── Data loader with auto-refresh ─────────────────────────────────────────────

def _load_sentiment_data(scan_df) -> tuple[dict, list, list, dict]:
    """Return (cues, signals, opportunities, scores). Refreshes stale data automatically."""
    ss = st.session_state

    now = time.time()
    last_news = ss.get("sentiment_news_ts", 0)
    last_cues = ss.get("sentiment_cues_ts", 0)
    news_stale = (now - last_news) > 1_800   # 30 min
    cues_stale = (now - last_cues) > 900     # 15 min

    if cues_stale or "sentiment_cues" not in ss:
        with st.spinner("Fetching global cues…"):
            ss["sentiment_cues"]    = fetch_global_cues()
            ss["sentiment_cues_ts"] = now

    if news_stale or "sentiment_signals" not in ss:
        with st.spinner("Fetching & analysing news signals…"):
            tickers = list(scan_df["ticker"]) if scan_df is not None and not scan_df.empty else []
            headlines = fetch_news_headlines()
            signals   = analyze_headlines(headlines, tickers)
            scores    = compute_stock_sentiment_scores(signals, tickers)
            opps      = detect_positional_opportunities(signals, scan_df)

            ss["sentiment_signals"]    = signals
            ss["sentiment_scores"]     = scores
            ss["sentiment_opps"]       = opps
            ss["sentiment_fii"]        = fetch_fii_dii_data()
            ss["sentiment_news_ts"]    = now

    cues   = ss.get("sentiment_cues", {})
    signals= ss.get("sentiment_signals", [])
    opps   = ss.get("sentiment_opps", [])
    scores = ss.get("sentiment_scores", {})
    return cues, signals, opps, scores


# ── Main render ───────────────────────────────────────────────────────────────

def render_sentiment_tab(scan_df=None) -> None:
    """Render Tab 4 — Sentiment & Geopolitical Intelligence."""
    cues, signals, opps, scores = _load_sentiment_data(scan_df)

    # Positional alert banner (top of page)
    if opps:
        _render_positional_alerts(opps)

    # Global cues strip
    _render_global_cues(dict(cues))

    # FII / DII strip
    fii_data = st.session_state.get("sentiment_fii", {})
    if fii_data:
        _render_fii_dii(fii_data)

    # Manual refresh button
    col_r, _ = st.columns([1, 5])
    if col_r.button("↺ Refresh Now", key="sent_refresh"):
        for k in ["sentiment_signals", "sentiment_cues", "sentiment_news_ts",
                  "sentiment_cues_ts", "sentiment_scores", "sentiment_opps"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);"
                "margin:8px 0 20px'>", unsafe_allow_html=True)

    # Two-column layout: heatmap | feed
    col_left, col_right = st.columns([1.4, 2])

    with col_left:
        if scores:
            _render_heatmap(scores)

        st.markdown("<div style='margin-top:24px'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.7em;color:rgba(255,255,255,0.35);'
                    'letter-spacing:0.1em;margin-bottom:12px">SECTOR OUTLOOK</div>',
                    unsafe_allow_html=True)
        if signals:
            _render_sector_summary(signals)
        else:
            st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:0.85em">'
                        'No signals yet.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div style="font-size:0.7em;color:rgba(255,255,255,0.35);'
                    'letter-spacing:0.1em;margin-bottom:8px">SIGNAL FEED</div>',
                    unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        filter_sector    = fc1.selectbox("Sector", ["All"] + _SECTORS,
                                          key="sent_sector_filter",
                                          label_visibility="collapsed")
        filter_sentiment = fc2.selectbox("Sentiment", ["All", "BULLISH", "BEARISH", "NEUTRAL"],
                                          key="sent_sent_filter",
                                          label_visibility="collapsed")

        n_signals = len(signals)
        bull = sum(1 for s in signals if s.get("sentiment") == "BULLISH")
        bear = sum(1 for s in signals if s.get("sentiment") == "BEARISH")
        st.markdown(
            f'<div style="font-size:0.78em;color:rgba(255,255,255,0.4);margin-bottom:12px">'
            f'{n_signals} signals · '
            f'<span style="color:#00e676">{bull} bullish</span> · '
            f'<span style="color:#ff5252">{bear} bearish</span></div>',
            unsafe_allow_html=True,
        )

        _render_signal_feed(signals, filter_sector, filter_sentiment)

    # ── Spec 07: Bulk/block deal feed + FII/DII flow heatmap ──────────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);"
                "margin:20px 0 16px'>", unsafe_allow_html=True)

    tickers = list(scan_df["ticker"]) if scan_df is not None and not scan_df.empty else []

    col_deals, col_heat = st.columns([1.4, 2])
    with col_deals:
        _render_bulk_deal_feed()
    with col_heat:
        _render_flow_heatmap(tickers)


# ── Spec 07: Bulk deal feed ───────────────────────────────────────────────────

def _render_bulk_deal_feed() -> None:
    """Bulk/block deal feed for Sentiment tab."""
    st.markdown('<div style="font-size:0.7em;color:rgba(255,255,255,0.35);'
                'letter-spacing:0.1em;margin-bottom:10px">BULK / BLOCK DEALS</div>',
                unsafe_allow_html=True)
    try:
        from data.fii_dii_engine import _fetch_market_bulk_deals
        deals = _fetch_market_bulk_deals()
    except Exception:
        deals = []

    if not deals:
        st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:0.82em">'
                    'No bulk deal data available right now.</div>',
                    unsafe_allow_html=True)
        return

    for d in deals[:12]:
        side   = (d.get("side") or "").upper()
        ticker = d.get("ticker", "?")
        client = d.get("client", "Unknown")[:30]
        val_cr = d.get("value_cr", 0)
        price  = d.get("price", 0)
        date   = d.get("date", "")
        etype  = d.get("entity_type", "UNKNOWN")

        side_color = "#00e676" if side in ("B", "BUY") else "#ff5252"
        side_label = "BUY" if side in ("B", "BUY") else "SELL"
        etype_icon = {"FII": "🏦", "DII": "🏛️", "MF": "📈", "HNI": "💼"}.get(etype, "❓")

        st.markdown(
            f'<div style="background:#12121a;border:1px solid rgba(255,255,255,0.07);'
            f'border-radius:8px;padding:8px 12px;margin-bottom:6px;font-size:0.78rem">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-weight:700;color:#f0f0f0">{ticker}</span>'
            f'<span style="color:{side_color};font-weight:700;font-size:0.85em">{side_label}</span>'
            f'</div>'
            f'<div style="opacity:0.7;margin:2px 0">{etype_icon} {client}</div>'
            f'<div style="display:flex;justify-content:space-between;opacity:0.6;font-size:0.75em">'
            f'<span>₹{val_cr:,.1f} Cr @ ₹{price}</span>'
            f'<span>{date}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Spec 07: Flow heatmap ─────────────────────────────────────────────────────

_FLOW_COLORS = [
    (80, "🟢", "#00e676", "Heavy Acc"),
    (60, "🟡", "#ffd740", "Mild Acc"),
    (40, "⚪", "#90a4ae", "Neutral"),
    (20, "🟠", "#ff9800", "Mild Dist"),
    (0,  "🔴", "#ff5252", "Heavy Dist"),
]


def _flow_chip(score: int) -> tuple[str, str, str]:
    """Return (emoji, color, label) for a flow score."""
    for threshold, emoji, color, label in _FLOW_COLORS:
        if score >= threshold:
            return emoji, color, label
    return "🔴", "#ff5252", "Heavy Dist"


def _render_flow_heatmap(tickers: list[str]) -> None:
    """FII/DII flow heatmap grid for all tracked stocks."""
    st.markdown('<div style="font-size:0.7em;color:rgba(255,255,255,0.35);'
                'letter-spacing:0.1em;margin-bottom:10px">FII/DII FLOW HEATMAP</div>',
                unsafe_allow_html=True)

    if not tickers:
        st.markdown('<div style="color:rgba(255,255,255,0.3);font-size:0.82em">'
                    'Run a scan first to see flow heatmap.</div>',
                    unsafe_allow_html=True)
        return

    try:
        from data.fii_dii_engine import compute_flow_score, flow_score_label
    except Exception as exc:
        st.warning(f"Flow heatmap unavailable: {exc}")
        return

    # Build score cards in a grid (4 per row)
    cols_per_row = 4
    ticker_chunks = [tickers[i:i + cols_per_row] for i in range(0, len(tickers), cols_per_row)]

    for chunk in ticker_chunks:
        grid_cols = st.columns(cols_per_row)
        for col, t in zip(grid_cols, chunk):
            try:
                score = compute_flow_score(t)
            except Exception:
                score = None

            if score is None:
                col.markdown(
                    f'<div style="background:#12121a;border:1px solid #333;'
                    f'border-radius:8px;padding:8px;text-align:center;font-size:0.75rem">'
                    f'<div style="font-weight:700;color:#f0f0f0">{t}</div>'
                    f'<div style="font-size:1.1em">⚪</div>'
                    f'<div style="color:#555;font-weight:600">N/A</div>'
                    f'<div style="opacity:0.4;font-size:0.68rem">No data</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                continue

            emoji, color, label = _flow_chip(score)
            col.markdown(
                f'<div style="background:#12121a;border:1px solid {color}40;'
                f'border-radius:8px;padding:8px;text-align:center;font-size:0.75rem">'
                f'<div style="font-weight:700;color:#f0f0f0">{t}</div>'
                f'<div style="font-size:1.1em">{emoji}</div>'
                f'<div style="color:{color};font-weight:600">{score}</div>'
                f'<div style="opacity:0.55;font-size:0.68rem">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
