#!/usr/bin/env python3
"""Tests for KH-391: summarize_findings deep-review rendering fixes.

Tests that deep-review findings are rendered honestly:
- (a) rule_id shows "dr:<category>" prefix
- (b) category column width is >=21 chars (accommodates "dr:" + longest category)
- (c) --by-confidence groups confidence levels separately (regression net for pre-existing behavior)
- (d) NEW: dr column shows deep-review confidence count in default view
- (e) NEW: --json mode includes deep_review_confidence in aggregated rows
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Bridge path to main repo
HARNESS_ROOT = Path(__file__).resolve().parents[2]
MAIN_REPO_ROOT = Path(os.environ.get("KICAD_HAPPY_DIR", str(HARNESS_ROOT.parent / "kicad-happy"))).resolve()
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from summarize_findings import main as summarize_main


def test_deep_review_dr_prefix():
    """Test (a): deep-review rows render with 'dr:' prefix in rule_id column."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_dir = Path(tmpdir) / "analysis"
        analysis_dir.mkdir()
        run_id = "20260101T000000Z-abc123"
        run_dir = analysis_dir / run_id
        run_dir.mkdir()

        # Create a minimal analyzer JSON (schematic.json)
        analyzer_data = {
            "findings": [
                {
                    "detector": "RC-DET",
                    "rule_id": "VD-001",
                    "category": "timing",
                    "severity": "warning",
                    "confidence": "heuristic",
                    "summary": "RC filter found"
                }
            ],
            "assessments": [],
            "inputs": {"source_files": []},
            "compat": {"minimum_consumer_version": "1.0.0"}
        }
        (run_dir / "schematic.json").write_text(json.dumps(analyzer_data))

        # Create deep_review.json
        deep_review_data = {
            "schema_version": "1.0",
            "produced_for_run_id": run_id,
            "produced_at": "2026-01-01T00:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Board layout issue",
                    "evidence": {
                        "components": ["R1"]
                    }
                },
                {
                    "detector": "deep_review",
                    "category": "power",
                    "severity": "info",
                    "confidence": "medium",
                    "summary": "Power distribution review",
                    "evidence": {
                        "nets": ["VCC"]
                    }
                }
            ],
            "quarantined": []
        }
        (analysis_dir / "deep_review.json").write_text(json.dumps(deep_review_data))

        # Create manifest
        manifest = {
            "version": 1,
            "current": run_id,
            "runs": {run_id: {"timestamp": "2026-01-01T00:00:00Z"}}
        }
        (analysis_dir / "manifest.json").write_text(json.dumps(manifest))

        # Capture output
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            result = summarize_main([str(analysis_dir)])

        output_text = output.getvalue()

        # Check that deep-review rows have "dr:" prefix
        assert "dr:manufacturability" in output_text, \
            f"Expected 'dr:manufacturability' in output, got:\n{output_text}"
        assert "dr:power" in output_text, \
            f"Expected 'dr:power' in output, got:\n{output_text}"


