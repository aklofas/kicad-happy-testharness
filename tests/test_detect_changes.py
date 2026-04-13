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
