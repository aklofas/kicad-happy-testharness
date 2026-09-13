"""KH-374 — `analyze_sleep_current` ignores real EN connectivity and drops
battery-rail voltages.

Two defects in the pre-fix tree at v2.2.1 (main @ 3cf837b):

1. `analyze_sleep_current` decided whether a regulator's output rail is
   "disableable" (and therefore zeroable during sleep) purely from whether
   the part has a pin NAMED "EN"/"ENABLE"/"SHDN"/etc — it never checked
   whether that pin is actually driven low/floating/high by anything.
   `analyze_power_sequencing` (same file) already computes exactly this
   from real net connectivity (`en_source` — "always_on" / "disabled" /
   "floating" / "controlled") but the two functions never talked: the
   caller ran `analyze_sleep_current` BEFORE `analyze_power_sequencing`.
   Net effect: a regulator whose EN is tied straight to its own input rail
   (i.e. always enabled, e.g. `en_source == "always_on"`) had every
   downstream divider/pull-up on its output rail — and its own quiescent
   current entry — wrongly zeroed as "can be disabled during sleep",
   because the chip merely *has* an EN pin.

2. Rail-voltage resolution only tried `_estimate_rail_voltage(name)`,
   which parses a number out of the net NAME (`+3V3` -> 3.3) or matches a
   couple of hardcoded patterns (VBUS/USB -> 5V). A battery rail named
   `+BATT` or `VBAT` has no parseable voltage and isn't VBUS/USB, so it
   resolved to `None` and every resistor on it was silently dropped from
   the audit even though `signal_analysis["rail_voltages"]` (built by
   `analyze_signal_paths`) or a regulator's `estimated_vout` may already
   know the real voltage, and a bare battery-name rail has an obvious
   nominal default (3.7V single-cell Li-ion/LiPo).

The fix (analyze_schematic.py `analyze_sleep_current`): accept an optional
`power_sequencing` argument (the caller now runs `analyze_power_sequencing`
first and passes its result in). When given, a rail/regulator only counts
as disableable if `analyze_power_sequencing` says its EN is actually
`"controlled"` — an `"always_on"` EN keeps every path on that rail "always
conducting" / "always-on" with `realistic_uA == current_uA`. Passing
`power_sequencing=None` preserves the old EN-pin-NAME heuristic verbatim
(back-compat for any other caller). A new `_rail_voltage(name)` closure
tries, in order: `_estimate_rail_voltage(name)` -> the caller-supplied
`signal_analysis["rail_voltages"]` (keyed by the UUID-stripped name) ->
a regulator entry's `estimated_vout` whose `output_rail == name` -> a
3.7V default for names matching `^\\+?(BATT?|VBATT?|BATTERY|BAT\\+)$`.

Fixtures hand-build an `AnalysisContext` mirroring the real producer
shapes: `pin_net` is `{(ref, pin_number): (net_name, net_info)}`, nets
carry `pins[]` dicts with `component/pin_number/pin_name/pin_type/x/y`
(see test_sp001_shorted_two_pin.py, test_kh375_power_budget_loads.py), and
a component's own physical `pins[]` (used to detect an EN-NAMED pin, the
old heuristic) carry `number/name/type/x/y` (analyze_schematic.py
`compute_pin_positions`).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import AnalysisContext  # noqa: E402
from analyze_schematic import analyze_sleep_current  # noqa: E402


def _pin(ref, num, ptype="passive", name="~"):
    return {"component": ref, "pin_number": num, "pin_name": name,
            "pin_type": ptype, "x": 0.0, "y": 0.0}


def _ctx(components, nets):
    pin_net = {}
    for net, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net, info)
    return AnalysisContext(components=components, nets=nets,
                           lib_symbols={}, pin_net=pin_net)


# --- (a)/(b): divider on a regulator's output rail, gated by en_source ---

def _divider_on_3v3_fixture():
    """R1/R2 form a feedback-style divider from +3V3 down to GND via FB."""
    components = [
        {"reference": "R1", "value": "10k", "type": "resistor", "lib_id": "Device:R"},
        {"reference": "R2", "value": "10k", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "+3V3": {"pins": [_pin("R1", "1")]},
        "FB": {"pins": [_pin("R1", "2"), _pin("R2", "1")]},
        "GND": {"pins": [_pin("R2", "2")]},
    }
    ctx = _ctx(components, nets)
    signal_analysis = {"power_regulators": [], "rail_voltages": {}}
    return ctx, signal_analysis


def _divider_entries(result):
    entries = result.get("rails", {}).get("+3V3", {}).get("current_paths", [])
    return [e for e in entries if e["type"] == "divider"]


def test_a_divider_stays_always_conducting_when_en_source_always_on():
    ctx, signal_analysis = _divider_on_3v3_fixture()
    power_sequencing = {"dependencies": [
        {"regulator": "U1", "output_rail": "+3V3", "en_source": "always_on"},
    ]}
    result = analyze_sleep_current(ctx, signal_analysis, power_sequencing)
    entries = _divider_entries(result)
    assert entries, "expected a divider entry on +3V3"
    for e in entries:
        assert e["likely_state"] == "always conducting"
        assert e["realistic_uA"] == e["current_uA"]


def test_b_divider_zeroed_when_en_source_controlled():
    ctx, signal_analysis = _divider_on_3v3_fixture()
    power_sequencing = {"dependencies": [
        {"regulator": "U1", "output_rail": "+3V3", "en_source": "controlled"},
    ]}
    result = analyze_sleep_current(ctx, signal_analysis, power_sequencing)
    entries = _divider_entries(result)
    assert entries, "expected a divider entry on +3V3"
    for e in entries:
        assert e["likely_state"] == "rail disabled during sleep"
        assert e["realistic_uA"] == 0.0


# --- (c): regulator_iq entry gated by en_source, not EN-pin presence -----

def test_c_regulator_iq_stays_always_on_when_en_source_always_on():
    components = [
        {"reference": "U1", "value": "XC6206", "type": "ic",
         "lib_id": "Regulator_Linear:XC6206",
         "pins": [
             {"number": "1", "name": "GND", "type": "power_in", "x": 0.0, "y": 0.0},
             {"number": "2", "name": "EN", "type": "input", "x": 0.0, "y": 0.0},
             {"number": "3", "name": "VOUT", "type": "power_out", "x": 0.0, "y": 0.0},
             {"number": "4", "name": "VIN", "type": "power_in", "x": 0.0, "y": 0.0},
         ]},
    ]
    ctx = _ctx(components, {})
    signal_analysis = {
        "power_regulators": [
            {"ref": "U1", "value": "XC6206", "output_rail": "+3V3", "topology": "LDO"},
        ],
        "rail_voltages": {},
    }
    power_sequencing = {"dependencies": [
        {"regulator": "U1", "output_rail": "+3V3", "en_source": "always_on"},
    ]}
    result = analyze_sleep_current(ctx, signal_analysis, power_sequencing)
    entries = result["rails"]["+3V3"]["current_paths"]
    iq_entries = [e for e in entries if e["type"] == "regulator_iq" and e["ref"] == "U1"]
    assert iq_entries, "expected a regulator_iq entry for U1"
    assert iq_entries[0]["has_enable_pin"] is True  # part physically has an EN pin
    assert iq_entries[0]["likely_state"] == "always-on"
    assert iq_entries[0]["realistic_uA"] == iq_entries[0]["current_uA"]


# --- (d): battery-rail voltage resolution --------------------------------

def _battery_resistor_fixture():
    components = [
        {"reference": "R3", "value": "100k", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "+BATT": {"pins": [_pin("R3", "1")]},
        "GND": {"pins": [_pin("R3", "2")]},
    }
    return _ctx(components, nets)


def _r3_entry(result):
    entries = result.get("rails", {}).get("+BATT", {}).get("current_paths", [])
    r3 = [e for e in entries if e["ref"] == "R3"]
    assert r3, "expected an R3 entry on +BATT"
    return r3[0]


def test_d_battery_rail_defaults_to_3v7_when_unresolvable():
    ctx = _battery_resistor_fixture()
    signal_analysis = {"power_regulators": [], "rail_voltages": {}}
    result = analyze_sleep_current(ctx, signal_analysis)
    assert _r3_entry(result)["rail_voltage"] == 3.7


def test_d_battery_rail_uses_signal_analysis_rail_voltages_when_present():
    ctx = _battery_resistor_fixture()
    signal_analysis = {"power_regulators": [], "rail_voltages": {"+BATT": 4.2}}
    result = analyze_sleep_current(ctx, signal_analysis)
    assert _r3_entry(result)["rail_voltage"] == 4.2


# --- fix round 1: SLEEP_PULL_MIN_OHM shunt floor --------------------------
#
# KH-374's battery-rail voltage fix (test (d) above) has a side effect: a
# real board (bastian2001/LiPo-Charger-Hardware) has a 5 mOhm current-sense
# shunt (R6) in series with VBAT, one side on the VBAT rail and the other on
# a sense net with nothing else on it. Before this fix, VBAT's voltage was
# unresolvable so the whole entry was silently dropped; after the (d) fix,
# VBAT resolves to 3.7V and the pre-existing pull-up "worst-case V/R"
# heuristic (which never checked resistance magnitude) reported a
# nonsensical 3.7V / 0.005 Ohm = 740,000,000 uA (740 A) pull-up current.
# `SLEEP_PULL_MIN_OHM` (100 Ohm) gates that classification: below it, a
# resistor between a rail and a signal net is a shunt/sense element, not a
# pull, and gets no entry at all rather than a guessed current.

def _pullup_fixture(r_value):
    components = [
        {"reference": "R6", "value": r_value, "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "VBAT": {"pins": [_pin("R6", "1")]},
        "SENSE": {"pins": [_pin("R6", "2")]},
    }
    return _ctx(components, nets)


def _pullup_entries(result, rail="VBAT"):
    entries = result.get("rails", {}).get(rail, {}).get("current_paths", [])
    return [e for e in entries if e["type"] == "pull_up"]


def test_shunt_resistor_below_floor_produces_no_pull_up_entry():
    ctx = _pullup_fixture("5m")  # 0.005 ohm current-sense shunt, as on R6
    signal_analysis = {"power_regulators": [], "rail_voltages": {}}
    result = analyze_sleep_current(ctx, signal_analysis)
    assert _pullup_entries(result) == []


def test_normal_pullup_resistor_above_floor_still_produces_entry():
    ctx = _pullup_fixture("10k")
    signal_analysis = {"power_regulators": [], "rail_voltages": {}}
    result = analyze_sleep_current(ctx, signal_analysis)
    entries = _pullup_entries(result)
    assert entries, "expected a pull_up entry for a normal 10k resistor"
    assert entries[0]["ref"] == "R6"


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
