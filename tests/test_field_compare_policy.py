import json
from pathlib import Path

import pytest

from regression.field_compare import Policy, PolicyError, load_policy, POLICY_DIR


def test_tracked_policy_loads_and_names_itself():
    p = load_policy("volatile-leaves-v1")
    assert isinstance(p, Policy)
    assert p.name == "volatile-leaves-v1"
    pointers = {leaf.get("pointer") or leaf.get("pointer_glob") for leaf in p.leaves}
    # both run-id leaves vary across identical-code runs
    assert "/inputs/run_id" in pointers
    assert "/capability_mode_ref/run_id" in pointers
    # unlisted top-level run_id/generated_at fields must remain comparable
    assert "/run_id" not in pointers
    assert "/inputs/generated_at" not in pointers


def test_policy_dir_is_tracked_location():
    assert POLICY_DIR == Path(__file__).resolve().parents[1] / "regression" / "normalization"
    assert (POLICY_DIR / "volatile-leaves-v1.json").exists()


def test_unknown_policy_name_raises(tmp_path):
    with pytest.raises(PolicyError, match="no-such-policy"):
        load_policy("no-such-policy", policy_dir=tmp_path)


def test_policy_name_must_match_file(tmp_path):
    (tmp_path / "x.json").write_text(json.dumps({"name": "y", "leaves": []}))
    with pytest.raises(PolicyError, match="name"):
        load_policy("x", policy_dir=tmp_path)


def test_leaf_needs_exactly_one_pointer_form(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({
        "name": "p", "leaves": [{"pointer": "/a", "pointer_glob": "/b/*"}]}))
    with pytest.raises(PolicyError, match="exactly one"):
        load_policy("p", policy_dir=tmp_path)


def test_leaf_rejects_unknown_keys_and_rewrites(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({
        "name": "p", "leaves": [{"pointer": "/a", "rewrite": "drop_block"}]}))
    with pytest.raises(PolicyError, match="rewrite"):
        load_policy("p", policy_dir=tmp_path)
    (tmp_path / "q.json").write_text(json.dumps({
        "name": "q", "leaves": [{"pointer": "/a", "mask_subtree": True}]}))
    with pytest.raises(PolicyError, match="unknown key"):
        load_policy("q", policy_dir=tmp_path)


def _bad(tmp_path, doc, match):
    (tmp_path / "p.json").write_text(json.dumps(doc) if not isinstance(doc, str) else doc)
    with pytest.raises(PolicyError, match=match):
        load_policy("p", policy_dir=tmp_path)


def test_pointer_must_be_absolute_rfc6901(tmp_path):
    _bad(tmp_path, {"name": "p", "leaves": [{"pointer": "inputs/run_id"}]}, "must start with")


@pytest.mark.parametrize("ptr", ["/a~2b", "/a~"])
def test_pointer_bad_tilde_escape(tmp_path, ptr):
    _bad(tmp_path, {"name": "p", "leaves": [{"pointer": ptr}]}, "~")


def test_glob_allows_star_and_valid_escapes(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({
        "name": "p", "leaves": [{"pointer_glob": "/a/*/b~0~1"}]}))
    assert load_policy("p", policy_dir=tmp_path).name == "p"
    _bad(tmp_path, {"name": "p", "leaves": [{"pointer": "/a/*/b~2"}]}, "~")


@pytest.mark.parametrize("doc", [
    [1, 2], {"name": 5, "leaves": []}, {"name": "p", "leaves": {}},
    {"name": "p", "leaves": ["x"]},
    {"name": "p", "leaves": [{"pointer": "/a", "shape": 3}]},
    {"name": "p", "leaves": [{"pointer": "/a", "rewrite": 3}]},
    {"name": "p", "leaves": [{"pointer": "/a", "equals": 3}]},
    {"name": "p", "leaves": [{"pointer": "/a", "shape": "(["}]},
])
def test_malformed_policy_raises_policy_error(tmp_path, doc):
    _bad(tmp_path, doc, ".")


def test_bad_shape_regex_message(tmp_path):
    _bad(tmp_path, {"name": "p", "leaves": [{"pointer": "/a", "shape": "(["}]}, "bad shape regex at /a")


def test_root_prefixes_forms(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({"name": "p", "leaves": [], "root_prefixes": "from_manifest"}))
    p = load_policy("p", policy_dir=tmp_path)
    assert p.root_prefixes == [] and p.root_prefixes_from_manifest is True
    (tmp_path / "p.json").write_text(json.dumps({"name": "p", "leaves": [], "root_prefixes": ["/x"]}))
    p = load_policy("p", policy_dir=tmp_path)
    assert p.root_prefixes == ["/x"] and p.root_prefixes_from_manifest is False
    for bad in ("other", 5, [1]):
        _bad(tmp_path, {"name": "p", "leaves": [], "root_prefixes": bad}, "root_prefixes")


def test_tracked_policy_notes():
    p = load_policy("volatile-leaves-v1")
    assert p.root_prefixes_from_manifest is True
    el = [l for l in p.leaves if l.get("pointer") == "/elapsed_s"][0]
    assert el["note"] == "cross_analysis/emc/thermal only"


def test_verify_values_validated(tmp_path):
    ok = {"pointer": "/inputs/source_hashes", "rewrite": "strip_root_prefix_keys", "verify_values": "sha256_of_key"}
    (tmp_path / "p.json").write_text(json.dumps({"name": "p", "leaves": [ok]}))
    assert load_policy("p", policy_dir=tmp_path).leaves == [ok]
    _bad(tmp_path, {"name": "p", "leaves": [dict(ok, verify_values="md5")]}, "verify_values must be one of")
    _bad(tmp_path, {"name": "p", "leaves": [dict(ok, rewrite="strip_root_prefix")]},
         "verify_values requires rewrite strip_root_prefix_keys")
    _bad(tmp_path, {"name": "p", "leaves": [{"pointer": "/x", "verify_values": "sha256_of_key"}]},
         "verify_values requires rewrite strip_root_prefix_keys")
