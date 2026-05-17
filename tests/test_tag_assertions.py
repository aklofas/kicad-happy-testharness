"""Tests for regression/tag_assertions.py (A8 backfill tool).

Builds a synthetic mini-corpus in tmp_path with 4 assertion files
(versioned/unversioned mix), runs the tool, asserts correct tagging.

Runs under bare python3 in the pre-push hook. Each test is a callable
test_* function; main() at bottom runs them all and exits non-zero on any
failure.
"""
from __future__ import annotations

TIER = "unit"

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Versioned detectors known to be in v14_changed_detectors.json
VERSIONED_1 = "validate_pullups"
VERSIONED_2 = "validate_led_resistors"
# Unversioned: does NOT appear in v14_changed_detectors.json
UNVERSIONED = "detect_rc_filters"


def _make_assertion(aid, detector, with_tag=False, tag_era="v1.4"):
    """Build a minimal assertion dict."""
    a = {
        "id": aid,
        "description": f"{detector} assertion {aid}",
        "check": {
            "path": "findings",
            "detector_filter": detector,
            "op": "min_count",
            "value": 1,
        },
    }
    if with_tag:
        a["schema_era"] = {
            "era": tag_era,
            "tagged_by_rule": "PU-001",
            "tagged_at": "2026-01-01T00:00:00Z",
            "tagged_reason": "pre-existing tag",
        }
    return a


def _write_assertion_file(path: Path, assertions: list) -> None:
    """Write an assertion file using the same serialization the tool expects."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "file_pattern": path.stem,
        "analyzer_type": "schematic",
        "assertions": assertions,
    }
    path.write_text(json.dumps(data, indent=2) + "\n")


def _setup_corpus(tmp: Path) -> None:
    """Create a synthetic mini-corpus under tmp/reference/.

    File 1 (repo1): 2 versioned assertions, untagged — both should be tagged after apply
    File 2 (repo2): 1 versioned assertion already tagged v1.4 — skipped unless --force
    File 3 (repo3): 1 unversioned assertion — never tagged
    File 4 (repo4): 1 versioned untagged + 1 unversioned — only versioned gets tagged
    """
    base = tmp / "reference"

    _write_assertion_file(
        base / "fake" / "repo1" / "proj" / "assertions" / "schematic" / "a.json",
        [
            _make_assertion("SEED-1", VERSIONED_1),
            _make_assertion("SEED-2", VERSIONED_2),
        ],
    )
    _write_assertion_file(
        base / "fake" / "repo2" / "proj" / "assertions" / "schematic" / "b.json",
        [
            _make_assertion("SEED-3", VERSIONED_1, with_tag=True, tag_era="v1.4"),
        ],
    )
    _write_assertion_file(
        base / "fake" / "repo3" / "proj" / "assertions" / "schematic" / "c.json",
        [
            _make_assertion("SEED-4", UNVERSIONED),
        ],
    )
    _write_assertion_file(
        base / "fake" / "repo4" / "proj" / "assertions" / "schematic" / "d.json",
        [
            _make_assertion("SEED-5", VERSIONED_1),
            _make_assertion("SEED-6", UNVERSIONED),
        ],
    )

    # Symlink the real v14_changed_detectors.json so schema_era module finds it
    reg_dir = tmp / "regression"
    reg_dir.mkdir(exist_ok=True)
    (reg_dir / "v14_changed_detectors.json").symlink_to(
        REPO / "regression" / "v14_changed_detectors.json"
    )


def _run(tmp: Path, *args) -> subprocess.CompletedProcess:
    """Run tag_assertions.py with --reference-dir and --registry-dir pointing at tmp."""
    return subprocess.run(
        [
            sys.executable,
            str(REPO / "regression" / "tag_assertions.py"),
            "--reference-dir", str(tmp / "reference"),
            "--registry-dir", str(tmp / "regression"),
            *args,
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )


def _read(tmp: Path, repo: str, filename: str) -> dict:
    """Read and parse one of the synthetic assertion files."""
    return json.loads(
        (tmp / "reference" / repo / filename).read_text()
    )


# ---- Tests ----------------------------------------------------------------

def test_dry_run_makes_no_changes():
    """dry-run must not modify any files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        file_path = tmp / "reference" / "fake" / "repo1" / "proj" / "assertions" / "schematic" / "a.json"
        original = file_path.read_text()
        result = _run(tmp, "--schema-era", "pre-v1.4", "--dry-run")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        after = file_path.read_text()
        assert after == original, "dry-run must not write anything"


