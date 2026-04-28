"""B1+B2 regression tests for capability_mode_ref + finding_id invariants.

Implements the four absorption asks from main-repo LOG entry #68:
  (a) capability_mode_ref top-level envelope field present + well-shaped
  (b) finding_id allowed on findings (additive, optional in v1.4)
  (c) every make_finding-produced finding has a finding_id matching the
      Phase 4 spec §3.2 pattern: {source}:{detection_id} or
      {source}:{rule_id}:{locator|hash}
  (d) make_finding determinism — same inputs produce identical finding_id
      across re-runs

Coverage scope per #68: HI-5 partial coverage. Many raw-dict findings
(all pcb/thermal/emc analyzers, most schematic detectors) bypass
make_finding and lack finding_id at v1.4. Tests assert the property
ONLY for findings that carry finding_id; v1.5 migration tightens.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tests"))

from fixtures._build_sch import Schematic, pin1, pin2

KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_PYTHON = KH_DIR / ".venv" / "bin" / "python"
ANALYZER = KH_DIR / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
FINDING_SCHEMA_DIR = KH_DIR / "skills" / "kicad" / "scripts"


def _python() -> str:
    """Pick kicad-happy venv python if present (provides jsonschema)."""
    return str(KH_PYTHON) if KH_PYTHON.exists() else sys.executable


def _import_make_finding():
    """Import make_finding from kicad-happy. Returns None if unavailable."""
    if not ANALYZER.exists():
        return None
    if str(FINDING_SCHEMA_DIR) not in sys.path:
        sys.path.insert(0, str(FINDING_SCHEMA_DIR))
    try:
        from finding_schema import make_finding
        return make_finding
    except ImportError:
        return None


def _run_analyzer_synthetic() -> dict | None:
    """Build a small synthetic schematic, run analyzer, return envelope."""
    if not ANALYZER.exists():
        return None
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 62))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 72))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), pin1(50, 62))
        .wire(pin2(50, 62), (50, 72))
    )
    with tempfile.TemporaryDirectory() as tmp:
        sch_path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        out_path = str(Path(tmp) / "out.json")
        proc = subprocess.run(
            [_python(), str(ANALYZER), sch_path, "--output", out_path],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            raise AssertionError(f"analyzer failed: {proc.stderr[:300]}")
        return json.loads(Path(out_path).read_text())


_FINDING_ID_PATTERN = re.compile(
    r"^[a-z_][a-z0-9_]*:"     # source
    r"[A-Z]+-\d+"              # rule_id like AM-001
    r"(?::[A-Za-z0-9_\-./+]+)?$"  # optional locator/hash; OR detection_id form
    # OR: source:detection_id (free-form detection_id) — looser fallback below
)
# Looser pattern for detection_id form (no rule_id segment).
_FINDING_ID_DETECTION_PATTERN = re.compile(
    r"^[a-z_][a-z0-9_]*:[A-Za-z0-9_\-./+]+$")


def _matches_finding_id_pattern(fid: str) -> bool:
    """True if fid matches either {source}:{detection_id} or
    {source}:{rule_id}:{locator|hash} per Phase 4 spec §3.2."""
    return bool(_FINDING_ID_PATTERN.match(fid)
                or _FINDING_ID_DETECTION_PATTERN.match(fid))


# ─── (a) capability_mode_ref envelope field ────────────────────────────────

def test_capability_mode_ref_present_in_envelope():
    """Schematic envelope carries top-level capability_mode_ref (Phase 4a)."""
    env = _run_analyzer_synthetic()
    if env is None:
        print("  SKIP: kicad-happy not available")
        return
    assert "capability_mode_ref" in env, \
        f"capability_mode_ref missing from envelope keys: {sorted(env.keys())[:10]}..."


def test_capability_mode_ref_shape():
    """capability_mode_ref has {source, run_id} shape with non-empty values."""
    env = _run_analyzer_synthetic()
    if env is None:
        print("  SKIP")
        return
    cmr = env["capability_mode_ref"]
    assert isinstance(cmr, dict), f"expected dict, got {type(cmr).__name__}"
    assert "source" in cmr and "run_id" in cmr, \
        f"capability_mode_ref keys: {sorted(cmr.keys())}"
    assert cmr["source"], "source is empty"
    assert cmr["run_id"], "run_id is empty"
    assert cmr["source"].endswith("capability_mode.json"), \
        f"source should reference capability_mode.json, got {cmr['source']!r}"


def test_capability_mode_ref_run_id_format():
    """run_id matches sortable format: YYYYMMDDTHHMMSSZ-<6hex>."""
    env = _run_analyzer_synthetic()
    if env is None:
        print("  SKIP")
        return
    run_id = env["capability_mode_ref"]["run_id"]
    assert re.match(r"^\d{8}T\d{6}Z-[0-9a-f]{6,}$", run_id), \
        f"run_id format unexpected: {run_id!r}"


# ─── (b) finding_id allowed on findings ────────────────────────────────────

def test_finding_id_allowed_in_finding_schema():
    """analyze_schematic --schema declares finding_id as optional on Finding."""
    if not ANALYZER.exists():
        print("  SKIP: analyzer not available")
        return
    proc = subprocess.run(
        [_python(), str(ANALYZER), "--schema"],
        capture_output=True, text=True, timeout=20,
    )
    assert proc.returncode == 0, f"--schema failed: {proc.stderr[:300]}"
    schema = json.loads(proc.stdout)
    findings_items = (schema.get("properties", {})
                       .get("findings", {})
                       .get("items", {}))
    finding_props = findings_items.get("properties") or {}
    assert "finding_id" in finding_props, \
        f"finding_id not declared on Finding; keys: {sorted(finding_props.keys())[:8]}"
    # Optional, not required
    assert "finding_id" not in findings_items.get("required", []), \
        "finding_id must be OPTIONAL on Finding in v1.4 (HI-5 partial coverage)"


# ─── (c) finding_id pattern compliance for findings that carry it ──────────

def test_make_finding_emits_finding_id_with_components():
    """make_finding(components=[...]) → {source}:{rule_id}:{component}."""
    mf = _import_make_finding()
    if mf is None:
        print("  SKIP: make_finding not importable")
        return
    f = mf(
        detector="detect_test", rule_id="AM-001",
        category="testing", summary="test summary",
        description="test description",
        components=["R1"], source="schematic",
    )
    assert "finding_id" in f
    assert f["finding_id"] == "schematic:AM-001:r1", \
        f"unexpected finding_id: {f['finding_id']!r}"
    assert _matches_finding_id_pattern(f["finding_id"])


def test_make_finding_emits_finding_id_with_detection_id():
    """make_finding(detection_id=X) → {source}:{detection_id}."""
    mf = _import_make_finding()
    if mf is None:
        print("  SKIP")
        return
    f = mf(
        detector="detect_test", rule_id="AM-001",
        category="testing", summary="test", description="test",
        source="schematic", detection_id="custom_detection_42",
    )
    assert f["finding_id"] == "schematic:custom_detection_42", \
        f"unexpected: {f['finding_id']!r}"
    assert _matches_finding_id_pattern(f["finding_id"])


def test_make_finding_emits_finding_id_with_summary_hash_fallback():
    """No locators → {source}:{rule_id}:{12-hex-hash} fallback."""
    mf = _import_make_finding()
    if mf is None:
        print("  SKIP")
        return
    f = mf(
        detector="detect_test", rule_id="AM-001",
        category="testing", summary="some specific summary text",
        description="test", source="schematic",
    )
    fid = f["finding_id"]
    assert fid.startswith("schematic:AM-001:"), f"unexpected: {fid!r}"
    locator = fid.split(":", 2)[2]
    # Hash form is 12 hex chars
    assert re.match(r"^[0-9a-f]{12}$", locator), \
        f"expected hash locator, got {locator!r}"
    assert _matches_finding_id_pattern(fid)


def test_finding_id_pattern_in_corpus_envelope():
    """Any finding in the synthetic envelope that carries finding_id matches
    the spec pattern. v1.4 partial-coverage scope: many findings will lack
    finding_id; that's expected and not a failure."""
    env = _run_analyzer_synthetic()
    if env is None:
        print("  SKIP")
        return
    findings = env.get("findings") or []
    with_id = [f for f in findings if f.get("finding_id")]
    bad = [(f.get("detector"), f["finding_id"]) for f in with_id
           if not _matches_finding_id_pattern(f["finding_id"])]
    assert not bad, f"finding_id pattern violations: {bad}"


