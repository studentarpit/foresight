# Public API Contract: data/fii_dii_engine.py

## Functions

### fetch_fii_dii_daily() → dict
Returns market-wide FII/DII daily flow. Empty dict on failure (never raises).
Cache: `("global", "fii_dii_daily")` · 1h TTL.

### fetch_shareholding_pattern(symbol: str) → list[dict]
Returns last 8 quarters of shareholding data for `symbol` from screener.in.
Returns `[]` on failure. Each dict: see data-model.md `ShareholdingQuarter`.

### fetch_bulk_block_deals(symbol: str) → list[dict]
Returns bulk/block deals for `symbol` filtered from market-wide data.
Returns `[]` when no deals found or API unavailable.

### detect_accumulation_distribution(symbol: str) → dict
Returns accumulation/distribution signal. Falls back to `_empty_accum()` dict (all NEUTRAL/LOW/0) when fewer than 2 quarters available.

### compute_flow_score(symbol: str) → Optional[int]
Returns `None` when shareholding data unavailable. Returns `int` 0–100 otherwise.
**Never raises** — all exceptions caught internally.

### prefetch_flow_data_batch(symbols: list[str], max_workers: int = 4) → None
Pre-warms shareholding + accum_dist cache for a list of symbols in parallel.
0.5s stagger between thread starts. No return value; results go to disk cache.

### flow_score_label(score: Optional[int]) → tuple[str, str]
Returns `(label_str, colour_class_str)`. Handles `None` → `("N/A", "grey")`.

## Invariants

- All functions are **cache-first**: check TTL cache before any HTTP request.
- **No side effects on failure**: exceptions logged at DEBUG, empty/None returned.
- `compute_flow_score` returns `None` (not 50) when no data — callers must handle `None`.
- Only FII, DII, MF entity types count in bulk score; UNKNOWN is excluded.
- Flow Score is a standalone metric and must NOT be added to FVS calculation.
