"""Shared fixtures for analyzer contract tests."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
EMC_SCRIPTS_DIR = MAIN_REPO_ROOT / "skills" / "emc" / "scripts"
FIXTURE_PROJECT = HARNESS_ROOT / "tests" / "fixtures" / "simple-project"

# Output stems == merge_annotations.ANALYZER_FILES (stems). The Layer 2
# merge keys on these exact names, so the e2e merge test depends on them.
ANALYZER_STEMS = ("schematic", "pcb", "gerber", "thermal", "emc", "cross_analysis")


@pytest.fixture
def fixture_project() -> Path:
    """Path to the minimal KiCad fixture project."""
    return FIXTURE_PROJECT


def _run_analyzer(script: Path, argv: list[str]) -> dict:
    result = subprocess.run(
        [sys.executable, str(script), *argv],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def _get_schema(script: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(script), "--schema"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


@pytest.fixture
def run_analyzer():
    return _run_analyzer


@pytest.fixture
def get_schema():
    return _get_schema


def _run_to_file(cmd: list[str], out_path: Path) -> None:
    """Run an analyzer subprocess that writes its envelope to ``out_path``.

    The exit code is ignored on purpose: emc/thermal exit 1 when they emit a
    critical finding but still write a valid envelope. A missing or unparseable
    output file IS a hard error. PYTHONHASHSEED is pinned so hash-seeded
    detector collections serialize reproducibly run-to-run.
    """
    subprocess.run(cmd, capture_output=True, text=True,
                   env={**os.environ, "PYTHONHASHSEED": "0"})
    if not out_path.exists() or out_path.stat().st_size < 3:
        raise RuntimeError(f"analyzer produced no output: {' '.join(cmd)}")
    json.loads(out_path.read_text())  # validate JSON; raises on garbage


@pytest.fixture(scope="session")
def analysis_dir(tmp_path_factory) -> Path:
    """Run all six analyzers on the simple-project fixture into one directory.

    Returns a dir holding real-analyzer envelope JSONs named
    ``<stem>.json`` for every stem in :data:`ANALYZER_STEMS` — the layout
    ``merge_annotations.merge`` consumes as its ``raw_dir``. Session-scoped:
    consumers must treat the directory as read-only (write merged output to
    their own tmp_path).
    """
    dest = tmp_path_factory.mktemp("analysis")
    sch_src = FIXTURE_PROJECT / "simple.kicad_sch"
    pcb_src = FIXTURE_PROJECT / "simple.kicad_pcb"
    gerber_src = FIXTURE_PROJECT / "gerbers"
    py = sys.executable

    sch_out = dest / "schematic.json"
    pcb_out = dest / "pcb.json"
    _run_to_file([py, str(SCRIPTS_DIR / "analyze_schematic.py"), str(sch_src),
                  "-o", str(sch_out), "--only-deterministic"], sch_out)
    _run_to_file([py, str(SCRIPTS_DIR / "analyze_pcb.py"), str(pcb_src),
                  "-o", str(pcb_out), "--only-deterministic"], pcb_out)
    _run_to_file([py, str(SCRIPTS_DIR / "analyze_gerbers.py"), str(gerber_src),
                  "-o", str(dest / "gerber.json")], dest / "gerber.json")
    for stem, script in (("thermal", "analyze_thermal.py"),
                         ("cross_analysis", "cross_analysis.py")):
        out = dest / f"{stem}.json"
        _run_to_file([py, str(SCRIPTS_DIR / script),
                      "--schematic", str(sch_out), "--pcb", str(pcb_out),
                      "--output", str(out), "--only-deterministic"], out)
    emc_out = dest / "emc.json"
    _run_to_file([py, str(EMC_SCRIPTS_DIR / "analyze_emc.py"),
                  "--schematic", str(sch_out), "--pcb", str(pcb_out),
                  "--output", str(emc_out), "--only-deterministic"], emc_out)
    return dest
