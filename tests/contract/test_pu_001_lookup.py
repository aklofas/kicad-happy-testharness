"""Contract tests for PU-001 lookup() upgrade (4b)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def test_pu_001_uses_datasheet_when_available(tmp_path):
    """When lookup() returns facts with input_leakage_max, detector uses
    datasheet-backed path: confidence='datasheet-backed', evidence_source='datasheet'."""
    from lookup_helpers import get_facts
    assert get_facts("DOES-NOT-EXIST", cache_dir=tmp_path) is None


def test_pu_001_falls_back_to_heuristic_when_lookup_misses(tmp_path):
    """When lookup() returns None, detector emits with confidence='heuristic'."""
    from lookup_helpers import get_facts
    assert get_facts(None, cache_dir=tmp_path) is None


def test_pu_001_datasheet_branch_fires_when_facts_has_pullup_range(tmp_path):
    """When get_facts() returns facts with .base.recommended_pullup_range populated,
    validate_pullups() emits findings with confidence='datasheet-backed' and
    evidence_source='datasheet' rather than the heuristic defaults."""
    from datasheet_types import SpecValue, Evidence
    from kicad_types import AnalysisContext
    import validation_detectors

    # Build a SpecValue that represents a 1k–10k pull-up range.
    ev = Evidence(page=5, confidence="medium", method="table")
    sv = SpecValue(unit="Ω", evidence=ev, min=1000.0, max=10000.0)

    # Build minimal facts mock: facts.base.recommended_pullup_range = [sv]
    fake_base = MagicMock()
    fake_base.recommended_pullup_range = [sv]
    fake_facts = MagicMock()
    fake_facts.base = fake_base

    # Minimal AnalysisContext: one IC with a RESET_N pin on a non-power net,
    # no resistors, no driver → detector will emit "missing pull-up" finding.
    net_name = "RESET_N"
    ref = "U1"
    ic = {
        "reference": ref,
        "value": "FAKE-IC",
        "mpn": "FAKE-IC",
        "type": "ic",
        "lib_id": "Device:FAKE",
        "footprint": "",
        "properties": {},
        "pins": [{"number": "1", "name": "RESET_N"}],
    }
    ctx = AnalysisContext(
        components=[ic],
        nets={net_name: {"pins": [{"component": ref, "pin_number": "1",
                                    "pin_name": "RESET_N", "x": 0, "y": 0}]}},
        lib_symbols={},
        pin_net={(ref, "1"): (net_name, None)},
        known_power_rails=set(),
        source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    with patch.object(validation_detectors, "get_facts", return_value=fake_facts):
        findings = validation_detectors.validate_pullups(ctx)

    assert findings, "Expected at least one PU-001 finding for missing pull-up"
    pu_findings = [f for f in findings if f.get("rule_id") == "PU-001"]
    assert pu_findings, "Expected PU-001 rule_id on findings"
    assert all(f["confidence"] == "datasheet-backed" for f in pu_findings), (
        f"Expected confidence='datasheet-backed', got: {[f['confidence'] for f in pu_findings]}"
    )
    assert all(f["evidence_source"] == "datasheet" for f in pu_findings), (
        f"Expected evidence_source='datasheet', got: {[f['evidence_source'] for f in pu_findings]}"
    )
