"""Unit tests for the formal inputs/provenance block (kicad-happy v1.4 Track 1.3).

Every analyzer envelope at v1.4 has a required top-level `inputs` block:

    {
        "source_files": list[str],
        "source_hashes": {path: sha256_hex},
        "run_id": "YYYYMMDDTHHMMSSZ-<6 hex>",
        "upstream_artifacts": {stage: UpstreamArtifact},
        "config_hash": str | None,
    }

Where `UpstreamArtifact = {path, sha256, schema_version, run_id}`.

Raw-input analyzers (schematic, PCB, gerber) emit `upstream_artifacts: {}`.
Derivative analyzers (thermal, EMC, cross_analysis) populate the map with
keys for each upstream stage they consumed.

This test scans fresh `results/outputs/*/**.json` fixtures and enforces:
  - inputs block is present and well-shaped on every fresh 1.4.0 envelope
  - source_files non-empty
  - source_hashes maps every source_files entry to a 64-hex string
  - run_id matches the canonical regex
  - raw analyzers carry empty upstream_artifacts
  - derivative analyzers carry expected stage keys with all 4 required fields

Skips cleanly if no fresh fixtures exist for an analyzer type.
"""

TIER = "unit"

import glob
import json
import os
import re
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"

CURRENT_SCHEMA_VERSION = "1.4.0"

RAW_ANALYZERS = {"schematic", "pcb", "gerber"}

# For each derivative analyzer: the upstream stages that MUST be present on
# every fresh fixture. Thermal needs both (junction-temp model needs schematic
# components AND PCB thermal pads). EMC defaults to schematic-only because
# some EMC checks (e.g. clock topology) run schematic-only when no PCB pair
# exists; PCB is added opportunistically when the file is available.
DERIVATIVE_REQUIRED_STAGES = {
    "thermal": {"schematic", "pcb"},
    "emc": {"schematic"},
    "cross_analysis": {"schematic", "pcb"},
}

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _check_inputs_well_shaped(path, inputs):
    """Return list of (path, problem) tuples. Empty = no problems."""
    problems = []
    if not isinstance(inputs, dict):
        return [(path, f"inputs is not a dict (got {type(inputs).__name__})")]

    # source_files non-empty
    src_files = inputs.get("source_files")
    if not isinstance(src_files, list) or not src_files:
        problems.append((path, f"source_files missing or empty: {src_files!r}"))

    # source_hashes covers every source_files entry; values are 64-hex
    src_hashes = inputs.get("source_hashes")
    if not isinstance(src_hashes, dict):
        problems.append((path, f"source_hashes is not a dict: {type(src_hashes).__name__}"))
    elif isinstance(src_files, list):
        for sf in src_files:
            h = src_hashes.get(sf)
            if not isinstance(h, str) or not SHA256_RE.match(h):
                problems.append((path, f"source_hashes[{sf!r}] not a valid sha256: {h!r}"))

    # run_id matches canonical regex
    run_id = inputs.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.match(run_id):
        problems.append((path, f"run_id does not match {RUN_ID_RE.pattern}: {run_id!r}"))

    # upstream_artifacts is a dict (may be empty)
    ua = inputs.get("upstream_artifacts")
    if not isinstance(ua, dict):
        problems.append((path, f"upstream_artifacts is not a dict: {type(ua).__name__}"))

    # config_hash: optional, must be str or None when present
    cfg = inputs.get("config_hash", None)
    if cfg is not None and not isinstance(cfg, str):
        problems.append((path, f"config_hash is neither str nor None: {type(cfg).__name__}"))

    return problems


def _check_upstream_artifact(path, stage, art):
    problems = []
    if not isinstance(art, dict):
        return [(path, f"upstream_artifacts[{stage!r}] is not a dict")]
    for field in ("path", "sha256", "schema_version", "run_id"):
        if field not in art:
            problems.append((path, f"upstream_artifacts[{stage!r}].{field} missing"))
            continue
        v = art[field]
        if not isinstance(v, str):
            problems.append((path, f"upstream_artifacts[{stage!r}].{field} not a string: {type(v).__name__}"))
    return problems


