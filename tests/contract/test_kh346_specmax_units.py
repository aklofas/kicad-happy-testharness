#!/usr/bin/env python3
"""KH-346: per-pin absolute_max lists mix voltage and current SpecValues;
the voltage comparison must skip non-voltage entries."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets" / "scripts"))
from datasheet_verify import _v1_view


def _extraction(abs_max_list):
    return {"base": {"pinout": [{"numbers": [1], "name": "OUT",
                                 "type": "power",
                                 "absolute_max": abs_max_list}]}}


def test_current_entry_first_is_skipped():
    v = _v1_view(_extraction([{"max": 0.025, "unit": "A"},
                              {"max": 6.0, "unit": "V"}]))
    assert v["pins"][0]["voltage_abs_max"] == 6.0


def test_unitless_entry_still_used():
    v = _v1_view(_extraction([{"max": 5.5}]))
    assert v["pins"][0]["voltage_abs_max"] == 5.5


def test_current_only_list_gives_none():
    v = _v1_view(_extraction([{"max": 0.025, "unit": "A"}]))
    assert v["pins"][0]["voltage_abs_max"] is None
