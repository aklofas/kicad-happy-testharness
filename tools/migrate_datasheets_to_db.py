#!/usr/bin/env python3
"""One-shot migration from the three datasheet locations to the new store.

Usage:
    python3 tools/migrate_datasheets_to_db.py --dry-run
    python3 tools/migrate_datasheets_to_db.py

Deleted after successful migration per the sole-maintainer one-shot
tool policy. See docs/superpowers/specs/2026-04-10-datasheet-store-design.md
§5 for the full phase sequence.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate.datasheet_db.storage import compute_sha256


def phase1_enumerate(repos_root: Path, bulk_root: Path, preserved_root: Path):
    """Yield entries for every PDF in the three source trees.

    Each entry is a dict: {path, sha256, size, filename, origin_kind, origin_ref}

    Filter rule: include files where either (a) the path contains a
    case-insensitive 'datasheet' segment, or (b) the file is > 50 KB.
    Excludes README PDFs, schematic printouts, and other non-datasheet PDFs.
    """
    # Source 1: repos/
    if repos_root.exists():
        for pdf in repos_root.rglob("*.pdf"):
            if not _is_likely_datasheet(pdf):
                continue
            yield _enum_entry(pdf, "repo", _repo_ref(pdf, repos_root))
    # Source 2: datasheets/ (flat bulk)
    if bulk_root.exists():
        for pdf in bulk_root.glob("*.pdf"):
            if pdf.is_file():
                yield _enum_entry(pdf, "bulk", "bulk")
    # Source 3: datasheets_from_repos/
    if preserved_root.exists():
        for pdf in preserved_root.rglob("*.pdf"):
            yield _enum_entry(pdf, "preserved", _preserved_ref(pdf, preserved_root))


def _is_likely_datasheet(pdf: Path) -> bool:
    path_str = str(pdf).lower()
    if "datasheet" in path_str:
        return True
    try:
        if pdf.stat().st_size > 50_000:
            return True
    except OSError:
        pass
    return False


def _enum_entry(pdf: Path, origin_kind: str, origin_ref: str) -> dict:
    return {
        "path": str(pdf),
        "sha256": compute_sha256(pdf),
        "size": pdf.stat().st_size,
        "filename": pdf.name,
        "origin_kind": origin_kind,
        "origin_ref": origin_ref,
    }


def _repo_ref(pdf: Path, repos_root: Path) -> str:
    rel = pdf.relative_to(repos_root)
    parts = rel.parts
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return "unknown"


def _preserved_ref(pdf: Path, preserved_root: Path) -> str:
    rel = pdf.relative_to(preserved_root)
    parts = rel.parts
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return "unknown"
