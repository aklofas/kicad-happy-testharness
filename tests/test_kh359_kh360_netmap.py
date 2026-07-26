"""Regression tests for KH-359 (serialization bare-name merge) and
KH-360 (first-wire-only union) in build_net_map."""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from analyze_schematic import build_net_map


def _comp(ref, x, y, sheet=0, pin="1"):
    return {"reference": ref, "type": "ic", "_sheet": sheet, "pins": [
        {"number": pin, "name": "P", "type": "passive", "x": x, "y": y}]}


def test_kh360_junction_joins_all_crossing_wires():
    wires = [
        {"x1": 0, "y1": 0, "x2": 10, "y2": 0},   # horizontal
        {"x1": 5, "y1": -5, "x2": 5, "y2": 5},   # vertical, crosses at (5, 0)
    ]
    junctions = [{"x": 5, "y": 0}]
    comps = [_comp("R1", 0, 0), _comp("R2", 5, 5)]
    for ws in (wires, list(reversed(wires))):
        nets = build_net_map(comps, ws, [], [], junctions, [])
        assert len(nets) == 1, f"wire order {ws} gave {len(nets)} nets"
        refs = {p["component"] for n in nets.values() for p in n["pins"]}
        assert refs == {"R1", "R2"}


def _label(name, x, y, sheet=0, ltype="label"):
    return {"name": name, "type": ltype, "x": x, "y": y, "_sheet": sheet}


def test_kh359_same_name_local_labels_stay_split_across_sheets():
    # Sheet 0 and sheet 1 each have a wire labelled STAT with one pin.
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": s} for s in (0, 1)]
    labels = [_label("STAT", 5, 0, sheet=s) for s in (0, 1)]
    comps = [_comp("U1", 0, 0, sheet=0), _comp("U2", 0, 0, sheet=1)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["top", "sub"])
    assert set(nets) == {"/top/STAT", "/sub/STAT"}
    assert nets["/top/STAT"]["display_name"] == "STAT"
    assert nets["/top/STAT"]["name"] == "/top/STAT"
    assert [p["component"] for p in nets["/top/STAT"]["pins"]] == ["U1"]
    assert [p["component"] for p in nets["/sub/STAT"]["pins"]] == ["U2"]


def test_kh359_local_label_does_not_merge_into_global_power_net():
    # GND power symbol net + a disconnected wire carrying a LOCAL "GND" label.
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0},
             {"x1": 0, "y1": 20, "x2": 10, "y2": 20}]
    power = [{"net_name": "GND", "x": 0, "y": 0, "_sheet": 0}]
    labels = [_label("GND", 5, 20)]
    comps = [_comp("U1", 10, 0), _comp("J1", 10, 20)]
    nets = build_net_map(comps, wires, labels, power, [], [],
                         sheet_names=["main"])
    assert set(nets) == {"GND", "/main/GND"}
    assert [p["component"] for p in nets["GND"]["pins"]] == ["U1"]
    assert [p["component"] for p in nets["/main/GND"]["pins"]] == ["J1"]
    assert nets["/main/GND"]["display_name"] == "GND"


def test_kh359_no_collision_is_untouched():
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0}]
    labels = [_label("SIG", 5, 0)]
    comps = [_comp("U1", 0, 0)]
    nets = build_net_map(comps, wires, labels, [], [], [])
    assert set(nets) == {"SIG"}
    assert "display_name" not in nets["SIG"]
    assert list(nets["SIG"].keys()) == [
        "name", "pins", "point_count", "no_connect", "has_pwr_flag", "labels"]


def test_kh359_sheet_names_fallback_and_instance_stems():
    # sheet_names=None -> sheet<idx>; repeated stems get #N.
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": s} for s in (1, 2)]
    labels = [_label("X", 5, 0, sheet=s) for s in (1, 2)]
    comps = [_comp("U1", 0, 0, sheet=1), _comp("U2", 0, 0, sheet=2)]
    nets = build_net_map(comps, wires, labels, [], [], [])
    assert set(nets) == {"/sheet1/X", "/sheet2/X"}
    nets2 = build_net_map(comps, wires, labels, [], [], [],
                          sheet_names=["top", "child", "child"])
    assert set(nets2) == {"/child/X", "/child#2/X"}


