"""Budget predicates for product 3.0.x Wave 9f (v3.0.1), range 8c42799 -> 246ee5a.

Two schematic fixes; every delta is claimed per UNIT (``classify_unit`` gives a unit one label or a
residual, as in ``v30x_wave9bc``).

Schematic:
  REG    a regulator part with a two-digit suffix below 0.5 V (``LC78_03-05``, ``-02``, ``-00``) no longer
         gets that suffix as its output voltage. Only units holding such a part may move regulator
         findings or the blocks built on rail voltages.
  IB     IB-DET reads ``_B`` / ``_SEC`` as an isolated rail only as a whole name token
         (``ISO|_(?:B|SEC)\\d*(?=[_/]|$)`` on the upper-cased name). An IB-DET finding is removed, or
         its ``isolated_power_rails`` narrows; every dropped rail fails that pattern, every kept one
         matches it.
  Nothing else in a schematic output may move; PCB and Gerber outputs may not move at all.

EMC, thermal and cross_analysis: D only, under a labelled upstream schematic move.

``python -m regression.budgets.v30x_wave9f GATE_DIR UNIT`` classifies one unit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

from regression.budgets.v30x_wave9bc import (
    _derived_ok,
    _moved,
    _rule_stats,
    _same_body,
    _sub_diffs,
    _verdict,
)
from regression.budgets.v30x_wave5 import _upstream_paths

ISOLATED_RAIL = re.compile(r"ISO|_(?:B|SEC)\d*(?=[_/]|$)")
LOW_SUFFIX = re.compile(r"[-_](0[0-4])(?=[^0-9.]|$)")
# Findings and blocks that read a regulator's output voltage.
REG_RULES = frozenset({"PR-DET", "DO-DET", "PS-001", "DC-DET", "RS-001", "PP-001", "VM-001", "RS-DET",
                       "PD-DET", "PP-DET"})
REG_BLOCKS = frozenset({"power_budget", "rail_voltages", "power_sequencing_validation", "power_sequencing",
                        "inrush_analysis", "sleep_current_audit", "pdn_impedance", "missing_info",
                        "design_analysis", "subcircuits", "simulation_readiness", "test_coverage"})


def _low_suffix_parts(doc: dict) -> list[str]:
    return [c.get("reference") for c in doc.get("components") or [] if isinstance(c, dict)
            and any(LOW_SUFFIX.search(str(c.get(k) or "")) for k in ("value", "lib_id", "mpn"))]


def _ib_ok(rem: list, add: list, stats: Counter) -> bool:
    """IB-DET findings only leave, or narrow their isolated rails to the names the new rule keeps."""
    ib_rem = [f for f in rem if f.get("rule_id") == "IB-DET"]
    ib_add = [f for f in add if f.get("rule_id") == "IB-DET"]
    pool = list(ib_rem)
    for f in ib_add:
        rails_b = f.get("isolated_power_rails") or []
        if not all(ISOLATED_RAIL.search(str(r).upper()) for r in rails_b):
            return False
        hit = None
        for i, g in enumerate(pool):
            rails_a = g.get("isolated_power_rails") or []
            dropped = [r for r in rails_a if r not in rails_b]
            if (set(rails_b) <= set(rails_a) and dropped
                    and not any(ISOLATED_RAIL.search(str(r).upper()) for r in dropped)):
                hit = i
                break
        if hit is None:
            return False
        pool.pop(hit)
        stats["IB-DET narrowed"] += 1
    for g in pool:
        if any(ISOLATED_RAIL.search(str(r).upper()) for r in g.get("isolated_power_rails") or []):
            return False
        stats["IB-DET removed"] += 1
    return True


def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    if any(f.get("rule_id") == "IB-DET" for f in rem + add):
        if _ib_ok(rem, add, stats):
            trig.add("IB")
        else:
            bad.append("IB-DET beyond removals / narrowing by the whole-token rule")
    other = [f for f in rem + add if f.get("rule_id") != "IB-DET"]
    low = _low_suffix_parts(b)
    if other or subs:
        if not low:
            bad.append("regulator or block movement without a part with a two-digit suffix below 0.5 V")
        else:
            trig.add("REG")
            stats["low-suffix units"] += 1
            if {f.get("rule_id") for f in other} - REG_RULES:
                bad.append(f"rules beyond the regulator readers: {sorted({str(f.get('rule_id')) for f in other} - REG_RULES)}")
            bad += [f"block {k}" for k in sorted(subs - REG_BLOCKS)]
    return _verdict(trig, bad, stats, "schematic")


_UP: OrderedDict = OrderedDict()


def _upstream_label(a: dict, b: dict, kind: str):
    pa, pb = _upstream_paths(a, b, kind)
    if not pa or not pb:
        return None
    hit = _UP.get((pa, pb))
    if hit is None:
        try:
            da = json.loads(Path(pa).read_text(encoding="utf-8"))
            db = json.loads(Path(pb).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            hit = (True, None)
        else:
            hit = (False, None) if _same_body(da, db) else (True, classify_unit(kind, da, db)["label"])
        _UP[(pa, pb)] = hit
        while len(_UP) > 64:
            _UP.popitem(last=False)
    return hit


def _downstream(analyzer: str, a: dict, b: dict) -> dict:
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    for kind in ("schematic", "pcb"):
        up = _upstream_label(a, b, kind)
        if up is None or not up[0]:
            continue
        if up[1] is None:
            return {"label": None, "reasons": [f"upstream {kind} unexplained"], "stats": stats}
        return {"label": "D", "reasons": [], "stats": stats}
    return {"label": None, "reasons": [f"{analyzer} movement without an upstream move"], "stats": stats}


_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    if analyzer == "schematic":
        label, reasons, stats = _schematic(a_doc, b_doc)
        r = {"label": label, "reasons": reasons, "stats": stats}
    elif analyzer in ("emc", "thermal", "cross_analysis"):
        r = _downstream(analyzer, a_doc, b_doc)
    else:
        return {"label": None, "reasons": [f"{analyzer} may not move in Wave 9f"], "stats": Counter()}
    reasons = list(r["reasons"])
    full = analyzer in _FULL_DERIVED
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
downstream = _labelled(("emc", "thermal", "cross_analysis"))


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
