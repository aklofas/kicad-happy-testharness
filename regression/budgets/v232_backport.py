"""Budget predicates for the v2.3.2 backport range 6a91aaa -> 4701c26 (GitHub PRs #57/#58/#59).

The strict comparator aligns ``findings[]`` by index, so one removed finding cascades into
field deltas on every later index, and ``audience_summary.*.top_issues`` embeds findings.
These predicates therefore judge a UNIT, not a delta: ``findings[]`` is re-paired by
``finding_id`` and every pairing outcome must be one of

  A  RS-001 with ``pins == []`` on both sides, differing only in ``confidence`` and
     ``provenance.confidence`` (deterministic -> heuristic) and ``description``
     ("carries power_in pins" -> "is named like a power rail (no power_in pin on it)");
  B  PU-001 removed whose net is ``no_connect`` with at most one pin;
  C  PP-001 removed whose pin name carries a BST / BOOT / BOOTSTRAP / CBST token;

nothing added, every other pair equal. ``summary``, ``trust_summary`` and
``audience_summary`` are pure functions of ``findings[]`` in the product (builders mirrored
below); each side's blocks must equal what its own findings produce, so a derived delta is
claimed only when it follows from an explained findings movement.

A delta is claimed only when its whole unit is explained: one unrelated change anywhere in
the unit's findings leaves EVERY delta of that unit as a residual.

``python -m regression.budgets.v232_backport GATE_DIR -o class_summary.json`` reports the
per-class magnitudes (findings / units / repos) the adjudication needs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

BOOTSTRAP_PIN_TOKENS = frozenset({"BST", "BOOT", "BOOTSTRAP", "CBST"})
RS_OLD = "carries power_in pins"
RS_NEW = "is named like a power rail (no power_in pin on it)"
A_FIELDS = frozenset({"/confidence", "/provenance/confidence", "/description"})
STAGES = ("schematic", "layout", "pre_fab", "bring_up")
_CONF_ALIAS = {"datasheet_backed": "datasheet-backed"}
DERIVED_PREFIXES = (
    "/summary/total_findings", "/summary/by_severity/",
    "/trust_summary/total_findings", "/trust_summary/trust_level", "/trust_summary/by_confidence/",
    "/trust_summary/by_evidence_source/", "/trust_summary/provenance_coverage_pct",
    "/trust_summary/unknown_confidence", "/trust_summary/unknown_evidence_source",
    "/audience_summary/",
)


# ---- class predicates on single findings --------------------------------------------------

def is_bootstrap_pin_name(pin_name: str) -> bool:
    """Mirror of the product's ``_is_bootstrap_pin_name`` (#59)."""
    tokens = re.split(r"[_/]", (pin_name or "").upper())
    return any(t.rstrip("0123456789") in BOOTSTRAP_PIN_TOKENS for t in tokens)


def pp_pin_name(finding: dict) -> str | None:
    """PP-001 names its pin ``REF.NUM (NAME)``; return NAME or None."""
    pins = finding.get("pins") or []
    if not pins or not isinstance(pins[0], str):
        return None
    m = re.search(r"\(([^()]*)\)\s*$", pins[0])
    return m.group(1) if m else None


def _diff_pointers(x: Any, y: Any, path: str = "") -> set[str]:
    if isinstance(x, dict) and isinstance(y, dict):
        out: set[str] = set()
        for k in set(x) | set(y):
            p = f"{path}/{k}"
            if k not in x or k not in y:
                out.add(p)
            else:
                out |= _diff_pointers(x[k], y[k], p)
        return out
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return {path}
        out = set()
        for i, (a, b) in enumerate(zip(x, y)):
            out |= _diff_pointers(a, b, f"{path}/{i}")
        return out
    return set() if x == y else {path}


def is_class_a(x: dict, y: dict) -> bool:
    if x.get("rule_id") != "RS-001" or y.get("rule_id") != "RS-001":
        return False
    if x.get("pins") != [] or y.get("pins") != []:
        return False
    if _diff_pointers(x, y) - {"/finding_id"} != A_FIELDS:
        return False
    if x.get("confidence") != "deterministic" or y.get("confidence") != "heuristic":
        return False
    if (x.get("provenance") or {}).get("confidence") != "deterministic" \
            or (y.get("provenance") or {}).get("confidence") != "heuristic":
        return False
    desc = x.get("description") or ""
    return RS_OLD in desc and y.get("description") == desc.replace(RS_OLD, RS_NEW, 1)


def is_class_b(x: dict, a_doc: dict) -> bool:
    if x.get("rule_id") != "PU-001":
        return False
    nets = x.get("nets") or []
    if len(nets) != 1:
        return False
    info = (a_doc.get("nets") or {}).get(nets[0])
    return isinstance(info, dict) and info.get("no_connect") is True and len(info.get("pins") or []) <= 1


