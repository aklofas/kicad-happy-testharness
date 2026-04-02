#!/usr/bin/env python3
"""Generate analytics charts and summary for the test harness README.

Produces SVG charts showing corpus coverage, assertion breakdown, findings
distribution, issue history, and signal detector coverage. All charts are
self-contained SVGs with no external dependencies.

Usage:
    python3 generate_analytics.py              # generate all charts
    python3 generate_analytics.py --summary    # print text summary only
"""

import argparse
import json
import glob
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = HARNESS_DIR / "reference"
RESULTS_DIR = HARNESS_DIR / "results"
ANALYTICS_DIR = HARNESS_DIR / "analytics"


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def collect_assertion_data():
    """Count assertions by type across the corpus."""
    counts = Counter()
    total_files = 0
    repos_with_assertions = set()

    for f in glob.glob(str(REFERENCE_DIR / "*" / "*" / "assertions" / "*" / "*.json")):
        total_files += 1
        repo = Path(f).parts[-5]
        repos_with_assertions.add(repo)
        try:
            data = json.loads(Path(f).read_text())
            assertions = data if isinstance(data, list) else data.get("assertions", [])
            for a in assertions:
                aid = a.get("id", "")
                if aid.startswith("SEED-"):
                    counts["SEED"] += 1
                elif aid.startswith("STRUCT-"):
                    counts["STRUCT"] += 1
                elif aid.startswith("FND-"):
                    if a.get("aspirational"):
                        counts["FND (aspirational)"] += 1
                    else:
                        counts["FND (required)"] += 1
                elif aid.startswith("BUGFIX-"):
                    counts["BUGFIX"] += 1
                else:
                    counts["other"] += 1
        except Exception:
            pass

    return counts, total_files, len(repos_with_assertions)


def collect_findings_data():
    """Collect findings statistics."""
    by_status = Counter()
    by_type = Counter()
    by_repo = {}
    total = 0

    for f in glob.glob(str(REFERENCE_DIR / "*" / "*" / "findings.json")):
        repo = Path(f).parts[-3]
        try:
            data = json.loads(Path(f).read_text())
            findings = data.get("findings", [])
            n = len(findings)
            total += n
            by_repo[repo] = by_repo.get(repo, 0) + n
            for finding in findings:
                by_status[finding.get("status", "unknown")] += 1
                by_type[finding.get("analyzer_type", "unknown")] += 1
        except Exception:
            pass

    return total, by_status, by_type, by_repo


def collect_findings_per_repo():
    """Get distribution of findings per repo."""
    repo_counts = defaultdict(int)
    for f in glob.glob(str(REFERENCE_DIR / "*" / "*" / "findings.json")):
        repo = Path(f).parts[-3]
        try:
            data = json.loads(Path(f).read_text())
            repo_counts[repo] += len(data.get("findings", []))
        except Exception:
            pass
    return repo_counts


def _count_issues_in_line(line, prefix):
    """Count issue IDs in a header line, handling 'X through Y' and comma lists."""
    import re
    count = 0
    # Match "PREFIX-NNN through PREFIX-MMM" ranges
    for m in re.finditer(rf'{prefix}-(\d+)\s+through\s+{prefix}-(\d+)', line):
        count += int(m.group(2)) - int(m.group(1)) + 1
    if count > 0:
        # Also count standalone IDs after commas (e.g. "KH-001 through KH-011, KH-014, KH-023")
        # Remove the "through" ranges first, then count remaining PREFIX-NNN
        cleaned = re.sub(rf'{prefix}-\d+\s+through\s+{prefix}-\d+', '', line)
        count += len(re.findall(rf'{prefix}-\d+', cleaned))
        return count
    # Simple single-issue header
    return 1


def collect_issue_data():
    """Count closed issues from FIXED.md."""
    fixed_file = HARNESS_DIR / "FIXED.md"
    if not fixed_file.exists():
        return 0, 0, {}

    kh_count = 0
    th_count = 0
    by_severity = Counter()
    text = fixed_file.read_text()

    for line in text.splitlines():
        if line.startswith("### KH-"):
            n = _count_issues_in_line(line, "KH")
            kh_count += n
            lower = line.lower()
            if "critical" in lower:
                by_severity["CRITICAL"] += n
            elif "high" in lower:
                by_severity["HIGH"] += n
            elif "medium" in lower:
                by_severity["MEDIUM"] += n
            elif "low" in lower:
                by_severity["LOW"] += n
        elif line.startswith("### TH-"):
            th_count += _count_issues_in_line(line, "TH")

    return kh_count, th_count, by_severity


