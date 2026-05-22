# Foresight — AI Equity Intelligence

AI-powered Indian equity discovery platform built with Streamlit.
See growth before the market does.

## Features

- Curated Indian stock universe by sector
- Stage 1 financial filter on ROE, Revenue CAGR, Debt/Equity, and Market Cap
- Market Radar tab with company ranking and deep dive
- Valuation model builder with bull/base/bear scenarios
- Master tracker for thesis health and watchlist monitoring
- Mutual fund screener with AI-style recommendation fallback

## Setup

1. Copy `.env.example` to `.env`
2. Fill in `CLAUDE_API_KEY` if you want Claude integration
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run main.py
   ```

## Notes

- If Claude is unavailable, the app uses fallback scoring and analysis.
- The app uses `yfinance`, `requests`, and `BeautifulSoup` for data collection.
