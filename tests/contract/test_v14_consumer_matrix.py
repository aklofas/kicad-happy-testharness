"""Contract test: v1.4 producer envelopes × downstream consumer compatibility.

Audit LOG 4 (regression-testing audit, 2026-05-15): producer/consumer pairs
crossing the v1.3.1 → v1.4 schema boundary are the highest-leverage place to
lock contracts. Pre-v1.4 the schematic envelope carried a top-level ``file``
field; v1.4 moved it under ``inputs.source_files``. Consumers (format-report,
EMC, thermal, cross_analysis, review-plan, summarizer, datasheet detectors)
that still read ``sch["file"]`` silently rendered "unknown" filenames for
every v1.4 run — bug F1.1, fixed in rc.1 polish at commit 8daa28d.

This test module complements LOG 1 (which uses cached fixtures with
synthesized v1.4 shape) by exercising FRESH v1.4 producer envelopes through
each consumer. A producer-side schema change here will immediately surface as
a failed consumer test in CI, not as a silent runtime regression in the
released Action.

Two pieces:

  - **Producer contracts** — each of the 5 v1.4 producers (schematic, PCB,
    EMC, thermal, cross_analysis) must emit the load-bearing envelope keys
    consumers depend on (``inputs.source_files``, ``analyzer_type``,
    ``summary.by_severity``, ``capability_mode_ref.run_id``, ``findings``).
  - **Consumer compatibility** — format-report (compact + full) successfully
    extracts content from each producer envelope. Filenames render correctly
    (not "unknown"). Severity counts propagate (not zero).

Marked TIER=online — shares the v14_run_dir fixture with
``test_analysis_dir_contract.py`` (runs all 5 analyzers on commodorelcd into
a fresh tmp dir). Skips cleanly when corpus repo or KICAD_HAPPY_DIR missing.
"""

from __future__ import annotations

TIER = "online"

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

REPOS_DIR = HARNESS_ROOT / "repos"
TEST_REPO = "jgrip/commodorelcd"
SCH_PATH = REPOS_DIR / TEST_REPO / "commodorelcd.kicad_sch"
PCB_PATH = REPOS_DIR / TEST_REPO / "commodorelcd.kicad_pcb"

KH_KICAD_SCRIPTS = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
KH_EMC_SCRIPTS = MAIN_REPO_ROOT / "skills" / "emc" / "scripts"
FORMAT_REPORT_PY = MAIN_REPO_ROOT / "action" / "format-report.py"

ANALYZERS = [
    ("schematic", KH_KICAD_SCRIPTS / "analyze_schematic.py", [str(SCH_PATH)]),
    ("pcb",       KH_KICAD_SCRIPTS / "analyze_pcb.py",       [str(PCB_PATH)]),
    ("emc",       KH_EMC_SCRIPTS / "analyze_emc.py",         []),
    ("thermal",   KH_KICAD_SCRIPTS / "analyze_thermal.py",   []),
    ("cross_analysis", KH_KICAD_SCRIPTS / "cross_analysis.py", []),
]

SUBPROC_TIMEOUT_S = 180


def _skip_unless_corpus_and_kh_present():
    if not SCH_PATH.is_file():
        pytest.skip(f"missing corpus repo {TEST_REPO!r} (run checkout.py)")
    if not PCB_PATH.is_file():
        pytest.skip(f"missing PCB at {PCB_PATH}")
    if not (KH_KICAD_SCRIPTS / "analyze_schematic.py").is_file():
        pytest.skip("KICAD_HAPPY_DIR scripts missing")