def is_class_c(x: dict) -> bool:
    return x.get("rule_id") == "PP-001" and is_bootstrap_pin_name(pp_pin_name(x) or "")


# ---- derived blocks (mirrors of the product builders at 4701c26) --------------------------

def _severity_bucket(severity: Any) -> str:
    s = str(severity or "").upper()
    if s in ("CRITICAL", "HIGH", "ERROR"):
        return "error"
    if s in ("MEDIUM", "WARNING", "WARN"):
        return "warning"
    return "info"


def expected_summary(findings: list, existing: dict) -> dict:
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        if not isinstance(f, dict):
            continue
        s = str(f.get("severity", "info")).lower()
        counts[s if s in counts else "info"] += 1
    return dict(existing, total_findings=len(findings), by_severity=counts)


def expected_trust_summary(findings: list, existing: dict) -> dict:
    conf_keys = list((existing.get("by_confidence") or {}).keys())
    ev_keys = list((existing.get("by_evidence_source") or {}).keys())
    conf_values = {_CONF_ALIAS.get(k, k): k for k in conf_keys}
    by_conf = {k: 0 for k in conf_keys}
    by_ev = {k: 0 for k in ev_keys}
    unknown_conf = unknown_ev = has_prov = 0
    for f in findings:
        if not isinstance(f, dict):
            continue
        c = f.get("confidence", "")
        if c in conf_values:
            by_conf[conf_values[c]] += 1
        else:
            unknown_conf += 1
        e = f.get("evidence_source", "")
        if e in by_ev:
            by_ev[e] += 1
        else:
            unknown_ev += 1
        if f.get("provenance") is not None:
            has_prov += 1
    total = len(findings)
    if total == 0:
        level = "high"
    else:
        heuristic_pct = 100 * by_conf.get("heuristic", 0) / total
        level = "low" if (heuristic_pct > 50 or unknown_conf > 0) else "mixed" if heuristic_pct > 20 else "high"
    out = dict(existing, total_findings=total, trust_level=level, by_confidence=by_conf, by_evidence_source=by_ev,
               provenance_coverage_pct=round(100 * has_prov / total, 1) if total else None)
    for key, n in (("unknown_confidence", unknown_conf), ("unknown_evidence_source", unknown_ev)):
        if n:
            out[key] = n
        else:
            out.pop(key, None)
    return out


def expected_audience_summary(findings: list) -> dict:
    errors, warnings, infos = [], [], []
    by_category: dict[str, int] = {}
    by_category_err_warn: dict[str, int] = {}
    for f in findings:
        bucket = _severity_bucket(f.get("severity", ""))
        cat = f.get("category", "uncategorized") or "uncategorized"
        by_category[cat] = by_category.get(cat, 0) + 1
        if bucket == "error":
            errors.append(f)
            by_category_err_warn[cat] = by_category_err_warn.get(cat, 0) + 1
        elif bucket == "warning":
            warnings.append(f)
            by_category_err_warn[cat] = by_category_err_warn.get(cat, 0) + 1
        else:
            infos.append(f)
    top_full = (errors + warnings)[:10]
    top_reviewer = [{
        "rule_id": f.get("rule_id", ""), "severity": f.get("severity", ""),
        "summary": f.get("summary", f.get("message", "")),
        "recommendation": f.get("recommendation", f.get("fix", "")),
        "category": f.get("category", "uncategorized"),
    } for f in errors + warnings]
    stage_readiness = {}
    for stage in STAGES:
        se = sum(1 for f in findings if stage in f.get("stages", ["schematic"]) and _severity_bucket(f.get("severity", "")) == "error")
        sw = sum(1 for f in findings if stage in f.get("stages", ["schematic"]) and _severity_bucket(f.get("severity", "")) == "warning")
        stage_readiness[stage] = "needs_work" if se else "needs_review" if sw else "pass"
    blocker_count, warning_count = len(errors), len(warnings)
    cat_count = len([c for c in by_category_err_warn if by_category_err_warn[c] > 0])
    blocked = [s for s in STAGES if stage_readiness[s] == "needs_work"]
    if blocker_count == 0 and warning_count == 0:
        one_liner = "No errors or warnings — all stages ready."
    else:
        parts = []
        if blocker_count:
            parts.append(f'{blocker_count} error{"s" if blocker_count != 1 else ""}')
        if warning_count:
            parts.append(f'{warning_count} warning{"s" if warning_count != 1 else ""}')
        summary_str = ", ".join(parts)
        cat_str = f'across {cat_count} categor{"ies" if cat_count != 1 else "y"}' if cat_count else ""
        blocker_str = ""
        if blocked:
            names = ", ".join(s.replace("_", "-") for s in blocked)
            blocker_str = (f' {names.capitalize()} stage{"s" if len(blocked) != 1 else ""} '
                           f'{"have" if len(blocked) != 1 else "has"} blockers.')
        one_liner = f'{summary_str}{" " + cat_str if cat_str else ""}.{blocker_str}'
    if blocker_count >= 5:
        risk = "high"
    elif blocker_count >= 1 or warning_count >= 10:
        risk = "moderate"
    elif warning_count >= 1:
        risk = "low"
    else:
        risk = "none"
    return {
        "designer": {"total_findings": len(findings),
                     "by_severity": {"error": len(errors), "warning": len(warnings), "info": len(infos)},
                     "by_category": by_category, "top_issues": top_full},
        "reviewer": {"total_findings": len(errors) + len(warnings), "by_category": by_category_err_warn,
                     "top_issues": top_reviewer},
        "manager": {"risk_level": risk, "blocker_count": blocker_count, "warning_count": warning_count,
                    "stage_readiness": stage_readiness, "one_liner": one_liner},
    }


