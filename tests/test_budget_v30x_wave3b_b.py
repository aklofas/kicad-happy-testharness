"""Unit tests for the product 3.0.x Wave 3b Part B budget predicates (regression/budgets/v30x_wave3b_b.py)."""
import copy
import json

import pytest

from regression.budgets import v30x_wave3b_b as w3bb
from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.field_compare import Delta

pytestmark = pytest.mark.unit

KICAD5_BOARD = """(kicad_pcb (version 20171130) (host pcbnew "(5.1.6)-1")
  (layers
    (0 Top signal)
    (31 Bottom signal)
    (32 B.Adhes user hide)
  )
  (via (at 1 1) (size 0.6) (layers Top Bottom) (net 1))
  (zone (net 1) (net_name GND) (layer Top) (min_thickness 0.254)
    (polygon (pts (xy 0 0) (xy 1 0) (xy 1 0) (xy 1 1)))
    (filled_polygon (pts (xy 0 0) (xy 1 0) (xy 1 1)))
  )
)
"""

MODERN_BOARD = """(kicad_pcb (version 20240108) (generator "pcbnew")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
  )
  (gr_poly (pts (xy 0 0) (arc (start 1 0) (mid 1.5 0.5) (end 1 1)) (xy 0 1)) (layer "F.Cu") (net 3))
  (segment (start 0 0) (end 1 0) (width 0.2) (layers "F.Cu" "F.Mask") (net 2))
  (arc (start 0 0) (mid 1 1) (end 2 0) (width 0.2) (layer "F.Cu") (net 2))
  (via (at 1 1) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net 2))
  (footprint "H" (layer "F.Cu")
    (pad "1" smd custom (at 0 0) (size 1 1) (layers "F.Cu") (net 2 "A") (primitives (gr_circle (center 0 0) (end 1 0))))
    (pad "" np_thru_hole circle (at 0 0) (size 3 3) (drill 2) (layers "*.Cu" "*.Mask") (net 1 "GND"))
  )
)
"""


def _d(analyzer, path="/findings/0", op="added"):
    return Delta(unit="u", analyzer=analyzer, path=path, op=op, before=None, after=None)


def _finding(rule_id, **kw):
    f = {"detector": "d", "rule_id": rule_id, "category": "c", "summary": "s", "description": "",
         "components": [], "nets": [], "pins": [], "severity": "warning", "confidence": "heuristic",
         "evidence_source": "topology", "recommendation": "", "report_context": {},
         "finding_id": f"x:{rule_id}:1"}
    f.update(kw)
    return f


def _doc(findings, **extra):
    doc = dict(extra)
    doc["findings"] = findings
    doc["summary"] = expected_summary(findings, {})
    doc["trust_summary"] = expected_trust_summary(
        findings, {"by_confidence": {"deterministic": 0, "heuristic": 0},
                   "by_evidence_source": {"topology": 0}})
    doc["audience_summary"] = expected_audience_summary(findings)
    return doc


