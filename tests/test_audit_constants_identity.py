"""audit_constants identity must not carry source line numbers (TH-065).

Two registry classes keyed by line: synthetic inline-keyword names (`func:<line>`) and
the `ast_<line>` content hash of non-literal constants. A pure line shift renamed the
first (removed + re-added) and marked the second stale.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_constants as ac  # noqa: E402

pytestmark = pytest.mark.unit

INLINE_SRC = '''
def f(v):
    if any(k in v for k in ("alpha", "beta", "gamma")):
        return 1
    if any(k in v for k in ("delta", "epsilon", "zeta")):
        return 2
    return 0
'''

DICT_SRC = '''
def f(x, y, z):
    reg = {"a": x, "b": y, "c": z}
    return reg
'''


def _scan(tmp_path, src, prefix_lines=0):
    p = tmp_path / "m.py"
    p.write_text("\n" * prefix_lines + textwrap.dedent(src), encoding="utf-8")
    return ac.scan_file(p, tmp_path)


def _entry(name, content_hash, scope="f", status="verified", **extra):
    e = {"id": extra.pop("id", "CONST-001"), "file": "m.py", "scope": scope, "function": scope,
         "name": name, "line": 1, "end_line": 1, "type": "inline_keywords", "entry_count": 3,
         "content_hash": content_hash, "status": status, "source": "s" if status == "verified" else None,
         "notes": None, "verified_entries": 0}
    e.update(extra)
    return e


def _info(name, content_hash, scope="f", const_type="inline_keywords", line=1):
    return ac.ConstantInfo(name=name, file="m.py", line=line, scope=scope, func=scope,
                           const_type=const_type, entry_count=3, content_hash=content_hash)


# --- inline keyword sets -------------------------------------------------------------------

def test_inline_keyword_name_is_an_ordinal_within_the_function(tmp_path):
    names = [c.name for c in _scan(tmp_path, INLINE_SRC) if c.const_type == "inline_keywords"]
    assert names == ["f:kw1", "f:kw2"]


def test_inline_keyword_identity_survives_a_line_shift(tmp_path):
    a = [(c.file, c.scope, c.name, c.content_hash) for c in _scan(tmp_path, INLINE_SRC)]
    b = [(c.file, c.scope, c.name, c.content_hash) for c in _scan(tmp_path, INLINE_SRC, prefix_lines=7)]
    assert a == b


def test_update_registry_repairs_inline_ordinals_by_content_hash():
    """A new keyword set inserted above the others shifts every ordinal; the existing entries
    must follow their content, not their old position."""
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("f:kw1", "sha256:h1", id="CONST-001"),
        _entry("f:kw2", "sha256:h2", id="CONST-002", status="unverified")]}
    added, updated, removed = ac.update_registry(reg, [
        _info("f:kw1", "sha256:h0"), _info("f:kw2", "sha256:h1"), _info("f:kw3", "sha256:h2")])
    assert (added, removed) == (1, 0)
    by_id = {c["id"]: c for c in reg["constants"]}
    assert by_id["CONST-001"]["name"] == "f:kw2" and by_id["CONST-001"]["status"] == "verified"
    assert by_id["CONST-002"]["name"] == "f:kw3"
    assert {c["name"] for c in reg["constants"]} == {"f:kw1", "f:kw2", "f:kw3"}


def test_update_registry_upgrades_legacy_line_named_inline_entries():
    reg = {"version": 2, "last_scan": None, "constants": [_entry("f:628", "sha256:h1")]}
    added, updated, removed = ac.update_registry(reg, [_info("f:kw1", "sha256:h1")])
    assert (added, removed) == (0, 0)
    c = reg["constants"][0]
    assert c["name"] == "f:kw1" and c["status"] == "verified" and c["id"] == "CONST-001"


def test_update_registry_inline_repair_stays_inside_the_function():
    """Same keyword tuple in two functions: each entry pairs with its own function's set."""
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("f:300", "sha256:h1", scope="f", id="CONST-001"),
        _entry("g:400", "sha256:h1", scope="g", id="CONST-002", status="unverified")]}
    ac.update_registry(reg, [_info("f:kw1", "sha256:h1", scope="f"), _info("g:kw1", "sha256:h1", scope="g")])
    by_id = {c["id"]: c for c in reg["constants"]}
    assert (by_id["CONST-001"]["scope"], by_id["CONST-001"]["status"]) == ("f", "verified")
    assert (by_id["CONST-002"]["scope"], by_id["CONST-002"]["status"]) == ("g", "unverified")


