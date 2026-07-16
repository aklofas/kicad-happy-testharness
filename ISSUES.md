# Issue Tracker

Single source of truth for kicad-happy analyzer bugs (KH-*) and test harness
issues (TH-*). Contains enough detail to resume work with zero conversation
history. Enhancements and features are tracked in `TODO-v1.3-roadmap.md`
in each repo, not here.

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

Last updated: 2026-07-12

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-354** (KH-349/350 filed 2026-07-13; KH-351..353
fixed-on-arrival 2026-07-15, see FIXED.md). Next TH number: **TH-046**.

> 24 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-328: `wrap_result.py` helper missing from datasheets skill

**Severity:** LOW
**File:** `skills/datasheets/scripts/` (helper absent)
**Discovered:** 2026-05-19 (SacMap rev2 review of v1.4 datasheet extraction layer)

**Symptom:** Consumers of the datasheets extraction pipeline hand-roll
the `{task_id, schema_version, status, extracted_at, model_tier,
model_id, data}` result envelope. SacMap's seed implementation at
`~/Projects/sacmap/wrap_result.seed.py` demonstrates a single-file
wrapper but ships nowhere central in kicad-happy.

**Spec (from SacMap reviewer):**
- read `<mpn>.plan.json` for tier/schema/task_id auto-population
- read `x-schema-version` from schema file
- read agent output from file/stdin
- strip prose preamble + markdown fences via regex first-balanced-JSON-block extraction
- validate against schema before writing
- write failed status (`data: null`, `error: msg`) if validation fails

**Likely fix:** Ship `skills/datasheets/scripts/wrap_result.py` with the
above contract. Ask the user whether to copy the SacMap seed as a
reference starting point.

**Not tag-blocking** — convenience helper; pipeline functional without it.

---

### KH-329: `plan_extraction.py` "not implemented" error lacks next-command pointer

**Severity:** LOW
**File:** `skills/datasheets/scripts/plan_extraction.py` (live-scout-dispatch path)
**Discovered:** 2026-05-19

**Symptom:** First invocation prints "live scout dispatch not implemented"
and points at a ~180-line markdown doc. The error message does not
include the exact next command to run, so users hit the wall and have
to read upstream docs to recover.

**Likely fix:** Either (a) include the exact next command in the error
message, or (b) ship the actual live-scout dispatch.

**Not tag-blocking** — error-message UX.

---

### KH-330: `base.schema.json` and `pinout.schema.json` missing `x-schema-version`

**Severity:** LOW
**File:** `skills/datasheets/schemas/base.schema.json`, `skills/datasheets/schemas/pinout.schema.json`
**Discovered:** 2026-05-19

**Symptom:** Other schemas in `skills/datasheets/schemas/` (regulator,
diode, mcu, opamp, transistor, crystal) carry a top-level
`x-schema-version` field; `base.schema.json` and `pinout.schema.json`
do not. Consumers (KH-328 `wrap_result.py` spec, validators) have to
guess or fall back to a hardcoded default.

**Likely fix:** Add `"x-schema-version": "<current>"` to both files;
sync the value with whatever Phase 4 declared as the base/pinout
baseline.

**Not tag-blocking** — consumer-visible inconsistency, no behavior
divergence today.

---

### KH-331: `jsonschema` + `referencing` deps undeclared in datasheets skill

**Severity:** LOW
**File:** `skills/datasheets/scripts/merge_results.py`, `skills/datasheets/scripts/validate_extraction_result.py`
**Discovered:** 2026-05-19

**Symptom:** Both scripts `import jsonschema` and use `referencing` but
the skill ships no `requirements.txt`, no SKILL.md mention, no install
instructions. On Debian this requires `pip install
--break-system-packages` for a global install. The codebase already
ships a stdlib equivalent at
`skills/datasheets/scripts/_mini_jsonschema.py` per harness memory
`feedback_stdlib_first`.

**Likely fix:** Three options:
1. Declare the dep in `requirements.txt` + SKILL.md (allows pip-install workflow).
2. Vendor / switch to the existing `_mini_jsonschema.py`.
3. Remove the dep where stdlib coverage suffices.

