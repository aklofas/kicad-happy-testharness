# tests/test_field_compare_masking.py
import copy
import hashlib
import json
from pathlib import Path

import pytest

from regression.field_compare import Policy, compare_strict, load_policy

pytestmark = pytest.mark.unit

U = dict(unit="thermal/o/r/k", analyzer="thermal")
RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"
ROOT = Path(__file__).resolve().parent.parent


def _doc(run_id, elapsed=0.0, extra=None):
    d = {"analyzer_type": "thermal",
         "inputs": {"run_id": run_id, "source_files": ["/ROOT/repos/o/r/x.kicad_sch"],
                    "source_hashes": {"/ROOT/repos/o/r/x.kicad_sch": "ab"}},
         "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
         "elapsed_s": elapsed, "findings": []}
    if extra:
        d.update(extra)
    return d


def _policy(leaves, **kw):
    return Policy(name="t", leaves=leaves, **kw)


def test_exact_leaf_masked_and_shape_checked():
    pol = _policy([{"pointer": "/inputs/run_id", "shape": "run_id"},
                   {"pointer": "/capability_mode_ref/run_id", "shape": "run_id", "equals": "/inputs/run_id"},
                   {"pointer": "/elapsed_s", "shape": "number"}])
    deltas, viol = compare_strict(_doc(RUN_A, 0.1), _doc(RUN_B, 0.3), pol, **U)
    assert deltas == [] and viol == []


def test_shape_mismatch_is_violation_but_still_masked():
    pol = _policy([{"pointer": "/inputs/run_id", "shape": "run_id"}])
    deltas, viol = compare_strict(_doc("not-a-run-id"), _doc(RUN_B), pol, **U)
    assert [d.path for d in deltas] == ["/capability_mode_ref/run_id"]   # unlisted, so unmasked
    assert len(viol) == 1 and "/inputs/run_id" in viol[0] and "side a" in viol[0] and "shape" in viol[0]
    deltas, viol = compare_strict(_doc(RUN_A), _doc("bad"), pol, **U)
    assert len(viol) == 1 and "side b" in viol[0]


def test_equals_linkage_violation():
    pol = _policy([{"pointer": "/inputs/run_id", "shape": "run_id"},
                   {"pointer": "/capability_mode_ref/run_id", "shape": "run_id", "equals": "/inputs/run_id"}])
    a = _doc(RUN_A)
    a["capability_mode_ref"]["run_id"] = RUN_B      # mismatch within side a
    deltas, viol = compare_strict(a, _doc(RUN_B), pol, **U)
    assert any("equals /inputs/run_id" in v and "side a" in v for v in viol)
    assert not any("side b" in v for v in viol)


def test_policy_pointer_on_container_is_violation():
    pol = _policy([{"pointer": "/inputs"}])
    a, b = _doc(RUN_A), _doc(RUN_B)
    deltas, viol = compare_strict(a, b, pol, **U)
    assert any("whole-block masking refused" in v for v in viol)
    assert any(d.path == "/inputs/run_id" for d in deltas)


def test_container_on_one_side_only_is_refused():
    pol = _policy([{"pointer": "/elapsed_s"}])
    a, b = _doc(RUN_A), _doc(RUN_A)
    b["elapsed_s"] = {"x": 1}
    deltas, viol = compare_strict(a, b, pol, **U)
    assert any("whole-block masking refused" in v for v in viol)
    assert [d.op for d in deltas] == ["type_changed"]


def test_leaf_absent_on_both_sides_is_fine():
    pol = _policy([{"pointer": "/elapsed_s", "shape": "number"}])
    a, b = _doc(RUN_A), _doc(RUN_A)
    del a["elapsed_s"]; del b["elapsed_s"]
    deltas, viol = compare_strict(a, b, pol, **U)
    assert deltas == [] and viol == []


def test_leaf_present_on_one_side_is_a_real_delta():
    pol = _policy([{"pointer": "/elapsed_s", "shape": "number"}])
    a, b = _doc(RUN_A), _doc(RUN_A)
    del b["elapsed_s"]
    deltas, viol = compare_strict(a, b, pol, **U)
    assert [(d.op, d.path) for d in deltas] == [("removed", "/elapsed_s")]
    assert viol == []


def test_number_shape_rejects_bool_and_string():
    pol = _policy([{"pointer": "/elapsed_s", "shape": "number"}])
    deltas, viol = compare_strict(_doc(RUN_A, True), _doc(RUN_A, "1"), pol, **U)
    assert len(viol) == 2


def test_unmasked_fields_still_compare():
    pol = _policy([{"pointer": "/inputs/run_id", "shape": "run_id"},
                   {"pointer": "/capability_mode_ref/run_id", "shape": "run_id"}])
    a, b = _doc(RUN_A), _doc(RUN_B)
    b["findings"] = [{"x": 1}]
    deltas, viol = compare_strict(a, b, pol, **U)
    assert [(d.op, d.path) for d in deltas] == [("added", "/findings/0")]


def test_strip_root_prefix_on_string_leaf_and_dict_keys():
    pol = _policy([{"pointer_glob": "/inputs/source_files/*", "rewrite": "strip_root_prefix"},
                   {"pointer": "/inputs/source_hashes", "rewrite": "strip_root_prefix_keys"}])
    a = _doc(RUN_A); b = _doc(RUN_A)
    b["inputs"]["source_files"] = ["/OTHER/repos/o/r/x.kicad_sch"]
    b["inputs"]["source_hashes"] = {"/OTHER/repos/o/r/x.kicad_sch": "ab"}
    deltas, viol = compare_strict(a, b, pol, root_prefixes=("/ROOT", "/OTHER"), **U)
    assert deltas == [] and viol == []
    # without prefixes the paths really differ
    deltas, _ = compare_strict(a, b, pol, **U)
    assert {d.path for d in deltas} == {"/inputs/source_files/0",
                                        "/inputs/source_hashes/~1ROOT~1repos~1o~1r~1x.kicad_sch",
                                        "/inputs/source_hashes/~1OTHER~1repos~1o~1r~1x.kicad_sch"}


