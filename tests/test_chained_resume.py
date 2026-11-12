"""run_emc / run_thermal / run_spice write a run manifest + units.jsonl and resume by identity,
as run_batch does: a unit is reused only under the matched run, with its upstream outputs and
its own output unchanged since the record.

The runners' main() runs in-process against monkeypatched utils paths (all under tmp_path),
so the harness ref is a clean temp repo rather than this (possibly dirty) checkout.
"""
TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT, ROOT / "run"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import utils  # noqa: E402
import run_emc  # noqa: E402
import run_spice  # noqa: E402
import run_thermal  # noqa: E402

# Fakes log one line per call next to the product dir (outside it, so the product stays clean)
# and fail when FAKE_MODE=fail reaches them through the runner's env.
_FAKE_HEAD = (
    "import json, os, sys\n"
    "from pathlib import Path\n"
    "a = sys.argv[1:]\n"
    "with open(Path(__file__).resolve().parents[4] / 'calls.log', 'a') as fh:\n"
    "    fh.write(Path(__file__).name + chr(10))\n"
    "if os.environ.get('FAKE_MODE') == 'fail':\n"
    "    sys.exit(3)\n"
    "out = a[a.index('--output') + 1]\n")
FAKES = {
    "skills/emc/scripts/analyze_emc.py": _FAKE_HEAD + (
        "json.dump({'analyzer_type': 'emc', 'findings': [], 'summary': {'total_checks': 0}},"
        " open(out, 'w'))\n"),
    "skills/kicad/scripts/analyze_thermal.py": _FAKE_HEAD + (
        "json.dump({'analyzer_type': 'thermal', 'findings': [], 'summary': {'total_checks': 0}},"
        " open(out, 'w'))\n"),
    "skills/spice/scripts/simulate_subcircuits.py": _FAKE_HEAD + (
        "json.dump({'simulation_results': [], 'summary': {'total': 0}}, open(out, 'w'))\n"),
    "skills/spice/scripts/extract_parasitics.py": _FAKE_HEAD + "json.dump({}, open(out, 'w'))\n",
}

RUNNERS = {
    # name: (module, output root, output name, extra argv)
    "emc": (run_emc, "emc", "a.kicad_sch.json", []),
    "thermal": (run_thermal, "thermal", "a_thermal.json", []),
    "spice": (run_spice, "spice", "a.kicad_sch.json", []),
}