Preference per `feedback_stdlib_first`: option 2.

**Not tag-blocking** — works on systems where `jsonschema` is installed.

---

### KH-332: Tier B `diode` and `mcu` extractor agents emit prose preamble on long page lists

**Severity:** LOW
**File:** `skills/datasheets/agents/diode.md`, `skills/datasheets/agents/mcu.md` (vs `regulator.md`)
**Discovered:** 2026-05-19 (SacMap rev2 — 2 of 9 extractor agents tripped)

**Symptom:** 2 of 9 Tier B extractor invocations emitted prose preamble
despite the prompt's "no prose, no fences" instruction. Tier B
regulator at similar page count was clean.

**Likely fix:** Diff `regulator.md` vs `diode.md` vs `mcu.md` and apply
whatever suppression pattern `regulator.md` uses to the other two.
Downstream consumers handle preamble defensively (see KH-328 spec item
"strip prose preamble"), but upstream cleanliness reduces wrap_result
fragility.

**Not tag-blocking** — extraction outputs still validate after
preamble stripping.

---

### KH-333: `capability_mode` not surfaced in datasheet `<mpn>.json` extraction output

**Severity:** LOW
**File:** `skills/datasheets/scripts/merge_results.py` (output envelope)
**Discovered:** 2026-05-19

**Symptom:** EMC analyzer surfaces `capability_mode` via a separate
`capability_mode.json` artifact + `capability_mode_ref` field on the
analyzer envelope. The datasheets extraction layer surfaces it nowhere
— neither in `<mpn>.json` nor in a sidecar. Consumers cannot tell
which capability mode produced an extraction.

**Likely fix:** Either (a) add `capability_mode` (or
`capability_mode_ref`) to the extraction envelope, mirroring the EMC
pattern, or (b) document the omission in SKILL.md as intentional.

**Not tag-blocking** — provenance gap, not a correctness issue.

---

### KH-334: v1.5 — empirical determinism check for datasheet extraction pipeline

**Severity:** LOW
**File:** `skills/datasheets/scripts/` (pipeline as a whole)
**Discovered:** 2026-05-19 (SacMap rev2 flagged but did not exercise)

**Symptom:** No automated check that re-running the same extraction
pipeline on the same PDF twice produces identical outputs. Temperature
defaults and tier selection could introduce silent drift. SacMap
reviewer flagged this as a concern but did not run the comparison.

**Likely fix (v1.5 carryover):** Add a smoke step that:
1. Runs full extraction on a sanity-vector MPN (e.g. LM2596-ADJ).
2. Re-runs the same pipeline.
3. Diffs the two `<mpn>.json` outputs and reports the magnitude of any
   drift (zero is target; non-zero is the calibration data point).

**Not tag-blocking** — v1.5 carryover, future work.

---

### KH-338: usb_compliance check failures never become findings[]; vbus_esd_protection false-fails on unnamed VBUS nets

**Severity:** HIGH
**File:** `skills/kicad/scripts/analyze_schematic.py` (~8162-8163, stored ~9256)
**Discovered:** 2026-07-12 (SacMap rev2 run-5)

**Symptom:** (a) `usb_compliance.connectors[].checks` results (e.g. `vbus_decoupling:
"fail"` — a genuine missing-bulk-cap defect) live only in the aux section; sole
consumer `domain_detectors.py:5639` ignores individual checks. The most important
electrical finding on the board never reached findings[]/summarize. (b)
`vbus_esd_protection: "fail"` while `usb_esd_ic: "pass"`: the VBUS net is unnamed
(`__unnamed_10`, display_name `U4.VBUS`); check resolves VBUS by net NAME or counts
only discrete TVS parts, so the ESD array's own VBUS pin (pin_name "VBUS",
connected_to J1.1) isn't credited.

**Fix sketch:** emit each failed check as a rich finding via make_finding (new rule
ids); resolve VBUS by connector-pin connectivity + pin_name, not net name.

