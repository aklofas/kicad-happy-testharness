#!/usr/bin/env python3
"""Regression diff for v1.3 vs v1.4 ``--only-deterministic`` envelope JSONs.

Compares two analyzer envelope JSONs (any of the 6 envelope types) and
reports whether v1.4 has any Layer 1 regressions versus v1.3. Used to
gate the v1.4 release across the harness corpus.

Allowed differences:
- Envelope-level: schema_version, analyzer_type, inputs, compat,
  capability_mode, run_id, trust_summary
- Finding-level: finding_id, schema_era, capability_mode_ref, provenance
- Findings moved between findings[] and assessments[] (v1.2 split)
- New v1.4 findings: rule_ids in NEW_V14_RULES are counted as
  additions, not regressions

Hard fails (exit 1):
- Any v1.3 finding/assessment whose canonical key is absent in v1.4
- Any severity downgrade on a shared canonical key

Usage:
    python3 tools/regression_diff.py --before v13.json --after v14.json
    python3 tools/regression_diff.py --before v13.json --after v14.json --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# New v1.4 finding surfaces. None of these existed as findings in v1.3.1,
# so they are clean additions with no `disappeared` risk — counted as
# additions, never regressions:
#   AM/OV/TJ/FT/PM/EX  Phase 4c detectors, fire under datasheet schema
#                      availability.
#   VD-001..VD-004     voltage/power-derating audit, migrated out of the
#                      v1.3.1 nested ``result["voltage_derating"]`` section
#                      into rich findings[].
#   XT-001             Phase 4b gave the crystal load-cap check a genuine
#                      heuristic path (target_load_source=
#                      "parsed_from_value"): the crystal value string
#                      carries an explicit pF spec and the board's C1/C2
#                      caps compute a CL_eff >10% off it. The datasheet
#                      branch is structurally unreachable in v1.4
#                      (DatasheetFacts.crystal / CrystalBlock is v1.5), so
#                      every XT-001 finding here is heuristic — additive,
#                      like VD-*. (Confirmed by main-repo; the original
#                      handoff mis-classified it as a datasheet upgrade.)
NEW_V14_RULES = {
    'AM-001', 'OV-001', 'TJ-001', 'FT-001', 'PM-001', 'EX-001',
    'VD-001', 'VD-002', 'VD-003', 'VD-004', 'XT-001',
    # rc.2 additions (Track 4 polish, c904bb3..6b6e622): per-color LED Vf
    # floor (LA-004), source-via-bridged-jumper info (RS-003), lifecycle
    # audit "not attached" info reminder (LC-007).
    'LA-004', 'RS-003', 'LC-007',
    # rc.3 addition (Phase A-D F5, 8e63900): high-DNP-rate BOM audit.
    # Only matters for gates whose baseline predates BL-001.
    'BL-001',
    # This set is CLOSED as of v2.0: per-rule budgeting for new heuristic
    # rule families is retired (v2.0 spec §2). Do not add v2.0+ entries.
}

# Phase 4b upgraded detectors whose datasheet-backed branch is gated off
# until AnalysisContext.cache_dir is wired. Heuristic-mode logic preserves
# v1.3 behaviour bit-for-bit. Any new additions in this set should appear
# only when the datasheet path activates — flag for manual review rather
# than auto-pass. Should be ~0 corpus-wide.
UPGRADED_V14_RULES = {'PU-001', 'LR-001'}

SEVERITY_ORDER = {'info': 0, 'warning': 1, 'error': 2}


def _canon_refs(seq):
    """Stable string for a list-like field — includes ALL items, sorted.

    LOG 6 (audit Highest-Risk #15): the original ``_first()`` helper only
    keyed on the first ref/net/pin, so a regression that dropped secondary
    refs (e.g. components ``["U1","C4","C5"]`` → ``["U1"]`` from one v1.4
    detector change) collided into the same canonical key as the v1.3
    finding. The diff engine then mis-reported the loss as a no-op.
    Including the full sorted set turns that loss into a key change
    (disappeared old key + new key with truncated refs) so it surfaces.
    """
    if not seq:
        return ''
    items = []
    for item in seq:
        if isinstance(item, dict):
            items.append(item.get('ref') or item.get('number')
                         or json.dumps(item, sort_keys=True))
        else:
            items.append(str(item))
    return ','.join(sorted(items))


# A run of two-or-more comma-separated identifier-like tokens (net names,
# component refs, pin names). v1.4's deterministic path can emit these in a
# different order than v1.3 because the underlying collection is a set —
# cosmetic churn, not a finding regression. Normalizing sorts each such run
# so the canonical key is stable across the reordering.
_COMMA_RUN = re.compile(r'[\w/.+\-]+(?:,\s*[\w/.+\-]+)+')
_WS_RUN = re.compile(r'\s+')


def _norm_summary(summary):
    """Sort comma-separated token runs inside a summary string AND collapse
    whitespace runs to single spaces so that ordering / formatting churn
    doesn't change the canonical key.

    LOG 6: whitespace-only diffs (e.g. double-space → single-space, trailing
    whitespace) on otherwise-identical summaries used to produce different
    canonical keys, causing spurious 'disappeared + new' pairs. The
    ``_WS_RUN`` collapse fixes that without losing any real content."""
    text = str(summary or '')

    def _sort_run(m):
        return ', '.join(sorted(p.strip() for p in m.group(0).split(',')))

    text = _COMMA_RUN.sub(_sort_run, text)
    text = _WS_RUN.sub(' ', text).strip()
    return text[:120]


def _canon_key(f):
    """Canonical identity for cross-version finding comparison.

    Excludes severity (so we can detect downgrades on shared findings)
    and excludes v1.4-only fields (finding_id, schema_era). Includes the
    FULL sorted ref/net/pin sets via :func:`_canon_refs` so dropped
    secondary refs change the key (audit Highest-Risk #15 / LOG 6).
    """
    return (
        str(f.get('rule_id') or ''),
        _canon_refs(f.get('components') or []),
        _canon_refs(f.get('nets') or []),
        _canon_refs(f.get('pins') or []),
        _norm_summary(f.get('summary')),
    )


def is_deep_review_doc(doc):
    """True if ``doc`` is a deep_review.json document (v2.0 spec §3.C).

    deep_review.json is LLM-written and NON-DETERMINISTIC BY DESIGN — it is
    permanently excluded from regression-diff scope (v2.0 spec §7,
    load-bearing). Shape: no ``analyzer_type``; carries a ``quarantined``
    list next to ``findings``.
    """
    if not isinstance(doc, dict):
        return False
    if doc.get('analyzer_type'):
        return False
    return 'quarantined' in doc


def _collect_observations(envelope):
    """Return findings ∪ assessments. Handles v1.2 split: assessments
    carry info-level rule_ids (e.g. TH-DET) that lived inside findings[]
    in v1.3. Comparing the union avoids false 'disappeared' reports for
    findings that simply moved key.

    deep_review findings (detector='deep_review' or finding_id prefixed
    'deep_review:') are dropped: non-deterministic by design, permanently
    out of diff scope (v2.0 spec §7) even if a future artifact merges
    them into an envelope.
    """
    obs = list(envelope.get('findings') or [])
    obs.extend(envelope.get('assessments') or [])
    return [
        f for f in obs
        if not (isinstance(f, dict) and (
            f.get('detector') == 'deep_review'
            or str(f.get('finding_id') or '').startswith('deep_review:')))
    ]


def _index(observations):
    idx = {}
    for f in observations:
        if not isinstance(f, dict):
            continue
        idx.setdefault(_canon_key(f), []).append(f)
    return idx


def _sev_cmp(before, after):
    b = SEVERITY_ORDER.get(before, -1)
    a = SEVERITY_ORDER.get(after, -1)
    if a < b:
        return 'downgrade'
    if a > b:
        return 'upgrade'
    return 'unchanged'


def diff(before_obs, after_obs):
    before_idx = _index(before_obs)
    after_idx = _index(after_obs)

    disappeared, severity_changes, shared = [], [], []
    new_known, new_upgraded, new_unknown = [], [], []

    for key, b_list in before_idx.items():
        a_list = after_idx.get(key, [])
        for i, b in enumerate(b_list):
            if i >= len(a_list):
                disappeared.append(b)
                continue
            a = a_list[i]
            cmp = _sev_cmp(b.get('severity'), a.get('severity'))
            if cmp != 'unchanged':
                severity_changes.append({
                    'rule_id': b.get('rule_id'),
                    'components': b.get('components'),
                    'nets': b.get('nets'),
                    'before_severity': b.get('severity'),
                    'after_severity': a.get('severity'),
                    'kind': cmp,
                })
            else:
                shared.append(b)

    for key, a_list in after_idx.items():
        b_count = len(before_idx.get(key, []))
        for a in a_list[b_count:]:
            rid = a.get('rule_id', '')
            if rid in NEW_V14_RULES:
                new_known.append(a)
            elif rid in UPGRADED_V14_RULES:
                new_upgraded.append(a)
            else:
                new_unknown.append(a)

    return {
        'disappeared': disappeared,
        'severity_changes': severity_changes,
        'shared': shared,
        'new_known': new_known,
        'new_upgraded': new_upgraded,
        'new_unknown': new_unknown,
    }


def verdict(d):
    downgrades = [c for c in d['severity_changes'] if c['kind'] == 'downgrade']
    if d['disappeared']:
        return 'FAIL', f"{len(d['disappeared'])} findings disappeared"
    if downgrades:
        return 'FAIL', f"{len(downgrades)} severity downgrades"
    if d['new_unknown']:
        return 'WARN', f"{len(d['new_unknown'])} new findings with unknown rule_ids"
    return 'PASS', 'no regressions'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--before', required=True, help='v1.3 envelope JSON path')
    ap.add_argument('--after', required=True, help='v1.4 envelope JSON path')
    ap.add_argument('--json', action='store_true', help='emit machine-readable JSON report')
    args = ap.parse_args(argv)

    before = json.loads(Path(args.before).read_text())
    after = json.loads(Path(args.after).read_text())

    if is_deep_review_doc(before) or is_deep_review_doc(after):
        print("SKIP: deep_review.json is excluded from regression-diff "
              "scope (non-deterministic by design, v2.0 spec §7)")
        sys.exit(0)

    before_obs = _collect_observations(before)
    after_obs = _collect_observations(after)
    d = diff(before_obs, after_obs)
    result, reason = verdict(d)

    downgrades = [c for c in d['severity_changes'] if c['kind'] == 'downgrade']
    upgrades = [c for c in d['severity_changes'] if c['kind'] == 'upgrade']

    report = {
        'verdict': result,
        'reason': reason,
        'before_total': len(before_obs),
        'after_total': len(after_obs),
        'shared_count': len(d['shared']),
        'disappeared_count': len(d['disappeared']),
        'severity_downgrades': len(downgrades),
        'severity_upgrades': len(upgrades),
        'new_known_count': len(d['new_known']),
        'new_upgraded_count': len(d['new_upgraded']),
        'new_unknown_count': len(d['new_unknown']),
        'disappeared': d['disappeared'],
        'severity_changes': d['severity_changes'],
        'new_unknown': d['new_unknown'],
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Verdict: {result} — {reason}")
        print(f"  before: {report['before_total']}  after: {report['after_total']}  shared: {report['shared_count']}")
        print(f"  disappeared: {report['disappeared_count']}")
        print(f"  severity downgrades: {report['severity_downgrades']}  upgrades: {report['severity_upgrades']}")
        print(f"  new known v1.4 (NEW_V14_RULES): {report['new_known_count']}")
        print(f"  new upgraded v1.4 (UPGRADED_V14_RULES): {report['new_upgraded_count']}")
        print(f"  new unknown rule_ids: {report['new_unknown_count']}")
        if d['disappeared']:
            print("\nDISAPPEARED FINDINGS (top 10):")
            for f in d['disappeared'][:10]:
                print(f"  {f.get('rule_id')} on {f.get('components')}: {(f.get('summary') or '')[:80]}")
        if downgrades:
            print("\nSEVERITY DOWNGRADES:")
            for c in downgrades:
                print(f"  {c['rule_id']} on {c['components']}: {c['before_severity']} → {c['after_severity']}")
        if d['new_unknown']:
            print("\nNEW UNKNOWN RULE_IDS (top 10):")
            for f in d['new_unknown'][:10]:
                print(f"  {f.get('rule_id')} on {f.get('components')}: {(f.get('summary') or '')[:80]}")

    sys.exit(0 if result == 'PASS' else 1)


if __name__ == '__main__':
    main()
