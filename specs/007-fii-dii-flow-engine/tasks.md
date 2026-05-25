# Tasks: FII/DII Flow Intelligence Engine

**Input**: Design documents from `specs/007-fii-dii-flow-engine/`

**Status key**: `[x]` = complete · `[ ]` = pending

**No formal test suite** (project convention). Import verification used after each file.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths in every description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Cache TTLs, parallel import, feature.json for speckit tooling

- [x] T001 Add 6 new TTL entries to `data/cache.py` (fii_dii_daily, shareholding, bulk_block, accum_dist, flow_score, bulk_deals_raw)
- [x] T002 [P] Add `concurrent.futures` import to `data/fii_dii_engine.py`
- [x] T003 Create speckit feature directory `specs/007-fii-dii-flow-engine/` and `.specify/feature.json`

**Checkpoint**: Infrastructure ready — all downstream tasks can proceed.

---

## Phase 2: Foundational (Core Engine)

**Purpose**: `data/fii_dii_engine.py` — all data functions. Blocks every UI story.

**⚠️ CRITICAL**: All US phases depend on this engine being complete.

- [x] T004 Implement `fetch_fii_dii_daily()` in `data/fii_dii_engine.py` — NSE fiidiiTradeReact, cookie session, correct fields (`buyValue`/`sellValue`/`netValue`/`category`)
- [x] T005 [P] Implement `fetch_shareholding_pattern(symbol)` in `data/fii_dii_engine.py` — screener.in `#shareholding` section, strip `%`, last 8 quarters, QoQ deltas
- [x] T006 [P] Implement `_fetch_market_bulk_deals()` + `fetch_bulk_block_deals(symbol)` in `data/fii_dii_engine.py` — NSE bulkdeals endpoint with session, filter by ticker, `_classify_entity()` keyword matcher
- [x] T007 Implement `detect_accumulation_distribution(symbol)` in `data/fii_dii_engine.py` — trend direction, duration counter, combined signal logic
- [x] T008 Implement `compute_flow_score(symbol)` in `data/fii_dii_engine.py` — returns `None` (not 50) when no shareholding data; UNKNOWN entities excluded from bulk component
- [x] T009 [P] Implement `prefetch_flow_data_batch(symbols, max_workers=4)` in `data/fii_dii_engine.py` — `ThreadPoolExecutor`, 0.5s stagger between thread starts
- [x] T010 [P] Implement `flow_score_label(score)` in `data/fii_dii_engine.py` — handles `None` → `("N/A", "grey")`
- [x] T011 Add `FII_DII_PATTERN_PROMPT` to `ai/prompts.py` (append only, no existing prompts modified)
- [x] T012 Add `flowScore` column (Optional[int]) to `score_universe()` in `ai/analyzer.py` via `_safe_flow_score()` — returns `None` on error

**Checkpoint**: Engine complete. All UI stories can now be implemented in parallel.

---

## Phase 3: US1 — FII/DII Daily Strip in Persistent Header (P1) 🎯 MVP

**Goal**: Every tab shows today's FII/DII net flow and market sentiment pill below the logo row.

**Independent Test**: Open any tab → strip renders with FII/DII figures when NSE data is available; renders nothing silently when API is unavailable.

- [x] T013 [US1] Add `_render_fii_dii_strip()` to `main.py` — calls `fetch_fii_dii_daily()`, renders FII net / DII net / combined / sentiment pill; hides silently when both nets are `None`
- [x] T014 [US1] Wire `_render_fii_dii_strip()` into `_render_header()` in `main.py` immediately after `st.markdown('<hr class="fs-header-hr">')`

**Checkpoint**: Launch app → FII/DII strip visible on all tabs.

---

## Phase 4: US2 — Shareholding Chart + AI Smart Money in Analyse Tab (P1)

**Goal**: Company deep-dive shows stacked area chart of 8 quarters of shareholding, QoQ table, and AI-powered historical pattern intelligence.

**Independent Test**: Select any company in Analyse tab → Section 10 shows shareholding chart + colour-coded QoQ table → Section 11 shows smart money signal card (rule-based without API key; AI-powered with key).

