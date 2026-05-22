# Foresight — Feature Specification

## Overview
An AI-powered Indian equity discovery platform that scans listed companies, extracts future
revenue visibility signals, and ranks them by AI conviction score. Retail investors get
institutional-style long-term growth research across a curated 50-stock + 100-fund universe.

## Spec 01 — Data Collector

### Purpose
Fetch financial, technical, and filing data for the curated Indian stock universe.
Apply Stage 1 filter before AI analysis.

### Input
List of stock tickers from universe/stocks.py

### Output
A filtered pandas DataFrame with columns:
ticker, name, sector, mcap, roe, roce, revcagr, profitcagr, debtEq,
orderBookRev, orderBookTrend, price, pe, above200dma, screenerUrl

### Data Sources
- **yfinance**: price, 200 DMA, market cap, PE, 52wk high/low
- **screener.in** (scrape public pages): ROE, ROCE, Revenue CAGR 3yr/5yr, Profit CAGR, D/E, quarterly actuals
- **NSE/BSE filings** (requests+BS4): corporate announcements, order wins, investor presentation PDF links
- **pdfplumber**: order book value, management guidance, capex plans from PDFs

### Order Book Trend Logic
- Compare order book across last 4 quarters
- order_inflow_rate = new orders won per quarter
- execution_rate = revenue per quarter
- ACCELERATING if inflow > execution, DECLINING if inflow < execution, else STABLE

### Stage 1 Financial Filter
Pass to AI only if ALL: ROE > 12%, Revenue CAGR (3yr) > 15%, D/E < 1.0, MCap > 500 Cr

### MF Data (separate function)
fetch_mf_data() from mfapi.in: fund name, category, AUM, 1yr/3yr/5yr/10yr returns, max drawdown, consistency score

### Error Handling
Skip bad tickers, fallback screener→yfinance, never crash full scan, show progress

## Spec 02 — AI Analyzer

### Purpose
Generate AI conviction scores, full investment analysis, valuation models, and thesis tracking.

### Four Functions

**score_universe(df)** — batch score all filtered companies, return JSON array:
[{"ticker": "BEL", "growthScore": 8.2, "riskScore": 3.1, "visibilityScore": 8.7, "convictionScore": 8.4}]
0.5s delay between calls, max 30 companies.

**analyze_company(company)** — full deep dive, return JSON:
{growthScore, riskScore, visibilityScore, convictionScore, thesis, bullCase, baseCase, bearCase,
risks[], orderBookInsight, technicalView, catalysts[]}

**build_valuation_model(company, assumptions)** — 3-scenario DCF:
inputs: revenueGrowth, marginExpansion, peMultiple, years
output: bull/base/bear with revenue[], profit[], targetPrice, cagr

**update_master_tracker(company, quarterlyData)** — thesis integrity tracker:
compare guidance vs actuals, return: thesisStatus, thesisColor, guidanceAccuracy, commentary, action

### Prompts (ai/prompts.py)
SCAN_PROMPT, DEEP_ANALYSIS_PROMPT, VALUATION_PROMPT, MASTER_TRACKER_PROMPT
All end with: "Return ONLY valid JSON. No markdown. No explanation."

### MF Analysis
analyze_mf(fund) → consistencyScore, drawdownRisk, recommendation (STRONG/MODERATE/AVOID), reasoning

## Spec 03 — Streamlit Dashboard

### Entry Point
main.py — `streamlit run main.py`

### Tab 1 — Market Radar
- Header: logo, tagline, "Run AI Scan" button + progress bar
- Summary row: Total Scanned / Passed Filter / Strong Buys / Avg Conviction
- Sidebar: sector multiselect, MCap filter, min conviction slider, OB trend filter, 200DMA toggle
- Table: Rank, Company, Sector, MCap, ROE, Rev CAGR, OB/Rev, OB Trend, 200DMA, Conviction, Signal
- Row click → Company Deep Dive: 4 score bars, thesis box, bull/base/bear columns, risks, catalysts

### Tab 2 — Valuation Model
- Left: company selector + inputs (revenue growth %, margin expansion %, exit PE, years)
- Right: bull/base/bear projection table, CAGR, upside %, colour coded

### Tab 3 — Master Tracker
- Table: Company, Thesis Date, Guided vs Actual (Rev, Margin, OB), Thesis Status, Last Updated
- Status: ON TRACK (green) / WATCH (yellow) / BROKEN (red)
- Add Company: manual guided metrics input, auto actual pull, Claude scores status
- 200 DMA Alert Panel: watchlist stocks crossing 200 DMA this week

### Tab 4 — MF Screener
- Sidebar: category, min 10yr return, max drawdown, min consistency
- Table: Fund, Category, AUM, 1yr/3yr/5yr/10yr, Max Drawdown, Consistency, AI Recommendation
- Click → AI reasoning, drawdown chart, return consistency bar chart

### Streamlit Rules
- st.session_state for all cached results
- st.spinner() for every API call
- st.tabs() for 4-tab structure
- st.columns() for side-by-side
- plotly for charts
