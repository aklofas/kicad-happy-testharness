"""Contract tests for crystal.schema.json (Phase 3b Stage 5 — final category)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
SCHEMA_PATH = SCHEMA_DIR / "crystal.schema.json"


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
    assert schema["$id"].endswith("/crystal.schema.json")
    assert schema["title"] == "CrystalExtension"
    assert schema["x-schema-version"] == "1.0"
    assert schema["additionalProperties"] is False


def test_minimal_validates():
    """Only crystal_type is required."""
    minimal = {"crystal_type": "at_cut"}
    assert list(_validator().iter_errors(minimal)) == []


def test_crystal_type_enum_rejects_unknown():
    bad = {"crystal_type": "sc_cut"}
    assert list(_validator().iter_errors(bad))


def test_full_abm8g_validates():
    """ABM8G-106-12.000MHZ-T: Abracon 12 MHz AT-cut fundamental SMD crystal.

    Values from harness sanity vector (abm8g-106-12.000mhz-t.json).
    Note: crystal_type not on this PDF explicitly; using at_cut as best-fit.
    Aging stored as ppm (symmetric ±3 ppm/year envelope) per sanity vector.
    """
    ev = {"page": 1, "section": "Key Electrical Specifications",
          "confidence": "high", "method": "table"}
    ev_pkg = {"page": 1, "section": "Package Dimensions",
              "confidence": "high", "method": "table"}
    full = {
        "crystal_type": "at_cut",
        "frequency": [
            {"min": None, "typ": 12000000.0, "max": None, "unit": "Hz",
             "condition": "Frequency Range, fundamental-mode operation",
             "notes": "Reported as 12.000 MHz; converted from MHz to Hz",
             "evidence": ev}
        ],
        "frequency_tolerance": [
            {"min": -20.0, "typ": None, "max": 20.0, "unit": "ppm",
             "condition": "Frequency Tolerance @ +25\u00b0C",
             "notes": "Reported as \u00b120 ppm",
             "evidence": ev}
        ],
        "frequency_stability": [
            {"min": -30.0, "typ": None, "max": 30.0, "unit": "ppm",
             "condition": "Frequency Stability over -40\u00b0C to +85\u00b0C, ref +25\u00b0C",
             "notes": "Reported as \u00b130 ppm",
             "evidence": ev}
        ],
        "aging": [
            {"min": -3.0, "typ": None, "max": 3.0, "unit": "ppm",
             "condition": "Aging @ 25\u00b0C \u00b13\u00b0C, first year",
             "notes": "\u00b13 ppm/year first-year envelope",
             "evidence": ev}
        ],
        "load_capacitance": [
            {"min": None, "typ": 1e-11, "max": None, "unit": "F",
             "condition": "Load capacitance (CL), typical",
             "notes": "Reported as 10 pF; converted from pF to F",
             "evidence": ev}
        ],
        "motional_capacitance": None,
        "motional_inductance": None,
        "esr_max": [
            {"min": None, "typ": None, "max": 120.0, "unit": "\u03a9",
             "condition": "Equivalent series resistance (R1), maximum",
             "notes": None,
             "evidence": ev}
        ],
        "drive_level_max": [
            {"min": None, "typ": None, "max": 1e-4, "unit": "W",
             "condition": "Drive Level, maximum",
             "notes": "Reported as 100 \u00b5W; converted to W",
             "evidence": ev}
        ],
        "operating_temp_range": [
            {"min": -40.0, "typ": None, "max": 85.0, "unit": "\u00b0C",
             "condition": "Operating Temperature Range",
             "notes": None,
             "evidence": ev}
        ],
        "mode": "fundamental",
        "package": {
            "code": "SMD-3225",
            "body_mm": {"length": 3.2, "width": 2.5, "height": 1.0},
            "evidence": ev_pkg
        }
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_additional_properties_rejected():
    bad = {"crystal_type": "at_cut", "made_up_field": 42}
    assert list(_validator().iter_errors(bad))
