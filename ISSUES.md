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

Last updated: 2026-08-31

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-402** (KH-401 filed 2026-08-31 during the
v2.2.x gate adjudication — cross_analysis VS-002 crash on
`board_outline.bounding_box: null`, pre-existing at v2.2.0, --full-only
trigger, verified identical at 43dad23 and ced9c8c; KH-395..400 filed 2026-08-31 during
v2.2.x Task 27 bookkeeping — item 11 remainder: KH-395 LOW bus_alias per-file
scoping merged project-wide; KH-396 MEDIUM rf_chains component_roles dict
key-order nondeterminism, pre-exists this batch, observed during Task 11's
hackrf-one A/B; KH-397 LOW GP-001 via-antipad credit (KH-392 fix) lacks
via-layer-span filter; KH-398 MEDIUM thermal assessment-level confidence
live twin of KH-387 at :444; KH-399 LOW EMC circle-outline edges fall through
to the generic (wrong) distance branch; KH-400 LOW project_config.py
trailing-comma regex not string-aware, KH-368's preserved-scope gap; KH-394 =
pcb_connectivity.py disconnected_pads
pair-order hash-nondeterminism, found by the v2.2.x determinism CI guard during
pre-landing sanity 2026-08-25 and FIXED-ON-DISCOVERY same session on v2.2.x-dev
commit 60d0f9e — never open, FIXED.md entry arrives with the v2.2.x adoption
handoff; KH-392/393 filed 2026-08-24 from GitHub
#39/#40 (curtisgalloway) — GP-001 via-antipad FP + power_rails never threaded
into analyze_pcb; both code+repro verified by main-repo agent, minimal-pair
fixture, evidence in the entries; KH-373..391 filed 2026-08-20 from the SacMap rev2 fresh-eyes soak review — 15 reviewer claims verified by 4 parallel agents (13 confirmed, 1 partial, 1 regression-theory refuted) + 4 verifier incidentals; evidence: kicad-happy sandbox Old-Reviews/sacmap-rev2/7/ + session-43 chat; KH-371/372 filed 2026-08-17 from GitHub PR #37 (fl4p) deliberately-left-out defects, code-verified — LC-ACT missing provenance fields, LC-005 single-source denominator semantics; KH-370 filed 2026-08-01 from GitHub #33, KH-220 description-substring oscillator FP, code+repro verified; KH-368/369 filed 2026-07-26 from verified external-review claims — JSONC string corruption + Action file-detect; KH-367 filed 2026-07-25, two more
hash-order nondeterminism sources; KH-366 filed 2026-07-24, RC-DET
nondeterminism found during v2.2 work; KH-357 filed 2026-07-24 from GitHub #31;
KH-358..365 filed 2026-07-24 from the verified subset of the KiCad-source audit
`docs/2026-07-24-kicad-parser-and-analysis-audit.md` — each entry cites its
KHPA finding ID). Next TH number: **TH-049** (TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 34 open issues (26 KH + 8 TH).

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

### KH-355: regulator FB-pin selection is first-match over dict order — arbitrary channel on multi-channel regulators

**Severity:** LOW
**File:** `skills/kicad/scripts/signal_detectors.py:1603-1610`
**Discovered:** 2026-07-16 (v2.1 gate adjudication, Siegmundshof93/kicadPCBs)

**Symptom:** `for pname ... in ic_pins.items(): if pn_parts & {"FB","VFB","ADJ","VADJ"}: if not fb_pin: fb_pin = ...`
picks the first FB/ADJ-named pin in dict insertion order. On dual-channel
regulators (e.g. U4 with ADJ1/ADJ2 on Siegmundshof93 power_management),
only one channel is analyzed and WHICH one depends on net-map enumeration
order: f50aa6e's pwr_flag point registration flipped the pick from ADJ1
(divider on __unnamed_0 → heuristic Vout=1.62V seeding rail_voltages) to
ADJ2 (+1V2, no divider → no estimate). Neither pick is wrong per se, but
the output is order-coupled and single-channel.

**Impact:** DO-DET regulator Vout estimates (and their rail_voltages
seeding) appear/disappear across otherwise-unrelated topology changes;
multi-channel regulators only ever get one channel estimated.

**Fix sketch:** iterate FB/ADJ pins deterministically (sorted) and/or
analyze each channel's divider independently.

---

### KH-364: connectivity graph never joins tracks to zone fill (and ignores arc tracks) (audit KHPA-005 subset)

**Severity:** MEDIUM
**File:** `skills/kicad/scripts/pcb_connectivity.py:421-423` (zones probe only
pads/vias), `:198` (segments only — no arcs), `:369-383` (endpoint buckets, no
mid-segment T-joins)
**Discovered:** 2026-07-24 (audit KHPA-005; code-verified same day)

**Symptom:** Zone attachment considers only `kind in ('pad','via')`; a
pad→track→pour→track→pad path whose only bridge is the pour splits into
separate islands. Arc track objects are extracted by analyze_pcb (:6605) but
never enter the graph. Mid-segment T-intersections aren't detected (endpoint
buckets at 0.05mm only). Connectivity exceptions are swallowed at
analyze_pcb.py:6609-6615 (`except: pass`) with no trust-state transition.

