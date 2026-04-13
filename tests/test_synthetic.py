"""Synthetic detector fixtures — voltage dividers."""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, pin1, pin2

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
