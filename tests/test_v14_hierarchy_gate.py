"""Lock the contract-check semantics of ``regression/run_hierarchy_regression_gate.py``.

Audit LOG 9 / regression-testing-audit F9 (2026-05-15): the hierarchy gate's
three contracts (expansion_evident, finding_set_superset, determinism) need
test-suite coverage so future helper refactors can't silently weaken them.
Mirrors the pattern of ``tests/test_v14_default_contract_gate.py`` — direct
calls into each ``_check_*`` helper with synthetic envelopes; no analyzer
runs.

The E2E gate-driver-against-real-corpus path is covered separately in
``tests/contract/test_hierarchy_gate_smoke.py`` (TIER="online").
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from regression.run_hierarchy_regression_gate import (  # noqa: E402
    _aggregate,
    _check_determinism,
    _check_finding_superset,
    _check_hierarchy_expansion,
    _envelope_hash,
    _print_summary,
    _strip_volatile,
)


# ---------------------------------------------------------------------------
# _check_hierarchy_expansion
# ---------------------------------------------------------------------------

def test_hierarchy_expansion_pass_when_hierarchy_grew_set():
    hier = {
        "components": [{"ref": "U1"}, {"ref": "R1"}, {"ref": "C1"}],
        "subcircuits": [{"name": "S1"}, {"name": "S2"}],
        "hierarchy_warning": None,
    }
    nohier = {
        "components": [{"ref": "U1"}],
        "subcircuits": [{"name": "S1"}],
        "hierarchy_warning": "File appears to be a sub-sheet but hierarchy "
                             "discovery is disabled (--no-hierarchy).",
    }
    v, d = _check_hierarchy_expansion(hier, nohier)
    assert v == "PASS", d
    assert "components 1→3" in d
    assert "subcircuits 1→2" in d


def test_hierarchy_expansion_fail_when_no_warning_in_nohier_mode():
    """If --no-hierarchy didn't populate hierarchy_warning, either the input
    isn't a sub-sheet or the flag is unwired. Either way the gate's premise
    is broken — fail loudly."""
    hier = {"components": [{"ref": "U1"}], "subcircuits": [], "hierarchy_warning": None}
    nohier = {"components": [{"ref": "U1"}], "subcircuits": [], "hierarchy_warning": None}
    v, d = _check_hierarchy_expansion(hier, nohier)
    assert v == "FAIL"
    assert "--no-hierarchy mode did NOT populate hierarchy_warning" in d


def test_hierarchy_expansion_fail_when_hierarchy_mode_warning_present():
    """Default-hierarchy mode should auto-discover the parent and clear the
    warning. If the warning persists, auto-discovery failed."""
    hier = {
        "components": [{"ref": "U1"}],
        "subcircuits": [],
        "hierarchy_warning": "auto-discovery failed",
    }
    nohier = {
        "components": [{"ref": "U1"}],
        "subcircuits": [],
        "hierarchy_warning": "sub-sheet, no-hierarchy",
    }
    v, d = _check_hierarchy_expansion(hier, nohier)
    assert v == "FAIL"
    assert "auto-discovery failed to find parent" in d


def test_hierarchy_expansion_fail_when_hier_shrinks_components():
    hier = {"components": [{"ref": "U1"}], "subcircuits": [{"name": "S"}], "hierarchy_warning": None}
    nohier = {
        "components": [{"ref": "U1"}, {"ref": "U2"}, {"ref": "U3"}],
        "subcircuits": [{"name": "S"}],
        "hierarchy_warning": "sub-sheet",
    }
    v, d = _check_hierarchy_expansion(hier, nohier)
    assert v == "FAIL"
    assert "components=1 < --no-hierarchy components=3" in d


def test_hierarchy_expansion_fail_when_hier_shrinks_subcircuits():
    hier = {"components": [{"ref": "U1"}], "subcircuits": [], "hierarchy_warning": None}
    nohier = {
        "components": [{"ref": "U1"}],
        "subcircuits": [{"name": "S1"}, {"name": "S2"}],
        "hierarchy_warning": "sub-sheet",
    }
    v, d = _check_hierarchy_expansion(hier, nohier)
    assert v == "FAIL"
    assert "subcircuits=0 < --no-hierarchy subcircuits=2" in d


# ---------------------------------------------------------------------------
# _check_finding_superset
# ---------------------------------------------------------------------------

def test_finding_superset_pass_when_strict_superset():
    hier_env = {"findings": [
        {"rule_id": "A"}, {"rule_id": "B"}, {"rule_id": "C"},
    ]}
    nohier_env = {"findings": [{"rule_id": "A"}, {"rule_id": "B"}]}
    v, d = _check_finding_superset(hier_env, nohier_env)
    assert v == "PASS", d
    assert "2 no-hier findings" in d and "3 hier findings" in d


def test_finding_superset_pass_when_equal():
    hier_env = {"findings": [{"rule_id": "X"}]}
    nohier_env = {"findings": [{"rule_id": "X"}]}
    v, _ = _check_finding_superset(hier_env, nohier_env)
    assert v == "PASS"


def test_finding_superset_fail_when_hier_drops_rule_id():
    hier_env = {"findings": [{"rule_id": "A"}]}
    nohier_env = {"findings": [{"rule_id": "A"}, {"rule_id": "B"}]}
    v, d = _check_finding_superset(hier_env, nohier_env)
    assert v == "FAIL"
    assert "['B']" in d
    assert "without being in known_suppressions" in d


def test_finding_superset_pass_when_dropped_rule_id_is_declared_suppression():
    """Hierarchy auto-discovery of parent context legitimately resolves
    context-bound findings (e.g., SS-002 'BOM has 1/2 MPNs' when the parent
    BOM completes the picture). Declared suppressions don't trip the gate."""
    hier_env = {"findings": [{"rule_id": "A"}]}
    nohier_env = {"findings": [{"rule_id": "A"}, {"rule_id": "SS-002"}]}
    v, d = _check_finding_superset(
        hier_env, nohier_env, known_suppressions=["SS-002"]
    )
    assert v == "PASS", d
    assert "declared suppressions used: ['SS-002']" in d


