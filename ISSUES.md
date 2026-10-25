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

Last updated: 2026-10-25

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-646** (KH-645 filed 2026-10-25 by the harness audit fix session — netlist oracle m68k-hbc splits 16 `/Bus/PEP/AD*` nets (oracle 4/5 since at least `0490c49`), MEDIUM; KH-644 filed 2026-10-25 by the harness audit fix session — PCB zone `fill_ratio` sums every filled layer over one layer's outline (1.83 on a two-layer zone), LOW, surfaced when the assertion engine stopped truncating fractional values; KH-643 filed 2026-10-25 by the main-repo agent — EMC SW-001 ignores `--standard` and discards its harmonic amplitude, MEDIUM; KH-497..642 filed 2026-10-25 from the external audit round 1 at `07b7fb1` — 30 static reviews in five bundles, every finding re-verified against the code, one entry per fix group; records and the wave plan in the main repo at `docs/audit/FIX-PLAN.md` and `docs/audit/0*/findings/VERIFICATION.md`; addenda added to KH-329, KH-331, KH-428, KH-432, KH-433, KH-437, KH-439, KH-442, KH-443, KH-470, KH-481, KH-482, KH-484, KH-487, KH-494; KH-480..496 filed 2026-10-24 from the v3 round-9b handoff §7 — the review-period bug-hunt deferrals, every claim re-verified in source at `07b7fb1` (19 confirmed / 4 partly), each with its budget or oracle re-freeze: failed-SPICE-run diagnostics (93 units), missing-sheet / truncated-input diagnostics, unannotated duplicate-ref collapse (1,598 units / 466 repos), GR-002 extents-only (MEDIUM), root-only `inputs` (4,261 multi-sheet units), suppressions only in EMC/thermal, `--parasitics` verbatim names, Mouser `""` key (4 frozen runs), SPICE cache hygiene, EMC `--severity` vocabulary, analysis_cache M3/M4, DigiKey 429, Action diff-base, three review-minor umbrellas; KH-479 assigned FIXED-direct 2026-10-24 to the review-period Critical A-C1 (analysis-dir containment, new in v3, fixed before release — see FIXED.md); KH-477 / KH-478 / KH-446 FIXED in round 9b (`cd2e49b` / `c6f4807`), KH-447 resolved for LT3514, see FIXED.md; KH-478 filed 2026-10-24 from the v3 round-9 handoff §11 — `emc_spice.run_distributed_pdn_spice` measurement tuples in the wrong shape → always `(False, None)`, temp dir never removed, no product caller, LOW; KH-472 / KH-464 / KH-466 / KH-475 FIXED in v3 round 9 (`ec81ca6`), see FIXED.md; KH-477 filed 2026-10-24 while fixing TH-077 — the SPICE model cache falls back to one global `/tmp` directory because `analyze_schematic.py` strips `file`; non-atomic manifest, cross-project leakage, LOW; KH-476 filed 2026-10-24 during the Checklist 11 `_KNOWN_FREQS` verification — the TPS62160 / TPS63000 keys miss the siblings of their own datasheets, 31 regulator findings default to 500 kHz, LOW; KH-470..475 filed 2026-10-23 from the v3 round-8 handoff §11 — thermal `title`+`summary` twin, `export_issues` severity vocabulary, `emc_spice.py` unquoted redirect without `cwd` (KH-463 sibling), RS-001 "carries power_in pins" wording on a name-admitted bootstrap-only rail, `lifecycle_audit` without `diagnostics`, Monte-Carlo per-trial fallback stderr noise; all pre-existing at `a0df172`, LOW; KH-454 / KH-455 / KH-463 FIXED in round 8 (`6222468`, `c598140`), see FIXED.md; KH-469 filed 2026-10-23 during the Checklist 11 SWITCHING_EFFICIENCY verification — three of the four `analyze_thermal.SWITCHING_EFFICIENCY` keys are unreachable and the schematic detector carries a third, different efficiency table; `ic_with_internal_regulator` regulators are costed as 85 %-efficient switchers, LOW; KH-468 filed 2026-10-23 during the Checklist 11 ADC-map verification — `_ADC_RESOLUTION_MAP` 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist, LOW; KH-467 filed 2026-10-23 during the Checklist 11 backlog pass — three divergent LED forward-voltage tables (`_LED_VF` / `_LED_VF_FLOOR` in domain_detectors, `_LED_VF_BY_COLOR` in validation_detectors) disagree per colour, LOW; KH-464..466 filed 2026-10-23 from the v3 round-7 handoff §11 — lifecycle_audit missing-input traceback, `is_cross_analysis_ground_name` exact-set policy (SGND/GNDPWR/GND_ISO/VSSA/`/Power/GND` not ground), `analyze_gerbers` exit 0 on a nonexistent dir; all pre-existing, verified at 0490c49, LOW; KH-463 filed 2026-10-23 at the v2.3.2 corpus regen — SPICE testbench `.control` `echo … > <path>` redirect unquoted, every measurement silently skips when the workdir path has whitespace or `,`/`&`/`'`/non-ASCII, the user-facing `analysis/<run>/spice_work/` default inherits the project path, MEDIUM; KH-456..462 filed 2026-10-22 from the SacMap rev2 run-9 soak at the v2.3.2 pre-tag `4701c26` — fab_release_gate counts `G***` logo footprints (false FAIL), silk revision regex misses `rev2`, `capability_mode` `datasheet_coverage_pct` is a hard-coded stub, `audit_pwr_flags` ignores `power_in` pins off named rails (ERC `power_pin_not_driven` ×3 unseen), EMC DC-002 fires on a part-numbered ESD array (dupes UC-001), `cross_domain_signals.needs_level_shifter` stale after KH-424, `datasheet_verify` rc 1 for warnings; riders on KH-431/432/436; all code-verified by the main-repo agent; KH-455 filed 2026-10-22 at the v2.3.2 backport gate — PP-001 `(ref, pin_number)` dedup masks a second symbol's power pin on unannotated `U?` designs, the gate's one residue unit, LOW; KH-454 filed 2026-10-22 at the v2.3.2 backport adoption — RS-001 fires on a bootstrap-only net whose sole `power_in` pin is the BST/BOOT pin, LOW, with the two GitHub #55 riders; KH-450..453 assigned 2026-10-22 FIXED-direct — GitHub #52–#55 / PRs #56–#59 by EldarPolitkin on `main` @ 4701c26, see FIXED.md; KH-449 filed 2026-10-16 at the v3 round-5 full-chain gate — pcb `--full` exceeds the 600 s cap on starshipraider MAXWELL both sides, LOW; KH-447 addendum: LT3514 is a ≥ 20 GB memory blow-up, OOM-killed under the 600 s cap; KH-448 filed 2026-10-16 at the v3 round-4 gate — hierarchy-mode `analyze_schematic.py` ~3 GB RSS on BerkeleyLab/Marble, both sides equal, LOW; KH-446/447 filed 2026-10-15 at the v3 round-2 reply per ruling Q3 — empty-input pcb traceback (hackclub/OnBoard placeholders), schematic 120 s timeouts on three hierarchical roots (discrete-nes ×2, LT3514); KH-445 filed 2026-10-15 at H0 plan 4 — `EQ-042` tags two different equations, LOW; KH-444 assigned 2026-10-14 FIXED-direct — PR #51 AM-001 `<domain>_max` key lookup, imrcly, see FIXED.md; KH-443 filed 2026-10-14 from GitHub #50 — net ties not bridged by RS-001/PP-001 DC-continuity audits, MEDIUM; KH-442 filed 2026-10-06 at the v2.3.1 regen — behavioral opamp model gain 0 false SP-WARN; KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
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
KHPA finding ID). Next TH number: **TH-090** (TH-089 filed and fixed 2026-10-25 by the harness audit fix session — `generate_catalog.py` counted the `capability_mode.json` sidecar as a schematic/PCB/EMC/SPICE output, see FIXED.md; TH-080..088 filed 2026-10-25 from the harness external audit round 1 — budgeted-kind worker exceptions, ledgered-timeout coverage, `discover.py --repo` global-manifest shrink, silent assertion-file drop, null/`[]` required-field locks (all HIGH, gate/assertion false-pass paths), constants corpus-hit names, `audit_equations --diff` no-op, `validate_design_intent` multi-repo scope, `analyze_bom_mismatch` layout (LOW); records `docs/audit/0*-harness-*/findings/VERIFICATION.md`, plan `docs/audit/HARNESS-FIX-PLAN.md`; TH-079 filed 2026-10-25 from the external audit round 1 — `generate_validation_md.py` category table and total use different denominators (1,855 = the aspirational count), LOW; TH-078 filed 2026-10-24 at the v3 round-9b gate — no "debt resolved" disposition: a ledgered unit the candidate fixes fails `skips_ok`, `strict_clean` and the strict comparator (`missing_a`), so the structural criterion cannot pass mechanically and the response builder carries a hand-written exception, LOW; TH-065, TH-066 + TH-077 FIXED 2026-10-24, see FIXED.md; TH-077 filed 2026-10-24 at the v3 round-8 spice-offline gate — `run_spice.py` output is not deterministic run-to-run: `simulation_results[*].model_note` flips `lookup:<MPN>` ↔ `cache:<MPN>` for the same product and inputs (132 of 8,829 reports between two baseline passes), LOW; TH-076 fixed-on-discovery 2026-10-23 during the Checklist 11 backlog pass — `audit_constants.py scan` dropped and re-added every constant whose file moved without a `relocate --map` (rounds 2/3), losing 41 verification records incl. `_REGULATOR_VREF` 55/114 and `_CAP_ESL` 7/7; the registry had also not been rescanned since round 5, see FIXED.md; TH-075 fixed-on-discovery 2026-10-23 at the v2.3.2 corpus regen — `run_spice.py` per-unit `--workdir` carried raw repo/file names into ngspice, 18,464 sims silently skipped on 5,198 corpus units, directory name now sanitized + digest, see FIXED.md; TH-074 fixed-on-discovery 2026-10-22 at the v2.3.2 backport gate — long-run waiters stalled on a `pgrep -f` self-match and on a zombie PID; `tools/wait_for_run.py` + RUNBOOK 26k + full-chain `done.json` marker, see FIXED.md; TH-073 fixed-on-discovery 2026-10-17 at the v3 round-6 gate preflight — `run_corpus_gate.py` accepted analyzer-less profiles (`spice-offline`, the new `distributor-offline`) and would have run a zero-unit gate, guard added, see FIXED.md; TH-072 fixed-on-discovery 2026-10-16 at the v3 round-5 gate preflight — `full-chain` profile declared no schematic analyzer, Phase B ran no chained unit, see FIXED.md; TH-071 filed 2026-10-16 at the v3 round-4 gate — `run_corpus_gate.py --jobs` not memory-aware, hierarchy profile at 32 jobs OOMs the box, LOW; TH-070 filed 2026-10-15 at the v3 round-2 reply — scan-coverage identity by line/file yields ~150 false losses per structural round, MEDIUM; TH-069 FIXED 2026-10-15 at the v3 round-3 reply — discover.py regular-file filter + manifest regen, see FIXED.md; TH-068 filed 2026-10-15 at H0 plan 6 — fixture-lane A/A chained envelopes unverifiable after the basetemp move, LOW; TH-067 filed 2026-10-15 — batch-runner pool workers outlive a killed parent (the TH-063 mechanism), MEDIUM; TH-066 filed 2026-10-15 at the H0 plan 4 final review — audit tools walk 58 of the 90 scanner files; TH-065 filed 2026-10-15 at H0 plan 4 — audit_constants function-scope `name:line` identity churns the registry; TH-064 filed 2026-10-15 — emc/thermal/spice `--resume` refused until identity-based resume exists; TH-063 filed 2026-10-14 — mutating runner launched against the live tree from a TDD RED step, 16,909 emc outputs rewritten, no measurable impact; TH-055 and TH-059 (harness half) fixed 2026-10-15 (H0 plan 2), see FIXED.md; TH-062 filed 2026-10-14 — 58 print-and-return vacuous skip paths in required-tier smoke files; TH-061 filed 2026-10-14 — test_datasheet_db_cli.py fallback fixture writes under repos/; TH-060 filed 2026-10-14 — test_kh393_power_rails_threaded premise stale since PR #44, now strict xfail; TH-052/053/058 fixed 2026-10-14 (H0 plan 1, honest pytest collection), see FIXED.md; TH-059 filed 2026-10-06 at the v2.3.1 regen — batch SPICE side effects: spice/ dirs in repos/ + live DigiKey lookups; TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 FIXED 2026-10-15 at H0 plan 5 — generator rewritten as grouped reconciliation, see FIXED.md; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 80 open issues (61 KH + 19 TH).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-645: netlist oracle — m68k-hbc splits 16 `/Bus/PEP/AD*` nets into `/ATA/D*` + `/Processor/D*` (oracle 4/5)

**Severity:** MEDIUM (hierarchical bus connectivity on one of the five oracle boards; was 5/5 at the v2.2 gate)

**Symptom:** `regression/run_netlist_oracle.py --board m68k-hbc` (kicad-cli 10.0.6): analyzer 1,222 nets vs oracle 1,230; matched 1,188, **split 16**, merged 0. Every split is one oracle net `/Bus/PEP/AD<n>` (n = 0..15) that the analyzer carries as two nets `/ATA/D<n>` and `/Processor/D<n>`. The other four boards pass.

**Root cause:** not traced. The split reproduces identically at product `0490c49`, `a0df172` and `07b7fb1`, so it predates v3 round 8. Not excluded: a kicad-cli upgrade on the harness box since the 2026-07-26 v2.2 gate (5/5 PASS) changing the oracle side of the comparison; check with the kicad-cli version recorded in that gate before tracing the analyzer's bus-alias/sheet-pin propagation for the `PEP` bus.

**File:** analyzer hierarchical bus connectivity (the KH-359/#25 code path); harness `regression/run_netlist_oracle.py` (oracle runner).

**Repro:** `repos/ehbc-project/ehbc-proto1-board/projects/m68k-hbc/m68k-hbc.kicad_sch`; `KICAD_HAPPY_DIR=<product> python3 regression/run_netlist_oracle.py --board m68k-hbc`.

**Discovered:** 2026-10-25, harness audit fix wave 4 (oracle re-run after moving its children onto `build_env`; the old runner fails identically).

### KH-644: PCB zone `fill_ratio` divides the filled area of every layer by one layer's outline — multi-layer zones report ratios above 1.0

**Severity:** LOW (a derived summary field; consumers that threshold `fill_ratio` misread multi-layer zones)

**Symptom:** `db-ok/SofleChocWireless` `Case/PCBBottom/SofleKeyboardBottomPlate.kicad_pcb`, zone 0 on `F&B.Cu`: `outline_area_mm2` 14,225.71, `filled_area_mm2` 26,028.28, `fill_ratio` 1.83. A zone cannot be more than fully filled.

**Root cause:** the zone parser at `skills/kicad/scripts/pcb/reader.py:808-816` (product `07b7fb1`) accumulates `total_filled_area` over every filled layer (the per-layer split lands in `filled_layers`), then sets `fill_ratio = total_filled_area / outline_area`, where `outline_area` is one layer's polygon area. A zone on N layers can report up to N.

**File:** `skills/kicad/scripts/pcb/reader.py:808-816` (zone parse, `fill_ratio`); `:654` (docstring: "1.0 = fully filled").

**Repro:** the board above; the curated lock `FND-00001367-AST-02` (`zones[0].fill_ratio` ≤ 1.0) records it, now aspirational. The harness assertion engine had truncated 1.83 to 1 and passed the lock until code A2-F10 was fixed.

**Fix direction:** divide per layer (`fill_ratio` = filled area / (outline area × filled layer count), or report a per-layer ratio). Budget: `fill_ratio` changes on multi-layer zones only.

**Discovered:** 2026-10-25, harness audit fix wave 2 (code A2-F10 corpus measurement).

### KH-643: EMC SW-001 ignores `--standard` (always the FCC 30-960 MHz bands) and discards the harmonic amplitude it computes

**Severity:** MEDIUM (default EMC path, every board with a switching regulator; wrong bands for every non-FCC `--standard`)
**File:** `skills/emc/scripts/emc_rules.py:1003` (`check_switching_harmonics(schematic, standard='fcc-class-b')`: `standard` never read in the body), `:1038-1042` (hard-coded bands `30-88` / `88-216` / `216-960` MHz), `:1048-1054` (`amp` from `trapezoidal_harmonic_amplitude`, spread-spectrum `amp *= 0.18`, never used afterwards), `:1056-1060` (severity from harmonic count and lowest order only); caller `:4562` passes the CLI `--standard` (`analyze_emc.py:322`, choices from `STANDARDS`)
**Discovered:** 2026-10-25, main-repo agent while answering the harness's SW-001 population-contract question (harness LOG 2026-10-25 item 3; harness code A4-F11), read at `07b7fb1`; not part of the external audit records

**Symptom:** `analyze_emc.py --standard cispr-class-b` (or `cispr-class-a`, `cispr-25`, `fcc-class-a`, `mil-std-461`) evaluates SW-001 against the FCC class B band edges 30/88/216/960 MHz, not the selected standard's own table in `emc_formulas.STANDARDS` (`:69-76`; e.g. `CISPR_25_CLASS5_RADIATED` `:55-59` is 30-68 / 68-108 / 108-230 / 230-1000 MHz). Nothing above 960 MHz is checked. The amplitude of the strongest in-band harmonic is computed, including the ~−15 dB spread-spectrum discount, and then dropped: severity is `HIGH` (→ `error`) if the lowest in-band harmonic is < 30, `MEDIUM` (→ `warning`) if more than 10 harmonics fall in the band and the lowest is < 100, else `INFO`, regardless of amplitude, the standard's limit, or spread spectrum. The switching frequency, harmonic range and envelope corner live only in `description` text; no structured field carries them, so a consumer (harness `validate/validate_emc.py`) cannot check band agreement without parsing prose.

**Fix direction / budget:** take the bands from the selected standard's limit table (`emc_formulas.get_emission_limit` / the `STANDARDS` tables) and grade severity from the amplitude against the limit at the harmonic frequency (spread spectrum included), optionally adding structured fields (`switching_frequency_hz`, `harmonic_range`, `band_hz`, `amplitude_dbuv_m`). Budget: output-changing — SW-001 band names, counts and severities move on every EMC unit with a switching regulator under the corpus's standard (size first; the harness EMC runner's `--standard` choice decides whether default-FCC units move at all beyond severity), and new structured keys are additive. Waits on ruling: whether `--standard` (and the EMC `--market` question in the skills record) selects the calculation standard or only the coverage labels; whether SW-001 gains structured fields (the harness needs an answer for A4-F11).

### KH-642: docs promise behaviour the code does not honour — Action base diffs for EMC/SPICE and several diffs, "agent cannot modify KiCad files", config cascade, full `diff_threshold` list, Python 3.8 support, PCBWay via ring

**Severity:** MEDIUM (user-facing promises; the safety statement is false)
**File:** `github-action.md:43`, `install-guidance.md:550-552` (Action diffs); `how-it-works.md:147` (safety); `skills/kicad/references/config-reference.md:21,148` + `skills/kicad/SKILL.md:364` (config); `skills/kicad/references/diff-analysis.md:3` (Python); `skills/pcbway/SKILL.md:94-96` (via/ring); R1/R2 minor registers (`CONTRIBUTING.md:12`, `install-guidance.md:392`, `llms.txt:21`, `standards-compliance.md:258`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R1-F5, do/R1-F9, do/R2-F14, do/R2-F15, do/R3-F13, R1 and R2 minor registers)

**Symptom:**
- **R1-F5.** The Action docs promise EMC and SPICE diffs against the base and several diffs in one report. `entrypoint.sh:315-322` re-runs only the schematic and PCB analyzers on the base. The loop at `:325` needs `base/emc.json` / `base/spice.json`, which nothing produces. The selection loop at `:333-338` `break`s on the first diff, so only one diff reaches the report.
- **R1-F9.** The doc says "the agent itself has no ability to modify your KiCad files directly", but `.codex-plugin/plugin.json:20` declares `Write` / `Shell`.
- **R2-F14.** The doc describes cascading config discovery for an explicit path. `project_config.py:170-177` loads only the explicit path, with no cascade, and a missing file silently returns `DEFAULT_CONFIG`. The documented `diff_threshold` list is incomplete: `VALID_DIFF_THRESHOLDS` (`:49`) is `all, minor, major, breaking`.
- **R2-F15.** The doc says Python 3.8+. `kicad_core/cli.py:65` uses `-> str | None` without `from __future__ import annotations`, which raises TypeError at import on 3.8/3.9.
- **R3-F13.** The PCBWay table gives a 0.30 mm via with a 0.15 mm drill, which leaves a 0.075 mm ring. The same table states a 0.15 mm minimum ring.
- **Registers.**

  | Location | Says | Actual |
  |---|---|---|
  | `CONTRIBUTING.md:12` | 18 reference guides | 20 |
  | `install-guidance.md:392` | 12 skills | 11 |
  | `llms.txt:21` | 42 checks / 17 categories | 44 / 18 |
  | `standards-compliance.md:258` | the analyzer "doesn't calculate impedance" | `pcb/routing.py:576` `_microstrip_impedance` does |
  | mouser docs | the provider "stays comfortably under" 30 calls/min | `provider_mouser.py:21` `DEFAULT_DELAY = 1.0` allows ~60/min |

**Fix direction / budget:** narrow the Action text to what runs (one diff, schematic and PCB base re-runs only). Replace the safety sentence (two-span substitution). Describe explicit-path loading and the full threshold list. Change the Python requirement to "3.10+" and sweep the other "Python 3.8" docstrings. Qualify the PCBWay row (PTH ring vs via) after checking PCBWay's current page. Correct the register counts. Output-neutral. The Action code side (generate base EMC/SPICE, report every diff) is architecture A5-F4, filed separately. Waits on ruling: implement the extra Action diff lanes in 3.0.x (feature work).

**Rider (from `docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-N1):** `skills/bom/scripts/bom_manager.py:182` and `skills/bom/references/part-number-conventions.md:329` say the built-in DNP attribute arrived in KiCad 9; the `(dnp yes/no)` symbol attribute arrived in KiCad 7.0.

### KH-641: `output-schema.md` and the kicad SKILL/reference JSON guides describe fields the analyzers do not emit — top-level `file`, PCB `pads[]`, `sch_sheetname`, `subcircuits` as hierarchical sheets

**Severity:** MEDIUM (agents reading the JSON as instructed hit missing keys or misread `subcircuits`)
**File:** `skills/kicad/SKILL.md:373,390,399`; `skills/kicad/references/supplementary-data-sources.md:217-218`; `report-generation.md:479`; `output-schema.md:112` (generated from `skills/kicad/scripts/envelopes/schematic.py:263`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R2-F12, with the generated-row parts of do/R2-F16)

**Symptom:**
- **Top-level `file`.** `analyze_schematic.py:109` and `analyze_pcb.py:134` `pop("file")`, so the envelope has no top-level `file`.
- **PCB pads.** `pcb/presentation.py:156` drops `pads` from each footprint summary and `:173` adds `pad_nets` instead. The docs still say `pads[].net_name` / `pads[].number`.
- **Sheet names.** `pcb/reader.py:473-476` emits `sheetname` / `sheetfile`, not `sch_sheetname` / `sch_sheetfile`.
- **Subcircuits.** `schematic/ic_analysis.py:512-519` builds `subcircuits` as IC neighbourhoods, but the envelope description at `envelopes/schematic.py:263` (and so `output-schema.md` and `--schema`) calls them "Hierarchical sub-sheets".

**Fix direction / budget:** fix the SKILL and reference lines (line-neutral at the 850 ceiling). Correct the envelope `description` metadata at the source and regenerate `output-schema.md` with `gen_output_schema_md.py`. Fold in R2-F16's residue wording in the generated rows through the same metadata. Budget: **`--schema` description strings change** for the schematic (and pcb if touched) envelopes. Re-baseline the `--schema` oracle (×6 md5 set) with an allow entry; no corpus budget. Waits on ruling: whether to remove the never-emitted optional PCB bags from the envelope (a schema change). The fix is description-only until then.

### KH-640: SPICE docs overclaim what the simulator does — parasitics on every subcircuit with relative thresholds, a typed datasheet tier that never runs, inconsistent validation counts, model-table sizes, a dead reference path

**Severity:** MEDIUM (users assume layout parasitics or typed datasheet specs were simulated when they were not)
**File:** `skills/spice/SKILL.md:98-100,315-317`; `skills/spice/references/simulation-models.md:29,401-404`; `spice-integration.md:82,190-195`; `README.md:284`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R3-F9, do/R3-F12, do/R1-F8 (spice-integration.md part), R1 register SPICE rows)

**Symptom:**
- **R3-F9.** The docs say `--parasitics` helps with LC filters and high-impedance feedback, injects trace R above 0.1 % of the smallest resistor and via L above ~10 MHz, and injects coupling C. In the code:
  - `_get_parasitic_lines` has one call site, the low-pass RC branch (`spice_templates.py:198`);
  - its thresholds are absolute (≥0.001 Ω, ≥0.01 nH, `:123-136`);
  - coupling C is never injected.

  This is the doc scope of KH-487, which covers the name-matching code.
- **R3-F12.** The docs put a typed `datasheet_types` lookup tier in the model cascade. `skills/spice/scripts` has no `datasheet_types` / `lookup(` call; the resolver goes fetch_specs → APIs → legacy `spice_specs` (`spice_spec_fetcher.py:556-628`).
- **R1-F8 (spice part).** The validation table does not add up: 28,544+1,297+5+922 = 30,768, which is 122 over the stated 30,646.
- **R1 register rows.**
  - `README.md:284` says "~100" opamp models; `OPAMP_SPECS` has 49 keys (`spice_part_library.py:31`).
  - `CRYSTAL_DRIVER_SPECS` has 24 keys (`:267`), which the doc misstates.
  - `spice-integration.md:82` points at a nonexistent `kicad/references/datasheet-extraction.md`.

**Fix direction / budget:**
- describe the parasitics feature as RC low-pass only, with absolute thresholds and no coupling C;
- drop the typed tier from the cascade;
- apply the R1-F8 After text for the SPICE table;
- correct the counts and the path.

Output-neutral. Waits on a ruling: add the typed datasheet tier in code later. That change is output-changing for spice-offline and is the same item as skills-code A2-F13, filed once.

### KH-639: EMC and thermal docs state a severity vocabulary and risk-score formula the analyzers do not use, and omit two emitted EMC rules

**Severity:** MEDIUM (documented scoring and severities disagree with every EMC/thermal run; a reader of the report misreads the score)
**File:** `emc-precompliance.md:143-165`; `README.md:325-331,395`; `example-report-1.md:295-323`; `example-report-2.md:338`; `skills/emc/references/emc-methodology.md:92,106-110`; `skills/emc/references/pcb-emc-rules.md` (Severity fields; CK-004/ML-001 absent); `skills/emc/SKILL.md:101,113`; `skills/kicad/SKILL.md:562-568`; `skills/kicad/references/report-generation.md:595ff`, `design-intent.md:110`, `diff-analysis.md:142`, `manual-schematic-parsing.md`, `pcb-layout-analysis.md`, `standards-compliance.md`, `gerber-parsing.md:727`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R1-F7, do/R2-F13, do/R3-F7, do/R3-F8)

**Symptom:**
- **EMC scoring (R1-F7, R3-F7).** `analyze_emc.py:45` uses `SEVERITY_WEIGHTS = {'error': 12, 'warning': 3, 'info': 0}`, applies a confidence multiplier at `:87` and clamps at `:90`. Per-net scoring (`:100-112`) has no 3-per-rule cap and applies ×1.5 to SPICE-verified findings. The docs describe a different weight set and the cap. "0 (low baseline risk)" contradicts the docstring at `:62`, where 0 is worst.
- **SU-001 (R3-F7).** `emc_rules.py:1467` emits SU-001 at `INFO` on two-layer boards and `HIGH` otherwise; the docs give a single severity.
- **Thermal and diff vocabulary (R2-F13).** The thermal rule→severity mapping is TS-001/TS-002 error, TS-003/TS-004 warning, TS-005/TP-001 info, TP-002 warning (`analyze_thermal.py:532-736`). The kicad SKILL table and references use the old names. `diff_engine.py:887` compares the normalised `error`, not "CRITICAL".
- **Missing rules (R3-F8).** CK-004 (`emc_rules.py:1320`) and ML-001 (`:4469`) are emitted but appear in neither `pcb-emc-rules.md` nor emc `SKILL.md`.

**Fix direction / budget:** one vocabulary sweep:
- the error/warning/info names and the real score equation;
- the 7 kicad SKILL.md cells, line-neutral;
- an "archived review" banner on the example reports, keeping their measurements;
- inserts for CK-004/ML-001 (emc SKILL.md +1 line; no ceiling there).

Output-neutral. Related: KH-490 (the `--severity` argparse vocabulary) and KH-471 (export_issues labels) are the code-side vocabulary items and stay separate. The emc-methodology.md:92 equation is also reported from the skills-code bundle (A1-F10); file once.

### KH-638: datasheet consumer docs describe an API and a trust contract the code does not have — nonexistent `get_thermal_params`, wrong regulator keys, `if feat:` read as a quality gate, invalid `evidence_source`, phantom typed categories

**Severity:** HIGH (contributor-facing; the quality-gate misreading means low-score or stale facts are treated as trusted with no visible sign)
**File:** `docs/datasheet-extraction.md:104,248-259,256-273,285`; `skills/datasheets/references/extraction-schema.md:3,5,380`, `quality-scoring.md:3`, `field-extraction-guide.md:3,202`, `cache-layout.md:34,54-64,120-142,159-180`, `consumer-api.md:134`; `skills/datasheets/SKILL.md:54,56`; `skills/kicad/references/datasheet-verification.md:23-28`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R1-F3, do/R1-F2, do/R1-F6, do/R3-F10, do/R3-F11, do/R3-F6, do/R2-F10, R3 register row consumer-api)

**Symptom:**
- **R1-F3 (High).** The doc tells consumers to use `if feat:` as a trust check. That is not a gate:
  - `_quality_v14` (`datasheet_features.py:108-121`) is documented as "Describes — never gates";
  - `get_regulator_features` returns `derived` with `quality` attached even when the extraction is untrusted (`:286-290`);
  - so `if feat:` passes low-score and stale facts.

  The doc also recommends `evidence_source="datasheet_extraction"`. That value is not in `VALID_EVIDENCE_SOURCES` (`finding_schema.py:14-17`), so `make_finding` raises.
- **R3-F10 (Medium).** `extraction-schema.md:380` says an older-version extraction "is treated as unavailable". `_quality_v13` also only describes the data and returns it. The legacy v1.3 guides (extraction-schema, quality-scoring, field-extraction-guide) never call themselves legacy, while `merge_results.py:123-142,273` writes the v1.4 envelope with a 0–100 score.
- **R1-F2 (Medium).** The example imports `get_thermal_params`, which does not exist, so copying it raises ImportError. It also reads regulator keys `en_threshold_v` / `pg_present`. The real keys (`:176-187`) are `topology, has_pg, has_soft_start, iss_time_us, en_v_ih_max, en_v_il_min, vin_pin, vout_pin, en_pin, pg_pin` (+ `quality`).
- **R1-F6 (Medium).** The doc says `DatasheetFacts` carries typed category attributes. `regulator` is the only one (`extraction.py:110-125`), and the docstring at `:103` defers new categories to v1.5.
- **R3-F11 (Medium).** `cache-layout.md` describes:
  - a SHA-dedup `pdfs` manifest, which nothing writes;
  - a manifest shape that differs from `{schematic, last_sync, parts}` (`manifest.py:83`);
  - filename sanitising that drops `.`, whereas `_UNSAFE_CHAR` (`cache_reader.py:42`) keeps it;
  - a `datasheets sync` CLI that does not exist.
- **R3-F6 (Medium).** The guide calls the LDO dropout "Min … worst case". Worst case is the Max column. `spice_model_generator.py:117-130` clamps on `dropout_mv`.
- **R2-F10 (Medium).** The doc says datasheet verification runs the `required_external` / `application_circuit` checks. The v2 adapter (`datasheet_verify.py:160-170`) has neither field, and `:406-412` / `:564-572` emit `extraction_not_verifiable` instead.
- **Register row.** `consumer-api.md:134` uses severity `"INFO"`, which `VALID_SEVERITIES` (`finding_schema.py:12`) rejects.

**Fix direction / budget:** apply the reports' replacements:
- the real function names and keys (check the `get_mcu_features` key list against `:330-373`);
- a Trust Gates block that tests `quality` explicitly;
- the valid `evidence_source`;
- `regulator` as the only typed category;
- "legacy v1.3" labels and the current-score paragraph;
- the cache-layout guide marked as the current manifest, with `pdfs` labelled unpopulated;
- Max for dropout;
- the two `extraction_not_verifiable` inserts;
- lowercase `info`.

Output-neutral for the analyzers. Waits on a ruling for whether to implement the SHA-dedup `pdfs` manifest or keep it as an unpopulated future contract.

### KH-637: agent-read kicad references give wrong electrical and geometry formulas — Zener power, IPC-2221 widths, 90°/270° pin rotation, anti-alias criterion, `what_if --target` gain units, boost battery current, and broken manual-fallback parsers

**Severity:** HIGH (agents apply these references during every design review; wrong numbers lead to wrong review advice)
**File:** `skills/kicad/references/schematic-analysis.md:339` (Zener), `:817` (anti-alias), `:1020` (battery current); `pcb-layout-analysis.md:160-161` + `standards-compliance.md:133-141` (IPC-2221 tables); `net-tracing.md:35-45` + Complete Example (rotation); `what-if.md:467,470` (`--target`); `manual-pcb-parsing.md:297-319,329-359` (zone and outline helpers); `manual-gerber-parsing.md:398-417` + `gerber-parsing.md:712-721` (Excellon units)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R2-F1, do/R2-F2, do/R2-F3, do/R2-F4, do/R2-F5, do/R2-F11, do/R2-F6, do/R2-F7)

**Symptom:**
- **R2-F1 (High).** Zener dissipation is given as `(VIN−VZ)·IZ`, which is the series resistor's power. The Zener dissipates `VZ·IZ`. At 12 V / 9.1 V / 20 mA that is 182 mW, against the doc's 58 mW, so the agent under-rates the part.
- **R2-F2 (High).** IPC-2221 recomputed with k=0.048, ΔT=10 °C, 1 oz external copper:

  | Width | Doc | IPC-2221 |
  |---|---|---|
  | 1.0 mm | 1.4 A | 2.38 A |
  | 5 A needs | 1.0 mm cap for 1–5 A (layout table) | 2.78 mm |
  | 20 A needs | — | ≈18.8 mm |

  The reviewer's replacement cells 0.60/0.87/1.44/2.38/3.94/5.28/7.65 reproduce from the formula.
- **R2-F3 (High).** The 90° and 270° rows of the pin-rotation table are swapped. `schematic/reader.py:164-168,213-228` is the transform checked against kicad-cli (48/48). Pin (0,3.81) on a resistor at (152.4,176.53) rotated 90° lands at (148.59,176.53); the doc says 156.21.
- **R2-F4 (High).** The doc says "ensure f_min is still above the Nyquist frequency". This is backwards: an anti-alias filter needs f_max well below fs/2, with the required attenuation there.
- **R2-F5 (High).** The doc presents `--target 20` as 20 dB. `what_if.py:1362-1366` maps `--target` to `fields[0]`, and `detection_schema.py:302-306` lists `gain` first, so 20 is a linear 20× (≈26 dB). `gain_dB` is reached only through an explicit field (`:210-211`).
- **R2-F11 (Medium).** Boost battery current is given as `I_load/η`, which leaves out the voltage ratio. The correct expression is `V_load·I_load/(V_bat·η)`. For 3 V → 5 V at 100 mA and 85 %, that is 196 mA against the doc's 118 mA.
- **R2-F6 (Medium, fallback-only).**
  - Zone helper: `in_target_zone` is only ever assigned False, so the helper always returns `[]`.
  - Outline helper: it drops its buffer at the first line ending in `)`. In the KiCad 7+ multi-line `gr_line` that line is `(start …)`, which comes before `(layer "Edge.Cuts")`, so no outline segment is ever kept.
- **R2-F7 (Medium, fallback-only).** Both Excellon snippets scale coordinates with an `x > 1000` magnitude heuristic, so a negative or small integer X is mis-scaled. `gerber-parsing.md:721` also says "decimal points ⇒ inches", but KiCad's metric decimal drill format exists. `analyze_gerbers.py:429-439` decides by the decimal point and the declared format.

**Fix direction / budget:** apply the reports' replacement text. For R2-F4 use the record's plainer sentence. When applying R2-F3, re-derive the Complete Example step-4 wire coordinate. When applying R2-F5, check the sign convention for inverting gain. R2-F6/F7 replacements point at the shared parser and the declared format. Output-neutral (references only). The Excellon code-side twin (02-v3-kicad-code A10-F10, numeric formats guessed) is filed separately.

### KH-636: documented commands and workflows fail or destroy user data — `--recursive` sync flag rejected, opencode config corrupted, manual BOM rows deleted, nonexistent Action outputs, repo-relative Deep Review paths, wrong flag precedence

**Severity:** HIGH (user-facing install and skill commands; two of them destroy user data: the opencode config and manual BOM rows)
**File:** `skills/bom/SKILL.md:76-78` (sync step); `install-guidance.md:401` (opencode); `skills/bom/SKILL.md:267` (BOM re-export); `install-guidance.md:632-635` (Action outputs); `skills/kicad/SKILL.md:702,717`, `skills/kicad/references/deep-review.md:113,120,134`, `skills/kicad/references/datasheet-verification.md:41` (Deep Review paths); `skills/kicad/SKILL.md:303-306` (output precedence); `skills/datasheets/references/dispatch-claude-code.md:168-176` (annotations addendum); `install-guidance.md:691-692` (DigiKey auth)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R3-F3, do/R1-F1, do/R3-F2, do/R1-F4, do/R2-F9, do/R2-F8, do/R3-F5, do/R1-F10)

**Symptom:**
- **R3-F3 (High).** The bom SKILL "Do this immediately" step passes `--recursive` to the sync CLIs. None of the three sync CLIs defines that flag (`--help` checked), so argparse exits 2. The doc also says a second provider can retry the first provider's misses. It cannot: `distributor_core/sync.py:171-173` skips any part whose stored status in the shared `datasheets/manifest.json` (`manifest.py:56-76`) is `failed` / `not_found` / `no_datasheet` unless `--force` is given.
- **R1-F1 (High).** The opencode step runs `cat >> ~/.config/opencode/opencode.json <<'EOF'` and appends a whole `{...}` root object. On an existing config this leaves two concatenated JSON documents, which is invalid JSON in the user's own file.
- **R3-F2 (High).** The doc says manually added BOM rows (for example `Reference=--`) survive re-export. In `bom_manager.py:827-888`, rows come only from the schematic `bom`. Existing rows only donate user columns to rows that match by MPN or first ref, and the file is rewritten with `"w"`, so an unmatched manual row is deleted without warning.
- **R1-F4 (High).** The doc lists Action outputs `emc-json`, `status` and `critical-count`. `action.yml:47-62` declares only `schematic-json, pcb-json, report-path, findings-count, has-critical`, and `entrypoint.sh` writes only those. A workflow that tests the documented names gets an empty string.
- **R2-F9 (High).** The two Deep Review gate commands use repo-relative `skills/kicad/...` paths. Every other command uses `<skill-path>` (defined at `SKILL.md:138`), and the repo-relative form fails from a hardware-project cwd. `datasheet-verification.md:41` names a sync script under `skills/kicad/scripts`, but the only one is in `skills/digikey/scripts`. The gate is the mandatory v2 step.
- **R2-F8 (Medium).** The doc says "`--output` wins" over `--analysis-dir` for every CLI. `analyze_schematic.py:126/133` and `analyze_pcb.py:152/159` check `analysis_dir` first, so `--analysis-dir` wins there. Only `analyze_gerbers.py:1639` lets `--output` win.
- **R3-F5 (Medium).** The doc tells the user to run `merge_annotations.py --review review_annotations.json --raw-dir analysis/`. Nothing produces `review_annotations.json` any more (the reviewer task is retired, and design_context writes `design_context.json`). `merge_annotations.py:94-96` reads `--review` unconditionally, so the command ends in a traceback. `--raw-dir analysis/` also predates the `analysis/<run_id>/` layout.
- **R1-F10 (Medium).** The doc describes a browser OAuth flow with a refresh token. `provider_digikey.py:159-190` `get_oauth_token` makes a plain `client_credentials` POST and gets back only `access_token`.

