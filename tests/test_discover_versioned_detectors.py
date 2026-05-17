"""Unit tests for tools/discover_versioned_detectors.py (A8 discovery).

Runs under bare python3 in pre-push hook. Tests synthetic analyzer files
in tmp_path — no dependency on real kicad-happy repo.
"""
from __future__ import annotations

TIER = "unit"

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO = Path(__file__).resolve().parent.parent

SYNTHETIC_ANALYZER = '''
"""Synthetic test analyzer for A8 discovery."""

def make_finding(detector, rule_id, schema_era, **kw):
    return {"detector": detector, "rule_id": rule_id, "schema_era": schema_era, **kw}


def validate_pullups(ctx):
    findings = []
    findings.append(make_finding(
        detector="validate_pullups", rule_id="PU-001", schema_era="v1.4"))
    findings.append(make_finding(
        detector="validate_pullups", rule_id="VM-001", schema_era="v1.4"))
    return findings


def validate_led_resistors(ctx):
    return [make_finding(
        detector="validate_led_resistors", rule_id="LR-001", schema_era="v1.4")]


def detect_old_thing(ctx):
    # Pre-v1.4 era — should NOT be picked up by --era v1.4 discovery
    return [make_finding(
        detector="detect_old_thing", rule_id="OLD-001", schema_era="v1.3")]


def _make_helper_finding(ref):
    # Private helper — discovery must capture the detector literal here even
    # though the enclosing function does not match the detect_/validate_ prefix.
    return make_finding(
        detector="detect_helper_emitted", rule_id="HX-001", schema_era="v1.4")


def detect_helper_emitted(ctx):
    return [_make_helper_finding("R1")]
'''


def _setup_fake_kicad_happy(tmp: Path) -> Path:
    scripts = tmp / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "validation_detectors.py").write_text(SYNTHETIC_ANALYZER)
    return tmp


def _run_tool(*args, env_extra=None):
    env = {**dict(__import__("os").environ), **(env_extra or {})}
    return subprocess.run(
        [sys.executable, str(REPO / "tools/discover_versioned_detectors.py"), *args],
        capture_output=True, text=True, env=env,
    )


def test_discover_finds_v14_rules_groups_by_detector():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_fake_kicad_happy(tmp)
        out_dir = tmp / "out"
        out_dir.mkdir()
        notes = tmp / "notes.json"
        notes.write_text(json.dumps({
            "validate_pullups": "test gating summary",
            "validate_led_resistors": "led summary",
            "detect_helper_emitted": "helper-emitted summary",
        }))
        result = _run_tool(
            "--era", "v1.4",
            "--gating-notes", str(notes),
            "--output", str(out_dir / "v14_changed_detectors.json"),
            env_extra={"KICAD_HAPPY_DIR": str(tmp)},
        )
        assert result.returncode == 0, result.stderr
        data = json.loads((out_dir / "v14_changed_detectors.json").read_text())
        assert data["era"] == "v1.4"
        assert "validate_pullups" in data["detectors"]
        assert "validate_led_resistors" in data["detectors"]
        # Pre-v1.4 era detector excluded
        assert "detect_old_thing" not in data["detectors"]
        # Multi-rule grouping (PU-001 + VM-001 share detector="validate_pullups")
        assert sorted(data["detectors"]["validate_pullups"]["rules"]) == ["PU-001", "VM-001"]
        # Primary rule = lowest sorted
        assert data["detectors"]["validate_pullups"]["primary_rule"] == "PU-001"


def test_discover_captures_emit_from_private_helper():
    """When detector=<str> is hardcoded inside a private helper (e.g.
    `_make_ex_001`), discovery must still bind the rule to the literal
    detector value, not the helper function name."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_fake_kicad_happy(tmp)
        out_dir = tmp / "out"
        out_dir.mkdir()
        result = _run_tool(
            "--era", "v1.4",
            "--output", str(out_dir / "v14_changed_detectors.json"),
            env_extra={"KICAD_HAPPY_DIR": str(tmp)},
        )
        assert result.returncode == 0, result.stderr
        data = json.loads((out_dir / "v14_changed_detectors.json").read_text())
        # detect_helper_emitted is the literal in _make_helper_finding's call;
        # discovery must key on that, not on the helper function name.
        assert "detect_helper_emitted" in data["detectors"]
        assert data["detectors"]["detect_helper_emitted"]["rules"] == ["HX-001"]
        # The helper function name itself MUST NOT appear as a detector key.
        assert "_make_helper_finding" not in data["detectors"]


def test_discover_merges_gating_notes():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_fake_kicad_happy(tmp)
        out_dir = tmp / "out"
        out_dir.mkdir()
        notes = tmp / "notes.json"
        notes.write_text(json.dumps({
            "validate_pullups": "test gating summary",
            "validate_led_resistors": "led summary",
        }))
        result = _run_tool(
            "--era", "v1.4",
            "--gating-notes", str(notes),
            "--output", str(out_dir / "v14_changed_detectors.json"),
            env_extra={"KICAD_HAPPY_DIR": str(tmp)},
        )
        assert result.returncode == 0
        data = json.loads((out_dir / "v14_changed_detectors.json").read_text())
        assert data["detectors"]["validate_pullups"]["gating_summary"] == "test gating summary"
        assert data["detectors"]["validate_led_resistors"]["gating_summary"] == "led summary"


def test_discover_typo_in_gating_notes_fails():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_fake_kicad_happy(tmp)
        notes = tmp / "notes.json"
        # Reference a non-existent detector literal — should fail
        notes.write_text(json.dumps({
            "validate_pullups": "ok",
            "validate_nonexistent_typo": "this detector does not exist",
        }))
        result = _run_tool(
            "--era", "v1.4",
            "--gating-notes", str(notes),
            "--output", str(tmp / "out.json"),
            env_extra={"KICAD_HAPPY_DIR": str(tmp)},
        )
        assert result.returncode != 0
        assert "validate_nonexistent_typo" in result.stderr


def test_discover_missing_kicad_happy_dir_fails():
    result = _run_tool(
        "--era", "v1.4",
        "--output", "/tmp/never-written.json",
        env_extra={"KICAD_HAPPY_DIR": "/nonexistent/path/abc"},
    )
    assert result.returncode != 0
    assert "/nonexistent/path/abc" in result.stderr or "not found" in result.stderr.lower()


def test_discover_default_gating_summary_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _setup_fake_kicad_happy(tmp)
        out_dir = tmp / "out"
        out_dir.mkdir()
        # No --gating-notes flag
        result = _run_tool(
            "--era", "v1.4",
            "--output", str(out_dir / "v14_changed_detectors.json"),
            env_extra={"KICAD_HAPPY_DIR": str(tmp)},
        )
        assert result.returncode == 0
        data = json.loads((out_dir / "v14_changed_detectors.json").read_text())
        # Fallback template per design §4.3 step 6
        summary = data["detectors"]["validate_pullups"]["gating_summary"]
        assert "validate_pullups" in summary
        assert "v1.4" in summary


def main() -> int:
    tests = [v for k, v in globals().items()
             if k.startswith("test_") and callable(v)]
    failed = []
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            print(f"FAIL {t.__name__}: {type(e).__name__}: {e}")
            failed.append(t.__name__)
    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
