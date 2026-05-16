#!/usr/bin/env python3
"""Layer 2 review metrics runner. v1.4 B9 scaffolding — measurement only.

Reads reference review packets, replays recorded reviewer output, computes
7 metrics per spec docs/superpowers/specs/2026-05-16-b9-layer2-review-metrics-design.md,
emits per_packet/aggregate JSON + markdown report. No live LLM dispatch at v1.4.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PACKETS_DIR = HARNESS_DIR / "regression" / "reference_review_packets"
DEFAULT_OUTPUT_ROOT = HARNESS_DIR / "results" / "review_metrics"

PACKET_FILES = {
    "findings": "findings.json",
    "design_context": "design_context.json",
    "extraction_facts": "extraction_facts.json",
    "review_annotations": "review_annotations.json",
    "expected_annotations": "expected_annotations.json",
}


def discover_packets(packets_dir, only=None):
    if not packets_dir.is_dir():
        raise FileNotFoundError(f"packets-dir not found: {packets_dir}")
    packets = sorted(p for p in packets_dir.iterdir()
                     if p.is_dir() and p.name.startswith("packet_"))
    if only is not None:
        packets = [p for p in packets if p.name == only]
        if not packets:
            raise ValueError(f"--packet {only!r} not found in {packets_dir}")
    return packets


def load_packet(pkt_dir):
    out = {}
    for key, filename in PACKET_FILES.items():
        path = pkt_dir / filename
        if not path.exists():
            return None, f"missing {filename}"
        try:
            out[key] = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            return None, f"invalid JSON in {filename}: {exc}"
    return out, None


def process_packet(pkt_dir):
    loaded, skip_reason = load_packet(pkt_dir)
    if loaded is None:
        return {"packet_name": pkt_dir.name, "status": "skipped",
                "reason": skip_reason}
    return {"packet_name": pkt_dir.name, "status": "ok", "metrics": {},
            "_loaded": loaded}


def aggregate(per_packet):
    return {
        "packet_count": len(per_packet),
        "packets_run": sum(1 for p in per_packet if p["status"] == "ok"),
        "packets_skipped": sum(1 for p in per_packet if p["status"] == "skipped"),
        "metrics": {},
        "escalation_overlay_violations_total": 0,
    }


def render_report(per_packet, agg):
    lines = ["# B9 Review Metrics Report", "",
             f"Packets: {agg['packet_count']} total, "
             f"{agg['packets_run']} run, {agg['packets_skipped']} skipped",
             "", "## Per-packet", ""]
    for p in per_packet:
        lines.append(f"- **{p['packet_name']}** — {p['status']}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute Layer 2 review metrics from reference packets")
    parser.add_argument("--packets-dir", type=Path, default=DEFAULT_PACKETS_DIR)
    parser.add_argument("--packet", default=None,
                        help="Run a single packet by directory name")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT,
                        help="Parent of <timestamp>/ output dirs")
    parser.add_argument("--json", action="store_true",
                        help="Emit aggregate JSON to stdout, suppress file writes")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    packets = discover_packets(args.packets_dir, only=args.packet)
    per_packet = [process_packet(p) for p in packets]
    agg = aggregate(per_packet)

    if args.json:
        print(json.dumps(agg, indent=2, sort_keys=True))
        return 0

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.output_dir / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "per_packet.json").write_text(json.dumps(per_packet, indent=2, sort_keys=True))
    (run_dir / "aggregate.json").write_text(json.dumps(agg, indent=2, sort_keys=True))
    (run_dir / "report.md").write_text(render_report(per_packet, agg))

    if not args.quiet:
        print(f"wrote {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
