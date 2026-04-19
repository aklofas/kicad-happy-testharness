"""Unit tests for the schema-compatibility metadata block (kicad-happy v1.4 Track 1.4).

Every analyzer envelope at v1.4 has a required top-level `compat` block:

    {
        "minimum_consumer_version": str,        # e.g. "1.4.0"
        "deprecated_fields": list[str],         # dotted-paths scheduled for removal
        "experimental_fields": list[str],       # dotted-paths whose shape may change
    }

At v1.4, all three are emitted with `minimum_consumer_version == "1.4.0"` and
both lists empty across every analyzer. v1.5+ will populate the lists as fields
are scheduled for removal or added as best-effort experiments — the loose
isinstance-list check keeps this invariant useful as that happens.

Fixture strategy: scan fresh `results/outputs/<analyzer>/**.json` files at
schema_version 1.4.0. Skips cleanly per analyzer if no fresh fixture.
"""

TIER = "unit"

import glob
import json
import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"

CURRENT_SCHEMA_VERSION = "1.4.0"
EXPECTED_MINIMUM_CONSUMER_VERSION = "1.4.0"
ANALYZER_TYPES = ("schematic", "pcb", "gerber", "thermal", "emc")
# cross_analysis is invoked live; no persisted output dir.


def _fresh_outputs(analyzer_type, limit=50):
    type_dir = OUTPUTS_DIR / analyzer_type
    if not type_dir.exists():
        return
    candidates = []
    for f in glob.glob(str(type_dir / "**" / "*.json"), recursive=True):
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


def _check_compat_well_shaped(path, compat):
    """Return list of (path, problem) tuples. Empty = no problems."""
    problems = []
    if not isinstance(compat, dict):
        return [(path, f"compat is not a dict (got {type(compat).__name__})")]

    mcv = compat.get("minimum_consumer_version")
    if mcv != EXPECTED_MINIMUM_CONSUMER_VERSION:
        problems.append((
            path,
            f"minimum_consumer_version != {EXPECTED_MINIMUM_CONSUMER_VERSION!r}: got {mcv!r}"
        ))

    for field in ("deprecated_fields", "experimental_fields"):
        v = compat.get(field)
        if not isinstance(v, list):
            problems.append((
                path,
                f"compat.{field} is not a list (got {type(v).__name__}: {v!r})"
            ))
            continue
        # Every entry must be a string (dotted-path)
        for i, entry in enumerate(v):
            if not isinstance(entry, str):
                problems.append((
                    path,
                    f"compat.{field}[{i}] is not a string: {entry!r}"
                ))

    return problems


def _run_per_analyzer(analyzer_type):
    problems = []
    samples = list(_fresh_outputs(analyzer_type))
    if not samples:
        return None  # no fresh fixtures — skip
    for path, data in samples:
        if "compat" not in data:
            problems.append((path, "compat key missing from envelope"))
            continue
        problems.extend(_check_compat_well_shaped(path, data["compat"]))
    return problems


# ---------------------------------------------------------------------------
# Per-analyzer tests
# ---------------------------------------------------------------------------

def test_schematic_compat_block():
    problems = _run_per_analyzer("schematic")
    if problems is None:
        return
    assert not problems, f"{len(problems)} schematic compat issue(s). First few: {problems[:5]}"


def test_pcb_compat_block():
    problems = _run_per_analyzer("pcb")
    if problems is None:
        return
    assert not problems, f"{len(problems)} pcb compat issue(s). First few: {problems[:5]}"


def test_gerber_compat_block():
    problems = _run_per_analyzer("gerber")
    if problems is None:
        return
    assert not problems, f"{len(problems)} gerber compat issue(s). First few: {problems[:5]}"


def test_thermal_compat_block():
    problems = _run_per_analyzer("thermal")
    if problems is None:
        return
    assert not problems, f"{len(problems)} thermal compat issue(s). First few: {problems[:5]}"


def test_emc_compat_block():
    problems = _run_per_analyzer("emc")
    if problems is None:
        return
    assert not problems, f"{len(problems)} emc compat issue(s). First few: {problems[:5]}"


# ---------------------------------------------------------------------------
# Helper-correctness tests (don't depend on fixtures)
# ---------------------------------------------------------------------------

def test_check_compat_well_shaped_passes_canonical():
    canonical = {
        "minimum_consumer_version": "1.4.0",
        "deprecated_fields": [],
        "experimental_fields": [],
    }
    assert _check_compat_well_shaped("path", canonical) == []


def test_check_compat_well_shaped_catches_wrong_version():
    bad = {
        "minimum_consumer_version": "1.3.0",
        "deprecated_fields": [],
        "experimental_fields": [],
    }
    problems = _check_compat_well_shaped("p", bad)
    assert any("minimum_consumer_version" in pr[1] for pr in problems)


def test_check_compat_well_shaped_catches_non_list_fields():
    bad = {
        "minimum_consumer_version": "1.4.0",
        "deprecated_fields": "not a list",
        "experimental_fields": None,
    }
    problems = _check_compat_well_shaped("p", bad)
    assert any("deprecated_fields" in pr[1] for pr in problems)
    assert any("experimental_fields" in pr[1] for pr in problems)


def test_check_compat_well_shaped_accepts_populated_lists():
    """v1.5+ will start populating these. Test still accepts."""
    populated = {
        "minimum_consumer_version": "1.4.0",
        "deprecated_fields": ["legacy.field_a", "legacy.field_b"],
        "experimental_fields": ["experimental.feature_x"],
    }
    assert _check_compat_well_shaped("path", populated) == []


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