def _board(tmp_path, text, name="b.kicad_pcb"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return {"source_files": [str(p)]}


def _pcb(tmp_path, text, findings=(), **extra):
    return _doc(list(findings), analyzer_type="pcb", inputs=_board(tmp_path, text), **extra)


def test_scan_kicad5_board():
    c = w3bb.scan_board(KICAD5_BOARD)
    assert c["P1"] == 2 and c["P1h"] == 1
    assert c["P7"] == 1 and c["P8"] == 1  # a KiCad 5 via has no drill of its own
    assert c["P6"] == 1 and c["P2d"] == 1
    assert "P2" not in c


def test_scan_modern_board():
    c = w3bb.scan_board(MODERN_BOARD)
    assert c["P2"] == 1 and c["P3"] == 1 and c["P4"] == 1 and c["P9"] == 1
    assert c["P5"] == 1 and c["P10"] == 1 and c["P7"] == 1
    assert not {"P1", "P1h", "P6", "P8"} & set(c)


def test_schematic_instance_path_only_is_x1():
    a = _doc([], analyzer_type="schematic", components=[{"reference": "R1", "value": "1k"}])
    b = copy.deepcopy(a)
    b["components"][0]["instance_path"] = "/u1/u2"
    assert w3bb.classify_unit("schematic", a, b)["label"] == "X1"


def test_schematic_movement_beside_instance_path_is_a_residual():
    a = _doc([], analyzer_type="schematic", components=[{"reference": "R1", "value": "1k"}])
    b = copy.deepcopy(a)
    b["components"][0]["instance_path"] = "/u1/u2"
    b["components"][0]["value"] = "2k"
    r = w3bb.classify_unit("schematic", a, b)
    assert r["label"] is None and "block components" in r["reasons"]


def test_pcb_layer_rename_opens_any_rule(tmp_path):
    a = _pcb(tmp_path, KICAD5_BOARD, layers=[{"name": "Top", "type": "signal"}])
    b = _pcb(tmp_path, KICAD5_BOARD, [_finding("TV-001")], layers=[{"name": "F.Cu", "type": "signal"}])
    assert w3bb.classify_unit("pcb", a, b)["label"].startswith("P1")


def test_pcb_rule_outside_the_board_constructs_is_a_residual(tmp_path):
    a = _pcb(tmp_path, MODERN_BOARD)
    b = _pcb(tmp_path, MODERN_BOARD, [_finding("CC-002")])
    r = w3bb.classify_unit("pcb", a, b)
    assert r["label"] is None and any("CC-002" in x for x in r["reasons"])


def test_pcb_block_outside_the_board_constructs_is_a_residual(tmp_path):
    board = '(kicad_pcb (version 20240108)\n  (layers (0 "F.Cu" signal))\n)\n'
    a = _pcb(tmp_path, board, zones=[{"filled_area_mm2": 1.0}])
    b = _pcb(tmp_path, board, zones=[{"filled_area_mm2": 2.0}])
    r = w3bb.classify_unit("pcb", a, b)
    assert r["label"] is None and "block zones" in r["reasons"]


def test_pcb_via_tenting_is_p7(tmp_path):
    a = _pcb(tmp_path, MODERN_BOARD, vias={"vias": [{"tenting": None}]})
    b = _pcb(tmp_path, MODERN_BOARD, vias={"vias": [{"tenting": "both"}]})
    assert w3bb.classify_unit("pcb", a, b)["label"] == "P7"


def _cross(findings, checks, **extra):
    return _doc(list(findings), analyzer_type="cross_analysis", checks_run=checks, **extra)


def test_cross_xv004_and_new_xv_findings_are_claimed():
    a = _cross([], [{"check": "XV-001", "ran": True}, {"check": "NR-001", "ran": False}])
    b = _cross([_finding("XV-003"), _finding("XV-004")],
               [{"check": "XV-001", "ran": True}, {"check": "XV-004", "ran": True}, {"check": "NR-001", "ran": False}])
    assert w3bb.classify_unit("cross_analysis", a, b)["label"] == "X2+X"


def _chained_pair(tmp_path, analyzer, pcb_a, pcb_b, findings_b=()):
    pa, pb = tmp_path / "pa.json", tmp_path / "pb.json"
    pa.write_text(json.dumps(pcb_a), encoding="utf-8")
    pb.write_text(json.dumps(pcb_b), encoding="utf-8")
    a = _doc([], analyzer_type=analyzer, inputs={"upstream_artifacts": {"pcb": {"path": str(pa)}}})
    b = _doc(list(findings_b), analyzer_type=analyzer, inputs={"upstream_artifacts": {"pcb": {"path": str(pb)}}})
    return a, b


def test_cross_other_rule_needs_a_moved_pcb(tmp_path):
    board = _pcb(tmp_path, MODERN_BOARD)
    a, b = _chained_pair(tmp_path, "cross_analysis", board, board, [_finding("PS-002")])
    r = w3bb.classify_unit("cross_analysis", a, b)
    assert r["label"] is None and any("identical upstream pcb" in x for x in r["reasons"])


def test_emc_behind_an_explained_pcb_is_d(tmp_path):
    pa = _pcb(tmp_path, MODERN_BOARD, vias={"vias": [{"tenting": None}]})
    pb = _pcb(tmp_path, MODERN_BOARD, vias={"vias": [{"tenting": "both"}]})
    a, b = _chained_pair(tmp_path, "emc", pa, pb, [_finding("GP-001")])
    assert w3bb.classify_unit("emc", a, b)["label"] == "D"
    assert w3bb.downstream(_d("emc"), a, b)
    assert not w3bb.pcb(_d("emc"), a, b)


def test_scan_reads_pad_type_and_shape_across_a_line_break():
    board = ('(kicad_pcb (version 20240108)\n  (footprint "X" (layer "F.Cu")\n'
             '    (pad "1" smd custom\n      (at 0 0) (size 1 1) (layers "B.Cu" "B.Mask")\n'
             '      (primitives (gr_circle (center 0 0) (end 1 0))))\n  )\n)\n')
    c = w3bb.scan_board(board)
    assert c["P5"] == 1 and c["P1s"] == 1
