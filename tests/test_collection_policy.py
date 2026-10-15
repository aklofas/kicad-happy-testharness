"""Root conftest.py marker derivation and default tier selection (B9, TH-053)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
TREE = HARNESS / "tests" / "fixtures" / "h0" / "plan1" / "sample_tree"


def _collect(*extra, quiet=True):
    env = {**os.environ, "KICAD_HAPPY_DIR": os.environ.get(
        "KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", *(["-q"] if quiet else []),
         "-p", "no:cacheprovider", str(TREE), *extra],
        capture_output=True, text=True, cwd=HARNESS, env=env)
    ids = [l for l in proc.stdout.splitlines() if "::" in l]
    return proc.returncode, ids, proc.stdout + proc.stderr


def test_default_selection_is_unit_and_offline_contract():
    rc, ids, out = _collect()
    names = {i.rsplit("::", 1)[1] for i in ids}
    assert names == {"test_unit_default", "test_cheap"}, out
    # -q suppresses the report header, so check it from a non-quiet run
    _, _, header = _collect(quiet=False)
    assert "default selection: unit or offline_contract" in header


def test_default_selection_excludes_online():
    _, ids, _ = _collect()
    assert not any("test_online_declared" in i for i in ids)


def test_explicit_marker_expression_overrides_default():
    _, ids, _ = _collect("-m", "online")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_online_declared"]
    _, ids, _ = _collect("-m", "corpus")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_corpus_marked"]
    _, ids, _ = _collect("-m", "perf")
    assert [i.rsplit("::", 1)[1] for i in ids] == ["test_slow_bound"]


def test_all_tiers_collects_everything():
    _, ids, _ = _collect("--all-tiers")
    assert len(ids) == 5


def test_unknown_marker_is_rejected():
    bad = HARNESS / "tests" / "fixtures" / "h0" / "plan1" / "bad_marker"
    bad.mkdir(parents=True, exist_ok=True)
    (bad / "test_typo.py").write_text(
        "import pytest\n@pytest.mark.uint\ndef test_x():\n    assert True\n")
    try:
        proc = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q",
                               "-p", "no:cacheprovider", str(bad)],
                              capture_output=True, text=True, cwd=HARNESS,
                              env={**os.environ, "KICAD_HAPPY_DIR": os.environ.get(
                                  "KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))})
        assert proc.returncode != 0
        assert "'uint' not found in `markers`" in proc.stdout + proc.stderr
    finally:
        shutil.rmtree(bad, ignore_errors=True)  # includes __pycache__


def test_header_reports_product_sha():
    rc, _, out = _collect(quiet=False)
    assert "product_root:" in out and "sha=" in out


def test_script_style_integration_file_is_ignored():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
         "integration/"],
        capture_output=True, text=True, cwd=HARNESS,
        env={**os.environ, "KICAD_HAPPY_DIR": os.environ.get(
            "KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))})
    assert proc.returncode in (0, 5), proc.stdout + proc.stderr
    assert "INTERNALERROR" not in proc.stdout + proc.stderr
