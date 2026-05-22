# Research: WIGA Future Growth Radar

## Technology Decisions

### Decision: Python 3.10+ with Streamlit
**Rationale**: Fastest path to interactive data dashboard without frontend build tooling.
Streamlit's session_state handles scan caching cleanly.
**Alternatives considered**: Dash (more complex), Flask+React (too heavy for MVP).

### Decision: yfinance for market data
**Rationale**: Free, no API key, covers NSE tickers with `.NS` suffix (e.g. `BEL.NS`).
Returns OHLCV, info dict with marketCap, trailingPE, 52wk data.
**Limitation**: 200 DMA must be computed from history(period="1y") manually.
**Alternatives considered**: NSE official API (rate-limited, auth required).

### Decision: screener.in scraping for fundamentals
**Rationale**: screener.in public pages expose ROE, ROCE, CAGR, D/E in structured HTML tables.
BeautifulSoup can parse these without JS rendering.
**Caveat**: Rate-limit scraping (1 req/2s). Fallback to yfinance info dict for partial data.
**Alternatives considered**: Trendlyne (paid), Moneycontrol (heavy JS).

### Decision: mfapi.in for MF data
**Rationale**: Free REST API, no key. Returns NAV history and scheme metadata.
Consistency score computed locally from return series.
**Limitations**: No drawdown data directly — compute from NAV series.

### Decision: pdfplumber for PDF extraction
**Rationale**: Best Python library for table extraction from investor presentation PDFs.
Handles column-based PDFs common in Indian corp filings.
**Alternatives considered**: PyMuPDF (better for text, worse for tables).

### Decision: claude-sonnet-4-20250514 model
**Rationale**: Specified in CLAUDE.md. Strong JSON instruction-following. Cost-effective for batch.
**Pattern**: All prompts end with "Return ONLY valid JSON. No markdown. No explanation."
Parse with json.loads(); catch JSONDecodeError for graceful fallback.

### Decision: NSE ticker suffix `.NS` for yfinance
**Rationale**: All NSE-listed stocks require `.NS` suffix in yfinance (e.g., `BEL.NS`, `RVNL.NS`).
BSE suffix is `.BO`. Use `.NS` as primary, `.BO` as fallback.

### Decision: No database for MVP
**Rationale**: Session_state + in-memory DataFrames sufficient for single-user MVP.
Master Tracker persists to `data/tracker.json` (simple JSON file).
**Future**: Migrate to SQLite when multi-user or historical tracking needed.

## Key Implementation Patterns

### screener.in URL pattern
`https://www.screener.in/company/{TICKER}/` (no .NS suffix)
Key HTML selectors:
- ROE: table#profit-loss → row "Return on equity"
- D/E: table#balance-sheet → row "Borrowings" / "Total Assets"
- Revenue CAGR: section#growth → compounded sales growth table

### Order Book Trend Calculation
```python
# From quarterly revenue data (4 quarters)
inflow_rate = mean(new_orders_per_quarter[-4:])
exec_rate   = mean(revenue_per_quarter[-4:])
trend = "ACCELERATING" if inflow_rate > exec_rate * 1.1 else \
        "DECLINING"    if inflow_rate < exec_rate * 0.9 else "STABLE"
```

### 200 DMA Calculation
```python
hist = yf.Ticker("BEL.NS").history(period="1y")
dma200 = hist["Close"].rolling(200).mean().iloc[-1]
above200dma = hist["Close"].iloc[-1] > dma200
```

### Valuation Model Scenarios
Bull = assumptions × 1.3, Base = as entered, Bear = assumptions × 0.7
Claude generates year-by-year revenue[] and profit[] projections.

## Risk Resolutions

| Risk | Resolution |
|------|-----------|
| screener.in blocks scraping | Add 2s delay + User-Agent header; fallback to yfinance |
| PDF link discovery failure | Skip PDF extraction; mark orderBookRev as None |
| Claude API timeout | 30s timeout; return error dict with fallback message |
| yfinance stale data | Use `fast_info` property; add data freshness warning if >24h |
| MF NAV history incomplete | Require min 3yr NAV history; skip funds with less |
