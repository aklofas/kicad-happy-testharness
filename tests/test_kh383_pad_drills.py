"""KH-383 — footprint pad drills feed DFM min-drill, via facts, and
design-rule compliance.

`analyze_pcb.py` parses pad drills into `pad["drill"]` for thru_hole /
np_thru_hole pads, but the DFM min-drill scan, the via-facts drill
distribution, and `analyze_design_rule_compliance` only ever looked at
board vias — so a 0.2mm footprint-embedded thermal via (or any small PTH
pad) under a QFN never tripped a 0.3mm project `min_through_hole_diameter`
rule, and DFM's `metrics["min_drill_mm"]` under-reported the true smallest
drill on the board.

Now both consumers take the minimum across via drills AND thru-hole /
np_thru_hole pad drills. `analyze_design_rule_compliance` gained a
`footprints` keyword parameter; when the smallest drill comes from a pad
rather than a via, the `min_via_drill` violation's `message` names the
source (`pad drill 0.200mm on U1`) even though the `rule` field stays
`min_via_drill`.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import analyze_pcb  # noqa: E402


VIAS = [{"size": 0.6, "drill": 0.3, "x": 0, "y": 0, "type": "through"}]
U1 = {
    "reference": "U1",
    "pads": [
        {"type": "thru_hole", "drill": 0.2, "abs_x": float(i), "abs_y": 0.0}
        for i in range(12)
    ],
}
PROJECT = {"design_rules": {"min_through_hole_diameter": 0.3}}


def test_design_rule_sees_pad_drills():
    res = analyze_pcb.analyze_design_rule_compliance(
        {"segments": [], "arcs": []}, {"vias": VIAS}, PROJECT, footprints=[U1])
    v = [x for x in res["violations"] if x["rule"] == "min_via_drill"]
    assert len(v) == 1 and v[0]["actual_mm"] == 0.2
    assert "pad drill" in v[0]["message"] and "U1" in v[0]["message"]


def test_dfm_min_drill_includes_pads():
    res = analyze_pcb.analyze_dfm(
        [U1], {"segments": [], "arcs": []}, {"vias": VIAS},
        {"edges": [], "bounding_box": None})
    assert res["metrics"]["min_drill_mm"] == 0.2


def test_design_rule_compliance_unaffected_when_no_footprints():
    # Backward compatibility: footprints defaults to None (call site omits
    # it entirely), via-only behavior is unchanged.
    project = {"design_rules": {"min_through_hole_diameter": 0.35}}
    res = analyze_pcb.analyze_design_rule_compliance(
        {"segments": [], "arcs": []}, {"vias": VIAS}, project)
    v = [x for x in res["violations"] if x["rule"] == "min_via_drill"]
    assert len(v) == 1 and v[0]["actual_mm"] == 0.3
    assert "pad drill" not in v[0]["message"]


def test_via_facts_report_min_pad_drill():
    fps = [U1]
    res = analyze_pcb.analyze_vias({"vias": VIAS}, fps, {})
    assert res["current_capacity"]["min_pad_drill_mm"] == 0.2


def test_dfm_prefers_via_drill_when_smaller_than_pads():
    small_via = [{"size": 0.35, "drill": 0.1, "x": 0, "y": 0}]
    res = analyze_pcb.analyze_dfm(
        [U1], {"segments": [], "arcs": []}, {"vias": small_via},
        {"edges": [], "bounding_box": None})
    assert res["metrics"]["min_drill_mm"] == 0.1
    v = [x for x in res.get("violations", []) if x["parameter"] == "via_drill"]
    assert v and "Via drill" in v[0]["message"]


def test_dfm_ignores_smd_pad_drills():
    smd = {"reference": "R1", "pads": [{"type": "smd", "drill": 0.0}]}
    res = analyze_pcb.analyze_dfm(
        [smd], {"segments": [], "arcs": []}, {"vias": VIAS},
        {"edges": [], "bounding_box": None})
    assert res["metrics"]["min_drill_mm"] == 0.3


# --- Oval pad drills (fix round 1) --------------------------------------
#
# An oval drill stores its two dimensions separately: `drill` (first) and
# `drill_h` (second) — e.g. a mounting slot or a polarised connector hole.
# Whichever dimension is smaller is the one that actually determines the
# smallest hole a fab has to drill, regardless of which field it landed in.

def test_design_rule_oval_pad_uses_smaller_dimension():
    u2 = {"reference": "U2", "pads": [
        {"type": "thru_hole", "drill": 0.6, "drill_h": 0.25,
         "abs_x": 0.0, "abs_y": 0.0}]}
    res = analyze_pcb.analyze_design_rule_compliance(
        {"segments": [], "arcs": []}, {"vias": []}, PROJECT, footprints=[u2])
    v = [x for x in res["violations"] if x["rule"] == "min_via_drill"]
    assert len(v) == 1 and v[0]["actual_mm"] == 0.25
    assert "pad drill" in v[0]["message"] and "U2" in v[0]["message"]


def test_design_rule_oval_pad_dimension_order_independent():
    u3 = {"reference": "U3", "pads": [
        {"type": "thru_hole", "drill": 0.25, "drill_h": 0.6,
         "abs_x": 0.0, "abs_y": 0.0}]}
    res = analyze_pcb.analyze_design_rule_compliance(
        {"segments": [], "arcs": []}, {"vias": []}, PROJECT, footprints=[u3])
    v = [x for x in res["violations"] if x["rule"] == "min_via_drill"]
    assert len(v) == 1 and v[0]["actual_mm"] == 0.25
    assert "pad drill" in v[0]["message"] and "U3" in v[0]["message"]


# --- Custom .kicad_dru hole_size rule (fix round 2) ---------------------
#
# analyze_design_rule_compliance's custom-rules loop still read the old
# `min_via_drill` local for the `hole_size` constraint after KH-383 renamed
# it to `min_drill` — a NameError on any board whose .kicad_dru has an
# unconditional hole_size constraint, breaking --full runs entirely.

def test_custom_hole_size_rule_sees_pad_drills():
    project = {
        "design_rules": {},
        "custom_rules": [
            {"name": "holes", "constraints": [{"type": "hole_size", "min": 0.3}]},
        ],
    }
    res = analyze_pcb.analyze_design_rule_compliance(
        {"segments": [], "arcs": []}, {"vias": []}, project, footprints=[U1])
    v = [x for x in res["violations"] if x.get("constraint_type") == "hole_size"]
    assert len(v) == 1
    assert v[0]["rule"] == "custom:holes"
    assert v[0]["actual_mm"] == 0.2


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
