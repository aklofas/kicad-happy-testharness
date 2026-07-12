"""deep_review.json schema + finding-id derivation contract (v2.0 spec 3.C)."""
import copy
import json
import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))
import _mini_jsonschema  # noqa: E402
import finding_schema  # noqa: E402

SCHEMA_PATH = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "schemas"
               / "deep_review.schema.json")
FIXTURE_PATH = (MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "fixtures"
                / "deep_review.example.json")


def _schema():
    return json.loads(SCHEMA_PATH.read_text())


def _fixture():
    return json.loads(FIXTURE_PATH.read_text())


def test_fixture_validates_and_schema_within_mini_subset():
    # iter_errors raises on unsupported keywords, so a clean pass also
    # proves the schema stays inside the _mini_jsonschema subset.
    _mini_jsonschema.validate(_fixture(), _schema())


def test_missing_evidence_is_a_schema_error():
    doc = _fixture()
    del doc["findings"][0]["evidence"]
    errors = list(_mini_jsonschema.iter_errors(doc, _schema()))
    assert errors, "evidence must be required on findings"


def test_derive_id_stable_and_prefixed():
    f = _fixture()["findings"][0]
    fid1 = finding_schema.derive_deep_review_id(f)
    fid2 = finding_schema.derive_deep_review_id(copy.deepcopy(f))
    assert fid1 == fid2
    assert fid1.startswith("deep_review:")


def test_derive_id_normalizes_anchors_but_not_rewording():
    f = _fixture()["findings"][0]
    lowered = copy.deepcopy(f)
    lowered["evidence"]["components"] = [c.lower() for c in f["evidence"]["components"]]
    assert (finding_schema.derive_deep_review_id(lowered)
            == finding_schema.derive_deep_review_id(f))
    reworded = copy.deepcopy(f)
    reworded["summary"] = "Inductor L2 at 220 nH sits under TPS61023's 470 nH floor"
    assert (finding_schema.derive_deep_review_id(reworded)
            != finding_schema.derive_deep_review_id(f))


def test_assign_ids_collision_suffix():
    f = _fixture()["findings"][0]
    pair = [copy.deepcopy(f), copy.deepcopy(f)]
    finding_schema.assign_deep_review_ids(pair)
    assert pair[0]["finding_id"] != pair[1]["finding_id"]
    assert pair[1]["finding_id"] == pair[0]["finding_id"] + "#1"
