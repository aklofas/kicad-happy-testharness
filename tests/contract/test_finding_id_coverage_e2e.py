"""Regression: every finding in real analyzer output carries a finding_id.

Layer 2 review matches annotations to findings by finding_id
(``merge_annotations._find_finding``). Before SKILL_FEEDBACK-2's
``finding_schema.assign_finding_ids`` serialization pass, only findings built
through ``make_finding`` (~1 of 11 on the fixture) had a finding_id, so the
merge matched almost nothing — a silent no-op. The synthetic envelopes in
``test_merge_annotations.py`` always set finding_id, so they never caught it.

These tests assert the contract against REAL analyzer output:
  * 100% finding_id COVERAGE per analyzer (the pre-F3 code fails this), and
  * distinct-object uniqueness of the id assignment, tested in-memory on
    ``assign_finding_ids`` (serialization breaks object aliasing, so it can
    only be checked before the envelope is written to disk — see below).

See ``test_layer2_merge_e2e.py`` for the producer→merge path itself.
"""

from tests.contract._paths import MAIN_REPO_ROOT
from tests.contract.conftest import ANALYZER_STEMS

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from finding_schema import assign_finding_ids


@pytest.fixture(scope="session")
def envelopes(analysis_dir):
    return {stem: json.loads((analysis_dir / f"{stem}.json").read_text())
            for stem in ANALYZER_STEMS}


# --------------------------------------------------------------------------
# Coverage — real serialized analyzer output
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stem", ANALYZER_STEMS)
def test_every_finding_has_finding_id(envelopes, stem):
    findings = envelopes[stem].get("findings", [])
    missing = [i for i, f in enumerate(findings) if not f.get("finding_id")]
    assert not missing, (
        f"{stem}: {len(missing)}/{len(findings)} findings missing finding_id "
        f"(indices {missing[:10]}) — assign_finding_ids did not cover them")


def test_coverage_is_not_vacuous(envelopes):
    """Guard against the parametrized coverage tests passing vacuously: the
    schematic analyzer must emit findings on the fixture, all with ids. If
    assign_finding_ids regressed to the pre-F3 ~1/11 coverage this fails
    loudly instead of the empty-list checks silently passing."""
    sch = envelopes["schematic"].get("findings", [])
    assert len(sch) > 0, "fixture schematic produced no findings"
    assert all(f.get("finding_id") for f in sch)


# --------------------------------------------------------------------------
# Uniqueness — in-memory contract on assign_finding_ids
# --------------------------------------------------------------------------
# NOT value-uniqueness over the serialized list: a couple of detectors append
# the SAME finding object twice (a pre-existing aliasing quirk, e.g. VD-DET
# feedback_networks). assign_finding_ids gives that single object one id, so
# the serialized list legitimately contains that id twice. After json.loads
# those become two distinct dicts, making object identity unrecoverable from
# disk. The uniqueness contract is therefore exercised here, in-memory.

def test_distinct_colliding_objects_get_distinct_ids():
    """Two DIFFERENT findings deriving the same base id must not collide —
    the second is disambiguated with a ``#N`` suffix."""
    f1 = {"rule_id": "VM-001", "components": ["U1"], "summary": "first"}
    f2 = {"rule_id": "VM-001", "components": ["U1"], "summary": "second"}
    assign_finding_ids([f1, f2], source="schematic")
    assert f1["finding_id"] == "schematic:VM-001:u1"
    assert f2["finding_id"] == "schematic:VM-001:u1#1"
    assert f1["finding_id"] != f2["finding_id"]


def test_aliased_object_keeps_single_id():
    """The SAME object appearing twice keeps one id — it is NOT bumped to a
    spurious ``#1`` (the quirk assign_finding_ids deliberately tolerates)."""
    g = {"rule_id": "AM-001", "components": ["U2"], "summary": "aliased"}
    findings = [g, g]
    assign_finding_ids(findings, source="schematic")
    assert findings[0] is findings[1]
    assert g["finding_id"] == "schematic:AM-001:u2"
    assert "#" not in g["finding_id"]


def test_distinct_object_uniqueness_invariant():
    """General invariant: across a findings list, no two DISTINCT objects
    share a finding_id (aliased duplicates of one object are exempt)."""
    a = {"rule_id": "VM-001", "components": ["U1"], "summary": "a"}
    b = {"rule_id": "VM-001", "components": ["U1"], "summary": "b"}  # collides w/ a
    c = {"rule_id": "EP-001", "nets": ["VCC"], "summary": "c"}
    findings = [a, b, c, a]  # `a` aliased twice
    assign_finding_ids(findings, source="schematic")

    by_obj = {id(f): f["finding_id"] for f in findings}  # one entry per object
    ids = list(by_obj.values())
    assert len(set(ids)) == len(ids), (
        f"distinct objects share a finding_id: {ids}")
    assert len(by_obj) == 3  # a, b, c — the second `a` collapses by identity
