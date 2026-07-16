#!/usr/bin/env python3
"""Regression test: XV-002 should not fire when PCB 'value' is just the footprint name.

Adopted from anyasabo/kicad-happy @ 0a2b1c7 (ported 2026-07-15).
"""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from cross_analysis import check_cross_validation


def make_schematic(components):
    return {"components": components}


def make_pcb(footprints):
    return {"footprints": footprints}


def test_no_false_positive_when_pcb_value_equals_footprint():
    """PCB value == footprint name means value was never synced — skip XV-002."""
    sch = make_schematic([
        {"reference": "C1", "value": "10uF"},
        {"reference": "R1", "value": "5.1k"},
        {"reference": "U1", "value": "TLV73333PDBVR"},
    ])
    pcb = make_pcb([
        {"reference": "C1", "value": "C_0603_1608Metric", "footprint": "C_0603_1608Metric"},
        {"reference": "R1", "value": "R_0603_1608Metric", "footprint": "R_0603_1608Metric"},
        {"reference": "U1", "value": "SOT-23-5", "footprint": "SOT-23-5"},
    ])
    findings = check_cross_validation(sch, pcb)
    xv002 = [f for f in findings if f.get("rule_id") == "XV-002"]
    assert not xv002, f"Expected no XV-002 findings, got: {[f['summary'] for f in xv002]}"


def test_no_false_positive_when_pcb_value_matches_lib_suffix():
    """PCB footprint may include library prefix (e.g. 'Lib:Name') — still skip."""
    sch = make_schematic([
        {"reference": "J1", "value": "USB4105-GF-A"},
    ])
    pcb = make_pcb([
        {"reference": "J1", "value": "GCT_USB4105-GF-A", "footprint": "library:GCT_USB4105-GF-A"},
    ])
    findings = check_cross_validation(sch, pcb)
    xv002 = [f for f in findings if f.get("rule_id") == "XV-002"]
    assert not xv002, f"Expected no XV-002 findings, got: {[f['summary'] for f in xv002]}"


def test_real_mismatch_still_detected():
    """A genuine value mismatch (PCB value differs from both schematic and footprint) fires."""
    sch = make_schematic([
        {"reference": "C1", "value": "10uF"},
    ])
    pcb = make_pcb([
        {"reference": "C1", "value": "100nF", "footprint": "C_0603_1608Metric"},
    ])
    findings = check_cross_validation(sch, pcb)
    xv002 = [f for f in findings if f.get("rule_id") == "XV-002"]
    assert len(xv002) == 1, f"Expected 1 XV-002 finding, got {len(xv002)}"


def test_whitespace_normalization_still_works():
    """Whitespace-only differences are still suppressed."""
    sch = make_schematic([
        {"reference": "R1", "value": "5.1 k"},
    ])
    pcb = make_pcb([
        {"reference": "R1", "value": "5.1k", "footprint": "R_0603_1608Metric"},
    ])
    findings = check_cross_validation(sch, pcb)
    xv002 = [f for f in findings if f.get("rule_id") == "XV-002"]
    assert not xv002, f"Expected no XV-002 findings, got: {[f['summary'] for f in xv002]}"


if __name__ == "__main__":
    test_no_false_positive_when_pcb_value_equals_footprint()
    test_no_false_positive_when_pcb_value_matches_lib_suffix()
    test_real_mismatch_still_detected()
    test_whitespace_normalization_still_works()
    print("All XV-002 tests passed.")
