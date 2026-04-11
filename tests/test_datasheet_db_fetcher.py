"""Unit tests for validate/datasheet_db/fetcher.py."""

TIER = "unit"

import sys
from pathlib import Path
import hashlib
from unittest.mock import patch, MagicMock

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.datasheet_db.fetcher import (
    sanitize_url, DomainRateLimiter, FetchResult, fetch_bytes, FetchError,
    fetch_verified, ShaVerificationResult, handle_drift
)


def test_sanitize_url_strips_signature():
    assert sanitize_url("https://x.com/p.pdf?sig=abc&id=1") == "https://x.com/p.pdf?id=1"


def test_sanitize_url_strips_token():
    assert sanitize_url("https://x.com/p.pdf?token=xyz") == "https://x.com/p.pdf"


def test_sanitize_url_strips_expires():
    assert sanitize_url("https://x.com/p.pdf?expires=999") == "https://x.com/p.pdf"


def test_sanitize_url_strips_aws_signing():
    assert sanitize_url("https://x.com/p.pdf?X-Amz-Signature=abc&X-Amz-Date=20260410") == "https://x.com/p.pdf"


def test_sanitize_url_preserves_benign_params():
    assert sanitize_url("https://x.com/p.pdf?id=1&lang=en") == "https://x.com/p.pdf?id=1&lang=en"


def test_sanitize_url_no_query():
    assert sanitize_url("https://x.com/p.pdf") == "https://x.com/p.pdf"


def test_sanitize_url_only_bad_params_drops_query():
    assert sanitize_url("https://x.com/p.pdf?sig=a&token=b") == "https://x.com/p.pdf"


def test_rate_limiter_no_wait_on_first_call():
    import time
    rl = DomainRateLimiter(interval_seconds=1.0)
    t0 = time.monotonic()
    rl.wait("example.com")
    elapsed = time.monotonic() - t0
    assert elapsed < 0.1, f"first call should not wait, waited {elapsed}"


def test_rate_limiter_waits_on_second_call_same_domain():
    import time
    rl = DomainRateLimiter(interval_seconds=0.2)
    rl.wait("example.com")
    t0 = time.monotonic()
    rl.wait("example.com")
    elapsed = time.monotonic() - t0
    assert 0.15 <= elapsed <= 0.35


def test_rate_limiter_no_wait_for_different_domain():
    import time
    rl = DomainRateLimiter(interval_seconds=1.0)
    rl.wait("a.example.com")
    t0 = time.monotonic()
    rl.wait("b.example.com")
    elapsed = time.monotonic() - t0
    assert elapsed < 0.1


def test_rate_limiter_treats_subdomains_distinctly():
    import time
    rl = DomainRateLimiter(interval_seconds=1.0)
    rl.wait("www.example.com")
    t0 = time.monotonic()
    rl.wait("api.example.com")
    elapsed = time.monotonic() - t0
    assert elapsed < 0.1


def test_rate_limiter_extracts_domain_from_url():
    import time
    rl = DomainRateLimiter(interval_seconds=0.2)
    rl.wait_for_url("https://example.com/a.pdf")
    t0 = time.monotonic()
    rl.wait_for_url("https://example.com/b.pdf")
    assert time.monotonic() - t0 >= 0.15


def _mock_response(body: bytes, status: int = 200, content_type: str = "application/pdf"):
    mock = MagicMock()
    mock.status = status
    mock.headers.get.return_value = content_type
    mock.__enter__ = lambda self: self
    mock.__exit__ = lambda self, *a: None
    # Split body into 8K chunks for streaming read
    chunks = [body[i:i+8192] for i in range(0, len(body), 8192)] + [b""]
    mock.read.side_effect = chunks
    return mock


def test_fetch_bytes_success():
    body = b"%PDF-1.5\n" + b"X" * 1000
    expected_sha = hashlib.sha256(body).hexdigest()
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_bytes("https://x.com/a.pdf")
        assert isinstance(result, FetchResult)
        assert result.sha256 == expected_sha
        assert result.size_bytes == len(body)
        assert result.content_type == "application/pdf"


def test_fetch_bytes_404_raises():
    with patch("urllib.request.urlopen", side_effect=Exception("HTTP 404")):
        try:
            fetch_bytes("https://x.com/missing.pdf")
            assert False, "should have raised"
        except FetchError:
            pass


def test_fetch_bytes_rejects_non_pdf_content_type():
    body = b"<html>not a pdf</html>"
    with patch("urllib.request.urlopen", return_value=_mock_response(body, content_type="text/html")):
        try:
            fetch_bytes("https://x.com/a.pdf")
            assert False, "should have raised"
        except FetchError as e:
            assert "content" in str(e).lower() or "pdf" in str(e).lower()


def test_fetch_bytes_accepts_pdf_magic_bytes_without_content_type():
    body = b"%PDF-1.5\n" + b"X" * 100
    with patch("urllib.request.urlopen", return_value=_mock_response(body, content_type="application/octet-stream")):
        result = fetch_bytes("https://x.com/a.pdf")
        assert result.size_bytes == len(body)


