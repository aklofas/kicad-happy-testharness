"""Unit tests for regression/seed.py — assertion generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from seed import (
    _range_bounds,
    generate_spice_assertions,
    generate_datasheets_assertions,
)


# === _range_bounds ===

def test_range_bounds_normal():
    lo, hi = _range_bounds(100, 0.10)
    assert lo == 90
    assert 110 <= hi <= 111  # ceil(110.0) may be 111 due to float precision

def test_range_bounds_zero():
    lo, hi = _range_bounds(0, 0.10)
    # Should NOT be (0, 0) — minimum spread of 2
    assert hi > lo
    assert lo == 0
    assert hi >= 1

def test_range_bounds_one():
    lo, hi = _range_bounds(1, 0.10)
    # Small value: minimum spread of 2
    assert hi - lo >= 2

def test_range_bounds_large():
    lo, hi = _range_bounds(1000, 0.10)
    assert lo == 900
    assert hi == 1100

def test_range_bounds_tight_tolerance():
    lo, hi = _range_bounds(50, 0.01)
    # 50 * 0.99 = 49.5, floor = 49; 50 * 1.01 = 50.5, ceil = 51
    assert lo == 49
    assert hi == 51

def test_range_bounds_no_negative():
    lo, hi = _range_bounds(1, 0.50)
    assert lo >= 0


# === generate_spice_assertions ===

def test_spice_assertions_basic():
    data = {
        "summary": {"total": 10, "pass": 8, "warn": 1, "fail": 0, "skip": 1},
        "simulation_results": [
            {"subcircuit_type": "rc_filter"},
            {"subcircuit_type": "rc_filter"},
            {"subcircuit_type": "opamp_circuit"},
        ],
    }
    assertions = generate_spice_assertions(data)
    assert len(assertions) >= 3  # total range + pass min + 2 type counts
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids)), "IDs should be unique"

def test_spice_assertions_empty():
    data = {"summary": {"total": 0}, "simulation_results": []}
    assertions = generate_spice_assertions(data)
    assert assertions == []

def test_spice_assertions_no_pass():
    data = {
        "summary": {"total": 5, "pass": 0, "warn": 5},
        "simulation_results": [{"subcircuit_type": "rc_filter"}] * 5,
    }
    assertions = generate_spice_assertions(data)
    # Should still have total range + type count, but NO pass min
    descs = [a["description"] for a in assertions]
    assert not any("passing" in d for d in descs)


# === generate_datasheets_assertions ===

def test_datasheets_assertions_basic():
    data = {
        "extracted": 5, "sufficient": 4,
        "by_category": {"opamp": 2, "regulator": 3},
        "parts": {},
    }
    assertions = generate_datasheets_assertions(data)
    assert len(assertions) >= 3  # count range + sufficient min + 2 categories
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_datasheets_assertions_empty():
    data = {"extracted": 0, "sufficient": 0, "by_category": {}, "parts": {}}
    assertions = generate_datasheets_assertions(data)
    assert assertions == []


# === Runner ===

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
