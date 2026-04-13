"""Unit tests for validate/ab_test.py — A/B blast-radius reporter."""

TIER = "unit"

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))

# Import via the package path so patching ab.DATA_DIR and calling
# ab.compare_one_project are consistent (same module object).
import validate.ab_test as ab
from regression._differ import extract_manifest_entry as _extract_manifest_entry

_compare_manifest_entries = ab._compare_manifest_entries
compare_one_project = ab.compare_one_project
aggregate_results = ab.aggregate_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO = "fake_owner/fake_repo"
_PROJECT = "fake_project"
_ANALYZER_TYPE = "schematic"


def _write_baseline(tmpdir, manifest, atype=_ANALYZER_TYPE):
    """Write a fake baseline file into a temp reference tree."""
    bl_dir = (Path(tmpdir) / "reference" / _REPO / _PROJECT / "baselines")
    bl_dir.mkdir(parents=True, exist_ok=True)
    (bl_dir / f"{atype}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    # Write minimal metadata
    (bl_dir / "metadata.json").write_text(
        json.dumps({"repo": _REPO, "project": _PROJECT, "project_path": "."}),
        encoding="utf-8",
    )


def _write_output(tmpdir, file_key, data, atype=_ANALYZER_TYPE):
    """Write a fake analyzer output JSON into a temp results tree."""
    out_dir = Path(tmpdir) / "results" / "outputs" / atype / _REPO
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / file_key).write_text(json.dumps(data), encoding="utf-8")


def _make_schematic_output(n_components=5, n_nets=3, signal_counts=None):
    """Build a minimal schematic analyzer output dict."""
    components = [
        {"reference": f"R{i}", "type": "resistor", "value": "10k"}
        for i in range(n_components)
    ]
    sc = signal_counts or {}
    sa = {k: [{"ref": "R1"}] * v for k, v in sc.items()}
    return {
        "file": "test.kicad_sch",
        "components": components,
        "nets": {f"net{i}": {} for i in range(n_nets)},
        "labels": [],
        "power_symbols": [],
        "no_connects": [],
        "bom": [{"references": ["R1"], "quantity": 1}],
        "statistics": {
            "total_components": n_components,
            "total_nets": n_nets,
            "total_labels": 0,
            "total_power_symbols": 0,
        },
        "signal_analysis": sa,
        "design_analysis": {},
    }


# ---------------------------------------------------------------------------
# Tests for _compare_manifest_entries
# ---------------------------------------------------------------------------

def test_compare_identical_entries_no_changes():
    entry = {
        "total_components": 10,
        "total_nets": 5,
        "signal_counts": {"voltage_dividers": 2},
        "sections": ["components", "nets"],
    }
    result = _compare_manifest_entries(entry, entry.copy())
    assert result == {}, f"Expected no changes, got {result}"


def test_compare_count_change_detected():
    base = {"total_components": 10, "total_nets": 5}
    curr = {"total_components": 12, "total_nets": 5}
    result = _compare_manifest_entries(base, curr)
    assert "total_components" in result
    assert result["total_components"]["delta"] == 2


def test_compare_signal_count_change_detected():
    base = {"signal_counts": {"voltage_dividers": 2, "filters": 1}}
    curr = {"signal_counts": {"voltage_dividers": 3, "filters": 1}}
    result = _compare_manifest_entries(base, curr)
    assert "signal_counts" in result
    assert "voltage_dividers" in result["signal_counts"]
    assert result["signal_counts"]["voltage_dividers"]["delta"] == 1
    assert "filters" not in result["signal_counts"]


def test_compare_new_section_detected():
    base = {"sections": ["components", "nets"]}
    curr = {"sections": ["components", "nets", "signal_analysis"]}
    result = _compare_manifest_entries(base, curr)
    assert "sections" in result
    assert "signal_analysis" in result["sections"]["new"]
    assert result["sections"]["lost"] == []


def test_compare_lost_section_detected():
    base = {"sections": ["components", "nets", "old_section"]}
    curr = {"sections": ["components", "nets"]}
    result = _compare_manifest_entries(base, curr)
    assert "sections" in result
    assert "old_section" in result["sections"]["lost"]
    assert result["sections"]["new"] == []


def test_compare_component_types_change():
    base = {"component_types": {"resistor": 5, "capacitor": 3}}
    curr = {"component_types": {"resistor": 6, "capacitor": 3}}
    result = _compare_manifest_entries(base, curr)
    assert "component_types" in result
    assert "resistor" in result["component_types"]
    assert result["component_types"]["resistor"]["delta"] == 1
    assert "capacitor" not in result["component_types"]


# ---------------------------------------------------------------------------
# Tests for compare_one_project (integration-style, uses temp dirs)
# ---------------------------------------------------------------------------

def _patched_compare(tmpdir, project_path, manifest, output_data_map, atype=_ANALYZER_TYPE):
    """Run compare_one_project with DATA_DIR / OUTPUTS_DIR redirected to tmpdir.

    We patch the module globals on the same module object that compare_one_project
    belongs to (ab == validate.ab_test), so the redirect is visible inside the
    function.
    """
    orig_data = ab.DATA_DIR
    orig_outputs = ab.OUTPUTS_DIR
    try:
        ab.DATA_DIR = Path(tmpdir) / "reference"
        ab.OUTPUTS_DIR = Path(tmpdir) / "results" / "outputs"

        _write_baseline(tmpdir, manifest, atype)
        for file_key, data in output_data_map.items():
            _write_output(tmpdir, file_key, data, atype)

        return ab.compare_one_project(_REPO, _PROJECT, project_path, [atype])
    finally:
        ab.DATA_DIR = orig_data
        ab.OUTPUTS_DIR = orig_outputs


