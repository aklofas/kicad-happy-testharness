"""Layer 2 strip is identity on deterministic content.

Audit LOG 8b / regression-testing-audit F8 (2026-05-15): the contract
explicitly deferred from LOG 8's commit message. ``strip_llm_overlays``
MUST be a no-op on analyzer envelopes that contain no ``llm_*`` keys
(i.e., default-mode and ``--only-deterministic``-mode outputs). The
LOG 11 synthetic-envelope tests cover the strip MECHANICS (top-level +
nested + lists + no-false-positives); this file covers the strip
INVARIANT on real cached analyzer envelopes — the v1.4 envelope shape
in production is wide enough that a synthetic mini-envelope can't
exhaust the surface.

Tied to HI-3 (``strip(merged) == raw``): once a Layer 2 review has been
merged, the strip operation must recover the raw envelope byte-for-byte.
Locking strip-identity on the RAW side (no llm_* keys present)
guarantees one half of that invariant: the strip is structurally
identity, the only difference HI-3 ever tolerates is removal of
the merge-added ``llm_review`` siblings.

Fixtures: reuse the noise-budget cached fixtures (real corpus
schematic envelopes, no llm_* keys). No TIER — the JSON files are
committed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

REVIEW_SCRIPTS_DIR = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
if str(REVIEW_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS_DIR))

FIXTURES_DIR = HARNESS_ROOT / "tests" / "fixtures" / "noise-budget"

FIXTURE_NAMES = [
    "macropad.schematic.json",
    "ir_uart.schematic.json",
    "ascii_display_module.schematic.json",
]


@pytest.fixture(scope="module", params=FIXTURE_NAMES, ids=lambda n: n.split(".")[0])
def real_envelope(request):
    path = FIXTURES_DIR / request.param
    if not path.is_file():
        pytest.skip(f"missing fixture {request.param}")
    return json.loads(path.read_text())


# ---------------------------------------------------------------------------
# Strip-identity on real envelopes (no llm_* keys present)
# ---------------------------------------------------------------------------

def _contains_any_llm_keys(node):
    """Recursive scan for ANY key starting with 'llm_' anywhere in the
    envelope. Used to assert the fixture precondition (no llm_* present)
    before testing the strip identity."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("llm_"):
                return True
            if _contains_any_llm_keys(v):
                return True
    elif isinstance(node, list):
        return any(_contains_any_llm_keys(item) for item in node)
    return False


def test_real_envelope_fixture_precondition_no_llm_keys(real_envelope):
    """Sanity: the noise-budget fixtures (default-mode analyzer outputs)
    must contain no ``llm_*`` keys anywhere. If this fails, the fixture
    was regenerated from a merged source rather than a raw analyzer run —
    invalidates the strip-identity tests below."""
    assert not _contains_any_llm_keys(real_envelope), (
        "fixture contains llm_* keys — was it generated from merged output? "
        "Regen from a raw analyzer run via run/run_schematic.py."
    )


def test_strip_is_identity_on_real_envelope(real_envelope):
    """strip_llm_overlays(envelope) == envelope when no llm_* keys exist.
    Locks the no-op-on-clean-input contract on real corpus envelopes
    (not just synthetic mini-envelopes)."""
    from merge_annotations import strip_llm_overlays
    stripped = strip_llm_overlays(real_envelope)
    assert stripped == real_envelope, (
        "strip mutated a clean envelope — false-positive removal of a "
        "key that doesn't start with 'llm_'"
    )


def test_strip_is_idempotent_on_real_envelope(real_envelope):
    """strip(strip(envelope)) == strip(envelope). Idempotence is necessary
    for HI-3 round-trip (a re-merged envelope must produce the same raw
    on a second strip pass)."""
    from merge_annotations import strip_llm_overlays
    once = strip_llm_overlays(real_envelope)
    twice = strip_llm_overlays(once)
    assert once == twice


