<!-- SPECKIT START -->
<!-- Plan: specs/007-fii-dii-flow-engine/plan.md -->

# Foresight — AI Equity Intelligence Constitution

## Product Identity
**Name:** Foresight  
**Tagline:** See growth before the market does  
**Audience:** Long-term retail investors wanting institutional-style research  
**Positioning:** AI-powered future growth discovery — NOT a trading tool  

## Core Philosophy
The user NEVER manually reads a balance sheet.  
The user NEVER manually reads a PDF.  
The user NEVER manually searches for order book data.  
Foresight does everything automatically.  
User opens app → sees top 20 companies per cap class  
→ clicks one → sees everything needed to invest confidently.  

## What This Is NOT
- Not an intraday trading tool
- Not an options prediction tool
- Not a manual screener
- Not a HFT platform

---

## Tech Stack
- Python 3.10+
- Streamlit (UI dashboard)
- yfinance (price, MCap, 200DMA, volume)
- NSE official API (filings, announcements, quarterly results)
- Trendlyne API (detailed financials, concall transcripts)
- pdfplumber + PyMuPDF (PDF order book extraction)
- anthropic SDK (AI analysis via Claude API)
- pandas (data processing)
- plotly (all charts — dark themed)
- python-dotenv (environment variables)
- threading (parallel data fetching)
- requests + BeautifulSoup (filing scraper)
- mftool (mutual fund data)

---

## Folder Structure

foresight/
├── .env                         ← API keys (never commit)
├── .streamlit/
│   └── config.toml              ← Dark theme config
├── CLAUDE.md                    ← This file
├── .specify/                    ← All spec files
├── main.py                      ← Streamlit entry point
├── requirements.txt
├── README.md
├── data/
│   ├── init.py
│   ├── collector.py             ← yfinance data fetching
│   ├── nse_scraper.py           ← NSE/BSE filing scraper
│   ├── trendlyne.py             ← Trendlyne API client
│   ├── pdf_extractor.py         ← pdfplumber PDF parsing
│   └── order_book_engine.py     ← Core moat: auto order book
├── ai/
│   ├── init.py
│   ├── analyzer.py              ← Claude API analysis
│   ├── prompts.py               ← All prompt templates
│   └── heat_engine.py           ← Heat score + momentum
├── ui/
│   ├── init.py
│   ├── discover.py              ← Tab 1: Market Radar
│   ├── analyse.py               ← Tab 2: Deep Dive
│   ├── funds.py                 ← Tab 3: MF Screener
│   ├── components.py            ← Reusable UI components
│   └── charts.py                ← All plotly chart functions
├── universe/
│   └── stocks.py                ← Curated 80-stock universe
└── cache/
└── .gitkeep                 ← PDF and data cache


---

## Stock Universe (80 stocks across 6 sectors)

### Large Cap (MCap > ₹20,000 Cr)
Defence: BEL, HAL, BHEL  
Power: NTPC, POWERGRID, SIEMENS, ABB, CUMMINSIND, THERMAX  
EPC: L&T  

### Mid Cap (MCap ₹5,000–20,000 Cr)
Defence: MAZDOCK, COCHINSHIP, GRSE, PARAS  
Railways: RVNL, IRFC, TITAGARH  
EPC: KPIL, KEC, TECHNO  
EMS: KAYNES, SYRMA, DIXON, PGEL  
Power: TRIL, HITACHIENERGY  
Solar/Wind: WAAREEENER, INOXWIND, STERLINWILS  

### Small Cap (MCap ₹500–5,000 Cr)
Defence: MTAR, DATAPATTNS, IDEAFORGE, AVANTEL, CENTUM  
Railways: RAILTEL, IRCON, NBCC  
Defence Ships: GARDENREACH  
Other: APOLLO  

---

## Cap Classes
- Large Cap: MCap > ₹20,000 Cr
- Mid Cap: MCap ₹5,000–20,000 Cr
- Small Cap: MCap ₹500–5,000 Cr
- Penny: MCap < ₹500 Cr, price < ₹50

Show TOP 20 companies per cap class ranked by FVS Score.

---

## Streamlit Theme (config.toml)

```toml
[theme]
base="dark"
backgroundColor="#0a0a0f"
secondaryBackgroundColor="#12121a"
primaryColor="#00e676"
textColor="#f0f0f0"
font="sans serif"
```

---

## UI Structure — 3 Tabs Only

### Tab 1 — 🔍 Discover
- Hero banner (first load only, hide after scan)
- Cap class selector (Large / Mid / Small / Penny)
- Heat leaderboard strip (top 5 heating, bottom 3 cooling)
- Horizontal filter bar (sector, FVS, OB trend, signal)
- Alert banner (collapsible, priority sorted)
- 20 company cards in 2-column grid (NOT a table)
- Summary strip (scanned / passed / strong buys / avg FVS)

### Tab 2 — 📊 Analyse
- Company header bar
- AI summary box (why Foresight selected this)
- 6-card plotly analytics grid
- Scenario analysis (Bull / Base / Bear)
- Financial health dashboard (8 quarters)
- Management credibility table
- Peer comparison
- Valuation model (user inputs assumptions)
- Risk register

