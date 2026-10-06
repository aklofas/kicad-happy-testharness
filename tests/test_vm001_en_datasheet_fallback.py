"""VM-001 — a trusted datasheet extraction that carries NO EN threshold
(`en_v_ih_max: None`) disabled the regulator-EN heuristic, so a 3.3 V GPIO
driving a boost converter's EN pin was reported as a 5.0 V / 3.3 V domain
crossing at error severity (SacMap rev2 soak, 2026-10-05, U2 TPS61023
EN_5V). The datasheet branch now only decides when it has a threshold; the
heuristic runs otherwise. Harness assigns the KH number.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, str(_HARNESS / "tests"))

from fixtures._build_ctx import build_ctx, ic, resistor
import validation_detectors as vd


def _boost_ctx():
    # U1 = 3.3 V MCU, U2 = TPS61023 boost (VIN=+BATT, EN, VOUT=+5V); MCU IO drives EN.
    return build_ctx(
        components=[
            ic("U1", "ESP32-S3", [("1", "3V3"), ("2", "GND"), ("3", "IO8")], mpn="ESP32-S3-WROOM-1-N4"),
            ic("U2", "TPS61023DRLR", [("1", "GND"), ("2", "EN"), ("3", "VIN"), ("6", "VOUT")], mpn="TPS61023DRLR"),
            resistor("R12", "10k"),
        ],
        nets={
            "+3V3": [("U1", "1")],
            "+BATT": [("U2", "3")],
            "+5V": [("U2", "6")],
            "GND": [("U1", "2"), ("U2", "1"), ("R12", "2")],
            "EN_5V": [("U1", "3"), ("U2", "2"), ("R12", "1")],
        },
        known_power_rails={"+3V3", "+BATT", "+5V", "GND"},
    )


def _features(en_v_ih_max):
    return {"topology": "boost", "has_pg": False, "en_pin": "2", "vin_pin": "3", "vout_pin": "6",
            "en_v_ih_max": en_v_ih_max, "quality": {"score": 91, "scale": "0-100", "trusted": True, "reasons": []}}


def _vm(findings):
    return [f for f in findings if f.get("rule_id") == "VM-001"]


def test_trusted_extraction_without_threshold_falls_back_to_heuristic(monkeypatch=None):
    orig = vd.get_regulator_features
    vd.get_regulator_features = lambda mpn, **kw: _features(None) if mpn == "TPS61023DRLR" else None
    try:
        assert _vm(vd.validate_voltage_levels(_boost_ctx())) == []
    finally:
        vd.get_regulator_features = orig


def test_trusted_extraction_with_compatible_threshold_skips():
    orig = vd.get_regulator_features
    vd.get_regulator_features = lambda mpn, **kw: _features(1.2) if mpn == "TPS61023DRLR" else None
    try:
        assert _vm(vd.validate_voltage_levels(_boost_ctx())) == []
    finally:
        vd.get_regulator_features = orig


def test_trusted_extraction_with_incompatible_threshold_keeps_finding():
    # Datasheet says EN needs >= 2*2.0 = 4.0 V to be safely high; 3.3 V drive -> keep VM-001.
    orig = vd.get_regulator_features
    vd.get_regulator_features = lambda mpn, **kw: _features(2.0) if mpn == "TPS61023DRLR" else None
    try:
        vm = _vm(vd.validate_voltage_levels(_boost_ctx()))
        assert len(vm) == 1 and vm[0]["nets"] == ["EN_5V"], vm
        assert vm[0]["confidence"] == "heuristic"
        assert vm[0]["provenance"]["confidence"] == "heuristic"
    finally:
        vd.get_regulator_features = orig


def test_no_extraction_uses_heuristic():
    orig = vd.get_regulator_features
    vd.get_regulator_features = lambda mpn, **kw: None
    try:
        assert _vm(vd.validate_voltage_levels(_boost_ctx())) == []
    finally:
        vd.get_regulator_features = orig


def test_genuine_crossing_still_fires():
    # Two non-regulator ICs on different rails sharing a signal — must still be VM-001.
    ctx = build_ctx(
        components=[ic("U1", "MCU", [("1", "VDD"), ("2", "SIG")]), ic("U2", "SENSOR", [("1", "VDD"), ("2", "SIG")])],
        nets={"+5V": [("U1", "1")], "+3V3": [("U2", "1")], "SIG": [("U1", "2"), ("U2", "2")]},
        known_power_rails={"+5V", "+3V3"},
    )
    orig = vd.get_regulator_features
    vd.get_regulator_features = lambda mpn, **kw: None
    try:
        assert len(_vm(vd.validate_voltage_levels(ctx))) == 1
    finally:
        vd.get_regulator_features = orig


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