# ---------------------------------------------------------------------------
# Task 4 (KH-359 consumer containment): bare-name matching against
# sheet-qualified keys at the four audited hard-break sites.
# ---------------------------------------------------------------------------

def test_qualified_keys_classify_as_power_and_ground():
    from kicad_utils import is_power_net_name, is_ground_name
    assert is_ground_name("/inc8b/GND")
    assert is_ground_name("/inc8b#2/GND")
    assert is_power_net_name("/psu/VCC")
    assert not is_power_net_name("/top/STAT")


def test_bus_alias_members_resolve_against_qualified_keys():
    # Bus alias member "D0" is a bare label name. Two sheets each carry a
    # local-labelled wire "D0" -> qualified keys /top/D0, /sub/D0. The
    # member-resolution check in analyze_bus_topology must match the bare
    # member name against display_name, not just the raw net key.
    from analyze_schematic import analyze_bus_topology

    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": s} for s in (0, 1)]
    labels = [_label("D0", 5, 0, sheet=s) for s in (0, 1)]
    comps = [_comp("U1", 0, 0, sheet=0), _comp("U2", 0, 0, sheet=1)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["top", "sub"])
    assert set(nets) == {"/top/D0", "/sub/D0"}

    bus_elements = {"bus_aliases": [{"name": "MYBUS", "members": ["D0"]}]}
    result = analyze_bus_topology(bus_elements, labels, nets)
    entry = result["aliases"][0]
    assert entry["resolved_nets"] == 1
    assert "unresolved_members" not in entry


def test_diffpair_detection_pairs_within_sheet_not_across():
    # Two sheets each carry a local USB_P/USB_N pair -> qualified keys.
    # _detect_differential_pairs must find both same-sheet pairs and must
    # NOT cross-pair /s1/USB_P with /s2/USB_N (or vice versa).
    from analyze_schematic import _detect_differential_pairs
    from kicad_types import AnalysisContext

    wires = []
    labels = []
    comps = []
    for i in (0, 1):
        wires += [
            {"x1": 0, "y1": i * 20, "x2": 10, "y2": i * 20, "_sheet": i},
            {"x1": 0, "y1": i * 20 + 5, "x2": 10, "y2": i * 20 + 5, "_sheet": i},
        ]
        labels += [
            _label("USB_P", 5, i * 20, sheet=i),
            _label("USB_N", 5, i * 20 + 5, sheet=i),
        ]
        comps += [_comp(f"U{i}a", 0, i * 20, sheet=i),
                  _comp(f"U{i}b", 0, i * 20 + 5, sheet=i)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["s1", "s2"])
    assert set(nets) == {"/s1/USB_P", "/s1/USB_N", "/s2/USB_P", "/s2/USB_N"}

    ctx = AnalysisContext(components=comps, nets=nets, lib_symbols={}, pin_net={})
    pairs = _detect_differential_pairs(ctx)
    found = {(p["positive"], p["negative"]) for p in pairs}
    assert found == {("/s1/USB_P", "/s1/USB_N"), ("/s2/USB_P", "/s2/USB_N")}


def test_diffpair_unqualified_board_unchanged():
    # No collisions -> bare keys, empty prefix; end-to-end pairing behavior
    # matches the pre-Task-4 single-map lookup.
    from analyze_schematic import _detect_differential_pairs
    from kicad_types import AnalysisContext

    wires = [
        {"x1": 0, "y1": 0, "x2": 10, "y2": 0},
        {"x1": 0, "y1": 5, "x2": 10, "y2": 5},
    ]
    labels = [_label("USB_P", 5, 0), _label("USB_N", 5, 5)]
    comps = [_comp("U1", 0, 0), _comp("U2", 0, 5)]
    nets = build_net_map(comps, wires, labels, [], [], [])
    assert set(nets) == {"USB_P", "USB_N"}
    assert "display_name" not in nets["USB_P"]

    ctx = AnalysisContext(components=comps, nets=nets, lib_symbols={}, pin_net={})
    pairs = _detect_differential_pairs(ctx)
    found = {(p["positive"], p["negative"]) for p in pairs}
    assert found == {("USB_P", "USB_N")}


