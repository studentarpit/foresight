# Research: Spec 07 — FII/DII Flow Intelligence Engine

## API Availability Findings

### Decision: NSE FII/DII Daily API
- **Chosen**: `https://www.nseindia.com/api/fiidiiTradeReact`
- **Rationale**: Confirmed working via live probe. Requires cookie session (GET homepage first, then data endpoint).
- **Actual field names**: `buyValue`, `sellValue`, `netValue`, `category` — NOT the spec's assumed `netPurchasesSales`/`grossPurchase`/`grossSales`
- **Alternatives considered**: NSE website scrape (fragile HTML), paid Trendlyne API (deferred)

### Decision: Shareholding Pattern Source
- **Chosen**: screener.in `#shareholding` section via HTML scraping
- **Rationale**: NSE shareholding APIs (`/api/corporate-share-holding-pattern`, `/api/shareholdingPattern`, etc.) all return 404. screener.in returns clean tabular HTML with quarterly data.
- **Parsing**: `section#shareholding table tr` — first row is headers (quarter labels), subsequent rows are entity categories ("Promoters+", "FIIs+", "DIIs+", "Public+"). Values have `%` suffix; strip before `float()` conversion.
- **Alternatives considered**: BSE API (same 404 problem), Trendlyne (paid, deferred)

### Decision: Bulk/Block Deal Source
- **Chosen**: NSE `/api/bulkdeals` (market-wide), filter by ticker symbol
- **Rationale**: `/api/bulkdeals` and `/api/blockdeals` both return 404 via direct call but may work if session cookie is present. Implemented with session-based attempt; empty list returned gracefully on failure.
- **Limitation**: Stock-level bulk history unavailable without paid source. Market-wide deals filtered by ticker gives recent activity only.
- **Alternatives considered**: Screener.in bulk deals page (no structured API), Trendlyne (paid, deferred)

---

## Implementation Decisions (from Clarification Session 2026-05-26)

### Decision: Flow Score not merged into FVS
- **Chosen**: Flow Score displayed as a standalone parallel metric alongside FVS
- **Rationale**: Merging as a 7th FVS component would reshuffle all existing company rankings and break historical comparability. Complementary signal, not replacement.

### Decision: FII/DII strip when no data
- **Chosen**: Hide strip silently — render nothing until data is cached
- **Rationale**: Strip is in persistent header on all tabs; a broken or loading state there is more disruptive than absence. Strip reappears automatically once NSE API responds.

### Decision: Flow Score when no shareholding data
- **Chosen**: Return `None` (displayed as N/A), excluded from heatmap ranking
- **Rationale**: Substituting 50 (neutral) creates false signal. N/A is transparent and prevents data-absent stocks from polluting ranked displays.

### Decision: UNKNOWN entities in bulk scoring
- **Chosen**: Exclude — only FII, DII, MF entity types count toward bulk score component
- **Rationale**: Unknown entity type (retail HNI, arbitrageur, nominee account) provides no institutional conviction signal. Including them dilutes the metric's precision.

### Decision: Parallel shareholding fetch
- **Chosen**: `ThreadPoolExecutor(max_workers=4)` with 0.5s stagger between thread starts
- **Rationale**: Total HTTP requests are identical to sequential (20 = 20). Parallel reduces wall time from ~25s to ~5s. Stagger prevents screener.in rate-limiting. screener.in is free — no billing impact. Matches existing `quarterly_fetcher.py` pattern.

---

## Cache TTL Decisions

| Cache Key | TTL | Rationale |
|-----------|-----|-----------|
| `fii_dii_daily` | 1h | NSE data updates after market close; 1h balances freshness vs API load |
| `shareholding` | 6h | Quarterly filings; once fetched per session is sufficient |
| `bulk_block` | 1h | Deal data can be stale for hours without material signal change |
| `accum_dist` | 6h | Derived from shareholding; same cadence |
| `flow_score` | 6h | Derived metric; recomputes only when underlying data refreshes |
| `bulk_deals_raw` | 1h | Market-wide raw deal list; shared across all stock queries |

---

## Entity Classification Heuristic

Rule-based keyword matching on client name (case-insensitive):
- **FII**: blackrock, vanguard, goldman, morgan, fidelity, templeton, aberdeen, jpmorgan, merrill, ubs, societe, nomura, macquarie, barclays, fii, fpi
- **DII**: lic, sbi, life insurance, general insurance, nps, epfo, uti, psu, nippon, mirae, hdfc mf, icici mf, kotak mf, dii, mutual fund, asset management, amc
- **HNI**: hni, promoter, family office
- **UNKNOWN**: no keyword matched → excluded from Flow Score bulk component

---

## screener.in Symbol Mapping

Known mismatches between NSE ticker and screener.in slug:

| NSE Ticker | screener.in Slug |
|-----------|-----------------|
| STERLINWILS | SWSOLAR |

Other tickers map 1:1. Falls back to consolidated view, then standalone view.
