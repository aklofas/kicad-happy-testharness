"""Schema-era registry requirements and independent selection/stamp eras."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from regression import schema_era as se  # noqa: E402

pytestmark = pytest.mark.unit

REG = HARNESS_ROOT / "tests" / "fixtures" / "h0" / "plan5" / "registry_dir"


def test_v30_is_known_and_current_unchanged():
    assert se.KNOWN_ERAS == ("pre-v1.4", "v1.4", "v3.0")
    assert se.CURRENT_SCHEMA_ERA == "v3.0"   # bumped at the v3.0 relock
    assert se.normalize_schema_era("v3.0")["era"] == "v3.0"
    assert se._registry_filename("v3.0") == "v30_changed_detectors.json"


def test_lenient_defaults_unchanged(tmp_path):
    assert se.is_versioned_detector("detect_rc_filters", era="v3.0", registry_dir=tmp_path) is False
    assert se.primary_rule_for_detector("detect_rc_filters", era="v3.0", registry_dir=tmp_path) is None
    assert se.gating_summary_for_detector("detect_rc_filters", era="v3.0", registry_dir=tmp_path) is None
    assert list(se.iter_versioned_detector_functions(era="v3.0", registry_dir=tmp_path)) == []


def test_required_raises_on_missing_registry(tmp_path):
    for fn in (se.is_versioned_detector, se.primary_rule_for_detector,
               se.gating_summary_for_detector):
        with pytest.raises(FileNotFoundError):
            fn("detect_rc_filters", era="v3.0", registry_dir=tmp_path, required=True)
    with pytest.raises(FileNotFoundError):
        list(se.iter_versioned_detector_functions(era="v3.0", registry_dir=tmp_path, required=True))


def test_v30_registry_selects_fixture_detector():
    assert se.is_versioned_detector("detect_rc_filters", era="v3.0", registry_dir=REG, required=True)
    assert se.primary_rule_for_detector("detect_rc_filters", era="v3.0", registry_dir=REG) == "RC-DET"
    assert not se.is_versioned_detector("validate_pullups", era="v3.0", registry_dir=REG)


def test_stamp_select_era_differs_from_stamp_value():
    a = {"id": "SEED-1", "check": {"path": "findings", "detector_filter": "detect_rc_filters",
                                   "op": "min_count", "value": 1}}
    tagged = se.stamp_schema_era(a, era="v1.4", select_era="v3.0", registry_dir=REG,
                                 tagged_at="2026-10-14T00:00:00Z", required=True)
    assert tagged is True
    assert a["schema_era"] == {"era": "v1.4", "tagged_by_rule": "RC-DET",
                               "tagged_at": "2026-10-14T00:00:00Z",
                               "tagged_reason": "fixture: rc filters reshaped in v3.0"}


def test_stamp_required_missing_registry_raises(tmp_path):
    a = {"id": "SEED-1", "check": {"detector_filter": "detect_rc_filters"}}
    with pytest.raises(FileNotFoundError):
        se.stamp_schema_era(a, era="v1.4", select_era="v3.0", registry_dir=tmp_path, required=True)
