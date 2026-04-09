"""Unit tests for analysis_cache.py — manifest ops + source hashing."""

TIER = "unit"

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KICAD_HAPPY = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KICAD_HAPPY, "skills", "kicad", "scripts"))
import analysis_cache


# === TestManifestOperations ===

def test_ensure_analysis_dir_creates_dir_and_manifest():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        result = analysis_cache.ensure_analysis_dir(tmpdir, "test.kicad_pro")
        analysis_dir = os.path.join(tmpdir, "analysis")
        assert os.path.isdir(analysis_dir), "analysis/ dir not created"
        manifest_path = os.path.join(analysis_dir, "manifest.json")
        assert os.path.isfile(manifest_path), "manifest.json not created"
        assert result == analysis_dir
    finally:
        shutil.rmtree(tmpdir)


def test_ensure_analysis_dir_creates_gitignore():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(tmpdir, "test.kicad_pro")
        gitignore_path = os.path.join(analysis_dir, ".gitignore")
        assert os.path.isfile(gitignore_path), ".gitignore not created"
        content = open(gitignore_path, encoding="utf-8").read()
        assert "!manifest.json" in content
        assert "!.gitignore" in content
    finally:
        shutil.rmtree(tmpdir)


def test_ensure_analysis_dir_skips_gitignore_when_track_in_git():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        config = {"analysis": {"track_in_git": True}}
        analysis_dir = analysis_cache.ensure_analysis_dir(
            tmpdir, "test.kicad_pro", config=config)
        gitignore_path = os.path.join(analysis_dir, ".gitignore")
        assert not os.path.exists(gitignore_path), \
            ".gitignore should not exist when track_in_git=True"
    finally:
        shutil.rmtree(tmpdir)


def test_fresh_manifest_structure():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            tmpdir, "myproject.kicad_pro")
        manifest = analysis_cache.load_manifest(analysis_dir)
        assert manifest["version"] == 1
        assert manifest["project"] == "myproject.kicad_pro"
        assert manifest["current"] is None
        assert manifest["runs"] == {}
    finally:
        shutil.rmtree(tmpdir)


def test_save_load_manifest_roundtrip():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        os.makedirs(tmpdir, exist_ok=True)
        custom = {
            "version": 1,
            "project": "roundtrip.kicad_pro",
            "current": "2026-01-01_0000",
            "runs": {
                "2026-01-01_0000": {
                    "source_hashes": {"main.kicad_sch": "sha256:abc123"},
                    "outputs": {"schematic": "schematic.json"},
                    "scripts": {"schematic": "analyze_schematic.py"},
                    "generated": "2026-01-01T00:00:00Z",
                    "pinned": False,
                }
            },
        }
        analysis_cache.save_manifest(tmpdir, custom)
        loaded = analysis_cache.load_manifest(tmpdir)
        assert loaded == custom
    finally:
        shutil.rmtree(tmpdir)


def test_ensure_analysis_dir_idempotent():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        analysis_cache.ensure_analysis_dir(tmpdir, "first.kicad_pro")
        analysis_cache.ensure_analysis_dir(tmpdir, "second.kicad_pro")
        analysis_dir = os.path.join(tmpdir, "analysis")
        manifest = analysis_cache.load_manifest(analysis_dir)
        assert manifest["project"] == "first.kicad_pro", \
            "second call should not overwrite project from first call"
    finally:
        shutil.rmtree(tmpdir)


# === TestHashing ===

def test_hash_source_file_format():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        filepath = os.path.join(tmpdir, "test.kicad_sch")
        with open(filepath, "w") as f:
            f.write("(kicad_sch (version 20230121))")
        result = analysis_cache.hash_source_file(filepath)
        assert result is not None
        assert result.startswith("sha256:")
        hex_part = result[len("sha256:"):]
        assert len(hex_part) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", hex_part), \
            f"expected 64 hex chars, got: {hex_part}"
    finally:
        shutil.rmtree(tmpdir)


def test_hash_source_file_deterministic():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        filepath = os.path.join(tmpdir, "test.kicad_sch")
        with open(filepath, "w") as f:
            f.write("(kicad_sch (version 20230121))")
        h1 = analysis_cache.hash_source_file(filepath)
        h2 = analysis_cache.hash_source_file(filepath)
        assert h1 == h2
    finally:
        shutil.rmtree(tmpdir)


def test_hash_source_file_missing_returns_none():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        result = analysis_cache.hash_source_file(
            os.path.join(tmpdir, "nonexistent.kicad_sch"))
        assert result is None
    finally:
        shutil.rmtree(tmpdir)


