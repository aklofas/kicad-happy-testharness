"""run_distributor_offline_gate: the distributor-offline profile runner (v3 round 6).

Two tiny git repos stand in for the product clones; a fake oracle honours the real one's
`--product/--all/--fixtures/--expected/--write-expected` contract by emitting the body of
`skills/x/scripts/cli.py` as its single artefact, so a baseline whose CLI differs from the
candidate's frozen set is the regression the runner must catch."""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regression import run_distributor_offline_gate as do  # noqa: E402
from regression import run_corpus_gate as gate  # noqa: E402

FAKE_ORACLE = r'''import argparse, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--product"); ap.add_argument("--all", action="store_true"); ap.add_argument("--fixtures")
ap.add_argument("--expected"); ap.add_argument("--write-expected")
a = ap.parse_args()
body = (Path(a.product) / "skills" / "x" / "scripts" / "cli.py").read_text()
if a.write_expected:
    d = Path(a.write_expected) / "p" / "run"; d.mkdir(parents=True)
    (d / "stdout.txt").write_text(body)
    print("wrote 1 runs to", a.write_expected)
else:
    ok = (Path(a.expected) / "p" / "run" / "stdout.txt").read_text() == body
    print("sync-offline: OK (1 runs)" if ok else "sync-offline: FAIL (1 runs)")
    sys.exit(0 if ok else 1)
'''


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _commit(repo, msg):
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


