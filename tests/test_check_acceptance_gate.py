"""Unit tests for validate/check_acceptance_gate.py."""
TIER = "unit"

import json
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))


def test_check_quality_score_passes_at_threshold():
    from validate.check_acceptance_gate import check_quality_score, Status

    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp) / "LM2596_ADJ.json"
        cache.write_text(json.dumps({"extraction": {"quality_score": 60}}))
        result = check_quality_score(cache_path=cache, threshold=60)

    assert result.status is Status.PASS
    assert result.details["score"] == 60


def test_check_quality_score_fails_below_threshold():
    from validate.check_acceptance_gate import check_quality_score, Status

    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp) / "x.json"
        cache.write_text(json.dumps({"extraction": {"quality_score": 59}}))
        result = check_quality_score(cache_path=cache, threshold=60)

    assert result.status is Status.FAIL
    assert result.details["score"] == 59


def test_check_quality_score_errors_on_missing_field():
    from validate.check_acceptance_gate import check_quality_score, Status

    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp) / "x.json"
        cache.write_text(json.dumps({"extraction": {}}))
        result = check_quality_score(cache_path=cache, threshold=60)

    assert result.status is Status.ERROR


def test_check_quality_score_errors_on_missing_file():
    from validate.check_acceptance_gate import check_quality_score, Status

    with tempfile.TemporaryDirectory() as tmp:
        result = check_quality_score(
            cache_path=Path(tmp) / "missing.json", threshold=60)

    assert result.status is Status.ERROR


def _write_pair(tmp, *, mpn="LM2596-ADJ", cache=None, vector=None):
    """Helper: write cache + vector files into tmp dir, return paths."""
    cache_path = Path(tmp) / "LM2596_ADJ.json"
    cache_path.write_text(json.dumps(cache or {}))
    vector_path = Path(tmp) / "lm2596-adj.json"
    vector_path.write_text(json.dumps(vector or {"mpn": mpn, "fields": []}))
    return cache_path, vector_path


def test_check_sanity_vector_diff_passes_within_tolerance():
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {
        "base": {"absolute_max": {"VIN_max": [
            {"min": None, "typ": None, "max": 45.5, "unit": "V"}
        ]}}
    }
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.absolute_max.VIN_max",
             "expected": {"max": 45, "unit": "V"},
             "page": 5, "tolerance_pct": 5},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.PASS, result.details
    assert result.details["fields_compared"] == 1
    assert result.details["divergences"] == []


def test_check_sanity_vector_diff_fails_outside_tolerance():
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {
        "base": {"absolute_max": {"VIN_max": [
            {"min": None, "typ": None, "max": 50, "unit": "V"}
        ]}}
    }
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.absolute_max.VIN_max",
             "expected": {"max": 45, "unit": "V"},
             "page": 5, "tolerance_pct": 5},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.FAIL
    div = result.details["divergences"][0]
    assert div["path"] == "base.absolute_max.VIN_max"
    assert div["expected"] == {"max": 45, "unit": "V"}
    assert div["actual"] == {"max": 50, "unit": "V", "min": None, "typ": None}
    assert div["tolerance_pct"] == 5
    assert div["page"] == 5
    assert "delta_pct" in div
    assert div["delta_pct"] > 5


def test_check_sanity_vector_diff_unit_mismatch_is_divergence():
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {
        "base": {"absolute_max": {"VIN_max": [
            {"min": None, "typ": None, "max": 45, "unit": "mV"}
        ]}}
    }
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.absolute_max.VIN_max",
             "expected": {"max": 45, "unit": "V"},
             "page": 5, "tolerance_pct": 5},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.FAIL
    div = result.details["divergences"][0]
    assert div["actual"]["unit"] == "mV"
    assert "unit_mismatch" in div.get("reason", "") or \
           div.get("expected_unit") != div.get("actual_unit")