def test_diffpair_case_collision_matches_old_last_wins_semantics():
    # Review finding: on an unqualified board with case-variant net names
    # that collide under .upper() (e.g. "usb_p" vs "USB_P"), the diff-pair
    # map must pick the same winner as the pre-Task-4 comprehension
    # `{n.upper(): n for n in nets}` -- iteration-order last-wins -- not
    # first-wins (setdefault). Computes the old-semantics reference
    # inline from the literal old algorithm so this locks in the *true*
    # old behavior, not an assumed one.
    from analyze_schematic import _detect_differential_pairs
    from kicad_types import AnalysisContext

    nets = {
        "usb_p": {"pins": []},
        "USB_P": {"pins": []},
        "usb_n": {"pins": []},
    }

    # Reference: the exact pre-Task-4 one-liner.
    old_upper = {n.upper(): n for n in nets}
    expected_pos = old_upper["USB_P"]
    expected_neg = old_upper["USB_N"]
    assert (expected_pos, expected_neg) == ("USB_P", "usb_n"), (
        "sanity check on the reference algorithm itself")

    ctx = AnalysisContext(components=[], nets=nets, lib_symbols={}, pin_net={})
    pairs = _detect_differential_pairs(ctx)
    assert len(pairs) == 1
    assert (pairs[0]["positive"], pairs[0]["negative"]) == (expected_pos, expected_neg)


def test_hierarchical_label_joins_same_sheet_local_label():
    # openmd root V_{ANA}: a hierarchical label and a local label of the SAME
    # name on ONE sheet name the same net (KiCad joins a hier label to same-name
    # local labels within its own sheet). Two separate wires, one carrying the
    # hier label, one the local label.
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0},
             {"x1": 0, "y1": 20, "x2": 10, "y2": 20}]
    labels = [_label("VA", 5, 0, ltype="hierarchical_label"),
              _label("VA", 5, 20, ltype="label")]
    comps = [_comp("U1", 0, 0), _comp("U2", 0, 20)]
    nets = build_net_map(comps, wires, labels, [], [], [])
    assert set(nets) == {"VA"}, f"hier VA + local VA on one sheet must be one net, got {set(nets)}"
    assert sorted(p["component"] for p in nets["VA"]["pins"]) == ["U1", "U2"]


def test_same_name_hierarchical_labels_always_union_never_qualify():
    # Review finding (Step 4, build_hierarchy_context cross-sheet match):
    # two hierarchical_label entries sharing a bare name on DIFFERENT,
    # physically-disconnected sheets do NOT produce a KH-359 bare-name
    # collision requiring qualification. build_net_map's pre-existing
    # (pre-Task-3) union-by-label-name pass unconditionally unions every
    # global_label / hierarchical_label / global-scope power symbol that
    # shares a literal name (lines ~1456-1502) -- that's the whole point
    # of a hierarchical label: connecting non-adjacent wires across the
    # sheet hierarchy. Only LOCAL-scope names ("label"/"directive_label"
    # types, or local power symbols) are scoped per-sheet and can
    # genuinely collide under two different physical nets.
    #
    # Consequence for Step 4's `or net_info.get("display_name") ==
    # label_name` clause in build_hierarchy_context: a hierarchical_label
    # bare-name "collision" across sheets is structurally unreachable, so
    # a hierarchical_label's own winning net_name can never end up on a
    # qualified (#N) key via this path -- the clause cannot fire for the
    # scenario it was written for. Confirmed both by this direct
    # build_net_map trace and by two independent build_hierarchy_context
    # fixture attempts (real 2-and-3-file .kicad_sch hierarchies) that
    # both converged on the identical result -- see task-4-report.md.
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": s} for s in (0, 1)]
    labels = [_label("SHARED", 5, 0, sheet=s, ltype="hierarchical_label")
              for s in (0, 1)]
    comps = [_comp("U1", 0, 0, sheet=0), _comp("U2", 0, 0, sheet=1)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["top", "sub"])
    assert set(nets) == {"SHARED"}, (
        "two same-named hierarchical_labels on different sheets must "
        "union into one net, not produce two qualified entries")
    assert sorted(p["component"] for p in nets["SHARED"]["pins"]) == ["U1", "U2"]
    assert not any("display_name" in v for v in nets.values())


