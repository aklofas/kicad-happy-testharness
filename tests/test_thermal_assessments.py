"""Unit test for thermal findings/assessments separation invariant.

At kicad-happy v1.4 (Track 1.2), per-component junction-temperature
estimates (rule_id=TH-DET) moved from `findings[]` to a new top-level
`assessments[]` list. Findings are normative (rolled into trust_summary,
severity-counted); assessments are informational measurements (not
trust-summarized). The two MUST stay separate at the envelope level.

This test enforces:
- Direction 1: TH-DET never appears in `findings[]` (moved out at v1.4).
- Direction 2: every entry in `assessments[]` carries `rule_id == "TH-DET"`
  (TH-DET is the only consumer at v1.4; future detectors may add to this
  set, in which case widen the allow-list).

Fixture strategy: scan all fresh `results/outputs/thermal/*.json` files
with `schema_version == "1.4.0"`. Skips cleanly if no fresh fixture
(corpus not regen'd post-v1.4).
"""

TIER = "unit"

import glob
import json
import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs" / "thermal"

CURRENT_SCHEMA_VERSION = "1.4.0"
ASSESSMENT_RULE_IDS = {"TH-DET"}  # widen as new assessment-emitting detectors land


def _fresh_thermal_outputs(limit=200):
    """Yield (path, data) for fresh 1.4.0 thermal outputs."""
    if not OUTPUTS_DIR.exists():
        return
    candidates = []
    for f in glob.glob(str(OUTPUTS_DIR / "**" / "*.json"), recursive=True):
        if "_aggregate" in f or "_timing" in f:
            continue
        try:
            mtime = os.path.getmtime(f)
        except OSError:
            continue
        candidates.append((mtime, f))
    candidates.sort(reverse=True)

    yielded = 0
    for _, f in candidates:
        if yielded >= limit:
            break
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("schema_version") != CURRENT_SCHEMA_VERSION:
            continue
        yield f, d
        yielded += 1


def test_th_det_absent_from_findings():
    """Direction 1: TH-DET must never appear in findings[] post-v1.4."""
    samples = list(_fresh_thermal_outputs())
    if not samples:
        return  # no fresh fixtures — skip cleanly
    offenders = []
    for path, data in samples:
        for finding in data.get("findings", []):
            if finding.get("rule_id") == "TH-DET":
                offenders.append((path, finding.get("ref", "?")))
    assert not offenders, (
        f"TH-DET found in findings[] in {len(offenders)} place(s) "
        f"(expected only in assessments[] post-Track 1.2). "
        f"First few: {offenders[:5]}"
    )


def test_assessments_contain_only_known_rule_ids():
    """Direction 2: every assessments[] entry has a known rule_id.

    Currently {TH-DET}. Widen ASSESSMENT_RULE_IDS as new detectors emit.
    """
    samples = list(_fresh_thermal_outputs())
    if not samples:
        return
    offenders = []
    for path, data in samples:
        for assessment in data.get("assessments", []):
            rid = assessment.get("rule_id")
            if rid not in ASSESSMENT_RULE_IDS:
                offenders.append((path, rid))
    assert not offenders, (
        f"assessments[] contains unknown rule_id in {len(offenders)} place(s). "
        f"Allowed: {ASSESSMENT_RULE_IDS}. First few: {offenders[:5]}"
    )


def test_assessments_field_always_present():
    """assessments[] is REQUIRED on every thermal envelope at v1.4."""
    samples = list(_fresh_thermal_outputs())
    if not samples:
        return
    missing = [path for path, data in samples if "assessments" not in data]
    assert not missing, (
        f"`assessments` key missing from {len(missing)} thermal output(s) — "
        f"required at v1.4. First few: {missing[:5]}"
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith("test_") and callable(fn)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
