"""Per-unit budget verdict for the v3.0.2 Wave 11c gate (product 046985ac..db551674), over the
v302_wave11b1_features.py census of the gate dir.

Wave 11c changes how net names are read (one shared power / ground predicate, survey classes P
and G), what the rail map and its consumers do with them (C) and how KO-001 tests a keep-out
(K). Every class is name-keyed except K, so a moved finding is attributed by mechanism, not by
path: it is claimed when one of its strings names a net whose reading differs between the two
products, as computed by importing both products' kicad_core.netnames side by side:

  NAME    a token whose (power, ground, ground-with-rail, vss, virtual-ground) reading flips,
          or (cross_analysis) whose cross-analysis ground reading flips (N6)
  REF     a reference-named net (token ending REF or starting VREF; N8, RS-001 / DO-DET only)
  SPLIT   the 4V5_N half of a split supply (N10, starshipraider only)
  VSS     a VSS-family net a regulator drives (N5 / KH-964, PR-DET / DO-DET only)
  ZERO    the net 0 named by #PWR symbols: the schematic ground-domain pass now reads the rail
          set (classify_ground_domains(power_rails=...)), so 0 is ground there too
  KO      KO-001 on the PCB (K1 / K2) and its rollups
  SCOPE   a rule of the owr-502 local-label divider class (N7) on that repo
  NOPLANE a PS-002 removal on a net the upstream PCB holds no copper zone for (N6b)
  UP      a downstream rule of a declared class on a unit whose upstream schematic / PCB moved
          and was claimed (weak: the finding names no flipped net)
  TRIG    a declared rule or block on a unit that already carries a NAME / REF / KO movement,
          or (NETFLIP) whose own net list holds a flipped name (weak: e.g. connector pin
          counts, single-pin-net counts, rollup-like blocks)
  PAIR    a finding rewritten in place whose other copy (same rule and detection id) is
          attributed

rail_voltages is judged per key: a key that moves must be a NAME / REF / SPLIT token, a ground
net newly at 0 V (g-726: cand is_ground_name and value 0), a regulator output given its name
voltage (c-regulator-output-name-voltage: key is a PR-DET output_rail in the candidate), a VSS
net losing its 0 V key (g-vss) or a sign flip (c-split-negative-rail).

Usage: python regression/budgets/v302_wave11c_judge.py GATE_DIR FEATURES_DIR OUT_PREFIX
       --base PRODUCT --cand PRODUCT [--profile standard|full-chain] [--jobs N]
Writes OUT_PREFIX.json + OUT_PREFIX.units.jsonl.
"""
import argparse
import importlib
import json
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

G = None
PROFILE = "standard"
BASE = CAND = None   # kicad_core.netnames modules of the two products
_CACHE = {}

DERIVED = frozenset({"summary", "trust_summary", "audience_summary"})
OWR = "bluesatunsw/owr-502/"
STARSHIP = "azonenberg/starshipraider/"

# rules each analyzer's declared classes name (union over the budget's classes)
RULES = {
    "schematic": {"RS-001", "DO-DET", "DC-DET", "PD-DET", "RC-DET", "CG-AUD", "EP-AUD", "OA-DET", "SJ-DET",
                  "VM-001", "VD-DET", "CS-DET", "TR-DET", "VD-004", "PP-001", "BR-DET", "LA-AUD", "LB-001",
                  "LS-DET", "IB-DET", "AD-DET", "LC-DET", "PR-DET", "XL-DET", "PL-001", "RF-DET",
                  "VD-003", "MD-DET", "RS-002", "RS-003"},
    "pcb": {"CC-DET", "CC-002", "TB-001", "KO-001"},
    "emc": {"IO-001", "IO-002", "DP-001", "DP-003", "GP-001", "RP-001", "BE-001", "GP-005", "DC-003",
            "DC-002", "SU-001", "SU-002", "DC-001", "PD-001"},
    "thermal": {"TS-001", "TP-001", "TS-004", "TS-005", "TH-DET"},
    "cross_analysis": {"EG-001", "RP-002", "DA-001", "PS-002", "VS-002", "TW-001"},
}
OWR_RULES = {"VD-DET", "PR-DET", "DO-DET", "VD-004", "DC-DET", "TH-DET", "TS-005", "PD-001"}
STARSHIP_RULES = {"PR-DET", "DO-DET", "TH-DET", "TS-005", "TW-001"}
BLOCKS = {
    "schematic": {"statistics", "rail_voltages", "design_analysis", "pdn_impedance", "power_budget",
                  "sleep_current_audit", "test_coverage", "subcircuits", "connectivity_issues",
                  "net_classifications", "ground_domains", "inrush_analysis", "power_sequencing",
                  "power_sequencing_validation", "missing_info", "protocol_compliance", "power_tree"},
    "pcb": {"power_net_resolution", "power_net_routing", "layer_transitions", "ground_domains",
            "decoupling_placement", "decoupling_proximity", "return_path_continuity",
            "reference_plane_changes", "board_thickness_mm"},
    "emc": {"per_net_scores", "category_summary", "regulatory_coverage", "test_plan", "emc_risk_score",
            "board_info"},
    "thermal": {"assessments", "missing_info", "skipped_components"},
    "cross_analysis": {"checks_run"},
}


