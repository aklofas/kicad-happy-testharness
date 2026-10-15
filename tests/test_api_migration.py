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
    (t / "fixtures" / "h0" / "fp").mkdir(parents=True)
    (t / "fixtures" / "h0" / "fp" / "bad.py").write_text("from zzz_fixture import q\n")
    (t / "fixtures" / "_build_ctx.py").write_text("from kicad_types import AnalysisContext\n")
    (t / "datasheets" / "fixtures").mkdir(parents=True)
    (t / "datasheets" / "fixtures" / "v13_cache.py").write_text(
        "from datasheet_extract_cache import _sanitize_mpn\n")
    (tmp_path / "harnesslib").mkdir()
    (tmp_path / "harnesslib" / "x.py").write_text("from run_id import compute_run_id\n")
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
    assert not any(m == "zzz_fixture" for m, _ in found)       # product-imitation tree
    assert ("kicad_types", "AnalysisContext") in found          # harness fixture helpers stay
    assert ("datasheet_extract_cache", "_sanitize_mpn") in found
    assert ("run_id", "compute_run_id") in found                 # harnesslib is scanned


def _dyn_inventory():
    return {"product_head": "x", "modules": [
        {"module": "deep_review_gate", "product_paths": ["skills/kicad/review/scripts/deep_review_gate.py"],
         "symbols": []},
        {"module": "format_report", "product_paths": ["action/format-report.py"], "symbols": []},
        {"module": "datasheet_types.codec", "product_paths": ["skills/datasheets/datasheet_types/codec.py"],
         "symbols": []}]}


def test_scan_dynamic_loads_getattr_from_import_module_and_helpers(tmp_path):
    t = tmp_path / "tests"
    t.mkdir()
    (t / "test_dyn.py").write_text(
        "import importlib, importlib.util\n"
        "import pytest\n"
        "from datasheet_types import codec\n"
        "from detection_schema import SCHEMAS\n"
        "import emc_rules\n"
        "import lookup_detectors\n"
        "GATE = ROOT / 'skills' / 'kicad' / 'review' / 'scripts' / 'deep_review_gate.py'\n"
        "FMT = ROOT / 'action' / 'format-report.py'\n"
        "spec = importlib.util.spec_from_file_location('deep_review_gate', GATE)\n"
        "gate = importlib.util.module_from_spec(spec)\n"
        "RP = getattr(emc_rules, 'check_layer_transition_stitching')\n"
        "dyn = importlib.import_module('kicad_utils')\n"
        "@pytest.fixture\n"
        "def fmt_mod():\n"
        "    spec2 = importlib.util.spec_from_file_location('format_report_mod', FMT)\n"
        "    mod = importlib.util.module_from_spec(spec2)\n"
        "    return mod\n"
        "def _ld():\n"
        "    return lookup_detectors\n"
        "def test_x(fmt_mod):\n"
        "    gate._quote_in_text('a', 'b')\n"
        "    fmt_mod.format_full_report()\n"
        "    codec.decode(1)\n"
        "    dyn.VALUE_RE\n"
        "    SCHEMAS.items()\n"
        "    ld = _ld()\n"
        "    ld.detect_tj_exceeds_max(1)\n", encoding="utf-8")
    found = {(f["module"], f["symbol"]) for f in am.scan_harness_imports(tmp_path, _dyn_inventory())}
    assert ("deep_review_gate", "<module>") in found
    assert ("deep_review_gate", "_quote_in_text") in found       # spec literal + path stem
    assert ("format_report", "format_full_report") in found      # fixture param, path -> module
    assert ("format_report", "<module>") in found
    assert ("emc_rules", "check_layer_transition_stitching") in found   # getattr literal
    assert ("kicad_utils", "VALUE_RE") in found and ("kicad_utils", "<module>") in found
    assert ("datasheet_types.codec", "decode") in found          # from P import M, P.M a module
    assert ("detection_schema", "SCHEMAS.items") in found        # from-imported name chain
    assert ("lookup_detectors", "detect_tj_exceeds_max") in found   # x = helper()


def test_spec_name_used_when_path_unresolvable(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_s.py").write_text(
        "import importlib.util\n"
        "spec = importlib.util.spec_from_file_location('project_config', some_path())\n"
        "pc = importlib.util.module_from_spec(spec)\n"
        "pc.load_config(1)\n", encoding="utf-8")
    found = {(f["module"], f["symbol"]) for f in am.scan_harness_imports(tmp_path, _dyn_inventory())}
    assert ("project_config", "load_config") in found


def test_dotted_patch_object_target_records_inventory_module(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_p.py").write_text(
        "import datasheet_types.codec\n"
        "from unittest import mock\n"
        "def test_p():\n"
        "    with mock.patch.object(datasheet_types.codec, 'decode'):\n"
        "        pass\n", encoding="utf-8")
    found = {(f["module"], f["symbol"]) for f in am.scan_harness_imports(tmp_path, _dyn_inventory())}
    assert ("datasheet_types.codec", "decode") in found and ("codec", "decode") in found


