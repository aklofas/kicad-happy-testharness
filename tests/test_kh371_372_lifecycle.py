"""
KH-371 + KH-372: LC-ACT provenance fields and honest LC-005 source accounting.

KH-371: the LC-ACT branch of audit_bom (the "component is active" finding,
and the LCSC-only "unknown" carve-out that reuses it) omitted `confidence`/
`evidence_source` entirely. compute_trust_summary() counts any finding whose
`confidence` isn't one of VALID_CONFIDENCES as `unknown_confidence`, which
forces `trust_level` to "low" — so a BOM of nothing but active parts (or an
LCSC-only run, where every part is genuinely 'unknown') reported low trust
for no real reason. The LCSC-only branch also reused the literal "active"
wording in its summary even though the part's status is 'unknown' — LCSC
(jlcsearch) exposes no lifecycle status field at all.

KH-372: LC-005 (single-source) computed its denominator from only the
sources that *responded* (`len(finding['sources'])`), so 3 errored/timed-out
sources silently vanished from the count instead of counting against
confidence. It also treated a source that responded with `status=None` as
if it had confirmed the part active (`in ('active', 'Active', None)`), and
it counted LCSC — which never carries a lifecycle status field — as if it
were a real lifecycle source.

Offline only: audit_component (the network-calling function) is
monkeypatched per test so no real distributor API is ever called.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import lifecycle_audit  # noqa: E402


def _analysis(mpn="TPS61023DRLR", ref="U1"):
    return {"bom": [{"references": [ref], "mpn": mpn, "type": "ic"}]}


def _lc_act_finding(result):
    acts = [f for f in result["findings"] if f["rule_id"] == "LC-ACT"]
    assert len(acts) == 1, result["findings"]
    return acts[0]


def _lc005_findings(result):
    return [f for f in result["findings"] if f["rule_id"] == "LC-005"]


# --- (a) active part: LC-ACT carries confidence + evidence_source ----------

def test_lc_act_active_part_carries_provenance(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        return {"mpn": mpn, "status": "active",
                "sources": {"digikey": {"status": "Active"}},
                "attempted": ["digikey"],
                "per_source_status": {"digikey": "active"}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=["digikey"], delay=0)
    finding = _lc_act_finding(result)
    # Must match the sibling LC-001..004 convention exactly (lifecycle_audit.py
    # rule_info branch): confidence='deterministic', evidence_source='api_lookup'.
    assert finding["confidence"] == "deterministic"
    assert finding["evidence_source"] == "api_lookup"
    assert "active" in finding["summary"]


# --- (b) LCSC-only unknown: summary says unknown, not active ---------------

def test_lc_act_lcsc_only_unknown_summary(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        return {"mpn": mpn, "status": "unknown",
                "sources": {"lcsc": {"stock_qty": 100}},
                "attempted": ["lcsc"],
                "per_source_status": {}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=["lcsc"], delay=0)
    finding = _lc_act_finding(result)
    assert "unknown" in finding["summary"]
    assert "LCSC returns no lifecycle status" in finding["summary"]
    assert "active" not in finding["summary"]
    # Still gets real provenance now (KH-371), even on the LCSC-only path.
    assert finding["confidence"] == "deterministic"
    assert finding["evidence_source"] == "api_lookup"


# --- (c) 4 attempted, 1 responded-active, 3 errored: no LC-005 finding -----

def test_lc005_no_finding_when_denominator_is_mostly_errors(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        # digikey responded active; mouser, element14, lcsc all errored/
        # timed out and never made it into "sources" at all (mirrors the
        # real audit_component's except-continue behavior).
        return {"mpn": mpn, "status": "active",
                "sources": {"digikey": {"status": "Active"}},
                "attempted": ["digikey", "mouser", "element14", "lcsc"],
                "per_source_status": {"digikey": "active"}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=[], delay=0)
    # Old code's denominator was len(finding['sources']) == 1 responded
    # source, so 1 >= 2 was False anyway here by coincidence -- the real
    # regression this guards is that the denominator must come from
    # ATTEMPTED sources, not just responded ones, so errored sources count
    # against confidence rather than disappearing. See the attempted-vs-
    # responded assertions in the other LC-005 tests below for that half.
    assert _lc005_findings(result) == []


# --- (d) status=None does not count as active ------------------------------

def test_lc005_none_status_not_counted_active(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        # digikey confirms active; mouser responded but with status=None.
        # The OLD code's `src_data.get('status') in ('active', 'Active',
        # None)` check treated mouser's None as an active confirmation too,
        # so it saw 2 "active" sources and did NOT flag single-source. The
        # fixed code only trusts explicit active statuses (per_source_status,
        # which the real audit_component only populates from a truthy raw
        # status), sees exactly 1 confirmed-active source out of 2 responses,
        # and correctly fires.
        return {"mpn": mpn, "status": "active",
                "sources": {"digikey": {"status": "Active"},
                            "mouser": {"status": None}},
                "attempted": ["digikey", "mouser"],
                "per_source_status": {"digikey": "active"}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=[], delay=0)
    lc005 = _lc005_findings(result)
    assert len(lc005) == 1
    assert lc005[0]["source_name"] == "digikey"


# --- (e) LCSC excluded from the lifecycle denominator, labeled stock-only --

def test_lc005_excludes_lcsc_and_names_attempted_vs_responded(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        # digikey confirms active; mouser responds but with no status;
        # lcsc responds with stock data only (no lifecycle status, ever).
        # Without the LCSC exclusion, lcsc would inflate both the attempted
        # and responded counts even though it can never confirm or deny
        # lifecycle status.
        return {"mpn": mpn, "status": "active",
                "sources": {"digikey": {"status": "Active"},
                            "mouser": {"status": None},
                            "lcsc": {"stock_qty": 50}},
                "attempted": ["digikey", "mouser", "lcsc"],
                "per_source_status": {"digikey": "active"}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=[], delay=0)
    lc005 = _lc005_findings(result)
    assert len(lc005) == 1
    finding = lc005[0]
    assert finding["source_name"] == "digikey"
    # lcsc excluded from both counts: 2 attempted (digikey, mouser), not 3.
    assert finding["total_attempted"] == 2
    assert finding["responded"] == 2
    assert "2 attempted" in finding["description"]
    assert "2 responded" in finding["description"]
    # ... but its presence is still called out, not silently dropped.
    assert "stock-only source" in finding["description"]


# --- Step 4: trust_summary check --------------------------------------------

def test_trust_summary_zero_unknown_confidence_for_lc_act_only(monkeypatch):
    def _mock(mpn, sources, project_dir=None, delay=1.0):
        return {"mpn": mpn, "status": "active",
                "sources": {"digikey": {"status": "Active"}},
                "attempted": ["digikey"],
                "per_source_status": {"digikey": "active"}}

    monkeypatch.setattr(lifecycle_audit, "audit_component", _mock)
    result = lifecycle_audit.audit_bom(_analysis(), sources=["digikey"], delay=0)
    assert result["findings"]
    assert all(f["rule_id"] == "LC-ACT" for f in result["findings"])
    trust_summary = result["trust_summary"]
    assert trust_summary.get("unknown_confidence", 0) == 0
    assert trust_summary["trust_level"] != "low"
