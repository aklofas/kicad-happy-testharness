"""Contract test: --analysis-dir routes capability_mode.json + run_id to the
caller-specified directory, NOT the default ``./analysis`` fallback. Every
analyzer envelope in the resulting run dir agrees on a single canonical
``run_id``.

Audit LOG 3 (regression-testing audit, 2026-05-15): the v1.4 capability_mode
machinery was added so consumers can ask "which producer wrote this envelope?"
via ``capability_mode_ref.run_id``. Two production-side bugs caught by the
audit needed contract-level locks:

  - Highest-Risk #4: ``--analysis-dir X`` accidentally wrote
    ``capability_mode.json`` to ``./analysis`` instead of ``X``. Now the
    analyzer resolves a single canonical ``_analysis_dir_for_ctx`` used for
    both the cache (``AnalysisContext``) and the capability_mode record.
  - Highest-Risk #5: ``inputs.run_id`` could drift from
    ``capability_mode_ref.run_id`` if the helpers were called out of order.
    Fix orders ``get_capability_mode_ref`` BEFORE ``build_inputs`` so the
    inputs block carries the same run_id.

This test runs all five v1.4 analyzers (schematic, PCB, EMC, thermal,
cross_analysis) into a fresh ``tmp_path/custom-analysis`` and asserts:

  1. ``capability_mode.json`` lives at ``custom-analysis/`` root (not
     leaked into ``./analysis``).
  2. Every envelope's ``inputs.run_id`` matches
     ``capability_mode_ref.run_id`` matches ``capability_mode.json``'s
     ``run_id``.

Marked TIER=online — spawns real analyzer subprocesses on the commodorelcd
corpus repo. Skips cleanly when the repo isn't cloned or KICAD_HAPPY_DIR
isn't set.
"""

from __future__ import annotations

TIER = "online"

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

ANALYZE_SCHEMATIC = KH_KICAD_SCRIPTS / "analyze_schematic.py"
ANALYZE_PCB = KH_KICAD_SCRIPTS / "analyze_pcb.py"
ANALYZE_EMC = KH_EMC_SCRIPTS / "analyze_emc.py"
ANALYZE_THERMAL = KH_KICAD_SCRIPTS / "analyze_thermal.py"
CROSS_ANALYSIS = KH_KICAD_SCRIPTS / "cross_analysis.py"

# Per-subprocess wall-clock budget. commodorelcd is small (~250 components,
# 1 sheet) — schematic should clear in ~30s; PCB ~20s; downstream three
# combined ~20s. 180s leaves headroom for slow CI without masking a stuck
# analyzer.
SUBPROC_TIMEOUT_S = 180


def _skip_unless_corpus_and_kh_present():
    """Skip cleanly when E2E prerequisites aren't met."""
    if not SCH_PATH.is_file():
        pytest.skip(f"missing corpus repo {TEST_REPO!r} (run checkout.py)")
    if not PCB_PATH.is_file():
        pytest.skip(f"missing PCB at {PCB_PATH}")
    if not ANALYZE_SCHEMATIC.is_file():
        pytest.skip(f"missing analyzer {ANALYZE_SCHEMATIC} (KICAD_HAPPY_DIR)")


