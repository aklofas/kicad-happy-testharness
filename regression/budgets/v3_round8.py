"""Budget predicates for v3 round 8, range 0490c49 -> a0df172 (the arc's first budgeted round).

Classes (handoff-round8.md §3; files ``v3-round8.json`` / ``v3-round8-full-chain.json``):

  B1  every envelope gains ``diagnostics`` right after ``compat``; the value must be ``[]``
      (a non-empty list is a real degraded path and stays a residual on purpose);
  B2  EMC findings lose ``title`` (``summary`` always carried the same text) and follow
      ``make_finding``'s key order, also in the ``audience_summary.*.top_issues`` copies;
  B3  ``schema_era: "v3.0"`` added on findings of the 73 listed rule IDs (and their
      top_issues / datasheet_verification copies); the value must be exactly ``"v3.0"``;
  B4  datasheet_verification severities CRITICAL/HIGH -> error, MEDIUM -> warning,
      LOW/INFO -> info, and ``summary.by_severity`` recounted;
  B5  schematic findings re-paired by ``finding_id`` base (the v232_backport pattern):
      (A) RS-001 removed where every power_in pin on its net is bootstrap-named (KH-454),
      (B) PP-001 added for a power_in ``(ref, pin_number)`` that sits on two or more nets
      (KH-455); every other pair equal modulo ``finding_id`` and a B3 ``schema_era``.
      ``summary`` / ``trust_summary`` / ``audience_summary`` must equal each side's own
      recomputation. A unit without an A or B movement is NOT a B5 unit: its B3 deltas
      belong to B3 alone, so the B5 unit bound counts only KH-454/KH-455 units.

``python -m regression.budgets.v3_round8 GATE_DIR -o class_summary.json`` reports the A / B
magnitudes (findings / units / repos), the unexplained units and any non-empty diagnostics.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

from regression.budgets.v232_backport import (
    DERIVED_PREFIXES,
    _diff_pointers,
    _pair_key,
    derived_mismatches,
    is_bootstrap_pin_name,
)

ERA = "v3.0"
RS_PIN_ADMITTED = "carries power_in pins"
# emc_rules._make_finding at a0df172 (= finding_schema.make_finding's order); extras follow
# report_context and finding_id is appended last by assign_finding_ids.
FINDING_KEY_ORDER = ("detector", "rule_id", "category", "summary", "description", "components",
                     "nets", "pins", "severity", "confidence", "evidence_source", "recommendation",
                     "fix_params", "report_context")
_SEVERITY_MAP = {"CRITICAL": "error", "HIGH": "error", "ERROR": "error",
                 "MEDIUM": "warning", "WARNING": "warning", "WARN": "warning",
                 "LOW": "info", "INFO": "info"}


def _b3_rules() -> frozenset:
    budget = json.loads((Path(__file__).with_name("v3-round8.json")).read_text(encoding="utf-8"))
    for c in budget["classes"]:
        if c["id"] == "B3-schema-era":
            return frozenset(c["where"]["rule_id"])
    raise RuntimeError("v3-round8.json has no B3-schema-era class")


B3_RULES = _b3_rules()


# ---- pointer helpers ----------------------------------------------------------------------

def _tokens(path: str) -> list[str]:
    return [t.replace("~1", "/").replace("~0", "~") for t in path.split("/")[1:]] if path else []


def _resolve(doc: Any, tokens: list[str]) -> tuple[bool, Any]:
    cur = doc
    for t in tokens:
        if isinstance(cur, dict):
            if t not in cur:
                return False, None
            cur = cur[t]
        elif isinstance(cur, list) and t.isdigit() and int(t) < len(cur):
            cur = cur[int(t)]
        else:
            return False, None
    return True, cur


def _parent_finding(doc: Any, path: str) -> dict | None:
    """The finding dict that owns ``path``'s last token (``/findings/3/title`` -> finding 3)."""
    ok, v = _resolve(doc, _tokens(path)[:-1])
    return v if ok and isinstance(v, dict) else None


def _canonical_order(keys: list[str]) -> bool:
    rank = {k: i for i, k in enumerate(FINDING_KEY_ORDER)}
    seen = [rank[k] for k in keys if k in rank]
    if seen != sorted(seen):
        return False
    # extras (schema_era, source_path, ...) sit after report_context, finding_id last
    if "report_context" in keys:
        after = keys[keys.index("report_context") + 1:]
        if any(k in rank for k in after):
            return False
    return "finding_id" not in keys or keys[-1] == "finding_id"


# ---- B1 / B2 / B3 / B4 --------------------------------------------------------------------

def b1_explained(delta, a_doc, b_doc) -> bool:
    return delta.path == "/diagnostics" and delta.op == "added" and delta.after == [] \
        and isinstance(a_doc, dict) and "diagnostics" not in a_doc


