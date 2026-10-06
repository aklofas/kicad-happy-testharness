"""KH-410 — RP-001 told users to add stitching vias at a layer transition
whose return path crosses a deliberate capacitive-touch void. For a
transition on a touch net the recommendation now says to route the
transition outside the void. Synthetic pcb JSON mirrors the real producer
shape (layer_transitions[].via_positions, vias.vias[].net_name, findings[]
CP-003 with nets, footprints[].connected_nets).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import emc_rules

RP001 = getattr(emc_rules, "check_layer_transition_stitching")


def _pcb(signal_net):
    return {
        "nets": {"GND": {}, signal_net: {}},
        "setup": {"stackup": []},
        "layer_transitions": [{"net": signal_net, "copper_layers": ["F.Cu", "B.Cu"],
                               "via_positions": [{"x": 10.0, "y": 10.0}]}],
        "vias": {"vias": [{"x": 40.0, "y": 40.0, "net_name": "GND"}]},
        "footprints": [{"reference": "TOUCH1", "library": "Touch:Pad",
                        "connected_nets": ["TOUCH_A"]}],
        "findings": [{"rule_id": "CP-003", "components": ["TOUCH1"], "nets": ["TOUCH_A"]}],
    }


def _rp001(net):
    return [f for f in RP001(_pcb(net), None) if f.get("rule_id") == "RP-001"]


def test_touch_net_recommendation_reworded():
    f = _rp001("TOUCH_A")
    assert len(f) == 1, f
    rec = f[0]["recommendation"]
    assert "outside the touch-pad void" in rec, rec
    assert "stitching via" not in rec.lower().replace("stitching vias", ""), rec
    assert f[0].get("is_touch_net") is True


def test_touch_net_severity_and_title_unchanged():
    touch = _rp001("TOUCH_A")[0]
    ctrl = _rp001("SIG1")[0]
    assert touch["severity"] == ctrl["severity"]
    assert touch["title"].replace("TOUCH_A", "X") == ctrl["title"].replace("SIG1", "X")


def test_control_net_keeps_original_text():
    rec = _rp001("SIG1")[0]["recommendation"]
    assert rec.startswith("Add a ground stitching via"), rec


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
