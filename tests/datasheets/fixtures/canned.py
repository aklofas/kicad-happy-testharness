"""Canned MPN fixture builders for A4 divergence/convergence tests.

Each builder returns (mutate_callback, mpn_string). The callback is passed
to write_cache_with_pdf(tmp_path, mpn=..., mutate=...) and mutates the
loaded LM2596-ADJ fixture template in place to match the target MPN shape.

Coverage: 7 MPNs exercising buck/ldo/boost/buck_boost topologies, presence
and absence of EN/PG/FB pins, and an MCU (no regulator) for the None path.
"""
from __future__ import annotations

from typing import Callable


# ---------------------------------------------------------------------------
# Pin builder helper
# ---------------------------------------------------------------------------

def _pin(numbers: list[str], name: str, ptype: str = "input") -> dict:
    """Return a minimal v1.4 Pin dict with sensible defaults."""
    return {
        "numbers": numbers,
        "name": name,
        "type": ptype,
        "subtype": None,
        "description": None,
        "power_domain": None,
        "alt_functions": [],
        "is_5v_tolerant": None,
        "absolute_max": None,
        "recommended": None,
        "drive_strength": None,
        "notes": None,
        "evidence": {
            "page": 2,
            "section": "Pin Configuration",
            "confidence": "high",
            "method": "table",
        },
    }


# ---------------------------------------------------------------------------
# 7 builders
# ---------------------------------------------------------------------------

def make_lm2596_adj() -> tuple[Callable[[dict], None], str]:
    """LM2596-ADJ — buck, EN on pin 5, no PG. Template is already this shape.

    Mutate is a no-op; the canned lm2596-adj.example.json is the reference.
    """
    def mutate(fixture: dict) -> None:
        pass

    return mutate, "LM2596-ADJ"


def make_ap2112k_33() -> tuple[Callable[[dict], None], str]:
    """AP2112K-3.3 — LDO, EN on pin 3, no PG, no FB."""

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["regulator"]
        fixture["regulator"]["topology"] = "ldo"
        fixture["regulator"]["enable_pin"] = "3"
        fixture["regulator"]["power_good_pin"] = None
        fixture["regulator"]["feedback_pin"] = None
        fixture["base"]["pinout"] = [
            _pin(["1"], "VIN",  "power_in"),
            _pin(["2"], "GND",  "power_in"),
            _pin(["3"], "EN",   "input"),
            _pin(["4"], "NC",   "input"),
            _pin(["5"], "VOUT", "output"),
        ]

    return mutate, "AP2112K-3.3"


def make_rt7272() -> tuple[Callable[[dict], None], str]:
    """RT7272 — buck with PG, EN on pin 3, PG on pin 4, FB on pin 5."""

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["regulator"]
        fixture["regulator"]["topology"] = "buck"
        fixture["regulator"]["enable_pin"] = "3"
        fixture["regulator"]["power_good_pin"] = "4"
        fixture["regulator"]["feedback_pin"] = "5"
        fixture["base"]["pinout"] = [
            _pin(["1"], "BOOT",    "input"),
            _pin(["2"], "VIN",     "power_in"),
            _pin(["3"], "EN",      "input"),
            _pin(["4"], "PG",      "output"),
            _pin(["5"], "FB",      "input"),
            _pin(["6"], "GND",     "power_in"),
            _pin(["7"], "OUT",     "output"),
            _pin(["8"], "GND_PAD", "power_in"),
        ]

    return mutate, "RT7272"


def make_tps62160() -> tuple[Callable[[dict], None], str]:
    """TPS62160 — buck with EN+PG, PG on pin 1, EN on pin 4, FB on pin 5."""

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["regulator"]
        fixture["regulator"]["topology"] = "buck"
        fixture["regulator"]["enable_pin"] = "4"
        fixture["regulator"]["power_good_pin"] = "1"
        fixture["regulator"]["feedback_pin"] = "5"
        fixture["base"]["pinout"] = [
            _pin(["1"], "PG",   "output"),
            _pin(["2"], "GND",  "power_in"),
            _pin(["3"], "VIN",  "power_in"),
            _pin(["4"], "EN",   "input"),
            _pin(["5"], "FB",   "input"),
            _pin(["6"], "VOS",  "input"),
            _pin(["7"], "OUT",  "output"),
            _pin(["8"], "VOUT", "output"),
        ]

    return mutate, "TPS62160"


def make_tps61023() -> tuple[Callable[[dict], None], str]:
    """TPS61023 — boost, EN on pin 4, no PG, FB on pin 3."""

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["regulator"]
        fixture["regulator"]["topology"] = "boost"
        fixture["regulator"]["enable_pin"] = "4"
        fixture["regulator"]["power_good_pin"] = None
        fixture["regulator"]["feedback_pin"] = "3"
        fixture["base"]["pinout"] = [
            _pin(["1"], "SW",   "output"),
            _pin(["2"], "GND",  "power_in"),
            _pin(["3"], "FB",   "input"),
            _pin(["4"], "EN",   "input"),
            _pin(["5"], "VOUT", "output"),
            _pin(["6"], "VIN",  "power_in"),
        ]

    return mutate, "TPS61023"


def make_ltc3114() -> tuple[Callable[[dict], None], str]:
    """LTC3114 — buck_boost (outside v1.3 topology gate), EN on pin 2, FB on pin 3.

    Deliberately uses buck_boost topology to exercise the fall-through path in
    _derive_regulator_features_v14 (topology passes through verbatim; v1.3
    detectors checking `topology in ('boost','buck','ldo')` skip it).
    """

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["regulator"]
        fixture["regulator"]["topology"] = "buck_boost"
        fixture["regulator"]["enable_pin"] = "2"
        fixture["regulator"]["power_good_pin"] = None
        fixture["regulator"]["feedback_pin"] = "3"
        fixture["base"]["pinout"] = [
            _pin(["1"], "VIN",  "power_in"),
            _pin(["2"], "EN",   "input"),
            _pin(["3"], "FB",   "input"),
            _pin(["4"], "GND",  "power_in"),
            _pin(["5"], "VOUT", "output"),
        ]

    return mutate, "LTC3114"


def make_stm32f103c8t6() -> tuple[Callable[[dict], None], str]:
    """STM32F103C8T6 — MCU, no regulator section.

    Exercises the None path: _derive_regulator_features_v14 returns None when
    facts.regulator is None. The public wrappers propagate this to callers.
    """

    def mutate(fixture: dict) -> None:
        fixture["categories"] = ["mcu"]
        fixture["regulator"] = None
        fixture["base"]["pinout"] = [
            _pin(["1"], "VBAT", "power_in"),
            _pin(["8"], "VSS",  "power_in"),
            _pin(["9"], "VDD",  "power_in"),
        ]

    return mutate, "STM32F103C8T6"


# ---------------------------------------------------------------------------
# Exported collection (ordered to match task spec)
# ---------------------------------------------------------------------------

ALL_BUILDERS = [
    make_lm2596_adj,
    make_ap2112k_33,
    make_rt7272,
    make_tps62160,
    make_tps61023,
    make_ltc3114,
    make_stm32f103c8t6,
]
