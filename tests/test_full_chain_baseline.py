import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from regression import full_chain_baseline as fc  # noqa: E402

pytestmark = pytest.mark.unit


def _mk_manifest(tmp_path, triples):
    repos = tmp_path / "trees"
    man = tmp_path / "manifests" / "x"
    man.mkdir(parents=True)
    lines = []
    for owner, repo, stem, complete in triples:
        d = repos / owner / repo
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{stem}.kicad_pcb").write_text("(kicad_pcb)")
        if complete:
            (d / f"{stem}.kicad_sch").write_text("(kicad_sch)")
            (d / f"{stem}.kicad_pro").write_text("{}")
        lines.append(str(d / f"{stem}.kicad_pcb"))
    (man / "pcbs.txt").write_text("\n".join(lines) + "\n")
    return tmp_path / "manifests", repos


def test_sample_projects_only_complete_triples_and_deterministic(tmp_path):
    manifests, _ = _mk_manifest(tmp_path, [("o", "a", "x", True), ("o", "b", "y", False), ("o", "c", "z", True)])
    s1, pop = fc.sample_projects(5, 23, manifests)
    s2, _ = fc.sample_projects(5, 23, manifests)
    assert pop == 2 and len(s1) == 2 and s1 == s2
    assert all(p.suffix == ".kicad_pcb" for p in s1)


def test_sample_projects_seed_changes_selection(tmp_path):
    manifests, _ = _mk_manifest(tmp_path, [("o", f"r{i}", "p", True) for i in range(20)])
    a, _ = fc.sample_projects(5, 1, manifests)
    b, _ = fc.sample_projects(5, 1, manifests)
    c, _ = fc.sample_projects(5, 2, manifests)
    assert a == b and a != c


def test_chain_steps_order_and_flags(tmp_path):
    steps = fc.chain_steps(tmp_path / "trees/o/a/x.kicad_pcb", tmp_path / "kh", tmp_path / "out")
    names = [n for n, _ in steps]
    assert names == ["schematic", "pcb", "emc", "thermal"]
    pcb_cmd = dict(steps)["pcb"]
    assert "--full" in pcb_cmd and "--proximity" in pcb_cmd
    assert dict(steps)["schematic"][1].endswith("skills/kicad/scripts/analyze_schematic.py")
    assert "--no-hierarchy" not in dict(steps)["schematic"]


def test_sides_default_to_baseline_only(tmp_path):
    assert fc.sides_for(base="/a", cand=None) == [("baseline", "/a")]
    assert fc.sides_for(base="/a", cand="/b") == [("baseline", "/a"), ("candidate", "/b")]