---

### KH-339: CP-003 touch-pad clearance measured to zone outline bbox, not filled copper

**Severity:** MEDIUM (false positive; SKILL.md itself warns "zone outline != actual copper")
**File:** `skills/kicad/scripts/analyze_pcb.py:5413`
**Discovered:** 2026-07-12 (SacMap rev2 run-5: reported 0.0mm, actual filled gap 1.000mm)

**Symptom:** uses `gz.get("outline_bbox")`; `filled_bbox` + zone_fills exist but unused.

**Fix sketch:** measure to filled_bbox / nearest filled-polygon edge when fill data
available; fall back to outline with confidence downgrade.

---

### KH-340: VP-001 via-in-pad uses bounding-box hit-test, no pad shape/rotation

**Severity:** MEDIUM (false positive)
**File:** `skills/kicad/scripts/analyze_pcb.py:5830-5844`
**Discovered:** 2026-07-12 (SacMap rev2 run-5: via 8.16mm radial from 7.5mm-radius circular pad flagged in-pad)

**Fix sketch:** point-in-shape test for circle/oval/roundrect + pad rotation.

---

### KH-341: DC-003 decoupling-cap-far-from-via lacks same-layer-pour / 2-layer suppression

**Severity:** MEDIUM (6 false positives on a 2-layer board)
**File:** `skills/emc/scripts/emc_rules.py:584-631`
**Discovered:** 2026-07-12 (SacMap rev2 run-5)

**Symptom:** flags cap >3mm from nearest via even when the pad ties directly into a
same-layer pour of the same net (no via needed).

**Fix sketch:** suppress/demote when pad abuts same-layer same-net zone, or when
copper_layers_used == 2.

---

### KH-342: sleep_current_audit scores divider legs independently and RC-filter pull-ups as DC loads

**Severity:** MEDIUM (overstated sleep current)
**File:** `skills/kicad/scripts/analyze_schematic.py:6280-6324`
**Discovered:** 2026-07-12 (SacMap rev2 run-5: R7 EN-RC filter scored 330uA, true ~0;
R10 scored via 680K leg alone, true 3.98uA through 680K+150K)

**Fix sketch:** detect series-R + shunt-C (steady-state DC ~ 0); sum divider legs as
one V/(R_top+R_bot) path.

---

### KH-343: rail-voltage inference maps any net containing "USB" to 5.0V — including data lines

**Severity:** MEDIUM (poisons derating + datasheet voltage checks downstream)
**File:** `skills/kicad/scripts/analyze_schematic.py:4719` AND `skills/kicad/scripts/signal_detectors.py:1547` (two copies)
**Discovered:** 2026-07-12 (SacMap rev2 run-5: rail_voltages contains USB_DM: 5.0, USB_DP: 5.0)

**Fix sketch:** tighten to VBUS/+5V_USB; exclude _DM/_DP/_D+/_D-/DPLUS/DMINUS
suffixes. Fix BOTH copies (and consider deduplicating the helper).

---

### KH-344: PM-002 emits "move further from board edge" for negative courtyard distances

**Severity:** LOW (nonsense recommendation on intentional overhangs)
**File:** `skills/kicad/scripts/analyze_pcb.py:3579` (RF/edge-mount demotion at 3549-3557 exists but recommendation text still fires)
**Discovered:** 2026-07-12 (SacMap rev2 run-5: U1 antenna courtyard at -14.51mm told to move >=1.0mm from edge)

**Fix sketch:** for min_edge < 0 reframe as "courtyard overhangs board edge by X mm";
suppress the move-it recommendation.

---

### KH-345: CLI/doc drift — simulate_subcircuits has no --text; lifecycle --temp-range space form fails

**Severity:** LOW
**File:** `skills/spice/scripts/simulate_subcircuits.py`; `skills/kicad/scripts/lifecycle_audit.py:951`; kicad SKILL.md
**Discovered:** 2026-07-12 (SacMap rev2 run-5)

