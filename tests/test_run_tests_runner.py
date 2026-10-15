"""run_tests.py is a thin alias over pytest (B9). It must never report success
for an empty selection or a failed pytest run."""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import run_tests  # noqa: E402

ENV = {**os.environ, "KICAD_HAPPY_DIR": os.environ.get(
    "KICAD_HAPPY_DIR", str(Path.home() / "Projects" / "kicad-happy"))}


class _Args:
    def __init__(self, **kw):
        self.unit = kw.get("unit", False)
        self.integration = kw.get("integration", False)
        self.tier = kw.get("tier")
        self.smoke = kw.get("smoke", False)
        self.json = kw.get("json", False)
        self.paths = kw.get("paths", [])


def _argv(**kw):
    """Alias argv minus the ``python -m pytest`` prefix (its own ``-m`` would confuse marker checks)."""
    argv = run_tests.build_pytest_argv(_Args(**kw))
    assert argv[1:3] == ["-m", "pytest"]
    return argv[3:]


def test_argv_unit():
    argv = _argv(unit=True)
    assert "-m" in argv and argv[argv.index("-m") + 1] == "unit"
    assert "tests" in argv and "integration" not in argv


def test_argv_online():
    argv = _argv(tier="online")
    assert argv[argv.index("-m") + 1] == "online"
    assert "integration" in argv and "tests" in argv


def test_argv_all_tiers():
    argv = _argv(tier="all")
    assert "--all-tiers" in argv and "-m" not in argv


def test_argv_smoke_uses_curated_files():
    argv = _argv(smoke=True)
    assert argv[argv.index("-m") + 1] == "unit"
    assert all(p in argv for p in run_tests.SMOKE_TESTS)


def test_exit_mapping():
    assert run_tests.pytest_exit_to_rc(0) == 0
    assert run_tests.pytest_exit_to_rc(5) == 2
    assert run_tests.pytest_exit_to_rc(1) == 1
    assert run_tests.pytest_exit_to_rc(2) == 1


def test_junit_to_legacy(tmp_path):
    xml = tmp_path / "j.xml"
    xml.write_text(textwrap.dedent('''\
        <testsuites><testsuite name="pytest" tests="3" failures="1" skipped="1">
          <testcase classname="tests.test_a" name="test_ok" file="tests/test_a.py"/>
          <testcase classname="tests.test_a" name="test_bad" file="tests/test_a.py"><failure message="x"/></testcase>
          <testcase classname="tests.test_b" name="test_skip" file="tests/test_b.py"><skipped message="y"/></testcase>
        </testsuite></testsuites>'''))
    d = run_tests.junit_to_legacy(xml)
    assert (d["total_passed"], d["total_failed"], d["total_skipped"]) == (1, 1, 1)
    files = {f["file"]: f for f in d["files"]}
    assert files["tests/test_a.py"]["status"] == "fail"
    assert files["tests/test_b.py"]["status"] == "pass"


def test_alias_zero_selection_is_failure(tmp_path):
    empty = tmp_path / "nothing"
    empty.mkdir()
    proc = subprocess.run([sys.executable, "run_tests.py", "--unit", "--paths", str(empty)],
                          capture_output=True, text=True, cwd=HARNESS, env=ENV)
    assert proc.returncode == 2, proc.stdout + proc.stderr


@pytest.mark.perf
def test_alias_smoke_runs_green():
    proc = subprocess.run([sys.executable, "run_tests.py", "--smoke", "--json"],
                          capture_output=True, text=True, cwd=HARNESS, env=ENV, timeout=900)
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    data = json.loads(proc.stdout[proc.stdout.index("{"):])
    assert data["total_failed"] == 0 and data["total_passed"] > 500
