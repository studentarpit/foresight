# Data Model: WIGA Future Growth Radar

## Core Entities

### StockUniverse (universe/stocks.py)
```python
{
  "ticker": str,        # NSE ticker without .NS (e.g. "BEL")
  "name": str,          # Company display name
  "sector": str,        # One of: Defence|Railways|EPC|EMS|Power|Solar/Wind
  "mcap_category": str  # Small (<2000Cr) | Mid (2000-20000Cr) | Large (>20000Cr)
}
```

### FinancialData (output of data/collector.py)
```python
{
  "ticker": str,
  "name": str,
  "sector": str,
  "mcap": float,           # Crores
  "roe": float,            # Percentage
  "roce": float,           # Percentage
  "revcagr": float,        # 3yr Revenue CAGR %
  "profitcagr": float,     # 3yr Profit CAGR %
  "debtEq": float,         # Debt/Equity ratio
  "orderBookRev": float,   # Order book / TTM revenue ratio (None if unavailable)
  "orderBookTrend": str,   # ACCELERATING | STABLE | DECLINING
  "price": float,          # Current price (INR)
  "pe": float,             # Trailing PE
  "above200dma": bool,     # Price > 200 DMA
  "screenerUrl": str       # screener.in URL
}
```

### AIAnalysis (output of ai/analyzer.py)
```python
{
  "ticker": str,
  "growthScore": float,       # 0-10
  "riskScore": float,         # 0-10 (lower = less risky)
  "visibilityScore": float,   # 0-10
  "convictionScore": float,   # 0-10
  "thesis": str,
  "bullCase": str,
  "baseCase": str,
  "bearCase": str,
  "risks": list[str],         # 3 items
  "orderBookInsight": str,
  "technicalView": str,
  "catalysts": list[str]      # 2 items
}
```

### ValuationModel
```python
{
  "ticker": str,
  "assumptions": {
    "revenueGrowth": float,   # e.g. 0.25
    "marginExpansion": float, # e.g. 0.02
    "peMultiple": float,      # e.g. 30.0
    "years": int              # 1-5
  },
  "bull": {
    "revenue": list[float],
    "profit": list[float],
    "targetPrice": float,
    "cagr": float
  },
  "base": { ... },  # same structure
  "bear": { ... }   # same structure
}
```

### TrackerEntry (persisted to data/tracker.json)
```python
{
  "ticker": str,
  "name": str,
  "addedDate": str,          # ISO date
  "guidedRevenue": float,
  "actualRevenue": float,
  "guidedMargin": float,
  "actualMargin": float,
  "orderBookGuidance": float,
  "actualOrderBook": float,
  "thesisStatus": str,       # ON_TRACK | WATCH | BROKEN
  "thesisColor": str,        # green | yellow | red
  "guidanceAccuracy": float,
  "commentary": str,
  "action": str,             # HOLD | REVIEW | EXIT
  "lastUpdated": str         # ISO date
}
```

### MFData
```python
{
  "schemeCode": str,
  "name": str,
  "category": str,       # Small Cap | Mid Cap | Flexi Cap | Sectoral
  "aum": float,          # Crores (from mfapi metadata if available)
  "return1yr": float,
  "return3yr": float,
  "return5yr": float,
  "return10yr": float,
  "maxDrawdown": float,  # Computed from NAV history
  "consistencyScore": float,  # 0-10, years beating benchmark / total years
  "recommendation": str,      # STRONG | MODERATE | AVOID
  "aiReasoning": str
}
```

## State Transitions

### Scan State (st.session_state)
```
IDLE → SCANNING (Run AI Scan clicked)
SCANNING → FILTERED (Stage 1 filter done)
FILTERED → SCORED (AI batch scoring done)
SCORED → READY (results displayed)
READY → IDLE (new scan triggered)
```

### Thesis Status
```
(new) → ON_TRACK (initial add)
ON_TRACK → WATCH (minor slippage detected)
WATCH → ON_TRACK (recovered)
WATCH → BROKEN (significant miss)
BROKEN → EXIT (action recommended)
```

## Financial Filter Gate
```python
def passes_stage1(row) -> bool:
    return (
        row["roe"] > 12 and
        row["revcagr"] > 15 and
        row["debtEq"] < 1.0 and
        row["mcap"] > 500
    )
```
