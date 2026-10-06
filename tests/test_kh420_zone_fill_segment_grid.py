"""KH-420 — ZoneFills.min_edge_distance walked every polygon vertex per
query point; KH-413's 8-points-per-THT-pad sampling pushed NLoy's 10x12
touch keyboard from ~10 s to ~110 s (harness 120 s cap). A lazily built
per-fill segment grid with an exact ring-walk cutoff makes each query
visit only nearby segments. Results must be byte-identical to brute force.
"""

TIER = "unit"

import json
import math
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
sys.path.insert(0, str(_KH / "skills" / "kicad" / "scripts"))

import analyze_pcb
from analyze_pcb import ZoneFills, _dist_point_to_segment

NLOY = _HARNESS / "repos/NLoy/Touch_Keyboard_10x12_KiCAD/Touch_Keyboard_10x12_Matrix.kicad_pcb"
KH413 = _HARNESS / "tests/fixtures/kh413/tht_touch_pad.kicad_pcb"


def _brute(coords, x, y):
    n = len(coords)
    return min(_dist_point_to_segment(x, y, *coords[i], *coords[(i + 1) % n]) for i in range(n))


def _random_polygon(rng, cx, cy, r, n):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * rng.uniform(0.4, 1.0)
        pts.append((round(cx + rr * math.cos(a), 4), round(cy + rr * math.sin(a), 4)))
    return pts


def test_grid_matches_brute_force_on_random_polygons():
    rng = random.Random(420)
    zf = ZoneFills()
    polys = []
    for k in range(6):
        p = _random_polygon(rng, rng.uniform(0, 200), rng.uniform(0, 200), rng.uniform(5, 60), rng.randint(3, 400))
        polys.append(p)
        zf.add(k, "F.Cu", p)
    zf.add(99, "B.Cu", _random_polygon(rng, 50, 50, 30, 50))  # other layer, must be ignored
    for _ in range(400):
        x, y = rng.uniform(-50, 250), rng.uniform(-50, 250)
        got = zf.min_edge_distance(x, y, "F.Cu")
        want = min(_brute(p, x, y) for p in polys)
        assert abs(got - want) < 1e-9, (x, y, got, want)
        # zone_idxs filter still honoured
        got2 = zf.min_edge_distance(x, y, "F.Cu", {2})
        assert abs(got2 - _brute(polys[2], x, y)) < 1e-9


def test_grid_handles_degenerate_inputs():
    zf = ZoneFills()
    assert zf.min_edge_distance(0, 0, "F.Cu") == float("inf")
    zf.add(0, "F.Cu", [(1.0, 1.0)])                       # single vertex
    assert abs(zf.min_edge_distance(0, 0, "F.Cu") - math.sqrt(2)) < 1e-9
    zf.add(1, "F.Cu", [(10.0, 0.0), (20.0, 0.0)])          # zero-height bbox
    assert abs(zf.min_edge_distance(15.0, 3.0, "F.Cu") - 3.0) < 1e-9
    zf.add(2, "F.Cu", [(5.0, 5.0), (5.0, 5.0), (5.0, 5.0)])  # all-identical vertices
    assert abs(zf.min_edge_distance(5.0, 6.0, "F.Cu") - 1.0) < 1e-9


def test_kh413_fixture_output_unchanged():
    out = subprocess.run([sys.executable, str(_KH / "skills/kicad/scripts/analyze_pcb.py"),
                          str(KH413), "--full"], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-2000:]
    f = [f for f in json.loads(out.stdout)["findings"] if f.get("rule_id") == "CP-003"]
    assert len(f) == 1 and abs(f[0]["gnd_clearance_mm"] - 0.5) < 0.05, f


def test_nloy_touch_keyboard_only_deterministic_under_30s():
    """Uses --only-deterministic, not --full: KH-420's regression and its
    "10 s -> 110 s" symptom (ISSUES.md) are both measured in this mode.
    --full on this board has a separate, pre-existing ~80 s
    _point_in_polygon cost (analyze_return_path_continuity /
    pcb_connectivity.build_connectivity_graph) that is not KH-420 and
    exists at v2.3.0 too, so an absolute --full bound can't guard this
    regression.
    """
    if not NLOY.exists():
        print("  SKIP: NLoy corpus board absent")
        return
    # Use a writable scratch path rather than os.devnull: analyze_pcb.py's
    # main() derives its capability-mode sidecar directory from --output's
    # parent, and /dev is root-owned (0755) on a non-root box — an
    # unrelated, pre-existing permission wall, not a KH-420 behavior.
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "out.json")
        t0 = time.time()
        out = subprocess.run([sys.executable, str(_KH / "skills/kicad/scripts/analyze_pcb.py"),
                              str(NLOY), "--only-deterministic", "--output", out_path],
                             capture_output=True, text=True, timeout=300)
        elapsed = time.time() - t0
    assert out.returncode == 0, out.stderr[-2000:]
    assert elapsed < 30, (
        f"{elapsed:.1f}s on --only-deterministic "
        f"(this box: 9.8s at v2.3.0, 108.9s at b008afa, 8.5s at KH-420 HEAD)"
    )


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
        except (AssertionError, AttributeError) as e:
            failed += 1
            print(f"  FAIL: {name}: {e!r}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
