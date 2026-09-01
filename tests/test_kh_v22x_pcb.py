"""KH-358/KH-363 regression tests (harness; adopt via harness agent).

Both tests import analyze_pcb.py directly (in-process) and call its
analyze_pcb() function, since the module-level ``findings`` list is
populated inside that function before any CLI/envelope wrapping.
"""

TIER = "unit"

import os
import sys
from pathlib import Path
from unittest.mock import patch

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import analyze_pcb as ap
import analyze_schematic as asch

_SIMPLE_SCH_FIXTURE = _HARNESS / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"

_HEADER = (
    '(kicad_pcb\n'
    '  (version 20241228)\n'
    '  (generator "pcbnew")\n'
    '  (generator_version "9.0")\n'
    '  (general (thickness 1.6))\n'
    '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (44 "Edge.Cuts" user))\n'
)


def _pad_footprint(ref, x, net_id, net_name):
    return (
        f'  (footprint "Test:Pad"\n'
        f'    (layer "F.Cu")\n'
        f'    (uuid "aaaaaaaa-0000-0000-0000-0000000000{net_id:02d}")\n'
        f'    (at {x} 100)\n'
        f'    (property "Reference" "{ref}")\n'
        f'    (pad "1" smd rect\n'
        f'      (at 0 0)\n'
        f'      (size 2 2)\n'
        f'      (layers "F.Cu" "F.Mask")\n'
        f'      (net {net_id} "{net_name}")\n'
        f'    )\n'
        f'  )\n'
    )


def _via(x, net_id, tented):
    tenting = " (tenting front back)" if tented else ""
    return (
        f'  (via (at {x} 100) (size 0.6) (drill 0.3) '
        f'(layers "F.Cu" "B.Cu") (net {net_id}){tenting})\n'
    )


def _vp001_board():
    """One tented via-in-pad (U1/N1) and one untented control (U2/N2)."""
    return (
        _HEADER
        + '  (net 0 "")\n  (net 1 "N1")\n  (net 2 "N2")\n'
        + _pad_footprint("U1", 100, 1, "N1")
        + _pad_footprint("U2", 110, 2, "N2")
        + _via(100, 1, tented=True)
        + _via(110, 2, tented=False)
        + ')\n'
    )


def test_vp001_reads_real_tenting_field(tmp_path):
    """KH-358: VP-001 must key off the ``tenting`` field the extractor
    actually writes, not the never-populated ``remove_unused_layers``.
    """
    pcb = tmp_path / "vp001.kicad_pcb"
    pcb.write_text(_vp001_board())

    result = ap.analyze_pcb(str(pcb), include_trace_segments=True)
    vp001 = {f["component"]: f for f in result["findings"] if f["rule_id"] == "VP-001"}

    assert "U1" in vp001, "expected a VP-001 finding for the tented via-in-pad"
    assert vp001["U1"]["tented"] is True, "tented via must not be reported as untented"

    assert "U2" in vp001, "expected a VP-001 finding for the untented control via"
    assert vp001["U2"]["tented"] is False, "untented control via must be reported as untented"


def _kicad10_pad_board(pads):
    """KiCad-10 style board: no top-level (net N) declarations at all,
    pads reference nets by name only — exercises _build_net_mapping().
    """
    fps = "".join(
        f'  (footprint "Test:Pad"\n'
        f'    (layer "F.Cu")\n'
        f'    (uuid "bbbbbbbb-0000-0000-0000-{i:012d}")\n'
        f'    (at {100 + i * 10} 100)\n'
        f'    (property "Reference" "{ref}")\n'
        f'    (pad "{num}" smd rect\n'
        f'      (at 0 0)\n'
        f'      (size 2 2)\n'
        f'      (layers "F.Cu" "F.Mask")\n'
        f'      (net "{net}")\n'
        f'    )\n'
        f'  )\n'
        for i, (ref, num, net) in enumerate(pads)
    )
    return _HEADER + fps + ')\n'


def _net_number_for(footprints, net_name):
    for fp in footprints:
        for pad in fp["pads"]:
            if pad.get("net_name") == net_name:
                return pad["net_number"]
    return None


