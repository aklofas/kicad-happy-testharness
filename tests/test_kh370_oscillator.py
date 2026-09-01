"""KH-370 (GitHub #33) — description-substring oscillator misclassification.

An IC whose symbol Description merely mentions a built-in "internal
oscillator" (common ADC/MCU/sensor datasheet phrasing) was reclassified
from "ic" to "oscillator" by the KH-220 description-substring branch in
kicad_utils.classify_component(). That misclassification cascaded into two
false findings: XL-DET `active_oscillator` (detect_crystal_circuits has an
unconditional include for type=="oscillator") and CD-DET `oscillator_output`
(the XL-DET fallback picked the IC's first non-power pin — an I2C SCL net on
a bus peripheral — as a fabricated clock output_net, which CD-DET phase 2
then traced to a bogus "consumer").

Minimal pair recreated from the verified 2026-08-01 repro in
kicad-happy-testharness ISSUES.md KH-370: U1 = 5-pin I2C ADC (SCL/SDA/GND/
VDD/AIN0) with a real-world-style description mentioning an internal
oscillator; U2 = generic MCU sharing the I2C bus via local labels.
"""
TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import pytest
except ImportError:  # pre-push hook runs root tests under bare python3 (no
    # pytest); only decorator applications happen at import time, so a no-op
    # stand-in keeps the file importable — the tests themselves need pytest.
    class _StubMark:
        @staticmethod
        def skipif(*_a, **_k):
            return lambda fn: fn

    class _StubPytest:
        mark = _StubMark

        @staticmethod
        def fixture(*_a, **_k):
            return lambda fn: fn

        @staticmethod
        def skip(reason=""):
            raise SystemExit(0)

    pytest = _StubPytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, ic_pin_pos

HARNESS_DIR = Path(__file__).resolve().parent.parent

BUG_DESCRIPTION = ("Low-Power, I2C-Compatible ADC With Internal Reference, "
                    "Oscillator, and Programmable Comparator")
CONTROL_DESCRIPTION = ("Low-Power, I2C-Compatible ADC With Internal Reference, "
                        "and Programmable Comparator")

ADC_PINS = [
    ("SCL",  "1", -7.62, -2.54, "input"),
    ("SDA",  "2", -7.62,  2.54, "input"),
    ("GND",  "3", 0,  7.62, "power_in"),
    ("VDD",  "4", 0, -7.62, "power_in"),
    ("AIN0", "5",  7.62,  0, "input"),
]
MCU_PINS = [
    ("SCL",  "1", -7.62, -2.54, "input"),
    ("SDA",  "2", -7.62,  2.54, "input"),
    ("GND",  "3", 0,  7.62, "power_in"),
    ("VDD",  "4", 0, -7.62, "power_in"),
]


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


def _build_two_ic_schematic(adc_description):
    """U1 = I2C ADC (given description) sharing SCL/SDA with U2 = generic MCU."""
    cx1, cy1 = 50, 50
    cx2, cy2 = 90, 50
    sch = (
        Schematic()
        .ic("U1", "ADC_I2C", "Analog_ADC:GenericI2CADC", ADC_PINS,
            at=(cx1, cy1), description=adc_description)
        .ic("U2", "MCU_Generic", "MCU_Generic:MCU_Generic", MCU_PINS, at=(cx2, cy2))
        .power("+3V3", at=(cx1, 30))
        .power("GND", at=(cx1, 70))
        .power("+3V3", at=(cx2, 30))
        .power("GND", at=(cx2, 70))
        # U1 power
        .wire(ic_pin_pos(cx1, cy1, "VDD", ADC_PINS), (cx1, 30))
        .wire(ic_pin_pos(cx1, cy1, "GND", ADC_PINS), (cx1, 70))
        # U2 power
        .wire(ic_pin_pos(cx2, cy2, "VDD", MCU_PINS), (cx2, 30))
        .wire(ic_pin_pos(cx2, cy2, "GND", MCU_PINS), (cx2, 70))
        # I2C bus: SCL/SDA joined via same-named local labels (not a direct wire)
        .wire(ic_pin_pos(cx1, cy1, "SCL", ADC_PINS),
              (ic_pin_pos(cx1, cy1, "SCL", ADC_PINS)[0] - 5, cy1 - 2.54))
        .label("SCL", at=(ic_pin_pos(cx1, cy1, "SCL", ADC_PINS)[0] - 5, cy1 - 2.54))
        .wire(ic_pin_pos(cx1, cy1, "SDA", ADC_PINS),
              (ic_pin_pos(cx1, cy1, "SDA", ADC_PINS)[0] - 5, cy1 + 2.54))
        .label("SDA", at=(ic_pin_pos(cx1, cy1, "SDA", ADC_PINS)[0] - 5, cy1 + 2.54))
        .wire(ic_pin_pos(cx2, cy2, "SCL", MCU_PINS),
              (ic_pin_pos(cx2, cy2, "SCL", MCU_PINS)[0] - 5, cy2 - 2.54))
        .label("SCL", at=(ic_pin_pos(cx2, cy2, "SCL", MCU_PINS)[0] - 5, cy2 - 2.54))
        .wire(ic_pin_pos(cx2, cy2, "SDA", MCU_PINS),
              (ic_pin_pos(cx2, cy2, "SDA", MCU_PINS)[0] - 5, cy2 + 2.54))
        .label("SDA", at=(ic_pin_pos(cx2, cy2, "SDA", MCU_PINS)[0] - 5, cy2 + 2.54))
    )
    return sch


