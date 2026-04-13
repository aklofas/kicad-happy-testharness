"""Unit tests for tools/generate_catalog.py — _parse_query and _match_entry."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from generate_catalog import _parse_query, _match_entry


# --- _parse_query ---

def test_parse_query_equals():
    clauses = _parse_query("category=ESP32")
    assert clauses == [("category", "=", "ESP32")]


def test_parse_query_contains():
    clauses = _parse_query("tags contains rf")
    assert clauses == [("tags", "contains", "rf")]


def test_parse_query_gt():
    clauses = _parse_query("quality.emc>70")
    assert clauses == [("quality.emc", ">", 70.0)]


def test_parse_query_gte():
    clauses = _parse_query("complexity.total_components>=100")
    assert len(clauses) == 1
    field, op, val = clauses[0]
    assert field == "complexity.total_components"
    assert op == ">="
    assert val == 100.0


def test_parse_query_multiple_and():
    clauses = _parse_query("category=ESP32 AND quality.emc>50")
    assert len(clauses) == 2
    assert clauses[0] == ("category", "=", "ESP32")
    assert clauses[1][1] == ">"


def test_parse_query_empty():
    clauses = _parse_query("")
    assert clauses == []


def test_parse_query_in_operator():
    # "kicad9 in kicad_versions"
    clauses = _parse_query("kicad9 in kicad_versions")
    assert clauses == [("kicad_versions", "in", "kicad9")]


# --- _match_entry ---

SAMPLE_ENTRY = {
    "repo": "user/myboard",
    "category": "ESP32",
    "tags": ["rf", "medium", "kicad8"],
    "quality": {"emc": 80, "bom": 70, "routing": None},
    "complexity": {"total_components": 150, "pcb_layers_max": 4},
    "kicad_versions": ["7.0.5", "8.0.0"],
}


def test_match_equals_hit():
    clauses = _parse_query("category=ESP32")
    assert _match_entry(SAMPLE_ENTRY, clauses) is True


def test_match_equals_miss():
    clauses = _parse_query("category=STM32")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


def test_match_contains_hit():
    clauses = _parse_query("tags contains rf")
    assert _match_entry(SAMPLE_ENTRY, clauses) is True


def test_match_contains_miss():
    clauses = _parse_query("tags contains fpga")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


def test_match_gt_hit():
    clauses = _parse_query("quality.emc>70")
    assert _match_entry(SAMPLE_ENTRY, clauses) is True


def test_match_gt_miss():
    clauses = _parse_query("quality.emc>90")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


def test_match_none_field_gt():
    # quality.routing is None — comparison should return False
    clauses = _parse_query("quality.routing>50")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


def test_match_multiple_clauses_all_true():
    clauses = _parse_query("category=ESP32 AND quality.emc>70")
    assert _match_entry(SAMPLE_ENTRY, clauses) is True


def test_match_multiple_clauses_one_false():
    clauses = _parse_query("category=ESP32 AND quality.emc>90")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


def test_match_in_operator():
    clauses = _parse_query("7.0.5 in kicad_versions")
    assert _match_entry(SAMPLE_ENTRY, clauses) is True


def test_match_in_operator_miss():
    clauses = _parse_query("9.0.0 in kicad_versions")
    assert _match_entry(SAMPLE_ENTRY, clauses) is False


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
