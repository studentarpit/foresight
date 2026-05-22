"""
Tracks every Claude API call made during a Foresight session.

Usage (after patching analyzer.py):
    from ai.token_logger import record, session_summary

Records written to: token_usage.jsonl  (one JSON object per line)
Live output printed per call.
Call session_summary() at end of scan to see totals + cost + remaining budget.

Set FORESIGHT_BUDGET=5.00 in .env to enable remaining-runs estimate.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# claude-sonnet-4-20250514 pricing (USD per token, May 2026)
_INPUT_COST_PER_TOKEN  = 3.00 / 1_000_000   # $3.00 / MTok
_OUTPUT_COST_PER_TOKEN = 15.00 / 1_000_000  # $15.00 / MTok

_LOG_FILE = Path(__file__).parent.parent / "data" / "token_usage.jsonl"

# Session accumulators — reset each time this module is imported fresh
_session_start: float = time.monotonic()
_session_calls: list[dict] = []


def record(label: str, input_tokens: int, output_tokens: int) -> None:
    """Log one API call, print a live summary line, append to JSONL file.

    Call this immediately after every client.messages.create() call.
    """
    cost = (input_tokens * _INPUT_COST_PER_TOKEN
            + output_tokens * _OUTPUT_COST_PER_TOKEN)
    session_cost = sum(c["cost_usd"] for c in _session_calls) + cost
    elapsed = time.monotonic() - _session_start

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": label or "call",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
    }
    _session_calls.append(entry)
    _append_to_log(entry)

    # Live per-call line
    tag = f"[{label}]" if label else "[api]"
    print(
        f"  {tag:<28} "
        f"{input_tokens:>5} in + {output_tokens:>5} out  "
        f"${cost:.4f}  |  session ${session_cost:.4f}  "
        f"({elapsed:.0f}s)"
    )


def session_summary() -> None:
    """Print a per-call table plus totals and remaining budget estimate."""
    if not _session_calls:
        print("[token_logger] No API calls recorded this session.")
        return

    elapsed = time.monotonic() - _session_start
    total_in  = sum(c["input_tokens"]  for c in _session_calls)
    total_out = sum(c["output_tokens"] for c in _session_calls)
    total_cost = sum(c["cost_usd"]     for c in _session_calls)

    print("\n" + "-" * 72)
    print(f"  {'Foresight Token Usage  |  Session Summary':^68}")
    print("-" * 72)
    print(f"  {'Label':<28} {'In':>6} {'Out':>6}  {'Cost':>8}")
    print("-" * 72)
    for c in _session_calls:
        print(
            f"  {c['label']:<28} {c['input_tokens']:>6} {c['output_tokens']:>6}"
            f"  ${c['cost_usd']:>7.4f}"
        )
    print("-" * 72)
    print(
        f"  {'TOTAL':<28} {total_in:>6} {total_out:>6}  ${total_cost:>7.4f}"
        f"   ({elapsed:.1f}s)"
    )
    print("-" * 72)

    # Remaining runs estimate
    budget = _get_budget()
    if budget and total_cost > 0:
        all_time_cost = _all_time_cost()
        remaining_budget = max(0.0, budget - all_time_cost)
        avg_cost_per_run = total_cost  # this session = one run
        remaining_runs = remaining_budget / avg_cost_per_run if avg_cost_per_run else 0
        print(
            f"  Budget: ${budget:.2f}  |  All-time spent: ${all_time_cost:.4f}"
            f"  |  Remaining budget: ${remaining_budget:.4f}"
        )
        print(f"  Estimated remaining full scans at this cost: {remaining_runs:.0f}")
        print("-" * 72)

    print()


def all_time_summary() -> None:
    """Print aggregate stats from the persistent token_usage.jsonl log."""
    entries = _load_log()
    if not entries:
        print("[token_logger] No all-time log found.")
        return

    total_cost = sum(e.get("cost_usd", 0) for e in entries)
    total_calls = len(entries)
    total_in  = sum(e.get("input_tokens", 0)  for e in entries)
    total_out = sum(e.get("output_tokens", 0) for e in entries)

    print("\n" + "-" * 50)
    print(f"  All-time token usage ({total_calls} calls)")
    print("-" * 50)
    print(f"  Input tokens : {total_in:,}")
    print(f"  Output tokens: {total_out:,}")
    print(f"  Total cost   : ${total_cost:.4f}")
    print("-" * 50)


def reset_session() -> None:
    """Clear session accumulators (useful for testing or a new scan run)."""
    global _session_start, _session_calls
    _session_start = time.monotonic()
    _session_calls = []


# -- internal helpers ----------------------------------------------------------

def _append_to_log(entry: dict) -> None:
    """Append one entry to the JSONL log file."""
    try:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # never crash the main flow over logging


def _load_log() -> list[dict]:
    """Read all entries from token_usage.jsonl."""
    if not _LOG_FILE.exists():
        return []
    entries = []
    with _LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _all_time_cost() -> float:
    """Sum cost_usd across the entire JSONL log."""
    return sum(e.get("cost_usd", 0) for e in _load_log())


def _get_budget() -> float | None:
    """Read FORESIGHT_BUDGET from env (falls back to legacy FORESIGHT_BUDGET for compat)."""
    raw = (os.getenv("FORESIGHT_BUDGET") or os.getenv("FORESIGHT_BUDGET") or "").strip()
    try:
        return float(raw) if raw else None
    except ValueError:
        return None
