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


if __name__ == "__main__":
    import traceback

    tests = [
        test_packet_schema_validates_demo,
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
