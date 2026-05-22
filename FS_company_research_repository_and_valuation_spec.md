# WIGA Future Growth Radar
# Company Research Repository, Order Book Intelligence & AI Valuation Engine
# Detailed Requirement Specification

---

# 1. Purpose of This Specification

This document defines the detailed implementation requirements for a major module inside the WIGA Future Growth Radar platform.

The purpose of this module is to move the product from:

```text
User enters one company → AI generates one report
```

to:

```text
AI scans all listed companies → builds pre-generated research reports → creates valuation models → ranks companies by expected future CAGR and risk-reward
```

This is the actual scalable product vision.

The goal is not to manually analyze one company at a time.

The goal is to build a continuously updated AI research repository for Indian listed companies.

---

# 2. Product Objective

The system should automatically research, analyze, value, and rank Indian listed companies using AI.

The platform should:

- Scan NSE/BSE-listed companies.
- Read BSE/NSE corporate announcements.
- Detect new order wins.
- Extract order value and execution timeline.
- Extract quarterly unexecuted order book from investor presentations.
- Read concalls, management commentary, annual reports, and investor presentations.
- Generate detailed company research reports.
- Generate bull/base/bear valuation models.
- Calculate expected 2–3 year and 3–5 year CAGR.
- Create a master comparison dashboard.
- Surface only companies with attractive expected CAGR and acceptable risk.

The user should not need to ask:

```text
Analyze HAL
Analyze BEL
Analyze JNK India
```

Instead, the system should already maintain reports for all companies in the research universe.

---

# 3. Core Investment Philosophy

The module is based on the following idea:

```text
Stocks move when future business reality improves faster than market expectations.
```

Therefore, the AI must identify:

- Companies receiving large new orders.
- Companies with rising unexecuted order books.
- Companies where order inflow is accelerating.
- Companies where revenue conversion may happen in future quarters.
- Companies with improving margins.
- Companies with strong sector tailwinds.
- Companies where valuation still offers attractive future CAGR.

The product is not only a screener.

It is a research automation and valuation intelligence system.

---

# 4. Major System Components

The module contains the following major components:

1. Market Universe Builder
2. BSE/NSE Order Notification Parser
3. Order Book Indexing Engine
4. Quarterly Unexecuted Order Book Extractor
5. Company Research Report Generator
6. AI Valuation Modeling Engine
7. Expected CAGR Calculator
8. Risk-Reward Engine
9. Pre-generated Company Research Repository
10. Master Comparison Dashboard
11. Technical Confirmation & Alert Engine

---

# 5. Market Universe Builder

## 5.1 Objective

Create and maintain the list of Indian companies that the platform should track.

## 5.2 Input Sources

- NSE listed companies
- BSE listed companies
- Screener-style company master data
- Sector classification data
- Market capitalization data

## 5.3 Data Fields

Each company record should include:

- Company name
- NSE symbol
- BSE code
- ISIN
- Sector
- Industry
- Market cap
- Small/mid/large cap classification
- Listing status
- Website
- Investor relations URL if available

## 5.4 Initial Universe Strategy

The platform does not need to track all companies on day one.

Initial universe can start with:

- Companies with market cap above a configurable threshold
- Companies from order-driven sectors
- Companies with recent corporate announcements
- Companies with available investor presentations

Priority sectors:

- Defence
- Railways
- Infrastructure
- EPC
- Power
- Capital goods
- EMS
- Manufacturing
- Oil & gas services
- Renewable energy

---

# 6. BSE/NSE Order Notification Parser

## 6.1 Objective

Detect companies receiving new orders from exchange announcements.

Companies are required to notify exchanges when they receive material orders or contracts.

The AI should process these announcements and extract structured order information.

## 6.2 Input Documents

- BSE corporate announcements
- NSE corporate filings
- PDFs attached with announcements
- Company press releases

## 6.3 Order Detection Keywords

The parser should search for phrases such as:

