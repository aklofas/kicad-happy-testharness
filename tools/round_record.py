#!/usr/bin/env python3
"""Per-round handoff record helper.

  new-request  --round-id R --baseline SHA --candidate SHA --kind K --profile P [--profile P2]
               [--relocation-map MAP.json] -o FILE
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
_FILE_SCOPE = re.compile(r"^[^\s:]+\.py:\S+$")  # renamed[].from/to: "<file>:<scope>"
_BUDGET = re.compile(r"^regression/budgets/[a-z0-9-]+\.json$")
KINDS = ("structural", "output-changing", "relock")
PROFILES = ("standard", "full-chain", "hierarchy", "spice-offline", "long-tail", "distributor-offline")
VERDICT_WORDS = {
    "raw": ("clean", "deltas", "error"),
    "strict": ("clean", "deltas", "error"),
    "budgeted": ("clean", "residuals", "over_budget", "error", "n/a"),
    "findings_summary": ("strict_clean", "clean", "not_clean"),
}
FINAL_VERDICTS = ("accept", "reject", "accept-with-filings")
REQUEST_KEYS = ("record_version", "round_id", "baseline_sha", "candidate_sha", "kind",
                "relocations", "profiles", "budget", "old_artifact_checks", "relock")
RESPONSE_KEYS = ("record_version", "round_id", "harness_sha", "run_ids", "normalization_policy",
                 "executed", "census", "verdicts", "deltas", "relocation_status",
                 "ledger_hits", "filings", "evidence", "verdict")


_POLICY = re.compile(r"^volatile-leaves-v[0-9]+$")
_FILING = re.compile(r"^(KH|TH)-[0-9]{3}$")
REQUEST_OPTIONAL = ("expected", "removed", "known_defects_deferred", "expected_sidecar_changes",
                    "product_evidence", "moved_modules", "emit_site_moves", "patch_targets", "renamed")
RESPONSE_OPTIONAL = ("apply_map_result", "accept_baseline_diff", "scan_coverage_verdict", "budget_sha256")
RELOCATION_KEYS = ("symbol", "old_owner", "new_owner", "new_name", "facade_until")
SCAN_VERDICTS = ("pass", "fail", "not_run")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
INVENTORY_PATH = Path(__file__).resolve().parents[1] / "reference" / "product_api" / "inventory_6a91aaa.json"


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _obj(doc, key, probs, required=(), exact=False):
    """Return doc[key] if it is an object with the required keys, else record problems and return None."""
    v = doc.get(key)
    if not isinstance(v, dict):
        probs.append(f"{key} must be an object")
        return None
    for k in required:
        if k not in v:
            probs.append(f"{key} missing key {k}")
    if exact:
        for k in v:
            if k not in required:
                probs.append(f"{key} has unknown key {k}")
    return v


def _counts(v, name, probs):
    if not isinstance(v, dict) or any(not _is_int(n) or n < 0 for n in v.values()):
        probs.append(f"{name} must be an object of non-negative integers")


def _items(doc, key, keys, probs, optional=()):
    """Yield (tag, item) for each object in optional list doc[key] that has every key in `keys`
    and nothing outside `keys` + `optional`."""
    v = doc[key]
    if not isinstance(v, list):
        probs.append(f"{key} must be a list")
        return
    for i, it in enumerate(v):
        tag = f"{key}[{i}]"
        if not isinstance(it, dict) or not set(keys) <= set(it) <= set(keys) | set(optional):
            probs.append(f"{tag} must be an object with keys {keys} (optional {optional})")
            continue
        yield tag, it


def _request_additions(doc, probs):
    if "removed" in doc:
        for tag, it in _items(doc, "removed", ("symbol", "harness_refs"), probs):
            if not (isinstance(it["symbol"], str) and it["symbol"]):
                probs.append(f"{tag}.symbol must be a non-empty string")
            if not isinstance(it["harness_refs"], list) or any(not isinstance(x, str) for x in it["harness_refs"]):
                probs.append(f"{tag}.harness_refs must be a list of strings")
    if "known_defects_deferred" in doc:
        for tag, it in _items(doc, "known_defects_deferred", ("file", "line", "summary", "fix_round"), probs,
                              optional=("decision",)):
            if "decision" in it and not isinstance(it["decision"], str):
                probs.append(f"{tag}.decision must be a string")
            if not (isinstance(it["file"], str) and _SKILL_PATH.fullmatch(it["file"])):
                probs.append(f"{tag}.file must be a skills/ .py path")
            if not _is_int(it["line"]) or it["line"] < 1:
                probs.append(f"{tag}.line must be an integer >= 1")
            if not isinstance(it["summary"], str):
                probs.append(f"{tag}.summary must be a string")
            fr = it["fix_round"]
            if fr is not None and not (isinstance(fr, str) and _FACADE_UNTIL.fullmatch(fr)):
                probs.append(f"{tag}.fix_round must be null or a round id")
    if "expected_sidecar_changes" in doc:
        for tag, it in _items(doc, "expected_sidecar_changes", ("file", "leaf", "reason"), probs):
            if not all(isinstance(it[k], str) for k in ("file", "leaf", "reason")):
                probs.append(f"{tag} fields must be strings")
            elif not it["leaf"].startswith("/"):
                probs.append(f"{tag}.leaf must start with /")
    if "moved_modules" in doc:
        mm = doc["moved_modules"]
        if not isinstance(mm, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mm.items()):
            probs.append("moved_modules must be an object of string -> string")
    if "emit_site_moves" in doc:
        for tag, it in _items(doc, "emit_site_moves",
                              ("rule_or_callee", "function", "count", "from", "to", "shape"), probs):
            for k in ("rule_or_callee", "function", "shape"):
                if not isinstance(it[k], str):
                    probs.append(f"{tag}.{k} must be a string")
            if not _is_int(it["count"]) or it["count"] < 1:
                probs.append(f"{tag}.count must be an integer >= 1")
            for k in ("from", "to"):
                if not (isinstance(it[k], str) and _SKILL_PATH.fullmatch(it[k])):
                    probs.append(f"{tag}.{k} must be a skills/ .py path")
    if "patch_targets" in doc:
        # harness patch.object sites whose target binding moves with a relocated symbol
        for tag, it in _items(doc, "patch_targets", ("old", "new"), probs, optional=("harness_site", "note")):
            for k in ("old", "new", "harness_site", "note"):
                if k in it and not isinstance(it[k], str):
                    probs.append(f"{tag}.{k} must be a string")
    if "renamed" in doc:
        # scope renames as "<file>:<scope>" pairs, so renamed scopes keep their identity (TH-070)
        for tag, it in _items(doc, "renamed", ("from", "to"), probs):
            for k in ("from", "to"):
                if not (isinstance(it[k], str) and _FILE_SCOPE.fullmatch(it[k])):
                    probs.append(f"{tag}.{k} must be '<file>:<scope>'")
    if "product_evidence" in doc:
        pe = _obj(doc, "product_evidence", probs, ("quick_json", "schema_identical", "pinned_harness"), exact=True)
        if pe is not None:
            for k in ("quick_json", "pinned_harness"):
                if k in pe and not isinstance(pe[k], str):
                    probs.append(f"product_evidence.{k} must be a string")
            if "schema_identical" in pe and not isinstance(pe["schema_identical"], bool):
                probs.append("product_evidence.schema_identical must be a boolean")


def _response_additions(doc, probs):
    if "apply_map_result" in doc:
        am = _obj(doc, "apply_map_result", probs, ("sites_migrated", "files"), exact=True)
        if am is not None:
            if "sites_migrated" in am and (not _is_int(am["sites_migrated"]) or am["sites_migrated"] < 0):
                probs.append("apply_map_result.sites_migrated must be a non-negative integer")
            if "files" in am and (not isinstance(am["files"], list)
                                  or any(not isinstance(x, str) for x in am["files"])):
                probs.append("apply_map_result.files must be a list of strings")
    if "accept_baseline_diff" in doc and doc["accept_baseline_diff"] is not None \
            and not isinstance(doc["accept_baseline_diff"], str):
        probs.append("accept_baseline_diff must be a string or null")
    if "scan_coverage_verdict" in doc and doc["scan_coverage_verdict"] not in SCAN_VERDICTS:
        probs.append(f"scan_coverage_verdict must be one of {SCAN_VERDICTS}")
    if "budget_sha256" in doc and doc["budget_sha256"] is not None \
            and not (isinstance(doc["budget_sha256"], str) and _SHA256.fullmatch(doc["budget_sha256"])):
        probs.append("budget_sha256 must be null or 64 lowercase hex")


def _request_problems(doc, probs):
    for k in ("baseline_sha", "candidate_sha"):
        if not _SHA.fullmatch(str(doc[k])):
            probs.append(f"{k} must be a full 40-hex sha")
    if doc["kind"] not in KINDS:
        probs.append(f"kind must be one of {KINDS}")
    profiles = doc["profiles"]
    if (not isinstance(profiles, list) or not profiles
            or any(not isinstance(p, str) or p not in PROFILES for p in profiles)
            or len(set(profiles)) != len(profiles)):
        probs.append(f"profiles must be a non-empty unique subset of {PROFILES}")
    if doc["budget"] is not None and not (isinstance(doc["budget"], str) and _BUDGET.fullmatch(doc["budget"])):
        probs.append("budget must be null or regression/budgets/<name>.json")
    if not isinstance(doc["old_artifact_checks"], list) or any(
            not isinstance(x, str) for x in doc["old_artifact_checks"]):
        probs.append("old_artifact_checks must be a list of strings")
    if not isinstance(doc["relock"], bool):
        probs.append("relock must be a boolean")
    if "expected" in doc and not isinstance(doc["expected"], dict):
        probs.append("expected must be an object")
    _request_additions(doc, probs)
    rels = doc["relocations"]
    if not isinstance(rels, list):
        probs.append("relocations must be a list")
        return
    for i, r in enumerate(rels):
        tag = f"relocations[{i}]"
        if not isinstance(r, dict):
            probs.append(f"{tag} must be an object")
            continue
        for k in RELOCATION_KEYS:
            if k not in r:
                probs.append(f"{tag} missing key {k}")
        for k in r:
            if k not in RELOCATION_KEYS:
                probs.append(f"{tag} has unknown key {k}")
        for k in ("symbol", "new_name"):
            if k in r and not (isinstance(r[k], str) and r[k]):
                probs.append(f"{tag}.{k} must be a non-empty string")
        for k in ("old_owner", "new_owner"):
            if k in r and not (isinstance(r[k], str) and _SKILL_PATH.fullmatch(r[k])):
                probs.append(f"{tag}.{k} must be a skills/ .py path")
        fu = r.get("facade_until")
        if "facade_until" in r and fu is not None and not (isinstance(fu, str) and _FACADE_UNTIL.fullmatch(fu)):
            probs.append(f"{tag}.facade_until must be null or a round id")


def _response_problems(doc, probs):
    if not _SHA.fullmatch(str(doc["harness_sha"])):
        probs.append("harness_sha must be a full 40-hex sha")
    ids = doc["run_ids"]
    if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or len(x) < 8 for x in ids):
        probs.append("run_ids must be a non-empty list of strings of length >= 8")
    if not (isinstance(doc["normalization_policy"], str) and _POLICY.fullmatch(doc["normalization_policy"])):
        probs.append("normalization_policy must match ^volatile-leaves-v[0-9]+$")
    ex = _obj(doc, "executed", probs, ("units", "pairs_by_analyzer", "checks", "tests"), exact=True)
    if ex is not None:
        for k in ("units", "checks"):
            if k in ex and (not _is_int(ex[k]) or ex[k] < 0):
                probs.append(f"executed.{k} must be a non-negative integer")
        if "pairs_by_analyzer" in ex:
            _counts(ex["pairs_by_analyzer"], "executed.pairs_by_analyzer", probs)
        if "tests" in ex:
            t = ex["tests"]
            keys = ("collected", "passed", "skipped", "errors")
            if (not isinstance(t, dict) or set(t) != set(keys)
                    or any(not _is_int(t[k]) for k in keys)):
                probs.append("executed.tests must be an object of integers collected/passed/skipped/errors")
    ce = _obj(doc, "census", probs, ("expected", "executed", "skip_reasons"), exact=True)
    if ce is not None:
        for k in ("expected", "executed", "skip_reasons"):
            if k in ce:
                _counts(ce[k], f"census.{k}", probs)
    v = _obj(doc, "verdicts", probs, tuple(VERDICT_WORDS), exact=True)
    if v is not None:
        for k, words in VERDICT_WORDS.items():
            if k in v and v[k] not in words:
                probs.append(f"verdicts.{k} must be one of {words}")
    if doc["verdict"] not in FINAL_VERDICTS:
        probs.append(f"verdict must be one of {FINAL_VERDICTS}")
    d = _obj(doc, "deltas", probs, ("complete_report", "by_class", "residuals"), exact=True)
    if d is not None:
        res = d.get("residuals")
        if "residuals" in d and (not _is_int(res) or res < 0):
            probs.append("deltas.residuals must be a non-negative integer")
        rep = d.get("complete_report")
        if "complete_report" in d and rep is not None and not isinstance(rep, str):
            probs.append("deltas.complete_report must be a string or null")
        if "by_class" in d and not isinstance(d["by_class"], dict):
            probs.append("deltas.by_class must be an object")
        if _is_int(res) and res > 0 and not (isinstance(rep, str) and rep):
            probs.append("deltas.complete_report required when residuals > 0")
    rs = _obj(doc, "relocation_status", probs, ("migrated", "pending", "facade_still_used"), exact=True)
    if rs is not None:
        for k in ("migrated", "pending"):
            if k in rs and not _is_int(rs[k]):
                probs.append(f"relocation_status.{k} must be an integer")
        f = rs.get("facade_still_used")
        if "facade_still_used" in rs and (not isinstance(f, list) or any(not isinstance(x, str) for x in f)):
            probs.append("relocation_status.facade_still_used must be a list of strings")
    lh = doc["ledger_hits"]
    if not isinstance(lh, list) or any(not isinstance(x, str) for x in lh):
        probs.append("ledger_hits must be a list of strings")
    fl = doc["filings"]
    if not isinstance(fl, list) or any(not (isinstance(x, str) and _FILING.fullmatch(x)) for x in fl):
        probs.append("filings must be a list of KH-NNN / TH-NNN ids")
    ev = _obj(doc, "evidence", probs, ("manifest", "rollup"))
    if ev is not None:
        for k in ("manifest", "rollup"):
            if k in ev and not isinstance(ev[k], str):
                probs.append(f"evidence.{k} must be a string")
        if "adjudication" in ev and ev["adjudication"] is not None and not isinstance(ev["adjudication"], str):
            probs.append("evidence.adjudication must be a string or null")
    _response_additions(doc, probs)


def _problems(doc) -> tuple[str | None, list[str]]:
    if not isinstance(doc, dict):
        return None, ["record is not an object"]
    if doc.get("record_version") != 1 or isinstance(doc.get("record_version"), bool):
        return None, ["record_version must be 1"]
    kind, keys = ("response", RESPONSE_KEYS) if "harness_sha" in doc else ("request", REQUEST_KEYS)
    probs = [f"missing key {k}" for k in keys if k not in doc]
    allowed = keys + (REQUEST_OPTIONAL if kind == "request" else RESPONSE_OPTIONAL)
    probs += [f"unknown key {k}" for k in doc if k not in allowed]
    if probs:
        return kind, probs
    if not (isinstance(doc["round_id"], str) and _ROUND_ID.fullmatch(doc["round_id"])):
        probs.append("round_id must match ^r[0-9]{2,3}-[a-z0-9-]+$")
    (_request_problems if kind == "request" else _response_problems)(doc, probs)
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


def load_inventory(path: Path = INVENTORY_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _owner_of(module: str, inventory: dict, warned: set) -> str:
    """Skill path of dotted `module`: the inventory's product path, else derived (with a warning)."""
    derived = "skills/kicad/scripts/" + module.replace(".", "/") + ".py"
    for m in inventory.get("modules", []):
        if m.get("module") == module and m.get("product_paths"):
            paths = m["product_paths"]
            if derived in paths:
                return derived
            if len(paths) > 1 and ("paths", module) not in warned:
                warned.add(("paths", module))
                print(f"warning: module {module} has several product_paths {paths}; using {paths[0]}",
                      file=sys.stderr)
            return paths[0]
    if module not in warned:
        warned.add(module)
        print(f"warning: module {module} not in the inventory; owner derived as {derived}", file=sys.stderr)
    return derived


