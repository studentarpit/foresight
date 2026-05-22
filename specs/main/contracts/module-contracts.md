# Module Contracts: Foresight

## universe/stocks.py
**Exports**: `STOCK_UNIVERSE: list[dict]`, `get_tickers() -> list[str]`, `get_by_sector(sector: str) -> list[dict]`
**Contract**: Each entry has keys: ticker, name, sector. No .NS suffix in ticker.

## data/collector.py
**Exports**: `collect_all(progress_cb=None) -> pd.DataFrame`, `fetch_mf_data() -> pd.DataFrame`
- `collect_all`: Returns DataFrame with all FinancialData columns. Rows that fail ALL data sources are dropped.
- `progress_cb`: Optional callable(current: int, total: int) for UI progress updates.
- Never raises — bad tickers are skipped with logging.

## data/scraper.py
**Exports**: `fetch_screener_data(ticker: str) -> dict`, `fetch_nse_filings(ticker: str) -> dict`
- Returns partial dict on scrape failure (missing keys omitted, not None-filled).

## data/pdf_extractor.py
**Exports**: `extract_investor_presentation(pdf_url: str) -> dict`
- Returns `{"orderBook": float|None, "guidance": str|None, "capex": str|None}`

## ai/prompts.py
**Exports**: `SCAN_PROMPT`, `DEEP_ANALYSIS_PROMPT`, `VALUATION_PROMPT`, `MASTER_TRACKER_PROMPT`
- All are string templates with `{placeholders}`.
- All end with: "Return ONLY valid JSON. No markdown. No explanation."

## ai/analyzer.py
**Exports**:
- `score_universe(df: pd.DataFrame) -> pd.DataFrame` — adds AI score columns
- `analyze_company(company: dict) -> dict` — returns AIAnalysis dict
- `build_valuation_model(company: dict, assumptions: dict) -> dict`
- `update_master_tracker(company: dict, quarterly_data: dict) -> dict`
- `analyze_mf(fund: dict) -> dict`
- All functions return error dict `{"error": str}` on API failure, never raise.

## ui/filters.py
**Exports**: `render_sidebar_filters() -> dict` — renders Streamlit sidebar, returns active filter state dict.

## ui/dashboard.py
**Exports**: `render_market_radar(df: pd.DataFrame, filters: dict)` — Tab 1

## ui/company_card.py
**Exports**: `render_company_deep_dive(company_row: dict, analysis: dict)` — deep dive panel

## ui/valuation_tab.py
**Exports**: `render_valuation_tab(df: pd.DataFrame)`

## ui/tracker_tab.py
**Exports**: `render_tracker_tab()`

## ui/mf_tab.py
**Exports**: `render_mf_tab(mf_df: pd.DataFrame)`
