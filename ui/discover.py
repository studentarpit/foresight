"""Tab 1 — Discover: hero strip, alert banner, cap class selector, heat leaderboard, card grid."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai.fvs import fvs_band, fvs_emoji
from ai.heat_engine import compute_heat_score, heat_level
from data.quarterly_fetcher import fetch_quarterly_data
from ui.filters import add_signal_column, apply_filters
from ui.components import SECTOR_COLORS, SIGNAL_BORDER, hex_to_rgb, smart_money_card_html
from data.fii_dii_engine import detect_accumulation_distribution, compute_flow_score, prefetch_flow_data_batch

_SECTORS    = ["Defence", "Railways", "EPC", "EMS", "Power", "Solar/Wind"]
_CAP_CLASSES = ["Large", "Mid", "Small", "Penny"]

_fvs_band = fvs_band  # local alias


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt(v, suffix="%"):
    """Format a numeric value or return '—'."""
    return f"{v:.1f}{suffix}" if v is not None and not (isinstance(v, float) and pd.isna(v)) else "—"


def _get_quarterly(ticker: str) -> dict:
    """Return quarterly data from session cache, fetching if absent."""
    cache = st.session_state.setdefault("quarterly_cache", {})
    if ticker not in cache:
        cache[ticker] = fetch_quarterly_data(ticker)
    return cache[ticker]


def _heat_for_row(row: dict) -> float:
    """Compute (and cache) heat score for one company row."""
    cache  = st.session_state.setdefault("heat_cache", {})
    ticker = row.get("ticker", "")
    if ticker not in cache:
        qd            = _get_quarterly(ticker)
        cache[ticker] = compute_heat_score(qd, row)
    return cache[ticker]


def _sparkline(values: list, color: str) -> go.Figure:
    """Tiny 40px sparkline — no axes, no margins."""
    clean = [v for v in values if v is not None]
    fig   = go.Figure()
    if len(clean) >= 2:
        fig.add_trace(go.Scatter(
            y=clean, mode="lines",
            line=dict(color=color, width=1.5),
            hoverinfo="skip",
        ))
    fig.update_layout(
        height=40, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


# ── Section renderers ──────────────────────────────────────────────────────────

def _render_hero_strip() -> None:
    """Full-width hero banner shown only before the first scan."""
    if st.session_state.get("_hero_dismissed"):
        return
    st.markdown(
        '<div style="background:linear-gradient(135deg,rgba(0,230,118,0.07),'
        'rgba(0,179,74,0.04));border:1px solid rgba(0,230,118,0.18);border-radius:14px;'
        'padding:32px 36px;margin-bottom:24px">'
        '<div style="font-family:\'DM Serif Display\',serif;font-size:1.9em;font-weight:400;'
        'margin-bottom:10px;color:#f0f0f0">Find your next compounder<br>'
        '<span style="color:#00e676">before the market does</span></div>'
        '<div style="font-size:0.88em;color:rgba(255,255,255,0.55);max-width:580px;'
        'line-height:1.7;margin-bottom:20px">AI scans 20 high-quality companies across '
        '6 sectors, pulls balance sheets, order books, and management guidance '
        'automatically. You just pick your bets.</div>'
        '<div style="font-size:0.75em;color:rgba(255,255,255,0.3);'
        'font-family:\'DM Mono\',monospace">'
        '⚡ Click <strong style="color:#00e676">Run AI Scan</strong> in the header '
        '— takes ~60 seconds</div></div>',
        unsafe_allow_html=True,
    )


def _render_alert_banner(alerts: list) -> None:
    """Collapsible alert banner sorted by priority."""
    if not alerts:
        return
    high  = [a for a in alerts if a.get("priority") == 1]
    rest  = [a for a in alerts if a.get("priority") != 1]
    items = (high + rest)[:15]

    label = f"🔔 {len(items)} Alert{'s' if len(items) != 1 else ''}"
    if high:
        label += f" — {len(high)} high priority"

    with st.expander(label, expanded=len(high) > 0):
        for alert in items:
            priority  = alert.get("priority", 3)
            atype     = alert.get("type", "")
            cls       = "alert-high" if priority == 1 else "alert-med"
            icon      = alert.get("icon", "ℹ️")
            ticker    = alert.get("ticker", "")
            msg       = alert.get("message", "")
            if atype == "SMART_MONEY_ACCUMULATION":
                st.markdown(
                    f'<div class="alert-row" style="border-left:3px solid #00bcd4;'
                    f'background:rgba(0,188,212,0.06);padding:8px 14px;border-radius:6px;'
                    f'display:flex;gap:8px;align-items:center;margin-bottom:4px">'
                    f'<span style="min-width:26px">{icon}</span>'
                    f'<span style="font-weight:700;min-width:70px;color:#00bcd4;'
                    f'font-family:\'DM Mono\',monospace">{ticker}</span>'
                    f'<span style="color:rgba(255,255,255,0.75)">{msg}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="alert-row {cls}">'
                    f'<span style="min-width:26px">{icon}</span>'
                    f'<span style="font-weight:700;min-width:70px;'
                    f'font-family:\'DM Mono\',monospace">{ticker}</span>'
                    f'<span style="color:rgba(255,255,255,0.7)">{msg}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def _render_cap_class_selector(df: pd.DataFrame) -> str:
    """4 large toggle buttons for cap class. Returns the active class string."""
    active = st.session_state.get("cap_class_filter", "Large")
    counts = {
        cls: int((df["capClass"] == cls).sum()) if "capClass" in df.columns else 0
        for cls in _CAP_CLASSES
    }
    labels = {"Large": "🏦 Large Cap", "Mid": "📈 Mid Cap",
              "Small": "🔬 Small Cap", "Penny": "💎 Penny"}
    for col, cls in zip(st.columns(4), _CAP_CLASSES):
        n        = counts.get(cls, 0)
        is_active = cls == active
        bg     = "rgba(0,230,118,0.12)" if is_active else "rgba(255,255,255,0.03)"
        border = "#00e676" if is_active else "rgba(255,255,255,0.08)"
        color  = "#00e676" if is_active else "rgba(255,255,255,0.55)"
        col.markdown(
            f'<div style="background:{bg};border:1.5px solid {border};border-radius:10px;'
            f'padding:14px 10px;text-align:center;cursor:pointer;margin-bottom:4px">'
            f'<div style="font-weight:700;font-size:0.9em;color:{color}">{labels[cls]}</div>'
            f'<div style="font-size:0.68em;color:rgba(255,255,255,0.3);margin-top:4px;'
            f'font-family:\'DM Mono\',monospace">'
            f'{"Scanning…" if n == 0 else f"{n} companies"}</div></div>',
            unsafe_allow_html=True,
        )
        if col.button(f"Select {cls}", key=f"cap_btn_{cls}",
                      use_container_width=True, help=f"Show {cls} Cap companies"):
            st.session_state["cap_class_filter"] = cls
            st.rerun()
    return st.session_state.get("cap_class_filter", "Large")


def _render_filter_bar(df: pd.DataFrame) -> dict:
    """Compact single-row horizontal filter bar."""
    c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.2, 1.2, 1.2, 1.0, 0.8])
    with c1:
        sectors = st.multiselect("Sector", _SECTORS,
                                 default=st.session_state.get("disc_sectors", _SECTORS),
                                 key="disc_sectors", placeholder="All Sectors",
                                 label_visibility="collapsed")
    with c2:
        ob_trend = st.selectbox("Order Trend", ["All", "ACCELERATING", "STABLE", "DECLINING"],
                                key="disc_ob", label_visibility="collapsed")
    with c3:
        signal = st.selectbox("Signal", ["All", "Strong Buy", "Watch", "Neutral", "Avoid"],
                              key="disc_signal", label_visibility="collapsed")
    with c4:
        exp = st.selectbox("Expectation", ["All", "BEAT", "MIXED", "MISS"],
                           key="disc_exp", label_visibility="collapsed")
    with c5:
        min_fvs = st.slider("Min FVS", 0, 100, 0, 5, key="disc_fvs",
                             label_visibility="collapsed")
    with c6:
        if st.button("↺ Reset", key="disc_reset", use_container_width=True):
            for k in ["disc_sectors", "disc_ob", "disc_signal", "disc_exp", "disc_fvs"]:
                st.session_state.pop(k, None)
            st.rerun()
    return {
        "sectors":    sectors or _SECTORS,
        "ob_trend":   ob_trend,
        "signal":     signal,
        "exp_signal": exp,
        "min_fvs":    min_fvs,
    }


def _apply_discover_filters(df: pd.DataFrame, cap_class: str, filters: dict) -> pd.DataFrame:
    """Filter DataFrame by cap class and all inline filter bar values."""
    result = df.copy()
    if "capClass" in result.columns:
        result = result[result["capClass"] == cap_class]
    sectors = filters.get("sectors", _SECTORS)
    if sectors:
        result = result[result["sector"].isin(sectors)]
    ob = filters.get("ob_trend", "All")
    if ob and ob != "All" and "orderBookTrend" in result.columns:
        result = result[result["orderBookTrend"] == ob]
    sig = filters.get("signal", "All")
    if sig and sig != "All" and "Signal" in result.columns:
        result = result[result["Signal"].str.contains(sig, na=False)]
    exp = filters.get("exp_signal", "All")
    if exp and exp != "All" and "expectationSignal" in result.columns:
        result = result[result["expectationSignal"] == exp]
    min_fvs = filters.get("min_fvs", 0)
    if min_fvs and min_fvs > 0 and "fvs" in result.columns:
        result = result[result["fvs"] >= min_fvs]
    return result


def _prefetch_quarterly_batch(tickers: list) -> None:
    """Parallel-fetch quarterly data for uncached tickers, 4 workers max."""
    cache  = st.session_state.setdefault("quarterly_cache", {})
    needed = [t for t in tickers if t not in cache]
    if not needed:
        return
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_quarterly_data, t): t for t in needed}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                cache[ticker] = future.result()
            except Exception:
                cache[ticker] = {}


def _render_heat_leaderboard(df: pd.DataFrame) -> None:
    """Horizontal scroll strip — top 5 heating + bottom 3 cooling companies."""
    if df.empty:
        return
    df = df.copy()
    df["_heat"] = [_heat_for_row(r.to_dict()) for _, r in df.iterrows()]
    df_sorted = df.sort_values("_heat", ascending=False).reset_index(drop=True)

    top5    = df_sorted.head(5).to_dict(orient="records")
    bottom3 = df_sorted.tail(3).sort_values("_heat").to_dict(orient="records") \
              if len(df_sorted) >= 3 else []

    st.markdown('<div class="section-lbl">🔥 HEAT LEADERBOARD</div>', unsafe_allow_html=True)

    cards_html = '<div class="heat-strip">'
    for rank, row in enumerate(top5, 1):
        hs      = row.get("_heat", 50)
        lbl, em = heat_level(hs)
        qd      = _get_quarterly(row.get("ticker", ""))
        rev_qoq = qd.get("revenue_qoq_growth", [])
        valid_g = [g for g in rev_qoq if g is not None]
        meta    = f"Rev {valid_g[-1]:+.0f}% QoQ" if valid_g else ""
        cards_html += (
            f'<div class="heat-card heat-card-hot">'
            f'<div class="heat-rank">#{rank} {em}</div>'
            f'<div class="heat-ticker">{row.get("ticker","")}</div>'
            f'<div class="heat-name">{row.get("name","")[:22]}</div>'
            f'<div class="heat-score">{hs:.0f} <span class="heat-label">{lbl}</span></div>'
            f'<div class="heat-meta">{meta}</div>'
            f'</div>'
        )

    if bottom3:
        cards_html += '<div class="heat-divider"></div>'
        for row in bottom3:
            hs      = row.get("_heat", 50)
            lbl, em = heat_level(hs)
            cards_html += (
                f'<div class="heat-card heat-card-cold">'
                f'<div class="heat-rank">❄️ {em}</div>'
                f'<div class="heat-ticker">{row.get("ticker","")}</div>'
                f'<div class="heat-name">{row.get("name","")[:22]}</div>'
                f'<div class="heat-score">{hs:.0f} <span class="heat-label">{lbl}</span></div>'
                f'</div>'
            )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def _render_company_card(rank: int, row: dict, col) -> None:
    """Render one company card in the 2-col grid."""
    ticker   = row.get("ticker", "")
    name     = row.get("name", ticker)
    sector   = row.get("sector", "")
    cap_cls  = row.get("capClass", "")
    signal   = row.get("Signal", "🟠 Neutral")
    fvs      = float(row.get("fvs") or 0)
    conv     = float(row.get("convictionScore") or 0)
    roe      = row.get("roe")
    revcagr  = row.get("revcagr")
    ob_rev   = row.get("orderBookRev")
    ob_trend = row.get("orderBookTrend", "STABLE")
    above200 = row.get("above200dma", False)

    hs, (ht_lbl, ht_emoji) = _heat_for_row(row), heat_level(_heat_for_row(row))
    hs = _heat_for_row(row)
    ht_lbl, ht_emoji = heat_level(hs)

    border_color = SIGNAL_BORDER.get(signal, "#ff9800")
    _, fvs_color = _fvs_band(fvs)
    fvs_hex = {"green": "#00e676", "yellow": "#ffd740",
               "orange": "#ff9800", "red": "#ff5252"}.get(fvs_color, "#f0f0f0")
    fvs_pct = min(100, int(fvs))

    ob_icon  = {"ACCELERATING": "📈", "DECLINING": "📉"}.get(ob_trend, "➡️")
    dma_txt  = "🟢 Above 200DMA" if above200 else "🔴 Below 200DMA"
    sec_clr  = SECTOR_COLORS.get(sector, "#6c757d")

    # Smart money HTML — instant cache hit after prefetch_flow_data_batch
    try:
        _accum      = detect_accumulation_distribution(ticker)
        _flow_score = compute_flow_score(ticker)
        sm_html     = smart_money_card_html(_accum, _flow_score)
    except Exception:
        sm_html = ""

    with col:
        st.markdown(
            f'<div class="company-card" style="border-left:3px solid {border_color}">'
            f'<div class="cc-header">'
            f'<div><span class="cc-rank">#{rank}</span> '
            f'<span class="cc-ticker">{ticker}</span> '
            f'<span class="cc-signal" style="color:{border_color}">{signal}</span></div>'
            f'<div class="cc-heat">{ht_emoji} {hs:.0f}</div>'
            f'</div>'
            f'<div class="cc-name">{name}</div>'
            f'<div class="cc-tags">'
            f'<span class="cc-tag" style="background:rgba({hex_to_rgb(sec_clr)},0.15);'
            f'color:{sec_clr}">{sector}</span>'
            f'<span class="cc-tag cc-tag-cap">{cap_cls} Cap</span>'
            f'</div>'
            f'<div class="cc-fvs-row">'
            f'<span style="color:{fvs_hex};font-weight:700;'
            f'font-family:\'DM Mono\',monospace">{fvs_emoji(fvs)} FVS {fvs:.0f}</span>'
            f'<div class="cc-fvs-track">'
            f'<div class="cc-fvs-fill" style="width:{fvs_pct}%;background:{fvs_hex}"></div>'
            f'</div>'
            f'<span style="font-size:0.75em;color:rgba(255,255,255,0.4)">Conv {conv:.1f}</span>'
            f'</div>'
            f'<div class="cc-metrics">'
            f'<div class="cc-metric"><div class="cc-metric-v">{_fmt(roe)}</div>'
            f'<div class="cc-metric-l">ROE</div></div>'
            f'<div class="cc-metric"><div class="cc-metric-v">{_fmt(revcagr)}</div>'
            f'<div class="cc-metric-l">Rev CAGR</div></div>'
            f'<div class="cc-metric">'
            f'<div class="cc-metric-v">{_fmt(ob_rev,"x") if ob_rev else "—"}</div>'
            f'<div class="cc-metric-l">OB/Rev</div></div>'
            f'</div>'
            f'<div class="cc-signals">'
            f'<span class="cc-signal-pill">{ob_icon} OB {ob_trend.title()}</span>'
            f'<span class="cc-signal-pill">{dma_txt}</span>'
            f'</div>'
            f'{sm_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Sparklines
        qd = _get_quarterly(ticker)
        rev_vals = qd.get("revenue", [])
        mar_vals = qd.get("operating_margin", [])
        if len([x for x in rev_vals if x is not None]) >= 3:
            sp1, sp2 = col.columns(2)
            with sp1:
                st.plotly_chart(_sparkline(rev_vals[-6:], "#00e676"),
                                use_container_width=True,
                                config={"displayModeBar": False},
                                key=f"sp_rev_{ticker}")
                st.caption("Revenue trend")
            with sp2:
                if mar_vals and len([m for m in mar_vals if m is not None]) >= 2:
                    st.plotly_chart(_sparkline(mar_vals[-6:], "#ffd740"),
                                    use_container_width=True,
                                    config={"displayModeBar": False},
                                    key=f"sp_mar_{ticker}")
                    st.caption("Margin trend")

        if st.button("View Full Analysis →", key=f"cta_{ticker}", use_container_width=True):
            st.session_state["analyse_ticker"]    = ticker
            st.session_state["analyse_tab_switch"] = True
            st.rerun()


# ── Main render ────────────────────────────────────────────────────────────────

def render_discover_tab() -> None:
    """Render the full Discover tab."""
    df_all  = st.session_state.get("scan_results")
    is_demo = st.session_state.get("_auto_demo_done", False)

    if df_all is None or (isinstance(df_all, pd.DataFrame) and df_all.empty):
        _render_hero_strip()
        st.info("Click **⚡ Run AI Scan** above to fetch live results.")
        return

    df_all = df_all.copy()
    df_all = add_signal_column(df_all)

    if "capClass" not in df_all.columns:
        from universe.stocks import compute_cap_class
        df_all["capClass"] = df_all.apply(
            lambda r: compute_cap_class(r.get("mcap") or 0, r.get("price") or 0), axis=1
        )

    if is_demo:
        st.markdown(
            '<div style="background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.15);'
            'border-radius:8px;padding:10px 16px;margin-bottom:12px;font-size:0.82em">'
            '📊 <strong>Sample data shown</strong> — click '
            '<strong style="color:#00e676">⚡ Run AI Scan</strong> to load live results'
            '</div>', unsafe_allow_html=True,
        )

    # Alert banner
    alerts = st.session_state.get("alerts", [])
    if alerts:
        _render_alert_banner(alerts)

    # Cap class selector
    st.markdown('<div class="section-lbl">CAP CLASS</div>', unsafe_allow_html=True)
    active_class = _render_cap_class_selector(df_all)

    # Filter bar
    st.markdown('<div class="section-lbl" style="margin-top:8px">FILTERS</div>',
                unsafe_allow_html=True)
    filters = _render_filter_bar(df_all)

    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:6px 0 12px'>",
        unsafe_allow_html=True,
    )

    # Apply filters and sort
    filtered = _apply_discover_filters(df_all, active_class, filters)
    sort_col = "fvs" if "fvs" in filtered.columns else "convictionScore"
    if sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)

    # Summary metric strip
    n_strong = int((filtered["fvs"] >= 80).sum()) if "fvs" in filtered.columns and not filtered.empty else 0
    avg_fvs  = filtered["fvs"].mean() if not filtered.empty and "fvs" in filtered.columns else None

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(
        f'<div class="metric-card"><div class="metric-label">Scanned</div>'
        f'<div class="metric-value mv-white">{len(df_all)}</div>'
        f'<div class="metric-sub">companies</div></div>', unsafe_allow_html=True)
    m2.markdown(
        f'<div class="metric-card"><div class="metric-label">{active_class} Cap</div>'
        f'<div class="metric-value mv-white">{len(filtered)}</div>'
        f'<div class="metric-sub">after filters</div></div>', unsafe_allow_html=True)
    m3.markdown(
        f'<div class="metric-card"><div class="metric-label">Strong Buys</div>'
        f'<div class="metric-value mv-green">{n_strong}</div>'
        f'<div class="metric-sub">FVS ≥ 80</div></div>', unsafe_allow_html=True)
    m4.markdown(
        f'<div class="metric-card"><div class="metric-label">Avg FVS</div>'
        f'<div class="metric-value mv-yellow">{avg_fvs:.0f}</div>'
        f'<div class="metric-sub">this class</div></div>'
        if avg_fvs else
        f'<div class="metric-card"><div class="metric-label">Avg FVS</div>'
        f'<div class="metric-value mv-white">—</div>'
        f'<div class="metric-sub">this class</div></div>',
        unsafe_allow_html=True)

    if filtered.empty:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px">'
            '<div style="font-size:3em;margin-bottom:14px">🔭</div>'
            '<div style="font-size:1.2em;color:rgba(255,255,255,0.4)">'
            'No companies match these filters</div>'
            '<div style="font-size:0.82em;color:rgba(255,255,255,0.25);margin-top:8px">'
            'Try widening your sector selection or lowering the minimum FVS</div></div>',
            unsafe_allow_html=True,
        )
        return

    # Prefetch quarterly data for all visible companies in parallel before rendering
    tickers = filtered["ticker"].tolist()
    cache   = st.session_state.setdefault("quarterly_cache", {})
    uncached = [t for t in tickers if t not in cache]
    if uncached:
        with st.spinner(f"Loading quarterly data for {len(uncached)} companies…"):
            _prefetch_quarterly_batch(tickers)

    # Prefetch FII/DII flow data (shareholding + accum) for all visible tickers
    try:
        prefetch_flow_data_batch(tickers, max_workers=4)
    except Exception:
        pass

    # Heat Leaderboard
    _render_heat_leaderboard(filtered)

    # Company card grid (top 20)
    top20 = filtered.head(20)
    st.markdown(
        f'<div class="section-lbl">TOP {len(top20)} {active_class.upper()} CAP COMPANIES</div>',
        unsafe_allow_html=True,
    )
    for i in range(0, len(top20), 2):
        c_left, c_right = st.columns(2)
        _render_company_card(i + 1, top20.iloc[i].to_dict(), c_left)
        if i + 1 < len(top20):
            _render_company_card(i + 2, top20.iloc[i + 1].to_dict(), c_right)
