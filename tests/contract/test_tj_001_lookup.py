"""Contract tests for TJ-001 junction-temp-exceeds-TJmax detector (4c)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def _build_facts(theta_ja_specs=None, tj_max_specs=None, tj_max_key="TJ"):
    fake_base = MagicMock()
    fake_base.thermal = {"theta_ja": theta_ja_specs} if theta_ja_specs else {}
    fake_base.absolute_max = {tj_max_key: tj_max_specs} if tj_max_specs else {}
    fake_facts = MagicMock()
    fake_facts.base = fake_base
    return fake_facts


def test_tj_001_returns_empty_for_empty_assessments(tmp_path):
    from lookup_detectors import detect_tj_exceeds_max
    assert detect_tj_exceeds_max([], source="thermal", cache_dir=tmp_path) == []


def test_tj_001_skips_when_no_facts(tmp_path):
    import lookup_detectors

    assessments = [{
        "ref": "U1", "value": "UNKNOWN", "ambient_c": 25.0,
        "pdiss_w": 1.0, "rtheta_ja_effective": 50.0,
        "tj_estimated_c": 75.0, "tj_max_c": 125.0,
    }]
    with patch.object(lookup_detectors, "get_facts", return_value=None):
        assert lookup_detectors.detect_tj_exceeds_max(
            assessments, source="thermal", cache_dir=tmp_path) == []


def test_tj_001_fires_when_v14_tj_exceeds_v14_tjmax(tmp_path):
    """When v1.4 theta_ja and absolute_max.TJ are both present, recompute
    TJ and emit error if exceeds."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    # theta_ja = 75°C/W (typ); pdiss = 1.5W; ambient = 50°C → TJ = 50 + 1.5*75 = 162.5°C
    # TJmax = 150°C → exceeds
    theta_sv = SpecValue(unit="C/W", evidence=ev, typ=75.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev, max=150.0)

    assessments = [{
        "ref": "U1", "value": "FAKE-REG", "ambient_c": 50.0,
        "pdiss_w": 1.5, "rtheta_ja_effective": 75.0,
        "tj_estimated_c": 162.5, "tj_max_c": 150.0,
    }]
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv])):
        findings = lookup_detectors.detect_tj_exceeds_max(
            assessments, source="thermal", cache_dir=tmp_path)

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert tj, f"Expected TJ-001 finding, got: {findings}"
    assert all(f["severity"] == "error" for f in tj)
    assert all(f["confidence"] == "datasheet-backed" for f in tj)
    assert tj[0].get("tj_estimated_c") == 162.5
    assert tj[0].get("tj_max_c") == 150.0


def test_tj_001_no_finding_when_within_tjmax(tmp_path):
    """When recomputed TJ is below TJmax, no finding."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    theta_sv = SpecValue(unit="C/W", evidence=ev, typ=20.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev, max=150.0)

    assessments = [{
        "ref": "U1", "value": "FAKE-REG", "ambient_c": 25.0,
        "pdiss_w": 0.5, "rtheta_ja_effective": 20.0,
        "tj_estimated_c": 35.0, "tj_max_c": 150.0,
    }]
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv])):
        findings = lookup_detectors.detect_tj_exceeds_max(
            assessments, source="thermal", cache_dir=tmp_path)

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert tj == [], f"Expected no TJ-001 (TJ=35°C << TJmax=150°C), got: {tj}"


def test_tj_001_resolves_tjmax_synonym(tmp_path):
    """Datasheet uses 'TJ_max' key — synonym resolves to TJ."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    theta_sv = SpecValue(unit="C/W", evidence=ev, typ=80.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev, max=125.0)

    assessments = [{
        "ref": "U1", "value": "FAKE-REG", "ambient_c": 25.0,
        "pdiss_w": 2.0, "rtheta_ja_effective": 80.0,
        "tj_estimated_c": 185.0, "tj_max_c": 125.0,
    }]
    # absolute_max key is "TJ_max" not "TJ" — synonym table must resolve.
    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv], tj_max_key="TJ_max")):
        findings = lookup_detectors.detect_tj_exceeds_max(
            assessments, source="thermal", cache_dir=tmp_path)

    assert any(f.get("rule_id") == "TJ-001" for f in findings), (
        "Expected TJ-001 to fire via TJ_max synonym resolution"
    )


