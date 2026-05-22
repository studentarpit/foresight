"""Realistic dummy data for Foresight demo mode. No API key needed."""

import pandas as pd

# ── Scan results (what score_universe() would return) ─────────────────────────
_COMPANIES = [
    {
        "ticker": "MAZDOCK", "name": "Mazagon Dock Shipbuilders", "sector": "Defence",
        "mcap": 8_500_000_000_000, "price": 4250.0, "pe": 38.0,
        "roe": 32.5, "roce": 28.0, "revcagr": 28.4, "profitcagr": 41.2,
        "debtEq": 0.04, "orderBookRev": 5.8, "orderBookTrend": "ACCELERATING",
        "above200dma": True, "above100dma": True, "above50dma": True, "above20dma": True,
        "dma20": 4180.0, "dma50": 4020.0, "dma100": 3850.0, "dma200": 3400.0,
        "relativeStrength": 82.0, "volumeTrend": "ACCUMULATING", "technicalTrend": "STRONG_UPTREND",
        "screenerUrl": "https://www.screener.in/company/MAZDOCK/",
        "concallText": "",
        "growthScore": 9.1, "riskScore": 2.8, "visibilityScore": 9.4,
        "convictionScore": 9.2, "concentrationFlag": True,
        "sectorTailwindScore": 9.5, "govtPolicyTailwind": True,
        "orderInflowAcceleration": True, "fvs": 84.2,
        "oneLineThesis": "India's primary warship builder with a ₹38,000 Cr order book covering 5+ years of revenue.",
        "expectationSignal": "BEAT",
        "aiExplanation": "Q4FY24 revenue +12% vs guided +8%; margin expanded 180 bps above guidance.",
        "Signal": "🟢 Strong Buy",
    },
    {
        "ticker": "BEL", "name": "Bharat Electronics", "sector": "Defence",
        "mcap": 2_200_000_000_000, "price": 300.0, "pe": 42.0,
        "roe": 24.8, "roce": 29.1, "revcagr": 21.6, "profitcagr": 24.3,
        "debtEq": 0.0, "orderBookRev": 3.9, "orderBookTrend": "ACCELERATING",
        "above200dma": True, "above100dma": True, "above50dma": True, "above20dma": False,
        "dma20": 306.0, "dma50": 288.0, "dma100": 272.0, "dma200": 248.0,
        "relativeStrength": 71.0, "volumeTrend": "ACCUMULATING", "technicalTrend": "UPTREND",
        "screenerUrl": "https://www.screener.in/company/BEL/",
        "concallText": "",
        "growthScore": 8.5, "riskScore": 2.6, "visibilityScore": 9.1,
        "convictionScore": 8.8, "concentrationFlag": False,
        "sectorTailwindScore": 9.2, "govtPolicyTailwind": True,
        "orderInflowAcceleration": True, "fvs": 80.1,
        "oneLineThesis": "Defence indigenisation darling with zero debt and accelerating order inflows across radar, EW and C4I.",
        "expectationSignal": "BEAT",
        "aiExplanation": "Order inflow beat FY24 guidance by 11%; EBITDA margin delivered 22.8% vs guided 22%.",
        "Signal": "🟢 Strong Buy",
    },
    {
        "ticker": "TITAGARH", "name": "Titagarh Rail Systems", "sector": "Railways",
        "mcap": 120_000_000_000, "price": 1050.0, "pe": 55.0,
        "roe": 18.4, "roce": 22.1, "revcagr": 32.8, "profitcagr": 48.5,
        "debtEq": 0.3, "orderBookRev": 4.1, "orderBookTrend": "ACCELERATING",
        "above200dma": True, "above100dma": True, "above50dma": True, "above20dma": True,
        "dma20": 1025.0, "dma50": 980.0, "dma100": 920.0, "dma200": 820.0,
        "relativeStrength": 68.0, "volumeTrend": "ACCUMULATING", "technicalTrend": "UPTREND",
        "screenerUrl": "https://www.screener.in/company/TITAGARH/",
        "concallText": "",
        "growthScore": 8.8, "riskScore": 3.5, "visibilityScore": 8.6,
        "convictionScore": 8.4, "concentrationFlag": False,
        "sectorTailwindScore": 8.8, "govtPolicyTailwind": True,
        "orderInflowAcceleration": True, "fvs": 76.8,
        "oneLineThesis": "India's largest private freight wagon and metro coach maker; capex expansion into Vande Bharat components.",
        "expectationSignal": "MIXED",
        "aiExplanation": "Revenue beat guidance but PAT missed due to higher depreciation on new capex.",
        "Signal": "🟡 Watch",
    },
    {
        "ticker": "RVNL", "name": "Rail Vikas Nigam", "sector": "Railways",
        "mcap": 950_000_000_000, "price": 460.0, "pe": 48.0,
        "roe": 16.2, "roce": 18.4, "revcagr": 19.2, "profitcagr": 22.1,
        "debtEq": 0.05, "orderBookRev": 3.2, "orderBookTrend": "STABLE",
        "above200dma": True, "above100dma": True, "above50dma": False, "above20dma": False,
        "dma20": 471.0, "dma50": 468.0, "dma100": 448.0, "dma200": 402.0,
        "relativeStrength": 55.0, "volumeTrend": "NEUTRAL", "technicalTrend": "MIXED",
        "screenerUrl": "https://www.screener.in/company/RVNL/",
        "concallText": "",
        "growthScore": 7.8, "riskScore": 3.2, "visibilityScore": 8.2,
        "convictionScore": 7.6, "concentrationFlag": True,
        "sectorTailwindScore": 8.8, "govtPolicyTailwind": True,
        "orderInflowAcceleration": False, "fvs": 71.4,
        "oneLineThesis": "Government railway EPC arm with assured order pipeline from MoR; upside from international projects.",
        "expectationSignal": "BEAT",
        "aiExplanation": "Q3FY24 revenue in line; order inflow guidance of ₹25,000 Cr likely beat at ₹27,500 Cr.",
        "Signal": "🟡 Watch",
    },
    {
        "ticker": "KECL", "name": "KEC International", "sector": "EPC",
        "mcap": 320_000_000_000, "price": 825.0, "pe": 38.0,
        "roe": 14.6, "roce": 17.2, "revcagr": 17.8, "profitcagr": 19.4,
        "debtEq": 0.65, "orderBookRev": 2.4, "orderBookTrend": "STABLE",
        "above200dma": False, "above100dma": True, "above50dma": True, "above20dma": True,
        "dma20": 810.0, "dma50": 795.0, "dma100": 780.0, "dma200": 860.0,
        "relativeStrength": 44.0, "volumeTrend": "NEUTRAL", "technicalTrend": "MIXED",
        "screenerUrl": "https://www.screener.in/company/KECL/",
        "concallText": "",
        "growthScore": 7.2, "riskScore": 5.1, "visibilityScore": 7.5,
        "convictionScore": 7.0, "concentrationFlag": False,
        "sectorTailwindScore": 7.5, "govtPolicyTailwind": True,
        "orderInflowAcceleration": False, "fvs": 64.3,
        "oneLineThesis": "T&D and infra EPC giant with global diversification; margin recovery in progress after commodity headwind.",
        "expectationSignal": "MIXED",
        "aiExplanation": "Revenue in line but EBITDA margin at 5.9% missed guidance of 6.5% due to legacy orders.",
        "Signal": "🟡 Watch",
    },
    {
        "ticker": "KAYNES", "name": "Kaynes Technology", "sector": "EMS",
        "mcap": 145_000_000_000, "price": 3650.0, "pe": 92.0,
        "roe": 16.9, "roce": 19.8, "revcagr": 38.6, "profitcagr": 52.4,
        "debtEq": 0.4, "orderBookRev": 1.8, "orderBookTrend": "ACCELERATING",
        "above200dma": True, "above100dma": True, "above50dma": True, "above20dma": True,
        "dma20": 3580.0, "dma50": 3420.0, "dma100": 3200.0, "dma200": 2950.0,
        "relativeStrength": 63.0, "volumeTrend": "ACCUMULATING", "technicalTrend": "UPTREND",
        "screenerUrl": "https://www.screener.in/company/KAYNES/",
        "concallText": "",
        "growthScore": 8.9, "riskScore": 5.8, "visibilityScore": 7.1,
        "convictionScore": 7.5, "concentrationFlag": False,
        "sectorTailwindScore": 8.0, "govtPolicyTailwind": True,
        "orderInflowAcceleration": True, "fvs": 61.2,
        "oneLineThesis": "IoT-embedded electronics EMS player expanding into aerospace, defence and industrial automation.",
        "expectationSignal": "BEAT",
        "aiExplanation": "Revenue growth of 41% beat guidance of 35%; gross margins held despite input cost pressure.",
        "Signal": "🟡 Watch",
    },
    {
        "ticker": "WAAREEENER", "name": "Waaree Energies", "sector": "Solar/Wind",
        "mcap": 680_000_000_000, "price": 2100.0, "pe": 45.0,
        "roe": 22.1, "roce": 24.5, "revcagr": 42.3, "profitcagr": 68.2,
        "debtEq": 0.28, "orderBookRev": 2.1, "orderBookTrend": "ACCELERATING",
        "above200dma": False, "above100dma": False, "above50dma": False, "above20dma": True,
        "dma20": 2060.0, "dma50": 2180.0, "dma100": 2320.0, "dma200": 2650.0,
        "relativeStrength": 28.0, "volumeTrend": "DISTRIBUTING", "technicalTrend": "WEAK",
        "screenerUrl": "https://www.screener.in/company/WAAREEENER/",
        "concallText": "",
        "growthScore": 8.6, "riskScore": 5.5, "visibilityScore": 6.8,
        "convictionScore": 7.0, "concentrationFlag": True,
        "sectorTailwindScore": 8.5, "govtPolicyTailwind": True,
        "orderInflowAcceleration": False, "fvs": 55.8,
        "oneLineThesis": "India's largest solar module maker; US export revenue growing rapidly but customer concentration risk elevated.",
        "expectationSignal": "MISS",
        "aiExplanation": "EBITDA margin at 15.8% missed guided 18% due to wafer cost spike; US capacity delayed 6 months.",
        "Signal": "🟠 Neutral",
    },
    {
        "ticker": "TECHNO", "name": "Techno Electric & Engineering", "sector": "Power",
        "mcap": 185_000_000_000, "price": 1580.0, "pe": 36.0,
        "roe": 13.8, "roce": 16.2, "revcagr": 15.6, "profitcagr": 18.3,
        "debtEq": 0.1, "orderBookRev": 1.6, "orderBookTrend": "STABLE",
        "above200dma": True, "above100dma": True, "above50dma": False, "above20dma": False,
        "dma20": 1610.0, "dma50": 1595.0, "dma100": 1540.0, "dma200": 1450.0,
        "relativeStrength": 48.0, "volumeTrend": "NEUTRAL", "technicalTrend": "MIXED",
        "screenerUrl": "https://www.screener.in/company/TECHNO/",
        "concallText": "",
        "growthScore": 6.2, "riskScore": 4.8, "visibilityScore": 6.0,
        "convictionScore": 6.0, "concentrationFlag": False,
        "sectorTailwindScore": 7.0, "govtPolicyTailwind": True,
        "orderInflowAcceleration": False, "fvs": 49.5,
        "oneLineThesis": "Steady T&D and substation EPC operator; power sector capex cycle benefits muted by thin margins.",
        "expectationSignal": "MIXED",
        "aiExplanation": "Revenue in line with guidance; order inflow below expectations due to state discom payment delays.",
        "Signal": "🟠 Neutral",
    },
]

