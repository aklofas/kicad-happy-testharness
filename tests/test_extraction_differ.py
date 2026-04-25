"""Unit tests for regression/extraction_differ.py."""
TIER = "unit"

import json
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))


def test_numeric_within_5pct():
    from regression.extraction_differ import _numeric_within_tolerance
    assert _numeric_within_tolerance(100, 95)
    assert _numeric_within_tolerance(100, 105)
    assert _numeric_within_tolerance(100, 100)


def test_numeric_outside_5pct():
    from regression.extraction_differ import _numeric_within_tolerance
    # Just outside 5% AND >1 LSD (gold=100, LSD=1): 94, 106
    assert not _numeric_within_tolerance(100, 94)
    assert not _numeric_within_tolerance(100, 106)


def test_numeric_lsd_rescues_small_value():
    """For small values, ±1 LSD may be more permissive than ±5%."""
    from regression.extraction_differ import _numeric_within_tolerance
    assert _numeric_within_tolerance(1, 2)
    assert _numeric_within_tolerance(1, 0)
    assert not _numeric_within_tolerance(1, 3)


def test_numeric_lsd_with_decimals():
    from regression.extraction_differ import _numeric_within_tolerance
    assert _numeric_within_tolerance(1.23, 1.24)
    assert not _numeric_within_tolerance(1.23, 1.30)


def test_numeric_zero_requires_exact_zero():
    from regression.extraction_differ import _numeric_within_tolerance
    assert _numeric_within_tolerance(0, 0)
    assert not _numeric_within_tolerance(0, 0.01)


def test_numeric_negative_values():
    from regression.extraction_differ import _numeric_within_tolerance
    assert _numeric_within_tolerance(-40, -42)
    assert not _numeric_within_tolerance(-40, -43)


def test_compute_lsd_integer():
    from regression.extraction_differ import _compute_lsd
    assert _compute_lsd(100) == 1
    assert _compute_lsd(45) == 1
    assert _compute_lsd(0) == 1


def test_compute_lsd_decimal():
    from regression.extraction_differ import _compute_lsd
    assert abs(_compute_lsd(1.23) - 0.01) < 1e-9
    assert abs(_compute_lsd(45.0) - 0.1) < 1e-9
    assert abs(_compute_lsd(0.001) - 0.001) < 1e-9


def test_compute_lsd_scientific():
    from regression.extraction_differ import _compute_lsd
    assert abs(_compute_lsd(4.7e-4) - 1e-5) < 1e-12


def test_condition_normalize_whitespace():
    from regression.extraction_differ import _normalize_condition
    assert _normalize_condition("4.5  V <= VIN <=  40 V") == \
           _normalize_condition("4.5 V <= VIN <= 40 V")


def test_condition_normalize_unicode_mu():
    """µ (U+00B5) and μ (U+03BC) should both normalize to the same canonical form."""
    from regression.extraction_differ import _normalize_condition
    a = "470 \u00b5F"  # µ MICRO SIGN
    b = "470 \u03bcF"  # μ GREEK LETTER MU
    assert _normalize_condition(a) == _normalize_condition(b)


def test_condition_normalize_omega():
    """Ω (U+03A9 GREEK CAPITAL OMEGA) and Ω (U+2126 OHM SIGN) normalize equal."""
    from regression.extraction_differ import _normalize_condition
    a = "0.5 \u03a9"
    b = "0.5 \u2126"
    assert _normalize_condition(a) == _normalize_condition(b)


def test_condition_normalize_temp_notation():
    """25°C vs 25 C — degree sign optional in spec convention."""
    from regression.extraction_differ import _normalize_condition
    assert _normalize_condition("TJ = 25°C") == _normalize_condition("TJ = 25 C")
    assert _normalize_condition("TA = -40°C to 125°C") == \
           _normalize_condition("TA = -40 C to 125 C")


def test_condition_distinct_strings_stay_distinct():
    """Real semantic differences must not normalize away."""
    from regression.extraction_differ import _normalize_condition
    assert _normalize_condition("VIN = 5V") != _normalize_condition("VIN = 12V")
    assert _normalize_condition("ILOAD = 1A") != _normalize_condition("ILOAD = 3A")


def test_specvalue_identical_no_entries():
    from regression.extraction_differ import _diff_specvalue
    sv = {"min": None, "typ": 1.23, "max": None, "unit": "V",
          "condition": "TJ = 25°C", "notes": "Vref",
          "evidence": {"page": 5, "section": "EC", "confidence": "high",
                       "method": "table"}}
    entries = _diff_specvalue("regulator.reference_voltage[0]", sv, sv)
    assert entries == []


