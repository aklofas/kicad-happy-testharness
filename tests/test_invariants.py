"""Unit tests for validate/validate_invariants.py — property-based invariant checker."""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_invariants import check_invariants

HARNESS_DIR = Path(__file__).resolve().parent.parent


def _clean_output():
    """Build a minimal valid schematic output with no violations."""
    return {
        "components": [
            {"reference": "R1", "type": "resistor"},
            {"reference": "R2", "type": "resistor"},
            {"reference": "C1", "type": "capacitor"},
        ],
        "statistics": {
            "total_components": 3,
            "component_types": {"resistor": 2, "capacitor": 1},
        },
        "signal_analysis": {
            "voltage_dividers": [{"ratio": 0.5}],
            "rc_filters": [{"cutoff_hz": 159.15}],
            "lc_filters": [{"resonant_hz": 7234.32}],
            "crystal_circuits": [{"effective_load_pF": 14.0}],
        },
        "annotation_issues": {"duplicate_references": []},
    }


# 1. Clean output -> no violations
def test_clean_output_no_violations():
    data = _clean_output()
    violations = check_invariants(data, "test.json")
    assert violations == [], f"Expected no violations, got: {violations}"


# 2. Divider ratio > 1 -> violation
def test_divider_ratio_above_one():
    data = _clean_output()
    data["signal_analysis"]["voltage_dividers"] = [{"ratio": 1.5}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=1.5 >= 1" in violations[0][1]


# 3. Divider ratio = 0 -> violation
def test_divider_ratio_zero():
    data = _clean_output()
    data["signal_analysis"]["voltage_dividers"] = [{"ratio": 0}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=0 <= 0" in violations[0][1]


# 4. Divider ratio negative -> violation
def test_divider_ratio_negative():
    data = _clean_output()
    data["signal_analysis"]["voltage_dividers"] = [{"ratio": -0.3}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "ratio=-0.3 <= 0" in violations[0][1]


# 5. RC filter negative cutoff -> violation
def test_rc_filter_negative_cutoff():
    data = _clean_output()
    data["signal_analysis"]["rc_filters"] = [{"cutoff_hz": -100}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "cutoff_hz=-100 <= 0" in violations[0][1]


# 6. LC filter zero resonance -> violation
def test_lc_filter_zero_resonance():
    data = _clean_output()
    data["signal_analysis"]["lc_filters"] = [{"resonant_hz": 0}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "resonant_hz=0 <= 0" in violations[0][1]


# 7. Crystal negative load -> violation
def test_crystal_negative_load():
    data = _clean_output()
    data["signal_analysis"]["crystal_circuits"] = [{"effective_load_pF": -5.0}]
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "effective_load_pF=-5.0 <= 0" in violations[0][1]


# 8. Component types sum exceeds total -> violation
def test_component_types_exceed_total():
    data = _clean_output()
    data["statistics"]["total_components"] = 2
    data["statistics"]["component_types"] = {"resistor": 2, "capacitor": 1}
    violations = check_invariants(data, "test.json")
    assert len(violations) == 1
    assert "component_types sum (3) > total_components (2)" in violations[0][1]


# 9. Duplicate refs flagged
def test_duplicate_refs_flagged():
    data = _clean_output()
    data["components"] = [
        {"reference": "R1", "type": "resistor"},
        {"reference": "R1", "type": "resistor"},
        {"reference": "R2", "type": "resistor"},
    ]
    data["annotation_issues"] = {"duplicate_references": []}
    violations = check_invariants(data, "test.json")
    assert any("duplicate ref 'R1'" in v[1] for v in violations), \
        f"Expected duplicate ref violation, got: {violations}"


# 10. Duplicate refs ignored if in annotation_issues
def test_duplicate_refs_ignored_when_known():
    data = _clean_output()
    data["components"] = [
        {"reference": "R1", "type": "resistor"},
        {"reference": "R1", "type": "resistor"},
        {"reference": "R2", "type": "resistor"},
    ]
    data["annotation_issues"] = {"duplicate_references": ["R1"]}
    violations = check_invariants(data, "test.json")
    # R1 is in annotation_issues, so it should not be flagged
    dupe_violations = [v for v in violations if "duplicate ref" in v[1]]
    assert dupe_violations == [], \
        f"Expected no duplicate violations, got: {dupe_violations}"


# 11. Null values skipped gracefully
def test_null_values_skipped():
    data = _clean_output()
    data["signal_analysis"] = {
        "voltage_dividers": [{"ratio": None}],
        "rc_filters": [{"cutoff_hz": None}],
        "lc_filters": [{"resonant_hz": None}],
        "crystal_circuits": [{"effective_load_pF": None}],
    }
    violations = check_invariants(data, "test.json")
    assert violations == [], f"Expected no violations for null values, got: {violations}"


# 12. Corpus spot-check (run on a real output)
def test_corpus_spot_check():
    # Use a known real output that should have valid invariants
    output_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
    if not output_dir.exists():
        return  # Skip if no outputs available

    # Find the first output with signal_analysis detections
    checked = 0
    for repo_dir in sorted(output_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        for sub in sorted(repo_dir.rglob("*.json")):
            try:
                with open(sub) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            sa = data.get("signal_analysis", {})
            if sa.get("voltage_dividers") or sa.get("rc_filters"):
                violations = check_invariants(data, str(sub))
                # Real outputs should have no violations
                assert violations == [], \
                    f"Invariant violation in {sub}: {violations}"
                checked += 1
                if checked >= 5:
                    return
        if checked >= 5:
            return

    # If we got here, we checked some files (or none existed)
    assert checked > 0 or not any(output_dir.iterdir()), \
        "No outputs with signal_analysis found for spot-check"


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