# ------------------------------------------------------------------------------- predicates

def _load_netnames(product):
    scripts = str(Path(product).resolve() / "skills/kicad/scripts")
    saved = {k: v for k, v in sys.modules.items() if k == "kicad_core" or k.startswith("kicad_core.")}
    for k in saved:
        del sys.modules[k]
    sys.path.insert(0, scripts)
    try:
        mod = importlib.import_module("kicad_core.netnames")
    finally:
        sys.path.remove(scripts)
        for k in [k for k in sys.modules if k == "kicad_core" or k.startswith("kicad_core.")]:
            del sys.modules[k]
        sys.modules.update(saved)
    return mod


def _init(base, cand, gate, profile):
    global BASE, CAND, G, PROFILE
    BASE, CAND, G, PROFILE = _load_netnames(base), _load_netnames(cand), Path(gate), profile


def _sig(m, t):
    virt = getattr(m, "is_virtual_ground_name", None)
    return (bool(m.is_power_net_name(t)), bool(m.is_ground_name(t)), bool(m.is_ground_name(t, {t})),
            bool(m.is_vss_name(t)), bool(virt(t)) if virt else False)


def _old_cross_ground(t):
    n = t.upper().replace('/', '').replace('-', '').replace('_', '')
    return n in ('GND', 'VSS', 'DGND', 'AGND', 'PGND', 'GNDD', 'GNDA', 'EARTH', 'CHASSIS', '0V')


def _new_cross_ground(t):
    return bool(CAND.is_ground_name(t)) or CAND.net_leaf(t).upper() in ('EARTH', 'CHASSIS')


def _is_ref(t):
    return any(x.endswith("REF") or x.startswith("VREF")
               for x in re.findall(r"[A-Z]+|[0-9]+", CAND.net_leaf(t).upper()))


_SPLIT_N = re.compile(r"\+?\d+V\d+_N")


def classify(t, an):
    """Mechanism labels a token carries ('' when none)."""
    key = (t, an == "cross_analysis")
    hit = _CACHE.get(key)
    if hit is not None:
        return hit
    out = set()
    try:
        if _sig(BASE, t) != _sig(CAND, t):
            out.add("NAME")
        if an == "cross_analysis" and _old_cross_ground(t) != _new_cross_ground(t):
            out.add("NAME")
        if _is_ref(t):
            out.add("REF")
        if _SPLIT_N.fullmatch(CAND.net_leaf(t).upper()):
            out.add("SPLIT")
        if CAND.is_vss_name(t):
            out.add("VSS")
        if CAND.net_leaf(t) == "0":
            out.add("ZERO")
    except Exception:  # noqa: BLE001 - a token the predicates cannot read names nothing
        pass
    _CACHE[key] = frozenset(out)
    return _CACHE[key]


_SPLIT_TOK = re.compile(r"[\s,;'\"`\[\]]+")


def _strings(x, keys=False):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            if keys and isinstance(k, str):
                yield k
            yield from _strings(v, keys)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v, keys)