# ---------------------------------------------------------------------------
# Task 10 (#25 phase 4a): bus pass integration into build_net_map. A parent
# bus reaching a sheet pin maps positionally onto the child's hier-label bus,
# so member i on both sides is one net.
# ---------------------------------------------------------------------------

def _bus_fixture():
    """Parent sheet 0: wire labelled B2 -> bus entry at (10,0)->(8,2) ->
    bus B[0..3] reaching sheet pin P[0..3] (ns /X). Child sheet 1: hier
    label P[0..3] on a bus, entry (20,0)->(18,2) to wire labelled P2.
    B2/P2 sit at member index 2 of B[0..3] / P[0..3]."""
    wires = [
        {"x1": 0, "y1": 2, "x2": 8, "y2": 2, "_sheet": 0},     # parent member wire
        {"x1": 0, "y1": 2, "x2": 0, "y2": 12, "_sheet": 0},    # stub to pin U1
        {"x1": 18, "y1": 2, "x2": 38, "y2": 2, "_sheet": 1},   # child member wire
    ]
    labels = [
        # Member labels: identified by name-in-expansion of their cluster.
        {"name": "B2", "type": "label", "x": 4, "y": 2, "_sheet": 0},
        {"name": "P2", "type": "label", "x": 30, "y": 2, "_sheet": 1},
        # bus label on the parent bus cluster:
        {"name": "B[0..3]", "type": "label", "x": 15, "y": 0, "_sheet": 0},
        # sheet-pin stub (parent side), shaped as parse_all_sheets emits it:
        {"name": "/X/P[0..3]", "type": "hierarchical_label", "x": 25, "y": 0,
         "_sheet": 0, "_bare_name": "P[0..3]", "_hier_ns": "/X",
         "_is_sheet_pin": True},
        # child-side hier label on the child bus cluster:
        {"name": "/X/P[0..3]", "type": "hierarchical_label", "x": 20, "y": 0,
         "_sheet": 1, "_bare_name": "P[0..3]", "_hier_ns": "/X"},
    ]
    bus_elements = {
        "bus_wires": [
            {"x1": 10, "y1": 0, "x2": 25, "y2": 0, "_sheet": 0},
            {"x1": 20, "y1": 0, "x2": 25, "y2": 0, "_sheet": 1},
        ],
        "bus_entries": [
            {"x": 10, "y": 0, "dx": -2, "dy": 2, "_sheet": 0},  # bus (10,0) -> wire (8,2)
            {"x": 20, "y": 0, "dx": -2, "dy": 2, "_sheet": 1},  # bus (20,0) -> wire (18,2)
        ],
        "bus_aliases": [],
    }
    return wires, labels, bus_elements


def test_bus_member_unifies_across_sheet_pin_positionally():
    wires, labels, bus = _bus_fixture()
    comps = [_comp("U1", 0, 12, sheet=0), _comp("U2", 38, 2, sheet=1)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["top", "child"], bus_elements=bus)
    # B2 (parent member index 2) and P2 (child member index 2) are ONE net,
    # named from the parent label (lowest sheet wins):
    b2 = nets["B2"]
    refs = {p["component"] for p in b2["pins"]}
    assert refs == {"U1", "U2"}
    assert "P2" not in nets          # absorbed into B2, not a separate net
    # No bus-name phantom nets:
    assert "B[0..3]" not in nets
    assert not any("P[0..3]" in k for k in nets)


