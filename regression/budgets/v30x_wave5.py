"""Budget predicates for product 3.0.x Wave 5 (tools outside the corpus gate, Gerbers, GitHub #60-#62),
range 7131f26 -> 698116c (baseline clone 40b8ff3, analyzer-identical to 7131f26).

Classes (Wave 5 handoff "Profiles and budgets"; files ``v30x-wave5{,-full-chain}.json``). Every delta is
claimed per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined set of the task classes
whose blocks or rules moved) and every delta of that unit is explained, or the unit is a residual
(label ``None``).

Gerber (Tasks 51-54): the blocks in ``GERBER_GROUPS`` and the rules GR-001 / GR-002 / GR-003 move; the
derived summaries follow the findings. Direction checks: ``alignment.aligned`` never True -> False,
``completeness.has_pth_drill`` / ``has_npth_drill`` never True -> False, and ``completeness.complete``
True -> False only on the job-file branch (``completeness.source == "gbrjob"``, Task 51).

Schematic (Task 73): only ``usb_compliance`` and UC-003 findings move.

PCB (full-chain only): ``return_path_continuity`` appears as ``[]`` (Task 71) and a degenerate
``switching_loop_areas`` record carries ``area_mm2: null`` + ``estimate: "degenerate"`` (Task 74, only
with ``--schematic``); nothing else moves.

EMC: the GP-001 "data not available" info leaves only where the upstream PCB gained the empty
``return_path_continuity`` (Task 71); GP-001 is reworded to "Return path not checked" (same count);
SW-003 "not estimated" info is added (Task 74); ``category_summary`` / ``regulatory_coverage`` follow.
Anything else needs an explained upstream pcb or schematic move (D). Thermal and cross_analysis: D only.

``python -m regression.budgets.v30x_wave5 GATE_DIR UNIT`` classifies one unit.
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
from regression.budgets.v30x_wave2 import _findings
from regression.field_compare import compare_strict, load_policy

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})
FIXED_TOP = frozenset({"analyzer_type", "schema_version", "kicad_version", "file_version", "compat"})

GERBER_GROUPS: dict[str, frozenset] = {
    "G51": frozenset({"completeness"}),
    "G52": frozenset({"component_analysis", "net_analysis", "pad_summary", "trace_widths", "connectivity",
                      "gerbers"}),
    "G53": frozenset({"drills", "drill_tools", "drill_classification", "statistics", "layer_count",
                      "completeness", "component_analysis", "gerbers", "alignment", "pad_summary"}),
    "G54": frozenset({"alignment", "board_dimensions"}),
}
GERBER_RULES = {"GR-001": "G51", "GR-002": "G54", "GR-003": "G53"}

SCH_BLOCKS = frozenset({"usb_compliance"})
SCH_RULES = frozenset({"UC-003"})

EMC_BLOCKS = frozenset({"category_summary", "regulatory_coverage"})
GP001_GONE = "Return path analysis data not available"
GP001_NEW = "Return path not checked"
SW003_NEW = "not estimated"

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


def _moved(a: dict, b: dict) -> tuple[list, list]:
    ca = Counter(_canon(f) for f in _findings(a))
    cb = Counter(_canon(f) for f in _findings(b))
    return [json.loads(k) for k in (ca - cb).elements()], [json.loads(k) for k in (cb - ca).elements()]


def _sub_diffs(a: dict, b: dict) -> set[str]:
    return {k for k in (set(a) | set(b)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}
            if a.get(k) != b.get(k) or (k in a) != (k in b)}


def _derived_ok(doc: dict, *, full: bool) -> bool:
    fs = _findings(doc)
    if full and isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


def _rule_stats(rem: list, add: list) -> Counter:
    s = Counter(f"{f.get('rule_id')}-" for f in rem)
    s.update(Counter(f"{f.get('rule_id')}+" for f in add))
    return s


def _get(doc: dict, *keys):
    for k in keys:
        if not isinstance(doc, dict):
            return None
        doc = doc.get(k)
    return doc


def _text(f: dict) -> str:
    return f"{f.get('summary', '')} {f.get('title', '')}"


# ---- gerber ---------------------------------------------------------------------------------------

def _gerber(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad = [f"block {k}" for k in sorted(subs) if k in FIXED_TOP]
    allowed = frozenset().union(*GERBER_GROUPS.values())
    bad += [f"block {k}" for k in sorted(subs - FIXED_TOP - allowed)]
    bad += [f"finding {r}" for r in sorted({f.get("rule_id") for f in rem + add} - set(GERBER_RULES))]
    trig = {g for g, blocks in GERBER_GROUPS.items() if subs & blocks}
    trig |= {GERBER_RULES[f.get("rule_id")] for f in rem + add if f.get("rule_id") in GERBER_RULES}

    al_a, al_b = _get(a, "alignment", "aligned"), _get(b, "alignment", "aligned")
    if al_a is True and al_b is False:
        bad.append("alignment.aligned True -> False")
    elif al_a is False and al_b is True:
        stats["aligned F->T"] += 1
    ca, cb = a.get("completeness") or {}, b.get("completeness") or {}
    for k in ("has_pth_drill", "has_npth_drill"):
        if ca.get(k) is True and cb.get(k) is False:
            bad.append(f"completeness.{k} True -> False")
    if ca.get("complete") is True and cb.get("complete") is False:
        if cb.get("source") == "gbrjob":
            stats["complete T->F (job)"] += 1
        else:
            bad.append("completeness.complete True -> False off the job-file branch")
    elif ca.get("complete") is False and cb.get("complete") is True:
        stats["complete F->T"] += 1
    return ("+".join(sorted(trig)) if not bad and trig else None), \
        bad or (["gerber movement without a trigger"] if not trig else []), stats


# ---- schematic ------------------------------------------------------------------------------------

def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad = [f"block {k}" for k in sorted(subs - SCH_BLOCKS)]
    bad += [f"finding {r}" for r in sorted({f.get("rule_id") for f in rem + add} - SCH_RULES)]
    trig = bool(subs & SCH_BLOCKS) or any(f.get("rule_id") in SCH_RULES for f in rem + add)
    if "usb_compliance" in subs:
        xa = {c.get("ref"): c.get("is_type_c") for c in _get(a, "usb_compliance", "connectors") or []
              if isinstance(c, dict)}
        for c in _get(b, "usb_compliance", "connectors") or []:
            if isinstance(c, dict) and c.get("ref") in xa and xa[c.get("ref")] != c.get("is_type_c"):
                stats[f"is_type_c {xa[c.get('ref')]}->{c.get('is_type_c')}"] += 1
    return ("T73" if not bad and trig else None), bad or ([] if trig else ["schematic movement without a trigger"]), stats


# ---- pcb ------------------------------------------------------------------------------------------

def _loops_ok(a: dict, b: dict) -> bool:
    la, lb = a.get("switching_loop_areas") or [], b.get("switching_loop_areas") or []
    if len(la) != len(lb):
        return False
    for x, y in zip(la, lb):
        if x == y:
            continue
        rest = {k: v for k, v in y.items() if k not in ("area_mm2", "estimate")}
        if (y.get("area_mm2") is not None or y.get("estimate") != "degenerate"
                or rest != {k: v for k, v in x.items() if k not in ("area_mm2", "estimate")}):
            return False
    return True


def _pcb(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    bad, trig, stats = [], set(), _rule_stats(rem, add)
    if "return_path_continuity" in subs:
        if "return_path_continuity" not in a and b.get("return_path_continuity") == []:
            trig.add("T71")
        else:
            bad.append("return_path_continuity beyond the empty result")
    if "switching_loop_areas" in subs:
        if _loops_ok(a, b):
            trig.add("T74")
        else:
            bad.append("switching_loop_areas beyond the degenerate record")
    bad += [f"block {k}" for k in sorted(subs - {"return_path_continuity", "switching_loop_areas"})]
    bad += [f"finding {f.get('rule_id')}" for f in rem + add][:10]
    return ("+".join(sorted(trig)) if not bad and trig else None), \
        bad or ([] if trig else ["pcb movement without a trigger"]), stats


# ---- emc ------------------------------------------------------------------------------------------

def _emc(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    trig, own_bad = set(), []
    # the old info reads "not available" on every board; a fill-less board keeps one, reworded
    gp_rem = [f for f in rem if f.get("rule_id") == "GP-001"]
    gp_add = [f for f in add if f.get("rule_id") == "GP-001"]
    if any(GP001_GONE not in _text(f) for f in gp_rem):
        own_bad.append("GP-001 other than the 'not available' info moved")
    if any(GP001_NEW not in _text(f) for f in gp_add) or len(gp_add) > len(gp_rem):
        own_bad.append("GP-001 added beyond the rewording")
    elif gp_add:
        trig.add("T71-reword")
    if len(gp_rem) > len(gp_add):
        up_pcb = _upstream_doc_pair(a, b, "pcb")
        if up_pcb is None or "return_path_continuity" in up_pcb[0] \
                or up_pcb[1].get("return_path_continuity") != []:
            own_bad.append("GP-001 'not available' removed without the empty upstream return path")
        else:
            trig.add("T71-removed")
    sw_add = [f for f in add if f.get("rule_id") == "SW-003"]
    sw_rem = [f for f in rem if f.get("rule_id") == "SW-003"]
    if sw_rem:
        own_bad.append("SW-003 lost or changed")
    if sw_add:
        if all(SW003_NEW in _text(f) and str(f.get("severity")).lower() == "info" for f in sw_add):
            trig.add("T74")
        else:
            own_bad.append("SW-003 added beyond the 'not estimated' info")
    other_blocks = [k for k in subs if k not in EMC_BLOCKS]
    other_rules = sorted({f.get("rule_id") for f in rem + add} - {"GP-001", "SW-003"})
    if not other_blocks and not other_rules:
        if own_bad:
            return None, own_bad, stats
        return ("+".join(sorted(trig)) if trig else None), ([] if trig else ["emc movement without a trigger"]), stats
    up = _upstream(a, b)
    reasons = list(own_bad)
    if not up:
        reasons.append(f"emc movement outside the Wave 5 rules with identical upstream: "
                       f"{(other_blocks + other_rules)[:6]}")
    for kind, da, db in up:
        if da is None:
            reasons.append(f"upstream {kind} unreadable")
        elif classify_unit(kind, da, db)["label"] is None:
            reasons.append(f"upstream {kind} unexplained")
    return ("+".join(sorted(trig | {"D"})) if not reasons else None), reasons, stats


_CLASSIFIERS = {"gerber": _gerber, "schematic": _schematic, "pcb": _pcb, "emc": _emc}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


# ---- upstream (chained analyzers), as in v30x_wave4b ----------------------------------------------

def _slot_root(p: str) -> str:
    m = re.match(r"(.*?/(?:baseline|candidate))/(?:schematic|pcb)/", p)
    return m.group(1) if m else ""


_UP: OrderedDict = OrderedDict()
_DELTA_UNITS: dict[str, frozenset | None] = {}


def _delta_units(slot_root: str) -> frozenset | None:
    """Units with strict deltas, from ``strict_delta_units.txt`` beside the gate (one unit per line);
    without it the upstream pair is compared directly (the strict report is too large per worker)."""
    gate = str(Path(slot_root).parent)
    if gate not in _DELTA_UNITS:
        try:
            lines = (Path(gate) / "strict_delta_units.txt").read_text(encoding="utf-8").splitlines()
            _DELTA_UNITS[gate] = frozenset(x for x in lines if x)
        except OSError:
            _DELTA_UNITS[gate] = None
    return _DELTA_UNITS[gate]


def _upstream_paths(a_doc: dict, b_doc: dict, kind: str) -> tuple[str | None, str | None]:
    ua = ((a_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    ub = ((b_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    return (ua.get(kind) or {}).get("path"), (ub.get(kind) or {}).get("path")


def _load_pair(pa: str, pb: str, kind: str):
    key = (pa, pb)
    hit = _UP.get(key)
    if hit is None:
        try:
            da = json.loads(Path(pa).read_text(encoding="utf-8"))
            db = json.loads(Path(pb).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            hit = (True, None, None)
        else:
            ds_, _ = compare_strict(da, db, _policy(), unit=kind, analyzer=kind,
                                    root_prefixes=(_slot_root(pa), _slot_root(pb)))
            hit = (bool(ds_), da, db)
        _UP[key] = hit
        while len(_UP) > 16:
            _UP.popitem(last=False)
    return hit


def _upstream_doc_pair(a_doc: dict, b_doc: dict, kind: str):
    pa, pb = _upstream_paths(a_doc, b_doc, kind)
    if not pa or not pb:
        return None
    hit = _load_pair(pa, pb, kind)
    return None if hit[1] is None else (hit[1], hit[2])


def _upstream(a_doc: dict, b_doc: dict) -> list[tuple[str, dict, dict]]:
    out = []
    for kind in ("schematic", "pcb"):
        pa, pb = _upstream_paths(a_doc, b_doc, kind)
        if not pa or not pb:
            continue
        rb = _slot_root(pb)
        known = _delta_units(rb) if rb else None
        if known is not None:
            unit = pb[len(rb) + 1:]
            unit = unit[:-len("/snap.json")] if unit.endswith("/snap.json") else unit
            if unit not in known:
                continue
        hit = _load_pair(pa, pb, kind)
        if hit[0]:
            out.append((kind, hit[1], hit[2]))
    return out


# ---- unit classification --------------------------------------------------------------------------

def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    if analyzer in ("thermal", "cross_analysis"):
        up = _upstream(a_doc, b_doc)
        if not up:
            return {"label": None, "reasons": [f"{analyzer} movement with identical upstream"], "stats": Counter()}
        reasons: list[str] = []
        for kind, da, db in up:
            if da is None:
                reasons.append(f"upstream {kind} unreadable")
            elif classify_unit(kind, da, db)["label"] is None:
                reasons.append(f"upstream {kind} unexplained")
        rem, add = _moved(a_doc, b_doc)
        return {"label": "D" if not reasons else None, "reasons": reasons,
                "stats": Counter({"upstream_" + k: 1 for k, _, _ in up}) + _rule_stats(rem, add)}
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


def _labelled(analyzers: tuple[str, ...]):
    def pred(delta, a_doc, b_doc) -> bool:
        if delta.analyzer not in analyzers:
            return False
        r = _cached(delta, a_doc, b_doc)
        return bool(r and r["label"])
    pred.__name__ = "labelled_" + "_".join(analyzers)
    return pred


gerber = _labelled(("gerber",))
schematic = _labelled(("schematic",))
pcb = _labelled(("pcb",))
emc = _labelled(("emc",))
downstream = _labelled(("thermal", "cross_analysis"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate_dir", type=Path)
    ap.add_argument("unit", help="one unit (<analyzer>/<owner>/<repo>/<file>) to classify")
    args = ap.parse_args(argv)
    a = json.loads((args.gate_dir / "baseline" / args.unit / "snap.json").read_text(encoding="utf-8"))
    b = json.loads((args.gate_dir / "candidate" / args.unit / "snap.json").read_text(encoding="utf-8"))
    r = classify_unit(args.unit.split("/", 1)[0], a, b)
    print(json.dumps({"label": r["label"], "reasons": r["reasons"], "stats": dict(r["stats"])}, indent=1))
    return 0 if r["label"] else 1


if __name__ == "__main__":
    sys.exit(main())
