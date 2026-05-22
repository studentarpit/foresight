"""
Patches ai/analyzer.py to add token logging via ai/token_logger.py.
No restructuring — only 3 targeted insertions.

  python analyzer_patch_instructions.py           # preview the diff
  python analyzer_patch_instructions.py --apply   # apply core patches
  python analyzer_patch_instructions.py --apply --labels  # + call-site labels

After applying, session_summary() will print at the end of each scan.
Set FORESIGHT_BUDGET=5.00 in .env to see remaining-runs estimate.
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parent / "ai" / "analyzer.py"

# ── 3 core changes — the only ones needed for logging to work ─────────────────

PATCHES = [
    (
        "Add token_logger import after ai.prompts block",
        """\
from ai.prompts import (
    DEEP_ANALYSIS_PROMPT,
    MASTER_TRACKER_PROMPT,
    MF_ANALYSIS_PROMPT,
    SCAN_PROMPT,
    VALUATION_PROMPT,
)""",
        """\
from ai.prompts import (
    DEEP_ANALYSIS_PROMPT,
    MASTER_TRACKER_PROMPT,
    MF_ANALYSIS_PROMPT,
    SCAN_PROMPT,
    VALUATION_PROMPT,
)
from ai.token_logger import record, session_summary  # noqa: F401""",
    ),
    (
        "Add label= parameter to _call_claude signature",
        "def _call_claude(prompt: str, max_tokens: int = 2048) -> Optional[str]:",
        'def _call_claude(prompt: str, max_tokens: int = 2048, label: str = "") -> Optional[str]:',
    ),
    (
        "Record usage after messages.create() inside _call_claude",
        """\
        msg = client.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text""",
        """\
        msg = client.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        record(label, msg.usage.input_tokens, msg.usage.output_tokens)
        return msg.content[0].text""",
    ),
]

# ── Optional: meaningful per-function labels at each call site ────────────────

LABEL_PATCHES = [
    (
        "score_universe: label scan batches",
        "_call_claude(prompt, max_tokens=1024)",
        '_call_claude(prompt, max_tokens=1024, label=f"scan_batch_{i // _BATCH_SIZE}")',
    ),
    (
        "analyze_company: label with ticker",
        "    text = _call_claude(prompt, max_tokens=1500)\n    fallback = {",
        '    ticker = data.get("ticker", "??")\n'
        '    text = _call_claude(prompt, max_tokens=1500, label=f"deep_{ticker}")\n'
        "    fallback = {",
    ),
    (
        "build_valuation_model: label with ticker",
        "    text = _call_claude(prompt, max_tokens=1500)\n    # Arithmetic fallback",
        '    ticker = data.get("ticker", "??")\n'
        '    text = _call_claude(prompt, max_tokens=1500, label=f"valuation_{ticker}")\n'
        "    # Arithmetic fallback",
    ),
    (
        "update_master_tracker: label with ticker",
        "    text = _call_claude(prompt, max_tokens=512)\n    # Arithmetic fallback",
        '    text = _call_claude(prompt, max_tokens=512, label=f"tracker_{company.get(\'ticker\',\'??\')}")\n'
        "    # Arithmetic fallback",
    ),
    (
        "analyze_mf: label with fund name",
        "    text = _call_claude(prompt, max_tokens=512)\n    consistency",
        '    text = _call_claude(prompt, max_tokens=512, label=f"mf_{fund.get(\'name\',\'??\')[:20]}")\n'
        "    consistency",
    ),
]


def _show(patches: list[tuple]) -> None:
    source = TARGET.read_text(encoding="utf-8")
    for desc, old, new in patches:
        found = old in source
        status = "[APPLY] " if found else "[SKIP]  "
        print(f"\n  {status} {desc}")
        if found:
            for line in old.splitlines():
                print(f"    - {line}")
            added = set(new.splitlines()) - set(old.splitlines())
            for line in new.splitlines():
                marker = "+" if line in added else " "
                print(f"    {marker} {line}")


def _apply(patches: list[tuple]) -> int:
    source = TARGET.read_text(encoding="utf-8")
    count = 0
    for desc, old, new in patches:
        if old in source:
            source = source.replace(old, new, 1)
            count += 1
            print(f"  [OK]  {desc}")
        else:
            print(f"  [--]  skipped (not found / already applied): {desc}")
    TARGET.write_text(source, encoding="utf-8")
    return count


def main() -> None:
    applying = "--apply" in sys.argv
    with_labels = "--labels" in sys.argv

    print("\n" + "=" * 62)
    print("  Foresight analyzer.py token-logging patch")
    print("=" * 62)
    print(f"  Target: {TARGET.relative_to(Path(__file__).parent)}")

    if not applying:
        print("\n  CORE PATCHES (3 changes - required):")
        _show(PATCHES)
        print("\n  LABEL PATCHES (5 changes - optional, improves readability):")
        _show(LABEL_PATCHES)
        print()
        print("  To apply:  python analyzer_patch_instructions.py --apply")
        print("  With labels: add --labels flag")
    else:
        print("\n  Applying core patches…")
        n = _apply(PATCHES)
        if with_labels:
            print("\n  Applying call-site label patches…")
            n += _apply(LABEL_PATCHES)
        print(f"\n  {n} change(s) written.")
        print()
        print("  Next steps:")
        print("    1. Add to .env:  FORESIGHT_BUDGET=5.00")
        print("    2. In main.py after scan completes, add:")
        print("         from ai.token_logger import session_summary")
        print("         session_summary()")
        print("    3. Run: streamlit run main.py")
        print()
        print("  All-time log: data/token_usage.jsonl")
    print()


if __name__ == "__main__":
    main()
