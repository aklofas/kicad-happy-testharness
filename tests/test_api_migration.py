"""tools/api_migration.py — inventory adoption + relocation checker (A1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "tools"))
import api_migration as am  # noqa: E402

INV = HARNESS / "reference" / "product_api" / "inventory_6a91aaa.json"
DISP = HARNESS / "reference" / "product_api" / "dispositions.json"


def _mini_inventory():
    return {"product_head": "abc123", "modules": [
        {"module": "finding_schema", "product_paths": ["skills/kicad/scripts/finding_schema.py"],
         "symbols": [
             {"symbol": "make_finding", "private": False, "dependencies": ["name"],
              "files": ["tests/a.py"], "sites": [{"file": "tests/a.py", "line": 3, "kind": "import"}]},
             {"symbol": "_apply_severity_tuning", "private": True, "dependencies": ["name"],
              "files": ["tests/b.py"], "sites": [{"file": "tests/b.py", "line": 9, "kind": "import"}]}]},
        {"module": "analyze_pcb", "product_paths": ["skills/kicad/scripts/analyze_pcb.py"],
         "symbols": [
             {"symbol": "_point_in_pad", "private": True, "dependencies": ["name", "signature"],
              "files": ["tests/c.py"], "sites": [{"file": "tests/c.py", "line": 12, "kind": "import"},
                                                 {"file": "tests/c.py", "line": 40, "kind": "call"}]},
             {"symbol": "extract_footprints", "private": False, "dependencies": ["name"],
              "files": ["tests/c.py"], "sites": [{"file": "tests/c.py", "line": 13, "kind": "patch.object"}]}]}]}


def test_initial_disposition_rules():
    assert am.initial_disposition("finding_schema", "make_finding", False) == "keep-contract"
    assert am.initial_disposition("finding_schema", "_apply_severity_tuning", True) == "retire"
    assert am.initial_disposition("analyze_pcb", "_point_in_pad", True) == "migrate"
    assert am.initial_disposition("analyze_pcb", "extract_footprints", False) == "undecided"
    assert am.initial_disposition("datasheet_types.codec", "decode", False) == "keep-contract"
    assert am.initial_disposition("datasheet_types.spec_value", "_from_value", True) == "migrate"


def test_build_dispositions_shape_and_site_counts():
    d = am.build_dispositions(_mini_inventory())
    assert d["version"] == 1 and d["product_sha"] == "abc123"
    by = {(e["module"], e["symbol"]): e for e in d["entries"]}
    assert by[("analyze_pcb", "_point_in_pad")]["sites"] == 2
    assert by[("analyze_pcb", "_point_in_pad")]["status"] == "open"
    assert by[("analyze_pcb", "_point_in_pad")]["new_owner"] is None
    assert len(d["entries"]) == 4


def test_shipped_inventory_and_dispositions_agree():
    inv = am.load_inventory(INV)
    disp = json.loads(DISP.read_text(encoding="utf-8"))
    assert inv["product_head"] == disp["product_sha"] == "6a91aaaea124152b2923326c1cf77278e0999cd4"
    assert len(disp["entries"]) == sum(len(m["symbols"]) for m in inv["modules"]) == 308
    counts = {}
    for e in disp["entries"]:
        counts[e["disposition"]] = counts.get(e["disposition"], 0) + 1
    assert counts["retire"] >= 2 and counts["migrate"] >= 40 and counts["keep-contract"] >= 20
