"""Catalog tags, reclassification rules and SPICE coverage read the emitted full detector
names (code A5-F10): every domain tag in repo_catalog.json was 0."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "tools"))
sys.path.insert(0, str(HARNESS))

pytestmark = pytest.mark.unit


def test_catalog_domain_tags_from_full_names():
    import generate_catalog as gc
    entry = {"design_domains": ["detect_power_regulators", "detect_rf_chains", "detect_key_matrices"],
             "complexity": {}, "stats": {}}
    tags = gc._generate_tags(entry)
    assert {"power", "rf", "keyboard"} <= set(tags)


def test_spice_coverage_counts_real_detectors():
    import spice_coverage as sc
    data = {"findings": [{"detector": "detect_current_sense"}, {"detector": "detect_decoupling"},
                         {"detector": "detect_rf_matching"}, {"detector": "detect_bms_systems"}]}
    counts = sc.count_detections(data)
    assert counts["current_sense"] == counts["decoupling"] == counts["rf_matching"] == 1
    assert counts["bms_systems"] == 1


def test_reclassify_strong_detectors_match_full_names():
    import reclassify_repos as rr
    rule = next(r for r in rr.CLASSIFICATION_RULES if r["category"] == "Keyboards")
    entry = {"repo": "o/thing", "detectors_fired": {"detect_key_matrices": 3}}
    score, reasons = rr._score_repo(entry, {}, rule)
    assert any("key_matrices" in r for r in reasons) and score >= 3
