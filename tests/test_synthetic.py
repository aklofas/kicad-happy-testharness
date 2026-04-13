"""Synthetic detector fixtures — voltage dividers and RC filters."""

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


def test_vd_equal_divider():
    """R1=R2=10k between +3V3 and GND — should detect 1 divider with ratio ≈ 0.5."""
    # Layout: +3V3 at (50,40), R1 at (50,50), R2 at (50,62), GND at (50,72)
    # Spacing >=10mm between resistor centers
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 62))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 72))
        # +3V3 pin at (50,40), R1 pin1 at pin1(50,50) = (50, 46.19)
        .wire((50, 40), pin1(50, 50))
        # R1 pin2 to R2 pin1
        .wire(pin2(50, 50), pin1(50, 62))
        # R2 pin2 to GND pin at (50,72)
        .wire(pin2(50, 62), (50, 72))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    vd = data.get("signal_analysis", {}).get("voltage_dividers", [])
    assert len(vd) == 1, f"Expected 1 divider, got {len(vd)}: {vd}"
    ratio = vd[0]["ratio"]
    assert abs(ratio - 0.5) <= 0.05, f"Expected ratio ≈ 0.5, got {ratio}"


def test_vd_unequal_divider():
    """R1=10k, R2=22k between +5V and GND — ratio ≈ 22/32 = 0.6875."""
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "22k", at=(50, 62))
        .power("+5V", at=(50, 40))
        .power("GND", at=(50, 72))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), pin1(50, 62))
        .wire(pin2(50, 62), (50, 72))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    vd = data.get("signal_analysis", {}).get("voltage_dividers", [])
    assert len(vd) == 1, f"Expected 1 divider, got {len(vd)}: {vd}"
    expected = 22 / (10 + 22)  # 0.6875
    ratio = vd[0]["ratio"]
    assert abs(ratio - expected) <= 0.05, f"Expected ratio ≈ {expected:.4f}, got {ratio}"


def test_vd_negative_pullup():
    """Single R1=10k from +3V3 to a signal label — not a divider (no bottom R to GND)."""
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .power("+3V3", at=(50, 40))
        .label("SIG", at=(50, 58))
        .wire((50, 40), pin1(50, 50))
        # R1 pin2 connects to a signal label (no path to GND)
        .wire(pin2(50, 50), (50, 58))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    vd = data.get("signal_analysis", {}).get("voltage_dividers", [])
    assert len(vd) == 0, f"Expected 0 dividers (pull-up only), got {len(vd)}: {vd}"


