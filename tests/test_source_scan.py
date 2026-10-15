"""Tests for tools/source_scan.py — the shared recursive source walker (A2)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "tools"))

import source_scan  # noqa: E402

FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "fake_product"


def test_iter_product_sources_recurses_and_sorts():
    files = source_scan.iter_product_sources(FAKE)
    rels = [source_scan.rel(FAKE, p) for p in files]
    assert rels == sorted(rels)
    assert "skills/kicad/scripts/schematic/reader.py" in rels
    assert "skills/kicad/scripts/pcb/reader.py" in rels
    assert "skills/kicad/scripts/schematic/__init__.py" in rels
    assert "skills/emc/scripts/emc_rules.py" in rels


def test_iter_product_sources_skips_pycache():
    junk_dir = FAKE / "skills" / "emc" / "scripts" / "__pycache__"
    junk_dir.mkdir(parents=True, exist_ok=True)
    (junk_dir / "junk.cpython-312.pyc").touch()
    rels = [source_scan.rel(FAKE, p) for p in source_scan.iter_product_sources(FAKE)]
    assert not any("__pycache__" in r for r in rels)
    assert all(r.endswith(".py") for r in rels)


def test_rel_is_posix_root_relative():
    p = FAKE / "skills" / "kicad" / "scripts" / "pcb" / "reader.py"
    assert source_scan.rel(FAKE, p) == "skills/kicad/scripts/pcb/reader.py"
    assert "\\" not in source_scan.rel(FAKE, p)


def test_iter_product_sources_pycache_above_root_not_skipped(tmp_path):
    root = tmp_path / "__pycache__" / "prod"
    f = root / "skills" / "kicad" / "scripts" / "mod.py"
    f.parent.mkdir(parents=True)
    f.write_text("X = 1\n")
    assert [source_scan.rel(root, p) for p in source_scan.iter_product_sources(root)] == [
        "skills/kicad/scripts/mod.py"]


def _sites(relpath, enum=None):
    return source_scan.emit_sites(FAKE, FAKE / relpath, det_enum=enum)


def test_literal_sites_resolved_with_era():
    sites = _sites("skills/kicad/scripts/validation_detectors.py")
    pu = [s for s in sites if s.rule_id == "PU-001"]
    assert len(pu) == 1
    s = pu[0]
    assert s.file == "skills/kicad/scripts/validation_detectors.py"
    assert s.callee == "make_finding"
    assert s.detector == "validate_pullups" and s.schema_era == "v1.4"
    assert s.resolved and s.reason == ""


def test_nested_package_site_found():
    sites = _sites("skills/kicad/scripts/schematic/reader.py")
    assert [(s.detector, s.rule_id, s.schema_era) for s in sites] == [
        ("detect_nested", "NX-001", "v3.0")]


def test_enum_attribute_unresolved_without_map_and_resolved_with_map():
    sites = _sites("skills/kicad/scripts/validation_detectors.py")
    sp = [s for s in sites if s.rule_id == "SP-001"][0]
    assert not sp.resolved and sp.reason == "detector:enum-attribute" and sp.detector is None
    enum = source_scan.resolve_det_enum(FAKE)
    assert enum["SHORTED_TWO_PIN"] == "detect_shorted_two_pin_components"
    sp2 = [s for s in _sites("skills/kicad/scripts/validation_detectors.py", enum)
           if s.rule_id == "SP-001"][0]
    assert sp2.resolved and sp2.detector == "detect_shorted_two_pin_components"
    assert sp2.reason == "detector:enum-attribute-resolved"


def test_nonliteral_rule_id_unresolved():
    sites = _sites("skills/kicad/scripts/validation_detectors.py")
    uc = [s for s in sites if s.detector == "analyze_usb_compliance"][0]
    assert not uc.resolved and uc.rule_id is None
    assert uc.reason == "rule_id:nonliteral"


def test_positional_emc_shape_derives_detector():
    sites = _sites("skills/emc/scripts/emc_rules.py")
    gp = [s for s in sites if s.rule_id == "GP-001"][0]
    assert gp.callee == "_make_finding"
    assert gp.detector == "emc_ground_plane"
    assert not gp.resolved and gp.reason == "positional-emc"
    assert gp.schema_era is None


def test_mixed_positional_keyword_is_unresolved():
    sites = _sites("skills/emc/scripts/emc_rules.py")
    sh = [s for s in sites if s.rule_id == "SH-009"]
    assert len(sh) == 1
    assert not sh[0].resolved and sh[0].reason == "positional-emc:mixed-shape"
    assert sh[0].detector is None


def test_emit_sites_latin1_cookie(tmp_path):
    src = (b"# -*- coding: latin-1 -*-\n"
           b"def make_finding(**kw): return kw\n"
           b"X = make_finding(detector='d\xe9tecteur', rule_id='LA-001', schema_era='v1.4')\n")
    root = tmp_path / "prod"
    f = root / "skills" / "kicad" / "scripts" / "mod.py"
    f.parent.mkdir(parents=True)
    f.write_bytes(src)
    sites = source_scan.emit_sites(root, f)
    assert len(sites) == 1 and sites[0].detector == "détecteur" and sites[0].resolved


def _fake_exceptions():
    return {"version": 1, "exceptions": [
        {"id": "emc-positional", "file": "skills/emc/scripts/emc_rules.py",
         "callee": "_make_finding", "reason": "positional-emc", "count": 2},
        {"id": "det-enum", "file": "skills/kicad/scripts/validation_detectors.py",
         "callee": "make_finding", "reason": "detector:enum-attribute-resolved", "count": 1},
        {"id": "uc-loop", "file": "skills/kicad/scripts/validation_detectors.py",
         "callee": "make_finding", "reason": "rule_id:nonliteral", "count": 1},
    ]}


def test_apply_exceptions_absorbs_counted_sites_only():
    enum = source_scan.resolve_det_enum(FAKE)
    sites = [s for p in source_scan.iter_product_sources(FAKE)
             for s in source_scan.emit_sites(FAKE, p, enum)]
    remaining, counts, violations = source_scan.apply_exceptions(sites, _fake_exceptions())
    assert counts == {"emc-positional": 2, "det-enum": 1, "uc-loop": 1}
    assert violations == []
    # the mixed-shape EMC call is not covered by any exception
    assert [s.reason for s in remaining] == ["positional-emc:mixed-shape"]


def test_apply_exceptions_count_growth_is_violation():
    exc = _fake_exceptions()
    exc["exceptions"][0]["count"] = 1          # ledger says 1, tree has 2
    sites = [s for p in source_scan.iter_product_sources(FAKE)
             for s in source_scan.emit_sites(FAKE, p, source_scan.resolve_det_enum(FAKE))]
    _, counts, violations = source_scan.apply_exceptions(sites, exc)
    assert counts["emc-positional"] == 2
    assert any("emc-positional" in v and "grew" in v for v in violations)


def test_apply_exceptions_partial_shrink_is_violation():
    exc = _fake_exceptions()
    exc["exceptions"][0]["count"] = 3          # ledger says 3, tree has 2
    sites = [s for p in source_scan.iter_product_sources(FAKE)
             for s in source_scan.emit_sites(FAKE, p, source_scan.resolve_det_enum(FAKE))]
    _, counts, violations = source_scan.apply_exceptions(sites, exc)
    assert counts["emc-positional"] == 2
    assert violations == ["exception emc-positional shrank: matched 2 < recorded 3"
                          " — shrink the ledger entry in the same commit"]


def test_apply_exceptions_zero_match_is_violation():
    exc = _fake_exceptions()
    exc["exceptions"].append({"id": "ghost", "file": "skills/none.py", "callee": "x",
                              "reason": "positional-emc", "count": 3})
    sites = [s for p in source_scan.iter_product_sources(FAKE)
             for s in source_scan.emit_sites(FAKE, p, source_scan.resolve_det_enum(FAKE))]
    _, _, violations = source_scan.apply_exceptions(sites, exc)
    assert any("ghost" in v and "matched 0" in v for v in violations)


def test_shipped_exception_file_loads_and_has_required_keys():
    exc = source_scan.load_exceptions()
    assert exc["version"] == 1
    for e in exc["exceptions"]:
        assert {"id", "file", "callee", "reason", "count", "retire_by"} <= set(e)


def test_apply_exceptions_unmatched_resolved_reason_site_is_not_dropped():
    exc = _fake_exceptions()
    exc["exceptions"] = [e for e in exc["exceptions"] if e["id"] != "det-enum"]
    enum = source_scan.resolve_det_enum(FAKE)
    sites = [s for p in source_scan.iter_product_sources(FAKE)
             for s in source_scan.emit_sites(FAKE, p, enum)]
    remaining, _, _ = source_scan.apply_exceptions(sites, exc)
    reasons = [s.reason for s in remaining]
    assert "detector:enum-attribute-resolved" in reasons
    assert "positional-emc:mixed-shape" in reasons


def test_coverage_snapshot_distinguishes_same_basename():
    snap = source_scan.coverage_snapshot(FAKE, exceptions=_fake_exceptions())
    assert "skills/kicad/scripts/schematic/reader.py|module|SHEET_DEPTH_MAX" in snap["constants"]
    assert "skills/kicad/scripts/pcb/reader.py|module|SHEET_DEPTH_MAX" in snap["constants"]
    assert snap["eq_ids"]["EQ-902"] == "skills/kicad/scripts/pcb/reader.py"
    assert snap["emit_sites"]["detect_nested|NX-001"] == 1
    assert snap["emit_sites"]["validate_pullups|PU-001"] == 1
    # SP-001 (enum-resolved, no schema_era) is the fixture's one resolved untagged site
    assert snap["untagged_era_sites"] == {"detect_shorted_two_pin_components|SP-001": 1}
    assert snap["untagged_era_total"] == 1
    assert snap["constant_eq_roots"] == ["skills/emc/scripts", "skills/kicad/scripts",
                                         "skills/spice/scripts"]


def test_coverage_diff_detects_lost_site_and_constant(tmp_path):
    base = source_scan.coverage_snapshot(FAKE, exceptions=_fake_exceptions())
    shrunk = tmp_path / "prod"
    shutil.copytree(FAKE, shrunk)
    (shrunk / "skills/kicad/scripts/schematic/reader.py").write_text(
        '"""emptied"""\nSHEET_DEPTH_MAX = 8\n', encoding="utf-8")
    cur = source_scan.coverage_snapshot(shrunk, exceptions=_fake_exceptions())
    d = source_scan.coverage_diff(base, cur)
    assert d["lost_sites"] == ["detect_nested|NX-001"]
    assert d["lost_eq"] == []
    assert d["lost_files"] == []
    assert not d["clean"]


def test_coverage_diff_lost_file(tmp_path):
    base = source_scan.coverage_snapshot(FAKE, exceptions=_fake_exceptions())
    shrunk = tmp_path / "prod"
    shutil.copytree(FAKE, shrunk)
    (shrunk / "skills/kicad/scripts/pcb/reader.py").unlink()
    d = source_scan.coverage_diff(base, source_scan.coverage_snapshot(shrunk, exceptions=_fake_exceptions()))
    assert d["lost_files"] == ["skills/kicad/scripts/pcb/reader.py"]
    assert "skills/kicad/scripts/pcb/reader.py|module|SHEET_DEPTH_MAX" in d["lost_constants"]
    assert d["lost_eq"] == ["EQ-902"]


def test_check_cli_exit_codes(tmp_path):
    exc = tmp_path / "exc.json"
    exc.write_text(json.dumps(_fake_exceptions()))
    base = tmp_path / "base.json"
    tool = str(HARNESS / "tools" / "source_scan.py")
    r = subprocess.run([sys.executable, tool, "snapshot", "--product", str(FAKE),
                        "--exceptions", str(exc), "-o", str(base)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    r = subprocess.run([sys.executable, tool, "check", "--product", str(FAKE),
                        "--exceptions", str(exc), "--baseline", str(base)],
                       capture_output=True, text=True)
    # the mixed-shape EMC call is unresolved and not excepted -> 1
    assert r.returncode == 1 and "positional-emc:mixed-shape" in r.stdout
    shrunk = tmp_path / "prod"
    shutil.copytree(FAKE, shrunk)
    (shrunk / "skills/kicad/scripts/pcb/reader.py").unlink()
    # --accept-baseline never absorbs unresolved sites: except the mixed-shape call first
    full = _fake_exceptions()
    full["exceptions"].append({"id": "emc-mixed", "file": "skills/emc/scripts/emc_rules.py",
                               "callee": "_make_finding",
                               "reason": "positional-emc:mixed-shape", "count": 1})
    exc_full = tmp_path / "exc_full.json"
    exc_full.write_text(json.dumps(full))
    before = base.read_bytes()
    r = subprocess.run([sys.executable, tool, "check", "--product", str(shrunk),
                        "--exceptions", str(exc), "--baseline", str(base), "--accept-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "unresolved" in r.stdout
    assert base.read_bytes() == before        # a refused accept never touches the baseline
    r = subprocess.run([sys.executable, tool, "check", "--product", str(shrunk),
                        "--exceptions", str(exc_full), "--baseline", str(base), "--accept-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "skills/kicad/scripts/pcb/reader.py" not in json.loads(base.read_text())["files"]


def test_check_cli_missing_product_is_usage_error(tmp_path):
    tool = str(HARNESS / "tools" / "source_scan.py")
    r = subprocess.run([sys.executable, tool, "check", "--product", str(tmp_path / "nope")],
                       capture_output=True, text=True)
    assert r.returncode == 2


def _full_exceptions_file(tmp_path):
    full = _fake_exceptions()
    full["exceptions"].append({"id": "emc-mixed", "file": "skills/emc/scripts/emc_rules.py",
                               "callee": "_make_finding",
                               "reason": "positional-emc:mixed-shape", "count": 1})
    p = tmp_path / "exc_full.json"
    p.write_text(json.dumps(full))
    return p


def test_coverage_diff_per_key_untagged_era(tmp_path):
    """Tagging one rule's site while a new untagged site of another rule appears
    nets to zero overall; the per-key map still reports the new key."""
    base = source_scan.coverage_snapshot(FAKE, exceptions=_fake_exceptions())
    prod = tmp_path / "prod"
    shutil.copytree(FAKE, prod)
    vd = prod / "skills/kicad/scripts/validation_detectors.py"
    src = vd.read_text(encoding="utf-8")
    src = src.replace('summary="short", description="x")]',
                      'summary="short", description="x", schema_era="v3.0")]')
    src += ('\n\ndef detect_new(ctx):\n    return [make_finding(detector="detect_new", '
            'rule_id="NW-001", category="x", summary="s", description="x")]\n')
    vd.write_text(src, encoding="utf-8")
    cur = source_scan.coverage_snapshot(prod, exceptions=_fake_exceptions())
    assert cur["untagged_era_total"] == base["untagged_era_total"]
    d = source_scan.coverage_diff(base, cur)
    assert d["new_untagged_era"] == ["detect_new|NW-001"]
    assert not d["clean"]
    assert d["grew"]["untagged_era_decreased"] == ["detect_shorted_two_pin_components|SP-001"]


def test_coverage_diff_rejects_v1_baseline():
    base = source_scan.coverage_snapshot(FAKE, exceptions=_fake_exceptions())
    base["untagged_era_sites"] = 1
    with pytest.raises(ValueError, match="snapshot_version 2"):
        source_scan.coverage_diff(base, base)


def test_check_accept_baseline_ratchets_growth(tmp_path):
    exc = _full_exceptions_file(tmp_path)
    base = tmp_path / "base.json"
    tool = str(HARNESS / "tools" / "source_scan.py")
    run = lambda *a: subprocess.run([sys.executable, tool, *a], capture_output=True, text=True)
    r = run("snapshot", "--product", str(FAKE), "--exceptions", str(exc), "-o", str(base))
    assert r.returncode == 0, r.stderr
    grown = tmp_path / "prod"
    shutil.copytree(FAKE, grown)
    (grown / "skills/kicad/scripts/schematic/extra.py").write_text(
        "from ..finding_schema import make_finding\nEXTRA_LIMIT = 7\n\n"
        "def f(a):\n    # EQ-950: y = a\n    return [make_finding(detector='detect_extra', "
        "rule_id='EX-950', category='x', summary='s', description='x', schema_era='v3.0')]\n",
        encoding="utf-8")
    before = base.read_bytes()
    r = run("check", "--product", str(grown), "--exceptions", str(exc), "--baseline", str(base))
    assert r.returncode == 0, r.stdout
    assert "CLEAN" in r.stdout and "coverage grew: 1 files, 1 site keys, 1 EQ, 1 constants" in r.stdout
    assert base.read_bytes() == before        # no flag: growth noted, baseline untouched
    r = run("check", "--product", str(grown), "--exceptions", str(exc), "--baseline", str(base),
            "--accept-baseline")
    assert r.returncode == 0, r.stdout
    assert "(baseline updated)" in r.stdout
    data = json.loads(base.read_text())
    assert "skills/kicad/scripts/schematic/extra.py" in data["files"]
    assert data["emit_sites"]["detect_extra|EX-950"] == 1 and "EQ-950" in data["eq_ids"]
    # the ratcheted floor now protects the new coverage: deleting the file fails
    (grown / "skills/kicad/scripts/schematic/extra.py").unlink()
    r = run("check", "--product", str(grown), "--exceptions", str(exc), "--baseline", str(base))
    assert r.returncode == 1 and "lost_files: skills/kicad/scripts/schematic/extra.py" in r.stdout


TRIPWIRE_SRC = (
    '"""Tripwire: importing or executing this module must never happen."""\n'
    'from finding_schema import make_finding\n'
    'raise RuntimeError("imported!")\n'
    'TRIP_MAX_OHMS = 4700\n'
    '\n'
    'def detect_trip(ctx):\n'
    '    # EQ-999: trip = ctx\n'
    '    return [make_finding(detector="d", rule_id="R-1", category="x",\n'
    '                         summary="s", description="x", schema_era="v1.4")]\n')


def test_scanners_never_import_product_code(tmp_path):
    """Every scanner walks a module that raises at import time, without raising,
    and still finds its emit site, EQ tag and constant (spec: ast only)."""
    sys.path.insert(0, str(HARNESS / "validate"))
    import audit_constants
    import audit_equations
    import detect_changes
    import discover_versioned_detectors as dvd
    prod = tmp_path / "prod"
    shutil.copytree(FAKE, prod)
    trip = prod / "skills" / "kicad" / "scripts" / "tripwire.py"
    trip.write_text(TRIPWIRE_SRC, encoding="utf-8")
    rel = "skills/kicad/scripts/tripwire.py"
    before = set(sys.modules)

    sites = source_scan.emit_sites(prod, trip)
    assert [(s.detector, s.rule_id, s.schema_era, s.resolved) for s in sites] == [
        ("d", "R-1", "v1.4", True)]
    snap = source_scan.coverage_snapshot(prod, exceptions=_fake_exceptions())
    assert rel in snap["files"] and snap["emit_sites"]["d|R-1"] == 1
    assert snap["eq_ids"]["EQ-999"] == rel
    assert f"{rel}|module|TRIP_MAX_OHMS" in snap["constants"]
    assert detect_changes.build_module_index(prod)["tripwire"] == rel
    assert "skills/kicad/scripts/finding_schema.py" in detect_changes._build_dependency_graph(prod)[rel]
    assert any(r["file"] == rel and r["name"] == "TRIP_MAX_OHMS"
               for r in audit_constants.iter_constant_records(prod))
    assert {"eq_id": "EQ-999", "file": rel}.items() <= next(
        e for e in audit_equations.iter_equations(prod) if e["eq_id"] == "EQ-999").items()
    out = dvd.discover(prod, "v1.4")
    assert out["detectors"]["d"]["rules"] == ["R-1"]
    assert out["detectors"]["d"]["source_file"] == rel
    assert "tripwire" not in sys.modules
    assert not {m for m in set(sys.modules) - before if "tripwire" in m}
