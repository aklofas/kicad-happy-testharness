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

Last updated: 2026-10-29

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-779** (KH-751..777 filed 2026-10-29 (+ KH-778 filed by the harness for the KH-575 KO-001 bounding-box residue) from the product 3.0.x Wave 4 Part B handoff — C14 board contact-model umbrella KH-751 (pad-to-fill misses, 11/296 false-incomplete boards; home of KH-701/702/710 (a)(b)(c)(i)), inferred stackup absent from output and EMC, PM-002 edge-mount keywords, ergogen nested modules / locked reference, IO-001 DNP / net identity / unclassified VBUS, schematic PDN DNP caps, PDN plane-area and grid residue, low-frequency PDN wording, EF rail-tap direction, legacy non-copper rule layers, legacy project rules reported, `.kicad_dru` expressions, custom-rule / annulus edge cases, per-side malformed courtyards, footprint parse edge cases, inferred-stackup edge cases, repeated stackup layer, small-patch return-path reference, KH-750 residue KH-771, SK-001 footprint text / rotated pads, `courtyard_clearance` for PM-001, `net_tie_pad_groups`, PD-003 dead key, board-setup annular width, TV-001 `drill_penalized`; KH-427 and 750 FIXED in 3.0.x Wave 4 Part B (unreleased, candidate `40b8ff3`), KH-364 track-in-zone half and KH-710 (d) fixed (entries stay open), KH-417 return-path half closed by construction (addendum on the FIXED entry), see FIXED.md; KH-711..749 filed 2026-10-28 from the product 3.0.x Wave 4 Part A handoff — case-insensitive mandatory fields, PCB rail set from board nets, op-amp bench below the feedback pole (gates KH-507), PNP bench never on (MEDIUM), P-ch `vth_V`, SPICE presence passes (KH-618 remainder, MEDIUM), `is_power_net_name` signal suffixes stop divider chains (MEDIUM), family Vref table values (MEDIUM), rail-sign readers (KH-675 remainder), CAN split termination (MEDIUM), VM-001 PG exemption unconditional, label-like regulator values, field-trim residue (KH-708 residue), reference nodes as rails, pre-KiCad 7 PCB rule / EG-001, `/x/PGND`, `ctx.rail_by_net` phase order, config-override consistency, regulator/half-bridge misdetections, DO-DET provenance, Vref rows awaiting datasheets, diff-pair ESD / USB-name / SPI-CAN / I2C VOL / family nickname / ERC / RC / LED / COMP / domain-advisory residues, alternate SPICE backends, op-amp `supply_min`, Monte Carlo parallel arms, bench-input residue, Vref key core cut, crystal residue, follow-up umbrella KH-749; KH-750 filed 2026-10-28 by the harness at the Wave 4 Part A gate — `/fpga-pg5/VCCINT` classed `interrupt` once KH-678 drops its rail match (KH-678 census); KH-675 (partly, → KH-719), 678, 699, 705, 708 (residue → KH-723), 672, 442, 676, 611, 612, 618 (partly, → KH-716), 619, 539, 669 FIXED in 3.0.x Wave 4 Part A (unreleased, candidate `b31d4ff`) and KH-709 closed as answered by ruling entry 54, see FIXED.md (commit-message corrections recorded under KH-675 / 678 / 676, the KH-509 CHANGELOG slip under KH-669); addenda on KH-548 / 667 / 483 / 707; KH-701..710 filed 2026-10-27 from the product 3.0.x Wave 3b Part B handoff §Asks 4 — net propagation onto net-less copper, custom-pad residue, instance-aware property writers, JLCPCB CPL convention reference, analyzer sheet-file case / KiCad 6 value settle, bom_manager diagnostics, unit-count semantics, mandatory-field whitespace trim, KiCad 5 `~` ruling question, follow-up umbrella; KH-417 / KH-426 FIXED in 3.0.x Wave 3b Part B (unreleased), see FIXED.md; KH-700 reclassified (R33 / R34: (a) budgeted class, (b) conformant, (c) → KH-708); addenda on KH-574 / 364 / 483; KH-699 / KH-700 filed 2026-10-27 by the harness at the Wave 3b Part A gate — `D_Zener` from an `*LED*` nickname typed `led` (false LR-001), `~` empty-field placeholder kept as a BOM footprint/datasheet on legacy schematics (MEDIUM); KH-679..698 filed 2026-10-27 from the product 3.0.x Wave 3b Part A handoff §Asks 4 — sibling-sheet driver ties, bus member fallbacks, hierarchical-label ERC, ktiger hierarchy join, PU-001 `MISO`, DO-DET port-name exemption, wired NC pins, bus group/quoted/mixed parsing, `~` pin names, bus-member naming, brace decode table, multi-root projects, unresolved text variables, CG-AUD by name, sheet-pin shape preference, follow-up umbrella KH-695; addenda on KH-483 / 667 / 669 / 671 / 677; KH-403 / KH-404 FIXED in 3.0.x Wave 3b Part A (unreleased) and KH-664 closed as conformant, see FIXED.md; KH-662 completion addendum in FIXED.md; KH-678 filed 2026-10-26 at the Wave 3 verdict — sheet net promoted to power by a same-named rail elsewhere (`/HVIL/HVIL_N`), Wave 4 group 1; KH-663..674 filed 2026-10-26 from the product 3.0.x Wave 3 handoff §Asks 4 — legacy buses, `E` decimal mark, EMC BE-001 origin distance, footprint Edge.Cuts outline, VM-001 heuristics, CS-DET set order, root hierarchical label fusion, LR-001 resistor association, same-net pad overlap, follow-up umbrella; KH-675..677 filed 2026-10-26 by the harness at the Wave 3 gate — negative regulator estimates on positive-named rails (Wave 4 group 1), SPICE zero-step transistor sweep (the spice-offline candidate failure), six legacy boards worse against their KiCad-5 netlist; KH-510..519, 560, 575, 576 FIXED in 3.0.x Wave 3 (unreleased) and KH-662 / 668 / 670 assigned FIXED-direct, see FIXED.md; KH-574 / KH-364 narrowed; KH-404 re-verified (reproduces); KH-653..661 filed 2026-10-25 from the product 3.0.x Wave 2 handoff §Asks 4 — `PH0`/`PH1` read as a regulator SW pin (MEDIUM), `RF-C10` typed resistor, EG-001 / GR-005 / CC-001+TW-001 follow-ups, `ThermalSkipped.reason` description, dead `has_esd` line, cross_verify keep/retire, LOW; KH-655 assigned FIXED-direct (test-plan / op-amp 2-hop / what_if order, fixed on discovery); KH-563..570, 582, 584, 591, 509, 607, 421 FIXED in 3.0.x Wave 2 (unreleased), see FIXED.md; KH-620 / 581 / 579 narrowed to their non-order halves; addenda on KH-484 and KH-529; KH-647..652 filed 2026-10-25 from the product 3.0.x Wave 1 residue — DNS rebinding (MEDIUM), NAT64/6to4 `is_global` bypass (MEDIUM), browser-fallback deadline/buffering/WebSocket gaps, `provider_mouser` unbounded `product_url` fetch, SPICE model denylist, `datasheet_extract_cache` fixed temp names / unchecked manifest joins, LOW; KH-497..505 FIXED in 3.0.x Wave 1 (unreleased), see FIXED.md, KH-507 left open by that round; KH-646 filed 2026-10-25 — split from KH-626 at the 3.0.x Wave 0 handoff: `distributor_offline` evicts only the selected tree's provider modules (sk/R6-F4), LOW; KH-626 FIXED on `v3.0.x-dev` `b3e4954` except that finding, see FIXED.md; KH-645 filed 2026-10-25 by the harness audit fix session — netlist oracle m68k-hbc splits 16 `/Bus/PEP/AD*` nets (oracle 4/5 since at least `0490c49`), MEDIUM; KH-644 filed 2026-10-25 by the harness audit fix session — PCB zone `fill_ratio` sums every filled layer over one layer's outline (1.83 on a two-layer zone), LOW, surfaced when the assertion engine stopped truncating fractional values; KH-643 filed 2026-10-25 by the main-repo agent — EMC SW-001 ignores `--standard` and discards its harmonic amplitude, MEDIUM; KH-497..642 filed 2026-10-25 from the external audit round 1 at `07b7fb1` — 30 static reviews in five bundles, every finding re-verified against the code, one entry per fix group; records and the wave plan in the main repo at `docs/audit/FIX-PLAN.md` and `docs/audit/0*/findings/VERIFICATION.md`; addenda added to KH-329, KH-331, KH-428, KH-432, KH-433, KH-437, KH-439, KH-442, KH-443, KH-470, KH-481, KH-482, KH-484, KH-487, KH-494; KH-480..496 filed 2026-10-24 from the v3 round-9b handoff §7 — the review-period bug-hunt deferrals, every claim re-verified in source at `07b7fb1` (19 confirmed / 4 partly), each with its budget or oracle re-freeze: failed-SPICE-run diagnostics (93 units), missing-sheet / truncated-input diagnostics, unannotated duplicate-ref collapse (1,598 units / 466 repos), GR-002 extents-only (MEDIUM), root-only `inputs` (4,261 multi-sheet units), suppressions only in EMC/thermal, `--parasitics` verbatim names, Mouser `""` key (4 frozen runs), SPICE cache hygiene, EMC `--severity` vocabulary, analysis_cache M3/M4, DigiKey 429, Action diff-base, three review-minor umbrellas; KH-479 assigned FIXED-direct 2026-10-24 to the review-period Critical A-C1 (analysis-dir containment, new in v3, fixed before release — see FIXED.md); KH-477 / KH-478 / KH-446 FIXED in round 9b (`cd2e49b` / `c6f4807`), KH-447 resolved for LT3514, see FIXED.md; KH-478 filed 2026-10-24 from the v3 round-9 handoff §11 — `emc_spice.run_distributed_pdn_spice` measurement tuples in the wrong shape → always `(False, None)`, temp dir never removed, no product caller, LOW; KH-472 / KH-464 / KH-466 / KH-475 FIXED in v3 round 9 (`ec81ca6`), see FIXED.md; KH-477 filed 2026-10-24 while fixing TH-077 — the SPICE model cache falls back to one global `/tmp` directory because `analyze_schematic.py` strips `file`; non-atomic manifest, cross-project leakage, LOW; KH-476 filed 2026-10-24 during the Checklist 11 `_KNOWN_FREQS` verification — the TPS62160 / TPS63000 keys miss the siblings of their own datasheets, 31 regulator findings default to 500 kHz, LOW; KH-470..475 filed 2026-10-23 from the v3 round-8 handoff §11 — thermal `title`+`summary` twin, `export_issues` severity vocabulary, `emc_spice.py` unquoted redirect without `cwd` (KH-463 sibling), RS-001 "carries power_in pins" wording on a name-admitted bootstrap-only rail, `lifecycle_audit` without `diagnostics`, Monte-Carlo per-trial fallback stderr noise; all pre-existing at `a0df172`, LOW; KH-454 / KH-455 / KH-463 FIXED in round 8 (`6222468`, `c598140`), see FIXED.md; KH-469 filed 2026-10-23 during the Checklist 11 SWITCHING_EFFICIENCY verification — three of the four `analyze_thermal.SWITCHING_EFFICIENCY` keys are unreachable and the schematic detector carries a third, different efficiency table; `ic_with_internal_regulator` regulators are costed as 85 %-efficient switchers, LOW; KH-468 filed 2026-10-23 during the Checklist 11 ADC-map verification — `_ADC_RESOLUTION_MAP` 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist, LOW; KH-467 filed 2026-10-23 during the Checklist 11 backlog pass — three divergent LED forward-voltage tables (`_LED_VF` / `_LED_VF_FLOOR` in domain_detectors, `_LED_VF_BY_COLOR` in validation_detectors) disagree per colour, LOW; KH-464..466 filed 2026-10-23 from the v3 round-7 handoff §11 — lifecycle_audit missing-input traceback, `is_cross_analysis_ground_name` exact-set policy (SGND/GNDPWR/GND_ISO/VSSA/`/Power/GND` not ground), `analyze_gerbers` exit 0 on a nonexistent dir; all pre-existing, verified at 0490c49, LOW; KH-463 filed 2026-10-23 at the v2.3.2 corpus regen — SPICE testbench `.control` `echo … > <path>` redirect unquoted, every measurement silently skips when the workdir path has whitespace or `,`/`&`/`'`/non-ASCII, the user-facing `analysis/<run>/spice_work/` default inherits the project path, MEDIUM; KH-456..462 filed 2026-10-22 from the SacMap rev2 run-9 soak at the v2.3.2 pre-tag `4701c26` — fab_release_gate counts `G***` logo footprints (false FAIL), silk revision regex misses `rev2`, `capability_mode` `datasheet_coverage_pct` is a hard-coded stub, `audit_pwr_flags` ignores `power_in` pins off named rails (ERC `power_pin_not_driven` ×3 unseen), EMC DC-002 fires on a part-numbered ESD array (dupes UC-001), `cross_domain_signals.needs_level_shifter` stale after KH-424, `datasheet_verify` rc 1 for warnings; riders on KH-431/432/436; all code-verified by the main-repo agent; KH-455 filed 2026-10-22 at the v2.3.2 backport gate — PP-001 `(ref, pin_number)` dedup masks a second symbol's power pin on unannotated `U?` designs, the gate's one residue unit, LOW; KH-454 filed 2026-10-22 at the v2.3.2 backport adoption — RS-001 fires on a bootstrap-only net whose sole `power_in` pin is the BST/BOOT pin, LOW, with the two GitHub #55 riders; KH-450..453 assigned 2026-10-22 FIXED-direct — GitHub #52–#55 / PRs #56–#59 by EldarPolitkin on `main` @ 4701c26, see FIXED.md; KH-449 filed 2026-10-16 at the v3 round-5 full-chain gate — pcb `--full` exceeds the 600 s cap on starshipraider MAXWELL both sides, LOW; KH-447 addendum: LT3514 is a ≥ 20 GB memory blow-up, OOM-killed under the 600 s cap; KH-448 filed 2026-10-16 at the v3 round-4 gate — hierarchy-mode `analyze_schematic.py` ~3 GB RSS on BerkeleyLab/Marble, both sides equal, LOW; KH-446/447 filed 2026-10-15 at the v3 round-2 reply per ruling Q3 — empty-input pcb traceback (hackclub/OnBoard placeholders), schematic 120 s timeouts on three hierarchical roots (discrete-nes ×2, LT3514); KH-445 filed 2026-10-15 at H0 plan 4 — `EQ-042` tags two different equations, LOW; KH-444 assigned 2026-10-14 FIXED-direct — PR #51 AM-001 `<domain>_max` key lookup, imrcly, see FIXED.md; KH-443 filed 2026-10-14 from GitHub #50 — net ties not bridged by RS-001/PP-001 DC-continuity audits, MEDIUM; KH-442 filed 2026-10-06 at the v2.3.1 regen — behavioral opamp model gain 0 false SP-WARN; KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
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
KHPA finding ID). Next TH number: **TH-100** (TH-099 filed 2026-10-29 at the 3.0.x relock — emc / thermal pair a schematic with an orphan pre-hash pcb output; TH-098 filed and fixed 2026-10-26 — tool-gated skips (pdftotext / ngspice) failed the required-tier skip guard on runners without the tools; listed in `tests/known_skips.json`, see FIXED.md; TH-097 filed and fixed 2026-10-26 — `run_spice.py` checked for ngspice before validating the selection, product CI red at pin `bd551df5b41`, see FIXED.md; TH-096 filed 2026-10-26 at the Wave 3 gate — the field comparator holds every delta in memory, ~55 M deltas exhausted the box, MEDIUM; TH-095 filed and fixed 2026-10-26 — `run_netlist_oracle.py` did not resolve a relative `--kicad-happy`, see FIXED.md; TH-093 and TH-094 filed and fixed 2026-10-25 at the wave 10 final review — bare-list assertion files crash the coverage and health report counters; `audit_equations.py untagged` indicator order follows PYTHONHASHSEED, both LOW, see FIXED.md; TH-091 filed and fixed 2026-10-25 during wave 10 planning — `generate_analytics.py` ignores `KICAD_HAPPY_TESTHARNESS_DATA_DIR`, see FIXED.md; TH-092 filed and fixed 2026-10-25 during wave 10 planning — `audit_equations.py` reads sources as UTF-8 text and `find_untagged` swallows `SyntaxError`, see FIXED.md; TH-090 filed and fixed 2026-10-25 during wave 10 planning — `refresh_findings.py` counted drift's no-checkable-items sentinel as an item and reported such findings as current, see FIXED.md; TH-089 filed and fixed 2026-10-25 by the harness audit fix session — `generate_catalog.py` counted the `capability_mode.json` sidecar as a schematic/PCB/EMC/SPICE output, see FIXED.md; TH-080..088 filed 2026-10-25 from the harness external audit round 1 — budgeted-kind worker exceptions, ledgered-timeout coverage, `discover.py --repo` global-manifest shrink, silent assertion-file drop, null/`[]` required-field locks (all HIGH, gate/assertion false-pass paths), constants corpus-hit names, `audit_equations --diff` no-op, `validate_design_intent` multi-repo scope, `analyze_bom_mismatch` layout (LOW); records `docs/audit/0*-harness-*/findings/VERIFICATION.md`, plan `docs/audit/HARNESS-FIX-PLAN.md`; TH-079 filed 2026-10-25 from the external audit round 1 — `generate_validation_md.py` category table and total use different denominators (1,855 = the aspirational count), LOW; TH-078 filed 2026-10-24 at the v3 round-9b gate — no "debt resolved" disposition: a ledgered unit the candidate fixes fails `skips_ok`, `strict_clean` and the strict comparator (`missing_a`), so the structural criterion cannot pass mechanically and the response builder carries a hand-written exception, LOW; TH-065, TH-066 + TH-077 FIXED 2026-10-24, see FIXED.md; TH-077 filed 2026-10-24 at the v3 round-8 spice-offline gate — `run_spice.py` output is not deterministic run-to-run: `simulation_results[*].model_note` flips `lookup:<MPN>` ↔ `cache:<MPN>` for the same product and inputs (132 of 8,829 reports between two baseline passes), LOW; TH-076 fixed-on-discovery 2026-10-23 during the Checklist 11 backlog pass — `audit_constants.py scan` dropped and re-added every constant whose file moved without a `relocate --map` (rounds 2/3), losing 41 verification records incl. `_REGULATOR_VREF` 55/114 and `_CAP_ESL` 7/7; the registry had also not been rescanned since round 5, see FIXED.md; TH-075 fixed-on-discovery 2026-10-23 at the v2.3.2 corpus regen — `run_spice.py` per-unit `--workdir` carried raw repo/file names into ngspice, 18,464 sims silently skipped on 5,198 corpus units, directory name now sanitized + digest, see FIXED.md; TH-074 fixed-on-discovery 2026-10-22 at the v2.3.2 backport gate — long-run waiters stalled on a `pgrep -f` self-match and on a zombie PID; `tools/wait_for_run.py` + RUNBOOK 26k + full-chain `done.json` marker, see FIXED.md; TH-073 fixed-on-discovery 2026-10-17 at the v3 round-6 gate preflight — `run_corpus_gate.py` accepted analyzer-less profiles (`spice-offline`, the new `distributor-offline`) and would have run a zero-unit gate, guard added, see FIXED.md; TH-072 fixed-on-discovery 2026-10-16 at the v3 round-5 gate preflight — `full-chain` profile declared no schematic analyzer, Phase B ran no chained unit, see FIXED.md; TH-071 filed 2026-10-16 at the v3 round-4 gate — `run_corpus_gate.py --jobs` not memory-aware, hierarchy profile at 32 jobs OOMs the box, LOW; TH-070 filed 2026-10-15 at the v3 round-2 reply — scan-coverage identity by line/file yields ~150 false losses per structural round, MEDIUM; TH-069 FIXED 2026-10-15 at the v3 round-3 reply — discover.py regular-file filter + manifest regen, see FIXED.md; TH-068 filed 2026-10-15 at H0 plan 6 — fixture-lane A/A chained envelopes unverifiable after the basetemp move, LOW; TH-067 filed 2026-10-15 — batch-runner pool workers outlive a killed parent (the TH-063 mechanism), MEDIUM; TH-066 filed 2026-10-15 at the H0 plan 4 final review — audit tools walk 58 of the 90 scanner files; TH-065 filed 2026-10-15 at H0 plan 4 — audit_constants function-scope `name:line` identity churns the registry; TH-064 filed 2026-10-15 — emc/thermal/spice `--resume` refused until identity-based resume exists; TH-063 filed 2026-10-14 — mutating runner launched against the live tree from a TDD RED step, 16,909 emc outputs rewritten, no measurable impact; TH-055 and TH-059 (harness half) fixed 2026-10-15 (H0 plan 2), see FIXED.md; TH-062 filed 2026-10-14 — 58 print-and-return vacuous skip paths in required-tier smoke files; TH-061 filed 2026-10-14 — test_datasheet_db_cli.py fallback fixture writes under repos/; TH-060 filed 2026-10-14 — test_kh393_power_rails_threaded premise stale since PR #44, now strict xfail; TH-052/053/058 fixed 2026-10-14 (H0 plan 1, honest pytest collection), see FIXED.md; TH-059 filed 2026-10-06 at the v2.3.1 regen — batch SPICE side effects: spice/ dirs in repos/ + live DigiKey lookups; TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 FIXED 2026-10-15 at H0 plan 5 — generator rewritten as grouped reconciliation, see FIXED.md; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 311 open issues (291 KH + 20 TH).

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

### KH-653: `PH0` / `PH1` GPIO pins read as a regulator SW pin, so STM32s become `ic_with_internal_regulator` / switching regulator records

**Severity:** MEDIUM (false regulator records with inductor, rail, RS-001 / DO-DET / PS-001 and downstream EMC / thermal / cross consequences on common MCUs)
**File:** `skills/kicad/scripts/signal_detectors.py:1618` (`pn_base = pname.rstrip("0123456789").rstrip("_")`), `:1627` (`pn_parts & {"SW", "PH", "LX"}`), `:1839` (same token list)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 (`004bba5`, handoff §Asks 4a); verified in source at `004bba5`

**Symptom:** stripping trailing digits turns the GPIO pins `PH0` / `PH1` (STM32 port H, usually the HSE oscillator pins) into `PH`, a TI SW-pin alias, so the MCU is taken for a switching regulator and the inductor search runs over its oscillator nets. Examples at the Wave 2 gate: cansat / Cubesat-EPS U4 (STM32F405, rail `3.3V_STM`), BerkeleyLab/Marble U54 (STM32F207, KH-421), bluerobotics ping-dev-kit U301 (STM32H563), formulaslug U1 (STM32WB55). Wave 2 made the pick deterministic (KH-509); the misread itself stays: most of the 51 H1 schematic units / 39 repos at the gate are these records.

**Fix direction / budget:** match `PH` only as the exact pin name (or `PH` + non-port suffix), never after digit stripping; or require the part to be a regulator family before the SW-pin aliases count. Budget: PR-DET / DO-DET / PS-001 / RS-001 records disappear on MCU refs plus downstream EMC / thermal / cross on those units; size with a corpus count of PR-DET records whose SW pin name matches `^PH\d`.

### KH-654: refs like `RF-C10` (lib `Device:C`, "5 pF") are typed `resistor`, so the current-sense detector reads a capacitor as a shunt

**Severity:** LOW (no longer reaches thermal after KH-568; still a false component type in the schematic output)
**File:** `skills/kicad/scripts/` component typing by reference prefix (the `RF-` prefix wins over the `Device:C` library symbol)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 (KH-568 investigation, handoff §Asks 4b)

**Symptom:** a capacitor whose reference starts with `R` (`RF-C10`, an RF-section cap) is typed `resistor` from its prefix, so the current-sense shunt path costed a 5 pF part; before KH-568 this produced the 2e9 W / Tj 3e11 °C thermal assessment.

**Fix direction / budget:** let the library symbol (`Device:C`) or a value with a capacitance unit override the reference prefix. Budget: component `type` on the affected refs and every detector keyed on it (size first: refs with a hyphenated prefix whose lib_id disagrees with the prefix type).

### KH-656: EG-001 follow-ups — keyword externality, protection through series parts, `VREG_*` / `VOUT_*` control names skipped as power

**Severity:** LOW (EG-001 is info since Wave 2)
**File:** `skills/kicad/scripts/cross_analysis.py:61` (`_is_power_net`), `:297` (connector keywords incl. `molex`, `phoenix`, `din`), EG-001 protection test
**Discovered:** 2026-10-25, product 3.0.x Wave 2 review (handoff §Asks 4d)

**Symptom:** (1) a connector is "external" when its value / footprint carries a keyword such as `molex` / `din` / `phoenix`, which also matches on-board headers; (2) protection reached through a series resistor / ferrite is not credited; (3) since `is_power_net_name` drives the power-rail skip, bare control / sense names such as `VREG_EN` and `VOUT_SENSE` are skipped as power, so EG-001 misses them. Corpus scale for context: EG-001 +12,915 info findings on 18,653 standard-profile cross units at the Wave 2 gate.

**Fix direction / budget:** classify externality from connector type / mounting rather than vendor keywords, follow one series part for protection, and exclude enable / sense suffixes from the power-name skip. Budget: EG-001 (info) presence on cross_analysis units.

### KH-657: GR-005 follow-ups — an open outer outline masked by any closed loop; stray Edge.Cuts endpoints have no info finding

**Severity:** LOW
**File:** `skills/kicad/scripts/analyze_gerbers.py` (GR-005 closure test after KH-565)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 review (handoff §Asks 4e, task-2 minors)

**Symptom:** any closed loop on Edge.Cuts (a cutout, a duplicated line) satisfies the closure test, so an open outer outline next to it passes; stray endpoints that close nothing get no finding. Related task-2 minors: a G74 arc with start == end is taken as a full circle, the GR-005 summary counts draws (undercounts modal-D draws), a `%` inside a G04 comment derails the outline parse.

**Fix direction / budget:** require the closed loop with the largest extent to enclose every other Edge.Cuts loop, add an info finding for unmatched endpoints. Budget: GR-005 presence on gerber units (Wave 2 gate moved GR-005 -66 / +64).

### KH-658: CC-001 compares the net-wide narrowest trace, not the connector's; TW-001 applies a regulator's output current to its input rail

**Severity:** LOW
**File:** `skills/kicad/scripts/cross_analysis.py` (CC-001 / TW-001 after KH-566)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 review (handoff §Asks 4g)

**Symptom:** CC-001 takes the narrowest trace anywhere on the net, so one unit got 6 findings from a single thin `+24V` segment far from the connector; TW-001 checks the input rail against the regulator's output current. Minor: CC-001 summaries state the estimated current as a fact (`~X A`; proxy capped at 1 A LDO / 2 A switcher).

**Fix direction / budget:** measure the trace attached to the connector pad, use the input current (`Iout * Vout / (Vin * eff)`) for the input rail, mark the current "(est.)". Budget: CC-001 / TW-001 on full-chain cross units (Wave 2 product estimate CC-001 6 / 1 unit, TW-001 6 / 3 units).

### KH-659: `ThermalSkipped.reason` schema description does not list `no_operating_current`

**Severity:** LOW (description text only; outputs stay schema-valid, the field is not an enum)
**File:** `skills/kicad/scripts/envelopes/thermal.py:80`
**Discovered:** 2026-10-25, product 3.0.x Wave 2 task-4 review (handoff §Asks 4h)

**Symptom:** KH-568 added the skip reason `no_operating_current`, but the `reason` field description still lists only the older reasons, so `analyze_thermal.py --schema` documents an incomplete vocabulary.

**Fix direction / budget:** add the reason to the description (docs wave). Budget: `--schema` text for thermal changes (one allow entry in the schema oracle); no output change.

### KH-660: dead `has_esd` conditional in the EMC test plan

**Severity:** LOW (cleanup)
**File:** `skills/emc/scripts/emc_rules.py:4158-4159` (`if not pair.get('has_esd', True) if proto else True: pass`)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 task-6 review (handoff §Asks 4i); verified at `004bba5`

**Symptom:** the conditional has a `pass` body and a misleading comment, so per-connector ESD never feeds the interface risk score.

**Fix direction / budget:** delete it, or score missing ESD per pair for real (then budget `test_plan.interface_risks[*].risk_score`). Deleting is output-neutral.

### KH-661: decide whether `cross_verify` is kept or retired (its decoupling check, KH-566 half, and DNP handling, KH-594)

**Severity:** LOW (decision item)
**File:** `skills/kicad/scripts/cross_verify.py:422` (rail name used as `ic_ref` in the decoupling check), `:121-186` (DNP, see KH-594)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 (handoff §Asks 4j); the decoupling half of KH-566 was left out of the Wave 2 fix

**Symptom:** `cross_verify`'s decoupling check never matches (it looks up a rail name as an IC ref), and KH-594 / KH-570 show the module drifting from the producer keys; Wave 2 fixed `cross_analysis` DA-001 but not this copy.

**Fix direction / budget:** rule keep or retire. Keep: port the DA-001 key reading and the `on_board` handling. Retire: remove the CLI and its harness tests. No corpus profile runs `cross_verify`.

### KH-663: legacy `Wire Bus Line` and bus entries are not parsed, so KiCad-5 bus connectivity is missing

**Severity:** MEDIUM (default path; 850 corpus `.sch` files carry `Wire Bus Line`)
**File:** `schematic/legacy_reader.py` (`_parse_legacy_single_sheet` reads `Wire Wire Line` only)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4)

