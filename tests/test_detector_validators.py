"""Unit tests for validate_* detectors in validation_detectors.py.

Each test builds a minimal AnalysisContext using fixtures._build_ctx and
invokes a single validator directly, checking that the produced findings
have the expected rule_id and reference the expected components/nets.

Fixtures are kept small: one or two nets, one or two ICs. This isolates
each detector's logic without invoking the schematic parser.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR / "tests"))

_KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy"))
_SCRIPTS = Path(_KICAD_HAPPY) / "skills" / "kicad" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from fixtures._build_ctx import build_ctx, ic, resistor, capacitor  # noqa: E402


def _skip_if_no_kh():
    if not (_SCRIPTS / "validation_detectors.py").exists():
        return True
    return False


# ---------------------------------------------------------------------------
# validate_pullups — PU-001
# ---------------------------------------------------------------------------

def test_validate_pullups_missing_on_nrst():
    """NRST pin with no pull-up should produce PU-001."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_pullups

    ctx = build_ctx(
        components=[ic("U1", "STM32F103", [("1", "VDD"), ("2", "VSS"),
                                            ("7", "NRST")])],
        nets={
            "+3V3":     [("U1", "1")],
            "GND":      [("U1", "2")],
            "RESET":    [("U1", "7")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_pullups(ctx)
    pu_findings = [f for f in findings if f.get("rule_id") == "PU-001"]
    assert pu_findings, f"Expected PU-001 for missing pull-up, got {findings}"
    assert any("U1" in f.get("components", []) for f in pu_findings)


def test_validate_pullups_present_on_nrst_no_finding():
    """NRST pin with a 10k pull-up should NOT produce PU-001."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_pullups

    ctx = build_ctx(
        components=[
            ic("U1", "STM32F103", [("1", "VDD"), ("2", "VSS"), ("7", "NRST")]),
            resistor("R1", "10k"),
        ],
        nets={
            "+3V3":   [("U1", "1"), ("R1", "1")],
            "GND":    [("U1", "2")],
            "RESET":  [("U1", "7"), ("R1", "2")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_pullups(ctx)
    pu_findings = [f for f in findings if f.get("rule_id") == "PU-001"
                   and "U1" in f.get("components", [])
                   and "too low" not in f.get("summary", "").lower()]
    assert not pu_findings, f"Unexpected PU-001 when pull-up present: {pu_findings}"


def test_validate_pullups_value_too_low():
    """NRST with 100R pull-up should produce PU-001 'value too low'."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_pullups

    ctx = build_ctx(
        components=[
            ic("U1", "STM32F103", [("1", "VDD"), ("2", "VSS"), ("7", "NRST")]),
            resistor("R1", "100"),  # 100 ohms — below PULLUP_MIN (1000 ohms)
        ],
        nets={
            "+3V3":   [("U1", "1"), ("R1", "1")],
            "GND":    [("U1", "2")],
            "RESET":  [("U1", "7"), ("R1", "2")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_pullups(ctx)
    low_findings = [f for f in findings if f.get("rule_id") == "PU-001"
                    and "too low" in f.get("summary", "").lower()]
    assert low_findings, f"Expected 'value too low' PU-001, got {findings}"


# ---------------------------------------------------------------------------
# validate_voltage_levels — VM-001
# NOTE: The plan spec listed rule_id as VL-001, but the actual validator emits
# VM-001 (see validation_detectors.py:498). Tests use VM-001 to match reality.
# ---------------------------------------------------------------------------

def test_validate_voltage_levels_no_shift_required():
    """3V3 MCU talking to 3V3 peripheral — no VM-001."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_voltage_levels

    ctx = build_ctx(
        components=[
            ic("U1", "STM32F103", [("1", "VDD"), ("2", "VSS"),
                                    ("3", "SDA"), ("4", "SCL")]),
            ic("U2", "LSM303D",   [("1", "VDD"), ("2", "VSS"),
                                    ("3", "SDA"), ("4", "SCL")]),
        ],
        nets={
            "+3V3": [("U1", "1"), ("U2", "1")],
            "GND":  [("U1", "2"), ("U2", "2")],
            "SDA":  [("U1", "3"), ("U2", "3")],
            "SCL":  [("U1", "4"), ("U2", "4")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_voltage_levels(ctx)
    vm = [f for f in findings if f.get("rule_id") == "VM-001"]
    assert not vm, f"Unexpected VM-001 when rails match: {vm}"


def test_validate_voltage_levels_signature_returns_list():
    """Sanity: even with no ICs, returns an empty list (no crash)."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_voltage_levels

    ctx = build_ctx(components=[], nets={}, known_power_rails=set())
    findings = validate_voltage_levels(ctx)
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# validate_i2c_bus — I2C-001..
# ---------------------------------------------------------------------------

def test_validate_i2c_bus_returns_list_shape():
    """Empty ctx returns list without crashing."""
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_i2c_bus
    ctx = build_ctx(components=[], nets={}, known_power_rails=set())
    assert isinstance(validate_i2c_bus(ctx), list)


def test_validate_i2c_bus_two_devices_same_address():
    """Two I2C devices with identical MPN → smoke test (no crash, returns list).

    Builds two copies of the same I2C sensor sharing SDA/SCL. Deep validator
    logic depends on an upstream MPN→address database which may or may not
    have an entry for BMP280; this test only confirms signature stability.
    """
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_i2c_bus

    ctx = build_ctx(
        components=[
            ic("U1", "BMP280", [("1", "VDD"), ("2", "GND"),
                                 ("3", "SDA"), ("4", "SCL")],
               lib_id="Sensor:BMP280", mpn="BMP280"),
            ic("U2", "BMP280", [("1", "VDD"), ("2", "GND"),
                                 ("3", "SDA"), ("4", "SCL")],
               lib_id="Sensor:BMP280", mpn="BMP280"),
        ],
        nets={
            "+3V3": [("U1", "1"), ("U2", "1")],
            "GND":  [("U1", "2"), ("U2", "2")],
            "SDA":  [("U1", "3"), ("U2", "3")],
            "SCL":  [("U1", "4"), ("U2", "4")],
        },
        known_power_rails={"+3V3", "GND"},
    )
    findings = validate_i2c_bus(ctx)
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# validate_spi_bus, validate_can_bus, validate_usb_bus — smoke tests
# ---------------------------------------------------------------------------

def test_validate_spi_bus_empty_ctx():
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_spi_bus
    assert isinstance(validate_spi_bus(
        build_ctx([], {}, set())), list)


def test_validate_can_bus_empty_ctx():
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_can_bus
    assert isinstance(validate_can_bus(
        build_ctx([], {}, set())), list)


def test_validate_usb_bus_empty_ctx():
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_usb_bus
    assert isinstance(validate_usb_bus(
        build_ctx([], {}, set())), list)


def test_validate_can_bus_missing_termination():
    """CAN transceiver with no 120R termination between CANH and CANL.

    Smoke test — validator looks for MCP2551/TJA1050/SN65HVD-class transceivers
    by lib_id or MPN and expects terminators at bus ends. This test only
    confirms no crash on a minimal CAN setup; actual termination detection
    is corpus-validated.
    """
    if _skip_if_no_kh():
        return
    from validation_detectors import validate_can_bus

    ctx = build_ctx(
        components=[
            ic("U1", "MCP2551", [("1", "TXD"), ("2", "VSS"), ("3", "VDD"),
                                  ("6", "CANL"), ("7", "CANH")],
               lib_id="Interface_CAN:MCP2551", mpn="MCP2551"),
        ],
        nets={
            "+5V":  [("U1", "3")],
            "GND":  [("U1", "2")],
            "TXD":  [("U1", "1")],
            "CANH": [("U1", "7")],
            "CANL": [("U1", "6")],
        },
        known_power_rails={"+5V", "GND"},
    )
    findings = validate_can_bus(ctx)
    assert isinstance(findings, list)


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