def _facade_round(retire) -> str:
    m = re.fullmatch(r"round\s+([0-9]+)", str(retire or "").strip())
    if not m:
        raise ValueError(f"relocation retire must be 'round N' when facade is true, got {retire!r}")
    return "r%02d" % int(m.group(1))


def normalize_relocations(data, inventory: dict) -> list[dict]:
    """Relocations in the record shape. Accepts a list (or a map dict with 'relocations') whose
    entries are either the record shape {symbol, old_owner, new_owner, new_name, facade_until}
    or the product shape {old, new, facade, retire}."""
    rels = data["relocations"] if isinstance(data, dict) else data
    if not isinstance(rels, list):
        raise ValueError("relocations must be a list")
    out, warned = [], set()
    for r in rels:
        if not isinstance(r, dict):
            raise ValueError(f"relocation must be an object: {r!r}")
        if "old" in r and "new" in r:
            old_mod, _, _ = str(r["old"]).rpartition(".")
            new_mod, _, new_name = str(r["new"]).rpartition(".")
            if not old_mod or not new_mod:
                raise ValueError(f"relocation old/new must be dotted module.symbol: {r!r}")
            out.append({"symbol": r["old"], "old_owner": _owner_of(old_mod, inventory, warned),
                        "new_owner": _owner_of(new_mod, inventory, warned), "new_name": new_name,
                        "facade_until": _facade_round(r.get("retire")) if r.get("facade") else None})
            continue
        for k in ("symbol", "old_owner", "new_owner", "new_name"):
            if k not in r:
                raise ValueError(f"relocation missing {k!r}: {r}")
        out.append({**r, "facade_until": r.get("facade_until")})
    return out


