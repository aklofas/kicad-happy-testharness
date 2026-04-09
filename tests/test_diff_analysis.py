"""Unit tests for diff_analysis.py and detection_schema.compute_detection_id."""

TIER = "unit"

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import analysis_cache
import diff_analysis
from detection_schema import compute_detection_id


# ============================================================
# Helper: create a temp analysis dir with N runs
# ============================================================

def _make_analysis_dir_with_runs(n_runs, output_type="schematic",
                                 output_data_fn=None):
    """Create a temp project with n_runs analysis runs.

    output_data_fn(i) -> dict to write as the output JSON for run i (0-based).
    Returns (analysis_dir, run_ids_newest_first, tmpdir).
    Caller must shutil.rmtree(tmpdir).
    """
    tmpdir = tempfile.mkdtemp(prefix="test_da_")
    project_dir = tmpdir
    analysis_dir = analysis_cache.ensure_analysis_dir(project_dir, "test.kicad_pro")

    run_ids = []
    for i in range(n_runs):
        outputs_dir = tempfile.mkdtemp(prefix="test_da_out_")
        try:
            data = (output_data_fn(i) if output_data_fn
                    else {"analyzer_type": output_type, "components": []})
            filename = analysis_cache.CANONICAL_OUTPUTS.get(
                output_type, f"{output_type}.json")
            with open(os.path.join(outputs_dir, filename), "w") as f:
                json.dump(data, f)
            rid = analysis_cache.create_run(
                analysis_dir, outputs_dir,
                source_hashes={"test.kicad_sch": f"sha256:hash{i}"},
                scripts={output_type: "analyze.py"},
                run_id=f"2026-01-0{i + 1}_1200")
            run_ids.append(rid)
        finally:
            shutil.rmtree(outputs_dir)

    # run_ids is in creation order (oldest first); reverse for newest-first
    run_ids_newest = list(reversed(run_ids))
    return analysis_dir, run_ids_newest, tmpdir


# ============================================================
# 3a. Cache integration (5 tests)
# ============================================================

def test_list_runs_newest_first():
    """list_runs returns runs sorted newest-first."""
    analysis_dir, expected_ids, tmpdir = _make_analysis_dir_with_runs(3)
    try:
        runs = analysis_cache.list_runs(analysis_dir)
        actual_ids = [r[0] for r in runs]
        assert actual_ids == expected_ids, (
            f"Expected newest-first {expected_ids}, got {actual_ids}")
    finally:
        shutil.rmtree(tmpdir)


def test_list_runs_respects_limit():
    """list_runs with limit=2 returns at most 2 entries."""
    analysis_dir, expected_ids, tmpdir = _make_analysis_dir_with_runs(3)
    try:
        runs = analysis_cache.list_runs(analysis_dir, limit=2)
        assert len(runs) == 2, f"Expected 2 runs, got {len(runs)}"
        actual_ids = [r[0] for r in runs]
        assert actual_ids == expected_ids[:2]
    finally:
        shutil.rmtree(tmpdir)


def test_analysis_dir_resolves_current_and_previous():
    """With 3 runs, current is newest, previous is second-newest."""
    analysis_dir, expected_ids, tmpdir = _make_analysis_dir_with_runs(3)
    try:
        all_runs = analysis_cache.list_runs(analysis_dir)
        # current = index 0 (newest)
        current_id = all_runs[0][0]
        # previous = index 1
        previous_id = all_runs[1][0]
        assert current_id == expected_ids[0], (
            f"Current should be {expected_ids[0]}, got {current_id}")
        assert previous_id == expected_ids[1], (
            f"Previous should be {expected_ids[1]}, got {previous_id}")
    finally:
        shutil.rmtree(tmpdir)


def test_explicit_run_ids():
    """Two explicit --run IDs resolve to the correct runs."""
    analysis_dir, expected_ids, tmpdir = _make_analysis_dir_with_runs(3)
    try:
        all_runs = analysis_cache.list_runs(analysis_dir)
        run_map = {r[0]: r[1] for r in all_runs}
        # Simulate --run RUN_A --run RUN_C (oldest and newest)
        oldest = expected_ids[-1]
        newest = expected_ids[0]
        assert oldest in run_map, f"Run {oldest} not in manifest"
        assert newest in run_map, f"Run {newest} not in manifest"
        assert oldest != newest
    finally:
        shutil.rmtree(tmpdir)