def test_fetch_bytes_rejects_non_pdf_magic_bytes():
    body = b"NOT_A_PDF" + b"X" * 100
    with patch("urllib.request.urlopen", return_value=_mock_response(body, content_type="application/octet-stream")):
        try:
            fetch_bytes("https://x.com/a.pdf")
            assert False, "should have raised"
        except FetchError:
            pass


def test_fetch_verified_matches():
    body = b"%PDF-1.5\n" + b"X" * 100
    sha = hashlib.sha256(body).hexdigest()
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_verified("https://x.com/a.pdf", expected_sha256=sha)
        assert result.matched is True
        assert result.fetch_result.sha256 == sha


def test_fetch_verified_mismatch():
    body = b"%PDF-1.5\n" + b"X" * 100
    wrong_sha = "00" * 32
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_verified("https://x.com/a.pdf", expected_sha256=wrong_sha)
        assert result.matched is False
        assert result.fetch_result.sha256 != wrong_sha


def test_fetch_verified_no_expected_always_matches():
    """expected_sha256=None means 'take whatever you get'."""
    body = b"%PDF-1.5\n" + b"X" * 100
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_verified("https://x.com/a.pdf", expected_sha256=None)
        assert result.matched is True


def _with_temp_manifest_dir(fn):
    """Helper: run `fn(tmp_path)` with MANIFEST_DIR pointed at a tmp dir."""
    from validate.datasheet_db import manifest as m
    original = m.MANIFEST_DIR
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        m.MANIFEST_DIR = Path(tmp)
        try:
            fn(Path(tmp))
        finally:
            m.MANIFEST_DIR = original


def test_handle_drift_creates_new_record():
    """Drift creates a new record with the new SHA and inherits metadata."""
    def inner(tmp):
        from validate.datasheet_db.manifest import save_record, load_record
        old_sha = "aa" * 32
        new_body = b"%PDF-1.5\n" + b"Y" * 100
        new_sha = hashlib.sha256(new_body).hexdigest()
        old_record = {
            "sha256": old_sha,
            "size_bytes": 1024,
            "page_count": 10,
            "mpns": [{"mpn": "R1", "primary": True}],
            "manufacturers": ["Acme"],
            "source_urls": [{
                "url": "https://x.com/a.pdf",
                "first_seen_at": "2026-04-10T00:00:00Z",
                "last_verified_at": "2026-04-10T00:00:00Z",
                "status": "live",
            }],
            "filename_aliases": [],
            "found_in": [],
            "revision_label": None,
            "first_seen": "2026-04-10T00:00:00Z",
            "last_seen": "2026-04-10T00:00:00Z",
            "verified": True,
            "verification_notes": None,
        }
        save_record(old_record)

        handle_drift(
            old_record=old_record,
            drifted_url="https://x.com/a.pdf",
            new_body=new_body,
            new_sha256=new_sha,
            now="2026-04-11T00:00:00Z",
        )

        new_record = load_record(new_sha)
        assert new_record is not None
        assert new_record["sha256"] == new_sha
        # Inherited MPN (marked as inherited)
        assert len(new_record["mpns"]) == 1
        assert new_record["mpns"][0]["mpn"] == "R1"
        # possible_revision_of back-reference
        assert old_sha in new_record.get("possible_revision_of", [])
        # verified=False (human must re-verify)
        assert new_record["verified"] is False

    _with_temp_manifest_dir(inner)


def test_handle_drift_updates_old_record_url_status():
    """Drift marks the old record's matching URL entry as 'drifted'."""
    def inner(tmp):
        from validate.datasheet_db.manifest import save_record, load_record
        # Same setup as above
        old_sha = "bb" * 32
        new_body = b"%PDF-1.5\n" + b"Z" * 100
        new_sha = hashlib.sha256(new_body).hexdigest()
        old_record = {
            "sha256": old_sha,
            "size_bytes": 1024,
            "page_count": 10,
            "mpns": [{"mpn": "R2", "primary": True}],
            "manufacturers": ["Acme"],
            "source_urls": [{
                "url": "https://y.com/b.pdf",
                "first_seen_at": "2026-04-10T00:00:00Z",
                "last_verified_at": "2026-04-10T00:00:00Z",
                "status": "live",
            }],
            "filename_aliases": [],
            "found_in": [],
            "revision_label": None,
            "first_seen": "2026-04-10T00:00:00Z",
            "last_seen": "2026-04-10T00:00:00Z",
            "verified": True,
            "verification_notes": None,
        }
        save_record(old_record)

        handle_drift(old_record, "https://y.com/b.pdf", new_body, new_sha,
                     now="2026-04-11T00:00:00Z")

        reloaded = load_record(old_sha)
        url_entry = next(u for u in reloaded["source_urls"] if u["url"] == "https://y.com/b.pdf")
        assert url_entry["status"] == "drifted"
        assert url_entry["drifted_to_sha256"] == new_sha

    _with_temp_manifest_dir(inner)


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