**Fix direction / budget:** apply the reports' After text in one docs commit:
- drop `--recursive` and say that `--force` is needed for a cross-provider retry;
- make the opencode edit preserving, with a create-if-absent block;
- say that re-export keeps only schematic-backed rows;
- list the five real Action outputs (add `has-critical`);
- use `<skill-path>` in the Deep Review commands, line-neutral at the 850-line SKILL.md ceiling;
- state the per-CLI precedence, line-neutral 4→4;
- point the annotations step at the current inputs and the run directory;
- describe the client-credentials DigiKey flow.

Output-neutral. Code-side twins are filed separately from the skills-code bundle: export that preserves unmatched rows (sk/R5-F8) and cross-provider retry (sk/R4-F3). Waits on rulings for 3.0.x code work: harmonise output precedence across the three CLIs (R2-F8), make export preserve unmatched rows (R3-F2), and let a second provider retry another provider's misses (R3-F3). Each of these changes output and needs a budget.

### KH-635: `escape_kicad_string` does not escape newlines, and property names are written unescaped, so BOM tools can write a broken KiCad string

**Severity:** LOW (only for values/names containing newlines or quotes; record rates it Low/Medium)
**File:** `skills/bom/scripts/kicad_sexp.py:75` (`escape_kicad_string` escapes only `\` and `"`); `skills/bom/scripts/edit_properties.py:132` (new property name interpolated unescaped), `:221-228` (escaped `old_value` compared with decoded `new_value`); `bom_manager.extract_properties` `:162-170` (returns escaped values)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-N2; R5 spot check #2) — remainder of review-period periphery I11; no open KH covers it (KH-495 does not list it)

**Symptom:** a value with a raw newline is written inside a quoted KiCad string unescaped (KiCad writes `\n`); a property name with `"` breaks the s-expression. Separately, a value holding `"` or `\` never compares equal to its update, so an identical update is logged "updated" and re-written, and `extract_properties` hands escaped text into MPN/Value.

**Fix direction / budget:** escape `\n` (and `\r`, `\t` as KiCad does) and escape property names; compare decoded to decoded. Align with the `kicad_core/sexp.py` writer. Budget: output changes only for such inputs (schematic write-back). Overlaps KH-365 item (3) (no unescaping) — close together if the BOM tools move to the shared parser.

### KH-634: `search_lcsc` overwrites a JLCPCB stock of 0 with LCSC warehouse stock after filtering and sorting, so displayed stock disagrees with `--in-stock` / `--sort stock`

**Severity:** MEDIUM (LCSC search CLI; not the sync path)
**File:** `skills/lcsc/scripts/search_lcsc.py:186-187` (`if not item.get("stock")`), `:128-130`, `:154` (`normalize_component` maps absent to 0), `:302-329` (filter/sort before enrichment), `:283-290`, `:338`, `:342`; `provider_lcsc.py:140-142`, `:160`; `lcsc/SKILL.md:239`; test `test_search_lcsc.py:296-302`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R4-F8, sk/R4-F10; R4 spot check #3)

**Symptom:** a jlcsearch row with `stock: 0` survives (no `--in-stock`), then enrichment replaces it with LCSC `stockNumber`, so the output shows LCSC stock for a row selected as JLCPCB-out-of-stock; absent and 0 are indistinguishable after normalisation. `test_cli_sort_price` passes with no sort (fixture rows already ascending). Rider: an exact-code search with both endpoints failing exits 1 instead of the documented 2 (jlcsearch exception swallowed at `:283-290`, direct returns None).

**Fix direction / budget:** keep a missing-vs-zero sentinel through normalisation and never overwrite a real 0; a separately named LCSC field if both are wanted; exit 2 on network failure. Waits on ruling: what `stock` means (recommended: jlcsearch/JLCPCB when a row exists). Budget: stock values on zero-stock exact-code / `--details` hits; distributor-oracle neutral.

### KH-633: datasheet extraction prompts ask for shapes the schemas reject (no-pinout base, scalar MSL, list compliance, `analog_in`, string `alt_functions`) and misstate which fields are required

**Severity:** MEDIUM (opt-in LLM extraction; failure is loud — schema rejection → retry → `_extraction_failed`)
**File:** `skills/datasheets/prompts/base.md:11`, `:20`, `:21`, `:28`; `prompts/pinout.md:15`, `:19`; `prompts/regulator.md:23`; validation on raw data `merge_results.py:209-224`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F4; same prompts as `docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R3-F1, which rates it HIGH because every extraction that follows the prompts is rejected)
**Symptom:** jsonschema 4.26 on the prompts' own shapes: no-pinout base → "'pinout' is a required property"; `moisture_sensitivity: 3` → not object/null; `compliance:['RoHS']` → not object; pinout `type:'analog_in'` → not in the 11-token enum; `alt_functions:['USART2_TX']` → not object. base.md:28 says every field is nullable except `package`; required is family/package/absolute_max/recommended_operating/pinout. The regulator schema has no generic `ceramic` dielectric token, though many LDO datasheets say only "ceramic".

**Fix direction / budget:** rewrite the prompt examples to the schema shapes. Waits on ruling: a generic-ceramic token (otherwise an extractor must invent a dielectric or drop the fact). Budget: prompt text only, analyzer-output neutral.

### KH-632: datasheet completeness score gives full category credit to five of six categories and a free 30 points for `reserved_v15`, so a sparse MCU extraction scores 71

**Severity:** MEDIUM (visible quality metadata; gates `extraction_quality_low` and `_quality_v14.trusted`)
**File:** `skills/datasheets/scripts/datasheet_score.py:361-367` (`_CATEGORY_FIELD_REQS` has only `regulator`), `:424-426`, `:449`; legacy pin scorer `:94-127` (unnamed pin `:111-112` adds no counter; `pins_with_specs` `:107` never read); `datasheet_features.py:107-119`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F3; R3 spot check #2)

**Symptom:** the report's sparse MCU example scores exactly 71 (pinout .5, base .25, category 1.0, reserved 1.0) — over the 60 threshold, so `extraction_quality_low` is suppressed and `trusted` is set. A topology-only regulator scores ≈51 (real rubric). Legacy scorer: N unnamed pins at the expected count score 10/10 on pin coverage.

**Fix direction / budget:** per-category field requirements for the other five categories, no free credit for reserved fields, count unnamed pins. Waits on ruling: score thresholds, with frozen examples. Budget: score values and `trusted` flags on extractions (deterministic detectors are affected only through regulator/MCU features).

### KH-631: SPICE `--parasitics` applies the first copper layer's thickness to every trace segment

**Severity:** MEDIUM (opt-in `--parasitics` / standalone CLI; wrong R on mixed-copper boards)
**File:** `skills/spice/scripts/extract_parasitics.py:149`, `:155-158` (first `type=="copper"` thickness, then `break`), `:191` (`trace_resistance(len, width, copper_thickness)`), `:195` (`seg["layer"]` recorded); stackup `pcb/reader.py:59-70`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F12)

**Symptom:** on a board with 35 µm outer / 70 µm inner copper every segment uses the first layer's thickness; 1.68e-8·0.0254/(0.000254·0.000035) = 48 mΩ vs 24 mΩ at 70 µm. The per-layer `name` → `thickness` map is already in `setup.stackup`.

**Fix direction / budget:** look up thickness by `seg["layer"]`. Budget: only under a SPICE profile that passes `--parasitics` (neutral for spice-offline). Sibling of KH-487 (same feature, different defect).

### KH-630: SPICE net-name sanitiser maps distinct nets to one node and does not reserve the testbench's own node names

**Severity:** LOW (rare collisions; usually a silently dropped run)
**File:** `skills/spice/scripts/spice_models.py:166-167` (char-replace loop); guard `spice_templates.py:177-178`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F10)

**Symptom:** `IN/1` and `IN?1` map to the same node; nothing reserves `ac_in`, `sig_in`, `VCC`, `VEE`, `fb_net`, `port`; ngspice node names are case-insensitive. Result: a guarded `None` (run dropped without a record) or, rarely, a short between nets.

**Fix direction / budget:** an injective, case-folded name map with the reserved names excluded. Budget: changes only on colliding designs (size first; expected tiny).

### KH-629: SPICE LTspice and Xyce backends lose their measurements — the LTspice `.log` is overwritten by the capture, and `let` / `extra_vars` / rise-fall are never emitted

**Severity:** MEDIUM (LTspice is the auto-detected engine when ngspice is absent, common on Windows/macOS; results skip rather than mislead, except the crystal bench)
**File:** `skills/spice/scripts/simulate_subcircuits.py:238-239`, `:269` (`<label>.log` opened "w" after `run()`); `spice_simulator.py:304-305` (`parse_results` derives `<label>.log` from `<label>.out`), `:317` (`encoding="utf-8", errors="replace"`), `:288-290` and `:400-402` (`elif func == "let": pass`), `:416-417` (Xyce `<label>.mt0`), `:473-477` (auto-detect falls through to LTspice)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F7, sk/R2-F8)

**Symptom:** on LTspice the native `.meas` log is replaced by the subprocess capture before parsing, so every measurement is lost → skip; native logs are commonly UTF-16LE, which defeats the `^(\w+):` regex even after a rename. On both alt backends every `let`-only result (divider `vout_sim`, `error_pct`, LC `f_peak`, op-amp `target`, …) is absent, `extra_vars` is accepted and dropped, rise/fall is dropped, and `when … =target_lo` names undefined values. The crystal bench passes on `{}` (KH-612). Xyce names measure files `<netlist>.cir.mt0` (convention, unverified here). Static reading only — no LTspice/Xyce installed.

**Fix direction / budget:** write the capture to a different file and decode UTF-16; translate lets to `.meas … param=` or compute them outside the simulator; or reject the alt backends explicitly until fixed. Waits on ruling: fix or reject. Budget: LTspice/Xyce users only; outside the ngspice-only spice-offline gate.

### KH-628: EMC switching-harmonic FFT runs Goertzel on ngspice's adaptive time points, and the steady-state fallback keeps a `dt` from the wrong start index

**Severity:** LOW (opt-in `--spice-enhanced` + ngspice; ≤0.4 dB effect)
**File:** `skills/emc/scripts/emc_spice.py:466-467` (fallback `steady_values = values`), `:471` (`dt` from `times[start_idx]`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F9)

**Symptom:** 12 V / 40 % / 10 ns / 1 MHz: `wrdata` after `run` writes 20,245 points with dt 1e-11…1e-9 s; Goertzel assumes uniform spacing. Against the analytic trapezoid: h1 7.273/7.264, h2 2.221/2.244, h3 1.517/1.495, h7 0.614/0.636 (≤0.4 dB). On the fallback branch the sample rate is wrong outright.

**Fix direction / budget:** `linearize v(sw)` before `wrdata` (20,001 uniform points at 1e-9 s); compute `dt` from the samples actually used. Budget: tiny EE-002 amplitude changes under `--spice-enhanced` only.

### KH-627: EMC DP-002 predicts cable radiation with a short-monopole model far outside its domain (≈20–35 dB high) and labels the table assumption `datasheet-backed`

**Severity:** MEDIUM (default EMC path on HS/SS/HDMI/Ethernet/LVDS pairs; the verdict direction often survives)
**File:** `skills/emc/scripts/emc_rules.py:2169-2213` (DP-002, `:2179`, `:2195`); `emc_formulas.py:170`, `:182`, `:800-819`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F5)

**Symptom:** USB-HS 20 ps skew → 8 mV → 87.0 dBµV/m at 1 GHz vs a 54 limit, using a 1 m cable against λ/4 = 0.075 m; the short-monopole field grows ∝ f·L while a real electrically long cable saturates. A half-wave-dipole bound (`E ≈ 60·I/r`) gives 60.6 (USB-HS), 57.3 (HDMI 1 mm), 53.2 vs 43.5 (Ethernet 5 mm), 54.2 (LVDS 2 mm) dBµV/m. The confidence label says `datasheet-backed` for a protocol-table assumption.

**Fix direction / budget:** a bounded radiation model, or report DP-002 as advisory. Waits on rulings: bounded model vs advisory; what `datasheet-backed` means (also TH-001/TH-002; KH-437 adjacent). Budget: DP-002 margin, description and confidence move (size first).

### KH-626: the product refactor oracle (`tools/check_refactor.py`) passes on unseen key reorders, relative snapshot roots, a write-then-fail analyzer, unknown budget selectors and worsened tag sites

**Severity:** MEDIUM (dev-only oracle and CI `tags` guard; no stored baseline is contaminated today)
**File:** `tools/check_refactor.py:121-123` (`order` delta only when key sets are equal); `:1002`, `:976-977`, `:942`, `:947`, `:413-417`, `:990`, `:1232` (`run_text_snapshot` with relative roots under `cwd=work/"cwd"`; no positive-exit check); `:343-348` (`_produce` fails only on an absent target); `:224-233`, `:261-268`, `:1192-1196` (`_class_claims` reads only `where.rule_id`; `path` not compiled; `quick --budget` skips validation); `:442`, `:574-605` (`_tag_key` identity only; shape compared only with `moved_from`); `tools/distributor_offline.py:223-229`, `:241-242` (`_drop_provider_modules` evicts only the selected tree)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R6-F1, sk/R6-F2, sk/R6-F3, sk/R6-F6, sk/R6-F5, sk/R6-F4)

**Symptom:** (1) `{"findings":[],"summary":{}}` vs `{"summary":{},"findings":[],"diagnostics":[]}` → one `added` delta; a budget class with `kinds:["added"]` claims it and the reorder is unseen (round 8 knew and routed it to the harness `key_order` op for B2 only). (2) A relative `--fixtures`/`--product` makes every text-snapshot CLI fail in the empty cwd; empty `.txt` + nonzero `.exit` on both sides compare equal → false pass (all 8 stored text baselines have positive `.exit` = 0). (3) A fake analyzer that writes `{}` and exits 1 → `failures == []` (no current analyzer fails after writing). (4) `where:{"detector":[…]}` is ignored → the class claims a GP-001 delta; `path:"["` passes validation then raises `re.error`. (5) A baseline tag site whose `nonliteral` grows from `["detector"]` to `["detector","rule_id"]` passes `tags` rc 0, against ARCHITECTURE.md:37 "may only shrink" (3 partial sites exposed). (6) A provider module preloaded from another tree survives eviction (no in-repo caller mixes trees).

**Fix direction / budget:** compare common-key order independently of add/remove; resolve roots at the top of `run_text_snapshot` (as `cmd_aba` does at `:765`, `:772`) and fail when a non-`neg__` run exits nonzero; `if rc != 0 or not target.exists()`; one validated budget loader for `budget-compare` and `quick` (type-check, compile `path`, reject unknown `where` keys); key the ratchet on identity and reject a known site whose `missing ∪ nonliteral` grew; assert loaded provider modules live under `product`. Budget: product-output neutral; oracle verdicts and CI `tags` get stricter (3 baseline sites). Waits on ruling (tools/ oracle policy) only for magnitude enforcement and mask presence checks, not for these fixes.

### KH-625: `sync_datasheet_urls` maps bare references to URLs across every manifest part, so a replaced part's stale entry fills the new symbol's Datasheet field

**Severity:** MEDIUM (fills blank Datasheet fields only; differing URLs are warned, not overwritten)
**File:** `skills/bom/scripts/sync_datasheet_urls.py:113-128` (`build_ref_url_map`, last wins, no MPN compare), `:197-210`, `:171` (manifest opened without `encoding=`), `:107`, `:144` (docstrings/help say `index.json`); producer `distributor_core/sync.py:167` (refreshes `references` only for parts in the current sync)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-F7) — split from fix group 20; consumer half of KH-605

**Symptom:** a part that was replaced or belongs to another revision keeps stale `references` in the manifest; the URL map is built by bare ref over every part, so the new symbol at that ref gets the old part's datasheet URL, visible only in the fill log.

**Fix direction / budget:** match on the current symbol's MPN; open the manifest as UTF-8; fix the `index.json` wording. Waits on ruling: how legacy manifest entries keyed by distributor PN are matched. Budget: filled Datasheet URLs (schematic write-back, not a gated analyzer).

### KH-624: BOM manager assigns each `Supplier N` slot to one distributor for the whole project, so a symbol whose `Supplier 1` is Mouser has its Mouser PN emitted as DigiKey

**Severity:** HIGH (narrow reach: projects mixing distributors in one Supplier slot)
**File:** `skills/bom/scripts/bom_manager.py:276` (`slot not in supplier_slots`, set once), `:305-308` (project-wide `field_mapping`), `:388-392` (`get_canonical` reads `field_map["digikey"]` on every symbol)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-F3) — split from fix group 20 (different mechanism from KH-625)

**Symptom:** the first symbol that names `Supplier 1=DigiKey` fixes slot 1 → digikey for every symbol, so another symbol's `Supplier 1=Mouser` PN is exported under `digikey`. Corpus: 6 repos use the slot convention with a named distributor; 2 mix distributors in slot 1 (`EPFLXplore/Power_HW` {digikey, mouser}, `bluerobotics/ping-dev-kit` {digikey, jlcpcb}).

**Fix direction / budget:** interpret the slot name→PN pair per symbol. Budget: BOM distributor-PN columns on those 2 repos' designs (not a gated analyzer). Order after KH-603 / -15.

### KH-623: EMC EF-001/EF-002 judge a regulator's input filter from the first LC record anywhere on the board, and claim SPICE verification that never runs

**Severity:** HIGH (default EMC path, every switching regulator on a board with any LC network)
**File:** `skills/emc/scripts/emc_rules.py:2834` (`input_rail` read, unused), `:2841-2851` (first record with `resonant_hz < f_sw`), `:2884-2889` ("verified … ≥{40·log10(ratio)} dB"); `run_filter_spice` has no production caller, `spice_backend` never read; producer `skills/kicad/scripts/signal_detectors.py:728-730` (`detect_lc_filters` skips L-C pairs whose shared net is power/ground); `skills/emc/references/emc-methodology.md:132`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F4)

**Symptom:** the loop never checks `input_rail` or `shared_net`. Because the producer drops any L-C pair joined on a power net, a real input pi/LC filter (junction on VIN) is never in `lc_filters`; every EF-001/EF-002 verdict comes from an unrelated signal-net or RF LC network, one record serves every regulator, and EF-002 says "verified" though no SPICE runs. methodology.md:132 repeats the SPICE claim.

**Fix direction / budget:** require the LC to feed `input_rail`, via a producer-side record (kicad bundle) or an EMC topology walk; drop the SPICE claim from methodology.md:132 or wire it in. Budget: EF-001/EF-002 mostly disappear or are re-attributed (size first); cross-bundle with `detect_lc_filters`.

### KH-622: typed datasheet cache reader crashes on a `null` or UTF-16 cache file, and rejects a partial `body_mm`

**Severity:** MEDIUM (malformed or partial caches; reaches analyzers through unguarded `datasheet_features`)
**File:** `skills/datasheets/datasheet_types/cache_reader.py:189-200` (except tuple misses `AttributeError` / `UnicodeDecodeError`); `datasheet_types/base_block.py:35` (`body_mm` dims required); unguarded callers `datasheet_features._try_v14_facts` (`:240-253`) → `validation_detectors.py:483`, `:578`, `:1051`, `emc_rules.py:48`; guarded `lookup_helpers.py:50-54`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F8, sk/R3-F9)

**Symptom:** `P1.json` = `null` → `AttributeError: 'NoneType' object has no attribute 'source'`; `\xff\xfe{` → `UnicodeDecodeError` (json.loads on bytes auto-detects UTF-16). Whether an outer analyzer phase catches it was not traced. A schema-valid `body_mm:{length,width}` (the schema object has no `required`) → `lookup` None, so the whole fact set is lost; all three dims or none → OK.

**Fix direction / budget:** catch both inside `lookup`'s error boundary and record a diagnostic; make the dims Optional and omit nulls on serialise. Budget: changes only for malformed or partial caches (more facts reach consumers on partial `body_mm`).

### KH-621: `datasheet_verify` v2 pin adapter keeps only the first of grouped pin numbers, uses the domain limit before the per-pin `recommended`, and ignores `is_5v_tolerant`

**Severity:** MEDIUM (current v2 pipeline, default verifier path; needs a signal pin tied straight to a 5 V rail)
**File:** `skills/datasheets/scripts/datasheet_verify.py:141-142` (first of `numbers` only), `:149-160` (domain `voltage_operating_max` before per-pin `recommended`), `:235-256` (`_estimate_net_voltage`), `:329-344` (`pin_voltage_abs_max_exceeded`); smoke `_smoke_v14_roundtrip.py:114-123`, `:196-199`; prompt `prompts/pinout.md:29` mandates grouped numbers
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F7, sk/R3-F12) — split from fix group 17

**Symptom:** v2 pin `numbers:['1','2']` → only pin 1 in the view. PA9 with per-pin `recommended` max 5.5 and abs 6.0 → `voltage_operating_max` 3.6 (domain), so a 5 V net warns (margin 16.7 %). PA10 with `is_5v_tolerant: true` and no per-pin abs max takes the domain abs max 4.0 → **error** `pin_voltage_abs_max_exceeded` on a 5 V net. The round-trip smoke's only voltage assertion ("no violations at 12 V") is satisfied by a no-op verifier.

**Fix direction / budget:** expand all numbers; per-pin `recommended` (voltage units) before the domain value; honour `is_5v_tolerant`; add an over-limit smoke case. Budget: `datasheet_verification` pin-voltage findings (≈0 corpus units; confirm).

### KH-620: `datasheet_verify` decoupling counts the X5R/X7R digit (and `max`) as a capacitor quantity, pools caps across every power pin with no input/output split, and orders `actual_caps` by set iteration

**Severity:** MEDIUM (legacy v1.3-shaped caches only; one nondeterminism in the schematic envelope)
**File:** `skills/datasheets/scripts/datasheet_verify.py:507` (quantity regex; docstring example `:493`), `:590` (`power_pin_nets` is a set), `:601-613` (caps pooled across all power-pin nets, no GND-terminal check), `:621`, `:636`; v2 adapter never synthesises `application_circuit` (`:121-123`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F5, sk/R3-F6) — split from fix group 17 (the pin adapter is KH-621; the `actual_caps` order half also se/R1-F8)
**Symptom:** (1) `"10uF ceramic, X5R or X7R"` → count 5 (its own docstring says 1), `"4.7uF X7R"` → 7, `"100nF max 10mm"` → 10. In EIA class-2 codes the digit is the upper-temperature code. Harness `test_parse_cap_22uf_x2` passes only because `x2` precedes `X5R`. (2) VIN and VOUT power pins, one 10 µF on VIN-GND, nothing on VOUT, recommendations input 10 µF + output 10 µF → no finding; a missing LDO output cap is the dangerous false negative. A cap bridging two power nets is counted once per net. (3) Six power nets at PYTHONHASHSEED 0-3 → four different `actual_caps` orders in `datasheet_verification` (byte-stability breach invisible to the seed-0 gate). The dielectric list is parsed and never checked.

**Fix direction / budget:** require a non-letter after the digits and a quantity context; partition caps by recommendation role with a GND check; sort `actual_caps`. Budget: `decoupling_insufficient` presence / `required_count` / severity and `actual_caps` order — ≈0 corpus units carry `datasheet_verification` (confirm with the harness).

### KH-619: SPICE `phase_at_fc_deg` carries radians, and inrush `t_peak` indexes with a value

**Severity:** MEDIUM (spice default path, every RC filter's phase value)
**File:** `skills/spice/scripts/spice_results.py:91` (copies `phase_fc` into `phase_at_fc_deg`); `spice_templates.py:237` (`("phase_fc","find","vp(out)","at=fc_sim")`), `:1477` (`i_out[vecmin(...)]`; `vecmin` returns a value); `skills/spice/SKILL.md:176` (shows −0.78)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F11) — split from fix group 16

**Symptom:** RC low-pass 1k/10n: ngspice `vp()` returns radians, `phase_fc=-0.784197` is published as `phase_at_fc_deg: -0.784197`; should be −45°. `t_peak` would index the time vector with a magnitude (moot today: `i_out` never exists, KH-618).

**Fix direction / budget:** ×180/π at the evaluator (key kept); `t_peak` from the time vector at the max. Waits on ruling: correct values under the existing `*_deg`/`*_us` keys (recommended yes). Budget: value-only change on every RC-filter result (and `phase_at_bw`, KH-610) under spice-offline; SKILL.md:176 example.

### KH-618: SPICE reports `pass` without measuring the quantity — inrush never measures current, the regulator feedback check is a tautology, RF matching networks are chained in series, and the half-bridge bench cannot conduct

**Severity:** MEDIUM (spice default path; pass labels on unmeasured or wrong numbers)
**File:** `skills/spice/scripts/spice_templates.py:1475` (`("i_out", "let", "abs(i(Rout))")`), `:1477` (`vecmin` used as an index); `:1324` (`expected_vfb = vin * ratio`), `:1334-1336`; `:1381-1387`, `:1395` (every component in series `port`→`0`); `:1538-1542` (high-side gate tied to 0, only load `Rload mid 0`); `spice_results.py:710-711` (docstring "checks … matches the expected Vref"), `:806-812`; `detection_schema.py:100`, `:329` (MC aggregates `vfb_V`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-N4, sk/R2-F1, sk/R2-F2, sk/R2-F4) — split from fix group 16 (the units half is KH-619)

**Symptom:** (1) Inrush: ngspice-42 has no `i()` of a resistor without `.save @rout[i]` → `no such function as i`, `i_peak=None t_peak=None`, then **pass** "Transient simulated" on `v_settled` alone. (2) Regulator feedback: Vref 0.8, 82k/10k, rail `+3V3` → `vfb_sim=0.358696 error_pct=1.5e-14` **pass**, though the divider sets 7.36 V (the bench drives the same ideal divider it compares against); under `--monte-carlo` a rail with no voltage in its name recomputes `vin = vref/ratio` per sample, so the spread collapses. (The schematic `vout_net_mismatch` flags the design independently.) (3) L_match 10 pF shunt + 10 nH: ngspice `singular matrix`, `z_min=0.265 Ω @ 501 MHz` **pass**; the real input impedance at 503 MHz is 19.98−j31.6 Ω. (4) Half-bridge: the low-side FET has no supply path; both `vth_lo` and `id_on` measure out of interval → skip "ngspice DC sweep measurement failed" (a test that can never run).

**Fix direction / budget:** measure inrush through a 0 V sense source and require `i_peak` for pass; relabel the regulator check as a divider-ratio check (or compare Vref·(1+Rt/Rb) against the rail) and aggregate Vref/ratio in MC; skip `L_match`/`pi_match`/`T_match` until terminals come from nets; add a VDD→mid load and a non-endpoint `at=` for the half-bridge, or drop the high-side claim; fix the `spice_results.py:710` docstring. Waits on ruling: what SPICE "pass" means (recommended: measured and matches; presence or tautology → skip/info). Budget: pass→skip/info/warn moves on inrush, regulator-feedback and RF-matching sims under spice-offline (size first per type).

### KH-617: BOM tracking-CSV re-export deletes manual rows, copies `Validated`/stock/PNs onto a different part matched by reference, and drops extra columns not filled on the first row

**Severity:** HIGH (default `bom_manager` export over an existing tracking CSV; silent user-data loss on a documented workflow)
**File:** `skills/bom/scripts/bom_manager.py:827-888` (`rows` built only from `bom`, written out with `extrasaction="ignore"`), `:858-875` (`existing.get(mpn)`, then first-reference fallback with no identity check; copies user columns incl. `Validated` and stock `:868-871`, CSV-only distributor PNs `:872-875`), `:781-785` (`load_existing_csv` keys rows by MPN only), `:814-819` (extra distributor columns sampled from the first row only)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-F8, sk/R5-F2; R5 spot check #1)

**Symptom:** (1) `bom/SKILL.md:267` tells users to add `Reference=--` rows; re-export never appends unmatched existing rows, so they are deleted (several MPN-less `--` rows also collapse to one key). (2) After an MPN change, the fallback matches the old row on the first reference and carries `Validated=yes`, stock and any CSV-only distributor PN onto the new part — the `Validated` carry-over happens even when the PN came from the schematic. (3) Two groups sharing an MPN (different value text or footprint) overwrite each other in `load_existing_csv`. (4) A distributor column not in `active_distributors` survives only if the first CSV row has a value in it; values on row 2+ are lost.

**Fix direction / budget:** keep manual rows; invalidate `Validated`/stock/PNs when the identity changes; key existing rows by the group identity; collect the extra columns over all rows. Waits on ruling: whether `Reference=--` rows live in the tracking CSV or only in `non-bom-items.csv`. Budget: tracking-CSV row count and columns (not a gated analyzer).

### KH-616: distributor sync loses worker exceptions under `--parallel`, schedules a repeated MPN twice with colliding `.part` files, and `--json` output is preceded by a stdout progress line

**Severity:** MEDIUM (opt-in `--parallel` / `--json`; multi-row MPNs on the default path)
**File:** `skills/datasheets/distributor_core/sync.py:261` (`executor.map(_process_part, to_download)` never iterated; no try in `_process_part` `:224-258`), `:175`, `:167`, `:275`, `:195-205` (no-work early return without a JSON dump), `:313`; `inputs.py:100`, `:109-145` (`extract_parts` appends each BOM row, docstring says "unique parts"); `download.py:112` (shared `.part` name), `:130` (`print(f"Downloaded ...")` to stdout); `provider_element14.py:146-147` (`product.get("datasheets", [])` TypeError on null); fetch CLIs e.g. `fetch_datasheet_digikey.py:121-124`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R4-F4, sk/R4-F6, sk/R4-F5)

**Symptom:** (1) with `--parallel`, a worker exception (e.g. element14 `datasheets: null`) vanishes; the summary undercounts and the CLI exits 0 (serial mode tracebacks instead). (2) `bom_stats.py:28` groups by `(value, footprint, mpn)`, so one MPN can be several rows; both are scheduled, serial downloads twice, the stored `references` hold only the last group (so `bom/sync_datasheet_urls.py:122` writes back to those refs only), and parallel workers race on the same `.part` file. (3) every fetch CLI and `sync --json` print "Downloaded …" to stdout before the JSON; a no-work `--json` sync emits no JSON at all (consumer: the agent following "JSON output for script integration", digikey SKILL.md:294-295).

**Fix direction / budget:** consume the futures; coalesce rows by effective key with references unioned in stable order and unique temp names; progress to stderr and JSON on every `--json` return. Waits on ruling: which metadata wins when rows coalesce (recommended first-seen BOM order). Budget: user-visible output (counts, references, stdout transcripts) changes; distributor-oracle neutral (no parallel run, no repeated MPN in the fixture BOM; the oracle fakes `download_pdf`) — verify.

### KH-615: distributor sync marks a PDF transport failure as permanent, one provider's failure blocks every other provider, and LCSC sync never tries the direct lookup

**Severity:** MEDIUM (default distributor sync; missing datasheets, visible skip count, recoverable with `--force`)
**File:** `skills/datasheets/distributor_core/download.py:133-134` (`except Exception: pass`), `:138` (`return False`); `provider_digikey.py:385-394` (`status: failed`), `:298-306` (failure entries carry no provider); `distributor_core/sync.py:67` (`_outage_entry` acts on `not_found` only), `:171-173` (unattributed skip), `:275` (`--force-all` overwrites a prior `ok`), `:343`; `skills/lcsc/scripts/provider_lcsc.py:310`, `:313`, `:359`, `:381-390` (no `search_lcsc_direct` in `sync_one_part`); docs `provider_digikey.py:46-48`, `bom/SKILL.md:73`, `kicad/SKILL.md:450`, `lcsc/SKILL.md:180`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R4-F2, sk/R4-F3, sk/R4-F7)

**Symptom:** (1) a download that fails without raising returns False → `status: failed`, and the next run skips it ("Skipped (previous failures, use --force)"); with `--force-all` a prior `ok` entry is overwritten by the failure (PDF stays, entry lost). The round-9b fix (`5e35592`/`c7eea3c`) covered search only. (2) All providers share one manifest and failures carry no provider, so the documented "if some fail, try others — they share the same directory" never re-tries those parts without `--force`. (3) LCSC: `search_lcsc` None → `enrich_with_wmsc(None)` None → retry needs an MPN → `not_found` → permanent skip, although `lcsc/SKILL.md:180` and single-fetch (`fetch_datasheet_lcsc.py:65`) use the direct lookup.

**Fix direction / budget:** transport failures retryable and a prior `ok` kept; per-provider attribution of negative results; add the direct lookup to LCSC sync. Riders: KH-492's 429 bound and dead refresh branch (`sync.py:270-272`). Lands after the output-neutral serial/parallel outcome-helper refactor (`sync.py:234-258` = `:274-297`). Waits on ruling: how legacy unattributed failure entries migrate. Budget: **distributor-oracle re-freeze** — the `PREVFAIL3` seed is an unattributed failure, so the sync runs move under (2); (1) is oracle-neutral if only exception-classified failures become retryable (verify); (3) oracle-neutral today (add a fixture case).

### KH-614: re-planning a datasheet extraction after a PDF revision reuses the old task results and stamps them with the new PDF's SHA

**Severity:** HIGH (opt-in extraction pipeline; defeats the only staleness guard)
**File:** `skills/datasheets/scripts/plan_extraction.py:161-165` (short-circuits only on SHA match; writes a new plan but never removes `<mpn>.<task>.result.json`); `merge_results.py:65`, `:83-88` (`_read_result` / `_classify` check status + schema only), `:130-131` (`_initial_extraction` stamps `source.sha256 = plan["pdf_sha256"]` and a fresh `extracted_at`); `references/dispatcher-contract.md:50`, `:57`, `:65`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F2)

**Symptom:** the contract says complete results MUST be skipped / never overwritten without `--force` and only failed ones deleted. After a PDF revision the new plan carries the new SHA, the old complete results are merged, and the extraction records the new SHA with a fresh timestamp; `cache_reader` then reports `is_stale=False`. Old facts are labelled as the new PDF's.

**Fix direction / budget:** bind each result wrapper to the plan/PDF SHA and reject unbound or mismatched results; the planner invalidates old results on a SHA change; update dispatcher-contract.md. Budget: extraction pipeline provenance only (no analyzer gate profile).

### KH-613: EMC PDN impedance drops phase (scalar `|Z|` summed in parallel), so no anti-resonance can exceed the best single cap; PD-003 never runs because of two consumer key mismatches; trace inductance is ×1.82; PD-004 picks the wrong worst source

**Severity:** HIGH (default EMC path; PD-001 false negatives on every multi-cap rail)
**File:** `skills/emc/scripts/emc_formulas.py:578-591` (`cap_impedance_at_freq` returns scalar `sqrt(ESR²+X²)`), `:644-646` (`parallel_cap_impedance` sums `1/|Z_i|`), `:1229` / `:1245` (distributed path, same); `:1107` (`'net_name' in nl`; producer `pcb/routing.py:785` emits `net`), `:978` (`entry['rail_net']`; DC-DET producer `signal_detectors.py:1227` emits `rail`); `:461-468` (`trace_inductance_nh_per_mm`); `emc_rules.py:3473-3490` (default analytic sweep), `:3697` (PD-003 skip), `:3586` (PD-002 `elif peaks` unreachable), `:3795-3800` (PD-004 worst source)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F1, sk/R1-F2, sk/R1-F8; spot checks R1 #1 and register PD-002)

**Symptom:** (1) 1 µF + 10 nF, 1 nH, 10 mΩ: true complex peak 2.433 Ω @ 35.73 MHz; the code's 1–100 MHz max is 0.251 Ω and `find_anti_resonances(sweep, 0.33)` → `[]` — PD-001 false negative. (2) `enrich_power_tree_with_pcb` keys on `net_name`, the producer emits `net` → trace R=L=0 and `check_pdn_distributed` skips (`:3697`), so PD-003 can never fire (with `net_name`: R 0.082 Ω, L 33 nH); `build_power_tree` reads `rail_net`, the producer emits `rail` → no cap is ever `ic_decoupling`. (3) L = Z0/v uses Z0_air with c/√3.3 → 0.5416 nH/mm instead of 0.2981 (×1.82); dead today behind (2). (4) PD-004 compares `i_trans > total_reflected - i_trans` (running sum, not max): sources 0.3/0.4/0.5 A pick #2 and report its frequency with the total current. PD-002's `elif peaks` branch is unreachable.

**Fix direction / budget:** complex impedance in both sweeps; consumer reads `net` / `rail` (no producer key renamed); Z0_air/c; track max current in PD-004; remove or fix the dead PD-002 branch. Budget: PD-001/PD-002/PD-004 presence, peak values and risk score move; **PD-003 appears for the first time** — budget it separately and validate on a single-source rail first (size first, `--full` boards). Related: KH-478 (distributed SPICE helper with no caller) waits on ruling: keep or retire it. Harness `test_kh377_pd001.py` mocks the peak list, not the math.

### KH-612: SPICE crystal bench wires the motional branch in parallel and drives no current, so every passive crystal with two load caps warns "Series resonance 0.000 MHz deviates 100 %"

**Severity:** HIGH (spice default path, every passive crystal with two load caps)
**File:** `skills/spice/scripts/spice_templates.py:667-669` (Lm, Cm, Rm all on `xtal1_int xtal2`), `:679` (`IAC 0 xtal1_drv DC 0 AC 0`, the only other element on VAC's node), `:689` (`cl_pF` echoed from `extra`); `spice_results.py:355-356`, `:368-377`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F3) — split from fix group 9

**Symptom:** the "BVD" motional branch is a parallel RLC and i(VAC)=0. 8 MHz, 2×22 pF on ngspice-42: rc 0 with `Error: argument out of range for divide`, `Can't evaluate "v(xtal1) / i(vac)"`, `no such vector as abs(z_real)`; `f_series` echoes as `0` → warn "Series resonance 0.000 MHz deviates 100.0% from nominal". On the LTspice path (`{}` results) the same bench passes "Load caps present". `cl_pF` is reported as if measured.

**Fix direction / budget:** series motional branch, a driven two-terminal stimulus, require a measured `f_series` before scoring, label CL as calculated. Budget: removes a spurious SP-WARN on every passive crystal sim under spice-offline (size first).

### KH-611: SPICE LC-filter bench fixes Q=100 by construction and then warns that Q is high — a spurious SP-WARN on every LC filter

**Severity:** HIGH (spice default path, every LC filter whose −3 dB points are found)
**File:** `skills/spice/scripts/spice_templates.py:270` (`r_series = 2π f L / 100  # Q=100`); `spice_results.py:165` (Q>10/Q>20 warns), `:1133-1162` (SP-WARN finding)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F5) — split from fix group 9

