"""Unit tests for regression/run_checks.py exit code behavior (TH-015).

Tests that run_checks.py exits with the correct code based on assertion
pass/fail/error state and the --allow-errors flag.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
RUN_CHECKS = HARNESS_DIR / "regression" / "run_checks.py"

_REPO = "fake_owner/fake_repo"
_PROJECT = "fake_project"


def _write_assertion_file(tmpdir, assertions, file_pattern="test_file",
                          analyzer_type="schematic"):
    """Write an assertion JSON file into the fake reference tree.

    Also creates an empty baselines/metadata.json so the stray-dir guard
    in checks.py:load_assertions() treats this as a real project dir.
    """
    proj_dir = Path(tmpdir) / "reference" / _REPO / _PROJECT
    # Create baselines/metadata.json to opt out of the stray-dir guard (TH-035).
    # project_path is None → project_prefix yields "" → output file looked up
    # at "{file_pattern}.json" (matches _write_output_file below).
    bdir = proj_dir / "baselines"
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / "metadata.json").write_text(json.dumps({
        "repo": _REPO, "project": _PROJECT,
    }), encoding="utf-8")
    adir = proj_dir / "assertions" / analyzer_type
    adir.mkdir(parents=True, exist_ok=True)
    afile = adir / "test_assertions.json"
    afile.write_text(json.dumps({
        "file_pattern": file_pattern,
        "analyzer_type": analyzer_type,
        "assertions": assertions,
    }), encoding="utf-8")


def _write_output_file(tmpdir, data, file_pattern="test_file",
                       analyzer_type="schematic"):
    """Write a fake analyzer output JSON file into the fake results tree."""
    odir = Path(tmpdir) / "results" / "outputs" / analyzer_type / _REPO
    odir.mkdir(parents=True, exist_ok=True)
    # Output filename matches what find_output_file expects:
    # project_prefix(project_path) + file_pattern + ".json"
    # Since project_path is None (no metadata), prefix is "" — so just file_pattern.json
    ofile = odir / f"{file_pattern}.json"
    ofile.write_text(json.dumps(data), encoding="utf-8")


def _run_checks(tmpdir, extra_args=None):
    """Invoke run_checks.py with --json --repo, redirecting DATA_DIR via env var.

    Returns (returncode, parsed_json_output).
    """
    env = os.environ.copy()
    env["KICAD_HAPPY_TESTHARNESS_DATA_DIR"] = str(tmpdir)
    cmd = [sys.executable, str(RUN_CHECKS), "--json", "--repo", _REPO]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env,
                            timeout=30)
    out = result.stdout.strip()
    # Parse last JSON object in output (there may be warnings on stderr)
    parsed = None
    if out:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            # Try the last line
            for line in reversed(out.splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        parsed = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
    return result.returncode, parsed


def test_exit_0_when_all_pass():
    """Assertions present, output present, all pass → exit 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assertions = [
            {
                "id": "TEST-001",
                "description": "component count in range",
                "check": {"path": "component_count", "op": "range",
                           "min": 1, "max": 999},
            }
        ]
        _write_assertion_file(tmpdir, assertions)
        _write_output_file(tmpdir, {"component_count": 42})

        rc, out = _run_checks(tmpdir)
        assert out is not None, "Expected JSON output from run_checks.py"
        assert out["passed"] == 1, f"Expected 1 passed, got {out}"
        assert out["failed"] == 0, f"Expected 0 failed, got {out}"
        assert out["errors"] == 0, f"Expected 0 errors, got {out}"
        assert rc == 0, f"Expected exit 0, got {rc}"


def test_exit_1_when_failures():
    """Assertion that cannot pass → exit 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assertions = [
            {
                "id": "TEST-002",
                "description": "impossible: count equals -1",
                "check": {"path": "component_count", "op": "equals", "value": -1},
            }
        ]
        _write_assertion_file(tmpdir, assertions)
        _write_output_file(tmpdir, {"component_count": 42})

        rc, out = _run_checks(tmpdir)
        assert out is not None, "Expected JSON output from run_checks.py"
        assert out["failed"] == 1, f"Expected 1 failed, got {out}"
        assert rc == 1, f"Expected exit 1, got {rc}"


def test_exit_1_when_errors_no_allow():
    """Output file missing → errors > 0, no --allow-errors → exit 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assertions = [
            {
                "id": "TEST-003",
                "description": "component count in range",
                "check": {"path": "component_count", "op": "range",
                           "min": 1, "max": 999},
            }
        ]
        _write_assertion_file(tmpdir, assertions)
        # Intentionally NO output file written

        rc, out = _run_checks(tmpdir)
        assert out is not None, "Expected JSON output from run_checks.py"
        assert out["errors"] > 0, f"Expected errors > 0, got {out}"
        assert rc == 1, f"Expected exit 1 when errors present without --allow-errors, got {rc}"


