"""Unit tests for validate/validate_invariants.py — property-based invariant checker."""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_invariants import check_invariants

HARNESS_DIR = Path(__file__).resolve().parent.parent


def _clean_output():
    """Build a minimal valid schematic output with no violations."""
    return {
        "components": [
            {"reference": "R1", "type": "resistor"},
            {"reference": "R2", "type": "resistor"},
            {"reference": "C1", "type": "capacitor"},
        ],
        "statistics": {
            "total_components": 3,
            "component_types": {"resistor": 2, "capacitor": 1},
        },
        "findings": [
            {"detector": "detect_voltage_dividers", "ratio": 0.5},
            {"detector": "detect_rc_filters", "cutoff_hz": 159.15},
            {"detector": "detect_lc_filters", "resonant_hz": 7234.32},
            {"detector": "detect_crystal_circuits", "effective_load_pF": 14.0},
        ],
        "annotation_issues": {"duplicate_references": []},
    }


# 1. Clean output -> no violations
def test_clean_output_no_violations():
    data = _clean_output()
    violations = check_invariants(data, "test.json")
    assert violations == [], f"Expected no violations, got: {violations}"


# 2. Divider ratio > 1 -> violation
def test_divider_ratio_above_one():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_voltage_dividers"]
    data["findings"].append({"detector": "detect_voltage_dividers", "ratio": 1.5})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=1.5 >= 1" in violations[0][1]


# 3. Divider ratio = 0 -> violation
def test_divider_ratio_zero():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_voltage_dividers"]
    data["findings"].append({"detector": "detect_voltage_dividers", "ratio": 0})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=0 <= 0" in violations[0][1]


# 4. Divider ratio negative -> violation
def test_divider_ratio_negative():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_voltage_dividers"]
    data["findings"].append({"detector": "detect_voltage_dividers", "ratio": -0.3})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=-0.3 <= 0" in violations[0][1]


# 5. RC filter negative cutoff -> violation
def test_rc_filter_negative_cutoff():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_rc_filters"]
    data["findings"].append({"detector": "detect_rc_filters", "cutoff_hz": -100})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "cutoff_hz=-100 <= 0" in violations[0][1]


# 6. LC filter zero resonance -> violation
def test_lc_filter_zero_resonance():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_lc_filters"]
    data["findings"].append({"detector": "detect_lc_filters", "resonant_hz": 0})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "resonant_hz=0 <= 0" in violations[0][1]


# 7. Crystal negative load -> violation
def test_crystal_negative_load():
    data = _clean_output()
    data["findings"] = [f for f in data["findings"] if f.get("detector") != "detect_crystal_circuits"]
    data["findings"].append({"detector": "detect_crystal_circuits", "effective_load_pF": -5.0})
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "effective_load_pF=-5.0 <= 0" in violations[0][1]


# 8. Component types sum exceeds total -> violation
def test_component_types_exceed_total():
    data = _clean_output()
    data["statistics"]["total_components"] = 2
    data["statistics"]["component_types"] = {"resistor": 2, "capacitor": 1}
    violations = check_invariants(data, "test.json")
    assert any("component_types sum (3) > total_components (2)" in v[1] for v in violations)


# 9. Duplicate refs flagged
def test_duplicate_refs_flagged():
    data = _clean_output()
    data["components"] = [
        {"reference": "R1", "type": "resistor"},
        {"reference": "R1", "type": "resistor"},
        {"reference": "R2", "type": "resistor"},
    ]
    data["annotation_issues"] = {"duplicate_references": []}
    violations = check_invariants(data, "test.json")
    assert any("duplicate ref 'R1'" in v[1] for v in violations), \
        f"Expected duplicate ref violation, got: {violations}"


# 10. Duplicate refs ignored if in annotation_issues
def test_duplicate_refs_ignored_when_known():
    data = _clean_output()
    data["components"] = [
        {"reference": "R1", "type": "resistor"},
        {"reference": "R1", "type": "resistor"},
        {"reference": "R2", "type": "resistor"},
    ]
    data["annotation_issues"] = {"duplicate_references": ["R1"]}
    violations = check_invariants(data, "test.json")
    # R1 is in annotation_issues, so it should not be flagged
    dupe_violations = [v for v in violations if "duplicate ref" in v[1]]
    assert dupe_violations == [], \
        f"Expected no duplicate violations, got: {dupe_violations}"


