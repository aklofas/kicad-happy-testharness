"""C1 on real chained envelopes: one project's schematic/pcb/emc/thermal/cross_analysis
units copied byte-identical from results/v22x_pr44_gate (see the fixture README). Only
the chained snaps' recorded absolute slot paths are rewritten to the tmp slot roots, so
the upstream sha256 values they carry stay valid."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from regression.field_compare import Policy, compare_trees, load_policy, run_modes

pytestmark = pytest.mark.unit

CHAINED = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "real" / "chained"
PROJECT = "0Prashant/Kicad/BAsanta_maga"
SCH = f"schematic/{PROJECT}.sch"
CHAINED_ANALYZERS = ("emc", "thermal", "cross_analysis")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _chained_snaps(slot: Path):
    return [slot / an / f"{PROJECT}.sch" / "snap.json" for an in CHAINED_ANALYZERS]


def _stage(tmp_path) -> Path:
    gate = tmp_path / "gate"
    shutil.copytree(CHAINED, gate, ignore=shutil.ignore_patterns("README.md"))
    for slot in ("baseline", "candidate"):
        root = gate / slot
        for snap in _chained_snaps(root):
            text = snap.read_text(encoding="utf-8")
            recorded = json.loads(text)["inputs"]["upstream_artifacts"]["schematic"]["path"]
            old_root = recorded[: -len(f"/{SCH}/snap.json")]
            snap.write_text(text.replace(old_root + "/", str(root) + "/"), encoding="utf-8")
    return gate


def _policy_without_verify() -> Policy:
    pol = load_policy("volatile-leaves-v1")
    leaves = [{k: v for k, v in lf.items() if k != "verify_values"} for lf in copy.deepcopy(pol.leaves)]
    return Policy(name="no-verify", leaves=leaves, root_prefixes_from_manifest=True)


def test_staged_upstream_hashes_are_valid(tmp_path):
    gate = _stage(tmp_path)
    for slot in ("baseline", "candidate"):
        for snap in _chained_snaps(gate / slot):
            hashes = json.loads(snap.read_text())["inputs"]["source_hashes"]
            assert len(hashes) == 2
            for key, value in hashes.items():
                assert key.startswith(str(gate / slot) + "/") and _sha(Path(key)) == value


def test_real_chained_pair_is_strict_clean(tmp_path):
    gate = _stage(tmp_path)
    rep = compare_trees(gate / "baseline", gate / "candidate", mode="strict", policy=load_policy("volatile-leaves-v1"))
    assert rep["policy_violations"] == []
    assert rep["verdict"] == "clean", rep["deltas"]
    assert rep["summary"]["compared"] == 5
    m = run_modes(gate)
    assert m["strict"]["verdict"] == "clean" and m["strict_field_clean"] is True
    assert m["raw"]["verdict"] == "deltas" and m["raw"]["summary"]["run_id_differs"] == 5


def test_real_chained_pair_without_verify_reproduces_c1(tmp_path):
    """Control: stripping the keys alone leaves every chained unit with two source_hashes deltas."""
    gate = _stage(tmp_path)
    rep = compare_trees(gate / "baseline", gate / "candidate", mode="strict", policy=_policy_without_verify())
    assert rep["policy_violations"] == []
    assert {(d["analyzer"], d["path"]) for d in rep["deltas"]} == {
        (an, f"/inputs/source_hashes/~1{up}~1{PROJECT.replace('/', '~1')}.{ext}~1snap.json")
        for an in CHAINED_ANALYZERS for up, ext in (("schematic", "sch"), ("pcb", "kicad_pcb"))}


def test_tampered_upstream_is_a_policy_violation(tmp_path):
    gate = _stage(tmp_path)
    up = gate / "candidate" / SCH / "snap.json"
    up.write_bytes(up.read_bytes() + b"\n")          # parsed-equal, bytes (and sha256) differ
    rep = compare_trees(gate / "baseline", gate / "candidate", mode="strict", policy=load_policy("volatile-leaves-v1"))
    assert rep["verdict"] == "error"
    key = f"/inputs/source_hashes/~1schematic~1{PROJECT.replace('/', '~1')}.sch~1snap.json"
    for an in CHAINED_ANALYZERS:
        unit = f"{an}/{PROJECT}.sch"
        assert f"{unit} {key}: verify_values sha256_of_key: mismatch on side b" in rep["policy_violations"]
    # the unverified value is not masked: it also surfaces as a delta
    assert sum(d["path"] == key for d in rep["deltas"]) == 3


def test_repo_keyed_source_hash_change_stays_a_delta(tmp_path):
    gate = _stage(tmp_path)
    up = gate / "candidate" / SCH / "snap.json"
    old_sha = _sha(up)
    doc = json.loads(up.read_text())
    (repo_key, repo_val), = doc["inputs"]["source_hashes"].items()
    doc["inputs"]["source_hashes"][repo_key] = "f" * 64
    up.write_text(json.dumps(doc, indent=2))
    new_sha = _sha(up)
    for snap in _chained_snaps(gate / "candidate"):   # as if the chained analyzers re-read the new upstream
        snap.write_text(snap.read_text().replace(old_sha, new_sha))
    rep = compare_trees(gate / "baseline", gate / "candidate", mode="strict", policy=load_policy("volatile-leaves-v1"))
    assert rep["policy_violations"] == []
    assert [(d["unit"], d["op"], d["before"], d["after"]) for d in rep["deltas"]] == [
        (SCH, "changed", repo_val, "f" * 64)]
    assert rep["deltas"][0]["path"].startswith("/inputs/source_hashes/")
