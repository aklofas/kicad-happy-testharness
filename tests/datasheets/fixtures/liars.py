"""Synthetic-liar fixtures — A3.3 gate-denial proof.

Per joint test plan §5.1 r3: each liar is a mutation on the canned
LM2596-ADJ template that injects a wrong value, a wrong confidence label,
or both. Tests use these fixtures with `write_cache_with_pdf(..., mutate=...)`
to prove the trust gate denies bad data rather than admitting it.

Liars target `regulator.reference_voltage` — the canonical confidence-bearing
numeric field for LM2596-ADJ (per the datasheet's Electrical Characteristics
table, typ=1.23V at high confidence). `regulator.topology` is a plain enum
string with no Evidence wrapper (Track 2.5 design per the r3 revision log),
so it cannot carry a confidence-level liar; liars go on SpecValue fields.

Canonical values for the LM2596-ADJ fixture:
    ACTUAL_VREF_V = 1.23  (TI datasheet, Electrical Characteristics, typ)
    LIE_VREF_V    = 2.7   (wrong value; chosen to be >2× actual for easy
                           spot-checks in assertions)
"""
from __future__ import annotations

ACTUAL_VREF_V = 1.23
LIE_VREF_V = 2.7


def _set_vref(fixture: dict, *, value: float, confidence: str) -> None:
    """Overwrite regulator.reference_voltage with a single SpecValue.

    Replaces the canned fixture's three-point (min/typ/max) entry with a
    typ-only single SpecValue at the requested confidence. Isolates the
    confidence signal so liar tests exercise a single gate transition
    rather than three.
    """
    fixture["regulator"]["reference_voltage"] = [{
        "min": None,
        "typ": value,
        "max": None,
        "unit": "V",
        "condition": None,
        "notes": None,
        "evidence": {
            "page": 5,
            "section": "Electrical Characteristics",
            "confidence": confidence,
            "method": "table",
        },
    }]


# ---------------------------------------------------------------------------
# Five liar patterns — §5.1 r3
# ---------------------------------------------------------------------------

def mutate_lie_wrong_vref_low_conf(fixture: dict) -> None:
    """Wrong vref (2.7V, actual 1.23V), confidence=low.

    Gate at "high" → None. Gate at "medium" → None. Gate at "low" → the
    wrong value (proves gate-bypass is possible at the lowest tier, which
    is by design — "low" means "accept any extracted value").
    """
    _set_vref(fixture, value=LIE_VREF_V, confidence="low")


def mutate_lie_wrong_vref_medium_conf(fixture: dict) -> None:
    """Wrong vref (2.7V, actual 1.23V), confidence=medium.

    Gate at "high" → None. Gate at "medium" → the wrong value. Proves
    that a medium-confidence claim is enough to sneak wrong data past a
    medium gate; detectors that depend on correct vref should use
    min_confidence="high".
    """
    _set_vref(fixture, value=LIE_VREF_V, confidence="medium")


def mutate_lie_correct_vref_low_conf(fixture: dict) -> None:
    """Correct vref (1.23V), confidence=low.

    Gate at "high" → None *even though the value is correct*. Proves the
    gate is confidence-based, not value-based — the library has no way to
    "know" 1.23V is right; it trusts the extractor's confidence label.
    Detectors that want value-correctness guarantees need Phase 4's
    reviewer layer, not the gate.
    """
    _set_vref(fixture, value=ACTUAL_VREF_V, confidence="low")


def mutate_lie_wrong_vref_high_conf(fixture: dict) -> None:
    """Wrong vref (2.7V), confidence=high.

    Gate admits the wrong value. **This is not a gate bug.** This case
    documents the boundary between trust-gating and content-correctness:

    - Gate scope: filter extractions by the extractor's own stated
      confidence. A truthful-high-confidence claim passes by design.
    - Out of gate scope: cross-checking the value against ground truth.

    The case this test documents — a wrong value paired with a truthful-
    seeming high-confidence label — is exactly what the reviewer subagent
    is designed to catch (Insertion Point C, §15 of the canonical
    extraction spec in kicad-happy's `docs/datasheet-extraction-v2.md`).

    Phase 4 Layer 2 review catches high-confidence-but-wrong by re-reading
    the datasheet with a second model and flagging divergence. Phase 3+
    cross-validation against distributor APIs catches it parametrically.
    Neither is the gate's job.

    Future readers: if you find yourself thinking "the gate has a hole
    here," read this docstring and the r3 revision log in the joint test
    plan spec. The gate is working correctly.
    """
    _set_vref(fixture, value=LIE_VREF_V, confidence="high")


# The fifth liar — lie_stale_high_conf_value — does not need a mutator.
# The canned LM2596-ADJ fixture already carries reference_voltage at
# high confidence with typ=1.23V. The "lie" is delivered by the PDF
# sha mismatch, not by any fixture mutation. Tests construct it via:
#     write_cache_with_pdf(tmp_path, pdf_sha_override="0" * 64)
# and then assert BOTH that facts.stale is True AND that best() still
# returns the value — locking the staleness ↔ trust-gating orthogonality
# invariant per §5.3 and r3 refinement 2.
