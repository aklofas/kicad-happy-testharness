"""A3.3 — synthetic-liar trust-gate denial + staleness orthogonality.

Covers §5.1 (per-liar gate behavior), §5.2 (compat-wrapper structural
invariants), §5.3 (staleness ↔ trust-gating orthogonality) of the joint
test plan, per r3 revision.

Scope: proves the trust gate denies bad data on the raw lookup path, and
that the compat-wrapper path architecturally cannot smuggle low-confidence
data into v1.3 detector call-sites (because the compat dict doesn't carry
SpecValue-derived numeric fields at all).

Liars target `regulator.reference_voltage` — the canonical confidence-
bearing numeric field on LM2596-ADJ — per r3 retarget. See fixtures/liars.py
for the five liar patterns and the framing of `lie_wrong_vref_high_conf`
as Phase 4 reviewer-caught territory.

Note on r3 refinement 2: the `lie_stale_high_conf_value` tests assert
BOTH `facts.stale is True` AND that the gate returned the value,
side-by-side. This makes the staleness ↔ trust-gating orthogonality
explicit rather than implicit in the gate return.
"""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HARNESS_DIR))

import tests.datasheets.fixtures  # noqa: F401 — sys.path side effect
from tests.datasheets.fixtures.pdf import write_cache_with_pdf
from tests.datasheets.fixtures.liars import (
    ACTUAL_VREF_V,
    LIE_VREF_V,
    mutate_lie_wrong_vref_low_conf,
    mutate_lie_wrong_vref_medium_conf,
    mutate_lie_correct_vref_low_conf,
    mutate_lie_wrong_vref_high_conf,
)


# ===========================================================================
# §5.1 — lie_wrong_vref_low_conf: wrong value, low confidence
# ===========================================================================

def test_lie_wrong_vref_low_conf_best_at_high_is_none():
    """Wrong value at low confidence → gate at "high" denies."""
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_low_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="high")
    assert picked is None, "low-confidence liar must not pass high gate"


def test_lie_wrong_vref_low_conf_trusted_at_high_is_empty():
    """Wrong value at low confidence → trusted() at "high" returns []."""
    from datasheet_lookup import lookup
    from datasheet_types import trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_low_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    passing = trusted(facts.regulator.reference_voltage, min_confidence="high")
    assert passing == [], "trusted() must return [] when nothing meets gate"


# ===========================================================================
# §5.1 — lie_wrong_vref_medium_conf: wrong value, medium confidence
# ===========================================================================

def test_lie_wrong_vref_medium_conf_best_at_high_is_none():
    """Medium-confidence wrong value → gate at "high" denies."""
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_medium_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="high")
    assert picked is None


def test_lie_wrong_vref_medium_conf_best_at_medium_admits_wrong_value():
    """Medium-confidence wrong value → gate at "medium" admits (by design).

    Proves gate-bypass is possible at the matching tier. Detectors that
    depend on correct vref should use min_confidence="high". The library
    can't know the value is wrong — it trusts the extractor's confidence
    label. Content correctness is out of gate scope (Phase 4 reviewer).
    """
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_medium_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="medium")
    assert picked is not None, "medium gate must admit medium-confidence entry"
    assert picked.typ == LIE_VREF_V, "the wrong value passes the medium gate"


def test_lie_wrong_vref_medium_conf_trusted_at_high_is_empty():
    """trusted() parallel of the best() high-gate denial."""
    from datasheet_lookup import lookup
    from datasheet_types import trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_medium_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert trusted(facts.regulator.reference_voltage, min_confidence="high") == []


# ===========================================================================
# §5.1 — lie_correct_vref_low_conf: correct value, low confidence
# ===========================================================================

def test_lie_correct_vref_low_conf_best_at_high_is_none_despite_correct_value():
    """Correct value at low confidence → gate at "high" denies anyway.

    Proves the gate is confidence-based, not value-based. The library
    has no ground truth for "1.23V is the right vref for LM2596-ADJ";
    it trusts the extractor's confidence claim. A low-confidence claim
    means "I'm not sure this is right" — which is valid epistemics, and
    the gate respects it even when the value happens to be correct.
    """
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_correct_vref_low_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="high")
    assert picked is None, (
        "gate denies by confidence label, not by value correctness"
    )


def test_lie_correct_vref_low_conf_best_at_low_admits_correct_value():
    """Sanity: low gate admits low-confidence entry with correct value."""
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_correct_vref_low_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="low")
    assert picked is not None
    assert picked.typ == ACTUAL_VREF_V


