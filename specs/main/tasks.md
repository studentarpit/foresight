---
description: "Task list for Foresight"
---

# Tasks: Foresight

**Input**: Design documents from `specs/main/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**User Stories** (from Definition of Done in CLAUDE.md):
- **US1**: Open app → click "Run AI Scan" → see companies ranked by AI conviction score
- **US2**: Click any company → see full bull/bear/base case analysis
- **US3**: Valuation Model tab — build 3-scenario DCF for any company
- **US4**: Master Tracker tab — track thesis integrity over time
- **US5**: MF Screener tab — discover consistent Indian mutual funds

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[Story]**: User story this task belongs to

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton, dependencies, environment config

- [x] T001 Create all package directories: `universe/`, `data/`, `ai/`, `ui/` with `__init__.py` files
- [x] T002 Create `requirements.txt` with: streamlit, yfinance, pdfplumber, requests, beautifulsoup4, anthropic, pandas, python-dotenv, plotly
- [x] T003 Create `.env.example` with `ANTHROPIC_API_KEY=your-key-here`
- [x] T004 [P] Create `.gitignore` excluding `.env`, `__pycache__`, `*.pyc`, `data/tracker.json`

**Checkpoint**: `pip install -r requirements.txt` runs without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data layer and AI infrastructure — must complete before any UI story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `universe/stocks.py` — define `STOCK_UNIVERSE` list (50 stocks across 6 sectors: Defence, Railways, EPC, EMS, Power, Solar/Wind) with ticker/name/sector/mcap_category fields. Export `get_tickers()` and `get_by_sector(sector)`
- [x] T006 Create `data/scraper.py` — implement `fetch_screener_data(ticker)` that scrapes screener.in public page for ROE, ROCE, revenue CAGR, D/E. Add 2s delay + User-Agent header. Return partial dict on failure (do not raise)
- [x] T007 [P] Create `data/pdf_extractor.py` — implement `extract_investor_presentation(pdf_url)` using pdfplumber. Return `{"orderBook": float|None, "guidance": str|None, "capex": str|None}`
- [x] T008 Create `data/collector.py` — implement `collect_all(progress_cb=None)`:
  - Iterate stocks from universe
  - Fetch yfinance data (price, MCap, PE, compute 200 DMA from 1yr history)
  - Call fetch_screener_data() with fallback to yfinance info dict
  - Compute orderBookTrend: ACCELERATING/STABLE/DECLINING based on inflow vs execution rate
  - Apply Stage 1 filter (ROE > 12%, RevCAGR > 15%, D/E < 1.0, MCap > 500Cr)
  - Call progress_cb(current, total) if provided
  - Skip bad tickers; never raise
  - Return filtered DataFrame with all FinancialData columns
- [x] T009 [P] Create `data/collector.py` — add `fetch_mf_data()` function that calls mfapi.in, computes 1yr/3yr/5yr/10yr returns from NAV history, computes max drawdown and consistency score. Skip funds with < 3yr history
- [x] T010 Create `ai/prompts.py` — define 4 prompt constants:
  - `SCAN_PROMPT` — batch scoring, expects JSON array output
  - `DEEP_ANALYSIS_PROMPT` — full company analysis, expects full AIAnalysis JSON
  - `VALUATION_PROMPT` — 3-scenario DCF, expects bull/base/bear JSON
  - `MASTER_TRACKER_PROMPT` — thesis integrity scoring
  - `MF_ANALYSIS_PROMPT` — MF consistency scoring
  - All end with: "Return ONLY valid JSON. No markdown. No explanation."
- [x] T011 Create `ai/analyzer.py` — implement `score_universe(df)`:
  - Iterate filtered DataFrame rows
  - Call Claude `claude-sonnet-4-20250514` with SCAN_PROMPT per batch
  - Add 0.5s delay between calls; max 30 companies
  - Parse JSON response; add growthScore/riskScore/visibilityScore/convictionScore columns
  - On API error return row with error dict, never raise
- [x] T012 [P] Create `ai/analyzer.py` — add `analyze_mf(fund)` function:
  - Call Claude with MF_ANALYSIS_PROMPT
  - Return `{consistencyScore, drawdownRisk, recommendation, reasoning}`
  - Return error dict on failure

**Checkpoint**: `python -c "from data.collector import collect_all; from ai.analyzer import score_universe; print('imports OK')"` runs without errors

---

## Phase 3: User Story 1 — AI Scan + Market Radar (Priority: P1) 🎯 MVP

**Goal**: User clicks "Run AI Scan", sees companies ranked by AI conviction score with filters

**Independent Test**: `streamlit run main.py` → Tab 1 loads → Run AI Scan completes → ranked table appears with conviction scores

### Implementation for User Story 1

- [x] T013 [US1] Create `ai/analyzer.py` — add `analyze_company(company)` function returning full AIAnalysis JSON (growthScore, riskScore, visibilityScore, convictionScore, thesis, bullCase, baseCase, bearCase, risks[], orderBookInsight, technicalView, catalysts[])
- [x] T014 [P] [US1] Create `ui/filters.py` — implement `render_sidebar_filters()`:
  - Sector multiselect (all 6 sectors)
  - MCap category (Small/Mid/Large checkboxes)
  - Min Conviction Score slider (0.0–10.0)
  - Order Book Trend multiselect (All/ACCELERATING/STABLE/DECLINING)
  - Above 200 DMA toggle
  - Return active filter state as dict
- [x] T015 [US1] Create `ui/dashboard.py` — implement `render_market_radar(df, filters)`:
  - Apply active filters to DataFrame
  - Summary row: Total Scanned / Passed Filter / Strong Buys (conviction ≥ 7) / Avg Conviction
  - Ranked table: Rank, Company, Sector, MCap, ROE, Rev CAGR, OB/Rev, OB Trend (📈/➡️/📉), 200DMA (✅/❌), Conviction, Signal (🟢/🟡/🔴)
  - Signal: 🟢 conviction ≥ 7, 🟡 conviction 5–7, 🔴 conviction < 5
  - Store selected company ticker in `st.session_state["selected_ticker"]` on row click
- [x] T016 [US1] Create `main.py` — wire Tab 1:
  - Load .env, set up st.session_state keys (scan_results, selected_ticker, mf_data, tracker)
  - st.tabs() for 4 tabs
  - "Run AI Scan" button in Tab 1: call collect_all() with progress bar → score_universe() → store in session_state
  - st.spinner() during scan
  - Never re-run scan on rerender (check session_state)
  - Call render_sidebar_filters() + render_market_radar()

**Checkpoint**: Full scan runs, table renders, filters work, signal badges appear correctly

---

## Phase 4: User Story 2 — Company Deep Dive (Priority: P2)

**Goal**: Clicking a company row shows full bull/bear/base case analysis panel

**Independent Test**: After scan, click any company row → deep dive panel appears with all AI scores, thesis, bull/base/bear cases, risks, catalysts

### Implementation for User Story 2

- [x] T017 [US2] Create `ui/company_card.py` — implement `render_company_deep_dive(company_row, analysis)`:
  - 4 horizontal score bars: Growth / Risk / Visibility / Conviction (st.progress)
  - Investment Thesis in green-bordered expander
  - 3 st.columns for Bull Case / Base Case / Bear Case
  - Risks as bulleted list
  - Order Book Insight and Technical View sections
  - Key Catalysts (2 items)
  - Show spinner while analysis is loading
- [x] T018 [US2] Update `main.py` — wire deep dive:
  - When `st.session_state["selected_ticker"]` is set, call `analyze_company()` with st.spinner
  - Cache result in `st.session_state["company_analyses"][ticker]` to avoid repeat API calls
  - Call `render_company_deep_dive()` below the ranked table
  - If analyze_company returns error dict, show st.warning with fallback message

**Checkpoint**: Click any row → spinner shows → all AI fields render (no raw JSON visible)

---

## Phase 5: User Story 3 — Valuation Model (Priority: P3)

**Goal**: Tab 2 lets user build a 3-scenario valuation model for any company without Excel

**Independent Test**: Select company from dropdown → enter assumptions → click "Generate Model" → bull/base/bear table renders with target prices and CAGR

### Implementation for User Story 3

- [x] T019 [US3] Create `ai/analyzer.py` — add `build_valuation_model(company, assumptions)`:
  - Call Claude with VALUATION_PROMPT
  - Claude generates 3 scenarios: bull (×1.3), base (as-is), bear (×0.7)
  - Return `{bull: {revenue[], profit[], targetPrice, cagr}, base: {...}, bear: {...}}`
  - Return error dict on failure
- [x] T020 [US3] Create `ui/valuation_tab.py` — implement `render_valuation_tab(df)`:
  - Left column: dropdown of companies from filtered df + 4 input fields (revenue growth %, margin expansion %, exit PE, projection years 1-5) + "Generate Model" button
  - Right column: bull/base/bear projection table (Year 1..N × Revenue/Profit/EPS/Target Price)
  - Show expected CAGR per scenario
  - Show upside % from current price (colour: green/yellow/red)
  - st.spinner during model generation
  - Store model result in `st.session_state["valuation_models"][ticker]`
- [x] T021 [US3] Update `main.py` — wire Tab 2 to call `render_valuation_tab()`

**Checkpoint**: Generate Model for any company → 3-scenario table appears colour-coded

---

## Phase 6: User Story 4 — Master Tracker (Priority: P4)

**Goal**: Tab 3 tracks thesis integrity — guided vs actual delivery, with ON TRACK/WATCH/BROKEN status

**Independent Test**: Add a company to tracker → enter guided metrics → status shows ON TRACK → modify actuals to show big miss → status changes to BROKEN

### Implementation for User Story 4

- [x] T022 [US4] Create `ai/analyzer.py` — add `update_master_tracker(company, quarterly_data)`:
  - Call Claude with MASTER_TRACKER_PROMPT
  - Compare guided vs actual (revenue, margin, order book)
  - Return `{thesisStatus, thesisColor, guidanceAccuracy, commentary, action}`
  - Return error dict on failure
- [x] T023 [US4] Create `ui/tracker_tab.py` — implement `render_tracker_tab()`:
  - Load tracker from `data/tracker.json` (create empty if missing)
  - Display tracker table with status badges: 🟢 ON TRACK / 🟡 WATCH / 🔴 BROKEN
  - "Add Company" form: ticker input + 6 guided metric fields → calls update_master_tracker() → saves to tracker.json
  - "Refresh Status" button: re-runs update_master_tracker() for each entry
  - 200 DMA Alert Panel: show watchlist stocks that crossed 200 DMA (compare price vs DMA from session_state)
  - st.spinner during Claude calls
- [x] T024 [US4] Update `main.py` — wire Tab 3 to call `render_tracker_tab()`

**Checkpoint**: Add/update entries, status badges correct, tracker.json persists between sessions

---

## Phase 7: User Story 5 — MF Screener (Priority: P5)

**Goal**: Tab 4 discovers consistent Indian mutual funds with AI-scored recommendations

**Independent Test**: Tab 4 loads MF data → filters work → click a fund → AI reasoning and charts appear

### Implementation for User Story 5

- [x] T025 [US5] Create `ui/mf_tab.py` — implement `render_mf_tab(mf_df)`:
  - Sidebar filters: category multiselect, min 10yr return %, max drawdown %, min consistency score
  - Filtered table: Fund Name, Category, AUM, 1yr/3yr/5yr/10yr returns, Max Drawdown, Consistency Score, AI Recommendation badge (STRONG 🟢/MODERATE 🟡/AVOID 🔴)
  - Row click → show AI reasoning + plotly bar chart of year-by-year returns + plotly line chart for drawdown history
  - st.spinner while loading AI analysis
- [x] T026 [US5] Update `main.py` — wire Tab 4:
  - Fetch MF data on first load (or with "Refresh MF Data" button), store in session_state
  - Run analyze_mf() for each fund (batch, with spinner)
  - Cache results in session_state["mf_analyses"]
  - Call `render_mf_tab(mf_df)`

**Checkpoint**: Tab 4 loads, filter sliders work, clicking a fund shows charts and AI reasoning

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final wiring, UX polish, error hardening across all tabs

- [x] T027 Add Foresight logo text + tagline to main.py header (st.markdown with custom CSS)
- [x] T028 [P] Add `st.set_page_config()` in main.py: title "Foresight", layout="wide", page_icon="🔍"
- [x] T029 [P] Add graceful error display: wrap all render_* calls in try/except, show st.error() on failure
- [x] T030 [P] Create `scraper.py` — add `fetch_nse_filings(ticker)` for order win announcements (used as supplementary data in collector)
- [x] T031 Validate `.env` loading in main.py with clear error message if `ANTHROPIC_API_KEY` is missing
- [x] T032 [P] Add `data/tracker.json` auto-creation logic in tracker_tab.py if file missing
- [x] T033 Run `streamlit run main.py` smoke test — confirm all 4 tabs render without errors, no raw JSON visible

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundation)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1 — Market Radar)**: Depends on Phase 2 (collector + score_universe complete)
- **Phase 4 (US2 — Deep Dive)**: Depends on Phase 3 (analyze_company added, session_state wired)
- **Phase 5 (US3 — Valuation)**: Depends on Phase 2 (independent of US1/US2)
- **Phase 6 (US4 — Tracker)**: Depends on Phase 2 (independent of other stories)
- **Phase 7 (US5 — MF Screener)**: Depends on T009/T012 (fetch_mf_data + analyze_mf)
- **Phase 8 (Polish)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 completes
- **US2 (P2)**: Depends on US1 (session_state["selected_ticker"] set by US1)
- **US3 (P3)**: Can start after Phase 2 — independent of US1/US2
- **US4 (P4)**: Can start after Phase 2 — independent
- **US5 (P5)**: Depends on T009 + T012 from Phase 2

### Parallel Opportunities

- T006, T007, T009, T012 can run in parallel within Phase 2
- T014 can run in parallel with T013 in Phase 3
- US3, US4, US5 can be developed in parallel after Phase 2 completes

---

## Parallel Example: Phase 2

```
Launch in parallel:
  Task T006: data/scraper.py — screener.in scraper
  Task T007: data/pdf_extractor.py — pdfplumber extractor
  Task T009: data/collector.py — fetch_mf_data()
  Task T012: ai/analyzer.py — analyze_mf()

Then sequentially:
  Task T008: data/collector.py — collect_all() (uses T006, T007)
  Task T011: ai/analyzer.py — score_universe() (uses T010)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundation (T005–T012)
3. Complete Phase 3: US1 Market Radar
4. Complete Phase 4: US2 Deep Dive
5. **STOP and VALIDATE**: `streamlit run main.py` — scan works, company click works
6. Deliver MVP — all Definition of Done items 1–4 satisfied

### Incremental Delivery

1. Phase 1+2 → skeleton running
2. Phase 3 (US1) → ranked table visible
3. Phase 4 (US2) → full company analysis
4. Phase 5 (US3) → valuation model
5. Phase 6 (US4) → thesis tracker
6. Phase 7 (US5) → MF screener
7. Phase 8 → polish + smoke test

---

## Notes

- No tests generated (not requested in spec)
- All Claude calls use `claude-sonnet-4-20250514` as specified in CLAUDE.md
- Never display raw API responses — always parse JSON first
- Each function must stay under 50 lines per CLAUDE.md
- Tracker persists to `data/tracker.json` — only persistence layer in MVP
- Total tasks: 33 (T001–T033)
