"""Unit tests for validate/validate_schema.py and checks.py assertion validation."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))

from validate_schema import (
    _collect_fields, scan_schematic_outputs, diff_inventories, build_inventory,
)
from checks import KNOWN_OPS, validate_assertion_structure


# === _collect_fields ===

def test_collect_fields_basic():
    items = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    fields = _collect_fields(items)
    assert fields == {"a": 2, "b": 1, "c": 1}

def test_collect_fields_empty():
    assert _collect_fields([]) == {}

def test_collect_fields_non_dict():
    assert _collect_fields(["string", 42, None]) == {}

def test_collect_fields_mixed():
    items = [{"a": 1}, "not a dict", {"b": 2}]
    fields = _collect_fields(items)
    assert fields == {"a": 1, "b": 1}


# === diff_inventories ===

def test_diff_no_changes():
    inv = {"schematic": {"voltage_dividers": {"ratio": 10, "r_top": 10}}, "pcb": {}}
    changes = diff_inventories(inv, inv)
    assert changes == []

def test_diff_added_field():
    saved = {"schematic": {"rc_filters": {"cutoff_hz": 5}}, "pcb": {}}
    current = {"schematic": {"rc_filters": {"cutoff_hz": 5, "new_field": 3}}, "pcb": {}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "added"
    assert changes[0]["field"] == "new_field"
    assert changes[0]["detector"] == "rc_filters"

def test_diff_removed_field():
    saved = {"schematic": {"rc_filters": {"cutoff_hz": 5, "old_field": 3}}, "pcb": {}}
    current = {"schematic": {"rc_filters": {"cutoff_hz": 5}}, "pcb": {}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "removed"
    assert changes[0]["field"] == "old_field"

def test_diff_rename_heuristic():
    """When a field is removed and another added in same detector, flag as possible rename."""
    saved = {"schematic": {"rc_filters": {"cutoff_hz": 5}}, "pcb": {}}
    current = {"schematic": {"rc_filters": {"fc_hz": 5}}, "pcb": {}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 2
    removed = [c for c in changes if c["change_type"] == "removed"][0]
    assert "possible rename" in removed["details"]

def test_diff_new_detector():
    saved = {"schematic": {}, "pcb": {}}
    current = {"schematic": {"new_detector": {"field1": 3}}, "pcb": {}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "new_detector"
    assert changes[0]["detector"] == "new_detector"

def test_diff_removed_detector():
    saved = {"schematic": {"old_detector": {"field1": 3}}, "pcb": {}}
    current = {"schematic": {}, "pcb": {}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "removed_detector"
    assert changes[0]["detector"] == "old_detector"

def test_diff_pcb_changes():
    saved = {"schematic": {}, "pcb": {"dfm.vias": {"drill": 10}}}
    current = {"schematic": {}, "pcb": {"dfm.vias": {"drill": 10, "tenting": 5}}}
    changes = diff_inventories(saved, current)
    assert len(changes) == 1
    assert changes[0]["category"] == "pcb"
    assert changes[0]["field"] == "tenting"

def test_diff_empty_inventories():
    changes = diff_inventories(
        {"schematic": {}, "pcb": {}},
        {"schematic": {}, "pcb": {}},
    )
    assert changes == []


# === KNOWN_OPS ===

def test_known_ops_contains_all():
    expected = {
        "range", "min_count", "max_count", "equals", "exists", "not_exists",
        "greater_than", "less_than", "field_equals", "contains_match",
        "not_contains_match", "count_matches",
    }
    assert KNOWN_OPS == expected

def test_known_ops_is_frozen():
    assert isinstance(KNOWN_OPS, frozenset)


# === validate_assertion_structure ===

def test_valid_assertion():
    a = {"id": "SEED-1", "description": "test", "check": {"path": "x", "op": "exists"}}
    assert validate_assertion_structure(a) == []

def test_missing_id():
    a = {"description": "test", "check": {"path": "x", "op": "exists"}}
    warnings = validate_assertion_structure(a)
    assert any("missing 'id'" in w for w in warnings)

def test_missing_description():
    a = {"id": "SEED-1", "check": {"path": "x", "op": "exists"}}
    warnings = validate_assertion_structure(a)
    assert any("missing 'description'" in w for w in warnings)

def test_missing_check():
    a = {"id": "SEED-1", "description": "test"}
    warnings = validate_assertion_structure(a)
    assert any("missing or invalid 'check'" in w for w in warnings)

def test_missing_path():
    a = {"id": "SEED-1", "description": "test", "check": {"op": "exists"}}
    warnings = validate_assertion_structure(a)
    assert any("missing 'path'" in w for w in warnings)

def test_missing_op():
    a = {"id": "SEED-1", "description": "test", "check": {"path": "x"}}
    warnings = validate_assertion_structure(a)
    assert any("missing 'op'" in w for w in warnings)

def test_unknown_op():
    a = {"id": "SEED-1", "description": "test", "check": {"path": "x", "op": "bogus"}}
    warnings = validate_assertion_structure(a)
    assert any("unknown operator 'bogus'" in w for w in warnings)

def test_all_known_ops_valid():
    for op in KNOWN_OPS:
        a = {"id": "T-1", "description": "t", "check": {"path": "x", "op": op}}
        assert validate_assertion_structure(a) == [], f"op '{op}' flagged as invalid"

def test_source_file_in_warning():
    a = {"id": "SEED-1", "check": {"path": "x", "op": "bogus"}}
    warnings = validate_assertion_structure(a, source_file="test.json")
    assert any("test.json" in w for w in warnings)

def test_non_dict_assertion():
    warnings = validate_assertion_structure("not a dict")
    assert any("not a dict" in w for w in warnings)


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
