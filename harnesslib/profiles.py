# harnesslib/profiles.py
"""Declared execution profiles. Each profile's timeout_s is the source of truth
for its per-file cap; the batch runners' default (harnesslib.batch.ANALYZER_TIMEOUT)
is read from the standard profile at import time."""
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
    # Memory (TH-071): the per-unit RSS the gate schedules for (default jobs = MemAvailable /
    # max_rss_mb), and the address-space ceiling each unit runs under (None: no ceiling).
    max_rss_mb: int = 1024
    unit_mem_limit_mb: int | None = None


PROFILES: dict[str, Profile] = {
    "standard": Profile("standard", SIX, 120, False, True, True, True),
    # schematic is declared because chained jobs are selected from successful
    # schematic records; without it the chained analyzers never run (TH-072)
    # caps above 120 s let a runaway unit (KH-447 LT3514: 53.7 GB) reach the host OOM killer
    "full-chain": Profile("full-chain", ("schematic", "pcb", "emc", "thermal", "cross_analysis"),
                          600, True, True, True, True, max_rss_mb=6144, unit_mem_limit_mb=16384),
    "hierarchy": Profile("hierarchy", ("schematic",), 300, False, False, True, True,
                         max_rss_mb=6144, unit_mem_limit_mb=16384),
    "spice-offline": Profile("spice-offline", ("spice",), 60, False, True, True, True),
    "long-tail": Profile("long-tail", SIX, 600, False, True, True, True,
                         max_rss_mb=6144, unit_mem_limit_mb=16384),
    # product oracle, not a corpus profile: tools/distributor_offline.py, run
    # both ways by regression/run_distributor_offline_gate.py; run_corpus_gate refuses it
    "distributor-offline": Profile("distributor-offline", ("distributor",), 120, False, True, True, True),
}


def mem_available_mb() -> int | None:
    """MemAvailable from /proc/meminfo (Linux), else None."""
    try:
        for line in open("/proc/meminfo", encoding="ascii"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return None


def default_jobs(profile: Profile, *, cpu: int, mem_available_mb: int | None) -> int:
    """Job count for a run with no explicit --jobs: the CPU count, capped so that jobs x the
    profile's per-unit RSS hint fits in available memory (TH-071)."""
    if mem_available_mb is None:
        return cpu
    return max(1, min(cpu, mem_available_mb // profile.max_rss_mb))
