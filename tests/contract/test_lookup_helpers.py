"""Contract tests for skills/kicad/scripts/lookup_helpers.py."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
# datasheet_types package lives here; get_facts() lazy-imports it at call time.
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def test_get_facts_returns_none_for_missing_mpn(tmp_path):
    from lookup_helpers import get_facts
    facts = get_facts("NONEXISTENT-MPN", cache_dir=tmp_path)
    assert facts is None


def test_get_facts_returns_none_for_empty_mpn(tmp_path):
    from lookup_helpers import get_facts
    assert get_facts(None, cache_dir=tmp_path) is None
    assert get_facts("", cache_dir=tmp_path) is None


def test_get_facts_returns_object_for_extant_mpn(tmp_path):
    """Use the LM2596-ADJ fixture from skills/datasheets/schemas/fixtures."""
    from lookup_helpers import get_facts
    fixture_path = (MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas" / "fixtures"
                    / "lm2596-adj.example.json")
    if not fixture_path.exists():
        pytest.skip("LM2596-ADJ fixture missing")
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "LM2596-ADJ.json").write_text(fixture_path.read_text())
    facts = get_facts("LM2596-ADJ", cache_dir=cache_dir)
    assert facts is not None
    # DatasheetFacts.mpn lives at facts.source.mpn (no top-level .mpn property).
    assert facts.source.mpn == "LM2596-ADJ"


def test_read_design_context_returns_none_when_absent(tmp_path):
    from lookup_helpers import read_design_context
    assert read_design_context(tmp_path) is None


def test_read_design_context_returns_dict_when_present(tmp_path):
    from lookup_helpers import read_design_context
    dc = {"design_category": "power_supply", "environment": "industrial",
           "compliance_targets": [], "user_declared_intent": None,
           "confidence": "high", "evidence": "test", "resolution": "inferred_only"}
    (tmp_path / "design_context.json").write_text(json.dumps(dc))
    result = read_design_context(tmp_path)
    assert result == dc


def test_lookup_helpers_exports_has_data():
    """has_data re-exported from lookup_helpers resolves to real datasheet_types impl."""
    from lookup_helpers import has_data
    # Empty/None → False
    assert has_data([]) is False
    assert has_data(None) is False
    # Non-empty list → True (uses real bool(specs) logic from trust_gating.py)
    sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))
    from datasheet_types import SpecValue, Evidence
    sv = SpecValue(unit="Ω", evidence=Evidence(page=1, confidence="medium", method="table"),
                   min=1000.0, max=10000.0)
    assert has_data([sv]) is True


def test_lookup_helpers_exports_best():
    """best re-exported from lookup_helpers resolves to real datasheet_types impl."""
    from lookup_helpers import best
    # Empty → None
    assert best([], min_confidence="medium") is None
    assert best(None, min_confidence="medium") is None