**Impact:** False island/plane-split conclusions (PS-002/GP-001/RP-002 class —
the same family #24 fixed for via layer-spans) on boards where copper pours
bridge track endpoints, and on any board using arc tracks. **Scope note:** this
is the top candidate for correctness-floor "brick two" after #25 —
kicad-cli/ratsnest oracle applies. The `except: pass` should be fixed cheaply
and early (surface a degradation note).

---

### KH-365: BOM manager double-counts twice-instantiated sheets and misses `private` properties (audit KHPA-012 subset, direction corrected)

**Severity:** MEDIUM
**File:** `skills/bom/scripts/bom_manager.py:532-544` (visited-at-dequeue),
`:167-168` (property regex); `kicad_sexp.py:58-62` (no unescaping)
**Discovered:** 2026-07-24 (audit KHPA-012; code-verified same day — the audit
had the count direction BACKWARDS)

**Symptom:** (1) `analyze()` marks files visited at dequeue but appends at
discovery under a stale check — a child sheet referenced twice by one parent
enters `files_to_parse` twice and is counted TWICE (the audit claimed
once/undercount; actual behavior is overcount — either way wrong quantities).
(2) The property regex requires `(property "` immediately, so
`(property private "Name" "Value")` is invisible — edits can create a duplicate
property instead of updating the private one. (The main sexp_parser
get_property path handles `private` fine; only the BOM regex path is affected.)
(3) Sheetfile paths are used without KiCad string unescaping.

**Fix direction:** migrate BOM/edit tools onto the shared sexp_parser loader
(dedupe at discovery, real property parsing); interim: fix the visited-set
order and widen the regex.

### KH-373: CP-003 touch-pad GND clearance measured origin-to-zone-BBOX — reports "deterministic" 0.0mm for enclosing pours (real clearance 1.00mm)

**Severity:** HIGH (78% corpus FP rate: 666/854 CP-003-emitting boards report 0.0mm, all at confidence "deterministic")
**File:** `skills/kicad/scripts/analyze_pcb.py:5335-5364` (`_nearest_zone_copper_distance`), caller :5570-5613
**Discovered:** 2026-08-20, SacMap rev2 fresh-eyes soak (run 7, report at kicad-happy sandbox Old-Reviews/sacmap-rev2/7/) — claim B1, code+fixture+corpus verified

**Symptom:** distance is FOOTPRINT ORIGIN point → zone AXIS-ALIGNED BBOX, with dx/dy clamped to 0 when the point is inside the box (:5358-5360). Any pour surrounding a touch pad yields exactly 0.0. `filled_bbox` basis (KH-339, v2.1) is the bbox over ALL filled vertices, so keyhole cutouts don't help; and :5584 labels precisely that branch "deterministic". Even with polygon math the origin-point choice understates a 15mm pad by 7.5mm. Skill guidance keys the Espressif 1mm-minimum comparison off this number.
**Fix direction:** pad-outline → filled-polygon-edge distance; `ZoneFills` already stores the polygon lists (:130-136) and `_dist_point_to_segment` exists (:195) — verified to recover the true 1.0mm on the repro fixture. Budget: CP-003 value changes corpus-wide (666 boards), possible finding disappearances where real clearance passes threshold. Supersedes the "touch-pad clearance metric" roadmap feature framing — this is a correctness defect.

### KH-374: sleep_current_audit systematically wrong on battery designs — EN-pin-presence ≠ disableable, rail-disable zeroing ignores always-on, battery rails dropped by name-parse voltage failure

**Severity:** HIGH (headline realistic_total_uA=0.0 on boards whose true floor is 40-60µA; battery designs are the feature's audience)
**File:** `skills/kicad/scripts/analyze_schematic.py:6809-6880` (`analyze_sleep_current`), `:5001-5017` (`_estimate_rail_voltage`), `kicad_utils.py:223`
**Discovered:** 2026-08-20, SacMap soak claim B2; reproduced on corpus board bastian2001/LiPo-Charger-Hardware

**Symptom:** (a) :6809-6818 sets disableable from EN/SHDN/CE pin NAME presence only — never consults connectivity; `analyze_power_sequencing` (:7752-7754) correctly derives `en_source: "always_on"` for EN-tied-to-VIN in the SAME output, and the two never talk. (b) `_disableable_rails` (:6832-6845) zeroes every divider/pull-down on such rails (:6867-6880) with no check the rail actually turns off (reproduced: rail zeroed while its own regulator's EN is tied to that rail). (c) rails whose voltage can't be parsed from the NET NAME are dropped wholesale at :6627-6629 — `+BATT`/`VBAT`/`BATTERY` all return None — so the largest resistive path (battery divider) vanishes while VD-DET reports it two sections away. The analyzer's own `rail_voltages` map is not consulted.
**Fix direction:** consult power_sequencing en_source; walk regulator input/battery rails; fall back to `rail_voltages`/regulator vin data before dropping a rail. Budget: sleep_current_audit values move on most battery boards.

### KH-375: power_budget misses loads — ICs-only, first-pin-on-net break bug drops EN-tied-to-VIN regulators, power-name heuristic gap

**Severity:** HIGH (silently under-reports; consumed by analyze_thermal.py:247-249 as regulator Iout and emc_formulas.py:1078 power tree — see KH-386/KH-377 cascades)
**File:** `skills/kicad/scripts/analyze_schematic.py:7586-7652` (`analyze_power_budget`)
**Discovered:** 2026-08-20, SacMap soak claim B3; reproduced on 4/14 sampled corpus boards (74HC595 ~{SRCLR}+VCC, BME280 CSB-before-VDD, RoboMausV2 "3.3V" rail)

**Symptom:** (1) loads = `comp["type"]=="ic"` only (:7586-7588) — LEDs/connectors/fuses/discretes never counted; series-element-fed loads on derived nets invisible. (2) Pin-qualification bug: outer loop iterates ref_pins but the test re-scans `nets[net]["pins"]`, evaluates the FIRST pin of that component on the net, and `break`s unconditionally (:7590-7617) — an IC whose non-power pin sorts first on a shared net is dropped from the rail entirely (exactly EN-hardwired-to-VIN regulators). (3) rails failing `is_power_net_name` with no #PWR symbol get zero loads. Result on the soak board: +5V estimated_load_mA 0 with ~52mA LEDs + 500mA USB; +BATT missing U3.
**Fix direction:** evaluate the iterated pin (pnum), not the first match; widen load classes deliberately (budget!); consider net-derived load tracing later. Budget: estimated_load_mA + downstream thermal/EMC movement — MUST be gated together with KH-386.

### KH-376: get_regulator_features/get_mcu_features called WITHOUT project_dir — every datasheet-authority gate in validation_detectors.py (+1 EMC site) permanently inert

**Severity:** HIGH (datasheet-backed suppression/verification paths dead code in production; extractions exist but resolve to /tmp fallback)
**File:** `skills/kicad/scripts/validation_detectors.py:484, :580, :922, :1049`; `skills/emc/scripts/emc_rules.py:2049`; root cause `skills/datasheets/scripts/datasheet_extract_cache.py:74-101` (`resolve_extract_dir` falls through to temp-dir fallback); `kicad_types.py:64-78` (AnalysisContext has no project_dir field)
**Discovered:** 2026-08-20, SacMap soak claim B4 (visible symptom: PS-001 "PG status unknown ... (no datasheet extraction)" beside ics_with_extractions:4 in the same JSON); isolation-verified both call shapes

**Symptom:** all five sites call the features API with no project_dir/extract_dir → `resolve_extract_dir()` → `/tmp/kicad-happy/datasheets/extracted` → None → "no data" branch always taken. Verified: same MPN with project_dir returns has_pg=False (power_good_pin:null handled correctly at datasheet_features.py:178 — cache format was never the problem, KH-337 hypothesis wrong here). Had lookup worked, PS-001 would emit NOTHING for a no-PG part (:1052 continue) — fix is not wording. Affected gates: PS-001 PG check, VM-001 EN-threshold suppression, PR-004 USB native-PHY suppression, regulator VIN rail estimation, one emc_rules datasheet path.
**Fix direction:** plumb project_dir through AnalysisContext (new field) + emc_rules call site. Budget: PS-001 disappearances on extraction-bearing projects; VM-001/PR-004 suppression behavior changes — corpus mostly has no extraction caches so gate movement should be small; contract fixtures DO (harness tests/fixtures/datasheets/).

### KH-377: EMC PD-001 counts series/feedforward caps as decouplers (manufactures error findings), unconfigurable 2×0.5A transient default, grid-point sweep ceiling, raw-float formatting, count/list mismatch

**Severity:** HIGH (on the soak board the +5V error finding is ENTIRELY caused by the 220pF feedforward cap — removal eliminates every anti-resonance peak; proven by execution)
**File:** cap collection `skills/kicad/scripts/signal_detectors.py:2017-2053` (accepts any capacitor touching the output rail, other terminal never checked); `skills/emc/scripts/emc_rules.py:3296-3304` (i_transient = 0.5 doubled when power_dissipation absent — which KH-375 makes common), :3321-3322 (hard 1kHz-1GHz sweep; 316.2MHz = 10^8.5 grid point, no board-relevance gate), :3334 (hard-coded HIGH severity), :3343 (`str(farads*1e6)` no rounding → "0.00021999999999999998µF", also hits 100nF), :3342-3343 (count=len, list=[:4], no "of N")
**Discovered:** 2026-08-20, SacMap soak claim B5, all five sub-claims reproduced

**Symptom/fix:** filter rail caps to shunt-to-GND topology before PDN modeling; surface + config the transient assumption (no path exists today — run_all_checks receives only standard/severity/spice_backend, analyze_emc.py:467-470); clamp sweep or demote out-of-band peaks; format engineering units; fix count/list. Budget: PD-001 findings change class-wide (any rail with a feedback divider feedforward cap).

### KH-378: EMC GP-001 has no touch/sense-net exemption — deliberate touch copper voids become the board's worst EMC finding

**Severity:** MEDIUM
**File:** `skills/emc/scripts/emc_rules.py:332-394` (`check_return_path_coverage`; severity ladder :362-370 coverage-only), :107-117 (`_is_high_speed_net` — no touch concept)
**Discovered:** 2026-08-20, SacMap soak claim B6 (TOUCH_1 79% coverage → error; recommendation text "or fill the void" is actively wrong for the net)

**Fix direction:** consume CP-003 touch-pad identification from pcb.json (present in findings; carries refs only, `nets: []` — needs ref→net join via footprints[].pads[].net_name; consider also emitting nets on CP-003, cheap producer fix) and downgrade/annotate touch nets in GP-001/RP-001. Budget: severity demotions on touch boards.

### KH-379: DC-001 cap association requires NO shared net — spurious warnings AND suppression of the correct DC-002; shared_nets/esd_bypass fields dead; ESD-only boards skip ESD-bypass analysis entirely

**Severity:** HIGH (a topologically irrelevant GND-only cap within 10mm both fires a spurious DC-001 and gates off DC-002's correct "no decoupling cap" — isolated by execution)
**File:** `skills/kicad/scripts/analyze_pcb.py:1994-2069` (`analyze_decoupling_placement`: :2012-2025 any cap ≤10mm appended unconditionally, `shared` computed and stored but never filtered on; :2027-2033 sort by distance alone; :2006-2007 early-return tests `ics` which EXCLUDES ESD/TVS parts, making the esd_ics block :2037-2067 unreachable on ESD-only boards); consumer `skills/emc/scripts/emc_rules.py:496-560` (DC-001 reads closest_cap_mm only; DC-002 gated by mere presence of a decoupling_placement entry). Repo-wide: `shared_nets` (written :2023/:2055/:6510) and `"category": "esd_bypass"` (:2064) have ZERO readers.
**Discovered:** 2026-08-20, SacMap soak claim B7 (verified stronger than reported) + verify-agent incidental

**Fix direction:** require a shared non-GND (power) net for association; consume esd_bypass category for ESD-specific messaging; fix the early-return guard. Budget: DC-001 disappearances + DC-002 appearances corpus-wide — budget both rules together.

### KH-383: min-drill blind to footprint pad drills — dfm min_drill_mm via-only AND design-rule check never receives footprints

**Severity:** HIGH (fab-facing number wrong; the board's own min_through_hole_diameter is structurally unenforceable against half its holes)
**File:** `skills/kicad/scripts/analyze_pcb.py:4292-4296` (dfm drill scan reads board via list only), :3100-3113 (same in via facts), :4575-4619 (`analyze_design_rule_compliance(tracks, vias, project_settings)` — no footprints param; min_via_drill vs min_through_hole_diameter). Pad drills ARE parsed (:710-720); only consumer is an unrelated proximity check (:5122).
**Discovered:** 2026-08-20, SacMap soak claim B9 (12×0.2mm footprint-embedded PTH thermal vias under U1, board rule 0.3mm, reported min 0.3 + "compliant: true"); fixture-reproduced

**Fix direction:** include pad drills in both paths; pass footprints into design-rule compliance. NOTE: LIMITS_STD min_drill=0.2 (:4066) means DFM alone stays silent at 0.2mm — the project-rule path is the one that must see pads. Budget: min_drill_mm value changes + new DR violations on boards with small pad drills.

### KH-386: thermal silently drops regulators whose rail shows zero load — partial assessment presents as complete (score 97-100)

**Severity:** HIGH (hotter of two identical regulators never evaluated, no note anywhere; compounds with KH-375 which produces the zero loads)
**File:** `skills/kicad/scripts/analyze_thermal.py:236-272` (`_estimate_all_power_dissipation` — bare `continue` at :253 on `not iout_a`), :1090-1097 (missing_info covers assessed components only), :756-762 (score None only when list fully empty)
**Discovered:** 2026-08-20, SacMap soak claim B13; end-to-end fixture repro (two identical TPS61023, one dropped, score 97, dropped ref appears NOWHERE)

**Fix direction:** emit a capability note / skipped-components list ("Uassessed n of m power components; U2 skipped: no load estimate") — fail-loudly posture; real fix arrives with KH-375 load accounting. Budget: additive field + note text only, until KH-375 lands (then joint thermal movement).
Context (structural, not this bug): trust_level "low" + provenance_coverage 0.0 are constants for thermal — confidence distribution drives trust (finding_schema.py:399-409) and analyze_thermal never calls make_provenance. PR #37's evidence_source flip did NOT alter trust_level (verified by execution).

### KH-395: bus_alias resolution merges aliases project-wide, but KiCad scopes them per schematic file

**Severity:** LOW (only matters when two schematic files in one hierarchy
define aliases of the same name with different member lists — rare, but
silently wrong when it happens)
**File:** `skills/kicad/scripts/analyze_schematic.py:9008-9012`
(`merged_bus["bus_aliases"].extend(...)` merges every sheet's aliases into
one project-wide list before the bus pass reads them — no per-file
namespace); consumed at `:1461-1462`
(`bus_aliases = {a["name"]: a["members"] for a in ...}` — bare-name dict
key); parsed per-sheet with no `_sheet` tag at `:1276-1289`
**Discovered:** 2026-07-24, roadmap item 11 (v2.2 final-review minors);
filed 2026-08-31 during Task 27 bookkeeping

**Symptom:** KiCad scopes `bus_alias` definitions to the schematic file that
declares them — an alias named `PHASES` in one sheet and a different
`PHASES` in another sheet are two distinct, non-conflicting definitions.
kicad-happy instead builds one project-wide `dict[name] -> members`, fed
from the flat merged list — a same-name alias on a later-processed sheet
silently overwrites the earlier one (last-wins), so `expand_bus_name()` can
resolve a group bus (`{PHASES}`) to the WRONG sheet's member list on a
project that reuses an alias name across independent sheets.

**Fix direction:** key the alias dict by (sheet, name) instead of bare name,
matching how bus labels are already sheet-scoped (`BusGraph` is per-sheet).
Needs the sheet index threaded from `bus_alias` parsing (:1276-1289, per-file
parse function — no `_sheet` field exists on its output today) through to the
`bus_aliases` dict build. Budget: alias-name reuse across sheets is uncommon
in the corpus (worth a quick scan before gating); low risk of broad movement.

### KH-396: rf_chains `component_roles` dict key order is hash-seed-dependent — pre-existing nondeterminism, invisible to the v2.2.x determinism CI guard

**Severity:** MEDIUM (silent byte-instability on any board with 2+ RF
components across categories — same class as KH-366/367/382, just not yet
caught because no guard fixture carries RF content)
**File:** `skills/kicad/scripts/domain_detectors.py:1215`
(`"component_roles": {ref: _rf_role(ref) for ref in all_rf_refs}` — dict
comprehension iterates `all_rf_refs`, a plain `set()` built at :1055/:1106);
note :1114 already computes `rf_ref_list = sorted(all_rf_refs)` for a
DIFFERENT field in the same function, so the sorted list exists locally but
isn't reused for `component_roles`
**Discovered:** 2026-08-2x, observed by the Task 11 (KH-370) implementer
during a double-run A/B on
`repos/greatscottgadgets/hackrf/hardware/hackrf-one/hackrf-one.kicad_sch`
— same code, two process runs, `rf_chains[0]["component_roles"]` key order
differed; pre-exists this batch, out of scope for KH-370, reported as a
concern in the main-repo SDD workspace `task-11-report.md`

**Fix direction:** iterate `sorted(all_rf_refs)` (or reuse `rf_ref_list`)
when building `component_roles` at :1215. Also add an RF-bearing board (e.g.
a trimmed hackrf-one fixture) to the determinism CI guard's fixture set —
the guard is currently blind to this class because none of its fixture
boards carry RF components. Budget: `component_roles` key order only, no
value changes — should be gate-invisible once fixed (byte-stability
improvement, not a finding-content change).

### KH-397: GP-001 via-antipad credit (KH-392 fix) doesn't check the via actually spans the probed reference layer

**Severity:** LOW (KH-392 fixed the common through-via case; this is the
residual gap on multi-layer boards using blind/buried vias — a narrower,
rarer condition)
**File:** `skills/kicad/scripts/analyze_pcb.py:1913-1920`
(`_in_via_antipad` credits ANY via within `vr + antipad_clearance` of the
sample point, regardless of layer span); via layer data is already parsed
and available at `:1090` (`via_info["layers"] = [l for l in
layers_node[1:] if isinstance(l, str)]` — KiCad's `(layers X Y)` endpoint
pair, blind/buried-aware)
**Discovered:** 2026-08-31, follow-up during KH-392 fix review —
deliberately left out of KH-392's scope per the over-engineering guard

**Symptom:** `_in_via_antipad` (added by the KH-392 fix) never consults
`v.get("layers")`. On an all-through-via board this is harmless (every via
spans every layer). On a board mixing through-vias with blind/buried vias,
a blind via that does NOT reach the probed `opp_layer` can still credit a
sample as "expected antipad void" near a genuine reference-plane gap on
that layer — masking a true GP-001 finding. Note: a naive fix that
requires `opp_layer in via["layers"]` would be WRONG on its own —
`layers` stores only the two endpoint layers of the via's span (e.g.
`["F.Cu", "In2.Cu"]`), not every inner layer the via physically passes
through, so a correct fix needs stackup-ordered layer-span logic (the same
machinery GH #24's `_expand_copper_layers` already has for plane
connectivity), not a literal membership check.

**Fix direction:** thread stackup order (already available via the #24
stackup machinery) into `_in_via_antipad` so it credits a via only when the
probed layer falls within — not just at the two endpoints of — the via's
physical span. Budget: narrows KH-392's fix on multi-layer/blind-via boards
only; through-hole-only boards (the corpus majority) unaffected.

### KH-398: TH-DET assessment-level `confidence` still claims "deterministic" for `package_table` — live twin of KH-387, different field

**Severity:** MEDIUM (every package_table TH-DET assessment currently
claims "deterministic" confidence; large class — fires on every board
where thermal estimates a package via footprint-regex lookup rather than
"default")
**File:** `skills/kicad/scripts/analyze_thermal.py:444`
(`"confidence": "heuristic" if rtheta_source == "default" else
"deterministic"` — the assessment-construction site; contradicts the
adjacent comment at :445-447 explaining why package_table can't claim
datasheet-grade provenance, and contradicts the sibling
`_thermal_confidence()` finding-level helper a few lines below, which
already treats package_table as heuristic post the KH-387 fix)
**Discovered:** 2026-08-31, found while verifying KH-387's fix at :473 —
that fix only touches the FINDING-level confidence helper
(`_thermal_confidence`, feeding TS-001..005 findings); this is a separate
ASSESSMENT-level field (feeds TH-DET assessments directly, same
trust_summary drift mechanism KH-387 describes)

**Fix direction:** same rationale as KH-387 — package_table is a
footprint-regex average, not per-MPN data; line 444 should read
`"heuristic" if rtheta_source in ("default", "package_table") else
"deterministic"`. Budget: unlike KH-387 (see its updated entry — corpus
movement there turned out to be zero), this field has NO `tj_max_source`
safety net catching it first, so the movement here is real and should be
budgeted: every package_table board's TH-DET assessment confidence flips
to heuristic on this fix.

### KH-399: EMC `_point_to_edges_min_distance` reads a nonexistent `start` key for circle-type board-outline edges — bogus BE-001 distances

**Severity:** LOW (only affects boards with `gr_circle` board-outline
edges — rectangular/polygon outlines are the corpus majority; same family
as KH-357's rect-diagonal bug, narrower trigger)
**File:** `skills/emc/scripts/emc_rules.py:2257-2294`
(`_point_to_edges_min_distance` — the `if/elif` chain handles
`rect`/`line`/`arc-with-mid`, and everything else, including `circle`,
falls to the generic `else` at :2289-2291 which reads `edge.get('start',
[0, 0])`); producer shape at `skills/kicad/scripts/analyze_pcb.py:1375-1383`
(`gr_circle` emits `{"type": "circle", "center": [...], "end": [...]}` —
no `start` key at all)
**Discovered:** 2026-08-31, code review during Task 27 bookkeeping;
live-verified (`edge.get('start', [0,0])` confirmed to default to `[0, 0]`
for a circle-shaped edge dict)

**Symptom:** any circle-shaped board-outline edge is measured as a line
segment from the origin `(0, 0)` to the circle's `end` point (one point on
its circumference) instead of the actual circular boundary — BE-001
distances near a circular board edge are essentially random, tied to the
board's position relative to the KiCad origin rather than to the real
edge. `cross_analysis.py`'s NR-001 already hit this and explicitly punted
(`:530` — "circle / polygon / curve: not yet implemented for NR-001");
`_point_to_edges_min_distance` should do the same rather than silently
computing a wrong number.

**Fix direction:** either mirror NR-001's explicit skip (exclude circle
edges from the min-distance scan, accepting under-coverage over a wrong
number) or implement true point-to-circle distance (`abs(dist(point,
center) - radius)`, using the `end` point to derive radius). Budget:
BE-001 finding/distance changes on the (small) subset of corpus boards
with circular outlines.

### KH-400: `_TRAILING_COMMA` regex in project_config.py's JSONC loader is not string-aware — corrupts string values containing `,}` or `,]`

**Severity:** LOW (narrow trigger — a config string value ending in a
literal `,}` or `,]` sequence; most config string values are net/rule-ID
globs that don't contain those sequences)
**File:** `skills/kicad/scripts/project_config.py:32`
(`_TRAILING_COMMA = re.compile(r',\s*([}\]])')`), `:76`
(`_TRAILING_COMMA.sub(r'\1', ''.join(out))` — applied to the FULL text,
including string-literal contents, after the string-aware comment-stripping
loop at :42-75 has already run)
**Discovered:** 2026-08-31, code review during Task 27 bookkeeping;
live-verified: `_strip_jsonc('{"a": "foo,}bar"}')` returns `'{"a":
"foo}bar"}'` — the comma inside the string literal is silently deleted

**Symptom:** `_strip_jsonc`'s comment stripper (the KH-368 fix) IS
string-aware — it tracks `in_string` state character-by-character and
leaves comment-like sequences inside strings untouched. But the
trailing-comma cleanup that runs afterward (:76) is a single regex
substitution over the whole already-joined text, with no knowledge of
string boundaries. A JSONC string value containing `,}` or `,]` (e.g. a
suppression note or datasheet URL fragment ending that way) has its comma
silently deleted — same class of silent corruption as KH-368's original
`/* */`-in-string bug, but KH-368's fix left this half of the job
preserved-as-is (KH-368's own fix-direction text called for BOTH comments
AND trailing commas to become string-aware; only comments were).

**Fix direction:** extend the same `in_string`-tracking scanner in
`_strip_jsonc` to also strip a trailing comma only when it's immediately
followed (skipping whitespace) by `}`/`]` OUTSIDE a string — i.e. fold
`_TRAILING_COMMA`'s job into the existing state machine instead of a
separate regex pass. Budget: narrow — config strings ending exactly in
`,}`/`,]` are rare; low corpus-gate risk, but worth a quick scan of corpus
`.kicad-happy.json` files for the pattern before treating this as
cosmetic-only.

### KH-401: cross_analysis VS-002 crashes when pcb `board_outline.bounding_box` is JSON null — `.get(key, {})` default doesn't guard explicit null

**Severity:** MEDIUM (hard crash of the whole cross_analysis run — no output
at all — on any --full pcb JSON whose board_outline carries
`"bounding_box": null`; plain-mode runs skip VS-002 earlier via the
no-vias/vias-shape guard, which is why the corpus gate never hit it)
**File:** `skills/kicad/scripts/cross_analysis.py:826-828`
(`check_via_stitching_density`: `bbox = outline.get('bounding_box', {})` →
`bbox.get('width', 0)` — the `{}` default only covers a MISSING key, not an
explicit null); producer question: `analyze_pcb.py --full` emitted
`"bounding_box": null` alongside a non-empty `edges` list on the repro board
— why bbox computation fails with edges present is a companion question.
**Discovered:** 2026-08-31, during the v2.2.x gate's targeted --full chain
A/B (NR-001 gate-blindness coverage); PRE-EXISTING — identical traceback at
`43dad23` (v2.2.0) and `ced9c8c`, NOT a v2.2.x regression.

**Repro:** `analyze_pcb.py repos/sparkfun/SparkFun_IoT_RedBoard-RP2350/Hardware/SparkFun_IoT_RedBoard-RP2350.kicad_pcb --full -o pcb.json`
then `cross_analysis.py -s <schematic.json> -p pcb.json` →
`AttributeError: 'NoneType' object has no attribute 'get'` at :828.

**Fix direction:** `bbox = outline.get('bounding_box') or {}` (and audit the
sibling `.get(key, {})` sites in cross_analysis for the same null-vs-missing
gap); separately, main-repo may want the ran/skip path to record VS-002 as
skipped rather than crashing the whole run — the KH-381 checks_run manifest
makes that the natural shape. Budget: none until fixed (crash → no output).

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

### TH-047: BUGFIX-KH-198-01 corpus anchor lost — LC-DET no longer fires on Caffeinated-AFTONSPARV; lock needs a new host board

**Severity:** LOW
**File:** `regression/bugfix_registry.json` (KH-198 entry, `assertions` now
empty with `corpus_anchor_lost` note)
**Discovered:** 2026-08-20 (v2.2.0 combined corpus regen adjudication)

**Symptom:** the KH-198 regression lock (LC-DET components exactly
`[C5, L1]`, guarding the capacitor-ref dedup fix) failed at regen with
`rule_id=LC-DET not found`. Root cause is NOT a KH-198 regression: the
board is in the v2.0 mirror-fix affected set
(`results/v20_mirror_gate/affected_repos.txt`) and the ratified
connectivity change dissolved the L1/C5 LC group, so `detect_lc_filters`
legitimately no longer fires there (verified absent at `fc94a3d` and
`43dad23`; v2.1/v2.2 gate diff records show zero movement — the change
predates the v2.1 baseline).

**Fix direction:** find another corpus board where LC-DET fires with a
capacitor whose ref collides across sub-projects (the KH-198 trigger
shape), re-anchor the registry assertion there, and regenerate. Until
then KH-198 is covered only by main-repo unit tests.

---

## Priority Queue

_26 open KH-* + 8 open TH-* issues (post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