def derived_mismatches(doc: dict, side: str) -> list[str]:
    findings = doc.get("findings") if isinstance(doc.get("findings"), list) else []
    out = []
    if isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(findings, doc["summary"]):
        out.append(f"{side}: summary not derived from findings")
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(findings, doc["trust_summary"]):
        out.append(f"{side}: trust_summary not derived from findings")
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(findings):
        out.append(f"{side}: audience_summary not derived from findings")
    return out


# ---- unit analysis ------------------------------------------------------------------------

def _pair_key(f: dict) -> str:
    """Pairing key: the finding_id without its ``#N`` duplicate suffix. The product numbers
    findings that share a detection hash ``…``, ``…#1``, ``…#2`` in list order, so removing
    one renumbers the rest; pairing on the base key and matching by content absorbs that."""
    fid = f.get("finding_id")
    if fid:
        return re.sub(r"#\d+$", "", str(fid))
    return json.dumps([f.get("rule_id"), f.get("detector"), f.get("components"), f.get("nets"),
                       f.get("pins"), f.get("summary")], sort_keys=True, default=str)


def _match_group(xs: list, ys: list) -> tuple[list, list, list]:
    """Pair baseline findings ``xs`` with candidate findings ``ys`` of one base key: content
    match first, then a class-A match. Returns (pairs, removed, added)."""
    left = list(ys)
    pairs, removed = [], []
    for x in xs:
        j = next((i for i, y in enumerate(left) if not (_diff_pointers(x, y) - {"/finding_id"})), None)
        if j is None:
            j = next((i for i, y in enumerate(left) if is_class_a(x, y)), None)
        if j is None:
            removed.append(x)
        else:
            pairs.append((x, left.pop(j)))
    return pairs, removed, left


def analyze_unit(a_doc: dict, b_doc: dict) -> dict:
    """Re-pair findings by finding_id and classify every movement. ``explained`` is True iff
    every movement is A, B or C; ``derived_ok`` iff both sides' derived blocks follow from
    their own findings."""
    a_f = a_doc.get("findings") if isinstance(a_doc.get("findings"), list) else []
    b_f = b_doc.get("findings") if isinstance(b_doc.get("findings"), list) else []
    ga: dict[str, list] = OrderedDict()
    gb: dict[str, list] = OrderedDict()
    for f in a_f:
        ga.setdefault(_pair_key(f), []).append(f)
    for f in b_f:
        gb.setdefault(_pair_key(f), []).append(f)
    n = {"A": 0, "B": 0, "C": 0}
    reasons: list[str] = []
    b_nets: list[str] = []
    c_pins: list[str] = []
    for key in list(ga) + [k for k in gb if k not in ga]:
        xs, ys = ga.get(key, []), gb.get(key, [])
        pairs, removed, added = _match_group(xs, ys)
        for x, y in pairs:
            d = _diff_pointers(x, y)
            if not d:
                continue
            if d == {"/finding_id"}:
                if not removed:
                    reasons.append(f"finding_id renumbered without a removal in its group ({key})")
                continue
            if is_class_a(x, y):
                n["A"] += 1
            else:
                reasons.append(f"changed finding {x.get('rule_id')} {key}: {sorted(d)[:8]}")
        for x in removed:
            if is_class_b(x, a_doc):
                n["B"] += 1
                b_nets.append((x.get("nets") or [""])[0])
            elif is_class_c(x):
                n["C"] += 1
                c_pins.append(pp_pin_name(x) or "")
            elif x.get("rule_id") == "RS-001" and x.get("pins") != [] and any(
                    y.get("rule_id") == "RS-001" and (_diff_pointers(x, y) - {"/finding_id"}) <= A_FIELDS for y in added):
                reasons.append(f"A-violation: RS-001 flip with pins != [] ({key})")
            else:
                reasons.append(f"removed finding outside B/C: {x.get('rule_id')} {key}")
        for y in added:
            reasons.append(f"added finding: {y.get('rule_id')} {key}")
    derived = derived_mismatches(a_doc, "a") + derived_mismatches(b_doc, "b")
    return {"explained": not reasons, "derived_ok": not derived, "reasons": reasons,
            "derived_reasons": derived, "A": n["A"], "B": n["B"], "C": n["C"],
            "b_nets": b_nets, "c_pins": c_pins}


