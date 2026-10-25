"""
KH-368: _strip_jsonc must be string-aware.

The old comment-stripping used two regexes (`//.*?$`, `/\\*.*?\\*/`) applied
directly to the raw text, blind to whether the matched text sits inside a
JSON string literal. That corrupts config values containing `//` (URLs) or
`/* ... */` (arbitrary text) — silently dropping or mangling whole config
layers.

No `load_jsonc_string` entry point exists (only `load_jsonc(path)` which reads a
file, and the private `_strip_jsonc(text)` helper; both live in `kicad_core.project`
since v3 round 3, re-exported from the old config module as a facade). Per the task brief's fallback, these tests exercise
`_strip_jsonc` + `json.loads` directly.
"""

import json
import os
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = str(PRODUCT_ROOT)
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_core.project import _strip_jsonc  # noqa: E402  (v3 round 3 relocation)


def _load(s):
    return json.loads(_strip_jsonc(s))


def test_url_in_string_survives():
    assert _load('{"documentation": "https://example.com/spec"}') == \
        {"documentation": "https://example.com/spec"}


def test_block_marker_in_string_survives():
    s = '{"note": "do not treat /* this */ as a comment"}'
    assert _load(s)["note"] == "do not treat /* this */ as a comment"


def test_real_comments_still_stripped():
    s = '{\n// header\n"a": 1, /* inline */ "b": 2, // trail\n"c": 3,\n}'
    assert _load(s) == {"a": 1, "b": 2, "c": 3}


def test_escaped_quote_in_string():
    assert _load(r'{"q": "she said \"hi\" // not a comment"}')["q"] == \
        'she said "hi" // not a comment'
