<!-- SPECKIT START -->
<!-- Plan: specs/main/plan.md -->
# Foresight — AI Equity Intelligence Constitution

## What This Project Is
An AI-powered Indian equity discovery platform that scans listed
companies, extracts future revenue visibility signals, and ranks
them by AI conviction score. The goal is to find future
compounders before the broader market recognises them.

This is NOT a trading tool. It is a long-term growth discovery
platform for retail investors who want institutional-style research.

## Tech Stack
- Python 3.10+
- Streamlit (UI dashboard)
- yfinance (market data and financials)
- pdfplumber (PDF extraction from investor presentations)
- requests + BeautifulSoup (scraping NSE/BSE filings)
- anthropic (AI analysis via Claude API)
- pandas (data processing)
- python-dotenv (environment variables)

## Folder Structure

foresight/
├── CLAUDE.md
├── .specify/
├── .env
├── main.py              ← Streamlit entry point
├── data/
│   ├── collector.py     ← yfinance data fetching
│   ├── scraper.py       ← NSE/BSE filing scraper
│   └── pdf_extractor.py ← pdfplumber PDF parsing
├── ai/
│   ├── analyzer.py      ← Claude API analysis
│   └── prompts.py       ← All prompt templates
├── ui/
│   ├── dashboard.py     ← Main dashboard view
│   ├── company_card.py  ← Individual company view
│   └── filters.py       ← Sector/metric filters
└── universe/
└── stocks.py        ← Curated stock universe

## Stock Universe
Focus on these sectors only for MVP:
- Defence (BEL, Mazagon Dock, HAL, BHEL, Paras Defence)
- Railways (RVNL, Titagarh Rail, Jupiter Wagons)
- EPC (Kalpataru, KEC International, Techno Electric)
- EMS (Kaynes Technology, Syrma SGS, Dixon Technologies)
- Power (Transformers & Rectifiers, Hitachi Energy, CESC)
- Solar/Wind (Waaree Energies, Inox Wind, Sterling Wilson)

## AI Rules
- Always use model: claude-sonnet-4-20250514
- Every company analysis must return: growthScore, riskScore,
  visibilityScore, convictionScore, thesis, bullCase, baseCase,
  bearCase, risks[]
- All Claude API responses must be requested as JSON only
- Never display raw API responses to the user

## Coding Rules
- NEVER hardcode API keys — always use .env file
- NEVER build everything in one file — follow folder structure
- ALWAYS handle API errors gracefully with fallback messages
- ALWAYS show loading states in Streamlit during API calls
- Keep each function under 50 lines
- Add a comment above every function explaining what it does

## What NOT To Do
- Do not build intraday or options features
- Do not use paid data APIs in MVP
- Do not over-engineer — MVP first, scale later
- Do not skip the financial filter stage before AI analysis
- Do not analyse all 2000+ stocks — use the curated universe

## Financial Filter Thresholds (Stage 1 Screen)
Only pass companies to AI that meet ALL of these:
- ROE > 12%
- Revenue CAGR (3yr) > 15%
- Debt/Equity < 1.0
- Market Cap > 500 Cr

## Definition of Done for MVP
A user can:
1. Open the Streamlit app
2. Click "Run AI Scan"
3. See companies ranked by AI conviction score
4. Click any company for full bull/bear/base case analysis
5. Filter by sector and market cap
<!-- SPECKIT END -->
