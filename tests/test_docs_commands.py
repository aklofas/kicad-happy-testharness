"""Documented commands must exist and do what the docs say (docs A1-F1, F3, F5, F7, F9, F12)."""
import re
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.unit


def _doc(name):
    return (HARNESS / name).read_text(encoding="utf-8")


def test_verify_parser_has_no_type_flag_in_docs():
    for name in ("RUNBOOK.md", "README.md"):
        assert not re.search(r"verify_parser\.py[^\n]*--type", _doc(name)), name


def test_harness_run_has_no_full_flag():
    for name in ("RUNBOOK.md", "README.md", "harness.py"):
        assert "harness.py run --full" not in _doc(name), name


def test_findings_are_promoted_with_findings_py_not_promote_py():
    runbook = _doc("RUNBOOK.md")
    sec = runbook[runbook.index("### 13e"):runbook.index("### 13f")]
    assert "findings.py promote-all" in sec
    assert "promote.py --repo" not in sec


def test_required_tiers_are_not_run_with_unit_only():
    runbook = _doc("RUNBOOK.md")
    assert 'pytest -m "unit or offline_contract"' in runbook
    for line in runbook.splitlines():
        if "run_tests.py --unit" in line:
            assert "offline_contract" not in line or "only" in line, line


def test_chained_runner_examples_carry_a_selector():
    for name in ("emc.md", "spice.md"):
        for line in _doc(name).splitlines():
            m = re.search(r"python3? run/run_(emc|spice|thermal)\.py([^\n`]*)", line)
            if m:
                assert re.search(r"--(all|repo|cross-section|repo-list)\b", m.group(2)), line


def test_python_floor_is_310():
    for name in ("README.md", "methodology.md"):
        assert "Python 3.8+" not in _doc(name), name


def test_harness_validate_is_described_as_assertions_only():
    readme = _doc("README.md")
    assert "runs unit tests + assertions + validators" not in readme
