"""Unit tests for datasheet_score.py v1.4 rubric (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import importlib.util

spec = importlib.util.spec_from_file_location(
    "datasheet_score_under_test",
    MAIN_REPO_ROOT / "skills/datasheets/scripts/datasheet_score.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
score_v14_extraction = mod.score_v14_extraction


def _full_extraction() -> dict:
    """A complete-ish LM2596-ADJ-shape extraction."""
    pin = lambda num, name, ty, pd: {
        "numbers": [num], "name": name, "type": ty, "power_domain": pd,
        "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}
    }
    sv = lambda **kw: [{"min": kw.get("min"), "typ": kw.get("typ"), "max": kw.get("max"),
                        "unit": kw.get("unit"), "condition": None, "notes": None,
                        "evidence": {"page": 5, "section": "EC", "confidence": "high", "method": "table"}}]
    return {
        "schema_version": {"base": "1.0", "categories": {"regulator": "0.3"}},
        "categories": ["regulator"],
        "base": {
            "package": {"code": "TO-263-5", "pin_count": 5, "thermal_pad": True,
                        "evidence": {"page": 1, "section": "F", "confidence": "high", "method": "prose"}},
            "thermal": {"theta_ja": sv(typ=50, unit="°C/W")},
            "absolute_max": {
                "VIN_max": sv(max=45, unit="V"),
                "TJ_max":  sv(max=150, unit="°C"),
            },
            "recommended_operating": {
                "VIN": sv(min=4.5, max=40, unit="V"),
                "TA":  sv(min=-40, max=125, unit="°C"),
            },
            "esd": {"HBM": sv(typ=2000, unit="V")},
            "pinout": [
                pin("1", "VIN", "power_in", "VIN"),
                pin("2", "OUT", "output", None),
                pin("3", "GND", "power_in", None),
                pin("4", "FB",  "input", None),
                pin("5", "EN",  "input", None),
            ],
        },
        "regulator": {
            "topology": "buck",
            "vin_range": sv(min=4.5, max=40, unit="V"),
            "vout_range": sv(min=1.23, max=37, unit="V"),
            "iout_max": sv(max=3, unit="A"),
            "reference_voltage": sv(min=1.18, typ=1.23, max=1.28, unit="V"),
            "switching_freq": sv(typ=150000, unit="Hz"),
            "feedback_pin": "4",
            "enable_pin": "5",
            "cin_min": sv(min=4.7e-4, unit="F"),
            "cout_min": sv(min=2.2e-4, unit="F"),
        }
    }


def test_full_extraction_scores_above_60():
    s = score_v14_extraction(_full_extraction())
    assert s["score"] >= 60
    assert "pinout_completeness" in s["dimensions"]
    assert "base_completeness" in s["dimensions"]
    assert "category_extension_completeness" in s["dimensions"]


def test_empty_extraction_scores_low():
    s = score_v14_extraction({"base": {}, "categories": []})
    assert s["score"] < 60


def test_pinout_dimension_scales_with_field_population():
    e = _full_extraction()
    # Strip name/power_domain/evidence from all pins
    for p in e["base"]["pinout"]:
        p["name"] = None
        p["power_domain"] = None
        p["evidence"] = {}
    s = score_v14_extraction(e)
    full = score_v14_extraction(_full_extraction())
    assert s["dimensions"]["pinout_completeness"] < full["dimensions"]["pinout_completeness"]


def test_category_extension_dimension_zero_when_failed_sentinel():
    e = _full_extraction()
    e["regulator"] = {"_extraction_failed": True, "reason": "x"}
    s = score_v14_extraction(e)
    assert s["dimensions"]["category_extension_completeness"] == 0


def test_score_in_zero_to_one_hundred():
    s = score_v14_extraction(_full_extraction())
    assert 0 <= s["score"] <= 100


def test_score_does_not_crash_on_pinout_sentinel():
    """Post-retry pinout failure → base.pinout = sentinel dict, not list."""
    e = _full_extraction()
    e["base"]["pinout"] = {"_extraction_failed": True, "reason": "pinout extractor failed twice"}
    s = score_v14_extraction(e)
    assert s["dimensions"]["pinout_completeness"] == 0.0
    assert 0 <= s["score"] <= 100


def test_score_does_not_crash_on_base_sentinel():
    """Post-retry base failure → entire base block is the sentinel."""
    e = _full_extraction()
    e["base"] = {"_extraction_failed": True, "reason": "base extractor failed twice"}
    s = score_v14_extraction(e)
    assert s["dimensions"]["base_completeness"] == 0.0
    assert s["dimensions"]["pinout_completeness"] == 0.0  # base.pinout doesn't exist
    assert 0 <= s["score"] <= 100


def test_score_does_not_crash_on_category_sentinel():
    """Post-retry category failure (already covered by test_category_extension_dimension_zero_when_failed_sentinel,
    but verifying overall score does not raise)."""
    e = _full_extraction()
    e["regulator"] = {"_extraction_failed": True, "reason": "regulator extractor failed twice"}
    s = score_v14_extraction(e)
    assert s["dimensions"]["category_extension_completeness"] == 0.0
    assert 0 <= s["score"] <= 100
