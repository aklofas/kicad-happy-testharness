"""KH-411 — `below_min_pdiss` covered two causes: a real sub-threshold
estimate AND "power_dissipation never computed upstream". The latter is now
`no_pdiss_estimate`. Inputs mirror detect_power_regulators' real field names
(ref/value/topology/power_dissipation{estimated_pdiss_W,...}).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from analyze_thermal import _estimate_all_power_dissipation, MIN_PDISS_W


def _reg(ref, **extra):
    d = {"detector": "detect_power_regulators", "ref": ref, "value": "LDO", "topology": "ldo"}
    d.update(extra)
    return d


def _reasons(*regs):
    _, skipped = _estimate_all_power_dissipation({"findings": list(regs), "power_budget": {}})
    return {s["ref"]: s["reason"] for s in skipped}


def test_ldo_missing_pdiss_is_no_pdiss_estimate():
    assert _reasons(_reg("U1")) == {"U1": "no_pdiss_estimate"}


def test_ldo_null_pdiss_is_no_pdiss_estimate():
    assert _reasons(_reg("U1", power_dissipation=None)) == {"U1": "no_pdiss_estimate"}


def test_ldo_pdiss_without_estimate_key_is_no_pdiss_estimate():
    assert _reasons(_reg("U1", power_dissipation={"vout_V": 3.3})) == {"U1": "no_pdiss_estimate"}


def test_ldo_sub_threshold_is_below_min_pdiss():
    tiny = MIN_PDISS_W / 10
    r = _reasons(_reg("U2", power_dissipation={"estimated_pdiss_W": tiny, "vin_estimated_V": 5,
                                                "vout_V": 3.3, "estimated_iout_A": 0.001}))
    assert r == {"U2": "below_min_pdiss"}


def test_ldo_above_threshold_not_skipped():
    big = MIN_PDISS_W * 10
    results, skipped = _estimate_all_power_dissipation({"findings": [
        _reg("U3", power_dissipation={"estimated_pdiss_W": big, "vin_estimated_V": 5,
                                      "vout_V": 3.3, "estimated_iout_A": 0.2})], "power_budget": {}})
    assert [r["ref"] for r in results] == ["U3"] and skipped == []


if __name__ == "__main__":
    import sys as _sys
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith("test_") and callable(fn)]
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
    _sys.exit(1 if failed else 0)
