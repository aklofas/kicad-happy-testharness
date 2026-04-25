"""A4 — v1.3 detectors on v1.4 caches: divergence + convergence.

Covers §6 of the A3/A4 joint test plan. Locks the 4 always-None divergence
fields (`has_soft_start`, `iss_time_us`, `en_v_ih_max`, `en_v_il_min`) and
the 6 convergence fields (`topology`, `has_pg`, `en_pin`, `pg_pin`,
`vin_pin`, `vout_pin`) against the 7-MPN canned set.

Scope: this file does NOT test gate denial (A3.3) or raw lookup (A3.1) —
it tests that running v1.3 detector logic on v1.4 caches via the compat
wrapper produces the expected dict shape, with intentional divergences
recorded as expected and convergence fields verified byte/value-equal.
"""

TIER = "unit"

import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(HARNESS_DIR))

import tests.datasheets.fixtures  # noqa: F401 — sys.path side effect
from tests.datasheets.fixtures.canned import ALL_BUILDERS
from tests.datasheets.fixtures.pdf import write_cache_with_pdf
from tests.datasheets.fixtures.v13_cache import write_v13_cache


# ===========================================================================
# Divergence tests — 4 always-None fields × 3 shapes per §6.2 of joint plan
# ===========================================================================
#
# For each always-None field (has_soft_start, iss_time_us, en_v_ih_max,
# en_v_il_min) we verify three shapes:
#
#   Shape A: v1.3-cache-populates / v1.4-cache-returns-None
#            v1.3 cache has the field set; no v1.4 cache exists. Compat
#            wrapper falls back to v1.3 and the field comes through.
#            (Sanity — proves v1.3 path still works post-Track 2.5.)
#
#   Shape B: dual-cache / v1.4-wins-and-field-is-None
#            Both v1.3 and v1.4 caches exist. Compat wrapper prefers v1.4.
#            The field is None even though the v1.3 cache has a value.
#            (The load-bearing assertion: v1.4 doesn't silently inherit
#            v1.3 data for fields v1.4 schema doesn't carry.)
#
#   Shape C: detector-degrades-gracefully-when-None
#            Standalone v1.4 cache. Field is None. Verifies the wrapper
#            doesn't raise / doesn't substitute a sentinel like 0 or False.
#            (None is the canonical "datasheet didn't specify" signal per
#            v1.3 contract.)


def test_divergence_has_soft_start_v13_cache_populates_v14_cache_returns_none():
    """Shape A: v1.3-only, has_soft_start=True comes through."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "datasheets" / "extracted"
        cache_dir.mkdir(parents=True)
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            features={"has_soft_start": True, "iss_time_us": 500.0,
                      "en_v_ih_max": 2.4, "en_v_il_min": 0.4},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["has_soft_start"] is True, (
        "v1.3 cache present and v1.4 absent → has_soft_start should come from v1.3")


def test_divergence_has_soft_start_dual_cache_v14_wins_and_field_is_none():
    """Shape B: both caches; v1.4 wins; has_soft_start is None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        # v1.4 cache via write_cache_with_pdf
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Add v1.3 cache alongside in the same dir, with has_soft_start=True
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            features={"has_soft_start": True, "iss_time_us": 500.0,
                      "en_v_ih_max": 2.4, "en_v_il_min": 0.4},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "buck"  # came from v1.4
    assert result["has_soft_start"] is None, (
        "v1.4 wins; has_soft_start has no v1.4 schema equivalent → must be None "
        "even though v1.3 cache has it set to True")


def test_divergence_has_soft_start_detector_degrades_gracefully_when_none():
    """Shape C: v1.4 only; detector consumer sees None, not False/0."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["has_soft_start"] is None, "must be None, not False or 0"
    # Document the contract: a downstream detector checking
    #   `if features.get('has_soft_start'): emit_finding(...)`
    # treats None and False identically (both falsy), so the detector
    # neither emits a soft-start finding nor crashes — degrades gracefully.
    assert not result["has_soft_start"]  # falsy contract


# =========================================================================
# iss_time_us (Tasks 4)
# =========================================================================

def test_divergence_iss_time_us_v13_cache_populates_v14_cache_returns_none():
    """Shape A: v1.3-only, iss_time_us=500.0 comes through."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "datasheets" / "extracted"
        cache_dir.mkdir(parents=True)
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            features={"has_soft_start": True, "iss_time_us": 500.0,
                      "en_v_ih_max": 2.4, "en_v_il_min": 0.4},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["iss_time_us"] == 500.0, (
        "v1.3 cache present and v1.4 absent → iss_time_us should come from v1.3")


