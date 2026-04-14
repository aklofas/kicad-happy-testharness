"""Unit tests for regression/refextract.py — component reference extraction."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from refextract import (
    extract_refs, extract_refs_ordered, get_ref_from_item,
    _is_valid_ref, _ref_prefix, REF_FIELD_MAP, PCB_REF_FIELD_MAP,
)


# === _ref_prefix ===

def test_ref_prefix_simple():
    assert _ref_prefix("R1") == "R"
    assert _ref_prefix("C23") == "C"
    assert _ref_prefix("U4") == "U"

def test_ref_prefix_multi_letter():
    assert _ref_prefix("SW1") == "SW"
    assert _ref_prefix("FB3") == "FB"
    assert _ref_prefix("TP12") == "TP"

def test_ref_prefix_empty():
    assert _ref_prefix("") == ""
    assert _ref_prefix("123") == ""


# === _is_valid_ref ===

def test_valid_ref_basic():
    assert _is_valid_ref("R1")
    assert _is_valid_ref("C23")
    assert _is_valid_ref("U4")
    assert _is_valid_ref("Q7")
    assert _is_valid_ref("D10")

def test_valid_ref_multi_prefix():
    assert _is_valid_ref("SW1")
    assert _is_valid_ref("FB3")
    assert _is_valid_ref("TP12")
    assert _is_valid_ref("RN1")

def test_invalid_ref_false_positives():
    assert not _is_valid_ref("I2C")
    assert not _is_valid_ref("SPI")
    assert not _is_valid_ref("USB")
    assert not _is_valid_ref("RS485")
    assert not _is_valid_ref("RS232")
    assert not _is_valid_ref("RP2040")

def test_invalid_ref_sheet_voltage_net():
    assert not _is_valid_ref("S1")
    assert not _is_valid_ref("V1")
    assert not _is_valid_ref("N1")

def test_invalid_ref_unknown_prefix():
    assert not _is_valid_ref("ZZ1")
    assert not _is_valid_ref("WW5")


# === extract_refs ===

def test_extract_simple():
    assert extract_refs("R1 and C2") == ["C2", "R1"]

def test_extract_multiple():
    refs = extract_refs("U4 drives Q7 through R10")
    assert refs == ["Q7", "R10", "U4"]

def test_extract_slash_separated():
    refs = extract_refs("R135/R134 voltage divider")
    assert "R134" in refs
    assert "R135" in refs

def test_extract_range():
    refs = extract_refs("Q13-Q16 are MOSFETs")
    assert refs == ["Q13", "Q14", "Q15", "Q16"]

def test_extract_filters_false_positives():
    refs = extract_refs("I2C bus with U4 and R1 pullups")
    assert "I2C" not in refs
    assert "U4" in refs
    assert "R1" in refs

def test_extract_empty():
    assert extract_refs("") == []
    assert extract_refs(None) == []

def test_extract_no_refs():
    assert extract_refs("no component references here") == []

def test_extract_composite_value():
    refs = extract_refs("R163 442k feedback resistor")
    assert "R163" in refs

def test_extract_sorted():
    refs = extract_refs("C2 R1 U4")
    assert refs == ["C2", "R1", "U4"]

def test_extract_deduplication():
    refs = extract_refs("R1 connects to R1")
    assert refs == ["R1"]


# === extract_refs_ordered ===

def test_ordered_preserves_appearance():
    refs = extract_refs_ordered("U4 drives R1 through C2")
    assert refs[0] == "U4"
    assert refs[1] == "R1"
    assert refs[2] == "C2"

def test_ordered_empty():
    assert extract_refs_ordered("") == []
    assert extract_refs_ordered(None) == []

def test_ordered_deduplication():
    refs = extract_refs_ordered("R1 then R1 again")
    assert refs == ["R1"]


# === get_ref_from_item ===

def test_get_ref_simple():
    assert get_ref_from_item("detect_protection_devices", {"ref": "D1"}) == "D1"

def test_get_ref_nested():
    item = {"r_top": {"ref": "R5", "value": "10k"}}
    assert get_ref_from_item("detect_voltage_dividers", item) == "R5"

def test_get_ref_nested_rc():
    item = {"resistor": {"ref": "R9", "value": "10k"}, "capacitor": {"ref": "C1"}}
    assert get_ref_from_item("detect_rc_filters", item) == "R9"

def test_get_ref_nested_lc():
    item = {"inductor": {"ref": "L1"}, "capacitor": {"ref": "C5"}}
    assert get_ref_from_item("detect_lc_filters", item) == "L1"

def test_get_ref_nested_current_sense():
    item = {"shunt": {"ref": "R3"}}
    assert get_ref_from_item("detect_current_sense", item) == "R3"

def test_get_ref_no_field_map():
    # Detectors with None field map should return None
    assert get_ref_from_item("detect_rf_matching", {"antenna": "ANT1"}) is None
    assert get_ref_from_item("detect_design_observations", {"category": "test"}) is None
    assert get_ref_from_item("detect_key_matrices", {"rows": 4}) is None

def test_get_ref_missing_field():
    assert get_ref_from_item("detect_protection_devices", {"type": "TVS"}) is None

def test_get_ref_composite_value():
    # "R163 442k" -> extract "R163"
    item = {"ref": "R163 442k"}
    assert get_ref_from_item("detect_power_regulators", item) == "R163"

def test_get_ref_question_mark():
    item = {"ref": "?"}
    assert get_ref_from_item("detect_protection_devices", item) is None

def test_get_ref_unknown_detector():
    assert get_ref_from_item("nonexistent_detector", {"ref": "R1"}) is None


# === REF_FIELD_MAP coverage ===

def test_ref_field_map_completeness():
    """Verify all expected detector types are in REF_FIELD_MAP."""
    expected = {
        "detect_opamp_circuits", "detect_voltage_dividers", "detect_protection_devices",
        "detect_transistor_circuits", "detect_power_regulators", "detect_crystal_circuits",
        "detect_rc_filters", "detect_lc_filters", "detect_led_drivers", "detect_current_sense",
        "detect_rf_matching", "detect_design_observations", "detect_key_matrices",
        "validate_feedback_stability", "detect_decoupling",
        "detect_buzzer_speakers", "detect_bridge_circuits", "detect_isolation_barriers",
        "detect_ethernet_interfaces", "detect_hdmi_dvi_interfaces", "detect_memory_interfaces",
        "detect_rf_chains", "detect_bms_systems", "detect_addressable_leds",
    }
    assert set(REF_FIELD_MAP.keys()) == expected

def test_pcb_ref_field_map():
    """Verify PCB field map has expected entries."""
    assert "decoupling_placement" in PCB_REF_FIELD_MAP
    assert "analyze_thermal_pad_vias" in PCB_REF_FIELD_MAP
    assert "analyze_tombstoning_risk" in PCB_REF_FIELD_MAP


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
