# Spec 03 — Dashboard (Premium Redesign)

## Design Philosophy
Dark premium UI. Think Bloomberg terminal meets modern fintech.
NOT a white SaaS tool. NOT a developer dashboard.
This is a serious investment intelligence product.

## Color Palette
- Background: #0a0a0f (near black)
- Surface cards: #12121a
- Border: rgba(255,255,255,0.07)
- Primary accent: #00e676 (green — buy signals)
- Warning: #ffd740 (yellow — watch signals)
- Danger: #ff5252 (red — avoid/miss signals)
- Text primary: #f0f0f0
- Text muted: rgba(255,255,255,0.4)

## Typography
- Headlines: DM Serif Display (Google Font)
- Body: DM Sans (Google Font)
- Numbers/scores: DM Mono

## Layout
Single page app. NO page reloads.
3 tabs only at the top:
- 🔍 Discover
- 📊 Analyse
- 🏦 Funds

---

## HEADER (persistent across all tabs)

Left side:
- Foresight logo (small green hexagon icon + "Foresight" wordmark)
- Tagline: "Future Growth Radar · Indian Equity Intelligence"

Right side:
- Market status pill (NSE OPEN / NSE CLOSED)
- Last scan timestamp
- "⚡ Run AI Scan" button (green gradient)

---

## TAB 1 — 🔍 Discover
(Merges: Market Radar + Order Intelligence + 
Expectation Intelligence + Alerts)

### Section A — Summary Strip (top, full width)
4 metric cards in a row:
- Universe Scanned: e.g. "48 companies"
- Passed Filter: e.g. "21 companies"
- Strong Buys: e.g. "7 companies" (green)
- Avg Conviction: e.g. "7.4 / 10"

### Section B — Alert Banner (collapsible)
Priority-sorted alerts in a compact strip:
Each alert shows: Priority dot / Company / Signal text
Signal types to detect and display:
- 🟢 FVS enters Strong Buy zone (≥80)
- ✅ Expectation BEAT — revenue/margin above guidance
- 📈 Price above all 4 DMAs — strong uptrend
- 📊 Volume ACCUMULATING — institutional buying detected
- ❌ Expectation MISS — guidance missed by X bps
- 📉 Order book DECLINING — execution outpacing inflow
- ⚠️ Thesis at risk — 2 consecutive quarterly misses
Collapse/expand toggle. Show count badge when collapsed.

### Section C — Left Sidebar Filters
- Sector multiselect
- Market Cap (Small / Mid / Large)
- Min Conviction Score slider (0-10)
- Order Book Trend (All / Accelerating / Stable / Declining)
- Expectation Signal (All / Beat / In-line / Miss)
- Toggle: Above 200 DMA only
- Toggle: Order book accelerating only

### Section D — Ranked Company Table
Columns:
- Rank (1, 2, 3...)
- Company Name + Sector tag
- MCap
- ROE / ROCE
- Rev CAGR
- OB/Rev ratio + trend arrow (📈➡️📉)
- Exp Signal (✅ BEAT / ➡️ IN-LINE / ❌ MISS)
- 200 DMA (🟢 Above / 🔴 Below)
- FVS Score (0-100, color coded)
- Conviction (0-10, progress bar)
- Signal badge (🟢 STRONG BUY / 🟡 WATCH / 🔴 AVOID)

Clicking any row expands Company Deep Dive BELOW the table
(no new page, no new tab — inline expansion)

### Section E — Company Deep Dive (inline, on row click)

Row 1 — Header:
- Company name + ticker + sector
- Current price + % change today
- Traffic light signal with label

Row 2 — 4 Score Cards:
- Growth Score / Risk Score / Visibility Score / Conviction
- Each with colored progress bar

Row 3 — Investment Thesis:
- Green bordered box
- 2-3 sentence AI thesis

Row 4 — 3 columns side by side:
- 🐂 Bull Case
- 📊 Base Case  
- 🐻 Bear Case

Row 5 — Order Book Intelligence:
- Current OB value + OB/Revenue ratio
- Trend chart: last 4 quarters order inflow vs execution
- AI insight text: why this matters