def test_divergence_iss_time_us_dual_cache_v14_wins_and_field_is_none():
    """Shape B: both caches; v1.4 wins; iss_time_us is None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        # v1.4 cache via write_cache_with_pdf
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Add v1.3 cache alongside in the same dir, with iss_time_us=500.0
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            features={"has_soft_start": True, "iss_time_us": 500.0,
                      "en_v_ih_max": 2.4, "en_v_il_min": 0.4},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "buck"  # came from v1.4
    assert result["iss_time_us"] is None, (
        "v1.4 wins; iss_time_us has no v1.4 schema equivalent → must be None "
        "even though v1.3 cache has it set to 500.0")


def test_divergence_iss_time_us_detector_degrades_gracefully_when_none():
    """Shape C: v1.4 only; detector sees None for inrush-time check."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["iss_time_us"] is None, "must be None, not 0.0 or empty"


# =========================================================================
# en_v_ih_max (Task 5)
# =========================================================================

def test_divergence_en_v_ih_max_v13_cache_populates_v14_cache_returns_none():
    """Shape A: v1.3-only, en_v_ih_max=2.4 comes through."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "datasheets" / "extracted"
        cache_dir.mkdir(parents=True)
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            pins=[{"number": "1", "name": "EN", "function": "EN",
                   "threshold_high_v": 2.4, "threshold_low_v": 0.4}],
            features={"has_soft_start": True, "iss_time_us": 500.0},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["en_v_ih_max"] == 2.4, (
        "v1.3 cache present and v1.4 absent → en_v_ih_max should come from v1.3")


def test_divergence_en_v_ih_max_dual_cache_v14_wins_and_field_is_none():
    """Shape B: both caches; v1.4 wins; en_v_ih_max is None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        # v1.4 cache via write_cache_with_pdf
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Add v1.3 cache alongside in the same dir, with en_v_ih_max=2.4
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            pins=[{"number": "1", "name": "EN", "function": "EN",
                   "threshold_high_v": 2.4, "threshold_low_v": 0.4}],
            features={"has_soft_start": True, "iss_time_us": 500.0},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "buck"  # came from v1.4
    assert result["en_v_ih_max"] is None, (
        "v1.4 wins; en_v_ih_max has no v1.4 schema equivalent → must be None "
        "even though v1.3 cache has it set to 2.4")


def test_divergence_en_v_ih_max_detector_degrades_gracefully_when_none():
    """Shape C: v1.4 only; EN-threshold detector skips when None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["en_v_ih_max"] is None, "must be None, not 0.0 or empty"


# =========================================================================
# en_v_il_min (Task 6)
# =========================================================================

def test_divergence_en_v_il_min_v13_cache_populates_v14_cache_returns_none():
    """Shape A: v1.3-only, en_v_il_min=0.4 comes through."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = Path(tmp) / "datasheets" / "extracted"
        cache_dir.mkdir(parents=True)
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            pins=[{"number": "1", "name": "EN", "function": "EN",
                   "threshold_high_v": 2.4, "threshold_low_v": 0.4}],
            features={"has_soft_start": True, "iss_time_us": 500.0},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["en_v_il_min"] == 0.4, (
        "v1.3 cache present and v1.4 absent → en_v_il_min should come from v1.3")