def test_compare_project_no_baselines_no_outputs():
    """When there are no baselines and no outputs, result is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_data = ab.DATA_DIR
        orig_outputs = ab.OUTPUTS_DIR
        try:
            ab.DATA_DIR = Path(tmpdir) / "reference"
            ab.OUTPUTS_DIR = Path(tmpdir) / "results" / "outputs"
            result = ab.compare_one_project(_REPO, _PROJECT, ".", ["schematic"])
        finally:
            ab.DATA_DIR = orig_data
            ab.OUTPUTS_DIR = orig_outputs

    # No baseline → nothing to compare
    assert result == {}, f"Expected empty result, got {result}"


def test_compare_project_matching_output_zero_changes():
    """Matching baseline and output → zero changed files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = _make_schematic_output(n_components=5, n_nets=3)
        entry = _extract_manifest_entry(output, "schematic")
        manifest = {"test.kicad_sch.json": entry}

        result = _patched_compare(tmpdir, ".", manifest,
                                  {"test.kicad_sch.json": output})

    assert "schematic" in result, f"Expected schematic key, got {result}"
    r = result["schematic"]
    assert r["compared"] == 1
    assert r["changed"] == 0, f"Expected 0 changed, got {r['changed']}"


def test_compare_project_different_output_changes_detected():
    """Different baseline and output → change detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Baseline uses 5 components; output now has 8
        baseline_output = _make_schematic_output(n_components=5, n_nets=3)
        current_output = _make_schematic_output(n_components=8, n_nets=3)

        baseline_entry = _extract_manifest_entry(baseline_output, "schematic")
        manifest = {"test.kicad_sch.json": baseline_entry}

        result = _patched_compare(tmpdir, ".", manifest,
                                  {"test.kicad_sch.json": current_output})

    assert "schematic" in result
    r = result["schematic"]
    assert r["compared"] == 1
    assert r["changed"] == 1, f"Expected 1 changed, got {r['changed']}"
    # total_components should appear in field_hits
    assert "total_components" in r["field_hits"], \
        f"Expected total_components in field_hits, got {r['field_hits']}"


def test_compare_project_signal_count_change():
    """Signal count change is attributed to the correct field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        baseline_output = _make_schematic_output(
            signal_counts={"voltage_dividers": 1})
        current_output = _make_schematic_output(
            signal_counts={"voltage_dividers": 3})

        baseline_entry = _extract_manifest_entry(baseline_output, "schematic")
        manifest = {"test.kicad_sch.json": baseline_entry}

        result = _patched_compare(tmpdir, ".", manifest,
                                  {"test.kicad_sch.json": current_output})

    assert "schematic" in result
    r = result["schematic"]
    assert r["changed"] == 1
    assert "signal_analysis.voltage_dividers" in r["field_hits"], \
        f"Expected signal field in hits, got {r['field_hits']}"


# ---------------------------------------------------------------------------
# Tests for aggregate_results
# ---------------------------------------------------------------------------

def test_aggregate_empty_input():
    summary = aggregate_results({}, ["schematic"])
    assert summary["total_files"] == 0
    assert summary["changed_files"] == 0
    assert summary["repos_changed"] == {}


def test_aggregate_zero_changes():
    """All unchanged → blast radius is zero."""
    repo_results = {
        "owner/repo1": {
            "schematic": {
                "compared": 10,
                "changed": 0,
                "only_baseline": [],
                "only_current": [],
                "field_hits": {},
                "new_sections": {},
                "lost_sections": {},
            }
        }
    }
    summary = aggregate_results(repo_results, ["schematic"])
    assert summary["total_files"] == 10
    assert summary["changed_files"] == 0
    assert summary["repos_changed"] == {}


def test_aggregate_some_changes():
    """Changes are aggregated correctly across repos."""
    repo_results = {
        "owner/repo1": {
            "schematic": {
                "compared": 10,
                "changed": 3,
                "only_baseline": [],
                "only_current": [],
                "field_hits": {"total_components": 2, "total_nets": 1},
                "new_sections": {"design_intent": 1},
                "lost_sections": {},
            }
        },
        "owner/repo2": {
            "schematic": {
                "compared": 5,
                "changed": 5,
                "only_baseline": [],
                "only_current": [],
                "field_hits": {"total_components": 5},
                "new_sections": {},
                "lost_sections": {},
            }
        },
    }
    summary = aggregate_results(repo_results, ["schematic"])
    assert summary["total_files"] == 15
    assert summary["changed_files"] == 8
    assert summary["field_hits"]["total_components"] == 7
    assert summary["field_hits"]["total_nets"] == 1
    assert summary["new_sections"]["design_intent"] == 1
    assert set(summary["repos_changed"].keys()) == {"owner/repo1", "owner/repo2"}
    # repo2 had more changes, should be listed first
    repos_list = list(summary["repos_changed"].keys())
    assert repos_list[0] == "owner/repo2"


def test_aggregate_pct_calculation():
    repo_results = {
        "owner/repo1": {
            "schematic": {
                "compared": 100,
                "changed": 25,
                "only_baseline": [],
                "only_current": [],
                "field_hits": {},
                "new_sections": {},
                "lost_sections": {},
            }
        }
    }
    summary = aggregate_results(repo_results, ["schematic"])
    assert summary["total_files"] == 100
    assert summary["changed_files"] == 25
    assert summary["unchanged_files"] == 75


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

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
        except Exception as e:
            failed += 1
            print(f"  ERROR: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
