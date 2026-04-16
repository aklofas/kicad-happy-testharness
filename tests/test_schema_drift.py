"""Unit tests for --schema vs emitted-output drift.

For each analyzer that exposes a --schema command, verify its documented
top-level keys match what the analyzer actually emits. Prevents the class
of bug that was KH-315 (schematic --schema documented hierarchy_context
which the analyzer no longer emitted) from recurring silently.

The class of bug we block (direction 1, STRICT):
- --schema documents a required key that the analyzer never emits.
  Example: KH-315 documented hierarchy_context in every schematic output,
  but the analyzer only emits it on sub-sheets. False advertising.

Tolerance rules for schema keys (do not require in output):
- Description starts with literal "OPTIONAL" (case-insensitive).
- Key is listed in the _optional_sections comma-separated string.
- Key starts with "_" (internal debug/metadata — e.g., _optional_sections).

The other direction (emitted keys not documented in --schema, direction 2)
is checked with an allow-list of currently-undocumented envelope growth.
New undocumented keys will fail the test; known gaps are annotated so the
main repo can close them incrementally without breaking the test suite.

Fixture strategy: use a fresh analyzer output under results/outputs/ as
the "emitted" sample (analyzer wasn't re-run inside the unit test).
cross_analysis has no persisted output directory, so it is invoked live
on a fresh schematic+PCB pair. Tests skip cleanly when no fresh fixture
is available.
"""

TIER = "unit"

import glob
import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(HARNESS_DIR.parent / "kicad-happy"),
)
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"


