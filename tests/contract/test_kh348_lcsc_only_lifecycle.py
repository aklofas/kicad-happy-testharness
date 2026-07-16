#!/usr/bin/env python3
"""KH-348: an LCSC-only lifecycle audit can never produce a real status —
say so up front instead of emitting LC-004 'unknown' per part."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
import lifecycle_audit


def _analysis():
    return {"bom": [{"references": ["U1"], "mpn": "TPS61023DRLR", "type": "ic"}]}


def _mock_audit(mpn, sources, project_dir=None, delay=1.0):
    return {"mpn": mpn, "status": "unknown",
            "sources": {"lcsc": {"stock": 100}}}


def test_lcsc_only_adds_capability_note_and_skips_lc004(monkeypatch):
    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock_audit)
    result = lifecycle_audit.audit_bom(_analysis(), sources=["lcsc"], delay=0)
    assert "capability_note" in result
    assert all(f.get("rule_id") != "LC-004" for f in result["findings"])
    # Per-part rows are kept (temp data may still be useful)
    assert result["findings"][0]["status"] == "unknown"


def test_other_sources_keep_lc004(monkeypatch):
    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock_audit)
    result = lifecycle_audit.audit_bom(_analysis(), sources=["digikey"], delay=0)
    assert any(f.get("rule_id") == "LC-004" for f in result["findings"])
    assert "capability_note" not in result