**Symptom:** legacy bus wires, bus entries and bus labels never reach the bus pass, so members joined only through a bus stay split on KiCad-5 designs. The Wave 3 legacy `.net` oracle residue (2,516 split rows over 2,233 boards, `results/v30x_w3_gate_aux/legacy_oracle.json`) includes this class.

**Fix direction / budget:** parse `Wire Bus Line` / `Entry Wire Line` / `Entry Bus Bus` into the same bus structures as the modern reader. Budget: corpus output on legacy bus units (nets, every detector); oracle: the shipped KiCad-5 `.net`.

### KH-665: EMC BE-001 `_point_to_edges_min_distance` measures polygon and curve edges from (0,0)

**Severity:** MEDIUM
**File:** `skills/emc/scripts/` (`_point_to_edges_min_distance`)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4)

**Symptom:** for outline edges that are not line segments the distance is taken from the origin, not from the component, so BE-001 edge distances are wrong on curved / polygon outlines.

**Fix direction / budget:** reuse the outline distance helpers added in Wave 3 (see KH-674 note l); budget: EMC BE-001 on boards with curved outlines.

### KH-666: footprint-level `Edge.Cuts` graphics never reach `board_outline`

**Severity:** MEDIUM
**File:** `pcb/reader.py` (outline extraction reads board-level `gr_*` only)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4)

**Symptom:** a board whose outline (or a cut-out) is drawn inside a footprint on `Edge.Cuts` gets no or a partial `board_outline`; size, DFM, BV-001, NR-001 and the EMC edge rules then work from the wrong outline.

