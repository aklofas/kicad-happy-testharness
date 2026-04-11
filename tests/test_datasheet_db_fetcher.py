"""Unit tests for validate/datasheet_db/fetcher.py."""

TIER = "unit"

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from validate.datasheet_db.fetcher import sanitize_url, DomainRateLimiter


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
