"""TH-099: the chained runners pair a schematic only with a PCB output that a current pcb
manifest unit writes, and tools/retire_orphan_outputs.py quarantines pcb/gerber outputs that
map to no manifest unit (dry-run by default).

Subprocesses always run with KICAD_HAPPY_TESTHARNESS_DATA_DIR = tmp_path and a fake repo
selector, so a misrouted path can never reach the live tree."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "run"))
import utils  # noqa: E402
from run_thermal import find_thermal_pairs  # noqa: E402

pytestmark = pytest.mark.unit

REPO = "th099-owner/th099-repo"


@pytest.fixture
def data(tmp_path, monkeypatch):
    root = tmp_path / "data"
    monkeypatch.setattr(utils, "REPOS_DIR", root / "repos")
    monkeypatch.setattr(utils, "OUTPUTS_DIR", root / "results" / "outputs")
    monkeypatch.setattr(utils, "MANIFESTS_DIR", root / "results" / "manifests")
    return root


def _manifest(root, kind, inputs):
    d = root / "results" / "manifests" / REPO
    d.mkdir(parents=True, exist_ok=True)
    (d / {"schematic": "schematics.txt", "pcb": "pcbs.txt", "gerber": "gerbers.txt"}[kind]
     ).write_text("".join(f"{p}\n" for p in inputs), encoding="utf-8")
    glob = root / "results" / "manifests" / {"schematic": "all_schematics.txt",
                                             "pcb": "all_pcbs.txt", "gerber": "all_gerbers.txt"}[kind]
    glob.write_text("".join(f"{p}\n" for p in inputs), encoding="utf-8")


def _output(root, kind, name, payload=None):
    d = root / "results" / "outputs" / kind / REPO
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(json.dumps(payload if payload is not None else {"analyzer_type": kind}))
    return p


def _live_untouched():
    for kind in ("schematic", "pcb", "gerber", "emc", "thermal"):
        assert not (HARNESS / "results" / "outputs" / kind / REPO).exists()


def test_pcb_output_outside_the_manifest_does_not_pair(data):
    sch_in = data / "repos" / REPO / "board.kicad_sch"
    _manifest(data, "schematic", [sch_in])
    _manifest(data, "pcb", [])                      # the board's pcb left the corpus
    sch = _output(data, "schematic", "board.kicad_sch.json")
    _output(data, "pcb", "board.kicad_pcb.json")    # its old output is still on disk
    assert utils.find_pcb_output(sch) is None
    assert find_thermal_pairs(REPO) == []


def test_pcb_output_in_the_manifest_pairs(data):
    sch_in = data / "repos" / REPO / "board.kicad_sch"
    _manifest(data, "schematic", [sch_in])
    _manifest(data, "pcb", [sch_in.with_suffix(".kicad_pcb")])
    sch = _output(data, "schematic", "board.kicad_sch.json")
    pcb = _output(data, "pcb", "board.kicad_pcb.json")
    assert utils.find_pcb_output(sch) == pcb


def test_pre_hash_pcb_name_is_not_paired(data):
    """The corpus case: the schematic's flat name fits the cap, the PCB's does not, so the
    current PCB output is hash-named and the name swap lands on the pre-hash leftover."""
    stem = "d/" * 58 + "Raspberry Pi Zero W"
    sch_in = data / "repos" / REPO / f"{stem}.sch"
    pcb_in = data / "repos" / REPO / f"{stem}.kicad_pcb"
    sch_name = utils.safe_name(str(sch_in)) + ".json"
    assert sch_name.endswith(".sch.json")
    assert not utils.safe_name(str(pcb_in)).endswith(".kicad_pcb")
    _manifest(data, "schematic", [sch_in])
    _manifest(data, "pcb", [pcb_in])
    sch = _output(data, "schematic", sch_name)
    orphan = _output(data, "pcb", sch_name.replace(".sch.json", ".kicad_pcb.json"))
    _output(data, "pcb", utils.safe_name(str(pcb_in)) + ".json")
    assert utils.find_pcb_output(sch) != orphan


def test_truncated_schematic_pairs_only_with_a_manifest_pcb(data):
    deep = "very_long_directory_name_" * 8
    sch_in = data / "repos" / REPO / deep / "board.kicad_sch"
    sch_name = utils.safe_name(str(sch_in)) + ".json"
    pcb_name = utils.safe_name(str(sch_in.with_suffix(".kicad_pcb"))) + ".json"
    assert not sch_name.endswith(".kicad_sch.json")
    _manifest(data, "schematic", [sch_in])
    _manifest(data, "pcb", [])
    sch = _output(data, "schematic", sch_name)
    _output(data, "pcb", pcb_name)
    assert utils.find_pcb_output(sch) is None


FAKE_EMC = (
    "import json, sys\n"
    "a = sys.argv[1:]\n"
    "pcb = a[a.index('--pcb') + 1] if '--pcb' in a else None\n"
    "json.dump({'analyzer_type': 'emc', 'findings': [], 'summary': {}, 'pcb_arg': pcb},\n"
    "          open(a[a.index('--output') + 1], 'w'))\n")


def test_run_emc_does_not_pass_an_orphan_pcb(tmp_path):
    root = tmp_path / "data"
    sch_in = root / "repos" / REPO / "board.kicad_sch"
    _manifest(root, "schematic", [sch_in])
    _manifest(root, "pcb", [])
    _output(root, "schematic", "board.kicad_sch.json", {"analyzer_type": "schematic"})
    _output(root, "pcb", "board.kicad_pcb.json")
    prod = tmp_path / "product"
    (prod / "skills" / "emc" / "scripts").mkdir(parents=True)
    (prod / "skills" / "emc" / "scripts" / "analyze_emc.py").write_text(FAKE_EMC)
    for git_args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        # the run manifest records the product SHA
        subprocess.run(["git", "-C", str(prod), "-c", "user.email=t@t", "-c", "user.name=t",
                        *git_args], check=True, capture_output=True)
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(root), KICAD_HAPPY_DIR=str(prod))
    r = subprocess.run([sys.executable, str(HARNESS / "run" / "run_emc.py"), "--repo", REPO,
                        "--jobs", "1"], env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    out = json.loads((root / "results" / "outputs" / "emc" / REPO / "board.kicad_sch.json").read_text())
    assert out["pcb_arg"] is None
    assert "(0 with PCB)" in r.stdout
    _live_untouched()


def _retire(root, *args):
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(root))
    return subprocess.run([sys.executable, str(HARNESS / "tools" / "retire_orphan_outputs.py"),
                           *args], env=env, capture_output=True, text=True, timeout=60)


def _retire_fixture(tmp_path):
    root = tmp_path / "data"
    repo_dir = root / "repos" / REPO
    _manifest(root, "pcb", [repo_dir / "board.kicad_pcb"])
    _manifest(root, "gerber", [repo_dir])          # a root-level gerber set writes ".json"
    keep = [_output(root, "pcb", "board.kicad_pcb.json"), _output(root, "gerber", ".json")]
    orphans = [_output(root, "pcb", "old name.kicad_pcb.json"), _output(root, "gerber", "gerbers.json")]
    side = []
    for kind in ("pcb", "gerber"):
        d = root / "results" / "outputs" / kind / REPO
        for n in ("_timing.json", "capability_mode.json", "old name.kicad_pcb.err"):
            (d / n).write_text("{}")
            side.append(d / n)
    return root, keep, orphans, side


def _tree(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def test_retire_dry_run_lists_and_renames_nothing(tmp_path):
    root, keep, orphans, side = _retire_fixture(tmp_path)
    before = _tree(root)
    r = _retire(root, "--repo", REPO)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _tree(root) == before
    listed = sorted(l for l in r.stdout.splitlines() if l.startswith("WOULD RETIRE "))
    assert listed == sorted(f"WOULD RETIRE {o.parent.parent.parent.name} {REPO}/{o.name}"
                            for o in orphans)
    assert "dry run: 2 output(s)" in r.stdout
    _live_untouched()


def test_retire_apply_quarantines_only_orphans(tmp_path):
    root, keep, orphans, side = _retire_fixture(tmp_path)
    r = _retire(root, "--repo", REPO, "--apply")
    assert r.returncode == 0, r.stdout + r.stderr
    for o in orphans:
        assert not o.exists() and o.with_name(o.name + ".stale").exists()
    assert all(p.exists() for p in keep + side)
    assert len([p for p in root.rglob("*.stale")]) == len(orphans)
    _live_untouched()


def test_retire_refuses_without_a_manifest(tmp_path):
    root, keep, orphans, side = _retire_fixture(tmp_path)
    (root / "results" / "manifests" / "all_pcbs.txt").unlink()
    before = _tree(root)
    r = _retire(root, "--repo", REPO, "--apply")
    assert r.returncode == 2
    assert _tree(root) == before
    _live_untouched()


def test_retire_needs_a_selector(tmp_path):
    root, *_ = _retire_fixture(tmp_path)
    r = _retire(root, "--apply")
    assert r.returncode == 2
    assert not list(root.rglob("*.stale"))