def test_relocate_renames_ordinal_synthetic_names_with_the_function():
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-020", "file": "a.py", "scope": "f", "function": "f", "name": "f:kw2",
         "status": "verified"}]}
    ac.relocate_registry(reg, [{"symbol": "a.f", "old_owner": "a.py", "new_owner": "b.py", "new_name": "g"}])
    c = reg["constants"][0]
    assert (c["file"], c["scope"], c["function"], c["name"]) == ("b.py", "g", "g", "g:kw2")


# --- non-literal constants -----------------------------------------------------------------

def test_non_literal_hash_is_structural_not_positional(tmp_path):
    a = [c for c in _scan(tmp_path, DICT_SRC) if c.name == "reg"][0]
    b = [c for c in _scan(tmp_path, DICT_SRC, prefix_lines=5) if c.name == "reg"][0]
    assert a.content_hash == b.content_hash
    assert a.content_hash.startswith("sha256:node_")


def test_non_literal_hash_changes_when_the_structure_changes(tmp_path):
    a = [c for c in _scan(tmp_path, DICT_SRC) if c.name == "reg"][0]
    b = [c for c in _scan(tmp_path, DICT_SRC.replace('"c": z', '"c": w')) if c.name == "reg"][0]
    assert a.content_hash != b.content_hash


def test_update_registry_keeps_verified_across_the_ast_hash_format_upgrade():
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("reg", "sha256:ast_1741", type="dict")]}
    ac.update_registry(reg, [_info("reg", "sha256:node_0123456789abcdef", const_type="dict")])
    c = reg["constants"][0]
    assert c["status"] == "verified" and c["content_hash"] == "sha256:node_0123456789abcdef"


def test_update_registry_structural_hash_change_still_goes_stale():
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("reg", "sha256:node_aaaaaaaaaaaaaaaa", type="dict")]}
    ac.update_registry(reg, [_info("reg", "sha256:node_bbbbbbbbbbbbbbbb", const_type="dict")])
    assert reg["constants"][0]["status"] == "stale"


def test_update_registry_structural_hash_never_carries_across_files():
    """Non-literal constants keep the no-carry rule the line hash had: same name and structure
    in another file is not evidence of the same constant."""
    reg = {"version": 2, "last_scan": None, "constants": [
        {"id": "CONST-139", "file": "a.py", "scope": "f", "name": "reg_info", "line": 1,
         "end_line": 1, "type": "dict", "entry_count": 3, "content_hash": "sha256:node_0123456789abcdef",
         "status": "verified", "source": "s", "notes": None, "verified_entries": 0}]}
    info = ac.ConstantInfo(name="reg_info", file="b.py", line=1, scope="g", const_type="dict",
                           entry_count=3, content_hash="sha256:node_0123456789abcdef")
    added, updated, removed = ac.update_registry(reg, [info])
    assert (added, removed) == (1, 1)
    assert reg["constants"][0]["status"] == "unverified"


def test_update_registry_pairs_identical_inline_sets_in_order():
    """Two identical keyword tuples in one function cannot be told apart by hash; pair them
    by position so the one-time rename keeps both ids."""
    reg = {"version": 2, "last_scan": None, "constants": [
        _entry("f:300", "sha256:h1", id="CONST-001", line=300),
        _entry("f:310", "sha256:h1", id="CONST-002", line=310, status="unverified")]}
    added, updated, removed = ac.update_registry(reg, [
        _info("f:kw1", "sha256:h1", line=3), _info("f:kw2", "sha256:h1", line=13)])
    assert (added, removed) == (0, 0)
    by_id = {c["id"]: c for c in reg["constants"]}
    assert (by_id["CONST-001"]["name"], by_id["CONST-001"]["status"]) == ("f:kw1", "verified")
    assert by_id["CONST-002"]["name"] == "f:kw2"