def test_co_clustered_sheet_pins_join_positionally():
    # Task 11 (m68k Bus-sheet pattern): a bus routed straight from one sub-sheet
    # symbol's pin to another's, on ONE physical cluster with NO local label to
    # canonicalize it (parent sheet 0 wires /A/P[0..3] and /B/Q[0..3] together).
    # The two pins are the same physical bus, so bit i of P = bit i of Q, which
    # makes childA.P0 and childB.Q0 one net. Before the fix each pin kept its own
    # member names and the two children never met.
    wires = [
        # childA(1): member wire P0 -> U_A
        {"x1": 20, "y1": 0, "x2": 30, "y2": 0, "_sheet": 1},
        # childB(2): member wire Q0 -> U_B
        {"x1": 20, "y1": 0, "x2": 30, "y2": 0, "_sheet": 2},
    ]
    labels = [
        # parent cluster: two sheet pins, different bus names, NO local label
        {"name": "/A/P[0..3]", "type": "hierarchical_label", "x": 0, "y": 0,
         "_sheet": 0, "_bare_name": "P[0..3]", "_hier_ns": "/A",
         "_is_sheet_pin": True},
        {"name": "/B/Q[0..3]", "type": "hierarchical_label", "x": 20, "y": 0,
         "_sheet": 0, "_bare_name": "Q[0..3]", "_hier_ns": "/B",
         "_is_sheet_pin": True},
        # childA(1): hier P[0..3] on its bus + member label P0
        {"name": "/A/P[0..3]", "type": "hierarchical_label", "x": 5, "y": 0,
         "_sheet": 1, "_bare_name": "P[0..3]", "_hier_ns": "/A"},
        {"name": "P0", "type": "label", "x": 25, "y": 0, "_sheet": 1},
        # childB(2): hier Q[0..3] on its bus + member label Q0
        {"name": "/B/Q[0..3]", "type": "hierarchical_label", "x": 5, "y": 0,
         "_sheet": 2, "_bare_name": "Q[0..3]", "_hier_ns": "/B"},
        {"name": "Q0", "type": "label", "x": 25, "y": 0, "_sheet": 2},
    ]
    bus = {
        "bus_wires": [
            {"x1": 0, "y1": 0, "x2": 20, "y2": 0, "_sheet": 0},   # parent shared cluster
            {"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": 1},   # childA bus
            {"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": 2},   # childB bus
        ],
        "bus_entries": [],
        "bus_aliases": [],
    }
    comps = [_comp("U_A", 30, 0, sheet=1), _comp("U_B", 30, 0, sheet=2)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["bus", "childA", "childB"], bus_elements=bus)
    joined = [k for k, v in nets.items()
              if any(p["component"] in ("U_A", "U_B") for p in v["pins"])]
    assert len(joined) == 1, (
        f"U_A and U_B must share one net via the co-clustered parent pins, "
        f"got {joined}")
    assert {p["component"] for p in nets[joined[0]]["pins"]} == {"U_A", "U_B"}


def test_bus_pass_is_inert_without_bus_elements():
    wires, labels, bus = _bus_fixture()
    comps = [_comp("U1", 0, 12, sheet=0), _comp("U2", 38, 2, sheet=1)]
    empty = {"bus_wires": [], "bus_entries": [], "bus_aliases": []}
    a = build_net_map(comps, wires, labels, [], [], [], sheet_names=["t", "c"])
    b = build_net_map(comps, wires, labels, [], [], [], sheet_names=["t", "c"],
                      bus_elements=empty)
    assert a == b


