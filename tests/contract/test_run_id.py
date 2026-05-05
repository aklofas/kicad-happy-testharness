"""Tests for run_id.generate_run_id."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from run_id import generate_run_id  # noqa: E402


RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$")


def test_default_format():
    rid = generate_run_id()
    assert RUN_ID_RE.match(rid), f"Unexpected run_id format: {rid}"


def test_deterministic_with_injected_clock_and_random():
    fixed_now = datetime(2026, 4, 18, 12, 34, 56, tzinfo=timezone.utc)
    rid = generate_run_id(now=fixed_now, rand_hex="abc123")
    assert rid == "20260418T123456Z-abc123"


def test_two_calls_produce_different_ids():
    """Randomness source gives distinct IDs even within the same second."""
    fixed_now = datetime(2026, 4, 18, 12, 34, 56, tzinfo=timezone.utc)
    r1 = generate_run_id(now=fixed_now)
    r2 = generate_run_id(now=fixed_now)
    # Same timestamp but different random suffixes (overwhelmingly likely).
    assert r1 != r2
    assert r1[:16] == r2[:16]  # timestamp prefix matches
    assert r1[-6:] != r2[-6:]  # random suffix differs


def test_rand_hex_must_be_six_hex_chars():
    """Explicit rand_hex is length-checked so consumers can't pass junk."""
    import pytest
    fixed_now = datetime(2026, 4, 18, 12, 34, 56, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="6 hex"):
        generate_run_id(now=fixed_now, rand_hex="abc")  # too short
    with pytest.raises(ValueError, match="6 hex"):
        generate_run_id(now=fixed_now, rand_hex="abcdefg")  # too long
    with pytest.raises(ValueError, match="6 hex"):
        generate_run_id(now=fixed_now, rand_hex="xyzxyz")  # non-hex
