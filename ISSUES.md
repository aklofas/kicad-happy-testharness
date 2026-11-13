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

Last updated: 2026-11-13

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-1103** (KH-1080..1102 filed 2026-11-13 by the harness from the v3.0.2 Wave 11c handoff, each verified at `db551674` (KH-1088 / KH-1089 fixed in the range, filed straight to FIXED.md); KH-1073..1079 filed 2026-11-11 by the harness from the product's TH-109 rulings, each re-verified by re-running the analyzer at `6138b126` — keyword-only regulators on uncached KiCad 5 libraries, discrete ORing / backfeed diodes in no detector, TVS keyword gaps (SMF/SM6T/SM712, MEDIUM), the HX711 regulator dropped by the op-amp/ADC exclusion, ESD-array `clamp_net` null, buzzer driver on the other pin, I2C pull-ups through 3-pad solder jumpers (MEDIUM); KH-1070..1072 filed 2026-11-11 from the TH-109 triage — `kicad_version` unknown without `generator_version`, BUZ11 FETs missing from transistor circuits, `single_pin_nets` duplicate `nets` key; KH-1068 / 1069 filed 2026-11-08 from the KH-755 / KH-480 closure reads — schematic-only DNP connectors, machine-dependent failed-run diagnostics; KH-1040..1067 filed 2026-11-08 by the harness at the product v3.0.2 Wave 11b-2 gate (unreleased, candidate `6138b126`) — the handoff's new-KH slugs, the ruled `es001-dnp-protection` slug its list dropped, and two residues found verifying the KH-573 / KH-713 closures, each claim re-read at the candidate; KH-1039 filed 2026-11-07 on the user's Wave 11b-1 ruling — no annotation for a duplicate `Value` property, the Eagle-import hidden empty copy that KiCad 10 reads; KH-994..1038 filed 2026-11-07 by the harness at the product v3.0.2 Wave 11b-1 gate (unreleased, candidate `f53d107e`) — the handoff's new-KH slugs plus the survey asks it dropped, each claim re-read in the candidate with probes and corpus snaps (several corrected: legacy `.sch` runs no system-level analyses, every GOST `VD`/`VT` reference typed varistor, MIC2305x dropped by a "load switching" substring, RM-DET `sma` matching `*_Small`), plus two false VM-001 adds from the gate and three closure residues; addenda on KH-925 (x3), KH-447, KH-654; 46 entries FIXED in Wave 11b-1 (KH-993 on the harness release-gate rerun), 16 partly fixed with addenda, see FIXED.md; KH-993 filed 2026-11-06 by the harness from the release-gate `RealPlaywrightTest` run at `a8207138` — the browser fallback never saves a direct PDF, Wave 11b list; KH-991 / KH-992 assigned FIXED-direct 2026-11-06 from the Wave 11a handoff — Windows CRLF stdout, JLCPCB translator LCSC part number, see FIXED.md; KH-980..990 filed 2026-11-06 by the harness at the product v3.0.2 Wave 11a gate (unreleased, candidate `5510006a`) from the handoff's new-KH list, each claim re-read in the candidate with probes — thermal extraction reader, `analysis.output_dir` containment, trusted-model `.end`, NaN/bool voltage overrides, lifecycle `X7R, 50V` split, Deep Review `not_found` fallback, `find_extraction` underscore collision, SPICE fetcher own lookup, NaN quality trust, VM-001 open-drain status pins, Action ordered-list lead; the `.kicad_dru` candidate is a KH-924 addendum (comma decimals refuted), the ground-name candidate a KH-925 addendum; KH-329..970 (83 entries) FIXED in v3.0.2 Wave 11a, see FIXED.md; KH-634 / 647 / 906 / 965 claimed fixed but partly fixed, KH-482 / 495 / 496 / 554 / 559 / 743 / 805 / 872 / 914 / 924 / 973 partly fixed as declared, addenda on each; KH-974..979 filed 2026-11-06 from the product's v3.0.2 survey candidates, each verified by the harness at `4c2a0d6` (the LTspice/Xyce exponent crash is a KH-743 addendum, the corpus capability sidecars a KH-793 addendum); KH-968..973 filed 2026-11-06 by the harness from SacMap rev2 soak run 11 at the v3.0.1 release `7d9d4d9f`, each verified by code read there — footprint keepouts never read, GP-001 per-net 95 % threshold without gap location, lifecycle MPN-only search, XV-004 blank-MPN / distributor-PN sub-cases, silent capability-loss diagnostics umbrella, `diff_analysis` tool-version grading and missing gerber / cross_analysis diffs; addenda on KH-433, KH-930, KH-462; KH-967 filed 2026-11-06 from the product ruling on the Wave 10b gate — `<n>V<n>_N` split rails read positive, verified in the candidate; KH-957..966 filed 2026-11-05 by the harness at the product 3.0.x Wave 10b gate (unreleased, candidate `2abc8496`) from the handoff's new-KH list, each claim re-read in the candidate — PM-001 ignores `drc_exclusions` (the handoff's graze-tolerance cause refuted: 0.119 mm overlaps) and both-layer tie order, duplicate courtyard outlines without `malformed_courtyard`, RP-001 power / high-speed classifiers, VS-001 branch disagreement (vias but no ground via), RP-002 `ran: true` without coverage, pin-only regulator outputs leaving `rail_voltages`, power-budget LDO sign guard, `VSS*` as ground for EN, DFM vs market-inferred IPC class, op-amp dead-output gain error (the 0.00 dB half refuted: deliberate below-minimum demotion); KH-947..956 filed 2026-11-05 by the harness at the product 3.0.x Wave 10a gate (unreleased, candidate `e60d03b5`) from the handoff's new-KH list, each claim re-read in the candidate — nested `.kicad_dru` bound ignored, `analysis: null` / non-string power_rails patterns, BOM-prefixed config, `RecursionError` at ~45 JSON loads, `--v14` null pin, Deep Review split exponent, SPICE LCSC `mfr`, Action residue, fab gate text, lazy `kicad_core.executables` import; addenda on KH-924 (nested condition) and KH-910 (still present); KH-915..946 filed 2026-11-04 by the harness at the product 3.0.x Waves 9b + 9c gate (unreleased, candidate `8c42799`) from the handoff's new-KH list, each claim re-read in the candidate — KH-920 filed FIXED-direct (load switches typed LDO, see FIXED.md) and KH-946 its open residual (dual-switch pin pairing); KH-912..914 filed 2026-11-03 by the harness at the product 3.0.x Wave 9d (docs) gate (unreleased, candidate `389fbd5`) from the handoff's new-KH list, each re-read in the candidate — gerber X2 docstring, unverified gerber version rows, raw `<MPN>` schema / provider text; KH-904..911 filed 2026-11-03 by the harness at the product 3.0.x Waves 9a + 9e gate (unreleased, candidate `6009004`) from the handoff's new-KH list, each claim re-read in the candidate — SPICE model-manifest reset, silent stale for PDFs outside `datasheets/`, `load_manifest` FIFO, abandoned download thread, LTspice/Xyce metadata, Action Top Risks severity, `test_cache_reader` isolation, deep-review partial pin names; KH-870 FIXED in 3.0.x Wave 9a, see FIXED.md; KH-895..903 filed 2026-11-03 by the harness on the product's request from SacMap rev2 soak run 10 at `07b7fb1` (v3.0.0 release base), each verified by code read at `07b7fb1` and v3.0.x-dev `5687ee1` — TE-001 touch pads, lifecycle `sources_available`, LC-007 contradiction, LC-004 multi-MPN wording, report-section gate, SPICE simulator version, two run ids, `power_domain` warning dedup, SKILL.md migration note; KH-894 filed 2026-11-03 by the harness on the product's request after the Wave 8c + 8b acceptance — supply-rail recognition by name only, su-pcb decoupling → rc_filter under KH-800's KiCad names; KH-867..893 filed 2026-11-03 by the harness at the product 3.0.x Wave 8c + 8b gate (unreleased, candidate `0efc012`) — KH-867..873 from the 8c handoff (other `--output` CLIs, `/dev/` link write-through, raw pipeline cache reads, PDF FIFO hash hang, Windows identity fallback, wrong-part `ok` refresh, Windows replace-onto-open-file), KH-874..892 from the 8b handoff (bus members as naming candidates, VM-001 cascade / multi-unit voltage, `4.5V-28V IN` rail, `SCLn`/`SDAn`, legacy and multi-root tie-break, stripline, plain `routing_complete` wording, ferrite `@` / `0R/2A` parsing, HS classifier, split-detection geometry gaps, SW-003 dead note), KH-893 by the harness (text-oracle jlcsearch call); each claim re-read in the candidate; KH-806/791/811/797/807/813 FIXED in 3.0.x Wave 8c and KH-851/820/825/863/850/800/864 FIXED in 3.0.x Wave 8b, KH-795 narrowed to the void half, KH-643 addendum, see FIXED.md; KH-863..866 filed 2026-11-02 by the harness at the product 3.0.x Wave 8a gate (unreleased, candidate `647bc85`) from the handoff's new-KH list, each claim re-read in the candidate — OR-001 angle rounding, EMC limit band edges, the Action's no-op `derating-profile`, what_if no-affected `--output` stdout; KH-818/819/821/822/826/827/828/849/852/853/854 FIXED in 3.0.x Wave 8a, KH-814 narrowed to the schematic / PCB `error` opt-in half, see FIXED.md; KH-829..848 assigned FIXED-direct 2026-11-01 from the product 3.0.x Wave 7 (architecture) close handoff (unreleased, candidate `988d576`) — the range's output-neutral slugs, each landed and closed by its named commit: UTF-8 register sites, dead `NetlistQueries` surface, dead core helpers, unread what-if / thermal / cross inputs, dead provider members, EMC severity-map duplicate, dead datasheet v2 validator / SPICE tables / smoke check, named-pin net / `pin_nets` annotation / S-expression property-decode duplicates, lifecycle derived writer, dead cache / context helpers, run-folder name, verifier helper names, detector netlist inline, lifecycle engine owner, PCB `--schema` thickness / `via_analysis` text, `summarize_findings` help vocabulary, see FIXED.md; KH-659 FIXED in 3.0.x Wave 7, see FIXED.md; KH-849..854 filed 2026-11-01 from the Wave 7 handoff's found-and-not-fixed list (each output-changing) — ~45 more locale-default text sites, ferrite `600R/200mA` parsed as 600 Ω, `(general (thickness))` dropped without `(setup)`, the Action's EMC / thermal "blocking findings" notice (thermal twin added by the harness), LC-007 text naming `lifecycle_audit.py`, undeclared `fix_params`; KH-855..862 filed 2026-11-01 from the Wave 7 deferred-by-ruling list — detector-family move, what-if engine extraction, vendor clients, PCB point-to-segment merge, SPICE kind registry, Action Python runner, `build_connectivity_graph` move (harness patch targets first), Phase 4 exercise script; KH-814..828 filed 2026-11-01 by the harness at the product 3.0.x Wave 6 (docs) gate (unreleased, candidate `c0a8a62`) from the handoff's new-KH list, every claim re-read in the candidate — Action `has-critical` / `findings-count` scope with the retired `voltage_derating` read (MEDIUM), per-CLI output-flag precedence, TW-001 width-table provenance, SPICE extraction-tier key and `meta` mismatch, EMC score after `--severity`, typed-lookup parent-folder cache (Security, MEDIUM, KH-782 residue), microstrip impedance on bulk εr (MEDIUM, output-changing under `--full`), five undeclared PCB envelope keys, silent missing `--config`, Action EMC/SPICE base lanes, Mouser default delay, PCB routing note as a `ValueError` diagnostic, what_if / detector `vref_source` confidence, what_if sweep `±tol` and `--output`; KH-636, 637, 638, 639, 640, 641, 642 FIXED (docs) in 3.0.x Wave 6, see FIXED.md; KH-329 doc halves fixed, entry narrowed to the `--use-cached-scout` traceback; addenda on KH-592 and 554, and on KH-633 in FIXED.md; KH-780..790 assigned FIXED-direct 2026-10-31 from the product 3.0.x Wave 5 handoff (unreleased, candidate `698116c`) — generic-transistor audit sync-manifest `parts`, multi-unit IC verification, extraction caches from a shared temp / parent directory (Security), review-plan run dir, Gerber job-file inner-layer completeness, Gerber X2 reader, Gerber drill model, empty return-path result (GitHub #60.1), `--gp001-debug` path (#60.4), Type-C detection (#61.2), degenerate switching-loop area (#62); KH-330, 484, 488, 571, 572, 577, 578, 579, 580, 595, 596, 600, 601, 602, 603, 604, 605, 614, 615, 616, 617, 620, 621, 622, 624, 625, 633, 646, 652 FIXED in 3.0.x Wave 5, see FIXED.md (commit-message omissions recorded under KH-571 / 572 / 578 / 617 / 646 / 652 / 781 / 786); KH-492, 606, 634, 636, 637 partly fixed (entries stay open with addenda); KH-791..813 filed 2026-10-31 from the Wave 5 handoff follow-ups — `analysis/manifest.json` 0600, SPICE model cache in a shared cwd, `capability_mode` cwd output, relative `inputs.source_files`, reference-net change under a trace (GitHub #60.2/#60.3, MEDIUM), pad-based hot loop, non-atomic `merge_results`, extraction lookup order, multi-condition SpecValue, root-sheet order dependence (MEDIUM), back-mounted THT side, Gerber outline choice, nightly job ids, Type-C CC reader, lifecycle / gerber carry-forward, `--output` atomic writes, spaced `±` in the Deep Review gate, family digit boundary, unnamed supplier slot, DNP value markers, cache-read nofollow, `export_issues` paging, orphan PDF on `--force-all`; addenda on KH-487 (GitHub #61.3), 585, 592, 495, 606, 634 (and 492, 636, 637); note on KH-522 (GitHub #61.1, already fixed); KH-779 filed 2026-10-29 from the product ruling on the 3.0.x relock FND locks — RT-001 gives no hint when a net's zones are unfilled, LOW; addenda on KH-484 (5 FND ids kept failing) and KH-685 (stacked NC pins, RTK Facet); KH-751..777 filed 2026-10-29 (+ KH-778 filed by the harness for the KH-575 KO-001 bounding-box residue) from the product 3.0.x Wave 4 Part B handoff — C14 board contact-model umbrella KH-751 (pad-to-fill misses, 11/296 false-incomplete boards; home of KH-701/702/710 (a)(b)(c)(i)), inferred stackup absent from output and EMC, PM-002 edge-mount keywords, ergogen nested modules / locked reference, IO-001 DNP / net identity / unclassified VBUS, schematic PDN DNP caps, PDN plane-area and grid residue, low-frequency PDN wording, EF rail-tap direction, legacy non-copper rule layers, legacy project rules reported, `.kicad_dru` expressions, custom-rule / annulus edge cases, per-side malformed courtyards, footprint parse edge cases, inferred-stackup edge cases, repeated stackup layer, small-patch return-path reference, KH-750 residue KH-771, SK-001 footprint text / rotated pads, `courtyard_clearance` for PM-001, `net_tie_pad_groups`, PD-003 dead key, board-setup annular width, TV-001 `drill_penalized`; KH-427 and 750 FIXED in 3.0.x Wave 4 Part B (unreleased, candidate `40b8ff3`), KH-364 track-in-zone half and KH-710 (d) fixed (entries stay open), KH-417 return-path half closed by construction (addendum on the FIXED entry), see FIXED.md; KH-711..749 filed 2026-10-28 from the product 3.0.x Wave 4 Part A handoff — case-insensitive mandatory fields, PCB rail set from board nets, op-amp bench below the feedback pole (gates KH-507), PNP bench never on (MEDIUM), P-ch `vth_V`, SPICE presence passes (KH-618 remainder, MEDIUM), `is_power_net_name` signal suffixes stop divider chains (MEDIUM), family Vref table values (MEDIUM), rail-sign readers (KH-675 remainder), CAN split termination (MEDIUM), VM-001 PG exemption unconditional, label-like regulator values, field-trim residue (KH-708 residue), reference nodes as rails, pre-KiCad 7 PCB rule / EG-001, `/x/PGND`, `ctx.rail_by_net` phase order, config-override consistency, regulator/half-bridge misdetections, DO-DET provenance, Vref rows awaiting datasheets, diff-pair ESD / USB-name / SPI-CAN / I2C VOL / family nickname / ERC / RC / LED / COMP / domain-advisory residues, alternate SPICE backends, op-amp `supply_min`, Monte Carlo parallel arms, bench-input residue, Vref key core cut, crystal residue, follow-up umbrella KH-749; KH-750 filed 2026-10-28 by the harness at the Wave 4 Part A gate — `/fpga-pg5/VCCINT` classed `interrupt` once KH-678 drops its rail match (KH-678 census); KH-675 (partly, → KH-719), 678, 699, 705, 708 (residue → KH-723), 672, 442, 676, 611, 612, 618 (partly, → KH-716), 619, 539, 669 FIXED in 3.0.x Wave 4 Part A (unreleased, candidate `b31d4ff`) and KH-709 closed as answered by ruling entry 54, see FIXED.md (commit-message corrections recorded under KH-675 / 678 / 676, the KH-509 CHANGELOG slip under KH-669); addenda on KH-548 / 667 / 483 / 707; KH-701..710 filed 2026-10-27 from the product 3.0.x Wave 3b Part B handoff §Asks 4 — net propagation onto net-less copper, custom-pad residue, instance-aware property writers, JLCPCB CPL convention reference, analyzer sheet-file case / KiCad 6 value settle, bom_manager diagnostics, unit-count semantics, mandatory-field whitespace trim, KiCad 5 `~` ruling question, follow-up umbrella; KH-417 / KH-426 FIXED in 3.0.x Wave 3b Part B (unreleased), see FIXED.md; KH-700 reclassified (R33 / R34: (a) budgeted class, (b) conformant, (c) → KH-708); addenda on KH-574 / 364 / 483; KH-699 / KH-700 filed 2026-10-27 by the harness at the Wave 3b Part A gate — `D_Zener` from an `*LED*` nickname typed `led` (false LR-001), `~` empty-field placeholder kept as a BOM footprint/datasheet on legacy schematics (MEDIUM); KH-679..698 filed 2026-10-27 from the product 3.0.x Wave 3b Part A handoff §Asks 4 — sibling-sheet driver ties, bus member fallbacks, hierarchical-label ERC, ktiger hierarchy join, PU-001 `MISO`, DO-DET port-name exemption, wired NC pins, bus group/quoted/mixed parsing, `~` pin names, bus-member naming, brace decode table, multi-root projects, unresolved text variables, CG-AUD by name, sheet-pin shape preference, follow-up umbrella KH-695; addenda on KH-483 / 667 / 669 / 671 / 677; KH-403 / KH-404 FIXED in 3.0.x Wave 3b Part A (unreleased) and KH-664 closed as conformant, see FIXED.md; KH-662 completion addendum in FIXED.md; KH-678 filed 2026-10-26 at the Wave 3 verdict — sheet net promoted to power by a same-named rail elsewhere (`/HVIL/HVIL_N`), Wave 4 group 1; KH-663..674 filed 2026-10-26 from the product 3.0.x Wave 3 handoff §Asks 4 — legacy buses, `E` decimal mark, EMC BE-001 origin distance, footprint Edge.Cuts outline, VM-001 heuristics, CS-DET set order, root hierarchical label fusion, LR-001 resistor association, same-net pad overlap, follow-up umbrella; KH-675..677 filed 2026-10-26 by the harness at the Wave 3 gate — negative regulator estimates on positive-named rails (Wave 4 group 1), SPICE zero-step transistor sweep (the spice-offline candidate failure), six legacy boards worse against their KiCad-5 netlist; KH-510..519, 560, 575, 576 FIXED in 3.0.x Wave 3 (unreleased) and KH-662 / 668 / 670 assigned FIXED-direct, see FIXED.md; KH-574 / KH-364 narrowed; KH-404 re-verified (reproduces); KH-653..661 filed 2026-10-25 from the product 3.0.x Wave 2 handoff §Asks 4 — `PH0`/`PH1` read as a regulator SW pin (MEDIUM), `RF-C10` typed resistor, EG-001 / GR-005 / CC-001+TW-001 follow-ups, `ThermalSkipped.reason` description, dead `has_esd` line, cross_verify keep/retire, LOW; KH-655 assigned FIXED-direct (test-plan / op-amp 2-hop / what_if order, fixed on discovery); KH-563..570, 582, 584, 591, 509, 607, 421 FIXED in 3.0.x Wave 2 (unreleased), see FIXED.md; KH-620 / 581 / 579 narrowed to their non-order halves; addenda on KH-484 and KH-529; KH-647..652 filed 2026-10-25 from the product 3.0.x Wave 1 residue — DNS rebinding (MEDIUM), NAT64/6to4 `is_global` bypass (MEDIUM), browser-fallback deadline/buffering/WebSocket gaps, `provider_mouser` unbounded `product_url` fetch, SPICE model denylist, `datasheet_extract_cache` fixed temp names / unchecked manifest joins, LOW; KH-497..505 FIXED in 3.0.x Wave 1 (unreleased), see FIXED.md, KH-507 left open by that round; KH-646 filed 2026-10-25 — split from KH-626 at the 3.0.x Wave 0 handoff: `distributor_offline` evicts only the selected tree's provider modules (sk/R6-F4), LOW; KH-626 FIXED on `v3.0.x-dev` `b3e4954` except that finding, see FIXED.md; KH-645 filed 2026-10-25 by the harness audit fix session — netlist oracle m68k-hbc splits 16 `/Bus/PEP/AD*` nets (oracle 4/5 since at least `0490c49`), MEDIUM; KH-644 filed 2026-10-25 by the harness audit fix session — PCB zone `fill_ratio` sums every filled layer over one layer's outline (1.83 on a two-layer zone), LOW, surfaced when the assertion engine stopped truncating fractional values; KH-643 filed 2026-10-25 by the main-repo agent — EMC SW-001 ignores `--standard` and discards its harmonic amplitude, MEDIUM; KH-497..642 filed 2026-10-25 from the external audit round 1 at `07b7fb1` — 30 static reviews in five bundles, every finding re-verified against the code, one entry per fix group; records and the wave plan in the main repo at `docs/audit/FIX-PLAN.md` and `docs/audit/0*/findings/VERIFICATION.md`; addenda added to KH-329, KH-331, KH-428, KH-432, KH-433, KH-437, KH-439, KH-442, KH-443, KH-470, KH-481, KH-482, KH-484, KH-487, KH-494; KH-480..496 filed 2026-10-24 from the v3 round-9b handoff §7 — the review-period bug-hunt deferrals, every claim re-verified in source at `07b7fb1` (19 confirmed / 4 partly), each with its budget or oracle re-freeze: failed-SPICE-run diagnostics (93 units), missing-sheet / truncated-input diagnostics, unannotated duplicate-ref collapse (1,598 units / 466 repos), GR-002 extents-only (MEDIUM), root-only `inputs` (4,261 multi-sheet units), suppressions only in EMC/thermal, `--parasitics` verbatim names, Mouser `""` key (4 frozen runs), SPICE cache hygiene, EMC `--severity` vocabulary, analysis_cache M3/M4, DigiKey 429, Action diff-base, three review-minor umbrellas; KH-479 assigned FIXED-direct 2026-10-24 to the review-period Critical A-C1 (analysis-dir containment, new in v3, fixed before release — see FIXED.md); KH-477 / KH-478 / KH-446 FIXED in round 9b (`cd2e49b` / `c6f4807`), KH-447 resolved for LT3514, see FIXED.md; KH-478 filed 2026-10-24 from the v3 round-9 handoff §11 — `emc_spice.run_distributed_pdn_spice` measurement tuples in the wrong shape → always `(False, None)`, temp dir never removed, no product caller, LOW; KH-472 / KH-464 / KH-466 / KH-475 FIXED in v3 round 9 (`ec81ca6`), see FIXED.md; KH-477 filed 2026-10-24 while fixing TH-077 — the SPICE model cache falls back to one global `/tmp` directory because `analyze_schematic.py` strips `file`; non-atomic manifest, cross-project leakage, LOW; KH-476 filed 2026-10-24 during the Checklist 11 `_KNOWN_FREQS` verification — the TPS62160 / TPS63000 keys miss the siblings of their own datasheets, 31 regulator findings default to 500 kHz, LOW; KH-470..475 filed 2026-10-23 from the v3 round-8 handoff §11 — thermal `title`+`summary` twin, `export_issues` severity vocabulary, `emc_spice.py` unquoted redirect without `cwd` (KH-463 sibling), RS-001 "carries power_in pins" wording on a name-admitted bootstrap-only rail, `lifecycle_audit` without `diagnostics`, Monte-Carlo per-trial fallback stderr noise; all pre-existing at `a0df172`, LOW; KH-454 / KH-455 / KH-463 FIXED in round 8 (`6222468`, `c598140`), see FIXED.md; KH-469 filed 2026-10-23 during the Checklist 11 SWITCHING_EFFICIENCY verification — three of the four `analyze_thermal.SWITCHING_EFFICIENCY` keys are unreachable and the schematic detector carries a third, different efficiency table; `ic_with_internal_regulator` regulators are costed as 85 %-efficient switchers, LOW; KH-468 filed 2026-10-23 during the Checklist 11 ADC-map verification — `_ADC_RESOLUTION_MAP` 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist, LOW; KH-467 filed 2026-10-23 during the Checklist 11 backlog pass — three divergent LED forward-voltage tables (`_LED_VF` / `_LED_VF_FLOOR` in domain_detectors, `_LED_VF_BY_COLOR` in validation_detectors) disagree per colour, LOW; KH-464..466 filed 2026-10-23 from the v3 round-7 handoff §11 — lifecycle_audit missing-input traceback, `is_cross_analysis_ground_name` exact-set policy (SGND/GNDPWR/GND_ISO/VSSA/`/Power/GND` not ground), `analyze_gerbers` exit 0 on a nonexistent dir; all pre-existing, verified at 0490c49, LOW; KH-463 filed 2026-10-23 at the v2.3.2 corpus regen — SPICE testbench `.control` `echo … > <path>` redirect unquoted, every measurement silently skips when the workdir path has whitespace or `,`/`&`/`'`/non-ASCII, the user-facing `analysis/<run>/spice_work/` default inherits the project path, MEDIUM; KH-456..462 filed 2026-10-22 from the SacMap rev2 run-9 soak at the v2.3.2 pre-tag `4701c26` — fab_release_gate counts `G***` logo footprints (false FAIL), silk revision regex misses `rev2`, `capability_mode` `datasheet_coverage_pct` is a hard-coded stub, `audit_pwr_flags` ignores `power_in` pins off named rails (ERC `power_pin_not_driven` ×3 unseen), EMC DC-002 fires on a part-numbered ESD array (dupes UC-001), `cross_domain_signals.needs_level_shifter` stale after KH-424, `datasheet_verify` rc 1 for warnings; riders on KH-431/432/436; all code-verified by the main-repo agent; KH-455 filed 2026-10-22 at the v2.3.2 backport gate — PP-001 `(ref, pin_number)` dedup masks a second symbol's power pin on unannotated `U?` designs, the gate's one residue unit, LOW; KH-454 filed 2026-10-22 at the v2.3.2 backport adoption — RS-001 fires on a bootstrap-only net whose sole `power_in` pin is the BST/BOOT pin, LOW, with the two GitHub #55 riders; KH-450..453 assigned 2026-10-22 FIXED-direct — GitHub #52–#55 / PRs #56–#59 by EldarPolitkin on `main` @ 4701c26, see FIXED.md; KH-449 filed 2026-10-16 at the v3 round-5 full-chain gate — pcb `--full` exceeds the 600 s cap on starshipraider MAXWELL both sides, LOW; KH-447 addendum: LT3514 is a ≥ 20 GB memory blow-up, OOM-killed under the 600 s cap; KH-448 filed 2026-10-16 at the v3 round-4 gate — hierarchy-mode `analyze_schematic.py` ~3 GB RSS on BerkeleyLab/Marble, both sides equal, LOW; KH-446/447 filed 2026-10-15 at the v3 round-2 reply per ruling Q3 — empty-input pcb traceback (hackclub/OnBoard placeholders), schematic 120 s timeouts on three hierarchical roots (discrete-nes ×2, LT3514); KH-445 filed 2026-10-15 at H0 plan 4 — `EQ-042` tags two different equations, LOW; KH-444 assigned 2026-10-14 FIXED-direct — PR #51 AM-001 `<domain>_max` key lookup, imrcly, see FIXED.md; KH-443 filed 2026-10-14 from GitHub #50 — net ties not bridged by RS-001/PP-001 DC-continuity audits, MEDIUM; KH-442 filed 2026-10-06 at the v2.3.1 regen — behavioral opamp model gain 0 false SP-WARN; KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
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
KHPA finding ID). Next TH number: **TH-112** (TH-049 and TH-063 FIXED 2026-11-11, TH-109 and TH-064 FIXED 2026-11-11, see FIXED.md; TH-111 filed 2026-11-11 from the TH-109 triage — check paths cannot reach dotted net names, LOW; TH-110 filed 2026-11-07 at the v3.0.2 Wave 11b-1 registry rescan — `audit_constants.py` reuses retired `CONST-NNN` ids for new constants, LOW; TH-109 filed 2026-11-06 from the TH-105 triage — 144 live FND locks with a check shape that cannot fail or reads the wrong finding; TH-107 / TH-108 filed 2026-11-06 at the v3.0.2 kickoff while classifying the nine standing non-passing locks for VALIDATION.md — 36 assertions never load their output (2 from a doubled `file_pattern` prefix), and the nine standing locks were never reviewed (7 stale, the analyzer now matches KiCad); earlier: TH-106 filed 2026-11-03 — `generate_analytics.py` issue counts read only `### <id>` headings, the TH-104 undercount in a second tool, LOW; TH-105 filed 2026-11-03 at the v3.0.1 regen — 360 FND locks on INCORRECT-marked findings are not aspirational, some pin the reported defect (six caught as Wave 5 KH-484 `aligned` flips); audit + rule recorded, MEDIUM; TH-104 filed and fixed 2026-11-03 at the v3.0.0 release prep — `generate_validation_md.py` counted only `### <id>` headings, so `## <date> — <id>` closures were dropped and the filed total shrank, see FIXED.md; TH-103 filed and fixed 2026-11-03 at the Waves 8c + 8b push — the hash-seed determinism test compared `elapsed_s`, see FIXED.md; TH-102 filed and fixed 2026-11-01 at the 3.0.x Wave 7 close — the fixture set had no multi-unit schematic (a placed symbol with unit > 1), so product `test_model_records` could not pin per-unit records; `tests/fixtures/multi-unit/dual_opamp.kicad_sch` + `tests/test_multi_unit_fixture.py`, see FIXED.md; TH-101 filed 2026-10-31 at the 3.0.x Wave 5 gate — no profile exercises gerber `--full` connectivity, the Task 52 class is gate-blind harness-side, LOW; TH-100 filed 2026-10-29 at the relock rulings — 235 aspirational FND assertions use operators `checks.py` does not know; TH-099 filed 2026-10-29 at the 3.0.x relock — emc / thermal pair a schematic with an orphan pre-hash pcb output; TH-098 filed and fixed 2026-10-26 — tool-gated skips (pdftotext / ngspice) failed the required-tier skip guard on runners without the tools; listed in `tests/known_skips.json`, see FIXED.md; TH-097 filed and fixed 2026-10-26 — `run_spice.py` checked for ngspice before validating the selection, product CI red at pin `bd551df5b41`, see FIXED.md; TH-096 filed 2026-10-26 at the Wave 3 gate — the field comparator holds every delta in memory, ~55 M deltas exhausted the box, MEDIUM; TH-095 filed and fixed 2026-10-26 — `run_netlist_oracle.py` did not resolve a relative `--kicad-happy`, see FIXED.md; TH-093 and TH-094 filed and fixed 2026-10-25 at the wave 10 final review — bare-list assertion files crash the coverage and health report counters; `audit_equations.py untagged` indicator order follows PYTHONHASHSEED, both LOW, see FIXED.md; TH-091 filed and fixed 2026-10-25 during wave 10 planning — `generate_analytics.py` ignores `KICAD_HAPPY_TESTHARNESS_DATA_DIR`, see FIXED.md; TH-092 filed and fixed 2026-10-25 during wave 10 planning — `audit_equations.py` reads sources as UTF-8 text and `find_untagged` swallows `SyntaxError`, see FIXED.md; TH-090 filed and fixed 2026-10-25 during wave 10 planning — `refresh_findings.py` counted drift's no-checkable-items sentinel as an item and reported such findings as current, see FIXED.md; TH-089 filed and fixed 2026-10-25 by the harness audit fix session — `generate_catalog.py` counted the `capability_mode.json` sidecar as a schematic/PCB/EMC/SPICE output, see FIXED.md; TH-080..088 filed 2026-10-25 from the harness external audit round 1 — budgeted-kind worker exceptions, ledgered-timeout coverage, `discover.py --repo` global-manifest shrink, silent assertion-file drop, null/`[]` required-field locks (all HIGH, gate/assertion false-pass paths), constants corpus-hit names, `audit_equations --diff` no-op, `validate_design_intent` multi-repo scope, `analyze_bom_mismatch` layout (LOW); records `docs/audit/0*-harness-*/findings/VERIFICATION.md`, plan `docs/audit/HARNESS-FIX-PLAN.md`; TH-079 filed 2026-10-25 from the external audit round 1 — `generate_validation_md.py` category table and total use different denominators (1,855 = the aspirational count), LOW; TH-078 filed 2026-10-24 at the v3 round-9b gate — no "debt resolved" disposition: a ledgered unit the candidate fixes fails `skips_ok`, `strict_clean` and the strict comparator (`missing_a`), so the structural criterion cannot pass mechanically and the response builder carries a hand-written exception, LOW; TH-065, TH-066 + TH-077 FIXED 2026-10-24, see FIXED.md; TH-077 filed 2026-10-24 at the v3 round-8 spice-offline gate — `run_spice.py` output is not deterministic run-to-run: `simulation_results[*].model_note` flips `lookup:<MPN>` ↔ `cache:<MPN>` for the same product and inputs (132 of 8,829 reports between two baseline passes), LOW; TH-076 fixed-on-discovery 2026-10-23 during the Checklist 11 backlog pass — `audit_constants.py scan` dropped and re-added every constant whose file moved without a `relocate --map` (rounds 2/3), losing 41 verification records incl. `_REGULATOR_VREF` 55/114 and `_CAP_ESL` 7/7; the registry had also not been rescanned since round 5, see FIXED.md; TH-075 fixed-on-discovery 2026-10-23 at the v2.3.2 corpus regen — `run_spice.py` per-unit `--workdir` carried raw repo/file names into ngspice, 18,464 sims silently skipped on 5,198 corpus units, directory name now sanitized + digest, see FIXED.md; TH-074 fixed-on-discovery 2026-10-22 at the v2.3.2 backport gate — long-run waiters stalled on a `pgrep -f` self-match and on a zombie PID; `tools/wait_for_run.py` + RUNBOOK 26k + full-chain `done.json` marker, see FIXED.md; TH-073 fixed-on-discovery 2026-10-17 at the v3 round-6 gate preflight — `run_corpus_gate.py` accepted analyzer-less profiles (`spice-offline`, the new `distributor-offline`) and would have run a zero-unit gate, guard added, see FIXED.md; TH-072 fixed-on-discovery 2026-10-16 at the v3 round-5 gate preflight — `full-chain` profile declared no schematic analyzer, Phase B ran no chained unit, see FIXED.md; TH-071 filed 2026-10-16 at the v3 round-4 gate — `run_corpus_gate.py --jobs` not memory-aware, hierarchy profile at 32 jobs OOMs the box, LOW; TH-070 filed 2026-10-15 at the v3 round-2 reply — scan-coverage identity by line/file yields ~150 false losses per structural round, MEDIUM; TH-069 FIXED 2026-10-15 at the v3 round-3 reply — discover.py regular-file filter + manifest regen, see FIXED.md; TH-068 filed 2026-10-15 at H0 plan 6 — fixture-lane A/A chained envelopes unverifiable after the basetemp move, LOW; TH-067 filed 2026-10-15 — batch-runner pool workers outlive a killed parent (the TH-063 mechanism), MEDIUM; TH-066 filed 2026-10-15 at the H0 plan 4 final review — audit tools walk 58 of the 90 scanner files; TH-065 filed 2026-10-15 at H0 plan 4 — audit_constants function-scope `name:line` identity churns the registry; TH-064 filed 2026-10-15 — emc/thermal/spice `--resume` refused until identity-based resume exists; TH-063 filed 2026-10-14 — mutating runner launched against the live tree from a TDD RED step, 16,909 emc outputs rewritten, no measurable impact; TH-055 and TH-059 (harness half) fixed 2026-10-15 (H0 plan 2), see FIXED.md; TH-062 filed 2026-10-14 — 58 print-and-return vacuous skip paths in required-tier smoke files; TH-061 filed 2026-10-14 — test_datasheet_db_cli.py fallback fixture writes under repos/; TH-060 filed 2026-10-14 — test_kh393_power_rails_threaded premise stale since PR #44, now strict xfail; TH-052/053/058 fixed 2026-10-14 (H0 plan 1, honest pytest collection), see FIXED.md; TH-059 filed 2026-10-06 at the v2.3.1 regen — batch SPICE side effects: spice/ dirs in repos/ + live DigiKey lookups; TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 FIXED 2026-10-15 at H0 plan 5 — generator rewritten as grouped reconciliation, see FIXED.md; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 301 open issues (298 KH + 3 TH).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-1102: KO-001 never checks a rule area's `pads` or `tracks` restriction
**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/assembly.py:1287`, `:1311` (only `footprints` and `vias` are tested; `_prohibits` at `:1210`)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey K §1 "out of scope, noted")
**Symptom:** kicad-cli reports 725 track and 87 pad items on the KO A/B boards that KO-001 does not report. A pad is judged by its own shape in KiCad, not by its footprint's courtyard.
**Fix direction:** add pad-shape and track-segment tests against the area outline for areas that prohibit them; measure against kicad-cli on the same boards.
**Gate budget (when fixed):** KO-001 additions (new reach), pcb lanes.

### KH-1101: `V1P` / `V2P` read as power rails while their `V1N` / `V2N` twins read as signals

**Severity:** LOW (no corpus case located; differential ADC inputs such as ADE7753 V1P/V1N, V2P/V2N)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:112` (`_V_NUMBER` `[VP]\d*` admits a bare `P`), `:121-126` (`_is_v_number_rail`: a voltage part with nothing after it is a rail), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (N1 review minor)

**Symptom:** probe: `is_power_net_name` True for `V1P`, `V2P`, `V1P_IN`; False for `V1N`, `V2N` (base: all True). A channel pair is split into a "rail" and a signal.

**Fix direction:** require a digit after `P` (`V1P8`, `V3P3`) for the voltage part. A bare trailing `P`/`N` pair is a channel. Add `V1P`/`V2P` to the False table.
**Gate budget (when fixed):** power-net reads on `V<n>P` names; measure (expected ~0 on the corpus).

### KH-1100: pcb top-level `board_thickness_mm` appears only when current-capacity findings exist

**Severity:** LOW (output-shape instability; the value stays in `setup.board_thickness_mm`)
**File:** `skills/kicad/scripts/pcb/presentation.py:336-337` (`current_capacity` kept only with entries), `:507-512` (`board_thickness_mm` copied from it); default `pcb/routing.py:1179`, `:1257-1258`, at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (N1 report item 3, ruling R6; also named KH-new-board-thickness-follows-cc-findings)

**Symptom:** a board loses the key when its last power or narrow net leaves the CC list. Solstrejf modmatrix-pots lost it in 11c because its only CC entries were V-number signals. apfaudio tiliqua-panel never has it.

**Fix direction:** emit `board_thickness_mm` from `setup` unconditionally (or retire the duplicate key), with null when the file has none.
**Gate budget (when fixed):** `board_thickness_mm` additions on every pcb unit without CC findings (std + fc); a schema decision first.

### KH-1099: PS-002 reports raw islands of an unfilled zone as a deterministic plane split

**Severity:** LOW (info-heavy; 26 PS-002 on 19 full-chain units at 6138b126)
**File:** `skills/kicad/scripts/cross_analysis.py:1029-1106` (`check_plane_splits`: islands from the connectivity graph; `confidence` `deterministic` at `:1093` when no crossing), at db551674; RT-001's per-net caveat is `pcb/presentation.py:148-149`, `:438-443`
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (N6b review minor)

**Symptom:** GoodEarthWeather/myKicadProjects QEX_PowerAmp_Experiment_v2: "GND plane split: 127 islands" (deterministic, info) on a GND zone saved without its fill. RT-001 on the same board says "Its zones are not filled in the saved file: refill zones before trusting this count". PS-002 only has the generic "if zones were modified" hint.

**Fix direction:** when every zone on the net has `is_filled` False, skip PS-002 or emit it as heuristic with RT-001's caveat in the description.
**Gate budget (when fixed):** PS-002 removals or description/confidence changes on ~19 fc units.

### KH-1098: one unreadable courtyard arc drops the footprint's courtyard on both sides

**Severity:** LOW (KO-001 and courtyard-overlap false negatives on footprints with one malformed courtyard arc)
**File:** `skills/kicad/scripts/pcb/reader.py:601`, `:680-681` (per-footprint `crtyd_unchainable`), `:692`, `:800`, `:812-813` (all sides dropped); consumer `pcb/assembly.py:1235-1238`, at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (K2 review minor)

**Symptom:** a footprint with a valid F.CrtYd and an arc without `mid`/`angle` on B.CrtYd is judged on neither side, so a front-side keep-out or courtyard overlap is not reported. KiCad rejects only the malformed side.

**Fix direction:** keep the flag per courtyard layer (`side_unchainable[layer]`) and drop only that side's polygons and box.
**Gate budget (when fixed):** KO-001 / courtyard-overlap additions on affected footprints; measure first (expected few).

### KH-1097: KO-001 summary of an unnamed rule area ends in a stray space

**Severity:** COSMETIC
**File:** `skills/kicad/scripts/pcb/assembly.py:1281` (`kz_name = kz.get("name", "unnamed")` is `''`), `:1301`, `:1332` (summary f-strings), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (K1 review minor, ruling R11)

**Symptom:** "Keepout violation: via at (103.7, 55.5) inside keepout " / "… REF** inside keepout zone " on every unnamed area (119 descriptions on 36 boards per the product).

**Fix direction:** test `if kz_name` in the summary. Because the summary is the via finding_id hash input, do it together with a finding_id re-key, or hash a summary-independent key.
**Gate budget (when fixed):** KO-001 `summary` values on unnamed-area boards, and finding_id changes if the hash input is not decoupled.

### KH-1096: KO-001 reports a via or footprint once per overlapping rule area

**Severity:** LOW (duplicate KO-001 errors, `#n` finding_id suffixes)
**File:** `skills/kicad/scripts/pcb/assembly.py:1274-1345` (`analyze_keepout_violations`: one finding per item per area, no merge), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (K1/K2 reviews, rulings R4)

**Symptom:** flosimn/Cyton-Mod `Cyton Mod.kicad_pcb`: via (103.70, 55.54) under four overlapping unnamed `In2.Cu` areas → 4 identical KO-001 errors (`…f8f4242245c8`, `#1`..`#3`); via (103.70, 56.54) → 2. apfaudio/tiliqua-panel: REF** at (4.21, 111.89) → 2. The product reports that kicad-cli lists each item once (not re-checked).

**Fix direction:** merge findings per item (via position or footprint uuid) and list the area names in one finding. Keep the first finding's identity so finding_ids stay stable.
**Gate budget (when fixed):** KO-001 removals of `#n` duplicates on boards with overlapping areas (std + fc), plus summary/trust/audience rollups.

### KH-1095: a reference-named net that feeds an IC supply pin named V-/VEE/VBAT/VIO/VL/PVIN (or a supply pin not typed power_in) is read as a bare reference node

**Severity:** LOW (DO-DET decoupling status / power-rail census on REF-named supplies; 0 lost rails in the product sample)
**File:** `skills/kicad/scripts/signal_detectors.py:3863-3867` (`_ic_supply_pin`), consumers `:3870-3878` (`_reference_net`, DO-DET IC power nets `:3904-3906`) and `:4716-4717` (`_power_rail`), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (N8 review minor)

**Symptom:** a net such as `VREF_NEG` or `2V5_REF` that feeds an op-amp's `V-`/`VEE` or a part's `VBAT`/`VIO`/`VL`/`PVIN` pin is treated as a reference node nothing supplies. Same if the pin is typed `power_out`/`passive`.

**Fix direction:** match supply pin names on the raw name (keep `-`), add VEE/VSS-negative/VBAT/VIO/VL/PVIN/AVCC forms, and accept `passive` pins whose name is a supply name.
**Gate budget (when fixed):** DO-DET IC decoupling rows on REF-named supply nets; measure first (expected small).

### KH-1094: a COM or `0` net that the context reads as ground gets no 0 V rail key

**Severity:** LOW (`rail_voltages` key missing; consumers then treat the net as unknown voltage)
**File:** `skills/kicad/scripts/schematic/net_analysis.py:1714-1723` (`_estimate_rail_voltage` calls `is_ground_name` without rails); caller `schematic/pipeline.py:367-368`, at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (final correctness review Minor 4)

**Symptom:** a `COM` net named by a power symbol is ground for every detector (`ctx.is_ground`), but `rail_voltages` has no `COM: 0` entry. Same for `0` once B3 lands. Same at 6138b126.

**Fix direction:** in `build_rail_map`, give 0 to a net where `ctx.is_ground(net)` is True and that is not VSS-family, before calling the name estimate (or pass `ctx.ground_name_rails` into `_estimate_rail_voltage`).
**Gate budget (when fixed):** `rail_voltages` additions on COM/0-ground units, and any consumer that reads them (VD-003, VM-001); measure first.

### KH-1093: an isolation-barrier Y-cap between a primary rail and the secondary ground is counted as decoupling

**Severity:** LOW (false info DC-DET / DO-DET; 6 units / 12 items per the product, Demetrius-Ross/SimMonitor family)
**File:** `skills/kicad/scripts/signal_detectors.py:1271-1297` (`detect_decoupling`: rail cap whose other pin `ctx.is_ground`), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (N3 review, unit 033)

**Symptom:** SimMonitor `board_MKIV/ESP-Board`: C3 (1000pf/3kV) joins `-Vin` (primary 0 V of PS1 REC5A-2405SW) to `ESP_GND2` (PS1 `-VOUT`). Once `ESP_GND2` reads as ground, C3 is reported as decoupling on `-Vin`.

**Fix direction:** do not count a cap as decoupling when its two nets sit on opposite sides of an isolated converter (the converter's input and output pins), or when its voltage rating is ≥ 1 kV.
**Gate budget (when fixed):** DC-DET / DO-DET info removal on the SimMonitor units (~6), standard lane.

### KH-1092: a net named `0` by the SPICE ground symbol (Simulation_SPICE:0 / pspice:0, `#GND01`) is not ground

**Severity:** LOW-MEDIUM (false RS-001 / PP-001 on simulation schematics; product: 148 units, −139 RS-001 / −53 PP-001 when fixed)
**File:** `skills/kicad/scripts/kicad_types.py:57-64` (`scan_power_rails`: `#PWR`/`#FLG` references only), `:67-73` + `:272-274` (the power-symbol set is used for COM only); `kicad_core/netnames.py:331-332`, at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (fix-wave STOP 2, ruling R26)

**Symptom:** joseluizmendonca/ph_driver_hardware `src/driver_sim.kicad_sch`: the `0` net (four `#GND0n` symbols) reads as a signal, and RS-001 warns "0 has no declared source". The same happens on every KiCad-SPICE example sheet that uses the `0` ground symbol.

**Fix direction:** let `power_symbol_com_nets` cover a net named `0` whose `power_symbol` part is a ground symbol (lib `Simulation_SPICE:0`, `pspice:0`), or add `#GND` to the scan. Needs its own survey (R26).
**Gate budget (when fixed):** RS-001 −139, PP-001 −53 and downstream rail rows on ~148 units (product estimate), standard + full-chain + spice.

### KH-1091: VD-003 takes a ground-named negative supply (AVSS) as the 0 V end of a resistor

**Severity:** MEDIUM (false VD-003 error; 1 design / 2 units on the corpus per the product)
**File:** `skills/kicad/scripts/schematic/system_analyses.py:763-775` (`_find_power_net`: `gnd_net` = any `is_ground` pin net), `:977-990` (VD-003 `v_across = |V(pwr_net)|` when both ends are found); `kicad_core/netnames.py` (`AVSS`/`DVSS` exact ground names since this range), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (fix-wave STOP 1, ruling R27)

**Symptom:** eez-open/dib-mio-afe3 `EEZ DIB AFE3`: R34 (10 Ω) feeds AVSS (−2.5 V) from `-2V5_ISO`. VD-003 reads AVSS as 0 V and reports 625 mW across R34 at error severity. In reality only the filter current flows. New in this range (base: AVSS not ground, resistor skipped).

**Fix direction:** in `_find_power_net`, treat a ground-named net as the 0 V end only when its rail voltage is 0 or unknown and it is not VSS-family (`is_vss_name`). Otherwise fall through to the two-voltage branch. Fixture: negative LDO → R → AVSS.
**Gate budget (when fixed):** VD-003 removal on the eez AFE3 units (2), standard + full-chain.

### KH-1090: a COM net used as the board or isolated-supply return is not ground unless a power symbol names it

**Severity:** LOW (info DO-DET "missing decoupling" + lost DC-DET; product count +16 DO-DET info, +4 warn/err false, accepted under R20)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:338-339` (`COM` ground only when in `power_rails`); `kicad_types.py:67-73` (`power_symbol_com_nets`), `:272-274` (ground rail set), at db551674
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (product final false-signal review; ruling R20)

**Symptom:** jagdeepsingh02/ENNOID-Dual-Gate-Driver (V0.2/V0.3 ISO_PSU and Dual Gate Driver sheets, VBUS-Sense ISO_PSU): +VCC/-VEE caps return to COM, the 0 V output of an MGJ2 isolated converter. At the candidate these caps are no longer decoupling, and DO-DET reports "IC U2 missing decoupling on +VCC, -VEE". Base read them correctly. The product also names 2 Arduino Nano Eagle exports and a microscope board (not re-checked).

**Fix direction:** read COM as ground also when (a) another label on the same net is a ground name (`GND_ISO`), or (b) a regulator/converter pin named `COM`/`GND`/`0V` sits on it, whatever its pin type. A `power_in`-only pin rule does not cover ENNOID (pins typed `output` / `input`).
**Gate budget (when fixed):** schematic DC-DET / DO-DET on COM-return boards (adds back the base items), CG-AUD.

### KH-1087: taps of a split negative rail (`7V0_N_1`, `7V0_N_2`) read +7 V, and a `V12N` / `V12P` pair gets no voltage

**Severity:** LOW (rail_voltages sign on starshipraider BLONDEL taps; no voltage on eurorack V<n>N/P rails)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:378`, `:381-398` (`negative_split_rails`: `fullmatch` on `<n>V<n>_N`), `:41-61` (`parse_voltage_from_net_name('V12N')` = None)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey C ask 3 and residue; KH-967 follow-up)

**Symptom:** starshipraider BLONDEL `entry-afe-characterization_psu.sch`: `rail_voltages` `7V0_N` −7.0 but `7V0_N_1` / `7V0_N_2` +7.0. eurorack-kicad AK4458VN breakout: `V12N` (op-amp V− pins) and `V12P` (V+) have no voltage, and RS-001 warns on both.
**Fix direction:** let a `<n>V<n>_N_<k>` tap share the sign of its `<n>V<n>_N` rail when the `_P` twin exists. Read `V<n>N` / `V<n>P` as ∓/±n V when both exist (the same twin evidence). Keep `1V5_N` alone positive (11b-2 ruling P1).
**Gate budget (when fixed):** `rail_voltages` / `statistics.power_rails` sign flips on BLONDEL taps; voltage adds on V<n>N/P pairs; downstream op-amp rail / regulator dissipation where read.

### KH-1086: `parse_voltage_from_net_name` misreads comma decimals (`3,3V` → 3.0, `2,75V` → 75), a minus inside the name (`F-15V`, `GENERATED -5V` → positive) and P-notation (`AVDD1P2V` → 2.0)

**Severity:** MEDIUM (shared parser behind rail_voltages and every `rail_voltage_or(..., parse_voltage_from_net_name)` caller; one new wrong rail value at db551674)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:41-61` (sign from the first character only `:53`; `(\d+)V(\d+)` `:55`; `(\d+(?:\.\d+)?)V` `:59`, dot decimals only, no `<n>P<n>`); guard `skills/kicad/scripts/schematic/pipeline.py:371-375` (KH-962 skips commas and sign disagreements only)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey C ask 3: slugs KH-new-net-voltage-comma-decimal, -mid-minus, -p-notation; ruling C-R4 → v3.0.3)

**Symptom:** probe: `3,3V` 3.0, `2,75V` 75.0, `+3,3V` 3.0; `F-15V` 15.0, `GENERATED -5V` 5.0, `VEE_-12V` 12.0, `AVDD_-5V` 5.0; `AVDD1P2V` 2.0, `1P2V` 2.0. Live: daisho `hw_de2-115-frontend_hdmi_hdmi.sch` gains `rail_voltages['AVDD1P2V'] = 2.0` at db551674 through KH-962's regulator-output pass (U901 TPS54218; no key at 6138b126). openventilator `rail_voltages['+3,3V-FAILURE'] = 3.0` (both SHAs). The sign and comma cases on regulator outputs (nvm `F-15V`, codesqueak `GENERATED -5V`, Carte_Wifi `3,3V`, STM32-SDR `2,75V`) are skipped by the C-R4 guard and get no value.
**Fix direction:** in the parser: accept `,` as the decimal mark between digits; take the sign from a `-` or `NEG` right before the voltage token (keep `-RESET`-style names out by requiring digits); read `<n>P<n>[V]` as a decimal (`1P2`, `AVDD1P2V`). Then drop the comma half of the `pipeline.py:371` guard. Same family as KH-719 (sign) and KH-917 (suffix voltages).
**Gate budget (when fixed):** `rail_voltages` value changes / adds on units whose rail names carry a comma, an inner minus or P-notation (survey C census: ~11 regulator outputs, plus power-named nets such as `+3,3V*`); VM-001 / PR-DET / power_budget downstream where they read these rails.

### KH-1085: a virtual-ground pour (VGND, HP_VGND) is no longer a reference plane on the PCB side, so GP-001 checks traces over it as a plane split

**Severity:** LOW (GP-001 error moves on ~8 full-chain units, E 12-16 corpus fc units, accepted under ruling P-G2)
**File:** `skills/kicad/scripts/pcb/routing.py:418-421` (return-path `ref_idxs`: ground or power by name only), `:437`; `skills/kicad/scripts/kicad_core/netnames.py:341-342` (virtual ground is not ground); divergent EMC rule `skills/emc/scripts/emc_rules.py:130` (`is_emc_ground_name` still takes `*gnd`)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey G §3b, ruling P-G2)

**Symptom:** after P-G2, `VGND` / `HP_VGND` zones leave the PCB reference-plane set (`analyze_return_path_continuity`), and VGND tracks are checked as signals. Survey G measured fc GP-001 +32 / −27 errors on 8 units. The EMC ground rule still calls VGND ground, so the PCB and EMC sides now disagree on the same net.
**Fix direction:** a PCB-only rule: a zone on a virtual-ground net that fills like a plane (the `_reference_plane_layers` fill test) and connects to bypass capacitors is a reference plane. Keep the schematic reading (neither ground nor power). Make `is_emc_ground_name` follow the shared rule for virtual grounds. Same family as the plane-identity half of KH-717.
**Gate budget (when fixed):** full-chain GP-001 / RP-001 / RP-002 moves on VGND boards (the survey's 8 units restored); PCB `reference_plane_changes` entries.

### KH-1084: a `Regulator_Switching` symbol on an unmapped reference prefix (VR, REG, PS, DC, POW…) is typed `switch`, and the regulator disappears from PR-DET

**Severity:** MEDIUM (the regulator vanishes from every power detector; 25 parts / 22 units at db551674, pre-existing)
**File:** `skills/kicad/scripts/kicad_core/classify.py:352` (`if "switch" in lib_lower or "button" in lib_lower: return "switch"` matches "regulator_switching"; it runs before any regulator rule)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff slug KH-new-vr-regulator-varistor at db551674 (probe + candidate snaps)

**Symptom:** probe: `classify_component(r, 'Regulator_Switching:LM2596S-5', 'LM2596S-5')` = `switch` for REG1 / PS1 / VREG1 / DC1 / VR1 / Z1 (ic for U1 / IC1). Candidate snaps: 25 switching regulators on 22 units typed `switch`, 0 with a PR-DET record (Horticulture-LED VR1 TPS560430, Erhannis POW1_* LM27313 ×13, MT3608 ×3, bluesat REG_{5}1 ADP2302, dridri DC1 LM22676, RECOM R-78E ×4).
**Fix direction:** test for a regulator library (`regulator_switching`, `regulator_linear`, `regulator_*`) before the `switch` substring. Better, match library-name words, not substrings. Fold `VR` into the map as a regulator prefix with the existing potentiometer / varistor overrides (KH-1033).
**Gate budget (when fixed):** `components[].type` switch → ic on 25 parts; new PR-DET records and their downstream (rail_voltages, power_budget, thermal, DO-DET) on 22 units.

### KH-1083: regulator current is estimated from output capacitance (10 mA per µF, cap 1 A / 2 A), so bulk caps make a 7 W LDO and a TS-001 Tj 445 °C error

**Severity:** MEDIUM (error-severity thermal false positive; the schematic output contradicts its own power_budget)
**File:** `skills/kicad/scripts/signal_detectors.py:2445-2448` (LDO: `min(total_cout * 1e4, 1.0)`), `:2466-2468` (switching: cap 2.0 A); consumer `skills/kicad/scripts/analyze_thermal.py:239-260` (LDO `estimated_pdiss_W` taken as is)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey G ask 3; exposed by KH-925's `DVSS` ground)

**Symptom:** HelveticaScenario/eurorack-kicad teensy_dc_interface U10 NCP1117-5.0 (+12 V → AVDD): once `DVSS` reads as ground, C52-C55 (4 × 47 µF) count as output capacitors. `estimated_iout_A` goes 0.1 → 1.0 and `estimated_pdiss_W` 0.7 → 7.0. Thermal then reports TS-001 error "estimated Tj 445°C exceeds abs max 125°C", plus TS-004 7.00 W and TP-001 ×2. The same output's `power_budget.rails.AVDD` gives 10 mA and 70 mW for U10.
**Fix direction:** estimate a regulator's load from the rail's `power_budget` load (as thermal already does for switchers), not from its capacitance. When there is no load estimate, give no dissipation (thermal `skipped: no_load_estimate`) rather than an error-grade Tj. If a proxy stays, it should only be able to raise an info.
**Gate budget (when fixed):** `power_dissipation.estimated_iout_A` / `estimated_pdiss_W` on every regulator with output caps; thermal TS-001..005 / TP-001 / TH-DET moves; power_tree / inrush where they read it.

### KH-1082: VM-001 reads an analog switch's channel pins (COM / NO / NC / X / D) as logic I/O at the switch supply

**Severity:** MEDIUM (error-severity false positive; 69 errors / 24 units / 13 repos at db551674)
**File:** `skills/kicad/scripts/validation_detectors.py:497-506` (`_ic_rail_voltage`), `:680-741` (`validate_voltage_levels`: every IC endpoint is a logic endpoint)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey G ask 3; exposed further by ruling P-G1)

**Symptom:** bec5-group/pid-controller: 14 errors "15.0V / 5.0V domain crossing" between LM7171 / LMH6505 pins (±5 V) and DG467 / DG468 / DG469 `COM` / `NO` (±15 V). 11 predate Wave 11c. 3 `COM` nets are new, because P-G1 made `COM` a signal. Corpus (candidate snaps): 69 such errors with a CD4051B / TMUX4051 / DG2xx / DG46x / ADG / CD74HC4067 / TS5A channel pin on 24 units (PolySynth 24, pid-controller 14, Esp32_patch_bay 11).
**Fix direction:** an analog switch / multiplexer passes its channel pins' signal and drives no logic level. Skip its channel pins in VM-001. Recognise the part by function (lib / value family, plus control-pin evidence: IN / EN / S0-S2 beside COM / NO / NC / X / Y / Z). Pin types will not do it: legacy libraries type every pin `input`. Control pins keep the KH-667 logic-supply rule.
**Gate budget (when fixed):** VM-001 error removals on the 24 units (69 findings) plus any unnamed-pin cases the function test reaches.

### KH-1081: `V1+` / `V2+` / `V<n>H±` rails lose their rail reading by name after KH-939

**Severity:** LOW (lost rail-source / decoupling / trace-width checks on a few switched outputs; survey P puts it at ≤ 1.8 % of the V-number class)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:115-142` (`_is_v_number_rail`: a trailing `+` / `-` gives False, `:127-142`)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey P ask 4)

**Symptom:** probe: `is_power_net_name` is True at 6138b126 and False at db551674 for `V1+`, `V2+`, `V1-`, `V3H+`, `V3H-`. Survey P names `V2+` / `V1+` (BTS7008 high-side outputs, KLON TL072 V+) and `V<n>H±` (KT88 heater supply). The pin path (`topology_rails`) still catches a net that feeds a power_in pin. A switch output typed `output` with only loads on it does not.
**Fix direction:** decide by pins, not by the name. A `V<n>[H][+-]` net is a rail when a power_out pin, a high-side-switch output or a power_in pin is on it. Do not widen the name rule back: `V1+` is also a sense node (EnergyMonitor divider).
**Gate budget (when fixed):** RS-001 / DO-DET / CC-DET adds and `power_rails` entries on the few units that carry these names (survey P: 28 occurrences).

### KH-1080: VM-001 reads a gate driver's logic input (IRS2304 HIN / LIN) as a 12 V output driving a 3.3 V MCU pin

**Severity:** MEDIUM (error-severity false positive; 309 errors / 28 units at db551674, +100 on DRV88xx inputs)
**File:** `skills/kicad/scripts/validation_detectors.py:497-506` (`_ic_rail_voltage`: an IC's domain is its first positive supply), `:680-741` (`validate_voltage_levels`: `v_max` over every endpoint; only open-drain outputs are dropped as drivers)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey P ask 3, ruling R-P3)

**Symptom:** AmericanRework Pico-2x-BLDC `PCB_2xBLDCPicoV3.kicad_sch`: 12 VM-001 errors "12.0V / 3.3V domain crossing without level shifter" between the Pico GPIOs and IRS2304 HIN / LIN. Those pins are typed `input` in the symbol, and their VIH is TTL-level whatever VCC is. 8 errors predate Wave 11c (U / W phases). 11c added 4 (`V1H`/`V1L`/`V2H`/`V2L`) when KH-939 stopped reading `V<n>H` as a rail. Corpus (candidate snaps): 309 VM-001 errors on 28 units / 23 repos have a gate-driver endpoint on an `input` pin (UCC27517 `IN+` 224 on two iorodeo panels, IR2104 30, MIC4427 12, IRS2304 12, LM5107 8, IR2302 8), and 100 more on 25 units on DRV88xx motor-driver logic inputs.
**Fix direction:** take `v_max` only from endpoints that can drive the net (output, bidirectional, tri-state, open collector, or untyped). An `input` pin cannot overdrive the net. For the VIH warning branch, a gate driver's logic inputs need the part's own threshold, not 0.7 × VCC. Family: KH-667 (first-supply domain), KH-989.
**Gate budget (when fixed):** VM-001 error removals on gate-driver and other input-only high-side endpoints. Measure how many removals the pin-type rule makes on legacy symbols, where every pin is typed `input`.

### KH-1079: I2C pull-ups that reach the rail through a 3-pad solder jumper (SparkFun `SolderJumper_3_Bridged123`) are not found: `has_pull_up` / `has_pullup` false and false PR-001 / PU-001 errors

**Severity:** MEDIUM (false PR-001 "SDA/SCL missing pull-up" errors; 109 units / 77 repos / 235 bus nets at `4c2a0d6` have a resistor on the I2C net whose far side reaches a rail through a jumper; 26 of those units carry PR-001)
**File:** `skills/kicad/scripts/schematic/net_analysis.py:743-757` (`bus_analysis.i2c` pull-ups: the resistor's far net must be a power net); `signal_detectors.py:3987-3996` (design_observations `i2c_bus` `has_pullup`, same test); `validation_detectors.py:71-122` (`_bridged_jumper_neighbor_nets` / `_find_pullups_on_net_with_bridged`, used by PR-001 only: it matches `solderjumper_2_bridged` only, needs exactly 2 jumper nets, and walks signal net → jumper rather than resistor far side → jumper → rail); `validation_detectors.py:325` (PU-001, no jumper walk)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (locks FND-00001481-AST-12, FND-00001542-AST-08, FND-00001467-AST-09, FND-00001475-AST-07); verified at `6138b126`

**Symptom:** in all four designs, SDA / SCL – 2.2 k – JP pad A or C, and JP pad B = `3.3V`. JP is `SparkFun-Jumper:SolderJumper_3_Bridged123`, and `detect_solder_jumpers` reports it `default_state: bridged`.
- RTK Postcard: SDA_1 / SCL_1 via R17 / R18 and JP6, `bus_analysis` `has_pull_up: false`.
- LIS3DH Micro: SCL / SDA via R6 / R1 and JP2, `has_pull_up: false` and `has_pullup: false`.
- OpenScale-BT: SDA / SCL via R7 / R13 and JP2, both false, plus 2 PR-001 errors.
- Red Vision Touch Display: SCL / SDA via R4 / R3 and JP1, both false, plus 2 PR-001 errors and 2 PU-001.

**Fix direction:** one shared pull-up resolver for `bus_analysis`, design_observations, PR-001 and PU-001. It should follow a bridged-by-default jumper (2-pad and 3-pad `Bridged`/`Bridged123`, lib or footprint) on the resistor's far side to a rail, in the same way as the KH-741 one-hop walk (`validation_detectors.py:1545`), and record the jumper ref in `pull_ups[]`. Output-changing: `has_pull_up` / `has_pullup` flips, and PR-001 / PU-001 removals on those units.

### KH-1078: `detect_buzzer_speakers` takes the first non-rail pin net as the signal net, so a low-side transistor on the other pin is missed (`has_transistor_driver: false`)

**Severity:** LOW (wrong driver attribution and a possible `direct_gpio_drive`; 138 buzzers on 128 units / 70 repos at `4c2a0d6` have a transistor on the pin net that was not examined)
**File:** `skills/kicad/scripts/domain_detectors.py:43-48` (first of n1/n2 that is neither ground nor power wins), `:51-70` (driver search and the `tc_by_output_net` lookup on that one net only)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (lock FND-00001516-AST-07); verified at `6138b126`

**Symptom:** SparkFun USB RFID Reader BZ1 has `+` on `__unnamed_14` → JP1 (solder jumper, bridged) → VUSB, and `-` on `__unnamed_2` = Q1.C (MMBT2222A, E on GND) + R3. The detector picks `__unnamed_14` (the high side behind the jumper, not a named rail) and reports `signal_net: __unnamed_14`, `has_transistor_driver: false`.

**Fix direction:** examine both pin nets. Prefer the net with a transistor collector or drain (or `tc_by_output_net`) as the driven side, and treat a net that reaches a rail through a bridged jumper as the supply side.

### KH-1077: multi-pin TVS / ESD arrays report `clamp_net: null`, drop the power rails they clamp, and list no-connect pins as protected nets

**Severity:** LOW (every `esd_ic` record carries a null `clamp_net` by construction; its protected-net list is wrong when an array is used on rails)
**File:** `skills/kicad/scripts/signal_detectors.py:2595-2628` (the multi-pin diode branch: `protected` drops power and ground nets (`:2601`), `clamp_net: None` (`:2612`), `protected_net = sorted_nets[0]`); the same shape in the IC-ESD branch (`:2789`)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (lock FND-00001453-AST-14); verified at `6138b126`

**Symptom:** SparkFun Qwiic GNSS SAM-M8Q D7 (PESD3V3L4UG, `D_TVS_ESD_4_3.3V`) has A on `GND`, K2 on `3.3V`, K4 on `V_BCKP`, and K1 / K3 on the single-pin nets `__unnamed_17` / `__unnamed_18`, both `no_connect: true`. The record is `type: esd_ic`, `protected_nets: [__unnamed_17, __unnamed_18]` (the two NC pins), `protected_net: __unnamed_17`, `clamp_net: null`. The two rails it actually clamps are missing.

**Fix direction:** set `clamp_net` to the common-anode or ground pin net. Keep rail pins as protected nets when the array is placed on rails, and drop pins whose net is no-connect or single-pin.

### KH-1076: the `hx711` entry in the op-amp/ADC exclusion drops the HX711's own regulator (VFB + BASE driving an external PNP to AVDD) from `detect_power_regulators`

**Severity:** LOW (the AVDD rail has no recorded source; long-standing, absent at `7d9d4d9f`, `f53d107` and `6138b126`)
**File:** `skills/kicad/scripts/signal_detectors.py:1845-1850` (`_opamp_adc_exclude` includes `"hx711"`, added in `0d9a018c` "op-amp exclusion", v1.3.0~136; FIXED.md:8691 points to a KH-260 for those 17 records, but neither tracker has a KH-260 entry)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (lock FND-00001467-AST-05); verified at `6138b126`

**Symptom:** SparkFun OpenScale-BT U3 (HX711, 16 pins) has VSUP on `5V`, BASE on `__unnamed_14` = Q2.B, AVDD on `__unnamed_15` = Q2.C/L2/R12, and VFB on `__unnamed_16` = R9/R12 (divider). This is the datasheet LDO controller with an external PNP pass transistor (Q2.E on 5V). `detect_power_regulators` lists only U4 RT9080. When the lock was written, U3 was reported as `ic_with_internal_regulator`.

**Fix direction:** remove `hx711` from the exclusion or recognise it on its pins (VFB + BASE + AVDD → regulator controller with an external pass element). Without the exclusion the existing logic gives `ic_with_internal_regulator`: VFB is 1 regulator pin of 16, below 20 % (`:2031-2039`). A better record would name AVDD as the output, with the R9/R12 divider. If the product picks a different topology, the lock (`topology == ic_with_internal_regulator`) has to follow it.

### KH-1075: `detect_protection_devices` misses TVS diodes named outside its 15-keyword list (SMF5V0A, SM6T, SMF24A, SM712 …) and never reads the symbol keywords or description; USB VBUS then reads unprotected

**Severity:** MEDIUM (false UC-002 warning "No ESD/TVS protection on VBUS" and `vbus_esd_protection: fail`; 452 TVS-keyworded diodes on 224 units / 82 repos at `4c2a0d6` are missing from PD-DET)
**File:** `skills/kicad/scripts/signal_detectors.py:2575-2586` (`tvs_keywords`; `is_tvs` tests value / lib_id only; `description` is read for Schottky only, `keywords` never); `schematic/system_analyses.py:2611-2614` (the VBUS ESD test, with its own 5-word list); `detector_helpers.py:133-140` `_PROTECTION_KEYWORDS` (31 entries incl. `sm712`, `h5vu`, `bsd5c`); `signal_detectors.py:3356` `_CLAMP_DIODE_WORDS` (a fourth list)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (lock FND-00000419-AST-03); verified at `6138b126`

**Symptom:** janc18/CAE32 `Pedals.kicad_sch` D5 is `Diode:SMF5V0A`, typed `diode`, with symbol `keywords` "diode TVS voltage suppressor" and an empty description. It sits on `+5V` (= J15 VBUS A4/A9/B4/B9) and `GNDREF` (classed ground). PD-DET lists only D4 and F2. `usb_compliance` J15 reports `vbus_esd_protection: fail`, and UC-002 fires (warning) on a board that has a VBUS TVS. The most common corpus misses are `Diode:SM712_SOT23` (124 parts), `Diode:SMF24A` (32), `Diode:SM6T10A` (28), `Diode:SMF5V0A` (17), `Diode:SM6T6V8A` (16), and the vendor-library BSD5C and H5VU families.

**Fix direction:** one shared TVS recogniser for PD-DET, the USB VBUS check and the clamp-diode test. It should read value, lib_id, symbol `keywords` and `description` ("TVS", "transient voltage suppressor"), and use `_PROTECTION_KEYWORDS` plus the SMF/SMA/SMB/SMC, SM6T/SM8T/SM15T and P4KE families. Output-changing: PD-DET additions, UC-002 / `vbus_esd_protection` removals, and the protected nets seen by ES-001 / EG-001.

### KH-1074: discrete ORing, steering and backfeed-blocking diodes appear in no detector; PD-DET takes only rail-to-rail or rail-to-ground Schottkys and labels them `reverse_polarity`

**Severity:** LOW (no review output names the diode-OR / battery-backup topology)
**File:** `skills/kicad/scripts/signal_detectors.py:2637-2643` (the Schottky branch of `detect_protection_devices` needs a power net on one side and ground or power on the other); `domain_detectors.py:2813-2819` (`detect_power_path` looks at `type == "ic"` only)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (locks FND-00000399-AST-06, FND-00001445-AST-12, FND-00001481-AST-15); verified at `6138b126`

**Symptom:**
- BT_DC_motor_board D1 (BAT85, `Device:D_Schottky_Small`) has K on `+5V` and A on `__unnamed_17` (SW13 common), and no detector reports it. Its twin D2 (+5VBUCK → +5V) is in PD-DET as `reverse_polarity`, although the pair is a diode-OR.
- SparkFun LG290P and RTK Postcard D5 (PMEG4005EJ) has A on `3.3V` and K on a net that reaches V_BCKP / BT1 through R7. It blocks the backup cell from backfeeding 3.3 V, and no detector reports it. The cathode net is not a named rail, so the Schottky branch skips it.

**Ruling asked:** in our view this is a real gap but not a protection device. PD-DET records are read as ESD / surge protection by EG-001 (KH-1043: reverse-polarity records already give false ESD credit), ES-001 and design_observations `protected_nets`. Adding ORing diodes there would widen KH-1043. The suggested home is `detect_power_path`, with a discrete `diode_or` / `backfeed_block` entry: a Schottky or diode whose cathode reaches a rail directly or through one series R, with a second source on the same rail or a battery on the far side. If the product chooses that home, the three locks must be re-anchored to it. As written (`detect_protection_devices` contains D1 / D5) they would stay failing after the fix.

### KH-1073: KiCad 5 schematics whose stock-library symbols are neither cached nor in the project table lose every pin, so regulators become keyword-only records with null rails

**Severity:** LOW (the loss is diagnosed, but every topology check on those parts is blind; 515 units / 262 repos carry a keyword-only regulator record at `4c2a0d6`)
**File:** `skills/kicad/scripts/schematic/legacy_reader.py:69` `_STANDARD_LIB_PINS` (passives, diodes, LED, crystals, switches and discrete transistors only); `schematic/pipeline.py:895-916` (the per-library "not available to the analyzer" diagnostic); `signal_detectors.py:1765-1798` (the keyword-only `PR-DET` record with `input_rail` / `output_rail` null)
**Discovered:** 2026-11-11, harness, from the product's TH-109 rulings (lock FND-00001647-AST-04); verified at `6138b126`

**Symptom:** Jana-Marie/USB-LED-Otter `USB-LED-Otter.sch` has no `-cache.lib`, and its `sym-lib-table` lists only `otter`. U1 `Regulator_Linear:MCP1700-3302E_SOT23` is reported as `topology: unknown`, `input_rail: null`, `output_rail: null` ("Power regulator detected by keyword match (no pin data)"). No net carries a U1 pin, and the diagnostic reads `library 'Regulator_Linear': 1 placed symbol(s) … no pins; the part is left unconnected`. The lock's claim that the rails are "traceable from the net data" is false at this commit. The pins exist only in KiCad's stock library (SOT-23 MCP1700: 1 GND, 2 VOUT, 3 VIN) and in the board's pad nets (`USB-LED-Otter.kicad_pcb` is present). The same file also loses the J1–J5, U2 (STM32F0) and SW1 pins. C-Beeper loses D1, Q1–Q3 and J1 the same way.

**Fix direction (product to choose):** (a) built-in pin maps for the common stock regulator symbols (`Regulator_Linear` SOT-23 / SOT-223 LDOs), in the way `_STANDARD_LIB_PINS` covers passives; (b) recover pin→net from the PCB pad nets when a board is next to the schematic; (c) rule this an input limitation and keep the lock aspirational.

### KH-1072: the `single_pin_nets` design observation sets `nets` twice in one dict literal, so its net list is always empty

**Severity:** LOW (the observation's `count` and `components` are right; every consumer of its `nets` reads `[]`)
**File:** `skills/kicad/scripts/signal_detectors.py:3949` `"nets": single_pin_nets` and `:3958` `"nets": []` in the same `design_observations.append({...})` (`detect_design_observations`)
**Discovered:** 2026-11-11, harness, TH-109 triage (FND-00002073); confirmed by code read at product `6138b126`

**Symptom:** the later key wins, so `nets` is `[]` while `count` reports the number of single-pin nets.

**Fix direction:** drop the second `"nets": []` (or rename the per-pin list to a different key if the envelope must keep `nets` as a list of names); a linter rule for duplicate dict keys (flake8 `F601`) would catch the class.

### KH-1071: `detect_transistor_circuits` reports none of the five BUZ11 MOSFETs on Strandjungs although their pins are named G / D / S

**Severity:** MEDIUM (a driven MOSFET stage is invisible to the transistor-circuit findings and to everything that reads them, e.g. flyback-diode pairing)
**File:** `skills/kicad/scripts/signal_detectors.py` `detect_transistor_circuits` (FET loop over `fet_pins` from `detect_bridge_circuits`, ~3239-3258); not traced further
**Discovered:** 2026-11-11, harness, TH-109 triage of FND-00001593-AST-03 (JochiSt/Strandjungs_ReactionGame `hardware/Strandjungs_1of5.kicad_sch`) at product `6138b126`

**Symptom:** Q2 / Q4 / Q6 / Q8 / Q10 (`Transistor_FET:BUZ11`, type `transistor`) are absent from `detect_transistor_circuits`; only the five BC847 (Q1 / Q3 / Q5 / Q7 / Q9) are reported. Q2's net pins carry `pin_name` `G` (`__unnamed_27`), `D` (`/switch_channel#3/MAG_RTN`), `S` (`GND`), so `fet_pins` should map it; the drop happens later in the FET branch. The shared flyback diode D7 (the FND's subject) cannot be observed while the FETs are missing.

**Fix direction:** trace why a mapped low-side N-FET whose gate is driven by a BJT collector produces no record; fixture from this sheet (one BC847 → BUZ11 channel with a flyback diode).

### KH-1070: `kicad_version` is `unknown` for every file without a `generator_version` token (KiCad 6 / 7 files and KiCad 5 boards), about a third of schematic and two thirds of PCB outputs

**Severity:** LOW (metadata; any consumer that keys on `kicad_version` loses the version for those files, while legacy `.sch` reports `5 (legacy)`)
**File:** `skills/kicad/scripts/pcb/pipeline.py:332` and `schematic/hierarchy.py:230` (`get_value(root, "generator_version") or "unknown"`), surfaced as `kicad_version` in `pcb/presentation.py:268` / `schematic/presentation.py:280`
**Discovered:** 2026-11-11, harness, TH-109 triage (FND-00001904-AST-05, FND-00002289-AST-03); corpus census of today's outputs

**Symptom:** only KiCad 8+ writes `(generator_version ...)`. Corpus: schematic 11,146 / 36,463 outputs `unknown` (file_version 20230121 5,807, 20211123 4,511, ...); pcb 12,114 / 18,684 (20171130 4,127, 20221018 2,730, 20211014 2,521, legacy `4` 1,950, `3` 252, ...). The file's `version` token is in the output as `file_version` and identifies the KiCad major version.

**Fix direction:** when `generator_version` is absent, derive `kicad_version` from `file_version` (the KiCad format-date table: 2017xxxx → 5, 2020-2021 → 6, 2022-2023 → 7, ...; pcb `3` / `4` → legacy), or rename the field to what it holds. Output-changing on ~23 k units; budget class at the gate.

### KH-1069: a failed-simulation `diagnostics` record copies ngspice's first error lines verbatim, so an include error carrying an absolute path makes the record machine-dependent

**Severity:** LOW (latent: 0 of the 108 records in the gate's quick_200 spice lane carry an absolute path)
**File:** `skills/spice/scripts/simulate_subcircuits.py:264-268` (`reason = " ".join(err_lines[:3])`; the comment notes an include error names the include path as written)
**Discovered:** 2026-11-08, harness, verifying the KH-480 closure at `6138b126` (code read; spice-offline census)

**Symptom:** the KH-480 fix records `<bench>.cir: <first 3 stderr lines>` for every failed simulation. The deck name is reduced to its basename, but the stderr text is kept as ngspice wrote it. When a bench includes a model by absolute path (a model cache or project dir), an include failure puts that path, and so the user's home or temp dir, into the output JSON. Two machines would then write different records for the same input.

**Fix direction:** replace known roots (workdir, model cache dir, project dir) in the copied lines with placeholders, or keep only the basename of any path token.

### KH-1068: EMC reads DNP only from the PCB footprint, so a connector marked DNP only in the schematic is still listed by IO-001 and the test plan

**Severity:** LOW (KiCad 6/7 boards whose DNP lives only on the schematic symbol; reach not measured)
**File:** `skills/kicad/scripts/pcb/reader.py:414` (`is_dnp` from the footprint `(attr ... dnp)` flag only); `skills/emc/scripts/emc_rules.py:312-317` `_connector_refs` (skips `fp['dnp']`; the schematic's `dnp` is not consulted), feeding IO-001, IO-002, ES-001 / ES-002, CK-003 and `test_plan.interface_risks`
**Discovered:** 2026-11-08, harness, verifying the KH-755 closure at `6138b126` (code read)

**Symptom:** KH-755 made EMC skip DNP connectors, using the PCB footprint flag. KiCad 7 added the footprint DNP attribute; on older boards, and wherever the user marks DNP on the schematic symbol only, the footprint carries no flag, so the connector still counts as a fitted external connector. The opposite case also exists in the gate: DavidRajchman SmartMPPTSolarCharger BCHW has connectors DNP on the board but not in the schematic, and those are skipped correctly.

**Fix direction:** when a schematic is given, treat a connector as DNP if either side says so (the schematic `dnp` by reference). Budget IO-001 / IO-002 / test-plan removals on those boards.

### KH-1067: TV-001 counts a same-point stacked via column once per segment, so one F.Cu–B.Cu column of three microvias reads as three thermal vias

**Severity:** LOW (can lift the grade on HDI thermal pads; corpus reach 0 at this gate)
**File:** `skills/kicad/scripts/pcb/copper.py:48` `_vias_reaching` (every via of a same-point, same-net chain that reaches the pad layer is returned), used by `analyze_thermal_pad_vias` (Tier 1); pinned by `tools/tests/test_pcb_thermal_pad_via_reach.py:87-94` (`via_count` 3 for one stacked F-In1 / In1-In2 / In2-B column)
**Discovered:** 2026-11-08, harness, verifying the KH-573 closure at `6138b126` (code read)

**Symptom:** D3 (KH-573) lets a blind or buried via count when a stack at the same point carries it to the pad's copper (ruling D P6). Each segment of the stack is then counted, so one column through the board gives `via_count` 3 and an effective count of three vias. Heat leaves through one barrel, so the adequacy grade can be one step too high. Survey D measured reach 0 (reDIP-64's blind vias are staggered).

**Fix direction:** count a same-point stacked chain as one via (its narrowest drill for the drill weighting). Budget TV-001 `via_count` / adequacy on HDI boards.

### KH-1066: the op-amp bench clamps its measuring point to 1 Hz, so an Rf‖Cf pole below about 10 Hz is measured less than a decade below the pole, or above it

**Severity:** LOW (a false SP-FAIL / SP-WARN on stages with a very low feedback pole; corpus reach not measured)
**File:** `skills/spice/scripts/spice_templates.py:541` (`f_meas = max(1, min(f_meas, 1000))`, after the KH-713 pole cap at `:537-540`); pinned by the product test `tools/tests/test_spice_opamp_bias.py:340` `test_measurement_point_keeps_the_1_hz_floor`
**Discovered:** 2026-11-08, harness, verifying the KH-713 closure at `6138b126` (code read)

**Symptom:** S1 measures the gain a decade below 1/(2π Rf Cf), then clamps the frequency to [1, 1000] Hz. A pole below 10 Hz is measured less than a decade below it, and a pole below 1 Hz is measured above it. Example: 66.5 kΩ ‖ 100 µF (0.024 Hz) is measured at 1 Hz, about 32 dB below the resistive gain, which reads as a gain error. The KH-713 examples are fine (Colossus −0.17 dB, ovobot about −0.04 dB).

**Fix direction:** lower the floor (ngspice's AC sweep has no 1 Hz limit), or report "pole below the bench range; gain not measured" when 0.1 × f_pole < 1 Hz. Budget opamp status / gain moves on those stages.

### KH-1065: ES-001 / ES-002 evaluate a DNP protection device

**Severity:** LOW (latent at `6138b126`: the fix wave made ES-001 removal-only, so the ruled ~11 false adds do not occur at the tip)
**File:** `skills/emc/scripts/emc_rules.py:3196` `check_esd_protection_path` (`:3237-3246` iterate PD-DET records with no DNP test on the device; only connectors carry `dnp`); `skills/kicad/scripts/signal_detectors.py:2571` `detect_protection_devices` (no DNP test)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (ruling M1 concern 1 and the budget text "KH-1033 addendum + KH-new-es001-dnp-protection (v3.0.3)"; the slug is missing from the handoff's file list)
**Target:** v3.0.3

**Symptom:** bobbycar-graz Bobbycar-FOC-hardware: D39 (`Device:D_Zener`, "51V TVS C310059") is `dnp: true` in the schematic and in the PCB footprint (`Diode_SMD:D_SMC`), yet it is an ES-001 candidate. Before the fix wave, the KH-755 fix gave it a false ES-001, and the ruling counted it with the 10 BSP89 adds (KH-1033 addendum) as ~11 false ES-001 on the board. At `6138b126` (after `3ac0ec6e`, option A) the gate shows ES-001 removal-only: Bobbycontroller goes from 4 ES-001 to 0, none on D39 or a `V` reference. The missing DNP test on the device remains.

**Fix direction:** skip DNP / off-board protection devices in ES-001 / ES-002 (and arguably in PD-DET's EMC consumers). Measure the reach first: this is a new rule with unmeasured reach (ruling).

### KH-1064: two product tests leave files open (`ResourceWarning`)

**Severity:** LOW (test hygiene; noise under `-X dev` / `-W error`)
**File:** `tools/tests/test_spice_workdir.py:46` (`json.load(open(_analysis(tmp), …))`), `tools/tests/test_lifecycle_cli_exit.py:29` (`open(SCRIPT, …).read()`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-test-resourcewarnings`)

**Symptom:** `python3 -X dev -W always::ResourceWarning -m unittest` on both files (export of `6138b126`): one "unclosed file <_io.TextIOWrapper …>" at each line, tests OK. These are the only two `open()` calls without a context manager in `tools/tests`. No socket warning appears in these files (the slug says "file/socket").

**Fix direction:** `with open(...)`. No output change.

### KH-1063: `_plane_fill_board_area` computes a multi-board area of its own instead of reading `statistics.board_area_mm2`

**Severity:** LOW (two board-area rules for one board; the plane decision can disagree with VS-001 / density)
**File:** `skills/emc/scripts/emc_rules.py:1594-1618` (`outline_loops` + depth parity, subtracts holes, clamps to `max(fill)`); the PCB area `skills/kicad/scripts/pcb/pipeline.py:174-184` `_board_area` → `pcb/geometry.py:315-336` `outline_board_area`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-plane-fill-area-twin`)

**Symptom:** after D2 (#69), `statistics.board_area_mm2` is already the summed outer-outline area that KiCad's Board Statistics reports. The EMC helper re-derives it from `board_outline.edges` with different rules:
- it subtracts inner loops (KiCad does not);
- it has no zero-length-line or touching-loop guard;
- it has no footprint Edge.Cuts guard;
- it uses a different polygon area routine.

It then takes `min(board, max(area, max fill))`. VS-001 (`:1547-1550`) reads the statistics value. No corpus delta was measured at this gate; the integrated A/B reports D2 × M2 consistent on the 9 plane boards.

**Fix direction:** read `board_area_mm2` and keep only the fill clamp. Budget any plane-layer change on multi-outline boards.

### KH-1062: VS-001 with exactly one (ground) via says "Board has 1 vias … (no vias detected)"

**Severity:** LOW (finding text contradicts itself)
**File:** `skills/emc/scripts/emc_rules.py:1557-1564` (`avg_spacing` only when `via_count > 1`; otherwise the note says `no {via_noun} detected`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-vs001-one-via-wording`)

**Symptom:** both branches show it. 11b-1 EMC snaps: std (count branch) 270 units "Board has 1 vias across 1404 mm² (no vias detected)" (bluepylons A-Thinkpad-USB-keyboard); full-chain (via-list branch) 115 units "Board has 1 ground vias across 24821 mm² (no ground vias detected)" (Fihdi Eurorack Kick-Drum). The plural is also wrong.

**Fix direction:** say "1 ground via, spacing not estimable" and fix the plural. Text-only budget on ~385 units. Sibling of KH-960 (same function, branch disagreement).

### KH-1061: EMC's connector set takes every footprint whose reference starts with `P`, so power switches, power LEDs, pushbuttons, potentiometers and pads are external connectors

**Severity:** MEDIUM (feeds IO-001, IO-002, ES-001 / ES-002, CK-003, shielding and the test plan on ~1,000 std units)
**File:** `skills/emc/scripts/emc_rules.py:312-332` `_connector_refs` (`ref.startswith('J') or ref.startswith('P') or ref.startswith('CN')`, excluded only by value words `test`/`tp`/`jumper`/`solder` and `JP`/`SJ`; `'usb' in lib` also admits USB ESD ICs such as `PESD4USB3BTTSQX` on a `U` ref)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-emc-pwr-prefix-switch-connector`; snak_28)

**Symptom:** JackMatanky kb_snak `28_nice_nano_view_03_pcb_snak_28.kicad_pcb` (candidate PCB snap): `PWR1` `ceoloide:power_switch_smd_side` and `PAD1` `pads` are both connectors. The 11b-1 std PCB snaps have 3,747 footprints on 991 units with a multi-letter `P` reference: `PILE` test pads 1,166, `PS` 352 (converters, caps, resistors), `PWR` 344 (109 `LED_0603_KA`), `PB` 128 (pushbuttons, test pads), `PAD`/`Pad` 227, `POT` 83. In the ES-001 sample, ConnectBox U9 is paired with pushbutton PB1.

**Fix direction:** use the schematic `type` when the board has a schematic. Otherwise require `P` followed by a digit, or a connector library / footprint, as the cross-analysis checks do. Budget EMC connector-derived findings and the test plan.

### KH-1060: a length bound written with a comma decimal and no unit (`(min 0,1)`) is accepted, while KiCad refuses the file

**Severity:** LOW (custom rules applied where KiCad applies none)
**File:** `skills/kicad/scripts/kicad_core/project.py:801-821` `_dru_bound_error` (evaluates the raw text: `parse_dru_length('0,1')` is None and `_dru_eval` returns `other` for the comma, `:719-720`, so no "Missing units."); the loader's comma→point rewrite `:1004` happens only on the value path
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff's DRU refusal siblings, "unitless comma bound")

**Symptom:** probes with a sentinel rule, kicad-cli 10:
- `clearance (min 0,1)`: refused. The reader says error `None` and keeps `'0,1'`.
- `clearance (min 0.1)`: refused. The reader correctly says "Missing units.".
- `clearance (min 0,1mm)`: loaded. The reader reads 0.1, as KiCad does.
- `via_count (max 1,5)`: loaded by KiCad, so no refusal is missing on unitless types.

**Fix direction:** apply the same comma→point rewrite before the bound check, so a unitless comma number reads as a number → "Missing units.". Expect ~0 corpus delta.

### KH-1059: the repeated-constraint refusal compares raw type names, so `hole` + `hole_size` in one rule loads, while KiCad refuses the file

**Severity:** LOW (custom rules applied where KiCad applies none)
**File:** `skills/kicad/scripts/kicad_core/project.py:897-903` (`ctype = item[1]`; `if ctype in constraint_types`, before `_DRU_CONSTRAINT_ALIASES` is applied at `:996`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff's DRU refusal siblings, "raw-type duplicate constraint")

**Symptom:** probe: `(rule d (constraint hole (min 0.1mm)) (constraint hole_size (min 0.1mm)))` next to a sentinel `track_width (min 5mm)` rule. kicad-cli 10 drops the sentinel (file refused). `load_kicad_dru_checked` returns error `None` and two `hole_size` constraints. The same applies to `mechanical_clearance` / `physical_clearance` and `mechanical_hole_clearance` / `physical_hole_clearance`.

**Fix direction:** map aliases before the duplicate test (one line). Expect ~0 corpus delta (KH-924's census found 0 refused files in 586).

### KH-1058: a custom rule whose `(layer …)` names a copper layer by its user name applies to holes but not to tracks, via diameters or annular rings

**Severity:** LOW (missed custom-rule violations on boards with renamed copper layers)
**File:** `skills/kicad/scripts/pcb/dfm.py:902-908` `_dru_layer_match` (pattern against the item's canonical layer), `:916-943` `_rule_items` (tracks on `t['layer']`, vias / annular on `'F.Cu'`), `:966-973` (holes tested against `board_layers`, which `pcb/presentation.py:173-183` fills with user names too)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-dru-user-layer-tracks`)

**Symptom:** probe with kicad-cli 10 `pcb drc`: `simple.kicad_pcb` with `(0 "F.Cu" signal "TopCopper")` and `(rule s (layer "TopCopper") (constraint track_width (min 5mm)))`. KiCad reports 3 `track_width` violations (the 3 F.Cu tracks), and the analyzer reports `compliant: true`. With `(layer "F.Cu")`, both flag them. This is the copper residue of KH-762 (closed by D8 for non-copper / hole matching).

**Fix direction:** map a rule layer through the board's user names to the canonical name before matching items. Budget `design_rule_compliance` additions on boards whose rules use user layer names.

### KH-1057: when a job file decides completeness, F.Paste / F.SilkS are never recommended, even on boards with SMD pads

**Severity:** LOW (2 true info findings lost at this gate, ruled; the gap covers every job-judged set)
**File:** `skills/kicad/scripts/analyze_gerbers.py:1206-1218` (job path returns `missing` from the job list only), `:1224` (`recommended = {"F.SilkS", "F.Paste"}` on the defaults path only), GR-001 `:2040-2043`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-job-completeness-skips-paste-check`; ruling D10 review minor 2)

**Symptom:** D10 reads Gerber-form job layer lists, so 5 more units are judged by their job. 2 of the 3 removed "Missing layer: F.Paste" info findings were true (otterprotect antispark, 68 SMD pads; usb_alien, 42). In the 11b-1 gerber snaps, 1,992 of 5,502 gerber units are already job-judged, and 307 of them have no F.Paste (108 no F.SilkS) with no note. The defaults path recommends F.Paste on 1,487 units regardless of SMD content.

**Fix direction:** after the job check, still recommend paste when the copper layers flash SMD pads (and silk when the job lists none), on both paths. Budget GR-001 info additions on job-judged sets.

### KH-1056: `is_touch_pad` matches "touch" anywhere in the footprint string, so every part in a library nicknamed `Touch…` is a touch electrode

**Severity:** LOW (FD-001 SMD counts low; visible only when the side has < 3 fiducials)
**File:** `skills/kicad/scripts/kicad_core/classify.py:37-45` (`is_touch_pad`: `_TOUCH_MARKERS` `:24` tested over the whole `nick:name` string); callers `pcb/assembly.py:979` (FD-001 SMD count), `:949` (TP references), `pcb/copper.py:1266`, `schematic/system_analyses.py:1963`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-touch-pad-library-nickname`; ruling D6 concern)

**Symptom:** the ruling names one part: hackclub ESP Drone SW1 `ESP32_TouchDown_lib:slide switch spdt` drops from the FD-001 SMD count (72→71). In the 11b-1 std PCB snaps, 503 footprints on 11 units have "touch" only in the nickname. NLoy Touch_Keyboard_10x12 alone has 417 (`Touch_Keyboard_Footprints:C_0402_1005Metric` 159, `SK6812-MINI-E_ROTATED` 117, `SW_MX_1u` 109; 168 of its SMD footprints), but the board has 4 fiducials, so FD-001 does not change there. Others: ESP Drone 57, cnlohr usbtouch 8, socfpga CapSense ×6.

**Fix direction:** match the nickname only together with an electrode-like footprint name or pad shape, or keep the nickname test for net-less / single-pad footprints. Ruling P3 kept the nickname to avoid losing real electrodes. Budget FD-001 count text.

### KH-1055: EG-001's series-clamp credit tests the far net for power or ground by name only, so an unnamed VBUS passes as a signal

**Severity:** LOW (up to 4 EG-001 info findings lost, ruled)
**File:** `skills/kicad/scripts/cross_analysis.py:378-395` (far side: `not _is_power_net(far) and not is_ground_name(far) and not is_power_net_name(far)`); `rails` (nets with a `#PWR` / `#FLG` symbol) is built at `:396` but not used for the far side
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-eg001-far-side-name-only`; ruling X5 doubtful credits)

**Symptom:** Spark-AE ×2: USB-C CC lines with 56 kΩ pull-ups to an unnamed VBUS net are credited as protected through the "series part" path. Also AgonLight2 (CC2 via 5.1 kΩ to a clamped D+) and LibreSolar pwm-2420 `SOLAR-` (12 kΩ to a varistor-clamped `BAT+`).

**Fix direction:** reject a far net that carries a power symbol, a rail voltage, or a power pin, and add a value ceiling for the series part. Budget EG-001 info additions. KH-656 (b) follow-up.

### KH-1054: a multi-letter `P…` reference whose library does not resolve falls back to `P` = connector, over a Device R / C / L / LED symbol

**Severity:** LOW (false EG-001 on one board seen; the parts vanish from type-keyed detectors)
**File:** `skills/kicad/scripts/kicad_core/classify.py:113` (`"P": "connector"`), single-letter fallback `:393-403` (the Device R/C/L override applies only when the fallback type is resistor or inductor); lib fallbacks `:300-389` test `"resistor" in lib`, not `Device:R_Small`, and an LED needs `led` + `diode` in the lib
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-pd-prefix-resistor-connector`; ruling X4 concern)

**Symptom:** probe at the candidate: `classify_component("PD1", "Device:R_Small", "10K")`, `("PWR1", "Device:LED", "RED")`, `("PS1", "Device:R", "1k")`, `("PL1", "Device:L", "10u")`, `("PC1", "Device:C", "1u")` all return `connector`. Gate candidate schematic snaps: PD refs typed connector 16 (11 `Device:R_Small` on 2 CRImier units, incl. vaio_re PD1..PD10, plus an LED and a PLUS153DN). PWR refs typed connector 128 on 77 units, of which at least 20 are LEDs (sirboard ×8, HadesFCS ×2, MAIANA ×3 …) and one an SPDT switch (`Korean Hroparts Elec SPDT:K3-1270L-F1`, ORBIT). vaio_re PD1 gets the 1 accepted false EG-001.

**Fix direction:** let a stock Device passive / LED symbol outrank the `P` fallback, as it does for `R` / `L`. Budget `components[].type` and downstream on the affected units. Same principle as KH-1033 (`V` fallback).

### KH-1053: a design net named VCC / VDD becomes the bench's own supply node (ngspice node names fold case)

**Severity:** LOW (info results with impossible values: 632 A on-current)
**File:** `skills/spice/scripts/spice_templates.py:1200` / `:1229` (`VCC vcc 0`), `:1102` / `:1131` (`VDD vdd 0`) with design nets from `_sanitize_net` (`spice_models.py:165`, `VCC` / `Vcc` / `VDD` pass through unchanged)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-spice-bench-supply-node-collision`; ruling S2 concern)

**Symptom:** baseline quick_200 counts match the handoff exactly. NPN collector on `VCC`: 166 info results, the load resistor shorted (`RLOAD vcc VCC`), reporting `ic_on_mA: 632043.0` (0Prashant edc Q1, daveho DIY8bit Q701). NMOS drain on `VDD`: 1 (embeddedalpha BLCx_XESCv2 `Q?`, 1,673 mA). PMOS drain on `VDD`: 2 (ovobot XCS-03A Q3 ×2, drain shorted to source, `vth_V: 0.0`; the candidate removes that value under sp-transistor-failed-sweep).

**Fix direction:** give bench-internal nodes names a design net cannot take (e.g. `_bench_vcc`), or rename a colliding design net. Budget value changes on the ~169 results.

### KH-1052: an NPN collector or NMOS drain on ground benches the load resistor alone and reports its 3.3 mA as the on-current

**Severity:** LOW (info-status values that measure the bench, not the part)
**File:** `skills/spice/scripts/spice_templates.py:1232` (`RLOAD vcc {collector} 1k`, NPN), `:1134` (`RLOAD vdd {drain} 1k`, NMOS); the load-on-ground guard exists only for PNP (`:1171`) and PMOS (`:1052`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-spice-npn-nmos-load-on-ground`; ruling S2 finding)

**Symptom:** with the collector / drain sanitized to node `0`, `RLOAD` runs from the supply straight to ground, so `i(VCC)` is 3.3 V / 1 kΩ at every drive level. Baseline quick_200 (`f53d107e`): NPN with collector on ground, 58 results (34 info reporting `ic_on_mA: 3.3`, 18 skip, 6 warn), e.g. Fihdi Eurorack Voice Q11 and Apple II CPU Q5. NMOS with drain on ground, 25 info reporting `i_on_mA: 3.3`, e.g. EBOThor LedDimmer Q5 / Q6. The handoff's NPN 64 is a candidate-side count that this draft could not check, because the candidate spice-offline lane had not run.

**Fix direction:** apply the same "load on ground: no switching bench" skip to NPN and NMOS (ruling S2 budgets the rule for all four polarities if the reach stays small). Budget info→skip on ~60 + 25 results.

### KH-1051: SPICE benches fail on duplicate element names (decoupling `R_esr_<ref>`, inrush capacitor cards) and on a design net named after an ngspice keyword (`OFF`)

**Severity:** LOW (each failure is a skipped bench, now visible as a diagnostics record after KH-480)
**File:** `skills/spice/scripts/spice_templates.py:1422-1424` (decoupling: `R_esr_{spice_ident(ref)}`, `L_par_…`, `C…` from the reference alone), `:1638` (inrush: one `C` card per output cap reference); `skills/spice/scripts/spice_models.py:165-186` `_sanitize_net` (no keyword escape: `OFF` stays `OFF`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-spice-duplicate-or-keyword-elements`; ruling S3; survey E3 named the first cause `KH-new-spice-decoupling-duplicate-esr`)

**Symptom:** the 108 failed runs that S3 now records are 99 decoupling benches with a repeated or `?` capacitor reference ("r_esr_c? rail n_esr_1 10m device already exists, bail out"), 5 inrush benches with a repeated cap card, and 4 PNP benches whose base net is `OFF`. The baseline quick_200 payload shows the last group: sPyOpenSource TeslaCoil Q6 / Q7 (base `OFF`) skip as "Simulation failed". ngspice reads `OFF` on a device line as the initial-condition keyword.

**Fix direction:** make element names unique per bench (suffix an index when a reference repeats or is `?`), and prefix design nets that collide with ngspice keywords (`off`, `on` …) in `_sanitize_net`. Budget spice-offline skip→measured moves and diagnostics removals.

### KH-1050: CP-002 reports "no opposite-layer copper" on mousebite / panel footprints that carry only holes

**Severity:** LOW (info noise on panels)
**File:** `skills/kicad/scripts/pcb/copper.py:1051` `analyze_copper_presence` (every footprint with pads is classified, `:1082-1133`; no test for `board_only` / `virtual`, NPTH-only pads or net-less footprints), CP-002 `:1222-1229` (only the passive-ref regex is excluded)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-cp002-virtual-footprints`; ruling D1 concern 2)

**Symptom:** D1 (mixed-token footprints read) adds 68 CP-002 on KiKit mousebites on 2 panels. The class is older and wider. The 11b-1 std PCB snaps already have 318 CP-002 on mousebite footprints on 42 units (fc 86 / 6), from Keebio-Parts `breakaway-mousebites` 70, a `10-My-Footprints:mousebite` 56, `Panelization:MouseBite3-2mm` 48, `local-libraries:mousebite` 28 and others. Of the 318, 268 are typed `through_hole` with no `board_only` / `exclude_from_pos` flag, and none has a pad net. The attribute test alone would miss them.

**Fix direction:** skip footprints with no copper pad (NPTH only) or no pad net, plus `board_only` / virtual ones. Budget CP-002 removals.

### KH-1049: MIC2305x (4 MHz) is not in `_KNOWN_FREQS`, so it gets the 500 kHz topology default

**Severity:** LOW (EMC harmonic bands, VS-002 spacing and power estimates use 1/8 of the real frequency)
**File:** `skills/kicad/scripts/kicad_core/parts.py:349` (`_KNOWN_FREQS`, no MIC2305 key), `:472-481` lookup, `:484-498` defaults
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-mic2305x-frequency`)

**Symptom:** gate candidate schematic snaps: 14 PR-DET records on 9 units are MIC23050 (`-SYML`, `-4YML`, `-GYML`, and legacy `_SYML` / `_GYML`), all `switching_frequency_hz: 500000.0`, `freq_source: topology_default`. Units: Wren6991 RISCBoy, Apex-Ottawa-Team Motherboard, embeddedalpha IMU_V100 ×3, cmcquinn replicookie ×2, lnsru melexisToFcamera4layer ×2. The MIC23050 is a 4 MHz part. Downstream: full-chain EMC SW-001 harmonics and the VS-002 text above.

**Fix direction:** add `MIC2305` at 4 MHz (datasheet-cited; Checklist 11 entry). Budget PR-DET `switching_frequency_hz` / `freq_source` on the 9 units and the EMC / cross text. KH-476 is the same table-gap class for other parts.

### KH-1048: VS-002 replaces its 100 MHz default with any known frequency, however low, so a 500 kHz default or a 32.768 kHz crystal sets a stitching spacing of metres

**Severity:** LOW (recommendation text and the sparse-grid finding on `--full` boards)
**File:** `skills/kicad/scripts/cross_analysis.py:215-230` `_get_highest_frequency` (max over crystal `frequency` and PR-DET `switching_frequency_hz`, including `topology_default` 500 kHz), `:1123` `check_via_stitching_density`, `:1141-1145` (100 MHz only when nothing is known)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-vs002-low-frequency-spacing`; ruling G1 concern 1)

**Symptom:** the slug says "lowest known frequency". The code takes the highest known one, but any known value wins over the 100 MHz default even when it is far below it. λ/20 then grows with it: 500 kHz gives 14,639 mm, a 32.768 kHz crystal 223,366 mm. 11b-1 full-chain cross snaps: 682 VS-002, 44 with a recommended spacing > 73 mm (λ/20 at 100 MHz), 22 > 1 m, most on "No ground stitching vias found". Examples: farmerbriantee Ace ×3, kaminaris GigaESC at 14,639 mm, the hackpad Wio LR1121 module at 223,366 mm. IMU_V100 moves 73 → 14,639 mm at this gate when its MIC23050 becomes a PR-DET (see KH-1049). EMC VS-001 does the opposite: it starts at 50 MHz and only raises it (`emc_rules.py:1505-1514`).

**Fix direction:** take `max(default, known)`, as VS-001 does, and ignore `topology_default` frequencies. Budget VS-002 recommendation text and sparse-grid findings on full-chain units.

### KH-1047: a regulator enable without a datasheet threshold is accepted for any driving voltage, so a 1.8 V output into an EN with VIH ≈ 2 V is not reported

**Severity:** LOW (missed weak-drive case; needs datasheet data to judge)
**File:** `skills/kicad/scripts/validation_detectors.py:547-565` `_en_endpoint_compatible` (datasheet path `:556-563`; otherwise an EN-named pin on a regulator-like part is compatible whatever `v_min` is, `:564-566`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-en-vih-low-drive`; survey G2 item 5)
**Target:** 3.1 (datasheet-backed)

**Symptom:** after G2, VM-001 correctly drops "overdrive" on load-switch enables. On 4 of the removed nets, though, the driver is a 1.8 V output (TUSB1210 / USB3320 CPEN) into an enable whose VIH is about 2 V (TPS2051B, MIC2025). With no extraction the code returns compatible from the pin name alone, so the under-drive goes unseen.

**Fix direction:** when the lowest domain on the net is below a conservative EN VIH (or below the extracted `en_v_ih_max`), emit an info / warning for under-drive instead of accepting by name. Datasheet-backed in 3.1.

### KH-1046: DO-DET "Regulator … missing capacitors" tests only the rails of the decoupling analysis, which skips unnamed and non-power-named nets, so a regulator with caps on such a net always reads "missing"

**Severity:** LOW (info observation, but wide: about 2,700 false entries)
**File:** `skills/kicad/scripts/signal_detectors.py:3844` (`decoupled_rails` = rails of `decoupling_analysis`), `:3885-3896` (`regulator_caps`); the decoupling pass skips `__unnamed_` nets and anything `ctx.is_power_net` rejects, `:1257-1262`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-regcaps-unnamed-input`; survey G4 item 5)
**Target:** v3.0.3

**Symptom:** the slug names the input side (Apex Motherboard U2 MIC23050: C16 4.7 µF sits on input `__unnamed_31`). The output side is the same. Census of the gate candidate schematic snaps: 7,691 `regulator_caps` entries, of which 3,755 on 2,298 units name an unnamed net (2,025 input, 1,730 output). In a random sample of 300 of those, 216 have a capacitor directly on the named net (121/152 input, 95/148 output). A named net that is not a power name (e.g. a filtered regulator input) takes the same path, and those are not counted here.

**Fix direction:** test the capacitors on the net itself (or the PR-DET record's own `input_capacitors` / `output_capacitors`), not membership in the decoupling rails. Budget DO-DET `regulator_caps` removals (~2,700) and rollups.

### KH-1045: VM-001's regulator-likeness is a part-number prefix list that misses most regulators PR-DET finds, so their enables are checked as logic inputs

**Severity:** LOW (false VM-001 / `needs_level_shifter` on EN pins of unlisted regulator families; it also blocks KH-1036)
**File:** `skills/kicad/scripts/validation_detectors.py:531-544` `_is_regulator_like` (prefixes `TPS6`, `TPS5`, `LM25`, … `REG`, or `type == 'power_regulator'`); used by `_en_endpoint_compatible` `:547-565` and the cross-domain pass `schematic/net_analysis.py:578`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-reglike-from-prdet`; survey G3 item 5, ruling P3)
**Target:** v3.0.3 (with KH-1036)

**Symptom:** census of the gate candidate schematic snaps: 9,431 of 13,578 PR-DET records (6,047 units) are not regulator-like by this test. The largest groups are LM1117, L7805, XC6206, MCP170x, TLV625, LD1117, AZ1117, AP6320, MCP182x, MIC550x and LP2985. Survey G found 239 VM-001 endpoints on an EN pin of a non-regulator-like part. In dpmj lora-payload, the LP5912 EN behind a TPS62912 PG is judged against a 1.8 V domain. That is the existing "Net PG_3V6RF: 3.6V / 1.8V" error, and it is why the KH-1036 fix alone adds 3 false `needs_level_shifter`.

**Fix direction:** treat a part with a PR-DET record as regulator-like (pass the detector result into the context). Budget VM-001 removals and `needs_level_shifter` flips. Land it with KH-1036.

### KH-1044: the shared `LOAD_SWITCH_KEYWORDS` misses the AP2265x / AP2280x / AP2261x / AP255x / SiP32 / MIC20xx / FPF families, so 58 load switches are PR-DET LDOs; VM-001's local family list matches substrings anywhere in the text

**Severity:** LOW (false regulator records feed power tree, rail sources and power_path)
**File:** `skills/kicad/scripts/kicad_core/parts.py:7-17` (`LOAD_SWITCH_KEYWORDS`, used by the regulator screen `signal_detectors.py:1692` / `:1841`, the power-path detector and the RS-001 switch chain); `skills/kicad/scripts/validation_detectors.py:528` (`_LOAD_SWITCH_FAMILIES`, VM-001 only), `:542-544` (bare substring over MPN + value + lib_id)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-load-switch-families`; survey G2, ruling P1)
**Target:** v3.0.3

**Symptom:** census of the gate candidate schematic snaps: exactly 58 PR-DET records on 52 units are one of the VM-001-local families, all typed `LDO`. Leading values: AP22653 23, AP22615 8, MIC2025 5, AP22802 5, AP22652 4. The VM-001-local tuple (225 parts / 156 units hit) is a plain substring over value, MPN and the full lib_id, so the symbol name decides. TDA2002 (an audio amplifier) drawn on an `FPF2002` symbol, and LP5907 (an LDO) on a `MIC20XX` symbol, both read as load switches.

**Fix direction:** fold `_LOAD_SWITCH_FAMILIES` into the shared list (ruling P1), match family prefixes at a part-number boundary on value / MPN before the lib_id, and budget the ~58 PR-DET removals plus power_path / RS-001 moves. Related: KH-920 (load switches typed LDO, fixed for the listed families) and KH-946.

### KH-1043: EG-001's direct protection check credits any PD-DET `protected_net`, fuses and reverse-polarity diodes included

**Severity:** LOW (EG-001 is info; a fuse or reverse-polarity diode on a connector signal line hides the ESD gap)
**File:** `skills/kicad/scripts/cross_analysis.py:357` `check_esd_coverage_gaps`, `:363-369` (`protected_nets` from every PD-DET record, any `type`); PD-DET emits `fuse` and `reverse_polarity` records with `protected_net` (`signal_detectors.py:2571` `detect_protection_devices`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-eg001-fuse-credit`; survey F1 KH-656 (b) item 5)
**Target:** v3.0.3 (with KH-656 (c))

**Symptom:** the series-clamp path (KH-656 (b), `:378-379`) admits only `esd_ic`, `diode`, `varistor` and `surge_arrester` clamps. The direct path takes every record type, so a PTC fuse or a series reverse-polarity diode on a connector net counts as ESD protection. Reach not measured (the gate's cross snaps were not written when this was drafted). Most fuses sit on rails, which EG-001 skips anyway.

**Fix direction:** apply the same clamp-type set to the direct check. Budget EG-001 info additions.

### KH-1042: the thermal assessment reads Tj max only from v1.3 extractions, while TJ-001 reads the v1.4 `absolute_max.TJ_max`

**Severity:** LOW (needs a trusted v1.4 extraction; no corpus extractions)
**File:** `skills/kicad/scripts/analyze_thermal.py:173-205` `_get_datasheet_thermal` (`absolute_maximum_ratings.junction_temp_max_c` only, `:194-198`; `find_extraction(..., v14_first=False)`), `:435-436` (`tj_max` / `tj_max_source` fall back to `default_125`); TJ-001 `skills/kicad/scripts/lookup_detectors.py:308`, `:344-350` (`_resolve_key(am_block, TJ_SYNONYMS)`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-thermal-v14-tjmax`; survey E10)
**Target:** 3.1 or v3.0.3 (survey)

**Symptom:** the slug says the v1.4 `TJ_max` "is still not read". That is half right. TJ-001 reads it, but the per-part assessment (`tj_max_c`, `margin_c`, TS-001/TS-002/TS-003 and the `default_tj_max` missing-info list) does not. With only a v1.4 extraction, one part is judged against 125 °C by TS-00x and against the datasheet value by TJ-001, and it is listed as missing a Tj max. Corpus reach is 0 (no `datasheets/extracted` in the corpus).

**Fix direction:** read Tj max through the same v1.4 facts path as TJ-001 (fall back to v1.3), and mark `tj_max_source: datasheet`. KH-430 is the θJA half of the same reader gap.

### KH-1041: ES-001 pairs a protection device with the nearest connector by distance only, even when they share no net

**Severity:** MEDIUM (an ES-001 warning that names the wrong connector. It is the majority case on the baseline, though the count is an upper bound.)
**File:** `skills/emc/scripts/emc_rules.py:3196` `check_esd_protection_path`, nearest-connector loop `:3248-3258` (Euclidean distance between footprint origins, no net test); connector set `_connector_refs` `:312`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-es001-shared-net`; survey E4, ruling P3)
**Target:** v3.0.3

**Symptom:** the survey framed this as 33 re-picks after the KH-755 DNP fix (example: candykingdom D1/D5 on `/SW1`/`/SW2` reported "far from J1", the USB connector 25 mm away). The gap is older and wider. In the 11b-1 trees, 671 of 1,046 std ES-001 findings (321 units) and 64 of 103 fc (35 units) name a connector whose PCB `connected_nets` share no non-ground net with the device. Pin headers (82) and sockets (54) lead. That count is an upper bound, because a device behind a series resistor also shares no net. A sample also shows non-connectors picked through the P-prefix rule: ConnectBox U9 paired with pushbutton PB1 (see KH-1061).

**Fix direction:** prefer a connector that shares a signal net with the device, or reaches it through one series part (the EG-001 KH-656 (b) rule). Use distance only to rank those candidates. Budget ES-001 component / text changes and removals.

### KH-1040: board net classes use `trace_width` / `via_dia`, project classes `track_width` / `via_diameter`; the impedance signal and the net-class summary read only `track_width`

**Severity:** LOW (one design-intent signal and one informational summary miss KiCad 5 board classes; no finding)
**File:** `skills/kicad/scripts/pcb/reader.py:2128` (`extract_net_classes` keys `clearance`, `trace_width`, `via_dia`, `via_drill`, `uvia_dia`, `uvia_drill`); `skills/kicad/scripts/kicad_core/project.py:630-631` (`.kicad_pro` classes: `track_width`, `via_diameter`); consumers `skills/kicad/scripts/design_intent.py:186-192` ("controlled impedance net classes present"), `skills/kicad/scripts/pcb/dfm.py:1127-1128` (`net_class_summary.track_width_mm`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-netclass-keys`; survey D)
**Target:** 3.1 (renaming the keys is an output shape change)

**Symptom:** the top-level `net_classes` holds project classes on KiCad 6+ boards and board classes on KiCad 5 boards, under different key names for the same values. `design_intent` tests `nc.get('track_width')`, so a KiCad 5 board class never counts. Census of the 11b-1 std PCB snaps: 1,481 units carry a non-Default board class with `trace_width`, and none of them has the impedance signal. 2,693 units carry project classes with `track_width`.

**Fix direction:** one key set for both sources (3.1), or read both spellings in the two consumers now. Budget `design_intent` signals and confidence on the ~1,481 units. This interacts with KH-763's full form (board classes in `net_classes`), which is also 3.1.

### KH-1038: `classify_inductor_shielding` still reads `NON SHIELDED` (with a space) as shielded

**Severity:** LOW (one spelling)
**File:** `skills/kicad/scripts/kicad_core/classify.py` `classify_inductor_shielding`
**Discovered:** 2026-11-07, harness, verifying the KH-557 closure at `f53d107e` (code read)

**Symptom:** the semi/non-shielded words are tested before `SHIELDED` now (KH-557), but the spaced form `NON SHIELDED` is not among them, so it matches `SHIELDED`.

**Fix direction:** normalise spaces / hyphens / underscores before the word test.

### KH-1037: `cache_reader.lookup` reads `<sanitize_mpn>.json` with no recorded-MPN check, so MPNs that sanitize alike share one extraction

**Severity:** LOW (needs a collision in the cache; a datasheet-backed value from another part)
**File:** `skills/datasheets/datasheet_types/cache_reader.py:280-284` `lookup`
**Discovered:** 2026-11-07, harness, verifying the KH-986 closure at `f53d107e` (code read)

**Symptom:** KH-986 made `find_extraction`'s file-name fallback check the file's recorded MPN. `cache_reader.lookup` still opens `<sanitize_mpn>.json` directly, so `BAV99 215` reads the v1.4 file written for `BAV99/215`. Its docstring accepts rare collisions.

**Fix direction:** check the record's `mpn` (as `_records_mpn` does) or route through `find_extraction`.

### KH-1036: the cross-domain pass exempts a regulator power-good pin unconditionally, while VM-001 now judges it at its pull-up rail

**Severity:** LOW (`design_analysis.cross_domain_signals[].needs_level_shifter` says false where VM-001 fires)
**File:** `skills/kicad/scripts/schematic/net_analysis.py:578-581`; VM-001 rule `skills/kicad/scripts/validation_detectors.py:593-603`, `:677-684`
**Discovered:** 2026-11-07, harness, verifying the KH-461 closure at `f53d107e` (code read)

**Symptom:** KH-461 aligned the cross-domain pass with VM-001 for enables. VM-001 now treats a regulator PG as open-drain and judges it at its pull-up rail, but the cross-domain pass still drops every PG endpoint. A PG pulled up above its receiver makes VM-001 fire while the cross-domain entry says no level shifter is needed.

**Fix direction:** share VM-001's endpoint rule (open-drain at the pull-up rail) in the cross-domain pass instead of a PG exemption.

**2026-11-08 (v3.0.2 Wave 11b-2, ruling P3):** moved to v3.0.3 with KH-1045. The G3 fix alone adds 3 false `needs_level_shifter: true` on dpmj lora-payload (TPS62912 PG pulled to +3V3_D into the LP5912-1.8 / -3.3 EN, LP59xx not regulator-like). Unchanged at `6138b126`: `schematic/net_analysis.py:578-582` still exempts a PG-named pin on any regulator-like ref. Since G2, `_is_regulator_like` (`validation_detectors.py:531-544`) also returns true for load switches, so a load switch's pin named `PG` / `PGOOD` / `PWRGD` / `NPG` (`_PG_PIN_PATTERNS`, `validation_detectors.py:525`) is exempt too.

### KH-1033: the `V` reference prefix types parts varistor over their library symbol: GOST-style `VD` diodes / bridges, `VT` transistors and even ICs (650 parts / 101 corpus units)

**Severity:** MEDIUM (diodes, transistors and ICs vanish from every type-keyed detector and appear as varistors in protection / ES-002)
**File:** `skills/kicad/scripts/kicad_core/classify.py:108` (`"V": "varistor"`), varistor overrides `:196-206` (pot, jumper / connector, regulator only)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey C1 (harness ask, named as the `VD100` D_Bridge); verified by the harness at `f53d107e` (probe + corpus)

**Symptom:** probe: `classify_component("VD100", "Device:D_Bridge_+-AA", "DB107")`, `("VD1", "Device:D", "1N4148")`, `("VD2", "Device:D_Zener", "BZX84")` and `("VT1", "Device:Q_NPN_BEC", "BC847")` all return `varistor`. Corpus census of the candidate snaps (36,463 schematic units): 650 parts on 101 units with a `V[DTSU]n` reference typed varistor: VD + diode symbols 257 (realizator/stereopi `VD4` `Device:D_Schottky_Small`), VT + BJT 117, VT + `gost_common:VT_NPN_EBC` 51, VT + `Q_NPN` 35, jotego/jtcores 74LS ICs on VD refs (~80), `Device:LED_RGBA` VD4 (E440QF/FOSSerZero), `1N4007`.

**Fix direction:** add the GOST prefixes (`VD` diode, `VT` transistor, `VS` thyristor, `VU` IC) and let a library symbol that names a diode / transistor / LED / IC outrank the single-letter `V` fallback. Budget `components[].type` and downstream detectors with a corpus census.

**2026-11-08 (v3.0.2 Wave 11b-2 gate, ruling M1 concern 1):** the plain `V<n>` prefix has the same fault outside the `V[DTSU]n` census. bobbycar-graz Bobbycontroller V1..V13 are `Transistor_FET:BSP89` MOSFETs (CRSS042N10N / NCE0115K), all typed `varistor`. PD-DET then lists them as protection. Before the fix wave the KH-755 fix made 10 of them false ES-001 adds; at `6138b126` ES-001 is removal-only and none fires on them, but they are still protection devices to every PD-DET consumer. Gate candidate census of plain `V<n>` references typed varistor on a transistor / diode / LED / IC symbol: 39 parts on 9 units (BSP89 16, `Device:D` 6, BC546 / 2N3904, `Device:Q_NMOS_SGD`, `Device:LED`, 74LS ICs). The fix direction already covers it: a library symbol naming a transistor / diode / LED / IC outranks `V`.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, candidate db551674; slug KH-new-vr-regulator-varistor):** `VR` is not in the prefix map, so a `VR<n>` reference falls back to `V` → varistor (`kicad_core/classify.py:395`). The override returns `ic` only for a "regulator" lib / footprint or six value families (`:431-438`). Couby/OpenBCI_hardware_KiCAD `OpenBCI.sch` VR1 TPS72325 (legacy lib_id `TPS72325`, footprint `SM`) is typed varistor and has no PR-DET record. Survey G's KH-964 rule had to drop its `type == ic` requirement because of this part. `VR` names a voltage regulator (US practice) or a variable resistor (Asian practice). Map it to a regulator, keep the potentiometer override, and let an IC-like value or pin set win over `varistor`. See also KH-1084: `VR` + `Regulator_Switching` is typed `switch`.

### KH-1032: PP-001 reports a false error on an IC's internal-regulator output pin typed `power_in` when the net is unnamed (ST25R3916 VDD_DR)

**Severity:** MEDIUM (error-severity false finding on a real design)
**File:** `skills/kicad/scripts/signal_detectors.py:4944` `audit_power_pin_dc_paths`; the internal-LDO demotion tests the net name only, `:5133-5138` via `_is_module_internal_rail(net_name)` `:4927-4935`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey B1 (harness ask 5) and final review; verified by the harness at `f53d107e` (corpus)

**Symptom:** candidate snap cbwhickstein/Flipper_Zero_DIY `NFC.kicad_sch`: PP-001 error "IC power pin RDD1.14 (VDD_DR) has no DC path to a power rail (net '__unnamed_15')". VDD_DR is the ST25R3916 driver-regulator output, typed `power_in` by the symbol, decoupled by RC29. Exposed this wave when RC29 stopped being typed resistor (a 0 Ω "bridge"); 2 units.

**Fix direction:** apply the internal-rail patterns to the pin name too (VDD_DR, VDD_A/D, VREG, VCAP, VDDCORE …), or exempt a `power_in` pin whose net holds only that IC's pins and caps (decoupling-only node), demoted to info.

### KH-1031: a legacy symbol whose library is missing falls back to the built-in `D` (pin 1 = K), reversing a project diode whose pin 1 is the anode

**Severity:** LOW (diode A/K names swapped on legacy boards with a missing rescue / cache library; consumers that read pin names get the orientation backwards)
**File:** `skills/kicad/scripts/schematic/legacy_reader.py:117-124` (built-in `D` / `D_Schottky`: 1 = K, 2 = A), `:584-600` (built-ins added for any missing name); `skills/kicad/scripts/schematic/pipeline.py:1016-1038` (`nick:D` → bare `D` → built-in, `_pin_source: builtin`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey B1 (harness ask 5); verified by the harness at `f53d107e` (code read)

**Symptom:** crazyflie rescue-backup D1: the rescue cache library is not found, so `…-rescue:D` takes the built-in pin map and reads A on +BATT; the project's KiCad 5 `.net` and main `.sch` give pin 1 (A) on the drain, pin 2 (K) on +BATT. TR-DET now ignores built-in pin names for flyback orientation (Wave 11b-1), so that detector is unchanged; other pin-name readers are not guarded. Visible only as `legacy_analysis_quality` `builtin_fallback` counts.

**Fix direction:** for polarized built-in fallbacks, do not assert A/K names (leave the pins unnamed), or take the orientation from the project's `.net` when present.

### KH-1030: AD-DET admits any IC whose library nickname names an ADC, and takes its resolution from that nickname (OLIMEX BB-ADS1262: MT3608 and AP2127K reported as 32-bit ADCs)

**Severity:** LOW (false AD-DET records on boards whose project library is named after their ADC)
**File:** `skills/kicad/scripts/domain_detectors.py:3027-3032` `_ADC_IC_KEYWORDS`, `:3210-3222` (admission over value + full `lib_id`), `:3250` (`_infer_adc_resolution(value, lib_id)` falls back to the lib_id)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey B1 (harness ask 5); verified by the harness at `f53d107e` (code read + probe + corpus)

**Symptom:** probe: `MT3608` / `BB-ADS1262:MT3608` and `AP2127K` / `BB-ADS1262:AP2127K` pass the `ads1` keyword and resolve to 32 bits. Candidate snap OLIMEX/BB-ADS1262 `BB-ADS1262-Rev.A.sch`: AD-DET U1 ADS1262 32, U2 `MT3608(SOT23-6)` 32, U3 `AP2127K-ADJ` 32. Pre-existing; this wave's table change moved them 24 → 32. The VREF phase (`:3131-3145`) has the same nickname read.

**Fix direction:** match keywords and stems on value, MPN and the symbol name only (drop the nickname), as `match_family` does.

**Addendum 2026-11-11 (TH-109 triage, FND-00000383-AST-02):** on both OLIMEX BB-ADS1262 revisions (Rev.A, Rev.A1) the MT3608 (U2) and AP2127K-ADJ (U3) have no `detect_power_regulators` finding and no regulator_caps observation at product `6138b126`; they appear only in the ADC findings with U1. The reviewed finding says Rev.A once reported both regulators, so the misclassification also loses the regulator record.

### KH-1029: a KiCad 5 `.sch` sub-sheet whose file is missing is dropped silently (the legacy twin of KH-481)

**Severity:** LOW (provenance; 82 corpus files / 255 sheet refs per survey A)
**File:** `skills/kicad/scripts/schematic/legacy_reader.py:1067-1070` (`if sub_path.exists()` with no else; no `missing_sheets`, no backslash replace); compare `schematic/reader.py:1345-1366` and `schematic/hierarchy.py:341-347`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey A (harness ask 5); verified by the harness at `f53d107e` (code read)

**Symptom:** the `.kicad_sch` reader now records "sheet file X named in Y does not exist" (missing sheet skipped). The legacy reader appends only sheets that exist and records nothing, so the design is analysed without the sheet and `diagnostics` stays empty. It also joins `base_dir / sheet_file` without the backslash replace.

**Fix direction:** collect missing legacy sheets the same way and record them through `parse_all_sheets`; normalize backslashes. Budget: `diagnostics[]` additions on the legacy units (v3.0.3).

### KH-1028: symbol instance resolution rescans every `(instances …)` path entry for each sheet instance, O(instances²) per symbol (discrete-nes ram > 300 s in `parse_all_sheets`)

**Severity:** MEDIUM (the remaining parse cost on ram.kicad_sch, a standard-profile timeout; neutral fix)
**File:** `skills/kicad/scripts/kicad_core/instances.py:48-81` `inline_instances` (walks all path entries), `:26-46` `resolve_instance` (linear scan); caller `schematic/reader.py:859-883` (per symbol, per sheet instance, also the `si_by_uuid` loop at `:862`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey A (harness ask 5); verified by the harness at `f53d107e` (code read + gate status)

**Symptom:** each sheet instance re-reads a symbol and rebuilds and scans the list of all its instance paths, one per instance of that sheet, so the work grows with the square of the instance count. Survey A: ram `parse_all_sheets` > 300 s both with and without this wave's per-file parse cache (row_group fell from 295 to 30 s with it). The running gate records `boards_ram_ram.kicad_sch` as a timeout on both sides (120.1 s).

**Fix direction:** index each symbol's instance entries by normalized path once per file (cached with the parse tree) and look the instance up by key.

### KH-1027: `ic_pin_analysis[*].pins[*].connected_to` lists every other pin on the net for every IC pin, so output grows with pins × net size (4.2 GB on discrete-nes row_group)

**Severity:** MEDIUM (output size; with the sheet cache, row_group reaches serialization inside the 120 s cap and needs > 8 GB to encode, MemoryError under an 8 GB limit)
**File:** `skills/kicad/scripts/schematic/ic_analysis.py:309-335` (`neighbor_summary` built from every `get_net_neighbors` entry, stored as `connected_to`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey A (harness ask 5); verified by the harness at `f53d107e` (code read + gate status)

**Symptom:** each IC pin on a shared bus or rail carries a dict per neighbour (ref, value, type, pin, pin name), so N ICs on one net give N² entries. Survey A measured row_group's output at 4.2 GB, 3.9 GB of it `connected_to`. The running Wave 11b-1 gate still records `AlexColello/discrete-nes/boards_ram_row_group.kicad_sch` as a timeout on both sides.

**Fix direction:** cap or summarize `connected_to` (counts by type plus the first few neighbours, or neighbour refs only). Output-changing; needs its own budget (3.1 / v3.0.3).

### KH-1026: `simulate_subcircuits.py` checks for a simulator before refusing a symlinked `--workdir`, so the symlink test fails when ngspice is absent

**Severity:** LOW (test-only failure; without a simulator the CLI still exits 1 and writes nothing)
**File:** `skills/spice/scripts/simulate_subcircuits.py:609-617` (simulator detection returns 1) before `:667-670` (symlink refusal) `main`; test `tools/tests/test_spice_workdir.py:169-183` `test_a_workdir_that_is_a_symlink_is_refused`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** with ngspice off PATH the test fails with `'symlink' not found in 'Error: no SPICE simulator found. Install one of: …'`. With ngspice on PATH it passes. The same failure occurs at `727d0ab3`.

**Fix direction:** validate `--workdir` (the symlink refusal) before simulator detection. Alternatively, mock `detect_simulator` in the test.

### KH-1025: the current-sense IC keyword `ina` is a bare substring over value + full lib_id

**Severity:** LOW (pre-existing; no false CS-DET found in a 13k-file scan)
**File:** `skills/kicad/scripts/signal_detectors.py:1362-1369` (`_SENSE_IC_KEYWORDS`, also `"asc"`); matched at `:1322-1323` `_sense_ics_across`, `:1462-1466`, `:1574-1580` `detect_current_sense`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:**
- **The match:** `"ina"` is a plain substring of `value + " " + lib_id` on any `ic`-typed part. It matches instrumentation amps (INA128, INA333, the INA82x family) as sense amplifiers, and library nicknames or symbol names containing "china", "terminal" or "Trinamic". `"asc"` is equally loose.
- **Scope:** only IC-typed parts are tested, so "terminal" matters only on an IC's lib_id.
- **Corpus:** the only non-INA-sense hit was RCMgames RCM-Hardware-BYTE, where TMC7300 matches through `TMC7300-Trinamic`. Its BRA/BRB shunts are real, so that one is right by luck.

**Fix direction:** match sense-amp families by anchored part-number prefixes on the value or MPN (`ina1[89]x`, `ina2xx`, `ina3xx`…), not substrings of the lib_id. Exclude instrumentation amps.

### KH-1024: RS-001 counts power-symbol pins as `power_in` loads, so a rail with no real load reads "carries power_in pins" at deterministic confidence

**Severity:** MEDIUM (5,021 of 15,555 deterministic RS-001 findings, on 3,157 units in 15,866 files scanned, rest only on power-symbol pins)
**File:** `skills/kicad/scripts/signal_detectors.py:4776-4787` `audit_rail_sources` (a `#`-reference power_in pin counts toward `deterministic` / "carries power_in pins"); rail admission `:4661-4673`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** KiCad power symbols have a `power_in` pin. The confidence test accepts a `power_in` pin when its component starts with `#`, so the power symbol that names the net is enough for "Net X carries power_in pins…" (deterministic).
- bluepylons Thinkpad-USB-keyboard BSS138-level-shifter: `+5V` has only `#PWR061` and R11.
- CreateRemoteThread glitcher bifrost: `VCC` has only `#PWR0115` and JP4.
- crice009 toolauth: `+3.3VA` has only `#PWR0154` and J3.

**Fix direction:** exclude `#` references from the power_in evidence, so that such rails take the name-admitted heuristic wording. Output-changing: RS-001 `confidence` and description on these findings; the finding set itself does not change.

### KH-1023: RM-DET takes any `*_Small` symbol as an antenna, because the antenna library keyword `sma` matches `Small`

**Severity:** MEDIUM (about 89 % of corpus RM-DET seeds are not antennas: 658 of 739 findings, 180 units, in the files scanned)
**File:** `skills/kicad/scripts/domain_detectors.py:1340` (`_ant_lib_keywords` includes `"sma"`), substring test `:1347` `detect_rf_matching`
**Discovered:** 2026-11-07, harness verification of the Wave 11b-1 candidate `rm-ferrite-at-value` at `f53d107e` (code read + corpus read)

**Symptom:**
- **The seed:** `"sma" in lib_lower` is true for `Device:C_Small`, `R_Small`, `L_Small`, `D_TVS_Small_Filled` and the like, so each becomes the "antenna" that the matching-network walk starts from.
- **faoziaziz:** D50 `Device:D_TVS_Small_Filled` (PTVS5V0Z1USK) is the "antenna" of the KH-1022 finding.
- **martinribelotta/h730duino:** `power.sch` gets "RF matching_network matching network at C19 / C20" from buck output caps beside 4.7 µH inductors.
- **pfork pitchfork:** each `_Small` part of a real pi network emits its own RM-DET.

**Fix direction:** match `sma` as a token (an SMA connector: `Connector_Coaxial:SMA*`, `\bsma\b`), not a substring. Output-changing: most corpus RM-DET findings go away; measure first.

### KH-1022: inductors written `<n> OHM@<f>` (or `Ohm@`) are not typed ferrite beads, so RM-DET walks them as RF matching elements

**Severity:** LOW (info findings; 2 corpus units seen)
**File:** `skills/kicad/scripts/kicad_core/classify.py:236-240` (ferrite-notation test `\d+[Rr]\s*[/@]\s*\d` only); RM-DET ferrite skip `skills/kicad/scripts/domain_detectors.py:1389-1398`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe + corpus read)

**Symptom:**
- **Typing:** the ferrite test knows the `<n>R@` / `<n>R/` notation only.
- **Probe:** on `Device:L` or `Device:L_Iron_Small`, `330 OHM@100MHZ`, `600Ohm@100MHz` and `600 Ohm @ 100MHz` are typed `inductor`, while `600R@100MHz` and `120R/200mA` are `ferrite_bead`.
- **RM-DET:** its skip looks for `ferrite` / `bead` / `emi` in the description, keywords or value, so an `OHM@` value passes.
- **Corpus:** on faoziaziz/FMU_tampantech `fmu_v1` and `memory`, L14 `330 OHM@100MHZ` (parsed_value None) becomes RM-DET "RF matching_network matching network at D50".

**Fix direction:** extend the ferrite notation to `<n>\s*(R|Ω|ohm)s?\s*[@/]\s*<n>`, case-insensitive. Same family as KH-883 (parse side).

### KH-1021: KiCad 5 rescue symbol names carry the old library or project name, so family matching on the symbol name still reads a library name

**Severity:** LOW (false WL-001 "wifi/ble module" on rescue-symbol parts; a few corpus units)
**File:** `skills/kicad/scripts/detector_helpers.py:105-122` `match_family` (symbol name after `:`, rescue suffix kept); WL-001 `skills/kicad/scripts/domain_detectors.py:5781-5786`; full-lib_id readers `domain_detectors.py:306-307` (isolation keywords) and `skills/kicad/scripts/validation_detectors.py:538-539` (`_is_regulator_like` load-switch match)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** rescue symbols are named `<sym>-<lib>-rescue` or `<sym>-RESCUE-<project>`, and a legacy lib_id may have no `:`. Stripping the nickname therefore leaves the library or project name in the text.
- **WL-001:** on OLIMEX ESP32-EVB Rev B and Rev C, U1 `MCP73833(MSOP10)` (lib_id `MCP73833(MSOP10)-RESCUE-ESP32-EVB_Rev_B`) is "wifi/ble module U1". On ccadic/TI92-revive (×2), IC1 TCA8418 (`kb5-rescue:TCA8418-tca8418-ESP32-S2-WROOM-rescue`) is the same.
- **CERT-001:** the fallback that named `#PWR042` / KXKM J9 is fixed at `f53d107e`; OLIMEX GATEWAY Rev I now names U3.
- **Full lib_id:** the isolation-part and load-switch readers still match the whole lib_id, nickname included. The load-switch match can only remove findings (0 seen).

**Fix direction:** strip a trailing `-<lib>-rescue` / `-RESCUE-<project>` from the symbol name in `match_family`, and use symbol-name matching in the two full-lib_id readers.

### KH-1020: `power_sequencing` makes a regulator `sequenced_after` itself when its own PG and EN share a net

**Severity:** LOW (output field only; `sequenced_after` has no reader in the product)
**File:** `skills/kicad/scripts/schematic/system_analyses.py:1772-1779` `analyze_power_sequencing` (post-loop PG→EN join)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** the join sets `sequenced_after = pg_entry["regulator"]` for every dependency whose `en_net` is the PG net, without excluding the same regulator. On `ISSUIUC/ISS-PCB` TARS-MK2 ACB v0.1 and v1.0, the one `IC?` part (MP2384GG-P) has EN and PG on `3V3_IO_PG` (with R201 and U201 EN), and its dependency reads `sequenced_after: "IC?"`, `sequence_signal: "power_good"`.

**Fix direction:** skip the edge when `dep["regulator"] == pg_entry["regulator"]`.

### KH-1019: TR-DET reads P-channel MOSFETs as N-channel unless the lib_id, keywords, value or description spells out the channel

**Severity:** LOW (flyback, gate-drive and drain/source readings on P-FETs are inverted; about 100 TR-DET records on 58 units in a third of the corpus for a short list of common P-FET MPNs)
**File:** `skills/kicad/scripts/signal_detectors.py:3433-3444` (transistor analysis, `is_pchannel`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** P-channel is decided only from the words `pmos` / `p-channel` / `p_channel` / `pchannel` (plus `dmp` in the value and `p-mos` / `p-mosfet` in the description). An MPN on a part-named symbol is read N-channel:
- `alexreinert/PCB` HB-RF-USB.sch Q1/Q2 `Transistor_FET:IRLML6402` (source on +3V3), and `0Prashant/Kicad` H-Bridge Q4/Q7 IRF9540N.
- gitdoalberto dosimetro Q1 `DMG2305UX-13`, whose description "MOSFET P-CH 20V…" uses `P-CH`, which is not in the list.
- The survey's AO3401A cases are the same.

**Fix direction:** add a P-channel MPN family table (IRLML64, IRF9, AO340x, DMG23, SI23xx P parts…) and accept `p-ch` in descriptions, or read the symbol's pin order or arrow where available.

### KH-1018: OA-DET admits instrumentation amplifiers and labels them `comparator_or_open_loop`

**Severity:** LOW (info findings with a false configuration; at least 31 on 25 units in a third of the corpus)
**File:** `skills/kicad/scripts/signal_detectors.py:2834-2851` `detect_opamp_circuits` (value prefixes `ad8`, `ina10`..`ina13`; description keyword `instrumentation`); INA exclusion `:2855-2857`; configuration `:3084-3085`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:**
- **Topology:** an instrumentation amp sets its gain with RG between its RG pins, with no feedback resistor to −IN, so the op-amp topology code falls to `comparator_or_open_loop`.
- **ExoFlex:** `ExoFlex-Inc/Electrique` ExoFlex_Kicad and loadcells U25-U27, `SymLib:INA823DR`, value "INST OP-AMP", admitted through the description "Instrumentation Amplifier". The `ina8` exclusion misses because it tests the start of `value + lib_part`, and the value comes first.
- **Elsewhere:** Gunethra/ecg U2 `Amplifier_Instrumentation:AD620`, BlueJayRacing bjr_kicad IC1/IC2/U5 AD8237, OeMga-me U1 AD8233.

**Fix direction:** recognise instrumentation amps (library `Amplifier_Instrumentation`, an RG pin pair, or the description) and give them their own configuration, with gain from RG where it can be found. Do not run op-amp topology on them.

### KH-1017: `net_leaf` splits a KiCad 5 label that contains `/`, so the net's own name loses its first part

**Severity:** LOW (6 `net_classifications` values worse on 2 corpus units; nothing user-visible beyond those)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:8-17` `net_leaf`; consumer `skills/kicad/scripts/schematic/net_analysis.py:414`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:**
- **The split:** for a sheet-pathed name, `net_leaf` returns the text after the last `/`. A KiCad 5 label can hold a literal `/` (KiCad 6+ writes `{slash}`).
- **Probe:** `/PX4FMU_SS_8/FMU-I2C2_SCL/3.4A` gives `3.4A`, which classifies `signal`; the label itself classifies `clock`. `/CoreOne/I2S_MCLKC/D3` gives `D3` (`signal` against `clock`).
- **Corpus:** lachlanA/eagle-to-kicad PX4FMUv2.4 and ohdsp/CoreOne.
- **Reach:** 11 call sites use the same helper, so every leaf-based reader sees the same truncation on such labels.

**Fix direction:** strip the known sheet path (the hierarchy prefix the parser built) instead of splitting on the last `/`.

### KH-1016: NC-pin skips test only `no_connect`, so KiCad 5 NC pins (read as `unconnected`) stay in ESD audits

**Severity:** LOW (legacy boards; about 300 EP-AUD records on 126 units)
**File:** `skills/kicad/scripts/domain_detectors.py:2460-2463` `_nc_pins_only`; `skills/kicad/scripts/cross_analysis.py:341-342` (inline copy); legacy pin type map `skills/kicad/scripts/schematic/legacy_reader.py:36` (`"N": "unconnected"`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** the legacy reader types an NC pin `unconnected`. Other readers accept both spellings (`connectivity.py:672`, `ic_analysis.py:305`, `erc_pins.py:51`). The two NC predicates test `no_connect` only, so an unused legacy connector pin counts as an unprotected signal. Corpus: 300 EP-AUD findings on 126 `.sch` units list a net whose only pins are `unconnected`, for example `Meshinger/Meshinger/Meshinger.sch` J5 (ethernet) NC pin and baldengineer Commodore VIC-20 P6 NC.

**Fix direction:** accept `unconnected` in both predicates, ideally through one shared helper (or `erc_pins` normalisation). Output-changing: EP-AUD coverage and records on legacy units.

### KH-1014: MCU internal-SMPS switch pins (`VLXSMPS`) are not switch pins, so the SMPS node gets RS-001 "no declared source"

**Severity:** LOW (a false warning on STM32H7/WB/U5 boards that use the internal SMPS)
**File:** `skills/kicad/scripts/signal_detectors.py:1746` `_screen_regulator_candidate` (switch tokens `{"SW","PH","LX"}` on the stripped pin name); RS-001 rail admission `:4661-4673`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:**
- **Aerolotl:** on `stanford-ssi/Aerolotl_KiCAD/aerolotl.kicad_sch`, the STM32H755 U1 pin `VLXSMPS` (typed `power_in` by its symbol) sits on net `VLX`, with L1 to `VFBSMPS` / `VCAP`. No regulator record covers it, so RS-001 warns "VLX has no declared source".
- **Why the base was silent:** port-H GPIO pins (PH0, PH1) made the MCU a false `ic_with_internal_regulator` record whose switch pin happened to stand in. Now that PH is no longer a switch pin, the SMPS node has no source.
- **Same pattern:** the STM32WB55 and STM32H7A3 records on nets `SMPSLXL` and `SMPS_out` are lost.
- **Not this defect:** the Apple IIGS clock-phase chips (PH0..PH3 and no other port pins) keep false regulator records, which is the opposite case.

**Fix direction:** read `VLXSMPS` / `VLX` (an LX token after a `V` prefix) as an internal-regulator switch node, so the MCU gets an `ic_with_internal_regulator` record that sources the switch and `VFBSMPS` nets.

### KH-1013: regulator feedback-divider match takes the first divider on the FB net, not the one topped by the output rail (LTC3558 picks a compensation resistor)

**Severity:** LOW (one corpus unit seen; the info DO-DET Vout is wrong)
**File:** `skills/kicad/scripts/signal_detectors.py:2134-2135` `_build_regulator_record`; channel choice `:2108-2114`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** the channel choice (`:2108-2114`) prefers a divider whose `top_net` is the output rail. The divider loop then takes the first divider whose `mid_net` is the FB net, whatever its top.
- On `Dzalex/NeedleDCF77`, U1 LTC3558 FB2 (`__unnamed_37`) carries two dividers: R11 270k from `+4V` over R14 68k (the real one), and R15 15k over R14. R15's top is `__unnamed_72`, whose only other part is C18, the compensation capacitor to `Vc2`.
- The record takes R15/R14: `estimated_vout` is 0.976 V and DO-DET reads "Regulator U1 estimated Vout=0.976V" on +4V. R11/R14 gives 0.8 × (1 + 270/68) = 3.98 V.

**Fix direction:** in the divider loop, prefer the divider whose `top_net` is the output rail, as the channel choice already does. Separately, reject a divider whose top net has no DC path, such as a resistor-capacitor compensation leg.

**Addendum 2026-11-11 (TH-109 triage, FND-00001776-AST-03/07):** LTC3536 on the same pattern: the analyzer takes R15 (6K49, the R15-C8 compensation branch on FB) as `r_top` and reports 0.618 V; the reviewed divider R17/R16 gives 3.315 V. The old FND lock could not fail and hid it.

### KH-1012: `led_color` reads `Infrared` as red, because colours are plain substrings tested in table order

**Severity:** LOW (no LED in the 36,463 candidate schematic outputs has "infrared" in its value or lib_id; latent)
**File:** `skills/kicad/scripts/kicad_core/parts.py:535-543` `led_color`; table `:522-525`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** every colour except `ir` is a substring test on value + full lib_id, in dict order, and `red` comes first.
- Probe: value `Infrared` gives `red`, as do `Infrared 940nm` and lib `LED:LED_Infrared`. The `ir` word rule never fires on "infrared", which has no `ir` substring.
- The LED then gets red's 2.0 V nominal and 1.5 V LA-004 floor instead of IR's 1.2 V and no floor (consumers `detector_helpers.py:365`, `domain_detectors.py:5051`).
- Same shape: value `Green` on lib `MyLib:LED_Red_0805` gives `red`, because the lib nickname is searched. `Ultraviolet` gives `None` (the 2.0 V default), not `uv`.

**Fix direction:** match colour words as words, map `infrared` → `ir` and `ultraviolet` → `uv`, prefer the value over the lib_id, and do not search the library nickname. Covers the "yellow checked before amber" note too.

### KH-1011: inrush estimation counts DNP and excluded-from-board output capacitors

**Severity:** LOW (inflates `inrush_analysis` totals and the `high_inrush` / `moderate_inrush` observations)
**File:** `skills/kicad/scripts/schematic/system_analyses.py:2817-2830` `analyze_inrush_current`; compare `:99` (the PDN builder skips `dnp` / `on_board is False`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** the output-capacitor loop has no `dnp` / `on_board` test. On `slimcdk/wisweep` `electronics/driver-board.kicad_sch`, the +3V3 rail of U1 and of U2 lists DNP parts C20 (10 µF) and C23 (100 nF). They make up 10.1 of its 31.5 µF `total_output_capacitance_uF` and raise `estimated_inrush_A` to match. In the first 4,000 schematic outputs, 13 rails have DNP caps (Hari-Singh-Tanwar Op-Amp-Training-Kit ±15V and others). The SPICE inrush benches simulate the same DNP caps.

**Fix direction:** skip `dnp` and `on_board is False` capacitors as the PDN builder does at `:99`. Output-changing: `inrush_analysis` rails, totals and observations, plus the SPICE inrush benches.

### KH-1010: a library nickname containing "invert" makes a regulator inverting; LM2675's switch pin named VOUT is taken as the output rail

**Severity:** LOW (negative `estimated_vout`, wrong output rail and topology on one corpus family)
**File:** `skills/kicad/scripts/signal_detectors.py:1806` (`lib_val_lower` includes the full lib_id), `:2041-2043` (`inverting_kw` substring); output rail from the pin named VOUT
**Discovered:** 2026-11-07, harness, while verifying the Wave 11b-1 inrush candidate at `f53d107e` (corpus)

**Symptom:** horychen/ProjectEureka `InverterLem.kicad_sch` U2 `inverter-altium-import:root_0_LM2675` `LM2675M-5.0`: PR-DET `inverting: True`, `estimated_vout: -5.0`, topology LDO, `output_rail: __unnamed_16`. That net is pin 8 (switch node, symbol name VOUT) plus only the 10 nF bootstrap cap C23 to CB, so inrush correctly finds no output cap. FB ties to +5V1, the real output. 5 records.

**Fix direction:** read only the symbol name for keyword tests. For an FB-sensed fixed part, take the FB net as the output rail when the VOUT-named pin's net holds no cap to ground.

### KH-1009: KiCad 5 `.sch` analysis runs no system-level analyses: no inrush, power budget, PDN, voltage derating, sequencing, sleep, USB / protocol compliance, test coverage, BOM optimization or assembly complexity

**Severity:** MEDIUM (whole analysis families are silently absent on every legacy schematic; 10,843 of 36,433 corpus schematic units are `.sch`; SKILL.md / methodology do not say so)
**File:** `skills/kicad/scripts/schematic/pipeline.py:930-1128` `analyze_legacy_schematic` (only `analyze_signal_paths` + `analyze_design_rules`, `:1096-1100`) vs `:1170-1281` `run_analyses` (the system-level calls, `:1227-1241`), which only the `.kicad_sch` path reaches (`:1427`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates, filed as an inrush cap-to-ground gap); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `analyze_schematic.py` on jherkenhoff/STM `Electronics/Supply-Board/Supply-Board.sch` (LM317 / LM337 ×2 each, output caps to `analog_gnd` / `piezo_gnd`) gives no `inrush_analysis`, `power_budget`, `pdn_impedance`, `power_sequencing`, `usb_compliance`, `protocol_compliance`. Findings carry no VD-001/002/004, DS-*, SS-*, ERC-label or PWR_FLAG audits. A wrapper on `analyze_inrush_current` is never called. The handoff's 7 regulators on 4 units (loxodes TPS72301 ×3, jherkenhoff LM337 ×2, blthree LM337, Fescron "DC/DC 5V out") are all `.sch`; their caps do resolve to ground.

**Fix direction:** run `run_analyses` (or the shared system-level subset) on the legacy context, behind its own corpus budget. Until then, document the reduced scope and record one `diagnostics` note.

### KH-1008: the FS-001 "too low" exemption for LM2596 / LM2576 matches by substring, so fixed-output variants (LM2596S-5.0, LM2576T-5.0) are exempt too

**Severity:** LOW (a low-impedance divider on a fixed part's FB goes unremarked; the datasheet R1 range is for the ADJ version)
**File:** `skills/kicad/scripts/validation_detectors.py:1465` `_LOW_DIVIDER_R1_RANGE`, `:1503-1507` (`match_ic_keywords(comp, (kw,))`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `match_ic_keywords` on `LM2596S-5.0`, `LM2596S-12`, `LM2596S-ADJ` all match `lm2596`; `LM2576T-5.0` matches `lm2576`. A fixed variant whose FB carries a 240 Ω–1.5 kΩ R1 (it should tie to the output directly) is exempt from FS-001. It reaches FS-001 at all because of KH-1006.

**Fix direction:** apply the range only when the part is the adjustable variant (no fixed suffix from `_lookup_regulator_vref`).

### KH-1007: the FB-at-top cross-reference attaches any divider hanging from a direct-sense regulator's output rail as its feedback (DDR VREF read as feedback, false FS-001)

**Severity:** LOW (false FS-001 info and a wrong `feedback_divider` on the regulator record)
**File:** `skills/kicad/scripts/signal_detectors.py:2267-2290` `_cross_reference_feedback_dividers` (first divider with `top_net == fb_net`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus)

**Symptom:** Gherkin/logix-core `logix-core.kicad_sch`: U2's FB4 senses `+1V5` directly. The cross-reference attaches R17/R18 (1k/1k from +1V5 to DDR_VREF, the DDR3 VREFCA/VREFDQ divider) as `fb_at_top`, and FS-001 reports "Regulator U2: feedback divider impedance too low (500R)". Pre-existing (727d0ab3 reports the same finding); this wave's multi-FB pick re-exposed it.

**Fix direction:** attach an FB-at-top divider only when its mid net reaches another pin of the same regulator (or the part is known FB-at-top). A direct-sense FB on the output rail takes no divider.

### KH-1006: a fixed-suffix regulator with a divider on FB runs the heuristic Vref sweep, which overwrites its fixed output voltage

**Severity:** MEDIUM (wrong `estimated_vout` / `rail_voltages`, read by DO-DET, derating, power budget, inrush, EMC, thermal and SPICE; 55 corpus records)
**File:** `skills/kicad/scripts/signal_detectors.py:2090-2101` (fixed estimate set), `:2121-2125` (comment says "Skip feedback divider analysis for fixed-output parts" but only sets `known_vref = None`), `:2153-2172` (heuristic estimate overwrites)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe + corpus)

**Symptom:** `_lookup_regulator_vref("LM2596S-12")` → (12.0, fixed_suffix); with the hackclub 10k/1k divider on FB the record becomes 6.6 V heuristic. Census of the candidate snaps (36,276 schematic units): 55 PR-DET records with `vref_source: heuristic` and a `feedback_divider` whose part number gives a fixed_suffix voltage, e.g. Animal-Crate LM2596T-3.3 at 1.56 / 1.61 / 2.52 V (5 units).

**Fix direction:** for a fixed_suffix part, keep the fixed estimate and skip the divider sweep (record the divider, do not estimate from it). Optionally flag a divider on a fixed part's FB pin.

### KH-1005: a chained feedback divider's pre-chain sub-pair stays in `feedback_networks`; only the presentation dedupe hides it

**Severity:** LOW (latent: output is right today because the belt drops the copy; any in-run consumer of `feedback_networks` sees the wrong top net and ratio)
**File:** `skills/kicad/scripts/signal_detectors.py:391-485` `_merge_series_dividers` (`:458` `new_vd = dict(vd)` replaces the record in `voltage_dividers` only); `schematic/pipeline.py:394-397`; mask `schematic/presentation.py:59-98` (`_vkey` = detector + components, `:94`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** for a divider extended through a series resistor (R10 3300 + R11 47 Ω, R133 51k + R144 3.9k, R2 3k + R30 210k …), `voltage_dividers` holds the chain record. `feedback_networks` keeps the original sub-pair, whose top is the junction between the chained resistors, with the sub-pair ratio. Output flattening drops the sub-pair only because the chain record still carries the sub-pair's two-ref `components` list, so the (detector, components) key collides. The product reverted a belt change after it restored 15 such duplicates (F6ITU PSU, piHPSDR, stmbl ×3, Beamer, alarmbuddy, Capibator ×2, …).

**Fix direction:** have `_merge_series_dividers` replace the matching `feedback_networks` record too (or rebuild `feedback_networks` from the merged list). Put the chain resistors in the chain record's `components`.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, verified at `db551674`):** the KH-717 local-label chain merge (3ade0bb8) keeps the first resistor's `r_top.value` string ("47k") beside the summed `ohms` 147000 and lists only R221 (bluesatunsw/owr-502 U220). Same class: the merged record's resistor fields describe one part, the numbers the chain.

### KH-1004: DS-001 / DS-002 say "No datasheets directory found" when the directory exists but holds no PDF

**Severity:** LOW (wording; `datasheets_dir: null` though a folder exists)
**File:** `skills/kicad/scripts/schematic/audits.py:300-319` (`ds_dir_found = next(...)` then `if ds_dir_found and ds_file_count > 0`), DS-001 `:372-409` summary `:383`, DS-002 `:410-440` summary `:420`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** a `datasheets/` that holds only `extracted/` JSON, a manifest or non-PDF files falls into the no-directory branch; the text says no directory was found and `datasheets_dir` is null. The product's final review counts 19 corpus units with this wording. Rider: `next(...)` takes the first existing candidate, so an empty `./datasheets` hides a populated `../datasheets` or `docs/datasheets`.

**Fix direction:** word it "datasheets directory <path> holds no PDF" with `datasheets_dir` set; pick the first candidate that holds a PDF.

### KH-1003: DC-DET lists DNP and off-board capacitors as decoupling, and the SPICE decoupling bench simulates them

**Severity:** LOW (overstated decoupling; a rail whose only cap is unfitted reads decoupled)
**File:** `skills/kicad/scripts/signal_detectors.py:1248-1300` `detect_decoupling` (no `dnp` / `on_board` test at `:1265-1281`); `skills/spice/scripts/spice_templates.py:1368-1400` (`using_pdn` set by any one cap, `:1376`, note at `:1400`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus)

**Symptom:** the schematic PDN now skips `dnp` / `on_board: false` caps (`schematic/system_analyses.py:99`, KH-758); DC-DET does not. Corpus sample (1,501 candidate snaps): 8 DC-DET records list a DNP cap, e.g. CIRCUITSTATE/Mitayi-Pico-D1 `+1V1` cap_count 3 including DNP C3. `total_capacitance_uF` and `cap_count` include it. DO-DET's decoupled-rail set is built from these records. The SPICE decoupling bench models the unfitted cap with estimated ESR/ESL and still prints "Model: ESR/ESL from pdn_impedance" when any other cap came from the PDN.

**Fix direction:** skip DNP / off-board caps in `detect_decoupling` (as `analyze_pdn_impedance` does); set the bench note per cap or "mixed".

### KH-1002: `datasheet_verify` trusts an infinite quality score, reports NaN / bool scores as `quality_score: NaN` / `true`, and the cache never re-queues a NaN score

**Severity:** LOW (needs a malformed extraction; NaN makes the verify JSON non-standard)
**File:** `skills/datasheets/scripts/datasheet_verify.py:164-194` (`_v13_score`, `_v14_score`, `_passes_trust_gate`), `:197-215` `_quality_finding`; `skills/datasheets/scripts/datasheet_extract_cache.py:468-471` (`score < MIN_SCORE` retry check)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `extraction.quality_score` inf (and v1.3 `extraction_score` inf) passes the gate, while `trust_gating.finite_score` / `facts_trusted` now reject it. NaN fails the gate, but the info finding carries `"quality_score": NaN` (`json.dumps` emits a bare `NaN`) and the detail "score nan". `True` gives `"quality_score": true`. `is_extraction_stale` on a cached extraction with `extraction_score: NaN` returns `(False, '')` (a 2.0 score returns `low_score`), so a NaN extraction is never retried.

**Fix direction:** read both scores through `trust_gating.finite_score` (None → untrusted, reported as none). Treat a non-finite score as stale in `is_extraction_stale`.

### KH-1001: `connector_layout` never sees the footprint, and reads the library nickname: opaque-symbol dual-row parts read `single`, a `_2x5` nickname reads `dual`

**Severity:** LOW (`components[].connector_layout` only; no reader in the product)
**File:** `skills/kicad/scripts/kicad_core/classify.py:557-566` `_row_layout`, `:569-593` `classify_connector(lib_id, value, pin_count)` (no footprint argument; `_row_layout(lib_id.lower())` reads the whole lib_id); caller `schematic/reader.py:1033`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `classify_connector("43650-0400", "Conn_01x04")` → `single`, though the part sits on `Molex_Micro-Fit_3.0_43045-0400_2x02_P3.00mm_Horizontal` (DRILLTEAM `Drill V2/DRILLTEAMYMchanges.kicad_sch`: LC1-3, ENC1, ENC2, Servo1, Stepper1, 7 parts). `classify_connector("Proj_2x5:Header", "HDR")` → `dual` from the nickname.

**Fix direction:** pass the footprint and let a footprint row count outrank the value. Read only the symbol name of the lib_id.

### KH-1000: the CERT-001 RF-chain suggestion lists empty component names (`components: [""]`)

**Severity:** LOW (output shape; the FCC suggestion names no part)
**File:** `skills/kicad/scripts/domain_detectors.py:5616` (`c.get("reference", c.get("ref", ""))` over `rf_chains[:3]`); RF-DET records `:1195-1219` carry `components`, not `reference` / `ref`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus)

**Symptom:** every "FCC Part 15 — RF transceiver detected (N chain(s))" finding has one `""` per chain. Candidate snaps: HNBN9/kestrel `pcb/kestrel.kicad_sch` and jarrod89/pocketPSU `elec_main_microcontroller.kicad_sch` show `components: ['']`; their CE RED twin has `[]`.

**Fix direction:** name the chain's transceiver (`transceivers[0].reference`) or take the chain's `components`; give the CE RED suggestion the same list.

### KH-999: CERT-001 and WL-001 miss a wireless module valued `WROOM32` (no `esp` in value or symbol name)

**Severity:** LOW (a true "Wireless module detected" FCC Part 15 suggestion is lost)
**File:** `skills/kicad/scripts/domain_detectors.py:5629-5631` `suggest_certifications` `radio_words`; WL-001 `_WIFI_BLE_KEYWORDS` (same file, after `:5740`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus)

**Symptom:** the fallback now reads value + symbol name only (the nickname is dropped), and neither list has a bare `wroom`. ep-infosec `makerspace-partsbin` `iot-button/esp32_button.sch` and `esp_module.sch`, M401 `WROOM32` (lib `esp32:WROOM32`): the baseline 5510006 says "FCC Part 15: Wireless module detected: M401"; the candidate has no CERT-001 there.

**Fix direction:** add `wroom` (and `wrover`) to both word lists, as words that name Espressif modules.

### KH-998: the headless-browser download fallback runs only with `datasheets.allow_private_hosts`; fetch through the pinned opener so it can run by default

**Severity:** LOW (about 2 % of downloads for users with Playwright, e.g. Broadcom `docs.broadcom.com` and Espressif, fall back to "give the user the URL")
**File:** `skills/datasheets/distributor_core/download.py:469` (`if _sync_playwright is not None and not addresses`), `:517-520` (once-per-process note), `:844-877` `_policy_route` (`route.fetch` resolves in the browser)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** with the default policy (addresses checked), `download_pdf` never adds the Playwright method, because the browser would resolve each host itself (the DNS-rebinding gap KH-647 closed by refusal). Sites that need JavaScript no longer auto-download.

**Fix direction:** fetch each routed hop in Python through the pinned urllib opener and answer it with `route.fulfill(status, headers, body)`. Launch Chromium with `--host-resolver-rules="MAP * ~NOTFOUND"` so the browser resolves nothing itself. Cookies, encoding and redirects need a real-browser test (`RealPlaywrightTest`). Target 3.1.

### KH-997: the BOM skill reads mandatory fields by exact name, while the analyzer matches them in any case with the last duplicate winning (KH-711)

**Severity:** LOW (BOM skill disagrees with the analyzer on value / footprint / datasheet / description)
**File:** `skills/bom/scripts/bom_manager.py:112-122` `extract_properties` (exact-name dict), `:147` (DNP marker from `Value`), `:372-375`, `:515`; analyzer rule `skills/kicad/scripts/schematic/reader.py:421-429` `mandatory_property`, `:751-768` `_symbol_fields`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** a symbol whose field is written `value`, `datasheet` or `DESCRIPTION` (KH-711 measured 4,158 such fields in 350 corpus `.kicad_sch` files) gets an empty value / footprint / datasheet / description in the BOM, and BOM grouping by value / footprint splits from the analyzer's. Rider: for a duplicated `Reference`, the BOM keeps the last (dict overwrite) and the analyzer the first.

**Fix direction:** read the five mandatory fields through the analyzer's rule (case-insensitive, last duplicate wins; `Reference` exact name, first entry). Share one helper.

### KH-996: the BOM skill's sub-sheet walker does not read backslash or `${VAR}` sheet file names, so those sheets' parts drop out of the BOM

**Severity:** LOW (BOM skill only; the analyzer now resolves both)
**File:** `skills/bom/scripts/kicad_sexp.py:148-174` `find_sub_sheet_entries` (`:162` `base_dir / unescape_quoted(name)`, `:163-164` skips a path that does not exist); callers `kicad_sexp.py:274`, `bom_manager.py:565`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** the analyzer resolves `expand_sheet_file(...).replace("\\", "/")` (`schematic/reader.py:1361`, `schematic/hierarchy.py:71`); the BOM walker does neither. Probe: a sheet `(property "Sheetfile" "sub\\power.kicad_sch")` with `sub/power.kicad_sch` on disk, and a `${PROJECTNAME}_power.kicad_sch` name, both return no sub-sheet; `sub/power.kicad_sch` is found. The parts on such sheets are missing from `bom_manager` output and its property write-back, with no warning. Corpus: the MST Charges_KiCAD_Project root names 5 backslash sheets.

**Fix direction:** reuse `kicad_core.project.expand_sheet_file` and the backslash replace in `find_sub_sheet_entries`.

### KH-995: ADC resolution stems `max1161` and `ad7606` cover parts of another resolution (MAX11610/11 10-bit read 12, AD7606C-18 read 16)

**Severity:** LOW (`resolution_bits` in AD-DET when no extraction is present)
**File:** `skills/kicad/scripts/domain_detectors.py:3054-3070` `_ADC_RESOLUTION_MAP` (`:3061` `max1161`, `:3065` `ad7606`), read by `_infer_adc_resolution` `:3076-3086` (first substring stem)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `MAX11610` → 12 and `MAX11611` → 12 (the MAX11606–MAX11611 family is 10-bit; MAX11612–17 are 12-bit). `AD7606C-18` → 16 (it is 18-bit; `AD7606C-16`, `AD7606B`, `AD7606-4` are 16). Correction to the handoff: `MAX11636` / `MAX11637` give None, not 12 (no stem matches). The KH-468 entry recorded `max1161` 12 as verified for its whole family; that verification is wrong for MAX11610/11 (constants registry CONST-553).

**Fix direction:** key `max1161` per part (`max11612`..`max11617`, plus `max11610`/`max11611` at 10). Give `ad7606c-18` its own longer stem at 18. Re-mark CONST-553's `max1161` verification.

### KH-994: `_read_ic_abs_max` keeps its own extraction lookup: an underscored stem with no recorded-MPN check, blind to hash-suffixed cache files and to the v1.4 abs-max block

**Severity:** LOW (needs an extraction cache; a wrong hit gives a datasheet-backed VD-002 error against another part's rating)
**File:** `skills/kicad/scripts/schematic/system_analyses.py:777-819` `analyze_voltage_derating._read_ic_abs_max`; consumer `:902-950` (VD-002)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** the reader sanitizes with `[^A-Za-z0-9_]` → `_` (`:789`) and opens `<stem>.json` directly (`:790`) without the recorded-MPN check that `find_extraction` gained this wave (`datasheet_extract_cache._records_mpn`). So `BAV99-215`, `BAV99.215` and `BAV99/215` all read one `BAV99_215.json`, whichever part it belongs to (the KH-986 collision, in a reader that fix did not cover). Its manifest step compares keys to the bare stem (`:797-801`), but `cache_extraction` writes `<stem>_<md5[:6]>` keys and files, so an extraction the datasheets skill writes is never found (`LM1117-3.3` → `LM1117_3_3_0956f6.json`). A v1.4 `<MPN>.json` with a dot or hyphen is missed by name. Any v1.4 file is read only for the v1.3 `absolute_maximum_ratings` key (v1.4 keeps ratings under `base.absolute_max`). Same class as KH-980 / KH-987.

**Fix direction:** route the reader through `find_extraction` and read the abs-max ratings from either schema version.

### KH-981: `.kicad-happy.json` `analysis.output_dir` accepts absolute and `../` paths, so `capability_mode.json` (and the cache dir derived from it) can be written outside the project

**Severity:** LOW
**File:** `skills/kicad/scripts/project_config.py:365-369`; consumers `analyze_schematic.py:90`, `analyze_pcb.py:89`, `emc/scripts/analyze_emc.py:476`, `capability_mode.py:231-240`
**Discovered:** 2026-11-06, product v3.0.2 Wave 11a handoff (new-KH candidates); verified by the harness at `5510006a` (code read + probe)

**Symptom:** validation checks only "non-empty string"; the consumers use `Path(output_dir)` as is. Probe: `resolve_config` on `{"analysis": {"output_dir": "../../escape"}}` keeps it with no warning. `capability_mode.json` is created there (first writer wins, no overwrite). The path is also cwd-relative, not project-relative (KH-793).

**Fix direction:** refuse (or warn and ignore) an absolute or escaping `output_dir`, resolved against the project dir. Related: KH-793.

### KH-985: Deep Review `find_pdf` falls back to `<MPN>_*.pdf` when the manifest marks the part `not_found`, so `LM317` gets the LM317/NOPB datasheet

**Severity:** LOW
**File:** `skills/kicad/review/scripts/deep_review_gate.py:261-315` (`_manifest_pdf`, `find_pdf`)
**Discovered:** 2026-11-06, product v3.0.2 Wave 11a handoff (new-KH candidates); verified by the harness at `5510006a` (code read + probe)

**Symptom:** `_manifest_pdf` stops only on `status: ok` + `verification: wrong`; `not_found` returns `(None, False)` and the single-hit prefix fallback runs. Probe: manifest `LM317: not_found`, `LM317/NOPB: ok → LM317_NOPB_Linear_Regulator.pdf`; `find_pdf(d, 'LM317')` returns that PDF. The fallback also runs with no manifest entry at all; `not_found` is the case where it is plainly wrong. The fallback came in with the KH-429 fix.

**Fix direction:** a manifest entry other than `ok` stops the lookup; the prefix fallback only for parts the manifest does not list, and only when the sibling is not itself a manifest key.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by fc88e9c9):** fixed: a prefix hit that the manifest lists for another part is dropped, so `LM317` no longer takes `LM317_NOPB_*.pdf` (`deep_review_gate.py:281-283`, `:318-319`). Still open: a `not_found` part still falls back to an unlisted `<MPN>_*.pdf` (`:302-320`), as does a stray sibling PDF whose manifest entry has no `file`. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-989: VM-001 reports an open-drain status output pulled up to a lower rail (a charger's STAT / CHG) as a domain crossing at the IC's supply voltage

**Severity:** MEDIUM (error-severity false positive)
**File:** `skills/kicad/scripts/validation_detectors.py:528-553`, `:576-700`
**Discovered:** 2026-11-06, product v3.0.2 Wave 11a handoff (new-KH candidates); verified by the harness at `5510006a` (code read + probe)

**Symptom:** each IC endpoint's domain is its supply estimate (`_estimate_rail_voltage_for_ic`); pin type (open collector / open drain) and the pull-up rail are never consulted. The only exemptions are USB D± and `_en_endpoint_compatible` (EN/PG names on regulator-like parts; no chargers such as BQ24/MCP738/TP4056, and no `STAT`/`CHG`/`CHRG`/`FAULT`). A 28 V charger's STAT reaching a 3.3 V MCU gives v_max 28 V > abs max → error. Reported by the PR #68 author once comma bus groups join the nets; not reproduced here (no design), plausible by code read.

**Fix direction:** exempt open-collector / open-drain output pins whose net has a pull-up to the receiving rail; size it on the corpus. Family: KH-667, KH-721. Lands with PR #68 (Wave 11b) if the join exposes it.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 3cf931c4):** fixed: open-collector and charger STAT/CHG/CHRG pins are judged at their pull-up rail (`validation_detectors.py:582`, `:593-603`, `:677-684`). Still open: `FAULT` / `nFAULT` (named in the symptom) is not in `_OD_STATUS_NAMES` (`:582`); charger PG / STDBY pins typed `output` are still judged at the IC supply. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-974: `parse_value("100N")` returns None — an uppercase `N` (nano) is not a multiplier

**Severity:** MEDIUM (a capacitor value written `100N` / `10N` reads as no value, so every detector that needs it skips the part)
**File:** `skills/kicad/scripts/kicad_core/values.py:90` `parse_value`, multiplier map `:174-178` (`p n u m k K M G R r`; no `N`, `U`, `P`)
**Discovered:** 2026-11-06, product v3.0.2 survey (candidate list); verified by the harness at `4c2a0d6` (= `7d9d4d9f` analyzer tree)

**Symptom:** `parse_value("100N")` → None; `"100n"` → 1e-7, `"100nF"` → 1e-7.

**Fix direction:** accept `N` / `U` / `P` (unambiguous: `M` stays mega, `m` milli); size the corpus values that change before the wave.

### KH-976: I2C SDA recognition misses `<prefix>_SDA` nets — `\bSDA\b` does not fire after an underscore

**Severity:** MEDIUM (I2C buses on names such as `OLED_SDA`, `SENSOR_SDA` are not detected; the prefix twin of KH-878)
**File:** `skills/kicad/scripts/signal_detectors.py:3835` (`re.search(r'\bSDA\b(?!T)', nn) or re.search(r'I2C.*SDA|SDA.*I2C', nn)`; the SCL line next to it has the same shape)
**Discovered:** 2026-11-06, product v3.0.2 survey (candidate list); verified by the harness at `4c2a0d6` (= `7d9d4d9f` analyzer tree)

**Symptom:** `I2C_SDA` and `SDA` match; `OLED_SDA`, `SENSOR_SDA` and `SDA1` (KH-878) do not: `_` is a word character, so `\b` never sits between it and `SDA`.

**Fix direction:** match `SDA` as an underscore- or boundary-delimited token (`(?:^|[_/\W])SDA\d*(?:$|[_/\W])`), together with KH-878's numbered suffix.

### KH-645: netlist oracle — m68k-hbc splits 16 `/Bus/PEP/AD*` nets into `/ATA/D*` + `/Processor/D*` (oracle 4/5)

**Severity:** MEDIUM (hierarchical bus connectivity on one of the five oracle boards; was 5/5 at the v2.2 gate)

**Symptom:** `regression/run_netlist_oracle.py --board m68k-hbc` (kicad-cli 10.0.6): analyzer 1,222 nets vs oracle 1,230; matched 1,188, **split 16**, merged 0. Every split is one oracle net `/Bus/PEP/AD<n>` (n = 0..15) that the analyzer carries as two nets `/ATA/D<n>` and `/Processor/D<n>`. The other four boards pass.

**Root cause:** not traced. The split reproduces identically at product `0490c49`, `a0df172` and `07b7fb1`, so it predates v3 round 8. Not excluded: a kicad-cli upgrade on the harness box since the 2026-07-26 v2.2 gate (5/5 PASS) changing the oracle side of the comparison; check with the kicad-cli version recorded in that gate before tracing the analyzer's bus-alias/sheet-pin propagation for the `PEP` bus.

**File:** analyzer hierarchical bus connectivity (the KH-359/#25 code path); harness `regression/run_netlist_oracle.py` (oracle runner).

**Repro:** `repos/ehbc-project/ehbc-proto1-board/projects/m68k-hbc/m68k-hbc.kicad_sch`; `KICAD_HAPPY_DIR=<product> python3 regression/run_netlist_oracle.py --board m68k-hbc`.

**Discovered:** 2026-10-25, harness audit fix wave 4 (oracle re-run after moving its children onto `build_env`; the old runner fails identically).

**Addendum 2026-11-06 (v3.0.2 survey):** a real analyzer bug, not oracle drift: kicad-cli 10.0.8 still joins `/Bus/PEP/AD0`.

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

**Addendum 2026-11-03 (3.0.x Wave 8b handoff):** SW-001 also counts a harmonic that sits exactly on a band edge in both bands (6,479 of 11,817 SW-001 findings in stored outputs, product census). KH-864 fixed the limit lookup only; this double count is not in Wave 8b.

### KH-634: `search_lcsc` overwrites a JLCPCB stock of 0 with LCSC warehouse stock after filtering and sorting, so displayed stock disagrees with `--in-stock` / `--sort stock`

**Severity:** MEDIUM (LCSC search CLI; not the sync path)
**File:** `skills/lcsc/scripts/search_lcsc.py:186-187` (`if not item.get("stock")`), `:128-130`, `:154` (`normalize_component` maps absent to 0), `:302-329` (filter/sort before enrichment), `:283-290`, `:338`, `:342`; `provider_lcsc.py:140-142`, `:160`; `lcsc/SKILL.md:239`; test `test_search_lcsc.py:296-302`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R4-F8, sk/R4-F10; R4 spot check #3)

**Symptom:** a jlcsearch row with `stock: 0` survives (no `--in-stock`), then enrichment replaces it with LCSC `stockNumber`, so the output shows LCSC stock for a row selected as JLCPCB-out-of-stock; absent and 0 are indistinguishable after normalisation. `test_cli_sort_price` passes with no sort (fixture rows already ascending). Rider: an exact-code search with both endpoints failing exits 1 instead of the documented 2 (jlcsearch exception swallowed at `:283-290`, direct returns None).

**Fix direction / budget:** keep a missing-vs-zero sentinel through normalisation and never overwrite a real 0; a separately named LCSC field if both are wanted; exit 2 on network failure. Waits on ruling: what `stock` means (recommended: jlcsearch/JLCPCB when a row exists). Budget: stock values on zero-stock exact-code / `--details` hits; distributor-oracle neutral.

**Addendum 2026-10-31 (3.0.x Wave 5, candidate `698116c`):** fixed in 3.0.x Wave 5 (`ad61947`, ruling W5-6): stock is JLCPCB stock; a real 0 from jlcsearch is no longer replaced by LCSC warehouse stock after the filter ran, and an exact-code search whose jlcsearch and direct lookups both fail exits 2. `be55cb4` (same task range, tagged KH-605) matches direct lookups to the requested code. Still open (handoff residue): exit 1 vs 2 on other outage paths; the error message names the jlcsearch exception for a wmsc 401/403; missing stock is still read as 0 before enrichment.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, claimed fixed by the handoff; partly fixed):**
- **Fixed:** product v3.0.x-dev ecbd069d fix(lcsc): unknown stock survives --in-stock, an unreachable LCSC lookup exits 2 (v3.0.2 Wave 11a Task 25, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: an exact-code search whose direct lookup fails exits 2 even when jlcsearch returned `[]`. The LCSC direct failure gets its own message instead of the jlcsearch exception (`skills/lcsc/scripts/search_lcsc.py:315-327`). For an exact code, a row with unknown stock is enriched from LCSC before `--in-stock`/`--min-stock` (`:332-338`). Missing stock is normalized to None, not 0 (`:155`).
- **Left open:** for keyword (non-exact) searches, `--in-stock`/`--min-stock` and `--sort stock` still read unknown stock as 0 before the `--details` enrichment (`:345,347,357`). A row whose stock is unknown is dropped before enrichment could fill it. This is the "missing stock is still read as 0 before enrichment" residue, now limited to non-exact queries.

### KH-632: datasheet completeness score gives full category credit to five of six categories and a free 30 points for `reserved_v15`, so a sparse MCU extraction scores 71

**Severity:** MEDIUM (visible quality metadata; gates `extraction_quality_low` and `_quality_v14.trusted`)
**File:** `skills/datasheets/scripts/datasheet_score.py:361-367` (`_CATEGORY_FIELD_REQS` has only `regulator`), `:424-426`, `:449`; legacy pin scorer `:94-127` (unnamed pin `:111-112` adds no counter; `pins_with_specs` `:107` never read); `datasheet_features.py:107-119`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F3; R3 spot check #2)

**Symptom:** the report's sparse MCU example scores exactly 71 (pinout .5, base .25, category 1.0, reserved 1.0) — over the 60 threshold, so `extraction_quality_low` is suppressed and `trusted` is set. A topology-only regulator scores ≈51 (real rubric). Legacy scorer: N unnamed pins at the expected count score 10/10 on pin coverage.

**Fix direction / budget:** per-category field requirements for the other five categories, no free credit for reserved fields, count unnamed pins. Waits on ruling: score thresholds, with frozen examples. Budget: score values and `trusted` flags on extractions (deterministic detectors are affected only through regulator/MCU features).

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

### KH-627: EMC DP-002 predicts cable radiation with a short-monopole model far outside its domain (≈20–35 dB high) and labels the table assumption `datasheet-backed`

**Severity:** MEDIUM (default EMC path on HS/SS/HDMI/Ethernet/LVDS pairs; the verdict direction often survives)
**File:** `skills/emc/scripts/emc_rules.py:2169-2213` (DP-002, `:2179`, `:2195`); `emc_formulas.py:170`, `:182`, `:800-819`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F5)

**Symptom:** USB-HS 20 ps skew → 8 mV → 87.0 dBµV/m at 1 GHz vs a 54 limit, using a 1 m cable against λ/4 = 0.075 m; the short-monopole field grows ∝ f·L while a real electrically long cable saturates. A half-wave-dipole bound (`E ≈ 60·I/r`) gives 60.6 (USB-HS), 57.3 (HDMI 1 mm), 53.2 vs 43.5 (Ethernet 5 mm), 54.2 (LVDS 2 mm) dBµV/m. The confidence label says `datasheet-backed` for a protocol-table assumption.

**Fix direction / budget:** a bounded radiation model, or report DP-002 as advisory. Waits on rulings: bounded model vs advisory; what `datasheet-backed` means (also TH-001/TH-002; KH-437 adjacent). Budget: DP-002 margin, description and confidence move (size first).

### KH-654: refs like `RF-C10` (lib `Device:C`, "5 pF") are typed `resistor`, so the current-sense detector reads a capacitor as a shunt

**Severity:** LOW (no longer reaches thermal after KH-568; still a false component type in the schematic output)
**File:** `skills/kicad/scripts/` component typing by reference prefix (the `RF-` prefix wins over the `Device:C` library symbol)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 (KH-568 investigation, handoff §Asks 4b)

**Symptom:** a capacitor whose reference starts with `R` (`RF-C10`, an RF-section cap) is typed `resistor` from its prefix, so the current-sense shunt path costed a 5 pF part; before KH-568 this produced the 2e9 W / Tj 3e11 °C thermal assessment.

**Fix direction / budget:** let the library symbol (`Device:C`) or a value with a capacitance unit override the reference prefix. Budget: component `type` on the affected refs and every detector keyed on it (size first: refs with a hyphenated prefix whose lib_id disagrees with the prefix type).

**Addendum 2026-11-07 (product v3.0.2 Wave 11b-1 handoff candidate, verified at `f53d107e`, code read + probe):**
- **What the narrow fix leaves:** the Device R/C/L override (`kicad_core/classify.py:394-402`, `_DEVICE_PASSIVE_SYMBOL` at `:65`) covers only passive symbols. An unknown `LD` prefix still falls back to its first letter, `L`, so the part is typed `inductor`. The LED rescue `_led_lib_evidence` runs only for the full-prefix `D` path (`:228`). The fallback LED test (`:316`) needs the library nickname `led` or a value of exactly `led`.
- **Probe:** `LD4` with `Device:LED` is `inductor` for value `""`, `"Green"`, `"LED_Small"`, and for `Device:LED_Small` and `Device:LED_RGB`. Only value `LED` gives `led`.
- **Corpus (first 4,200 outputs):** 32 such parts on 4 units, among them dominicbeesley bbc-keyboard LD1-LD3 (`Device:LED`, values SHIFT/CAPS/CAS), the beagleboard TechLab LD3-LD11 eagle-import LEDs, and the baldengineer Game Gear `LD1 Device:LED_Small`. The handoff's Arty LD4-LD8 (empty value) is one instance.
- **Fix direction:** in the single-letter fallback, let LED symbol evidence (the `_LED_WORD` test on the symbol name, as `_led_lib_evidence` does) outrank the first letter.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 925b67e6):** fixed: a stock `Device:` R/C/L symbol outranks an R or L reference prefix (`classify.py:65`, `:401`). Still open: non-stock symbols and value-unit evidence: `RF-C20` on a `CP-Device` rescue symbol and `RF-L10` on `L_Core_Ferrite` still read resistor. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-656: EG-001 follow-ups — keyword externality, protection through series parts, `VREG_*` / `VOUT_*` control names skipped as power

**Severity:** LOW (EG-001 is info since Wave 2)
**File:** `skills/kicad/scripts/cross_analysis.py:61` (`_is_power_net`), `:297` (connector keywords incl. `molex`, `phoenix`, `din`), EG-001 protection test
**Discovered:** 2026-10-25, product 3.0.x Wave 2 review (handoff §Asks 4d)

**Symptom:** (1) a connector is "external" when its value / footprint carries a keyword such as `molex` / `din` / `phoenix`, which also matches on-board headers; (2) protection reached through a series resistor / ferrite is not credited; (3) since `is_power_net_name` drives the power-rail skip, bare control / sense names such as `VREG_EN` and `VOUT_SENSE` are skipped as power, so EG-001 misses them. Corpus scale for context: EG-001 +12,915 info findings on 18,653 standard-profile cross units at the Wave 2 gate.

**Fix direction / budget:** classify externality from connector type / mounting rather than vendor keywords, follow one series part for protection, and exclude enable / sense suffixes from the power-name skip. Budget: EG-001 (info) presence on cross_analysis units.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 343f27fb, e832698a):** fixed: Item 3: `_is_power_net` returns False for a rail name with a signal suffix (`cross_analysis.py:72-76`); probe: `VREG_EN`, `VOUT_SENSE`, `VBUS_DET`, `+5V_SENSE`, `5VEN` are signals for both `_is_power_net` and `is_power_net_name`. Item 2: a clamp one fitted series R / ferrite / L away is credited (`:378-395`, used at `:418`). Still open: Item 1, keyword externality, is unchanged: a connector is external when its value or lib_id holds `molex`, `din`, `phoenix` and the like (`cross_analysis.py:350-354`, `:404-406`), which also matches on-board headers. Scheduled for v3.0.3 (the handoff calls it (c)). The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-657: GR-005 follow-ups — an open outer outline masked by any closed loop; stray Edge.Cuts endpoints have no info finding

**Severity:** LOW
**File:** `skills/kicad/scripts/analyze_gerbers.py` (GR-005 closure test after KH-565)
**Discovered:** 2026-10-25, product 3.0.x Wave 2 review (handoff §Asks 4e, task-2 minors)

**Symptom:** any closed loop on Edge.Cuts (a cutout, a duplicated line) satisfies the closure test, so an open outer outline next to it passes; stray endpoints that close nothing get no finding. Related task-2 minors: a G74 arc with start == end is taken as a full circle, the GR-005 summary counts draws (undercounts modal-D draws), a `%` inside a G04 comment derails the outline parse.

**Fix direction / budget:** require the closed loop with the largest extent to enclose every other Edge.Cuts loop, add an info finding for unmatched endpoints. Budget: GR-005 presence on gerber units (Wave 2 gate moved GR-005 -66 / +64).

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

**Addendum 2026-11-06 (v3.0.2 survey):** local labels only, so it does not depend on KH-671.

### KH-687: `~` as `pin_name` / pin number reads as a literal in files < 20250318

**Severity:** LOW (separately budgeted output change)
**File:** `schematic/reader.py` (`extract_lib_symbols`, pin fields)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part A (handoff 3b-A §Asks 4, ruling R14)

**Symptom:** KiCad reads a `~` pin name (and number) as empty below 20250318, as it does for fields (hb-N2); the analyzer keeps `~`. Changing it moves 5,763 entries in 38 quick outputs plus nets movement corpus-wide.

**Fix direction / budget:** apply the field rule to pin names/numbers in its own budgeted round.

**Addendum 2026-11-06 (v3.0.2 survey):** reaches 28.9 M pins in 24 k outputs.

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

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 20fb4d5e):** fixed: a bus member slot is a naming candidate: a net joined through a bus label takes the member's name at that label's priority (`connectivity.py:992`, `:1210-1224`). Still open: the same-wire alias case (MAXI030, Printer+Sticks `D16` vs KiCad `D31`), previously parked under the closed KH-403, and other residual name diffs with no cause given (tehkanwch 18, wwfsstar 54, neotron 3). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

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

**2026-11-08 (v3.0.2 Wave 11b-2, ruling D1 concern 1):** the converse case. KiCad also re-nets a segment that carries a net in the file, taking the net of the pads it joins, while the analyzer keeps the file's net. JackMatanky kb_snak `snak_28` (2 boards) exposes it now that D1 reads its mixed-token footprints (the candidate PCB snap has 172 footprints, incl. `PWR1` / `JST1` / `PAD1`). The product reports fc CK-003 +2 and 4 RT-001 extras, false by KiCad's reading, budgeted under d6-mixed-tokens. Not re-run against kicad-cli here. Same `read_board` net pass; flip the snak_28 items when it lands.

### KH-702: custom-pad residue — zone probes, VP-001 and CP-003 use the anchor box; KiCad 9+ padstack primitives are not read

**Severity:** LOW
**File:** `pcb/geometry.py` (`copper_radius`, `_point_in_pad`), `pcb/copper.py` (VP-001, CP-003 sampling), `pcb/reader.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (Task 20, survey-deferred); filed by the harness

**Symptom:** after `e44cafe` custom primitives take part in pad-track contact, but zone probes (`copper_radius`), VP-001 `_point_in_pad` and CP-003 sampling still use the custom pad's anchor box (residue e.g. BelaPlatform textile capelet, 1 split). KiCad 9+ per-layer custom primitives and anchors inside `(padstack (layer …) (primitives …))` are not read (front-layer geometry is used), and a hatched primitive fill counts as solid.

**Fix direction / budget:** one shape model for custom pads across contact, probes and sampling; budget `--full` graph + VP-001 / CP-003 on custom-pad boards (2,252 boards carry the construct).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** stays open; home is the C14 umbrella KH-751 (one custom-pad shape model with A7-F1 / A7-F3).

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

### KH-712: the PCB power-rail set is built from schematic power-symbol values and heuristic names, not board net names

**Severity:** LOW-MEDIUM
**File:** PCB power-rail set (`pcb/*` power-net resolution)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** the rail set comes from schematic power-symbol values and heuristic names. These differ from board net names since power nets can be named from the pin (Wave 3b A2-F2), and KiCad 9+ local power symbols lose rail status on the board (product rails survey §6).

**Fix direction / budget:** derive the board rail set from board net names; budget pcb power-net consumers (its own survey).

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

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, partly fixed by 3ade0bb8):**
- **Fixed (local-label form, ruling C-R5):** `_merge_series_dividers._is_passthrough` (`signal_detectors.py:419-425`) lets a power-named node pass when `_local_label_only` holds (`:407-418`: not a known or pin-recognised rail, only local `label`s, and every IC in the design has pins, `:404-405`). bluesat owr-502 U220 MP2459 r_top 47k → 147k, Vout 4.617 → 12.717 V (4 sheets); TPS54560 U220 3.42 → 12.56 V (2 sheets).
- **Still open:** (a) the predicate in the title: `is_power_net_name` is still True for `PWR_OK2`, `5V_FAULT`, `VBAT_ADC`, `5V_ISENSE`, `12V_{FBM}`, `PWR_LED` (probe at db551674; unchanged from base), so the `PWR_OK2` LR-001 / LA-AUD reading stands (survey C assigned it to KH-939, whose fix does not cover it); (b) a rail-named node with a global or hierarchical label still stops a chain; (c) the 2026-10-29 plane-identity addendum (v3.0.3): only `_GND_0` moved (now ground); `Earth`, `3x2M_NM`, `V_SUPPLY`, `/ADAU1452/IOVDD`, `VUSB`, `/power/VCCINT` unchanged.
- **Note:** the merged chain keeps `r_top.value` "47k" beside `ohms` 147000 and lists only R221 (KH-1005 class: the chain record's resistor fields).

### KH-718: family Vref table values are wrong for members of the family (TPS6102x/3x, TPS561201, LT8606, TPS562212, TPS563240)

**Severity:** MEDIUM
**File:** regulator Vref table (`signal_detectors.py` `_lookup_vref`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** TPS61025/32 (`TPS6102`/`TPS6103` 0.595), TPS561201 (`TPS561` 0.6), LT8606 (`LT860` 0.97), TPS562212 (`TPS562` 0.768), TPS563240 (`TPS5632` 0.76). SPICE no longer uses a shorter key as a criterion (R35), but these values drive analyzer `estimated_vout`.

**Fix direction / budget:** fix from datasheets; analyzer budget on `estimated_vout` / `rail_voltages`.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 28487ee0):** fixed: `TPS6103` uses TPS61030's 0.5 V reference (`parts.py:30`). Still open: `TPS6102` 0.595 (`:29`), `TPS561` (`:39`), `TPS562` (`:40`), `TPS5632` (`:41`), `LT860` (`:78`) unchanged until a data sheet is cited. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-719: readers that lose a rail's sign (fixed 79xx estimate +5 V on `-5V`, boost with a negative divider top, `-VCC_5V`, op-amp `-VBAT`, SPICE `_infer_voltage`)

**Severity:** LOW-MEDIUM (KH-675 sibling)
**File:** `signal_detectors.py` (`_lookup_vref` `LM7[89]…`, boost path, `_rail_name_voltage`), op-amp rail read, `skills/spice/scripts/spice_templates.py` (`_infer_voltage`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (KH-675 remainder)

**Symptom:** fixed 79xx regulators estimate +5 V on `-5V` (james-l-key U204 LM7905, `rail_voltages['-5V'] = 5.0`); a boost path with a `V-`/`VEE`/leading-minus divider top reads positive (no test); `_rail_name_voltage` reads `-VCC_5V` as 5; op-amp `-VBAT` → +3.7; SPICE `_infer_voltage` has no sign (negative-rail transistor benches run at +3.3 V, results info/warn, never pass) and reads `0V…` names (`0VCC`, `0V_SENSE`) as 0 V (`test_spice_zero_span.py` pins the no-sign quirk and must flip with the fix); op-amp rails on sheet paths (`/sheet/-12V`) are not parsed (lost criterion → info).

**Fix direction / budget:** keep the sign in every reader; budget `rail_voltages` / regulator estimates and the affected benches.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, candidate db551674; slug KH-new-negative-fixed-suffix):** the fixed-suffix reader keeps a sign only for `LM79xx` (`kicad_core/parts.py:238-240`). `[-_](\d+\.\d+)` (`:252-255`) reads other negative fixed parts as positive: `LM2990SX-5.0` → +5.0, `ADP7182AUJZ-5.0` → +5.0. `L7905CV` / `MC7912` → no value. skumlos bkm-129x IC050 LM2990SX-5.0 (input `-6V`) shows `estimated_vout` +5.0 beside `output_rail` `VSSA` now that KH-964 restored the output rail. `rail_voltages` is protected by the VSS guard (`schematic/pipeline.py:342`), but the regulator record is not. The `LM7905` example in the symptom is already −5.0 (fixed before 6138b126). Fix: a negative-regulator family or an input-rail sign (negative Vin, not `inverting`) negates the suffix.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; handoff note "LM317 F+15V info vs LM337 F-15V fail"):** SPICE `_rail_name_voltage` (`skills/spice/scripts/spice_templates.py:894-912`) reads `F-15V` as +15 (a `-` after a letter is not a sign) and cannot read `F+15V` (a `+` inside the token). On jaromir-sukuba/nvm MARGE `nvm_pmain_fpsu`, U16/U17 LM337 are compared against |15| / |8| V and fail (6.7 %, true: the dividers set 16.08 / 7.5 V). U14/U15 LM317, with the same dividers on `F+15V` / `F+8V`, fall to info ("the rail's name carries no voltage"), so two true fails are missed. Fix with the KH-719 sign work: take a `+`/`-` before the number inside a token as the sign. Kicad-side half: KH-new-net-voltage-mid-minus. Gate budget: SPICE regulator_feedback info → fail on the nvm LM317 twins (2 per MARGE sheet).

### KH-720: CAN split termination (60 + 60 Ω) and off-board termination are reported "missing termination"

**Severity:** MEDIUM (false issue)
**File:** `schematic/net_analysis.py` (`bus_analysis.can`), PR-003
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** split termination (60 + 60 Ω) and off-board termination read as missing termination. PR-003 counts a DNP terminator (R15).

**Fix direction / budget:** recognise split termination; budget `can[].termination` / `protocol_compliance[can]`.

### KH-724: reference and bias nodes named like rails get RS-001 "no declared source" and DO-DET "missing decoupling"

**Severity:** LOW
**File:** RS-001 / DO-DET (power-net consumers)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (class A4a, R6); filed by the harness

**Symptom:** `1.25V_REF`, `1.8V_REF`, `2.5V`, `REV2V5` read as rails (product legacy sample: RS-001 3 + DO-DET 5 per 80).

**Question / fix direction:** should DO-DET/RS-001 treat a reference node as a rail? Budget: RS-001 / DO-DET on reference nodes.

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, partly fixed by 1a5ea052):**
- **Fixed:** a net with a REF token (a token ending in `REF` or starting with `VREF`: `1.25V_REF`, `2V5_REF`, `DDRVREF`; not `REFCLK` / `220V_REFRIG`) is left out of RS-001 unless an IC takes its supply from it, and out of DO-DET's IC power nets unless a regulator, IC or diode output drives it or an IC supply pin sits on it (rulings C-R1..C-R3; `signal_detectors.py:3856-3879`, `:3906`, `:4716`). Gate: RS-001 / RS-002 / RS-003 and DO-DET removals on REF-named nets, std lane.
- **Still open:** rail names without a REF token (`2.5V`, `REV2V5`). The product closes them by argument ("no name rule can tell them from a 2.5 V rail"), but the false RS-001 is a pin question: `_has_direct_source` (`signal_detectors.py:4648-4661`) counts only `power_out` pins, `PWR_FLAG` and regulator outputs, and the output-pin rule in `_reference_net` is applied only to REF-named nets. Fix direction: count an IC or reference-diode `output` pin as a source in RS-001 whatever the name; size it first, since logic outputs sit on rail-named nets too.

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

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 28487ee0):** fixed: an LTC3558 row at 0.8 V (`parts.py:81`). Still open: no LM2731x row; LMR33640 is still covered by `LMR336` 1.0 V (`:57`). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-733: diff-pair ESD credit residue — all-input clock buffer and a connector typed `ic` still credited; bare "protection" matched in descriptions

**Severity:** LOW
**File:** `classify_ic_function`, diff-pair ESD credit (`schematic/net_analysis.py`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R13); filed by the harness

**Symptom:** an all-input clock buffer (Si53322) and a connector typed `ic` (SM05B) are still credited; `classify_ic_function` matches a bare "protection" in descriptions (regulators with overcurrent protection, transceivers with ESD protection).

**Fix direction / budget:** budget `differential_pairs[].has_esd`.

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

**Addendum 2026-11-06 (v3.0.2 survey, verified at `4c2a0d6`):** the misread is a crash: the LTspice `.meas` regex `^(\w+):\s+.*?=\s*([-+]?[\d.eE]+)` (`spice_simulator.py:340`) and the Xyce one (`:442`) stop at the exponent sign, so `1.58e+04` / `1.58e-04` capture `1.58e` and `float()` raises `ValueError`, uncaught at `simulate_subcircuits.py:263`. Fix with an exponent-aware number pattern (`[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?`).

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 40a2d271 fix(spice): LTspice and Xyce measurement output with a signed exponent parses instead of crashing (v3.0.2 Wave 11a Task 14, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: a shared `_NUM` pattern (`skills/spice/scripts/spice_simulator.py:31`) is used by the LTspice (`:343`, `:348`) and Xyce (`:444`) parsers. Probe: `1.58e+04`, `-3.2E-05`, `1.5917e+04` and the Xyce `1.58e-04` all parse.
- **Left open:** the Xyce/LTspice phase unit; LTspice lines with two `=` (`.*?=` still takes the first `=`); `let` still skipped on LTspice/Xyce (`:305`, `:417`). All expected PARTIAL.

---
Tally: 33 checked — 27 FIXED, 6 PARTIAL (482, 554, 559, 743 as the maintainer expected; 634, 647 claimed FIXED but PARTIAL), 0 NOT-FIXED, 0 UNCLEAR.

### KH-744: op-amp library `supply_min` values look high (OPA1612, TL07x, NE5532)

**Severity:** LOW
**File:** op-amp model library (`supply_min`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** OPA1612 9 V vs 4.5 V datasheet; TL07x vs TL07xH; NE5532. They decide S2's below-minimum warns/infos.

**Fix direction / budget:** verify against datasheets before editing; budget op-amp bench status.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 21f27d74):** fixed: TL072 / TL074 `supply_min` 7 -> 4.5 V (`spice_part_library.py:35-38`); confirmed harness-side against SLOS080W §5.3 (local datasheets/TL072-019ed851.pdf): VS min 4.5 V for all devices except NS/PS packages and TL07xM (10 V). Still open: OPA1612 `supply_min` 9 V (`spice_part_library.py:55`) against the 4.5 V the KH cites, and NE5532 8 V (`:41`) are unchanged; not scheduled in the handoff. TL082/TL084 also still carry 7 V (`:39-40`), outside the KH's list. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

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

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 21f27d74):** fixed: (b) the op-amp ground-leg move drops the input resistor's line by exact element token, not prefix (`spice_templates.py:470-471`); product test `GroundLegElementTest` (R1 vs R10). Still open: (a) is not touched by this wave: an LM317-family (three-terminal ADJ) regulator with a trimmer in its divider still breaks out before a `feedback_divider` is set (`signal_detectors.py:2141-2145`), so `generate_regulator_feedback` returns None (`spice_templates.py:1469-1471`) and `simulate_subcircuits.py:238-239` / `:304-305` write no record at all. Non-three-terminal regulators with a trimmer already get the info 'divider arm X is adjustable' (`spice_results.py:845`, since 4438e8bd). No schedule in the handoff. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-747: Vref key core cut — fixed-output parts cut to a covering core; wildcard values make a key cover

**Severity:** LOW
**File:** regulator Vref key matching
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** `LD33`/`NCP1117ST33` fixed-output parts cut to a covering core; wildcard values (`TPS6103x`, `LM259x`) make a key cover (a simple rule breaks `TPS560430X`).

**Fix direction:** per-pattern rule with tests for the cases above.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 28487ee0):** fixed: a Vref key no longer covers a part when a fixed-voltage code follows the key (`parts.py:292-305` `_FIXED_PART_KEYS`). Still open: wildcard values (`TPS6103X`, `LM259X`) still match (`:301-305`). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-748: crystal residue — frequency misparse, no sanity range, CL omits stray capacitance, duplicated leg grouping

**Severity:** LOW
**File:** `detect_crystal_circuits`, SPICE crystal bench
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** frequency misparse (`32768_1206_12.5pF` → 0.0328 Hz, `32.768` → Hz, jotego Y2 400 Hz); no sanity range; the expected CL omits the 3 pF stray; leg grouping is duplicated between the kicad and spice skills.

**Fix direction / budget:** add a sanity range (outside 1 kHz-200 MHz → warn "frequency not a crystal value"); include the stray; share the leg grouping.

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

### KH-756: IO-001 and the test plan compare schematic and PCB net names without the net-identity map

**Severity:** LOW
**File:** `emc/scripts/emc_rules.py` (IO-001, test plan)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** schematic and PCB net names are compared literally, without the net-identity map; the effect is missed clears only.

**Fix direction / budget:** compare through the net-identity map; budget IO-001 clears.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 4eef6daf):** fixed: IO-001's schematic-protection test now adds the connector's schematic `pin_nets` to its board net names (`emc_rules.py:993-997`), so a protection device named by the schematic net clears it. Still open: The test plan's protocol lookup still compares the board's connector net names literally against the schematic `differential_pairs` names (`emc_rules.py:4424-4439`, `_connector_net_names(conn)`); KH-756 addendum, stays open (handoff ruling M1 concern 2). The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-757: a TVS on an unclassified VBUS rail clears IO-001

**Severity:** LOW (reach 0)
**File:** `emc/scripts/emc_rules.py` (IO-001)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** a TVS on a VBUS rail that is not classified clears IO-001. Reach 0 in the sample.

**Fix direction / budget:** see Symptom; no corpus budget expected.

### KH-759: PDN residue — plane area is the smaller of the two fills, and both sweep grids under-read narrow anti-resonance peaks

**Severity:** LOW (missed direction)
**File:** `emc/scripts/emc_rules.py` (PD-001 PDN sweep), `schematic/system_analyses.py` (`analyze_pdn_impedance`)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (class P14a); filed by the harness

**Symptom:** the plane area is the smaller of the two fills (an overlap bound; shapes are not intersected): m222 1V8 has bounding-box overlap 0 and still gets 0.5 pF. Both sweep grids under-read narrow anti-resonance peaks: a 2.431 Ω peak reads 1.96 Ω on the EMC grid and 0.52 Ω on the schematic grid, below its 1 Ω observation threshold.

**Fix direction / budget:** intersect the fill shapes; refine each grid maximum. Budget PD-001 / `pdn_impedance` additions.

### KH-761: EF input filter counts caps upstream of a rail tap

**Severity:** LOW
**File:** `emc/scripts/emc_rules.py` (EF-001 / EF-002)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff (Task 115 M2); filed by the harness

**Symptom:** capacitors upstream of a rail tap count toward the input filter (rail-tap direction).

**Fix direction / budget:** count only caps on the converter side of the tap; budget EF-001 / EF-002.

### KH-763: a legacy board with a `.kicad_pro` reports project rules it does not use

**Severity:** LOW
**File:** `pcb/dfm.py` (design-rule compliance), `project_settings` output
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** the minima ignore the project (correct), but `rules_source`, `net_class_*` and `project_settings.design_rules` still come from it.

**Fix direction / budget:** report the rules actually used; budget those fields on legacy boards with a project file.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by d3383359):** fixed: On a KiCad 5 board with a `.kicad_pro` (`pcb/pipeline.py:400-403`, `:417-418`), `project_settings` omits the project's `net_classes` and `design_rules`, `design_rule_compliance` omits `rules_source` (`pcb/dfm.py:1185`), and `net_class_summary` goes with the classes. Still open: Top-level `net_classes` still takes the project's classes on a KiCad 5 board (`pcb/pipeline.py:394-395`, set before the legacy test). Scheduled for 3.1 with KH-new-netclass-keys (ruling D P4). The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

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

### KH-768: inferred-stackup edge cases

**Severity:** LOW
**File:** `pcb/pipeline.py` (stackup inference)
**Discovered:** 2026-10-29, product 3.0.x Wave 4 Part B handoff; filed by the harness

**Symptom:** a board with no `(setup)` infers 1.6 mm, though KiCad builds the default from the general thickness (`board.cpp:3279-3287`; fixtures only); a B.Cu-only board gets no dielectric (its impedance may vanish), an F.Cu-only board a dangling one; loss tangent is not read. The sublayer εr docstring must not claim KiCad: the thickness-weighted εr is ruling 20's choice (KiCad writes sublayers separately and uses sublayer 0).

**Fix direction / budget:** per item; fix the docstring.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 7c3dc7ff):** fixed: `pcb/pipeline.py:129-134`: a single copper layer gets one dielectric on its inner side (B.Cu-only board now has one). The no-(setup) thickness item was already fixed by KH-851 (`pcb/reader.py:128-133` reads `(general (thickness))`). The docstring half needs no change: `_merged_sublayers` (`pcb/reader.py:104-107`) does not claim KiCad. Still open: The loss-tangent item is not addressed and no survey or handoff names it. KiCad's default stack sets loss tangent 0.02 on each dielectric (board_stackup.cpp:72); the inferred stack (`pcb/pipeline.py:129-143`) carries none, and a sublayered dielectric keeps the last sublayer's loss tangent (`pcb/reader.py:154-163`). No analyzer reads `loss_tangent`, so there is no output symptom; close by ruling or keep open. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

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

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by ee7446b1):** fixed: net classification reads the net's leaf name (`net_analysis.py:414`), so sheet-path and UUID tokens no longer classify a net. Still open: classes lost to whole-token matching remain (`DOUTXBee`, `~{UCSE*}` / `~{LCSE*}` read signal, `_keyword_hit` `:233-249`); legacy `/` labels are newly exposed (filed separately). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

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

### KH-793: `capability_mode.py` writes `analysis/capability_mode.json` relative to the cwd and lists a cwd-relative `datasheets/extracted`

**Severity:** LOW
**File:** `skills/kicad/scripts/capability_mode.py` (output path; `:80` `datasheets/extracted` listing)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 3 (a stray `analysis/capability_mode.json` appeared in the product worktree root during the wave); not verified harness-side

**Symptom:** the sidecar lands in the cwd's `analysis/`, not the project's or the run's, and datasheet coverage counts the cwd's extractions.

**Fix direction / budget:** write beside the analyzer output (or into `--analysis-dir`) and list the project's own cache. Harness: runners already treat `capability_mode.json` as a sidecar (TH-050 / TH-089); check the corpus output trees for strays when it lands.

**Addendum 2026-11-06 (v3.0.2 survey):** visible in the corpus: every `capability_mode.json` sidecar under `results/outputs/` reads `datasheet_extraction: partial` (3,000 / 3,000 sampled), because the batch runners and the gate inherit the harness cwd, which holds `datasheets/extracted`. Gate scope (checked): the sidecar sits in each unit's private dir beside `snap.json`; the strict and budgeted comparators read `snap.json` only (`field_compare.iter_units` / `_compare_unit`), and the envelope carries only `capability_mode_ref` (source + run_id, volatile-masked); only the informational raw mode sees the sidecar. Both gate sides see the same cwd, so the verdict is unaffected; a fix that changes what the analyzer does under `partial` is output-changing for the corpus.

### KH-794: `inputs.source_files` records paths as given, and consumers resolve relative paths against their own cwd

**Severity:** LOW
**File:** analyzer envelopes (`inputs.source_files`); consumers EMC `_schematic_project_dir`, `schematic/audits.py:282` (`project_dir or "."`), the datasheet verifier's API fallback
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 4; not verified harness-side

**Symptom:** a JSON produced from one cwd and read from another resolves a relative source path against the reader's cwd, so project-relative lookups (extractions, project files) silently miss or hit another project.

**Fix direction / budget:** record absolute paths (an envelope change: every unit's `inputs.source_files` moves; corpus budget on all analyzer types), or record the project root once and resolve against it.

### KH-795: a trace crossing a split between two power planes is not reported — the return-path check never compares the reference net (GitHub #60.2 / #60.3)

**Severity:** MEDIUM (a missed reference-plane change under a high-speed trace is a false negative on a core EMC check; the fix is output-changing)
**File:** at `7131f26`: `skills/kicad/scripts/pcb/routing.py:425-429` (one `ref_idxs` set for every ground / power zone), `:441` (`SAMPLE_INTERVAL`, 2.113 mm on the reporter's board), `:497` and `pcb/geometry.py:631-651` (`has_coverage_near`, radius 0.5 mm); `cross_analysis.py:943-1000` (PS-002 sees one net's islands only)
**Discovered:** 2026-10-30, GitHub #60 items 2-3 (PGIRang, filed against v2.3.2; verified at v2.3.2 and `7131f26`, product `.superpowers/sdd/2026-10-29-v3.0.x-wave5/github/gh-60-62-findings.md`); filed from the product 3.0.x Wave 5 handoff follow-up 5

**Symptom:** a trace over a 1 mm split between `+3V3` and `+5V` planes is not a discontinuity. The 0.5 mm coverage radius finds copper at every sample across the 1 mm void (`--return-path-radius-mm 0.1` still misses), and the check asks only "is any ground/power copper present", never which net. kicad-cli DRC reports 0 violations (KiCad has no plane-split rule). Side note: a trace end over J4's own THT pad clearance on In2 — the antipad credit covers vias, not THT pads.

**Fix direction / budget:** record the reference net per sample and report per-net reference changes (GP-001 on clock / high-speed nets), or intersect the trace exactly with the fill polygons. Output-changing (full-chain `return_path_continuity` and GP-001): survey and budget first.

**Addendum 2026-11-03 (3.0.x Wave 8b, product `87bf8b1` `1d83bf7` `6f143cb` `2483758` `a9190b7` `0efc012`, unreleased):** the reference-net-change half is fixed. `--full` PCB output carries `reference_plane_changes` (`{net, layer, reference_layer, net_a, net_b, x, y, sample_points}`, `net_a`/`net_b` unordered) beside `return_path_continuity`; a plane net counts only where it holds over about 2 mm of trace across segment ends; EMC GP-001 (severity error) reports a high-speed / clock net (leaf name) whose reference plane changes between two plane nets unless a capacitor joining them sits within 5 mm of the bounding samples. Harness gate (full-chain, 260 repos): key on 1,985 pcb units / 223 repos, non-empty on 94; 23 split findings on 15 EMC units / 8 repos (handoff E ~70 boards / ~140); `return_path_continuity`, RP-002 and the existing GP-001 unchanged. New `tests/test_kh795_split_plane.py` (split + bridged fixtures). Still open: the void half (exact trace-against-fill test instead of the sample radius), post-3.0. Residues filed as KH-885..891.

### KH-799: a multi-condition SpecValue is read from its first entry

**Severity:** LOW
**File:** datasheet SpecValue readers (`skills/datasheets/datasheet_types/`; the handoff names no line)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 10 (ruling W5-9, deferred); not verified harness-side

**Symptom:** when a spec lists values per condition (temperature, supply, load), consumers take the first condition's value whether or not it matches the design.

**Fix direction / budget:** choose the entry by condition, or take the worst case; waits on the W5-9 ruling. Corpus-neutral (no corpus extraction caches).

### KH-801: back-mounted THT parts are read as front from the Gerber X2 attributes

**Severity:** LOW
**File:** `skills/kicad/scripts/analyze_gerbers.py` (component side from `%TO.C` / `%TO.P`, `c3be297` single-sided rule)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 12 (KH-785 remainder); not verified harness-side

**Symptom:** KiCad writes `%TO.C` for THT pads on both masks, so F.Mask names back-mounted THT parts and the front wins: `back_side` is low on 11 of 39 kicad-cli boards (the same at the base).

**Fix direction / budget:** side from the silkscreen / courtyard / component-layer attributes, or from copper only for SMD; budget `component_analysis.front_side` / `back_side` on gerber units.

### KH-802: GR-002 outline choice — a larger stale outline can swallow real outside copper, and board dimensions take the first Edge.Cuts file

**Severity:** LOW
**File:** `skills/kicad/scripts/analyze_gerbers.py` (GR-002 outline union from `0c6a506`; `compute_board_dimensions`; extents walker)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 13 (KH-484 remainder); not verified harness-side

**Symptom:** all Edge.Cuts files are merged (this fixed a stale-outline false fire), but a larger stale outline can hide real copper outside the board. `compute_board_dimensions` still takes the first Edge.Cuts file; G70 legacy files without `%MO` stay in inches; the extents walker lacks `%FST` / incremental-coordinate support.

**Fix direction / budget:** prefer the job-listed Profile, then an Edge.Cuts file whose X2 `CreationDate` matches the set, then the union; read G70 as inches → mm; `%FST` and incremental modes in the walker. Budget GR-002 and `board_dimensions` on gerber units.

### KH-804: Type-C CC resistor reader gaps — unreadable value forms, `GND_LV`, two resistors on one CC net, PD-controller list, summary status, a duplicated Rp table

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/system_analyses.py` (CC checks); `domain_detectors.py:2783-2800` (second Rp table); `parse_value`
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 15 (KH-789 remainder); not verified harness-side

**Symptom:**
- `parse_value` cannot read `5.1kR`, `5k1R 1%`, `R5k1`, `R-5k1-0402`, `R_5k1_0402` (now reported as info; the description or MPN could supply it).
- `GND_LV` is not read as ground.
- Two resistors on one CC net: last wins (KrishveerCard J6).
- The PD-controller list lacks CYPD3175 / CCG3PA and FUSB303B.
- `usb_c_cc_status.status` is "pass" while checks fail.
- The Rp table exists twice (`domain_detectors.py:2783-2800` and `system_analyses.py`).

**Fix direction / budget:** widen the value reader, ground names and controller list; judge every resistor on a CC net; derive the status from the checks; one Rp table. Budget `usb_compliance` / UC-* on Type-C units.

### KH-805: `--analysis-dir` carries `lifecycle.json` forward after a BOM change, and `gerber.json` is never judged stale

**Severity:** LOW
**File:** `skills/kicad/scripts/analysis_cache.py` (copy-forward; derived-output staleness from `4c8e838` / `53a917c`)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 16 (KH-596 remainder); not verified harness-side

**Symptom:** after a part swap the run keeps the old `lifecycle.json` (the wrong part's lifecycle); `gerber.json` records no source hashes, so it is never dropped.

**Fix direction / budget:** treat lifecycle as derived from `schematic.json`; record Gerber source hashes. Neutral for the harness (no gate profile uses `--analysis-dir`).

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 99b688c7 fix: a new schematic drops the run's lifecycle.json instead of carrying it forward (v3.0.2 Wave 11a Task 19, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `skills/kicad/scripts/analysis_cache.py:68-69` adds `lifecycle.json` to `_DERIVED_OUTPUTS`, with `_DERIVED_UPSTREAMS = {'lifecycle.json': ('schematic.json',)}`. `_derived_stale` drops it on both the new-run path (`:694-698`) and the overwrite path (`:795-799`) when schematic.json changes.
- **Left open:** the gerber half. `gerber.json` still records no source hashes and is never judged stale; this moved to v3.0.3 by ruling 11.

### KH-808: the ruling W5-3 family match accepts a digit continuation (`LM358` → `LM3580`), and strict identity drops correct base-part datasheets

**Severity:** LOW
**File:** `skills/datasheets/distributor_core/` identity / family match (`c64acde`, `4b5f2d6`; KH-605)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 19; not verified harness-side

**Symptom:** a family match for a Value-named part accepts a hit whose next character is a digit, so `LM358` can take `LM3580`'s datasheet. The W5-3 user cost: strict mode drops correct base-part datasheets when the MPN property names a base part (TPS61023 → TPS61023DRLR is now `not_found`).

**Fix direction / budget:** require a non-digit boundary after the family stem; accept an ordering-code extension of a base part named in the MPN property. Distributor-offline re-freeze if the fixture BOM carries such parts (the `sync-identity` runs).

### KH-814: the Action's `has-critical` / `findings-count` count only EMC and thermal errors — schematic and PCB `error` findings never gate, and the VD-* derating rows are read from a retired key

**Severity:** MEDIUM (Action gating, like KH-507; the shipped example `action/examples/simple.yml:79-84` gates "Fail on critical" on `has-critical`)
**File:** `action/format-report.py:559-583` (reads `sch["voltage_derating"]["issues"]`), `:641-664` (EMC and thermal summary rows, the only `critical` sources), `:671-672` (counts), `:960-964` (`findings_count`, `has_critical`)
**Discovered:** 2026-11-01, product 3.0.x Wave 6 docs surveys (ruling W6-2); filed by the harness at the Wave 6 gate

**Symptom:** the counts come from the report's own rows, not from the analyzers' `findings[]`. Schematic and PCB findings are never added as rows, so a schematic with two `error` findings gives `has_critical false`, `findings_count 0` (workflows survey, measured). The derating block reads `sch.get("voltage_derating", {})`, a top-level key the schematic output no longer has: `schematic/presentation.py:231-232` puts the VD-* findings into `findings[]`, so the loop at `:562-583` never runs and derating never sets `has-critical`. Schematic rows that do count: `protocol_compliance` issues (warning) and up to 3 `connectivity_issues.single_pin_nets` (warning). The docs now state this behaviour (`install-guidance.md:633`, `action.yml:61`; product `1cae2e9`). Verified harness-side at `c0a8a62`: code read; `voltage_derating` appears in no schematic result key (only `presentation.py:77,231-232`). Line correction: the handoff's `:558` is `sig = _group_findings(sch)`; the derating read is `:559`.

**Fix direction / budget:** decide with KH-507 (SPICE gating, ruling 3, after KH-442): count schematic / PCB `error` findings (possibly behind an input; SS-001 "Sourcing blocker" is an `error` on any board under 50 % MPN coverage, so a plain count would fail many CIs), and read derating from `findings[]` (`detector == "analyze_voltage_derating"`) or drop the dead block. Budget: Action outputs and PR comment text (text oracle `action-format-report` fixtures); no corpus profile runs the Action.

**Addendum 2026-11-02 (3.0.x Wave 8a, product `edfddbd` `8199c29` `5add137`, unreleased):** the derating half is fixed. The Action reads VD-* findings from `findings[]` (`detector == "analyze_voltage_derating"`, `action/format-report.py:144`, `:1203`): `error` → critical row, `warning` → warning row, `info` → none, in both the PR comment and the step summary; the full report lists them (`5add137`). Still open: other schematic / PCB `error` findings do not gate. 65 % of corpus schematics and 64 % of PCBs carry one (product survey), so that half needs an opt-in input, post-3.0. Harness gate: see status.md (Wave 8a).

### KH-816: TW-001's trace-width table `_IPC2152_1OZ_10C` has no cited source and matches neither printed standard

**Severity:** LOW (one advisory rule; the table is wider than IPC-2221 up to ~12 A and narrower above it)
**File:** `skills/kicad/scripts/cross_analysis.py:112-115` (`_IPC2152_1OZ_10C`), `:124ff` (`_min_trace_width_for_current`, interpolation), `:881ff` (TW-001)
**Discovered:** 2026-11-01, product 3.0.x Wave 6 docs surveys (ruling W6-5); filed by the harness at the Wave 6 gate

**Symptom:** the table (0.5 A → 0.25 mm … 5 A → 3.5 mm, 10 A → 9.0 mm) is labelled IPC-2152 1 oz / 10 °C but reproduces neither IPC-2152 nor the IPC-2221 formula, and stops at 10 A / 9.0 mm, so above about 12 A its recommended width is narrower than IPC-2221's. `references/pcb-layout-analysis.md:164` now names the mismatch (product `b977a2e`, `93f43ea`; KH-637). Verified harness-side at `c0a8a62`: table at `:112-115` (the code twin of the doc line), no source comment.

**Fix direction / budget:** cite a source and recompute the table from it (or use the IPC-2221 formula the references already state), and extend it past 10 A. Budget: TW-001 recommended widths and fire set on boards with routed power nets (`--full` / cross-analysis lanes). The harness constants registry should carry the table as unverified until then.

### KH-823: the Action's diff mode re-runs only the schematic and PCB analyzers on the base, so EMC and SPICE changes are never compared

**Severity:** LOW (feature gap; the docs stopped promising the lanes in Wave 6)
**File:** `action/entrypoint.sh:308-321` (base re-runs: `analyze_schematic.py`, `analyze_pcb.py` only), `:324` (`for dtype in schematic pcb`)
**Discovered:** 2026-11-01, product 3.0.x Wave 6 docs surveys (schema survey P4, ruling W6-20; architecture audit A5-F4, the code side of KH-642 R1-F5); filed by the harness at the Wave 6 gate

**Symptom:** no `base/emc.json` or `base/spice.json` is produced, so `diff_analysis` never sees an EMC or SPICE pair. The other R1-F5 half (only the first diff reached the report) is already fixed: the loop collects every diff into `DIFF_JSONS` (`:329-331`). Verified harness-side at `c0a8a62` by reading `:285-340`. KH-642 said the code side was "filed separately"; no open entry carried it, so it is filed here. `github-action.md:43` now says EMC and SPICE are not re-run on the base (product `d762249`).

**Fix direction / budget:** run EMC (and optionally SPICE) on the base tree and add their diff lanes. Feature work, post-3.0: Action runtime and the Action contract tests; no corpus profile. Related: KH-493 (base extraction scope), KH-507.

### KH-824: the Mouser provider's `DEFAULT_DELAY = 1.0` allows ~60 calls a minute, above the documented free-tier quota

**Severity:** LOW (free-tier 429s on large BOMs; retried since KH-615)
**File:** `skills/mouser/scripts/provider_mouser.py:22` (`DEFAULT_DELAY = 1.0`); consumer `skills/datasheets/distributor_core/sync.py:197`
**Discovered:** 2026-11-01, product 3.0.x Wave 6 docs surveys (schema survey P6, ruling W6-22); filed by the harness at the Wave 6 gate

**Symptom:** one serial worker makes up to about 60 calls a minute and `--parallel N` multiplies that; the previously documented quota was 30 calls a minute. The docs no longer claim the default stays under a quota and tell the user to set `--delay` / `--parallel` (`skills/mouser/SKILL.md:216-219`, product `d762249`). Verified harness-side at `c0a8a62` (code line; KH-642 cited `:21`, now `:22`). The quota itself was not re-checked (no network).

**Fix direction / budget:** confirm Mouser's current quota, then set the default from it (2.0 s for 30/min). Changes `--help` "default: 1.0" (text oracle `help__sync_datasheets_mouser`) and sync timing; distributor-offline transcripts unaffected.

### KH-855: detector-family move deferred — signal / domain / validation detectors stay in their current modules

**Severity:** LOW (architecture, deferred by ruling; no behaviour change)
**File:** product `oracle-scripts/relocate/relocation-map-full-draft.json` (Wave 7 records) — the full relocation map
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-detector-family-move); `2cc1a36` (KH-845) did the `_get_net_components` inline only

**Symptom:** the detectors are not grouped by family; the move was ruled out of 3.0.x.

**Fix direction / budget:** apply the draft map in a structural wave; harness churn about 18 files / 112 binding sites (api_migration apply-map + scan-coverage / constants re-key). Empty corpus budget.

### KH-856: `what_if` engine extraction deferred until KH-826 / 827 / 828 and the sweep / corner vectors land

**Severity:** LOW (architecture, deferred by ruling)
**File:** `skills/kicad/scripts/what_if.py`
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-what-if-engine-extraction)

**Symptom:** the what-if CLI and its engine share one module; extracting the engine first would move code that KH-826 / 827 / 828 still have to change.

**Fix direction / budget:** fix KH-826..828, add sweep and corner test vectors, then split the engine from the CLI (structural, empty budget).

### KH-857: distributor vendor-client extraction deferred until recorded SPICE request/response fixtures exist

**Severity:** LOW (architecture, deferred by ruling)
**File:** request construction in the provider adapters (`skills/*/scripts/provider_*.py`) and the SPICE spec fetcher (audit ar A4-F2)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-vendor-clients)

**Symptom:** the vendor clients were ruled out of 3.0.x: the SPICE side has no recorded request/response fixtures, so a shared client could not be shown output-neutral there.

**Fix direction / budget:** record SPICE request/response fixtures, then extract the clients; distributor-offline oracle plus the new SPICE replay.

### KH-858: the two PCB point-to-segment distance helpers are not merged — they are not bit-identical

**Severity:** LOW (architecture, deferred by ruling)
**File:** `skills/kicad/scripts/pcb/geometry.py:81` vs `:576` (audit ar/R2-F4)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-pcb-point-to-segment-dedup)

**Symptom:** the merge is fixture-neutral (`check_refactor quick` OK) but not floating-point identical: 80,477 of 200,000 random inputs differ, by up to 2.95e-10 relative (product measurement). Ruled not worth a corpus round for about −10 LOC.

**Fix direction / budget:** merge in a wave that runs a corpus gate over the families the helpers feed (board-edge / BV-001 / clearance), empty budget or a float-noise class measured with a both-direction walk.

### KH-859: SPICE subcircuit kinds have no single registry

**Severity:** LOW (architecture, deferred by ruling)
**File:** `skills/spice/scripts/` (audit ar/R4-F4)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-spice-kind-registry)

**Symptom:** still as the audit reported; two product tests now consume the existing registries, so the change is larger than a Wave 7 fold (ruled defer).

**Fix direction / budget:** one kind registry in a structural wave; spice-offline oracle identical.

### KH-860: the Action entrypoint has no Python runner

**Severity:** LOW (architecture, deferred by ruling; harness-coupled)
**File:** `action/entrypoint.sh` (audit ar/R5-F4)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-action-python-runner)

**Symptom:** the step logic stays in shell with inline `python3 -c` readers (see KH-852). The dead-copy half of ar/R5-F4 is done (`463c523`, KH-572); the runner is neutral but has no product oracle.

**Fix direction / budget:** a tested Python runner with an Action output parity check; coordinate with the harness (the Action tests are harness-side).

### KH-861: `build_connectivity_graph` stays in `pcb.presentation` — moving it needs two harness patch targets moved first

**Severity:** LOW (architecture, deferred by ruling; harness-coordinated)
**File:** product `pcb/presentation.py` → `pcb/pipeline.py` (audit A2-F6, `ARCHITECTURE.md:184`); harness `tests/test_kh_v22x_pcb.py:26,173` (`patch.object(pcb_presentation, "build_connectivity_graph", ...)`) and `tests/test_api_migration.py:427-438` (expects `("pcb.presentation", "build_connectivity_graph")`)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-pcb-late-phase-move)

**Symptom:** the late PCB phases moved except this one; moving it would break the harness patch target.

**Fix direction / budget:** harness checkpoint first (re-target the patch to `pcb.pipeline.build_connectivity_graph`, tolerant of both locations, and update the api_migration expectation), then the structural move with an empty budget.

### KH-871: on Windows, the KH-811 identity fallback returns None for every read if `fstat` and `lstat` disagree on `st_ino`/`st_dev`

**Severity:** LOW (Windows only; risk not demonstrated)
**File:** `skills/datasheets/datasheet_types/cache_reader.py:74` (`if not hasattr(os, "O_NOFOLLOW") and not os.path.samestat(st, os.lstat(path)): return None`)
**Discovered:** 2026-11-03, product 3.0.x Wave 8c (slug KH-new-windows-fstat-identity); verified harness-side at `0efc012` by reading only (Linux box; the branch is not reachable here)

**Symptom:** if some Windows filesystem or Python version fills `st_ino`/`st_dev` differently for `fstat` and `lstat`, every extraction read silently returns None and datasheet-backed findings disappear with no warning.

**Fix direction / budget:** a Windows smoke run (one cached extraction read through `read_json_object`) before v3.0.1 ships; consider a one-time stderr note when the identity check refuses a regular file. Corpus-neutral. Before v3.0.1 ships (smoke run); any code change post-3.0.

### KH-872: a `--force-all` refresh that verifies as a different part replaces a good `ok` entry and deletes its PDF

**Severity:** LOW
**File:** `skills/datasheets/distributor_core/sync.py:56-57` (`_outage_entry`: any `ok` result replaces the entry), `:165-176` (`_replaced_file`), `:191-218` (`_record` removes the old PDF); verdict from `distributor_core/verify.py:243-269` (`"verification": "wrong"` keeps `"status": "ok"`)
**Discovered:** 2026-11-03, product 3.0.x Wave 8c (slug KH-new-force-all-wrong-part-ok); verified harness-side at `0efc012` (code reading; at `647bc85` `_outage_entry` already replaced the entry, but no PDF was removed)

**Symptom:** a refresh whose PDF fails identity verification (`verification: wrong`) still counts as `ok`, so it overwrites a verified entry; since KH-813 the previous PDF is also deleted when the new file name differs. The handoff says this predates the wave: the entry replacement does, the deletion is new in 8c.

**Fix direction / budget:** treat an `ok` with `verification: wrong` like an outage when the previous entry is `ok` and its file exists (keep entry and PDF, report the result). Distributor-offline lane only if a fixture covers it. Post-3.0.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 355afcfb fix(datasheets): a refresh that verifies as a different part keeps the previous datasheet (v3.0.2 Wave 11a Task 25, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `skills/datasheets/distributor_core/sync.py:58-68` handles an `ok` refresh with `verification: wrong` over a verified `ok` entry whose file exists under a different name. The run keeps the previous entry and PDF and reports `failed`, and `_record` removes the new wrong file instead (`:201`).
- **Left open:** the same-name case. The refreshed file has already overwritten the good PDF, so the code leaves it alone (comment at `:64`).

### KH-874: bus labels are never net-name candidates, so a net reached only through a bus member takes a child-sheet name

**Severity:** LOW (net naming on bus-heavy hierarchical designs; the jotego s18 regression waived in Wave 8b)
**File:** `skills/kicad/scripts/schematic/connectivity.py:758-759` (`if idx in bus_label_idx: continue`); bus member slots `("bus", sheet, cluster, member)` at `:885-889` carry no `point_info`, so the naming loop at `:1095-1135` never ranks them
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (code reading; the s18 numbers 331/279 → 281 are the product's measurement, not re-run)

**Symptom:** KiCad names a bus member net after the bus label's member (on the shallower sheet first). The analyzer drops bus labels from the label pass, so a net whose shallowest driver is a bus member is named by a deeper hierarchical label instead. The skip applies to bus labels on every sheet; the handoff's "root-level" is the case where it changes the winner.

**Fix direction / budget:** give each bus member slot a candidate entry (priority of the bus label's type, the bus label's sheet) so the depth/full-name tie-break sees it. Output-changing: net renames on bus designs (standard + full-chain); measure against `regression/netlist_oracle.py`. Post-3.0.

### KH-876: VM-001 takes one voltage per multi-unit IC from the first powered pin, so multi-bank FPGAs swing with pin order

**Severity:** LOW (VM-001 on multi-bank FPGAs/MCUs; ±44-100 findings on three boards per the product survey)
**File:** `skills/kicad/scripts/validation_detectors.py:496-500` (`_ic_rail_voltage`: first positive power-pin voltage in `ctx.ref_pins` order)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (code reading; counts from survey-sch §4: EI2030 Archer −49, Caster −44, aswinvenu BeagleV −100 when the unit order changed)

**Symptom:** a bank-split IC (1.35 V DRAM bank, 1.8 V config bank, 3.3 V I/O) gets one voltage, taken from whichever unit's power pin comes first. Every signal pin is judged against it, so VM-001 flags a different set of nets when the sheet or unit order changes. Wave 8b made the order stable; the result is still wrong.

**Fix direction / budget:** per-unit (or per-bank) supply voltage for the pins of that unit. Output-changing: VM-001 on multi-unit ICs; measure before budgeting. Post-3.0.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; slug KH-new-vm001-core-rail-logic-level):** the same first-positive-pin rule (`validation_detectors.py:498-506`, `_ic_rail_voltage`) takes an MCU's core rail as its I/O level when the core rail carries a name voltage and the I/O rail does not. es-ude/elastic-ai.hardware v6 `main_env`: RP2040 U7 IOVDD on `VCC_MCU`, DVDD on `MCU_1V1`. VM-001 "PIO6/I2C1_SDA: 3.3V / 1.1V domain crossing" with the PAC1934s (11c moved it from 1.8 V; v5 `elasticnode_tiny` already read 1.1 V). Fix with KH-876: choose the I/O supply pin by name (IOVDD/VDDIO/VCCIO/VDD over DVDD/VCORE/VREG_VOUT) before pin order.

### KH-878: I2C recognition misses numbered bus names (`SCL2`/`SDA2`, `SCL_2`)

**Severity:** LOW (DO-DET `i2c_bus` records and pull-up checks on second/third I2C buses)
**File:** `skills/kicad/scripts/signal_detectors.py:3827-3828` (`\bSDA\b(?!T)` / `\bSCL\b`, else `I2C.*SDA` forms)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (the two regexes on literals: `SCL2`, `SDA2`, `SDA0`, `SCL_2`, `/X/SCL2` miss; `I2C2_SCL` matches)

**Symptom:** a word boundary is needed after `SDA`/`SCL`, so a digit (or `_2`) suffix fails. The 12v-2x6 board loses its 2 true I2C records once KH-800 names the nets `SCL2`/`SDA2`.

**Fix direction / budget:** allow an optional `[_]?\d+` suffix (`\bSDA(?:_?\d+)?\b(?!T)`, same for SCL). Output-changing: DO-DET i2c records added; measure before budgeting. Post-3.0.

### KH-879: legacy KiCad 5 `.sch` still breaks net-name ties by sheet index

**Severity:** LOW (hand-reordered legacy hierarchies only; 881 legacy multi-sheet files, none known reordered)
**File:** `skills/kicad/scripts/schematic/pipeline.py:1061-1064` (`analyze_legacy_schematic` calls `build_net_map` without `sheet_paths`), so `skills/kicad/scripts/schematic/connectivity.py:1131-1132` ranks by `(sheet index, name)`; sheet order from `legacy_reader.py:1070` (file order)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (code reading)

**Symptom:** for legacy files, equal-rank names still depend on the order `$Sheet` blocks appear in the file. Wave 8b left this unchanged on purpose (KiCad 5 builds its sheet list in file order; kicad-cli 10 cannot load legacy files to check).

**Fix direction / budget:** confirm KiCad 5's rule (eeschema 5 source) before changing; if it is depth + full name, pass legacy `sheet_paths`. Output-changing on legacy hierarchies; measure first. Post-3.0.

### KH-880: the KH-800 tie-break is unverified on multi-root (peer top-level sheet) projects

**Severity:** LOW (KiCad 10 multi-root projects)
**File:** `skills/kicad/scripts/schematic/hierarchy.py:430-432` (`merge_top_level_sheets` extends `sheet_paths` with each peer's paths, which start at "/"); `skills/kicad/scripts/schematic/connectivity.py:1129-1130`
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (code reading; `tools/tests/test_sheet_order.py` and `test_top_level_sheets_kicad10.py` have no tie across peer roots)

**Symptom:** every peer root gets the path "/", so labels on two top-level sheets tie at depth 1 and fall to the name. Whether KiCad qualifies peer roots by their own sheet name is not checked against kicad-cli.

**Fix direction / budget:** build a two-root fixture with an equal-rank tie across roots, compare with a kicad-cli netlist, then fix the path if it differs. Output-changing only if the rule changes. Post-3.0.

### KH-881: inner-layer trace impedance uses the microstrip formula with bulk εr; no stripline formula

**Severity:** LOW (`impedance_ohm` on inner layers; no finding reads the field)
**File:** `skills/kicad/scripts/pcb/routing.py:716-763` (`_microstrip_impedance`, `outer=False` keeps `e_eff = er`); callers `:859-860`, `:894-895`
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-820); verified harness-side at `0efc012` (code reading)

**Symptom:** KH-820 fixed outer layers with Hammerstad εeff. A buried trace is stripline (two reference planes), so the microstrip expression with bulk εr is only a rough estimate there.

**Fix direction / budget:** IPC-2141 / Cohn symmetric or offset stripline using the two nearest plane heights from the stackup. Output-changing: full-chain `impedance_ohm` on inner layers (982 values in the product's 163-board sample). Post-3.0.

### KH-884: `0R/2A` (a zero-ohm link with its current rating) now reads None

**Severity:** LOW (0 corpus records per the product)
**File:** `skills/kicad/scripts/kicad_core/values.py:33-35` (`_IMPEDANCE_SLASH`), `:125`
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-850); verified harness-side at `0efc012` (`parse_value('0R/2A')`, `'1R/2A'`, `'0 Ohm/2A'` all None for every component type; `0R/0805` 0.0)

**Symptom:** the KH-850 rule treats any `<n>R/<current>` as ferrite impedance notation, so a jumper or low-ohm resistor with a current rating loses its value.

**Fix direction / budget:** exclude a resistor-typed part, or a zero value, from the slash rule. Output-changing only where such values exist (none measured). Post-3.0.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 285054a6):** fixed: values below 1 ohm with an ampere rating (`0R/2A`, `0.1R/3A`) keep their value (`values.py:36-37`, `:129` `_LOW_OHM_RATED`). Still open: `1R/2A` (a listed symptom) still reads None. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-885: the EMC high-speed/clock net classifier matches substrings (`ADDR`, `lse`/`hse`/`osc`, enable lines) and misses common names (`D+`/`D-`, `TX0P`, `SDIO_D0`)

**Severity:** LOW (GP-001 split errors on slow nets, missed on fast ones; also sets GP-001 coverage severity)
**File:** `skills/emc/scripts/emc_rules.py:158-181` (`_is_clock_net`, `_is_high_speed_net`: plain `in` on the lower-cased name); used at `:482`, `:560`, `:2560` and `:4111`
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-795); verified harness-side at `0efc012` (`_is_high_speed_net`: True for `ADDR0` (ddr), `PULSE`/`FALSE_TRIG` (lse), `HSENSE` (hse), `OSC_EN`, `USB_EN`, `ETH_EN`, `USBOTG_ID`, `Net-(U1-CLK)`; False for `D+`, `D-`, `TX0P`, `TX0N`, `SDIO_D0`, `SDIO_CMD`)

**Symptom:** one of the 8 split GP-001 errors in the product sample is `USBOTG_ID`, a slow net. Address buses, pulse/false-named nets and peripheral enables also match; USB data nets named `D+`/`D-`, differential pairs `TXnP/N` and SDIO data lines do not.

**Fix direction / budget:** token-based matching (split on `_`/`-`/`/`, whole tokens or known prefixes), excluding enable/ID/detect suffixes and `Net-(` pin-derived names, adding `D+`/`D-`, `*P`/`*N` pair suffixes and `SDIO_*`. Output-changing: GP-001 severity and split errors; measure before budgeting. Post-3.0.

### KH-886: a reference-plane change is missed when a short segment lies entirely over the gap

**Severity:** LOW (KH-795 split detection)
**File:** `skills/kicad/scripts/pcb/routing.py:560-626` (`_plane_net_changes`: within-segment changes need two counted samples on one segment; junction changes need counted samples on segments sharing an end)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-795); verified harness-side at `0efc012` (direct call: GND segment → 1 mm segment with no plane hit → +3V3 segment returns `[]`; the same GND and +3V3 segments joined directly return the pair)

**Symptom:** the segment over the gap has no counted samples, so neither neighbour shares an end with a counted sample of the other net, and the crossing is not reported. Segments under 0.1 mm are also skipped at `:494`.

**Fix direction / budget:** walk the net's segment graph and compare the last counted plane net before and the first after any run of unknown samples. Output-changing: `reference_plane_changes` entries and GP-001 split errors; measure. Post-3.0.

### KH-887: reference-plane sampling ignores arcs

**Severity:** LOW (boards with curved routing)
**File:** `skills/kicad/scripts/pcb/routing.py:427` (`segments = tracks.get("segments", [])`; no `tracks["arcs"]` loop in `analyze_return_path_continuity`)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-795); verified harness-side at `0efc012` (code reading; every other routing pass in the file reads `tracks["arcs"]`, `:47,124,865,1057,1131,1280`)

**Symptom:** a crossing on an arc is not seen, and an arc between two segments breaks the end-key join, so a change across it is missed. The older `return_path_continuity` coverage has the same gap.

**Fix direction / budget:** sample arcs along their chord points (as `analyze_net_lengths` does) and give them end keys. Output-changing on `--full` boards with arcs (`reference_plane_changes`, `return_path_continuity`, GP-001); measure. Post-3.0.

### KH-888: at a junction where three plane nets meet, only one pair is reported

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/routing.py:622` (`a, b = sorted(by_net)[:2]`)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-795); verified harness-side at `0efc012` (direct call: GND, +3V3 and +5V segments meeting at one end give only (+3V3, +5V))

**Symptom:** the alphabetically first two nets are kept; the pairs involving the third net (here GND) are dropped, which can also hide the pair a bridge capacitor does not cover.

**Fix direction / budget:** emit every pair at the junction (or every pair not already bridged). Output-changing: `reference_plane_changes` entries; measure. Post-3.0.

### KH-889: the 2 mm plane-hold rule sums branch lengths at a T-junction

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/routing.py:595-602` (runs touching the same segment end and net are unioned, `held` sums their lengths)
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-795); verified harness-side at `0efc012` (direct call: GND trunk plus two 1 mm +5V branches at one T reports a +5V/GND change; a single 1 mm +5V branch does not)

**Symptom:** the rule is meant to require about 2 mm of continuous trace over a plane net. At a T, two short stubs each under the limit add up and pass, so a pad-sized island under a stub fork counts as a plane change.

**Fix direction / budget:** measure the longest path through the unioned runs rather than the sum. Output-changing: fewer `reference_plane_changes` / GP-001 split errors; measure. Post-3.0.

### KH-896: lifecycle `sources_available` lists only sources that returned data — a configured source that fails reads the same as an unconfigured one, with no diagnostic

**Severity:** LOW (report trust: the reviewer cannot tell "element14 not set up" from "element14 down / key rejected")
**File:** `skills/kicad/scripts/lifecycle_engine.py:1079` (`5687ee1`; `lifecycle_audit.py:929` at `07b7fb1`) — built from `f["sources"]` of the findings; `query_lifecycle_element14` (:407) returns `None` both for a missing `ELEMENT14_API_KEY` and for any `URLError` / `OSError` / JSON error; `audit_component` keeps a per-part `attempted` list but the envelope does not carry it.
**Discovered:** 2026-11-03, SacMap rev2 soak run 10 (as KH-895); element14 key exported, no element14 data, no message; verified at `07b7fb1` and `5687ee1`

**Fix direction / budget:** add `sources_attempted` (configured) and `sources_failed` (configured, every call errored) to the envelope, and a `diagnostics` record or stderr line per failing source. Additive lifecycle envelope keys only. Post-3.0.

### KH-900: `spice.json` `simulator` is the ngspice path with no version, beside `total_elapsed_s` — a reviewer read the elapsed time as the version

**Severity:** LOW (provenance: the simulator version is not recorded)
**File:** `skills/spice/scripts/simulate_subcircuits.py:398-400` (`5687ee1`; :385-387 at `07b7fb1`) — `report["simulator"] = find_ngspice()` (path), `report["ngspice"]` alias, no version field.
**Discovered:** 2026-11-03, SacMap rev2 soak run 10 (as KH-895); reviewer-agent claim, verified by code read at `07b7fb1` and `5687ee1`

**Fix direction / budget:** add `simulator_version` (from `ngspice --version` / the batch banner, once per run). Additive SPICE envelope key; spice-offline comparator must mask or allow it. Post-3.0.

### KH-901: one run carries two unrelated ids — analysis folder `2026-11-03_0917` (local time) and provenance `run_id` `20261103T171710Z-581a02` (UTC) — and no output links them

**Severity:** LOW (cross-referencing a report to its envelopes; the two timestamps also differ by the UTC offset)
**File:** `skills/kicad/scripts/analysis_cache.py:226` `generate_run_folder_name` (local `%Y-%m-%d_%H%M`) vs `skills/kicad/scripts/run_id.py:44` `generate_run_id` (UTC `%Y%m%dT%H%M%SZ-<hex>`) at `5687ee1` (:287 / :40 at `07b7fb1`); the manifest does not record the `run_id`. The `5687ee1` docstrings name the distinction; outputs do not.
**Discovered:** 2026-11-03, SacMap rev2 soak run 10 (as KH-895); reviewer-agent claim, verified by code read at `07b7fb1` and `5687ee1`

**Fix direction / budget:** record the provenance `run_id` per run in the manifest (and the folder name in `capability_mode.json`), or derive one from the other. Additive manifest / envelope key. Post-3.0.

### KH-906: `analysis_cache.load_manifest` still opens `analysis/manifest.json` following links and unbounded

**Severity:** LOW
**File:** `skills/kicad/scripts/analysis_cache.py:192` (`with open(manifest_path, 'r', encoding='utf-8')`) at `6009004`
**Discovered:** 2026-11-03, product 3.0.x Waves 9a + 9e handoff

**Symptom:** a planted FIFO at `analysis/manifest.json` blocks the reader; the Wave 9a manifest-read hardening covers the other readers.

**Fix direction / budget:** read via `read_json_object`. Corpus-neutral.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, claimed fixed by the handoff; partly fixed):**
- **Fixed:** product v3.0.x-dev 5c8c73ef fix: analysis cache ignores link, FIFO, malformed and too-deep manifests and run entries (v3.0.2 Wave 11a Task 17, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `analysis_cache.py:188-208` opens with `O_NOFOLLOW|O_NONBLOCK`, checks `fstat` for a regular file and drops links and FIFOs with a diagnostic. Probe: a FIFO at `manifest.json` returns the empty manifest at once, with a warning.
- **Left open:** the "unbounded" half of the title. `_read_manifest_bytes` still calls `f.read()` with no size cap (:208). The filed fix (`read_json_object`, 10 MB cap) was not used.

### KH-908: LTspice / Xyce `format_measurement_block` drop `extra_vars` (no `model_source` note)

**Severity:** LOW (roadmap)
**File:** `skills/spice/scripts/spice_simulator.py` — only the ngspice backend reads `extra_vars` (:181); the other backends accept and ignore it, at `6009004`
**Discovered:** 2026-11-03, product 3.0.x Waves 9a + 9e handoff

**Symptom:** model metadata (the `model_source` note) is lost under LTspice / Xyce.

**Fix direction / budget:** carry metadata outside the measurement echo stream for every backend. ngspice is the only simulator the corpus lanes run.

### KH-915: EP-AUD and EG-001 list NC-type connector pins as unprotected signal nets

**Severity:** LOW (info-level EP-AUD lists and EG-001 `unprotected_nets` text)
**File:** `skills/kicad/scripts/domain_detectors.py:2480-2486` (`audit_esd_protection`: a connector net is skipped only when it is ground or power; no pin-type test); `skills/kicad/scripts/cross_analysis.py:330-337` (`check_esd_coverage_gaps`, same filter on `pin_nets`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-4-report.md`; `D/surveys/survey-sch.md` item 1, ruling sch P4)

**Symptom:** a connector pin KiCad types `no_connect` sits on its own net after the Wave 9b NC isolation, and EP-AUD lists that net as an unprotected signal net. The base already listed 414 NC-pin-only nets on the survey's NC sample; the isolation adds +87 / −19 entries on 39 units (survey-sch :62, :78). EG-001 reads the connector's `pin_nets` with the same name-only filter.

**Fix direction / budget:** skip pins typed `no_connect` when collecting `signal_nets` in EP-AUD and `unprotected_nets` in EG-001. Output-changing: EP-AUD `signal_nets` / `unprotected_nets` / `coverage`, EG-001 counts. v3.0.2 (ruling sch P4).

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by eca70eb2):** fixed: EP-AUD and EG-001 skip nets whose pins are all `no_connect` (`domain_detectors.py:2460-2463`, `:2505`; `cross_analysis.py:341-343`). Still open: KiCad 5 files type NC pins `unconnected` (`legacy_reader.py:36`), which the filter misses: 297 EP-AUD records on 125 units keep NC nets (filed separately). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-917: regulator suffix voltages: integer-volt families get no value, and package names the token list misses still read as a voltage

**Severity:** LOW (PR-DET `estimated_vout` and the thermal estimate)
**File:** `skills/kicad/scripts/kicad_core/parts.py:201-204` (`_PACKAGE_TOKEN`), `:208` (`_AMBIGUOUS_SUFFIXES`), `:233-237` (two-digit suffix read as a decimal), `:238-241` (fall-through to `_REGULATOR_VREF`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-5-report.md`, `task-5-review.md`; `D/surveys/survey-sch.md` P2)

**Symptom:** three parts.
- The ambiguous suffixes `-05/-09/-10/-12/-15/-24/-48` give no value, on purpose (ruling 16a refined), so 35 corpus parts lose a correct estimate (task-5-report :36: LM2678S-12 x4, LM2940-12 x4, LM2596S-12 x4, NCP1117-12 x3, TL780-12/15 x4, …).
- An ambiguous fixed part falls through to the adjustable Vref table: probe at `8c42799`, `lookup_regulator_vref("LM2596S-12", "")` = `(1.23, "lookup")`.
- `_PACKAGE_TOKEN` has no MLP, WLCSP, PowerPAD, SO, LFCSP, TSOP, HSOP, ESOP, DSBGA, UQFN, QSOP, PQFN or DDPAK. Probe: `REG_MLP-16` → 1.6 V, `REG_WLCSP-25` → 2.5 V, `REG_PowerPAD-20` → 2.0 V, all `fixed_suffix`. This was already so in the base (task-5-review :19).

**Fix direction / budget:** option b of P2: integer-volt families for the ambiguous suffixes (LM2596/LM2940/NCP1117/LM2678/TL780/… `-12` = 12 V). An ambiguous fixed part should give no value rather than an adjustable-table Vref. Widen `_PACKAGE_TOKEN`. Output-changing: PR-DET `estimated_vout` / `vref_source` on those parts, thermal `skipped_components`. v3.0.2.

**Addendum 2026-11-04 (3.0.x Waves 9b + 9c gate):** the decimal-suffix rule also gives a wrong value: `LC78_03-05` (der-pw/hm_stm32_2ch_dimmer, `Kicad_STM32_2CH_Dimmer.sch`) reads `_03` as 0.3 V, and EMC now adds a PD-001 "VCC PDN anti-resonance exceeds target" at Vout = 0.3 V, target 0.034 Ω (std gate EMC lane, PD-001 +1). The part is a 3.3 V module; a suffix followed by another `-NN` group needs the family rule too.

**Addendum 2026-11-04 (3.0.x Wave 9f, `2a9db0b3`, gated at `246ee5a`):** the low-suffix case is fixed — a two-digit suffix below 0.5 V gives no value. Std gate: 4 units move (BerkeleyLab/Marble `design_Power`, `design_Power_SW`, `design_Marble` ADM7155ACPZ-02-R7; der-pw/hm_stm32_2ch_dimmer LC78_03-05, whose EMC PD-001 at Vout 0.3 V goes); faoziaziz/qris_iot UM1750S-00 does not move in the output (its Vout comes from the feedback divider on both sides). Still open (v3.0.2): integer-volt families (`-05/-09/-10/-12/-15/-24/-48`) and the package tokens `_PACKAGE_TOKEN` misses.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 28487ee0):** fixed: the missing package tokens (`parts.py:203-207`), the ambiguous two-digit suffix skip (`:237-268`) and a per-family integer-volt table (`:213-221`). Still open: LM2678S-12 (named in the issue), LM2676, LM2575, LM1085 and LM340 now give no value instead of the right one; a fixed-suffix part with an FB divider is still overwritten by the heuristic sweep (`signal_detectors.py:2122-2150`, hackclub LM2596S-12 reads 6.6 V; filed separately). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-918: DO-DET "IC missing decoupling" on rails whose caps have values the parser cannot read

**Severity:** LOW (info-level DO-DET)
**File:** `skills/kicad/scripts/signal_detectors.py:1263-1267` (`detect_decoupling` keeps a cap only when `ctx.parsed_values` has it); `:3701`, `:3716-3732` (`detect_design_observations` flags every IC power net not in `decoupled_rails`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-8-report.md` :194-203; `L9B/progress.md` Task 8 handoff item)

**Symptom:** about 20 DO-DET "IC X missing decoupling on <rail>" findings on the Task 8 sample300, on topology rails that do have a cap to ground. DC-DET drops the cap because its value does not parse. Probe at `8c42799`: `parse_value` returns None for `C_100n_0402`, `C`, `1u,20%,6.3V` and `C0805C105K4RACTU`. Name rails with such caps already had the same false claim.

**Fix direction / budget:** count a two-terminal cap to ground as decoupling present even when its value is unknown (with no capacitance total), or parse the underscore / MPN-style value forms. Output-changing: DC-DET entries and DO-DET "missing decoupling" on boards with such values.

### KH-919: topology rails: a single cap/bias `power_out` pin makes a rail; net ties ignored; motor-driver break and bridge-name rule over-reach

**Severity:** LOW (rail set: DC-DET / DO-DET / rail-dependent detectors)
**File:** `skills/kicad/scripts/schematic/net_analysis.py:324-382` (`topology_rail_nets`): `:356-364` (any `power_out` IC pin not excluded by name counts as a supply; a part classed `motor_driver` breaks the net; the bridge-name exemption depends on `_ic_function`), `:367-368` (`power_in` by supply name, so a VBUS / VBAT pin behind an RC counts), `:375-380` (only capacitor / resistor neighbours are read; net ties are not consulted), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/progress.md` Task 8 minors; `task-8-report.md` :213-221, :268-273; `task-8-rereview-1.md` :42, :51)

**Symptom:**
- a sensor or DSP with one `power_out` cap/bias pin makes that net a rail: LIS2MDL `C1` (set/reset cap; gains DC-DET and DO-DET "Decoupling on C1") and FV-1 `MID`.
- a rail reached only through a net tie is missed.
- `VBUS_DET` / `VBAT_SENSE` `power_in` pins behind an RC become rails (ruling P5; none in the sample).
- the bridge-name rule depends on the IC classifier: a regulator described as sensor/display first falls under it.
- the `motor_driver` break also disqualifies a real supply output on a motor-driver part, e.g. DRV83xx VREG feeding an MCU VDD.

**Fix direction / budget:** require two or more supply-input pins (or a power_management part) before a lone `power_out` makes a rail; read net-tie conductors (`conductor_of`); break on bridge-named outputs only, not on every `power_out` of a motor driver. Output-changing; measure on the Task 8 sample before budgeting.

### KH-924: `.kicad_dru` parse errors KiCad raises are not all modelled

**Severity:** LOW (custom rules applied where KiCad would refuse the file)
**File:** `skills/kicad/scripts/kicad_core/project.py:662-688` (`_dru_parse_error`: checks the version statement, top-level forms, rule names, severity names and unitless lengths only), at `8c42799`. The variant half is in `skills/kicad/scripts/schematic/reader.py:897-913`.
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`D/surveys/survey-pcb.md` item 3 :91; `L9B/task-12-report.md`, `task-12-review.md` :10; `L9B/progress.md` Task 2 minor)

**Symptom:** an unknown constraint type, an unrecognised layer, an unparseable condition or an unresolved text variable makes KiCad refuse the whole file, but the analyzer still applies the rules. The review also flags two stricter-than-KiCad cases that are unverified: a UTF-8 BOM before `(version 1)` is refused ("Missing '('."), and the keyword match is case-sensitive (`(Version 1)`, `(severity Error)`). The handoff puts a second item on this slug that is not a DRU item: in the schematic reader the variant `_props` override folds case (`reader.py:904-905`), but the text-variable path `var_fields.get(name, text)` (`:913`) still needs the exact case.

**Fix direction / budget:** add the remaining parse checks behind kicad-cli DRC cases (corpus census showed 0 refused files among 586 `.kicad_dru`, so expect ~0 corpus delta); settle BOM / case against kicad-cli; make the variant text-variable lookup use the same rule as `_props`. Related: KH-764, KH-773, KH-945.

**Addendum 2026-11-05 (3.0.x Wave 10a handoff, candidate `e60d03b5`):** a nested condition is one of the unparseable conditions above: probe at `e60d03b5` `(rule a (condition (x)) (constraint clearance (min 0.2mm)))` loads with `custom_rules_error` unset and `condition` = the string `"['x']"`, while kicad-cli 10.0.8 refuses the file. Wave 10a added the nested severity / constraint type / layer refusals only. The opposite divergence, a nested bound kicad-cli applies, is KH-947.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev cdb1d299 fix(pcb): refuse a .kicad_dru with an unknown constraint, item or layer, a malformed condition, or a repeated constraint; 724f368d unbalanced parentheses; 88e78f24 fix(schematic): a variant overrides a symbol field only by its exact name (v3.0.2 Wave 11a Task 9/10, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `kicad_core/project.py:851-903` `_dru_parse_error` is checked by probe. These are refused:
  - an unknown constraint type
  - an unknown layer
  - a nested condition `(condition (x))` (the 10a addendum case)
  - a repeated constraint
  - a leading BOM and `(Version 1)` (kept refused, pinned against kicad-cli in the task-9 report)
- Variant half: `schematic/reader.py:904-907` now applies a variant field to `_props` only by exact name, the same rule as `var_fields.get(name)`.
- **Left open:** the duplicate-layer refusal and the `hole`/`mechanical_*` aliases (11b, declared; probe: `(layer outer) (layer inner)` loads with no error). Also still not refused:
  - a syntactically malformed condition string, e.g. `"A.Type == "`
  - an unresolved `${FOO}` text variable in a condition
  - The issue lists both as KiCad refusals. The declared scope does not name them, and I did not check them against kicad-cli.

---
Tally: 33 checked. 29 FIXED (KH-725/728/749/817 against the narrowed scope) and 4 PARTIAL (805, 872, 914, 924, all expected). 0 NOT-FIXED, 0 UNCLEAR.

**Addendum 2026-11-06 (Wave 11a handoff candidate, verified at `5510006a` against kicad-cli 10.0.8 `pcb drc` with a sentinel rule; KiCad drops a refused file silently):** over-refusal: `solder_paste_rel_margin (opt -0.1)` (and `(opt -10)`) loads in KiCad, but the reader says "Missing units." (`kicad_core/project.py:693-694` `_DRU_UNITLESS_CONSTRAINTS` lacks it, `:801-809`). Under-refusals (KiCad refuses, the reader accepts): `min_resolved_spokes` with any `(min/opt/max …)` bound (KiCad takes only the bare `(constraint min_resolved_spokes 2)`, and the reader keeps no value for that form), `track_angle (min 45deg)`, `clearance (min 0.1MM)`, a tab inside an expression (`0.1mm<TAB>+<TAB>0.1mm`, evaluated to 0.2). Correction to the handoff: comma decimals (`0,1mm`) LOAD in kicad-cli 10.0.8, so the reader agrees there.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by d3383359):** fixed: `kicad_core/project.py:908-911` refuses a second `(layer ...)` ("'layer' keyword already present."); `:835-836`, `:996` map `hole`, `mechanical_clearance`, `mechanical_hole_clearance` to their current names; `:1004` reads a comma between digits as the decimal point. Probe confirms all three. Still open: Still not as kicad-cli 10.0.8 (probe of `load_kicad_dru_checked` at 6138b126): a malformed condition string `"A.Type == "` loads with no error, and so does an unresolved `${FOO}` in a condition (`_dru_parse_error` `:886-892` checks only nesting and arity). The 11a addendum items are unchanged: `solder_paste_rel_margin (opt -0.1)` is refused "Missing units." (not in `_DRU_UNITLESS_CONSTRAINTS`, `:701-702`); `min_resolved_spokes (min 2)`, `track_angle (min 45deg)`, `clearance (min 0.1MM)` and a tab inside an expression all load (KiCad refuses them). None of these is in the D8 scope or scheduled. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-925: shared `is_ground_name` holes: `0V_10V` interface nets read as ground, `AVSS` / `DVSS` / `ground` / `VGND1` not

**Severity:** MEDIUM (shared predicate, many consumers; false GP-005 on 2 boards)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:248-285` (`is_ground_name`): `:270` (`^\+?0+V(?!\d)([A-Z_][A-Z0-9_]*)?$` accepts `0V_10V`), exact set without `AVSS`/`DVSS`/`GROUND`; consumer `skills/kicad/scripts/pcb/routing.py:972-976` (PCB ground domains: `COM` only when the rail set names it, otherwise the shared rule or the leaf substring `GND`/`VSS`/`GROUND`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-14-report.md` :20-22; `L9B/final-fix-report.md` :11, :35-37)

**Symptom:** probe at `8c42799`:
- `is_ground_name` True for `0V_10V`, `/Board_ZorionX/0V_10V/0V_10V`, `0V_32V` (0-10 V / 0-32 V interface nets; false GP-005 on 2 boards) and for bare `COM`;
- False for `AVSS`, `DVSS`, `ground`, `VGND1`, `REFGND_0.5V`, `Virtual_Ground`, `HEATER_GND_1`, `AGND_CODEC`. `VGND` alone is True, so the handoff's "VGND not taken" holds only for the numbered forms.

The PCB ground-domain rule (`routing.py`) recovers the GND/VSS-substring names and keeps virtual grounds (`VGND1..8`, `VGND_V+`, `REFGND_0.5V`, `Virtual_Ground`) and switched returns (`HEATER_GND_1`, `CONTROL_VALVE_GND_n`) as domains, as in v3.0.0. Battery-negative domains (`BAT-`, `BATT-`; switched from GND on fuzzface/ts9/tp4056) give a MEDIUM "ground domains" finding of low value (task-14-report :21).

**Fix direction / budget:** the zero-volt pattern should not take `0V_<n>V`; add `AVSS`/`DVSS`/`GROUND` and the `VSS*`/`*GND<n>` forms to the shared rule; decide whether virtual grounds and switched returns are domains. Output-changing across every `is_ground_name` consumer; needs its own gate. Same family as KH-938 / KH-939.

**Addendum 2026-11-06 (Wave 11a handoff candidate, verified at `5510006a`):** `is_ground_name` (`kicad_core/netnames.py:248-285`) returns False for `GROUND`, `EARTH`, `CHASSIS` and `PE` even when the name is a power rail (`GND_CHASSIS` / `CHASSIS_GND` return True). Consequences: EX-001 (`lookup_detectors.py:586-601`, via `ctx.is_ground`) does not credit a capacitor returning to them, and PR-DET's ground checks (`signal_detectors.py:1985-2044`, incl. the three-terminal ADJ test) see them as non-ground on every project, not only projects with extraction caches as the handoff said.

**Addendum 2026-11-07 (Wave 11b-1 handoff candidate, verified at `f53d107e`, probe):** `Earth` and `Earth_Protective` (KiCad `power:Earth` / `power:Earth_Protective` symbols) are not ground but are power rails once a power symbol names them: `is_ground_name("Earth", {"Earth"})` False, `is_power_net_name("Earth", {"Earth"})` True (same for `Earth_Protective`, `EARTH`, `PE`). So `ctx.is_power_net` and `not ctx.is_ground` treat them as a supply (rail lists, DC-DET "decoupling on Earth", drain-to-supply tests). The handoff's flyback case (x_board, arduino++, brainmachine: a diode anode on Earth read as drain-to-supply flyback) no longer misfires at `f53d107e`: the TR-DET orientation check (`signal_detectors.py:3507-3514`) now needs the anode on the drain. The name gap remains for every other consumer.

**Addendum 2026-11-07 (Wave 11b-1 handoff candidate, verified at `f53d107e`, probe):** `is_ground_name` accepts `COM` (exact set, `kicad_core/netnames.py:275-277`) and any `GND*` / `*GND` name (`:290-291`), so `GND_LED`, `GND_BULB`, `LED_GND`, `GND_MOTOR` (designer-named switched returns) read as ground. New consumer in v3.0.2: CG-AUD now judges *pin names* on unnamed nets with it (`domain_detectors.py:5499-5510` `_ground_pin_on_wired_unnamed_net`). OLIMEX ESP32-EVB B/F/K2 and ESP32-GATEWAY D LAN1 count the Ethernet magnetics centre tap `COM` (75 Ω + cap) as a ground pin (4 units, a 5:1 advisory lost). FabianGmeiner BMW E30 J1 counts `GND_LED` / `GND_BULB` (warning → info). Wave 11c's A/B must include CG-AUD.

**Addendum 2026-11-07 (product v3.0.2 Wave 11b-1 handoff candidate, verified at `f53d107e`, code read + probe + corpus read):**
- **The hole:** `is_ground_name` (`kicad_core/netnames.py:259-295`, prefix/suffix test `:290`) accepts `GND*` / `*GND` and exact `PGND`, but not a ground prefix followed by a rail suffix.
- **Probe:** `PGND_3V3`, `AGND_5V` and `DGND_1V8` are not ground, and `parse_voltage_from_net_name` gives them 3.3 / 5.0 / 1.8 V.
- **Corpus:** on `bluerobotics/ping-dev-kit` `lumen2_3v3_buck` and `power-layouts_lumen2_3v3_buck`, the net `PGND_3V3` carries GNDREF power symbols and U5 `PGND`, yet `rail_voltages` gives it 3.3 V. C59 then gets VD-004 "over-designed across 3V3 and PGND_3V3 (25V on 2.3V)", where the rail-to-rail derating used the wrong difference.
- **Fix direction:** add `(A|D|P|S)GND_<suffix>` to the shared rule. Consider also treating a net that a ground power symbol names, or sits on, as ground. Related: KH-726 (PGND in the net_analysis ground set).

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, partly fixed by c9fb4dbf, 49ce08f3, 2d4c5efd, 4a5f05cb, db551674):**
- **Fixed:** `is_ground_name` (`kicad_core/netnames.py:322-367`): `0V_<n>V` is no longer ground (`:353`); `COM` is ground only when a power symbol names it (`:338-339`; the context's ground rail set adds `COM` nets a `power_symbol` part sits on, `kicad_types.py:67-73`); `AVSS`, `DVSS`, `GROUND` join the exact set (`:345`); a ground token inside a longer name is ground (`_GROUND_TOKEN`, `:305`, `:367`: `AGND_CODEC`, `HEATER_GND_1`, `PGND_3V3`, `AGND_5V`, `DGND_1V8`); virtual grounds are neither ground nor power (`:341`; `VGND`, `VGND1`, `Virtual_Ground`; ruling P-G2). PCB ground domains keep the substring rule minus virtual grounds (`pcb/routing.py:970-974`, P-G4). Corpus: bluerobotics/ping-dev-kit `lumen2_3v3_buck` (both copies) `rail_voltages` `PGND_3V3` 3.3 → 0 and the C59 VD-004 "2.3V across 3V3 and PGND_3V3" is gone; OLIMEX ESP32-EVB (12 revisions) and ESP32-GATEWAY (5) LAN1 CG-AUD "5:1 signal-to-ground ratio" info is back (centre-tap pin `COM` no longer a ground pin).
- **Closed by ruling (R4):** `GND_LED`, `GND_BULB`, `LED_GND`, `GND_MOTOR` stay ground (designer-named switched returns).
- **Still open (v3.0.3, ruling P-G5):** `EARTH`, `CHASSIS`, `PE`, `Earth`, `Earth_Protective` are still not ground, and still power once a power symbol names them (probe at db551674). `230V_PE` reads 230 V in `rail_voltages` (jherkenhoff/STM `Supply-Board.sch`). Battery-negative domains (`BAT-`, `BATT-`) are still ground domains (the symptom's low-value MEDIUM finding; not addressed).

**Addendum 2026-11-13 (v3.0.2 Wave 11c, candidate db551674; slug KH-new-earth-ground-family, ruling P-G5 → v3.0.3):** still open after 11c's ground-name work: `is_ground_name` (`kicad_core/netnames.py:322-367`) is False for `Earth`, `EARTH`, `Earth_Protective`, `CHASSIS`, `PE` (also with a power symbol). `is_power_net_name` is True for them once a symbol names them. 521 schematic units / 198 repos in the candidate snaps carry one (`Earth` 430). EMC's `is_emc_ground_name` takes `earth` but not `chassis` (`emc/scripts/emc_rules.py:127-128`). Needs its own survey (protective earth vs signal ground) before it joins the shared rule.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; slug KH-new-ground-token-control-suffix):** control and sense signals read as ground. New in 11c through the token rule (`kicad_core/netnames.py:367`, `_GROUND_TOKEN` `:305`): `USB_GND_EN`, `GROUND_FAULT`, `AGND_SENSE` (False at 6138b126). Pre-existing: `/GNDDetect`, `GND_EN` (`:361` prefix rule) and `VSS_SW_EN` (`:364` `VSS*` prefix). Fix direction: drop a name whose last token is a control/sense word (`RAIL_SIGNAL_SUFFIXES`, `SENSE`, `DETECT`, `FAULT`) from every ground rule, as `is_power_net_name` already does for rails. 0 corpus findings per the product; budget expected empty.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; slug KH-new-0v-return-names):** the `0V_<n>V` exclusion (`kicad_core/netnames.py:351-353`) that stops `0V_10V` / `0V_32V` reading as ground also drops `0V_24V` and `0V_5V` (True at 6138b126, False now). On PLC boards these name the return of a 24 V / 5 V supply. A name rule cannot tell them from 0-10 V signals. Fix direction: read `0V_<n>V` as ground when a power symbol names it or a supply's ground pin sits on it. 0 corpus per the product.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; slug KH-new-virtual-ground-token-split):** the new virtual-ground exclusion splits names on `[_.\s]` only (`kicad_core/netnames.py:311`, used at `:319` / `:341`), so `HP-VGND` and `AUDIO{slash}VGND` (one token after unescaping) still read as ground through `endswith("GND")` (`:361`), while `HP_VGND` does not. Fix: split tokens on `-` and `/` too. 0 corpus per the product.

**Addendum 2026-11-13 (v3.0.2 Wave 11c gate, std lane, harness):** KH-726 (b2307f70) gives 0 V to every name `is_ground_name` accepts, so names that already read as ground now lose their name voltage in `rail_voltages` (98 keys on 28 names, e.g. `USB_GND` 5.0 → 0, `GND_12V_3` 12.0 → 0: correct). 40 keys on 13 names read as both power and ground (`12VGND`, `V2V_GND`, `24V_GND`, `5V_tvs_gnd`: domain grounds, correct). Two are wrong or doubtful: `+12V_F19_BKGND` (Hiawathaflow/Trabbi-schematic, 2 sheets) is a 12 V feed whose `BKGND` tail ("background") reads as ground at base and candidate alike, now 12.0 → 0 V; `GND_OR_5V` (5.0 → 0) names a jumper-selected net. Fix direction: a `+<voltage>` leading token should outrank a trailing `GND` substring that is not a ground token.

### KH-926: PCB decoupling: supply pins typed `input` / `output` / `bidirectional` lose their caps (DC-002 false errors)

**Severity:** MEDIUM (false HIGH DC-002 / DC-001 movement)
**File:** `skills/kicad/scripts/pcb/assembly.py:16-17` (`_SUPPLY_PIN_NAME`: VCC|VDD|VIN|AVDD|DVDD|PVDD|VDDA|VDDIO|VDDQ|VBAT[_n]|V+), `:74-92` (`_ic_signal_nets`: a pad typed in `IC_SIGNAL_PIN_TYPES` on a non-rail net, with no supply pin name, is a signal and its caps do not count); the schematic has a separate list, `skills/kicad/scripts/schematic/net_analysis.py:297-298` (`_SUPPLY_PIN_FULL_NAME`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-15-report.md` :70-101, :115-152; `L9B/final-fix-report.md` :74; `D/combined-ab/REPORT.md` :67)

**Symptom:** ruling 14a refined (9b T15) drops a cap whose only shared net the IC's own pad marks as a signal. The residue is supply pins that their library types as signal pins, on nets with no rail name:
- regulator / load-switch / boost `IN` / `OUT` / `INPUT` / `OUTPUT` pins: board 195 U7 TPS7A49 (pin 8 `IN`, C34 at 4.4 mm) and U9 L4931 get a new DC-002 error, 2 of the 29 added DC-002 on R;
- `VDEC` / `VBIAS`, LCD bias `V0-V3`, `USB1.VBUS` (TPS2051 `OUT` bidirectional), ADC inputs named `VIN`.

The task-15 fix round added the pin-name rescue, so MCP9700 / HX7027 / AV9173 / TP5410 (`VDD` / `VIn` / `VCC` typed input) now keep their caps. Those four, listed in the handoff, no longer reproduce by code read. Probe of the regex at `8c42799`: `IN`, `OUT`, `VDEC`, `VBIAS`, `AVCC`, `VCCA`, `VCCIO`, `VDD_IO`, `VDDD`, `VBUS`, `PVIN` do not match `_SUPPLY_PIN_NAME`. The schematic `_SUPPLY_PIN_FULL_NAME` matches `AVCC`, `VCCA`, `VCCIO`, `VDDD`, `VBUS` and `PVIN`, so the two lists differ.

**Fix direction / budget:** one supply-pin-name rule shared by PCB and schematic, with `AVCC`, `VCCA`, `VCCIO`, `VDD_IO`, `VDDD`; treat `IN`/`OUT` pins of a part the schematic classes as a regulator or load switch as supply pins. Output-changing: DC-001 / DC-002 / `decoupling_placement`. With KH-894 / KH-877; KH-937 is the same family.

### KH-927: touch pads are still typed `test_point`; a real TP with "touch" in its value on a non-TestPoint footprint is dropped

**Severity:** LOW (component type / TE-001 count edge case)
**File:** `skills/kicad/scripts/kicad_core/classify.py:12-20` (`is_touch_pad`: a touch marker in the value is enough unless the footprint names a test point), `:101` (`"TP": "test_point"` by reference prefix); consumers `skills/kicad/scripts/pcb/assembly.py:928-936`, `skills/kicad/scripts/schematic/system_analyses.py:1902-1907`, at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-13-report.md`; `D/surveys/survey-pcb.md` ask 6)

**Symptom:** 9b T13 keeps touch pads out of TE-001 / `test_coverage`, but a `TP`-referenced touch pad is still classified `test_point` in `components[]`. The other half is the reverse case. A real test point on a non-TestPoint footprint (e.g. a pogo pad) whose value contains "touch" / "capacitive" is classed a touch pad and dropped. None in the corpus. The FD-001 rider stays on KH-436.

**Fix direction / budget:** type a touch electrode (`is_touch_pad`) as its own component type at classification. Read the value marker only with a non-test-point footprint *and* a touch-like footprint or library. Small; measure the `components[].type` movement.

### KH-930: hot loop: a far nearest input cap gives a thin loop under 25 mm², the shoelace nets self-crossing lobes, and the buck loop is used for boost parts

**Severity:** MEDIUM (SW-003 false negatives; loop area is the graded quantity)
**File:** `skills/kicad/scripts/kicad_core/hotloop.py:50-57` (`polygon_area`: signed shoelace, `abs` at the end), `:60` (`polygon_loop_area` and the degenerate guard); `skills/kicad/scripts/pcb/assembly.py:795-870` (`_compute_switching_loop_areas`; `:824-826` excludes only ldo/linear/unknown/ic_with_internal_regulator…, so boost and inverting parts get the buck-shaped 6-pad loop), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9B/task-19-report.md` :52, :57, :62; `task-19-review.md` :86-105, :119)

**Symptom:**
- the nearest input cap far from the regulator, with pads near one line, gives a thin polygon under 25 mm²: 20 of 456 loops with reach > 20 mm (survey); Jin-Neuron TurtlePico U2 has reach 175 mm and 40.3 mm².
- the SW → inductor → ground leg folds back, the polygon crosses itself and the shoelace nets the lobes. Of the 26 records the guard marks degenerate on the slice, 25 cross themselves and none is collinear (task-19-review :86-87; the handoff's "all 26" is 25 in the review). 5 of the 26 have reach over 10 mm, where cancellation hides a far cap. The other 21 are compact loops marked "not estimated" (26/167 on the slice).
- a boost or inverting part's hot loop is on the output side, but it is measured as a buck.

**Fix direction / budget:** unsigned loop area (non-zero winding or union of lobes) instead of the netted shoelace; a reach-aware guard; a topology-specific loop for boost / inverting parts. Method change, needs a new A/B on the S3 board set. v3.0.2 (geom P4).

#### Addendum to KH-930 (soak run 11: boost hot loop)
**Added:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`
SW-003 on SacMap U2 / U3 (TPS61023, boost) reports "Hot loop … not estimated": the buck pad path is used for a boost part (symptom 3 above). A hand measurement through the output caps gives about 4–6 mm².

### KH-933: ES-001 gives ESD-path wording to surge TVS parts on power inputs

**Severity:** LOW (finding text; ES-001 on surge parts)
**File:** `skills/emc/scripts/emc_rules.py:3234` (`diode`-typed TVS accepted, 9c T3), `:3256-3277` (ES-001 text: "8kV ESD strike", "dI/dt = 37.5 GA/s" for every part), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/task-3-5-report.md` :10-13; `L9C/progress.md` Task 3)

**Symptom:** 36 of the 100 added ES rows are SMAJ / SMBJ surge TVS parts on power inputs (SMAJ58CA on OpenEFI, SMBJ16CA/26CA on 12 V, SMAJ24A on +24V). They get the connector-ESD distance and overshoot wording, which is not the part's job there.

**Fix direction / budget:** recognise surge TVS on a power input (series / package family, clamp net a rail) and either skip ES-001 or word it for surge. Output-changing: ES-001 count / text and EMC score on those boards.

### KH-934: ES-002 counts ground vias only, so a TVS whose ground pad sits on a same-side GND pour reads "no ground via"

**Severity:** MEDIUM (false HIGH ES-002)
**File:** `skills/emc/scripts/emc_rules.py:3283-3330` (ES-002: counts ground-net vias within 3 mm; zones are not read), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/task-3-5-report.md` :14)

**Symptom:** a TVS whose ground pad connects straight to a GND pour on its own layer, with no via within 3 mm, gets ES-002 "No ground via near ESD device" (HIGH).

**Fix direction / budget:** count a same-side ground zone fill under or touching the TVS ground pad as a low-inductance return (a fill / pad overlap test, as the copper analyses already do). Output-changing: ES-002 error/info and EMC score.

### KH-936: RP-001 / DP-003 stitching: any ground via counts, whatever the reference ground or via span; DP-003 on non-differential pairs

**Severity:** LOW (RP-001 / DP-003 false negatives and false positives)
**File:** `skills/emc/scripts/emc_rules.py:4133-4145` (`_ground_via_positions`: every via on any ground-named net), `:4163-4167` (`_via_stitched`: distance only, no layer span), `:2464`, `:2485-2491` (DP-003 uses the same set per net), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/task-6-report.md` :26; `L9C/task-6-review.md` :54, :63)

**Symptom:**
- an AGND via stitches a DGND-referenced pair or signal.
- a blind or buried ground via counts even when it does not span the signal via's layers (`via_positions[].layers` is available).
- DP-003 fires on schematic pairs that are not differential (`SUB-A+`, `BUTTON_MIN-`). That is a schematic pair-detector gap.
- grading is per net, so one pair can read N info and P warning (T 025 S_{in}1).

**Fix direction / budget:** match the via's ground net to the pair's reference plane net; require the via span to cover the signal transition; tighten the diff-pair detector's name rule. Output-changing: RP-001 / DP-003 under `--full`.

### KH-937: DC-002 where the IC's supply net is not power-named: PCB decoupling pairing drops the supply cap

**Severity:** MEDIUM (false HIGH DC-002)
**File:** `skills/kicad/scripts/pcb/assembly.py:74-92` (`_ic_signal_nets`), `:95-117` (`_nearby_decoupling_caps`: only caps sharing a non-ground net with the IC, less the signal nets); `skills/emc/scripts/emc_rules.py:759-786` (`check_missing_decoupling`), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/progress.md` Task 2 handoff item; slug proposed by the handoff draft, the ledger records it only as a HANDOFF ITEM)

**Symptom:** R board 195 U7 TPS7A49 `IN` with 10 µF C34 at 6.6 mm still gets DC-002. T board 70 TPS3808 `VDD` is on `/WATCHDOG/VDD` while its cap is on `3V3`. Partly reproduced by code read. The TPS7A49 case is the KH-926 cause: the `IN` pad is typed as a signal pin on a non-rail net and `IN` is not a supply pin name, so the cap is dropped (`D/combined-ab/REPORT.md` :67 says the same). The TPS3808 case has no shared net between IC and cap, so `_nearby_decoupling_caps` cannot pair them on any naming rule. The cause there is how the two nets are joined (a tie or a series part, not shown), not the name test. Not measured here.

**Fix direction / budget:** fold the TPS7A49 shape into KH-926; for the TPS3808 shape, pair through net-tie / zero-ohm conductors (`conductor_of`) before the shared-net test. Output-changing: DC-002 / DC-001.

### KH-938: shared `is_power_net_name` misses spaced voltage names, `PWR` / `POWER`, `V-`, `VMOT`

**Severity:** MEDIUM (shared predicate, 51+ consumers)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:119-200` (`is_power_net_name`); EMC works around it at `skills/emc/scripts/emc_rules.py:94-108` (`_is_power_or_ground`: shared OR the old local prefix rule less control/status suffixes), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/progress.md` Task 8 stop condition and ruling)

**Symptom:** probe at `8c42799`: `is_power_net_name` is False for `5V PCIE`, `3.3v from USB`, `5V Reference`, `5v OUT`, `PWR`, `POWER`, `V-`, `VMOT`; the EMC composed predicate is True for all of them. 9c T8 hit its stop condition (~10/66 = 15 % false adds) with the shared predicate and composed the EMC predicate instead of widening the shared one.

**Fix direction / budget:** widen the shared predicate (spaced `<n>V <word>`, `PWR`/`POWER`, `V-`, `VMOT`), then retire the EMC composition. Needs its own gate (every consumer moves). Same family as KH-925 / KH-939.

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, partly fixed by 566f0ec4):**
- **Fixed:** `V-` and `VMOT` join the exact rail set (`kicad_core/netnames.py:215`). Probe base → candidate: `V-`, `VMOT`, `/x/V-` False → True; `VMOT_SENSE`, `VMOT1` stay False.
- **Still open (v3.0.3, rulings R-P1 / R-P2):** `PWR`, `POWER` and the spaced names (`5V PCIE`, `3.3v from USB`, `5v OUT`) are still False in the shared predicate and True only through the EMC composition `_is_power_or_ground` (`skills/emc/scripts/emc_rules.py:94-108`), which stays until the spaced-name widening. `5V Reference` is a reference node, not a rail (KH-724 class), so the widening should not take it.

### KH-942: SU-003 tests layer names and KiCad layer types, not the fill planes

**Severity:** LOW (SU-003 rarely fires)
**File:** `skills/emc/scripts/emc_rules.py:1731-1760` (`check_stackup` interplane-capacitance loop: `t1 == 'power' and is_emc_ground_name(l2['name'])`, with `l*['name']` the copper layer name), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/final-review-9c.md`)

**Symptom:** SU-003 needs one layer typed `power` and the adjacent layer *named* like ground (`GND`), so `In1.Cu` / `In2.Cu` planes never pair. 9c T7 made SU-001 / CK-001 / DP-004 judge planes by zone fill (`_reference_plane_layers`), but SU-003 was left as it was.

**Fix direction / budget:** pair adjacent plane layers from `_reference_plane_layers` with their fill nets (ground vs power). Output-changing: SU-003 additions on 4+ layer boards.

### KH-943: DC-002 matches any `U<digit>` / `IC<digit>` reference, including non-IC parts

**Severity:** LOW (false HIGH DC-002 on mis-referenced parts)
**File:** `skills/emc/scripts/emc_rules.py:769-780` (`check_missing_decoupling`: `re.match(r'^(U|IC)\d', ref)` with a value-word exemption list; no component-type test), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`D/combined-ab/REPORT.md` :68)

**Symptom:** board 063 U1 `JumperPad` (jumper footprint, no power pin) is newly flagged on R. A signal-net cap used to suppress it, and 9b T15 dropped that cap. U2 `Core` on the same board was already flagged in base. A pre-existing class, now wider.

**Fix direction / budget:** take the schematic component type (`ic`) when the schematic is given, and otherwise require a footprint pad whose net or pin name is a supply. Output-changing: DC-002 removals.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 93a899e3):** fixed: With a schematic, DC-002 skips a U/IC reference the schematic types as something other than `ic` or `oscillator` (`emc_rules.py:772-785`). Still open: With no schematic, or a part the schematic does not list, the type is None and the part is still checked (`emc_rules.py:785`); the 'require a supply pad' half for PCB-only runs is not done -> v3.0.3 (handoff). Board 063 U1 `JumperPad` is gone only if its schematic types it non-IC; not verified harness-side. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-957: PM-001 ignores the project's per-violation DRC exclusions; a pair colliding on both courtyard layers reports the first layer in file order

**Severity:** LOW (warnings the designer already waived; tie order has 0 corpus occurrences so far)
**File:** `skills/kicad/scripts/pcb/assembly.py:347-431` (`analyze_placement` pair loop and `reported` dedupe), `skills/kicad/scripts/pcb/pipeline.py:501-503` (only `rule_severities` ignore is honoured) at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (pre-existing, exposed by Wave 10b)

**Symptom:** The handoff calls these grazing overlaps below a DRC tolerance. They are not. On calvin-mcd/vdf-fullsized-keybored (`fullsized keybored 3v3.kicad_pcb`), the candidate reports 18 PM-001, 17 of them between `TestPoint_THTPad_D1.5mm` J parts at 0.053-0.054 mm². The courtyards are circles of r = 1.25 mm on 2.381 mm centres, so they overlap by 0.119 mm, twelve times KiCad's 0.01 mm allowance. The project's `board.design_settings.drc_exclusions` lists exactly 10 of those pairs as `courtyards_overlap` (J31-J29, J29-J27, J23-J21, J30-J28, J28-J26, J26-J24, J24-J22, J10-J4, J11-J7, J12-J8). Those are the 10 that DRC leaves out; the other 7 J-J pairs have the same geometry and DRC reports them. The analyzer reads `rule_severities` (a whole check set to ignore) but never reads `drc_exclusions`. At `e60d03b5` the 50-pair cap hid these pairs. Second point: the pair dedupe is keyed on `(id(fp_a), id(fp_b))`, and `_courtyard_sides` keeps file order. So when a pair collides on both F.CrtYd and B.CrtYd, `layer`, `overlap_mm2` and severity come from whichever layer comes first in the file, not from the larger overlap.

**Fix direction / budget:** Drop PM-001 pairs whose `courtyards_overlap|…|uuid_a|uuid_b` entry appears in `drc_exclusions`, or keep them and tag them excluded. Either way it should work for every check type, not only PM-001. For a pair that collides on both layers, report the larger overlap. Standard lane: PM-001 removals on boards with exclusions, plus rollups. Check how many corpus `.kicad_pro` files carry `courtyards_overlap` exclusions before budgeting.

### KH-958: duplicated `fp_rect`/`fp_poly` courtyard outlines are silently de-duplicated; KiCad flags `malformed_courtyard`

**Severity:** LOW (a DRC finding is missed; the courtyard stays in PM-001, where KiCad drops it)
**File:** `skills/kicad/scripts/pcb/reader.py:700-711` (`_distinct_polys`) and `:784` (per side), where `:664-680` raises the diagnostic only for a twice-drawn segment, at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (pre-existing; the merged-list dedupe was already there at `e60d03b5`)

**Symptom:** A footprint that draws the same closed outline twice on one courtyard layer (two identical `fp_rect`, or two identical `fp_poly`) is reduced to one polygon, with no `diagnostics` record. kicad-cli 10.0.8 DRC on a two-footprint synthetic board (one of each case) reports `malformed_courtyard` on both footprints. Both analyzers (`e60d03b5` and `2abc8496`) report `diagnostics: []` and a normal courtyard. KiCad also leaves a malformed courtyard out of its overlap test, so PM-001 can report pairs that DRC does not.

**Fix direction / budget:** Treat a repeated closed outline on one side like a repeated segment: record the diagnostic and drop that side. Do it together with KH-766, so only the bad side goes. Standard lane: `diagnostics` additions and PM-001 removals on the affected footprints. The corpus count is unmeasured.

### KH-959: EMC net classifiers misgrade rails on RP-001: `/VUSB` and `/brdaddr*` read as high-speed, `vN`/`V_*` rails read as signals

**Severity:** MEDIUM (false error-grade RP-001 on power rails; the shared classifiers also feed other rules)
**File:** `skills/emc/scripts/emc_rules.py:74-108` (`_is_power_or_ground_prefix`, `_is_power_or_ground`), `:191-200` (`_is_high_speed_net`, substring match), `:4255` (RP-001 grades HIGH) at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (classifiers pre-existing and unchanged; exposed by the new `:4210` gate, under which RP-001 now runs on boards with no ground via and ≥ 2 ground-filled layers)

**Symptom:** At both `e60d03b5` and `2abc8496`, `_is_power_or_ground` returns False for `/VUSB`, `/V5`, `V_ESC` and `Fuse_V_Bat`. The prefix list has no `vusb`, and the `^[+-]?\d+\.?\d*v` pattern needs a leading digit. Because `_is_high_speed_net` matches the substrings `usb` and `ddr`, it returns True for `/VUSB` and `/brdaddr0`, which therefore get HIGH (error). Per the product's sample, about 5 of the 260 new RP-001 land on power rails. That count was not re-measured here.

**Fix direction / budget:** Add `vusb` and a `vN` / `v<digits>` rail rule to the power prefix set. Match high-speed patterns on tokens, not substrings (`usb` as a word or a `USB_D±` form, `ddr` not inside `addr`). `_is_high_speed_net` is also used at `:501` and `:2685`, so budget those rules as well. Standard and full-chain EMC: RP-001 removals and severity drops. Expect a smaller tail on the other two callers.

### KH-960: VS-001 disagrees between the via-list and count-only branches; a zero-via board fires in both

**Severity:** LOW (heuristic finding; standard and `--full` disagree on the same board)
**File:** `skills/emc/scripts/emc_rules.py:1507-1527` (`check_via_stitching`: `if via_list:` ground-via branch vs `else` count branch) at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (new in Wave 10b: the via-list early return at `:1521-1522`)

**Symptom:** Calling `check_via_stitching` directly on a 100 × 100 mm board with one non-ground via and no ground fill returns nothing with the via list (`--full`) and VS-001 with the count only (standard). At `e60d03b5`, both returned VS-001. The handoff's "zero-via" wording is off. A board with no vias at all has an empty list, so it takes the count branch even under `--full`, and it fires VS-001 ("0 vias … no vias detected") in both modes at both SHAs. The new silence only covers boards that have vias but no ground vias.

**Fix direction / budget:** Make one early return for both branches: no ground via (or no via at all) and no ground fill means nothing to stitch. Test `'vias' in vias` rather than truthiness, so an empty list counts as a list. Standard lane: VS-001 removals on boards with no ground fill. Full-chain: removals on zero-via boards. The 23 "rule present" locks from this wave's relock will move again.

### KH-963: power-budget LDO block has no same-sign guard; an inverting buck read as an LDO gets a dropout

**Severity:** LOW (power_mW is 0 on the known case; the root cause is an upstream LDO misclassification)
**File:** `skills/kicad/scripts/schematic/system_analyses.py:1578-1589` (`analyze_power_budget`: `abs(v_in) > abs(v_out)` only), compared with `skills/kicad/scripts/signal_detectors.py:2331` (`vin * vout > 0` guard) at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (pre-existing: at `e60d03b5` the block was already there with dropout 20.1 V; Wave 10b's `abs()` changed it to 10.1 V)

**Symptom:** horychen's U2 (LM2675M-5.0, ×5 units) is a buck used inverting, +15V1 in and −5 V out. The regulator detector classifies it as `LDO`. `_estimate_regulator_dissipation` now skips it, because the rails differ in sign. `analyze_power_budget` still writes `ldo_dissipation` with dropout 10.1 V, which means nothing for this part. The two LDO paths disagree on the same regulator.

**Fix direction / budget:** Add the same-sign guard to the power-budget block. Separately, stop classifying a fixed-suffix switcher (LM2675) as an LDO. Standard lane: `ldo_dissipation` removed on the 5 horychen units, a `missing` delta outside this wave's value-only dropout class.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by b3a0c596):** fixed: the power-budget LDO block has the regulator detector's same-sign guard (`system_analyses.py:1614-1617`). Still open: LM2675 (a fixed-suffix switcher) is still classified as an LDO: it is missing from `_KNOWN_FREQS` (`parts.py:324`), so it falls to `signal_detectors.py:2017`. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-964: `ctx.is_ground` treats `VSS*` as ground, so an EN on a `VSS`-named negative rail reads `tied_to_ground`

**Severity:** LOW (0 corpus occurrences per the product census)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:281-283` (`is_ground_name`: any `VSS*`), `skills/kicad/scripts/schematic/system_analyses.py:1664-1670` (ground test now ahead of the power test) at `2abc8496`
**Discovered:** 2026-11-05, product 3.0.x Wave 10b handoff (the `VSS*` rule is pre-existing; the new label comes from Wave 10b's reordering)

**Symptom:** Partly confirmed. `is_ground_name` is True for `VSS`, `VSSA` and `VSS_NEG`, the same at both SHAs. It is False for `VEE`, so the `VEE` half of the claim does not hold for `ctx.is_ground`; only the EMC `is_emc_ground_name` accepts `VEE`. `VSS` is also a power name. At `e60d03b5` the power test ran first, so an EN on `VSS` read `always_on`. At `2abc8496` the ground test runs first, so it reads `tied_to_ground`, or `always_on` for an active-low EN. Where `VSS` is the negative supply of a bipolar design, `tied_to_ground` is wrong. The same `VSS*` rule already costs bkm-129x's LM2990 its `VSSA` output rail (named in the rails survey).

**Gate measurement (Wave 10b gate):** not 0 on the corpus. loxodes/vna `breakouts/bias_controller` (root sheet and `power` sub-sheet, standard and full-chain): U601's EN (−6 V regulator) sits on the hierarchical label `VSS_SW_EN`, a switch enable driven from another sheet; `power_sequencing` `en_source` moves `disabled` → `tied_to_ground` and `power_tree` `enable_type` `floating` / `gpio_controlled` → `tied_to_ground`. These are the gate's only 2 residual units (7 deltas per lane). v3.0.1 handles this corpus case with a narrow guard (product ruling 2026-11-06: an EN on a `VSS`-prefixed net keeps the pre-10b order at both EN classification sites, `is_ground_name` unchanged, landed in the 10c range); this entry stays open for v3.0.2 for the general rule (`VSS*` as a negative rail vs ground).

**Fix direction / budget:** Have `VSS*` count as ground only when no negative-regulator output or negative-voltage evidence names it. Otherwise classify it as a negative rail. Standard lane: `power_sequencing` `en_source` values. Expected 0 per the census, so mostly a fixture test.

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, partly fixed by 6bf0af2b, 27bf1462, 3ea7f96f):**
- **Fixed (ruling P-G3, narrow form):** `vss_supply_rail_nets` (`kicad_types.py:231-250`) marks a ground-named VSS net that a regulator `power_out` pin drives when that part also has a pin on another ground. On those nets the regulator keeps its `output_rail` (`signal_detectors.py:2081`, `:2119`), the rail map takes no positive estimate and no name voltage (`schematic/pipeline.py:342`, `:353`, `:365`), and DO-DET does not report missing output decoupling (`signal_detectors.py:3939`). Corpus: bkm-129x IC050 LM2990SX-5.0 `output_rail` None → `VSSA`, and `rail_voltages` gets no `VSSA` key (it still carries `estimated_vout` +5.0: handoff slug negative-fixed-suffix).
- **Still open:** `ctx.is_ground` (`kicad_types.py:171-172`) is still True on these nets, so every other ground consumer still reads a negative VSS supply as 0 V; the decoupling detector counts none of its capacitors (comment at `signal_detectors.py:3937-3938`). The EN sites (`schematic/system_analyses.py:1700`, `domain_detectors.py:5368`) still use the 10c name-only guard (`not is_vss_name(en_net)`), so an EN tied to a VSS that really is 0 V reads `always_on` / `disabled`, never `tied_to_ground`. Negative-voltage evidence other than a regulator output (a negative power symbol, a config override) is not used.

### KH-967: rails named `<n>V<n>_N` read as positive voltages; an op-amp on `4V5_P` / `4V5_N` gets V− == V+ and a single-supply bench

**Severity:** LOW (SPICE bench topology and rail voltages wrong on suffix-named split rails)
**File:** `skills/spice/scripts/spice_templates.py:844-850` (`_leaf_voltage`) and `:863-880` (`_infer_negative_rail`: only a `-` / `NEG` / `VNEG` / `V-` prefix or a named negative rail reads negative) at `2abc8496`
**Discovered:** 2026-11-06, product ruling on the Wave 10b gate (pre-existing; the 10b `vee_repaired` note now states it)

**Symptom:** `_leaf_voltage('4V5_N')` and `_leaf_voltage('6V0_N')` return +4.5 / +6.0, the same as their `_P` twins, and `_infer_negative_rail` returns None for both. starshipraider akl-av1 U5 (V+ `4V5_P`, V− `4V5_N`) and BLONDEL U18 (VDD `6V0_P`, VSS `6V0_N`) therefore read V− == V+, the sanity check falls back to single-supply, and the bench runs on 0 V / +V. The schematic side agrees with the misread: akl-av1 `rail_voltages` has `4V5_N: 4.484` (positive).

**Fix direction / budget:** read a `_N` / `N` / `NEG` suffix after a voltage (`4V5_N`, `3V3N`, `5V_NEG`) as negative in the SPICE rail reader, and check the schematic rail-name parser and regulator estimate for the same suffix. Output-changing (spice-offline op-amp benches, schematic `rail_voltages`), v3.0.2.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 21f27d74):** fixed: SPICE side: `spice_templates.py:786` and `:798-800` read a `<n>V<n>_N` leaf as negative when its `<n>V<n>_P` twin is in the design; A/B removes the `vee_repaired` notes on akl-av1 U5 and BLONDEL U18. Without a twin `1V5_N` stays positive (product test). Still open: Schematic half: `rail_voltages` still reads `4V5_N` as +4.484 -> Wave 11c (handoff). `_leaf_voltage('4V5_N')` itself still returns +4.5 and `_infer_negative_rail` returns None (the flip is local to `_infer_opamp_rails`); the fix direction's other spellings (`3V3N`, `5V_NEG`) are not read as negative (`spice_templates.py:798` matches only `<n>V<n>_N`). The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

**Addendum 2026-11-13 (v3.0.2 Wave 11c handoff candidate, verified at `db551674`, schematic half fixed by 4183f710 in the twin form):**
- **Fixed:** `negative_split_rails` (`kicad_core/netnames.py:378-392`) marks a `<n>V<n>_N` leaf whose `<n>V<n>_P` twin is in the design. The rail map negates its name voltage (`schematic/pipeline.py:363`, `:369-370`), `statistics.power_rails[].voltage` is negated too (`schematic/bom_stats.py:131`, `:139`; ruling C-R6), and a regulator whose output is such a net is `inverting` (`signal_detectors.py:2072`). akl-av1 (psu and root sheets): U1 LM27761 `estimated_vout` +4.484 → −4.484, `rail_voltages` `4V5_N` → −4.484, `power_rails` `4V5_N` → −4.5.
- **Still open:** names outside the twin form stay positive: MAXWELL `5V0_N` (LM27761 U68, twin named `5V0`) +4.837 / +5.0 on 8 sheets; KiwiSDR `5V_NEG` beside `5V_POS` +5.0 (2 units); `12V_N`-style leaves (no digit after V) and `3V3N` are not matched by `(\d+V\d+)_N`. SPICE `_leaf_voltage` / `_infer_negative_rail` (`spice_templates.py:856`, `:875`) still read `4V5_N` as +4.5 / None outside `_infer_opamp_rails`. The handoff's negative-rail-taps slug (`7V0_N_1`, `V12N`/`V12P`) covers only part of this.

### KH-968: keepouts / rule areas inside a library footprint are never read — KO-001 and the antenna checks see only board-level zones

**Severity:** MEDIUM (false negative that turns into wrong advice: two earlier soak reviews told the user to add an ESP32 antenna keepout that the module footprint already carries)
**File:** `skills/kicad/scripts/pcb/reader.py:1261` (`extract_zones`: `find_all(root, "zone")`, direct children of the board only; `kicad_core/sexp.py:227` `find_all` is not recursive) and `:1432` (`_extract_keepout_zones` filters that list); `pcb/assembly.py:1216` (`analyze_keepout_violations` gets nothing else), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** the ESP32-S3-WROOM-1 footprint defines its antenna keepout as a footprint zone on both copper layers; KiCad DRC enforces it (0 violations), while the analyzer reports no keepout near the module. No other `"zone"` reader exists in the PCB analyzer.

**Fix direction / budget:** read `(zone …)` children of each `(footprint …)`, transform the outline by the footprint position, rotation and side (flip the layer set for back-side parts), tag the entry with the owning reference, and feed KO-001 and the antenna / RF checks. Output-changing: new `keepout_zones` entries and KO-001 findings on boards whose footprints carry rule areas (measure the corpus count first). v3.0.2 or later. Belongs with KH-972.

### KH-969: GP-001 skips a net once its coverage is ≥ 95 %, so only some of the nets crossing one gap are reported, and the finding gives no gap location

**Severity:** LOW (incomplete and hard-to-act-on finding)
**File:** `skills/emc/scripts/emc_rules.py:509` (`elif coverage < 95` … `else: continue`) and `:516` (finding fields: `signal_net`, `coverage_pct`, `trace_mm`, no coordinates), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** five nets cross the same unpoured patch under U1; GP-001 reports three. By code read the threshold is per net and by percentage, so a net with long routing elsewhere passes 95 % with the same crossing (the soak's "unexplained" two). The finding names no gap, so the user cannot tell that the three findings are one void.

**Fix direction / budget:** add the gap location (x, y, layer, and the uncovered length) to the finding, and group the nets that cross the same gap (or add a per-gap finding listing every crossing net). Output-changing (GP-001 fields; GP-001 count if grouping changes the threshold). v3.0.2 or later.

### KH-971: XV-004 skips a part whose MPN is blank on either side and never compares distributor part numbers

**Severity:** LOW (the parity check is silent on the cases most likely to be wrong at assembly)
**File:** `skills/kicad/scripts/cross_analysis.py:670` (`if not sch_mpn or not pcb_mpn: continue` in `check_mpn_parity`, :656), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** on SacMap 14 footprints have no MPN; they are skipped without a count or a finding. F1's PCB DigiKey PN `F2084CT-ND` does not resolve, and distributor PNs are not compared between schematic and PCB at all. (XV-004 itself works: it caught Q1–Q3 BSS138 vs BSS138LT1G, the KH-426 case.)

**Fix direction / budget:** report as their own sub-cases (a) MPN blank on the PCB but set on the symbol (or the reverse), (b) distributor PN differs between symbol and footprint; keep (c) the both-set mismatch as today. Resolving a PN online belongs to the BOM / lifecycle tools, not here. Output-changing (new XV-004 sub-case findings on corpus boards with blank footprint MPNs; measure first). v3.0.2 or later.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 1f31409f):** fixed: `cross_analysis.py:757`, `:772-773` count pairs with a blank MPN on either side; `main` prints `XV-004: N paired part(s) not compared ...` to stderr (`:1443`); SKILL.md:242 says XV-004 compares where both sides carry one. Still open: Sub-case (a) is only a stderr line; there is no JSON count or finding (the JSON field is scheduled for 3.1, ruling F1 P5). Sub-case (b), comparing distributor part numbers between symbol and footprint, is not done and is not scheduled anywhere: `check_mpn_parity` (`cross_analysis.py:740-776`) compares MPN only. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-972: silent capability loss is not listed in `diagnostics[]` — a distrusted extraction, an unread footprint keepout, a part skipped by a check

**Severity:** LOW (umbrella; report trust: the soak meta report's top trust item)
**File:** several producers at `7d9d4d9f`: `datasheet_types/cache_reader.py` (`lookup` marks `pdf_missing` with no record), `pcb/reader.py` (KH-968), `cross_analysis.py:670` (KH-971 skips), lifecycle (KH-896 / KH-474)
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** each loss above changes what the review can claim, but nothing in the output says it happened; the reviewer reads "no finding" as "checked and fine".

**Fix direction / budget:** one diagnostic per lost capability (code, affected refs / MPNs, reason), emitted where the loss happens. Group the fixes: KH-433 + KH-905 (extraction distrust), KH-968 (footprint keepouts), KH-971 (skipped parts), KH-896 / KH-474 (lifecycle sources). Additive `diagnostics` entries; corpus effect depends on the member fixes. v3.0.2 or later.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, verified at `db551674`):** KO-001 now skips a footprint with no readable courtyard on the side the area covers (ruling K-R1, as KiCad does), and leaves nothing in `diagnostics[]` for it (`pcb/assembly.py:1229-1247`). Same silent-capability class.

### KH-973: `diff_analysis.py` grades an analyzer-version change on an unchanged design as "breaking", and has no diff for `gerber` or `cross_analysis`

**Severity:** LOW (tool output only)
**File:** `skills/kicad/scripts/diff_analysis.py:505-515` (`diff_funcs` covers schematic / pcb / emc / spice / thermal; any other type prints "no diff function" and returns 1); neither `diff_analysis.py` nor `diff_engine.py` reads `inputs.source_hashes` or the generator version before `classify_regressions`, at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** run 11 against run 10 (same design files): the diff reports "breaking, 3 regressions" when the ERC list realigned with KiCad in v3.0.1. `gerber.json` and `cross_analysis.json` exit rc 1.

**Fix direction / budget:** when both sides' `inputs.source_hashes` match and the generator version differs, say "analyzer change, design unchanged" and do not grade the delta as design breakage; add gerber and cross_analysis diff functions (or exit 0 with a "not supported" note). Tool only, no corpus output change. v3.0.2 or later.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev b8b0561e fix(diff): say when the design files are unchanged and the changes come from the analyzer (v3.0.2 Wave 11a Task 29, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `diff_analysis.py` `_same_design` compares the `source_hashes` values and `config_hash` and adds `ANALYZER_ONLY_NOTE` to the text output (in JSON mode, to stderr).
- **Left open:** the delta is still graded by `classify_regressions`, so "breaking" can still be reported. `gerber` and `cross_analysis` still get "no diff function" with rc 1 (:528-537), frozen as declared.

### KH-613: EMC PDN impedance drops phase (scalar `|Z|` summed in parallel), so no anti-resonance can exceed the best single cap; PD-003 never runs because of two consumer key mismatches; trace inductance is ×1.82; PD-004 picks the wrong worst source

**Severity:** HIGH (default EMC path; PD-001 false negatives on every multi-cap rail)
**File:** `skills/emc/scripts/emc_formulas.py:578-591` (`cap_impedance_at_freq` returns scalar `sqrt(ESR²+X²)`), `:644-646` (`parallel_cap_impedance` sums `1/|Z_i|`), `:1229` / `:1245` (distributed path, same); `:1107` (`'net_name' in nl`; producer `pcb/routing.py:785` emits `net`), `:978` (`entry['rail_net']`; DC-DET producer `signal_detectors.py:1227` emits `rail`); `:461-468` (`trace_inductance_nh_per_mm`); `emc_rules.py:3473-3490` (default analytic sweep), `:3697` (PD-003 skip), `:3586` (PD-002 `elif peaks` unreachable), `:3795-3800` (PD-004 worst source)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F1, sk/R1-F2, sk/R1-F8; spot checks R1 #1 and register PD-002)

**Symptom:** (1) 1 µF + 10 nF, 1 nH, 10 mΩ: true complex peak 2.433 Ω @ 35.73 MHz; the code's 1–100 MHz max is 0.251 Ω and `find_anti_resonances(sweep, 0.33)` → `[]` — PD-001 false negative. (2) `enrich_power_tree_with_pcb` keys on `net_name`, the producer emits `net` → trace R=L=0 and `check_pdn_distributed` skips (`:3697`), so PD-003 can never fire (with `net_name`: R 0.082 Ω, L 33 nH); `build_power_tree` reads `rail_net`, the producer emits `rail` → no cap is ever `ic_decoupling`. (3) L = Z0/v uses Z0_air with c/√3.3 → 0.5416 nH/mm instead of 0.2981 (×1.82); dead today behind (2). (4) PD-004 compares `i_trans > total_reflected - i_trans` (running sum, not max): sources 0.3/0.4/0.5 A pick #2 and report its frequency with the total current. PD-002's `elif peaks` branch is unreachable.

**Fix direction / budget:** complex impedance in both sweeps; consumer reads `net` / `rail` (no producer key renamed); Z0_air/c; track max current in PD-004; remove or fix the dead PD-002 branch. Budget: PD-001/PD-002/PD-004 presence, peak values and risk score move; **PD-003 appears for the first time** — budget it separately and validate on a single-source rail first (size first, `--full` boards). Related: KH-478 (distributed SPICE helper with no caller) waits on ruling: keep or retire it. Harness `test_kh377_pd001.py` mocks the peak list, not the math.

**2026-11-08 (v3.0.2 Wave 11b-2, M2 / survey E9):** the key bug now has a product test pinned to the wrong key. `tools/tests/test_copper_thickness_per_layer.py:31-32` feeds `net_lengths` entries with `net_name`, which the PCB producer never writes (`pcb/routing.py:809` `analyze_net_lengths` emits `net`, `:938`). The consumer still keys on it (`emc_formulas.py:1086-1088`). The same file's `SpiceParasitics` test uses `net` (`:52`). When the consumer reads `net`, update `PowerTreeEnrichment._r`. KH-979's per-layer copper code is dead on real output until then (survey E9).

### KH-609: EMC reads `pads` from PCB footprints that the PCB analyzer always strips, so the IO-001 schematic fallback never clears, test-plan protocols are always `unknown`, and BE-003 is unfirable

**Severity:** HIGH (default EMC path, every board)
**File:** `skills/emc/scripts/emc_rules.py:2592`, `:844`, `:4143` (iterate `conn.get('pads', [])`); producer `skills/kicad/scripts/pcb/presentation.py:156` (strips `pads` unconditionally, leaves `pad_nets` `{num: {net, pin}}`); BE-003 `:2592-2614`; leaked loop variable `:4160`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R1-F3)

**Symptom:** the three consumers see no pads. (1) The IO-001 schematic-protection fallback (`:842-854`) can never clear, so a connector whose TVS sits >25 mm away gets a false IO-001. (2) `test_plan.interface_risks[].protocol` is always `unknown`. (3) BE-003 frequency stays 100 MHz. Independently BE-003 cannot fire: max `avg_spacing` = sqrt(π·100) = 17.72 mm (1 via) vs `2·λ/20` = 142.9 mm at 100 MHz (εr 4.4); zero vias → `continue` (`:2614`). Even after a pads fix a 1 GHz knee gives a 14.3 mm limit that fires only with exactly 1 via.

**Fix direction / budget:** read `pad_nets[*].net` in the three consumers. Budget: IO-001 count and `interface_risks` protocol/risk_score move (size first: EMC units with IO-001 and a schematic-side protection part). The BE-003 half waits on ruling: the BE-003 density model and the zero-ground-via policy (also RP-001 `:3903`, ES-002 `:3010`) — without it BE-003 stays silent.

### KH-606: `datasheet_verify` cannot find any extraction written by `datasheet_extract_cache` (hashed file names and manifest keys), and reads quality from a `meta` key no producer writes

**Severity:** HIGH (the verifier runs on every schematic analysis; all three verifier families skip silently)
**File:** `skills/datasheets/scripts/datasheet_verify.py:40` (name sanitiser keeps `.-`, no hash), `:43` (direct `<mpn>.json` read), `:62` (manifest key compared to the unhashed name), `:195`, `:210` (`"meta"`); writer `datasheet_extract_cache.py:152-154` (`_sanitize_mpn` = `[^A-Za-z0-9_]`→`_` + `_<md5[:6]>`), `:293-294`, `:315`, `:304`, `:322` (`extraction_metadata`); caller `schematic/pipeline.py:1474-1484`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R3-F1, sk/R3-F10)

**Symptom:** `cache_extraction(d, 'LM2596-ADJ', …)` writes `LM2596_ADJ_d61933.json` and a manifest key with the hash; `_load_extraction` looks for `LM2596-ADJ.json` / an unhashed key → `{}`, while the cache's own `get_cached_extraction` finds it. Every legacy-cache verifier family skips and `ics_with_extractions` undercounts, though `kicad/SKILL.md:479` tells the agent to cache via `datasheet_extract_cache` (and names `datasheets/extracted/<MPN>.json`, which the writer never emits). Separately, `:195` / `:210` read `meta`, which no producer in `skills/` writes (the writer and `datasheet_features.py:92` use `extraction_metadata`), so a low legacy score never yields `extraction_quality_low`.

**Fix direction / budget:** resolve through the manifest's `mpn` value or the cache manager's reader, keeping the direct-file path as a fallback; read `extraction_metadata`; fix the SKILL.md:479 filename. Budget: the schematic envelope's `datasheet_verification` gains findings on legacy caches — expected ≈0 corpus-wide (round-8 pre-scan: 0 units carry `datasheet_verification`); harness to confirm.

**Addendum 2026-10-31 (3.0.x Wave 5, candidate `698116c`):** fixed in 3.0.x Wave 5 (`740d2b6`, `5728851`): the verifier matches legacy manifest entries by their `mpn` value, reads cache-manager (hashed) names, accepts only leaf `file` names, ignores non-object files, refuses symlinked caches and reads `extraction_metadata` (fallback `meta`); `kicad/SKILL.md:479` and `references/datasheet-verification.md` name the cache manager's files. The multi-unit merge it needed is KH-781. The handoff lists this entry as fixed with a note; kept open for the note: `datasheet_verify._v1_view` passes v2 pin types through unchanged (latent). Close when that is ruled or fixed.

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

### KH-594: cross_verify and DA-001 ignore `on_board`, so a normal DNP part with a footprint warns, and an excluded-from-board part is expected on the PCB

**Severity:** MEDIUM (cross_verify / cross_analysis on any design with DNP parts)
**File:** `skills/kicad/scripts/cross_verify.py:121-123,155-157,181-186,130-134` (PCB `dnp`, `pcb/reader.py:461`, discarded); `skills/kicad/scripts/cross_analysis.py:425-430`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F10)

**Symptom:** in KiCad, DNP keeps the footprint and "exclude from board" (`on_board` no) omits it. The schematic emits `on_board` on 15,712 of 15,712 sampled components, 50 of them false. Neither builder reads it. cross_verify warns whenever a DNP ref has a footprint, which is the normal KiCad case.

**Fix direction / budget:** key PCB-presence expectations on `on_board`, and use the PCB `dnp` flag for the DNP comparison. Budget: cross_verify warnings disappear on DNP designs, and cross_analysis findings may move on `on_board: false` parts (size first). Waits on ruling: whether cross_verify is maintained or retired.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 92c7e36b):** fixed: DA-001 skips DNP and `on_board: false` ICs (`cross_analysis.py:485-486`). Still open: cross_verify still reads no `on_board` and no PCB `dnp` flag: it warns on every DNP ref that has a footprint (`cross_verify.py:118-129`, `:159`, `:195-200`). Scheduled for v3.0.3 (ruling F1 P6). DNP decoupling caps counted by DA-001 also go to v3.0.3 (F1 P7). The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

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

**Addendum 2026-10-31 (3.0.x Wave 5, candidate `698116c`):** narrowed. Fixed in 3.0.x Wave 5: Excellon route-mode slots count one hole each (`59f9184`, KH-786, which does not name KH-592); arcs and full circles count their full sweep in extents (`0c6a506`, KH-484). Still open (handoff residue): unitless-M72 inch drill files read as mm (9 newly readable `.xln` + 47 existing `.drl` / `.TXT`); modal route continuation after M15 (1 Altium file); macro-aperture Gerber drill holes; no diagnostic for an unreadable `.drl`; FIFO `*.gbr` blocks; `%FST` trailing zeros in extents. Not named by the handoff and still present at `698116c`: the leading-dot tool form (`T(\d+)C(\d+\.?\d*)` at `analyze_gerbers.py:649` misses `T1C.04`), LZ decoding, the G85 end point in extents.

**Addendum 2026-11-01 (3.0.x Wave 6, candidate `c0a8a62`):** `skills/kicad/references/gerber-parsing.md:377` now carries one sentence on the analyzer's residue (ruling W6-4): "The analyzer's drill reader misreads integer coordinates in `LZ` files (hole positions come out wrongly scaled); hand-decode those files. Hole counts and tool sizes are unaffected." (`1921308`, tagged KH-637). Remove it when this entry's LZ fix lands. Correction to the handoff: the doc sentence is about LZ decoding; no doc line mentions the unitless-M72 inch residue.

### KH-590: PCB reader gaps on KiCad 9/10 formats — numeric-only net names collide with net IDs (the track is dropped), and custom padstacks read only the top-level size

**Severity:** MEDIUM (latent: 0 of 83 corpus KiCad-10 boards have a numeric net name; 21 corpus boards use custom padstacks)
**File:** `skills/kicad/scripts/pcb/reader.py:530` (also `:331,336` pad, `:553` arc, `:619` via, `:779` zone), backfill `pcb/pipeline.py:145-158`, `kicad_core/model.py:150` (`PcbReaderState.net_id`); `pcb/reader.py:283,312-313` (`find_first(pad, "size")`; nothing in the PCB scripts reads `padstack`)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R8-F3, kc/R8-F4)

**Symptom:** a minimal KiCad-10 board with nets "12" and "GND" gives segment `net: 12` without `_net_name`, pads `('12', 12)`, net map `{1: '12', 2: 'GND'}`, zone `(0, '')`, and graph `'12': islands 2`, so the track is lost. A `(padstack (mode custom|front_inner_back))` pad uses its front size on every layer.

**Fix direction / budget:** add a name-only lookup to `PcbReaderState` for KiCad 10 string nets (one fix across the reader, the model and the backfill). Read per-layer padstack sizes. Budget: latent in the corpus for the net-name half; the padstack half moves geometry on about 21 boards. Size first.

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

### KH-583: `--schema` marks optional setup keys as required on PCB, and gerber `missing`/`extra` as required although the defaults branch omits them, so most real outputs fail their own schema

**Severity:** MEDIUM (schema contract; 877 of 1,168 corpus PCB outputs with `setup`, and 3,475 of 5,449 gerber outputs)
**File:** `skills/kicad/scripts/envelopes/pcb.py:96-103` (setup requires `pad_to_mask_clearance`, `legacy_teardrops`, `allow_soldermask_bridges`); emitter `pcb/reader.py:76-106` (adds each key only when present; `:42-43` emits `setup: {}` without a `(setup)`); `skills/kicad/scripts/envelopes/gerber.py` (completeness `missing` / `extra` required) vs `analyze_gerbers.py:755-756`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R13-F7, R10 Empirical row "envelopes/gerber.py requires missing/extra")

**Symptom:** 877 of 1,168 corpus PCB outputs (75 %) lack `legacy_teardrops`, 874 lack `allow_soldermask_bridges` and 95 lack `pad_to_mask_clearance`. 3,475 gerber outputs (64 %) lack both `missing` and `extra`. Contract tests pass only because the harness fixture happens to carry all of them.

**Fix direction / budget:** make these fields optional in the envelope dataclasses. Budget: a `--schema` text change only, JSON-neutral. Declare it to the harness (schema artefacts and contract tests re-freeze). Waits on ruling: whether `diagnostics` also becomes schema-required in the same change.

### KH-554: lookup detectors (AM / OV / TJ / EX / FT / PM) never inspect fact staleness or quality, and AM-001 skips per-pin limits when no domain limit resolves [group 14]

**Severity:** MEDIUM (cache-backed parts only; no corpus caches)
**File:** consumers `lookup_detectors.py:108`, `:203`, `:316`, `:407`, `:504`, `:610` (no read of `_cache_context.is_stale` or `quality`); `lookup_helpers.py:34-38` (`get_facts` docstring names a nonexistent `facts.best(field, trust_gate=...)`); `skills/datasheets/datasheet_types/cache_reader.py:213-232` (`lookup` marks stale and still returns, by design); `lookup_detectors.py:116`, `:133-147` (`detect_absolute_max_violations`: per-pin `absolute_max` only tightens a resolved global limit; `:134-135` `continue`, empty `am_block` skips the component at :116); VDD synonym pool `:38-39`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R7-F1, kc/R7-F8)

**Symptom:** `get_facts` returning facts with a quality flag is the deliberate v2.0 §3.A.1 design (consumers decide); the validation detectors do decide (`validation_detectors.py:485/580/924/1053`), the lookup detectors never do, so a stale or score <60 extraction drives deterministic AM / OV findings. An extraction with per-pin limits and no domain limit produces no AM-001 check at all. The VDD synonym pool can merge distinct domains.

**Fix direction / budget:** per-consumer gating (not inside `get_facts`, which would reverse §3.A.1); evaluate per-pin limits without a domain limit; correct the docstring now (neutral). Waits on ruling: the lookup-detector trust policy (stale / score <60 / unscored / pin-level evidence / synonym pool), which must come after KH-433 because staleness is unreliable on copied projects. Budget: corpus-invisible (no extraction caches in the corpus); user-visible on cached projects.

**Addendum 2026-11-01 (3.0.x Wave 6, candidate `c0a8a62`):** the docs now describe today's behaviour (ruling W6-11): `skills/datasheets/references/cache-layout.md:124-133` says `lookup()` only marks a stale entry, the regulator detector skips stale or low-score facts and the lookup detectors do not read `stale` yet (`0dd234e`, `7c55b17`, tagged KH-638). Re-edit that paragraph when this entry's per-consumer gating lands. Code unchanged.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 1a4702a4 fix(kicad): a stale datasheet extraction is named once in diagnostics; get_facts docstring matches its behaviour (v3.0.2 Wave 11a Task 5, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: the `get_facts` docstring (`skills/kicad/scripts/lookup_helpers.py:40-49`) now names the real `best(specs, min_confidence=...)` / `has_data(specs)` (`datasheet_types/trust_gating.py:68,78`), with no nonexistent `facts.best(trust_gate=)`.
- **Left open:** per-consumer stale/quality gating in AM/OV/TJ/EX/FT/PM (`lookup_detectors.py` has no `stale`/`quality` read), AM-001 per-pin limits without a domain limit, and the VDD synonym pool (expected PARTIAL).

### KH-552: `unconnected_pin_list` in IC pinouts is effectively dead — every placed pin has a net, so `not net_name` almost never holds [group 13]

**Severity:** MEDIUM (descriptive field the review LLM reads; NT-001 still reports the condition)
**File:** `schematic/ic_analysis.py:417` (`analyze_ic_pinouts`), count `:444`, list `:452`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R3-F6)

**Symptom:** corpus: 123,992 IC pins sit on single-pin unnamed nets; for 123,795 of them the IC has no `unconnected_pin_list` entry. The field contradicts NT-001 (`schematic/net_analysis.py:64-89`).

**Fix direction / budget:** treat a pin alone on an unnamed net (and not NC-marked) as unconnected. Waits on ruling: whether a pinout row is a package or a symbol unit (sets multi-unit IC counting). Budget: `ic_pin_analysis` unconnected counts / lists on most units with ICs (large, field-only); same wave as KH-522..16 is fine.

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

### KH-545: integrated-magnetics RJ45 jacks (HR911105A, MagJack, HFJ11, LPJ, ARJP) are not counted as magnetics — "No magnetics" warning on a very common Ethernet design [group 11]

**Severity:** HIGH (common path; advisory sub-field)
**File:** `domain_detectors.py:432-441` (`detect_ethernet_interfaces`: magjack keywords recognised as `eth_connectors` only), `:595-606` (`impedance_advisory` "No magnetics"); `:530-531` (global fallback gives `pass` from an unconnected transformer)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R6-F7)

**Symptom:** PHY → HR911105A with no discrete transformer → `impedance_advisory.status="warning"` "No magnetics"; a design with an unconnected transformer anywhere passes.

**Fix direction / budget:** treat integrated-magnetics jacks as magnetics, and credit a transformer only when it is connected to the PHY's MDI nets. Budget: Ethernet `impedance_advisory` status changes on magjack units; size first.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 492b30d7):** fixed: a wider integrated-magnetics keyword list admits magjack connectors and they pass (`domain_detectors.py:419-425`, `:460-461`, `:617-623`). Still open: crediting a transformer only when it is wired to the PHY's MDI nets is not done: the global fallback stays (`:552-555`). The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-540: flyback-diode check is symmetric in the diode terminals — a reversed diode across a relay coil reads `has_flyback_diode=true` [group 10]

**Severity:** MEDIUM (designer-error path; false assurance)
**File:** `signal_detectors.py:3162-3179` (`detect_transistor_circuits`: both branches ignore pin names / roles A/K)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R5-F8)

**Symptom:** anode at +12V, cathode at the FET drain: the diode conducts across the coil when the FET is on and does not clamp at turn-off, yet the record says it has a flyback diode.

**Fix direction / budget:** require cathode on the supply side and anode on the switched node. Budget: `has_flyback_diode` flips and any related observation, on reversed-diode units only (expected tiny; size first).

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by c631ed88):** fixed: on N-channel drain-to-supply the flyback check requires cathode on the supply and skips zener / TVS parts (`signal_detectors.py:3355-3385`, `:3505-3516`). Still open: the drain-to-source branch (`:3498-3503`) still accepts either orientation and zener / TVS parts, P-channel skips the check (`:3507`), and unnamed-pin diodes (`:3513`) are not judged. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-531: USB VBUS capacitance check has no upper bound — a device port with more than 10 µF passes [group 8]

**Severity:** MEDIUM (missing check on an aux status; needs port-role inference)
**File:** `schematic/system_analyses.py:2377-2408` (`analyze_usb_compliance`: only `total_uf < 1.0` warns, else `"pass"`; caps counted without confirming a ground return)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R4-F2)

**Symptom:** USB 2.0 §7.2.4.1 limits a device / upstream port to 10 µF at attach (unless inrush-limited); hosts / downstream ports need ≥120 µF. A 47 µF device VBUS reports `pass`.

**Fix direction / budget:** waits on ruling: extend UC-004 with a role-gated upper bound (new semantics on an existing rule) or document as a known limitation. If extended: UC-004 status changes on device-role boards with >10 µF; size first; also require a ground return for counted caps.

### KH-507: SPICE `fail` results never set the Action's `has_critical` / status, because only EMC and thermal findings are counted

**Severity:** MEDIUM (Action gating; the outcome depends on a ruling)
**File:** `action/format-report.py:571-606` (only EMC and thermal append to `findings` before the counts), `:892,896`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/04-v3-security/findings/VERIFICATION.md` se/R2-F5, PARTIAL)

**Symptom:** a SPICE result with `status: fail` appears in the report body but never reaches the counts, so `has_critical` stays false and the Action does not fail. Whether that is a defect depends on intent: `entrypoint.sh:197` labels SPICE "optional, best-effort", and KH-442 still produces false SP-WARN, so counting SPICE could fail CI on false results.

**Fix direction / budget:** after the ruling, either count SPICE `fail` into the totals (behind an input, or only once KH-442 is fixed), or document in the Action README that SPICE never gates. Budget: output-changing (Action outputs and report summary); text-oracle budget for the Action report artefacts. Waits on ruling: should SPICE results gate the Action?

2026-10-25: left open by the 3.0.x Wave 1 security round (product ruling 3: revisit after KH-442).

### KH-496: docs/text leftovers from the review-period bug hunt (review C) — corpus-size wording, `what_if` sweep labels, datasheets SKILL line, offline `lifecycle_audit` unverified

**Severity:** LOW (documentation and `--text` wording)
**File:** README / SKILL docs (`5,800+` / `5,829` / `5,857` corpus-size variants), `skills/kicad/scripts/what_if.py` (sweep labels render as `1e+04`), `skills/datasheets/SKILL.md` ("used by both pipelines" line for `datasheet_page_selector`), `skills/kicad/scripts/lifecycle_audit.py` (behaviour without credentials unverified offline)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 17 (review C leftovers; deferred output-neutral docs items)

**Fix direction:** one corpus number sourced from the harness (`repos.md` count at the release), engineering-notation sweep labels, the SKILL line corrected, and an offline run of `lifecycle_audit` recorded. Budget: the `what_if` label change moves the `what_if` `--text` artefacts in the product text oracle (re-freeze with an allow entry); everything else is docs-only.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 6e4d9202 fix(what_if): log-sweep labels use SI prefixes (v3.0.2 Wave 11a Task 30, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: `what_if.py:65` formats swept values with 4 significant figures and an SI prefix. `skills/datasheets/SKILL.md:65` now says no pipeline script imports `datasheet_page_selector`.
- **Left open:** corpus-size wording still differs (`README.md:458` "5,800+", :464 "5,857"). No offline `lifecycle_audit` run is recorded.

### KH-495: periphery minors from the review-period bug hunt (review B) — SPICE top-level JSON list traceback, generic values pass `is_real_mpn`, EMC stderr count pre-`--compact`, and ten unverified items

**Severity:** LOW
**File:** `skills/spice/scripts/simulate_subcircuits.py:135` (`analysis_json.get("findings")` on a top-level JSON list → `AttributeError` traceback, exit 1; the loader at `:597-603` accepts any JSON); `skills/datasheets/distributor_core/inputs.py:17-44` (`is_real_mpn` rejects <3 chars, bare value+unit, percentages, DNP/NC/N/A and letter-only or digit-only strings, but passes `4k7`, `2k2`, `100nF 50V`, `4.7uF 0805`, `10K 1%`, `1uF/16V`, `100nF X7R`, `SOT-23`, `MH1`, `Conn_01x02`); `skills/emc/scripts/analyze_emc.py:632` (stderr finding count printed from the pre-filter list after `:579-584` reduced `result['findings']`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); the three named items verified in source at `07b7fb1` (`results/v3_round9b_gate_aux/`, scratch report)

**Unverified riders (maintainer's list, not yet checked harness-side):** `--spice-enhanced` without a simulator only warns on stderr; the manifest `scripts` entry; `--add-distributor` silently drops unknown names; LCSC order quantities; `verify.py` error coverage; `format-report --severity` is loose; `detect_project.sh` zero-file exit; `_smoke_v14_roundtrip --help`; sub-sheet redirect provenance; the `datasheet_verify` flag message.

**Fix direction / budget:** the JSON-list and stderr-count items are neutral. `is_real_mpn` tightening is a **distributor-oracle re-freeze** (the part set and skip counts of the frozen sync runs change wherever a fixture BOM carries such values) — size against `tools/tests/fixtures/distributor/` before changing it.

**Addendum 2026-10-31 (3.0.x Wave 5, candidate `698116c`):** note from 3.0.x Wave 5 (ruling R11, KH-488 `27989c7`): Value-derived MPNs are searchable, so a generic symbol name such as `Conn_01x03` is now searched by a provider that lacks its own part number whenever another distributor's number exists. The `is_real_mpn` tightening here would remove those searches. Still open as filed.

**Addendum 2026-11-06 (v3.0.2 Wave 11a, candidate `5510006a`, partly fixed):**
- **Fixed:** product v3.0.x-dev 8a4665c7 fix(spice): a JSON input whose top level is not an object is a named error, not a traceback (v3.0.2 Wave 11a Task 29, unreleased; local and unpushed at the handoff).
- **Verification:** harness re-read at `5510006a`: probe: `simulate_subcircuits.py` on `[1,2]` → "top level is list, not an object", rc 1, no traceback.
- **Left open:** `is_real_mpn` still passes `4k7`, `2k2`, `100nF 50V`, `SOT-23`, `MH1` and `Conn_01x02` (probe; deferred (b)). The EMC stderr count still prints the pre-filter `len(findings)` (`emc/scripts/analyze_emc.py:632`). The ten riders are unchecked.

### KH-494: core minors from the review-period bug hunt (review A) — NaN/non-numeric coordinates traceback, `--no-hierarchy` still merges top-level sheets, `--text` drops `--output`, no PCB duplicate-reference check, and eight unverified items

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/connectivity.py:323` (`(at nan 100.33 0)` on a placed symbol → `ValueError: cannot convert float NaN to integer`, traceback exit 1; `(at abc …)` → `kicad_core/sexp.py:195` `could not convert string to float`; no guard around `get_at` / `get_xy` in `schematic/reader.py:471-621` or `pcb/reader.py:52-374`); `schematic/pipeline.py:1281` (`merge_top_level_sheets` runs unconditionally — `hierarchy.py:197-198` says so by design — while `analyze_schematic.py:33` `--no-hierarchy` help says "treat file as standalone root"); `analyze_schematic.py:114-117` / `analyze_pcb.py:140-143` (`--text` prints and returns before the `--output` / `--analysis-dir` branches, no warning; EMC has the opposite precedence at `analyze_emc.py:628-640`); `pcb/*.py` (no duplicate-reference audit; the schematic has one at `schematic/audits.py:29`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 15 (review A minors); the four named items verified at `07b7fb1` (the NaN and `abc` cases by running the analyzer on an edited fixture)

**Unverified riders (maintainer's list):** datasheet index shape crashes; silent datasheet-manifest and sym-lib-table failures; missing `lib_symbols` gives no diagnostic; `--project-root` traceback; the `--stage` wording; zip-only gerber dirs; invalid numeric args accepted; thermal/cross exit-code mismatch.

**Fix direction / budget:** coordinate guards, `--text`+`--output` precedence and the unverified riders are neutral (malformed input / CLI only). The `--no-hierarchy` item is a `--help` text change (text oracle) if the doc is fixed, or neutral for the corpus if the behaviour is (the harness never passes the flag outside the standard profile, where it is on for every unit — a behaviour change there WOULD move sub-sheet-redirect units: size before choosing). A PCB duplicate-reference check is a **new finding** = corpus-output class on every board with duplicate footprint refs (size with a corpus scan of `footprints[].reference`).

#### Addendum to KH-494 (core minors, review A)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` part a, Empirical: "R1: diagnostics newline")
`skills/kicad/scripts/kicad_core/diagnostics.py:31`, `:38`: the stderr `Warning:` line embeds `str(exc)[:200]` unescaped, so an exception message containing a newline breaks the one-line-per-diagnostic stderr contract. Escape or replace newlines. Neutral for the envelope, stderr only.

### KH-487: SPICE `--parasitics` matches net names verbatim between the schematic and PCB name spaces, so it applies only to RC-filter output nets on global or root-sheet labels

**Severity:** LOW (feature coverage, not correctness; harness SPICE profiles never pass `--parasitics`)
**File:** `skills/spice/scripts/spice_templates.py:112-115` (`parasitics_data["nets"].get(net_name)` verbatim), called only from `generate_rc_filter` (`:198`) with `det["output_net"]` — the other 17 generators accept `parasitics=` and ignore it. Schematic names (`schematic/connectivity.py:840-847`): bare `NET`, `/<sheet-file-stem>/NET` only on a cross-sheet collision, `__unnamed_N` for unlabeled. PCB names (`pcb/reader.py:160-190` → `net_lengths[].net`): KiCad's board names — `NET` for globals / root locals, `/<Sheet instance name>/NET` for sub-sheet locals, `Net-(R1-Pad1)` for unlabeled.
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 8 (review B-I2); verified at `07b7fb1`. The handoff's "never applies on real designs" is overstated: global-label / root-sheet RC filters do match.

**Fix direction:** normalise both sides (strip the sheet prefix, map `__unnamed_N` ↔ `Net-(…)` through the shared pad/pin net, or match through the cross-analysis net map) and pass `parasitics` to the other generators. Budget: corpus-output only under a SPICE profile that passes `--parasitics` (`run_spice.py --with-parasitics`); neutral for the default spice-offline profile.

#### Addendum to KH-487 (sch ↔ pcb net names compared verbatim)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R11-F9)
The same name-space mismatch affects cross_verify and cross_analysis, not only SPICE `--parasitics`, and is HIGH there. Sites: `cross_verify.py:232-233,356,506`; `cross_analysis.py:145,256,719,993-996`. Comparing schematic `pin_nets` with PCB `pad_nets` by (ref, pin) over 331 corpus pairs (44,179 named pins), 14,785 names differ, 8,914 of them only by a `/…/` prefix, in 170 of 331 pairs. Root-sheet local labels differ too (sch `TD+` vs PCB `/TD+`), so the bug is not limited to child sheets. Fix both consumers through one shared sch↔pcb net correspondence (pad ↔ pin join) and widen the title. Waits on ruling: the correspondence design.

**Addendum 2026-10-31 (GitHub #61.3, PGIRang):** a reporter case for the EMC side. EMC DP-001..004 look schematic pair names up in PCB-keyed maps, so a root-sheet local `USB_DM` never matches the board's `/USB_DM` and no PCB-side pair check runs: `emc_rules.py:2083`, `:2104-2105` (DP-001), `:2164` (DP-002), `:2260` (DP-003), `:2323` (DP-004), map from `_build_net_length_map` `:2032-2043` (at `7131f26`). Prefixing `/` in the schematic JSON makes DP-004 fire twice. The reporter's "match with and without the prefix" is unsafe (sub-sheet locals share leaves); the fix is the pad ↔ pin correspondence above (kc/R11-F9). An intra-pair spacing check is a feature request (HS/SS only). Source: product `.superpowers/sdd/2026-10-29-v3.0.x-wave5/github/gh-60-62-findings.md`.

**Addendum 2026-11-06 (v3.0.1 shipped):** GitHub #61 stays open after v3.0.1 (#60 and #62 closed as fixed); this entry is its harness home. The PCB pair checks still match nets by name (`USB_DM` vs `/USB_DM`); the planned fix is the pad / pin net matching above, in a later release.

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

### KH-483: unannotated duplicate references (`U?`, `R?` …) collapse in the detector context and the BOM statistics

**Severity:** LOW (unannotated designs only; sibling of KH-455's `(ref, pin)` dedup)
**File:** `skills/kicad/scripts/kicad_types.py:21` (`comp_lookup = {c["reference"]: c for c in components}` — last wins; both symbols' pins carry `"component": "U?"` via `schematic/connectivity.py:352`), `schematic/bom_stats.py:15-24` / `:59-63` (dedupe by reference, so BOM rows and `statistics` counts drop the duplicates). The `components` list itself keeps both and `schematic/audits.py:29-45` flags them (`duplicate_references` + `unannotated`).
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 4 (review A-I5); verified at `07b7fb1`. Corpus (2026-10-24 scan of the 36,462 schematic outputs, `results/v3_round9b_gate_aux/sec7_sizing.json`): 1,598 units / 466 repos carry at least one `?`-suffixed reference on more than one symbol (`U?` 13,619 symbols, `R?` 9,013, `C?` 7,157, `D?` 3,203, `J?` 1,506, `P?` 1,259, `Q?` 895, `SW?` 664); 5,825 units carry `annotation_issues`.

**Fix direction:** key the detector context by UUID (or `reference#uuid`) and let BOM statistics count unannotated symbols individually. Budget: **corpus-output** on the units above — `statistics.total_components` / `unique_parts`, `bom[]` rows and every detector that resolves a pin's component through `comp_lookup` on those designs (SEED/STRUCT count locks move) — plus KH-455's PP-001 residue class.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part A):** (a) phodina/openwrt-one `bom_fp_bad` 0 → 1: a duplicated `U?` ref merges package fields across different parts once a record carries `_unit_count > 1` (Wave 3b H4). (b) Sorcerer UE9: a duplicated ref whose records are two different parts.

**Addendum (2026-10-27, product 3.0.x Wave 3b Part B):** cross_analysis never treats a blank or `?` reference as multi-unit, and DA-001 keys such parts by `instance_path`, so separate `U?` ICs count separately. Board-side duplicates remain: stanford-ssi Aerolotl U3 ×3 and PocketQube OBC U1 ×2 give one distinct XV-002/XV-003 per footprint (real differences, not duplicates).

**Addendum 2026-10-28 (3.0.x Wave 4 Part A):** ERC `pin_positions` are keyed by (ref, number), so unannotated duplicate refs collapse and hide markers.

### KH-481: a sub-sheet whose file is missing is dropped silently — no `diagnostics` record, unlike the recursive and empty cases

**Severity:** LOW (provenance; the design is analysed without the sheet and nothing says so)
**File:** `skills/kicad/scripts/schematic/reader.py:713-716` (appends a sub-sheet only `if sub_path.exists()`, so `parse_all_sheets` never sees the missing file); `schematic/hierarchy.py:143-157` records diagnostics for the recursive (`:151-154`) and empty (`:84-90`) cases but has no branch for an absent file; `hierarchy.py:194-195` documents the gap
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 2 (review A-I2); verified at `07b7fb1`

**Fix direction:** record `schematic.hierarchy.parse_all_sheets` / `FileNotFoundError` / "missing sheet skipped" where the recursive case records. Budget: `envelope/diagnostics` additions on every corpus root with an unresolvable `Sheetfile` (size with a corpus walk before the fix; the harness's `diagnostics: []` expectations in the chain oracle and spice-offline comparator are additive-tolerant only through a budget).

#### Addendum to KH-481 (silent drops without a `diagnostics` record)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` kc/R9-F8)
Same silent-degradation class on the PCB side. When every zone is unfilled, `pcb/copper.py:961-966` returns a warning dict that `pcb/presentation.py:414-420` pops, keeping only the finding lists, with no diagnostic. Per-zone `is_filled` is still emitted (`reader.py:792` → `presentation.py:202`), so it is not invisible. 61 of 3,023 sampled boards have only unfilled zones. Waits on ruling R9-F8 (which skipped checks get a `diagnostics` record).

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by b22bab32):** fixed: the `.kicad_sch` reader reports each missing sub-sheet in a diagnostic (`reader.py:1366`, `hierarchy.py:340-348`) and reads backslashes in sheet paths as separators (`hierarchy.py:71`). Still open: legacy `.sch`: `legacy_reader.py:1068-1070` still drops a missing sheet silently (82 files, v3.0.3); the PCB unfilled-zones addendum (`pcb/copper.py:1009-1013`) waits on ruling R9-F8. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

### KH-474: `lifecycle_audit.py` output carries no `diagnostics` key — the seventh JSON producer is outside the round-8 envelope rule

**Severity:** LOW (consistency: every analyzer envelope and the SPICE report gained `diagnostics: []`; a reader that keys on it sees `lifecycle_audit` as pre-v3)
**File:** `skills/kicad/scripts/lifecycle_audit.py` (no `diagnostics` anywhere in the file at `a0df172`; it is not one of the six `--schema` envelopes)
**Discovered:** 2026-10-24, v3 round-8 handoff §11

**Fix direction:** add `diagnostics: []` after its `compat`-equivalent block and route its guarded sites through `kicad_core.diagnostics.record`; additive, harness `--schema`/contract tests gain one key. Closes together with KH-464 (missing-input traceback) if the file is touched once.

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

### KH-459: `audit_pwr_flags` only inspects `known_power_rails` — `power_in` pins on unnamed or locally named nets (connector VBUS, battery holder) are never audited, so `pwr_flag_warnings` is empty where KiCad ERC reports `power_pin_not_driven`

**Severity:** LOW (false negative in an advisory list that the skill advertises as the "PWR_FLAG audit"; ERC remains authoritative; likely frequent corpus-wide — connector-fed `power_in` pins on unnamed nets)
**File:** `skills/kicad/scripts/analyze_schematic.py:5137-5165` — `audit_pwr_flags(components, nets, known_power_rails)` iterates `sorted(known_power_rails)` only
**Discovered:** 2026-10-22, SacMap rev2 soak run 9 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/9/`, product `main` @ `4701c26` = v2.3.2 pre-tag; report `REVIEW-2026-10-22.md`, meta `REVIEW-2026-10-22-meta.md`), meta §2 #17

**Repro:** SacMap: native ERC (KiCad 10.0.7) → 3 × `power_pin_not_driven` (`BT1.1`, `BT1.2`, `J1.1 VBUS`). Analyzer: `pwr_flag_warnings: []`. The three pins sit on `__unnamed_40` (BT1.1 + BT1.3, both `power_in`), `__unnamed_8` (BT1.2 `power_in` + Q4.3 passive) and `__unnamed_10` (J1.1 `power_in` + U4.5 + F1.1 passive) — none is in `known_power_rails` (`+3V3`, `+5V`, `+BATT`, `GND`, all of which carry PWR_FLAG and are correctly skipped).

**Fix direction:** iterate every net: `power_in` present, no `power_out`, no `has_pwr_flag` → warn (KiCad's rule is per pin, not per named rail); keep the entry shape. Gate budget: `pwr_flag_warnings` additions corpus-wide (the v2.1 KH-354 fix REMOVED 7,946 on 3,442 units; this adds a different population — measure before the fixing round).

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

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, `727d0ab3..f53d107e`):** each sheet file is now parsed once per design (row.kicad_sch 36.8 → 6.6 s; row_group `parse_all_sheets` 295 → 30 s). Both remaining units still time out in the Wave 11b-1 gate (ram 120.1 / 120.1 s, row_group 120.1 / 122.1 s), for two other causes now filed: KH-1027 (`connected_to` output growth, row_group) and KH-1028 (quadratic instance resolution, ram). Stays PARTIAL. Harness: row_group now reaches serialization inside the cap and can pass 8 GB RSS; the standard profile has no per-unit memory ceiling.


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

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by de3fb6e1, a6ab651a, d8c3281d):** fixed: all FB pins are collected; the one whose divider tops out on the output rail, or that ties straight to it, sets the estimate (`signal_detectors.py:1741-1761`, `:2108-2117`). Still open: the output rail itself still follows pin order (first SW pin `:1746-1748`, last VOUT `:1754-1755`), so which channel of a TPS62410-class part is estimated depends on `ic_pins` order, and only one channel is estimated. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

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

### KH-430: thermal package table lacks SOT-563, and the analyzer ignores the extraction's RθJA (142.7 vs default 150 °C/W)

**Severity:** LOW (Tj estimates on SOT-563 parts fall back to a default even when the datasheet extraction carries the real θJA)
**File:** `skills/thermal/scripts/analyze_thermal.py` (package table; θJA source precedence)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap U2 (SOT-563) is assessed with the 150 °C/W default; the cached extraction has `theta_ja = 142.7`.

**Fix direction:** add SOT-563 (and the SOT-363/SC-70 family) to the package table; when a trusted extraction provides θJA use it ahead of the table and mark `evidence_source: datasheet`.

**Gate budget (when fixed):** TH-DET/TS-00x content on SOT-563 boards and on boards with extracted θJA (corpus: ≈0 extractions).

**2026-11-08 (v3.0.2 Wave 11b-2 gate, candidate `6138b126`; product slug `KH-new-thermal-ipc-sot-names`, survey E10):** M3 fixed `SOT223` / `SOT23` without a hyphen (KH-978). The table still has no SOT-563 / SOT-583 row, and the SOT-363 / SC-70 / SOT-89 rows need the hyphen. Probe of `_classify_package` (`analyze_thermal.py:130-147`, table `:71-118`):
- `unknown` (150 °C/W default): `SOT-563`, `SOT-583`, IPC `SOT95P280X145-5N`, `SOT65P210X110-6N`, `SOT230P700X180-4N`, `SOT89`, `SOT363`, `SC70-6`, `SOT-323`, `SOT-353`, `SOT-666`, `SOT-723`, `SOT-883`, `SOT-1123`, `SOT-457`, `SOT-886`.
- Correctly classified: `SOT-89-3`, `SOT-363_SC-70-6`, `SOT-23-6`, `SOT-223-3_TabPin2`.

Fix as listed, with optional hyphens and IPC body codes. The extraction θJA half is unchanged.

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

### KH-434: PD-001 is silent when evaluated with no peaks — no `checks_run`-style line in `category_summary`

**Severity:** LOW (observability: a board with zero PDN peaks is indistinguishable from a board where the PDN check did not run)
**File:** `skills/emc/scripts/emc_rules.py` (PD-001 / `category_summary`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap's EMC output has no PDN entry at all; nothing says the check ran and found 0 peaks.

**Fix direction:** emit a `category_summary.pdn` (or `checks_run`) record with `peaks_total: 0` when the check runs and finds nothing, matching the `checks_run` convention in cross_analysis.

**Gate budget (when fixed):** additive `category_summary` entry on every EMC unit with a PDN evaluation.

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

## Test Harness Issues

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

**Addendum 2026-11-06 (code fixed, data pending):** `tools/generate_catalog.py` now reads the v3 top-level `sheets` list (`_max_hierarchy_sheets`; v3 outputs carry no `hierarchy_context`). A dry run (`generate_catalog.py --json`) gives 1,589 repos with `max_hierarchy_sheets > 1`. The tracked `reference/repo_catalog.json` was not regenerated: it is stale on 17 fields (emc_summary 4,380 repos, assertions 4,243, ...) and moves VALIDATION.md's corpus numbers, so regenerate it, then `generate_cross_sections.py`, at the v3.0.2 corpus regen and close this then.

## Priority Queue

_35 open KH-* + 16 open TH-* issues (2026-10-14: TH-052/053/058 FIXED (H0 plan 1), +TH-060/061/062 filed. Earlier: 2026-10-06: v2.3.1 shipped @ 0684046 and the corpus regen ran CLEAN. Closed this cycle, all in FIXED.md: KH-408..415, KH-418/420 (v2.3.1 batch + follow-up), KH-419/424/425 (SacMap soak fixes), TH-054 (run_emc crash masking). Open KH: 328..334 datasheets-infra backlog; 355/364/365 audit remainder; 403/404 HIGH connectivity over-unions; 416/417 v2.3.1 riders; 421 Marble hash-seed nondeterminism; 422 `--full` point-in-polygon cost; 423 legacy `.sch` empty fields; 426..440 SacMap soak long tail; 441 via_in_pad attribution; 442 behavioral opamp gain 0. Open TH: 037..042/044/047 legacy; 049 contamination tripwire; 055 timeout-class v1.3-era pcb outputs (191 boards); 056 KH-313 anchor; 057 bugfix generator merge-by-id; 059 batch SPICE hermeticity; 060 kh393 power-rails test premise stale (strict xfail); 061 test_datasheet_db_cli writes repos/.test_fallback; 062 print-and-return vacuous skips in smoke files. Earlier history: 19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