def b2_explained(delta, a_doc, b_doc) -> bool:
    if delta.analyzer != "emc":
        return False
    if delta.op == "removed" and delta.path.endswith("/title"):
        x = _parent_finding(a_doc, delta.path)
        y = _parent_finding(b_doc, delta.path)
        if not x or not y or "title" in y:
            return False
        return x.get("summary") == x.get("title") and y.get("summary") == x.get("title")
    if delta.op == "key_order":
        ok, y = _resolve(b_doc, _tokens(delta.path))
        ok2, x = _resolve(a_doc, _tokens(delta.path))
        if not (ok and ok2 and isinstance(x, dict) and isinstance(y, dict)):
            return False
        return "title" not in y and _canonical_order(list(y.keys())) \
            and set(x) - set(y) <= {"title"} and set(y) - set(x) <= {"schema_era"}
    return False


def b3_explained(delta, a_doc, b_doc) -> bool:
    if delta.op != "added" or not delta.path.endswith("/schema_era") or delta.after != ERA:
        return False
    y = _parent_finding(b_doc, delta.path)
    if not y or y.get("rule_id") not in B3_RULES:
        return False
    x = _parent_finding(a_doc, delta.path)
    return x is None or "schema_era" not in x


def _dv_counts(doc: Any) -> dict | None:
    dv = (doc or {}).get("datasheet_verification") if isinstance(doc, dict) else None
    if not isinstance(dv, dict):
        return None
    counts: dict[str, int] = {}
    for f in dv.get("findings") or []:
        if isinstance(f, dict):
            s = str(f.get("severity", "")).lower()
            counts[s] = counts.get(s, 0) + 1
    return counts


def b4_explained(delta, a_doc, b_doc) -> bool:
    if delta.analyzer != "schematic":
        return False
    if delta.path.startswith("/datasheet_verification/findings/") and delta.path.endswith("/severity"):
        return delta.op == "changed" and _SEVERITY_MAP.get(str(delta.before).upper()) == delta.after \
            and str(delta.after) in ("error", "warning", "info")
    if delta.path.startswith("/datasheet_verification/summary/by_severity/"):
        a_c, b_c = _dv_counts(a_doc), _dv_counts(b_doc)
        if a_c is None or b_c is None:
            return False
        b_by = b_doc["datasheet_verification"].get("summary", {}).get("by_severity")
        return isinstance(b_by, dict) and all(b_by.get(k, 0) == v for k, v in b_c.items()) \
            and set(b_by) <= {"error", "warning", "info"}
    return False


# ---- B5: unit-level analysis ---------------------------------------------------------------

def _b3_allowance(x: dict, y: dict) -> set[str]:
    """Pointers a pair may differ on besides finding_id: a freshly added v3.0 schema_era."""
    if "schema_era" not in x and y.get("schema_era") == ERA and y.get("rule_id") in B3_RULES:
        return {"/finding_id", "/schema_era"}
    return {"/finding_id"}


def _same(x: dict, y: dict) -> bool:
    return not (_diff_pointers(x, y) - _b3_allowance(x, y))


def is_class_a(x: dict, a_doc: dict) -> bool:
    """KH-454: a pin-admitted RS-001 whose power_in pins are all bootstrap-named."""
    if x.get("rule_id") != "RS-001" or RS_PIN_ADMITTED not in (x.get("description") or ""):
        return False
    nets = x.get("nets") or []
    info = (a_doc.get("nets") or {}).get(nets[0]) if nets else None
    if not isinstance(info, dict):
        return False
    pins = [p for p in info.get("pins") or [] if isinstance(p, dict) and p.get("pin_type") == "power_in"]
    return bool(pins) and all(is_bootstrap_pin_name(p.get("pin_name") or "") for p in pins)


_PP_PIN = re.compile(r"^\s*(?P<ref>[^.\s]+)\.(?P<num>[^\s(]+)")


def is_class_b(y: dict, b_doc: dict) -> bool:
    """KH-455: a PP-001 for a power_in (ref, pin_number) that sits on two or more nets."""
    if y.get("rule_id") != "PP-001":
        return False
    pins = y.get("pins") or []
    m = _PP_PIN.match(pins[0]) if pins and isinstance(pins[0], str) else None
    if not m:
        return False
    ref, num = m.group("ref"), m.group("num")
    on_nets = 0
    for info in (b_doc.get("nets") or {}).values():
        if not isinstance(info, dict):
            continue
        if any(isinstance(p, dict) and p.get("component") == ref and str(p.get("pin_number")) == num
               and p.get("pin_type") == "power_in" for p in info.get("pins") or []):
            on_nets += 1
    return on_nets >= 2


def _match_group(xs: list, ys: list) -> tuple[list, list, list]:
    left = list(ys)
    pairs, removed = [], []
    for x in xs:
        j = next((i for i, y in enumerate(left) if _same(x, y)), None)
        if j is None:
            removed.append(x)
        else:
            pairs.append((x, left.pop(j)))
    return pairs, removed, left