def test_output_type_selects_correct_file():
    """--type pcb selects pcb.json from the run."""
    tmpdir = tempfile.mkdtemp(prefix="test_da_")
    try:
        project_dir = tmpdir
        analysis_dir = analysis_cache.ensure_analysis_dir(
            project_dir, "test.kicad_pro")
        # Create run with both schematic.json and pcb.json
        outputs_dir = tempfile.mkdtemp(prefix="test_da_out_")
        try:
            with open(os.path.join(outputs_dir, "schematic.json"), "w") as f:
                json.dump({"analyzer_type": "schematic"}, f)
            with open(os.path.join(outputs_dir, "pcb.json"), "w") as f:
                json.dump({"analyzer_type": "pcb", "footprints": [],
                           "tracks": []}, f)
            rid = analysis_cache.create_run(
                analysis_dir, outputs_dir,
                source_hashes={}, scripts={},
                run_id="2026-01-01_1200")
        finally:
            shutil.rmtree(outputs_dir)

        # Check pcb.json exists in run
        pcb_path = os.path.join(analysis_dir, rid,
                                analysis_cache.CANONICAL_OUTPUTS["pcb"])
        assert os.path.isfile(pcb_path), "pcb.json not in run folder"
        with open(pcb_path) as f:
            data = json.load(f)
        assert data["analyzer_type"] == "pcb"
    finally:
        shutil.rmtree(tmpdir)


def test_error_only_one_run_previous_requested():
    """With only 1 run, requesting 'previous' should fail."""
    analysis_dir, _, tmpdir = _make_analysis_dir_with_runs(1)
    try:
        all_runs = analysis_cache.list_runs(analysis_dir)
        assert len(all_runs) == 1, f"Expected 1 run, got {len(all_runs)}"
        # Simulate the resolution logic from diff_analysis.main:
        # "previous" requires at least 2 runs
        has_previous = len(all_runs) >= 2
        assert not has_previous, "Should not have 'previous' with only 1 run"
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# 3b. Change attribution (3 tests)
# ============================================================

def _make_schematic_json(components, signal_analysis):
    """Build a minimal schematic JSON."""
    return {
        "analyzer_type": "schematic",
        "statistics": {"total_components": len(components)},
        "components": components,
        "signal_analysis": signal_analysis,
        "bom": [],
        "connectivity_issues": {},
        "design_analysis": {},
    }


def test_attribution_exists_when_component_and_signal_change():
    """Modified detection is attributed to the component value change."""
    base = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "10k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 159.15}
            ],
        },
    )
    head = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "4.7k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 4700},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 338.63}
            ],
        },
    )
    result = diff_analysis.diff_schematic(base, head, threshold=1.0)

    # Should have both component and signal_analysis changes
    assert "components" in result, "Expected component changes"
    assert "signal_analysis" in result, "Expected signal analysis changes"

    # Check attribution on the modified rc_filter
    rc_mods = result["signal_analysis"]["rc_filters"]["modified"]
    assert len(rc_mods) >= 1, "Expected at least one modified rc_filter"
    mod = rc_mods[0]
    assert "attributed_to" in mod, (
        f"Expected 'attributed_to' on modified detection, got keys: {list(mod.keys())}")
    refs = [a["ref"] for a in mod["attributed_to"]]
    assert "R5" in refs, f"Expected R5 in attributed refs, got {refs}"


def test_attribution_only_with_both_component_and_signal():
    """Attribution only appears when both component AND signal changes exist."""
    base = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "10k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 159.15}
            ],
        },
    )
    # Head: signal changes but NO component changes
    head = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "10k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 340.0}
            ],
        },
    )
    result = diff_analysis.diff_schematic(base, head, threshold=1.0)

    # Signal changes exist but no component changes, so no attribution
    if "signal_analysis" in result:
        for det_type, det_diff in result["signal_analysis"].items():
            for mod in det_diff.get("modified", []):
                assert "attributed_to" not in mod, (
                    "Should not have attribution when no component changes exist")


