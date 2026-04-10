#!/usr/bin/env python3
"""Independent parser verification for KiCad schematics (TH-013 follow-up, v1.3 P1).

Walks the raw `.kicad_sch` AST using only `sexp_parser.py` from kicad-happy
(no analyzer helpers) and compares directly-observable facts against the
analyzer's output JSON. Surfaces parser bugs in analyze_schematic.py before
they corrupt any downstream detector.

**Scope:** schematic only (Sprint 1). PCB is a follow-up. Extraction facts
only, not interpretation — this verifier cannot catch detector semantic bugs
or resolved-net errors.

Usage:
    python3 validate/verify_parser.py --cross-section smoke
    python3 validate/verify_parser.py --repo owner/repo
    python3 validate/verify_parser.py --all --jobs 16
    python3 validate/verify_parser.py --report reports/parser_verification/latest.md
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Synthetic sheet-pin labels created by analyze_schematic.py:2885-2898 always
# have form `/<identifier>/<rest>` where <identifier> is the sheet UUID or
# friendly name. Identifier characters are limited (no spaces, +, =, etc.),
# so this regex excludes real logic-notation labels like `/WR + /MREQ`.
_SHEET_PIN_LABEL_RE = re.compile(r"^/[A-Za-z0-9_.-]+/")

def _is_synthetic_sheet_pin_label(name: str) -> bool:
    """True if the label name was synthesized by analyze_schematic.py from
    a (sheet ...) pin during hierarchy walking, not present in the source.

    Synthetic format: `/<sheet-id>/<rest>` where sheet-id is a UUID or
    friendly identifier (alphanumeric/underscore/dash/period only).
    Real labels that look similar but must be PRESERVED:
    - `/CE`, `/BBE` — single-slash, no second slash → kept
    - `PA1/VMUTE/3V3` — doesn't start with `/` → kept
    - `/WR + /MREQ` — has spaces and `+` between slashes, breaks the
      identifier match → kept (observed on abzman/Exidy-Sorcerer-Stuff
      in 2026-04-10)
    """
    return bool(_SHEET_PIN_LABEL_RE.match(name))

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from utils import (OUTPUTS_DIR, MANIFESTS_DIR, REPOS_DIR, list_repos,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
                   _truncate_with_hash, resolve_kicad_happy_dir)

# Import sexp_parser from kicad-happy (independent of analyzer helpers)
KICAD_HAPPY_DIR = resolve_kicad_happy_dir()
sys.path.insert(0, str(Path(KICAD_HAPPY_DIR) / "skills" / "kicad" / "scripts"))
from sexp_parser import parse_file, find_all, find_first, get_value, get_property

# Normalization rules for Sprint 1 — deliberately empty.
# When a mismatch class shows up repeatedly across the corpus and the
# difference is a documented formatting artifact (e.g., trailing whitespace,
# unicode normalization), add a rule here. Each rule must be justified in
# reports/parser_verification/normalization_rationale.md.
NORMALIZATION_RULES = {
    # "component_values": [],  # list of (regex, replacement) pairs
    # "label_names": [],
}


def _normalize(field: str, value):
    """Apply NORMALIZATION_RULES for the given field. No-op in Sprint 1."""
    return value


def _collect_power_lib_ids(root: list) -> set:
    """Walk lib_symbols and return the set of lib_ids marked `(power)`.

    The analyzer filters power symbols out of `components[]` based on the
    lib_symbol's `(power)` flag — see analyze_schematic.py:546
    `is_power_sym = sym_def.get("is_power", False)`. We mirror that exact
    rule by parsing the same `(power)` flag here, so the verifier matches
    the analyzer's component population on KiCad 6+ files.

    Pattern in source: `(symbol "Library:Name" (power) (in_bom yes) ...)`.
    """
    power_ids = set()
    lib_symbols = find_first(root, "lib_symbols")
    if not lib_symbols:
        return power_ids
    for entry in lib_symbols:
        if not isinstance(entry, list) or len(entry) < 2 or entry[0] != "symbol":
            continue
        lib_id = entry[1]
        if not isinstance(lib_id, str):
            continue
        # The (power) flag is a direct child of the symbol entry. Check both
        # bare "power" atoms and ["power"] singleton lists since sexp_parser
        # may return either depending on the source formatting.
        for child in entry[2:]:
            if child == "power" or (isinstance(child, list) and child and child[0] == "power"):
                power_ids.add(lib_id)
                break
    return power_ids


def extract_sexp_facts(root: list) -> dict:
    """Walk a parsed .kicad_sch AST and extract directly-observable facts.

    The input `root` is the output of `sexp_parser.parse_file()`. This function
    uses ONLY sexp_parser primitives — no analyze_schematic helpers. That
    independence is the whole point: if the analyzer and the verifier share
    extraction logic, verification becomes circular.

    Returns a dict with these keys (all present, even when empty):
        component_refs: set[str]          — every placed symbol's "Reference" property
        component_count: int              — count of placed symbols (excluding lib_symbols entries)
        component_values: dict[str, str]  — ref -> "Value" property (for matched refs)
        component_footprints: dict[str, str] — ref -> "Footprint" property
        label_count: int                  — total labels of all types
        label_names: set[str]             — union of names across all label types
        hierarchical_label_count: int     — count of (hierarchical_label ...) nodes only
        no_connect_count: int             — count of (no_connect ...) nodes

    Fact extraction is direct and deterministic. No classification, no
    connectivity resolution, no detector logic.
    """
    component_refs = set()
    component_values = {}
    component_footprints = {}
    component_count = 0
    label_names = set()
    label_count = 0
    hierarchical_label_count = 0
    no_connect_count = 0

    LABEL_KINDS = ("label", "global_label", "hierarchical_label", "directive_label")
    power_lib_ids = _collect_power_lib_ids(root)

    for node in root:
        if not isinstance(node, list) or not node:
            continue
        tag = node[0]
        if tag == "symbol":
            lib_id_node = find_first(node, "lib_id")
            if lib_id_node is None:
                continue
            lib_id = lib_id_node[1] if len(lib_id_node) > 1 else None
            # KH-083: KiCad 7+ may write `(lib_name "X")` alongside
            # `(lib_id "Library:Y")` and use the lib_name as the actual
            # key into lib_symbols (a flat namespace). Match the
            # analyzer at analyze_schematic.py:545 — try lib_name first.
            # Confirmed on FarrenMartinus/EMG in 2026-04-10 where the
            # placed Simulation_SPICE:0 symbol's lib_symbol is keyed as
            # "0_1" and carries the (power) flag.
            lib_name_node = find_first(node, "lib_name")
            lib_name = (lib_name_node[1] if lib_name_node is not None
                        and len(lib_name_node) > 1 else None)
            # The analyzer keeps malformed symbols (empty/missing
            # Reference) in components[] with `reference=""`. Mirror that
            # so component_count totals match. The component_refs set
            # still only holds non-empty refs since you can't compare
            # anonymous components by name. Confirmed on
            # ltwmori/designGuardDesktopApp test fixtures in 2026-04-10.
            ref = get_property(node, "Reference") or ""
            # Mirror the analyzer's power-symbol filtering. The analyzer
            # excludes anything whose `type` is `power_symbol`, `power_flag`,
            # or `flag` (analyze_schematic.py:2782-2785). Four detection
            # rules total — the first three from
            # kicad_utils.classify_component():379-396, the fourth from the
            # type_map at line 416 (`#FLG` → "flag"):
            #   1. lib_symbol carries the (power) flag
            #   2. lib_id starts with "power:" AND not in_bom (KH-080:
            #      power-prefix parts in BOM are real, e.g. DD4012SA)
            #   3. ref starts with #PWR (legacy fallback for files where
            #      KiCad version upgrades dropped the (power) flag —
            #      observed on cnlohr/cnhardware KiCad 9 files in 2026-04-10)
            #   4. ref starts with #FLG (PWR_FLAG symbols, observed on
            #      ForestHubAI/boardsmith in 2026-04-10)
            # Reference prefix alone is unreliable for the general case:
            # graphic symbols (#G1, #FRAME8) start with `#` but the analyzer
            # keeps them — only #PWR and #FLG are recognized as special.
            in_bom_node = find_first(node, "in_bom")
            in_bom = (in_bom_node is not None and len(in_bom_node) > 1
                      and in_bom_node[1] == "yes")
            is_power = (
                lib_name in power_lib_ids
                or lib_id in power_lib_ids
                or (isinstance(lib_id, str) and lib_id.startswith("power:") and not in_bom)
                or ref.startswith("#PWR")
                or ref.startswith("#FLG")
            )
            if is_power:
                continue
            component_count += 1
            if ref:  # only named refs go in the comparable set
                component_refs.add(ref)
            val = get_property(node, "Value")
            # Match the analyzer-side filter (extract_analyzer_facts): treat
            # empty string the same as missing, so both extractors return the
            # same dict shape. Skip value/footprint indexing for anonymous
            # symbols since there's no key to bind them to.
            if ref and val is not None and val != "":
                component_values[ref] = val
            fp = get_property(node, "Footprint")
            if ref and fp is not None and fp != "":
                component_footprints[ref] = fp
        elif tag in LABEL_KINDS:
            name = node[1] if len(node) > 1 else ""
            # Defensive: malformed sexps can yield nested lists as label name
            if isinstance(name, list):
                name = str(name[0]) if name else ""
            if name:
                label_names.add(name)
            label_count += 1
            if tag == "hierarchical_label":
                hierarchical_label_count += 1
        elif tag == "no_connect":
            no_connect_count += 1

    return {
        "component_refs": component_refs,
        "component_count": component_count,
        "component_values": component_values,
        "component_footprints": component_footprints,
        "label_count": label_count,
        "label_names": label_names,
        "hierarchical_label_count": hierarchical_label_count,
        "no_connect_count": no_connect_count,
    }


def extract_analyzer_facts(output: dict) -> dict:
    """Extract the same fact set from an analyzer output JSON dict.

    The keys returned match `extract_sexp_facts()` exactly, so a downstream
    comparison function can diff the two dicts directly without branching
    on the data source.

    Expects the analyzer JSON shape produced by `analyze_schematic.py`:
    - components: list of dicts with `reference`, `value`, `footprint`, ...
    - labels: list of dicts with `name`, `type`, `x`, `y`, ...
    - no_connects: list of dicts with `x`, `y`, ...

    Filters by `_sheet == 0` so we only see facts that belong to the file
    being verified. The analyzer walks hierarchical child sheets and tags
    each element with `_sheet=N` where N is the sheet index (0 = the file
    being analyzed, 1+ = walked children). Confirmed empirically in
    analyze_schematic.py:2650 and 7515 — `sheet_idx = len(sheets_parsed)`
    so the first sheet processed (the analyzed file itself) is always 0.
    Without this filter, root sheets in hierarchical projects show
    massive `extra_item` floods (e.g. bitaxeUltra: 16 sexp vs 136 analyzer).
    Cross-sheet verification is a follow-up — Sprint 1 verifies one file
    at a time against itself.
    """
    components = [c for c in (output.get("components") or []) if c.get("_sheet", 0) == 0]
    no_connects = [n for n in (output.get("no_connects") or []) if n.get("_sheet", 0) == 0]
    # Sheet-pin-stub labels are synthesized by analyze_schematic.py:2885-2898
    # for every (pin "NAME") inside a (sheet ...) block — they aren't real
    # labels in the source file. After traversal these get names of the
    # form `/<sheet-uuid>/<name>` and tagged `_sheet=0`. We filter only
    # those, using the precise UUID format match. Real labels can contain
    # slashes (alt-function pin names like `PA1/VMUTE/3V3` on
    # gav-vdm/G_Pad_Max) and can even start with a single slash
    # (`/CE`, `/BBE`, `/BEXTIO` on fachat/cbm_ultipet) — both observed
    # in 2026-04-10. The UUID regex avoids false positives.
    labels = [
        l for l in (output.get("labels") or [])
        if l.get("_sheet", 0) == 0 and not _is_synthetic_sheet_pin_label(l.get("name") or "")
    ]

    component_refs = set()
    component_values = {}
    component_footprints = {}
    for comp in components:
        ref = comp.get("reference")
        if not ref:
            continue
        component_refs.add(ref)
        val = comp.get("value")
        if val is not None and val != "":
            component_values[ref] = val
        fp = comp.get("footprint")
        if fp is not None and fp != "":
            component_footprints[ref] = fp

    label_names = set()
    label_count = 0
    hierarchical_label_count = 0
    for lbl in labels:
        label_count += 1
        name = lbl.get("name", "")
        if name:
            label_names.add(name)
        if lbl.get("type") == "hierarchical_label":
            hierarchical_label_count += 1

    return {
        "component_refs": component_refs,
        "component_count": len(components),
        "component_values": component_values,
        "component_footprints": component_footprints,
        "label_count": label_count,
        "label_names": label_names,
        "hierarchical_label_count": hierarchical_label_count,
        "no_connect_count": len(no_connects),
    }


def compare_facts(sexp_facts: dict, analyzer_facts: dict) -> list:
    """Compare two fact dicts and return a list of mismatch records.

    Each mismatch is a dict with:
        kind: str   — "missing_item" | "extra_item" | "wrong_value" | "wrong_count"
        field: str  — which fact category the mismatch is in
        detail: str — short human-readable description

    Sprint 1 uses strict comparison — no normalization. The verifier defaults
    to "the sexp is the source of truth" when they disagree, since sexp is
    closer to the raw file than any analyzer interpretation.
    """
    mismatches = []

    # Component reference set
    sexp_refs = sexp_facts["component_refs"]
    analyzer_refs = analyzer_facts["component_refs"]
    for ref in sorted(sexp_refs - analyzer_refs):
        mismatches.append({
            "kind": "missing_item",
            "field": "component_refs",
            "detail": f"sexp has component {ref}, analyzer does not",
        })
    for ref in sorted(analyzer_refs - sexp_refs):
        mismatches.append({
            "kind": "extra_item",
            "field": "component_refs",
            "detail": f"analyzer has component {ref}, sexp does not",
        })

    # Component count (redundant with ref set, but gives a direct signal)
    if sexp_facts["component_count"] != analyzer_facts["component_count"]:
        mismatches.append({
            "kind": "wrong_count",
            "field": "component_count",
            "detail": f"sexp={sexp_facts['component_count']}, analyzer={analyzer_facts['component_count']}",
        })

    # Component values (only for refs present in both)
    shared_refs = sexp_refs & analyzer_refs
    for ref in sorted(shared_refs):
        sv = sexp_facts["component_values"].get(ref)
        av = analyzer_facts["component_values"].get(ref)
        if sv is not None and av is not None and sv != av:
            mismatches.append({
                "kind": "wrong_value",
                "field": "component_values",
                "detail": f"{ref}: sexp={sv!r}, analyzer={av!r}",
            })

    # Component footprints (same pattern)
    for ref in sorted(shared_refs):
        sf = sexp_facts["component_footprints"].get(ref)
        af = analyzer_facts["component_footprints"].get(ref)
        if sf is not None and af is not None and sf != af:
            mismatches.append({
                "kind": "wrong_value",
                "field": "component_footprints",
                "detail": f"{ref}: sexp={sf!r}, analyzer={af!r}",
            })

    # Label count
    if sexp_facts["label_count"] != analyzer_facts["label_count"]:
        mismatches.append({
            "kind": "wrong_count",
            "field": "label_count",
            "detail": f"sexp={sexp_facts['label_count']}, analyzer={analyzer_facts['label_count']}",
        })

    # Label name set
    sexp_labels = sexp_facts["label_names"]
    analyzer_labels = analyzer_facts["label_names"]
    for name in sorted(sexp_labels - analyzer_labels):
        mismatches.append({
            "kind": "missing_item",
            "field": "label_names",
            "detail": f"sexp has label {name!r}, analyzer does not",
        })
    for name in sorted(analyzer_labels - sexp_labels):
        mismatches.append({
            "kind": "extra_item",
            "field": "label_names",
            "detail": f"analyzer has label {name!r}, sexp does not",
        })

    # Hierarchical label count
    if sexp_facts["hierarchical_label_count"] != analyzer_facts["hierarchical_label_count"]:
        mismatches.append({
            "kind": "wrong_count",
            "field": "hierarchical_label_count",
            "detail": f"sexp={sexp_facts['hierarchical_label_count']}, analyzer={analyzer_facts['hierarchical_label_count']}",
        })

    # No-connect count
    if sexp_facts["no_connect_count"] != analyzer_facts["no_connect_count"]:
        mismatches.append({
            "kind": "wrong_count",
            "field": "no_connect_count",
            "detail": f"sexp={sexp_facts['no_connect_count']}, analyzer={analyzer_facts['no_connect_count']}",
        })

    return mismatches


def check_schematic_file(sch_path: str, analyzer_output: dict) -> list:
    """Parse a .kicad_sch file and compare its facts against the analyzer output.

    Returns a list of mismatch records (same shape as `compare_facts()`).
    Each mismatch will be passed up to the per-repo aggregator and eventually
    written to the report.

    Parse failures (malformed sexp, missing file) are returned as a single
    mismatch of kind `parse_error` so the main loop can still proceed.
    """
    try:
        root = parse_file(sch_path)
    except Exception as e:
        return [{
            "kind": "parse_error",
            "field": "file",
            "detail": f"{sch_path}: {type(e).__name__}: {e}",
        }]
    sexp_facts = extract_sexp_facts(root)
    analyzer_facts = extract_analyzer_facts(analyzer_output)
    return compare_facts(sexp_facts, analyzer_facts)


def _check_repo(repo_pair):
    """Walker for one repo. Picklable for ProcessPoolExecutor.

    Iterates every `.kicad_sch` file in the repo's manifest, finds the matching
    analyzer JSON output in `results/outputs/schematic/{owner}/{repo}/`, and
    runs `check_schematic_file()` on the pair. Returns `(repo_name, findings)`
    where findings is a list of dicts augmented with `file` and `repo` keys.
    """
    repo, schematics = repo_pair
    repos_dir = str(REPOS_DIR)
    all_findings = []

    for sch_path in schematics:
        relpath = sch_path
        if sch_path.startswith(repos_dir):
            relpath = sch_path[len(repos_dir):].lstrip("/").lstrip(os.sep)

        parts = relpath.replace("\\", "/").split("/", 2)
        if len(parts) < 3:
            continue
        owner = parts[0]
        repo_name = parts[1]
        within_repo = parts[2]
        safe_name = _truncate_with_hash(within_repo.replace(os.sep, "_").replace("/", "_"))

        json_path = OUTPUTS_DIR / "schematic" / owner / repo_name / f"{safe_name}.json"
        if not json_path.exists():
            # No analyzer output — not this tool's concern. Skip silently.
            continue

        try:
            analyzer_output = json.loads(json_path.read_text())
        except Exception as e:
            all_findings.append({
                "kind": "parse_error",
                "field": "analyzer_output",
                "detail": f"{json_path}: {type(e).__name__}: {e}",
                "file": sch_path,
                "repo": repo,
            })
            continue

        findings = check_schematic_file(sch_path, analyzer_output)
        for f in findings:
            f["file"] = sch_path
            f["repo"] = repo
            all_findings.append(f)

    return repo, all_findings


def _write_report(all_findings: list, total_files: int, total_repos: int,
                  report_path: Path) -> None:
    """Write a markdown report of all findings to the given path.

    The report groups findings by mismatch kind, then by repo, with concrete
    examples for each class. This is the primary artifact human maintainers
    use to decide what to file as KH-* issues.
    """
    by_kind = defaultdict(list)
    by_repo = defaultdict(list)
    for f in all_findings:
        by_kind[f["kind"]].append(f)
        by_repo[f["repo"]].append(f)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as out:
        out.write("# Parser Verification Report (v1.3 P1)\n\n")
        out.write("**Scope:** schematic only. Extraction facts only — NOT interpretation.\n")
        out.write(f"**Limitation:** this report only catches extraction bugs. ")
        out.write("Detector semantic errors, cross-sheet connectivity, and ")
        out.write("wrong classifications are out of scope.\n\n")

        out.write("## Summary\n\n")
        out.write(f"- Files checked: {total_files}\n")
        out.write(f"- Repos checked: {total_repos}\n")
        out.write(f"- Total mismatches: {len(all_findings)}\n")
        out.write(f"- Repos with mismatches: {len(by_repo)}\n\n")

        out.write("### By mismatch kind\n\n")
        for kind in sorted(by_kind.keys()):
            out.write(f"- **{kind}**: {len(by_kind[kind])}\n")
        out.write("\n")

        out.write("## Mismatches by kind\n\n")
        for kind in sorted(by_kind.keys()):
            out.write(f"### {kind} ({len(by_kind[kind])})\n\n")
            # Show up to 10 examples per kind
            for f in by_kind[kind][:10]:
                out.write(f"- `{f['repo']}` — `{os.path.basename(f['file'])}` — ")
                out.write(f"{f['field']}: {f['detail']}\n")
            if len(by_kind[kind]) > 10:
                out.write(f"- *...and {len(by_kind[kind]) - 10} more*\n")
            out.write("\n")

        out.write("## Top offending repos\n\n")
        sorted_repos = sorted(by_repo.items(), key=lambda x: -len(x[1]))[:20]
        for repo, findings in sorted_repos:
            out.write(f"- `{repo}`: {len(findings)} mismatches\n")
        out.write("\n")

        out.write("---\n\n")
        out.write("## Next steps\n\n")
        out.write("1. For each mismatch class with 10+ occurrences: file as a KH-* issue ")
        out.write("in ISSUES.md, including the field name and a representative example.\n")
        out.write("2. Fix parser bugs on the kicad-happy side before proceeding to P4 ")
        out.write("(synthetic detector fixtures). Parser bugs poison downstream detectors.\n")
        out.write("3. Re-run this verifier after any kicad-happy parser change to confirm fixes.\n")


def main():
    ap = argparse.ArgumentParser(
        description="Independent parser verification for .kicad_sch files (v1.3 P1).",
    )
    add_repo_filter_args(ap)
    ap.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                    help=f"Parallel workers (default: {DEFAULT_JOBS})")
    ap.add_argument("--report", type=str,
                    default="reports/parser_verification/latest.md",
                    help="Markdown report output path (default: reports/parser_verification/latest.md)")
    ap.add_argument("--summary", action="store_true",
                    help="Print summary counts only, not individual findings")
    ap.add_argument("--json", action="store_true",
                    help="JSON output to stdout (suppresses markdown report)")
    args = ap.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()

    schematics_list = MANIFESTS_DIR / "all_schematics.txt"
    if not schematics_list.exists():
        print(f"Error: {schematics_list} not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    with open(schematics_list) as f:
        all_schematics = [line.strip() for line in f if line.strip()]

    # Filter to KiCad 6+ .kicad_sch files only. Legacy `.sch` files (KiCad 5)
    # use a non-S-expression format that sexp_parser cannot read. Verifying
    # them would require a separate parser that shares code with
    # analyze_schematic's legacy path — explicitly out of scope for Sprint 1.
    all_schematics = [s for s in all_schematics if s.endswith(".kicad_sch")]

    repos_dir = str(REPOS_DIR)
    repo_set = set(repos)
    by_repo = defaultdict(list)
    for s in all_schematics:
        relpath = s
        if s.startswith(repos_dir):
            relpath = s[len(repos_dir):].lstrip("/").lstrip(os.sep)
        parts = relpath.replace("\\", "/").split("/")
        if len(parts) >= 2:
            repo_name = f"{parts[0]}/{parts[1]}"
        else:
            repo_name = parts[0]
        if repo_name in repo_set:
            by_repo[repo_name].append(s)

    total_files = sum(len(v) for v in by_repo.values())
    work_items = list(by_repo.items())

    all_findings = []
    jobs = args.jobs

    if jobs > 1 and len(work_items) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(work_items))) as pool:
            futures = {pool.submit(_check_repo, item): item[0] for item in work_items}
            for future in as_completed(futures):
                _repo, findings = future.result()
                all_findings.extend(findings)
    else:
        for item in work_items:
            _repo, findings = _check_repo(item)
            all_findings.extend(findings)

    affected_repos = len({f["repo"] for f in all_findings})

    if args.json:
        output = {
            "files_checked": total_files,
            "repos_checked": len(by_repo),
            "total_mismatches": len(all_findings),
            "repos_with_mismatches": affected_repos,
            "mismatches": all_findings,
        }
        print(json.dumps(output, indent=2))
        return

    # Write the markdown report. Pass `len(by_repo)` as total_repos so the
    # Summary section can distinguish "how many repos were checked" from
    # "how many had mismatches" (the latter is derived from all_findings
    # inside _write_report).
    report_path = HARNESS_DIR / args.report
    _write_report(all_findings, total_files, len(by_repo), report_path)

    # Print summary to stdout
    print(f"Parser verification: {total_files} files checked across {len(by_repo)} repos")
    print(f"Total mismatches: {len(all_findings)} ({affected_repos} repos affected)")
    print(f"Report: {report_path.relative_to(HARNESS_DIR)}")

    if all_findings and not args.summary:
        by_kind = defaultdict(int)
        for f in all_findings:
            by_kind[f["kind"]] += 1
        print("\nBy kind:")
        for kind, count in sorted(by_kind.items(), key=lambda x: -x[1]):
            print(f"  {kind}: {count}")

    sys.exit(0 if not all_findings else 2)


if __name__ == "__main__":
    main()