def test_check_sanity_vector_diff_missing_path_is_divergence():
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {"base": {}}
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.absolute_max.VIN_max",
             "expected": {"max": 45, "unit": "V"},
             "page": 5, "tolerance_pct": 5},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.FAIL
    div = result.details["divergences"][0]
    assert div["actual"] is None
    assert "not found" in div.get("reason", "").lower() or \
           div.get("reason", "").startswith("path")


def test_check_sanity_vector_diff_pin_count_dimensionless():
    """pin_count vectors omit 'unit'; cache also omits unit. Compare typ only."""
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {"base": {"package": {"pin_count": 5}}}  # scalar, not list
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.package.pin_count",
             "expected": {"typ": 5},
             "page": 4, "tolerance_pct": 0},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.PASS, result.details


def test_check_sanity_vector_diff_enum_field():
    """expected_enum vectors compare actual.name (or .code) against list."""
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    cache = {"base": {"package": {"code": "TO-263"}}}
    vector = {
        "mpn": "LM2596-ADJ",
        "fields": [
            {"path": "base.package.code",
             "expected_enum": ["TO-220", "TO-263"],
             "page": 4, "tolerance_pct": 0},
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        c, v = _write_pair(tmp, cache=cache, vector=vector)
        result = check_sanity_vector_diff(cache_path=c, sanity_vector_path=v)

    assert result.status is Status.PASS, result.details


def test_check_sanity_vector_diff_errors_on_missing_files():
    from validate.check_acceptance_gate import check_sanity_vector_diff, Status

    with tempfile.TemporaryDirectory() as tmp:
        result = check_sanity_vector_diff(
            cache_path=Path(tmp) / "missing.json",
            sanity_vector_path=Path(tmp) / "missing.json",
        )
    assert result.status is Status.ERROR


# Check 1 tests

def test_check_schema_validation_skipped_when_tool_missing():
    from validate.check_acceptance_gate import check_schema_validation, Status

    with tempfile.TemporaryDirectory() as tmp:
        result = check_schema_validation(
            mpn="LM2596-ADJ", extract_dir=Path(tmp),
            kicad_happy_dir=Path(tmp) / "no-kh")

    assert result.status is Status.SKIPPED
    assert "validate_extraction_result" in result.details["reason"] or \
           "Phase 3a" in result.details["reason"]


def test_check_schema_validation_passes_with_stub_tool():
    from validate.check_acceptance_gate import check_schema_validation, Status
    import validate.check_acceptance_gate as mod

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    original = mod.subprocess.run
    mod.subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            extract = Path(tmp)
            for tid in ("scout", "base", "pinout", "regulator"):
                (extract / f"LM2596-ADJ.{tid}.result.json").write_text("{}")
            kh = Path(tmp) / "kh"
            scripts_dir = kh / "skills" / "datasheets" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "validate_extraction_result.py").write_text("#")
            result = check_schema_validation(
                mpn="LM2596-ADJ", extract_dir=extract, kicad_happy_dir=kh)
    finally:
        mod.subprocess.run = original

    assert result.status is Status.PASS, result.details
    assert len(result.details["task_results"]) == 4


def test_check_schema_validation_fails_on_invalid_task():
    from validate.check_acceptance_gate import check_schema_validation, Status
    import validate.check_acceptance_gate as mod

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 1 if "pinout" in str(cmd) else 0
            stdout = ""
            stderr = "schema violation: missing 'pins'" if "pinout" in str(cmd) else ""
        return R()

    original = mod.subprocess.run
    mod.subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            extract = Path(tmp)
            for tid in ("scout", "base", "pinout", "regulator"):
                (extract / f"LM2596-ADJ.{tid}.result.json").write_text("{}")
            kh = Path(tmp) / "kh"
            scripts_dir = kh / "skills" / "datasheets" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "validate_extraction_result.py").write_text("#")
            result = check_schema_validation(
                mpn="LM2596-ADJ", extract_dir=extract, kicad_happy_dir=kh)
    finally:
        mod.subprocess.run = original

    assert result.status is Status.FAIL
    failures = [t for t in result.details["task_results"] if not t["valid"]]
    assert len(failures) == 1


