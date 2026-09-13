"""SP-001 / GitHub PR #43 (danielboston38) — two-pin components with both
pins on one net are reported by `detect_shorted_two_pin_components`.
(The PR used rule_id SH-001; renamed at merge because the EMC skill already
owns SH-001 and the SH- prefix maps to the layout stage.)

The condition was already computed and discarded: `index_two_pin_components`
(detector_helpers.py) skips a two-pin part whose pins share a net so the
divider / RC / pull-up / termination detectors never see a degenerate
topology, but nothing reported the part. SP-001 emits one `warning` finding
per such part (`confidence=deterministic`, `evidence_source=topology`).

The review round on the PR added three guards that these tests pin down:

* exactly-two-pin guard -- `get_two_pin_nets()` reads pins "1"/"2" without a
  pin-count check, so without the guard a rheostat-wired pot, a dual-anode
  diode symbol, an ESD array or a passive pack whose pins 1 and 2 share a net
  would fire;
* the component type string is `ferrite_bead` (what `classify_component`
  emits), not bare `ferrite`;
* unannotated refs ("R?") are skipped and findings are deduplicated by ref
  (a hierarchical sheet instanced n times lists the same ref n times in
  `ctx.components`).

Maintainer additions at merge: five or more hits on one net collapse into a
single net-level SP-001 finding (`confidence=heuristic`, components = all
refs) -- on the corpus that pattern is the net map having merged two rails
(KH-403/404 class), not N real shorts; and SP-001 is in the schematic stage.

Fixtures hand-build an `AnalysisContext` mirroring the real producer shapes:
`components[]` dicts carry `reference / value / type / lib_id / dnp`
(analyze_schematic.py parse_symbol_instances), `pin_net` is
`{(ref, pin_number): (net_name, net_info)}` (build_pin_to_net_map), and
`ref_pins` / `parsed_values` are derived in `AnalysisContext.__post_init__`
exactly as in production.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import AnalysisContext
from signal_detectors import detect_shorted_two_pin_components


def _comp(ref, value, ctype, lib_id="Device:R", dnp=False):
    return {"reference": ref, "value": value, "type": ctype,
            "lib_id": lib_id, "footprint": "", "dnp": dnp, "in_bom": True}


def _ctx(components, pins):
    """pins: {ref: {pin_number: net_name}} -> real pin_net / nets shapes."""
    nets = {}
    for ref, pinmap in pins.items():
        for num, net in pinmap.items():
            nets.setdefault(net, {"pins": []})["pins"].append(
                {"component": ref, "pin_number": num, "pin_name": "~",
                 "pin_type": "passive", "x": 0.0, "y": 0.0})
    pin_net = {}
    for net, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net, info)
    return AnalysisContext(components=components, nets=nets,
                           lib_symbols={}, pin_net=pin_net)


def _sp001(ctx):
    findings = detect_shorted_two_pin_components(ctx)
    assert all(f["rule_id"] == "SP-001" for f in findings)
    return findings


def test_genuine_two_pin_short_fires():
    ctx = _ctx([_comp("R1", "10k", "resistor")],
               {"R1": {"1": "SWCLK", "2": "SWCLK"}})
    findings = _sp001(ctx)
    assert len(findings) == 1
    assert findings[0]["components"] == ["R1"]
    assert findings[0]["nets"] == ["SWCLK"]


def test_finding_envelope_fields():
    ctx = _ctx([_comp("R1", "10k", "resistor")],
               {"R1": {"1": "SWCLK", "2": "SWCLK"}})
    f = _sp001(ctx)[0]
    assert f["detector"] == "detect_shorted_two_pin_components"
    assert f["rule_id"] == "SP-001"
    assert f["severity"] == "warning"
    assert f["confidence"] == "deterministic"
    assert f["evidence_source"] == "topology"
    assert f["category"] == "signal"
    assert "R1" in f["summary"] and "SWCLK" in f["summary"]
    assert f["recommendation"]


def test_three_pin_pot_with_pins_1_and_2_shared_does_not_fire():
    # Rheostat-wired potentiometer: wiper (2) tied to one end (1).
    ctx = _ctx([_comp("RV1", "10k", "resistor", lib_id="Device:R_Potentiometer")],
               {"RV1": {"1": "A", "2": "A", "3": "B"}})
    assert _sp001(ctx) == []


def test_shorted_ferrite_bead_fires():
    # classify_component emits "ferrite_bead"; the first PR revision used
    # bare "ferrite" and silently excluded every bead.
    ctx = _ctx([_comp("FB1", "600R", "ferrite_bead", lib_id="Device:FerriteBead")],
               {"FB1": {"1": "+5V", "2": "+5V"}})
    findings = _sp001(ctx)
    assert len(findings) == 1
    assert findings[0]["components"] == ["FB1"]


def test_unannotated_ref_is_skipped():
    ctx = _ctx([_comp("R?", "10k", "resistor")],
               {"R?": {"1": "GND", "2": "GND"}})
    assert _sp001(ctx) == []


def test_sheet_instanced_ref_reports_once():
    # A hierarchical sheet instanced twice lists the same ref twice in
    # ctx.components; the shared pin_net entry makes both look shorted.
    comps = [_comp("R1104", "4k7", "resistor"), _comp("R1104", "4k7", "resistor")]
    ctx = _ctx(comps, {"R1104": {"1": "SCL", "2": "SCL"}})
    findings = _sp001(ctx)
    assert len(findings) == 1
    assert findings[0]["components"] == ["R1104"]


def test_zero_ohm_link_excluded():
    ctx = _ctx([_comp("R5", "0R", "resistor")],
               {"R5": {"1": "GND", "2": "GND"}})
    assert _sp001(ctx) == []


def test_dnp_part_excluded():
    ctx = _ctx([_comp("C7", "100n", "capacitor", lib_id="Device:C", dnp=True)],
               {"C7": {"1": "+3V3", "2": "+3V3"}})
    assert _sp001(ctx) == []


def test_net_tie_lib_id_excluded():
    ctx = _ctx([_comp("NT1", "NetTie", "resistor", lib_id="Device:NetTie_2")],
               {"NT1": {"1": "GNDA", "2": "GNDA"}})
    assert _sp001(ctx) == []


def test_normal_two_net_resistor_no_finding():
    ctx = _ctx([_comp("R2", "4k7", "resistor")],
               {"R2": {"1": "+3V3", "2": "SDA"}})
    assert _sp001(ctx) == []


def test_five_hits_on_one_net_collapse_into_one_finding():
    comps = [_comp(f"C{i}", "100n", "capacitor", lib_id="Device:C") for i in range(1, 6)]
    ctx = _ctx(comps, {f"C{i}": {"1": "GND", "2": "GND"} for i in range(1, 6)})
    findings = _sp001(ctx)
    assert len(findings) == 1
    f = findings[0]
    assert f["components"] == ["C1", "C2", "C3", "C4", "C5"]
    assert f["nets"] == ["GND"]
    assert f["confidence"] == "heuristic"
    assert f["severity"] == "warning"
    assert f["component_count"] == 5
    assert "5 two-pin components" in f["summary"]


def test_four_hits_on_one_net_stay_individual():
    comps = [_comp(f"C{i}", "100n", "capacitor", lib_id="Device:C") for i in range(1, 5)]
    ctx = _ctx(comps, {f"C{i}": {"1": "GND", "2": "GND"} for i in range(1, 5)})
    findings = _sp001(ctx)
    assert len(findings) == 4
    assert all(f["confidence"] == "deterministic" for f in findings)


def test_collapse_is_per_net():
    # 5 on GND collapse; a lone short on SDA stays individual.
    comps = [_comp(f"C{i}", "100n", "capacitor", lib_id="Device:C") for i in range(1, 6)]
    comps.append(_comp("R9", "4k7", "resistor"))
    pins = {f"C{i}": {"1": "GND", "2": "GND"} for i in range(1, 6)}
    pins["R9"] = {"1": "SDA", "2": "SDA"}
    findings = _sp001(_ctx(comps, pins))
    assert len(findings) == 2
    kinds = {f["nets"][0]: f["confidence"] for f in findings}
    assert kinds == {"GND": "heuristic", "SDA": "deterministic"}


def test_sp001_is_in_schematic_stage():
    from output_filters import assign_stages
    ctx = _ctx([_comp("R1", "10k", "resistor")], {"R1": {"1": "SWCLK", "2": "SWCLK"}})
    findings = _sp001(ctx)
    tagged = assign_stages(findings) or findings
    assert tagged[0]["stages"] == ["schematic"]


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