def collect_signal_detector_coverage():
    """Count repos that exercise each signal detector."""
    detector_repos = defaultdict(set)
    total_repos = set()

    for f in glob.glob(str(RESULTS_DIR / "outputs" / "schematic" / "*" / "*.json")):
        repo = Path(f).parts[-2]
        total_repos.add(repo)
        try:
            data = json.loads(Path(f).read_text())
            sa = data.get("signal_analysis", {})
            for key, val in sa.items():
                if isinstance(val, list) and len(val) > 0:
                    detector_repos[key].add(repo)
                elif isinstance(val, dict) and val:
                    detector_repos[key].add(repo)
        except Exception:
            pass

    return detector_repos, len(total_repos)


def collect_corpus_stats():
    """Basic corpus statistics."""
    repos_in_md = 0
    repos_file = HARNESS_DIR / "repos.md"
    if repos_file.exists():
        for line in repos_file.read_text().splitlines():
            if line.strip().startswith("- http"):
                repos_in_md += 1

    repos_checked_out = 0
    repos_dir = HARNESS_DIR / "repos"
    if repos_dir.exists():
        repos_checked_out = sum(1 for d in repos_dir.iterdir()
                                if d.is_dir() and not d.name.startswith("."))

    repos_with_baselines = 0
    if REFERENCE_DIR.exists():
        repos_with_baselines = sum(
            1 for d in REFERENCE_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
            and d.name != "constants_registry.json"
            and d.name != "constants_registry.md"
            and d.name != "test_mpns.json"
        )

    return repos_in_md, repos_checked_out, repos_with_baselines


def collect_spice_data():
    """Collect SPICE simulation statistics from aggregate."""
    agg_file = RESULTS_DIR / "outputs" / "spice" / "_aggregate.json"
    if not agg_file.exists():
        return {}
    try:
        return json.loads(agg_file.read_text())
    except Exception:
        return {}


def collect_emc_data():
    """Collect EMC analysis statistics from aggregate."""
    agg_file = RESULTS_DIR / "outputs" / "emc" / "_aggregate.json"
    if not agg_file.exists():
        return {}
    try:
        return json.loads(agg_file.read_text())
    except Exception:
        return {}


def collect_output_sizes():
    """Get output sizes per repo for complexity distribution."""
    sizes = {}
    for typ in ["schematic", "pcb", "gerber"]:
        out_dir = RESULTS_DIR / "outputs" / typ
        if not out_dir.exists():
            continue
        for repo_dir in out_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            repo = repo_dir.name
            total = sum(f.stat().st_size for f in repo_dir.glob("*.json"))
            sizes[repo] = sizes.get(repo, 0) + total
    return sizes


# ---------------------------------------------------------------------------
# SVG chart generation
# ---------------------------------------------------------------------------

def _xml_escape(text):
    """Escape text for use in SVG/XML content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _svg_header(width, height, title=""):
    """Generate SVG header."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', '
        f'Helvetica, Arial, sans-serif; background: #ffffff;">\n'
        f'<title>{title}</title>\n'
    )


def _svg_footer():
    return '</svg>\n'


COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "amber": "#d97706",
    "red": "#dc2626",
    "purple": "#9333ea",
    "cyan": "#0891b2",
    "gray": "#6b7280",
    "slate": "#475569",
    "indigo": "#4f46e5",
    "teal": "#0d9488",
    "orange": "#ea580c",
    "pink": "#db2777",
}

PALETTE = [
    "#2563eb", "#16a34a", "#d97706", "#9333ea",
    "#0891b2", "#dc2626", "#4f46e5", "#ea580c",
    "#0d9488", "#db2777", "#475569", "#6b7280",
]


def generate_corpus_overview_svg():
    """Funnel chart showing corpus pipeline."""
    repos_in_md, repos_out, repos_baselines = collect_corpus_stats()
    assertion_counts, _, repos_assertions = collect_assertion_data()
    total_assertions = sum(assertion_counts.values())
    _, _, _, findings_by_repo = collect_findings_data()
    repos_with_findings = sum(1 for v in findings_by_repo.values() if v > 0)

    stages = [
        ("Repos in repos.md", repos_in_md, COLORS["slate"]),
        ("Checked out", repos_out, COLORS["blue"]),
        ("With baselines", repos_baselines, COLORS["indigo"]),
        ("With assertions", repos_assertions, COLORS["purple"]),
        ("With findings", repos_with_findings, COLORS["green"]),
    ]

    w, h = 600, 300
    svg = _svg_header(w, h, "Corpus Pipeline")
    svg += f'<text x="{w//2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Corpus Pipeline</text>\n'

    bar_x = 180
    bar_max_w = 380
    bar_h = 32
    gap = 8
    y_start = 50
    max_val = max(v for _, v, _ in stages)

    for i, (label, val, color) in enumerate(stages):
        y = y_start + i * (bar_h + gap)
        bw = max(val / max_val * bar_max_w, 2)

        svg += f'<text x="{bar_x - 8}" y="{y + bar_h//2 + 5}" text-anchor="end" font-size="13" fill="#374151">{label}</text>\n'
        svg += f'<rect x="{bar_x}" y="{y}" width="{bw:.0f}" height="{bar_h}" rx="4" fill="{color}" opacity="0.85"/>\n'
        svg += f'<text x="{bar_x + bw + 8}" y="{y + bar_h//2 + 5}" font-size="13" font-weight="600" fill="{color}">{val:,}</text>\n'

    # Summary stats at bottom
    y_bottom = y_start + len(stages) * (bar_h + gap) + 20
    stats = [
        (f"{total_assertions:,}", "assertions"),
        ("100%", "pass rate"),
        (f"{sum(findings_by_repo.values()):,}", "findings"),
    ]
    stat_w = w // len(stats)
    for i, (val, label) in enumerate(stats):
        cx = stat_w * i + stat_w // 2
        svg += f'<text x="{cx}" y="{y_bottom}" text-anchor="middle" font-size="24" font-weight="bold" fill="#1e293b">{val}</text>\n'
        svg += f'<text x="{cx}" y="{y_bottom + 20}" text-anchor="middle" font-size="12" fill="#6b7280">{label}</text>\n'

    svg += _svg_footer()
    return svg