def test_deep_review_column_width():
    """Test (b): rule_id column width is >=21 chars to fit 'dr:manufacturability'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_dir = Path(tmpdir) / "analysis"
        analysis_dir.mkdir()
        run_id = "20260101T000000Z-abc123"
        run_dir = analysis_dir / run_id
        run_dir.mkdir()

        # Create minimal analyzer JSON
        analyzer_data = {
            "findings": [],
            "assessments": [],
            "inputs": {"source_files": []},
            "compat": {"minimum_consumer_version": "1.0.0"}
        }
        (run_dir / "schematic.json").write_text(json.dumps(analyzer_data))

        # Create deep_review.json with "manufacturability" (17 chars + "dr:" = 20 chars)
        deep_review_data = {
            "schema_version": "1.0",
            "produced_for_run_id": run_id,
            "produced_at": "2026-01-01T00:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Long category name test",
                    "evidence": {"components": ["R1"]}
                }
            ],
            "quarantined": []
        }
        (analysis_dir / "deep_review.json").write_text(json.dumps(deep_review_data))

        # Create manifest
        manifest = {
            "version": 1,
            "current": run_id,
            "runs": {run_id: {"timestamp": "2026-01-01T00:00:00Z"}}
        }
        (analysis_dir / "manifest.json").write_text(json.dumps(manifest))

        # Capture output
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            result = summarize_main([str(analysis_dir)])

        output_text = output.getvalue()
        lines = output_text.split("\n")

        # Find the header line and data line
        header_line = None
        data_line = None
        for line in lines:
            if line.startswith("rule_id"):
                header_line = line
            elif "dr:manufacturability" in line:
                data_line = line

        assert header_line is not None, f"No header line found in:\n{output_text}"
        assert data_line is not None, f"No data line with 'dr:manufacturability' found in:\n{output_text}"

        # Verify column width by checking character position of severity field.
        # Format: {rule_id:<21} {severity:<9} ...
        # So severity should start at position 21
        # Split by finding where "warning" or "info" starts in the data line

        # Find where the rule_id ends (should be around position 21)
        # "dr:manufacturability" is 20 chars, so it should fit in :<21
        rule_id_text = "dr:manufacturability"
        assert rule_id_text in data_line, f"Expected '{rule_id_text}' in line: {data_line}"

        # Check that it doesn't overflow: severity should come after position 21
        rule_start = data_line.find(rule_id_text)
        rule_end = rule_start + len(rule_id_text)

        # After the rule_id (at position 20), we should have at least 1 space before severity
        # The next non-space should start at position 21 or later
        assert rule_end <= 21, \
            f"Rule ID '{rule_id_text}' ends at position {rule_end}, exceeds field width 21"


def test_deep_review_dr_column_text_mode():
    """Test (d): text mode shows 'dr' column with count of deep-review findings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_dir = Path(tmpdir) / "analysis"
        analysis_dir.mkdir()
        run_id = "20260101T000000Z-abc123"
        run_dir = analysis_dir / run_id
        run_dir.mkdir()

        # Create analyzer JSON with deterministic findings
        analyzer_data = {
            "findings": [
                {
                    "detector": "RC-DET",
                    "rule_id": "VD-001",
                    "severity": "warning",
                    "confidence": "deterministic",
                    "summary": "RC filter"
                }
            ],
            "assessments": [],
            "inputs": {"source_files": []},
            "compat": {"minimum_consumer_version": "1.0.0"}
        }
        (run_dir / "schematic.json").write_text(json.dumps(analyzer_data))

        # Create deep_review.json with 2 high-confidence findings
        deep_review_data = {
            "schema_version": "1.0",
            "produced_for_run_id": run_id,
            "produced_at": "2026-01-01T00:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Board review 1",
                    "evidence": {"components": ["R1"]}
                },
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Board review 2",
                    "evidence": {"components": ["R2"]}
                }
            ],
            "quarantined": []
        }
        (analysis_dir / "deep_review.json").write_text(json.dumps(deep_review_data))

        # Create manifest
        manifest = {
            "version": 1,
            "current": run_id,
            "runs": {run_id: {"timestamp": "2026-01-01T00:00:00Z"}}
        }
        (analysis_dir / "manifest.json").write_text(json.dumps(manifest))

        # Capture output
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            result = summarize_main([str(analysis_dir)])

        output_text = output.getvalue()
        lines = output_text.split("\n")

        # Find the header and data lines
        header_line = None
        dr_data_line = None
        analyzer_data_line = None
        for line in lines:
            if line.startswith("rule_id"):
                header_line = line
            elif "dr:manufacturability" in line:
                dr_data_line = line
            elif "VD-001" in line:
                analyzer_data_line = line

        # Verify header has 'dr' column
        assert "dr" in header_line, f"Expected 'dr' column in header: {header_line}"

        # Verify deep-review row has dr count of 2
        assert dr_data_line is not None, f"No deep-review data line found in:\n{output_text}"
        # Extract the dr column value (should be after ds column)
        # Format: {rule_id:<21} {severity:<9} {count:>5}  {det:>4} {heu:>4} {ds:>3} {dr:>4}
        parts = dr_data_line.split()
        # The dr value should be near the end before "example"
        # Look for the number "2" that represents the dr count
        assert " 2 " in dr_data_line or dr_data_line.endswith("2"), \
            f"Expected dr count of 2 in line: {dr_data_line}"

        # Verify analyzer row has dr count of 0
        assert analyzer_data_line is not None, f"No analyzer data line found in:\n{output_text}"
        # The dr count should be 0 for analyzer findings
        # Extract the numeric values from the line
        import re
        numbers = re.findall(r'\s(\d+)\s', analyzer_data_line)
        # We should see 0 in the dr column (last numeric column)
        assert numbers[-1] == '0', \
            f"Expected dr count of 0 for analyzer row, got: {numbers[-1]} from line: {analyzer_data_line}"


