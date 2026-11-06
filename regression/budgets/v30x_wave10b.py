"""Budget predicates for product 3.0.x Wave 10b (v3.0.1), range e60d03b5 -> 2abc8496.

Every delta is claimed per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined
set of classes that moved it) or None (a residual). Per-class magnitudes are tallied in ``stats``
and compared with the handoff by hand.

Schematic:
  RV    ``rail_voltages`` entries only leave (pin-only supplies, ground-output regulators); a ground
        net's entry may read 0.
  SEQ   ``power_sequencing`` EN sources only go always_on -> tied_to_ground (+ observations);
        ``power_sequencing_validation.power_tree`` enable_type tied_to_rail -> tied_to_ground /
        always_on, sequence_order may drop and entries re-sort.
  LDO   ``power_budget`` moves only in ``ldo_dissipation`` (negative LDO dropout by magnitude).
  DER   PR-DET / DC-DET gain derating fields in place (negative rails).
  REG   a regulator whose output pin is on ground: output_rail -> null, DO-DET follows,
        ``net_classifications`` drops the ground net's power_rail entry.
PCB:
  PM    PM-001 findings only (per courtyard layer); ``dfm_summary`` only the IPC detection_source.
Gerber: the six named directories only (drill not Excellon, comment not an operation, BOM .txt).
EMC:
  STAGE SU- / PD-00x / EE- findings carry stages ['layout'].
  CKDP  CK-001 / DP-004 by length share; PD-001 removed on negative rails or (full-chain)
        transient_source power_budget -> output_cap_proxy; RP-001 added, VS-001 added / removed.
Thermal: TH-DET added for the negative switcher (one unit).
Cross: RP-002 removed or confidence -> heuristic, PS-002 confidence -> heuristic, checks_run.

``python -m regression.budgets.v30x_wave10b GATE_DIR UNIT`` classifies one unit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

from regression.budgets.v30x_wave2 import _findings
from regression.budgets.v30x_wave9bc import _derived_ok, _moved, _rule_stats, _sub_diffs, _verdict

GROUND = re.compile(r"(?:^|/)(?:A|D|P|S|E|C)?GND\w*$|(?:^|/)VSS\w*$|(?:^|/)0V\w*$", re.I)


def _strip(xs: Any, keys: tuple) -> list:
    return [json.dumps({k: v for k, v in x.items() if k not in keys} if isinstance(x, dict) else x,
                       sort_keys=True, default=str) for x in xs or []]


# ---- schematic ------------------------------------------------------------------------------------

SCH_RAW = ("labels", "power_symbols", "no_connects", "text_annotations", "components", "nets", "statistics")
SCH_BLOCKS = frozenset({"rail_voltages", "power_sequencing", "power_sequencing_validation", "power_budget",
                        "net_classifications"})
SCH_INPLACE = frozenset({"PR-DET", "DC-DET", "DO-DET"})


def _rails_ok(a: dict, b: dict, stats: Counter) -> bool:
    ra, rb = a.get("rail_voltages") or {}, b.get("rail_voltages") or {}
    if set(rb) - set(ra):
        return False
    for n in set(rb):
        if ra[n] != rb[n] and not (GROUND.search(str(n)) and rb[n] == 0):
            return False
    stats["rail_voltages removed"] += len(set(ra) - set(rb))
    stats["rail_voltages ground -> 0"] += sum(1 for n in rb if ra[n] != rb[n])
    return True


def _seq_ok(a: dict, b: dict, stats: Counter) -> bool:
    pa, pb = a.get("power_sequencing") or {}, b.get("power_sequencing") or {}
    if {k for k in set(pa) | set(pb) if pa.get(k) != pb.get(k)} - {"dependencies", "observations"}:
        return False
    da, db = pa.get("dependencies") or [], pb.get("dependencies") or []
    if len(da) != len(db):
        return False
    for x, y in zip(da, db):
        if x == y:
            continue
        if {k for k in set(x) | set(y) if x.get(k) != y.get(k)} != {"en_source"}:
            return False
        if (x.get("en_source"), y.get("en_source")) != ("always_on", "tied_to_ground"):
            return False
        stats["en_source -> tied_to_ground"] += 1
    return True


def _psv_ok(a: dict, b: dict, stats: Counter) -> bool:
    va, vb = a.get("power_sequencing_validation") or {}, b.get("power_sequencing_validation") or {}
    if {k for k in set(va) | set(vb) if va.get(k) != vb.get(k)} - {"power_tree"}:
        return False
    ta, tb = va.get("power_tree") or [], vb.get("power_tree") or []
    drop = ("enable_type", "sequence_order", "rail")
    if Counter(_strip(ta, drop)) != Counter(_strip(tb, drop)):
        return False
    key = lambda e: json.dumps({k: v for k, v in e.items() if k not in drop}, sort_keys=True, default=str)  # noqa: E731
    ia = {}
    for e in ta:
        ia.setdefault(key(e), []).append(e)
    for e in tb:
        x = ia[key(e)].pop(0)
        if x == e:
            continue
        ea, eb = x.get("enable_type"), e.get("enable_type")
        if ea == eb and {k for k in set(x) | set(e) if x.get(k) != e.get(k)} == {"rail"} \
                and GROUND.search(str(x.get("rail"))) and e.get("rail") is None:
            stats["power_tree ground rail -> null"] += 1
            continue
        if ea == eb:
            stats["power_tree re-sort"] += 1
            continue
        if ea != "tied_to_rail" or eb not in ("tied_to_ground", "always_on"):
            return False
        if eb == "always_on" and e.get("sequence_order") != x.get("sequence_order"):
            return False
        stats[f"power_tree -> {eb}"] += 1
    return True


def _budget_ok(a: dict, b: dict, stats: Counter) -> bool:
    ba, bb = a.get("power_budget") or {}, b.get("power_budget") or {}
    if {k for k in set(ba) | set(bb) if ba.get(k) != bb.get(k)} - {"rails"}:
        return False
    ra, rb = ba.get("rails") or {}, bb.get("rails") or {}
    if set(ra) != set(rb):
        return False
    for n in ra:
        x, y = ra[n], rb[n]
        if x == y:
            continue
        if {k for k in set(x) | set(y) if x.get(k) != y.get(k)} != {"ldo_dissipation"}:
            return False
        lx, ly = x["ldo_dissipation"], y["ldo_dissipation"]
        if not isinstance(lx, dict) or not isinstance(ly, dict) or set(lx) != set(ly):
            return False
        if any(lx[k] != ly[k] and not re.search(r"dropout|power", k) for k in lx):
            return False
        stats["ldo_dissipation rails"] += 1
    return True


def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    for k in SCH_RAW:
        if a.get(k) != b.get(k):
            bad.append(f"{k} changed")
    bad += [f"block {k}" for k in sorted(subs - SCH_BLOCKS - set(SCH_RAW))]
    if "rail_voltages" in subs:
        (trig.add("RV") if _rails_ok(a, b, stats) else bad.append("rail_voltages beyond removals / ground -> 0"))
    if subs & {"power_sequencing"}:
        (trig.add("SEQ") if _seq_ok(a, b, stats) else bad.append("power_sequencing beyond EN -> tied_to_ground"))
    if "power_sequencing_validation" in subs:
        (trig.add("SEQ") if _psv_ok(a, b, stats) else bad.append("power_tree beyond enable_type / sequence_order"))
    if "power_budget" in subs:
        (trig.add("LDO") if _budget_ok(a, b, stats) else bad.append("power_budget beyond ldo_dissipation"))
    reg = False
    if "net_classifications" in subs:
        na, nb = a.get("net_classifications") or {}, b.get("net_classifications") or {}
        if set(nb) - set(na) or any(na[n] != nb[n] for n in nb) or not all(GROUND.search(str(n)) for n in set(na) - set(nb)):
            bad.append("net_classifications beyond ground nets leaving")
        else:
            reg = True
    rules = {f.get("rule_id") for f in rem + add}
    if rules - SCH_INPLACE:
        bad.append(f"findings outside PR-DET / DC-DET / DO-DET: {sorted(map(str, rules - SCH_INPLACE))}")
    counts = Counter(f.get("rule_id") for f in add)
    counts.subtract(Counter(f.get("rule_id") for f in rem))
    if any(n for r, n in counts.items() if r != "DO-DET") or counts.get("DO-DET", 0) > 0:
        bad.append("finding counts move beyond DO-DET removals")
    gnd_out = any(f.get("rule_id") == "PR-DET" and f.get("output_rail") and GROUND.search(str(f["output_rail"]))
                  for f in rem) and any(f.get("rule_id") == "PR-DET" and f.get("output_rail") is None for f in add)
    if counts.get("DO-DET", 0) < 0 and not gnd_out:
        bad.append("DO-DET removed without a ground-output regulator")
    if gnd_out or reg:
        trig.add("REG")
    elif rules:
        trig.add("DER")
        for f in add:
            for k in ("capacitors", "output_capacitors"):
                stats["derated caps"] += sum(1 for c in f.get(k) or [] if isinstance(c, dict) and "derating_factor" in c)
    return _verdict(trig, bad, stats, "schematic")


# ---- pcb ------------------------------------------------------------------------------------------

def _pcb(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    stats = Counter()
    bad, trig = [], set()
    fa = [f for f in _findings(a) if f.get("rule_id") == "PM-001"]
    fb = [f for f in _findings(b) if f.get("rule_id") == "PM-001"]
    if Counter(_strip([f for f in _findings(a) if f.get("rule_id") != "PM-001"], ("finding_id",))) != \
            Counter(_strip([f for f in _findings(b) if f.get("rule_id") != "PM-001"], ("finding_id",))):
        bad.append("findings beyond PM-001")
    if Counter(_strip(fa, ("finding_id",))) != Counter(_strip(fb, ("finding_id",))):
        trig.add("PM")
        ca, cb = Counter(_strip(fa, ("finding_id",))), Counter(_strip(fb, ("finding_id",)))
        stats["PM-001 removed"] += sum((ca - cb).values())
        stats["PM-001 added"] += sum((cb - ca).values())
        stats["PM-001 net"] += len(fb) - len(fa)
    if "dfm_summary" in subs:
        da, db = a.get("dfm_summary") or {}, b.get("dfm_summary") or {}
        ia, ib = da.get("ipc_class_compliance") or {}, db.get("ipc_class_compliance") or {}
        if {k for k in set(da) | set(db) if da.get(k) != db.get(k)} != {"ipc_class_compliance"} or \
                {k for k in set(ia) | set(ib) if ia.get(k) != ib.get(k)} != {"detection_source"} or \
                ib.get("detection_source") != "pcb_fab_notes":
            bad.append("dfm_summary beyond detection_source -> pcb_fab_notes")
        else:
            trig.add("IPC")
    bad += [f"block {k}" for k in sorted(subs - {"dfm_summary"})]
    return _verdict(trig, bad, stats, "pcb")


# ---- gerber ---------------------------------------------------------------------------------------

GERBER_DIRS = re.compile(r"Darkzveller/.*Herkulex|Raziz1/.*Class_4|DamianPodrazaCode/.*S6D0164|"
                         r"jorisplusplus/pcdock/|GlasgowEmbedded/glasgow/.*rev[AB]")
GERBER_BLOCKS = frozenset({"drills", "diagnostics", "alignment", "statistics", "gerbers", "completeness",
                           "layer_count"})


def _gerber(a: dict, b: dict, unit: str = ""):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    if not subs and not rem and not add and a.get("findings") == b.get("findings"):
        # gerber-noop-controls: dot companion files (``._*``) leave inputs.source_files, nothing else moves
        sa = set((a.get("inputs") or {}).get("source_files") or [])
        sb = set((b.get("inputs") or {}).get("source_files") or [])
        gone = sa - sb
        ok = sb <= sa or all(Path(x).name.lstrip("._") in {Path(y).name for y in sa} for x in sb - sa)
        if gone and ok and all(Path(x).name.startswith(".") for x in gone):
            stats["dot files left inputs"] += len(gone)
            return "G-DOT", [], stats
    bad = [f"block {k}" for k in sorted(subs - GERBER_BLOCKS)]
    if {f.get("rule_id") for f in rem + add} - {"GR-003"}:
        bad.append("findings beyond GR-003")
    if not GERBER_DIRS.search(unit):
        bad.append("gerber directory not named by the handoff")
    return _verdict({"GERBER"}, bad, stats, "gerber")


# ---- emc ------------------------------------------------------------------------------------------

STAGE_FAMILY = re.compile(r"^(SU-|PD-00|EE-)")
EMC_RULES = frozenset({"CK-001", "DP-004", "PD-001", "RP-001", "VS-001"})
EMC_FOLLOW = frozenset({"category_summary", "regulatory_coverage", "per_net_scores", "test_plan"})


def _emc(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    bad, trig = [], set()
    stats = Counter()
    fb = _findings(b)
    for f in fb:
        if STAGE_FAMILY.match(str(f.get("rule_id"))) and f.get("stages") != ["layout"]:
            bad.append(f"{f.get('rule_id')} stages {f.get('stages')}")
    fam_a = [f for f in _findings(a) if STAGE_FAMILY.match(str(f.get("rule_id")))]
    fam_b = [f for f in fb if STAGE_FAMILY.match(str(f.get("rule_id")))]
    n_stage = sum(1 for f in fam_a if f.get("stages") != ["layout"])
    if n_stage:
        trig.add("STAGE")
        stats["stages -> layout"] += n_stage
    # PD-001 transient_source relabel (full-chain): compare without it
    relabel = sum(1 for f in fb if f.get("rule_id") == "PD-001" and f.get("transient_source") == "output_cap_proxy")
    rem, add = _moved(a, b, drop=("stages", "transient_source"))
    stats.update(_rule_stats(rem, add))
    if relabel and any(f.get("rule_id") == "PD-001" and f.get("transient_source") == "power_budget" for f in _findings(a)):
        trig.add("PD-SRC")
        stats["PD-001 transient_source relabel"] += relabel
    if any(f.get("transient_source") == "power_budget" for f in fb):
        bad.append("PD-001 transient_source power_budget left")
    rules = {f.get("rule_id") for f in rem + add}
    if rules - EMC_RULES:
        bad.append(f"rules outside the 10b EMC set: {sorted(map(str, rules - EMC_RULES))}")
    if any(f.get("rule_id") == "PD-001" for f in add):
        bad.append("PD-001 added")
    if any(f.get("rule_id") == "RP-001" for f in rem):
        bad.append("RP-001 removed")
    if rules:
        trig.add("CKDP" if rules & {"CK-001", "DP-004"} else "ZG" if rules & {"RP-001", "VS-001"} else "PDN")
        if rules & {"RP-001", "VS-001"}:
            trig.add("ZG")
        if "PD-001" in rules:
            trig.add("PDN")
    bad += [f"block {k}" for k in sorted(subs - EMC_FOLLOW)]
    if subs & EMC_FOLLOW and not rules:
        bad.append("EMC roll-ups moved without a finding move")
    _ = fam_b
    return _verdict(trig, bad, stats, "emc")


# ---- thermal / cross ------------------------------------------------------------------------------

def _thermal(a: dict, b: dict, unit: str = ""):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad = [f"block {k}" for k in sorted(subs - {"assessments", "skipped_components", "missing_info"})]
    if rem or {f.get("rule_id") for f in add} - {"TH-DET"}:
        bad.append("findings beyond TH-DET added")
    if "BelaPlatform/" not in unit:
        bad.append("thermal unit not named by the handoff")
    return _verdict({"TH-NEG"}, bad, stats, "thermal")


def _cross(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    stats = Counter()
    bad, trig = [], set()
    fa, fb = _findings(a), _findings(b)
    norm = lambda fs: Counter(_strip(fs, ("finding_id", "confidence")))  # noqa: E731
    ka, kb = norm(fa), norm(fb)
    gone = ka - kb
    if kb - ka:
        bad.append("cross findings added")
    if any(json.loads(g).get("rule_id") != "RP-002" for g in gone.elements()):
        bad.append("cross findings removed beyond RP-002")
    if gone:
        trig.add("RP2")
        stats["RP-002 removed"] += sum(gone.values())
    ca = Counter((f.get("rule_id"), f.get("confidence")) for f in fa)
    cb = Counter((f.get("rule_id"), f.get("confidence")) for f in fb)
    for (r, c), n in (cb - ca).items():
        if c != "heuristic" or r not in ("RP-002", "PS-002"):
            bad.append(f"{r} confidence {c} gained")
        else:
            trig.add("RELABEL")
            stats[f"{r} -> heuristic"] += n
    bad += [f"block {k}" for k in sorted(subs - {"checks_run"})]
    if "checks_run" in subs:
        trig.add("RP2")
    return _verdict(trig, bad, stats, "cross_analysis")


# ---- unit classification --------------------------------------------------------------------------

_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


def classify_unit(analyzer: str, a_doc: dict, b_doc: dict, unit: str = "") -> dict:
    if analyzer == "schematic":
        label, reasons, stats = _schematic(a_doc, b_doc)
    elif analyzer == "pcb":
        label, reasons, stats = _pcb(a_doc, b_doc)
    elif analyzer == "gerber":
        label, reasons, stats = _gerber(a_doc, b_doc, unit)
    elif analyzer == "emc":
        label, reasons, stats = _emc(a_doc, b_doc)
    elif analyzer == "thermal":
        label, reasons, stats = _thermal(a_doc, b_doc, unit)
    elif analyzer == "cross_analysis":
        label, reasons, stats = _cross(a_doc, b_doc)
    else:
        return {"label": None, "reasons": [f"no class for analyzer {analyzer}"], "stats": Counter()}
    reasons = list(reasons)
    full = analyzer in _FULL_DERIVED
    if not _derived_ok(a_doc, full=full):
        reasons.append("a: derived blocks not from findings")
    if not _derived_ok(b_doc, full=full):
        reasons.append("b: derived blocks not from findings")
    return {"label": label if not reasons else None, "reasons": reasons, "stats": stats}


_CACHE: OrderedDict = OrderedDict()


def _cached(delta, a_doc, b_doc) -> dict | None:
    if not isinstance(a_doc, dict) or not isinstance(b_doc, dict):
        return None
    key = (id(a_doc), id(b_doc))
    hit = _CACHE.get(key)
    if hit is None:
        hit = (classify_unit(delta.analyzer, a_doc, b_doc, getattr(delta, "unit", "") or ""), a_doc, b_doc)
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
gerber = _labelled(("gerber",))
emc = _labelled(("emc",))
thermal = _labelled(("thermal",))
cross_analysis = _labelled(("cross_analysis",))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate_dir", type=Path)
    ap.add_argument("unit", help="one unit (<analyzer>/<owner>/<repo>/<file>) to classify")
    args = ap.parse_args(argv)
    a = json.loads((args.gate_dir / "baseline" / args.unit / "snap.json").read_text(encoding="utf-8"))
    b = json.loads((args.gate_dir / "candidate" / args.unit / "snap.json").read_text(encoding="utf-8"))
    r = classify_unit(args.unit.split("/", 1)[0], a, b, args.unit)
    print(json.dumps({"label": r["label"], "reasons": r["reasons"], "stats": dict(r["stats"])}, indent=1))
    return 0 if r["label"] else 1


if __name__ == "__main__":
    sys.exit(main())
