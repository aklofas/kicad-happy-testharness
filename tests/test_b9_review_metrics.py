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
        # With one ok packet, suppression_precision aggregate == per-packet
        ok = [p for p in per_packet if p["status"] == "ok"]
        if len(ok) == 1:
            assert (agg["metrics"]["suppression_precision"]
                    == ok[0]["metrics"]["suppression_precision"])
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
