"""Blob storage: filename sanitization, atomic write, SHA256 computation."""

import hashlib

_BAD_CHARS = set('/\\:*?"<>|')


def _sanitize_mpn(mpn: str) -> str:
    """Return a filesystem-safe form of `mpn`.

    Rules (in order):
      1. Replace each char in /\\:*?"<>|, any whitespace, or any non-ASCII
         character with '_'
      2. Collapse runs of '_' to a single '_'
      3. Strip leading and trailing '_' and '.'

    The result may be an empty string if `mpn` contains only problematic
    characters. Callers handle the empty case by falling back to
    `"unknown-{sha256[:8]}"`.
    """
    out = []
    for ch in mpn:
        if ch in _BAD_CHARS or ch.isspace() or ord(ch) > 127:
            out.append("_")
        else:
            out.append(ch)
    # Collapse runs of underscore
    collapsed = []
    prev_underscore = False
    for ch in out:
        if ch == "_":
            if not prev_underscore:
                collapsed.append(ch)
            prev_underscore = True
        else:
            collapsed.append(ch)
            prev_underscore = False
    # Strip leading/trailing _ and .
    return "".join(collapsed).strip("_.")


def _truncate_to_byte_limit(name: str, byte_limit: int) -> str:
    """Truncate `name` so its UTF-8 byte length is <= `byte_limit`.

    When truncation happens, the last character is replaced with '_' to
    signal a truncation visually. If the name already fits, return as-is.

    All callers pass already-sanitized ASCII-only names, so byte length
    equals character length in practice — we still count bytes for
    consistency with the TH-013 fix conventions (see
    utils._truncate_with_hash)."""
    encoded = name.encode("utf-8")
    if len(encoded) <= byte_limit:
        return name
    # Reserve one byte for the trailing underscore marker
    truncated = encoded[: byte_limit - 1].decode("utf-8", errors="ignore")
    return truncated + "_"


# The total filename budget is 143 bytes to stay within the TH-013
# eCryptfs filename-length limit (see FIXED.md → TH-013). The suffix
# "-{sha256[:8]}.pdf" is always exactly 13 bytes (1 + 8 + 4), leaving
# 130 bytes for the sanitized primary MPN.
_FILENAME_BYTE_LIMIT = 143
_SUFFIX_BYTES = len("-12345678.pdf")  # 13
_PRIMARY_MPN_BYTE_BUDGET = _FILENAME_BYTE_LIMIT - _SUFFIX_BYTES  # 130


def canonical_filename(record: dict) -> str:
    """Return the canonical on-disk filename for a manifest record.

    Form: `{sanitize(primary_mpn)}-{sha256[:8]}.pdf`. Truncated if the
    sanitized primary MPN exceeds the 130-byte budget. Falls back to
    `unknown-{sha256[:8]}.pdf` if the primary MPN sanitizes to empty.

    Raises ValueError if the record lacks a primary MPN entry — this is a
    programming error, not a data-quality issue, and should never happen
    on records loaded from disk (invariant checks catch it earlier).
    """
    mpns = record.get("mpns") or []
    primary = None
    for entry in mpns:
        if entry.get("primary"):
            primary = entry.get("mpn", "")
            break
    if primary is None:
        raise ValueError(
            f"record {record.get('sha256', '?')[:12]} has no primary MPN "
            f"(mpns={mpns})"
        )
    sanitized = _sanitize_mpn(primary)
    if not sanitized:
        sanitized = "unknown"
    truncated = _truncate_to_byte_limit(sanitized, _PRIMARY_MPN_BYTE_BUDGET)
    sha = record["sha256"]
    return f"{truncated}-{sha[:8]}.pdf"


_SHA256_CHUNK_BYTES = 8192


def compute_sha256(path) -> str:
    """Return the SHA256 hex digest of the file at `path`.

    Streams the file in 8 KB chunks to avoid loading large PDFs into
    memory. `path` may be a str or pathlib.Path.
    """
    h = hashlib.sha256()
    with open(str(path), "rb") as f:
        while True:
            chunk = f.read(_SHA256_CHUNK_BYTES)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
