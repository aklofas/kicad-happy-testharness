"""Budget predicates for product 3.0.x Waves 8c + 8b (v3.0.1), range 647bc85 -> 0efc012
(8c = 647bc85..a565254, corpus-neutral; 8b = a565254..0efc012, output-changing).

Classes (8b handoff "Corpus classes to budget"; files ``v30x-wave8b{,-full-chain}.json``). Every delta
is claimed per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined set of classes
whose blocks or rules moved) and every delta of that unit is explained, or the unit is a residual
(label ``None``).

Schematic:
  KH800  equal-rank net names tie-break as KiCad, child sheets read in sheet-uuid order. Connectivity
         does not change: the multiset of nets keyed by their pins and labels (names ignored), the
         components without ``pin_nets``, and the raw label / power-symbol / no-connect / text lists
         must be equal as multisets on both sides. The unit is KH800 when a net name changed or the
         component / label order changed; then name- and order-derived blocks and findings may move
         (``KH800_STATS`` records the finding movement left after net names are replaced by pin-set
         tokens and lists are sorted).
  KH850  a ``/``-joined impedance value (``600R/200mA``) loses ``parsed_value``; LC-DET findings built
         on it are removed. Without KH800 in the same unit nothing else may move.

PCB:
  KH851  ``setup.board_thickness_mm`` added where the baseline had no ``setup`` thickness.
  KH825  the plain-mode routing note leaves ``diagnostics`` (``pads are not checked for a copper path``).
  KH863  OR-001 findings only removed (buckets merge).
  KH820  (``--full``) ``net_lengths[].trace_segments[].impedance_ohm`` rises x1.0-1.3 on outer copper,
         inner layers unchanged.
  KH795  (``--full``) ``reference_plane_changes`` appears where ``return_path_continuity`` is present.

EMC: GP-001 "Signal crosses a split between reference planes" added (KH795, with its upstream PCB
carrying a non-empty ``reference_plane_changes``); ``category_summary`` / ``regulatory_coverage`` /
``per_net_scores`` / ``test_plan`` follow. Anything else needs an explained upstream schematic move (D).
Thermal and cross_analysis: D only, from an explained upstream schematic move, or identical bodies.

``python -m regression.budgets.v30x_wave8b GATE_DIR UNIT`` classifies one unit.
"""
from __future__ import annotations

import argparse
import hashlib
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
from regression.budgets.v30x_wave5 import _upstream_doc_pair

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})
FIXED_TOP = frozenset({"analyzer_type", "schema_version", "kicad_version", "file_version", "compat"})

# Schematic blocks holding raw drawing text (label names are not net references).
SCH_RAW = ("labels", "power_symbols", "no_connects", "text_annotations")
SCH_INVARIANT = frozenset(SCH_RAW) | {"nets", "components"}

ROUTING_NOTE = "pads are not checked for a copper path"
SPLIT_TITLE = "Signal crosses a split between reference planes"
EMC_FOLLOW = frozenset({"category_summary", "regulatory_coverage", "per_net_scores", "test_plan"})
OUTER = re.compile(r"^[FB]\.Cu$")
IMPEDANCE_MAX_RATIO = 1.3


def _canon(f: Any) -> str:
    g = dict(f) if isinstance(f, dict) else {"_": f}
    g.pop("finding_id", None)
    return json.dumps(g, sort_keys=True, default=str)


def _moved(a: dict, b: dict) -> tuple[list, list]:
    ca = Counter(_canon(f) for f in _findings(a))
    cb = Counter(_canon(f) for f in _findings(b))
    return [json.loads(k) for k in (ca - cb).elements()], [json.loads(k) for k in (cb - ca).elements()]


def _same_body(a: dict, b: dict) -> bool:
    return ({k: v for k, v in a.items() if k not in VOLATILE_TOP}
            == {k: v for k, v in b.items() if k not in VOLATILE_TOP})


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


def _key(x: Any) -> str:
    return json.dumps(x, sort_keys=True, default=str)


