"""KH-412 — (a) DFM-001 / design-rule drill violations whose minimum came
from a footprint pad still said `parameter: "via_drill"`; (b) degenerate
drills such as MeloCar's `(drill 0.00001)` pads were reported faithfully as
"Drill 1e-05mm". Now: `parameter: "pad_drill"` / `drill_source: "pad"`, and
drills below MIN_REAL_DRILL_MM (0.05) are excluded from the minimums and
listed in `vias.via_analysis.degenerate_drills`. Fixture: tests/fixtures/kh412/.

Path note (deviation from the task brief, confirmed against live output):
DFM-001 violations are NOT at `d["dfm"]["violations"]` -- a harmonization
pass in analyze_pcb.py pops the whole `dfm` key and merges its violations
into the top-level `findings` list, keeping only summary data under
`dfm_summary`. This test reads them from `d["findings"]` filtered by
`rule_id == "DFM-001"`. The `design_rule_compliance.violations` path in
the brief is correct as given (verified against live output).

Fixture note: the brief's fixture used a 0.2mm pad-1 drill, but
analyze_pcb.py's DFM-001 check against the JLCPCB standard-tier limit
(also 0.2mm) is a strict `<` -- a drill exactly at the limit does not
violate it. The fixture here uses 0.18mm instead so DFM-001 actually
fires (one violation, the "requires advanced process" warning branch).

Fix round 1 (review): two gaps found in the first pass --
(1) analyze_vias() early-returned {} for a board with zero vias,
silently dropping degenerate_drills and current_capacity.min_pad_drill_mm
for via-less boards (e.g. MeloCar's remote_3.kicad_pcb). Covered here by
test_novias_board_still_reports_pad_facts against
tests/fixtures/kh412/pad_drill_min_novias.kicad_pcb (same footprint as
the main fixture, with the `via` line omitted).
(2) current_capacity.min_drill_mm / ratings still counted degenerate via
drills (filter was `d > 0`, not the MIN_REAL_DRILL_MM floor). Covered
here by test_degenerate_via_excluded_from_current_capacity_min_and_ratings,
calling analyze_vias() directly with a synthetic degenerate + real via.
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
FIXTURE = _HARNESS / "tests/fixtures/kh412/pad_drill_min.kicad_pcb"
FIXTURE_NOVIAS = _HARNESS / "tests/fixtures/kh412/pad_drill_min_novias.kicad_pcb"
_CACHE = {}


def _d():
    if "d" not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(FIXTURE), "--full"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["d"] = json.loads(out.stdout)
    return _CACHE["d"]


def _d_novias():
    if "d_novias" not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(FIXTURE_NOVIAS), "--full"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["d_novias"] = json.loads(out.stdout)
    return _CACHE["d_novias"]


def _dfm_drill_violations():
    return [v for v in _d().get("findings", [])
            if v.get("rule_id") == "DFM-001" and "drill" in v.get("parameter", "")]


def test_min_drill_ignores_degenerate_and_is_pad_sourced():
    assert abs(_d()["dfm_summary"]["metrics"]["min_drill_mm"] - 0.18) < 1e-6


def test_dfm001_parameter_is_pad_drill():
    v = _dfm_drill_violations()
    assert len(v) == 1, v
    assert v[0]["parameter"] == "pad_drill" and abs(v[0]["actual_mm"] - 0.18) < 1e-6, v[0]
    assert "J1" in v[0]["message"]


def test_degenerate_drills_listed():
    dd = _d()["vias"]["via_analysis"].get("degenerate_drills")
    assert dd == [{"kind": "pad", "ref": "J1", "pad": "3", "drill_mm": 1e-05}], dd


def test_min_pad_drill_fact_ignores_degenerate():
    cc = _d()["vias"]["via_analysis"].get("current_capacity", {})
    assert abs(cc.get("min_pad_drill_mm", 0) - 0.18) < 1e-6, cc


def test_design_rule_violation_attributes_pad():
    drc = [v for v in _d().get("design_rule_compliance", {}).get("violations", [])
           if v.get("rule") == "min_via_drill"]
    assert len(drc) == 1, drc
    assert abs(drc[0]["actual_mm"] - 0.18) < 1e-6
    assert drc[0]["drill_source"] == "pad" and drc[0]["source_ref"] == "J1", drc[0]


def test_floor_boundary_0p05_is_real():
    from analyze_pcb import MIN_REAL_DRILL_MM, _pad_drills
    assert MIN_REAL_DRILL_MM == 0.05
    fps = [{"reference": "X1", "pads": [
        {"type": "thru_hole", "number": "1", "drill": 0.05},
        {"type": "thru_hole", "number": "2", "drill": 0.049},
        {"type": "thru_hole", "number": "3", "drill": 0.0},
    ]}]
    assert _pad_drills(fps) == [0.05]


def test_degenerate_helper_sorted_and_typed():
    from analyze_pcb import _degenerate_drills
    fps = [{"reference": "B2", "pads": [{"type": "thru_hole", "number": "9", "drill": 0.01}]},
           {"reference": "A1", "pads": [{"type": "np_thru_hole", "number": "1", "drill": 0.02}]}]
    vias = [{"x": 1, "y": 2, "drill": 0.001}]
    assert _degenerate_drills(fps, vias) == [
        {"kind": "pad", "ref": "A1", "pad": "1", "drill_mm": 0.02},
        {"kind": "pad", "ref": "B2", "pad": "9", "drill_mm": 0.01},
        {"kind": "via", "ref": None, "pad": None, "drill_mm": 0.001, "x": 1, "y": 2},
    ]


def test_novias_board_still_reports_pad_facts():
    # Fix round 1: analyze_vias() used to early-return {} for a via-less
    # board, dropping degenerate_drills and min_pad_drill_mm entirely.
    via_analysis = _d_novias()["vias"]["via_analysis"]
    assert via_analysis.get("degenerate_drills") == [
        {"kind": "pad", "ref": "J1", "pad": "3", "drill_mm": 1e-05}
    ], via_analysis
    cc = via_analysis.get("current_capacity", {})
    assert abs(cc.get("min_pad_drill_mm", 0) - 0.18) < 1e-6, cc


def test_degenerate_via_excluded_from_current_capacity_min_and_ratings():
    # Fix round 1: current_capacity.min_drill_mm / ratings still counted
    # degenerate via drills (filter was `d > 0`, not the MIN_REAL_DRILL_MM
    # floor) -- a degenerate via showed up both in degenerate_drills AND
    # as the board's "minimum drill" with an IPC ampacity rating.
    from analyze_pcb import analyze_vias
    vias = {"vias": [
        {"type": "through", "size": 0.6, "drill": 0.3, "x": 1, "y": 1, "net": 1},
        {"type": "through", "size": 0.1, "drill": 0.001, "x": 2, "y": 2, "net": 1},
    ]}
    result = analyze_vias(vias, [], {1: "GND"})
    cc = result.get("current_capacity", {})
    assert cc.get("min_drill_mm") == 0.3, cc
    assert "0.001" not in cc.get("drill_size_distribution", {}), cc
    assert all(abs(r["drill_mm"] - 0.001) > 1e-9 for r in cc.get("ratings", [])), cc
    assert result.get("degenerate_drills") == [
        {"kind": "via", "ref": None, "pad": None, "drill_mm": 0.001, "x": 2, "y": 2}
    ], result


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
        except (AssertionError, ImportError, KeyError) as e:
            failed += 1
            print(f"  FAIL: {name}: {e!r}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
