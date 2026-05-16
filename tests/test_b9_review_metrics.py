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


if __name__ == "__main__":
    import traceback

    tests = [
        test_packet_schema_validates_demo,
        test_runner_smoke,
        test_missing_review_annotations_skips_clean,
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