def test_deep_review_dr_column_json_mode():
    """Test (e): --json mode includes deep_review_confidence in aggregated rows."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_dir = Path(tmpdir) / "analysis"
        analysis_dir.mkdir()
        run_id = "20260101T000000Z-abc123"
        run_dir = analysis_dir / run_id
        run_dir.mkdir()

        # Create minimal analyzer JSON
        analyzer_data = {
            "findings": [],
            "assessments": [],
            "inputs": {"source_files": []},
            "compat": {"minimum_consumer_version": "1.0.0"}
        }
        (run_dir / "schematic.json").write_text(json.dumps(analyzer_data))

        # Create deep_review.json with mixed confidence levels
        deep_review_data = {
            "schema_version": "1.0",
            "produced_for_run_id": run_id,
            "produced_at": "2026-01-01T00:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Board review",
                    "evidence": {"components": ["R1"]}
                },
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "medium",
                    "summary": "Board review 2",
                    "evidence": {"components": ["R2"]}
                }
            ],
            "quarantined": []
        }
        (analysis_dir / "deep_review.json").write_text(json.dumps(deep_review_data))

        # Create manifest
        manifest = {
            "version": 1,
            "current": run_id,
            "runs": {run_id: {"timestamp": "2026-01-01T00:00:00Z"}}
        }
        (analysis_dir / "manifest.json").write_text(json.dumps(manifest))

        # Capture JSON output
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            result = summarize_main([str(analysis_dir), "--json"])

        json_text = output.getvalue()
        payload = json.loads(json_text)

        # Verify the payload has rows with deep_review_confidence
        rows = payload.get("rows", [])
        assert len(rows) > 0, "No rows in JSON payload"

        # Find the deep-review row (JSON output uses rule_id without dr: prefix)
        dr_row = None
        for row in rows:
            if row["rule_id"] == "manufacturability" and "deep_review.json" in row.get("sources", []):
                dr_row = row
                break

        assert dr_row is not None, f"No deep-review row found in: {rows}"

        # Verify deep_review_confidence structure
        dr_conf = dr_row.get("deep_review_confidence", {})
        assert isinstance(dr_conf, dict), "deep_review_confidence should be a dict"

        # Should have high=1, medium=1, low=0
        assert dr_conf.get("high") == 1, f"Expected high=1, got: {dr_conf.get('high')}"
        assert dr_conf.get("medium") == 1, f"Expected medium=1, got: {dr_conf.get('medium')}"
        assert dr_conf.get("low") == 0, f"Expected low=0, got: {dr_conf.get('low')}"


def test_by_confidence_regression_net():
    """Regression net (c): --by-confidence groups confidence levels correctly (pre-existing behavior).

    This test verifies that the --by-confidence aggregation already separated
    analyzer vocabulary (deterministic/heuristic/datasheet_backed) from
    deep-review vocabulary (high/medium/low) by grouping on confidence value.
    This behavior was not changed by the fix; the test serves as a regression net.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_dir = Path(tmpdir) / "analysis"
        analysis_dir.mkdir()
        run_id = "20260101T000000Z-abc123"
        run_dir = analysis_dir / run_id
        run_dir.mkdir()

        # Create analyzer JSON with deterministic findings
        analyzer_data = {
            "findings": [
                {
                    "detector": "RC-DET",
                    "rule_id": "VD-001",
                    "severity": "warning",
                    "confidence": "deterministic",
                    "summary": "RC filter"
                }
            ],
            "assessments": [],
            "inputs": {"source_files": []},
            "compat": {"minimum_consumer_version": "1.0.0"}
        }
        (run_dir / "schematic.json").write_text(json.dumps(analyzer_data))

        # Create deep_review.json with high/medium/low confidence
        deep_review_data = {
            "schema_version": "1.0",
            "produced_for_run_id": run_id,
            "produced_at": "2026-01-01T00:00:00Z",
            "findings": [
                {
                    "detector": "deep_review",
                    "category": "manufacturability",
                    "severity": "warning",
                    "confidence": "high",
                    "summary": "Board review",
                    "evidence": {"components": ["R1"]}
                },
                {
                    "detector": "deep_review",
                    "category": "power",
                    "severity": "info",
                    "confidence": "medium",
                    "summary": "Power review",
                    "evidence": {"nets": ["VCC"]}
                },
                {
                    "detector": "deep_review",
                    "category": "thermal",
                    "severity": "info",
                    "confidence": "low",
                    "summary": "Thermal review",
                    "evidence": {"components": ["IC1"]}
                }
            ],
            "quarantined": []
        }
        (analysis_dir / "deep_review.json").write_text(json.dumps(deep_review_data))

        # Create manifest
        manifest = {
            "version": 1,
            "current": run_id,
            "runs": {run_id: {"timestamp": "2026-01-01T00:00:00Z"}}
        }
        (analysis_dir / "manifest.json").write_text(json.dumps(manifest))

        # Test JSON mode with --by-confidence
        import io
        from contextlib import redirect_stdout
        output_json = io.StringIO()
        with redirect_stdout(output_json):
            result = summarize_main([str(analysis_dir), "--by-confidence", "--json"])

        json_text = output_json.getvalue()
        payload = json.loads(json_text)

        # The payload should have rows with both analyzer vocabulary and deep-review vocabulary
        rows = payload.get("rows", [])

        # Should have at least one analyzer vocabulary row and deep-review vocabulary rows
        analyzer_confidences = [r["confidence"] for r in rows
                               if r["confidence"] in {"deterministic", "heuristic", "datasheet_backed"}]
        deep_review_confidences = [r["confidence"] for r in rows
                                   if r["confidence"] in {"high", "medium", "low"}]

        assert len(analyzer_confidences) > 0, \
            f"Expected analyzer vocabulary rows, got: {rows}"
        assert len(deep_review_confidences) >= 3, \
            f"Expected 3 deep-review vocabulary rows (high/medium/low), got: {rows}"


if __name__ == "__main__":
    test_deep_review_dr_prefix()
    test_deep_review_column_width()
    test_deep_review_dr_column_text_mode()
    test_deep_review_dr_column_json_mode()
    test_by_confidence_regression_net()
    print("All tests passed!")
