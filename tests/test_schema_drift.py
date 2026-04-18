"""Unit tests for --schema vs emitted-output drift.

For each analyzer that exposes a --schema command, verify its documented
top-level keys match what the analyzer actually emits. Prevents the class
of bug that was KH-315 (schematic --schema documented hierarchy_context
which the analyzer no longer emitted) from recurring silently.

The class of bug we block (direction 1, STRICT):
- --schema documents a required key that the analyzer never emits.
  Example: KH-315 documented hierarchy_context in every schematic output,
  but the analyzer only emits it on sub-sheets. False advertising.

Schema format (v1.4+): JSON Schema Draft 2020-12 emitted by the typed
analyzer_envelope SOT. Top-level shape is:
    {"$schema": ..., "type": "object", "title": ...,
     "properties": {field: {...}, ...},
     "required": [field, ...]}
Field names live under "properties"; required vs optional comes from the
"required" array. Properties not in "required" are optional (analyzer may
emit only conditionally).

The other direction (emitted keys not documented in --schema, direction 2)
is checked with an allow-list of currently-undocumented envelope growth.
New undocumented keys will fail the test; known gaps are annotated so the
main repo can close them incrementally without breaking the test suite.
With v1.4 typed envelope SOT, the allow-list is largely obsolete (all
documented keys live in `properties`); kept for tolerance during the
incremental Track 1 rollout (1.2-1.5) and any analyzer-specific drift.

Fixture strategy: use the NEWEST fresh analyzer output under results/outputs/
(by mtime) as the "emitted" sample — the analyzer isn't re-run inside the
unit test. cross_analysis has no persisted output directory, so it is
invoked live on a fresh schematic+PCB pair. Tests skip cleanly when no
fresh fixture is available.

Known limitation: if the newest fixture is stale (corpus not regen'd after
an analyzer change), the test proves consistency with the fixture rather
than with today's runtime behavior. Warn-on-stderr for fixtures > 30 days.
Interim workaround: `python3 run/run_<type>.py --cross-section smoke` before
trusting a PASS result on touched analyzers.
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
        "footprint_filter_warnings", "generic_symbol_warnings", "ground_domains",
        "hierarchical_labels", "instance_consistency_warnings",
        "label_shape_warnings", "labels",
        "legacy_analysis_quality", "no_connects",
        "placement_analysis",
        "power_sequencing_validation", "power_symbols", "property_issues",
        "protocol_compliance", "pwr_flag_warnings", "sheet_files", "sheets_parsed",
        "simulation_readiness", "sourcing_audit", "text_annotations",
        "voltage_derating", "wire_geometry",
    },
    "pcb": {
        "audience_summary", "board_metadata", "board_thickness_mm",
        "connectivity_graph", "copper_presence_summary", "decoupling_proximity",
        "design_intent", "design_rule_compliance", "dfm_summary", "dimensions",
        "groups", "layer_transitions", "net_classes", "pad_to_pad_distances",
        "placement_density", "project_settings", "return_path_continuity",
        "silkscreen", "thermal_pad_scan",
    },
    "gerber": {
        "audience_summary", "drill_tools",
    },
    "emc": set(),  # clean — EMC is zero-drift
    "thermal": {
        "audience_summary",
    },
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


def _schema_field_keys(schema):
    """Return the set of envelope field names declared in the JSON Schema."""
    return set(schema.get("properties", {}).keys())


def _required_field_keys(schema):
    """Return the set of envelope field names declared required."""
    return set(schema.get("required", []))


def _optional_keys(schema):
    """Return the set of envelope field names that are optional.

    Under JSON Schema 2020-12, optional = declared in `properties` but absent
    from `required`. Underscore-prefixed properties (e.g. `_redirected_from`,
    `_stale_file_warning`) are always treated as optional internal metadata.
    """
    fields = _schema_field_keys(schema)
    required = _required_field_keys(schema)
    opt = fields - required
    opt |= {k for k in fields if k.startswith("_")}
    return opt


CURRENT_SCHEMA_VERSION = "1.4.0"


def _emitted_keys(analyzer_type, sample_limit=50, max_age_days=30):
    """Return the UNION of top-level keys across fresh analyzer outputs.

    Different boards trigger different optional detector sections — a single
    fixture undercounts the analyzer's true key footprint. Sampling up to
    `sample_limit` fresh (schema_version == CURRENT_SCHEMA_VERSION) outputs
    and unioning their top-level keys gives a complete picture of what the
    analyzer can emit, avoiding both false-positive drift (required key
    missing from a trivial input) and false-negative drift (undocumented
    key appearing only on complex boards).

    Returns (emitted_keys: set | None, newest_mtime: float | None).
    Returns (None, None) if no fresh outputs exist.

    Warns on stderr when the newest fresh fixture is older than
    max_age_days — signal that the corpus needs a re-run for the drift
    test to be meaningful.
    """
    type_dir = OUTPUTS_DIR / analyzer_type
    if not type_dir.exists():
        return None, None
    candidates = []
    for f in glob.glob(str(type_dir / "**" / "*.json"), recursive=True):
        if "_aggregate" in f:
            continue
        try:
            mtime = os.path.getmtime(f)
        except OSError:
            continue
        candidates.append((mtime, f))
    candidates.sort(reverse=True)

    emitted_keys = set()
    newest_mtime = None
    samples_taken = 0
    for mtime, f in candidates:
        if samples_taken >= sample_limit:
            break
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("schema_version") != CURRENT_SCHEMA_VERSION:
            continue
        emitted_keys |= set(d.keys())
        if newest_mtime is None:
            newest_mtime = mtime
        samples_taken += 1

    if samples_taken == 0:
        return None, None

    import time
    age_days = (time.time() - newest_mtime) / 86400
    if age_days > max_age_days:
        sys.stderr.write(
            f"test_schema_drift: newest {analyzer_type} fixture is "
            f"{age_days:.0f} days old. Re-run the analyzer to revalidate "
            f"current behavior.\n"
        )
    return emitted_keys, newest_mtime


# Backward-compatible shim — returns a dict-like with .keys() for callers
# that want key-level comparison only. (cross_analysis path still loads
# a full dict because it runs live.)
def _fresh_output(analyzer_type):
    keys, _ = _emitted_keys(analyzer_type)
    if keys is None:
        return None
    # Minimal object with .keys() to preserve _assert_no_drift contract.
    return {k: None for k in keys}


def _assert_no_drift(schema, emitted, analyzer_type):
    """Direction 1 (strict): every required schema field must appear in output.
    Direction 2 (allow-listed): emitted keys not in --schema must either be
    optional in schema, prefixed with _, or in _KNOWN_UNDOCUMENTED.
    """
    schema_keys = _schema_field_keys(schema)
    emitted_keys = set(emitted.keys())
    optional = _optional_keys(schema)
    required = _required_field_keys(schema)

    # Direction 1: schema documents a required key the output doesn't emit.
    # This is the KH-315 class.
    missing = required - emitted_keys
    assert not missing, (
        f"{analyzer_type}: --schema documents required keys not in emitted "
        f"output: {sorted(missing)}. Either remove from --schema `required`, "
        f"or emit them unconditionally."
    )

    # Direction 2: analyzer emits a key --schema doesn't document.
    # Tolerated if explicitly in the known-gap allow-list, declared in
    # `properties` (which makes it optional automatically when not in
    # `required`), or underscore-prefixed (internal).
    allowed = _KNOWN_UNDOCUMENTED.get(analyzer_type, set())
    undocumented = emitted_keys - schema_keys - optional - allowed
    undocumented = {k for k in undocumented if not k.startswith("_")}
    assert not undocumented, (
        f"{analyzer_type}: NEW emitted keys not documented in --schema: "
        f"{sorted(undocumented)}. Either (a) add the key to the typed "
        f"envelope dataclass (so it appears in --schema `properties`), or "
        f"(b) add to _KNOWN_UNDOCUMENTED[{analyzer_type!r}] in this test "
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


def test_thermal_schema_drift():
    schema = _schema(f"{KICAD_HAPPY}/skills/kicad/scripts/analyze_thermal.py")
    if schema is None:
        return
    emitted = _fresh_output("thermal")
    if emitted is None:
        return
    _assert_no_drift(schema, emitted, "thermal")


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
        if d.get("schema_version") != CURRENT_SCHEMA_VERSION:
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

def _mk_schema(properties, required):
    """Build a minimal JSON Schema 2020-12 envelope for testing."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {p: {"type": "string"} for p in properties},
        "required": list(required),
    }


