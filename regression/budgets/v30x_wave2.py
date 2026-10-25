"""Budget predicates for product 3.0.x Wave 2 (false signals), range 63f6a20 (= 2a9f998 code) -> 004bba5.

Classes (handoff-wave2.md "Budget classes"; file ``v30x-wave2.json``). Every delta is claimed per
UNIT: a unit gets exactly one label from ``classify_unit`` and every delta of that unit belongs to
the class carrying the label, or the unit is a residual (label ``None``).

  G2   gerber: findings move only on GR-001 / GR-002 / GR-005; non-finding movement only under
       completeness / alignment / gerbers / statistics / pad_summary (inner layers implied by the
       stackup, uppercase ``.GL<n>`` files read, closure-based GR-005);
  G3   cross_analysis: findings move only on CC-001 / EG-001 / DA-001 / TW-001 / DP-005;
       non-finding movement only under ``checks_run/*/{items_examined,findings}``;
  G4   thermal: every moved assessment / finding names a shunt the candidate skips with
       ``reason: no_operating_current`` (G4a) or a ref whose package row changed (G4b, the
       assessment differs only in rtheta / tj / margin fields); summary / skipped_components /
       missing_info follow;
  H1   schematic: a PR-DET regulator's ``inductor`` (or ``output_rail``) changed; every other moved
       finding names one of those regulators, their inductors (either side) or their rails, and
       non-finding movement stays in the power blocks listed in ``H1_BLOCKS``;
  H2   schematic: an OA-DET op-amp's feedback parts changed (same rules, no power blocks);
  H3   pcb: CP-001 ``description`` changed with the same multiset of words (sorted nets);
  H4   emc: ML-001 changed with the same multiset of victims (components / nets order, text);
  H5   emc: ``test_plan`` movement only;
  H6   schematic order-only: a finding's list fields changed order only (CD-DET consumers);
  DS   chained analyzers (emc / thermal / cross_analysis) whose upstream schematic or pcb snap
       differs under strict: the unit is downstream of a schematic/pcb class above (claimed only
       when the upstream unit is itself explained).

``summary`` / ``trust_summary`` / ``audience_summary`` must equal each side's own recomputation
(the v232_backport rule) for every analyzer whose derived blocks follow from ``findings[]``;
thermal and emc summaries carry extra scores, so only their ``trust_summary`` / ``audience_summary``
are recomputed.

``python -m regression.budgets.v30x_wave2 GATE_DIR -o class_summary.json`` reports per-class
units / repos / finding movements and the unexplained units with their reasons.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.field_compare import compare_strict, load_policy

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})
G2_RULES = frozenset({"GR-001", "GR-002", "GR-005"})
G2_BLOCKS = frozenset({"completeness", "alignment", "gerbers", "statistics", "pad_summary"})
# blocks built from every parsed layer: they move only when newly read .GL<n> files join (G2b)
G2_NEW_FILE_BLOCKS = frozenset({"trace_widths", "component_analysis", "layer_count"})
G3_RULES = frozenset({"CC-001", "EG-001", "DA-001", "TW-001", "DP-005"})
G4_BLOCKS = frozenset({"assessments", "skipped_components", "missing_info", "summary"})
G4_ASSESS_FIELDS = frozenset({"package", "rtheta_ja_raw", "rtheta_ja_source", "rtheta_ja_effective", "pcb_correction",
                              "pcb_correction_notes", "tj_estimated_c", "margin_c", "summary", "description"})
H1_BLOCKS = frozenset({"net_classifications", "power_budget", "pdn_impedance", "inrush_analysis",
                       "power_sequencing", "power_sequencing_validation", "rail_voltages",
                       "sleep_current_audit"})
OA_FIELDS = ("feedback_resistor", "feedback_capacitor", "input_resistor", "gain", "gain_db")
EMC_TEST_PLAN = frozenset({"test_plan"})
_REF = re.compile(r"\b[A-Z]{1,4}\d+[A-Z]?\b")

_POLICY = None


def _policy():
    global _POLICY
    if _POLICY is None:
        _POLICY = load_policy("volatile-leaves-v1")
    return _POLICY


def _canon(f: Any) -> str:
    g = dict(f) if isinstance(f, dict) else {"_": f}
    g.pop("finding_id", None)
    return json.dumps(g, sort_keys=True, default=str)


def _findings(doc: dict) -> list:
    f = doc.get("findings")
    return f if isinstance(f, list) else []


def _moved(a_doc: dict, b_doc: dict) -> tuple[list, list]:
    """Findings present on one side only, compared by content without ``finding_id``."""
    ca = Counter(_canon(f) for f in _findings(a_doc))
    cb = Counter(_canon(f) for f in _findings(b_doc))
    return [json.loads(k) for k in (ca - cb).elements()], [json.loads(k) for k in (cb - ca).elements()]


def _block_diffs(a_doc: dict, b_doc: dict) -> set[str]:
    keys = (set(a_doc) | set(b_doc)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}
    return {k for k in keys if a_doc.get(k, None) != b_doc.get(k, None) or (k in a_doc) != (k in b_doc)}


def _derived_ok(doc: dict, *, full: bool) -> bool:
    fs = _findings(doc)
    if full and isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


def _refs(f: dict) -> set[str]:
    out = set(x for x in (f.get("components") or []) if isinstance(x, str))
    for k in ("ref", "inductor", "regulator"):
        if isinstance(f.get(k), str):
            out.add(f[k])
    out |= set(_REF.findall(str(f.get("summary", ""))))
    return out


def _nets(f: dict) -> set[str]:
    out = set(x for x in (f.get("nets") or []) if isinstance(x, str))
    for k in ("output_rail", "input_rail", "net", "rail"):
        if isinstance(f.get(k), str):
            out.add(f[k])
    return out


def _order_only(x: dict, y: dict) -> bool:
    """Same finding modulo the order of its list fields (and finding_id)."""
    def norm(v):
        if isinstance(v, list):
            return sorted((norm(i) for i in v), key=lambda i: json.dumps(i, sort_keys=True, default=str))
        if isinstance(v, dict):
            return {k: norm(w) for k, w in v.items() if k != "finding_id"}
        return v
    return norm(x) == norm(y)


def _pair_by(xs: list, ys: list, key) -> tuple[list, list, list]:
    left = list(ys)
    pairs, rem = [], []
    for x in xs:
        j = next((i for i, y in enumerate(left) if key(x) == key(y)), None)
        if j is None:
            rem.append(x)
        else:
            pairs.append((x, left.pop(j)))
    return pairs, rem, left


def _fkey(f: dict):
    return (f.get("rule_id"), f.get("detector"), tuple(sorted(str(c) for c in (f.get("components") or []))),
            f.get("ref"))


# ---- per-analyzer classifiers: (label | None, reasons, stats) -----------------------------

def _gerber(a, b):
    rem, add = _moved(a, b)
    bad = [f"{f.get('rule_id')} moved" for f in rem + add if f.get("rule_id") not in G2_RULES]
    allowed = G2_BLOCKS | (G2_NEW_FILE_BLOCKS if len(b.get("gerbers") or []) > len(a.get("gerbers") or []) else set())
    bad += [f"block {k}" for k in _block_diffs(a, b) - allowed]
    stats = Counter()
    for f in rem:
        stats[f"{f.get('rule_id')}-"] += 1
    for f in add:
        stats[f"{f.get('rule_id')}+"] += 1
    if a.get("completeness", {}).get("complete") != b.get("completeness", {}).get("complete"):
        stats["complete->incomplete" if a.get("completeness", {}).get("complete") else "incomplete->complete"] += 1
    if len(a.get("gerbers") or []) != len(b.get("gerbers") or []):
        stats["gerber_files_changed"] += 1
    return ("G2" if not bad else None), bad, stats


def _cross(a, b):
    rem, add = _moved(a, b)
    bad = [f"{f.get('rule_id')} moved" for f in rem + add if f.get("rule_id") not in G3_RULES]
    blocks = _block_diffs(a, b)
    if "checks_run" in blocks:
        blocks.discard("checks_run")
        ca = {c.get("check"): c for c in a.get("checks_run") or []}
        cb = {c.get("check"): c for c in b.get("checks_run") or []}
        for k in set(ca) | set(cb):
            x, y = ca.get(k), cb.get(k)
            if x == y:
                continue
            if x is None or y is None or k not in G3_RULES:
                bad.append(f"checks_run {k}")
                continue
            if {f for f in set(x) | set(y) if x.get(f) != y.get(f)} - {"items_examined", "findings", "ran", "reason_skipped"}:
                bad.append(f"checks_run {k} fields")
    bad += [f"block {k}" for k in blocks]
    stats = Counter()
    for f in rem:
        stats[f"{f.get('rule_id')}-"] += 1
    for f in add:
        stats[f"{f.get('rule_id')}+"] += 1
    return ("G3" if not bad else None), bad, stats


def _thermal(a, b):
    skipped = {s.get("ref") for s in (b.get("skipped_components") or [])
               if isinstance(s, dict) and s.get("reason") == "no_operating_current"}
    aa = {x.get("ref"): x for x in a.get("assessments") or [] if isinstance(x, dict)}
    bb = {x.get("ref"): x for x in b.get("assessments") or [] if isinstance(x, dict)}
    bad, shunts, pkg = [], set(), set()
    for ref in set(aa) | set(bb):
        x, y = aa.get(ref), bb.get(ref)
        if x == y:
            continue
        if y is None and ref in skipped:
            shunts.add(ref)
        elif x is not None and y is not None and not ({k for k in set(x) | set(y) if x.get(k) != y.get(k)} - G4_ASSESS_FIELDS):
            pkg.add(ref)
        else:
            bad.append(f"assessment {ref}")
    touched = shunts | pkg
    rem, add = _moved(a, b)
    for f in rem + add:
        if not (_refs(f) & touched):
            bad.append(f"finding {f.get('rule_id')} {sorted(_refs(f))[:3]}")
    sk_a = {(s.get("ref"), s.get("reason")) for s in a.get("skipped_components") or [] if isinstance(s, dict)}
    sk_b = {(s.get("ref"), s.get("reason")) for s in b.get("skipped_components") or [] if isinstance(s, dict)}
    if (sk_a - sk_b) or any(r not in shunts for r, _ in sk_b - sk_a):
        bad.append("skipped_components beyond the shunts")
    bad += [f"block {k}" for k in _block_diffs(a, b) - G4_BLOCKS]
    if not touched and not bad:
        bad.append("thermal movement without a shunt or package change")
    stats = Counter({"shunt_assessments_removed": len(shunts), "package_rows": len(pkg),
                     "findings-": len(rem), "findings+": len(add)})
    if (a.get("summary") or {}).get("thermal_score") != (b.get("summary") or {}).get("thermal_score"):
        stats["thermal_score_moved"] += 1
    return ("G4" if not bad else None), bad, stats


def _schematic(a, b):
    a_f, b_f = _findings(a), _findings(b)
    pr_a = [f for f in a_f if f.get("rule_id") == "PR-DET"]
    pr_b = [f for f in b_f if f.get("rule_id") == "PR-DET"]
    regs, parts, rails = set(), set(), set()
    for x, y in _pair_by(pr_a, pr_b, lambda f: f.get("ref") or tuple(f.get("components") or []))[0]:
        if x.get("inductor") != y.get("inductor") or x.get("output_rail") != y.get("output_rail"):
            regs.add(x.get("ref") or (x.get("components") or [None])[0])
            parts |= {p for p in (x.get("inductor"), y.get("inductor")) if p}
            rails |= {r for r in (x.get("output_rail"), y.get("output_rail"), x.get("input_rail"), y.get("input_rail")) if r}
    oa_a = [f for f in a_f if f.get("rule_id") == "OA-DET"]
    oa_b = [f for f in b_f if f.get("rule_id") == "OA-DET"]
    opamps = set()
    for x, y in _pair_by(oa_a, oa_b, lambda f: f.get("ref") or tuple(f.get("components") or []))[0]:
        if any(x.get(k) != y.get(k) for k in OA_FIELDS):
            opamps.add(x.get("ref") or (x.get("components") or [None])[0])
            for k in ("feedback_resistor", "feedback_capacitor"):
                for v in (x.get(k), y.get(k)):
                    if isinstance(v, dict) and v.get("ref"):
                        parts.add(v["ref"])
    rem, add = _moved(a, b)
    pairs, rem2, add2 = _pair_by(rem, add, _fkey)
    order_only = [(x, y) for x, y in pairs if _order_only(x, y)]
    roots = regs | opamps
    bad = []
    moved = [x for x, y in pairs if (x, y) not in order_only] + rem2 + add2
    direct = [f for f in moved if roots and ((_refs(f) & (roots | parts)) or (_nets(f) & rails))]
    # one hop: a finding that shares a part with a directly affected one (an RC-DET pick that
    # moves because the op-amp now claims the other capacitor)
    hop = set().union(*(_refs(f) for f in direct)) if direct else set()
    for f in moved:
        if any(f is g for g in direct) or (f.get("rule_id") == "RC-DET" and _refs(f) & hop):
            continue
        bad.append(f"finding {f.get('rule_id')} {f.get('summary', '')[:60]}")
    blocks = _block_diffs(a, b)
    bad += [f"block {k}" for k in blocks - (H1_BLOCKS if regs else set())]
    stats = Counter({"regulators": len(regs), "opamps": len(opamps), "order_only_findings": len(order_only),
                     "findings-": len(rem2), "findings+": len(add2)})
    if bad:
        return None, bad, stats
    if regs:
        return "H1", [], stats
    if opamps:
        return "H2", [], stats
    if order_only:
        return "H6", [], stats
    return None, ["schematic movement without a trigger"], stats


def _words(text) -> Counter:
    return Counter(w.rstrip(".") for w in re.findall(r"[^\s,]+", str(text)))


def _pcb(a, b):
    rem, add = _moved(a, b)
    pairs, rem2, add2 = _pair_by(rem, add, _fkey)
    bad = [f"finding {f.get('rule_id')}" for f in rem2 + add2]
    for x, y in pairs:
        diff = {k for k in set(x) | set(y) if x.get(k) != y.get(k)} - {"finding_id"}
        if x.get("rule_id") != "CP-001" or diff - {"description", "summary"} or \
                _words(x.get("description")) != _words(y.get("description")):
            bad.append(f"changed {x.get('rule_id')} {sorted(diff)}")
    bad += [f"block {k}" for k in _block_diffs(a, b)]
    return ("H3" if not bad else None), bad, Counter({"cp001_text": len(pairs)})


def _emc(a, b):
    rem, add = _moved(a, b)
    pairs, rem2, add2 = _pair_by(rem, add, _fkey)
    bad = [f"finding {f.get('rule_id')}" for f in rem2 + add2]
    ml = 0
    if not rem and not add:
        # same findings, new order: ML-001 victims re-bound to their finding_id slots (H4)
        for x, y in zip(_findings(a), _findings(b)):
            if x != y:
                if x.get("rule_id") == "ML-001" and y.get("rule_id") == "ML-001":
                    ml += 1
                else:
                    bad.append(f"reordered {x.get('rule_id')}/{y.get('rule_id')}")
    for x, y in pairs:
        if x.get("rule_id") == "ML-001" and Counter(_refs(x)) == Counter(_refs(y)) \
                and sorted(x.get("nets") or []) == sorted(y.get("nets") or []):
            ml += 1
        else:
            bad.append(f"changed {x.get('rule_id')}")
    blocks = _block_diffs(a, b)
    bad += [f"block {k}" for k in blocks - EMC_TEST_PLAN]
    if bad:
        return None, bad, Counter({"ml001": ml})
    if ml:
        return "H4", [], Counter({"ml001": ml})
    if blocks:
        return "H5", [], Counter({"test_plan": 1})
    return None, ["emc movement without ML-001 or test_plan"], Counter()


_CLASSIFIERS = {"gerber": _gerber, "cross_analysis": _cross, "thermal": _thermal,
                "schematic": _schematic, "pcb": _pcb, "emc": _emc}
_FULL_DERIVED = {"gerber", "cross_analysis", "schematic", "pcb"}


# ---- upstream (chained analyzers) --------------------------------------------------------

def _slot_root(p: str) -> str:
    m = re.match(r"(.*?/(?:baseline|candidate))/(?:schematic|pcb)/", p)
    return m.group(1) if m else ""


_UP: OrderedDict = OrderedDict()
_DELTA_UNITS: dict[str, frozenset | None] = {}


def _delta_units(slot_root: str) -> frozenset | None:
    """Units with strict deltas, from the gate's ``field_report_strict.json`` next to the slot."""
    gate = str(Path(slot_root).parent)
    if gate not in _DELTA_UNITS:
        rep = Path(gate) / "field_report_strict.json"
        try:
            doc = json.loads(rep.read_text(encoding="utf-8"))
            _DELTA_UNITS[gate] = frozenset(d["unit"] for d in doc.get("deltas") or [])
        except (OSError, json.JSONDecodeError):
            _DELTA_UNITS[gate] = None
    return _DELTA_UNITS[gate]


