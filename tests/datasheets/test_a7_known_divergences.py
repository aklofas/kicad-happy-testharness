"""Tests for _KNOWN_DIVERGENCES.md content + cross-reference behavior.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §6.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TIER = "unit"

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KD_PATH = REPO_ROOT / "regression" / "reference_extractions" / "_KNOWN_DIVERGENCES.md"


def test_kd_file_exists():
    assert KD_PATH.exists()


def test_kd_has_4_seed_entries():
    content = KD_PATH.read_text()
    expected_headers = [
        "## `mcu.core_speed_max` bare-scalar shape",
        "## opamp/mcu cross-category TOPR-vs-T_A divergence",
        "## `body_mm` shape — already canonical",
        "## `datasheet_lookup.sanitize_mpn` dot-stripping",
    ]
    for h in expected_headers:
        assert h in content, f"missing header: {h}"


def test_kd_each_entry_has_source_or_resolution_line():
    content = KD_PATH.read_text()
    sections = content.split("## ")[1:]  # drop preamble
    for sec in sections:
        assert "**Source:**" in sec or "**Resolution:**" in sec, \
               f"entry without source/resolution: {sec[:100]}"


def test_kd_referenced_in_check_gold_currency_help():
    r = subprocess.run(
        [sys.executable,
         str(REPO_ROOT / "regression" / "check_gold_currency.py"),
         "--help"],
        capture_output=True, text=True,
    )
    assert "known-divergences" in r.stdout.lower() or \
           "known_divergences" in r.stdout.lower()


# Custom-runner __main__ block (harness convention)
if __name__ == "__main__":
    import traceback
    fn_names = sorted(n for n, v in globals().items()
                      if n.startswith("test_") and callable(v))
    failed = 0
    passed = 0
    for n in fn_names:
        try:
            globals()[n]()
            print(f"PASS {n}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {n}: {e}")
            failed += 1
        except Exception as e:
            print(f"FAIL {n}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"{passed} passed, {failed} failed ({len(fn_names)} total)")
    sys.exit(0 if failed == 0 else 1)
