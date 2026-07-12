"""A3.2 — compat wrapper path (get_regulator_features / get_pin_function /
is_extraction_available).

Covers §4 of the A3/A4 joint test plan. Exercises Track 2.5's dual-cache-read
wrappers: v1.4 lookup() preferred, v1.3 legacy cache as fallback, v1.4 wins
when both coexist.

Scope: the compat-layer surface, not the raw lookup() path (that's A3.1) and
not the synthetic-liar gate-denial layer (A3.3).

Key invariant at the end: for a v1.4-only cache, `get_regulator_features(mpn)`
must match `_derive_regulator_features_v14(lookup(mpn))` field-for-field.
Protects against the public wrapper drifting from the derivation helper.
"""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HARNESS_DIR))

import tests.datasheets.fixtures  # noqa: F401 — sys.path side effect
from tests.datasheets.fixtures.pdf import write_cache_with_pdf
from tests.datasheets.fixtures.v13_cache import write_v13_cache


# ===========================================================================
# get_regulator_features — dual-cache-read
# ===========================================================================

def test_get_regulator_features_reads_v14_cache():
    """v1.4 cache alone → wrapper returns a derived dict with topology='buck'."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None, "v1.4 cache present → should return dict"
    assert result["topology"] == "buck"
    # Always-None fields per Track 2.5 design.
    assert result["has_soft_start"] is None
    assert result["iss_time_us"] is None
    assert result["en_v_ih_max"] is None
    assert result["en_v_il_min"] is None


def test_get_regulator_features_falls_back_to_v13_cache_when_v14_missing():
    """v1.3 cache alone → wrapper falls through and returns v1.3 derived dict."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp) / "datasheets" / "extracted"
        write_v13_cache(
            extract_dir, mpn="LM2596-ADJ",
            topology="buck",
            pins=[
                {"number": "1", "name": "VIN", "function": "VIN"},
                {"number": "2", "name": "OUT", "function": "VOUT"},
                {"number": "5", "name": "EN", "function": "EN",
                 "threshold_high_v": 1.4, "threshold_low_v": 0.4},
            ],
            features={"has_pg": False, "has_soft_start": True, "iss_time_us": 500.0},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=extract_dir)

    assert result is not None
    assert result["topology"] == "buck"
    # v1.3 path populates these — unlike the v1.4 path.
    assert result["has_soft_start"] is True
    assert result["iss_time_us"] == 500.0
    assert result["en_v_ih_max"] == 1.4
    assert result["en_v_il_min"] == 0.4
    assert result["en_pin"] == "5"


def test_get_regulator_features_prefers_v14_when_both_coexist():
    """Both caches present → v1.4 wins. v1.3's populated soft_start/iss_time_us
    must be masked by v1.4's always-None contract."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Overlay a v1.3 cache in the same dir with DIFFERENT values.
        write_v13_cache(
            cache_dir, mpn="LM2596-ADJ",
            topology="ldo",  # Deliberately different to prove v1.4 wins.
            features={"has_soft_start": True, "iss_time_us": 9999.9},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    # v1.4 wins: topology is 'buck' (from fixture), not 'ldo' (v1.3 overlay).
    assert result["topology"] == "buck"
    # v1.4 always-None, not v1.3's 9999.9.
    assert result["has_soft_start"] is None
    assert result["iss_time_us"] is None


def test_get_regulator_features_returns_none_for_missing_mpn():
    """Neither cache has the MPN → None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("DOES-NOT-EXIST", extract_dir=cache_dir)

    assert result is None


# ===========================================================================
# get_pin_function — derivation precedence
# ===========================================================================

def test_get_pin_function_reads_v14_cache_regulator_pin_refs_first():
    """v1.4 regulator.enable_pin takes precedence over pinout name map."""
    from datasheet_features import get_pin_function

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # LM2596-ADJ fixture has enable_pin = "5" on the regulator.
        fn = get_pin_function("LM2596-ADJ", "5", extract_dir=cache_dir)

    assert fn == "EN", "regulator.enable_pin ref wins over pinout name"


def test_get_pin_function_falls_back_to_pin_name_map_when_refs_absent():
    """Pin that isn't enable/pg/feedback falls back to pinout Name map."""
    from datasheet_features import get_pin_function

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # LM2596-ADJ fixture has a VIN pin at number "1" (not a regulator ref).
        fn = get_pin_function("LM2596-ADJ", "1", extract_dir=cache_dir)

    assert fn == "VIN", "pinout Name='VIN' → function='VIN' via map"


def test_get_pin_function_returns_none_for_unknown_pin():
    """Pin not in the pinout and not in the regulator refs → None."""
    from datasheet_features import get_pin_function

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        fn = get_pin_function("LM2596-ADJ", "99", extract_dir=cache_dir)

    assert fn is None


# ===========================================================================
# is_extraction_available — cache presence probe
# ===========================================================================

def test_is_extraction_available_true_for_v14_only():
    from datasheet_features import is_extraction_available

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        assert is_extraction_available("LM2596-ADJ", extract_dir=cache_dir) is True


def test_is_extraction_available_true_for_v13_only():
    from datasheet_features import is_extraction_available

    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp) / "datasheets" / "extracted"
        write_v13_cache(extract_dir, mpn="LM2596-ADJ")
        assert is_extraction_available("LM2596-ADJ", extract_dir=extract_dir) is True


def test_is_extraction_available_true_for_both():
    from datasheet_features import is_extraction_available

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        write_v13_cache(cache_dir, mpn="LM2596-ADJ")
        assert is_extraction_available("LM2596-ADJ", extract_dir=cache_dir) is True


