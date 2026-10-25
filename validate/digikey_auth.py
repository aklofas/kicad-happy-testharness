"""DigiKey OAuth client-credentials token, shared by the validate/ tools that query the API."""
import json
import os
import sys
import urllib.parse
import urllib.request

TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"


def get_digikey_token():
    """(access_token, client_id), or (None, None) without credentials or on failure."""
    client_id = os.environ.get("DIGIKEY_CLIENT_ID", "")
    client_secret = os.environ.get("DIGIKEY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None, None
    try:
        data = urllib.parse.urlencode({
            "client_id": client_id, "client_secret": client_secret,
            "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request(
            TOKEN_URL, data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read()).get("access_token", "")
        return token, client_id
    except Exception as e:
        print(f"DigiKey auth failed: {e}", file=sys.stderr)
        return None, None
