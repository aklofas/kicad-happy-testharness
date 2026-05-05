"""Test for strip_llm_overlays helper (Phase 4 spec §3.4 / HI-3)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from finding_schema import strip_llm_overlays


def _flatten_examples(data):
    """Walk summarize_findings JSON output and collect all 'examples' strings.

    The JSON shape may have rows[].examples[] or similar; this helper is
    robust to either by walking all dicts and collecting any 'examples' value.
    """
    found = []
    def _walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "examples" and isinstance(v, list):
                    found.extend(str(x) for x in v)
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)
    _walk(data)
    return found


def test_strip_removes_top_level_llm_field():
    data = {"a": 1, "llm_review": {"status": "confirmed"}}
    assert strip_llm_overlays(data) == {"a": 1}


def test_strip_removes_nested_llm_field():
    data = {"findings": [{"rule_id": "R1", "llm_review": {"status": "suppressed"}}]}
    expected = {"findings": [{"rule_id": "R1"}]}
    assert strip_llm_overlays(data) == expected


def test_strip_preserves_non_llm_fields():
    data = {"a": "x", "b": [1, 2, 3], "c": {"d": "y"}}
    assert strip_llm_overlays(data) == data


def test_strip_round_trip_byte_identical_when_no_llm():
    """HI-3 invariant smoke test."""
    raw = {"findings": [{"rule_id": "R1", "severity": "warning"}],
           "trust_summary": {"by_severity": {"warning": 1}}}
    stripped = strip_llm_overlays(raw)
    assert stripped == raw


def test_summarize_findings_only_deterministic_flag(tmp_path):
    """summarize_findings honors --only-deterministic by reading raw, not merged."""
    import subprocess
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"
    merged_dir.mkdir()

    raw = {
        "schema_version": "1.4.0",
        "findings": [{"rule_id": "TEST-1", "severity": "warning",
                       "summary": "raw finding", "category": "test",
                       "detector": "test", "confidence": "heuristic",
                       "evidence_source": "topology", "finding_id": "sch:TEST-1:u1"}],
        "trust_summary": {"by_severity": {"warning": 1, "info": 0, "error": 0}},
        "inputs": {"source_files": [], "source_hashes": {}, "run_id": "x", "config_hash": None, "upstream_artifacts": {}},
        "compat": {"minimum_consumer_version": "1.4.0", "deprecated_fields": [], "experimental_fields": []},
        "assessments": [],
    }
    merged = dict(raw)
    merged["findings"] = [
        dict(raw["findings"][0],
             summary="merged finding",
             llm_review={"status": "suppressed", "reason": "x" * 25,
                          "confidence": "high", "reviewed_at": "2026-04-27T00:00:00Z"})
    ]

    # Write manifest so summarize_findings can resolve the run dir
    run_id = "2026-04-27_0000"
    run_dir = raw_dir / run_id
    run_dir.mkdir()
    manifest = {
        "version": 1,
        "current": run_id,
        "runs": {run_id: {"outputs": {"schematic": "schematic.json"}}},
    }
    (raw_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "schematic.json").write_text(json.dumps(raw))
    merged_run_dir = merged_dir / run_id
    merged_run_dir.mkdir()
    (merged_run_dir / "schematic.json").write_text(json.dumps(merged))

    # Default: merged/ exists, so this reads analysis/merged/<run>/<analyzer>.json
    result = subprocess.run(
        ["python3", "skills/kicad/scripts/summarize_findings.py",
         str(raw_dir), "--json"],
        capture_output=True, text=True, check=True,
        cwd=MAIN_REPO_ROOT,
    )
    # With --only-deterministic: merged/ is bypassed; reads raw analysis/<run>/<analyzer>.json
    result_det = subprocess.run(
        ["python3", "skills/kicad/scripts/summarize_findings.py",
         str(raw_dir), "--json", "--only-deterministic"],
        capture_output=True, text=True, check=True,
        cwd=MAIN_REPO_ROOT,
    )
    # Both modes return rc=0; assert behavioral distinction.
    assert result.returncode == 0
    assert result_det.returncode == 0
    data_default = json.loads(result.stdout)
    data_det = json.loads(result_det.stdout)
    # Default mode read the merged finding (summary="merged finding").
    # Deterministic mode read the raw finding (summary="raw finding").
    # The summary is surfaced via the "examples" field in summarize_findings JSON output.
    default_examples = _flatten_examples(data_default)
    det_examples = _flatten_examples(data_det)
    assert "merged finding" in default_examples, (
        f"Default mode should read merged JSON; got examples: {default_examples}")
    assert "raw finding" in det_examples, (
        f"--only-deterministic should read raw JSON; got examples: {det_examples}")
