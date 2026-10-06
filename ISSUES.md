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

Last updated: 2026-10-06

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-442** (KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
PR #41 fold adoption — no-connect mid-span connectivity, externally
reported+fixed by danielboston38, FIXED-direct, never open here;
KH-401 filed 2026-08-31 during the
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
KHPA finding ID). Next TH number: **TH-059** (TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 filed 2026-10-05 — generate_bugfix_assertions.py merges by assertion id and never updates a changed expected value, so a registry re-anchor silently does not land; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 48 open issues (33 KH + 15 TH).

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

### KH-421: hash-seed nondeterminism on BerkeleyLab/Marble U54 (STM32F207) — PS-001 and a DO-DET "Regulator U54 missing capacitors" vary with PYTHONHASHSEED (539/538/537 findings at seeds 0/1/3)

**Severity:** LOW-MEDIUM (pre-existing — identical at b008afa and 9fbbb26;
KH-366/367 class; invisible to every harness gate because the gate pins
`PYTHONHASHSEED=0`, so it needs the determinism-guard treatment, not a gate)
**File:** `skills/kicad/scripts/analyze_schematic.py` (PS-001 power-sequencing
+ DO-DET regulator-capacitor observation on U54; some set-ordered iteration
upstream of both)
**Discovered:** 2026-10-05, main-repo agent, KH-418 fix-wave determinism check
(`follow-up-fix-wave-report.md`); filed by the harness 2026-10-06

**Fix direction:** find the set/dict-order dependence feeding U54's regulator
/ capacitor association (sorted iteration or a stable key), add the Marble
root sheet to the main-repo determinism CI guard's seed sweep (1/7/123).

**Gate budget (when fixed):** PS-001 / DO-DET content on Marble only; count
stabilises at one of 537-539.

### KH-422: `--full` pcb analysis spends ~85-90 s on NLoy Touch_Keyboard_10x12 in `_point_in_polygon` (124,904 calls) — pre-existing performance cost, not KH-413/KH-420

**Severity:** LOW (performance only; 87 s at v2.3.0 on the main-repo box,
unchanged by KH-420 which fixed the `--only-deterministic` 11× regression)
**File:** `skills/kicad/scripts/analyze_pcb.py` (`zones_at_point` /
`has_copper_at` / `fill_regions_at_point` called from
`analyze_return_path_continuity`) and `pcb_connectivity.build_connectivity_graph`
**Discovered:** 2026-10-05, main-repo agent, KH-420 profiling
(`task-B-report.md`); filed by the harness 2026-10-06

**Fix direction:** the KH-420 per-fill segment grid applied to point-in-polygon
queries — the per-fill bbox prefilter already exists; add an edge-crossing
index per fill so each query walks only the segments in its grid column.
Target: the NLoy `--full` run under 30 s. Corpus relevance: the harness
`run_pcb.py` runs `--full --proximity` under a 120 s cap, so touch-pad-dense
boards sit in the TH-055 timeout class today.

**Gate budget (when fixed):** none (exact algorithm, no output change —
verify with the KH-420 equality-query method).

### KH-423: legacy `.sch` parser skips truly-empty `""` custom fields entirely (`elif field_num >= 4 and field_val:`) — distinct from the KH-414 whitespace path

**Severity:** LOW (pre-existing; an empty-string MPN/DigiKey/… field in a
KiCad 5 schematic is dropped instead of recorded as present-but-blank, so
"field exists but is empty" and "field absent" are indistinguishable on the
legacy path; the KH-418 blank-value tiering could not be mirrored for `""`
on that branch)
**File:** `skills/kicad/scripts/analyze_schematic.py` (legacy `.sch` field
loop, `elif field_num >= 4 and field_val:`)
**Discovered:** 2026-10-05, main-repo agent, KH-418 final wave (rider note);
filed by the harness 2026-10-06

**Fix direction:** record custom fields with empty values (name present,
value `""`) so the modern and legacy paths agree; `tests/fixtures/kh418/
legacy_blank_primary.sch` is the natural fixture to extend with a `""`
field.

**Gate budget (when fixed):** nil (legacy boards whose `""` fields currently
vanish gain blank entries; no MPN value changes).

### KH-416: peer sheets' own inner `(sheet ...)` hierarchy never gets `_is_sheet_pin` / `_hier_ns` tagging — bus-pass role misclassification on hybrid Altium-flat projects

**Severity:** LOW (latent; found while ruling out a KH-409 candidate, not
investigated or fixed)
**File:** `skills/kicad/scripts/analyze_schematic.py` (~l.9105-9121 main
hierarchy "namespace hierarchical labels" post-process; bus-pass role
classification `"pin"` vs `"hier"` ~l.1477)
**Discovered:** 2026-10-04, main-repo agent, KH-409 round-1 investigation
(`.superpowers/sdd/2026-10-04-v2.3.1-maintenance-batch/kh409-repro.md`,
"Follow-up not pursued"); filed by the harness 2026-10-05

**Symptom / root cause:** a peer sheet's own inner `(sheet ...)` hierarchy
(the genuine "hybrid" shape the merge loop's comments describe) never runs
the post-process the main hierarchy loop runs, so `_is_sheet_pin` /
`_hier_ns` are never set on a peer's own sheet-pin pseudo-labels and the
bus pass would classify them as `"hier"` instead of `"pin"`. Distinct from
KH-409 (bus_wires / bus_entries `_sheet` tagging, fixed in v2.3.1).

**Fix direction:** run the namespace post-process per peer sheet's inner
hierarchy; fixture = Altium-flat project whose peer sheet contains a nested
sheet with a bus crossing the sheet pin. Candidate for a
hybrid-hierarchy-nesting task.

**Gate budget:** none until fixed (bus_topology roles on hybrid projects).

### KH-417: `_pad_on_layer` treats `np_thru_hole` pads carrying a `*.Cu` layer wildcard as copper

**Severity:** LOW (inert at the only current call site — the CP-003
touch-pad gate reaches `_pad_on_layer` only for pads already known to be
touch candidates — but a sharp edge for any future caller that reads
`_pad_on_layer` as "has copper on this layer")
**File:** `skills/kicad/scripts/analyze_pcb.py` (~l.5636 `_pad_on_layer`)
**Discovered:** 2026-10-04, main-repo agent, v2.3.1 Task 6 review; filed by
the harness 2026-10-05

**Fix direction:** exclude `np_thru_hole` pads (and pads with `layers: []`)
before the wildcard match; add the explicit `layers: []` / NPTH case to the
KH-413 fixture.

**Gate budget:** none (no live behaviour change).

### KH-441: via-analysis `via_in_pad` attributes a via to the FIRST pad whose outline contains it — ambiguous on footprints where a pin pad's rotated extent and the exposed pad both contain the via (attribution + `same_net` flip with pad order)

**Severity:** LOW (fact-field attribution; surfaced by the KH-419 outline test
at the soak-fix gate: 879 entries re-attributed and 678 `same_net` flips on
the 2,057 moved units, e.g. Thinkpad U2 via (35.4, 31.7) is inside both the
unnumbered exposed pad and pad 57 at 45° and now reports pad `""` /
`same_net: false` instead of `57` / `true`)
**File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_vias` via-in-pad
loop, `break` on first containing pad)
**Discovered:** 2026-10-06, harness soak-fix gate 9fbbb26 → ef6d55c
(`results/v23x_soak_gate/adjudication_soak.md`)

**Fix direction:** when several pads contain the via, prefer the pad on the
via's net, then the smallest pad (the exposed pad's bounding rect swallows
pin pads on rotated QFN/DFN footprints); report `pad: ""` only when no
numbered pad contains the via. Fixture: a QFN at 45° with a via on a pin pad
that also falls inside the exposed-pad rectangle.

**Gate budget (when fixed):** `via_in_pad[].pad` / `same_net` on rotated
QFN/DFN boards (subset of the KH-419 class); VP-001 unaffected.

### KH-426: XV-001..003 never compare MPN schematic ↔ PCB — 17 stale footprint MPNs and `BSS138LT1G` vs `BSS138` on the SacMap board produce 0 findings

**Severity:** MEDIUM (cross-analysis blind spot: a stale PCB MPN is exactly the sync error the XV rules exist for)
**File:** `skills/kicad/scripts/cross_analysis.py` (XV-001..003 compare value/footprint only)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** the soak board's PCB carries 17 footprint MPNs that no longer match the schematic symbols' MPNs (incl. `BSS138LT1G` on the PCB vs `BSS138` in the schematic); XV-001/002/003 report nothing.

**Fix direction:** add an MPN comparison to the XV sync check (normalised, case-insensitive, alias-tiered per KH-418) with its own rule or an XV-002 variant; fixture = one footprint whose `mpn` differs from the symbol's.

**Gate budget (when fixed):** XV-* gains on boards with sch↔pcb MPN drift — size at the gate walk (the KH-414 PCB class, 996 units, is the candidate population).

### KH-427: `design_rule_compliance` applies the `.kicad_pro` global min drill without honouring an UNCONDITIONAL `.kicad_dru` `hole_size` override — reports a violation native DRC does not

**Severity:** MEDIUM (false design-rule violation on boards that relax/tighten drills via `.kicad_dru`; the KH-383/412 pad-drill work made the drill check more visible)
**File:** `skills/kicad/scripts/analyze_pcb.py` (design-rule compliance drill branch; `.kicad_dru` parsing per KH-383)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap has an unconditional `(rule ... (constraint hole_size (min ...)))` in its `.kicad_dru`; the analyzer still evaluates the `.kicad_pro` `min_via_drill`/global drill and emits a violation KiCad's own DRC does not raise.

**Fix direction:** when an unconditional `.kicad_dru` `hole_size` rule exists it supersedes the `.kicad_pro` global drill for that check (KiCad precedence: `.kicad_dru` > netclass > global); record `rules_source` accordingly. Fixture = `.kicad_pro` min drill 0.3 + `.kicad_dru` hole_size min 0.2 + a 0.25 mm drill → no violation.

**Gate budget (when fixed):** DR drill-violation disappearances on boards with an unconditional `.kicad_dru` hole_size rule (erikbeerepoot/bramble class from the KH-383 gate).

### KH-428: `power_sequencing.dependencies[].has_pull_up` is true for a 10 k pull-DOWN (sign of the resistor's rail end ignored)

**Severity:** LOW (wrong polarity in a fact field; PS-00x reasoning about EN defaults inherits it)
**File:** `skills/kicad/scripts/analyze_schematic.py` (power-sequencing dependency builder, pull resistor classification)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap U-EN net has a 10 k resistor to GND; `dependencies[].has_pull_up` reads `true`.

**Fix direction:** classify by the resistor's far-end net (rail → pull-up, ground → pull-down) and emit `has_pull_down` alongside; fixture with both polarities.

**Gate budget (when fixed):** `has_pull_up` flips on boards with EN pull-downs; PS-001 content where the default-state text depends on it.

### KH-429: `deep_review_gate.find_pdf` matches only `<MPN>.pdf` — sync-style `<MPN>_<desc>.pdf` names silently degrade datasheet quotes to "partial"

**Severity:** LOW (Layer 2 evidence quality; the datasheet sync scripts write `<MPN>_<desc>.pdf`, so the common case misses)
**File:** `skills/kicad/scripts/deep_review_gate.py` (`find_pdf`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** quotes against a PDF saved by `sync_datasheets_*` as `TPS61023DRLR_datasheet.pdf` are graded `partial` because `find_pdf` looks for `TPS61023DRLR.pdf` only.

**Fix direction:** match `<MPN>*.pdf` (case-insensitive, sanitised MPN per `datasheet_lookup.sanitize_mpn`) and prefer the exact name when several exist.

**Gate budget (when fixed):** none (Layer 2 only; `deep_review.json` is excluded from the diff scope).

### KH-430: thermal package table lacks SOT-563, and the analyzer ignores the extraction's RθJA (142.7 vs default 150 °C/W)

**Severity:** LOW (Tj estimates on SOT-563 parts fall back to a default even when the datasheet extraction carries the real θJA)
**File:** `skills/thermal/scripts/analyze_thermal.py` (package table; θJA source precedence)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap U2 (SOT-563) is assessed with the 150 °C/W default; the cached extraction has `theta_ja = 142.7`.

**Fix direction:** add SOT-563 (and the SOT-363/SC-70 family) to the package table; when a trusted extraction provides θJA use it ahead of the table and mark `evidence_source: datasheet`.

**Gate budget (when fixed):** TH-DET/TS-00x content on SOT-563 boards and on boards with extracted θJA (corpus: ≈0 extractions).

### KH-431: `lifecycle_audit` findings carry no `finding_id` (40/40) and the script has no `--analysis-dir`; not in the analysis manifest (LC-007 still emitted by the schematic analyzer)

**Severity:** LOW-MEDIUM (Layer 2 merge keys on `finding_id`; lifecycle is the one analyzer outside the manifest/cache contract)
**File:** `skills/kicad/scripts/lifecycle_audit.py`
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** every lifecycle finding on the soak board lacks `finding_id`; the script cannot write into `analysis/`; `analysis_manifest` has no lifecycle entry while `analyze_schematic` still emits LC-007 itself.

**Fix direction:** route findings through `finding_schema.assign_finding_ids('lifecycle', …)`, add `--analysis-dir` + manifest registration like the other analyzers, and decide the LC-007 ownership (one emitter).

**Gate budget (when fixed):** additive `finding_id` on every lifecycle finding; LC-007 single-source.

### KH-432: power_budget counts an RGB LED as a flat 5 mA (cathode resistors R3/R4/R5 ignored, ~48 mA real) and ignores the USB VBUS load behind the PTC — thermal then skips U2 as `below_min_pdiss`

**Severity:** MEDIUM (KH-375 rider: multi-die LEDs and PTC-fed loads are under-counted, so a regulator that really dissipates is skipped by thermal)
**File:** `skills/kicad/scripts/analyze_schematic.py` (power_budget LED load model, KH-375 series-resistor branch; VBUS/PTC path)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap RGB LED with three cathode resistors is budgeted at 5 mA total instead of ≈48 mA (three channels × (3.3 − Vf)/R); the VBUS consumer behind the PTC is not attributed to the rail; thermal `skipped_components` lists U2 `below_min_pdiss`.

**Fix direction:** model multi-pin LEDs per channel through each cathode/anode resistor; treat a PTC (fuse-typed, KH-414 F-ref rules) as a pass-through for load attribution; fixture = RGB LED + 3 resistors + PTC-fed consumer.

**Gate budget (when fixed):** `power_budget.rails[*].estimated_load_mA` up on RGB-LED / PTC boards, thermal T3-class downstream (TS-00x/TP-001), `skipped_components` shrink.

### KH-433: datasheet staleness: `datasheet_lookup._resolve_pdf_path` uses `source.local_path`, stored by the extraction as an ABSOLUTE original-project path — any copied project reads its extractions as stale (irreproducible trust toggles between runs)

**Severity:** MEDIUM (this is why the VM-001 repro differed between the reviewer's and the controller's run: trusted vs stale depended on whose copy of the project ran)
**File:** `skills/datasheets/scripts/datasheet_lookup.py` (`_resolve_pdf_path`), extraction writers (`source.local_path`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** copy a project with `datasheets/extracted/` elsewhere → every extraction resolves its PDF through the old absolute path, fails the staleness check, and the analyzers drop to heuristic trust.

**Fix direction:** store `local_path` relative to the project root (or to the extraction file) and resolve relative to the current project; keep a fallback to the absolute path for old extractions; a determinism-style test that copies a fixture project and asserts identical trust.

**Gate budget (when fixed):** none in the corpus (no extractions); on extraction-bearing projects, trust flips heuristic → datasheet after copy.

### KH-434: PD-001 is silent when evaluated with no peaks — no `checks_run`-style line in `category_summary`

**Severity:** LOW (observability: a board with zero PDN peaks is indistinguishable from a board where the PDN check did not run)
**File:** `skills/emc/scripts/emc_rules.py` (PD-001 / `category_summary`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap's EMC output has no PDN entry at all; nothing says the check ran and found 0 peaks.

**Fix direction:** emit a `category_summary.pdn` (or `checks_run`) record with `peaks_total: 0` when the check runs and finds nothing, matching the `checks_run` convention in cross_analysis.

**Gate budget (when fixed):** additive `category_summary` entry on every EMC unit with a PDN evaluation.

### KH-435: DS-003 counts extraction JSON sidecars and symlinks as "datasheets"

**Severity:** LOW (inflates datasheet coverage)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`audit_datasheet_coverage`, DS-003 file census)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** a `datasheets/` dir with `<MPN>.json` extraction sidecars and symlinked PDFs is counted as more datasheets than PDFs present.

**Fix direction:** count regular `.pdf` files only (resolve symlinks, dedupe by target), exclude `extracted/` and `*.json`.

**Gate budget (when fixed):** DS-003 counts shrink on repos that ship extraction sidecars/symlinks (corpus: ≈0).

### KH-436: `test_coverage` counts `Connector:TestPoint`-based touch pads as test points

**Severity:** LOW (coverage metric inflated on capacitive-touch boards; same footprint family KH-373/413 already classify as touch pads)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`test_coverage`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap's two capacitive touch pads (TestPoint symbols) are reported as test points.

**Fix direction:** exclude symbols the touch-pad classifier recognises (net name / value / footprint touch markers used by CP-003) from the test-point census; fixture with one real TP and one touch TP.

**Gate budget (when fixed):** `test_coverage` counts shrink on touch-pad boards (CP-003 population).

### KH-437: `trust_summary.provenance_coverage_pct` 0.0 / `trust_level: low` on pcb / emc / thermal / lifecycle while every finding is `deterministic` (Aug B13, still open)

**Severity:** LOW-MEDIUM (trust rollup contradicts the findings it summarises; consumers keyed on `trust_level` down-rank deterministic output)
**File:** `skills/kicad/scripts/finding_schema.py` / per-analyzer `trust_summary` builders (pcb, emc, thermal, lifecycle)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** on the soak board all four non-schematic analyzers report `provenance_coverage_pct 0.0` and `trust_level low` although their findings carry `confidence: deterministic` with evidence sources.

**Fix direction:** compute provenance coverage from the findings' `evidence_source`/`provenance` the same way the schematic analyzer does; one shared helper.

**Gate budget (when fixed):** `trust_summary` values move on every pcb/emc/thermal unit (facts-only, no finding movement) — large additive-style class; pre-scan locks on `trust_level`/`provenance_coverage_pct`.

### KH-438: `datasheet_verification.findings` entries with null `rule_id` / `summary`

**Severity:** LOW (schema hygiene; Layer 2 merge and the harness differ skip null-rule findings)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`datasheet_verification` section builder)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** entries in `datasheet_verification.findings` carry `rule_id: null`, `summary: null`.

**Fix direction:** route them through `make_finding` with a DV-00x rule and a summary; or drop the section's pseudo-findings into `assessments`.

**Gate budget (when fixed):** additive rule ids on extraction-bearing projects (corpus ≈0).

### KH-439: sleep audit: U3 note "can be disabled via EN" next to `always-on`; 15 µA Iq placeholder vs 20 µA datasheet; `+BATT` assumed 3.7 V on a 2×AA board; MCU deep-sleep current absent

**Severity:** LOW (KH-374 rider — four accounting gaps in one section on the soak board)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`sleep_current_audit`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** contradictory EN note vs always-on classification; regulator Iq from a placeholder rather than the trusted extraction; battery chemistry inferred as Li-ion for a 2×AA pack (3.0 V nominal); the MCU's deep-sleep current is not an entry at all.

**Fix direction:** (1) EN-disable note only when the rail is not always-on; (2) prefer extraction `iq` when trusted; (3) infer battery voltage from the battery symbol/value (`2xAA`, `AAA`, `18650`) with a stated assumption otherwise; (4) add MCU deep-sleep from the extraction or the MCU family table.

**Gate budget (when fixed):** `sleep_current_audit` content on battery boards (KH-374 class population).

### KH-440: docs: native DRC/ERC on a project copy without lib tables emits `lib_footprint` / `lib_symbol` warnings — skill should say so

**Severity:** LOW (documentation; the kicad skill's DRC/ERC step surprises users on copied projects)
**File:** `skills/kicad/SKILL.md` (DRC/ERC section)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** running `kicad-cli pcb drc` / `sch erc` on a copied project without `fp-lib-table` / `sym-lib-table` yields library-resolution warnings unrelated to the design.

**Fix direction:** one doc note: copy the lib tables (or run from the original location) and how to recognise/ignore the lib_* class.

**Gate budget (when fixed):** none.

## Test Harness Issues

### TH-058: `test_kh420_zone_fill_segment_grid.py` asserts wall-clock time (< 30 s on the NLoy corpus board) — load-sensitive in the unit tree / pre-push hook

**Severity:** LOW (flake risk, not a correctness gap)
**File:** `tests/test_kh420_zone_fill_segment_grid.py` (NLoy timing test,
skip-if-absent, `--only-deterministic`)
**Discovered:** 2026-10-06, KH-418/420 follow-up adoption — the board runs
8.5 s idle (main-repo box), 19.5 s on this box while the 32-job incremental
gate was running (base side took 197.5 s vs 110 s idle under the same load).
The pre-push hook runs the whole unit tree; a concurrent gate or regen could
push the test past 30 s and block a push for a non-regression.

**Fix direction:** replace the absolute bound with a ratio against a
same-run baseline (e.g. time a reference board, or compare against the
`_point_in_polygon`-free path), or mark the timing assertion `TIER="perf"`
and keep a cheap structural test (segment-grid equality queries) in the
unit tier.

### TH-057: `generate_bugfix_assertions.py --apply` merges by assertion id — a changed expected value in the registry never reaches the reference file

**Severity:** LOW (one-line gotcha, but it defeats the documented RUNBOOK 4f
"regenerate bugfix assertions" step for exactly the case it exists for)
**File:** `regression/generate_bugfix_assertions.py` (~l.109-116: when the
output file exists and `generated_by` matches, an assertion whose `id` is
already present is skipped — the existing record wins)
**Discovered:** 2026-10-05, v2.3.0 regen (KH-299 7→6 and KH-311 50→47
re-anchors: `--issue KH-299 --apply` reported "Assertions generated: 1" yet
the reference file still held `value: 7`; same for KH-311; stale
KH-313-02/03 records likewise survived the registry removal)

**Fix direction:** replace the matching record when the registry version
differs (compare `check` + `description`), and drop records whose id is no
longer in the registry for that project; print `updated`/`removed` counts.
Workaround used this cycle: delete the affected `*_bugfix.json` files and
run a full `--apply`.

### TH-056: KH-313 corpus-lock anchor lost — TERES never exercises `check_inductor_leakage`'s crash path, and `summary.categories_checked` no longer means "categories that ran"

**Severity:** LOW (regression guard for a fixed crash is weaker than it
reads; same shape as TH-047 / KH-198)
**File:** `regression/bugfix_registry.json` (KH-313 entry); main-repo
`skills/emc/scripts/emc_rules.py::check_inductor_leakage(pcb, schematic)`
**Discovered:** 2026-10-05, v2.3.0 regen (BUGFIX-KH-313-02/03 failed once the
stale EMC output was finally rewritten — TH-054)

**Symptom:** BUGFIX-KH-313-02 (`emc_inductor_leakage` ≥ 1 finding on
OLIMEX/DIY-LAPTOP TERES Rev.C) and -03 (`summary.categories_checked == 10`)
had passed against a 2026-05-15-era EMC output. On a fresh output at BOTH
d5fd7da and 78b8f02 the board yields 8 findings in 2 categories and zero
inductor-leakage findings: the legacy `.sch` has no PCB pairing in the EMC
runner and `rf_chains` is empty, so the detector's bare-refdes RF-chain
crash path (the KH-313 bug) is never reached; `categories_checked` now
counts categories that produced findings, not categories executed.

**Disposition at the regen:** -02 re-anchored to fuad1502/open-running-watch-hw
(`open-running-watch.kicad_sch`, PCB-paired, ML-001 ×10 at v2.3.0) as a
"detector executes" guard; -03 removed (its proxy is semantically dead);
-01 (`summary` exists on TERES) kept. **2026-10-05 later (v2.3.1 gate):** that
anchor flips to 0 ML-001 at b008afa — KH-414's PCB alias widening fills L7's
MPN (`DFE252012F-2R2M=P2`) and the shielding lookup suppresses all 10 —
re-anchored again to CogniPilot/spinali_mcxn_t1_hub (ML-001 ×4 at both
78b8f02 and b008afa, PCB-paired, no timeout). Third anchor in two cycles:
the contract fixture is the real fix.

**Fix direction (main-repo):** a contract fixture reproducing the KH-313
input shape (RF chain whose `components[]` holds a bare refdes string) so
the crash path is pinned independent of the corpus; harness: audit other
BUGFIX locks whose premise depends on an input pairing that the runner no
longer produces.

### TH-055: pcb timeout-class units keep v1.3-era outputs — 198 boards never re-analyzed since the 120 s cap was introduced; downstream emc/thermal stale too

**Severity:** MEDIUM (corpus hygiene; every regen since v1.3 has carried these
as "stale-but-consistent": v2.2.0 226, v2.2.1 211, v2.3.0 198 units)
**File:** `utils.py` (`ANALYZER_TIMEOUT = 120`, module constant, no CLI/env
override; `run/run_pcb.py` exposes no `--timeout` — only
spice/emc/thermal runners do)
**Discovered:** 2026-10-05, v2.3.0 corpus regen (chain-oracle check)

**Symptom:** at the v2.3.0 regen 198 `.kicad_pcb` units hit the 120 s cap.
Their `results/outputs/pcb/` files are whatever last completed: **148 at
`schema_version` 1.3.0, 29 with no `schema_version` at all (pre-envelope),
21 with no output ever**. The 8 of them that fall inside the v23 gate's
300-project `--full` chain sample were the ONLY corpus units that differed
from the chain's candidate tree (`results/v230_regen/chain_oracle_report.json`
— e.g. acastles91/lifeSequencer emc GP-001 1 vs 77, RP-001 0 vs 22, DC-003
0 vs 7, all because the corpus pcb input is a v1.3 file). The chain A/B
completed every one of these boards with its own longer timeout, so they
are slow, not broken. Their emc/thermal downstream outputs and every
assertion seeded from them are v1.3-era as well.

**Fix direction:** (1) make the cap overridable (`--timeout` on
`run_pcb.py` / `run_schematic.py` / `run_gerbers.py`, or an env var read
by `utils.ANALYZER_TIMEOUT`); (2) a dedicated long-timeout pass over the
timeout-class list (`FAIL [...] *.kicad_pcb` lines in
`results/v230_regen/regen_runners.log`) followed by emc + thermal for those
repos and a reseed scoped to them — budgeted as its own class (v1.3 →
v2.3.0 on 198 boards), NOT folded into a release regen; (3) consider
writing the `.err` AND deleting the stale output on timeout so a v1.3 file
cannot masquerade as current.

### TH-053: 17 pre-existing tests fail under plain `pytest tests/` but pass under `run_tests.py --unit` — tier filtering hides them from the pytest path

**Severity:** LOW (the two runners disagree on what the suite IS: files
declaring `TIER = "online"` or reading corpus data are skipped/filtered by
`run_tests.py --unit` but collected by a bare `pytest tests/`, e.g.
`test_kh393_power_rails_threaded`; contributors running pytest see red on a
green tree)
**File:** `run_tests.py` (TIER filter); the root `tests/` tree has no
`conftest.py` (only `tests/contract/` does)
**Discovered:** 2026-09-13 (v2.3 batch, main-repo agent, while running the
new tests under pytest)

**Fix direction:** a root `tests/conftest.py` that reads each module's
`TIER` and skips non-unit files under pytest, so the two runners agree;
document `run_tests.py --unit` as the canonical runner.

### TH-052: 17 root `tests/` files have no `__main__` runner — 190 tests silently skipped by the pre-push hook (`run_tests.py --unit`), each counted as "1 passed"

**Severity:** MEDIUM (the hook's "N/0" baseline over-claims: every bare-python3
"verified" count since the v2.2 era included these files as 1 pass each while
executing nothing — the TH-014 class, recurring)
**Where:** `run_tests.py` fallback at ~:284 (unparsed summary → `p = 1`,
status ok, only a `WARN` line in the log) + the 17 files below.
**Discovered:** 2026-09-13 (S49) adopting PR #44 — `tests/test_pr44_pp001_fuse_power_names.py`
arrived without a runner block, the hook logged
`WARN ... (unparsed summary: '')` and counted it 1/0; adding the stdlib
runner moved the tree 1,336 → 1,349 (+13 = 14 real − 1 phantom). The same
WARN line sits on 17 pre-existing files (no `__main__`, no pytest import —
they run only under venv pytest): test_bus_resolver (26 tests),
test_kh359_kh360_netmap (19), test_kh359_suppression_bare_tail (6),
test_kh362_discovery (11), test_kh366_367_determinism (4), test_kh368_jsonc
(4), test_kh369_entrypoint (5), test_kh370_oscillator (5),
test_kh371_372_lifecycle (6), test_kh384_385_gate (5), test_kh388_vddet_dedup
(3), test_kh392_kh393_gp001_power (4), test_kh_v22x_pcb (10),
test_regression_diff_identity (17), test_v14_default_contract_gate (27),
test_v14_gate_criteria (14), test_v14_hierarchy_gate (24) — **190 tests**.
Six more files print a non-standard summary (`6/6 passed`, `All tests
passed!`) — they DO execute, only the count is lost.

**Fix direction:** (a) add the stdlib `__main__` runner (the
test_sp001_shorted_two_pin.py block) to the 17 files → hook baseline
becomes 1,349 − 17 + 190 = 1,522 if all pass; (b) harden `run_tests.py`:
when a file has no `__main__` block, import it and run its `test_*`
callables instead of counting a phantom pass, and make the unparsed-summary
fallback a FAIL, not a WARN. Do (a) first (surgical), then (b) so the
class cannot recur. Verify each file GREEN under bare python3 before
counting it.

### TH-049: partial results/outputs contamination between regens — unidentified full-corpus sweep, killed mid-flight

**Severity:** LOW (before-baseline noise only THIS cycle — the v2.2.1 regen
rewrites every output authoritatively — but "writer unidentified" is the
kind of thing that recurs)
**Where:** `results/outputs/` (862 files, 849 schematic), mtimes
2026-08-31 03:22:17–03:26:47
**Discovered:** 2026-09-01, v2.2.1 regen before-baseline (24 fails vs the
expected 7 — the 17 extras all sat on contaminated files)

**Facts:** a full-corpus `run_schematic`-shaped sweep ran with the
post-batch analyzer (v2.2.x tree), alphabetical repo order, writing 862
outputs before dying mid-corpus. Sidecar `capability_mode.json` run_ids
were reused, so `inputs.run_id` still reads the 2026-08-20 regen — mtime
and content (VD-DET dedup shapes, verified 67→54 by direct A/B on
43dad23-vs-d5fd7da) are the tells. Timing coincides with a TaskStop-kill
of a stale background `run_tests.py --unit`; but no unit-tier test can
produce an UNSCOPED sweep as written (`tests/test_run_integration.py`
always passes `--repo jgrip/commodorelcd`, which explains only the
sweep's first file). Kernel logs show no OOM kill. Full forensics:
`results/v221_regen/adjudication_v221_regen.md`.

**Fix direction:** (a) identify the writer if it recurs (this entry is the
tripwire — symptom: post-regen run_checks fails clustered on
alphabetically-early repos with fresh mtimes but stale run_ids); (b)
consider a guard: corpus runners refuse unscoped (no --repo /
--cross-section) invocation unless an explicit --all flag is passed —
would also prevent accidental full-corpus runs from test/CI contexts.

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

### KH-403: schematic connectivity over-union on label-only sheets — MAXI030 collapses all power symbols + 367 components into one 723-pin `__unnamed_0` net (kicad-cli: 522 nets, analyzer: 810)

**Severity:** HIGH (correctness-floor: every net-based detector on the board
is fed a fictitious net; refuted by the kicad-cli netlist oracle)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`build_net_map` /
pin-position keying — suspect: pins with no wire endpoint at all)
**Discovered:** 2026-09-10 (S47), by running PR #43's SH-001 candidate over a
494-file corpus sample: 73 "shorted" caps on this board, every one refuted.
PRE-EXISTING — identical on `main` @ 3cf837b (v2.2.1).

**Repro:** `analyze_schematic.py repos/aslak3/MAXI030/MAXI030.kicad_sch` →
`nets["__unnamed_0"]` has 723 pins incl. every `#PWR*`/`#FLG*` symbol and
C1 pins 1+2; `kicad-cli sch export netlist --format kicadxml` gives C1 =
`+2V5` / `GNDA`. File is KiCad 6 (`20211123`), generator eeschema, only 9
`(wire` and 8 `(junction` elements against 1,215 labels — connectivity is
label-on-pin / pin-on-pin, no wires. Likely the no-wire pin path shares one
grouping key.

**Fix direction:** oracle-diff the net map against kicad-cli on this board
(memory pattern `reference_kicad_cli_netlist_oracle`); add it to the
determinism/oracle fixture set. Budget: whole-board net churn on every
label-only corpus board — gate as its own class.

### KH-404: schematic connectivity over-union — Olivetti M20 L1 builds a 1,679-pin GND; 140 capacitors read as both-pins-on-GND (kicad-cli: C1 = `+5P`/`GND`)

**Severity:** HIGH (same class as KH-403, different trigger — root-sheet run
reproduces, so NOT a sub-sheet-as-root artifact)
**File:** `skills/kicad/scripts/analyze_schematic.py` (`build_net_map`)
**Discovered:** 2026-09-10 (S47), same SH-001 sample sweep; PRE-EXISTING on
`main` @ 3cf837b.

**Repro:** `analyze_schematic.py "repos/anchorz/Olivetti_M20_L1_schematics/Olivetti M20 L1.kicad_sch"`
→ 1,077 nets, `GND` has 1,679 pins, C1..C142 both pins on GND;
`kicad-cli sch export netlist` from the same root: 403 refs, 145 caps, zero
two-pin-same-net. Sub-sheets P04/P12 (`20220820`) show the same when run
standalone. Cause not yet localized — may or may not share KH-403's root.

**Fix direction:** same oracle-diff as KH-403; bisect which sub-sheet
introduces the union. Budget: with KH-403.

**2026-09-12 addendum (S48, PR #43 SP-001 sample, kicad-cli oracle on all
243 sample findings):** eleven MORE boards in an every-8th root sample show
the same class (205 of 243 "shorted two-pin part" findings refuted by
`kicad-cli sch export netlist`; 140 = this board, 65 = the eleven below).
Symptoms (analyzer net vs KiCad): mort13/mutable_eurorack_kicad `stages_v70`
(15, `__unnamed_1` swallows +3V3/VCC/VEE/GND) and `kinks_v41` (9, same);
acastles91/menelaos-rev-4 (14, net `blue` swallows +12V/GND/12V-Unfiltered);
flypie/Ace-2019 ACEZ380 (12, GND merged into `+5V`, 414 pins vs KiCad
110+142); benanderman/spork-8 Programmer (4, net counts MATCH KiCad but
C1–C4 pin 1 assigned VCC instead of GND — pin→net mapping, not a union);
axello Brasilia Espresso Controller (3, `__unnamed_2` swallows +12V/GND);
circuitly/kicad-demos pic_programmer (2, `VCC_PIC` swallows GND);
Squantor nuclone_LPC824 (2, VREFP–VREFN read as VBUS); georgsnarbuts
stm32_calc (1); Hanqaqa Easyduino_ESP32S3 (1); Queens-Rocket Sensors_Module
(1, R7 +3.3V–USB_D+ read as CH1_N); ALXCO ROMboard (1, `__unnamed_4`
swallows +5V/GND). Extrapolated ~90 corpus boards. Per-finding oracle log:
kicad-happy scratchpad `pr43-sample/oracle.log` (session-local — regenerate
with the oracle on these paths). These are the bisect set for KH-403/404;
the spork-8 pin-assignment variant may be a third root cause. SP-001's
per-net collapse (>=5 hits) keeps user output to one finding per such net.

_19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
