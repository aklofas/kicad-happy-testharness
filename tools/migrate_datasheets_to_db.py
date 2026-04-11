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
import re
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


_MPN_TOKEN_RE = re.compile(r"[A-Z0-9][A-Z0-9_\-]{3,}[A-Z0-9]")

_MANUFACTURER_PREFIXES = {
    "ad": "Analog Devices", "adi": "Analog Devices",
    "ti": "Texas Instruments", "txn": "Texas Instruments",
    "stm": "STMicroelectronics", "st": "STMicroelectronics",
    "nxp": "NXP",
    "pic": "Microchip", "atmel": "Microchip",
    "on": "ON Semiconductor",
    "ltc": "Linear Technology",
    "max": "Maxim Integrated",
}


def _infer_mpn(filename: str) -> str:
    """Return the longest MPN-looking token from `filename` stem, or the stem itself."""
    stem = Path(filename).stem.upper().replace("-", "_")
    tokens = _MPN_TOKEN_RE.findall(stem)
    if tokens:
        return max(tokens, key=len)
    return Path(filename).stem


def _infer_manufacturer(filename: str) -> str:
    lower = Path(filename).stem.lower()
    for prefix, mfr in _MANUFACTURER_PREFIXES.items():
        if lower.startswith(prefix):
            return mfr
    return "Unknown"


def phase2_group(entries: list) -> list:
    """Group entries by SHA256, return one record per unique SHA."""
    from datetime import datetime, timezone
    from collections import defaultdict
    buckets = defaultdict(list)
    for e in entries:
        buckets[e["sha256"]].append(e)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    for sha, bucket in buckets.items():
        filenames = sorted({e["filename"] for e in bucket})
        primary_mpn = _infer_mpn(filenames[0])
        manufacturer = _infer_manufacturer(filenames[0])
        records.append({
            "sha256": sha,
            "size_bytes": bucket[0]["size"],
            "page_count": None,
            "mpns": [{"mpn": primary_mpn, "primary": True}],
            "manufacturers": [manufacturer],
            "source_urls": [],
            "filename_aliases": filenames,
            "found_in": sorted([
                {"type": e["origin_kind"], "ref": e["origin_ref"],
                 "path": e["path"], "first_seen": now}
                for e in bucket
            ], key=lambda f: (f["type"], f["ref"], f["path"])),
            "revision_label": None,
            "first_seen": now,
            "last_seen": now,
            "verified": False,
            "verification_notes": None,
        })
    return records


def phase3_stage(records, staging_store, staging_manifest):
    """Copy blobs to `staging_store` and write record JSONs to `staging_manifest`.

    Each record's first `found_in` entry is used as the source path for the
    blob copy. The blob lands at `staging_store/{canonical_filename(rec)}`.
    The record JSON lands at `staging_manifest/{sha[:2]}/{sha}.json`.
    """
    import json
    import shutil
    from validate.datasheet_db.storage import canonical_filename

    staging_store = Path(staging_store)
    staging_manifest = Path(staging_manifest)
    staging_store.mkdir(parents=True, exist_ok=True)
    staging_manifest.mkdir(parents=True, exist_ok=True)

    for rec in records:
        found_in = rec.get("found_in") or []
        if not found_in:
            continue
        source_path = Path(found_in[0]["path"])
        if not source_path.exists():
            continue

        # Copy the blob
        blob_target = staging_store / canonical_filename(rec)
        blob_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source_path), str(blob_target))

        # Write the record JSON to the sharded staging manifest
        sha = rec["sha256"]
        record_target = staging_manifest / sha[:2] / f"{sha}.json"
        record_target.parent.mkdir(parents=True, exist_ok=True)
        with open(record_target, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, sort_keys=True)
            f.write("\n")


def phase4_swap(live_store, live_manifest, staging_store, staging_manifest,
                bulk_bak, preserved_root, preserved_bak):
    """Swap staging directories into live positions, backing up the originals.

    Sequence (each step is a single rename, atomic on POSIX):
      1. live_store → bulk_bak (preserve original bulk tree)
      2. staging_store → live_store (promote staging to live)
      3. preserved_root → preserved_bak (preserve original repo-preserved tree)
      4. staging_manifest → live_manifest (promote staging manifest to live)

    If interrupted between any two steps, the state is recoverable manually
    via the .bak directories.
    """
    import shutil

    live_store = Path(live_store)
    live_manifest = Path(live_manifest)
    staging_store = Path(staging_store)
    staging_manifest = Path(staging_manifest)
    bulk_bak = Path(bulk_bak)
    preserved_root = Path(preserved_root)
    preserved_bak = Path(preserved_bak)

    # Step 1: back up live store (if it exists)
    if live_store.exists():
        shutil.move(str(live_store), str(bulk_bak))

    # Step 2: promote staging store to live
    shutil.move(str(staging_store), str(live_store))

    # Step 3: back up preserved tree (if it exists)
    if preserved_root.exists():
        shutil.move(str(preserved_root), str(preserved_bak))

    # Step 4: promote staging manifest to live
    if live_manifest.exists():
        # Defensive: a previous failed migration may have left a manifest behind
        shutil.rmtree(str(live_manifest))
    shutil.move(str(staging_manifest), str(live_manifest))