**Fix direction / budget:** transform footprint `fp_line` / `fp_arc` / `fp_circle` / `fp_rect` / `fp_poly` on `Edge.Cuts` into board coordinates and add them to the outline; budget: corpus output on boards with footprint outlines.

**Addendum 2026-10-29 (3.0.x Wave 4 Part B, close-triage rider):** footprint Edge.Cuts left out of the outline gives 4/299 closure mismatches with KiCad (Gecko_choc false "does not close"; 3 boards loops vs KiCad bbox); a self-intersecting outline is not detected (board 38); the duplicate-outline guard matches exact vertices only (a circle redrawn as arcs, or an offset copy, still cancels).

### KH-667: VM-001 voltage-domain heuristics misfire once connectivity is correct

**Severity:** MEDIUM
**File:** `validation_detectors.py` (`validate_voltage_levels`, `_estimate_rail_voltage_for_ic`)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4); VM-001 findings moved +3,099 / −984 on legacy units and +310 / −164 on modern units in the Wave 3 gate (`results/v30x_w3_gate/`; not all of it is this class)

**Symptom:** the detector takes an IC's voltage from its first rail, treats FPGA per-bank rails as one domain, flags dual-supply level translators and op-amp reference rails, reads an SSR input as a logic domain, and parses a voltage out of a sheet path. Correct connectivity (KH-511/513/514) exposes these on designs that used to be mis-joined.

**Fix direction / budget:** per-pin supply mapping (bank / VCCA-VCCB), skip translators and isolators by function, strip sheet paths before the voltage parse; budget: VM-001 on the affected designs.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part A):** VM-001 now fires on correctly joined nets: antmicro osm-l-bmc-som +18 (PCIe/REFCLK through an HD3SS3202, FPGA/SoC per-bank IO), HimaSava udimm +1, MAXI030 U35 EPF10K130 vs the 5 V bus / 74HCT245s +117, mort13 yarns +4, TVC +2. For Wave 4.

**Addendum 2026-10-28 (3.0.x Wave 4 Part A):** VM-001 now exempts USB D± (C1), takes regulator EN and PG endpoints as compatible (V5, C2), and judges each EN endpoint (`dda57cb`, `9b2f77f`, `6b671a0`, `b31d4ff`). Still open: a multi-supply IC's domain is its first positive supply (class A4c, james-l-key Esp32_patch_bay ADG419: logic set by VL 5 V, read at V+ 15 V); logic-supply pins (VL/VIO/VDDIO/VCCIO) should set the signal domain. The unconditional PG exemption is KH-721.

### KH-671: a root-sheet hierarchical label is keyed by its bare name and fuses with a global label or global bus member of the same name

**Severity:** MEDIUM
**File:** `schematic/connectivity.py` (`build_net_map`, label keys)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4)

**Symptom:** a dangling root `hierarchical_label D0` joins a `global_label D0` or a member `D0` of a global bus, which KiCad keeps apart.

**Fix direction / budget:** namespace root hierarchical labels like the child-sheet ones; budget: units with root hierarchical labels whose names collide with globals.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part A):** same-name hierarchical labels placed directly on two different top-level sheets join by bare name, where KiCad keeps them apart. Same fix: key root-level hierarchical labels per sheet.

### KH-673: same-net pad-pad overlap (stacked footprints) is not joined in the `--full` connectivity graph

**Severity:** LOW (opt-in `--full`)
**File:** `pcb/connectivity.py` (`build_connectivity_graph`)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4); 2 reCamera USB nets split vs KiCad DRC

**Symptom:** two overlapping pads of the same net on stacked/alternate footprints stay separate islands; KiCad joins them.

**Fix direction / budget:** add a pad-pad overlap pass beside the track-pad and pad-via passes; full-chain budget (`connectivity_graph`, PS-002 / RP-002).

### KH-674: Wave 3 follow-up notes (umbrella)

**Severity:** LOW (each item small; split out when picked up)
**File:** see items
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r)

**Items:**
- (a) the KH-518 vocabulary keeps `ON` / `OFF`, so switched rails like `5V_ON` classify as signals (the one vocabulary call to revisit; the Wave 3 gate saw `/pmu/3V3_POWER_ON` leave the power-net blocks on erikbeerepoot/bramble);
- (b) the no-underscore branch (`5VEN`) still uses the old suffix set;
- (c) LB-001 `label_count` counts instance-qualified entries, and LB-001 fires on legacy port renames once per instance;
- (d) a repeated legacy sheet with no `AR` record gives every instance the same references;
- (e) legacy sheet-pin labels are always angle 0; an escaped quote in a sheet-pin name truncates it;
- (f) `rail_voltages` sign is inconsistent across sources (inverting-regulator output rails stay positive; `/Analog/-5V` reads +5, W3-10 deferred); what_if drops the fix suggestion for inverting rails (see also KH-675);
- (g) capacitor `1e3` → 1,000 F (no plausibility guard);
- (h) a full-circle `gr_arc` (|angle| ≥ 360) is treated as a point by bbox / NR-001 / EMC;
- (i) duplicate `fp_circle` / `fp_rect` courtyards are not checked for doubling; different F/B outlines still interfere in PM-001; a side doubled on one layer drops both sides;
- (j) trapezoid / chamfered pads are measured as their full box in the contact model; explicit `F.Cu` / `B.Cu` THT pads get no inner layers (unverified); the track-track overlap query scans a whole bbox (slow on long diagonals); `float(roundrect_rratio)` is unguarded;
- (k) sheet pins use the label rule (1 IU on a wire) where KiCad may join them only at wire ends (unmeasured); `SEG::SquaredDistance` rounding ported from KiCad master;
- (l) the wave's three outline / pad distance helpers duplicate geometry (consolidate);
- (r) a courtyard side with only degenerate (< 0.01 mm) segments loses the whole `courtyard_poly` (PM-001 falls back to the AABB) — one-token fix `if not _unique: continue` at `pcb/reader.py` ~:539.

**Fix direction / budget:** per item.

### KH-677: six legacy boards match their shipped KiCad-5 netlist worse at `d2b9e72` than at `004bba5`

**Severity:** MEDIUM (triage; may include stale `.net` files despite equal ref sets)
**File:** `schematic/legacy_reader.py` / `schematic/reader.py` (pin placement, KH-511)
**Discovered:** 2026-10-26, harness, Wave 3 legacy `.net` oracle over the gate trees (`results/v30x_w3_gate_aux/legacy_oracle.json`)

**Symptom:** of 2,233 legacy boards whose netlist ref set equals the candidate's, 1,855 are clean at `d2b9e72` (100 at `004bba5`); six score worse (split+merged): NilujePerchut/doppelganger_hardware `arcade_adapter` (32 → 39; candidate `CMD` joins `/CMD`+`/Start`, `Down` joins `/CMD`+`/HK`, pins land on the neighbouring labels) and `usb_alien` (34 → 44), dannyandreev FadecandyHatV1.0 (8 → 18), azonenberg/antikernel `cat5-tdr` (64 → 65), DaniMzT encoderArduino_IoT (8 → 10), ChipCE/juice-plus-pcb `boost-converter` (2 → 3; `+24V` joins `Net-(D1-Pad2)`).

**Fix direction / budget:** check each against KiCad 5 (stale netlist vs a transform / orientation case the KH-511 fix misses).

**Disposition (2026-10-26, main repo):** stays open for triage against KiCad 5.

**Addendum (2026-10-27, Wave 3b Part A legacy oracle):** one fresh legacy board is worse at `6c488c2` than at `d2b9e72` (2,234 fresh boards: clean 1,856 → 1,985, split rows 2,516 → 2,282, merged 571 → 564). Duet3D/Duet-2-Hardware `Duet2/EthernetModule/DuetEthernet.sch` (bisected to `3f9e218`, power nets named from the hidden pin): the cache DEF `+3V3_A` (pin `+3V3_A`) carries `ALIAS +3.3V`, so the `+3.3V` symbols now join `+3V3_A`; the shipped netlist (Eeschema 4.0.2, 2017) keeps `+3V3`, made when `+3.3V` was the stock `power` library alias of `+3V3`. The candidate follows the cache; KiCad with the stock `power` library present would not. A library-availability ambiguity, not a clear defect.

### KH-679: equal-depth sibling-sheet driver ties resolve by sheet order; KiCad uses the sheet-name path

**Severity:** LOW (names only; membership unchanged)
**File:** `schematic/connectivity.py` (`build_net_map`, driver tie-break)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, ruling R5)

**Symptom:** when two drivers of equal priority sit on sibling sheets at the same depth, the net takes its name from the first sheet in parse order; KiCad compares the sheet-name paths. 28 name diffs vs kicad-cli on 4 s_rand boards (akuker pixel_grid, ClemensElflein CoverUI, jirihusak TinySensor, Nixie Driver Tester). Full ties (same priority, sheet and bare name) still resolve by encounter order.

**Fix direction / budget:** pass sheet names into `build_net_map` and break ties by sheet path; budget: net-name renames on boards with sibling-sheet ties.

### KH-680: `matchBusMember` flat-index-0 fallback for a group label on a group driver is not modelled

**Severity:** LOW (reach ≈ 0)
**File:** `schematic/connectivity.py` (bus member matching)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, ruling R6)

**Symptom:** in kicad-cli `P{X Y}` + `Q{Y Z}` on one bus gives P.X = {R1, R2} (KiCad falls back to the member at flat index 0); the analyzer keeps them apart.

### KH-681: no check for a hierarchical label with no matching sheet pin

**Severity:** LOW
**File:** `schematic/audits.py` / `validate_hierarchical_labels`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, entry 33)

**Symptom:** KiCad ERC reports a hierarchical label whose parent sheet has no matching pin. Since the Wave 3b false-signal fix (a hierarchical label on a net named by another driver is not "unconnected"), `hierarchical_labels.unconnected_hierarchical` effectively never fires, and nothing reports the missing pin.

**Fix direction / budget:** add the pin-less hierarchical label check; budget: new findings on boards with orphan hierarchical labels.

### KH-682: jotego ktiger joins root `/OBJDRAW3` with `/boardc/board c bot/OBJDRAW3` by hierarchy name

**Severity:** MEDIUM (false merge vs kicad-cli)
**File:** `schematic/connectivity.py` (hierarchical name join)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** the last power-sample merge outside the KH-403 class: a root net and a nested sheet net with the same leaf name join; KiCad keeps them apart. May share KH-671's mechanism.

### KH-683: PU-001 lists `MISO` among pull-up pin names

**Severity:** LOW (Wave 4)
**File:** `signal_detectors.py` (PU-001 pin-name list)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** now that pins carry their alternate names (kf/A2-F3), 6 new PU-001 findings appear on `SPI1_MISO` ×4 / `SPI2_MISO` ×2 pins; MISO is a push-pull output and needs no pull-up.

### KH-684: the DO-DET single-pin observation exempts pins by port-like names only

**Severity:** LOW (Wave 4)
**File:** `signal_detectors.py` (~:3604, `^P[A-K]\d` / `^GPIO` exemption)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** pins that now carry their alternate function name (`I2C3_SCL`, `TIM3_CH4`) lose the exemption: +4 observations in 4 units on the same single-pin nets.

**Fix direction / budget:** exempt by pin type / MCU part, or test the base name as well as the alternate.

### KH-685: a `no_connect`-type pin wired to a label or net joins it; kicad-cli isolates it

**Severity:** MEDIUM (membership, pre-existing; made scorable by Wave 3b instance refs)
**File:** `schematic/connectivity.py` (pin-to-net assignment)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, class C3)

**Symptom:** jotego vendetta JM1.15 (pin type `no_connect`) wired to `TEST` joins `/TEST`; kicad-cli exports it as `unconnected-(JM1-NC-Pad15)`. With that pin made `passive` kicad-cli exports `/TEST` {JM1.15}, and Gekkio SGB U3/U4/U5 pin 1 (NC wired to GND) is also left out, so this is a membership rule, not only naming. Reach on the samples: 9 nets / 4 boards (s_f1r vendetta, exterm ×4, Gekkio ×3; s_rand s18 `COIN_3`), plus m68k-hbc U25/U12 (its 2 merged nets).

**Fix direction / budget:** isolate `no_connect`-type pins as KiCad does; budget: nets / NT-001 / pin counts on boards with wired NC-type pins.

### KH-686: `{A{space}B C}` splits a bus group on the decoded space

**Severity:** LOW (pre-existing, not yet checked against kicad-cli)
**File:** `schematic/connectivity.py` (`expand_bus_name`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

### KH-687: `~` as `pin_name` / pin number reads as a literal in files < 20250318

**Severity:** LOW (separately budgeted output change)
**File:** `schematic/reader.py` (`extract_lib_symbols`, pin fields)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, ruling R14)

**Symptom:** KiCad reads a `~` pin name (and number) as empty below 20250318, as it does for fields (hb-N2); the analyzer keeps `~`. Changing it moves 5,763 entries in 38 quick outputs plus nets movement corpus-wide.

**Fix direction / budget:** apply the field rule to pin names/numbers in its own budgeted round.

### KH-688: quoted bus names are not parsed

**Severity:** LOW (0 known corpus uses)
**File:** `schematic/connectivity.py` (`expand_bus_name`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

### KH-689: KiCad's mixed vector ↔ group sheet-pin mapping is not modelled

**Severity:** LOW (an ERC-error construct)
**File:** `schematic/connectivity.py` (`match_ports`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, survey N4)

### KH-690: a bus-member net is named after a plain label on the net; KiCad names it after the driver's member

**Severity:** MEDIUM (names; membership matches kicad-cli)
**File:** `schematic/connectivity.py` (naming candidates)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, class C2)

**Symptom:** bus-member slot names are not naming candidates, for same-wire aliases (N1) and sheet-pin mappings. MAXI030 global `D[15..31]` + local `D[16..31]`: membership equals KiCad's but the name is `D16` vs KiCad `D31`; jotego ktiger has 18 nets with offset sheet-pin ranges (`/CPU_DB0` vs ours `/object/CPU_DB1`, `/MID12` vs `/object/MID28`). Reach: s_pwr 20 nets / 3 boards, s_f1r 1, and part of the s_busr residual.

**Fix direction / budget:** make the driver's member name a naming candidate at bus priority; budget: net renames on bus designs.

### KH-691: the tokenizer's brace-decode table differs from KiCad's `UnescapeString`

**Severity:** LOW (reach ≈ 0)
**File:** `kicad_core/sexp.py` (`_KICAD_UNESCAPE`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** the table lacks `{comma}` / `{dollar}`, decodes `{amp}` / `{newline}`, and ignores the `$ ~ ^ _` prefix rule. It affects non-net text and a power Value containing `{comma}`. Switching to KiCad's table would move values and descriptions.

### KH-692: multi-root projects share no text variables, power renames or root instances across peers

**Severity:** LOW (0 corpus multi-root projects)
**File:** `schematic/hierarchy.py` (`merge_top_level_sheets`), `kicad_core/textvars.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** `${REF:FIELD}` across top-level sheets stays literal (one `TextVarRegistry` per peer); the power rename and root instances are not shared across peers; sheet order follows the named file, not the declared order.

### KH-693: text-variable tokens left unresolved

**Severity:** LOW
**File:** `kicad_core/textvars.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** `${#}` / `${##}` page numbers, net/pin functions (`${SHORT_NET_NAME(1)}`), `@{}` math, dates / VCS, `FILEPATH`, custom unit names and KiCad 10 variant overrides stay literal. On the tv sample this leaves 8 values (`${SHORT_NET_NAME(1)}` ×6, `${#}` ×2).

### KH-694: CG-AUD finds ground by net name, so a connector whose GND pins sit on an unnamed sub-sheet ground net reports "no ground pins"

**Severity:** LOW (Wave 4)
**File:** `domain_detectors.py` / audits (CG-AUD)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4) — Just4Stan `pi_header` J4, now that the RPi header has pins

