# Spec 07 — FII & DII Flow Intelligence Engine

## Core Concept
Follow the smart money.
FII and DII buying/selling patterns reveal 
institutional conviction BEFORE price moves 
fully reflect it.

Foresight tracks:
- Who is buying/selling each stock
- For how long (accumulation vs distribution)
- At what price levels
- Whether pattern is accelerating or reversing
- What it historically meant for price

---

## Clarifications

### Session 2026-05-26
- Q: How should FVS weight be restructured when Flow Score is added as a 7th component? → A: Keep FVS unchanged (6 components, weights unmodified). Display Flow Score as a separate parallel metric alongside FVS on cards, ranked tables, and the Analyse tab header. Do not blend it into FVS.
- Q: When the FII/DII header strip has no data (API down, pre-market), what should it do? → A: Hide the strip silently — render nothing. Strip reappears automatically once data is cached.
- Q: When a stock has no shareholding data, what should Flow Score default to? → A: None (N/A) — show "N/A" on cards and exclude from heatmap ranking. Do not substitute 50; a placeholder neutral score distorts rankings.
- Q: Should bulk deals from UNKNOWN entities count toward the Flow Score bulk/block component? → A: No — exclude UNKNOWN; only FII, DII, and MF deals count. Unknown entities provide no institutional conviction signal.
- Q: Should shareholding fetches run in parallel during scan? → A: Yes — parallel, up to 4 workers, 0.5s stagger between thread starts. screener.in is free so no billing impact; total requests are identical to sequential. Matches existing quarterly-fetcher pattern.

---

## Why This Matters

FII selling + DII buying = Domestic confidence,
  possible near-term weakness but long-term hold
FII buying + DII selling = Foreign conviction,
  strong bullish signal
Both buying together = STRONGEST buy signal
Both selling together = EXIT immediately signal
FII buying after long absence = Re-rating signal

---

## Data Sources

### Free (use first)
NSE official shareholding pattern:
https://www.nseindia.com/companies-listing/
corporate-filings-shareholding-pattern

BSE shareholding pattern API:
https://api.bseindia.com/BseIndiaAPI/api/
ShareHoldingPatternData/w

NSE bulk deals:
https://www.nseindia.com/market-data/bulk-deals

NSE block deals:
https://www.nseindia.com/market-data/block-deals

NSE FII/DII daily data:
https://www.nseindia.com/market-data/fii-dii-activity

### Paid (add later)
- Trendlyne shareholding history
- Tickertape institutional data

---

## Architecture

### New File: data/fii_dii_engine.py

Function: fetch_fii_dii_daily()
Pulls market-wide FII/DII net buy/sell daily.
Returns:
{
  date: string,
  fii_net_buy_cr: float,
  fii_gross_buy_cr: float,
  fii_gross_sell_cr: float,
  dii_net_buy_cr: float,
  dii_gross_buy_cr: float,
  dii_gross_sell_cr: float,
  market_sentiment: RISK_ON/RISK_OFF/NEUTRAL
}
Cache for 1 hour during market hours.
Cache for 12 hours after market close.

Function: fetch_shareholding_pattern(symbol)
Pulls quarterly shareholding pattern from NSE/BSE.
Returns last 8 quarters:
{
  quarter: string,
  promoter_pct: float,
  fii_pct: float,
  dii_pct: float,
  retail_pct: float,
  fii_change_qoq: float,
  dii_change_qoq: float,
  promoter_change_qoq: float,
  retail_change_qoq: float
}

Function: fetch_bulk_block_deals(symbol)
Pulls bulk and block deals for specific stock.
Returns last 20 deals:
{
  date: string,
  deal_type: BULK/BLOCK,
  client_name: string,
  buy_sell: BUY/SELL,
  quantity: int,
  price: float,
  value_cr: float,
  entity_type: FII/DII/MF/HNI/UNKNOWN
}

Function: fetch_fii_dii_stock_level(symbol)
Pulls stock-specific FII/DII activity.
Some stocks have this via NSE API.
Fallback: derive from shareholding pattern changes.
Returns monthly net buy/sell for last 12 months.

Function: detect_accumulation_distribution(symbol)
Analyzes shareholding pattern + bulk deals together.
Returns:
{
  pattern: ACCUMULATING/DISTRIBUTING/NEUTRAL,
  pattern_strength: HIGH/MEDIUM/LOW,
  duration_quarters: int,
  fii_trend: INCREASING/DECREASING/STABLE,
  dii_trend: INCREASING/DECREASING/STABLE,
  combined_signal: string,
  smart_money_verdict: string
}

Function: get_historical_flow_impact(symbol)
Sends historical FII/DII pattern + price data 
to Claude.
Claude identifies: what happened to price 
last time FII accumulated/distributed this stock.
Returns pattern intelligence:
{
  historical_pattern: string,
  avg_price_impact_pct: float,
  avg_timeframe_days: int,
  reliability_score: float,
  insight: string
}

---

## AI Prompt — Add to ai/prompts.py

FII_DII_PATTERN_PROMPT:
"Analyze this FII/DII shareholding pattern 
and bulk deal history for an Indian listed company.

Identify:
1. Whether smart money is accumulating or 
   distributing
2. How long this pattern has been running
3. What the combined FII+DII signal means
4. Historical precedent — what happened to 
   price when similar pattern occurred before