def _upstream(a_doc: dict, b_doc: dict) -> list[tuple[str, dict, dict]]:
    """Upstream (kind, a_doc, b_doc) pairs that differ under strict. The gate's strict report
    decides when it is present; otherwise the two upstream snaps are compared here."""
    out = []
    ua = ((a_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    ub = ((b_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    for kind in ("schematic", "pcb"):
        pa, pb = (ua.get(kind) or {}).get("path"), (ub.get(kind) or {}).get("path")
        if not pa or not pb:
            continue
        ra, rb = _slot_root(pa), _slot_root(pb)
        known = _delta_units(rb) if rb else None
        if known is not None:
            unit = pb[len(rb) + 1:]
            unit = unit[:-len("/snap.json")] if unit.endswith("/snap.json") else unit
            if unit not in known:
                continue
        key = (pa, pb)
        hit = _UP.get(key)
        if hit is None:
            try:
                da = json.loads(Path(pa).read_text(encoding="utf-8"))
                db = json.loads(Path(pb).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                hit = (True, None, None)
            else:
                ds_, _ = compare_strict(da, db, _policy(), unit=kind, analyzer=kind, root_prefixes=(ra, rb))
                hit = (bool(ds_), da, db)
            _UP[key] = hit
            while len(_UP) > 16:
                _UP.popitem(last=False)
        if hit[0]:
            out.append((kind, hit[1], hit[2]))
    return out


# ---- unit classification ------------------------------------------------------------------

def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    up = _upstream(a_doc, b_doc) if analyzer in ("emc", "thermal", "cross_analysis") else []
    reasons: list[str] = []
    if up:
        for kind, da, db in up:
            if da is None:
                reasons.append(f"upstream {kind} unreadable")
                continue
            ulab = classify_unit(kind, da, db)["label"]
            if ulab is None:
                reasons.append(f"upstream {kind} unexplained")
        label = "DS" if not reasons else None
        return {"label": label, "reasons": reasons, "stats": Counter({"upstream_" + k: 1 for k, _, _ in up})}
    clf = _CLASSIFIERS.get(analyzer)
    if clf is None:
        return {"label": None, "reasons": [f"no class for analyzer {analyzer}"], "stats": Counter()}
    label, reasons, stats = clf(a_doc, b_doc)
    full = analyzer in _FULL_DERIVED
    if not _derived_ok(a_doc, full=full):
        reasons = reasons + ["a: derived blocks not from findings"]
    if not _derived_ok(b_doc, full=full):
        reasons = reasons + ["b: derived blocks not from findings"]
    return {"label": label if not reasons else None, "reasons": reasons, "stats": stats}


_CACHE: OrderedDict = OrderedDict()


def _cached(delta, a_doc, b_doc) -> dict | None:
    if not isinstance(a_doc, dict) or not isinstance(b_doc, dict):
        return None
    key = (id(a_doc), id(b_doc))
    hit = _CACHE.get(key)
    if hit is None:
        hit = (classify_unit(delta.analyzer, a_doc, b_doc), a_doc, b_doc)
        _CACHE[key] = hit
        while len(_CACHE) > 8:
            _CACHE.popitem(last=False)
    return hit[0]


def _label_is(label):
    def pred(delta, a_doc, b_doc) -> bool:
        r = _cached(delta, a_doc, b_doc)
        return bool(r and r["label"] == label)
    pred.__name__ = f"is_{label}"
    return pred


g2 = _label_is("G2")
g3 = _label_is("G3")
g4 = _label_is("G4")
h1 = _label_is("H1")
h2 = _label_is("H2")
h3 = _label_is("H3")
h4 = _label_is("H4")
h5 = _label_is("H5")
h6 = _label_is("H6")
ds = _label_is("DS")


# ---- adjudication summary ----------------------------------------------------------------

def summarize(gate_dir: Path, report_name: str = "field_report_strict.json") -> dict:
    rep = json.loads((gate_dir / report_name).read_text(encoding="utf-8"))
    units: dict[tuple[str, str], int] = OrderedDict()
    for d in rep.get("deltas") or []:
        units[(d["analyzer"], d["unit"])] = units.get((d["analyzer"], d["unit"]), 0) + 1
    per: dict[str, dict] = {}
    unexplained = []
    for (analyzer, unit), n in units.items():
        sub = unit.split("/", 1)[1]
        try:
            a = json.loads((gate_dir / "baseline" / unit / "snap.json").read_text(encoding="utf-8"))
            b = json.loads((gate_dir / "candidate" / unit / "snap.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            unexplained.append({"unit": unit, "reasons": [f"unreadable: {e}"]})
            continue
        r = classify_unit(analyzer, a, b)
        lab = r["label"] or "UNEXPLAINED"
        slot = per.setdefault(f"{lab}/{analyzer}", {"units": 0, "repos": set(), "deltas": 0, "stats": Counter()})
        slot["units"] += 1
        slot["repos"].add("/".join(sub.split("/")[:2]))
        slot["deltas"] += n
        slot["stats"].update(r["stats"])
        if r["label"] is None:
            unexplained.append({"unit": unit, "deltas": n, "reasons": r["reasons"][:10]})
    return {"report": str(gate_dir / report_name),
            "classes": {k: {"units": v["units"], "repos": len(v["repos"]), "deltas": v["deltas"],
                            "stats": dict(sorted(v["stats"].items()))} for k, v in sorted(per.items())},
            "unexplained_units": len(unexplained), "unexplained": unexplained}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate_dir", type=Path)
    ap.add_argument("--report", default="field_report_strict.json")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args(argv)
    out = summarize(args.gate_dir, args.report)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "unexplained"}, indent=1)[:4000])
    return 0 if out["unexplained_units"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
