# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

> **Reporting guidelines for Level 3 subagents**: Root cause descriptions must cite
> specific function names and line numbers, not just file names. When claiming code
> "doesn't check X", trace the actual code path for the repro input and show which line
> returns the wrong result — don't infer from the symptom what the code must be doing.
> Common pitfalls:
> - Code checks the right field but matches the wrong strings (KH-213: checked keywords
>   for `p-channel` but actual keywords contain `PMOS`)
> - Code has the right pattern but wrong format (KH-209: matched `Vnn` but not `nnVn`)
> - Fix exists but callers bypass it (KH-212: KH-153 fix requires `component_type` param
>   that callers don't pass)
> - Transforms are applied but decomposed wrong (KH-207: `compute_pin_positions` runs but
>   matrix→angle extraction is mathematically incorrect)
>
> Include in every report: (1) the function name and line number that produces the wrong
> result, (2) the actual input values from the repro file, (3) what the code returns vs
> what it should return.

Last updated: 2026-04-10

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-234**. Next TH number: **TH-015**.

> 4 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-231: opamp_circuits non-inverting gain uses inverting formula

**Severity:** HIGH
**Discovered:** 2026-04-10 by re-enabling `tests/test_detection_schema.py` (TH-014 fix)
**Where:** `kicad_utils.py` or `detection_schema.py` in `kicad-happy/skills/kicad/scripts/` — the `recalc_derived` path for the `opamp_circuits` schema.

**Repro:**
```python
from detection_schema import recalc_derived
det = {"feedback_resistor": {"ohms": 47000},
       "input_resistor": {"ohms": 10000},
       "configuration": "non_inverting"}
recalc_derived(det, "opamp_circuits")
print(det["gain"])  # got -4.7, expected 5.7 (= 1 + Rf/Ri)
```

The recalc returns `-Rf/Ri` (the inverting formula) regardless of the
`configuration` field. Same wrong value for both `non_inverting` and
`inverting` cases — the configuration switch is missing or broken.

**Affected tests** (all currently `XFAIL` in the harness):
- `test_recalc_opamp_non_inverting` — direct gain check
- `test_inverse_opamp_gain` — inverse solver targeting `gain=10` (gets -9)
- `test_inverse_opamp_gain_dB` — inverse solver targeting `gain_dB=20` (gets 19.08 ≈ 20·log10(9))

**Expected fix:** in `recalc_derived` for opamp_circuits, branch on
`det["configuration"]`:
- `non_inverting` → `gain = 1 + Rf/Ri`
- `inverting` → `gain = -Rf/Ri`

**Impact:** every opamp_circuits detection in 36,541 schematic outputs
has wrong gain values. Severity is HIGH because the bug is silent (wrong
numbers, no errors) and the field is consumed by downstream detectors.

**How to verify the fix:** in the harness, re-run
`python3 tests/test_detection_schema.py` — the three tests should flip
from XFAIL to XPASS. Remove the entries from `KNOWN_FAILURES` in that
file. Then re-run the smoke set and the full unit suite.

---

### KH-232: lc_filters has no inverse solver registered for resonant_hz

**Severity:** MEDIUM
**Discovered:** 2026-04-10 by re-enabling `tests/test_detection_schema.py` (TH-014 fix)
**Where:** `detection_schema.py` in `kicad-happy/skills/kicad/scripts/` — the `lc_filters` schema's inverse solver registry.

**Repro:**
```python
from detection_schema import get_inverse_solver
solver = get_inverse_solver("lc_filters", "resonant_hz")
print(solver)  # got None, expected a callable
```

`get_inverse_solver` returns `None` for `(lc_filters, resonant_hz)`.
Either the solver was never registered or it was removed without
removing the test. Other schemas (`crystal_circuits`, `current_sense`,
`opamp_circuits`) have inverse solvers registered for their primary
fields and the corresponding tests pass.

**Affected tests** (currently `XFAIL`):
- `test_inverse_lc_resonant` — expects a solver that recommends C given
  fixed L and target resonant_hz

**Expected fix:** register an inverse solver for `(lc_filters, resonant_hz)`.
Math: `f = 1 / (2π√(LC))` so `C = 1 / (L·(2πf)²)`. Should also handle
solving for L given fixed C.

**Impact:** users asking "what cap should I use for a 100 kHz LC filter
with this inductor?" get no answer. Functional gap, not a wrong value.

**How to verify the fix:** in the harness, re-run
`python3 tests/test_detection_schema.py` — `test_inverse_lc_resonant`
should flip from XFAIL to XPASS. Remove the entry from `KNOWN_FAILURES`.

---

### KH-233: SCHEMAS dict missing 22 detector entries

**Severity:** MEDIUM
**Discovered:** 2026-04-10 by re-enabling `tests/test_detection_schema.py` (TH-014 fix)
**Where:** `detection_schema.py` in `kicad-happy/skills/kicad/scripts/` — the top-level `SCHEMAS` registry.

**Repro:** `python3 tests/test_detection_schema.py` →
`test_schema_completeness_zebra_x` reports 22 `signal_analysis` keys
present in real analyzer outputs but absent from `SCHEMAS`:

```
addressable_led_chains, adc_circuits, audio_circuits, battery_chargers,
buzzer_speaker_circuits, clock_distribution, connector_ground_audit,
debug_interfaces, display_interfaces, hdmi_dvi_interfaces, key_matrices,
led_driver_ics, level_shifters, lvds_interfaces, motor_drivers,
rail_voltages, reset_supervisors, rtc_circuits, sensor_interfaces,
snubbers, suggested_certifications, thermocouple_rtd
```

These detectors fire and write into the analyzer JSON but have no
schema entry — meaning identity/derived field metadata, recalc
functions, and inverse solvers are unavailable for them.

**Expected fix:** add a `DetectionSchema` entry per detector to
`SCHEMAS`. Most are simple (identity fields only, no derived). A few
(rail_voltages, battery_chargers) have computable values that warrant
derived fields and inverse solvers in a follow-up.

**Impact:** downstream code that walks SCHEMAS to determine field
semantics (regression seeding, validation, packet generation) silently
skips these 22 detector classes. Coverage gap.

**How to verify the fix:** in the harness, re-run
`python3 tests/test_detection_schema.py` — `test_schema_completeness_zebra_x`
should flip from XFAIL to XPASS once all 22 keys are present. Remove the
entry from `KNOWN_FAILURES`.

---

### KH-230: Empty placed Value silently substituted with lib_symbol default

**Severity:** LOW
**Discovered:** 2026-04-10 by `validate/verify_parser.py` (P1 Parser Verification, full corpus run)
**Repro:** `hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`

The file has two placed `(symbol (lib_id "Device:R") ...)` instances both
annotated as `R1` (a duplicate-annotation design issue independent of this
bug). The second instance has `(property "Value" "")` — explicitly empty —
but the analyzer reports `value: "R"` for it, which is the `Device:R`
lib_symbol's placeholder default Value.

**Expected:** `components[].value` should reflect the placed instance's
property exactly. An empty placed Value should serialize as `""`, not be
silently replaced by the lib_symbol template default. Otherwise downstream
detectors and BOM logic see a fabricated value that doesn't exist in the
source.

**Evidence:**
- sexp parse: R1 instance #2 Value = `""`
- analyzer output: R1 instance #2 value = `"R"` (= lib_symbol default)
- file: `repos/hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`
- analyzer output: `results/outputs/schematic/hamster/SAINTCON/CHC_2022_Circuits - Series and Parallel.kicad_sch.json`

Likely in `analyze_schematic.py` symbol parsing path — when the placed
Value property is empty, the code is falling back to `sym_def.get("value")`
or similar instead of preserving the empty string.

Severity is LOW because it requires both a duplicate-annotation defect
AND an empty Value on one of the duplicates, and only 1/25,625 corpus
files hits it.

---



---

## Test Harness Issues

(none)



---

## Deferred

(none)

---

## Priority Queue (open issues, ordered by impact)

1. **KH-231** — HIGH — opamp non-inverting gain uses inverting formula (silent wrong value across all opamp_circuits detections)
2. **KH-232** — MED — lc_filters missing inverse solver for resonant_hz
3. **KH-233** — MED — SCHEMAS dict missing 22 detector entries (coverage gap)
4. **KH-230** — LOW — empty placed Value silently replaced with lib_symbol default (1 file in corpus)

