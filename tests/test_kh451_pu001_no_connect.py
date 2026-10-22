"""GitHub #53 - PU-001 asked for a pull-up on an open-collector INT pin
that carries a no-connect marker. The net builder already flags that net
`no_connect`; validate_pullups now skips a pin alone on such a net (same
single-pin rule as the pin-level NO_CONNECT logic in analyze_schematic.py).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import AnalysisContext  # noqa: E402
from validation_detectors import validate_pullups  # noqa: E402


def _pin(ref, num, ptype="passive", name=""):
    return {"component": ref, "pin_number": num, "pin_type": ptype,
            "pin_name": name}


def _ctx(int_no_connect, extra_int_pins=()):
    comps = [{"reference": "U1", "type": "ic", "value": "TMP_SENSOR",
              "lib_id": "Repro:SENSOR",
              "pins": [{"number": "1", "name": "VDD"},
                       {"number": "2", "name": "GND"},
                       {"number": "3", "name": "INT"}]}]
    nets = {
        "+3V3": {"pins": [_pin("U1", "1", "power_in", "VDD")]},
        "GND": {"pins": [_pin("U1", "2", "power_in", "GND")]},
        "__unnamed_0": {"pins": [_pin("U1", "3", "open_collector", "INT"),
                                 *extra_int_pins],
                        "no_connect": int_no_connect},
    }
    pin_net = {}
    for net_name, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net_name, p["pin_type"])
    return AnalysisContext(components=comps, nets=nets, lib_symbols={},
                           pin_net=pin_net)


def _pu001(ctx):
    return [f for f in validate_pullups(ctx) if f["rule_id"] == "PU-001"]


def test_no_connect_pin_needs_no_pullup():
    assert _pu001(_ctx(int_no_connect=True)) == []


def test_floating_int_without_marker_still_fires():
    found = _pu001(_ctx(int_no_connect=False))
    assert len(found) == 1 and "INT" in found[0]["summary"], found


def test_stray_marker_on_multi_pin_net_does_not_suppress():
    # A marker absorbed into a net that also reaches another pin must not
    # hide the finding (net flag is only trusted for a single-pin net).
    found = _pu001(_ctx(int_no_connect=True,
                        extra_int_pins=[_pin("TP1", "1", "passive", "1")]))
    assert len(found) == 1, found


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