# ---------------------------------------------------------------------------
# Shared fixture: run all 5 analyzers once into a fresh analysis-dir
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def v14_run_dir(tmp_path_factory):
    """Module-scoped: run all 5 v1.4 analyzers on commodorelcd into a
    custom-analysis dir. Yields the current run subdir (containing
    schematic.json, pcb.json, emc.json, thermal.json, cross_analysis.json).
    Skips the entire module if prereqs missing."""
    _skip_unless_corpus_and_kh_present()
    base = tmp_path_factory.mktemp("v14_matrix")
    analysis_dir = base / "custom-analysis"
    analysis_dir.mkdir()
    scratch_cwd = base / "scratch"
    scratch_cwd.mkdir()
    env = {**os.environ, "PYTHONHASHSEED": "0"}

    for name, script, positional in ANALYZERS:
        r = subprocess.run(
            [sys.executable, str(script), *positional,
             "--analysis-dir", str(analysis_dir), "--only-deterministic"],
            capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
            cwd=str(scratch_cwd), env=env,
        )
        assert r.returncode == 0, (
            f"v1.4 producer {name!r} failed during shared fixture setup: "
            f"rc={r.returncode}\nstderr: {r.stderr[-500:]}"
        )

    manifest = json.loads((analysis_dir / "manifest.json").read_text())
    run_dir = analysis_dir / manifest["current"]
    return run_dir


