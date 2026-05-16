"""E2E smoke test for the hierarchy regression gate driver.

Audit LOG 9 / regression-testing-audit F9 (2026-05-15): wires
``regression/run_hierarchy_regression_gate.py`` through to real analyzer
runs on each curated sub-sheet. The unit-test file
(``tests/test_v14_hierarchy_gate.py``) covers the contract helpers with
synthetic envelopes; this file covers the corpus-integration path that
the unit tests can't.

Each parametrized case invokes the gate driver's ``_process_board``
worker on one curated sub-sheet and asserts the result is PASS. A
regression in the analyzer's ``--no-hierarchy`` wiring, hierarchy
auto-discovery, or intra-seed determinism would FAIL the corresponding
board (without breaking the synthetic-envelope unit tests).

TIER="online" — requires:
  * ``KICAD_HAPPY_DIR`` env var
  * the 3 curated repos checked out under ``repos/`` (run ``checkout.py``)

Runtime: ~30-60 s per board (3 analyzer subprocesses each); the largest
(``pyspice-analog-inputs``) dominates at ~20 s × 3 runs.
"""

from __future__ import annotations

TIER = "online"

import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from regression.run_hierarchy_regression_gate import (  # noqa: E402
    CURATED_SET,
    REPOS_DIR,
    _process_board,
)


@pytest.mark.parametrize("spec", CURATED_SET, ids=[b["name"] for b in CURATED_SET])
def test_hierarchy_gate_board_passes(spec):
    """Run the gate driver against one curated sub-sheet end-to-end and
    assert all 3 contracts pass. Skips cleanly if the underlying repo
    isn't checked out."""
    sch_path = REPOS_DIR / spec["sch_path_rel"]
    if not sch_path.is_file():
        pytest.skip(f"missing sub-sheet {sch_path} — run checkout.py")

    record = _process_board((spec, MAIN_REPO_ROOT, False))

    contracts_detail = ", ".join(
        f"{cn}={cv}({cd[:80]})"
        for cn, (cv, cd) in record["contracts"].items()
    )
    assert record["verdict"] == "PASS", (
        f"board {spec['name']!r}: {contracts_detail}"
    )
