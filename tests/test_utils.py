"""Unit tests for utils.py — shared harness utilities."""

TIER = "unit"

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import utils
from utils import project_prefix, resolve_path


# === project_prefix ===

def test_project_prefix_subdir():
    assert project_prefix("sub/dir") == "sub_dir_"

def test_project_prefix_root():
    assert project_prefix(".") == ""

def test_project_prefix_empty():
    assert project_prefix("") == ""

def test_project_prefix_single():
    assert project_prefix("hardware") == "hardware_"

def test_project_prefix_deep():
    assert project_prefix("a/b/c") == "a_b_c_"

def test_project_prefix_backslash():
    assert project_prefix("a\\b") == "a_b_"


# === resolve_path ===

def test_resolve_simple():
    assert resolve_path({"a": 1}, "a") == 1

def test_resolve_nested():
    assert resolve_path({"a": {"b": 2}}, "a.b") == 2

def test_resolve_deep():
    assert resolve_path({"a": {"b": {"c": 3}}}, "a.b.c") == 3

def test_resolve_missing():
    assert resolve_path({"a": 1}, "b") is None

def test_resolve_partial_missing():
    assert resolve_path({"a": {"b": 1}}, "a.c") is None

def test_resolve_empty_data():
    assert resolve_path({}, "a") is None

def test_resolve_list_value():
    data = {"items": [1, 2, 3]}
    assert resolve_path(data, "items") == [1, 2, 3]

def test_resolve_zero_value():
    assert resolve_path({"n": 0}, "n") == 0

def test_resolve_false_value():
    assert resolve_path({"flag": False}, "flag") is False

def test_resolve_none_value():
    assert resolve_path({"x": None}, "x") is None


# === resolve_path bracket notation ===

def test_resolve_bracket_simple():
    data = {"items": [{"name": "a"}, {"name": "b"}]}
    assert resolve_path(data, "items[0].name") == "a"

def test_resolve_bracket_index1():
    data = {"items": [{"name": "a"}, {"name": "b"}]}
    assert resolve_path(data, "items[1].name") == "b"

def test_resolve_bracket_out_of_range():
    data = {"items": [{"name": "a"}]}
    assert resolve_path(data, "items[5].name") is None

def test_resolve_bracket_nested():
    data = {"findings": [{"detector": "detect_crystal_circuits", "frequency": 8000000}]}
    assert resolve_path(data, "findings[0].frequency") == 8000000

def test_resolve_bracket_missing_key():
    data = {"items": [{"name": "a"}]}
    assert resolve_path(data, "missing[0].name") is None

def test_resolve_bracket_not_list():
    data = {"items": "not a list"}
    assert resolve_path(data, "items[0]") is None


# === discover_projects ===

def test_discover_projects_multi_pro_same_dir():
    """Multiple .kicad_pro files in one directory → separate projects."""
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    try:
        # Create a fake repo with 3 .kicad_pro files in one dir
        kicad_dir = os.path.join(tmp, "KiCAD")
        os.makedirs(kicad_dir)
        for name in ["Alpha", "Beta", "Gamma"]:
            with open(os.path.join(kicad_dir, f"{name}.kicad_pro"), "w") as f:
                f.write("{}")

        # Monkey-patch REPOS_DIR to point at parent of our fake repo
        old_repos = utils.REPOS_DIR
        utils.REPOS_DIR = Path(tmp).parent
        # Clear the LRU cache so discover_projects re-scans
        utils.discover_projects.cache_clear()
        try:
            repo_name = Path(tmp).name
            projects = utils.discover_projects(repo_name)
            names = sorted(p["name"] for p in projects)
            # Each .kicad_pro should be its own project
            assert len(projects) == 3, f"Expected 3 projects, got {names}"
            # All names should be unique
            assert len(set(names)) == 3, f"Duplicate names: {names}"
            # All should share the same path
            paths = [p["path"] for p in projects]
            assert all(p == "KiCAD" for p in paths), f"Expected all paths='KiCAD', got {paths}"
            # Stems should be the .kicad_pro basenames
            stems = sorted(p["stem"] for p in projects)
            assert stems == ["Alpha", "Beta", "Gamma"], f"Got stems: {stems}"
        finally:
            utils.REPOS_DIR = old_repos
            utils.discover_projects.cache_clear()
    finally:
        shutil.rmtree(tmp)


# === Runner ===

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
