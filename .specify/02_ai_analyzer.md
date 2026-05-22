# Spec 02 — AI Analyzer (Upgraded)

## Purpose
Generate AI conviction scores, full investment analysis,
valuation models, and thesis tracking using Claude API.

## Input
Filtered DataFrame from data/collector.py

## Output
Same DataFrame enriched with AI columns plus separate
valuation model and master tracker outputs

## Four AI Functions to Build

### Function 1 — score_universe(df)
Batch score all filtered companies.
Prompt instructs Claude to return JSON array:
[{"ticker": "BEL", "growthScore": 8.2, "riskScore": 3.1,
  "visibilityScore": 8.7, "convictionScore": 8.4}]
Add 0.5s delay between calls. Max 30 companies per scan.

### Function 2 — analyze_company(company)
Full deep dive for one selected company.
Return JSON:
{
  "growthScore": float,
  "riskScore": float,
  "visibilityScore": float,
  "convictionScore": float,
  "thesis": string,
  "bullCase": string,
  "baseCase": string,
  "bearCase": string,
  "risks": [string, string, string],
  "orderBookInsight": string,
  "technicalView": string,
  "catalysts": [string, string]
}

### Function 3 — build_valuation_model(company, assumptions)
This replaces manual Excel modeling.
Inputs:
- company: dict with financial data
- assumptions: dict with user inputs:
  {
    "revenueGrowth": float,   (e.g. 0.25 for 25%)
    "marginExpansion": float, (e.g. 0.02 for 2%)
    "peMultiple": float,      (e.g. 30.0)
    "years": int              (e.g. 3)
  }
Claude generates 3 scenarios automatically:
- Bull: assumptions * 1.3
- Base: assumptions as entered
- Bear: assumptions * 0.7
Return JSON:
{
  "bull": {"revenue": [], "profit": [], "targetPrice": float, "cagr": float},
  "base": {"revenue": [], "profit": [], "targetPrice": float, "cagr": float},
  "bear": {"revenue": [], "profit": [], "targetPrice": float, "cagr": float}
}

### Function 4 — update_master_tracker(company, quarterlyData)
This tracks thesis integrity over time.
Compare management guidance vs actual delivery:
- guidedRevenue vs actualRevenue
- guidedMargin vs actualMargin
- orderBookGuidance vs actualOrderBook
Claude scores thesis health:
{
  "thesisStatus": "ON_TRACK" / "WATCH" / "BROKEN",
  "thesisColor": "green" / "yellow" / "red",
  "guidanceAccuracy": float,
  "commentary": string,
  "action": "HOLD" / "REVIEW" / "EXIT"
}

## Prompts File (ai/prompts.py)
Store all prompt templates here as constants:
- SCAN_PROMPT
- DEEP_ANALYSIS_PROMPT
- VALUATION_PROMPT
- MASTER_TRACKER_PROMPT

All prompts must end with:
"Return ONLY valid JSON. No markdown. No explanation."

## MF Analysis Function — analyze_mf(fund)
Score mutual funds for long term consistency:
{
  "consistencyScore": float,
  "drawdownRisk": float,
  "recommendation": "STRONG" / "MODERATE" / "AVOID",
  "reasoning": string
}