def test_lie_correct_vref_low_conf_has_data_true():
    """has_data() is True even when all entries are below the gate.

    Tri-state case 2: field is populated (has_data=True) but nothing
    meets a chosen confidence tier (trusted=[]). The library reports
    presence separately from gate admission so detectors can emit
    low-confidence findings rather than skipping silently.
    """
    from datasheet_lookup import lookup
    from datasheet_types import has_data, trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_correct_vref_low_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert has_data(facts.regulator.reference_voltage) is True
    assert trusted(facts.regulator.reference_voltage, min_confidence="high") == []


# ===========================================================================
# §5.1 — lie_wrong_vref_high_conf: wrong value, high confidence (Phase 4)
# ===========================================================================

def test_lie_wrong_vref_high_conf_best_at_high_admits_wrong_value_phase4_territory():
    """High-confidence wrong value → gate admits. NOT a gate bug.

    This test documents the boundary between trust-gating and content
    correctness. The gate filters by the extractor's stated confidence;
    a truthful-high-confidence claim passes by design. The wrong value
    gets through.

    This is the case the Phase 4 reviewer subagent is designed to catch
    (Insertion Point C, §15 of the canonical extraction spec in
    kicad-happy's `docs/datasheet-extraction-v2.md`). Phase 4 re-reads
    the datasheet with a second model and flags divergence. Phase 3+
    cross-validation against distributor APIs catches parametric drift.
    Neither is the gate's job.

    Future readers: if this test makes you think the gate has a hole,
    read the r3 revision log of the joint test plan — the gate is
    working correctly.
    """
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_high_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    picked = best(facts.regulator.reference_voltage, min_confidence="high")
    assert picked is not None, (
        "high-confidence claim passes high gate by design — content "
        "correctness is Phase 4 reviewer territory, not gate scope"
    )
    assert picked.typ == LIE_VREF_V, (
        "the wrong value is admitted; Phase 4 reviewer catches it"
    )


def test_lie_wrong_vref_high_conf_trusted_at_high_admits_wrong_value_phase4_territory():
    """trusted() parallel of the best() high-confidence admission case."""
    from datasheet_lookup import lookup
    from datasheet_types import trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_high_conf)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    passing = trusted(facts.regulator.reference_voltage, min_confidence="high")
    assert len(passing) == 1
    assert passing[0].typ == LIE_VREF_V


# ===========================================================================
# §5.2 — compat-wrapper structural invariants (no-smuggle by construction)
# ===========================================================================

def test_compat_wrapper_output_identical_regardless_of_vref_confidence():
    """Compat dict is byte-identical across low/medium/high vref confidence.

    Locks the no-smuggle property structurally: `get_regulator_features()`
    pulls no SpecValue-derived numeric fields (per Track 2.5's
    `_derive_regulator_features_v14` at datasheet_features.py:132-143),
    so manipulating vref confidence has zero effect on the output. The
    wrapper cannot smuggle low-confidence values because it doesn't
    carry confidence-bearing data at all.
    """
    from datasheet_features import get_regulator_features

    outputs = {}
    for conf, mutator in [
        ("low", mutate_lie_wrong_vref_low_conf),
        ("medium", mutate_lie_wrong_vref_medium_conf),
        ("high", mutate_lie_wrong_vref_high_conf),
    ]:
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir, _ = write_cache_with_pdf(
                Path(tmp), mutate=mutator)
            outputs[conf] = get_regulator_features(
                "LM2596-ADJ", extract_dir=cache_dir)

    assert outputs["low"] == outputs["medium"] == outputs["high"], (
        f"compat dict differs by vref confidence — smuggle risk:\n"
        f"  low:    {outputs['low']}\n"
        f"  medium: {outputs['medium']}\n"
        f"  high:   {outputs['high']}"
    )


def test_compat_wrapper_dict_has_no_specvalue_derived_numeric_fields():
    """Compat dict key set is locked. Regression trip-wire for r3 §5.2.

    If future work adds a `vref`, `vin_range`, or other SpecValue-derived
    numeric field to the compat dict, this test fires — forcing a gate
    discussion before the change lands. Catching such an addition at test
    time is the point of r3's structural-invariant approach.

    The expected key set is exhaustive per
    `_derive_regulator_features_v14` at datasheet_features.py:132-143.
    """
    from datasheet_features import get_regulator_features

    expected_keys = {
        "topology",
        "has_pg",
        "has_soft_start",
        "iss_time_us",
        "en_v_ih_max",
        "en_v_il_min",
        "vin_pin",
        "vout_pin",
        "en_pin",
        "pg_pin",
    }

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    actual_keys = set(result.keys())
    assert actual_keys == expected_keys, (
        f"compat dict key set drifted — was the shape changed without a "
        f"gate review?\n"
        f"  expected: {sorted(expected_keys)}\n"
        f"  actual:   {sorted(actual_keys)}\n"
        f"  added:    {sorted(actual_keys - expected_keys)}\n"
        f"  removed:  {sorted(expected_keys - actual_keys)}"
    )


