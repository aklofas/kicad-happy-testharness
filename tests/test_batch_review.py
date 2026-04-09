"""Tests for tools/batch_review.py."""
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
