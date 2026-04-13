#!/usr/bin/env python3
"""Generate negative assertions from false-positive findings.

Scans Layer 3 findings for "incorrect" items that document false positives,
misclassifications, or overcounts. Generates not_contains_match or max_count
assertions to prevent regressions where a fix is later undone.

Usage:
    python3 regression/seed_negative.py --all --dry-run
    python3 regression/seed_negative.py --repo 0x42 --dry-run
    python3 regression/seed_negative.py --all --apply
"""

import argparse
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from findings import _iter_findings_files
from utils import (
    DATA_DIR,
    DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
)

# Keywords that indicate a false positive in finding descriptions
FP_KEYWORDS = re.compile(
    r"false.?positive|misclassif|overcounted|should not|incorrectly|"
    r"not a |not an |wrongly|erroneously|spurious",
    re.IGNORECASE,
)


def scan_findings_for_negatives(repo_name=None):
    """Find findings with 'incorrect' items suitable for negative assertions.

    Returns list of dicts with keys: repo, project, finding_id, incorrect_item,
    analyzer_section, has_check.
    """
    candidates = []

    for repo, proj, ff in _iter_findings_files(repo_name):
        try:
            data = json.loads(ff.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        for finding in data.get("findings", []):
            fid = finding.get("id", "?")
            for inc in finding.get("incorrect", []):
                desc = inc.get("description", "")
                section = inc.get("analyzer_section", "")
                check = inc.get("check")

                # Prioritize items with explicit check fields
                has_check = check is not None and isinstance(check, dict)

                # Also accept items with FP keywords in description
                if not has_check and not FP_KEYWORDS.search(desc):
                    continue

                candidates.append({
                    "repo": repo,
                    "project": proj,
                    "finding_id": fid,
                    "description": desc[:200],
                    "analyzer_section": section,
                    "check": check,
                    "has_check": has_check,
                })

    return candidates


def generate_negative_assertions(candidates):
    """Convert candidates into assertion dicts.

    Uses the check field if present, otherwise generates a generic
    assertion from the description.
    """
    assertions_by_key = {}  # (repo, project) -> list of assertions

    for i, cand in enumerate(candidates):
        key = (cand["repo"], cand["project"])

        if cand["has_check"]:
            check = cand["check"]
            assertion = {
                "id": f"NEG-{i+1:06d}",
                "description": (f"[Negative] {cand['description'][:120]} "
                                f"(from {cand['finding_id']})"),
                "check": check,
                "aspirational": True,
            }
        else:
            # Generate generic assertion from description
            assertion = {
                "id": f"NEG-{i+1:06d}",
                "description": (f"[Negative] {cand['description'][:120]} "
                                f"(from {cand['finding_id']})"),
                "check": {
                    "path": cand["analyzer_section"] or "signal_analysis",
                    "op": "exists",
                },
                "aspirational": True,
                "_needs_manual_check": True,
            }

        assertions_by_key.setdefault(key, []).append(assertion)

    return assertions_by_key


def _scan_repo_worker(repo_name):
    """Worker function for parallel scanning. Returns (repo, candidates)."""
    return repo_name, scan_findings_for_negatives(repo_name)


def _write_repo_worker(repo, project, assertions):
    """Worker function for parallel writing. Returns (repo/project, written)."""
    atype = "schematic"  # default
    out_dir = DATA_DIR / repo / project / "assertions" / atype
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find the file_pattern from existing assertion files
    file_pattern = None
    for existing in out_dir.glob("*.json"):
        try:
            ed = json.loads(existing.read_text(encoding="utf-8"))
            file_pattern = ed.get("file_pattern")
            atype = ed.get("analyzer_type", atype)
            if file_pattern:
                break
        except Exception:
            continue

    if not file_pattern:
        return f"{repo}/{project}", 0

    outfile = out_dir / f"{file_pattern}_negative.json"
    data = {
        "file_pattern": file_pattern,
        "analyzer_type": atype,
        "generated_by": "seed_negative.py",
        "evidence_source": "auto_seeded",
        "assertions": assertions,
    }
    outfile.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return f"{repo}/{project}", 1


def main():
    parser = argparse.ArgumentParser(
        description="Generate negative assertions from false-positive findings")
    add_repo_filter_args(parser)
    parser.add_argument("--all", action="store_true", help="Process all repos")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Number of parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated (default)")
    parser.add_argument("--apply", action="store_true",
                        help="Write assertion files")
    args = parser.parse_args()

    resolved = resolve_repos(args)
    if resolved is None and not args.all:
        print("Specify --repo, --cross-section, --repo-list, or --all", file=sys.stderr)
        sys.exit(1)

    jobs = args.jobs

    # Scan phase: collect candidates
    if resolved is not None:
        # Process specific repos
        if jobs <= 1 or len(resolved) <= 1:
            candidates = []
            for repo in resolved:
                candidates.extend(scan_findings_for_negatives(repo))
        else:
            candidates = []
            with ProcessPoolExecutor(max_workers=jobs) as pool:
                futures = {pool.submit(_scan_repo_worker, repo): repo
                           for repo in resolved}
                for future in as_completed(futures):
                    _repo, repo_candidates = future.result()
                    candidates.extend(repo_candidates)
    else:
        # --all: scan everything at once (no per-repo breakdown needed)
        candidates = scan_findings_for_negatives(None)

    print(f"Found {len(candidates)} negative assertion candidates")

    with_check = sum(1 for c in candidates if c["has_check"])
    without_check = len(candidates) - with_check
    print(f"  With explicit check field: {with_check}")
    print(f"  From FP keywords only:     {without_check}")

    if not candidates:
        return

    assertions_by_key = generate_negative_assertions(candidates)

    total_assertions = sum(len(v) for v in assertions_by_key.values())
    print(f"\nGenerated {total_assertions} negative assertions "
          f"across {len(assertions_by_key)} projects")

    if args.apply and not args.dry_run:
        written = 0
        if jobs <= 1 or len(assertions_by_key) <= 1:
            for (repo, project), assertions in assertions_by_key.items():
                _, count = _write_repo_worker(repo, project, assertions)
                written += count
        else:
            with ProcessPoolExecutor(max_workers=jobs) as pool:
                futures = {
                    pool.submit(_write_repo_worker, repo, project, assertions): (repo, project)
                    for (repo, project), assertions in assertions_by_key.items()
                }
                for future in as_completed(futures):
                    _, count = future.result()
                    written += count

        print(f"Wrote {written} assertion files")
    else:
        # Dry run: show samples
        for (repo, project), assertions in list(assertions_by_key.items())[:5]:
            print(f"\n  {repo}/{project}:")
            for a in assertions[:3]:
                check_str = "explicit" if not a.get("_needs_manual_check") else "needs review"
                print(f"    {a['id']}: {a['description'][:80]} [{check_str}]")
            if len(assertions) > 3:
                print(f"    ... and {len(assertions) - 3} more")


if __name__ == "__main__":
    main()