def test_no_attribution_when_signal_changes_unrelated():
    """No attribution when component changes don't match signal detections."""
    base = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "10k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
            {"reference": "U1", "value": "LM317", "footprint": "SOT-223"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 159.15}
            ],
        },
    )
    # Head: U1 value changes but rc_filter cutoff also shifts (unrelated)
    head = _make_schematic_json(
        components=[
            {"reference": "R5", "value": "10k", "footprint": "R_0402"},
            {"reference": "C1", "value": "100nF", "footprint": "C_0402"},
            {"reference": "U1", "value": "LM7805", "footprint": "SOT-223"},
        ],
        signal_analysis={
            "rc_filters": [
                {"resistor": {"ref": "R5", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": 340.0}
            ],
        },
    )
    result = diff_analysis.diff_schematic(base, head, threshold=1.0)

    # U1 changed value but is not referenced in rc_filter, so no attribution
    if "signal_analysis" in result:
        rc_diff = result["signal_analysis"].get("rc_filters", {})
        for mod in rc_diff.get("modified", []):
            attr = mod.get("attributed_to", [])
            attr_refs = [a["ref"] for a in attr]
            assert "U1" not in attr_refs, (
                "U1 should not be attributed to rc_filter change")


# ============================================================
# 3c. Regression detection (8 tests)
# ============================================================

def test_regression_schematic_new_erc_warning():
    """New ERC warning -> regression with severity 'breaking'."""
    diff_result = {
        "erc": {
            "new_warnings": [
                {"type": "unconnected_pin", "net": "VCC", "message": "Pin unconnected"}
            ],
        },
    }
    regressions = diff_analysis.classify_regressions("schematic", diff_result)
    assert len(regressions) >= 1
    erc_regs = [r for r in regressions if r["category"] == "erc"]
    assert len(erc_regs) == 1
    assert erc_regs[0]["severity"] == "breaking"


def test_regression_schematic_new_single_pin_net():
    """New single_pin_net -> regression with severity 'major'."""
    diff_result = {
        "connectivity": {
            "single_pin_nets": {
                "new": ["Net-R1-Pad1"],
            },
        },
    }
    regressions = diff_analysis.classify_regressions("schematic", diff_result)
    assert len(regressions) >= 1
    conn_regs = [r for r in regressions if r["category"] == "connectivity"]
    assert len(conn_regs) == 1
    assert conn_regs[0]["severity"] == "major"


def test_regression_schematic_removed_protection_device():
    """Removed protection device -> regression with severity 'major'."""
    diff_result = {
        "signal_analysis": {
            "protection_devices": {
                "removed": [
                    {"reference": "D1", "type": "TVS"},
                ],
            },
        },
    }
    regressions = diff_analysis.classify_regressions("schematic", diff_result)
    assert len(regressions) >= 1
    prot_regs = [r for r in regressions if r["category"] == "protection"]
    assert len(prot_regs) == 1
    assert prot_regs[0]["severity"] == "major"


def test_regression_emc_new_critical_finding():
    """New CRITICAL EMC finding -> regression with severity 'breaking'."""
    diff_result = {
        "findings": {
            "new": [
                {"rule_id": "GND-001", "severity": "CRITICAL",
                 "title": "Missing ground plane"},
            ],
        },
    }
    regressions = diff_analysis.classify_regressions("emc", diff_result)
    assert len(regressions) >= 1
    emc_regs = [r for r in regressions if r["category"] == "emc"]
    assert len(emc_regs) == 1
    assert emc_regs[0]["severity"] == "breaking"


def test_regression_emc_risk_score_increase():
    """EMC risk score increase -> regression with severity 'major'."""
    diff_result = {
        "risk_score": {"base": 42, "head": 58, "delta": 16},
    }
    regressions = diff_analysis.classify_regressions("emc", diff_result)
    assert len(regressions) >= 1
    risk_regs = [r for r in regressions if r["category"] == "emc_risk"]
    assert len(risk_regs) == 1
    assert risk_regs[0]["severity"] == "major"


def test_regression_spice_pass_to_fail():
    """SPICE pass->fail -> regression with severity 'breaking'."""
    diff_result = {
        "status_changes": [
            {"subcircuit_type": "rc_filter", "components": ["R1", "C1"],
             "base_status": "pass", "head_status": "fail"},
        ],
    }
    regressions = diff_analysis.classify_regressions("spice", diff_result)
    assert len(regressions) >= 1
    spice_regs = [r for r in regressions if r["category"] == "spice"]
    assert len(spice_regs) == 1
    assert spice_regs[0]["severity"] == "breaking"


def test_regression_pcb_unrouted_increase():
    """PCB unrouted count increase -> regression with severity 'major'."""
    diff_result = {
        "unrouted": {
            "connectivity.unrouted_count": {"base": 0, "head": 3, "delta": 3},
        },
    }
    regressions = diff_analysis.classify_regressions("pcb", diff_result)
    assert len(regressions) >= 1
    routing_regs = [r for r in regressions if r["category"] == "routing"]
    assert len(routing_regs) >= 1
    assert routing_regs[0]["severity"] == "major"


def test_no_regressions_on_improvements():
    """No regressions when changes are improvements."""
    # EMC: findings resolved, risk score decreased
    diff_result = {
        "findings": {
            "new": [],
            "resolved": [
                {"rule_id": "GND-001", "severity": "CRITICAL",
                 "title": "Missing ground plane"},
            ],
        },
        "risk_score": {"base": 58, "head": 42, "delta": -16},
    }
    regressions = diff_analysis.classify_regressions("emc", diff_result)
    # Risk score decrease (delta < 0) should not be flagged
    risk_regs = [r for r in regressions if r["category"] == "emc_risk"]
    assert len(risk_regs) == 0, "Decreasing risk score should not be a regression"
    # Resolved findings are not regressions
    emc_regs = [r for r in regressions if r["category"] == "emc"]
    assert len(emc_regs) == 0, "Resolved findings should not be regressions"


# ============================================================
# 3d. Stable detection IDs (5 tests)
# ============================================================

def test_detection_id_deterministic():
    """Same input -> same output."""
    det = {"resistor": {"ref": "R5", "ohms": 10000},
           "capacitor": {"ref": "C1", "farads": 1e-7}}
    id1 = compute_detection_id(det, "rc_filters")
    id2 = compute_detection_id(det, "rc_filters")
    assert id1 == id2, f"Expected deterministic, got {id1!r} vs {id2!r}"


def test_detection_id_different_components():
    """Different components -> different IDs."""
    det_a = {"resistor": {"ref": "R5", "ohms": 10000},
             "capacitor": {"ref": "C1", "farads": 1e-7}}
    det_b = {"resistor": {"ref": "R10", "ohms": 10000},
             "capacitor": {"ref": "C2", "farads": 1e-7}}
    id_a = compute_detection_id(det_a, "rc_filters")
    id_b = compute_detection_id(det_b, "rc_filters")
    assert id_a != id_b, f"Different components should produce different IDs"


def test_detection_id_format():
    """ID format is det_type:xxxxxxxxxxxx (type prefix + colon + 12 hex chars)."""
    det = {"resistor": {"ref": "R1", "ohms": 1000},
           "capacitor": {"ref": "C1", "farads": 1e-9}}
    did = compute_detection_id(det, "rc_filters")
    assert did.startswith("rc_filters:"), (
        f"Expected 'rc_filters:' prefix, got {did!r}")
    parts = did.split(":")
    assert len(parts) == 2, f"Expected exactly one colon, got {did!r}"
    hex_part = parts[1]
    assert len(hex_part) == 12, (
        f"Expected 12 hex chars after colon, got {len(hex_part)}")
    assert re.match(r'^[0-9a-f]{12}$', hex_part), (
        f"Expected hex chars, got {hex_part!r}")


def test_diff_matching_uses_detection_id():
    """R5->R10 renumber with same detection_id = no change (matched by ID)."""
    base_items = [
        {"detection_id": "rc_filters:abcdef123456",
         "resistor": {"ref": "R5", "ohms": 10000},
         "capacitor": {"ref": "C1", "farads": 1e-7},
         "cutoff_hz": 159.15}
    ]
    head_items = [
        {"detection_id": "rc_filters:abcdef123456",
         "resistor": {"ref": "R10", "ohms": 10000},
         "capacitor": {"ref": "C1", "farads": 1e-7},
         "cutoff_hz": 159.15}
    ]
    result = diff_analysis._diff_lists(
        base_items, head_items,
        id_fields=["resistor.ref", "capacitor.ref"],
        value_fields=["cutoff_hz"],
        threshold=1.0)
    # detection_id matches, so item is found (not added/removed)
    assert len(result["added"]) == 0, (
        f"Should not have added items when detection_id matches: {result['added']}")
    assert len(result["removed"]) == 0, (
        f"Should not have removed items when detection_id matches: {result['removed']}")
    # Value unchanged, so not modified either
    assert result["unchanged_count"] == 1


def test_diff_falls_back_to_identity_fields():
    """Without detection_id, falls back to identity fields for matching."""
    base_items = [
        {"resistor": {"ref": "R5", "ohms": 10000},
         "capacitor": {"ref": "C1", "farads": 1e-7},
         "cutoff_hz": 159.15}
    ]
    head_items = [
        {"resistor": {"ref": "R5", "ohms": 4700},
         "capacitor": {"ref": "C1", "farads": 1e-7},
         "cutoff_hz": 338.63}
    ]
    result = diff_analysis._diff_lists(
        base_items, head_items,
        id_fields=["resistor.ref", "capacitor.ref"],
        value_fields=["cutoff_hz"],
        threshold=1.0)
    # Matched by identity fields (R5::C1), so it should be modified, not added/removed
    assert len(result["added"]) == 0
    assert len(result["removed"]) == 0
    assert len(result["modified"]) == 1
    assert result["modified"][0]["changes"][0]["field"] == "cutoff_hz"


# ============================================================
# 3e. Trend extraction (3 tests)
# ============================================================

def _make_schematic_with_cutoff(cutoff_hz):
    """Build a minimal schematic JSON with one rc_filter detection."""
    return {
        "analyzer_type": "schematic",
        "statistics": {"total_components": 2},
        "components": [
            {"reference": "R1", "value": "10k"},
            {"reference": "C1", "value": "100nF"},
        ],
        "signal_analysis": {
            "rc_filters": [
                {"resistor": {"ref": "R1", "ohms": 10000},
                 "capacitor": {"ref": "C1", "farads": 1e-7},
                 "cutoff_hz": cutoff_hz}
            ],
        },
    }


def test_extract_trends_returns_correct_structure():
    """_extract_trends returns {det_type: {identity: {field: [(run_id, value)]}}}."""
    cutoffs = [150.0, 155.0, 160.0, 165.0]
    analysis_dir, run_ids, tmpdir = _make_analysis_dir_with_runs(
        4, output_type="schematic",
        output_data_fn=lambda i: _make_schematic_with_cutoff(cutoffs[i]))
    try:
        trends = diff_analysis._extract_trends(analysis_dir, "schematic", 4)
        assert "rc_filters" in trends, (
            f"Expected 'rc_filters' in trends, got keys: {list(trends.keys())}")
        # Should have one identity key (R1::C1)
        identities = list(trends["rc_filters"].keys())
        assert len(identities) >= 1, "Expected at least one identity"
        fields = trends["rc_filters"][identities[0]]
        assert "cutoff_hz" in fields, (
            f"Expected 'cutoff_hz' in fields, got: {list(fields.keys())}")
        datapoints = fields["cutoff_hz"]
        assert len(datapoints) == 4, (
            f"Expected 4 datapoints, got {len(datapoints)}")
    finally:
        shutil.rmtree(tmpdir)


def test_extract_trends_values_in_run_order():
    """Values are returned in newest-first order (from list_runs)."""
    cutoffs = [100.0, 200.0, 300.0, 400.0]
    analysis_dir, run_ids, tmpdir = _make_analysis_dir_with_runs(
        4, output_type="schematic",
        output_data_fn=lambda i: _make_schematic_with_cutoff(cutoffs[i]))
    try:
        trends = diff_analysis._extract_trends(analysis_dir, "schematic", 4)
        identities = list(trends["rc_filters"].keys())
        datapoints = trends["rc_filters"][identities[0]]["cutoff_hz"]
        # list_runs returns newest-first, so run_ids[0] is newest
        # datapoints are appended in iteration order (newest first)
        dp_run_ids = [dp[0] for dp in datapoints]
        assert dp_run_ids == run_ids, (
            f"Expected run order {run_ids}, got {dp_run_ids}")
        # Values should correspond to newest-first ordering
        dp_values = [dp[1] for dp in datapoints]
        # Newest run (index 3) had cutoff 400, oldest (index 0) had 100
        assert dp_values == [400.0, 300.0, 200.0, 100.0], (
            f"Expected [400, 300, 200, 100], got {dp_values}")
    finally:
        shutil.rmtree(tmpdir)


def test_extract_trends_missing_runs_skipped():
    """Runs without the output file are skipped gracefully."""
    analysis_dir, run_ids, tmpdir = _make_analysis_dir_with_runs(
        4, output_type="schematic",
        output_data_fn=lambda i: _make_schematic_with_cutoff(100.0 + i * 50))
    try:
        # Delete the output file from the second-newest run
        second_run_id = run_ids[1]
        output_path = os.path.join(
            analysis_dir, second_run_id, "schematic.json")
        if os.path.isfile(output_path):
            os.remove(output_path)

        trends = diff_analysis._extract_trends(analysis_dir, "schematic", 4)
        # Should still work with 3 remaining runs
        if "rc_filters" in trends:
            identities = list(trends["rc_filters"].keys())
            if identities:
                datapoints = trends["rc_filters"][identities[0]]["cutoff_hz"]
                assert len(datapoints) == 3, (
                    f"Expected 3 datapoints (one skipped), got {len(datapoints)}")
    finally:
        shutil.rmtree(tmpdir)


# ============================================================
# __main__ runner
# ============================================================

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS  {name}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
    total = passed + failed
    print(f"\n{passed}/{total} passed, {failed} failed")
    if failed:
        sys.exit(1)
