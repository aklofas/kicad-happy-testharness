"""Tests for tools/batch_review.py."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.batch_review import _output_project_prefix, _collect_outputs


def test_output_project_prefix_schematic():
    assert _output_project_prefix("/x/y/Foo.kicad_sch.json") == "Foo"

def test_output_project_prefix_pcb():
    assert _output_project_prefix("/x/y/Foo.kicad_pcb.json") == "Foo"

def test_output_project_prefix_gerber():
    assert _output_project_prefix("/x/y/Foo_gerber.json") == "Foo"

def test_output_project_prefix_legacy_sch():
    assert _output_project_prefix("/x/y/Bar.sch.json") == "Bar"

def test_output_project_prefix_nested():
    assert _output_project_prefix("/x/sub_dir_Proj.kicad_sch.json") == "sub_dir_Proj"

def test_output_project_prefix_no_match():
    assert _output_project_prefix("/x/y/mystery.json") == "mystery"


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
