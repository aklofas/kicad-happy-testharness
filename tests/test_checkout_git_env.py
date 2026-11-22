"""checkout.py: corpus clone and fetch never stop to ask for credentials (a repo that went
private would otherwise hang the run on a username prompt)."""
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import checkout  # noqa: E402

pytestmark = pytest.mark.unit


def _capture_envs(monkeypatch):
    envs = []

    def fake_run(cmd, **kw):
        envs.append(kw.get("env"))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(checkout.subprocess, "run", fake_run)
    return envs


def test_clone_disables_terminal_prompt(monkeypatch, tmp_path):
    envs = _capture_envs(monkeypatch)
    assert checkout.clone_repo("https://example.invalid/a/b", tmp_path / "b")
    assert envs and all(e["GIT_TERMINAL_PROMPT"] == "0" for e in envs)


def test_fetch_and_checkout_disable_terminal_prompt(monkeypatch, tmp_path):
    envs = _capture_envs(monkeypatch)
    assert checkout.checkout_hash(tmp_path, "c" * 40)
    assert len(envs) == 2 and all(e["GIT_TERMINAL_PROMPT"] == "0" for e in envs)
