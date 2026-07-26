"""Unit tests for bus_resolver.expand_bus_name (GH #25 phase 1)."""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from bus_resolver import expand_bus_name, BusGraph, match_ports


def test_vector_ascending_descending_and_singleton():
    assert expand_bus_name("D[0..3]") == ["D0", "D1", "D2", "D3"]
    assert expand_bus_name("A[15..13]") == ["A15", "A14", "A13"]
    assert expand_bus_name("D[3..3]") == ["D3"]


def test_vector_prefix_may_contain_dots():
    # Real label on the Incrementer golden board.
    assert expand_bus_name("Incremented0.Out[0..1]") == [
        "Incremented0.Out0", "Incremented0.Out1"]


def test_group_and_labeled_group():
    assert expand_bus_name("{SDA SCL}") == ["SDA", "SCL"]
    assert expand_bus_name("PORT{SDA SCL}") == ["PORT.SDA", "PORT.SCL"]


def test_nested_group_vectors():
    assert expand_bus_name("{CLK D[0..2]}") == ["CLK", "D0", "D1", "D2"]
    assert expand_bus_name("B{CLK D[0..1]}") == ["B.CLK", "B.D0", "B.D1"]


def test_aliases_resolve_inside_groups_only():
    aliases = {"PHASES": ["A", "B", "C"],
               "DIFF_PHASES": ["A+", "A-", "B+", "B-"]}
    # Real OpenMD golden-board constructs:
    assert expand_bus_name("{PHASES}", aliases) == ["A", "B", "C"]
    assert expand_bus_name("SW{PHASES}", aliases) == ["SW.A", "SW.B", "SW.C"]
    assert expand_bus_name("{DIFF_PHASES}", aliases) == ["A+", "A-", "B+", "B-"]
    # A bare label that merely equals an alias name is a NET, not a bus.
    assert expand_bus_name("PHASES", aliases) is None


def test_kicad_text_markup_is_not_a_group_bus():
    # Real labels on the Incrementer/OpenMD boards: subscript/overline markup.
    # KiCad 7+ overline is ~{FOO}; KiCad 6 wrote a brace-free leading ~FOO —
    # both must stay non-bus across every supported format era (5-10).
    for name in ("C_{Out}", "C_{in}", "~{OE}", "V_{ANA}", "Carry_{Out}",
                 "~OE", "~RESET"):
        assert expand_bus_name(name) is None


def test_markup_wrapped_vector_expands_and_rewraps():
    # KiCad overline/subscript markup wrapping a vector distributes over each
    # member: the markup stays on every expanded member. Real m68k-hbc labels.
    assert expand_bus_name("~{IPL[0..2]}") == ["~{IPL0}", "~{IPL1}", "~{IPL2}"]
    assert expand_bus_name("SIMM_~{CAS[0..3]}") == [
        "SIMM_~{CAS0}", "SIMM_~{CAS1}", "SIMM_~{CAS2}", "SIMM_~{CAS3}"]
    assert expand_bus_name("~{RAS[0..7]}") == [f"~{{RAS{i}}}" for i in range(8)]
    # A markup wrapper around a NON-bus content stays a plain net.
    assert expand_bus_name("~{IPL}") is None
    assert expand_bus_name("SIMM_~{CAS}") is None


def test_non_bus_and_malformed():
    for name in ("GND", "D0", "D[0..7]x", "D[0..]", "D[a..b]", "{ }", "", "{}"):
        assert expand_bus_name(name) is None


def _bg(bus_wires, bus_entries=(), aliases=None):
    return BusGraph(0, list(bus_wires), list(bus_entries), aliases or {})


def test_bus_segments_cluster_by_endpoint_and_midpoint_touch():
    g = _bg([
        {"x1": 0, "y1": 0, "x2": 10, "y2": 0},
        {"x1": 10, "y1": 0, "x2": 10, "y2": 10},   # shares endpoint
        {"x1": 0, "y1": 50, "x2": 10, "y2": 50},   # separate cluster
        {"x1": 5, "y1": 0, "x2": 5, "y2": -10},    # T-taps first segment mid-span
    ])
    assert g.add_bus_label("D[0..3]", 5, 0)
    assert g.add_bus_label("E[0..1]", 5, 50)
    g.finalize()
    # same cluster for segments 0,1,3; different for segment 2:
    c_main = g.cluster_at(5, -10)
    assert c_main == g.cluster_at(10, 10) == g.cluster_at(0, 0)
    assert g.cluster_at(0, 50) != c_main
    assert g.cluster_member_set(c_main) == {"D0", "D1", "D2", "D3"}


