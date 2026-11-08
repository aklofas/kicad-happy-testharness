"""Per-unit movement features for the Wave 11b-1 gate (census + input to the budget judge).

For every unit that moves under compare_strict (volatile-leaves-v1) it records, as one JSON line:
  tops        top-level keys that differ (volatile inputs/capability_mode_ref/elapsed_s ignored)
  sub         for dict blocks: the second-level keys that differ
  gpaths      generalized strict-delta paths (/findings/N/summary) with op -> count (capped)
  rules       rule_id -> [removed, added] over findings paired by content (finding_id ignored)
  id_only     rule_id -> count of findings whose content pairs but whose finding_id changed
  comp        component field -> count of changed values (paired by index when refs line up)
  comp_types  'old->new' component type transitions
  nets        {"names_equal", "groups_equal", "fields_ok"} (groups = pin multisets, names ignored)
  diag        [len a, len b] of diagnostics
  derived_ok  [a, b] summary/trust/audience recompute from findings
  upstream    analyzer -> unit id of the upstream artefact read (chained units)

Usage: python regression/budgets/v302_wave11b1_features.py GATE_DIR ANALYZER OUT.jsonl [--jobs N]
"""
import argparse
import json
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

H = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(H))

from regression.field_compare import compare_strict, load_policy  # noqa: E402
from regression.budgets.v232_backport import (  # noqa: E402
    expected_audience_summary, expected_summary, expected_trust_summary,
)

VOLATILE_TOP = {"inputs", "capability_mode_ref", "elapsed_s"}
FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}
_POL = None
_ROOTS = None


def _findings(d):
    f = d.get("findings")
    return [x for x in f if isinstance(x, dict)] if isinstance(f, list) else []


def _canon(f):
    g = {k: v for k, v in f.items() if k != "finding_id"}
    return json.dumps(g, sort_keys=True, default=str)


def _rules(a, b):
    fa, fb = _findings(a), _findings(b)
    ca = Counter(_canon(f) for f in fa)
    cb = Counter(_canon(f) for f in fb)
    rem, add = ca - cb, cb - ca
    out = {}
    for k, n in rem.items():
        r = str(json.loads(k).get("rule_id"))
        out.setdefault(r, [0, 0])[0] += n
    for k, n in add.items():
        r = str(json.loads(k).get("rule_id"))
        out.setdefault(r, [0, 0])[1] += n
    # finding_id-only changes among content-paired findings
    ida, idb = {}, {}
    for f in fa:
        ida.setdefault(_canon(f), []).append(f.get("finding_id"))
    for f in fb:
        idb.setdefault(_canon(f), []).append(f.get("finding_id"))
    id_only = Counter()
    for k in set(ida) & set(idb):
        if sorted(map(str, ida[k])) != sorted(map(str, idb[k])):
            r = str(json.loads(k).get("rule_id"))
            id_only[r] += len(set(map(str, ida[k])) ^ set(map(str, idb[k]))) // 2 or 1
    ex_rem = [json.loads(k) for k in list(rem)[:4]]
    ex_add = [json.loads(k) for k in list(add)[:4]]
    return out, dict(id_only), ex_rem, ex_add


def _derived_ok(doc, analyzer):
    fs = _findings(doc)
    if analyzer in FULL_DERIVED and isinstance(doc.get("summary"), dict) \
            and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


def _comp(a, b):
    ca = [c for c in a.get("components") or [] if isinstance(c, dict)]
    cb = [c for c in b.get("components") or [] if isinstance(c, dict)]
    fields, types = Counter(), Counter()
    if [c.get("reference") for c in ca] != [c.get("reference") for c in cb]:
        fields["__refs_differ__"] += 1
        ia = {}
        for c in ca:
            ia.setdefault(c.get("reference"), []).append(c)
        ib = {}
        for c in cb:
            ib.setdefault(c.get("reference"), []).append(c)
        fields["__refs_added__"] = len(set(ib) - set(ia))
        fields["__refs_removed__"] = len(set(ia) - set(ib))
        pairs = [(ia[r][0], ib[r][0]) for r in set(ia) & set(ib)]
    else:
        pairs = list(zip(ca, cb))
    for x, y in pairs:
        if x == y:
            continue
        for k in set(x) | set(y):
            if x.get(k) != y.get(k) or (k in x) != (k in y):
                fields[k] += 1
        if x.get("type") != y.get("type"):
            types[f"{x.get('type')}->{y.get('type')}"] += 1
    return dict(fields), dict(types)


def _groups(d):
    out = Counter()
    for n in (d.get("nets") or {}).values():
        if not isinstance(n, dict):
            continue
        ps = n.get("pins") or []
        key = tuple(sorted(Counter((p.get("component"), p.get("pin_number"), p.get("pin_type"))
                                   for p in ps if isinstance(p, dict)).items()))
        if key:
            out[key] += 1
    return out