Row 6 — Expectation Intelligence:
- Table: Last 4 quarters
  Columns: Quarter / Guided Rev / Actual Rev / 
           Guided Margin / Actual Margin / Beat/Miss
- AI commentary on management credibility

Row 7 — Technical View:
- Price vs 50 DMA / 200 DMA status
- Volume trend (accumulating / distributing)
- AI technical commentary

Row 8 — Key Catalysts + Risks:
- 2 columns: Upcoming Catalysts (green) / Key Risks (red)

---

## TAB 2 — 📊 Analyse
(Merges: Valuation Model + Master Tracker + Research Repository)

### Sub-section A — Valuation Model

Left panel — Inputs:
- Company selector dropdown (from filtered universe)
- Current price (auto-filled)
- Revenue Growth Assumption (% slider)
- Margin Expansion Assumption (% slider)
- Exit PE Multiple (number input)
- Projection Years (1-5 selector)
- "Generate Model" button (green)

Right panel — Model Output:
Projection table:
- Rows: Year 1 to Year N
- Columns: Revenue / Profit / EPS / Target Price
- 3 scenario columns: Bull / Base / Bear
- Color coded: green / yellow / red

Summary cards below table:
- Bull upside % from current price
- Base upside % from current price  
- Bear downside % from current price
- Expected CAGR for each scenario

### Sub-section B — Master Tracker

Purpose: Track if companies are delivering on their thesis

Table columns:
- Company
- Thesis Added Date
- Guided Rev vs Actual Rev (with % variance)
- Guided Margin vs Actual Margin (with % variance)
- OB Guidance vs Actual OB
- Consecutive Beats/Misses streak
- Thesis Status badge:
  🟢 ON TRACK / 🟡 WATCH / 🔴 BROKEN
- Recommended Action: HOLD / REVIEW / EXIT
- Last Updated

Add to Tracker button:
- Input: ticker + guided metrics
- System pulls actuals automatically
- Claude scores thesis status

200 DMA Alert Panel (below tracker):
- Stocks in watchlist that crossed 200 DMA this week
- Show: ticker / direction (crossed above or below) / date
- Green for above cross / Red for below cross

### Sub-section C — Research Repository

Compact card grid of saved research:
- Each card: Company name / Date / Source / Summary snippet
- Sources: NSE filing / Investor presentation / Annual report
- Search bar to find across all saved research
- Tag filter: by sector or company
- Click card to expand full extracted content

---

## TAB 3 — 🏦 Funds
(MF Screener — standalone, unchanged from spec 02)

### Filters Sidebar:
- Category (Small Cap / Mid Cap / Flexi Cap / Sectoral)
- Min 10yr return (%)
- Max drawdown limit (%)
- Min consistency score

### Fund Table columns:
- Fund Name
- Category
- AUM
- 1yr / 3yr / 5yr / 10yr returns
- Max Drawdown
- Consistency Score
- AI Recommendation badge

Clicking a fund shows:
- AI reasoning card
- Year-by-year return bar chart
- Drawdown history chart
- Peer comparison

---

## Streamlit Implementation Rules
- Dark theme: set via config.toml
  [theme]
  base="dark"
  backgroundColor="#0a0a0f"
  secondaryBackgroundColor="#12121a"
  primaryColor="#00e676"
  textColor="#f0f0f0"

- Use st.tabs() for 3 tab structure
- Use st.session_state for ALL cached data
- Use st.spinner() for every API call
- Use st.columns() for side by side layouts
- Use st.expander() for collapsible sections
- Use plotly for all charts (not matplotlib)
- Load Google Fonts via st.markdown with unsafe_allow_html=True

## Definition of Done
- streamlit run main.py launches with no errors
- Dark theme renders correctly on first load
- All 3 tabs render with correct layout
- AI Scan completes within 90 seconds
- Company deep dive expands inline without page reload
- Valuation model generates in under 10 seconds
- Master Tracker updates thesis status correctly
- No feature from previous spec is missing