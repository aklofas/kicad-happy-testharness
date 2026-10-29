"""Budget predicates for product 3.0.x Wave 4 Part B (PCB checks, board graph, return paths, EMC, net classes),
range d5c500e -> 40b8ff3.

Classes (Wave 4 Part B handoff "Budget classes"; files ``v30x-wave4b{,-full-chain}.json``). Every delta is
claimed per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined set of the classes whose
blocks or rules moved) and every delta of that unit is explained, or the unit is a residual (label ``None``).

PCB: each class in ``PCB_CLASSES`` opens its blocks (top-level keys, or ``<composite>.<sub-key>`` for the
dict blocks in ``COMPOSITE``) and its finding rules; a class is triggered by its own blocks or rules moving.
``footprints[]`` records may move only in ``FOOTPRINT_FIELDS`` (P6 courtyards, P7 attributes) and
``diagnostics`` only by records whose message names a Part B diagnostic (``DIAG_MARKERS``: P6 open
courtyards, P9 outline, P11d routing note, P11 graph errors).

Schematic: only ``pdn_impedance`` (P14b) and ``design_analysis.net_classification`` (P16) may move.

EMC: the P8b / P12 / P13 / P14a / P15 rules and blocks in ``EMC_RULES`` / ``EMC_BLOCKS`` move on their own
(the EMC rules changed in this round); anything else needs an explained upstream pcb or schematic move (D).
Thermal and cross_analysis: ``D`` only, behind an explained upstream (P10 thermal, P11c / P12 cross).

``python -m regression.budgets.v30x_wave4b GATE_DIR -o class_summary.json`` reports per-label units /
repos / deltas and the unexplained units with their reasons.
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
COMPOSITE = frozenset({"statistics", "setup", "connectivity", "design_analysis", "placement",
                       "design_rule_compliance", "test_plan"})

PCB_CLASSES: dict[str, tuple[frozenset, frozenset]] = {
    "P1": (frozenset(), frozenset({"KO-001"})),
    "P2": (frozenset({"project_settings", "net_classes", "design_intent", "design_rule_compliance"}), frozenset()),
    # P3 / P3c / P4 / P5: minima, micro vias, custom rules, ignored checks — all in the compliance block
    "P3": (frozenset({"design_rule_compliance"}), frozenset()),
    "P5": (frozenset({"design_rule_compliance"}), frozenset({"PM-001", "KO-001"})),
    # via fanout patterns group vias by the courtyard they fall in
    "P6": (frozenset({"placement", "courtyard_overlaps", "diagnostics", "footprints", "vias"}),
           frozenset({"PM-001", "PM-002"})),
    "P7": (frozenset({"footprints", "statistics.smd_count", "statistics.tht_count"}), frozenset({"TE-001", "FD-001"})),
    "P8": (frozenset({"setup", "copper_presence_summary"}), frozenset({"CP-002"})),
    "P8b": (frozenset({"net_lengths", "return_path_continuity"}), frozenset()),
    "P9": (frozenset({"diagnostics"}), frozenset({"PM-002"})),
    "P10": (frozenset({"thermal_pad_vias", "thermal_pad_scan"}), frozenset({"TV-001", "VP-001"})),
    "P11": (frozenset({"connectivity", "connectivity_graph", "statistics.routing_complete",
                       "statistics.unrouted_net_count", "diagnostics"}), frozenset({"RT-001"})),
    "P12": (frozenset({"return_path_continuity"}), frozenset()),
}
FOOTPRINT_FIELDS = frozenset({"courtyard_poly", "courtyard", "type", "board_only", "exclude_from_bom",
                              "exclude_from_pos_files", "exclude_from_pos", "attributes", "pad_properties"})
DIAG_MARKERS = ("courtyard outline is not closed", "does not close", "drawn twice",
                "pads are not checked for a copper path", "copper graph", "connectivity graph")

SCH_BLOCKS = frozenset({"pdn_impedance", "design_analysis.net_classification"})

EMC_RULES = frozenset({"DP-001", "IO-001", "PD-001", "PD-002", "PD-003", "PD-004", "EF-001", "EF-002",
                       "GP-001", "SU-002", "BE-003"})
EMC_BLOCKS = frozenset({"test_plan", "category_summary", "per_net_scores", "regulatory_coverage",
                        "test_plan.interface_risks", "test_plan.probe_points", "power_tree", "pdn"})

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
    out = set()
    for k in (set(a) | set(b)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}:
        x, y = a.get(k), b.get(k)
        if x == y and (k in a) == (k in b):
            continue
        if k in COMPOSITE and isinstance(x, dict) and isinstance(y, dict):
            out |= {f"{k}.{s}" for s in set(x) | set(y) if x.get(s) != y.get(s) or (s in x) != (s in y)}
        else:
            out.add(k)
    return out


def _top(k: str) -> str:
    return k.split(".", 1)[0]


def _covered(sub: str, blocks: frozenset) -> bool:
    return sub in blocks or _top(sub) in blocks


def _diag_records(doc: dict) -> Counter:
    d = doc.get("diagnostics")
    return Counter(_canon(x) for x in d) if isinstance(d, list) else Counter()


def _diag_moves_ok(a: dict, b: dict) -> bool:
    ca, cb = _diag_records(a), _diag_records(b)
    moved = list((ca - cb).elements()) + list((cb - ca).elements())
    return all(any(m in x for m in DIAG_MARKERS) for x in moved)


def _footprint_moves(a: dict, b: dict) -> tuple[Counter, list[str]]:
    stats, bad = Counter(), []
    fa, fb = a.get("footprints") or [], b.get("footprints") or []
    if len(fa) != len(fb):
        return stats, [f"footprint count {len(fa)} -> {len(fb)}"]
    for x, y in zip(fa, fb):
        if x == y or not isinstance(x, dict) or not isinstance(y, dict):
            continue
        for k in set(x) | set(y):
            if x.get(k) != y.get(k):
                if k in FOOTPRINT_FIELDS:
                    stats[f"fp_{k}"] += 1
                else:
                    bad.append(f"footprint {x.get('reference')} {k}")
    return stats, bad[:10]


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


# ---- pcb ------------------------------------------------------------------------------------------

def _pcb(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad = [f"block {k}" for k in subs if _top(k) in FIXED_TOP]
    trig = set()
    moved_rules = {f.get("rule_id") for f in rem + add}
    for cid, (blocks, rules) in PCB_CLASSES.items():
        if any(_covered(s, blocks) for s in subs) or moved_rules & rules:
            trig.add(cid)
    open_blocks, open_rules = set(), set()
    for t in trig:
        open_blocks |= PCB_CLASSES[t][0]
        open_rules |= PCB_CLASSES[t][1]
    bad += [f"block {k}" for k in sorted(subs) if _top(k) not in FIXED_TOP and not _covered(k, frozenset(open_blocks))]
    bad += [f"finding {r}" for r in sorted({f.get('rule_id') for f in rem + add} - open_rules)]
    if "footprints" in subs:
        fstats, fbad = _footprint_moves(a, b)
        stats.update(fstats)
        bad += fbad
    if "diagnostics" in subs and not _diag_moves_ok(a, b):
        bad.append("diagnostics beyond the Part B records")
    return ("+".join(sorted(trig)) if not bad and trig else None), bad or (["pcb movement without a trigger"] if not trig else []), stats


# ---- schematic ------------------------------------------------------------------------------------

def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    bad = [f"block {k}" for k in sorted(subs - SCH_BLOCKS)] + [f"finding {f.get('rule_id')}" for f in rem + add][:10]
    trig = set()
    if "pdn_impedance" in subs:
        trig.add("P14b")
    if "design_analysis.net_classification" in subs:
        trig.add("P16")
    stats = Counter()
    if "P16" in trig:
        na = (a.get("design_analysis") or {}).get("net_classification") or {}
        nb = (b.get("design_analysis") or {}).get("net_classification") or {}
        for n in set(na) | set(nb):
            if na.get(n) != nb.get(n):
                stats[f"P16:{na.get(n)}->{nb.get(n)}"] += 1
    return ("+".join(sorted(trig)) if not bad and trig else None), bad, stats


# ---- emc ------------------------------------------------------------------------------------------

def _emc(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    other_blocks = [k for k in subs if not _covered(k, EMC_BLOCKS)]
    other_rules = sorted({f.get("rule_id") for f in rem + add} - EMC_RULES)
    if not other_blocks and not other_rules:
        return "E", [], stats
    up = _upstream(a, b)
    reasons = []
    if not up:
        reasons.append(f"emc movement outside the Part B rules with identical upstream: "
                       f"{(other_blocks + other_rules)[:6]}")
    for kind, da, db in up:
        if da is None:
            reasons.append(f"upstream {kind} unreadable")
        elif classify_unit(kind, da, db)["label"] is None:
            reasons.append(f"upstream {kind} unexplained")
    return ("E+D" if not reasons else None), reasons, stats


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb, "emc": _emc}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


# ---- upstream (chained analyzers), as in v30x_wave4a ----------------------------------------------

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


def _upstream(a_doc: dict, b_doc: dict) -> list[tuple[str, dict, dict]]:
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


pcb = _labelled(("pcb",))
schematic = _labelled(("schematic",))
emc = _labelled(("emc",))
downstream = _labelled(("thermal", "cross_analysis"))


# ---- adjudication summary -------------------------------------------------------------------------

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