_IDENTICAL = re.compile(r"\b(?:byte-)?identical\b", re.I)
_NOT_IDENTICAL = re.compile(r"\b(?:not|non)[\s-]*(?:byte-)?identical\b", re.I)


def schema_identical(text) -> bool:
    """Exact vocabulary for the product's --schema note: '(byte-)identical' as a whole word is
    True, the same preceded by not/non/non- is False; anything else raises (never guess)."""
    s = text if isinstance(text, str) else ""
    if _NOT_IDENTICAL.search(s):
        return False
    if _IDENTICAL.search(s):
        return True
    raise ValueError(f"product_evidence_tip.schema {text!r} is not a recognised identical/not identical note")


def import_relocation_map(data: dict, inventory: dict) -> dict:
    """Request fields carried by a product relocation map; unknown top-level keys are ignored.

    `product_evidence` / `expected_sidecar_changes` / `moved_modules` / `emit_site_moves` /
    `patch_targets` / `renamed` in the record shape are carried verbatim;
    the older `product_evidence_tip` {quick, schema, harness_live_<sha>} shape is converted."""
    extra = {"relocations": normalize_relocations(data.get("relocations", []), inventory)}
    if "removed" in data:
        extra["removed"] = data["removed"]
    if "known_defects_deferred" in data:
        extra["known_defects_deferred"] = [
            {"file": d["file"], "line": d["line"], "summary": d.get("summary", d.get("issue", "")),
             "fix_round": d.get("fix_round"), **({"decision": d["decision"]} if "decision" in d else {})}
            for d in data["known_defects_deferred"]]
    if "expected_sidecar_changes" in data:
        extra["expected_sidecar_changes"] = data["expected_sidecar_changes"]
    # relocation maps (TH-070 keying input, patch_targets, renamed): carried verbatim
    for key in ("moved_modules", "emit_site_moves", "patch_targets", "renamed"):
        if key in data:
            extra[key] = data[key]
    tip = data.get("product_evidence_tip")
    if isinstance(data.get("product_evidence"), dict):
        # record shape carried verbatim; validate_record checks it
        extra["product_evidence"] = data["product_evidence"]
    elif isinstance(tip, dict):
        # keep the SHA that only the key carries: "<sha>: <value>"
        pinned = [f"{k[len('harness_live_'):]}: {v}" for k, v in sorted(tip.items())
                  if k.startswith("harness_live_")]
        extra["product_evidence"] = {"quick_json": str(tip.get("quick", "")),
                                     "schema_identical": schema_identical(tip.get("schema")),
                                     "pinned_harness": pinned[0] if pinned else ""}
    return extra


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
    ) + _summarize_additions(resp)