# ── Deep-dive analyses (what analyze_company() would return) ──────────────────
_ANALYSES = {
    "MAZDOCK": {
        "growthScore": 9.1, "riskScore": 2.8, "visibilityScore": 9.4, "convictionScore": 9.2,
        "fvsRefined": 87.5,
        "thesis": (
            "Mazagon Dock is India's premier naval shipbuilder with a ₹38,000 Cr order book "
            "representing 5+ years of revenue. The IN's Project 75I submarine programme and P17B "
            "stealth frigate orders provide decade-long revenue visibility. Zero MSME-style execution "
            "risk given captive government client and advance payments."
        ),
        "bullCase": (
            "Export orders from friendly navies (UAE, Indonesia) add a 3rd revenue leg. P75I "
            "submarine programme fast-tracks, adding ₹45,000 Cr to order book. Re-rating to 50x PE "
            "on Defence PSU premium."
        ),
        "baseCase": (
            "Steady 25-28% revenue CAGR driven by existing order book execution. Margins stable at "
            "10-12%. Stock delivers 18-22% CAGR matching earnings growth."
        ),
        "bearCase": (
            "Government delays on P75I RFP push order inflow below ₹8,000 Cr/year. Margin pressure "
            "from steel and labour cost inflation. Stock de-rates to 28x PE."
        ),
        "risks": [
            "Single customer concentration — 100% revenue from Indian Navy and Coast Guard",
            "Programme delays: P17B or P75I schedule slip could defer revenue recognition",
            "Input cost inflation (steel, marine equipment, imported electronics)",
        ],
        "orderBookInsight": (
            "Order book of ₹38,000 Cr (5.8x FY24 revenue) is at an all-time high. "
            "ACCELERATING inflow driven by P17B frigates and P75 submarine programme milestones."
        ),
        "technicalView": "Price is above all DMAs in a strong uptrend; RSI at 62 — not overbought. Volume accumulation confirms institutional buying.",
        "catalysts": [
            "P75I submarine RFP finalisation (₹40,000-50,000 Cr potential order)",
            "Coast Guard OPV order inflow expected Q2 FY25",
            "Export MoU with UAE Navy for patrol vessels",
        ],
        "concentrationRisk": {
            "flag": True, "severity": "MEDIUM",
            "detail": "Indian Navy accounts for ~90% of revenue; Coast Guard 10%. Diversification via exports underway.",
        },
        "managementConsistencyScore": 9.0,
        "managementConsistencyEvidence": [
            "Delivered on P17A frigate timeline with less than 8% schedule variance",
            "Guidance of ₹10,000 Cr revenue by FY26 — on track after FY24 revenue of ₹8,600 Cr",
        ],
        "capexExpansionDetected": True,
        "capexKeywords": ["dry dock expansion", "new facility", "capacity expansion"],
        "exportOpportunity": True,
        "exportCommentary": "Active MoU discussions with UAE, Indonesia and Vietnam navies for patrol vessel exports.",
        "workingCapitalStress": False,
        "workingCapitalFlags": [],
        "promoterBehaviour": "neutral",
        "institutionalAccumulation": True,
        "institutionalTrend": "FII ownership up 4.2% YoY; domestic MFs added ₹800 Cr in last 2 quarters.",
        "concallSentiment": "positive",
        "concallToneKeywords": ["strong pipeline", "confident", "on track", "record order book"],
        "expectationSignal": "BEAT",
        "expectationGapSummary": "Q4FY24: Revenue +12% vs guided +8%; EBITDA margin 11.8% vs guided 10.5%. Strong beat across all metrics.",
        "guidanceReliabilityAssessment": "Management has beaten or met guidance in 4 of last 4 quarters. High credibility score — guidance upgrades consistently.",
        "aiExplanation": "Q4FY24 revenue +12% vs guided +8%; margin expanded 180 bps above guidance.",
    },
    "BEL": {
        "growthScore": 8.5, "riskScore": 2.6, "visibilityScore": 9.1, "convictionScore": 8.8,
        "fvsRefined": 82.4,
        "thesis": (
            "BEL is the backbone of India's defence electronics ecosystem — radars, EW systems, "
            "communication gear, and C4ISR platforms. Zero debt, 29% ROCE, and an order book of "
            "₹68,000 Cr (3.9x revenue) signal multi-year compounding visibility."
        ),
        "bullCase": (
            "Exports to ASEAN and Middle East accelerate. iDEX and DRDO tech pipeline fuels new "
            "product categories. Order book crosses ₹90,000 Cr by FY27; stock re-rates to 55x PE."
        ),
        "baseCase": (
            "20-22% revenue CAGR through FY27 driven by domestic defence budget growth. "
            "Margin expansion from scale. Stock delivers 18-20% CAGR."
        ),
        "bearCase": (
            "Budget allocation to private defence players under AtmaNirbhar dilutes BEL's market "
            "share. Execution bottlenecks on large radar programmes cause revenue slippage."
        ),
        "risks": [
            "Government budget allocation shifts to private players (L&T, TATA, Adani Defence)",
            "Technology import dependency for critical components (semiconductor chips)",
            "Working capital cycle elongation on large project-based revenues",
        ],
        "orderBookInsight": (
            "Order book of ₹68,000 Cr with ACCELERATING inflow — ₹20,000+ Cr new orders expected "
            "in FY25 from Akash missile system, LRSAM, and soldier modernisation programmes."
        ),
        "technicalView": "Price above 200/100/50 DMA; consolidating below 20 DMA — minor pullback in uptrend. Strong institutional support at ₹270.",
        "catalysts": [
            "LRSAM Batch II order (₹8,000 Cr) expected Q3 FY25",
            "Akash Next Gen missile system production order",
            "Export order for Akash to a friendly Asian nation",
        ],
        "concentrationRisk": {
            "flag": False, "severity": "LOW",
            "detail": "Diversified across Army, Navy, Air Force, Coast Guard and paramilitary; no single client >40%.",
        },
        "managementConsistencyScore": 8.5,
        "managementConsistencyEvidence": [
            "FY24 order inflow of ₹20,000 Cr beat guidance of ₹18,000 Cr by 11%",
            "EBITDA margin guidance of 22-23% consistently delivered for 4 consecutive years",
        ],
        "capexExpansionDetected": True,
        "capexKeywords": ["new facility", "EW complex expansion", "capacity enhancement"],
        "exportOpportunity": True,
        "exportCommentary": "Export pipeline of ₹5,000 Cr under negotiation with ASEAN and Middle East defence forces.",
        "workingCapitalStress": False,
        "workingCapitalFlags": [],
        "promoterBehaviour": "neutral",
        "institutionalAccumulation": True,
        "institutionalTrend": "Consistent DII and FII accumulation; LIC added 1.2% stake in FY24.",
        "concallSentiment": "positive",
        "concallToneKeywords": ["record order inflow", "strong visibility", "confident on margins"],
        "expectationSignal": "BEAT",
        "expectationGapSummary": "FY24 order inflow beat guidance by 11%; EBITDA margin 22.8% vs guided 22%. Consistent outperformer.",
        "guidanceReliabilityAssessment": "4 consecutive years of meeting or beating margin guidance. Among the most reliable management teams in the Defence sector.",
        "aiExplanation": "Order inflow beat FY24 guidance by 11%; EBITDA margin delivered 22.8% vs guided 22%.",
    },
    "WAAREEENER": {
        "growthScore": 8.6, "riskScore": 5.5, "visibilityScore": 6.8, "convictionScore": 7.0,
        "fvsRefined": 54.2,
        "thesis": (
            "Waaree is India's largest solar module manufacturer with 13.3 GW capacity and a "
            "dominant position in both domestic and US export markets. Revenue visibility is "
            "strong near-term but US tariff and customer concentration risks are material."
        ),
        "bullCase": (
            "PLI scheme and BCD on imported panels lock in domestic market. US manufacturing "
            "facility reduces tariff risk. Revenue doubles by FY27 at 20%+ EBITDA margins."
        ),
        "baseCase": (
            "Moderate 30-35% revenue CAGR with margins settling at 16-18% as competition "
            "intensifies. US IRA benefits partly offset by rising wafer costs."
        ),
        "bearCase": (
            "US anti-dumping investigation triggers order cancellations. Domestic rooftop solar "
            "slowdown. Margins compress to 10-12%. Stock corrects 35-40% from peak."
        ),
        "risks": [
            "US tariff escalation — Enforcement of AD/CVD duties could disrupt $600M export book",
            "Customer concentration — Top 3 US customers represent ~55% of export revenue",
            "Chinese wafer price volatility impacts EBITDA margins",
        ],
        "orderBookInsight": (
            "Order book of 2.1x revenue with ACCELERATING domestic utility-scale enquiries. "
            "US backlog strong but exposed to IRA policy uncertainty."
        ),
        "technicalView": "Price below all DMAs in a weak downtrend. Only above 20 DMA — a bear bounce, not a trend reversal. High distribution volume.",
        "catalysts": [
            "US manufacturing facility commencement — removes tariff overhang",
            "Domestic PM Surya Ghar scheme accelerating rooftop demand",
        ],
        "concentrationRisk": {
            "flag": True, "severity": "HIGH",
            "detail": "Single US customer (NextEra Energy) accounts for ~30% of FY24 revenue.",
        },
        "managementConsistencyScore": 6.5,
        "managementConsistencyEvidence": [
            "FY24 margin guidance of 18% missed — delivered 15.8% due to wafer cost spike",
            "US capacity commissioning delayed by 6 months vs original guidance",
        ],
        "capexExpansionDetected": True,
        "capexKeywords": ["US manufacturing facility", "greenfield plant", "capacity expansion to 20GW"],
        "exportOpportunity": True,
        "exportCommentary": "US exports represent 38% of revenue; Middle East utility-scale pipeline building.",
        "workingCapitalStress": True,
        "workingCapitalFlags": [
            "Debtor days up from 42 to 68 (US customers on longer payment terms)",
            "Inventory buildup due to module stocking ahead of US shipment",
        ],
        "promoterBehaviour": "neutral",
        "institutionalAccumulation": False,
        "institutionalTrend": "FII net sellers in last 2 quarters; DII steady. Retail holding rising.",
        "concallSentiment": "cautious",
        "concallToneKeywords": ["monitoring closely", "headwind", "working through", "remain watchful"],
        "expectationSignal": "MISS",
        "expectationGapSummary": "FY24: EBITDA margin 15.8% vs guided 18% (-220 bps miss). US capacity delayed. Revenue in line.",
        "guidanceReliabilityAssessment": "Management missed margin guidance in FY24 and delayed capacity timeline. Credibility under question — discount guidance by 15-20%.",
        "aiExplanation": "EBITDA margin at 15.8% missed guided 18% due to wafer cost spike; US capacity delayed 6 months.",
    },
}

