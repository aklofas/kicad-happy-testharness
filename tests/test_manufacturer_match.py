"""Unit tests for validate/datasheet_db/manufacturer.py."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate.datasheet_db.manufacturer import guess_manufacturer, guess_manufacturers_for_record


def test_ti_prefixes():
    assert guess_manufacturer("TPS54302") == "Texas Instruments"
    assert guess_manufacturer("LM7805") == "Texas Instruments"
    assert guess_manufacturer("OPA1612") == "Texas Instruments"
    assert guess_manufacturer("BQ24195") == "Texas Instruments"


def test_stm_prefixes():
    assert guess_manufacturer("STM32F405") == "STMicroelectronics"
    assert guess_manufacturer("L7805CV") == "STMicroelectronics"


def test_adi_prefixes():
    assert guess_manufacturer("ADP1706") == "Analog Devices"
    assert guess_manufacturer("LTC3601") == "Analog Devices"
    assert guess_manufacturer("MAX17043") == "Analog Devices"


def test_microchip_prefixes():
    assert guess_manufacturer("ATMEGA328P") == "Microchip"
    assert guess_manufacturer("MCP1700") == "Microchip"
    assert guess_manufacturer("PIC16F877") == "Microchip"


def test_espressif():
    assert guess_manufacturer("ESP32-S3") == "Espressif"


def test_nordic():
    assert guess_manufacturer("NRF52840") == "Nordic Semiconductor"


def test_passive_no_match():
    assert guess_manufacturer("100nF") is None
    assert guess_manufacturer("10k") is None
    assert guess_manufacturer("4.7uH") is None
    assert guess_manufacturer("") is None
    assert guess_manufacturer(None) is None


def test_case_insensitive():
    assert guess_manufacturer("tps54302") == "Texas Instruments"
    assert guess_manufacturer("stm32f405") == "STMicroelectronics"


def test_guess_for_record():
    record = {"mpns": [{"mpn": "TPS54302", "primary": True}, {"mpn": "LM7805"}]}
    result = guess_manufacturers_for_record(record)
    assert result == ["Texas Instruments"]


def test_guess_for_record_multiple():
    record = {"mpns": [{"mpn": "TPS54302", "primary": True}, {"mpn": "ADP1706"}]}
    result = guess_manufacturers_for_record(record)
    assert "Texas Instruments" in result
    assert "Analog Devices" in result


def test_guess_for_record_empty():
    assert guess_manufacturers_for_record({"mpns": []}) == []
    assert guess_manufacturers_for_record({}) == []


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
