"""Lock the contract-check semantics of ``regression/run_v14_default_contract_gate.py``.

Audit LOG 8 / regression-testing-audit F4 (2026-05-15): the v1.4 default-mode
contracts the gate validates need test-suite coverage so future helper
refactors can't silently weaken them. Mirrors the pattern of
``tests/test_v14_gate_criteria.py``: synthetic envelopes, no analyzer runs,
direct call into each ``_check_*`` helper.

Contracts covered (each tested both PASS and FAIL paths):

  * ``_check_summary_integrity``  — total_findings vs len(findings),
    by_severity bucket sums, per-severity counter consistency
  * ``_check_severity_normalized`` — lowercase {error,warning,info} only;
    catches the F1.4 literal ``'WARNING'`` regression class
  * ``_check_run_id_linkage``     — inputs.run_id == capability_mode_ref.run_id
  * ``_check_schema_validates``   — soft-skip when jsonschema/schema absent,
    PASS on valid envelope, FAIL with path on violation

Plus aggregator (``_aggregate``) and printed-summary (``_print_summary``)
contract checks — synthetic records, captured stdout.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from regression.run_v14_default_contract_gate import (  # noqa: E402
    _aggregate,
    _check_run_id_linkage,
    _check_schema_validates,
    _check_severity_normalized,
    _check_summary_integrity,
    _print_summary,
)


# ---------------------------------------------------------------------------
# _check_summary_integrity
# ---------------------------------------------------------------------------

def test_summary_integrity_pass_when_total_matches():
    env = {
        "findings": [{"severity": "error"}, {"severity": "warning"}],
        "summary": {
            "total_findings": 2,
            "by_severity": {"error": 1, "warning": 1, "info": 0},
        },
    }
    v, d = _check_summary_integrity(env)
    assert v == "PASS", d


def test_summary_integrity_fail_when_total_mismatched():
    """Catches the consumer-side bug class where a stale total_findings
    survives a findings[] mutation (and downstream UI shows the wrong
    count)."""
    env = {
        "findings": [{"severity": "info"}],
        "summary": {"total_findings": 3},
    }
    v, d = _check_summary_integrity(env)
    assert v == "FAIL"
    assert "total_findings=3" in d
    assert "len(findings)=1" in d


def test_summary_integrity_fail_when_buckets_dont_sum():
    env = {
        "findings": [{"severity": "warning"}, {"severity": "warning"}],
        "summary": {
            "total_findings": 2,
            "by_severity": {"error": 1, "warning": 2, "info": 0},  # sums to 3
        },
    }
    v, d = _check_summary_integrity(env)
    assert v == "FAIL"
    assert "by_severity" in d


def test_summary_integrity_fail_when_per_sev_count_mismatched():
    """by_severity says 1 error, but findings has 0 — common F1.4-shape
    bug (severity literal mismatch hides findings from the bucket)."""
    env = {
        "findings": [{"severity": "warning"}],
        "summary": {
            "total_findings": 1,
            "by_severity": {"error": 0, "warning": 0, "info": 1},  # warning=0 wrong
        },
    }
    v, d = _check_summary_integrity(env)
    assert v == "FAIL"
    assert "by_severity" in d


def test_summary_integrity_skip_when_summary_absent():
    """Gerber-shape envelopes may omit summary blocks entirely. Skip
    rather than fail — the gate's intent is consistency, not presence."""
    env = {"findings": [{"severity": "info"}]}
    v, d = _check_summary_integrity(env)
    assert v == "SKIP"


# ---------------------------------------------------------------------------
# _check_severity_normalized — locks F1.4 bug class
# ---------------------------------------------------------------------------

def test_severity_normalized_pass_on_all_lowercase():
    env = {"findings": [
        {"severity": "error"},
        {"severity": "warning"},
        {"severity": "info"},
    ]}
    v, d = _check_severity_normalized(env)
    assert v == "PASS"
    assert "3 findings" in d


def test_severity_normalized_fail_on_uppercase_warning():
    """Direct F1.4 lock — literal uppercase ``'WARNING'`` from a producer
    that downstream filters won't match. The 8daa28d commit fixed the
    canonical case; this test catches any new producer that repeats it."""
    env = {"findings": [
        {"rule_id": "RC-DET", "severity": "WARNING"},
        {"rule_id": "OK-001", "severity": "info"},
    ]}
    v, d = _check_severity_normalized(env)
    assert v == "FAIL"
    assert "'WARNING'" in d
    assert "RC-DET" in d


