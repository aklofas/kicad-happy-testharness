"""Per-unit budget verdict for the v3.0.2 Wave 11b-2 gate (product 0f2deade..6138b126), over the
v302_wave11b1_features.py census of the gate dir.

A moved unit is CLAIMED when every movement falls inside one of the merged budget's mechanisms
(budget-wave11b-2.json: survey classes D / E / F1 / G + restatements), checked per unit. Where the
features cannot prove a class, the judge reads both snaps of the unit:

schematic  VM-001 removals only; needs_level_shifter true -> false; property_issues gains only
           duplicate_value_field entries; the MIC2305x regulator add (PR-DET grows, then DO-DET /
           PS-001 / RS-001 and the derived power blocks may move on that unit); goya1746 ipc_class.
pcb        d1 board area (the new area equals kicad-cli's Board Statistics area, --kc-area;
           design_intent follows), d2 revision (only missing_revision warnings leave,
           revision_marking false -> true), d3 TV-001 rewritten in place (+ finding_id
           renumbering), d5 stackup cut at the first repeated layer (CP-002 /
           copper_presence_summary follow; full-chain: via stub lengths and return-path
           entries counted through the repeated copies go), d6 the mixed-token boards
           (any block), d7 via_in_pad pad / same_net / component, d8 FD-001 never grows,
           d9 legacy rules / classes removed only, d10 the DRU boards.
gerber     d12: gerbers / gerber_files / diagnostics shrink, job-file completeness, GR-001 removals.
emc / thermal / cross_analysis
           rules and blocks listed per analyzer with a direction; a rule marked UP moves only when
           the upstream schematic or PCB the unit read moved and is claimed.

Usage: python regression/budgets/v302_wave11b2_judge.py GATE_DIR FEATURES_DIR OUT_PREFIX --samples SURVEY_D_SAMPLES
       [--kc-area KC.jsonl] [--profile standard|full-chain]
Writes OUT_PREFIX.json + OUT_PREFIX.units.jsonl.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

G = None  # gate dir
PROFILE = "standard"


def _sample_units(samples_dir, name):
    """pcb unit ids from a survey sample list (tab-separated, last column = path under repos/)."""
    out = set()
    p = Path(samples_dir) / f"{name}.tsv"
    for line in p.open(encoding="utf-8"):
        path = line.rstrip("\n").split("\t")[-1]
        if "/repos/" in path:
            o, r, rest = path.split("/repos/", 1)[1].split("/", 2)
            out.add(f"pcb/{o}/{r}/{rest.replace('/', '_')}")
    return out


MIXED = set()  # d6: the 15 boards with mixed module / footprint tokens (survey D mixed.tsv)
DRU = set()    # d10: boards with a .kicad_dru the survey reached (survey D dru.tsv)
ADJUDICATED = {}                 # unit -> reason, filled from hand checks (see operations.log)
KC_AREA = {}                     # unit -> kicad-cli stats record (--kc-area JSONL from kc_stats.py)


def _snap(side, unit):
    return json.loads((G / side / unit / "snap.json").read_text(encoding="utf-8"))


def _gp(r):
    """[(path, op)] from the census' generalized delta paths."""
    return [tuple(k.rsplit("|", 1)) for k in (r.get("gpaths") or {})]


DERIVED = frozenset({"summary", "trust_summary", "audience_summary"})


def _rules_check(r, spec, bad, up_moved=True):
    """spec: rule -> 'inplace' | 'shrink' | 'remove' | 'grow' | 'any', optional '+UP' (needs an upstream move)."""
    rules = r.get("rules") or {}
    for rid, (rem, add) in rules.items():
        s = spec.get(rid)
        if s is None:
            bad.append(f"rule {rid} -{rem}+{add}")
            continue
        mode, _, need = s.partition("+")
        if need == "UP" and not up_moved:
            bad.append(f"rule {rid} -{rem}+{add} without an upstream move")
        elif mode == "inplace" and rem != add:
            bad.append(f"in-place rule {rid} -{rem}+{add}")
        elif mode == "shrink" and add > rem:
            bad.append(f"shrink-only rule {rid} -{rem}+{add}")
        elif mode == "remove" and add:
            bad.append(f"remove-only rule {rid} -{rem}+{add}")
        elif mode == "grow" and rem > add:
            bad.append(f"grow-only rule {rid} -{rem}+{add}")
    for rid in (r.get("id_only") or {}):
        if rid not in spec:
            bad.append(f"finding_id change on {rid}")
    return rules


