"""audit_constants never reuses a CONST-NNN number (TH-110).

A retired constant is popped from the registry, so the id allocator must keep a
high-water mark (`next_id` in the registry header) instead of filling gaps.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_constants as ac  # noqa: E402

pytestmark = pytest.mark.unit


def _entry(name, cid):
    return {"id": cid, "file": "m.py", "scope": "module", "function": None, "name": name,
            "line": 1, "end_line": 1, "type": "keyword_set", "entry_count": 3,
            "content_hash": f"sha256:{name}", "status": "unverified", "source": None,
            "notes": None, "verified_entries": 0}


def _info(name):
    return ac.ConstantInfo(name=name, file="m.py", line=1, scope="module", func=None,
                           const_type="keyword_set", entry_count=3, content_hash=f"sha256:{name}")


def _ids(reg):
    return {c["name"]: c["id"] for c in reg["constants"]}


def test_retired_gap_id_is_not_reused():
    """CONST-002 was retired by an earlier scan; a registry written before the header
    field existed seeds the mark from the current max."""
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("A", "CONST-001"), _entry("C", "CONST-003")]}
    added, _, removed = ac.update_registry(reg, [_info("A"), _info("C"), _info("NEW")])
    assert (added, removed) == (1, 0)
    assert _ids(reg)["NEW"] == "CONST-004"


def test_retired_highest_id_is_not_reused_by_a_later_scan():
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("A", "CONST-001"), _entry("B", "CONST-002")]}
    ac.update_registry(reg, [_info("A")])          # retires CONST-002, adds nothing
    assert reg["next_id"] == 3
    ac.update_registry(reg, [_info("A"), _info("NEW")])
    assert _ids(reg)["NEW"] == "CONST-003"


def test_stored_high_water_mark_wins_over_current_max():
    reg = {"version": 2, "last_scan": None, "next_id": 50,
           "constants": [_entry("A", "CONST-001")]}
    ac.update_registry(reg, [_info("A"), _info("NEW")])
    assert _ids(reg)["NEW"] == "CONST-050"
    assert reg["next_id"] == 51


def test_ids_added_in_one_scan_are_distinct_and_increasing():
    reg = {"version": 2, "last_scan": None, "constants": [_entry("A", "CONST-007")]}
    ac.update_registry(reg, [_info("A"), _info("X"), _info("Y")])
    assert sorted([_ids(reg)["X"], _ids(reg)["Y"]]) == ["CONST-008", "CONST-009"]
    assert reg["next_id"] == 10


def test_empty_registry_starts_at_one():
    reg = {"version": 2, "last_scan": None, "constants": []}
    ac.update_registry(reg, [_info("A")])
    assert _ids(reg)["A"] == "CONST-001"
