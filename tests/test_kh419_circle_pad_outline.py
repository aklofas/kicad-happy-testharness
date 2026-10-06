"""KH-419 — `_pad_sample_points` sampled the 8 corners/edge-midpoints of a
pad's bounding box regardless of `shape`. On a circle the corners sit at
r·√2, well outside the copper; SacMap rev2's two Ø15 mm touch pads read an
unrelated fill cutout 3.1 mm off the real outline as their CP-003 clearance.
Separately, the via-analysis `via_in_pad` list used the same unrotated bbox
test and flagged vias in the bbox corner region but outside a circular pad.
Fixture: tests/fixtures/kh419/ (a Ø15 mm circle touch pad with a 1.0 mm
keyhole-ring GND clearance plus an island 0.1 mm from the bbox corner but
3.3 mm from the circumference).
"""

TIER = "unit"

import json
import math
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
sys.path.insert(0, str(_KH / "skills" / "kicad" / "scripts"))
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
FIXTURE = _HARNESS / "tests/fixtures/kh419/circle_touch_pad.kicad_pcb"
KH413_FIXTURE = _HARNESS / "tests/fixtures/kh413/tht_touch_pad.kicad_pcb"
SACMAP = Path.home() / "Projects/sandbox/Old-Reviews/sacmap-rev2/8/sacmap-rev2.kicad_pcb"
_CACHE = {}


def _run(fixture):
    key = str(fixture)
    if key not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(fixture), "--full"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE[key] = json.loads(out.stdout)
    return _CACHE[key]


def _cp003(fixture):
    return [f for f in _run(fixture)["findings"] if f.get("rule_id") == "CP-003"]


def _via_in_pad(fixture):
    return _run(fixture).get("vias", {}).get("via_analysis", {}).get("via_in_pad")


def test_outline_points_circle():
    from analyze_pcb import _pad_outline_points
    pts = _pad_outline_points("circle", 7.5, 7.5)
    assert len(pts) == 8, pts
    for x, y in pts:
        assert abs(math.hypot(x, y) - 7.5) < 1e-9, (x, y)
    rounded = [(round(x, 6), round(y, 6)) for x, y in pts]
    assert (7.5, 0.0) in rounded, rounded
    assert (0.0, 7.5) in rounded, rounded


def test_outline_points_oval():
    from analyze_pcb import _pad_outline_points
    pts = _pad_outline_points("oval", 5.0, 2.0)
    for x, y in pts:
        val = max(abs(x) - 3.0, 0) ** 2 + y ** 2
        assert abs(val - 4.0) < 1e-9, (x, y, val)
    rounded = [(round(x, 6), round(y, 6)) for x, y in pts]
    assert (5.0, 0.0) in rounded, rounded
    assert (0.0, 2.0) in rounded, rounded

    pts2 = _pad_outline_points("oval", 2.0, 5.0)
    for x, y in pts2:
        val = max(abs(y) - 3.0, 0) ** 2 + x ** 2
        assert abs(val - 4.0) < 1e-9, (x, y, val)
    rounded2 = [(round(x, 6), round(y, 6)) for x, y in pts2]
    assert (2.0, 0.0) in rounded2, rounded2
    assert (0.0, 5.0) in rounded2, rounded2


def test_outline_points_rect_unchanged():
    from analyze_pcb import _pad_outline_points
    expected = [(-1, -2), (0, -2), (1, -2), (1, 0), (1, 2), (0, 2), (-1, 2), (-1, 0)]
    assert _pad_outline_points("rect", 1, 2) == expected
    assert _pad_outline_points("roundrect", 1, 2) == expected


def test_fixture_circle_pad_clearance():
    f = _cp003(FIXTURE)
    assert len(f) == 1 and f[0]["components"] == ["TOUCH1"], f
    assert f[0]["measurement_basis"] == "filled_polygon"
    assert abs(f[0]["gnd_clearance_mm"] - 1.0) < 0.05, f[0]["gnd_clearance_mm"]


def test_fixture_via_in_pad_uses_outline():
    vip = _via_in_pad(FIXTURE)
    assert vip is not None and len(vip) == 1, vip
    assert vip[0]["via_x"] == 127.0, vip


def test_sacmap_tp1_regression():
    if not SACMAP.exists():
        print(f"SKIP: {SACMAP} not present")
        return
    f = [x for x in _cp003(SACMAP) if set(x["components"]) & {"TP1", "TP2"}]
    by_ref = {}
    for finding in f:
        for ref in finding["components"]:
            by_ref[ref] = finding["gnd_clearance_mm"]
    for ref in ("TP1", "TP2"):
        assert ref in by_ref, by_ref
        assert abs(by_ref[ref] - 1.0) < 0.02, (ref, by_ref[ref])
    vip = _via_in_pad(SACMAP)
    if vip:
        assert not any(v["component"] in ("TP1", "TP2") for v in vip), vip


def test_kh413_tht_fixture_unchanged():
    f = _cp003(KH413_FIXTURE)
    assert len(f) == 1 and f[0]["components"] == ["TOUCH1"], f
    assert abs(f[0]["gnd_clearance_mm"] - 0.5) < 0.05, f[0]["gnd_clearance_mm"]


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
