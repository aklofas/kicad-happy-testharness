"""Unit tests for regression/schema_era.py (A8 schema-era module).

Runs under bare python3 in the pre-push hook. Each test is a callable
test_* function; main() at bottom runs them all and exits non-zero on any
failure.
"""
from __future__ import annotations

TIER = "unit"

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from regression import schema_era


def test_normalize_none_returns_none():
    assert schema_era.normalize_schema_era(None) is None


def test_normalize_bare_string_wraps_in_object():
    result = schema_era.normalize_schema_era("v1.4")
    assert result == {
        "era": "v1.4",
        "tagged_by_rule": None,
        "tagged_at": None,
        "tagged_reason": None,
    }


def test_normalize_full_object_passes_through():
    obj = {"era": "pre-v1.4", "tagged_by_rule": "PU-001",
           "tagged_at": "2026-05-17T15:00:00Z", "tagged_reason": "reason"}
    assert schema_era.normalize_schema_era(obj) == obj


def test_normalize_object_without_era_raises_valueerror():
    try:
        schema_era.normalize_schema_era({"tagged_by_rule": "PU-001"})
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_normalize_unknown_era_raises_valueerror():
    try:
        schema_era.normalize_schema_era("v9.9")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_normalize_unsupported_type_raises_typeerror():
    try:
        schema_era.normalize_schema_era(42)
    except TypeError:
        return
    raise AssertionError("expected TypeError")


def test_era_of_present():
    a = {"schema_era": "v1.4"}
    assert schema_era.era_of(a) == "v1.4"


def test_era_of_absent():
    assert schema_era.era_of({}) is None


def test_era_of_object_form():
    a = {"schema_era": {"era": "pre-v1.4", "tagged_by_rule": None,
                        "tagged_at": None, "tagged_reason": None}}
    assert schema_era.era_of(a) == "pre-v1.4"


def test_era_filter_all_passes_everything():
    assert schema_era.era_filter({"schema_era": "v1.4"}, "all") is True
    assert schema_era.era_filter({"schema_era": "pre-v1.4"}, "all") is True
    assert schema_era.era_filter({}, "all") is True


def test_era_filter_matches_current_or_untagged():
    assert schema_era.era_filter({"schema_era": "v1.4"}, "v1.4") is True
    assert schema_era.era_filter({}, "v1.4") is True
    assert schema_era.era_filter({"schema_era": "pre-v1.4"}, "v1.4") is False


def test_era_filter_matches_explicit_pre_v14():
    assert schema_era.era_filter({"schema_era": "pre-v1.4"}, "pre-v1.4") is True
    assert schema_era.era_filter({"schema_era": "v1.4"}, "pre-v1.4") is False
    # Untagged is filtered OUT when explicitly asking for non-current era
    assert schema_era.era_filter({}, "pre-v1.4") is False


def _write_registry(tmp_dir: Path, era: str = "v1.4") -> Path:
    path = tmp_dir / "v14_changed_detectors.json"
    path.write_text(json.dumps({
        "era": era,
        "generated_at": "2026-05-17T15:00:00Z",
        "kicad_happy_commit": "abc1234",
        "kicad_happy_branch": "v1.4-dev",
        "source_files_scanned": ["validation_detectors.py"],
        "detectors": {
            "validate_pullups": {
                "rules": ["PU-001", "VM-001"],
                "primary_rule": "PU-001",
                "source_file": "validation_detectors.py",
                "emit_line_count": 6,
                "gating_summary": "datasheet-gated on ds.quality >= 60",
            },
            "validate_led_resistors": {
                "rules": ["LR-001"],
                "primary_rule": "LR-001",
                "source_file": "validation_detectors.py",
                "emit_line_count": 3,
                "gating_summary": "datasheet-gated on LED Vf + If",
            },
        },
    }))
    return path


def test_load_versioned_detector_map_returns_dict():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        result = schema_era.load_versioned_detector_map("v1.4", registry_dir=Path(tmp))
        assert "validate_pullups" in result["detectors"]
        assert result["era"] == "v1.4"


def test_load_versioned_detector_map_missing_raises():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            schema_era.load_versioned_detector_map("v1.4", registry_dir=Path(tmp))
        except FileNotFoundError:
            return
        raise AssertionError("expected FileNotFoundError")


def test_is_versioned_detector_true_false():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assert schema_era.is_versioned_detector("validate_pullups", era="v1.4",
                                                registry_dir=Path(tmp)) is True
        assert schema_era.is_versioned_detector("detect_rc_filters", era="v1.4",
                                                registry_dir=Path(tmp)) is False


def test_primary_rule_for_detector_multi_rule_returns_lowest():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assert schema_era.primary_rule_for_detector("validate_pullups",
                                                    era="v1.4",
                                                    registry_dir=Path(tmp)) == "PU-001"


def test_primary_rule_for_unversioned_returns_none():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assert schema_era.primary_rule_for_detector("detect_rc_filters",
                                                    era="v1.4",
                                                    registry_dir=Path(tmp)) is None


def test_stamp_versioned_detector_writes_full_object():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assertion = {"check": {"detector_filter": "validate_pullups"}}
        result = schema_era.stamp_schema_era(
            assertion, era="v1.4",
            tagged_at="2026-05-17T15:00:00Z",
            registry_dir=Path(tmp),
        )
        assert result is True
        assert assertion["schema_era"] == {
            "era": "v1.4",
            "tagged_by_rule": "PU-001",
            "tagged_at": "2026-05-17T15:00:00Z",
            "tagged_reason": "datasheet-gated on ds.quality >= 60",
        }


def test_stamp_unversioned_detector_skips():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assertion = {"check": {"detector_filter": "detect_rc_filters"}}
        result = schema_era.stamp_schema_era(
            assertion, era="v1.4", registry_dir=Path(tmp),
        )
        assert result is False
        assert "schema_era" not in assertion


def test_stamp_already_tagged_skips_without_force():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assertion = {
            "check": {"detector_filter": "validate_pullups"},
            "schema_era": {"era": "pre-v1.4", "tagged_by_rule": "PU-001",
                           "tagged_at": "old", "tagged_reason": "old"},
        }
        result = schema_era.stamp_schema_era(
            assertion, era="v1.4", registry_dir=Path(tmp),
        )
        assert result is False
        assert assertion["schema_era"]["era"] == "pre-v1.4"


def test_stamp_already_tagged_overwrites_with_force():
    with tempfile.TemporaryDirectory() as tmp:
        _write_registry(Path(tmp))
        assertion = {
            "check": {"detector_filter": "validate_pullups"},
            "schema_era": {"era": "pre-v1.4", "tagged_by_rule": "PU-001",
                           "tagged_at": "old", "tagged_reason": "old"},
        }
        result = schema_era.stamp_schema_era(
            assertion, era="v1.4",
            tagged_at="new",
            registry_dir=Path(tmp), force=True,
        )
        assert result is True
        assert assertion["schema_era"]["era"] == "v1.4"
        assert assertion["schema_era"]["tagged_at"] == "new"


def main() -> int:
    tests = [v for k, v in globals().items()
             if k.startswith("test_") and callable(v)]
    failed = []
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            print(f"FAIL {t.__name__}: {type(e).__name__}: {e}")
            failed.append(t.__name__)
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