def _summarize_additions(resp: dict) -> str:
    parts = []
    am = resp.get("apply_map_result")
    if am:
        parts.append(f"apply-map migrated {am['sites_migrated']} sites in {len(am['files'])} files")
    if "accept_baseline_diff" in resp:
        parts.append(f"accept-baseline diff: {resp['accept_baseline_diff'] or 'none'}")
    if "scan_coverage_verdict" in resp:
        parts.append(f"scan coverage {resp['scan_coverage_verdict']}")
    if "budget_sha256" in resp:
        parts.append(f"budget sha256 {(resp['budget_sha256'] or 'none')[:12]}")
    return (" " + "; ".join(parts) + ".") if parts else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    nr = sub.add_parser("new-request")
    nr.add_argument("--round-id", required=True)
    nr.add_argument("--baseline", required=True)
    nr.add_argument("--candidate", required=True)
    nr.add_argument("--kind", required=True, choices=KINDS)
    nr.add_argument("--profile", action="append", required=True, choices=PROFILES)
    nr.add_argument("--relocation-map", default=None, metavar="MAP.json",
                    help="product relocation map (record or product shape) imported into the request")
    nr.add_argument("-o", "--output", required=True)
    va = sub.add_parser("validate")
    va.add_argument("file")
    su = sub.add_parser("summarize")
    su.add_argument("file")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "new-request":
            doc = new_request(args.round_id, args.baseline, args.candidate, args.kind, args.profile)
            if args.relocation_map:
                try:
                    data = json.loads(Path(args.relocation_map).read_text(encoding="utf-8"))
                    doc.update(import_relocation_map(data, load_inventory()))
                except (OSError, KeyError, TypeError) as e:
                    raise ValueError(f"--relocation-map {args.relocation_map}: {e}") from e
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
