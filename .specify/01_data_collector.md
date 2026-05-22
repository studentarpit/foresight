# Spec 01 — Data Collector (Upgraded)

## Purpose
Fetch financial, technical, and filing data for the curated
Indian stock universe. Apply Stage 1 filter before AI analysis.

## Input
List of stock tickers from universe/stocks.py

## Output
A filtered pandas DataFrame with these columns:
- ticker, name, sector, mcap, roe, roce, revcagr,
  profitcagr, debtEq, orderBookRev, orderBookTrend,
  price, pe, above200dma, screenerUrl

## Data Sources to Pull From

### yfinance
- Current price
- 200 DMA (200 day moving average)
- Market cap
- PE ratio
- 52 week high/low

### screener.in (scrape public pages)
- ROE, ROCE
- Revenue CAGR 3yr and 5yr
- Profit CAGR
- Debt/Equity
- Quarterly revenue actuals vs guidance

### NSE/BSE filings (requests + BeautifulSoup)
- Latest corporate announcements
- Order win announcements
- Investor presentation PDF links

### PDF Extraction (pdfplumber)
- Extract order book value from investor presentations
- Extract management guidance statements
- Extract capex plans

## Order Book Trend Logic
This is critical — not just current order book but TREND:
- Compare order book value across last 4 quarters
- Calculate: order_inflow_rate = new orders won per quarter
- Calculate: execution_rate = revenue per quarter
- If order_inflow_rate > execution_rate → ACCELERATING (bullish)
- If order_inflow_rate < execution_rate → DECLINING (bearish)
- Store as orderBookTrend: "ACCELERATING" / "STABLE" / "DECLINING"

## Technical Filter
- above200dma: True if current price > 200 day moving average
- Use this as confirmation signal, not primary filter

## Stage 1 Financial Filter
Only pass companies to AI that meet ALL of these:
- ROE > 12%
- Revenue CAGR (3yr) > 15%
- Debt/Equity < 1.0
- Market Cap > 500 Cr

## Mutual Fund Data (separate function)
Write a separate function fetch_mf_data() that pulls:
- Fund name, category, AUM
- 1yr, 3yr, 5yr, 10yr returns
- Maximum drawdown (10yr)
- Consistency score (how many years beat benchmark)
Source: Use mfapi.in (free API, no key needed)

## Error Handling
- If yfinance fails for a ticker, skip and log
- If screener.in scrape fails, use yfinance fallback
- Never crash full scan for one bad ticker
- Show progress: "Scanning 12/50 companies..."

## Expected Output
From ~50 stocks: 15-25 pass financial filter
From MF universe of ~100 funds: 10-20 pass consistency filter