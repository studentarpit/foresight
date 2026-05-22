"""
token_logger.py  –  Foresight
Tracks Anthropic API token usage and cost per call, per stock, per session.
Drop this file into C:\Foresight\ and import it in ai/analyzer.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ── Pricing (USD per million tokens) ──────────────────────────────────────────
PRICING = {
    "claude-opus-4-5":       {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6":     {"input":  3.00, "output": 15.00},
    "claude-haiku-4-5":      {"input":  0.80, "output":  4.00},
}
DEFAULT_MODEL = "claude-sonnet-4-6"

LOG_FILE = Path(__file__).parent / "token_usage.jsonl"   # one JSON record per line


# ── Core logger ───────────────────────────────────────────────────────────────
class TokenLogger:
    """
    Usage:
        logger = TokenLogger()
        response = client.messages.create(...)          # your existing call
        logger.log(response, label="analyze_company", ticker="RELIANCE")
        logger.print_session_summary()
    """

    def __init__(self, log_file: Path = LOG_FILE):
        self.log_file = log_file
        self.session_records: list[dict] = []
        self.session_start = datetime.now()

    # ── Single-call logging ───────────────────────────────────────────────────
    def log(self, response, label: str = "api_call", ticker: str = "") -> dict:
        """
        Pass the raw Anthropic response object.
        Works with both streaming (accumulated) and non-streaming responses.
        """
        usage = response.usage
        model = getattr(response, "model", DEFAULT_MODEL)

        input_tokens  = getattr(usage, "input_tokens",  0)
        output_tokens = getattr(usage, "output_tokens", 0)

        cost = self._calc_cost(model, input_tokens, output_tokens)

        record = {
            "ts":            datetime.now().isoformat(timespec="seconds"),
            "ticker":        ticker,
            "label":         label,
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "total_tokens":  input_tokens + output_tokens,
            "cost_usd":      round(cost, 6),
        }

        self.session_records.append(record)
        self._write_to_file(record)
        self._print_line(record)
        return record

    # ── Summaries ─────────────────────────────────────────────────────────────
    def print_session_summary(self):
        if not self.session_records:
            print("No API calls recorded this session.")
            return

        total_input  = sum(r["input_tokens"]  for r in self.session_records)
        total_output = sum(r["output_tokens"] for r in self.session_records)
        total_cost   = sum(r["cost_usd"]      for r in self.session_records)
        calls        = len(self.session_records)
        elapsed      = datetime.now() - self.session_start

        print("\n" + "═" * 55)
        print("  Foresight  ·  API Token Usage  ·  Session Summary")
        print("═" * 55)
        print(f"  Calls          : {calls}")
        print(f"  Input tokens   : {total_input:,}")
        print(f"  Output tokens  : {total_output:,}")
        print(f"  Total tokens   : {total_input + total_output:,}")
        print(f"  Total cost     : ${total_cost:.4f}")
        print(f"  Elapsed        : {str(elapsed).split('.')[0]}")

        # Remaining budget estimate (if FORESIGHT_BUDGET env var is set)
        budget = float(os.getenv("FORESIGHT_BUDGET", os.getenv("FORESIGHT_BUDGET", "0")))
        if budget > 0:
            spent_all_time = self._total_spent_all_time()
            remaining = budget - spent_all_time
            runs_left  = int(remaining / total_cost) if total_cost > 0 else "∞"
            print(f"\n  Budget         : ${budget:.2f}")
            print(f"  Spent (all)    : ${spent_all_time:.4f}")
            print(f"  Remaining      : ${remaining:.4f}")
            print(f"  Runs left (est): {runs_left}")

        # Per-ticker breakdown
        tickers = {}
        for r in self.session_records:
            t = r["ticker"] or "general"
            tickers.setdefault(t, {"tokens": 0, "cost": 0.0})
            tickers[t]["tokens"] += r["total_tokens"]
            tickers[t]["cost"]   += r["cost_usd"]

        if len(tickers) > 1:
            print("\n  Per-ticker breakdown:")
            for t, v in sorted(tickers.items()):
                print(f"    {t:<15} {v['tokens']:>8,} tokens   ${v['cost']:.4f}")

        print("═" * 55 + "\n")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _calc_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = PRICING.get(model, PRICING[DEFAULT_MODEL])
        return (input_tokens / 1_000_000) * prices["input"] + \
               (output_tokens / 1_000_000) * prices["output"]

    def _print_line(self, r: dict):
        ticker_str = f"[{r['ticker']}] " if r["ticker"] else ""
        print(f"  🔢 {ticker_str}{r['label']} → "
              f"{r['input_tokens']}in + {r['output_tokens']}out = "
              f"{r['total_tokens']} tokens  (${r['cost_usd']:.5f})")

    def _write_to_file(self, record: dict):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def _total_spent_all_time(self) -> float:
        if not self.log_file.exists():
            return 0.0
        total = 0.0
        with open(self.log_file, encoding="utf-8") as f:
            for line in f:
                try:
                    total += json.loads(line).get("cost_usd", 0.0)
                except json.JSONDecodeError:
                    pass
        return total


# ── Convenience: read all historical spend ────────────────────────────────────
def print_all_time_report(log_file: Path = LOG_FILE):
    if not log_file.exists():
        print("No usage log found yet.")
        return
    records = []
    with open(log_file, encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if not records:
        print("Log is empty.")
        return

    total_cost = sum(r["cost_usd"] for r in records)
    print(f"\nAll-time spend across {len(records)} calls: ${total_cost:.4f}")
    print(f"Log file: {log_file}\n")