# 11. Null values skipped gracefully
def test_null_values_skipped():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": None},
        {"detector": "detect_rc_filters", "cutoff_hz": None},
        {"detector": "detect_lc_filters", "resonant_hz": None},
        {"detector": "detect_crystal_circuits", "effective_load_pF": None},
    ]
    violations = check_invariants(data, "test.json")
    assert violations == [], f"Expected no violations for null values, got: {violations}"


# 12. total_components < len(components) -> violation
def test_total_components_less_than_list():
    data = _clean_output()
    data["statistics"]["total_components"] = 1  # but 3 components in list
    violations = check_invariants(data, "test.json")
    assert any("len(components)=3 > total_components=1" in v[1] for v in violations)


# 13. total_components >= len(components) -> no violation
def test_total_components_gte_list():
    data = _clean_output()
    data["statistics"]["total_components"] = 5  # >= 3 components in list
    violations = check_invariants(data, "test.json")
    assert not any("len(components)" in v[1] for v in violations)


# 14. Net in findings not in nets -> violation
def test_signal_net_not_in_nets():
    data = _clean_output()
    data["nets"] = {"GND": {"name": "GND", "pins": []}, "VCC": {"name": "VCC", "pins": []}}
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "top_net": "VCC", "mid_net": "MISSING_NET", "bottom_net": "GND"}
    ]
    violations = check_invariants(data, "test.json")
    assert any("MISSING_NET" in v[1] and "not in nets" in v[1] for v in violations)


# 15. All findings nets present -> no violation
def test_signal_nets_all_present():
    data = _clean_output()
    data["nets"] = {"GND": {"name": "GND", "pins": []}, "VCC": {"name": "VCC", "pins": []},
                    "MID": {"name": "MID", "pins": []}}
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "top_net": "VCC", "mid_net": "MID", "bottom_net": "GND"}
    ]
    violations = check_invariants(data, "test.json")
    assert not any("not in nets" in v[1] for v in violations)


# 16. Empty nets dict skips net cross-check
def test_empty_nets_skips_cross_check():
    data = _clean_output()
    data["nets"] = {}
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "top_net": "VCC", "mid_net": "MID", "bottom_net": "GND"}
    ]
    violations = check_invariants(data, "test.json")
    assert not any("not in nets" in v[1] for v in violations)


# 17. Confidence taxonomy — valid values pass
def test_confidence_valid_values():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "confidence": "deterministic"},
        {"detector": "detect_rc_filters", "cutoff_hz": 159.0, "confidence": "heuristic"},
        {"detector": "detect_lc_filters", "resonant_hz": 7234.0, "confidence": "datasheet-backed"},
    ]
    violations = check_invariants(data, "test.json")
    assert not any("confidence" in v[1] for v in violations)


# 18. Confidence taxonomy — invalid value flagged
def test_confidence_invalid_value():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "confidence": "high"},
    ]
    violations = check_invariants(data, "test.json")
    assert any("confidence='high'" in v[1] for v in violations)


# 19. Confidence taxonomy — absent confidence is OK
def test_confidence_absent_ok():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_suggested_certifications"},
    ]
    violations = check_invariants(data, "test.json")
    assert not any("confidence" in v[1] for v in violations)


# 20. Provenance — valid structure passes
def test_provenance_valid():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "confidence": "deterministic",
         "provenance": {"evidence": "vd_two_resistor", "confidence": "deterministic",
                        "claimed_components": ["R1", "R2"], "excluded_by": [],
                        "suppressed_candidates": []}},
    ]
    violations = check_invariants(data, "test.json")
    assert not any("provenance" in v[1] for v in violations)


# 21. Provenance — missing required field flagged
def test_provenance_missing_field():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "confidence": "deterministic",
         "provenance": {"evidence": "vd_two_resistor", "confidence": "deterministic"}},
    ]
    violations = check_invariants(data, "test.json")
    assert any("missing 'claimed_components'" in v[1] for v in violations)


