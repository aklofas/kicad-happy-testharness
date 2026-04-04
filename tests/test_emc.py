"""Unit tests for EMC analysis integration in the regression system.

Tests:
  - EMC seed assertion generation (seed.py)
  - EMC structural assertion generation (seed_structural.py)
  - EMC manifest extraction (_differ.py)
  - EMC cross-validation logic (validate_emc.py)
  - Full round-trip: generate assertions -> evaluate against same data
"""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from checks import evaluate_assertion
from _differ import extract_manifest_entry
from seed import generate_emc_assertions
from seed_structural import generate_emc_structural_assertions

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_emc import cross_validate_file


# ---------------------------------------------------------------------------
# Realistic synthetic EMC output
# ---------------------------------------------------------------------------
EMC_OUTPUT = {
    "summary": {
        "total_checks": 19,
        "critical": 1,
        "high": 4,
        "medium": 8,
        "low": 4,
        "info": 2,
        "emc_risk_score": 24,
    },
    "target_standard": "fcc-class-b",
    "findings": [
        # v1 categories
        {"category": "ground_plane", "severity": "CRITICAL", "rule_id": "GP-002",
         "title": "No ground plane", "description": "...",
         "components": ["U1", "U2"], "nets": ["GND"], "recommendation": "..."},
        {"category": "ground_plane", "severity": "HIGH", "rule_id": "GP-003",
         "title": "Fragmented ground", "description": "...",
         "components": [], "nets": ["GND"], "recommendation": "..."},
        {"category": "decoupling", "severity": "HIGH", "rule_id": "DC-001",
         "title": "Cap too far", "description": "...",
         "components": ["C1", "U1"], "nets": [], "recommendation": "..."},
        {"category": "io_filtering", "severity": "HIGH", "rule_id": "IO-001",
         "title": "Unfiltered USB", "description": "...",
         "components": ["J1"], "nets": ["USB_D+", "USB_D-"], "recommendation": "..."},
        {"category": "switching_emc", "severity": "MEDIUM", "rule_id": "SW-001",
         "title": "Harmonics in 30-88", "description": "...",
         "components": ["U4"], "nets": ["SW"], "recommendation": "..."},
        {"category": "clock_routing", "severity": "MEDIUM", "rule_id": "CK-001",
         "title": "Clock on outer layer", "description": "...",
         "components": ["Y1", "U1"], "nets": ["CLK"], "recommendation": "..."},
        {"category": "via_stitching", "severity": "LOW", "rule_id": "VS-001",
         "title": "Sparse stitching", "description": "...",
         "components": [], "nets": ["GND"], "recommendation": "..."},
        {"category": "stackup", "severity": "LOW", "rule_id": "SU-001",
         "title": "Adjacent signal layers", "description": "...",
         "components": [], "nets": [], "recommendation": "..."},
        {"category": "emission_estimate", "severity": "INFO", "rule_id": "EE-001",
         "title": "Cavity resonance", "description": "...",
         "components": [], "nets": [], "recommendation": "..."},
        # Phase 2 categories
        {"category": "diff_pair", "severity": "HIGH", "rule_id": "DP-001",
         "title": "USB skew exceeds limit", "description": "...",
         "components": [], "nets": ["USB_DP", "USB_DM"], "recommendation": "..."},
        {"category": "board_edge", "severity": "MEDIUM", "rule_id": "BE-002",
         "title": "Partial ground pour", "description": "...",
         "components": [], "nets": [], "recommendation": "..."},
        {"category": "pdn", "severity": "MEDIUM", "rule_id": "PD-001",
         "title": "Anti-resonance spike", "description": "...",
         "components": ["C5", "C6"], "nets": ["VCC"], "recommendation": "..."},
        # Phase 3 categories
        {"category": "crosstalk", "severity": "MEDIUM", "rule_id": "XT-001",
         "title": "3H violation CLK-ADC", "description": "...",
         "components": [], "nets": ["CLK", "ADC_IN"], "recommendation": "..."},
        {"category": "emi_filter", "severity": "MEDIUM", "rule_id": "EF-001",
         "title": "Filter cutoff too close", "description": "...",
         "components": ["L2"], "nets": [], "recommendation": "..."},
        {"category": "esd_path", "severity": "MEDIUM", "rule_id": "ES-001",
         "title": "TVS far from connector", "description": "...",
         "components": ["D1", "J1"], "nets": [], "recommendation": "..."},
        # Phase 4 categories
        {"category": "thermal_emc", "severity": "MEDIUM", "rule_id": "TH-001",
         "title": "DC bias derating", "description": "...",
         "components": ["C10"], "nets": [], "recommendation": "..."},
        {"category": "thermal_emc", "severity": "LOW", "rule_id": "TH-002",
         "title": "Ferrite near SMPS", "description": "...",
         "components": ["FB1", "U4"], "nets": [], "recommendation": "..."},
        {"category": "shielding", "severity": "INFO", "rule_id": "SH-001",
         "title": "Connector aperture", "description": "...",
         "components": ["J1"], "nets": [], "recommendation": "..."},
        {"category": "shielding", "severity": "LOW", "rule_id": "SH-001",
         "title": "Aperture near harmonic", "description": "...",
         "components": ["J2"], "nets": [], "recommendation": "..."},
    ],
    "board_info": {
        "layer_count": 4,
        "footprint_count": 85,
        "total_components": 120,
        "crystal_frequencies_hz": [8000000, 32768],
        "switching_frequencies_hz": [500000],
    },
    "test_plan": {
        "frequency_bands": [
            {"band": "30-88 MHz", "freq_min_hz": 30e6, "freq_max_hz": 88e6,
             "risk_level": "high", "source_count": 2, "sources": ["U4", "Y1"]},
            {"band": "88-216 MHz", "freq_min_hz": 88e6, "freq_max_hz": 216e6,
             "risk_level": "medium", "source_count": 1, "sources": ["U4"]},
            {"band": "216-960 MHz", "freq_min_hz": 216e6, "freq_max_hz": 960e6,
             "risk_level": "low", "source_count": 0, "sources": []},
        ],
        "interface_risks": [
            {"interface": "USB", "risk_score": 0.8},
            {"interface": "SPI", "risk_score": 0.3},
        ],
        "probe_points": [
            {"x": 30, "y": 20, "type": "inductor", "ref": "L1", "reason": "switching loop"},
            {"x": 50, "y": 40, "type": "crystal", "ref": "Y1", "reason": "clock source"},
        ],
    },
    "regulatory_coverage": {
        "market": "us",
        "applicable_standards": ["FCC Part 15 Class B", "FCC Part 15 conducted"],
        "coverage_matrix": [
            {"test_type": "radiated", "checked_rules": ["GP-001", "SW-001", "CK-001"]},
            {"test_type": "conducted", "checked_rules": ["DC-001", "IO-001"]},
        ],
    },
    "elapsed_s": 0.142,
}