def test_same_sheet_bus_label_joins_separate_clusters_member_wise():
    # Task 11 (m68k Memory pass-through pattern): a mid sheet routes a bus
    # from its parent down to two children through TWO physically-separate
    # bus wire clusters that carry the SAME local bus label B[0..3] but no
    # member wires of their own. KiCad connects same-name local/hier bus
    # labels within a sheet, so member Bi is ONE net across both clusters —
    # which makes childA.B0 and childB.B0 the same net. Before the fix the
    # two mid clusters kept separate member slots and the two children never
    # met.
    wires = [
        # mid(0): two separate bus-side stubs are the bus wires (below);
        # the sheet-pin labels sit on them. No mid member wires.
        # childA(1): member wire B0 -> U_A
        {"x1": 20, "y1": 0, "x2": 30, "y2": 0, "_sheet": 1},
        # childB(2): member wire B0 -> U_B
        {"x1": 20, "y1": 0, "x2": 30, "y2": 0, "_sheet": 2},
    ]
    labels = [
        # mid cluster A: local bus label + sheet pin toward child A (ns /A)
        {"name": "B[0..3]", "type": "label", "x": 5, "y": 0, "_sheet": 0},
        {"name": "/A/B[0..3]", "type": "hierarchical_label", "x": 0, "y": 0,
         "_sheet": 0, "_bare_name": "B[0..3]", "_hier_ns": "/A",
         "_is_sheet_pin": True},
        # mid cluster B: local bus label + sheet pin toward child B (ns /B)
        {"name": "B[0..3]", "type": "label", "x": 5, "y": 20, "_sheet": 0},
        {"name": "/B/B[0..3]", "type": "hierarchical_label", "x": 0, "y": 20,
         "_sheet": 0, "_bare_name": "B[0..3]", "_hier_ns": "/B",
         "_is_sheet_pin": True},
        # childA(1): hier label on its bus + member wire label B0
        {"name": "/A/B[0..3]", "type": "hierarchical_label", "x": 5, "y": 0,
         "_sheet": 1, "_bare_name": "B[0..3]", "_hier_ns": "/A"},
        {"name": "B0", "type": "label", "x": 25, "y": 0, "_sheet": 1},
        # childB(2): hier label on its bus + member wire label B0
        {"name": "/B/B[0..3]", "type": "hierarchical_label", "x": 5, "y": 0,
         "_sheet": 2, "_bare_name": "B[0..3]", "_hier_ns": "/B"},
        {"name": "B0", "type": "label", "x": 25, "y": 0, "_sheet": 2},
    ]
    bus = {
        "bus_wires": [
            {"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": 0},    # mid cluster A
            {"x1": 0, "y1": 20, "x2": 10, "y2": 20, "_sheet": 0},  # mid cluster B
            {"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": 1},    # childA bus
            {"x1": 0, "y1": 0, "x2": 10, "y2": 0, "_sheet": 2},    # childB bus
        ],
        "bus_entries": [],
        "bus_aliases": [],
    }
    comps = [_comp("U_A", 30, 0, sheet=1), _comp("U_B", 30, 0, sheet=2)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["mid", "childA", "childB"], bus_elements=bus)
    b0_nets = [k for k, v in nets.items()
               if any(p["component"] in ("U_A", "U_B") for p in v["pins"])]
    assert len(b0_nets) == 1, (
        f"U_A and U_B must share one net via the mid sheet's B[0..3] "
        f"pass-through, got {b0_nets}")
    refs = {p["component"] for p in nets[b0_nets[0]]["pins"]}
    assert refs == {"U_A", "U_B"}