# 22. Provenance — invalid confidence flagged
def test_provenance_invalid_confidence():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "confidence": "deterministic",
         "provenance": {"evidence": "vd_test", "confidence": "high",
                        "claimed_components": [], "excluded_by": [],
                        "suppressed_candidates": []}},
    ]
    violations = check_invariants(data, "test.json")
    assert any("provenance.confidence='high'" in v[1] for v in violations)


# 23. Provenance absent is OK (not all detectors have it yet)
def test_provenance_absent_ok():
    data = _clean_output()
    violations = check_invariants(data, "test.json")
    assert not any("provenance" in v[1] for v in violations)


# 24. Evidence source taxonomy — valid values pass
def test_evidence_source_valid_values():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "evidence_source": "topology"},
        {"detector": "detect_rc_filters", "cutoff_hz": 159.0, "evidence_source": "heuristic_rule"},
        {"detector": "detect_lc_filters", "resonant_hz": 7234.0, "evidence_source": "datasheet"},
    ]
    violations = check_invariants(data, "test.json")
    assert not any("evidence_source" in v[1] for v in violations)


# 25. Evidence source taxonomy — invalid value flagged
def test_evidence_source_invalid_value():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_voltage_dividers", "ratio": 0.5, "evidence_source": "package_table"},
    ]
    violations = check_invariants(data, "test.json")
    assert any("evidence_source='package_table'" in v[1] for v in violations)


# 26. Evidence source taxonomy — absent evidence_source is OK
def test_evidence_source_absent_ok():
    data = _clean_output()
    data["findings"] = [
        {"detector": "detect_suggested_certifications"},
    ]
    violations = check_invariants(data, "test.json")
    assert not any("evidence_source" in v[1] for v in violations)


# 27. Evidence source taxonomy — all valid enum values accepted
def test_evidence_source_all_valid_enums():
    data = _clean_output()
    data["findings"] = [
        {"detector": "test", "evidence_source": src}
        for src in ("datasheet", "topology", "heuristic_rule",
                    "symbol_footprint", "bom", "geometry", "api_lookup")
    ]
    violations = check_invariants(data, "test.json")
    assert not any("evidence_source" in v[1] for v in violations)