def _product(tmp_path, name, cli_body, *, oracle_body=None):
    """A product repo: commit 1 = the CLI; commit 2 (optional) = the oracle + frozen set."""
    repo = tmp_path / name
    (repo / "skills" / "x" / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    (repo / "skills" / "x" / "scripts" / "cli.py").write_text(cli_body)
    base = _commit(repo, "base")
    oracle = None
    if oracle_body is not None:
        exp = repo / do.EXPECTED / "p" / "run"
        exp.mkdir(parents=True)
        (exp / "stdout.txt").write_text(oracle_body)
        (repo / do.ORACLE).write_text(FAKE_ORACLE)
        oracle = _commit(repo, "oracle")
    return repo, base, oracle


def test_compare_dirs_reports_missing_and_different(tmp_path):
    e, a = tmp_path / "e", tmp_path / "a"
    for d in (e, a):
        (d / "p").mkdir(parents=True)
    (e / "p" / "same.txt").write_text("x"); (a / "p" / "same.txt").write_text("x")
    (e / "p" / "diff.txt").write_text("x"); (a / "p" / "diff.txt").write_text("y")
    (e / "p" / "only_e.txt").write_text("x")
    (a / "p" / "only_a.txt").write_text("x")
    assert do.compare_dirs(e, a) == ["p/diff.txt", "p/only_a.txt", "p/only_e.txt"]
    assert do.compare_dirs(e, tmp_path / "missing") == ["p/diff.txt", "p/only_e.txt", "p/same.txt"]


def test_git_archive_exports_a_revision_and_overlays_paths(tmp_path):
    repo, base, oracle = _product(tmp_path, "repo", "v1\n", oracle_body="v1\n")
    dest = tmp_path / "dest"
    do.git_archive(repo, base, dest)
    assert (dest / "skills/x/scripts/cli.py").read_text() == "v1\n"
    assert not (dest / do.ORACLE).exists()
    do.git_archive(repo, oracle, dest, (do.ORACLE, do.FIXTURES))
    assert (dest / do.ORACLE).read_text() == FAKE_ORACLE
    assert (dest / do.EXPECTED / "p/run/stdout.txt").read_text() == "v1\n"
    assert (dest / "skills/x/scripts/cli.py").read_text() == "v1\n"  # overlay kept the export


def test_gate_pass_needs_both_directions_and_no_diffs():
    ok, bad = {"exit_code": 0}, {"exit_code": 1}
    assert do.gate_pass(ok, ok, [])
    assert not do.gate_pass(bad, ok, []) and not do.gate_pass(ok, bad, [])
    assert not do.gate_pass(ok, {"exit_code": None}, []) and not do.gate_pass(ok, ok, ["p/run/stdout.txt"])


def test_main_passes_when_baseline_reproduces_the_frozen_set(tmp_path, capsys):
    base_repo, _, _ = _product(tmp_path, "base", "v1\n")
    cand_repo, _, oracle_rev = _product(tmp_path, "cand", "v1\n", oracle_body="v1\n")
    gate_dir = tmp_path / "g"
    rc = do.main(["--baseline-dir", str(base_repo), "--candidate-dir", str(cand_repo),
                  "--runner-rev", oracle_rev, "--gate-dir", str(gate_dir), "--label", "t",
                  "--fixtures", str(tmp_path)])
    assert rc == 0, capsys.readouterr()
    rec = json.loads((gate_dir / "distributor_offline.json").read_text())
    assert rec["profile"] == "distributor-offline" and rec["gate_pass"]["pass"] is True
    assert rec["candidate"]["exit_code"] == 0 and rec["candidate"]["summary"] == "sync-offline: OK (1 runs)"
    assert rec["baseline"]["exit_code"] == 0 and rec["baseline"]["runner_sha"] == oracle_rev
    assert rec["diffs"] == [] and rec["expected_artefacts"] == 1
    assert (gate_dir / "baseline_expected/p/run/stdout.txt").read_text() == "v1\n"
    assert (gate_dir / "candidate.stdout.txt").exists() and (gate_dir / "baseline.stderr.txt").exists()
    # the clones were never written to
    assert _git(base_repo, "status", "--porcelain") == "" and _git(cand_repo, "status", "--porcelain") == ""
    assert "gate_pass: PASS" in capsys.readouterr().out


def test_main_accepts_relative_dirs(tmp_path, monkeypatch, capsys):
    """The oracle runs with cwd=<exported tree>, so a relative --gate-dir must be resolved
    before it is joined into the oracle path (round-6 first run: exit 2, file not found)."""
    base_repo, _, _ = _product(tmp_path, "base", "v1\n")
    cand_repo, _, oracle_rev = _product(tmp_path, "cand", "v1\n", oracle_body="v1\n")
    monkeypatch.chdir(tmp_path)
    rc = do.main(["--baseline-dir", "base", "--candidate-dir", "cand", "--runner-rev", oracle_rev,
                  "--gate-dir", "g", "--fixtures", "."])
    assert rc == 0, capsys.readouterr()
    rec = json.loads((tmp_path / "g" / "distributor_offline.json").read_text())
    assert rec["gate_pass"]["pass"] is True and rec["baseline"]["exit_code"] == 0


def test_main_fails_when_the_baseline_diverges(tmp_path, capsys):
    base_repo, _, _ = _product(tmp_path, "base", "v0\n")
    cand_repo, _, oracle_rev = _product(tmp_path, "cand", "v1\n", oracle_body="v1\n")
    gate_dir = tmp_path / "g"
    rc = do.main(["--baseline-dir", str(base_repo), "--candidate-dir", str(cand_repo),
                  "--runner-rev", oracle_rev, "--gate-dir", str(gate_dir), "--fixtures", str(tmp_path)])
    assert rc == 1
    rec = json.loads((gate_dir / "distributor_offline.json").read_text())
    assert rec["gate_pass"]["pass"] is False and rec["diffs"] == ["p/run/stdout.txt"]
    assert rec["candidate"]["exit_code"] == 0 and rec["baseline"]["exit_code"] == 0
    assert "differs: p/run/stdout.txt" in capsys.readouterr().out


def test_main_refuses_a_non_empty_gate_dir(tmp_path, capsys):
    gate_dir = tmp_path / "g"
    gate_dir.mkdir()
    (gate_dir / "stale").write_text("")
    rc = do.main(["--baseline-dir", str(tmp_path), "--candidate-dir", str(tmp_path),
                  "--runner-rev", "HEAD", "--gate-dir", str(gate_dir)])
    assert rc == 2 and "not empty" in capsys.readouterr().err


@pytest.mark.parametrize("profile", ["distributor-offline", "spice-offline"])
def test_corpus_gate_refuses_profiles_without_corpus_analyzers(tmp_path, profile, capsys):
    with pytest.raises(SystemExit) as e:
        gate.main(["--baseline-dir", str(tmp_path / "nope"), "--candidate-dir", str(tmp_path / "nope"),
                   "--gate-dir", str(tmp_path / "g"), "--all", "--profile", profile])
    assert e.value.code == 2
    assert "runs no corpus analyzer" in capsys.readouterr().err
    assert not (tmp_path / "g").exists()
