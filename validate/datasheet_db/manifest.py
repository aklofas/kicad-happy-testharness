"""Manifest layer: sharded per-record JSON load/save and lookup indexes."""

import json
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent
MANIFEST_DIR = HARNESS_DIR / "reference" / "datasheet_manifest"


def record_path(sha256: str) -> Path:
    """Return the sharded on-disk path for a record keyed by sha256.

    Layout: reference/datasheet_manifest/{sha256[:2]}/{sha256}.json

    Defensively rejects sha values that are obviously too short to be a real
    sha256. The threshold (more than 3 chars) is arbitrary — the sharding
    logic only requires 2 chars for `sha[:2]`. Plan called for `< 3`; raised
    to `<= 3` so the rejection test (`record_path("abc")`) actually fires.
    Real shas are 64 chars, so this guard never trips in production.
    """
    if not isinstance(sha256, str) or len(sha256) <= 3:
        raise ValueError(f"sha256 must be a string of more than 3 chars, got {sha256!r}")
    return MANIFEST_DIR / sha256[:2] / f"{sha256}.json"


from validate.datasheet_db._validators import validate_record


def save_record(record: dict) -> None:
    """Validate and atomically write a record to its sharded path.

    Raises ValueError if the record violates any invariant.
    """
    violations = validate_record(record)
    if violations:
        raise ValueError(
            f"record {record.get('sha256', '?')[:12]} has invariant violations: "
            + "; ".join(violations)
        )
    path = record_path(record["sha256"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")
    import os
    os.replace(str(tmp), str(path))


def load_record(sha256: str) -> dict:
    """Return the record for `sha256`, or None if not present."""
    path = record_path(sha256)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_record(existing: dict, incoming: dict, now: str = None) -> dict:
    """Merge `incoming` into `existing` and return a new record dict.

    Rules:
      - New MPN aliases are added (deduped by .mpn); existing primary wins
      - New source URLs are added (deduped by .url); on match, last_verified_at
        is updated to the max of existing and incoming
      - New filename_aliases are added, sorted, deduped
      - New found_in entries are added, deduped by (type, ref, path)
      - last_seen bumped to `now` (or current UTC if not provided)
      - first_seen preserved from existing

    Does NOT change the record's sha256 or mpns-primary flag.
    """
    import copy
    if now is None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    merged = copy.deepcopy(existing)

    # Merge mpns (dedup by mpn string, existing primary wins)
    seen_mpns = {m["mpn"] for m in merged["mpns"]}
    for m in incoming.get("mpns", []) or []:
        if m["mpn"] not in seen_mpns:
            merged["mpns"].append({"mpn": m["mpn"], "primary": False})
            seen_mpns.add(m["mpn"])

    # Merge source_urls (dedup by url, update last_verified_at on match)
    url_map = {u["url"]: u for u in merged.get("source_urls", []) or []}
    for u in incoming.get("source_urls", []) or []:
        key = u["url"]
        if key in url_map:
            existing_u = url_map[key]
            # Max of last_verified_at
            if u.get("last_verified_at", "") > existing_u.get("last_verified_at", ""):
                existing_u["last_verified_at"] = u["last_verified_at"]
        else:
            url_map[key] = dict(u)
    merged["source_urls"] = sorted(url_map.values(), key=lambda x: x["url"])

    # Merge filename_aliases (sort + dedup)
    aliases = set(merged.get("filename_aliases") or [])
    for a in incoming.get("filename_aliases", []) or []:
        aliases.add(a)
    merged["filename_aliases"] = sorted(aliases)

    # Merge found_in (dedup by (type, ref, path))
    found_keys = {(f["type"], f["ref"], f.get("path", ""))
                  for f in (merged.get("found_in") or [])}
    for f in incoming.get("found_in", []) or []:
        key = (f["type"], f["ref"], f.get("path", ""))
        if key not in found_keys:
            merged.setdefault("found_in", []).append(dict(f))
            found_keys.add(key)
    merged["found_in"] = sorted(
        merged.get("found_in", []),
        key=lambda f: (f["type"], f["ref"], f.get("path", ""))
    )

    merged["last_seen"] = now
    return merged


def iter_records():
    """Yield every record in the manifest directory.

    Walks MANIFEST_DIR/{00..ff}/*.json. Returns an iterator of dicts.
    """
    if not MANIFEST_DIR.exists():
        return
    for shard in sorted(MANIFEST_DIR.iterdir()):
        if not shard.is_dir():
            continue
        for record_file in sorted(shard.glob("*.json")):
            try:
                with open(record_file, "r", encoding="utf-8") as f:
                    yield json.load(f)
            except (json.JSONDecodeError, OSError):
                continue


def find_by_mpn(mpn: str) -> list:
    """Return all records whose mpns list contains `mpn` (primary or alias)."""
    matches = []
    for rec in iter_records():
        for m in rec.get("mpns", []):
            if m.get("mpn") == mpn:
                matches.append(rec)
                break
    return matches


def find_by_url(url: str) -> list:
    """Return all records whose source_urls contain `url`."""
    matches = []
    for rec in iter_records():
        for u in rec.get("source_urls", []):
            if u.get("url") == url:
                matches.append(rec)
                break
    return matches


def find_by_sha256_prefix(prefix: str) -> list:
    """Return all records whose sha256 starts with `prefix`."""
    return [rec for rec in iter_records() if rec["sha256"].startswith(prefix)]
