"""Audit registries keep honest verification: a changed value drops its evidence, a parse
failure aborts instead of deleting records, every tag gets a hash, corpus scoring matches
full detector names and is idempotent (code A4-F2 A4-F7 A4-F8 A4-F12 A4-F13, arch O6 O7a)."""
import json
import sys
import textwrap
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "validate"))
import audit_constants as ac  # noqa: E402
import audit_equations as ae  # noqa: E402

pytestmark = pytest.mark.unit


def _src(tmp_path, text, name="m.py"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_changed_table_entry_value_drops_its_verification(tmp_path):
    reg = {"constants": []}
    p = _src(tmp_path, 'TABLE = {"a": 1.0, "b": 2.0, "c": 3.0}\n')
    ac.update_registry(reg, ac.scan_file(p, tmp_path))
    e = reg["constants"][0]
    for v in e["entries"].values():
        v.update(status="verified", source="datasheet")
    e.update(status="verified", verified_entries=3)
    _src(tmp_path, 'TABLE = {"a": 1.5, "b": 2.0, "c": 3.0}\n')
    ac.update_registry(reg, ac.scan_file(p, tmp_path))
    e = reg["constants"][0]
    assert e["entries"]["a"]["status"] == "stale" and e["entries"]["a"]["source"] is None
    assert e["entries"]["b"]["status"] == "verified" and e["entries"]["b"]["source"] == "datasheet"
    assert e["status"] != "verified" and e["verified_entries"] == 2
    assert ac.verified_fraction(e) < 1.0


def test_constants_parse_failure_raises_not_empty(tmp_path):
    with pytest.raises(ac.ScanError):
        ac.scan_file(_src(tmp_path, "def broken(:\n"), tmp_path)


def test_constants_scan_with_a_broken_file_does_not_save(tmp_path, monkeypatch):
    scripts = tmp_path / "skills" / "x" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "ok.py").write_text("A = {'k': 1, 'j': 2, 'l': 3}\n")
    (scripts / "bad.py").write_text("def broken(:\n")
    monkeypatch.setattr(ac, "resolve_kicad_happy_dir", lambda: tmp_path)
    monkeypatch.setattr(ac, "load_registry", lambda: {"constants": []})
    monkeypatch.setattr(ac, "save_registry", lambda r: pytest.fail("registry saved after a parse failure"))
    with pytest.raises(SystemExit) as ex:
        ac.cmd_scan(type("A", (), {"diff": False})())
    assert ex.value.code == 2


def test_equation_parse_failure_raises(tmp_path):
    with pytest.raises(ae.ScanError):
        ae.scan_file(_src(tmp_path, "# EQ-001: x = y\ndef broken(:\n"), product_root=tmp_path)


def test_equation_tags_outside_functions_get_a_hash(tmp_path):
    p = _src(tmp_path, """
        # EQ-001: f = 1 / (2 pi R C)
        CUTOFF = 1 / (2 * 3.14159 * 1e3 * 1e-6)

        class Table:
            # EQ-002: z = sqrt(L / C)
            Z0 = (1e-9 / 1e-12) ** 0.5
        """)
    eqs = {e["id"]: e for e in ae.scan_file(p, product_root=tmp_path)}
    assert eqs["EQ-001"]["content_hash"] and eqs["EQ-002"]["content_hash"]
    _src(tmp_path, """
        # EQ-001: f = 1 / (2 pi R C)
        CUTOFF = 1 / (2 * 3.14159 * 2e3 * 1e-6)

        class Table:
            # EQ-002: z = sqrt(L / C)
            Z0 = (1e-9 / 1e-12) ** 0.5
        """)
    eqs2 = {e["id"]: e for e in ae.scan_file(p, product_root=tmp_path)}
    assert eqs2["EQ-001"]["content_hash"] != eqs["EQ-001"]["content_hash"]
    assert eqs2["EQ-002"]["content_hash"] == eqs["EQ-002"]["content_hash"]


def test_verified_equation_without_a_hash_goes_stale_once_hashed():
    reg = {"equations": [{"id": "EQ-099", "file": "m.py", "line": 1, "function": None, "formula": "x",
                          "content_hash": None, "status": "verified", "sources": []}]}
    scanned = [{"id": "EQ-099", "file": "m.py", "line": 1, "function": None, "formula": "x",
                "content_hash": "sha256:abc", "sources": []}]
    ae.update_registry(reg, scanned)
    assert reg["equations"][0]["status"] == "stale"


def test_equation_scan_diff_reports_changes(tmp_path, monkeypatch, capsys):
    """arch O7a: --diff compared against the registry it had just saved, so it printed nothing."""
    old = [{"id": "EQ-001", "file": "m.py", "line": 1, "function": "f", "formula": "x",
            "content_hash": "sha256:old", "status": "verified", "sources": []}]
    new = [{"id": "EQ-001", "file": "m.py", "line": 1, "function": "f", "formula": "x",
            "content_hash": "sha256:new", "sources": []},
           {"id": "EQ-002", "file": "m.py", "line": 9, "function": "g", "formula": "y",
            "content_hash": "sha256:g", "sources": []}]
    store = {"r": {"equations": old}}
    monkeypatch.setattr(ae, "resolve_kicad_happy_dir", lambda: tmp_path)
    monkeypatch.setattr(ae, "iter_source_files", lambda root: [tmp_path / "m.py"])
    monkeypatch.setattr(ae, "scan_all", lambda: (new, []))
    monkeypatch.setattr(ae, "load_registry", lambda: json.loads(json.dumps(store["r"])))
    monkeypatch.setattr(ae, "save_registry", lambda r: store.update(r=r))
    ae.cmd_scan(type("A", (), {"diff": True})())
    err = capsys.readouterr().err
    assert "+ m.py:f (EQ-001)" in err and "+ m.py:g (EQ-002)" in err


def _corpus_run(monkeypatch, tmp_path, registry):
    out = tmp_path / "o.json"
    out.write_text(json.dumps({"findings": [{"detector": "detect_crystal_circuits"}], "components": []}))
    monkeypatch.setattr(ac, "load_registry", lambda: registry)
    monkeypatch.setattr(ac, "save_registry", lambda r: None)
    monkeypatch.setattr(ac, "_iter_schematic_outputs", lambda: iter([("o/r", out)]))
    ac.cmd_corpus(type("A", (), {})())


def test_corpus_hits_match_full_detector_names_and_rerun_is_idempotent(tmp_path, monkeypatch):
    entry = {"id": "CONST-1", "name": "_osc_keywords", "file": "m.py", "line": 1, "entry_count": 4,
             "overfit_score": 0.1, "overfit_flags": [], "impact_score": 0.2}
    zero = {"id": "CONST-2", "name": "_eth_net_re", "file": "m.py", "line": 2, "entry_count": 4,
            "overfit_score": 0.1, "overfit_flags": [], "impact_score": 0.2}
    reg = {"constants": [entry, zero]}
    _corpus_run(monkeypatch, tmp_path, reg)
    assert entry["corpus_hits"]["repos"] == 1          # was 0: "crystal_circuits" never met the full name
    assert "corpus_zero_hits" not in entry["overfit_flags"]
    assert zero["overfit_score"] == 0.6 and "corpus_zero_hits" in zero["overfit_flags"]
    for _ in range(2):
        _corpus_run(monkeypatch, tmp_path, reg)
    assert zero["overfit_score"] == 0.6                # was +0.5 per run, capped at 1.0
    assert zero["overfit_flags"].count("corpus_zero_hits") == 1