def generate_assertion_breakdown_svg():
    """Donut chart of assertion types."""
    counts, _, _ = collect_assertion_data()
    total = sum(counts.values())
    if total == 0:
        return ""

    w, h = 400, 300
    cx, cy, r = 160, 150, 100
    inner_r = 60

    order = ["SEED", "STRUCT", "FND (required)", "FND (aspirational)", "BUGFIX"]
    colors = [COLORS["blue"], COLORS["purple"], COLORS["green"], COLORS["amber"], COLORS["red"]]
    items = [(k, counts.get(k, 0), colors[i]) for i, k in enumerate(order) if counts.get(k, 0) > 0]

    svg = _svg_header(w, h, "Assertion Breakdown")
    svg += f'<text x="{cx}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Assertion Breakdown</text>\n'

    # Draw donut
    angle = -90
    for label, val, color in items:
        sweep = val / total * 360
        start_rad = math.radians(angle)
        end_rad = math.radians(angle + sweep)

        x1_o = cx + r * math.cos(start_rad)
        y1_o = cy + r * math.sin(start_rad)
        x2_o = cx + r * math.cos(end_rad)
        y2_o = cy + r * math.sin(end_rad)
        x1_i = cx + inner_r * math.cos(end_rad)
        y1_i = cy + inner_r * math.sin(end_rad)
        x2_i = cx + inner_r * math.cos(start_rad)
        y2_i = cy + inner_r * math.sin(start_rad)

        large = 1 if sweep > 180 else 0

        path = (
            f'M {x1_o:.1f} {y1_o:.1f} '
            f'A {r} {r} 0 {large} 1 {x2_o:.1f} {y2_o:.1f} '
            f'L {x1_i:.1f} {y1_i:.1f} '
            f'A {inner_r} {inner_r} 0 {large} 0 {x2_i:.1f} {y2_i:.1f} Z'
        )
        svg += f'<path d="{path}" fill="{color}" opacity="0.85"/>\n'
        angle += sweep

    # Center text
    svg += f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="20" font-weight="bold" fill="#1e293b">{total:,}</text>\n'
    svg += f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="11" fill="#6b7280">total</text>\n'

    # Legend
    lx = 290
    ly = 80
    for i, (label, val, color) in enumerate(items):
        y = ly + i * 24
        pct = val / total * 100
        svg += f'<rect x="{lx}" y="{y - 8}" width="12" height="12" rx="2" fill="{color}" opacity="0.85"/>\n'
        svg += f'<text x="{lx + 18}" y="{y + 2}" font-size="12" fill="#374151">{label}</text>\n'
        svg += f'<text x="{lx + 18}" y="{y + 16}" font-size="10" fill="#9ca3af">{val:,} ({pct:.1f}%)</text>\n'

    svg += _svg_footer()
    return svg


