#!/usr/bin/env python3
"""Regression guard: analyzers must accept bare filenames (no directory component).

Covers kicad-happy bug #2 from the 2026-04-11 main-repo inspection brief:
`analyze_pcb.py` crashed with `FileNotFoundError: ''` when given a bare
filename like `"foo.kicad_pcb"` because `os.path.dirname("foo.kicad_pcb")`
returns `""` and `os.listdir('')` fails. The harness normalizes paths before
invoking analyzers, so the bug was invisible in routine runner use — it only
tripped on ad-hoc invocations from inside a project directory. Main-repo fix
landed in kicad-happy commit 9693347 (status as of 2026-04-11: unpushed —
this test will stay in FAIL state until the fix is pulled, then flip to PASS).

This test walks real corpus projects, chdir's into each project directory,
invokes each analyzer with a BARE filename (no `./`, no absolute path), and
asserts exit 0 + non-empty JSON output.

Covers:
- analyze_pcb.py (the originally reported bug)
- analyze_schematic.py (checked for the symmetric class of bug — clean)
- analyze_gerbers.py (checked for the symmetric class of bug — clean)

Run:
    python3 integration/test_analyzer_cli_bare_filename.py
    # or via the dispatcher:
    python3 run_tests.py --tier online

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (default: ../kicad-happy)
"""

TIER = "online"

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

KICAD_HAPPY = Path(os.environ.get("KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
SCRIPTS = KICAD_HAPPY / "skills" / "kicad" / "scripts"
ANALYZE_PCB = SCRIPTS / "analyze_pcb.py"
ANALYZE_SCHEMATIC = SCRIPTS / "analyze_schematic.py"
ANALYZE_GERBERS = SCRIPTS / "analyze_gerbers.py"

# Projects selected to exercise the .kicad_pro reading code path that was
# the locus of the original bug. Each must have both a .kicad_pcb AND a
# sibling .kicad_pro file.
PROJECTS = [
    # path relative to HARNESS_DIR, filename of the .kicad_pcb to test with
    ("repos/datcal/midi-box/hardware/midi-box", "midi-box.kicad_pcb"),
    ("repos/Fihdi/Eurorack/ClockDividerV2", "ClockDividerV2.kicad_pcb"),
    ("repos/jkominek/piano-conversion/hardware/sensorboards/2040-centered-4x",
     "2040-centered-4x.kicad_pcb"),
    ("repos/JeremyJStarcher/pal1-ram-rom/kicad/level-shifted", "level-shifted.kicad_pcb"),
    ("repos/JustinHsu845/PiEDB-Y15/PDB", "PDB.kicad_pcb"),
]


def _run_analyzer_from_dir(analyzer_path, project_dir, bare_arg):
    """Invoke analyzer_path with bare_arg while cwd is project_dir.

    Returns (returncode, stdout, stderr). On success, stdout should be valid
    JSON; on failure, stderr will contain the Python traceback.
    """
    result = subprocess.run(
        [sys.executable, str(analyzer_path), bare_arg],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode, result.stdout, result.stderr


def test_analyze_pcb_bare_filename():
    """analyze_pcb.py must accept a bare PCB filename from its own directory."""
    failures = []
    for rel_dir, pcb_name in PROJECTS:
        project_dir = HARNESS_DIR / rel_dir
        if not (project_dir / pcb_name).exists():
            failures.append(f"{rel_dir}/{pcb_name}: project missing — fixture gone")
            continue
        rc, stdout, stderr = _run_analyzer_from_dir(ANALYZE_PCB, project_dir, pcb_name)
        if rc != 0:
            failures.append(f"{rel_dir}/{pcb_name}: rc={rc}\n  stderr tail: {stderr[-500:]}")
            continue
        try:
            data = json.loads(stdout)
            if not data or not isinstance(data, dict):
                failures.append(f"{rel_dir}/{pcb_name}: empty/non-dict JSON output")
        except json.JSONDecodeError as e:
            failures.append(f"{rel_dir}/{pcb_name}: invalid JSON ({e})")
    assert not failures, (
        "analyze_pcb.py failed on bare filenames:\n  " + "\n  ".join(failures)
    )


def test_analyze_schematic_bare_filename():
    """analyze_schematic.py must accept a bare schematic filename — checking
    for symmetric bugs to kicad-happy #2."""
    failures = []
    for rel_dir, pcb_name in PROJECTS:
        project_dir = HARNESS_DIR / rel_dir
        sch_name = pcb_name.replace(".kicad_pcb", ".kicad_sch")
        if not (project_dir / sch_name).exists():
            continue  # not all projects have a top-level schematic with the matching name
        rc, stdout, stderr = _run_analyzer_from_dir(ANALYZE_SCHEMATIC, project_dir, sch_name)
        if rc != 0:
            failures.append(f"{rel_dir}/{sch_name}: rc={rc}\n  stderr tail: {stderr[-500:]}")
            continue
        try:
            data = json.loads(stdout)
            if not data or not isinstance(data, dict):
                failures.append(f"{rel_dir}/{sch_name}: empty/non-dict JSON output")
        except json.JSONDecodeError as e:
            failures.append(f"{rel_dir}/{sch_name}: invalid JSON ({e})")
    assert not failures, (
        "analyze_schematic.py failed on bare filenames:\n  " + "\n  ".join(failures)
    )


def test_analyze_gerbers_bare_dirname():
    """analyze_gerbers.py must accept a bare directory name (the gerbers
    analyzer takes a directory rather than a file) — checking for symmetric
    bugs to kicad-happy #2."""
    failures = []
    # Find any project with a gerber directory we can test with a bare name
    tested = 0
    for owner_dir in sorted((HARNESS_DIR / "repos").iterdir()):
        if not owner_dir.is_dir() or tested >= 3:
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or tested >= 3:
                continue
            # Look for a subdirectory with .gbr files
            for candidate in repo_dir.rglob("*.gbr"):
                gerber_dir = candidate.parent
                parent = gerber_dir.parent
                bare_name = gerber_dir.name
                rc, stdout, stderr = _run_analyzer_from_dir(
                    ANALYZE_GERBERS, parent, bare_name
                )
                if rc != 0:
                    failures.append(
                        f"{parent}/{bare_name}: rc={rc}\n  stderr tail: {stderr[-500:]}"
                    )
                else:
                    try:
                        json.loads(stdout)
                    except json.JSONDecodeError as e:
                        failures.append(f"{parent}/{bare_name}: invalid JSON ({e})")
                tested += 1
                break
    assert not failures, (
        "analyze_gerbers.py failed on bare dirnames:\n  " + "\n  ".join(failures)
    )
    assert tested > 0, "no gerber fixture found in corpus — test did not run"


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
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
