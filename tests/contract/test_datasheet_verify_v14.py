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


# ---------------------------------------------------------------------------
# KH-337: v2-format extraction adapter tests
# ---------------------------------------------------------------------------

# Fixtures from harness tests/fixtures/datasheets-extracted/
V2_FIXTURE_DIR = HARNESS_ROOT / "tests" / "fixtures" / "datasheets-extracted"
LM2596_FIXTURE = V2_FIXTURE_DIR / "LM2596-ADJ.json"

verify_pin_voltages = mod.verify_pin_voltages
verify_decoupling = mod.verify_decoupling
run_datasheet_verification = mod.run_datasheet_verification


def _setup_v2_extract_dir(tmp_path, fixture_path=LM2596_FIXTURE, mpn="LM2596-ADJ"):
    """Copy a real v2 fixture into a temp extracted dir."""
    import shutil
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    shutil.copy(fixture_path, extract_dir / f"{mpn}.json")
    return str(extract_dir)


def _lm2596_components(pin_nets=None):
    """Minimal IC component dict for LM2596-ADJ."""
    return [{
        "reference": "U1",
        "type": "ic",
        "mpn": "LM2596-ADJ",
        "pin_nets": pin_nets or {"1": "VIN", "2": "OUT", "3": "GND", "4": "FB", "5": "ON_OFF"},
    }]


# --- RED test (KH-337): v2 fixture + pin above abs max → must emit finding ---

def test_v2_pin_voltage_abs_max_exceeded(tmp_path):
    """Pin 1 (VIN, domain VIN, abs_max=45V) connected to a 50V net → CRITICAL finding.

    This was the silent-zero bug: before the adapter, extraction.get('pins')
    returned None (v2 has base.pinout, not pins) → verifier skipped entirely.
    """
    extract_dir = _setup_v2_extract_dir(tmp_path)
    # Connect pin 1 (VIN) to a 50V net — exceeds LM2596 VIN_max of 45V
    components = _lm2596_components(pin_nets={"1": "+50V", "2": "OUT", "3": "GND"})
    rail_voltages = {"+50V": 50.0}
    nets = {}

    findings = verify_pin_voltages(components, nets, extract_dir, rail_voltages)
    types = {f["type"] for f in findings}
    assert "pin_voltage_abs_max_exceeded" in types, (
        f"Expected pin_voltage_abs_max_exceeded finding but got: {[f['type'] for f in findings]}"
    )
    crit = [f for f in findings if f["type"] == "pin_voltage_abs_max_exceeded"]
    assert crit[0]["severity"] == "CRITICAL"
    assert crit[0]["mpn"] == "LM2596-ADJ"
    assert crit[0]["pin_number"] == "1"
    assert crit[0]["abs_max_V"] == 45


def test_v2_pin_voltage_operating_exceeded(tmp_path):
    """Pin 1 (VIN, op_max=40V) connected to 42V net → operating-exceeded finding."""
    extract_dir = _setup_v2_extract_dir(tmp_path)
    components = _lm2596_components(pin_nets={"1": "+42V"})
    rail_voltages = {"+42V": 42.0}
    nets = {}

    findings = verify_pin_voltages(components, nets, extract_dir, rail_voltages)
    types = {f["type"] for f in findings}
    assert "pin_voltage_operating_exceeded" in types, (
        f"Expected pin_voltage_operating_exceeded but got: {[f['type'] for f in findings]}"
    )


# --- extraction_not_verifiable emitted for v2 (benign usage) ---