# 28. trust_summary — valid structure passes
def test_trust_summary_valid():
    data = _clean_output()
    # 4 findings, 2 heuristic → trust_level=mixed (20% < heu=50% <= 50%)
    # 0 findings have provenance key → provenance_coverage_pct=0.0
    data["trust_summary"] = {
        "total_findings": 4,
        "trust_level": "mixed",
        "by_confidence": {"deterministic": 2, "heuristic": 2, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 1, "topology": 1, "heuristic_rule": 2,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert not any("trust_summary" in v[1] for v in violations)


# 29. trust_summary — total_findings mismatch flagged
def test_trust_summary_total_mismatch():
    data = _clean_output()
    data["trust_summary"] = {
        "total_findings": 99,
        "trust_level": "high",
        "by_confidence": {"deterministic": 99, "heuristic": 0, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 99,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert any("total_findings=99" in v[1] and "len(findings)=4" in v[1] for v in violations)


# 30. trust_summary — invalid trust_level flagged
def test_trust_summary_invalid_trust_level():
    data = _clean_output()
    data["trust_summary"] = {
        "total_findings": 4,
        "trust_level": "medium",
        "by_confidence": {"deterministic": 4, "heuristic": 0, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 4,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert any("trust_level='medium'" in v[1] for v in violations)


# 31. trust_summary — by_confidence sum mismatch flagged
def test_trust_summary_confidence_sum_mismatch():
    data = _clean_output()
    data["trust_summary"] = {
        "total_findings": 4,
        "trust_level": "high",
        "by_confidence": {"deterministic": 1, "heuristic": 0, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 4,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert any("by_confidence sum (1)" in v[1] for v in violations)


# 32. trust_summary — absent is OK (backward compat)
def test_trust_summary_absent_ok():
    data = _clean_output()
    violations = check_invariants(data, "test.json")
    assert not any("trust_summary" in v[1] for v in violations)


# 33. trust_summary — bom_coverage pct out of range flagged
def test_trust_summary_bom_coverage_invalid_pct():
    data = _clean_output()
    data["trust_summary"] = {
        "total_findings": 4,
        "trust_level": "low",
        "by_confidence": {"deterministic": 0, "heuristic": 4, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 4,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
        "bom_coverage": {"total_components": 10, "with_mpn": 5, "with_datasheet": 3,
                         "mpn_pct": 150.0, "datasheet_pct": 30.0},
    }
    violations = check_invariants(data, "test.json")
    assert any("mpn_pct=150.0" in v[1] for v in violations)


# 34. trust_level threshold — high correct
def test_trust_level_threshold_high():
    data = _clean_output()
    data["findings"] = [{"detector": "test", "confidence": "deterministic"}] * 8 + \
                       [{"detector": "test", "confidence": "heuristic"}] * 2
    data["trust_summary"] = {
        "total_findings": 10,
        "trust_level": "high",
        "by_confidence": {"deterministic": 8, "heuristic": 2, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 10,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert not any("trust_level" in v[1] and "expected" in v[1] for v in violations)


# 35. trust_level threshold — should be mixed but says high
def test_trust_level_threshold_wrong():
    data = _clean_output()
    data["findings"] = [{"detector": "test", "confidence": "deterministic"}] * 7 + \
                       [{"detector": "test", "confidence": "heuristic"}] * 3
    data["trust_summary"] = {
        "total_findings": 10,
        "trust_level": "high",  # wrong: 30% heuristic should be mixed
        "by_confidence": {"deterministic": 7, "heuristic": 3, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 10,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
    }
    violations = check_invariants(data, "test.json")
    assert any("expected 'mixed'" in v[1] for v in violations)


# 36. provenance_coverage_pct cross-check — mismatch
def test_provenance_pct_cross_check():
    data = _clean_output()
    data["findings"] = [
        {"detector": "test", "confidence": "deterministic", "provenance": {"evidence": "test"}},
        {"detector": "test", "confidence": "deterministic"},
    ]
    data["trust_summary"] = {
        "total_findings": 2,
        "trust_level": "high",
        "by_confidence": {"deterministic": 2, "heuristic": 0, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 2,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,  # wrong: should be 50.0
    }
    violations = check_invariants(data, "test.json")
    assert any("provenance_coverage_pct" in v[1] and "actual=50.0%" in v[1] for v in violations)


# 37. BOM coverage cross-check — total_components mismatch
def test_bom_coverage_total_mismatch():
    data = _clean_output()
    data["bom"] = [
        {"reference": "R1", "type": "resistor"},
        {"reference": "C1", "type": "capacitor"},
        {"reference": "#PWR01", "type": "power_symbol"},
    ]
    data["trust_summary"] = {
        "total_findings": 4,
        "trust_level": "high",
        "by_confidence": {"deterministic": 4, "heuristic": 0, "datasheet-backed": 0},
        "by_evidence_source": {"datasheet": 0, "topology": 0, "heuristic_rule": 4,
                               "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
        "provenance_coverage_pct": 0.0,
        "bom_coverage": {"total_components": 5, "with_mpn": 0, "with_datasheet": 0,
                         "mpn_pct": 0.0, "datasheet_pct": 0.0},
    }
    violations = check_invariants(data, "test.json")
    assert any("bom_coverage.total_components=5" in v[1] and "actual=2" in v[1] for v in violations)


# 38. Corpus spot-check (run on a real output)
def test_corpus_spot_check():
    # Use known real outputs that should have valid invariants.
    # Only check modern (.kicad_sch) outputs — legacy .sch files
    # may have total_components vs component-list mismatches from
    # multi-unit symbol handling differences.
    output_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
    if not output_dir.exists():
        return  # Skip if no outputs available

    checked = 0
    clean = 0
    for repo_dir in sorted(output_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        for sub in sorted(repo_dir.rglob("*.json")):
            if ".sch.json" in sub.name and ".kicad_sch" not in sub.name:
                continue  # skip legacy
            try:
                with open(sub) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            findings = data.get("findings", [])
            has_vd = any(f.get("detector") == "detect_voltage_dividers" for f in findings)
            has_rc = any(f.get("detector") == "detect_rc_filters" for f in findings)
            if has_vd or has_rc:
                violations = check_invariants(data, str(sub))
                checked += 1
                if not violations:
                    clean += 1
                if clean >= 5:
                    return  # found 5 clean files — engine works
        if clean >= 5:
            return

    # The test proves the engine runs and finds clean files.
    # Violations in specific corpus files are expected (filed as KH-* issues).
    assert clean > 0 or not any(output_dir.iterdir()), \
        "No clean outputs found for spot-check"


# 39. trust_summary works on cross_analysis-style output (Phase 1 addition)
def test_trust_summary_cross_analysis():
    data = {
        "analyzer_type": "cross_analysis",
        "schema_version": "1.3.0",
        "findings": [
            {"detector": "sch_pcb_ref_count", "confidence": "deterministic",
             "evidence_source": "topology"},
        ],
        "trust_summary": {
            "total_findings": 1,
            "trust_level": "high",
            "by_confidence": {"deterministic": 1, "heuristic": 0, "datasheet-backed": 0},
            "by_evidence_source": {"datasheet": 0, "topology": 1, "heuristic_rule": 0,
                                   "symbol_footprint": 0, "bom": 0, "geometry": 0, "api_lookup": 0},
            "provenance_coverage_pct": 0.0,
        },
        "elapsed_s": 0.5,
    }
    violations = check_invariants(data, "test.json")
    assert not any("trust_summary" in v[1] for v in violations)
    assert not any("schema_version" in v[1] for v in violations)


# 40. schema_version — valid semver passes
def test_schema_version_valid():
    data = _clean_output()
    data["schema_version"] = "1.3.0"
    violations = check_invariants(data, "test.json")
    assert not any("schema_version" in v[1] for v in violations)


# 40. schema_version — invalid string flagged
def test_schema_version_invalid():
    data = _clean_output()
    data["schema_version"] = "1.3"
    violations = check_invariants(data, "test.json")
    assert any("schema_version='1.3'" in v[1] for v in violations)


# 41. schema_version — non-string flagged
def test_schema_version_non_string():
    data = _clean_output()
    data["schema_version"] = 1.3
    violations = check_invariants(data, "test.json")
    assert any("schema_version is float" in v[1] for v in violations)


# 42. schema_version — absent is OK (backward compat)
def test_schema_version_absent_ok():
    data = _clean_output()
    violations = check_invariants(data, "test.json")
    assert not any("schema_version" in v[1] for v in violations)


# 43. by_severity — valid {error, warning, info} passes
def test_by_severity_valid():
    data = _clean_output()
    data["summary"] = {"total_findings": 10, "by_severity": {"error": 3, "warning": 5, "info": 2}}
    violations = check_invariants(data, "test.json")
    assert not any("by_severity" in v[1] for v in violations)


# 44. by_severity — wrong keys flagged
def test_by_severity_wrong_keys():
    data = _clean_output()
    data["summary"] = {"total_findings": 5, "by_severity": {"critical": 1, "high": 2, "medium": 2}}
    violations = check_invariants(data, "test.json")
    assert any("by_severity keys" in v[1] for v in violations)


# 45. by_severity — sum mismatch flagged
def test_by_severity_sum_mismatch():
    data = _clean_output()
    data["summary"] = {"total_findings": 10, "by_severity": {"error": 1, "warning": 1, "info": 1}}
    violations = check_invariants(data, "test.json")
    assert any("by_severity sum (3)" in v[1] and "total_findings (10)" in v[1] for v in violations)


# 46. by_severity — absent is OK (pre-Phase-4 outputs)
def test_by_severity_absent_ok():
    data = _clean_output()
    data["summary"] = {"total_findings": 5}
    violations = check_invariants(data, "test.json")
    assert not any("by_severity" in v[1] for v in violations)


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
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
