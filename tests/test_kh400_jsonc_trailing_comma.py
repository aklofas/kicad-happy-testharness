"""KH-400 — `_TRAILING_COMMA` regex ran over the whole JSONC text after the
string-aware comment stripper, deleting a comma inside a string literal that
ends in `,}` / `,]`. Fold trailing-comma removal into a string-aware pass."""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from project_config import _strip_jsonc  # noqa: E402


def test_comma_inside_string_survives():
    assert json.loads(_strip_jsonc('{"a": "foo,}bar"}')) == {"a": "foo,}bar"}
    assert json.loads(_strip_jsonc('{"a": "x,]"}')) == {"a": "x,]"}


def test_real_trailing_commas_still_stripped():
    src = '{"a": [1, 2, ], "b": {"c": 1, }, // comment\n }'
    assert json.loads(_strip_jsonc(src)) == {"a": [1, 2], "b": {"c": 1}}


def test_trailing_comma_before_comment_then_brace():
    src = '{"a": 1, /* note */ }'
    assert json.loads(_strip_jsonc(src)) == {"a": 1}


def test_escaped_quote_in_string():
    assert json.loads(_strip_jsonc('{"a": "q\\"uo,}te", }')) == {"a": 'q"uo,}te'}


if __name__ == "__main__":
    import sys
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
