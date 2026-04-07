#!/usr/bin/env python3
"""Human-in-the-loop figure review tool for kidoc generators.

Runs a single generator across auto-selected corpus repos, serves a numbered
gallery in the browser, and accepts terminal feedback for iterative refinement.

Usage:
    python3 tools/figure_review.py --list
    python3 tools/figure_review.py --generator power_tree
    python3 tools/figure_review.py --generator power_tree --reuse-repos
    python3 tools/figure_review.py --generator power_tree --count 20
    python3 tools/figure_review.py --generator power_tree --repo owner/repo

Prerequisites:
    Relevant analyzer outputs must exist in results/outputs/ (run the analyzers first).

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import time
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Dict, List, Optional, Tuple

# Test harness utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, REPOS_DIR, resolve_kicad_happy_dir,
                   list_repos, safe_load_json)

# kicad-happy figure system — added to sys.path after resolution
_kicad_happy = resolve_kicad_happy_dir()
_kidoc_scripts = _kicad_happy / "skills" / "kidoc" / "scripts"
sys.path.insert(0, str(_kidoc_scripts))
from figures.registry import get_registry, check_requires, GeneratorEntry
from figures.lib.theme import FigureTheme

REVIEW_DIR = Path(__file__).resolve().parent.parent / "results" / "figure_review"

# Maps generator names to (output_type, check_function) pairs.
# check_function(data) -> int: returns a "richness" score (0 = not applicable).
# The output_type tells which results/outputs/{type}/ directory to scan.

def _count_signal(data: dict, detector_name: str) -> int:
    """Count hits for a detector in signal_analysis."""
    sa = data.get("signal_analysis", {})
    hits = sa.get(detector_name, [])
    return len(hits) if isinstance(hits, list) else 0


def _check_power_tree(data: dict) -> int:
    return _count_signal(data, "power_regulators")


def _check_architecture(data: dict) -> int:
    stats = data.get("statistics", {})
    count = stats.get("total_components", 0)
    return count if count > 5 else 0


def _check_bus_topology(data: dict) -> int:
    total = 0
    for det in ("i2c_buses", "spi_buses", "uart_interfaces", "can_interfaces"):
        total += _count_signal(data, det)
    return total


def _check_pinout(data: dict) -> int:
    return _count_signal(data, "connectors")


def _check_schematic_overview(data: dict) -> int:
    # Any schematic output qualifies
    return 1 if data.get("statistics") else 0


def _check_schematic_crop(data: dict) -> int:
    sa = data.get("signal_analysis", {})
    return sum(1 for v in sa.values() if isinstance(v, list) and v)


def _check_has_data(data: dict) -> int:
    """Generic check: output exists and has content."""
    return 1 if data else 0


# (output_type_to_scan, checker_function)
GENERATOR_SIGNAL_MAP: Dict[str, Tuple[str, callable]] = {
    "power_tree":          ("schematic", _check_power_tree),
    "architecture":        ("schematic", _check_architecture),
    "bus_topology":        ("schematic", _check_bus_topology),
    "pinouts":             ("schematic", _check_pinout),
    "schematic_overview":  ("schematic", _check_schematic_overview),
    "schematic_crop":      ("schematic", _check_schematic_crop),
    "thermal_margin":      ("emc",       _check_has_data),
    "emc_severity":        ("emc",       _check_has_data),
    "spice_validation":    ("spice",     _check_has_data),
    "monte_carlo":         ("spice",     _check_has_data),
    "pcb_views":           ("pcb",       _check_has_data),
}


def select_repos(generator_name: str, count: int) -> List[Dict]:
    """Auto-select repos that exercise the given generator.

    Returns:
        List of dicts: [{"repo": "owner/repo", "output_file": Path,
                         "richness": int}, ...]
        Sorted by richness descending, capped at count, with diversity spread.
    """
    mapping = GENERATOR_SIGNAL_MAP.get(generator_name)
    if mapping is None:
        print(f"Warning: no signal mapping for '{generator_name}', "
              f"falling back to schematic outputs", file=sys.stderr)
        mapping = ("schematic", _check_has_data)

    output_type, checker = mapping
    output_dir = OUTPUTS_DIR / output_type
    if not output_dir.exists():
        print(f"Error: no {output_type} outputs found at {output_dir}. "
              f"Run the {output_type} analyzer first.", file=sys.stderr)
        sys.exit(1)

    # Scan all output files
    candidates = []
    for json_file in sorted(output_dir.rglob("*.json")):
        # Skip timing/metadata files
        if json_file.name.startswith("_"):
            continue
        data = safe_load_json(json_file)
        if data is None:
            continue
        score = checker(data)
        if score > 0:
            # Derive repo name from path: outputs/{type}/{owner}/{repo}/{file}.json
            rel = json_file.relative_to(output_dir)
            parts = rel.parts
            if len(parts) >= 3:
                repo = f"{parts[0]}/{parts[1]}"
            else:
                continue
            candidates.append({
                "repo": repo,
                "output_file": str(json_file),
                "richness": score,
                "project_file": json_file.name,
            })

    if not candidates:
        print(f"No repos found with data for generator '{generator_name}'.",
              file=sys.stderr)
        sys.exit(1)

    # Deduplicate: keep the richest output per repo
    best_per_repo: Dict[str, Dict] = {}
    for c in candidates:
        key = c["repo"]
        if key not in best_per_repo or c["richness"] > best_per_repo[key]["richness"]:
            best_per_repo[key] = c
    candidates = sorted(best_per_repo.values(), key=lambda x: x["richness"],
                        reverse=True)

    # Diversity spread: split into thirds by richness, pick evenly
    if len(candidates) <= count:
        selected = candidates
    else:
        third = len(candidates) // 3
        complex_pool = candidates[:third] or candidates[:1]
        medium_pool = candidates[third:2*third] or candidates[:1]
        simple_pool = candidates[2*third:] or candidates[:1]

        per_tier = count // 3
        remainder = count - per_tier * 3

        selected = (complex_pool[:per_tier + remainder]
                    + medium_pool[:per_tier]
                    + simple_pool[:per_tier])
        # Trim to exact count
        selected = selected[:count]

    print(f"Selected {len(selected)} repos "
          f"(from {len(best_per_repo)} candidates)", file=sys.stderr)
    return selected


def manual_repos(repo_names: List[str], generator_name: str) -> List[Dict]:
    """Build selection from manually specified repo names."""
    mapping = GENERATOR_SIGNAL_MAP.get(generator_name,
                                        ("schematic", _check_has_data))
    output_type, checker = mapping
    output_dir = OUTPUTS_DIR / output_type

    selected = []
    for repo in repo_names:
        repo_dir = output_dir / repo
        if not repo_dir.exists():
            print(f"Warning: no {output_type} outputs for '{repo}', skipping",
                  file=sys.stderr)
            continue
        for json_file in sorted(repo_dir.glob("*.json")):
            if json_file.name.startswith("_"):
                continue
            data = safe_load_json(json_file)
            if data is None:
                continue
            score = checker(data)
            selected.append({
                "repo": repo,
                "output_file": str(json_file),
                "richness": score,
                "project_file": json_file.name,
            })
    if not selected:
        print(f"Error: no qualifying outputs for specified repos.",
              file=sys.stderr)
        sys.exit(1)
    return selected


SELECTION_FILE = REVIEW_DIR / "selection.json"


def save_selection(selection: List[Dict]) -> None:
    """Save repo selection to disk for --reuse-repos."""
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with open(SELECTION_FILE, "w") as f:
        json.dump(selection, f, indent=2)


def load_selection() -> List[Dict]:
    """Load previous repo selection."""
    if not SELECTION_FILE.exists():
        print("Error: no previous selection found. "
              "Run without --reuse-repos first.", file=sys.stderr)
        sys.exit(1)
    with open(SELECTION_FILE) as f:
        return json.load(f)


def load_analysis(repo: str, output_file: str) -> dict:
    """Load and merge all available analyzer outputs for a repo into
    the unified analysis dict that kidoc generators expect.

    The primary output is loaded from output_file. Supplemental outputs
    (PCB, EMC, SPICE) are merged if available.
    """
    analysis = safe_load_json(output_file, {})

    # Try to find and merge supplemental outputs
    repo_dir_sch = OUTPUTS_DIR / "schematic" / repo
    repo_dir_pcb = OUTPUTS_DIR / "pcb" / repo
    repo_dir_emc = OUTPUTS_DIR / "emc" / repo
    repo_dir_spice = OUTPUTS_DIR / "spice" / repo

    # If primary wasn't schematic, try to load schematic as base
    if "signal_analysis" not in analysis:
        for f in sorted(repo_dir_sch.glob("*.json")) if repo_dir_sch.exists() else []:
            if not f.name.startswith("_"):
                sch_data = safe_load_json(f)
                if sch_data and "signal_analysis" in sch_data:
                    # Merge schematic under analysis, don't overwrite primary
                    merged = dict(sch_data)
                    merged.update(analysis)
                    analysis = merged
                    break

    # Merge PCB, EMC, SPICE if available
    for supplemental_dir in (repo_dir_pcb, repo_dir_emc, repo_dir_spice):
        if supplemental_dir.exists():
            for f in sorted(supplemental_dir.glob("*.json")):
                if not f.name.startswith("_"):
                    sup = safe_load_json(f)
                    if sup:
                        analysis.update(sup)
                    break  # one file per type is enough

    # Augment with file paths (generators may use these)
    repo_path = REPOS_DIR / repo
    if repo_path.exists():
        for sch in repo_path.rglob("*.kicad_sch"):
            analysis["_sch_path"] = str(sch)
            break
        for pcb in repo_path.rglob("*.kicad_pcb"):
            analysis["_pcb_path"] = str(pcb)
            break

    return analysis


def generate_figure(entry: GeneratorEntry, selection_item: dict,
                    theme: FigureTheme) -> dict:
    """Run a generator on one repo/project.

    Returns:
        dict with keys: repo, project_file, svg_path (or None),
        prepared_data (for stats), error (traceback string or None)
    """
    repo = selection_item["repo"]
    output_file = selection_item["output_file"]
    project_file = selection_item["project_file"]

    result = {
        "repo": repo,
        "project_file": project_file,
        "svg_path": None,
        "prepared_data": None,
        "error": None,
    }

    try:
        analysis = load_analysis(repo, output_file)
        config = {}  # No per-project config needed for review

        data = entry.generator_cls.prepare(analysis, config)
        if data is None:
            result["error"] = "prepare() returned None — no data for this generator"
            return result

        result["prepared_data"] = data

        # Render
        figures_dir = REVIEW_DIR / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename: owner_repo_projectfile.svg
        safe_name = repo.replace("/", "_") + "_" + Path(project_file).stem

        if entry.multi_output:
            # Multi-output: render all, collect paths
            if not isinstance(data, list):
                result["error"] = "multi_output generator returned non-list"
                return result
            svg_paths = []
            for key, input_dict in data:
                svg_path = str(figures_dir / f"{safe_name}_{key}.svg")
                path = entry.generator_cls.render(input_dict, svg_path,
                                                  theme=theme)
                if path:
                    svg_paths.append(path)
            result["svg_path"] = svg_paths  # list for multi-output
        else:
            svg_path = str(figures_dir / f"{safe_name}.svg")
            path = entry.generator_cls.render(data, svg_path, theme=theme)
            result["svg_path"] = path

    except Exception:
        result["error"] = traceback.format_exc()

    return result


def generate_all(entry: GeneratorEntry,
                 selection: List[Dict]) -> List[dict]:
    """Run the generator on all selected repos.

    Returns:
        List of result dicts from generate_figure().
    """
    theme = FigureTheme()
    results = []
    for i, item in enumerate(selection, 1):
        print(f"  [{i}/{len(selection)}] {item['repo']}...",
              end="", flush=True, file=sys.stderr)
        result = generate_figure(entry, item, theme)
        if result["error"]:
            print(f" ERROR", file=sys.stderr)
        elif result["svg_path"]:
            print(f" OK", file=sys.stderr)
        else:
            print(f" no output", file=sys.stderr)
        results.append(result)
    return results


def extract_stats(generator_name: str, prepared_data) -> str:
    """Extract a human-readable stats line from prepared data.

    Each generator has specific stats that are meaningful for review.
    Falls back to a generic summary for unknown generators.
    """
    if prepared_data is None:
        return "no data"

    extractors = {
        "power_tree": _stats_power_tree,
        "architecture": _stats_architecture,
        "bus_topology": _stats_bus_topology,
        "pinouts": _stats_pinouts,
        "schematic_overview": _stats_schematic_overview,
        "pcb_views": _stats_pcb_views,
        "thermal_margin": _stats_thermal_margin,
        "emc_severity": _stats_emc_severity,
    }

    fn = extractors.get(generator_name)
    if fn:
        try:
            return fn(prepared_data)
        except Exception:
            return "stats extraction failed"
    return _stats_generic(prepared_data)


def _stats_power_tree(data: dict) -> str:
    regs = len(data.get("regulators", []))
    rails = len(data.get("output_rails", []))
    enables = len(data.get("enable_chains", []))
    parts = [f"{regs} regulators", f"{rails} rails"]
    if enables:
        parts.append(f"{enables} enable chains")
    return ", ".join(parts)


def _stats_architecture(data: dict) -> str:
    groups = data.get("groups", {})
    total = sum(len(v) for v in groups.values() if isinstance(v, list))
    cats = [k for k, v in groups.items() if isinstance(v, list) and v]
    return f"{total} components in {len(cats)} categories"


def _stats_bus_topology(data: dict) -> str:
    buses = data.get("buses", [])
    parts = []
    for bus in buses:
        btype = bus.get("type", "?")
        devs = len(bus.get("devices", []))
        parts.append(f"{btype}({devs})")
    return ", ".join(parts) if parts else "no buses"


def _stats_pinouts(data) -> str:
    # Multi-output: data is list of (key, dict) tuples
    if isinstance(data, list):
        return f"{len(data)} connectors"
    return "1 connector"


def _stats_schematic_overview(data) -> str:
    if isinstance(data, list):
        return f"{len(data)} sheets"
    return "1 sheet"


def _stats_pcb_views(data) -> str:
    if isinstance(data, list):
        return f"{len(data)} views"
    footprints = data.get("footprint_count", "?")
    return f"{footprints} footprints"


def _stats_thermal_margin(data: dict) -> str:
    components = data.get("components", [])
    return f"{len(components)} thermal components"


def _stats_emc_severity(data: dict) -> str:
    categories = data.get("categories", {})
    total = sum(v for v in categories.values() if isinstance(v, int))
    return f"{total} findings in {len(categories)} categories"


def _stats_generic(data) -> str:
    if isinstance(data, list):
        return f"{len(data)} items"
    if isinstance(data, dict):
        return f"{len(data)} keys"
    return "data present"


GALLERY_FILE = REVIEW_DIR / "gallery.html"


def build_gallery(generator_name: str, results: List[dict]) -> str:
    """Build the HTML gallery page and write to GALLERY_FILE.

    Returns:
        Path to the gallery file.
    """
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    ok_count = sum(1 for r in results if r["svg_path"])

    cards_html = []
    figure_num = 0
    for r in results:
        figure_num += 1
        repo_escaped = html.escape(r["repo"])
        project_escaped = html.escape(r["project_file"])
        stats = extract_stats(generator_name, r["prepared_data"])
        stats_escaped = html.escape(stats)

        if r["error"]:
            # Error card — show traceback
            error_escaped = html.escape(r["error"])
            figure_html = (
                f'<pre style="color:#f87171; font-size:12px; '
                f'overflow-x:auto; white-space:pre-wrap;">'
                f'{error_escaped}</pre>'
            )
        elif r["svg_path"]:
            if isinstance(r["svg_path"], list):
                # Multi-output: show all SVGs stacked
                parts = []
                for svg_path in r["svg_path"]:
                    svg_content = _read_svg(svg_path)
                    parts.append(
                        f'<div style="margin-bottom:16px;">{svg_content}</div>'
                    )
                figure_html = "\n".join(parts)
            else:
                figure_html = _read_svg(r["svg_path"])
        else:
            figure_html = (
                '<p style="color:#94a3b8; font-style:italic;">'
                'No output generated</p>'
            )

        cards_html.append(f'''
        <div style="margin-bottom:32px; padding:24px;
                    background:#1e293b; border-radius:8px;
                    border:1px solid #334155;">
          <div style="display:flex; align-items:baseline; gap:16px;
                      margin-bottom:12px;">
            <span style="font-size:28px; font-weight:bold;
                         color:#60a5fa; min-width:48px;">#{figure_num}</span>
            <div>
              <div style="font-size:16px; color:#e2e8f0;
                          font-weight:600;">{repo_escaped}</div>
              <div style="font-size:13px; color:#64748b;">{project_escaped}</div>
            </div>
          </div>
          <div style="font-size:13px; color:#94a3b8;
                      margin-bottom:16px; padding:8px 12px;
                      background:#0f172a; border-radius:4px;
                      font-family:monospace;">{stats_escaped}</div>
          <div style="background:#0f172a; border-radius:4px;
                      padding:16px; overflow-x:auto;">
            {figure_html}
          </div>
        </div>
        ''')

    all_cards = "\n".join(cards_html)

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(generator_name)} — Figure Review</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0f172a; color:#e2e8f0; font-family:system-ui,
         -apple-system, sans-serif; padding:24px; }}
  svg {{ max-width:100%; height:auto; }}
</style>
</head>
<body>
  <div style="max-width:1200px; margin:0 auto;">
    <div style="display:flex; justify-content:space-between;
                align-items:baseline; margin-bottom:32px;
                padding-bottom:16px; border-bottom:1px solid #334155;">
      <h1 style="font-size:24px; color:#f8fafc;">
        {html.escape(generator_name)}</h1>
      <span style="color:#64748b; font-size:14px;">
        {ok_count} figures &mdash; {timestamp}</span>
    </div>
    {all_cards}
  </div>

  <script>
    // Auto-refresh: poll mtime every 2 seconds
    let lastMtime = null;
    async function checkRefresh() {{
      try {{
        const resp = await fetch("/?mtime");
        const mtime = await resp.text();
        if (lastMtime === null) {{
          lastMtime = mtime;
        }} else if (mtime !== lastMtime) {{
          location.reload();
        }}
      }} catch(e) {{}}
    }}
    setInterval(checkRefresh, 2000);
  </script>
</body>
</html>'''

    with open(GALLERY_FILE, "w") as f:
        f.write(page_html)

    return str(GALLERY_FILE)


def _read_svg(svg_path: str) -> str:
    """Read an SVG file and return its content for inline embedding.

    Strips the XML declaration if present so it embeds cleanly in HTML.
    """
    try:
        with open(svg_path) as f:
            content = f.read()
        # Strip XML declaration
        if content.startswith("<?xml"):
            idx = content.index("?>")
            content = content[idx + 2:].lstrip()
        return content
    except Exception as e:
        return (f'<p style="color:#f87171;">Failed to read SVG: '
                f'{html.escape(str(e))}</p>')


PID_FILE = REVIEW_DIR / ".server.pid"


class _ReviewHandler(SimpleHTTPRequestHandler):
    """Serves the gallery directory with a ?mtime endpoint for auto-refresh."""

    def do_GET(self):
        if self.path == "/?mtime" or self.path == "/?mtime=":
            # Return gallery file mtime as plain text
            try:
                mtime = os.path.getmtime(GALLERY_FILE)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(str(mtime).encode())
            except OSError:
                self.send_error(404, "Gallery not found")
            return
        # Serve / as gallery.html
        if self.path == "/" or self.path == "":
            self.path = "/gallery.html"
        super().do_GET()

    def translate_path(self, path):
        """Root all file serving at REVIEW_DIR."""
        # Get the path component (strip query string)
        path = path.split("?")[0].split("#")[0]
        # Remove leading /
        path = path.lstrip("/")
        return str(REVIEW_DIR / path)

    def log_message(self, format, *args):
        """Suppress request logging to keep terminal clean."""
        pass


def find_running_server() -> Optional[int]:
    """Check if a server is already running. Returns port if so."""
    if not PID_FILE.exists():
        return None
    try:
        info = json.loads(PID_FILE.read_text())
        pid = info["pid"]
        port = info["port"]
        # Check if the process is still alive
        os.kill(pid, 0)
        return port
    except (OSError, KeyError, json.JSONDecodeError):
        # Process not running or PID file corrupt — clean up
        PID_FILE.unlink(missing_ok=True)
        return None


def start_server(port: int = 0) -> Tuple[HTTPServer, int]:
    """Start the gallery HTTP server in a daemon thread.

    Writes a PID file so subsequent --reuse-repos invocations can detect
    the running server and exit without starting a duplicate.

    Args:
        port: Port to bind (0 = random available)

    Returns:
        (server, actual_port)
    """
    server = HTTPServer(("127.0.0.1", port), _ReviewHandler)
    actual_port = server.server_address[1]

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Write PID file so other invocations know a server exists
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        json.dump({"pid": os.getpid(), "port": actual_port}, f)

    return server, actual_port


def list_generators() -> None:
    """Print all registered figure generators."""
    registry = get_registry()
    print(f"Available generators ({len(registry)}):\n")
    for entry in registry:
        deps = f"  (requires: {', '.join(entry.requires)})" if entry.requires else ""
        multi = "  [multi-output]" if entry.multi_output else ""
        print(f"  {entry.name:<22} → {entry.output}{deps}{multi}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Human-in-the-loop figure review tool for kidoc generators")
    parser.add_argument("--list", action="store_true",
                        help="List available generators and exit")
    parser.add_argument("--generator", "-g",
                        help="Generator name to review (e.g., power_tree)")
    parser.add_argument("--count", "-n", type=int, default=15,
                        help="Number of repos to select (default: 15)")
    parser.add_argument("--repo", action="append", default=[],
                        help="Manually specify repo(s) instead of auto-select")
    parser.add_argument("--reuse-repos", action="store_true",
                        help="Reuse repo selection from previous run")
    parser.add_argument("--port", type=int, default=0,
                        help="HTTP server port (default: random available)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        list_generators()
        return

    if not args.generator:
        print("Error: --generator is required (use --list to see options)",
              file=sys.stderr)
        sys.exit(1)

    # Find the requested generator in the registry
    registry = get_registry()
    entry = None
    for e in registry:
        if e.name == args.generator:
            entry = e
            break
    if entry is None:
        print(f"Error: unknown generator '{args.generator}'. "
              f"Use --list to see available generators.", file=sys.stderr)
        sys.exit(1)

    if not check_requires(entry):
        print(f"Error: generator '{entry.name}' requires {entry.requires} "
              f"which are not installed.", file=sys.stderr)
        sys.exit(1)

    # Select repos
    if args.reuse_repos:
        selection = load_selection()
        print(f"Reusing {len(selection)} repos from previous selection")
    elif args.repo:
        selection = manual_repos(args.repo, entry.name)
        save_selection(selection)
    else:
        selection = select_repos(entry.name, args.count)
        save_selection(selection)

    print(f"Selected {len(selection)} repos for {entry.name}")
    for i, s in enumerate(selection, 1):
        print(f"  #{i}: {s['repo']} (richness={s['richness']})")

    # Generate figures
    print(f"\nGenerating {entry.name} figures...")
    results = generate_all(entry, selection)

    ok = sum(1 for r in results if r["svg_path"])
    err = sum(1 for r in results if r["error"])
    print(f"\nGenerated: {ok} OK, {err} errors, "
          f"{len(results) - ok - err} skipped")

    # Build gallery
    gallery_path = build_gallery(entry.name, results)

    # Start or detect server
    existing_port = find_running_server()
    if existing_port:
        url = f"http://localhost:{existing_port}"
        print(f"\n{'='*60}")
        print(f"  Gallery updated: {url}")
        print(f"  Generator: {entry.name}")
        print(f"  Figures: {ok}")
        print(f"{'='*60}")
        print(f"\nGallery regenerated. Browser will auto-refresh.")
    else:
        server, actual_port = start_server(args.port)
        url = f"http://localhost:{actual_port}"
        print(f"\n{'='*60}")
        print(f"  Gallery: {url}")
        print(f"  Generator: {entry.name}")
        print(f"  Figures: {ok}")
        print(f"{'='*60}")
        print(f"\nReview the figures in your browser.")
        print(f"Provide feedback in the terminal (reference figures by #number).")
        print(f"To regenerate, re-run with --reuse-repos.")
        print(f"Press Ctrl+C to stop the server.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServer stopped.")
            PID_FILE.unlink(missing_ok=True)
            server.shutdown()


if __name__ == "__main__":
    main()
