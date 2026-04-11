"""Schema invariant checks for manifest records. Private to the package.

Each public checker returns a list of human-readable violation strings.
An empty list means the record is valid. Callers should raise on non-empty
results — invariant violations are programming errors, not data-quality
issues."""

import re


_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_record(record: dict) -> list:
    """Return a list of invariant violations for `record`.

    Empty list = valid. Non-empty = each string describes one violation.

    Checks (in order):
      1. sha256 present, string, 64 hex chars lowercase
      2. mpns present, non-empty list
      3. exactly one mpns entry has primary=True
      4. source_urls sorted alphabetically by 'url' field
      5. filename_aliases sorted alphabetically
      6. first_seen <= last_seen (string comparison on ISO 8601 is valid)
    """
    violations = []

    # 1. sha256
    sha = record.get("sha256")
    if sha is None:
        violations.append("missing sha256")
    elif not isinstance(sha, str) or not _SHA256_HEX_RE.match(sha):
        violations.append(
            f"sha256 must be 64 lowercase hex chars, got {sha!r}"
        )

    # 2. mpns present and non-empty
    mpns = record.get("mpns")
    if mpns is None:
        violations.append("missing mpns")
    elif not isinstance(mpns, list) or len(mpns) == 0:
        violations.append("mpns must be a non-empty list")
    else:
        # 3. exactly one primary
        primary_count = sum(1 for m in mpns if m.get("primary") is True)
        if primary_count == 0:
            violations.append("no mpns entry has primary=True")
        elif primary_count > 1:
            violations.append(
                f"mpns has {primary_count} entries with primary=True, must be exactly 1"
            )

    # 4. source_urls sorted
    source_urls = record.get("source_urls") or []
    url_keys = [u.get("url", "") for u in source_urls]
    if url_keys != sorted(url_keys):
        violations.append("source_urls must be sorted alphabetically by url")

    # 5. filename_aliases sorted
    aliases = record.get("filename_aliases") or []
    if aliases != sorted(aliases):
        violations.append("filename_aliases must be sorted alphabetically")

    # 6. first_seen <= last_seen
    first = record.get("first_seen")
    last = record.get("last_seen")
    if first and last and first > last:
        violations.append(
            f"first_seen ({first}) must be <= last_seen ({last})"
        )

    return violations
