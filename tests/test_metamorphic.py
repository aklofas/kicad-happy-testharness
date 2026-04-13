"""Metamorphic tests — invariance and covariance properties of detector outputs.

Each test builds two synthetic schematics: a base case and a transformed variant.
Invariance tests verify that a transformation doesn't change a key output property.
Covariance tests verify that a transformation changes a property predictably.

Families covered: voltage divider, RC filter, regulator, protection, crystal.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, pin1, pin2, ic_pin_pos

HARNESS_DIR = Path(__file__).resolve().parent.parent


def run_analyzer(sch):
    """Build schematic, run analyzer, return parsed JSON or None."""
    kh_dir = os.environ.get("KICAD_HAPPY_DIR",
                str(HARNESS_DIR.parent / "kicad-happy"))
    script = Path(kh_dir) / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
    if not script.exists():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        sch_path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        out_path = str(Path(tmp) / "output.json")
        result = subprocess.run(
            [sys.executable, str(script), sch_path, "--output", out_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise AssertionError(f"Analyzer failed: {result.stderr[:300]}")
        return json.loads(Path(out_path).read_text(encoding="utf-8"))


# --- Builder helpers ---

def _build_divider(r1_val, r2_val):
    return (
        Schematic()
        .resistor("R1", r1_val, at=(50, 50))
        .resistor("R2", r2_val, at=(50, 62))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 72))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), pin1(50, 62))
        .wire(pin2(50, 62), (50, 72))
    )


def _build_rc_lowpass(r_val, c_val):
    R_cx, R_cy = 50, 50
    C_cx, C_cy = 60, 50
    return (
        Schematic()
        .resistor("R1", r_val, at=(R_cx, R_cy), angle=90)
        .capacitor("C1", c_val, at=(C_cx, C_cy))
        .power("GND", at=(C_cx, 65))
        .label("IN", at=(pin1(R_cx, R_cy, 90)[0], R_cy))
        .label("FILT", at=(C_cx, R_cy))
        .wire((pin1(R_cx, R_cy, 90)[0], R_cy), pin1(R_cx, R_cy, 90))
        .wire(pin2(R_cx, R_cy, 90), (C_cx, R_cy))
        .wire((C_cx, R_cy), pin1(C_cx, C_cy))
        .wire(pin2(C_cx, C_cy), (C_cx, 65))
    )


_REG_PINS = [
    ("VIN", "1", -5.08, 0, "input"),
    ("GND", "2", 0, 5.08, "power_in"),
    ("VOUT", "3", 5.08, 0, "output"),
]


def _build_regulator(ref, value, lib_id):
    cx, cy = 50, 50
    return (
        Schematic()
        .ic(ref, value, lib_id, _REG_PINS, at=(cx, cy))
        .power("+12V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("OUT", at=(65, cy))
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", _REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", _REG_PINS), (cx, 65))
        .wire(ic_pin_pos(cx, cy, "VOUT", _REG_PINS), (65, cy))
    )


def _build_crystal(freq_val, cap_val):
    Y_cx, Y_cy = 50, 50
    C1_cx = pin1(Y_cx, Y_cy, 90)[0]
    C2_cx = pin2(Y_cx, Y_cy, 90)[0]
    C1_cy = C2_cy = 60
    return (
        Schematic()
        .crystal("Y1", freq_val, at=(Y_cx, Y_cy), angle=90)
        .capacitor("C1", cap_val, at=(C1_cx, C1_cy))
        .capacitor("C2", cap_val, at=(C2_cx, C2_cy))
        .power("GND", at=(C1_cx, 70))
        .power("GND", at=(C2_cx, 70))
        .wire(pin1(Y_cx, Y_cy, 90), pin1(C1_cx, C1_cy))
        .wire(pin2(Y_cx, Y_cy, 90), pin1(C2_cx, C2_cy))
        .wire(pin2(C1_cx, C1_cy), (C1_cx, 70))
        .wire(pin2(C2_cx, C2_cy), (C2_cx, 70))
    )


# === Voltage Divider ===

def test_vd_invariance_r_scaling():
    """Scaling both R values by 10x should not change the divider ratio."""
    d1 = run_analyzer(_build_divider("10k", "10k"))
    d2 = run_analyzer(_build_divider("100k", "100k"))
    if d1 is None or d2 is None:
        return
    vd1 = d1["signal_analysis"]["voltage_dividers"]
    vd2 = d2["signal_analysis"]["voltage_dividers"]
    assert len(vd1) == 1 and len(vd2) == 1
    assert abs(vd1[0]["ratio"] - vd2[0]["ratio"]) < 0.01, \
        f"R-scaling changed ratio: {vd1[0]['ratio']} vs {vd2[0]['ratio']}"


def test_vd_covariance_r_bottom_increases_ratio():
    """Increasing R_bottom should increase the divider ratio."""
    d1 = run_analyzer(_build_divider("10k", "10k"))
    d2 = run_analyzer(_build_divider("10k", "22k"))
    if d1 is None or d2 is None:
        return
    vd1 = d1["signal_analysis"]["voltage_dividers"]
    vd2 = d2["signal_analysis"]["voltage_dividers"]
    assert len(vd1) == 1 and len(vd2) == 1
    assert vd2[0]["ratio"] > vd1[0]["ratio"], \
        f"Larger R_bottom should increase ratio: {vd1[0]['ratio']} vs {vd2[0]['ratio']}"


# === RC Filter ===

def test_rc_invariance_constant_product():
    """RC product 1e-3 (R=1k,C=1u vs R=10k,C=100n) → same cutoff_hz."""
    d1 = run_analyzer(_build_rc_lowpass("1k", "1u"))
    d2 = run_analyzer(_build_rc_lowpass("10k", "100n"))
    if d1 is None or d2 is None:
        return
    rc1 = d1["signal_analysis"]["rc_filters"]
    rc2 = d2["signal_analysis"]["rc_filters"]
    assert len(rc1) >= 1 and len(rc2) >= 1
    fc1, fc2 = rc1[0]["cutoff_hz"], rc2[0]["cutoff_hz"]
    # Same RC product → same cutoff (within 10% tolerance for rounding)
    assert abs(fc1 - fc2) / max(fc1, fc2) < 0.1, \
        f"Constant RC product should give same fc: {fc1} vs {fc2}"


def test_rc_covariance_doubling_r_halves_fc():
    """Doubling R should approximately halve the cutoff frequency."""
    d1 = run_analyzer(_build_rc_lowpass("1k", "1u"))
    d2 = run_analyzer(_build_rc_lowpass("2k", "1u"))
    if d1 is None or d2 is None:
        return
    rc1 = d1["signal_analysis"]["rc_filters"]
    rc2 = d2["signal_analysis"]["rc_filters"]
    assert len(rc1) >= 1 and len(rc2) >= 1
    fc1, fc2 = rc1[0]["cutoff_hz"], rc2[0]["cutoff_hz"]
    ratio = fc1 / fc2
    # fc1/fc2 should be ≈ 2.0 (doubling R halves fc)
    assert 1.5 < ratio < 2.5, \
        f"Doubling R should halve fc: fc1={fc1}, fc2={fc2}, ratio={ratio}"


# === Regulator ===

def test_reg_invariance_ref_relabel():
    """Changing reference (U1→U2) should not change estimated_vout."""
    d1 = run_analyzer(_build_regulator("U1", "LM7805", "Regulator_Linear:LM7805"))
    d2 = run_analyzer(_build_regulator("U2", "LM7805", "Regulator_Linear:LM7805"))
    if d1 is None or d2 is None:
        return
    r1 = d1["signal_analysis"].get("power_regulators", [])
    r2 = d2["signal_analysis"].get("power_regulators", [])
    assert len(r1) >= 1 and len(r2) >= 1
    v1 = r1[0].get("estimated_vout")
    v2 = r2[0].get("estimated_vout")
    assert v1 is not None and v2 is not None
    assert abs(v1 - v2) < 0.01, \
        f"Ref relabel changed vout: {v1} vs {v2}"


def test_reg_covariance_different_part_different_vout():
    """LM7805 (5V) vs LM7812 (12V) → different estimated_vout."""
    d1 = run_analyzer(_build_regulator("U1", "LM7805", "Regulator_Linear:LM7805"))
    d2 = run_analyzer(_build_regulator("U1", "LM7812", "Regulator_Linear:LM7812"))
    if d1 is None or d2 is None:
        return
    r1 = d1["signal_analysis"].get("power_regulators", [])
    r2 = d2["signal_analysis"].get("power_regulators", [])
    assert len(r1) >= 1 and len(r2) >= 1
    v1 = r1[0].get("estimated_vout")
    v2 = r2[0].get("estimated_vout")
    assert v1 is not None and v2 is not None
    assert v2 > v1, f"LM7812 vout should be > LM7805 vout: {v2} vs {v1}"
    assert abs(v1 - 5.0) < 1.0, f"LM7805 vout should be ~5V: {v1}"
    assert abs(v2 - 12.0) < 1.0, f"LM7812 vout should be ~12V: {v2}"


# === Protection ===

def test_prot_invariance_ref_relabel():
    """Changing TVS ref (D1→D2) should still detect protection device."""
    D_cx, D_cy = 50, 50
    for ref in ("D1", "D2"):
        sch = (
            Schematic()
            .diode(ref, "PESD5V0S1BA", at=(D_cx, D_cy), variant="D_TVS")
            .label("SIG", at=(D_cx, 40))
            .power("GND", at=(D_cx, 60))
            .wire((D_cx, 40), pin1(D_cx, D_cy))
            .wire(pin2(D_cx, D_cy), (D_cx, 60))
        )
        data = run_analyzer(sch)
        if data is None:
            return
        pd = data["signal_analysis"].get("protection_devices", [])
        assert len(pd) >= 1, f"Protection device {ref} not detected"


def test_prot_covariance_adding_device_increases_count():
    """Adding a second TVS on a different net should increase count by 1."""
    D1_cx, D1_cy = 40, 50
    D2_cx, D2_cy = 60, 50

    # Base: single TVS
    sch1 = (
        Schematic()
        .diode("D1", "PESD5V0S1BA", at=(D1_cx, D1_cy), variant="D_TVS")
        .label("SIG_A", at=(D1_cx, 40))
        .power("GND", at=(D1_cx, 60))
        .wire((D1_cx, 40), pin1(D1_cx, D1_cy))
        .wire(pin2(D1_cx, D1_cy), (D1_cx, 60))
    )
    # Variant: two TVS on different signals
    sch2 = (
        Schematic()
        .diode("D1", "PESD5V0S1BA", at=(D1_cx, D1_cy), variant="D_TVS")
        .diode("D2", "PESD5V0S1BA", at=(D2_cx, D2_cy), variant="D_TVS")
        .label("SIG_A", at=(D1_cx, 40))
        .label("SIG_B", at=(D2_cx, 40))
        .power("GND", at=(D1_cx, 60))
        .power("GND", at=(D2_cx, 60))
        .wire((D1_cx, 40), pin1(D1_cx, D1_cy))
        .wire(pin2(D1_cx, D1_cy), (D1_cx, 60))
        .wire((D2_cx, 40), pin1(D2_cx, D2_cy))
        .wire(pin2(D2_cx, D2_cy), (D2_cx, 60))
    )
    d1 = run_analyzer(sch1)
    d2 = run_analyzer(sch2)
    if d1 is None or d2 is None:
        return
    pd1 = d1["signal_analysis"].get("protection_devices", [])
    pd2 = d2["signal_analysis"].get("protection_devices", [])
    assert len(pd2) > len(pd1), \
        f"Adding TVS should increase count: {len(pd1)} vs {len(pd2)}"


# === Crystal ===

def test_crystal_invariance_load_cap_value():
    """Changing load cap value should not change reported crystal frequency."""
    d1 = run_analyzer(_build_crystal("16MHz", "18p"))
    d2 = run_analyzer(_build_crystal("16MHz", "22p"))
    if d1 is None or d2 is None:
        return
    cc1 = d1["signal_analysis"]["crystal_circuits"]
    cc2 = d2["signal_analysis"]["crystal_circuits"]
    assert len(cc1) >= 1 and len(cc2) >= 1
    f1, f2 = cc1[0]["frequency"], cc2[0]["frequency"]
    assert f1 == f2, f"Load cap change altered frequency: {f1} vs {f2}"


def test_crystal_covariance_different_frequency():
    """16MHz vs 8MHz crystal → different reported frequency."""
    d1 = run_analyzer(_build_crystal("16MHz", "18p"))
    d2 = run_analyzer(_build_crystal("8MHz", "18p"))
    if d1 is None or d2 is None:
        return
    cc1 = d1["signal_analysis"]["crystal_circuits"]
    cc2 = d2["signal_analysis"]["crystal_circuits"]
    assert len(cc1) >= 1 and len(cc2) >= 1
    f1, f2 = cc1[0]["frequency"], cc2[0]["frequency"]
    assert f1 > f2, f"16MHz should be > 8MHz: {f1} vs {f2}"
    assert abs(f1 / f2 - 2.0) < 0.1, f"Frequency ratio should be ~2.0: {f1/f2}"


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
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
    sys.exit(1 if failed else 0)
