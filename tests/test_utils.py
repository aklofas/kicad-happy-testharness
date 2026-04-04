"""Unit tests for utils.py — shared harness utilities."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
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
    data = {"signal_analysis": {"crystal_circuits": [{"frequency": 8000000}]}}
    assert resolve_path(data, "signal_analysis.crystal_circuits[0].frequency") == 8000000

def test_resolve_bracket_missing_key():
    data = {"items": [{"name": "a"}]}
    assert resolve_path(data, "missing[0].name") is None

def test_resolve_bracket_not_list():
    data = {"items": "not a list"}
    assert resolve_path(data, "items[0]") is None


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
