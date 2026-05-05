"""Contract tests for mcu.schema.json (Phase 3b Stage 4)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
SCHEMA_PATH = SCHEMA_DIR / "mcu.schema.json"


def _registry() -> Registry:
    registry = Registry()
    for p in SCHEMA_DIR.glob("*.schema.json"):
        s = json.loads(p.read_text())
        if s.get("$id"):
            registry = registry.with_resource(s["$id"], Resource.from_contents(s))
    return registry


def _validator():
    schema = json.loads(SCHEMA_PATH.read_text())
    return Draft202012Validator(schema, registry=_registry())


def test_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(json.loads(SCHEMA_PATH.read_text()))


def test_schema_has_required_metadata():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["$id"].endswith("/mcu.schema.json")
    assert schema["title"] == "MCUExtension"
    assert schema["x-schema-version"] == "1.0"
    assert schema["additionalProperties"] is False
    # Tier 2 deferral must be documented in the description
    desc = schema["description"].lower()
    assert "tier 2" in desc or "v1.5" in desc, \
        "description must mention Tier 2 deferral or v1.5"


def test_minimal_validates():
    """Only core_family is required."""
    minimal = {"core_family": "cortex_m3"}
    assert list(_validator().iter_errors(minimal)) == []


def test_debug_interface_enum_rejects_unknown():
    bad = {"core_family": "cortex_m3", "debug_interface": "openocd"}
    assert list(_validator().iter_errors(bad))


def test_full_atmega328p_au_validates():
    """8-bit AVR, TQFP-32; nvic_priorities=null, dac=null, eeprom_size=1024."""
    ev_hi = {"page": 1, "section": "Features", "confidence": "high", "method": "prose"}
    ev_pkg = {"page": 300, "section": "Package Information", "confidence": "high", "method": "table"}
    full = {
        "core_family": "avr_8bit",
        "core_speed_max": 20000000,
        "flash_size": 32768,
        "ram_size": 2048,
        "eeprom_size": 1024,
        "pin_count": 32,
        "gpio_count": 23,
        "nvic_priorities": None,
        "vdd_range": [
            {"min": 1.8, "typ": None, "max": 5.5, "unit": "V",
             "condition": "VCC; full operating range from Absolute Maximum Ratings",
             "notes": "1.8V minimum for reduced speed; 4.5–5.5V for 20MHz operation.",
             "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "high", "method": "table"}}
        ],
        "vddio_range": None,
        "vdda_range": [
            {"min": 1.8, "typ": None, "max": 5.5, "unit": "V",
             "condition": "AVCC analog supply",
             "notes": None,
             "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "high", "method": "table"}}
        ],
        "peripheral_counts": {
            "uart": 1,
            "spi": 1,
            "i2c": 1,
            "can": 0,
            "usb": 0,
            "ethernet": 0,
            "dac": 0,
            "timer_general": 3,
            "timer_advanced": 0
        },
        "adc": {
            "bit_depth": 10,
            "channel_count": 8,
            "sample_rate_max_hz": 76900.0
        },
        "dac": None,
        "boot_pins": [],
        "debug_interface": "debugwire",
        "reset_pin": "29",
        "temperature_grades": ["industrial: -40 to +85"],
        "thermal_resistance": {
            "rtheta_ja": [
                {"min": None, "typ": 50, "max": None, "unit": "°C/W",
                 "condition": "TQFP-32, free air",
                 "notes": None,
                 "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "medium", "method": "prose"}}
            ],
            "rtheta_jc": None,
            "rtheta_jl": None
        },
        "package": {
            "code": "TQFP-32",
            "pin_count": 32,
            "pitch_mm": 0.8,
            "body_mm": {"length": 7.0, "width": 7.0, "height": 1.0},
            "thermal_pad": False,
            "evidence": ev_pkg
        }
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_full_stm32f103c8t6_validates():
    """Cortex-M3, LQFP-48; nvic_priorities=16, dac=null, eeprom_size=0."""
    ev_hi = {"page": 3, "section": "Electrical Characteristics", "confidence": "high", "method": "table"}
    ev_pkg = {"page": 80, "section": "Package Mechanical Data", "confidence": "high", "method": "table"}
    full = {
        "core_family": "cortex_m3",
        "core_speed_max": 72000000,
        "flash_size": 65536,
        "ram_size": 20480,
        "eeprom_size": 0,
        "pin_count": 48,
        "gpio_count": 37,
        "nvic_priorities": 16,
        "vdd_range": [
            {"min": 2.0, "typ": None, "max": 3.6, "unit": "V",
             "condition": "VDD operating range",
             "notes": None,
             "evidence": ev_hi}
        ],
        "vddio_range": None,
        "vdda_range": [
            {"min": 2.0, "typ": None, "max": 3.6, "unit": "V",
             "condition": "VDDA analog supply",
             "notes": None,
             "evidence": ev_hi}
        ],
        "peripheral_counts": {
            "uart": 3,
            "spi": 2,
            "i2c": 2,
            "can": 1,
            "usb": 1,
            "ethernet": 0,
            "dac": 0,
            "timer_general": 4,
            "timer_advanced": 1
        },
        "adc": {
            "bit_depth": 12,
            "channel_count": 10,
            "sample_rate_max_hz": 1000000.0
        },
        "dac": None,
        "boot_pins": [
            {"pin_number": "44", "function": "BOOT0"}
        ],
        "debug_interface": "swd_jtag",
        "reset_pin": "7",
        "nvic_priorities": 16,
        "temperature_grades": ["industrial: -40 to +85"],
        "thermal_resistance": {
            "rtheta_ja": [
                {"min": None, "typ": 60, "max": None, "unit": "°C/W",
                 "condition": "LQFP-48, free air",
                 "notes": None,
                 "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "medium", "method": "prose"}}
            ],
            "rtheta_jc": None,
            "rtheta_jl": None
        },
        "package": {
            "code": "LQFP-48",
            "pin_count": 48,
            "pitch_mm": 0.5,
            "body_mm": {"length": 7.0, "width": 7.0, "height": 1.4},
            "thermal_pad": False,
            "evidence": ev_pkg
        }
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_additional_properties_rejected():
    bad = {"core_family": "cortex_m3", "made_up_field": 42}
    assert list(_validator().iter_errors(bad))
