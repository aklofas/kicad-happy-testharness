"""Contract test: action/entrypoint.sh preserves valid analyzer JSON across
nonzero analyzer exits.

Audit B2 / F2 cases 1+3: EMC and thermal analyzers exit nonzero when blocking
findings are detected. Pre-fix, entrypoint.sh treated any nonzero exit as a
crash and cleared the JSON path — silently dropping exactly the runs that found
release-blocking issues. The fix wraps the nonzero-exit branch in a JSON-validity
check: keep the path set if the output exists and parses; clear only on
missing/malformed JSON.

Test approach: extract the EMC and thermal blocks from entrypoint.sh, stub the
analyzer binaries to control exit code + JSON output, run the extracted blocks
under bash, observe final state of EMC_JSON / THERMAL_JSON and stderr.
"""

from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path

import pytest

from tests.contract._paths import MAIN_REPO_ROOT

ENTRYPOINT_SH = MAIN_REPO_ROOT / "action" / "entrypoint.sh"


@pytest.fixture(scope="module")
def emc_block() -> str:
    """Extract the EMC analysis block from entrypoint.sh by its comment fence."""
    text = ENTRYPOINT_SH.read_text()
    m = re.search(
        r"# Run EMC analysis.*?(?=# -+\n# Run thermal analysis)",
        text,
        re.DOTALL,
    )
    assert m, "could not locate EMC block in entrypoint.sh"
    return m.group(0)


@pytest.fixture(scope="module")
def thermal_block() -> str:
    """Extract the thermal analysis block from entrypoint.sh by its comment fence."""
    text = ENTRYPOINT_SH.read_text()
    m = re.search(
        r"# Run thermal analysis.*?(?=# -+\n# Diff against base branch)",
        text,
        re.DOTALL,
    )
    assert m, "could not locate thermal block in entrypoint.sh"
    return m.group(0)


