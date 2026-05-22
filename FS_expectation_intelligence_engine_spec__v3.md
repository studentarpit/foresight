# WIGA Future Growth Radar
# Expectation Intelligence Engine — Technical Specification

---

# 1. Overview

This document captures the implementation-level specification for the newly identified core capability of the WIGA Future Growth Radar platform:

# "Expectation Intelligence Engine"

This engine is one of the most important differentiators of the platform.

The objective is NOT simply identifying good companies.

The objective is:

> Detecting situations where market expectations and business reality diverge.

This is a critical institutional investing concept.

Many stocks fall despite strong results because expectations were even higher.

Similarly, many stocks rally despite weak absolute growth because expectations were very low.

The system must therefore analyze:

- What the market expected
- What management guided
- What the company actually delivered
- How the market reacted
- Whether the market sentiment trend is changing

This transforms the platform from a normal stock screener into an institutional-grade expectation tracking system.

---

# 2. Core Philosophy

Traditional retail investors think:

```text
Good company = good investment
```

Institutional investors think:

```text
Expectation vs Reality
```

Examples:

| Expected Growth | Actual Growth | Market Reaction |
|---|---|---|
| 40% | 25% | Negative |
| 8% | 15% | Positive |

The system therefore needs to model:

- Expectation buildup
- Delivery quality
- Market disappointment
- Positive surprise
- Trend reversal
- Sentiment transition

---

# 3. New Architecture Components

The platform architecture is now divided into five major engines.

---

## 3.1 Business Quality Engine

Purpose:

```text
Is the company fundamentally strong?
```

Metrics:

- ROE
- ROCE
- Revenue CAGR
- Profit CAGR
- Debt/Equity
- Cash flow quality
- Margin profile

---

## 3.2 Future Visibility Engine

Purpose:

```text
Can future growth continue?
```

Metrics:

- Order book
- Order inflow
- Order book / revenue ratio
- Capex expansion
- Sector tailwinds
- Export opportunities
- Management commentary

---

## 3.3 Expectation Intelligence Engine

Purpose:

```text
Did the company beat or disappoint market expectations?
```

Core concept:

The market does not move only on good or bad numbers.

The market moves based on:

```text
Expected numbers vs Actual numbers
```

This engine tracks:

- Management guidance
- Consensus expectations
- Previous expectations
- Actual delivery
- Result deviation
- Surprise factor
- Guidance credibility

---

## 3.4 Technical Confirmation Engine

Purpose:

```text
Is the market validating the business thesis?
```

Metrics:

- 20 DMA
- 50 DMA
- 100 DMA
- 200 DMA
- Relative strength
- Volume accumulation
- Breakout structure
- Consolidation patterns

---

## 3.5 Alert Engine

Purpose:

```text
Detect trend transition automatically.
```

Examples:

- Price crossing above 200 DMA
- Management guidance deterioration
- Margin deterioration
- Order inflow slowdown
- Positive breakout
- Technical reversal

---

# 4. Expectation Intelligence Engine
# Detailed Specification

---

# 4.1 Problem Statement

Companies are often judged incorrectly if only absolute growth is measured.

Example:

| Company | Revenue Growth |
|---|---|
| Company A | 20% |
| Company B | 20% |

Yet:

- Company A stock crashes
- Company B stock rallies

Reason:

| Company | Expected | Actual |
|---|---|---|
| A | 35% | 20% |
| B | 8% | 20% |

This expectation gap creates major stock movements.

The engine must therefore quantify:

# "Expectation Gap"

---

# 4.2 Core Metrics

The system should track the following:

---

## Revenue Expectation Gap

Formula:

```text
Actual Revenue Growth - Expected Revenue Growth
```

Interpretation:

| Result |
|---|
| Positive = Beat |
| Negative = Miss |

---

## Margin Expectation Gap

Formula:

```text
Actual Margin - Guided Margin
```

Interpretation:

- Margin improvement better than guidance = strong signal
- Margin deterioration below guidance = negative signal

---

## Profit Expectation Gap

Formula:

```text
Actual PAT Growth - Expected PAT Growth
```

---

## Guidance Reliability Score

Tracks:

```text
How often management delivers what it promises.
```

Example:

| Quarter | Guidance | Actual |
|---|---|---|
| Q1 | 25% | 12% |
| Q2 | 30% | 15% |
| Q3 | 20% | 10% |

Result:

```text
Low guidance credibility
```

---

# 4.3 Scoring System

---

## Positive Surprise

Conditions:

- Actual > Expected
- Margins improving
- Guidance upgraded
- Order inflow accelerating

Result:

```text
GREEN signal
```

---

## Negative Surprise

Conditions:

- Actual < Expected
- Margin miss
- Weak commentary
- Guidance downgrade

Result:

```text
RED signal
```

---

# 4.4 Color Classification System

The system should visually classify results.

---

## Green

Meaning:

```text
Company performed better than expectations.
```

---

## Yellow

Meaning:

```text
Mixed or neutral results.
```

---

## Red

Meaning:

```text
Company underperformed expectations.
```

Important:

This does NOT necessarily mean:

```text
Bad company
```

It means:

```text
Market disappointment
```

This distinction is critical.

---

# 5. Technical Confirmation Engine
# Detailed Specification

---

# 5.1 Core Philosophy

A company may be fundamentally strong but still not attractive for entry.

The market must confirm the thesis.

The platform therefore needs:

# Technical Confirmation Layer

---

# 5.2 Why Technical Confirmation Matters

Example discussed:

Vaibhav Global.

Even though:

- Business looked acceptable
- Financials looked reasonable

The stock price continuously declined.

Meaning:

```text
Market still not interested.
```

This is a major insight.

---

# 5.3 Moving Average Intelligence

The system should continuously track:

- 20 DMA
- 50 DMA
- 100 DMA
- 200 DMA

---

## Interpretation

### Price below 200 DMA

Meaning:

```text
Downtrend active.
Weak institutional participation.
```

---

### Price above 200 DMA

Meaning:

```text
Trend improving.
Institutional participation increasing.
Potential accumulation phase.
```

---

# 5.4 Technical Summary Generator

The platform should automatically generate summaries.

Example:

```text
Price below 200 DMA.
Still in weak long-term trend.
No confirmed reversal yet.
```

OR

```text
Price crossed above 200 DMA with volume support.
Possible trend reversal starting.
```

---

# 5.5 Alert Engine

The system should provide real-time or scheduled alerts.

Example triggers:

- Price crossing 200 DMA
- Volume breakout
- Relative strength improvement
- Technical trend reversal
- Order inflow acceleration
- Guidance upgrade
- Margin expansion

---

# 6. Dashboard Implementation

---

# 6.1 Dashboard Overview

The dashboard should display:

- Top future-growth companies
- Top expectation beats
- Top expectation misses
- Technical reversal candidates
- Strong order-book companies
- Institutional accumulation candidates

---

# 6.2 Key Dashboard Columns

| Column |
|---|
| Company |
| Sector |
| Revenue CAGR |
| Profit CAGR |
| ROE |
| ROCE |
| Debt/Equity |
| Order Book / Revenue |
| Guidance Reliability |
| Expectation Gap |
| Technical Trend |
| AI Conviction Score |
| Risk Score |

---

# 6.3 AI Explanation Column

One of the most important differentiators.

Example:

```text
Selected because order inflow accelerated for 3 quarters, margins beat guidance, management upgraded commentary, and stock crossed above 200 DMA.
```

This creates explainable AI investment reasoning.

---

# 7. Data Sources

---

## Free Sources

### Yahoo Finance / yfinance

Purpose:

- Price data
- Historical trends
- Moving averages
- Relative strength

---

### Screener.in

Purpose:

- Financial ratios
- Revenue growth
- Profit growth
- ROE
- ROCE
- Debt metrics

---

### NSE / BSE Filings

Purpose:

- Corporate announcements
- Investor presentations
- Order wins
- Management commentary
- Quarterly results

---

### PDF Extraction

Tools:

- PyMuPDF
- pdfplumber

Used for:

- Investor presentations
- Annual reports
- Concall notes
- Corporate filings

---

# 8. Future AI Enhancements

---

## Concall Sentiment Analysis

AI should analyze:

- confidence
- aggressiveness
- cautiousness
- repeated excuses
- execution tone

---

## Historical Multibagger Matching

Example:

```text
Find companies behaving like HAL in 2018.
```

---

## Institutional Pattern Detection

AI should learn:

- accumulation phases
- rerating cycles
- momentum transitions

---

# 9. Final Strategic Insight

The platform is NOT intended to become:

- Intraday trading software
- Options prediction software
- HFT platform

The actual mission is:

# "AI-Powered Future Business Visibility Intelligence"

The moat will NOT be:

- raw data
- technical indicators
- standard financial ratios

The moat WILL be:

- expectation intelligence
- guidance tracking
- future visibility analysis
- explainable AI reasoning
- market psychology modeling
- technical confirmation
- signal combination

This creates an institutional-style AI investment discovery platform capable of identifying future compounders before the broader market fully recognizes them.