**Symptom:** textbook 10 µH / 1 µF: f error 0.00 %, measured Q 115.7 → `status: warn` "High Q factor (115.7) — underdamped, risk of oscillation or ringing in power path". The Q comes only from the generator's own assumed series R.

**Fix direction / budget:** mark Q as assumed and suppress the Q>10/Q>20 warns unless loss is modelled (DCR/ESR from the part). Budget: SP-WARN → pass on LC-filter sims under spice-offline (size first: LC sims warning on Q).

### KH-610: SPICE op-amp `phase_at_bw` measure has no `at=`, so the phase-at-bandwidth metric is never populated

**Severity:** LOW (spice default path; a missing value, no false verdict)
**File:** `skills/spice/scripts/spice_templates.py:599` (and `:565`, transimpedance) (`("phase_at_bw", "find", f"vp({out_net})", "bw_3db")`); consumer `spice_results.py:321`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-N2) — split from fix group 8 (the rest of that group is the KH-442 addendum below)

**Symptom:** the tuple renders `meas ac phase_at_bw find vp(out) bw_3db`; ngspice-42 logs `find(FIND) : bad syntax of WHEN` on every op-amp run and `phase_at_bw` is always None.

**Fix direction / budget:** emit `at=bw_3db` (and convert radians, see KH-619). Budget: adds a value to op-amp results under the spice-offline profile; land with the KH-442 fix.

### KH-609: EMC reads `pads` from PCB footprints that the PCB analyzer always strips, so the IO-001 schematic fallback never clears, test-plan protocols are always `unknown`, and BE-003 is unfirable

**Severity:** HIGH (default EMC path, every board)
**File:** `skills/emc/scripts/emc_rules.py:2592`, `:844`, `:4143` (iterate `conn.get('pads', [])`); producer `skills/kicad/scripts/pcb/presentation.py:156` (strips `pads` unconditionally, leaves `pad_nets` `{num: {net, pin}}`); BE-003 `:2592-2614`; leaked loop variable `:4160`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F3)

**Symptom:** the three consumers see no pads. (1) The IO-001 schematic-protection fallback (`:842-854`) can never clear, so a connector whose TVS sits >25 mm away gets a false IO-001. (2) `test_plan.interface_risks[].protocol` is always `unknown`. (3) BE-003 frequency stays 100 MHz. Independently BE-003 cannot fire: max `avg_spacing` = sqrt(π·100) = 17.72 mm (1 via) vs `2·λ/20` = 142.9 mm at 100 MHz (εr 4.4); zero vias → `continue` (`:2614`). Even after a pads fix a 1 GHz knee gives a 14.3 mm limit that fires only with exactly 1 via.

**Fix direction / budget:** read `pad_nets[*].net` in the three consumers. Budget: IO-001 count and `interface_risks` protocol/risk_score move (size first: EMC units with IO-001 and a schematic-side protection part). The BE-003 half waits on ruling: the BE-003 density model and the zero-ground-via policy (also RP-001 `:3903`, ES-002 `:3010`) — without it BE-003 stays silent.

### KH-608: EMC DP-001 applies the USB High-Speed 25 ps skew limit to every USB-named pair, so routine Full-Speed boards get an error

**Severity:** HIGH (default EMC path, every board with a USB pair)
**File:** `skills/emc/scripts/emc_rules.py:2073` (DP-001 looks up `DIFF_PAIR_PROTOCOLS[protocol]` with no speed resolution); `emc_formulas.py:757` (`'USB'` = HS params, 25 ps); producer `schematic/net_analysis.py:1150-1151` → `:1232` (`_guess_diff_protocol` returns bare `"USB"`); DP-002 resolves speed at `emc_rules.py:2128-2147`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F6) — split from fix group 6

**Symptom:** `diff_pair_skew_ps(10 mm, 4.4)` = 54.8 ps → DP-001 error; the warning threshold 12.5 ps is ≈2.3 mm of mismatch and the error 25 ps ≈4.6 mm — routine on FS-only MCU boards (12 Mbit/s, 4–20 ns edges, where skew is irrelevant). DP-002 treats the same unresolved pair as FS, so the two rules disagree on one pair.

**Fix direction / budget:** one USB endpoint-speed resolver shared by DP-001 and DP-002 (unresolved → FS, as DP-002 does). Budget: DP-001 severity/text on USB pairs moves error→warning/info (size first: DP-001 findings whose protocol is bare `USB`). Cross-bundle: `_guess_diff_protocol` has no FS/HS split.

### KH-607: EMC ML-001 lists victims in set-iteration order, so finding order varies with PYTHONHASHSEED

**Severity:** MEDIUM (default EMC path; order-only, invisible to the seed-0 gate)
**File:** `skills/emc/scripts/emc_rules.py:4393` (`sensitive_refs = set()`), `:4426` (iterated unsorted into `sensitive`); no later sort (`run_all_checks` `:4589`, `analyze_emc.py:84` sorts only local per-rule lists)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F7) — split from fix group 6 (different mechanism and budget from KH-608)

**Symptom:** a synthetic board with L1 + Y1/Y2 + U5/U6 within 15 mm gives five different victim orders at PYTHONHASHSEED 0..4 (`['U5','Y2','U6','Y1']`, `['Y1','Y2','U5','U6']`, …). `finding_id` is content-derived and stable; the list order is not, which breaks the Layer-1 byte-stability rule. The gate pins seed 0 and cannot see it.

**Fix direction / budget:** `sorted(sensitive_refs)`. Budget: ORDER ONLY vs the seed-0 baseline on multi-victim boards (size first: EMC units with ML-001 and ≥2 victims). Consider adding EMC to the unpinned determinism guard.

### KH-606: `datasheet_verify` cannot find any extraction written by `datasheet_extract_cache` (hashed file names and manifest keys), and reads quality from a `meta` key no producer writes

**Severity:** HIGH (the verifier runs on every schematic analysis; all three verifier families skip silently)
**File:** `skills/datasheets/scripts/datasheet_verify.py:40` (name sanitiser keeps `.-`, no hash), `:43` (direct `<mpn>.json` read), `:62` (manifest key compared to the unhashed name), `:195`, `:210` (`"meta"`); writer `datasheet_extract_cache.py:152-154` (`_sanitize_mpn` = `[^A-Za-z0-9_]`→`_` + `_<md5[:6]>`), `:293-294`, `:315`, `:304`, `:322` (`extraction_metadata`); caller `schematic/pipeline.py:1474-1484`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F1, sk/R3-F10)

**Symptom:** `cache_extraction(d, 'LM2596-ADJ', …)` writes `LM2596_ADJ_d61933.json` and a manifest key with the hash; `_load_extraction` looks for `LM2596-ADJ.json` / an unhashed key → `{}`, while the cache's own `get_cached_extraction` finds it. Every legacy-cache verifier family skips and `ics_with_extractions` undercounts, though `kicad/SKILL.md:479` tells the agent to cache via `datasheet_extract_cache` (and names `datasheets/extracted/<MPN>.json`, which the writer never emits). Separately, `:195` / `:210` read `meta`, which no producer in `skills/` writes (the writer and `datasheet_features.py:92` use `extraction_metadata`), so a low legacy score never yields `extraction_quality_low`.

**Fix direction / budget:** resolve through the manifest's `mpn` value or the cache manager's reader, keeping the direct-file path as a fallback; read `extraction_metadata`; fix the SKILL.md:479 filename. Budget: the schematic envelope's `datasheet_verification` gains findings on legacy caches — expected ≈0 corpus-wide (round-8 pre-scan: 0 units carry `datasheet_verification`); harness to confirm.

### KH-605: distributor sync stores a fuzzy or first-result search hit under the requested MPN as `ok` / `verified`, and the substitute's datasheet URL is written back to the schematic

**Severity:** HIGH (default distributor sync; wrong datasheets reach the user's Datasheet fields and extraction)
**File:** `skills/lcsc/scripts/provider_lcsc.py:120` (`components[0]` fallback for queries ≥6 chars, `:116-117`), `:327` (`effective_pn = lcsc_mpn or display_pn`), `:336` (`verify_datasheet(..., effective_pn, ...)`); `skills/digikey/scripts/provider_digikey.py:228-231` (`startswith`, then `products[0]`), `:339`; `skills/element14/scripts/provider_element14.py:141`, `:243`, `:252`; `skills/datasheets/distributor_core/verify.py:70` (substring match), `:111` (`confidence="verified"`); `distributor_core/sync.py:147`, `:275` (stored under the requested key); consumer `skills/bom/scripts/sync_datasheet_urls.py:111-126`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R4-F1)

**Symptom:** a requested MPN with no exact hit resolves to the provider's first result; the PDF is then verified against the *returned* MPN (which it trivially matches), recorded `confidence="verified"`, and stored under the *requested* MPN. `bom/sync_datasheet_urls.py` then writes that `datasheet_url` into the schematic for every reference of the `ok` entry, and per-MPN extraction runs on the substitute's PDF. Should: verify against the requested identity and refuse to store a non-equivalent hit as `ok`.

**Fix direction / budget:** keep requested and returned identity separate; accept a result only on an exact or explicitly supported ordering-code equivalence (`verify.py:76-80` has an ad-hoc suffix list that could seed it); keyword search stays for discovery. Waits on ruling: which ordering suffixes / families count as the same part. Budget: `status` / `file` / `verification` move on fuzzy hits; **distributor-oracle re-freeze likely** — size against the frozen LM358DR / TPS61023DRLR search fixtures in `tools/tests/fixtures/distributor/` before the change, then RUNBOOK 26j both ways.

### KH-604: `translate_bom_pnp` ignores a DNP/population column and does not expand `R1-R4` ranges, so JLCPCB assembles DNP parts and drops ranged parts as orphans

**Severity:** HIGH (documented "KiCad/Altium BOM" input to the JLCPCB translator)
**File:** `skills/bom/scripts/translate_bom_pnp.py:393` (`_is_dnp(val)` on the value cell only; `DNP_MARKERS` `:42`, `:101-104`; columns found `:335-340`), `:459-461` (`_expand_designators`), `:486` (`_read_bom_designators`), `:541` / `:562-566` (`pnp --bom` orphan filter), `:297` (exit 0)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-F5, sk/R5-F6; tests sk/R5-F10)

**Symptom:** (1) A KiCad 7+ BOM export carries DNP in a `DNP` column / `${DNP}` field and keeps `Value=10k`; no DNP column is looked up, so the row is kept and `pnp --bom` keeps its placement — JLCPCB assembles the DNP part. (2) `_expand_designators('R1-R4')` → `['R1-R4']` (it splits only on `,`, `;`, whitespace). KiCad's grouped shorthand `R1-R4, R7` (Symbol Fields Table / BOM export) then makes R1..R4 absent from `bom_designators`, so their placements are dropped as orphans at `:562` and the CLI exits 0 (`filtered_orphan_samples` lists them, a partial mitigation). Existing tests (`:670-678`) assert substrings only (`"2.5400mm" in out_text`).

**Fix direction / budget:** honour a DNP/population column alongside the value markers; expand `<prefix><n>-<prefix><m>` ranges. Replace the substring asserts with per-row identity tests. Budget: translated BOM/CPL rows and `skipped_dnp` change (not a gated analyzer; no harness test covers `translate_bom_pnp`).

### KH-603: BOM manager reads `POPULATE=1` as DNP, and a group's DNP state comes from its first member, so the order file depends on symbol file order

**Severity:** HIGH (default `bom_manager` export/order path; POPULATE projects lose every fitted part)
**File:** `skills/bom/scripts/bom_manager.py:188-192` (`is_dnp`), `:124` (`DNP_FIELDS`); `:423-427` (group keys), `:444` / `:450-451` (group `dnp` from the first member), `:1008` (order path skips `DNP=yes` rows)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R5-F4, sk/R5-F1)

**Symptom:** (1) `DNP_FIELDS` includes `POPULATE` and the loop tests every field for `("YES","TRUE","1","DNP")` before the POPULATE-specific `"0"` check, so `is_dnp('(dnp no)', {'POPULATE':'1'})` → True (and `'0'` → True; `{}` → False). `references/part-number-conventions.md:334` says `1` = populate. Every fitted part on a POPULATE project is dropped from gaps and orders (corpus: `(property "POPULATE" "1"` in 70 sheets of 1 repo). (2) The default key `(value, footprint, mpn)` (and the `mpn`/`value` modes) omits population state, and the group takes `"dnp": sym["dnp"]` from its first member. R1 `(dnp yes)` + R2 `(dnp no)` with the same value/footprint/MPN export as one row `R1,R2 qty 2 DNP=yes` (nothing ordered) when R1 comes first, or `R2,R1 qty 2 DNP=""` (the DNP part ordered) when R2 comes first. A fitted part next to an identical DNP alternate is common.

**Fix direction / budget:** test `POPULATE` only against its own vocabulary (`0` = DNP, `1` = fitted); add DNP state to every group key. Budget: `bom_manager` CSV/JSON `bom[]` rows, quantities and order files move on POPULATE projects and on designs mixing DNP/fitted identical parts (not a gated analyzer; size the mixed-DNP class first). Harness: `test_kh414_bom_manager_roundtrip.py` exercises export — re-check its expectations.

### KH-602: `lifecycle_audit` temperature-range parsing reads a negative maximum as positive and starts a decimal minimum mid-number

**Severity:** LOW (rare distributor attribute shapes)
**File:** `skills/kicad/scripts/lifecycle_audit.py:138` (temperature-range regex)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-F7)

**Symptom:** `-40°C~-10°C` → (-40, 10); `-40.5°C ~ +85.5°C` → (5, 85). Normal strings (`-40°C ~ 85°C`, `-55°C ~ 150°C (TJ)`) parse correctly. A U+2212 minus would read -40 as 40.

**Fix direction / budget:** one signed-decimal token pattern (accepting U+2212) for each bound. Budget: lifecycle LT-001 values on the affected strings only.

### KH-601: LC-005 counts a source that responds with `status: None` as responding but not active, so a part stocked at Mouser (null `LifecycleStatus`) is flagged single-source

**Severity:** LOW (PLAUSIBLE in the audit; needs a frozen Mouser response to settle)
**File:** `skills/kicad/scripts/lifecycle_audit.py:789-797` (LC-005 `responded` / active counting)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-X2)

**Symptom:** Mouser documents `LifecycleStatus` as string|null (mouser SKILL.md:151) and returns null for ordinary active parts. DigiKey Active plus Mouser null fires LC-005 "single source (digikey)". The KH-372 live run in FIXED.md shows LC-ACT 11 / LC-005 11, i.e. every active part flagged single-source. The harness test `test_lc005_none_status_not_counted_active` pins today's firing. This is the opposite direction to the refuted kc/R14-F8, where outages deliberately suppress LC-005 and that suppression stays.

**Fix direction / budget:** count a null-status response with stock or a part match as available (or exclude it from `responded`). Budget: lifecycle output only, LC-005 disappearances. The harness test changes. Waits on ruling: R14-X2 (does a null-status response count toward `responded`).

### KH-600: `lifecycle_audit` provider lookups accept a result whose MPN only shares a 6-character prefix (DigiKey, LCSC) or take the first result with no MPN comparison (Mouser, element14)

**Severity:** HIGH (online lifecycle path; reports a sibling part's status as the BOM part's)
**File:** `skills/kicad/scripts/lifecycle_audit.py:241` (DigiKey keyword search, Limit 3, `startswith(mpn[:6])`); `:333` (LCSC, same); `:294` (Mouser `partSearchOptions: ""`, not Exact); `:382` (element14 first result)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-F2)

**Symptom:** for an obsolete part that DigiKey no longer lists exactly, a sibling with the same 6-character prefix is returned and its "Active" status is reported for the BOM part. Ranking and vocabulary cannot be checked offline, and no lifecycle fixtures exist (`tools/tests/fixtures/distributor` is for the sync oracle only).

**Fix direction / budget:** require an exact (normalised) MPN match per provider (Mouser Exact search option), and report "not found" otherwise. Budget: lifecycle output only, with no corpus gate. Needs a provider-identity contract and frozen per-provider lifecycle responses first.

### KH-599: `inputs.config_hash` hashes only `<search_dir>/.kicad-happy.json`, not the ancestor and home layers that were merged

**Severity:** MEDIUM (provenance contract; corpus has no configs)
**File:** `skills/kicad/scripts/project_config.py:193-195` (`hash_input`), `inputs_builder.py:62`; envelope description `analyzer_envelope.py:267-269`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F8)

**Symptom:** a change to the user's home or a parent-directory config changes the resolved configuration but leaves `config_hash` unchanged. With only an ancestor config, the envelope still promises "the hash of the resolved .kicad-happy.json … or null when no project config was loaded". The `resolve_config` docstring keeps this behaviour on purpose.

**Fix direction / budget:** hash the resolved merged content (canonical JSON) or every layer in `paths`, or narrow the envelope description. Budget: corpus-neutral (0 corpus configs); a `--schema` text change if the description changes. Waits on ruling: R13-F8 (layer set vs resolved-content hash).

### KH-598: `finding_id` ordinals (`#N`) come from occurrence order within a derived-id group, so ids shift when an unrelated member of the group appears or disappears

**Severity:** MEDIUM (stable for identical input; breaks annotation reuse across revisions; 30 % of sampled findings carry `#N`)
**File:** `skills/kicad/scripts/finding_schema.py:81-90,128-130` (`assign_finding_ids` ordinal suffix); e.g. PP-001 emits `components: [ref]` with no `detection_id` (`signal_detectors.py:4711-4734`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F3)

**Symptom:** about 2,900 sampled harness corpus schematic outputs hold 12,933 of 43,317 findings (30 %) with a `#N` id, across 903 units (NT-001 9,374, DO-DET 888, DC-DET 799, PP-001 167, …). Adding one NT-001 earlier in the group renumbers every later one.

**Fix direction / budget:** anchor collision groups on a content key (net, pin, detection identity) before falling back to the ordinal. This is the same mechanism as REPORT-3 A3-F8. Budget: a corpus-wide `finding_id` migration class on the 903+ units (output-changing everywhere ids are compared; Deep Review / annotation consumers). Waits on ruling: the collision-group anchor scheme and the `finding_id` migration budget.

### KH-597: `analysis_cache` run creation is an unlocked manifest read-modify-write with minute-resolution run ids, so parallel analyzers into one `--analysis-dir` can lose updates

**Severity:** MEDIUM (SKILL.md:409/415 tells the agent to run the analyzers in parallel into one analysis dir; the window is milliseconds)
**File:** `skills/kicad/scripts/analysis_cache.py:330-407` (`create_run`: `load_manifest` … `save_manifest`; `makedirs(exist_ok=True)` at `:335` accepts a folder another process took); `output_io.py:47-52,69`; `generate_run_id` (minute resolution)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F2)

**Symptom:** two analyzers that start within the same minute pick the same run folder, and the second `save_manifest` overwrites the first's `outputs` / `scripts` entry. Established by reading only; it needs a barrier-controlled two-process test.

**Fix direction / budget:** create run folders exclusively (`mkdir` without `exist_ok`, then retry with a `-N` suffix), and merge manifest entries under a lock file or through a per-writer merge on replace. Budget: neutral for the harness. This is the same unlocked read-modify-write class as KH-489 (SPICE model cache) but a different file, so one helper could serve both.

### KH-596: a re-run with `--analysis-dir` mixes a fresh schematic.json with stale pcb/thermal outputs in the new run, and `source_hashes` drops the PCB hash

**Severity:** MEDIUM (documented `--analysis-dir` workflow; a cache-coherence gap, not wrong analysis)
**File:** `skills/kicad/scripts/analysis_cache.py:365` (copy-forward), `:48-53` (`_OUTPUT_SOURCE_EXT` excludes derived outputs), `:395` (a stale-skipped entry stays in `outputs`), `:401` (hashes)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F1)

**Symptom:** on a copy of harness simple-project, run sch → pcb → thermal with `--analysis-dir`, change R 330 → 10k, and re-run the schematic. The new run `…_0048-2` holds the new schematic.json plus the old pcb.json and the old thermal.json, which was built from the old schematic. Its `source_hashes` keeps only the `.kicad_sch` hash and `scripts` lists only the schematic. Derived files (thermal/emc/cross/spice) are never marked stale. Compounds with KH-572 (the `should_create_new_run` overwrite path).

**Fix direction / budget:** either do not copy derived outputs forward (or mark them stale when an upstream changes), or record the full source-hash set. Budget: neutral for the harness (no gate profile uses `--analysis-dir`). Waits on ruling: R13-F1 (is the current run a coherent snapshot or a mixed cache).

### KH-595: `export_issues` dedups by rule label only, so the first export opens N issues per rule and later runs skip every new instance of an already-open rule

**Severity:** MEDIUM (visible `SKIP` lines, not silent; GitHub issue creation)
**File:** `skills/kicad/scripts/export_issues.py:505-524` (skip logic), `:280` (dedup key = rule label), `:294-298` (a failed lookup returns `[]`, so duplicates can appear the other way)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R12-F7)

**Symptom:** the first run creates one issue per finding with no dedup within the run. A later run prints `SKIP [rule] summary (already open: #n)` for every new finding of a rule that has any open issue. When the open-issue lookup fails, every finding is re-filed.

**Fix direction / budget:** key issues by `finding_id` (or a stable per-finding marker in the body), dedup within the run, and treat a failed lookup as an error. Budget: exporter CLI only, corpus-neutral. Waits on ruling: per-finding vs per-rule issue identity and the migration of label-only issues. KH-471 is the same file (severity labels).

### KH-594: cross_verify and DA-001 ignore `on_board`, so a normal DNP part with a footprint warns, and an excluded-from-board part is expected on the PCB

**Severity:** MEDIUM (cross_verify / cross_analysis on any design with DNP parts)
**File:** `skills/kicad/scripts/cross_verify.py:121-123,155-157,181-186,130-134` (PCB `dnp`, `pcb/reader.py:461`, discarded); `skills/kicad/scripts/cross_analysis.py:425-430`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F10)

**Symptom:** in KiCad, DNP keeps the footprint and "exclude from board" (`on_board` no) omits it. The schematic emits `on_board` on 15,712 of 15,712 sampled components, 50 of them false. Neither builder reads it. cross_verify warns whenever a DNP ref has a footprint, which is the normal KiCad case.

**Fix direction / budget:** key PCB-presence expectations on `on_board`, and use the PCB `dnp` flag for the DNP comparison. Budget: cross_verify warnings disappear on DNP designs, and cross_analysis findings may move on `on_board: false` parts (size first). Waits on ruling: whether cross_verify is maintained or retired.

### KH-593: thermal fallback θJA table comment says "no enhanced copper pour" while the SOT-223 / TO-252 values are JEDEC high-K / ~1 in² copper figures

**Severity:** MEDIUM (non-conservative baseline for power packages; a calibration choice)
**File:** `skills/kicad/scripts/analyze_thermal.py:63,72,75` (`_PACKAGE_THETA_JA` and comment)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F5)

**Symptom:** SOT-223 = 60 °C/W and TO-252 = 40 °C/W match a 2s2p / ~1 in² copper board, not minimum-pad copper. The LM1117 copper-area table the reviewer cites gives 136 → 66 °C/W for SOT-223 and 103 → 47 for TO-252; it could not be fetched offline. QFN with and without EP are not distinguished (`QFN-32-1EP_5x5` → 25).

**Fix direction / budget:** state the baseline board condition, and either correct the comment or pick conservative values. Budget: comment-only if the values stay; thermal Tj on every power-package assessment if they change (size first). Related to KH-430 (SOT-563 missing, extraction RθJA ignored). Waits on ruling: R11-F5 baseline board condition.

### KH-592: Gerber/Excellon parser state — modal coordinates, trailing-zero formats, G-prefixed lines, full-circle G75 arcs, route-mode and G85 slots, LZ and leading-dot tools are all misread

**Severity:** MEDIUM (small corpus reach outside the arc and slot cases; KiCad writes full XY under FSLAX46Y46)
**File:** `skills/kicad/scripts/analyze_gerbers.py:223` (anchored `re.match` skips G-prefixed lines; modal axes and FS trailing omission decoded wrongly); `:223-231` (G75 start == end is a full circle, read as zero extent); `:420` (Excellon route mode `G00/M15/G01/M16/G05` skipped; `G85` drops the end point); `:395,428-436` (LZ decoding, leading-dot `T1C.04`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-F4, kc/R10-F5, kc/R10-F6, kc/R10-F10)

**Symptom:**
- **Modal and FS decoding:** a modal rectangle gives zero extents. `%FSTAX23Y23` X10Y20 gives (0.01, 0.02); it should be (10, 20). About 3,300 corpus edge lines of the form `G02X…Y…I…J…D01*` never enter the extents.
- **Full-circle arc:** G75 from (5,10) with I = 5 gives extents 5..5 / 10..10, so `board_dimensions` is `{}` when there is no gbrjob.
- **Excellon route mode and G85:** a route-mode drill file gives `hole_count 0`. `X1.0Y2.0G85X11.0Y2.0` keeps only (1,2).
- **LZ and leading-dot tools:** `T1C.04` gives tools `{}`. LZ `X1.5Y2.5` reads as (0.0015, 0.0025).

Corpus prevalence over 4,415 Edge.Cuts files and 8,636 drl files: modal-axis edges 9, TZ 0, G70-only 7, SR 1, arc-bearing edges 2,362, drl M15 1,005, G85 424, LZ 13, leading-dot tools 5.

**Fix direction / budget:** a real modal parser state (current X/Y, FS zero mode, G-code prefix, G74/G75), full-circle arcs, Excellon route mode, G85 slots, and LZ / leading-dot tool forms. Budget: corpus output on gerber units (extents, `board_dimensions`, hole counts, tool classification, the GR-003 zero-hole info). Build against a gerbv/kicad-cli oracle. Waits on ruling: whether this group goes into 3.0.x or waits for an oracle round, and slot accounting in `hole_count`. KH-565 shares the arc handling.

### KH-591: Gerber `%TO.P` attributes take the previous pad's `%TO.N` net because KiCad emits P before N

**Severity:** HIGH (systematic off-by-one on KiCad 6/7/8 output; reaches output only through `--full` gerber `connectivity`, which no product consumer reads)
**File:** `skills/kicad/scripts/analyze_gerbers.py:184-191` (pin mapping attaches the current net at `%TO.P` time); output at `:1386-1399`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-F7)

**Symptom:** KiCad 6.0.9 (PiEDB-Y15), 7 (Thinkpad-USB-keyboard) and 8 (ecg) all write `%TO.P` before `%TO.N` per pad. On a copy of PiEDB F_Cu, R11.1 gets net "" and R11.2 gets "Net-(D3-Pad5)", which is R11.1's real net. Named `TD` deletes appear in only 11 corpus files.

**Fix direction / budget:** attach the attribute dictionary in effect at the D03 flash operation, and honour named `%TD`. Budget: `--full` gerber `connectivity` only. The corpus has no `--full` gerber outputs, so it is corpus-neutral today. The record notes it could join KH-564.

### KH-590: PCB reader gaps on KiCad 9/10 formats — numeric-only net names collide with net IDs (the track is dropped), and custom padstacks read only the top-level size

**Severity:** MEDIUM (latent: 0 of 83 corpus KiCad-10 boards have a numeric net name; 21 corpus boards use custom padstacks)
**File:** `skills/kicad/scripts/pcb/reader.py:530` (also `:331,336` pad, `:553` arc, `:619` via, `:779` zone), backfill `pcb/pipeline.py:145-158`, `kicad_core/model.py:150` (`PcbReaderState.net_id`); `pcb/reader.py:283,312-313` (`find_first(pad, "size")`; nothing in the PCB scripts reads `padstack`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F3, kc/R8-F4)

**Symptom:** a minimal KiCad-10 board with nets "12" and "GND" gives segment `net: 12` without `_net_name`, pads `('12', 12)`, net map `{1: '12', 2: 'GND'}`, zone `(0, '')`, and graph `'12': islands 2`, so the track is lost. A `(padstack (mode custom|front_inner_back))` pad uses its front size on every layer.

**Fix direction / budget:** add a name-only lookup to `PcbReaderState` for KiCad 10 string nets (one fix across the reader, the model and the backfill). Read per-layer padstack sizes. Budget: latent in the corpus for the net-name half; the padstack half moves geometry on about 21 boards. Size first.

### KH-589: DFM netclass track-width and via-diameter checks are dead: they read `net_name`, which no segment, arc or via carries

**Severity:** MEDIUM (dead checks; resolving the IDs naively would create false violations)
**File:** `skills/kicad/scripts/pcb/dfm.py:878,901` (also `:177,188`); producer `pcb/reader.py:528,616` (numeric `net`, plus `_net_name` on KiCad 10 only, `:530,620`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F7, kc/R9-F11)

**Symptom:** the per-netclass loops never match a net, so no netclass width or diameter violation is ever emitted. The unit test `tools/tests/test_pcb_dfm.py:58` feeds a synthetic `net_name`, which hides this. KiCad netclass track width and via diameter are router defaults, not DRC minima; only netclass clearance is enforced.

**Fix direction / budget:** delete the width/diameter class checks, or re-scope them as info. Give the test an independent oracle. Budget: neutral if deleted; a new info class if re-scoped. Waits on ruling: R9-F7 (delete vs info).

### KH-588: DFM `approx_min_spacing_mm` measures endpoint to endpoint over the first 2,000 segments, so crossing or parallel traces read far apart

**Severity:** MEDIUM (labelled approximate; the harm is a falsely good `dfm_tier`)
**File:** `skills/kicad/scripts/pcb/dfm.py:265-296` (endpoint distances, the first 2,000 segments, the next 49 neighbours in file order, negatives dropped at `:294`); tier at `:659-669`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F4)

**Symptom:** an orthogonal crossing of two 0.2 mm traces gives `min_spacing 6.8711`. The violation note says "approximate (endpoint-to-endpoint…)", but `dfm_tier` takes the number as measured.

**Fix direction / budget:** use segment-to-segment distance over a spatial grid (the KH-420 `ZoneFills` grid pattern), different nets only. Budget: a corpus-wide DFM output change (`approx_min_spacing_mm`, `dfm_tier`, spacing violations). Needs its own budgeted round, and native DRC remains the authority. Mind the KH-449 performance cliff.

### KH-587: `pad_to_pad_distances` joins track endpoints by (x, y) only, so two layers with coincident endpoints and no via count as connected

**Severity:** MEDIUM (opt-in `--full`, informational output, DRC-dangling layouts only)
**File:** `skills/kicad/scripts/pcb/routing.py:141-183` (`_snap` keys ignore layer; vias only `setdefault` a node at `:183`, and the `:175` comment claims cross-layer edges)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F3)

**Symptom:** F.Cu (0,0)-(5,0) plus B.Cu (5,0)-(10,0) with no via gives `routed_distance_mm 10.0`.

**Fix direction / budget:** key nodes by (layer, x, y) and add via edges across the via's layer span. Budget: `--full` `pad_to_pad_distances` values on affected boards (full-chain profile; size first).

### KH-586: `connectivity.routing_complete` is True whenever every multi-pad net has any copper, although the envelope promises "no pads remain unrouted"

**Severity:** HIGH (default path; feeds `statistics.routing_complete`, the diff engine and the fab gate)
**File:** `skills/kicad/scripts/pcb/routing.py:30-49,77` (`analyze_connectivity` membership test only); `pcb/presentation.py:96`; envelope `envelopes/pcb.py:83-84`; consumer `diff_engine.py:516`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F1)

**Symptom:** a 3-pad net with one 1 mm stub gives `routing_complete=True`. The `--full` `connectivity_graph` islands / `disconnected_pads` (`connectivity.py:443-513`) are never reconciled with it. The docstring (`routing.py:15-18`) states the weak semantics, and the envelope description states the strong one.

**Fix direction / budget:** either derive `routing_complete` / `unrouted_count` from pad-level connectivity, or narrow the envelope description to what the code does. Budget: if the semantics are strengthened, corpus output `routing_complete` / `unrouted_count` flips on partially routed boards (size first). If only the docs change, it is a `--schema` text change. Waits on ruling: R9-F1 `routing_complete` semantics. Not a KH-364 duplicate.

### KH-585: input-boundary crashes and silent drops — PCB `--schematic` with a non-dict JSON, a directory named `*.drl`, a truncated report input, and platform-encoding I/O in review/lifecycle/what_if

**Severity:** MEDIUM (malformed or non-UTF-8 input; output-neutral on valid input)
**File:**
- `skills/kicad/scripts/analyze_pcb.py:106-117` (+ `pcb/pipeline.py:85`): `open()` without encoding, and `[{}]` passes the `'signal_analysis' in` test and then raises AttributeError.
- `skills/kicad/scripts/analyze_gerbers.py:1211` → `:777`: a drill stub without `coordinate_range` raises KeyError.
- `skills/kicad/scripts/check_report_sections.py:105-111`: a corrupt `emc.json` is dropped without a warning.
- `skills/kicad/review/scripts/deep_review_gate.py:66,73,83,227,303,304,338`, `merge_annotations.py:48,63,95,125,130,131,150`, `validate_review.py:29,51`, `build_review_plan.py:58`, `skills/kicad/scripts/lifecycle_audit.py:188,209,420,432,1107,1117`, `what_if.py:1200,1206`: no `encoding="utf-8"`.

**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F10, kc/R10-F11, kc/R12-F10, kc/R14-F11)

**Symptom:**
- **`*.drl` directory:** a directory named `g.drl` beside an edge gerber makes `analyze_gerbers()` raise `KeyError 'coordinate_range'`.
- **PCB `--schematic` input:** JSON `[{}]` passed to the PCB `--schematic` option raises AttributeError, and load failures go to stderr only.
- **Corrupt report input:** `check_report_sections --run-dir` with a truncated `emc.json` reports "Analyzers present: schematic", stops requiring the EMC section, and prints no warning.
- **Platform encoding on Windows:** an LLM-authored `deep_review.json` with non-ASCII decodes as cp1252 and is written back mangled, which leads to false quarantine. pdftotext output read in the locale (`:227`) breaks µ/≤ quotes. At lifecycle `:432` a UnicodeDecodeError escapes the `(JSONDecodeError, OSError)` catch.

**Fix direction / budget:** turn each crash into a result plus one diagnostic. Warn on a corrupt sibling input. Run the standing UTF-8 sweep over review/, lifecycle, what_if and diff_analysis. Budget: output-neutral on valid input and on Linux.

### KH-584: CP-001 interpolates `list(set(nets))` into its description, so the text varies with the hash seed

**Severity:** MEDIUM (multi-net CP-001 only; gate-invisible because the gate pins seed 0)
**File:** `skills/kicad/scripts/pcb/copper.py:1022-1025,1068`; `finding_schema.py:425-428` (`sort_findings` sorts only `nets`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F9)

**Symptom:** `list(set(["AGND","DGND","GND"]))` order differs across PYTHONHASHSEED 0..5, and that order goes into `description`. There are 5 multi-net CP-001 findings in 3,023 sampled PCB outputs (e.g. Dodokamel2005/EPS- J1 `/+5V, GND`).

**Fix direction / budget:** `sorted(set(...))`. Budget: output changes only under non-zero seeds; at seed 0 the description may reorder on those 5-ish findings (size at the gate). This is the same hash-seed class as KH-421 and REPORT-4/5/7 items.

### KH-583: `--schema` marks optional setup keys as required on PCB, and gerber `missing`/`extra` as required although the defaults branch omits them, so most real outputs fail their own schema

**Severity:** MEDIUM (schema contract; 877 of 1,168 corpus PCB outputs with `setup`, and 3,475 of 5,449 gerber outputs)
**File:** `skills/kicad/scripts/envelopes/pcb.py:96-103` (setup requires `pad_to_mask_clearance`, `legacy_teardrops`, `allow_soldermask_bridges`); emitter `pcb/reader.py:76-106` (adds each key only when present; `:42-43` emits `setup: {}` without a `(setup)`); `skills/kicad/scripts/envelopes/gerber.py` (completeness `missing` / `extra` required) vs `analyze_gerbers.py:755-756`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F7, R10 Empirical row "envelopes/gerber.py requires missing/extra")

**Symptom:** 877 of 1,168 corpus PCB outputs (75 %) lack `legacy_teardrops`, 874 lack `allow_soldermask_bridges` and 95 lack `pad_to_mask_clearance`. 3,475 gerber outputs (64 %) lack both `missing` and `extra`. Contract tests pass only because the harness fixture happens to carry all of them.

**Fix direction / budget:** make these fields optional in the envelope dataclasses. Budget: a `--schema` text change only, JSON-neutral. Declare it to the harness (schema artefacts and contract tests re-freeze). Waits on ruling: whether `diagnostics` also becomes schema-required in the same change.

### KH-582: the Action "Top Risks" section and `summarize_findings` use legacy severity/confidence names, so Top Risks never renders and `datasheet-backed` findings are not counted

