"""Contract test: ``--only-deterministic`` must produce byte-stable output
regardless of ``PYTHONHASHSEED``.

Audit LOG 7 / Roadmap static-audit #16 (2026-05-15): the ``--only-deterministic``
flag was added in v1.4 with the contract that downstream consumers can rely on
analyzer output being reproducible run-to-run. But the flag does NOT currently
pin ``PYTHONHASHSEED`` itself — several detectors (RC-001/RC-DET, DO-DET, etc.)
iterate hash-seeded sets, so the emitted JSON's ``findings[]`` ordering and
nested ``component/net/pin/evidence`` list ordering depend on the interpreter's
random hash seed.

**This test is intentionally RED today.** It locks the contract that
``--only-deterministic`` SHOULD provide; the product-side fix (sort findings +
nested lists at the analyzer level, OR have ``--only-deterministic`` pin
``PYTHONHASHSEED=0`` itself) is deferred to v1.5 (roadmap static-audit #16).
Marked ``xfail(strict=True)`` so that when the v1.5 fix lands, the test
FLIPS to XPASS, the suite fails loudly, and someone must remove the xfail
marker — turning the test into a positive lock for the fix.

The v1.4 Layer 1 regression gate currently works around this gap by pinning
``PYTHONHASHSEED=0`` for every analyzer subprocess; see RUNBOOK Checklist 16.

Marked TIER=online — spawns 3 analyzer subprocesses (one per hash-seed) on
the commodorelcd corpus.
"""

from __future__ import annotations

TIER = "online"

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

REPOS_DIR = HARNESS_ROOT / "repos"
TEST_REPO = "jgrip/commodorelcd"
SCH_PATH = REPOS_DIR / TEST_REPO / "commodorelcd.kicad_sch"
ANALYZE_SCHEMATIC = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"

SUBPROC_TIMEOUT_S = 180


def _skip_unless_corpus_and_kh_present():
    if not SCH_PATH.is_file():
        pytest.skip(f"missing corpus repo {TEST_REPO!r} (run checkout.py)")
    if not ANALYZE_SCHEMATIC.is_file():
        pytest.skip("KICAD_HAPPY_DIR scripts missing")


def _run_schematic_with_seed(seed: str, output_path: Path) -> None:
    """Run analyze_schematic.py with the given PYTHONHASHSEED value, writing
    JSON to output_path. Uses ``--only-deterministic`` to scope the contract
    being tested."""
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = seed
    r = subprocess.run(
        [sys.executable, str(ANALYZE_SCHEMATIC), str(SCH_PATH),
         "--output", str(output_path), "--only-deterministic",
         "--no-hierarchy"],
        capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S, env=env,
    )
    assert r.returncode == 0, (
        f"analyze_schematic failed with PYTHONHASHSEED={seed!r}: "
        f"rc={r.returncode}\nstderr (last 500): {r.stderr[-500:]}"
    )


def _strip_volatile_fields(envelope: dict) -> dict:
    """Drop fields that are SUPPOSED to vary between runs (timestamps,
    run_ids, capability_mode pointers). Hash-seed determinism is about
    finding/list ORDER, not about provenance fields that legitimately
    change every invocation."""
    blob = json.loads(json.dumps(envelope))  # deep copy
    blob.pop("capability_mode_ref", None)
    inputs = blob.get("inputs") or {}
    inputs.pop("run_id", None)
    inputs.pop("timestamp", None)
    inputs.pop("ran_at", None)
    if "inputs" in blob:
        blob["inputs"] = inputs
    # Strip any nested timestamp keys at the top level too
    for key in ("generated_at", "timestamp", "ran_at"):
        blob.pop(key, None)
    return blob


# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="LOG 7: --only-deterministic doesn't pin PYTHONHASHSEED itself; "
           "v1.5 product fix deferred (roadmap static-audit #16). When v1.5 "
           "fix lands this XPASSES → remove xfail to convert into a positive "
           "lock.",
)
def test_only_deterministic_output_is_hash_seed_invariant(tmp_path):
    """Run analyze_schematic.py 3 times with PYTHONHASHSEED=0, =1, =random.
    With ``--only-deterministic`` set, the resulting envelopes (modulo
    legitimately-volatile provenance fields) MUST be byte-equal.

    Today: RED — hash-seed-iterating detectors emit findings in
    different order. v1.5 fix: sort findings + nested
    component/net/pin/evidence lists at the analyzer level."""
    _skip_unless_corpus_and_kh_present()

    seed0_path = tmp_path / "seed_0.json"
    seed1_path = tmp_path / "seed_1.json"
    seedrand_path = tmp_path / "seed_random.json"

    _run_schematic_with_seed("0", seed0_path)
    _run_schematic_with_seed("1", seed1_path)
    _run_schematic_with_seed("random", seedrand_path)

    e0 = _strip_volatile_fields(json.loads(seed0_path.read_text()))
    e1 = _strip_volatile_fields(json.loads(seed1_path.read_text()))
    er = _strip_volatile_fields(json.loads(seedrand_path.read_text()))

    # Hash-based comparison keeps the assertion message small. The
    # envelopes are ~7MB each — letting pytest's assertion rewriter try
    # to char-diff them blows the test runner up (5+ min then OOM-ish).
    h0 = hashlib.sha256(
        json.dumps(e0, sort_keys=True, default=str).encode()
    ).hexdigest()
    h1 = hashlib.sha256(
        json.dumps(e1, sort_keys=True, default=str).encode()
    ).hexdigest()
    hr = hashlib.sha256(
        json.dumps(er, sort_keys=True, default=str).encode()
    ).hexdigest()

    assert h0 == h1, (
        f"schematic output differs between PYTHONHASHSEED=0 and =1 even "
        f"with --only-deterministic (sha256 {h0[:12]} vs {h1[:12]}). "
        f"Likely cause: hash-seeded set iteration in detector output "
        f"(RC-DET, DO-DET, etc.). v1.5 fix: sort findings + nested lists "
        f"at analyzer level."
    )
    assert h0 == hr, (
        f"schematic output differs between PYTHONHASHSEED=0 and =random "
        f"(sha256 {h0[:12]} vs {hr[:12]}). Same root cause as above."
    )
