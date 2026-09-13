"""KH-398 + KH-399 — thermal package_table assessment confidence; EMC circle-edge distance

KH-398: In analyze_thermal.py, TH-DET assessments with rtheta_ja_source=="package_table"
should have confidence=="heuristic" (not "deterministic"), matching the finding-level
helper in KH-387. The assessment carries the measurement confidence field, so it must
agree with the sibling finding confidence.

KH-399: In emc_rules.py, _point_to_edges_min_distance() has no 'circle' branch, so
circle outline edges (from KiCad 10+ board_outline) fall to the generic segment branch
and try to read a nonexistent 'start' key. Add proper point-to-circle distance using
'center' and 'end' (where end defines the radius).
"""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from analyze_thermal import _thermal_confidence, _compute_junction_temps  # noqa: E402
import emc_rules  # noqa: E402


# ---------------------------------------------------------------------------
# KH-398: Thermal package_table assessment confidence
# ---------------------------------------------------------------------------

def test_thermal_package_table_assessment_confidence():
    """package_table rtheta_ja_source must yield 'heuristic' confidence in assessments."""
    assessment = {
        "rtheta_ja_source": "package_table",
        "tj_max_source": "datasheet"
    }
    # Currently fails: _thermal_confidence returns "deterministic" for package_table
    assert _thermal_confidence(assessment) == "heuristic", \
        f"Expected 'heuristic', got {_thermal_confidence(assessment)}"


def test_thermal_default_rtheta_stays_heuristic():
    """Regression guard: 'default' rtheta_ja_source remains heuristic."""
    assessment = {
        "rtheta_ja_source": "default",
        "tj_max_source": "datasheet"
    }
    assert _thermal_confidence(assessment) == "heuristic"


def test_thermal_datasheet_rtheta_can_be_datasheet_backed():
    """Regression guard: datasheet rtheta_ja with datasheet tj_max is datasheet-backed."""
    assessment = {
        "rtheta_ja_source": "datasheet",
        "tj_max_source": "datasheet"
    }
    assert _thermal_confidence(assessment) == "datasheet-backed"


# ---------------------------------------------------------------------------
# KH-399: EMC circle-edge distance
# ---------------------------------------------------------------------------

def test_circle_edge_distance_inside():
    """Point inside circle (but outside radius) distance to circle edge."""
    edges = [{"type": "circle", "center": [10, 10], "end": [20, 10]}]
    # Center at [10, 10], radius = distance from [10,10] to [20,10] = 10
    # Point at [15, 10] is 5 units from center, so 5 units inside circle edge
    d = emc_rules._point_to_edges_min_distance(15, 10, edges)
    assert d == 5.0, f"Expected 5.0, got {d}"


def test_circle_edge_distance_outside():
    """Point outside circle distance to circle edge."""
    edges = [{"type": "circle", "center": [10, 10], "end": [20, 10]}]
    # Radius = 10, point at [30, 10] is 20 units from center
    # Distance to edge = 20 - 10 = 10
    d = emc_rules._point_to_edges_min_distance(30, 10, edges)
    assert d == 10.0, f"Expected 10.0, got {d}"


def test_circle_edge_distance_on_edge():
    """Point on circle edge distance should be ~0."""
    edges = [{"type": "circle", "center": [10, 10], "end": [20, 10]}]
    # Radius = 10, point at [20, 10] is on the edge
    d = emc_rules._point_to_edges_min_distance(20, 10, edges)
    assert abs(d) < 0.01, f"Expected ~0, got {d}"


def test_circle_edge_with_other_edges():
    """Circle edge mixed with line edges — min distance applies."""
    edges = [
        {"type": "circle", "center": [10, 10], "end": [20, 10]},
        {"type": "line", "start": [0, 0], "end": [0, 10]}
    ]
    # Point at [2, 5]: distance to line [0,0]-[0,10] is 2
    # Distance to circle at [10, 10] with r=10: distance from [2,5] to center is sqrt(64+25)=sqrt(89)≈9.43
    # Distance to edge = 10 - 9.43 ≈ 0.566
    # Minimum is the circle distance ≈ 0.566
    d = emc_rules._point_to_edges_min_distance(2, 5, edges)
    assert abs(d - 0.566) < 0.01, f"Expected ~0.566, got {d}"


# ---------------------------------------------------------------------------
# KH-398 End-to-End: Thermal assessment confidence via analyze_thermal.py
# ---------------------------------------------------------------------------