def _derived(r, bad):
    tops = set(r["tops"])
    if not all(r["derived_ok"]):
        bad.append(f"derived blocks not from findings {r['derived_ok']}")
    if tops & DERIVED and not (r.get("rules") or r.get("id_only") or "findings" in tops):
        bad.append(f"rollups moved without findings {sorted(tops & DERIVED)}")


# ----------------------------------------------------------------------------------- schematic

SCH_SPEC = {"VM-001": "remove", "PR-DET": "grow", "DO-DET": "any", "PS-001": "any", "RS-001": "remove"}
SCH_REG_BLOCKS = frozenset({"power_sequencing_validation", "inrush_analysis", "net_classifications",
                            "power_sequencing", "pdn_impedance", "power_budget", "sleep_current_audit",
                            "rail_voltages", "design_analysis", "missing_info", "subcircuits"})


def judge_schematic(r):
    bad, trig = [], set()
    tops = set(r["tops"])
    rules = _rules_check(r, SCH_SPEC, bad)
    reg_add = (rules.get("PR-DET") or [0, 0])[1] > (rules.get("PR-DET") or [0, 0])[0]
    if reg_add:
        trig.add("G4")
    elif set(rules) - {"VM-001"}:
        bad.append(f"regulator-class rules {sorted(set(rules) - {'VM-001'})} without a PR-DET add")
    if "VM-001" in rules:
        trig.add("G1G2")
    if r.get("comp") or r.get("nets") or r.get("labels"):
        bad.append("components / nets / labels moved")
    for k in sorted(tops - DERIVED - {"findings"}):
        if k == "property_issues":
            a, b = _snap("baseline", r["unit"]).get(k) or {}, _snap("candidate", r["unit"]).get(k) or {}
            ia = Counter(json.dumps(x, sort_keys=True) for x in a.get("issues") or [])
            ib = Counter(json.dumps(x, sort_keys=True) for x in b.get("issues") or [])
            gone, new = ia - ib, ib - ia
            if gone or any(json.loads(x).get("issue") != "duplicate_value_field" for x in new):
                bad.append("property_issues moved beyond duplicate_value_field adds")
            trig.add("G5")
        elif k == "design_analysis" and not reg_add:
            sub = set(r["sub"].get(k) or [])
            if sub - {"cross_domain_signals"}:
                bad.append(f"design_analysis {sorted(sub)}")
            for p, op in _gp(r):
                if p.startswith("/design_analysis/") and not re.fullmatch(
                        r"/design_analysis/cross_domain_signals/N/needs_level_shifter", p):
                    bad.append(f"design_analysis path {p}")
                    break
            a = _snap("baseline", r["unit"])["design_analysis"]["cross_domain_signals"]
            b = _snap("candidate", r["unit"])["design_analysis"]["cross_domain_signals"]
            def _flip_ok(x, y):
                diff = {f for f in set(x) | set(y) if x.get(f) != y.get(f)}
                return not diff or (diff == {"needs_level_shifter"}
                                    and x.get("needs_level_shifter") is True and y.get("needs_level_shifter") is False)
            if len(a) != len(b) or not all(_flip_ok(x, y) for x, y in zip(a, b)):
                bad.append("needs_level_shifter moved other than true -> false")
            trig.add("G1G2-XD")
        elif k == "design_intent" and r["unit"].startswith("schematic/escaroda/goya1746/"):
            if set(r["sub"].get(k) or []) - {"ipc_class", "detection_signals"}:
                bad.append(f"design_intent {r['sub'].get(k)}")
            trig.add("D11")
        elif k in SCH_REG_BLOCKS and reg_add:
            trig.add("G4")
        else:
            bad.append(f"block {k}")
    _derived(r, bad)
    if not trig and not bad:
        bad.append("movement without a trigger")
    return ("+".join(sorted(trig)) if not bad else None), bad


# ----------------------------------------------------------------------------------------- pcb

PCB_SPEC = {"TV-001": "inplace", "FD-001": "shrink", "CP-002": "any", "RT-001": "any", "TE-001": "any",
            "PM-002": "any", "GP-001": "any"}
D1_SUB = {"statistics": {"board_area_mm2"},
          "placement_density": {"board_area_cm2", "front_density_per_cm2", "back_density_per_cm2"},
          "design_intent": {"detection_signals", "confidence", "product_class", "target_market"}}
D9_PATHS = re.compile(r"/(design_rule_compliance/(rules_source|net_class_summary)|project_settings/(net_classes|design_rules))")
D10_PATHS = re.compile(r"/(project_settings/custom_rules.*|design_rule_compliance/conditional_rules_.*|design_rule_compliance/rules_checked)")
D7_PATH = re.compile(r"/vias/via_analysis/via_in_pad/N/(pad|same_net|component)")
FC_PCB = re.compile(r"/(vias/(via_analysis/)?(stub|.*stub_length_mm).*|return_path_continuity.*|vias/.*stub.*)")


