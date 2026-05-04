"""B5 absorption — Phase 4b + 4c detector invariants.

Per main-repo handoff (LOG #74 deferred → 2026-05-03 prompt). Combined
batch covering 11 detectors:

  4b (validation_detectors.py): PU-001, LR-001, XT-001, FS-001, VM-001
  4c (lookup_detectors.py): AM-001, OV-001, TJ-001, FT-001, PM-001, EX-001

Asks (a)/(b)/(c) covered here. Path A scope per harness 2026-05-03 reply:
ask (d) — datasheet-branch activation gated on AnalysisContext.cache_dir
wiring — defers to a follow-up file once Phase 4d-active lands the
cache_dir + design_context fields on the AnalysisContext dataclass. Per-rule
fire-shape fixtures (AM-001 known-violation board, etc.) defer with (d) —
they require real cache wiring to fire.

Tested here:
  (a) Every make_finding(...) call inside the 11 detector functions tags
      schema_era="v1.4" at the top level (NOT under extra). AST-walk catches
      regressions if a future emit-site forgets the tag.
  (b) make_finding enum tightening — confidence + evidence_source rejected
      with ValueError on values outside the published vocabularies.
  (c) XT-001 emission gate — frequency_default suppression. The detector
      fires for status in {out_of_spec, marginal} and silent for {ok,
      unverified}; a finding sourced from frequency_default is NOT tagged
      datasheet-backed.
"""
from __future__ import annotations

TIER = "unit"

import ast
import os
import sys
from pathlib import Path
from types import SimpleNamespace

HARNESS_DIR = Path(__file__).resolve().parent.parent
KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_SCRIPTS = KH_DIR / "skills" / "kicad" / "scripts"
KH_DS_SCRIPTS = KH_DIR / "skills" / "datasheets" / "scripts"
VALIDATION_DETECTORS = KH_SCRIPTS / "validation_detectors.py"
LOOKUP_DETECTORS = KH_SCRIPTS / "lookup_detectors.py"

# Map rule_id → owning detector function (for AST-walk scope context).
# Helper functions (e.g., _make_ex_001 for EX-001) are reachable via the
# rule_id kwarg, so we filter by rule_id rather than enclosing function.
_RULE_IDS = (
    "PU-001", "VM-001", "LR-001", "XT-001", "FS-001",
    "AM-001", "OV-001", "TJ-001", "FT-001", "PM-001", "EX-001",
)

_MISSING = object()


def _import_make_finding():
    """Import make_finding from kicad-happy. Returns None if unavailable."""
    if not (KH_SCRIPTS / "finding_schema.py").exists():
        return None
    if str(KH_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(KH_SCRIPTS))
    try:
        from finding_schema import make_finding
        return make_finding
    except ImportError:
        return None


def _import_validate_crystal_load_caps():
    """Import validate_crystal_load_caps. Returns None if dep chain breaks."""
    if not VALIDATION_DETECTORS.exists():
        return None
    if str(KH_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(KH_SCRIPTS))
    if KH_DS_SCRIPTS.exists() and str(KH_DS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(KH_DS_SCRIPTS))
    try:
        from validation_detectors import validate_crystal_load_caps
        return validate_crystal_load_caps
    except ImportError:
        return None


def _collect_make_finding_calls(path: Path) -> list[ast.Call]:
    """Return every ast.Call node in `path` whose func is named 'make_finding'."""
    tree = ast.parse(path.read_text())
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == "make_finding":
                calls.append(node)
    return calls


def _kwarg_constant(call: ast.Call, key: str):
    """Return the constant value of kwarg `key`, or _MISSING sentinel."""
    for kw in call.keywords:
        if kw.arg == key and isinstance(kw.value, ast.Constant):
            return kw.value.value
    return _MISSING


# ---------------------------------------------------------------------------
# (a) schema_era tagging — every emit site for the 11 detectors carries v1.4
# ---------------------------------------------------------------------------

