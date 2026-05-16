"""Contract test: action/format-report.py renders v1.4 envelopes correctly.

Locks both EMC summary-rendering paths against the v1.4 ``summary.by_severity``
vocabulary while keeping the legacy v1.3.1 ``summary.critical/high/total_checks``
fallback alive. Closes the stale-key regression class that 693b664 only
partially fixed (compact-comment path patched, full-report path missed).

Cases:
  1. v1.4 EMC, full-report path  — must print real "N checks: E error, W warning"
  2. v1.4 EMC, compact PR-comment path  — locks 693b664's _summary_counts() fix
  3. legacy v1.3.1 EMC, full-report path — fallback maps critical→error, high→warning
  4. v1.4 thermal, full-report path — pin the thermal-side total_findings fallback
  5. format_report() summary JSON — has_critical=True when by_severity.error >= 1

Fixtures: real cached v1.4 corpus outputs (per
``feedback_real_fixtures_for_verification`` — synthetic envelopes encode
developer mental models that lag the actual producer schema and have already
cost one recheck cycle on this exact bug class).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

FORMAT_REPORT_PY = MAIN_REPO_ROOT / "action" / "format-report.py"
FIXTURES = HARNESS_ROOT / "tests" / "fixtures" / "action-format-report"
EMC_V14 = FIXTURES / "emc_v14_aslanpad_macropad.json"
THERMAL_V14 = FIXTURES / "thermal_v14_rpi_i2c_board.json"
# Thermal fixture WITH at least one error-severity finding — required for the
# B3 compact-path test (mirrors case 5's EMC has_critical assertion). The
# rpi_i2c_board fixture has only warning/info; ARIG-Robotique ControleursPompes
# has summary.by_severity.error == 1 (U1 above Tjmax).
THERMAL_V14_WITH_ERROR = FIXTURES / "thermal_v14_arig_controleurspompes_error.json"
# Required for the full-report EMC section: format_full_report() nests the EMC
# subsection inside ``if sig:``, so without a schematic (and a non-empty signal
# group) the EMC block is skipped entirely. AslanPad schematic comes from the
# same corpus project as EMC_V14, so the pair is naturally consistent.
SCHEMATIC_V14 = FIXTURES / "schematic_v14_aslanpad_macropad.json"


@pytest.fixture(scope="module")
def fmt_mod():
    """Load action/format-report.py via importlib (hyphenated filename can't
    be `import`-ed directly)."""
    spec = importlib.util.spec_from_file_location(
        "format_report_mod", FORMAT_REPORT_PY
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["format_report_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def emc_v14_envelope():
    return json.loads(EMC_V14.read_text())


@pytest.fixture(scope="module")
def thermal_v14_envelope():
    return json.loads(THERMAL_V14.read_text())


@pytest.fixture
def emc_legacy_envelope_path(tmp_path, emc_v14_envelope):
    """Derive a legacy v1.3.1 EMC envelope from the real v1.4 fixture via the
    documented schema migration (per ``_summary_counts()`` docstring):

        by_severity.error  → critical
        by_severity.warning → high
        total_findings      → total_checks

    Real data, deterministic transform — keeps the legacy fallback under test
    without committing a hand-rolled mental-model envelope that could lag the
    historic shape."""
    legacy = json.loads(json.dumps(emc_v14_envelope))
    s = legacy["summary"]
    by_sev = s.pop("by_severity")
    s["critical"] = by_sev["error"]
    s["high"] = by_sev["warning"]
    s["total_checks"] = s.pop("total_findings")
    path = tmp_path / "emc_legacy_v131.json"
    path.write_text(json.dumps(legacy))
    return path


# ----------------------------------------------------------------------------
# Case 1: v1.4 EMC, full-report path
# ----------------------------------------------------------------------------

def test_full_report_emc_v14_uses_real_counts(fmt_mod, emc_v14_envelope):
    """v1.4 EMC envelope: full-report EMC section must read by_severity +
    total_findings, NOT the stale legacy critical/high/total_checks keys.

    Regression: pre-fix, format_full_report() read summary.critical /
    summary.high / summary.total_checks directly at lines 1070-1078 and
    printed ``"0 checks: 0 critical, 0 high, 0 medium"`` for every v1.4
    envelope. See TODO-v1.4-regression-testing-audit.md Finding 1.
    """
    out = fmt_mod.format_full_report(
        schematic_path=str(SCHEMATIC_V14),
        pcb_path=None,
        spice_path=None,
        emc_path=str(EMC_V14),
        derating_profile="commercial",
        thermal_path=None,
    )
    s = emc_v14_envelope["summary"]
    err = s["by_severity"]["error"]
    warn = s["by_severity"]["warning"]
    total = s["total_findings"]
    # Sanity: the fixture must actually exercise both severities and >0 total
    # for this test to be meaningful.
    assert err >= 1 and warn >= 1 and total >= 2

    expected = f"{total} checks: {err} error, {warn} warning"
    assert expected in out, (
        f"Expected EMC section to contain {expected!r}.\n"
        f"Full report output:\n{out}"
    )
    # Regression string from the legacy four-key vocabulary must not appear.
    assert "0 checks: 0 critical" not in out
    assert " medium" not in out, "Legacy 'medium' vocabulary leaked into v1.4 output"


# ----------------------------------------------------------------------------
# Case 2: v1.4 EMC, compact PR-comment path (locks 693b664's fix)
# ----------------------------------------------------------------------------

def test_compact_report_emc_v14_uses_real_counts(fmt_mod, emc_v14_envelope):
    """v1.4 EMC envelope: compact PR-comment path must surface real error and
    warning counts via _summary_counts(). Locks 693b664 (format_report at
    line 502)."""
    report, _summary = fmt_mod.format_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=str(EMC_V14),
        severity="all",
        derating_profile="commercial",
    )
    s = emc_v14_envelope["summary"]
    err = s["by_severity"]["error"]
    warn = s["by_severity"]["warning"]

    assert f"EMC: {err} error-severity finding" in report, (
        f"Expected 'EMC: {err} error-severity finding' in compact report.\n"
        f"Report:\n{report}"
    )
    assert f"EMC: {warn} warning-severity finding" in report


# ----------------------------------------------------------------------------
# Case 3: legacy v1.3.1 EMC, full-report path (fallback alive)
# ----------------------------------------------------------------------------

def test_full_report_emc_legacy_v131_renders_via_fallback(
    fmt_mod, emc_v14_envelope, emc_legacy_envelope_path
):
    """Legacy v1.3.1 EMC envelope (summary.critical / high / total_checks, no
    by_severity, no total_findings) must still render through
    _summary_counts()'s fallback. Maps critical→error, high→warning."""
    out = fmt_mod.format_full_report(
        schematic_path=str(SCHEMATIC_V14),
        pcb_path=None,
        spice_path=None,
        emc_path=str(emc_legacy_envelope_path),
        derating_profile="commercial",
        thermal_path=None,
    )
    s = emc_v14_envelope["summary"]
    err = s["by_severity"]["error"]      # fallback source = summary.critical
    warn = s["by_severity"]["warning"]   # fallback source = summary.high
    total = s["total_findings"]          # fallback source = summary.total_checks

    expected = f"{total} checks: {err} error, {warn} warning"
    assert expected in out, (
        f"Expected legacy fallback to render {expected!r}.\n"
        f"Output:\n{out}"
    )


