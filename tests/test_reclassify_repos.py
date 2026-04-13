"""Unit tests for tools/reclassify_repos.py — _score_repo and classify_repo."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from reclassify_repos import _score_repo, classify_repo, CLASSIFICATION_RULES


def _rule(category):
    """Return the classification rule for a named category."""
    for r in CLASSIFICATION_RULES:
        if r["category"] == category:
            return r
    raise KeyError(f"No rule for category {category!r}")


# --- Name pattern scoring ---

def test_score_name_esp32():
    repo_entry = {"repo": "user/esp32-badge", "detectors_fired": {}, "tags": []}
    score, reasons = _score_repo(repo_entry, None, _rule("ESP32"))
    assert score >= 2, f"Expected score>=2, got {score}"
    assert any("name:" in r for r in reasons)


def test_score_name_keyboard():
    repo_entry = {"repo": "user/my-keyboard", "detectors_fired": {}, "tags": []}
    score, reasons = _score_repo(repo_entry, None, _rule("Keyboards"))
    assert score >= 2


def test_score_strong_detector_keyboard():
    repo_entry = {
        "repo": "user/typing-gadget",
        "detectors_fired": {"key_matrices": 5},
        "tags": [],
    }
    score, reasons = _score_repo(repo_entry, None, _rule("Keyboards"))
    assert score >= 3, f"Strong detector should give >=3, got {score}"
    assert any("det:key_matrices" in r for r in reasons)


# --- Topic scoring ---

def test_score_topic_arduino():
    validated = {"description": "", "topics": ["arduino"]}
    repo_entry = {"repo": "user/some-shield", "detectors_fired": {}, "tags": []}
    score, reasons = _score_repo(repo_entry, validated, _rule("Arduino recreations"))
    assert score >= 3
    assert any("topic:arduino" in r for r in reasons)


# --- Zero score for unrelated rule ---

def test_score_zero_for_unrelated():
    repo_entry = {"repo": "user/myproject", "detectors_fired": {}, "tags": []}
    score, reasons = _score_repo(repo_entry, None, _rule("CubeSat / aerospace"))
    assert score == 0


# --- classify_repo picks best category ---

def test_classify_esp32_wins():
    repo_entry = {"repo": "user/esp32-sensor", "detectors_fired": {}, "tags": []}
    validated = {"description": "esp32 iot sensor board", "topics": ["esp32"]}
    result = classify_repo(repo_entry, validated, min_score=2)
    assert result is not None
    cat, score, reasons = result
    assert cat == "ESP32"


def test_classify_keyboard_detector():
    repo_entry = {
        "repo": "user/kbd",
        "detectors_fired": {"key_matrices": 3},
        "tags": ["keyboard"],
    }
    result = classify_repo(repo_entry, None, min_score=2)
    assert result is not None
    cat, score, reasons = result
    assert cat == "Keyboards"


def test_classify_returns_none_below_min_score():
    repo_entry = {"repo": "user/board", "detectors_fired": {}, "tags": []}
    result = classify_repo(repo_entry, None, min_score=10)
    assert result is None


def test_classify_description_motor():
    repo_entry = {"repo": "user/project", "detectors_fired": {}, "tags": []}
    validated = {"description": "brushless motor controller board", "topics": []}
    result = classify_repo(repo_entry, validated, min_score=2)
    assert result is not None
    cat, score, reasons = result
    assert cat == "Motor controllers / robotics"


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
