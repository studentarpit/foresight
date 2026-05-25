"""Streamlit entry point — run with: python -m streamlit run main.py"""

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Foresight · AI Equity Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui.styles import inject_styles  # noqa: E402
inject_styles()

# ── Session state init ────────────────────────────────────────────────────────
for _k, _v in [
    ("demo_mode", False), ("scan_results", None), ("company_analyses", {}),
    ("mf_data", None), ("mf_analyses", {}), ("alerts", []),
    ("last_scan_ts", None), ("_auto_demo_done", False),
    ("analyse_ticker", None), ("cap_class_filter", "Large"),
    ("quarterly_cache", {}), ("heat_cache", {}),
]:
    st.session_state.setdefault(_k, _v)

# ── Auto-load demo data on first visit ────────────────────────────────────────
if st.session_state["scan_results"] is None and not st.session_state["_auto_demo_done"]:
    try:
        from data.demo import (
            load_scan_results, load_company_analyses,
            load_demo_alerts, seed_demo_repository,
        )
        results = load_scan_results()
        # Inject capClass into demo data
        from universe.stocks import compute_cap_class
        if hasattr(results, "apply"):
            results["capClass"] = results.apply(
                lambda r: compute_cap_class(r.get("mcap") or 0, r.get("price") or 0), axis=1
            )
        st.session_state["scan_results"]     = results
        st.session_state["company_analyses"] = load_company_analyses()
        st.session_state["alerts"]           = load_demo_alerts()
        st.session_state["_auto_demo_done"]  = True
        seed_demo_repository()
    except Exception:
        pass

from data.collector import collect_all, fetch_mf_data          # noqa: E402
from ui.discover import render_discover_tab                    # noqa: E402
from ui.analyse import render_analyse_tab                      # noqa: E402
from ui.funds import render_mf_tab                             # noqa: E402
from ui.sentiment_dashboard import render_sentiment_tab        # noqa: E402
from ai.analyzer import score_universe                         # noqa: E402
from ai.token_logger import reset_session, session_summary     # noqa: E402
from data.alerts import detect_alerts, detect_smart_money_alerts, load_snapshot, save_snapshot  # noqa: E402


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_nse_open() -> bool:
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return 555 <= mins <= 930  # 9:15 AM – 3:30 PM IST


def _run_scan() -> None:
    prog_slot = st.empty()
    with prog_slot.container():
        pb  = st.progress(0)
        txt = st.empty()

        def cb(current, total):
            pb.progress(int(current / total * 100))
            txt.text(f"Scanning {current}/{total} companies…")

        reset_session()
        df = collect_all(progress_cb=cb)
        if df.empty:
            txt.text("No companies passed Stage 1 filter.")
            return
        txt.text("Running AI scoring…")
        scored = score_universe(df)

        # Ensure capClass column
        from universe.stocks import compute_cap_class
        if "capClass" not in scored.columns:
            scored["capClass"] = scored.apply(
                lambda r: compute_cap_class(r.get("mcap") or 0, r.get("price") or 0), axis=1
            )

        prev_snap = load_snapshot()
        alerts    = detect_alerts(scored, prev_snap)

        # Merge smart money accumulation alerts (append unique ticker+type pairs)
        try:
            sm_alerts = detect_smart_money_alerts(scored)
            seen = {(a["ticker"], a["type"]) for a in alerts}
            for a in sm_alerts:
                if (a["ticker"], a["type"]) not in seen:
                    alerts.append(a)
        except Exception:
            pass

        save_snapshot(scored)

        st.session_state["scan_results"]     = scored
        st.session_state["company_analyses"] = {}
        st.session_state["quarterly_cache"]  = {}
        st.session_state["heat_cache"]       = {}
        st.session_state["alerts"]           = alerts
        st.session_state["last_scan_ts"]     = datetime.now().strftime("%H:%M  %d %b")
        st.session_state["demo_mode"]        = False
        session_summary()
    prog_slot.empty()