# Check 2 tests

def test_check_self_consistency_skipped_when_tool_missing():
    from validate.check_acceptance_gate import check_self_consistency, Status

    with tempfile.TemporaryDirectory() as tmp:
        result = check_self_consistency(
            mpn="LM2596-ADJ", extract_dir=Path(tmp),
            kicad_happy_dir=Path(tmp) / "no-kh")
    assert result.status is Status.SKIPPED


def test_check_self_consistency_errors_on_missing_cache():
    from validate.check_acceptance_gate import check_self_consistency, Status

    with tempfile.TemporaryDirectory() as tmp:
        kh = Path(tmp) / "kh"
        scripts_dir = kh / "skills" / "datasheets" / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "datasheet_verify.py").write_text("#")
        result = check_self_consistency(
            mpn="LM2596-ADJ", extract_dir=Path(tmp), kicad_happy_dir=kh)
    assert result.status is Status.ERROR


def test_check_self_consistency_passes_on_exit_zero():
    """datasheet_verify.py <cache> exits 0 → PASS."""
    from validate.check_acceptance_gate import check_self_consistency, Status
    import validate.check_acceptance_gate as mod

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 0
            stdout = "OK: 0 issues"
            stderr = ""
        return R()

    original = mod.subprocess.run
    mod.subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            extract = Path(tmp)
            (extract / "LM2596-ADJ.json").write_text("{}")
            kh = Path(tmp) / "kh"
            scripts_dir = kh / "skills" / "datasheets" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "datasheet_verify.py").write_text("#")
            result = check_self_consistency(
                mpn="LM2596-ADJ", extract_dir=extract, kicad_happy_dir=kh)
    finally:
        mod.subprocess.run = original

    assert result.status is Status.PASS


def test_check_self_consistency_fails_on_exit_nonzero():
    """datasheet_verify.py <cache> exits nonzero → FAIL with stdout/stderr."""
    from validate.check_acceptance_gate import check_self_consistency, Status
    import validate.check_acceptance_gate as mod

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 1
            stdout = "ISSUE: absolute_max VIN_max (45) < recommended_operating VIN max (40)"
            stderr = ""
        return R()

    original = mod.subprocess.run
    mod.subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            extract = Path(tmp)
            (extract / "LM2596-ADJ.json").write_text("{}")
            kh = Path(tmp) / "kh"
            scripts_dir = kh / "skills" / "datasheets" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "datasheet_verify.py").write_text("#")
            result = check_self_consistency(
                mpn="LM2596-ADJ", extract_dir=extract, kicad_happy_dir=kh)
    finally:
        mod.subprocess.run = original

    assert result.status is Status.FAIL
    assert "ISSUE" in result.details["stdout"]