def test_apply_tags_versioned_untagged():
    """apply tags both versioned untagged assertions in File 1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        data = _read(tmp, "fake/repo1/proj/assertions/schematic", "a.json")
        for a in data["assertions"]:
            assert "schema_era" in a, f"expected schema_era on {a['id']}"
            assert a["schema_era"]["era"] == "pre-v1.4", (
                f"expected pre-v1.4, got {a['schema_era']['era']}"
            )
            assert a["schema_era"]["tagged_by_rule"] is not None, (
                f"tagged_by_rule should be set on {a['id']}"
            )
            assert a["schema_era"]["tagged_at"] is not None, (
                f"tagged_at should be set on {a['id']}"
            )
            assert a["schema_era"]["tagged_reason"] is not None, (
                f"tagged_reason should be set on {a['id']}"
            )


def test_apply_skips_already_tagged():
    """apply leaves SEED-3's existing v1.4 tag intact (not stomped to pre-v1.4)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        data = _read(tmp, "fake/repo2/proj/assertions/schematic", "b.json")
        a = data["assertions"][0]
        assert a["schema_era"]["era"] == "v1.4", (
            f"existing v1.4 tag should be preserved, got: {a['schema_era']['era']}"
        )


def test_apply_skips_unversioned_detectors():
    """apply does not touch File 3 (detect_rc_filters is not versioned)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        data = _read(tmp, "fake/repo3/proj/assertions/schematic", "c.json")
        a = data["assertions"][0]
        assert "schema_era" not in a, (
            f"unversioned detector {UNVERSIONED} should not be tagged"
        )


def test_apply_handles_mixed_file():
    """apply tags only the versioned assertion in the mixed File 4."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        data = _read(tmp, "fake/repo4/proj/assertions/schematic", "d.json")
        versioned_a = data["assertions"][0]   # SEED-5, validate_pullups
        unversioned_a = data["assertions"][1]  # SEED-6, detect_rc_filters
        assert "schema_era" in versioned_a, (
            f"SEED-5 ({VERSIONED_1}) should be tagged"
        )
        assert versioned_a["schema_era"]["era"] == "pre-v1.4"
        assert "schema_era" not in unversioned_a, (
            f"SEED-6 ({UNVERSIONED}) should not be tagged"
        )


def test_force_overwrites_existing_tag():
    """--force overwrites SEED-3's existing v1.4 tag with pre-v1.4."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply", "--force")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"
        data = _read(tmp, "fake/repo2/proj/assertions/schematic", "b.json")
        a = data["assertions"][0]
        assert a["schema_era"]["era"] == "pre-v1.4", (
            f"--force should have overwritten v1.4 → pre-v1.4, got: {a['schema_era']['era']}"
        )


def test_idempotent_second_run_does_nothing():
    """Running apply twice yields byte-identical output on the second run."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        file_path = tmp / "reference" / "fake" / "repo1" / "proj" / "assertions" / "schematic" / "a.json"
        _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        after_first = file_path.read_text()
        _run(tmp, "--schema-era", "pre-v1.4", "--apply")
        after_second = file_path.read_text()
        assert after_first == after_second, (
            "second apply run must produce byte-identical output"
        )


def test_repo_filter_scopes_walk():
    """--repo fake/repo1 only touches repo1; repo4 stays unmodified."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_corpus(tmp)
        repo4_path = tmp / "reference" / "fake" / "repo4" / "proj" / "assertions" / "schematic" / "d.json"
        original_repo4 = repo4_path.read_text()

        result = _run(tmp, "--schema-era", "pre-v1.4", "--apply", "--repo", "fake/repo1")
        assert result.returncode == 0, f"exit {result.returncode}:\n{result.stderr}"

        # repo1 was tagged
        d1 = _read(tmp, "fake/repo1/proj/assertions/schematic", "a.json")
        assert "schema_era" in d1["assertions"][0], "repo1 assertion should be tagged"

        # repo4 is byte-identical (untouched)
        assert repo4_path.read_text() == original_repo4, (
            "repo4 must be untouched when --repo fake/repo1 is specified"
        )


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
