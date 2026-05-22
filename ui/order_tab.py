"""Tab 6 — Order Intelligence Engine.

Sections 6-8 of research spec:
- Fetch order announcements from NSE for any tracked company
- AI-extract structured fields (value, customer, type, segment)
- Per-company order history table + cumulative value chart
- Sector-wide order momentum view
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai.analyzer import extract_order_from_announcement
from data.order_fetcher import fetch_order_announcements
from data.order_history import (
    all_tickers_with_orders,
    delete_order,
    load_ticker_orders,
    save_orders,
    total_order_value,
)
from universe.stocks import STOCK_UNIVERSE

_TYPE_ICONS = {"domestic": "🏠", "export": "✈️", "unknown": "—"}
_SIG_COLORS = {"HIGH": "#28a745", "MEDIUM": "#fd7e14", "LOW": "#6c757d"}


def render_order_tab() -> None:
    st.markdown("### Order Intelligence Engine")
    st.caption(
        "Track new order wins from NSE corporate announcements. "
        "AI extracts order value, customer, segment, and execution timeline automatically."
    )

    scan_df = st.session_state.get("scan_results")
    scan_tickers = list(scan_df["ticker"]) if scan_df is not None and not scan_df.empty else []
    hist_tickers = all_tickers_with_orders()
    all_t = sorted(set(scan_tickers + [s["ticker"] for s in STOCK_UNIVERSE]))

    # ── Fetch panel ───────────────────────────────────────────────────────────
    with st.expander("📡 Fetch Orders from NSE", expanded=not hist_tickers):
        col_sel, col_btn = st.columns([3, 1])
        fetch_ticker = col_sel.selectbox(
            "Ticker to fetch", all_t, key="fetch_order_ticker",
            format_func=lambda t: _ticker_label(t),
        )
        fetch_all = st.checkbox("Fetch for all scanned companies", value=False)

        if col_btn.button("Fetch Orders", use_container_width=True):
            targets = scan_tickers if fetch_all else ([fetch_ticker] if fetch_ticker else [])
            if not targets:
                st.warning("No tickers selected.")
            else:
                prog = st.progress(0)
                total_found = 0
                for i, t in enumerate(targets):
                    company_meta = next((s for s in STOCK_UNIVERSE if s["ticker"] == t), {})
                    name = company_meta.get("name", t)
                    with st.spinner(f"Fetching orders for {name}…"):
                        raw_orders = fetch_order_announcements(t, days=365)
                    # AI-enrich each order
                    enriched = []
                    for ann in raw_orders:
                        ai = extract_order_from_announcement(t, name, ann.get("description", ""))
                        merged = {**ann, **{k: v for k, v in ai.items() if v is not None and k not in ann}}
                        enriched.append(merged)
                    added = save_orders(t, enriched)
                    total_found += len(enriched)
                    prog.progress(int((i + 1) / len(targets) * 100))
                st.success(f"Fetched {total_found} order announcements for {len(targets)} company/companies.")
                st.rerun()

    st.markdown("---")

    # ── Sector order momentum summary ─────────────────────────────────────────
    if hist_tickers:
        _render_sector_momentum()
        st.markdown("---")

    # ── Per-company order history ─────────────────────────────────────────────
    selected = st.selectbox(
        "Select company",
        ["—"] + sorted(set(all_t)),
        format_func=lambda t: _ticker_label(t) if t != "—" else "— Select a company —",
        key="order_company_select",
    )
    if selected == "—":
        if not hist_tickers:
            st.info("No order data yet. Use the panel above to fetch orders from NSE.")
        return

    orders = load_ticker_orders(selected)
    total_val = total_order_value(selected)

    c1, c2, c3 = st.columns(3)
    c1.metric("Orders Tracked", len(orders))
    c2.metric("Total Value (Cr)", f"₹{total_val:,.0f}" if total_val else "—")
    domestic = sum(1 for o in orders if o.get("order_type") == "domestic")
    export = sum(1 for o in orders if o.get("order_type") == "export")
    c3.metric("Domestic / Export", f"{domestic} / {export}")

    if orders:
        _render_order_table(orders, selected)
        _render_order_chart(orders, selected)
    else:
        st.info(f"No orders saved for {selected}. Click Fetch Orders above.")


# ── Sector momentum view ──────────────────────────────────────────────────────

def _render_sector_momentum() -> None:
    st.markdown("#### Sector Order Momentum")
    rows = []
    for ticker in all_tickers_with_orders():
        orders = load_ticker_orders(ticker)
        total = total_order_value(ticker) or 0
        meta = next((s for s in STOCK_UNIVERSE if s["ticker"] == ticker), {})
        rows.append({
            "Ticker": ticker,
            "Sector": meta.get("sector", "—"),
            "Orders": len(orders),
            "Total Value (Cr)": total,
            "Latest": orders[0].get("announcement_date", "—") if orders else "—",
        })
    if rows:
        df = pd.DataFrame(rows).sort_values("Total Value (Cr)", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Order history table ───────────────────────────────────────────────────────

def _render_order_table(orders: list, ticker: str) -> None:
    st.markdown(f"#### Order History")
    rows = []
    for o in orders:
        val = o.get("order_value_cr")
        sig = o.get("significance", "MEDIUM")
        rows.append({
            "Date":      o.get("announcement_date", "—"),
            "Value (Cr)": f"₹{val:,.0f}" if val else "—",
            "Type":      _TYPE_ICONS.get(o.get("order_type", "unknown"), "—") + " " + o.get("order_type", "—").title(),
            "Customer":  o.get("customer", "Undisclosed"),
            "Segment":   o.get("segment", "—") or "—",
            "Exec Period": o.get("execution_period", "—") or "—",
            "Repeat":    "Yes" if o.get("is_repeat_order") else "No",
            "Significance": sig,
            "Description": (o.get("description", "")[:120] + "…") if len(o.get("description", "")) > 120 else o.get("description", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Remove an order entry", expanded=False):
        if orders:
            options = [f"{o.get('announcement_date','?')} — {o.get('description','')[:60]}" for o in orders]
            idx = st.selectbox("Select entry to remove", range(len(options)),
                               format_func=lambda i: options[i], key=f"del_order_{ticker}")
            if st.button("Delete", key=f"del_order_btn_{ticker}"):
                oid = orders[idx].get("id", "")
                if delete_order(ticker, oid):
                    st.success("Removed.")
                    st.rerun()


# ── Order value chart ─────────────────────────────────────────────────────────

def _render_order_chart(orders: list, ticker: str) -> None:
    dated = [(o["announcement_date"], o["order_value_cr"])
             for o in orders if o.get("order_value_cr") and o.get("announcement_date")]
    if not dated:
        return
    dated.sort()
    dates, vals = zip(*dated)
    cumulative = []
    running = 0.0
    for v in vals:
        running += v
        cumulative.append(round(running, 1))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Order Value (Cr)", x=list(dates), y=list(vals),
                         marker_color="#28a745", opacity=0.75))
    fig.add_trace(go.Scatter(name="Cumulative (Cr)", x=list(dates), y=cumulative,
                             mode="lines+markers", line=dict(color="#fd7e14", width=2),
                             yaxis="y2"))
    fig.update_layout(
        title=f"{ticker} — Order Inflow Timeline",
        xaxis_title="Date",
        yaxis=dict(title="Order Value (Cr)"),
        yaxis2=dict(title="Cumulative (Cr)", overlaying="y", side="right"),
        barmode="group", height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def _ticker_label(ticker: str) -> str:
    meta = next((s for s in STOCK_UNIVERSE if s["ticker"] == ticker), {})
    name = meta.get("name", ticker)
    return f"{ticker} — {name}" if name != ticker else ticker