def test_severity_normalized_fail_on_critical():
    """Some legacy producers emit ``'critical'`` (mapped from EMC). The
    v1.4 vocabulary is strict — must be ``error``."""
    env = {"findings": [{"rule_id": "X-001", "severity": "critical"}]}
    v, d = _check_severity_normalized(env)
    assert v == "FAIL"
    assert "critical" in d


def test_severity_normalized_fail_on_none():
    env = {"findings": [{"rule_id": "X-001", "severity": None}]}
    v, d = _check_severity_normalized(env)
    assert v == "FAIL"


def test_severity_normalized_pass_on_empty_findings():
    env = {"findings": []}
    v, d = _check_severity_normalized(env)
    assert v == "PASS"


def test_severity_normalized_caps_sample_at_three():
    """Detail line must stay one-liner-ish for the rollup. Even with
    100 bad findings, only first 3 shown."""
    env = {"findings": [
        {"rule_id": f"X-{i:03d}", "severity": "WARNING"} for i in range(100)
    ]}
    v, d = _check_severity_normalized(env)
    assert v == "FAIL"
    assert "100 finding" in d
    # 3 sample entries — count instances of 'rule=' in detail
    assert d.count("rule=") == 3


# ---------------------------------------------------------------------------
# _check_run_id_linkage — Highest-Risk #5 invariant
# ---------------------------------------------------------------------------

def test_run_id_linkage_pass_when_matched():
    env = {
        "inputs": {"run_id": "20260516T000000Z-abc123"},
        "capability_mode_ref": {
            "source": "analysis/capability_mode.json",
            "run_id": "20260516T000000Z-abc123",
        },
    }
    v, d = _check_run_id_linkage(env)
    assert v == "PASS"


def test_run_id_linkage_fail_when_mismatched():
    """Two analyzers in the same analysis dir each writing their own
    capability_mode would produce mismatched run_ids — the first-writer-wins
    invariant breaks. Catches that class of bug."""
    env = {
        "inputs": {"run_id": "20260516T000000Z-abc123"},
        "capability_mode_ref": {"run_id": "20260516T000001Z-def456"},
    }
    v, d = _check_run_id_linkage(env)
    assert v == "FAIL"
    assert "abc123" in d
    assert "def456" in d


def test_run_id_linkage_fail_when_inputs_run_id_missing():
    env = {
        "capability_mode_ref": {"run_id": "20260516T000000Z-abc123"},
    }
    v, d = _check_run_id_linkage(env)
    assert v == "FAIL"
    assert "inputs.run_id missing" in d


def test_run_id_linkage_fail_when_cmr_run_id_missing():
    env = {
        "inputs": {"run_id": "20260516T000000Z-abc123"},
        "capability_mode_ref": {},
    }
    v, d = _check_run_id_linkage(env)
    assert v == "FAIL"
    assert "capability_mode_ref.run_id missing" in d


def test_run_id_linkage_skip_when_both_absent():
    """Legacy envelopes from before run_id was added — no inputs, no
    capability_mode_ref. Skip rather than fail; this gate doesn't
    retroactively require the field on archived snapshots."""
    env = {"findings": []}
    v, d = _check_run_id_linkage(env)
    assert v == "SKIP"


# ---------------------------------------------------------------------------
# _check_schema_validates — soft-skip + validation paths
# ---------------------------------------------------------------------------

def test_schema_validates_skip_when_no_schema():
    """Soft skip: analyzer's --schema unavailable / failed. Gate should
    surface the gap, not fail the snapshot."""
    v, d = _check_schema_validates({"findings": []}, None)
    assert v == "SKIP"
    assert "no schema" in d


def test_schema_validates_pass_on_conforming():
    schema = {
        "type": "object",
        "required": ["analyzer_type", "findings"],
        "properties": {
            "analyzer_type": {"type": "string"},
            "findings": {"type": "array"},
        },
    }
    env = {"analyzer_type": "schematic", "findings": []}
    v, d = _check_schema_validates(env, schema)
    assert v == "PASS"


def test_schema_validates_fail_on_missing_required():
    schema = {
        "type": "object",
        "required": ["analyzer_type"],
        "properties": {"analyzer_type": {"type": "string"}},
    }
    env = {"findings": []}
    v, d = _check_schema_validates(env, schema)
    assert v == "FAIL"
    assert "analyzer_type" in d


