"""Tests for tools/source_scan.py — the shared recursive source walker (A2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS / "tools"))

import source_scan  # noqa: E402

FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan4" / "fake_product"


def test_iter_product_sources_recurses_and_sorts():
    files = source_scan.iter_product_sources(FAKE)
    rels = [source_scan.rel(FAKE, p) for p in files]
    assert rels == sorted(rels)
    assert "skills/kicad/scripts/schematic/reader.py" in rels
    assert "skills/kicad/scripts/pcb/reader.py" in rels
    assert "skills/kicad/scripts/schematic/__init__.py" in rels
    assert "skills/emc/scripts/emc_rules.py" in rels


def test_iter_product_sources_skips_pycache():
    junk_dir = FAKE / "skills" / "emc" / "scripts" / "__pycache__"
    junk_dir.mkdir(parents=True, exist_ok=True)
    (junk_dir / "junk.cpython-312.pyc").touch()
    rels = [source_scan.rel(FAKE, p) for p in source_scan.iter_product_sources(FAKE)]
    assert not any("__pycache__" in r for r in rels)
    assert all(r.endswith(".py") for r in rels)


def test_rel_is_posix_root_relative():
    p = FAKE / "skills" / "kicad" / "scripts" / "pcb" / "reader.py"
    assert source_scan.rel(FAKE, p) == "skills/kicad/scripts/pcb/reader.py"
    assert "\\" not in source_scan.rel(FAKE, p)