def test_all_4b_4c_detectors_tag_schema_era_v14():
    """Every make_finding call binding rule_id to one of the 11 4b/4c rules
    must include schema_era='v1.4' as a constant kwarg.

    AST-walks both validation_detectors.py and lookup_detectors.py, filters
    calls whose rule_id constant matches, asserts schema_era is present and
    equals 'v1.4'. Fails if a detector emit site forgets or downgrades the
    tag.
    """
    if not VALIDATION_DETECTORS.exists() or not LOOKUP_DETECTORS.exists():
        return  # silent skip — kicad-happy not present

    calls = _collect_make_finding_calls(VALIDATION_DETECTORS) + \
            _collect_make_finding_calls(LOOKUP_DETECTORS)

    failures = []
    missing_rules = []
    for rule_id in _RULE_IDS:
        matching = [c for c in calls if _kwarg_constant(c, "rule_id") == rule_id]
        if not matching:
            missing_rules.append(rule_id)
            continue
        for call in matching:
            era = _kwarg_constant(call, "schema_era")
            if era != "v1.4":
                failures.append(
                    f"{rule_id} make_finding at line {call.lineno}: "
                    f"schema_era={era!r} (expected 'v1.4')")

    assert not missing_rules, (
        f"No make_finding calls found for rules: {missing_rules}. "
        f"Emit sites may have moved or been refactored away.")
    assert not failures, (
        "Detectors with missing/wrong schema_era tag (Phase 4 spec §3.4):\n"
        + "\n".join("  " + f for f in failures))


def test_schema_era_lands_at_top_level_not_in_extra():
    """Sanity: schema_era passed via **kwargs lands at finding[top-level],
    not nested under finding['extra'] or similar. Phase 4b convention per
    LOG #74; main-repo wording was loose ('NOT nested under extra')."""
    make_finding = _import_make_finding()
    if make_finding is None:
        return  # silent skip

    finding = make_finding(
        detector="detect_absolute_max_violations",
        rule_id="AM-001",
        category="electrical_safety",
        summary="dummy",
        description="dummy",
        severity="error",
        confidence="datasheet-backed",
        evidence_source="datasheet",
        source="schematic",
        schema_era="v1.4",
    )
    assert finding["schema_era"] == "v1.4", \
        "schema_era should be at the top level of the finding dict"
    assert "extra" not in finding or "schema_era" not in finding.get("extra", {}), \
        "schema_era must not be nested under 'extra'"


# ---------------------------------------------------------------------------
# (b) confidence + evidence_source enum tightening
# ---------------------------------------------------------------------------

def test_make_finding_rejects_invalid_confidence():
    """make_finding must raise ValueError on confidence outside
    VALID_CONFIDENCES = ('deterministic', 'heuristic', 'datasheet-backed').
    Catches drift if a detector starts emitting bogus confidence values."""
    make_finding = _import_make_finding()
    if make_finding is None:
        return

    try:
        make_finding(
            detector="x", rule_id="X-001", category="x",
            summary="x", description="x",
            confidence="bogus_value",
            evidence_source="datasheet",
            source="schematic",
        )
    except ValueError as e:
        assert "invalid confidence" in str(e), \
            f"Expected 'invalid confidence' in error message, got: {e}"
        return
    raise AssertionError(
        "make_finding accepted invalid confidence='bogus_value'; "
        "expected ValueError")


def test_make_finding_rejects_invalid_evidence_source():
    """make_finding must raise ValueError on evidence_source outside
    VALID_EVIDENCE_SOURCES vocabulary."""
    make_finding = _import_make_finding()
    if make_finding is None:
        return

    try:
        make_finding(
            detector="x", rule_id="X-001", category="x",
            summary="x", description="x",
            confidence="datasheet-backed",
            evidence_source="bogus_value",
            source="schematic",
        )
    except ValueError as e:
        assert "invalid evidence_source" in str(e), \
            f"Expected 'invalid evidence_source' in error message, got: {e}"
        return
    raise AssertionError(
        "make_finding accepted invalid evidence_source='bogus_value'; "
        "expected ValueError")


def test_make_finding_accepts_datasheet_backed_combo():
    """The (confidence='datasheet-backed', evidence_source='datasheet')
    combo used by all 6 4c detectors must be accepted and round-trip into
    the finding dict at the top level."""
    make_finding = _import_make_finding()
    if make_finding is None:
        return

    finding = make_finding(
        detector="detect_absolute_max_violations",
        rule_id="AM-001",
        category="electrical_safety",
        summary="dummy",
        description="dummy",
        severity="error",
        confidence="datasheet-backed",
        evidence_source="datasheet",
        source="schematic",
        schema_era="v1.4",
    )
    assert finding["confidence"] == "datasheet-backed"
    assert finding["evidence_source"] == "datasheet"
    assert finding["schema_era"] == "v1.4"
    assert finding["severity"] == "error"


