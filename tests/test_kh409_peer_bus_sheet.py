"""KH-409 -- the Altium-flat / hybrid peer-sheet merge tags `_sheet` on
components/wires/labels/junctions/no-connects but not on bus_wires /
bus_entries, so the bus resolver's wires_by_sheet/entries_by_sheet dicts
(keyed by `bw.get("_sheet", 0)` / `be.get("_sheet", 0)` in
build_net_map's bus pass) file every peer sheet's bus geometry under
sheet 0 alongside the root sheet's -- only one shared BusGraph(0) is
built instead of one per sheet.

Fixture tests/fixtures/kh409-altium-bus/: page1 (root) and page2 (peer,
discovered via .kicad_pro top_level_sheets) each carry two independent
bus constructs:

  - DATA[0..1] (Round 1): identical bus geometry + member labels on
    both pages. NOT REPRODUCED there -- page2's bus-name label and its
    plain member-name labels ("DATA0"/"DATA1") are correctly `_sheet`
    tagged (label tagging is unaffected by this bug) and route around
    the broken shared BusGraph entirely via the ordinary per-sheet
    local-label path, so net identity comes out correct by accident.
    Kept here as a non-regression check (test_page_local_members_*).

  - CTRL[0..1] (Round 2): an independent bus per page, each with one
    bus_entry-tapped, plainly-labeled "CTRL0" member (R5 on page1, R6
    on page2; kicad-cli 10.0.6 confirms both are genuinely connected --
    see the fixture README). REPRODUCED: page2's tap gets bogusly
    flagged "unlabeled_entry_tap" in bus_topology.unresolved despite
    the valid label, because the tap-resolution mechanism's own
    add_point()/union_with_overlapping_wires() calls
    (analyze_schematic.py's bus pass, mechanism B1/B2) run under the
    shared BusGraph(0)'s sheet key (0), not page2's true sheet (1), so
    they never find page2's (correctly sheet-1-tagged) member wire --
    root_names comes back empty and the tap is marked unlabeled even
    though it plainly isn't. Verified in isolation: page1's identical
    construct, analyzed completely standalone (no .kicad_pro, no
    merge), resolves with bus_topology.unresolved == [].

The real bus_topology schema has no `buses[]` / per-bus "sheet" key (as
an earlier draft of this fixture's test assumed) -- only
bus_wire_count, bus_entry_count, unresolved, and optionally aliases /
detected_bus_signals exist (analyze_schematic.py's
analyze_bus_topology()). This test asserts on the net join and on
`unresolved` directly instead.

Fix round 1 (reviewer-caught): the fix also removes a THIRD symptom
that Rounds 1/2's evidence missed entirely -- pre-fix, page2's
bus-name labels ("DATA[0..1]", "CTRL[0..1]"), having fallen through to
the ordinary per-sheet local-label path with no matching same-name
label and no pins, each become their own degenerate zero-pin net using
the label TEXT itself as the net name. These phantom nets show up in
d["nets"] (pins: []) and in design_analysis.net_classification
(classified "signal"), and statistics.total_nets counts them (14
pre-fix vs 12 post-fix on this fixture). test_no_phantom_bus_name_nets
below covers this.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
SCH = _KH / "skills/kicad/scripts/analyze_schematic.py"
FIXTURE = _HARNESS / "tests/fixtures/kh409-altium-bus/page1.kicad_sch"
_CACHE = {}


def _d():
    if "d" not in _CACHE:
        out = subprocess.run([sys.executable, str(SCH), str(FIXTURE)],
                              capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["d"] = json.loads(out.stdout)
    return _CACHE["d"]


def _net_of(ref, pin="1"):
    for name, net in _d()["nets"].items():
        if any(p["component"] == ref and str(p["pin_number"]) == pin
               for p in net.get("pins", [])):
            return name
    return None


def test_page_local_members_not_joined_across_pages():
    assert _net_of("R1") != _net_of("R2"), (_net_of("R1"), _net_of("R2"))
    assert _net_of("R3") != _net_of("R4"), (_net_of("R3"), _net_of("R4"))


def test_peer_bus_tap_with_valid_label_resolves_cleanly():
    assert _net_of("R5") is not None, "R5 (page1 CTRL0) should be connected"
    assert _net_of("R6") is not None, "R6 (page2 CTRL0) should be connected"
    assert _net_of("R5") != _net_of("R6"), (_net_of("R5"), _net_of("R6"))


def test_no_unresolved_bus_constructs():
    assert not _d().get("bus_topology", {}).get("unresolved"), \
        _d()["bus_topology"]["unresolved"]


def test_no_phantom_bus_name_nets():
    # Pre-fix, page2's bus-name labels ("DATA[0..1]", "CTRL[0..1]")
    # fall through to the ordinary per-sheet local-label path and
    # become their own zero-pin phantom nets (the label TEXT used as
    # the net name) -- see kh409-repro.md "Round 2 -- correction".
    phantom = [name for name in _d()["nets"] if "[" in name]
    assert not phantom, phantom
    assert _d()["statistics"]["total_nets"] == 12, \
        _d()["statistics"]["total_nets"]


if __name__ == "__main__":
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
    sys.exit(1 if failed else 0)
