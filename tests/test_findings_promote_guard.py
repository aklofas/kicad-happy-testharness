"""findings.py promote refuses an assertion the engine would reject at load (TH-100)."""

TIER = "unit"

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
import findings  # noqa: E402


def test_promote_refuses_an_unknown_operator(monkeypatch):
    finding = {"id": "FND-9", "analyzer_type": "schematic", "source_file": "schematic/o/r/f.kicad_sch.json",
               "repo": "o/r", "project": "p",
               "correct": [{"description": "d", "check": {"path": "x", "op": "eq", "value": 1}}]}
    monkeypatch.setattr(findings, "_find_finding", lambda fid: ("o/r", "p", {"findings": [finding]}, finding))
    with pytest.raises(ValueError, match="unknown operator 'eq'"):
        findings.promote_to_assertion("FND-9", dry_run=True)