def test_compat_wrapper_topology_is_value_verbatim_not_gated():
    """Topology passes through unchanged regardless of adjacent SpecValue
    confidence. Documents that topology is architecturally ungated.

    `regulator.topology` is a plain enum string (no Evidence wrapper) —
    Track 2.5 design confirmed in the r3 revision log. The compat
    wrapper copies it verbatim. Liar confidence on sibling SpecValue
    fields (vref here) has no effect on topology passthrough.
    """
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        # Add a low-confidence liar for vref; topology is untouched by
        # the mutator, so the canned "buck" is what the cache carries.
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), mutate=mutate_lie_wrong_vref_low_conf)
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "buck", (
        "topology passes through verbatim regardless of liar confidence "
        "on other fields (topology itself has no confidence gate)"
    )


# ===========================================================================
# §5.3 — staleness ↔ trust-gating orthogonality
# ===========================================================================
# r3 refinement 2: each test asserts BOTH facts.stale AND the gate outcome,
# side-by-side, so orthogonality is explicit rather than implicit.

def test_best_ignores_stale_flag_on_high_conf_value():
    """best() returns the value even when facts.stale is True.

    Locks the architectural decoupling: staleness is advisory, not a
    trust-gate input. If `best()` started consulting `facts.stale`, the
    layers would entangle — someone "fixing" trust-gating could start
    denying fresh-but-gate-passing data on cache freshness grounds, or
    vice versa.

    r3 refinement: asserts both the stale flag AND the gate return
    side-by-side, making the orthogonality explicit.
    """
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        # Canned fixture already has reference_voltage at high confidence.
        # The "lie" here is delivered by the PDF sha mismatch, not a mutation.
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    # Side-by-side assertion — the whole point of this test.
    assert facts.stale is True, (
        "pre-condition: PDF sha mismatch produced a stale cache entry"
    )
    picked = best(facts.regulator.reference_voltage, min_confidence="high")
    assert picked is not None, (
        "best() still returned a value — staleness is NOT a gate input"
    )
    assert picked.typ == ACTUAL_VREF_V, (
        "the admitted value is the correct canned vref"
    )


def test_trusted_ignores_stale_flag():
    """trusted() returns the value list even when facts.stale is True.

    Parallel to the best() orthogonality test. Same architectural
    decoupling: trusted() filters on confidence, not on cache freshness.
    r3 refinement: side-by-side assertion on stale flag + gate output.
    """
    from datasheet_lookup import lookup
    from datasheet_types import trusted

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    assert facts.stale is True
    passing = trusted(facts.regulator.reference_voltage, min_confidence="high")
    assert len(passing) == 1, "trusted() admitted the value despite stale cache"
    assert passing[0].typ == ACTUAL_VREF_V


def test_advisory_pattern_detector_can_filter_manually():
    """Doc-as-test: detector consumes best() + facts.stale independently.

    Demonstrates the advisory pattern the architecture enables: a detector
    that cares about staleness checks `facts.stale` explicitly, orthogonal
    to the gate. If the two layers were entangled (gate short-circuits on
    stale), detectors couldn't distinguish "fresh and gate-passing" from
    "stale but gate-passing" — losing a signal.

    The test simulates minimal detector logic: gate-pass gives the value,
    then the detector decides what to do based on staleness.
    """
    from datasheet_lookup import lookup
    from datasheet_types import best

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(
            Path(tmp), pdf_sha_override="0" * 64)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)

    # Simulated detector — two orthogonal signals, combined explicitly.
    vref = best(facts.regulator.reference_voltage, min_confidence="high")
    detector_action = (
        "skip_due_to_stale" if facts.stale
        else "use_value"
    )

    # Both signals are independently accessible:
    assert vref is not None, "gate passed — value is available"
    assert vref.typ == ACTUAL_VREF_V
    assert facts.stale is True, "staleness signal is also available"
    # Detector combined them its own way — the architecture supports this:
    assert detector_action == "skip_due_to_stale", (
        "detector filtered on facts.stale independent of gate outcome"
    )


# ===========================================================================
# __main__ runner — harness convention (run_tests.py subprocess model)
# ===========================================================================

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({len(tests)} total)")
    sys.exit(1 if failed else 0)
