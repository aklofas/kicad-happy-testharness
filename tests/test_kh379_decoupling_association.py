"""KH-379 — `analyze_decoupling_placement` associated ANY capacitor within
10 mm of an IC, including caps that share only GND with the IC (no power
net in common). A ground-only cap both fired a spurious EMC DC-001 (too
far, since the real decoupling cap wasn't chosen) and suppressed the
correct DC-002 (no decoupling cap) for that IC.

Now: a cap only counts as "nearby" if it shares at least one non-ground
net with the IC. Caps within 10 mm that are rejected for being
ground-only are still reported, in the additive `gnd_only_caps` field, so
the data isn't silently dropped. The function also no longer early-returns
when there are no U/IC non-ESD parts, so ESD-only boards get their bypass
association analysed too.
"""

TIER = "unit"

import os
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = str(PRODUCT_ROOT)
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import pcb.assembly as pcb_assembly  # noqa: E402


def _fp(ref, value, x, pads):
    return {"reference": ref, "value": value, "layer": "F.Cu", "x": x, "y": 0.0,
            "pads": [{"number": str(i + 1), "abs_x": x + i * 0.5, "abs_y": 0.0, "net_name": n, "layers": ["F.Cu"]}
                     for i, n in enumerate(pads)]}


def test_ground_only_cap_is_not_associated():
    fps = [_fp("U1", "MCU", 0.0, ["+3V3", "GND"]), _fp("C1", "100n", 2.0, ["GND", "SIG_X"]), _fp("C2", "100n", 7.0, ["+3V3", "GND"])]
    out = pcb_assembly.analyze_decoupling_placement(fps)
    assert len(out) == 1 and out[0]["ic"] == "U1"
    assert [c["cap"] for c in out[0]["nearby_caps"]] == ["C2"]
    # Note: 6.5mm, not the naive pin-1-to-pin-1 reading of 7.0mm -- U1's GND
    # pad (abs_x=0.5) already counts as a "power pad" in the pre-existing,
    # out-of-scope `_min_power_pad_distance` (nu in ("GND", ...) is_pwr_gnd
    # check predates KH-379) and it's 6.5mm from C2, closer than U1's +3V3
    # pad at abs_x=0.0.
    assert out[0]["closest_cap_mm"] == 6.5
    assert out[0]["gnd_only_caps"] == ["C1"]


def test_no_shared_power_net_means_no_entry():
    fps = [_fp("U1", "MCU", 0.0, ["+3V3", "GND"]), _fp("C1", "100n", 2.0, ["GND", "SIG_X"])]
    assert pcb_assembly.analyze_decoupling_placement(fps) == []


def test_esd_only_board_gets_esd_bypass_entry():
    fps = [_fp("U9", "USBLC6-2SC6", 0.0, ["VBUS", "GND"]), _fp("C3", "100n", 1.0, ["VBUS", "GND"])]
    out = pcb_assembly.analyze_decoupling_placement(fps)
    assert out and out[0]["category"] == "esd_bypass" and out[0]["ic"] == "U9"



def _typed_fp(ref, value, x, pads):
    """KiCad 6+ footprint: each pad carries its symbol pin type and pin function."""
    fp = _fp(ref, value, x, [n for n, _, _ in pads])
    for pad, (_, pintype, pinfunction) in zip(fp["pads"], pads):
        pad["pintype"], pad["pinfunction"] = pintype, pinfunction
    return fp


def test_crystal_load_cap_on_input_pin_is_not_decoupling():
    """A cap on an IC net whose own pad is typed `input` (crystal load cap on OSC_IN) is not
    the IC's decoupling; the supply cap further away is."""
    mcu = _typed_fp("U1", "MCU", 0.0, [("+3V3", "power_in", "VDD"), ("GND", "power_in", "VSS"),
                                       ("/OSC_IN", "input", "OSC_IN")])
    fps = [mcu, _fp("C1", "18p", 2.0, ["/OSC_IN", "GND"]), _fp("C2", "100n", 7.0, ["+3V3", "GND"])]
    out = pcb_assembly.analyze_decoupling_placement(fps)
    assert len(out) == 1 and out[0]["ic"] == "U1"
    assert [c["cap"] for c in out[0]["nearby_caps"]] == ["C2"]


def test_untyped_pads_keep_the_load_cap():
    """KiCad 5 pads carry no pin type: the load cap still counts, as before."""
    fps = [_fp("U1", "MCU", 0.0, ["+3V3", "GND", "/OSC_IN"]), _fp("C1", "18p", 2.0, ["/OSC_IN", "GND"]),
           _fp("C2", "100n", 7.0, ["+3V3", "GND"])]
    out = pcb_assembly.analyze_decoupling_placement(fps)
    assert [c["cap"] for c in out[0]["nearby_caps"]] == ["C1", "C2"]


def test_input_typed_pad_named_as_a_supply_pin_counts():
    """A supply pin typed `input` (pin function VDD) on a non-rail net is still a supply."""
    ic = _typed_fp("U1", "SENSOR", 0.0, [("/LDO_OUT", "input", "VDD"), ("GND", "power_in", "GND")])
    fps = [ic, _fp("C1", "100n", 2.0, ["/LDO_OUT", "GND"])]
    out = pcb_assembly.analyze_decoupling_placement(fps)
    assert [c["cap"] for c in out[0]["nearby_caps"]] == ["C1"]


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