def test_v2_benign_usage_emits_not_verifiable(tmp_path):
    """Benign schematic usage of LM2596-ADJ (v2 extraction) must emit
    extraction_not_verifiable INFO finding because required-external and
    decoupling checks have no v2 equivalent data.

    No violation findings expected (VIN=12V well within 40V op / 45V abs max).
    """
    extract_dir = _setup_v2_extract_dir(tmp_path)
    components = _lm2596_components()
    rail_voltages = {"VIN": 12.0}
    nets = {"VIN": {"pins": [{"component": "U1"}, {"component": "C1"}]}}
    comp_lookup = {"U1": {"type": "ic"}, "C1": {"type": "capacitor"}}
    parsed_values = {}

    # Collect findings from all three verifiers via run_datasheet_verification
    analysis = {
        "file": "/tmp/fake.kicad_sch",
        "components": components + [
            {"reference": "C1", "type": "capacitor", "value": "100uF", "parsed_value": 100e-6},
        ],
        "nets": nets,
        "rail_voltages": rail_voltages,
    }

    import tempfile, shutil
    with tempfile.TemporaryDirectory() as tmp_proj:
        import os
        ds_dir = os.path.join(tmp_proj, "datasheets", "extracted")
        os.makedirs(ds_dir)
        shutil.copy(str(LM2596_FIXTURE), os.path.join(ds_dir, "LM2596-ADJ.json"))
        result = run_datasheet_verification(analysis, project_dir=tmp_proj)

    findings = result["findings"]
    types = [f["type"] for f in findings]

    # No voltage violations for 12V input
    assert "pin_voltage_abs_max_exceeded" not in types
    assert "pin_voltage_operating_exceeded" not in types

    # Exactly one not-verifiable finding (deduped across verifiers)
    nv_findings = [f for f in findings if f["type"] == "extraction_not_verifiable"]
    assert len(nv_findings) == 1, (
        f"Expected exactly 1 extraction_not_verifiable finding, got {len(nv_findings)}: {nv_findings}"
    )
    nv = nv_findings[0]
    assert nv["severity"] == "INFO"
    assert nv["mpn"] == "LM2596-ADJ"
    # Detail must mention what couldn't be checked
    assert "required-external" in nv["detail"] or "decoupling" in nv["detail"] or "application_circuit" in nv["detail"]


# --- v1-format regression: adapter must not change v1 behavior ---

def test_v1_format_pin_voltage_behavior_unchanged(tmp_path):
    """v1-format extraction (has 'pins' key) must produce identical results
    to pre-adapter behavior — the adapter must be transparent for v1.
    """
    # Craft a v1-format extraction with a known abs_max violation
    v1_extraction = {
        "extraction": {"quality_score": 90},
        "pins": [
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 5.5, "voltage_operating_max": 5.0},
        ],
    }
    import re, tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "FAKE-IC.json")
        with open(path, "w") as f:
            json.dump(v1_extraction, f)

        components = [{"reference": "U2", "type": "ic", "mpn": "FAKE-IC",
                       "pin_nets": {"1": "+6V"}}]
        rail_voltages = {"+6V": 6.0}

        findings = verify_pin_voltages(components, {}, tmpdir, rail_voltages)

    assert any(f["type"] == "pin_voltage_abs_max_exceeded" for f in findings), (
        "v1-format extraction must still trigger pin_voltage_abs_max_exceeded"
    )
    # No not-verifiable finding for v1 format
    assert not any(f["type"] == "extraction_not_verifiable" for f in findings), (
        "extraction_not_verifiable must NOT fire for v1-format extractions"
    )


# --- KH-337 fix round 1 regressions ---

def _sv(max_=None, min_=None, typ=None, unit="V"):
    """Full-shape SpecValue dict matching spec_value.schema.json producers."""
    return {
        "condition": None, "max": max_, "min": min_, "notes": None,
        "typ": typ, "unit": unit,
        "evidence": {"confidence": "high", "method": "table",
                     "page": 5, "section": "Abs Max"},
    }


def _run_full_pipeline(tmp_path, mpn, extraction, analysis_overrides=None):
    """Seed <tmp_path>/datasheets/extracted/<mpn>.json and run the full
    run_datasheet_verification pipeline (all three verifiers)."""
    ds_dir = tmp_path / "datasheets" / "extracted"
    ds_dir.mkdir(parents=True, exist_ok=True)
    (ds_dir / f"{mpn}.json").write_text(json.dumps(extraction))
    analysis = {
        "file": str(tmp_path / "fake.kicad_sch"),
        "components": [
            {"reference": "U2", "type": "ic", "mpn": mpn,
             "pin_nets": {"1": "+3V3", "2": "GND"}},
        ],
        "nets": {"+3V3": {"pins": [{"component": "U2"}]},
                 "GND": {"pins": [{"component": "U2"}]}},
        "rail_voltages": {"+3V3": 3.3},
    }
    if analysis_overrides:
        analysis.update(analysis_overrides)
    return run_datasheet_verification(analysis, project_dir=str(tmp_path))


