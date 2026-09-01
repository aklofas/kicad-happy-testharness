"""KH-402 / GitHub #41 — no-connect markers must not union with wires
passing mid-span beneath them.

`build_net_map`'s no-connect handling used to call both `add_point()`
*and* `union_with_overlapping_wires()` for every no-connect marker. The
latter unions the marker's coordinate key with every wire segment the
marker's (x, y) lies on -- including a wire that merely passes *under*
the marker without an endpoint there. KiCad does not treat "NC marker
sitting on top of a wire's midpoint" as a connection, so that union
dragged the NC'd pin into the wire's net and (because a no-connect
marker sets `no_connect: True` on the whole absorbing net) mislabeled
the wire's real net as intentionally-unconnected too.

Post-fix (`skills/kicad/scripts/analyze_schematic.py` ~1583-1595) the
no-connect loop calls `add_point()` only. `add_point()` still shares
the coordinate key with a pin or *wire endpoint* sitting at the exact
same point (both hash through the same `key(x, y, sheet)`), which is
all the legitimate "NC marker directly on a pin/endpoint" absorption
needs -- only the *mid-span* union is removed.

Fixtures hand-build minimal component/wire/no_connect dicts mirroring
the real producer field names (reference/value/type/_sheet/pins[...],
x1/y1/x2/y2/_sheet, x/y/_sheet) per repo convention for targeted
regression tests (see test_kh357_be001_rect.py, test_kh359_kh360_netmap.py).
"""

TIER = "unit"

import json
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


def _net_for(nets, ref):
    return next(k for k, v in nets.items()
                if any(p["component"] == ref for p in v["pins"]))


def test_nc_marker_does_not_union_with_midspan_wire():
    """The bug: an NC marker sitting mid-span on a wire must NOT drag the
    NC'd pin into the wire's net (and must not mislabel that net as
    no_connect). Pin U1 + NC marker both sit at (5,0), which is the
    midpoint of wire (0,0)->(10,0); pin U2 sits on the wire's (0,0)
    endpoint."""
    comps = [_comp("U1", 5, 0), _comp("U2", 0, 0)]
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0}]
    no_connects = [{"x": 5, "y": 0}]

    nets = build_net_map(comps, wires, [], [], [], no_connects)

    assert len(nets) == 2, f"expected 2 nets (NC'd pin split from the wire), got {nets}"
    u1_net, u2_net = _net_for(nets, "U1"), _net_for(nets, "U2")
    assert u1_net != u2_net, "NC'd pin must not share a net with the mid-span wire"
    assert nets[u1_net]["no_connect"] is True, "NC'd pin's own net must be tagged no_connect"
    assert nets[u2_net]["no_connect"] is False, (
        "the wire's net must NOT be tagged no_connect just because an "
        "NC marker happened to sit mid-span on top of it"
    )
    assert [p["component"] for p in nets[u1_net]["pins"]] == ["U1"]
    assert [p["component"] for p in nets[u2_net]["pins"]] == ["U2"]


def test_nc_marker_at_wire_endpoint_stays_connected():
    """An NC marker sitting exactly on a wire ENDPOINT (coincident with a
    pin there) still shares that coordinate key via add_point() -- the
    pin stays joined to the rest of the wire's net, and the net is
    tagged no_connect. This is the legitimate absorption case the fix
    must preserve."""
    comps = [_comp("U1", 0, 0), _comp("U2", 10, 0)]
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0}]
    no_connects = [{"x": 0, "y": 0}]

    nets = build_net_map(comps, wires, [], [], [], no_connects)

    assert len(nets) == 1, f"expected 1 net (endpoint NC absorption), got {nets}"
    net = next(iter(nets.values()))
    assert net["no_connect"] is True
    assert {p["component"] for p in net["pins"]} == {"U1", "U2"}


def test_isolated_nc_pin_no_crash_no_phantom_nets():
    """An NC marker on a pin with no wire anywhere: the pin's net is
    tagged no_connect, no crash, and no phantom extra net is created."""
    comps = [_comp("U1", 0, 0)]
    wires = []
    no_connects = [{"x": 0, "y": 0}]

    nets = build_net_map(comps, wires, [], [], [], no_connects)

    assert len(nets) == 1, f"expected exactly 1 net, got {nets}"
    net = next(iter(nets.values()))
    assert net["no_connect"] is True
    assert [p["component"] for p in net["pins"]] == ["U1"]


def test_plain_midspan_pin_stays_unconnected_without_nc():
    """Pre-existing behavior guard (not the fix itself): a plain pin
    sitting mid-span on a wire, with NO no-connect marker involved,
    must stay unconnected from that wire -- confirms the fix didn't
    change ordinary mid-span pin behavior."""
    comps = [_comp("U1", 5, 0), _comp("U2", 0, 0)]
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0}]

    nets = build_net_map(comps, wires, [], [], [], [])

    assert len(nets) == 2, f"expected 2 nets (mid-span pin stays isolated), got {nets}"
    assert _net_for(nets, "U1") != _net_for(nets, "U2")


def test_determinism_repeated_build():
    """Repeated builds of the bug-case fixture must be byte-identical."""
    comps = [_comp("U1", 5, 0), _comp("U2", 0, 0)]
    wires = [{"x1": 0, "y1": 0, "x2": 10, "y2": 0}]
    no_connects = [{"x": 5, "y": 0}]

    a = build_net_map(comps, wires, [], [], [], no_connects)
    b = build_net_map(comps, wires, [], [], [], no_connects)

    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


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
