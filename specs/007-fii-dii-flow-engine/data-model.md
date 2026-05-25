# Data Model: Spec 07 — FII/DII Flow Intelligence Engine

## Entities

### FII/DII Daily Flow
Source: `fetch_fii_dii_daily()` → `data/fii_dii_engine.py`

```python
{
  "fii": {
    "gross_buy":  float,   # ₹ Cr gross purchases
    "gross_sell": float,   # ₹ Cr gross sales
    "net":        float,   # positive = net buyer, negative = net seller
    "date":       str,     # ISO date string from NSE
  },
  "dii": {
    "gross_buy":  float,
    "gross_sell": float,
    "net":        float,
    "date":       str,
  },
  "market_sentiment": "RISK_ON" | "RISK_OFF" | "NEUTRAL"
  # RISK_ON: combined net > +500 Cr
  # RISK_OFF: combined net < -500 Cr
  # NEUTRAL: otherwise
}
```

Cache key: `("global", "fii_dii_daily")` · TTL: 3600s

---

### Shareholding Quarter
Source: `fetch_shareholding_pattern(symbol)` → returns `list[ShareholdingQuarter]`

```python
{
  "quarter":              str,            # e.g. "Mar 2025"
  "fii_pct":              float | None,   # % of total shares held by FII/FPI
  "dii_pct":              float | None,   # % held by DII
  "promoter_pct":         float | None,   # % held by Promoters
  "public_pct":           float | None,   # % held by Public/Retail
  "fii_change_qoq":       float | None,   # percentage point change vs prev quarter
  "dii_change_qoq":       float | None,
  "promoter_change_qoq":  float | None,
  "public_change_qoq":    float | None,
}
```

Ordered oldest-first. Maximum 8 quarters returned.
Cache key: `(symbol, "shareholding")` · TTL: 21600s (6h)

---

### Bulk/Block Deal
Source: `fetch_bulk_block_deals(symbol)` / `_fetch_market_bulk_deals()`

```python
{
  "ticker":      str,                          # NSE symbol
  "date":        str,                          # deal date
  "deal_type":   "BULK" | "BLOCK",
  "client":      str,                          # entity name (raw from NSE)
  "side":        "B" | "S" | "BUY" | "SELL",
  "quantity":    int,
  "price":       float,                        # ₹ per share
  "value_cr":    float,                        # ₹ Cr = quantity × price / 1e7
  "entity_type": "FII" | "DII" | "MF" | "HNI" | "UNKNOWN"
}
```

Cache key: `(symbol, "bulk_block")` · TTL: 3600s

---

### Accumulation/Distribution Signal
Source: `detect_accumulation_distribution(symbol)`

```python
{
  "pattern":             "ACCUMULATING" | "DISTRIBUTING" | "NEUTRAL",
  "pattern_strength":    "HIGH" | "MEDIUM" | "LOW",
  "duration_quarters":   int,      # consecutive quarters in same direction (FII)
  "fii_trend":           "INCREASING" | "DECREASING" | "STABLE",
  "dii_trend":           "INCREASING" | "DECREASING" | "STABLE",
  "combined_signal":     "STRONG_BUY" | "BUY" | "NEUTRAL" | "SELL" | "STRONG_SELL",
  "smart_money_verdict": str,      # human-readable 1-sentence summary
  "fii_last_qoq":        float | None,
  "dii_last_qoq":        float | None,
}
```

Cache key: `(symbol, "accum_dist")` · TTL: 21600s

---

### Flow Score
Source: `compute_flow_score(symbol)` → `Optional[int]`

```
Returns None when shareholding data is unavailable.
Returns int 0–100 when data exists.

Component weights:
  FII trend direction    30%  (INCREASING=30, STABLE=15, DECREASING=0)
  DII trend direction    25%  (INCREASING=25, STABLE=12, DECREASING=0)
  Duration of pattern    20%  (capped at 4 quarters; penalised if DISTRIBUTING)
  Bulk/block activity    15%  (FII/DII/MF deals only; UNKNOWN excluded)
  Signal strength        10%  (HIGH=10, MEDIUM=5, LOW=0; inverted if DISTRIBUTING)

Interpretation:
  80–100  Strong Accumulation   (green)
  60–79   Mild Accumulation     (yellow)
  40–59   Neutral               (grey)
  20–39   Distribution Beginning (orange)
  0–19    Heavy Distribution    (red)
  None    N/A — no data         (grey, excluded from rankings)
```

Cache key: `(symbol, "flow_score")` · TTL: 21600s

**Relationship to FVS**: Flow Score is a parallel metric. It is NOT blended into FVS. FVS remains a 6-component score with unchanged weights.

---

### AI Pattern Insight
Source: Claude via `FII_DII_PATTERN_PROMPT` in `ai/prompts.py`

```python
{
  "accumulation_score":        int,      # 0–100
  "distribution_score":        int,      # 0–100
  "smart_money_verdict":       str,
  "pattern_duration_quarters": int,
  "fii_conviction":            "HIGH" | "MEDIUM" | "LOW",
  "dii_conviction":            "HIGH" | "MEDIUM" | "LOW",
  "combined_signal":           "STRONG_BUY" | "BUY" | "NEUTRAL" | "SELL" | "STRONG_SELL",
  "historical_insight":        str,
  "price_impact_prediction":   str,
  "positional_opportunity":    bool,
  "confidence":                int,      # 0–100
  "reasoning":                 str,
}
```

Cache key: `(symbol, "fii_ai_analysis")` · TTL: 21600s

---

## State Transitions

```
No data → shareholding fetch → QoQ computed → accumulation signal → flow score → AI insight
                ↓ (fails)
           None flow score → N/A displayed
```

---

## Relationships to Existing Models

| Existing Entity | Relationship |
|----------------|--------------|
| `scan_results` DataFrame | `flowScore` column added (Optional[int]) |
| FVS Score | No change — Flow Score is parallel, not blended |
| Company card (Discover tab) | Displays `smart_money_card_html()` from `ui/components.py` |
| Analyse tab | Sections 10 (shareholding chart) + 11 (AI smart money) appended |
| Sentiment tab | Bulk deal feed + flow heatmap sections appended |