- [x] T015 [US2] Add `chart_shareholding_pattern(quarters)` to `ui/charts.py` — stacked area (FII blue / DII green / Promoter orange / Public grey), dark theme, returns `go.Figure`
- [x] T016 [US2] Add `chart_shareholding_pattern` to imports in `ui/analyse.py`
- [x] T017 [US2] Append Section 10 call `_render_shareholding_section(ticker)` to `render_analyse_tab()` in `ui/analyse.py`
- [x] T018 [US2] Implement `_render_shareholding_section(ticker)` in `ui/analyse.py` — fetches pattern, renders chart, renders accumulation signal banner, renders QoQ colour table
- [x] T019 [US2] Append Section 11 call `_render_smart_money_history(ticker, row)` to `render_analyse_tab()` in `ui/analyse.py`
- [x] T020 [US2] Implement `_render_smart_money_history()`, `_render_smart_money_fallback()`, `_render_smart_money_card()` in `ui/analyse.py` — keyword fallback when no API key; Claude analysis cached at `(ticker, "fii_ai_analysis")` 6h TTL

**Checkpoint**: Analyse tab → company selected → Sections 10 + 11 both render.

---

## Phase 5: US3 — Smart Money Card + Flow Score on Company Cards (P2)

**Goal**: Every company card on the Discover tab shows the smart money signal card and Flow Score alongside FVS.

**Independent Test**: Run scan (or use demo data) → each company card in Discover tab shows a coloured smart money signal block with FII/DII QoQ and accumulation verdict; Flow Score shows as a number or "N/A".

- [x] T021 [US3] Add `smart_money_card_html(accum, flow_score)` to `ui/components.py` — returns HTML string for company card embed; handles `None` flow score as N/A
- [x] T022 [US3] Import `smart_money_card_html` and `detect_accumulation_distribution`, `compute_flow_score` in `ui/discover.py`
- [x] T023 [US3] Call `prefetch_flow_data_batch(tickers)` in `render_discover_tab()` in `ui/discover.py` — after existing quarterly prefetch, before card render loop (max_workers=4)
- [x] T024 [US3] Inject `smart_money_card_html()` HTML into each company card in `ui/discover.py` — fetch `accum` and `flow_score` per ticker from cache (already warm after T023); append card HTML inside each card's `st.markdown` block
- [x] T025 [US3] Display Flow Score in company header in `_render_company_header()` in `ui/analyse.py` — add `flow_score_label()` badge next to FVS badge in the header HTML

**Checkpoint**: Discover tab → company cards each show smart money signal block + Flow Score chip.

---

## Phase 6: US4 — Bulk Deal Feed + Flow Heatmap in Sentiment Tab (P2)

**Goal**: Sentiment tab shows a live bulk/block deal card feed and a colour-coded per-stock flow heatmap grid.

**Independent Test**: Open Sentiment tab → below the signal feed, a deal feed renders (or "No data" gracefully) and a heatmap grid shows all tracked stocks coloured by flow score.

- [x] T026 [US4] Add `_render_bulk_deal_feed()` to `ui/sentiment_dashboard.py` — calls `_fetch_market_bulk_deals()`, renders deal cards (ticker / client / side badge / value / date); entity icon by type
- [x] T027 [US4] Add `_render_flow_heatmap(tickers)` to `ui/sentiment_dashboard.py` — 4-column grid; `None` score shown as ⚪ N/A greyed out; non-None scored and coloured
- [x] T028 [US4] Wire both into `render_sentiment_tab()` in `ui/sentiment_dashboard.py` — below existing signal feed, two-column layout: deals left, heatmap right

**Checkpoint**: Sentiment tab → bulk deal feed + flow heatmap both render.

---

## Phase 7: US5 — Smart Money Positional Alert (P3)

**Goal**: When FII has been accumulating for 2+ consecutive quarters AND a fresh bulk deal BUY from a known FII entity is detected for the same stock, trigger an enhanced positional alert.

**Independent Test**: Manually inject a test case via `data/alerts.py` with a stock that has FII trend INCREASING for 3 quarters + a matching bulk BUY deal → alert appears at top of Discover tab.

