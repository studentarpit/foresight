"""All Claude prompt templates for WIGA AI analysis. All return strict JSON.

Enhanced to v2.0 spec: 20-signal architecture with FVS composite scoring.
"""

# Batch conviction scoring — enhanced with S07 sector tailwind, S11 policy,
# S02 order inflow acceleration, S18 FVS estimate.
# {companies_json}: JSON array with ticker, sector, roe, revcagr, debtEq, mcap,
#   orderBookRev, orderBookTrend, above200dma
SCAN_PROMPT = """\
You are an expert Indian equity analyst specialising in identifying long-term compounders \
in capital goods, defence, railways, EMS, power, and renewable energy sectors.

Score each company below for long-term investment potential.
Companies: {companies_json}

Return a JSON array with one object per company. Use your knowledge of each sector's \
government policy backdrop, order book dynamics, and growth tailwinds.

[
  {{
    "ticker": "BEL",
    "growthScore": 8.2,
    "riskScore": 3.1,
    "visibilityScore": 8.7,
    "convictionScore": 8.4,
    "concentrationFlag": false,
    "sectorTailwindScore": 8.5,
    "govtPolicyTailwind": true,
    "orderInflowAcceleration": true,
    "fvs": 76.4,
    "oneLineThesis": "Strong defence indigenisation policy drives multi-year order visibility."
  }}
]

Scoring guide (0-10 unless noted):
- growthScore: Revenue and earnings growth momentum over 3-5 years
- riskScore: Execution, competition, debt, and regulatory risk (LOWER = less risky)
- visibilityScore: Revenue visibility from order book, contracts, sector tailwinds
- convictionScore: Overall long-term investment conviction
- concentrationFlag: true if >60%% revenue from a single customer/ministry/scheme
- sectorTailwindScore: 0-10 strength of government policy and macro tailwinds for this sector
- govtPolicyTailwind: true if sector benefits from active PLI/Make-in-India/defence/railway policy
- orderInflowAcceleration: true if order inflow is visibly accelerating (QoQ or YoY)
- fvs: 0-100 Future Visibility Score — weighted composite of all visible signals. \
  80-100 Strong Buy, 60-79 Watch, 40-59 Neutral, <40 Avoid
- oneLineThesis: one concise sentence capturing the core investment case
- expectationSignal: "BEAT" if the company has recently delivered above market expectations, \
  "MISS" if it has disappointed, "MIXED" if results are uneven, "UNKNOWN" if insufficient data
- aiExplanation: one sentence starting with "Selected because..." explaining the 2-3 strongest \
  reasons this company ranks here (order inflow trend, margin trajectory, DMA position, policy, etc.)

Return ONLY valid JSON. No markdown. No explanation."""


