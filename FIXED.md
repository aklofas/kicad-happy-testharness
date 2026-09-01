# Fixed Issues

Record of resolved kicad-happy analyzer bugs (KH-*) and test harness issues (TH-*).
Shows what changed, where, and how it was verified — useful for cross-referencing
regressions, understanding analyzer evolution, and onboarding collaborators.

> **Protocol**: When fixing issues, remove them from [ISSUES.md](ISSUES.md) and add here
> in the same session. Each entry must include: root cause, fix description, and
> verification results. See README.md "Issue tracking protocol" for full details.
> Open issues are in [ISSUES.md](ISSUES.md).

---

## 2026-09-01 — TH-051: dual-format twins raced on one thermal output file under parallel runs

**Severity:** MEDIUM-latent (silent nondeterministic winner even when it
"worked": X.kicad_sch.json and X.sch.json — the same board analyzed in both
formats — both strip to `{stem}_thermal.json`, so under `--jobs N` two
workers wrote the SAME output concurrently; last-writer-wins at best, torn
JSON at worst. v2.2.0's regen got lucky/zero; the v2.2.1 regen surfaced it
as 15 intermittent thermal FAILs on 8 twin-pair boards with identical
JSON-error offsets on both twins that MOVED between passes — the race
signature. Sequential retry: 8/8 repos clean.)
**File:** `run/run_thermal.py` (`_process_one_thermal` output naming;
`find_thermal_pairs`)
**Discovered & fixed same session** (v2.2.1 combined corpus regen)

- **Fix:** `thermal_output_stem()` helper + dedup in `find_thermal_pairs`
  keyed on (repo dir, output stem) — only the first twin runs (sorted order
  prefers the modern `.kicad_sch`), making the winner deterministic AND
  removing the race. Also halves redundant twin work.
- **Verification:** new `tests/test_run_thermal_pairs.py` (2 tests);
  thermal full-corpus pass 4 post-fix (see `regen_runners_pass4.log`).
- Related cleanup in the same session: 127 ancient orphan outputs removed
  (pre-v1.3 wrapper / corrupt JSON, inventory
  `results/v221_regen/orphans_removed.txt`) — the v2.2.0 record's queued
  housekeeping; they were crashing the v2.2.1 spice skill's summary print
  (pre-existing skill bug on legacy-format inputs, crashes identically at
  43dad23 — not a v2.2.x regression).

---

## 2026-09-01 — TH-050: find_schematic_outputs fed capability_mode.json sidecars to the spice/emc/thermal runners