# ---------------------------------------------------------------------------
# Seed assertion generation
# ---------------------------------------------------------------------------

def test_emc_seed_count():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    # total + 4 severity + score + 15 categories + standard + test_plan(2) + reg(2) = 25+
    assert len(assertions) >= 20

def test_emc_seed_total_range():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    total_a = next(a for a in assertions if "Finding count" in a["description"])
    check = total_a["check"]
    assert check["op"] == "range"
    assert check["min"] <= 19 <= check["max"]

def test_emc_seed_risk_score_range():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    score_a = next(a for a in assertions if "risk score" in a["description"])
    check = score_a["check"]
    assert check["op"] == "range"
    assert check["min"] <= 24 <= check["max"]

def test_emc_seed_severity_counts():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    sev_assertions = [a for a in assertions
                      if any(s in a["description"] for s in ("critical count", "high count", "medium count", "low count"))]
    assert len(sev_assertions) == 4  # all four are non-zero

def test_emc_seed_category_counts():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    cat_assertions = [a for a in assertions if a["check"]["op"] == "count_matches"]
    cats_found = {a["check"]["pattern"].strip("^$") for a in cat_assertions}
    assert "ground_plane" in cats_found
    assert "decoupling" in cats_found
    assert "io_filtering" in cats_found
    assert "switching_emc" in cats_found
    assert "clock_routing" in cats_found

def test_emc_seed_target_standard():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    std_a = next(a for a in assertions if "standard" in a["description"])
    assert std_a["check"]["op"] == "equals"
    assert std_a["check"]["value"] == "fcc-class-b"