def test_vd_negative_series_r():
    """R1=100 ohm in series on a signal line (IN → R → OUT), no power/ground — not a divider."""
    # Horizontal resistor: pin1 at left, pin2 at right
    sch = (
        Schematic()
        .resistor("R1", "100", at=(50, 50), angle=90)
        .label("IN",  at=(pin1(50, 50, 90)[0], 50))
        .label("OUT", at=(pin2(50, 50, 90)[0], 50))
        # IN label at pin1 position, OUT label at pin2 position
        .wire((pin1(50, 50, 90)[0], 50), pin1(50, 50, 90))
        .wire(pin2(50, 50, 90), (pin2(50, 50, 90)[0], 50))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    vd = data.get("signal_analysis", {}).get("voltage_dividers", [])
    assert len(vd) == 0, f"Expected 0 dividers (series R only), got {len(vd)}: {vd}"


# === RC Filter Tests ===

def test_rc_lowpass():
    """R1=1k + C1=1uF: IN → R → junction(FILT) → C → GND — low-pass filter detected."""
    # Topology: IN label at (40,50) → R1 horizontal pin1(43.19,50) → R1 pin2(56.81,50)
    # → FILT label (junction at 60,50) → C1 vertical pin1(60,46.19) → C1 pin2(60,53.81)
    # → GND at (60,63.81).  Shared net is FILT (signal net, not power/ground).
    #
    # Use angle=90 for R1 (horizontal): pin1 at (cx-3.81, cy), pin2 at (cx+3.81, cy)
    # Use angle=0 for C1 (vertical): pin1 at (cx, cy-3.81), pin2 at (cx, cy+3.81)
    R1_cx, R1_cy = 50, 50
    C1_cx, C1_cy = 60, 50

    sch = (
        Schematic()
        .resistor("R1", "1k", at=(R1_cx, R1_cy), angle=90)
        .capacitor("C1", "1u", at=(C1_cx, C1_cy))
        .power("GND", at=(C1_cx, 65))
        # IN label at R1 pin1 x-position
        .label("IN", at=(pin1(R1_cx, R1_cy, 90)[0], R1_cy))
        # FILT label at junction between R1 pin2 and C1 pin1
        .label("FILT", at=(C1_cx, R1_cy))
        # Wire: IN label → R1 pin1
        .wire((pin1(R1_cx, R1_cy, 90)[0], R1_cy), pin1(R1_cx, R1_cy, 90))
        # Wire: R1 pin2 → FILT junction
        .wire(pin2(R1_cx, R1_cy, 90), (C1_cx, R1_cy))
        # Wire: FILT junction → C1 pin1 (top of capacitor)
        .wire((C1_cx, R1_cy), pin1(C1_cx, C1_cy))
        # Wire: C1 pin2 → GND
        .wire(pin2(C1_cx, C1_cy), (C1_cx, 65))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    rc = data.get("signal_analysis", {}).get("rc_filters", [])
    assert len(rc) >= 1, f"Expected ≥1 RC filter, got {len(rc)}: {rc}"
    assert rc[0]["cutoff_hz"] > 0, f"Expected cutoff_hz > 0, got {rc[0]['cutoff_hz']}"
    assert rc[0]["type"] == "low-pass", f"Expected low-pass, got {rc[0]['type']}"


def test_rc_highpass():
    """C1=100n + R1=10k: IN → C → junction(FILT) → R → GND — high-pass filter detected."""
    # Topology: signal flows through C, then R to GND.
    # C1 horizontal (angle=90): pin1 at (cx-3.81, cy), pin2 at (cx+3.81, cy)
    # R1 vertical (angle=0): pin1 at (cx, cy-3.81), pin2 at (cx, cy+3.81)
    # Junction node FILT is the shared signal net between C pin2 and R pin1.
    C1_cx, C1_cy = 50, 50
    R1_cx, R1_cy = 60, 50

    sch = (
        Schematic()
        .capacitor("C1", "100n", at=(C1_cx, C1_cy), angle=90)
        .resistor("R1", "10k", at=(R1_cx, R1_cy))
        .power("GND", at=(R1_cx, 65))
        # IN label at C1 pin1 x-position
        .label("IN", at=(pin1(C1_cx, C1_cy, 90)[0], C1_cy))
        # FILT label at junction between C1 pin2 and R1 pin1
        .label("FILT", at=(R1_cx, C1_cy))
        # Wire: IN label → C1 pin1
        .wire((pin1(C1_cx, C1_cy, 90)[0], C1_cy), pin1(C1_cx, C1_cy, 90))
        # Wire: C1 pin2 → FILT junction
        .wire(pin2(C1_cx, C1_cy, 90), (R1_cx, C1_cy))
        # Wire: FILT junction → R1 pin1 (top of resistor)
        .wire((R1_cx, C1_cy), pin1(R1_cx, R1_cy))
        # Wire: R1 pin2 → GND
        .wire(pin2(R1_cx, R1_cy), (R1_cx, 65))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    rc = data.get("signal_analysis", {}).get("rc_filters", [])
    assert len(rc) >= 1, f"Expected ≥1 RC filter, got {len(rc)}: {rc}"
    assert rc[0]["cutoff_hz"] > 0, f"Expected cutoff_hz > 0, got {rc[0]['cutoff_hz']}"
    assert rc[0]["type"] == "high-pass", f"Expected high-pass, got {rc[0]['type']}"


def test_rc_negative_bypass_cap():
    """C1=100n between +3V3 and GND only — bypass cap, NOT an RC filter (no resistor)."""
    sch = (
        Schematic()
        .capacitor("C1", "100n", at=(50, 50))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 60))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), (50, 60))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    rc = data.get("signal_analysis", {}).get("rc_filters", [])
    assert len(rc) == 0, f"Expected 0 RC filters (bypass cap only), got {len(rc)}: {rc}"