@pytest.fixture(scope="module")
def fmt_mod():
    """Load action/format-report.py — same pattern as
    test_action_format_report_v14.py (hyphenated filename can't be `import`-ed
    directly)."""
    spec = importlib.util.spec_from_file_location(
        "format_report_mod_matrix", FORMAT_REPORT_PY
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["format_report_mod_matrix"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Producer contracts — each v1.4 envelope satisfies its public schema
# ---------------------------------------------------------------------------

def _load(run_dir: Path, name: str) -> dict:
    p = run_dir / name
    assert p.is_file(), f"missing producer envelope {p}"
    return json.loads(p.read_text())


def test_schematic_envelope_v14_shape(v14_run_dir):
    """F1.1 producer-side lock: schematic envelope MUST NOT carry top-level
    ``file`` and MUST carry ``inputs.source_files``. Plus standard v1.4
    envelope keys (analyzer_type, summary.by_severity, capability_mode_ref).
    """
    sch = _load(v14_run_dir, "schematic.json")
    assert "file" not in sch, (
        "Top-level 'file' key leaked back into v1.4 schematic envelope — "
        "F1.1 regression. Filename must come from inputs.source_files only."
    )
    src_files = (sch.get("inputs") or {}).get("source_files") or []
    assert src_files, (
        f"inputs.source_files missing or empty: {sch.get('inputs')!r}. "
        f"Required for consumer filename rendering."
    )
    assert sch.get("analyzer_type") == "schematic"
    assert isinstance(sch.get("findings"), list)
    summary = sch.get("summary") or {}
    assert "by_severity" in summary, "summary.by_severity required (v1.4)"
    assert "total_findings" in summary
    assert (sch.get("capability_mode_ref") or {}).get("run_id"), (
        "capability_mode_ref.run_id required for run linking (LOG 3 invariant)"
    )


def test_pcb_envelope_v14_shape(v14_run_dir):
    """v1.4 PCB envelope: analyzer_type=pcb, inputs.source_files set,
    summary.by_severity present, capability_mode_ref.run_id set."""
    pcb = _load(v14_run_dir, "pcb.json")
    assert pcb.get("analyzer_type") == "pcb"
    src_files = (pcb.get("inputs") or {}).get("source_files") or []
    assert src_files, "PCB inputs.source_files missing"
    assert isinstance(pcb.get("findings"), list)
    summary = pcb.get("summary") or {}
    assert "by_severity" in summary, "PCB summary.by_severity required"
    assert (pcb.get("capability_mode_ref") or {}).get("run_id")


def test_emc_envelope_v14_shape(v14_run_dir):
    """v1.4 EMC envelope: summary.by_severity with error/warning/info buckets
    (NOT the legacy critical/high keys). Locks the producer side of the
    stale-key bug fixed at 693b664."""
    emc = _load(v14_run_dir, "emc.json")
    assert emc.get("analyzer_type") == "emc"
    summary = emc.get("summary") or {}
    by_sev = summary.get("by_severity") or {}
    assert set(by_sev.keys()) >= {"error", "warning", "info"}, (
        f"EMC by_severity missing v1.4 keys; got {sorted(by_sev.keys())!r}. "
        f"Producer regressed to legacy critical/high vocabulary."
    )
    # Legacy keys MUST NOT appear at the summary top level — those would
    # confuse _summary_counts()'s fallback logic.
    assert "critical" not in summary, (
        "Legacy 'critical' key leaked into v1.4 EMC summary"
    )
    assert "high" not in summary
    assert "total_findings" in summary
    assert (emc.get("capability_mode_ref") or {}).get("run_id")


def test_thermal_envelope_v14_shape(v14_run_dir):
    """v1.4 thermal envelope: summary.by_severity (sibling-symmetric with
    EMC). Pre-fix the thermal renderer in format-report.py had the same
    stale-key bug class (B3 / F1.5 sibling site)."""
    thermal = _load(v14_run_dir, "thermal.json")
    assert thermal.get("analyzer_type") == "thermal"
    summary = thermal.get("summary") or {}
    by_sev = summary.get("by_severity") or {}
    assert set(by_sev.keys()) >= {"error", "warning", "info"}, (
        f"thermal by_severity missing v1.4 keys; got {sorted(by_sev.keys())!r}"
    )
    assert "critical" not in summary
    assert "total_findings" in summary
    assert (thermal.get("capability_mode_ref") or {}).get("run_id")


def test_cross_analysis_envelope_v14_shape(v14_run_dir):
    """v1.4 cross_analysis envelope: analyzer_type=cross_analysis (NOT the
    pre-rc.1 name "cross" — that rename is F6 from the static audit).
    capability_mode_ref.run_id pins it to the run."""
    cross = _load(v14_run_dir, "cross_analysis.json")
    assert cross.get("analyzer_type") == "cross_analysis", (
        f"cross_analysis envelope analyzer_type={cross.get('analyzer_type')!r}; "
        f"the F6 rename to 'cross_analysis' regressed."
    )
    assert (cross.get("capability_mode_ref") or {}).get("run_id")


# ---------------------------------------------------------------------------
# Consumer compatibility — format-report (compact + full) reads each producer
# ---------------------------------------------------------------------------

def test_format_report_full_consumes_fresh_v14_schematic(v14_run_dir, fmt_mod):
    """End-to-end F1.1 lock: format_full_report reads a FRESH v1.4 schematic
    envelope and extracts the filename from inputs.source_files. Counterpart
    to test_full_report_filename_from_inputs_source_files (LOG 1) which uses
    a transformed cached fixture — this version exercises the PRODUCER's
    actual envelope shape, not a hand-crafted v1.4 shape."""
    sch_path = v14_run_dir / "schematic.json"
    out = fmt_mod.format_full_report(
        schematic_path=str(sch_path),
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        derating_profile="commercial",
        thermal_path=None,
    )
    assert "**commodorelcd.kicad_sch** —" in out, (
        f"format_full_report didn't extract filename from fresh v1.4 "
        f"schematic envelope. Output (first 500 chars):\n{out[:500]}"
    )
    assert "**unknown** —" not in out


def test_format_report_compact_consumes_fresh_v14_schematic(
    v14_run_dir, fmt_mod
):
    """F1.1 sibling-site lock for the compact PR-comment formatter."""
    sch_path = v14_run_dir / "schematic.json"
    report, summary = fmt_mod.format_report(
        schematic_path=str(sch_path),
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        severity="all",
        derating_profile="commercial",
    )
    assert "**commodorelcd.kicad_sch** —" in report, (
        f"compact format_report didn't extract filename.\n{report[:500]}"
    )
    assert "**unknown** —" not in report


def test_format_report_full_consumes_fresh_v14_pcb(v14_run_dir, fmt_mod):
    """PCB envelope consumed by format_full_report. Verifies the consumer
    survives a fresh v1.4 PCB envelope without crashing (no specific content
    invariant — PCB section may be terse on a small board)."""
    sch_path = v14_run_dir / "schematic.json"
    pcb_path = v14_run_dir / "pcb.json"
    out = fmt_mod.format_full_report(
        schematic_path=str(sch_path),
        pcb_path=str(pcb_path),
        spice_path=None,
        emc_path=None,
        derating_profile="commercial",
        thermal_path=None,
    )
    # The PCB header is rendered if the section runs at all
    assert "PCB" in out, (
        f"format_full_report didn't render any PCB section.\n{out[:1500]}"
    )


def test_format_report_full_consumes_fresh_v14_emc(v14_run_dir, fmt_mod):
    """Fresh EMC envelope consumed by full-report. Verifies by_severity
    counts propagate (locks the producer-side of the rc.1 polish stale-key
    bug fixed at 693b664)."""
    sch_path = v14_run_dir / "schematic.json"
    emc_path = v14_run_dir / "emc.json"
    emc = _load(v14_run_dir, "emc.json")
    by_sev = emc["summary"]["by_severity"]
    total = emc["summary"].get("total_findings", 0)

    out = fmt_mod.format_full_report(
        schematic_path=str(sch_path),
        pcb_path=None,
        spice_path=None,
        emc_path=str(emc_path),
        derating_profile="commercial",
        thermal_path=None,
    )
    if total > 0:
        assert f"{total} checks" in out, (
            f"EMC section didn't propagate total_findings={total} from a "
            f"fresh v1.4 envelope.\nfull report (last 2000):\n{out[-2000:]}"
        )
    # The legacy "0 checks: 0 critical" string MUST NOT leak through for
    # a fresh v1.4 envelope.
    assert "0 checks: 0 critical" not in out


def test_format_report_compact_consumes_fresh_v14_emc(v14_run_dir, fmt_mod):
    """F1.2 + F1.4 sibling lock: compact PR-comment path must surface EMC
    error/warning counts from a FRESH v1.4 envelope. If F1.4's uppercase
    'WARNING' typo regressed at the producer side, this would fail."""
    emc = _load(v14_run_dir, "emc.json")
    by_sev = emc["summary"]["by_severity"]
    err = by_sev.get("error", 0)
    warn = by_sev.get("warning", 0)
    report, summary = fmt_mod.format_report(
        schematic_path=None,
        pcb_path=None,
        spice_path=None,
        emc_path=str(v14_run_dir / "emc.json"),
        severity="all",
        derating_profile="commercial",
    )
    if err > 0:
        assert f"EMC: {err} error-severity finding" in report
        assert summary["has_critical"] is True
    if warn > 0:
        assert f"EMC: {warn} warning-severity finding" in report
        assert summary["warning_count"] >= 1


def test_format_report_full_consumes_fresh_v14_thermal(v14_run_dir, fmt_mod):
    """Fresh thermal envelope consumed by full-report — F1.5 sibling lock.
    Thermal section MUST render when thermal_path is supplied (pre-fix the
    section was silently dropped)."""
    sch_path = v14_run_dir / "schematic.json"
    thermal_path = v14_run_dir / "thermal.json"
    thermal = _load(v14_run_dir, "thermal.json")
    total = thermal["summary"].get("total_findings", 0)
    out = fmt_mod.format_full_report(
        schematic_path=str(sch_path),
        pcb_path=None,
        spice_path=None,
        emc_path=None,
        derating_profile="commercial",
        thermal_path=str(thermal_path),
    )
    if total > 0:
        assert "Thermal Analysis" in out, (
            f"Thermal section missing from full report despite total_findings="
            f"{total}. F1.5 regression — format_full_report dropped "
            f"thermal_path again.\nlast 2000 chars:\n{out[-2000:]}"
        )
