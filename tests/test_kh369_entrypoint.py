"""KH-369: GitHub Action project auto-detection must be deterministic.

The Action entrypoint used to auto-detect the schematic with a bare
`find | head -1`, silently picking an arbitrary project/child-sheet in
multi-project repos. Detection now lives in action/detect_project.sh
(sourced by action/entrypoint.sh) and must: auto-select when exactly one
project is unambiguous, honor an explicit schematic input as-is, and
fail loudly (nonzero exit, candidates listed on stderr) otherwise.

These tests exercise detect_project.sh directly rather than the full
entrypoint.sh — detection runs before any python3/analyzer invocation,
so sourcing just that file avoids needing to stub the rest of the
pipeline (schematic/PCB/EMC/thermal analysis, report generation, the
GitHub status POST, etc.), which would be brittle to shim faithfully.

The hard-fail only applies when NEITHER schematic nor PCB could be
resolved: a caller that explicitly supplies INPUT_PCB (a PCB-only
re-spin or footprint-library repo with zero/ambiguous .kicad_sch
files) must keep working PCB-only, exactly as it did before KH-369 —
see test_explicit_pcb_survives_missing_schematic and
test_explicit_pcb_survives_ambiguous_schematic below.
"""
import os
import shutil
import subprocess
from pathlib import Path

try:
    import pytest
except ImportError:  # pre-push hook runs root tests under bare python3 (no
    # pytest); only decorator applications happen at import time, so a no-op
    # stand-in keeps the file importable — the tests themselves need pytest.
    class _StubMark:
        @staticmethod
        def skipif(*_a, **_k):
            return lambda fn: fn

    class _StubPytest:
        mark = _StubMark

        @staticmethod
        def fixture(*_a, **_k):
            return lambda fn: fn

        @staticmethod
        def skip(reason=""):
            raise SystemExit(0)

    pytest = _StubPytest

KH = Path(os.environ["KICAD_HAPPY_DIR"])
DETECT_SCRIPT = KH / "action/detect_project.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash not available"
)


def _run_detect(workdir, *, input_schematic="", input_pcb=""):
    """Source detect_project.sh the same way entrypoint.sh does.

    Seeds SCHEMATIC/PCB from INPUT_SCHEMATIC/INPUT_PCB (mirroring
    entrypoint.sh lines 14-15), sources the script under `set -euo
    pipefail` (mirroring entrypoint.sh line 4), then prints the
    resulting SCHEMATIC/PCB values so the test can parse them.
    """
    driver = f"""
set -euo pipefail
cd {workdir!s}
SCHEMATIC="{input_schematic}"
PCB="{input_pcb}"
ACTION_PATH="{KH!s}"
. "{DETECT_SCRIPT!s}"
echo "RESULT_SCHEMATIC=$SCHEMATIC"
echo "RESULT_PCB=$PCB"
"""
    return subprocess.run(
        ["bash", "-c", driver],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _parse_results(stdout):
    values = {}
    for line in stdout.splitlines():
        if line.startswith("RESULT_SCHEMATIC="):
            values["schematic"] = line[len("RESULT_SCHEMATIC=") :]
        elif line.startswith("RESULT_PCB="):
            values["pcb"] = line[len("RESULT_PCB=") :]
    return values


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")


def test_two_projects_fails_with_candidates(tmp_path):
    """Multi-project repo with no explicit input must fail, not guess."""
    _touch(tmp_path / "a" / "a.kicad_pro")
    _touch(tmp_path / "a" / "a.kicad_sch")
    _touch(tmp_path / "b" / "b.kicad_pro")
    _touch(tmp_path / "b" / "b.kicad_sch")

    result = _run_detect(tmp_path)

    assert result.returncode != 0, result.stdout
    assert "::error::" in result.stderr
    assert "a.kicad_sch" in result.stderr
    assert "b.kicad_sch" in result.stderr


def test_single_project_auto_selects(tmp_path):
    """Exactly one project auto-selects its schematic and sibling PCB."""
    _touch(tmp_path / "proj" / "proj.kicad_pro")
    _touch(tmp_path / "proj" / "proj.kicad_sch")
    _touch(tmp_path / "proj" / "proj.kicad_pcb")

    result = _run_detect(tmp_path)

    assert result.returncode == 0, result.stderr
    values = _parse_results(result.stdout)
    assert values["schematic"] == "./proj/proj.kicad_sch"
    assert values["pcb"] == "./proj/proj.kicad_pcb"


def test_explicit_schematic_used_as_is(tmp_path):
    """An explicit INPUT_SCHEMATIC bypasses auto-detection entirely."""
    _touch(tmp_path / "a" / "a.kicad_pro")
    _touch(tmp_path / "a" / "a.kicad_sch")
    _touch(tmp_path / "b" / "b.kicad_pro")
    _touch(tmp_path / "b" / "b.kicad_sch")

    result = _run_detect(tmp_path, input_schematic="./b/b.kicad_sch")

    assert result.returncode == 0, result.stderr
    values = _parse_results(result.stdout)
    assert values["schematic"] == "./b/b.kicad_sch"


def test_explicit_pcb_survives_missing_schematic(tmp_path):
    """PCB-only invocation (e.g. a footprint-library repo) must not fail.

    Regression case: a repo with zero .kicad_sch files but an explicit
    INPUT_PCB used to run PCB-only under the old find|head-1 code
    (SCHEMATIC just stayed empty). The KH-369 fix must not turn this
    into a hard failure.
    """
    _touch(tmp_path / "board.kicad_pcb")

    result = _run_detect(tmp_path, input_pcb="./board.kicad_pcb")

    assert result.returncode == 0, result.stderr
    assert "::error::" not in result.stderr
    values = _parse_results(result.stdout)
    assert values["schematic"] == ""
    assert values["pcb"] == "./board.kicad_pcb"


def test_explicit_pcb_survives_ambiguous_schematic(tmp_path):
    """PCB-only invocation must survive an ambiguous (multi-project) repo too.

    Same regression as above, but with two candidate schematics instead
    of zero — either way, schematic auto-detection can't resolve one,
    and an explicit INPUT_PCB means that's fine (PCB-only), not fatal.
    A stderr notice is acceptable; a hard failure is not.
    """
    _touch(tmp_path / "a" / "a.kicad_pro")
    _touch(tmp_path / "a" / "a.kicad_sch")
    _touch(tmp_path / "b" / "b.kicad_pro")
    _touch(tmp_path / "b" / "b.kicad_sch")
    _touch(tmp_path / "board.kicad_pcb")

    result = _run_detect(tmp_path, input_pcb="./board.kicad_pcb")

    assert result.returncode == 0, result.stderr
    assert "::error::" not in result.stderr
    values = _parse_results(result.stdout)
    assert values["schematic"] == ""
    assert values["pcb"] == "./board.kicad_pcb"