def test_divergence_en_v_il_min_dual_cache_v14_wins_and_field_is_none():
    """Shape B: both caches; v1.4 wins; en_v_il_min is None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        # v1.4 cache via write_cache_with_pdf
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        # Add v1.3 cache alongside in the same dir, with en_v_il_min=0.4
        write_v13_cache(
            cache_dir,
            mpn="LM2596-ADJ",
            topology="buck",
            pins=[{"number": "1", "name": "EN", "function": "EN",
                   "threshold_high_v": 2.4, "threshold_low_v": 0.4}],
            features={"has_soft_start": True, "iss_time_us": 500.0},
        )
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["topology"] == "buck"  # came from v1.4
    assert result["en_v_il_min"] is None, (
        "v1.4 wins; en_v_il_min has no v1.4 schema equivalent → must be None "
        "even though v1.3 cache has it set to 0.4")


def test_divergence_en_v_il_min_detector_degrades_gracefully_when_none():
    """Shape C: v1.4 only; EN-threshold low-side detector skips when None."""
    from datasheet_features import get_regulator_features

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir, _ = write_cache_with_pdf(Path(tmp))
        result = get_regulator_features("LM2596-ADJ", extract_dir=cache_dir)

    assert result is not None
    assert result["en_v_il_min"] is None, "must be None, not 0.0 or empty"


# ===========================================================================
# Convergence tests — 6 fields × 7 MPNs per §6.3 of joint plan
# ===========================================================================
#
# Asserts byte/value equality between v1.4 cache → compat wrapper → v1.3
# dict for fields that have direct equivalents on both schemas. Failure
# means Track 2.5's _derive_regulator_features_v14 has drifted from the
# v1.3 contract.
#
# Note: vout_pin reflects what _derive_regulator_features_v14 returns —
# the first pin matching OUT → VOUT → VOUT+ in the pinout. For RT7272
# this is pin 7 (named "OUT", the switch node), not a true power output.
# For TPS62160 this is also pin 7 (named "OUT"), not pin 8 (named "VOUT"),
# because OUT is checked first in the fallback chain.
# That's the wrapper's documented behavior; semantic refinement is out of
# scope for A4 (would belong in Track 2.5 or v1.5).
#
# Plan called for pytest.mark.parametrize over ALL_BUILDERS; harness uses
# standalone def test_*() with __main__ runner. Each convergence test is
# therefore one function looping over ALL_BUILDERS with per-MPN assertion
# messages, preserving the per-MPN diagnostic on failure without spawning
# 7 separately-named test functions.

# (topology, has_pg, en_pin, pg_pin, vin_pin, vout_pin)
CONVERGENCE_EXPECTED = {
    "LM2596-ADJ":      ("buck",       False, "5",  None, "1",  "2"),
    "AP2112K-3.3":     ("ldo",        False, "3",  None, "1",  "5"),
    "RT7272":          ("buck",       True,  "3",  "4",  "2",  "7"),
    "TPS62160":        ("buck",       True,  "4",  "1",  "3",  "7"),
    "TPS61023":        ("boost",      False, "4",  None, "6",  "5"),
    # LTC3114 buck_boost: rejected by v1.3 topology gate; falls through to
    # v1.3 cache (or returns None when no v1.3 fallback). Topology-gate
    # behavior is tested in test_a3_compat_path.py via T10.
    "LTC3114":         (None, None, None, None, None, None),
    # STM32F103C8T6: no regulator → wrapper returns None entirely.
    "STM32F103C8T6":   (None, None, None, None, None, None),
}


def _run_convergence(field_index: int, field_name: str):
    """Helper: loop over ALL_BUILDERS asserting CONVERGENCE_EXPECTED[mpn][field_index]."""
    from datasheet_features import get_regulator_features

    for builder in ALL_BUILDERS:
        mutate, mpn = builder()
        expected = CONVERGENCE_EXPECTED[mpn][field_index]
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir, _ = write_cache_with_pdf(Path(tmp), mpn=mpn, mutate=mutate)
            result = get_regulator_features(mpn, extract_dir=cache_dir)

        if CONVERGENCE_EXPECTED[mpn][0] is None:
            # Non-regulator or topology-gate-filtered → wrapper returns None entirely.
            assert result is None, (
                f"{mpn}: non-regulator or topology-gate-filtered MPN should return None, "
                f"got {result!r}")
        else:
            assert result is not None, f"{mpn}: regulator MPN should return a dict"
            actual = result[field_name]
            if isinstance(expected, bool):
                # bool: use `is` for identity (True/False, not just truthiness)
                assert actual is expected, (
                    f"{mpn}: {field_name} should be {expected!r}, got {actual!r}")
            else:
                assert actual == expected, (
                    f"{mpn}: {field_name} should be {expected!r}, got {actual!r}")


def test_convergence_topology_matches_v13_dict():
    """v1.4 regulator.topology → v1.3 dict 'topology' byte-equal across 7 MPNs."""
    _run_convergence(0, "topology")


def test_convergence_has_pg_matches_v13_dict():
    """v1.4 regulator.power_good_pin not None → v1.3 dict 'has_pg' boolean across 7 MPNs."""
    _run_convergence(1, "has_pg")


def test_convergence_en_pin_matches_v13_dict():
    """v1.4 regulator.enable_pin → v1.3 dict 'en_pin' string-equal across 7 MPNs."""
    _run_convergence(2, "en_pin")


def test_convergence_pg_pin_matches_v13_dict():
    """v1.4 regulator.power_good_pin → v1.3 dict 'pg_pin' string-equal across 7 MPNs."""
    _run_convergence(3, "pg_pin")


def test_convergence_vin_pin_matches_v13_dict():
    """v1.4 base.pinout VIN-name lookup → v1.3 dict 'vin_pin' string-equal across 7 MPNs."""
    _run_convergence(4, "vin_pin")


def test_convergence_vout_pin_matches_v13_dict_with_fallback():
    """v1.4 base.pinout OUT/VOUT/VOUT+ fallback → v1.3 dict 'vout_pin' across 7 MPNs."""
    _run_convergence(5, "vout_pin")


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
