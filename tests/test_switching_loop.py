"""Unit tests for switching loop area computation and EMC SW-003 integration.

Tests:
  - _compute_switching_loop_areas pad-to-pad loop area (method "pad")
  - Topology filtering (non-switching topologies produce empty results)
  - Missing/incomplete data handling
  - EMC SW-003 pre-computed path (pad loops graded, other records not)
  - EMC SW-003 fallback path (centre triangle: info estimate, not graded)
  - End-to-end via corpus output scan (skips gracefully if unavailable)
"""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

import pytest
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = str(PRODUCT_ROOT)
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from pcb.assembly import _compute_switching_loop_areas
from emc_rules import check_input_cap_loop_area

_RESULTS = _HARNESS / "results" / "outputs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_footprints(*refs_and_positions):
    """Build synthetic footprint list from (ref, x, y) tuples (no pads)."""
    return [{"reference": ref, "x": x, "y": y, "pads": []}
            for ref, x, y in refs_and_positions]


def _pad(number, net, x, y):
    return {"number": number, "net_name": net, "abs_x": x, "abs_y": y}


def _buck_footprints(cap_vin, reg_vin, reg_sw, ind_sw, reg_gnd, cap_gnd):
    """Input cap C1 (VIN/GND), regulator U1 (VIN/SW/GND) and inductor L1 (SW/VOUT),
    with the six hot-loop pads at the given (x, y) positions."""
    return [
        {"reference": "C1", "x": cap_vin[0], "y": (cap_vin[1] + cap_gnd[1]) / 2,
         "pads": [_pad("1", "VIN", *cap_vin), _pad("2", "GND", *cap_gnd)]},
        {"reference": "U1", "x": reg_sw[0], "y": reg_sw[1],
         "pads": [_pad("1", "VIN", *reg_vin), _pad("2", "SW", *reg_sw), _pad("3", "GND", *reg_gnd)]},
        {"reference": "L1", "x": ind_sw[0], "y": ind_sw[1] + 2.0,
         "pads": [_pad("1", "SW", *ind_sw), _pad("2", "VOUT", ind_sw[0], ind_sw[1] + 4.0)]},
    ]


def _make_regulator(ref="U1", topology="switching", inductor="L1",
                    input_caps=None, value="TPS54331"):
    """Build a single regulator finding matching schematic findings[] format."""
    if input_caps is None:
        input_caps = [{"ref": "C1"}]
    return {
        "detector": "detect_power_regulators",
        "ref": ref,
        "topology": topology,
        "inductor": inductor,
        "input_capacitors": input_caps,
        "value": value,
        "rule_id": "PR-DET", "severity": "info", "confidence": "deterministic",
        "evidence_source": "topology", "summary": "", "description": "",
        "components": [ref], "nets": [], "pins": [],
        "recommendation": "", "report_context": {},
    }


def _make_schematic(regulators):
    """Build minimal schematic_data dict with findings[] format."""
    return {"findings": regulators}


# ---------------------------------------------------------------------------
# 2a. Loop area computation (pad to pad)
# ---------------------------------------------------------------------------

def test_pad_loop_area_basic():
    """Six hot-loop pads on a 10 x 10 mm square give a 100.0 mm^2 pad loop."""
    footprints = _buck_footprints(
        cap_vin=(1.0, 11.0), reg_vin=(6.0, 11.0), reg_sw=(11.0, 11.0),
        ind_sw=(11.0, 1.0), reg_gnd=(6.0, 1.0), cap_gnd=(1.0, 1.0))
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    loop = results[0]
    assert loop["method"] == "pad"
    assert loop["area_mm2"] == 100.0, f"Expected 100.0, got {loop['area_mm2']}"
    assert loop["regulator_ref"] == "U1"
    assert loop["inductor_ref"] == "L1"
    assert loop["cap_ref"] == "C1"
    assert "estimate" not in loop
    print("  PASS  test_pad_loop_area_basic")


def test_returned_structure():
    """A resolved pad loop names its six pads in loop order and their positions."""
    footprints = _buck_footprints(
        cap_vin=(1.0, 11.0), reg_vin=(6.0, 11.0), reg_sw=(11.0, 11.0),
        ind_sw=(11.0, 1.0), reg_gnd=(6.0, 1.0), cap_gnd=(1.0, 1.0))
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert len(results) == 1
    loop = results[0]
    expected_keys = {"regulator_ref", "regulator_value", "inductor_ref", "cap_ref",
                     "method", "area_mm2", "loop_pads", "vertices_mm"}
    assert expected_keys == set(loop.keys()), f"Keys mismatch: {set(loop.keys())}"
    assert loop["loop_pads"] == ["C1.1", "U1.1", "U1.2", "L1.1", "U1.3", "C1.2"]
    assert loop["vertices_mm"] == [[1.0, 11.0], [6.0, 11.0], [11.0, 11.0],
                                   [11.0, 1.0], [6.0, 1.0], [1.0, 1.0]]
    print("  PASS  test_returned_structure")


def test_collinear_pads_degenerate():
    """GitHub #62: hot-loop pads in a line give no area, not 0 mm^2."""
    footprints = _buck_footprints(
        cap_vin=(1.0, 5.0), reg_vin=(3.0, 5.0), reg_sw=(5.0, 5.0),
        ind_sw=(7.0, 5.0), reg_gnd=(9.0, 5.0), cap_gnd=(11.0, 5.0))
    schematic = _make_schematic([_make_regulator()])
    results = _compute_switching_loop_areas(footprints, schematic)
    assert len(results) == 1
    assert results[0]["method"] == "pad"
    assert results[0]["area_mm2"] is None
    assert results[0]["estimate"] == "degenerate"
    assert len(results[0]["vertices_mm"]) == 6
    print("  PASS  test_collinear_pads_degenerate")


