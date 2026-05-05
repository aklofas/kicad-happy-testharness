"""Unit tests for plan_extraction.py (Phase 3a)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = MAIN_REPO_ROOT / "skills/datasheets/scripts/plan_extraction.py"
SCOUT_FIXTURE = HARNESS_ROOT / "tests/fixtures/datasheets/scout-lm2596-adj.example.json"


@pytest.fixture
def workdir(tmp_path):
    pdf = tmp_path / "LM2596-ADJ.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%fake fixture content\n")
    cache = tmp_path / "datasheets" / "extracted"
    cache.mkdir(parents=True)
    scout_payload = json.loads(SCOUT_FIXTURE.read_text())
    (cache / "LM2596-ADJ.scout.json").write_text(json.dumps(scout_payload))
    return tmp_path, pdf, cache


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True
    )


def test_writes_plan_with_pdf_sha(workdir):
    tmp, pdf, cache = workdir
    res = _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache), "--use-cached-scout")
    assert res.returncode == 0, res.stderr
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    expected_sha = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert plan["pdf_sha256"] == expected_sha
    assert plan["mpn"] == "LM2596-ADJ"


def test_plan_has_one_task_per_scout_category_plus_base_and_pinout(workdir):
    tmp, pdf, cache = workdir
    res = _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache), "--use-cached-scout")
    assert res.returncode == 0
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    task_ids = {t["task_id"] for t in plan["tasks"]}
    assert task_ids == {"base", "pinout", "regulator"}


def test_plan_pages_match_scout_extraction_pages(workdir):
    tmp, pdf, cache = workdir
    _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache), "--use-cached-scout")
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    by_id = {t["task_id"]: t for t in plan["tasks"]}
    scout = json.loads((cache / "LM2596-ADJ.scout.json").read_text())
    for tid in ("base", "pinout", "regulator"):
        assert by_id[tid]["pages"] == scout["extraction_pages"][tid]


def test_skip_verdict_writes_empty_plan_and_exits_nonzero(workdir):
    tmp, pdf, cache = workdir
    scout = json.loads((cache / "LM2596-ADJ.scout.json").read_text())
    scout["quality_verdict"] = {"verdict": "skip", "reason": "scanned image"}
    (cache / "LM2596-ADJ.scout.json").write_text(json.dumps(scout))
    res = _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache), "--use-cached-scout")
    assert res.returncode == 1
    plan = json.loads((cache / "LM2596-ADJ.plan.json").read_text())
    assert plan["tasks"] == []


def test_existing_cache_unchanged_without_force(workdir):
    tmp, pdf, cache = workdir
    sha = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
    (cache / "LM2596-ADJ.json").write_text(json.dumps({
        "schema_version": {"base": "1.0", "categories": {"regulator": "0.3"}},
        "source": {"manufacturer": "TI", "mpn": "LM2596-ADJ", "sha256": sha},
        "extraction": {"extracted_at": "2026-04-25T10:00:00Z", "extractor_schema_version": "1.0"},
        "base": {}
    }))
    res = _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache), "--use-cached-scout")
    assert res.returncode == 0
    assert "already up-to-date" in (res.stdout + res.stderr)


def test_force_regenerates_plan(workdir):
    tmp, pdf, cache = workdir
    sha = "sha256:" + hashlib.sha256(pdf.read_bytes()).hexdigest()
    (cache / "LM2596-ADJ.json").write_text(json.dumps({
        "schema_version": {"base": "1.0", "categories": {"regulator": "0.3"}},
        "source": {"manufacturer": "TI", "mpn": "LM2596-ADJ", "sha256": sha},
        "extraction": {"extracted_at": "2026-04-25T10:00:00Z", "extractor_schema_version": "1.0"},
        "base": {}
    }))
    res = _run("LM2596-ADJ", str(pdf), "--cache-dir", str(cache),
               "--use-cached-scout", "--force")
    assert res.returncode == 0
    assert (cache / "LM2596-ADJ.plan.json").exists()