**Severity:** MEDIUM (Action PR comment on every run; summary tool undercounts)
**File:** `skills/kicad/scripts/project_config.py:899-901,932` (`compute_top_risks` weights keyed `HIGH`/…, `CONFIDENCE_WEIGHTS` uses `ai-inferred`), caller `action/format-report.py:178-198,487`; `skills/kicad/scripts/summarize_findings.py:153-160,187,206` (`_aggregate` confidence buckets and `--confidence` / `--evidence-source` choices)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F4, kc/R12-F6; also `docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-reg-risk)
**Symptom:** `compute_top_risks([{severity: 'error', confidence: 'deterministic', category: 'thermal_safety'}])` leaves every bucket empty; with `'HIGH'` it scores. Current findings are lowercase `error/warning/info`, so the Action's Top Risks section never renders (checked on 400 harness EMC outputs whose categories do match the bucket sets). `_aggregate` on [datasheet-backed, heuristic] gives count 2 with `datasheet_backed 0`. `--confidence datasheet-backed` and `--evidence-source api_lookup` both exit "unknown". 182 corpus EMC outputs carry `datasheet-backed`. The comment at `summarize_findings.py:153` claims the vocabulary comes from finding_schema; the code does not.

**Fix direction / budget:** normalise through `kicad_core.render.normalize_severity` and take the confidence/evidence enums from `finding_schema`. This belongs to the same sweep as the REPORT-3 A3-F9 uppercase lookup tables. Budget: Action report text and summarize_findings CLI output. Analyzer JSON is neutral. Waits on ruling: the weight for canonical `error` (8 vs 15).

### KH-581: a config section set to `null` crashes thermal, and `_deep_merge` makes `project_config` key order depend on the hash seed

**Severity:** MEDIUM (needs a user-written `.kicad-happy.json`; the corpus has none, so the gate cannot see it)
**File:** `skills/kicad/scripts/project_config.py:258-259` (`_deep_merge` replaces the default `{}` with None), crash at `analyze_thermal.py:1018-1019`; `project_config.py:87-88` (merge iterates a set), emitted at `schematic/pipeline.py:1347-1349`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F6, kc/R13-F5)

**Symptom:** thermal with `--config {"project": null}` (or the same in a discovered `.kicad-happy.json`) raises `AttributeError: 'NoneType' object has no attribute 'get'` at `:1019`. The schematic survives because of a truthiness check at `pipeline.py:1348`. `analyze_schematic.py` on a copied simple-project with a 4-key `project` config gives 4 different `project_config` key orders under seeds 0-3, with identical values.

**Fix direction / budget:** keep the default when a section is null, with a config type warning (the round-9b pattern). Merge keys in a deterministic order. Budget: corpus-neutral (0 corpus `.kicad-happy.json`). The crash becomes a result.

### KH-580: the Deep Review evidence gate certifies numerically different quotes (`55 V` vs `5.5 V`, `-40 C` vs `40 C`, `<` vs `>`, `"..."`) and crashes on non-dict evidence

**Severity:** HIGH (Deep Review gate default path; a wrong quote is stamped `evidence_checked: full`)
**File:** `skills/kicad/review/scripts/deep_review_gate.py:130,165-175` (`_quote_in_text` squash/normalise, all-punctuation `return True` at `:172-173`), called from `check_datasheet` `:232` ← `gate_finding` `:270`, stamped at `:277`; `:259-260` (`evidence.get` on a str/list → AttributeError); `:319` (`findings: 1` → TypeError); `:222-224` (a non-positive `page` leads to whole-document extraction)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-F1, kc/R14-F4, nonpositive-page register item)

**Symptom:** `_quote_in_text("Maximum input voltage 55 V", "...5.5 V")` = True through the squash path. `"-40 C"` vs `"40 C"` = True (sign dropped). `"VIN < 5 V"` vs `"VIN > 5 V"` = True. `"..."` = True, which satisfies schema minLength 1. Each is stamped `evidence_checked: full`. `gate_finding({... 'evidence': 'U3'})` raises AttributeError before the write at `:338`. That is a loud traceback rather than the promised quarantine (docstring `:9-11`). A cited `page: 0` or negative page is checked against the whole document and can still be marked full.

**Fix direction / budget:** keep digits, signs, decimal points and comparison operators significant in normalisation, and reject quotes with no alphanumerics. Quarantine (not crash) on malformed evidence or findings. Treat a non-positive page as invalid. Budget: only `deep_review.json` quarantine / `evidence_checked`, which is permanently outside the harness diff scope. Output-neutral for valid documents.

### KH-579: `lifecycle_audit` `sources_available` order varies with the hash seed, the cold-temperature shortfall has the wrong sign, and LC-006 weeks are floor-divided

**Severity:** MEDIUM (determinism rule violation; lifecycle only)
**File:** `skills/kicad/scripts/lifecycle_audit.py:929` (`sources_available` built from a set); `:898` (cold shortfall `design_min - comp_min`, versus `:899` hot); `:843` (`weeks = weeks // 7`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-F10, kc/R14-F13, LC-006 rounding row of the Empirical table; the `sources_available` half also se/R1-F8)
**Symptom:** under PYTHONHASHSEED 0..5, `audit_bom` (stubbed, 3 sources) gives 4 different `sources_available` orders. Design -40 °C vs component 0 °C gives shortfall -40, while hot 70 vs 85 gives +15. 90 days becomes 12 weeks (no LC-006, true 12.86), and 183 days becomes 26 (info, not warning).

**Fix direction / budget:** `sorted()` the source list, use `comp_min - design_min`, and compare exact weeks against the thresholds. Budget: lifecycle output only. The F10 change is order-only. The sign fix changes the shortfall values. Waits on ruling: LC-006 floor vs exact weeks.

### KH-578: `lifecycle_audit` finds the project directory through the removed top-level `file` key, so datasheet-extracted temperatures are never used

**Severity:** MEDIUM (default canonical layout `analysis/<run_id>/`; LT-001 falls back to API data silently)
**File:** `skills/kicad/scripts/lifecycle_audit.py:1061-1062` (`project_dir` from `analysis["file"]`); `read_extraction_temperature` `:405-445`; `:438` (`AttributeError` on a `null` / non-dict extraction JSON)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-X1)

**Symptom:** the schematic envelope no longer carries `file` (`analyze_schematic.py` on harness simple-project: `'file' in out` is False; the path is only in `inputs.source_files`). So `project_dir` becomes the JSON's own directory, and the extraction lookup reads `analysis/<run_id>/datasheets/extracted/`, which never exists. LT-001 never uses datasheet-backed temperatures. A `null` or non-dict extraction file raises instead of degrading. This is the same root cause as KH-477 (fixed for SPICE only, through `spice_model_cache.project_dir_from_analysis`, `spice_model_cache.py:48-61`). The analyzer-side `file` fallbacks in `analyze_thermal.py:994,1011` share it.

**Fix direction / budget:** resolve the project dir through the same `file` → `inputs.source_files[0]` helper (move it somewhere shared). Degrade a malformed extraction with one diagnostic. Budget: lifecycle output only. LT-001 `evidence_source` and temperature values change for projects with extractions. No corpus gate.

### KH-577: `lifecycle_audit` status consensus takes the last non-unknown source, so a later "active" erases an earlier "obsolete", and explicit discontinuation flags and labels normalise to `unknown`

**Severity:** HIGH (lifecycle default path whenever two distributors disagree; no corpus gate)
**File:** `skills/kicad/scripts/lifecycle_audit.py:495` (`audit_component` status merge; the comment at `:457` says worst case); `:490-492` and map `:82-98` (`_normalize_status`); `discontinued` written at `:252,297` and never read
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R14-F3, kc/R14-F6)

**Symptom:**
- **DigiKey Obsolete + Mouser Active:** status `active` with `consensus_split True`, which goes down the LC-ACT branch (no rule for `active`, `:717`). The result is info "active" and no LC-001.
- **Reversed order:** status `obsolete`, and LC-001 is demoted to warning.
- **DigiKey Obsolete + element14 NRND:** `nrnd`, a warning instead of an error.
- **Order dependence:** the last non-unknown source in dict order (lcsc, digikey, element14, mouser) wins.
- **Unread flags and labels:** DigiKey `{'status': None, 'discontinued': True}` → `unknown`. `_normalize_status("Discontinued at Digi-Key")` and `("Not Recommended for New Designs")` → `unknown`, so LC-004 is only info.

**Fix direction / budget:** rank statuses worst-first, independent of order (obsolete > LTB > NRND > active > unknown), and read the `discontinued` flag. Budget: lifecycle output only (status, LC rule, severity), with no corpus gate. Add tests for both directions of each disagreement. Waits on ruling: the label map and flag-vs-status precedence for "Discontinued at Digi-Key" and the `discontinued` flag (the flag read alone does not wait). Live vocabularies cannot be checked offline, so freeze per-provider lifecycle responses.

### KH-576: silkscreen visibility ignores the bare `hide` flag and `(hide yes)` on reference properties, so hidden refs count as visible

**Severity:** MEDIUM (default path; any KiCad 6+ board with hidden reference text)
**File:** `skills/kicad/scripts/pcb/reader.py:1094,1111,1134,1149,1164` (five branches in `extract_silkscreen`); the shared helper `kicad_core/sexp.py:209` (`has_flag`) already handles both forms
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F8)

**Symptom:** corpus files carry `(property "Reference" "LOGO2" … (layer "F.SilkS") hide (tstamp …` (e.g. JustinHsu845/PiEDB-Y15). Both the bare-`hide` form and the `(hide yes)` form give `refs_visible_on_silk 2, refs_hidden_on_silk 0`.

**Fix direction / budget:** use `has_flag` in all five branches. Budget: corpus output, `silkscreen` visible/hidden counters and the documentation warnings derived from them, on every board with hidden reference text. Size first.

### KH-575: legacy KiCad-5 `gr_arc` outlines are read with the wrong endpoints (zero-height bbox), and circular courtyards and curved board edges are dropped from geometry

**Severity:** HIGH (default path; 2,037 corpus boards carry KiCad-5 Edge.Cuts `gr_arc … (angle …)`)
**File:** `skills/kicad/scripts/pcb/reader.py:889`, `:1001-1006`, `:1025-1026` (legacy arc parsing and outline bbox); `:430-437`, `:434`, `:494-500` (courtyard fallback ignores `fp_circle`; consumer `assembly.py:223-226`); `skills/kicad/scripts/pcb/copper.py:1300-1316` (BV-001 converts only `line` / `rect` edges); `skills/kicad/scripts/cross_analysis.py:540` (NR-001 measures a `mid`-less arc as a chord); `skills/kicad/scripts/pcb/assembly.py:1045-1059` (KO-001 via keepout loop has no layer test)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F6, kc/R8-F5, kc/R9-F5, kc/R9-LT-KO)

**Symptom:**
- **Legacy arc outline:** in KiCad 5 `gr_arc`, `start` is the centre, `end` is the arc's first point and `angle` is the sweep. A two-arc KiCad-5 board reads as bbox width 20 / height 0, `height_mm 0.0`. In a 298-board sample the bbox is wrong by more than 0.05 mm on 28 boards and by more than 1 mm on 15. NR-001 then measures a fake chord edge inside the board.
- **Circular courtyard:** an `fp_circle (center 0 0)(end 3 0)` courtyard on a footprint at (110,100) yields `{min_x 110, min_y 100, max_x 113, max_y 100}`, so PM-001 misses the overlap.
- **Curved edges and BV-001:** a circle outline r = 10 with a via at (9.8, 0) gives no BV-001. 75 of 3,023 sampled PCB outputs (2.5 %) have no line/rect edge at all, so BV-001 can never fire on them.
- **Keepout:** KO-001 never checks a keepout's layers against the via span.

**Fix direction / budget:** convert legacy arcs (centre/start/sweep) to start/mid/end at read time. Include `fp_circle` (and arcs) in courtyard bounds. Give BV-001 and NR-001 arc/circle/polygon edges. Add the layer test to KO-001. Budget: corpus output on about 2,000 KiCad-5 boards (`board_outline` bbox / `dimensions`, NR-001 edges), PM-001 appearances on boards with circular courtyards, and BV-001 appearances (`--full`). Size first per sub-class. Waits on ruling: whether BV-001 measures from the via centre (today, `copper.py:1325-1330`) or the copper edge.

### KH-574: the `--full` connectivity graph unions a pad with only the nearest track endpoint, uses a max(w,h)/2 circle for pad copper, and leaves `F&B.Cu` pads on a fictitious layer

**Severity:** HIGH (opt-in `--full`; changes `connectivity_graph` islands on 98 of 250 sampled boards / 259 nets)
**File:** `skills/kicad/scripts/pcb/connectivity.py:402` (Phase 2 unions only `_SpatialGrid.nearest`, `:161-174`, and has no segment-interior pass); `:237`, `:401`, `:407-408`, `:26` (pad radius max(w,h)/2, tolerance and clearance, zone probe at 0.85·r); `:100-111`, `:234` (`_expand_copper_layers` does not expand `F&B.Cu`); `:200-213` (layer universe inferred from segments, vias and zones); `skills/kicad/scripts/pcb/geometry.py:316,352` (`CopperPresence` buckets `*.Cu` / `F&B.Cu` literally)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F2, kc/R8-F7, kc/R8-F1)

**Symptom:**
- **Nearest endpoint only:** a three-pad case gives `islands: 2` and `disconnected_pads [['C:1','R:1']]`, and a pad in the middle of a 95→105 track also gives `islands: 2`. Unioning every endpoint within tolerance changes island counts on 98 of 250 random corpus boards (259 nets, an upper bound).
- **Circle surrogate:** a 6×0.4 pad with a 0.7 mm bare gap to a same-net track gives `islands: 1`, because the radius is 3 and the threshold is 3 + 0.1 + 0.12 mm. A real gap is hidden. Consumers are cross_analysis RP-002 (`:614`) and PS-002 (`:754`).
- **Layer wildcards:** an `F&B.Cu` pad with a B.Cu track gives `islands: 2`, and `has_coverage_near(..., 'B.Cu')` over a THT pad is False. This shifts the return-path % in `routing.py:453` (threshold 95 %, `:472`). `F&B.Cu` is the first layers clause in at least 1,026 KiCad-5/6 corpus files.

**Fix direction / budget:** union every endpoint and segment interior inside the pad's real outline (rect/oval/polygon, not a circle). Expand `F&B.Cu` / `*.Cu` from the board layer table in both the graph and `CopperPresence`, and keep KH-417's NPTH type check. Build against a kicad-cli ratsnest/DRC oracle together with KH-364 (fills and arcs). Budget: `--full` only (`connectivity_graph`, PS-002 / RP-002, return-path coverage %), about 40 % of sampled boards. A full-chain profile class. Waits on ruling: R8 O2 (any-net copper credited as a return path), O4 (same-number pads force-unioned at `connectivity.py:346-350`), and O5 (confidence degradation for unmodelled shapes).

### KH-573: thermal-pad via adequacy (TV-001) counts vias of any net and layer, and its exemption hides an untented via in a signal pad (VP-001)

**Severity:** HIGH (TV-001 default path; feeds thermal's via correction factor)
**File:** `skills/kicad/scripts/pcb/copper.py:648-668` (Tier-1 loop over `all_vias` with no net or layer test; only Tier 2 at `:697` checks net); `:1219-1220` (VP-001 exemption by component ref, called at `pipeline.py:484-486`); consumer `analyze_thermal.py:349-354`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F2, kc/R9-F6)

**Symptom:** a 2×2 mm GND exposed pad with 5 net-99 vias at x = 1.3 (outside the pad, inside the 1.5× box) gives `via_count 5`, `adequacy adequate`, `severity info`. Thermal then applies the via correction from those foreign vias. The VP-001 exemption set holds component refs from TV-001 entries, so every SMD pad of that footprint is skipped. A QFN with an untented via in signal pad 1 gives `[]` with the exemption and `Via in pad: U1:1 (untented)` without it (`--full`).

**Fix direction / budget:** in Tier 1, count only vias on the pad's net that span the pad's layer. Exempt by `(ref, pad)` for the exposed pad only. Budget: corpus output, TV-001 `via_count` / `adequacy`, thermal via correction (Tj values), and VP-001 appearances (`--full`). Size first. This is distinct from KH-441 (via_in_pad first-pad attribution).

### KH-572: diff drops rich findings without a `reference`/`detection_id` and counts only entities, so VD-001 additions and routing-only regressions report "No changes detected"

**Severity:** HIGH (every PR through the Action; also drives the analysis cache's new-run decision)
**File:** `skills/kicad/scripts/diff_engine.py:369` and `:120-141` (`_get_key` / `_generic_identity`; `_diff_lists` drops items whose key is None); `:1006-1050` (total count), `:873-910` (severity); `:535,540` (footprint `lib_id`); `:583-585` (EMC severity reads flat legacy keys); `diff_analysis.py:523,53` (`has_changes`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R12-F1, kc/R12-F4, kc/R12-reg-libid)

**Symptom:**
- **VD-001:** the finding from `system_analyses.py:824-836` carries only `components` / `nets` / `finding_id` (checked on corpus AmpStation PowerAmp). `diff_schematic(base={}, head={VD-001})` → `{}`, total 0, severity none.
- **Routing-only change:** `diff_pcb` with only `routing_complete` True→False and unrouted 0→2 gives total 0, severity none. A statistics-only schematic diff gives total 0, severity minor.
- **What the user sees:** both say "No changes detected." `action/format-report.py:438` skips the "Changes from Base" PR-comment section, and `analysis_cache.py:676-677` keeps the current run.
- **Footprint swaps:** corpus PCB footprints have no `lib_id`, so a swap with the same value and layer is never reported as modified.
- **EMC severity:** the nested `summary.by_severity` is never compared.

**Fix direction / budget:** key rich findings by `finding_id` (fallback `components`+`nets`). Derive `has_changes` from a non-empty diff, not from the count. Compare footprint `library`. Read the nested `by_severity`. Budget: diff JSON/text, the Action PR comment, and the cache new-run decision. This is not an analyzer corpus class, but product text-oracle diff artefacts may move. Waits on ruling: the `total_changes` counting unit (the entity-only count is documented in `references/diff-analysis.md:253`). The `has_changes` fix does not wait.

### KH-571: `what_if` never reaches the patched detection for SPICE, EMC or tolerance, and its crystal fix suggests one cap when the formula is joint

**Severity:** HIGH (what_if CLI; the SPICE and EMC comparisons are empty or "UNKNOWN" on every run)
**File:** `skills/kicad/scripts/what_if.py:327-334` (SPICE re-sim passes `signal_analysis`, which `simulate_subcircuits` reads only in its pre-v1.3 guard, `simulate_subcircuits.py:109,135-150`); `:1224-1248` (EMC compare reads `overall_risk` / per-finding `risk_level`, keyed by rule); `:458` (tolerance field list from nominal deltas only); `:513-514`, `:1519-1521` (`parsed_value` treated as a dict); `:1005-1012` (crystal suggestions); `:119-120` (log sweep from 0)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R12-F2, kc/R12-F3, kc/R12-F8, kc/R12-F5, kc/R12-F9, kc/R12-reg-logsweep)

**Symptom:**
- **SPICE re-sim (stub recorder, RC R1 10k→11k on the CrabikBoards fixture copy):** both the before and after simulations see R1 = 10000 Ω and the result is `{}`. `sim_results[0]` is the first det of that type, not necessarily the patched one.
- **EMC compare:** `overall_risk` exists only in what_if.py, and findings carry `severity`, not `risk_level`. Before/after is always "UNKNOWN" and `improved` is always empty. The 8× RP-001 on 0101shift/Business_Card_AI collapse into one dict slot.
- **Tolerance:** `R1=10k+-5%` (nominal unchanged) gives delta `[]` and tolerance `[]`, while `R1=11k+-5%` gives 13.78-15.23 Hz.
- **`parsed_value`:** the producer emits a scalar (`schematic/presentation.py:81-83`), so JSON `changes.R1.before` is None and the exported `components[].parsed_value` stays stale (consumer `datasheet_verify.py:664`).
- **Crystal:** `_inverse_crystal_load` (`detection_schema.py:231-245`) is symmetric, so the two per-cap suggestions are one joint edit. 10/10 pF + 3 pF stray = 8 pF; one cap at 18 pF gives 9.43 pF and both give 12 pF.
- **Log sweep:** `R1=0..10k:3` raises a ZeroDivisionError traceback.

**Fix direction / budget:** rebuild the SPICE input as a `findings[]` list carrying the patched det, matched by identity. Compare EMC on `summary.emc_risk_score` and per-finding identity. Take tolerance fields from the swept components, not the nominal deltas. Handle a scalar `parsed_value`. Present the crystal suggestion as one joint change. Make a zero log-sweep bound a usage error (exit 2). Budget: what_if CLI JSON/text only, with no analyzer envelope or corpus budget. Re-freeze any what_if text-oracle artefacts. Waits on ruling: the `recalc_derived` freshness contract (which derived fields stay valid).

### KH-570: thermal `--text` report and `cross_verify.check_thermal_vias` read the retired `thermal_assessments` key, so the component table is missing and the counts print 0; a summary-only finding raises `KeyError: 'title'`

**Severity:** HIGH (every current thermal output through the text reader; `check_thermal_vias` always returns `[]`)
**File:** `skills/kicad/scripts/analyze_thermal.py:841,862-866,894` (`format_text_report`); `skills/kicad/scripts/cross_verify.py:561` (`check_thermal_vias`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F8)

**Symptom:** the producer emits `assessments` and `summary.by_severity` (`analyze_thermal.py:1139,1145`). Of 21,298 corpus thermal outputs, only 23 stale schema-less legacy files carry `thermal_assessments`. On a real current output, `format_text_report` omits the "Component Thermal Summary" table and prints HIGH/INFO counts of 0. A TJ-001-shaped finding (summary only, as `make_finding` builds it, `lookup_detectors.py:351-370`) raises `KeyError: 'title'`.

**Fix direction / budget:** read `assessments` / `summary.by_severity`, and render through `kicad_core.render.summary_or_title`. Port `check_thermal_vias` the same way, or retire it with cross_verify (ruling). Budget: thermal `--text` artefacts in the product text oracle (re-freeze with an allow entry). JSON is neutral. Must land before KH-470's `title` removal (see addendum).

### KH-569: `_classify_package` patterns match in the wrong order, so MSOP/TSSOP get SOP θJA and `SOP.*8` catches SSOP-28 and SOIC-14

**Severity:** MEDIUM (declared heuristic table; matters when dissipation is about 0.3 W or more in small packages)
**File:** `skills/kicad/scripts/analyze_thermal.py:95-102,137-141` (`_PACKAGE_PATTERNS` order, `_classify_package`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F4)

**Symptom:** MSOP-8 → `('SOP-8', 120)`, TSSOP-8 → `('SOP-8', 120)`, TSSOP-20 / TSSOP-14 / MSOP-10 → `('SOP', 100)`. `SOP.*8` matches SSOP-28 and any name with a later "8" (`SOIC-14_3.9x8.7mm`). A typical MSOP-8 θJA is about 180-210 °C/W, so at 0.6 W Tj is underestimated by about 40 °C (97 vs 145 °C, checked by hand).

**Fix direction / budget:** put the specific families before the generic ones, anchor the pin-count token, and add MSOP/TSSOP rows (and SOT-563, KH-430). Budget: thermal assessment θJA/Tj values move on boards with MSOP/TSSOP/SSOP parts. Size first by counting classified footprints per pattern.

### KH-568: thermal costs a current-sense shunt at the hypothetical 100 mV full-scale current and labels it `deterministic`, so a misdetected pF capacitor reports 2e9 W and Tj 3e11 °C

**Severity:** HIGH (default thermal path; 453 shunt assessments in 21,298 corpus thermal outputs, 135 of them above 1 W)
**File:** `skills/kicad/scripts/analyze_thermal.py:313-327` (shunt dissipation); producer `signal_detectors.py:1422-1423` (`detect_current_sense` 50/100 mV full-scale currents)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F6)

**Symptom:** thermal computes P = (0.1/R)²·R = 0.01/R. A 1 mΩ shunt gives 10 W, and in a 2512 package at 40 °C/W that is Tj = 425 °C (checked by hand). A capacitor misdetected as a shunt ("12 pF" read as 1.2e-11 Ω) gives 8.3e9 A, pdiss 2e9 W and Tj 3e11 °C (bit-preserve C64, Flipper_Zero_DIY). Findings on shunt refs: 150 TS-001, 26 TS-002, 29 TS-003.

**Fix direction / budget:** do not derive dissipation from the full-scale sense voltage. Use a known load current, or skip with a reason, at heuristic confidence. Separately, `detect_current_sense` must reject capacitors; this is the REPORT-5 owner's producer side and is new to that report. Budget: thermal assessments and TS-001/002/003 findings on shunt refs disappear or flip, about 453 assessments and 205 findings. Waits on ruling: the authoritative operating-current source and how unknown-load shunts are treated (shared with KH-566).

### KH-567: DP-005 diff-pair matching accepts `…P`/`…N` only, so USB `DP`/`DM` pairs are never paired

**Severity:** MEDIUM (warning-level DP-005; 5 of 4,000 sampled corpus schematics have differential `…DM` nets, all left unpaired)
**File:** `skills/kicad/scripts/cross_analysis.py:904-910` (`_find_diff_pairs` patterns)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F7)

**Symptom:** `USB_DP` matches `(.+)[_]?P$` with base `USB_D`, so the code looks for `USB_DN`. No pattern accepts `…DM`, yet the schematic producer pairs DP/DM (`schematic/net_analysis.py:1186`) and PR-004 marks them differential (`schematic/pipeline.py:289-292`). Affected corpus examples: xDuinoRail, am64x, usb-sniffer-lite, RLCMeterH750.

**Fix direction / budget:** add a `DP`↔`DM` pattern (better: read the schematic's own pairing). Budget: a small DP-005 appearance class on the boards with DP/DM nets. Under the sch↔pcb name-space bug (KH-487 addendum, kc/R11-F9) most pairs are still blocked, so the visible change stays small until that is fixed.

### KH-566: cross-analysis CC-001 / EG-001 / DA-001 / TW-001 read producer keys no analyzer emits, so they emit 0 findings on every real input (and cross_verify's decoupling check never matches)

**Severity:** HIGH (default cross-analysis path; dead on 100 % of 331 real corpus sch+pcb pairs)
**File:** `skills/kicad/scripts/cross_analysis.py:246,254,705` (CC-001 / TW-001 read PCB `pads` and top-level `estimated_iout_A`); `:313` (EG-001 reads top-level `pin_net`); `:371-386,410` (DA-001 reads `per_rail` / `rails` / `ics` / `ic_count` / `ic_ref`, and only `decoupling_list[0]`); `skills/kicad/scripts/cross_verify.py:422` (rail name used as `ic_ref`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F1, kc/R11-F2, kc/R11-F3, kc/R11-F11)

**Symptom:** these are the producer shapes today:
- `pcb/presentation.py:156` strips `pads` and emits `pad_nets` (191/191 corpus PCB outputs have `pad_nets`, 0 have `pads`).
- `signal_detectors.py:2188-2192` nests `estimated_iout_A` under `power_dissipation` (117 of 505 regulator findings carry the nested key, 0 the top-level one).
- No schematic producer emits top-level `pin_net`. Components carry `pin_nets` (`schematic/presentation.py:158`): 0 of 1,288 corpus outputs have `pin_net`, 1,210 have `pin_nets`.
- DC-DET emits one record per rail with `rail` / `capacitors` / `cap_count` (`signal_detectors.py:1226-1236`).

`run_all_checks` over 331 pairs: CC-001 ran 331× on 1,718 connectors with 0 findings; EG-001 ran 331× with 0 findings; DA-001 ran 173× and examined 0 items; TW-001 never ran ("no power regulator current estimates"). cross_verify's `(ic, cap)` lookup into PCB `decoupling_placement` (`pcb/assembly.py:109-112`) can never hit.

**Fix direction / budget:** read the current shapes (`pad_nets`, `power_dissipation.estimated_iout_A`, component `pin_nets`, the per-rail DC-DET records over the whole list). Ship producer-shape integration tests built from real analyzer output (kc/R11-F11). Budget: a new-findings class on cross units: CC-001, EG-001, DA-001 and TW-001 appear for the first time. Size first by re-running `run_all_checks` over the corpus pairs with the fix. Waits on ruling: the authoritative operating-current source for TW-001 (the record recommends `power_budget` rail loads with an explicit heuristic fallback; see the KH-432 addendum), and whether cross_verify is maintained or retired (this decides its half).

### KH-565: GR-005 "open board outline" fires at error severity on closed round boards because it counts draws instead of checking closure

**Severity:** HIGH (default path; 54 of the 55 corpus Edge.Cuts files with 1-3 D01 draws are arc outlines)
**File:** `skills/kicad/scripts/analyze_gerbers.py:1531-1537` (draw-count heuristic)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-F8)

**Symptom:** a round board drawn as one or two arcs has fewer than the threshold number of draws, so it gets an error-severity GR-005. Example: the corpus output `AlpenglowIndustries/Alpenglow_RadiantRainbow_PCB/Gerbers.json` carries GR-005 on a closed 53.68 mm round board. Corpus-wide there are 66 GR-005 findings.

**Fix direction / budget:** decide closure geometrically (endpoint chaining, with a full-circle G75 arc counting as closed) rather than by draw count. Budget: a GR-005 disappearance class, at most 66 findings, most of them expected to go. The circle-extent bug in KH-592 (kc/R10-F5) shares the arc handling, so land this one first or together with it.

### KH-564: gerber completeness (defaults branch) requires only the inner copper layers it found, so a missing inner layer reports `complete: True`

**Severity:** HIGH (default path without a `.gbrjob`; 3,475 of 5,449 corpus gerber outputs; a missing inner layer is fab-fatal)
**File:** `skills/kicad/scripts/analyze_gerbers.py:746-747` (`check_completeness` defaults branch); `layer_count` inferred at `:1219-1232` and never passed in
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-F3)

**Symptom:** `check_completeness([..., 'In1.Cu', ...], [PTH])` for a 4-layer set missing `In2.Cu` returns `complete: True, missing_required: []`. The required set is built from the inner layers present, not from the board's layer count.

**Fix direction / budget:** pass the inferred `layer_count` (or the gbrjob / drill evidence) into `check_completeness`, and require `In1..In(n-2).Cu`. Budget: corpus output on gerber units. `completeness` and GR-001 move on sets with a gap in their inner layers. Size first with a corpus walk (inferred layer count vs inner layers present).

### KH-563: `fab_release_gate` reads producer keys that no longer exist, so missing layers and EMC errors pass, and a mistyped optional input path still gives PASS under `--strict`

**Severity:** HIGH (the release GO signal; every real gerber and EMC input)
**File:** `skills/kicad/scripts/fab_release_gate.py:241` (`check_layer_completeness` reads `completeness.missing_layers`); `:316` (`check_emc` reads a flat `critical` count); `:572-575` (`_load`), `:578` (`run_gate`); `:294` (thermal `f.get("components", ["?"])[0]`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-F1, kc/R10-F9, kc/R10-F2, kc/R10-reg-thermalidx)

**Symptom:** `analyze_gerbers.py` emits `missing` (gbrjob branch, `analyze_gerbers.py:738`) or `missing_required` / `missing_recommended` (defaults branch, `:755-756`). Nothing writes `missing_layers`: 0 of 5,449 corpus gerber outputs carry it, while 656 have a non-empty missing list. `run_gate` with `missing_required: ['Edge.Cuts']` reports layer_completeness "pass — All expected layers present". EMC: the producer writes `summary.by_severity` (`analyze_emc.py:592-602`), so `check_emc` with `by_severity.error = 4` returns pass on every real EMC input. A mistyped `--gerbers` / `--thermal` / `--emc` path makes `_load` return None, the check becomes "skip", and `--strict` still gives PASS. A thermal error finding with `components: []` raises IndexError at `:294`.

**Fix direction / budget:** read the producer's real keys (`missing` / `missing_required`, `summary.by_severity.error`). Treat a missing file at an explicitly given path as an error. Guard the empty `components` list. Budget: fab gate statuses only, with no analyzer envelope change. The harness has only no-crash tests (`test_downstream_tools.py:152-178`), so add completeness and EMC-counter assertions. Waits on ruling for the follow-up parts: the gate's exit code on FAIL (today 0, `main()` :584-606), freshness/evidence policy, and input-kind validation.

### KH-562: `analyze_voltage_derating` IC abs-max read swallows JSON / OS errors with no `diagnostics` record [group 15]

**Severity:** LOW (observability)
**File:** `schematic/system_analyses.py:781-789` (`_read_ic_abs_max` inside `analyze_voltage_derating`: `except (json.JSONDecodeError, OSError): pass` / `return None`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-R1)

**Symptom:** a corrupt or unreadable extraction JSON silently disables the IC abs-max derating check.

**Fix direction / budget:** record one diagnostic through `kicad_core/diagnostics.record`. Budget: additive `diagnostics` entries on units with unreadable extractions (same additive class as KH-480; ≈0 in the corpus, which carries no extractions). Separately, the legacy VD-002 reader expects `absolute_maximum_ratings` while extractions carry `base.absolute_max`; that waits on the ruling to migrate VD-002 to the typed datasheet API or retire it in favour of AM-001.

### KH-561: LC-filter capacitor derating never runs — `apply_capacitor_derating` reads `filt["rail"]`, LC records carry `shared_net` [group 15]

**Severity:** LOW (missing derating results on LC filters)
**File:** `schematic/pipeline.py:647` (`apply_capacitor_derating` → `_derate_cap`, `filt.get("rail")`); producer `signal_detectors.py:692-830` (`detect_lc_filters`, no `rail` key)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-LT1)

**Symptom:** LC filter capacitors get no derating fields, whatever their voltage.

**Fix direction / budget:** read the LC record's rail-side net. Budget: additive derating fields (and any derating warnings) on LC-filter units; size first.

### KH-560: schematic connectivity quantizes keys to 0.01 mm and joins points within 0.05 mm of a segment — off-lattice points can join wrongly or straddle a bucket and split [group 15]

**Severity:** MEDIUM (realistic but uncommon; `net-tracing.md:50` documents exact coordinates)
**File:** `schematic/connectivity.py:322-323` (`build_net_map` → `key`), `:391-407` (`point_on_segment`, tol 0.05)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F7)

**Symptom:** on-grid drawings never hit it (computed pin positions are rounded to 4 dp, `schematic/reader.py:227-228`); a point off the 0.01 mm lattice by less than its pitch can merge with a neighbour, and two points 0.002 mm apart can fall into different buckets and stay unconnected.

**Fix direction / budget:** waits on ruling: exact integer IU coordinates plus a separate proximity diagnostic. Budget: size first (off-lattice units only). Possible shared concern with the kc-b R8 PCB bucketing tolerance.

### KH-559: root-schematic discovery checks only the root file's raw text — grandchild sheets are not found and `adc.kicad_sch` matches inside `my_adc.kicad_sch` [group 15]

**Severity:** MEDIUM (leaf invocations only; degraded and announced)
**File:** `kicad_core/project.py:183-209` (`is_referenced_as_child` / `_root_references_target`: substring membership of rel path or basename, child Sheetfile references never followed), `:264-286` (`discover_root_schematic` tier 3)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F7)

**Symptom:** invoking the analyzer on a grandchild sheet in a nested directory finds no root, so the leaf is analysed alone (with a warning pointing to `--project-root`, `schematic/pipeline.py:1264-1270`). A sheet named `adc.kicad_sch` is wrongly found as referenced by a root that contains `my_adc.kicad_sch`.

**Fix direction / budget:** parse `Sheetfile` properties and walk the hierarchy; compare whole path components. Budget: ≈0 (the corpus runs roots); leaf invocations only.

### KH-558: `classify_connector` reports every generic single-row connector (`Conn_01x04`) as `dual` [group 15]

**Severity:** MEDIUM (emitted metadata on nearly every board; no consumer)
**File:** `kicad_core/classify.py:507-509` (`classify_connector`: `conn_\d+x\d+` matches before the single-row branch); written at `schematic/reader.py:447-449`, `kicad_core/model.py:91`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F8)

**Symptom:** `classify_connector('Connector_Generic:Conn_01x04','Conn_01x04',4)` → (False, 'dual').

**Fix direction / budget:** test `conn_01x` before the generic pattern. Budget: large field-only class, `components[].connector_layout` on most boards, no finding movement.

### KH-557: `classify_inductor_shielding` matches `SHIELDED` inside `SEMI_SHIELDED` / `NON_SHIELDED` / `NONSHIELDED` → `shielded` [group 15]

**Severity:** MEDIUM (missed heuristic ML-001 EMC finding)
**File:** `kicad_core/passives.py:255-256` (`classify_inductor_shielding`); consumer `skills/emc/scripts/emc_rules.py:4378-4379` (ML-001 skips shielded)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F6)

**Symptom:** a footprint / value / MPN containing `NON_SHIELDED` classifies as shielded, the opposite of its meaning; ML-001 skips it. Input is footprint lib + value + MPN, not description (where most corpus "Semi-Shielded" hits, about 50, sit), so reach is small.

**Fix direction / budget:** check `NON` / `SEMI` / `UN` prefixes before `SHIELDED`. Budget: small; ML-001 appearances on those inductors.

### KH-556: PU-001 `_net_has_driver` suppresses the warning for any other IC on the net, whatever its pin type [group 14]

**Severity:** MEDIUM (deliberate FP policy whose docstring claims more than the code does)
**File:** `validation_detectors.py:163-174` (`_net_has_driver`; docstring "non-OD/OC IC output"), consumer `:346-349` (`validate_pullups`); net pins carry `pin_type` (`schematic/connectivity.py:360`, `:805`, `:885`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F3)

**Symptom:** an open-drain INT line from a sensor to an MCU input (no external pull-up) gets no PU-001, because the MCU counts as a "driver". The MCU's internal pull-up may be configured in firmware and is invisible statically, so the suppression may be right.

**Fix direction / budget:** waits on ruling: does an MCU input on the net suppress PU-001? Fix the docstring now (neutral). If tightened to push-pull outputs only, PU-001 appears on most INT→MCU nets (unmeasured; PU-001 was v2.3.2 gate class B, 4,894); size first.

### KH-555: `detect_missing_required_components` accepts any capacitor on the regulator rail as Cout / Cin — a second, unfixed site of the KH-377 ground-return distinction [group 14]

**Severity:** MEDIUM (cache-backed regulators with `cout_min`; rare topology)
**File:** `lookup_detectors.py:576-588` (`_net_has_component_type`), `:621-623` (Cin), `:632-636` (Cout) in `detect_missing_required_components`; the regulator detector already requires a ground return at `signal_detectors.py:2073-2078`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F5)

**Symptom:** a regulator whose output carries only a feedforward cap (FB-to-VOUT) is credited with an output cap; the "missing Cout" finding does not fire.

**Fix direction / budget:** reuse the KH-377 ground-return helper. Budget: corpus-invisible (no caches); one fixture with a feedforward-only output. Groups with KH-554's ruling wave but does not need its ruling.

### KH-554: lookup detectors (AM / OV / TJ / EX / FT / PM) never inspect fact staleness or quality, and AM-001 skips per-pin limits when no domain limit resolves [group 14]

**Severity:** MEDIUM (cache-backed parts only; no corpus caches)
**File:** consumers `lookup_detectors.py:108`, `:203`, `:316`, `:407`, `:504`, `:610` (no read of `_cache_context.is_stale` or `quality`); `lookup_helpers.py:34-38` (`get_facts` docstring names a nonexistent `facts.best(field, trust_gate=...)`); `skills/datasheets/datasheet_types/cache_reader.py:213-232` (`lookup` marks stale and still returns, by design); `lookup_detectors.py:116`, `:133-147` (`detect_absolute_max_violations`: per-pin `absolute_max` only tightens a resolved global limit; `:134-135` `continue`, empty `am_block` skips the component at :116); VDD synonym pool `:38-39`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F1, kc/R7-F8)

**Symptom:** `get_facts` returning facts with a quality flag is the deliberate v2.0 §3.A.1 design (consumers decide); the validation detectors do decide (`validation_detectors.py:485/580/924/1053`), the lookup detectors never do, so a stale or score <60 extraction drives deterministic AM / OV findings. An extraction with per-pin limits and no domain limit produces no AM-001 check at all. The VDD synonym pool can merge distinct domains.

**Fix direction / budget:** per-consumer gating (not inside `get_facts`, which would reverse §3.A.1); evaluate per-pin limits without a domain limit; correct the docstring now (neutral). Waits on ruling: the lookup-detector trust policy (stale / score <60 / unscored / pin-level evidence / synonym pool), which must come after KH-433 because staleness is unreliable on copied projects. Budget: corpus-invisible (no extraction caches in the corpus); user-visible on cached projects.

### KH-553: the pre-finalize severity histograms count only `critical` / `high` as errors — direct Python callers of `assemble_result` see zero errors [group 13]

**Severity:** LOW (CLI recomputes in `finalize_for_cli`; direct-API callers only)
**File:** `schematic/presentation.py:238` (`assemble_result`), `:453` (`assemble_legacy_result`); CLI recompute at `schematic/pipeline.py:1515`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F9)

**Symptom:** canonical findings use `error`, so the histogram built before finalize reports 0 errors. The only in-tree direct caller, `skills/datasheets/distributor_core/inputs.py:65`, uses components only.

**Fix direction / budget:** count through `kicad_core/render.normalize_severity`. Budget: CLI output-neutral; changes the direct-API result. Waits on ruling: whether the phase functions are a supported Python API (decides whether signatures may change).

### KH-552: `unconnected_pin_list` in IC pinouts is effectively dead — every placed pin has a net, so `not net_name` almost never holds [group 13]

**Severity:** MEDIUM (descriptive field the review LLM reads; NT-001 still reports the condition)
**File:** `schematic/ic_analysis.py:417` (`analyze_ic_pinouts`), count `:444`, list `:452`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F6)