BLIND = HARNESS / "reference" / "product_api" / "binding_blind_list.json"


def test_live_blind_set_is_subset_of_tracked_blind_list():
    """Fail closed: a symbol the scanner cannot bind must be listed (shrink-only)."""
    disp = json.loads(DISP.read_text(encoding="utf-8"))
    live = am.blind_symbols(am.load_inventory(INV), am.scan_harness_imports(HARNESS),
                            HARNESS, aliases=am.done_aliases(disp))
    tracked = am.load_blind_list(BLIND)
    new = sorted(tuple(k) for k in live if tuple(k) not in tracked)
    assert not new, f"scanner blind to {new}: fix the scanner or list them in {BLIND.name}"


def test_blind_symbols_per_file_and_gone_sites(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.py").write_text("from m import sym\n")
    (tmp_path / "tests" / "b.py").write_text("x = load()\nx.sym()\n")      # invisible binding
    (tmp_path / "tests" / "c.py").write_text("# nothing here any more\n")
    inv = {"product_head": "x", "modules": [{"module": "m", "product_paths": [], "symbols": [
        {"symbol": "sym", "sites": [{"file": "tests/a.py", "line": 1}, {"file": "tests/b.py", "line": 2}]},
        {"symbol": "gone", "sites": [{"file": "tests/c.py", "line": 1}]}]}]}
    imports = am.scan_harness_imports(tmp_path, inv)
    assert am.blind_symbols(inv, imports, tmp_path) == [["m", "sym"]]   # b.py masks nothing
    assert am.blind_symbols(inv, imports, tmp_path, skip={("m", "sym")}) == []


def test_done_entry_is_covered_by_new_key_but_dynamic_old_binding_stays_blind(tmp_path):
    """A done relocation is not flagged when its site file binds the NEW key, yet a
    done entry whose old-owner site is still dynamically bound stays visible."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "a.py").write_text("from pcb.reader import point_in_pad\n# _point_in_pad\n")
    (tmp_path / "tests" / "b.py").write_text("x = load()\nx._other(1)\n")       # dynamic, old owner
    inv = {"product_head": "x", "modules": [{"module": "analyze_pcb", "product_paths": [], "symbols": [
        {"symbol": "_point_in_pad", "sites": [{"file": "tests/a.py", "line": 1}]},
        {"symbol": "_other", "sites": [{"file": "tests/b.py", "line": 2}]}]}]}
    disp = {"version": 1, "product_sha": "x", "entries": [
        {"module": "analyze_pcb", "symbol": "_point_in_pad", "disposition": "migrate",
         "new_owner": "skills/kicad/scripts/pcb/reader.py", "new_name": "point_in_pad",
         "round": "r03", "status": "done", "sites": 1},
        {"module": "analyze_pcb", "symbol": "_other", "disposition": "migrate",
         "new_owner": "skills/kicad/scripts/pcb/reader.py", "round": "r03", "status": "done", "sites": 1}]}
    imports = am.scan_harness_imports(tmp_path, inv)
    assert am.done_aliases(disp) == {("analyze_pcb", "_point_in_pad"): ("pcb.reader", "point_in_pad"),
                                     ("analyze_pcb", "_other"): ("pcb.reader", "_other")}
    assert am.blind_symbols(inv, imports, tmp_path, aliases=am.done_aliases(disp)) == [["analyze_pcb", "_other"]]
    # the old skip-everything-done behaviour would have hidden _other entirely
    assert am.blind_symbols(inv, imports, tmp_path, skip=am.done_keys(disp)) == []


def test_check_done_or_retire_on_blind_list_is_unverifiable():
    disp = {"version": 1, "product_sha": "x", "entries": [
        {"module": "deep_review_gate", "symbol": "_quote_in_text", "disposition": "migrate",
         "new_owner": "skills/kicad/review/scripts/quotes.py", "round": "r03", "status": "done", "sites": 1},
        {"module": "finding_schema", "symbol": "_gone", "disposition": "retire",
         "new_owner": None, "round": None, "status": "open", "sites": 1},
        {"module": "a", "symbol": "open_one", "disposition": "migrate",
         "new_owner": None, "round": None, "status": "open", "sites": 1}]}
    blind = {("deep_review_gate", "_quote_in_text"), ("finding_schema", "_gone"), ("a", "open_one")}
    v = am.check(disp, [], blind)
    assert v == ["deep_review_gate._quote_in_text UNVERIFIABLE (dynamic binding; verify with apply-map)",
                 "finding_schema._gone UNVERIFIABLE (dynamic binding; verify with apply-map)"]
    assert am.check(disp, [], set()) == []


def test_check_cli_unverifiable_exit_1(tmp_path):
    entries = json.loads(DISP.read_text(encoding="utf-8"))
    e = next(x for x in entries["entries"] if x["disposition"] == "migrate")
    e["status"], e["new_owner"] = "done", "skills/kicad/scripts/new_home.py"
    d = tmp_path / "disp.json"
    d.write_text(json.dumps(entries))
    bl = tmp_path / "blind.json"
    bl.write_text(json.dumps({"version": 1, "blind": [[e["module"], e["symbol"]]]}))
    r = subprocess.run([sys.executable, str(TOOL), "check", "--dispositions", str(d),
                        "--blind-list", str(bl)], capture_output=True, text=True)
    assert r.returncode == 1
    assert f"{e['module']}.{e['symbol']} UNVERIFIABLE" in r.stdout


def test_apply_map_missing_key_exit_2(tmp_path):
    bad = tmp_path / "reloc.json"
    bad.write_text(json.dumps([{"symbol": "analyze_pcb.x", "old_owner": "a"}]))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(bad)], capture_output=True, text=True)
    assert r.returncode == 2 and "error:" in r.stderr and "Traceback" not in r.stderr


PRODUCT_MAP = HARNESS / "tests" / "fixtures" / "h0" / "round2" / "relocation_map_product.json"


def test_apply_map_accepts_product_shape_map():
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(PRODUCT_MAP), "--json"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    edits = json.loads(r.stdout)
    assert edits and all(e["module"] == "kicad_utils" and e["new_module"] == "kicad_core.fields" for e in edits)
    assert {e["symbol"] for e in edits} == {"normalize_field_name", "MPN_FIELD_ALIASES_PRIMARY",
                                            "MPN_FIELD_ALIASES_GENERIC"}
    assert all(e["facade_until"] == "r09" for e in edits)


def test_load_relocations_product_shape_uses_inventory(tmp_path):
    rels = am._load_relocations(PRODUCT_MAP, am.load_inventory(INV))
    assert rels[0]["old_owner"] == "skills/kicad/scripts/kicad_utils.py"


def test_apply_map_skips_unbound_symbols_with_one_note(tmp_path):
    """A product-shape map lists everything it moved; names the harness never bound are skipped
    with ONE summary note, exit 0, and the listed sites are unchanged."""
    bound = {"old": "kicad_utils.normalize_field_name", "new": "kicad_core.fields.normalize_field_name",
             "facade": True, "retire": "round 9"}
    only = tmp_path / "only.json"
    only.write_text(json.dumps({"relocations": [bound]}))
    mixed = tmp_path / "mixed.json"
    mixed.write_text(json.dumps({"relocations": [
        bound,
        {"old": "kicad_utils.not_bound_a", "new": "kicad_core.fields.not_bound_a", "facade": False},
        {"old": "kicad_utils.not_bound_b", "new": "kicad_core.fields.not_bound_b", "facade": False}]}))
    run = lambda m: subprocess.run([sys.executable, str(TOOL), "apply-map", str(m), "--json"],  # noqa: E731
                                   capture_output=True, text=True)
    r0, r = run(only), run(mixed)
    assert r0.returncode == 0 and r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == json.loads(r0.stdout) and json.loads(r.stdout)
    notes = [ln for ln in r.stderr.splitlines() if ln.startswith("note:")]
    assert notes == ["note: 2 relocations name symbols the harness never bound (skipped)"]
    assert "error" not in r.stderr and "note: " not in r0.stderr.replace("warning:", "")


def test_apply_map_record_shape_unknown_symbol_is_hard_error(tmp_path):
    """A record-shape map is hand-written: a symbol not in the inventory is a typo (exit 2)."""
    m = tmp_path / "map.json"
    m.write_text(json.dumps([{"symbol": "kicad_utils.typo_name", "old_owner": "skills/kicad/scripts/kicad_utils.py",
                              "new_owner": "skills/kicad/scripts/kicad_core/fields.py", "new_name": "typo_name",
                              "facade_until": None}]))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(m)], capture_output=True, text=True)
    assert r.returncode == 2 and "error: kicad_utils.typo_name not in inventory" in r.stderr
    assert "never bound" not in r.stderr


def test_apply_map_mixed_map_skips_product_entries_errors_record_entries(tmp_path):
    m = tmp_path / "map.json"
    m.write_text(json.dumps({"relocations": [
        {"old": "kicad_utils.not_bound_a", "new": "kicad_core.fields.not_bound_a", "facade": False},
        {"symbol": "kicad_utils.typo_b", "old_owner": "skills/kicad/scripts/kicad_utils.py",
         "new_owner": "skills/kicad/scripts/kicad_core/fields.py", "new_name": "typo_b", "facade_until": None}]}))
    r = subprocess.run([sys.executable, str(TOOL), "apply-map", str(m)], capture_output=True, text=True)
    assert r.returncode == 2
    assert "error: kicad_utils.typo_b not in inventory" in r.stderr
    assert "note: 1 relocations name symbols the harness never bound (skipped)" in r.stderr