# ----------------------------------------------------------------------------
# Case 4: v1.4 thermal, full-report path
# ----------------------------------------------------------------------------

def test_full_report_thermal_v14_renders_total_findings(
    fmt_mod, thermal_v14_envelope
):
    """v1.4 thermal envelope: full-report thermal section reads total_findings
    via inline fallback at line 1303. Pin current behavior so the sibling
    renderer next to EMC stays in sync."""
    out = fmt_mod.format_full_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        derating_profile="commercial",
        thermal_path=str(THERMAL_V14),
    )
    s = thermal_v14_envelope["summary"]
    total = s["total_findings"]
    assert total >= 1, "Fixture must have >=1 thermal finding to render the section"

    # Level-agnostic — main-repo harmonized "### Thermal Analysis" → "##" in
    # the rc.2 bundle (sibling to EMC's promotion). Don't pin the heading rank.
    assert "Thermal Analysis" in out
    assert f"{total} checks" in out, (
        f"Expected '{total} checks' in thermal section.\nOutput:\n{out}"
    )


# ----------------------------------------------------------------------------
# Case 5: format_report() summary JSON has_critical
# ----------------------------------------------------------------------------

def test_format_report_summary_marks_has_critical_for_emc_errors(
    fmt_mod, emc_v14_envelope
):
    """Audit F2 case 1: with a v1.4 EMC envelope where summary.by_severity.error
    >= 1, format_report()'s returned summary_data must report has_critical=True
    and findings_count >= 1. Locks the Action-level public-output contract."""
    _report, summary = fmt_mod.format_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=str(EMC_V14),
        severity="all",
        derating_profile="commercial",
    )
    err = emc_v14_envelope["summary"]["by_severity"]["error"]
    assert err >= 1, "Fixture must have >=1 EMC error for this test"

    assert summary["has_critical"] is True, (
        f"Expected has_critical=True with {err} EMC error(s); got "
        f"summary={summary!r}"
    )
    assert summary["findings_count"] >= 1
    assert summary["has_emc"] is True