# ---------------------------------------------------------------------------
# (c) XT-001 emission gate — fires only on out_of_spec / marginal,
#                            frequency_default does NOT carry datasheet-backed
# ---------------------------------------------------------------------------

def _make_xc(status, *, target_load_source="datasheet", reference="Y1"):
    """Build a minimal crystal_circuits dict matching detect_crystal_circuits
    output shape for XT-001 input."""
    return {
        "reference": reference,
        "load_cap_status": status,
        "target_load_source": target_load_source,
        "effective_load_pF": 18.0,
        "target_load_pF": 18.0,
        "load_cap_error_pct": 0.0,
        "load_caps": [
            {"ref": "C1", "net": "XTAL_IN"},
            {"ref": "C2", "net": "XTAL_OUT"},
        ],
    }


def _make_ctx():
    """Minimal duck-typed AnalysisContext stand-in. XT-001 reads only
    ctx.source and getattr(ctx, 'design_context', None)."""
    return SimpleNamespace(source="schematic")


def test_xt_001_silent_when_status_ok():
    """XT-001 must NOT emit findings for load_cap_status='ok'."""
    fn = _import_validate_crystal_load_caps()
    if fn is None:
        return
    findings = fn(_make_ctx(), [_make_xc("ok")])
    assert findings == [], \
        f"XT-001 must be silent for status='ok'; got {len(findings)} findings."


def test_xt_001_silent_when_status_unverified():
    """XT-001 must NOT emit findings for load_cap_status='unverified'."""
    fn = _import_validate_crystal_load_caps()
    if fn is None:
        return
    findings = fn(_make_ctx(), [_make_xc("unverified")])
    assert findings == [], (
        f"XT-001 must be silent for status='unverified'; got "
        f"{len(findings)} findings.")


def test_xt_001_fires_datasheet_backed_when_out_of_spec_with_datasheet_source():
    """When status='out_of_spec' AND target_load_source='datasheet',
    XT-001 fires with confidence='datasheet-backed', evidence_source='datasheet'."""
    fn = _import_validate_crystal_load_caps()
    if fn is None:
        return
    findings = fn(
        _make_ctx(),
        [_make_xc("out_of_spec", target_load_source="datasheet")])
    assert len(findings) == 1
    f = findings[0]
    assert f["rule_id"] == "XT-001"
    assert f["confidence"] == "datasheet-backed"
    assert f["evidence_source"] == "datasheet"
    assert f["schema_era"] == "v1.4"
    assert f["severity"] == "warning"


def test_xt_001_frequency_default_not_datasheet_backed():
    """Emission gate (per main-repo ask c): when target_load_source is
    'frequency_default' (analyzer's fallback when datasheet didn't publish
    load_cap), the finding fires but is NOT tagged datasheet-backed.
    Catches regression where the routing forgets to demote confidence
    away from a frequency-default fallback."""
    fn = _import_validate_crystal_load_caps()
    if fn is None:
        return
    findings = fn(
        _make_ctx(),
        [_make_xc("out_of_spec", target_load_source="frequency_default")])
    assert len(findings) == 1
    f = findings[0]
    assert f["rule_id"] == "XT-001"
    assert f["confidence"] != "datasheet-backed", (
        "XT-001 must not claim datasheet-backed confidence when target "
        "load source is the analyzer's frequency_default fallback.")
    assert f["confidence"] == "heuristic"
    assert f["evidence_source"] == "topology"


def test_xt_001_marginal_fires_as_info():
    """status='marginal' fires with severity='info' (vs 'warning' for
    out_of_spec). Confirms the severity routing matches the docstring."""
    fn = _import_validate_crystal_load_caps()
    if fn is None:
        return
    findings = fn(
        _make_ctx(),
        [_make_xc("marginal", target_load_source="datasheet")])
    assert len(findings) == 1
    assert findings[0]["severity"] == "info"
    assert findings[0]["rule_id"] == "XT-001"


# ---------------------------------------------------------------------------
# Custom-runner __main__ block (harness convention)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback
    fn_names = sorted(n for n, v in globals().items()
                      if n.startswith("test_") and callable(v))
    failed = 0
    passed = 0
    for n in fn_names:
        try:
            globals()[n]()
            print(f"PASS {n}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {n}: {e}")
            failed += 1
        except Exception as e:
            print(f"FAIL {n}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"{passed} passed, {failed} failed ({len(fn_names)} total)")
    sys.exit(0 if failed == 0 else 1)