def test_net_id_map_reset_before_footprint_extraction(tmp_path):
    """KH-363: the module-level _net_name_to_id map must not leak stale
    IDs from a prior analyze_pcb() call into the next call's pad
    net_number assignment (A -> B -> A in-process, same interpreter).
    """
    board_a = tmp_path / "a.kicad_pcb"
    board_b = tmp_path / "b.kicad_pcb"
    # Both boards use net name "COMMON", but board_b's alphabetically-sorted
    # net set assigns it a different synthetic ID (2) than board_a's (1).
    board_a.write_text(_kicad10_pad_board([("U1", "1", "COMMON")]))
    board_b.write_text(_kicad10_pad_board([("U1", "1", "AAA"), ("U2", "1", "COMMON")]))

    captured = []
    real_extract = ap.extract_footprints

    def spy(root):
        fps = real_extract(root)
        captured.append(fps)
        return fps

    with patch.object(ap, "extract_footprints", side_effect=spy):
        ap.analyze_pcb(str(board_a))
        ap.analyze_pcb(str(board_b))
        ap.analyze_pcb(str(board_a))

    run1_net_number = _net_number_for(captured[0], "COMMON")
    run3_net_number = _net_number_for(captured[2], "COMMON")

    assert run1_net_number == run3_net_number, (
        f"pad net_number for net 'COMMON' changed across A->B->A: "
        f"run1={run1_net_number} run3={run3_net_number} "
        f"(stale _net_name_to_id contamination from the intervening board_b run)"
    )


def test_connectivity_graph_failure_surfaces_error_note(tmp_path):
    """Task 9 (KHPA-005 subset): a raising connectivity-graph build must
    not be silently swallowed. It should set connectivity_graph_error and
    still let the rest of the --full analysis complete.
    """
    pcb = tmp_path / "vp001.kicad_pcb"
    pcb.write_text(_vp001_board())

    with patch.object(ap, "build_connectivity_graph",
                       side_effect=RuntimeError("boom")):
        result = ap.analyze_pcb(str(pcb), include_trace_segments=True)

    assert "connectivity_graph" not in result
    assert result.get("connectivity_graph_error") == (
        "connectivity graph unavailable: RuntimeError: boom")
    # Rest of --full analysis still completed.
    assert "findings" in result
    assert result["tracks"]["segments"] is not None


def test_connectivity_graph_success_no_error_note(tmp_path):
    """Control: a board where connectivity graph construction succeeds
    must not carry connectivity_graph_error.
    """
    pcb = tmp_path / "vp001_ok.kicad_pcb"
    pcb.write_text(_vp001_board())

    result = ap.analyze_pcb(str(pcb), include_trace_segments=True)

    assert "connectivity_graph_error" not in result


def test_fv001_present_when_pcb_version_newer_than_tested(tmp_path):
    """Task 10 (KHPA-002 lite): a board whose (version ...) token is newer
    than analyze_pcb.MAX_TESTED_FORMAT_VERSION must fire FV-001.
    """
    pcb = tmp_path / "future.kicad_pcb"
    pcb.write_text(_vp001_board().replace(
        "(version 20241228)", "(version 99999999)"))

    result = ap.analyze_pcb(str(pcb))
    fv001 = [f for f in result["findings"] if f["rule_id"] == "FV-001"]

    assert len(fv001) == 1
    assert fv001[0]["detector"] == "format_version_gate"
    assert fv001[0]["severity"] == "info"
    assert "99999999" in fv001[0]["summary"]


def test_fv001_absent_on_normal_pcb_fixture(tmp_path):
    """Control: a normal-version board must not fire FV-001."""
    pcb = tmp_path / "normal.kicad_pcb"
    pcb.write_text(_vp001_board())

    result = ap.analyze_pcb(str(pcb))
    fv001 = [f for f in result["findings"] if f["rule_id"] == "FV-001"]

    assert fv001 == []


def test_fv001_present_when_sch_version_newer_than_tested(tmp_path):
    """Task 10 (KHPA-002 lite), schematic side: a .kicad_sch whose
    (version ...) token is newer than analyze_schematic.MAX_TESTED_FORMAT_VERSION
    must fire FV-001.
    """
    src = _SIMPLE_SCH_FIXTURE.read_text()
    sch = tmp_path / "future.kicad_sch"
    sch.write_text(src.replace("(version 20241228)", "(version 99999999)", 1))

    result = asch.analyze_schematic(str(sch), no_hierarchy=True)
    fv001 = [f for f in result["findings"] if f["rule_id"] == "FV-001"]

    assert len(fv001) == 1
    assert fv001[0]["detector"] == "format_version_gate"
    assert fv001[0]["severity"] == "info"
    assert "99999999" in fv001[0]["summary"]


