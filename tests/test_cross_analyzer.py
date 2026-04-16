"""Unit tests for validate/cross_analyzer.py public functions.

Tests the three cross_validate_* functions with synthetic output dicts
covering: perfect match, acceptable mismatch (info status), hard mismatch
(mismatch status). Also tests find_paired_outputs via tmp directory.
"""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.cross_analyzer import (  # noqa: E402
    cross_validate_schematic_pcb,
    cross_validate_pcb_emc,
    cross_validate_schematic_spice,
    find_paired_outputs,
)


# ---------------------------------------------------------------------------
# cross_validate_schematic_pcb
# ---------------------------------------------------------------------------

def test_sch_pcb_component_count_match():
    sch = {"statistics": {"total_components": 50, "total_nets": 30}}
    pcb = {"statistics": {"footprint_count": 50, "net_count": 30}}
    results = cross_validate_schematic_pcb(sch, pcb)
    comp = next(r for r in results if r["check"] == "component_vs_footprint_count")
    assert comp["status"] == "match", f"Got {comp}"


def test_sch_pcb_component_count_info_when_pcb_has_fab_marks():
    """PCB 10% higher than schematic → still match (within 0.8-1.25 ratio)."""
    sch = {"statistics": {"total_components": 50, "total_nets": 30}}
    pcb = {"statistics": {"footprint_count": 55, "net_count": 30}}
    results = cross_validate_schematic_pcb(sch, pcb)
    comp = next(r for r in results if r["check"] == "component_vs_footprint_count")
    # 55/50 = 1.10 which is within 0.8-1.25 → match
    assert comp["status"] == "match"


def test_sch_pcb_component_count_mismatch_when_pcb_much_smaller():
    """PCB has half the components → mismatch."""
    sch = {"statistics": {"total_components": 50, "total_nets": 30}}
    pcb = {"statistics": {"footprint_count": 25, "net_count": 30}}
    results = cross_validate_schematic_pcb(sch, pcb)
    comp = next(r for r in results if r["check"] == "component_vs_footprint_count")
    assert comp["status"] == "mismatch"


def test_sch_pcb_net_count_mismatch_over_10pct():
    """Net count differing by >10% → mismatch."""
    sch = {"statistics": {"total_components": 50, "total_nets": 100}}
    pcb = {"statistics": {"footprint_count": 50, "net_count": 80}}
    results = cross_validate_schematic_pcb(sch, pcb)
    net = next(r for r in results if r["check"] == "net_count")
    assert net["status"] == "mismatch"


# ---------------------------------------------------------------------------
# cross_validate_pcb_emc
# ---------------------------------------------------------------------------

def test_pcb_emc_via_count_exact_match():
    pcb = {"statistics": {"via_count": 42, "copper_layers_used": 4,
                          "footprint_count": 50}}
    emc = {"board_info": {"via_count": 42, "layer_count": 4,
                          "footprint_count": 50}}
    results = cross_validate_pcb_emc(pcb, emc)
    via = next(r for r in results if r["check"] == "via_count")
    assert via["status"] == "match"


def test_pcb_emc_via_count_off_by_one_is_mismatch():
    pcb = {"statistics": {"via_count": 42}}
    emc = {"board_info": {"via_count": 43}}
    results = cross_validate_pcb_emc(pcb, emc)
    via = next(r for r in results if r["check"] == "via_count")
    assert via["status"] == "mismatch"


# ---------------------------------------------------------------------------
# cross_validate_schematic_spice
# ---------------------------------------------------------------------------

def test_spice_refs_all_present():
    sch = {"components": [{"reference": "R1"}, {"reference": "R2"}],
           "findings": []}
    spice = {"simulation_results": [{"components": ["R1", "R2"]}]}
    results = cross_validate_schematic_spice(sch, spice)
    r = next(r for r in results if r["check"] == "spice_component_refs")
    assert r["status"] == "match"


def test_spice_orphan_ref_produces_mismatch():
    sch = {"components": [{"reference": "R1"}], "findings": []}
    spice = {"simulation_results": [{"components": ["R1", "R_GHOST"]}]}
    results = cross_validate_schematic_spice(sch, spice)
    r = next(r for r in results if r["check"] == "spice_component_refs")
    assert r["status"] == "mismatch"
    assert "R_GHOST" in r["detail"]


# ---------------------------------------------------------------------------
# find_paired_outputs
# ---------------------------------------------------------------------------

def test_find_paired_outputs_empty_repo():
    """Non-existent repo returns empty list, no crash."""
    assert find_paired_outputs("nonexistent/repo") == []


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
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
    sys.exit(1 if failed else 0)