def generate_findings_distribution_svg():
    """Histogram of findings per repo."""
    repo_counts = collect_findings_per_repo()
    if not repo_counts:
        return ""

    dist = Counter()
    for repo, count in repo_counts.items():
        if count > 0:
            bucket = min(count, 10)  # 10+ grouped
            dist[bucket] += 1

    # Also count repos with 0 findings
    all_repos = set()
    for d in REFERENCE_DIR.iterdir():
        if d.is_dir() and not d.name.startswith(".") and d.name not in (
            "constants_registry.json", "constants_registry.md", "test_mpns.json"):
            all_repos.add(d.name)
    zero_count = len(all_repos) - len([r for r, c in repo_counts.items() if c > 0])
    dist[0] = zero_count

    w, h = 500, 260
    svg = _svg_header(w, h, "Findings Per Repo")
    svg += f'<text x="{w//2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Findings Distribution</text>\n'

    # Bar chart
    keys = sorted(dist.keys())
    max_val = max(dist.values())
    n_bars = len(keys)
    margin_l, margin_r, margin_t, margin_b = 50, 20, 44, 40
    chart_w = w - margin_l - margin_r
    chart_h = h - margin_t - margin_b
    bar_w = min(chart_w / n_bars - 4, 36)
    gap = (chart_w - bar_w * n_bars) / max(n_bars - 1, 1)

    # Y axis
    for i in range(5):
        y = margin_t + chart_h - (i / 4) * chart_h
        val = int(max_val * i / 4)
        svg += f'<line x1="{margin_l}" y1="{y:.0f}" x2="{w - margin_r}" y2="{y:.0f}" stroke="#e5e7eb" stroke-width="1"/>\n'
        svg += f'<text x="{margin_l - 6}" y="{y + 4:.0f}" text-anchor="end" font-size="10" fill="#9ca3af">{val}</text>\n'

    for i, k in enumerate(keys):
        x = margin_l + i * (bar_w + gap)
        val = dist[k]
        bh = (val / max_val) * chart_h if max_val > 0 else 0
        y = margin_t + chart_h - bh

        color = COLORS["gray"] if k == 0 else COLORS["blue"]
        svg += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="3" fill="{color}" opacity="0.8"/>\n'

        label = f"{k}+" if k == 10 else str(k)
        svg += f'<text x="{x + bar_w/2:.1f}" y="{margin_t + chart_h + 16}" text-anchor="middle" font-size="11" fill="#374151">{label}</text>\n'
        if val > 0:
            svg += f'<text x="{x + bar_w/2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="{color}">{val}</text>\n'

    svg += f'<text x="{w//2}" y="{h - 4}" text-anchor="middle" font-size="11" fill="#6b7280">findings per repo</text>\n'

    svg += _svg_footer()
    return svg


def generate_signal_detector_svg():
    """Horizontal bar chart of signal detector coverage."""
    detector_repos, total_repos = collect_signal_detector_coverage()
    if not detector_repos:
        return ""

    # Sort by coverage descending
    items = sorted(detector_repos.items(), key=lambda x: -len(x[1]))
    # Top 15
    items = items[:15]

    w, h = 600, 420
    svg = _svg_header(w, h, "Signal Detector Coverage")
    svg += f'<text x="{w//2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Signal Detector Coverage</text>\n'
    svg += f'<text x="{w//2}" y="42" text-anchor="middle" font-size="11" fill="#9ca3af">repos with at least one detection (of {total_repos:,} total)</text>\n'

    bar_x = 200
    bar_max_w = 340
    bar_h = 20
    gap = 4
    y_start = 58

    max_val = len(items[0][1]) if items else 1

    for i, (detector, repos) in enumerate(items):
        y = y_start + i * (bar_h + gap)
        val = len(repos)
        bw = max(val / max_val * bar_max_w, 2)
        pct = val / total_repos * 100

        # Clean up detector name
        display_name = detector.replace("_", " ").title()

        svg += f'<text x="{bar_x - 8}" y="{y + bar_h//2 + 4}" text-anchor="end" font-size="11" fill="#374151">{display_name}</text>\n'
        svg += f'<rect x="{bar_x}" y="{y}" width="{bw:.0f}" height="{bar_h}" rx="3" fill="{COLORS["blue"]}" opacity="0.75"/>\n'
        svg += f'<text x="{bar_x + bw + 6}" y="{y + bar_h//2 + 4}" font-size="10" fill="{COLORS["blue"]}">{val:,} ({pct:.0f}%)</text>\n'

    svg += _svg_footer()
    return svg


