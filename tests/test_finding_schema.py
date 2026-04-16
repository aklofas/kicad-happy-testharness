"""Unit tests for kicad-happy finding_schema.py contract."""

TIER = "unit"

import os
import sys
from pathlib import Path

# Harness root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# kicad-happy scripts directory
KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "kicad-happy"),
)
SCRIPTS_DIR = os.path.join(KICAD_HAPPY, "skills", "kicad", "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from finding_schema import (
    make_finding, make_provenance, compute_trust_summary,
    get_findings, group_findings,
    VALID_SEVERITIES, VALID_CONFIDENCES, VALID_EVIDENCE_SOURCES,
)

_REQUIRED = dict(detector="test_det", rule_id="T-001", category="test",
                 summary="test summary", description="test desc")


# === make_finding() ===

# 1. Rejects invalid severity
def test_make_finding_invalid_severity():
    try:
        make_finding(**_REQUIRED, severity="critical")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "severity" in str(e)


# 2. Rejects invalid confidence
def test_make_finding_invalid_confidence():
    try:
        make_finding(**_REQUIRED, confidence="high")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "confidence" in str(e)


# 3. Rejects invalid evidence_source
def test_make_finding_invalid_evidence():
    try:
        make_finding(**_REQUIRED, evidence_source="deterministic")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "evidence_source" in str(e)


# 4. Accepts all valid severity values
def test_make_finding_valid_severities():
    for sev in VALID_SEVERITIES:
        f = make_finding(**_REQUIRED, severity=sev)
        assert f["severity"] == sev


# 5. Accepts all valid confidence values
def test_make_finding_valid_confidences():
    for conf in VALID_CONFIDENCES:
        f = make_finding(**_REQUIRED, confidence=conf)
        assert f["confidence"] == conf


# 6. Accepts all valid evidence_source values
def test_make_finding_valid_evidence_sources():
    for ev in VALID_EVIDENCE_SOURCES:
        f = make_finding(**_REQUIRED, evidence_source=ev)
        assert f["evidence_source"] == ev


# 7. Extra kwargs merge into output
def test_make_finding_extra_kwargs():
    f = make_finding(**_REQUIRED, provenance={"evidence": "test"}, ratio=0.5)
    assert f["provenance"] == {"evidence": "test"}
    assert f["ratio"] == 0.5


# 8. Required fields present
def test_make_finding_required_fields():
    f = make_finding(**_REQUIRED)
    for key in ("detector", "rule_id", "category", "summary", "description",
                "severity", "confidence", "evidence_source", "components",
                "nets", "pins", "recommendation", "report_context"):
        assert key in f, f"Missing key: {key}"


# === make_provenance() ===

# 9. Rejects invalid confidence
def test_make_provenance_invalid_confidence():
    try:
        make_provenance("test_evidence", confidence="high")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "confidence" in str(e)


# 10. Accepts all valid confidences
def test_make_provenance_valid_confidences():
    for conf in VALID_CONFIDENCES:
        p = make_provenance("test_evidence", confidence=conf)
        assert p["confidence"] == conf


# 11. Returns dict with required keys
def test_make_provenance_required_keys():
    p = make_provenance("test_evidence")
    for key in ("evidence", "confidence", "claimed_components",
                "excluded_by", "suppressed_candidates"):
        assert key in p, f"Missing key: {key}"


# 12. Defaults
def test_make_provenance_defaults():
    p = make_provenance("test_evidence")
    assert p["confidence"] == "heuristic"
    assert p["claimed_components"] == []
    assert p["excluded_by"] == []
    assert p["suppressed_candidates"] == []


# === compute_trust_summary() ===

# 13. Empty findings -> high trust
def test_trust_summary_empty():
    ts = compute_trust_summary([])
    assert ts["total_findings"] == 0
    assert ts["trust_level"] == "high"
    # Empty findings: no denominator, so pct is None (nothing to measure)
    assert ts["provenance_coverage_pct"] is None
    assert all(v == 0 for v in ts["by_confidence"].values())


# 14. 100% deterministic -> high
def test_trust_summary_all_deterministic():
    findings = [{"confidence": "deterministic", "evidence_source": "topology"}] * 10
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "high"
    assert ts["by_confidence"]["deterministic"] == 10