**Symptom:** SKILL.md implies all analyzers support --text; simulate_subcircuits does
not. `--temp-range "-40,105"` (space form) is parsed as a flag by argparse; only
`--temp-range=...` works (already documented in help text).

**Fix sketch:** add --text to simulate_subcircuits (or correct the doc claim); doc-only
fix acceptable for --temp-range.

---

### KH-346: per-pin absolute_max SpecValue list read is unit-blind (latent false-CRITICAL)

**Severity:** LOW (latent — no extraction populates per-pin absolute_max today; becomes MEDIUM the day one does)
**File:** `skills/datasheets/scripts/datasheet_verify.py` (`_spec_max` consumer in `_v1_view` per-pin path, ~L152)
**Discovered:** 2026-07-12 (KH-337 review round 2, residual)

**Symptom:** pinout.schema.json allows per-pin `absolute_max` to mix voltage and
current SpecValues; `_spec_max` takes `sv_list[0].max` blind. A current rating
first in the list (e.g. max=0.025, unit="A") would be compared against net VOLTS
-> false CRITICAL `pin_voltage_abs_max_exceeded` — worst noise class for a
correctness-floor tool.

**Fix sketch:** one-line unit filter — first entry with `unit == "V"` instead of
`[0]`. Must land before extraction prompts start populating per-pin ratings.

---

### KH-348: lifecycle_audit `--only lcsc` returns all-unknown — LCSC/jlcsearch exposes no lifecycle status

**Severity:** LOW (misleading "audit ran, board clean" appearance)
**File:** `skills/kicad/scripts/lifecycle_audit.py`
**Discovered:** 2026-07-12 (SacMap rev2 run-6: 20/20 MPNs `unknown`, including parts LCSC definitely stocks — TPS61023DRLR, USBLC6-2SC6, ESP32-S3-WROOM-1-N4)

**Symptom:** the jlcsearch community API has no lifecycle/obsolescence field, so an
LCSC-only audit can never produce a real status; output is indistinguishable from
"audited and fine" unless the reader notices every row is `unknown`.