def test_schema_validates_fail_with_path_on_nested_violation():
    """Failure detail MUST name the JSON path of the violation so
    operators can find the offending field without staring at the
    full envelope. Generic 'schema violation' isn't enough."""
    schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "object",
                "properties": {"total_findings": {"type": "integer"}},
            },
        },
    }
    env = {"summary": {"total_findings": "not_an_int"}}
    v, d = _check_schema_validates(env, schema)
    assert v == "FAIL"
    assert "summary.total_findings" in d


def test_schema_validates_skip_on_malformed_schema():
    """If the schema itself is broken, skip rather than fail (the issue
    is the analyzer's --schema output, not the envelope)."""
    bad_schema = {"type": "not_a_valid_type"}
    v, d = _check_schema_validates({"findings": []}, bad_schema)
    assert v == "SKIP"


# ---------------------------------------------------------------------------
# _aggregate — rollup bucket structure
# ---------------------------------------------------------------------------

def _rec(analyzer="schematic", repo="a/b", identity="a/b/x.kicad_sch",
         verdict="PASS", contract_fails=None):
    contracts = {
        "summary_integrity": ("PASS", "ok"),
        "severity_normalized": ("PASS", "ok"),
        "run_id_linkage": ("PASS", "ok"),
        "schema_validates": ("PASS", "ok"),
    }
    if contract_fails:
        for k in contract_fails:
            contracts[k] = ("FAIL", f"forced-fail-{k}")
    return {
        "analyzer": analyzer, "repo": repo, "identity": identity,
        "snap_path": f"/tmp/{identity}",
        "verdict": verdict, "contracts": contracts,
    }


def test_aggregate_buckets_per_analyzer():
    records = [
        _rec(analyzer="schematic", verdict="PASS"),
        _rec(analyzer="schematic", verdict="FAIL",
             contract_fails=["severity_normalized"]),
        _rec(analyzer="pcb", verdict="PASS"),
        _rec(analyzer="pcb", verdict="SKIP"),
    ]
    out = _aggregate(records)
    assert out["by_analyzer"]["schematic"]["PASS"] == 1
    assert out["by_analyzer"]["schematic"]["FAIL"] == 1
    assert out["by_analyzer"]["pcb"]["PASS"] == 1
    assert out["by_analyzer"]["pcb"]["SKIP"] == 1
    assert out["corpus"]["PASS"] == 2
    assert out["corpus"]["FAIL"] == 1


def test_aggregate_counts_contract_fails_by_name():
    """corpus.contract_fails MUST tell operators which contract is biting,
    not just count overall failures."""
    records = [
        _rec(verdict="FAIL", contract_fails=["severity_normalized"]),
        _rec(verdict="FAIL", contract_fails=["severity_normalized"]),
        _rec(verdict="FAIL", contract_fails=["run_id_linkage"]),
    ]
    out = _aggregate(records)
    assert out["corpus"]["contract_fails"]["severity_normalized"] == 2
    assert out["corpus"]["contract_fails"]["run_id_linkage"] == 1


def test_aggregate_caps_fail_repos_at_20():
    """fail_repos list is a sample for operator triage, not exhaustive.
    Bounded at 20 per analyzer."""
    records = [
        _rec(identity=f"a/b/{i}.kicad_sch", verdict="FAIL",
             contract_fails=["severity_normalized"])
        for i in range(50)
    ]
    out = _aggregate(records)
    assert len(out["by_analyzer"]["schematic"]["fail_repos"]) == 20


# ---------------------------------------------------------------------------
# _print_summary — operator-facing text
# ---------------------------------------------------------------------------

def _summary_text(records):
    rollup = _aggregate(records)
    buf = io.StringIO()
    with redirect_stdout(buf):
        _print_summary(rollup)
    return buf.getvalue()


def test_print_summary_clean_says_so():
    out = _summary_text([_rec(verdict="PASS"), _rec(verdict="PASS")])
    assert "CLEAN" in out
    assert "NOT CLEAN" not in out


def test_print_summary_not_clean_when_any_fail():
    out = _summary_text([
        _rec(verdict="PASS"),
        _rec(verdict="FAIL", contract_fails=["severity_normalized"]),
    ])
    assert "NOT CLEAN" in out
    assert "1 snapshots" in out


def test_print_summary_lists_contract_fails_inline():
    """Per-analyzer line must call out which contracts failed by name
    so the operator knows which bug class to chase."""
    out = _summary_text([
        _rec(analyzer="emc", verdict="FAIL",
             contract_fails=["severity_normalized"]),
    ])
    assert "emc" in out
    assert "severity_normalized" in out
