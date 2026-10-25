"""reference_io owns output lookup, project resolution and set loading."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "regression"))

import reference_io  # noqa: E402


def test_old_names_are_the_same_objects():
    import run_checks
    import check_staleness
    import assertion_metrics
    assert run_checks.find_output_file is reference_io.find_output_file
    assert check_staleness.find_output_file is reference_io.find_output_file
    assert assertion_metrics.find_output_file is reference_io.find_output_file


def test_resolve_project_path_prefers_metadata_then_discovery(monkeypatch):
    monkeypatch.setattr(reference_io, "load_project_metadata",
                        lambda r, p: {"project_path": "meta/path"})
    monkeypatch.setattr(reference_io, "discover_projects",
                        lambda r: [{"name": "p", "path": "disc"}])
    assert reference_io.resolve_project_path("o/r", "p") == "meta/path"

    monkeypatch.setattr(reference_io, "load_project_metadata", lambda r, p: {})
    assert reference_io.resolve_project_path("o/r", "p") == "disc"
    assert reference_io.resolve_project_path("o/r", "other") is None

    def boom(r):
        raise OSError("no repo")
    monkeypatch.setattr(reference_io, "discover_projects", boom)
    assert reference_io.resolve_project_path("o/r", "p") is None


def test_load_set_output_reports_missing_and_parse_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(reference_io, "OUTPUTS_DIR", tmp_path)
    d = tmp_path / "schematic" / "o_r"
    d.mkdir(parents=True)
    aset = {"file_pattern": "a", "_repo": "o_r", "_project_path": "."}
    assert reference_io.load_set_output(aset) == (None, "output file not found")
    (d / "a.json").write_text("{not json")
    data, err = reference_io.load_set_output(aset)
    assert data is None and err.startswith("JSON parse error: ")
    (d / "a.json").write_text('{"k": 1}')
    assert reference_io.load_set_output(aset) == ({"k": 1}, None)


def test_no_regression_module_imports_find_output_file_from_run_checks():
    out = subprocess.run(
        ["git", "grep", "-n", "from run_checks import.*find_output_file",
         "--", "*.py"], cwd=ROOT, capture_output=True, text=True).stdout
    own = [l for l in out.splitlines()
           if not l.startswith("tests/test_reference_io.py")]
    assert own == []


def test_checks_importable_package_style_with_only_root_on_path(tmp_path):
    code = ("import sys; sys.path.insert(0, %r); "
            "from regression.checks import evaluate_assertion" % str(ROOT))
    r = subprocess.run([sys.executable, "-c", code], cwd=tmp_path,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("module", ["findings", "seed", "seed_structural", "seed_negative"])
def test_writers_share_one_reference_io_module_package_style(tmp_path, module):
    code = ("import sys; sys.path.insert(0, %r); "
            "import regression.%s as m; import reference_io; "
            "assert m.write_assertion_file is reference_io.write_assertion_file; "
            "assert 'regression.reference_io' not in sys.modules" % (str(ROOT), module))
    r = subprocess.run([sys.executable, "-c", code], cwd=tmp_path,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