def _unsheeted(x: Any) -> Any:
    """``x`` without ``_sheet`` indices, which follow the sheet read order (KH-800)."""
    if isinstance(x, dict):
        return {k: _unsheeted(v) for k, v in x.items() if k != "_sheet"}
    if isinstance(x, list):
        return [_unsheeted(v) for v in x]
    return x


def _skey(x: Any) -> str:
    return _key(_unsheeted(x))


def _sorted_deep(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _sorted_deep(v) for k, v in x.items()}
    if isinstance(x, list):
        return sorted((_sorted_deep(v) for v in x), key=_key)
    return x


# ---- schematic ------------------------------------------------------------------------------------

def _pins(net: dict) -> tuple:
    return tuple(sorted(f"{p.get('component')}.{p.get('pin_number')}" for p in net.get("pins") or []
                        if isinstance(p, dict)))


def _net_structure(doc: dict) -> Counter:
    nets = doc.get("nets") if isinstance(doc.get("nets"), dict) else {}
    return Counter(_key(_sorted_deep(_unsheeted({k: v for k, v in n.items() if k not in ("name", "display_name")})))
                   for n in nets.values() if isinstance(n, dict))


def _net_tokens(doc: dict) -> dict[str, str]:
    nets = doc.get("nets") if isinstance(doc.get("nets"), dict) else {}
    return {k: "N:" + hashlib.sha1("|".join(_pins(v)).encode()).hexdigest()[:12]
            for k, v in nets.items() if isinstance(v, dict)}


def _kh850_value(value: Any) -> bool:
    return isinstance(value, str) and "/" in value


def _components(a: dict, b: dict) -> tuple[bool, int]:
    """(components equal as a multiset modulo pin_nets and the KH-850 parsed_value drop, drops).

    A ``/``-joined value may lose ``parsed_value``; it may not gain or change one."""
    def body(c):
        return _skey({k: v for k, v in c.items() if k != "pin_nets"
                      and not (k == "parsed_value" and _kh850_value(c.get("value")))})

    def parsed(cs):
        return Counter(_key((c.get("reference"), c.get("value"), c["parsed_value"])) for c in cs
                       if isinstance(c, dict) and "parsed_value" in c and _kh850_value(c.get("value")))

    ca, cb = a.get("components") or [], b.get("components") or []
    if Counter(body(c) if isinstance(c, dict) else _key(c) for c in ca) != \
            Counter(body(c) if isinstance(c, dict) else _key(c) for c in cb):
        return False, 0
    pa, pb = parsed(ca), parsed(cb)
    if pb - pa:
        return False, 0
    return True, sum((pa - pb).values())


def _order(doc: dict) -> tuple:
    return (tuple(c.get("reference") for c in doc.get("components") or [] if isinstance(c, dict)),
            tuple(l.get("name") for l in doc.get("labels") or [] if isinstance(l, dict)))


def _tok_canon(x: Any, m: dict, rx) -> Any:
    if isinstance(x, dict):
        return {_tok_canon(k, m, rx): _tok_canon(v, m, rx) for k, v in x.items()
                if k not in ("finding_id", "_sheet", "detection_id")}
    if isinstance(x, list):
        return sorted((_tok_canon(v, m, rx) for v in x), key=_key)
    if isinstance(x, str):
        if x in m:
            return m[x]
        if rx is not None:
            return rx.sub(lambda g: m[g.group(0)], x)
    return x


def _token_rx(m: dict):
    names = sorted((k for k in m if len(k) >= 2), key=len, reverse=True)
    if not names:
        return None
    return re.compile("|".join(r"(?<![A-Za-z0-9_])" + re.escape(k) + r"(?![A-Za-z0-9_])" for k in names))


