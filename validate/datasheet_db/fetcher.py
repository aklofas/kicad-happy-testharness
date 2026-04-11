"""HTTP fetcher with URL sanitization, per-domain rate limiting, and drift handling."""

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


# Query parameter names that indicate auth tokens or session-specific state.
# These are stripped from URLs before committing them to the manifest because
# they expire (making the URL useless after minutes) and may contain secrets.
_BAD_QUERY_KEYS = frozenset([
    "sig", "signature", "token", "auth", "key", "expires", "expire",
    "X-Amz-Signature", "X-Amz-Date", "X-Amz-Expires", "X-Amz-SignedHeaders",
    "X-Amz-Credential", "X-Amz-Algorithm", "X-Amz-Security-Token",
])


def sanitize_url(url: str) -> str:
    """Return `url` with known-problematic query parameters stripped.

    Strips params matching `_BAD_QUERY_KEYS` (case-sensitive for AWS-style,
    case-insensitive for the short forms). Preserves scheme, host, path,
    and all other query params. Drops the `?` entirely if no params remain.
    """
    parsed = urlparse(url)
    if not parsed.query:
        return url
    kept = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key in _BAD_QUERY_KEYS or key.lower() in {k.lower() for k in _BAD_QUERY_KEYS}:
            continue
        kept.append((key, value))
    new_query = urlencode(kept)
    return urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, new_query, parsed.fragment,
    ))
