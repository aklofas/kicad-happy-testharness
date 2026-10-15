"""Unit tests for tools/detect_changes.py — map_file_to_types."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from detect_changes import map_file_to_types


# --- Exact-match entries from FILE_TO_TYPES ---

def test_analyze_schematic():
    result = map_file_to_types("skills/kicad/scripts/analyze_schematic.py")
    assert result == {"schematic"}


def test_signal_detectors():
    result = map_file_to_types("skills/kicad/scripts/signal_detectors.py")
    assert result == {"schematic"}


def test_analyze_pcb():
    result = map_file_to_types("skills/kicad/scripts/analyze_pcb.py")
    assert result == {"pcb"}


def test_analyze_gerbers():
    result = map_file_to_types("skills/kicad/scripts/analyze_gerbers.py")
    assert result == {"gerber"}


def test_analyze_emc_script():
    result = map_file_to_types("skills/emc/scripts/analyze_emc.py")
    assert result == {"emc"}


def test_emc_rules():
    result = map_file_to_types("skills/emc/scripts/emc_rules.py")
    assert result == {"emc"}


def test_simulate_subcircuits():
    result = map_file_to_types("skills/spice/scripts/simulate_subcircuits.py")
    assert result == {"spice"}


def test_kicad_utils_multi_type():
    result = map_file_to_types("skills/kicad/scripts/kicad_utils.py")
    assert "schematic" in result
    assert "pcb" in result
    assert "spice" in result


def test_diff_analysis_no_impact():
    # diff_analysis.py is explicitly mapped to empty set
    result = map_file_to_types("skills/kicad/scripts/diff_analysis.py")
    assert result == set()


# --- Glob pattern matches ---

def test_emc_glob_new_file():
    # Any new file under skills/emc/ should map to emc
    result = map_file_to_types("skills/emc/scripts/new_helper.py")
    assert result == {"emc"}


def test_spice_glob_new_file():
    result = map_file_to_types("skills/spice/scripts/spice_utils.py")
    assert result == {"spice"}


def test_kicad_scripts_glob():
    result = map_file_to_types("skills/kicad/scripts/kicad_helpers.py")
    assert "schematic" in result
    assert "pcb" in result


# --- Unknown / unrelated files ---

def test_unknown_file_returns_empty():
    result = map_file_to_types("README.md")
    assert result == set()


def test_unknown_path_returns_empty():
    result = map_file_to_types("docs/some/doc.txt")
    assert result == set()


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


import json
import os
import subprocess
import tempfile

import detect_changes as dc

FAKE = Path(__file__).resolve().parent / "fixtures" / "h0" / "plan4" / "fake_product"


def test_module_index_is_package_qualified():
    idx = dc.build_module_index(FAKE)
    assert idx["schematic.reader"] == "skills/kicad/scripts/schematic/reader.py"
    assert idx["pcb.reader"] == "skills/kicad/scripts/pcb/reader.py"
    assert idx["schematic"] == "skills/kicad/scripts/schematic/__init__.py"
    assert idx["datasheet_types"] == "skills/datasheets/datasheet_types/__init__.py"
    assert idx["analyze_schematic"] == "skills/kicad/scripts/analyze_schematic.py"


def test_graph_resolves_absolute_relative_and_package_imports():
    g = dc._build_dependency_graph(FAKE)
    assert "skills/kicad/scripts/schematic/reader.py" in g["skills/kicad/scripts/analyze_schematic.py"]
    # relative import inside the package: from ..finding_schema import make_finding
    assert "skills/kicad/scripts/finding_schema.py" in g["skills/kicad/scripts/schematic/reader.py"]
    assert "skills/kicad/scripts/pcb/__init__.py" in g["skills/kicad/scripts/analyze_thermal.py"]
    assert "skills/datasheets/datasheet_types/__init__.py" in g["skills/datasheets/scripts/datasheet_lookup.py"]


def test_impact_map_reaches_nested_and_thermal():
    g = dc._build_dependency_graph(FAKE)
    impact = dc._compute_impact_map(g, dc.ENTRY_POINTS)
    assert impact["skills/kicad/scripts/schematic/reader.py"] == {"schematic"}
    assert impact["skills/kicad/scripts/pcb/reader.py"] == {"thermal"}
    assert impact["skills/kicad/scripts/pcb/__init__.py"] == {"thermal"}
    assert impact["skills/datasheets/datasheet_types/__init__.py"] == {"datasheets"}


def test_entry_points_cover_all_six_analyzer_families():
    types = set()
    for v in dc.ENTRY_POINTS.values():
        types |= set(v) if isinstance(v, (set, frozenset, list, tuple)) else {v}
    assert {"schematic", "pcb", "gerber", "emc", "spice", "thermal", "datasheets"} <= types


def test_syntax_error_is_parse_incomplete_not_no_change(tmp_path):
    assert dc._extract_functions("def broken(:\n") is None
    assert dc._extract_functions("") == {}


def test_git_failure_is_diagnostic_exit_2(tmp_path):
    # a directory that is not a git repo: git diff must fail -> exit 2, not "No changes"
    (tmp_path / "skills").mkdir()
    tool = Path(__file__).resolve().parent.parent / "tools" / "detect_changes.py"
    r = subprocess.run([sys.executable, str(tool), "--json"], capture_output=True, text=True,
                       env={**os.environ, "KICAD_HAPPY_DIR": str(tmp_path)})
    assert r.returncode == 2, r.stdout + r.stderr
    assert "git" in r.stderr.lower()


def test_relative_import_in_sibling_package_resolves():
    g = dc._build_dependency_graph(FAKE)
    init = "skills/datasheets/datasheet_types/__init__.py"
    base = "skills/datasheets/datasheet_types/base_block.py"
    assert base in g[init]
    impact = dc._compute_impact_map(g, dc.ENTRY_POINTS)
    assert impact[base] == {"datasheets"}


def test_dot_import_inside_package_init_resolves():
    g = dc._build_dependency_graph(FAKE)
    assert "skills/kicad/scripts/schematic/reader.py" in g["skills/kicad/scripts/schematic/__init__.py"]


def test_collision_keeps_both_files_as_nodes_and_warns(tmp_path, capsys):
    for sk in ("a", "b"):
        d = tmp_path / "skills" / sk / "scripts"
        d.mkdir(parents=True)
        (d / "x.py").write_text("")
    g = dc._build_dependency_graph(tmp_path)
    assert "skills/a/scripts/x.py" in g and "skills/b/scripts/x.py" in g
    err = capsys.readouterr().err
    assert "skills/a/scripts/x.py" in err and "skills/b/scripts/x.py" in err


def test_datasheets_prefix_covers_standalone_scripts():
    f = "skills/datasheets/scripts/validate_sanity_vector.py"
    assert (FAKE / f).exists()
    assert dc.map_file_to_types(f) == {"datasheets"}


def test_relative_import_above_root_resolves_to_nothing():
    import ast
    idx = dc.build_module_index(FAKE)
    node = ast.parse("from ... import reader").body[0]
    assert dc.resolve_import("skills/kicad/scripts/schematic/reader.py", node, idx) == set()
    node = ast.parse("from .. import finding_schema").body[0]
    assert dc.resolve_import("skills/kicad/scripts/analyze_schematic.py", node, idx) == set()


def test_from_import_walks_up_to_indexed_prefix():
    import ast
    idx = dc.build_module_index(FAKE)
    node = ast.parse("from schematic.nothing_here import y").body[0]
    assert dc.resolve_import("skills/kicad/scripts/analyze_schematic.py", node, idx) == \
        {"skills/kicad/scripts/schematic/__init__.py"}