def _write_stub_analyzer(path: Path, mode: str) -> None:
    """Write a Python stub analyzer that simulates one of four behaviors.

    Modes:
      success — write valid JSON, exit 0
      valid_blocking — write valid v1.4 JSON with by_severity.error=1, exit 1
      malformed — write garbage to --output, exit 1
      missing — exit 1 without writing anything
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload_blocking = {
        "analyzer_type": "stub",
        "schema_version": "1.4.0",
        "summary": {
            "total_findings": 1,
            "by_severity": {"error": 1, "warning": 0, "info": 0},
            "emc_risk_score": 50,
            "thermal_score": 50,
            "components_analyzed": 1,
        },
        "findings": [],
    }
    payload_success = {
        "analyzer_type": "stub",
        "schema_version": "1.4.0",
        "summary": {
            "total_findings": 0,
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "emc_risk_score": 0,
            "thermal_score": 100,
            "components_analyzed": 0,
        },
        "findings": [],
    }
    script = textwrap.dedent(f'''\
        #!/usr/bin/env python3
        import json, sys
        mode = {mode!r}
        out = None
        for i, a in enumerate(sys.argv):
            if a == "--output":
                out = sys.argv[i + 1]
        if mode == "success":
            json.dump({payload_success!r}, open(out, "w"))
            sys.exit(0)
        elif mode == "valid_blocking":
            json.dump({payload_blocking!r}, open(out, "w"))
            sys.exit(1)
        elif mode == "malformed":
            open(out, "w").write("{{garbage")
            sys.exit(1)
        elif mode == "missing":
            sys.exit(1)
        else:
            sys.exit(99)
    ''')
    path.write_text(script)
    path.chmod(0o755)


def _run_emc_block(emc_block: str, tmp_path: Path, stub_mode: str) -> dict:
    """Run the extracted EMC block under bash with a stub analyzer; report
    final EMC_JSON value + captured stderr."""
    action_path = tmp_path / "action_root"
    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    sch_json = tmp_path / "sch.json"
    sch_json.write_text("{}")  # presence-only — stub ignores content

    stub = action_path / "skills" / "emc" / "scripts" / "analyze_emc.py"
    _write_stub_analyzer(stub, stub_mode)

    driver = textwrap.dedent(f"""\
        #!/bin/bash
        set -u
        OUTDIR={outdir}
        ACTION_PATH={action_path}
        SCH_JSON={sch_json}
        PCB_JSON=""
        CONFIG_PATH=""
        {emc_block}
        echo "FINAL_EMC_JSON=$EMC_JSON"
    """)
    result = subprocess.run(
        ["bash", "-c", driver],
        capture_output=True, text=True,
    )
    final_line = next(
        (l for l in result.stdout.splitlines() if l.startswith("FINAL_EMC_JSON=")),
        "FINAL_EMC_JSON=__missing__",
    )
    return {
        "final_emc_json": final_line.split("=", 1)[1],
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def _run_thermal_block(thermal_block: str, tmp_path: Path, stub_mode: str) -> dict:
    """Same as _run_emc_block but for thermal. Stub lives at
    $ACTION_PATH/skills/kicad/scripts/analyze_thermal.py."""
    action_path = tmp_path / "action_root"
    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text("{}")
    pcb_json.write_text("{}")

    stub = action_path / "skills" / "kicad" / "scripts" / "analyze_thermal.py"
    _write_stub_analyzer(stub, stub_mode)

    driver = textwrap.dedent(f"""\
        #!/bin/bash
        set -u
        OUTDIR={outdir}
        ACTION_PATH={action_path}
        SCRIPTS={action_path}/skills/kicad/scripts
        SCH_JSON={sch_json}
        PCB_JSON={pcb_json}
        CONFIG_PATH=""
        DS_DIR=""
        {thermal_block}
        echo "FINAL_THERMAL_JSON=$THERMAL_JSON"
    """)
    result = subprocess.run(
        ["bash", "-c", driver],
        capture_output=True, text=True,
    )
    final_line = next(
        (l for l in result.stdout.splitlines() if l.startswith("FINAL_THERMAL_JSON=")),
        "FINAL_THERMAL_JSON=__missing__",
    )
    return {
        "final_thermal_json": final_line.split("=", 1)[1],
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


# ---------------------------------------------------------------------------
# EMC
# ---------------------------------------------------------------------------

def test_emc_valid_json_survives_nonzero_exit(emc_block, tmp_path):
    """Audit B2 case 1: when EMC analyzer exits nonzero AND writes valid JSON,
    the EMC_JSON path must remain set so the report formatter consumes the
    findings. A `::notice::` line surfaces the disposition."""
    r = _run_emc_block(emc_block, tmp_path, "valid_blocking")
    assert r["final_emc_json"].endswith("emc.json"), (
        f"EMC_JSON cleared on valid-JSON nonzero exit; should have been "
        f"preserved.\nstdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )
    # File must exist + be parseable (sanity on the stub)
    p = Path(r["final_emc_json"])
    assert p.is_file()
    assert json.loads(p.read_text())["summary"]["by_severity"]["error"] == 1
    # Disposition notice must mention blocking findings
    combined = r["stdout"] + r["stderr"]
    assert "blocking findings" in combined, (
        f"Expected '::notice::...blocking findings' in output.\n"
        f"stdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )


def test_emc_malformed_json_clears_path(emc_block, tmp_path):
    """Audit B2 case 2: malformed JSON on nonzero exit must clear EMC_JSON and
    emit the non-blocking failure notice."""
    r = _run_emc_block(emc_block, tmp_path, "malformed")
    assert r["final_emc_json"] == "", (
        f"EMC_JSON should be cleared on malformed output; got "
        f"{r['final_emc_json']!r}.\nstdout:\n{r['stdout']}"
    )
    combined = r["stdout"] + r["stderr"]
    assert "non-blocking" in combined or "failed" in combined


def test_emc_missing_output_clears_path(emc_block, tmp_path):
    """Audit B2 sub-case: missing output file on nonzero exit must clear
    EMC_JSON (true crash, no surviving artifact)."""
    r = _run_emc_block(emc_block, tmp_path, "missing")
    assert r["final_emc_json"] == ""


# ---------------------------------------------------------------------------
# Thermal — same shape
# ---------------------------------------------------------------------------

def test_thermal_valid_json_survives_nonzero_exit(thermal_block, tmp_path):
    """Audit B2 case 3 (thermal sibling): valid thermal JSON on nonzero exit
    must keep THERMAL_JSON set."""
    r = _run_thermal_block(thermal_block, tmp_path, "valid_blocking")
    assert r["final_thermal_json"].endswith("thermal.json"), (
        f"THERMAL_JSON cleared on valid-JSON nonzero exit.\n"
        f"stdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )
    p = Path(r["final_thermal_json"])
    assert p.is_file()
    assert json.loads(p.read_text())["summary"]["by_severity"]["error"] == 1
    combined = r["stdout"] + r["stderr"]
    assert "blocking findings" in combined


def test_thermal_malformed_json_clears_path(thermal_block, tmp_path):
    r = _run_thermal_block(thermal_block, tmp_path, "malformed")
    assert r["final_thermal_json"] == ""
    combined = r["stdout"] + r["stderr"]
    assert "non-blocking" in combined or "failed" in combined


# ---------------------------------------------------------------------------
# INPUT_DIFF_BASE — opt-in diff branch wiring
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def diff_block() -> str:
    """Extract the 'Diff against base branch' block from entrypoint.sh.
    Anchored on ``DIFF_JSON=""`` (the first line below the header banner)
    so the trailing ``# ---`` separator under the header doesn't truncate
    the match. Ends at the start of the next top-level section banner.
    """
    text = ENTRYPOINT_SH.read_text()
    m = re.search(
        r'^DIFF_JSON="".*?(?=^# -+\n# Format markdown report)',
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert m, "could not locate diff branch block in entrypoint.sh"
    return m.group(0)


def _run_diff_block(diff_block: str, tmp_path: Path,
                    input_diff_base: str,
                    github_base_ref: str) -> dict:
    """Run the extracted diff block with the given env vars. Stubs ``git`` so
    fetch/checkout never touch the real repo, and stubs ``python3`` invocations
    by routing them through PATH-shadowed no-op stubs."""
    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    # Stub git binary — emits args to debug, exits 0 (so BASE_OK stays true)
    stub_bin = tmp_path / "bin"
    stub_bin.mkdir(parents=True, exist_ok=True)
    git_stub = stub_bin / "git"
    git_stub.write_text("#!/bin/bash\necho \"[stub git] $@\" >&2\nexit 0\n")
    git_stub.chmod(0o755)
    # Stub analyzer scripts — no-op
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for name in ("analyze_schematic.py", "analyze_pcb.py", "diff_analysis.py"):
        s = scripts_dir / name
        s.write_text("#!/usr/bin/env python3\nimport sys; sys.exit(0)\n")
        s.chmod(0o755)

    driver = textwrap.dedent(f"""\
        #!/bin/bash
        set -u
        export PATH={stub_bin}:$PATH
        OUTDIR={outdir}
        SCRIPTS={scripts_dir}
        SCHEMATIC=/nonexistent.kicad_sch
        PCB=
        SCH_JSON=
        PCB_JSON=
        EMC_JSON=
        SPICE_JSON=
        INPUT_DIFF_BASE={input_diff_base!r}
        GITHUB_BASE_REF={github_base_ref!r}
        {diff_block}
        echo "FINAL_DIFF_JSON=$DIFF_JSON"
    """)
    result = subprocess.run(
        ["bash", "-c", driver],
        capture_output=True, text=True,
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def test_input_diff_base_true_with_base_ref_enters_diff_branch(
    diff_block, tmp_path
):
    """Audit F2 / B2 wiring case: INPUT_DIFF_BASE=true AND GITHUB_BASE_REF set
    must reach the diff branch (``::group::Diff Analysis`` opened). Locks the
    env-wiring fix from rc.1 polish — pre-fix the env vars never reached the
    branch because the check happened against a different name."""
    r = _run_diff_block(diff_block, tmp_path, "true", "main")
    combined = r["stdout"] + r["stderr"]
    assert "::group::Diff Analysis" in combined, (
        f"Diff branch not entered with INPUT_DIFF_BASE=true + "
        f"GITHUB_BASE_REF=main.\nstdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )
    assert "::endgroup::" in combined


def test_input_diff_base_false_skips_diff_branch(diff_block, tmp_path):
    """Counter-example: INPUT_DIFF_BASE=false (or unset) must NOT enter the
    diff branch, even with GITHUB_BASE_REF set. Default behavior is opt-in."""
    r = _run_diff_block(diff_block, tmp_path, "false", "main")
    combined = r["stdout"] + r["stderr"]
    assert "::group::Diff Analysis" not in combined, (
        f"Diff branch unexpectedly entered with INPUT_DIFF_BASE=false.\n"
        f"stdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )


def test_input_diff_base_true_without_base_ref_skips_diff_branch(
    diff_block, tmp_path
):
    """Counter-example: INPUT_DIFF_BASE=true but GITHUB_BASE_REF missing must
    skip the diff branch — both conditions are required by the AND-guard."""
    r = _run_diff_block(diff_block, tmp_path, "true", "")
    combined = r["stdout"] + r["stderr"]
    assert "::group::Diff Analysis" not in combined, (
        f"Diff branch entered without GITHUB_BASE_REF.\n"
        f"stdout:\n{r['stdout']}\nstderr:\n{r['stderr']}"
    )


# ---------------------------------------------------------------------------
# GITHUB_OUTPUT — Action outputs reflect SUMMARY_JSON values
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def outputs_block() -> str:
    """Extract the 'Set finding outputs' block from entrypoint.sh."""
    text = ENTRYPOINT_SH.read_text()
    m = re.search(
        r"# Set finding outputs.*?(?=^# -+$|^# Post commit)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert m, "could not locate 'Set finding outputs' block in entrypoint.sh"
    return m.group(0)


def _run_outputs_block(outputs_block: str, tmp_path: Path,
                       summary_payload: dict | None) -> dict:
    """Run the extracted GITHUB_OUTPUT block. If summary_payload is None,
    SUMMARY_JSON file is not created so the fallback branch fires."""
    summary_path = tmp_path / "summary.json"
    if summary_payload is not None:
        summary_path.write_text(json.dumps(summary_payload))
    github_output = tmp_path / "github_output"
    github_output.write_text("")  # ensure exists

    driver = textwrap.dedent(f"""\
        #!/bin/bash
        set -u
        SUMMARY_JSON={summary_path}
        GITHUB_OUTPUT={github_output}
        {outputs_block}
    """)
    result = subprocess.run(
        ["bash", "-c", driver],
        capture_output=True, text=True,
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "github_output": github_output.read_text(),
    }


def test_action_outputs_match_summary_json(outputs_block, tmp_path):
    """Audit F2 case 4: Action outputs (``findings-count``, ``has-critical``)
    must mirror the SUMMARY_JSON values written by format-report.py. Pre-fix
    these went through a parallel computation that could drift from the
    formatter's own numbers; fix routes both through SUMMARY_JSON."""
    payload = {
        "findings_count": 7,
        "has_critical": True,
        "verified_count": 12,
    }
    r = _run_outputs_block(outputs_block, tmp_path, payload)
    assert "findings-count=7" in r["github_output"], (
        f"Expected findings-count=7 in GITHUB_OUTPUT.\n"
        f"github_output content:\n{r['github_output']}"
    )
    assert "has-critical=true" in r["github_output"], (
        f"Expected has-critical=true in GITHUB_OUTPUT (lowercase per "
        f"action.yml convention).\ngithub_output:\n{r['github_output']}"
    )


def test_action_outputs_match_summary_json_no_critical(outputs_block, tmp_path):
    """Counter-example: has_critical=False from SUMMARY_JSON must serialize as
    lowercase ``false`` (action outputs are string-typed; capitalization
    matters for downstream ``if`` conditions in workflow YAML)."""
    payload = {
        "findings_count": 3,
        "has_critical": False,
        "verified_count": 5,
    }
    r = _run_outputs_block(outputs_block, tmp_path, payload)
    assert "findings-count=3" in r["github_output"]
    assert "has-critical=false" in r["github_output"], (
        f"Expected has-critical=false (lowercase) when summary.has_critical=False.\n"
        f"github_output:\n{r['github_output']}"
    )


def test_action_outputs_default_to_zero_when_summary_missing(
    outputs_block, tmp_path
):
    """Audit F2 fallback case: when SUMMARY_JSON doesn't exist (e.g. format-
    report.py crashed before writing it), Action outputs must default to
    ``findings-count=0`` + ``has-critical=false`` so downstream gates fail-safe."""
    r = _run_outputs_block(outputs_block, tmp_path, summary_payload=None)
    assert "findings-count=0" in r["github_output"]
    assert "has-critical=false" in r["github_output"]
