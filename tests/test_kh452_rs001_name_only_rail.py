"""GitHub #54 - RS-001 admits a net by name alone (is_power_net_name), but
always said "carries power_in pins" at deterministic confidence, with an
empty pins[] when no pin was power_in. A name-only rail now says so and is
heuristic; a rail with power_in loads is unchanged.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import build_analysis_context  # noqa: E402
from signal_detectors import audit_rail_sources  # noqa: E402


def _pin(ref, num, ptype="passive", name=""):
    return {"component": ref, "pin_number": num, "pin_type": ptype,
            "pin_name": name}


def _ctx(nets, comps):
    return build_analysis_context(comps, nets, {})


def _rs001(ctx, net):
    return [f for f in audit_rail_sources(ctx)
            if f["rule_id"] == "RS-001" and f["nets"] == [net]]


def test_name_only_rail_is_heuristic_and_says_why():
    ctx = _ctx({"VBAT": {"pins": [_pin("R1", "1"), _pin("R2", "1")]}},
               [{"reference": "R1", "type": "resistor", "value": "10k"},
                {"reference": "R2", "type": "resistor", "value": "10k"}])
    [f] = _rs001(ctx, "VBAT")
    assert f["confidence"] == "heuristic", f
    assert f["provenance"]["confidence"] == "heuristic", f
    assert "carries power_in pins" not in f["description"], f["description"]
    assert "named like a power rail" in f["description"], f["description"]
    assert f["pins"] == []


def test_rail_with_power_in_load_unchanged():
    ctx = _ctx({"VBAT": {"pins": [_pin("U1", "1", "power_in", "VDD")]}},
               [{"reference": "U1", "type": "ic", "value": "MCU"}])
    [f] = _rs001(ctx, "VBAT")
    assert f["confidence"] == "deterministic", f
    assert "carries power_in pins" in f["description"], f["description"]
    assert f["pins"] == ["U1.1"]


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