def _tokens(x, keys=False):
    seen = set()
    for s in _strings(x, keys):
        if len(s) > 400:
            parts = _SPLIT_TOK.split(s)
        else:
            parts = [s] + _SPLIT_TOK.split(s)
        for p in parts:
            for t in (p, p.rstrip(".,:;)!?"), p.lstrip("(")):
                if t and len(t) <= 80 and t not in seen:
                    seen.add(t)
                    yield t


def mechanisms(x, an, keys=False):
    out = set()
    for t in _tokens(x, keys):
        out |= classify(t, an)
    return out


# ------------------------------------------------------------------------------------ judge

def _snap(side, unit):
    return json.loads((G / side / unit / "snap.json").read_text(encoding="utf-8"))


def _findings(d):
    f = d.get("findings")
    return [x for x in f if isinstance(x, dict)] if isinstance(f, list) else []


def _canon(f):
    return json.dumps({k: v for k, v in f.items() if k != "finding_id"}, sort_keys=True, default=str)


def _finding_moves(a, b):
    ca = Counter(_canon(f) for f in _findings(a))
    cb = Counter(_canon(f) for f in _findings(b))
    rem = [json.loads(k) for k, n in (ca - cb).items() for _ in range(n)]
    add = [json.loads(k) for k, n in (cb - ca).items() for _ in range(n)]
    return rem, add


def _attr_finding(f, an, unit, side, ctx):
    rid = str(f.get("rule_id"))
    mech = mechanisms(f, an)
    if an == "pcb" and rid == "KO-001":
        return "KO"
    if "NAME" in mech:
        return "NAME"
    if "ZERO" in mech and rid in ("RS-001", "DO-DET", "DC-DET", "RC-DET", "VD-DET"):
        return "ZERO"
    if "REF" in mech and rid in ("RS-001", "RS-002", "RS-003", "DO-DET"):
        return "REF"
    if "SPLIT" in mech and STARSHIP in unit:
        return "SPLIT"
    if "VSS" in mech and rid in ("PR-DET", "DO-DET"):
        return "VSS"
    if OWR in unit and rid in OWR_RULES:
        return "SCOPE"
    if STARSHIP in unit and rid in STARSHIP_RULES:
        return "SCOPE"
    if an == "cross_analysis" and rid == "PS-002" and side == "removed" and ctx.get("zones") is not None:
        plane = (f.get("nets") or [None])[0]
        if plane and plane not in ctx["zones"]:
            return "NOPLANE"
    if rid in RULES.get(an, ()) and an in ("emc", "thermal", "cross_analysis") and ctx.get("up_claimed"):
        return "UP"
    return None


def _ko_desc_only(rem, add):
    """KO-001 rewritten in place (description) pairs one-for-one."""
    return [f for f in rem if f.get("rule_id") == "KO-001"], [f for f in add if f.get("rule_id") == "KO-001"]


def _rail_key_ok(k, va, vb, unit, b_doc):
    mech = classify(k, "schematic")
    if mech & {"NAME", "REF"}:
        return "NAME"
    if "SPLIT" in mech and STARSHIP in unit:
        return "SPLIT"
    if vb == 0 and CAND.is_ground_name(k):
        # g-726: a ground-named net gets 0 V (was absent, or its name voltage: 5V_tvs_gnd 5.0)
        if va is None:
            return "G726"
        return "G726-AMBIG" if CAND.is_power_net_name(k) else "G726-VALUE"
    leaf = CAND.net_leaf(k)
    regs = [f for f in _findings(b_doc) if f.get("rule_id") == "PR-DET"
            and f.get("output_rail") and CAND.net_leaf(f["output_rail"]) == leaf]
    if regs and vb is not None and any(f.get("estimated_vout") == vb for f in regs):
        return "C-REGEST"
    if regs and va is None and vb is not None:
        return "C-REGNAME"
    if "VSS" in mech and (vb is None or va is None or va != vb):
        return "G-VSS"
    if va is not None and vb is not None and isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
            and vb == -va and STARSHIP in unit:
        return "SPLIT"
    if OWR in unit:
        return "SCOPE"
    if STARSHIP in unit:
        return "SCOPE"
    return None