_CACHE: OrderedDict = OrderedDict()   # (id(a), id(b)) -> (analysis, a, b); the docs are held so ids stay valid
_CACHE_MAX = 8


def _analysis(a_doc: Any, b_doc: Any) -> dict | None:
    if not isinstance(a_doc, dict) or not isinstance(b_doc, dict):
        return None
    key = (id(a_doc), id(b_doc))
    hit = _CACHE.get(key)
    if hit is not None:
        _CACHE.move_to_end(key)
        return hit[0]
    an = analyze_unit(a_doc, b_doc)
    _CACHE[key] = (an, a_doc, b_doc)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)
    return an


# ---- the budget predicates: (delta, a_doc, b_doc) -> bool ---------------------------------

def findings_explained(delta, a_doc, b_doc) -> bool:
    an = _analysis(a_doc, b_doc)
    return bool(an and an["explained"])


def derived_explained(delta, a_doc, b_doc) -> bool:
    an = _analysis(a_doc, b_doc)
    return bool(an and an["explained"] and an["derived_ok"] and delta.path.startswith(DERIVED_PREFIXES))


# ---- adjudication summary ----------------------------------------------------------------

def summarize(gate_dir: Path, report_name: str = "field_report_strict.json") -> dict:
    """Per-class magnitudes over every compared unit with deltas in a gate's strict report."""
    g = Path(gate_dir)
    rep = json.loads((g / report_name).read_text(encoding="utf-8"))
    a_root, b_root = Path(rep["a_root"]), Path(rep["b_root"])
    classes = {k: {"findings": 0, "units": 0, "repos": set()} for k in "ABC"}
    unexplained, derived_bad = [], []
    by_analyzer: dict[str, int] = {}
    c_pin_names: dict[str, int] = {}
    b_units_multi = 0
    for u in rep["units"]:
        if u["status"] != "compared" or not u.get("delta_count"):
            continue
        by_analyzer[u["analyzer"]] = by_analyzer.get(u["analyzer"], 0) + 1
        if u["analyzer"] != "schematic":
            continue
        a_doc = json.loads((a_root / u["a"]).read_text(encoding="utf-8"))
        b_doc = json.loads((b_root / u["b"]).read_text(encoding="utf-8"))
        an = analyze_unit(a_doc, b_doc)
        repo = "/".join(u["unit"].split("/")[1:3])
        for k in "ABC":
            if an[k]:
                classes[k]["findings"] += an[k]
                classes[k]["units"] += 1
                classes[k]["repos"].add(repo)
        for p in an["c_pins"]:
            c_pin_names[p] = c_pin_names.get(p, 0) + 1
        if an["B"] > 1:
            b_units_multi += 1
        if not an["explained"]:
            unexplained.append({"unit": u["unit"], "reasons": an["reasons"][:20]})
        if not an["derived_ok"]:
            derived_bad.append({"unit": u["unit"], "reasons": an["derived_reasons"]})
    return {
        "report": str(g / report_name),
        "units_with_deltas_by_analyzer": by_analyzer,
        "classes": {k: {"findings": v["findings"], "units": v["units"], "repos": len(v["repos"])} for k, v in classes.items()},
        "c_pin_names": dict(sorted(c_pin_names.items(), key=lambda kv: (-kv[1], kv[0]))),
        "b_units_with_several_removals": b_units_multi,
        "unexplained_units": unexplained,
        "derived_inconsistent_units": derived_bad,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("gate_dir")
    ap.add_argument("--report", default="field_report_strict.json")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    out = summarize(Path(args.gate_dir), args.report)
    text = json.dumps(out, indent=1)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("units_with_deltas_by_analyzer", "classes", "c_pin_names",
                                          "b_units_with_several_removals")}, indent=1))
    print(f"unexplained units: {len(out['unexplained_units'])}  derived-inconsistent units: {len(out['derived_inconsistent_units'])}")
    return 0 if not out["unexplained_units"] and not out["derived_inconsistent_units"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
