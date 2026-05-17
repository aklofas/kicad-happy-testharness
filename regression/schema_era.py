"""Schema-era tagging for assertion migration (spec §19, design A8).

Single source of truth for era logic. Imported by checks.py, seed*.py,
run_checks.py, check_staleness.py, tag_assertions.py.

Design: docs/superpowers/specs/2026-05-16-a8-schema-era-tagging-design.md
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterator, Optional

# ---- Constants -----------------------------------------------------------

CURRENT_SCHEMA_ERA: str = "v1.4"
"""Current assertion-era marker. Bump when detector behavior changes
materially (next bump expected at v1.5)."""

KNOWN_ERAS: tuple[str, ...] = ("pre-v1.4", "v1.4")
"""Eras the harness recognizes. Append-only; never remove."""

_DEFAULT_REGISTRY_DIR = Path(__file__).resolve().parent

# ---- Normalization -------------------------------------------------------


def normalize_schema_era(raw) -> Optional[dict]:
    """Canonicalize a schema_era value to its full object form.

    Accepts None / bare-string / object. See spec §3.6 for precedence.
    Returns None for missing input. Raises ValueError on malformed dict,
    TypeError on unsupported types.
    """
    if raw is None:
        return None
    if isinstance(raw, str):
        if raw not in KNOWN_ERAS:
            raise ValueError(f"unknown schema_era value: {raw!r}")
        return {"era": raw, "tagged_by_rule": None,
                "tagged_at": None, "tagged_reason": None}
    if isinstance(raw, dict):
        if "era" not in raw:
            raise ValueError("schema_era object missing 'era' key")
        if raw["era"] not in KNOWN_ERAS:
            raise ValueError(f"unknown schema_era value: {raw['era']!r}")
        return raw
    raise TypeError(f"unsupported schema_era type: {type(raw).__name__}")


# ---- Era accessors -------------------------------------------------------


def era_of(assertion: dict) -> Optional[str]:
    """Return the era string of an assertion (post-normalization), or None."""
    raw = assertion.get("schema_era")
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return raw.get("era")
    return None


def era_filter(assertion: dict, target_era: str) -> bool:
    """Spec §19.4 default rule.

    Returns True if the assertion should run under target_era:
      - target_era == "all"     -> always True
      - schema_era absent       -> True (untagged treated as current)
      - schema_era == target    -> True
      - else                    -> False
    """
    if target_era == "all":
        return True
    actual = era_of(assertion)
    if actual is None:
        return target_era == CURRENT_SCHEMA_ERA
    return actual == target_era


# ---- Versioned-detector registry -----------------------------------------


def _registry_filename(era: str) -> str:
    """Map era string to its registry filename."""
    if era in ("v1.4", "pre-v1.4"):
        return "v14_changed_detectors.json"
    # Generic: strip 'v' prefix and dots, e.g. "v1.5" -> "v15_changed_detectors.json"
    era_short = era.lstrip("v").replace(".", "")
    return f"v{era_short}_changed_detectors.json"


@lru_cache(maxsize=8)
def _cached_load(era: str, registry_dir_str: str) -> dict:
    registry_dir = Path(registry_dir_str)
    filename = _registry_filename(era)
    path = registry_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"no versioned-detector registry at {path}")
    data = json.loads(path.read_text())
    if "detectors" not in data:
        raise ValueError(f"malformed registry: missing 'detectors' key in {path}")
    return data


def load_versioned_detector_map(era: str = CURRENT_SCHEMA_ERA,
                                registry_dir: Optional[Path] = None) -> dict:
    """Load v{N}_changed_detectors.json for the given era. Cached.

    Raises FileNotFoundError if no registry exists for the era.
    Validates top-level shape; raises ValueError on malformed registry.
    """
    registry_dir = registry_dir or _DEFAULT_REGISTRY_DIR
    return _cached_load(era, str(registry_dir))


def is_versioned_detector(detector_function: str,
                          era: str = CURRENT_SCHEMA_ERA,
                          registry_dir: Optional[Path] = None) -> bool:
    """True iff the named detector function appears in the era's changed set."""
    if not detector_function:
        return False
    try:
        reg = load_versioned_detector_map(era, registry_dir=registry_dir)
    except FileNotFoundError:
        return False
    return detector_function in reg.get("detectors", {})


def primary_rule_for_detector(detector_function: str,
                              era: str = CURRENT_SCHEMA_ERA,
                              registry_dir: Optional[Path] = None) -> Optional[str]:
    """Return primary rule_id (lowest sorted) for a versioned detector,
    or None if not versioned."""
    try:
        reg = load_versioned_detector_map(era, registry_dir=registry_dir)
    except FileNotFoundError:
        return None
    info = reg.get("detectors", {}).get(detector_function)
    return info.get("primary_rule") if info else None


def gating_summary_for_detector(detector_function: str,
                                era: str = CURRENT_SCHEMA_ERA,
                                registry_dir: Optional[Path] = None) -> Optional[str]:
    """Return hand-curated gating summary string for a versioned detector."""
    try:
        reg = load_versioned_detector_map(era, registry_dir=registry_dir)
    except FileNotFoundError:
        return None
    info = reg.get("detectors", {}).get(detector_function)
    return info.get("gating_summary") if info else None


def iter_versioned_detector_functions(era: str = CURRENT_SCHEMA_ERA,
                                      registry_dir: Optional[Path] = None) -> Iterator[str]:
    """Iterate function names in the era's changed set. Deterministic order."""
    try:
        reg = load_versioned_detector_map(era, registry_dir=registry_dir)
    except FileNotFoundError:
        return iter([])
    return iter(sorted(reg.get("detectors", {}).keys()))


def stamp_schema_era(
    assertion: dict,
    *,
    era: str = CURRENT_SCHEMA_ERA,
    detector_filter: Optional[str] = None,
    tagged_at: Optional[str] = None,
    registry_dir: Optional[Path] = None,
    force: bool = False,
) -> bool:
    """Add schema_era to assertion in-place when applicable.

    Conditions:
      (a) detector_filter is in the era's versioned set
      (b) assertion is not already tagged (unless force=True)

    Returns True if the assertion was tagged, False if skipped.
    detector_filter defaults to assertion['check']['detector_filter'].
    tagged_at defaults to current UTC ISO timestamp.
    """
    if "schema_era" in assertion and not force:
        return False
    if detector_filter is None:
        detector_filter = assertion.get("check", {}).get("detector_filter")
    if not detector_filter:
        return False
    if not is_versioned_detector(detector_filter, era=era, registry_dir=registry_dir):
        return False
    primary = primary_rule_for_detector(detector_filter, era=era, registry_dir=registry_dir)
    summary = gating_summary_for_detector(detector_filter, era=era, registry_dir=registry_dir)
    if tagged_at is None:
        tagged_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    assertion["schema_era"] = {
        "era": era,
        "tagged_by_rule": primary,
        "tagged_at": tagged_at,
        "tagged_reason": summary,
    }
    return True
