"""KH-408 — analyze_thermal_pad_vias rotated via offsets by -(footprint +
pad) angle; KiCad's pad angle is already absolute (v2.3.0 fixed the same
mistake in CP-003's _pad_sample_points, commit ba3a269). Fixture: identical
QFN at 0° (U1) and 30° (U2); via_count must match.

TV-001 entries are folded into the top-level `findings` list (rule_id ==
"TV-001") by analyze_pcb.py's harmonization pass, not a separate
`thermal_pad_vias` key -- this test reads them from `findings`.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
FIXTURE = _HARNESS / "tests/fixtures/kh408/qfn_rotated.kicad_pcb"
_CACHE = {}


def _thermal():
    if "t" not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(FIXTURE), "--full"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        data = json.loads(out.stdout)
        tv = [f for f in data.get("findings", []) if f.get("rule_id") == "TV-001"]
        _CACHE["t"] = {t["component"]: t for t in tv}
    return _CACHE["t"]


def test_fixture_has_both_thermal_pads():
    assert set(_thermal()) == {"U1", "U2"}, set(_thermal())


def test_unrotated_counts_all_three():
    assert _thermal()["U1"]["via_count"] == 3


def test_rotated_counts_all_three():
    assert _thermal()["U2"]["via_count"] == 3, _thermal()["U2"]


def test_rotation_invariant_adequacy():
    assert _thermal()["U1"]["adequacy"] == _thermal()["U2"]["adequacy"]


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
