# Quickstart: Foresight

## Prerequisites
- Python 3.10+
- ANTHROPIC_API_KEY in `.env`

## Setup
```bash
pip install streamlit yfinance pdfplumber requests beautifulsoup4 anthropic pandas python-dotenv plotly
cp .env.example .env   # add ANTHROPIC_API_KEY
streamlit run main.py
```

## Usage
1. Open http://localhost:8501
2. **Tab 1 — Market Radar**: Click "Run AI Scan" → wait ~60-90s → browse ranked companies
3. **Tab 2 — Valuation Model**: Select company → enter assumptions → "Generate Model"
4. **Tab 3 — Master Tracker**: Add companies to watchlist → track thesis vs actuals
5. **Tab 4 — MF Screener**: Browse and filter mutual funds by long-term consistency

## Environment Variables
```
ANTHROPIC_API_KEY=sk-ant-...
```