def _build_minimal_schematic_with_power_ic():
    """Build minimal schematic JSON with a power IC (footprint: SOT-223-3).

    The SOT-223 footprint is common and matches package_table regex in
    PACKAGE_THERMAL_RESISTANCE, so rtheta_ja_source will be "package_table".
    """
    return {
        "version": 20231211,
        "kind": "schematic",
        "metadata": {
            "title": "KH-398 Test",
            "date": "2026-09-13",
            "rev": "A"
        },
        "title_block": {
            "title": "KH-398 Thermal Test",
            "date": "2026-09-13",
            "rev": "A",
            "company": "test"
        },
        "sheets": [
            {
                "uuid": "00000000-0000-0000-0000-000000000001",
                "name": "/",
                "instances": {}
            }
        ],
        "symbols": [
            {
                "uuid": "00000000-0000-0000-0000-000000000101",
                "lib_id": "Regulator_Linear:LM1117-3.3",
                "at": [100, 100],
                "unit": 1
            }
        ],
        "components": [
            {
                "reference": "U1",
                "value": "LM1117-3.3",
                "footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                "type": "linear_regulator",
                "lib_id": "Regulator_Linear:LM1117-3.3",
                "dnp": False,
                "in_bom": True,
                "uuid": "00000000-0000-0000-0000-000000000101",
                "x": 100.0,
                "y": 100.0,
                "pdiss_w": 0.5,
                "pdiss_source": "schematic",
                "pdiss_confidence": "heuristic"
            }
        ],
        "nets": [
            {"uuid": "00000000-0000-0000-0000-000000010001", "name": "GND", "pins": []},
            {"uuid": "00000000-0000-0000-0000-000000010002", "name": "+5V", "pins": []},
            {"uuid": "00000000-0000-0000-0000-000000010003", "name": "+3.3V", "pins": []}
        ],
        "power_supplies": {
            "+5V": {"nominal_v": 5.0, "tolerance": 0.05, "confidence": "schematic"},
            "+3.3V": {"nominal_v": 3.3, "tolerance": 0.05, "confidence": "schematic"}
        }
    }


def _build_minimal_pcb_for_thermal():
    """Build minimal PCB JSON matching the schematic."""
    return {
        "version": 20240000,
        "kind": "pcb",
        "footprints": [
            {
                "reference": "U1",
                "footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                "value": "LM1117-3.3",
                "mpn": "",
                "at": [100.0, 100.0],
                "layer": "F.Cu",
                "uuid": "00000000-0000-0000-0000-000000000101"
            }
        ],
        "tracks": {"segments": []},
        "zones": [],
        "board_outline": {"edges": []},
        "net_map": {}
    }


def test_thermal_package_table_assessment_end_to_end():
    """Test _compute_junction_temps directly: package_table assessments have heuristic confidence.

    This test directly calls _compute_junction_temps (the function that creates assessment
    objects on line 444 of analyze_thermal.py) with mock power component data, and verifies
    that the assessment's confidence field is correctly set to "heuristic" when the
    rtheta_ja_source is "package_table".
    """
    # Mock power components that would result from power dissipation estimation
    power_comps = [
        {
            "ref": "U1",
            "value": "LM1117-3.3",
            "type": "linear_regulator",
            "pdiss_w": 0.5,
            "pdiss_source": "estimation",
            "pdiss_confidence": "heuristic"
        },
        {
            "ref": "U2",
            "value": "LM7805",
            "type": "linear_regulator",
            "pdiss_w": 1.0,
            "pdiss_source": "estimation",
            "pdiss_confidence": "heuristic"
        }
    ]

    # Mock PCB with footprints that will map to our components
    # _classify_package reads the "library" field (the footprint library name)
    # and returns a package name if it matches PACKAGE_THERMAL_RESISTANCE regex
    # For SOT-223 and TO-220, the footprint library name should match package_table patterns
    pcb = {
        "footprints": [
            {
                "reference": "U1",
                "footprint": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                "library": "Package_TO_SOT_SMD:SOT-223",  # This will be matched by _classify_package
                "value": "LM1117-3.3",
                "mpn": "",
                "at": [100.0, 100.0],
                "layer": "F.Cu",
                "uuid": "00000000-0000-0000-0000-000000000101"
            },
            {
                "reference": "U2",
                "footprint": "Package_TO_SMD:TO-220-3_Vertical",
                "library": "Package_TO_SMD:TO-220",  # This will be matched by _classify_package
                "value": "LM7805",
                "mpn": "",
                "at": [150.0, 100.0],
                "layer": "F.Cu",
                "uuid": "00000000-0000-0000-0000-000000000102"
            }
        ],
        "outline": []
    }

    # Call _compute_junction_temps directly
    # It requires: power_comps, pcb, extract_dir (path to datasheets), ambient_c
    # Pass extract_dir="" to skip datasheet lookup (we just want to test the assessment creation)
    assessments = _compute_junction_temps(
        power_comps=power_comps,
        pcb=pcb,
        extract_dir="",  # No datasheets dir; use defaults for Tj_max
        ambient_c=25.0   # 25°C ambient
    )

    # Verify assessments were created
    assert len(assessments) > 0, "Expected at least one assessment"

    # Find assessments with package_table source
    package_table_assessments = [
        a for a in assessments
        if a.get("rtheta_ja_source") == "package_table"
    ]

    # Verify at least one package_table assessment exists (fixture sanity)
    assert len(package_table_assessments) > 0, \
        f"Expected at least one package_table assessment. Got rtheta sources: {[a.get('rtheta_ja_source') for a in assessments]}"

    # Check all package_table assessments have heuristic confidence
    for a in package_table_assessments:
        confidence = a.get("confidence")
        ref = a.get("ref", "?")
        assert confidence == "heuristic", \
            f"Assessment {ref}: package_table rtheta must have heuristic confidence, got {confidence}"

    # Regression: check default assessments (if any) are also heuristic
    default_assessments = [
        a for a in assessments
        if a.get("rtheta_ja_source") == "default"
    ]
    for a in default_assessments:
        confidence = a.get("confidence")
        ref = a.get("ref", "?")
        assert confidence == "heuristic", \
            f"Assessment {ref}: default rtheta must have heuristic confidence, got {confidence}"


if __name__ == "__main__":
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