def test_strip_root_prefix_does_not_mutate_inputs():
    pol = _policy([{"pointer_glob": "/inputs/source_files/*", "rewrite": "strip_root_prefix"}])
    a, b = _doc(RUN_A), _doc(RUN_A)
    snap = copy.deepcopy(a)
    compare_strict(a, b, pol, root_prefixes=("/ROOT", "/ROOT"), **U)
    assert a == snap


def test_strip_keys_needs_dict():
    pol = _policy([{"pointer": "/elapsed_s", "rewrite": "strip_root_prefix_keys"}])
    deltas, viol = compare_strict(_doc(RUN_A), _doc(RUN_A), pol, root_prefixes=("/R", "/R"), **U)
    assert any("needs a dict" in v for v in viol)


def test_policy_root_prefixes_used_when_no_kwarg():
    pol = _policy([{"pointer_glob": "/inputs/source_files/*", "rewrite": "strip_root_prefix"}],
                  root_prefixes=["/ROOT", "/OTHER"])
    a, b = _doc(RUN_A), _doc(RUN_A)
    b["inputs"]["source_files"] = ["/OTHER/repos/o/r/x.kicad_sch"]
    deltas, viol = compare_strict(a, b, pol, **U)
    assert deltas == [] and viol == []


def test_manifest_prefixes_required_but_not_supplied():
    pol = _policy([{"pointer_glob": "/inputs/source_files/*", "rewrite": "strip_root_prefix"}],
                  root_prefixes_from_manifest=True)
    deltas, viol = compare_strict(_doc(RUN_A), _doc(RUN_A), pol, **U)
    assert any("root prefixes required but not supplied" in v for v in viol)
    deltas, viol = compare_strict(_doc(RUN_A), _doc(RUN_A), pol, root_prefixes=("/ROOT", "/ROOT"), **U)
    assert viol == []


def test_sha256_of_linkage(tmp_path):
    up_a = tmp_path / "a_up.json"; up_a.write_text('{"x": 1}')
    up_b = tmp_path / "b_up.json"; up_b.write_text('{"x": 2}')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    pol = _policy([{"pointer_glob": "/inputs/upstream_artifacts/*/path", "rewrite": "strip_root_prefix"},
                   {"pointer_glob": "/inputs/upstream_artifacts/*/sha256", "shape": "^[0-9a-f]{64}$", "sha256_of": "path"}])
    a = _doc(RUN_A, extra={}); b = _doc(RUN_A, extra={})
    a["inputs"]["upstream_artifacts"] = {"schematic": {"path": str(up_a), "sha256": sha(up_a)}}
    b["inputs"]["upstream_artifacts"] = {"schematic": {"path": str(up_b), "sha256": sha(up_b)}}
    rp = (str(up_a.parent) + "/a_", str(up_b.parent) + "/b_")
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, **U)
    assert deltas == [] and viol == []
    b["inputs"]["upstream_artifacts"]["schematic"]["sha256"] = "0" * 64
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, **U)
    assert any("sha256_of" in v and "side b" in v for v in viol)
    assert not any("side a" in v for v in viol)


def test_sha256_of_missing_file(tmp_path):
    pol = _policy([{"pointer_glob": "/inputs/upstream_artifacts/*/sha256", "sha256_of": "path"}])
    a, b = _doc(RUN_A), _doc(RUN_A)
    for d in (a, b):
        d["inputs"]["upstream_artifacts"] = {"s": {"path": str(tmp_path / "nope"), "sha256": "0" * 64}}
    deltas, viol = compare_strict(a, b, pol, **U)
    assert sum("linked file missing" in v for v in viol) == 2


def test_glob_matches_exactly_one_segment():
    pol = _policy([{"pointer_glob": "/inputs/upstream_artifacts/*/run_id", "shape": "run_id"}])
    a = _doc(RUN_A); b = _doc(RUN_A)
    a["inputs"]["upstream_artifacts"] = {"schematic": {"run_id": RUN_A}, "pcb": {"nested": {"run_id": RUN_A}}}
    b["inputs"]["upstream_artifacts"] = {"schematic": {"run_id": RUN_B}, "pcb": {"nested": {"run_id": RUN_B}}}
    deltas, viol = compare_strict(a, b, pol, **U)
    assert [d.path for d in deltas] == ["/inputs/upstream_artifacts/pcb/nested/run_id"]


@pytest.mark.corpus
def test_real_policy_on_real_envelope(tmp_path):
    src = ROOT / "results/v22x_pr44_gate/v14/schematic/JustinHsu845/PiEDB-Y15/USBTTL_USBTTL.kicad_sch/snap.json"
    if not src.exists():
        pytest.skip("corpus snap not present")
    a = json.loads(src.read_text())
    (tmp_path / "snap.json").write_text(json.dumps(a))      # tmp copy, source untouched
    b = json.loads((tmp_path / "snap.json").read_text())
    b["inputs"]["run_id"] = RUN_B
    b["capability_mode_ref"]["run_id"] = RUN_B
    pol = load_policy("volatile-leaves-v1")
    rp = (str(ROOT), str(ROOT))
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, unit="schematic/x", analyzer="schematic")
    assert deltas == [] and viol == []
    b["capability_mode_ref"]["run_id"] = "20260101T000000Z-000000"
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, unit="schematic/x", analyzer="schematic")
    assert any("equals /inputs/run_id" in v and "side b" in v for v in viol)