def test_bus_member_does_not_fuse_with_unrelated_global_label():
    # Review CASE C: a parent LOCAL bus B[0..3] reaches sheet pin P[0..3]; the
    # parent has NO local B0 member wire, but an unrelated GLOBAL label "B0"
    # sits on U9 elsewhere. Child sheet 1: hier P[0..3], member P0 -> U2. Bus
    # member B0 is local-scoped and must NOT fuse with the global B0/U9 — the
    # pre-guard bare-key fallback wrongly merged U2 + U9 into net "B0".
    wires = [
        {"x1": 18, "y1": 2, "x2": 38, "y2": 2, "_sheet": 1},   # child member P0 -> U2
        {"x1": 0, "y1": 50, "x2": 10, "y2": 50, "_sheet": 0},  # parent global-B0 wire -> U9
    ]
    labels = [
        {"name": "B[0..3]", "type": "label", "x": 15, "y": 0, "_sheet": 0},
        {"name": "/X/P[0..3]", "type": "hierarchical_label", "x": 25, "y": 0,
         "_sheet": 0, "_bare_name": "P[0..3]", "_hier_ns": "/X",
         "_is_sheet_pin": True},
        {"name": "/X/P[0..3]", "type": "hierarchical_label", "x": 20, "y": 0,
         "_sheet": 1, "_bare_name": "P[0..3]", "_hier_ns": "/X"},
        {"name": "P0", "type": "label", "x": 30, "y": 2, "_sheet": 1},
        {"name": "B0", "type": "global_label", "x": 5, "y": 50, "_sheet": 0},
    ]
    bus = {
        "bus_wires": [
            {"x1": 10, "y1": 0, "x2": 25, "y2": 0, "_sheet": 0},
            {"x1": 20, "y1": 0, "x2": 25, "y2": 0, "_sheet": 1},
        ],
        "bus_entries": [
            {"x": 20, "y": 0, "dx": -2, "dy": 2, "_sheet": 1},  # child entry -> wire (18,2)
        ],
        "bus_aliases": [],
    }
    comps = [_comp("U9", 0, 50, sheet=0), _comp("U2", 38, 2, sheet=1)]
    nets = build_net_map(comps, wires, labels, [], [], [],
                         sheet_names=["top", "child"], bus_elements=bus)
    # Global "B0" keeps ONLY U9; U2 (bus member) is a separate net, not fused.
    assert {p["component"] for p in nets["B0"]["pins"]} == {"U9"}
    u2_nets = [k for k, v in nets.items()
               if any(p["component"] == "U2" for p in v["pins"])]
    assert u2_nets and all(k != "B0" for k in u2_nets)


# ---------------------------------------------------------------------------
# Task 12 (carried from Task 11 review): two small gaps in the bus-label /
# sheet-pin exclusion logic that weren't covered by an explicit unit test.
# ---------------------------------------------------------------------------

def test_validate_hierarchical_labels_bus_filter_excludes_bus_names_only():
    # A bus-name hier label (e.g. In[0..7]) is consumed by the bus pass and
    # legitimately never appears as a net under its own bus name -- it must
    # be excluded from unconnected_hierarchical. A markup label like ~{OE}
    # is NOT a bus name (expand_bus_name returns None for it) and must stay
    # subject to the check.
    from analyze_schematic import validate_hierarchical_labels

    labels = [
        _label("In[0..7]", 0, 0, ltype="hierarchical_label"),
        _label("~{OE}", 0, 10, ltype="hierarchical_label"),
    ]
    result = validate_hierarchical_labels(labels, {}, {"bus_aliases": []})
    unconnected = result.get("unconnected_hierarchical", [])
    assert "In[0..7]" not in unconnected
    assert "~{OE}" in unconnected


def test_sheet_pin_label_does_not_join_local_label_by_bare_name():
    # Task 11 fix #5's essential half: a SHEET-PIN hier label (marked
    # _is_sheet_pin) must NOT join same-name local labels on the same sheet
    # by bare name -- only a genuine (non-sheet-pin) hierarchical label does
    # that (see test_hierarchical_label_joins_same_sheet_local_label above).
    # Two disconnected wires, same bare name "X", one carrying a sheet-pin
    # stub, one carrying a plain local label -- they must stay separate nets.
    wires = [
        {"x1": 0, "y1": 0, "x2": 10, "y2": 0},
        {"x1": 0, "y1": 20, "x2": 10, "y2": 20},
    ]
    labels = [
        {"name": "X", "type": "hierarchical_label", "x": 5, "y": 0,
         "_sheet": 0, "_is_sheet_pin": True},
        _label("X", 5, 20),
    ]
    comps = [_comp("U1", 10, 0), _comp("U2", 10, 20)]
    nets = build_net_map(comps, wires, labels, [], [], [])
    u1_net = next(k for k, v in nets.items()
                  if any(p["component"] == "U1" for p in v["pins"]))
    u2_net = next(k for k, v in nets.items()
                  if any(p["component"] == "U2" for p in v["pins"]))
    assert u1_net != u2_net, (
        "sheet-pin label must NOT join the same-name local label's net")
