"""Smoke tests for WIGA core flows (non-UI).
Run: python tests/ui_flow_test.py
"""
import sys
import os
# Ensure project root is on sys.path so `ai`, `data`, etc. import correctly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
from ai import analyzer
from data import collector


def test_score_and_valuation():
    df = pd.DataFrame([
        {
            "ticker": "BEL",
            "name": "Bharat Electronics Ltd",
            "sector": "Defence",
            "mcap": 6_000_000_000.0,
            "roe": 18.0,
            "revcagr": 22.0,
            "debtEq": 0.4,
            "orderBookRev": 1200.0,
            "orderBookTrend": "ACCELERATING",
            "price": 150.0,
        }
    ])
    scored = analyzer.score_universe(df)
    print("score_universe output:")
    print(scored[["ticker", "convictionScore", "growthScore", "riskScore", "visibilityScore"]].to_dict(orient="records"))

    company = scored.iloc[0]
    assumptions = {"revenueGrowth": 0.25, "marginExpansion": 0.02, "peMultiple": 30.0, "years": 3}
    model = analyzer.build_valuation_model(company, assumptions)
    print("valuation model targets:", {k: model[k]["targetPrice"] for k in model})


def test_master_tracker():
    company = {"Company": "BEL", "Guided Rev": 100.0, "Actual Rev": 95.0, "Guided Margin": 10.0, "Actual Margin": 9.0}
    tracker = analyzer.update_master_tracker(company, company)
    print("master tracker:", tracker)


def test_mf_fetch():
    mf = collector.fetch_mf_data()
    print("mf rows:", len(mf))


if __name__ == "__main__":
    print("Running WIGA smoke tests...")
    test_score_and_valuation()
    test_master_tracker()
    test_mf_fetch()
    print("Smoke tests finished.")
