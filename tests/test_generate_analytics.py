"""Unit tests for tools/generate_analytics.py — _count_issues_in_line."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from generate_analytics import _count_issues_in_line


# --- Normal cases ---

def test_single_issue_returns_1():
    # A line with no range and no comma list → always returns 1
    assert _count_issues_in_line("### KH-042 — Some fix", "KH") == 1


def test_range_inclusive():
    # "KH-001 through KH-011" → 11 issues
    assert _count_issues_in_line("### KH-001 through KH-011", "KH") == 11


def test_range_with_comma_extra():
    # "KH-001 through KH-011, KH-014" → 11 + 1 = 12
    assert _count_issues_in_line("### KH-001 through KH-011, KH-014", "KH") == 12


def test_range_with_multiple_extra():
    # Range plus two extra IDs
    line = "### KH-001 through KH-005, KH-010, KH-023"
    assert _count_issues_in_line(line, "KH") == 7  # 5 + 2


# --- Prefix isolation ---

def test_prefix_th():
    assert _count_issues_in_line("### TH-001 through TH-003", "TH") == 3


def test_prefix_does_not_match_other():
    # KH prefix should not count TH IDs
    line = "### TH-001 through TH-003"
    assert _count_issues_in_line(line, "KH") == 1  # no KH range found → single fallback


# --- Edge cases ---

def test_range_of_one():
    # "KH-007 through KH-007" → 1
    assert _count_issues_in_line("### KH-007 through KH-007", "KH") == 1


def test_empty_string():
    # No prefix IDs → returns 1 (single-issue fallback)
    assert _count_issues_in_line("", "KH") == 1


def test_comma_only_no_range():
    # Two IDs with a comma but no "through" → treated as a single-issue line (no range)
    # The function only counts extras when a "through" range is present
    line = "### KH-001, KH-002"
    assert _count_issues_in_line(line, "KH") == 1


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
