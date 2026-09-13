"""GitHub PR #44 (danielboston38) — fuses bridge DC in PP-001; plain / suffixed
/ descriptive voltage names are power rails.

Two changes, both in the pre-fix tree at v2.2.1 (main @ 3cf837b):

1. `audit_power_pin_dc_paths` (PP-001) did not treat `type == "fuse"` as a
   DC bridge, so `connector -> fuse -> (cap + IC power_in)` halted at the
   fuse, saw only the cap, and emitted a false "no DC path" error. The walk
   now crosses fuses (classifier emits "fuse" for F-refs / Polyfuse libs)
   and credits a net reached during the hop walk when it carries a
   connector, the same way the start net already was.

2. `is_power_net_name` missed plain `5V` / `12V` (the old `^\\d+V\\d` needed
   a trailing digit; `5V` is the single most common label in the corpus),
   letter-suffixed rails (`5VSB`, `12VIN`, `5VUSB`) and descriptive rails
   (`USB_5V`, `RAW_5V`, `SERVO_VCC`, `USB_VBUS`, `SYS_VOUT`). Maintainer-side
   tightening on top of the PR: `0V` stays ground-only, control suffixes
   (`5VEN`, `12VPG`) stay signals, `*_VOUT` needs a power prefix because
   half the corpus's `_VOUT` nets are op-amp / sensor outputs, and the old
   un-anchored `^\\d+V\\d` rule is kept so `3V3-A` style names don't regress.

Fixtures hand-build the component / net dicts with the real producer field
names (reference/value/type, nets[name]["pins"][{component, pin_number,
pin_type, pin_name}]) per repo convention (see test_kh402_nc_midspan.py).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import AnalysisContext  # noqa: E402
from kicad_utils import is_power_net_name, is_ground_name  # noqa: E402
from signal_detectors import audit_power_pin_dc_paths  # noqa: E402


def _pin(ref, num, ptype="passive", name=""):
    return {"component": ref, "pin_number": num, "pin_type": ptype,
            "pin_name": name}


def _ctx(components, nets):
    pin_net = {}
    for net_name, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net_name, p["pin_type"])
    return AnalysisContext(components=components, nets=nets, lib_symbols={},
                           pin_net=pin_net)


def _fused_board(bridge_type="fuse", far_net="__unnamed_9", with_connector=True):
    """J1 --far_net-- F1 --__unnamed_3-- (C1 to GND, U1.3 power_in)."""
    comps = [
        {"reference": "J1", "type": "connector", "value": "USB_C"},
        {"reference": "F1", "type": bridge_type, "value": "2A"},
        {"reference": "C1", "type": "capacitor", "value": "10uF"},
        {"reference": "U1", "type": "ic", "value": "TPS2553"},
    ]
    far_pins = [_pin("F1", "1")]
    if with_connector:
        far_pins.insert(0, _pin("J1", "1"))
    nets = {
        far_net: {"pins": far_pins},
        "__unnamed_3": {"pins": [_pin("F1", "2"), _pin("C1", "1"),
                                 _pin("U1", "3", "power_in", "IN")]},
        "GND": {"pins": [_pin("C1", "2"), _pin("U1", "1", "power_in", "GND")]},
    }
    return _ctx(comps, nets)


def _pp001(ctx):
    return [f for f in audit_power_pin_dc_paths(ctx) if f["rule_id"] == "PP-001"]


# --- PP-001: fuse is a DC bridge -------------------------------------------

def test_fuse_to_connector_net_is_a_dc_path():
    # Pre-fix: F1 blocked the walk, C1 was the only thing seen -> PP-001.
    assert _pp001(_fused_board()) == []


def test_fuse_to_named_rail_is_a_dc_path():
    assert _pp001(_fused_board(far_net="+5V", with_connector=False)) == []


def test_connector_reached_through_bridge_is_credited():
    # The far net has no power-looking name; only the connector on it says
    # "external supply". Credited during the hop walk, not just at the start.
    assert _pp001(_fused_board(bridge_type="inductor")) == []


def test_non_bridge_still_emits_pp001():
    # Control: an IC (not a bridge) between the pin's net and the connector
    # net leaves the cap-only path -> PP-001 still fires.
    ctx = _fused_board(bridge_type="ic", with_connector=True)
    found = _pp001(ctx)
    assert len(found) == 1
    assert "U1.3" in found[0]["summary"]
    assert found[0]["severity"] == "error"


def test_fuse_ref_without_fuse_type_is_not_a_bridge():
    # The raw "F<digit>" ref heuristic was dropped in favour of the
    # classifier's type; a mis-typed F1 is not bridged.
    ctx = _fused_board(bridge_type="ic")
    assert len(_pp001(ctx)) == 1


# --- is_power_net_name ------------------------------------------------------

def test_plain_and_suffixed_voltage_names_are_rails():
    for n in ("5V", "12V", "24V", "5v", "5VSB", "12VIN", "24VDC", "5VUSB",
              "3V3", "5V0", "3V3RAW", "+5V", "/Power/5V"):
        assert is_power_net_name(n), n


def test_zero_volt_is_ground_not_power():
    assert is_ground_name("0V")
    assert not is_power_net_name("0V")


def test_voltage_with_control_suffix_is_a_signal():
    for n in ("5VEN", "12VPG", "5VOK", "12VON", "5VFB", "12VENABLE", "24VSENSE"):
        assert not is_power_net_name(n), n


def test_hyphen_suffixed_nnvn_names_still_rails():
    # The old un-anchored ^\d+V\d rule is retained on purpose.
    assert is_power_net_name("3V3-A")
    assert is_power_net_name("5V0.SW")


def test_descriptive_rails_with_power_prefix():
    for n in ("USB_5V", "RAW_5V", "fused_5v", "ISO_3V3", "MCU_1V1", "EXT_5V",
              "SW_12V", "BOARD_3V3", "SYS_VOUT", "BOOST_VOUT", "LDO_VOUT",
              "BUCK_VOUT", "MAIN_VOUT"):
        assert is_power_net_name(n), n


def test_signal_prefix_with_voltage_stays_signal():
    for n in ("PWM_5V", "EN_5V", "GATE_12V", "SENSE_12V", "TX_3V3", "ADC_VIN",
              "FB_VOUT", "SNS_VIN", "ADC_VBUS", "HEATER_5V", "LED_5V"):
        assert not is_power_net_name(n), n


def test_supply_tails_are_rails_regardless_of_prefix():
    for n in ("SERVO_VCC", "RS485_VCC", "MCU_VDD", "ADC_AVDD", "PWM1_VCC",
              "USB_VBUS", "LED_VIN", "POWER_VBAT", "POWER_VSYS", "T_VCC"):
        assert is_power_net_name(n), n


def test_vout_without_power_prefix_is_not_a_rail():
    for n in ("OPAMP1_VOUT", "MIC_VOUT", "CURRENTSENSE_VOUT", "ACCEL_VOUT",
              "DIV_VOUT", "TIMER_VOUT", "MISO_VOUT"):
        assert not is_power_net_name(n), n


def test_power_rails_set_still_wins():
    assert is_power_net_name("WEIRD_NAME", {"WEIRD_NAME"})


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
