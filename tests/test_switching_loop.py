"""Unit tests for switching loop area computation and EMC SW-003 integration.

Tests:
  - _compute_switching_loop_areas triangle area calculation
  - Topology filtering (non-switching topologies produce empty results)
  - Missing/incomplete data handling
  - EMC SW-003 pre-computed path (findings for large loops, none for small)
  - EMC SW-003 fallback path (without pre-computed data)
  - End-to-end via corpus output scan (skips gracefully if unavailable)
"""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from analyze_pcb import _compute_switching_loop_areas
from emc_rules import check_input_cap_loop_area

_RESULTS = _HARNESS / "results" / "outputs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_footprints(*refs_and_positions):
    """Build synthetic footprint list from (ref, x, y) tuples."""
    return [{"reference": ref, "x": x, "y": y, "pads": []}
            for ref, x, y in refs_and_positions]


def _make_schematic(regulators):
    """Build minimal schematic_data dict."""
    return {"signal_analysis": {"power_regulators": regulators}}


def _make_regulator(ref="U1", topology="switching", inductor="L1",
                    input_caps=None, value="TPS54331"):
    """Build a single regulator dict matching schematic output format."""
    if input_caps is None:
        input_caps = [{"ref": "C1"}]
    return {
        "ref": ref,
        "topology": topology,
        "inductor": inductor,
        "input_capacitors": input_caps,
        "value": value,
    }


# ---------------------------------------------------------------------------
# 2a. Loop area computation
# ---------------------------------------------------------------------------

def test_triangle_area_basic():
    """Triangle (0,0)-(10,0)-(0,10) should give area = 50.0 mm^2."""
    # Place cap at (10,0), IC at (0,0), inductor at (0,10) — but note
    # the function skips positions at (0,0).  Use offset positions instead.
    # Triangle at (1,1), (11,1), (1,11): area = 0.5 * |10*10| = 50.0
    footprints = _make_footprints(
        ("U1", 1.0, 1.0),
        ("L1", 1.0, 11.0),
        ("C1", 11.0, 1.0),
    )
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    loop = results[0]
    assert loop["area_mm2"] == 50.0, f"Expected 50.0, got {loop['area_mm2']}"
    assert loop["regulator_ref"] == "U1"
    assert loop["inductor_ref"] == "L1"
    assert loop["cap_ref"] == "C1"
    print("  PASS  test_triangle_area_basic")


def test_returned_structure():
    """Verify all expected keys exist in result dict."""
    footprints = _make_footprints(
        ("U1", 5.0, 5.0),
        ("L1", 15.0, 5.0),
        ("C1", 10.0, 15.0),
    )
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert len(results) == 1
    loop = results[0]
    expected_keys = {"regulator_ref", "regulator_value", "inductor_ref",
                     "cap_ref", "area_mm2", "vertices_mm"}
    assert expected_keys == set(loop.keys()), f"Keys mismatch: {set(loop.keys())}"
    # vertices_mm should be a list of 3 [x, y] pairs
    assert len(loop["vertices_mm"]) == 3
    for v in loop["vertices_mm"]:
        assert len(v) == 2 and isinstance(v[0], float)
    print("  PASS  test_returned_structure")


# ---------------------------------------------------------------------------
# 2b. Topology filtering
# ---------------------------------------------------------------------------

def test_non_switching_topologies_filtered():
    """LDO, linear, load_switch, charge_pump should all return empty."""
    footprints = _make_footprints(
        ("U1", 5.0, 5.0),
        ("L1", 15.0, 5.0),
        ("C1", 10.0, 15.0),
    )
    for topo in ("ldo", "linear", "load_switch", "charge_pump",
                 "unknown", "ic_with_internal_regulator"):
        schematic = _make_schematic([_make_regulator(topology=topo)])
        results = _compute_switching_loop_areas(footprints, schematic)
        assert results == [], f"Topology '{topo}' should be filtered, got {results}"
    print("  PASS  test_non_switching_topologies_filtered")


def test_switching_topology_produces_results():
    """'switching' and 'buck' topologies should produce results."""
    footprints = _make_footprints(
        ("U1", 5.0, 5.0),
        ("L1", 15.0, 5.0),
        ("C1", 10.0, 15.0),
    )
    for topo in ("switching", "buck", "boost", "buck-boost"):
        schematic = _make_schematic([_make_regulator(topology=topo)])
        results = _compute_switching_loop_areas(footprints, schematic)
        assert len(results) == 1, f"Topology '{topo}' should produce result, got {len(results)}"
    print("  PASS  test_switching_topology_produces_results")


# ---------------------------------------------------------------------------
# 2c. Missing data handling
# ---------------------------------------------------------------------------

def test_no_schematic_data():
    """Empty schematic_data → empty result."""
    footprints = _make_footprints(("U1", 5.0, 5.0))
    assert _compute_switching_loop_areas(footprints, {}) == []
    assert _compute_switching_loop_areas(footprints, {"signal_analysis": {}}) == []
    print("  PASS  test_no_schematic_data")


def test_no_regulators():
    """No power_regulators key → empty result."""
    footprints = _make_footprints(("U1", 5.0, 5.0))
    schematic = _make_schematic([])
    assert _compute_switching_loop_areas(footprints, schematic) == []
    print("  PASS  test_no_regulators")


def test_inductor_ref_missing_from_footprints():
    """Inductor ref not in footprint list → skip that regulator."""
    footprints = _make_footprints(
        ("U1", 5.0, 5.0),
        ("C1", 10.0, 15.0),
        # L1 missing from footprints
    )
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert results == [], f"Expected empty, got {results}"
    print("  PASS  test_inductor_ref_missing_from_footprints")


