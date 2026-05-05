"""Contract tests for diode.schema.json (Phase 3b)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
SCHEMA_PATH = SCHEMA_DIR / "diode.schema.json"


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
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)


def test_schema_has_required_metadata():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["$id"].endswith("/diode.schema.json")
    assert schema["title"] == "DiodeExtension"
    assert schema["x-schema-version"] == "1.0"
    assert schema["additionalProperties"] is False


def _minimal_valid_diode() -> dict:
    return {
        "diode_type": "schottky",
    }


def test_minimal_diode_validates():
    errors = list(_validator().iter_errors(_minimal_valid_diode()))
    assert errors == []


def test_diode_type_enum_rejects_unknown():
    bad = {"diode_type": "definitely-not-a-real-type"}
    errors = list(_validator().iter_errors(bad))
    assert errors


def test_full_mbrs540t3g_validates():
    """Full extraction shape — the real Phase 3b extraction must validate."""
    full = {
        "diode_type": "schottky",
        "vf": [{"min": None, "typ": None, "max": 0.50, "unit": "V",
                "condition": "iF=5A, TC=25°C", "notes": None,
                "evidence": {"page": 2, "section": "Electrical Characteristics",
                             "confidence": "high", "method": "table"}}],
        "if_max": [
            {"min": None, "typ": None, "max": 5.0, "unit": "A",
             "condition": "Average rectified, TC=105°C", "notes": None,
             "evidence": {"page": 2, "section": "Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 10.0, "unit": "A",
             "condition": "Repetitive peak, square wave 20kHz, TC=80°C", "notes": None,
             "evidence": {"page": 2, "section": "Maximum Ratings",
                          "confidence": "high", "method": "table"}},
        ],
        "ifsm": [{"min": None, "typ": None, "max": 190, "unit": "A",
                  "condition": "Halfwave, single phase, 60Hz, surge", "notes": None,
                  "evidence": {"page": 2, "section": "Maximum Ratings",
                               "confidence": "high", "method": "table"}}],
        "vr_max": [{"min": None, "typ": None, "max": 40, "unit": "V",
                    "condition": "VRRM / VRWM / VR (DC blocking)", "notes": None,
                    "evidence": {"page": 2, "section": "Maximum Ratings",
                                 "confidence": "high", "method": "table"}}],
        "ir": [
            {"min": None, "typ": None, "max": 3e-4, "unit": "A",
             "condition": "Rated DC voltage, TC=25°C", "notes": None,
             "evidence": {"page": 2, "section": "Electrical Characteristics",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 1.5e-2, "unit": "A",
             "condition": "Rated DC voltage, TC=100°C", "notes": None,
             "evidence": {"page": 2, "section": "Electrical Characteristics",
                          "confidence": "high", "method": "table"}},
        ],
        "tj_max": [{"min": -65, "typ": None, "max": 150, "unit": "°C",
                    "condition": None, "notes": None,
                    "evidence": {"page": 2, "section": "Maximum Ratings",
                                 "confidence": "high", "method": "table"}}],
        "thermal_resistance": {
            "rtheta_ja": [{"min": None, "typ": 111, "max": None, "unit": "K/W",
                           "condition": "Min pad", "notes": None,
                           "evidence": {"page": 2, "section": "Thermal Characteristics",
                                        "confidence": "high", "method": "table"}}],
            "rtheta_jc": None,
            "rtheta_jl": [{"min": None, "typ": 12, "max": None, "unit": "K/W",
                           "condition": "Min pad", "notes": None,
                           "evidence": {"page": 2, "section": "Thermal Characteristics",
                                        "confidence": "high", "method": "table"}}],
        },
        "package": {
            "code": "SMC", "pin_count": 2, "pitch_mm": None,
            "body_mm": {"length": 5.9, "width": 6.875, "height": 2.28},
            "thermal_pad": False,
            "evidence": {"page": 5, "section": "Package Dimensions",
                         "confidence": "high", "method": "table"}
        },
        "marking_code": "B540",
        "polarity_marking_convention": "polarity band on plastic body indicates cathode",
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_full_1n4148_validates():
    """Through-hole signal diode — exercises trr, breakdown_voltage, single-Vr-variant path."""
    full = {
        "diode_type": "switching",
        "vf": [{"min": None, "typ": None, "max": 1.0, "unit": "V",
                "condition": "IF=10mA", "notes": None,
                "evidence": {"page": 2, "section": "Electrical Characteristics",
                             "confidence": "high", "method": "table"}}],
        "if_max": [
            {"min": None, "typ": None, "max": 0.30, "unit": "A",
             "condition": "Continuous", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 0.15, "unit": "A",
             "condition": "Average, VR=0", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 0.50, "unit": "A",
             "condition": "Repetitive peak", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
        ],
        "ifsm": [{"min": None, "typ": None, "max": 2.0, "unit": "A",
                  "condition": "tp=1µs, peak surge", "notes": None,
                  "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                               "confidence": "high", "method": "table"}}],
        "vr_max": [
            {"min": None, "typ": None, "max": 100, "unit": "V",
             "condition": "VRRM (repetitive peak)", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 75, "unit": "V",
             "condition": "VR (continuous DC)", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
        ],
        "breakdown_voltage": [{"min": 100, "typ": None, "max": None, "unit": "V",
                               "condition": "IR=100µA, tp=0.3ms", "notes": None,
                               "evidence": {"page": 2, "section": "Electrical Characteristics",
                                            "confidence": "high", "method": "table"}}],
        "ir": [
            {"min": None, "typ": None, "max": 2.5e-8, "unit": "A",
             "condition": "VR=20V", "notes": None,
             "evidence": {"page": 2, "section": "Electrical Characteristics",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 5.0e-6, "unit": "A",
             "condition": "VR=75V", "notes": None,
             "evidence": {"page": 2, "section": "Electrical Characteristics",
                          "confidence": "high", "method": "table"}},
        ],
        "trr": [{"min": None, "typ": None, "max": 8e-9, "unit": "s",
                 "condition": "IF=IR=10mA, iR=1mA", "notes": None,
                 "evidence": {"page": 2, "section": "Electrical Characteristics",
                              "confidence": "high", "method": "table"}}],
        "cd": [{"min": None, "typ": None, "max": 4e-12, "unit": "F",
                "condition": "VR=0V, f=1MHz", "notes": None,
                "evidence": {"page": 2, "section": "Electrical Characteristics",
                             "confidence": "high", "method": "table"}}],
        "power_dissipation": [{"min": None, "typ": None, "max": 0.500, "unit": "W",
                               "condition": "l=4mm, TL≤25°C", "notes": None,
                               "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                                            "confidence": "high", "method": "table"}}],
        "tj_max": [{"min": None, "typ": None, "max": 175, "unit": "°C",
                    "condition": None, "notes": None,
                    "evidence": {"page": 1, "section": "Thermal Characteristics",
                                 "confidence": "high", "method": "table"}}],
        "thermal_resistance": {
            "rtheta_ja": [{"min": None, "typ": 350, "max": None, "unit": "K/W",
                           "condition": "l=4mm, TL=constant", "notes": None,
                           "evidence": {"page": 1, "section": "Thermal Characteristics",
                                        "confidence": "high", "method": "table"}}],
            "rtheta_jc": None,
            "rtheta_jl": None,
        },
        "package": {
            "code": "DO-35", "pin_count": 2, "pitch_mm": None,
            "body_mm": {"length": 3.4, "width": 1.75, "height": 1.75},
            "thermal_pad": False,
            "evidence": {"page": 3, "section": "Package Dimensions",
                         "confidence": "high", "method": "table"}
        },
        "marking_code": "V4148",
        "polarity_marking_convention": "cathode band",
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_additional_properties_rejected():
    bad = {"diode_type": "signal", "made_up_field": 42}
    errors = list(_validator().iter_errors(bad))
    assert errors