# ── Demo alerts ───────────────────────────────────────────────────────────────
_DEMO_ALERTS = [
    {
        "ticker": "MAZDOCK", "name": "Mazagon Dock Shipbuilders",
        "type": "FVS_STRONG_BUY", "priority": 1,
        "icon": "🟢", "message": "FVS 84 — enters Strong Buy zone (≥80)",
    },
    {
        "ticker": "MAZDOCK", "name": "Mazagon Dock Shipbuilders",
        "type": "EXPECTATION_BEAT", "priority": 1,
        "icon": "✅", "message": "Expectation BEAT — Q4FY24 revenue and margin above guidance",
    },
    {
        "ticker": "BEL", "name": "Bharat Electronics",
        "type": "STRONG_UPTREND", "priority": 2,
        "icon": "🚀", "message": "Price above all 4 DMAs — Strong Uptrend confirmed",
    },
    {
        "ticker": "KAYNES", "name": "Kaynes Technology",
        "type": "ACCUMULATING", "priority": 2,
        "icon": "📊", "message": "Volume trend ACCUMULATING — institutional buying detected",
    },
    {
        "ticker": "WAAREEENER", "name": "Waaree Energies",
        "type": "EXPECTATION_MISS", "priority": 1,
        "icon": "❌", "message": "Expectation MISS — margin guidance missed by 220 bps",
    },
    {
        "ticker": "WAAREEENER", "name": "Waaree Energies",
        "type": "CONCENTRATION_RISK", "priority": 1,
        "icon": "⚠️", "message": "Concentration Risk HIGH — single customer >30% revenue",
    },
    {
        "ticker": "KECL", "name": "KEC International",
        "type": "DMA200_CROSS_DOWN", "priority": 2,
        "icon": "🔻", "message": "Price slipped below 200 DMA — trend caution",
    },
]


