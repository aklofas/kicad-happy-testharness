"""Tests for the grouped BUGFIX reconciliation (TH-057 / A4)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from regression import generate_bugfix_assertions as gba  # noqa: E402

pytestmark = pytest.mark.unit

FIX = HARNESS_ROOT / "tests" / "fixtures" / "h0" / "plan5"


def _load(name: str) -> list[dict]:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def test_load_registry_missing_raises(tmp_path):
    with pytest.raises(gba.RegistryError, match="not found"):
        gba.load_registry(tmp_path / "nope.json")


def test_desired_groups_by_target_file(tmp_path):
    groups = gba.desired_assertions(_load("registry_basic.json"), tmp_path)
    paths = sorted(str(p.relative_to(tmp_path)) for p in groups)
    assert paths == [
        "fake/repo1/proj/assertions/schematic/a.kicad_sch_bugfix.json",
        "fake/repo2/board/assertions/pcb/hw_board.kicad_pcb_bugfix.json",
    ]
    sch = groups[tmp_path / "fake/repo1/proj/assertions/schematic/a.kicad_sch_bugfix.json"]
    assert sch.analyzer_type == "schematic"
    assert sch.file_pattern == "a.kicad_sch"
    assert [a["id"] for a in sch.assertions] == [
        "BUGFIX-KH-900-01", "BUGFIX-KH-900-02", "BUGFIX-KH-901-07"]
    assert list(sch.assertions[0]) == ["id", "description", "issue", "fix_type", "check"]
    assert sch.assertions[0]["fix_type"] == "detection_fix"
    assert sch.assertions[2]["check"]["op"] == "max_count"


def test_pinned_id_is_used_verbatim_and_pcb_type_inferred(tmp_path):
    groups = gba.desired_assertions(_load("registry_basic.json"), tmp_path)
    pcb = groups[tmp_path / "fake/repo2/board/assertions/pcb/hw_board.kicad_pcb_bugfix.json"]
    assert pcb.analyzer_type == "pcb"
    assert [a["id"] for a in pcb.assertions] == ["BUGFIX-KH-901-01"]


def test_issue_filter_limits_desired_set(tmp_path):
    groups = gba.desired_assertions(_load("registry_basic.json"), tmp_path,
                                    issue_filter="KH-901")
    ids = sorted(a["id"] for g in groups.values() for a in g.assertions)
    assert ids == ["BUGFIX-KH-901-01", "BUGFIX-KH-901-07"]


def test_duplicate_ids_in_one_file_raise(tmp_path):
    with pytest.raises(gba.RegistryError) as ei:
        gba.desired_assertions(_load("registry_dup_ids.json"), tmp_path)
    msg = str(ei.value)
    assert "BUGFIX-KH-910-01" in msg
    assert "a.kicad_sch_bugfix.json" in msg


def test_incomplete_assertion_raises(tmp_path):
    with pytest.raises(gba.RegistryError, match="KH-920.*source_file"):
        gba.desired_assertions(_load("registry_incomplete.json"), tmp_path)


def test_bad_pinned_id_raises(tmp_path):
    reg = _load("registry_basic.json")
    reg[1]["assertions"][0]["id"] = "KH-901-07"
    with pytest.raises(gba.RegistryError, match="BUGFIX-"):
        gba.desired_assertions(reg, tmp_path)


REF = FIX / "reference"
REF_HAND = FIX / "reference_hand"
A_PATH = Path("fake/repo1/proj/assertions/schematic/a.kicad_sch_bugfix.json")
HAND_PATH = Path("fake/repo3/proj/assertions/schematic/hand.kicad_sch_bugfix.json")


def _existing(rel: Path) -> dict:
    return json.loads((REF / rel).read_text(encoding="utf-8"))


def _desired_for_a(issue_filter=None):
    groups = gba.desired_assertions(_load("registry_basic.json"), REF, issue_filter)
    return groups[REF / A_PATH].assertions


def test_reconcile_buckets_and_result_order():
    diff = gba.reconcile_file(_existing(A_PATH), _desired_for_a(),
                              issue_filter=None, path=REF / A_PATH)
    assert [a["id"] for a in diff.added] == ["BUGFIX-KH-901-07"]
    assert [new["id"] for _, new, _ in diff.updated] == ["BUGFIX-KH-900-01"]
    # KH-900-03 is stale; KH-905-01 is not in this registry at all -> both removed (no --issue)
    assert sorted(a["id"] for a in diff.removed) == ["BUGFIX-KH-900-03", "BUGFIX-KH-905-01"]
    assert [a["id"] for a in diff.unchanged] == ["BUGFIX-KH-900-02"]
    # retained records keep file order, added ones are appended
    assert [a["id"] for a in diff.result] == [
        "BUGFIX-KH-900-01", "BUGFIX-KH-900-02", "BUGFIX-KH-901-07"]
    assert diff.changed()


def test_update_preserves_extra_keys():
    diff = gba.reconcile_file(_existing(A_PATH), _desired_for_a(),
                              issue_filter=None, path=REF / A_PATH)
    old, new, lines = diff.updated[0]
    assert new["check"]["value"] == 6
    assert new["migration_note"] == "Path migrated from: signal_analysis.x"
    assert list(new) == ["id", "description", "issue", "fix_type", "check", "migration_note"]
    assert any("check.value: 7 -> 6" in line for line in lines)
    assert any("description:" in line for line in lines)


def test_issue_filter_isolates_removals():
    diff = gba.reconcile_file(_existing(A_PATH), _desired_for_a("KH-900"),
                              issue_filter="KH-900", path=REF / A_PATH)
    assert [a["id"] for a in diff.removed] == ["BUGFIX-KH-900-03"]
    assert "BUGFIX-KH-905-01" in [a["id"] for a in diff.result]
    assert diff.added == []           # KH-901-07 is outside the filter


def test_missing_file_is_all_added():
    desired = _desired_for_a()
    diff = gba.reconcile_file(None, desired, issue_filter=None, path=REF / A_PATH)
    assert len(diff.added) == len(desired) == 3
    assert diff.removed == [] and diff.updated == [] and diff.unchanged == []


def test_unchanged_file_reports_no_change():
    existing = _existing(A_PATH)
    desired = [gba.owned_view(a) for a in existing["assertions"]]
    diff = gba.reconcile_file(existing, desired, issue_filter=None, path=REF / A_PATH)
    assert not diff.changed()
    assert len(diff.unchanged) == 4


def test_hand_authored_file_raises():
    existing = json.loads((REF_HAND / HAND_PATH).read_text(encoding="utf-8"))
    with pytest.raises(gba.HandAuthoredCollision, match="hand.kicad_sch_bugfix.json"):
        gba.reconcile_file(existing, [], issue_filter=None, path=REF_HAND / HAND_PATH)


def test_check_diff_lines_cover_nested_and_added_keys():
    old = {"id": "X", "description": "d", "issue": "KH-1", "fix_type": "f",
           "check": {"path": "findings", "op": "min_count", "value": 7}}
    new = dict(old, check={"path": "findings", "op": "min_count", "value": 6,
                           "detector_filter": "detect_x"})
    lines = gba.check_diff_lines(old, new)
    assert "  check.value: 7 -> 6" in lines
    assert "  check.detector_filter: <absent> -> 'detect_x'" in lines
