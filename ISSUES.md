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

Last updated: 2026-08-20

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-392** (KH-373..391 filed 2026-08-20 from the SacMap rev2 fresh-eyes soak review — 15 reviewer claims verified by 4 parallel agents (13 confirmed, 1 partial, 1 regression-theory refuted) + 4 verifier incidentals; evidence: kicad-happy sandbox Old-Reviews/sacmap-rev2/7/ + session-43 chat; KH-371/372 filed 2026-08-17 from GitHub PR #37 (fl4p) deliberately-left-out defects, code-verified — LC-ACT missing provenance fields, LC-005 single-source denominator semantics; KH-370 filed 2026-08-01 from GitHub #33, KH-220 description-substring oscillator FP, code+repro verified; KH-368/369 filed 2026-07-26 from verified external-review claims — JSONC string corruption + Action file-detect; KH-367 filed 2026-07-25, two more
hash-order nondeterminism sources; KH-366 filed 2026-07-24, RC-DET
nondeterminism found during v2.2 work; KH-357 filed 2026-07-24 from GitHub #31;
KH-358..365 filed 2026-07-24 from the verified subset of the KiCad-source audit
`docs/2026-07-24-kicad-parser-and-analysis-audit.md` — each entry cites its
KHPA finding ID). Next TH number: **TH-049** (TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 51 open issues (43 KH + 8 TH).

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

### KH-357: BE-001 treats `rect` board outline as its diagonal — false edge-proximity findings (GitHub #31)

**Severity:** MEDIUM
**File:** `skills/emc/scripts/emc_rules.py:2265-2267` (`_point_to_edges_min_distance`)
**Discovered:** 2026-07-24 (GitHub #31, reported by enorfelt 2026-07-18; code-verified same day)

**Symptom:** `if etype == 'line' or etype == 'rect':` computes
`point_to_segment_distance` from `start` to `end` — but for a `rect` edge
those are the two OPPOSITE CORNERS, so the measured distance is to the
rectangle's corner-to-corner DIAGONAL, not to any of its 4 sides. Reporter's
repro (100×100mm board, outline = single `gr_rect`): trace midpoint
(38.425, 38.755) sits near the y=x diagonal → BE-001 fires "0.23mm from
board edge" (= |mx−my|/√2) while the real nearest edge is 38.4mm away.
Verified against pcbnew ground truth by the reporter; defect line confirmed
in current main (v2.1.0).

**Impact:** Any board whose Edge.Cuts outline is a single KiCad `gr_rect`
primitive (common workflow) gets spurious BE-001 findings for traces near
the diagonal — and, conversely, real edge-proximity near the actual sides
is UNDER-measured only when the diagonal is closer, so the miss direction
is false-positive-dominant. Also inflates the `near_edge_count > 10`
summarization path.

**Fix sketch:** expand `rect` into its 4 sides before the point-to-segment
test — mirror the existing correct expansion in `analyze_pcb.py:6106-6110`
(`(x1,y1)→(x2,y1)→(x2,y2)→(x1,y2)→(x1,y1)`). Reporter's suggested patch in
GitHub #31 does exactly this. Check the `arc`/fallback branches of the same
function while in there. Gate note: BE-001 churn on rect-outline boards is
the expected budget class (disappearances near diagonals; possible new
findings near real edges previously shadowed by a closer diagonal).

---

### KH-358: VP-001 tenting check reads `remove_unused_layers` — a field nothing writes (audit KHPA-019)

**Severity:** MEDIUM
**File:** `skills/kicad/scripts/analyze_pcb.py:6048` (check) vs `:1092-1094` (extractor)
**Discovered:** 2026-07-24 (audit KHPA-019; code-verified same day)

**Symptom:** The via extractor parses real `(tenting ...)` into `via["tenting"]`
(:1092-1094), but the via-in-pad check tests `via.get("remove_unused_layers",
False)` (:6048) — grep confirms that key is never written anywhere. So `tented`
is ALWAYS False and every tented via in a pad is reported untented. The comment
at :6046-6047 ("KiCad doesn't export tenting") is false — contradicted by the
extractor AND by the codebase's own correct check at :5103
(`via.get("tenting", [])`).

**Impact:** False-positive untented-via-in-pad warnings in `--full`/proximity
runs; tented vias mislabeled. **Fix:** read `tenting` like :5103 does.
Gate/corpus note: VP-001 text/severity churn on boards with tented vias in pads.

---

### KH-359: same-name local labels on different sheets MERGE in the output nets dict (audit KHPA-003)

**Severity:** HIGH
**File:** `skills/kicad/scripts/analyze_schematic.py:1600-1605` (merge branch);
union keys :1457/:1475; naming :1555-1566
**Discovered:** 2026-07-24 (audit KHPA-003; code-verified same day)

**Symptom:** `build_net_map()` correctly keeps local labels sheet-scoped in the
union-find (`(lbl_name, sheet)` keys, :1457; local power symbols :1475), but the
final `nets` dict is keyed by bare display name. A second disjoint root with an
already-present name hits `nets[net_name]["pins"].extend(...)` (:1600-1605) —
a silent MERGE. Two sheets each with local label "MISO" on different components
→ one output net holding both pin sets. KiCad keeps them separate (sheet path is
part of local-label identity, `sch_connection.cpp:393-452`). The per-instance
namespacing pass applies ONLY to `hierarchical_label` (:8636/:8644), so it does
not defeat the collision. Local-vs-global same-name collapses identically.

**Impact:** Corrupts the core `nets` model consumed by every downstream detector
on any multi-sheet design that reuses a bare local-label/local-power name on ≥2
sheets. Silent — no warning, no downgraded confidence.

**Fix sketch:** disambiguate at serialization (sheet-qualified name or list/ID
keyed nets with a `display_name -> [ids]` index) — schema decision.
**SCHEDULED: v2.2 (user-confirmed 2026-07-24)** — folded into the #25
bus-connectivity release: same function, same kicad-cli netlist oracle, same
golden boards (unfixed, this defect would confound the #25 oracle diffs on
multi-sheet golden boards). Budget class: net splits on multi-sheet boards with
reused local names.

---

### KH-360: `union_with_overlapping_wires` stops after the first matching wire (audit KHPA-007)

**Severity:** MEDIUM
**File:** `skills/kicad/scripts/analyze_schematic.py:1431-1435`
**Discovered:** 2026-07-24 (audit KHPA-007; code-verified same day)

**Symptom:** `union(k, wk1); return` after the FIRST wire whose segment overlaps
the label/junction/no-connect point (tol 0.05mm, :1411). Safe when all wires
TERMINATE at the point (shared endpoint key already unions them). Broken when a
wire passes THROUGH the point as a mid-segment (junction tap off an un-split
backbone wire): if the tap wire is iterated first, the union is a no-op and the
backbone stays disconnected — result depends on wire insertion order.

**Impact:** Order-dependent silent disconnection at mid-segment junction taps;
narrower than the audit claimed (ordinary all-terminating junctions unaffected).
**Fix:** drop the early `return`, union every overlapping wire.
**SCHEDULED: v2.2 (user-confirmed 2026-07-24)** — folded into the #25 release
(covered by the same netlist oracle).

---

### KH-361: `.kicad_dru` conditional rules applied as GLOBAL minimums — condition never evaluated (audit KHPA-016 part 3)

**Severity:** MEDIUM
**File:** `skills/kicad/scripts/analyze_pcb.py:4735-4772`; loader
`kicad_utils.py:1796/:1818`
**Discovered:** 2026-07-24 (audit KHPA-016; code-verified same day)

**Symptom:** `load_kicad_dru` captures each rule's `condition` string but the
consumer loop applies every constraint's minimum board-wide and never reads
`rule.get('condition')`. A rule scoped to one net/layer/item class (e.g. an
`A.isPlated()` or netclass-gated clearance) produces violations on unrelated
items. Output lands in the plain `design_rule_compliance` block with definitive
"requires X>=Ymm, actual Zmm" wording — no confidence/heuristic softening.

**Impact:** False DRC-style violations on any board whose .kicad_dru uses
conditions (most real .kicad_dru files do). **Fix:** evaluate a supported
condition subset, else SKIP the rule and note it unsupported — never apply
globally. (The audit's run-6 SacMap review already hit this class from the
other side: 7 spurious errors from an unmatched isPlated rule.)

---

### KH-362: project/.kicad_dru discovery returns the FIRST file in the directory, ignoring the board stem (audit KHPA-015)

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_utils.py:1451-1456` (`load_kicad_pro`),
`:1769` (`load_kicad_dru`)
**Discovered:** 2026-07-24 (audit KHPA-015; code-verified same day)

**Symptom:** Both loaders glob the board's directory and return the first
match; callers pass the full board path but the functions keep only dirname.
Multi-project or panelized directories can silently apply another project's
settings/rules. Also: raw `json.load` where KiCad's settings loader permits
comments.

**Fix:** match by stem first, fall back to single-file case; tolerate commented
JSON; surface a note when ambiguous.

---

### KH-363: stale module-global net-ID map can leak into pad `net_number` on re-entrant use (audit KHPA-017)

**Severity:** LOW (latent — no shipped path triggers it)
**File:** `skills/kicad/scripts/analyze_pcb.py:535` (global), `:585` (reset),
`:6277` vs `:6285` (order), `:6300-6301` (pad ==0 backfill guard)
**Discovered:** 2026-07-24 (audit KHPA-017; code-verified same day)

**Symptom:** `_net_name_to_id` IS reset in `_build_net_mapping` (:585) — but the
reset runs at :6285, AFTER `extract_footprints` (:6277) has already stamped pad
`net_number` via the previous board's mapping. Tracks/vias/zones are then
rebuilt unconditionally (:6287-6297) while pads are only backfilled when
`net_number == 0` (:6300-6301) — a second KiCad-10 string-net board analyzed in
the same process can keep first-board pad IDs. All shipped paths are
one-board-per-process (CLI, subprocess orchestration), so impact is zero today.

**Fix:** reset before extraction or carry the map in an analysis-context object;
add an A→B→A same-process determinism test when touched.

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

### KH-366: RC-filter detection is run-to-run NONDETERMINISTIC (hash-order candidate selection) — violates the Layer-1 byte-stability invariant

**Severity:** MEDIUM (HIGH for gate trust: affected boards can FLAKE any byte-diff gate)
**File:** `skills/kicad/scripts/signal_detectors.py` — RC-DET / `passive_filters`
candidate-cap selection (parallel-cap grouping path); exact lines TBD at fix time
**Discovered:** 2026-07-24 during v2.2 Task 4 isolation byte-diffing (main-repo
agent; reproduced independently by controller)

**Symptom:** Repeated runs of `analyze_schematic.py` on the SAME file with the
SAME code produce different `findings` — an RC-filter finding alternates
between e.g. `capacitor C25 (1u, farads 1e-06, components [C25,R50])` and
`capacitor C110 ("2 caps parallel", farads ~2e-05, parallel_caps [C110,C34])`.
`finding_id`, cutoff, and components all flip with it. Repro: run
`analyze_schematic.py repos/bec5-group/pid-controller/pid/pid.sch` 3-4 times
and byte-compare outputs minus `inputs` — divergence typically appears within
3 runs (output sizes flip e.g. 304594 vs 304598 bytes).

**Verified PRE-EXISTING:** reproduced on pristine `c6b504a` (= v2.1.0 + CI-only
commit) via `git archive` copy — NOT introduced by the v2.2 branch (KH-359/360
work). This means shipped v2.1.0 violates the "Layer 1 findings deterministic +
byte-stable; finding_id stable across runs" invariant on affected boards.

**Likely mechanism:** per-process hash randomization (PYTHONHASHSEED) changing
iteration order of a `set`/dict of candidate caps or nets in the RC-filter
detector's parallel-cap grouping — each CLI invocation is a fresh process with
a fresh seed. Fix direction: sort candidates deterministically (by ref) before
selection/grouping. Audit siblings: grep detectors for selection out of
unsorted `set()` iteration.

**Gate/corpus implications (why this matters beyond the one finding):**
(1) any byte-diff regression gate can flake on affected boards regardless of
the code under test — adjudicate such diffs against this issue; (2) determinism
re-verification runs that set a fixed PYTHONHASHSEED (or run in-process) would
never see it — check how the harness determinism check invokes the analyzer.
NOT in v2.2 scope (one-theme rule); natural home = v2.2.x maintenance batch.

### KH-367: two more hash-order nondeterminism sources (DO-DET list order; power_sequencing en_net unnamed-net identity) — same class as KH-366, distinct detectors

**Severity:** MEDIUM (gate-flake risk, same class as KH-366)
**File:** (1) `skills/kicad/scripts/signal_detectors.py:3474` — unsorted `set`
comprehension feeding DO-DET `rails_without_caps` + summary list order;
(2) `skills/kicad/scripts/analyze_schematic.py` `build_net_map` — union-find
root-selection order flips which `__unnamed_N` id lands in
`power_sequencing_validation.issues[].en_net` (exact unsorted-set source not
yet pinned; value observed as `__unnamed_46`/`61`/`73` across 3 runs)
**Discovered:** 2026-07-25 during v2.2 Task 13 determinism sweep on
`ehbc-project/ehbc-proto1-board/projects/m68k-hbc` (main-repo agent)

**Symptom:** Repeated CLI runs on the same file differ: (1) DO-DET rails list
order flips; (2) an en_net identity VALUE flips (not just ordering). Both
reproduce identically on pristine `c6b504a` via git-archive checkout —
PRE-EXISTING in shipped v2.1.0, NOT introduced by the v2.2 branch (whose
signal_detectors.py diff vs main is zero).

**Fix direction:** (1) sort the comprehension at :3474 (one-liner); (2) trace
the en_net path for set-derived ordering (candidate: iteration over a set of
nets/pins in power_sequencing validation or unnamed-net numbering inputs) and
sort at the source. Audit siblings per KH-366's grep suggestion — this entry
is evidence the class is systemic (3 known instances).

**Gate implications:** same as KH-366 — adjudicate m68k-class byte-diff flakes
against BOTH issues; repro technique documented in v2.2 Task 13 report
(kicad-happy `.superpowers/sdd/2026-07-24-v2.2-schematic-connectivity/`).
NOT in v2.2 scope; natural home = v2.2.x maintenance batch alongside KH-366.

### KH-368: JSONC comment-stripping corrupts string values containing `//` or `/* */` — config layer silently dropped

**Severity:** MEDIUM
**File:** `skills/kicad/scripts/project_config.py:32-49` (`_LINE_COMMENT`/
`_BLOCK_COMMENT` regex substitution in `_strip_jsonc`, applied before
`json.loads`); failure swallowed at `_load_and_validate` (~:196-205)
**Discovered:** 2026-07-26, external review claim VERIFIED empirically by
main-repo agent (both failure modes reproduced)

**Symptom:** (1) A `.kicad-happy.json` string value containing `//` — e.g.
`"documentation": "https://example.com/spec"` — is truncated at the `//`
(`'{"documentation": "https:'`), producing a `json.JSONDecodeError`;
`_load_and_validate` then returns None with only a stderr warning and the
ENTIRE config layer (suppressions, design intent, power rails) is silently
skipped. (2) `/*...*/` inside a string value is silently DELETED and the file
still parses — silent value corruption (`"do not treat /* this */ as a
comment"` → `"do not treat  as a comment"`). Any user putting a URL in their
config (datasheet link, doc pointer) loses their suppressions without a
visible failure in the report.

**Fix direction:** replace the regexes with a small stateful scanner that
tracks in-string state (quote + backslash escape) and strips comments/
trailing commas only outside strings — stdlib-only, ~25 lines. Keep the
public `load_jsonc` contract. Unit tests: both repro cases above + escaped
quotes + `//`-after-value-on-same-line (real comment) still stripped.
Related: KH-362 (KHPA-015) covers `.kicad_pro`/`.kicad_dru` discovery +
commented-JSON tolerance — same subsystem, different file/path; fix together.

### KH-369: GitHub Action schematic auto-detect is `find | head -1` — comment claims root-preference/largest, code does neither

**Severity:** MEDIUM (silent wrong-project/wrong-sheet analysis in CI)
**File:** `action/entrypoint.sh:17-27`
**Discovered:** 2026-07-26, external review claim VERIFIED by main-repo agent

**Symptom:** When `INPUT_SCHEMATIC` is empty, the entrypoint runs
`find . -name "*.kicad_sch" ... | head -1`. The comment above it says
"prefer root-level, then pick the largest" but no such logic exists. `find`
order is filesystem-traversal-dependent, so: (a) multi-project repos get an
arbitrary project analyzed silently; (b) even a single hierarchical project
can get a CHILD sheet selected instead of the root (partially mitigated by
the analyzer's sub-sheet detection redirecting to full-project analysis, but
the selection is still arbitrary and non-portable). Same pattern for the PCB
pick at :26.

**Fix direction:** implement what the comment promises, or better: use
explicit input when given; else group candidates by `.kicad_pro` stem;
auto-select only when exactly ONE project exists; otherwise FAIL with the
candidate list (silent selection is inappropriate for a review gate —
matches the project's own honest-degradation posture). Same class as KH-362
(first-file-in-dir discovery).

### KH-370: KH-220 description-substring oscillator classification misfires on "internal oscillator" ICs → false XL-DET + CD-DET findings (GitHub #33)

**Severity:** MEDIUM (2 false info-findings per affected part; ADC/MCU/sensor
descriptions mentioning an internal oscillator are common datasheet phrasing)
**File:** `skills/kicad/scripts/kicad_utils.py:528-533` (KH-220 branch in the
full-prefix-match override section; a second KH-220 site at :612-616 is
X-prefix-only and NOT implicated); cascade via
`signal_detectors.py:1041-1042` + `:1074-1079` and
`domain_detectors.py:3724-3764`
**Discovered:** 2026-07-29, GitHub issue #33 (VoltixSpark/William Leismer,
repro'd on a real KiCad 8 design); claim VERIFIED empirically by main-repo
agent 2026-08-01 (minimal-pair repro, mechanism confirmed with one correction)

**Symptom:** Any U-prefix IC whose symbol `Description` contains the bare
substring "oscillator" (and not "crystal") — e.g. "Low-Power, I2C-Compatible
ADC With Internal Reference, Oscillator, and Programmable Comparator" — is
reclassified from `ic` to `oscillator`. Two false findings cascade: (1)
**XL-DET** `active_oscillator` — `detect_crystal_circuits` has an
unconditional always-include branch for `type == "oscillator"`
(`signal_detectors.py:1041-1042`; the `_osc_keywords`/`_osc_exclude` guards
only run for `crystal`/`ic` types, so they can't save a misclassified part);
(2) **CD-DET** `oscillator_output` — with no OUT/OUTPUT/CLK/CLKOUT pin, the
XL-DET fallback (`signal_detectors.py:1074-1079`) picks the FIRST non-power
non-ground pin as `output_net` (an I2C SCL/SDA net on a bus peripheral), then
CD-DET phase 2 (`domain_detectors.py:3724-3764`) traces it and reports the
bus neighbor as a clock "consumer" ("Detected active oscillator U1 driving
clock output.").

**Mechanism correction vs the GitHub report:** issue #33 attributes the SCL
pickup to `_CLOCK_OUTPUT_PINS` — actually `_CLOCK_OUTPUT_PINS` is not involved
in CD-DET phase 2; the SCL net arrives via the XL-DET first-non-power-pin
fallback above. Same outcome, different path (matters for where the fix goes).

**Repro (minimal pair, verified 2026-08-01 at v2.2-dev e67aeb5):** 2-IC
synthetic schematic — U1 5-pin I2C ADC (pins SCL/SDA/GND/VDD/AIN0) with the
description string above, U2 generic MCU, wired SCL+SDA with local labels,
VDD/GND labeled. Result: U1 classified `oscillator`, XL-DET
`active_oscillator` with `output_net: "SCL"`, CD-DET `oscillator_output` with
`consumers: ["U2"]`. Control (identical file, description minus the word
"Oscillator"): U1 stays `ic`, zero XL-DET/CD-DET findings.

**Fix direction (issue offers 3 options, all reasonable — pick during fix):**
(a) require is-a-clock-source phrasing ("crystal oscillator", "oscillator IC",
"clock generator") instead of bare substring; (b) add internal-oscillator
exclusions ("internal oscillator", "on-chip oscillator", "internal reference,
oscillator") alongside the existing `"crystal" not in _desc_low` guard; (c)
gate description-based classification behind corroborating pin evidence
(XTAL/OSC/CLK-OUT-named pin, no I2C/SPI bus pins). Option (c) is the most
robust; (b) is the smallest diff. ALSO consider hardening the XL-DET fallback
(`:1074-1079`) — picking an arbitrary non-power pin as a "clock output" is a
second-layer defect that would still misfire for any future misclassification.
Budget note: XL-DET + CD-DET fire together, and description phrasing is
common on TI/ADI ADC symbols — corpus movement could be broad; budget both
rule IDs together per the shared-keyword-list rule. Natural home = v2.2.x
maintenance batch alongside KH-357/366/367.

### KH-371: LC-ACT findings omit `confidence` and `evidence_source` → forced `trust_level="low"`; "active" summary overstated for LCSC-only unknowns

**Severity:** LOW (info-only rule; but it drags `trust_summary.trust_level`
down via `unknown_confidence` on every lifecycle run with active parts)
**File:** `skills/kicad/scripts/lifecycle_audit.py:731-740` (LC-ACT else-branch
in `audit_bom`)
**Discovered:** 2026-08-11, reported in GitHub PR #37 (fl4p) as a
deliberately-left-out semantic defect; code-verified by main-repo agent
2026-08-17 (the else-branch builds the finding dict with no `confidence` and
no `evidence_source` keys, unlike every sibling rule at :713-714)

**Symptom:** Every "active" component emits an LC-ACT finding missing both
provenance fields. `compute_trust_summary` counts these as
`unknown_confidence`, forcing `trust_level="low"` on otherwise-clean runs.
Additionally the LC-ACT branch is reached for LCSC-only `unknown` status
(the `lcsc_only and status == "unknown"` carve-out at :694) yet writes
summary "active" — status the data doesn't support.

**Fix direction:** add `confidence`/`evidence_source` (api_lookup, matching
:714) to the LC-ACT dict; for the lcsc_only-unknown path, say "unknown
(LCSC returns no lifecycle status)" instead of "active". Semantic change —
budget LC-ACT summary churn (not corpus-gate-visible: lifecycle has no
corpus runner; verify on the contract fixture + a live-API board).

### KH-372: LC-005 "single source" denominator counts only APIs that responded; `status is None` counts as active; LCSC carries no lifecycle status

**Severity:** LOW (info-only rule, but its claim is unsupported by its own
data)
**File:** `skills/kicad/scripts/lifecycle_audit.py:744-770` (LC-005 block in
`audit_bom`)
**Discovered:** 2026-08-11, reported in GitHub PR #37 (fl4p) as a
deliberately-left-out semantic defect; code-verified by main-repo agent
2026-08-17

**Symptom:** `total_queried = len(finding.get('sources', {}))` (:749) counts
only sources that RETURNED data, not sources attempted — a part carried by
one distributor while three APIs errored/timed out reports "only available
from X out of 1 sources checked" or is skipped entirely, while transient API
failures can conjure false single-source findings. `active_sources` counts
`status in ('active', 'Active', None)` (:747) — a None status is treated as
active. LCSC returns no lifecycle status at all, so its rows are None →
"active" by default. The description "only available from {X} out of
{total_queried} sources checked" is therefore not supported by the data.

**Fix direction:** thread the attempted-sources list from `audit_component`
into the finding (attempted vs responded vs active), require an explicit
active status (None → unknown, excluded from the numerator), and exclude
LCSC from the lifecycle denominator (or label it stock-only). Semantic
change — same validation caveat as KH-371 (no corpus runner; live-API
verification needed).


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

### KH-380: cross_analysis NR-001 is unreachable dead code — reads board_outline['segments'], producer emits 'edges'

**Severity:** HIGH (an advertised rule that can never fire; zero firings across 36,462 gate units + all fresh --full runs)
**File:** `skills/kicad/scripts/cross_analysis.py:459-460`; producer `analyze_pcb.py:1485` (`"edges": edges`; BoardOutline envelope declares edges, never segments). emc_rules.py:2291/:2369 read `edges` correctly — cross_analysis-only defect.
**Discovered:** 2026-08-20, SacMap soak B8 investigation (corpus: segments non-empty in 0/3,001 sampled snapshots; edges in 2,435)

**Fix direction:** one-line key fix + a harness fixture that makes NR-001 fire (critical net near outline). Budget: NR-001 appearances corpus-wide (rule fires for the first time ever — could be broad; treat as NewKnown-style budget).

### KH-381: cross_analysis emits no record of which checks ran — silent [] returns indistinguishable from clean; assessments[] structurally always empty

**Severity:** MEDIUM (trust/observability; the SacMap zero-findings result was CORRECT behavior but unprovable from the artifact)
**File:** `skills/kicad/scripts/cross_analysis.py` — ~20 ungated early-return guards (:173,:324,:371,:453,:456,:459,:512,:513,:595,:609,:647,:650,:727,:852,:857); `assessments` hardcoded [] at :1037; envelope carries no checks-run field
**Discovered:** 2026-08-20, SacMap soak claim B8 (observability part CONFIRMED; no except:pass exists — that sub-claim refuted; elapsed_s plausible for genuine execution, scaling verified)

**Fix direction:** emit a `checks_run` manifest (rule id, inputs-present bool, items examined, findings count) — same honesty posture as bus_topology.unresolved / the fail-loudly pool item. Additive schema field; budget additive-key drift only.

### KH-382: XV-002 emission order is PYTHONHASHSEED-dependent (set-intersection iteration)

**Severity:** MEDIUM (KH-366/367 family; violates "deterministic + byte-stable"; gate-invisible under PYTHONHASHSEED=0 pinning)
**File:** `skills/kicad/scripts/cross_analysis.py:412` (`for ref in sch_refs & pcb_refs:`)
**Discovered:** 2026-08-20, SacMap soak B8 A/B (discrete-nes board: identical finding SET, order varies across seeds 0/1/12345; verified same at v2.1.0)

**Fix direction:** `sorted(sch_refs & pcb_refs)`. Fold into the KH-366/367 determinism batch + its CI guard. Budget: byte-order-only.

### KH-383: min-drill blind to footprint pad drills — dfm min_drill_mm via-only AND design-rule check never receives footprints

**Severity:** HIGH (fab-facing number wrong; the board's own min_through_hole_diameter is structurally unenforceable against half its holes)
**File:** `skills/kicad/scripts/analyze_pcb.py:4292-4296` (dfm drill scan reads board via list only), :3100-3113 (same in via facts), :4575-4619 (`analyze_design_rule_compliance(tracks, vias, project_settings)` — no footprints param; min_via_drill vs min_through_hole_diameter). Pad drills ARE parsed (:710-720); only consumer is an unrelated proximity check (:5122).
**Discovered:** 2026-08-20, SacMap soak claim B9 (12×0.2mm footprint-embedded PTH thermal vias under U1, board rule 0.3mm, reported min 0.3 + "compliant: true"); fixture-reproduced

**Fix direction:** include pad drills in both paths; pass footprints into design-rule compliance. NOTE: LIMITS_STD min_drill=0.2 (:4066) means DFM alone stays silent at 0.2mm — the project-rule path is the one that must see pads. Budget: min_drill_mm value changes + new DR violations on boards with small pad drills.

### KH-384: deep_review_gate resolves computation script paths against shell cwd, not --analysis-dir

**Severity:** MEDIUM (valid findings quarantined depending on invocation directory; --project-dir escape hatch exists but is undocumented)
**File:** `skills/kicad/review/scripts/deep_review_gate.py:175-180` (`check_computation`: `Path(project_dir)/script`, --project-dir defaults "." at :222; --analysis-dir used only by load_anchor_sets :239); docs `references/deep-review.md:109-111` show only project-root invocation, :83-90 mandate root-relative helper paths
**Discovered:** 2026-08-20, SacMap soak claim B11, reproduced verbatim incl. error string

**Fix direction:** default --project-dir to parent of --analysis-dir; document the flag; add schema description on computation.script.

### KH-385: gate datasheet-quote check — elided quotes always fail, quarantine reason lacks nearest-match context, schema has no description on quote/script fields

**Severity:** MEDIUM (an accurate elided quote and a fabricated paraphrase produce identical-shaped quarantine reasons)
**File:** `skills/kicad/review/scripts/deep_review_gate.py:125-144` (`_norm_text` turns .../… into word breaks; `_quote_in_text` single contiguous-substring only), :168-171 (reason = first 80 chars, no context); `skills/kicad/review/schemas/deep_review.schema.json` quote/script fields bare strings, no description. deep-review.md:100-101 DOES state the verbatim rule (doc part of claim overstated) but nothing mentions elision.
**Discovered:** 2026-08-20, SacMap soak claim B12, 7-case matrix tested against a real datasheet page

**Fix direction:** segment-split on elision markers (each segment substring-matched, in order) OR document the no-elision rule in schema+docs; add nearest-match snippet to the quarantine reason.

### KH-386: thermal silently drops regulators whose rail shows zero load — partial assessment presents as complete (score 97-100)

**Severity:** HIGH (hotter of two identical regulators never evaluated, no note anywhere; compounds with KH-375 which produces the zero loads)
**File:** `skills/kicad/scripts/analyze_thermal.py:236-272` (`_estimate_all_power_dissipation` — bare `continue` at :253 on `not iout_a`), :1090-1097 (missing_info covers assessed components only), :756-762 (score None only when list fully empty)
**Discovered:** 2026-08-20, SacMap soak claim B13; end-to-end fixture repro (two identical TPS61023, one dropped, score 97, dropped ref appears NOWHERE)

**Fix direction:** emit a capability note / skipped-components list ("Uassessed n of m power components; U2 skipped: no load estimate") — fail-loudly posture; real fix arrives with KH-375 load accounting. Budget: additive field + note text only, until KH-375 lands (then joint thermal movement).
Context (structural, not this bug): trust_level "low" + provenance_coverage 0.0 are constants for thermal — confidence distribution drives trust (finding_schema.py:399-409) and analyze_thermal never calls make_provenance. PR #37's evidence_source flip did NOT alter trust_level (verified by execution).

### KH-387: _thermal_confidence still returns "datasheet-backed" for package_table — the parallel overclaim PR #37 fixed in evidence_source but left in confidence (the field that drives trust_level)

**Severity:** MEDIUM (a package-average estimate can yield confidence "datasheet-backed" → trust_level "high"; now visibly contradicts the corrected evidence_source "heuristic_rule" in the same finding)
**File:** `skills/kicad/scripts/analyze_thermal.py:467-473` (:473 `"datasheet-backed" if rtheta_ja_source == "package_table"`); PR #37 (91ea659) touched :445/:489-491 only
**Discovered:** 2026-08-20, verify-agent while checking soak claim B13

**Fix direction:** same rationale as PR #37 — package_table is a footprint-regex average; confidence should be heuristic (or a distinct "reference_table" tier if added deliberately). Budget: confidence + trust_level shifts on every package_table board (large class — the #37 fold moved 1,421 corpus units; this moves the same class's confidence). Gate with care; pairs naturally with KH-386.

### KH-388: VD-DET double-emission → duplicate findings sharing one finding_id + duplicate SPICE simulations

**Severity:** MEDIUM (finding_id uniqueness contract violated; inflated counts; wasted sims. DELIBERATE double-append with 8c36212 cascade warning — fix MUST be corpus-gated with the exclusion-set interplay in mind)
**File:** `skills/kicad/scripts/signal_detectors.py:372+:392` (same dict object appended to feedback_networks AND voltage_dividers; warning comment :324-346), `:3355-3377` (postfilter dedups within-list only); `analyze_schematic.py:9629-9636` (flatten lands both); `finding_schema.py:112-134` (id(f) skip → aliased finding_id, docstring :106-110 admits it); consumer `skills/spice/scripts/simulate_subcircuits.py:120-127, :219` (no dedup). A second duplication path exists producing DISTINCT objects/detection_ids (soak board R8/R9+R10/R11 dup'd via aliasing, third divider via the other path).
**Discovered:** 2026-08-20, SacMap soak claim B14; artifact-confirmed duplicate finding_ids (schematic:feedback_networks-9318b64d03a6 ×2 etc.)

**Fix direction:** dedup at flatten (by object id + by (detector, components) key) rather than touching the double-append; spice-side dedup as belt. Budget: VD-DET counts drop corpus-wide (the 8c36212 lesson: gate the FULL corpus, watch RC-DET exclusion interplay).

### KH-389: PM-002 negative "distance from board edge" leaks through RF/edge-mount branches; off-board-parked parts read "overhangs board edge" at ERROR

**Severity:** MEDIUM (22,147 negative PM-002 findings on 6,731/18,745 corpus boards; 8,991 below −5mm are parked-off-board WIP, not overhangs)
**File:** `skills/kicad/scripts/analyze_pcb.py:3648-3662` (signed bbox gap math — correct), :3693 (KH-344 rewrite guarded `if clearance < 0 and not is_rf and not is_edge_mount` — RF/edge-mount branches still emit :3687 literal "X is -Nmm from board edge"), :3508/:3542 (loose substring classifiers), no distinction between overhang and fully-off-board
**Discovered:** 2026-08-20, SacMap soak claim PM-002 (PARTIAL — math fine, framing wrong); corpus-scanned

**Fix direction:** extend the KH-344 rewrite to all branches (message should never render a negative "distance"); classify fully-outside-outline as "component placed off-board (n mm outside outline)" at INFO/WARNING, reserving ERROR for genuine partial overhang. Budget: PM-002 message/severity churn corpus-wide (large).

### KH-390: BOM-coverage denominators differ between DS-003 (per-reference, lacking-MPN polarity) and SS-002 (unique value+footprint lines, having-MPN polarity)

**Severity:** LOW
**File:** `skills/kicad/scripts/analyze_schematic.py:5242-5255+:5313-5315` (DS-003) vs `:5465-5487+:5505` (SS-002); identical `real` filter duplicated verbatim, then diverging grouping; SS-002's own comment :5474-5476 argues against per-reference counting
**Discovered:** 2026-08-20, SacMap soak claim B15 ("17/48" beside "21/27" for one fact)

**Fix direction:** adopt SS-002's unique-line basis in DS-003 (the project already picked a side) and label the basis in both summaries. Budget: DS-003 summary text corpus-wide.

### KH-391: summarize_findings mislabels deep-review categories as rule_id, overflows column format, and shows 0/0/0 confidence due to vocabulary mismatch

**Severity:** LOW-MEDIUM (the system's most rigorously evidence-gated findings display as having NO evidence)
**File:** `skills/kicad/scripts/summarize_findings.py:334` (rule_id = category), :234 ({:<14} vs 17-char "manufacturability"), :183+:201 (bucket keys deterministic/heuristic/datasheet_backed vs deep-review's high/medium/low — never match; --by-confidence mixes both vocabularies and "high" collides with the severity bucket)
**Discovered:** 2026-08-20, SacMap soak claim B15c (+2 defects beyond the claim). --json output is fine (sources/detectors disambiguate) — text table only.

**Fix direction:** tag deep-review rows (e.g. "dr:usb_power" or a source column), widen format, map or separately-bucket deep-review confidence.

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

_43 open KH-* + 7 open TH-* issues: NEW 2026-08-20 SacMap-soak batch KH-373..391 — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-380 (NR-001 unreachable), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch), KH-381 (cross_analysis checks-run), KH-382 (XV-002 hash order → determinism batch), KH-384/385 (gate cwd + quote elision), KH-387 (PR#37-leftover thermal confidence), KH-388 (VD-DET dup finding_ids), KH-389 (PM-002 leaks); LOW: KH-390/391. KH-371/372 LOW (lifecycle LC-ACT provenance omission forcing trust_level=low; LC-005 responded-only denominator + None-as-active — PR #37 left-outs, code-verified 2026-08-17, no corpus runner so live-API verification needed); KH-370 MEDIUM (KH-220 description-substring oscillator FP → false XL-DET/CD-DET, GitHub #33, repro-verified 2026-08-01, v2.2.x batch); KH-368/369 MEDIUM (JSONC string corruption dropping config layers; Action find|head-1 arbitrary project pick — external-review finds, code-verified 2026-07-26); KH-366/KH-367 MEDIUM (hash-order
nondeterminism: RC-DET + DO-DET/en_net, pre-existing in v2.1.0, gate-flake
risk — filed during v2.2 Tasks 4/13; 3 known instances = systemic class); the
2026-07-24 audit batch KH-358..365 (KH-359 HIGH net-identity merge — natural home = #25 release; KH-358/360/361/364/365 MEDIUM; KH-362/363 LOW) + KH-357 MEDIUM (BE-001 rect-diagonal false positive, GitHub #31) + KH-355 LOW (multi-channel FB-pin selection, needs design) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items. Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md` (verified subset only — forward-compat KHPA-001/002 items live in the roadmap, not here). The v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15, and gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