def test_entry_taps_resolve_wire_side_end():
    # Entry at (5,0) on the bus, other end (7,-2) on the wire side.
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}],
            [{"x": 5, "y": 0, "dx": 2, "dy": -2}])
    assert g.add_bus_label("D[0..1]", 2, 0)
    g.finalize()
    assert len(g.taps) == 1
    t = g.taps[0]
    assert (t["x"], t["y"]) == (7, -2)
    assert g.cluster_member_set(t["cluster"]) == {"D0", "D1"}


def test_entry_touching_no_bus_is_unresolved():
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}],
            [{"x": 50, "y": 50, "dx": 2, "dy": 2}])
    g.finalize()
    assert not g.taps
    assert any("entry" in u["reason"] for u in g.unresolved)


def test_label_off_bus_returns_false():
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert not g.add_bus_label("D[0..3]", 99, 99)


def test_mid_sheet_relabel_shares_member_names_only():
    # Two labels on ONE cluster: members union by NAME (KiCad rule 4 —
    # no positional relabel mid-sheet).
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert g.add_bus_label("D[0..3]", 2, 0)
    assert g.add_bus_label("X[0..1]", 8, 0)
    g.finalize()
    cid = g.cluster_at(0, 0)
    assert g.cluster_member_set(cid) == {"D0", "D1", "D2", "D3", "X0", "X1"}
    assert g.cluster_ordered(cid, 4) == ["D0", "D1", "D2", "D3"]
    assert g.cluster_ordered(cid, 2) == ["X0", "X1"]
    assert g.cluster_ordered(cid, 8) is None


def test_cluster_ordered_falls_back_to_hier_label():
    # A cluster whose only bus label is a hierarchical one (no local label)
    # still has a canonical ordering — the hier label names the local wire, so
    # co-clustered sheet pins map positionally to it (openmd's {PHASES} feeding
    # OUT{PHASES}/V{PHASES} pins).
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert g.add_bus_label("D[0..3]", 5, 0, role="hier")
    g.finalize()
    cid = g.cluster_at(0, 0)
    assert g.cluster_ordered(cid, 4) == ["D0", "D1", "D2", "D3"]


def test_cluster_ordered_prefers_local_over_hier():
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert g.add_bus_label("L[0..3]", 2, 0, role="local")
    assert g.add_bus_label("H[0..3]", 8, 0, role="hier")
    g.finalize()
    cid = g.cluster_at(0, 0)
    assert g.cluster_ordered(cid, 4) == ["L0", "L1", "L2", "L3"]


def test_anonymous_cluster_has_none_member_set():
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    g.finalize()
    assert g.cluster_member_set(g.cluster_at(0, 0)) is None


def test_duplicate_identical_bus_labels_are_not_ambiguous():
    # Same bus labeled twice along one wire for readability — common real
    # KiCad pattern. Ambiguity is two DIFFERENT expansions of the same
    # width, not a repeated identical one.
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert g.add_bus_label("D[0..3]", 2, 0)
    assert g.add_bus_label("D[0..3]", 8, 0)
    g.finalize()
    cid = g.cluster_at(0, 0)
    assert g.cluster_ordered(cid, 4) == ["D0", "D1", "D2", "D3"]
    assert g.unresolved == []


def test_different_same_width_labels_are_ambiguous():
    g = _bg([{"x1": 0, "y1": 0, "x2": 10, "y2": 0}])
    assert g.add_bus_label("D[0..3]", 2, 0)
    assert g.add_bus_label("A[0..3]", 8, 0)
    g.finalize()
    cid = g.cluster_at(0, 0)
    assert g.cluster_ordered(cid, 4) is None
    assert any("ambiguous" in u["reason"] for u in g.unresolved)


