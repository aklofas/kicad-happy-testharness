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
PACKET_SCHEMA_PATH = DEFAULT_PACKETS_DIR / "packet_schema.json"

PACKET_FILES = {
    "findings": "findings.json",
    "design_context": "design_context.json",
    "extraction_facts": "extraction_facts.json",
    "review_annotations": "review_annotations.json",
    "expected_annotations": "expected_annotations.json",
}

CONFIDENCE_BUCKETS = ("high", "medium", "low")
CALIBRATION_MIN_N = 5


def _validate_packet_schema(packet_dict):
    """Validate combined packet dict against packet_schema.json.

    Soft-imports jsonschema (returns None if absent — matches harness pattern).
    Returns None on success, or the first error message string on failure.
    """
    try:
        import jsonschema
    except ImportError:
        return None
    if not PACKET_SCHEMA_PATH.exists():
        return None
    schema = json.loads(PACKET_SCHEMA_PATH.read_text())
    try:
        jsonschema.validate(instance=packet_dict, schema=schema)
    except jsonschema.ValidationError as exc:
        return exc.message
    return None


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
    combined = {
        "inputs": {
            "findings": out["findings"],
            "design_context": out["design_context"],
            "extraction_facts": out["extraction_facts"],
        },
        "recorded_output": out["review_annotations"],
        "expected": out["expected_annotations"],
    }
    err = _validate_packet_schema(combined)
    if err is not None:
        return None, f"schema validation failed: {err}"
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
    cal = {}
    counts = {}
    for bucket in CONFIDENCE_BUCKETS:
        bucket_ids = {a["finding_id"] for a in annotations
                      if a.get("status") == "suppressed"
                      and a.get("confidence") == bucket}
        matched = len(bucket_ids & exp_supp_ids)
        total = len(bucket_ids)
        counts[bucket] = {"suppressed_in_bucket": total, "matched_expected": matched}
        if total < CALIBRATION_MIN_N:
            cal[bucket] = "insufficient_data"
        else:
            cal[bucket] = matched / total
    return cal, counts


def _compute_overlay_violations(loaded):
    """Escalated annotations must not mutate the raw severity field.

    At v1.4 the reviewer schema has additionalProperties=false and provides
    no mutation channel, so this always returns 0. The counter is surfaced
    in per-packet output so v1.5 can replace this body when the schema
    grows a distinguishable mutation channel.
    """
    return 0


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

    cal, cal_counts = _compute_calibration(annotations, exp_supp)
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
        "confidence_calibration": cal,
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
        "calibration_counts": cal_counts,
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


def _weighted_mean(per_packet, metric_key, weight_count_key):
    num = denom = 0.0
    for p in per_packet:
        if p["status"] != "ok":
            continue
        val = p["metrics"].get(metric_key)
        w = p["counts"].get(weight_count_key, 0)
        if val is None or w == 0:
            continue
        num += val * w
        denom += w
    return num / denom if denom > 0 else None


def _aggregate_calibration(per_packet):
    """Per-bucket pooled precision across all ok packets.

    Sums raw per-bucket counts (suppressed_in_bucket, matched_expected) from
    each ok packet's calibration_counts, then divides once per bucket.
    Returns "insufficient_data" when pooled suppressed_in_bucket < CALIBRATION_MIN_N.
    """
    out = {}
    for bucket in CONFIDENCE_BUCKETS:
        total_suppressed = 0
        total_matched = 0
        for p in per_packet:
            if p["status"] != "ok":
                continue
            cal_counts = p["counts"].get("calibration_counts", {})
            b = cal_counts.get(bucket, {})
            total_suppressed += b.get("suppressed_in_bucket", 0)
            total_matched += b.get("matched_expected", 0)
        if total_suppressed < CALIBRATION_MIN_N:
            out[bucket] = "insufficient_data"
        else:
            out[bucket] = total_matched / total_suppressed
    return out


def aggregate(per_packet):
    ok = [p for p in per_packet if p["status"] == "ok"]
    skipped = [p for p in per_packet if p["status"] == "skipped"]

    cost_deltas = [p["metrics"]["cost_delta"] for p in ok
                   if p["metrics"]["cost_delta"] is not None]

    return {
        "packet_count": len(per_packet),
        "packets_run": len(ok),
        "packets_skipped": len(skipped),
        "metrics": {
            "suppression_precision": _weighted_mean(per_packet, "suppression_precision", "suppressed"),
            "false_suppression_miss_rate": _weighted_mean(per_packet, "false_suppression_miss_rate", "expected_confirmations"),
            "confirmation_recall": _weighted_mean(per_packet, "confirmation_recall", "expected_confirmations"),
            "escalation_precision": _weighted_mean(per_packet, "escalation_precision", "escalated"),
            "correlation_coverage": _weighted_mean(per_packet, "correlation_coverage", "expected_correlations"),
            "confidence_calibration": _aggregate_calibration(per_packet),
            "cost_delta": (sum(cost_deltas) / len(cost_deltas)
                           if cost_deltas else None),
        },
        "escalation_overlay_violations_total": sum(
            p.get("escalation_overlay_violations", 0) for p in per_packet
        ),
    }


def _fmt_metric(v):
    if v is None:
        return "null"
    if isinstance(v, str):
        return v
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def render_report(per_packet, agg):
    lines = [
        "# B9 Review Metrics Report",
        "",
        f"Packets: {agg['packet_count']} total, "
        f"{agg['packets_run']} run, {agg['packets_skipped']} skipped",
        f"Escalation overlay violations total: {agg['escalation_overlay_violations_total']}",
        "",
        "## Per-packet",
        "",
    ]
    for p in per_packet:
        if p["status"] == "skipped":
            lines.append(f"- **{p['packet_name']}** — skipped: {p.get('reason', '?')}")
            continue
        m = p["metrics"]
        lines.append(
            f"- **{p['packet_name']}** — supp_prec={_fmt_metric(m['suppression_precision'])}, "
            f"miss_rate={_fmt_metric(m['false_suppression_miss_rate'])}, "
            f"conf_recall={_fmt_metric(m['confirmation_recall'])}, "
            f"esc_prec={_fmt_metric(m['escalation_precision'])}"
        )
    lines += ["", "## Aggregate", ""]
    am = agg["metrics"]
    for k in ("suppression_precision", "false_suppression_miss_rate",
              "confirmation_recall", "escalation_precision",
              "correlation_coverage", "cost_delta"):
        lines.append(f"- {k}: {_fmt_metric(am[k])}")
    lines.append("- confidence_calibration:")
    for bucket in CONFIDENCE_BUCKETS:
        lines.append(f"    - {bucket}: {_fmt_metric(am['confidence_calibration'][bucket])}")
    lines += ["", "## Carry-overs in this run", ""]
    if am["cost_delta"] is None:
        lines.append("- `cost_delta` is null — no review-cost ledger present (main-repo carry-over)")
    if all(am["confidence_calibration"][b] == "insufficient_data"
           for b in CONFIDENCE_BUCKETS):
        lines.append("- `confidence_calibration` all `insufficient_data` — pending packet corpus growth")
    if agg["packets_run"] == 1:
        lines.append("- Only 1 packet exercised — packets 02-05 await main-repo contribution (spec §15.1)")
    lines.append("")
    return "\n".join(lines)


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
