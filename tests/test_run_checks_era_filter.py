"""Tests for --era filter on regression/run_checks.py (A8 read-side).

Builds a tiny synthetic repo + assertions tree in tmp, runs run_checks.py as
a subprocess with --json, asserts the right assertions are included/excluded
in each mode (default / --era pre-v1.4 / --era all).

Runs under bare python3 in the pre-push hook. Each test is a callable
test_* function; main() at bottom runs them all and exits non-zero on any
failure.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

OUTPUT_JSON = {
    "analyzer_type": "schematic",
    "summary": {"total_findings": 2, "by_severity": {"info": 2}},
    "findings": [
        {"detector": "validate_pullups", "rule_id": "PU-001", "severity": "info"},
        {"detector": "detect_rc_filters", "rule_id": "RC-001", "severity": "info"},
    ],
}

ASSERTIONS = [
    # Untagged → runs by default (untagged treated as CURRENT_SCHEMA_ERA)
    {
        "id": "SEED-1",
        "description": "any RC filter",
        "check": {"path": "findings", "detector_filter": "detect_rc_filters",
                  "op": "min_count", "value": 1},
    },
    # Tagged v1.4 → runs in default mode (CURRENT_SCHEMA_ERA), runs in --era v1.4,
    # NOT in --era pre-v1.4
    {
        "id": "SEED-2",
        "description": "any pullup",
        "check": {"path": "findings", "detector_filter": "validate_pullups",
                  "op": "min_count", "value": 1},
        "schema_era": {"era": "v1.4", "tagged_by_rule": "PU-001",
                       "tagged_at": "2026-01-01T00:00:00Z", "tagged_reason": "r"},
    },
    # Tagged pre-v1.4 → NOT in default mode, NOT in --era v1.4, runs in --era pre-v1.4
    {
        "id": "SEED-3",
        "description": "pullup pre-v1.4",
        "check": {"path": "findings", "detector_filter": "validate_pullups",
                  "op": "min_count", "value": 1},
        "schema_era": {"era": "pre-v1.4", "tagged_by_rule": "PU-001",
                       "tagged_at": "2026-01-01T00:00:00Z", "tagged_reason": "r"},
    },
]


def _setup_corpus(tmp: Path) -> None:
    """Create a minimal synthetic corpus under tmp.

    Reference structure: {tmp}/reference/{owner}/{repo}/{project}/...
    Output structure:    {tmp}/results/outputs/{type}/{owner}/{repo}/...
    Repo name:           "fake/demo" (owner=fake, repo=demo, project=demo_proj)
    """
    # Output file under results/outputs/schematic/fake/demo/
    out_dir = tmp / "results" / "outputs" / "schematic" / "fake" / "demo"
    out_dir.mkdir(parents=True)
    (out_dir / "demo.kicad_sch.json").write_text(json.dumps(OUTPUT_JSON))

    # Reference layout: reference/fake/demo/{project}/...
    # project dir name = "demo_proj"
    proj_dir = tmp / "reference" / "fake" / "demo" / "demo_proj"

    # Baselines metadata (so load_assertions doesn't skip the project dir)
    baselines_dir = proj_dir / "baselines"
    baselines_dir.mkdir(parents=True)
    (baselines_dir / "metadata.json").write_text(json.dumps({
        "project_path": ".",
        "project_name": "demo_proj",
    }))

    # Assertion file
    ref_dir = proj_dir / "assertions" / "schematic"
    ref_dir.mkdir(parents=True)
    (ref_dir / "demo.kicad_sch.json").write_text(json.dumps({
        "file_pattern": "demo.kicad_sch",
        "analyzer_type": "schematic",
        "assertions": ASSERTIONS,
    }))


def _run(tmp: Path, *args):
    """Run run_checks.py as a subprocess under tmp as the data root."""
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp)}
    return subprocess.run(
        [sys.executable, str(REPO / "regression" / "run_checks.py"),
         "--repo", "fake/demo", "--json", *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def _result_ids(result) -> set:
    """Parse --json stdout and return the set of assertion IDs in results."""
    data = json.loads(result.stdout)
    return {r["id"] for r in data.get("results", [])}


def test_default_mode_runs_current_and_untagged_not_pre_v14():
    """Default mode: SEED-1 (untagged) + SEED-2 (v1.4 == CURRENT) run; SEED-3 filtered."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stderr}"
        ids = _result_ids(result)
        assert "SEED-1" in ids, f"Expected SEED-1 in results, got: {ids}"
        assert "SEED-2" in ids, f"Expected SEED-2 in results, got: {ids}"
        assert "SEED-3" not in ids, f"Expected SEED-3 filtered out, got: {ids}"


def test_era_v14_same_as_default():
    """--era v1.4 is identical to default (CURRENT_SCHEMA_ERA == v1.4)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--era", "v1.4")
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stderr}"
        ids = _result_ids(result)
        assert "SEED-1" in ids
        assert "SEED-2" in ids
        assert "SEED-3" not in ids


def test_era_pre_v14_runs_only_pre_v14():
    """--era pre-v1.4: only SEED-3 runs (tagged pre-v1.4); others filtered."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--era", "pre-v1.4")
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stderr}"
        ids = _result_ids(result)
        assert "SEED-3" in ids, f"Expected SEED-3 in results, got: {ids}"
        assert "SEED-1" not in ids, f"Expected SEED-1 filtered out, got: {ids}"
        assert "SEED-2" not in ids, f"Expected SEED-2 filtered out, got: {ids}"


def test_era_all_runs_everything():
    """--era all disables filtering: all 3 assertions run."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--era", "all")
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stderr}"
        ids = _result_ids(result)
        for sid in ("SEED-1", "SEED-2", "SEED-3"):
            assert sid in ids, f"Expected {sid} in results with --era all, got: {ids}"


def test_default_mode_total_count():
    """Default mode runs exactly 2 assertions (SEED-1 + SEED-2)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp)
        data = json.loads(result.stdout)
        assert data["total"] == 2, f"Expected total=2, got {data['total']}"


def test_era_all_total_count():
    """--era all runs all 3 assertions."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--era", "all")
        data = json.loads(result.stdout)
        assert data["total"] == 3, f"Expected total=3, got {data['total']}"


def main() -> int:
    tests = [v for k, v in globals().items()
             if k.startswith("test_") and callable(v)]
    failed = []
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            print(f"FAIL {t.__name__}: {type(e).__name__}: {e}")
            failed.append(t.__name__)
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