def _render_header(demo: bool) -> bool:
    """Render persistent Foresight header. Returns True if scan button clicked."""
    is_open   = _is_nse_open()
    mkt_cls   = "market-open" if is_open else "market-closed"
    mkt_label = "NSE OPEN"    if is_open else "NSE CLOSED"
    last_scan = st.session_state.get("last_scan_ts") or "—"

    col_logo, _spacer, col_right = st.columns([3, 3, 3])

    with col_logo:
        st.markdown(
            '<div class="fs-logo-row">'
            '<div class="fs-hex"></div>'
            '<div>'
            '<div class="fs-wordmark">Foresight</div>'
            '<div class="fs-tagline">AI-Powered Equity Intelligence · India</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        rc1, rc2, rc3 = st.columns([2, 2, 2])
        rc1.markdown(
            f'<div style="padding-top:8px">'
            f'<span class="market-pill {mkt_cls}">{mkt_label}</span></div>',
            unsafe_allow_html=True,
        )
        rc2.markdown(
            f'<div class="scan-ts" style="padding-top:8px">Last scan<br>{last_scan}</div>',
            unsafe_allow_html=True,
        )
        scan_clicked = rc3.button(
            "⚡ Run AI Scan",
            use_container_width=True,
            disabled=demo,
            key="header_scan_btn",
        )

    st.markdown('<hr class="fs-header-hr">', unsafe_allow_html=True)
    _render_fii_dii_strip()
    return scan_clicked


def _render_fii_dii_strip() -> None:
    """Render FII/DII daily flow strip below the header (Spec 07)."""
    try:
        from data.fii_dii_engine import fetch_fii_dii_daily
        data = fetch_fii_dii_daily()
    except Exception:
        data = {}

    fii = data.get("fii", {})
    dii = data.get("dii", {})
    sentiment = data.get("market_sentiment", "")

    fii_net = fii.get("net")
    dii_net = dii.get("net")

    if fii_net is None and dii_net is None:
        # No data yet — skip strip silently
        return

    def _fmt(val) -> str:
        if val is None:
            return "—"
        sign = "+" if val >= 0 else ""
        return f"{sign}₹{val:,.0f} Cr"

    def _color(val) -> str:
        if val is None:
            return "#aaa"
        return "#00e676" if val >= 0 else "#ff5252"

    combined = (fii_net or 0) + (dii_net or 0)
    sent_icon = {"RISK_ON": "🟢", "RISK_OFF": "🔴", "NEUTRAL": "⚪"}.get(sentiment, "")

    fii_clr = _color(fii_net)
    dii_clr = _color(dii_net)
    net_clr = _color(combined)

    fii_lbl = _fmt(fii_net)
    dii_lbl = _fmt(dii_net)
    net_lbl = _fmt(combined)

    st.markdown(
        f"""
        <div style="
            background:#12121a;border:1px solid #1e1e2e;border-radius:8px;
            padding:8px 20px;margin-bottom:10px;display:flex;gap:32px;
            align-items:center;font-size:0.82rem;flex-wrap:wrap;">
          <span>🏦 <b>FII Today:</b>
            <span style="color:{fii_clr};font-weight:600">{fii_lbl}</span>
          </span>
          <span>🏛️ <b>DII Today:</b>
            <span style="color:{dii_clr};font-weight:600">{dii_lbl}</span>
          </span>
          <span>📊 <b>Net:</b>
            <span style="color:{net_clr};font-weight:600">{net_lbl}</span>
          </span>
          <span style="margin-left:auto;opacity:0.7">{sent_icon} {sentiment.replace("_"," ")}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    demo         = st.session_state["demo_mode"]
    scan_clicked = _render_header(demo)

    if scan_clicked and not demo:
        _run_scan()
        st.rerun()

    # Switch to Analyse tab if user clicked "View Full Analysis" on a card
    default_tab = 1 if st.session_state.get("analyse_tab_switch") else 0

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discover", "📊 Analyse", "🏦 Funds", "🌐 Sentiment"])

    with tab1:
        try:
            render_discover_tab()
        except Exception as exc:
            st.error(f"Discover error: {exc}")
            raise

    with tab2:
        try:
            render_analyse_tab()
        except Exception as exc:
            st.error(f"Analyse error: {exc}")
            raise

    with tab3:
        try:
            if not demo and st.button("🏦 Load MF Data", key="mf_load_btn"):
                with st.spinner("Fetching mutual fund data…"):
                    st.session_state["mf_data"] = fetch_mf_data()
                    st.rerun()
            render_mf_tab(st.session_state.get("mf_data"))
        except Exception as exc:
            st.error(f"Funds error: {exc}")

    with tab4:
        try:
            render_sentiment_tab(st.session_state.get("scan_results"))
        except Exception as exc:
            st.error(f"Sentiment error: {exc}")
            raise


main()