# 15. 20% heuristic boundary -> high (<=20)
def test_trust_summary_20pct_heuristic_is_high():
    findings = ([{"confidence": "deterministic", "evidence_source": "topology"}] * 8 +
                [{"confidence": "heuristic", "evidence_source": "heuristic_rule"}] * 2)
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "high"


# 16. 21% heuristic -> mixed
def test_trust_summary_21pct_heuristic_is_mixed():
    # 21/100 = 21%
    findings = ([{"confidence": "deterministic", "evidence_source": "topology"}] * 79 +
                [{"confidence": "heuristic", "evidence_source": "heuristic_rule"}] * 21)
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "mixed"


# 17. 50% heuristic -> mixed (<=50)
def test_trust_summary_50pct_heuristic_is_mixed():
    findings = ([{"confidence": "deterministic", "evidence_source": "topology"}] * 5 +
                [{"confidence": "heuristic", "evidence_source": "heuristic_rule"}] * 5)
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "mixed"


# 18. 51% heuristic -> low
def test_trust_summary_51pct_heuristic_is_low():
    # 51/100
    findings = ([{"confidence": "deterministic", "evidence_source": "topology"}] * 49 +
                [{"confidence": "heuristic", "evidence_source": "heuristic_rule"}] * 51)
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "low"


# 19. Unknown confidence -> low
def test_trust_summary_unknown_confidence_is_low():
    findings = [{"confidence": "deterministic", "evidence_source": "topology"}] * 9 + \
               [{"evidence_source": "topology"}]  # no confidence field
    ts = compute_trust_summary(findings)
    assert ts["trust_level"] == "low"
    assert ts.get("unknown_confidence", 0) == 1


# 20. Provenance counting uses "provenance" key
def test_trust_summary_provenance_counting():
    findings = [
        {"confidence": "deterministic", "evidence_source": "topology",
         "provenance": {"evidence": "test"}},
        {"confidence": "deterministic", "evidence_source": "topology"},
    ]
    ts = compute_trust_summary(findings)
    assert ts["provenance_coverage_pct"] == 50.0


# 21. BOM coverage excludes power types
def test_trust_summary_bom_coverage():
    bom = [
        {"reference": "R1", "type": "resistor", "mpn": "RC0402", "datasheet": "http://x"},
        {"reference": "C1", "type": "capacitor", "mpn": "", "datasheet": ""},
        {"reference": "#PWR01", "type": "power_symbol", "mpn": "", "datasheet": ""},
        {"reference": "PWR_FLAG1", "type": "power_flag", "mpn": "", "datasheet": ""},
    ]
    ts = compute_trust_summary([], bom=bom)
    bc = ts.get("bom_coverage")
    assert bc is not None
    assert bc["total_components"] == 2  # excludes power_symbol + power_flag
    assert bc["with_mpn"] == 1
    assert bc["with_datasheet"] == 1
    assert bc["mpn_pct"] == 50.0
    assert bc["datasheet_pct"] == 50.0


# 22. BOM coverage absent when bom=None
def test_trust_summary_no_bom():
    ts = compute_trust_summary([])
    assert "bom_coverage" not in ts


# === get_findings() / group_findings() ===

# 23. Filters by detector
def test_get_findings_by_detector():
    data = {"findings": [
        {"detector": "det_a", "rule_id": "A-001"},
        {"detector": "det_b", "rule_id": "B-001"},
        {"detector": "det_a", "rule_id": "A-002"},
    ]}
    result = get_findings(data, detector="det_a")
    assert len(result) == 2
    assert all(f["detector"] == "det_a" for f in result)


# 24. Returns empty for nonexistent detector
def test_get_findings_nonexistent():
    data = {"findings": [{"detector": "det_a"}]}
    result = get_findings(data, detector="det_z")
    assert result == []


# 25. group_findings keys by detector
def test_group_findings_keys():
    data = {"findings": [
        {"detector": "det_a"},
        {"detector": "det_b"},
        {"detector": "det_a"},
    ]}
    groups = group_findings(data)
    assert set(groups.keys()) == {"det_a", "det_b"}
    assert len(groups["det_a"]) == 2
    assert len(groups["det_b"]) == 1


# 26. Empty findings
def test_group_findings_empty():
    groups = group_findings({"findings": []})
    assert groups == {}


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except (AssertionError, Exception) as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
