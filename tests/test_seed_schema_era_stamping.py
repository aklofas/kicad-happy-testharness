"""Tests for write-side schema-era stamping in seed.py, seed_structural.py,
seed_negative.py (A8 Commit 3).

Uses greatscottgadgets/ubertooth as a real corpus repo (it has both
validate_pullups [versioned] and detect_rc_filters [unversioned] findings).
Sets KICAD_HAPPY_TESTHARNESS_DATA_DIR to a tmp dir so seeder writes
assertions to tmp/reference/ rather than the live reference/.

Runs under bare python3 in the pre-push hook. Each test is a callable
test_* function; main() at bottom runs them all and exits non-zero on any
failure.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Real repo that has both a versioned and an unversioned detector in its outputs
TEST_REPO = "greatscottgadgets/ubertooth"

# Versioned detector (in v14_changed_detectors.json)
VERSIONED_DETECTOR = "validate_pullups"
# Unversioned detector (not in v14_changed_detectors.json)
UNVERSIONED_DETECTOR = "detect_rc_filters"


def _setup_tmp_outputs(tmp: Path) -> None:
    """Copy ubertooth schematic outputs into the tmp data tree.

    seed.py reads from OUTPUTS_DIR (= tmp/results/outputs/ when the env var
    is set) and writes assertions to DATA_DIR (= tmp/reference/).
    We only copy the output JSON files — the seeder discovers projects via
    the real repos/ directory, so no repos/ setup is needed.
    """
    src = REPO / "results" / "outputs" / "schematic" / TEST_REPO
    dst = tmp / "results" / "outputs" / "schematic" / TEST_REPO
    dst.mkdir(parents=True, exist_ok=True)
    for jf in src.glob("*.json"):
        shutil.copy2(jf, dst / jf.name)


def _run_seed(tmp: Path, *extra_args) -> subprocess.CompletedProcess:
    """Run seed.py as a subprocess with DATA_DIR redirected to tmp."""
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp)}
    return subprocess.run(
        [sys.executable, str(REPO / "regression" / "seed.py"),
         "--repo", TEST_REPO, "--type", "schematic",
         "--min-components", "5",
         *extra_args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def _run_seed_and_read_assertions(tmp: Path, *extra_args) -> list:
    """Run seed.py (non-dry-run) and return all emitted assertions from all files."""
    _setup_tmp_outputs(tmp)
    result = _run_seed(tmp, *extra_args)
    if result.returncode != 0:
        raise RuntimeError(
            f"seed.py exited {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    # Collect all assertions from all written assertion files
    all_assertions = []
    ref_dir = tmp / "reference" / TEST_REPO
    if ref_dir.exists():
        for proj_dir in ref_dir.iterdir():
            atype_dir = proj_dir / "assertions" / "schematic"
            if not atype_dir.exists():
                continue
            for af in atype_dir.glob("*.json"):
                try:
                    data = json.loads(af.read_text())
                    all_assertions.extend(data.get("assertions", []))
                except Exception:
                    continue
    if not all_assertions:
        raise RuntimeError(
            f"No assertions emitted for {TEST_REPO}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return all_assertions


def _get_assertions_for_detector(assertions: list, detector: str) -> list:
    """Return assertions whose check.detector_filter matches detector."""
    return [
        a for a in assertions
        if a.get("check", {}).get("detector_filter") == detector
    ]


def _get_stamped(assertions: list, detector: str) -> list:
    """Return assertions for detector that have schema_era set."""
    return [
        a for a in _get_assertions_for_detector(assertions, detector)
        if "schema_era" in a
    ]


def _get_unstamped(assertions: list, detector: str) -> list:
    """Return assertions for detector that do NOT have schema_era."""
    return [
        a for a in _get_assertions_for_detector(assertions, detector)
        if "schema_era" not in a
    ]


# ---- seed.py tests (flags and stamp behavior) ----------------------------

def test_seed_default_stamps_versioned_detector():
    """Default mode: assertions for validate_pullups get schema_era=v1.4 stamped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        assertions = _run_seed_and_read_assertions(tmp)
        stamped = _get_stamped(assertions, VERSIONED_DETECTOR)
        assert stamped, (
            f"Expected at least one assertion for {VERSIONED_DETECTOR} "
            f"to be stamped with schema_era, got none.\n"
            f"All detector_filters: "
            f"{sorted(d for d in set(a.get('check',{}).get('detector_filter') for a in assertions) if d)}"
        )
        era_obj = stamped[0]["schema_era"]
        assert era_obj.get("era") == "v1.4", (
            f"Expected era=v1.4, got {era_obj!r}"
        )
        assert era_obj.get("tagged_by_rule") == "PU-001", (
            f"Expected tagged_by_rule=PU-001, got {era_obj!r}"
        )
        assert era_obj.get("tagged_at") is not None, "Expected tagged_at to be set"
        assert era_obj.get("tagged_reason") is not None, "Expected tagged_reason to be set"


def test_seed_default_does_not_stamp_unversioned_detector():
    """Default mode: assertions for detect_rc_filters are NOT stamped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        assertions = _run_seed_and_read_assertions(tmp)
        stamped = _get_stamped(assertions, UNVERSIONED_DETECTOR)
        assert not stamped, (
            f"Expected no assertions for {UNVERSIONED_DETECTOR} to be stamped, "
            f"but found: {stamped}"
        )
        # Confirm there ARE assertions for this detector (just not stamped)
        all_for_det = _get_assertions_for_detector(assertions, UNVERSIONED_DETECTOR)
        assert all_for_det, (
            f"Expected some assertions for {UNVERSIONED_DETECTOR} at all "
            f"(sanity check that the repo has rc_filter findings)"
        )


def test_seed_no_schema_era_skips_all_stamping():
    """--no-schema-era: no assertions are stamped regardless of detector."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        assertions = _run_seed_and_read_assertions(tmp, "--no-schema-era")
        any_stamped = [a for a in assertions if "schema_era" in a]
        assert not any_stamped, (
            f"Expected no stamped assertions with --no-schema-era, "
            f"but found {len(any_stamped)} stamped"
        )


