"""Second corpus entries: an upgrade pair `- URL @ sha (as owner/repo@sha7)` lives in its own
repos/ dir and never disturbs the pinned entry of the same URL."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "tools"))
sys.path.insert(0, str(HARNESS))
import add_repos  # noqa: E402
import checkout  # noqa: E402
import generate_catalog  # noqa: E402

pytestmark = pytest.mark.unit

PIN = "a" * 40
NEW = "b" * 40
URL = "https://github.com/acme/board"
MD = f"""## Boards
- {URL} @ {PIN}
- {URL} @ {NEW} (as acme/board@bbbbbbb)
- https://github.com/acme/other @ {PIN} (shallow)
"""


def test_parse_reads_the_entry_name(tmp_path):
    md = tmp_path / "repos.md"
    md.write_text(MD)
    entries = checkout.parse_repos_md(md)
    assert [checkout.entry_name(e) for e in entries] == ["acme/board", "acme/board@bbbbbbb", "acme/other"]
    assert entries[1]["hash"] == NEW and entries[1]["category"] == "Boards"


@pytest.mark.parametrize("name", ["other/board@bbbbbbb", "acme/board", "acme/board@xyz1234", "acme/board@bbb"])
def test_parse_refuses_a_name_that_is_not_the_url_plus_a_sha(tmp_path, name):
    md = tmp_path / "repos.md"
    md.write_text(f"- {URL} @ {NEW} (as {name})\n")
    with pytest.raises(ValueError, match="second entry"):
        checkout.parse_repos_md(md)


def test_pin_never_touches_a_second_entry(tmp_path, monkeypatch):
    md = tmp_path / "repos.md"
    md.write_text(f"- {URL} @ {NEW} (as acme/board@bbbbbbb)\n- {URL} @ {PIN}\n")
    monkeypatch.setattr(checkout, "REPOS_MD", md)
    checkout.pin_hash_in_repos_md(URL, "c" * 40)
    assert md.read_text() == f"- {URL} @ {NEW} (as acme/board@bbbbbbb)\n- {URL} @ {'c' * 40}\n"


def test_filter_and_check_updates_use_the_entry_name(tmp_path, monkeypatch, capsys):
    md = tmp_path / "repos.md"
    md.write_text(MD)
    entries = checkout.parse_repos_md(md)
    assert [checkout.entry_name(e) for e in checkout._filter_repos(entries, "acme/board@*")] == ["acme/board@bbbbbbb"]
    monkeypatch.setattr(checkout, "REPOS_MD", md)
    monkeypatch.setattr(checkout, "get_remote_head", lambda url: "c" * 40)
    checkout.check_updates(entries[:2], do_fetch=False, do_pin=True, as_json=True, jobs=1)
    rows = json.loads(capsys.readouterr().out)["repos"]
    assert [(r["name"], r["status"]) for r in rows] == [("acme/board", "update-available"),
                                                        ("acme/board@bbbbbbb", "second-entry")]
    assert f"- {URL} @ {NEW} (as acme/board@bbbbbbb)" in md.read_text()


def test_clone_goes_to_the_entry_dir(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(checkout, "CLONE_DIR", tmp_path / "clones")
    monkeypatch.setattr(checkout, "clone_repo", lambda url, dest: seen.append(dest) or dest.mkdir(parents=True) or True)
    monkeypatch.setattr(checkout, "checkout_hash", lambda dest, h: True)
    monkeypatch.setattr(checkout, "get_head_hash", lambda dest: NEW)
    entry = {"url": URL, "hash": NEW, "shallow": False, "category": "Boards", "name": "acme/board@bbbbbbb"}
    assert checkout.clone_repos([entry], 0) == 0
    assert seen == [tmp_path / "clones" / "acme" / "board@bbbbbbb"]


def test_add_and_remove_a_pair_leave_the_pinned_line(tmp_path, monkeypatch):
    md = tmp_path / "repos.md"
    md.write_text(f"## Boards\n- {URL} @ {PIN}\n- https://github.com/acme/zzz @ {PIN}\n\n## Keyboards\n")
    monkeypatch.setattr(add_repos, "REPOS_MD", md)
    monkeypatch.setattr(add_repos, "get_remote_head", lambda url: pytest.fail("a pair is pinned by its candidate"))
    cand = {"owner": "acme", "repo": "board", "url": URL, "commit": NEW, "name": "acme/board@bbbbbbb"}
    assert add_repos._pre_add_repo(cand) == ("acme/board@bbbbbbb", URL, NEW, "Boards")
    lines = md.read_text().splitlines()
    assert lines[1:3] == [f"- {URL} @ {PIN}", f"- {URL} @ {NEW} (as acme/board@bbbbbbb)"]
    add_repos.remove_from_repos_md(URL, name="acme/board@bbbbbbb")
    assert md.read_text() == f"## Boards\n- {URL} @ {PIN}\n- https://github.com/acme/zzz @ {PIN}\n\n## Keyboards\n"


def test_catalog_keys_a_pair_by_its_name(tmp_path, monkeypatch):
    md = tmp_path / "repos.md"
    md.write_text(MD)
    monkeypatch.setattr(generate_catalog, "REPOS_MD", md)
    assert generate_catalog._load_categories()["acme/board@bbbbbbb"] == "Boards"
    assert generate_catalog._load_repo_urls()["acme/board@bbbbbbb"]["hash"] == NEW
    assert generate_catalog._load_repo_urls()["acme/board"]["hash"] == PIN