def _nets(a, b):
    na, nb = a.get("nets") or {}, b.get("nets") or {}
    if na == nb:
        return None
    names = set(na) == set(nb)
    groups = _groups(a) == _groups(b)
    skip = ("pins", "no_connect", "point_count")
    fields_ok = all({k: v for k, v in na[n].items() if k not in skip} == {k: v for k, v in nb[n].items() if k not in skip}
                    for n in set(na) & set(nb) if isinstance(na.get(n), dict) and isinstance(nb.get(n), dict))
    renamed = len(set(na) ^ set(nb))
    return {"names_equal": names, "groups_equal": groups, "fields_ok": fields_ok, "name_sym_diff": renamed,
            "count": [len(na), len(nb)]}


def _labels(a, b):
    la, lb = a.get("labels") or [], b.get("labels") or []
    if la == lb:
        return None
    if len(la) != len(lb):
        return {"__len__": [len(la), len(lb)]}
    out = Counter()
    for x, y in zip(la, lb):
        if isinstance(x, dict) and isinstance(y, dict) and x != y:
            for k in set(x) | set(y):
                if x.get(k) != y.get(k):
                    out[k] += 1
    return dict(out)


def _root_hier(doc):
    """Root-sheet hierarchical labels whose name is also a global label or power net elsewhere (KH-671)."""
    labs = [l for l in doc.get("labels") or [] if isinstance(l, dict)]
    root = {l.get("name") for l in labs if l.get("type") == "hierarchical_label" and l.get("_sheet") in (0, None)}
    glob = {l.get("name") for l in labs if l.get("type") == "global_label"}
    glob |= {p.get("net_name") for p in doc.get("power_symbols") or [] if isinstance(p, dict) and p.get("_sheet") not in (0, None)}
    return sorted(str(x) for x in root & glob)[:10]


def _gen(path):
    return re.sub(r"/\d+(?=/|$)", "/N", path)


def _unit_of(path, slot_root):
    if not path:
        return None
    s = str(path)
    for r in slot_root:
        if s.startswith(r + "/"):
            rel = s[len(r) + 1:]
            return rel[:-len("/snap.json")] if rel.endswith("/snap.json") else rel
    return s


def _one(task):
    global _POL
    if _POL is None:
        _POL = load_policy("volatile-leaves-v1")
    unit, pa, pb, roots = task
    an = unit.split("/", 1)[0]
    try:
        a = json.loads(Path(pa).read_text(encoding="utf-8"))
        b = json.loads(Path(pb).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"unit": unit, "error": str(e)[:200]}
    ds, viol = compare_strict(a, b, _POL, unit=unit, analyzer=an, root_prefixes=roots)
    if not ds and not viol:
        return None
    gp = Counter()
    for d in ds:
        gp[f"{_gen(d.path)}|{d.op}"] += 1
    tops = sorted(k for k in set(a) | set(b) if k not in VOLATILE_TOP and (a.get(k) != b.get(k) or (k in a) != (k in b)))
    sub = {}
    for k in tops:
        x, y = a.get(k), b.get(k)
        if isinstance(x, dict) and isinstance(y, dict):
            sub[k] = sorted(s for s in set(x) | set(y) if x.get(s) != y.get(s) or (s in x) != (s in y))[:40]
    rules, id_only, ex_rem, ex_add = _rules(a, b)
    rec = {"unit": unit, "an": an, "n": len(ds), "viol": viol[:3], "tops": tops, "sub": sub,
           "gpaths": dict(gp.most_common(150)), "rules": rules, "id_only": id_only,
           "ex_rem": ex_rem, "ex_add": ex_add,
           "diag": [len(a.get("diagnostics") or []), len(b.get("diagnostics") or [])],
           "derived_ok": [_derived_ok(a, an), _derived_ok(b, an)]}
    if an == "schematic":
        rec["comp"], rec["comp_types"] = _comp(a, b)
        rec["nets"] = _nets(a, b)
        rec["labels"] = _labels(a, b)
        rec["root_hier"] = _root_hier(a) or _root_hier(b)
    ua = ((a.get("inputs") or {}).get("upstream_artifacts") or {})
    ub = ((b.get("inputs") or {}).get("upstream_artifacts") or {})
    up = {}
    for k in set(ua) | set(ub):
        up[k] = [_unit_of((ua.get(k) or {}).get("path"), roots[0]), _unit_of((ub.get(k) or {}).get("path"), roots[1])]
    if up:
        rec["upstream"] = up
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gate", type=Path)
    ap.add_argument("analyzer")
    ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    g = args.gate.resolve()
    ra = (str(g / "baseline"), str(args.gate / "baseline"))
    rb = (str(g / "candidate"), str(args.gate / "candidate"))
    tasks = []
    for pb in sorted((g / "candidate" / args.analyzer).rglob("snap.json")):
        rel = pb.parent.relative_to(g / "candidate").as_posix()
        pa = g / "baseline" / rel / "snap.json"
        if pa.exists():
            tasks.append((rel, str(pa), str(pb), (ra, rb)))
    n = moved = 0
    with open(args.out, "w", encoding="utf-8") as fo, ProcessPoolExecutor(args.jobs) as ex:
        for r in ex.map(_one, tasks, chunksize=16):
            n += 1
            if r is None:
                continue
            moved += 1
            fo.write(json.dumps(r, default=str) + "\n")
    print(f"{args.analyzer}: {n} paired units, {moved} moved -> {args.out}")


if __name__ == "__main__":
    main()
