"""Blob storage: filename sanitization, atomic write, SHA256 computation."""

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
