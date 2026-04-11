"""HTTP fetcher with URL sanitization, per-domain rate limiting, and drift handling."""

from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import threading
import time
import hashlib
import urllib.request
from dataclasses import dataclass


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


class FetchError(Exception):
    """Raised when an HTTP fetch fails or returns non-PDF content."""


@dataclass
class FetchResult:
    """Return value from fetch_bytes: the downloaded body + metadata."""
    body: bytes
    sha256: str
    size_bytes: int
    content_type: str


_FETCH_CHUNK_BYTES = 8192
_FETCH_USER_AGENT = "kicad-happy-testharness/1.3 (+https://github.com/aklofas/kicad-happy-testharness)"
_FETCH_MAX_REDIRECTS = 5
_FETCH_DEFAULT_TIMEOUT = 60.0
_PDF_MAGIC = b"%PDF-"
_ACCEPTED_CONTENT_TYPES = {"application/pdf", "application/octet-stream", ""}


def fetch_bytes(url: str, timeout: float = _FETCH_DEFAULT_TIMEOUT) -> FetchResult:
    """Download `url` and return a FetchResult.

    Streams the body in 8 KB chunks, computing SHA256 as it goes. Verifies
    content-type is PDF-like OR the first bytes match the PDF magic number.
    Raises FetchError on any network failure or non-PDF response.

    Does NOT perform SHA256 verification against an expected value — that's
    the caller's job (see fetch_verified in Task 15).
    """
    req = urllib.request.Request(url, headers={"User-Agent": _FETCH_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
            buf = bytearray()
            h = hashlib.sha256()
            while True:
                chunk = resp.read(_FETCH_CHUNK_BYTES)
                if not chunk:
                    break
                buf.extend(chunk)
                h.update(chunk)
            body = bytes(buf)
    except FetchError:
        raise
    except Exception as e:
        raise FetchError(f"HTTP error fetching {url}: {e}")

    # PDF sniff: either the content-type is PDF-ish OR the magic bytes match
    is_pdf_ctype = content_type in _ACCEPTED_CONTENT_TYPES and "pdf" in content_type
    is_pdf_magic = body.startswith(_PDF_MAGIC)
    if content_type == "application/pdf":
        pass  # trust explicit PDF content-type
    elif is_pdf_magic:
        pass  # trust magic bytes
    else:
        raise FetchError(
            f"fetched {url} but content is not a PDF "
            f"(content-type={content_type!r}, first 8 bytes={body[:8]!r})"
        )

    return FetchResult(
        body=body,
        sha256=h.hexdigest(),
        size_bytes=len(body),
        content_type=content_type,
    )


@dataclass
class ShaVerificationResult:
    """Result of fetch_verified: the underlying FetchResult + match status."""
    fetch_result: FetchResult
    matched: bool      # True if no expected sha, or if expected matches actual
    expected_sha256: str  # None if no verification was requested


def fetch_verified(url: str, expected_sha256: str = None, timeout: float = _FETCH_DEFAULT_TIMEOUT) -> ShaVerificationResult:
    """Fetch `url` and report whether its SHA256 matches `expected_sha256`.

    Does NOT raise on mismatch — returns `matched=False` so the caller
    can handle drift vs corruption as appropriate. Still raises on
    network errors and non-PDF content.
    """
    result = fetch_bytes(url, timeout=timeout)
    if expected_sha256 is None:
        return ShaVerificationResult(
            fetch_result=result, matched=True, expected_sha256=None
        )
    return ShaVerificationResult(
        fetch_result=result,
        matched=(result.sha256 == expected_sha256),
        expected_sha256=expected_sha256,
    )


def handle_drift(old_record: dict, drifted_url: str, new_body: bytes,
                 new_sha256: str, now: str = None) -> dict:
    """Handle a URL that returned different bytes than the manifest claims.

    Creates a new manifest record at `new_sha256` inheriting MPN and
    manufacturer metadata from `old_record`, and updates the old record's
    matching source_urls entry with `status="drifted"` and
    `drifted_to_sha256=new_sha256`.

    Does NOT write the new blob to `datasheets/` — that's the caller's
    job (storage.write_blob_atomic). This function only handles the
    manifest-side bookkeeping.

    Returns the new record dict (already saved to disk).
    """
    from datetime import datetime, timezone
    from validate.datasheet_db.manifest import save_record, load_record, merge_record
    import copy

    if now is None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build the new inherited record
    new_record = {
        "sha256": new_sha256,
        "size_bytes": len(new_body),
        "page_count": None,  # caller can update if they extract it
        "mpns": [dict(m) for m in old_record["mpns"]],
        "manufacturers": list(old_record.get("manufacturers") or []),
        "source_urls": [{
            "url": drifted_url,
            "first_seen_at": now,
            "last_verified_at": now,
            "status": "live",
        }],
        "filename_aliases": [],
        "found_in": [],
        "revision_label": None,
        "first_seen": now,
        "last_seen": now,
        "verified": False,
        "verification_notes": f"Created from drift on {drifted_url}; see possible_revision_of",
        "possible_revision_of": [old_record["sha256"]],
    }
    save_record(new_record)

    # Update the old record's matching URL entry
    old_updated = copy.deepcopy(old_record)
    for u in old_updated.get("source_urls") or []:
        if u["url"] == drifted_url:
            u["status"] = "drifted"
            u["drifted_to_sha256"] = new_sha256
    old_updated["last_seen"] = now
    save_record(old_updated)

    return new_record
