import json
from pathlib import Path

import pytest

from regression.field_compare import Policy, PolicyError, load_policy, POLICY_DIR


def test_tracked_policy_loads_and_names_itself():
    p = load_policy("volatile-leaves-v1")
    assert isinstance(p, Policy)
    assert p.name == "volatile-leaves-v1"
    pointers = {leaf.get("pointer") or leaf.get("pointer_glob") for leaf in p.leaves}
    # the two leaves that differ on an identical-code pair (see plan "Reality check")
    assert "/inputs/run_id" in pointers
    assert "/capability_mode_ref/run_id" in pointers
    # the spec's wrong guesses must NOT be in the tracked policy
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


def test_pointer_must_be_absolute_rfc6901(tmp_path):
    (tmp_path / "p.json").write_text(json.dumps({
        "name": "p", "leaves": [{"pointer": "inputs/run_id"}]}))
    with pytest.raises(PolicyError, match="must start with"):
        load_policy("p", policy_dir=tmp_path)
