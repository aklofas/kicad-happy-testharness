"""KH-375 — `analyze_power_budget` drops loads it should count.

Three defects in the pre-fix tree at v2.2.1 (main @ 3cf837b):

1. The inner pin scan evaluated the FIRST pin `nets[net_name]["pins"]` lists
   for a component on a rail and `break`-ed after that one pin, regardless
   of whether it was the power pin. A component whose non-power pin sorts
   first in the net's pin list (e.g. a 74HC595 with `~{SRCLR}` tied to VCC
   for "always enabled", or a regulator with EN tied to VIN) was dropped
   from the rail entirely even though it has a genuine power_in pin on the
   same net.

2. Rails only got a load estimate when `is_power_net()` matched the net's
   *name* (or a `#PWR` symbol sat on it). A regulator's output rail with an
   unrecognized name (no `#PWR`, doesn't look power-y) got no loads even
   when ICs draw from it -- e.g. `3.3V` (fails the pattern; compare to
   `+3.3V` / `3V3` which pass) driven by a regulator whose
   `power_regulators` entry names it as `output_rail`.

3. Only `type == "ic"` components were counted as loads. LEDs draw real
   current (nominal 5 mA) and were invisible to `estimated_load_mA`.

The fix (analyze_schematic.py `analyze_power_budget`): build `reg_by_rail`
before the IC loop, compute `candidate_rails = power-named nets ∪
regulator output rails`, and for each `(pnum, net_name)` on an IC look up
THE ITERATED PIN specifically (`p["component"] == ref and
str(p["pin_number"]) == str(pnum)`) instead of the first pin found for
that component on the net. LEDs are walked separately into a new
`other_loads` list per rail (5 mA each), included in `estimated_load_mA`
but reported under their own key so `rails[rail]["ics"]` keeps its
existing shape.

Fixtures hand-build an `AnalysisContext` mirroring the real producer
shapes: `pin_net` is `{(ref, pin_number): (net_name, net_info)}`
(`build_pin_to_net_map`), nets carry `pins[]` dicts with
`component/pin_number/pin_name/pin_type/x/y` (see test_sp001_shorted_two_pin.py,
test_pr44_pp001_fuse_power_names.py).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import AnalysisContext  # noqa: E402
from analyze_schematic import analyze_power_budget  # noqa: E402


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


# --- (a) iterated-pin qualification -----------------------------------

def test_ic_counted_when_non_power_pin_sorts_first_on_the_rail():
    # U1 (74HC595-style): pin 1 is ~{SRCLR} (input) tied to +5V for
    # "always enabled", pin 16 is VCC (power_in), also on +5V. Pin 1
    # sorts first in the net's pin list.
    comps = [{"reference": "U1", "value": "74HC595", "type": "ic",
              "lib_id": "74xx:74HC595"}]
    nets = {
        "+5V": {"pins": [
            _pin("U1", "1", "input", "~{SRCLR}"),
            _pin("U1", "16", "power_in", "VCC"),
        ]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert [ic["ref"] for ic in result["rails"]["+5V"]["ics"]] == ["U1"]


def test_ic_still_dropped_when_only_non_power_pin_is_on_the_rail():
    # Control: if U1 truly has no power pin on the rail, it must not be
    # counted (the fix shouldn't turn into "count any IC touching the net").
    comps = [{"reference": "U1", "value": "74HC595", "type": "ic",
              "lib_id": "74xx:74HC595"}]
    nets = {
        "+5V": {"pins": [_pin("U1", "1", "input", "~{SRCLR}")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert result == {}


# --- (b) regulator-output rails with no power-looking name --------------

def test_regulator_output_rail_gets_loads_despite_failing_name_pattern():
    # "3.3V" fails is_power_net_name's pattern (no leading +, no #PWR
    # symbol on it) but a regulator names it as its output_rail.
    comps = [
        {"reference": "U2", "value": "AP2112", "type": "ic", "lib_id": "Regulator_Linear:AP2112"},
        {"reference": "U3", "value": "BME280", "type": "ic", "lib_id": "Sensor:BME280"},
    ]
    nets = {
        "3.3V": {"pins": [_pin("U3", "1", "power_in", "VDD")]},
    }
    ctx = _ctx(comps, nets)
    signal_analysis = {
        "power_regulators": [
            {"ref": "U2", "value": "AP2112", "topology": "LDO", "output_rail": "3.3V"},
        ],
    }
    result = analyze_power_budget(ctx, signal_analysis)
    assert result["rails"]["3.3V"]["ic_count"] == 1
    assert result["rails"]["3.3V"]["ics"][0]["ref"] == "U3"


# --- (c) LED loads --------------------------------------------------------

def test_led_counted_as_other_load():
    # D1 between +5V and a series resistor (not ground) -- a real load
    # on the rail, previously invisible because only ICs were counted.
    comps = [
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R1", "value": "330", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "+5V": {"pins": [_pin("D1", "1"), _pin("R1", "1")]},
        "__unnamed_1": {"pins": [_pin("D1", "2"), _pin("R1", "2")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    rail = result["rails"]["+5V"]
    assert rail["other_loads"] == [{"ref": "D1", "type": "led", "estimated_mA": 5}]
    assert rail["estimated_load_mA"] == 5


def test_led_and_ic_loads_combine_on_the_same_rail():
    comps = [
        {"reference": "U1", "value": "STM32F103", "type": "ic", "lib_id": "MCU_ST_STM32F1:STM32F103"},
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R1", "value": "330", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "+5V": {"pins": [
            _pin("U1", "1", "power_in", "VDD"),
            _pin("D1", "1"), _pin("R1", "1"),
        ]},
        "__unnamed_1": {"pins": [_pin("D1", "2"), _pin("R1", "2")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    rail = result["rails"]["+5V"]
    assert rail["ic_count"] == 1
    assert rail["other_loads"] == [{"ref": "D1", "type": "led", "estimated_mA": 5}]
    assert rail["estimated_load_mA"] == 50 + 5  # STM32F103 default keyword est. + LED


def test_no_other_loads_key_when_no_led_on_rail():
    comps = [{"reference": "U1", "value": "STM32F103", "type": "ic",
              "lib_id": "MCU_ST_STM32F1:STM32F103"}]
    nets = {"+5V": {"pins": [_pin("U1", "1", "power_in", "VDD")]}}
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert "other_loads" not in result["rails"]["+5V"]


# --- Round 1: LED behind a series resistor, LDO dissipation uses total load ---
#
# The A/B on the 74HC595/BME280/RoboMausV2 tracker boards showed the direct
# LED-on-rail rule never fires on real boards: every sampled LED sits one hop
# behind a series resistor (rail -> R -> LED -> GND), not with a pin directly
# on the rail net. `analyze_power_budget` now walks one resistor hop from
# either LED pin looking for a candidate rail on the resistor's far end, and
# stamps the entry with `"via": "<Rref>"` when that hop was used. Also: the
# LDO thermal-dissipation calc used to divide by `total_ic_mA` only, ignoring
# `other_loads` -- it now uses the rail's full `estimated_load_mA` so
# KH-386/thermal see the same number `power_budget` reports.

def test_led_behind_series_resistor_is_attributed_to_the_rail():
    # +5V -- R1 -- LED_A -- D1 -- GND (the common real-board wiring).
    comps = [
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R1", "value": "330", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "+5V": {"pins": [_pin("R1", "1")]},
        "LED_A": {"pins": [_pin("R1", "2"), _pin("D1", "1")]},
        "GND": {"pins": [_pin("D1", "2")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert result["rails"]["+5V"]["other_loads"] == [
        {"ref": "D1", "type": "led", "estimated_mA": 5, "via": "R1"}]


def test_led_behind_resistor_to_a_signal_net_is_not_counted():
    # Same shape, but the resistor's far end is a signal net, not a rail --
    # must not be mistaken for a power load.
    comps = [
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R1", "value": "330", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "SIG_NET": {"pins": [_pin("R1", "1")]},
        "LED_A": {"pins": [_pin("R1", "2"), _pin("D1", "1")]},
        "GND": {"pins": [_pin("D1", "2")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert result == {}


def test_led_reachable_via_two_rails_picks_lexicographically_first():
    # Minor (reviewer): the tie-break when an LED's anchor net is reachable
    # via resistors to more than one candidate rail must be deterministic.
    # R1 leads to +5V, R2 leads to +3.3V, both from the LED's own net.
    # sorted(reachable_via) puts "+3.3V" first ('+3' < '+5'), so that's the
    # rail the LED is attributed to, via R2 -- not R1/+5V.
    comps = [
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R1", "value": "330", "type": "resistor", "lib_id": "Device:R"},
        {"reference": "R2", "value": "1k", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "LED_A": {"pins": [_pin("D1", "1"), _pin("R1", "1"), _pin("R2", "1")]},
        "+5V": {"pins": [_pin("R1", "2")]},
        "+3.3V": {"pins": [_pin("R2", "2")]},
        "GND": {"pins": [_pin("D1", "2")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    assert result["rails"]["+3.3V"]["other_loads"] == [
        {"ref": "D1", "type": "led", "estimated_mA": 5, "via": "R2"}]
    assert "+5V" not in result["rails"]


def test_led_on_ground_is_not_attributed_via_an_unrelated_bleeder_resistor():
    # Fix round 2 (Critical, reviewer repro): D1 has no series resistor of
    # its own -- it sits directly on GND, driven from a GPIO. R_BLEED is a
    # totally unrelated bleeder resistor from +5V to GND elsewhere on the
    # board. Before the fix, the hop loop anchored off D1's GND pin, found
    # R_BLEED sitting on that same (shared, bus-like) GND net, and wrongly
    # attributed D1 to +5V "via" R_BLEED even though the two parts aren't in
    # series. Ground must never be used as a hop anchor.
    comps = [
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
        {"reference": "R_BLEED", "value": "10k", "type": "resistor", "lib_id": "Device:R"},
    ]
    nets = {
        "GPIO_NET": {"pins": [_pin("D1", "1")]},
        "GND": {"pins": [_pin("D1", "2"), _pin("R_BLEED", "2")]},
        "+5V": {"pins": [_pin("R_BLEED", "1")]},
    }
    ctx = _ctx(comps, nets)
    result = analyze_power_budget(ctx, {})
    # No ICs, no regulators, and D1 must not be attributed to +5V (or
    # anywhere else) -- the function should see no loads at all here.
    assert result == {}


def test_ldo_dissipation_uses_the_rails_total_load_including_other_loads():
    # U1 draws 10 mA (unrecognized keyword -> default estimate); D1 is a
    # direct-on-rail LED load (5 mA). Dissipation must be computed from
    # 15 mA, not just the IC's 10 mA.
    comps = [
        {"reference": "U2", "value": "AP2112", "type": "ic", "lib_id": "Regulator_Linear:AP2112"},
        {"reference": "U1", "value": "XYZ123", "type": "ic", "lib_id": "Some:XYZ123"},
        {"reference": "D1", "value": "LED", "type": "led", "lib_id": "Device:LED"},
    ]
    nets = {
        "3.3V": {"pins": [_pin("U1", "1", "power_in", "VDD"), _pin("D1", "1")]},
        "__unnamed_1": {"pins": [_pin("D1", "2")]},
    }
    ctx = _ctx(comps, nets)
    signal_analysis = {
        "power_regulators": [
            {"ref": "U2", "value": "AP2112", "topology": "LDO", "output_rail": "3.3V",
             "estimated_vout": 3.3, "input_rail": "+5V"},
        ],
    }
    result = analyze_power_budget(ctx, signal_analysis)
    rail = result["rails"]["3.3V"]
    assert rail["estimated_load_mA"] == 15
    v_drop = 5.0 - 3.3
    expected_power_mW = round(v_drop * (15 / 1000.0) * 1000, 1)
    assert rail["ldo_dissipation"]["power_mW"] == expected_power_mW


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