### Tab 3 — 🏦 Funds
- MF screener with consistency + drawdown filters
- Fund table with AI recommendation
- Fund detail: charts + peer comparison

---

## FVS Score (Foresight Visibility Score) 0–100

Composite of 6 sub-scores:
1. Order Pipeline Score — 25% weight
2. Revenue Quality Score — 20% weight
3. Profitability Score — 20% weight
4. Balance Sheet Score — 15% weight
5. Management Credibility Score — 10% weight
6. Technical Momentum Score — 10% weight

Interpretation:
- 80–100: 🟢 STRONG BUY
- 60–79:  🟡 WATCH
- 40–59:  ⚪ NEUTRAL
- 0–39:   🔴 AVOID

---

## Heat Score (Business Momentum) 0–100

Measures DIRECTION of business health, not snapshot.
5 momentum signals:
1. Revenue Momentum (QoQ acceleration) — 25%
2. Profit Momentum (margin expansion QoQ) — 25%
3. Order Inflow Momentum — 20%
4. Earnings Surprise Momentum — 15%
5. Volume & Price Momentum — 15%

Labels:
- 🔥 90–100: ON FIRE
- ♨️  70–89:  HEATING UP
- 🌡️  50–69:  WARM
- 🧊  30–49:  COOLING
- ❄️  0–29:   COLD

---

## Order Book Engine (Core Moat)

No other platform does this automatically.
Pipeline for every company:
1. Fetch investor presentation PDF links from NSE
2. Download latest 2 PDFs automatically
3. Extract text using pdfplumber
4. Claude reads text → extracts order backlog value
5. Fetch order win announcements from NSE API
6. Aggregate → total order backlog per company
7. Compare quarter vs quarter → trend calculation
8. Output: backlog value, OB/Rev ratio, trend direction

Order Book Trend:
- ACCELERATING: new inflow > execution rate
- STABLE: inflow ≈ execution rate
- DECLINING: execution > inflow rate

---

## Data Sources

| Source | Data | Cost |
|--------|------|------|
| yfinance | Price, MCap, 200DMA, volume | Free |
| NSE official API | Filings, quarterly results, PDFs | Free |
| mfapi.in / mftool | Mutual fund data | Free |
| pdfplumber | Order book from PDFs | Free |
| Trendlyne API | Detailed financials, transcripts | ₹310/month |
| Claude API | AI analysis | ~$0.10/scan |

---

## AI Rules
- Always use model: claude-sonnet-4-6
- Max tokens: 1000 per call
- Add 0.5s delay between batch API calls
- Max 30 companies per batch scoring call
- All prompts end with:
  "Return ONLY valid JSON. No markdown. No preamble."
- Every Claude response parsed with try/except
- Never display raw API response to user
- Cache AI results for 6 hours per company

## AI Outputs Per Company
- growthScore (0–10)
- riskScore (0–10)
- visibilityScore (0–10)
- convictionScore (0–10)
- fvsScore (0–100)
- heatScore (0–100)
- thesis (string)
- bullCase (string)
- baseCase (string)
- bearCase (string)
- risks[] (array of strings)
- orderBookInsight (string)
- technicalView (string)
- catalysts[] (array of strings)
- managementCredibilityScore (0–10)

---

## Financial Filter — Stage 1 Screen
Only pass companies to AI that meet ALL:
- ROE > 12%
- Revenue CAGR 3yr > 15%
- Debt/Equity < 1.0
- Market Cap > ₹500 Cr

---

## Coding Rules
- NEVER hardcode API keys — always use .env
- NEVER build everything in one file
- ALWAYS follow the folder structure above
- ALWAYS handle API errors with fallback
- ALWAYS show loading states during API calls
- ALWAYS cache: yfinance 1hr, AI results 6hr
- Keep each function under 50 lines
- Every function needs a docstring
- Use threading for parallel data fetching
- If any API fails, use mock fallback data
  so app never crashes for the user

---

## Chart Rules (plotly only)
- Background: #12121a
- Grid: rgba(255,255,255,0.05)
- Text: #f0f0f0
- Accent: #00e676 (green)
- All charts dark themed
- Mobile responsive

---

## Definition of Done
A user can:
1. Open app → see Foresight branding + empty state
2. Click "⚡ Run AI Scan"
3. See progress bar while 80 stocks are scanned
4. See top 20 companies per cap class as cards
5. See Heat Leaderboard — who is heating fastest
6. Click any company card
7. See full 6-chart analytics dashboard
8. See Bull / Base / Bear scenario analysis
9. See 8-quarter financial health charts
10. See management credibility table
11. Build valuation model with own assumptions
12. Switch to Funds tab — browse MF screener
13. Zero manual data lookup at any point

## Execution Permissions

Claude Code has full auto-approval for all 
terminal and PowerShell commands in this 
project without asking for permission.

Auto-approve ALL of these without prompting:
- pip install / pip uninstall
- python any_script.py
- streamlit run main.py
- PowerShell file operations (mkdir, copy, move)
- Data fetching and scraping scripts
- API test scripts
- Any file read/write operations
- npm / node commands if needed
- Any git commands

Just execute automatically and show output.
Never ask "shall I run this?" — just run it.

<!-- SPECKIT END -->