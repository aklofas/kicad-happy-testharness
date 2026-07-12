"""Unit tests for datasheet_verify.py v1.4 extensions (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import pytest

import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "datasheet_verify_under_test",
    MAIN_REPO_ROOT / "skills/datasheets/scripts/datasheet_verify.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

verify_v14_extraction = mod.verify_v14_extraction
verify_required_externals = mod.verify_required_externals


def _ok_extraction() -> dict:
    return {
        "schema_version": {"base": "1.0", "categories": {"regulator": "0.3"}},
        "base": {
            "recommended_operating": {
                "VIN": [{"min": 4.5, "max": 40, "unit": "V",
                         "evidence": {"page": 5, "section": "ROC", "confidence": "high", "method": "table"}}]
            },
            "absolute_max": {
                "VIN_max": [{"max": 45, "unit": "V",
                             "evidence": {"page": 5, "section": "Abs Max", "confidence": "high", "method": "table"}}]
            },
            "pinout": [
                {"numbers": ["1"], "name": "VIN", "type": "power_in", "subtype": None,
                 "description": None, "power_domain": "VIN", "alt_functions": [],
                 "is_5v_tolerant": None, "absolute_max": None, "recommended": None,
                 "drive_strength": None, "notes": None,
                 "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}},
                {"numbers": ["4"], "name": "FB", "type": "input", "subtype": None,
                 "description": None, "power_domain": None, "alt_functions": [],
                 "is_5v_tolerant": None, "absolute_max": None, "recommended": None,
                 "drive_strength": None, "notes": None,
                 "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}},
                {"numbers": ["5"], "name": "EN", "type": "input", "subtype": None,
                 "description": None, "power_domain": None, "alt_functions": [],
                 "is_5v_tolerant": None, "absolute_max": None, "recommended": None,
                 "drive_strength": None, "notes": None,
                 "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}}
            ]
        },
        "categories": ["regulator"],
        "regulator": {
            "topology": "buck",
            "feedback_pin": "4",
            "enable_pin": "5",
            "power_good_pin": None
        }
    }


def test_clean_extraction_zero_findings():
    assert verify_v14_extraction(_ok_extraction()) == []


def test_unresolved_power_domain_flags_warning():
    e = _ok_extraction()
    e["base"]["pinout"][0]["power_domain"] = "VBUS"  # not in recommended_operating
    issues = verify_v14_extraction(e)
    assert any(i["path"] == "base.pinout[0].power_domain" and i["severity"] == "warning" for i in issues)


def test_recommended_max_above_absolute_max_flags_error():
    e = _ok_extraction()
    e["base"]["recommended_operating"]["VIN"][0]["max"] = 50  # > absolute 45
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and "VIN" in i["path"] for i in issues)


def test_min_above_max_within_specvalue_flags_error():
    e = _ok_extraction()
    e["base"]["recommended_operating"]["VIN"][0]["min"] = 50
    e["base"]["recommended_operating"]["VIN"][0]["max"] = 40
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and "min > max" in i["description"] for i in issues)


def test_unresolved_regulator_pin_reference_flags_error():
    e = _ok_extraction()
    e["regulator"]["feedback_pin"] = "99"  # not in pinout
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and i["path"] == "regulator.feedback_pin" for i in issues)


def test_categories_array_lists_role_but_payload_missing_flags_error():
    e = _ok_extraction()
    del e["regulator"]
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and "regulator" in i["description"] for i in issues)


def test_partial_merge_sentinel_flags_error():
    e = _ok_extraction()
    e["regulator"] = {"_extraction_failed": True, "reason": "subagent could not locate EC table"}
    issues = verify_v14_extraction(e)
    sentinel_issues = [i for i in issues if "sentinel" in i["description"].lower()]
    assert len(sentinel_issues) == 1
    assert sentinel_issues[0]["severity"] == "error"
    assert sentinel_issues[0]["path"] == "regulator"


def test_empty_list_category_payload_flags_error():
    e = _ok_extraction()
    e["regulator"] = []
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and "empty list" in i["description"] for i in issues)


def _ok_opamp_extraction() -> dict:
    return {
        "schema_version": {"base": "1.0", "categories": {"opamp": "1.0"}},
        "base": {
            "recommended_operating": {},
            "absolute_max": {},
            "pinout": [
                {"numbers": ["8"], "name": "SHDN", "type": "input", "subtype": None,
                 "description": None, "power_domain": None, "alt_functions": [],
                 "is_5v_tolerant": None, "absolute_max": None, "recommended": None,
                 "drive_strength": None, "notes": None,
                 "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}},
            ],
        },
        "categories": ["opamp"],
        "opamp": {"shutdown_pin": "8"},
    }


def test_opamp_unresolved_shutdown_pin_flags_error():
    e = _ok_opamp_extraction()
    e["opamp"]["shutdown_pin"] = "99"  # not in pinout
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and i["path"] == "opamp.shutdown_pin" for i in issues)


def test_opamp_resolved_shutdown_pin_no_issue():
    issues = verify_v14_extraction(_ok_opamp_extraction())
    pin_issues = [i for i in issues if "shutdown" in i["path"]]
    assert pin_issues == []


def _ok_mcu_extraction() -> dict:
    return {
        "schema_version": {"base": "1.0", "categories": {"mcu": "1.0"}},
        "base": {
            "recommended_operating": {},
            "absolute_max": {},
            "pinout": [
                {"numbers": ["7"], "name": "NRST", "type": "input", "subtype": None,
                 "description": None, "power_domain": None, "alt_functions": [],
                 "is_5v_tolerant": None, "absolute_max": None, "recommended": None,
                 "drive_strength": None, "notes": None,
                 "evidence": {"page": 3, "section": "Pinout", "confidence": "high", "method": "table"}},
            ],
        },
        "categories": ["mcu"],
        "mcu": {"reset_pin": "7"},
    }


def test_mcu_unresolved_reset_pin_flags_error():
    e = _ok_mcu_extraction()
    e["mcu"]["reset_pin"] = "99"  # not in pinout
    issues = verify_v14_extraction(e)
    assert any(i["severity"] == "error" and i["path"] == "mcu.reset_pin" for i in issues)


def test_mcu_resolved_reset_pin_no_issue():
    issues = verify_v14_extraction(_ok_mcu_extraction())
    pin_issues = [i for i in issues if "reset" in i["path"]]
    assert pin_issues == []


def test_diode_no_pin_fields_no_resolution_pass():
    """Diode schema has no pin-reference fields — verify no pin issues are produced."""
    e = {
        "schema_version": {"base": "1.0", "categories": {"diode": "1.0"}},
        "base": {"recommended_operating": {}, "absolute_max": {}, "pinout": []},
        "categories": ["diode"],
        "diode": {"diode_type": "schottky"},
    }
    issues = verify_v14_extraction(e)
    pin_issues = [i for i in issues if "_pin" in i["path"]]
    assert pin_issues == []


# --- Quality-finding tests ---------------------------------------------------

import os


def _make_extraction_with_score(pins, score):
    """Build an extraction dict with a given quality_score."""
    return {
        "extraction": {"quality_score": score},
        "pins": pins,
    }


def _write_extraction(tmpdir, mpn, extraction):
    import re
    sanitized = re.sub(r'[^A-Za-z0-9_.-]', '_', mpn)
    path = os.path.join(tmpdir, f"{sanitized}.json")
    with open(path, "w") as f:
        json.dump(extraction, f)


def test_low_quality_extraction_is_verified_and_flagged(tmp_path):
    # Build a required-external scenario (VIN pin, no cap connected) with
    # extraction["extraction"]["quality_score"] = 30.
    tmpdir = str(tmp_path / "extracted")
    os.makedirs(tmpdir)
    extraction = _make_extraction_with_score(
        [{"number": "1", "name": "BYPASS", "type": "power",
          "required_external": "100nF bypass capacitor"}],
        score=30,
    )
    _write_extraction(tmpdir, "MAX232", extraction)

    components = [
        {"reference": "U1", "type": "ic", "mpn": "MAX232",
         "pin_nets": {"1": "NET_BYPASS"}},
    ]
    nets = {
        "NET_BYPASS": {"pins": [
            {"component": "U1"},
        ]},
    }
    comp_lookup = {"U1": {"type": "ic"}}

    findings = verify_required_externals(components, nets, tmpdir, comp_lookup)
    types = {f["type"] for f in findings}
    # 1. quality is visible data:
    assert "extraction_quality_low" in types
    # 2. verification still ran on the low-quality extraction —
    #    the finding the copied test asserted must still be present:
    assert "missing_required_external" in types


# --- CLI tests ----------------------------------------------------------------
# The harness 4-check gate (Check 2) calls the v1.4 CLI in flag-based mode:
#   datasheet_verify.py --mpn <mpn> --extract-dir <dir> --self-consistency --json
# The legacy positional shape (datasheet_verify.py <path>) must keep working.

import subprocess
import sys

SCRIPT = MAIN_REPO_ROOT / "skills/datasheets/scripts/datasheet_verify.py"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def _seed_extract_dir(tmp_path, mpn: str, extraction: dict):
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    (extract_dir / f"{mpn}.json").write_text(json.dumps(extraction, indent=2))
    return extract_dir


def test_positional_mode_clean_extraction_exits_zero(tmp_path):
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", _ok_extraction())
    res = _run(str(extract_dir / "TEST-PART.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload == {"issues": [], "count": 0}


def test_flag_mode_clean_extraction_emits_violations_shape(tmp_path):
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", _ok_extraction())
    res = _run(
        "--mpn", "TEST-PART",
        "--extract-dir", str(extract_dir),
        "--self-consistency",
        "--json",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["violations"] == []
    assert payload["count"] == 0
    assert payload["mpn"] == "TEST-PART"
    assert payload["extract_dir"] == str(extract_dir)


def test_flag_mode_propagates_violations(tmp_path):
    bad = _ok_extraction()
    bad["regulator"]["feedback_pin"] = "99"  # not in pinout
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", bad)
    res = _run(
        "--mpn", "TEST-PART",
        "--extract-dir", str(extract_dir),
        "--self-consistency",
        "--json",
    )
    assert res.returncode == 1
    payload = json.loads(res.stdout)
    assert payload["count"] >= 1
    paths = [v["path"] for v in payload["violations"]]
    assert "regulator.feedback_pin" in paths


def test_flag_mode_without_json_prints_human_summary(tmp_path):
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", _ok_extraction())
    res = _run(
        "--mpn", "TEST-PART",
        "--extract-dir", str(extract_dir),
        "--self-consistency",
    )
    assert res.returncode == 0, res.stderr
    assert "TEST-PART: 0 issue" in res.stdout


def test_flag_mode_requires_self_consistency_flag(tmp_path):
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", _ok_extraction())
    res = _run(
        "--mpn", "TEST-PART",
        "--extract-dir", str(extract_dir),
        "--json",
    )
    assert res.returncode == 2
    assert "--self-consistency" in res.stderr


def test_flag_and_positional_mixed_exits_two(tmp_path):
    extract_dir = _seed_extract_dir(tmp_path, "TEST-PART", _ok_extraction())
    res = _run(
        str(extract_dir / "TEST-PART.json"),
        "--mpn", "TEST-PART",
        "--extract-dir", str(extract_dir),
        "--self-consistency",
    )
    assert res.returncode == 2
    assert "cannot mix" in res.stderr.lower()


def test_flag_mode_missing_extraction_exits_two(tmp_path):
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    res = _run(
        "--mpn", "DOES-NOT-EXIST",
        "--extract-dir", str(extract_dir),
        "--self-consistency",
        "--json",
    )
    assert res.returncode == 2
    assert "not found" in res.stderr.lower()


def test_no_args_exits_two():
    res = _run()
    assert res.returncode == 2
    assert "must supply" in res.stderr.lower()
