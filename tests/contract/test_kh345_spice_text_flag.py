#!/usr/bin/env python3
"""KH-345: simulate_subcircuits gains --text (SKILL.md says all analyzers
support it); SKILL.md stops showing the broken --temp-range space form."""

import json
import shutil
import subprocess
import sys

import pytest

from tests.contract._paths import MAIN_REPO_ROOT

SCRIPT = MAIN_REPO_ROOT / "skills" / "spice" / "scripts" / "simulate_subcircuits.py"
SKILL_MD = MAIN_REPO_ROOT / "skills" / "kicad" / "SKILL.md"


def test_text_flag_in_help():
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "--text" in r.stdout


@pytest.mark.skipif(shutil.which("ngspice") is None,
                    reason="ngspice not installed")
def test_text_output_is_not_json(tmp_path):
    analysis = {"schema_version": "1.4.0", "findings": [], "components": []}
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(analysis))
    r = subprocess.run([sys.executable, str(SCRIPT), str(p), "--text"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert not r.stdout.lstrip().startswith("{")


def test_skill_md_temp_range_uses_equals_form():
    text = SKILL_MD.read_text()
    assert '--temp-range "-40' not in text