- order received
- work order
- letter of award
- letter of intent
- contract awarded
- purchase order
- EPC contract
- project awarded
- supply order
- agreement signed
- repeat order
- export order
- domestic order
- turnkey contract

## 6.4 Extracted Fields

For every order announcement, extract:

- Company name
- Announcement date
- Exchange source
- Order value
- Currency
- Customer name
- Domestic or international order
- Segment/business vertical
- Project description
- Execution timeline
- Expected completion date if available
- Whether order is new/repeat/extension
- PDF/document URL
- Confidence score of extraction

## 6.5 Example Output

```json
{
  "company": "Supreme Power Equipment",
  "announcement_date": "2026-05-20",
  "order_value_cr": 50,
  "customer": "Unknown",
  "execution_period": "12 months",
  "order_type": "domestic",
  "source": "BSE Announcement",
  "confidence": 0.86
}
```

---

# 7. Order Book Indexing Engine

## 7.1 Objective

Build a company-level searchable index of all new order announcements.

The user should be able to see:

- All orders received by a company
- Total orders received in a quarter
- Total orders received in a year
- Sector-wise order momentum
- Order inflow trend

## 7.2 Company-Level Order Summary

For each company, calculate:

- Orders received this quarter
- Orders received last quarter
- Orders received this financial year
- Orders received last financial year
- Average order size
- Largest order received
- Domestic vs export order split
- Customer concentration in orders

## 7.3 Limitation to Remember

Order received does not necessarily mean revenue has been recognized.

This is a critical limitation.

Therefore, order inflow must be connected later with:

- revenue growth
- execution timeline
- unexecuted order book
- quarterly order book snapshots

---

# 8. Quarterly Unexecuted Order Book Extractor

## 8.1 Objective

Extract the pending/unexecuted order book disclosed by companies in investor presentations or results documents.

This is more powerful than only tracking order announcements.

New order announcement tells:

```text
Company received an order
```

Unexecuted order book tells:

```text
How much future business is still pending for execution
```

## 8.2 Input Documents

- Quarterly investor presentations
- Earnings presentations
- Result PDFs
- Annual reports
- Concall transcripts if available

## 8.3 Extraction Keywords

AI should detect:

- unexecuted order book
- pending order book
- order backlog
- outstanding order book
- order book position
- executable order book
- order book as of quarter end
- carried forward order book

## 8.4 Extracted Fields

- Company
- Quarter
- Financial year
- Order book value
- Currency
- Segment-wise order book
- Domestic/export split
- Execution period
- Source document
- Page number if available
- Confidence score

## 8.5 Timeline Creation

For every company, build time series:

```text
Q1 FY25 → ₹1,000 Cr
Q2 FY25 → ₹1,250 Cr
Q3 FY25 → ₹1,700 Cr
Q4 FY25 → ₹2,100 Cr
```

## 8.6 Derived Metrics

Calculate:

- Quarter-on-quarter order book growth
- Year-on-year order book growth
- Order book / annual revenue ratio
- Order book trend direction
- Order book acceleration
- Order book decline risk

## 8.7 Interpretation

Increasing unexecuted order book means:

- future revenue visibility is improving
- execution pipeline is growing
- company has business visibility

Declining unexecuted order book may mean:

- execution is happening faster than new orders
- new order inflow is weak
- future revenue visibility is reducing

AI must interpret this carefully and not blindly treat every decline as negative.

---

# 9. Company Research Report Generator

## 9.1 Objective

Generate a full AI research report for each company in the universe.

The report should be pre-generated and stored in the repository.

The user should not have to wait for on-demand research unless the report is outdated.

## 9.2 Inputs

The AI report generator should use:

- latest annual report
- quarterly results
- investor presentations
- concall transcripts
- BSE/NSE announcements
- order book data
- price trend
- sector context
- management commentary
- financial history

## 9.3 Report Sections

Each company report should contain:

1. Company overview
2. Business model
3. Revenue segments
4. Sector opportunity
5. Recent developments
6. Order inflow analysis
7. Unexecuted order book timeline
8. Financial performance
9. Margin trend
10. Management commentary
11. Growth triggers
12. Key risks
13. Bull case
14. Base case
15. Bear case
16. Valuation model
17. Expected CAGR
18. Technical confirmation
19. Final AI view

