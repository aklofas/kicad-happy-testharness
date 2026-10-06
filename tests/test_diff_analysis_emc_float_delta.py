"""`diff_analysis.py --text` crashed on an EMC diff whose risk score changed:
`f"(delta {risk.get('delta', 0):+d})"` raises ValueError on a float delta
(EMC `emc_risk_score` is a float, e.g. 50.5 -> 80.5). SacMap rev2 soak,
2026-10-05. Harness assigns the KH number.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from diff_analysis import format_text


def test_emc_risk_delta_float_renders():
    out = {"analyzer_type": "emc",
           "summary": {"severity": "minor", "total_changes": 1,
                       "added": 0, "removed": 0, "modified": 1},
           "diff": {"risk_score": {"base": 50.5, "head": 80.5, "delta": 30.0}}}
    text = format_text(out)
    assert "EMC Risk Score: 50.5 → 80.5 (delta +30.0)" in text


def test_emc_risk_delta_int_renders():
    out = {"analyzer_type": "emc",
           "summary": {"severity": "minor", "total_changes": 1,
                       "added": 0, "removed": 0, "modified": 1},
           "diff": {"risk_score": {"base": 50, "head": 80, "delta": 30}}}
    assert "(delta +30.0)" in format_text(out)


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
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
