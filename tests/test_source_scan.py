"""Tests for tools/source_scan.py — the shared recursive source walker (A2)."""
from __future__ import annotations

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