def test_is_extraction_available_false_for_neither():
    from datasheet_features import is_extraction_available

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "empty_cache"
        cache_dir.mkdir()
        assert is_extraction_available("ANYTHING", extract_dir=cache_dir) is False


# ===========================================================================
# Bridging invariant: wrapper ≡ direct derivation on v1.4-only cache
# ===========================================================================

def test_compat_wrapper_matches_direct_derivation_on_v14_cache():
    """Key bridging assertion between A3.1 and A3.2.

    For a v1.4-only cache, `get_regulator_features(mpn)` must return
    exactly what `_derive_regulator_features_v14(lookup(mpn))` produces,
    plus the `quality` flag the wrapper attaches in v2.0 (spec §3.A.1).
    Without this test, someone could refactor the wrapper to add fields,
    apply transforms, or short-circuit in ways that drift from the
    derivation helper — which would change behavior for any detector
    reading through the wrapper vs the helper directly.
    """
    from datasheet_features import (
        get_regulator_features,
        _derive_regulator_features_v14,
    )
    from datasheet_lookup import lookup

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))

        via_wrapper = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)
        facts = lookup("LM2596-ADJ", cache_dir=cache_dir)
        via_derivation = _derive_regulator_features_v14(facts)

    # v2.0: quality is wrapper-attached, not part of the derivation helper.
    quality = via_wrapper.pop("quality", None)
    assert quality is not None and set(quality) == {
        "score", "scale", "trusted", "reasons"}, (
        f"wrapper must attach a well-formed quality flag, got {quality!r}"
    )
    assert via_wrapper == via_derivation, (
        f"wrapper drifted from direct derivation:\n"
        f"  wrapper:    {via_wrapper}\n"
        f"  derivation: {via_derivation}"
    )


# ===========================================================================
# Topology-gate behavior — §8 of joint plan, A3.2 addition
# ===========================================================================
#
# get_regulator_features() gates the v1.4 derivation on
# `topology in {"buck", "ldo", "boost"}` (datasheet_features.py:244).
# Topologies outside that set (notably "buck_boost") are rejected; the
# wrapper falls through to the v1.3 cache, or returns None if no v1.3
# fallback exists.


def test_topology_gate_boost_passes_through_v14_cache():
    """TPS61023 (boost) — v1.4 topology in {buck, ldo, boost} passthrough gate."""
    from datasheet_features import get_regulator_features
    from tests.datasheets.fixtures.canned import make_tps61023

    mutate, mpn = make_tps61023()
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp), mpn=mpn, mutate=mutate)
        result = get_regulator_features(mpn, extract_dir=cache_dir)

    assert result is not None, "boost is in _REGULATOR_TOPOLOGIES → must passthrough"
    assert result["topology"] == "boost"
    assert result["en_pin"] == "4"


def test_topology_gate_boost_dual_cache_v14_still_wins():
    """TPS61023 — even with v1.3 cache present, v1.4 boost wins via gate passthrough."""
    from datasheet_features import get_regulator_features
    from tests.datasheets.fixtures.canned import make_tps61023

    mutate, mpn = make_tps61023()
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp), mpn=mpn, mutate=mutate)
        write_v13_cache(cache_dir, mpn=mpn, topology="buck",
                        features={"has_soft_start": True})
        result = get_regulator_features(mpn, extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "boost", (
        "v1.4 boost passthrough → result must come from v1.4 not v1.3 buck")
    assert result["has_soft_start"] is None, (
        "v1.4 wins → has_soft_start always-None even though v1.3 cache had True")


def test_topology_gate_buck_boost_falls_through_to_v13():
    """LTC3114 (buck_boost) — not in v1.3 _REGULATOR_TOPOLOGIES → fall through."""
    from datasheet_features import get_regulator_features
    from tests.datasheets.fixtures.canned import make_ltc3114

    mutate, mpn = make_ltc3114()
    with tempfile.TemporaryDirectory() as tmp:
        # v1.4 cache only — no v1.3 fallback.
        cache_dir, _ = write_cache_with_pdf(Path(tmp), mpn=mpn, mutate=mutate)
        result = get_regulator_features(mpn, extract_dir=cache_dir)

    # v1.4 produces buck_boost dict but the gate rejects it; no v1.3 cache
    # exists; final result is None (the gate-fall-through-with-no-fallback case).
    assert result is None, (
        "buck_boost not in v1.3 enum → v1.4 dict rejected; no v1.3 fallback → None")


def test_topology_gate_buck_boost_uses_v13_fallback_when_present():
    """LTC3114 — v1.4 buck_boost rejected; v1.3 buck cache wins."""
    from datasheet_features import get_regulator_features
    from tests.datasheets.fixtures.canned import make_ltc3114

    mutate, mpn = make_ltc3114()
    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp), mpn=mpn, mutate=mutate)
        # v1.3 cache claims topology=buck (a stand-in for "the legacy reading
        # before LTC3114 had its own buck_boost category"). Realistic for
        # mid-migration corpus state.
        write_v13_cache(cache_dir, mpn=mpn, topology="buck",
                        features={"has_soft_start": False},
                        pins=[{"number": "1", "name": "VIN", "function": "VIN"},
                              {"number": "2", "name": "EN", "function": "EN"},
                              {"number": "5", "name": "VOUT", "function": "VOUT"}])
        result = get_regulator_features(mpn, extract_dir=cache_dir)

    assert result is not None, "v1.4 rejected; v1.3 fallback present → must return v1.3 dict"
    assert result["topology"] == "buck", "topology comes from v1.3, not v1.4 buck_boost"
    assert result["has_soft_start"] is False, (
        "has_soft_start comes from v1.3 cache (False, not None) → "
        "fall-through case loses the v1.4-always-None invariant")


# ===========================================================================
# __main__ runner — harness convention
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
