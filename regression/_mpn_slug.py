"""Shared MPN→slug derivation for A7 gold storage.

Mirrors validate/check_acceptance_gate.py:_sanitize_mpn but lowercases for
filesystem-friendly slugs. Dots preserved per Phase 3b convention
(ABM8G-106-12.000MHZ-T → abm8g-106-12.000mhz-t).
"""
from __future__ import annotations

import re

_SLUG_RE = re.compile(r"[^a-z0-9_\-.]")


def mpn_slug(mpn: str) -> str:
    """Lowercase MPN with non-[a-z0-9_-.] replaced with _.

    Examples:
        LM2596-ADJ → lm2596-adj
        ABM8G-106-12.000MHZ-T → abm8g-106-12.000mhz-t
        Some/Bad MPN → some_bad_mpn
    """
    return _SLUG_RE.sub("_", mpn.strip().lower())