def _kh800_left(a: dict, b: dict) -> Counter:
    """Finding movement left after net names become pin-set tokens and every list is sorted."""
    ta, tb = _net_tokens(a), _net_tokens(b)
    diff = {k for k in set(ta) | set(tb) if ta.get(k) != tb.get(k)}
    ma = {k: v for k, v in ta.items() if k in diff}
    mb = {k: v for k, v in tb.items() if k in diff}
    ra, rb = _token_rx(ma), _token_rx(mb)
    fa = Counter(_key(_tok_canon(f, ma, ra)) for f in _findings(a))
    fb = Counter(_key(_tok_canon(f, mb, rb)) for f in _findings(b))
    out = Counter()
    for s in (fa - fb).elements():
        out[f"{json.loads(s).get('rule_id')}-"] += 1
    for s in (fb - fa).elements():
        out[f"{json.loads(s).get('rule_id')}+"] += 1
    return out


def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad = [f"block {k}" for k in sorted(subs & FIXED_TOP)]
    if _net_structure(a) != _net_structure(b):
        bad.append("connectivity changed (nets by pins and labels)")
    for k in SCH_RAW:
        if Counter(_skey(x) for x in a.get(k) or []) != Counter(_skey(x) for x in b.get(k) or []):
            bad.append(f"raw list {k} changed")
    comps_ok, drops = _components(a, b)
    if not comps_ok:
        bad.append("components changed beyond pin_nets / KH-850 parsed_value")
    renamed = set(a.get("nets") or {}) != set(b.get("nets") or {})
    reordered = _order(a) != _order(b)
    trig = set()
    if drops:
        trig.add("KH850")
        stats["parsed_value dropped"] += drops
    if renamed or reordered:
        trig.add("KH800")
        stats["renamed" if renamed else "reordered"] += 1
        if rem or add:
            left = _kh800_left(a, b)
            stats.update(Counter({f"left {k}": v for k, v in left.items()}))
    else:
        others = sorted(subs - SCH_INVARIANT - FIXED_TOP)
        bad += [f"block {k} without a KH-800 rename or reorder" for k in others]
        if any(f.get("rule_id") != "LC-DET" for f in rem) or add:
            bad.append("findings beyond LC-DET removals without a KH-800 rename or reorder")
        elif rem:
            trig.add("KH850")
    if bad:
        return None, bad, stats
    return ("+".join(sorted(trig)) if trig else None), ([] if trig else ["schematic movement without a trigger"]), stats


# ---- pcb ------------------------------------------------------------------------------------------

def _setup_ok(a: dict, b: dict) -> bool:
    sa, sb = a.get("setup"), b.get("setup")
    sa = sa if isinstance(sa, dict) else {}
    if not isinstance(sb, dict) or "board_thickness_mm" in sa or "board_thickness_mm" not in sb:
        return False
    return {k: v for k, v in sb.items() if k != "board_thickness_mm"} == sa


def _diagnostics_ok(a: dict, b: dict) -> bool:
    da, db = list(a.get("diagnostics") or []), list(b.get("diagnostics") or [])
    gone = [d for d in da if d not in db]
    return (len(da) - len(db) == len(gone) and all(d in da for d in db) and gone
            and all(ROUTING_NOTE in json.dumps(d) for d in gone))


def _impedance_ok(a: dict, b: dict, stats: Counter) -> bool:
    la, lb = a.get("net_lengths"), b.get("net_lengths")
    if not isinstance(la, list) or not isinstance(lb, list) or len(la) != len(lb):
        return False
    for x, y in zip(la, lb):
        if x == y:
            continue
        if not isinstance(x, dict) or not isinstance(y, dict):
            return False
        if {k: v for k, v in x.items() if k != "trace_segments"} != {k: v for k, v in y.items() if k != "trace_segments"}:
            return False
        sa, sb = x.get("trace_segments") or [], y.get("trace_segments") or []
        if len(sa) != len(sb):
            return False
        for s, t in zip(sa, sb):
            if s == t:
                continue
            if {k: v for k, v in s.items() if k != "impedance_ohm"} != {k: v for k, v in t.items() if k != "impedance_ohm"}:
                return False
            za, zb = s.get("impedance_ohm"), t.get("impedance_ohm")
            if not isinstance(za, (int, float)) or not isinstance(zb, (int, float)) or za <= 0:
                return False
            if not OUTER.match(str(s.get("layer", ""))) or not 1.0 <= zb / za <= IMPEDANCE_MAX_RATIO:
                return False
            stats["impedance outer up"] += 1
    return True


