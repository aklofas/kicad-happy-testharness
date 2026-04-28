#!/usr/bin/env python3
"""Pre-push advisory wrapper for A7.

Runs gold-currency + batch-diff in report-only mode and prints output to
stdout/stderr. Used by pre-push hooks or CI advisory jobs to surface A7
findings without blocking. Hard-gating happens elsewhere (schema-bumping
PRs use check_gold_currency.py + run_extraction_checks.py directly).

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §7.1.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_HARNESS_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    """Run gold currency-check then batch-diff; ignore exit codes (advisory only)."""
    print("=== A7 advisory: gold currency check ===")
    subprocess.run(
        [sys.executable,
         str(_HARNESS_ROOT / "regression" / "check_gold_currency.py"),
         "--all"],
        check=False,
    )
    print()
    print("=== A7 advisory: extraction diff vs gold ===")
    subprocess.run(
        [sys.executable,
         str(_HARNESS_ROOT / "regression" / "run_extraction_checks.py"),
         "--all"],
        check=False,
    )


if __name__ == "__main__":
    main()
