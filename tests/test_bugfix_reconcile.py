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
