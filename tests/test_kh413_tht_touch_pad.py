"""KH-413 — CP-003 pad sampling skipped any pad whose `layers` did not
literally contain the probed layer; through-hole pads carry the "*.Cu"
wildcard, so a THT-only touch footprint fell back to the footprint origin
(the KH-373 0.0 mm failure class again). Fixture: tests/fixtures/kh413/.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
sys.path.insert(0, str(_KH / "skills" / "kicad" / "scripts"))
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
FIXTURE = _HARNESS / "tests/fixtures/kh413/tht_touch_pad.kicad_pcb"
_CACHE = {}


def _cp003():
    if "f" not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(FIXTURE), "--full"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["f"] = [f for f in json.loads(out.stdout)["findings"] if f.get("rule_id") == "CP-003"]
    return _CACHE["f"]


def test_tht_touch_pad_measured_from_outline():
    f = _cp003()
    assert len(f) == 1 and f[0]["components"] == ["TOUCH1"], f
    assert f[0]["measurement_basis"] == "filled_polygon"
    assert abs(f[0]["gnd_clearance_mm"] - 0.5) < 0.05, f[0]["gnd_clearance_mm"]


def test_pad_on_layer_wildcards():
    from analyze_pcb import _pad_on_layer
    assert _pad_on_layer({"layers": ["*.Cu", "*.Mask"]}, "F.Cu", "F.Cu")
    assert _pad_on_layer({"layers": ["*.Cu", "*.Mask"]}, "In1.Cu", "F.Cu")
    assert _pad_on_layer({"layers": ["F&B.Cu"]}, "B.Cu", "F.Cu")
    assert not _pad_on_layer({"layers": ["F&B.Cu"]}, "In1.Cu", "F.Cu")
    assert not _pad_on_layer({"layers": ["B.Cu", "B.Mask"]}, "F.Cu", "F.Cu")


def test_pad_on_layer_explicit_list():
    from analyze_pcb import _pad_on_layer
    assert _pad_on_layer({"layers": ["F.Cu", "B.Cu"]}, "F.Cu", "F.Cu")
    assert _pad_on_layer({"layers": ["F.Cu", "B.Cu"]}, "B.Cu", "F.Cu")
    # No layers key at all: falls back to the footprint's layer.
    assert _pad_on_layer({}, "F.Cu", "F.Cu")
    assert not _pad_on_layer({}, "B.Cu", "F.Cu")


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
        except (AssertionError, ImportError) as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
