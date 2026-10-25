"""Shared readers for analyzer output directories and assertion ids."""

from pathlib import Path

# Written beside analyzer outputs by the product, never an analyzer result itself.
SIDECAR_NAMES = frozenset({"capability_mode.json"})


def json_files(directory: Path, *, sort: bool, skip_underscore: bool,
               skip_sidecar: bool) -> list[Path]:
    """The ``*.json`` files in ``directory`` (``[]`` when it is missing).

    Callers differ on ordering and on which non-analyzer files they drop, so
    every policy is an explicit argument.
    """
    if not directory.exists():
        return []
    files = [f for f in directory.glob("*.json")
             if not (skip_underscore and f.name.startswith("_"))
             and not (skip_sidecar and f.name in SIDECAR_NAMES)]
    return sorted(files) if sort else files


def assertion_prefix(aid: str, no_dash: str = "OTHER") -> str:
    """The id family of an assertion id (``SEED-12`` -> ``SEED``)."""
    return aid.split("-")[0] if "-" in aid else no_dash


def assertion_items(data) -> list:
    """The assertion dicts of a loaded assertion file. Only an object file carries them: a
    bare list loads as an error in ``checks.load_assertions`` and runs no assertions, so it
    contributes none here."""
    return data.get("assertions", []) if isinstance(data, dict) else []