**Fix sketch:** when the effective source set is LCSC-only, say so up front
(capability note / explicit "LCSC does not expose lifecycle status — use DigiKey or
element14 credentials for a real audit" in the summary) instead of emitting 20
LC-004 unknowns. Keep the per-part rows for temp-range data if present.

---

### KH-349: VP-001 flags vias in copper-less pads (all technical layers cleared)

**Severity:** MEDIUM (false positive; GitHub #28)
**File:** `skills/kicad/scripts/analyze_pcb.py:5810-5836` (`analyze_via_in_pad`)
**Discovered:** 2026-07-13 (GitHub #28, ademuri rfboard: RFM69 module pads
"disabled" by clearing all technical layers — `(pad "" smd rect (layers
"Dwgs.User"))`; 4 of 8 VP-001 findings on the board are these pads)

**Symptom:** the SMD-pad collector filters only on `pad.type == "smd"` and
hit-tests via centers against the width/height bbox; it never inspects the
pad's layer list, so a pad with no copper layer still catches vias.
Reproduced on the attached board: `U2:''` ×4 false, while `J3:2/3`, `U2:1`,
`U3:6` sit on real F.Cu/B.Cu pads (genuine via-in-pad, not part of this bug).

**Fix sketch:** skip pads whose `layers` contain no copper (`*.Cu` / `F.Cu` /
`B.Cu`). Pad layers are already parsed into `pad_info["layers"]`
(analyze_pcb.py:734) — filter is one condition in the collector loop.
Natural batch-mate for KH-340 (same collector, shape/rotation hit-test).
Corpus impact: disappearing VP-001 findings on boards using the
cleared-layers pad trick — budgeted gate.

---

### KH-350: courtyard overlap uses single AABB per footprint — notched courtyards (QFP cross shape) false-positive

**Severity:** MEDIUM (false positive at error severity; GitHub #29)
**File:** `skills/kicad/scripts/analyze_pcb.py:775-862` (courtyard extraction) + `:3451` (`analyze_component_placement`)
**Discovered:** 2026-07-13 (GitHub #29, ademuri rfboard: LQFP-32 U1 vs R2 in
the corner notch — reported 1.41mm² overlap at error severity)

**Symptom:** extraction collapses all CrtYd primitives to one axis-aligned
bbox (`fp_entry["courtyard"]` = min/max only), filling in the notched corners
of cross-shaped QFP courtyards. Verified against the true 20-segment U1
courtyard polygon: R2's real overlap is 0.000mm² — the reported 1.41mm² is
entirely the bbox artifact. Same board: U1/C28 0.984mm² (also corner-notch
artifact, lands just under the 1.0mm² error threshold → warning).

**Fix sketch:** preserve courtyard geometry beyond the AABB — chain CrtYd
fp_line/fp_rect/fp_poly primitives into polygon(s), do polygon-polygon
intersection area (sampling like `copper_connected` is an acceptable stdlib
fallback). Keep AABB as a cheap pre-filter. Corpus impact: disappearing/
downgraded courtyard-overlap findings on QFP-adjacent placements — budgeted
gate.

---

## Test Harness Issues

### TH-037: `add_repos.py` raises `KeyError: 'stats'` on fresh runs

**Severity:** LOW
**File:** `tools/add_repos.py:323` (`_update_progress`) and `tools/add_repos.py:512` (dry-run summary)
**Discovered:** 2026-04-27 while adding Hanqaqa/Easyduino

**Symptom:** When invoked with no pre-existing progress file (i.e. first run for an
input), both `--dry-run` and the post-pipeline summary path traceback with
`KeyError: 'stats'`. Pipeline side effects (repos.md edit, clones, analyzer runs,
seeds, run_checks) all complete successfully *before* the error — only the
final summary/persistence is broken.

**Repro:**
```
python3 tools/add_repos.py --input /tmp/easyduino-validate/validated.json --jobs 4
# ...
# [1/1] OK Hanqaqa/Easyduino (153s elapsed)
# Traceback (most recent call last):
#   File "tools/add_repos.py", line 435, in _run_parallel
#     _update_progress(progress, result)
#   File "tools/add_repos.py", line 323, in _update_progress
#     progress["stats"]["total_succeeded"] += 1
# KeyError: 'stats'
```

**Likely fix:** Initialize `progress["stats"] = {"total_succeeded": 0, ...}` in
the new-progress-dict path (and the same for `--dry-run`). Defensive `.setdefault`
in `_update_progress` would also work.

---

### TH-038: `validate_candidates.py` 60s clone timeout too tight for medium repos

**Severity:** LOW
**File:** `tools/validate_candidates.py:90` (`_shallow_clone(timeout=60)`)
**Discovered:** 2026-04-27 while adding Hanqaqa/Easyduino

**Symptom:** Repos in the 200MB+ class (Easyduino is 605MB unpacked / 215MB packed)
exceed the 60s shallow-clone timeout on a typical home connection, causing
`validate_candidates.py` to mis-classify them as `clone_failed`. Bumping the
timeout to 180s allowed Easyduino to clone in 78s and pass validation cleanly.

**Repro:** Run `python3 tools/validate_candidates.py` against any repo whose
`--depth 1` clone exceeds 60s. Output reports `Clone failed: 1` and writes 0
validated candidates.

**Likely fix:** Bump default to 180s, or scale by repo size if the candidates
file carries one. The 60s default was probably set for small repos and never
revisited.

---

### TH-039: `test_kh238_feedback_divider_detected` synthetic LM317 fixture never triggers detector

**Severity:** LOW
**File:** `tests/test_bug_cemetery.py:257-306` (`test_kh238_feedback_divider_detected`)
**Discovered:** 2026-05-15 during pre-push gate before v1.4.0-rc.1 tag

**Symptom:** The KH-238 regression test (added 2026-04-12 in harness commit
`a9a34766ae0`) builds a synthetic LM317 fixture and expects
`detect_power_regulators` to populate `feedback_divider` for U1. Test asserts:
```
assert fb is not None, "KH-238 regression: feedback_divider not detected for LM317"
```
But `feedback_divider` is `None` on every kicad-happy `v1.4-dev` SHA bisected:
`968f5c8` (v1.3.1), `0df3b7f`, `d2c3eb6`, `ea9b61b`, `fa02ba4`, `aba7083`,
`8c36212`, `8daa28d`, `7870c45`, `693b664`. The bug is NOT a recent regression —
the test has likely been failing since the day it was added (it was the lone
"1 fail" recorded in `status.md` at 2026-05-14).

**Root cause hypothesis:** The KH-238 fix in kicad-happy
(`9c8ec19`, "Fix KH-238 feedback divider pair-ordering drops valid R-R pairs",
on both `main` and `v1.4-dev`) IS present in the analyzer at every bisected SHA.
The code paths that populate `feedback_divider` exist at
`skills/kicad/scripts/signal_detectors.py:1877`, `:1894`, `:1988`. But the
synthetic fixture's wire topology, lib_id (`Regulator_Linear:LM317_SOT-223`), or
power-pin labeling doesn't trigger any of those branches — most likely the
detector requires a specific topology (e.g. ADJ pin handling, particular net
labeling, or a footprint hint) that the `_build_sch.Schematic().ic(...)` helper
doesn't emit in the form the detector expects.

The analyzer DOES find U1 as a regulator (`detect_power_regulators` emits an
entry with `ref=U1, value=LM317`), so the issue is specifically in the
divider-pairing branch, not regulator detection itself.

**Repro:** see `/tmp/kh238_repro/` (created during 2026-05-15 investigation):
```
python3 -c "from fixtures._build_sch import ...; ..."  # build fixture
python3 ~/Projects/kicad-happy/skills/kicad/scripts/analyze_schematic.py \
    /tmp/kh238_repro/lm317.kicad_sch --output /tmp/kh238_repro/output.json
jq '.findings[] | select(.detector=="detect_power_regulators")' /tmp/kh238_repro/output.json
# → "feedback_divider": null
```

**Likely fix paths (pick one):**
- Inspect what topology the detector actually expects for LM317-class adjustables
  (probably needs ADJ pin, not FB pin; or specific net naming like the original
  KH-238 corpus exemplar) and adjust the fixture's pin definitions and wire
  topology to match.
- Or: replace the synthetic fixture with a real-corpus exemplar regression by
  pinning a specific repo+project that exhibits the KH-238-fixed pattern.

**Not tag-blocking** for v1.4.0-rc.1 — pre-existing, doesn't reflect rc.1 polish
behavior. Pre-push gate must use `--no-verify` while this is open.

---

### TH-040: `test_corpus_spot_check` fails after v1.4 `datasheet-backed` → `datasheet_backed` key rename

**Severity:** LOW
**File:** `tests/test_invariants.py:490-528` (`test_corpus_spot_check`) and
`validate/validate_invariants.py` (the `check_invariants` invariant checker)
**Discovered:** 2026-05-15 during pre-push gate before v1.4.0-rc.1 tag

**Symptom:** `test_corpus_spot_check` walks `results/outputs/schematic/` looking
for ≥5 envelopes that have `detect_voltage_dividers` or `detect_rc_filters`
findings AND pass `check_invariants`. Currently finds 0 clean envelopes out of
49 eligible (sampled), failing with `"No clean outputs found for spot-check"`.

Every sampled envelope fails on the same invariant:
```
trust_summary.by_confidence keys {'heuristic', 'deterministic', 'datasheet-backed'}
                                 != {'heuristic', 'deterministic', 'datasheet_backed'}
```

**Root cause:** v1.4 breaking change documented in shared
`LOG-v1.4-progress.md` line 1079 — `trust_summary.by_confidence` aggregate key
renamed from `'datasheet-backed'` (hyphen) to `'datasheet_backed'` (underscore).
(Per-finding `confidence` VALUE stays `'datasheet-backed'`; only the rollup
key changed.) `validate_invariants.check_invariants` was updated to expect the
new key, but the cached corpus outputs in `results/outputs/schematic/` were
generated by a pre-v1.4 analyzer and still have the hyphenated key. Re-running
analyzers across the corpus would refresh them.

**Likely fix paths:**
- **Quick (5 min):** loosen `check_invariants` to accept either key shape during
  the v1.4 transition (treat `{datasheet-backed, datasheet_backed}` as
  equivalent for the by_confidence keys check). Mark as transitional with a
  "remove after corpus regen" comment.
- **Proper:** re-run `run/run_schematic.py` across the corpus (hours) to
  regenerate `results/outputs/schematic/` with the v1.4 key shape. Cascade to
  re-snapshot reference baselines for any drifts the regen surfaces.

**Not tag-blocking** — pre-existing harness-side data-staleness, not an
analyzer or producer bug. Pre-push gate must use `--no-verify` while this
is open.

---

### TH-041: `test_run_*_basic` integration tests fail with `KeyError: 'analyzer_type'` — `_first_output()` picks up `capability_mode.json`

**Severity:** LOW
**File:** `tests/test_run_integration.py:38-46` (`_first_output`) and call sites at
`:74` (schematic), `:93` (pcb), `:158` (spice via downstream chain)
**Discovered:** 2026-05-16 during first venv-backed full-suite run after v1.4.0-rc.1

**Symptom:** Three integration tests fail back-to-back:
```
tests/test_run_integration.py::test_run_schematic_basic - KeyError: 'analyzer_type'
tests/test_run_integration.py::test_run_pcb_basic      - KeyError: 'analyzer_type'
tests/test_run_integration.py::test_run_spice_basic    - AssertionError (downstream)
```

The schematic test asserts `data["analyzer_type"] == "schematic"` on the file
returned by `_first_output("schematic")`. That envelope key IS present in the
actual analyzer output (`commodorelcd.kicad_sch.json` has `analyzer_type` at
top level), but `_first_output` returns `capability_mode.json` instead because
it sorts alphabetically and only skips files starting with `_`.

**Root cause:** v1.4 added `capability_mode.json` as a sibling metadata file in
each analyzer output dir (B1/B2 absorption work, see `project_b1_b2_absorption`
memory). Pre-v1.4 the directory only contained `*.kicad_sch.json` envelopes, so
`_first_output`'s "first `*.json` that doesn't start with `_`" heuristic
worked by accident. Now `capability_mode.json` sorts before
`commodorelcd.kicad_sch.json` and is returned first — it lacks `analyzer_type`
because it's a metadata sidecar, not an envelope.

Repro:
```
$ ls results/outputs/schematic/jgrip/commodorelcd/
capability_mode.json          # ← picked up by _first_output
commodorelcd.kicad_sch.err
commodorelcd.kicad_sch.json   # ← what the test actually wants
```

Same pattern applies to PCB (`capability_mode.json` next to `*.kicad_pcb.json`)
and SPICE (chain-dependency on the schematic check).

**Likely fix:** Tighten `_first_output()` to filter for actual envelope files
(`*.kicad_sch.json`, `*.kicad_pcb.json`, `*.gbr.json`, etc.) or exclude the
specific metadata sidecar names (`capability_mode.json`, `capability_mode_ref.json`).
Skipping only `_`-prefixed files is no longer sufficient.

**Not tag-blocking** — pre-existing in rc.1, doesn't affect analyzer behavior.

---

### TH-042: `test_schema_completeness_zebra_x` fails — 7 new v1.4 detectors lack `SCHEMAS` entries

**Severity:** LOW
**File:** `tests/test_detection_schema.py:289-333` (`test_schema_completeness_zebra_x`)
and `SCHEMAS` dict (location TBD — likely under `regression/` or main-repo helper)
**Discovered:** 2026-05-16 during first venv-backed full-suite run after v1.4.0-rc.1

**Symptom:**
```
AssertionError: findings detector keys missing from SCHEMAS: [
  'audit_datasheet_coverage', 'audit_rail_sources', 'decoupling',
  'integrated_ldos', 'validate_pullups', 'validate_voltage_levels',
  'audit_sourcing_gate'
]
```

The test walks the `findings[]` array of a known-clean repo (`zebra-x`) and
asserts every detector short-name maps to an entry in `SCHEMAS`. Seven v1.4-era
detectors emit findings but have no schema entry, so the test fails the
"every detector has a schema" invariant.

**Root cause:** v1.4 added these seven detectors (auditors for datasheet
coverage, rail sources, integrated LDOs, sourcing gates; validators for
pullups and voltage levels; a `decoupling` analyzer family) but the harness
`SCHEMAS` dict was never updated alongside them. The `test_detection_schema`
ignore-list at `:312-316` only covers the older informational sections
(`design_observations`, `esd_coverage_audit`, etc.).

**Likely fix paths:**
- **Add schemas** for each of the 7 detectors (preferred long-term; the test
  exists specifically to force this discipline).
- **Add to ignore-list** if any of the 7 are intentionally schema-less
  informational sections (decide per-detector; treat as a stop-gap).
- **Process gap:** when adding a new detector to the analyzer, the schema-companion
  step is currently implicit. Worth a `CONTRIBUTING.md` or RUNBOOK Checklist
  note so v1.5 detector additions don't recreate the gap.

**Not tag-blocking** — pre-existing in rc.1, the seven detectors still produce
valid findings; the test is enforcing harness-side completeness, not analyzer
correctness.

---

### TH-044: `hierarchical` cross-section reads 0 repos — catalog's `max_hierarchy_sheets` field is stale (always 0)

**Severity:** LOW
**File:** `tools/generate_cross_sections.py:187-193` (`section_hierarchical`) +
`reference/repo_catalog.json` (`complexity.max_hierarchy_sheets` field)
**Discovered:** 2026-05-16 (LOG 9 hierarchy regression gate — scoped to a
hand-picked curated set because the `hierarchical` cross-section was empty)

**Symptom:**
```
$ python3 tools/generate_cross_sections.py --list
...
hierarchical                   0  Repos with multi-sheet hierarchical schematics
```

despite the corpus actually containing thousands of multi-sheet projects
(scan over `results/v14_gate/v14/schematic/*/snap.json` found 4,040 projects
with non-empty `hierarchical_labels`).

**Root cause:** The `section_hierarchical` filter reads
`complexity.max_hierarchy_sheets`, but that field is **always 0** in the
catalog — 5857/5857 entries have `max_hierarchy_sheets=0`. Catalog
generation populates the sibling `complexity.sheets` field correctly
(3407/5857 entries have `sheets > 1`), so the bug is specifically in the
catalog-generator code that derives `max_hierarchy_sheets`.

**Likely fix paths:**
1. **Generator-side fix** — `tools/generate_catalog.py` should populate
   `max_hierarchy_sheets` from the same source as `sheets` (or by walking
   v14 schematic snapshots and counting `hierarchical_labels`), then
   regenerate `reference/repo_catalog.json`.
2. **Filter-side fallback** — `section_hierarchical` could fall back to
   `complexity.sheets > 1` if `max_hierarchy_sheets` is 0 across the
   catalog. Lower-quality (treats single-file multi-page sheets the same
   as proper hierarchical projects with sub-sheets) but unblocks
   `--cross-section hierarchical` immediately.

LOG 9's hierarchy regression gate works around this by hand-picking 3
sub-sheets with confirmed differentials (see `CURATED_SET` in
`regression/run_hierarchy_regression_gate.py`). The gate is not blocked,
but the broader corpus-wide hierarchy regression testing this section is
meant to enable IS blocked until the field is repopulated.

**Not tag-blocking** — cosmetic gap in cross-section coverage; no
release-quality impact.

---

## Priority Queue

_19 open KH-* + 7 open TH-* issues. KH-338 HIGH; KH-339–KH-343 + KH-349/KH-350 MEDIUM; remainder LOW._