def test_sources_changed_detects_modification():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        filepath = os.path.join(tmpdir, "main.kicad_sch")
        with open(filepath, "w") as f:
            f.write("original content")
        old_hash = analysis_cache.hash_source_file(filepath)
        old_hashes = {"main.kicad_sch": old_hash}
        # Modify the file
        with open(filepath, "w") as f:
            f.write("modified content")
        assert analysis_cache.sources_changed(old_hashes, tmpdir) is True
    finally:
        shutil.rmtree(tmpdir)


def test_sources_changed_false_when_unchanged():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        filepath = os.path.join(tmpdir, "main.kicad_sch")
        with open(filepath, "w") as f:
            f.write("stable content")
        old_hash = analysis_cache.hash_source_file(filepath)
        old_hashes = {"main.kicad_sch": old_hash}
        assert analysis_cache.sources_changed(old_hashes, tmpdir) is False
    finally:
        shutil.rmtree(tmpdir)


# === TestRunCreation ===

def test_generate_run_id_format():
    run_id = analysis_cache.generate_run_id()
    parts = run_id.split("_")
    assert len(parts) == 2, f"expected 2 parts separated by _, got {parts}"
    date_part, time_part = parts
    assert len(date_part) == 10, f"date part should be 10 chars, got {len(date_part)}"
    assert len(time_part) == 4, f"time part should be 4 chars, got {len(time_part)}"


def test_generate_run_id_deduplicates():
    tmpdir = tempfile.mkdtemp(prefix="test_ac_")
    try:
        first_id = analysis_cache.generate_run_id(tmpdir)
        # Create a folder with that ID so the next call must deduplicate
        os.makedirs(os.path.join(tmpdir, first_id))
        second_id = analysis_cache.generate_run_id(tmpdir)
        assert second_id != first_id, \
            f"second ID should differ from first, both are {first_id}"
        assert second_id.startswith(first_id.split("-")[0]), \
            "deduped ID should share the base timestamp"
    finally:
        shutil.rmtree(tmpdir)


