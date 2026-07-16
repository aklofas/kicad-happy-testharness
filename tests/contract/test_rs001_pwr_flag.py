#!/usr/bin/env python3
"""Regression test: RS-001 should recognize PWR_FLAG as a rail source declaration.

Adopted from anyasabo/kicad-happy @ 16c6265 (ported 2026-07-15).
"""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_schematic import build_net_map


def test_pwr_flag_sets_has_pwr_flag_on_net():
    """A PWR_FLAG component's pin should mark its net with has_pwr_flag=True."""
    components = [
        {
            "reference": "#FLG01",
            "value": "PWR_FLAG",
            "type": "power_flag",
            "in_bom": False,
            "_sheet": 0,
            "pins": [{"x": 10.0, "y": 20.0, "number": "1", "name": "pwr", "type": "power_out"}],
        },
        {
            "reference": "J1",
            "value": "Conn_01x02",
            "type": "connector",
            "in_bom": True,
            "_sheet": 0,
            "pins": [
                {"x": 10.0, "y": 20.0, "number": "1", "name": "Pin_1", "type": "passive"},
                {"x": 10.0, "y": 22.54, "number": "2", "name": "Pin_2", "type": "passive"},
            ],
        },
    ]
    # Wire from connector pin 1 straight up — label names the net VBUS
    wires = [{"x1": 10.0, "y1": 20.0, "x2": 10.0, "y2": 18.0, "_sheet": 0}]
    labels = [{"x": 10.0, "y": 18.0, "name": "VBUS", "type": "label", "_sheet": 0}]
    power_symbols = []
    junctions = []

    nets = build_net_map(components, wires, labels, power_symbols, junctions)

    assert "VBUS" in nets, f"Expected VBUS net, got: {list(nets.keys())}"
    vbus = nets["VBUS"]
    assert vbus.get("has_pwr_flag") is True, (
        f"Expected has_pwr_flag=True on VBUS, got: {vbus.get('has_pwr_flag')}"
    )
    # PWR_FLAG pin should NOT appear in the net's pins list
    refs_in_pins = [p["component"] for p in vbus["pins"]]
    assert "#FLG01" not in refs_in_pins, "PWR_FLAG should not appear in net pins list"


def test_net_without_pwr_flag():
    """A net with no PWR_FLAG should have has_pwr_flag=False."""
    components = [
        {
            "reference": "R1",
            "value": "10k",
            "type": "resistor",
            "in_bom": True,
            "_sheet": 0,
            "pins": [
                {"x": 5.0, "y": 10.0, "number": "1", "name": "1", "type": "passive"},
                {"x": 5.0, "y": 12.0, "number": "2", "name": "2", "type": "passive"},
            ],
        },
    ]
    wires = [{"x1": 5.0, "y1": 10.0, "x2": 5.0, "y2": 8.0, "_sheet": 0}]
    labels = [{"x": 5.0, "y": 8.0, "name": "SIG", "type": "label", "_sheet": 0}]

    nets = build_net_map(components, wires, labels, [], [])

    assert "SIG" in nets
    assert nets["SIG"].get("has_pwr_flag") is False


if __name__ == "__main__":
    test_pwr_flag_sets_has_pwr_flag_on_net()
    test_net_without_pwr_flag()
    print("All RS-001 PWR_FLAG tests passed.")
