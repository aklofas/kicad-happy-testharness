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