def _stackup_cut(unit):
    a = (_snap("baseline", unit).get("setup") or {}).get("stackup") or []
    b = (_snap("candidate", unit).get("setup") or {}).get("stackup") or []
    if not b or len(b) >= len(a) or a[:len(b)] != b:
        return False
    names = {x.get("name") for x in b}
    return a[len(b)].get("name") in names


def judge_pcb(r):
    bad, trig = [], set()
    unit = r["unit"]
    tops = set(r["tops"])
    if unit in MIXED:
        _derived(r, bad)
        return ("D6" if not bad else None), bad
    rules = _rules_check(r, PCB_SPEC, bad)
    stack = "setup" in tops
    if stack:
        if set(r["sub"].get("setup") or []) - {"stackup"} or not _stackup_cut(unit):
            bad.append("setup moved other than a stackup cut at the first repeated layer")
        trig.add("D5")
    for rid in set(rules) & {"CP-002", "GP-001"}:
        if not stack:
            bad.append(f"{rid} moved without a stackup cut")
    for rid in set(rules) & {"RT-001", "TE-001", "PM-002"}:
        if not (rid == "RT-001" and PROFILE == "full-chain"):
            bad.append(f"{rid} moved off the mixed-token boards")
    if "TV-001" in rules or "TV-001" in (r.get("id_only") or {}):
        trig.add("D3")
    if "FD-001" in rules:
        trig.add("D8")
    if "RT-001" in rules:
        trig.add("D4")
    paths = _gp(r)
    for k in sorted(tops - DERIVED - {"findings", "setup"}):
        sub = set(r["sub"].get(k) or [])
        if k in D1_SUB:
            if sub - D1_SUB[k]:
                bad.append(f"{k} {sorted(sub - D1_SUB[k])}")
            trig.add("D1")
        elif k == "silkscreen":
            a, b = _snap("baseline", unit)["silkscreen"], _snap("candidate", unit)["silkscreen"]
            ca = Counter(json.dumps(x, sort_keys=True) for x in a.get("documentation_warnings") or [])
            cb = Counter(json.dumps(x, sort_keys=True) for x in b.get("documentation_warnings") or [])
            gone = {json.loads(x).get("type") for x in (ca - cb)}
            other = {s for s in set(a) | set(b) if a.get(s) != b.get(s)} - {"documentation_warnings", "silkscreen_completeness"}
            rm = ((a.get("silkscreen_completeness") or {}).get("checks") or {}).get("revision_marking")
            rmb = ((b.get("silkscreen_completeness") or {}).get("checks") or {}).get("revision_marking")
            if cb - ca or gone - {"missing_revision"} or other or not (rm is False and rmb is True):
                bad.append("silkscreen moved beyond the revision-mark fix")
            trig.add("D2")
        elif k == "vias":
            for p, op in paths:
                if p.startswith("/vias/") and not (D7_PATH.fullmatch(p) and op == "changed") \
                        and not (PROFILE == "full-chain" and "stub" in p):
                    bad.append(f"vias path {p} {op}")
                    break
            trig.add("D7")
        elif k in ("design_rule_compliance", "project_settings"):
            for p, op in paths:
                if not p.startswith("/" + k):
                    continue
                if D9_PATHS.match(p) and op == "removed":
                    trig.add("D9")
                elif D10_PATHS.match(p) and unit in DRU:
                    trig.add("D10")
                else:
                    bad.append(f"{k} path {p} {op}")
                    break
        elif k == "copper_presence_summary" and stack:
            pass
        elif k == "return_path_continuity" and stack and PROFILE == "full-chain":
            pass
        elif k == "net_lengths" and stack and PROFILE == "full-chain":
            # d5 full-chain: via stubs were counted through the repeated stack copies (beetleback panels)
            for p, op in paths:
                if p.startswith("/net_lengths/") and not (p.endswith("/stub_length_mm") and op == "removed"):
                    bad.append(f"net_lengths path {p} {op}")
                    break
        else:
            bad.append(f"block {k}")
    if "statistics" in tops or "placement_density" in tops:
        # d1: the new area is KiCad's Board Statistics area (kicad-cli pcb export stats)
        b = (_snap("candidate", unit).get("statistics") or {}).get("board_area_mm2")
        kc = KC_AREA.get(unit)
        if kc is None:
            bad.append("board area moved; no kicad-cli oracle record")
        elif kc.get("area") is None:
            trig.add("D1-KC-UNLOADABLE")
        elif not (isinstance(b, (int, float)) and abs(b - kc["area"]) <= max(1.0, 0.005 * kc["area"])):
            bad.append(f"board area {b} != kicad-cli {kc['area']}")
    if "design_intent" in tops and "statistics" not in tops:
        bad.append("design_intent moved without a board-area change")
    _derived(r, bad)
    if not trig and not bad:
        bad.append("movement without a trigger")
    if bad and unit in ADJUDICATED:
        return "ADJ", []
    return ("+".join(sorted(trig)) if not bad else None), bad


