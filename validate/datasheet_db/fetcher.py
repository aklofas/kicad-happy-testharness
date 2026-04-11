"""HTTP fetcher with URL sanitization, per-domain rate limiting, and drift handling."""

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import threading
import time


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


class DomainRateLimiter:
    """Serialize requests per domain with a minimum interval.

    Thread-safe. One shared instance across all workers in a single process.
    Does NOT cross process boundaries — if you use ProcessPoolExecutor, each
    process has its own limiter and the first request per domain per process
    is not rate-limited. This is a known limitation we accept for
    simplicity (see spec §4.5).
    """

    def __init__(self, interval_seconds: float = 1.0):
        self.interval = interval_seconds
        self._locks = {}  # domain -> Lock
        self._last_seen = {}  # domain -> monotonic timestamp
        self._master = threading.Lock()

    def _lock_for(self, domain: str) -> threading.Lock:
        with self._master:
            if domain not in self._locks:
                self._locks[domain] = threading.Lock()
            return self._locks[domain]

    def wait(self, domain: str) -> None:
        """Block until it's OK to make a new request to `domain`."""
        lock = self._lock_for(domain)
        with lock:
            now = time.monotonic()
            last = self._last_seen.get(domain, 0)
            wait_needed = (last + self.interval) - now
            if wait_needed > 0:
                time.sleep(wait_needed)
            self._last_seen[domain] = time.monotonic()

    def wait_for_url(self, url: str) -> None:
        """Extract domain from `url` and wait. Includes subdomain."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        self.wait(domain)