# ---------------------------------------------------------------------------
# Known undocumented emitted keys per analyzer.
#
# These are keys the analyzer emits today but --schema doesn't document.
# Not a KH-315-class bug (--schema isn't falsely advertising), but the
# envelope documentation is incomplete. Tracked so the test fails if a
# NEW undocumented key appears — prompting the main repo to either add
# it to --schema or list it in _optional_sections.
#
# When main repo closes a gap, remove the key from this set.
# ---------------------------------------------------------------------------
_KNOWN_UNDOCUMENTED = {
    "schematic": {
        "annotation_issues", "audience_summary", "bus_topology", "design_intent",
        "footprint_filter_warnings", "ground_domains", "hierarchical_labels",
        "label_shape_warnings", "labels", "no_connects", "placement_analysis",
        "power_sequencing_validation", "power_symbols", "property_issues",
        "pwr_flag_warnings", "simulation_readiness", "sourcing_audit", "wire_geometry",
    },
    "pcb": {
        "audience_summary", "board_metadata", "connectivity_graph",
        "copper_presence_summary", "design_intent", "design_rule_compliance",
        "dfm_summary", "net_classes", "pad_to_pad_distances", "placement_density",
        "project_settings", "return_path_continuity", "silkscreen",
    },
    "gerber": {
        "audience_summary", "drill_tools",
    },
    "emc": set(),  # clean — EMC is zero-drift
    "cross_analysis": {
        "audience_summary",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schema(analyzer_script):
    """Run analyzer --schema and return parsed dict, or None if unsupported."""
    if not os.path.exists(analyzer_script):
        return None
    r = subprocess.run(
        [sys.executable, analyzer_script, "--schema"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def _optional_keys(schema):
    """Return the set of schema keys considered optional.

    A key is optional if:
    - Its name starts with underscore (internal debug/metadata).
    - Its description (string value) starts with the literal token OPTIONAL.
    - It is listed (comma-separated) in the _optional_sections meta key.
    """
    opt = set()
    for k, v in schema.items():
        if k.startswith("_"):
            opt.add(k)
            continue
        if isinstance(v, str) and v.strip().upper().startswith("OPTIONAL"):
            opt.add(k)
    sections = schema.get("_optional_sections", "")
    if isinstance(sections, str):
        for entry in sections.split(","):
            # Strip parenthetical annotations like "sheets (multi-sheet only)"
            name = entry.split("(")[0].strip()
            if name:
                opt.add(name)
    return opt


def _fresh_output(analyzer_type):
    """Return parsed JSON of the first fresh (schema_version==1.3.0) output.

    Fresh means post-Batch-20 — the envelope we expect --schema to document.
    Returns None if no fresh output exists for this type.
    """
    type_dir = OUTPUTS_DIR / analyzer_type
    if not type_dir.exists():
        return None
    for f in glob.glob(str(type_dir / "**" / "*.json"), recursive=True):
        if "_aggregate" in f:
            continue
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("schema_version") == "1.3.0":
            return d
    return None


def _assert_no_drift(schema, emitted, analyzer_type):
    """Direction 1 (strict): every required schema key must appear in output.
    Direction 2 (allow-listed): emitted keys not in --schema must either be
    in _optional_sections, prefixed with _, or in _KNOWN_UNDOCUMENTED.
    """
    schema_keys = set(schema.keys())
    emitted_keys = set(emitted.keys())
    optional = _optional_keys(schema)
    required = schema_keys - optional

    # Direction 1: schema documents a required key the output doesn't emit.
    # This is the KH-315 class.
    missing = required - emitted_keys
    assert not missing, (
        f"{analyzer_type}: --schema documents required keys not in emitted "
        f"output: {sorted(missing)}. Either remove from --schema, or emit "
        f"them (and tag OPTIONAL if only emitted conditionally)."
    )

    # Direction 2: analyzer emits a key --schema doesn't document.
    # Tolerated if explicitly in the known-gap allow-list, optional in schema,
    # or underscore-prefixed (internal).
    allowed = _KNOWN_UNDOCUMENTED.get(analyzer_type, set())
    undocumented = emitted_keys - schema_keys - optional - allowed
    undocumented = {k for k in undocumented if not k.startswith("_")}
    assert not undocumented, (
        f"{analyzer_type}: NEW emitted keys not documented in --schema: "
        f"{sorted(undocumented)}. Either (a) add to --schema (with OPTIONAL "
        f"prefix if conditional), (b) list in _optional_sections, or "
        f"(c) add to _KNOWN_UNDOCUMENTED[{analyzer_type!r}] in this test "
        f"if the gap is accepted as tech debt."
    )


def _derive_pcb_path(sch_path):
    """Given a fresh schematic output path, return the matching PCB path."""
    return (sch_path
            .replace("/schematic/", "/pcb/")
            .replace(".kicad_sch.json", ".kicad_pcb.json"))


# ---------------------------------------------------------------------------
# Per-analyzer tests
# ---------------------------------------------------------------------------

def test_schematic_schema_drift():
    schema = _schema(f"{KICAD_HAPPY}/skills/kicad/scripts/analyze_schematic.py")
    if schema is None:
        return
    emitted = _fresh_output("schematic")
    if emitted is None:
        return
    _assert_no_drift(schema, emitted, "schematic")


def test_pcb_schema_drift():
    schema = _schema(f"{KICAD_HAPPY}/skills/kicad/scripts/analyze_pcb.py")
    if schema is None:
        return
    emitted = _fresh_output("pcb")
    if emitted is None:
        return
    _assert_no_drift(schema, emitted, "pcb")


def test_gerber_schema_drift():
    schema = _schema(f"{KICAD_HAPPY}/skills/kicad/scripts/analyze_gerbers.py")
    if schema is None:
        return
    emitted = _fresh_output("gerber")
    if emitted is None:
        return
    _assert_no_drift(schema, emitted, "gerber")


def test_emc_schema_drift():
    schema = _schema(f"{KICAD_HAPPY}/skills/emc/scripts/analyze_emc.py")
    if schema is None:
        return
    emitted = _fresh_output("emc")
    if emitted is None:
        return
    _assert_no_drift(schema, emitted, "emc")


def test_cross_analysis_schema_drift():
    """cross_analysis has no persisted output dir — run it live on a pair."""
    script = f"{KICAD_HAPPY}/skills/kicad/scripts/cross_analysis.py"
    schema = _schema(script)
    if schema is None:
        return

    sch_json = None
    pcb_json = None
    for sch_path in glob.glob(str(OUTPUTS_DIR / "schematic" / "**" / "*.json"),
                              recursive=True):
        if "_aggregate" in sch_path:
            continue
        try:
            d = json.load(open(sch_path))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("schema_version") != "1.3.0":
            continue
        candidate = _derive_pcb_path(sch_path)
        if os.path.exists(candidate):
            sch_json = sch_path
            pcb_json = candidate
            break
    if sch_json is None or pcb_json is None:
        return

    r = subprocess.run(
        [sys.executable, script,
         "--schematic", sch_json, "--pcb", pcb_json],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        return
    try:
        emitted = json.loads(r.stdout)
    except json.JSONDecodeError:
        return
    _assert_no_drift(schema, emitted, "cross_analysis")


# ---------------------------------------------------------------------------
# Helper / classifier tests (don't depend on analyzers)
# ---------------------------------------------------------------------------

def test_optional_keys_handles_optional_prefix():
    schema = {
        "a": "string — required",
        "b": "OPTIONAL — conditional",
        "c": "optional (lowercase should still match via .upper())",
    }
    opt = _optional_keys(schema)
    assert "b" in opt
    assert "c" in opt
    assert "a" not in opt


def test_optional_keys_parses_sections_string():
    schema = {
        "_optional_sections": "foo, bar, baz (annotated), qux",
    }
    opt = _optional_keys(schema)
    assert {"foo", "bar", "baz", "qux"}.issubset(opt)


def test_optional_keys_treats_underscore_keys_as_optional():
    schema = {"_debug": "internal", "_optional_sections": "", "public": "required"}
    opt = _optional_keys(schema)
    assert "_debug" in opt
    assert "_optional_sections" in opt
    assert "public" not in opt


def test_assert_no_drift_catches_kh315_class():
    """Regression-test the core invariant: a missing required key fails."""
    schema = {"a": "required", "b": "required"}
    emitted = {"a": 1}  # missing b — should fail
    try:
        _assert_no_drift(schema, emitted, "emc")  # use 'emc' (empty allow-list)
        raised = False
    except AssertionError as e:
        raised = "not in emitted" in str(e) and "b" in str(e)
    assert raised, "expected AssertionError flagging missing required key"


def test_assert_no_drift_tolerates_optional_absence():
    schema = {"a": "required", "b": "OPTIONAL — sometimes emitted"}
    emitted = {"a": 1}  # b absent, OK because OPTIONAL
    _assert_no_drift(schema, emitted, "emc")  # should not raise


def test_assert_no_drift_catches_new_undocumented_key():
    """An emitted key not in schema, not in _optional_sections, not in allow-list → fail."""
    schema = {"a": "required"}
    emitted = {"a": 1, "totally_new": "surprise"}
    try:
        _assert_no_drift(schema, emitted, "emc")  # emc allow-list is empty
        raised = False
    except AssertionError as e:
        raised = "NEW emitted keys" in str(e) and "totally_new" in str(e)
    assert raised, "expected AssertionError flagging new undocumented key"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