# -------------------------------------------------------------------------------------- gerber

GERBER_TOPS = frozenset({"diagnostics", "gerbers", "statistics", "board_dimensions", "completeness",
                         "generator", "job_file", "findings"}) | DERIVED


def judge_gerber(r):
    bad = []
    tops = set(r["tops"])
    if tops - GERBER_TOPS:
        bad.append(f"gerber blocks {sorted(tops - GERBER_TOPS)}")
    if set(r["sub"].get("statistics") or []) - {"gerber_files"}:
        bad.append(f"statistics {r['sub'].get('statistics')}")
    if r["diag"][1] > r["diag"][0]:
        bad.append("diagnostics grew")
    rules = _rules_check(r, {"GR-001": "remove"}, bad)
    if rules and "completeness" not in tops:
        bad.append("GR-001 moved without a completeness change")
    if tops & {"board_dimensions", "generator", "job_file"} and "completeness" not in tops:
        bad.append("job-file blocks without a completeness change")
    _derived(r, bad)
    return ("D12" if not bad else None), bad


# --------------------------------------------------------------------------- emc / thermal / cross

# rule -> mode[+UP]; UP = only with a claimed upstream move
DOWN_SPEC = {
    "emc": {
        # D1 (+ 2 removals), D5, D6
        "VS-001": "shrink+UP", "SU-001": "shrink", "SU-002": "shrink",
        # M1 DNP connectors / net identity (rare power-only info add), ES-001 removal-only after the fix wave
        "IO-001": "any", "IO-002": "shrink", "ES-001": "remove",
        # M2 DC-002 non-IC, power-typed planes, BE-001 polygon edges (full-chain)
        "DC-002": "remove", "CK-001": "remove", "DP-004": "remove", "BE-001": "grow",
        # fc DNP extras, G1 MIC2305x (fc), D6 board extras
        "CK-003": "any", "ES-002": "remove", "SW-001": "any+UP", "EE-002": "any+UP", "SW-003": "any+UP",
        "RT-001": "any+UP", "TE-001": "any+UP", "PM-002": "any+UP", "CP-002": "any+UP", "GP-001": "any+UP",
    },
    "thermal": {"TS-001": "any", "TS-002": "any", "TS-003": "any", "TS-005": "any", "TP-001": "any",
                "TH-DET": "any", "TS-004": "any"},
    "cross_analysis": {"DA-001": "shrink", "CC-001": "shrink", "TW-001": "shrink", "EG-001": "any",
                       "XV-001": "any+UP", "XV-002": "any+UP", "VS-002": "any+UP", "PS-002": "any+UP"},
}
DOWN_BLOCKS = {
    "emc": {"findings", "summary", "trust_summary", "audience_summary", "category_summary", "per_net_scores",
            "regulatory_coverage", "test_plan", "board_info"},
    "thermal": {"findings", "assessments", "summary", "trust_summary", "audience_summary", "missing_info",
                "skipped_components"},
    "cross_analysis": {"findings", "checks_run", "summary", "trust_summary", "audience_summary"},
}


def judge_downstream(r, claimed):
    up = r.get("upstream") or {}
    moved, unclaimed = [], []
    for kind in ("schematic", "pcb"):
        ua = (up.get(kind) or [None, None])[0]
        if ua and ua in claimed:
            (unclaimed if claimed[ua] is None else moved).append(kind)
    bad = [f"upstream {k} unclaimed" for k in unclaimed]
    an = r["an"]
    tops = set(r["tops"])
    if tops - DOWN_BLOCKS[an]:
        if moved:
            pass  # a claimed upstream move may reach any block of the chained unit
        else:
            bad.append(f"{an} blocks {sorted(tops - DOWN_BLOCKS[an])} without an upstream move")
    _rules_check(r, DOWN_SPEC[an], bad, up_moved=bool(moved))
    if an == "cross_analysis" and "checks_run" in tops:
        for p, op in _gp(r):
            # a checks_run row carries its own finding count, which follows the finding moves
            if p == "/checks_run/N/findings" and r.get("rules"):
                continue
            if p.startswith("/checks_run/") and not re.fullmatch(r"/checks_run/N/(ran|reason_skipped|items_examined)", p):
                if not moved:
                    bad.append(f"checks_run path {p}")
                    break
    if not all(r["derived_ok"]):
        bad.append(f"derived blocks not from findings {r['derived_ok']}")
    label = ("D:" + "+".join(moved)) if moved else "E"
    return (label if not bad else None), bad


