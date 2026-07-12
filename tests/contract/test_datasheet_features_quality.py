"""Quality-flag contract for datasheet_features (v2.0 spec §3.A.1).

Below-threshold extractions must be returned WITH a quality flag,
never silently converted to None (the rc.3 P0 failure class).
"""
import json
import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets" / "scripts"))
import datasheet_features  # noqa: E402


def _write_v13_extraction(tmp_path, mpn, score, version=2):
    ext = {
        "extraction_metadata": {
            "extraction_score": score,
            "extraction_version": version,
        },
        "topology": "buck",
        "pins": [{"number": "1", "function": "VIN"},
                 {"number": "3", "function": "VOUT"},
                 {"number": "4", "function": "EN", "threshold_high_v": 1.4}],
        "features": {"has_pg": False},
    }
    (tmp_path / f"{mpn}.json").write_text(json.dumps(ext))
    return tmp_path


def test_low_score_returns_features_with_untrusted_quality(tmp_path):
    d = _write_v13_extraction(tmp_path, "FAKE-REG-LO", score=2.0)
    feat = datasheet_features.get_regulator_features(
        "FAKE-REG-LO", extract_dir=str(d))
    assert feat is not None, "below-threshold must not be None (spec 3.A.1)"
    q = feat["quality"]
    assert q["trusted"] is False
    assert q["score"] == 2.0
    assert q["scale"] == "0-10"
    assert any("low_score" in r for r in q["reasons"])
    assert feat["topology"] == "buck"          # facts still present


def test_stale_version_returns_features_with_untrusted_quality(tmp_path):
    d = _write_v13_extraction(tmp_path, "FAKE-REG-V1", score=9.0, version=1)
    feat = datasheet_features.get_regulator_features(
        "FAKE-REG-V1", extract_dir=str(d))
    assert feat is not None
    assert feat["quality"]["trusted"] is False
    assert any("stale_version" in r for r in feat["quality"]["reasons"])


def test_good_score_returns_trusted_quality(tmp_path):
    d = _write_v13_extraction(tmp_path, "FAKE-REG-HI", score=8.5)
    feat = datasheet_features.get_regulator_features(
        "FAKE-REG-HI", extract_dir=str(d))
    assert feat is not None
    assert feat["quality"]["trusted"] is True
    assert feat["quality"]["reasons"] == []


def test_cache_miss_still_returns_none(tmp_path):
    assert datasheet_features.get_regulator_features(
        "NO-SUCH-MPN", extract_dir=str(tmp_path)) is None


def test_pin_function_keeps_trusted_gate(tmp_path):
    # get_pin_function returns a bare str, so it keeps the old gate —
    # explicitly, inside the function, not buried in _load().
    d = _write_v13_extraction(tmp_path, "FAKE-REG-LO2", score=2.0)
    assert datasheet_features.get_pin_function(
        "FAKE-REG-LO2", "4", extract_dir=str(d)) is None


def test_is_extraction_available_keeps_trusted_gate(tmp_path):
    d = _write_v13_extraction(tmp_path, "FAKE-REG-LO3", score=2.0)
    assert datasheet_features.is_extraction_available(
        "FAKE-REG-LO3", extract_dir=str(d)) is False