# ----------------------------------------------------------------------------
# Case 6: format_report() summary marks has_critical for THERMAL errors (B3)
# ----------------------------------------------------------------------------

def test_format_report_summary_marks_has_critical_for_thermal_errors(fmt_mod):
    """B3 (audit F1.2 second site): thermal by_severity.error must flow into
    has-critical / findings-count, mirroring the EMC fix at commit 693b664.

    Pre-fix the rich-Markdown thermal section ran AFTER critical_count /
    warning_count were computed, so a thermal-only error fixture rendered via
    the Action returned has_critical=False — silently downgrading thermal
    blockers to non-critical status in downstream CI gates and Slack alerts.

    Uses a real cached corpus thermal envelope (ARIG-Robotique
    ControleursPompes, U1 above Tjmax) — synthetic envelope would re-encode
    the developer mental model that hid this exact bug class on the EMC side.
    """
    thermal_env = json.loads(THERMAL_V14_WITH_ERROR.read_text())
    s = thermal_env["summary"]
    err = s["by_severity"]["error"]
    warn = s["by_severity"]["warning"]
    assert err >= 1, "Fixture must have >=1 thermal error for this test"

    report, summary = fmt_mod.format_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        severity="all",
        derating_profile="commercial",
        thermal_path=str(THERMAL_V14_WITH_ERROR),
    )

    assert summary["has_critical"] is True, (
        f"Expected has_critical=True with {err} thermal error(s); got "
        f"summary={summary!r}"
    )
    assert summary["findings_count"] >= 1
    # Compact PR-comment findings table must surface the thermal source.
    assert "Thermal:" in report, (
        f"Expected 'Thermal:' line in compact report findings table.\n"
        f"Report:\n{report}"
    )
    assert f"{err} error-severity finding" in report
    if warn >= 1:
        assert f"{warn} warning-severity finding" in report


# ----------------------------------------------------------------------------
# Case 7+8: schematic filename comes from inputs.source_files (F1.1)
# ----------------------------------------------------------------------------

@pytest.fixture
def schematic_v14_with_source_files_path(tmp_path):
    """v1.4 schematic envelope shape: top-level "file" removed,
    inputs.source_files populated. Built by transforming the cached
    AslanPad fixture (which still has the legacy top-level "file") so the
    test pins the v1.4 source_files path without committing a hand-rolled
    envelope. Falls under feedback_real_fixtures_for_verification — the
    statistics + other fields are real producer output, only the inputs
    shape is migrated forward.

    Returns (path, expected_basename)."""
    raw = json.loads(SCHEMATIC_V14.read_text())
    legacy_file = raw.pop("file", "v14_mainboard.kicad_sch")
    expected_name = Path(legacy_file).name
    raw["inputs"] = {
        "source_files": [legacy_file],
        "run_id": "test-source-files-run",
    }
    p = tmp_path / "schematic_v14_source_files.json"
    p.write_text(json.dumps(raw))
    return p, expected_name


def test_full_report_filename_from_inputs_source_files(
    fmt_mod, schematic_v14_with_source_files_path
):
    """Audit F1.1: v1.4 removed the top-level ``file`` field; full step summary
    must read schematic filename from ``inputs.source_files[0]`` instead.
    Pre-fix (rc.1 first cut) the report header rendered ``**unknown** —`` for
    every v1.4 envelope. The fix at 8daa28d adds the inputs-side read with a
    fallback to legacy ``file`` for cached v1.3.1 envelopes."""
    path, expected_name = schematic_v14_with_source_files_path
    out = fmt_mod.format_full_report(
        schematic_path=str(path),
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        derating_profile="commercial",
        thermal_path=None,
    )
    assert f"**{expected_name}** —" in out, (
        f"Expected '**{expected_name}** —' in full report header.\n"
        f"Output (first 2000 chars):\n{out[:2000]}"
    )
    assert "**unknown** —" not in out, (
        "Header rendered 'unknown' filename despite inputs.source_files being set"
    )