### KH-696: KiCad's output-shape sheet-pin driver preference is not modelled

**Severity:** LOW (not seen)
**File:** `schematic/connectivity.py` (sheet-pin driver choice; sheet-pin shape not parsed)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** ResolveDrivers prefers an output sheet pin before the name. With two pins this only changes which root taps join; with three or more same-kind pins and no superset, a narrower driver could leave members unpaired where KiCad pairs them.

### KH-697: a vector driver over a group child pairs by name; KiCad gives group members VectorIndex 0

**Severity:** LOW (pre-existing)
**File:** `schematic/connectivity.py` (`match_ports`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** `X[0..1]` + `{X0 X1 Y}`: kicad-cli joins cpu X0 with io X0, X1 and Y.

### KH-698: a label-less cluster of ≥ 3 pins mixing kinds with two shifted-range vectors still unions `grp[0]` positionally

**Severity:** LOW (not seen)
**File:** `schematic/connectivity.py` (sheet-pin clusters, the `6c488c2` C6 path)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

**Symptom:** could chain like the tnzs C1 case that `6c488c2` fixed for single-kind clusters.

### KH-695: Wave 3b Part A follow-up notes (umbrella)

**Severity:** LOW
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4)

- (a) `0` as ground needs schematic rails, so PCB/EMC/cross callers still read `0` as a signal;
- (b) `power_symbol_drives` checks only `pins[0]` (KiCad decides per pin);
- (c) a hidden power-in pin with an alternate names its net from the alternate (KiCad: the base name; `connectivity.py` ~:830);
- (d) duplicate-number jumpers are grouped by the expanded number (KiCad: raw number, first pin only);
- (e) the junction union uses the 0.05 mm bus tolerance where KiCad is exact; the unterminated-range quirk `D[1..3` is not reproduced;
- (f) KiCad's legacy rule 1 (an unshared screen ≤ 20200310 uses the field) is not modelled (24 files); the KiCad 6 first-instance fallback follows `symbol_instances` order; a duplicate path keeps the last entry (KiCad: the first); a uuid group mixing `""` and a value takes the fast path;
- (g) `.pro` `LibName` / `LibDir` regexes scan the whole file incl. `[pcbnew/libraries]` (487 `.pro`); a bare name with no cache falls back to the first table row; duplicate table nicknames: the last row wins;
- (h) `1 000k` (grouped mantissa + prefix) reads 1 where KiCad reads 1e6; `100nF,50V` (no space) stays None; a 4+-digit first group does not start a join (R17);
- (i) a multi-unit line takes DNP/exclusion from its first in-BOM unit in parse order; duplicate single-unit refs keep one copy's fields where KiCad's BOM merges them (8 f4 footprint rows); `compute_statistics` takes the first record per ref;
- (j) project name from the named schematic stem, not the `.kicad_pro` stem; mixed path normalisation; a single-entry `top_level_sheets` with a non-nil uuid is not applied (R20, headless 10.0.7; 1 project);
- (k) cross-references stay literal on `merge_top_level_sheets` peers; title-block text gets 6-pass expansion (KiCad: one pass);
- (l) tokenizer: the `#` line-start test is quadratic on one-line files; octal `\400` wraps to NUL;
- (m) stale "verbatim move" module docstrings in `schematic/connectivity.py:3` and `audits.py:1`.

### KH-701: net-less copper never takes a net — KiCad's `PropagateNets` joins pads through a net-less or `(net 0)` copper shape

**Severity:** LOW (pre-existing; conformance)
**File:** `pcb/reader.py` (`read_board`), `pcb/connectivity.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (ruling R25); filed by the harness from the handoff §Asks 4

**Symptom:** KiCad propagates nets onto net-less copper (`connectivity_algo.cpp:665-724`: net-agnostic clusters, zones excluded; tracks, arcs, `PCB_SHAPE` and non-free vias take the cluster's net unless the cluster has pads of two nets; it never merges nets). kicad-cli 10 joins two pads through a net-less or `(net 0)` copper `gr_poly` or segment with 0 unconnected. We keep "no net joins nothing". Reach upper bounds: ≈ 430 boards with net-less copper `gr_*`, ≈ 570 with net-0 tracks.

**Fix direction / budget:** the pass belongs in `read_board` (the graph is per net) and moves default-path track nets (`net_lengths`, RT-001), so it needs its own survey, oracle and budget. When it lands, flip the product tests `tools/tests/test_pcb_graphic_copper.py::test_graphic_without_net_joins_nothing` (:105) and `::test_graphic_net_zero_joins_nothing` (:110).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** stays open; home is the C14 umbrella KH-751 (rerun Task 111's residual when it lands).

### KH-702: custom-pad residue — zone probes, VP-001 and CP-003 use the anchor box; KiCad 9+ padstack primitives are not read

**Severity:** LOW
**File:** `pcb/geometry.py` (`copper_radius`, `_point_in_pad`), `pcb/copper.py` (VP-001, CP-003 sampling), `pcb/reader.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (Task 20, survey-deferred); filed by the harness

**Symptom:** after `e44cafe` custom primitives take part in pad-track contact, but zone probes (`copper_radius`), VP-001 `_point_in_pad` and CP-003 sampling still use the custom pad's anchor box (residue e.g. BelaPlatform textile capelet, 1 split). KiCad 9+ per-layer custom primitives and anchors inside `(padstack (layer …) (primitives …))` are not read (front-layer geometry is used), and a hatched primitive fill counts as solid.

**Fix direction / budget:** one shape model for custom pads across contact, probes and sampling; budget `--full` graph + VP-001 / CP-003 on custom-pad boards (2,252 boards carry the construct).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** stays open; home is the C14 umbrella KH-751 (one custom-pad shape model with A7-F1 / A7-F3).

### KH-703: property writers cannot target an instance reference on a repeated sheet

**Severity:** LOW (writer correctness; `sync_datasheet_urls --recursive` reach widened in Part B)
**File:** `skills/bom/scripts/edit_properties.py` (`apply_updates`), `sync_datasheet_urls`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (entry 46); filed by the harness

**Symptom:** `bom_manager` now reports instance references (C7 on a repeated sheet whose file property says C4), but `edit_properties.apply_updates` and `sync_datasheet_urls` find a symbol by the file's `Reference` property, so they cannot target such a ref. `sync_datasheet_urls --recursive` now reaches KiCad 6 sub-sheets (before Part B it skipped them); on a repeated sheet a stale file reference could receive another part's URL (it fills only empty Datasheet fields). No dry-run test covers it.

**Fix direction:** resolve the target by instance path; add a repeated-sheet dry-run test.

### KH-704: JLCPCB CPL bottom-side rotation / X convention has no cited reference

**Severity:** LOW (waits on a reference)
**File:** `skills/bom/scripts/translate_bom_pnp.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (ruling 23); filed by the harness

**Symptom:** the translator's bottom-side rotation and X convention is unchanged. Ruling 23 requires JLCPCB's current published CPL convention, cited in code; no dated reference has been found yet.

**Fix direction:** find the dated JLCPCB reference, cite it, align the transform; oracle = a known-good JLCPCB bottom-side order.

### KH-706: bom_manager has no report-level `diagnostics`

**Severity:** LOW (report shape change when fixed)
**File:** `skills/bom/scripts/bom_manager.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness

**Symptom:** on the `.kicad_sch` path a sheet that includes its ancestor is skipped silently; on the `.sch` path one stderr `Warning:` line is printed (pinned by `test_sheet_including_its_ancestor_is_skipped_with_a_warning`).

**Fix direction:** add a `diagnostics` list to both paths (a BOM report shape change; re-pin the product test).

### KH-707: unit-count semantics differ across cross_analysis, bom_manager and the analyzer

**Severity:** LOW
**File:** `cross_analysis.py` (`_multi_unit`), `skills/bom/scripts/bom_manager.py` (`_library_unit_counts`), schematic analyzer
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness

**Symptom:** cross_analysis `_multi_unit` infers a multi-unit part from placed unit numbers (the output has no library unit count), so a multi-unit part with only unit 1 placed twice, or with no unit number, compares as separate symbols where KiCad would merge (`GetUnitCount() > 1`, `netlist_exporter_base.cpp:113-119`). bom_manager counts distinct sub-symbol unit numbers, the analyzer counts units with pins, and KiCad uses the highest unit number (differs only for pinless units or gaps).

**Fix direction:** emit the library unit count in the schematic output and use KiCad's highest-unit rule everywhere.

**Addendum 2026-10-28 (3.0.x Wave 4 Part A):** after `be60a07` (missing units by library unit count): legacy symbols resolved through pipeline fallbacks get unit_count 1 (no missing-unit record); the footprint name is taken after the last `:` (KiCad: the first); an unparseable footprint string is not skipped; the pin-based `_unit_count` leftover remains at `reader.py:912`.

### KH-710: Wave 3b Part B follow-up notes (umbrella)

