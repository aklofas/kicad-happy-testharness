#!/usr/bin/env python3
"""Known-baseline-debts ledger (spec §7 step 3).

  build --product-sha SHA --references-sha SHA --checks checks.json --junit contract.xml \
        --units results/.../units.jsonl --issues ISSUES.md --analyzer-diff TEXT \
        --expected-movement TEXT -o reference/baseline_debts/<sha7>.json
  check --ledger FILE [--units units.jsonl] [--checks checks.json] [--junit contract.xml]
        exit 0 if every observed debt identity is in the ledger, 1 otherwise (prints the new ones)

`checks.json` must carry a top-level "product_sha" (emitted by run_checks.py --json).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

_KH_HEAD = re.compile(r"^### (KH-\d{3}): (.*)$")
_REPO_IN_TITLE = re.compile(r"\bon ([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b")


def check_identities(checks: dict) -> list[dict]:
    out = []
    for r in checks.get("results", []):
        if r.get("passed") or r.get("aspirational"):
            continue
        kind = "error" if r.get("error") else "fail"
        repo, project, file = r.get("repo"), r.get("project"), r.get("file")
        # run_checks parse-error records carry no repo/project: key them on the file alone
        ident = (f"{repo}/{project}/{file}::{r['id']}" if repo and project
                 else f"{file or '?'}::{r['id']}")
        out.append({
            "identity": ident,
            "id": r["id"], "repo": repo, "project": project, "file": file,
            "kind": kind, "actual": r.get("actual"), "expected": r.get("expected"),
            "error": r.get("error"), "cause": "unreviewed", "accepted_by": None,
        })
    return sorted(out, key=lambda e: e["identity"])


def _nodeid(classname: str, name: str) -> str:
    return classname.replace(".", "/") + ".py::" + name


def contract_entries(junit_xml_text: str) -> list[dict]:
    root = ET.fromstring(junit_xml_text)
    out = []
    for tc in root.iter("testcase"):
        sk = tc.find("skipped")
        if sk is None:
            continue
        kind = "xfailed" if (sk.get("type") or "").endswith("xfail") else "skipped"
        out.append({"identity": _nodeid(tc.get("classname", ""), tc.get("name", "")),
                    "kind": kind, "reason": sk.get("message", ""), "accepted_by": None})
    return sorted(out, key=lambda e: e["identity"])


def timeout_units(units_jsonl_lines: Iterable[str]) -> list[dict]:
    out = []
    for line in units_jsonl_lines:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        for side in ("baseline", "candidate"):
            s = rec.get(side)
            if s and s.get("status") == "timeout":
                out.append({"identity": f"{rec['analyzer']}/{rec['unit_id']}", "analyzer": rec["analyzer"],
                            "unit_id": rec["unit_id"], "side": side, "elapsed_s": s.get("elapsed_s"),
                            "accepted_by": None})
                break
    return sorted(out, key=lambda e: e["identity"])


def nondeterminism_entries(issues_text: str) -> list[dict]:
    out = []
    for line in issues_text.splitlines():
        m = _KH_HEAD.match(line)
        if m and re.search(r"hash[- ]seed|PYTHONHASHSEED|nondetermin", m.group(2), re.I):
            rm = _REPO_IN_TITLE.search(m.group(2))
            out.append({"identity": m.group(1), "repo": rm.group(1) if rm else None,
                        "summary": m.group(2), "accepted_by": None})
    return sorted(out, key=lambda e: e["identity"])


def build_ledger(*, product_sha: str, references_sha: str, checks: dict, junit_text: str,
                 units_lines: Iterable[str], issues_text: str, context: dict) -> dict:
    got = checks.get("product_sha")
    if not got:
        raise ValueError("checks.json has no product_sha; refuse to build a ledger from unattributed checks")
    if got != product_sha:
        raise ValueError(f"checks.json product_sha {got} != requested product_sha {product_sha}")
    return {
        "ledger_version": 1, "product_sha": product_sha, "references_target_sha": references_sha,
        "context": context, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": check_identities(checks), "contract": contract_entries(junit_text),
        "timeout_units": timeout_units(units_lines), "nondeterminism": nondeterminism_entries(issues_text),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--product-sha", required=True)
    b.add_argument("--references-sha", required=True)
    b.add_argument("--checks", required=True)
    b.add_argument("--junit", required=True)
    b.add_argument("--units", required=True)
    b.add_argument("--issues", default=str(Path(__file__).resolve().parents[1] / "ISSUES.md"))
    b.add_argument("--analyzer-diff", required=True)
    b.add_argument("--expected-movement", required=True)
    b.add_argument("-o", "--output", required=True)
    c = sub.add_parser("check")
    c.add_argument("--ledger", required=True)
    c.add_argument("--units")
    c.add_argument("--checks")
    c.add_argument("--junit")
    args = ap.parse_args(argv)

    if args.cmd == "build":
        led = build_ledger(
            product_sha=args.product_sha, references_sha=args.references_sha,
            checks=json.loads(Path(args.checks).read_text(encoding="utf-8")),
            junit_text=Path(args.junit).read_text(encoding="utf-8"),
            units_lines=Path(args.units).read_text(encoding="utf-8").splitlines(),
            issues_text=Path(args.issues).read_text(encoding="utf-8"),
            context={"analyzer_diff": args.analyzer_diff, "expected_corpus_movement": args.expected_movement},
        )
        led["sources"] = {"checks": args.checks, "contract_junit": args.junit, "units": args.units,
                          "issues": args.issues}
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"ledger: checks {len(led['checks'])} / contract {len(led['contract'])} / "
              f"timeouts {len(led['timeout_units'])} / nondeterminism {len(led['nondeterminism'])} -> {out}")
        return 0
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from baseline_ledger_check import run_check  # Task 5
    except ImportError:
        print("check requires baseline_ledger_check (Task 5)", file=sys.stderr)
        return 2
    return run_check(args)


if __name__ == "__main__":
    sys.exit(main())
