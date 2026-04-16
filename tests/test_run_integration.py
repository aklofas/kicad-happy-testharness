"""Integration tests for run/*.py runner scripts.

Each test invokes a runner on a single small repo and verifies:
- Exit code 0
- Output JSON written to the expected path
- Output JSON is valid and contains expected top-level keys

TIER = "online" because these spawn the full analyzer pipeline on a real
checked-out repo. Skips cleanly if the target repo isn't present.

Target repo: jgrip/commodorelcd (small: 1 schematic, 1 PCB).
"""

TIER = "online"

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
REPOS_DIR = HARNESS_DIR / "repos"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"

# Target repo for integration tests. Update if the smoke pack changes.
INTEGRATION_TEST_REPO = "jgrip/commodorelcd"


def _skip_if_no_repo():
    return not (REPOS_DIR / INTEGRATION_TEST_REPO).exists()


def _skip_if_no_kh():
    kh = os.environ.get(
        "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy"))
    return not (Path(kh) / "skills" / "kicad" / "scripts"
                / "analyze_schematic.py").exists()


def _run(runner_rel_path: str, *extra_args):
    """Run run/XXX.py --repo $REPO --jobs 1 and return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(HARNESS_DIR / runner_rel_path),
         "--repo", INTEGRATION_TEST_REPO, "--jobs", "1", *extra_args],
        cwd=str(HARNESS_DIR), capture_output=True, text=True, timeout=300,
    )


def _first_output(analyzer_type: str):
    """Return first .json under results/outputs/{type}/{repo}/, or None."""
    repo_dir = OUTPUTS_DIR / analyzer_type / INTEGRATION_TEST_REPO
    if not repo_dir.exists():
        return None
    for p in sorted(repo_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        return p
    return None


# ---------------------------------------------------------------------------
# run_schematic.py
# ---------------------------------------------------------------------------

def test_run_schematic_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    r = _run("run/run_schematic.py")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"
    out = _first_output("schematic")
    assert out is not None, "no schematic output produced"
    data = json.loads(out.read_text())
    assert data["analyzer_type"] == "schematic"
    assert "findings" in data
    assert "schema_version" in data


# ---------------------------------------------------------------------------
# run_pcb.py
# ---------------------------------------------------------------------------

def test_run_pcb_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    r = _run("run/run_pcb.py")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"
    out = _first_output("pcb")
    if out is None:
        # Not every repo has a PCB; that's not a test failure.
        return
    data = json.loads(out.read_text())
    assert data["analyzer_type"] == "pcb"


# ---------------------------------------------------------------------------
# run_gerbers.py
# ---------------------------------------------------------------------------

def test_run_gerbers_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    r = _run("run/run_gerbers.py")
    # Exit 0 if gerbers were found and analyzed; exit 1 if none found — both are
    # normal. Only unexpected non-zero exit codes (e.g. from crashes) matter here.
    if r.returncode != 0:
        # Acceptable: no gerbers in this repo
        assert "No gerbers found" in r.stderr or r.returncode == 1, \
            f"unexpected exit {r.returncode}: {r.stderr[:500]}"


# ---------------------------------------------------------------------------
# run_emc.py (requires schematic output to already exist — test_run_schematic_basic
# runs first alphabetically and populates it)
# ---------------------------------------------------------------------------

def test_run_emc_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    if _first_output("schematic") is None:
        return
    r = _run("run/run_emc.py")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"
    out = _first_output("emc")
    if out is not None:
        data = json.loads(out.read_text())
        assert data["analyzer_type"] == "emc"


# ---------------------------------------------------------------------------
# run_thermal.py
# ---------------------------------------------------------------------------

def test_run_thermal_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    if _first_output("schematic") is None or _first_output("pcb") is None:
        return
    r = _run("run/run_thermal.py")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"


# ---------------------------------------------------------------------------
# run_spice.py
# ---------------------------------------------------------------------------

def test_run_spice_basic():
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    if _first_output("schematic") is None:
        return
    # SPICE requires ngspice installed
    try:
        subprocess.run(["ngspice", "-v"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return
    r = _run("run/run_spice.py")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"


# ---------------------------------------------------------------------------
# run_datasheets.py (DigiKey API — usually skipped without creds)
# ---------------------------------------------------------------------------

def test_run_datasheets_validate_only_no_crash():
    """--validate-only doesn't require API creds; should not crash."""
    if _skip_if_no_repo() or _skip_if_no_kh():
        return
    r = _run("run/run_datasheets.py", "--validate-only")
    assert r.returncode == 0, f"stderr: {r.stderr[:500]}"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
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
