"""Contract tests for Phase 4 hard invariants HI-1 (immutability),
HI-3 (strip recovers baseline), HI-5 (finding_id determinism)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

import pytest




def _fixture_sch():
    fx = HARNESS_ROOT / "tests" / "fixtures" / "simple-project"
    candidates = list(fx.glob("*.kicad_sch"))
    if not candidates:
        pytest.skip("simple-project fixture missing")
    return candidates[0]


def _run_schematic(out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["python3", "skills/kicad/scripts/analyze_schematic.py",
         str(_fixture_sch()), "--output", str(out_path)],
        check=True, cwd=MAIN_REPO_ROOT,
    )
    return json.loads(out_path.read_text())


def test_hi5_finding_id_deterministic_across_runs(tmp_path):
    """HI-5: re-running same analyzer on same inputs produces identical finding_id set.

    Only findings that carry finding_id are compared — schematic findings that
    bypass make_finding() (tracked as v1.5 carry-over) are excluded by filter.
    """
    out1 = tmp_path / "a" / "schematic.json"
    out2 = tmp_path / "b" / "schematic.json"
    data1 = _run_schematic(out1)
    data2 = _run_schematic(out2)
    ids1 = sorted(f["finding_id"] for f in data1.get("findings", []) if "finding_id" in f)
    ids2 = sorted(f["finding_id"] for f in data2.get("findings", []) if "finding_id" in f)
    # At least one make_finding()-produced finding must be present in the fixture.
    assert ids1, "No findings with finding_id found — fixture may have changed"
    assert ids1 == ids2


def test_hi5_finding_id_nonempty_on_every_finding(tmp_path):
    """HI-5: every finding that carries finding_id has a non-empty, well-formed value.

    Note: in v1.4 4a, only findings produced via make_finding() carry finding_id.
    Findings from pcb/thermal/emc and legacy schematic paths (tracked as v1.5
    carry-over) may lack finding_id — this test asserts quality only for those
    findings that do carry the field.
    """
    data = _run_schematic(tmp_path / "schematic.json")
    findings_with_id = [f for f in data.get("findings", []) if "finding_id" in f]
    assert findings_with_id, "No make_finding()-produced findings found in fixture"
    for f in findings_with_id:
        assert f["finding_id"], f"Empty finding_id on {f.get('rule_id')}"
        assert ":" in f["finding_id"], f"finding_id lacks ':' separator: {f['finding_id']!r}"


def test_hi3_strip_recovers_baseline_when_no_overlays(tmp_path):
    """HI-3 smoke: stripping a finding-set with no llm_* yields identical bytes."""
    from finding_schema import strip_llm_overlays
    data = _run_schematic(tmp_path / "schematic.json")
    stripped = strip_llm_overlays(data)
    assert stripped == data  # no llm_* fields present yet


def test_hi1_make_finding_returns_independent_lists():
    """HI-1: make_finding doesn't share component/net/pin list state with caller.

    Mutating the caller's list after make_finding returns must not affect the
    finding's components/nets/pins.
    """
    from finding_schema import make_finding
    caller_components = ["U1"]
    f = make_finding(
        detector="t", rule_id="HI1-T", category="test",
        summary="t", description="t",
        severity="warning", confidence="heuristic", evidence_source="topology",
        components=caller_components, source="sch",
    )
    # Mutate the caller's list AFTER make_finding returned.
    caller_components.append("U2")
    # The finding's components must NOT reflect the post-call mutation.
    assert f.get("components") == ["U1"], (
        "HI-1 violation: make_finding aliased the caller's list — "
        "mutating it post-construction changed the finding")


def test_hi1_make_finding_returns_independent_nets_list():
    """HI-1: make_finding doesn't share nets list state with caller.

    Companion to test_hi1_make_finding_returns_independent_lists; covers
    the nets field separately to guard against future regressions on the
    list() copy fix in finding_schema.make_finding.
    """
    from finding_schema import make_finding
    caller_nets = ["VCC"]
    f = make_finding(
        detector="t", rule_id="HI1-T", category="test",
        summary="t", description="t",
        severity="warning", confidence="heuristic", evidence_source="topology",
        nets=caller_nets, source="sch",
    )
    caller_nets.append("GND")
    assert f["nets"] == ["VCC"], "HI-1 violation: nets list aliased"