# Full deep-dive analysis — enhanced to v2.0 with S03-S05, S08-S10, S12, S14-S16, S19.
# {company_json}: dict with all FinancialData fields
DEEP_ANALYSIS_PROMPT = """\
You are an institutional equity research analyst producing a deep-dive company note for \
an Indian listed company.

Company data: {company_json}

Analyse this company across all available signals. The company data includes a \
`concallText` field — if non-empty, it contains excerpts from the most recent \
earnings call transcript; use it to assess management tone, guidance credibility, \
and order book commentary. Where data is absent, use your knowledge of Indian \
capital markets, sector dynamics, and company history.

Pay special attention to:
1. Customer and scheme concentration risk (single-customer/ministry >60%% is a red flag)
2. Management guidance vs delivery track record
3. Capex expansion signals suggesting capacity-driven growth phase
4. Working capital and balance sheet stress indicators
5. Promoter and institutional behaviour signals

Return a single JSON object with EXACTLY these fields:
{{
  "growthScore": <float 0-10>,
  "riskScore": <float 0-10, higher = riskier>,
  "visibilityScore": <float 0-10>,
  "convictionScore": <float 0-10>,
  "thesis": "<2-3 sentence core investment thesis>",
  "bullCase": "<2-3 sentence bull case>",
  "baseCase": "<2-3 sentence base case>",
  "bearCase": "<2-3 sentence bear case>",
  "risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "orderBookInsight": "<1 sentence on order book trend and revenue visibility>",
  "technicalView": "<1 sentence on price vs 200 DMA and momentum>",
  "catalysts": ["<catalyst 1>", "<catalyst 2>"],
  "concentrationRisk": {{
    "flag": <true if >60%% revenue from single customer/ministry/scheme>,
    "detail": "<name the specific customer/scheme or 'Diversified'>",
    "severity": "HIGH" | "MEDIUM" | "LOW"
  }},
  "managementConsistencyScore": <float 0-10, 10 = always delivers on guidance>,
  "managementConsistencyEvidence": ["<evidence 1>", "<evidence 2>"],
  "capexExpansionDetected": <true if company is in active capacity expansion phase>,
  "capexKeywords": ["<keyword found, e.g. 'new facility', 'capacity expansion'>"],
  "exportOpportunity": <true if meaningful export revenue or active global expansion>,
  "exportCommentary": "<1 sentence on export opportunity or lack thereof>",
  "workingCapitalStress": <true if receivables/inventory are stretching dangerously>,
  "workingCapitalFlags": ["<flag e.g. 'receivables days increasing', 'inventory buildup'>"],
  "promoterBehaviour": "buying" | "neutral" | "selling" | "pledging",
  "institutionalAccumulation": <true if FII/DII/MF are net buyers>,
  "institutionalTrend": "<1 sentence on FII/DII/MF activity trend>",
  "concallSentiment": "positive" | "neutral" | "cautious" | "defensive",
  "concallToneKeywords": ["<tone keyword 1>", "<tone keyword 2>"],
  "expectationSignal": "BEAT" | "MISS" | "MIXED" | "UNKNOWN",
  "expectationGapSummary": "<1-2 sentences: did the company beat or miss market expectations recently, and by how much?>",
  "guidanceReliabilityAssessment": "<1 sentence on management's track record of delivering on guidance>",
  "aiExplanation": "<Selected because... — 1 sentence listing the 2-3 strongest conviction drivers>"
}}

Return ONLY valid JSON. No markdown. No explanation."""


# 3-scenario DCF/PE valuation model — enhanced with S06 operating leverage, S13 margin trend.
# {company_json}: dict with ticker, name, price, pe, revcagr, mcap
# {assumptions_json}: dict with revenueGrowth, marginExpansion, peMultiple, years
VALUATION_PROMPT = """\
You are a quantitative equity analyst building a 3-scenario valuation model for an Indian company.

Company data: {company_json}
Base assumptions: {assumptions_json}

Create 3 scenarios:
- bull: multiply revenueGrowth and marginExpansion by 1.3
- base: use assumptions as provided
- bear: multiply revenueGrowth and marginExpansion by 0.7

For each scenario project year-by-year (years 1 to N as specified):
- revenue[]: projected revenue in Cr
- profit[]: projected profit in Cr
- targetPrice: float (estimated fair value per share)
- cagr: float (expected stock CAGR %%)

Also include top-level valuation intelligence fields:
- operatingLeverageDetected: true if margin improvement accelerates as revenue scales
- marginTrend: "expanding" | "stable" | "contracting"
- valuationCommentary: 2 sentence rationale for the base case target

Return a single JSON object:
{{
  "bull":  {{"revenue": [], "profit": [], "targetPrice": 0.0, "cagr": 0.0}},
  "base":  {{"revenue": [], "profit": [], "targetPrice": 0.0, "cagr": 0.0}},
  "bear":  {{"revenue": [], "profit": [], "targetPrice": 0.0, "cagr": 0.0}},
  "operatingLeverageDetected": false,
  "marginTrend": "stable",
  "valuationCommentary": "<2 sentence commentary>"
}}

Return ONLY valid JSON. No markdown. No explanation."""


# Thesis integrity tracker — compare guidance vs actuals via Claude.
# {company_json}: dict with name, ticker
# {quarterly_json}: dict with guidedRevenue, actualRevenue, guidedMargin,
#   actualMargin, orderBookGuidance, actualOrderBook
MASTER_TRACKER_PROMPT = """\
You are an investment monitoring analyst. Evaluate management's delivery vs guidance for \
this Indian company:

Company: {company_json}
Quarterly data: {quarterly_json}

Assess whether the investment thesis is still intact based on:
1. Revenue delivery vs guidance
2. Margin delivery vs guidance
3. Order book vs guidance

Return a single JSON object:
{{
  "thesisStatus": "ON_TRACK" | "WATCH" | "BROKEN",
  "thesisColor": "green" | "yellow" | "red",
  "guidanceAccuracy": <float 0-100, percentage of guided metrics hit>,
  "commentary": "<2-3 sentence assessment of thesis health>",
  "action": "HOLD" | "REVIEW" | "EXIT"
}}

Return ONLY valid JSON. No markdown. No explanation."""