**Symptom:** corpus: 123,992 IC pins sit on single-pin unnamed nets; for 123,795 of them the IC has no `unconnected_pin_list` entry. The field contradicts NT-001 (`schematic/net_analysis.py:64-89`).

**Fix direction / budget:** treat a pin alone on an unnamed net (and not NC-marked) as unconnected. Waits on ruling: whether a pinout row is a package or a symbol unit (sets multi-unit IC counting). Budget: `ic_pin_analysis` unconnected counts / lists on most units with ICs (large, field-only); same wave as KH-522..16 is fine.

### KH-551: legacy result path concatenates finding lists without the object-id dedupe — duplicate `finding_id`s on 59 legacy outputs [group 13]

**Severity:** MEDIUM (legacy `.sch` only)
**File:** `schematic/presentation.py:445` (`assemble_legacy_result`: plain `extend`); the modern path dedupes by object id at `:185-190`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F8)

**Symptom:** 59 of 10,843 legacy results serialise duplicate `finding_id`s, all `schematic:feedback_networks-*` (e.g. ubertooth-one). They pass through `finding_schema.assign_finding_ids` unchanged (kc-b R13).

**Fix direction / budget:** apply the modern path's object-id dedupe. Budget: duplicate findings disappear on the 59 legacy units.

### KH-550: BOM groups by (value, footprint, MPN) without `dnp` — a fitted and a DNP part merge into one row and the first member decides the row's DNP flag [group 13]

**Severity:** HIGH (fitted quantity wrong in the order sheet; 651 corpus files)
**File:** `schematic/bom_stats.py:28` (`generate_bom` group key), `:44` (row state from the first member), `:70` / `:107` (statistics count DNP rows by that flag)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F2)

**Symptom:** R1 (fitted) and R2 (DNP), both 10k 0402 with the same MPN, become one row with quantity 2 and `dnp` from whichever came first; `statistics.unique_parts` / `dnp_parts` follow. Corpus: 651 result files have a mixed fitted/DNP group. Unrelated to KH-483 and KH-365. The same rule in `bom_manager` (audit row sk/R5-F1) is filed separately.

**Fix direction / budget:** add `dnp` to the group key. Waits on ruling: whether `statistics.dnp_parts` includes `in_bom:false` parts (the merge is wrong either way; the ruling sets the target count). Budget: `bom[]` rows and `statistics.unique_parts` / `dnp_parts` on the 651 units.

### KH-549: `opamp_circuits` detection identity is `["reference"]` only — the units of a dual / quad op-amp share one `detection_id` and the diff drops per-unit changes [group 12]

**Severity:** HIGH (dual and quad op-amps are common; diff silently loses changes)
**File:** `detection_schema.py:301-303` (`opamp_circuits` `identity_fields=["reference"]`); detector emits one record per (ref, unit) at `signal_detectors.py:2593-2596`, `:2803-2804`; `compute_detection_id` hashes identity fields only (`detection_schema.py:647-662`); `diff_engine.py:120-141` keys by `detection_id`, last wins
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F6)

**Symptom:** a gain change on U1 unit B of an LM358 does not appear in `diff_analysis` output, because unit A's record overwrites unit B's in the map. Distinct from KH-483.

**Fix direction / budget:** add `unit` to the op-amp identity. Budget: `detection_id` moves on every multi-unit op-amp record; stored IDs in saved runs and `diff_analysis` against an older run need a compatibility note. Coordinate with the kc-b R12 diff-consumer entry.

### KH-548: lower-reach domain-detector gaps — isolator shared-ground check skipped with one ground net, BMS cell taps named `VBAT_CELLn` dropped as power nets, `VBOOT` partner looked up as `VSOOT` [group 11]

**Severity:** MEDIUM (info-level records)
**File:** `domain_detectors.py:273`, `:285` (`detect_isolation_barriers` guards; shared-ground loop :327-370); `:1608-1617`, `:1679` (`detect_bms_systems`: taps filtered by `is_power_net_name`, `cell_count = max`); `:2140-2148` (`detect_motor_drivers`: `suffix = vb_name[2:]`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F3, kc/R6-F8, kc/R6 register VBOOT)

**Symptom:** with a single ground net the per-isolator shared-ground check never runs (`shared_ground_warnings` of an info IB-DET record; possibly intentional non-isolated use). `VBAT`, `+BATT`, `VBAT_CELL4` are power names, `VC5` / `CELL5` / `BAT+` / `PACK+` are not, so `VBAT_CELLn` taps are dropped and the cell count is low (mitigated: BQ769x0 taps usually sit on an unnamed RC node). `VBOOT` → suffix `OOT` → looks up nonexistent `VSOOT`.

**Fix direction / budget:** run the shared-ground check whenever an isolator exists (report the single shared ground as info); count BMS taps by IC pin, not net name; compute the VBOOT partner by name pattern. Budget: small info-record changes on isolator / BMS / bootstrap-gate-driver units.

### KH-547: part-family keyword tables overlap and the first match wins — `sn74lvc` single-supply buffers are level shifters (exempting VM-001), `ser`⊂`deserializer`, `hmc54`/`hmc58`/`tps38`/`lis2`/`max9`/`stm32wl` in two tables; type-gated optocouplers missed [group 11]

**Severity:** MEDIUM (mostly mislabelled info records; the `sn74lvc` exemption reaches VM-001)
**File:** `domain_detectors.py:4115`, `:4157-4168`, `:4197-4208` (`detect_sensor_interfaces` / level-shifter keywords) → `validation_detectors.py:535-549` (`shifted_nets` exempt from VM-001); overlaps at `domain_detectors.py:846/858`, `:1009/1035`, `:1018/3987`, `:3335` vs `:3429/3466`, `:3978/3987` (branch :4016-4020), `:6100`, `:5726/5738` (WiFi first at :5768); optocoupler type gate `:5835-5837` (`detect_transformer_feedback`) + `detector_helpers.py:73-74`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F4, kc/R6-F9)

**Symptom:** a single-rail SN74LVC buffer is a level shifter and its nets skip VM-001 (often electrically right, since LVC inputs are 5 V-tolerant, but not by design); `stm32wl` is reported as WiFi/BLE, not LoRa; an optocoupler with an `OC` / `OK` ref (type `optocoupler`, not `ic`) is not found as TF-001 feedback. The stock `Isolator:PC817` with a `U` ref is matched.

**Fix direction / budget:** one classifier-precedence fix (longest / most specific match, explicit tables per family, the optocoupler type accepted). Waits on ruling: the MPN / capability authority for family matching (shared with KH-546). Budget: info record labels on the overlapping families, VM-001 appearances on single-supply LVC nets, TF-001 appearances; size first.

### KH-546: I2C address conflicts are grouped by `device_type:config`, so different models at the same address never collide, and two unresolved address pins collide as a deterministic error [group 11]

**Severity:** HIGH (IA-001 misses real conflicts and raises false `error`s)
**File:** `domain_detectors.py:5947-5971` (`detect_i2c_address_conflicts`: key at :5956; unresolved net → `'unknown'` at :5924; `severity='error', confidence='deterministic'` + `swap_connection` at :5968); table `:5906-5907`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F2)

**Symptom:** DS1307 and DS3231 (both 0x68, also in the table) never collide; INA219 / INA226 / PCA9685 at base 0x40 never collide. Two parts whose address nets the resolver does not recognise both get `'unknown'` and produce a deterministic `error` conflict. ADS1115 ADDR → GND/VDD/SDA/SCL is resolved correctly.

**Fix direction / budget:** group by resolved address per bus; treat `unknown` as unknown (no conflict, or an info). Waits on ruling: the authoritative MPN / capability source for I2C address maps (without one the fix swaps one prefix list for another). Budget: IA-001 appearances (cross-model conflicts) and disappearances (`unknown` pairs); size first.

### KH-545: integrated-magnetics RJ45 jacks (HR911105A, MagJack, HFJ11, LPJ, ARJP) are not counted as magnetics — "No magnetics" warning on a very common Ethernet design [group 11]

**Severity:** HIGH (common path; advisory sub-field)
**File:** `domain_detectors.py:432-441` (`detect_ethernet_interfaces`: magjack keywords recognised as `eth_connectors` only), `:595-606` (`impedance_advisory` "No magnetics"); `:530-531` (global fallback gives `pass` from an unconnected transformer)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F7)

**Symptom:** PHY → HR911105A with no discrete transformer → `impedance_advisory.status="warning"` "No magnetics"; a design with an unconnected transformer anywhere passes.

**Fix direction / budget:** treat integrated-magnetics jacks as magnetics, and credit a transformer only when it is connected to the PHY's MDI nets. Budget: Ethernet `impedance_advisory` status changes on magjack units; size first.

### KH-544: LED audit picks the first resistor on any non-ground LED net, including the supply rail — any pull-up on +3V3 becomes the "series resistor" [group 11]

**Severity:** HIGH (default path, every LED; current estimate from the wrong R)
**File:** `domain_detectors.py:4916-4951` (`audit_led_circuits` → `_scan_net_for_resistor`: `check_nets` includes the supply rail, first resistor returned with no check that it is in the LED's current path); `:5040-5042` (a string uses one `_estimate_led_vf`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F1)

**Symptom:** +3V3 → LED → R → GND: the rail is scanned first in pin order, so any 10 Ω–100 kΩ pull-up on +3V3 is reported as the LED's resistor. N-LED strings use a single Vf, over-estimating current ((12 − 3·2)/1k = 6 mA checks only with per-LED Vf). Distinct from KH-467 (Vf tables).

**Fix direction / budget:** walk only the LED's own anode / cathode nets (excluding rails and ground) and require the resistor's other end to continue the current path; sum Vf over the string. Coordinate with KH-532 (LR-001) and KH-467. Budget: LED audit resistor / current / power on most LED units; size first.

### KH-543: USB-PD controller exemption never fires (`pd_controller` key never set) and the source-Rp statuses can only be assigned to pull-downs [group 11]

**Severity:** HIGH (every listed PD controller with CC pins gets false `missing` pull-down messages)
**File:** `domain_detectors.py:2944-2992` (`detect_power_path`: `entry` never gets `pd_controller`, the only reference is the read at :2944; only ground-side resistors collected at :2961; the 56k / 22k / 10k "source" statuses at :2989- are reachable only for pull-downs)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F5)

**Symptom:** a controller with internal Rd/Rp (e.g. a PD sink IC) gets "missing CC pull-down"; a source design with Rp to VBUS is never recognised because Rp pulls up (56k / 22k / 10k to 5 V, or 36k / 12k / 4.7k to 3.3 V), while sink Rd is 5.1 kΩ to GND.

**Fix direction / budget:** set `pd_controller` from the controller match and collect rail-side resistors for the Rp statuses. Budget: CC status / message changes on USB-C units with PD controllers or source Rp; size first.

### KH-542: two consumer-producer key mismatches leave features dead corpus-wide — ADC `anti_aliasing` reads RC `reference` (producer writes `ref`), CD-DET reads `frequency_hz` (producer writes `frequency`) [group 11]

**Severity:** HIGH (the `anti_aliasing` feature never emits; 0 of 692 ADC-bearing outputs)
**File:** `domain_detectors.py:3116`, `:3276-3279` (`detect_adc_circuits` reads `reference`; producer `signal_detectors.py:630-631`, `:679-683` use `ref`); `domain_detectors.py:3748`, `:3758` (`detect_clock_distribution` reads `frequency_hz`; producer `signal_detectors.py:1065` writes `frequency`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F6, kc/R6 register CD-DET `frequency_hz`)

**Symptom:** `rc_by_net` is always empty, so `anti_aliasing` is never emitted (grep of harness `results/outputs/schematic`: 0 files with `"anti_aliasing"` vs 692 with ADC records). CD-DET `frequency_hz` is always null and the MHz suffix never prints.

**Fix direction / budget:** read the producer's key names; index the corrected high-pass `output_net` (land after KH-536). Budget: additive `anti_aliasing` records on ADC units with RC filters, and CD-DET `frequency_hz` / text on clock units; size both.

### KH-541: current-sense detection drops shunts whose two terminals are both power-classified; the second pass misses INA219-class pin names [group 10]

**Severity:** MEDIUM (missed CS-DET detection; no false finding)
**File:** `signal_detectors.py:1301-1304` (`detect_current_sense`, power guard); second pass `:1441-1473` (`_integrated_csa_pins` lacks IN+ / IN− / VIN+)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F5)

**Symptom:** a high-side shunt between `VBAT` and `VBAT_LOAD` (both power names) feeding an INA219 is not detected; one info CS-DET observation is lost.

**Fix direction / budget:** allow a power-to-power shunt when a sense amplifier sits across it, and add the INA-family pin names. Budget: CS-DET appearances on such boards; size first.

### KH-540: flyback-diode check is symmetric in the diode terminals — a reversed diode across a relay coil reads `has_flyback_diode=true` [group 10]

**Severity:** MEDIUM (designer-error path; false assurance)
**File:** `signal_detectors.py:3162-3179` (`detect_transistor_circuits`: both branches ignore pin names / roles A/K)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F8)

**Symptom:** anode at +12V, cathode at the FET drain: the diode conducts across the coil when the FET is on and does not clamp at turn-off, yet the record says it has a flyback diode.

**Fix direction / budget:** require cathode on the supply side and anode on the switched node. Budget: `has_flyback_diode` flips and any related observation, on reversed-diode units only (expected tiny; size first).

### KH-539: parallel resistors and capacitors are handled as separate parts — a 10k / (10k‖10k) feedback divider reads 1.6 V (2.4 V correct), crystal CL uses the first two caps on any leg [group 10]

**Severity:** HIGH (divider half; crystal half MEDIUM)
**File:** `signal_detectors.py:224-294` (`detect_voltage_dividers`: two parallel resistors share two nets so the pair is skipped at :236; each pairs with R1 at ratio 0.5), `:3410-3418` (`postfilter_vd_and_dedup` keeps `entries[0]` with `parallel_count=2`); `:2690-2699` (op-amp parallel feedback); `:935-941` (`detect_crystal_circuits`: `load_caps` filled per net in sorted order and the first two taken whatever their `net`), `:1164-1167`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F3 parallel-equivalent half, kc/R5-F6)

**Symptom:** TPS54040 FB with 10k top and 10k‖10k bottom → 1.6 V, correct 2.4 V. Op-amp with parallel Rf → −10 or −20 by hash seed, correct −6.667 (the determinism half is KH-509). Crystal with 22 pF + 5 pF trim on one leg and 27 pF on the other → 22·5/27 + 3 = 7.07 pF, correct (27·27/54) + 3 = 16.5 pF. `detection_schema.py:101` (what-if `estimated_vout` recompute) inherits the divider ratio.

**Fix direction / budget:** waits on ruling: compute the parallel equivalent, or mark the value uncomputed. Then sum each arm / leg before the formula. Budget: `voltage_dividers` / `feedback_networks` ratio, regulator `estimated_vout` → `rail_voltages`, op-amp gain, crystal `effective_load_pf` and the crystal validation findings on units with parallel parts; size first.

### KH-538: op-amp `non_inverting` configuration is unreachable — a ground-ended Rg is rejected and `neg_has_signal` is always true in the Rf+Ri branch [group 10]

**Severity:** HIGH (every non-inverting amplifier; dead SPICE template)
**File:** `signal_detectors.py:2759` (Ri loop rejects a ground-ended resistor), `:2773-2776` (`detect_opamp_circuits`: `neg_has_signal = ri_ref is not None`, so :2775 is never reached); consumer `skills/spice/scripts/spice_templates.py:430`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F2)

**Symptom:** Rf = 100k, Rg = 10k to GND, signal on + → `('transimpedance_or_buffer', None)`; correct is non-inverting, gain +11.

**Fix direction / budget:** treat a ground-ended resistor on the − input as Rg and decide inverting vs non-inverting by where the signal enters. Budget: `opamp_circuits` configuration / gain on non-inverting stages and the SPICE profile (the non-inverting template starts running); size both.

### KH-537: ESD design observation reads the singular `protected_net`; the producer emits `protected_nets` [group 10]

**Severity:** MEDIUM (DO-DET ESD observation only)
**File:** `signal_detectors.py:3523`, `:3827` (`detect_design_observations` reads the singular field); producer `:2541-2542`, `:2364-2365` emits `protected_nets`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F9)

**Symptom:** `has_esd_protection` is false for nets that a TVS array protects; no other reader of the field exists in `skills/`.

**Fix direction / budget:** read `protected_nets`. Budget: small; DO-DET observation text / flags on units with protection devices.

### KH-536: high-pass RC filters report the ground node as `output_net` and the R/C junction as `input_net` — every high-pass is skipped by the SPICE template [group 10]

**Severity:** HIGH (every high-pass RC; dead SPICE coverage)
**File:** `signal_detectors.py:634-635` (`detect_rc_filters`; the KH-116 comment at :636-638 contradicts the code; merge key at :666 uses these fields); consumer `skills/spice/scripts/spice_templates.py:177` (skips `out_net == "0"`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F4)

**Symptom:** C from IN to OUT, R from OUT to GND → `('high-pass','OUT','GND','GND')`. The input is the cap's far node and the output the shared node. Any spice-bundle report of "high-pass filters never simulated" has this root cause.

**Fix direction / budget:** for high-pass, input = `c_other`, output = `shared_net`; recheck the merge key at :666. The ADC anti-aliasing consumer (KH-542) indexes `output_net`, so land them in order. Budget: `rc_filters[]` input/output nets on every high-pass, RC merge results, and the SPICE profile (high-pass sims start running); size both profiles.

### KH-535: PS-001 regulator-cycle key repeats the closing node, so one 2-regulator cycle is reported once per start node [group 9]

**Severity:** LOW (designs with a PG/EN cycle)
**File:** `validation_detectors.py:1001-1019` (`validate_power_sequencing` → nested `dfs`: the cycle is `path[idx:] + [node]`; `sorted()` of A→B→A = [A,A,B] vs B→A→B = [A,B,B])
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-minor-2)

**Symptom:** the A↔B cycle yields two PS-001 findings with different summaries.

**Fix direction / budget:** key the cycle on its node set without the repeated closing node (or a canonical rotation). Budget: small; PS-001 duplicates disappear on cyclic units.

### KH-534: VM-001 `skip_en` is one net-wide flag — a regulator EN pin on the net skips every other domain pair on it [group 9]

**Severity:** MEDIUM (nets with three or more ICs, one of them a regulator EN)
**File:** `validation_detectors.py:571-608` (`validate_voltage_levels`: the heuristic path :595-606 and the trusted-threshold path :587-588 set `skip_en` for the whole net)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F4)

**Symptom:** a 5 V output fanning out to a 3.3 V IC input and a regulator EN reports no VM-001: the EN exemption also suppresses the 5 V → 3.3 V crossing. A new consequence of the fixed KH-424 path, separate from KH-461.

**Fix direction / budget:** exempt the EN endpoint pair only, keep checking the others. Budget: VM-001 appearances on such nets; size first.

### KH-533: FS-001 "requires external compensation" lists internally compensated parts (LM2596/LM2576, LM317/337/350, TPS5430/5450, MC3406x) and prescribes a harmful 10 nF FB→GND cap [group 9]

**Severity:** HIGH (every LM2596-ADJ / LM317 board with an empty FB net; the suggested fix can hurt the loop)
**File:** `validation_detectors.py:1325-1332` (`_REQUIRES_COMPENSATION_KEYWORDS`), `:1406-1429` (`validate_feedback_stability`, warning + `fix_params`); `:1380` ("divider impedance too low" info)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F7)

**Symptom:** LM2596/LM2576 (Simple Switcher) and TPS5430/5450 are internally compensated; LM317/337/350 and LT108x ADJ bypass caps are optional ripple-rejection parts; MC3406x has no compensation pin. Only UC384x/UC282x COMP and TPS40xxx controllers need an external network. The fix prescribes 10 nF FB→GND, which adds a pole on a FB node. The low-impedance info also fires on the LM317 datasheet-standard 240 Ω / 720 Ω divider (180 Ω parallel, needed for the minimum load current).

**Fix direction / budget:** reduce the keyword list to parts that really need external compensation (UC384x / UC282x / TPS40xxx), drop the FB→GND prescription, exempt LM317-class dividers from the low-impedance info. Budget: FS-001 disappearances on LM2596 / LM317 / TPS54xx units (size first) plus the info disappearances.

### KH-532: LR-001 skips every low-side LED resistor — `series_resistors[].rail` is the resistor's far net, which is GND [group 9]

**Severity:** HIGH (default path; low-side current limiting is a common topology)
**File:** `validation_detectors.py:1159-1169`, `:1210-1213` (`validate_led_resistors`: `parse_voltage_from_net_name('GND')` → None, `continue` at :1213 skips both checks); `anode_net` / `cathode_net` computed at :1147-1157 and never read
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F2)

**Symptom:** +5V → red LED (Vf 1.8 V, table :1091) → 47 Ω → GND: (5 − 1.8)/47 = 68.1 mA, above the 40 mA trigger (:1095, :1216), 0.218 W; no finding. With 10 Ω: 320 mA and 1.02 W; both the current and the dissipation findings are lost.

**Fix direction / budget:** take the supply from the LED anode side (the far end of the LED string), not the resistor's far net. Coordinate with KH-544 (LED audit series resistor) and KH-467 (Vf tables). Budget: LR-001 appearances on low-side LED circuits; size first.

### KH-531: USB VBUS capacitance check has no upper bound — a device port with more than 10 µF passes [group 8]

**Severity:** MEDIUM (missing check on an aux status; needs port-role inference)
**File:** `schematic/system_analyses.py:2377-2408` (`analyze_usb_compliance`: only `total_uf < 1.0` warns, else `"pass"`; caps counted without confirming a ground return)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F2)

**Symptom:** USB 2.0 §7.2.4.1 limits a device / upstream port to 10 µF at attach (unless inrush-limited); hosts / downstream ports need ≥120 µF. A 47 µF device VBUS reports `pass`.

**Fix direction / budget:** waits on ruling: extend UC-004 with a role-gated upper bound (new semantics on an existing rule) or document as a known limitation. If extended: UC-004 status changes on device-role boards with >10 µF; size first; also require a ground return for counted caps.

### KH-530: capacitor voltage-derating stress uses pin 1's power net and skips negative rails — rail-to-rail and negative-rail caps are mis-assessed [group 8]

**Severity:** MEDIUM (small population; VD-001 / VD-004)
**File:** `schematic/system_analyses.py:749-755` (selection), `:807-818` in `analyze_voltage_derating` (`_find_power_net` takes the pin-1 power net, ignores the other terminal unless ground; `v_rail <= 0` skips negative outputs, which `signal_detectors.py:1961` produces by negating inverting Vout)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F6)

**Symptom:** a cap between +12V and +5V is derated against 12 V (stress is |V1 − V2| = 7 V); a cap on −12V is skipped. Negative rails named `-12V` also depend on the sign fix (KH-519).

**Fix direction / budget:** stress = |V(pin1) − V(pin2)| with ground = 0 and signed rails. Budget: VD-001 / VD-004 movement on rail-to-rail and negative-rail caps; land after KH-519.

### KH-529: `power_sequencing` PG→EN edges exist only when the consumer regulator precedes the producer in `power_regulators` [group 8]

**Severity:** MEDIUM (multi-regulator designs with PG→EN chains; order-dependent)
**File:** `schematic/system_analyses.py:1644-1647` (`analyze_power_sequencing`: the PG scan runs inside the per-regulator loop over the `dependencies` appended so far; no post-loop join)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F7)

**Symptom:** regulator A's PG drives regulator B's EN; when B is listed before A the edge is recorded, when after it is lost. No ordering contract exists.

**Fix direction / budget:** two passes, build all dependencies, then join PG→EN. Budget: small; `power_sequencing` edges / `sequence_order` on multi-regulator units. The meaning of `sequence_order` (startup dependency vs PG→EN depth) is an open ruling but does not block this fix.

### KH-528: schematic `pdn_impedance` combines decoupling branches as Σ1/|Z| — antiresonance peaks understated (2.6× in the worked case) [group 8]

**Severity:** HIGH (every schematic with decoupling caps; `pdn_impedance` section)
**File:** `schematic/system_analyses.py:78-82` (`_cap_impedance` returns a real magnitude), `:177-180` (branches combined as Σ1/|Zi|), `:184` (VRM term, same real-only combination) in `analyze_pdn_impedance`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F3)

**Symptom:** two caps with ESR 0.005 / 0.0379 Ω give Z1 = 0.005 + j0.04879 and Z2 = 0.0379 − j0.05063 at 15.8489 MHz; the magnitude method gives 0.027622 Ω, the complex parallel 0.072232 Ω. The magnitude sum is bounded above by min|Zi|, so antiresonance peaks are always understated, never shown at full height.

**Fix direction / budget:** complex admittance sum, VRM included. The EMC twin (`skills/emc/scripts/emc_formulas.py:646`, audit row sk/R1-F1) is filed separately; the two must be fixed together so the schematic and EMC PDN models agree. Budget: `pdn_impedance` values on every unit with decoupling (and the EMC PDN results via the twin); size first.

### KH-527: I2C `vol_compatibility` treats the VOL limit as an upper bound on the pull-up — warns on every realistic pull-up (4.7 k, 10 k, 2.2 k) [group 8]

**Severity:** HIGH (every I2C bus with a pull-up)
**File:** `schematic/system_analyses.py:1059-1124` (`analyze_protocol_compliance`: `r_max_for_vol = 0.4/(iol_ma*1e-3)` → 133 Ω / 67 Ω; `:1112` `if min_pu_ohms > r_max_for_vol` warns); exported via `schematic/pipeline.py:1154` → `schematic/presentation.py:324` as `protocol_compliance.findings[].issues` + `checks.vol_compatibility`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F1)

**Symptom:** VOL bounds the pull-up from below: R_min = (VDD − VOL_max) / I_OL (UM10204: 3 mA Standard/Fast, 20 mA Fm+), e.g. (3.3 − 0.4) / 3 mA = 967 Ω; the rise time gives the upper bound. Corpus: the warning is on 1,755 saved outputs / 2,229 buses; top flagged values 4.7 kΩ (685), 10 kΩ (679), 2.2 kΩ (344).

**Fix direction / budget:** compute R_min from VDD, warn when the pull-up is below it, rename / document `max_for_vol`. Budget: the warning disappears on nearly all 2,229 buses (section output, not rich findings); `checks.vol_compatibility` values change on every I2C bus with a pull-up.

### KH-526: `unconnected_hierarchical` lists hierarchical labels that ARE connected — membership is tested against net keys, not net labels [group 8]

**Severity:** HIGH (every hierarchical design; informational section, essentially always false)
**File:** `schematic/audits.py:1324-1326` (`validate_hierarchical_labels`: `scalar_hier_names - set(nets.keys())`); net naming at `schematic/connectivity.py:729-777` picks the parent-sheet / highest-priority label, so child labels are rarely keys
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F8)

**Symptom:** corpus: `unconnected_hierarchical` on 2,271 saved outputs; in a 400-output sample all 8,444 of 8,444 listed labels appear in some net's `labels[]`.

**Fix direction / budget:** test membership against `nets[*].labels`. Budget: `unconnected_hierarchical` empties on most of the 2,271 units.

### KH-525: I2C rise time over 1000 ns defaults the mode to "Standard" with no warning [group 7]

**Severity:** MEDIUM (I2C buses with heavy RC; the over-limit case is silent)
**File:** `schematic/net_analysis.py:698` (`_detect_i2c_buses`, no guard; the warning loop at :707 breaks only on a passing mode); `:664` (`load_count*5` pF)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F7)

**Symptom:** tr = 0.8473·RC > 1000 ns (UM10204 Standard limit; 300 / 120 ns Fast / Fm+ thresholds are correct) yields mode "Standard" and nothing flags the bus as out of spec. Side note: 5 pF per load is optimistic; the spec budgets about 10 pF per pin plus trace.

**Fix direction / budget:** report "exceeds Standard-mode rise time" when tr > 1000 ns. Budget: small; I2C bus records with large pull-ups / many loads. Unify with the second I2C enrichment path at the same time (record's deferred item).

### KH-524: CAN termination is computed once across all CANH×CANL nets and stamped on every bus [group 7]

**Severity:** HIGH (multi-CAN designs; small reach, wrong every time)
**File:** `schematic/net_analysis.py:975-995` (`_detect_can_buses`: one `termination` for all buses, :988 accepts any CANL net, not the paired one, :994-995 stamps it on every entry); same concept in the fallback `schematic/system_analyses.py:1287-1291` (`analyze_protocol_compliance`, "termination from any CAN pair")
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F4, kc/R4 register CAN fallback)

**Symptom:** corpus: 13 multi-bus files. FOME-Tech/Polygonus psu has CANH2/CANL2 credited with R9; USB2XXX has two hierarchical channels plus their CAN_TX/RX entries all credited with R10. Each bus segment is terminated independently.

**Fix direction / budget:** pair CANH/CANL by name stem and judge termination per pair, in both sites. Budget: small (the 13 multi-bus files); split / off-board termination is a separate rule-design question.

### KH-523: SPI `cs_conflicts` counts the controller on every CS net, substring-matches `SS` / `CS` in `VSS` / `SSP1_SCK`, and counts one IC twice [group 7]

**Severity:** HIGH (default path; the normal MCU + one slave case is reported as a conflict)
**File:** `schematic/net_analysis.py:1090-1093` (net selection: substring `SS` / `CS`), `:1100-1105` (`_analyze_bus_protocols`: every `type=="ic"` pin counted, no direction / role test, repeated pins of one IC counted)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F5)

**Symptom:** corpus: 1,321 `cs_conflicts`, 1,225 with exactly two devices (typically MCU + one slave, the normal SPI wiring); 134 sit on non-CS nets (SCK / MOSI / MISO / VSS, `DAC_VSS`, `SSP1_MOSI`); 51 list the same ref twice.

**Fix direction / budget:** match CS net names on token boundaries, exclude the driving controller, dedupe by ref. Budget: large; most of the 1,321 `cs_conflicts` disappear.

### KH-522: differential-pair `has_esd` is set by any shared IC — the USB PHY itself (e.g. `CH340G`) is credited as ESD protection [group 7]

**Severity:** HIGH (default path; a false protection claim on most pairs)
**File:** `schematic/net_analysis.py:1242-1251` (`_detect_differential_pairs`: any component on both legs with `type=="ic"` sets `has_esd`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F3)

**Symptom:** corpus: 10,894 pairs carry `esd_protection`; 8,960 of them name no part whose lib_id or value looks like a protection device (approximate substring test). Example: `CH340G` listed as the USB pair's ESD protection.

**Fix direction / budget:** credit only protection-classified parts (TVS / ESD array / protection-keyword ICs). Budget: large: `esd_protection` / `has_esd` on about 8,960 pairs. Check whether cross_analysis EG-001 (kc-b R11) consumes the field before sizing.

### KH-521: regulator detector takes the inductor's far side as `output_rail` on a boost (output = input rail, 5 V rail given 7.2 V), and the Vref lookup ignores the MPN [group 6]

**Severity:** HIGH (default path, boost converters without a VOUT pin; Vref half MEDIUM)
**File:** `signal_detectors.py:1804-1808` (+ retry `:1869-1876`) in `_build_regulator_record` (no boost qualification; `:2211-2232` only labels `sw_type`); `schematic/pipeline.py:326-330` writes `rail_voltages[out_rail] = v_out` unconditionally; `signal_detectors.py:1893-1894`, `:1910-1911` + `kicad_core/parts.py:146-200` (Vref lookup by value and lib_id only; `mpn` from `schematic/reader.py:379/409` never consulted); provenance `signal_detectors.py:1925/1943` reads `vref_source` before setting it
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F1, kc/R5-F7)

**Symptom:** an MT3608-style boost (+5V → L1 → SW, divider from +12V to FB) gives `input_rail=+5V, output_rail=+5V, estimated_vout=7.2`, so the 5 V rail carries 7.2 V into every rail consumer. A part identified only by MPN falls to the heuristic Vref (`vref_source: heuristic`, visible), which `rail_voltages` then consumes without regard to confidence; the provenance always says `divider_plus_lookup` / `heuristic`.

**Fix direction / budget:** for a boost, take the output from the diode / synchronous FET's far side (or the divider's top net), never the input-side inductor terminal; consult `mpn` in the Vref lookup; set `vref_source` before reading it. Budget: `power_regulators[].output_rail` / `estimated_vout` / `vref_source` and `rail_voltages` on boost and MPN-only regulator units, then the AM / OV / FT / VM inputs; size first; land after KH-520.

### KH-520: `rail_voltages` is keyed by the path-stripped net name — distinct `/<uuid>/VOUT` rails collapse, the safety detectors miss them, and sheet-stem voltages land on ground and switch nodes [group 6]

**Severity:** HIGH (default path, hierarchical designs; feeds AM-001 / OV-001 / FT-001)
**File:** `schematic/pipeline.py:330`, `:333` (`detect_topologies` stores `_clean_hierarchical_name()` keys; `kicad_core/netnames.py:189-190` strips to the last `/`); `:332-337` (power-net inference runs `_estimate_rail_voltage` on sheet-stem keys); consumers `lookup_detectors.py:126`, `:221`, `:424` (look up the raw pin net)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F1)

**Symptom:** `schematic/hierarchy.py:131` prefixes child hierarchical labels with the UUID instance path, so lookups by raw net miss. Corpus: 507 regulator outputs on UUID-qualified rails, 242 with a voltage but no matching key. bluerobotics/ping-dev-kit sonar_power has three distinct `/<uuid>/VOUT` nets collapsed into one `VOUT: 3.318`. The inference loop emits `'/3v3_buck/PGND': 3.3`, `'/3v3_buck/SW': 3.3`, `'/5v_buck/PGND': 5.0`, attaching the sheet name's voltage to ground and switch nodes; AM / OV / FT can then compare pins against a false rail voltage.

**Fix direction / budget:** key `rail_voltages` by the full net name, look up by the same, and do not infer a voltage from a sheet stem. Waits on ruling: whether `voltage_overrides` feeds detection or only summaries. Budget: AM-001 / OV-001 / FT-001 appearances and disappearances plus the `rail_voltages` key set; land after KH-518/11.

### KH-519: `parse_voltage_from_net_name` drops the sign — `-5V`, `NEG5V`, `-12V` parse as +5 / +12 V, and an unstripped sheet path is read as the voltage [group 5]

**Severity:** MEDIUM (wrong polarity in rail facts; magnitude-based checks unaffected)
**File:** `kicad_core/netnames.py:14-20` (`parse_voltage_from_net_name`); 21 callers, including `schematic/net_analysis.py:369` (`_rails_voltage_compatible`) and `schematic/bom_stats.py:95`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F4)

**Symptom:** `-5V` → 5.0, `NEG5V` → 5.0, `-12V` → 12.0, `/5V_sheet/VCC` → 5.0. `statistics.power_rails[].voltage` shows the wrong polarity, and a ±5 V pair counts as voltage-compatible. `bom_stats.py:94` strips the sheet path first, so the path sub-case does not reach `statistics.power_rails`, but it reaches the other callers. Feeds KH-530 and KH-532's negative-rail cases.

**Fix direction / budget:** return a signed value and strip the sheet path inside the function; audit the 21 callers for an `abs()` need first. Budget: corpus-output on units with negative rails (`power_rails[].voltage`, voltage-compatibility results); size first.

### KH-518: `is_power_net_name` treats `VCC_EN`, `5V_EN`, `VDD_PG`, `3V3_PG` as power rails — the control-suffix veto runs only on the no-underscore branch [group 5]

**Severity:** HIGH (default path, rail classification corpus-wide)
**File:** `kicad_core/netnames.py:114` (`5V_EN`), `:119-126` (first-segment list) in `is_power_net_name`; the `_VOLTAGE_SIGNAL_SUFFIXES` veto (:55) is applied only at :105; consumer `validation_detectors.py:270` (`validate_pullups` skips power nets before checking the pin)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F3)

**Symptom:** `VCC_EN`, `VBUS_DET`, `5V_EN`, `VDD_PG`, `VIN_EN`, `3V3_PG` → True; `5VEN` → False. PU-001 then never checks an open-drain PG / EN net named this way (it also needs extraction facts, :266, which narrows reach); rail statistics and the power tree count the control nets as rails.

**Fix direction / budget:** apply the suffix veto to the underscore-segment branch too; keep the `power_rails` membership short-circuit (:72), as the record recommends (ruling, recommended keep). Budget: corpus-wide rail classification (`statistics.power_rails`, power tree, PU-001 appearances); size first.

### KH-517: `snap_to_e_series` uses linear distance within the decade and the table has no 10.0 — values just under a decade snap down by up to 17 % [group 5]

**Severity:** HIGH (what_if `--suggest-fixes` E-series suggestions and EMC cap recommendations)
**File:** `kicad_core/values.py:197-201` (`snap_to_e_series`; the comment at :190-196 says log-scale nearest neighbour); consumers `what_if.py:832`, `skills/emc/scripts/emc_formulas.py:574` (`round_to_e12`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F5)

**Symptom:** `snap_to_e_series(9900,'E12')` → (8200, −17.17 %) where 10 k is nearer; `(9.6,'E24')` → 9.1 (10 is nearer); `(9.9,'E96')` → 9.76. The EMC skill bundle has the sibling note `round_to_e12(9.9 nF)` → 8.2 nF.

**Fix direction / budget:** log-distance nearest neighbour with the next decade's first value as a candidate. Budget: small; what_if suggestions and EMC recommendations whose value sits just under a decade boundary; size first.

### KH-516: `parse_value` rescales explicit-farad capacitor values as legacy pF/µF — `1F` → 1e-12, `120F` supercaps mis-scaled [group 5]

**Severity:** HIGH (default path, every schematic with a farad-unit value)
**File:** `kicad_core/values.py:61` (`parse_value`: the unit strip loses the explicit `F`) → `:104-112` (legacy pF/µF rescale); docstring `:36-37` says only bare integers are rescaled
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F2)

**Symptom:** with `component_type="capacitor"`: `1F` → 1e-12, `0.1F` → 1e-7, `1e-6F` → 1e-12, `1 F` → 1e-12, `0.47F 5.5V` → 4.7e-7. The corpus has `120F` ×40, `1F` ×11, `40F` ×4, `0.3F`, `0.10F`, `1.5F`, `2.5F`, `20F`, `50F` (about 80 values); each one is off by 1e-12 or 1e-6 and feeds `parsed_values` → RC / derating / power math.

**Fix direction / budget:** an explicit `F` suffix is SI; rescale only bare integers, as the docstring says. Waits on ruling: whether bare exponent notation (`1e-6`) is SI (record recommends SI; no KiCad 5 writer emits exponents). Budget: corpus-output on the supercap units (`parsed_value` and downstream RC-DET / derating / power-budget results).

### KH-515: modern sub-symbol names `Name_<unit>_<bodystyle>` keep only the unit — De Morgan symbols get both body styles' pins [group 4]

**Severity:** HIGH (default path, modern schematics with De Morgan symbols)
**File:** `schematic/reader.py:98-104` (`_extract_pins_from_node`, :100 keeps the unit only), `:187-195` (`compute_pin_positions`); no `convert` / `body_style` read anywhere in `schematic/` or `kicad_core/`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F3 modern half)

**Symptom:** `VCAR.kicad_sch` `4xxx:4001` units each carry duplicate pins 1/2/3, 4/5/6 … (six entries for three pins); the alternate-body pins sit at other coordinates and can join wrong nets. Legacy twin: KH-512.