def _git(path, *args):
    subprocess.run(["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


def _commit_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q")
    _git(path, "commit", "-q", "--allow-empty", "-m", "x")


@pytest.fixture
def env(tmp_path, monkeypatch):
    product = tmp_path / "product"
    for rel, text in FAKES.items():
        (product / rel).parent.mkdir(parents=True, exist_ok=True)
        (product / rel).write_text(text)
    _commit_repo(product)
    _git(product, "add", "-A")
    _git(product, "commit", "-q", "-m", "fakes")
    harness = tmp_path / "harness"
    _commit_repo(harness)

    data = tmp_path / "data"
    outputs = data / "results" / "outputs"
    manifests = data / "results" / "manifests"
    repos = data / "repos"
    sch = outputs / "schematic" / "o" / "r" / "a.kicad_sch.json"
    sch.parent.mkdir(parents=True)
    sch.write_text(json.dumps({"analyzer_type": "schematic", "v": 1}))
    pcb = outputs / "pcb" / "o" / "r" / "a.kicad_pcb.json"
    pcb.parent.mkdir(parents=True)
    pcb.write_text(json.dumps({"analyzer_type": "pcb", "v": 1}))
    (manifests / "o" / "r").mkdir(parents=True)
    (manifests / "o" / "r" / "pcbs.txt").write_text(f"{repos / 'o' / 'r' / 'a.kicad_pcb'}\n")

    monkeypatch.setenv("KICAD_HAPPY_DIR", str(product))
    monkeypatch.setenv("NGSPICE_PATH", "/bin/true")
    monkeypatch.delenv("FAKE_MODE", raising=False)
    monkeypatch.setattr(utils, "HARNESS_DIR", harness)
    monkeypatch.setattr(utils, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(utils, "MANIFESTS_DIR", manifests)
    monkeypatch.setattr(utils, "REPOS_DIR", repos)
    for mod in (run_emc, run_thermal, run_spice):
        monkeypatch.setattr(mod, "OUTPUTS_DIR", outputs)
    return SimpleNamespace(tmp=tmp_path, product=product, outputs=outputs, sch=sch, pcb=pcb,
                           monkeypatch=monkeypatch)


def _run(env, name, *extra, resume=False):
    mod, _, _, base = RUNNERS[name]
    argv = ["--repo", "o/r", "--jobs", "1", *base, *extra] + (["--resume"] if resume else [])
    if name == "spice":
        argv += ["--workdir", str(env.tmp / "work")]
    with pytest.raises(SystemExit) as ei:
        mod.main(argv)
    return ei.value.code


def _calls(env):
    log = env.tmp / "calls.log"
    return len(log.read_text().splitlines()) if log.exists() else 0


def _root(env, name):
    return env.outputs / RUNNERS[name][1]


def _output(env, name):
    return _root(env, name) / "o" / "r" / RUNNERS[name][2]


def _records(env, name):
    p = _root(env, name) / "units.jsonl"
    return [json.loads(ln) for ln in p.read_text().splitlines()] if p.exists() else []


def _manifest(env, name):
    return json.loads((_root(env, name) / "manifest.json").read_text())


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_run_writes_manifest_and_unit_records(env, name, capsys):
    assert _run(env, name) == 0
    m = _manifest(env, name)
    assert m["kind"] == "batch" and m["selection"]["source"] == "repo:o/r"
    assert m["expected_census"] == {RUNNERS[name][1]: 1}
    assert m["totals"] == {"ok": 1, "skipped": 0}
    assert len(m["product"]["candidate"]["sha"]) == 40 and "--resume" not in m["argv"]
    recs = _records(env, name)
    assert len(recs) == 1 and recs[0]["status"] == "ok" and recs[0]["run_id"] == m["run_id"]
    assert recs[0]["analyzer"] == RUNNERS[name][1]
    assert recs[0]["unit_id"] == f"o/r/{RUNNERS[name][2]}"


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_resume_reuses_a_current_unit(env, name, capsys):
    assert _run(env, name) == 0
    before = _output(env, name).read_bytes()
    n = _calls(env)
    capsys.readouterr()
    assert _run(env, name, resume=True) == 0
    out = capsys.readouterr().out
    assert _calls(env) == n and "Skip:  1" in out
    assert _output(env, name).read_bytes() == before
    assert _manifest(env, name)["totals"] == {"skipped": 1}


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_resume_reruns_when_the_schematic_output_changed(env, name):
    _run(env, name)
    n = _calls(env)
    env.sch.write_text(json.dumps({"analyzer_type": "schematic", "v": 2}))
    assert _run(env, name, resume=True) == 0
    assert _calls(env) > n


@pytest.mark.parametrize("name", ["emc", "thermal"])
def test_resume_reruns_when_the_pcb_output_changed(env, name):
    _run(env, name)
    n = _calls(env)
    env.pcb.write_text(json.dumps({"analyzer_type": "pcb", "v": 2}))
    _run(env, name, resume=True)
    assert _calls(env) == n + 1


def test_emc_resume_reruns_when_the_pcb_pairing_appears(env):
    env.pcb.unlink()
    _run(env, "emc")
    n = _calls(env)
    env.pcb.write_text(json.dumps({"analyzer_type": "pcb", "v": 1}))
    _run(env, "emc", resume=True)
    assert _calls(env) == n + 1


def test_spice_without_parasitics_ignores_the_pcb_output(env):
    _run(env, "spice")
    n = _calls(env)
    env.pcb.write_text(json.dumps({"analyzer_type": "pcb", "v": 2}))
    _run(env, "spice", resume=True)
    assert _calls(env) == n


def test_spice_with_parasitics_reruns_when_the_pcb_output_changed(env):
    root = env.outputs / "spice-parasitics"
    assert _run(env, "spice", "--with-parasitics") == 0
    assert (root / "manifest.json").exists()
    n = _calls(env)
    _run(env, "spice", "--with-parasitics", resume=True)
    assert _calls(env) == n                                  # current: extractor + simulator skipped
    env.pcb.write_text(json.dumps({"analyzer_type": "pcb", "v": 2}))
    _run(env, "spice", "--with-parasitics", resume=True)
    assert _calls(env) == n + 2                              # extractor + simulator


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_resume_disabled_when_the_product_sha_changes(env, name, capsys):
    _run(env, name)
    n = _calls(env)
    _git(env.product, "commit", "-q", "--allow-empty", "-m", "y")
    capsys.readouterr()
    _run(env, name, resume=True)
    out = capsys.readouterr().out
    assert "resume disabled: candidate_sha" in out and _calls(env) == n + 1


def test_resume_disabled_when_the_args_change(env, capsys):
    _run(env, "emc")
    n = _calls(env)
    capsys.readouterr()
    _run(env, "emc", "--standard", "cispr-class-b", resume=True)
    out = capsys.readouterr().out
    assert "resume disabled: argv" in out and _calls(env) == n + 1


@pytest.mark.parametrize("name", sorted(RUNNERS))
@pytest.mark.parametrize("change", ["edit", "delete"])
def test_resume_reruns_when_the_output_was_edited_or_deleted(env, name, change):
    _run(env, name)
    n = _calls(env)
    out = _output(env, name)
    if change == "edit":
        out.write_text(out.read_text() + " ")
    else:
        out.unlink()
    _run(env, name, resume=True)
    assert _calls(env) == n + 1 and json.loads(out.read_text())


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_resume_reruns_a_unit_whose_record_failed(env, name):
    env.monkeypatch.setenv("FAKE_MODE", "fail")
    assert _run(env, name) == 1
    assert _records(env, name)[0]["status"] == "crash"          # exit 3, no output written
    assert _manifest(env, name)["totals"] == {"crash": 1, "skipped": 0}
    env.monkeypatch.delenv("FAKE_MODE")
    n = _calls(env)
    assert _run(env, name, resume=True) == 0
    assert _calls(env) == n + 1 and _records(env, name)[-1]["status"] == "ok"


def test_resume_reruns_when_the_record_run_id_is_not_the_manifests(env):
    """A record left by a different run (here: the manifest names another run) is never reused."""
    _run(env, "thermal")
    n = _calls(env)
    p = _root(env, "thermal") / "manifest.json"
    m = json.loads(p.read_text())
    m["run_id"] = "another-run"
    p.write_text(json.dumps(m))
    _run(env, "thermal", resume=True)
    assert _calls(env) == n + 1
    assert _records(env, "thermal")[-1]["run_id"] == "another-run" == _manifest(env, "thermal")["run_id"]


def test_non_resume_run_archives_the_old_log(env):
    _run(env, "emc")
    first = _manifest(env, "emc")["run_id"]
    _run(env, "emc")
    root = _root(env, "emc")
    archived = root / f"units.{first}.jsonl"
    assert archived.exists() and json.loads(archived.read_text())["run_id"] == first
    recs = _records(env, "emc")
    assert len(recs) == 1 and recs[0]["run_id"] == _manifest(env, "emc")["run_id"] != first


@pytest.mark.parametrize("name", sorted(RUNNERS))
def test_resume_without_a_prior_manifest_runs_everything(env, name, capsys):
    assert _run(env, name, resume=True) == 0
    out = capsys.readouterr().out
    assert "resume disabled: no prior manifest" in out and _calls(env) >= 1
    assert _records(env, name)[0]["status"] == "ok"


def test_parallel_run_logs_every_unit(tmp_path):
    """--jobs > 1: the records are appended in this process as the pool's units finish."""
    product = tmp_path / "product"
    script = product / "skills" / "emc" / "scripts" / "analyze_emc.py"
    script.parent.mkdir(parents=True)
    script.write_text(FAKES["skills/emc/scripts/analyze_emc.py"])
    _commit_repo(product)
    _git(product, "add", "-A")
    _git(product, "commit", "-q", "-m", "fake")
    data = tmp_path / "data"
    sch_dir = data / "results" / "outputs" / "schematic" / "o" / "r"
    sch_dir.mkdir(parents=True)
    for n in ("a", "b", "c"):
        (sch_dir / f"{n}.kicad_sch.json").write_text(json.dumps({"analyzer_type": "schematic"}))
    env = dict(os.environ, KICAD_HAPPY_TESTHARNESS_DATA_DIR=str(data), KICAD_HAPPY_DIR=str(product))
    r = subprocess.run([sys.executable, str(ROOT / "run" / "run_emc.py"), "--repo", "o/r",
                        "--jobs", "2"], env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    root = data / "results" / "outputs" / "emc"
    m = json.loads((root / "manifest.json").read_text())
    recs = [json.loads(ln) for ln in (root / "units.jsonl").read_text().splitlines()]
    assert sorted(x["unit_id"] for x in recs) == [f"o/r/{n}.kicad_sch.json" for n in "abc"]
    assert all(x["status"] == "ok" and x["run_id"] == m["run_id"] for x in recs)
    assert m["totals"] == {"ok": 3, "skipped": 0}


def test_harness_run_passes_resume_to_spice_and_emc(monkeypatch):
    import harness
    calls = []
    monkeypatch.setattr(harness, "_run", lambda cmd, desc, timeout=600: calls.append((desc, cmd)) or True)
    args = SimpleNamespace(smoke=False, cross_section=None, repo="o/r", all_repos=False, resume=True,
                           skip_spice=False, skip_emc=False, continue_on_error=False)
    assert harness.cmd_run(args) is True
    cmds = dict(calls)
    for desc in ("SPICE simulations", "EMC analysis", "Analyzer: run_schematic"):
        assert cmds[desc][-1] == "--resume", desc


def test_spice_offline_compare_ignores_the_run_manifest(tmp_path):
    from regression import compare_spice_offline
    for side, sha in (("a", "1" * 40), ("b", "2" * 40)):
        (tmp_path / side / "o" / "r").mkdir(parents=True)
        (tmp_path / side / "o" / "r" / "x.json").write_text('{"simulation_results": []}')
        (tmp_path / side / "manifest.json").write_text(json.dumps({"product": {"candidate": {"sha": sha}}}))
    rep = compare_spice_offline.compare(tmp_path / "a", tmp_path / "b")
    assert rep["files"]["a"] == 1 and not rep["differences"]
