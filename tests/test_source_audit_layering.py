"""harnesslib.source_audit owns the source walker and both scan engines; the audit CLIs and
tools/source_scan.py import from it, never the other way round."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "tools"))
sys.path.insert(0, str(HARNESS / "validate"))

import audit_constants as ac  # noqa: E402
import audit_equations as ae  # noqa: E402
import discover_versioned_detectors as dvd  # noqa: E402
import source_scan  # noqa: E402
from harnesslib.source_audit import constants, equations, sources  # noqa: E402

pytestmark = pytest.mark.unit

ENGINE_DIR = HARNESS / "harnesslib" / "source_audit"
CLI_LAYERS = {"tools", "validate", "utils", "regression", "run",
              "source_scan", "audit_constants", "audit_equations"}


def test_source_scan_does_not_import_the_audit_clis():
    src = (HARNESS / "tools" / "source_scan.py").read_text(encoding="utf-8")
    assert "import audit_constants" not in src and "import audit_equations" not in src


def test_source_audit_imports_no_cli_layer():
    files = sorted(ENGINE_DIR.glob("*.py"))
    assert {p.name for p in files} >= {"__init__.py", "sources.py", "constants.py", "equations.py"}
    for path in files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                roots = {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                roots = {(node.module or "").split(".")[0]}
            else:
                continue
            assert not roots & CLI_LAYERS, f"{path.name} imports {roots & CLI_LAYERS}"


def test_cli_names_are_the_engine_objects():
    assert ac.scan_file is constants.scan_file
    assert ac.iter_constant_records is constants.iter_constant_records
    assert ac.ConstantInfo is constants.ConstantInfo and ac.ScanError is constants.ScanError
    assert ac.iter_source_files is constants.iter_source_files
    assert ae.iter_equations is equations.iter_equations
    assert ae.scan_file is equations.scan_file and ae.find_untagged is equations.find_untagged
    assert ae.scan_all_tagged is equations.scan_all_tagged and ae.ScanError is equations.ScanError
    assert ae.iter_source_files is equations.iter_source_files
    assert source_scan.iter_product_sources is sources.iter_product_sources
    assert source_scan.rel is sources.rel and source_scan.parse_source is sources.parse_source
    assert dvd.sources.str_literal is sources.str_literal


def test_constants_scan_honours_a_latin1_cookie(tmp_path):
    f = tmp_path / "legacy.py"
    f.write_bytes(b"# -*- coding: latin-1 -*-\n"
                  b"NAMES = ('caf\xe9', 'na\xefve', 'r\xe9sum\xe9')\n")
    found = constants.scan_file(f)
    assert [(c.name, c.const_type, c.entry_count) for c in found] == [("NAMES", "keyword_list", 3)]