def test_rc_negative_rc_snubber_like():
    """R1=100R and C1=10n in parallel (same two nets A↔B) — NOT detected as RC filter."""
    # Both R and C connect between net A (SNUB_A label) and net B (SNUB_B label).
    # The detector requires len(shared_nets)==1; two shared nets → skipped.
    R1_cx, R1_cy = 50, 50
    C1_cx, C1_cy = 50, 65

    sch = (
        Schematic()
        .resistor("R1", "100", at=(R1_cx, R1_cy))
        .capacitor("C1", "10n", at=(C1_cx, C1_cy))
        .label("SNUB_A", at=(50, 35))
        .label("SNUB_B", at=(50, 80))
        # Wire: SNUB_A → R1 pin1
        .wire((50, 35), pin1(R1_cx, R1_cy))
        # Wire: R1 pin2 → SNUB_B
        .wire(pin2(R1_cx, R1_cy), (50, 80))
        # Wire: SNUB_A → C1 pin1 (parallel path)
        .wire((50, 35), pin1(C1_cx, C1_cy))
        # Wire: C1 pin2 → SNUB_B (parallel path)
        .wire(pin2(C1_cx, C1_cy), (50, 80))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    rc = data.get("signal_analysis", {}).get("rc_filters", [])
    assert len(rc) == 0, f"Expected 0 RC filters (parallel R+C snubber), got {len(rc)}: {rc}"


# === Deferred Stubs (need IC/crystal/diode builder support) ===

def test_reg_positive_by_value():
    """AMS1117-3.3 LDO with VIN/VOUT/GND — should detect power regulator."""
    REG_PINS = [
        ("VIN",  "3", -5.08, 0, "input"),
        ("GND",  "1", 0, 5.08, "power_in"),
        ("VOUT", "2", 5.08, 0, "output"),
    ]
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "AMS1117-3.3", "Regulator_Linear:AMS1117-3.3", REG_PINS, at=(cx, cy))
        .power("+5V", at=(35, cy))
        .power("GND", at=(cx, 65))
        .label("3V3_OUT", at=(65, cy))
        # +5V → VIN
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        # GND pin → GND symbol
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 65))
        # VOUT → 3V3_OUT label
        .wire(ic_pin_pos(cx, cy, "VOUT", REG_PINS), (65, cy))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    regs = data.get("signal_analysis", {}).get("power_regulators", [])
    assert len(regs) >= 1, f"Expected ≥1 regulator, got {len(regs)}: {regs}"
    refs = [r["ref"] for r in regs]
    assert "U1" in refs, f"U1 not found in regulators: {refs}"


def test_crystal_positive():
    """16MHz crystal with two 18pF load caps to GND — should detect crystal circuit."""
    # Y1 horizontal (angle=90), C1 and C2 vertical beneath each crystal pin
    Y1_cx, Y1_cy = 50, 50
    C1_cx, C1_cy = pin1(Y1_cx, Y1_cy, 90)[0], 60  # under pin1
    C2_cx, C2_cy = pin2(Y1_cx, Y1_cy, 90)[0], 60  # under pin2

    sch = (
        Schematic()
        .crystal("Y1", "16MHz", at=(Y1_cx, Y1_cy), angle=90)
        .capacitor("C1", "18p", at=(C1_cx, C1_cy))
        .capacitor("C2", "18p", at=(C2_cx, C2_cy))
        .power("GND", at=(C1_cx, 70))
        .power("GND", at=(C2_cx, 70))
        # Y1 pin1 → C1 pin1 (vertical wire)
        .wire(pin1(Y1_cx, Y1_cy, 90), pin1(C1_cx, C1_cy))
        # Y1 pin2 → C2 pin1 (vertical wire)
        .wire(pin2(Y1_cx, Y1_cy, 90), pin1(C2_cx, C2_cy))
        # C1 pin2 → GND
        .wire(pin2(C1_cx, C1_cy), (C1_cx, 70))
        # C2 pin2 → GND
        .wire(pin2(C2_cx, C2_cy), (C2_cx, 70))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    cc = data.get("signal_analysis", {}).get("crystal_circuits", [])
    assert len(cc) >= 1, f"Expected ≥1 crystal circuit, got {len(cc)}: {cc}"
    y1 = [c for c in cc if c.get("reference") == "Y1"]
    assert len(y1) == 1, f"Y1 not found in crystal circuits: {cc}"
    assert y1[0].get("frequency", 0) > 0, f"Expected frequency > 0"


def test_protection_positive():
    """TVS diode between signal and GND — should detect protection device."""
    D_cx, D_cy = 50, 50
    sch = (
        Schematic()
        .diode("D1", "PESD5V0S1BA", at=(D_cx, D_cy), variant="D_TVS")
        .label("USB_D+", at=(D_cx, 40))
        .power("GND", at=(D_cx, 60))
        # Signal → D1 cathode (pin1)
        .wire((D_cx, 40), pin1(D_cx, D_cy))
        # D1 anode (pin2) → GND
        .wire(pin2(D_cx, D_cy), (D_cx, 60))
    )
    data = run_analyzer(sch)
    if data is None:
        print("  SKIP: kicad-happy not available")
        return
    pd = data.get("signal_analysis", {}).get("protection_devices", [])
    assert len(pd) >= 1, f"Expected ≥1 protection device, got {len(pd)}: {pd}"
    d1 = [d for d in pd if d.get("ref") == "D1"]
    assert len(d1) == 1, f"D1 not found in protection devices: {pd}"


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = skipped = 0
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
