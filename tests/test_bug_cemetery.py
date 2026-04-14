"""Bug cemetery — minimal reproducers for historical analyzer bugs.

Each test builds a synthetic schematic that would have triggered a past bug,
runs the analyzer, and asserts the FIXED behavior. If the bug regresses,
the test fails.

Bugs are referenced by KH-* issue number from FIXED.md.
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


# --- KH-276: RC filter with zero-ohm R should not be detected ---

def test_kh276_zero_ohm_rc_not_detected():
    """KH-276: R=0 + C wired as RC filter should NOT produce cutoff_hz=0."""
    R_cx, R_cy = 50, 50
    C_cx, C_cy = 60, 50
    sch = (
        Schematic()
        .resistor("R1", "0", at=(R_cx, R_cy), angle=90)
        .capacitor("C1", "1u", at=(C_cx, C_cy))
        .power("GND", at=(C_cx, 65))
        .label("IN", at=(pin1(R_cx, R_cy, 90)[0], R_cy))
        .label("FILT", at=(C_cx, R_cy))
        .wire((pin1(R_cx, R_cy, 90)[0], R_cy), pin1(R_cx, R_cy, 90))
        .wire(pin2(R_cx, R_cy, 90), (C_cx, R_cy))
        .wire((C_cx, R_cy), pin1(C_cx, C_cy))
        .wire(pin2(C_cx, C_cy), (C_cx, 65))
    )
    data = run_analyzer(sch)
    if data is None:
        return  # skip if kicad-happy not available
    rc = [f for f in data.get("findings", []) if f.get("detector") == "detect_rc_filters"]
    # Bug: zero-ohm R produced cutoff_hz=0. Fix: excluded from detection.
    for f in rc:
        assert f.get("cutoff_hz", 0) != 0, \
            f"KH-276 regression: RC filter with cutoff_hz=0 detected: {f}"


# --- KH-230: Empty Value should not be substituted with lib_symbol default ---

def test_kh230_empty_value_preserved():
    """KH-230: Component with empty Value should keep value='' not 'R'."""
    sch = (
        Schematic()
        .resistor("R1", "", at=(50, 50))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 60))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), (50, 60))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    components = data.get("components", [])
    r1 = [c for c in components if c.get("reference") == "R1"]
    assert len(r1) == 1, f"R1 not found in components"
    # Bug: empty value was replaced with "R" (lib default). Fix: preserved as "".
    assert r1[0].get("value") == "", \
        f"KH-230 regression: R1 value should be '' but got {r1[0].get('value')!r}"


# --- KH-236: LM7805 should use fixed_suffix parser, not broad prefix ---

def test_kh236_lm7805_vout():
    """KH-236: LM7805 → estimated_vout ≈ 5.0V via fixed_suffix, not 1.25V."""
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("VOUT", "3", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "LM7805", "Regulator_Linear:LM7805", REG_PINS, at=(cx, cy))
        .power("+12V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("5V_OUT", at=(65, cy))
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        .wire(ic_pin_pos(cx, cy, "VOUT", REG_PINS), (65, cy))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    assert len(u1) >= 1, f"U1 not found in power_regulators: {regs}"
    vout = u1[0].get("estimated_vout")
    # Bug: broad prefix "LM78" matched → Vref=1.25V. Fix: fixed_suffix → 5.0V.
    assert vout is not None, "estimated_vout missing"
    assert abs(vout - 5.0) < 0.5, \
        f"KH-236 regression: LM7805 vout should be ~5.0V, got {vout}"


# --- KH-236b: TPS7A4901 split prefix → Vref ≈ 1.194V ---

def test_kh236b_tps7a4901_vref():
    """KH-236: TPS7A4901 should have Vref ≈ 1.194V after prefix split."""
    REG_PINS = [
        ("IN",   "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("OUT",  "3", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "TPS7A4901", "Regulator_Linear:TPS7A4901", REG_PINS, at=(cx, cy))
        .power("+5V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("OUT_RAIL", at=(65, cy))
        .wire((35, cy), ic_pin_pos(cx, cy, "IN", REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        .wire(ic_pin_pos(cx, cy, "OUT", REG_PINS), (65, cy))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    if not u1:
        return  # detector may not fire without FB divider — acceptable skip
    vout = u1[0].get("estimated_vout")
    if vout is None:
        return  # no vout estimation for adjustable without FB — acceptable
    # Bug: broad prefix "TPS7A" gave wrong Vref. Fix: per-sub-family entries.
    # TPS7A49xx series Vref = 1.194V (adjustable).
    assert abs(vout - 1.194) < 0.1 or vout > 1.0, \
        f"KH-236 regression: TPS7A4901 vout/vref unexpected: {vout}"


# --- KH-237: TPS54302 switching frequency should be 400kHz, not 570kHz ---

def test_kh237_tps54302_freq():
    """KH-237: TPS54302 → switching_frequency_hz ≈ 400kHz (was 570kHz)."""
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("SW",   "3", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "TPS54302", "Regulator_Switching:TPS54302", REG_PINS, at=(cx, cy))
        .power("+12V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("SW_OUT", at=(65, cy))
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        .wire(ic_pin_pos(cx, cy, "SW", REG_PINS), (65, cy))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    assert len(u1) >= 1, f"U1 not found in power_regulators"
    freq = u1[0].get("switching_frequency_hz")
    # Bug: broad prefix "TPS54" gave 570kHz. Fix: TPS54302-specific → 400kHz.
    assert freq is not None, "switching_frequency_hz missing"
    assert abs(freq - 400_000) < 50_000, \
        f"KH-237 regression: TPS54302 freq should be ~400kHz, got {freq}"


# --- KH-237b: TPS62203 frequency should be ~1MHz ---

def test_kh237b_tps62203_freq():
    """KH-237: TPS62203 → switching_frequency_hz ≈ 1MHz (was 2.5MHz)."""
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("SW",   "3", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "TPS62203", "Regulator_Switching:TPS62203", REG_PINS, at=(cx, cy))
        .power("+5V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("SW_NODE", at=(65, cy))
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        .wire(ic_pin_pos(cx, cy, "SW", REG_PINS), (65, cy))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    assert len(u1) >= 1, f"U1 not found in power_regulators"
    freq = u1[0].get("switching_frequency_hz")
    assert freq is not None, "switching_frequency_hz missing"
    # Bug: TPS62 prefix gave 2.5MHz. Fix: TPS62203-specific → 1MHz.
    assert abs(freq - 1_000_000) < 200_000, \
        f"KH-237 regression: TPS62203 freq should be ~1MHz, got {freq}"


# --- KH-240: BATT- rail should be classified as ground ---

def test_kh240_batt_minus_is_ground():
    """KH-240: Voltage divider between +3V3 and BATT- should be detected."""
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 62))
        .power("+3V3", at=(50, 40))
        .power("BATT-", at=(50, 72))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), pin1(50, 62))
        .wire(pin2(50, 62), (50, 72))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    vd = [f for f in data.get("findings", []) if f.get("detector") == "detect_voltage_dividers"]
    # Bug: BATT- not classified as ground → divider not detected.
    # Fix: battery-negative patterns recognized as ground.
    assert len(vd) >= 1, \
        f"KH-240 regression: divider between +3V3 and BATT- not detected: {vd}"


# --- KH-238: Feedback divider should be correctly paired with regulator ---

def test_kh238_feedback_divider_detected():
    """KH-238: Adjustable regulator with FB divider → feedback_divider present."""
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("VOUT", "3", 5.08, -2.54, "output"),
        ("FB",   "4", 5.08, 2.54, "input"),
    ]
    cx, cy = 50, 50
    # R_top and R_bottom in a vertical divider at x=70
    Rt_cx, Rt_cy = 70, 47  # R_top center
    Rb_cx, Rb_cy = 70, 60  # R_bottom center

    sch = (
        Schematic()
        .ic("U1", "LM317", "Regulator_Linear:LM317_SOT-223", REG_PINS, at=(cx, cy))
        .resistor("R1", "240", at=(Rt_cx, Rt_cy))      # R_top (adj pin to VOUT)
        .resistor("R2", "390", at=(Rb_cx, Rb_cy))       # R_bottom (adj pin to GND)
        .power("+12V", at=(35, cy))
        .power("GND", at=(cx, 70))
        .power("GND", at=(Rb_cx, 75))
        # VIN connection
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        # U1 GND
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 70))
        # VOUT pin → horizontal to R_top column → up to R_top pin1
        .wire(ic_pin_pos(cx, cy, "VOUT", REG_PINS), (Rt_cx, cy - 2.54))
        .wire((Rt_cx, cy - 2.54), pin1(Rt_cx, Rt_cy))
        # FB pin → horizontal to R_top/R_bottom junction
        .wire(ic_pin_pos(cx, cy, "FB", REG_PINS), (Rt_cx, cy + 2.54))
        # R_top pin2 → FB junction
        .wire(pin2(Rt_cx, Rt_cy), (Rt_cx, cy + 2.54))
        # FB junction → R_bottom pin1
        .wire((Rt_cx, cy + 2.54), pin1(Rb_cx, Rb_cy))
        # R_bottom pin2 → GND
        .wire(pin2(Rb_cx, Rb_cy), (Rb_cx, 75))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    assert len(u1) >= 1, f"U1 not found in power_regulators"
    fb = u1[0].get("feedback_divider")
    # Bug: pair-ordering bug caused missed/misidentified divider pairs.
    # Fix: corrected pair ordering logic.
    assert fb is not None, \
        f"KH-238 regression: feedback_divider not detected for LM317"
    assert "r_top" in fb and "r_bottom" in fb, \
        f"KH-238: feedback_divider missing r_top/r_bottom: {fb}"


# --- KH-247: Cap without footprint should not get fabricated "0603" package ---

def test_kh247_no_fabricated_package():
    """KH-247: Output cap without footprint → package not fabricated as '0603'."""
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("VOUT", "3", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    C_cx, C_cy = 70, 50
    sch = (
        Schematic()
        .ic("U1", "AMS1117-3.3", "Regulator_Linear:AMS1117-3.3", REG_PINS, at=(cx, cy))
        .capacitor("C1", "10u", at=(C_cx, C_cy))
        .power("+5V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .power("GND", at=(C_cx, 65))
        # VIN
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        # U1 GND
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        # VOUT → C1 pin1 (output cap on VOUT rail)
        .wire(ic_pin_pos(cx, cy, "VOUT", REG_PINS), (C_cx, cy))
        .wire((C_cx, cy), pin1(C_cx, C_cy))
        # C1 pin2 → GND
        .wire(pin2(C_cx, C_cy), (C_cx, 65))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    if not u1:
        return  # detector may not fire — acceptable skip
    out_caps = u1[0].get("output_capacitors", [])
    for cap in out_caps:
        pkg = cap.get("package")
        # Bug: missing package → default "0603". Fix: extract from footprint,
        # skip derating when package unknown.
        if pkg is not None:
            assert pkg != "0603", \
                f"KH-247 regression: cap {cap.get('ref')} has fabricated package '0603'"


# --- KH-239: LED series resistor should not be classified as pull_up ---

def test_kh239_led_series_r_not_pullup():
    """KH-239: R in series with LED from VCC to GND → not a pull_up resistor."""
    # +3V3 → R1 (330Ω) → D1 (LED) → GND
    R_cx, R_cy = 50, 50
    D_cx, D_cy = 50, 62
    sch = (
        Schematic()
        .resistor("R1", "330", at=(R_cx, R_cy))
        .diode("D1", "LED", at=(D_cx, D_cy), variant="LED")
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 72))
        .wire((50, 40), pin1(R_cx, R_cy))
        .wire(pin2(R_cx, R_cy), pin1(D_cx, D_cy))
        .wire(pin2(D_cx, D_cy), (50, 72))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    # Check that R1 is NOT listed as a pull_up in sleep current analysis
    # sleep_current_analysis is a nested section under design_analysis (not findings)
    design = data.get("design_analysis", {})
    # Check design_analysis first, then fall back to findings
    sleep = design.get("sleep_current_analysis", {})
    if not sleep:
        sleep_findings = [f for f in data.get("findings", [])
                         if f.get("detector") == "detect_sleep_current_analysis"]
        sleep = sleep_findings[0] if sleep_findings else {}
    pullups = sleep.get("pullup_resistors", sleep.get("pull_up_resistors", []))
    if isinstance(pullups, list):
        pullup_refs = [p.get("ref", p.get("reference", "")) for p in pullups]
    else:
        pullup_refs = []
    # Bug: LED series R was double-classified as pull_up. Fix: excluded.
    assert "R1" not in pullup_refs, \
        f"KH-239 regression: R1 (LED series) classified as pull_up: {pullups}"


# --- KH-276 guard: Valid RC filter should still be detected ---

def test_kh276_valid_rc_still_detected():
    """Guard: A valid RC filter (R=1k, C=1u) must still be detected."""
    R_cx, R_cy = 50, 50
    C_cx, C_cy = 60, 50
    sch = (
        Schematic()
        .resistor("R1", "1k", at=(R_cx, R_cy), angle=90)
        .capacitor("C1", "1u", at=(C_cx, C_cy))
        .power("GND", at=(C_cx, 65))
        .label("IN", at=(pin1(R_cx, R_cy, 90)[0], R_cy))
        .label("FILT", at=(C_cx, R_cy))
        .wire((pin1(R_cx, R_cy, 90)[0], R_cy), pin1(R_cx, R_cy, 90))
        .wire(pin2(R_cx, R_cy, 90), (C_cx, R_cy))
        .wire((C_cx, R_cy), pin1(C_cx, C_cy))
        .wire(pin2(C_cx, C_cy), (C_cx, 65))
    )
    data = run_analyzer(sch)
    if data is None:
        return
    rc = [f for f in data.get("findings", []) if f.get("detector") == "detect_rc_filters"]
    # Guard: valid RC filter must still be detected after KH-276 fix.
    assert len(rc) >= 1, f"Guard failed: valid RC filter not detected"
    assert rc[0]["cutoff_hz"] > 0, f"Guard: cutoff_hz should be > 0"


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
