# harnesslib/profiles.py
"""Declared execution profiles. Each profile's timeout_s is the source of truth
for its per-file cap; the batch runners' default (utils.ANALYZER_TIMEOUT) is
read from the standard profile at import time."""
from __future__ import annotations

from dataclasses import dataclass

SIX = ("schematic", "pcb", "gerber", "thermal", "emc", "cross_analysis")


@dataclass(frozen=True)
class Profile:
    name: str
    analyzers: tuple[str, ...]
    timeout_s: int
    pcb_full: bool
    schematic_no_hierarchy: bool
    only_deterministic: bool
    offline: bool


PROFILES: dict[str, Profile] = {
    "standard": Profile("standard", SIX, 120, False, True, True, True),
    # schematic is declared so Phase B (paired off schematic records) runs the
    # chained analyzers at all (TH-072)
    "full-chain": Profile("full-chain", ("schematic", "pcb", "emc", "thermal", "cross_analysis"),
                          600, True, True, True, True),
    "hierarchy": Profile("hierarchy", ("schematic",), 300, False, False, True, True),
    "spice-offline": Profile("spice-offline", ("spice",), 60, False, True, True, True),
    "long-tail": Profile("long-tail", SIX, 600, False, True, True, True),
    # product oracle, not a corpus profile: tools/distributor_offline.py (v3 round 6) run
    # both ways by regression/run_distributor_offline_gate.py; run_corpus_gate refuses it
    "distributor-offline": Profile("distributor-offline", ("distributor",), 120, False, True, True, True),
}