def _load(p):
    if not p.exists():
        return []
    return [json.loads(line) for line in p.open(encoding="utf-8")]


def main():
    global G, PROFILE
    ap = argparse.ArgumentParser()
    ap.add_argument("gate", type=Path)
    ap.add_argument("features_dir", type=Path)
    ap.add_argument("out")
    ap.add_argument("--profile", default="standard")
    ap.add_argument("--kc-area", type=Path, help="kc_stats.py JSONL (unit, area) for the d1 board-area oracle")
    ap.add_argument("--samples", type=Path, required=True,
                    help="survey D samples dir holding mixed.tsv and dru.tsv")
    args = ap.parse_args()
    G, PROFILE = args.gate.resolve(), args.profile
    MIXED.update(_sample_units(args.samples, "mixed"))
    DRU.update(_sample_units(args.samples, "dru"))
    if args.kc_area and args.kc_area.exists():
        for line in args.kc_area.open(encoding="utf-8"):
            rec = json.loads(line)
            KC_AREA[rec["u"]] = rec
    fd = args.features_dir
    out_units, claimed = [], {}
    tally = {"rules": defaultdict(lambda: [0, 0, 0]), "blocks": Counter(), "id_only": Counter(), "units": Counter()}
    for an, fn in (("schematic", judge_schematic), ("pcb", judge_pcb), ("gerber", judge_gerber)):
        for r in _load(fd / f"{an}.jsonl"):
            label, bad = fn(r) if "error" not in r else (None, [r["error"]])
            claimed[r["unit"]] = label
            out_units.append({"unit": r["unit"], "an": an, "label": label, "bad": bad[:8]})
    for an in ("emc", "thermal", "cross_analysis"):
        for r in _load(fd / f"{an}.jsonl"):
            label, bad = judge_downstream(r, claimed) if "error" not in r else (None, [r["error"]])
            if bad and r["unit"] in ADJUDICATED:
                label, bad = "ADJ", []
            claimed[r["unit"]] = label
            out_units.append({"unit": r["unit"], "an": an, "label": label, "bad": bad[:8]})
    for an in ("schematic", "pcb", "gerber", "emc", "thermal", "cross_analysis"):
        for r in _load(fd / f"{an}.jsonl"):
            tally["units"][an] += 1
            for rid, (rem, add) in (r.get("rules") or {}).items():
                t = tally["rules"][f"{an}:{rid}"]
                t[0] += rem; t[1] += add; t[2] += 1
            for k in r["tops"]:
                tally["blocks"][f"{an}:{k}"] += 1
            for k, v in (r.get("id_only") or {}).items():
                tally["id_only"][f"{an}:{k}"] += v
    resid = [u for u in out_units if u["label"] is None]
    reasons = Counter(re.sub(r" -\d+\+\d+.*", "", b) for u in resid for b in u["bad"])
    summary = {
        "profile": PROFILE,
        "moved_units": dict(tally["units"]),
        "claimed": sum(1 for u in out_units if u["label"]),
        "residual_units": len(resid),
        "residual_by_analyzer": dict(Counter(u["an"] for u in resid)),
        "residual_reasons": dict(reasons.most_common(60)),
        "labels": dict(Counter(f"{u['an']}:{u['label']}" for u in out_units if u["label"]).most_common(60)),
        "rules": {k: {"removed": v[0], "added": v[1], "units": v[2]} for k, v in sorted(tally["rules"].items())},
        "blocks": dict(tally["blocks"].most_common()),
        "id_only": dict(tally["id_only"].most_common()),
        "adjudicated": ADJUDICATED,
        "verdict": "clean" if not resid else "residuals",
    }
    Path(args.out + ".json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    with open(args.out + ".units.jsonl", "w", encoding="utf-8") as fo:
        for u in out_units:
            fo.write(json.dumps(u) + "\n")
    print(json.dumps({k: summary[k] for k in ("moved_units", "claimed", "residual_units", "residual_by_analyzer",
                                               "residual_reasons", "labels", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