def test_finding_superset_fail_when_undeclared_suppression_alongside_declared():
    """Even with one suppression declared, any NEW undeclared suppression
    still trips the gate. Ensures the allowlist is narrow, not a blanket
    'hierarchy may drop anything' loophole."""
    hier_env = {"findings": [{"rule_id": "A"}]}
    nohier_env = {"findings": [
        {"rule_id": "A"}, {"rule_id": "SS-002"}, {"rule_id": "EX-007"},
    ]}
    v, d = _check_finding_superset(
        hier_env, nohier_env, known_suppressions=["SS-002"]
    )
    assert v == "FAIL"
    assert "['EX-007']" in d
    # SS-002 should NOT be in the failure reason — it's the declared one
    assert "SS-002" not in d.split("rule_id(s)")[1].split("that")[0]


def test_finding_superset_fail_when_hier_count_below_expected_minimum():
    """Even when no rule_ids are missing (rule_id check passes), the count
    check must still catch silent drops — e.g., hier emits one finding per
    rule_id while no-hier emits N findings of the same rule_id. Catches the
    'grouping regression' where hier mode collapses duplicates that no-hier
    correctly emitted separately."""
    # All no-hier rule_ids appear in hier (passes the set check); but hier
    # has 1 finding while no-hier has 3 (2 of rule A, 1 of SS-002).
    # Declared SS-002 suppression accounts for 1 → expected_min = 3 - 1 = 2;
    # hier has 1 → FAIL via the count check (not the set check).
    hier_env = {"findings": [{"rule_id": "A"}]}
    nohier_env = {"findings": [
        {"rule_id": "A"}, {"rule_id": "A"}, {"rule_id": "SS-002"},
    ]}
    v, d = _check_finding_superset(
        hier_env, nohier_env, known_suppressions=["SS-002"]
    )
    assert v == "FAIL"
    assert "default-hierarchy findings=1" in d
    assert "expected minimum 2" in d


# ---------------------------------------------------------------------------
# _check_determinism + _strip_volatile + _envelope_hash
# ---------------------------------------------------------------------------

def test_determinism_pass_when_byte_equal():
    env = {"findings": [{"rule_id": "A", "severity": "info"}]}
    v, d = _check_determinism(env, env)
    assert v == "PASS", d


def test_determinism_pass_when_only_volatile_fields_differ():
    """Volatile fields (timestamp, run_id, capability_mode_ref) MUST be
    stripped before the hash comparison. Otherwise every run would FAIL
    determinism just from the timestamp tick."""
    env_a = {
        "findings": [{"rule_id": "A"}],
        "timestamp": "2026-05-16T10:00:00Z",
        "inputs": {"run_id": "abc"},
        "capability_mode_ref": {"run_id": "abc"},
    }
    env_b = {
        "findings": [{"rule_id": "A"}],
        "timestamp": "2026-05-16T10:00:05Z",
        "inputs": {"run_id": "def"},
        "capability_mode_ref": {"run_id": "def"},
    }
    v, _ = _check_determinism(env_a, env_b)
    assert v == "PASS"


def test_determinism_fail_when_findings_order_differs():
    """The whole point of the determinism contract is to catch order-
    dependent emission (e.g., iterating an unsorted set)."""
    env_a = {"findings": [{"rule_id": "A"}, {"rule_id": "B"}]}
    env_b = {"findings": [{"rule_id": "B"}, {"rule_id": "A"}]}
    v, d = _check_determinism(env_a, env_b)
    assert v == "FAIL"
    assert "two consecutive runs produced different envelopes" in d


def test_determinism_fail_when_findings_content_differs():
    env_a = {"findings": [{"rule_id": "A", "severity": "warning"}]}
    env_b = {"findings": [{"rule_id": "A", "severity": "info"}]}
    v, d = _check_determinism(env_a, env_b)
    assert v == "FAIL"
    assert "sha256" in d