**Fix direction / budget:** parse the body-style suffix and keep the placed symbol's body style (its `convert` / `body_style` field, default 1). Budget: corpus-output on De Morgan units (pin lists, pin→net); size first.

### KH-514: same-name global bus labels never union their members — `global_label` on a bus falls to role `local` in the bus pass [group 4]

**Severity:** HIGH (default path, designs that carry a bus across sheets on global labels)
**File:** `schematic/connectivity.py:456-463`, `:473-474` (`build_net_map`: a `global_label` gets role `"local"` and goes into `bus_label_idx`, skipping the global branch at :487); `:607-622` (`bus_slot`: members joined only via `label_keys.get((member, s))` / `member_rep[(s, member)]`, per sheet)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F4)

**Symptom:** a `D[0..7]` global bus label on two sheets leaves `D0`…`D7` as separate per-sheet nets; KiCad connects bus members across same-name global bus labels. No global-scope member union exists anywhere in the bus pass (:485-744).

**Fix direction / budget:** give global bus labels a global-scope member key. Budget: corpus-output on units with global bus labels (net merges); size first; oracle-check (kicad-cli netlist) on one such board.

### KH-513: legacy `$Sheet` blocks drop their F2+ sheet-pin records and child HLabels are keyed by bare name — legacy hierarchies never join parent to child, and same-named HLabels in different children short [group 4]

**Severity:** HIGH (default path, every hierarchical legacy schematic)
**File:** `schematic/legacy_reader.py:707-720`, `:775-783` (`_parse_legacy_single_sheet`, the `$Sheet` loop keeps only F1 = the file name); `schematic/connectivity.py:489-491` (`build_net_map`, HLabels into `label_keys` under the bare name with no namespace; the legacy caller `schematic/pipeline.py:885-896` adds only `_sheet`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F5)

**Symptom:** a legacy parent's sheet pins produce no port point, so a child's `HLabel VOUT` never reaches the parent net; two children each with an `HLabel EN` are merged into one net.

**Fix direction / budget:** parse the F2+ sheet-pin records into ports and namespace child HLabels per sheet instance, as the modern path does. Waits on ruling: whether repeated legacy sheet instances get per-instance refs (AR annotation), which sets the scope together with the hierarchy traversal. Budget: corpus-output on hierarchical legacy units (nets, every detector); size first; oracle-check.

### KH-512: the legacy library parser drops the pin visibility and De Morgan `convert` fields — hidden power pins never join their rail and both body styles merge [group 3]

**Severity:** HIGH (default path, legacy schematics with hidden power pins or De Morgan symbols)
**File:** `schematic/legacy_reader.py:266-289` (`_parse_legacy_lib`: pin dicts carry no `hidden` key, `parts[12]` (shape/visibility, `N` = invisible) is never read, `parts[10]` (convert) is discarded); consumer `schematic/connectivity.py:529-540` (`build_net_map` legacy implicit-power pass, which therefore never fires)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F6, kc/R2-F3 legacy half)

**Symptom:** the corpus `*-cache.lib` files hold 6,756 hidden VCC/GND/VDD/VSS `power_in` pins (`W N`); the implicit-power pass, whose comment names exactly this case, joins none of them to their rail. A De Morgan symbol's two body styles both contribute pins, giving duplicate pin entries per unit (the modern twin is KH-515).

**Fix direction / budget:** read the visibility field into `hidden` and keep only body style 1 (`convert` 0/1). Budget: corpus-output on legacy units with hidden power pins (power-rail membership, PP-001 / RS-001 / power tree on them) and on legacy De Morgan units; size first. Oracle-check on a legacy fixture with hidden pins.

### KH-511: legacy `.sch` pin positions invert Y twice under a raw TRANSFORM matrix and skip matrices starting with `-`; `_snap_pins_to_wires` then moves correctly placed pins to the nearest wire end [group 3]

**Severity:** HIGH (default path, every legacy KiCad 5 schematic)
**File:** `schematic/reader.py:205-228` (`compute_pin_positions`: raw-matrix branch `rpy = c*px + d*py` at :208, then `abs_y = cy - rpy` at :228); `schematic/legacy_reader.py:664` (`_parse_legacy_single_sheet`, `cl[0].isdigit()` drops matrix lines like `\t-1 0 0 1`); `schematic/legacy_reader.py:465-541` (`_snap_pins_to_wires`, sole caller `schematic/pipeline.py:970`, passes every component)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R2-F1, kc/R2-F2)

**Symptom:** KiCad legacy applies TRANSFORM as pos + T·p (default `1 0 0 -1` already flips Y); the code flips again. Share of pins landing on a wire endpoint before snapping, current code vs corrected convention: ltc3331.sch 79/110 vs 109/110; dtnking STM32F401CCT6.sch 99/150 vs 141/150 (74 matrix lines, several starting `-1`); clock.sch 32/68 vs 38/68; TemperatureHumidityEPD 60/66 vs 64/66. The snap pass hides much of this: its docstring (:468-471) says it exists for built-in fallback offsets, but it has no `_pin_source` guard and skips only power/flag types (:492), so any pin not on a wire endpoint (on an NC marker, a label, or another pin) is moved to the nearest endpoint within 12 mm in the pin direction (:528-539).

**Fix direction / budget:** apply the matrix as KiCad does, accept negative leading entries, and restrict snapping to fallback-sourced pins. Both changes land in one commit, because the snap is what compensates for the transform today. Budget: large legacy corpus class (pin→net maps on legacy units, then every detector on them); size first, and check against a kicad-cli netlist oracle on legacy fixtures (ltc3331, STM32F401CCT6). Check whether KH-403/404 boards are legacy `.sch`; this may bear on them (unproven).

### KH-510: `_tokenize` gives a quoted `")"` / `"("` the same token as punctuation, so valid files with a lone bracket in a string swallow the following symbols [group 2]

**Severity:** HIGH (valid input; every parser consumer, schematic and PCB)
**File:** `kicad_core/sexp.py:77` (`_tokenize`, quoted string appended as a bare `str`); compared as punctuation at `:94` / `:97` (`parse`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R1-F1)

**Symptom:** `parse('(kicad_sch (text ")") (symbol (lib_id "Device:R")))')` → `['kicad_sch', ['text']]`. On `ccadic/TI92-revive/ti92revive/keyboard.kicad_sch` (keycap values `(property "Value" "(")` at :1461 and `")"` at :1583) the file has 86 placed `(symbol (lib_id` blocks but parsing yields 78 top-level `symbol` lists; the ones in between are nested into a bogus list. About 26 corpus `.kicad_sch` / `.kicad_pcb` files hold a lone quoted `"("` / `")"` (a few false hits on escaped quotes). Distinct from KH-482, which is malformed input.

**Fix direction / budget:** give quoted strings their own token kind (a `str` subclass or tagged tuple) so the parser tells them from punctuation, keeping the parser's list-of-str output. Budget: corpus-output on about 20-26 units (restored components / nets and everything downstream); size the exact list with a corpus grep before the fix.

### KH-509: `netlist_queries.trace_through` / `components_within_hops` and the op-amp `fb_resistors` loop iterate sets — output order, first-match picks and op-amp gain vary with PYTHONHASHSEED [group 1]

**Severity:** HIGH (default path, every schematic; breaks the Layer-1 byte-stable rule; seed-pinned gates cannot see it)
**File:** `netlist_queries.py:194-201` (`trace_through` returns `_nets_by_comp`, a `set[str]`, in set order), `:285-286`, `:302` (`components_within_hops`); `signal_detectors.py:2690-2699` (`detect_opamp_circuits`, `for fb_ref in fb_resistors` over a set of str); first-match consumers `signal_detectors.py:1790-1797` (`_build_regulator_record`, `inductors = …; break`), `domain_detectors.py:3620-3627` → `:3695` (`_trace_clock_consumers` / clock distribution)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F9, kc/R5-F3 determinism half)

**Symptom:** a synthetic six-output clock buffer gives four different consumer orders at PYTHONHASHSEED 0-3 (`['CLK_OUT5','CLK_OUT3',…]`, `['CLK_OUT0','CLK_OUT1',…]`, …). A regulator whose other nets carry more than one inductor gets `reg_info["inductor"]` by hash order. An inverting op-amp with two parallel feedback resistors reports gain −10 on four of seeds 0-7 and −20 on the other four (correct −6.667; the parallel value is KH-539). Same class as KH-366/367, a new location; distinct from KH-421, though the regulator inductor first-match may feed KH-421's U54 regulator-capacitor drift, so re-run Marble's seed sweep after the fix.

**Fix direction / budget:** `sorted(...)` at the three `netlist_queries` returns and over `fb_resistors`; add a seed 0-3 A/B (synthetic clock buffer + parallel-feedback op-amp) to the determinism guard. Budget: order-only and first-match changes at seed 0. Size first with a seed-0 A/B (clock consumer lists, regulator `inductor`, op-amp gain on parallel-feedback units).

### KH-508: `action/examples/fork-safe-comment.yml` takes the PR number from the untrusted artifact and passes it unvalidated to the write-token comment step

**Severity:** MEDIUM (example workflow only, but users copy it; a fork PR chooses which PR or issue the privileged job comments on)
**File:** `action/examples/fork-safe-comment.yml:33-35` (PR number read from the lower-privilege run's artifact and written to `$GITHUB_OUTPUT`), `:42` (used by the comment step)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-reg-fork, register item promoted)

**Symptom:** the fork's run writes the PR number into its artifact, and the `workflow_run` job copies it into `$GITHUB_OUTPUT` without validation, so a fork can make the write-token job comment on any PR or issue. Should: take the PR number from `github.event.workflow_run` metadata, or require a bare integer.

**Fix direction / budget:** take the number from `github.event.workflow_run.pull_requests[0].number` (or match `^[0-9]+$` and fail otherwise). Budget: neutral (example file; no gate profile runs it).

### KH-507: SPICE `fail` results never set the Action's `has_critical` / status, because only EMC and thermal findings are counted

**Severity:** MEDIUM (Action gating; the outcome depends on a ruling)
**File:** `action/format-report.py:571-606` (only EMC and thermal append to `findings` before the counts), `:892,896`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F5, PARTIAL)

**Symptom:** a SPICE result with `status: fail` appears in the report body but never reaches the counts, so `has_critical` stays false and the Action does not fail. Whether that is a defect depends on intent: `entrypoint.sh:197` labels SPICE "optional, best-effort", and KH-442 still produces false SP-WARN, so counting SPICE could fail CI on false results.

**Fix direction / budget:** after the ruling, either count SPICE `fail` into the totals (behind an input, or only once KH-442 is fixed), or document in the Action README that SPICE never gates. Budget: output-changing (Action outputs and report summary); text-oracle budget for the Action report artefacts. Waits on ruling: should SPICE results gate the Action?

### KH-506: the Action report puts raw schematic strings (component values etc.) into Markdown unescaped

**Severity:** MEDIUM (report integrity in PR comments; GitHub sanitises HTML, so no script execution)
**File:** `action/format-report.py:1066` (raw `oa.get('value')`), also `:452-457,629,642-643,1013-1015,1081`; `skills/kicad/scripts/export_issues.py:168-209`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F6)

**Symptom:** a component value or other schematic string containing `|`, newlines, backticks, `[text](url)` or heading markers is placed into a table cell or list line as is, so a PR author can break the report's tables, add links, or forge report sections under the bot's identity. There is no escape helper in the file. `export_issues.py` builds GitHub issue bodies the same way. Should: one Markdown-escape helper for every interpolated analyzer string.

**Fix direction / budget:** one escape helper (table-cell and inline variants) applied at every listed site. Budget: output-changing in rendered report text only for strings containing Markdown-significant characters; needs a text-oracle budget for the `format-report` / `export_issues` artefacts (corpus-neutral).

### KH-505: extraction plan/result filenames interpolate the raw MPN, so `LM317/NOPB` crashes `_load_scout` and `../` writes outside the cache

**Severity:** MEDIUM (ordinary TI-style MPNs break the datasheets pipeline; the path write is local-argument reach with a fixed `.json` / `.plan.json` suffix)
**File:** `skills/datasheets/scripts/plan_extraction.py:73,179,182,191` (`_load_scout` and plan path); `skills/datasheets/scripts/merge_results.py:195,279-281`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F7, open-question row "Windows reserved and overlong filenames")

**Symptom:** the raw MPN is interpolated into the path. An MPN with `/` (e.g. `LM317/NOPB`, common for TI parts) produces a subdirectory path, so `_load_scout` raises `FileNotFoundError` with a traceback, against the degraded-input contract. An MPN with `../` writes a `*.plan.json` / `*.json` file outside the extraction directory. Windows reserved names (`CON`, `NUL`) and overlong names are not handled either. Should: one MPN-to-filename mapping, shared by plan, merge and cache readers.

**Fix direction / budget:** one MPN-to-filename mapping (the cache's existing sanitiser, or a new shared one) used by `plan_extraction`, `merge_results` and the cache reader, plus reserved/overlong name handling. Budget: output changes only for `/`-containing MPNs (their extraction filenames move); existing caches need a read-time fallback to the old name or the files go stale. Size the corpus `datasheets/extracted/` filenames with `/` or `\` in the MPN first.

### KH-504: `action/format-report.py` reads and writes text with the locale encoding, so the emoji report raises `UnicodeEncodeError` on cp1252/ASCII hosts

**Severity:** MEDIUM (supported non-UTF-8 hosts: Windows default locale, `LANG=C`)
**File:** `action/format-report.py:1402,1408,1413` (`open(args.output, "w")` with no encoding, writing emoji such as `:824` `🔴 FAIL`), `:131` (`open(path)` read with no encoding); `skills/spice/scripts/spice_model_cache.py:153` (`read_text()` with no encoding); plus the other sites listed in `REPORT-2.md` A2-F7
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F7)

**Symptom:** with a cp1252 or ASCII default text encoding, a normal report with a warning or SPICE section raises `UnicodeEncodeError` at `:1402`, and UTF-8 JSON or model caches can be misread at `:131` / `spice_model_cache.py:153`. Same class as the `c7eea3c` / `5e35592` encoding fixes, at sites those commits did not cover. Should: explicit `encoding="utf-8"` at every text open.

**Fix direction / budget:** add `encoding="utf-8"` at the listed sites, with a test under `PYTHONUTF8=0` and a cp1252 locale. Budget: output-neutral on UTF-8 hosts (every gate profile).

### KH-503: BOM datasheet-URL sync follows `Sheetfile` paths and symlinks outside the project and writes `Datasheet` values into those schematics

**Severity:** HIGH (reach Critical: `--recursive` is the documented normal usage on an untrusted project; outcome bounded to `Datasheet` values on matching refs in another `.kicad_sch`)
**File:** `skills/bom/scripts/kicad_sexp.py:89-91` (`base_dir / Sheetfile`); `skills/bom/scripts/sync_datasheet_urls.py:182` (`collect_schematic_files`, resolves symlinks with no containment check), `:256` (write to every collected file); `skills/bom/scripts/edit_properties.py:132` (property name written unescaped)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F4, open-question row "`edit_properties.py:132` unescaped `prop_name`")

**Symptom:** a sub-sheet whose `Sheetfile` is absolute, contains `..`, or is a symlink to a `.kicad_sch` elsewhere is collected, and `sync_datasheet_urls.py --recursive` (`skills/bom/SKILL.md:44,90`) rewrites `Datasheet` properties on matching references in that outside file. Values pass through `escape_kicad_string`, so no s-expression break-out occurs. Rider: `edit_properties.py:132` escapes the value but not the property name, which comes from the caller's update JSON (local reach only). Should: collect only sheets that resolve inside the project root, and escape property names.

**Fix direction / budget:** resolve each `Sheetfile` and require it under the root project directory (skip with a warning otherwise); escape `prop_name` in the same commit. Budget: output-neutral for in-project trees (BOM write-back is not a gate profile). Waits on ruling: shared-sheet write roots outside the project.

### KH-502: `analysis_cache` copies follow symlinked destination leaves and symlinked copy-forward sources, escaping the run directory

**Severity:** HIGH (local reach: `--analysis-dir` mode on a project tree with planted links; the Action writes with `-o` into `mktemp -d` and is not affected)
**File:** `skills/kicad/scripts/analysis_cache.py:448-455` (`shutil.copy2` onto the destination leaf), `:377-380` (copy-forward `isfile(prev_file)`), `:79` (containment check covers the run directory only); `skills/spice/scripts/spice_model_cache.py:175-178` (same leaf-link pattern); `skills/kicad/scripts/project_config.py:349-353` (`analysis.output_dir` escape, fixed-name sidecar only)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F3)

**Symptom:** a pre-existing symlink at an output leaf inside the run directory (for example `analysis/<run>/schematic.json` pointing elsewhere) makes `shutil.copy2` write through it to the link target. The KH-479 run-dir containment check covers the directory, not the leaf. Copy-forward checks `isfile(prev_file)`, which follows links, so an outside file is copied into the new run. The SPICE model cache write has the same pattern. Should: refuse symlinked leaves and symlinked copy-forward sources.

**Fix direction / budget:** `lstat` / `O_NOFOLLOW` on every leaf write and copy-forward source; refuse and record one diagnostic. Distinct from KH-491 (symlinked run dirs during prune) and KH-489 (model-cache atomicity). Budget: output-neutral (no gate profile uses `--analysis-dir`). Waits on ruling: may `.kicad-happy.json` choose a write root outside the project?

### KH-501: DigiKey OAuth token cache is a fixed shared `/tmp` file written world-readable, with three writers in two incompatible shapes

**Severity:** HIGH (local reach: another account on a shared Linux host reads a bearer token)
**File:** `skills/kicad/scripts/lifecycle_audit.py:186-210` (`gettempdir()/digikey_token_cache.json`, default mode, no chmod, no client binding, `access_token` shape); `skills/digikey/scripts/provider_digikey.py:72-112` (same path, `token`+`client_id` shape, chmod 0600 only after writing); `skills/spice/scripts/spice_spec_fetcher.py:252-282` (hard-coded `/tmp/digikey_token_cache.json`, default mode, lifecycle's shape)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F6, se/R2-F4; the skills-code bundle row sk/R2-F9 is the same defect and is absorbed here)

**Symptom:** on Linux the cache path is shared by every account (`gettempdir()` is per-user only on macOS and Windows). Lifecycle and the SPICE fetcher write the token with the umask's mode and never chmod. The provider chmods 0600 only after the write, which leaves a window. None of the three ties a cached token to the client ID that obtained it. Because the writers use incompatible shapes, each one invalidates the others' cache, which forces extra OAuth round-trips. A pre-planted file or symlink at the fixed path is also followed. Should: one per-user private location, created 0600, bound to the client ID, one schema.

**Fix direction / budget:** one core helper for all three writers: per-user private directory, file created 0600 (`os.open` with mode, `O_NOFOLLOW`), client-bound, one schema; the old shared file is ignored. Budget: output-neutral (online paths only; no gate profile touches DigiKey OAuth).

### KH-500: project-local SPICE model cache (`<project>/spice/models/`) is read verbatim and embedded ahead of every other source, and its manifest `file` is joined without containment

**Severity:** HIGH (Critical in the audit: an untrusted project supplies netlist text, which ngspice runs, on the default SPICE path)
**File:** `skills/spice/scripts/spice_model_cache.py:87-89` (tier 0 = project cache), `:148-154` (manifest `file` joined, `model_file.read_text()`), `:298-305` (tier 0 consulted first); `skills/spice/scripts/spice_templates.py:483-487,576` (model text embedded in the netlist)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F2)

**Symptom:** a repository that ships `spice/models/manifest.json` plus a `.sub` file has that text embedded verbatim into every netlist that resolves the part, ahead of the built-in, API and datasheet tiers, so the project chooses what ngspice executes (including control blocks). The manifest `file` value is joined at `:148` without a containment check, so an absolute or `..` value reads a file outside the cache. Should: project `.sub` text is used only under an explicit trust decision, and manifest `file` resolves inside the cache directory.

**Fix direction / budget:** containment check on the manifest `file`, and project models accepted only under an explicit trust setting (or parsed and filtered to `.subckt … .ends` with no control lines). Adjacent to KH-489, which covers the cache's atomicity and cleanup; this entry covers trust and containment. Budget: neutral for the corpus if the default keeps project models (the harness pins `--model-cache-dir` per unit, TH-077); changing the default moves SPICE results on every unit that ships a project model (size first). Waits on ruling: are project `.sub` files trusted programs?

### KH-499: schematic text with embedded newlines reaches SPICE netlists verbatim, so a component Value can inject ngspice directives (incl. `.control` blocks)

**Severity:** HIGH (Critical in the audit: reachable from an untrusted schematic on the default SPICE path; the Action runs SPICE by default when ngspice is present)
**File:** `skills/spice/scripts/spice_templates.py:384` (`value = det.get("value", "opamp")`), `:571` (value placed on a comment line); also `skills/spice/scripts/spice_models.py:149,166`, `skills/spice/scripts/spice_model_generator.py:77-78` (per the report); `skills/kicad/scripts/kicad_core/sexp.py:76` (turns `\n` escapes into real newlines); `skills/spice/scripts/spice_simulator.py:111` (netlist handed to the simulator); `action/entrypoint.sh:201-205`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F1)

**Symptom:** an opamp buffer whose Value is `OPA_AUDIT\n.control\nshell id\n.endc\n*` keeps its line breaks through the s-expression parser. The template writes the value onto a `*` comment line at `:571` with no line-break handling (only nets pass through `_sanitize_net`), so the netlist gains real `.control … .endc` lines and ngspice runs them with the caller's environment. Traced statically only; no simulator was run. Should: every schematic-derived string in a netlist goes through one encoder that removes or escapes CR/LF and other SPICE-significant characters, both in identifiers and in comment text.

**Fix direction / budget:** one encoder for identifiers and comment text, used by every template and model generator. Related item filed by the skills drafter: sk/R5-N2 (`escape_kicad_string` does not escape newlines). Budget: output changes only in `.cir` artefacts whose values contain line breaks or other encoded characters; SPICE results should not move for ordinary values, which needs a spice-offline budget check (expected: identical measurements, `.cir` text identical for ordinary values).

### KH-498: datasheet downloads accept any `://` URL (incl. `file://`, loopback, private hosts, redirects) with no byte or wall-clock bound