def _pcb(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    if "setup" in subs:
        if _setup_ok(a, b):
            trig.add("KH851")
        else:
            bad.append("setup beyond the added board_thickness_mm")
    if "diagnostics" in subs:
        if _diagnostics_ok(a, b):
            trig.add("KH825")
        else:
            bad.append("diagnostics beyond the removed routing note")
    if "net_lengths" in subs:
        if _impedance_ok(a, b, stats):
            trig.add("KH820")
        else:
            bad.append("net_lengths beyond outer-layer impedance_ohm rising")
    if "reference_plane_changes" in subs:
        if ("reference_plane_changes" not in a and isinstance(b.get("reference_plane_changes"), list)
                and "return_path_continuity" in b):
            trig.add("KH795")
            if b["reference_plane_changes"]:
                stats["reference_plane_changes non-empty"] += 1
        else:
            bad.append("reference_plane_changes beyond the added key")
    bad += [f"block {k}" for k in sorted(subs - {"setup", "diagnostics", "net_lengths", "reference_plane_changes"})]
    if add or any(f.get("rule_id") != "OR-001" for f in rem):
        bad.append("findings beyond OR-001 removals")
    elif rem:
        trig.add("KH863")
    if bad:
        return None, bad, stats
    return ("+".join(sorted(trig)) if trig else None), ([] if trig else ["pcb movement without a trigger"]), stats


# ---- emc ------------------------------------------------------------------------------------------

def _emc(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    split = [f for f in add if f.get("rule_id") == "GP-001" and f.get("summary") == SPLIT_TITLE]
    reasons, trig = [], set()
    if split:
        stats["GP-001 split+"] += len(split)
        up = _upstream_doc_pair(a, b, "pcb")
        if up is None or not up[1].get("reference_plane_changes"):
            reasons.append("GP-001 split finding without upstream reference_plane_changes")
        else:
            trig.add("KH795")
    rest = rem or [f for f in add if f not in split] or (subs - EMC_FOLLOW)
    if rest or not split:
        # name-derived movement (findings, finding_id, per-net scores) needs an explained upstream rename
        up = _upstream_doc_pair(a, b, "schematic")
        if up is None or _same_body(*up):
            reasons.append("emc movement outside KH-795 without an upstream schematic move")
        elif classify_unit("schematic", up[0], up[1])["label"] is None:
            reasons.append("emc movement outside KH-795 with an unexplained upstream schematic")
        else:
            trig.add("D")
    return ("+".join(sorted(trig)) if not reasons else None), reasons, stats


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb, "emc": _emc}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


def _downstream(analyzer: str, a: dict, b: dict) -> dict:
    up = _upstream_doc_pair(a, b, "schematic")
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    if up is None or _same_body(*up):
        return {"label": None, "reasons": [f"{analyzer} movement without an upstream schematic move"], "stats": stats}
    if classify_unit("schematic", up[0], up[1])["label"] is None:
        return {"label": None, "reasons": ["upstream schematic unexplained"], "stats": stats}
    return {"label": "D", "reasons": [], "stats": stats}


def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    if analyzer in ("thermal", "cross_analysis"):
        r = _downstream(analyzer, a_doc, b_doc)
    else:
        clf = _CLASSIFIERS.get(analyzer)
        if clf is None:
            return {"label": None, "reasons": [f"no class for analyzer {analyzer}"], "stats": Counter()}
        label, reasons, stats = clf(a_doc, b_doc)
        r = {"label": label, "reasons": reasons, "stats": stats}
    full = analyzer in _FULL_DERIVED
    reasons = list(r["reasons"])
    if not _derived_ok(a_doc, full=full):
        reasons.append("a: derived blocks not from findings")
    if not _derived_ok(b_doc, full=full):
        reasons.append("b: derived blocks not from findings")
    return {"label": r["label"] if not reasons else None, "reasons": reasons, "stats": r["stats"]}


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