# ===========================================================================
# Cache-variant locks — stale + low-conf-theta + low-conf-tjmax + max-fallback (LOG 13)
# ===========================================================================

def _fires_assessment():
    """Reusable assessment that would fire TJ-001 with the canonical
    (theta=75, tjmax=150) fixture: TJ = 50 + 1.5*75 = 162.5 > 150."""
    return [{
        "ref": "U1", "value": "FAKE-REG", "ambient_c": 50.0,
        "pdiss_w": 1.5, "rtheta_ja_effective": 75.0,
        "tj_estimated_c": 162.5, "tj_max_c": 150.0,
    }]


def test_tj_001_stale_cache_still_fires(tmp_path):
    """Detector does NOT branch on facts.stale — TJ-001 fires identically
    whether the cache is fresh or stale. Per-detector half of the A3.3
    staleness ↔ trust-gating orthogonality lock."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    theta_sv = SpecValue(unit="C/W", evidence=ev, typ=75.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev, max=150.0)
    facts = _build_facts([theta_sv], [tjmax_sv])
    facts.stale = True

    with patch.object(lookup_detectors, "get_facts", return_value=facts):
        findings = lookup_detectors.detect_tj_exceeds_max(
            _fires_assessment(), source="thermal", cache_dir=tmp_path)

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert tj, "stale cache must NOT suppress TJ-001 — orthogonality lock"


def test_tj_001_low_confidence_theta_ja_no_finding(tmp_path):
    """Low-confidence theta_ja → best(min_confidence='medium') returns
    None → silent skip even when TJ would otherwise exceed TJmax. Locks
    the per-rule low-conf gate on the thermal-resistance side."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev_high = Evidence(page=2, confidence="high", method="table")
    ev_low = Evidence(page=2, confidence="low", method="prose")
    theta_sv = SpecValue(unit="C/W", evidence=ev_low, typ=75.0)  # low conf
    tjmax_sv = SpecValue(unit="C", evidence=ev_high, max=150.0)

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv])):
        findings = lookup_detectors.detect_tj_exceeds_max(
            _fires_assessment(), source="thermal", cache_dir=tmp_path)

    assert findings == [], (
        f"low-conf theta_ja must fail medium gate → silent skip, got {findings}"
    )


def test_tj_001_low_confidence_tj_max_no_finding(tmp_path):
    """Low-confidence TJmax → best(min_confidence='medium') returns None →
    silent skip even when TJ would otherwise exceed. Symmetric to the
    theta_ja low-conf test; both gates must independently work."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev_high = Evidence(page=2, confidence="high", method="table")
    ev_low = Evidence(page=2, confidence="low", method="prose")
    theta_sv = SpecValue(unit="C/W", evidence=ev_high, typ=75.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev_low, max=150.0)  # low conf

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv])):
        findings = lookup_detectors.detect_tj_exceeds_max(
            _fires_assessment(), source="thermal", cache_dir=tmp_path)

    assert findings == [], (
        f"low-conf TJmax must fail medium gate → silent skip, got {findings}"
    )


def test_tj_001_theta_typ_missing_falls_back_to_max(tmp_path):
    """When theta_sv.typ is None, detector falls back to theta_sv.max
    (worst-case). Locks the `theta = theta_sv.typ if theta_sv.typ is not
    None else theta_sv.max` line — a regression that lost the fallback
    would silently skip thermal checks on parts where only the max θJA
    was published."""
    from datasheet_types import SpecValue, Evidence
    import lookup_detectors

    ev = Evidence(page=2, confidence="high", method="table")
    # typ=None forces max fallback; max=75 produces same TJ as the fires test.
    theta_sv = SpecValue(unit="C/W", evidence=ev, typ=None, max=75.0)
    tjmax_sv = SpecValue(unit="C", evidence=ev, max=150.0)

    with patch.object(lookup_detectors, "get_facts",
                       return_value=_build_facts([theta_sv], [tjmax_sv])):
        findings = lookup_detectors.detect_tj_exceeds_max(
            _fires_assessment(), source="thermal", cache_dir=tmp_path)

    tj = [f for f in findings if f.get("rule_id") == "TJ-001"]
    assert tj, (
        "typ=None must fall back to max for theta_ja — got no finding, "
        "suggesting the fallback path is broken"
    )
    assert tj[0].get("theta_ja") == 75.0, (
        f"Expected theta_ja=75.0 from max fallback, got {tj[0].get('theta_ja')}"
    )