def analyze_unit(a_doc: dict, b_doc: dict) -> dict:
    a_f = a_doc.get("findings") if isinstance(a_doc.get("findings"), list) else []
    b_f = b_doc.get("findings") if isinstance(b_doc.get("findings"), list) else []
    ga: dict[str, list] = OrderedDict()
    gb: dict[str, list] = OrderedDict()
    for f in a_f:
        ga.setdefault(_pair_key(f), []).append(f)
    for f in b_f:
        gb.setdefault(_pair_key(f), []).append(f)
    n = {"A": 0, "B": 0}
    reasons: list[str] = []
    a_nets: list[str] = []
    b_pins: list[str] = []
    for key in list(ga) + [k for k in gb if k not in ga]:
        xs, ys = ga.get(key, []), gb.get(key, [])
        pairs, removed, added = _match_group(xs, ys)
        for x, y in pairs:
            d = _diff_pointers(x, y) - _b3_allowance(x, y)
            if d:
                reasons.append(f"changed finding {x.get('rule_id')} {key}: {sorted(d)[:8]}")
            elif "/finding_id" in _diff_pointers(x, y) and not removed and not added:
                reasons.append(f"finding_id renumbered without a movement in its group ({key})")
        for x in removed:
            if is_class_a(x, a_doc):
                n["A"] += 1
                a_nets.append((x.get("nets") or [""])[0])
            else:
                reasons.append(f"removed finding outside A: {x.get('rule_id')} {key}")
        for y in added:
            if is_class_b(y, b_doc):
                n["B"] += 1
                b_pins.append((y.get("pins") or [""])[0])
            else:
                reasons.append(f"added finding outside B: {y.get('rule_id')} {key}")
    derived = derived_mismatches(a_doc, "a") + derived_mismatches(b_doc, "b")
    return {"explained": not reasons, "derived_ok": not derived, "reasons": reasons,
            "derived_reasons": derived, "A": n["A"], "B": n["B"], "a_nets": a_nets, "b_pins": b_pins,
            "moved": bool(n["A"] or n["B"])}


_CACHE: OrderedDict = OrderedDict()   # (id(a), id(b)) -> (analysis, a, b); docs held so ids stay valid
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


def b5_findings_explained(delta, a_doc, b_doc) -> bool:
    an = _analysis(a_doc, b_doc)
    return bool(an and an["moved"] and an["explained"])


def b5_derived_explained(delta, a_doc, b_doc) -> bool:
    an = _analysis(a_doc, b_doc)
    return bool(an and an["moved"] and an["explained"] and an["derived_ok"]
                and delta.path.startswith(DERIVED_PREFIXES))


# ---- adjudication summary ----------------------------------------------------------------

def summarize(gate_dir: Path, report_name: str = "field_report_strict.json") -> dict:
    """A / B magnitudes over every schematic unit with deltas, the unexplained units, and
    every unit whose candidate ``diagnostics`` is not ``[]``."""
    g = Path(gate_dir)
    rep = json.loads((g / report_name).read_text(encoding="utf-8"))
    a_root, b_root = Path(rep["a_root"]), Path(rep["b_root"])
    classes = {k: {"findings": 0, "units": 0, "repos": set()} for k in "AB"}
    unexplained, derived_bad, diag = [], [], []
    by_analyzer: dict[str, int] = {}
    a_net_names: dict[str, int] = {}
    for u in rep["units"]:
        if u["status"] != "compared" or not u.get("delta_count"):
            continue
        by_analyzer[u["analyzer"]] = by_analyzer.get(u["analyzer"], 0) + 1
        b_doc = json.loads((b_root / u["b"]).read_text(encoding="utf-8"))
        if isinstance(b_doc, dict) and b_doc.get("diagnostics"):
            diag.append({"unit": u["unit"], "diagnostics": b_doc["diagnostics"]})
        if u["analyzer"] != "schematic":
            continue
        a_doc = json.loads((a_root / u["a"]).read_text(encoding="utf-8"))
        an = analyze_unit(a_doc, b_doc)
        repo = "/".join(u["unit"].split("/")[1:3])
        for k in "AB":
            if an[k]:
                classes[k]["findings"] += an[k]
                classes[k]["units"] += 1
                classes[k]["repos"].add(repo)
        for name in an["a_nets"]:
            a_net_names[name] = a_net_names.get(name, 0) + 1
        if not an["explained"]:
            unexplained.append({"unit": u["unit"], "reasons": an["reasons"][:20]})
        if an["moved"] and not an["derived_ok"]:
            derived_bad.append({"unit": u["unit"], "reasons": an["derived_reasons"]})
    return {
        "report": str(g / report_name),
        "units_with_deltas_by_analyzer": by_analyzer,
        "classes": {k: {"findings": v["findings"], "units": v["units"], "repos": len(v["repos"])}
                    for k, v in classes.items()},
        "a_net_names": dict(sorted(a_net_names.items(), key=lambda kv: (-kv[1], kv[0]))),
        "non_empty_diagnostics": diag,
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
    print(json.dumps({k: out[k] for k in ("units_with_deltas_by_analyzer", "classes", "a_net_names")}, indent=1))
    print(f"non-empty diagnostics: {len(out['non_empty_diagnostics'])}  unexplained units: "
          f"{len(out['unexplained_units'])}  derived-inconsistent units: {len(out['derived_inconsistent_units'])}")
    return 0 if not out["unexplained_units"] and not out["derived_inconsistent_units"] and not out["non_empty_diagnostics"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
