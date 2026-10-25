"""integration/test_bom_manager.py is a script, not a pytest module: its parameterised
helpers are not `test_*`, a failed bom_manager run is a failed check, and repo identity is
owner/repo (arch A3-F6, sec A1-F8 A1-F9, code A7-F13 A7-F18)."""
import ast
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
DRIVER = HARNESS / "integration" / "test_bom_manager.py"
pytestmark = pytest.mark.unit


def test_no_parameterised_test_functions():
    tree = ast.parse(DRIVER.read_text())
    bad = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)
           and n.name.startswith("test_") and n.args.args]
    assert bad == []


def test_failed_run_is_a_failed_check(monkeypatch, tmp_path):
    sys.path.insert(0, str(HARNESS / "integration"))
    import test_bom_manager as tbm
    monkeypatch.setattr(tbm, "run_bom_manager", lambda args, timeout=60: {
        "success": False, "exit_code": 1, "elapsed_s": 0.0, "stdout": "", "stderr": "boom"})
    for checks in (tbm.check_analyze(tmp_path / "a.kicad_sch")["checks"],
                   tbm.check_export(tmp_path / "a.kicad_sch", tmp_path / "bom.csv")["checks"]):
        assert checks["exit_ok"] is False