def _zones_of(unit_pcb):
    """net names holding a copper zone in the candidate upstream PCB snap (None if unreadable)."""
    try:
        doc = _snap("candidate", unit_pcb)
    except Exception:  # noqa: BLE001
        return None
    return {z.get("net_name") for z in doc.get("zones") or [] if isinstance(z, dict)}


def judge_unit(task):
    r, up_claimed = task
    unit, an = r["unit"], r["an"]
    labels, bad = Counter(), []
    if "error" in r:
        return unit, an, None, [r["error"]], {}
    try:
        a, b = _snap("baseline", unit), _snap("candidate", unit)
    except Exception as e:  # noqa: BLE001
        return unit, an, None, [f"snap {e}"], {}
    ctx = {"up_claimed": up_claimed}
    if an == "cross_analysis":
        ub = ((r.get("upstream") or {}).get("pcb") or [None, None])[1]
        ctx["zones"] = _zones_of(ub) if ub else None
    rem, add = _finding_moves(a, b)
    weak, got = [], {}
    for side, fs in (("removed", rem), ("added", add)):
        for f in fs:
            lab = _attr_finding(f, an, unit, side, ctx)
            if lab is None:
                weak.append((side, f))
            else:
                labels[lab] += 1
                got.setdefault((f.get("rule_id"), f.get("detection_id") or f.get("summary")), lab)
    # a finding rewritten in place inherits the label of its other copy (MD-DET gains VMOT)
    still = []
    for side, f in weak:
        if (f.get("rule_id"), f.get("detection_id") or f.get("summary")) in got:
            labels["PAIR"] += 1
        else:
            still.append((side, f))
    weak = still
    # rail_voltages per key
    tops = set(r["tops"])
    if "rail_voltages" in tops:
        ra, rb = a.get("rail_voltages") or {}, b.get("rail_voltages") or {}
        for k in set(ra) | set(rb):
            va, vb = ra.get(k), rb.get(k)
            if va == 0 and vb == 0 and type(va) is not type(vb):
                # N4: a 0V-named ground now gets 0 from is_ground_name, not 0.0 from the parser
                labels["RV:G726-INT"] += 1
                continue
            if va != vb or (k in ra) != (k in rb):
                lab = _rail_key_ok(k, ra.get(k), rb.get(k), unit, b)
                if lab is None:
                    bad.append(f"rail_voltages key {k!r} {ra.get(k)} -> {rb.get(k)}")
                else:
                    labels["RV:" + lab] += 1
    if "statistics" in tops:
        sub = set(r["sub"].get("statistics") or [])
        if sub - {"power_rails"}:
            bad.append(f"statistics {sorted(sub - {'power_rails'})}")
        pa = {json.dumps(x, sort_keys=True) for x in (a.get("statistics") or {}).get("power_rails") or []}
        pb = {json.dumps(x, sort_keys=True) for x in (b.get("statistics") or {}).get("power_rails") or []}
        for x in pa ^ pb:
            nm = json.loads(x).get("name") or ""
            m = classify(nm, "schematic")
            if m & {"NAME", "REF"} or (STARSHIP in unit and "SPLIT" in m):
                labels["SP:NAME"] += 1
            else:
                bad.append(f"statistics.power_rails {nm!r}")
    strong = sum(v for k, v in labels.items())
    trig = bool(strong) or bool(up_claimed)
    if not trig and an == "schematic":
        # a net of the unit whose reading flips (COM, a V-number signal) without being named
        # in the moved item: single-pin-net counts, op-amp input resistors, decoupling credit
        for nm in set(a.get("nets") or {}) | set(b.get("nets") or {}):
            if classify(nm, an) & {"NAME", "ZERO"}:
                trig = True
                labels["NETFLIP"] += 1
                break
    for side, f in weak:
        rid = str(f.get("rule_id"))
        if trig and rid in RULES.get(an, ()):
            labels["TRIG"] += 1
        else:
            bad.append(f"{side} {rid}: {str(f.get('summary') or f.get('description') or f.get('detector'))[:90]}")
    for k in sorted(tops - DERIVED - {"findings", "rail_voltages", "statistics"}):
        if k in BLOCKS.get(an, ()):
            hit = (mechanisms(b.get(k), an, keys=True) | mechanisms(a.get(k), an, keys=True)) & {"NAME", "REF", "ZERO"}
            if not trig and not hit:
                bad.append(f"block {k} without a trigger")
            else:
                labels["BLK"] += 1
        else:
            bad.append(f"block {k}")
    if "findings" in tops and not rem and not add and not trig:
        bad.append("findings order / ids moved without a trigger")
    if (r.get("id_only") or {}) and not trig:
        bad.append(f"finding_id change {sorted(r['id_only'])} without a trigger")
    if not all(r["derived_ok"]):
        bad.append(f"derived blocks not from findings {r['derived_ok']}")
    thermal_counts = an == "thermal" and tops & {"assessments", "skipped_components"}
    if tops & DERIVED and not (rem or add or "findings" in tops or r.get("id_only") or thermal_counts):
        bad.append(f"rollups moved without findings {sorted(tops & DERIVED)}")
    if not labels and not bad:
        bad.append("movement without a trigger")
    label = "+".join(sorted(k for k in labels)) if not bad else None
    return unit, an, label, bad, dict(labels)


