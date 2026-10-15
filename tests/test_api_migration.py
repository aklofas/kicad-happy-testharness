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


import os
import subprocess

FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "fake_product"
RELOC = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "relocation_sample.json"
TOOL = HARNESS / "tools" / "api_migration.py"


def test_plan_edits_lists_every_site_with_new_module():
    edits = am.plan_edits(_mini_inventory(), json.loads(RELOC.read_text())["relocations"])
    assert len(edits) == 3     # 2 sites for _point_in_pad + 1 patch site for extract_footprints
    e = [x for x in edits if x["symbol"] == "_point_in_pad" and x["line"] == 12][0]
    assert e["file"] == "tests/c.py" and e["kind"] == "import"
    assert e["new_module"] == "pcb.reader" and e["new_name"] == "point_in_pad"
    p = [x for x in edits if x["kind"] == "patch.object"][0]
    assert p["symbol"] == "extract_footprints" and p["new_module"] == "pcb.reader"


def test_scan_harness_imports_finds_import_patch_and_monkeypatch(tmp_path):
    t = tmp_path / "tests"
    t.mkdir()
    (t / "test_x.py").write_text(
        "from analyze_pcb import _point_in_pad\n"
        "import kicad_utils\n"
        "from unittest.mock import patch\n"
        "def test_a(monkeypatch):\n"
        "    with patch.object(kicad_utils, 'classify_component'):\n"
        "        pass\n"
        "    monkeypatch.setattr(kicad_utils, 'VALUE_RE', None)\n"
        "    with patch('lifecycle_audit.audit_component'):\n"
        "        pass\n", encoding="utf-8")
    found = {(f["module"], f["symbol"]) for f in am.scan_harness_imports(tmp_path)}
    assert ("analyze_pcb", "_point_in_pad") in found
    assert ("kicad_utils", "classify_component") in found
    assert ("kicad_utils", "VALUE_RE") in found
    assert ("lifecycle_audit", "audit_component") in found


def test_check_flags_done_entry_still_imported_from_old_owner_and_retire_sites():
    disp = {"version": 1, "product_sha": "x", "entries": [
        {"module": "analyze_pcb", "symbol": "_point_in_pad", "disposition": "migrate",
         "new_owner": "skills/kicad/scripts/pcb/reader.py", "round": "r03", "status": "done", "sites": 1},
        {"module": "finding_schema", "symbol": "normalize_severity", "disposition": "retire",
         "new_owner": None, "round": None, "status": "open", "sites": 1}]}
    imports = [{"file": "tests/c.py", "line": 12, "module": "analyze_pcb", "symbol": "_point_in_pad"},
               {"file": "tests/d.py", "line": 5, "module": "finding_schema", "symbol": "normalize_severity"}]
    v = am.check(disp, imports)
    assert any("analyze_pcb._point_in_pad" in x and "old owner" in x for x in v)
    assert any("normalize_severity" in x and "retire" in x for x in v)
    imports2 = [{"file": "tests/c.py", "line": 12, "module": "pcb.reader", "symbol": "point_in_pad"}]
    assert am.check(disp, imports2) == []


def test_apply_map_missing_new_owner_exit_2(tmp_path):
    bad = tmp_path / "reloc.json"
    bad.write_text(json.dumps([{"symbol": "analyze_pcb._point_in_pad",
                                "old_owner": "skills/kicad/scripts/analyze_pcb.py",
                                "new_owner": "skills/kicad/scripts/pcb/nope.py",
                                "new_name": "point_in_pad", "facade_until": None}]))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(bad), "--product", str(FAKE)],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "analyze_pcb._point_in_pad" in r.stderr and "nope.py" in r.stderr


def test_apply_map_ok_on_fixture(tmp_path):
    inv = tmp_path / "inv.json"      # live inventory has no _point_in_pad; use the mini one
    inv.write_text(json.dumps(_mini_inventory()))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(RELOC), "--inventory", str(inv),
                        "--product", str(FAKE), "--json"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    edits = json.loads(r.stdout)
    assert all(e["new_module"] == "pcb.reader" for e in edits)


def test_status_cli_runs():
    r = subprocess.run([sys.executable, str(TOOL), "status"], capture_output=True, text=True)
    assert r.returncode == 0 and "undecided" in r.stdout and "308" in r.stdout


def test_scan_alias_mock_dotted_and_fixture_exclusion(tmp_path):
    t = tmp_path / "tests"
    (t / "fixtures" / "fp").mkdir(parents=True)
    (t / "fixtures" / "fp" / "bad.py").write_text("from zzz_fixture import q\n")
    (t / "test_y.py").write_text(
        "from unittest import mock\n"
        "import kicad_utils\n"
        "import analyze_pcb as ap\n"
        "import pkg.mod\n"
        "def test_b():\n"
        "    with mock.patch.object(kicad_utils, 'x'):\n"
        "        pass\n"
        "    with mock.patch('lifecycle_audit.audit_component'):\n"
        "        pass\n"
        "    ap._point_in_pad(1)\n"
        "    with mock.patch.object(pkg.mod, 'y'):\n"
        "        pass\n"
        "    with mock.patch.object(ap, 'z'):\n"
        "        pass\n", encoding="utf-8")
    found = {(f["module"], f["symbol"]) for f in am.scan_harness_imports(tmp_path)}
    assert ("kicad_utils", "x") in found
    assert ("lifecycle_audit", "audit_component") in found
    assert ("analyze_pcb", "_point_in_pad") in found
    assert ("analyze_pcb", "<module>") in found
    assert ("mod", "y") in found
    assert ("analyze_pcb", "z") in found
    assert not any(m == "zzz_fixture" for m, _ in found)


def test_apply_map_missing_key_exit_2(tmp_path):
    bad = tmp_path / "reloc.json"
    bad.write_text(json.dumps([{"symbol": "analyze_pcb.x", "old_owner": "a"}]))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(bad)], capture_output=True, text=True)
    assert r.returncode == 2 and "error:" in r.stderr and "Traceback" not in r.stderr