def test_compact_report_filename_from_inputs_source_files(
    fmt_mod, schematic_v14_with_source_files_path
):
    """Audit F1.1 (sibling site): compact PR-comment path has the same
    filename-read logic at line 349. Both sites must agree."""
    path, expected_name = schematic_v14_with_source_files_path
    report, _summary = fmt_mod.format_report(
        schematic_path=str(path),
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        severity="all",
        derating_profile="commercial",
    )
    assert f"**{expected_name}** —" in report, (
        f"Expected '**{expected_name}** —' in compact PR comment header.\n"
        f"Report:\n{report[:1500]}"
    )
    assert "**unknown** —" not in report


# ----------------------------------------------------------------------------
# Case 9: EMC warning-severity finding propagates to warning_count (F1.4)
# ----------------------------------------------------------------------------

def test_emc_warning_finding_propagates_to_warning_count(
    fmt_mod, emc_v14_envelope
):
    """Audit F1.4: format-report.py line 481 used to emit
    ``("WARNING", ...)`` (uppercase) when EMC reported high-severity findings.
    The downstream counter at line ~528 does ``s == "warning"`` (lowercase),
    so the typo silently zeroed warning_count for every EMC-only warning run.
    The fix lowercases the literal so the count actually increments.

    Lock: an EMC envelope with ``by_severity.warning >= 1`` must produce
    ``summary["warning_count"] >= 1`` and a "warning-severity finding(s)"
    line in the compact report.
    """
    warn = emc_v14_envelope["summary"]["by_severity"]["warning"]
    assert warn >= 1, "Fixture must have >=1 EMC warning for this test"

    report, summary = fmt_mod.format_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=str(EMC_V14),
        severity="all",
        derating_profile="commercial",
    )
    assert summary["warning_count"] >= 1, (
        f"Expected warning_count>=1 with {warn} EMC warning(s); got "
        f"summary={summary!r} — the uppercase 'WARNING' typo at format-report.py "
        f"line 481 may have regressed."
    )
    assert f"EMC: {warn} warning-severity finding" in report
    # findings_count = critical_count + warning_count, so the EMC warning
    # must show up there too.
    assert summary["findings_count"] >= 1


# ----------------------------------------------------------------------------
# Case 10: normalize_severity helper covers the legacy taxonomy
# ----------------------------------------------------------------------------

def test_normalize_severity_handles_legacy_uppercase_and_v14():
    """Audit F1: the ``normalize_severity`` helper landed in rc.1 polish to
    let consumers read ``finding["severity"]`` without caring whether the
    producer emits legacy uppercase (CRITICAL/HIGH/MEDIUM/LOW/INFO) or v1.4
    lowercase (error/warning/info). Lock the mapping so a producer-side rename
    can't silently break Action consumers downstream.

    Imports the helper from kicad-happy directly (resolved via _paths.py).
    """
    import sys
    main_repo_scripts = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
    inserted = False
    if str(main_repo_scripts) not in sys.path:
        sys.path.insert(0, str(main_repo_scripts))
        inserted = True
    try:
        from finding_schema import normalize_severity
    finally:
        if inserted:
            sys.path.remove(str(main_repo_scripts))

    # Legacy uppercase pre-v1.3 taxonomy
    assert normalize_severity("CRITICAL") == "error"
    assert normalize_severity("HIGH") == "error"
    assert normalize_severity("MEDIUM") == "warning"
    assert normalize_severity("LOW") == "info"
    assert normalize_severity("INFO") == "info"
    # Lowercase legacy variants
    assert normalize_severity("critical") == "error"
    assert normalize_severity("high") == "error"
    assert normalize_severity("medium") == "warning"
    assert normalize_severity("low") == "info"
    # v1.4 normalized vocabulary passes through
    assert normalize_severity("error") == "error"
    assert normalize_severity("warning") == "warning"
    assert normalize_severity("info") == "info"
    # Unknown / None / non-string defaults to "info" (per docstring)
    assert normalize_severity(None) == "info"
    assert normalize_severity("") == "info"
    assert normalize_severity(42) == "info"
    assert normalize_severity("garbage") == "info"