_DEMO_ORDERS = {
    "MAZDOCK": [
        {
            "id": "2025-01-15_84231",
            "announcement_date": "2025-01-15",
            "description": "Receipt of order from Indian Navy for construction of two P17B stealth frigates valued at approximately Rs. 12,000 Crore under the Make in India programme.",
            "order_value_cr": 12000.0,
            "customer": "Indian Navy",
            "customer_type": "government",
            "order_type": "domestic",
            "segment": "Naval Shipbuilding",
            "execution_period": "7 years",
            "is_repeat_order": False,
            "significance": "HIGH",
            "confidence": 0.95,
            "pdf_url": "",
        },
        {
            "id": "2024-10-08_61234",
            "announcement_date": "2024-10-08",
            "description": "Letter of Award received from Ministry of Defence for P75 submarine programme. Contract value approximately Rs. 35,000 Crore for six submarines.",
            "order_value_cr": 35000.0,
            "customer": "Ministry of Defence",
            "customer_type": "government",
            "order_type": "domestic",
            "segment": "Submarine Programme",
            "execution_period": "10 years",
            "is_repeat_order": False,
            "significance": "HIGH",
            "confidence": 0.92,
            "pdf_url": "",
        },
        {
            "id": "2024-07-22_39812",
            "announcement_date": "2024-07-22",
            "description": "Intimation of order from Indian Coast Guard for three advanced offshore patrol vessels. Order value Rs. 1,800 Crore.",
            "order_value_cr": 1800.0,
            "customer": "Indian Coast Guard",
            "customer_type": "government",
            "order_type": "domestic",
            "segment": "Patrol Vessels",
            "execution_period": "3 years",
            "is_repeat_order": True,
            "significance": "MEDIUM",
            "confidence": 0.88,
            "pdf_url": "",
        },
    ],
    "BEL": [
        {
            "id": "2025-02-10_73412",
            "announcement_date": "2025-02-10",
            "description": "Receipt of order for Long Range Surface-to-Air Missile (LRSAM) system Batch II from Indian Air Force valued at Rs. 8,200 Crore.",
            "order_value_cr": 8200.0,
            "customer": "Indian Air Force",
            "customer_type": "government",
            "order_type": "domestic",
            "segment": "Missile Systems",
            "execution_period": "4 years",
            "is_repeat_order": True,
            "significance": "HIGH",
            "confidence": 0.93,
            "pdf_url": "",
        },
        {
            "id": "2024-12-05_55678",
            "announcement_date": "2024-12-05",
            "description": "Contract awarded for Akash Next Generation surface-to-air missile system ground equipment valued at approximately Rs. 4,500 Crore.",
            "order_value_cr": 4500.0,
            "customer": "Indian Army",
            "customer_type": "government",
            "order_type": "domestic",
            "segment": "Air Defence Systems",
            "execution_period": "3 years",
            "is_repeat_order": False,
            "significance": "HIGH",
            "confidence": 0.90,
            "pdf_url": "",
        },
    ],
}