def test_specvalue_numeric_within_tolerance_silent():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.24, "unit": "V", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    assert all(e.severity is Severity.SILENT for e in entries), \
        [(e.path, e.severity, e.summary) for e in entries]


def test_specvalue_numeric_outside_tolerance_warning():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.50, "unit": "V", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    warnings = [e for e in entries if e.severity is Severity.WARNING]
    assert len(warnings) == 1
    assert "typ" in warnings[0].path


def test_specvalue_unit_mismatch_error():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "mV", "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    errors = [e for e in entries if e.severity is Severity.ERROR]
    assert len(errors) == 1
    assert "unit" in errors[0].path


def test_specvalue_condition_fuzzy_silent_when_equivalent():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "condition": "TJ = 25°C, ILOAD = 1 A",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "condition": "TJ = 25 C, ILOAD = 1 A",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    info_entries = [e for e in entries if e.severity is Severity.INFO]
    assert len(info_entries) == 0


def test_specvalue_condition_distinct_info():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "condition": "TJ = 25°C",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "condition": "TJ = -40°C",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    info_entries = [e for e in entries if e.severity is Severity.INFO]
    assert len(info_entries) == 1


def test_specvalue_evidence_page_within_tolerance_silent():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 6, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    page_entries = [e for e in entries if "page" in e.path]
    assert all(e.severity is Severity.SILENT for e in page_entries), \
        [(e.path, e.severity) for e in page_entries]


def test_specvalue_evidence_page_outside_tolerance_warning():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 10, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    warnings = [e for e in entries if e.severity is Severity.WARNING and "page" in e.path]
    assert len(warnings) == 1


def test_specvalue_confidence_downgrade_warning():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "low", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    warnings = [e for e in entries if e.severity is Severity.WARNING and "confidence" in e.path]
    assert len(warnings) == 1


def test_specvalue_confidence_upgrade_silent():
    """Per spec line 629: upgrades are fine."""
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "low", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    confidence_warnings = [e for e in entries
                           if e.severity is Severity.WARNING and "confidence" in e.path]
    assert len(confidence_warnings) == 0


def test_specvalue_method_mismatch_error():
    from regression.extraction_differ import _diff_specvalue, Severity
    gold = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V",
            "evidence": {"page": 5, "confidence": "high", "method": "prose"}}
    entries = _diff_specvalue("p", gold, cand)
    errors = [e for e in entries if e.severity is Severity.ERROR and "method" in e.path]
    assert len(errors) == 1


def test_specvalue_notes_not_diffed():
    """Spec line 626: notes are not diffed (advisory only)."""
    from regression.extraction_differ import _diff_specvalue
    gold = {"typ": 1.23, "unit": "V", "notes": "different note A",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    cand = {"typ": 1.23, "unit": "V", "notes": "different note B",
            "evidence": {"page": 5, "confidence": "high", "method": "table"}}
    entries = _diff_specvalue("p", gold, cand)
    notes_entries = [e for e in entries if "notes" in e.path]
    assert len(notes_entries) == 0


def test_diff_extractions_identical():
    from regression.extraction_differ import diff_extractions
    extraction = {
        "schema_version": {"base": "1.0"},
        "regulator": {
            "topology": "buck",
            "reference_voltage": [
                {"min": None, "typ": 1.23, "max": None, "unit": "V",
                 "condition": "TJ=25°C", "notes": "Vref",
                 "evidence": {"page": 5, "section": "EC",
                              "confidence": "high", "method": "table"}}
            ],
        },
    }
    report = diff_extractions(gold=extraction, candidate=extraction)
    non_silent = [e for e in report.entries
                  if e.severity.value != "silent"]
    assert len(non_silent) == 0, [(e.path, e.severity.value) for e in non_silent]
    assert report.gold_diff_score == 100
    assert not report.has_regression


def test_diff_extractions_topology_enum_mismatch_is_error():
    from regression.extraction_differ import diff_extractions, Severity
    gold = {"regulator": {"topology": "buck"}}
    cand = {"regulator": {"topology": "boost"}}
    report = diff_extractions(gold=gold, candidate=cand)
    errors = report.by_severity(Severity.ERROR)
    assert len(errors) == 1
    assert "topology" in errors[0].path
    assert report.has_regression


def test_diff_extractions_missing_field_is_error():
    from regression.extraction_differ import diff_extractions, Severity
    gold = {"regulator": {"topology": "buck", "vin_range": [
        {"max": 40, "unit": "V",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}}]}}
    cand = {"regulator": {"topology": "buck"}}
    report = diff_extractions(gold=gold, candidate=cand)
    errors = report.by_severity(Severity.ERROR)
    assert any("vin_range" in e.path for e in errors), \
        [e.path for e in errors]
    assert report.has_regression