def _load(p):
    if not p.exists():
        return []
    return [json.loads(line) for line in p.open(encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gate", type=Path)
    ap.add_argument("features_dir", type=Path)
    ap.add_argument("out")
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--profile", default="standard")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    gate = args.gate.resolve()
    fd = args.features_dir
    out_units, claimed = [], {}
    tally = {"mech": Counter(), "units": Counter(), "rules": defaultdict(lambda: [0, 0, 0]), "blocks": Counter()}
    with ProcessPoolExecutor(args.jobs, initializer=_init,
                             initargs=(args.base, args.cand, str(gate), args.profile)) as ex:
        for stage in (("schematic", "pcb", "gerber"), ("emc", "thermal", "cross_analysis")):
            tasks = []
            for an in stage:
                for r in _load(fd / f"{an}.jsonl"):
                    up = r.get("upstream") or {}
                    ups = [(up.get(k) or [None])[0] for k in ("schematic", "pcb")]
                    upc = any(u and claimed.get(u) for u in ups)
                    if any(u and u in claimed and claimed[u] is None for u in ups):
                        upc = False
                    tasks.append((r, upc))
                    tally["units"][an] += 1
                    for rid, (rem, add) in (r.get("rules") or {}).items():
                        t = tally["rules"][f"{an}:{rid}"]
                        t[0] += rem; t[1] += add; t[2] += 1
                    for k in r["tops"]:
                        tally["blocks"][f"{an}:{k}"] += 1
            for unit, an, label, bad, labs in ex.map(judge_unit, tasks, chunksize=4):
                claimed[unit] = label
                tally["mech"].update({f"{an}:{k}": v for k, v in labs.items()})
                out_units.append({"unit": unit, "an": an, "label": label, "bad": bad[:10], "mech": labs})
    resid = [u for u in out_units if u["label"] is None]
    reasons = Counter(re.sub(r"(: .*|'.*)$", "", b) for u in resid for b in u["bad"])
    summary = {
        "profile": args.profile,
        "moved_units": dict(tally["units"]),
        "claimed": sum(1 for u in out_units if u["label"]),
        "residual_units": len(resid),
        "residual_by_analyzer": dict(Counter(u["an"] for u in resid)),
        "residual_reasons": dict(reasons.most_common(80)),
        "mechanisms": dict(sorted(tally["mech"].items())),
        "rules": {k: {"removed": v[0], "added": v[1], "units": v[2]} for k, v in sorted(tally["rules"].items())},
        "blocks": dict(tally["blocks"].most_common()),
        "verdict": "clean" if not resid else "residuals",
    }
    Path(args.out + ".json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    with open(args.out + ".units.jsonl", "w", encoding="utf-8") as fo:
        for u in out_units:
            fo.write(json.dumps(u) + "\n")
    print(json.dumps({k: summary[k] for k in ("moved_units", "claimed", "residual_units", "residual_by_analyzer",
                                               "residual_reasons", "mechanisms", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
