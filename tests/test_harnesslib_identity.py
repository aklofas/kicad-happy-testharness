# tests/test_harnesslib_identity.py
"""harnesslib.identity: run identity, manifest, unit log (H0-1, report A3/A6)."""
TIER = "unit"

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnesslib import identity as ident  # noqa: E402


def _git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "wt"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c",
                    "user.name=t", "commit", "-q", "--allow-empty", "-m", "x"],
                   check=True)
    return repo


def _spec(repo: Path, **over) -> ident.RunSpec:
    ref = ident.git_worktree_ref(repo)
    kw = dict(kind="gate", profile="standard", harness=ref, baseline=ref,
              candidate=ref, argv=("--cross-section", "smoke"),
              selection_source="cross_section:smoke",
              unit_ids=("o/r/a.kicad_sch", "o/r/b.kicad_pcb"),
              normalization_policy="volatile-leaves-v1",
              env=(("PYTHONHASHSEED", "0"),))
    kw.update(over)
    return ident.RunSpec(**kw)


def test_git_worktree_ref_reports_sha_and_dirty(tmp_path):
    repo = _git_repo(tmp_path)
    ref = ident.git_worktree_ref(repo)
    assert len(ref.sha) == 40 and ref.path == str(repo.resolve())
    assert ref.dirty is False
    (repo / "junk.txt").write_text("x")
    assert ident.git_worktree_ref(repo).dirty is True


def test_sha256_file_and_digests_are_stable(tmp_path):
    f = tmp_path / "in.txt"
    f.write_bytes(b"abc")
    assert ident.sha256_file(f) == hashlib.sha256(b"abc").hexdigest()
    d1 = ident.selection_digest(["b/x", "a/y"])
    d2 = ident.selection_digest(["a/y", "b/x"])
    assert d1 == d2 == hashlib.sha256("a/y\nb/x".encode()).hexdigest()
    i1 = ident.input_digest([("u2", "ff"), ("u1", "aa")])
    assert i1 == hashlib.sha256("u1\taa\nu2\tff".encode()).hexdigest()


def test_identity_key_excludes_resume_and_includes_shas(tmp_path):
    repo = _git_repo(tmp_path)
    spec = _spec(repo, argv=("--cross-section", "smoke", "--resume"))
    key = ident.identity_key(spec)
    assert "--resume" not in key["argv"]
    assert key["baseline_sha"] == key["candidate_sha"] == spec.candidate.sha
    assert key["selection_digest"] == ident.selection_digest(spec.unit_ids)
    assert set(key) == {"kind", "profile", "harness_sha", "baseline_sha",
                        "candidate_sha", "argv", "selection_source",
                        "selection_digest", "normalization_policy", "env"}


def test_manifest_roundtrip_and_match(tmp_path):
    repo = _git_repo(tmp_path)
    spec = _spec(repo)
    root = tmp_path / "gate"
    p = ident.write_manifest(root, spec, run_id="r1",
                             expected_census={"schematic": 1, "pcb": 1},
                             input_digest="deadbeef",
                             runtime={"python": "3.12"})
    assert p == root / "manifest.json"
    m = ident.read_manifest(root)
    assert m["manifest_version"] == 1 and m["run_id"] == "r1"
    assert m["product"]["candidate"]["sha"] == spec.candidate.sha
    assert m["selection"]["unit_count"] == 2
    assert m["finished_at"] is None and m["totals"] is None
    ident.finish_manifest(root, {"PASS": 2})
    m2 = ident.read_manifest(root)
    assert m2["totals"] == {"PASS": 2} and m2["finished_at"]
    ok, reasons = ident.manifests_match(m, m2)
    assert ok and reasons == []
    other = ident.write_manifest(tmp_path / "g2", _spec(repo, profile="long-tail"),
                                 run_id="r2", expected_census={}, input_digest="x",
                                 runtime={})
    ok, reasons = ident.manifests_match(m, ident.read_manifest(tmp_path / "g2"))
    assert not ok and reasons == ["profile: standard != long-tail"]


def test_unit_log_append_iter_by_unit_latest_wins(tmp_path):
    log = ident.UnitLog(tmp_path)
    log.append({"analyzer": "pcb", "unit_id": "o/r/b.kicad_pcb", "status": "timeout"})
    log.append({"analyzer": "pcb", "unit_id": "o/r/b.kicad_pcb", "status": "ok"})
    assert [r["status"] for r in log] == ["timeout", "ok"]
    assert log.by_unit()["pcb/o/r/b.kicad_pcb"]["status"] == "ok"
    assert (tmp_path / "units.jsonl").read_text().count("\n") == 2