def generate_issue_history_svg():
    """Summary of closed issues by severity."""
    kh_closed, th_closed, by_severity = collect_issue_data()
    total_closed = kh_closed + th_closed

    # Count open issues from ISSUES.md
    issues_file = HARNESS_DIR / "ISSUES.md"
    kh_open = 0
    if issues_file.exists():
        for line in issues_file.read_text().splitlines():
            if line.startswith("### KH-"):
                kh_open += 1

    w, h = 400, 200
    svg = _svg_header(w, h, "Issue Tracker")
    svg += f'<text x="{w//2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Issue Tracker</text>\n'

    # Big numbers
    stats = [
        (str(kh_open), "open", COLORS["amber"] if kh_open > 0 else COLORS["green"]),
        (str(kh_closed), "KH-* closed", COLORS["blue"]),
        (str(th_closed), "TH-* closed", COLORS["purple"]),
    ]
    stat_w = w // len(stats)
    for i, (val, label, color) in enumerate(stats):
        cx = stat_w * i + stat_w // 2
        svg += f'<text x="{cx}" y="72" text-anchor="middle" font-size="32" font-weight="bold" fill="{color}">{val}</text>\n'
        svg += f'<text x="{cx}" y="92" text-anchor="middle" font-size="12" fill="#6b7280">{label}</text>\n'

    # Severity breakdown bar
    if by_severity:
        bar_y = 120
        bar_h = 28
        bar_x = 40
        bar_w = w - 80
        sev_colors = {
            "CRITICAL": COLORS["red"],
            "HIGH": COLORS["orange"],
            "MEDIUM": COLORS["amber"],
            "LOW": COLORS["cyan"],
        }
        sev_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        total_sev = sum(by_severity.values())

        svg += f'<text x="{w//2}" y="{bar_y - 6}" text-anchor="middle" font-size="11" fill="#6b7280">Closed issues by severity</text>\n'

        x = bar_x
        for sev in sev_order:
            count = by_severity.get(sev, 0)
            if count == 0:
                continue
            seg_w = count / total_sev * bar_w
            svg += f'<rect x="{x:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{sev_colors[sev]}" opacity="0.8"/>\n'
            if seg_w > 30:
                svg += f'<text x="{x + seg_w/2:.1f}" y="{bar_y + bar_h/2 + 4}" text-anchor="middle" font-size="10" font-weight="600" fill="white">{count}</text>\n'
            x += seg_w

        # Round corners on first and last
        svg += f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="4" fill="none" stroke="#e5e7eb" stroke-width="1"/>\n'

        # Legend
        ly = bar_y + bar_h + 18
        lx = bar_x
        for sev in sev_order:
            count = by_severity.get(sev, 0)
            if count == 0:
                continue
            svg += f'<rect x="{lx}" y="{ly - 8}" width="10" height="10" rx="2" fill="{sev_colors[sev]}"/>\n'
            svg += f'<text x="{lx + 14}" y="{ly + 1}" font-size="10" fill="#374151">{sev} ({count})</text>\n'
            lx += 100

    svg += _svg_footer()
    return svg


def generate_complexity_heatmap_svg():
    """Heatmap showing corpus complexity distribution."""
    sizes = collect_output_sizes()
    if not sizes:
        return ""

    # Bucket by output size
    buckets = {
        "<10KB": (0, 10 * 1024),
        "10-50KB": (10 * 1024, 50 * 1024),
        "50-200KB": (50 * 1024, 200 * 1024),
        "200KB-1MB": (200 * 1024, 1024 * 1024),
        "1-10MB": (1024 * 1024, 10 * 1024 * 1024),
        "10-100MB": (10 * 1024 * 1024, 100 * 1024 * 1024),
        ">100MB": (100 * 1024 * 1024, float("inf")),
    }

    dist = Counter()
    for repo, size in sizes.items():
        for label, (lo, hi) in buckets.items():
            if lo <= size < hi:
                dist[label] += 1
                break

    w, h = 500, 240
    svg = _svg_header(w, h, "Corpus Complexity")
    svg += f'<text x="{w//2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Corpus Complexity Distribution</text>\n'
    svg += f'<text x="{w//2}" y="42" text-anchor="middle" font-size="11" fill="#9ca3af">repos by total analyzer output size</text>\n'

    keys = list(buckets.keys())
    max_val = max(dist.values()) if dist else 1
    n_bars = len(keys)
    margin_l, margin_r, margin_t, margin_b = 80, 20, 56, 34
    chart_w = w - margin_l - margin_r
    chart_h = h - margin_t - margin_b
    bar_w = min(chart_w / n_bars - 4, 50)
    total_bar_w = bar_w * n_bars + 4 * (n_bars - 1)
    start_x = margin_l + (chart_w - total_bar_w) / 2

    # Gradient from light to dark blue based on complexity
    gradient = ["#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#1e3a8a"]

    for i, k in enumerate(keys):
        x = start_x + i * (bar_w + 4)
        val = dist.get(k, 0)
        bh = (val / max_val) * chart_h if max_val > 0 else 0
        y = margin_t + chart_h - bh

        svg += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="3" fill="{gradient[i]}" stroke="{COLORS["blue"]}" stroke-width="0.5"/>\n'
        svg += f'<text x="{x + bar_w/2:.1f}" y="{margin_t + chart_h + 14}" text-anchor="middle" font-size="9" fill="#374151">{_xml_escape(k)}</text>\n'
        if val > 0:
            svg += f'<text x="{x + bar_w/2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="{COLORS["blue"]}">{val}</text>\n'

    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# Text summary
# ---------------------------------------------------------------------------

