"""Unit tests for tests/fixtures/_build_sch.py — KiCad schematic builder."""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, pin1, pin2, _PIN_OFFSET


def test_empty_schematic_is_valid_sexp():
    sch = Schematic()
    text = sch.render()
    assert text.startswith("(kicad_sch")
    assert "(lib_symbols" in text
    assert text.strip().endswith(")")


def test_resistor_produces_symbol():
    sch = Schematic().resistor("R1", "10k", at=(50, 50))
    text = sch.render()
    assert '"R1"' in text
    assert '"10k"' in text
    assert 'lib_id "Device:R"' in text


def test_capacitor_produces_symbol():
    sch = Schematic().capacitor("C1", "100n", at=(60, 60))
    text = sch.render()
    assert '"C1"' in text
    assert '"100n"' in text
    assert 'lib_id "Device:C"' in text


def test_wire_produces_wire_sexp():
    sch = Schematic().wire((50, 50), (50, 60))
    text = sch.render()
    assert "(wire" in text
    assert "xy 50" in text


def test_power_produces_power_symbol():
    sch = Schematic().power("GND", at=(50, 80))
    text = sch.render()
    assert "GND" in text
    assert "(power)" in text


def test_label_produces_label_sexp():
    sch = Schematic().label("MID", at=(55, 60))
    text = sch.render()
    assert '(label "MID"' in text


def test_write_creates_file():
    sch = Schematic().resistor("R1", "10k", at=(50, 50))
    with tempfile.TemporaryDirectory() as tmp:
        path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        assert Path(path).exists()
        assert Path(path).stat().st_size > 100


def test_pin1_vertical():
    assert pin1(50, 50, 0) == (50, round(50 - _PIN_OFFSET, 4))


def test_pin2_vertical():
    assert pin2(50, 50, 0) == (50, round(50 + _PIN_OFFSET, 4))


def test_pin1_horizontal():
    assert pin1(50, 50, 90) == (round(50 - _PIN_OFFSET, 4), 50)


def test_pin2_horizontal():
    assert pin2(50, 50, 90) == (round(50 + _PIN_OFFSET, 4), 50)


def test_analyzer_accepts_output():
    """The analyzer should parse our generated schematic without crashing."""
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 60))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 70))
        .wire(pin1(50, 50), (50, 40))       # R1 pin1 to +3V3
        .wire(pin2(50, 50), pin1(50, 60))    # R1 pin2 to R2 pin1
        .wire(pin2(50, 60), (50, 70))        # R2 pin2 to GND
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        kh_dir = os.environ.get("KICAD_HAPPY_DIR",
                    str(Path(__file__).resolve().parent.parent.parent / "kicad-happy"))
        script = Path(kh_dir) / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
        if not script.exists():
            return  # skip if kicad-happy not available
        out_json = str(Path(tmp) / "output.json")
        result = subprocess.run(
            [sys.executable, str(script), path, "--output", out_json],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Analyzer failed: {result.stderr[:300]}"
        data = json.loads(Path(out_json).read_text(encoding="utf-8"))
        assert "components" in data
        # Should find R1 and R2 (power symbols may or may not be in components)
        refs = [c["reference"] for c in data["components"]]
        assert "R1" in refs, f"R1 not found in {refs}"
        assert "R2" in refs, f"R2 not found in {refs}"


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