def test_fv001_absent_on_normal_sch_fixture(tmp_path):
    """Control: the unmodified simple.kicad_sch fixture must not fire FV-001."""
    result = asch.analyze_schematic(str(_SIMPLE_SCH_FIXTURE), no_hierarchy=True)
    fv001 = [f for f in result["findings"] if f["rule_id"] == "FV-001"]

    assert fv001 == []


_PM002_OUTLINE = (
    '  (net 0 "")\n'
    '  (gr_line (start 90 90) (end 130 90) (layer "Edge.Cuts") (width 0.1))\n'
    '  (gr_line (start 130 90) (end 130 130) (layer "Edge.Cuts") (width 0.1))\n'
    '  (gr_line (start 130 130) (end 90 130) (layer "Edge.Cuts") (width 0.1))\n'
    '  (gr_line (start 90 130) (end 90 90) (layer "Edge.Cuts") (width 0.1))\n'
)


def _crtyd_footprint(ref, x, y, uid, value="", half_size=2.0):
    """A footprint with an F.CrtYd rectangle courtyard centered on (x, y)."""
    value_prop = f'    (property "Value" "{value}")\n' if value else ""
    return (
        f'  (footprint "Test:Pad"\n'
        f'    (layer "F.Cu")\n'
        f'    (uuid "cccccccc-0000-0000-0000-{uid:012d}")\n'
        f'    (at {x} {y})\n'
        f'    (property "Reference" "{ref}")\n'
        f'{value_prop}'
        f'    (fp_rect (start {-half_size} {-half_size}) (end {half_size} {half_size}) '
        f'(layer "F.CrtYd") (width 0.05))\n'
        f'    (pad "1" smd rect\n'
        f'      (at 0 0)\n'
        f'      (size 1 1)\n'
        f'      (layers "F.Cu" "F.Mask")\n'
        f'      (net 0 "")\n'
        f'    )\n'
        f'  )\n'
    )


def test_pm002_rf_negative_clearance_no_negative_distance_in_message(tmp_path):
    """KH-389: an RF-classified footprint (ESP32-WROOM) whose courtyard
    overhangs the board's left edge by 2mm (negative clearance) must not
    render a negative "mm from board edge" distance in the PM-002 summary.
    The KH-344 overhang-message rewrite must apply regardless of the
    RF-module message exemption; severity stays 'info' (RF exemption still
    governs severity, just not message formatting).
    """
    pcb = tmp_path / "pm002_rf.kicad_pcb"
    board = (
        _HEADER + _PM002_OUTLINE
        + _crtyd_footprint("U1", 90, 110, 1, value="ESP32-WROOM-32")
        + ')\n'
    )
    pcb.write_text(board)

    result = ap.analyze_pcb(str(pcb))
    pm002 = [f for f in result["findings"] if f["rule_id"] == "PM-002"]

    assert len(pm002) == 1
    finding = pm002[0]
    assert "mm from board edge" not in finding["summary"], (
        f"negative-distance phrasing leaked into RF-exempt summary: {finding['summary']!r}")
    assert finding["summary"] == "U1 courtyard overhangs board edge by 2.0mm"
    assert finding["severity"] == "info"


def test_pm002_off_board_part_gets_distinct_classification(tmp_path):
    """KH-389: a part whose footprint bbox lies entirely outside the board
    outline (well past the "overhang" case) must be classified as
    off-board, not "overhangs", with severity demoted to warning (not
    error).
    """
    pcb = tmp_path / "pm002_off.kicad_pcb"
    board = (
        _HEADER + _PM002_OUTLINE
        + _crtyd_footprint("U2", 70, 110, 2)
        + ')\n'
    )
    pcb.write_text(board)

    result = ap.analyze_pcb(str(pcb))
    pm002 = [f for f in result["findings"] if f["rule_id"] == "PM-002"]

    assert len(pm002) == 1
    finding = pm002[0]
    assert "overhangs" not in finding["summary"]
    assert finding["summary"] == "U2 placed off-board (22.0 mm outside outline)"
    assert finding["severity"] == "warning"
