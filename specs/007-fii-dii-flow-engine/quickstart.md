# Quickstart: FII/DII Flow Intelligence Engine

## Prerequisites
- `pip install requests beautifulsoup4` (already in requirements.txt)
- No API key required for data fetching (all free sources)
- Claude API key required only for Section 11 AI smart money insight

## Using the Engine

### Get market-wide FII/DII today
```python
from data.fii_dii_engine import fetch_fii_dii_daily

data = fetch_fii_dii_daily()
print(data["fii"]["net"])           # e.g. -1240.5 (₹ Cr net sell)
print(data["dii"]["net"])           # e.g. +2180.0 (₹ Cr net buy)
print(data["market_sentiment"])     # "RISK_ON" | "RISK_OFF" | "NEUTRAL"
```

### Get shareholding pattern for a stock
```python
from data.fii_dii_engine import fetch_shareholding_pattern

quarters = fetch_shareholding_pattern("BEL")
for q in quarters:
    print(q["quarter"], q["fii_pct"], q["fii_change_qoq"])
# Mar 2025  19.51  +1.00
```

### Get smart money signal
```python
from data.fii_dii_engine import detect_accumulation_distribution

signal = detect_accumulation_distribution("BEL")
print(signal["pattern"])            # "ACCUMULATING"
print(signal["combined_signal"])    # "STRONG_BUY"
print(signal["smart_money_verdict"])
```

### Get flow score
```python
from data.fii_dii_engine import compute_flow_score, flow_score_label

score = compute_flow_score("BEL")  # returns None if no data
if score is not None:
    label, color = flow_score_label(score)
    print(f"Flow Score: {score} — {label}")  # e.g. "Flow Score: 72 — Mild Accumulation"
```

### Pre-warm cache for a batch of stocks (parallel)
```python
from data.fii_dii_engine import prefetch_flow_data_batch

tickers = ["BEL", "HAL", "BHEL", "NTPC", "MAZDOCK"]
prefetch_flow_data_batch(tickers, max_workers=4)
# Now compute_flow_score() calls are instant (cache hit)
```

## Where Each Component Renders

| Component | Location | File |
|-----------|----------|------|
| FII/DII daily strip | Persistent header (all tabs) | `main.py:_render_fii_dii_strip()` |
| Shareholding chart + QoQ table | Analyse tab Section 10 | `ui/analyse.py:_render_shareholding_section()` |
| AI smart money card | Analyse tab Section 11 | `ui/analyse.py:_render_smart_money_history()` |
| Smart money signal card | Company cards (Discover tab) | `ui/components.py:smart_money_card_html()` |
| Bulk deal feed | Sentiment tab | `ui/sentiment_dashboard.py:_render_bulk_deal_feed()` |
| Flow heatmap | Sentiment tab | `ui/sentiment_dashboard.py:_render_flow_heatmap()` |
| flowScore column | scan_results DataFrame | `ai/analyzer.py:score_universe()` |

## Cache Location
All cache files: `cache/` directory in repo root.
Format: `{ticker}_{source}_{YYYYMMDD}.json`
Example: `BEL_shareholding_20260526.json`
