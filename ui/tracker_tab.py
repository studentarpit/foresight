"""Tab 3 — Master Tracker: thesis integrity, guided vs actual, 200 DMA alerts."""

import json
import os
from datetime import date

import pandas as pd
import streamlit as st

from ai.analyzer import update_master_tracker

_TRACKER_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tracker.json")


def _load_tracker() -> list[dict]:
    """Load tracker entries from tracker.json. Returns empty list if file missing."""
    try:
        with open(_TRACKER_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_tracker(entries: list[dict]) -> None:
    """Persist tracker entries to tracker.json."""
    os.makedirs(os.path.dirname(_TRACKER_FILE), exist_ok=True)
    with open(_TRACKER_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def _status_badge(status: str) -> str:
    """Return emoji badge for thesis status."""
    return {"ON_TRACK": "🟢 ON TRACK", "WATCH": "🟡 WATCH", "BROKEN": "🔴 BROKEN"}.get(status, status)


def render_tracker_tab() -> None:
    """Render the Master Tracker tab with watchlist table and add-company form."""
    st.markdown("### 📋 Master Tracker")
    st.caption("Track whether management is delivering on its promises.")

    entries = _load_tracker()

    # Add Company form
    with st.expander("➕ Add Company to Tracker"):
        c1, c2 = st.columns(2)
        ticker = c1.text_input("NSE Ticker (e.g. BEL)").strip().upper()
        name = c2.text_input("Company Name")
        c3, c4, c5 = st.columns(3)
        guided_rev = c3.number_input("Guided Revenue (Cr)", min_value=0.0, value=0.0)
        actual_rev = c3.number_input("Actual Revenue (Cr)", min_value=0.0, value=0.0)
        guided_margin = c4.number_input("Guided Margin (%)", min_value=0.0, value=0.0)
        actual_margin = c4.number_input("Actual Margin (%)", min_value=0.0, value=0.0)
        guided_ob = c5.number_input("OB Guidance (Cr)", min_value=0.0, value=0.0)
        actual_ob = c5.number_input("Actual OB (Cr)", min_value=0.0, value=0.0)

        if st.button("Add to Tracker") and ticker:
            quarterly = {
                "guidedRevenue": guided_rev, "actualRevenue": actual_rev,
                "guidedMargin": guided_margin, "actualMargin": actual_margin,
                "orderBookGuidance": guided_ob, "actualOrderBook": actual_ob,
            }
            with st.spinner(f"Scoring thesis for {ticker}…"):
                result = update_master_tracker({"ticker": ticker, "name": name}, quarterly)
            entry = {
                "ticker": ticker, "name": name,
                "addedDate": str(date.today()),
                **quarterly,
                "thesisStatus": result.get("thesisStatus", "WATCH"),
                "thesisColor": result.get("thesisColor", "yellow"),
                "guidanceAccuracy": result.get("guidanceAccuracy", 0),
                "commentary": result.get("commentary", ""),
                "action": result.get("action", "REVIEW"),
                "lastUpdated": str(date.today()),
            }
            # Update if exists, else append
            existing = next((i for i, e in enumerate(entries) if e["ticker"] == ticker), None)
            if existing is not None:
                entries[existing] = entry
            else:
                entries.append(entry)
            _save_tracker(entries)
            st.success(f"{ticker} added — status: {_status_badge(entry['thesisStatus'])}")
            st.rerun()

    if not entries:
        st.info("No companies tracked yet. Add one above.")
        return

    rows = []
    for e in entries:
        rows.append({
            "Company": f"{e.get('ticker')} — {e.get('name','')}",
            "Added": e.get("addedDate", ""),
            "Guided Rev": e.get("guidedRevenue", 0),
            "Actual Rev": e.get("actualRevenue", 0),
            "Guided Margin": e.get("guidedMargin", 0),
            "Actual Margin": e.get("actualMargin", 0),
            "OB Guidance": e.get("orderBookGuidance", 0),
            "Actual OB": e.get("actualOrderBook", 0),
            "Status": _status_badge(e.get("thesisStatus", "WATCH")),
            "Accuracy %": e.get("guidanceAccuracy", 0),
            "Action": e.get("action", "REVIEW"),
            "Commentary": e.get("commentary", ""),
            "Last Updated": e.get("lastUpdated", ""),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_dma_alerts_section() -> None:
    """Standalone 200 DMA alerts panel — shown as its own section in the Analyse page."""
    scan_df = st.session_state.get("scan_results")
    entries = _load_tracker()

    if scan_df is None or scan_df.empty:
        st.info("Run AI Scan to populate 200 DMA data.")
        return

    # Show all scanned stocks (not just watchlist) with DMA status
    dma_df = scan_df[["ticker", "name", "price", "above200dma"]].copy()
    dma_df["Direction"] = dma_df["above200dma"].map(
        {True: "🟢 Above 200 DMA", False: "🔴 Below 200 DMA"}
    )
    tracked = {e["ticker"] for e in entries}
    dma_df["Tracked"] = dma_df["ticker"].apply(lambda t: "★" if t in tracked else "")

    above = dma_df[dma_df["above200dma"] == True].copy()   # noqa: E712
    below = dma_df[dma_df["above200dma"] == False].copy()  # noqa: E712

    c1, c2 = st.columns(2)
    with c1:
        st.caption(f"**🟢 Above 200 DMA — {len(above)} stocks**")
        if not above.empty:
            st.dataframe(
                above[["Tracked", "ticker", "name", "price"]].rename(
                    columns={"ticker": "Ticker", "name": "Company", "price": "Price ₹"}
                ),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("None above 200 DMA.")
    with c2:
        st.caption(f"**🔴 Below 200 DMA — {len(below)} stocks**")
        if not below.empty:
            st.dataframe(
                below[["Tracked", "ticker", "name", "price"]].rename(
                    columns={"ticker": "Ticker", "name": "Company", "price": "Price ₹"}
                ),
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("All stocks above 200 DMA.")
    st.caption("★ = in Master Tracker watchlist")
