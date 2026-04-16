"""Unit tests for regression/assertion_metrics.py compute_margin().

compute_margin() scores how close an assertion result is to its boundary:
- 0.0 = at boundary (fragile)
- 1.0 = far from boundary (robust)
- Used by `cmd_fragile` to flag near-boundary assertions.
"""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from regression.assertion_metrics import compute_margin  # noqa: E402


# ---------------------------------------------------------------------------
# range operator
# ---------------------------------------------------------------------------

def test_margin_range_at_center_is_half():
    assertion = {"check": {"op": "range", "min": 0, "max": 100}}
    result = {"passed": True, "actual": 50}
    # min(50-0, 100-50) / (100-0) = 50/100 = 0.5
    m = compute_margin(assertion, result)
    assert abs(m - 0.5) < 0.01, f"Got {m}"


def test_margin_range_at_boundary_is_zero():
    assertion = {"check": {"op": "range", "min": 0, "max": 100}}
    result = {"passed": True, "actual": 0}
    m = compute_margin(assertion, result)
    assert m == 0.0


def test_margin_range_failed_is_zero():
    assertion = {"check": {"op": "range", "min": 0, "max": 100}}
    result = {"passed": False, "actual": 150}
    assert compute_margin(assertion, result) == 0.0


# ---------------------------------------------------------------------------
# min_count / greater_than
# ---------------------------------------------------------------------------

def test_margin_min_count_far_above_threshold():
    assertion = {"check": {"op": "min_count", "value": 10}}
    result = {"passed": True, "actual": 100}
    # (100-10)/10 = 9.0, clamped to 1.0
    assert compute_margin(assertion, result) == 1.0


def test_margin_min_count_just_above_threshold():
    assertion = {"check": {"op": "min_count", "value": 10}}
    result = {"passed": True, "actual": 11}
    # (11-10)/10 = 0.1
    m = compute_margin(assertion, result)
    assert abs(m - 0.1) < 0.01, f"Got {m}"


def test_margin_min_count_zero_threshold_is_robust():
    """value=0 → any pass is maximally robust."""
    assertion = {"check": {"op": "min_count", "value": 0}}
    result = {"passed": True, "actual": 5}
    assert compute_margin(assertion, result) == 1.0


# ---------------------------------------------------------------------------
# max_count / less_than
# ---------------------------------------------------------------------------

def test_margin_max_count_just_under_threshold():
    assertion = {"check": {"op": "max_count", "value": 10}}
    result = {"passed": True, "actual": 9}
    # (10-9)/10 = 0.1
    m = compute_margin(assertion, result)
    assert abs(m - 0.1) < 0.01, f"Got {m}"


# ---------------------------------------------------------------------------
# binary operators
# ---------------------------------------------------------------------------

def test_margin_binary_op_passed_is_one():
    assertion = {"check": {"op": "exists"}}
    result = {"passed": True, "actual": "anything"}
    assert compute_margin(assertion, result) == 1.0


def test_margin_binary_op_failed_is_zero():
    assertion = {"check": {"op": "contains_match"}}
    result = {"passed": False, "actual": None}
    assert compute_margin(assertion, result) == 0.0


# ---------------------------------------------------------------------------
# edge cases
# ---------------------------------------------------------------------------

def test_margin_non_numeric_actual_returns_zero_or_one():
    """Non-numeric actual with range op: returns 0.0 (explicit early return at line 47)."""
    assertion = {"check": {"op": "range", "min": 0, "max": 100}}
    result = {"passed": True, "actual": "not a number"}
    # Per source line 46-47: if not isinstance(actual, (int, float)): return 0.0
    assert compute_margin(assertion, result) == 0.0


def test_margin_missing_op_treated_as_binary():
    """No op → binary (pass=1.0, fail=0.0)."""
    assertion = {"check": {}}
    assert compute_margin(assertion, {"passed": True}) == 1.0
    assert compute_margin(assertion, {"passed": False}) == 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
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