def _port(role, ns, name, members, sheet, cluster, parent_ordered=None):
    return {"role": role, "ns": ns, "name": name, "members": members,
            "sheet": sheet, "cluster": cluster,
            "parent_ordered": parent_ordered}


def test_positional_mapping_across_relabel():
    # Parent bus Increment[0..3] reaches pin Inc[0..3]; child hier label
    # Inc[0..3]. Mapping is by index: Increment2 <-> Inc2 (spec rule 5).
    pin = _port("pin", "/X", "Inc[0..3]",
                ["Inc0", "Inc1", "Inc2", "Inc3"], 0, 7,
                parent_ordered=["Increment0", "Increment1",
                                "Increment2", "Increment3"])
    hier = _port("hier", "/X", "Inc[0..3]",
                 ["Inc0", "Inc1", "Inc2", "Inc3"], 1, 3)
    unresolved = []
    pairs = match_ports([pin], [hier], unresolved)
    assert ((0, 7, "Increment2"), (1, 3, "Inc2")) in pairs
    assert len(pairs) == 4 and not unresolved


def test_per_instance_ports_do_not_cross():
    # Two instances of the same child: ns differs, pairs stay separate.
    mk = lambda ns, sheet: (_port("pin", ns, "In[0..1]", ["In0", "In1"], 0,
                                  sheet, parent_ordered=[f"P{sheet}_0", f"P{sheet}_1"]),
                            _port("hier", ns, "In[0..1]", ["In0", "In1"], sheet, 0))
    p1, h1 = mk("/A", 1); p2, h2 = mk("/B", 2)
    pairs = match_ports([p1, p2], [h1, h2], [])
    assert ((0, 1, "P1_0"), (1, 0, "In0")) in pairs
    assert ((0, 2, "P2_0"), (2, 0, "In0")) in pairs
    assert not any(a[0] == 1 and b[0] == 2 for a, b in pairs)


def test_width_mismatch_flags_no_partial_map():
    pin = _port("pin", "/X", "D[0..7]", [f"D{i}" for i in range(8)], 0, 1,
                parent_ordered=["A0", "A1"])   # parent bus is 2 wide
    hier = _port("hier", "/X", "D[0..7]", [f"D{i}" for i in range(8)], 1, 1)
    unresolved = []
    assert match_ports([pin], [hier], unresolved) == []
    assert unresolved and "width" in unresolved[0]["reason"]


def test_missing_counterpart_flags():
    pin = _port("pin", "/X", "D[0..1]", ["D0", "D1"], 0, 1,
                parent_ordered=["D0", "D1"])
    unresolved = []
    assert match_ports([pin], [], unresolved) == []
    assert unresolved


def test_hier_port_without_pin_counterpart_flags():
    # Mirror of test_missing_counterpart_flags: a hier label with no
    # matching sheet pin is also an unresolved condition (brief step 3,
    # "missing counterpart in either direction").
    hier = _port("hier", "/X", "D[0..1]", ["D0", "D1"], 1, 3)
    unresolved = []
    assert match_ports([], [hier], unresolved) == []
    assert unresolved
    assert "D[0..1]" in unresolved[0]["reason"]


def test_duplicate_hier_ports_first_wins_plus_note():
    # Two hier ports share (ns, name) — malformed. The pairing uses the
    # FIRST one's sheet/cluster, and a duplicate note is appended.
    pin = _port("pin", "/X", "D[0..1]", ["D0", "D1"], 0, 1,
                parent_ordered=["D0", "D1"])
    hier1 = _port("hier", "/X", "D[0..1]", ["D0", "D1"], 1, 3)
    hier2 = _port("hier", "/X", "D[0..1]", ["D0", "D1"], 2, 9)
    unresolved = []
    pairs = match_ports([pin], [hier1, hier2], unresolved)
    assert ((0, 1, "D0"), (1, 3, "D0")) in pairs
    assert ((0, 1, "D1"), (1, 3, "D1")) in pairs
    assert len(pairs) == 2
    assert any("duplicate" in u["reason"] for u in unresolved)