def test_emc_seed_ids_unique():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_emc_seed_empty_output():
    empty = {"summary": {"total_checks": 0}, "findings": []}
    assert generate_emc_assertions(empty) == []

def test_emc_seed_test_plan():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    tp_assertions = [a for a in assertions if "test plan" in a["description"]]
    assert len(tp_assertions) == 2  # frequency_bands + probe_points
    fb_a = next(a for a in tp_assertions if "frequency" in a["description"])
    assert fb_a["check"]["op"] == "min_count"
    assert fb_a["check"]["value"] == 3

def test_emc_seed_regulatory():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    reg_assertions = [a for a in assertions if "market" in a["description"].lower()
                      or "applicable standard" in a["description"].lower()]
    assert len(reg_assertions) == 2  # market + applicable_standards
    market_a = next(a for a in reg_assertions if "market" in a["description"].lower())
    assert market_a["check"]["op"] == "equals"
    assert market_a["check"]["value"] == "us"

def test_emc_seed_no_test_plan():
    """Output without test_plan section generates no test_plan assertions."""
    data = dict(EMC_OUTPUT)
    data = {k: v for k, v in data.items() if k != "test_plan"}
    assertions = generate_emc_assertions(data)
    tp_assertions = [a for a in assertions if "test plan" in a["description"]]
    assert len(tp_assertions) == 0

def test_emc_seed_no_critical():
    data = dict(EMC_OUTPUT)
    data["summary"] = dict(data["summary"])
    data["summary"]["critical"] = 0
    assertions = generate_emc_assertions(data)
    descs = [a["description"] for a in assertions]
    assert not any("critical count" in d for d in descs)


# ---------------------------------------------------------------------------
# Structural assertion generation
# ---------------------------------------------------------------------------

def test_emc_structural_category_counts():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    cat_assertions = [a for a in assertions if "finding(s)" in a["description"]]
    assert len(cat_assertions) == 16  # 16 unique categories in EMC_OUTPUT

def test_emc_structural_rule_ids():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    rule_assertions = [a for a in assertions if "Rule " in a["description"]]
    rules_found = {a["description"].split("Rule ")[1].split(" ")[0] for a in rule_assertions}
    # v1 rules
    assert "GP-002" in rules_found
    assert "DC-001" in rules_found
    assert "IO-001" in rules_found
    assert "SW-001" in rules_found
    assert "CK-001" in rules_found
    # Phase 2-4 rules
    assert "DP-001" in rules_found
    assert "BE-002" in rules_found
    assert "XT-001" in rules_found
    assert "ES-001" in rules_found
    assert "TH-001" in rules_found
    assert "SH-001" in rules_found

def test_emc_structural_component_refs():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    ref_assertions = [a for a in assertions if "in EMC findings" in a["description"]]
    refs_found = {a["description"].split(" ")[0] for a in ref_assertions}
    assert "U1" in refs_found
    assert "J1" in refs_found
    assert "U4" in refs_found
    assert "Y1" in refs_found

def test_emc_structural_ids_unique():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    ids = [a["id"] for a in assertions]
    assert len(ids) == len(set(ids))

def test_emc_structural_empty():
    assert generate_emc_structural_assertions({"findings": []}) == []

def test_emc_structural_deduplicates_refs():
    """Same component in multiple findings gets one assertion."""
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    u1_assertions = [a for a in assertions if a["description"] == "U1 in EMC findings"]
    assert len(u1_assertions) == 1  # U1 appears in GP-002, DC-001, and CK-001


# ---------------------------------------------------------------------------
# Round-trip: seed assertions -> evaluate against same data
# ---------------------------------------------------------------------------

def test_emc_seed_roundtrip():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    for a in assertions:
        result = evaluate_assertion(a, EMC_OUTPUT)
        assert result["passed"], (
            f"Assertion {a['id']} failed: {a['description']} "
            f"— actual={result.get('actual')}, expected={result.get('expected')}")

def test_emc_structural_roundtrip():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    for a in assertions:
        result = evaluate_assertion(a, EMC_OUTPUT)
        assert result["passed"], (
            f"Assertion {a['id']} failed: {a['description']} "
            f"— actual={result.get('actual')}, expected={result.get('expected')}")

