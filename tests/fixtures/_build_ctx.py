"""Minimal AnalysisContext builder for validator unit tests.

Usage:
    from fixtures._build_ctx import build_ctx, ic, resistor, capacitor

    ctx = build_ctx(
        components=[
            ic("U1", "STM32F103C8T6", [("3", "NRST"), ("1", "VDD"), ("2", "VSS")]),
            resistor("R1", "10k"),
        ],
        nets={
            "NRST_NET": [("U1", "3"), ("R1", "1")],
            "+3V3":     [("U1", "1"), ("R1", "2")],
            "GND":      [("U1", "2")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_pullups(ctx)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add kicad-happy scripts dir so `from kicad_types import AnalysisContext` works.
_KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "kicad-happy"),
)
_SCRIPTS = Path(_KICAD_HAPPY) / "skills" / "kicad" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from kicad_types import AnalysisContext  # noqa: E402


def ic(ref: str, value: str, pins: list[tuple[str, str]],
       lib_id: str = "Device:U", mpn: str | None = None) -> dict:
    """Create an IC component dict. pins is [(pin_number, pin_name), ...]."""
    c = {
        "reference": ref,
        "value": value,
        "type": "ic",
        "lib_id": lib_id,
        "footprint": "",
        "properties": {},
        "pins": [{"number": n, "name": name} for n, name in pins],
    }
    if mpn is not None:
        c["mpn"] = mpn
    return c


def resistor(ref: str, value: str) -> dict:
    """Create a 2-pin resistor component dict."""
    return {
        "reference": ref, "value": value, "type": "resistor",
        "lib_id": "Device:R", "footprint": "",
        "properties": {}, "pins": [
            {"number": "1", "name": "~"}, {"number": "2", "name": "~"},
        ],
    }


def capacitor(ref: str, value: str) -> dict:
    """Create a 2-pin capacitor component dict."""
    return {
        "reference": ref, "value": value, "type": "capacitor",
        "lib_id": "Device:C", "footprint": "",
        "properties": {}, "pins": [
            {"number": "1", "name": "~"}, {"number": "2", "name": "~"},
        ],
    }


def led(ref: str, value: str = "LED") -> dict:
    """Create a 2-pin LED component dict. pin 1 = cathode, pin 2 = anode.

    type is "led" (not "diode") to match the actual analyzer output: components
    with a "LED" reference prefix get type "led" via classify_component in
    kicad_utils.py.  validate_led_resistors checks c['type'] == 'led', so
    callers should pass an LED-prefixed ref such as "LED1" or a plain "LED"
    suffix ref like "D_LED1" if they want this fixture to be detected.
    Simplest choice: use "LED1" as the ref so the type matches.
    """
    return {
        "reference": ref, "value": value, "type": "led",
        "lib_id": "Device:LED", "footprint": "",
        "properties": {}, "pins": [
            {"number": "1", "name": "K"}, {"number": "2", "name": "A"},
        ],
    }


def connector(ref: str, value: str, pins: list[tuple[str, str]]) -> dict:
    """Create a connector component dict with configurable pin list."""
    return {
        "reference": ref, "value": value, "type": "connector",
        "lib_id": "Connector:Generic", "footprint": "",
        "properties": {}, "pins": [
            {"number": n, "name": name} for n, name in pins
        ],
    }


def build_ctx(components: list[dict],
              nets: dict[str, list[tuple[str, str]]],
              known_power_rails: set[str] | None = None,
              lib_symbols: dict | None = None,
              generator_version: str = "9.0.1") -> AnalysisContext:
    """Construct a minimal AnalysisContext.

    components: list of component dicts (use ic(), resistor(), etc.)
    nets: {net_name: [(ref, pin_number), ...]} — pin_name is looked up from
          the component's pins list.
    known_power_rails: explicit set of power net names. Defaults to empty
          set; `AnalysisContext.__post_init__` then auto-detects power nets
          from any pin whose component ref starts with '#PWR' or '#FLG'.
          Pass a set explicitly when your fixtures don't use power symbols.

    __post_init__ builds comp_lookup, parsed_values, ref_pins from inputs.
    """
    if known_power_rails is None:
        known_power_rails = set()
    if lib_symbols is None:
        lib_symbols = {}

    # Build nets dict in AnalysisContext shape: {name: {"pins": [...]}}
    nets_full: dict[str, dict] = {}
    pin_net: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    comp_by_ref = {c["reference"]: c for c in components}

    for net_name, pin_refs in nets.items():
        pin_entries = []
        for ref, pnum in pin_refs:
            comp = comp_by_ref.get(ref)
            pname = ""
            if comp:
                for p in comp.get("pins", []):
                    if p.get("number") == pnum:
                        pname = p.get("name", "")
                        break
            pin_entries.append({
                "component": ref, "pin_number": pnum,
                "pin_name": pname, "x": 0.0, "y": 0.0,
            })
            pin_net[(ref, pnum)] = (net_name, pname)
        nets_full[net_name] = {"pins": pin_entries}

    return AnalysisContext(
        components=components,
        nets=nets_full,
        lib_symbols=lib_symbols,
        pin_net=pin_net,
        known_power_rails=known_power_rails,
        generator_version=generator_version,
    )


if __name__ == "__main__":
    # Self-test: build a tiny context and verify auto-populated fields.
    ctx = build_ctx(
        components=[ic("U1", "MCU", [("1", "VDD"), ("2", "GND"), ("3", "NRST")]),
                    resistor("R1", "10k")],
        nets={"+3V3": [("U1", "1"), ("R1", "1")],
              "GND":  [("U1", "2"), ("R1", "2")]},
        known_power_rails={"+3V3", "GND"},
    )
    assert ctx.comp_lookup["U1"]["value"] == "MCU"
    assert ctx.parsed_values["R1"] == 10_000.0
    assert ctx.ref_pins["U1"]["1"] == ("+3V3", "VDD")
    assert ctx.is_power_net("+3V3")
    print("build_ctx self-test: PASS")