## 9.4 Report Freshness

Each report should store:

- generated date
- data cutoff date
- latest result included
- latest presentation included
- latest announcement included
- freshness status

Freshness labels:

- Fresh
- Needs refresh
- Stale

---

# 10. AI Valuation Modeling Engine

## 10.1 Objective

Automate the valuation modeling process that was earlier done manually in Excel.

The user should not need to manually collect:

- historical revenue
- margins
- profit numbers
- number of shares
- PE assumptions
- growth assumptions

The AI should create a structured valuation model quickly.

## 10.2 Required Inputs

For each company:

- historical revenue
- revenue CAGR
- EBITDA margin
- PAT margin
- net profit
- EPS
- number of shares
- current market price
- current market cap
- current PE
- industry PE range
- expected revenue growth
- expected margin range
- expected valuation multiple

## 10.3 Scenario Modeling

The engine should create three scenarios:

### Bear Case

Conservative assumptions:

- lower revenue growth
- margin pressure
- lower PE multiple
- delayed execution

### Base Case

Reasonable assumptions:

- expected revenue growth
- stable margins
- fair valuation multiple
- normal execution

### Bull Case

Optimistic assumptions:

- strong execution
- margin expansion
- higher order conversion
- valuation rerating

## 10.4 Valuation Outputs

For every scenario, calculate:

- projected revenue
- projected profit
- projected EPS
- assumed PE multiple
- target market cap
- target price
- expected upside/downside
- expected CAGR

## 10.5 Example Output

| Scenario | Expected CAGR | Risk View |
|---|---:|---|
| Bear | -5% to 5% | Downside risk high |
| Base | 18% to 22% | Acceptable |
| Bull | 30%+ | Strong upside |

---

# 11. Expected CAGR Calculator

## 11.1 Objective

Calculate expected future return based on valuation model.

## 11.2 CAGR Formula

```text
Expected CAGR = (Target Price / Current Price) ^ (1 / Years) - 1
```

## 11.3 Time Horizons

Support:

- 1 year
- 2 years
- 3 years
- 5 years

## 11.4 Screening Rule

The system should allow filters such as:

```text
Show companies where expected CAGR > 25%
```

or

```text
Show companies where base-case CAGR > 20% and downside risk < 15%
```

---

# 12. Risk-Reward Engine

## 12.1 Objective

Estimate whether the possible reward justifies the risk.

## 12.2 Inputs

- Bear case downside
- Base case upside
- Bull case upside
- business risk
- valuation risk
- execution risk
- technical trend

## 12.3 Risk-Reward Interpretation

Example:

```text
Bear Case: -20%
Base Case: +45%
Bull Case: +110%
```

This is attractive if business quality is acceptable.

But:

```text
Bear Case: -45%
Base Case: +20%
Bull Case: +50%
```

This may be unattractive due to poor risk-reward.

---

# 13. Pre-generated Company Research Repository

## 13.1 Objective

Maintain a repository of AI-generated research reports and valuation models for all tracked companies.

## 13.2 Why This Is Needed

If the system generates reports only on demand, then:

- discovery becomes slow
- comparison becomes difficult
- user must manually ask for each company

Instead, pre-generation allows:

- instant comparison
- market-wide ranking
- dashboard search
- CAGR filtering
- risk filtering
- watchlist creation

## 13.3 Repository Contents

For each company:

- structured data file
- AI research report
- valuation model
- order book timeline
- latest signal summary
- risk score
- expected CAGR score
- technical status
- freshness metadata

## 13.4 Suggested Storage

For local prototype:

```text
/data/company_reports/{symbol}.md
/data/company_models/{symbol}.json
/data/order_books/{symbol}.csv
/data/master_company_scores.csv
```

For later product:

- PostgreSQL
- Object storage
- Vector database
- Search index

---

# 14. Master Comparison Dashboard