def test_strip_volatile_drops_top_level_and_inputs_volatile_keys():
    env = {
        "findings": [],
        "generated_at": "X",
        "timestamp": "Y",
        "ran_at": "Z",
        "capability_mode_ref": {"run_id": "abc"},
        "inputs": {"run_id": "abc", "timestamp": "T", "ran_at": "R", "source_files": ["a.sch"]},
    }
    out = _strip_volatile(env)
    for k in ("generated_at", "timestamp", "ran_at", "capability_mode_ref"):
        assert k not in out, f"top-level {k!r} not stripped"
    for k in ("run_id", "timestamp", "ran_at"):
        assert k not in out["inputs"], f"inputs.{k!r} not stripped"
    # Non-volatile fields preserved
    assert out["inputs"]["source_files"] == ["a.sch"]


def test_strip_volatile_does_not_mutate_input():
    env = {"timestamp": "X", "inputs": {"run_id": "abc"}}
    _ = _strip_volatile(env)
    assert env["timestamp"] == "X"
    assert env["inputs"]["run_id"] == "abc"


def test_envelope_hash_deterministic_for_equivalent_dicts():
    a = {"findings": [{"rule_id": "X", "severity": "info"}]}
    b = {"findings": [{"rule_id": "X", "severity": "info"}]}
    assert _envelope_hash(a) == _envelope_hash(b)


def test_envelope_hash_key_order_independent():
    """sort_keys=True in the hash function should make {a:1,b:2} hash the
    same as {b:2,a:1}."""
    a = {"a": 1, "b": 2}
    b = {"b": 2, "a": 1}
    assert _envelope_hash(a) == _envelope_hash(b)


# ---------------------------------------------------------------------------
# _aggregate
# ---------------------------------------------------------------------------

def test_aggregate_counts_pass_fail_skip():
    records = [
        {"board": "b1", "verdict": "PASS", "contracts": {
            "c1": ("PASS", "ok"), "c2": ("PASS", "ok"),
        }},
        {"board": "b2", "verdict": "FAIL", "contracts": {
            "c1": ("PASS", "ok"), "c2": ("FAIL", "broke"),
        }},
        {"board": "b3", "verdict": "SKIP", "contracts": {
            "setup": ("SKIP", "missing"),
        }},
    ]
    rollup = _aggregate(records)
    assert rollup["summary"]["PASS"] == 1
    assert rollup["summary"]["FAIL"] == 1
    assert rollup["summary"]["SKIP"] == 1
    assert rollup["summary"]["contract_fails"] == {"c2": 1}
    assert set(rollup["boards"]) == {"b1", "b2", "b3"}
    assert rollup["boards"]["b2"]["contracts"]["c2"]["verdict"] == "FAIL"


def test_aggregate_contract_fails_only_counts_fail_records():
    """Contracts that PASS or SKIP on a FAIL board shouldn't be counted as
    contract-level fails — only the FAIL ones should bump the counter."""
    records = [
        {"board": "b1", "verdict": "FAIL", "contracts": {
            "c1": ("PASS", "ok"),
            "c2": ("FAIL", "x"),
            "c3": ("SKIP", "y"),
        }},
    ]
    rollup = _aggregate(records)
    assert rollup["summary"]["contract_fails"] == {"c2": 1}


def test_aggregate_empty_records():
    rollup = _aggregate([])
    assert rollup["summary"]["PASS"] == 0
    assert rollup["summary"]["FAIL"] == 0
    assert rollup["summary"]["SKIP"] == 0
    assert rollup["boards"] == {}


# ---------------------------------------------------------------------------
# _print_summary
# ---------------------------------------------------------------------------

def test_print_summary_says_clean_when_no_failures():
    rollup = {
        "summary": {"PASS": 3, "FAIL": 0, "SKIP": 0, "contract_fails": {}},
        "boards": {
            "b1": {"verdict": "PASS", "contracts": {"c1": {"verdict": "PASS", "detail": ""}}},
        },
    }
    buf = io.StringIO()
    with redirect_stdout(buf):
        _print_summary(rollup)
    out = buf.getvalue()
    assert "CLEAN" in out
    assert "NOT CLEAN" not in out
    assert "PASS=3" in out and "FAIL=0" in out


def test_print_summary_says_not_clean_when_failures_present():
    rollup = {
        "summary": {"PASS": 2, "FAIL": 1, "SKIP": 0, "contract_fails": {"c2": 1}},
        "boards": {
            "b1": {"verdict": "PASS", "contracts": {"c1": {"verdict": "PASS", "detail": "ok"}}},
            "b2": {"verdict": "FAIL", "contracts": {
                "c1": {"verdict": "PASS", "detail": "ok"},
                "c2": {"verdict": "FAIL", "detail": "broke"},
            }},
        },
    }
    buf = io.StringIO()
    with redirect_stdout(buf):
        _print_summary(rollup)
    out = buf.getvalue()
    assert "NOT CLEAN" in out
    assert "1 board(s) failed" in out
    # FAIL boards surface their failing contract in the per-line listing
    assert "c2=FAIL" in out
