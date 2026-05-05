"""Contract tests for v1.3 compat wrappers in datasheet_features.py.

Track 2.5 of the v1.4 datasheet extraction work. Tests the dual-cache-
read behavior: v1.4 cache preferred via lookup(), v1.3 cache as fallback.

All tests use pytest.tmp_path for self-contained cache fixtures. The
v1.4 cache is written in the Track 2.1 extraction.schema.json shape;
the v1.3 cache is written in the extraction_version=2 shape that
datasheet_extract_cache.py historically produced.
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

import pytest

SCHEMA_DIR = MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas"
FIXTURE_DIR = SCHEMA_DIR / "fixtures"

# Both sys.path entries needed: datasheet_types as a package + scripts dir
# for datasheet_features/datasheet_extract_cache/datasheet_lookup.
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets" / "scripts"))


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _build_lm2596_facts():
    """Construct a DatasheetFacts from the LM2596-ADJ fixture."""
    from datasheet_types.codec import from_dict
    from datasheet_types.extraction import DatasheetFacts

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    return from_dict(DatasheetFacts, fixture)


# ---------------------------------------------------------------------------
# _derive_regulator_features_v14 — unit tests (no filesystem)
# ---------------------------------------------------------------------------

def test_derive_regulator_features_v14_lm2596() -> None:
    """LM2596-ADJ fixture → v1.3 regulator feature dict."""
    from datasheet_features import _derive_regulator_features_v14

    facts = _build_lm2596_facts()
    feat = _derive_regulator_features_v14(facts)

    assert feat is not None
    assert feat["topology"] == "buck"
    assert feat["en_pin"] == "5"
    # LM2596-ADJ has no PG pin.
    assert feat["pg_pin"] is None
    assert feat["has_pg"] is False
    # Derived VIN / VOUT pin refs from base.pinout by name match.
    assert feat["vin_pin"] == "1"     # Pin 1 is named "VIN"
    assert feat["vout_pin"] == "2"    # Pin 2 is named "OUT" (falls into the VOUT map)
    # Fields with no v1.4 equivalent degrade to None.
    assert feat["has_soft_start"] is None
    assert feat["iss_time_us"] is None
    assert feat["en_v_ih_max"] is None
    assert feat["en_v_il_min"] is None


def test_derive_regulator_features_v14_returns_none_when_no_regulator_category() -> None:
    """Non-regulator fixtures return None."""
    from datasheet_types.codec import from_dict
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_features import _derive_regulator_features_v14

    fixture = _load_json(FIXTURE_DIR / "minimal.example.json")
    facts = from_dict(DatasheetFacts, fixture)
    # minimal.example.json has no regulator category.
    assert _derive_regulator_features_v14(facts) is None


def test_derive_regulator_features_v14_derives_has_pg_from_power_good_pin() -> None:
    """has_pg is True iff regulator.power_good_pin is populated."""
    from datasheet_features import _derive_regulator_features_v14

    facts = _build_lm2596_facts()
    # LM2596 has no power_good_pin → has_pg=False, pg_pin=None.
    feat = _derive_regulator_features_v14(facts)
    assert feat["has_pg"] is False
    assert feat["pg_pin"] is None

    # Mutate the fixture to add a PG pin, re-derive.
    facts.regulator.power_good_pin = "3"
    feat2 = _derive_regulator_features_v14(facts)
    assert feat2["has_pg"] is True
    assert feat2["pg_pin"] == "3"


# ---------------------------------------------------------------------------
# _derive_mcu_features_v14 — always None on v1.4 MVP (no mcu category yet)
# ---------------------------------------------------------------------------

def test_derive_mcu_features_v14_returns_none_on_v14_mvp() -> None:
    """v1.4 MVP has no mcu category — derivation always returns None.

    Consumers fall through to the v1.3 cache path in the public
    get_mcu_features wrapper.
    """
    from datasheet_features import _derive_mcu_features_v14

    facts = _build_lm2596_facts()
    # Regulator category only; no mcu.
    assert _derive_mcu_features_v14(facts) is None


# ---------------------------------------------------------------------------
# _derive_pin_function_v14 — per-pin function lookup
# ---------------------------------------------------------------------------

def test_derive_pin_function_v14_enable_pin() -> None:
    """Regulator.enable_pin → 'EN' function."""
    from datasheet_features import _derive_pin_function_v14

    facts = _build_lm2596_facts()
    # LM2596 EN is pin 5.
    assert _derive_pin_function_v14(facts, "5") == "EN"


def test_derive_pin_function_v14_vin_pin_by_name() -> None:
    """Pin named VIN → 'VIN' function."""
    from datasheet_features import _derive_pin_function_v14

    facts = _build_lm2596_facts()
    assert _derive_pin_function_v14(facts, "1") == "VIN"


def test_derive_pin_function_v14_gnd_pin_by_name() -> None:
    """Pin named GND → 'GND' function."""
    from datasheet_features import _derive_pin_function_v14

    facts = _build_lm2596_facts()
    # LM2596 GND is pin 3.
    assert _derive_pin_function_v14(facts, "3") == "GND"


def test_derive_pin_function_v14_unknown_pin_returns_none() -> None:
    """Nonexistent pin number → None."""
    from datasheet_features import _derive_pin_function_v14

    facts = _build_lm2596_facts()
    assert _derive_pin_function_v14(facts, "99") is None


# ---------------------------------------------------------------------------
# Integration tests — public wrappers with tmp_path cache fixtures
# ---------------------------------------------------------------------------

def _write_v14_cache(tmp_path: Path, *, mpn: str = "LM2596-ADJ") -> Path:
    """Write a v1.4 cache file under tmp_path/datasheets/extracted/.

    Returns the extract_dir (tmp_path/datasheets/extracted/).
    """
    datasheets_dir = tmp_path / "datasheets"
    extracted_dir = datasheets_dir / "extracted"
    extracted_dir.mkdir(parents=True)

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    fixture["source"]["mpn"] = mpn
    (extracted_dir / f"{mpn}.json").write_text(json.dumps(fixture))
    return extracted_dir


def _write_v13_cache(
    tmp_path: Path,
    *,
    mpn: str = "LM2596-ADJ",
    topology: str = "buck",
    has_pg: bool = False,
    en_pin_number: str = "5",
) -> Path:
    """Write a v1.3 cache file (extraction_version=2 shape).

    Minimal shape that datasheet_extract_cache.get_cached_extraction
    will accept: index.json + one MPN.json under tmp_path/datasheets/extracted/.
    """
    from datasheet_extract_cache import cache_extraction

    datasheets_dir = tmp_path / "datasheets"
    extracted_dir = datasheets_dir / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)

    extraction = {
        "extraction_metadata": {
            "extraction_version": 2,
            "extraction_score": 8.0,   # Above MIN_SCORE so _load accepts.
            "extraction_date": "2026-01-01T00:00:00+00:00",
        },
        "topology": topology,
        "pins": [
            {"number": "1", "name": "VIN", "function": "VIN"},
            {"number": en_pin_number, "name": "EN", "function": "EN"},
        ],
        "features": {
            "has_pg": has_pg,
            "has_soft_start": None,
            "iss_time_us": None,
        },
    }
    cache_extraction(extracted_dir, mpn, extraction)
    return extracted_dir


# ---- v1.4 path ----------------------------------------------------------

def test_get_regulator_features_reads_v14_cache_when_present(tmp_path: Path) -> None:
    """v1.4 cache on disk → public wrapper returns derived dict."""
    from datasheet_features import get_regulator_features

    extracted_dir = _write_v14_cache(tmp_path)
    feat = get_regulator_features("LM2596-ADJ", extract_dir=extracted_dir)

    assert feat is not None
    assert feat["topology"] == "buck"
    assert feat["en_pin"] == "5"
    assert feat["vin_pin"] == "1"
    assert feat["has_pg"] is False


def test_get_regulator_features_returns_none_when_no_cache(tmp_path: Path) -> None:
    """Neither cache → None."""
    from datasheet_features import get_regulator_features

    empty_dir = tmp_path / "datasheets" / "extracted"
    empty_dir.mkdir(parents=True)
    assert get_regulator_features("NOT-CACHED", extract_dir=empty_dir) is None


# ---- v1.3 fallback ------------------------------------------------------

def test_get_regulator_features_falls_back_to_v13_cache(tmp_path: Path) -> None:
    """v1.3-only cache → wrapper reads it via the existing _load path."""
    from datasheet_features import get_regulator_features

    extracted_dir = _write_v13_cache(
        tmp_path, mpn="LEGACY-BUCK", topology="buck", has_pg=True, en_pin_number="4"
    )
    feat = get_regulator_features("LEGACY-BUCK", extract_dir=extracted_dir)

    assert feat is not None
    assert feat["topology"] == "buck"
    # v1.3 cache: has_pg comes from features.has_pg directly.
    assert feat["has_pg"] is True
    # v1.3 cache: en_pin comes from pin_with_function("EN") → pins[].number.
    assert feat["en_pin"] == "4"


def test_get_mcu_features_falls_back_to_v13_cache(tmp_path: Path) -> None:
    """v1.4 MVP has no mcu category; wrapper uses v1.3 cache for MCU data."""
    from datasheet_features import get_mcu_features
    from datasheet_extract_cache import cache_extraction

    datasheets_dir = tmp_path / "datasheets"
    extracted_dir = datasheets_dir / "extracted"
    extracted_dir.mkdir(parents=True)

    v13_mcu = {
        "extraction_metadata": {
            "extraction_version": 2,
            "extraction_score": 8.0,
            "extraction_date": "2026-01-01T00:00:00+00:00",
        },
        "topology": "mcu",
        "pins": [],
        "peripherals": {
            "usb": {
                "speed": "HS",
                "native_phy": True,
                "series_r_required": False,
            },
        },
    }
    cache_extraction(extracted_dir, "MCU-PART", v13_mcu)

    feat = get_mcu_features("MCU-PART", extract_dir=extracted_dir)
    assert feat is not None
    assert feat["usb_speed"] == "HS"
    assert feat["has_native_usb_phy"] is True
    assert feat["usb_series_r_required"] is False


# ---- v1.4 preferred over v1.3 ------------------------------------------

def test_get_regulator_features_prefers_v14_when_both_caches_exist(tmp_path: Path) -> None:
    """When both v1.4 and v1.3 caches exist for the same MPN, v1.4 wins."""
    from datasheet_features import get_regulator_features

    extracted_dir = _write_v14_cache(tmp_path, mpn="LM2596-ADJ")
    # Also write a v1.3 cache with a different topology so we can tell which path fired.
    # The v1.3 cache_extraction() call will coexist with the v1.4 file since
    # file naming differs (LM2596-ADJ.json vs LM2596_ADJ_<hash>.json).
    _write_v13_cache(tmp_path, mpn="LM2596-ADJ", topology="ldo", en_pin_number="99")

    feat = get_regulator_features("LM2596-ADJ", extract_dir=extracted_dir)
    # v1.4 wins: topology is buck (from fixture), not ldo (from v1.3 cache).
    assert feat["topology"] == "buck"
    assert feat["en_pin"] == "5"


# ---- is_extraction_available ------------------------------------------------

def test_is_extraction_available_true_for_v14(tmp_path: Path) -> None:
    """v1.4 cache present → True."""
    from datasheet_features import is_extraction_available

    extracted_dir = _write_v14_cache(tmp_path)
    assert is_extraction_available("LM2596-ADJ", extract_dir=extracted_dir) is True


def test_is_extraction_available_true_for_v13(tmp_path: Path) -> None:
    """v1.3 cache present → True (fallback)."""
    from datasheet_features import is_extraction_available

    extracted_dir = _write_v13_cache(tmp_path, mpn="LEGACY")
    assert is_extraction_available("LEGACY", extract_dir=extracted_dir) is True


def test_is_extraction_available_false_when_neither_cache(tmp_path: Path) -> None:
    """Neither cache → False."""
    from datasheet_features import is_extraction_available

    empty_dir = tmp_path / "datasheets" / "extracted"
    empty_dir.mkdir(parents=True)
    assert is_extraction_available("NONE", extract_dir=empty_dir) is False


# ---- get_pin_function integration --------------------------------------

def test_get_pin_function_reads_v14_cache(tmp_path: Path) -> None:
    """v1.4 cache → pin_function via derivation."""
    from datasheet_features import get_pin_function

    extracted_dir = _write_v14_cache(tmp_path)
    # LM2596 EN is pin 5.
    assert get_pin_function("LM2596-ADJ", "5", extract_dir=extracted_dir) == "EN"
    # LM2596 VIN is pin 1.
    assert get_pin_function("LM2596-ADJ", "1", extract_dir=extracted_dir) == "VIN"