## 14.1 Objective

Create one master view across all analyzed companies.

The dashboard should answer:

```text
Which companies currently offer the best future CAGR with acceptable risk?
```

## 14.2 Required Columns

- Rank
- Company
- Sector
- Market cap
- Order book / revenue
- Order book growth
- Revenue CAGR
- Profit CAGR
- Margin trend
- Expected base CAGR
- Expected bull CAGR
- Bear case downside
- Risk-reward score
- Technical trend
- AI conviction score
- Report freshness

## 14.3 Filters

Required filters:

- Sector
- Market cap category
- Expected CAGR
- Bear case downside
- Order book growth
- Technical trend
- Report freshness
- Risk score
- AI conviction score

## 14.4 Example Filters

```text
Show only companies where:
- Base case CAGR > 25%
- Bear case downside < 20%
- Order book growth positive
- Price above 200 DMA
```

---

# 15. Technical Confirmation & Alert Engine

## 15.1 Objective

Confirm whether market price action supports the business thesis.

## 15.2 Indicators

- 20 DMA
- 50 DMA
- 100 DMA
- 200 DMA
- volume breakout
- relative strength
- trend reversal

## 15.3 Alerts

Generate alerts when:

- price crosses above 200 DMA
- price falls below 200 DMA
- order book jumps sharply
- new large order is announced
- base-case CAGR improves
- risk-reward becomes attractive
- expectation miss occurs

---

# 16. Local Prototype Implementation

## 16.1 Recommended Stack

- Python
- Streamlit
- Pandas
- yfinance
- pdfplumber
- PyMuPDF
- SQLite or CSV storage
- Markdown reports
- JSON valuation models

## 16.2 Local Folder Structure

```text
wiga-future-growth-radar/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── universe/
│   ├── announcements/
│   ├── pdfs/
│   ├── order_books/
│   ├── company_reports/
│   ├── valuation_models/
│   └── master_scores/
│
├── src/
│   ├── universe_builder.py
│   ├── announcement_parser.py
│   ├── order_extractor.py
│   ├── order_book_timeline.py
│   ├── report_generator.py
│   ├── valuation_engine.py
│   ├── cagr_calculator.py
│   ├── risk_reward_engine.py
│   ├── technical_engine.py
│   └── dashboard.py
│
└── prompts/
    ├── company_research_prompt.md
    ├── order_extraction_prompt.md
    ├── valuation_prompt.md
    └── risk_reward_prompt.md
```

---

# 17. MVP Build Scope

## 17.1 Day-1 / Early Prototype

Do not attempt all 3000 companies initially.

Start with:

- 25 to 50 companies
- 3 to 5 sectors
- manually downloaded PDFs
- semi-automated order extraction
- local valuation models
- Streamlit dashboard

## 17.2 MVP Features

- Upload investor presentation
- Extract order book values
- Add company financials
- Generate valuation scenarios
- Calculate expected CAGR
- Show master comparison table
- Filter companies by expected CAGR
- Generate AI summary

## 17.3 Later Automation

- Auto-download filings
- Auto-refresh company reports
- Full universe scanning
- Automated valuation refresh
- Real-time alerts
- Cloud deployment

---

# 18. Acceptance Criteria

The module is successful when:

- The system can track multiple companies.
- It can extract order-related information from PDFs.
- It can store company-level order histories.
- It can generate valuation scenarios.
- It can calculate expected CAGR.
- It can compare companies in one master dashboard.
- It can identify companies with expected CAGR above a threshold.
- It can explain why a company is ranked highly.

---

# 19. Final Strategic Summary

This module transforms WIGA from a one-stock analysis tool into a market-wide AI research platform.

The core value is:

```text
AI builds the research repository before the user asks.
```

This enables:

- faster discovery
- better comparison
- automated valuation
- systematic screening
- reduced manual effort
- scalable investment intelligence

The long-term product should become:

# AI Research Analyst + AI Valuation Analyst + AI Screener + AI Dashboard

all working together for Indian equity discovery.

