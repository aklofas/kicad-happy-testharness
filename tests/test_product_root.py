"""tests/product_root.py is the one required bridge to KICAD_HAPPY_DIR."""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent


def _fresh_import(monkeypatch, env):
    for k in ("KICAD_HAPPY_DIR", "HARNESS_ALLOW_SIBLING_FALLBACK"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    sys.modules.pop("tests.product_root", None)
    return importlib.import_module("tests.product_root")


def _fake_product(tmp_path):
    root = tmp_path / "kh"
    (root / "skills" / "kicad" / "scripts").mkdir(parents=True)
    (root / "skills" / "kicad" / "scripts" / "analyze_schematic.py").write_text("# stub\n")
    (root / "skills" / "emc" / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    return root


def test_missing_env_raises(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # no sibling kicad-happy here
    with pytest.raises(RuntimeError) as ei:
        _fresh_import(monkeypatch, {})
    assert "KICAD_HAPPY_DIR" in str(ei.value)


def test_env_points_to_non_product_dir_raises(monkeypatch, tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(RuntimeError) as ei:
        _fresh_import(monkeypatch, {"KICAD_HAPPY_DIR": str(tmp_path / "empty")})
    assert "analyze_schematic.py" in str(ei.value)


def test_valid_env_resolves_and_reports_sha(monkeypatch, tmp_path):
    root = _fake_product(tmp_path)
    mod = _fresh_import(monkeypatch, {"KICAD_HAPPY_DIR": str(root)})
    assert mod.PRODUCT_ROOT == root.resolve()
    sha = mod.product_sha()
    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)
    assert mod.product_is_dirty() is False
    (root / "untracked.txt").write_text("x")
    assert mod.product_is_dirty() is True


def test_script_dir_and_import_paths_idempotent(monkeypatch, tmp_path):
    root = _fake_product(tmp_path)
    mod = _fresh_import(monkeypatch, {"KICAD_HAPPY_DIR": str(root)})
    assert mod.script_dir("kicad") == root.resolve() / "skills" / "kicad" / "scripts"
    before = list(sys.path)
    mod.ensure_import_paths("kicad", "emc")
    mod.ensure_import_paths("kicad", "emc")
    added = [p for p in sys.path if p not in before]
    assert added == [str(mod.script_dir("kicad")), str(mod.script_dir("emc"))] or \
        set(added) == {str(mod.script_dir("kicad")), str(mod.script_dir("emc"))}
    assert sys.path.count(str(mod.script_dir("kicad"))) == 1


def test_sibling_fallback_requires_flag(monkeypatch, tmp_path):
    # Build <tmp>/harness-ish/tests/product_root.py sibling layout is not
    # reproducible without copying the module; instead assert the flag gate
    # through the resolver's documented error text.
    with pytest.raises(RuntimeError) as ei:
        _fresh_import(monkeypatch, {})
    assert "HARNESS_ALLOW_SIBLING_FALLBACK" in str(ei.value)


def test_contract_paths_reexports(monkeypatch):
    monkeypatch.setenv("KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))
    sys.modules.pop("tests.product_root", None)
    sys.modules.pop("tests.contract._paths", None)
    paths = importlib.import_module("tests.contract._paths")
    pr = importlib.import_module("tests.product_root")
    assert paths.MAIN_REPO_ROOT == pr.PRODUCT_ROOT
    assert paths.HARNESS_ROOT == pr.HARNESS_ROOT == HARNESS