**Severity:** LOW
**File:** `pcb/*`, `schematic/*`, `skills/bom/scripts/bom_manager.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness

- (a) the CP-001 finding's `layer` field still names the footprint's layer when only a cross-side SMD pad fires it (finding-shape change; 0 seen in 100 boards);
- (b) a hatch fill on a copper graphic counts as solid (KiCad's effective shape leaves holes; could join both ways);
- (c) a zone with no `min_thickness` on a stroked-fill board is not inflated; KiCad uses the 0.25 mm default (corpus ≈ 0; harness `tests/fixtures/kh392-antipad/board.kicad_pcb` has this shape);
- (d) TV-001 inside-outline uses the rectangular pad bounds (round/oval thermal pads count their bbox corners as inside); a via tented on one side counts as tented; a negative `solder_mask_margin` that closes the opening is not considered;
- (e) VP-001 does not read KiCad 9 via `(filling)` / `(capping)` protection;
- (f) `--variant`: the analyzer applies a variant `(field (name "Reference") …)` and overrides Value/Footprint/Datasheet/Description even when the symbol lacks the property; bom_manager and KiCad's `GetFieldText` do neither (KiCad never writes a Reference override);
- (g) malformed polygon arcs are skipped silently (KiCad raises);
- (h) a modern board with drill-less vias and no `(net_class)` uses KiCad's 0.3 / 0.1 mm default; KiCad would use the `.kicad_pro` Default class, which the reader does not read (1 corpus board);
- (i) the pad drill offset decides NPTH copper only; the graph still places every pad's copper at the hole centre (KiCad uses `ShapePos`; pre-existing for all pads, W3-15);
- (j) bom_manager names the project from the input stem, not the `.kicad_pro` stem or a KiCad 10 declared root; it walks only the named root of a multi-root project (KH-692 family).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** (d) FIXED by `24d60d4` (TV-001 inside test by pad outline, one-side tenting, negative mask margin; thermal-pad vias by net and pad outline; via-in-pad exempts only the thermal pad; kc/R9-F2, R9-F6, ruling R53; classes P10 / P10b). (e) not folded (AD-B9: reach 0). Still open with the C14 umbrella KH-751 as their home: (a) fold into the next CP-001 edit, (b) reach 0, (c) would move the `kh392-antipad` fixture (own ask), (i) contact-model change, rerun `rc_conf_g.py`. The handoff does not address (f), (g), (h), (j).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B, close-triage rider):** `copper.py` `_mask_opening_size` reads only the pad-local margin (KiCad: pad → footprint → board `pad_to_mask_clearance` → DRC rule) and its docstring overclaims; VP-001 `_via_exposed_by_pad` ignores a negative margin and one-side tenting (TV-001 and VP-001 disagree); a heatsink pad without a TV-001 entry gets no wicking feedback (R53 cost).

### KH-711: placed-symbol mandatory fields are read by exact name; KiCad 10 matches them case-insensitively and lets a later duplicate replace the earlier

**Severity:** MEDIUM
**File:** `schematic/reader.py` (placed-symbol property read)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** KiCad 10 matches `Reference/Value/Footprint/Datasheet/Description` case-insensitively (`sch_io_kicad_sexpr_parser.cpp:2338-2346`), and a later duplicate of a mandatory field replaces the earlier (`:3526-3553`). We read the exact name. Corpus: 4,158 such fields in 350 `.kicad_sch` files (Description 2,535, Datasheet 1,173, Value 431, Footprint 11, Reference 8; measured, product `oracle-scripts/planA/reach.py`).

**Fix direction / budget:** match the five mandatory names case-insensitively, last duplicate wins; budget component values/datasheets on those files (class AD-A1).

### KH-712: the PCB power-rail set is built from schematic power-symbol values and heuristic names, not board net names

**Severity:** LOW-MEDIUM
**File:** PCB power-rail set (`pcb/*` power-net resolution)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the rail set comes from schematic power-symbol values and heuristic names. These differ from board net names since power nets can be named from the pin (Wave 3b A2-F2), and KiCad 9+ local power symbols lose rail status on the board (product rails survey §6).

**Fix direction / budget:** derive the board rail set from board net names; budget pcb power-net consumers (its own survey).

### KH-713: the op-amp bench measures gain at 1 kHz even when a feedback capacitor puts the closed-loop pole below it

**Severity:** MEDIUM
**File:** `skills/spice/scripts/spice_templates.py` (op-amp bench)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** Colossus U3 250 MΩ ∥ 125 pF; ovobot U14/U15 51k ∥ 100 nF, f_pole ≈ 31 Hz. Measuring at 1 kHz gives false SP-FAIL and part of the remaining op-amp warns.

**Fix direction / budget:** measure below 1/(2π·Rf·Cf). Gates KH-507. Budget: op-amp benches with a feedback capacitor under spice-offline.

### KH-714: the PNP transistor bench template never reaches an on-state (VBE(on) ≈ 2.647 V, `ic_on_mA` ≈ 2.5e16)

**Severity:** MEDIUM
**File:** `skills/spice/scripts/spice_templates.py` (transistor bench, PNP)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the plan's "NPN VBE 2.647 V" item: all 17/17 PNP benches that ran in the product sample warned with it (dvhx Q11/Q14/Q17 …). Since `c9374d6` they warn "not measured" without values and are labelled PNP. Estimated 762 + 78 corpus.

**Fix direction / budget:** fix the template, then take polarity-correct measurements; budget PNP `transistor_circuit` results under spice-offline.

### KH-715: the P-channel MOSFET bench reports `vth_V` 0.0 (sweep direction)

**Severity:** LOW
**File:** `skills/spice/scripts/spice_templates.py` (transistor bench, P-channel)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** P-channel MOSFET benches report `vth_V` 0.0 because of the sweep direction, left after Task 24's `i_on` fix.

**Fix direction / budget:** sweep in the P-channel direction; budget P-ch `transistor_circuit` values under spice-offline.

### KH-716: SPICE benches that still pass on presence, not a design-derived criterion (entry 13)

**Severity:** MEDIUM (ruling R40 merged)
**File:** `skills/spice/scripts/spice_templates.py`, `spice_results.py`
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (KH-618 remainder)

**Symptom:** protection "diode present" (165 / 300 sample), decoupling below a generic 10 Ω at 1 MHz or "caps present" (1,061), inrush passes whenever `i_peak` is measured and never compares it with `estimated_inrush_A` (334), snubber τ-range (15), rf_chain warns outside −30..+40 dB on heuristic gains (should be info), divider/feedback-network self-comparison, transistor pass on `i_on` alone with a part-library model.

**Fix direction / budget:** each needs a criterion (estimate tolerance, IC-derived Z target) or `info`, with a corpus budget.

### KH-717: `is_power_net_name` admits signal suffixes (`PWR_OK2`, `5V_FAULT`, `VBAT_ADC`, `5V_ISENSE`, `12V_{FBM}`, `PWR_LED`), so divider chains stop at such a node

**Severity:** MEDIUM
**File:** `kicad_core/netnames.py` (`is_power_net_name`); `signal_detectors.py:411-425` (`_merge_series_dividers._is_passthrough`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (pre-existing at base and tip)

**Symptom:** `_is_passthrough` stops at a power-by-name node, so bluesat owr-502 U220 MP2459 reads r_top 47k (4.617 V) instead of 147k (12.7 V); its SPICE fail (159.9 %) was false and is info since `1569ae9` (R39). The LR-001/LA-AUD `PWR_OK2` reading (R25 M6) is the same root.

**Fix direction / budget:** a node that is power by name only and carries exactly two resistors passes through. Moves VD-DET/PR-DET chains corpus-wide; needs a survey and budget.

**Addendum 2026-10-29 (3.0.x Wave 4 Part B, close-triage rider):** the classifier-missed planes of P12c (Earth, `3x2M_NM`, V_SUPPLY, `/ADAU1452/IOVDD`, `_GND_0`, VUSB, pin-named rails) give false return-path entries and RP-002 (m221 MCLK, m000 XTAL). m000's `3x2M_NM` GND needs identity by pin function. `/power/VCCINT` on an LDO `power_out` reads `signal` in net classification.

### KH-718: family Vref table values are wrong for members of the family (TPS6102x/3x, TPS561201, LT8606, TPS562212, TPS563240)

**Severity:** MEDIUM
**File:** regulator Vref table (`signal_detectors.py` `_lookup_vref`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** TPS61025/32 (`TPS6102`/`TPS6103` 0.595), TPS561201 (`TPS561` 0.6), LT8606 (`LT860` 0.97), TPS562212 (`TPS562` 0.768), TPS563240 (`TPS5632` 0.76). SPICE no longer uses a shorter key as a criterion (R35), but these values drive analyzer `estimated_vout`.

**Fix direction / budget:** fix from datasheets; analyzer budget on `estimated_vout` / `rail_voltages`.

### KH-719: readers that lose a rail's sign (fixed 79xx estimate +5 V on `-5V`, boost with a negative divider top, `-VCC_5V`, op-amp `-VBAT`, SPICE `_infer_voltage`)

**Severity:** LOW-MEDIUM (KH-675 sibling)
**File:** `signal_detectors.py` (`_lookup_vref` `LM7[89]…`, boost path, `_rail_name_voltage`), op-amp rail read, `skills/spice/scripts/spice_templates.py` (`_infer_voltage`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (KH-675 remainder)

**Symptom:** fixed 79xx regulators estimate +5 V on `-5V` (james-l-key U204 LM7905, `rail_voltages['-5V'] = 5.0`); a boost path with a `V-`/`VEE`/leading-minus divider top reads positive (no test); `_rail_name_voltage` reads `-VCC_5V` as 5; op-amp `-VBAT` → +3.7; SPICE `_infer_voltage` has no sign (negative-rail transistor benches run at +3.3 V, results info/warn, never pass) and reads `0V…` names (`0VCC`, `0V_SENSE`) as 0 V (`test_spice_zero_span.py` pins the no-sign quirk and must flip with the fix); op-amp rails on sheet paths (`/sheet/-12V`) are not parsed (lost criterion → info).

**Fix direction / budget:** keep the sign in every reader; budget `rail_voltages` / regulator estimates and the affected benches.

### KH-720: CAN split termination (60 + 60 Ω) and off-board termination are reported "missing termination"

**Severity:** MEDIUM (false issue)
**File:** `schematic/net_analysis.py` (`bus_analysis.can`), PR-003
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** split termination (60 + 60 Ω) and off-board termination read as missing termination. PR-003 counts a DNP terminator (R15).

**Fix direction / budget:** recognise split termination; budget `can[].termination` / `protocol_compliance[can]`.

### KH-721: the VM-001 PG endpoint exemption (C2) is unconditional

**Severity:** LOW-MEDIUM (R42 b)
**File:** `validation_detectors.py` (`validate_voltage_levels`, `_PG_PIN_PATTERNS`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** a push-pull PG, or PG pulled up to the regulator's higher VIN and wired to a lower-voltage IC, now drops a real crossing (≈ 50 corpus PG-pin VM-001).

**Fix direction / budget:** judge the PG net's pull-up rail against the input's limit instead; budget VM-001 on PG nets.

### KH-722: a label-like regulator Value that parses as a part-number core makes the SPICE regulator bench `info` "the value names another part"

**Severity:** LOW (R42 e)
**File:** `skills/spice/scripts/spice_templates.py` (regulator Vref criterion, `d2e0b70`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** a label-like Value (`LDO1`, `BUCK5V`, `U3V3`, `DCDC24V/5V NUM`) on a real-part symbol gives info with a misleading note, and a valid criterion is lost. 17 / 987 corpus lookup-Vref regulators, ≈ 4 bogus (3 label-like, 1 typo `TPMP2359DJ`).

**Fix direction / budget:** do not treat label-like values as a part number; budget the regulator benches above.

### KH-723: field-trim residue — KiCad 6 instance `(value " ")`, KiCad 10 variant override texts, stale `mandatory_field` docstring

**Severity:** LOW
**File:** `schematic/reader.py` (~:725 `mandatory_field` docstring, instance values, variant texts)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (KH-708 residue)

**Symptom:** a KiCad 6 instance `(value " ")` reads as unset where KiCad overwrites with `""` (`sch_sheet_path.cpp:1585`; 0 corpus); KiCad 10 variant override texts are not trimmed (≈ 0 reach); the `mandatory_field` docstring at `reader.py:725` still names the old character set.

**Fix direction / budget:** as KiCad; ≈ 0 corpus reach.

### KH-724: reference and bias nodes named like rails get RS-001 "no declared source" and DO-DET "missing decoupling"

**Severity:** LOW
**File:** RS-001 / DO-DET (power-net consumers)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (class A4a, R6); filed by the harness

**Symptom:** `1.25V_REF`, `1.8V_REF`, `2.5V`, `REV2V5` read as rails (product legacy sample: RS-001 3 + DO-DET 5 per 80).

**Question / fix direction:** should DO-DET/RS-001 treat a reference node as a rail? Budget: RS-001 / DO-DET on reference nodes.

### KH-725: PCB-only runs on pre-KiCad 7 boards keep the VPP/VM name rule; EG-001 `pin_signals` does not skip power-symbol rails

**Severity:** LOW
**File:** `pcb/*` (power-net rule without pad pin types), `cross_analysis.py:316` (EG-001 `pin_signals`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** boards before KiCad 7 have no pad pin type, so PCB-only runs keep the VPP/VM name rule; EG-001 `pin_signals` does not skip power-symbol rails (0 chain deltas).

**Fix direction / budget:** small; 0 chain deltas measured.

### KH-726: a sheet-local `/x/PGND` gets no 0 V in the rail map

**Severity:** LOW
**File:** `schematic/net_analysis.py` (~:1397, ground set)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the ground set omits PGND, so a sheet-local `/x/PGND` gets no 0 V entry.

**Fix direction / budget:** add PGND to the ground set; budget `rail_voltages` keys.

### KH-727: `ctx.rail_by_net` is a phase-1 side effect read unchecked in phase 3

**Severity:** LOW
**File:** `schematic/pipeline.py` (~:370, 473-475)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** a caller that skips phase 1 silently loses AM/OV/FT.

**Fix direction:** check or build the map where phase 3 reads it; no output change expected.

### KH-728: config-override consistency — `voltage_overrides` leaf match, LDO dissipation, inrush `abs()`, VM-001 skip, name-only readers

**Severity:** LOW (corpus 0, no configs)
**File:** `voltage_overrides` consumers (rail map, LDO dissipation, inrush, VM-001, `_rails_voltage_compatible`, `bom_stats`, what_if)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R9); filed by the harness

**Symptom:** a `voltage_overrides` leaf match reaches non-power nets (`/S/VOUT`); LDO dissipation uses `estimated_vout` with an overridden VIN; inrush takes `abs()` of a negative override; an override on a net that is not power by name skips VM-001; cross-domain `_rails_voltage_compatible`, `bom_stats` and what_if read voltages by name only.

**Fix direction / budget:** one override-aware voltage reader; corpus 0.

### KH-729: the regulator detector types an MCU and gate drivers as regulators

**Severity:** LOW
**File:** regulator detection (`signal_detectors.py`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** bluerobotics ping-dev-kit: an MCU and gate drivers become regulator records.

**Fix direction / budget:** budget PR-DET on the affected units.

### KH-730: half-bridge detections on logic nets

**Severity:** LOW
**File:** half-bridge detection
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** tmarhguy `W6`, joewing `DBUS11` are detected as half bridges; their benches are info now (generic model).

**Fix direction / budget:** budget half-bridge records and benches.

### KH-731: DO-DET observations carry no `divider_plus_rail_name` provenance

**Severity:** LOW
**File:** DO-DET record provenance
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** only PR-DET carries the provenance, so what_if cannot tell a manufactured agreement.

**Fix direction:** carry the provenance on DO-DET observations.

### KH-732: Vref table rows waiting for cited datasheets — LTC3558, LM2731x, LMR33640

**Severity:** LOW
**File:** regulator Vref table (`_lookup_vref`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** LTC3558 (0.8 V; restores a true `+4V` mismatch), LM2731x (1.23 V), LMR33640 (a full-core row would turn alexnaet's true 86 % divider error from info back to fail; no local SNVSB37).

**Fix direction / budget:** add with cited datasheets; small regulator budget.

### KH-733: diff-pair ESD credit residue — all-input clock buffer and a connector typed `ic` still credited; bare "protection" matched in descriptions

**Severity:** LOW
**File:** `classify_ic_function`, diff-pair ESD credit (`schematic/net_analysis.py`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R13); filed by the harness

**Symptom:** an all-input clock buffer (Si53322) and a connector typed `ic` (SM05B) are still credited; `classify_ic_function` matches a bare "protection" in descriptions (regulators with overcurrent protection, transceivers with ESD protection).

**Fix direction / budget:** budget `differential_pairs[].has_esd`.

### KH-734: `is_usb_data_net_name` still matches `USB_DTR`/`USB_DET` for the KH-343 VBUS fallback; GPIO-style `USB_DP_*` nets take the VM-001 exemption

**Severity:** LOW
**File:** `is_usb_data_net_name` and its callers (KH-343 VBUS fallback, VM-001)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** a VBUS-detect net named `USB_DET` does not inherit 5 V through the KH-343 fallback; `USB_DP_PU`/`USB_DP_EN`-style GPIO nets would take the VM-001 USB exemption (0 corpus).

**Fix direction / budget:** one shared exclusion list; 0 corpus for the second half.

### KH-735: SPI/CAN bus-check residue (master select as CS conflict, empty CAN nets, `CAN1H`/`CAN1L`, terminator filter, passive CS pins, `SS`/`CS` tokens)

**Severity:** LOW
**File:** `schematic/net_analysis.py` (`_analyze_bus_protocols`, `_detect_differential_pairs`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** a master select typed input reads as a CS conflict (Dash BT817); a CAN transceiver with no bus nets reports `nets: []`; `CAN1H`/`CAN1L` names are not detected; a multi-transceiver placeholder can mask a second bare bus; the diff-pair terminator list takes any resistor (no 100-150 Ω filter); CS conflicts are lost when slave CS pins are typed passive/bidirectional or the slave is an FPGA/CPLD; `SS`/`CS` tokens match soft-start/current-sense nets in `chip_select_count`; an ambiguous unpaired CANH falls back to "present" with `nets: []`.

**Fix direction / budget:** per item; budget `bus_analysis`.

### KH-736: I2C VOL checks SDA pull-ups only; Fm+ not modelled; no mixed-rail Thevenin test

**Severity:** LOW
**File:** `protocol_compliance[i2c].checks.vol_compatibility`
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** only SDA pull-ups are checked; Fm+ (IOL 20 mA) is not modelled; no mixed-rail Thevenin test.

**Fix direction / budget:** budget I2C `vol_compatibility`.

### KH-737: family matching on `lib_id` reads the library nickname

**Severity:** LOW
**File:** part-family matching (`detect_rf_chains` / wireless family lookup)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** 6 files: non-radio parts in `STM32WL-DevKit` libraries are typed LoRa (wrong before and after Part A).

**Fix direction / budget:** match the symbol name after the nickname; 6 files.

### KH-738: ERC residue — hierarchical-port NC suppression not modelled; double PWR_FLAG and positionless PWR_FLAG marker misses

**Severity:** LOW-MEDIUM
**File:** `schematic/erc_pins.py`, `schematic/net_analysis.py` (`_check_erc_warnings`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** KiCad's hierarchical-port suppression of NC markers is not modelled (≈ 8 % of `no_connect_connected`); nets with two PWR_FLAGs and the positionless PWR_FLAG nearest-pin rule give the remaining pin_to_pin marker misses (recall 0.983 vs kicad-cli 10.0.7).

**Fix direction / budget:** model both rules; budget `erc_warnings`.

### KH-739: RC/high-pass residue — caps to different grounds merge onto one R, reversed high-pass nets, `claimed_components` inconsistency

**Severity:** LOW
**File:** RC-DET / high-pass records (`signal_detectors.py`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R21, R22); filed by the harness

**Symptom:** caps to different grounds or far nodes still merge onto one R (unlabelled since R21); high-pass `input_net`/`output_net` read reversed when the resistor sits source-side; `claimed_components` is inconsistent between RC records (R22).

**Fix direction / budget:** budget RC-DET records.

### KH-740: LED residue — LR-001 `has_driver` scans rails/GND, `_is_led_node` counts any resistor, parallel-string dissipation, LA-AUD chain walk crosses a branch

**Severity:** LOW
**File:** `validation_detectors.py` (`validate_led_resistors`), LED audit
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R25 M5, R26); filed by the harness

**Symptom:** LR-001's `has_driver` scans rails/GND, so an MCU on GND silences a dangling LED; `_is_led_node` counts any resistor, so a pull-up on a name-only LED+R rail can make it a node; parallel strings sharing one resistor report dissipation per string with one string's current; the LA-AUD fallback LED-chain walk crosses a branch point.

**Fix direction / budget:** budget LR-001 / LA-AUD.

### KH-741: a UC3845 COMP pin behind a solder jumper is not found

**Severity:** LOW
**File:** FS-001 COMP-pin lookup
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** kaminaris: a UC3845 COMP pin behind a solder jumper is not found.

**Fix direction:** follow solder jumpers (net ties) in the COMP lookup.

### KH-742: domain-advisory residue — USB-PD summary shows an overwritten value, integrated-magnetics keywords missing, STUSB4500 `CC1DB` duplicates `cc_nets`

**Severity:** LOW
**File:** `domain_detectors.py` (~:3001 USB-PD summary, `_INTEGRATED_MAG_KEYWORDS`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the USB-PD summary shows an overwritten component's value (the summary text feeds ids); integrated-magnetics jack keywords `rjmg`/`lpjg`/`7499` missing (`+mag`/`-mag`/`transfo` need a negation check); STUSB4500 `CC1DB` tied to CC1 duplicates `cc_nets`.

**Fix direction / budget:** per item; ids move where the summary text changes.

### KH-743: alternate SPICE backends — Xyce/LTspice phase unit, LTspice parser misreads exponents and two-`=` lines, `let` skipped

**Severity:** LOW
**File:** `skills/spice/scripts/spice_simulator.py`, `spice_results.py`
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** Xyce/LTspice phase unit not established (only the ngspice read converts radians); the LTspice output parser misreads exponent numbers (`1.58e+04`) and lines with two `=`; LTspice/Xyce skip `let`, so the crystal note blames the sweep.

**Fix direction:** establish units per backend; fix the parser (see KH-629).

### KH-744: op-amp library `supply_min` values look high (OPA1612, TL07x, NE5532)

**Severity:** LOW
**File:** op-amp model library (`supply_min`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** OPA1612 9 V vs 4.5 V datasheet; TL07x vs TL07xH; NE5532. They decide S2's below-minimum warns/infos.

**Fix direction / budget:** verify against datasheets before editing; budget op-amp bench status.

### KH-745: Monte Carlo varies a parallel equivalent arm as one part, overstating the spread

**Severity:** LOW
**File:** `skills/spice/scripts/spice_tolerance.py:67-86`
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the spread is overstated by up to √N for N equal members (wider, never narrower). Members' values are not in the record. MC is opt-in.

**Fix direction:** carry member values and vary each.

### KH-746: SPICE bench-input residue — a regulator divider holding a pot leaves no record; op-amp ground-leg filter matches refs by prefix

**Severity:** LOW
**File:** `skills/spice/scripts/` (regulator pot guard, op-amp ground-leg filter)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R34 M6, M8); filed by the harness

**Symptom:** a regulator whose divider holds a pot/trimmer (pot guard) leaves no SPICE record at all; the op-amp ground-leg filter matches refs by prefix (`R1` drops an `R10…` line).

**Fix direction / budget:** report the pot case as info/skip with a reason; match refs exactly.

### KH-747: Vref key core cut — fixed-output parts cut to a covering core; wildcard values make a key cover

**Severity:** LOW
**File:** regulator Vref key matching
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** `LD33`/`NCP1117ST33` fixed-output parts cut to a covering core; wildcard values (`TPS6103x`, `LM259x`) make a key cover (a simple rule breaks `TPS560430X`).

**Fix direction:** per-pattern rule with tests for the cases above.

### KH-748: crystal residue — frequency misparse, no sanity range, CL omits stray capacitance, duplicated leg grouping

**Severity:** LOW
**File:** `detect_crystal_circuits`, SPICE crystal bench
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** frequency misparse (`32768_1206_12.5pF` → 0.0328 Hz, `32.768` → Hz, jotego Y2 400 Hz); no sanity range; the expected CL omits the 3 pF stray; leg grouping is duplicated between the kicad and spice skills.

**Fix direction / budget:** add a sanity range (outside 1 kHz-200 MHz → warn "frequency not a crystal value"); include the stray; share the leg grouping.

### KH-749: Wave 4 Part A follow-up notes (umbrella)

**Severity:** LOW
**File:** `signal_detectors.py`, regulator Vref, `detect_lvds_interfaces`
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

- (a) `_infer_rail_voltage` keeps an unreachable `(\d+\.?\d*)V` pattern (`signal_detectors.py` ~:1524);
- (b) `_datasheet_vref` copies the trust rule (score ≥ 60, current PDF) from `datasheet_features` instead of sharing it;
- (c) `_far_side_is_input` is popped in `_cross_reference_feedback_dividers`, not in presentation;
- (d) `detect_lvds_interfaces` tests value+lib_id while the role reads MPN first (0 corpus).

**Fix direction / budget:** per item.

### KH-751: C14 board contact-model umbrella — pad-to-fill contact misses make `--full` call 11/296 modern boards incompletely routed that kicad-cli reports fully routed

**Severity:** MEDIUM
**File:** `pcb/connectivity.py` (`--full` copper graph), `pcb/geometry.py` (pad contact)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** pad-to-fill contact misses (A10-F2) make `--full` call 11/296 modern sample boards incompletely routed that kicad-cli 10.0.7 reports with 0 unconnected items (m035 m110 m121 m123 m135 m158 m166 m170 m187 m207 m292; e.g. m110 `+BATT`: BT2 contacts 12.85 mm apart joined through the F.Cu fill). Each is a fab-gate FAIL (P17, R64).

**Items:**
- (a) pad-touch over-approximation for trapezoid / chamfer / padstack pads;
- (b) `REF:N#k` keys would collide with a pad literally numbered `1#2` (no corpus instance shown);
- (c) fill-only nodes (entry 50, KH-364);
- (d) A10-F1, A7-F4 (effect 0), A10-F3 / F4 / F6;
- (e) A7-F3: 19/1,116 roundrect VP-001 via centres outside the corner;
- (f) A9-F7: blind-via stub (101 files);
- (g) A9-F8: zone holes (with KH-644).

Home of KH-701, KH-702 and KH-710 (a)(b)(c)(i).

**Fix direction / budget:** each item lands with a rerun of `rc_conf_g.py` and its own budget; A10-F2 first.

### KH-752: the inferred stackup is absent from the output and from EMC

**Severity:** MEDIUM
**File:** `pcb/pipeline.py` (`setup.stackup` / `stackup_source`); `emc/scripts/emc_rules.py` (`_rail_plane_cap_f`, ~:3393-3440)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** `setup.stackup` stays `[]` when `stackup_source` is `inferred` (18 multilayer boards of the 449). EMC `_rail_plane_cap_f` and its εr use no stackup there, while Task 112's return path uses the inferred one, so R51 parity does not hold in EMC. Reach today ≈ 1-2 boards (a 6-layer board infers ≈ 0.27 mm, under the 0.3 mm pair limit).

**Fix direction / budget:** output-shape decision (emit the inferred stackup and feed it to EMC); budget the EMC plane-capacitance consumers.

### KH-753: PM-002 edge-mount exemption keywords miss common mid-mount / edge-launch parts

**Severity:** MEDIUM
**File:** `pcb/assembly.py` (`_EDGE_MOUNT_LIBRARY_KEYWORDS`, PM-002)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (class P9, ruling R52); filed by the harness

**Symptom:** the exemption misses TYPE-C-31-M-13C, PJ-398A, Molex 47272, Switchcraft 35RAPC, GSG-SMA, RJ45 and battery holders: ≈30 overhang errors on 18/300 sample boards. operacake PB0-PB4 edge-launch parts without a courtyard report error 0.0.

**Fix direction / budget:** widen `_EDGE_MOUNT_LIBRARY_KEYWORDS` / values; budget PM-002 disappearances on those parts.

### KH-754: footprints inside ergogen nested modules are missed, and a `locked` reference is misread

**Severity:** MEDIUM (pre-existing)
**File:** `pcb/reader.py` (footprint parse)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** footprints inside ergogen nested modules are not read (boards 67 and 121 of the pcbchecks sample); a `locked` reference is misread (board 69).

**Fix direction / budget:** read nested-module footprints and the locked reference form; budget footprint-derived output on ergogen boards.

### KH-755: EMC IO-001 and `test_plan.interface_risks` list DNP connectors

**Severity:** LOW
**File:** `emc/scripts/emc_rules.py` (IO-001, test plan)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** DNP connectors are listed by IO-001 and in `test_plan.interface_risks` (12 in the sample).

**Fix direction / budget:** skip DNP connectors; budget IO-001 / `interface_risks` removals.

### KH-756: IO-001 and the test plan compare schematic and PCB net names without the net-identity map

**Severity:** LOW
**File:** `emc/scripts/emc_rules.py` (IO-001, test plan)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** schematic and PCB net names are compared literally, without the net-identity map; the effect is missed clears only.

**Fix direction / budget:** compare through the net-identity map; budget IO-001 clears.

### KH-757: a TVS on an unclassified VBUS rail clears IO-001

**Severity:** LOW (reach 0)
**File:** `emc/scripts/emc_rules.py` (IO-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** a TVS on a VBUS rail that is not classified clears IO-001. Reach 0 in the sample.

**Fix direction / budget:** see Symptom; no corpus budget expected.

### KH-758: the schematic PDN counts DNP capacitors

**Severity:** LOW
**File:** `schematic/system_analyses.py` (`analyze_pdn_impedance`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** DNP capacitors take part in the schematic `pdn_impedance` (2/428 rails).

**Fix direction / budget:** skip DNP capacitors; budget `pdn_impedance` on the affected rails.

### KH-759: PDN residue — plane area is the smaller of the two fills, and both sweep grids under-read narrow anti-resonance peaks

**Severity:** LOW (missed direction)
**File:** `emc/scripts/emc_rules.py` (PD-001 PDN sweep), `schematic/system_analyses.py` (`analyze_pdn_impedance`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (class P14a); filed by the harness

**Symptom:** the plane area is the smaller of the two fills (an overlap bound; shapes are not intersected): m222 1V8 has bounding-box overlap 0 and still gets 0.5 pF. Both sweep grids under-read narrow anti-resonance peaks: a 2.431 Ω peak reads 1.96 Ω on the EMC grid and 0.52 Ω on the schematic grid, below its 1 Ω observation threshold.

**Fix direction / budget:** intersect the fill shapes; refine each grid maximum. Budget PD-001 / `pdn_impedance` additions.

### KH-760: schematic PDN observations on VRM rails below ~2 MHz recommend an SRF-matched cap where bulk capacitance or damping is the remedy

**Severity:** LOW
**File:** `schematic/system_analyses.py` (`analyze_pdn_impedance` observations)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** below ~2 MHz on VRM rails the observation says "consider adding cap with SRF near this frequency" (m282 TPS63001 2×100 nF: 631 kHz, 6.23 Ω).

**Fix direction / budget:** word it as regulator output impedance / bulk capacitance; text-only budget on `observations`.

### KH-761: EF input filter counts caps upstream of a rail tap

**Severity:** LOW
**File:** `emc/scripts/emc_rules.py` (EF-001 / EF-002)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (Task 115 M2); filed by the harness

**Symptom:** capacitors upstream of a rail tap count toward the input filter (rail-tap direction).

**Fix direction / budget:** count only caps on the converter side of the tap; budget EF-001 / EF-002.

### KH-762: a custom rule's layer match uses the file's layer names for non-copper legacy layers

**Severity:** LOW (removes only)
**File:** `pcb/presentation.py` (~:279, `board_layers`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** kicad-cli applies a `(layer F.Silkscreen)` hole rule on a board whose layer is `"F.SilkS" user "F.Silkscreen"` (`drill_out_of_range`); we skip it.

**Fix direction / budget:** match rule layers against the canonical (user) layer name as well; budget `design_rule_compliance` additions on legacy-named boards.

### KH-763: a legacy board with a `.kicad_pro` reports project rules it does not use

**Severity:** LOW
**File:** `pcb/dfm.py` (design-rule compliance), `project_settings` output
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** the minima ignore the project (correct), but `rules_source`, `net_class_*` and `project_settings.design_rules` still come from it.

**Fix direction / budget:** report the rules actually used; budget those fields on legacy boards with a project file.

### KH-764: `.kicad_dru` constraint values that are arithmetic expressions are not evaluated

**Severity:** LOW (plan A6-F8 expression half; removes only)
**File:** `pcb/dfm.py` (custom rules)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** values such as `2*0.1mm` stay strings and are not evaluated; an unconditional expression bound makes "cannot judge" replace the board minimum. Reach unknown; 0 unconditional corpus rules in the plan census.

**Fix direction / budget:** report them as "not evaluated" (or evaluate); budget `design_rule_compliance` on boards with expression rules.

### KH-765: custom-rule / annulus edge cases

**Severity:** LOW
**File:** `pcb/dfm.py` (custom rules, annulus), `pcb/reader.py` (`_chamfer_ratio`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** the annulus duplicate-number guard counts all same-number pads (SMD, non-overlapping); `_chamfer_ratio` is read without chamfer corners; `conditional_rules_skipped` lists names when the file is dropped. Unverified against kicad-cli: `6 mil` with a space; whether an unknown rule layer drops the whole file in KiCad; via padstacks (KiCad 9+) judged on F.Cu only.

**Fix direction / budget:** per item; verify the three open points against kicad-cli first.

### KH-766: KiCad flags F and B malformed courtyards separately and still tests the good side; we drop both

**Severity:** LOW
**File:** `pcb/reader.py` (`courtyard_poly`), `pcb/assembly.py` (PM-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** a malformed courtyard on one side drops both sides; KiCad reports each side separately and still tests the good side.

**Fix direction / budget:** keep the good side; budget PM-001 / `diagnostics` on boards with one malformed side.

### KH-767: footprint parse edge cases — first `property` node's last token; footprint-level `(version)` ignored

**Severity:** LOW (reach ~0)
**File:** `pcb/reader.py` (~:466; `_file_version`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** `reader.py` ~:466 reads only the first `property` node's last token (KiCad keeps the last known token across nodes); `_file_version` ignores a footprint-level `(version)` (KiCad takes the max, parser :5163).

**Fix direction / budget:** follow KiCad's token and version rules; reach ~0.

### KH-768: inferred-stackup edge cases

**Severity:** LOW
**File:** `pcb/pipeline.py` (stackup inference)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** a board with no `(setup)` infers 1.6 mm, though KiCad builds the default from the general thickness (`board.cpp:3279-3287`; fixtures only); a B.Cu-only board gets no dielectric (its impedance may vanish), an F.Cu-only board a dangling one; loss tangent is not read. The sublayer εr docstring must not claim KiCad: the thickness-weighted εr is ruling 20's choice (KiCad writes sublayers separately and uses sublayer 0).

**Fix direction / budget:** per item; fix the docstring.

### KH-769: a stackup that lists a board layer twice — KiCad stops at the first repeat, we skip only the repeated layer

**Severity:** LOW
**File:** `pcb/routing.py` (~:564-567, :586-590), `pcb/reader.py`
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** KiCad stops adding stackup items at the first repeat (`pcb_io_kicad_sexpr_parser.cpp:1966-1968, :2062-2085`); `b1a34c2` skips only the repeated layer. One sample board (m271).

**Fix direction / budget:** truncate once in the reader so impedance and the return path agree; budget m271-class boards.

### KH-770: an adjacent layer carrying only a small ground/power patch becomes that layer's return-path reference board-wide

**Severity:** LOW (declared residue, class P12d)
**File:** `pcb/routing.py` (`analyze_return_path_continuity`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** 54 `return_path_continuity` entries on 2 boards take a small adjacent patch as the reference board-wide (pre-existing pick; 4 newly exposed now that tracks no longer cover).

**Fix direction / budget:** a bounded variant (reference only at ≥ 25 % of the largest such layer's area) was measured in the Task 112 review; budget `return_path_continuity` / GP-001 / RP-002.

### KH-771: KH-750 residue in `design_analysis.net_classification` — keyword matching still sees sheet-path and UUID tokens

**Severity:** LOW (no product reader)
**File:** `schematic/net_analysis.py` (`_classify_nets`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (KH-750 residue); filed by the harness

**Symptom:** sheet-path and UUID tokens still match keywords (`central_railcom` → `CE` → chip_select; `_XRXW` ×2 data → chip_select). Real classes lost: `DOUTXBee` ×15 data → signal; `~{UCSE0..3}`, `~{LCSE0..3}`, `~{EXPUCSE*}`, `~{EXPLCSE*}` chip_select → signal (48 nets; a `CSE` keyword would also hit `CSENSE`). Older residue kept (R62): `SHUTDOWN` → debug, `Points` / `INTENSE` → interrupt.

**Fix direction / budget:** classify on `net_leaf`; budget `design_analysis.net_classification` (class P16 shape).

### KH-772: SK-001 sees only board `gr_text` and tests the pad unrotated

**Severity:** LOW-MEDIUM (plan; held by ruling 64)
**File:** `pcb/assembly.py` (SK-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (plan "Part B — Deferred / filed"); filed by the harness

**Symptom:** KiCad's `silk_over_copper` checks footprint fields/text against mask openings (`drc_test_provider.cpp:285-327`, `pad.cpp:1245`). A prototype with footprint silk text + rotated pads gave +224 findings, 89 uncorroborated (mostly mask-covered touch pads).

**Fix direction / budget:** add the mask-opening test first; share the rotated pad outline helper with TV-001. Budget SK-001 appearances ~5-15 % of boards.

### KH-773: `.kicad_dru` `courtyard_clearance` constraints are not applied to PM-001

**Severity:** LOW (plan)
**File:** `pcb/assembly.py` (PM-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (plan "Part B — Deferred / filed"); filed by the harness

**Symptom:** KiCad applies them (`drc_test_provider_courtyard_clearance.cpp:223-228`); we do not. 23 corpus files, mostly conditional.

**Fix direction / budget:** apply unconditional `courtyard_clearance` constraints; budget PM-001 on the 23 files.

### KH-774: add `net_tie_pad_groups` (list) beside the string field

**Severity:** LOW (plan, A7-F5; schema change)
**File:** `pcb/reader.py` (`net_tie_pad_groups`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (plan "Part B — Deferred / filed"); filed by the harness

**Symptom:** only the string field is emitted (ruling 21).

**Fix direction / budget:** add the list field in the next schema-changing release.

### KH-775: EMC `enrich_power_tree_with_pcb` reads `net_name` where the producer writes `net`, so PD-003 never fires

**Severity:** LOW-MEDIUM (plan)
**File:** `emc/scripts/emc_rules.py` (`enrich_power_tree_with_pcb`, PD-002 / PD-003, BE-003)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (plan "Part B — Deferred / filed"); filed by the harness

**Symptom:** PD-003 is dead. Fixing the key alone sums every segment of the rail net in series (m068 `+3V3` 368 mm) and fires at 200-800 MHz without an in-band filter. BE-003 stays on its current input until the via-density ruling (m187 PCIe/USB3 at a 5 GHz knee: λ/20 stitching unachievable). The PD-002 "within target" branch is unreachable and not emitted (ruling 64).

**Fix direction / budget:** a regulator-pad-to-IC-pad path model and a band limit before the key fix; delete the PD-002 branch or make it reachable with a ruling. Budget PD-003 appearances.

### KH-776: design-rule compliance never checks the board-setup minimum annular width

**Severity:** LOW-MEDIUM (plan)
**File:** `pcb/dfm.py` (design-rule compliance)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (plan "Part B — Deferred / filed"); filed by the harness

**Symptom:** KiCad's DRC applies `m_ViasMinAnnularWidth` (default 0.1 mm) and reports `annular_width` violations on 24/299 sampled boards that we do not (compliance vs KiCad annular 1/0/24 YY/Yn/nY, unchanged by Part B).

**Fix direction / budget:** check the board-setup annular width; budget `design_rule_compliance` violations.

### KH-777: TV-001 `drill_penalized` promotion — adequate → good when the effective count dips below the minimum

**Severity:** LOW (plan; pre-existing)
**File:** `pcb/copper.py` (~:803-808)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (class P10); filed by the harness

**Symptom:** m262 U2:15 goes adequate → good when the raw count meets "good" but the effective count dips below the minimum.

**Fix direction / budget:** grade on the effective count; budget TV-001 adequacy on drill-penalized pads.

### KH-778: KO-001 tests a footprint by its bounding box; KiCad by courtyard / pad shape

**Severity:** LOW
**File:** `pcb/` keepout check (KO-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B close triage (KH-575 rider); filed by the harness

**Symptom:** KiCad's keepout test judges a footprint by its courtyard (`pcbexpr_functions.cpp:581-620`) and pads by their shape; we test the footprint bounding box. Boards 27, 89, 148, 239, 261, 278 and 284 of the product's pcbchecks 300 sample still report KO-001 where kicad-cli reports none (residue of KH-575 after Wave 4 Part B Tasks 101 / 105).

**Fix direction / budget:** test the courtyard polygon (pad outlines for pads) as KiCad does; KO-001 removals only, measured against kicad-cli on the pcbchecks sample.

### KH-700: a KiCad `~` empty-field placeholder becomes a BOM footprint / datasheet value on legacy schematics

**Severity:** MEDIUM (false negatives: `statistics.missing_footprint` drops parts that have no footprint; BOM shows `~`)
**File:** `schematic/bom_stats.py` (package fields across units, `9ff9b48` / `4199900`); `schematic/legacy_reader.py` (quoted fields, `f907aa4`)
**Discovered:** 2026-10-27, harness, Wave 3b Part A gate adjudication (residual units, bisected)

**Symptom (two mechanisms, 4 legacy units + 1 modern):**
- Multi-unit merge reads the library DEF's `F2 "~"` / `F3 "~"` (the `.lib` placeholder for an empty field) as a set value: RobertPHeller/RPi-RRCircuits `QuadSMC.sch` U3/U4 LM324N have `F 2 ""` / `F 3 ""` on every unit, the cache DEF has `"~"`, and the candidate BOM row reads footprint `~` / datasheet `~`; `missing_footprint` goes `['R1','U3','U4']` → `['R1']`. Same on cellularmitosis `CSI1802X.sch` (`U?`).
- The legacy quoted-field reader keeps `F 3 "~<newline>"` (a quoted field spanning a line break) as `~`: immortalserg/Ass-shield `nanopi_neo_core.sch` and `v2_nanopi_neo_core.sch` J3 datasheet `""` → `~`.
- Modern: RWeick/FCD-0003.1S-Xplorer64 `FCD-0003.1S.kicad_sch` BOM row J3 datasheet `""` → ` ~` (leading space, so H2's `~` rule misses it) on a duplicated `J3` that merges two different parts (KH-483 rider).

**Fix direction / budget:** treat `~` (after trimming) as empty wherever a library or legacy field is read, as KiCad does; budget: `bom[]` / `statistics.missing_*` on the units above (5 units in the Wave 3b gate).

**2026-10-27 reclassified (product 3.0.x Wave 3b Part B handoff; rulings R33 / R34; `task-kh700-report.md`):**
- (a) The mechanism above is wrong: no library DEF field reaches a component. The `~` is the placed unit's own field (QuadSMC U3/U4 unit 3 carries `F 2 "~"` / `F 3 "~"`, units 1, 2 and 4 carry `""`). KiCad 10.0.7 keeps a legacy field's `~` literally (`sch_io_kicad_legacy.cpp:1279-1373`) and its multi-unit merge takes the lowest unit whose text is not empty (`netlist_exporter_xml.cpp:122-191`), so U3's footprint is `~` in KiCad 10 as well. **Ruling R33: KiCad 10's merge is kept; (a) is the multi-unit form of the R27 `~` class, budgeted, not fixed.** KiCad 5.1.12 voids it (`IsVoid`); that choice is KH-709. Size on the legacy leg sample: 12 multi-unit refs in 3 of 100 roots (5 footprints, 12 datasheets) plus QuadSMC and CSI1802X (`U?`, KH-483).
- (b) **Closed as conformant:** for `F 3 "~<newline>"` KiCad 10.0.7 reads `~\n` and `SCH_FIELD::SetText` strips mandatory fields (`sch_field.cpp:1050-1061`), storing `~` as we do.
- (c) Moved to **KH-708** (KiCad 10 trims the five mandatory fields; RWeick J3 is one part whose Datasheet is `" ~"`).
- Remaining open: none in this entry; it stays as the record of the (a) class until KH-709 is ruled.


### KH-647: DNS rebinding between the download URL check and the connect

**Severity:** MEDIUM
**File:** `skills/datasheets/distributor_core/download.py:100` (`_resolve`), `:112` (`_address_problem`), `:350` (`download_pdf`)
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** `url_problem` resolves the host and requires every address to be public, then requests/urllib resolve the name again when they connect. A server that answers the check with a public address and the connect with a private one (short TTL) passes the policy.

**Fix direction / budget:** connect to the address that was checked (pin the resolved IP, keep the Host header / SNI), on every redirect hop. Budget: output-neutral; the distributor-offline oracle replays recorded URLs, re-check both ways.

### KH-648: download policy: NAT64 / 6to4 / IPv4-compatible IPv6 addresses pass `is_global`

**Severity:** MEDIUM
**File:** `skills/datasheets/distributor_core/download.py:112` (`_address_problem`; only IPv4-mapped addresses are unwrapped at `:109-110`)
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** `ipaddress.is_global` is true for `64:ff9b::/96` (NAT64), `2002::/16` (6to4) and IPv4-compatible `::a.b.c.d` forms that embed a private or loopback IPv4 address, so a host resolving to one reaches the internal address through a translator.

**Fix direction / budget:** unwrap the embedded IPv4 address of those prefixes and apply the IPv4 check to it (or refuse the prefixes). Budget: output-neutral except rejected URLs (diagnostics).

### KH-649: download policy: browser fallback ignores the call deadline until the end, buffers before the size check, and leaves WebSocket / service-worker requests unrouted

**Severity:** LOW
**File:** `skills/datasheets/distributor_core/download.py:521` (`_policy_route`), `:552` (`_download_playwright`), `:565` (`page.route("**/*", ...)`)
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** the Playwright fallback applies the policy through `page.route`, but the per-call deadline is only passed as timeouts to individual steps, the response body is buffered before the byte cap is checked, and `page.route` does not see WebSocket connections or service-worker-initiated requests.