def test_emc_seed_detects_regression():
    assertions = generate_emc_assertions(EMC_OUTPUT)
    degraded = {
        "summary": {"total_checks": 3, "critical": 0, "high": 1, "medium": 1,
                     "low": 1, "info": 0, "emc_risk_score": 86},
        "target_standard": "fcc-class-b",
        "findings": [
            {"category": "decoupling", "severity": "HIGH", "rule_id": "DC-001",
             "components": [], "nets": []},
            {"category": "clock_routing", "severity": "MEDIUM", "rule_id": "CK-001",
             "components": [], "nets": []},
            {"category": "stackup", "severity": "LOW", "rule_id": "SU-001",
             "components": [], "nets": []},
        ],
    }
    failures = [a for a in assertions if not evaluate_assertion(a, degraded)["passed"]]
    assert len(failures) > 0, "Should detect regression from 12->3 findings"

def test_emc_structural_detects_missing_rule():
    assertions = generate_emc_structural_assertions(EMC_OUTPUT)
    # Remove all GP-002 findings
    modified = dict(EMC_OUTPUT)
    modified["findings"] = [f for f in EMC_OUTPUT["findings"]
                            if f.get("rule_id") != "GP-002"]
    gp002_assertions = [a for a in assertions if "GP-002" in a["description"]]
    assert len(gp002_assertions) > 0
    for a in gp002_assertions:
        result = evaluate_assertion(a, modified)
        assert not result["passed"], "GP-002 assertion should fail when rule removed"


# ---------------------------------------------------------------------------
# Manifest extraction
# ---------------------------------------------------------------------------

def test_emc_manifest_extraction():
    entry = extract_manifest_entry(EMC_OUTPUT, "emc")
    assert entry["total_findings"] == 19
    assert entry["critical"] == 1
    assert entry["high"] == 4
    assert entry["medium"] == 8
    assert entry["low"] == 4
    assert entry["emc_risk_score"] == 24
    assert entry["target_standard"] == "fcc-class-b"
    assert entry["by_category"]["ground_plane"] == 2
    assert entry["by_category"]["diff_pair"] == 1
    assert entry["by_category"]["thermal_emc"] == 2
    assert entry["by_category"]["shielding"] == 2

def test_emc_manifest_zero_findings():
    data = {"summary": {"total_checks": 0, "emc_risk_score": 100},
            "target_standard": "fcc-class-b", "findings": []}
    entry = extract_manifest_entry(data, "emc")
    assert entry["total_findings"] == 0
    assert entry["emc_risk_score"] == 100
    assert entry["by_category"] == {}


# ---------------------------------------------------------------------------
# Cross-validation (validate_emc.py)
# ---------------------------------------------------------------------------

def test_crossval_layer_count_match():
    emc = {"board_info": {"layer_count": 4}, "findings": []}
    pcb = {"statistics": {"copper_layers_used": 4}}
    results = cross_validate_file(None, pcb, emc)
    layer_r = [r for r in results if r["check"] == "layer_count"]
    assert len(layer_r) == 1
    assert layer_r[0]["status"] == "match"

def test_crossval_layer_count_mismatch():
    emc = {"board_info": {"layer_count": 4}, "findings": []}
    pcb = {"statistics": {"copper_layers_used": 2}}
    results = cross_validate_file(None, pcb, emc)
    layer_r = [r for r in results if r["check"] == "layer_count"]
    assert len(layer_r) == 1
    assert layer_r[0]["status"] == "mismatch"

def test_crossval_crystal_frequencies():
    emc = {"board_info": {"crystal_frequencies_hz": [8e6, 32768]}, "findings": []}
    sch = {"signal_analysis": {"crystal_circuits": [
        {"frequency": 8e6}, {"frequency": 32768}
    ]}, "statistics": {}}
    results = cross_validate_file(sch, None, emc)
    xtal_r = [r for r in results if r["check"] == "crystal_frequencies"]
    assert len(xtal_r) == 1
    assert xtal_r[0]["status"] == "match"

def test_crossval_component_count():
    emc = {"board_info": {"total_components": 42}, "findings": []}
    sch = {"statistics": {"total_components": 42}, "signal_analysis": {}}
    results = cross_validate_file(sch, None, emc)
    comp_r = [r for r in results if r["check"] == "component_count"]
    assert len(comp_r) == 1
    assert comp_r[0]["status"] == "match"

