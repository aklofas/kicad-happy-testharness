#!/usr/bin/env python3
"""Per-round handoff record helper (spec §9).

  new-request  --round-id R --baseline SHA --candidate SHA --kind K --profile P [--profile P2] -o FILE
  validate     FILE                     exit 0 (prints kind) / 1 (prints reasons to stderr)
  summarize    RESPONSE.json            prints the LOG paragraph

Runtime validation is a small stdlib checker; the full JSON Schema at
regression/round_record.schema.json is enforced by tests/test_round_record_schema.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SHA = re.compile(r"^[0-9a-f]{40}$")
_ROUND_ID = re.compile(r"^r[0-9]{2,3}-[a-z0-9-]+$")
_FACADE_UNTIL = re.compile(r"^r[0-9]{2,3}(-[a-z0-9-]+)?$")
_SKILL_PATH = re.compile(r"^skills/[A-Za-z0-9_./-]+\.py$")
_BUDGET = re.compile(r"^regression/budgets/[a-z0-9-]+\.json$")
KINDS = ("structural", "output-changing", "relock")
PROFILES = ("standard", "full-chain", "hierarchy", "spice-offline", "long-tail")
VERDICT_WORDS = {
    "raw": ("clean", "deltas", "error"),
    "strict": ("clean", "deltas", "error"),
    "budgeted": ("clean", "residuals", "error", "n/a"),
    "findings_summary": ("strict_clean", "clean", "not_clean"),
}
FINAL_VERDICTS = ("accept", "reject", "accept-with-filings")
REQUEST_KEYS = ("record_version", "round_id", "baseline_sha", "candidate_sha", "kind",
                "relocations", "profiles", "budget", "old_artifact_checks", "relock")
RESPONSE_KEYS = ("record_version", "round_id", "harness_sha", "run_ids", "normalization_policy",
                 "executed", "census", "verdicts", "deltas", "relocation_status",
                 "ledger_hits", "filings", "evidence", "verdict")


def _problems(doc) -> tuple[str | None, list[str]]:
    if not isinstance(doc, dict):
        return None, ["record is not an object"]
    if doc.get("record_version") != 1:
        return None, ["record_version must be 1"]
    kind, keys = ("response", RESPONSE_KEYS) if "harness_sha" in doc else ("request", REQUEST_KEYS)
    probs = [f"missing key {k}" for k in keys if k not in doc]
    if probs:
        return kind, probs
    if not _ROUND_ID.match(str(doc["round_id"])):
        probs.append("round_id must match ^r[0-9]{2,3}-[a-z0-9-]+$")
    if kind == "request":
        for k in ("baseline_sha", "candidate_sha"):
            if not _SHA.match(str(doc[k])):
                probs.append(f"{k} must be a full 40-hex sha")
        if doc["kind"] not in KINDS:
            probs.append(f"kind must be one of {KINDS}")
        profiles = doc["profiles"]
        if (not isinstance(profiles, list) or not profiles or len(set(profiles)) != len(profiles)
                or any(p not in PROFILES for p in profiles)):
            probs.append(f"profiles must be a non-empty unique subset of {PROFILES}")
        if doc["budget"] is not None and not _BUDGET.match(str(doc["budget"])):
            probs.append("budget must be null or regression/budgets/<name>.json")
        if not isinstance(doc["relock"], bool):
            probs.append("relock must be a boolean")
        for r in doc["relocations"]:
            for k in ("symbol", "old_owner", "new_owner", "new_name", "facade_until"):
                if k not in r:
                    probs.append(f"relocation {r.get('symbol')}: missing key {k}")
            for k in ("old_owner", "new_owner"):
                if k in r and not _SKILL_PATH.match(str(r[k])):
                    probs.append(f"relocation {r.get('symbol')}: {k} must be a skills/ .py path")
            fu = r.get("facade_until")
            if "facade_until" in r and fu is not None and not _FACADE_UNTIL.match(str(fu)):
                probs.append(f"relocation {r.get('symbol')}: facade_until must be null or a round id")
    else:
        if not _SHA.match(str(doc["harness_sha"])):
            probs.append("harness_sha must be a full 40-hex sha")
        for k, words in VERDICT_WORDS.items():
            if doc["verdicts"].get(k) not in words:
                probs.append(f"verdicts.{k} must be one of {words}")
        if doc["verdict"] not in FINAL_VERDICTS:
            probs.append(f"verdict must be one of {FINAL_VERDICTS}")
        d = doc["deltas"]
        if d.get("residuals", 0) > 0 and not d.get("complete_report"):
            probs.append("deltas.complete_report required when residuals > 0")
    return kind, probs


def validate_record(doc: dict) -> str:
    kind, probs = _problems(doc)
    if probs:
        raise ValueError("; ".join(probs))
    return kind


def new_request(round_id: str, baseline_sha: str, candidate_sha: str,
                kind: str, profiles: list[str]) -> dict:
    return {
        "record_version": 1, "round_id": round_id,
        "baseline_sha": baseline_sha, "candidate_sha": candidate_sha,
        "kind": kind, "relocations": [], "profiles": list(profiles),
        "budget": None, "old_artifact_checks": [],
        "expected": {"rule_count_delta": "0", "notes": ""}, "relock": False,
    }


def summarize_response(resp: dict) -> str:
    v = resp["verdicts"]
    ex = resp["executed"]
    t = ex["tests"]
    rs = resp["relocation_status"]
    return (
        f"- **{resp['round_id']}** harness `{resp['harness_sha'][:11]}` policy "
        f"`{resp['normalization_policy']}`: {ex['units']:,} units; tests "
        f"{t['collected']:,} collected / {t['passed']:,} passed / {t['skipped']} skipped / "
        f"{t['errors']} errors; raw {v['raw']}, strict {v['strict']}, budgeted {v['budgeted']}, "
        f"findings {v['findings_summary']}; residuals {resp['deltas']['residuals']}; "
        f"relocations migrated {rs['migrated']} / pending {rs['pending']}; "
        f"ledger hits {len(resp['ledger_hits'])}; "
        f"filings {', '.join(resp['filings']) or 'none'}; verdict {resp['verdict']}. "
        f"Evidence: `{resp['evidence']['manifest']}`, `{resp['evidence']['rollup']}`."
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    nr = sub.add_parser("new-request")
    nr.add_argument("--round-id", required=True)
    nr.add_argument("--baseline", required=True)
    nr.add_argument("--candidate", required=True)
    nr.add_argument("--kind", required=True, choices=KINDS)
    nr.add_argument("--profile", action="append", required=True, choices=PROFILES)
    nr.add_argument("-o", "--output", required=True)
    va = sub.add_parser("validate")
    va.add_argument("file")
    su = sub.add_parser("summarize")
    su.add_argument("file")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "new-request":
            doc = new_request(args.round_id, args.baseline, args.candidate, args.kind, args.profile)
            validate_record(doc)
            Path(args.output).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            print(args.output)
            return 0
        doc = json.loads(Path(args.file).read_text(encoding="utf-8"))
        kind = validate_record(doc)
        if args.cmd == "validate":
            print(kind)
        else:
            if kind != "response":
                raise ValueError("summarize needs a response record")
            print(summarize_response(doc))
        return 0
    except ValueError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