5. Whether this creates a positional 
   trading opportunity

Return ONLY valid JSON:
{
  accumulation_score: 0-100,
  distribution_score: 0-100,
  smart_money_verdict: string,
  pattern_duration_quarters: int,
  fii_conviction: HIGH/MEDIUM/LOW,
  dii_conviction: HIGH/MEDIUM/LOW,
  combined_signal: STRONG_BUY/BUY/NEUTRAL/
                   SELL/STRONG_SELL,
  historical_insight: string,
  price_impact_prediction: string,
  positional_opportunity: boolean,
  confidence: 0-100,
  reasoning: string
}
Return ONLY valid JSON. No markdown. No preamble."

---

## UI Components to Add

### Component 1 — FII/DII Flow Strip
Add to persistent header (all tabs see this):
Full width strip below global cues:

🏦 FII Today: -₹1,240 Cr  
🏛️ DII Today: +₹2,180 Cr  
📊 Net: +₹940 Cr (DII absorbing FII selling)
🔴 FII: 12 day selling streak
🟢 DII: 18 day buying streak

Color: green if net positive / red if net negative
Updates every 30 minutes during market hours.

### Component 2 — Shareholding Pattern Chart
Add to Company Deep Dive (Analyse tab Section 10)

Stacked area chart — last 8 quarters:
- Blue area: FII %
- Green area: DII %
- Orange area: Promoter %
- Grey area: Retail %

Below chart: QoQ change table:
Quarter / FII Δ / DII Δ / Promoter Δ / Retail Δ
Color each cell: green if increasing / red if decreasing

### Component 3 — Smart Money Signal Card
Add to every company card on Discover tab:

┌─────────────────────────────┐
│ 🏦 Smart Money Signal       │
│ FII: 📈 +2.3% (3 quarters) │
│ DII: 📈 +1.1% (2 quarters) │
│ 🟢 BOTH ACCUMULATING        │
│ Strongest signal since 2022 │
└─────────────────────────────┘

### Component 4 — Bulk/Block Deal Feed
Add to Sentiment tab Signal Feed section:

Each deal card:
- Date + time
- Stock name + ticker
- Entity name (e.g. "Goldman Sachs")
- BUY/SELL badge
- Quantity + value in ₹ Cr
- % of total volume
- Context: "First FII buy in 6 months"

### Component 5 — Flow Heatmap
Add to Sentiment tab:

Grid of all 20 stocks:
Color by 3-month FII flow:
🟢 Heavy accumulation (FII % up > 2%)
🟡 Mild accumulation (FII % up 0.5-2%)
⚪ Neutral (FII % unchanged)
🟠 Mild distribution (FII % down 0.5-2%)
🔴 Heavy distribution (FII % down > 2%)

Separate heatmap for DII flow.
Toggle: FII / DII / Combined

### Component 6 — Historical Pattern Intelligence
Add to Analyse tab after peer comparison:

"What happened last time smart money 
did this in {company}?"

Card showing:
- Last 3 similar accumulation/distribution episodes
- Price action that followed (% gain/loss)
- Timeframe (how many days)
- Current pattern vs historical match %
- AI prediction based on history

---

## Flow Score Per Stock

Add FII_DII_Flow_Score (0-100) to each stock:

Components:
- FII trend direction (30%)
- DII trend direction (25%)
- Duration of pattern (20%)
- Bulk/block deal activity (15%)
- Historical pattern match (10%)

Interpretation:
- 80-100: 🟢 Strong accumulation — follow the money
- 60-79:  🟡 Mild accumulation — watch closely
- 40-59:  ⚪ Neutral — no clear signal
- 20-39:  🟠 Distribution beginning — caution
- 0-19:   🔴 Heavy distribution — avoid/exit

Add Flow Score to:
- Every company card (displayed alongside FVS, not blended into it)
- Ranked table (separate column)
- Company header in Analyse tab

**Decision:** Flow Score is a standalone parallel metric — it is NOT added as a 7th
component to the FVS Score. FVS remains a 6-component score (weights unchanged).
Rationale: merging would reshuffle all existing company rankings and break historical
comparability. Flow Score provides complementary institutional-sentiment context.

---

## Positional Alert Enhancement

If BOTH conditions true:
- FII accumulating for 2+ quarters AND
- Bulk deal BUY from known FII entity detected

Trigger enhanced positional alert:
🚨 SMART MONEY ACCUMULATION ALERT
"FII has increased stake by 3.2% over
3 quarters. Fresh bulk deal by [entity]
detected today at ₹X. Historical pattern
suggests 18-25% upside over 3-6 months."

---

## Refresh Schedule

FII/DII daily market data: every 30 min
Bulk/block deals: every 15 min during market hours
Shareholding pattern: quarterly (auto-detect new filing)
Flow score: recalculate after each data refresh
Historical pattern analysis: once daily

---

## Definition of Done

- FII/DII strip shows in persistent header
- Flow heatmap renders in Sentiment tab
- Shareholding pattern chart in Analyse tab
- Smart money signal card on company cards
- Bulk/block deal feed in Sentiment tab
- Historical pattern intelligence in Analyse tab
- Flow Score added to all company rankings
- Positional alert triggers on smart money signal
- All existing features remain 100% intact