def test_v1_without_application_circuit_no_not_verifiable(tmp_path):
    """CRITICAL regression (fix round 1): a v1-format extraction with pins but
    WITHOUT the optional application_circuit field must run the FULL pipeline
    with zero extraction_not_verifiable findings — v1 behavior byte-identical.
    """
    v1_extraction = {
        "extraction": {"quality_score": 90},
        "pins": [
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 5.5, "voltage_operating_max": 5.0},
            {"number": "2", "name": "GND", "type": "ground"},
        ],
        # no application_circuit — optional in v1, must stay a silent skip
    }
    result = _run_full_pipeline(tmp_path, "FAKE-IC", v1_extraction)
    types = [f["type"] for f in result["findings"]]
    assert "extraction_not_verifiable" not in types, (
        f"v1 cache without application_circuit must not emit "
        f"extraction_not_verifiable; findings: {result['findings']}"
    )


def test_v2_per_pin_abs_max_overrides_domain(tmp_path):
    """Fix round 1: a per-pin absolute_max SpecValue list (pinout schema shape)
    must override the domain-level abs-max lookup.

    Domain VIN abs max = 45V; per-pin abs max = 6V. Pin on a 7V net must be
    flagged against 6V (domain lookup alone would pass 7V < 45V silently).
    """
    v2_extraction = {
        "base": {
            "absolute_max": {"VIN_max": [_sv(max_=45)]},
            "recommended_operating": {"VIN": [_sv(max_=40, min_=4.5)]},
            "pinout": [
                {"numbers": ["1"], "name": "SENSE", "type": "input",
                 "subtype": None, "description": None, "power_domain": "VIN",
                 "alt_functions": [], "is_5v_tolerant": None,
                 "absolute_max": [_sv(max_=6)],  # per-pin rating, tighter than domain
                 "recommended": None, "drive_strength": None, "notes": None,
                 "evidence": {"confidence": "high", "method": "table",
                              "page": 3, "section": "Pinout"}},
            ],
        },
        "categories": [],
        "extraction": {"quality_score": 95},
    }
    result = _run_full_pipeline(
        tmp_path, "FAKE-V2", v2_extraction,
        analysis_overrides={
            "components": [
                {"reference": "U3", "type": "ic", "mpn": "FAKE-V2",
                 "pin_nets": {"1": "+7V"}},
            ],
            "nets": {"+7V": {"pins": [{"component": "U3"}]}},
            "rail_voltages": {"+7V": 7.0},
        },
    )
    abs_findings = [f for f in result["findings"]
                    if f["type"] == "pin_voltage_abs_max_exceeded"]
    assert abs_findings, (
        f"7V on a pin with per-pin abs max 6V must be flagged; "
        f"findings: {result['findings']}"
    )
    assert abs_findings[0]["abs_max_V"] == 6, (
        f"per-pin abs max (6V) must win over domain limit (45V); "
        f"got abs_max_V={abs_findings[0]['abs_max_V']}"
    )


def test_quality_low_emitted_once_per_mpn(tmp_path):
    """Fix round 1: extraction_quality_low must appear exactly once per MPN
    in run_datasheet_verification output (each verifier emits independently;
    the orchestrator dedups).
    """
    v1_extraction = {
        "extraction": {"quality_score": 30},
        "pins": [
            {"number": "1", "name": "VCC", "type": "power",
             "voltage_abs_max": 5.5, "voltage_operating_max": 5.0},
        ],
        # no application_circuit: each verifier still emits its own quality
        # finding (emitted right after _load_extraction, before data guards),
        # so pre-dedup this MPN produces 3 identical extraction_quality_low.
    }
    result = _run_full_pipeline(tmp_path, "LOWQ-IC", v1_extraction)
    quality = [f for f in result["findings"]
               if f["type"] == "extraction_quality_low"]
    assert len(quality) == 1, (
        f"expected exactly 1 extraction_quality_low for one MPN, "
        f"got {len(quality)}: {quality}"
    )
    assert quality[0]["mpn"] == "LOWQ-IC"