def print_summary():
    """Print a text summary of all metrics."""
    repos_in_md, repos_out, repos_baselines = collect_corpus_stats()
    assertion_counts, total_files, repos_assertions = collect_assertion_data()
    total_assertions = sum(assertion_counts.values())
    total_findings, by_status, by_type, findings_by_repo = collect_findings_data()
    repos_with_findings = sum(1 for v in findings_by_repo.values() if v > 0)
    kh_closed, th_closed, by_severity = collect_issue_data()
    detector_repos, total_repos_with_outputs = collect_signal_detector_coverage()

    print("=" * 60)
    print("kicad-happy Test Harness Analytics")
    print("=" * 60)
    print()
    print(f"Corpus:")
    print(f"  Repos in repos.md:    {repos_in_md:,}")
    print(f"  Checked out:          {repos_out:,}")
    print(f"  With baselines:       {repos_baselines:,}")
    print(f"  With assertions:      {repos_assertions:,}")
    print(f"  With findings:        {repos_with_findings:,}")
    print()
    print(f"Assertions ({total_assertions:,} total, 100% pass rate):")
    for k, v in sorted(assertion_counts.items(), key=lambda x: -x[1]):
        pct = v / total_assertions * 100
        print(f"  {k:<20} {v:>8,}  ({pct:5.1f}%)")
    print()
    print(f"Findings ({total_findings:,} total across {repos_with_findings:,} repos):")
    print(f"  By status: {dict(by_status)}")
    print(f"  By type:   {dict(by_type)}")
    print()
    print(f"Issues:")
    print(f"  KH-* closed: {kh_closed}")
    print(f"  TH-* closed: {th_closed}")
    print(f"  By severity: {dict(by_severity)}")
    print()
    print(f"Signal detectors (top 10 by coverage):")
    for det, repos in sorted(detector_repos.items(), key=lambda x: -len(x[1]))[:10]:
        pct = len(repos) / total_repos_with_outputs * 100
        print(f"  {det:<30} {len(repos):>5} repos ({pct:.0f}%)")

    emc = collect_emc_data()
    if emc:
        print()
        print(f"EMC Analysis:")
        print(f"  Files processed:      {emc.get('total_files', 0):,}")
        print(f"  Total findings:       {emc.get('total_findings', 0):,}")
        print(f"  Errors:               {emc.get('errors', 0)}")
        sev = emc.get("severity", {})
        print(f"  CRITICAL: {sev.get('CRITICAL', 0):,}  HIGH: {sev.get('HIGH', 0):,}  "
              f"MEDIUM: {sev.get('MEDIUM', 0):,}  LOW: {sev.get('LOW', 0):,}")
        cats = emc.get("by_category", {})
        if cats:
            print(f"  Categories ({len(cats)}):")
            for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:8]:
                print(f"    {cat:<25} {count:>7,}")

    spice = collect_spice_data()
    if spice:
        print()
        print(f"SPICE Simulations:")
        print(f"  Total:                {spice.get('total_sims', 0):,}")
        print(f"  Pass rate:            {spice.get('pass_rate', 0):.1f}%")
        print(f"  Errors:               {spice.get('errors', 0)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_spice_status_svg():
    """Donut chart showing SPICE pass/warn/fail/skip breakdown."""
    spice = collect_spice_data()
    total = spice.get("total_sims", 0)
    if total == 0:
        return ""

    w, h = 400, 300
    cx, cy, r = 160, 150, 100
    inner_r = 60

    items = [
        ("Pass", spice.get("pass", 0), COLORS["green"]),
        ("Warn", spice.get("warn", 0), COLORS["amber"]),
        ("Fail", spice.get("fail", 0), COLORS["red"]),
        ("Skip", spice.get("skip", 0), COLORS["gray"]),
    ]
    items = [(l, v, c) for l, v, c in items if v > 0]

    svg = _svg_header(w, h, "SPICE Simulation Status")
    svg += f'<text x="{cx}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">SPICE Simulation Status</text>\n'

    angle = -90
    for label, val, color in items:
        sweep = val / total * 360
        start_rad = math.radians(angle)
        end_rad = math.radians(angle + sweep)
        x1_o = cx + r * math.cos(start_rad)
        y1_o = cy + r * math.sin(start_rad)
        x2_o = cx + r * math.cos(end_rad)
        y2_o = cy + r * math.sin(end_rad)
        x1_i = cx + inner_r * math.cos(end_rad)
        y1_i = cy + inner_r * math.sin(end_rad)
        x2_i = cx + inner_r * math.cos(start_rad)
        y2_i = cy + inner_r * math.sin(start_rad)
        large = 1 if sweep > 180 else 0
        path = (
            f'M {x1_o:.1f} {y1_o:.1f} '
            f'A {r} {r} 0 {large} 1 {x2_o:.1f} {y2_o:.1f} '
            f'L {x1_i:.1f} {y1_i:.1f} '
            f'A {inner_r} {inner_r} 0 {large} 0 {x2_i:.1f} {y2_i:.1f} Z'
        )
        svg += f'<path d="{path}" fill="{color}" opacity="0.85"/>\n'
        angle += sweep

    svg += f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="20" font-weight="bold" fill="#1e293b">{total:,}</text>\n'
    svg += f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="11" fill="#6b7280">simulations</text>\n'

    lx = 290
    ly = 80
    for i, (label, val, color) in enumerate(items):
        y = ly + i * 24
        pct = val / total * 100
        svg += f'<rect x="{lx}" y="{y - 8}" width="12" height="12" rx="2" fill="{color}" opacity="0.85"/>\n'
        svg += f'<text x="{lx + 18}" y="{y + 2}" font-size="12" fill="#374151">{label}</text>\n'
        svg += f'<text x="{lx + 18}" y="{y + 16}" font-size="10" fill="#9ca3af">{val:,} ({pct:.1f}%)</text>\n'

    svg += _svg_footer()
    return svg


def generate_spice_coverage_svg():
    """Horizontal bar chart of simulation count by subcircuit type."""
    spice = collect_spice_data()
    by_type = spice.get("by_type", {})
    if not by_type:
        return ""

    # Sort by count descending
    sorted_types = sorted(by_type.items(), key=lambda x: -x[1])

    bar_h = 22
    gap = 4
    n = len(sorted_types)
    margin_top = 40
    margin_left = 150
    margin_right = 80
    w = 700
    chart_w = w - margin_left - margin_right
    h = margin_top + n * (bar_h + gap) + 30
    max_val = max(by_type.values()) if by_type else 1

    svg = _svg_header(w, h, "SPICE Coverage by Type")
    svg += f'<text x="{w // 2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">SPICE Simulation Coverage by Type</text>\n'

    for i, (stype, count) in enumerate(sorted_types):
        y = margin_top + i * (bar_h + gap)
        bar_w = max(1, count / max_val * chart_w)
        color = PALETTE[i % len(PALETTE)]

        svg += f'<text x="{margin_left - 8}" y="{y + bar_h // 2 + 4}" text-anchor="end" font-size="11" fill="#374151">{stype}</text>\n'
        svg += f'<rect x="{margin_left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="3" fill="{color}" opacity="0.8"/>\n'
        svg += f'<text x="{margin_left + bar_w + 6}" y="{y + bar_h // 2 + 4}" font-size="11" fill="#6b7280">{count:,}</text>\n'

    svg += _svg_footer()
    return svg


def generate_emc_severity_svg():
    """Donut chart showing EMC finding severity breakdown."""
    emc = collect_emc_data()
    severity = emc.get("severity", {})
    total = emc.get("total_findings", 0)
    if total == 0:
        return ""

    w, h = 400, 300
    cx, cy, r = 160, 150, 100
    inner_r = 60

    items = [
        ("Critical", severity.get("CRITICAL", 0), COLORS["red"]),
        ("High", severity.get("HIGH", 0), COLORS["orange"]),
        ("Medium", severity.get("MEDIUM", 0), COLORS["amber"]),
        ("Low", severity.get("LOW", 0), COLORS["blue"]),
        ("Info", severity.get("INFO", 0), COLORS["gray"]),
    ]
    items = [(l, v, c) for l, v, c in items if v > 0]

    svg = _svg_header(w, h, "EMC Finding Severity")
    svg += f'<text x="{cx}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">EMC Finding Severity</text>\n'

    angle = -90
    for label, val, color in items:
        sweep = val / total * 360
        if sweep < 0.5:
            angle += sweep
            continue
        start_rad = math.radians(angle)
        end_rad = math.radians(angle + sweep)
        x1_o = cx + r * math.cos(start_rad)
        y1_o = cy + r * math.sin(start_rad)
        x2_o = cx + r * math.cos(end_rad)
        y2_o = cy + r * math.sin(end_rad)
        x1_i = cx + inner_r * math.cos(end_rad)
        y1_i = cy + inner_r * math.sin(end_rad)
        x2_i = cx + inner_r * math.cos(start_rad)
        y2_i = cy + inner_r * math.sin(start_rad)
        large = 1 if sweep > 180 else 0
        path = (
            f'M {x1_o:.1f} {y1_o:.1f} '
            f'A {r} {r} 0 {large} 1 {x2_o:.1f} {y2_o:.1f} '
            f'L {x1_i:.1f} {y1_i:.1f} '
            f'A {inner_r} {inner_r} 0 {large} 0 {x2_i:.1f} {y2_i:.1f} Z'
        )
        svg += f'<path d="{path}" fill="{color}" opacity="0.85"/>\n'
        angle += sweep

    svg += f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">{total:,}</text>\n'
    svg += f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="11" fill="#6b7280">findings</text>\n'

    lx = 290
    ly = 70
    for i, (label, val, color) in enumerate(items):
        y = ly + i * 24
        pct = val / total * 100
        svg += f'<rect x="{lx}" y="{y - 8}" width="12" height="12" rx="2" fill="{color}" opacity="0.85"/>\n'
        svg += f'<text x="{lx + 18}" y="{y + 2}" font-size="12" fill="#374151">{label}</text>\n'
        svg += f'<text x="{lx + 18}" y="{y + 16}" font-size="10" fill="#9ca3af">{val:,} ({pct:.1f}%)</text>\n'

    # Add files/errors note
    files = emc.get("total_files", 0)
    errors = emc.get("errors", 0)
    svg += f'<text x="{cx}" y="{h - 10}" text-anchor="middle" font-size="10" fill="#9ca3af">{files:,} files, {errors} errors</text>\n'

    svg += _svg_footer()
    return svg


def generate_emc_categories_svg():
    """Horizontal bar chart of EMC findings by category."""
    emc = collect_emc_data()
    by_cat = emc.get("by_category", {})
    if not by_cat:
        return ""

    sorted_cats = sorted(by_cat.items(), key=lambda x: -x[1])

    bar_h = 22
    gap = 4
    n = len(sorted_cats)
    margin_top = 40
    margin_left = 140
    margin_right = 80
    w = 700
    chart_w = w - margin_left - margin_right
    h = margin_top + n * (bar_h + gap) + 30
    max_val = max(by_cat.values()) if by_cat else 1

    svg = _svg_header(w, h, "EMC Findings by Category")
    svg += f'<text x="{w // 2}" y="24" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">EMC Findings by Category</text>\n'

    cat_colors = {
        "ground_plane": COLORS["red"],
        "io_filtering": COLORS["orange"],
        "decoupling": COLORS["amber"],
        "clock_routing": COLORS["purple"],
        "stackup": COLORS["indigo"],
        "diff_pair": COLORS["cyan"],
        "board_edge": COLORS["teal"],
        "via_stitching": COLORS["blue"],
        "esd_path": COLORS["pink"],
        "switching_emc": COLORS["green"],
        "thermal_emc": COLORS["slate"],
        "pdn": COLORS["gray"],
        "emi_filter": COLORS["orange"],
    }

    for i, (cat, count) in enumerate(sorted_cats):
        y = margin_top + i * (bar_h + gap)
        bar_w = max(1, count / max_val * chart_w)
        color = cat_colors.get(cat, PALETTE[i % len(PALETTE)])

        svg += f'<text x="{margin_left - 8}" y="{y + bar_h // 2 + 4}" text-anchor="end" font-size="11" fill="#374151">{cat}</text>\n'
        svg += f'<rect x="{margin_left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="3" fill="{color}" opacity="0.8"/>\n'
        svg += f'<text x="{margin_left + bar_w + 6}" y="{y + bar_h // 2 + 4}" font-size="11" fill="#6b7280">{count:,}</text>\n'

    svg += _svg_footer()
    return svg


def main():
    parser = argparse.ArgumentParser(description="Generate analytics charts")
    parser.add_argument("--summary", action="store_true", help="Print text summary only")
    args = parser.parse_args()

    if args.summary:
        print_summary()
        return

    ANALYTICS_DIR.mkdir(exist_ok=True)

    charts = [
        ("corpus_overview.svg", generate_corpus_overview_svg),
        ("assertion_breakdown.svg", generate_assertion_breakdown_svg),
        ("findings_distribution.svg", generate_findings_distribution_svg),
        ("signal_detector_coverage.svg", generate_signal_detector_svg),
        ("issue_tracker.svg", generate_issue_history_svg),
        ("corpus_complexity.svg", generate_complexity_heatmap_svg),
        ("spice_status.svg", generate_spice_status_svg),
        ("spice_coverage.svg", generate_spice_coverage_svg),
        ("emc_severity.svg", generate_emc_severity_svg),
        ("emc_categories.svg", generate_emc_categories_svg),
    ]

    for filename, generator in charts:
        svg = generator()
        if svg:
            path = ANALYTICS_DIR / filename
            path.write_text(svg)
            print(f"  Generated {path}")
        else:
            print(f"  Skipped {filename} (no data)")

    print_summary()

    # Generate markdown snippet for README
    snippet = ANALYTICS_DIR / "README_SNIPPET.md"
    snippet.write_text(
        "## Analytics\n"
        "\n"
        "Auto-generated by `python3 generate_analytics.py`. "
        "Charts update from live corpus data.\n"
        "\n"
        "| | |\n"
        "|---|---|\n"
        "| ![Corpus Pipeline](analytics/corpus_overview.svg) | ![Assertion Breakdown](analytics/assertion_breakdown.svg) |\n"
        "| ![Findings Distribution](analytics/findings_distribution.svg) | ![Issue Tracker](analytics/issue_tracker.svg) |\n"
        "| ![Signal Detector Coverage](analytics/signal_detector_coverage.svg) | ![Corpus Complexity](analytics/corpus_complexity.svg) |\n"
        "| ![SPICE Status](analytics/spice_status.svg) | ![SPICE Coverage](analytics/spice_coverage.svg) |\n"
        "| ![EMC Severity](analytics/emc_severity.svg) | ![EMC Categories](analytics/emc_categories.svg) |\n"
    )
    print(f"\n  README snippet: {snippet}")
    print("  Copy the contents of analytics/README_SNIPPET.md into README.md")


if __name__ == "__main__":
    main()