def test_strip_preserves_top_level_field_count_on_real_envelope(real_envelope):
    """Stronger lock: not only must strip == envelope, the top-level field
    count must be unchanged. Catches a regression that drops a sibling
    field along with an llm_* key (e.g., a buggy 'remove llm_* AND its
    documented field' fix)."""
    from merge_annotations import strip_llm_overlays
    stripped = strip_llm_overlays(real_envelope)
    assert sorted(stripped.keys()) == sorted(real_envelope.keys())


# ---------------------------------------------------------------------------
# Strip-identity after merge applies llm_review — round-trip mechanical
# ---------------------------------------------------------------------------

def test_strip_after_synthetic_merge_recovers_raw(real_envelope, tmp_path):
    """Bolts the HI-3 invariant onto real corpus envelopes: manually
    inject an llm_review sibling on the first finding (simulating a merge),
    strip, confirm we recover the byte-identical raw input. Uses real
    envelopes so the test exercises the full v1.4 envelope shape, not
    just the few keys a synthetic fixture would touch."""
    from merge_annotations import strip_llm_overlays

    if not real_envelope.get("findings"):
        pytest.skip("fixture has no findings to mutate")

    # Snapshot the raw before mutation
    raw_blob = json.dumps(real_envelope, sort_keys=True)

    # Mutate a copy (don't pollute the module-scoped fixture)
    mutated = json.loads(raw_blob)
    mutated["findings"][0]["llm_review"] = {
        "status": "confirmed",
        "reason": "test injection — twenty-character-min reason string",
        "confidence": "medium",
        "reviewed_at": "2026-05-16T12:00:00Z",
    }

    stripped = strip_llm_overlays(mutated)
    stripped_blob = json.dumps(stripped, sort_keys=True)

    assert stripped_blob == raw_blob, (
        "strip after synthetic merge did NOT recover the raw envelope "
        "byte-for-byte (HI-3 contract on real envelope shape)"
    )


def test_strip_handles_multiple_llm_keys_at_once_on_real_envelope(real_envelope):
    """Add several llm_* keys at different nesting levels; confirm all are
    removed in one pass and nothing else moves. Lock that the strip
    handles multi-llm-key inputs (which a future v1.5 'multi-pass review'
    pipeline might produce)."""
    from merge_annotations import strip_llm_overlays

    if not real_envelope.get("findings"):
        pytest.skip("fixture has no findings to mutate")

    raw_blob = json.dumps(real_envelope, sort_keys=True)
    mutated = json.loads(raw_blob)
    # Top-level injection
    mutated["llm_summary"] = "fake top-level llm output"
    # Per-finding injection (multiple findings, multiple llm_*)
    for f in mutated["findings"][:3]:
        f["llm_review"] = {"status": "confirmed", "reason": "x" * 25,
                           "confidence": "medium", "reviewed_at": "2026-05-16T12:00:00Z"}
        f["llm_meta"] = {"reviewed_by": "test-reviewer"}

    stripped = strip_llm_overlays(mutated)
    assert json.dumps(stripped, sort_keys=True) == raw_blob


# ---------------------------------------------------------------------------
# Negative path — corruption surfaces via inequality
# ---------------------------------------------------------------------------

def test_strip_identity_fails_loudly_if_raw_envelope_was_actually_modified(real_envelope):
    """Sanity: if we manually break the strip preconditions (mutate a
    non-llm_* key), the identity check must FAIL. Proves the equality
    comparison in test_strip_is_identity_on_real_envelope is meaningful
    (not just always-True via reference identity).

    This is a guard against a test-suite bug where the assertion would
    silently pass even with a broken strip implementation."""
    from merge_annotations import strip_llm_overlays
    mutated = json.loads(json.dumps(real_envelope))
    # Add a non-llm field at top level — strip should NOT remove it,
    # so the stripped output should NOT equal the unmodified original.
    mutated["__test_injection"] = "this should survive the strip"
    stripped = strip_llm_overlays(mutated)
    assert stripped != real_envelope, (
        "strip removed a non-llm_* field — false-positive removal regression"
    )
    assert stripped["__test_injection"] == "this should survive the strip"