@pytest.fixture(scope="module")
def bug_data():
    data = run_analyzer(_build_two_ic_schematic(BUG_DESCRIPTION))
    if data is None:
        pytest.skip("kicad-happy analyzer not available")
    return data


@pytest.fixture(scope="module")
def control_data():
    data = run_analyzer(_build_two_ic_schematic(CONTROL_DESCRIPTION))
    if data is None:
        pytest.skip("kicad-happy analyzer not available")
    return data


def test_kh370_internal_oscillator_adc_stays_ic(bug_data):
    """KH-370: an I2C ADC whose description just mentions an internal
    reference/oscillator must stay classified as "ic", not "oscillator"."""
    u1 = [c for c in bug_data.get("components", []) if c.get("reference") == "U1"]
    assert len(u1) == 1, f"U1 not found in components"
    assert u1[0].get("type") == "ic", \
        f"KH-370 regression: U1 misclassified as {u1[0].get('type')!r}, expected 'ic'"


def test_kh370_internal_oscillator_no_xldet_finding(bug_data):
    """KH-370: no false XL-DET active_oscillator finding for U1."""
    findings = bug_data.get("findings", [])
    osc = [f for f in findings
           if f.get("detector") == "detect_crystal_circuits"
           and f.get("type") == "active_oscillator"
           and f.get("reference") == "U1"]
    assert osc == [], f"KH-370 regression: false XL-DET active_oscillator for U1: {osc}"


def test_kh370_internal_oscillator_no_cddet_finding(bug_data):
    """KH-370: no false CD-DET oscillator_output finding for U1 (the XL-DET
    fallback must not have fabricated an output_net from the SCL pin)."""
    findings = bug_data.get("findings", [])
    clk = [f for f in findings
           if f.get("detector") == "detect_clock_distribution"
           and f.get("type") == "oscillator_output"
           and f.get("ref") == "U1"]
    assert clk == [], f"KH-370 regression: false CD-DET oscillator_output for U1: {clk}"


def test_kh370_control_unaffected(control_data):
    """Control: description without "Oscillator" must not regress —
    U1 stays "ic" with zero XL-DET/CD-DET findings, same as the fixed bug case."""
    u1 = [c for c in control_data.get("components", []) if c.get("reference") == "U1"]
    assert len(u1) == 1
    assert u1[0].get("type") == "ic"
    findings = control_data.get("findings", [])
    osc = [f for f in findings
           if f.get("detector") == "detect_crystal_circuits"
           and f.get("type") == "active_oscillator" and f.get("reference") == "U1"]
    clk = [f for f in findings
           if f.get("detector") == "detect_clock_distribution"
           and f.get("type") == "oscillator_output" and f.get("ref") == "U1"]
    assert osc == []
    assert clk == []


# --- True-positive guard: a real active-oscillator IC must still classify
# as "oscillator" — the KH-370 fix must not blanket-suppress legitimate
# oscillator detection (real-world phrasing: SiTime/Abracon-style MEMS/
# programmable oscillator datasheets), corroborated by both an "OUT"-named
# pin and a pin count <= 4.

TP_DESCRIPTION = "Programmable Oscillator, 25MHz, LVCMOS Output"
TP_PINS = [
    ("VDD", "1", 0, -7.62, "power_in"),
    ("GND", "2", 0,  7.62, "power_in"),
    ("OE",  "3", -7.62, 0, "input"),
    ("OUT", "4",  7.62, 0, "output"),
]


def test_kh370_true_positive_oscillator_still_classifies():
    """True-positive guard: a genuine oscillator IC (OUT-named pin, <=4 pins,
    no internal-oscillator/internal-reference exclusion phrasing) must still
    classify as "oscillator"."""
    cx, cy = 50, 50
    sch = (
        Schematic()
        .ic("U1", "OSC25M", "Oscillator_Generic:OSC25M", TP_PINS,
            at=(cx, cy), description=TP_DESCRIPTION)
        .power("+3V3", at=(cx, 30))
        .power("GND", at=(cx, 70))
        .wire(ic_pin_pos(cx, cy, "VDD", TP_PINS), (cx, 30))
        .wire(ic_pin_pos(cx, cy, "GND", TP_PINS), (cx, 70))
    )
    data = run_analyzer(sch)
    if data is None:
        pytest.skip("kicad-happy analyzer not available")
    u1 = [c for c in data.get("components", []) if c.get("reference") == "U1"]
    assert len(u1) == 1, "U1 not found in components"
    assert u1[0].get("type") == "oscillator", \
        f"True-positive regression: U1 should classify 'oscillator', got {u1[0].get('type')!r}"
