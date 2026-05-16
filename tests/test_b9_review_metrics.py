"""B9 Layer 2 review metrics — runner + packet schema tests.

v1.4 scaffolding: replay-only runner, all 7 metrics computed,
synthetic demo packet locks on-disk schema. Spec at
docs/superpowers/specs/2026-05-16-b9-layer2-review-metrics-design.md.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
PACKETS_DIR = HARNESS_DIR / "regression" / "reference_review_packets"
DEMO_PACKET = PACKETS_DIR / "packet_01_suppress_true_fp"
SCHEMA_PATH = PACKETS_DIR / "packet_schema.json"
RUNNER = HARNESS_DIR / "run" / "run_review_metrics.py"


def _load(path: Path):
    return json.loads(path.read_text())


def _build_packet_dict(pkt_dir: Path) -> dict:
    return {
        "inputs": {
            "findings": _load(pkt_dir / "findings.json"),
            "design_context": _load(pkt_dir / "design_context.json"),
            "extraction_facts": _load(pkt_dir / "extraction_facts.json"),
        },
        "recorded_output": _load(pkt_dir / "review_annotations.json"),
        "expected": _load(pkt_dir / "expected_annotations.json"),
    }


def _jsonschema():
    try:
        import jsonschema
        return jsonschema
    except ImportError:
        return None


def test_packet_schema_validates_demo():
    """Demo packet (packet_01_suppress_true_fp) is schema-conformant.
    Skips cleanly when jsonschema library is absent."""
    js = _jsonschema()
    if js is None:
        print("SKIP: jsonschema unavailable")
        return
    schema = _load(SCHEMA_PATH)
    packet = _build_packet_dict(DEMO_PACKET)
    js.validate(instance=packet, schema=schema)


def test_runner_smoke():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        # Output dir is <out_dir>/<timestamp>/
        runs = list(out_dir.iterdir())
        assert len(runs) == 1, f"expected 1 timestamped run dir, got {runs}"
        run_dir = runs[0]
        assert (run_dir / "per_packet.json").exists()
        assert (run_dir / "aggregate.json").exists()
        assert (run_dir / "report.md").exists()


def test_missing_review_annotations_skips_clean():
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        packets_dir = tmp / "packets"
        packets_dir.mkdir()
        dest = packets_dir / DEMO_PACKET.name
        shutil.copytree(DEMO_PACKET, dest)
        (dest / "review_annotations.json").unlink()
        out_dir = tmp / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(packets_dir),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        assert len(per_packet) == 1
        assert per_packet[0]["status"] == "skipped"
        assert "review_annotations" in per_packet[0].get("reason", "")


def test_demo_packet_suppression_precision():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        entry = next(p for p in per_packet
                     if p["packet_name"] == "packet_01_suppress_true_fp")
        assert entry["status"] == "ok"
        assert entry["metrics"]["suppression_precision"] == 1.0
        assert entry["metrics"]["false_suppression_miss_rate"] is None
        assert entry["metrics"]["confirmation_recall"] is None
        assert entry["counts"]["suppressed"] == 1
        assert entry["counts"]["expected_suppressions"] == 1


def test_per_packet_json_shape():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        entry = per_packet[0]
        assert entry["status"] == "ok"
        m = entry["metrics"]
        for key in ("suppression_precision", "false_suppression_miss_rate",
                    "confirmation_recall", "escalation_precision",
                    "correlation_coverage", "confidence_calibration",
                    "cost_delta"):
            assert key in m, f"missing metric key: {key}"
        # Calibration: per-bucket structure, all "insufficient_data" at n=1
        cal = m["confidence_calibration"]
        for bucket in ("high", "medium", "low"):
            assert bucket in cal
            assert cal[bucket] in ("insufficient_data",) or isinstance(cal[bucket], float)
        # Cost null at v1.4 (no ledger)
        assert m["cost_delta"] is None
        # Overlay violations surfaced
        assert "escalation_overlay_violations" in entry
        assert entry["escalation_overlay_violations"] == 0


def test_aggregate_json_shape():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        run_dir = next(out_dir.iterdir())
        agg = json.loads((run_dir / "aggregate.json").read_text())
        assert agg["packet_count"] == agg["packets_run"] + agg["packets_skipped"]
        m = agg["metrics"]
        for key in ("suppression_precision", "false_suppression_miss_rate",
                    "confirmation_recall", "escalation_precision",
                    "correlation_coverage", "confidence_calibration",
                    "cost_delta"):
            assert key in m
        assert "escalation_overlay_violations_total" in agg


def test_aggregate_consistency():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True, check=True
        )
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        agg = json.loads((run_dir / "aggregate.json").read_text())
        # Aggregate suppression_precision = weighted mean across ok packets,
        # weighted by per-packet suppressed counts.
        ok = [p for p in per_packet if p["status"] == "ok"]
        assert len(ok) >= 1
        num = sum(p["metrics"]["suppression_precision"] * p["counts"]["suppressed"]
                  for p in ok
                  if p["metrics"]["suppression_precision"] is not None
                  and p["counts"]["suppressed"] > 0)
        denom = sum(p["counts"]["suppressed"] for p in ok
                    if p["metrics"]["suppression_precision"] is not None)
        expected = num / denom if denom > 0 else None
        assert agg["metrics"]["suppression_precision"] == expected
        # Overlay violations total = sum of per-packet
        assert (agg["escalation_overlay_violations_total"]
                == sum(p.get("escalation_overlay_violations", 0)
                       for p in per_packet))


def test_report_md_nonempty():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True, check=True
        )
        run_dir = next(out_dir.iterdir())
        md = (run_dir / "report.md").read_text()
        assert "B9 Review Metrics" in md
        assert "packet_01_suppress_true_fp" in md
        assert "Aggregate" in md
        assert "Carry-overs" in md


def test_single_packet_filter():
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        packets_dir = tmp / "packets"
        packets_dir.mkdir()
        # Copy demo packet twice with different names
        shutil.copytree(DEMO_PACKET, packets_dir / "packet_01_suppress_true_fp")
        shutil.copytree(DEMO_PACKET, packets_dir / "packet_02_decoy")
        out_dir = tmp / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(packets_dir),
             "--packet", "packet_01_suppress_true_fp",
             "--output-dir", str(out_dir)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        assert len(per_packet) == 1
        assert per_packet[0]["packet_name"] == "packet_01_suppress_true_fp"


def test_json_flag_stdout_only():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(PACKETS_DIR),
             "--output-dir", str(out_dir),
             "--json"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        agg = json.loads(result.stdout)
        assert agg["packet_count"] >= 1
        assert "metrics" in agg
        assert not out_dir.exists(), "expected no output dir with --json"


def test_malformed_packet_skips_clean_via_schema():
    """A packet with expected_annotations missing required keys skips clean.

    Replaces expected_annotations.json with empty {} (missing expected_suppressions
    and other required fields). With jsonschema present, load_packet should return
    status=skipped with reason containing 'schema'. Soft-skips if jsonschema absent.
    """
    import shutil

    js = _jsonschema()
    if js is None:
        print("SKIP: jsonschema unavailable")
        return

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        packets_dir = tmp / "packets"
        packets_dir.mkdir()
        dest = packets_dir / DEMO_PACKET.name
        shutil.copytree(DEMO_PACKET, dest)
        # Replace expected_annotations with a dict missing required keys
        (dest / "expected_annotations.json").write_text(json.dumps({}))

        out_dir = tmp / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(packets_dir),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        assert len(per_packet) == 1
        assert per_packet[0]["status"] == "skipped", per_packet[0]
        assert "schema" in per_packet[0].get("reason", ""), per_packet[0]


def test_aggregate_calibration_pooled():
    """Aggregate calibration pools per-bucket counts, not average of per-packet floats.

    Packet A: 10 high-confidence suppressions, 4 correct → per-packet precision 0.4.
    Packet B:  6 high-confidence suppressions, 6 correct → per-packet precision 1.0.
    Pooled = 10/16 = 0.625; arithmetic mean = (0.4 + 1.0)/2 = 0.7.
    Test asserts pooled value, not mean.
    """
    import shutil

    def _make_annotations(finding_ids_high, correct_ids):
        """All findings suppressed at high confidence; correct_ids are in expected."""
        return {
            "schema_version": "1.0",
            "produced_for_run_id": "test-run",
            "produced_at": "2026-05-16T00:00:00Z",
            "annotations": [
                {
                    "finding_id": fid,
                    "status": "suppressed",
                    "reason": "test suppression",
                    "confidence": "high",
                    "reviewed_at": "2026-05-16T00:00:00Z",
                }
                for fid in finding_ids_high
            ],
            "reviewer_observations": [],
        }

    def _make_expected(correct_ids):
        return {
            "expected_suppressions": [{"finding_id": fid} for fid in correct_ids],
            "expected_confirmations": [],
            "expected_escalations": [],
            "expected_correlations": [],
            "expected_novel_observations_count": 0,
        }

    def _make_findings(finding_ids):
        return {
            "schema_version": "1.4.0",
            "analyzer_type": "schematic",
            "findings": [
                {
                    "finding_id": fid,
                    "detector": "detect_test",
                    "rule_id": "TST-001",
                    "severity": "warning",
                    "summary": f"test finding {fid}",
                }
                for fid in finding_ids
            ],
        }

    minimal_context = {"design_category": "test", "confidence": "low"}
    minimal_facts = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        packets_dir = tmp / "packets"
        packets_dir.mkdir()

        # Packet A: 10 high suppressions, 4 correct (f_a0..f_a3 correct, f_a4..f_a9 wrong)
        a_ids = [f"sch:TST-001:A{i}" for i in range(10)]
        a_correct = a_ids[:4]
        pkt_a = packets_dir / "packet_01_a"
        pkt_a.mkdir()
        (pkt_a / "review_annotations.json").write_text(
            json.dumps(_make_annotations(a_ids, a_correct)))
        (pkt_a / "expected_annotations.json").write_text(
            json.dumps(_make_expected(a_correct)))
        (pkt_a / "findings.json").write_text(json.dumps(_make_findings(a_ids)))
        (pkt_a / "design_context.json").write_text(json.dumps(minimal_context))
        (pkt_a / "extraction_facts.json").write_text(json.dumps(minimal_facts))

        # Packet B: 6 high suppressions, 6 correct (all correct)
        b_ids = [f"sch:TST-001:B{i}" for i in range(6)]
        b_correct = b_ids[:]
        pkt_b = packets_dir / "packet_02_b"
        pkt_b.mkdir()
        (pkt_b / "review_annotations.json").write_text(
            json.dumps(_make_annotations(b_ids, b_correct)))
        (pkt_b / "expected_annotations.json").write_text(
            json.dumps(_make_expected(b_correct)))
        (pkt_b / "findings.json").write_text(json.dumps(_make_findings(b_ids)))
        (pkt_b / "design_context.json").write_text(json.dumps(minimal_context))
        (pkt_b / "extraction_facts.json").write_text(json.dumps(minimal_facts))

        out_dir = tmp / "metrics"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             "--packets-dir", str(packets_dir),
             "--output-dir", str(out_dir)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"runner failed: {result.stderr}"
        run_dir = next(out_dir.iterdir())
        per_packet = json.loads((run_dir / "per_packet.json").read_text())
        agg = json.loads((run_dir / "aggregate.json").read_text())

        # Both packets should be ok and carry n>=CALIBRATION_MIN_N (10, 6)
        assert all(p["status"] == "ok" for p in per_packet), per_packet

        # Per-packet precision values (order may vary by name sort)
        a_entry = next(p for p in per_packet if p["packet_name"] == "packet_01_a")
        b_entry = next(p for p in per_packet if p["packet_name"] == "packet_02_b")
        assert a_entry["metrics"]["confidence_calibration"]["high"] == 4 / 10
        assert b_entry["metrics"]["confidence_calibration"]["high"] == 6 / 6

        # Pooled = (4+6)/(10+6) = 10/16 = 0.625
        # Arithmetic mean = (0.4 + 1.0)/2 = 0.7  (the wrong formula)
        pooled = 10 / 16
        agg_high = agg["metrics"]["confidence_calibration"]["high"]
        assert agg_high == pooled, (
            f"Expected pooled calibration {pooled}, got {agg_high}; "
            f"arithmetic mean would be 0.7"
        )


if __name__ == "__main__":
    import traceback

    tests = [
        test_packet_schema_validates_demo,
        test_runner_smoke,
        test_missing_review_annotations_skips_clean,
        test_demo_packet_suppression_precision,
        test_per_packet_json_shape,
        test_aggregate_json_shape,
        test_aggregate_consistency,
        test_report_md_nonempty,
        test_single_packet_filter,
        test_json_flag_stdout_only,
        test_malformed_packet_skips_clean_via_schema,
        test_aggregate_calibration_pooled,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception:
            failed += 1
            print(f"FAIL: {t.__name__}")
            traceback.print_exc()
    total = passed + failed
    print(f"\n{passed} passed, {failed} failed ({total} total)")
    sys.exit(0 if failed == 0 else 1)