def _run_per_analyzer(analyzer_type, required_upstream_stages):
    """Returns list of (path, problem) for an analyzer type.

    required_upstream_stages: empty set for raw analyzers, set of stage names
    that MUST be present for derivative analyzers. Additional stages beyond
    the required set are allowed (e.g. EMC may opportunistically include PCB).
    """
    problems = []
    samples = list(_fresh_outputs(analyzer_type))
    if not samples:
        return None  # signal to skip
    for path, data in samples:
        if "inputs" not in data:
            problems.append((path, "inputs key missing from envelope"))
            continue
        inputs = data["inputs"]
        problems.extend(_check_inputs_well_shaped(path, inputs))

        ua = inputs.get("upstream_artifacts", {})
        if isinstance(ua, dict):
            actual_stages = set(ua.keys())
            if required_upstream_stages == set():
                # Raw analyzer — must have empty upstream_artifacts
                if actual_stages:
                    problems.append((
                        path,
                        f"raw analyzer expected empty upstream_artifacts, got {sorted(actual_stages)}"
                    ))
            else:
                # Derivative analyzer — must have all REQUIRED stages
                # (additional stages allowed; e.g. EMC may opportunistically add PCB).
                missing = required_upstream_stages - actual_stages
                if missing:
                    problems.append((
                        path,
                        f"derivative analyzer missing required upstream stages {sorted(missing)} "
                        f"(have {sorted(actual_stages)})"
                    ))
                # Per-stage shape check (for every stage actually present)
                for stage in actual_stages:
                    problems.extend(_check_upstream_artifact(path, stage, ua[stage]))
    return problems


# ---------------------------------------------------------------------------
# Per-analyzer tests — raw-input analyzers
# ---------------------------------------------------------------------------

def test_schematic_inputs_block():
    problems = _run_per_analyzer("schematic", set())
    if problems is None:
        return  # no fresh fixtures
    assert not problems, f"{len(problems)} schematic inputs-block issue(s). First few: {problems[:5]}"


def test_pcb_inputs_block():
    problems = _run_per_analyzer("pcb", set())
    if problems is None:
        return
    assert not problems, f"{len(problems)} pcb inputs-block issue(s). First few: {problems[:5]}"


def test_gerber_inputs_block():
    problems = _run_per_analyzer("gerber", set())
    if problems is None:
        return
    assert not problems, f"{len(problems)} gerber inputs-block issue(s). First few: {problems[:5]}"


# ---------------------------------------------------------------------------
# Per-analyzer tests — derivative analyzers
# ---------------------------------------------------------------------------

def test_thermal_inputs_block_with_upstream():
    problems = _run_per_analyzer("thermal", DERIVATIVE_REQUIRED_STAGES["thermal"])
    if problems is None:
        return
    assert not problems, f"{len(problems)} thermal inputs-block issue(s). First few: {problems[:5]}"


def test_emc_inputs_block_with_upstream():
    problems = _run_per_analyzer("emc", DERIVATIVE_REQUIRED_STAGES["emc"])
    if problems is None:
        return
    assert not problems, f"{len(problems)} emc inputs-block issue(s). First few: {problems[:5]}"


# cross_analysis is invoked live (no persisted output dir). Skip per-fixture
# test for it; the contract test (test_schema_drift) covers its --schema shape.


# ---------------------------------------------------------------------------
# Helper / regex tests (don't depend on fixtures)
# ---------------------------------------------------------------------------

def test_run_id_regex_accepts_canonical_form():
    assert RUN_ID_RE.match("20260418T123456Z-a1b2c3")
    assert RUN_ID_RE.match("99991231T235959Z-ffffff")


def test_run_id_regex_rejects_malformed():
    assert not RUN_ID_RE.match("20260418-a1b2c3")           # no T
    assert not RUN_ID_RE.match("20260418T123456-a1b2c3")    # no Z
    assert not RUN_ID_RE.match("20260418T123456Z-XYZ123")   # non-hex suffix
    assert not RUN_ID_RE.match("20260418T123456Z-abc")      # too short hex
    assert not RUN_ID_RE.match("")


def test_sha256_regex_canonical():
    assert SHA256_RE.match("a" * 64)
    assert SHA256_RE.match("0" * 64)
    assert not SHA256_RE.match("a" * 63)                    # too short
    assert not SHA256_RE.match("A" * 64)                    # uppercase rejected
    assert not SHA256_RE.match("g" * 64)                    # non-hex
    assert not SHA256_RE.match("0x" + "a" * 62)             # hex prefix rejected


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
