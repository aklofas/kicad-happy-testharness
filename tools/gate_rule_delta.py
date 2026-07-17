#!/usr/bin/env python3
"""Per-rule net-delta aggregation from raw gate snap.json pairs (RUNBOOK 26g).

Walks <gate-dir>/v131 and <gate-dir>/v14, counts findings[] rule_ids per unit
on both sides, prints global per-(analyzer, rule_id) baseline/candidate/net
and writes a per-unit delta JSON for repo attribution.
"""
import json
import os
import sys
from collections import Counter, defaultdict

gate_dir = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else None


def collect(side):
    units = {}
    root = os.path.join(gate_dir, side)
    for dirpath, _, files in os.walk(root):
        if 'snap.json' not in files:
            continue
        rel = os.path.relpath(dirpath, root)
        try:
            with open(os.path.join(dirpath, 'snap.json')) as f:
                env = json.load(f)
        except (json.JSONDecodeError, OSError):
            units[rel] = None
            continue
        units[rel] = Counter(
            f.get('rule_id') for f in env.get('findings', []) if isinstance(f, dict)
        )
    return units


base = collect('v131')
cand = collect('v14')

global_base = defaultdict(Counter)
global_cand = defaultdict(Counter)
per_unit = {}
for rel in sorted(set(base) | set(cand)):
    analyzer = rel.split(os.sep)[0]
    b = base.get(rel)
    c = cand.get(rel)
    if b is None or c is None:
        per_unit[rel] = {'error': f"missing side: base={b is not None} cand={c is not None}"}
        continue
    global_base[analyzer].update(b)
    global_cand[analyzer].update(c)
    if b != c:
        delta = {r: c.get(r, 0) - b.get(r, 0)
                 for r in set(b) | set(c) if c.get(r, 0) != b.get(r, 0)}
        per_unit[rel] = delta

rows = []
for analyzer in sorted(set(global_base) | set(global_cand)):
    for rule in sorted(set(global_base[analyzer]) | set(global_cand[analyzer])):
        nb = global_base[analyzer][rule]
        nc = global_cand[analyzer][rule]
        if nb != nc:
            rows.append((analyzer, rule, nb, nc, nc - nb))

rows.sort(key=lambda r: -abs(r[4]))
print(f"{'analyzer':<16} {'rule_id':<10} {'base':>8} {'cand':>8} {'net':>8}")
for analyzer, rule, nb, nc, d in rows:
    print(f"{analyzer:<16} {rule!s:<10} {nb:>8} {nc:>8} {d:>+8}")
print(f"\nunits with any rule-count delta: {sum(1 for v in per_unit.values() if 'error' not in v)}")
print(f"units missing one side: {sum(1 for v in per_unit.values() if isinstance(v, dict) and 'error' in v)}")

if out_path:
    with open(out_path, 'w') as f:
        json.dump(per_unit, f, indent=1, sort_keys=True)
    print(f"per-unit deltas -> {out_path}")