def test_exit_1_when_failures_even_with_allow_errors():
    """Failures present even with --allow-errors → exit 1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assertions = [
            {
                "id": "TEST-004",
                "description": "impossible: count equals -1",
                "check": {"path": "component_count", "op": "equals", "value": -1},
            }
        ]
        _write_assertion_file(tmpdir, assertions)
        _write_output_file(tmpdir, {"component_count": 42})

        rc, out = _run_checks(tmpdir, extra_args=["--allow-errors"])
        assert out is not None, "Expected JSON output from run_checks.py"
        assert out["failed"] == 1, f"Expected 1 failed, got {out}"
        assert rc == 1, f"Expected exit 1 even with --allow-errors when failures present, got {rc}"


def test_stray_project_dir_is_skipped_with_warning():
    """TH-035 guard: a project dir with assertions/ but no baselines/ and
    no resolvable project_path should be skipped with a stderr WARNING,
    not silently mis-resolve output file paths via project_prefix("").
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Scenario: we create BOTH a real project dir AND a stray sibling.
        # Real dir has baselines/ + assertions/; stray has only assertions/.
        # Without the guard, run_checks would try to resolve the stray's
        # assertions against a non-existent output file path.

        # Real project: has baselines/metadata.json with project_path
        real_proj = Path(tmpdir) / "reference" / _REPO / "real_proj"
        (real_proj / "baselines").mkdir(parents=True, exist_ok=True)
        (real_proj / "baselines" / "metadata.json").write_text(json.dumps({
            "repo": _REPO, "project": "real_proj",
            "project_path": "real_path",
        }), encoding="utf-8")
        (real_proj / "assertions" / "schematic").mkdir(parents=True, exist_ok=True)
        (real_proj / "assertions" / "schematic" / "a.json").write_text(json.dumps({
            "file_pattern": "real_file",
            "analyzer_type": "schematic",
            "assertions": [{
                "id": "REAL-001",
                "description": "real assertion",
                "check": {"path": "count", "op": "range", "min": 1, "max": 99},
            }],
        }), encoding="utf-8")

        # Stray project: assertions/ but NO baselines/ — no project_path resolvable
        stray_proj = Path(tmpdir) / "reference" / _REPO / "stray_proj"
        (stray_proj / "assertions" / "schematic").mkdir(parents=True, exist_ok=True)
        (stray_proj / "assertions" / "schematic" / "b.json").write_text(json.dumps({
            "file_pattern": "stray_file",
            "analyzer_type": "schematic",
            "assertions": [{
                "id": "STRAY-001",
                "description": "stray assertion (should be skipped)",
                "check": {"path": "count", "op": "range", "min": 1, "max": 99},
            }],
        }), encoding="utf-8")

        # Write output for the real project only
        odir = (Path(tmpdir) / "results" / "outputs" / "schematic"
                / _REPO)
        odir.mkdir(parents=True, exist_ok=True)
        # project_prefix("real_path") = "real_path_" → filename "real_path_real_file.json"
        (odir / "real_path_real_file.json").write_text(json.dumps({"count": 42}),
                                                        encoding="utf-8")

        env = os.environ.copy()
        env["KICAD_HAPPY_TESTHARNESS_DATA_DIR"] = str(tmpdir)
        result = subprocess.run(
            [sys.executable, str(RUN_CHECKS), "--json", "--repo", _REPO],
            capture_output=True, text=True, env=env, timeout=30,
        )
        # Parse JSON
        try:
            out = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            out = None

        assert out is not None, f"Expected JSON output; stdout={result.stdout[:500]}"
        # Real assertion should have run
        assert out["passed"] == 1, (
            f"Expected real assertion to pass (1); got {out}")
        # Stray assertion should NOT have produced errors or failures
        assert out["errors"] == 0, (
            f"Stray dir should be skipped, not errored; got errors={out['errors']}")
        assert out["failed"] == 0, (
            f"Stray dir should be skipped, not failed; got failed={out['failed']}")
        # Stderr must mention the stray skip warning
        assert "stray project dir" in result.stderr.lower(), (
            f"Expected 'stray project dir' warning on stderr; got {result.stderr[:500]}")


def test_exit_0_when_errors_with_allow_flag():
    """Output file missing, --allow-errors → exit 0 (errors tolerated)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        assertions = [
            {
                "id": "TEST-005",
                "description": "component count in range",
                "check": {"path": "component_count", "op": "range",
                           "min": 1, "max": 999},
            }
        ]
        _write_assertion_file(tmpdir, assertions)
        # Intentionally NO output file written

        rc, out = _run_checks(tmpdir, extra_args=["--allow-errors"])
        assert out is not None, "Expected JSON output from run_checks.py"
        assert out["errors"] > 0, f"Expected errors > 0, got {out}"
        assert out["failed"] == 0, f"Expected 0 failures, got {out}"
        assert rc == 0, f"Expected exit 0 when only errors with --allow-errors, got {rc}"


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