_DEMO_REPORTS = {
    "MAZDOCK": {
        "ticker": "MAZDOCK",
        "generatedDate": "2026-05-20",
        "companyOverview": "Mazagon Dock Shipbuilders is India's premier naval shipyard, building warships and submarines for the Indian Navy and Coast Guard since 1774. It holds monopoly status for complex warship construction and benefits from zero private competition in the heavy submarine segment.",
        "businessModel": "Revenue generated through long-term government contracts for warship construction, submarine programmes, and vessel maintenance. Advance payments reduce working capital risk while milestone-based billing provides earnings visibility.",
        "revenueSegments": ["Warship Construction", "Submarine Programmes", "Vessel Repair & Refit"],
        "sectorOpportunity": "India's defence budget is targeted at 3% of GDP by 2030. Navy is acquiring 24 new ships and 6 submarines over the next decade, with Mazagon as the primary domestic builder. Total order opportunity exceeds Rs. 1,00,000 Crore over 10 years.",
        "recentDevelopments": "P75 submarine LOA of Rs. 35,000 Cr received. P17B frigate programme on schedule. Export discussions underway with UAE and Indonesia navies for patrol vessels.",
        "orderWinsAnalysis": "3 major orders tracked: P75 submarine (Rs. 35,000 Cr), P17B frigates (Rs. 12,000 Cr), and Coast Guard OPVs (Rs. 1,800 Cr). Total tracked order value Rs. 48,800 Cr — all domestic, all government, no customer concentration risk beyond IN/MoD.",
        "financialSummary": "Revenue CAGR of 28% over 3 years driven by order book execution. ROE at 32% reflects asset-light government contract model. Zero debt with net cash position.",
        "marginTrend": "expanding",
        "managementQuality": "Consistently delivered on P17A frigates with less than 8% timeline variance. FY26 revenue guidance of Rs. 10,000 Cr is on track. Management has zero track record of guidance downgrades.",
        "growthTriggers": ["P75I submarine RFP expected — potential Rs. 50,000 Cr programme", "Export orders from ASEAN navies", "Dry dock expansion enabling larger vessel capacity"],
        "risks": ["100% revenue concentration in government clients", "P17B/P75 schedule slippage risk", "Steel and imported electronics cost inflation"],
        "bullCase": "P75I RFP awarded and export orders announced. Order book crosses Rs. 55,000 Cr. Re-rating to 50x PE drives 40%+ CAGR over 3 years.",
        "baseCase": "Steady 25-28% revenue growth from existing order execution. Margins stable at 11-12%. Stock delivers 20-22% CAGR matching earnings.",
        "bearCase": "P75I delayed by 2 years. Steel inflation compresses margins to 8%. Stock de-rates to 28x PE, limiting returns to 8-10%.",
        "expectedBaseCagr": 21.0,
        "riskRewardAssessment": "Attractive risk-reward: base case +21% CAGR, limited downside given government contract certainty.",
        "aiView": "Mazagon Dock is one of India's strongest long-term compounder opportunities in the Defence sector. Government captive client, decade-long revenue visibility, and zero debt create a rare combination. The main risk is execution timeline slippage on large programmes, not demand. At current valuations, the stock offers compelling base-case CAGR with limited downside. A core long-term holding for Indian equity investors.",
        "reportSections": ["companyOverview", "orderWins", "financials", "risks", "valuation"],
    },
    "BEL": {
        "ticker": "BEL",
        "generatedDate": "2026-05-20",
        "companyOverview": "Bharat Electronics is India's largest defence electronics company, supplying radars, electronic warfare systems, communication gear, and C4ISR platforms to all three armed forces. It benefits from the AtmaNirbhar Bharat programme which is increasing domestic procurement mandates.",
        "businessModel": "Order-based manufacturing for defence and non-defence electronics. Revenue recognised on project milestones. High proportion of government orders provides earnings predictability. Non-defence revenue from energy meters and medical electronics provides diversification.",
        "revenueSegments": ["Defence Electronics (85%)", "Non-Defence (15%)"],
        "sectorOpportunity": "India's defence electronics market is estimated at Rs. 1,50,000 Cr by FY30. DRDO and iDEX pipeline is adding 15-20 new product categories annually that BEL can manufacture. Export opportunity to ASEAN and Middle East growing.",
        "recentDevelopments": "LRSAM Batch II order of Rs. 8,200 Cr received. Akash Next Gen production contract awarded. Export pipeline of Rs. 5,000 Cr under negotiation.",
        "orderWinsAnalysis": "2 major orders tracked: LRSAM Batch II (Rs. 8,200 Cr) and Akash Next Gen (Rs. 4,500 Cr). Both domestic, both government. Cumulative tracked value Rs. 12,700 Cr. Order book at Rs. 68,000 Cr (3.9x FY24 revenue) remains at all-time high.",
        "financialSummary": "Revenue CAGR of 21.6% over 3 years. ROE at 29.1% and zero debt make this the highest quality balance sheet in Indian Defence. EBITDA margins of 22-23% have been delivered consistently for 4 consecutive years.",
        "marginTrend": "stable",
        "managementQuality": "Best-in-class guidance credibility: FY24 order inflow of Rs. 20,000 Cr beat guidance of Rs. 18,000 Cr by 11%. EBITDA margin guidance of 22-23% delivered for 4 years in a row. No instances of revenue or margin guidance misses in recent history.",
        "growthTriggers": ["Akash export order to friendly ASEAN nation", "Soldier modernisation programme Rs. 12,000 Cr", "iDEX SPRINT pipeline adding new product categories"],
        "risks": ["Private defence players capturing market share under AtmaNirbhar", "Technology import dependency for critical semiconductors", "Working capital elongation on large C4ISR projects"],
        "bullCase": "Exports announced, iDEX pipeline monetised. Order book crosses Rs. 90,000 Cr. Re-rating to 55x PE on Defence premium drives 28%+ CAGR.",
        "baseCase": "20-22% revenue CAGR driven by domestic order execution. Margin stability maintained. Stock delivers 18-20% CAGR.",
        "bearCase": "Private players capture 15% market share. Order inflow drops below Rs. 15,000 Cr. Stock de-rates to 32x PE, limiting CAGR to 10-12%.",
        "expectedBaseCagr": 19.0,
        "riskRewardAssessment": "Excellent risk-reward for long-term investors: consistent guidance delivery, zero debt, strong institutional accumulation.",
        "aiView": "BEL is the anchor of any Indian Defence equity portfolio. Consistent, predictable, and growing — this is an institutional-grade compounder with 4-year track record of delivering exactly what management guides. The stock warrants a core, long-term position for investors seeking quality over volatility.",
        "reportSections": ["companyOverview", "orderWins", "financials", "risks", "valuation"],
    },
}

