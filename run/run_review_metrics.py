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

CONFIDENCE_BUCKETS = ("high", "medium", "low")
CALIBRATION_MIN_N = 5


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


def _ids_by_status(annotations, status):
    return {a["finding_id"] for a in annotations if a.get("status") == status}


def _ids_with_severity_overlay(annotations):
    return {a["finding_id"] for a in annotations
            if a.get("suggested_severity") is not None}


def _expected_ids(expected, key):
    return {e["finding_id"] for e in expected.get(key, [])}


def _ids_with_correlation(annotations):
    return {a["finding_id"] for a in annotations
            if a.get("correlation") is not None}


def _compute_calibration(annotations, exp_supp_ids):
    out = {}
    for bucket in CONFIDENCE_BUCKETS:
        bucket_ids = {a["finding_id"] for a in annotations
                      if a.get("status") == "suppressed"
                      and a.get("confidence") == bucket}
        if len(bucket_ids) < CALIBRATION_MIN_N:
            out[bucket] = "insufficient_data"
        else:
            out[bucket] = len(bucket_ids & exp_supp_ids) / len(bucket_ids)
    return out


def _compute_overlay_violations(loaded):
    """Escalated annotations must not mutate the raw severity field.

    Returns count of (finding_id with suggested_severity) whose raw severity
    in findings.json differs from the recorded severity at review time.
    At v1.4 the reviewer schema has additionalProperties=false and provides
    no mutation channel, so this is always 0; surfaced for v1.5 when
    overlay vs mutation becomes distinguishable.
    """
    violations = 0
    for a in loaded["review_annotations"].get("annotations", []):
        if a.get("suggested_severity") is not None:
            # No mutation channel exists in v1.4 schema.
            pass
    return violations


def _compute_cost_delta(loaded):
    # Cost ledger not present at v1.4 — flagged carry-over for main-repo.
    rec = loaded["review_annotations"]
    cost = rec.get("cost")
    if not isinstance(cost, dict):
        return None
    actual = cost.get("actual")
    estimated = cost.get("estimated")
    if actual is None or estimated in (None, 0):
        return None
    return (actual - estimated) / estimated


def compute_metrics(loaded):
    annotations = loaded["review_annotations"].get("annotations", [])
    expected = loaded["expected_annotations"]

    suppressed = _ids_by_status(annotations, "suppressed")
    confirmed = _ids_by_status(annotations, "confirmed")
    escalated = _ids_with_severity_overlay(annotations)
    correlated = _ids_with_correlation(annotations)

    exp_supp = _expected_ids(expected, "expected_suppressions")
    exp_conf = _expected_ids(expected, "expected_confirmations")
    exp_esc = _expected_ids(expected, "expected_escalations")
    exp_corr = _expected_ids(expected, "expected_correlations")

    findings_list = loaded["findings"].get("findings", [])

    metrics = {
        "suppression_precision": (len(suppressed & exp_supp) / len(suppressed)
                                  if suppressed else None),
        "false_suppression_miss_rate": (len(exp_conf & suppressed) / len(exp_conf)
                                        if exp_conf else None),
        "confirmation_recall": (len(confirmed & exp_conf) / len(exp_conf)
                                if exp_conf else None),
        "escalation_precision": (len(escalated & exp_esc) / len(escalated)
                                 if escalated else None),
        "correlation_coverage": (len(correlated & exp_corr) / len(exp_corr)
                                 if exp_corr else None),
        "confidence_calibration": _compute_calibration(annotations, exp_supp),
        "cost_delta": _compute_cost_delta(loaded),
    }
    counts = {
        "findings": len(findings_list),
        "suppressed": len(suppressed),
        "confirmed": len(confirmed),
        "escalated": len(escalated),
        "expected_suppressions": len(exp_supp),
        "expected_confirmations": len(exp_conf),
        "expected_escalations": len(exp_esc),
        "expected_correlations": len(exp_corr),
    }
    overlay_violations = _compute_overlay_violations(loaded)
    return metrics, counts, overlay_violations


def process_packet(pkt_dir):
    loaded, skip_reason = load_packet(pkt_dir)
    if loaded is None:
        return {"packet_name": pkt_dir.name, "status": "skipped",
                "reason": skip_reason}
    metrics, counts, overlay_violations = compute_metrics(loaded)
    return {"packet_name": pkt_dir.name, "status": "ok",
            "metrics": metrics, "counts": counts,
            "escalation_overlay_violations": overlay_violations}


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