# ─── (d) determinism ───────────────────────────────────────────────────────

def test_make_finding_is_deterministic():
    """Same inputs produce identical finding_id across calls."""
    mf = _import_make_finding()
    if mf is None:
        print("  SKIP")
        return
    kwargs = dict(
        detector="detect_test", rule_id="AM-001",
        category="testing", summary="determinism check",
        description="test", source="schematic",
        components=["U1", "U2"],
    )
    f1 = mf(**kwargs)
    f2 = mf(**kwargs)
    assert f1["finding_id"] == f2["finding_id"], \
        f"non-deterministic: {f1['finding_id']!r} != {f2['finding_id']!r}"


def test_finding_id_set_stable_across_analyzer_runs():
    """Re-running analyzer on the same synthetic schematic produces the same
    set of finding_ids (filtered to make_finding-produced ones).

    HI-5 partial-coverage: only findings that already carry finding_id
    participate. Empty set on both runs is acceptable (synthetic fixture
    doesn't trigger any make_finding-produced detector at v1.4)."""
    env1 = _run_analyzer_synthetic()
    env2 = _run_analyzer_synthetic()
    if env1 is None or env2 is None:
        print("  SKIP")
        return
    ids1 = {f["finding_id"] for f in env1.get("findings", [])
            if f.get("finding_id")}
    ids2 = {f["finding_id"] for f in env2.get("findings", [])
            if f.get("finding_id")}
    assert ids1 == ids2, \
        f"finding_id set divergence across runs: {ids1 ^ ids2}"


# Custom-runner __main__ block (harness convention)
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