**Fix direction / budget:** enforce the total deadline around the whole fallback, stream or check `Content-Length` before buffering, and block service workers and WebSockets (`service_workers="block"`, `route_web_socket`). Needs a machine with Playwright (the fallback is tested only against a fake module). Budget: output-neutral.

### KH-650: `provider_mouser` fetches the API-provided `ProductDetailUrl` without the download policy or a size bound

**Severity:** LOW
**File:** `skills/mouser/scripts/provider_mouser.py:104-145` (`scrape_product_page`: `requests.get` at `:129`, `urlopen` at `:140`, both `timeout=20`), called with the API value at `:267-268`
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** the product page URL comes from the Mouser API response and is fetched with no `url_problem` check, no redirect re-check and no byte or total-time cap, unlike datasheet downloads since the Wave 1 round.

**Fix direction / budget:** route the fetch through the same URL policy and bounded read as `download_pdf`. Budget: output-neutral; distributor-offline transcripts include this fetch, re-check both ways.

### KH-651: SPICE project-model check is a denylist: XSPICE file-reading models and Xyce / LTspice file-writing cards are not recognised

**Severity:** LOW
**File:** `skills/spice/scripts/spice_model_cache.py:162-195` (`_CONTROL_CARD_PREFIXES`, `_INCLUDE_CARD_PREFIXES`, `model_text_problem`)
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** `model_text_problem` refuses control cards, `shell` / `source` and includes, but XSPICE code models that read files and Xyce / LTspice cards that write files (for example `.print` / `.measure` file outputs, `.wrdata`-style output cards) pass, so an untrusted project `.sub` can still touch files with a simulator other than ngspice.