**Severity:** HIGH (reach Critical through the Action's automatic LCSC sync, outcome bounded: blind GETs to internal hosts, local PDFs copied in, availability)
**File:** `skills/datasheets/distributor_core/download.py:111,149-153,156-159,165-168,187,198` (`download_pdf`, urllib fallback, `resp.content`, `copyfileobj`); `skills/lcsc/scripts/provider_lcsc.py:279` (the only guard, `"://" in url`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F3, se/R1-F5)

**Symptom:** a datasheet URL taken from the project or a distributor response is fetched if it contains `://`. A scratch check on Python 3.12 confirmed that `file://` is fetched through the urllib fallback (`requests` rejects `file:` and falls through to urllib when it is installed). No loopback, private or link-local filter exists, and redirects are followed. Outcome: GET requests to local or internal hosts (blind unless the body is a PDF), and local PDFs copied into the project's `datasheets/`. In CI this reaches runner-local and internal endpoints, which matters most on self-hosted runners. Separately, `resp.content` buffers the whole body in memory, `copyfileobj` copies to disk without a limit, and `timeout=20` applies per socket operation, not per transfer. The PDF sniff happens only after the full transfer, so an endless or huge response runs the job until its timeout or until the disk fills. Should: fetch only HTTP(S) to public addresses, re-check on each redirect, and stop at a byte and time limit.

**Fix direction / budget:** HTTP(S) only, a public-address check after normalisation and on each redirect, streamed reads with a byte cap and a total-time cap (CLI override), and Playwright gated behind the same URL policy. Same commit as KH-497. Budget: output changes only for rejected URLs (diagnostics records); about zero on the corpus because the corpus does not run syncs, and the distributor-offline oracle replays recorded URLs (re-check both ways). Waits on rulings: the allowed private datasheet hosts and local-file import, and the byte/time limits plus override name.

### KH-497: distributor sync writes through symlinked `manifest.tmp` / `<name>.pdf.part` and renames manifest `file` paths from outside `datasheets/`

**Severity:** HIGH (Critical in the audit: reachable from PR content in the Action with no credentials, because the LCSC sync runs on every Action run)
**File:** `skills/datasheets/distributor_core/manifest.py:92-95` (`save_index`); `skills/datasheets/distributor_core/download.py:112,123,158,167` (`download_pdf`); `skills/datasheets/distributor_core/sync.py:153-163` (rename-present branch), `:195-203` (empty-BOM manifest save before `authenticate()`), `:208`, `:220-261` (`--parallel` `executor.map`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F1, se/R1-F2, open-question row "`executor.map` result never consumed")

**Symptom:** (a) `save_index` and `download_pdf` open a predictable sibling path (`manifest.tmp`, `<name>.pdf.part`) for writing, and `open()` follows a symlink there. A scratch check with a `file://` source and sentinel files: a committed `.part` symlink caused an outside file to be overwritten with the fetched bytes, and `os.remove(part_path)` then removed the link. A `manifest.tmp` symlink caused the outside file to receive the manifest JSON and left `manifest.json` as a link to it. The empty-BOM path saves the manifest before `authenticate()`. LCSC needs no credentials (`provider_lcsc.py:42-47`). (b) A manifest `file` value that is absolute or contains `..` makes `out_dir / old_file` resolve outside `out_dir`. `.exists()` is the only check, and `rename()` then moves the outside file into `datasheets/`. This runs before `authenticate()`. DigiKey and Mouser `preflight` return `{}` (`provider_digikey.py:35`, `provider_mouser.py:38`) with `RENAME_PRESENT=True`, so no credentials are needed; in the Action it fires only when the DigiKey or Mouser secrets are set. (c) Rider: with `--parallel`, the result of `executor.map` is never consumed, so worker exceptions are silently dropped. Should: create temp files exclusively under random names, refuse symlinked leaves, and require every manifest `file` to resolve inside `out_dir`.

**Fix direction / budget:** create exclusive random temp files (`mkstemp` / `O_EXCL|O_NOFOLLOW`), check symlinks and containment before every write and rename, validate manifest `file` values on load, and consume the `executor.map` results. Budget: output-neutral for regular project trees. The distributor-offline oracle (RUNBOOK 26j) should stay identical both ways. Add boundary tests (symlinked `.part`, symlinked `manifest.tmp`, `..` and absolute `file`). Waits on ruling: whether an external datasheet directory is ever allowed (the record's "Allowed private datasheet hosts, local-file import, external datasheet dirs, shared-sheet write roots" question).

### KH-496: docs/text leftovers from the review-period bug hunt (review C) — corpus-size wording, `what_if` sweep labels, datasheets SKILL line, offline `lifecycle_audit` unverified

**Severity:** LOW (documentation and `--text` wording)
**File:** README / SKILL docs (`5,800+` / `5,829` / `5,857` corpus-size variants), `skills/kicad/scripts/what_if.py` (sweep labels render as `1e+04`), `skills/datasheets/SKILL.md` ("used by both pipelines" line for `datasheet_page_selector`), `skills/kicad/scripts/lifecycle_audit.py` (behaviour without credentials unverified offline)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 17 (review C leftovers; deferred output-neutral docs items)

**Fix direction:** one corpus number sourced from the harness (`repos.md` count at the release), engineering-notation sweep labels, the SKILL line corrected, and an offline run of `lifecycle_audit` recorded. Budget: the `what_if` label change moves the `what_if` `--text` artefacts in the product text oracle (re-freeze with an allow entry); everything else is docs-only.

### KH-495: periphery minors from the review-period bug hunt (review B) — SPICE top-level JSON list traceback, generic values pass `is_real_mpn`, EMC stderr count pre-`--compact`, and ten unverified items

**Severity:** LOW
**File:** `skills/spice/scripts/simulate_subcircuits.py:135` (`analysis_json.get("findings")` on a top-level JSON list → `AttributeError` traceback, exit 1; the loader at `:597-603` accepts any JSON); `skills/datasheets/distributor_core/inputs.py:17-44` (`is_real_mpn` rejects <3 chars, bare value+unit, percentages, DNP/NC/N/A and letter-only or digit-only strings, but passes `4k7`, `2k2`, `100nF 50V`, `4.7uF 0805`, `10K 1%`, `1uF/16V`, `100nF X7R`, `SOT-23`, `MH1`, `Conn_01x02`); `skills/emc/scripts/analyze_emc.py:632` (stderr finding count printed from the pre-filter list after `:579-584` reduced `result['findings']`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); the three named items verified in source at `07b7fb1` (`results/v3_round9b_gate_aux/`, scratch report)

**Unverified riders (maintainer's list, not yet checked harness-side):** `--spice-enhanced` without a simulator only warns on stderr; the manifest `scripts` entry; `--add-distributor` silently drops unknown names; LCSC order quantities; `verify.py` error coverage; `format-report --severity` is loose; `detect_project.sh` zero-file exit; `_smoke_v14_roundtrip --help`; sub-sheet redirect provenance; the `datasheet_verify` flag message.

**Fix direction / budget:** the JSON-list and stderr-count items are neutral. `is_real_mpn` tightening is a **distributor-oracle re-freeze** (the part set and skip counts of the frozen sync runs change wherever a fixture BOM carries such values) — size against `tools/tests/fixtures/distributor/` before changing it.

### KH-494: core minors from the review-period bug hunt (review A) — NaN/non-numeric coordinates traceback, `--no-hierarchy` still merges top-level sheets, `--text` drops `--output`, no PCB duplicate-reference check, and eight unverified items

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/connectivity.py:323` (`(at nan 100.33 0)` on a placed symbol → `ValueError: cannot convert float NaN to integer`, traceback exit 1; `(at abc …)` → `kicad_core/sexp.py:195` `could not convert string to float`; no guard around `get_at` / `get_xy` in `schematic/reader.py:471-621` or `pcb/reader.py:52-374`); `schematic/pipeline.py:1281` (`merge_top_level_sheets` runs unconditionally — `hierarchy.py:197-198` says so by design — while `analyze_schematic.py:33` `--no-hierarchy` help says "treat file as standalone root"); `analyze_schematic.py:114-117` / `analyze_pcb.py:140-143` (`--text` prints and returns before the `--output` / `--analysis-dir` branches, no warning; EMC has the opposite precedence at `analyze_emc.py:628-640`); `pcb/*.py` (no duplicate-reference audit; the schematic has one at `schematic/audits.py:29`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 15 (review A minors); the four named items verified at `07b7fb1` (the NaN and `abc` cases by running the analyzer on an edited fixture)

**Unverified riders (maintainer's list):** datasheet index shape crashes; silent datasheet-manifest and sym-lib-table failures; missing `lib_symbols` gives no diagnostic; `--project-root` traceback; the `--stage` wording; zip-only gerber dirs; invalid numeric args accepted; thermal/cross exit-code mismatch.

**Fix direction / budget:** coordinate guards, `--text`+`--output` precedence and the unverified riders are neutral (malformed input / CLI only). The `--no-hierarchy` item is a `--help` text change (text oracle) if the doc is fixed, or neutral for the corpus if the behaviour is (the harness never passes the flag outside the standard profile, where it is on for every unit — a behaviour change there WOULD move sub-sheet-redirect units: size before choosing). A PCB duplicate-reference check is a **new finding** = corpus-output class on every board with duplicate footprint refs (size with a corpus scan of `footprints[].reference`).

#### Addendum to KH-494 (core minors, review A)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` part a, Empirical: "R1: diagnostics newline")
`skills/kicad/scripts/kicad_core/diagnostics.py:31`, `:38`: the stderr `Warning:` line embeds `str(exc)[:200]` unescaped, so an exception message containing a newline breaks the one-line-per-diagnostic stderr contract. Escape or replace newlines. Neutral for the envelope, stderr only.

### KH-493: Action `diff_base.sh` extracts only the schematic's own directory, so a base re-run drops sub-sheets referenced from outside it

**Severity:** LOW (GitHub Action diff mode only)
**File:** `action/diff_base.sh:31-37` (`git ls-tree -r <ref> -- <schematic dir>` filtered to `.kicad_sch` / `.sch` / `.kicad_pro` / `.kicad_dru`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 14 (review minor); verified at `07b7fb1`

**Symptom:** a sub-sheet referenced via `../` or an absolute path is not extracted into the base tree, and (KH-481) `parse_all_sheets` then drops it silently, so the Action's diff compares a complete head against an incomplete base and reports spurious removals. Neutral for the harness (no corpus profile runs the Action).

**Fix direction:** extract every `(sheet … (property "Sheetfile" …))` target reachable from the root (walk the base tree), or at least the repository root for the file types above.

### KH-492: DigiKey provider retries HTTP 429 recursively without a bound; outage attribution and 401 wording riders (review M6)

**Severity:** LOW (online paths only)
**File:** `skills/digikey/scripts/provider_digikey.py:209-212` (on 429: `sleep(10)` then `return search_digikey_with_token(…)` with no attempt counter — pre-existing); riders from the whole-range review M6: DigiKey outage attribution, the 401 "credentials" wording for an expired token, the no-op refresh branch in `distributor_core/sync.py`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 12 (M6) / 13; the 429 branch verified at `07b7fb1`

**Fix direction:** bounded retries with backoff (the sibling providers' pattern), token-expiry wording distinct from bad credentials, remove or wire the refresh branch. Budget: neutral — the distributor-offline oracle never sees a 429 (recorded responses).

### KH-491: `analysis_cache.prune_runs` raises on a symlinked sibling run dir and tracebacks on non-dict manifest values (review M3 / M4)

**Severity:** LOW (local analysis-dir hygiene; the containment fix KH-479 is not affected)
**File:** `skills/kicad/scripts/analysis_cache.py:77-81` (`_run_id_problem` accepts a symlink whose realpath is a sibling directory directly under the root), `:526-527` (`os.path.isdir` is true for a directory symlink and `shutil.rmtree` raises `OSError: Cannot call rmtree on a symbolic link`), `:503-505` / `:516` (`meta.get(...)` on a run value that is a string or null → `AttributeError`; `load_manifest` guards JSON-level corruption only — identical at `2498831`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 12 (whole-range review minors M3 / M4); verified at `07b7fb1`

**Fix direction:** reject a symlinked run id outright (or `os.unlink` the link instead of `rmtree`), and skip non-dict run values with a diagnostic. Budget: neutral (no gate profile uses `--analysis-dir`).

### KH-490: `analyze_emc.py --severity` rejects `error` / `warning` / `info` although the filter already understands them

**Severity:** LOW (CLI usability)
**File:** `skills/emc/scripts/analyze_emc.py:319-321` (`choices=['all','low','medium','high','critical']`); the consumer `emc_rules.py:4583-4587` maps the threshold through `kicad_core/render.normalize_severity`, which accepts the error/warning/info vocabulary, so only argparse refuses it
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 11 (review B minor, after `5e35592` made the filter case-insensitive); verified at `07b7fb1`

**Fix direction:** add the three names to `choices`. Budget: `--help` text change → the EMC `help__…` text-oracle artefact and the `--help` md5 set re-freeze (allow entry); corpus-neutral.

### KH-489: SPICE model cache / workdir hygiene after KH-477 — unlocked manifest read-modify-write, non-atomic `.sub` model write, 0600 manifest, per-process cache dir and `spice_sim_*` workdir never removed (`cleanup_workdir` dead)

**Severity:** LOW (local temp hygiene; measurements unaffected)
**File:** `skills/spice/scripts/spice_model_cache.py:182-188` (manifest read-modify-write with no lock: two concurrent writers each `os.replace` their own copy and the loser's entry is dropped), `:178` (`.sub` model written with a plain `write_text`), `:201-207` (`NamedTemporaryFile` creates 0600 and `os.replace` keeps it, so `manifest.json` is 0600 rather than umask mode), `:91-92` (the per-process `mkdtemp("kicad-happy-spice-")` fallback is never removed); `simulate_subcircuits.py:165-168` (`cleanup_workdir` assigned twice, read nowhere; no `rmtree` / `atexit` / `TemporaryDirectory` anywhere in `skills/spice/scripts/`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 10 (task-10 notes) and 12 (M5); verified at `07b7fb1`. The atomic manifest swap itself (KH-477) is in place.

**Fix direction:** write the `.sub` through the same temp-file + replace path, `os.chmod` the manifest to umask mode (or create it with `mkstemp` + explicit mode), a lock file (or per-writer merge on replace) for the manifest, `atexit`/`TemporaryDirectory` for the per-process cache dir, and either honour `cleanup_workdir` or delete it. Budget: neutral — the harness pins `--workdir` and `--model-cache-dir` per unit (TH-077) and never reaches the fallback dir.

### KH-488: Mouser `KEY_PRIORITY = ("mouser",)` keys every part without an MPN or Mouser number as `""`, so they collide in `manifest.parts[""]`

**Severity:** LOW (Mouser sync manifest only)
**File:** `skills/mouser/scripts/provider_mouser.py:22-23` (`ID_KEYS = ("mouser","digikey","lcsc","element14")` but `KEY_PRIORITY = ("mouser",)`); `skills/datasheets/distributor_core/sync.py:144-145` (`part_key = part["mpn"] or next(… provider.KEY_PRIORITY …)`); the other three providers have `KEY_PRIORITY == ID_KEYS`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 9 (review B-I8); verified at `07b7fb1`

**Symptom:** a part admitted by `extract_parts` on a DigiKey / LCSC / element14 number alone gets the empty key; every such part overwrites the previous one in the Mouser manifest.

**Fix direction:** `KEY_PRIORITY = ID_KEYS` (one line, the maintainer's `task-12-report.md`). Budget: **distributor-oracle re-freeze** — the maintainer measured 4 frozen runs change (`mouser/sync-default`, `sync-dry-json`, `sync-force`, `sync-legacy-index`); re-freeze them in the same commit and run RUNBOOK 26j both ways.

### KH-487: SPICE `--parasitics` matches net names verbatim between the schematic and PCB name spaces, so it applies only to RC-filter output nets on global or root-sheet labels

**Severity:** LOW (feature coverage, not correctness; harness SPICE profiles never pass `--parasitics`)
**File:** `skills/spice/scripts/spice_templates.py:112-115` (`parasitics_data["nets"].get(net_name)` verbatim), called only from `generate_rc_filter` (`:198`) with `det["output_net"]` — the other 17 generators accept `parasitics=` and ignore it. Schematic names (`schematic/connectivity.py:840-847`): bare `NET`, `/<sheet-file-stem>/NET` only on a cross-sheet collision, `__unnamed_N` for unlabeled. PCB names (`pcb/reader.py:160-190` → `net_lengths[].net`): KiCad's board names — `NET` for globals / root locals, `/<Sheet instance name>/NET` for sub-sheet locals, `Net-(R1-Pad1)` for unlabeled.
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 8 (review B-I2); verified at `07b7fb1`. The handoff's "never applies on real designs" is overstated: global-label / root-sheet RC filters do match.

**Fix direction:** normalise both sides (strip the sheet prefix, map `__unnamed_N` ↔ `Net-(…)` through the shared pad/pin net, or match through the cross-analysis net map) and pass `parasitics` to the other generators. Budget: corpus-output only under a SPICE profile that passes `--parasitics` (`run_spice.py --with-parasitics`); neutral for the default spice-offline profile.

#### Addendum to KH-487 (sch ↔ pcb net names compared verbatim)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F9)
The same name-space mismatch affects cross_verify and cross_analysis, not only SPICE `--parasitics`, and is HIGH there. Sites: `cross_verify.py:232-233,356,506`; `cross_analysis.py:145,256,719,993-996`. Comparing schematic `pin_nets` with PCB `pad_nets` by (ref, pin) over 331 corpus pairs (44,179 named pins), 14,785 names differ, 8,914 of them only by a `/…/` prefix, in 170 of 331 pairs. Root-sheet local labels differ too (sch `TD+` vs PCB `/TD+`), so the bug is not limited to child sheets. Fix both consumers through one shared sch↔pcb net correspondence (pad ↔ pin join) and widen the title. Waits on ruling: the correspondence design.

### KH-486: `.kicad-happy.json` suppressions (`components` / `nets`) are applied only by the EMC and thermal analyzers

**Severity:** LOW (documented feature gap; the corpus carries no `.kicad-happy.json` with suppressions)
**File:** `skills/kicad/scripts/project_config.py:838` (`apply_suppressions`) is called only at `skills/kicad/scripts/analyze_thermal.py:1082` and `skills/emc/scripts/analyze_emc.py:498`; `analyze_schematic.py:65-66` and `analyze_pcb.py:72-73` say so in comments; no call in `cross_analysis.py` or either `pipeline.finalize_for_cli`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 7 (review A-I14); verified at `07b7fb1`

**Fix direction:** apply the same suppression pass in the schematic, pcb and cross pipelines. Budget: **corpus-output if done EMC-style** (`suppressed` / `suppression_reason` keys on every schematic/pcb finding + the summary split → every unit's envelope changes = a schema/envelope class, not a findings class); neutral if the keys are added only when a suppression matches (0 corpus repos ship such a config: `find repos -maxdepth 6 -name .kicad-happy.json` = 0 at 2026-10-24).

### KH-485: `inputs.source_files` / `source_hashes` list only the root sheet and key the hashes by the path as given

**Severity:** LOW (provenance envelope; chained consumers verify the root hash only)
**File:** `skills/kicad/scripts/analyze_schematic.py:92-93` (passes `[Path(args.schematic)]` only), `skills/kicad/scripts/inputs_builder.py:60-64` (keys `source_hashes` by `str(p)` as given — a basename when invoked with a bare filename, a relative path otherwise, never canonicalised); sub-sheets walked by `parse_all_sheets` are never added. Thermal (`analyze_thermal.py:1049`) and cross (`cross_analysis.py:1134-1137`) list sch + pcb; gerbers lists every file.
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 6 (review A-I13); verified at `07b7fb1`

**Fix direction:** add every parsed sub-sheet to `source_files` / `source_hashes`, key by a path relative to the root sheet's directory. Budget: an **envelope class on every multi-sheet root** (4,261 of 36,462 corpus schematic units have components on more than one sheet, `results/v3_round9b_gate_aux/sec7_sizing.json`) — `volatile-leaves-v1` masks `source_hashes` VALUES after sha256 verification, not the key set, so the strict comparator reports the added keys; the chained analyzers' `source_hashes` linkage check (RUNBOOK 26i) must still find the root's hash under its old key or the policy needs a v2.

### KH-484: GR-002 compares layer extent SIZES, not offsets — a layer shifted by any amount with the same bounding-box size passes the alignment check

**Severity:** MEDIUM (a misaligned gerber set is exactly what GR-002 exists to catch)
**File:** `skills/kicad/scripts/analyze_gerbers.py:765-803` (`check_alignment` stores only `width = x_max - x_min` / `height = y_max - y_min` per layer and compares the max-min spread of the widths / heights against 5 % / 2 mm; `x_min` / `y_min` are never compared)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 5 (review A-I12); verified at `07b7fb1`

**Fix direction:** compare the per-layer bounding-box origins (and ideally the drill-vs-copper offset) with the same tolerance, keep the size check. Budget: **corpus-output on gerber units** (5,502 in the standard census): new GR-002 fires on sets whose layers share a size but not an origin — size with a corpus walk over the gerber outputs' per-layer extents before the fix.

#### Addendum to KH-484 (GR-002 compares extent sizes, not offsets)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R10-reg-GR002units)
A second unit defect is in the same function (`analyze_gerbers.py:785-792`). The 2.0 mm floor and the 5 % threshold are applied to raw extents in each layer's own units, so an inch-unit layer gets an effective 2-inch tolerance. Drills are never compared with gerbers (`alignment_layers` = F.Cu / B.Cu / Edge.Cuts / In*.Cu), so the reviewer's drill-vs-gerber mismatch does not occur. Normalise to mm in the same fix.

### KH-483: unannotated duplicate references (`U?`, `R?` …) collapse in the detector context and the BOM statistics

**Severity:** LOW (unannotated designs only; sibling of KH-455's `(ref, pin)` dedup)
**File:** `skills/kicad/scripts/kicad_types.py:21` (`comp_lookup = {c["reference"]: c for c in components}` — last wins; both symbols' pins carry `"component": "U?"` via `schematic/connectivity.py:352`), `schematic/bom_stats.py:15-24` / `:59-63` (dedupe by reference, so BOM rows and `statistics` counts drop the duplicates). The `components` list itself keeps both and `schematic/audits.py:29-45` flags them (`duplicate_references` + `unannotated`).
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 4 (review A-I5); verified at `07b7fb1`. Corpus (2026-10-24 scan of the 36,462 schematic outputs, `results/v3_round9b_gate_aux/sec7_sizing.json`): 1,598 units / 466 repos carry at least one `?`-suffixed reference on more than one symbol (`U?` 13,619 symbols, `R?` 9,013, `C?` 7,157, `D?` 3,203, `J?` 1,506, `P?` 1,259, `Q?` 895, `SW?` 664); 5,825 units carry `annotation_issues`.

**Fix direction:** key the detector context by UUID (or `reference#uuid`) and let BOM statistics count unannotated symbols individually. Budget: **corpus-output** on the units above — `statistics.total_components` / `unique_parts`, `bom[]` rows and every detector that resolves a pin's component through `comp_lookup` on those designs (SEED/STRUCT count locks move) — plus KH-455's PP-001 residue class.

### KH-482: truncated or non-KiCad input parses as a partial tree or one bare atom — exit 0, `diagnostics: []`

**Severity:** LOW (malformed input; the empty / whitespace-only case is now a usage error since `c6f4807`)
**File:** `skills/kicad/scripts/kicad_core/sexp.py:91-96` (raises only when `pos >= len(tokens)` at entry; the list loop `while pos < len(tokens) and tokens[pos] != ")"` exits silently at EOF); `kicad_core/project.py:376-385` rejects whitespace-only files only
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 3 (review A-I4); reproduced at `07b7fb1` — a fixture cut at 3,000 of 4,220 bytes and a plain-text file both exit 0 with `diagnostics: []` (the text file gives `components: 0`, `kicad_version: "unknown"`); `analyze_pcb` likewise exits 0 with 0 footprints

**Fix direction:** record one `diagnostics` entry when the parser reaches EOF inside an open list (truncation) or when the root atom is not `kicad_sch` / `kicad_pcb` (garbage). The maintainer removed a root-token REJECTION under ruling R14 because dozens of gate units with non-standard roots would have become rc 2 — so this must be a diagnostic, not an exit code. Budget: `envelope/diagnostics` on those non-standard-root units (size: count corpus units whose root atom is not the canonical one before choosing the wording).

#### Addendum to KH-482 (truncated / non-KiCad input)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` part a, Empirical: "R1: deep nesting refusal")
`kicad_core/sexp.py` `parse` is recursive. Nesting depth 990 parses, and depth 1100 raises `RecursionError` with a traceback and no diagnostic. Only adversarial input reaches it. Fold it into the same diagnostic: an iterative parser, or catch and record.

### KH-481: a sub-sheet whose file is missing is dropped silently — no `diagnostics` record, unlike the recursive and empty cases

**Severity:** LOW (provenance; the design is analysed without the sheet and nothing says so)
**File:** `skills/kicad/scripts/schematic/reader.py:713-716` (appends a sub-sheet only `if sub_path.exists()`, so `parse_all_sheets` never sees the missing file); `schematic/hierarchy.py:143-157` records diagnostics for the recursive (`:151-154`) and empty (`:84-90`) cases but has no branch for an absent file; `hierarchy.py:194-195` documents the gap
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 2 (review A-I2); verified at `07b7fb1`

**Fix direction:** record `schematic.hierarchy.parse_all_sheets` / `FileNotFoundError` / "missing sheet skipped" where the recursive case records. Budget: `envelope/diagnostics` additions on every corpus root with an unresolvable `Sheetfile` (size with a corpus walk before the fix; the harness's `diagnostics: []` expectations in the chain oracle and spice-offline comparator are additive-tolerant only through a budget).

#### Addendum to KH-481 (silent drops without a `diagnostics` record)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F8)
Same silent-degradation class on the PCB side. When every zone is unfilled, `pcb/copper.py:961-966` returns a warning dict that `pcb/presentation.py:414-420` pops, keeping only the finding lists, with no diagnostic. Per-zone `is_filled` is still emitted (`reader.py:792` → `presentation.py:202`), so it is not invisible. 61 of 3,023 sampled boards have only unfilled zones. Waits on ruling R9-F8 (which skipped checks get a `diagnostics` record).

### KH-480: a failed SPICE simulation leaves no `diagnostics` record (the `5e35592` record was reverted in `cf51839` as output-changing)

**Severity:** LOW (observability; the result already says `status: skip`, `note: "Simulation failed"`)
**File:** `skills/spice/scripts/simulate_subcircuits.py` (`run` path; the one-hunk implementation is `git show 5e35592 -- skills/spice/scripts/simulate_subcircuits.py`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 1 (implemented in `5e35592`, reverted in `cf51839` to keep the release range output-neutral)

**Fix direction:** re-apply the hunk in a 3.0.x output-changing round. Budget (maintainer's measurement on the round-9 quick spice-offline set, harness to confirm at the gate): **93 units** whose result already carries `Simulation failed` gain 1–4 `simulate_subcircuits.run` diagnostics records — 65 gain 1, 21 gain 2, 3 gain 3, 4 gain 4 — a clean additive `diagnostics` class; `regression/compare_spice_offline.py` must be told to expect it (TH-077-style masking is NOT appropriate: the record is the deliverable).

### KH-476: `_KNOWN_FREQS` keys name one member of a multi-part datasheet, so the siblings fall to the 500 kHz topology default

**Severity:** LOW (`detect_power_regulators` reports `switching_frequency_hz` / `freq_source: topology_default` for the sibling parts; EMC rules and `cross_analysis` then size harmonic reach from 500 kHz instead of the datasheet 2.25 MHz / 1.5 MHz; no reference assertion involved)
**File:** `skills/kicad/scripts/kicad_core/parts.py:208` (`_KNOWN_FREQS`, read by `lookup_switching_freq` :327 — longest `startswith` prefix, so a key only covers the part numbers that begin with it)
**Discovered:** 2026-10-24, Checklist 11b (constants registry CONST-835, the three unverified entries) at product `a0df172`; the two TI entries were checked against the local datasheets

**Symptom:** the values are right but the keys are too narrow for their own datasheets:

- `'TPS62160': 2.25e6` — TI SLVSAM2E covers TPS62160/62161/62162/62163 at one nominal 2.25 MHz; corpus designs carry TPS62162 and TPS62163 (11 regulator findings) and every one is reported at 500 kHz `topology_default`.
- `'TPS63000': 1.5e6` — TI SLVS520C covers TPS63000/63001/63002 with one oscillator row (1250 min / 1500 max kHz); TPS63001/63002 (20 regulator findings) default to 500 kHz. The product's own `_REGULATOR_VREF` (parts.py:31) keys the same family as `'TPS6300'`, so the two tables disagree on who is in the family.

Together 31 findings whose part values appear on 37 units / 20 repos. A corpus scan of every `topology_default` switching regulator whose value begins with a table key minus its last one or two characters lists 259 findings on 222 units across 30 keys (TPS61023/TPS61235/TPS54202/TPS54331/TPS61391/TPS61170/TPS61090 lead); those are candidates only — most are different families with different frequencies (TPS6104x, TPS6120x, TPS54335) and need their own datasheet before any key is widened. The two above are the ones the datasheets settle.

**Expected:** key the table by the datasheet family where the family shares one frequency (`'TPS6216'`, `'TPS6300'`), as KH-237 did for the sub-family splits, and keep `_REGULATOR_VREF` and `_KNOWN_FREQS` on the same family keys. The 4-digit-suffix siblings (`TPS62160-Q1`, `TPS63001DRCR`) then resolve by the same prefix.

**Harness:** CONST-835 entries TPS62160 / TPS63000 verified with these notes; near-miss scan not kept (one-shot).

### KH-474: `lifecycle_audit.py` output carries no `diagnostics` key — the seventh JSON producer is outside the round-8 envelope rule

**Severity:** LOW (consistency: every analyzer envelope and the SPICE report gained `diagnostics: []`; a reader that keys on it sees `lifecycle_audit` as pre-v3)
**File:** `skills/kicad/scripts/lifecycle_audit.py` (no `diagnostics` anywhere in the file at `a0df172`; it is not one of the six `--schema` envelopes)
**Discovered:** 2026-10-24, v3 round-8 handoff §11

**Fix direction:** add `diagnostics: []` after its `compat`-equivalent block and route its guarded sites through `kicad_core.diagnostics.record`; additive, harness `--schema`/contract tests gain one key. Closes together with KH-464 (missing-input traceback) if the file is touched once.

### KH-473: RS-001 says "carries power_in pins" at deterministic confidence on a name-admitted rail whose only `power_in` pins are bootstrap pins

**Severity:** LOW (wording / confidence only; KH-454 removed the finding on NON-name-admitted bootstrap nets, so what remains is a rail like `+5V_USB_BOOT` or `19V_BST` that is admitted by its name but whose `power_in` pins are all BST/BOOT)
**File:** `skills/kicad/scripts/signal_detectors.py:4412` (`rs_load = "carries power_in pins"` chosen whenever the net has any `power_in` pin, bootstrap pins included; the name-only wording `is named like a power rail (no power_in pin on it)` + heuristic confidence is the honest one here)
**Discovered:** 2026-10-24, v3 round-8 handoff §11; corpus: 4 such RS-001 findings on 4 units (`realizator/stereopi-kicad-schematic` `+5V_USB_BOOT` ×2, `Wet-Lettuce-Robocup/robot_pcb` `19V_BST` ×2 — the pre-scan's 33 all-bootstrap findings minus the 29 KH-454 removals)

**Fix direction:** compute the load wording from the non-bootstrap `power_in` pins (the same filter `_power_rail` now applies), so a name-admitted rail with only bootstrap loads reads as name-only / heuristic. Gate budget: those 4 findings flip confidence + description (the v2.3.2 class-A shape).

### KH-471: `export_issues.py` keeps its own severity label vocabulary (`critical`/`high`/`medium` ranks, `_norm_severity` → `high`/`warning`/`info`) outside the round-8 `error`/`warning`/`info` unification

**Severity:** LOW (the exporter still accepts the new names on input, but its own labels differ from every analyzer's — `high` where the analyzers now say `error`)
**File:** `skills/kicad/scripts/export_issues.py:26-47` (`_SEVERITY_RANK` with `critical`/`high`/`medium`, `_norm_severity` returning `high`)
**Discovered:** 2026-10-24, v3 round-8 handoff §11 (B4 scope was datasheet_verify / cross_verify / summarize_findings)

**Fix direction:** rank and emit `error`/`warning`/`info`, accept the legacy names on input only (the B4 pattern). Corpus-neutral (the harness does not run the exporter); a product text-oracle artefact if one exists.

### KH-470: thermal findings carry both `title` and `summary` built from identical expressions — the twin that B2 removed from EMC

**Severity:** LOW (shape consistency; every other analyzer emits `summary` only after round 8)
**File:** `skills/kicad/scripts/analyze_thermal.py:534/547`, `:559/573`, `:585/…` (each TS-* finding sets `title` and `summary` from the same f-string)
**Discovered:** 2026-10-24, v3 round-8 handoff §11

**Fix direction:** drop `title` (readers already use `kicad_core.render.summary_or_title`); a budgeted class `thermal /findings/*/title removed` + the `top_issues` copies, same predicate shape as B2 (corpus: 16,083 thermal units). Harness: the `_thermal` contract tests that read `title` move to `summary`.

#### Addendum to KH-470 (thermal `title` + `summary` twin)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F8)
`analyze_thermal.format_text_report` (`:841,862-866,894`) still indexes `finding['title']`. A summary-only finding (as `make_finding` builds TJ-001, `lookup_detectors.py:351-370`) raises `KeyError: 'title'`. Dropping `title` here before KH-570 lands would break the thermal `--text` report on every unit with a finding. Order: KH-570 first.

### KH-469: `SWITCHING_EFFICIENCY` — the `buck` / `boost` / `buck-boost` keys never match, the schematic detector carries a different efficiency table, and `ic_with_internal_regulator` parts are costed as 85 %-efficient switchers

**Severity:** LOW (thermal `switching_reg` dissipation is `pdiss_confidence: heuristic` either way; the effect is that the thermal report and the schematic report disagree on the same regulator's dissipation, and the per-topology refinement the table promises never happens)
**File:** `skills/kicad/scripts/analyze_thermal.py:53` (`SWITCHING_EFFICIENCY`, read at `:281` via `SWITCHING_EFFICIENCY.get(topology, 0.85)` where `topology` is `detect_power_regulators`' `topology` field); `skills/kicad/scripts/signal_detectors.py:2223-2245` (inline `efficiency = 0.85 / 0.80 / 0.78` by `sub_topology`, unregistered literals); `:259-260` (the `("ldo", "linear", "")` skip list)
**Discovered:** 2026-10-23, Checklist 11b (constants registry CONST-393, critical-risk) at product `0490c49`

**Symptom:** `detect_power_regulators` emits `topology` only as `LDO`, `switching`,
`charge_pump`, `ic_with_internal_regulator` or `unknown` (corpus: 7,684 / 3,777 / 46 /
1,410 / 881 findings); the buck / boost / buck-boost distinction lives in
`power_dissipation.sub_topology`, which `analyze_thermal` never reads. So the thermal
table's `buck` 0.87 / `boost` 0.85 / `buck-boost` 0.83 entries are dead and every corpus
`switching_reg` dissipation uses the generic 85 % (432 occurrences, no other value).
Meanwhile the schematic detector costs the same regulator with its own inline table
(buck 0.85 / boost 0.80 / buck-boost 0.78; corpus 636 / 85 / 12 units) and a different
current estimate (output-capacitance proxy vs the thermal pass's `power_budget` rail
load): on the 45 corpus regulators that carry both numbers the thermal estimate is 0.1×
to 2.4× the schematic one. Two further riders: (a) `ic_with_internal_regulator` is not in
the thermal skip list, so 10 corpus "regulators" of that kind (MCU/SoC internal LDOs)
are given a switching-regulator dissipation at 85 %; `charge_pump` and `unknown` fall
through the same way when they have a vout and a rail load; (b) the `0.85` literal in the
`.get()` default duplicates the `switching` entry.

**Fix direction:** one shared efficiency table in `kicad_core` (shared-tables pattern,
as KH-467/468) with a cited basis per topology, read by both the schematic
`power_dissipation` block and `analyze_thermal`; thermal should consume the schematic's
`sub_topology` (or its `power_dissipation` block outright, as it already does for LDOs)
instead of recomputing; skip `charge_pump` / `ic_with_internal_regulator` / `unknown` with
a named `skipped` reason. Harness: the registry keeps the generic `switching` 85 %
verified as an engineering default (sources on CONST-393); the three dead keys stay
unverified until the tables are unified; gate budget at the fixing round = every
`switching_reg` thermal finding whose regulator has a non-buck `sub_topology` plus the 10
internal-regulator units.

### KH-468: `_ADC_RESOLUTION_MAP` — 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist

**Severity:** LOW (`detect_adc_circuits` reports `resolution_bits` from this table when no datasheet extraction is present; a wrong value mis-states the ADC in the report and feeds any LSB / noise-floor arithmetic downstream; no other detector reads it)
**File:** `skills/kicad/scripts/domain_detectors.py:3068` (`_ADC_RESOLUTION_MAP`, read by `_infer_adc_resolution` :3082 — first substring match of `value + lib_id`, so a prefix stands for the whole family it names)
**Discovered:** 2026-10-23, Checklist 11b (constants registry CONST-553, critical-risk) at product `0490c49`; every entry checked against the manufacturer datasheet or product page (local `datasheets/` PDFs where held)

**Symptom:** 14 prefixes hold for their whole family and are now verified in the registry
(`ads111` 16, `ads101` 12, `ads131` 24, `ads868` 16, `mcp320` 12, `mcp346` 16, `mcp356` 24,
`max1161` 12, `max1198` 8, `adc081` 8, `adc082` 8, `adc121` 12, `adc122` 12, `nau780` 24).
The other 15 fall into three classes:

- **Wrong value** — `mcp330` 10 (MCP3301/02/04 are 13-bit; the 10-bit parts are MCP300x,
  which no prefix covers), `mcp355` 24 (MCP3550/51/53 are 22-bit), `max1192` 10 (MAX1192
  is a dual 8-bit), `ad770` 14 (AD7705..AD7709 are 16-bit, ADI AN-607).
- **One prefix, several resolutions** — `ads126` 24 (ADS1260/61 24-bit, ADS1262/63
  32-bit), `mcp342` 18 (MCP3421..24 18-bit, MCP3425..28 16-bit), `ltc24` 24 (LTC2440/2485
  24-bit, LTC2450..2483 16-bit), `ltc23` 16 (LTC2308/09 12, LTC2314/2320 14, LTC2310 16,
  LTC2372 18, LTC2376/78 20), `ad760` 16 (AD7605/06 16, AD7607 14, AD7608/09 18), `ad799` 8
  (AD7991 12, AD7995 10, AD7999 8), `max1163` 12 (MAX11632..37 12-bit, MAX11638/39 8-bit).
- **No such part at the manufacturer** — `ads861` (no ADS861x on ti.com; the 16-bit
  ADS8860/8861 do not contain this substring), `mcp340`, `max1194`, `max1141`.

Corpus exposure (42,307 schematic outputs): `ltc23` matches 8 repos and is wrong for 6
of them (LTC2372-18, LTC2376-20 ×2, LTC2378-20, LTC2310-16, LTC2309); `ads126` 3 repos,
all ADS1262 (32-bit reported as 24); `mcp355` 2 repos (MCP3550, 22 reported as 24); `mcp342`
13 repos, MCP3426/3428 (16-bit) in 4; `ltc24` 4 repos, LTC2451 (16-bit) in 1; `ad799` 1 repo
(AD7991, 12 reported as 8). The four nonexistent prefixes match nothing. A rider: the
substring match also fires on passives whose `lib_id` embeds the board name
(`ADS1262…:C` capacitors) — harmless today because only ADC candidates reach the lookup.

**Fix direction:** key the table on full part-number stems long enough to be
resolution-unique (`ads1262`, `ads1261`, `mcp3421`..`mcp3428`, `ltc2440`, `ltc2309`,
`ltc2372`, `ad7606`, `ad7607`, `ad7991`, …), correct the four wrong values, drop the four
dead prefixes, and cite the datasheet per row (shared-table pattern, like KH-467). Where a
family genuinely splits (LTC23xx), return `None` rather than a guess. Harness: re-register
and verify under Checklist 11b after the fix; the corpus units above change
`resolution_bits` and are the gate budget.

### KH-467: three LED forward-voltage tables disagree per colour — `audit_led_circuits` and `validate_led_resistors` assume different Vf for the same LED

**Severity:** LOW (both detectors are heuristic when no datasheet extraction is present; the disagreement means the two rules can reach different current estimates for one LED, and none of the three tables cites a source)
**File:** `skills/kicad/scripts/domain_detectors.py:4815` (`_LED_VF`, nominal, read by `_estimate_led_vf` :4829 for `audit_led_circuits` :4848), `:4823` (`_LED_VF_FLOOR`, read at :5060); `skills/kicad/scripts/validation_detectors.py:1090` (`_LED_VF_BY_COLOR`, read by `_guess_led_color` :1099 and `validate_led_resistors` :1201)
**Discovered:** 2026-10-23, Checklist 11 (constants registry CONST-604 / CONST-605 / CONST-800, all unverified, critical-risk) at product `0490c49`

**Symptom:** the same colour maps to different forward voltages depending on which
rule evaluates the LED — nominal `_LED_VF` vs `_LED_VF_BY_COLOR`: red 2.0 vs 1.8,
yellow 2.0 vs 2.1, green 3.2 vs 2.2 (the floor table says 2.1), uv 3.5 vs 3.3;
`_LED_VF_BY_COLOR` carries `ir` (1.2) and the other two do not. Green is the
substantive one: 2.2 V is a GaP/AlGaInP green, 3.2 V an InGaN green, and the two
rules silently pick opposite technologies. Orange/amber agree.

**Measured 2026-10-23 (Checklist 11b, sources on CONST-604/605/800):** per-colour
typicals from the local LED datasheets (Würth 150060/150080 series, Kingbright APT2012,
Lite-On LTST-C170/C190/C191/C193, Vishay VLMO1300/VLMTG1500, Broadcom HSMW-C170, Cree
CLV1A-FKB, SunLED XZM2, OSRAM LY P47F) plus the Wikipedia LED material table:
red 1.95–2.1 (min 1.5–1.8), orange 2.0 (min 1.8), yellow 2.0–2.35 (min 1.95), amber 2.0,
blue 3.2–3.3 (min 2.5–2.8), white ~3.2 (min 2.7–2.9), UV 3.5–3.7 (min 3.1), IR 1.2–1.35.
**Green is genuinely bimodal:** GaP/AlInGaP green 2.0–2.2 V (LTST-C170GKT 2.1, VLMTG1500
2.0) vs InGaN green 3.2–3.3 V (150060GS 3.2, APT2012ZGCK 3.3, XZM2DG53W 3.2); the colour
word cannot pick one. So: `_LED_VF` 7/8 verified (green open); `_LED_VF_BY_COLOR` 6/9
(red 1.8 is the datasheet minimum, not the typical; green 2.2 is the other technology; UV
3.3 is below every sampled typical). **Floor rider:** `_LED_VF_FLOOR` red 1.85 / orange
2.0 / amber 2.0 / blue 3.0 / white 3.0 all sit ABOVE the sampled datasheet minimums, so
LA-004 can declare an LED dead on a rail it would light from (blue on 2.8 V); yellow /
green / UV floors verified. Corpus: 11,472 LEDs carry a colour hint (red 3,940, green
3,215, blue 1,311, ir 957, yellow 926, white 717, orange 223, amber 151, uv 32); 63,734
carry none and take the 2.0 V default in both detectors; LA-004 fired 5 times, all green.
For the unified table: nominal + minimum per colour as above, and for a bare "green" hint
either a 2.1/3.2 pair with the lower bound for LA-004 and the current estimate reported
as a range, or a technology keyword pass (`gap`, `ingan`, `pure green`, `true green`)
before falling back.

**Fix direction:** one shared table in `kicad_core` (the round-7 shared-tables
pattern) with a cited source per colour (manufacturer typical-Vf ranges, e.g.
Vishay / Kingbright / Würth colour tables), nominal + floor as two fields of one
entry; both detectors read it. Harness: register the table once and verify it under
Checklist 11b; the three current constants retire.

### KH-465: `cross_analysis.is_cross_analysis_ground_name` matches an exact name set only — `SGND`, `GNDPWR`, `GND_ISO`, `VSSA` and sheet-pathed `/Power/GND` are not ground to cross_analysis

**Severity:** LOW (pre-existing policy, named in round 7; the schematic side already classifies these as ground via `kicad_core.netnames.is_ground_name`, so cross-analysis plane-split / ground-domain checks disagree with the schematic on such designs)
**File:** `skills/kicad/scripts/cross_analysis.py:41` (`is_cross_analysis_ground_name`, formerly `_is_ground_net`; strips `/`, `-`, `_` then matches an exact set; the `GND_D` / `GND_A` entries are unreachable after stripping)
**Discovered:** 2026-10-23, v3 round-7 handoff §11; verified at `0490c49`: `{'GND': True, 'SGND': False, 'GNDPWR': False, 'GND_ISO': False, 'VSSA': False, '/Power/GND': False, '/GND': True, 'EARTH': True}`

**Fix direction:** delegate to `kicad_core.netnames.is_ground_name` (strip the sheet path first) plus the cross-analysis extras (EARTH, CHASSIS). Gate budget at the fixing round: cross_analysis findings on every board whose ground nets use the newly-recognised names — size with a corpus walk before the gate.

### KH-462: `datasheet_verify.py` exits 1 for warnings-only results — scripted gates cannot tell "warnings" from "errors"

**Severity:** LOW (exit-code convention; two rc 1 exits per review on extractions whose only issues are naming warnings)
**File:** `skills/datasheets/scripts/datasheet_verify.py:1066` — `return 0 if not issues else 1` in `_cli_v14` (issues includes `warning`-level violations)
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), meta §1 #34/#35

**Repro:** `datasheet_verify.py --mpn ESP32-S3-WROOM-1-N4 --extract-dir datasheets/extracted --self-consistency --json` → 4 `warning` violations (`power_domain '3V3' does not resolve to a key in base.recommended_operating`), 0 errors, rc 1. Same for `USBLC6-2SC6` (6 warnings).

**Fix direction:** 0 = clean or warnings-only, 1 = at least one `error`, 2 = usage/missing extraction; keep the JSON unchanged. No analyzer output moves (CLI only).

### KH-461: `design_analysis.cross_domain_signals[].needs_level_shifter` stays `true` for a regulator EN pin after KH-424 removed the VM-001 finding — the data block contradicts the findings list

**Severity:** LOW (no finding emitted; a JSON consumer reading `design_analysis` reaches the opposite conclusion from `findings`)
**File:** `skills/kicad/scripts/analyze_schematic.py:4101` (`"needs_level_shifter": needs_shifter` in the cross-domain pass) vs `validation_detectors.validate_voltage_levels` (VM-001, regulator-EN heuristic since KH-424 @ `fea561e`)
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), report §18.7 / meta §2 #8

**Repro:** SacMap `EN_5V` (3.3 V GPIO → TPS61023 EN, rated 7 V): VM-001 no longer fires (correct), `cross_domain_signals` still lists `EN_5V` with `needs_level_shifter: true` and no reason.

**Fix direction:** apply the same regulator-EN exemption in the cross-domain pass (or emit `needs_level_shifter: false` with `reason: "regulator_en_tolerant"`), so the data block and VM-001 agree. Gate budget: `design_analysis.cross_domain_signals` value flips on every board where VM-001 was suppressed by KH-424 (10,372 VM-001 provenance flips at the soak gate bound it).

### KH-460: EMC DC-002 "no decoupling cap near <IC>" fires on an ESD-protection array (USBLC6-2SC6) at `error` — the non-IC exemption keys on the value substring `esd`/`tvs`, and the finding duplicates the schematic UC-001 warning at a higher severity

**Severity:** LOW (one false `error` per board with a part-numbered ESD array on a connector VBUS net; the only `error` on a fab-ready board)
**File:** `skills/emc/scripts/emc_rules.py:632-639` — the "Skip known non-ICs" test `any(p in val for p in ('esd', 'tvs', 'test', 'tp', 'net_tie'))` runs on the component value; `USBLC6-2SC6`, `TPD2E*`, `PESD*`, `SP05*` contain neither token
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), report §18.1 / meta §2 #1 (unchanged since the 2026-10-05 run)

**Repro:** SacMap U4 `USBLC6-2SC6`, pin 5 on VBUS net `__unnamed_10` (J1.1, U4.5, F1.1 — no capacitor). DC-002 `error` components `["U4"]`, `nearby_caps`/`closest_cap_mm` null; schematic UC-001 `warning` "No decoupling capacitor on VBUS at J1" describes the same fact.

**Fix direction:** classify by role, not value text — the schematic analyzer already identifies ESD arrays (`esd_audit` / protection detector components, `ic_pin_analysis` function `esd_protection`); skip those refs in DC-002, or keep the check and emit at `warning` with `related_rule: UC-001`. Gate budget: DC-002 disappearances on boards with part-numbered ESD arrays (count at the filing round).

### KH-459: `audit_pwr_flags` only inspects `known_power_rails` — `power_in` pins on unnamed or locally named nets (connector VBUS, battery holder) are never audited, so `pwr_flag_warnings` is empty where KiCad ERC reports `power_pin_not_driven`

**Severity:** LOW (false negative in an advisory list that the skill advertises as the "PWR_FLAG audit"; ERC remains authoritative; likely frequent corpus-wide — connector-fed `power_in` pins on unnamed nets)
**File:** `skills/kicad/scripts/analyze_schematic.py:5137-5165` — `audit_pwr_flags(components, nets, known_power_rails)` iterates `sorted(known_power_rails)` only
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), meta §2 #17

**Repro:** SacMap: native ERC (KiCad 10.0.7) → 3 × `power_pin_not_driven` (`BT1.1`, `BT1.2`, `J1.1 VBUS`). Analyzer: `pwr_flag_warnings: []`. The three pins sit on `__unnamed_40` (BT1.1 + BT1.3, both `power_in`), `__unnamed_8` (BT1.2 `power_in` + Q4.3 passive) and `__unnamed_10` (J1.1 `power_in` + U4.5 + F1.1 passive) — none is in `known_power_rails` (`+3V3`, `+5V`, `+BATT`, `GND`, all of which carry PWR_FLAG and are correctly skipped).

**Fix direction:** iterate every net: `power_in` present, no `power_out`, no `has_pwr_flag` → warn (KiCad's rule is per pin, not per named rail); keep the entry shape. Gate budget: `pwr_flag_warnings` additions corpus-wide (the v2.1 KH-354 fix REMOVED 7,946 on 3,442 units; this adds a different population — measure before the fixing round).

### KH-458: `capability_mode.json` `datasheet_coverage_pct` is a hard-coded 0 — `_compute_coverage_pct` is still the Phase-4a stub

**Severity:** LOW (misleading sidecar field; `datasheet_extraction: "partial"` + 0 % on a project with 24 PDFs and extractions for every IC)
**File:** `skills/kicad/scripts/capability_mode.py:87-89` — `def _compute_coverage_pct(cache_dir=None) -> int: """Stub: 0 in 4a; refined in 4d-skeleton.""" return 0`; written at `:119`
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), meta §2 #23 (present since v1.4; never refined)

**Repro:** any run — the field is 0 regardless of `datasheets/extracted/` contents.

**Fix direction:** compute `extracted MPNs / BOM MPNs` from `datasheets/extracted/*.json` (and `datasheets/index.json` when present) against the schematic's MPN set, or drop the field with a `compat.deprecated_fields` entry. Sidecar-only change (`capability_mode.json` is outside the strict gate scope); `datasheet_extraction` should then be derived from the same count.

### KH-457: silkscreen revision check misses `rev2` / `v1.1`-style marks with no separator — `\b(?:REV|VER|VERSION)\b|(?<!\w)[RV]\d` needs a word boundary after REV or a lone R/V

**Severity:** LOW (false `missing_revision` documentation warning → `fab_release_gate` `[WARN] No revision marking found on silkscreen` on a board whose silk reads `sacmap-rev2 (2026)`)
**File:** `skills/kicad/scripts/analyze_pcb.py:3531-3541` (`rev_pattern`; consumed by `fab_release_gate.py:144-152` `revision_marking`)
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), report §18.6 / meta §2 #3

**Repro:** silk text `sacmap-rev2 (2026)`, empty title-block `rev`: `REV\b` fails (V is followed by `2`), `(?<!\w)[RV]\d` fails (`V` is preceded by `E`) → `has_revision False`.

**Fix direction:** `(?<![A-Z])(?:REV|VER|VERSION|R|V)\s*[-_.]?\s*\d` (case-insensitive) plus the existing word forms; keep the title-block `rev` precedence. Gate budget: `documentation_warnings` `missing_revision` disappearances corpus-wide (count at the filing round).

### KH-456: `fab_release_gate` component-count check counts every PCB footprint, including `G***` logo/graphic footprints — false FAIL "schematic 52 vs PCB 56"

**Severity:** LOW (a FAIL verdict on a release gate for a correct board; any board with logo footprints or other non-BOM graphics trips it)
**File:** `skills/kicad/scripts/fab_release_gate.py:173-205` — `pcb_fp = pcb_stats.get("footprint_count", len(pcb.get("footprints", [])))` vs `sch_placeable = total_components - dnp_parts`; no exclusion of graphic footprints
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), report §18.5 / meta §2 #3

**Repro:** SacMap `pcb.json` has 56 footprints, four of which are `reference "G***"`, `footprint "LOGO"`; the schematic has 52 placeable parts. `check_pin_nets`-style comparisons (and the PCB analyzer's own footprint summaries) treat `G***` as graphics. Gate: `[FAIL] Component count mismatch: schematic 52 vs PCB 56 (diff 4, 8%)`.

**Fix direction:** exclude footprints that are graphics (reference matching `^G\*+$|^G\d*$` with no schematic counterpart, `attr` board-only / `exclude_from_bom`, or a `footprint_count_placeable` stat the PCB analyzer emits) before comparing; report the excluded count in `details`. Gate budget: `fab_release_gate` is not in the corpus profile — no gate movement.

### KH-449: `analyze_pcb.py --full` exceeds the 600 s full-chain cap on `azonenberg/starshipraider` MAXWELL `maxwell-main.kicad_pcb` (both sides)

**Severity:** LOW (correct output in the standard profile, which completes without `--full`; the `--full` run is a performance cliff of the KH-422 kind, not a defect — but it is the only full-chain-profile timeout in 3,015 pcb units and sizes the profile's cap)
**File:** `skills/kicad/scripts/pcb/` (`--full` trace-segment analyses: `routing.py` / `geometry.py` hot paths — not profiled; KH-422's `_point_in_polygon` cost is the first suspect)
**Discovered:** 2026-10-16, v3 round-5 full-chain gate (`results/v3_round5_gate_fc/`, run `f6784ec3`): `timeout after 600s` on BOTH `6a91aaa` and `d55c851` (600.181 s / 600.187 s), so a baseline debt, not a round delta; ledgered in `reference/baseline_debts/6a91aaa.json` `timeout_units` with `profile: full-chain` and `accepted_by: null` (maintainer to accept per ruling Q3). The board was not in the H0 seed-23 full-chain sample, so the profile's first corpus-scale run surfaced it. A standalone `--full --only-deterministic` run of the `6a91aaa` product on an otherwise idle box completes in **619.9 s** with 1.8 GB peak RSS and a 235 MB output (`results/v3_round5_gate_aux/debt_measure/maxwell_memrun.json`), so the unit sits just past the 600 s cap: a marginal cliff, not a hang.

**Fix direction:** profile a `--full` run of the board; if it is `_point_in_polygon`
again, KH-422's spatial-index fix covers it. Until then the unit stays a
both-sided debt under the full-chain profile; a fix turns it into a compared
pair, i.e. a round delta the fixing round must budget.

### KH-448: `analyze_schematic.py` in hierarchy mode peaks at ~3 GB RSS on `BerkeleyLab/Marble` (25 sheets, 1,041 components) — a 32-way corpus run exceeds 62 GB

**Severity:** LOW (correct output, byte-identical across 6a91aaa and 9465206; a resource footprint, not a defect — but it sizes every hierarchy-profile corpus run)
**File:** `skills/kicad/scripts/analyze_schematic.py` → `schematic/` package at 9465206 (hot spot not profiled; every sub-sheet unit redirects to the 25-sheet root and re-parses the whole project)
**Discovered:** 2026-10-16, v3 round-4 hierarchy-profile gate (`results/v3_round4_gate_aux/hier_attempt1_jobs32/`): 32 workers on Marble sub-sheets held ~2.2 GB RSS each (in flight) and the box sat at 60 of 62 GB; measured in isolation with `resource.getrusage(RUSAGE_CHILDREN)`:

| tree | unit | peak RSS | wall |
|---|---|---|---|
| 6a91aaa | `design/PMOD.kicad_sch` (redirect → `Marble.kicad_sch`) | 3,077 MB | 10.3 s |
| 9465206 | same | 3,050 MB | 11.1 s |

Outputs byte-identical; 1,041 components / 1,380 nets / 539 findings. Pre-existing
(both sides equal), so not a round-4 regression. The standard profile is unaffected
(`--no-hierarchy` never takes the redirect).

**Fix direction:** profile the hierarchy build on Marble (sheet-instance expansion is
the suspect, as in KH-447); cache the root parse across sub-sheet redirects, or stream
sheets instead of holding every parsed sheet plus the merged net map at once.
Harness side the gate runs the hierarchy profile at 10 jobs until this moves (TH-071).

### KH-447: `analyze_schematic.py` exceeds the 120 s cap on two hierarchical root sheets (was three; LT3514 resolved 2026-10-24) (standard profile, `--no-hierarchy`)

**Severity:** MEDIUM (the only standard-profile timeouts in 149,629 baseline units; the sheets are small)
**File:** `skills/kicad/scripts/analyze_schematic.py` (hot path not yet profiled — sheet-instance expansion / net classification are the candidates; `cristobalcuevas/Kicad` LT3514 is the smallest repro)
**Discovered:** 2026-10-15, v3 baseline at `6a91aaa` (both sides time out identically; ledgered in `reference/baseline_debts/6a91aaa.json` `timeout_units`; filed at the round-2 reply per the maintainer's ruling Q3 — gate debt is not triage)

**Symptom:** three root sheets time out at 120.1–121.6 s on both slots of the
A/A and of every gate since:

| unit | symbols | sheet instances | wires | bytes |
|---|---|---|---|---|
| `AlexColello/discrete-nes` `boards/ram/ram.kicad_sch` | 69 | 20 | 239 | 158,905 |
| `AlexColello/discrete-nes` `boards/ram/row_group.kicad_sch` | 48 | 8 | 81 | 207,655 |
| `cristobalcuevas/Kicad` `LT3514/LT3514.kicad_sch` | 0 | 5 | 7 | 17,477 |

A 17 KB root with zero symbols and five sub-sheets exceeding 120 s rules out
detector cost; the sheet-instance / sub-sheet path is the suspect. Downstream
emc/thermal/cross units are `dependency_missing` skips (9 in the baseline census).

**Fix direction:** profile LT3514 first (`--no-hierarchy` is already on in the
standard profile, so the hierarchy builder is not the whole story). A fixed unit
stops being `both_failed` and becomes a compared pair — a round delta under
ruling Q3 — so the fix belongs in an output-changing round with these three
units named in its budget.

**Addendum 2026-10-16 (round-5 full-chain gate):** the cap hides a memory
blow-up, not just a slow path. Under the full-chain profile's 600 s cap both
sides of LT3514 were SIGKILLed (exit -9) at ~403 / ~420 s with 32 workers
running — the host OOM killer, not the harness. A standalone run of the
`6a91aaa` product under a 20 GB address-space rlimit dies with `MemoryError`
at 76.6 s with 19.5 GB resident, in `parse_all_sheets` at the
`lbl["name"] = lbl["_hier_ns"] + "/" + lbl["name"]` line (hierarchical-label
namespace expansion grows without bound on this five-sub-sheet root); RSS
climbs ~150–250 MB/s from the start (2.0 GB at 20 s). So every standard-profile
gate already runs each of these three units up to ~20–30 GB before the 120 s
cap fires, and any profile with a longer cap OOMs the box at 32 jobs
(TH-071). Severity stays MEDIUM but the fix is now a correctness/safety item:
bound the namespace expansion. Evidence `results/v3_round5_gate_aux/debt_measure/`.

**Addendum 2026-10-24 (v3 round 9b, `2498831..07b7fb1`): LT3514 RESOLVED; the two
discrete-nes roots stay open.** The LT3514 root sheet lists ITSELF as a sub-sheet, so the
memory blow-up in the 2026-10-16 addendum was unbounded self-recursion in `parse_all_sheets`,
not a slow path. `c6f4807`'s recursion guard skips the recursive instance with one
`diagnostics` record (`schematic.hierarchy.parse_all_sheets`, `ValueError: sheet file
LT3514.kicad_sch includes its own ancestor LT3514.kicad_sch`, effect `recursive sheet
skipped`): direct run under `ulimit -v 8000000`, `--no-hierarchy`, `PYTHONHASHSEED=0` →
`2498831` MemoryError rc 1 at ~44 s; `07b7fb1` rc 0 in 0.09 s, 25 components, 28 findings
(`tools/tests/test_schematic_input_guards.py::test_self_referencing_sheet_terminates_with_one_diagnostic`
+ `test_mutual_recursion_terminates_with_one_diagnostic`). In the 9b standard gate the unit is
a `WARN baseline failed; not comparable` (not `both_failed`), and its three downstream
emc / thermal / cross units stay `dependency_missing` (Phase B needs both schematic sides OK)
— these four are the LT3514 half of the gate's declared movements. The ledger
`crash_units` / `timeout_units` entries for LT3514 retire at the `07b7fb1` re-baseline; the
unit becomes a compared pair from the next round on and gains corpus assertions at the next
relock. `AlexColello/discrete-nes` `ram` / `row_group` are acyclic deep fan-out
(16 × 8 × 16 sheet instances) and still exit 124 at 120 s on both sides (the maintainer's
`round9b-units/` measurement + the 9b gate) — the remaining item; severity stays as filed.


### KH-445: `EQ-042` tags two different equations (duplicate equation id)

**Severity:** LOW (documentation/traceability; no analyzer behaviour change)
**File:** `skills/emc/scripts/emc_rules.py` (~l.3060: `# EQ-042: DC bias derating lookup + ferrite µ thermal degradation`), `skills/emc/scripts/emc_formulas.py` (~l.936: `# EQ-042: R_trace = rho * L / (W * T) — DC trace resistance`)
**Discovered:** 2026-10-15, H0 plan 4 (recursive equation scan + coverage baseline)

**Symptom:** the `EQ-NNN` tag is the equation identity for the harness equation
registry (`validate/audit_equations.py`) and the scan-coverage baseline
(`reference/scan_coverage_baseline.json`, `eq_ids` keyed by id). Two unrelated
formulas carry `EQ-042`, so the registry has carried a duplicate entry pair since
2026-04 and the baseline's id→file map can hold only one of them — a lost or
moved second site would be invisible to `source_scan.py check`.

**Fix direction:** re-id one of the two (next free `EQ-` number) in a v3 round;
the harness relocates its registry entry via `audit_equations.py scan`
(relocation-vs-stale is now distinguished) and the baseline is re-accepted.

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

#### Addendum to KH-329 (`plan_extraction.py` "not implemented" error lacks next-command pointer)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/05-v3-docs/findings/VERIFICATION.md` do/R3-F4)
The code side looks resolved at `07b7fb1`: `plan_extraction.py:167-174` returns 2 without `--use-cached-scout`, and the message at `:168-171` names the recovery (run scout, write `<mpn>.scout.json`, re-invoke with the flag). The docs still lead users into that exit:
- `skills/datasheets/SKILL.md:74` and `references/extraction-pipeline.md:10-12` order plan → scout;
- `dispatch-claude-code.md:21` substitutes `<plan.mpn>` before any plan exists.

Fix: the report's three doc replacements (scout first, then plan with `--use-cached-scout`). Output-neutral. Close KH-329 with this doc fix if the harness confirms the message.

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

#### Addendum to KH-331 (`jsonschema` + `referencing` deps undeclared in datasheets skill)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F11; also `docs/audit/04-v3-security/findings/VERIFICATION.md` se/R1-F9)
A third undeclared dependency: `skills/datasheets/scripts/validate_sanity_vector.py:17` imports `yaml` unconditionally at module level (used at `:149`), against datasheets SKILL.md:74's stdlib-only promise, so even `--help` fails without PyYAML. QA helper only (referenced by `dispatcher-contract.md:76-78`), not on an analyzer path. Fix: lazy import, or JSON vectors. Output-neutral.

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

### KH-443: Net ties are not bridged by the DC-continuity audits — RS-001 false "no declared source" when a rail is fed through a `NetTie_2`; PP-001 / power tracing have the same blind spot (GitHub #50)

**Severity:** MEDIUM (false RS-001 WARNING on a rail that is sourced; corpus:
213 `.kicad_sch` files / 136 repos place `Device:NetTie_*`, 565 `.kicad_pcb`
files carry `net_tie_pad_groups`)
**File:** `skills/kicad/scripts/signal_detectors.py` — `audit_rail_sources`
(RS-001/002, bridges `solder_jumpers` with `default_state == "bridged"` only),
`audit_power_pin_dc_paths` (PP-001 `_bridges_dc`: inductor / ferrite / fuse /
≤1 Ω resistor / bridged jumper — no `net_tie`); any other consumer that walks
DC continuity (power_budget rail attribution, regulator output→rail mapping)
**Discovered:** 2026-10-14, GitHub #50 (bson): "Net ties aren't understood…
can be treated as 0R resistor arrays… but of course there is no BOM part"
**Reported by:** bson (GitHub #50)

**Repro (verified 2026-10-14 at main `0684046`, kicad-cli 10.0.6 oracle):**
`repos/Envious-Data/EnvOpenPico/RP2040/EnvPicoLiPo/EnvPicoLiPo.kicad_sch` —
U1 BQ24072RGT pin 10 `OUT` (`power_out`) sits on `Net-(C2-Pad2)` (analyzer
`__unnamed_8`); NT1 `Device:NetTie_2` pin 1 is on that net, pin 2 on `VDD`,
which carries U2 `Vin` (`power_in`), C3, R4. kicad-cli keeps the two nets
distinct (correct — a net tie IS two nets in KiCad) and the analyzer's net
membership matches the oracle exactly. But `audit_rail_sources` emits
**RS-001 "VDD has no declared source"** (description: "…no bridged solder
jumper path to a sourced net") although the rail is sourced one net-tie hop
away. The same audit would have accepted a bridged `SolderJumper` in NT1's
place. Pattern example (no RS-001 fires there today — the rails carry
`#PWR` symbols): `greatscottgadgets/hackrf/hardware/hackrf-one` NT2 ties
`REG_OUT1`↔`VCC` and NT1 `REG_OUT2`↔`+1V8`, so U21 TPS62410's outputs reach
their rails only through ties; regulator→rail attribution (power_budget,
DC-001 output-cap checks) cannot cross them either.
Counter-evidence checked: `piotr-binkowski/kintex-pcie-board` NT6/NT3 tie
`MGTAVCC`/`+1V8` to U8 `FB3`/`FB1` (feedback sense) — the PP-001 fires there
are NOT tie-caused (U8 VOUT3 is on `MGTAVCC` directly).

**What already works (so #50's "not identified" is only half right):**
`kicad_utils` classifies `NT*` refs / `NetTie` lib_ids / values as
`type: "net_tie"`; `in_bom no` is honoured, so NTs never enter
`missing_mpn`, SS-001 or `bom_coverage`; SP-001 excludes them; the
datasheet-sync scripts and `lifecycle_audit` skip them; `analyze_pcb`
exports `net_tie_pad_groups` per footprint.

**Minor rider:** `simulation_readiness.components_without_model` lists
every NT (868-antenna: NT1..NT4; EnvPicoLiPo: NT1) — a net tie needs no
SPICE model; exempt `net_tie` (and arguably `jumper`) in that filter at
`analyze_schematic.py` ≈ l.6040.

**Fix direction:** treat `type == "net_tie"` as an always-bridged jumper in
`audit_rail_sources` and `_bridges_dc` (one predicate shared by both — the
PR #44 fuse-bridge change is the template), keep net membership untouched
(KiCad ground truth), and record the hop in the RS finding the way
`source_path: "bridged_jumper"` does (`"net_tie"`). Gate budget: RS-001
disappearances + RS-00x info "sourced via net tie" appearances on the ≈136
NetTie repos; PP-001 disappearances where the only rail path crosses a tie;
`components_without_model` shrinks by the NT count. Not for the PCB side:
`net_tie_pad_groups` already lets copper join the two nets; no analyzer rule
flags that join today.

#### Addendum to KH-443 (net ties not bridged)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F11)
RS-003 traversal has the same scope question. The comment at `skills/kicad/scripts/signal_detectors.py:4311-4312` and SKILL.md say it crosses a "bridged jumper / ferrite", but `:4244` iterates only `bridge_facts.jumpers`. Ruling needed together with this item: should RS-003 (and the bridge set generally) traverse ferrites, fuses and 0 Ω parts, or jumpers only? Then align the code or the comment.

### KH-442: SPICE behavioral opamp model (DigiKey/cache-sourced GBW) yields gain_linear 0.0 / −520 dB in the inverting testbench — false SP-WARN wherever a part number resolves to a behavioral model

**Severity:** MEDIUM (297 corpus simulations warn with a simulated gain of
exactly 0.0; e.g. Bergi84/GrowOMatic sim2 U1 TLV9001IDCK: expected gain −2.0,
simulated −520.83 dB at BOTH v2.3.0 and v2.3.1 — the behavioral model, not the
analyzer version, is the variable)
**File:** `skills/spice/scripts/simulate_subcircuits.py` (opamp behavioral
model / inverting testbench), `spice_spec_fetcher.py` (api:digikey →
behavioral GBW), `spice_model_cache.py`
**Discovered:** 2026-10-06, v2.3.1 corpus regen (`results/v231_regen/
adjudication_v231_regen.md`, SPICE fracture class)

**Symptom:** when the part number resolves (cache or live API) to a behavioral
model (`model_note: "<MPN> behavioral (api:digikey|cache:<MPN>, GBW=…)"`) the
inverting/non-inverting gain testbench measures ~0 output; the same circuit
with the ideal fallback model passes. Corpus: 1,166 boards carry behavioral
opamp models; 2,924 warn vs 1,878 pass; 297 warn with gain_linear == 0.0.

**Fix direction:** fix the behavioral opamp subcircuit's port/bias wiring in
the testbench (likely supply rails or the output node of the GBW-limited
model); add a contract test that the TLV9001 behavioral model reproduces the
ideal −2.0 gain within tolerance.

**Gate budget (when fixed):** SP-WARN → pass on behavioral-model opamp sims
(up to 2,924 sims); `summary.pass` locks rise.

#### Addendum to KH-442 (SPICE behavioral opamp model yields gain 0 / false SP-WARN)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F6, sk/R2-N1)
Root cause 1 (`skills/spice/scripts/spice_templates.py:446`, `:590`): the inverting bench grounds the reference input (`Rpos_bias {pos_net} 0 0.001`) and the stimulus is `VAC … DC 0`, so with VEE=0 the DC target is 0 V and the non-RRO clamp `Vswl vee_int vee DC {swing}` (`spice_model_generator.py:95`) pins the output. LM358 inverting −10 single supply: OP `v(out)=1.392 V`, gain −34.86 dB vs +20 dB → warn; RRO MCP6002 −2: −17.38 dB → warn; the same bench with no context (±5 V) passes at 20.00 dB — the "ideal passes, behavioral warns" pattern. Root cause 2 (`spice_templates.py:744-755`, `:773-776`): `_infer_voltage` is anchored `[+]?(\d…)V…`, so `-5V`, `-12V`, `VEE`, `-VCC`, `V-` return None; `_infer_opamp_rails` then sets `vee_v = 0`, and the CLI always passes context (`simulate_subcircuits.py:202`), so every dual-supply op-amp with a recognised MPN is simulated single-supply (LM358 on +5V/−5V nets → −34.86 dB warn). Fix: bias reference and stimulus at mid-rail (or an AC-only unclamped linear model) and parse a leading `-`/`−` and `VEE`/`VSS-` names; land with KH-610. Budget unchanged (up to 2,924 SP-WARN → pass). The exact −520 dB TLV9001 bench needs its saved `.cir` from the harness. Cross-bundle: `signal_detectors._parse_voltage_from_net_name` (`:3757`) may share the negative-rail blind spot (unverified).

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

#### Addendum to KH-428 (`has_pull_up` true for a pull-down)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F5)
New location and consequence, same code: `skills/kicad/scripts/schematic/system_analyses.py:1588-1617` (`analyze_power_sequencing`). Any non-power-symbol neighbour on EN, including a lone pull-up resistor to VIN, sets `en_source="controlled"`. The sleep pass (`:572-576`, `:614-633`) then zeroes Iq, dividers and resistor-to-GND for that rail in the realistic estimate, so a rail tied permanently on is treated as disableable. Fix together with the polarity fix (classify passive pulls as not-controlled). Budget: `realistic_total_uA` on affected battery units.

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

**Rider (2026-10-22, soak run 9):** the manifest's `outputs` also never lists `drc.json`, `erc.json`, `parasitics.json` or `fab_release_gate.json` written into the run folder, and `LC-007` "Lifecycle audit not run — --lifecycle flag not passed" remains in `schematic.json` after the standalone `lifecycle_audit.py` wrote `<run>/lifecycle.json`. Same fix family: register side outputs; drop LC-007 when `lifecycle.json` exists for the current run.

### KH-432: power_budget counts an RGB LED as a flat 5 mA (cathode resistors R3/R4/R5 ignored, ~48 mA real) and ignores the USB VBUS load behind the PTC — thermal then skips U2 as `below_min_pdiss`

**Severity:** MEDIUM (KH-375 rider: multi-die LEDs and PTC-fed loads are under-counted, so a regulator that really dissipates is skipped by thermal)
**File:** `skills/kicad/scripts/analyze_schematic.py` (power_budget LED load model, KH-375 series-resistor branch; VBUS/PTC path)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap RGB LED with three cathode resistors is budgeted at 5 mA total instead of ≈48 mA (three channels × (3.3 − Vf)/R); the VBUS consumer behind the PTC is not attributed to the rail; thermal `skipped_components` lists U2 `below_min_pdiss`.

**Fix direction:** model multi-pin LEDs per channel through each cathode/anode resistor; treat a PTC (fuse-typed, KH-414 F-ref rules) as a pass-through for load attribution; fixture = RGB LED + 3 resistors + PTC-fed consumer.

**Gate budget (when fixed):** `power_budget.rails[*].estimated_load_mA` up on RGB-LED / PTC boards, thermal T3-class downstream (TS-00x/TP-001), `skipped_components` shrink.

**Rider (2026-10-22, soak run 9):** `cross_analysis.py:686-699` TW-001 builds its current map from `detect_power_regulators` findings' `estimated_iout_A` only and skips with "no power regulator current estimates in schematic analysis" while `power_budget.rails[*].regulator` / `estimated_load_mA` exist for both rails — the two scripts disagree about what counts as an estimate. When the budget is fixed, TW-001 should fall back to `power_budget` rail loads.

#### Addendum to KH-432 (power_budget RGB LED / PTC; TW-001 rider)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F1)
The rider's TW-001 skip has a second cause besides the budget disagreement. `cross_analysis.py:705` reads a top-level `estimated_iout_A`, while `signal_detectors.py:2188-2192` nests it under `power_dissipation` (117 of 505 corpus regulator findings carry the nested key, 0 the top-level one). Over 331 corpus sch+pcb pairs TW-001 never ran. Fixed by KH-566; the `power_budget` fallback here is still needed for regulators without an estimate.

### KH-433: datasheet staleness: `datasheet_lookup._resolve_pdf_path` uses `source.local_path`, stored by the extraction as an ABSOLUTE original-project path — any copied project reads its extractions as stale (irreproducible trust toggles between runs)

**Severity:** MEDIUM (this is why the VM-001 repro differed between the reviewer's and the controller's run: trusted vs stale depended on whose copy of the project ran)
**File:** `skills/datasheets/scripts/datasheet_lookup.py` (`_resolve_pdf_path`), extraction writers (`source.local_path`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** copy a project with `datasheets/extracted/` elsewhere → every extraction resolves its PDF through the old absolute path, fails the staleness check, and the analyzers drop to heuristic trust.

**Fix direction:** store `local_path` relative to the project root (or to the extraction file) and resolve relative to the current project; keep a fallback to the absolute path for old extractions; a determinism-style test that copies a fixture project and asserts identical trust.

**Gate budget (when fixed):** none in the corpus (no extractions); on extraction-bearing projects, trust flips heuristic → datasheet after copy.

#### Addendum to KH-433 (absolute `source.local_path` staleness)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F1, kc/R7-F8)
This now blocks KH-554, the lookup-detector trust policy. Gating AM / OV / TJ / EX / FT / PM on `is_stale` before this item is fixed would switch trust on and off between copies of the same project. Fix this first.

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

**Rider (2026-10-22, soak run 9):** `FD-001` has the same blind spot — "No fiducials on B.Cu (2 SMD components)" counts the two 15 mm touch pads as the B.Cu SMD components. Whatever CP-003 uses to classify a `TestPoint` symbol as a touch pad should feed `test_coverage` AND the fiducial check.

### KH-437: `trust_summary.provenance_coverage_pct` 0.0 / `trust_level: low` on pcb / emc / thermal / lifecycle while every finding is `deterministic` (Aug B13, still open)

**Severity:** LOW-MEDIUM (trust rollup contradicts the findings it summarises; consumers keyed on `trust_level` down-rank deterministic output)
**File:** `skills/kicad/scripts/finding_schema.py` / per-analyzer `trust_summary` builders (pcb, emc, thermal, lifecycle)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** on the soak board all four non-schematic analyzers report `provenance_coverage_pct 0.0` and `trust_level low` although their findings carry `confidence: deterministic` with evidence sources.

**Fix direction:** compute provenance coverage from the findings' `evidence_source`/`provenance` the same way the schematic analyzer does; one shared helper.

**Gate budget (when fixed):** `trust_summary` values move on every pcb/emc/thermal unit (facts-only, no finding movement) — large additive-style class; pre-scan locks on `trust_level`/`provenance_coverage_pct`.

#### Addendum to KH-437 (provenance 0 % / trust `low` on all-deterministic outputs)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` R13 Empirical row "KH-437 all-deterministic low trust")
At `07b7fb1` the helper gives `trust_level: high` with `provenance_coverage_pct 0.0` for all-deterministic findings. The 0 % half reproduces; the `low` half does not. Update the symptom and narrow the budget to `provenance_coverage_pct`.

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

#### Addendum to KH-439 (sleep audit realism)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F4)
`skills/kicad/scripts/schematic/system_analyses.py:604-607` (`analyze_sleep_current`): every `led_indicator` gets `realistic_uA = 0.0` ("LEDs are typically GPIO-controlled"), so a hardwired power LED vanishes from `realistic_total_uA` and its observation. It still counts in `always_on_uA` / `total_estimated_sleep_uA` (`:647-655`). Fix with item (1): zero only LEDs driven from a GPIO / switched net. No consumer outside the module.

### KH-440: docs: native DRC/ERC on a project copy without lib tables emits `lib_footprint` / `lib_symbol` warnings — skill should say so

**Severity:** LOW (documentation; the kicad skill's DRC/ERC step surprises users on copied projects)
**File:** `skills/kicad/SKILL.md` (DRC/ERC section)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** running `kicad-cli pcb drc` / `sch erc` on a copied project without `fp-lib-table` / `sym-lib-table` yields library-resolution warnings unrelated to the design.

**Fix direction:** one doc note: copy the lib tables (or run from the original location) and how to recognise/ignore the lib_* class.

**Gate budget (when fixed):** none.

## Test Harness Issues

### TH-078: the gate has no "debt resolved" disposition — a ledgered crash/timeout unit that the candidate fixes fails `skips_ok`, the findings `strict_clean` and the strict comparator, so a structural round with a resolved debt can never `gate_pass` mechanically

**Severity:** LOW (adjudication cost + a hand-written exception in the round's response builder; no wrong verdict was issued)
**File:** `regression/run_corpus_gate.py` (`diff_envelopes` → `WARN baseline failed; not comparable` counts against `strict_clean`; `build_phase_b_jobs` emits `dependency_missing` for a schematic that succeeded on the candidate only, and `skip_covering` covers a `dependency_missing` only through a `both_failed` upstream; `compute_gate_pass` has no resolved-debt bucket), `tools/baseline_ledger_check.py` (`new_crash` treats a changed exit code as new debt — right under ruling Q3, but the KH-446 units then have no place to go but `unledgered`), `regression/compare_snap_trees.py` / `field_compare.py` (a unit present on one side only → `status: missing_a`, verdict `error`, `strict_field_clean = False`, even with 0 deltas on 149,629 compared pairs)
**Discovered:** 2026-10-24, v3 round-9b gate `2498831..07b7fb1` (`results/v3_round9b_gate/`): LT3514 (KH-447, ledgered timeout + full-chain crash) went from a baseline timeout to a 0.17 s result → 1 `WARN`, 3 unledgered `dependency_missing` downstream, strict `missing_a`; the two KH-446 units changed exit code 1 → 2 → 2 unledgered `both_failed`. All five were the handoff's DECLARED movements, yet `gate_pass.pass = false` on both profiles and the verdict had to be adjudicated by hand (`results/v3_round9b_gate_aux/build_response.py` encodes the expected set).

**Expected:** a `--ledger`-aware disposition: when a ledgered `timeout_units` / `crash_units` identity fails on the baseline and succeeds on the candidate, the gate reports it under `gate_pass.resolved_debts` (with its downstream `dependency_missing` units and the strict `missing_a` entry), keeps it out of `unledgered_skips` / `WARN`, and lists it in the rollup so the adjudication quotes it; a both-sided crash whose exit code changed should likewise land in a `shape_changed_debts` list rather than `unledgered`. The structural criterion then reads `… AND unledgered == 0 AND strict_field_clean(compared pairs)`, with resolved and shape-changed debts carried into the next ledger automatically (`baseline_ledger.py build --carry-accepted-from` already copies stamps). Until then: RUNBOOK 26i names the pattern and the hand adjudication.

### TH-071: `run_corpus_gate.py --jobs` is not memory-aware — the hierarchy profile at 32 jobs drives the box into OOM on multi-GB units

**Severity:** LOW (operator hazard; the run was killed and re-run at 10 jobs with an identical verdict, but nothing in the tool stops the next operator from repeating it)
**File:** `regression/run_corpus_gate.py` (`--jobs`, default `os.cpu_count()`), `harnesslib/profiles.py` (profile declares a timeout, not a memory envelope)
**Discovered:** 2026-10-16, v3 round-4 hierarchy-profile gate attempt 1 (`results/v3_round4_gate_aux/hier_attempt1_jobs32/`): 32 analyzer subprocesses on `BerkeleyLab/Marble` sub-sheets (KH-448, ~2.2–3 GB RSS each) → 60 of 62 GB used, kernel OOM killer active on the host; the attempt was stopped at 3,691 / 9,848 units and re-run at `--jobs 10` (`results/v3_round4_gate_hier/`, 9,848 PASS).

**Symptom:** the gate's only throttle is the job count; a profile that redirects
sub-sheet units to a large root multiplies the per-unit footprint by the worker
count with no cap. The standard profile (`--no-hierarchy`) never shows it.

**Fix direction:** give `Profile` a `max_rss_mb` hint and let the gate derive a
default job cap from `MemAvailable` / hint (override with an explicit `--jobs`);
record peak RSS per unit in `units.jsonl` (`resource.getrusage` after each
subprocess) so the budget can be measured rather than guessed. RUNBOOK gate
preflight now says: hierarchy profile ≤ 10 jobs on a 62 GB box.

**Addendum 2026-10-16 (round-5):** the full-chain profile at 32 jobs reproduced
it: `cristobalcuevas/Kicad` LT3514 (KH-447) is a memory blow-up (~20 GB at
77 s, still climbing) that the standard profile's 120 s cap truncates and the
600 s cap lets run into the host OOM killer — both gate sides died with
SIGKILL at ~400 s and the user's concurrent work was exposed. A per-profile
`max_rss_mb` hint is not enough on its own; the gate also needs a per-unit
RSS ceiling (rlimit on the child, recorded as a `crash`/`oom` status) so one
runaway unit cannot take the host down regardless of the job count. RUNBOOK
preflight now lists the full-chain profile with the hierarchy profile.

### TH-062: 58 print-and-return vacuous skip paths in required-tier smoke files bypass the known-skips allowlist

**Severity:** LOW (tests pass vacuously when the analyzer is not importable or a
fixture is missing; no current failure, but a product-layout move such as the v3
arc would silently turn them into no-ops)
**Files:** `tests/test_synthetic.py` (11), `tests/test_b1_b2_finding_id_invariants.py`
(10), `tests/test_b4_b7_layer2_schemas.py` (15), `tests/test_b3_b8_layer2_behavior.py`
(16), `tests/test_top_level_sheets.py` (4), `tests/test_b9_review_metrics.py` (2)
**Discovered:** 2026-10-14, H0 plan 1 final review. The paths are gated on
"analyzer not importable" or "fixture missing" and print then return, so pytest
records a pass and the known-skips allowlist never sees them.

**Fix direction:** convert each to `pytest.skip` with a reason (then each must be
allowlisted or fixed) before the H0-7 CI pin checkpoint.

### TH-061: `tests/test_datasheet_db_cli.py` plants and deletes a file under `HARNESS_DIR/repos/.test_fallback/` — a write into the corpus checkout tree

**Severity:** LOW (corpus inputs must be immutable; the fixture cleans up after
itself, but a crash between plant and delete leaves a stray dir in `repos/`)
**File:** `tests/test_datasheet_db_cli.py` (~lines 481-527, the `.test_fallback`
fixture)
**Discovered:** 2026-10-14, H0 plan 1 Task 4 corpus-marker audit.

**Fix direction:** point the fallback fixture at `tmp_path` and monkeypatch the
CLI's repos root, so no test writes into `repos/`.

### TH-060: `test_kh393_power_rails_threaded` premise is stale — "P1_VBUS is not classified power by name heuristics" no longer holds

**Severity:** LOW (one explicit strict xfail; the `--power-rails` override half
of the test still holds)
**File:** `tests/test_kh392_kh393_gp001_power.py::test_kh393_power_rails_threaded`
**Discovered:** 2026-10-14, H0 plan 1 (honest collection). The first assertion
became false when PR #44 (2026-09-13) broadened `is_power_net_name`. Never
noticed because the file had no `__main__` block (TH-052 phantom pass). Now
`xfail(strict=True)` citing this issue (commit a81858a).

**Fix direction:** split the test: keep the override assertions; pick a fixture
net the heuristics do not match for the negative half; then drop the xfail.

### TH-063: mutating runner launched against the live tree from a TDD RED step — 16,909 `results/outputs/emc` files rewritten

**Severity:** LOW (no measurable impact; the standing rule below is the point)
**File:** `tests/test_run_chained_execution.py` (plan 2 Task 6 RED step), `run/run_emc.py`,
`run/run_thermal.py`
**Discovered:** 2026-10-14, H0 plan 2 Task 6

**Symptom:** on 2026-10-14 23:56:39-23:57:39 local, the Task 6 RED step spawned
the then-ungated `run/run_emc.py` (and `run_thermal.py`) with no selector from a
subprocess test. That started an unqualified full-corpus EMC run for about 60 s:
16,909 EMC outputs rewritten (thermal 0).

**Impact:** none measurable. The EMC analyzer is identical between 0684046 and
6a91aaa, run ids are sidecar-sourced and unchanged (e.g.
20261005T071505Z-7e06ee), and `run_checks` afterwards passed 259/259 on an
affected repo and 34,645/34,645 on the smoke cross-section. No quarantine
needed; `elapsed_s` drift only.

**Root cause:** the test spawned the real runner with the inherited environment,
and the `--all` gate did not yet exist in that runner.

**Fix direction / standing rule:** every subprocess test that spawns a mutating
runner sets `KICAD_HAPPY_TESTHARNESS_DATA_DIR=<tmp_path>` (`utils.py` redirects
`OUTPUTS_DIR` at import) and asserts the data dir stays empty. Done for the
emc/thermal/spice/gate tests in plan 2. Remaining risk: any future test, or any
runner not yet gated. Closes when the corpus-marker/hermeticity audit also checks
for that env on runner subprocesses (H1 item).

**Addendum 2026-10-15:** mechanism identified — the RED step's 60 s subprocess timeout killed the parent runner; its 32 pool workers survived (ppid 1) and completed the whole emc corpus unsupervised, then idled ~6 h. Tracked as TH-067.

### TH-070: scan-coverage baseline keys anonymous constants by `function:line` and by file, so every structural round reports false losses

**Severity:** MEDIUM (the required offline_contract test `test_scan_coverage_not_lost` goes RED against every product round until `--accept-baseline`; a CI checkpoint pin can therefore only be cut from a re-baseline commit)
**File:** `tools/source_scan.py` (`coverage_snapshot` constant identity `file|scope|name:line`; `coverage_diff` compares identities verbatim), `tests/test_scan_coverage_gate.py`; same identity in the registry → TH-065
**Discovered:** 2026-10-15, v3 round-2 reply (maintainer measured 156 `lost_constants` + `lost_eq: EQ-065` against `8912a5a`; reproduced, report `results/v3_round2_gate_aux/scan_check_8912a5a.txt`)

**Symptom:** all 156 "lost" constants are either anonymous constants in
untouched functions whose line shifted under round-1 deletions
(`analyze_schematic`, `signal_detectors`, `validation_detectors`, `emc_rules`)
or constants whose file moved (`kicad_utils.py` → `kicad_core/*.py`,
`diff_analysis.py` → `diff_engine.py`). Nothing was lost; EQ-065 is the one
true removal (dead `apply_rotation`, deleted in round 1). The review artifact of
every structural round is therefore ~150 lines of noise around one real line.

**Fix direction (maintainer suggestion, adopted):** key anonymous constants by
`(file, scope qualname, ordinal-within-scope, value)` with the line kept as
location metadata; apply the round's relocation map (file moves) to constant and
EQ identities before diffing, as `api_migration.py apply-map` does for symbols.
Until then each accepted round ends with `source_scan.py check --accept-baseline`
and the diff is attached to the round response (`accept_baseline_diff`).

### TH-068: fixture-lane A/A cannot strict-verify chained envelopes after the basetemp tree is moved

**Severity:** LOW (the corpus lanes prove the chained analyzers strict-clean at scale; only the offline fixture lane is affected)
**File:** `tools/aa_run.py` (`snapify`, `--fixture-trees`), RUNBOOK/plan-6 Task 7 Step 4 recipe
**Discovered:** 2026-10-15, H0 plan 6 Task 7 Step 4

**Symptom:** emc / thermal / cross_analysis envelopes embed ABSOLUTE upstream paths
(`inputs.source_hashes` keys, `upstream_artifacts[].path`) under the pytest basetemp.
The recipe runs the contract suite twice at the same basetemp and moves the tree aside
between runs, so verify-then-mask (`sha256_of` / `strip_root_prefix_keys`) cannot read
the upstream file → "linked file missing", 36 violations / 18 source_hashes deltas on the
9 chained units; the 12 non-chained units are identical.

**Fix direction:** `snapify` re-roots chained upstream references into the snapified
tree (or the recipe keeps both basetemps in place and passes them as root prefixes), so
the fixture lane covers all six analyzers in strict mode.

### TH-067: batch-runner pool workers outlive a killed parent and keep running the corpus

**Severity:** MEDIUM (unsupervised corpus writes; the actual mechanism behind TH-063's 16,909-file rewrite)
**File:** `run/run_emc.py` (`ProcessPoolExecutor` at ~l.200; same pattern in `run_thermal.py`, `run_spice.py`, `utils.run_analyzer`)
**Discovered:** 2026-10-15 05:50 local — 32 `run_emc.py` worker processes found with ppid 1, state S, age 21,216 s (started 2026-10-14 23:57 = the TH-063 RED step), environment `PYTEST_CURRENT_TEST=tests/test_run_chained_execution.py::test_unqualified_runs_exit_2_without_all`, no `KICAD_HAPPY_TESTHARNESS_DATA_DIR`

**Symptom:** the TDD RED run launched the then-ungated `run_emc.py` under
`subprocess.run(..., timeout=60)`. The timeout SIGKILLed the parent, but the
32 forked pool workers were never signalled: they drained the already-submitted
work queue against the LIVE tree (every emc unit — the TH-063 rewrite), then sat
idle as orphans for ~6 h until killed by hand. Any killed batch run (Ctrl-C to a
wrapper, a gate timeout, an OOM kill of the parent) can do the same.

**Fix direction:** make workers die with the parent — a pool `initializer` that
sets `PR_SET_PDEATHSIG` via `ctypes` on Linux (stdlib only) and/or a cheap
`os.getppid() == 1` check at the top of each unit task; run every batch runner in
its own process group and have `harness.py`/gate wrappers kill the group; add a
test that kills a runner parent mid-run and asserts no worker survives.

### TH-064: emc/thermal/spice runners have no identity-based `--resume`

**Severity:** LOW (the flag is refused, so nothing runs on stale identity)
**File:** `run/run_emc.py`, `run/run_thermal.py`, `run/run_spice.py`, `harness.py`
**Discovered:** 2026-10-15, H0 plan 2 final review

**Symptom:** these three runners kept the old existence-based `--resume`
(`should_skip_resume`), which reuses any output regardless of product SHA or args.
Plan 2 gave only `utils.run_analyzer` (schematic/pcb/gerber) identity resume.

**Interim fix:** each runner now exits 2 on `--resume` with "identity-based resume
is not implemented for this runner yet (TH-064); rerun without --resume";
`harness.py run` no longer passes `--resume` to spice/emc.

**Fix direction:** reuse the `run_analyzer` pattern: batch manifest + `units.jsonl`
(records stamped with `run_id`), archive the old log on non-resume runs, and
`unit_is_current(..., run_id=<matched manifest run_id>)`. Closes when `--resume`
works on all three and the refusal tests are replaced by reuse/rerun tests.

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

_35 open KH-* + 16 open TH-* issues (2026-10-14: TH-052/053/058 FIXED (H0 plan 1), +TH-060/061/062 filed. Earlier: 2026-10-06: v2.3.1 shipped @ 0684046 and the corpus regen ran CLEAN. Closed this cycle, all in FIXED.md: KH-408..415, KH-418/420 (v2.3.1 batch + follow-up), KH-419/424/425 (SacMap soak fixes), TH-054 (run_emc crash masking). Open KH: 328..334 datasheets-infra backlog; 355/364/365 audit remainder; 403/404 HIGH connectivity over-unions; 416/417 v2.3.1 riders; 421 Marble hash-seed nondeterminism; 422 `--full` point-in-polygon cost; 423 legacy `.sch` empty fields; 426..440 SacMap soak long tail; 441 via_in_pad attribution; 442 behavioral opamp gain 0. Open TH: 037..042/044/047 legacy; 049 contamination tripwire; 055 timeout-class v1.3-era pcb outputs (191 boards); 056 KH-313 anchor; 057 bugfix generator merge-by-id; 059 batch SPICE hermeticity; 060 kh393 power-rails test premise stale (strict xfail); 061 test_datasheet_db_cli writes repos/.test_fallback; 062 print-and-return vacuous skips in smoke files. Earlier history: 19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