def test_run_gate_aggregates_4_checks_into_pass():
    from validate.check_acceptance_gate import run_gate, Status
    import validate.check_acceptance_gate as mod

    def fake_run(cmd, **kwargs):
        class R:
            returncode = 0
            stdout = (
                json.dumps({"violations": []}) if "datasheet_verify" in str(cmd)
                else ""
            )
            stderr = ""
        return R()

    original = mod.subprocess.run
    mod.subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            extract = Path(tmp) / "extracted"
            extract.mkdir()
            cache = extract / "LM2596-ADJ.json"
            cache.write_text(json.dumps({
                "extraction": {"quality_score": 87},
                "base": {"absolute_max": {"VIN_max": [
                    {"max": 45, "unit": "V"}]}},
            }))
            for tid in ("scout", "base", "pinout", "regulator"):
                (extract / f"LM2596-ADJ.{tid}.result.json").write_text("{}")
            sanity = Path(tmp) / "lm2596-adj.json"
            sanity.write_text(json.dumps({
                "mpn": "LM2596-ADJ",
                "fields": [
                    {"path": "base.absolute_max.VIN_max",
                     "expected": {"max": 45, "unit": "V"},
                     "page": 5, "tolerance_pct": 5}
                ],
            }))
            kh = Path(tmp) / "kh"
            scripts_dir = kh / "skills" / "datasheets" / "scripts"
            scripts_dir.mkdir(parents=True)
            for stem in ("validate_extraction_result", "datasheet_verify"):
                (scripts_dir / f"{stem}.py").write_text("#")
            results = run_gate(
                mpn="LM2596-ADJ", extract_dir=extract,
                sanity_vector_path=sanity, kicad_happy_dir=kh)
    finally:
        mod.subprocess.run = original

    assert len(results) == 4
    assert all(r.status is Status.PASS for r in results), \
        [(r.name, r.status, r.summary) for r in results]


def test_run_gate_marks_skipped_when_phase3a_tools_missing():
    """No Phase 3a tools → 2 PASS (Check 3 + Check 4) + 2 SKIPPED."""
    from validate.check_acceptance_gate import run_gate, Status

    with tempfile.TemporaryDirectory() as tmp:
        extract = Path(tmp) / "extracted"
        extract.mkdir()
        cache = extract / "LM2596-ADJ.json"
        cache.write_text(json.dumps({
            "extraction": {"quality_score": 87},
            "base": {"absolute_max": {"VIN_max": [
                {"max": 45, "unit": "V"}]}},
        }))
        sanity = Path(tmp) / "lm2596-adj.json"
        sanity.write_text(json.dumps({
            "mpn": "LM2596-ADJ",
            "fields": [
                {"path": "base.absolute_max.VIN_max",
                 "expected": {"max": 45, "unit": "V"},
                 "page": 5, "tolerance_pct": 5}
            ],
        }))
        kh = Path(tmp) / "no-such-kh"
        results = run_gate(
            mpn="LM2596-ADJ", extract_dir=extract,
            sanity_vector_path=sanity, kicad_happy_dir=kh)

    statuses = [r.status for r in results]
    assert statuses.count(Status.PASS) == 2, statuses
    assert statuses.count(Status.SKIPPED) == 2, statuses


def test_render_text_report_includes_all_checks():
    from validate.check_acceptance_gate import (
        render_text_report, CheckResult, Status,
    )
    results = [
        CheckResult("Check 1 — Schema validation", Status.PASS, "4/4 valid"),
        CheckResult("Check 2 — datasheet_verify.py", Status.SKIPPED,
                    "tool not found", details={"reason": "Phase 3a"}),
        CheckResult("Check 3 — Quality score >= 60", Status.PASS, "score=87"),
        CheckResult("Check 4 — Sanity-vector diff", Status.PASS, "10/10"),
    ]
    text = render_text_report(results)
    for label in ("Check 1", "Check 2", "Check 3", "Check 4",
                  "PASS", "SKIPPED", "PARTIAL"):
        assert label in text, f"missing {label!r}:\n{text}"


def test_compute_exit_code():
    from validate.check_acceptance_gate import (
        compute_exit_code, CheckResult, Status,
    )
    pass_only = [CheckResult("c", Status.PASS, "")] * 4
    has_fail = pass_only[:3] + [CheckResult("c4", Status.FAIL, "")]
    has_skip = pass_only[:3] + [CheckResult("c4", Status.SKIPPED, "")]
    has_error = pass_only[:3] + [CheckResult("c4", Status.ERROR, "")]
    assert compute_exit_code(pass_only) == 0
    assert compute_exit_code(has_fail) == 1
    assert compute_exit_code(has_skip) == 2
    assert compute_exit_code(has_error) == 3


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
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({len(tests)} total)")
    sys.exit(1 if failed else 0)