**Severity:** LOW-visible / long-standing (v2.2.0-and-earlier processed the
sidecars SILENTLY, writing garbage `<type>/<repo>/capability_mode.json`
outputs — 17,355 accumulated — that collide with those analyzers' own
legitimate sidecar paths; the v2.2.1 spice skill's stricter error report
turned the class loud: 5,889 `KeyError: 'total_elapsed_s'` FAILs and
rc=1 on the v2.2.1 regen's spice/thermal passes)
**File:** `utils.py` (`find_schematic_outputs`)
**Discovered & fixed same session** (v2.2.1 combined corpus regen, pass 1)

- **Root cause:** the discovery glob (`*.json` per repo dir) had no name
  filter, so the analyzer's run-metadata sidecar rode along as an "analysis
  output" into every consumer runner.
- **Fix:** skip `json_file.name == "capability_mode.json"` in
  `find_schematic_outputs` (central — covers run_spice/run_emc/run_thermal).
- **Verification:** new
  `tests/test_utils.py::test_find_schematic_outputs_skips_capability_mode_sidecar`
  (27/27 file total); regen pass 2 eliminated the sidecar class entirely
  (5,889 KeyErrors -> 0; remaining pass-2 failures were the distinct
  orphan-debris and TH-051 classes, resolved separately). Residual debris: the historical garbage
  `capability_mode.json` outputs under `results/outputs/{spice,emc,thermal}`
  linger unasserted (deliberately not mass-deleted — the path collides with
  each analyzer's own legitimate sidecar; same housekeeping bucket as the
  v2.2.0 record's ancient pre-envelope orphans).

---

## 2026-09-01 — KH-402 (MEDIUM): no-connect markers created mid-span connectivity — NC'd pins absorbed into passing wires' nets (GitHub PR #41, danielboston38)

Externally reported AND fixed in one motion (FIXED-direct; never open in
ISSUES.md — number assigned at adoption, next KH → 403). Credit:
danielboston38, who joins the v2.2.x release credits.

- **File:** `skills/kicad/scripts/analyze_schematic.py` (~:1583-1595,
  `build_net_map` no_connect loop)
- **Root cause:** the loop called both `add_point()` AND
  `union_with_overlapping_wires()` for every NC marker. The latter unions
  with every wire the marker's (x,y) lies ON — including a wire passing
  MID-SPAN beneath it, which KiCad does not connect. Two wrong outcomes:
  the NC'd pin was dragged into the passing wire's net (false connectivity
  — hides floating pins), and the absorbing net inherited
  `no_connect: true` (suppressing legitimate audits on the wire's real
  net).
- **Fix (`0fc045a`, squash of PR #41; folded to `v2.2.x-dev` as
  `da979fb`; origin/main advanced 43dad23 → 0fc045a per fold precedent):**
  drop the `union_with_overlapping_wires` call — `add_point()` key-sharing
  already handles the legitimate marker-on-pin/endpoint absorption; only
  the mid-span union is removed. KH-360's junction/label union untouched.
- **Verification:** upstream — PR #41 kicad-cli netlist oracle 16/18 →
  18/18 net agreement on the reporter's board; main-repo controller repro
  both directions; post-fold contract 707/8/3 + unpinned determinism
  double-run clean. Harness — `tests/test_kh402_nc_midspan.py` (5 tests:
  mid-span split RED @ ced9c8c / GREEN @ da979fb, endpoint-NC absorption
  preserved, isolated NC, plain mid-span pin guard, determinism
  double-build); unit tree 1,318/0. Incremental gate ced9c8c→da979fb:
  smoke STRICT-CLEAN;
  full corpus 170,014 units / 0 downgrades / 42-of-149,629 pairs moved, ALL
  attributed (32 schematic units across ~24 repos with geometry-verified
  markers — 27 own-file mid-span, 4 via child sheets, 1 near-endpoint
  0.018mm off-grid sub-variant; 9 emc board_info-metadata-only; 1 thermal
  gain). Exact nets: NT-001 +10, LB-001 −8 (eight falsely-shorted I2C pairs
  un-merged on one board), DO-DET/RS-001 +2 each, EP-AUD +1, TS-005 +1.
- **Gate budget:** one class — NC-mid-span net splits / nc-tag removals /
  downstream finding movement; corpus surfaced 32 units / ~24 repos (PR frequency scan under-predicted), each
  geometry-attributed (record
  `results/v22x_kh402_gate/adjudication_kh402.md`).

---

## 2026-08-31 — v2.2.x maintenance batch: 25 fixes on main-repo `v2.2.x-dev` (`43dad23..ced9c8c`)

Fixed in one SDD-planned batch (main-repo `.superpowers/sdd/2026-08-24-v2.2.x-maintenance-batch/`,
31 commits, every task independently reviewed; final whole-branch review clean). Harness
adoption: 13 new test files + 4 extended + `_build_sch.py` fixture support +
`tests/fixtures/kh392-antipad/` minimal-pair board. Adoption-file pytest sweep:
107 tests — 58 RED at `43dad23` (every new file has RED coverage), 107 GREEN at
`ced9c8c`. Full unit tree 1,313/0; contract suite 707 passed / 8 skipped / 3 xfailed
(baseline moved from 706/8/4 — the `test_only_deterministic_hash_seed` xfail lock
XPASSED and was converted to a positive lock per its own docstring).
Corpus gate: full budgeted corpus gate 43dad23→ced9c8c **CLEAN**
(170,014 units / 141,636 PASS / 0 downgrades; 149,629-pair whole-output walk
with 3 hand-adjudicated class-6-downstream residue units; RC-DET net exactly
0; FV-001 zero firings; gerber byte-identical; record
`results/v22x_gate/adjudication_v22x.md`).

### KH-357 (MEDIUM): BE-001 treated `rect` board outline as its diagonal — false edge-proximity findings (GitHub #31)

- **File:** `skills/emc/scripts/emc_rules.py`
- **Root cause:** a `rect` outline entry was measured as one segment start→end (the
  diagonal), so components near the middle of a large board read as "near the edge".
- **Fix (`a743adc`):** rect outlines expand to their 4 sides; distances measure to the
  nearest side, corner-order independent.
- **Verification:** `tests/test_kh357_be001_rect.py` (2 tests, RED→GREEN); task-28 A/B
  on USBTTL (gr_rect outline): 2 false BE-001 disappear, `board_edge` category 2→0.
- **Gate budget:** BE-001 drops near rect diagonals + possible NEW findings near real
  edges on rect-outline boards (class 9).

### KH-358 (MEDIUM): VP-001 tenting check read `remove_unused_layers` — a field nothing writes (audit KHPA-019)

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_via_in_pad`)
- **Fix (`9287a72`):** reads the real via tenting field parsed from the board.
- **Verification:** `tests/test_kh_v22x_pcb.py::test_vp001_reads_real_tenting_field`.
- **Gate budget:** VP-001 flips on tented via-in-pad boards (class 3).

### KH-361 (MEDIUM): `.kicad_dru` conditional rules applied as GLOBAL minimums (audit KHPA-016 part 3)

- **File:** `skills/kicad/scripts/analyze_pcb.py`
- **Fix (`43cd662` + `ced9c8c` polish):** conditional rules are skipped first-in-loop
  instead of applied board-wide; sorted `conditional_rules_skipped` list + `_count` +
  count-aware note ("1 conditional rule ..." / "N conditional rules ..."), emitted only
  when non-empty so unaffected boards stay byte-identical; `rules_checked` excludes skipped.
- **Verification:** `tests/test_kh362_discovery.py` conditional-rule tests (RED→GREEN).
- **Gate budget:** design_rule_compliance violation drops on conditional-`.kicad_dru`
  boards + additive keys (class 11; may compound with KH-362 on the same boards).

### KH-362 (LOW): project/.kicad_dru discovery returned the FIRST file in the directory, ignoring the board stem (audit KHPA-015)

- **Files:** `skills/kicad/scripts/kicad_utils.py`, `analyze_pcb.py`, `project_config.py`
- **Fix (`28e460a` + `30bab88`):** stem-matched `load_kicad_pro`/`load_kicad_dru`; a
  shared `find_project_settings_file` helper routes both the loader AND the
  `project_settings['source']` field (the old source path was an independent unsorted
  `os.listdir` scan — a live filesystem-order determinism bug and wrong-provenance claim,
  fixed in the same change with an adversarial listdir-monkeypatch RED test).
- **Verification:** `tests/test_kh362_discovery.py` (11 tests).
- **Gate budget:** netclass/design-rule shifts + `rules_source`/`source` naming the
  stem-matched file on multi-`.kicad_pro` dirs (class 12).

### KH-363 (LOW): stale module-global net-ID map could leak into pad `net_number` on re-entrant use (audit KHPA-017)

- **File:** `skills/kicad/scripts/analyze_pcb.py`
- **Fix (`51b1553`):** net-ID map reset at the top of `analyze_pcb` before footprint
  extraction.
- **Verification:** `tests/test_kh_v22x_pcb.py::test_net_id_map_reset_before_footprint_extraction`.
- **Gate budget:** none (single-run CLI outputs unaffected; re-entrant-use hygiene).

### KH-366 (MEDIUM) / KH-367 (MEDIUM) / KH-382 (MEDIUM): hash-order nondeterminism — RC-DET pick, DO-DET list order, en_net identity, XV-002 order (+ ~21 sibling sites)

- **Files:** `skills/kicad/scripts/signal_detectors.py`, `domain_detectors.py`,
  `validation_detectors.py`, `cross_analysis.py`
- **Root cause / correction:** KH-367's en_net defect was pin SELECTION in
  `domain_detectors._match_pin` (unsorted set iteration picking an arbitrary EN pin) —
  the originally-hypothesized `build_net_map` was EXONERATED (net numbering was already
  deterministic). Fix lands on the lexicographic-first EN pin.
- **Fix (`a5072a8` DO-DET rails_without_caps + rails_with_caps; `28a8836` XV-002
  emission order; `a721848` RC-DET candidate pick + en_net + sibling audit: ~14
  pick-changing + ~7 order-only sites across 4 files, itemized in the commit body):**
  sorted iteration at every site that reaches analyzer output.
- **Also (`85676da`):** CI determinism guard — analyzer must be byte-stable across
  processes with unpinned PYTHONHASHSEED. The guard proved its value pre-landing by
  catching KH-394 (below).
- **Verification:** `tests/test_kh366_367_determinism.py` (4 tests, corpus-board
  skipif-guarded); contract xfail lock `test_only_deterministic_hash_seed` XPASSED →
  converted to positive lock (contract baseline 706/8/4 → 707/8/3); task-28 determinism
  sweep 0 diffs unpinned across 4 fixtures.
- **Gate budget:** vs-baseline diffs on affected boards are the fix landing (class 18):
  RC-DET pick changes, DO-DET rails lists, en_net lexicographic-first, XV-002 order.

### KH-368 (MEDIUM): JSONC comment-stripping corrupted string values containing `//` or `/* */` — config layer silently dropped

- **File:** `skills/kicad/scripts/project_config.py`
- **Fix (`f26a7ca`):** 4-state string-aware scanner replaces the two comment regexes;
  `_TRAILING_COMMA` behavior preserved verbatim (its own non-string-awareness filed as
  KH-400).
- **Verification:** `tests/test_kh368_jsonc.py` (4 tests: URL survives, block marker in
  string, escaped quotes).
- **Gate budget:** URL-containing JSONC configs now load → suppression activations =
  finding disappearances (class 13, small).

### KH-369 (MEDIUM): GitHub Action schematic auto-detect was `find | head -1` — arbitrary project pick

- **File:** `action/detect_project.sh`
- **Fix (`02e222e` + `7c6e297` + `ced9c8c`):** deterministic ladder — one project or
  fail with the candidate list; PCB-only invocations with explicit INPUT_PCB survive
  missing/ambiguous schematics; PCB fallback sorted + node_modules-excluded.
  **Release note obligation:** multi-project Action users must now set inputs explicitly.
- **Verification:** `tests/test_kh369_entrypoint.py` (5 subprocess tests).
- **Gate budget:** none (CI path only, class 19).

### KH-370 (MEDIUM): KH-220 description-substring oscillator classification misfired on "internal oscillator" ICs → false XL-DET + CD-DET (GitHub #33)

- **File:** `skills/kicad/scripts/kicad_utils.py` (`classify_component` KH-220 branch),
  `signal_detectors.py` (XL-DET fallback)
- **Fix (`3a96995`):** internal-oscillator phrase exclusions + corroborating pin
  evidence; XL-DET fallback no longer invents `output_net`. **Deliberate residual:** the
  legacy `.sch` parser path stays permissive (`pins is None` short-circuit, documented in
  the classify_component docstring) — KH-370 symptoms can still occur on legacy `.sch`;
  not a regression, out of the fix's scope.
- **Verification:** `tests/test_kh370_oscillator.py` (5 tests, synthetic ADC
  minimal-pair); hackrf-one A/B: real crystal entries byte-identical, 8 fabricated
  output_net → null.
- **Gate budget:** XL-DET active_oscillator drops + output_net→null; CD-DET
  oscillator_output drops (class 6, could be broad).

### KH-371 (LOW) / KH-372 (LOW): LC-ACT findings omitted provenance; LC-005 denominator counted only responding APIs, `status=None` as active

- **File:** `skills/kicad/scripts/lifecycle_audit.py`
- **Fix (`4266ac6`):** LC-ACT carries `confidence`/`evidence_source` (copied from the
  sibling emit site) so `trust_level` is no longer forced low; lcsc-only-unknown
  wording; LC-005 accounts attempted/responded/active_confirmed, `status=None`
  structurally excluded, LCSC filtered as stock-only, firing rule `==1 && responded>=2`.
- **Verification:** `tests/test_kh371_372_lifecycle.py` (6 offline tests) +
  **live-API run 2026-08-31 (user-authorized), ALL TARGETS PASS** — board:
  CIRCUITSTATE/Mitayi-Pico-D1 `Mitayi-Pico-D1.kicad_sch` (57 components, 20
  unique MPNs; DigiKey + Mouser responding, element14 attempted/no key, LCSC
  correctly excluded from lifecycle accounting as stock-only). Results: 39
  findings (LC-ACT 11 / LC-005 11 / LC-006 8 / LC-004 8 / LC-001 1);
  LC-ACT 11/11 carry confidence=deterministic + evidence_source=api_lookup;
  LC-005 11/11 satisfy active_confirmed==1 && responded>=2 with counts named
  ("3 attempted, 2 responded lifecycle source(s)"); all 8 unknowns say
  "unknown", unknown∩active = ∅; ambiguous "Discontinued at DigiKey"
  (discontinued:false) honestly lands as unknown, not active; trust_summary
  39/39 deterministic / api_lookup, trust_level "high", zero
  unknown-confidence findings (pre-fix this board would have been forced
  low). LC-001 obsolete fired on W25Q32JVSSIQ (real DigiKey status). The
  LCSC-only-RESPONDING wording variant was not exercisable on this board (no
  part returned LCSC lifecycle data) — remains covered by the offline test.
- **Gate budget:** not corpus-gateable (class 19).

### KH-380 (HIGH) / KH-381 (MEDIUM): NR-001 was unreachable dead code; cross_analysis had no record of which checks ran

- **File:** `skills/kicad/scripts/cross_analysis.py`
- **Root cause (KH-380):** NR-001 read `board_outline['segments']`; the producer emits
  `edges` — the rule had NEVER fired corpus-wide.
- **Fix (`a1ac772`):** NR-001 reads edges (line/rect/arc; explicit circle skip avoiding
  the KH-399-class sibling bug); `checks_run` manifest (CheckRun entries incl. honest
  skip reasons) on every cross_analysis output.
- **Verification:** `tests/test_kh380_381_cross_analysis.py` (4 tests).
- **Gate budget:** NR-001 fires for the FIRST TIME EVER (class 14, NewKnown-style);
  `checks_run` = additive REQUIRED envelope key on all cross_analysis outputs → known
  schema-drift false-positive on stale corpus until regen (class 15; do NOT relax schema).

### KH-384 (MEDIUM) / KH-385 (MEDIUM): deep_review_gate cwd-dependent script paths; elided quotes always failed

- **File:** `skills/kicad/review/scripts/deep_review_gate.py`
- **Fix (`6f014e1`):** script paths anchor to the analysis dir (project dir defaults to
  its parent); elided quotes verify segment-wise in order (both norm and squash
  branches) with deterministic difflib nearest-match reasons (80/40 thresholds) in
  quarantine records.
- **Verification:** `tests/test_kh384_385_gate.py` (5 tests).
- **Gate budget:** deep_review is permanently excluded from regression-diff scope
  (class 19).

### KH-387 (MEDIUM): `_thermal_confidence` returned "datasheet-backed" for package_table Rθ

- **File:** `skills/kicad/scripts/analyze_thermal.py:473`
- **Fix (`8d5b566`):** package_table → "heuristic" (same rationale as PR #37's
  evidence_source fix).
- **Correction vs the filed budget note:** corpus movement is ZERO, not "large class" —
  pre-fix, the `tj_max_source == "default_125"` check already caught every real corpus
  board first (the datasheet tj_max path is corpus-wide dead, KH-376 plumbing gap). The
  fix is LATENT-PROTECTIVE: it matters when KH-376 lands. The LIVE twin — the
  assessment-level `confidence` at `analyze_thermal.py:444`, which has no such safety
  net — is filed as **KH-398**.
- **Verification:** `tests/test_thermal_assessments.py::test_package_table_confidence_is_heuristic_even_with_datasheet_tj_max`
  (direct unit test of the producer function — the case the corpus can't reach).
- **Gate budget:** zero thermal movement expected; ANY movement = escalate (class 10).

### KH-388 (MEDIUM): VD-DET double-emission → duplicate findings sharing one finding_id + duplicate SPICE sims

- **Files:** `skills/kicad/scripts/analyze_schematic.py` (flatten), `skills/spice/scripts/simulate_subcircuits.py`
- **Fix (`12aaadb`):** dedup aliased VD-DET findings at flatten — id()-based dedup
  general; semantic-key belt scoped to `detect_voltage_dividers` only (an unscoped key
  collapsed 46→3 legitimate VM-001 findings and crashed on dict-valued components —
  implementer-caught brief defect); spice consumer belt. `signal_detectors.py`
  double-append untouched per the 8c36212 danger note.
- **Verification:** `tests/test_kh388_vddet_dedup.py` (3 tests); bitaxeUltra A/B: 2
  aliased dividers removed; 150-board spot-check: 29 boards affected, RC-DET 0 movement.
- **Gate budget:** VD-DET duplicate drops (class 7); RC-DET must NOT gain (8c36212 watch).

### KH-389 (MEDIUM): PM-002 negative "distance from board edge" leaked; off-board parts read "overhangs board edge" at ERROR

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_placement`)
- **Fix (`15a5599`):** KH-344 rewrite unconditional in all branches (no negative mm
  anywhere); AABB-disjoint off-board parts get a distinct classification at `warning`
  severity ("placed off-board (N mm outside outline)"), same rule_id.
- **Verification:** `tests/test_kh_v22x_pcb.py` PM-002 tests (2).
- **Gate budget:** LARGE message/severity churn — ~22k findings / 6.7k boards (class 8).

### KH-390 (LOW): DS-003 and SS-002 BOM-coverage denominators disagreed

- **File:** `skills/kicad/scripts/analyze_schematic.py`
- **Fix (`5a85191`):** DS-003 groups by (value, footprint) unique BOM lines exactly like
  SS-002 (`bom_size` KEY SEMANTICS changed: per-ref count → unique-BOM-line count, same
  key name); both summaries label the basis ("unique BOM lines").
- **Verification:** `tests/test_detector_audits.py::test_ds003_ss002_share_unique_bom_line_denominator`;
  USBTTL A/B: bom_size 8→6.
- **Gate budget:** DS-003 summary text + count churn corpus-wide (class 16).

### KH-391 (LOW): summarize_findings mislabeled deep-review categories as rule_id, overflowed columns, 0/0/0 confidence

- **File:** `skills/kicad/scripts/summarize_findings.py`
- **Fix (`865a232` + `ee1dead`):** `dr:` prefix routed by source; rule column ≥21 chars
  (fits `dr:`+longest category); dr counter; honest coverage in both text and JSON modes.
- **Verification:** `tests/test_kh391_summarize.py` (5 tests).
- **Gate budget:** none (display CLI, class 19).

### KH-392 (HIGH): GP-001 sampler read every via ≥ ~0.7 mm as a reference-plane gap (GitHub #39)

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_return_path_continuity`)
- **Root cause:** KiCad fills store the antipad void carved around a via; a track's
  via-end sample probes center + 8 points at exactly 0.5 mm — all inside any void with
  radius > 0.5 (KiCad default 0.8/0.4 via at 0.15 clearance → 0.55). Every plane-fanout
  stub scored uniform 50.0% → severity-`error` EMC finding.
- **Fix (`0f33fdf`):** antipad-aware sampling — a sample within `via_dia/2 + clearance`
  (0.2 conservative + max zone clearance) of a via center is credited as an expected
  void; grid-bucketed via lookup; credit-only accounting (coverage never decreases).
- **Known residuals (deliberate, filed):** no via-layer-span filter (blind/buried vias
  can over-credit on multi-layer boards — **KH-397**) + all-zones clearance max; the two
  accepted false-negative mechanisms STACK on multi-layer/mixed-via/aggressive-clearance
  boards (final-review rider).
- **Verification:** `tests/test_kh392_kh393_gp001_power.py` +
  `tests/fixtures/kh392-antipad/` minimal-pair board (SENSE1 0.8 vs SENSE2 0.6 via,
  SENSE3 real-gap control); XTA-Interface A/B (207 vias): strictly monotonic coverage
  improvement; bitaxeUltra A/B: 37→6 return_path entries, 31 GP-001 findings drop, 0
  regressions.
- **Gate budget:** GP-001 / return_path_continuity entry drops, credit-only (class 1).

### KH-393 (HIGH): analyze_pcb never threaded power_rails into `is_power_net_name` — per-port rail names read as signal at all 5 call sites (GitHub #40)

- **Files:** `skills/kicad/scripts/analyze_pcb.py` (5 sites: power routing, return
  path, proximity pairs, current capacity, layer transitions), `kicad_utils.py`
- **Fix (`e65188d`):** rails loaded from schematic analysis (`statistics.power_rails` —
  the producer's real shape; the brief's top-level read was a verified-nonexistent
  shape) and threaded through all 5 sites; `--power-rails` CLI flag for PCB-only runs;
  additive `power_net_resolution` block on ALL pcb outputs makes the resolved
  classification inspectable.
- **Verification:** `tests/test_kh392_kh393_gp001_power.py` (P1_VBUS/VBUS minimal pair
  incl. `--gp001-debug` RED→GREEN sample-site pair).
- **Gate budget:** additive `power_net_resolution` block on all pcb outputs; zero
  classification changes in corpus runs (no rails passed) (class 2).

### KH-394 (MEDIUM): `disconnected_pads` pair order + island representative were PYTHONHASHSEED-dependent (fixed-on-discovery)

- **File:** `skills/kicad/scripts/pcb_connectivity.py:335/:479`
- **Discovered:** by the new v2.2.x determinism CI guard during pre-landing sanity
  (2026-08-25) — unsorted `pad_keys` set iteration; NOT covered by KH-366/367's audit
  (schematic-side files only). Never open in ISSUES.md.
- **Fix (`60d0f9e`):** sort `pad_keys` before island-representative selection.
- **Verification:** 6/6 unpinned trials clean both analyzers post-fix (4/6 differed
  pre-fix); task-28: XTA-Interface + bitaxeUltra reorder deltas match this class exactly.
- **Gate budget:** disconnected_pads pair-order churn in `--full` outputs (class 18;
  the corpus gate runs non-full pcb, so mostly gate-invisible).

---

## 2026-08-31 — KH-359 / KH-360 (shipped in v2.2.0; tracker-hygiene closure)

Both fixed by v2.2.0's core #25 hierarchical-bus-connectivity work (shipped
2026-08-20, main `43dad23`); their ISSUES.md entries stayed open by a
v2.2-arc tracker-hygiene miss — main-repo CONFIRMED closure 2026-08-31.
Gate-validated in the v2.2 budgeted gate (`c6b504a`→`e67aeb5` CLEAN
2026-07-26, `results/v22_gate/adjudication_v22.md`: KH-359 class-1 splits
exercised on 750 units / 372 repos) and oracle-validated (kicad-cli netlist
oracle 5/5 golden boards PASS --strict); harness tests
`tests/test_kh359_kh360_netmap.py` + `tests/test_kh359_suppression_bare_tail.py`
adopted 2026-07-26 (`d40ef20ca18`), RED @ c6b504a / GREEN @ e67aeb5.

### KH-359 (HIGH): same-name local labels on different sheets MERGED in the output nets dict (audit KHPA-003)

- **File:** `skills/kicad/scripts/analyze_schematic.py` (`build_net_map`)
- **Root cause:** union-find kept local labels sheet-scoped, but the final
  `nets` dict was keyed by bare display name — a second disjoint root with an
  already-present name silently extended the first net's pins. KiCad keeps
  them separate (sheet path is part of local-label identity).
- **Fix (v2.2.0 / #25):** sheet-qualified net identity at serialization —
  multi-sheet same-name locals emit as distinct qualified keys with
  `display_name`; corpus movement was the v2.2 gate's class-1 split budget.
- **Verification:** netlist oracle 5/5 --strict; v2.2 gate class-1 exercised
  750 units / 372 repos, 0 violations; harness tests above.

### KH-360 (MEDIUM): `union_with_overlapping_wires` stopped after the first matching wire (audit KHPA-007)

- **File:** `skills/kicad/scripts/analyze_schematic.py`
- **Root cause:** `union(k, wk1); return` after the FIRST overlapping wire —
  a mid-segment junction tap off an un-split backbone could leave the
  backbone disconnected depending on wire insertion order.
- **Fix (v2.2.0 / #25):** union every overlapping wire (early return
  dropped); covered by the same netlist oracle.
- **Verification:** oracle + v2.2 gate class-2 (junction-tap merges);
  harness tests above.

---

## 2026-08-20 — TH-048: seed.py enum-field assertions count None-field items in the expected total

**Severity:** LOW (5 false FAILs at the v2.2.0 regen; latent since LA-004 shipped)
**File:** `regression/seed.py` (`_field_spec_assertions`, enum branch)
**Discovered & fixed same session** (v2.2.0 combined corpus regen adjudication)

- **Root cause:** the enum-field template guards `all_valid` over items whose
  field is non-None, but emits `count_matches` with `value = len(detections)` —
  the FULL detector-findings count. A detector emitting mixed rule shapes
  (audit_led_circuits: LA-AUD rows carry `drive_method`, LA-004 Vf-floor rows
  don't) seeds an expectation off by the number of field-less rows.
  `count_matches` only matches field carriers, so the assertion fails on every
  board where both rules fire (5 boards at the v2.2.0 regen: jabr-cm5-carrier +
  Cesium Flight Computer/Test Rocket sheets).
- **Fix:** emit `value = n_with_field` (count of items carrying the field),
  matching the guard's own scoping.
- **Verification:** re-seed schematic post-fix → the 5
  "All audit_led_circuits drive_method values are valid" FAILs flip to PASS
  (expected 3-of-4 style counts); full-corpus checks 100.0%.

---

## 2026-07-16 — TH-046: `filter_manifest_by_repo` drops root-level gerber units on repo-scoped runs

**Severity:** MEDIUM (silent coverage gap in every `--repo`/`--cross-section` run)
**File:** `utils.py:302` (`filter_manifest_by_repo`)
**Discovered & fixed same session** (v2.1 budgeted gate adjudication)

- **Root cause:** the filter matched lines containing `repos/{owner}/{repo}/`
  (trailing slash required). 63 of 5,502 `all_gerbers.txt` entries are exactly
  the repo ROOT directory (gerber sets at repo top level) — nothing follows the
  repo name, so the marker never matches and the unit is silently dropped from
  any repo-scoped invocation (`run_v14_gate.py --cross-section full`,
  `run_checks.py --repo`, etc.). Unfiltered runs (no `--repo`/`--cross-section`)
  were unaffected, which is why the v2.0 full gates showed 170,014 units while
  the v2.1 `--cross-section full` first pass showed 169,951 (−63, all
  `gerber/<owner>/<repo>/.json` root-level units).
- **Fix:** also match lines that END on the repo directory at a path-component
  boundary (`l.endswith("/repos/{owner}/{repo}")`, plus `os.sep` variant).
- **Verification:** RED→GREEN — new `tests/test_utils.py`
  `test_filter_manifest_root_level_unit` failed pre-fix, passes post-fix
  (26/26 file total); prefix-collision guard test (`owner/repo` must not claim
  `owner/repo2`) passes; v2.1 gate backfill run processed exactly the 63
  missing gerber pairs → gerber 5,502/5,502 PASS, total 170,014 units (exact
  match with all prior full-corpus benchmarks).

---

## 2026-07-16 — KH-354 / KH-356 (v2.1 gate-adjudication findings, fixed on main-repo `v2.1-dev`)

Both filed 2026-07-16 from the v2.1 gate adjudication, fixed same day on `v2.1-dev`
(`bd4372e` + `683297a`, tip now `683297a`). KH-355 remains open (needs a multi-channel
design decision). Contract suite vs `683297a`: **706 passed / 8 skipped / 4 xfailed**
(= 702 + 2 new KH-354 tests + 2 tests added to the reworked KH-341 file). Determinism
re-verified (double-run byte-identical ex-inputs).

### KH-354 (MEDIUM): audit_pwr_flags never credited PWR_FLAG — pwr_flag_warnings false-positived on every flagged rail

- **File:** `skills/kicad/scripts/analyze_schematic.py` (`audit_pwr_flags`)
- **Root cause:** `flagged_nets` scanned `nets[].pins` for the PWR_FLAG reference, but
  PWR_FLAG pins never register as net pins (build_net_map keeps them as source points) —
  the scan was structurally dead and every power_in-only rail warned even with a PWR_FLAG.
- **Fix (`bd4372e`):** dead scan replaced with the net-level `has_pwr_flag` credit
  (`net_info.get("has_pwr_flag")` → skip), per the fix sketch.
- **Verification:** `tests/contract/test_kh354_pwr_flag_erc.py` (2 tests via build_net_map,
  RED→GREEN; unflagged-rail warning invariant preserved).
- **Gate budget (incremental gate 8bc21d3..683297a):** pwr_flag_warnings disappearances on
  every rail carrying a PWR_FLAG — corpus-wide aux-section churn (correct behavior: the
  warning's own remedy now silences it).

### KH-356 (MEDIUM): KH-341 pour-connected suppression read stripped footprints[].pads — dead code in the real pipeline

- **File:** `skills/emc/scripts/emc_rules.py` (`check_decoupling_via_distance`)
- **Root cause:** `_pad_in_same_net_pour` consumed `pads[].abs_x/net_name`, fields
  analyze_pcb strips from ALL output footprints — the per-cap skip could never fire on real
  data; its contract test passed on synthesized fields (F6 IO-001 anti-pattern).
- **Fix (`683297a`):** helper reworked as `_cap_in_same_net_pour` reading fields that
  survive output — footprint center x/y + `connected_nets` (`pad_nets` fallback); center
  containment is a sound proxy for chip-cap pad positions.
- **Verification:** `tests/contract/test_kh341_dc003_suppression.py` REWRITTEN — fixtures
  now use the real output shape (no `pads` key), plus a producer-shape guard test that runs
  analyze_pcb on the simple-project fixture and asserts footprints carry
  pad_nets/connected_nets and NOT pads (RED→GREEN; 2-layer + foreign-net invariants kept).
- **Gate budget:** none at snap level (DC-003 had zero firings in the 170k baseline);
  affects --full-era/corpus-regen behavior only.

---

## 2026-07-15 — v2.1 bug batch: KH-338..346 + KH-348..350 (12 fixes on main-repo `v2.1-dev`)

Fixed in one planned batch (plan: main-repo `docs/superpowers/plans/2026-07-15-v2.1-bug-batch.md`),
one commit per issue on `v2.1-dev` (`40fa9f9..c65604a` + determinism follow-up `8bc21d3`, tip
after batch = `8bc21d3`). Every fix has a RED→GREEN regression test staged UNCOMMITTED in
`tests/contract/` (11 files, 36 test functions; KH-340+KH-349 share one file) — all RED at `2067260`, GREEN at `8bc21d3`.
Full contract suite vs `8bc21d3`: **702 passed / 8 skipped / 4 xfailed** (= 666 baseline + 36).

### KH-338 (HIGH): usb_compliance failures never became findings[]; vbus_esd_protection false-failed on ESD arrays

- **File:** `skills/kicad/scripts/analyze_schematic.py` (`analyze_usb_compliance`)
- **Root cause:** (a) per-check results lived only in the aux section — no findings[] emission;
  (b) the VBUS ESD scan only credited `type == "diode"` parts with TVS keywords, so ESD-array
  ICs (USBLC6) with their own VBUS pin never counted.
- **Fix (`b07fd3d`):** `ic`-typed parts matching the shared ESD keyword list on the VBUS net now
  credit `vbus_esd_protection`; failed checks emit rich findings via `make_finding` — **new rule
  ids UC-001 (no VBUS decoupling), UC-002 (no VBUS ESD), UC-003 (CC pulldown missing), UC-004
  (VBUS capacitance undersized)**, all warning/deterministic/topology, detector
  `analyze_usb_compliance`. Findings are popped into top-level findings[] — the emitted
  `usb_compliance` section shape is unchanged. USER-APPROVED exception to the no-new-rule-ids
  rule (2026-07-15) — **harness must register UC-001..UC-004 in the known-rules set.**
- **Verification:** `tests/contract/test_kh338_usb_compliance.py` (2 tests, synthetic ctx).
- **Gate budget:** NewKnown UC-* corpus-wide; `vbus_esd_protection` fail→pass flips on ESD-array boards.

### KH-339 (MEDIUM): CP-003 touch-pad clearance measured to zone outline bbox, not filled copper

- **File:** `skills/kicad/scripts/analyze_pcb.py`
- **Fix (`7395b4e`):** new `_nearest_zone_copper_distance()` prefers `filled_bbox` over
  `outline_bbox`; outline fallback downgrades confidence to heuristic and says so in the
  description; finding gains `measurement_basis` key.
- **Verification:** `tests/contract/test_kh339_cp003_filled_bbox.py` (3 tests; SacMap 0.0→1.0mm repro).
- **Gate budget:** CP-003 value/description churn where fills exist; additive `measurement_basis` key.

### KH-340 (MEDIUM): VP-001 bbox hit-test ignored pad shape/rotation

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_via_in_pad`)
- **Fix (`846d05c`):** new `_point_in_pad()` — circle/oval exact (stadium test), other shapes as
  rotated bounding rect using the pad's absolute angle.
- **Verification:** `tests/contract/test_kh349_kh340_via_in_pad.py` (4 of its 7 tests; includes
  the 8.16mm-radial circular-pad repro).
- **Gate budget:** VP-001 disappearances on large circular/oval pads; rare NEW VP-001 on rotated pads.

### KH-341 (MEDIUM): DC-003 lacked same-layer-pour / 2-layer suppression

- **File:** `skills/emc/scripts/emc_rules.py` (`check_decoupling_via_distance`)
- **Fix (`8ae7501`):** early return when copper layer count == 2; per-cap skip when any pad sits
  inside a same-layer zone of its own net (`filled_bbox`/`outline_bbox` containment).
- **Verification:** `tests/contract/test_kh341_dc003_suppression.py` (3 tests).
- **Gate budget:** DC-003 disappearances on 2-layer boards (large class) + pour-connected caps.

### KH-342 (MEDIUM): sleep_current_audit scored divider legs independently and RC pull-ups as DC loads

- **File:** `skills/kicad/scripts/analyze_schematic.py` (`analyze_sleep_current`)
- **Fix (`334650f`):** signal-side classification before worst-case V/R — second resistor to
  ground → `divider` at V/(R1+R2) with `divider_partner`; shunt-C with no other DC sink
  (switch/led/diode/transistor/other-R) → `rc_filter` at 0.0µA. Plain pull-ups unchanged.
- **Verification:** `tests/contract/test_kh342_sleep_current.py` (3 tests; 680k+150k → 3.98µA repro).
- **Gate budget:** sleep_current entry type/current churn corpus-wide; rail totals shift.

### KH-343 (MEDIUM): rail-voltage inference mapped any net containing "USB" to 5.0V — including data lines

- **Files:** `skills/kicad/scripts/analyze_schematic.py` + `skills/kicad/scripts/signal_detectors.py`
  (both copies) + new shared `kicad_utils.is_usb_data_net_name()`
- **Fix (`40fa9f9`):** VBUS keeps the 5.0 fallback; bare "USB" only when the name is not a data
  line (markers USB_D/USBDP/USBDM/USBDN/DPLUS/DMINUS or D+/D- suffix). Both copies fixed via the
  shared helper (exactly these two consumers).
- **Verification:** `tests/contract/test_kh343_usb_rail_voltage.py` (2 tests, both copies).
- **Gate budget:** rail_voltages loses USB-data entries → cascading disappearances possible in
  AM-001/OV-001/FT-001, passive derating, sleep-current.

### KH-344 (LOW): PM-002 "move further from board edge" on negative courtyard distances

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_placement`)
- **Fix (`823b458`):** negative clearance (non-RF, non-edge-mount) reframed as "courtyard
  overhangs board edge by X mm" with a verify-intent recommendation; severity logic unchanged.
- **Verification:** `tests/contract/test_kh344_pm002_overhang.py` (2 tests).
- **Gate budget:** PM-002 summary/recommendation text churn on overhang findings.

### KH-345 (LOW): CLI/doc drift — simulate_subcircuits had no --text; SKILL.md showed broken --temp-range space form

- **Files:** `skills/spice/scripts/simulate_subcircuits.py`; `skills/kicad/SKILL.md:633`
- **Fix (`c65604a`):** `--text` added (reuses `output_filters.format_text` via the existing
  kicad-scripts path bridge; tolerant of early-exit reports without `total_elapsed_s`);
  SKILL.md example switched to `--temp-range="-40,105"` (line count unchanged, 848).
  USER-APPROVED choice: add the flag rather than doc-only (2026-07-15).
- **Verification:** `tests/contract/test_kh345_spice_text_flag.py` (3 tests).
- **Gate budget:** none (JSON output unchanged).

### KH-346 (LOW, latent): per-pin absolute_max SpecValue read was unit-blind

- **File:** `skills/datasheets/scripts/datasheet_verify.py`
- **Fix (`09c62ef`):** new `_spec_max_voltage()` — first entry with unit V or no unit — used only
  in the `_v1_view` per-pin path; `_spec_max` untouched (its rec-vs-abs callers compare like units).
- **Verification:** `tests/contract/test_kh346_specmax_units.py` (3 tests).
- **Gate budget:** none (no extraction populates per-pin absolute_max yet).

### KH-348 (LOW): lifecycle `--only lcsc` returned all-unknown silently

- **File:** `skills/kicad/scripts/lifecycle_audit.py` (`audit_bom`)
- **Fix (`4916e05`):** LCSC-only source set → top-level `capability_note` + leading observation;
  LC-004 rule fields skipped for unknown-status rows (rows kept for temp data — same shape as
  active rows, schema-safe).
- **Verification:** `tests/contract/test_kh348_lcsc_only_lifecycle.py` (2 tests, mocked audit_component).
- **Gate budget:** none (network analyzer, not in corpus gate). Additive `capability_note` key.

### KH-349 (MEDIUM, GitHub #28): VP-001 flagged vias in copper-less pads

- **File:** `skills/kicad/scripts/analyze_pcb.py` (`analyze_via_in_pad`)
- **Fix (`9320931`):** collector skips pads whose layer list contains no `*.Cu` entry (missing
  layer list keeps old behavior). Close GitHub #28 at v2.1 ship.
- **Verification:** `tests/contract/test_kh349_kh340_via_in_pad.py` (3 of its 7 tests; Dwgs.User repro).
- **Gate budget:** VP-001 disappearances on cleared-layers pad boards (already in roadmap budget).

### KH-350 (MEDIUM, GitHub #29): courtyard overlap used single AABB per footprint

- **File:** `skills/kicad/scripts/analyze_pcb.py` (extraction + `analyze_placement`) +
  `envelopes/pcb.py` + regenerated `references/output-schema.md`
- **Fix (`8529c94`):** CrtYd fp_line segments chained into closed polygons (`_chain_segments`,
  tol 0.01mm; fp_rect/fp_poly direct; arcs/circles → AABB fallback), emitted as new footprint key
  `courtyard_poly` (declared in envelope description). `analyze_placement` keeps AABB as
  pre-filter, then grid-samples true polygon overlap (`_refined_overlap_mm2`, 24×24) — zero true
  overlap → finding skipped; else refined area drives severity. Close GitHub #29 at v2.1 ship.
- **Verification:** `tests/contract/test_kh350_courtyard_poly.py` (6 tests incl. end-to-end
  extraction on a synthetic cross-courtyard board and the R2-in-notch no-finding repro).
- **Gate budget:** courtyard-overlap disappearances/downgrades on QFP-adjacent placements +
  **additive `courtyard_poly` key corpus-wide** (assertion drift until corpus regen, same class
  as `has_pwr_flag`).

### Batch follow-up: pwr_flag_warnings ordering was hash-randomized (pre-existing, found by batch verification)

- **File:** `skills/kicad/scripts/analyze_schematic.py` (`audit_pwr_flags`)
- **Root cause:** `for net_name in known_power_rails:` iterated a set — per-process hash
  randomization made `pwr_flag_warnings` order flip between runs (byte-stability violation,
  probabilistic; predates this batch).
- **Fix (`8bc21d3`):** `sorted(known_power_rails)`.
- **Verification:** 4-process double-run byte-identical (ex-`inputs`) on the simple-project
  fixture for schematic + PCB.
- **Gate budget:** pwr_flag_warnings ordering stabilizes — cached corpus comparisons that
  captured the other order will churn once.

---

## 2026-07-15 — KH-351 / KH-352 / KH-353 (anyasabo fork-fix port, fixed on arrival at main-repo v2.1-dev)

Three detector fixes authored by **anyasabo** (GitHub fork `anyasabo/kicad-happy`),
ported to main-repo `v2.1-dev` as `036c6bf` / `d657493` / `f50aa6e` (+ `2067260`
schema declaration). Filed directly here — the bugs arrived already fixed. Harness
adopted 3 fork tests + 1 fixture into `tests/contract/` (7 test functions), all
verified RED at pre-fix `0c0ba34` → GREEN at `2067260` locally.

### KH-351 (MEDIUM): stray NC marker on a multi-pin net flips all its pins to NO_CONNECT

- **File:** `skills/kicad/scripts/analyze_schematic.py`
- **Root cause:** the net-level `no_connect` flag is set when *any* point in a net's
  union-find group is an NC marker, and `ic_pin_analysis` consumed that flag directly —
  so a single stray NC marker absorbed into a rail (e.g. VBUS/GND) reported every
  IC/connector pin on that rail as NO_CONNECT.
- **Fix (main-repo `036c6bf`, author anyasabo):** the net-level flag is only honored
  for single-pin nets (`has_no_connect`); multi-pin nets report the real net name.
- **Verification:** `tests/contract/test_no_connect_propagation.py` +
  `tests/fixtures/nc_marker_on_multipin_net.kicad_sch` (fork @ `23c5c31`) — a 2-pin
  connector on VBUS with a stray NC marker joined via same-name label; asserts both
  J1 pins report `VBUS`, not NO_CONNECT. RED at `0c0ba34` → GREEN at `2067260`.
- **Gate budget:** `ic_pin_analysis` `pins[].net` churn NO_CONNECT → real net name on
  multi-pin nets carrying a stray NC marker (downstream pin-net consumers may shift).

### KH-352 (LOW): XV-002 value-mismatch false positive on never-synced boards

- **File:** `skills/kicad/scripts/cross_analysis.py`
- **Root cause:** boards whose PCB `value` field was never synced from the schematic
  carry the footprint name (or its `lib:`-prefixed form) as the value — XV-002 flagged
  every such component as a schematic↔PCB value mismatch.
- **Fix (main-repo `d657493`, author anyasabo):** skip XV-002 when the PCB value equals
  the footprint name or its `lib:` suffix; genuine mismatches and whitespace
  normalization unchanged.
- **Verification:** `tests/contract/test_xv002_value_footprint.py` (fork @ `0a2b1c7`) —
  4 tests: footprint-name value, `lib:`-suffix value (both RED pre-fix), real mismatch
  still fires, whitespace suppression intact. RED at `0c0ba34` → GREEN at `2067260`.
- **Gate budget:** XV-002 disappearances where PCB value == footprint name or its
  `lib:`-suffix (never-synced boards).

### KH-353 (LOW): RS-001 does not recognize PWR_FLAG as a rail source declaration

- **File:** `skills/kicad/scripts/analyze_schematic.py`
- **Root cause:** RS-001 (rail without source) ignored PWR_FLAG symbols, firing on
  rails the designer explicitly declared powered via PWR_FLAG.
- **Fix (main-repo `f50aa6e` + `2067260`, author anyasabo):** PWR_FLAG pins register
  internally as `source="pwr_flag"`; new `nets[*].has_pwr_flag: bool` declared on
  `NetEntry` (default false, present on EVERY net). Invariant unchanged: `#FLG` refs
  never appear in `nets[].pins`.
- **Verification:** `tests/contract/test_rs001_pwr_flag.py` (fork @ `16c6265`) —
  2 tests: PWR_FLAG net gets `has_pwr_flag=True` with `#FLG01` absent from pins;
  plain net gets `has_pwr_flag=False`. RED at `0c0ba34` → GREEN at `2067260`.
- **Gate budget:** RS-001 (+ RS-002 per the family-budget rule) disappearances on
  rails carrying PWR_FLAG. `has_pwr_flag` is an additive key on all schematic nets —
  expect `test_schema_drift`-style assertion drift until corpus regen (additive;
  do NOT relax schema).

---

## 2026-07-12 — KH-347 (MEDIUM): deep_review_gate net cite-check single-identity + quote match breaks on Unicode/hyphenation

- **File:** `skills/kicad/review/scripts/deep_review_gate.py`
- **Discovered:** 2026-07-12 (SacMap rev2 run-6 — the v2.0 A/B soak leg @ `a9504cf`)
- **Root cause:** (a) `load_anchor_sets` built the net anchor set from schematic internal
  net names only. One physical net carries three identities — schematic internal name
  (`__unnamed_10`), analyzer `display_name` (`U4.VBUS`), and PCB net name
  (`Net-(J1-VBUS)`) — so citing either human-readable form quarantined the finding; the
  reviewer had to rewrite 4 legitimate findings to the opaque internal name, now frozen
  in the durable `deep_review.json`. (b) The PDF quote match: the filed
  "whitespace-sensitive" wording was **partially stale** — `_norm_text` whitespace
  collapse existed since `85d719c` and ran in run-6. The actual residual failure modes,
  proven from the run-6 artifact (quote truncated right before `°C`), were Unicode
  symbols (°C-class) and PDF line-wrap hyphenation (`over-\nvoltage`).
- **Fix (main-repo `76185a5` + `20cdf89`):** (a) `load_anchor_sets` accepts all three
  net identities — schematic name, `nets[name].display_name`, and pcb.json net names
  (top-level `nets` values ∪ `net_name_to_id` keys, both emitted unconditionally);
  unknown nets still quarantine. (b) `_norm_text` gained NFKC fold +
  punctuation→word-break, plus a `_squash` fallback that absorbs "5.5V" vs "5.5 V" and
  line-wrap hyphenation; new `_quote_in_text(quote, text)` helper, same failure message.
  Fabricated quotes still quarantine. Behavior note: `finding_id` re-derives when
  citation content changes (content-hash by design). Schema untouched (`evidence.nets`
  items are unconstrained strings).
- **Verification:** 4 new contract tests in `tests/contract/test_deep_review_gate.py`
  (PCB-only net `Net-(D1-K)` accepted, `display_name` accepted, unknown net still
  quarantined, quote match tolerates °C/unit-spacing/hyphenation with a fabricated-quote
  negative); module fixture now also runs `analyze_pcb.py` on the simple-project
  fixture. Contract suite vs `b4cf24c`: 659 passed / 8 skipped / 4 xfailed (655 + 4).
  Main-repo spot-check vs run-6 evidence: poster-child finding rewritten to
  `Net-(J1-VBUS)` → 10 verified / 0 quarantined, exit 0. Incremental full-corpus
  symmetric gate `a9504cf` → `b4cf24c` STRICT-CLEAN against a zero-delta budget
  (`results/v20_kh347_gate/`).

---

## 2026-07-12 — KH-337 (P0, v2.0 tag-blocking): datasheet_verify silent zero findings on v2 extraction caches

- **File:** `skills/datasheets/scripts/datasheet_verify.py`
- **Discovered:** 2026-07-12 (SacMap rev2 run-5 external review, verified vs v2.0-dev `f57277d`)
- **Root cause:** All three verifiers (`verify_pin_voltages`, `verify_required_externals`,
  `verify_decoupling`) consumed v1-format extraction keys only — `extraction.get("pins")` /
  `application_circuit` guards and singular `p.get("number")`. v2 caches store
  `base.pinout[]` (plural `numbers`, category blocks), so every verifier short-circuited
  to zero findings while the trust gate still counted the part in `ics_with_extractions`
  — invisible degradation, spec §6 violation. Real-world: 3 high-quality SacMap caches
  (91/77/87) produced zero datasheet verification.
- **Fix (main-repo `a9504cf`):** `_v1_view` v2→v1 adapter — flattens `base.pinout[]` to
  `pins[]` (`numbers[0]` → `number`), resolves per-pin `voltage_abs_max` /
  `voltage_operating_max` via `power_domain` → `base.absolute_max["{domain}_max"|"{domain}"]`
  / `recommended_operating[domain]`; a per-pin `absolute_max` SpecValue overrides the
  domain lookup via `_spec_max`. Gaps with no v2 equivalent (per-pin `required_external`,
  `application_circuit`) emit a loud `extraction_not_verifiable` INFO finding, deduped to
  one per MPN. All not-verifiable emissions gate on the `_v2_adapted` marker, so v1 caches
  of any shape stay byte-identical to pre-adapter output. Folded in:
  `extraction_quality_low` deduped per MPN in `run_datasheet_verification` (was
  triple-emitted, once per verifier). Full report:
  main-repo `.superpowers/sdd/kh337-report.md`.
- **Verification:** 7 new contract tests in `tests/contract/test_datasheet_verify_v14.py`
  (v2 abs-max/op-max violations, benign v2 → exactly one not-verifiable INFO, v1 behavior
  unchanged, v1 without `application_circuit` → no spurious finding, per-pin override,
  quality-low single emission) — RED against pre-fix, GREEN at `a9504cf`. Full harness
  suite vs `a9504cf`: 655 passed / 8 skipped / 4 xfailed. Main-repo
  `_smoke_v14_roundtrip.py` exit 0 (findings=1, `extraction_not_verifiable` INFO).
  Incremental full-corpus symmetric gate `f57277d` → `a9504cf` STRICT-CLEAN against a
  zero-delta budget (`results/v20_kh337_gate/`).
- **Residual:** KH-346 filed (per-pin `absolute_max` SpecValue read is unit-blind — latent
  until extractions populate per-pin ratings).

---

## 2026-05-28 — KH-335 / KH-336 / TH-045 (finding_id well-formedness + schema drift, SKILL_FEEDBACK-2 follow-up)

All three surfaced by the harness `run_tests.py --unit` gate during
SKILL_FEEDBACK-2 validation (main-repo F3 = `finding_schema.assign_finding_ids`
stamping a `finding_id` on every finding). Closed together once main-repo
`56e5e2a` landed the rule_id convention fix and the harness re-gated green
(`run_tests.py --unit` = 1,286 pass / 0 fail / 0 skip across 85 files vs
kicad-happy `56e5e2a`).

### KH-335 (LOW): section-promoted detectors emit non-`XX-NNN` `rule_id`s → malformed finding_id

- **File:** `skills/kicad/scripts/finding_schema.py` `_derive_finding_id`
- **Root cause:** Once F3 stamped a `finding_id` on every finding,
  `_derive_finding_id` built `{source}:{rule_id}:{locator}` using `rule_id`
  verbatim. Detectors emitting non-conventional `rule_id`s — lowercase section
  names (`voltage_dividers`, `validation_findings`) and audit/detection suffix
  forms (`EP-AUD`, `LA-AUD`, the `*-DET` family) — produced ids the harness
  pattern invariant rejected (e.g. `schematic:voltage_dividers:96344a7cd2eb`).
- **Fix (main-repo `56e5e2a`):** `_derive_finding_id` now folds every
  non-numbered `rule_id` (and every `detection_id`) into the colon-free
  2-segment form `{source}:{token}` (e.g. `schematic:EP-AUD-j1`,
  `schematic:decoupling_analysis-<hash>`); only numbered `XX-NNN` codes keep the
  3-segment `{source}:{RULE}:{locator}` form (e.g. `schematic:AM-001:r1`,
  unchanged). Every id now parses as one of the two spec §3.2 shapes regardless
  of the constructing detector.
- **Harness alignment:** `tests/contract/test_finding_id.py` — 3 stale
  assertions updated to the new form (`sch:absolute_max-abc123def456`; the
  no-locator hash-fallback test switched to a numbered code `GN-001` to keep
  exercising the 3-segment path).
- **Verified:** `tests/contract/test_finding_id.py` 9/9;
  `tests/test_b1_b2_finding_id_invariants.py` 10/10; full `--unit` 1,286/0/0.

### KH-336 (LOW): `transistor_pin_analysis` schema drift — stale corpus outputs predating F4

- **File:** harness `results/outputs/schematic/` (data, not analyzer code)
- **Root cause:** NOT an analyzer bug. The analyzer (`analyze_schematic.py:9186`)
  emits `transistor_pin_analysis` **unconditionally** as `[]` even on
  no-transistor inputs, and `--schema` correctly lists it in both `required` and
  `properties` (verified by running the analyzer on a no-transistor synthetic
  schematic: key present, value `[]`, `schema_version` `1.4.0`). The
  `test_schema_drift::test_schematic_schema_drift` failure was caused by ~12-day
  stale `results/outputs/schematic/` outputs predating F4 (`e5567d4`) that lacked
  the key, so the union-of-fresh-outputs sampled by the drift test missed it.
- **Fix:** regenerated the `quick_200` schematic corpus
  (`run/run_schematic.py --cross-section quick_200 --jobs 16` against kicad-happy
  `56e5e2a`) so fresh schema-1.4.0 outputs carry `transistor_pin_analysis`. Kept
  the key `required` in the contract (it IS always emitted; matches
  `ic_pin_analysis`).
- **Verified:** `tests/test_schema_drift.py` 12/12.

### TH-045 (LOW): `finding_id` pattern invariant rejected the `#N` collision suffix

- **File:** `tests/test_b1_b2_finding_id_invariants.py:86-94`
- **Root cause:** `assign_finding_ids` appends a `#N` suffix on id collisions
  (and `tests/contract/test_finding_id_coverage_e2e.py` mandates the `#N` form),
  but `_FINDING_ID_PATTERN` / `_FINDING_ID_DETECTION_PATTERN` had no trailing
  `#N` allowance — the two tests disagreed. The originally-feared `-AUD`/`-DET`/
  lowercase breadth turned out moot: main-repo `56e5e2a` folds those into the
  2-segment form the looser pattern already accepts, so the strict pattern stays
  strict.
- **Fix:** appended `(?:#\d+)?` before `$` in both regexes, reconciling the
  pattern test with the coverage-e2e test.
- **Verified:** `tests/test_b1_b2_finding_id_invariants.py` 10/10; full `--unit`
  1,286/0/0.

---

## 2026-05-16 — TH-043 + TH-043-residual (schema-vs-emitter drift across 4 analyzers, fully fixed)

### TH-043 (LOW): `--schema` declared keys not always emitted across schematic / pcb / gerber / thermal

- **Where fixed:** Two main-repo commits — `e27f0f9` (initial pass, 2 of 5
  pcb keys + all schematic / gerber / thermal keys) and `70d25ca`
  (TH-043-residual: remaining 3 pcb keys `ground_domains`,
  `placement_density`, `power_net_routing`). Per-key categorization:
  top-level dict keys → `{}` default, nested required list keys → `[]`
  default, scalar required keys genuinely missing in source files →
  `Optional[T] = None` (e.g., `board_thickness_mm` for `.kicad_pcb` files
  with no `(general (thickness ...))` node). Defaulted `Optional` fields
  moved to the tail of envelope dataclasses per Python's "defaulted-fields-last"
  rule. `70d25ca` also moved the 3 residual fields to the defaulted-tail of
  `envelopes/pcb.py PCBEnvelope`. **All 5 originally-filed PCB keys + all
  cross-analyzer keys now structurally present in every emitted output.**
- **Symptom (corpus-wide gate evidence from `run_v14_default_contract_gate.py`
  @ `87274cb701d` over 149,566 v14 snapshots):**

  | Analyzer | FAIL rate | Example drift |
  |----------|-----------|---------------|
  | pcb | 96.5% (18004/18658) | `board_metadata`, `board_thickness_mm`, `design_rule_compliance` |
  | schematic | 87.8% (32030/36462) | `title_block` (legacy `.sch` parser path didn't emit) |
  | gerber | 66.6% (3621/5439) | `pad_summary.smd_ratio`, `completeness.expected_layers` |
  | thermal | 8.5% (1364/16083) | `missing_info.default_rtheta_ja`/`default_tj_max` |

  emc + cross_analysis already clean (0% drift) — existence proof that the
  bug class is fixable per analyzer.

- **Root cause:** Each `--schema` `required` list declared structural
  invariants the analyzer's emit code didn't honor — e.g., `board_metadata`
  conditionally emitted only when certain title-block fields exist, `title_block`
  emitted only on the v6+ parser path (legacy `.sch` skipped it), thermal
  `missing_info.default_rtheta_ja` set only on one branch of the
  partial-fallback path. Same bug class corpus-wide.
- **Verification (e27f0f9 + 70d25ca combined):** `py_compile` clean across
  touched modules in both commits; `--schema` parses as valid JSON on every
  analyzer. Smoke-tested against `Arduino_OpenTherm_shield` (all 5 PCB keys
  populate naturally) + `martinribelotta/h730duino/gerber` +
  `jgrip/commodorelcd` + `chrisjohgorman/clock-design` (empty-default paths
  for the 70d25ca residual fields). `tests/test_schema_drift.py` clears
  fully (12/12 pass) on a harness checkout pinned to main-repo `70d25ca`.
  Regression-diff impact: zero — finding identity (`rule_id` + `components`)
  unchanged in either commit; only envelope-shape additions. Next
  `run_v14_default_contract_gate.py` run on v1.4-dev tip should report a
  clean drop to ~0% drift across all 4 analyzers.
- **No per-analyzer KH-*** — fix landed in two surgical commits; per-analyzer
  issues would be over-tracking. Filed harness-side as a single TH-043 with
  corpus-wide scope from the LOG 8 gate evidence (commit `40f5fa825d2`
  widened the original PCB-only scope; TH-043-residual was the harness-side
  re-open for the 3 keys e27f0f9 missed, closed the same day with 70d25ca).
- **Not tag-blocking** — pre-existing in rc.1, schema-vs-output mismatch
  affected only strict consumers, not the default-mode report. Shipped in
  rc.2 candidate `70d25ca` along with the other 7 main-repo fixes (per LOG
  entries 117 + 120).

---

## 2026-05-15 — KH-327 (bom SKILL.md description exceeds Codex 1024-char limit)

### KH-327 (MEDIUM): `bom/SKILL.md` description exceeds Codex 1024-char limit (1026/1024, 2 over)

- **Where fixed:** kicad-happy `488de7a` (`fix: trim bom SKILL.md description
  under Codex 1024-char cap (KH-327)`). Dropped redundant "cost estimate"
  trigger phrase (covered by "how much will this cost" earlier in the same
  list). Description now 1009 chars (15-char buffer under the 1024 cap).
- **Symptom:** `tests/test_skill_metadata.py::test_description_under_codex_limit`
  failed: `bom: 1026 chars (limit 1024)`. Codex users of v1.4.0-rc.1 hit a
  rejected/truncated skill load for `bom`; Claude Code users unaffected
  (different limit).
- **Root cause:** rc.1 doc-pass commit `c904bb3` ("docs: v1.4.0-rc.1 doc-pass")
  appended trigger phrases to the bom description, pushing it 2 chars over the
  Codex cap. Pre-doc-pass length was ~1018 chars (already close to the cap);
  the orchestration-softening edits added ~10 chars and went over. No
  length guard in the doc-pass workflow caught it; harness pre-push hook
  (`tests/test_skill_metadata.py`) caught it post-tag during the wrap-up
  bundle push attempt.
- **Verification:** `python3 tests/test_skill_metadata.py` post-fix: 4 passed,
  0 failed (was 3 passed, 1 failed). bom description length recomputed at
  1009 chars.
- **Not retroactive:** rc.1 was already published on GitHub at `c904bb3` —
  retroactive retag would create more confusion than it solves. Trim ships
  in the next tag in the release line (rc.2 or v1.4.0 final). Codex users of
  existing rc.1 stay broken until they upgrade.
- **v1.5 process candidates (noted by main-repo):** (a) one-time audit of all
  12 SKILL.md descriptions for any others sitting close to the cap before they
  regress under future edits; (b) mirror `test_skill_metadata.py` char-limit
  check as a pre-commit hook on the main-repo side so this catches at
  edit-time rather than at the harness layer.

---

## 2026-05-15 — KH-326 (analyze_pcb mis-parses fp_text value as a list)

### KH-326 (LOW): `analyze_pcb.py` mis-parses footprint `value` as S-expr token list, crashes emc + cross_analysis with AttributeError

- **Where fixed:** kicad-happy `8c36212` (rc.1 polish-pass from manual review +
  static audit). Two layers:
  - `skills/kicad/scripts/analyze_pcb.py` footprint parser now coerces
    `fp_text "value"/"reference"` to empty string when the field has no text
    body (was emitting a list of S-expression tokens for `(fp_text value (at
    ...) (layer ...) hide (effects ...))` shapes with no quoted body).
  - `skills/emc/scripts/emc_rules.py` `check_thermal_emc` and
    `skills/kicad/scripts/cross_analysis.py` `check_cross_validation` gained
    defensive `isinstance(str)` guards.
- **Symptom:** Running `analyze_emc.py` or `cross_analysis.py` with `--pcb` on
  `ccadic/TI92-revive` tracebacked with
  `AttributeError: 'list' object has no attribute 'lower'` (in
  `emc_rules.py:2962`) and `'list' object has no attribute 'replace'` (in
  `cross_analysis.py:416`). Schematic-only path didn't crash — the malformed
  field is on the PCB side.
- **Root cause:** `analyze_pcb.py` captured `(fp_text value ...)` element's
  property list rather than the quoted value string when the value text was
  missing. Footprint `kbLBrack1` (`18650:Kbpad`) was the exemplar — `value`
  came out as `[['at','0.508','-4.064'], ['layer','F.SilkS'], 'hide', ...]`.
  Both consumers assumed `footprint['value']` was always a string.
- **Verification:** Recheck #3 reran
  `regression/run_v14_gate.py --repo ccadic/TI92-revive --v14-dir
  /home/aklofas/Projects/kicad-happy --jobs 8` pointing at the polish-pass
  working tree. emc: 3 PASS / 3 WARN / 0 FAIL / 0 SKIP. cross_analysis: 4
  PASS / 2 WARN / 0 FAIL / 0 SKIP. Previously both showed SKIPs from the
  AttributeError. Gate verdict: CLEAN.
- **Filed by:** v1.4 Layer 1 regression gate 2026-05-14 (as a both-versions-
  fail-identically SKIP — present in v1.3.1 `968f5c8` too, NOT a v1.4
  regression).

---

## 2026-05-14 — KH-325 (capability_mode.json TOCTOU race)

### KH-325 (MEDIUM): `get_or_create_capability_mode()` non-atomic create races concurrent analyzers

- **Where fixed:** `skills/kicad/scripts/capability_mode.py` —
  `get_or_create_capability_mode()`. Fixed in kicad-happy commit `ea9b61b`
  ("fix: make capability_mode.json creation atomic + concurrency-safe").
- **Symptom:** Two or more analyzer processes starting concurrently against the
  same fresh `analysis/` directory could crash with
  `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`,
  or end up with divergent `run_id`s across the run's envelopes (HI-7).
- **Root cause:** `get_or_create_capability_mode()` did a non-atomic
  `path.exists()` check followed by `path.write_text()`. Between one process's
  check and the completion of its write, a sibling process could observe the
  file as existing but read it mid-write (empty / partial), then
  `json.loads()` it and crash. `capability_mode.py` is on every analyzer's
  startup path, so any concurrent multi-analyzer launch was exposed.
- **Fix:** Atomic create — write to a temp file in the same directory, then
  `os.link()` it into place; exactly one linker wins, losers fall back to
  reading the winner's file. `os.replace()` self-heals a partial file.
- **Verification:** Main-repo ran a 640-way concurrent stress test — 0 crashes,
  0 `run_id` divergence; harness contract suite still 454+8. Harness-side: the
  v1.4 Layer 1 regression gate, which originally surfaced this crash, re-ran
  CLEAN on the smoke cross-section against `ea9b61b` (0 FAIL across all 6
  analyzers).
- **Found by:** the v1.4 Layer 1 regression gate (`regression/run_v14_gate.py`)
  — a transient emc analyzer crash on `sparkfun/SparkFun_GNSS_mosaic-T` during
  the parallel corpus run, traced to the shared `capability_mode.json` sidecar.

---

## 2026-04-19 — TH-036 (TH-035 stray dirs recurred after registry cleanup)

### TH-036 (LOW): 15 stray project dirs recreated by re-seed using stale registry entries

- **Where fixed:** `reference/` tree (15 dirs deleted). No code changes — the loader
  guard from TH-035 (`regression/checks.py:339-350`) was already correctly skipping
  them with WARNING messages, so this was data cleanup only.
- **Symptom:** Every `regression/run_checks.py` invocation emitted 15 lines of
  `WARNING: skipping stray project dir without baselines/...` to stderr. Pattern
  identical to TH-035 (assertions/ exists but no baselines/, with doubled-suffix
  project names like `hardware_ubertooth-one_ubertooth-one`).
- **Root cause:** The TH-035 fix (commit `042245497ea`) only corrected the 2 SparkFun
  XRP Controller entries in `bugfix_registry.json` — it left 19 other entries with
  doubled-suffix project paths (KH-015, 045, 051, 085, 092, 094, 095, 102, 127, 147,
  152, 154, 165, 167, 183, 184). The next re-seed at `59285c3de15` ("Re-seed after
  KH-320/321/322") ran `generate_bugfix_assertions.py --apply` against those stale
  entries and recreated 15 stray dirs. Commit `05057265eca` later fixed the registry
  (0 doubled entries remain) but never deleted the dirs the prior re-seed had spawned.
- **Fix:** Deleted the 15 stray dirs. Each had at most 2 bugfix assertion files, all
  fully redundant with the sibling real-project dir's content. Verified file-by-file
  before deletion (only `pms67/HadesFCS/Hardware_Hades_Hades/.../Gerber_bugfix.json`
  differed from its sibling — by a single missing `evidence_source` line; sibling is
  the newer superset).
- **Why TH-035's loader guard wasn't enough:** the guard prevents the strays from
  *breaking* anything (run_checks skips them safely), but doesn't prevent them from
  being re-created or alert anyone to clean them up. Long-term prevention is to
  ensure `bugfix_registry.json` never carries doubled-suffix project names — already
  achieved at `05057265eca`. A defense-in-depth step would be `generate_bugfix_
  assertions.py` validating its target paths against `discover_projects()` before
  writing, but that's premature given the registry is the single source of truth.
- **Verification:**
  - Stray scan after delete: `0 remaining` (was 15)
  - smoke regression: `33,705/33,705 passed` (unchanged)
  - run_checks stderr: clean (was 15 WARNING lines per invocation)

---

## 2026-04-18 — KH-323 (pin_coverage_warnings undocumented in --schema)

### KH-323 (LOW): `pin_coverage_warnings` emitted by schematic analyzer but missing from `--schema`

- **Where fixed:** kicad-happy commits `c3e37b7..e6863f2` on `v1.4-dev` (Track 1.1
  typed envelope SOT). `pin_coverage_warnings` is now declared as an OPTIONAL field
  in `SchematicEnvelope` (`skills/kicad/scripts/envelopes/schematic.py`) and appears
  in `analyze_schematic.py --schema` under `properties` but NOT in `required` (so
  conditional emission is honored).
- **Symptom:** Harness `tests/test_schema_drift.py::test_schematic_schema_drift`
  flagged `pin_coverage_warnings` as drift on 2026-04-17 — emitted by the schematic
  analyzer but absent from the `--schema` declared envelope.
- **Root cause:** `pin_coverage_warnings` was added to runtime emission without a
  corresponding `--schema` declaration. Predates the typed envelope SOT.
- **Fix:** Track 1.1's typed envelope refactor declares `pin_coverage_warnings`
  on the dataclass, so it's automatically present in the JSON Schema 2020-12
  `properties` array. Harness side: removed from `_KNOWN_UNDOCUMENTED['schematic']`
  in `tests/test_schema_drift.py`.
- **Shape note:** Runtime emits `list[PinCoverageWarning]` with fields
  `component, lib_id, expected_pins, placed_pins, missing_count, message` —
  NOT `list[str]` as the prior allow-listed form may have implied. No harness
  Python code reads the list contents, so the shape change is harness-side no-op.
- **Verification (harness):**
  - `python3 tests/test_schema_drift.py` → 12 passed (helper tests + per-analyzer
    drift detectors after fixture regeneration on smoke section).
  - `analyze_schematic.py --schema` lists `pin_coverage_warnings` in `properties`
    (verified directly).
- **Harness impact:**
  - `tests/test_schema_drift.py::_KNOWN_UNDOCUMENTED['schematic']` —
    `pin_coverage_warnings` entry removed.
  - The whole drift test was rewritten to consume JSON Schema 2020-12 (Track 1.1
    breaking change) rather than the old descriptive-string dict format. See
    LOG-v1.4-progress.md entry 11 (2026-04-18) for full context.

---

## 2026-04-16 — KH-312 (sync scripts --mpn-list batch mode)

### KH-312 (LOW): Sync scripts needed `--mpn-list` batch mode

- **Where fixed:** kicad-happy commit `f49469c`,
  `skills/datasheets/scripts/sync_datasheets_{digikey,mouser,lcsc,element14}.py`.
- **Symptom:** Harness batch extraction had no way to download datasheets
  for a bare MPN list — sync scripts only accepted a `.kicad_sch` or
  analyzer JSON as positional input. Workaround (`fetch_datasheet_digikey.py
  --search <MPN>` in a loop) skipped the `datasheets/index.json` manifest
  update.
- **Root cause:** Input parsing assumed project context. No MPN-list
  fast path.
- **Fix:** Added `--mpn-list FILE` to all 4 distributor sync scripts
  (ticket scope was DigiKey; user elected to do all 4 for consistency).
  - `--mpn-list` is mutually exclusive with the positional input argument.
  - Reads one MPN per line; skips blank lines and `#` comments
    (full-line and inline); filters via `is_real_mpn()`; de-duplicates.
  - When `--mpn-list` is given without `--output`, output dir defaults
    to `./datasheets/` in cwd.
  - **Latent bug fixed:** `index["schematic"] = str(input_path)` would
    have written `"None"` into the manifest in MPN-list mode. Now uses
    `str(mpn_list or input_path)` at all 12 sites (3 per script × 4 scripts).
- **Verification (main repo):**
  - `--help` on all 4 shows `[input]` and `[--mpn-list FILE]` as alternatives
  - Synthetic MPN list (3 valid + DNP + dup + comments): all 4 scripts
    report `Loaded 3 unique MPNs`, dedupe, filter DNP correctly
  - Mutex errors: both `(input AND --mpn-list)` and `(neither)` produce
    clear argparse errors
  - 7-CLI analyzer `--help` smoke green (no regression)
- **Harness impact:** None (new CLI surface, not an analyzer behavior
  change — no re-seed needed). Batch extraction workflows can now target
  any of the 4 distributors with an MPN list.
- **Known non-blocking followups** (deferred to v1.4 polish):
  - `element14` api_key guard fires before dry-run evaluation (other 3
    allow dry-run without credentials; harness has the key, no current impact)
  - `index["schematic"]` field semantics doc — in MPN-list mode the field
    holds the MPN-list path, which is correct for staleness semantics but
    the field name is slightly misleading

---

## 2026-04-16 — TH-033 (KiCad 10 fixture discoverability + coverage)

### TH-033 (MEDIUM): No KiCad 10.0.0 test fixtures in the corpus

- **Where fixed:** `tools/generate_cross_sections.py`, `reference/smoke_pack.md`,
  `tests/test_kicad10_format.py` (new).
- **Symptom as filed:** "No corpus file is in 10.0.0 format (version 20260206)."
  Claim was based on sampling one file; survey was incorrect.
- **Actual state discovered:** Corpus already contains 42 repos with 198
  schematic files in KiCad 10 format (versions 20260306, 20260101, 20251028)
  and 37 repos with 59 PCB files (versions 20260206, 20250926, 20251101).
  34 repos have both. The gap was **test infrastructure**, not fixtures:
  no named cross-section for KiCad 10, no smoke-pack coverage, no targeted
  regression test.
- **Fix:**
  1. Added `section_kicad10()` to `generate_cross_sections.py` — returns all
     40 catalog repos with `10.0` in their `kicad_versions` list, ranked by
     assertion count. Available as `--cross-section kicad10`.
  2. Fixed `kicad_versions` section description (was `5/6/7/8/9`, now
     `5/6/7/8/9/10`) — it already included 20 KiCad 10 repos silently.
  3. Added 7 KiCad 10 repos to `reference/smoke_pack.md` (was 0):
     `7m4gmh/7seg-panel`, `Just4Stan/OpenRX`, `ADBeta/IR_UART`,
     `Coder1203/Macropad`, `cyfinfaza/Half-Bridge-Module`,
     `JuliCai/SmarterWatch`, `corybuecker/reflow-oven`. Mix of pure-v10 /
     mixed-v10-v9, varied sizes (1–23 schematic files), diverse categories
     (USB, keyboards, motors, wearables, thermal).
  4. New `tests/test_kicad10_format.py` (TIER=unit, 7 tests):
     - Confirms pinned fixtures actually report v10 file version
     - Runs schematic + PCB analyzers end-to-end on fixtures
     - Asserts `analyzer_type`, `schema_version`, `findings[]` present
     - Asserts every via carries a `type` field with a valid value (KH-318 regression guard)
  5. Re-snapshotted + re-seeded smoke with new entries (327 files, 13,031
     schematic + 5,619 PCB assertions, 0 failures).
- **Verification:** `test_kicad10_format.py` 7/7 pass. Smoke grew 20 → 27 repos.
  `kicad10` cross-section has 40 repos. Unit suite 965 → 972 tests, 0 failures.
- **Followup:** If KiCad 10.1+ ships with new format breaks, the `kicad10`
  section and smoke entries will naturally catch them (version strings
  starting `10.` are all included).

---

## 2026-04-16 — KH-320, KH-321, KH-322 (pre-v1.3 audit followups)

### KH-320 (LOW): 10 untagged math functions tagged as EQ-098..EQ-107

- **Where fixed:** kicad-happy commit `db277fe`, across `analyze_pcb.py`,
  `emc_formulas.py`, `emc_rules.py`, `kicad_utils.py`.
- **Fix:** Added `# EQ-NNN:` comment blocks for 10 math functions
  (EQ-098 through EQ-107). 7 self-evident geometry primitives (distance
  formulas) tagged as "Self-evident — 2D Euclidean distance" etc.; 3
  substantive functions cited real sources:
  - EQ-105 `estimate_inductor_h_field` — Jackson "Classical Electrodynamics"
    3rd ed. §5.6, Ott "EMC Engineering" Ch. 11
  - EQ-106 `check_inductor_leakage` — Ott "EMC Engineering" Ch. 11
    (15mm proximity threshold + EQ-105 H-field)
  - EQ-107 `snap_to_e_series` — IEC 60063 (E-series tables)
- **Harness side:** No re-seed needed (pure doc change). Next
  `audit_equations.py scan` picks up the 10 new tags.
- **Known tool-convention mismatch:** 9 of 10 tags were placed ABOVE the
  `def` line; `audit_equations.py find_untagged` looks inside function
  bodies so still flags them as untagged. Tags and sources are present —
  only the locator convention differs. Not filing as a new issue since
  the tags are valid; can be normalized during future audit tooling work.

### KH-321 (LOW): Corrected TPS62160, TPS63000 frequencies + narrowed SY820 prefix

- **Where fixed:** kicad-happy commit `b22bee4`, `kicad_utils.py:_KNOWN_FREQS`.
- **Fix:**
  - `TPS62160`: 2.5 MHz → **2.25 MHz** (TI SLVSAK8 §7.5 confirms fSW = 2.25 MHz typ)
  - `TPS63000`: 2.4 MHz → **1.5 MHz** (−37%; TI SLVS590M §7.5 confirms fS range 1.25–1.5 MHz)
  - `SY820` prefix narrowed to exact `SY8208` (800 kHz applies only to
    SY8208, not SY8200-series which is 500 kHz)
- **Harness re-seed:**
  - Re-ran schematic + PCB + SPICE + EMC on smoke + quick_200. Pre-re-seed
    check showed 3,772 assertion flips concentrated in (a) the KH-321
    cascade on boards with these parts, and (b) a separate stale baseline
    issue for `suggest_certifications` (985 boards) from the pre-existing
    c497fa6 CERT-001 hobby-gating change that predated our last smoke+quick_200
    re-seed — the `full` corpus projects were seeded before c497fa6 and
    quick_200's growth over time pulled them in.
  - Re-seeded SEED + STRUCT on smoke + quick_200 absorbed both cascades.
    Post-re-seed: 801,347/801,349 pass (1 pre-existing empty-.sch FND
    failure unrelated).
  - Bugfix registry regenerated (85 assertions). Unit suite 973/0/2.
- **Handoff source:** main-repo agent `2026-04-16` post-audit handoff.

### KH-322 (LOW): EQ-089 duplicate tag collision resolved upstream

- **Where fixed:** kicad-happy commit `e09b642`, `analyze_schematic.py:3920`.
- **Fix:** Renamed `# EQ-089:` → `# EQ-097:` at the I2C rise-time site in
  `_detect_i2c_buses`. The EMC cap-SRF site in `emc_formulas.py:cap_value_for_srf`
  retains EQ-089 (original holder).
- **Harness side:** Registry already aligned with this state in commit
  `2f587c5` (Pre-v1.3 audit sweep) — my local kicad-happy working tree
  had the rename applied pending upstream. Upstream now matches.
- **Verification:** `audit_equations.py scan` shows EQ-089 and EQ-097 as
  two distinct verified entries. No collision.

---

## 2026-04-16 — TH-035 (stray project dirs broke `--quick-sanity`)

### TH-035 (LOW): 16 stray project dirs in `reference/` had assertions/ but no baselines/

- **Where fixed:** `reference/` tree (16 dirs deleted), `regression/checks.py` (loader
  hardened), `regression/bugfix_registry.json` (one stale entry corrected),
  `tests/test_run_checks.py` (regression-guard test added).
- **Symptom:** `run_tests.py --quick-sanity` returned FAIL on 3 of 5 repos
  (greatscottgadgets/ubertooth, jgrip/commodorelcd, greatscottgadgets/hackrf)
  despite all assertions being valid. Main-repo CI `harness-quick-sanity`
  job dropped in main-repo commit `c45e161` as a result; `harness-smoke`
  (565 tests) retained.
- **Root cause:** A prior layout restructure left 16 "flattened" project dirs
  under `reference/{owner}/{repo}/` whose names embed the parent prefix twice
  (e.g., `hardware_ubertooth-one_ubertooth-one/` next to real sibling
  `hardware_ubertooth-one/`). The strays contained only `assertions/` (no
  `baselines/metadata.json`). `checks.py:load_assertions()` couldn't resolve
  a `project_path`, fell back to `None`, then `project_prefix(None) = ""`
  caused `find_output_file` to look for `ubertooth-one.sch.json` instead of
  `hardware_ubertooth-one_ubertooth-one_ubertooth-one.sch.json`.
- **Fix (3 parts):**
  1. Deleted all 16 stray dirs. Content audit confirmed each stray's files
     were also present in a sibling dir with newer content (generated by
     `regenerate_bugfix_assertions.py`), so no unique data lost.
  2. Corrected 2 bugfix_registry entries targeting
     `sparkfun/SparkFun_XRP_Controller` — the `project` field pointed at a
     flattened name (`Hardware_Production_SparkFun_XRP_Controller`) that
     never existed as a real project; changed to
     `Hardware_SparkFun_XRP_Controller` with `source_file: Production`.
     Re-ran `generate_bugfix_assertions.py --apply` to regenerate the
     assertion file at the correct path.
  3. Hardened `checks.py:load_assertions()` (Option 3a in main-repo
     handoff): when a project dir has `assertions/` but no `baselines/`
     AND `project_path` is unresolvable, emit a stderr WARNING and skip
     the dir rather than silently mis-resolving file paths. Prevents
     recurrence.
- **Verification:**
  - `run_tests.py --quick-sanity` now reports 5/5 PASS (ubertooth 477,
    commodorelcd 178, OpenMower 628, DIY-LAPTOP 2017, hackrf 3022
    assertions).
  - `run_tests.py --smoke` 566/0/0 (unchanged).
  - Full unit suite 972 → 973 (added
    `test_stray_project_dir_is_skipped_with_warning` in
    `tests/test_run_checks.py`).
  - `regression/audit_bugfix_paths.py` clean on sparkfun XRP.
- **Main-repo followup:** Once this commit is pushed, main-repo agent can
  re-enable the `harness-quick-sanity` CI job at whatever pin they bump
  to next (was dropped at pin `fa454ff3eb`).
- **Side effects:** Re-ran SPICE on `jgrip/commodorelcd` to refresh stale
  baseline (C53/C37 component references had drifted); `seed_structural
  --repo jgrip/commodorelcd --type spice` absorbed the diff. Reference
  file count: -17 (16 stray deletions + 1 commodorelcd structural).

---

## 2026-04-16 — KH-318, KH-319 (KiCad 10.0.1 format-compat fixes)

### KH-318 (HIGH): PCB via type detection always returned None

- **Where fixed:** kicad-happy commits `a17b453` (fix) + `782a5aa` (cleanup),
  `skills/kicad/scripts/analyze_pcb.py` `extract_vias()` and `_get_schema()`.
- **Symptom:** `via["type"]` in `analyze_pcb.py` output JSON was `None` for
  every via in every board. Microvias, blind vias, and buried vias were
  indistinguishable from through vias in the analyzer output.
- **Root cause:** `extract_vias()` used `get_value(via, "type")` which looks
  for a nested `(type X)` child. KiCad has never emitted that shape — the via
  type is a bare token between `(via` and `(at ...)` (e.g., `(via blind ...)`,
  `(via micro ...)`). Schema at `_get_schema()` also didn't list the `type`
  field in `vias._with_full_flag`.
- **Fix:** Replaced `get_value(via, "type")` with a bare-token scan (`blind` /
  `buried` / `micro`), default `"through"`. Every via now carries `type`
  unconditionally. Schema updated to list the field. Cleanup commit dropped
  dead fallback code and synced `output-schema.md`.
- **Verification:** Re-ran PCB analyzer on `quick_200` (4940/4949 pass, 9
  pre-existing timeouts on complex boards). Sampled outputs: all vias now
  carry `type: "through"`. Baselines re-snapshotted, SEED + STRUCT re-seeded
  (smoke 4,985 assertions + quick_200 115,803, 0 content failures). Schema
  drift test `test_pcb_schema_drift` passes.

### KH-319 (MEDIUM): `has_flag()` didn't match `(hide yes)` boolean sub-lists

- **Where fixed:** kicad-happy commit `ef5b672`, `skills/kicad/scripts/sexp_parser.py:209`.
- **Symptom:** Hidden pins reported as visible on any schematic saved by
  KiCad ≥9.0 (schematic version 20250114; the boolean format change landed
  at version 20241004).
- **Root cause:** `has_flag()` was `return flag in node`, membership test on
  the top-level list. Worked for legacy bare-token form `(pin ... hide ...)`
  but failed for post-20241004 form `(pin ... (hide yes) ...)` where `hide`
  is inside a sub-list.
- **Fix:** Broadened `has_flag()` to also match `(flag yes|true)` sub-lists.
  Backward compatible with old format; fixes all callers (today only
  `analyze_schematic.py:213` for pin-hidden detection, but safer against
  future `in_bom`/`on_board`/`dnp`/`locked`/etc. migrations).
- **Verification:** Re-ran schematic analyzer on `quick_200`. 15 KiCad 9+
  corpus boards showed assertion flips (theremin, PingDevKit, synthtest,
  cnlohr TMS9918ADisplay/F68, .sch legacy finds) — all consistent with
  "hidden pins now correctly treated as hidden" cascade (fewer
  connections → lower net counts, `analyze_connectivity` /
  `validate_power_sequencing` / `audit_rail_sources` counts drop).
  Re-seeded, smoke schematic 11,449 passing + quick_200 295,395 assertions
  with 1 pre-existing empty-`.sch` FND failure unrelated to this fix.
- **Handoff source:** main-repo agent `2026-04-16-kicad10-format-compat-fixes.md`.

---

## 2026-04-16 — TH-034 (run_datasheets missing datasheets/scripts sys.path)

### TH-034 (LOW): `run_datasheets.py --validate-only` crashed with ModuleNotFoundError

- **Where fixed:** `run/run_datasheets.py`, lines 46–49
- **Symptom:** `python3 run/run_datasheets.py --repo X --validate-only` raised
  `ModuleNotFoundError: No module named 'datasheet_extract_cache'` when
  `validate_extractions()` called `from datasheet_extract_cache import ...`.
- **Root cause:** `run_datasheets.py` inserted only `skills/kicad/scripts` into
  `sys.path` at module-load time, but `datasheet_extract_cache.py` lives in
  `skills/datasheets/scripts`. The validate path is only reached at runtime
  (inside `validate_extractions()`), so the missing path went unnoticed.
- **Fix:** Added `_ds_scripts = _kicad_happy / "skills" / "datasheets" / "scripts"`
  and `sys.path.insert(0, str(_ds_scripts))` alongside the existing kicad/scripts
  insertion.
- **Verification:** `python3 run/run_datasheets.py --repo jgrip/commodorelcd
  --validate-only --jobs 1` exits 0. New integration test
  `test_run_datasheets_validate_only_no_crash` passes.

---

## 2026-04-16 — KH-314, KH-315, KH-316, KH-317 (Session 11 harness-filed bugs)

### KH-317 (MEDIUM): XT-001 suppression read wrong `differential_pairs` path

- **Where fixed:** kicad-happy repo, `skills/emc/scripts/emc_rules.py` lines 2458–2478
- **Symptom:** XT-001 (crosstalk 3H rule) fired on 63 diff-pair nets across
  730 corpus boards that were clearly listed in the schematic's
  `design_analysis.differential_pairs`.
- **Root cause:** `check_crosstalk_3h_rule` read from
  `schematic.design_analysis.buses.differential_pairs` — a path that never
  existed. Schematic analyzer emits diff pairs flat at
  `design_analysis.differential_pairs`. Neither code path nor docs had this
  right (the `output-schema.md` and `_get_schema()` both documented the
  non-existent `buses` key). Result: the suppression set was empty on every
  board, so every diff pair slipped through to fire XT-001.
- **Fix:** Read all three candidate paths (current flat + legacy nested +
  legacy top-level). Also corrected the stale docs in both
  `_get_schema()` on `analyze_schematic.py` and
  `skills/kicad/references/output-schema.md` — real structure under
  `design_analysis` is `net_classification`, `power_domains`,
  `cross_domain_signals`, `bus_analysis`, `differential_pairs`,
  `erc_warnings`, `passive_warnings`.
- **Verification:** Synthetic test — USB_DP/DM and CAN_H/L suppressed,
  CLK/MISO still fires.
- **Commit:** a07bd4b

### KH-314 (LOW): `analyze_thermal.py` had no `--schema` command

- **Where fixed:** kicad-happy repo, `skills/kicad/scripts/analyze_thermal.py` lines 846–910
- **Symptom:** All other analyzers expose `--schema`; thermal errored with
  "expected --schematic argument".
- **Root cause:** Phase 6 `--schema` sync (session 9) covered schematic,
  PCB, gerber, EMC, and cross_analysis — missed thermal.
- **Fix:** Added a `--schema` branch at the top of `main()` that prints
  the output envelope (analyzer_type, schema_version, summary, findings,
  trust_summary, elapsed_s, optional missing_info) and short-circuits
  before the required `--schematic`/`--pcb` check.
- **Verification:** `analyze_thermal.py --schema` prints schema JSON and
  exits cleanly.
- **Commit:** a07bd4b

### KH-315 (LOW): schematic `--schema` advertised `hierarchy_context` not present in most outputs

- **Where fixed:** kicad-happy repo, `skills/kicad/scripts/analyze_schematic.py` lines 9060–9071
- **Symptom:** Harness schema-drift test flagged that `--schema` documented
  `hierarchy_context` which wasn't in most real outputs.
- **Root cause:** `hierarchy_context` is emitted conditionally (only when
  the analyzer has sub-sheet hierarchy context to report — rare in the
  corpus). The schema documented it as if always present.
- **Fix:** Marked `hierarchy_context`, `hierarchy_warning`,
  `_redirected_from`, and `_stale_file_warning` explicitly as OPTIONAL
  with a prefix string. Harness drift test already tolerates keys marked
  OPTIONAL.
- **Verification:** Drift test passes cleanly post-fix.
- **Commit:** 0882866 (actually shipped earlier but only filed/closed now)

### KH-316 (LOW): schematic/PCB findings[] nondeterministic order

- **Where fixed:** kicad-happy repo, `skills/kicad/scripts/finding_schema.py`
  (new `sort_findings()` helper), `skills/kicad/scripts/detection_schema.py`
  (sort list-valued identity fields in `compute_detection_id()`),
  analyze_schematic.py + analyze_pcb.py (call sort before serialization).
- **Symptom:** Two runs on the same input produced same set of findings
  in different array order. Same content, same count, different ordering.
- **Root cause:** Upstream set/dict iteration ordering leaked into
  findings list construction and into the `components` list inside
  individual findings. `compute_detection_id()` hashed the stringified
  list, so detection_id also shifted.
- **Fix:** Added `sort_findings()` in `finding_schema.py` that
  canonicalizes scalar `components`/`nets`/`pins` lists inside each
  finding and sorts the top-level list by
  (rule_id, detector, first_component, first_net, summary). Called at
  the end of main() / analyze_ functions. Also fixed
  `compute_detection_id()` to sort list-valued identity fields before
  hashing.
- **Verification:** `findings[]` array is now position-stable across
  runs. `components`/`nets`/`pins` within each finding are sorted.
  `detection_id` is invariant.
- **Known remaining:** Lists of *dicts* nested inside findings
  (`load_caps` under DO-DET, etc.) and `design_analysis` sub-sections
  still have non-canonical ordering. Out of scope for this fix —
  requires canonicalizing upstream detector builders that iterate over
  sets. Deferred to v1.4.
- **Commit:** 1725cb9

---

## 2026-04-15 — TH-031 (list-field matching in checks ops)

### TH-031 (LOW): SPICE/EMC structural seeders relied on Python list repr for regex matching

- **Where fixed:** harness repo, `regression/checks.py` — new `_field_strings` helper; `contains_match`, `not_contains_match`, `count_matches` now iterate list-typed field values instead of calling `str()` on them.
- **Symptom:** `seed_structural.py` emitted `\bR5\b`-style patterns with `field="components"` for SPICE and EMC findings. `components` is a list of refdes strings, but the three evaluator ops stringified the whole list (`str(['R5', 'C3'])` → `"['R5', 'C3']"`) and regex-searched that. Functional only by accident — would break silently if list repr changed.
- **Root cause:** `regression/checks.py` lines 214, 231, 248 did `str(_item_field(item, field))` unconditionally, losing the distinction between scalar and list fields.
- **Fix:** Added `_field_strings(field_val)` helper that returns a list of strings (single-element for scalars, `str()` of each element for lists). All three ops iterate this list and regex-match each string; for `count_matches` an item counts once if any element matches.
- **Verification:** `python3 tests/test_checks.py` → 54 pass, 0 fail (was 43 pre-TH-031; added 8 list-field integration tests + 3 `_field_strings` direct unit tests). Full unit suite: 903 pass, 0 fail (was 894). `python3 regression/run_checks.py --cross-section smoke` still reports 0 value mismatches on the re-seeded smoke corpus.
- **Commits:** 092146a0b15 (tests), d8f6b6ef880 (fix + `_field_strings` direct tests).

---

## 2026-04-16 — KH-311, KH-313 (Phase 5 harness-found bugs)

### KH-311 (MEDIUM): EMC `trust_summary.total_findings` doesn't match `len(findings)`

- **Where fixed:** kicad-happy repo, `skills/emc/scripts/analyze_emc.py` lines 510–522
- **Symptom:** 161 EMC outputs on smoke had `trust_summary.total_findings`
  higher than actual `len(findings)`. The diff was consistently 2.
- **Root cause:** `compute_trust_summary()` was called inside the result
  dict literal, **before** the `--compact` filter stripped INFO findings
  and before `apply_output_filters()` ran. So trust_summary reflected the
  pre-filter count while findings[] reflected the post-filter count.
- **Fix:** Removed `trust_summary` from the initial result dict literal.
  Re-added it as `result['trust_summary'] = compute_trust_summary(result['findings'])`
  after both filters run. Now reflects what's actually in the output.
- **Verification:** On Thinkpad-USB-keyboard schematic with `--compact`:
  `findings[]: 18`, `trust_summary.total_findings: 18`. Matching.
- **Commit:** a8f4d41

### KH-313 (MEDIUM): `check_inductor_leakage` crashes when RF chain component is a string

- **Where fixed:** kicad-happy repo, `skills/emc/scripts/emc_rules.py` lines 4004–4010
- **Symptom:** 2 EMC outputs on smoke crashed with `AttributeError: 'str'
  object has no attribute 'get'` inside `check_inductor_leakage`.
- **Root cause:** `emc_rules.py:4006` did `r = comp.get('ref') or comp.get('reference', '')`
  over `rf.get('components', [])`, but `components` can contain bare refdes strings,
  not just dicts. A similar loop at line 4000 already handled this with an
  `isinstance` check.
- **Fix:** Applied the same pattern at line 4006:
  ```python
  if isinstance(comp, str):
      r = comp
  else:
      r = comp.get('ref') or comp.get('reference', '')
  ```
- **Verification:** `py_compile` + smoke test pass. The 2 OLIMEX/DIY-LAPTOP
  EMC outputs that previously errored will now produce clean output on
  next harness run.
- **Commit:** a8f4d41

---

## 2026-04-15 — TH-032 (datasheet_verify import path)

### TH-032 (LOW): `test_datasheet_verify.py` imported from old `skills/kicad/scripts/` path

- **Where fixed:** harness repo, `tests/test_datasheet_verify.py` lines 14-15
- **Symptom:** `ModuleNotFoundError: No module named 'datasheet_verify'`.
- **Root cause:** Session 8 commit 6f321cd moved `datasheet_verify.py` from
  `skills/kicad/scripts/` to `skills/datasheets/scripts/`. Test still pointed
  at the old path.
- **Fix:** Added `skills/datasheets/scripts/` to sys.path for the import, kept
  `skills/kicad/scripts/` too because datasheet_verify imports `kicad_utils`
  from there.
- **Verification:** `python3 tests/test_datasheet_verify.py` → 27/27 pass.
- **Commit:** (this session)

---

## 2026-04-15 — KH-310 (format-report device reference key)

### KH-310 (LOW): `format-report.py` line 516 tries `reference` but devices use `ref`

- **Where fixed:** kicad-happy repo, `action/format-report.py` line 516
- **Symptom:** Buses & Protocols section rendered raw dicts instead of
  component references (e.g., `{'ref': 'U1', 'value': ...}` instead of `U1`).
- **Root cause:** `d.get('reference', str(d))` but protocol_compliance device
  dicts use `'ref'` not `'reference'`.
- **Fix:** Added `d.get('ref', ...)` fallback.
- **Verification:** `format-report.py` on macropad output renders `U1` cleanly.
- **Commit:** 28faedc

---

## 2026-04-15 — KH-308..309 (Batch 16 trust_summary bugs)

### KH-308 (MEDIUM): `compute_trust_summary` checks `_provenance` instead of `provenance`

- **Where fixed:** kicad-happy repo, `finding_schema.py` line 157
- **Symptom:** `provenance_coverage_pct` always 0.0% despite ~80% of schematic
  findings having provenance dicts from KH-263 Phase 1.
- **Root cause:** Typo — `f.get('_provenance')` instead of `f.get('provenance')`.
  The `**extra` kwargs in `make_finding()` store provenance without underscore prefix.
- **Fix:** Changed `'_provenance'` to `'provenance'`.
- **Verification:** After re-run, provenance_coverage_pct: median 62.1%, p75 81.8%
  (was 0.0% everywhere). Confirmed working.
- **Commit:** 0b1ad2d

### KH-309 (LOW): `detect_suggested_certifications` emits raw dicts without `make_finding()`

- **Where fixed:** kicad-happy repo, `domain_detectors.py:suggest_certifications()`
- **Symptom:** 100% of schematic outputs had `trust_level: "low"` because 74,076
  certification suggestion findings lacked `confidence` and `evidence_source` fields.
- **Root cause:** Only detector not using `make_finding()`. Raw dicts had no
  confidence/evidence_source, triggering `unknown_confidence > 0` → "low".
- **Fix:** Annotated all suggestion dicts with `detector='suggest_certifications'`,
  `rule_id='CERT-001'`, `confidence='heuristic'`, `evidence_source='topology'`.
- **Verification:** After re-run, unknown_confidence = 0 across all 36,314 outputs.
  Trust level distribution: high 30.4%, mixed 53.0%, low 16.6% (was 100% low).
- **Commit:** 0b1ad2d

---

## 2026-04-15 — KH-307 (incomplete Batch 14 evidence_source fix in thermal)

### KH-307 (MEDIUM): Thermal TS-*/TP-* findings emit invalid evidence_source

- **Where fixed:** kicad-happy repo, `analyze_thermal.py` lines 503–710
- **Symptom:** 5,451 thermal findings had `evidence_source` set to
  `"deterministic"` or `"heuristic"` — valid confidence values but not
  valid evidence_source enums. Caught by new `evidence_source` invariant
  in `validate_invariants.py`.
- **Root cause:** Batch 14 (c7eae6f) fixed the TH-DET assessment dict but
  missed 7 finding creation points: 4 in `_generate_findings()` copied the
  `confidence` variable into `evidence_source`, and 3 in TS-004/TP-001/TP-002
  hardcoded `"deterministic"` as the evidence_source string.
- **Fix:** TS-001/002/003/005: derive `ev_source` from
  `a["rtheta_ja_source"]` (same logic as line 437). TS-004/TP-001/TP-002:
  use `"geometry"` (these check PCB via presence and proximity distances).
- **Verification:** After fix + full corpus re-run (16,101 files):
  `evidence_source` values are `datasheet` (3,455), `geometry` (3,362),
  `heuristic_rule` (851). Zero invalid values. Invariant check passes.

---

## 2026-04-15 — TH-028..029 (release-readiness findings)

### TH-028 (HIGH): `validate/` import collision breaks smoke gate on stock environments

- **Where fixed:** Added `validate/__init__.py` (empty)
- **Symptom:** `python3 run_tests.py --smoke` failed with `ModuleNotFoundError` on
  4 tests (`test_datasheet_db_storage`, `test_datasheet_db_manifest`, `test_ab_test`,
  `test_manufacturer_match`) on machines with the system `validate` package installed.
- **Root cause:** The harness `validate/` directory had no `__init__.py`, so
  `import validate.*` resolved to the system `validate` package instead of the
  harness directory when the system package was installed.
- **Fix:** Added empty `validate/__init__.py` to make it a proper package.
- **Verification:** `run_tests.py --smoke` passes 489/489 tests, 0 failures.

### TH-029 (MEDIUM): RUNBOOK references nonexistent `validate/invariants.py`

- **Where fixed:** `RUNBOOK.md` lines 84 and 49
- **Symptom:** RUNBOOK Checklist 2 step 1c3 referenced `validate/invariants.py` which
  doesn't exist. Also described `quick_200` as "100-repo subset" when it's ~200 repos.
- **Root cause:** Stale command from before the script was renamed to
  `validate/validate_invariants.py`. Description copy-paste error.
- **Fix:** Changed `validate/invariants.py` → `validate/validate_invariants.py` and
  `100-repo subset` → `~200-repo subset` in RUNBOOK.md.
- **Verification:** File exists at the corrected path. Cross-sections.json confirms
  quick_200 has 255 repos.

### TH-030 (LOW): Data directories cause slow/noisy traversal for code-scanning tools

- **Where fixed:** `README.md` and `CLAUDE.md`
- **Symptom:** `python3 -m compileall .` takes 55 seconds traversing 464,000
  directories (99.99% data, 0 `.py` files). Discovered by an OpenAI Codex agent
  doing a standard Python syntax check on cold read.
- **Root cause:** The repo mixes ~130 code files across 7 directories with ~470,000
  data directories (`repos/` 290k, `reference/` 114k, `results/` 65k). Python tools
  don't read `.gitignore`, so they traverse everything. No documentation existed to
  warn about the code/data split.
- **Fix:** Added "Project layout" table to README.md separating code from data
  directories. Added "Code vs data" note to CLAUDE.md with explicit scoping example.
  Both include a bolded "never run recursive tools on `.`" warning.
- **Verification:** Scoped compileall (0.02s) vs naive (55s). Documentation clearly
  identifies which 7 dirs contain code vs which contain data.

---

## 2026-04-14 — KH-304..306 (issue #14 sub-sheet redirect edge cases)

### KH-304 (MEDIUM): Intermediate sub-sheets misclassified as root

- **Where fixed:** kicad-happy repo, `analyze_schematic.py:detect_sub_sheet()` Tier 2
- **Root cause:** Files with `(sheet ...)` blocks were always classified as root.
  Intermediate hierarchy nodes (sub-sheets that also have children) were misclassified.
- **Fix:** Tier 2 now checks whether the file is referenced by a sibling's sheet block.
  If so, it's an intermediate node, not the root.
- **Verification:** CDFER/Auckland-LED-Train-Map `NAL-NIMT-1.kicad_sch` — was 118
  components (partial), now matches root (249). 7/7 targeted tests pass.
- **Commit:** 699fa94

### KH-305 (MEDIUM): discover_root_schematic only searches same directory

- **Where fixed:** kicad-happy repo, `kicad_utils.py:discover_root_schematic()`
- **Root cause:** `os.listdir(parent_dir)` only searched the sub-sheet's directory.
  Sub-sheets in subdirectories (e.g. `sheets/video.kicad_sch`) couldn't find the
  `.kicad_pro` in the parent directory.
- **Fix:** Walks up parent directories (up to 5 levels) looking for `.kicad_pro`,
  then verifies sheet-tree membership.
- **Verification:** Board-Folk/NeoGeoAES-3.5 `sheets/video.kicad_sch` — was 35
  components (isolated), now matches root (365). 7/7 targeted tests pass.
- **Commit:** 699fa94

### KH-306 (LOW): First .kicad_pro wins in multi-project directories

- **Where fixed:** kicad-happy repo, `kicad_utils.py:discover_root_schematic()` and
  `analyze_schematic.py:detect_sub_sheet()` Tier 3
- **Root cause:** When multiple `.kicad_pro` files shared a directory, both functions
  used the first one from `os.listdir()` without checking sheet-tree membership.
- **Fix:** Scans each candidate `.kicad_pro`'s root schematic sheet tree to find
  which one actually references the target file.
- **Verification:** ghent360/PrntrBoardV2 `mcu.kicad_sch` — was redirecting to
  WiFi-Addon (wrong project, 33 components), now correctly redirects to
  PrntrBoardV2 (304 components). No stale warning. 7/7 targeted tests pass.
- **Commit:** 699fa94

---

## 2026-04-14 — TH-027 (assertion filenames exceed eCryptfs 143-byte limit)

### TH-027 (MEDIUM): Assertion filenames exceed eCryptfs 143-byte NAME_MAX

- **Where fixed:** `regression/seed.py`, `regression/seed_structural.py`,
  `regression/findings.py`, `regression/generate_bugfix_assertions.py`
- **Symptom:** `git pull` on eCryptfs-encrypted home fails with "File name too
  long" on 43 assertion files across 5 repos (flisboac/mixlib-tps7a26-kicad-block,
  arborium-dev/macroAll, JaytirthJOSHI/hackpad, DaAwesomeP/prox-sense,
  AmbassadorDoge/Solder-Start). Same root cause as TH-013.
- **Root cause:** TH-013 fixed `project_key()` and `project_prefix()` in `utils.py`
  to cap generated directory names at 143 bytes. But the **assertion filename
  construction** in 4 regression scripts appended suffixes (`_structural.json`,
  `_finding.json`, `_bugfix.json`) to already-long `file_pattern` strings without
  re-applying the length cap. The `file_pattern` includes the source filename
  (e.g. `pmic-vreg-ldo-tps7a2601-extcontrol_widevout.kicad_pcb`) which can be
  very long for deeply nested KiCad block libraries.
- **Fix:** Wrap the final filename (including `.json` extension) in
  `_truncate_with_hash()` before constructing the output path. Deleted 43
  overlong files and re-seeded the 5 affected repos.
- **Verification:** 0 overlong files remaining in reference/. 820 unit tests pass.
  18,823/18,826 assertions pass (same 3 pre-existing stale FND).

---

## 2026-04-14 — KH-295..303 (bc-breakout round-2: 6 new detectors + summary tool)

### KH-295 (LOW, enhancement): CP-001 over-noisy on GND-under-bypass-cap cases

- **Where fixed:** kicad-happy repo, `analyze_pcb.py:analyze_copper_presence`
- **Symptom:** ~35 of 38 CP-001 warnings on bc-breakout were decoupling caps sitting
  over the GND pour — the intended layout, not a clearance violation.
- **Fix:** CP-001 emits severity=info when every foreign zone under a component is
  ground-family AND the component has a GND pad. Total count unchanged (demote, not
  suppress).
- **Commit:** d58345a

### KH-296 (MEDIUM, enhancement): Sourcing gap invisible to severity rollups

- **Where fixed:** kicad-happy repo, new `analyze_schematic.audit_sourcing_gate`
- **Symptom:** 0/132 MPN coverage surfaced only as INFO in design-observations;
  `--stage pre_fab` filter didn't flag the pre-fab-blocking problem.
- **Fix:** New `audit_sourcing_gate` emits SS-001 (high, <50%), SS-002 (warning,
  50-80%), SS-003 (info, 80-100%) based on MPN coverage. All registered in `pre_fab`.
- **Commit:** 0668dae

### KH-297 (LOW, enhancement): Single-pin nets not weighted by pin type

- **Where fixed:** kicad-happy repo, `analyze_schematic.analyze_connectivity`
- **Symptom:** Single-pin nets were a plain list with no findings path. `__unnamed_*`
  blanket-suppressed — a power_in pin on `__unnamed_0` is a real wiring bug but was
  silently filtered.
- **Fix:** NT-001 finding with pin-type-weighted severity. Signal pins → warning;
  power_out/passive → info; no_connect/free/unspecified/unconnected → skip.
  `__unnamed_*` nets emit findings when warranted; legacy `single_pin_nets` list
  remains filtered.
- **Commit:** 1466598 (+ 5888aea followup)

### KH-298 (MEDIUM, enhancement): Rails lack a source-audit rule

- **Where fixed:** kicad-happy repo, new `signal_detectors.audit_rail_sources`
- **Symptom:** Power rails sourced through solder jumpers had no declared source.
  Reviewers manually traced e.g. +3.3V → JP23 (bridged) → REGIN_3V3 → MAX5035.
- **Fix:** RS-001 info (bridged jumper path), RS-001 warning (no path), RS-002 high
  (open jumper only). Traces one hop through solder jumpers using SJ-DET classifier.
  3-pin selector jumpers conservatively skipped.
- **Commit:** 3b5f194 (+ eefcac8 followup)

### KH-299 (LOW, enhancement): Net aliases not flagged

- **Where fixed:** kicad-happy repo, `analyze_schematic.build_net_map` + new
  `signal_detectors.detect_label_aliases`
- **Symptom:** Multiple global/hierarchical labels on the same net (e.g. SLS1 ↔ RS1P)
  went unnoticed — footgun on next edit.
- **Fix:** `build_net_map` records `labels: [{name, type}]` on every net. LB-001 info
  for ≥2 distinct global/hierarchical label names. Power nets excluded (Kelvin return
  pattern).
- **Commit:** f083d0f (+ 98bea8d followup)

### KH-300 (HIGH, enhancement): IC power pins can AC-couple to GND silently

- **Where fixed:** kicad-happy repo, new `signal_detectors.audit_power_pin_dc_paths`
- **Symptom:** A power_in pin reaching GND only through a capacitor is a silent wiring
  bug — ERC passes, but the IC supply floats DC.
- **Fix:** PP-001 high. BFS ≤2 hops: capacitor → REJECT; resistor ≤1Ω/inductor/ferrite
  bead/bridged jumper → bridge. Three suppression guards (ground start, connector-hosted,
  no-cap-seen). Known limitation: series protection diodes NOT treated as DC bridges
  (v1.3.1 follow-up). REGIN_x/REGOUT_x added to `is_power_net_name`.
- **Commit:** c80e967 (+ 38c331b followup)

### KH-301 (LOW, tooling): No cross-run finding summary

- **Where fixed:** kicad-happy repo, new `summarize_findings.py`
- **Symptom:** Reviewers manually walked `analysis/<run>/*.json` to tabulate findings.
- **Fix:** Reads current run via manifest.json, groups by (rule_id, severity), prints
  top-N table. Flags: `--top`, `--severity` (with aliases), `--run`, `--json` (schema
  version + totals). Stdlib-only, Python 3.8+.
- **Commit:** 772e774 (+ 8390275 followup)

### KH-302 (LOW, enhancement): Unnamed nets show as `__unnamed_N` in reports

- **Where fixed:** kicad-happy repo, `analyze_schematic.py` post-processing
- **Symptom:** ~30% of interesting nets (boot caps, LX nodes) are auto-named
  `__unnamed_N`, requiring pin-by-pin tracing.
- **Fix:** Annotates `nets[name].display_name = "Ref.PinName"` when an `__unnamed_N`
  net has exactly one named pin on an IC-type component. Does NOT rename the net key —
  additive field only.
- **Commit:** f7a83b4

### KH-303 (docs-only): SKILL.md misses new rule IDs and summary tool

- **Where fixed:** kicad-happy repo, `SKILL.md`
- **Fix:** Added rule-ID tables (SS/NT/RS/LB/PP), "Findings Summary" section for
  `summarize_findings.py`, CP-001 severity-split note.
- **Commit:** dec8593

---

## 2026-04-14 — KH-291..294 (solder-jumper detector, datasheet banner, thermal dedup)

### KH-291 (LOW, enhancement): Solder jumpers don't report default state

- **Where fixed:** kicad-happy repo, new `signal_detectors.detect_solder_jumpers` +
  `kicad_utils.classify_jumper_default_state`
- **Symptom:** Reviewers flagged "rail has no active source" on rails sourced through
  bridged-by-default solder jumpers. The analyzer had no way to surface that KiCad
  encodes jumper default state in symbol/footprint names.
- **Fix:** New `detect_solder_jumpers` detector (SJ-DET) emits one INFO finding per
  jumper with `default_state` in {bridged, open, switchable, unknown}, the two nets
  it straddles, and which are power/ground.
- **Verification:** 330 schematic outputs tested, 38 files with SJ-DET findings (126
  items). 0 state misclassifications. Schematic assertions: pass (see below).
- **Commit:** a92d61c

### KH-292 (MEDIUM, enhancement): Datasheet gap was silent

- **Where fixed:** kicad-happy repo, new `analyze_schematic.audit_datasheet_coverage`
- **Symptom:** Designs with no datasheets/ dir and no MPNs passed through analysis
  silently, and downstream reviewers wrote "verified per datasheet" language for parts
  with no datasheet evidence.
- **Fix:** New `audit_datasheet_coverage` emits DS-001 (HIGH, no datasheets AND no
  MPNs), DS-002 (MEDIUM, MPNs exist but no datasheets dir), DS-003 (INFO, partial
  coverage < 90%). Recommendation text tells reviewer to drop "verified" wording.
- **Verification:** 330 outputs tested: DS-001=114, DS-002=97, DS-003=37, none=82.
  All severities correct.
- **Commit:** a92d61c

### KH-293 (LOW): TP-DET and TV-001 reported contradictory via counts

- **Where fixed:** kicad-happy repo, `analyze_pcb.py:analyze_pcb()`
- **Symptom:** `analyze_thermal_vias` (TP-DET, proximity count) and
  `analyze_thermal_pad_vias` (TV-001, copper-verified) both emitted as findings,
  producing contradictory via counts on the same thermal pad.
- **Fix:** TP-DET entries no longer appended to `findings[]`; raw data preserved under
  `result.thermal_pad_scan`. TV-001 is the sole authoritative thermal-pad finding.
- **Verification:** 141 freshly-run PCB outputs: 0 with TP-DET, 92 with TV-001. PCB
  assertions: pass (see below).
- **Commit:** a92d61c

### KH-294 (LOW, docs-only): SKILL.md cheat sheet described non-existent subcircuits layout

- **Where fixed:** kicad-happy repo, `SKILL.md` field cheat sheet
- **Symptom:** Reviewers looked for `subcircuits.power_regulators` keyed-dict paths
  that never existed in v1.3 output.
- **Fix:** Cheat sheet now correctly describes `subcircuits[]` as IC-neighborhood
  grouping and points to `findings[]` + `get_findings(data, Det.*)` for detections.
- **Verification:** Docs-only change, no code impact.
- **Commit:** a92d61c

---

## 2026-04-14 — KH-287..290 (EMC NameError + analysis-cache coherence)

### KH-287 (HIGH): check_inductor_leakage crashes with undefined `signal` variable

- **Where fixed:** kicad-happy repo, `emc_rules.py:3946` (`check_inductor_leakage`)
- **Root cause:** ML-001 rule referenced `signal.get('adc_circuits',...)` but `signal`
  was never defined. The entire EMC analysis crashed with `NameError` on any project
  with switching regulators plus ADCs, opamps, crystals, or RF circuits.
- **Fix:** Replaced `signal.get(...)` calls with `get_findings(schematic, Det.*)` using
  the v1.3 rich-finding API (ADC_CIRCUITS, OPAMP_CIRCUITS, CRYSTAL_CIRCUITS, RF_CHAINS).
- **Verification:** 20 repos tested, 0 NameError crashes. EMC smoke (20 repos): all pass,
  `inductor_leakage` category now fires 5 findings. EMC assertions: 4,410/4,410 (100%).
- **Commit:** 442388c

### KH-288 (HIGH): Sequential analyzer runs create duplicate run folders

- **Where fixed:** kicad-happy repo, `analysis_cache.py` (`should_create_new_run`,
  `overwrite_current`, `create_run`)
- **Root cause:** `should_create_new_run` returned True when a new output type (pcb.json)
  appeared in a run that only had schematic.json, treating "new file" as "new run."
  Also `overwrite_current` wiped `source_hashes` wholesale (running pcb after schematic
  erased the schematic hash), and `create_run` copy-forward was all-or-nothing on hash
  mismatch (re-running schematic stripped pcb.json from the new folder).
- **Fix:** New output types extend the current run; `source_hashes` merge instead of
  replace; copy-forward is per-file keyed to source extensions via `_OUTPUT_SOURCE_EXT`.
- **Verification:** 26 projects tested, all produced exactly 1 run folder with both
  schematic.json and pcb.json. Schematic assertions: 9,125/9,125 (100%).
- **Commit:** 442388c

### KH-289 (MEDIUM): Derived-analysis outputs written to analysis/ root

- **Where fixed:** kicad-happy repo, `analyze_thermal.py`, `cross_analysis.py`,
  `analyze_gerbers.py` (all `main()` functions)
- **Root cause:** These analyzers wrote to `analysis/thermal.json`,
  `analysis/cross_analysis.json`, `analysis/gerbers.json` instead of
  `analysis/<run_id>/<name>.json`, leaving them orphaned from the manifest.
- **Fix:** Route through `overwrite_current` into the current run folder and register
  in the manifest. Added `cross_analysis` to `CANONICAL_OUTPUTS`.
- **Verification:** thermal.json confirmed in run folder (not root) on test project.
  Gerber smoke: 33/33 pass (100%). Gerber assertions: 199/199 (100%).
- **Commit:** 442388c

### KH-290 (MEDIUM): EMC creates recursive analysis/<run>/analysis/<run>/ nesting

- **Where fixed:** kicad-happy repo, `analyze_emc.py` (`main()`)
- **Root cause:** Passing a schematic JSON already inside the analysis tree (e.g.
  `analysis/2026-04-14_1807/schematic.json`) with `--analysis-dir analysis` caused EMC
  to anchor the output path on the schematic's parent, producing
  `analysis/<run>/analysis/<run>/emc.json`.
- **Fix:** Resolve `--analysis-dir` relative to CWD via `os.path.abspath`, matching
  the other analyzers.
- **Verification:** 13 repos tested, no nested `analysis` directories found. EMC
  assertions: 4,410/4,410 (100%).
- **Commit:** 442388c

---

## 2026-04-13 — KH-286 (analyze_fiducials value-is-list crash)

### KH-286 (LOW): analyze_fiducials crashes when footprint value is a list

- **Where fixed:** kicad-happy repo, `analyze_pcb.py:5205`
- **Root cause:** `fp.get("value", "")` returns a list on some PCB files (TI92-revive). String concatenation with `+` then raises TypeError.
- **Fix:** Added `if not isinstance(val, str): val = str(val)` guard.
- **Verification:** ccadic/TI92-revive both pass. Full PCB corpus: 18,652 pass / 3 fail (pre-existing).

---

## 2026-04-13 — TH-026 (multi-project directory discovery)

### TH-026 (LOW): discover_projects() collapsed multiple .kicad_pro in same directory

- **Where fixed:** `utils.py:discover_projects()` lines 339-362
- **Root cause:** `project_dirs` dict was keyed by directory path alone. When multiple
  `.kicad_pro` files share a directory (e.g., `KiCAD/PCB1_Mainboard.kicad_pro` and
  `KiCAD/Startlight-Baerenkeller.kicad_pro`), only the first was discovered. The
  snapshot/seed code then only processed one project, leaving assertion files for the
  other project(s) stale and never regenerated.
- **Impact:** 494 repos have multiple .kicad_pro in same directory. ~3,457 stale
  structural assertions across schematic/EMC/PCB.
- **Fix:** Changed `project_dirs` from `dict[str, str]` to `list[tuple[str, str]]`
  keyed by `(directory, stem)` so every `.kicad_pro` becomes its own project.
- **Verification:** Full re-snapshot + re-seed. 2,415,216 assertions at 100.0% pass
  rate. 820 unit tests, 0 failures. 1,466 new project baselines discovered.

---

## 2026-04-13 — KH-283, KH-284, KH-285 (None/type crashes from rich format migration)

### KH-285 (LOW): _min_power_pad_distance KeyError on pads without abs_x/abs_y

- **Where fixed:** kicad-happy repo, `analyze_pcb.py:1677`
- **Root cause:** `_min_power_pad_distance` accessed `ip["abs_x"]` directly. Some PCB files have pads parsed without absolute position fields, causing KeyError.
- **Impact:** 2 PCB analysis failures (circuit-synth ESP32_C6_Dev_Board, generated variant).
- **Fix:** Changed to `.get()` with None check and `continue`.
- **Verification:** Both files now pass.

### KH-284 (LOW): extract_pro_net_classes crashes when netclass_patterns is None

- **Where fixed:** kicad-happy repo, `kicad_utils.py:1450`
- **Root cause:** `.get('netclass_patterns', [])` returns `None` when key exists with value `None` in .kicad_pro JSON. Iterating over `None` raises TypeError.
- **Impact:** 2 PCB analysis failures (eugenio/zigbee_plant_sensor_solar_node quilter outputs).
- **Fix:** Changed to `ns.get('netclass_patterns') or []`.
- **Verification:** Both files now pass.

---

## 2026-04-13 — KH-283 (crystal guard ring freq None crash)

### KH-283 (MEDIUM): check_crystal_guard_ring crashes when crystal frequency is None

- **Where fixed:** kicad-happy repo, `emc_rules.py:1120`
- **Root cause:** Rich format migration changed crystal_circuits entries so `frequency` key can be `None` (not just absent). `xtal.get('frequency', 0)` returns `None` when the key exists with value `None`, causing `freq > 1e6` to raise TypeError.
- **Impact:** 97 EMC analysis failures across the corpus (every project with crystals lacking parsed frequency values).
- **Fix:** Changed `xtal.get('frequency', 0)` to `xtal.get('frequency') or 0`.
- **Verification:** Full EMC corpus rerun — 0 failures (was 97). All 97 `.err` files contained the same TypeError traceback.

---

## 2026-04-12 — Batch 53: KH-282 (ML-001 inductor shielding)

### KH-282 (LOW): classify_inductor_shielding hyphen/underscore mismatch

- **Where fixed:** kicad-happy repo, commit `4e84f6f`
- **Root cause:** `_SHIELDED_PATTERNS` in `kicad_utils.py` contained `WE-MAPI` (hyphen) but KiCad footprint libraries use underscores (`Inductor_WE_MAPI`). Pattern match failed for Wurth WE-series families.
- **Impact:** 3 false positives in quick_200 (ISSUIUC/ISS-PCB TARS-MK4-PMB L103, 3 board revisions).
- **Fix:** Normalized hyphens to underscores in shielding classifier.
- **Harness verification:** Pending (verify when Batch 1-3 handoffs arrive — EMC re-run will confirm 3 false positives resolved).

---

## 2026-04-12 — Batch 52: TH-021..TH-025 + B5/B7 (Phase 1 bug fixes)

### TH-021 (MED): harness.py _run() catches TimeoutExpired
- **Fix:** Wrapped `subprocess.run` in try/except `TimeoutExpired`. Returns False instead of crashing pipeline.

### TH-022 (MED): run_tests.py regex-based summary parsing
- **Fix:** Replaced fragile `split()` parsing with `re.search(r'(\d+)\s+passed,\s+(\d+)\s+failed')`. Warns on fallback. Test count jumped 302→326 because `test_diff_analysis.py` (25 tests) was previously counted as 1.

### TH-023 (MED): cleanup_drift.py matches on category not description substrings
- **Fix:** Rewrote to iterate items in same order as `validate_finding()`, matching on `(category, item_type)` pairs. Items with explicit check fields now correctly identified.

### TH-024 (LOW): cleanup_drift.py calls save_findings() for markdown regeneration
- **Fix:** Replaced raw `fpath.write_text()` with `save_findings()` which auto-regenerates findings.md.

### TH-025 (MED): run_pcb.py uses run_analyzer() standard CLI
- **Fix:** Removed manual argparse. Pre-parses `--full` flag, delegates to `run_analyzer()` which provides `--cross-section`, `--repo-list`, `--resume`, `--validate`, `--json`, and `DEFAULT_JOBS`.

### B5: seed_structural.py tolerant SPICE — documented as exact-only
- **Fix:** Removed dead `lo`/`hi` computation. Documented that `count_matches` op only supports exact equality.

### B7: add_repos.py --resume ternary fixed
- **Fix:** Non-resume branch now returns empty progress dict instead of loading saved progress.

---

## 2026-04-12 — Batch 51: TH-016..TH-020 (Phase 0 critical fixes)

### TH-016 (HIGH): validate_outputs.py + validate_invariants.py owner/repo path
- **Fix:** `split("/", 1)` → `split("/", 2)` to get `[owner, repo, within_repo]`. Both tools were finding 0 outputs.

### TH-017 (HIGH): validate_spice.py two-level directory iteration
- **Fix:** Replaced flat `iterdir()` with two-level `owner_dir/repo_dir` iteration matching `validate_emc.py` pattern.

### TH-018 (HIGH): generate_analytics.py glob depth + Path.rglob
- **Fix:** Replaced 4 `glob.glob` patterns with `Path.rglob`. Added `owner/` level. Fixed `parts[]` indexing. Was showing ~0.3% of data.

### TH-019 (MED): compare.py --all uses list_repos()
- **Fix:** One-line change from `d.name for d in DATA_DIR.iterdir()` to `list_repos()`.

### TH-020 (MED): promote.py regenerates all analyzer types
- **Fix:** Loop over `ANALYZER_TYPES` instead of hardcoding `"schematic"`.

---

## 2026-04-12 — Batch 50: Code quality fixes (KH-276, KH-278, KH-279, KH-280, KH-281)

### KH-276 (LOW): RC filter detected with cutoff_hz=0.0

- **Where fixed:** kicad-happy repo, commit `a243870`
- **Root cause:** `detect_rc_filters()` allowed zero-value R/C pairs into the detection pipeline.
- **Fix:** Added early `continue` when `r_val` or `c_val` is zero/None.

### KH-278 (MED): GP-001 silently returns empty when PCB data missing

- **Where fixed:** kicad-happy repo, commit `fc450e2`
- **Root cause:** `check_return_path_coverage()` returned empty findings when `return_path_continuity` data was absent.
- **Fix:** Emits INFO finding recommending `--full` flag when data is missing.

### KH-279 (MED): Formula divide-by-zero on zero/negative inputs

- **Where fixed:** kicad-happy repo, commit `12ecbac`
- **Root cause:** `dm_radiation_v_m`, `cm_radiation_v_m`, `harmonic_spectrum` had no guards on zero freq/distance.
- **Fix:** Early return 0.0/[] for unphysical inputs.

### KH-280 (MED): MPN sanitization cache key collisions

- **Where fixed:** kicad-happy repo, commit `998dfbd`
- **Root cause:** `_sanitize_mpn()` mapped `STM32F-103` and `STM32F/103` to identical keys.
- **Fix:** Appends 6-char MD5 hash suffix for uniqueness.

### KH-281 (MED): Cache copies forward stale outputs

- **Where fixed:** kicad-happy repo, commit `0b0e72e`
- **Root cause:** Copy-forward block didn't compare source hashes between runs.
- **Fix:** Skips copy when `source_hashes` differ between previous and current run.

### KH-277 — WON'T FIX

Mouser/element14 APIs require API key in URL query params. By design. Closed.

---

## 2026-04-12 — Batch 49: KH-230 empty Value substitution

### KH-230 (LOW): Empty placed Value silently substituted with lib_symbol default

- **Where fixed:** kicad-happy repo, commit `7eb2926`
- **Root cause:** `analyze_schematic.py:443-448` used `if not value:` to decide whether to fall back to the lib_symbol default. An explicitly empty `(property "Value" "")` is falsy, so the fallback triggered and replaced `""` with the lib_symbol's placeholder (e.g., `"R"`).
- **Fix:** Check `if value is None:` instead of `if not value:`. Only fall back when the property is entirely missing (Eagle imports), not when it exists but is empty.
- **Verified:** py_compile clean, synthetic test covers all 3 cases (value present, empty, missing). CLI smoke test passes.
- **Harness verification:** Affected: schematic analyzer. 1 corpus file: `hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`. Verify R1 instance with empty Value now has `value: ""` not `value: "R"`.

---

## 2026-04-12 — Batch 48: KH-236 Vref prefix-collision

### KH-236 (MED): Regulator Vref prefix-collision in _REGULATOR_VREF table

- **Where fixed:** kicad-happy repo, commits `a457129` (phase 1), `58459de` (phase 2)
- **Root cause:** Three failure modes: (1) LM78xx/LM79xx fixed-output parts not caught by suffix parser (no separator before voltage digits), falling through to `LM78 → 1.25V`. (2) Broad prefixes (TPS7A, TPS56, MP2, AP73, AP736) spanning sub-families with different Vref values. (3) Fixed-output-only families (LM78, LM79) in the table. 185 confirmed mismatches across 337 DigiKey-verified variants.
- **Fix (2 phases):**
  1. Extended suffix parser with `re.match(r'LM7[89][A-Z]?(\d{2})')` pattern for LM78xx/LM79xx fixed-output convention.
  2. Replaced 6 broad collision prefixes with ~40 per-sub-family entries. Removed LM78/LM79 (fixed-output only). Split TPS7A into 9 sub-families, TPS56 into 11, MP2 into 13, AP73/AP736 into 4 explicit adjustable entries. Added TPS54302/08=0.596V cross-reference from KH-237.
- **Phase 3 (vref_source annotation):** Already implemented — `signal_detectors.py` already tracks and emits `vref_source` (fixed_suffix/lookup/heuristic).
- **Verified:** 19/19 targeted assertions pass, py_compile clean, CLI smoke tests pass.
- **Harness verification:** Affected: schematic analyzer. Re-run `run_schematic.py` on quick_200. Expect `estimated_vout` changes on LM78xx (now fixed_suffix), TPS7A (split Vref), MP2/TPS56 (corrected Vref). BUGFIX assertion candidates: LM7805→fixed_suffix=5V (was lookup=1.25V), TPS7A4901→Vref=1.194V (was 1.19V), MP2338→Vref=0.5V (was 0.8V).

---

## 2026-04-12 — Batch 47: KH-237 switching frequency prefix-collision

### KH-237 (HIGH): Switching frequency prefix-collision + duplicated table

- **Where fixed:** kicad-happy repo, commits `356c363` (phase 1), `c4bf52b` (phase 2), `dedf767` (phase 3)
- **Root cause:** `_KNOWN_FREQS` table used 8 broad prefixes (TPS54, TPS62, etc.) that collided across distinct part families with different switching frequencies. 175 confirmed mismatches across 302 DigiKey-verified variants. Table was also duplicated between `signal_detectors.py` and `emc_rules.py` with divergent matchers (startswith vs substring).
- **Fix (3 phases):**
  1. Extracted `_KNOWN_FREQS` + `lookup_switching_freq()` to `kicad_utils.py` as single source of truth. Deleted EMC copy. Standardized all callers to `startswith`.
  2. Replaced 8 collision prefixes with 92 DigiKey-verified per-sub-family entries (105 total). Key corrections: TPS54302=400kHz (was 570kHz), TPS62203=1MHz (was 2.5MHz), TPS560430=1.1MHz (was 500kHz), LTC3601=2MHz (was 1MHz).
  3. Added `freq_source` annotation (`lookup_table`/`topology_default`) to regulator output.
- **Verified:** py_compile on all 3 files, 18/18 targeted assertions pass (collision fixes + regression), CLI smoke tests pass.
- **Harness verification:** Affected: schematic + EMC analyzers. Re-run `run_schematic.py` + `run_emc.py` on quick_200. Expect `switching_frequency_hz` changes on TPS54/62/61/56/63 regulators + corresponding SW-001 harmonic shifts. BUGFIX assertion candidates: TPS54302→400kHz, TPS62203→1MHz.

---

## 2026-04-12 — Batch 46: KH-240 + KH-233

### KH-240 (MED): Battery-negative rails not classified as ground

- **Where fixed:** kicad-happy repo, commit `23f62e3`
- **Root cause:** `kicad_utils.py:is_ground_name()` only recognized GND/VSS/COM/0V variants. Battery-negative rails (BATT-, BAT-, VBAT-) used as circuit ground in single-supply designs were classified as ordinary signals.
- **Fix:** Added narrow exact-match set for battery-negative patterns. Deliberately excludes V-/VEE (legitimate bipolar supplies).

### KH-233 (MED): SCHEMAS dict missing 22 detector entries

- **Where fixed:** kicad-happy repo, commit `d5a7f09`
- **Root cause:** `detection_schema.py:SCHEMAS` had entries for 19 detector types but the analyzer emits 40. 21 types had no schema entry. Also `snubber_circuits` key didn't match the analyzer's `snubbers` key.
- **Fix:** Added 21 DetectionSchema entries (identity-only, no derived fields). Renamed `snubber_circuits` → `snubbers`.

---

## 2026-04-12 — Batch 45: Trust restoration (KH-241 through KH-248)

8 core bugs fixed in kicad-happy main repo. All fixes verified via py_compile + --help smoke tests. Full analysis behind each issue is in `kicad-happy/TODO-combined-findings.md`.

### KH-241 (HIGH): EMC --compact flag overrides severity threshold

- **Where fixed:** kicad-happy repo, commit `2681e04`
- **Root cause:** `analyze_emc.py:357` had `severity = 'low' if args.compact else args.severity`, so `--compact` widened the severity filter instead of just hiding INFO findings.
- **Fix:** Keep `args.severity` authoritative for `run_all_checks()`. Strip INFO findings in post-processing only.

### KH-242 (HIGH): EMC suppressions don't filter derived metrics

- **Where fixed:** kicad-happy repo, commit `751b4fd`
- **Root cause:** `analyze_emc.py:419-426` fed full `findings` (including suppressed) into `compute_risk_score`, `generate_test_plan`, `compute_per_net_scores`, `analyze_regulatory_coverage`. Suppressed findings still dragged down score.
- **Fix:** `active_findings = [f for f in findings if not f.get('suppressed')]`, used for all derived metrics. Mirrors thermal analyzer pattern.

### KH-243 (HIGH): Schematic design-intent title_block handoff dead

- **Where fixed:** kicad-happy repo, commit `f91f89e`
- **Root cause:** `analyze_schematic.py:8339-8344` checked `if 'metadata' in result:` but result has no `metadata` key — title_block is at top level (`:8084`). Title-block IPC detection was dead code.
- **Fix:** `'title_block': result.get('title_block', {})`.

### KH-244 (HIGH): PCB design-intent misroutes metadata/net_classes/net_names

- **Where fixed:** kicad-happy repo, commit `dbccedf`
- **Root cause:** `analyze_pcb.py:5182-5188` had three wiring bugs: `result.get('metadata', {})` (should be `board_metadata`), net_classes pulled from DRC wrapper (should be top-level), net_names hardcoded to `{}`.
- **Fix:** Use `board_metadata`, direct `net_classes`, build `net_names` from `net_name_to_id`.

### KH-245 (MED): EMC/thermal config auto-discovery uses JSON-internal path

- **Where fixed:** kicad-happy repo, commit `23553d6`
- **Root cause:** `analyze_emc.py:379-383` and `analyze_thermal.py:804-820` discovered `.kicad-happy.json` from `schematic.get('file', '')` — a path stored inside the JSON. Fails when consuming cached JSON or JSON moved between machines.
- **Fix:** Prefer `os.path.dirname(os.path.abspath(args.schematic))`, fall back to JSON-internal path.

### KH-246 (LOW): summary.total_checks = len(findings) misleading

- **Where fixed:** kicad-happy repo, commit `67ac089`
- **Root cause:** `analyze_emc.py:451` and `analyze_thermal.py:879` both used `total_checks: len(findings)`. Clean board = `total_checks: 0` = "no analysis ran."
- **Fix:** Renamed to `total_findings`, added `categories_checked` (EMC) and `components_assessed` (thermal).

### KH-247 (HIGH): TH-001/PDN silently defaults MLCC package to 0603

- **Where fixed:** kicad-happy repo, commit `f92bea6`
- **Root cause:** `signal_detectors.py:1745-1749` didn't carry package from footprint into `output_capacitors[]`. `emc_rules.py:2974,3272` did `cap.get('package', '0603')` — fabricated input for package-sensitive derating.
- **Fix:** Extract package from footprint in detector. Skip package-dependent derating when package unknown.

### KH-248 (MED): SPICE drops generator-time failures silently

- **Where fixed:** kicad-happy repo, commit `58541c0`
- **Root cause:** `simulate_subcircuits.py:134-139` returned `(None, 0)` on generator exceptions. `_run_detection_batch:194-203` only emitted skip when `elapsed > 0`. Generator failures (elapsed=0) vanished from report.
- **Fix:** Return sentinel dict on generator failure, emit skip record with reason in batch handler.

---

## 2026-04-12 — Batch 44: TH-015 run_checks.py false PASS on errors

### TH-015 (MED): run_checks.py exits 0 when errors > 0, harness reports false PASS

- **Files**: `regression/run_checks.py` (exit code logic + new `--allow-errors` flag), `utils.py` (env var override for test isolation)
- **Root cause**: Two bugs. (1) `sys.exit(1 if failed > 0 else 0)` at line 300 only checked `failed`, ignoring `errors` — a run with thousands of missing-output errors and zero failures exited 0. (2) The `--json` code path at line 275 used `return` instead of falling through to the exit code, so JSON mode always exited 0 regardless of failures. `harness.py` trusted the exit code and reported `[PASS]`.
- **Fix**: Restructured `main()` so JSON and text output are `if/else` branches that both fall through to a unified exit code block. Exit nonzero when `failed > 0` OR `errors > 0` (unless `--allow-errors` flag set). Added `KICAD_HAPPY_TESTHARNESS_DATA_DIR` env var override to `utils.py` for test isolation.
- **Verified**: New `tests/test_run_checks.py` (5 tests) covers all exit code paths. Added to smoke gate (287 tests, 13 files, all pass).

---

## 2026-04-12 — Batch 43: KH-234/KH-235/KH-238/KH-239 (fixed in kicad-happy)

### KH-234 (MED): cross_verify thermal-via dict-key bug

- **Where fixed:** kicad-happy repo, commit `a37c1c0`
- **Root cause:** `cross_verify.py:566-569` (`check_thermal_vias`, not `check_thermal_via_adequacy` as originally filed) used wrong dict keys when accessing thermal pad via data, causing KeyError or silent misclassification.
- **Fix:** Corrected dict keys to `component`/`via_count` matching the actual `thermal_pad_vias` output schema.
- **Verified:** 3,489 `thermal_pad_vias` entries in quick_200 have 100% correct `component`/`via_count` keys post-fix. Corpus too sparse for direct flagged-count delta (only 7 populated `thermal_assessments` corpus-wide).

### KH-235 (MED): extract_pro_net_classes TypeError on list-valued assignments

- **Where fixed:** kicad-happy repo, commit `6dd0ab0`
- **Root cause:** `kicad_utils.py:1207-1209` (`extract_pro_net_classes`) iterated net-class assignment values assuming strings, but KiCad 8 `.kicad_pro` files can have list values like `"NET_NAME": ["NET_NAME"]`. Crashed `analyze_pcb.py` before `analyze_thermal_pad_vias` ran.
- **Fix:** Single-site fix (~8 LOC) wrapping the assignments-loop value access. Pre-fix audit confirmed 139 corpus files affected (~1.1% of 12,551 `.kicad_pro` files), patterns-loop at line 1200-1204 had 0 corpus hits (no symmetric bug).
- **Verified:** Both confirmed target crashers (Mitayi-Pico-D1, bluerobotics/ping-dev-kit) no longer crash. Audit scripts at `inspections/2026-04-11_kh235_audit/` (local).

### KH-238 (HIGH): feedback divider pair-ordering bug

- **Where fixed:** kicad-happy repo, commit `9c8ec19`
- **Root cause:** `signal_detectors.py:274-280` had a pair-ordering bug in feedback divider detection, causing missed or misidentified divider pairs.
- **Fix:** Corrected pair ordering logic.
- **Verified:** 342/342 in-scope records fixed (100.0%). The remaining 814 records in the original 1,156-assertion YAML were false positives from the inspection: 797 hierarchical-sheet misses (resistors on different sheet than regulator, now KH-259) + 17 op-amp false positives (ADA4817, HX711, now KH-260).

### KH-239 (MED): LED current-limit resistors double-classified as pull_up

- **Where fixed:** kicad-happy repo, commit `a39a7d1`
- **Root cause:** `analyze_schematic.py` `analyze_sleep_current` classified LED current-limit resistors as pull-up resistors, double-counting them in sleep current analysis.
- **Fix:** Added exclusion for LED series resistors in the pull-up classification path.
- **Verified:** 4,122/4,123 fixed (100.0%). The 1 straggler is a stale pre-TH-013 output file (safe_name truncation left orphaned old-name copy on disk), not a regression.

---

## 2026-04-10 — Batch 42: KH-231/KH-232 dormant analyzer bugs (fixed in kicad-happy)

### KH-231 (HIGH): opamp_circuits non_inverting recalc used inverting formula

- **Where fixed:** kicad-happy repo, commit `beaddb8` (not this repo)
- **Root cause:** branch ordering in `detection_schema.py::_recalc_opamp_gain` checked `inverting` before `non_inverting`, which matched both configurations and applied `-Rf/Ri` to non-inverting parts. The `_inverse_opamp_gain` solver had the correct ordering, which is why the inverse tests still computed sensible intermediate values (they just disagreed with the broken forward pass).
- **Fix:** reversed the branch order so `non_inverting` is checked first, mirroring `_inverse_opamp_gain`.
- **Impact before fix:** every opamp_circuits detection in 36,541 schematic outputs had `gain = -Rf/Ri` regardless of configuration. Silent wrong value across the entire corpus.
- **Verified on harness side:** after pulling kicad-happy to `beaddb8` and re-running `python3 tests/test_detection_schema.py`, three tests flipped XFAIL → XPASS:
  - `test_recalc_opamp_non_inverting`
  - `test_inverse_opamp_gain`
  - `test_inverse_opamp_gain_dB`
  Runner explicitly printed "remove from KNOWN_FAILURES, KH-231 may be fixed" for each.
- **Harness cleanup (this commit):** removed the three entries from `KNOWN_FAILURES` in `tests/test_detection_schema.py`. Test file now declares 25 passing tests + 1 xfailed (KH-233 only).

### KH-232 (MED): lc_filters had no inverse solver for resonant_hz

- **Where fixed:** kicad-happy repo, commit `beaddb8` (same commit as KH-231)
- **Root cause:** the `_inverse_lc_resonant` solver function existed but was never wired into the `lc_filters` schema's `DerivedField("resonant_hz", ...)` constructor. `get_inverse_solver("lc_filters", "resonant_hz")` returned None.
- **Fix:** added `_inverse_lc_resonant` as the third argument to the DerivedField constructor. One-line wiring fix.
- **Side effect noted by kicad-happy agent:** `get_inverse_solver("lc_filters", "impedance_ohms")` now falls through to `_inverse_lc_resonant` via the second-pass loop in `get_inverse_solver`. Harness grep confirmed no test asserts None for that lookup — safe.
- **Verified on harness side:** `test_inverse_lc_resonant` flipped XFAIL → XPASS.
- **Harness cleanup (this commit):** removed the entry from `KNOWN_FAILURES`.

---

## 2026-04-10 — Batch 41: TH-014 missing __main__ runner blocks

### TH-014 (MED): Two test files silently passing — 36 tests never executed

- **Files**: `tests/test_batch_review.py` (added TIER + runner block, +21 LOC), `tests/test_detection_schema.py` (added KNOWN_FAILURES set + XFAIL-aware runner block, +44 LOC).
- **Root cause**: Both files defined `def test_*` functions but lacked the standard `if __name__ == "__main__":` runner block at the bottom. When `run_tests.py` invoked them via `subprocess.run([python, file])` they imported cleanly and exited 0 with no output. The runner's empty-output fallback at `run_tests.py:188-195` then assigned `p=1, status="ok"` and reported PASS — masking 36 dead tests across the two files.
- **Fix**: Appended the standard stdlib runner block to both files (pattern lifted from `tests/test_verify_parser.py:394-410`). For `test_detection_schema.py`, the runner additionally honors a `KNOWN_FAILURES` dict mapping test names to KH-* IDs — those tests report as `XFAIL` with the issue ID and don't break the suite, while still appearing in every run as a visible TODO. When a known-failing test starts passing, the runner prints `XPASS (remove from KNOWN_FAILURES, ... may be fixed)` to nudge cleanup.
- **Dormant bugs surfaced** (filed as new KH issues, all currently `XFAIL`):
  - **KH-231 (HIGH)** — `opamp_circuits` non-inverting recalc returns `-Rf/Ri` (the inverting formula) regardless of `configuration` field. Affects 3 tests.
  - **KH-232 (MED)** — `lc_filters` schema has no inverse solver registered for `resonant_hz`. Affects 1 test.
  - **KH-233 (MED)** — `SCHEMAS` dict missing 22 detector entries (coverage gap; downstream code that walks SCHEMAS silently skips them). Affects 1 test.
- **Verified**: `python3 tests/test_batch_review.py` reports `6 passed, 0 failed (6 total)` (was: silent exit). `python3 tests/test_detection_schema.py` reports `25 passed, 0 failed, 5 xfailed (30 total)` exit 0 (was: silent exit). Full unit suite: `480 passed, 0 failed, 3 skipped, 24 files (24 ok)` — net +29 visible passes vs pre-fix (was 451). Smoke gate (`run_tests.py --smoke`) unchanged: `218 passed, 0 failed, 10 files`.

---

## 2026-04-10 — Batch 40: TH-013 filesystem name length fix

### TH-013 (HIGH): Flattened project/file names exceed NAME_MAX on eCryptfs and ext4

- **Files**: `utils.py` (new `project_key`, `_truncate_with_hash` helpers; added `NAME_MAX_BYTES=143`, `_NAME_HASH_LEN=10`; updated `project_prefix`, `safe_name`, `discover_projects`), `regression/findings.py` (4 inline sites), `regression/generate_bugfix_assertions.py`, `regression/audit_bugfix_paths.py` (3 sites), `validate/validate_invariants.py`, `validate/validate_outputs.py`, `tools/figure_review.py`, plus new `tools/migrate_th013_rename.py` and 9,055+ rename operations across `reference/`.
- **Root cause**: `utils.py:296-302` (`discover_projects`) flattened project paths with `_` and appended the `.kicad_pro` stem without any length awareness. Two compounding problems: (1) KiCad convention of `foo/foo.kicad_pro` produced `..._foo_foo` duplicated names on ~30% of project directories (4,989 of 16,766); (2) no filesystem limit enforcement meant deeply nested or Cyrillic project dirs blew past 143-byte eCryptfs and 255-byte ext4 NAME_MAX. Worst offender: 570-byte Cyrillic directories in `reference/Exaster/4Labs/`. Additionally, 15 inline `replace("/", "_")` sites across 7 files duplicated the same logic without centralized length capping.
- **Fix**: Centralized flattening into `project_key(pdir, stem)` and `_truncate_with_hash(name, budget)` helpers in `utils.py`. Added stem deduplication (when `Path(pdir).name == stem`) and 143-byte cap with SHA1[:10] suffix fallback. Replaced all 15 inline call sites with helper calls. Updated `discover_projects()` to use `project_key()` and store a `stem` field on returned project dicts. Added symmetric collision resolution (mirroring the helper in utils.discover_projects for conflict handling). One-shot migration script `tools/migrate_th013_rename.py` used `git mv` to rename affected directories while preserving history — featuring: (a) walker that skips `assertions`/`baselines` at repo level for old-layout data, (b) reverse-engineering fallback for metadata-less orphans, (c) best-effort orphan rename via trailing-duplicate detection, (d) empty-shell orphan deletion pass (122 dirs), (e) file-level basename rename pass (42 files with >143-byte names inside correctly-renamed project dirs).
- **Verified**: New `tests/test_safe_names.py` (22 tests) all pass. Full unit suite: 424 tests green. Post-migration byte-length scan: 0 components >143 bytes, 0 components >255 bytes (256,221 tracked files). Smoke cross-section: 26,137/26,138 (1 pre-existing orphan error). Quick_200: 584,730/584,732 (2 pre-existing orphan errors). Local clean-clone: succeeded, 256,220 files checked out on ext4. Cyrillic Exaster case: 570-byte dirs → exactly 143 bytes. AmbassadorDoge/Solder-Start stem-dedup: 130 bytes → 93 bytes. Metadata `project` field updated on 9,044 files to match new enclosing directory.

---

## 2026-04-10 — Batch 39: KH-229 USB compliance crash fix

### KH-229 (HIGH): USB compliance vbus_capacitance crashes analyzer

- **File**: `analyze_schematic.py` — `analyze_usb_compliance()`, lines 7251-7262
- **Root cause**: `vbus_capacitance` check stored a dict `{"status": "warning", "total_uf": ...}` in `conn_checks["checks"]` where all other checks store plain strings. Summary loop at line 7289 used the value as a dict key, crashing with `TypeError: unhashable type: 'dict'`.
- **Fix**: `checks["vbus_capacitance"]` now stores "warning" or "pass" string. Detail data moved to separate `vbus_capacitance_detail` field.
- **Verified**: Dylanfg123/Zebra-X (repro case) no longer crashes. Output has `vbus_capacitance: "pass"` (string) and `vbus_capacitance_detail: {"total_uf": 4.7}` (dict). Regression test added.

---

## 2026-04-09 — Batch 38: TH-012 structural seed stale cleanup

### TH-012 (MEDIUM): seed_structural.py leaves stale assertions when detections drop to zero

- **File**: `regression/seed_structural.py` — `generate_for_repo()`
- **Root cause**: The threshold skip conditions (`total_checks < 1`, `comps < min_components`, etc.) used `continue` to skip below-threshold outputs, bypassing the stale-file cleanup code at line 429. When an analyzer change removed detections, the old structural assertion file persisted expecting the now-gone detections.
- **Fix**: Refactored threshold checking to set a `below_threshold` flag instead of `continue`-ing. Below-threshold outputs now fall through to the cleanup code which deletes stale assertion files generated by `seed_structural.py`. Normal assertion generation is skipped via the `if not below_threshold:` guard.
- **Verified**: Synthetic test — created stale structural assertion for EMC output with 0 findings, ran `seed_structural.py`, confirmed file deleted. Full corpus: EMC 517,083 passed 0 failed, schematic 680,727 passed 5 aspirational.

---

## 2026-04-09 — KH-205 closed (unreproducible)

### KH-205 (MEDIUM): D+ net lost in KiCad 5 legacy net resolution

- **Status**: Closed as unreproducible.
- **Investigation**: Original repro file (`Mouse/Mouse.sch` in `prashantbhandary/Meshmerize-MicroMouse-`) no longer exists (repo converted to `.kicad_sch`). Searched corpus for other KiCad 5 `.sch` files with `D+` nets. Found `martinribelotta/pic32mz-board/mz.sch` and `asmr-systems/development-boards/samd21g17d/samd21g17d.sch` — both show `D+` net with 0 pins, but investigation revealed: (1) pic32mz labels are genuinely floating (no wire endpoints at label coordinates), (2) samd21 has broader GLabel connectivity issues (PAxx nets also 0 pins) due to legacy coordinate-based matching limitations, not D+-specific. The `+` character is not the cause. No fix needed — behavior is correct for these inputs.

---

## 2026-04-09 — Batch 37: Fix 10 analyzer bugs (KH-218..KH-227)

### KH-218 (HIGH): Vref heuristic wrong for TPS62912, TPS73601, LM22676

- **File**: `kicad_utils.py` — `_REGULATOR_VREF` lookup table
- **Root cause**: Table missing 3 common regulator families. Fell back to 0.6V heuristic.
- **Fix**: Added TPS62912=0.8V, TPS736xx=1.204V, LM22676=1.285V.
- **Verified**: Vout estimates now correct. 1,347 schematic + 530 EMC assertions reseeded. 0 regressions.

### KH-219 (MEDIUM): Load switches classified as LDO topology

- **File**: `signal_detectors.py` — regulator topology detection
- **Fix**: TPS229/TPS205 added to load switch exclusion + description keywords.

### KH-220 (MEDIUM): Active oscillators with custom libs misclassified as connector

- **File**: `kicad_utils.py` — `classify_component()` now takes description param
- **Fix**: Checks description for oscillator keywords. Both call sites in analyze_schematic.py updated.

### KH-221 (MEDIUM): Opamp TIA feedback classified as "compensator"

- **File**: `signal_detectors.py` — opamp topology classification
- **Fix**: feedback_R >> input_R (ratio > 10:1) → "transimpedance" instead of "compensator".

### KH-222 (MEDIUM): Multi-unit symbol duplication in led_audit, sleep_current, usb_compliance

- **File**: `analyze_schematic.py`, `domain_detectors.py`
- **Fix**: Deduplication by reference designator in led_audit, sleep_current_audit, usb_compliance.

### KH-223 (MEDIUM): Power sequencing cascade not resolved into power_tree ordering

- **File**: `domain_detectors.py` — power sequencing
- **Fix**: Pin name matching fixed for `~{EN}`/`~{PG}` overbar markup.

### KH-224 (LOW): Multi-unit IC power_domains only shows one unit's rails

- **File**: `domain_detectors.py` — power domain extraction
- **Fix**: Aggregated across all units of multi-unit ICs.

### KH-225 (LOW): LM2664 charge pump classified as LDO topology

- **File**: `signal_detectors.py`
- **Fix**: `charge_pump` topology for LM2664/MAX660/ICL7660 families.

### KH-226 (LOW): NUCLEO dev board module classified as switching regulator

- **File**: `signal_detectors.py`
- **Fix**: Dev board modules (NUCLEO/Arduino/Raspberry) excluded from regulator detection.

### KH-227 (LOW): Logic gates misclassified as level_shifter_ic

- **File**: `domain_detectors.py`
- **Fix**: 74-series logic gates excluded from level shifter detection.

---

## 2026-04-09 — Batch 36: KH-228 detect_sub_sheet fix

### KH-228 (LOW): detect_sub_sheet only identifies 34% of sub-sheets

- **File**: `analyze_schematic.py` — `detect_sub_sheet()`
- **Root cause**: Detection relied solely on `hierarchical_label` presence. Many valid sub-sheets lack this marker.
- **Fix**: Added `file_path` parameter. New tiered strategy: (1) symbol_instances → root, (2) sheet blocks → root, (3) .kicad_pro stem matching → root if match, sub-sheet if no match, (4) hierarchical_label fallback → sub-sheet, (5) conservative default → root.
- **Verified**: Detection rate 34% → 99% (66/67 sub-sheets). 0 false positives on 28 root schematics. 10 unit tests covering all 5 tiers. 681,209 schematic assertions pass (16 reseeded from minor design_observations count changes).

---

## 2026-04-09 — Batch 35: Test harness fixes (TH-009, TH-010)

### TH-009 (MEDIUM): Constants audit missing Vref heuristic coverage check

- **File**: `validate/audit_constants.py` — `cmd_corpus()`
- **Root cause**: The corpus scan only counted `vref_source == "lookup"` hits. Regulators falling back to the 0.6V heuristic (`vref_source == "heuristic"`) were silently ignored, so missing Vref table entries never surfaced.
- **Fix**: Added `vref_heuristic` accumulator to the existing regulator scan loop. After the Vref summary, reports total heuristic-fallback count, unique parts, and top candidates (5+ hits) for table inclusion.
- **Verified**: `audit_constants.py corpus` reports 1,277 heuristic regulators across 369 parts, with 65 parts having 5+ hits. Top: TLV62569DBV (44x), TLV62569DRL (41x), TPS62A02 (31x).

### TH-010 (LOW): Legacy findings cleanup

- **File**: `tools/migrate_findings.py` (new one-time script)
- **Root cause**: Early findings (pre-March 2026) were created before the standardized FND-* ID system and analyzer_type conventions. 89 findings had no ID, 30 had non-standard or missing types.
- **Fix**: Migration script assigns FND-* IDs via `next_id()` (FND-00002540 through FND-00002628), normalizes `analyze_schematic` → `schematic` etc., defaults missing types to `schematic`, re-renders all 45 affected findings.md files.
- **Verified**: All 2,596 findings have IDs (0 missing). `batch_review.py status` shows only standard types (schematic: 1656, pcb: 619, gerber: 298). 277 tests pass.

---

## 2026-04-09 — Batch 34: Layer 3 workflow improvements (TH-011)

### TH-011 (LOW): batch_review.py multi-project output alignment

- **File**: `tools/batch_review.py` — `_collect_outputs()`, `_output_project_prefix()`
- **Root cause**: For multi-project repos (37% of corpus, 2,186 repos), `_collect_outputs()` independently picked the highest-scoring file per output type. The best schematic and best PCB could come from different projects, making cross-referencing meaningless.
- **Fix**: Added `_output_project_prefix()` to extract a shared project name from output filenames (stripping `.kicad_sch`, `.kicad_pcb`, `_gerber` suffixes). `_collect_outputs()` now iterates schematic candidates and finds matching PCB/gerber with the same prefix, scoring by type coverage + complexity to select the best project set.
- **Verified**: Project_OAK now picks V0 PCB to match V0 schematic (previously picked V0.1 PCB). Zebra-X, lora-payload, meteo_mini all correctly align sch+pcb prefixes. Single-project repos unaffected.

---

## 2026-04-09 — Batch 33: Layer 3 batch review bugs (KH-207..KH-217)

### KH-207 (HIGH): Legacy 2x2 matrix decomposition produces wrong pin positions

- **File**: `analyze_schematic.py` — `compute_pin_positions()`, legacy matrix parser
- **Root cause**: Legacy parser decomposed 2x2 orientation matrix into angle+mirror flags incorrectly. Matrix `(0,1,-1,0)` produced pin offset `(-5,10)` instead of correct `(5,-10)`. `mirror_y` was never set for legacy components.
- **Fix**: Store raw 2x2 matrix as `transform_matrix` on component. `compute_pin_positions()` uses it directly (`rpx = a*px + b*py`) when present, falling back to angle/mirror path for KiCad 6+.
- **Verified**: All 6 matrix combinations (identity, 90/180/270, mirror X/Y) produce correct pin offsets.

### KH-208 (HIGH): Component type classification ignores lib_id, over-relies on ref prefix

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: `type_map.get(prefix)` returns immediately for standard prefixes (T→transformer, C→capacitor), never reaching lib_id fallback. T1 with `Sensor_Temperature:DS18B20` got "transformer".
- **Fix**: Added early lib_id override block inside type_map result path for unambiguous library categories: `Connector:*`→connector, `Sensor_Temperature:*`→ic, `Motor:*`→motor, `*CircuitBreaker*`→switch.
- **Verified**: T1/DS18B20→ic, CB1/CircuitBreaker→switch, LED1_W/Connector→connector, R1/Device:R→resistor (unchanged).

### KH-209 (MEDIUM): Power rails with nnVn naming pattern classified as signal

- **File**: `kicad_utils.py` — `is_power_net_name()`
- **Root cause**: Only matched V-first format (V3V3, V5V0). Industry-standard digit-first format (3V3, 5V0, 12V0) unmatched.
- **Fix**: Added 4 patterns: `^\d+V\d` (nnVn), `^NEG\d+V` (negative rails), `^V[CD][CD]\d` (VDDn/VCCn), and `^\d+V` with underscore (nV_xxx).
- **Verified**: All 10 reported nets (12V0, 3V3, 5V0, 1V5, 1V8, VDD5, VDD12, NEG6V, 5V_INT) now classify as power.

### KH-210 (MEDIUM): SPI chip select detection too narrow

- **File**: `analyze_schematic.py` — SPI CS detection
- **Root cause**: Only matched 5 keywords: CS, SS, NSS, SPI_CS, SPI_SS.
- **Fix**: Added CSN, NCS, SSEL, CSEL to keyword list.
- **Verified**: Compile-check passes.

### KH-211 (MEDIUM): Incomplete pin_nets for components on unnamed nets

- **File**: `analyze_schematic.py` — pin_nets serialization (both legacy and KiCad 6+ paths)
- **Root cause**: Original diagnosis (chain tracer can't cross hierarchy) was wrong. The chain tracer uses `ctx.ref_pins` which includes all nets and works correctly. The real issue: `pin_nets` serialization filtered `__unnamed_*` nets, hiding connections made through unlabelled wires (common in hierarchical sub-sheets). This made the JSON output appear disconnected.
- **Fix**: Removed `__unnamed_*` skip filter from both pin_nets population loops. All nets now included.
- **Verified**: yuiop60hh LED2 now shows all 4 pins (was missing 2). Chain detection unchanged. Tested on 4 multi-sheet LED projects — identical chain results.

### KH-212 (MEDIUM): Bare capacitor values < 1.0 parsed as Farads

- **File**: `kicad_utils.py` — `parse_value()`, `analyze_schematic.py` — callers
- **Root cause**: Two-part: (1) KH-153 pF fix only applied for values ≥1.0, values <1.0 fell through as Farads. (2) Callers at lines 6278 and 7595 didn't pass `component_type`.
- **Fix**: (1) Added `else: result *= 1e-6` branch for values <1.0 when component_type="capacitor". (2) Fixed both callers to pass component_type.
- **Verified**: `parse_value("0.1", "capacitor")` → 1e-7, `parse_value("0.47", "capacitor")` → 4.7e-7, `parse_value("100", "capacitor")` → 1e-10, `parse_value("0.1", None)` → 0.1.

### KH-213 (LOW): P-MOSFET detection misses PMOS/P-MOS/P-MOSFET keyword variants

- **File**: `signal_detectors.py` — P-channel detection in FET analysis
- **Root cause**: Keywords check matched `p-channel`/`pchannel` but real KiCad keywords use `PMOS`/`P-MOS`/`P-MOSFET`. Description field never checked.
- **Fix**: Added `pmos`, `p-mos`, `p-mosfet` to keywords check. Added description field fallback.
- **Verified**: IRF9310 keywords `"transistor PMOS P-MOS P-MOSFET"` now match.

### KH-214 (LOW): INA2xx power monitors misclassified as opamp circuits

- **File**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: `ina2` in `opamp_value_keywords` matched INA233/INA226 power monitors.
- **Fix**: Removed `ina2`/`ina8` from keywords (INA128/103/114 still caught by `ina10`-`ina13`). Added post-gate exclusion for INA2xx/INA8xx/INA90x.
- **Verified**: INA instrumentation amps still detected; INA233/INA226 excluded.

### KH-215 (LOW): LM2576/LM2596 switching bucks classified as LDO

- **File**: `signal_detectors.py` — regulator topology detection
- **Root cause**: LM2576 pin "OUT" matches `vout_pin` not `sw_pin`. Keyword fallback catches "switching" from standard lib_id but not custom libraries.
- **Fix**: Extracted `known_freqs` to module-level `_KNOWN_FREQS`. Added `_match_known_switching()` check before LDO default.
- **Verified**: LM2576/LM2596 → topology="switching". LM317 → still "LDO".

### KH-216 (LOW): Multi-unit IC pin_nets shows wrong unit's pins

- **File**: `analyze_schematic.py` — pin_nets assignment (both legacy and KiCad 6+ paths)
- **Root cause**: pin_nets built by reference only; multi-unit components sharing a reference got all units' pins merged.
- **Fix**: Store `_unit_pins` set from `compute_pin_positions()` on each component. Filter pin_nets to only include unit-valid pins. Clean up transient field after.
- **Verified**: Compile-check passes. Each unit now gets only its own pins + shared (unit 0) power pins.

### KH-217 (LOW): Crystal frequency parsing case-sensitive

- **File**: `signal_detectors.py` — `_parse_crystal_frequency()`
- **Root cause**: Regex used literal `z` not `[Zz]`, so `kHZ`/`MHZ` failed.
- **Fix**: Changed `z` to `[Zz]` in both MHz and kHz regex patterns.
- **Verified**: `32.768kHZ`, `25MHZ`, `8mhz` all parse correctly.

---

## 2026-04-08 — Batch 32: v1.2 pre-release bugs (KH-204, KH-206)

### KH-204 (MEDIUM): power_rails uses UUID sheet paths instead of human-readable names

- **File**: `skills/kicad/scripts/analyze_schematic.py`
- **Root cause**: `compute_statistics()` iterated `nets` keys which include hierarchical UUID path prefixes (e.g., `/201ab4ae-.../VIN`) and added them to `power_rails` without cleaning.
- **Fix**: Added `_clean_hierarchical_name()` helper using UUID regex to strip path prefixes. Applied to both the net-name-based rail discovery and the final power_rails list builder.
- **Verified**: VoltageSwitchboard repro now produces `['VIN', 'VOUT', 'V+', '+3V3', 'GND']` — no UUID paths.

### KH-206 (MEDIUM): Global labels with different names merged into one net

- **File**: `skills/kicad/scripts/analyze_schematic.py`
- **Root cause**: `build_net_map()` had a post-processing pass (lines 1100-1108) that called `union_with_overlapping_wires()` for ALL component pins. This falsely connected pins that sat geometrically on a wire segment (same Y, X between endpoints) without a junction. In the haxophone001 design, R2 pin 2 at (104.14, 62.23) sat on the SDA horizontal wire (96.52→110.49, y=62.23) even though R2 only connects via a vertical wire to the SCL bus. KiCad requires a junction or wire endpoint for connection; geometric overlap alone is not sufficient.
- **Fix**: Removed the mid-wire pin union pass entirely. Component pins already connect via wire endpoints through the `add_point` coordinate matching. The mid-wire union was only needed for labels, power symbols, junctions, and no-connects — all of which already have their own `union_with_overlapping_wires` calls.
- **Verified**: haxophone001 repro now produces separate SDA (3 pins) and SCL (3 pins) nets.

---

## 2026-04-08 — KH-205 resolved (already fixed)

### KH-205 (MEDIUM): D+ net lost in KiCad 5 legacy net resolution

- **File**: `skills/kicad/scripts/analyze_schematic.py`
- **Root cause**: D+ net was not being resolved in legacy .sch parsing, possibly due to
  the `+` character in the net name.
- **Fix**: Already fixed by a prior commit (likely hierarchical context or net resolution
  improvements). D+ now appears correctly in nets dict with pins R17, C13, C9, R8.
  The differential pair detector now correctly identifies {D+, D-} as a USB pair.
- **Verified**: Re-ran analyzer on `RandomDelta6/USB-Mouse/Mouse.sch`. D+ in nets: True.
  `design_analysis.differential_pairs` contains `{type: differential, positive: D+, negative: D-}`.
  Finding assertion updated from `equals []` to `min_count 1`.

---

## 2026-04-08 — Batch 31: power_tree figure quality (KH-201, KH-202, KH-203)

### KH-201 (LOW): power_tree legend always shows green for output rails

- **File**: `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`
- **Root cause**: Legend hardcoded a single "Output Rail" entry using the first color from `output_color_map`, regardless of how many output rails exist or what colors they use.
- **Fix**: When <= 5 output rails, render one legend entry per rail with its actual assigned color and rail name. When > 5, fall back to a single "Output Rails" entry to avoid overflow.
- **Verified**: Syntax check passes. Visual inspection pending next kidoc render.

### KH-202 (MEDIUM): power_tree output rail boxes lack context

- **File**: `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`
- **Root cause**: `prepare()` only extracted rail name and voltage for output rails. No information about what loads each rail powers.
- **Fix**: In `prepare()`, collect load context per output rail: cascade regulators (other regulators fed by this rail) and `cross_sheet_loads` from feeding regulators. In `render()`, display up to 2 load items as a subtitle below the voltage (e.g. "U3 (LDO), U4 (Buck)"). Truncated with "+N" for >2 loads.
- **Verified**: Syntax check passes. Visual inspection pending next kidoc render.

### KH-203 (MEDIUM): power_tree regulator boxes have minimal detail

- **File**: `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`
- **Root cause**: Regulator body_lines only showed topology and output cap summary. No voltage conversion context (input→output).
- **Fix**: In `prepare()`, resolve input voltage per regulator from upstream regulator `estimated_vout` or `_infer_voltage()` on input rail name. In `render()`, restructured body_lines: line 1 = voltage conversion (e.g. "5.0V → 3.3V"), line 2 = topology + inductor, line 3 = Cout summary.
- **Verified**: Syntax check passes. Visual inspection pending next kidoc render.

---

## 2026-04-06 — Batch 30: kidoc test plan bugs (KH-199, KH-200)

### KH-199 (P0): power_tree figure generator crashes on None rail names

- **File**: `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`
- **Phase**: 8 (corpus smoke test)
- **Root cause**: Regulators with `None` as `input_rail` or `output_rail` caused two crashes: (1) `sorted()` on a set containing `None` and `str` raises `TypeError: '<' not supported`, (2) `_infer_voltage(None)` calls `.strip()` on `None`.
- **Fix**: Added `input_rail_set.discard(None)` / `output_rail_set.discard(None)` before sorting. Added early return `""` in `_infer_voltage()` when `rail_name` is falsy.
- **Verified**: 100/100 corpus smoke files pass with zero crashes (was 5 failures).

### KH-200 (P0): narrative executive_summary extractor crashes on None output_rail

- **File**: `skills/kidoc/scripts/kidoc_narrative_extractors.py` line 474
- **Phase**: 8 (corpus smoke test)
- **Root cause**: `r.get('output_rail', '?')` returns `None` (not `'?'`) when the key exists but has a `None` value. The `None` then causes `', '.join(rails)` to fail with `TypeError: sequence item 0: expected str instance, NoneType found`.
- **Fix**: Changed to `r.get('output_rail') or '?'` which correctly falls back to `'?'` for both missing and `None` values.
- **Verified**: 100/100 corpus smoke files pass with zero crashes (was 4 failures).

---

## 2026-04-04 — Batch 29: Pre-existing bugs found during v1.2 Batch 4 (KH-196, KH-197, KH-198)

### KH-196 (HIGH): Bare capacitor values parsed as Farads in inrush/PDN analysis

- **File**: `analyze_schematic.py` — `analyze_inrush_current()` line 6658, `analyze_pdn_impedance()` line 4788
- **Root cause**: Both functions called `parse_value(comp.get("value", ""))` without `component_type="capacitor"`. Bare numeric values like "2.2" were interpreted as 2.2 Farads instead of applying the KH-153 picofarad heuristic. On the BandSelector board, this produced `total_output_capacitance_uF: 2,200,000` and `estimated_inrush_A: 22,000` — physically impossible for a small THT electrolytic.
- **Fix**: Replaced both call sites with `ctx.parsed_values.get(comp["reference"])` which uses pre-computed values from `AnalysisContext.__post_init__()` (already passes `component_type`).
- **Verified**: 6,850/6,850 batch pass. BandSelector assertion now passes. 122,038/122,038 regression assertions at 100%.

### KH-197 (MEDIUM): Key matrix topology detector false positives and overcounting

- **File**: `domain_detectors.py` — `detect_key_matrices()`
- **Root cause**: Three sub-bugs in the topology-based key matrix detector:
  (a) Net-name detection counted switches/diodes across all row+col nets without deduplicating by component reference, inflating counts when a component touches both a row and column net.
  (b) Topology detection didn't track paired switches, allowing the same switch to pair with different diodes from both pin orderings, double-counting it.
  (c) Topology detection assigned row_net/col_net based on arbitrary diode orientation without checking for nets appearing in both sets, causing row/column confusion.
- **Fix**: (a) Added `counted_refs` set to deduplicate switch/diode counts by reference. (b) Added `paired_switches` tracking with `found_pair` flag to limit one pair per switch. (c) Added ambiguous net resolution: nets appearing in both row_nets and col_nets are assigned to whichever set they appear in more often (ties removed from both).
- **Side effect**: 19 non-keyboard boards (GEODE robot, cm4_robot, vortex_core, BMP_SuperColliderClone, etc.) previously had false positive key_matrices detections from the overcounting bug. These are now correctly empty. Updated 38 stale assertions.
- **Verified**: 6,850/6,850 batch pass. Original 3 keyboard failures resolved. 122,038/122,038 regression at 100%.

### KH-198 (MEDIUM): LC filter reference collision in multi-project schematics

- **File**: `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: The Caffeinated-AFTONSPARV schematic has components from another project embedded, causing multiple physically distinct capacitors to share reference "C5". The LC filter detector iterated pins on the LX net and found 9 pins all belonging to "C5", counting them as 9 parallel caps instead of 1.
- **Fix**: Added reference deduplication in the parallel-cap merge loop — if the same capacitor reference appears multiple times in an LC group, only the first occurrence is kept.
- **Verified**: 6,850/6,850 batch pass. Caffeinated-AFTONSPARV assertion now passes.

---

## 2026-04-03 — Batch 28: v1.2 Batch 3 interface validation detectors (KH-194, KH-195)

### KH-194 (MEDIUM): ESD audit "can" keyword matches inside "scan" footprint names

- **File**: `signal_detectors.py` — `_classify_connector_interface()`
- **Root cause**: Plain substring check `"can" in combined` matched "can" inside footprint strings like `sockets_scanhead:motor_13pin`, causing generic connectors to be classified as CAN bus / high_risk. Affected the `firestarter` project (8 connectors) and potentially other boards with "scan", "cancel", etc. in footprint or lib_id.
- **Fix**: Added `_kw_match()` helper that uses `re.search(r'\b...\b', combined)` word-boundary matching for short keywords (≤3 chars). Applied to all three keyword lists (high/medium/low risk). Longer keywords like "ethernet", "displayport" still use plain substring matching.
- **Verified**: 6,850/6,850 schematic batch pass. 0 generic pin headers classified as high_risk (was 10 before fix). 117,167/117,167 regression assertions pass.

### KH-195 (LOW): USBPDSINK01 assertion expects 3 USB compliance failures, now 1

- **File**: Assertion `FND-00001757-AST-04` in `reference/mlab-modules/USBPDSINK01/.../USBPDSINK01.kicad_sch_finding.json`
- **Root cause**: New PD controller detection in `analyze_usb_compliance()` correctly identifies STUSB4500QTR on CC1/CC2 nets and marks legacy `cc1_pulldown_5k1`/`cc2_pulldown_5k1` checks as "pass" instead of "fail". The STUSB4500 integrates internal CC termination, so external 5.1kΩ pull-downs are absent by design. This reduced `usb_compliance.summary.fail` from 3 to 1 (only `vbus_esd_protection` remains as a failure).
- **Fix**: Updated assertion expected value from 3 → 1 and rewrote description to reflect PD-controlled CC termination.
- **Verified**: 117,167/117,167 regression assertions pass (100%).

---

## 2026-04-02 — Batch 27: parse_tolerance() coverage + run_spice.py passthrough (KH-193, TH-008)

### KH-193 (LOW): parse_tolerance() misses value strings with non-standard delimiters

- **File**: `kicad_utils.py` — `parse_tolerance()`
- **Root cause**: Split regex only covered `/ \s _ , ±` delimiters. Values using hyphen (`100K-1%`), pipe (`100p|5%|16V`), or leading-dot tolerance (`.1%`) were not parsed. Affected Monte Carlo tolerance bands for ~6% of values with explicit tolerance.
- **Fix**: Three changes:
  1. Added `-` and `|` to the split regex: `r'[/\s_,±|\-]+'`
  2. Changed number regex from `\d+(?:\.\d+)?` to `\d*\.?\d+` to accept `.1%` (no leading digit)
  3. Applied same regex fix to the parenthesized fallback pattern
- **Verified**: Parse rate 756/759 (99.6%), up from 711/759 (93.7%). All parsed tolerances in valid 0.1%-50% range. MC test on Power-PCB passes, SPICE assertions unchanged.
- **Note**: Initial fix (splitting on `_ , ±`, stripping `()+-`) was included in commit `4eb8fb2` by the other agent. This fix addresses the remaining edge cases.

### TH-008 (LOW): run_spice.py missing --extra-args passthrough

- **File**: `run/run_spice.py`
- **Root cause**: No mechanism to forward additional arguments (e.g., `--monte-carlo`, `--mc-seed`, `--mc-distribution`) from the batch runner to `simulate_subcircuits.py`.
- **Fix**: Added `--extra-args` CLI flag that passes through to `run_one_spice()` via `shlex.split()`. Args appended to the subprocess command.
- **Verified**: Used in all MC test plan phases (1-8). MC N=100 on 5 repos, reproducibility test, edge cases all pass through the runner.

---

## 2026-04-02 — Batch 26: diff_analysis.py set-on-dicts crash (KH-192)

### KH-192 (HIGH): diff_analysis.py crashes with TypeError on 44% of schematic outputs

- **File**: `diff_analysis.py` — `diff_schematic()`, lines ~352 and ~366
- **Root cause**: Two locations used `set()` on lists that can contain dicts:
  1. Line ~352: `connectivity_issues` — `single_pin_nets`, `floating_nets`, `multi_driver_nets` can contain dicts with nested pin info, not just strings
  2. Line ~366: `erc_warnings` — always dicts with nested `pins` lists containing component/pin_number/pin_name
  `set()` requires hashable elements; dicts are not hashable, so both lines raise `TypeError: unhashable type: 'dict'`.
- **Impact**: 3,023 of 6,853 schematic outputs (44%) have ERC warnings; 140+ have dict-type connectivity issues. diff_analysis.py crashed with 100% failure rate on any file with either. Blocked diff-aware design reviews on nearly half of real-world designs.
- **Fix**: Both locations now use hashable key representations — JSON serialization for connectivity issues, tuple keying for ERC warnings. Set operations (difference, intersection) work on the keys while preserving the original dicts for output.
- **Verified**: 4-phase test plan executed:
  - Phase 1: 50 previously-crashing files (25 ERC + 25 conn) all self-diff successfully with `has_changes: false`
  - Phase 2: ERC diff correctness — added/removed warnings correctly detected using mutated test data
  - Phase 3: Connectivity diff correctness — added/removed items correctly detected using mutated test data
  - Phase 4: 100 corpus pairs (82 with ERC, 55 with connectivity issues), 0 crashes, 0 errors
- **Discovered**: 2026-04-01 during diff-analysis test plan Phase 2 (schematic diff mutations)

---

## 2026-04-01 — Batch 25: PCB --full stackup string type bug (KH-191)

### KH-191 (HIGH): PCB analyzer crashes with --full on boards with string stackup values

- **File**: `analyze_pcb.py` — `_build_layer_heights()`, `_microstrip_impedance()`
- **Root cause**: `_microstrip_impedance()` compares height_mm/thickness_mm/epsilon_r against 0 using `<=`, but stackup values from some KiCad files are strings (e.g., `"0.2"` instead of `0.2`). `_build_layer_heights()` passes these raw values through. Affects 1,137 of 3,498 PCB files when using `--full`.
- **Fix**: Added `_safe_num()` helper (same pattern as EMC's `_safe_float()`). Applied in `_build_layer_heights()` for thickness, epsilon_r, and copper_thickness reads. Also applied as guard at top of `_microstrip_impedance()`.
- **Verified**: Full corpus with `--full`: 3,496/3,498 pass (99.9%). 2 failures are known empty stub files.

---

## 2026-04-01 — Batch 24 (EMC): 4 EMC analyzer bugs found during corpus run (KH-187–KH-190)

Bugs discovered during first full-corpus EMC run (6,853 files). All in `analyze_emc.py` and `emc_rules.py`.

### KH-187 (MEDIUM): Crystal frequency field can be None, crashes comparison

- **File**: `emc_rules.py` — `check_via_stitching()`, `analyze_emc.py` — `extract_board_info()`
- **Root cause**: Schematic analyzer sometimes emits `"frequency": null` for crystal circuits with unparseable values. EMC code did `freq > highest_freq` which raises TypeError on NoneType.
- **Fix**: Changed `xtal.get('frequency', 0)` to `xtal.get('frequency') or 0` with `isinstance(freq, (int, float))` guard in both files.
- **Verified**: Full corpus 6853/6853, 0 script errors. Eliminated 495 crashes.

### KH-188 (MEDIUM): Stackup thickness field can be string, crashes addition

- **File**: `emc_rules.py` — `check_stackup()`
- **Root cause**: Some KiCad files export stackup layer thickness as string (e.g., `"0.2"` instead of `0.2`). The `d_total += thickness` addition raised TypeError.
- **Fix**: Added `_safe_float()` helper that handles None, str, and invalid values with a default. Applied to all `thickness` and `epsilon_r` reads in stackup checks.
- **Verified**: Full corpus 6853/6853, 0 script errors. Eliminated 69 crashes.

### KH-189 (LOW): Footprint value field can be list, crashes .lower()

- **File**: `emc_rules.py` — `_connector_refs()`, `check_connector_filtering()`, `check_missing_decoupling()`
- **Root cause**: Some schematic analyzer outputs emit `"value": ["part1", "part2"]` as a list when a component has multiple value fields. Three places called `.lower()` directly on the result of `fp.get('value', '')`.
- **Fix**: Wrapped all three sites with `(raw_val if isinstance(raw_val, str) else str(raw_val)).lower()`.
- **Verified**: Full corpus 6853/6853, 0 script errors. Eliminated 3 crashes.

### KH-190 (LOW): Footprint lib_id field can be list

- **File**: `emc_rules.py` — `_connector_refs()`, `check_connector_filtering()`
- **Root cause**: Same pattern as KH-189 but for `lib_id` field.
- **Fix**: Same wrapping as KH-189 applied to `lib_id` reads.
- **Verified**: Full corpus 6853/6853, 0 script errors.

---

## 2026-03-23 — Batch 25: Last 2 LOW issues (KH-173, KH-176)

Fixes the final 2 open issues. All KH-* issues are now closed.

### KH-173 (LOW): SMD ratio uses incommensurate units

- **File**: `analyze_gerbers.py` — `parse_gerber()`, `build_pad_summary()`
- **Root cause**: `by_function` counted unique aperture definitions (shapes), not flash instances. A board with 13 unique SMDPad shapes but 113 placements on one layer got the same count as one with 13 placements. THT used actual hole instances, making the SMD ratio meaningless.
- **Fix**: Track aperture selection state (`current_aperture`) and count flashes per D-code in `aperture_flash_counts`. Aggregate into `by_function_flashes` (instance counts per function). `build_pad_summary()` now prefers `by_function_flashes` over `by_function`, falling back for backward compatibility.
- **Verified**: bitaxe SMD went from 45 (unique defs) to 364 (instances), ratio from 0.44 to 0.85 — correct for a BGA design. Full corpus 1048/1048 gerber pass, 203K assertions 0 failures.

### KH-176 (LOW): DFM fab house capability thresholds not canonicalized

- **File**: `references/standards-compliance.md`, `references/report-generation.md`, `analyze_pcb.py`
- **Root cause**: No single authoritative fab capability table in reference files. LLM report author filled in thresholds from training data, which varied between runs.
- **Fix**: Added canonical "Fab House Capabilities" table to `standards-compliance.md` with JLCPCB standard/advanced tiers and PCBWay standard tier, all with source and verification date. Added source comments to `LIMITS_STD`/`LIMITS_ADV` in `analyze_pcb.py` pointing to the canonical table. Updated `report-generation.md` DFM section to mandate citing from the canonical table.
- **Verified**: All three files updated consistently. PCB full corpus 3491/3491 pass, 203K assertions 0 failures.

---

## 2026-03-23 — Batch 24: 4 LOW issues (KH-186, KH-166, KH-167, KH-175)

Fixes 4 LOW severity issues across gerber, PCB, and schematic analyzers.

### KH-186 (LOW): Large NPTH holes misclassified as component_holes via X2

- **File**: `analyze_gerbers.py` — `classify_drill_tools()`
- **Root cause**: KiCad labels all NPTH holes as `ComponentDrill` in X2 attributes regardless of diameter. The analyzer trusted this, so 3.0-3.5mm mounting holes were misclassified.
- **Fix**: In both NPTH and general branches, NPTH holes with `ComponentDrill` aper_function and diameter >= 2.5mm are reclassified as mounting holes. Threshold is conservative (higher than the 2.0mm no-X2 heuristic) since we're overriding explicit X2 data.
- **Verified**: SparkFun XRP mounting_holes 0→24. Full corpus 1048/1048 gerber pass, 203K assertions 0 failures.

### KH-166 (LOW): False positive missing_revision silkscreen warning

- **File**: `analyze_pcb.py` — `extract_silkscreen()`
- **Root cause**: Revision check only scanned silkscreen text for keywords like "REV", "V1". Did not check the title block `rev` field, which is KiCad's canonical revision storage.
- **Fix**: Check title block `rev` field first. If non-empty, skip warning. Also improved silkscreen regex to match patterns like `R3B7` via `[RV]\d`.
- **Verified**: modular-psu aux-ps: missing_revision warning gone (rev=r3B7 from title block). Full corpus 3491/3491 PCB pass.

### KH-167 (LOW): ESD/TVS protection devices in decoupling analysis

- **File**: `analyze_pcb.py` — `analyze_decoupling_placement()`
- **Root cause**: All U-prefix components were included in decoupling analysis. ESD/TVS devices (RCLAMP, PRTR, USBLC, etc.) use U-prefix but don't need bypass caps.
- **Fix**: Added `_ESD_TVS_PREFIXES` tuple and value-based filter to exclude known ESD/TVS families from the IC selection list.
- **Verified**: cnhardware radioset: U3 (RCLAMP0502N) no longer in decoupling. ~303 false positives removed across corpus.

### KH-175 (LOW): Sleep current total includes conditional pull-up paths

- **File**: `analyze_schematic.py` — `analyze_sleep_current()` summary loop
- **Root cause**: `total_estimated_sleep_uA` summed all paths equally, including pull-up resistors at worst-case I=V/R. Pull-ups are conditional on signal state — during sleep they typically draw zero current.
- **Fix**: Split into `total_estimated_sleep_uA` (always-on only: dividers, LEDs, regulator Iq) and `conditional_pull_up_uA` (pull-ups). Added per-rail `always_on_uA`/`conditional_uA` breakdowns.
- **Verified**: No test corpus repos produce sleep_current_audit output (requires specific power topology). Code review confirmed correct type-based classification.

---

## 2026-03-22 — Batch 23: 3 MEDIUM gerber issues (KH-183–KH-185)

Fixes 3 MEDIUM severity gerber analyzer bugs. All fixes in analyze_gerbers.py.

### KH-183 (MEDIUM): Drill extent coordinates not normalized to mm

- **File**: `analyze_gerbers.py` — `parse_drill()`
- **Root cause**: Drill files with integer coordinates (no decimal point, e.g. `X40123Y-40386` meaning 40.123mm) were stored as raw integers. Gerber layer extents are in mm, so drill extents were 1000x too large for metric 3:3 format files.
- **Fix**: Detect integer vs decimal coordinate format on first coordinate line. Parse `; FORMAT={X:Y/...}` comment for decimal digits. Apply divisor (1000 for metric, 10000 for inch) for integer-format files, then convert inch to mm.
- **Verified**: HadesFCS Hades drill_PTH width: 97663→97.663mm. Full corpus 1048/1048 gerber pass, 8970 gerber assertions 0 failures.

### KH-184 (MEDIUM): Combined PTH+NPTH drill file → has_pth/npth both false

- **File**: `analyze_gerbers.py` — `analyze_gerbers()`
- **Root cause**: `has_pth_drill`/`has_npth_drill` only true when drill type is explicitly "PTH"/"NPTH"/"mixed". Combined drill files without X2 FileFunction header got type "unknown", so both flags were false even with 189+ vias.
- **Fix**: After `classify_drill_tools()`, infer PTH from via presence — if vias exist and drill type is "unknown", set type to "PTH". Moved `classify_drill_tools()` before `check_completeness()` so inferred types are available.
- **Verified**: HadesFCS (3 boards) and glasgow (5 revisions) all report has_pth_drill=true. 8970 gerber assertions 0 failures.

### KH-185 (MEDIUM): front_side/back_side component counts wrong

- **File**: `analyze_gerbers.py` — `build_component_analysis()`
- **Root cause**: Component side assignment used only F.Cu/B.Cu layers, but KiCad's X2 export doesn't include TO.C attributes on copper layers. TO.C attributes are on mask/silk/paste layers.
- **Fix**: Expanded layer matching to include F.Mask/F.SilkS/F.Paste (and back equivalents) in addition to F.Cu/B.Cu.
- **Verified**: bitaxe front_side 0→124, SparkFun XRP front_side 0→227. 8970 gerber assertions 0 failures.

---

## 2026-03-22 — Batch 22: 6 HIGH gerber issues (KH-177–KH-182)

Fixes 6 HIGH severity gerber analyzer bugs discovered during first gerber Layer 3
reviews (Batch 21). All fixes in analyze_gerbers.py.

### KH-177 (HIGH): pad_summary.smd_apertures always zero

- **File**: `analyze_gerbers.py` — `build_pad_summary()`
- **Root cause**: `smd_apertures` counted unique aperture definitions with X2 `SMDPad` function. KiCad 5 outputs lack X2 aperture function tags, so count was always 0.
- **Fix**: Added paste layer flash count fallback — when X2 smd count is 0, count flash instances on F.Paste/B.Paste layers (paste only contains SMD pad openings). Added `smd_source` field to indicate data source.
- **Verified**: HadesFCS Hades: 0 → 716 smd_apertures (paste_layer_flashes). Full corpus 1048/1048 pass. 203,179 assertions, 0 failures.

### KH-178 (HIGH): Eagle .TXT Excellon drill files not recognized

- **File**: `analyze_gerbers.py` — `analyze_gerbers()`, new `_is_excellon_file()`
- **Root cause**: File glob only matched `*.drl`/`*.DRL`. Eagle CAM exports drill files with `.TXT` extension.
- **Fix**: Added `.TXT`/`.txt` glob with M48 header validation to avoid false positives on non-drill text files. Also filter `.txt` from gerber file list.
- **Verified**: modular-psu aux-ps Eagle: drill_files 0→1, total_holes 0→258.

### KH-179 (HIGH): Eagle .G2L/.G3L inner copper layers not discovered

- **File**: `analyze_gerbers.py` — `identify_layer_type()`, `analyze_gerbers()`
- **Root cause**: Protel inner layer regex `\.g(\d+)$` didn't match `.g2l`/`.G2L`. Glob patterns didn't include `.G2L` etc.
- **Fix**: Changed regex to `\.g(\d+)l?$`. Added `*.G2L`/`*.G3L`/`*.G4L`/`*.G5L`/`*.G6L`/`*.GTP`/`*.GBP` to uppercase globs.
- **Verified**: modular-psu DCP405: layer_count 2→4, inner layers In2.Cu/In3.Cu found.

### KH-180 (HIGH): Eagle board dimensions in inches mislabeled as mm

- **File**: `analyze_gerbers.py` — `compute_board_dimensions()`
- **Root cause**: Edge.Cuts coordinate range stored in raw file units without checking gerber's `units` field.
- **Fix**: Check `g.get("units") == "inch"` and multiply by 25.4 before returning.
- **Verified**: modular-psu aux-ps Eagle: 9.07x2.36 "mm" → 230.5x60.0mm (correct).

### KH-181 (HIGH): GKO misclassified when X2 FileFunction conflicts with AperFunction=Profile

- **File**: `analyze_gerbers.py` — `identify_layer_type()`
- **Root cause**: KiCad 8 Pcbnew sometimes assigns wrong FileFunction (Copper) to .GKO board outline. Analyzer trusted X2 FileFunction without cross-checking filename.
- **Fix**: In the X2 copper branch, check if filename extension is `.gko` — if so, return `Edge.Cuts` since .gko is unambiguously the board outline.
- **Verified**: SparkFun XRP production: GKO layer_type In4.Cu→Edge.Cuts, board_dimensions restored, missing_required empty, complete=true.

### KH-182 (HIGH): %TD*% does not clear current_component

- **File**: `analyze_gerbers.py` — `parse_gerber()`
- **Root cause**: `%TD*%` handler only cleared `pending_aper_function`. Per Gerber X2 spec, it should clear ALL object attributes including component and net.
- **Fix**: Also set `current_component = None` and `current_net = None` on `%TD*%`.
- **Verified**: bitaxe J2: 203 pads → 2 pads (correct for 2-pin connector).

---

## 2026-03-17 — Batch 19: 5 MEDIUM issues (KH-160, KH-163, KH-164, KH-165, KH-174)

Fixes remaining 5 MEDIUM issues across schematic and PCB analyzers. All independent
fixes: IC-prefix decoupling, PWR_FLAG skip removal, small DFN/QFN thermal pad detection,
thermal via containment margin, and raw adequacy reporting.

### KH-160 (MEDIUM): PWR_FLAG skip over-aggressive for connector-powered designs

- **File**: `analyze_schematic.py` — `check_pwr_flag_warnings()` lines ~3703–3707
- **Root cause**: Lines 3704–3707 skipped PWR_FLAG warnings on any net with a recognized
  power/ground name, even when no power port symbol (power_out pin) existed. The function
  already iterates only over `known_power_rails` (nets with `#PWR`/`#FLG` components).
  If a power port symbol provides power_out, `has_power_out` is True and the skip never
  triggers. Reaching the skip meant the net genuinely lacked a power_out driver.
- **Fix**: Removed the name-based skip entirely (deleted lines 3704–3707).
- **Verified**: Full corpus 6827/6827 schematic pass. No false positives in modular-psu
  (multi-sheet with proper power symbols). 162,234 assertions, 0 failures.

### KH-163 (MEDIUM): thermal_pad_vias and thermal_analysis contradictory via counts

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` line ~3050
- **Root cause**: Rectangular containment used 1.1x margin. Vias placed on standard
  manufacturing grids fell outside. IC2 (BD00FC0W, TO-252-5) in modular-psu: pad is
  5.5×5.7mm rotated 90°, nearest vias at ±4.25mm from pad center in local-y (half_h=2.85,
  ratio=1.49x). thermal_analysis uses 1.5x circular radius, found 44 vias; thermal_pad_vias
  found 0.
- **Fix**: Widened containment margin from 1.1x to 1.5x to match thermal_analysis proximity.
- **Verified**: IC2 now reports via_count=18, adequacy="good" (was 0/"none"). Full corpus
  3491/3493 pass (2 pre-existing parser errors).

### KH-164 (MEDIUM): decoupling_placement absent for IC-prefix components

- **File**: `analyze_pcb.py` — `analyze_decoupling_placement()` line ~1040
- **Root cause**: IC regex `^U\d` only matched U-prefix components. modular-psu has IC1
  (MAX31760AEE+) and IC2 (BD00FC0W) — "IC" prefix not "U".
- **Fix**: Broadened regex to `^(U|IC)\d`.
- **Verified**: modular-psu aux-ps now has 2 decoupling_placement entries (IC1, IC2). MCU
  boards show 16 entries each.

### KH-165 (MEDIUM): Thermal pad detection misses small DFN/QFN exposed pads

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` and `analyze_thermal_vias()`
- **Root cause**: Two issues: (1) EP detection only matched pad names "0", "EP", "" — DFN
  variants use numbered pads as EP. (2) Area thresholds too high: EP pads needed >4mm²,
  non-EP needed >9mm² — excluded 2×2mm DFN EPs (~2.5mm²).
- **Fix**: (1) Added area-ratio EP detection: if pad area ≥3× median signal pad area,
  treat as EP. Applied to both functions. (2) Lowered thresholds: EP pads ≥2mm² (was >4mm²),
  non-EP >6mm² (was >9mm²).
- **Verified**: cnhardware CH32V003F4U6 now detected (pad_area=2.72mm²) in both
  thermal_pad_vias and thermal_pads.

### KH-174 (MEDIUM): Thermal via adequacy too aggressive for small-drill designs

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` lines ~3104–3111
- **Root cause**: Adequacy thresholds calibrated for 0.3mm reference vias. Designs using
  smaller vias (0.2mm) to prevent solder wicking scored "insufficient" despite following
  manufacturer's recommended via pattern.
- **Fix**: Added `raw_adequacy` field (same thresholds but using raw via count instead of
  effective). Added `small_via_note` when raw count meets threshold but effective doesn't,
  explaining the discrepancy with average drill size. Tracks drill_sum during via counting.
- **Verified**: New fields appear correctly. Existing fields unchanged. 162,234 assertions,
  0 failures.

---

## 2026-03-17 — Batch 18: 7 PCB/Gerber issues (KH-161, KH-162, KH-168–KH-172)

PCB and Gerber Layer 3 reviews surfaced 14 issues; this batch fixes the 4 HIGH and 3
MEDIUM issues with clear root causes. Remaining 7 issues (KH-160, KH-163–167, KH-173)
need more investigation or are LOW severity.

### KH-161 (HIGH): back_side footprint count is 0 on KiCad 9

- **File**: `analyze_pcb.py` — `compute_statistics()` line ~2300
- **Root cause**: `back_copper` was resolved via `l["number"] == 31`. In KiCad 9, B.Cu
  is layer number 2 (not 31), so number 31 resolved to "F.CrtYd" — no footprint matched.
- **Fix**: Removed number-based layer lookup. Hardcoded `front_copper, back_copper =
  "F.Cu", "B.Cu"` since these names are invariant across KiCad 5–9.
- **Verified**: explorer `back_side=83` (was 0), `front_side=185` unchanged. Full corpus
  3491/3493 pass (2 pre-existing parser errors).

### KH-162 (HIGH): Hierarchical net names not recognized as power

- **File**: `kicad_utils.py` — `is_power_net_name()` line ~591, `is_ground_name()` line ~627
- **Root cause**: `/Power Supply/VCC` didn't match because hierarchical path prefix
  wasn't stripped before pattern matching.
- **Fix**: Added `rsplit("/", 1)[-1]` prefix stripping at the top of both functions.
- **Verified**: explorer `power_net_routing` now has 2 nets, `current_capacity` present.

### KH-168 (HIGH): NPTH holes unconditionally classified as mounting

- **File**: `analyze_gerbers.py` — `classify_drill_holes()` lines ~564–568
- **Root cause**: All NPTH file holes went to `mounting_count` without checking diameter
  or per-tool aper_function.
- **Fix**: For NPTH files, check per-tool X2 aper_function first (ViaDrill/ComponentDrill),
  then fall back to diameter heuristic: ≤2.0mm → component, >2.0mm → mounting.
- **Verified**: CO60 mounting 510→326 (NPTH alignment pins moved to component),
  MechKeyboard mounting 371→0 (all NPTH ≤2mm). Full corpus 1048/1048 pass.

### KH-169 (HIGH): Layer count not inferred from X2 Ln designation

- **File**: `analyze_gerbers.py` — after layer count computation, line ~1058
- **Root cause**: Layer count only counted found copper gerber files. If inner layers
  were missing but B.Cu had `Copper,L4,Bot`, layer_count stayed at 2.
- **Fix**: Added scan of all gerber X2 FileFunction attributes for `Copper,Ln` pattern,
  using max(Ln) as lower bound for layer count.
- **Verified**: SparkFun_GNSSDO `layer_count=4` (was 2).

### KH-170 (MEDIUM): MixedPlating drill files not recognized

- **File**: `analyze_gerbers.py` — drill type detection lines ~387–395, completeness
  checks lines ~628–644
- **Root cause**: Only "NonPlated" and "Plated" matched in FileFunction; "MixedPlating"
  fell through to "unknown".
- **Fix**: Added "MixedPlating" → type "mixed". Updated layer_span regex. Updated
  `has_pth_drill`/`has_npth_drill` to accept "mixed" type.
- **Verified**: glasgow revC3 `has_pth=True, has_npth=True` (MixedPlating recognized).

### KH-171 (MEDIUM): Unknown-type drill files cause complete=false

- **File**: `analyze_gerbers.py` — completeness check line ~644
- **Root cause**: Required `d.get("type") == "PTH"` for completeness. KiCad 5 combined
  .drl files without X2 attributes got type "unknown".
- **Fix**: Relaxed `complete` check to accept "unknown" type drills (in addition to PTH
  and mixed). `has_pth_drill` stays strict for informational accuracy.
- **Verified**: esp32-lifepo4-board `complete=True` (was False).

### KH-172 (MEDIUM): Alignment threshold fixed at 2mm

- **File**: `analyze_gerbers.py` — `check_alignment()` lines ~675–680
- **Root cause**: Hardcoded 2.0mm threshold caused false positives on large boards where
  copper-to-edge gap naturally exceeds 2mm.
- **Fix**: Use relative threshold: 5% of Edge.Cuts dimension, minimum 2.0mm.
- **Verified**: bitaxe `aligned=True` (was False), modular-psu mostly `aligned=True`.
  Full corpus 161,878 assertions, 0 failures.

---

## 2026-03-17 — Batch 17: 6 PCB issues (KH-154–KH-159)

PCB Layer 3 review surfaced 6 bugs in analyze_pcb.py: incorrect copper layer counts,
false positive thermal pad detections, and inflated zone stitching densities. All fixed.

### KH-154 (HIGH): copper_layers_used includes non-copper layers

- **File**: `analyze_pcb.py` — `compute_statistics()` line ~2277
- **Root cause**: Filtered layers by type `in ("signal", "power", "mixed", "user")`. In KiCad
  7+ files, non-copper layers (F.SilkS, F.Mask, B.Paste, etc.) all have type `"user"`, so
  they were included in `copper_layer_names`.
- **Fix**: Replaced type-based filter with layer-number filter. KiCad copper layers have
  numbers 0–31 (0=F.Cu, 31=B.Cu, 1–30=inner layers).
- **Verified**: hackrf 5→4, Neo6502pc-PWR 3→2. Full corpus 42,872 assertions at 100%.

### KH-155 (MEDIUM): copper_layers_used misses zone-only layers

- **File**: `analyze_pcb.py` — `compute_statistics()` lines ~2306–2308
- **Root cause**: Zones WERE included in `all_used_layers`, but the buggy type filter from
  KH-154 excluded their copper layers. Fixing KH-154's layer-number filter resolved this.
- **Fix**: No additional code change needed — resolved by KH-154 fix.
- **Verified**: moteus now correctly reports 4 copper layers (In1.Cu counted via zone fills).

### KH-156 (HIGH): Paste-only stencil aperture pads as thermal pads

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` and `analyze_thermal_vias()`
- **Root cause**: Thermal pad detection checked `pad.get("type") != "smd"` but didn't verify
  the pad has copper layers. Paste-only stencil apertures (type=smd, layers=["F.Paste"])
  passed the filter.
- **Fix**: Added copper-layer check: skip pads whose layers don't include any `*.Cu` layer.
  Applied to both `analyze_thermal_pad_vias()` and `analyze_thermal_vias()`.
- **Verified**: ESP32-P4-PC thermal_pad_vias ~19→2, Neo6502pc ~19→2-3.

### KH-157 (MEDIUM): Connector structural/shield pads as thermal pads

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` and `analyze_thermal_vias()`
- **Root cause**: Unnamed/EP pads with no net bypassed the power/ground net check. Structural
  pads on connectors (mounting tabs, shield pads) have no net but passed as EP pads.
- **Fix**: Added no-net filter before the power/ground check: skip pads with empty net_name
  or net_number ≤ 0. Real thermal pads always have a net connection.
- **Verified**: False positives from connector structural pads eliminated.

### KH-158 (LOW): Thermal via adequacy ignores drill diameter

- **File**: `analyze_pcb.py` — `analyze_thermal_pad_vias()` lines ~3044–3061
- **Root cause**: Via count and adequacy thresholds treated all vias equally regardless of
  drill size. A 1.0mm drill via conducts ~10× more heat than a 0.3mm via.
- **Fix**: Weight each via by `(drill/0.3)²` (cross-sectional area ratio). Added
  `effective_via_count` to output. Adequacy thresholds use effective count.
- **Verified**: Boards with larger drill vias now get more accurate adequacy ratings.

### KH-159 (LOW): Zone stitching per-polygon areas inflate density

- **File**: `analyze_pcb.py` — `analyze_thermal_vias()` lines ~1441–1467
- **Root cause**: Iterated over `zone_bounds` (one entry per zone polygon). Multi-polygon
  nets created duplicate stitching entries with different areas but the same via list.
- **Fix**: Aggregate zone_bounds by net before computing density. One stitching entry per
  net with total area across all polygons.
- **Verified**: Duplicate stitching entries eliminated. Full corpus 42,872 assertions at 100%.

---

## 2026-03-16 — Batch 14: 13 issues (KH-141–KH-153)

Layer 3 Batch 15 review surfaced 9 new bugs, 4 already known. All 13 fixed: false positives
eliminated, misclassifications corrected, missing parser support added.

### KH-141 (MEDIUM-HIGH): Legacy KiCad 5 sym-lib-table not parsed for pin resolution

- **File**: `analyze_schematic.py` — `_resolve_legacy_libs()`
- **Root cause**: Only tried `*-cache.lib` (Strategy 1) and `LIBS:` header (Strategy 2). KiCad 5
  file version 4 uses `sym-lib-table` (S-expression) — never parsed. 515 repos affected.
- **Fix**: Added Strategy 2.5 — parse `sym-lib-table`, resolve `${KIPRJMOD}`, load referenced
  `.lib` files via `_parse_legacy_lib()`.
- **Verified**: All 13 affected repos pass, 0 failures.

### KH-142 (MEDIUM): Legacy .lib ALIAS directive not handled

- **File**: `analyze_schematic.py` — `_parse_legacy_lib()`
- **Root cause**: Only registered primary `DEF` name, ignoring `ALIAS name1 name2 ...` lines.
  397 `.lib` files use ALIAS directives.
- **Fix**: Track `current_aliases` list during DEF block parsing. At ENDDEF, register same
  symbol definition under each alias name.
- **Verified**: All repos pass, 0 failures.

### KH-143 (LOW): Multi-unit TVS diode arrays create duplicate protection entries

- **File**: `signal_detectors.py` — `detect_protection_devices()` line ~1631
- **Root cause**: Missing duplicate ref check for 2-pin TVS path. Multi-unit TVS arrays
  (e.g. PESD3V3L4UG) created one entry per unit with same pins.
- **Fix**: Added `if any(p["ref"] == comp["reference"] for p in protection_devices): continue`
  before appending, matching existing pattern at lines 1587 and 1644.
- **Verified**: 9 genuine duplicates eliminated across corpus.

### KH-144 (MEDIUM): Test pad components misclassified when value is empty

- **File**: `kicad_utils.py` — `classify_component()`, and `analyze_schematic.py` — test point detection
- **Root cause**: testpad/testpoint check only checked `val_low`, not `lib_low` or `fp_low`.
  JITX-generated `gen_testpad` components with empty value misclassified as IC.
- **Fix**: (1) Expanded classify_component check to also match `lib_low` and `fp_low`.
  (2) Added "testpad"/"test_pad" to lib_lower check. (3) Added to footprint check in
  analyze_test_coverage.
- **Verified**: All repos pass.

### KH-145 (HIGH): RC filter false positives from opamp feedback R+C pairs

- **File**: `signal_detectors.py` — `detect_rc_filters()`, `analyze_schematic.py` — detector ordering
- **Root cause**: No exclusion for R+C pairs already identified as opamp feedback components.
  Any R+C sharing a signal net matched as RC filter.
- **Fix**: (1) Moved `detect_opamp_circuits()` before `detect_rc_filters()`. (2) Added
  `opamp_circuits` parameter to `detect_rc_filters()`. (3) Built exclusion set from
  feedback_resistor, feedback_capacitor, input_resistor refs. (4) Excluded from both
  resistor loop and capacitor check.
- **Verified**: eurorack-pmod RC filters 15→1 (14 false positives eliminated). All repos pass.

### KH-146 (MEDIUM): JFET classified as mosfet in transistor_circuits

- **File**: `signal_detectors.py` — FET type assignment and P-channel detection
- **Root cause**: Line 2227 hardcoded `"type": "mosfet"` for all FETs. No JFET detection from
  lib_id. "p_jfet" missing from P-channel patterns.
- **Fix**: (1) Added "p_jfet" to P-channel detection. (2) Added JFET keyword detection from
  lib_id/value (jfet, n_jfet, p_jfet, j310, j271, mmbfj, bf545, etc.). (3) Set type to
  "jfet" when keywords match.
- **Verified**: All JFET circuits now correctly typed.

### KH-147 (MEDIUM): LED driver false positives — no net connectivity verification

- **File**: `signal_detectors.py` — `detect_led_drivers()`
- **Root cause**: LED found on other_net wasn't verified to actually have a pin there.
  Resistors >100kΩ (pull-downs, not current limiters) not excluded.
- **Fix**: (1) Verify LED has a pin on other_net via get_two_pin_nets. (2) Reject
  resistors >100kΩ as not current-limiting.
- **Verified**: zx-sizif-512, tokay-lite-pcb, FHNW false positives eliminated.

### KH-148 (MEDIUM): Duplicate design_observations for multi-unit ICs

- **File**: `signal_detectors.py` — `detect_design_observations()` and `detect_power_regulators()`
- **Root cause**: Iterating `ctx.components` which has one entry per schematic unit. A 7-unit
  IC appears 7 times with same reference.
- **Fix**: Pre-filter to unique references using dict comprehension
  `{c["reference"]: c for c in ctx.components if c["type"] == "ic"}.values()` in both
  detect_design_observations (IC loop and reset_pin loop) and detect_power_regulators.
- **Verified**: moco U1 (7 units) now 1 entry each. 3458A-A3-66533 observations reduced.

### KH-149 (MEDIUM): Integrator misclassified as compensator

- **File**: `signal_detectors.py` — opamp feedback search
- **Root cause**: `out_comps & neg_comps` found components on both nets but didn't verify
  direct pin-to-pin connection. Input resistors touching inverting input from a different
  source were falsely matched as feedback resistors. Also, 2-hop search didn't check
  `mid == neg_net` (degenerate case through feedback cap).
- **Fix**: (1) After finding candidates via set intersection, verify with
  `get_two_pin_nets()` that {pin1_net, pin2_net} == {out_net, neg_net}. (2) Added
  `mid == neg_net` skip in 2-hop search.
- **Verified**: VCO U101u2 now correctly `integrator` (was `compensator`). All repos pass.

### KH-150 (MEDIUM): RF matching false positives on non-RF circuits

- **File**: `signal_detectors.py` — `detect_rf_matching()`
- **Root cause**: Triggered on any L+C network near an IC without verifying RF context.
  Ferrite beads, AVCC decoupling, precision input guards all matched.
- **Fix**: (1) Skip components with "ferrite"/"bead"/"emi" in description/keywords/value
  during BFS. (2) After finding target IC, require RF-related keywords. (3) Skip
  ferrite_bead type components.
- **Verified**: 3458A-A3-66533 RF matching 10→0. cubesat-boards geiger 1→0. All repos pass.

### KH-151 (LOW): VC-prefix trimmer capacitor misclassified as varistor

- **File**: `kicad_utils.py` — `classify_component()` type_map
- **Root cause**: No entry for prefix `VC`. Single-char fallback matched `V` → `varistor`.
- **Fix**: Added `"VC": "capacitor"` to type_map.
- **Verified**: Amiga-2000-EATX VC800 now `capacitor` (was `varistor`).

### KH-152 (LOW): Solar cell array falsely detected as key matrix

- **File**: `signal_detectors.py` — `detect_key_matrices()` topology method
- **Root cause**: Solar cells with blocking diodes satisfy switch-diode grid topology.
  Row/col nets are power rails, not scan lines.
- **Fix**: (1) Exclude components with "solar" in lib_id/value. (2) Filter out power rail
  nets from topology-detected row/col nets.
- **Verified**: cubesat-boards ykts-power key_matrices 1→0.

### KH-153 (MEDIUM): Bare integer capacitor values parsed as Farads instead of pF

- **File**: `kicad_utils.py` — `parse_value()`, `kicad_types.py`, `analyze_schematic.py`
- **Root cause**: Bare numbers returned as literal float. For capacitors in KiCad 5 legacy
  schematics, bare integers represent picofarads.
- **Fix**: Added optional `component_type` parameter to `parse_value()`. When
  `component_type == "capacitor"` and result >= 1.0 (bare number path), multiply by 1e-12.
  Updated callers in `kicad_types.py` and `analyze_schematic.py` to pass component type.
- **Verified**: cubesat-boards geiger 9 capacitors now correct pF values.

---

## 2026-03-16 — Batch 13: 8 issues (KH-132–KH-140)

Pin name suffix stripping, gate resistor power rail filtering, 5 already-fixed issues confirmed, 1 not-a-bug closed.

### KH-140 (MEDIUM): Pin name suffix stripping leaves trailing underscores

- **File**: `signal_detectors.py` — 4 sites using `.rstrip("0123456789")`
- **Root cause**: `pname.rstrip("0123456789")` strips trailing digits but leaves underscores,
  so `FB_1` → `FB_` instead of `FB`. Affected 343 pin instances across corpus. Root cause
  of KH-137 (buck classified as LDO) — SW/LX/FB/BOOT pins with `_N` suffixes unrecognized.
- **Fix**: Added `.rstrip("_")` after `.rstrip("0123456789")` at all 4 sites (lines 582, 1129,
  1201, 1979). Also expanded EN pin length check from `<= 3` to `<= 4` for `EN_1`.
- **Verified**: OpenMower 15/15 pass, Glasgow 6/6 pass. 63,876 assertions, 0 failures.

### KH-139 (LOW): Gate resistors enumerated on power rail nets

- **File**: `signal_detectors.py` — `detect_transistor_circuits()` line ~2099
- **Root cause**: When a MOSFET gate net is a power rail, `_get_net_components()` returns all
  components on that rail. Q13-Q16 (BSS138 level shifters on +3V3) each showed 7 gate_resistors.
- **Fix**: When gate net is a power rail, only include resistors connecting gate rail to
  drain/source/ground (actual pull-up/pull-down), not all resistors on the rail.
- **Verified**: OpenMower Q13-Q16 gate_resistors reduced from 7 to 0 (correct — gate tied
  directly to +3V3 with no series resistor). 63,876 assertions, 0 failures.

### KH-137 (MEDIUM): Buck converter classified as LDO — closed as duplicate of KH-140

- Root cause was pin name suffix issue (KH-140): `SW_1` → `SW_` not matching `SW` pin pattern.
  With KH-140 fix, SW/FB/BOOT pins now match correctly, enabling switching topology detection.

### KH-133 (LOW): Feedback network through jumper — closed as not-a-bug

- Original finding claimed R11/R12 voltage divider connects through JP5 to IC3 (MAX20405)
  FB pin. Investigation shows JP5 pin A connects to IC3's **BIAS** pin, not FB.
  MAX20405AFOF is a fixed-output variant — FB_1/FB_2 are internally bonded NC pins.
  The divider is not a feedback network; analyzer is correct.

### KH-132 (MEDIUM): DigiKey property case mismatch — already fixed

- "Digikey" (lowercase k) was already in the property fallback chain at `analyze_schematic.py`
  line 370. OpenMower shows 18/23 dcdc components with populated digikey field.
- Original assertion used unsupported `[*]` path syntax, making it always fail.

### KH-134 (LOW): Capacitive feedback — already fixed by KH-020

- C7 (22pF) in Wien bridge oscillator IS detected as `feedback_capacitor` in opamp_circuits.
  KH-020 added capacitive feedback recognition. Assertion checked `feedback_networks` (different
  section) using wrong project path.

### KH-135 (MEDIUM): Value parser prefix-first notation — already fixed

- Prefix-first notation (u1, n47, p33) already implemented in `parse_value()`.
  73 Glasgow capacitors with value "u1" all have `parsed_value: 1e-07`.
- Original assertion used unsupported `[*]` path syntax.

### KH-136 (CRITICAL): +3V3 power rail missing — already fixed by KH-131

- Root cause was KH-131 power symbol classification regression. +3V3 now has 151 pins in
  Glasgow output. All power rails correctly resolved.

### KH-138 (LOW): Bootstrap cap LC filter FP — already fixed

- Bootstrap cap exclusion code at lines 576-588 correctly filters BST/BOOT pin circuits.
  OpenMower has 0 LC filters (no false positive).

---

## 2026-03-16 — Batch 12: 1 issue (KH-131)

Power symbol classification regression fix.

### KH-131 (CRITICAL): Power symbols with in_bom=yes misclassified, breaking net naming

- **Files**: `kicad_utils.py` — `classify_component()`
- **Root cause**: KH-080 fix added `and not in_bom` to the power symbol check, but standard KiCad power symbols (`power:+3V3`, `power:GND`, etc.) have `in_bom yes` in their s-expression. This caused them to fall through to prefix lookup (`#PWR` → `power_flag`) instead of `power_symbol`, breaking net naming. Power rails became `__unnamed_*` nets, cascading into: inflated net counts, missed decoupling detection, missed design observations.
- **Fix**: Trust the lib_symbol `(power)` flag unconditionally (`if is_power: return "power_symbol"`). Only apply the `in_bom` guard to `lib_id.startswith("power:")` without the `(power)` flag (the KH-080 case: real components like DD4012SA placed in the power library).
- **Verified**: 6,827/6,827 schematics pass. DD4012SA still classified as `ic`. Assertions: 64,431 total, 99.1% pass rate (up from 98.6%). 520 repos promoted with corrected baselines.

---

## 2026-03-16 — Batch 11: 6 issues (KH-125 through KH-130)

Op-amp legacy fallback, protection device dedup, integrated LDO exclusion, 3 false findings closed.

### KH-125 (HIGH): Op-amp / instrumentation amplifier circuits not detected on legacy format

- **Files**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: KiCad 5 legacy format components have `pins: []`. The op-amp detector iterates `ctx.pin_net` to find +IN/-IN/OUT pin names. Without pin data, no pins found → no op-amps detected, even though keyword match succeeds.
- **Fix**: (1) Added legacy format fallback: if no op-amp pins found (`pos_in`, `neg_in`, `out_pin` all None) but keyword matched, add entry with `configuration: "unknown"`. (2) Expanded `opamp_value_keywords` with `"ina2"` (INA210/219/226 current sense amps) and `"ina8"` (INA821/826/828 instrumentation amps). (3) Added `"instrumentation"` to description keyword check.
- **Verified**: DEVLPR: 5 op-amps detected (3x OPA187, 1x OPA2375, 1x INA821) — was 0. 44/44 assertions pass.

### KH-126 (MEDIUM): Multi-pin TVS/ESD arrays overcounted as protection devices

- **Files**: `signal_detectors.py` — `detect_protection_devices()`
- **Root cause**: Two locations iterate per unique protected net, creating one entry per net: multi-pin TVS diodes (>2 pins, is_tvs) and IC-based ESD protection (type "ic"). A USBLC6-2SC6 protecting 2 data lines creates 2+ entries with the same ref.
- **Fix**: In both locations, replaced per-net loop with single entry per component. Collects all protected nets into `protected_nets` list. `protected_net` (singular) set to first net alphabetically for backward compatibility.
- **Verified**: SparkFun_GNSS_mosaic-T: 10 protection devices (was ~40). pygmy: USBLC6-2SC6 = 1 entry (was 4). 30/39 assertions pass (9 pre-existing failures unrelated).

### KH-127 (MEDIUM): USB hub IC VREG pin falsely detected as LDO regulator

- **Files**: `signal_detectors.py` — `detect_integrated_ldos()`
- **Root cause**: Pin name "VREG" matches LDO output heuristics without verifying the IC is actually a voltage regulator. CY7C65642 USB hub has a VREG pin for internal regulator decoupling.
- **Fix**: Added `_non_reg_ic_keywords` exclusion tuple in `detect_integrated_ldos()`. Checks lib_id+value against USB hub, FPGA, MCU, PHY, codec, and audio IC families. Skips matched ICs before pin scan.
- **Verified**: keypad KP08Hub: CY7C65642 (U3) no longer in power_regulators. 50/63 assertions pass (13 pre-existing failures unrelated).

### KH-128 (MEDIUM): Crystal not detected when value field is missing — CLOSED (false finding)

- **Resolution**: Not a bug. Crystal IS detected. `PCB_schematic_KiCad/pcb_pcb.kicad_sch.json` → `crystal_circuits` contains Y1 with `value: "Crystal"`, `frequency: null`, `load_caps: []`. Null frequency is expected when value is a generic word ("Crystal"), not a parseable frequency string. The finding misinterpreted `frequency: null` as "not detected".

### KH-129 (HIGH): Multi-project repos inflate component counts — CLOSED (false finding)

- **Resolution**: Not a bug. `jamma_raspi.kicad_sch` has `(property "Sheetfile" "jamma_raspi_ios.kicad_sch")` — a legitimate KiCad hierarchical sheet reference within the same project. Sheet 0 has 91 components, sheet 1 has 56 (sub-sheet). `total_components: 119` (after power symbol filtering). The analyzer correctly follows the project's own hierarchy; this is not cross-project inclusion.

### KH-130 (LOW): Test pads from gen_testpad library not recognized — CLOSED (already working)

- **Resolution**: Not a bug. Root schematic `CAD.kicad_sch` output has 18 `type: test_point` components with `lib=gen_testpad`. Classification works via value check (`"testpad" in "gen_testpad"`). The finding referenced sub-sheet CAD-2, but test pads are on CAD-5 — root output correctly includes them.

### Regression results

- DEVLPR: 44/44 assertions pass
- SparkFun_GNSS_mosaic-T: 30/39 pass (9 pre-existing failures)
- keypad: 50/63 pass (13 pre-existing failures)
- pygmy: 44/54 pass (10 pre-existing failures)
- All analyzer runs: 100% pass rate, 0 crashes

---

## 2026-03-16 — Batch 10: 9 issues (KH-116 through KH-124)

RC/LC filter fixes, classification corrections, keyword expansion, varistor detection, BMS refinement.

### KH-116 (MEDIUM): RC filter false positive when output==ground net

- **Files**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: `ground_net` assignment defaulted to `r_other` when `c_other` wasn't ground, making `output_net == ground_net` for "RC-network" type filters.
- **Fix**: Changed `ground_net` to use `c_other` (capacitor's far end) when neither end is ground. Also added `r_other == c_other` skip for truly shorted cases.
- **Verified**: CoffeeRoaster R1/C1 and R2/C2 now have distinct output/ground nets. 53/53 assertions pass.

### KH-117 (LOW): Varistors not detected as protection devices

- **Files**: `signal_detectors.py` — `detect_protection_devices()`
- **Root cause**: `get_two_pin_nets()` hardcodes pin numbers "1"/"2", but Eagle-imported varistors use "P$1"/"P$2"/"P$3" pin names.
- **Fix**: Added fallback in varistor loop: if `get_two_pin_nets` fails, scan all `pin_net` entries for the component and collect unique nets.
- **Verified**: robocup-pcb RV1 (500V PVG3 varistor) now detected as protection device. 91/91 assertions pass.

### KH-118 (MEDIUM): TPLP5907MFX-3.3 linear regulator not detected

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: "TPLP" not in regulator keyword list.
- **Fix**: Added "tplp" and "hx630" to `reg_lib_keywords`.
- **Verified**: pcb_kicad_rf_scom_bk48_v3 U19 TPLP5907MFX-3.3 now detected as LDO. 38/38 assertions pass.

### KH-119 (HIGH): LC filter overcounting in RF designs

- **Files**: `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: Every L-C pair sharing a net counted as a filter. No topology validation; no fanout limit. RF matching networks triggered massive overcounting.
- **Fix**: (1) Added shared_net fanout limit (>6 pins → skip). (2) Post-processing: if an inductor has LC pairings on both its nets (matching network pattern), keep only the largest-capacitance entry per side.
- **Verified**: pcb_kicad_rf_scom_bk48_v3 LC filters reduced from 23 to 14. L7 reduced from 4 entries to 2. 38/38 assertions pass.

### KH-120 (MEDIUM): RF transceiver ICs not detected in RF chains

- **Files**: `signal_detectors.py` — `detect_rf_chains()`
- **Root cause**: (1) BK4819 and CMX994 not in transceiver keyword list. (2) RF chain detection only searched `type == "ic"`, missing non-standard reference ICs classified as "other".
- **Fix**: (1) Added "bk4819", "cmx994", "cmx99", "si4463", "si4432", "a7105" to transceiver keywords. (2) Changed type check to `c["type"] in ("ic", "other")`.
- **Verified**: BK4819QN32SC and CMX994E1 both detected as RF transceivers. 38/38 assertions pass.

### KH-121 (MEDIUM): RC filter bidirectional traversal duplicates

- **Files**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: Same R-C pair found from both net endpoints, creating duplicate entries with swapped input/output.
- **Fix**: Track `seen_rc_pairs` as `set[frozenset[str]]`. Skip if R-C pair already processed.
- **Verified**: DIY-LAPTOP Power Supply sheet: 0 duplicate R-C pairs (was >0 before). 176/176 assertions pass.

### KH-122 (MEDIUM): SK6812/WS2812 addressable LEDs misclassified as diodes

- **Files**: `kicad_utils.py` — `classify_component()`; `signal_detectors.py` — `detect_addressable_leds()`
- **Root cause**: D-prefix components classified as "diode" before reaching SK6812 keyword checks. Custom library `tm_leds:SK6812MINI-E` lacks "led" token needed by the generic LED regex.
- **Fix**: (1) Added addressable LED keyword check in `classify_component()` diode block. (2) `detect_addressable_leds()` now also searches "diode" type components as fallback.
- **Verified**: kuro65: all 69 SK6812MINI-E components now type "led" (was "diode"). 1 addressable LED chain detected. 43/43 assertions pass.

### KH-123 (LOW): MCP73871 battery charger misclassified as BMS

- **Files**: `signal_detectors.py` — `detect_bms_systems()`
- **Root cause**: BMS keyword list included single-cell charger ICs (TP4056, MP2639, MCP738xx) that handle charging only, not multi-cell monitoring/balancing.
- **Fix**: Removed single-cell charger keywords from `bms_ic_keywords`. Only multi-cell BMS/AFE ICs remain (BQ769xx, LTC681x, ISL942x, MAX172x).
- **Verified**: PCB-Modular-Multi-Protocol-Hub: 0 BMS systems (was 1 false positive for MCP73871). 85/85 assertions pass.

### KH-124 (HIGH): PMIC regulators not detected (AXP803, MT3608)

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: (1) "AXP" and "MT36" not in keyword list. (2) KiCad 5 legacy format components have 0 pins, causing early skip before keyword check.
- **Fix**: (1) Added "axp", "mt36", "pmic", "dd40", "ip51" to `reg_lib_keywords`. (2) Added keyword-only fallback for pin-less ICs: if no FB/SW/VOUT pins found but component matches PMIC keywords, add as "unknown" topology entry.
- **Verified**: DIY-LAPTOP Power Supply: AXP803 and MT3608 both detected (was 0). 176/176 assertions pass.

---

## 2026-03-16 — Batch 9: 12 issues (KH-078, KH-080, KH-081, KH-082, KH-085, KH-087, KH-098, KH-105, KH-112, KH-113, KH-114, KH-115)

Crash fix, classification corrections, false positive suppression, detection expansion, chain merging, rail tracing.

### KH-078 (MEDIUM): `build_net_map()` unhashable list crash

- **Files**: `analyze_schematic.py` — `extract_labels()` and `build_net_map()`
- **Root cause**: Malformed s-expression yields list instead of string for label name. Flows into dict key as unhashable type.
- **Fix**: Defensive `isinstance(name, list)` coercion in both `extract_labels()` (line 597) and `build_net_map()` (line 901).
- **Verified**: All test repos pass (kicad_schemes not checked out for direct verification).

### KH-080 (MEDIUM): Power symbol despite in_bom=yes

- **Files**: `kicad_utils.py` — `classify_component()`; `analyze_schematic.py` — call site
- **Root cause**: `classify_component()` returned `"power_symbol"` for `lib_id.startswith("power:")` without checking `in_bom`. DD4012SA buck converter (lib_id=`power:DD4012SA`, in_bom=yes) became invisible.
- **Fix**: Added `in_bom` parameter to `classify_component()`. Guard: `not in_bom` before returning `"power_symbol"`. Call site passes `in_bom=in_bom`.
- **Verified**: ethersweep DD4012SA (U4) now type=`ic`. 10/10 schematics pass. Baselines unchanged (0/17 diffs).

### KH-081 (MEDIUM): Current sense FPs on Ethernet termination

- **Files**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: No IC exclusion mechanism. Ethernet PHYs (W5500) and RJ45 modules (HR911105A) falsely match as current sense ICs.
- **Fix**: Added `_SENSE_IC_EXCLUDE` frozenset with Ethernet PHY/RJ45/MagJack families. Applied in both Pass 1 and Pass 2.
- **Verified**: ethersweep current_sense=0 (was 3 false positives). 10/10 pass.

### KH-082 (MEDIUM): TVS IC-packaged protection devices not detected

- **Files**: `signal_detectors.py` — `detect_protection_devices()`
- **Root cause**: ESD IC keyword list missed TVS/ECMF/CDSOT families; no `Power_Protection:` library check.
- **Fix**: Added `tvs18`, `tvs1`, `ecmf`, `cdsot`, `smda`, `rclamp` to keywords. Added `is_protection_lib` check for `power_protection:` in lib_id.
- **Verified**: ISS-PCB 181/181 pass.

### KH-085 (MEDIUM): RF chain keyword lists too narrow

- **Files**: `signal_detectors.py` — `detect_rf_chains()`
- **Root cause**: Missing IC families (ADRF, ADMV, MAAM, HMC3xx) and missing categories (attenuators, couplers, power detectors, frequency multipliers).
- **Fix**: Expanded switch keywords (+`adrf`, `hmc3`), amp keywords (+`maam`, `admv`). Added 4 new category tuples with classification loops, output dict entries, and `_rf_role()` mappings.
- **Verified**: vna 229/229 pass.

### KH-087 (MEDIUM): Switching regulator output_rail missing

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Output rail through inductor only traced before sanitization; input rail not traced through ferrite beads.
- **Fix**: After GND sanitization, retry output_rail trace through inductor if topology=switching and no output_rail. Added ferrite bead input_rail tracing (skip same inductor).
- **Verified**: Power_HW 114/114 pass. ISS-PCB 181/181 pass.

### KH-098 (MEDIUM): Flyback diode drain-to-supply not detected

- **Files**: `signal_detectors.py` — MOSFET analysis flyback check
- **Root cause**: Detector only checked drain-to-source topology, missing standard low-side switch flyback (drain to supply rail).
- **Fix**: After existing drain-to-source check, added drain-to-supply check: if diode's other pin is a power net (not GND), mark as flyback.
- **Verified**: KiDiff 16/16 pass. Note: KiDiff test cases use connectors instead of power symbols, so flyback detection requires named power rails to trigger.

### KH-105 (MEDIUM): 3-resistor feedback networks not handled

- **Files**: `signal_detectors.py` — new `_merge_series_dividers()`; `analyze_schematic.py` — integration
- **Root cause**: Pairwise divider detection can't see series resistors in feedback networks. R56+R59 (20.15k combined) treated as separate, yielding wrong Vout.
- **Fix**: Added `_merge_series_dividers()` post-processor. Identifies pass-through nodes (2 resistors, no active pins), extends chains, combines series resistances, recalculates ratios.
- **Verified**: Ventilator 30/30 pass. No baseline changes in tested repos.

### KH-112 (LOW): Ferrite bead impedance notation parsed as inductance

- **Files**: `kicad_utils.py` — `parse_value()` and `classify_component()`
- **Root cause**: "600R/200mA" → split("/") → "600R" → trailing R multiplier → 600.0. Used as inductance in LC filter detection.
- **Fix**: Early guard in `parse_value()`: regex `\d+[Rr]\s*[/@]\s*\d` returns None. In `classify_component()`: same regex reclassifies inductor as ferrite_bead.
- **Verified**: All test repos pass (panstamp-nrg3 not checked out).

### KH-113 (LOW): RS485 transceiver current sense FP

- **Files**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: LT1785 RS485 transceiver matched as current sense IC (no exclusion list).
- **Fix**: Added RS-485/RS-232/UART transceiver families to `_SENSE_IC_EXCLUDE` (lt178, max48, sn65hvd, st348, adm281/485/491, sp338/339, isl3, iso15, max23/31/32).
- **Verified**: Gas-sens_Rs-485 10/10 pass.

### KH-114 (LOW): Active oscillators treated as passive crystals

- **Files**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Passive crystal loop processes all `type == "crystal"` components including active oscillators with 4+ pins, producing nonsensical load capacitance.
- **Fix**: Before passive crystal loop body, check if component has >=4 pins AND has a VCC/VDD power pin (by name or connected net). If so, skip to active oscillator section.
- **Verified**: explorer 4/4 pass.

### KH-115 (LOW): Multi-tap attenuator spurious dividers

- **Files**: `signal_detectors.py` — `_merge_series_dividers()` (same as KH-105)
- **Root cause**: Pairwise detection generates all combinations from 3+ resistor chains.
- **Fix**: Same `_merge_series_dividers()` function. Pass-through nodes are detected and chains merged. Sub-pair dividers marked `suppressed_by_chain: True`.
- **Verified**: Ventilator 30/30 pass.

---

## 2026-03-15 — Batch 8: 15 issues (KH-090, KH-097, KH-099, KH-100, KH-101, KH-102, KH-103, KH-104, KH-106, KH-107, KH-108, KH-109, KH-110, KH-111)

Lookup table additions, exclusion lists, classification fixes, regex fixes, and defensive coding.

### KH-103 (MEDIUM): Regulator Vref lookup missing several ICs

- **Files**: `kicad_utils.py` — `_REGULATOR_VREF` table
- **Root cause**: LMR38010, XL7015, TPS631000, AP7365 not in Vref lookup table, falling back to wrong heuristic values.
- **Fix**: Added `LMR380: 1.0`, `XL70: 1.25`, `TPS6310: 0.5`, `AP736: 0.8` to `_REGULATOR_VREF`.
- **Verified**: All entries match datasheet values (SNVSB89, SLVSEK5, XL7015 datasheet, AP7365 datasheet).

### KH-109 (MEDIUM): Charger ICs not detected in BMS systems

- **Files**: `signal_detectors.py` — `detect_bms_systems()` keyword list
- **Root cause**: `bms_ic_keywords` tuple only had multi-cell BMS ICs; single-cell charger families missing.
- **Fix**: Added `mcp738`, `bq2104`, `bq2405`, `bq2407`, `ltc405`, `max1555`, `max1551` to keyword list.
- **Verified**: Covers MCP73831/MCP73833, BQ21040, BQ24050/BQ24070, LTC4054, MAX1555/MAX1551 families.

### KH-108 (MEDIUM): LM66200 ideal diode controller misclassified as LDO

- **Files**: `signal_detectors.py` — `_power_mux_exclude` tuple
- **Root cause**: LM66200 has VIN/VOUT pins matching regulator pattern but is an ideal diode OR controller.
- **Fix**: Added `lm6620`, `lm6610`, `ltc435`, `ltc430` to `_power_mux_exclude`.
- **Verified**: SparkFun_IoT_RedBoard-RP2350 — LM66200 no longer in power_regulators output.

### KH-100 (LOW): WiFi/BT modules classified as power regulators

- **Files**: `signal_detectors.py` — `_non_reg_exclude` tuple
- **Root cause**: AP6236 has filter inductor on power pin, triggering switching regulator detection.
- **Fix**: Added `ap62`, `ap63`, `esp32`, `esp8266`, `cyw43`, `wl18` to `_non_reg_exclude`.
- **Verified**: OtterCam-s3 — AP6236 no longer in power_regulators output.

### KH-106 (MEDIUM): MX key switches misclassified as relays

- **Files**: `kicad_utils.py` — `classify_component()` relay override + lib_lower switch detection
- **Root cause**: K prefix maps to "relay" in type_map. MX switches use K prefix with lib_id containing "MX_Alps_Hybrids". No relay→switch override existed.
- **Fix**: (1) Added relay→switch override in full-prefix match section checking for MX/Cherry/Kailh/Gateron/Alps in lib_low/val_low. (2) Added same patterns to lib_lower switch detection before relay check.
- **Verified**: Mechanical-Keyboard-PCBs — all 91 MX switches now type=switch (was relay). Updated assertion files for pok3r, steamvan, vortex_tester repos.

### KH-110 (LOW): Audio jack components misclassified as ICs

- **Files**: `kicad_utils.py` — `classify_component()` connector detection
- **Root cause**: Connector_Audio library and PJ-3xx part number patterns not in connector classification.
- **Fix**: Added `connector_audio`/`audio_jack` lib_lower checks and `PJ-3`/`SJ-3`/`MJ-3` value prefix checks.
- **Verified**: Pattern matches standard audio connector part numbering (PJ-327E-SMT, etc.).

### KH-111 (LOW): Common-mode choke misclassified as transformer

- **Files**: `kicad_utils.py` — `classify_component()` transformer override
- **Root cause**: T prefix maps to transformer. RFCMF/ACM/DLW/CMC components had no override.
- **Fix**: Added CMC exclusion before transformer return: checks val_low for `cmc`, `common mode`, `common_mode`, `rfcmf`, `acm`, `dlw` and lib_low for `common_mode`, `cmc`, `emi_filter`.
- **Verified**: SparkFun_GNSS_Flex_pHAT — RFCMF1220100M4T now type=inductor (was transformer).

### KH-097 (MEDIUM): CSYNC nets misclassified as chip_select

- **Files**: `analyze_schematic.py` — net classification
- **Root cause**: "CS" substring match in chip_select classification catches CSYNC/CSYNC_IN/CSYNC_OUT video sync signals.
- **Fix**: Added sync signal exclusion: if net name contains CSYNC/HSYNC/VSYNC/SYNC, classify as "signal" instead of "chip_select".
- **Verified**: Unit test confirms CSYNC_IN→signal, SPI_CS→chip_select (no false exclusions).

### KH-099 (MEDIUM): I2S audio bus misidentified as I2C

- **Files**: `signal_detectors.py` — I2C bus detection
- **Root cause**: I2S data pin names (SDAT) contain "SDA" as substring, matching `\bSDA\b` regex.
- **Fix**: (1) Added I2S keyword exclusion: skip nets with SDAT, LRCK, BCLK, WSEL. (2) Tightened SDA regex to `\bSDA\b(?!T)` (negative lookahead for 'T').
- **Verified**: Prevents SDAT from matching SDA while preserving standard I2C SDA detection.

### KH-101 (LOW): sexp_parser crashes on truncated PCB files

- **Files**: `sexp_parser.py` — `_parse_tokens()`
- **Root cause**: No bounds check before `tokens[pos]` access. Truncated files with unbalanced parens cause IndexError.
- **Fix**: Added `if pos >= len(tokens): raise ValueError(...)` before first token access.
- **Verified**: OnBoard — 235/237 pass (99.2%). 2 truncated files now get descriptive ValueError instead of IndexError crash.

### KH-102 (LOW): extract_silkscreen crashes on list-typed footprint value

- **Files**: `analyze_pcb.py` — `extract_silkscreen()` footprint iteration
- **Root cause**: Some PCB files have list-typed value fields in footprint data. `.lower()` called on list raises AttributeError.
- **Fix**: Added defensive type check: if value is list, extract `str(val[1])` or empty string.
- **Verified**: TI92-revive — both PCB files now pass (was crash). 2/2 pass.

### KH-107 (MEDIUM): Crystal oscillator load components as standalone RC filters

- **Files**: `signal_detectors.py` — `detect_rc_filters()` signature + exclusion; `analyze_schematic.py` — call site
- **Root cause**: Crystal feedback resistor + load capacitor pairs matched RC filter pattern. Existing post-filter in analyze_schematic.py was redundant but didn't handle all cases.
- **Fix**: (1) Added `crystal_circuits` parameter to `detect_rc_filters()`. (2) Built crystal component exclusion set (crystal refs, load cap refs, feedback resistor refs). (3) Skip R and C components in crystal_refs during filter detection. (4) Updated call site to pass crystal_circuits.
- **Verified**: SparkFun_IoT_RedBoard-RP2350 — no crystal components in RC filters. 92 assertion files updated for reduced (correct) RC filter counts across corpus.

### KH-090 (LOW): LDO inverting flag incorrect for fixed-output LDOs

- **Files**: `signal_detectors.py` — regulator detection, after inverting keyword check
- **Root cause**: Inverting keyword check matched on part number substrings even for fixed-output LDOs that are clearly non-inverting.
- **Fix**: Added check: if topology is "LDO" and no FB pin exists, delete the `inverting` flag.
- **Verified**: Fixed-output LDOs (TLV757xx family) no longer incorrectly marked as inverting.

### KH-104 (MEDIUM): Regulator pin mapping GND as input/output rail

- **Files**: `signal_detectors.py` — regulator detection, after rail assignment
- **Root cause**: Pin-to-net mapping sometimes assigns GND net to input_rail or output_rail when pin names don't match expected patterns.
- **Fix**: Added GND sanity filter: if input_rail or output_rail is a GND net (via `_is_ground_name()`), set to None.
- **Verified**: Prevents nonsensical GND power rails in regulator output.

### Regression results

- Full corpus: 6,827 schematic files, 100% analyzer pass rate (0 regressions)
- OnBoard PCB: 235/237 pass (99.2%), 2 truncated files get proper error
- TI92-revive PCB: 2/2 pass (was crash)
- Assertions: 64,399 total, 63,846 passed, 38 failed (pre-existing), 515 errors, 99.1% pass rate
- 145 assertion files updated for corrected RC filter / power regulator / switch counts

---

## 2026-03-15 — KH-091, KH-092, KH-093, KH-094, KH-095, KH-096 (batch 7, 6 issues)

Component classification fixes in `kicad_utils.py classify_component()`.
Source repos verified: commodorelcd, iMX8MP-SOM-EVB, ESP32-S3-DevKit-LiPo, NB-IoT,
Castor_and_Pollux, NUS-CPU-03-Nintendo-64-Motherboard

### KH-091 (HIGH): CR-prefix diodes misclassified as capacitor

- **Files**: `kicad_utils.py` — `classify_component()` type_map
- **Root cause**: CR (IPC-2612 standard diode/rectifier prefix) was not in type_map,
  so it fell to single-char fallback where prefix[0]='C' → capacitor.
- **Fix**: Added `"CR": "diode"` to type_map.
- **Verified**: commodorelcd: 15 CR-prefix components now classified as diode (was capacitor).

### KH-092 (HIGH): T-prefix transistors classified as transformer

- **Files**: `kicad_utils.py` — `classify_component()` transformer override
- **Root cause**: T→transformer in type_map. KH-079 added lib_id overrides but only
  for "mosfet/fet/transistor/amplifier" keywords. Custom libs with Q_NPN_BEC or
  "Transistors" footprint were missed.
- **Fix**: (1) Added "bjt", "q_npn", "q_pnp", "q_nmos", "q_pmos" to transformer
  override keyword list. (2) Added footprint check (fp_low) to transformer override.
  (3) Changed return from "ic" to "transistor" for transistor-related overrides.
- **Verified**: iMX8MP T1/T2 (BC817-40) → transistor (was transformer).
  ESP32-S3-DevKit-LiPo T1/T2 (BC817-40) → transistor. NB-IoT T1-T5 → transistor.

### KH-093 (HIGH): VR-prefix regulators classified as varistor

- **Files**: `kicad_utils.py` — `classify_component()` varistor override, single-char fallback
- **Root cause**: VR prefix falls to single-char V→varistor. Custom libs like
  "iMX8MPLUS-SOM-EVB_Rev_B:AMS1117-ADJ" don't contain "regulator" keyword.
- **Fix**: (1) Added footprint-based check ("regulator" in fp_low) to varistor override.
  (2) Added value-based check for known regulator families (ams1117, lm78, lm317, etc.).
  (3) Added same checks to single-char fallback varistor override.
- **Verified**: iMX8MP VR1/VR2 (AMS1117) → ic (was varistor).

### KH-094 (MEDIUM): Potentiometers (RV-prefix) classified as varistor

- **Files**: `kicad_utils.py` — `classify_component()` varistor override
- **Root cause**: RV→varistor in type_map. Override checked "r_pot" and "potentiometer"
  but missed custom libs like "winterbloom:Eurorack_Pot" where only "pot" appears.
- **Fix**: Broadened potentiometer check to include "pot" in lib_low alongside existing
  "r_pot" and "potentiometer" checks.
- **Verified**: Castor_and_Pollux RV1-RV5 → resistor (was varistor).

### KH-095 (MEDIUM): D_TVS_Filled classified as LED

- **Files**: `kicad_utils.py` — `classify_component()` diode→LED override
- **Root cause**: `"led" in lib_low` matched "fi**led**" substring in "Device:D_TVS_Filled".
- **Fix**: Changed from substring check to regex with negative lookbehind/lookahead:
  `re.search(r'(?<![a-z])led(?![a-z])', ...)` ensures "led" appears as a standalone token.
- **Verified**: Castor_and_Pollux D3-D6 (D_TVS_Filled) → diode (was led).

### KH-096 (MEDIUM): Ferrite beads (FerriteBead) classified as fuse

- **Files**: `kicad_utils.py` — `classify_component()` lib_id section + single-char fallback
- **Root cause**: FIL prefix not in type_map, fell to single-char F→fuse. No ferrite bead
  check in fuse override or lib_id fallback section.
- **Fix**: (1) Added "ferritebead"/"ferrite_bead" check in lib_id fallback section before
  inductor check. (2) Added "ferrite"/"bead" check in single-char fallback fuse override.
- **Verified**: NUS-CPU-03 FIL1-FIL8 → ferrite_bead (was fuse).

### Regression results

- Full corpus: 6,827 files, 100% analyzer pass rate
- Assertions: 55,245 total, 54,455 passed (98.6%) — no regression vs baseline
- 23 repos reseeded assertions to reflect corrected classifications
- Drift check: 0 regressions, 2 possibly_fixed findings (FND-183)

---

## 2026-03-15 — KH-079, KH-083, KH-084, KH-086, KH-088, KH-089 (batch 6, 6 issues)

Source repos verified: mutable_eurorack_kicad (102), Power_HW (114), openwrt-one (9),
ISS-PCB (181), cnhardware (77), ethersweep (10), vna (229)

### KH-088 (CRITICAL): Eagle-import empty Value cascading power symbol net failure

- **Files**: `analyze_schematic.py` — `extract_lib_symbols()`, `extract_components()`
- **Root cause**: Eagle-imported KiCad schematics have empty instance Value for power
  symbols. The analyzer used only the instance Value, so all power/ground connections
  merged into a single empty-string net. Cascaded to break power rails, voltage
  dividers, RC filters, and op-amp configurations.
- **Fix**: (1) Store `lib_value` from lib_symbol definition in `extract_lib_symbols()`.
  (2) In `extract_components()`, fall back to lib_symbol Value when instance Value is
  empty.
- **Verified**: mutable_eurorack_kicad Ripples: power rails now GND/VCC/VEE (was empty
  mega-net). All 102 files pass.

### KH-083 (CRITICAL): lib_name/lib_id mismatch causes 0-pin parsing in KiCad 7+

- **Files**: `analyze_schematic.py` — `extract_components()`, `compute_pin_positions()`
- **Root cause**: KiCad 7+ uses `(lib_name X)` when the local symbol name differs from
  the library's `lib_id`. `compute_pin_positions()` only looked up by `lib_id`, missing
  symbols keyed by their raw name (e.g., `TPS2116DRLR_1`).
- **Fix**: (1) Extract `lib_name` from symbol instances. (2) Try `lib_name` first, then
  `lib_id` as lookup key in `compute_pin_positions()` and `classify_component()` sym_def
  lookup.
- **Verified**: Power_HW GEODE rev2 TPS2116DRLR: 8 pins (was 0), full IC analysis.
  PMV90ENER: 3 pins with gate/drain/source nets. All 114 files pass.

### KH-079 (HIGH): Ref prefix single-char fallback overrides lib_id/footprint

- **Files**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Single-char prefix fallback (T→transformer, F→fuse, etc.) returned
  without checking lib_id/footprint/value for contradicting evidence.
- **Fix**: Added `footprint` parameter to `classify_component()`. After single-char
  fallback match, check lib_id/footprint/value keywords to override: transformer→test_point
  (TP footprint), transformer→diode (TVS), fuse→fiducial, fuse→filter (EMI),
  capacitor→mechanical (shield clips), switch→mounting_hole (standoffs),
  ic→transistor (BJT), ic→transformer.
- **Verified**: openwrt-one TPD → test_point (was transformer). All 7 repos pass.

### KH-086 (HIGH): SPI nets falsely detected as I2C via pin-name fallback

- **Files**: `analyze_schematic.py`, `signal_detectors.py`
- **Root cause**: I2C detection scanned all nets for SDA/SCL pins but didn't exclude
  SPI nets. Sensors with dual-function SDA/SCL pin names in SPI mode triggered false
  I2C detection.
- **Fix**: Added SPI keyword exclusion (SPI, MOSI, MISO in net name) to three I2C
  detection paths: net-name-based, pin-name-based, and observation detector.
- **Verified**: ISS-PCB TARS-MK4-FCB: SNS_SPI_* nets no longer reported as I2C.
  All 181 ISS-PCB files pass.

### KH-089 (HIGH): Regulator detection false positives from non-regulator ICs

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Any IC with VOUT/OUT/FB/SW pins passed the regulator gate. Title
  blocks (0 pins), flash chips, RTCs, EEPROMs, logic buffers leaked through.
- **Fix**: Added early exclusions: (1) Skip components with no pins. (2) Skip known
  non-regulator IC families (eeprom, flash, rtc, uart, buffer, logic, w25q, at24c,
  ht42b, ch340, cp210, ft232, 74lvc, 74hc).
- **Verified**: openwrt-one regulators 40→25 (title blocks and non-regulators excluded).

### KH-084 (HIGH): Voltage divider/feedback not linked to parent regulator

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: (1) Switching regulator output_rail missing — no trace through inductor
  from SW pin. (2) FB-at-top divider topology not recognized.
- **Fix**: (1) After finding inductor on SW net, trace through to find output rail net.
  (2) After building regulator list, cross-reference voltage divider top_nets with
  regulator FB pins to detect FB-at-top topology.
- **Verified**: Power_HW LMR36506: output_rail now traced through inductor. All 7 repos
  pass with 0 regressions.

### Regression results

- All analyzer runs pass: mutable_eurorack_kicad (102), Power_HW (114), openwrt-one (9),
  ISS-PCB (181), cnhardware (77), ethersweep (10), vna (229)
- 0 regressions, multiple `now_detected` and `possibly_fixed` across all 7 repos
- 66 findings promoted to assertions (119 confirmed, 44 new)
- Assertion corpus: 55,276 total, 54,502 passed (98.6%)

---

## 2026-03-15 — KH-016, KH-026, KH-048, KH-052, KH-064, KH-066, KH-067, KH-073 (batch 5, 8 issues)

Source repos verified: ESP32-P4-PC, ESP32-EVB (12 revisions), ESP32-GATEWAY (9 revisions),
daisho (60 files), hackrf (23), splitflap (8), Voron-Hardware (29), icebreaker (15), OnBoard

### KH-016 (HIGH): Legacy wire-to-pin coordinate matching broken

- **Files**: `analyze_schematic.py` — `_STANDARD_LIB_PINS`, `_snap_pins_to_wires()`, cache lib suffix map
- **Root cause**: Three compounding issues: (1) `_STANDARD_LIB_PINS` had pin offsets at ±40 mils
  (body end) instead of ±150 mils (connection endpoint where wires attach). Surveyed 1292 real
  cache.lib files to find correct positions. (2) Cache libs store symbols as `Library_Symbol`
  but component references use `Library:Symbol` — suffix lookup was missing. (3) When pin positions
  are slightly off due to KiCad version differences, no snap-to-wire fallback existed.
- **Fix**: (1) Rewrote entire `_STANDARD_LIB_PINS` with correct offsets (±150 mils for 2-pin passives,
  ±200/250 mils for connectors, etc.) and added ~60 new symbols including `CONN_01X01` through
  `CONN_01X20`, `CONN_02X02` through `CONN_02X20`, transistors, crystals, switches. (2) Added
  `_cache_suffix_map` for resolving bare symbol names to prefixed cache lib names. (3) Added
  `_snap_pins_to_wires()` post-processing step that snaps unmatched pin positions to nearby
  wire endpoints (max 12mm, direction-aware).
- **Verified**: daisho power.sch orphan rate 97.5% → 53.9%, multi-pin nets 4 → 24.
  ESP32-C3-DevKit-Lipo: ICs with power rails 0 → 2. All 60 daisho files pass.

### KH-026 (HIGH): Hierarchical net merging for multi-instance sub-sheets

- **Files**: `analyze_schematic.py` — hierarchical label handling in `build_net_map()`
- **Root cause**: Already fixed in a prior batch. Instance-path prefixing exists at
  analyze_schematic.py with `_sheet_uuid` tagging for per-instance net namespacing.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: cynthion type_c.kicad_sch instantiated 3 times. CC1/CC2 nets from different
  USB-C port instances are properly namespaced with different UUID paths. Nets are electrically
  isolated per instance.

### KH-048 (MEDIUM): Key matrix detection fails on non-standard net names

- **Files**: `signal_detectors.py` — `detect_key_matrices()`
- **Root cause**: Already fixed in a prior batch. Both net-name detection and topology-based
  detection (switch-diode pair grouping) are implemented and working. The original issue report's
  expectation of "16 columns for 65 keys" was incorrect — the Nat3z keyboard actually uses a
  single-column (COL5) design with 4 rows and diode isolation.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: Nat3z 65-key keyboard: net-name method correctly detects 4 rows × 1 column,
  65 estimated keys. Hugo keyboard: topology method correctly detects 14 rows × 6 columns
  (GPIO-style names A0-A3, D0-D13, MOSI, MISO, SCK), 76 estimated keys.

### KH-052 (MEDIUM): SPI/I2C/RS-485 bus protocol detection missing

- **Files**: `analyze_schematic.py` — I2C, SPI, UART, CAN, RS-485, SDIO aggregation
- **Root cause**: Already implemented in a prior batch. Bus protocol detection exists:
  I2C (lines 2706-2800), SPI (lines 2802-2847), UART, CAN (lines 2948+), RS-485 (lines 2978-3029),
  SDIO (lines 2872-2946).
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: ESP32-EVB Rev-L: UART (8-10 entries), CAN (2), I2C (2). Bus protocols
  correctly aggregated from signal prefix groups.

### KH-064 (HIGH): Crystal circuit detector incomplete/inconsistent

- **Files**: `kicad_utils.py` — `classify_component()`, `signal_detectors.py` — `_xtal_pin_re`
- **Root cause**: Crystal components using `Q` reference prefix (Q for quartz crystal) were
  classified as `transistor` by `classify_component()` because `Q` maps to `transistor` in the
  `type_map`. Similarly, oscillators with `CR` prefix were classified as `capacitor` (falls back
  to `C`). The crystal detector requires `type == "crystal"` to fire, so these components were
  invisible.
- **Fix**: (1) Added crystal/oscillator override in `classify_component()`: when lib_id contains
  "crystal"/"xtal" keywords, override to `crystal`; when lib_id contains "oscillator", override
  to `oscillator`. Applies regardless of reference prefix. (2) Expanded `_xtal_pin_re` regex
  to include more IC crystal pin name variants: XTAL1/2, OSC1/2, XIN/XOUT, XT1/XT2,
  XTAL_P/XTAL_N, RTC_XTAL, RTC32K_XP/XN.
- **Verified**: ESP32-P4-PC: 5 crystal circuits detected (Q1 32.768kHz, Q2/Q6 25MHz, Q4 12MHz,
  Q3 40MHz) with load caps. ESP32-EVB Rev-L: CR1 50MHz active oscillator detected. Legacy
  Rev-K2: 2 crystals detected. Q5 (BC817-40 transistor) correctly stays as transistor.

### KH-066 (MEDIUM): Ethernet interface missing magnetics and connector linkage

- **Files**: `signal_detectors.py` — `detect_ethernet_interfaces()`, `kicad_utils.py` — `classify_component()`
- **Root cause**: Three compounding issues: (1) `_eth_tx_rx_re` regex only matched MII differential
  pairs (TXP/TXN/TX+/TX-), not RMII single-ended signals (TXD0/RXD0/TXEN/CRS_DV). (2) When PHY
  component has no parsed pins (pin_net empty), BFS had no seed nets to start from. (3) RJ45
  connector `LAN1` was classified as `inductor` (LAN prefix → L fallback) and not detected as
  Ethernet connector (part number RJLBC/LPJ4013 not in keyword list).
- **Fix**: (1) Expanded `_eth_tx_rx_re` to include RMII signals (TXD\d, RXD\d, TXEN, CRS_DV, MDIO,
  MDC). (2) Added net-scanning fallback: when PHY has no parsed pins, scan all nets for the PHY
  reference and match on pin_name or net name patterns. (3) Added LAN/CON/USB/HDMI/RJ/ANT connector
  prefixes to `type_map` in `classify_component()`. (4) Added integrated-magnetics RJ45 part numbers
  (lpj4, hr911, rjlbc, etc.) and LAN reference prefix to Ethernet connector detection.
- **Verified**: ESP32-EVB Rev-L: PHY U4 (LAN8710A) → connector LAN1 (LPJ4013EDNL MagJack).
  All 9 ESP32-GATEWAY revisions: same PHY→RJ45 linkage detected. All 12 ESP32-EVB revisions pass.

### KH-067 (MEDIUM): HDMI/DVI interface detection not implemented

- **Files**: `signal_detectors.py` — `detect_hdmi_dvi_interfaces()`
- **Root cause**: Already implemented in a prior batch. `detect_hdmi_dvi_interfaces()` exists
  with bridge IC keywords, PIO-DVI pattern, and generic connector fallback.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: ESP32-P4-PC: LT8912B HDMI bridge IC correctly detected as HDMI/DVI interface.

### KH-073 (HIGH): Power domain detection fails on KiCad 5 legacy schematics

- **Files**: `analyze_schematic.py` — power domain analysis (cascading from KH-016)
- **Root cause**: Power domain detection requires pin-level net connectivity to map IC power pins
  to rails. On legacy .sch files, IC pins were empty due to incorrect `_STANDARD_LIB_PINS`
  offsets (KH-016), making the IC-to-rail mapping impossible.
- **Fix**: Resolved by KH-016 fix — corrected pin offsets, wire-snap fallback, and cache lib
  suffix resolution now populate IC pins on legacy files, enabling power domain analysis.
- **Verified**: ESP32-C3-DevKit-Lipo Rev B: ICs with power rails 0 → 2 (U1, U2 detected).
  ESP32-DevKit-LiPo: similar improvement.

### Regression results

- All analyzer runs pass: ESP32-P4-PC (1), ESP32-EVB (12), ESP32-GATEWAY (9), daisho (60),
  hackrf (23), splitflap (8), Voron-Hardware (29), icebreaker (15)
- Pre-existing assertion failures (net count drift from legacy .sch orphan improvements,
  rf_matching gaps on icebreaker) unchanged — 0 new regressions from this batch
- Assertion test corpus: hackrf, splitflap, Voron-Hardware, icebreaker, daisho all checked

---

## 2026-03-14 — KH-013, KH-017, KH-020, KH-021, KH-047, KH-051 (batch 4, 6 issues)

Source repos verified: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

### KH-047 (HIGH): IC function field always empty

- **File**: `analyze_schematic.py` — new `_classify_ic_function()` helper + `ic_result` dict
- **Root cause**: `analyze_ic_pinouts()` built `ic_result` but never populated a `function` field.
- **Fix**: Added `_classify_ic_function(lib_id, value, description)` with three-tier lookup:
  (1) KiCad stdlib library prefix mapping (40+ prefixes), (2) value/part number keyword matching
  (100+ patterns covering MCUs, regulators, logic, communication, sensors, etc.), (3) description
  keyword fallback. Connectors excluded to prevent false positives. Result inserted into `ic_result`.
- **Verified**: Hugo Keyboard KB2040→"microcontroller (RP dev board)", Nat3z ATmega32U4→"microcontroller (AVR)",
  CACKLE ESP32-S3→"microcontroller (ESP)", 74HC595→"logic IC", THVD1420→"UART interface",
  Buck LM2596S-12→"switching regulator". All 292 files pass.

### KH-013 (LOW): PWR_FLAG false warnings per sheet

- **File**: `analyze_schematic.py` — `audit_pwr_flags()`
- **Root cause**: Warnings on power nets with only `power_in` pins even when PWR_FLAG on another sheet.
- **Fix**: Skip warnings for well-known power/ground net names (via `_is_power_net_name()` / `_is_ground_name()`).
  These are nearly always driven globally via power symbols.
- **Verified**: No regressions; false warnings on sub-sheet power rails suppressed.

### KH-017 (LOW): Opamp input resistor verification

- **File**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: Input resistor detection didn't verify the resistor's other net is a signal,
  not power/ground. Bias resistors to power rails counted as signal input resistors.
- **Fix**: Added `not ctx.is_power_net(other) and not ctx.is_ground(other)` check on the input
  resistor's other net.
- **Verified**: No regressions in opamp detection across test repos.

### KH-020 (LOW): Capacitive feedback recognition

- **File**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: Only resistive feedback detected. Integrators (C feedback) and compensators
  (R+C feedback) missed.
- **Fix**: Added capacitor feedback search using same `out_comps & neg_comps` pattern as resistor
  feedback. New configurations: `"integrator"` (C feedback + R input), `"compensator"` (R+C feedback).
  Added `feedback_capacitor` field to output entry.
- **Verified**: No regressions; new configurations available for opamp circuits with capacitive feedback.

### KH-021 (LOW): BSS138 level shifter detection

- **File**: `signal_detectors.py` — `detect_transistor_circuits()`
- **Root cause**: BSS138-based bidirectional level shifters appeared as generic MOSFET switches.
- **Fix**: After load_type classification, check for level shifter pattern: N-channel MOSFET
  with gate→power rail, pull-up resistors on both source and drain to *different* power rails.
  Sets `topology="level_shifter"` and `load_type="level_shifter"`.
- **Verified**: No regressions; level shifter topology now detected for matching circuits.

### KH-051 (LOW): Addressable LED chain detection

- **File**: `signal_detectors.py` — new `detect_addressable_leds()` function
- **Root cause**: No detector for WS2812/SK6812/APA102 chains.
- **Fix**: New detector finds LEDs with addressable keywords in value/lib_id, identifies
  DIN/DOUT pins by name, traces DOUT→DIN chains. Reports chain length, protocol
  (single-wire vs SPI), LED type, estimated current draw (60mA/LED for WS2812).
  Wired into `analyze_signal_paths()` as `addressable_led_chains`.
- **Verified**: esp-rust-board: 1x WS2812B chain correctly detected. All 292 files pass.

### Regression results

- **6970/7004** assertions pass (34 failures pre-existing from batch 3)
- **0 regressions**, 19 possibly fixed, 15 newly detected in drift check
- All test repos pass: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

---

## 2026-03-14 — KH-012, KH-018, KH-019, KH-048 (partial), KH-068, KH-069, KH-070, KH-072, KH-074, KH-075, KH-076 (batch 3, 11 issues)

Source repos verified: esp-rust-board, OnBoard (279 files), hackrf-pro (12 files)

### KH-075 (LOW): TESTPAD misclassified as diode

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Ref prefix `D` matched `diode` before value `TESTPAD` was checked.
- **Fix**: After prefix-based result, check value for testpad/testpoint keywords and override to `test_point`.
- **Verified**: Components with value "TESTPAD" now classified as test_point regardless of ref prefix.

### KH-069 (LOW): Button/switch classified as 'other'

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Prefixes `BTN`, `BUTTON` not in type_map. Custom footprint buttons (YTS-A016-X, T1102D) fell through.
- **Fix**: (a) Added `BTN` and `BUTTON` to type_map. (b) Added button keywords (`button`, `tact`, `push`, `t1102`, `t1107`, `yts-a`) in library/value fallback. (c) Added `"button" in lib_lower` to switch detection.
- **Verified**: OnBoard keyboard projects correctly classify buttons as switches.

### KH-068 (LOW): Power multiplexer ICs classified as LDO

- **File**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: TPS2116/TPS2121 have VIN/VOUT pins, pass through regulator detector.
- **Fix**: Added power mux/load switch exclusion list after RF exclusion: `tps211`, `tps212`, `ltc441`, `ideal_diode`, `power_mux`, `load_switch`.
- **Verified**: Power mux ICs no longer appear in regulator results.

### KH-076 (MEDIUM): Crystal detector FPs on non-crystal ICs

- **File**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Active oscillator keyword match too broad — RF switches, baluns, muxes with "oscillator" in generic lib descriptions matched.
- **Fix**: Added exclusion keywords for RF/analog ICs: `switch`, `mux`, `balun`, `filter`, `amplifier`, `lna`, `driver`, `mixer`, `attenuator`, `diplexer`, `splitter`, `spdt`, `sp3t`, `sp4t`, `74lvc`, `74hc`.
- **Verified**: RF ICs no longer falsely detected as active oscillators.

### KH-012 (MEDIUM): Voltage divider false positives

- **File**: `signal_detectors.py` — `detect_voltage_dividers()`, `postfilter_vd_and_dedup()`
- **Root cause**: Pull-up/pull-down pairs and opamp feedback resistors matched as dividers.
- **Fix**: (a) Added extreme ratio filter (>100:1 skip). (b) Extended postfilter to remove VDs whose mid_net connects to opamp inverting input (IN-, INV, INN pin names).
- **Verified**: False-positive dividers reduced without affecting real divider detection.

### KH-019 (LOW): RC filter false pairs from shared-node

- **File**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: Pull-up + bypass cap on same signal net detected as "RC-network" filter.
- **Fix**: Skip filter entries classified as `RC-network` (neither end grounded). Only report properly classified low-pass/high-pass filters where shunt element connects to ground.
- **Verified**: 13 false-positive RC filter assertions now correctly return 0. Real low-pass/high-pass filters retained.

### KH-048 partial (MEDIUM): Key matrix net name spaces

- **File**: `signal_detectors.py` — `detect_key_matrices()`
- **Root cause**: "Row 0", "Column 2" don't match `ROW(\d+)` regex because spaces aren't stripped.
- **Fix**: Added `.replace(" ", "")` to net name normalization.
- **Note**: Topology-based detection (GPIO-style names, switch-diode connectivity) deferred.
- **Verified**: Space-containing net names now match ROW/COL patterns.

### KH-074 (LOW): Crystal frequency not parsed from value

- **File**: `signal_detectors.py` — new `_parse_crystal_frequency()` helper
- **Root cause**: `parse_value()` can't extract frequency from MPNs like "YIC-12M20P2".
- **Fix**: Added `_parse_crystal_frequency()` that tries `parse_value()` first, then regex for embedded MHz/kHz patterns. Used in place of bare `parse_value()` in crystal detector.
- **Verified**: Crystal values with MHz/kHz suffixes and MPN-embedded frequencies now parsed.

### KH-018 (LOW): Diff pair detector matches power rails

- **File**: `analyze_schematic.py` — differential pair detection
- **Root cause**: V+/V- and IN+/IN- matched as differential pairs.
- **Fix**: After finding suffix pair match, skip if either net is power or ground via `_is_power_net_name()` / `_is_ground_name()`.
- **Verified**: Power supply rail pairs no longer appear in differential_pairs.

### KH-072 (MEDIUM): SPI/I2C FPs from connector pin names

- **File**: `analyze_schematic.py` — I2C and SPI bus detection
- **Root cause**: Connectors with SDA/SCL/MOSI/MISO pins trigger bus detection with no ICs on the bus.
- **Fix**: Skip I2C/SPI bus entries when `devices` list is empty (no ICs = connector-only routing). Applied to net-name-based I2C, pin-name-based I2C, and SPI detection.
- **Verified**: Connector-only bus routes no longer generate false bus entries.

### KH-070 (MEDIUM): Subcircuit neighbors identical for all ICs

- **File**: `analyze_schematic.py` — `identify_subcircuits()`
- **Root cause**: Neighbor collection iterated all nets including power/ground. Every IC shares VCC/GND, so neighbors = everything.
- **Fix**: Skip power/ground nets in the neighbor loop using `_is_power_net_name()` / `_is_ground_name()`.
- **Verified**: Each IC now gets distinct neighbors based on signal connectivity, not shared power rails.

### Regression results

- **6970/7004** assertions pass (34 failures from intentional behavior changes — stale assertions need regeneration)
- **0 regressions**, 19 possibly fixed, 15 newly detected in drift check
- All test repos pass: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

---

## 2026-03-14 — KH-022, KH-024, KH-025, KH-049, KH-050, KH-053, KH-054+055, KH-056, KH-057+065, KH-071, KH-077 (batch fix, 13 issues)

Source repos verified: hackrf-pro, ESP32-EVB, LNA1109, OnBoard (279 files), urti-mainboard

### KH-053 (CRITICAL): KiCad 9 value parsing — SI prefixes dropped

- **File**: `kicad_utils.py` — `parse_value()`
- **Root cause**: `.split()[0]` discarded the SI prefix when KiCad 9 uses space-separated
  format `"18 pF"` instead of `"18pF"`. All derived calculations were orders of magnitude wrong.
- **Fix**: Before taking first token, check if second token starts with an SI prefix letter
  and rejoin: `"18 pF"` → `"18pF"` → correct 1.8e-11.
- **Verified**: hackrf-pro praline.kicad_sch: all capacitor/inductor values now correct.

### KH-024 (MEDIUM): #GND power symbols as components

- **File**: `analyze_schematic.py` — legacy parser
- **Root cause**: Checked `#PWR`/`#FLG` prefixes but not generic `#` prefix. Non-standard
  power symbols like `#GND`, `#+3V3` slipped through as regular components.
- **Fix**: Changed to `comp["reference"].startswith("#")`. Also updated enable/power-good
  filtering and known_power_rails detection to use `startswith("#")`.
- **Verified**: All legacy schematic repos pass.

### KH-049 (MEDIUM): Non-standard ref prefixes (CB, RB, QB)

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Full prefix "CB" not in type_map, fell to "other".
- **Fix**: After full-prefix lookup fails, try first-character fallback:
  `type_map.get(prefix[0])`. CB→C→capacitor, RB→R→resistor, QB→Q→transistor.
- **Verified**: Unit tests pass for CB1, RB3, QB2.

### KH-077 (MEDIUM): Per-component category always None

- **File**: `analyze_schematic.py` — component output
- **Root cause**: Component dict had `type` but output expected `category` field.
- **Fix**: Added `comp["category"] = comp.get("type")` before serialization loop.
- **Verified**: All components now have category field populated.

### KH-025 (LOW): X prefix crystals as connectors

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: X-prefix components defaulted to connector when value didn't match
  keyword list. Compact frequency values like "8M", "12M" didn't match "mhz"/"khz".
- **Fix**: Added regex `r'^\d+\.?\d*[mkMK]$'` to catch compact frequency notation.
- **Verified**: X1 with value "8M", "12M", "32.768K" all correctly classified as crystal.

### KH-056 (MEDIUM): I2S data lines detected as I2C

- **Files**: `analyze_schematic.py`, `signal_detectors.py`
- **Root cause**: "SDA" substring matched I2S pins like `I2S0_RX_SDA`.
- **Fix**: Added `"I2S" in nu` exclusion before I2C matching in three locations:
  net-name-based detection, pin-name-based detection, and observation detector.
- **Verified**: hackrf-pro: I2S nets no longer appear in I2C bus results.

### KH-057 + KH-022 + KH-065 (MEDIUM/LOW): UART false positives

- **File**: `analyze_schematic.py` — UART detection
- **Root cause**: TX/RX substring match without excluding RMII/PCIe/clock/USB/HDMI/I2S.
- **Fix**: Expanded exclusion list to include RMII, MII, EMAC, ENET, ETH, PCIE, PCI_,
  HDMI, LVDS, MIPI, CLK, CLOCK, USB_D, USBDM, USBDP, I2S.
- **Verified**: ESP32-EVB: RMII signals no longer in UART. urti-mainboard: clock/RF
  signals excluded.

### KH-050 (MEDIUM): Fixed regulator analyzed as adjustable

- **Files**: `kicad_utils.py` — `lookup_regulator_vref()`, `signal_detectors.py`
- **Root cause**: No suffix parsing for fixed-output variants (LM2596S-**12**).
- **Fix**: (a) Parse part number for fixed voltage suffix patterns: `-3.3`, `-33`, `-3V3`,
  `-1V8`, `-12`. Return fixed voltage directly with source="fixed_suffix".
  (b) In regulator detector, emit fixed vout before feedback analysis and skip
  feedback divider when fixed suffix found.
- **Verified**: LM2596S-12→1.2V, AMS1117-3.3→3.3V, RT9013-18→1.8V all correct.

### KH-054 + KH-055 (HIGH): RF amplifier/switch not detected

- **File**: `signal_detectors.py`
- **Root cause**: rf_amp_keywords missing BGB741, TRF37C, etc. LNAs misclassified as
  power regulators due to having VIN/VOUT-like pins.
- **Fix**: (a) Expanded rf_amp_keywords with `bgb7`, `trf37`, `sga-`, `tqp3`, `sky67`.
  (b) Added RF IC exclusion list in power regulator detector pre-filter.
- **Verified**: hackrf-pro: BGB741L7ESD now in rf_chains amplifiers, not power_regulators.
  LNA1109: BGB741L7ESD no longer falsely detected as regulator.
- **Note**: KH-055 RF switch detection was already implemented via rf_switch_keywords in
  a prior fix. This batch confirmed switches are detected and added the RF exclusion
  to prevent regulator false positives on RF ICs.

### KH-071 (MEDIUM): RF matching FPs on power LC filters

- **File**: `signal_detectors.py` — `detect_rf_matching()`
- **Root cause**: No value range filtering — 6.8uH + 10uF treated as RF matching.
- **Fix**: After has_inductor check, parse values and skip if inductors >1uH or caps >1nF.
- **Verified**: Power supply LC filters no longer flagged as RF matching networks.
  4 false-positive assertions removed from reference data.

### Regression results

- **7004/7004** assertions pass (4 FP assertions removed)
- **0 regressions**, 19 possibly fixed, 15 newly detected
- All test repos pass: hackrf-pro (12), ESP32-EVB (12), LNA1109 (1), OnBoard (279),
  urti-mainboard (18)

---

## 2026-03-13 — KH-015, KH-041 through KH-046, TH-007 (batch fix, 8 issues)

Source repos reviewed: ubertooth, analog-toolkit, throwing-star-lan-tap

### KH-015 (HIGH): Legacy schematic missing signal_analysis

- **File**: `analyze_schematic.py` — `parse_legacy_schematic()`
- **Root cause**: Legacy parser never called `analyze_signal_paths()` or `analyze_design_rules()`.
  All KiCad 4/5 `.sch` files got zero signal detections.
- **Fix**: Added `analyze_signal_paths()` and `analyze_design_rules()` calls after
  `build_pin_to_net_map()`, matching the KiCad 6+ path. Added `signal_analysis` and
  `design_analysis` to the return dict.
- **Note**: Limited value until KH-016 (wire-to-pin connectivity) is fixed — many nets are
  orphaned. But some nets resolve correctly, and detectors now find circuits on those.
- **Verified**: ubertooth-one.sch: 1 voltage divider, 3 LC filters, 1 crystal circuit,
  3 decoupling analyses, 4 protection devices, 1 transistor circuit, 1 RF matching network.

### KH-041 (MEDIUM): RF matching false positives on non-RF designs

- **File**: `signal_detectors.py` — `detect_rf_matching()`
- **Root cause**: (1) `sma` keyword in value field matched SMA connectors used as test points,
  not antennas. (2) Pure R+C networks near "antennas" were flagged as matching networks.
- **Fix**: (1) Moved `sma` to lib_id-only keyword list — value field no longer triggers.
  (2) Added inductor requirement: matching networks without inductors are skipped (pure C
  networks are decoupling/filtering, not impedance matching).
- **Verified**: analog-toolkit: 13 false positives eliminated (was RC anti-aliasing on ADC inputs).
  icebreaker: 4 false positives eliminated. ubertooth: real pi_match with L1/L2/C1/C3/C5 retained.

### KH-042 (LOW): dnp_parts counts BOM lines not instances

- **File**: `analyze_schematic.py` — `compute_statistics()`
- **Root cause**: `len(dnp_items)` counted BOM group entries (unique value/footprint combos),
  not individual component instances.
- **Fix**: Changed to `sum(b["quantity"] for b in dnp_items)`.
- **Verified**: analog-toolkit: 13 DNP resistors now correctly reported as dnp_parts=13 (was 1).

### KH-043 + KH-044 (LOW): PCB copper_layers_used and front/back counts for custom layer names

- **File**: `analyze_pcb.py` — `compute_statistics()`
- **Root cause**: (1) `copper_layers_used` checked `"Cu" in layer_name` — failed for KiCad 5
  custom names like `"Front"`, `"Back"`. (2) `front_side`/`back_side` hardcoded `"F.Cu"`/`"B.Cu"`.
- **Fix**: Added `layers` parameter to `compute_statistics()`. Resolves copper layer names from
  layer declarations (type in signal/power/mixed/user). Front/back resolved by layer number
  (0=front, 31=back) instead of hardcoded names. Fallback to `"Cu" in name` when no layer
  declarations available.
- **Verified**: throwing-star-lan-tap: copper_layers_used=2 (was 0), copper_layer_names=["Back","Front"],
  front_side=6/11 (was 0), back_side=1 (was 0).

### KH-045 (MEDIUM): Legacy custom field MPN/manufacturer extraction

- **File**: `analyze_schematic.py` — legacy component field parsing
- **Root cause**: Fields with generic names `"Field1"`, `"Field2"` (common KiCad 4/5 convention)
  weren't matched by keyword-based extraction.
- **Fix**: Track generic-named fields during parsing. After keyword matching, apply positional
  fallback: Field2→MPN, Field1→manufacturer (only when mpn/manufacturer still empty).
- **Verified**: ubertooth: 68/89 components now have MPNs and manufacturers (was 0/89).
  Examples: FB5→Murata/BLM18TG601TN1D, R17→Bourns/CR0603-JW-103ELF.

### KH-046 (LOW): CONN_1 tilde prefix prevents pin lookup

- **File**: `analyze_schematic.py` — `_parse_legacy_lib()`
- **Root cause**: Legacy lib stores symbol name as `~CONN_1` (tilde = invisible name display
  flag). Parser stored `~CONN_1` but schematic lookup used `CONN_1`. Lookup failed, pins empty.
- **Fix**: Strip leading tilde from symbol name: `parts[1].lstrip("~")`.
- **Verified**: ubertooth: P5-P13 (9 CONN_1 test pads) now have 1 pin each (was 0).

### TH-007 (MEDIUM): discover_projects() doesn't recognize .pro as project marker

- **File**: `utils.py` — `discover_projects()`
- **Root cause**: Only `.kicad_pro` and `.kicad_pcb` recognized as project markers. KiCad 4/5
  uses `.pro` files.
- **Fix**: Added `.pro` rglob with header check (first line starts with `update=`, `[pcbnew`,
  or `[eeschema`) to confirm KiCad format.
- **Verified**: ubertooth: 7 projects discovered (was 0). Snapshot/baseline workflows now work.

---

## 2026-03-13 — KH-027 through KH-040 (batch fix, 14 issues)

Source repos reviewed: hackrf, bitaxe, icebreaker, moteus, OtterCastAudioV2

### KH-027 (CRITICAL): Symbol name filter skips valid custom symbols

- **File**: `analyze_schematic.py` — `extract_lib_symbols()`
- **Root cause**: Sub-unit filter `name.split("_")[-1].isdigit()` matched any symbol
  ending in `_<digit>`, not just sub-unit patterns like `Device:C_0_1`.
- **Fix**: Changed to `rsplit("_", 2)` and require both last two segments are digits.
  `Q_NMOS_CSD17311Q5_1` → parts `["Q_NMOS", "CSD17311Q5", "1"]` → not filtered.
  `Device:C_0_1` → parts `["C", "0", "1"]` → correctly filtered.
- **Verified**: bitaxe Q1/Q2 now `type=transistor` (were missing from lib_symbols entirely).

### KH-028 (HIGH): Ferrite bead values parsed as henries

- **Files**: `kicad_utils.py` — `classify_component()`, `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: L-prefix components with "ferrite"/"bead" in lib_id/value were classified
  as `inductor`. Their impedance values (e.g., "600" = 600Ω @ 100MHz) were treated as
  henries, producing nonsensical LC filter results.
- **Fix**: (1) `classify_component()` now returns `ferrite_bead` when lib_id or value
  contains "ferrite" or "bead". (2) `detect_lc_filters()` skips components with
  `type == "ferrite_bead"` or ferrite/bead keywords.
- **Limitation**: Doesn't catch rescue-library ferrite beads with generic symbol names
  and bare numeric values (e.g., icebreaker L1/L2 = `pkl_L_Small` value `600`). Would
  need heuristic value-range detection for those.
- **Verified**: Components with ferrite metadata correctly reclassified and excluded from LC filters.

### KH-029 (HIGH): MPN field aliases (PARTNO, Part Number)

- **File**: `analyze_schematic.py` — KiCad 6+ property chain and legacy field handler
- **Root cause**: MPN extraction only recognized a narrow set of field names. Common
  alternatives `PARTNO`, `Part Number`, `PART_NUMBER` were not mapped.
- **Fix**: Added `PARTNO`, `PartNo`, `Partno` to KiCad 6+ `get_property()` chain.
  Added `PARTNO`, `PART NUMBER`, `PART_NUMBER`, `PART NO` to legacy field name tuple.
- **Verified**: bitaxe 86/136 components now have MPNs populated (was 0).

### KH-030 (HIGH): Current sense with IC-integrated amplifier

- **File**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: Detector only matched shunt + discrete sense IC topology. Gate drivers
  and power ICs with integrated CSA inputs (CSP/CSN/SEN/ISENSE pins) were not detected.
- **Fix**: Added second-pass loop over unmatched shunt candidates. Checks if either shunt
  net connects to an IC pin with a CSA-related name from `_integrated_csa_pins` frozenset.
  Creates entry with `type: "integrated_csa"`.
- **Limitation**: moteus DRV8323 not matched because shunt→CSA path goes through net ties
  and RC filters, and KH-026 (multi-instance net merging) prevents correct net resolution.
- **Verified**: Detection works for direct shunt-to-IC-pin topologies.

### KH-031 (HIGH): RF antenna matching networks

- **File**: `signal_detectors.py` — new `detect_rf_matching()`
- **Root cause**: No detector existed for antenna matching networks.
- **Fix**: New function finds antenna connectors (AE*/ANT* prefix or antenna/u.fl/sma
  keywords), BFS through L/C components (max 6 hops), classifies topology:
  - `pi_match`: ≥1 series L + ≥2 shunt C
  - `T_match`: ≥2 series L + ≥1 shunt C
  - `L_match`: 2 components, 1 series + 1 shunt
  - `matching_network`: other arrangements
  Reports target IC if BFS reaches one.
- **Wiring**: Added to `analyze_signal_paths()` imports, call, and results dict as `rf_matching`.
- **Verified**: Compiles and runs on all 9 test repos.

### KH-032 (HIGH): SDIO bus protocol detection

- **File**: `analyze_schematic.py` — `analyze_design_rules()` bus detection section
- **Root cause**: No SDIO/SD/eMMC bus category existed in the bus protocol detector.
- **Fix**: Added SDIO detection after UART, before CAN. Matches net names with prefixes
  `SDIO`, `SD_`, `SD1_`, `SD2_`, `EMMC`, `MMC`, `WL_SDIO` combined with CLK/CMD/D0-D7
  signals. Requires CLK + CMD + D0 minimum. Reports bus width, pull-up presence on CMD
  and data lines, and connected IC devices.
- **Verified**: OtterCastAudioV2 detects both `SD` (SDC0_*) and `SDIO` (WL_SDIO_*) buses,
  4-bit width, pull-ups on CMD+D0-D3.

### KH-033 (MEDIUM): DNP from value/Note field

- **File**: `analyze_schematic.py` — KiCad 6+ and legacy paths
- **Root cause**: Only checked explicit KiCad 7+ `dnp` attribute or field named "DNP".
  Designs using `value="DNP"` or `Note="DNP"` convention were not recognized.
- **Fix**: KiCad 6+ path: after `dnp = get_value(sym, "dnp") == "yes"`, check if value
  is in `("DNP", "DO NOT POPULATE", "DO NOT PLACE", "NP")`. Legacy path: same value
  check after field processing, plus `NOTE`/`NOTES`/`COMMENT` field value check.
- **Verified**: OtterCastAudioV2 C49 now `dnp=True` (value="DNP").

### KH-034 (MEDIUM): Active oscillator detection

- **File**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Only passive crystals with load caps were detected. Active oscillators
  (TCXO, VCXO, MEMS) with VDD/GND/OUT pins were ignored.
- **Fix**: Added loop after passive crystal detection, before return. Matches components
  with `type == "oscillator"` or oscillator keywords in value/lib_id. Identifies output
  pin by name (OUT/CLK/CLKOUT) or falls back to first non-power/non-ground pin. Emits
  entries with `type: "active_oscillator"` and empty `load_caps`.
- **Verified**: Compiles and runs on all test repos.

### KH-035 (MEDIUM): Integrated LDO on IC pins

- **File**: `signal_detectors.py` — new `detect_integrated_ldos()`
- **Root cause**: ICs with internal LDOs (e.g., FT2232H VREGOUT pin) were not detected
  as power sources.
- **Fix**: New function scans ICs not already in `power_regulators` for pins named
  `VREGOUT`, `VREG`, `LDO_OUT`, `REGOUT`, etc. If pin drives a power net (not ground),
  adds entry with `topology: "integrated_ldo"`. Results appended to `power_regulators`.
- **Verified**: Compiles and runs on all test repos.

### KH-036 (MEDIUM): LC filter parallel cap merging

- **File**: `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: Caps were grouped for parallel merging by `(inductor_ref, shared_net)`
  only. Caps with different "other" nets (series vs shunt topology) were falsely merged.
- **Fix**: Changed grouping key to include the cap's other net:
  `(ind_ref, shared_net, cap_other_net)`. Only caps sharing both terminals get merged.
- **Verified**: Compiles and runs on all test repos.

### KH-037 (MEDIUM): IC with internal regulator

- **File**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Complex ICs with internal switching regulators (e.g., AP6236 WiFi module
  with SW pin + inductor) classified as dedicated power regulators.
- **Fix**: After topology classification, check pin ratio. If IC has >10 total pins and
  <20% are regulator-related names (VIN/VOUT/FB/SW/EN/BST/etc.), set topology to
  `"ic_with_internal_regulator"`.
- **Verified**: Compiles and runs on all test repos.

### KH-038 (MEDIUM): Sense inputs vs power domain

- **File**: `analyze_schematic.py` — power domain mapping in `analyze_design_rules()`
- **Root cause**: IC sense/measurement pins (IN+, IN-, SENSE, CSP, CSN) connected to
  power rails being monitored were included in the IC's power domain, causing false
  cross-domain warnings.
- **Fix**: Added `_sense_pin_names` exclusion set. Pins with these names are skipped
  before power domain classification.
- **Verified**: Compiles and runs on all test repos.

### KH-039 (MEDIUM): Power rail detection beyond power symbols

- **File**: `analyze_schematic.py` — `build_statistics()`
- **Root cause**: `power_rails` only included nets from `power_symbol` components.
  Nets defined by local/hierarchical labels matching voltage patterns (e.g., "3V3",
  "VIN_M") were missed.
- **Fix**: After collecting power symbol rails, also scan all net names through
  `is_power_net_name()` and add matches.
- **Verified**: Compiles and runs on all test repos.

### KH-040 (MEDIUM): Legacy Description field

- **File**: `analyze_schematic.py` — legacy custom field handler
- **Root cause**: No case for `DESCRIPTION` or `DESC` field names in the legacy parser's
  custom field handler.
- **Fix**: Added `elif fu in ("DESCRIPTION", "DESC"): comp["description"] = field_val`.
- **Verified**: Compiles and runs on all test repos.

---

## Pre-2026-03-13 — Earlier fixes (KH-001 through KH-011, KH-014, KH-023, TH-001 through TH-006)

These issues were fixed in earlier sessions. Details not recorded here — see git history
of the kicad-happy and kicad-happy-testharness repos for the actual changes.

### KH-001 through KH-011, KH-014, KH-023

Analyzer fixes predating the structured issue tracker. Covered schematic parsing,
legacy format support, component classification, and signal detection improvements.

### TH-001 through TH-006

Test harness infrastructure: checkout.py, discover.py, run scripts, regression framework,
validation pipeline, budget monitoring. All resolved.