def test_crossval_empty():
    results = cross_validate_file(None, None, {"board_info": {}, "findings": []})
    assert results == []

def test_crossval_regulatory_market_consistency():
    emc = {"board_info": {}, "findings": [],
           "target_standard": "fcc-class-b",
           "regulatory_coverage": {"market": "us"}}
    results = cross_validate_file(None, None, emc)
    market_r = [r for r in results if r["check"] == "regulatory_market_consistency"]
    assert len(market_r) == 1
    assert market_r[0]["status"] == "match"

def test_crossval_regulatory_market_mismatch():
    emc = {"board_info": {}, "findings": [],
           "target_standard": "fcc-class-b",
           "regulatory_coverage": {"market": "eu"}}  # wrong market for FCC
    results = cross_validate_file(None, None, emc)
    market_r = [r for r in results if r["check"] == "regulatory_market_consistency"]
    assert len(market_r) == 1
    assert market_r[0]["status"] == "mismatch"

def test_crossval_test_plan_bands():
    emc = {"board_info": {}, "findings": [],
           "test_plan": {"frequency_bands": [
               {"band": "30-88MHz", "source_count": 2, "sources": ["U1", "Y1"]},
               {"band": "88-216MHz", "source_count": 0, "sources": []},
           ]}}
    sch = {"signal_analysis": {"crystal_circuits": [{"reference": "Y1", "frequency": 8e6}],
                               "power_regulators": [{"ref": "U1", "topology": "buck"}]},
           "statistics": {}}
    results = cross_validate_file(sch, None, emc)
    tp_r = [r for r in results if r["check"] == "test_plan_frequency_bands"]
    assert len(tp_r) == 1
    assert tp_r[0]["emc_value"] == 1  # 1 band with sources


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_emc_single_finding():
    data = {
        "summary": {"total_checks": 1, "critical": 0, "high": 0,
                     "medium": 1, "low": 0, "info": 0, "emc_risk_score": 97},
        "target_standard": "fcc-class-b",
        "findings": [
            {"category": "via_stitching", "severity": "MEDIUM", "rule_id": "VS-001",
             "components": [], "nets": ["GND"]},
        ],
    }
    seed = generate_emc_assertions(data)
    struct = generate_emc_structural_assertions(data)
    assert len(seed) >= 3  # total + medium + score + category + standard
    assert len(struct) >= 2  # category count + rule_id
    for a in seed + struct:
        assert evaluate_assertion(a, data)["passed"]

def test_emc_all_categories():
    categories = ["ground_plane", "decoupling", "io_filtering", "switching_emc",
                   "clock_routing", "via_stitching", "stackup", "emission_estimate",
                   "diff_pair", "board_edge", "pdn", "crosstalk",
                   "emi_filter", "esd_path", "thermal_emc", "shielding"]
    findings = [
        {"category": cat, "severity": "MEDIUM", "rule_id": f"X-{i:03d}",
         "components": [f"U{i}"], "nets": []}
        for i, cat in enumerate(categories)
    ]
    data = {
        "summary": {"total_checks": len(categories), "critical": 0, "high": 0,
                     "medium": len(categories), "low": 0, "info": 0,
                     "emc_risk_score": 100 - 3 * len(categories)},
        "target_standard": "fcc-class-b",
        "findings": findings,
    }
    seed = generate_emc_assertions(data)
    cat_assertions = [a for a in seed if a["check"]["op"] == "count_matches"]
    assert len(cat_assertions) == 16

def test_emc_schematic_only():
    """EMC output from schematic-only (no PCB info) should still work."""
    data = {
        "summary": {"total_checks": 2, "critical": 0, "high": 1,
                     "medium": 1, "low": 0, "info": 0, "emc_risk_score": 89},
        "target_standard": "fcc-class-b",
        "findings": [
            {"category": "switching_emc", "severity": "HIGH", "rule_id": "SW-001",
             "components": ["U1"], "nets": []},
            {"category": "switching_emc", "severity": "MEDIUM", "rule_id": "SW-001",
             "components": ["U1"], "nets": []},
        ],
        "board_info": {"total_components": 50},
    }
    seed = generate_emc_assertions(data)
    struct = generate_emc_structural_assertions(data)
    for a in seed + struct:
        assert evaluate_assertion(a, data)["passed"]


# === Runner ===

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
