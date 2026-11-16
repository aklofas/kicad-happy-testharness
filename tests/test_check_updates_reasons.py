"""checkout.py --check-updates: a failed remote lookup carries its reason, failures get one slow
retry, and --github-api resolves GitHub entries through authenticated GraphQL (a deleted repo is
`gone`, not a generic error)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import checkout  # noqa: E402

pytestmark = pytest.mark.unit

PIN = "a" * 40
TIP = "b" * 40


def _done(rc=0, out="", err=""):
    return subprocess.CompletedProcess([], rc, stdout=out, stderr=err)


@pytest.mark.parametrize("result, expected", [
    (_done(out=f"{TIP}\tHEAD\n"), (TIP, None)),
    (_done(128, err="fatal: could not read Username for 'https://github.com': terminal prompts disabled"),
     (None, "denied-or-missing")),
    (_done(128, err="fatal: repository 'https://gitlab.com/x/y/' not found"), (None, "denied-or-missing")),
    (_done(128, err="fatal: unable to access: Could not resolve host: example.org"), (None, "unreachable")),
    (_done(0, out=""), (None, "empty")),
])
def test_ls_remote_head_keeps_the_reason(monkeypatch, result, expected):
    monkeypatch.setattr(checkout.subprocess, "run", lambda *a, **k: result)
    assert checkout.ls_remote_head("https://github.com/acme/board") == expected


def test_ls_remote_head_timeout(monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired("git", 30)
    monkeypatch.setattr(checkout.subprocess, "run", boom)
    assert checkout.ls_remote_head("https://github.com/acme/board") == (None, "timeout")


def test_get_remote_head_still_returns_the_hash(monkeypatch):
    monkeypatch.setattr(checkout, "ls_remote_head", lambda url: (TIP, None))
    assert checkout.get_remote_head("https://github.com/acme/board") == TIP


def _graphql_reply(query):
    """Answer like GitHub: every alias resolves to TIP except names containing 'gone'."""
    data, errors = {}, []
    for alias, name in re.findall(r'(\w+): repository\(owner: "[^"]*", name: "([^"]*)"\)', query):
        if "gone" in name:
            data[alias] = None
            errors.append({"type": "NOT_FOUND", "path": [alias]})
        elif "forbidden" in name:
            data[alias] = None
            errors.append({"type": "FORBIDDEN", "path": [alias]})
        else:
            data[alias] = {"defaultBranchRef": {"target": {"oid": TIP}}}
    return json.dumps({"data": data, **({"errors": errors} if errors else {})})


def test_github_heads_batches_and_marks_deleted_repos_gone(monkeypatch):
    calls = []

    def fake_run(cmd, **k):
        calls.append(cmd)
        query = cmd[-1].removeprefix("query=")
        return _done(1 if "gone" in query else 0, out=_graphql_reply(query))
    monkeypatch.setattr(checkout.subprocess, "run", fake_run)
    urls = [f"https://github.com/acme/b{i}" for i in range(118)] + [
        "https://github.com/acme/gone-one", "https://github.com/acme/forbidden-one.git"]
    heads = checkout.github_heads(urls)
    assert len(calls) == 3 and all(c[:3] == ["gh", "api", "graphql"] for c in calls)
    assert heads["https://github.com/acme/b0"] == (TIP, None)
    assert heads["https://github.com/acme/gone-one"] == (None, "gone")
    assert "https://github.com/acme/forbidden-one.git" not in heads   # unresolved: falls back


def test_github_heads_falls_back_when_gh_is_unusable(monkeypatch):
    monkeypatch.setattr(checkout.subprocess, "run", lambda *a, **k: _done(4, err="gh: not logged in"))
    assert checkout.github_heads(["https://github.com/acme/board"]) == {}

    def missing(*a, **k):
        raise FileNotFoundError("gh")
    monkeypatch.setattr(checkout.subprocess, "run", missing)
    assert checkout.github_heads(["https://github.com/acme/board"]) == {}


def _entries(*names):
    return [{"url": f"https://github.com/acme/{n}", "hash": PIN, "shallow": False,
             "category": "Boards"} for n in names]


def test_check_updates_reports_reasons_and_retries_once(monkeypatch, capsys):
    tries = {}

    def flaky(url):
        tries[url] = tries.get(url, 0) + 1
        if url.endswith("/flaky") and tries[url] == 1:
            return None, "denied-or-missing"
        if url.endswith("/dead"):
            return None, "denied-or-missing"
        return PIN, None
    monkeypatch.setattr(checkout, "ls_remote_head", flaky)
    monkeypatch.setattr(checkout, "RETRY_DELAY_S", 0)
    checkout.check_updates(_entries("ok", "flaky", "dead"), do_fetch=False, do_pin=False,
                           as_json=True, jobs=2)
    out = json.loads(capsys.readouterr().out)
    rows = {r["name"]: r for r in out["repos"]}
    assert rows["acme/ok"]["status"] == "up-to-date" and tries["https://github.com/acme/ok"] == 1
    assert rows["acme/flaky"]["status"] == "up-to-date" and tries["https://github.com/acme/flaky"] == 2
    assert rows["acme/dead"]["status"] == "error" and rows["acme/dead"]["reason"] == "denied-or-missing"
    assert out["errors"] == 1 and out["error_reasons"] == {"denied-or-missing": 1}


def test_check_updates_github_api_path(monkeypatch, capsys):
    monkeypatch.setattr(checkout, "github_heads", lambda urls: {
        "https://github.com/acme/moved": (TIP, None), "https://github.com/acme/gone": (None, "gone")})
    monkeypatch.setattr(checkout, "ls_remote_head", lambda url: (PIN, None))   # the unresolved rest
    checkout.check_updates(_entries("moved", "gone", "rest"), do_fetch=False, do_pin=False,
                           as_json=True, jobs=1, github_api=True)
    out = json.loads(capsys.readouterr().out)
    rows = {r["name"]: r["status"] for r in out["repos"]}
    assert rows == {"acme/moved": "update-available", "acme/gone": "gone", "acme/rest": "up-to-date"}
    assert out["gone"] == 1 and out["errors"] == 0
