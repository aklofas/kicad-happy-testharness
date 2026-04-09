"""Unit tests for validate/validate_design_intent.py — design_intent field validation."""

TIER = "unit"

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "validate"))
from validate_design_intent import validate_design_intent
from utils import OUTPUTS_DIR


def _valid_design_intent():
    """Build a minimal valid output with design_intent."""
    return {
        "design_intent": {
            "product_class": "prototype",
            "ipc_class": 2,
            "target_market": "hobby",
            "expected_lifetime_years": 5,
            "operating_temp_range": [-10, 70],
            "preferred_passive_size": "0603",
            "test_coverage_target": 0.85,
            "approved_manufacturers": [],
            "confidence": 0.3,
            "detection_signals": [],
            "source": {
                "ipc_class": "auto",
                "product_class": "auto",
            },
        }
    }


# 1. Valid design_intent -> no issues
def test_valid_design_intent():
    data = _valid_design_intent()
    issues = validate_design_intent(data, "test.json")
    assert issues == [], f"Expected no issues, got: {issues}"


# 2. Missing design_intent -> issue
def test_missing_design_intent():
    issues = validate_design_intent({}, "test.json")
    assert len(issues) == 1
    assert "missing design_intent" in issues[0][1]


# 3. Invalid product_class -> issue
def test_invalid_product_class():
    data = _valid_design_intent()
    data["design_intent"]["product_class"] = "beta"
    issues = validate_design_intent(data, "test.json")
    assert any("product_class" in desc for _, desc in issues)


# 4. Invalid ipc_class -> issue
def test_invalid_ipc_class():
    data = _valid_design_intent()
    data["design_intent"]["ipc_class"] = 5
    issues = validate_design_intent(data, "test.json")
    assert any("ipc_class" in desc for _, desc in issues)


# 5. Confidence out of range -> issue
def test_confidence_out_of_range():
    data = _valid_design_intent()
    data["design_intent"]["confidence"] = 1.5
    issues = validate_design_intent(data, "test.json")
    assert any("confidence" in desc for _, desc in issues)


# 6. Invalid target_market -> issue
def test_invalid_target_market():
    data = _valid_design_intent()
    data["design_intent"]["target_market"] = "military"
    issues = validate_design_intent(data, "test.json")
    assert any("target_market" in desc for _, desc in issues)


# 7. Wrong type for detection_signals -> issue
def test_wrong_type_detection_signals():
    data = _valid_design_intent()
    data["design_intent"]["detection_signals"] = "not a list"
    issues = validate_design_intent(data, "test.json")
    assert any("detection_signals" in desc for _, desc in issues)


# 8. Nullable fields with None -> no issues
def test_nullable_fields_none():
    data = _valid_design_intent()
    data["design_intent"]["expected_lifetime_years"] = None
    data["design_intent"]["operating_temp_range"] = None
    data["design_intent"]["preferred_passive_size"] = None
    data["design_intent"]["test_coverage_target"] = None
    data["design_intent"]["approved_manufacturers"] = None
    issues = validate_design_intent(data, "test.json")
    assert issues == [], f"Expected no issues for None nullable fields, got: {issues}"


# 9. Corpus spot-check (load one real output, validate it)
def test_corpus_spot_check():
    """Load one real schematic output and validate its design_intent."""
    sch_dir = OUTPUTS_DIR / "schematic"
    if not sch_dir.exists():
        return  # skip if no outputs available

    # Find first non-empty JSON file
    found = None
    for owner_dir in sorted(sch_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            for json_file in sorted(repo_dir.glob("*.json")):
                if json_file.name.startswith("_"):
                    continue
                if json_file.stat().st_size > 100:
                    found = json_file
                    break
            if found:
                break
        if found:
            break

    if not found:
        return  # skip if no outputs

    data = json.loads(found.read_text())
    issues = validate_design_intent(data, str(found.name))
    assert issues == [], f"Real output {found.name} has design_intent issues: {issues}"


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