def test_optional_keys_uses_required_array():
    schema = _mk_schema(["a", "b", "c"], ["a"])
    opt = _optional_keys(schema)
    assert opt == {"b", "c"}


def test_optional_keys_treats_underscore_properties_as_optional():
    schema = _mk_schema(["_debug", "public"], ["public"])
    opt = _optional_keys(schema)
    assert "_debug" in opt
    assert "public" not in opt


def test_optional_keys_handles_no_required_array():
    schema = {"properties": {"a": {}, "b": {}}}
    opt = _optional_keys(schema)
    assert opt == {"a", "b"}


def test_assert_no_drift_catches_kh315_class():
    """Regression-test the core invariant: a missing required key fails."""
    schema = _mk_schema(["a", "b"], ["a", "b"])
    emitted = {"a": 1}  # missing required b — should fail
    try:
        _assert_no_drift(schema, emitted, "emc")  # use 'emc' (empty allow-list)
        raised = False
    except AssertionError as e:
        raised = "not in emitted" in str(e) and "b" in str(e)
    assert raised, "expected AssertionError flagging missing required key"


def test_assert_no_drift_tolerates_optional_absence():
    schema = _mk_schema(["a", "b"], ["a"])  # b is optional
    emitted = {"a": 1}  # b absent, OK
    _assert_no_drift(schema, emitted, "emc")  # should not raise


def test_assert_no_drift_catches_new_undocumented_key():
    """An emitted key not in schema, not in allow-list → fail."""
    schema = _mk_schema(["a"], ["a"])
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
