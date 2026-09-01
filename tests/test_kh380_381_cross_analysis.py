"""KH-380 / KH-381 — cross_analysis NR-001 key fix + checks_run manifest.

KH-380: `check_critical_net_routing` (NR-001) read
`board_outline['segments']`, but `analyze_pcb.py`'s `extract_board_outline`
has only ever emitted `board_outline['edges']`. NR-001 was structurally
unreachable — the outline-lookup guard always saw an empty list and
returned before doing any distance computation, regardless of how close a
critical-net track actually ran to the board edge.

KH-381: cross_analysis had ~15 ungated early-return guards across its 10
check_* functions with no way for a consumer to tell "this check ran and
found nothing" apart from "this check silently skipped because its
required input was absent". `checks_run[]` is the manifest that makes
that distinction visible (one entry per check function, in call order).

Fixtures below hand-build minimal schematic/pcb dicts mirroring the real
producer field names (`board_outline.edges`, `tracks.segments`, `nets`,
`net_classifications`) rather than using real analyzer output, per repo
convention for targeted regression tests (see test_kh357_be001_rect.py).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from cross_analysis import check_critical_net_routing, run_all_checks


def _schematic_with_clock_net():
    return {
        "components": [],
        "findings": [],
        "net_classifications": {"CLK1": {"type": "clock"}},
    }


def _pcb_with_track_near_rect_edge():
    """A 100x100 rect board outline with a CLK1 track running 0.3mm from
    the x=0 side — well inside the NR-001 error threshold (1.0mm)."""
    return {
        "footprints": [],
        "nets": {"1": "CLK1"},
        "tracks": {"segments": [
            {"net": 1, "x1": 0.3, "y1": 50.0, "x2": 0.3, "y2": 55.0},
        ]},
        "board_outline": {"edges": [
            {"type": "rect", "start": [0.0, 0.0], "end": [100.0, 100.0]},
        ]},
    }


def test_nr001_fires_when_critical_net_track_runs_near_board_edge():
    """KH-380: NR-001 must read board_outline['edges'] (the real producer
    key) and actually flag a high-speed net routed near the board edge.
    Before the fix this was structurally impossible: the function read a
    key ('segments') the producer never writes, so the outline-presence
    guard always returned early with zero findings no matter how close
    the track ran to the edge."""
    sch = _schematic_with_clock_net()
    pcb = _pcb_with_track_near_rect_edge()
    findings = check_critical_net_routing(sch, pcb)
    nr001 = [f for f in findings if f.get("rule_id") == "NR-001"]
    assert len(nr001) == 1, f"expected exactly one NR-001 finding, got {nr001}"
    assert nr001[0]["severity"] == "error"
    assert "CLK1" in nr001[0]["nets"]


def test_nr001_rect_edge_measures_to_nearest_side_not_diagonal():
    """The rect outline edge must expand to its 4 sides (KH-357/Task 14
    pattern), not measure to the corner-to-corner diagonal. A track at
    x=0.3 near the x=0 side must NOT be scored against the (0,0)->(100,100)
    diagonal, which would report a much smaller/wrong distance."""
    sch = _schematic_with_clock_net()
    pcb = _pcb_with_track_near_rect_edge()
    findings = check_critical_net_routing(sch, pcb)
    nr001 = [f for f in findings if f.get("rule_id") == "NR-001"]
    assert len(nr001) == 1
    # severity is 'error' only because measured distance (~0.3mm) is below
    # the 1.0mm error threshold; against the diagonal the point sits at
    # (0.3, 52.5) which is nowhere near the y=x line, so a diagonal
    # measurement would give a large distance and NOT fire at all.
    assert "0.3mm" in nr001[0]["summary"]


def test_checks_run_manifest_present_with_valid_entries():
    """KH-381: every analyzer run must carry checks_run[], one entry per
    check function, each with the documented shape."""
    sch = _schematic_with_clock_net()
    pcb = _pcb_with_track_near_rect_edge()
    findings, checks_run = run_all_checks(sch, pcb)

    assert isinstance(checks_run, list) and checks_run, "checks_run must be a non-empty list"
    for entry in checks_run:
        assert set(entry.keys()) == {"check", "ran", "reason_skipped", "items_examined", "findings"}
        assert isinstance(entry["check"], str) and entry["check"]
        assert isinstance(entry["ran"], bool)
        assert isinstance(entry["items_examined"], int)
        assert isinstance(entry["findings"], int)
        if entry["ran"]:
            assert entry["reason_skipped"] is None, entry
        else:
            assert isinstance(entry["reason_skipped"], str) and entry["reason_skipped"], entry

    nr001_entries = [e for e in checks_run if e["check"] == "NR-001"]
    assert len(nr001_entries) == 1
    assert nr001_entries[0]["ran"] is True
    actual_nr001_findings = [f for f in findings if f.get("rule_id") == "NR-001"]
    assert nr001_entries[0]["findings"] == len(actual_nr001_findings) == 1


def test_checks_run_reports_honest_skip_reason_for_missing_connectivity_graph():
    """KH-381: a check that returns early for lack of required input
    (here, PS-002 needs pcb['connectivity_graph'], which this fixture
    doesn't provide) must report ran: False with a real reason string,
    not silently blend into the same shape as 'ran and found nothing'."""
    sch = _schematic_with_clock_net()
    pcb = _pcb_with_track_near_rect_edge()
    assert "connectivity_graph" not in pcb
    _findings, checks_run = run_all_checks(sch, pcb)

    ps002_entries = [e for e in checks_run if e["check"] == "PS-002"]
    assert len(ps002_entries) == 1, f"expected exactly one PS-002 entry, got {ps002_entries}"
    ps002 = ps002_entries[0]
    assert ps002["ran"] is False
    assert ps002["items_examined"] == 0
    assert ps002["findings"] == 0
    assert "connectivity_graph" in ps002["reason_skipped"]


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
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