**Fix direction / budget:** accept only an allowlist of dot-cards in a cached model (`.subckt`, `.ends`, `.model`, `.param`, `.func`, `.global` and the like) and refuse the rest. Budget: output-neutral for corpus units (no corpus unit should ship such a model); run spice-offline both ways.

### KH-652: `datasheet_extract_cache.py` writes fixed `.tmp` names and joins manifest `file` values without containment

**Severity:** LOW
**File:** `skills/datasheets/scripts/datasheet_extract_cache.py:224` (`new_path.with_suffix(".tmp")`), `:267` (`Path(extract_dir) / entry.get("file", "")`), `:496` (`index_path.with_suffix(".tmp")`)
**Discovered:** 2026-10-25, recorded as residue by the product 3.0.x Wave 1 security round (`63f6a20`)

**Symptom:** the two manifest writers open a predictable `*.tmp` sibling (a planted symlink is followed) and the cache reader joins the manifest `file` value without a leaf or containment check, the same class KH-497 closed in the distributor sync manifest.

**Fix direction / budget:** random temp names via `mkstemp`, refuse symlinked leaves, and require manifest `file` to be a plain leaf name inside `extract_dir`. Budget: output-neutral for regular trees.

### KH-646: `distributor_offline._drop_provider_modules` evicts only provider modules loaded from the selected product tree

**Severity:** LOW (dev-only oracle; no in-repo caller mixes trees)
**File:** `tools/distributor_offline.py:223-229`, `:241-242` (`_drop_provider_modules`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R6-F4). Split from KH-626 on 2026-10-25 when the other five findings of that group were fixed on `v3.0.x-dev` (`b3e4954`).

**Symptom:** a provider module preloaded from another product tree survives eviction, so an offline run can execute that tree's adapter instead of the selected one.

**Fix direction / budget:** assert that every loaded provider module lives under `product` (or evict by module name regardless of origin). Product-output neutral; affects only the distributor-offline oracle.

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

**Status 2026-10-25 (3.0.x Wave 2, `c40e135`):** the `actual_caps` order half is FIXED (sorted). Still open: the X5R/X7R digit and `max` quantity parse, and the pooled power-pin nets with no input/output split.

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

**Addendum 2026-10-29 (3.0.x Wave 4 Part B, close-triage rider):** net-class compliance holds micro vias to the class `via_diameter`, and reports net-class track-width / via-diameter violations that KiCad never reports (class values are preferred values, `SetOpt`, `drc_engine.cpp:308-309, 378-379`); MEDIUM. Plan addendum (A6-F6): completing KiCad 6 `classes[].nets` membership would revive these dead loops; decide delete vs info first (ruling 57, `drc_engine.cpp:330-385`).

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

### KH-583: `--schema` marks optional setup keys as required on PCB, and gerber `missing`/`extra` as required although the defaults branch omits them, so most real outputs fail their own schema

**Severity:** MEDIUM (schema contract; 877 of 1,168 corpus PCB outputs with `setup`, and 3,475 of 5,449 gerber outputs)
**File:** `skills/kicad/scripts/envelopes/pcb.py:96-103` (setup requires `pad_to_mask_clearance`, `legacy_teardrops`, `allow_soldermask_bridges`); emitter `pcb/reader.py:76-106` (adds each key only when present; `:42-43` emits `setup: {}` without a `(setup)`); `skills/kicad/scripts/envelopes/gerber.py` (completeness `missing` / `extra` required) vs `analyze_gerbers.py:755-756`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F7, R10 Empirical row "envelopes/gerber.py requires missing/extra")

**Symptom:** 877 of 1,168 corpus PCB outputs (75 %) lack `legacy_teardrops`, 874 lack `allow_soldermask_bridges` and 95 lack `pad_to_mask_clearance`. 3,475 gerber outputs (64 %) lack both `missing` and `extra`. Contract tests pass only because the harness fixture happens to carry all of them.

**Fix direction / budget:** make these fields optional in the envelope dataclasses. Budget: a `--schema` text change only, JSON-neutral. Declare it to the harness (schema artefacts and contract tests re-freeze). Waits on ruling: whether `diagnostics` also becomes schema-required in the same change.

### KH-581: a config section set to `null` crashes thermal, and `_deep_merge` makes `project_config` key order depend on the hash seed