def test_diff_extractions_added_field_is_error():
    """Per spec line 635: 'Added field not in schema: ERROR'."""
    from regression.extraction_differ import diff_extractions, Severity
    gold = {"regulator": {"topology": "buck"}}
    cand = {"regulator": {"topology": "buck", "extra_field": "something"}}
    report = diff_extractions(gold=gold, candidate=cand)
    errors = report.by_severity(Severity.ERROR)
    assert any("extra_field" in e.path for e in errors)
    assert report.has_regression


def test_diff_extractions_specvalue_list_index_aware():
    from regression.extraction_differ import diff_extractions
    gold = {"regulator": {"vin_range": [
        {"min": 4.5, "max": 40, "unit": "V",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}}]}}
    cand = {"regulator": {"vin_range": [
        {"min": 4.6, "max": 41, "unit": "V",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}}]}}
    report = diff_extractions(gold=gold, candidate=cand)
    # All numeric within 5% — score stays 100 (silent entries don't deduct)
    assert report.gold_diff_score == 100, \
        [(e.path, e.severity.value, e.summary) for e in report.entries
         if e.severity.value != "silent"]


def test_diff_extractions_specvalue_list_length_mismatch_is_error():
    from regression.extraction_differ import diff_extractions, Severity
    gold = {"base": {"thermal": {"theta_ja": [
        {"typ": 50, "unit": "°C/W",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}},
        {"typ": 30, "unit": "°C/W",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}},
    ]}}}
    cand = {"base": {"thermal": {"theta_ja": [
        {"typ": 50, "unit": "°C/W",
         "evidence": {"page": 5, "confidence": "high", "method": "table"}},
    ]}}}
    report = diff_extractions(gold=gold, candidate=cand)
    errors = report.by_severity(Severity.ERROR)
    assert any("theta_ja" in e.path and "length" in e.summary.lower()
               for e in errors), [e.path + ": " + e.summary for e in errors]


def test_render_text_report_includes_severity_groups():
    from regression.extraction_differ import (
        render_text_report, DiffEntry, DiffReport, Severity, Category,
    )
    report = DiffReport(entries=[
        DiffEntry(path="regulator.topology", category=Category.EXACT,
                  severity=Severity.ERROR,
                  summary="enum mismatch: 'buck' vs 'boost'"),
        DiffEntry(path="regulator.vref[0].typ", category=Category.NUMERIC,
                  severity=Severity.WARNING,
                  summary="1.23 vs 1.50 (Δ=21.95%)"),
        DiffEntry(path="base.thermal.theta_ja[0].condition",
                  category=Category.FUZZY, severity=Severity.INFO,
                  summary="condition divergence"),
    ])
    text = render_text_report(report)
    for marker in ("ERROR", "WARNING", "INFO", "Gold diff score",
                   "regulator.topology"):
        assert marker in text, f"missing {marker!r} in:\n{text}"


def test_compute_exit_code_no_regression():
    from regression.extraction_differ import compute_exit_code, DiffReport
    assert compute_exit_code(DiffReport()) == 0


def test_compute_exit_code_regression_on_error():
    from regression.extraction_differ import (
        compute_exit_code, DiffReport, DiffEntry, Severity, Category,
    )
    r = DiffReport(entries=[DiffEntry(
        path="x", category=Category.EXACT,
        severity=Severity.ERROR, summary="err")])
    assert compute_exit_code(r) == 1


def test_compute_exit_code_regression_on_score_drop():
    """3 WARNINGs → 15 pt deduction → score 85 → regression."""
    from regression.extraction_differ import (
        compute_exit_code, DiffReport, DiffEntry, Severity, Category,
    )
    r = DiffReport(entries=[
        DiffEntry(path=f"p{i}", category=Category.NUMERIC,
                  severity=Severity.WARNING, summary="w") for i in range(3)
    ])
    assert r.gold_diff_score == 85
    assert compute_exit_code(r) == 1


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