def test_empty_input_caps():
    """No input_capacitors → skip."""
    footprints = _make_footprints(
        ("U1", 5.0, 5.0),
        ("L1", 15.0, 5.0),
        ("C1", 10.0, 15.0),
    )
    schematic = _make_schematic([_make_regulator(input_caps=[])])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert results == [], f"Expected empty, got {results}"
    print("  PASS  test_empty_input_caps")


# ---------------------------------------------------------------------------
# 2d. EMC SW-003 pre-computed path
# ---------------------------------------------------------------------------

def test_sw003_precomputed_large_loop():
    """Pre-computed loop area > 25 mm^2 should produce a SW-003 finding."""
    pcb = {
        "switching_loop_areas": [{
            "regulator_ref": "U1",
            "regulator_value": "TPS54331",
            "inductor_ref": "L1",
            "cap_ref": "C1",
            "area_mm2": 150.0,
            "vertices_mm": [[10, 0], [0, 0], [0, 10]],
        }],
        "footprints": [],
    }
    schematic = _make_schematic([_make_regulator()])
    findings = check_input_cap_loop_area(pcb, schematic)
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    f = findings[0]
    assert f["rule_id"] == "SW-003"
    assert f["severity"] == "HIGH"  # > 100 mm^2
    assert "U1" in f["components"]
    assert "150" in f["description"]
    print("  PASS  test_sw003_precomputed_large_loop")


def test_sw003_precomputed_small_loop():
    """Pre-computed loop area < 25 mm^2 should produce no findings."""
    pcb = {
        "switching_loop_areas": [{
            "regulator_ref": "U1",
            "regulator_value": "TPS54331",
            "inductor_ref": "L1",
            "cap_ref": "C1",
            "area_mm2": 15.0,
            "vertices_mm": [[1, 1], [4, 1], [1, 4]],
        }],
        "footprints": [],
    }
    schematic = _make_schematic([_make_regulator()])
    findings = check_input_cap_loop_area(pcb, schematic)
    assert len(findings) == 0, f"Expected 0 findings, got {len(findings)}"
    print("  PASS  test_sw003_precomputed_small_loop")


# ---------------------------------------------------------------------------
# 2e. EMC SW-003 fallback (no pre-computed data)
# ---------------------------------------------------------------------------

def test_sw003_fallback_no_precomputed():
    """Without switching_loop_areas, function falls back to footprint positions."""
    pcb = {
        "footprints": _make_footprints(
            ("U1", 5.0, 5.0),
            ("L1", 30.0, 5.0),
            ("C1", 5.0, 30.0),
        ),
    }
    schematic = _make_schematic([_make_regulator()])
    # Triangle (5,5)-(30,5)-(5,30): area = 0.5 * 25 * 25 = 312.5 mm^2
    # That's > 25 so should trigger a finding
    findings = check_input_cap_loop_area(pcb, schematic)
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    assert findings[0]["rule_id"] == "SW-003"
    assert findings[0]["severity"] == "HIGH"  # > 100 mm^2
    print("  PASS  test_sw003_fallback_no_precomputed")


# ---------------------------------------------------------------------------
# 2f. End-to-end (corpus scan)
# ---------------------------------------------------------------------------

def test_end_to_end_corpus_output():
    """Find a real corpus PCB output with switching_loop_areas and validate it."""
    pcb_dir = _RESULTS / "pcb"
    if not pcb_dir.exists():
        print("  SKIP  test_end_to_end_corpus_output (no pcb outputs dir)")
        return

    found = None
    scanned = 0
    for owner in sorted(pcb_dir.iterdir()):
        if not owner.is_dir():
            continue
        for repo in sorted(owner.iterdir()):
            if not repo.is_dir():
                continue
            for jf in sorted(repo.glob("*.json")):
                try:
                    data = json.loads(jf.read_text(encoding="utf-8"))
                    if data.get("switching_loop_areas"):
                        found = (data, str(jf))
                        break
                except Exception:
                    pass
                scanned += 1
                if scanned >= 10000:
                    break
            if found:
                break
        if found:
            break

    if not found:
        print("  SKIP  test_end_to_end_corpus_output (no output with switching_loop_areas found)")
        return

    data, path = found
    loops = data["switching_loop_areas"]
    assert isinstance(loops, list) and len(loops) > 0
    for loop in loops:
        assert "regulator_ref" in loop
        assert "inductor_ref" in loop
        assert "cap_ref" in loop
        assert "area_mm2" in loop
        assert isinstance(loop["area_mm2"], (int, float))
        assert loop["area_mm2"] > 0
        assert "vertices_mm" in loop
        assert len(loop["vertices_mm"]) == 3
    print(f"  PASS  test_end_to_end_corpus_output ({path}, {len(loops)} loops)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # 2a. Loop area computation
    test_triangle_area_basic,
    test_returned_structure,
    # 2b. Topology filtering
    test_non_switching_topologies_filtered,
    test_switching_topology_produces_results,
    # 2c. Missing data handling
    test_no_schematic_data,
    test_no_regulators,
    test_inductor_ref_missing_from_footprints,
    test_empty_input_caps,
    # 2d. EMC SW-003 pre-computed path
    test_sw003_precomputed_large_loop,
    test_sw003_precomputed_small_loop,
    # 2e. EMC SW-003 fallback
    test_sw003_fallback_no_precomputed,
    # 2f. End-to-end
    test_end_to_end_corpus_output,
]


def main():
    passed = failed = 0
    for t in ALL_TESTS:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    total = passed + failed
    print(f"\n{passed}/{total} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
