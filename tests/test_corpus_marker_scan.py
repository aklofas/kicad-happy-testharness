"""tools/corpus_marker_scan.py: transform token outside strings, line-leading conflict markers."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import corpus_marker_scan as cms  # noqa: E402

pytestmark = pytest.mark.unit


def test_transform_token_counted_only_outside_strings(tmp_path):
    pcb = tmp_path / "b.kicad_pcb"
    pcb.write_text('(kicad_pcb\n (footprint "x"\n  (transform (translate 1 2) (rotate 0) (scale 1 1))\n'
                   '  (property "Note" "(transform here")\n  (transformer 1)\n ))\n')
    assert cms.scan_file(str(pcb)) == (1, [])


def test_conflict_markers_line_leading_only(tmp_path):
    sch = tmp_path / "a.kicad_sch"
    sch.write_text('(kicad_sch\n<<<<<<< HEAD\n (a)\n=======\n (b)\n>>>>>>> branch\n'
                   '  ======= \n (text "<<<<<<< not")\n)\n')
    assert cms.scan_file(str(sch)) == (0, [(2, "<<<<<<<"), (4, "======="), (6, ">>>>>>>")])


def test_legacy_files_need_eeschema_header(tmp_path):
    eagle = tmp_path / "e.sch"
    eagle.write_text('<?xml version="1.0"?>\n<<<<<<< HEAD\n')
    lib = tmp_path / "s.lib"
    lib.write_text("EESchema-LIBRARY Version 2.4\n>>>>>>> x\n")
    assert cms.scan_file(str(eagle)) == (0, [])
    assert cms.scan_file(str(lib)) == (0, [(2, ">>>>>>>")])
    assert cms.main(["--root", str(tmp_path), "--jobs", "1"]) == 0