- [x] T029 [US5] Add `detect_smart_money_alerts(scan_df)` to `data/alerts.py` — for each ticker: fetch `accum_dist` (from cache, no new HTTP), check `duration_quarters >= 2` and `fii_trend == "INCREASING"`, then check `fetch_bulk_block_deals()` for a FII/DII BUY within last 30 days
- [x] T030 [US5] Format smart money alert dict in `data/alerts.py`: `{ type: "SMART_MONEY_ACCUMULATION", ticker, message, fii_change_pct, duration_quarters, deal_entity, deal_value_cr, deal_date }`
- [x] T031 [US5] Call `detect_smart_money_alerts(scan_df)` in `_run_scan()` in `main.py` — merge returned alerts into existing `alerts` list (do not replace; append unique)
- [x] T032 [US5] Render smart money alert banner in Discover tab alert section in `ui/discover.py` — distinguish `SMART_MONEY_ACCUMULATION` type from other alerts with 🚨 icon and teal border

**Checkpoint**: Trigger conditions met → 🚨 SMART MONEY ACCUMULATION ALERT banner appears on Discover tab.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T033 [P] Verify all import chains: `python -c "from data.fii_dii_engine import *; from ui.sentiment_dashboard import render_sentiment_tab; from ui.analyse import render_analyse_tab; from ui.discover import render_discover_tab; print('OK')"`
- [x] T034 [P] Verify `flowScore` column present in `score_universe()` output: `python -c "import pandas as pd; from ai.analyzer import _safe_flow_score; print(_safe_flow_score('BEL', lambda t: None))"`
- [x] T035 Clear stale cache entries before final demo: delete `cache/*.json` files older than 6h
- [ ] T036 Merge `007-fii-dii-flow-engine` → `feature-foresight` after all tasks complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — complete immediately
- **Phase 2 (Foundational engine)**: Depends on Phase 1 — **BLOCKS all US phases**
- **Phase 3–7 (User Stories)**: All depend on Phase 2; US phases can run in parallel
- **Phase 8 (Polish)**: Depends on all desired US phases done

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|-----------|------------------|
| US1 (Strip) | Phase 2 engine | US2, US4 |
| US2 (Analyse sections) | Phase 2 engine | US1, US4 |
| US3 (Cards) | US2 functions in components.py | — |
| US4 (Sentiment tab) | Phase 2 engine | US1, US2 |
| US5 (Alert) | Phase 2 engine + US3 | — |

### Completion Status

| Story | Status | Remaining |
|-------|--------|-----------|
| US1 — FII/DII strip | ✅ Complete | — |
| US2 — Analyse sections 10+11 | ✅ Complete | — |
| US3 — Smart money on cards | ✅ Complete | — |
| US4 — Bulk feed + heatmap | ✅ Complete | — |
| US5 — Positional alert | ✅ Complete | — |

---

## Parallel Opportunities

```text
# Phase 2 — run together:
T005 fetch_shareholding_pattern()
T006 fetch_bulk_block_deals()
T009 prefetch_flow_data_batch()
T010 flow_score_label()
T011 FII_DII_PATTERN_PROMPT

# Phase 5 — run together after T021:
T022 discover.py imports
T025 analyse.py header badge

# Phase 8 — run together:
T033 import chain verification
T034 flowScore column verification
```

---

## Implementation Strategy

### MVP (already delivered — US1 + US2 + US4)
1. ✅ Phase 1 Setup
2. ✅ Phase 2 Engine
3. ✅ Phase 3 US1 — FII/DII strip in header
4. ✅ Phase 4 US2 — Shareholding chart + smart money in Analyse
5. ✅ Phase 6 US4 — Bulk feed + heatmap in Sentiment

### Remaining Increment (US3 + US5)
6. Phase 5 US3 — Wire smart money card into company cards (T022–T025)
7. Phase 7 US5 — Smart money positional alert (T029–T032)
8. Phase 8 Polish — Import verification + merge

### Single-Developer Sequence for Remaining Work
```
T022 → T023 → T024 → T025   (US3, ~30 min)
T029 → T030 → T031 → T032   (US5, ~45 min)
T033 → T034 → T035 → T036   (Polish + merge, ~15 min)
```

---

## Notes

- `[P]` tasks touch different files — safe to implement in any order or concurrently
- `[x]` tasks are verified complete (import-checked); do not re-implement
- T023 (`prefetch_flow_data_batch`) must run before T024 (card render) — cache must be warm
- T029–T032 (US5 alert) can be skipped for MVP delivery; alerts still fire for existing alert types
- All HTTP fetches are cache-first — repeat runs within TTL window are instant
- After T036 (merge), delete branch: `git branch -d 007-fii-dii-flow-engine`
