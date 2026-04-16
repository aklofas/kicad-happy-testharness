"""Unit tests for regression/seed_negative.py.

scan_findings_for_negatives: reads findings.json files under DATA_DIR
and returns candidates with `incorrect` entries.

generate_negative_assertions: converts candidates → per-project assertion
dicts. Pure transformation — no filesystem access.
"""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from regression.seed_negative import (  # noqa: E402
    generate_negative_assertions,
    FP_KEYWORDS,
)


# ---------------------------------------------------------------------------
# generate_negative_assertions — pure transform
# ---------------------------------------------------------------------------

def test_generate_with_explicit_check():
    """Candidate with `check` field produces assertion using that check verbatim."""
    cands = [{
        "repo": "foo/bar",
        "project": "proj1",
        "finding_id": "F-001",
        "description": "wrong voltage divider",
        "analyzer_section": "findings",
        "check": {"path": "findings", "op": "not_contains_match",
                  "field": "rule_id", "pattern": "^VD-001$"},
        "has_check": True,
    }]
    result = generate_negative_assertions(cands)
    key = ("foo/bar", "proj1")
    assert key in result
    a = result[key][0]
    assert a["id"] == "NEG-000001"
    assert a["aspirational"] is True
    assert a["check"]["op"] == "not_contains_match"
    assert "_needs_manual_check" not in a


def test_generate_without_check_gets_manual_flag():
    """Candidate without check field produces generic assertion flagged for review."""
    cands = [{
        "repo": "foo/bar",
        "project": "proj1",
        "finding_id": "F-002",
        "description": "false positive on R1 voltage divider",
        "analyzer_section": "findings",
        "check": None,
        "has_check": False,
    }]
    result = generate_negative_assertions(cands)
    a = result[("foo/bar", "proj1")][0]
    assert a.get("_needs_manual_check") is True
    assert a["check"]["op"] == "min_count"


def test_generate_groups_by_repo_and_project():
    """Candidates across different (repo, project) pairs end up grouped."""
    cands = [
        {"repo": "a/b", "project": "p1", "finding_id": "F1",
         "description": "x", "analyzer_section": "findings",
         "check": {"op": "exists"}, "has_check": True},
        {"repo": "a/b", "project": "p1", "finding_id": "F2",
         "description": "y", "analyzer_section": "findings",
         "check": {"op": "exists"}, "has_check": True},
        {"repo": "a/b", "project": "p2", "finding_id": "F3",
         "description": "z", "analyzer_section": "findings",
         "check": {"op": "exists"}, "has_check": True},
    ]
    result = generate_negative_assertions(cands)
    assert len(result[("a/b", "p1")]) == 2
    assert len(result[("a/b", "p2")]) == 1


def test_generate_assigns_sequential_ids():
    """Candidates get NEG-NNNNNN IDs in enumeration order."""
    cands = [
        {"repo": "x/y", "project": "p", "finding_id": f"F-{i}",
         "description": "d", "analyzer_section": "findings",
         "check": {"op": "exists"}, "has_check": True}
        for i in range(3)
    ]
    result = generate_negative_assertions(cands)
    ids = [a["id"] for a in result[("x/y", "p")]]
    assert ids == ["NEG-000001", "NEG-000002", "NEG-000003"]


def test_generate_truncates_description():
    """Descriptions > 120 chars are truncated in the assertion description."""
    long_desc = "x" * 500
    cands = [{"repo": "r", "project": "p", "finding_id": "F",
              "description": long_desc, "analyzer_section": "findings",
              "check": {"op": "exists"}, "has_check": True}]
    result = generate_negative_assertions(cands)
    assert len(result[("r", "p")][0]["description"]) < 200


# ---------------------------------------------------------------------------
# FP_KEYWORDS regex
# ---------------------------------------------------------------------------

def test_fp_keywords_matches_false_positive():
    assert FP_KEYWORDS.search("this is a false positive")
    assert FP_KEYWORDS.search("FALSE POSITIVE")
    assert FP_KEYWORDS.search("false-positive")


def test_fp_keywords_matches_variants():
    assert FP_KEYWORDS.search("misclassified as a divider")
    assert FP_KEYWORDS.search("overcounted the resistors")
    assert FP_KEYWORDS.search("should not be detected")
    assert FP_KEYWORDS.search("incorrectly flagged")
    assert FP_KEYWORDS.search("erroneously identified")


def test_fp_keywords_does_not_match_unrelated():
    assert not FP_KEYWORDS.search("component R1 has 10k value")
    assert not FP_KEYWORDS.search("normal operation")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
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