def test_unit_is_current_requires_status_input_and_output_hash(tmp_path):
    out = tmp_path / "snap.json"
    out.write_text("{}")
    log = ident.UnitLog(tmp_path)
    rec = {"analyzer": "pcb", "unit_id": "u", "status": "ok",
           "input_sha256": "in1", "output_sha256": ident.sha256_file(out)}
    log.append(rec)
    assert ident.unit_is_current(log, "pcb", "u", "in1", out) is True
    assert ident.unit_is_current(log, "pcb", "u", "in2", out) is False
    out.write_text("{\"changed\": 1}")
    assert ident.unit_is_current(log, "pcb", "u", "in1", out) is False
    log.append(dict(rec, status="crash"))
    assert ident.unit_is_current(log, "pcb", "u", "in1", out) is False


def test_by_unit_is_cached_and_updated_on_append(tmp_path, monkeypatch):
    log = ident.UnitLog(tmp_path)
    log.append({"analyzer": "pcb", "unit_id": "u", "status": "ok"})
    calls = []
    orig = Path.read_text

    def counting(self, *a, **k):
        calls.append(self)
        return orig(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", counting)
    assert log.by_unit()["pcb/u"]["status"] == "ok"
    log.by_unit()
    log.append({"analyzer": "pcb", "unit_id": "u", "status": "crash"})
    assert log.by_unit()["pcb/u"]["status"] == "crash"
    assert len(calls) == 1


def test_unit_log_tolerates_torn_last_line_only(tmp_path, capsys):
    p = tmp_path / "units.jsonl"
    p.write_text('{"analyzer":"a","unit_id":"1"}\n{"analyzer":"a","unit_id":"2"}\n{"analyzer":"a","un')
    assert len(list(ident.UnitLog(tmp_path))) == 2
    assert "units.jsonl: ignoring torn trailing line" in capsys.readouterr().err
    p.write_text('{"analyzer":"a"\n{"analyzer":"a","unit_id":"2"}\n')
    import pytest
    with pytest.raises(json.JSONDecodeError):
        list(ident.UnitLog(tmp_path))


def test_manifests_match_refuses_dirty_and_malformed(tmp_path):
    import copy
    repo = _git_repo(tmp_path)
    ident.write_manifest(tmp_path / "g", _spec(repo), run_id="r", expected_census={},
                         input_digest="x", runtime={})
    m = ident.read_manifest(tmp_path / "g")
    d = copy.deepcopy(m)
    d["product"]["candidate"]["dirty"] = True
    assert ident.manifests_match(m, d) == (False, ["dirty worktree: candidate"])
    n = copy.deepcopy(m)
    del n["identity"]
    assert ident.manifests_match(m, n) == (False, ["missing identity block"])
    v = copy.deepcopy(m)
    v["manifest_version"] = 2
    assert ident.manifests_match(m, v) == (False, ["manifest_version mismatch"])


def test_append_after_torn_tail_truncates_fragment(tmp_path, capsys):
    p = tmp_path / "units.jsonl"
    p.write_text('{"analyzer":"a","unit_id":"1"}\n{"analyzer":"a","unit_id":"2"}\n{"analyzer":"a","un')
    log = ident.UnitLog(tmp_path)
    log.append({"analyzer": "a", "unit_id": "3"})
    assert [r["unit_id"] for r in ident.UnitLog(tmp_path)] == ["1", "2", "3"]
    assert capsys.readouterr().err.count("ignoring torn trailing line") == 1


def test_append_validates_keys_before_writing(tmp_path):
    import pytest
    log = ident.UnitLog(tmp_path)
    with pytest.raises(KeyError):
        log.append({"analyzer": "a"})
    assert not (tmp_path / "units.jsonl").exists()


def test_valid_json_without_newline_is_torn(tmp_path, capsys):
    p = tmp_path / "units.jsonl"
    p.write_text('{"analyzer":"a","unit_id":"1"}\n{"analyzer":"a","unit_id":"2"}')
    assert [r["unit_id"] for r in ident.UnitLog(tmp_path)] == ["1"]
    assert "ignoring torn trailing line" in capsys.readouterr().err
    log = ident.UnitLog(tmp_path)
    log.append({"analyzer": "a", "unit_id": "3"})
    assert [r["unit_id"] for r in ident.UnitLog(tmp_path)] == ["1", "3"]


def test_append_is_tail_only_fast(tmp_path):
    import time
    log = ident.UnitLog(tmp_path)
    t = time.monotonic()
    for i in range(2000):
        log.append({"analyzer": "a", "unit_id": str(i), "pad": "x" * 200})
    assert time.monotonic() - t < 2
    assert len(log.by_unit()) == 2000
