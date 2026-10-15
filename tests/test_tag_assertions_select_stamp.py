"""tag_assertions.py: selection era vs stamp era (H0-5 / A4)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

HARNESS_ROOT = Path(__file__).resolve().parents[1]
TOOL = HARNESS_ROOT / "regression" / "tag_assertions.py"
REG_FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "h0" / "plan5" / "registry_dir"


def _assertion(aid, detector):
    return {"id": aid, "description": f"{detector} {aid}",
            "check": {"path": "findings", "detector_filter": detector,
                      "op": "min_count", "value": 1}}


def _corpus(tmp_path: Path, with_v30_registry: bool = True) -> tuple[Path, Path]:
    ref = tmp_path / "reference"
    f = ref / "fake" / "repo1" / "proj" / "assertions" / "schematic" / "a.json"
    f.parent.mkdir(parents=True)
    f.write_text(json.dumps({"file_pattern": "a", "analyzer_type": "schematic",
                             "assertions": [_assertion("SEED-1", "detect_rc_filters"),
                                            _assertion("SEED-2", "validate_pullups")]},
                            indent=2) + "\n")
    reg = tmp_path / "regression"
    reg.mkdir()
    if with_v30_registry:
        shutil.copy(REG_FIXTURE / "v30_changed_detectors.json", reg / "v30_changed_detectors.json")
    (reg / "v14_changed_detectors.json").symlink_to(
        HARNESS_ROOT / "regression" / "v14_changed_detectors.json")
    return ref, reg


def _run(tmp_path, ref, reg, *args):
    env = dict(os.environ)
    env["KICAD_HAPPY_TESTHARNESS_DATA_DIR"] = str(tmp_path / "data")
    return subprocess.run([sys.executable, str(TOOL), "--reference-dir", str(ref),
                           "--registry-dir", str(reg), *args],
                          cwd=str(HARNESS_ROOT), capture_output=True, text=True, env=env)


def _read(ref):
    return json.loads((ref / "fake/repo1/proj/assertions/schematic/a.json").read_text())


def test_select_v30_stamps_v14(tmp_path):
    ref, reg = _corpus(tmp_path)
    res = _run(tmp_path, ref, reg, "--select-era", "v3.0", "--stamp-era", "v1.4", "--apply")
    assert res.returncode == 0, res.stderr
    a = _read(ref)["assertions"]
    assert a[0]["schema_era"]["era"] == "v1.4"
    assert a[0]["schema_era"]["tagged_by_rule"] == "RC-DET"
    assert "schema_era" not in a[1]
    assert "select=v3.0" in res.stdout and "stamp=v1.4" in res.stdout


def test_schema_era_alias_still_works_and_warns(tmp_path):
    ref, reg = _corpus(tmp_path)
    res = _run(tmp_path, ref, reg, "--schema-era", "pre-v1.4", "--apply")
    assert res.returncode == 0, res.stderr
    a = _read(ref)["assertions"]
    assert a[1]["schema_era"]["era"] == "pre-v1.4"
    assert "schema_era" not in a[0]
    assert "deprecated" in (res.stdout + res.stderr).lower()


def test_mixing_alias_and_split_flags_is_an_error(tmp_path):
    ref, reg = _corpus(tmp_path)
    res = _run(tmp_path, ref, reg, "--schema-era", "v1.4", "--select-era", "v3.0", "--apply")
    assert res.returncode == 2
    assert "schema_era" not in _read(ref)["assertions"][0]


def test_missing_select_registry_aborts(tmp_path):
    ref, reg = _corpus(tmp_path, with_v30_registry=False)
    res = _run(tmp_path, ref, reg, "--select-era", "v3.0", "--stamp-era", "v1.4", "--apply")
    assert res.returncode == 2
    assert "v30_changed_detectors.json" in res.stderr
    assert "schema_era" not in _read(ref)["assertions"][0]
    assert "schema_era" not in _read(ref)["assertions"][1]


def test_unknown_stamp_era_aborts(tmp_path):
    ref, reg = _corpus(tmp_path)
    res = _run(tmp_path, ref, reg, "--select-era", "v3.0", "--stamp-era", "v9.9", "--apply")
    assert res.returncode == 2
    assert "v9.9" in res.stderr


def test_dry_run_with_split_flags_writes_nothing(tmp_path):
    ref, reg = _corpus(tmp_path)
    before = (ref / "fake/repo1/proj/assertions/schematic/a.json").read_bytes()
    res = _run(tmp_path, ref, reg, "--select-era", "v3.0", "--stamp-era", "v1.4")
    assert res.returncode == 0
    assert (ref / "fake/repo1/proj/assertions/schematic/a.json").read_bytes() == before
    assert "[DRY-RUN]" in res.stdout
