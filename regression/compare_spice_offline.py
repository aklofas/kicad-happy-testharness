#!/usr/bin/env python3
"""Compare two spice-offline runs (RUNBOOK 26l): the `results/outputs/spice` trees that
`run/run_spice.py` wrote under two `KICAD_HAPPY_TESTHARNESS_DATA_DIR` roots, one per product.

Volatile leaves (run ids, timings, the data-dir prefix in paths) are masked; every other
difference is reported as (op, path-with-indices-wildcarded) with a count and one example
unit. Exit 0 when the two trees are identical after masking and share at least one report,
1 otherwise (two empty trees are no evidence), 2 on a bad tree.

    python3 regression/compare_spice_offline.py A_ROOT B_ROOT -o report.json
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

VOLATILE = frozenset({"run_id", "elapsed_s", "elapsed", "timestamp", "generated_at", "started_at",
                      "finished_at", "total_elapsed_s", "avg_per_file_s", "slowest", "duration_s",
                      "sim_time_s", "wall_s"})


def _files(root: Path) -> dict[str, Path]:
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".json") and not f.startswith("_"):      # _aggregate / _timing are run-level
                p = Path(dp) / f
                out[str(p.relative_to(root))] = p
    return out


def _norm(o, prefixes: tuple[str, ...]):
    if isinstance(o, dict):
        return {k: _norm(v, prefixes) for k, v in o.items() if k not in VOLATILE}
    if isinstance(o, list):
        return [_norm(v, prefixes) for v in o]
    if isinstance(o, str):
        for p in prefixes:
            o = o.replace(p, "<DATA_DIR>")
        return o
    return o


def _diff(x, y, p=""):
    out = []
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x:
                out.append(("added", f"{p}/{k}", None, y[k] if isinstance(y[k], (str, int, float, bool)) or y[k] == [] else "<obj>"))
            elif k not in y:
                out.append(("removed", f"{p}/{k}", "<obj>", None))
            else:
                out += _diff(x[k], y[k], f"{p}/{k}")
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            out.append(("len", p, len(x), len(y)))
        else:
            for i, (a, b) in enumerate(zip(x, y)):
                out += _diff(a, b, f"{p}/{i}")
    elif x != y:
        out.append(("changed", p, str(x)[:80], str(y)[:80]))
    return out


def compare(a_root: Path, b_root: Path) -> dict:
    fa, fb = _files(a_root), _files(b_root)
    prefixes = (str(a_root.resolve()), str(b_root.resolve()), str(a_root), str(b_root))
    kinds: collections.Counter = collections.Counter()
    examples: dict = {}
    identical = unreadable = 0
    for rel in sorted(set(fa) & set(fb)):
        try:
            x = json.loads(fa[rel].read_text(encoding="utf-8"))
            y = json.loads(fb[rel].read_text(encoding="utf-8"))
        except (OSError, ValueError):
            unreadable += 1
            continue
        d = _diff(_norm(x, prefixes), _norm(y, prefixes))
        if not d:
            identical += 1
        for op, path, before, after in d:
            key = f"{op} {re.sub(r'/\d+(?=/|$)', '/*', path)}"
            kinds[key] += 1
            examples.setdefault(key, {"unit": rel, "before": before, "after": after})
    return {
        "a_root": str(a_root), "b_root": str(b_root),
        "files": {"a": len(fa), "b": len(fb), "only_a": sorted(set(fa) - set(fb)), "only_b": sorted(set(fb) - set(fa))},
        "compared": len(set(fa) & set(fb)) - unreadable,
        "identical_after_mask": identical, "unreadable": unreadable,
        "differences": {k: {"count": v, "example": examples[k]} for k, v in kinds.most_common()},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("a_root")
    ap.add_argument("b_root")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    a, b = Path(args.a_root), Path(args.b_root)
    if not a.is_dir() or not b.is_dir():
        print("error: both roots must be directories", file=sys.stderr)
        return 2
    rep = compare(a, b)
    if args.output:
        Path(args.output).write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
    print(f"files a={rep['files']['a']} b={rep['files']['b']} only_a={len(rep['files']['only_a'])} "
          f"only_b={len(rep['files']['only_b'])} identical={rep['identical_after_mask']} unreadable={rep['unreadable']}")
    for k, v in rep["differences"].items():
        print(f"  {v['count']:7d}  {k}   e.g. {v['example']['unit'][:70]}")
    clean = (not rep["differences"] and not rep["files"]["only_a"] and not rep["files"]["only_b"]
             and not rep["unreadable"] and rep["compared"] > 0)
    print("spice-offline:", "IDENTICAL" if clean else
          ("NO COMPARED REPORTS" if rep["compared"] == 0 else "DIFFERENCES"))
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
