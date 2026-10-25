"""One DigiKey OAuth helper for the validate/ tools (arch A3-F5, sec A1-F10)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
pytestmark = pytest.mark.unit


def test_tools_share_the_helper(monkeypatch):
    sys.path.insert(0, str(HARNESS / "validate"))
    from validate import digikey_auth
    import validate_mpns, verify_constants_online
    assert validate_mpns.get_digikey_token is digikey_auth.get_digikey_token
    assert verify_constants_online.get_digikey_token is digikey_auth.get_digikey_token
    monkeypatch.delenv("DIGIKEY_CLIENT_ID", raising=False)
    assert digikey_auth.get_digikey_token() == (None, None)   # no network without credentials
