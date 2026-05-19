"""End-to-end contract test: v1.4 datasheet cache round-trip through
``analyze_schematic.py``.

Catches the rc.3 P0 regression class — "verifier silently breaks because
cache shape drifted." The main-repo smoke
(``skills/datasheets/scripts/_smoke_v14_roundtrip.py``) imports
``run_datasheet_verification`` and calls it directly with a synthetic
analysis dict. That covers the trivial crash on
``verify_decoupling(None.get(...))``. This contract test goes one step
deeper: it drives ``analyze_schematic.py`` end-to-end with a real
fixture schematic and a v1.4-shape extraction planted at
``<project>/datasheets/extracted/<MPN>.json``, then validates the
``datasheet_verification`` block in the analyzer's output JSON.

Regression-class discriminators baked in:

1. ``ics_with_extractions >= 1`` — the cache file *was* loaded. Pre-rc.3
   ``_load_extraction`` reads ``meta.extraction_score`` (a v1.3 key) and
   trust-gates v1.4 caches at 0 < 6.0; the load returns ``{}``, which the
   verifier treats as "no extraction" and increments nothing.
2. ``"error" not in summary`` — the verifier ran to completion. Pre-rc.3
   ``verify_decoupling`` then crashed on ``None.get(...)``;
   ``analyze_schematic.py`` catches ``AttributeError`` as
   defense-in-depth and writes ``summary.error = "AttributeError: ..."``.

A future drift in either direction (cache shape changes again,
``_load_extraction`` mis-trusts a new key) will trip discriminator 1
before discriminator 2 — that's the "more-subtle drift" main-repo smoke
can't see, because it bypasses ``analyze_schematic.py`` wiring.

Fixture strategy: copy the simple-project fixture and patch two strings
in-memory before writing it back to tmp:

  * ``"R1"`` → ``"U1"`` — flips the ref prefix from R (resistor) to U
    (ic). ``classify_component()`` uses the ref prefix; ``Device:R``
    lib_id is irrelevant for type assignment when prefix wins.
  * ``"RC0603FR-07330RL"`` → ``"LM2596-ADJ"`` — retargets the MPN at
    the canonical sanity-vector regulator that ships an example
    extraction at ``skills/datasheets/examples/lm2596-adj.json``.

Both strings appear exactly 2× and 1× respectively in the fixture, so
``str.replace`` is unambiguous.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

SIMPLE_FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"
EXAMPLE_EXTRACTION = MAIN_REPO_ROOT / "skills" / "datasheets" / "examples" / "lm2596-adj.json"
ANALYZE_SCHEMATIC = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"

MPN = "LM2596-ADJ"


def _build_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    sch_text = SIMPLE_FIXTURE.read_text(encoding="utf-8")
    assert sch_text.count('"R1"') == 2, (
        f"Fixture invariant broken: expected 2 occurrences of '\"R1\"' in "
        f"{SIMPLE_FIXTURE}, found {sch_text.count('\"R1\"')}"
    )
    assert sch_text.count('"RC0603FR-07330RL"') == 1, (
        f"Fixture invariant broken: expected 1 occurrence of MPN string "
        f"in {SIMPLE_FIXTURE}, found {sch_text.count('\"RC0603FR-07330RL\"')}"
    )
    sch_text = sch_text.replace('"R1"', '"U1"')
    sch_text = sch_text.replace('"RC0603FR-07330RL"', f'"{MPN}"')
    sch_path = project_dir / "minimal.kicad_sch"
    sch_path.write_text(sch_text, encoding="utf-8")
    return sch_path


def _plant_cache(project_dir: Path) -> Path:
    cache_dir = project_dir / "datasheets" / "extracted"
    cache_dir.mkdir(parents=True)
    cache_file = cache_dir / f"{MPN}.json"
    shutil.copy(EXAMPLE_EXTRACTION, cache_file)
    return cache_file


def _run_analyzer(sch_path: Path, output_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(ANALYZE_SCHEMATIC),
            str(sch_path),
            "--output",
            str(output_path),
            "--no-hierarchy",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_v14_cache_roundtrip_does_not_error(tmp_path):
    sch_path = _build_project(tmp_path)
    cache_file = _plant_cache(sch_path.parent)
    assert cache_file.is_file()

    out_path = tmp_path / "out.json"
    res = _run_analyzer(sch_path, out_path)
    assert res.returncode == 0, (
        f"analyze_schematic.py exited {res.returncode}\nSTDERR:\n{res.stderr}"
    )
    out = json.loads(out_path.read_text(encoding="utf-8"))

    ics = [
        c for c in out.get("components", [])
        if c.get("type") == "ic" and c.get("mpn") == MPN
    ]
    assert ics, (
        f"Test-setup invariant broken: no IC with mpn={MPN!r} in analyzer "
        f"output. The verifier would never attempt cache load and the "
        f"test would pass vacuously. Components: "
        f"{[(c.get('reference'), c.get('type'), c.get('mpn')) for c in out.get('components', [])]}"
    )

    assert "datasheet_verification" in out, (
        "datasheet_verification block missing; analyzer wraps it when "
        "findings exist, ics_with_extractions > 0, or an exception was "
        "caught into summary.error. None of these fired."
    )
    ds = out["datasheet_verification"]

    assert isinstance(ds.get("findings"), list), (
        f"datasheet_verification.findings must be a list; got "
        f"{type(ds.get('findings')).__name__}"
    )
    assert isinstance(ds.get("summary"), dict), (
        f"datasheet_verification.summary must be a dict; got "
        f"{type(ds.get('summary')).__name__}"
    )

    assert "error" not in ds["summary"], (
        f"datasheet_verification.summary.error present — the v1.4 cache "
        f"shape was not handled cleanly. error="
        f"{ds['summary'].get('error')!r}"
    )

    assert ds["summary"].get("ics_with_extractions", 0) >= 1, (
        f"ics_with_extractions={ds['summary'].get('ics_with_extractions')}; "
        f"v1.4 cache for {MPN} did not pass the trust gate. "
        f"summary={ds['summary']!r}"
    )