def _run_analyzer(script: Path, *args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Run an analyzer subprocess with --only-deterministic and pinned hash
    seed. Per RUNBOOK Checklist 16k workaround for --only-deterministic not
    pinning PYTHONHASHSEED itself (v1.5 carry-over)."""
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(script), *args, "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S, env=env,
    )


def _load_capability_mode(analysis_dir: Path) -> dict:
    p = analysis_dir / "capability_mode.json"
    assert p.is_file(), (
        f"capability_mode.json missing at {p} — analyzer probably wrote it "
        f"to the default ./analysis fallback instead of the --analysis-dir "
        f"target (audit Highest-Risk #4 regression)."
    )
    return json.loads(p.read_text())


def _resolve_current_run_dir(analysis_dir: Path) -> Path:
    """Read manifest.json under analysis_dir and return the current run dir."""
    manifest_path = analysis_dir / "manifest.json"
    assert manifest_path.is_file(), (
        f"manifest.json missing at {manifest_path} — analyzers ran but did "
        f"not register a run in the manifest."
    )
    manifest = json.loads(manifest_path.read_text())
    current = manifest.get("current")
    assert current, f"manifest has no 'current' run pointer: {manifest}"
    run_dir = analysis_dir / current
    assert run_dir.is_dir(), f"current run dir {run_dir} missing"
    return run_dir


# ---------------------------------------------------------------------------

def test_analysis_dir_routes_capability_mode_and_run_id_across_envelopes(
    tmp_path,
):
    """E2E: all 5 v1.4 analyzers write into a custom --analysis-dir, and the
    resulting run is internally consistent — single capability_mode.json at
    the root + every envelope's inputs.run_id == capability_mode_ref.run_id
    == capability_mode.json's run_id.

    Pre-fix counter-example would be a capability_mode.json leaking into
    ``./analysis`` (Highest-Risk #4) or an envelope where ``inputs.run_id``
    drifted from ``capability_mode_ref.run_id`` (Highest-Risk #5).
    """
    _skip_unless_corpus_and_kh_present()

    analysis_dir = tmp_path / "custom-analysis"
    analysis_dir.mkdir()

    # Snapshot the fallback path to catch leakage. The fallback is
    # ./analysis relative to CWD; we use tmp_path/scratch as CWD so any
    # leakage is contained and detectable.
    scratch_cwd = tmp_path / "scratch"
    scratch_cwd.mkdir()
    fallback_dir = scratch_cwd / "analysis"

    # ----- 1. schematic -----
    r = subprocess.run(
        [sys.executable, str(ANALYZE_SCHEMATIC), str(SCH_PATH),
         "--analysis-dir", str(analysis_dir), "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
        cwd=str(scratch_cwd),
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    assert r.returncode == 0, (
        f"analyze_schematic failed: rc={r.returncode}\n"
        f"stderr (last 500): {r.stderr[-500:]}"
    )

    # ----- 2. PCB -----
    r = subprocess.run(
        [sys.executable, str(ANALYZE_PCB), str(PCB_PATH),
         "--analysis-dir", str(analysis_dir), "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
        cwd=str(scratch_cwd),
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    assert r.returncode == 0, (
        f"analyze_pcb failed: rc={r.returncode}\n"
        f"stderr (last 500): {r.stderr[-500:]}"
    )

    # ----- 3. EMC (auto-resolves schematic + pcb from analysis-dir current run) -----
    r = subprocess.run(
        [sys.executable, str(ANALYZE_EMC),
         "--analysis-dir", str(analysis_dir), "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
        cwd=str(scratch_cwd),
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    assert r.returncode == 0, (
        f"analyze_emc failed: rc={r.returncode}\n"
        f"stderr (last 500): {r.stderr[-500:]}"
    )

    # ----- 4. thermal -----
    r = subprocess.run(
        [sys.executable, str(ANALYZE_THERMAL),
         "--analysis-dir", str(analysis_dir), "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
        cwd=str(scratch_cwd),
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    assert r.returncode == 0, (
        f"analyze_thermal failed: rc={r.returncode}\n"
        f"stderr (last 500): {r.stderr[-500:]}"
    )

    # ----- 5. cross_analysis -----
    r = subprocess.run(
        [sys.executable, str(CROSS_ANALYSIS),
         "--analysis-dir", str(analysis_dir), "--only-deterministic"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
        cwd=str(scratch_cwd),
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    assert r.returncode == 0, (
        f"cross_analysis failed: rc={r.returncode}\n"
        f"stderr (last 500): {r.stderr[-500:]}"
    )

    # ----- Assertion 1: capability_mode.json at analysis-dir root -----
    cm = _load_capability_mode(analysis_dir)
    assert "run_id" in cm, f"capability_mode.json missing run_id: {cm}"
    canonical_run_id = cm["run_id"]

    # Fallback ./analysis MUST NOT have been created — that would mean some
    # analyzer ignored --analysis-dir for its capability_mode write.
    assert not fallback_dir.exists(), (
        f"./analysis fallback was created at {fallback_dir} despite "
        f"--analysis-dir being set. Highest-Risk #4 regression: some "
        f"analyzer is computing capability_mode_dir from a different "
        f"source than the cache dir."
    )

    # ----- Assertion 2: run_id consistency across all envelopes -----
    run_dir = _resolve_current_run_dir(analysis_dir)
    expected_files = {
        "schematic.json", "pcb.json", "emc.json",
        "thermal.json", "cross_analysis.json",
    }
    actual_files = {p.name for p in run_dir.glob("*.json")}
    missing = expected_files - actual_files
    assert not missing, (
        f"run dir {run_dir} missing expected envelopes: {missing}. "
        f"Present: {sorted(actual_files)}"
    )

    drift_reports = []
    for envelope_name in sorted(expected_files):
        env_path = run_dir / envelope_name
        env_data = json.loads(env_path.read_text())
        inputs = env_data.get("inputs") or {}
        ref = env_data.get("capability_mode_ref") or {}
        inputs_run_id = inputs.get("run_id")
        ref_run_id = ref.get("run_id")
        if inputs_run_id != canonical_run_id:
            drift_reports.append(
                f"{envelope_name}: inputs.run_id={inputs_run_id!r} != "
                f"capability_mode.run_id={canonical_run_id!r}"
            )
        if ref_run_id != canonical_run_id:
            drift_reports.append(
                f"{envelope_name}: capability_mode_ref.run_id={ref_run_id!r} "
                f"!= capability_mode.run_id={canonical_run_id!r}"
            )

    assert not drift_reports, (
        "run_id drift detected (Highest-Risk #5 regression — "
        "get_capability_mode_ref must be called BEFORE build_inputs so "
        "inputs.run_id carries the canonical id):\n  "
        + "\n  ".join(drift_reports)
    )


def test_analysis_dir_capability_mode_first_writer_wins(tmp_path):
    """Audit invariant: get_or_create_capability_mode is first-writer-wins.
    A second analyzer run into the same analysis-dir must reuse the existing
    capability_mode.json, not overwrite it. Pin run_id stability so downstream
    consumers that store the id (review packets, datasheet caches keyed by
    run_id) don't see it flip mid-session."""
    _skip_unless_corpus_and_kh_present()

    analysis_dir = tmp_path / "custom-analysis"
    analysis_dir.mkdir()
    scratch_cwd = tmp_path / "scratch"
    scratch_cwd.mkdir()

    def _run_schematic():
        return subprocess.run(
            [sys.executable, str(ANALYZE_SCHEMATIC), str(SCH_PATH),
             "--analysis-dir", str(analysis_dir), "--only-deterministic"],
            capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S,
            cwd=str(scratch_cwd),
            env={**os.environ, "PYTHONHASHSEED": "0"},
        )

    r1 = _run_schematic()
    assert r1.returncode == 0, f"first schematic run failed: {r1.stderr[-400:]}"
    cm_first = _load_capability_mode(analysis_dir)

    r2 = _run_schematic()
    assert r2.returncode == 0, f"second schematic run failed: {r2.stderr[-400:]}"
    cm_second = _load_capability_mode(analysis_dir)

    assert cm_first["run_id"] == cm_second["run_id"], (
        f"capability_mode.run_id changed between runs: "
        f"{cm_first['run_id']!r} → {cm_second['run_id']!r}. "
        f"first-writer-wins invariant violated."
    )