_DEMO_VALUATIONS = {
    "MAZDOCK": {
        "ticker": "MAZDOCK",
        "savedDate": "2026-05-20",
        "years": 3,
        "currentPrice": 4250.0,
        "bull":  {"revenue": [10800, 13800, 17600], "profit": [1296, 1656, 2112], "targetPrice": 6800.0, "cagr": 16.9},
        "base":  {"revenue": [10000, 12500, 15600], "profit": [1200, 1500, 1872], "targetPrice": 5600.0, "cagr": 9.6},
        "bear":  {"revenue": [8200, 9600, 11200],   "profit": [820, 960, 1120],   "targetPrice": 3360.0, "cagr": -7.5},
        "operatingLeverageDetected": True,
        "marginTrend": "stable",
        "valuationCommentary": "Base case assumes 25% revenue CAGR on existing order book. Bear case discounts for P17B execution delays.",
    },
    "BEL": {
        "ticker": "BEL",
        "savedDate": "2026-05-20",
        "years": 3,
        "currentPrice": 300.0,
        "bull":  {"revenue": [24000, 29000, 35000], "profit": [5280, 6380, 7700], "targetPrice": 460.0, "cagr": 15.3},
        "base":  {"revenue": [21000, 25200, 30200], "profit": [4620, 5544, 6644], "targetPrice": 390.0, "cagr": 9.1},
        "bear":  {"revenue": [18000, 20700, 23800], "profit": [3960, 4554, 5236], "targetPrice": 260.0, "cagr": -4.8},
        "operatingLeverageDetected": False,
        "marginTrend": "stable",
        "valuationCommentary": "Base case on 22% revenue CAGR with margins steady at 22%. Bear case models 15% private-sector share loss.",
    },
}


