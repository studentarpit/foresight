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
]:
    st.session_state.setdefault(_k, _v)

# ── Auto-load demo data on very first visit so the table is never blank ───────
if st.session_state["scan_results"] is None and not st.session_state["_auto_demo_done"]:
    try:
        from data.demo import (
            load_scan_results, load_company_analyses,
            load_demo_alerts, seed_demo_repository,
        )
        st.session_state["scan_results"]     = load_scan_results()
        st.session_state["company_analyses"] = load_company_analyses()
        st.session_state["alerts"]           = load_demo_alerts()
        st.session_state["_auto_demo_done"]  = True
        seed_demo_repository()
    except Exception:
        pass  # graceful — real scan will populate data

from data.collector import collect_all, fetch_mf_data          # noqa: E402
from ui.dashboard import render_discover_tab                   # noqa: E402
from ui.valuation_tab import render_valuation_tab              # noqa: E402
from ui.tracker_tab import render_tracker_tab, render_dma_alerts_section  # noqa: E402
from ui.mf_tab import render_mf_tab                            # noqa: E402
from ui.expectation_tab import render_expectation_tab          # noqa: E402
from ui.order_tab import render_order_tab                      # noqa: E402
from ui.repository_tab import render_repository_tab            # noqa: E402
from ai.analyzer import score_universe                         # noqa: E402
from ai.token_logger import reset_session, session_summary     # noqa: E402
from data.alerts import detect_alerts, load_snapshot, save_snapshot  # noqa: E402


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
        prev_snap = load_snapshot()
        alerts    = detect_alerts(scored, prev_snap)
        save_snapshot(scored)

        st.session_state["scan_results"]     = scored
        st.session_state["company_analyses"] = {}
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
    return scan_clicked


def _section(icon: str, title: str) -> None:
    st.markdown(
        f'<h2 style="font-family:\'DM Serif Display\',serif;font-size:1.35em;font-weight:400;'
        f'margin:32px 0 4px 0;padding-bottom:10px;'
        f'border-bottom:1px solid rgba(255,255,255,0.07);color:#f0f0f0">'
        f'{icon} {title}</h2>',
        unsafe_allow_html=True,
    )


def main() -> None:
    demo         = st.session_state["demo_mode"]
    scan_clicked = _render_header(demo)

    if scan_clicked and not demo:
        _run_scan()
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["🔍 Discover", "📊 Analyse", "🏦 Funds"])

    with tab1:
        try:
            render_discover_tab()
        except Exception as exc:
            st.error(f"Discover error: {exc}")
            raise

    with tab2:
        try:
            _render_analyse_tab()
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


def _render_analyse_tab() -> None:
    _section("📊", "Valuation Model")
    render_valuation_tab(st.session_state.get("scan_results"))

    _section("📋", "Master Tracker")
    render_tracker_tab()

    _section("📡", "200 DMA Alerts")
    render_dma_alerts_section()

    _section("📁", "Research Repository")
    render_repository_tab()


main()
