"""Contract tests for transistor.schema.json (Phase 3b)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
SCHEMA_PATH = SCHEMA_DIR / "transistor.schema.json"


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
    assert schema["$id"].endswith("/transistor.schema.json")
    assert schema["title"] == "TransistorExtension"
    assert schema["x-schema-version"] == "1.0"
    assert schema["additionalProperties"] is False


def test_minimal_validates():
    minimal = {"transistor_type": "mosfet_n"}
    assert list(_validator().iter_errors(minimal)) == []


def test_transistor_type_enum_rejects_unknown():
    bad = {"transistor_type": "definitely-not-a-type"}
    assert list(_validator().iter_errors(bad))


def test_full_2n3904_validates():
    """NPN BJT path — BJT fields populated, FET fields null."""
    full = {
        "transistor_type": "bjt_npn",
        "vceo_max": [{"min": 40, "typ": None, "max": None, "unit": "V",
                      "condition": "IC=1.0mAdc, IB=0", "notes": None,
                      "evidence": {"page": 1, "section": "Electrical Characteristics — OFF",
                                   "confidence": "high", "method": "table"}}],
        "vcbo_max": [{"min": 60, "typ": None, "max": None, "unit": "V",
                      "condition": "IC=10µAdc, IE=0", "notes": None,
                      "evidence": {"page": 1, "section": "Electrical Characteristics — OFF",
                                   "confidence": "high", "method": "table"}}],
        "vebo_max": [{"min": 6.0, "typ": None, "max": None, "unit": "V",
                      "condition": "IE=10µAdc, IC=0", "notes": None,
                      "evidence": {"page": 1, "section": "Electrical Characteristics — OFF",
                                   "confidence": "high", "method": "table"}}],
        "ic_max": [{"min": None, "typ": None, "max": 0.200, "unit": "A",
                    "condition": "Continuous collector current", "notes": None,
                    "evidence": {"page": 1, "section": "Features",
                                 "confidence": "medium", "method": "prose"}}],
        "hfe": [
            {"min": 40, "typ": None, "max": None, "unit": None,
             "condition": "IC=0.1mAdc, VCE=1.0V", "notes": None,
             "evidence": {"page": 1, "section": "Electrical Characteristics — ON",
                          "confidence": "high", "method": "table"}},
            {"min": 70, "typ": None, "max": None, "unit": None,
             "condition": "IC=1.0mAdc, VCE=1.0V", "notes": None,
             "evidence": {"page": 1, "section": "Electrical Characteristics — ON",
                          "confidence": "high", "method": "table"}},
            {"min": 100, "typ": None, "max": 300, "unit": None,
             "condition": "IC=10mAdc, VCE=1.0V", "notes": None,
             "evidence": {"page": 1, "section": "Electrical Characteristics — ON",
                          "confidence": "high", "method": "table"}},
        ],
        "vce_sat": [{"min": None, "typ": None, "max": 0.2, "unit": "V",
                     "condition": "IC=10mAdc, IB=1.0mAdc", "notes": None,
                     "evidence": {"page": 1, "section": "Electrical Characteristics — ON",
                                  "confidence": "high", "method": "table"}}],
        "vbe_sat": [{"min": 0.65, "typ": None, "max": 0.85, "unit": "V",
                     "condition": "IC=10mAdc, IB=1.0mAdc", "notes": None,
                     "evidence": {"page": 1, "section": "Electrical Characteristics — ON",
                                  "confidence": "high", "method": "table"}}],
        "ft": [{"min": 250e6, "typ": None, "max": None, "unit": "Hz",
                "condition": "IC=10mAdc, VCE=20V, f=100MHz", "notes": None,
                "evidence": {"page": 1, "section": "Small-Signal Characteristics",
                             "confidence": "high", "method": "table"}}],
        "power_dissipation": [{"min": None, "typ": None, "max": 0.625, "unit": "W",
                               "condition": "Capable of 625mW (per Features)", "notes": None,
                               "evidence": {"page": 1, "section": "Features",
                                            "confidence": "medium", "method": "prose"}}],
        "tj_max": [{"min": -55, "typ": None, "max": 150, "unit": "°C",
                    "condition": "Operating Temperature", "notes": None,
                    "evidence": {"page": 1, "section": "Features",
                                 "confidence": "high", "method": "prose"}}],
        "thermal_resistance": {
            "rtheta_ja": [{"min": None, "typ": None, "max": 200, "unit": "°C/W",
                           "condition": None, "notes": None,
                           "evidence": {"page": 1, "section": "Thermal Resistance",
                                        "confidence": "high", "method": "table"}}],
            "rtheta_jc": None,
            "rtheta_jl": None,
        },
        "package": {
            "code": "TO-92", "pin_count": 3, "pitch_mm": 1.27,
            "body_mm": {"length": 4.575, "width": 4.575, "height": 5.05},
            "thermal_pad": False,
            "evidence": {"page": 1, "section": "TO-92 DIMENSIONS",
                         "confidence": "high", "method": "table"}
        },
        "pin_assignment": {
            "base_pin": "2", "collector_pin": "3", "emitter_pin": "1",
            "gate_pin": None, "drain_pin": None, "source_pin": None,
        },
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_full_irlml6344_validates():
    """N-MOSFET path — FET fields populated, BJT fields null."""
    full = {
        "transistor_type": "mosfet_n",
        "vds_max": [{"min": None, "typ": None, "max": 30, "unit": "V",
                     "condition": "Drain-Source Voltage absolute max", "notes": None,
                     "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                                  "confidence": "high", "method": "table"}}],
        "vgs_max": [{"min": -12, "typ": None, "max": 12, "unit": "V",
                     "condition": "Gate-Source Voltage", "notes": None,
                     "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                                  "confidence": "high", "method": "table"}}],
        "id_max": [
            {"min": None, "typ": None, "max": 5.0, "unit": "A",
             "condition": "Continuous, TA=25°C, VGS=10V", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 4.0, "unit": "A",
             "condition": "Continuous, TA=70°C, VGS=10V", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
        ],
        "rds_on": [
            {"min": None, "typ": 0.022, "max": 0.029, "unit": "Ω",
             "condition": "VGS=4.5V, ID=5.0A", "notes": None,
             "evidence": {"page": 2, "section": "Electric Characteristics",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": 0.027, "max": 0.037, "unit": "Ω",
             "condition": "VGS=2.5V, ID=4.0A", "notes": None,
             "evidence": {"page": 2, "section": "Electric Characteristics",
                          "confidence": "high", "method": "table"}},
        ],
        "vgs_th": [{"min": 0.5, "typ": 0.8, "max": 1.1, "unit": "V",
                    "condition": "VDS=VGS, ID=10µA", "notes": None,
                    "evidence": {"page": 2, "section": "Electric Characteristics",
                                 "confidence": "high", "method": "table"}}],
        "qg": [{"min": None, "typ": 6.8e-9, "max": None, "unit": "C",
                "condition": "ID=5.0A, VDS=15V, VGS=4.5V", "notes": None,
                "evidence": {"page": 2, "section": "Electric Characteristics",
                             "confidence": "high", "method": "table"}}],
        "qgd": [{"min": None, "typ": 2.4e-9, "max": None, "unit": "C",
                 "condition": "ID=5.0A, VDS=15V, VGS=4.5V", "notes": None,
                 "evidence": {"page": 2, "section": "Electric Characteristics",
                              "confidence": "high", "method": "table"}}],
        "ciss": [{"min": None, "typ": 6.5e-10, "max": None, "unit": "F",
                  "condition": "VGS=0V, VDS=25V, f=1MHz", "notes": None,
                  "evidence": {"page": 2, "section": "Electric Characteristics",
                               "confidence": "high", "method": "table"}}],
        "coss": [{"min": None, "typ": 6.5e-11, "max": None, "unit": "F",
                  "condition": "VGS=0V, VDS=25V, f=1MHz", "notes": None,
                  "evidence": {"page": 2, "section": "Electric Characteristics",
                               "confidence": "high", "method": "table"}}],
        "crss": [{"min": None, "typ": 4.6e-11, "max": None, "unit": "F",
                  "condition": "VGS=0V, VDS=25V, f=1MHz", "notes": None,
                  "evidence": {"page": 2, "section": "Electric Characteristics",
                               "confidence": "high", "method": "table"}}],
        "body_diode_vf": [{"min": None, "typ": None, "max": 1.2, "unit": "V",
                           "condition": "TJ=25°C, IS=5.0A, VGS=0V", "notes": None,
                           "evidence": {"page": 2, "section": "Source-Drain Ratings",
                                        "confidence": "high", "method": "table"}}],
        "power_dissipation": [
            {"min": None, "typ": None, "max": 1.3, "unit": "W",
             "condition": "TA=25°C", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
            {"min": None, "typ": None, "max": 0.8, "unit": "W",
             "condition": "TA=70°C", "notes": None,
             "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                          "confidence": "high", "method": "table"}},
        ],
        "tj_max": [{"min": -55, "typ": None, "max": 150, "unit": "°C",
                    "condition": "Junction and Storage Temperature Range", "notes": None,
                    "evidence": {"page": 1, "section": "Absolute Maximum Ratings",
                                 "confidence": "high", "method": "table"}}],
        "thermal_resistance": {
            "rtheta_ja": [{"min": None, "typ": None, "max": 100, "unit": "°C/W",
                           "condition": "Surface mounted on 1-in² Cu board", "notes": None,
                           "evidence": {"page": 1, "section": "Thermal Resistance",
                                        "confidence": "high", "method": "table"}}],
            "rtheta_jc": None,
            "rtheta_jl": None,
        },
        "package": {
            "code": "SOT-23", "pin_count": 3, "pitch_mm": 0.95,
            "body_mm": {"length": 2.92, "width": 1.30, "height": 1.005},
            "thermal_pad": False,
            "evidence": {"page": 8, "section": "Micro3 (SOT-23) Package Outline",
                         "confidence": "high", "method": "table"}
        },
        "pin_assignment": {
            "gate_pin": "1", "drain_pin": "3", "source_pin": "2",
            "base_pin": None, "collector_pin": None, "emitter_pin": None,
        },
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_additional_properties_rejected():
    bad = {"transistor_type": "bjt_npn", "made_up_field": 42}
    assert list(_validator().iter_errors(bad))