# Mutual fund consistency and risk scoring.
# {fund_json}: dict with name, category, return1yr, return3yr, return5yr, return10yr,
#   maxDrawdown, consistencyScore
MF_ANALYSIS_PROMPT = """\
You are a mutual fund analyst specialising in Indian equity funds.

Evaluate this fund for long-term consistency and risk-adjusted returns:
{fund_json}

Return a single JSON object:
{{
  "consistencyScore": <float 0-10>,
  "drawdownRisk": <float 0-10, higher = riskier drawdown profile>,
  "recommendation": "STRONG" | "MODERATE" | "AVOID",
  "reasoning": "<2-3 sentence explanation of the recommendation>"
}}

Return ONLY valid JSON. No markdown. No explanation."""


# Order announcement extraction — Section 6 of research spec.
# {ticker}: NSE symbol
# {company_name}: full company name
# {announcement_text}: raw announcement subject/description text
ORDER_EXTRACTION_PROMPT = """\
You are an order-announcement analyst for Indian listed companies.

Extract structured order information from this corporate announcement:

Ticker: {ticker}
Company: {company_name}
Announcement: {announcement_text}

Return a single JSON object:
{{
  "order_value_cr": <float in Crores, or null if not mentioned>,
  "customer": "<customer name, or 'Undisclosed' if not named>",
  "customer_type": "government" | "psu" | "private" | "export" | "unknown",
  "order_type": "domestic" | "export" | "unknown",
  "segment": "<business segment e.g. 'Defence Electronics', 'Railway Wagons', or null>",
  "execution_period": "<e.g. '18 months', '2 years', or null>",
  "is_repeat_order": <true/false>,
  "description": "<2 sentence summary of the order>",
  "significance": "HIGH" | "MEDIUM" | "LOW",
  "confidence": <0.0 to 1.0 extraction confidence>
}}

Return ONLY valid JSON. No markdown. No explanation."""


# Full company research report — Section 9 of research spec.
# {company_json}: full company data dict
# {order_summary}: text summary of recent orders
# {concall_text}: concall transcript excerpt
FULL_REPORT_PROMPT = """\
You are an institutional equity research analyst generating a pre-built company research \
report for the WIGA Future Growth Radar platform.

Company data: {company_json}
Recent order wins: {order_summary}
Management commentary (concall): {concall_text}

Generate a comprehensive research report covering all major aspects of this company. \
Use your knowledge of Indian capital markets, sector dynamics, and company history to \
supplement the provided data.

Return a single JSON object:
{{
  "companyOverview": "<2-3 sentences on what the company does>",
  "businessModel": "<2-3 sentences on how it makes money>",
  "revenueSegments": ["<segment 1>", "<segment 2>"],
  "sectorOpportunity": "<2-3 sentences on the sector TAM and growth drivers>",
  "recentDevelopments": "<2-3 sentences on latest news, orders, and events>",
  "orderWinsAnalysis": "<2-3 sentences analysing recent order wins and pipeline>",
  "financialSummary": "<2-3 sentences on revenue growth, margins, and profit trajectory>",
  "marginTrend": "expanding" | "stable" | "contracting",
  "managementQuality": "<2-3 sentences on management track record and credibility>",
  "growthTriggers": ["<trigger 1>", "<trigger 2>", "<trigger 3>"],
  "risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "bullCase": "<2-3 sentences>",
  "baseCase": "<2-3 sentences>",
  "bearCase": "<2-3 sentences>",
  "expectedBaseCagr": <float %, estimated 3-year base-case stock CAGR, or null>,
  "riskRewardAssessment": "<1 sentence on whether risk-reward is attractive>",
  "aiView": "<3-4 sentence final analyst view and overall recommendation>",
  "reportSections": ["companyOverview", "orderWins", "financials", "risks", "valuation"]
}}

Return ONLY valid JSON. No markdown. No explanation."""
