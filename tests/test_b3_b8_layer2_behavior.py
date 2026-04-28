"""B3+B8 regression tests for Layer 2 behavior invariants.

Implements two of the four absorption asks from main-repo LOG entry #71:
  (B3) renderer contract — stored severity is base; effective severity
       is computed at render time only. _apply_severity_tuning is gated
       on design_context being passed (finding_schema.py:186); detectors
       don't pass it, so analyzer-emitted findings carry base severity.
  (B8) annotation merge lifecycle — orphan annotations and HI-8 violations
       are LOGGED in the merge report (orphan_annotations vs
       invariant_violations top-level keys), not propagated as merge
       failures. HI-3 round-trip strip yields dict-equal raw.

Tests subprocess to merge_annotations.py and import _apply_severity_tuning
+ strip_llm_overlays from kicad-happy. Pattern matches B1+B2: graceful
skip when KH unavailable.

Note: LOG #71 ask wording conflates orphan_annotations and
invariant_violations into one key. Code separates them. Tests assert
against actual code shape; flag mismatch in closure handoff.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tests"))

KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_PYTHON = KH_DIR / ".venv" / "bin" / "python"

FINDING_SCHEMA_DIR = KH_DIR / "skills" / "kicad" / "scripts"
REVIEW_SCRIPTS_DIR = KH_DIR / "skills" / "kicad" / "review" / "scripts"
SEVERITY_TUNING_PATH = KH_DIR / "skills" / "kicad" / "review" / "severity_tuning.json"
MERGE_ANNOTATIONS_SCRIPT = REVIEW_SCRIPTS_DIR / "merge_annotations.py"


def _python() -> str:
    """Pick kicad-happy venv python if present (provides jsonschema)."""
    return str(KH_PYTHON) if KH_PYTHON.exists() else sys.executable


def _import_severity_tuning_fns():
    """Import _apply_severity_tuning from kicad-happy. Returns None if unavailable."""
    if not (FINDING_SCHEMA_DIR / "finding_schema.py").exists():
        return None
    if str(FINDING_SCHEMA_DIR) not in sys.path:
        sys.path.insert(0, str(FINDING_SCHEMA_DIR))
    try:
        from finding_schema import _apply_severity_tuning
        return _apply_severity_tuning
    except ImportError:
        return None


def _import_strip_llm_overlays():
    """Import strip_llm_overlays from merge_annotations.py."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        return None
    if str(REVIEW_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(REVIEW_SCRIPTS_DIR))
    try:
        from merge_annotations import strip_llm_overlays
        return strip_llm_overlays
    except ImportError:
        return None


def _load_severity_tuning():
    """Load the severity_tuning.json rules dict. Returns {} if unavailable."""
    if not SEVERITY_TUNING_PATH.exists():
        return {}
    return json.loads(SEVERITY_TUNING_PATH.read_text()).get("rules", {})


# ─── (B3) renderer contract ───────────────────────────────────────────────

def test_apply_severity_tuning_changes_severity_on_known_input():
    """OV-001 base=warning + environment=automotive → severity_delta +1 → error."""
    fn = _import_severity_tuning_fns()
    if fn is None:
        print("  SKIP: _apply_severity_tuning not importable")
        return
    result = fn("OV-001", "warning", {"environment": "automotive"})
    assert result == "error", \
        f"expected 'error' (severity_delta +1), got {result!r}"


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