def load_scan_results() -> pd.DataFrame:
    """Return a DataFrame mimicking score_universe() output."""
    return pd.DataFrame(_COMPANIES)


def load_company_analyses() -> dict:
    """Return pre-built deep-dive analyses keyed by ticker."""
    return dict(_ANALYSES)


def load_demo_alerts() -> list:
    """Return pre-built alert list for demo mode."""
    return list(_DEMO_ALERTS)


def seed_demo_repository() -> None:
    """Write demo orders, reports, and valuation models to the repository files.

    Called once when demo mode starts, safe to call multiple times.
    """
    from data.order_history import save_orders
    from data.report_repository import save_report, save_valuation

    for ticker, orders in _DEMO_ORDERS.items():
        save_orders(ticker, orders)

    for ticker, report in _DEMO_REPORTS.items():
        # save_report adds generatedDate but we want to keep our demo date, so inject directly
        from data.report_repository import _REPORTS_DIR
        import json, os
        os.makedirs(_REPORTS_DIR, exist_ok=True)
        path = os.path.join(_REPORTS_DIR, f"{ticker}.json")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

    for ticker, model in _DEMO_VALUATIONS.items():
        existing = __import__("data.report_repository", fromlist=["load_valuation"]).load_valuation(ticker)
        if not existing:
            price = model.get("currentPrice", 0)
            years = model.get("years", 3)
            save_valuation(ticker, model, years, price)