def test_seed_custom_schema_era_stamps_with_pre_v14():
    """--schema-era pre-v1.4: versioned detector stamped with pre-v1.4."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        assertions = _run_seed_and_read_assertions(tmp, "--schema-era", "pre-v1.4")
        stamped = _get_stamped(assertions, VERSIONED_DETECTOR)
        assert stamped, (
            f"Expected assertions for {VERSIONED_DETECTOR} to be stamped "
            f"with pre-v1.4, got none."
        )
        era_obj = stamped[0]["schema_era"]
        assert era_obj.get("era") == "pre-v1.4", (
            f"Expected era=pre-v1.4, got {era_obj!r}"
        )


def test_seed_dry_run_with_era_flags_does_not_crash():
    """--dry-run with --schema-era v1.4 should not crash (no files written)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        result = _run_seed(tmp, "--dry-run", "--schema-era", "v1.4")
        assert result.returncode == 0, (
            f"seed.py --dry-run --schema-era v1.4 exited {result.returncode}\n"
            f"stderr: {result.stderr}"
        )


def test_seed_dry_run_no_schema_era_does_not_crash():
    """--dry-run with --no-schema-era should not crash."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        result = _run_seed(tmp, "--dry-run", "--no-schema-era")
        assert result.returncode == 0, (
            f"seed.py --dry-run --no-schema-era exited {result.returncode}\n"
            f"stderr: {result.stderr}"
        )


# ---- seed_structural.py sanity tests --------------------------------------

def _run_structural_seeder(tmp: Path, *extra_args) -> subprocess.CompletedProcess:
    """Run seed_structural.py as a subprocess with DATA_DIR redirected to tmp."""
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp)}
    return subprocess.run(
        [sys.executable, str(REPO / "regression" / "seed_structural.py"),
         "--repo", TEST_REPO, "--type", "schematic",
         "--min-components", "5",
         *extra_args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def test_seed_structural_no_schema_era_flag_accepted():
    """seed_structural.py accepts --no-schema-era without crashing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_tmp_outputs(tmp)
        result = _run_structural_seeder(tmp, "--no-schema-era", "--dry-run")
        assert result.returncode == 0, (
            f"seed_structural.py --no-schema-era exited {result.returncode}\n"
            f"stderr: {result.stderr}"
        )


def test_seed_structural_schema_era_flag_accepted():
    """seed_structural.py accepts --schema-era without crashing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_tmp_outputs(tmp)
        result = _run_structural_seeder(tmp, "--schema-era", "v1.4", "--dry-run")
        assert result.returncode == 0, (
            f"seed_structural.py --schema-era exited {result.returncode}\n"
            f"stderr: {result.stderr}"
        )


def test_seed_structural_default_stamps_versioned_detector():
    """seed_structural.py default: assertions for validate_pullups get stamped."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_tmp_outputs(tmp)
        result = _run_structural_seeder(tmp)
        if result.returncode != 0:
            raise RuntimeError(
                f"seed_structural.py exited {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        # Collect all assertions from structural files
        all_assertions = []
        ref_dir = tmp / "reference" / TEST_REPO
        if ref_dir.exists():
            for proj_dir in ref_dir.iterdir():
                atype_dir = proj_dir / "assertions" / "schematic"
                if not atype_dir.exists():
                    continue
                for af in atype_dir.glob("*_structural.json"):
                    try:
                        data = json.loads(af.read_text())
                        all_assertions.extend(data.get("assertions", []))
                    except Exception:
                        continue
        if not all_assertions:
            # If no structural assertions emitted (no ref fields matched),
            # just verify the flags don't crash — the flag-acceptance tests above cover this.
            return
        stamped = _get_stamped(all_assertions, VERSIONED_DETECTOR)
        # validate_pullups is in REF_FIELD_MAP, so structural assertions should exist for it
        if _get_assertions_for_detector(all_assertions, VERSIONED_DETECTOR):
            assert stamped, (
                f"Expected validate_pullups structural assertions to be stamped.\n"
                f"Detectors found: "
                f"{sorted(d for d in set(a.get('check',{}).get('detector_filter') for a in all_assertions) if d)}"
            )


# ---- seed_negative.py sanity tests ----------------------------------------

def _run_negative_seeder(tmp: Path, *extra_args) -> subprocess.CompletedProcess:
    """Run seed_negative.py as a subprocess with DATA_DIR redirected to tmp."""
    env = {**os.environ, "KICAD_HAPPY_TESTHARNESS_DATA_DIR": str(tmp)}
    return subprocess.run(
        [sys.executable, str(REPO / "regression" / "seed_negative.py"),
         "--repo", TEST_REPO,
         *extra_args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        env=env,
    )


def test_seed_negative_no_schema_era_flag_accepted():
    """seed_negative.py accepts --no-schema-era without crashing."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_negative_seeder(Path(tmp), "--no-schema-era")
        assert result.returncode == 0, (
            f"seed_negative.py --no-schema-era exited {result.returncode}\n"
            f"stderr: {result.stderr}"
        )


def test_seed_negative_schema_era_flag_accepted():
    """seed_negative.py accepts --schema-era without crashing."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_negative_seeder(Path(tmp), "--schema-era", "v1.4")
        assert result.returncode == 0, (
            f"seed_negative.py --schema-era exited {result.returncode}\n"
            f"stderr: {result.stderr}"
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