def test_create_run_creates_folder_and_updates_manifest():
    project_dir = tempfile.mkdtemp(prefix="test_ac_proj_")
    outputs_dir = tempfile.mkdtemp(prefix="test_ac_out_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        # Create a fake schematic output
        with open(os.path.join(outputs_dir, "schematic.json"), "w") as f:
            json.dump({"analyzer_type": "schematic", "components": []}, f)
        hashes = {"main.kicad_sch": "sha256:abc123"}
        rid = analysis_cache.create_run(
            analysis_dir, outputs_dir, hashes,
            scripts={"schematic": "analyze_schematic.py"},
            run_id="2026-04-09_test")
        assert rid == "2026-04-09_test"
        # Verify folder exists
        run_dir = os.path.join(analysis_dir, rid)
        assert os.path.isdir(run_dir), "run folder not created"
        # Verify schematic.json was copied
        assert os.path.isfile(os.path.join(run_dir, "schematic.json"))
        # Verify manifest updated
        manifest = analysis_cache.load_manifest(analysis_dir)
        assert manifest["current"] == rid
        assert manifest["runs"][rid]["source_hashes"] == hashes
        assert "schematic" in manifest["runs"][rid]["outputs"]
    finally:
        shutil.rmtree(project_dir)
        shutil.rmtree(outputs_dir)


def test_create_run_copies_forward_previous_outputs():
    project_dir = tempfile.mkdtemp(prefix="test_ac_proj_")
    outputs_dir_1 = tempfile.mkdtemp(prefix="test_ac_out1_")
    outputs_dir_2 = tempfile.mkdtemp(prefix="test_ac_out2_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        # Run 1: pcb.json only
        with open(os.path.join(outputs_dir_1, "pcb.json"), "w") as f:
            json.dump({"analyzer_type": "pcb", "footprints": []}, f)
        analysis_cache.create_run(
            analysis_dir, outputs_dir_1,
            source_hashes={"board.kicad_pcb": "sha256:aaa"},
            scripts={"pcb": "analyze_pcb.py"},
            run_id="run1")
        # Run 2: schematic.json only
        with open(os.path.join(outputs_dir_2, "schematic.json"), "w") as f:
            json.dump({"analyzer_type": "schematic", "components": []}, f)
        analysis_cache.create_run(
            analysis_dir, outputs_dir_2,
            source_hashes={"main.kicad_sch": "sha256:bbb"},
            scripts={"schematic": "analyze_schematic.py"},
            run_id="run2")
        # Run 2 should have both files: pcb.json copied forward + schematic.json
        run2_dir = os.path.join(analysis_dir, "run2")
        assert os.path.isfile(os.path.join(run2_dir, "pcb.json")), \
            "pcb.json should be copied forward from run1"
        assert os.path.isfile(os.path.join(run2_dir, "schematic.json")), \
            "schematic.json should exist in run2"
    finally:
        shutil.rmtree(project_dir)
        shutil.rmtree(outputs_dir_1)
        shutil.rmtree(outputs_dir_2)


def test_overwrite_current_updates_in_place():
    project_dir = tempfile.mkdtemp(prefix="test_ac_proj_")
    outputs_dir = tempfile.mkdtemp(prefix="test_ac_out_")
    overwrite_dir = tempfile.mkdtemp(prefix="test_ac_ow_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        # Create initial run
        with open(os.path.join(outputs_dir, "schematic.json"), "w") as f:
            json.dump({"version": 1}, f)
        analysis_cache.create_run(
            analysis_dir, outputs_dir,
            source_hashes={"main.kicad_sch": "sha256:v1"},
            scripts={"schematic": "analyze_schematic.py"},
            run_id="2026-04-09_0001")
        # Overwrite with new content
        with open(os.path.join(overwrite_dir, "schematic.json"), "w") as f:
            json.dump({"version": 2}, f)
        analysis_cache.overwrite_current(
            analysis_dir, overwrite_dir,
            source_hashes={"main.kicad_sch": "sha256:v2"})
        # Verify same run ID
        manifest = analysis_cache.load_manifest(analysis_dir)
        assert manifest["current"] == "2026-04-09_0001"
        assert len(manifest["runs"]) == 1
        # Verify file content updated
        run_file = os.path.join(analysis_dir, "2026-04-09_0001", "schematic.json")
        with open(run_file) as f:
            data = json.load(f)
        assert data["version"] == 2, "file content should be updated"
    finally:
        shutil.rmtree(project_dir)
        shutil.rmtree(outputs_dir)
        shutil.rmtree(overwrite_dir)


def test_overwrite_current_updates_source_hashes():
    project_dir = tempfile.mkdtemp(prefix="test_ac_proj_")
    outputs_dir = tempfile.mkdtemp(prefix="test_ac_out_")
    overwrite_dir = tempfile.mkdtemp(prefix="test_ac_ow_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        # Create initial run with hash v1
        with open(os.path.join(outputs_dir, "schematic.json"), "w") as f:
            json.dump({"ok": True}, f)
        analysis_cache.create_run(
            analysis_dir, outputs_dir,
            source_hashes={"main.kicad_sch": "sha256:hash_v1"},
            scripts={"schematic": "analyze_schematic.py"},
            run_id="2026-04-09_0002")
        # Overwrite with hash v2
        with open(os.path.join(overwrite_dir, "schematic.json"), "w") as f:
            json.dump({"ok": True}, f)
        analysis_cache.overwrite_current(
            analysis_dir, overwrite_dir,
            source_hashes={"main.kicad_sch": "sha256:hash_v2"})
        # Verify manifest has v2
        manifest = analysis_cache.load_manifest(analysis_dir)
        run_entry = manifest["runs"]["2026-04-09_0002"]
        assert run_entry["source_hashes"]["main.kicad_sch"] == "sha256:hash_v2"
    finally:
        shutil.rmtree(project_dir)
        shutil.rmtree(outputs_dir)
        shutil.rmtree(overwrite_dir)


def test_get_current_run_returns_path_and_metadata():
    project_dir = tempfile.mkdtemp(prefix="test_ac_proj_")
    outputs_dir = tempfile.mkdtemp(prefix="test_ac_out_")
    try:
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        with open(os.path.join(outputs_dir, "schematic.json"), "w") as f:
            json.dump({"analyzer_type": "schematic"}, f)
        analysis_cache.create_run(
            analysis_dir, outputs_dir,
            source_hashes={"main.kicad_sch": "sha256:abc"},
            scripts={"schematic": "analyze_schematic.py"},
            run_id="2026-04-09_0003")
        result = analysis_cache.get_current_run(analysis_dir)
        assert result is not None, "get_current_run should return a result"
        path, metadata = result
        assert os.path.isdir(path), "returned path should be a directory"
        assert path.endswith("2026-04-09_0003")
        assert "source_hashes" in metadata
        assert "outputs" in metadata
        assert metadata["source_hashes"]["main.kicad_sch"] == "sha256:abc"
    finally:
        shutil.rmtree(project_dir)
        shutil.rmtree(outputs_dir)


# === Helpers for retention tests ===

def _create_numbered_runs(adir, count, pinned=None):
    """Create `count` runs with sequential IDs, optionally pin some."""
    if pinned is None:
        pinned = set()
    for i in range(count):
        rid = f"run{i:03d}"
        out = tempfile.mkdtemp(prefix="test_out_")
        with open(os.path.join(out, "schematic.json"), "w") as f:
            json.dump({"run": i}, f)
        analysis_cache.create_run(adir, out, source_hashes={}, scripts={}, run_id=rid)
        shutil.rmtree(out)
        if i in pinned:
            analysis_cache.pin_run(adir, rid)


# === TestRetentionPruning ===

def test_prune_runs_removes_oldest_beyond_retention():
    project_dir = tempfile.mkdtemp(prefix="test_ac_prune_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        _create_numbered_runs(adir, 7)
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["current"] == "run006", "current should be last created"
        pruned = analysis_cache.prune_runs(adir, retention=5)
        assert len(pruned) == 2, f"expected 2 pruned, got {len(pruned)}"
        assert "run000" in pruned
        assert "run001" in pruned
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["current"] == "run006", "current must survive"
        for rid in pruned:
            assert rid not in manifest["runs"], f"{rid} should be removed"
            assert not os.path.isdir(os.path.join(adir, rid)), \
                f"{rid} folder should be deleted"
    finally:
        shutil.rmtree(project_dir)


def test_prune_runs_preserves_pinned():
    project_dir = tempfile.mkdtemp(prefix="test_ac_pin_prune_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        _create_numbered_runs(adir, 7, pinned={0, 1})
        pruned = analysis_cache.prune_runs(adir, retention=3)
        manifest = analysis_cache.load_manifest(adir)
        # Pinned runs must survive
        assert "run000" in manifest["runs"], "pinned run000 should survive"
        assert "run001" in manifest["runs"], "pinned run001 should survive"
        # Current (run006) must survive
        assert manifest["current"] == "run006"
        assert "run006" in manifest["runs"], "current run006 should survive"
        # Pinned runs must not be in pruned list
        assert "run000" not in pruned
        assert "run001" not in pruned
        assert "run006" not in pruned
    finally:
        shutil.rmtree(project_dir)


def test_prune_runs_noop_under_limit():
    project_dir = tempfile.mkdtemp(prefix="test_ac_noop_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        _create_numbered_runs(adir, 3)
        pruned = analysis_cache.prune_runs(adir, retention=5)
        assert pruned == [], f"expected no pruning, got {pruned}"
        manifest = analysis_cache.load_manifest(adir)
        assert len(manifest["runs"]) == 3
    finally:
        shutil.rmtree(project_dir)


def test_prune_runs_zero_retention_keeps_all():
    project_dir = tempfile.mkdtemp(prefix="test_ac_zero_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        _create_numbered_runs(adir, 5)
        pruned = analysis_cache.prune_runs(adir, retention=0)
        assert pruned == [], "retention=0 means unlimited, no pruning"
        manifest = analysis_cache.load_manifest(adir)
        assert len(manifest["runs"]) == 5
    finally:
        shutil.rmtree(project_dir)


def test_pin_unpin_toggles_flag():
    project_dir = tempfile.mkdtemp(prefix="test_ac_toggle_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        out = tempfile.mkdtemp(prefix="test_out_")
        with open(os.path.join(out, "schematic.json"), "w") as f:
            json.dump({"ok": True}, f)
        analysis_cache.create_run(adir, out, source_hashes={}, scripts={},
                                  run_id="toggle_run")
        shutil.rmtree(out)
        # Initially unpinned
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["runs"]["toggle_run"].get("pinned", False) is False
        # Pin
        analysis_cache.pin_run(adir, "toggle_run")
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["runs"]["toggle_run"]["pinned"] is True
        # Unpin
        analysis_cache.unpin_run(adir, "toggle_run")
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["runs"]["toggle_run"]["pinned"] is False
    finally:
        shutil.rmtree(project_dir)


def test_prune_never_removes_current():
    project_dir = tempfile.mkdtemp(prefix="test_ac_keep_cur_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        _create_numbered_runs(adir, 7)
        pruned = analysis_cache.prune_runs(adir, retention=1)
        manifest = analysis_cache.load_manifest(adir)
        assert manifest["current"] == "run006", "current must survive"
        assert "run006" in manifest["runs"]
        assert os.path.isdir(os.path.join(adir, "run006")), \
            "current run folder must survive"
        assert "run006" not in pruned
    finally:
        shutil.rmtree(project_dir)


# === TestNewRunDecision ===

def test_should_create_new_run_true_when_no_current():
    project_dir = tempfile.mkdtemp(prefix="test_ac_newrun_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        out = tempfile.mkdtemp(prefix="test_out_")
        with open(os.path.join(out, "schematic.json"), "w") as f:
            json.dump({"analyzer_type": "schematic"}, f)
        result = analysis_cache.should_create_new_run(adir, out)
        assert result is True, "should return True when no current run exists"
        shutil.rmtree(out)
    finally:
        shutil.rmtree(project_dir)


def test_get_current_run_none_when_empty():
    project_dir = tempfile.mkdtemp(prefix="test_ac_empty_")
    try:
        adir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")
        result = analysis_cache.get_current_run(adir)
        assert result is None, "should return None when no runs exist"
    finally:
        shutil.rmtree(project_dir)


# === Runner ===

if __name__ == "__main__":
    import inspect
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
