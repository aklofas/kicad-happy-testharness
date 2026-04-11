#!/usr/bin/env python3
"""Generate a searchable metadata catalog for all repos in the test corpus.

Scans analyzer outputs to build per-repo metadata including KiCad versions,
complexity metrics, multi-axis quality scores, design domains, and tags.
Outputs reference/repo_catalog.json + reference/repo_catalog.md.

Usage:
    python3 generate_catalog.py                              # Generate catalog
    python3 generate_catalog.py --repo hackrf                # One repo only
    python3 generate_catalog.py --json                       # Print JSON to stdout
    python3 generate_catalog.py --query "kicad_generation=kicad9"
    python3 generate_catalog.py --query "category=ESP32"
    python3 generate_catalog.py --query "tags contains rf"
    python3 generate_catalog.py --query "quality.emc>70"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import OUTPUTS_DIR, DATA_DIR, list_repos, safe_load_json
CATALOG_JSON = DATA_DIR / "repo_catalog.json"
CATALOG_MD = DATA_DIR / "repo_catalog.md"
REPOS_MD = HARNESS_DIR / "repos.md"


# --- KiCad generation mapping ---

def _classify_generation(file_version, kicad_version=""):
    """Map file_version string to a KiCad generation bucket."""
    if kicad_version and "legacy" in kicad_version.lower():
        return "kicad5"
    fv = str(file_version)
    if fv in ("3", "4"):
        return "kicad5"
    try:
        n = int(fv)
    except (ValueError, TypeError):
        return "unknown"
    if n < 20220101:
        return "kicad6"
    if n < 20231212:
        return "kicad7"
    if n < 20250101:
        return "kicad8"
    if n < 20260101:
        return "kicad9"
    return "kicad10"


# --- Category parsing ---

def _load_categories():
    """Parse repos.md section headers to build {repo_name: category} mapping.

    repos.md is organized with '## Category' headers followed by repo URLs.
    Each repo inherits the category of its section.
    """
    cats = {}
    current_category = "Uncategorized"
    try:
        text = REPOS_MD.read_text(encoding="utf-8")
    except OSError:
        return cats
    for line in text.splitlines():
        if line.startswith("## "):
            current_category = line[3:].strip()
            continue
        if line.strip().startswith("- http"):
            url = line.strip()[2:].split(" @")[0].split(" (")[0].strip()
            parts = url.rstrip("/").removesuffix(".git").split("/")
            if len(parts) >= 2:
                repo_name = f"{parts[-2]}/{parts[-1]}"
                cats[repo_name] = current_category
    return cats


def _load_repo_urls():
    """Parse repos.md to build {repo_name: {url, hash}} mapping."""
    from checkout import parse_repos_md
    repos = parse_repos_md(REPOS_MD)
    mapping = {}
    for r in repos:
        url = r["url"]
        parts = url.rstrip("/").removesuffix(".git").split("/")
        name = f"{parts[-2]}/{parts[-1]}"
        mapping[name] = {"url": url, "hash": r.get("hash", "")}
    return mapping


# --- Quality scoring ---

def _score_emc(emc_outputs):
    """EMC quality score (0-100). Higher = fewer/less severe findings."""
    if not emc_outputs:
        return None
    total_risk = 0
    count = 0
    for data in emc_outputs:
        summary = data.get("summary", {})
        risk = summary.get("emc_risk_score")
        if risk is not None:
            total_risk += risk
            count += 1
    if count == 0:
        return None
    avg_risk = total_risk / count
    return max(0, min(100, round(100 - avg_risk)))


def _score_bom(sch_outputs):
    """BOM quality score (0-100). Higher = more ICs have MPN + footprint."""
    total_ics = 0
    ics_with_mpn = 0
    ics_with_fp = 0
    for data in sch_outputs:
        for comp in data.get("bom", []):
            if comp.get("type") == "ic" or comp.get("type") == "microcontroller":
                qty = comp.get("quantity", 1)
                total_ics += qty
                if comp.get("mpn"):
                    ics_with_mpn += qty
                if comp.get("footprint"):
                    ics_with_fp += qty
    if total_ics == 0:
        return None
    mpn_ratio = ics_with_mpn / total_ics
    fp_ratio = ics_with_fp / total_ics
    return round((mpn_ratio * 60 + fp_ratio * 40))


def _score_routing(pcb_outputs):
    """Routing quality score (0-100). Higher = more completely routed."""
    if not pcb_outputs:
        return None
    scores = []
    for data in pcb_outputs:
        stats = data.get("statistics", {})
        if stats.get("routing_complete"):
            scores.append(100)
        else:
            unrouted = stats.get("unrouted_net_count", 0)
            total_nets = stats.get("net_count", 1)
            if total_nets > 0:
                scores.append(round(max(0, (1 - unrouted / total_nets) * 100)))
    return round(sum(scores) / len(scores)) if scores else None


def _score_completeness(has_sch, has_pcb, has_gerber, has_spice, has_emc):
    """Completeness score (0-100). Higher = more output types present."""
    parts = [
        (has_sch, 30),
        (has_pcb, 30),
        (has_gerber, 20),
        (has_spice, 10),
        (has_emc, 10),
    ]
    return sum(w for present, w in parts if present)


def _score_documentation(sch_outputs):
    """Documentation score (0-100). Higher = better title block coverage."""
    if not sch_outputs:
        return None
    scores = []
    for data in sch_outputs:
        tb = data.get("title_block", {})
        score = 0
        if tb.get("title"):
            score += 40
        if tb.get("date"):
            score += 30
        if tb.get("rev"):
            score += 30
        scores.append(score)
    return round(sum(scores) / len(scores)) if scores else None


# --- Tag generation ---

def _generate_tags(entry):
    """Generate searchable tags from catalog entry."""
    tags = []

    # KiCad generation
    gen = entry.get("kicad_generation", "")
    if gen == "kicad5":
        tags.append("legacy_schematic")
    if gen:
        tags.append(gen)

    # Layer count
    layers = entry.get("complexity", {}).get("pcb_layers_max", 0)
    if layers:
        tags.append(f"{layers}_layer")

    # Data availability
    if entry.get("gerber_dirs", 0) > 0:
        tags.append("has_gerbers")
    if entry.get("pcb_files", 0) > 0:
        tags.append("has_pcb")
    if entry.get("spice_summary", {}).get("total_simulations", 0) > 0:
        tags.append("has_spice")
    if entry.get("emc_summary", {}).get("total_findings", 0) > 0:
        tags.append("has_emc")

    # Size
    comps = entry.get("complexity", {}).get("total_components", 0)
    if comps < 20:
        tags.append("small")
    elif comps < 200:
        tags.append("medium")
    elif comps < 1000:
        tags.append("large")
    else:
        tags.append("xlarge")

    # Design domains
    domains = entry.get("design_domains", [])
    if any(d in domains for d in ("rf_chains", "rf_matching")):
        tags.append("rf")
    if any(d in domains for d in ("power_regulators", "feedback_networks")):
        tags.append("power")
    if any(d in domains for d in ("ethernet_interfaces", "hdmi_dvi_interfaces",
                                   "memory_interfaces")):
        tags.append("digital_interfaces")
    if any(d in domains for d in ("key_matrices",)):
        tags.append("keyboard")
    if any(d in domains for d in ("opamp_circuits",)):
        tags.append("analog")
    if any(d in domains for d in ("bridge_circuits",)):
        tags.append("motor_driver")

    # Hierarchical
    if entry.get("complexity", {}).get("sheets", 0) > 1:
        tags.append("hierarchical")

    return sorted(set(tags))


# --- Main catalog builder ---

def build_repo_entry(repo_name, categories, repo_urls):
    """Build a complete catalog entry for one repo."""
    entry = {
        "repo": repo_name,
        "url": repo_urls.get(repo_name, {}).get("url", ""),
        "hash": repo_urls.get(repo_name, {}).get("hash", ""),
        "category": categories.get(repo_name, "Uncategorized"),
    }

    # Collect all outputs
    sch_outputs = []
    sch_dir = OUTPUTS_DIR / "schematic" / repo_name
    if sch_dir.exists():
        for f in sch_dir.glob("*.json"):
            data = safe_load_json(f, {})
            if data:
                sch_outputs.append(data)

    pcb_outputs = []
    pcb_dir = OUTPUTS_DIR / "pcb" / repo_name
    if pcb_dir.exists():
        for f in pcb_dir.glob("*.json"):
            data = safe_load_json(f, {})
            if data:
                pcb_outputs.append(data)

    emc_outputs = []
    emc_dir = OUTPUTS_DIR / "emc" / repo_name
    if emc_dir.exists():
        for f in emc_dir.glob("*.json"):
            data = safe_load_json(f, {})
            if data:
                emc_outputs.append(data)

    spice_outputs = []
    spice_dir = OUTPUTS_DIR / "spice" / repo_name
    if spice_dir.exists():
        for f in spice_dir.glob("*.json"):
            data = safe_load_json(f, {})
            if data:
                spice_outputs.append(data)

    gerber_dir = OUTPUTS_DIR / "gerber" / repo_name
    gerber_count = len(list(gerber_dir.glob("*.json"))) if gerber_dir.exists() else 0

    # KiCad versions
    versions = set()
    file_versions = set()
    for data in sch_outputs + pcb_outputs:
        v = data.get("kicad_version", "")
        fv = data.get("file_version", "")
        if v:
            versions.add(v)
        if fv:
            file_versions.add(str(fv))

    generations = set()
    for data in sch_outputs + pcb_outputs:
        gen = _classify_generation(
            data.get("file_version", ""),
            data.get("kicad_version", ""))
        if gen != "unknown":
            generations.add(gen)

    if len(generations) > 1:
        entry["kicad_generation"] = "mixed"
    elif generations:
        entry["kicad_generation"] = generations.pop()
    else:
        entry["kicad_generation"] = "unknown"

    entry["kicad_versions"] = sorted(versions)
    entry["file_versions"] = sorted(file_versions)

    # File counts
    entry["projects"] = len(set(
        f.stem.rsplit(".", 1)[0] if "." in f.stem else f.stem
        for f in (list(sch_dir.glob("*.json")) if sch_dir.exists() else [])
    ))
    entry["schematic_files"] = len(sch_outputs)
    entry["pcb_files"] = len(pcb_outputs)
    entry["gerber_dirs"] = gerber_count

    # Complexity
    total_comps = sum(d.get("statistics", {}).get("total_components", 0) for d in sch_outputs)
    unique_parts = sum(d.get("statistics", {}).get("unique_parts", 0) for d in sch_outputs)
    total_nets = sum(d.get("statistics", {}).get("total_nets", 0) for d in sch_outputs)
    sheets = len(sch_outputs)

    pcb_layers = [d.get("statistics", {}).get("copper_layers_used", 0) for d in pcb_outputs]
    board_areas = [d.get("statistics", {}).get("board_area_mm2") or 0 for d in pcb_outputs]
    smd_counts = sum(d.get("statistics", {}).get("smd_count", 0) for d in pcb_outputs)
    tht_counts = sum(d.get("statistics", {}).get("tht_count", 0) for d in pcb_outputs)

    # Max hierarchical sheets in any single project (from hierarchy_context)
    max_hierarchy_sheets = 0
    for data in sch_outputs:
        hc = data.get("hierarchy_context")
        if isinstance(hc, dict):
            sip = hc.get("sheets_in_project", [])
            if isinstance(sip, list) and len(sip) > max_hierarchy_sheets:
                max_hierarchy_sheets = len(sip)

    entry["complexity"] = {
        "total_components": total_comps,
        "unique_parts": unique_parts,
        "total_nets": total_nets,
        "pcb_layers_max": max(pcb_layers) if pcb_layers else 0,
        "board_area_mm2_max": round(max(board_areas), 1) if board_areas else 0,
        "sheets": sheets,
        "max_hierarchy_sheets": max_hierarchy_sheets,
        "smd_ratio": round(smd_counts / (smd_counts + tht_counts), 2)
            if (smd_counts + tht_counts) > 0 else 0,
    }

    # Design domains (detectors that fired)
    detectors_fired = {}
    for data in sch_outputs:
        sa = data.get("signal_analysis", {})
        for det, items in sa.items():
            count = 0
            if isinstance(items, list):
                count = len(items)
            elif isinstance(items, dict):
                count = 1 if items else 0
            if count > 0:
                detectors_fired[det] = detectors_fired.get(det, 0) + count

    entry["design_domains"] = sorted(d for d, c in detectors_fired.items() if c > 0)
    entry["detectors_fired"] = dict(sorted(detectors_fired.items()))

    # EMC summary
    emc_findings = 0
    emc_critical = emc_high = emc_medium = emc_low = 0
    emc_risks = []
    for data in emc_outputs:
        s = data.get("summary", {})
        emc_findings += s.get("total_checks", 0)
        emc_critical += s.get("critical", 0)
        emc_high += s.get("high", 0)
        emc_medium += s.get("medium", 0)
        emc_low += s.get("low", 0)
        risk = s.get("emc_risk_score")
        if risk is not None:
            emc_risks.append(risk)

    entry["emc_summary"] = {
        "total_findings": emc_findings,
        "critical": emc_critical,
        "high": emc_high,
        "medium": emc_medium,
        "low": emc_low,
        "risk_score_avg": round(sum(emc_risks) / len(emc_risks)) if emc_risks else None,
    }

    # SPICE summary
    spice_total = spice_pass = spice_warn = spice_fail = 0
    for data in spice_outputs:
        s = data.get("summary", {})
        spice_total += s.get("total", 0)
        spice_pass += s.get("pass", 0)
        spice_warn += s.get("warn", 0)
        spice_fail += s.get("fail", 0)

    entry["spice_summary"] = {
        "total_simulations": spice_total,
        "pass": spice_pass,
        "warn": spice_warn,
        "fail": spice_fail,
    }

    # Assertion counts
    repo_ref = DATA_DIR / repo_name
    assertion_total = 0
    if repo_ref.exists():
        for af in repo_ref.rglob("assertions/*/*.json"):
            data = safe_load_json(af, {})
            assertion_total += len(data.get("assertions", []))

    entry["assertions"] = {"total": assertion_total}

    # Quality scores
    has_sch = len(sch_outputs) > 0
    has_pcb = len(pcb_outputs) > 0
    has_gerber = gerber_count > 0
    has_spice = spice_total > 0
    has_emc = emc_findings > 0

    entry["quality"] = {
        "emc": _score_emc(emc_outputs),
        "bom": _score_bom(sch_outputs),
        "routing": _score_routing(pcb_outputs),
        "completeness": _score_completeness(has_sch, has_pcb, has_gerber, has_spice, has_emc),
        "documentation": _score_documentation(sch_outputs),
    }

    # Tags
    entry["tags"] = _generate_tags(entry)

    return entry


def build_catalog(repo_filter=None):
    """Build the full catalog."""
    categories = _load_categories()
    repo_urls = _load_repo_urls()

    repos = [repo_filter] if repo_filter else list_repos()
    catalog = []
    for i, repo in enumerate(repos, 1):
        if i % 100 == 0:
            print(f"  Processing {i}/{len(repos)}...", file=sys.stderr)
        entry = build_repo_entry(repo, categories, repo_urls)
        catalog.append(entry)

    return sorted(catalog, key=lambda e: e["repo"].lower())


# --- Query engine ---

def _resolve_field(entry, field_path):
    """Resolve dotted field path against a catalog entry."""
    parts = field_path.split(".")
    val = entry
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            return None
    return val


def _parse_query(query_str):
    """Parse a query string into a list of (field, op, value) tuples."""
    clauses = []
    for part in query_str.split(" AND "):
        part = part.strip()
        if " in " in part:
            value, field = part.split(" in ", 1)
            clauses.append((field.strip(), "in", value.strip()))
        elif " contains " in part:
            field, value = part.split(" contains ", 1)
            clauses.append((field.strip(), "contains", value.strip()))
        elif ">=" in part:
            field, value = part.split(">=", 1)
            clauses.append((field.strip(), ">=", float(value.strip())))
        elif ">" in part:
            field, value = part.split(">", 1)
            clauses.append((field.strip(), ">", float(value.strip())))
        elif "<=" in part:
            field, value = part.split("<=", 1)
            clauses.append((field.strip(), "<=", float(value.strip())))
        elif "<" in part:
            field, value = part.split("<", 1)
            clauses.append((field.strip(), "<", float(value.strip())))
        elif "=" in part:
            field, value = part.split("=", 1)
            clauses.append((field.strip(), "=", value.strip()))
    return clauses


def _match_entry(entry, clauses):
    """Check if a catalog entry matches all query clauses."""
    for field, op, value in clauses:
        actual = _resolve_field(entry, field)
        if op == "=" and str(actual) != str(value):
            return False
        elif op == ">" and (actual is None or actual <= value):
            return False
        elif op == ">=" and (actual is None or actual < value):
            return False
        elif op == "<" and (actual is None or actual >= value):
            return False
        elif op == "<=" and (actual is None or actual > value):
            return False
        elif op == "in" and (not isinstance(actual, list) or value not in actual):
            return False
        elif op == "contains" and (not isinstance(actual, list) or value not in actual):
            return False
    return True


def query_catalog(catalog, query_str):
    """Filter catalog entries by query string."""
    clauses = _parse_query(query_str)
    return [e for e in catalog if _match_entry(e, clauses)]


# --- Rendering ---

def render_markdown(catalog):
    """Render catalog as markdown."""
    lines = []
    lines.append("# Repo Catalog")
    lines.append("")
    lines.append(f"{len(catalog)} repos | Generated {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    # Generation summary
    gen_counts = {}
    for e in catalog:
        g = e.get("kicad_generation", "unknown")
        gen_counts[g] = gen_counts.get(g, 0) + 1

    lines.append("## KiCad Generations")
    lines.append("")
    lines.append("| Generation | Count |")
    lines.append("|-----------|------:|")
    for g, c in sorted(gen_counts.items()):
        lines.append(f"| {g} | {c} |")
    lines.append("")

    # Category summary
    cat_counts = {}
    for e in catalog:
        c = e.get("category", "Uncategorized")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    lines.append("## Categories")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|------:|")
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {c} | {n} |")
    lines.append("")

    # Tag summary
    tag_counts = {}
    for e in catalog:
        for t in e.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    lines.append("## Tags")
    lines.append("")
    lines.append("| Tag | Count |")
    lines.append("|-----|------:|")
    for t, n in sorted(tag_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {n} |")
    lines.append("")

    # Repo table
    lines.append("## Repos")
    lines.append("")
    lines.append("| Repo | Category | KiCad | Components | Layers | EMC | BOM | Routing | Tags |")
    lines.append("|------|----------|-------|----------:|-------:|----:|----:|--------:|------|")
    for e in catalog:
        repo = e["repo"]
        cat = e.get("category", "")[:20]
        gen = e.get("kicad_generation", "?")
        comps = e.get("complexity", {}).get("total_components", 0)
        layers = e.get("complexity", {}).get("pcb_layers_max", 0)
        q = e.get("quality", {})
        emc = q.get("emc") if q.get("emc") is not None else "-"
        bom = q.get("bom") if q.get("bom") is not None else "-"
        routing = q.get("routing") if q.get("routing") is not None else "-"
        tags = ", ".join(e.get("tags", [])[:4])
        lines.append(f"| {repo} | {cat} | {gen} | {comps} | {layers or '-'} | {emc} | {bom} | {routing} | {tags} |")

    lines.append("")
    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Generate searchable metadata catalog for test repos")
    parser.add_argument("--repo", help="Generate for one repo only")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--query", help="Filter repos by query (e.g., 'category=ESP32')")
    args = parser.parse_args()

    if args.query:
        # Query existing catalog
        if not CATALOG_JSON.exists():
            print(f"No catalog at {CATALOG_JSON}. Run without --query first.",
                  file=sys.stderr)
            sys.exit(1)
        catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        results = query_catalog(catalog, args.query)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"{len(results)} repos matching: {args.query}")
            for e in results:
                print(f"  {e['repo']}")
        return

    print(f"Building catalog...", file=sys.stderr)
    catalog = build_catalog(repo_filter=args.repo)

    if args.json:
        print(json.dumps(catalog, indent=2))
        return

    if not args.repo:
        # Write files
        CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_JSON.write_text(json.dumps(catalog, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        md = render_markdown(catalog)
        CATALOG_MD.write_text(md, encoding="utf-8")
        print(f"Catalog: {len(catalog)} repos")
        print(f"  JSON: {CATALOG_JSON}")
        print(f"  Markdown: {CATALOG_MD}")
    else:
        print(json.dumps(catalog[0] if catalog else {}, indent=2))


if __name__ == "__main__":
    main()