**Severity:** MEDIUM (needs a user-written `.kicad-happy.json`; the corpus has none, so the gate cannot see it)
**File:** `skills/kicad/scripts/project_config.py:258-259` (`_deep_merge` replaces the default `{}` with None), crash at `analyze_thermal.py:1018-1019`; `project_config.py:87-88` (merge iterates a set), emitted at `schematic/pipeline.py:1347-1349`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F6, kc/R13-F5)

**Symptom:** thermal with `--config {"project": null}` (or the same in a discovered `.kicad-happy.json`) raises `AttributeError: 'NoneType' object has no attribute 'get'` at `:1019`. The schematic survives because of a truthiness check at `pipeline.py:1348`. `analyze_schematic.py` on a copied simple-project with a 4-key `project` config gives 4 different `project_config` key orders under seeds 0-3, with identical values.

**Fix direction / budget:** keep the default when a section is null, with a config type warning (the round-9b pattern). Merge keys in a deterministic order. Budget: corpus-neutral (0 corpus `.kicad-happy.json`). The crash becomes a result.

**Status 2026-10-25 (3.0.x Wave 2, `c40e135`):** the `_deep_merge` key-order half is FIXED (deterministic merge order). Still open: a `null` config section crashes thermal.

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

**Status 2026-10-25 (3.0.x Wave 2, `c40e135`):** the `sources_available` order half is FIXED (sorted). Still open: the cold-temperature shortfall sign and the LC-006 week rounding.

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

### KH-574: the `--full` connectivity graph unions a pad with only the nearest track endpoint, uses a max(w,h)/2 circle for pad copper, and leaves `F&B.Cu` pads on a fictitious layer

**Severity:** HIGH (opt-in `--full`; changes `connectivity_graph` islands on 98 of 250 sampled boards / 259 nets)
**File:** `skills/kicad/scripts/pcb/connectivity.py:402` (Phase 2 unions only `_SpatialGrid.nearest`, `:161-174`, and has no segment-interior pass); `:237`, `:401`, `:407-408`, `:26` (pad radius max(w,h)/2, tolerance and clearance, zone probe at 0.85·r); `:100-111`, `:234` (`_expand_copper_layers` does not expand `F&B.Cu`); `:200-213` (layer universe inferred from segments, vias and zones); `skills/kicad/scripts/pcb/geometry.py:316,352` (`CopperPresence` buckets `*.Cu` / `F&B.Cu` literally)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F2, kc/R8-F7, kc/R8-F1)

**Symptom:**
- **Nearest endpoint only:** a three-pad case gives `islands: 2` and `disconnected_pads [['C:1','R:1']]`, and a pad in the middle of a 95→105 track also gives `islands: 2`. Unioning every endpoint within tolerance changes island counts on 98 of 250 random corpus boards (259 nets, an upper bound).
- **Circle surrogate:** a 6×0.4 pad with a 0.7 mm bare gap to a same-net track gives `islands: 1`, because the radius is 3 and the threshold is 3 + 0.1 + 0.12 mm. A real gap is hidden. Consumers are cross_analysis RP-002 (`:614`) and PS-002 (`:754`).
- **Layer wildcards:** an `F&B.Cu` pad with a B.Cu track gives `islands: 2`, and `has_coverage_near(..., 'B.Cu')` over a THT pad is False. This shifts the return-path % in `routing.py:453` (threshold 95 %, `:472`). `F&B.Cu` is the first layers clause in at least 1,026 KiCad-5/6 corpus files.

**Fix direction / budget:** union every endpoint and segment interior inside the pad's real outline (rect/oval/polygon, not a circle). Expand `F&B.Cu` / `*.Cu` from the board layer table in both the graph and `CopperPresence`, and keep KH-417's NPTH type check. Build against a kicad-cli ratsnest/DRC oracle together with KH-364 (fills and arcs). Budget: `--full` only (`connectivity_graph`, PS-002 / RP-002, return-path coverage %), about 40 % of sampled boards. A full-chain profile class. Waits on ruling: R8 O2 (any-net copper credited as a return path), O4 (same-number pads force-unioned at `connectivity.py:346-350`), and O5 (confidence degradation for unmodelled shapes).

**2026-10-26 narrowed (3.0.x Wave 3, `6f99b5c` / `3ad03ec`):** the graph half is fixed — exact pad contact, every touching track, arc tracks, track-track and pad-via overlap, `*.Cu` / `F&B.Cu` expanded from the board layer table, NPTH excluded. Open: the `CopperPresence` wildcard half (`pcb/geometry.py` buckets `*.Cu` / `F&B.Cu` literally) plus KH-417's NPTH check there, held for ruling R8 O2 (any-net copper as a return path).

**Addendum (2026-10-27, product 3.0.x Wave 3b Part B, R8 O4 half):** the held same-`ref:number` force-union (`pcb/connectivity.py`) now also reaches netted NPTH pads with copper (mounting holes are often numbered `""` or `0`). KiCad joins same-number pads only under `duplicate_pad_numbers_are_jumpers` / `jumper_pad_groups`. Measured reach: 2 boards (alexdrymonitis module_specific_board / board2, NPTH pads numbered `0` on GND), where KiCad also reports one GND cluster, so 0 false signals. Belongs with O4.

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

**Addendum 2026-10-28 (3.0.x Wave 4 Part A):** the VBOOT half is fixed by `5c153a7` (output-neutral). The isolator shared-ground and `VBAT_CELLn` halves stay open.

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

**Note 2026-10-25 (product 3.0.x Wave 2):** not part of Wave 2; REPORT-4 A4-F7 (PG -> EN sequencing) stays with the system-analyses group.

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

2026-10-25: left open by the 3.0.x Wave 1 security round (product ruling 3: revisit after KH-442).

### KH-506: the Action report puts raw schematic strings (component values etc.) into Markdown unescaped

**Severity:** MEDIUM (report integrity in PR comments; GitHub sanitises HTML, so no script execution)
**File:** `action/format-report.py:1066` (raw `oa.get('value')`), also `:452-457,629,642-643,1013-1015,1081`; `skills/kicad/scripts/export_issues.py:168-209`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F6)

**Symptom:** a component value or other schematic string containing `|`, newlines, backticks, `[text](url)` or heading markers is placed into a table cell or list line as is, so a PR author can break the report's tables, add links, or forge report sections under the bot's identity. There is no escape helper in the file. `export_issues.py` builds GitHub issue bodies the same way. Should: one Markdown-escape helper for every interpolated analyzer string.

**Fix direction / budget:** one escape helper (table-cell and inline variants) applied at every listed site. Budget: output-changing in rendered report text only for strings containing Markdown-significant characters; needs a text-oracle budget for the `format-report` / `export_issues` artefacts (corpus-neutral).

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

#### Addendum to KH-484 (2026-10-25, product 3.0.x Wave 2)

KH-564 (`57745d5`) reads uppercase `.GL<n>` inner files, so panelized SparkFun-style sets now carry inner-plane extents and gain GR-002 alignment warnings (2 per board); `fab_release_gate` turns them into a `layer_alignment` FAIL. Wave 2 FULL standard gate: GR-002 +32 / -1 over 29 gerber units that read new `.GL<n>` files (e.g. sparkfun SparkFun_GNSSDO `Hardware_GNSSDO_Plus_Production`, `SparkFun_Serial_MP3_Player_Shield-MY1690X`). A size-only comparison flags a panel whose inner planes are smaller than the panel rails; the offset rework here should judge inner planes against the board outline, not the panel extent.

### KH-483: unannotated duplicate references (`U?`, `R?` …) collapse in the detector context and the BOM statistics

**Severity:** LOW (unannotated designs only; sibling of KH-455's `(ref, pin)` dedup)
**File:** `skills/kicad/scripts/kicad_types.py:21` (`comp_lookup = {c["reference"]: c for c in components}` — last wins; both symbols' pins carry `"component": "U?"` via `schematic/connectivity.py:352`), `schematic/bom_stats.py:15-24` / `:59-63` (dedupe by reference, so BOM rows and `statistics` counts drop the duplicates). The `components` list itself keeps both and `schematic/audits.py:29-45` flags them (`duplicate_references` + `unannotated`).
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 4 (review A-I5); verified at `07b7fb1`. Corpus (2026-10-24 scan of the 36,462 schematic outputs, `results/v3_round9b_gate_aux/sec7_sizing.json`): 1,598 units / 466 repos carry at least one `?`-suffixed reference on more than one symbol (`U?` 13,619 symbols, `R?` 9,013, `C?` 7,157, `D?` 3,203, `J?` 1,506, `P?` 1,259, `Q?` 895, `SW?` 664); 5,825 units carry `annotation_issues`.

**Fix direction:** key the detector context by UUID (or `reference#uuid`) and let BOM statistics count unannotated symbols individually. Budget: **corpus-output** on the units above — `statistics.total_components` / `unique_parts`, `bom[]` rows and every detector that resolves a pin's component through `comp_lookup` on those designs (SEED/STRUCT count locks move) — plus KH-455's PP-001 residue class.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part A):** (a) phodina/openwrt-one `bom_fp_bad` 0 → 1: a duplicated `U?` ref merges package fields across different parts once a record carries `_unit_count > 1` (Wave 3b H4). (b) Sorcerer UE9: a duplicated ref whose records are two different parts.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part B):** cross_analysis never treats a blank or `?` reference as multi-unit, and DA-001 keys such parts by `instance_path`, so separate `U?` ICs count separately. Board-side duplicates remain: stanford-ssi Aerolotl U3 ×3 and PocketQube OBC U1 ×2 give one distinct XV-002/XV-003 per footprint (real differences, not duplicates).

**Addendum 2026-10-28 (3.0.x Wave 4 Part A):** ERC `pin_positions` are keyed by (ref, number), so unannotated duplicate refs collapse and hide markers.

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

**2026-10-26 narrowed (3.0.x Wave 3, `6f99b5c` / `3ad03ec`):** arc tracks, track-track and pad-via overlap now join in the `--full` graph. Open: track-in-zone contact (zones still attach only pads and vias) and its KH-422 runtime cost.

---

**Addendum (2026-10-27, product 3.0.x Wave 3b Part B, entry 50):** Wave 3b took only the NPTH half of entry 25 (KH-417). Fill nodes (a zone-fill island as a graph node, so fill-only islands count) are deferred to C14 together with track-in-zone and KH-422's point-in-polygon cost. Survey prototype on the 197-board set: fill nodes alone lower islands agreement 98.6 → 98.1 % (+29 false splits from fills touched only by tracks); with track-in-zone 98.8 %, but graph time 214 → 389 s and two boards past 280 s. Also for C14: the Part B graphic-to-fill join (`2eaad7f`) probes graphic vertices only (KiCad tests the effective shape), so it can only miss a join.

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** the track-in-zone half is FIXED in `1c71826` `f38aceb` (`routing_complete` from the copper graph; track ends join same-net fills; same-number pads join only through copper or jumper settings; `routed_nets` from the graph; kc/R9-F1, rulings R54, R55). Class P11: board agreement with kicad-cli DRC 87.6 → 95.9 % modern, 94.7 → 100 % legacy; runtime at the tip m118 `--full --proximity` 210.6 s (graph 175 s, 75 % of the 280 s cap). Harness gate `d5c500e`..`40b8ff3` budgeted clean. Still open: fill-only nodes (entry 50); their home is the C14 umbrella KH-751.

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

### TH-099: emc / thermal can pair a schematic with an orphan pcb output left over from the pre-hash output naming

**Severity:** LOW (one corpus unit at the 40b8ff3 relock)
**File:** `results/outputs/pcb/` hygiene; the chained runners' sch↔pcb pairing (`run/run_emc.py`, `run/run_thermal.py`) reads any pcb output whose name matches, fresh or not
**Discovered:** 2026-10-29, 3.0.x relock at 40b8ff3 (`results/v30x_w4b_relock/`)

**Symptom:** 93 pcb outputs (81 repos) were not rewritten by the relock because no manifest unit maps to their names any more (outputs named before long output names were hashed). The emc and thermal runners still pair one schematic with one of them: hmaerki/experiment_microoctopus `…Raspberry Pi Zero W.sch` reads `…Raspberry Pi Zero W.kicad_pcb.json` (2026-04-09) while the fresh `…Raspberry Pi Z_b81a647b03.json` exists. The same unit in the gate tree pairs with nothing. The emc runner already retires orphan emc / spice outputs whose schematic output is gone (`RETIRED … schematic output missing/stale`); pcb and gerber orphans (93 / 10) are not retired.

**Fix direction:** retire pcb and gerber outputs that map to no manifest unit (same `.stale` rename as the emc runner), and have the chained runners pair only with outputs whose source is in the current manifest.

### TH-096: the gate's field comparator keeps every delta in memory and writes them all — an output-changing round of ~55 M deltas exhausts a 62 GB box

**Severity:** MEDIUM (blocks the mechanical verdict on large output-changing rounds; the box is shared)
**File:** `regression/field_compare.py` (`compare_trees` accumulates `deltas` and serialises `[d.to_json() for d in deltas]`; `budgeted_report` rebuilds every `Delta`); `regression/run_corpus_gate.py` (`run_modes` runs the comparator with the gate's `--jobs`); `regression/compare_snap_trees.py`
**Discovered:** 2026-10-26, product 3.0.x Wave 3 gate (`results/v30x_w3_gate/`)

**Symptom:** after phases A/B finished, the in-process comparator's 32 workers reached ~67 GB summed RSS, swap climbed 17 → 20.6 GB in 30 s with ~10 GB available; the run was stopped by hand (SIGTERM to its process group, `results/v30x_w3_gate_aux/operations.log`). Sampled estimate: ~55 M strict deltas on schematic units (3,445 per moved unit × 15,884) and ~1.8 M on pcb, before the chained analyzers. No `field_report_*.json` was written. The verdict was produced instead by `results/v30x_w3_gate_aux/stream_budgeted.py` (same `compare_strict` / `evaluate_budget` per unit, counts only), valid because the Wave 3 budget has no `unit_bound` / `expected_magnitude`.

**Fix direction:** stream deltas to a JSONL file and keep counts in memory; evaluate the budget per unit when no class carries a cross-unit bound (bounds can aggregate claimed counts per class); give the comparator its own worker cap.

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

**2026-10-25:** the dead existence-resume plumbing behind the refusal (the worker `resume` argument, the `SKIPPED` branches and counters, `utils.should_skip_resume`) was deleted (arch A1-F6). The refusal stays; identity resume is built fresh from the pattern below.

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

_35 open KH-* + 16 open TH-* issues (2026-10-14: TH-052/053/058 FIXED (H0 plan 1), +TH-060/061/062 filed. Earlier: 2026-10-06: v2.3.1 shipped @ 0684046 and the corpus regen ran CLEAN. Closed this cycle, all in FIXED.md: KH-408..415, KH-418/420 (v2.3.1 batch + follow-up), KH-419/424/425 (SacMap soak fixes), TH-054 (run_emc crash masking). Open KH: 328..334 datasheets-infra backlog; 355/364/365 audit remainder; 403/404 HIGH connectivity over-unions; 416/417 v2.3.1 riders; 421 Marble hash-seed nondeterminism; 422 `--full` point-in-polygon cost; 423 legacy `.sch` empty fields; 426..440 SacMap soak long tail; 441 via_in_pad attribution; 442 behavioral opamp gain 0. Open TH: 037..042/044/047 legacy; 049 contamination tripwire; 055 timeout-class v1.3-era pcb outputs (191 boards); 056 KH-313 anchor; 057 bugfix generator merge-by-id; 059 batch SPICE hermeticity; 060 kh393 power-rails test premise stale (strict xfail); 061 test_datasheet_db_cli writes repos/.test_fallback; 062 print-and-return vacuous skips in smoke files. Earlier history: 19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