def test_pads_without_nets_unresolved():
    """Footprints whose pads carry no nets give a pad record with no area."""
    footprints = _make_footprints(("U1", 5.0, 5.0), ("L1", 15.0, 5.0), ("C1", 10.0, 15.0))
    results = _compute_switching_loop_areas(footprints, _make_schematic([_make_regulator()]))
    assert len(results) == 1
    assert results[0]["method"] == "pad"
    assert results[0]["area_mm2"] is None
    assert results[0]["estimate"] == "pads_unresolved"
    assert "vertices_mm" not in results[0]
    print("  PASS  test_pads_without_nets_unresolved")


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
    assert _compute_switching_loop_areas(footprints, {"findings": []}) == []
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
    """A pad loop over 100 mm^2 is graded: one SW-003 error."""
    pcb = {
        "switching_loop_areas": [{
            "regulator_ref": "U1",
            "regulator_value": "TPS54331",
            "inductor_ref": "L1",
            "cap_ref": "C1",
            "method": "pad",
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
    assert f["severity"] == "error"  # > 100 mm^2 (normalized from "HIGH" per 4ab788e)
    assert "U1" in f["components"]
    assert "150" in f["description"]
    print("  PASS  test_sw003_precomputed_large_loop")


def test_sw003_precomputed_without_method_not_graded():
    """A loop record without method "pad" holds the centre triangle: one info, not graded."""
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
    findings = check_input_cap_loop_area(pcb, _make_schematic([_make_regulator()]))
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    assert findings[0]["rule_id"] == "SW-003"
    assert findings[0]["severity"] == "info"
    assert findings[0]["summary"] == "Hot loop for U1 not graded: estimated from part centres"
    print("  PASS  test_sw003_precomputed_without_method_not_graded")


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


def test_sw003_precomputed_degenerate_not_estimated():
    """A degenerate pre-computed loop gives one SW-003 info 'not estimated', not a pass."""
    pcb = {
        "switching_loop_areas": [{
            "regulator_ref": "U1",
            "regulator_value": "TPS54331",
            "inductor_ref": "L1",
            "cap_ref": "C1",
            "area_mm2": None,
            "estimate": "degenerate",
            "vertices_mm": [[5, 5], [15, 5], [25, 5]],
        }],
        "footprints": [],
    }
    schematic = _make_schematic([_make_regulator()])
    findings = check_input_cap_loop_area(pcb, schematic)
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    assert findings[0]["rule_id"] == "SW-003"
    assert findings[0]["severity"] == "info"
    assert "not estimated" in findings[0]["summary"]
    print("  PASS  test_sw003_precomputed_degenerate_not_estimated")


# ---------------------------------------------------------------------------
# 2e. EMC SW-003 fallback (no pre-computed data)
# ---------------------------------------------------------------------------

def test_sw003_fallback_no_precomputed():
    """Without switching_loop_areas the centre triangle is an info estimate, not graded."""
    pcb = {
        "footprints": _make_footprints(
            ("U1", 5.0, 5.0),
            ("L1", 30.0, 5.0),
            ("C1", 5.0, 30.0),
        ),
    }
    schematic = _make_schematic([_make_regulator()])
    # Triangle (5,5)-(30,5)-(5,30): area = 0.5 * 25 * 25 = 312.5 mm^2
    findings = check_input_cap_loop_area(pcb, schematic)
    assert len(findings) == 1, f"Expected 1 finding, got {len(findings)}"
    assert findings[0]["rule_id"] == "SW-003"
    assert findings[0]["severity"] == "info"
    assert findings[0]["summary"] == "Hot loop for U1 not graded: estimated from part centres"
    assert "312" in findings[0]["description"]
    print("  PASS  test_sw003_fallback_no_precomputed")


# ---------------------------------------------------------------------------
# 2f. End-to-end (corpus scan)
# ---------------------------------------------------------------------------

@pytest.mark.corpus
def test_end_to_end_corpus_output():
    """Find a real corpus PCB output with switching_loop_areas and validate it."""
    pcb_dir = _RESULTS / "pcb"
    if not pcb_dir.exists():
        pytest.skip("no pcb outputs dir (corpus tier)")

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
        pytest.skip("no output with switching_loop_areas found (corpus tier)")

    data, path = found
    loops = data["switching_loop_areas"]
    assert isinstance(loops, list) and len(loops) > 0
    for loop in loops:
        assert "regulator_ref" in loop
        assert "inductor_ref" in loop
        assert "cap_ref" in loop
        assert "area_mm2" in loop
        assert loop.get("method") == "pad"
        if loop["area_mm2"] is None:
            assert loop.get("estimate") in ("degenerate", "pads_unresolved")
        else:
            assert isinstance(loop["area_mm2"], (int, float))
            assert loop["area_mm2"] > 0
        if loop.get("estimate") != "pads_unresolved":
            assert len(loop["vertices_mm"]) == 6
    print(f"  PASS  test_end_to_end_corpus_output ({path}, {len(loops)} loops)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_TESTS = [
    # 2a. Loop area computation
    test_pad_loop_area_basic,
    test_returned_structure,
    test_collinear_pads_degenerate,
    test_pads_without_nets_unresolved,
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
    test_sw003_precomputed_without_method_not_graded,
    test_sw003_precomputed_small_loop,
    test_sw003_precomputed_degenerate_not_estimated,
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
        except pytest.skip.Exception as e:
            print(f"  SKIP  {t.__name__}: {e}")
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    total = passed + failed
    print(f"\n{passed}/{total} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
