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

Last updated: 2026-11-19

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-1340** (KH-1339 filed 2026-11-19 from the 12c constants check, product-confirmed; KH-1285..1338 filed 2026-11-19 by the harness from the v3.0.3 Wave 12c handoff, each checked at `ea5f7fd1` by read-only agents: KH-1285..1287 fixed in the range and filed straight to FIXED.md, the rest open from `kh-filings-wave12c.md` (A, B; 5 duplicates folded into existing KHs) and two harness finds (KH-1337, KH-1338); `D/` and `X/` in those entries are the product's `.superpowers/sdd/2026-11-17-v3.0.3-wave12c/` and `.claude/worktrees/v3.0.x-dev/.superpowers/sdd/2026-11-17-v3.0.3-wave12c/`; KH-1195..1284 filed 2026-11-17 by the harness from the v3.0.3 Wave 12b handoff; KH-1195..1284 filed 2026-11-17 by the harness from the v3.0.3 Wave 12b handoff, each checked at `7ed10f3e` by read-only agents: KH-1195..1207 fixed in the range and filed straight to FIXED.md, the rest open from `kh-filings-wave12b.md` (A, B), survey-H section 3 (H1-H3, H5, H7-H9) and one harness find (KH-1284); `E/` and `D/` in those entries are the product's `.claude/worktrees/v3.0.x-dev/.superpowers/sdd/2026-11-16-v3.0.3-wave12b/` and `.superpowers/sdd/2026-11-16-v3.0.3-wave12b/`; KH-1175 filed 2026-11-16 by the product; KH-1176..1194 filed 2026-11-16 by the harness from the v3.0.3 Wave 12a handoff, each verified at `08879e2d` / `f254cb23` (KH-1176..1178 and KH-1193 fixed in the range, filed straight to FIXED.md; KH-1193 was a regression inside the range, reverted at `f254cb23`; KH-1194 split from KH-805); KH-1122..1137 filed 2026-11-15 from the product's v3.0.3 triage survey at `6b9767e1` — SPICE sources typed varistor, VM-001 multi-supply ICs, DP-001 untyped-pair default, #50 net ties (power_budget, rail voltages), single-layer fill_ratio > 1, ES-002 without a ground pad, KiCad 10 project bus aliases / rounded-rect outlines / rule-area flags / backdrill knockouts, KiCad 11 footprint `(transform)` (HIGH) / ellipses / pin-to-pad maps / escaped stacked pins / variant `symbol_override`; KH-1138..1174 split the same day from the umbrellas KH-674 (13), KH-710 (12) and KH-495 (12); KH-364 merged into KH-751; KH-915 / 906 / 981 / 1071 / 437 / 634 closed and KH-328 / 855-857 / 859-861 moved to the roadmap, see FIXED.md; KH-1109..1121 filed 2026-11-15 by the harness from SacMap rev2 soak runs 12 + 13 at the v3.0.2 release `2c645996` (product report), each verified by code read at `365aea94` — lifecycle PN stderr, multi-MPN part numbers (KH-970 residue), capability_mode legacy index (KH-458 residue) and platform, offline lifecycle trust (MEDIUM), silkscreen completeness without a finding, cross_verify logo orphans, fab gate `--analysis-dir`, summarize_findings stray JSON, reworded deep-review diff, previous-run choice, PM-002 by-design, DC-002 per-IC (LOW-MEDIUM); addenda on KH-430, 1042, 716, 661, 971, 973, 896, 1107, 495, 432, 428, 968, 930, 969; KH-1108 filed 2026-11-13 from the product's v3.0.2 Wave 11e handoff (junction-load pin-type trust + RC direction when the far end is the source); KH-1103..1107 filed 2026-11-13 by the harness from the product's v3.0.2 Wave 11d handoff (CHANGELOG accuracy pass), each re-read at `206403e8`: export_issues Markdown gaps, two tools' `--output` stream writes, NCP1117 order codes read as 1.25 V (MEDIUM), balanced merge conflicts with no diagnostic, LC-004 no-answer vs no-match; KH-1080..1102 filed 2026-11-13 by the harness from the v3.0.2 Wave 11c handoff, each verified at `db551674` (KH-1088 / KH-1089 fixed in the range, filed straight to FIXED.md); KH-1073..1079 filed 2026-11-11 by the harness from the product's TH-109 rulings, each re-verified by re-running the analyzer at `6138b126` — keyword-only regulators on uncached KiCad 5 libraries, discrete ORing / backfeed diodes in no detector, TVS keyword gaps (SMF/SM6T/SM712, MEDIUM), the HX711 regulator dropped by the op-amp/ADC exclusion, ESD-array `clamp_net` null, buzzer driver on the other pin, I2C pull-ups through 3-pad solder jumpers (MEDIUM); KH-1070..1072 filed 2026-11-11 from the TH-109 triage — `kicad_version` unknown without `generator_version`, BUZ11 FETs missing from transistor circuits, `single_pin_nets` duplicate `nets` key; KH-1068 / 1069 filed 2026-11-08 from the KH-755 / KH-480 closure reads — schematic-only DNP connectors, machine-dependent failed-run diagnostics; KH-1040..1067 filed 2026-11-08 by the harness at the product v3.0.2 Wave 11b-2 gate (unreleased, candidate `6138b126`) — the handoff's new-KH slugs, the ruled `es001-dnp-protection` slug its list dropped, and two residues found verifying the KH-573 / KH-713 closures, each claim re-read at the candidate; KH-1039 filed 2026-11-07 on the user's Wave 11b-1 ruling — no annotation for a duplicate `Value` property, the Eagle-import hidden empty copy that KiCad 10 reads; KH-994..1038 filed 2026-11-07 by the harness at the product v3.0.2 Wave 11b-1 gate (unreleased, candidate `f53d107e`) — the handoff's new-KH slugs plus the survey asks it dropped, each claim re-read in the candidate with probes and corpus snaps (several corrected: legacy `.sch` runs no system-level analyses, every GOST `VD`/`VT` reference typed varistor, MIC2305x dropped by a "load switching" substring, RM-DET `sma` matching `*_Small`), plus two false VM-001 adds from the gate and three closure residues; addenda on KH-925 (x3), KH-447, KH-654; 46 entries FIXED in Wave 11b-1 (KH-993 on the harness release-gate rerun), 16 partly fixed with addenda, see FIXED.md; KH-993 filed 2026-11-06 by the harness from the release-gate `RealPlaywrightTest` run at `a8207138` — the browser fallback never saves a direct PDF, Wave 11b list; KH-991 / KH-992 assigned FIXED-direct 2026-11-06 from the Wave 11a handoff — Windows CRLF stdout, JLCPCB translator LCSC part number, see FIXED.md; KH-980..990 filed 2026-11-06 by the harness at the product v3.0.2 Wave 11a gate (unreleased, candidate `5510006a`) from the handoff's new-KH list, each claim re-read in the candidate with probes — thermal extraction reader, `analysis.output_dir` containment, trusted-model `.end`, NaN/bool voltage overrides, lifecycle `X7R, 50V` split, Deep Review `not_found` fallback, `find_extraction` underscore collision, SPICE fetcher own lookup, NaN quality trust, VM-001 open-drain status pins, Action ordered-list lead; the `.kicad_dru` candidate is a KH-924 addendum (comma decimals refuted), the ground-name candidate a KH-925 addendum; KH-329..970 (83 entries) FIXED in v3.0.2 Wave 11a, see FIXED.md; KH-634 / 647 / 906 / 965 claimed fixed but partly fixed, KH-482 / 495 / 496 / 554 / 559 / 743 / 805 / 872 / 914 / 924 / 973 partly fixed as declared, addenda on each; KH-974..979 filed 2026-11-06 from the product's v3.0.2 survey candidates, each verified by the harness at `4c2a0d6` (the LTspice/Xyce exponent crash is a KH-743 addendum, the corpus capability sidecars a KH-793 addendum); KH-968..973 filed 2026-11-06 by the harness from SacMap rev2 soak run 11 at the v3.0.1 release `7d9d4d9f`, each verified by code read there — footprint keepouts never read, GP-001 per-net 95 % threshold without gap location, lifecycle MPN-only search, XV-004 blank-MPN / distributor-PN sub-cases, silent capability-loss diagnostics umbrella, `diff_analysis` tool-version grading and missing gerber / cross_analysis diffs; addenda on KH-433, KH-930, KH-462; KH-967 filed 2026-11-06 from the product ruling on the Wave 10b gate — `<n>V<n>_N` split rails read positive, verified in the candidate; KH-957..966 filed 2026-11-05 by the harness at the product 3.0.x Wave 10b gate (unreleased, candidate `2abc8496`) from the handoff's new-KH list, each claim re-read in the candidate — PM-001 ignores `drc_exclusions` (the handoff's graze-tolerance cause refuted: 0.119 mm overlaps) and both-layer tie order, duplicate courtyard outlines without `malformed_courtyard`, RP-001 power / high-speed classifiers, VS-001 branch disagreement (vias but no ground via), RP-002 `ran: true` without coverage, pin-only regulator outputs leaving `rail_voltages`, power-budget LDO sign guard, `VSS*` as ground for EN, DFM vs market-inferred IPC class, op-amp dead-output gain error (the 0.00 dB half refuted: deliberate below-minimum demotion); KH-947..956 filed 2026-11-05 by the harness at the product 3.0.x Wave 10a gate (unreleased, candidate `e60d03b5`) from the handoff's new-KH list, each claim re-read in the candidate — nested `.kicad_dru` bound ignored, `analysis: null` / non-string power_rails patterns, BOM-prefixed config, `RecursionError` at ~45 JSON loads, `--v14` null pin, Deep Review split exponent, SPICE LCSC `mfr`, Action residue, fab gate text, lazy `kicad_core.executables` import; addenda on KH-924 (nested condition) and KH-910 (still present); KH-915..946 filed 2026-11-04 by the harness at the product 3.0.x Waves 9b + 9c gate (unreleased, candidate `8c42799`) from the handoff's new-KH list, each claim re-read in the candidate — KH-920 filed FIXED-direct (load switches typed LDO, see FIXED.md) and KH-946 its open residual (dual-switch pin pairing); KH-912..914 filed 2026-11-03 by the harness at the product 3.0.x Wave 9d (docs) gate (unreleased, candidate `389fbd5`) from the handoff's new-KH list, each re-read in the candidate — gerber X2 docstring, unverified gerber version rows, raw `<MPN>` schema / provider text; KH-904..911 filed 2026-11-03 by the harness at the product 3.0.x Waves 9a + 9e gate (unreleased, candidate `6009004`) from the handoff's new-KH list, each claim re-read in the candidate — SPICE model-manifest reset, silent stale for PDFs outside `datasheets/`, `load_manifest` FIFO, abandoned download thread, LTspice/Xyce metadata, Action Top Risks severity, `test_cache_reader` isolation, deep-review partial pin names; KH-870 FIXED in 3.0.x Wave 9a, see FIXED.md; KH-895..903 filed 2026-11-03 by the harness on the product's request from SacMap rev2 soak run 10 at `07b7fb1` (v3.0.0 release base), each verified by code read at `07b7fb1` and v3.0.x-dev `5687ee1` — TE-001 touch pads, lifecycle `sources_available`, LC-007 contradiction, LC-004 multi-MPN wording, report-section gate, SPICE simulator version, two run ids, `power_domain` warning dedup, SKILL.md migration note; KH-894 filed 2026-11-03 by the harness on the product's request after the Wave 8c + 8b acceptance — supply-rail recognition by name only, su-pcb decoupling → rc_filter under KH-800's KiCad names; KH-867..893 filed 2026-11-03 by the harness at the product 3.0.x Wave 8c + 8b gate (unreleased, candidate `0efc012`) — KH-867..873 from the 8c handoff (other `--output` CLIs, `/dev/` link write-through, raw pipeline cache reads, PDF FIFO hash hang, Windows identity fallback, wrong-part `ok` refresh, Windows replace-onto-open-file), KH-874..892 from the 8b handoff (bus members as naming candidates, VM-001 cascade / multi-unit voltage, `4.5V-28V IN` rail, `SCLn`/`SDAn`, legacy and multi-root tie-break, stripline, plain `routing_complete` wording, ferrite `@` / `0R/2A` parsing, HS classifier, split-detection geometry gaps, SW-003 dead note), KH-893 by the harness (text-oracle jlcsearch call); each claim re-read in the candidate; KH-806/791/811/797/807/813 FIXED in 3.0.x Wave 8c and KH-851/820/825/863/850/800/864 FIXED in 3.0.x Wave 8b, KH-795 narrowed to the void half, KH-643 addendum, see FIXED.md; KH-863..866 filed 2026-11-02 by the harness at the product 3.0.x Wave 8a gate (unreleased, candidate `647bc85`) from the handoff's new-KH list, each claim re-read in the candidate — OR-001 angle rounding, EMC limit band edges, the Action's no-op `derating-profile`, what_if no-affected `--output` stdout; KH-818/819/821/822/826/827/828/849/852/853/854 FIXED in 3.0.x Wave 8a, KH-814 narrowed to the schematic / PCB `error` opt-in half, see FIXED.md; KH-829..848 assigned FIXED-direct 2026-11-01 from the product 3.0.x Wave 7 (architecture) close handoff (unreleased, candidate `988d576`) — the range's output-neutral slugs, each landed and closed by its named commit: UTF-8 register sites, dead `NetlistQueries` surface, dead core helpers, unread what-if / thermal / cross inputs, dead provider members, EMC severity-map duplicate, dead datasheet v2 validator / SPICE tables / smoke check, named-pin net / `pin_nets` annotation / S-expression property-decode duplicates, lifecycle derived writer, dead cache / context helpers, run-folder name, verifier helper names, detector netlist inline, lifecycle engine owner, PCB `--schema` thickness / `via_analysis` text, `summarize_findings` help vocabulary, see FIXED.md; KH-659 FIXED in 3.0.x Wave 7, see FIXED.md; KH-849..854 filed 2026-11-01 from the Wave 7 handoff's found-and-not-fixed list (each output-changing) — ~45 more locale-default text sites, ferrite `600R/200mA` parsed as 600 Ω, `(general (thickness))` dropped without `(setup)`, the Action's EMC / thermal "blocking findings" notice (thermal twin added by the harness), LC-007 text naming `lifecycle_audit.py`, undeclared `fix_params`; KH-855..862 filed 2026-11-01 from the Wave 7 deferred-by-ruling list — detector-family move, what-if engine extraction, vendor clients, PCB point-to-segment merge, SPICE kind registry, Action Python runner, `build_connectivity_graph` move (harness patch targets first), Phase 4 exercise script; KH-814..828 filed 2026-11-01 by the harness at the product 3.0.x Wave 6 (docs) gate (unreleased, candidate `c0a8a62`) from the handoff's new-KH list, every claim re-read in the candidate — Action `has-critical` / `findings-count` scope with the retired `voltage_derating` read (MEDIUM), per-CLI output-flag precedence, TW-001 width-table provenance, SPICE extraction-tier key and `meta` mismatch, EMC score after `--severity`, typed-lookup parent-folder cache (Security, MEDIUM, KH-782 residue), microstrip impedance on bulk εr (MEDIUM, output-changing under `--full`), five undeclared PCB envelope keys, silent missing `--config`, Action EMC/SPICE base lanes, Mouser default delay, PCB routing note as a `ValueError` diagnostic, what_if / detector `vref_source` confidence, what_if sweep `±tol` and `--output`; KH-636, 637, 638, 639, 640, 641, 642 FIXED (docs) in 3.0.x Wave 6, see FIXED.md; KH-329 doc halves fixed, entry narrowed to the `--use-cached-scout` traceback; addenda on KH-592 and 554, and on KH-633 in FIXED.md; KH-780..790 assigned FIXED-direct 2026-10-31 from the product 3.0.x Wave 5 handoff (unreleased, candidate `698116c`) — generic-transistor audit sync-manifest `parts`, multi-unit IC verification, extraction caches from a shared temp / parent directory (Security), review-plan run dir, Gerber job-file inner-layer completeness, Gerber X2 reader, Gerber drill model, empty return-path result (GitHub #60.1), `--gp001-debug` path (#60.4), Type-C detection (#61.2), degenerate switching-loop area (#62); KH-330, 484, 488, 571, 572, 577, 578, 579, 580, 595, 596, 600, 601, 602, 603, 604, 605, 614, 615, 616, 617, 620, 621, 622, 624, 625, 633, 646, 652 FIXED in 3.0.x Wave 5, see FIXED.md (commit-message omissions recorded under KH-571 / 572 / 578 / 617 / 646 / 652 / 781 / 786); KH-492, 606, 634, 636, 637 partly fixed (entries stay open with addenda); KH-791..813 filed 2026-10-31 from the Wave 5 handoff follow-ups — `analysis/manifest.json` 0600, SPICE model cache in a shared cwd, `capability_mode` cwd output, relative `inputs.source_files`, reference-net change under a trace (GitHub #60.2/#60.3, MEDIUM), pad-based hot loop, non-atomic `merge_results`, extraction lookup order, multi-condition SpecValue, root-sheet order dependence (MEDIUM), back-mounted THT side, Gerber outline choice, nightly job ids, Type-C CC reader, lifecycle / gerber carry-forward, `--output` atomic writes, spaced `±` in the Deep Review gate, family digit boundary, unnamed supplier slot, DNP value markers, cache-read nofollow, `export_issues` paging, orphan PDF on `--force-all`; addenda on KH-487 (GitHub #61.3), 585, 592, 495, 606, 634 (and 492, 636, 637); note on KH-522 (GitHub #61.1, already fixed); KH-779 filed 2026-10-29 from the product ruling on the 3.0.x relock FND locks — RT-001 gives no hint when a net's zones are unfilled, LOW; addenda on KH-484 (5 FND ids kept failing) and KH-685 (stacked NC pins, RTK Facet); KH-751..777 filed 2026-10-29 (+ KH-778 filed by the harness for the KH-575 KO-001 bounding-box residue) from the product 3.0.x Wave 4 Part B handoff — C14 board contact-model umbrella KH-751 (pad-to-fill misses, 11/296 false-incomplete boards; home of KH-701/702/710 (a)(b)(c)(i)), inferred stackup absent from output and EMC, PM-002 edge-mount keywords, ergogen nested modules / locked reference, IO-001 DNP / net identity / unclassified VBUS, schematic PDN DNP caps, PDN plane-area and grid residue, low-frequency PDN wording, EF rail-tap direction, legacy non-copper rule layers, legacy project rules reported, `.kicad_dru` expressions, custom-rule / annulus edge cases, per-side malformed courtyards, footprint parse edge cases, inferred-stackup edge cases, repeated stackup layer, small-patch return-path reference, KH-750 residue KH-771, SK-001 footprint text / rotated pads, `courtyard_clearance` for PM-001, `net_tie_pad_groups`, PD-003 dead key, board-setup annular width, TV-001 `drill_penalized`; KH-427 and 750 FIXED in 3.0.x Wave 4 Part B (unreleased, candidate `40b8ff3`), KH-364 track-in-zone half and KH-710 (d) fixed (entries stay open), KH-417 return-path half closed by construction (addendum on the FIXED entry), see FIXED.md; KH-711..749 filed 2026-10-28 from the product 3.0.x Wave 4 Part A handoff — case-insensitive mandatory fields, PCB rail set from board nets, op-amp bench below the feedback pole (gates KH-507), PNP bench never on (MEDIUM), P-ch `vth_V`, SPICE presence passes (KH-618 remainder, MEDIUM), `is_power_net_name` signal suffixes stop divider chains (MEDIUM), family Vref table values (MEDIUM), rail-sign readers (KH-675 remainder), CAN split termination (MEDIUM), VM-001 PG exemption unconditional, label-like regulator values, field-trim residue (KH-708 residue), reference nodes as rails, pre-KiCad 7 PCB rule / EG-001, `/x/PGND`, `ctx.rail_by_net` phase order, config-override consistency, regulator/half-bridge misdetections, DO-DET provenance, Vref rows awaiting datasheets, diff-pair ESD / USB-name / SPI-CAN / I2C VOL / family nickname / ERC / RC / LED / COMP / domain-advisory residues, alternate SPICE backends, op-amp `supply_min`, Monte Carlo parallel arms, bench-input residue, Vref key core cut, crystal residue, follow-up umbrella KH-749; KH-750 filed 2026-10-28 by the harness at the Wave 4 Part A gate — `/fpga-pg5/VCCINT` classed `interrupt` once KH-678 drops its rail match (KH-678 census); KH-675 (partly, → KH-719), 678, 699, 705, 708 (residue → KH-723), 672, 442, 676, 611, 612, 618 (partly, → KH-716), 619, 539, 669 FIXED in 3.0.x Wave 4 Part A (unreleased, candidate `b31d4ff`) and KH-709 closed as answered by ruling entry 54, see FIXED.md (commit-message corrections recorded under KH-675 / 678 / 676, the KH-509 CHANGELOG slip under KH-669); addenda on KH-548 / 667 / 483 / 707; KH-701..710 filed 2026-10-27 from the product 3.0.x Wave 3b Part B handoff §Asks 4 — net propagation onto net-less copper, custom-pad residue, instance-aware property writers, JLCPCB CPL convention reference, analyzer sheet-file case / KiCad 6 value settle, bom_manager diagnostics, unit-count semantics, mandatory-field whitespace trim, KiCad 5 `~` ruling question, follow-up umbrella; KH-417 / KH-426 FIXED in 3.0.x Wave 3b Part B (unreleased), see FIXED.md; KH-700 reclassified (R33 / R34: (a) budgeted class, (b) conformant, (c) → KH-708); addenda on KH-574 / 364 / 483; KH-699 / KH-700 filed 2026-10-27 by the harness at the Wave 3b Part A gate — `D_Zener` from an `*LED*` nickname typed `led` (false LR-001), `~` empty-field placeholder kept as a BOM footprint/datasheet on legacy schematics (MEDIUM); KH-679..698 filed 2026-10-27 from the product 3.0.x Wave 3b Part A handoff §Asks 4 — sibling-sheet driver ties, bus member fallbacks, hierarchical-label ERC, ktiger hierarchy join, PU-001 `MISO`, DO-DET port-name exemption, wired NC pins, bus group/quoted/mixed parsing, `~` pin names, bus-member naming, brace decode table, multi-root projects, unresolved text variables, CG-AUD by name, sheet-pin shape preference, follow-up umbrella KH-695; addenda on KH-483 / 667 / 669 / 671 / 677; KH-403 / KH-404 FIXED in 3.0.x Wave 3b Part A (unreleased) and KH-664 closed as conformant, see FIXED.md; KH-662 completion addendum in FIXED.md; KH-678 filed 2026-10-26 at the Wave 3 verdict — sheet net promoted to power by a same-named rail elsewhere (`/HVIL/HVIL_N`), Wave 4 group 1; KH-663..674 filed 2026-10-26 from the product 3.0.x Wave 3 handoff §Asks 4 — legacy buses, `E` decimal mark, EMC BE-001 origin distance, footprint Edge.Cuts outline, VM-001 heuristics, CS-DET set order, root hierarchical label fusion, LR-001 resistor association, same-net pad overlap, follow-up umbrella; KH-675..677 filed 2026-10-26 by the harness at the Wave 3 gate — negative regulator estimates on positive-named rails (Wave 4 group 1), SPICE zero-step transistor sweep (the spice-offline candidate failure), six legacy boards worse against their KiCad-5 netlist; KH-510..519, 560, 575, 576 FIXED in 3.0.x Wave 3 (unreleased) and KH-662 / 668 / 670 assigned FIXED-direct, see FIXED.md; KH-574 / KH-364 narrowed; KH-404 re-verified (reproduces); KH-653..661 filed 2026-10-25 from the product 3.0.x Wave 2 handoff §Asks 4 — `PH0`/`PH1` read as a regulator SW pin (MEDIUM), `RF-C10` typed resistor, EG-001 / GR-005 / CC-001+TW-001 follow-ups, `ThermalSkipped.reason` description, dead `has_esd` line, cross_verify keep/retire, LOW; KH-655 assigned FIXED-direct (test-plan / op-amp 2-hop / what_if order, fixed on discovery); KH-563..570, 582, 584, 591, 509, 607, 421 FIXED in 3.0.x Wave 2 (unreleased), see FIXED.md; KH-620 / 581 / 579 narrowed to their non-order halves; addenda on KH-484 and KH-529; KH-647..652 filed 2026-10-25 from the product 3.0.x Wave 1 residue — DNS rebinding (MEDIUM), NAT64/6to4 `is_global` bypass (MEDIUM), browser-fallback deadline/buffering/WebSocket gaps, `provider_mouser` unbounded `product_url` fetch, SPICE model denylist, `datasheet_extract_cache` fixed temp names / unchecked manifest joins, LOW; KH-497..505 FIXED in 3.0.x Wave 1 (unreleased), see FIXED.md, KH-507 left open by that round; KH-646 filed 2026-10-25 — split from KH-626 at the 3.0.x Wave 0 handoff: `distributor_offline` evicts only the selected tree's provider modules (sk/R6-F4), LOW; KH-626 FIXED on `v3.0.x-dev` `b3e4954` except that finding, see FIXED.md; KH-645 filed 2026-10-25 by the harness audit fix session — netlist oracle m68k-hbc splits 16 `/Bus/PEP/AD*` nets (oracle 4/5 since at least `0490c49`), MEDIUM; KH-644 filed 2026-10-25 by the harness audit fix session — PCB zone `fill_ratio` sums every filled layer over one layer's outline (1.83 on a two-layer zone), LOW, surfaced when the assertion engine stopped truncating fractional values; KH-643 filed 2026-10-25 by the main-repo agent — EMC SW-001 ignores `--standard` and discards its harmonic amplitude, MEDIUM; KH-497..642 filed 2026-10-25 from the external audit round 1 at `07b7fb1` — 30 static reviews in five bundles, every finding re-verified against the code, one entry per fix group; records and the wave plan in the main repo at `docs/audit/FIX-PLAN.md` and `docs/audit/0*/findings/VERIFICATION.md`; addenda added to KH-329, KH-331, KH-428, KH-432, KH-433, KH-437, KH-439, KH-442, KH-443, KH-470, KH-481, KH-482, KH-484, KH-487, KH-494; KH-480..496 filed 2026-10-24 from the v3 round-9b handoff §7 — the review-period bug-hunt deferrals, every claim re-verified in source at `07b7fb1` (19 confirmed / 4 partly), each with its budget or oracle re-freeze: failed-SPICE-run diagnostics (93 units), missing-sheet / truncated-input diagnostics, unannotated duplicate-ref collapse (1,598 units / 466 repos), GR-002 extents-only (MEDIUM), root-only `inputs` (4,261 multi-sheet units), suppressions only in EMC/thermal, `--parasitics` verbatim names, Mouser `""` key (4 frozen runs), SPICE cache hygiene, EMC `--severity` vocabulary, analysis_cache M3/M4, DigiKey 429, Action diff-base, three review-minor umbrellas; KH-479 assigned FIXED-direct 2026-10-24 to the review-period Critical A-C1 (analysis-dir containment, new in v3, fixed before release — see FIXED.md); KH-477 / KH-478 / KH-446 FIXED in round 9b (`cd2e49b` / `c6f4807`), KH-447 resolved for LT3514, see FIXED.md; KH-478 filed 2026-10-24 from the v3 round-9 handoff §11 — `emc_spice.run_distributed_pdn_spice` measurement tuples in the wrong shape → always `(False, None)`, temp dir never removed, no product caller, LOW; KH-472 / KH-464 / KH-466 / KH-475 FIXED in v3 round 9 (`ec81ca6`), see FIXED.md; KH-477 filed 2026-10-24 while fixing TH-077 — the SPICE model cache falls back to one global `/tmp` directory because `analyze_schematic.py` strips `file`; non-atomic manifest, cross-project leakage, LOW; KH-476 filed 2026-10-24 during the Checklist 11 `_KNOWN_FREQS` verification — the TPS62160 / TPS63000 keys miss the siblings of their own datasheets, 31 regulator findings default to 500 kHz, LOW; KH-470..475 filed 2026-10-23 from the v3 round-8 handoff §11 — thermal `title`+`summary` twin, `export_issues` severity vocabulary, `emc_spice.py` unquoted redirect without `cwd` (KH-463 sibling), RS-001 "carries power_in pins" wording on a name-admitted bootstrap-only rail, `lifecycle_audit` without `diagnostics`, Monte-Carlo per-trial fallback stderr noise; all pre-existing at `a0df172`, LOW; KH-454 / KH-455 / KH-463 FIXED in round 8 (`6222468`, `c598140`), see FIXED.md; KH-469 filed 2026-10-23 during the Checklist 11 SWITCHING_EFFICIENCY verification — three of the four `analyze_thermal.SWITCHING_EFFICIENCY` keys are unreachable and the schematic detector carries a third, different efficiency table; `ic_with_internal_regulator` regulators are costed as 85 %-efficient switchers, LOW; KH-468 filed 2026-10-23 during the Checklist 11 ADC-map verification — `_ADC_RESOLUTION_MAP` 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist, LOW; KH-467 filed 2026-10-23 during the Checklist 11 backlog pass — three divergent LED forward-voltage tables (`_LED_VF` / `_LED_VF_FLOOR` in domain_detectors, `_LED_VF_BY_COLOR` in validation_detectors) disagree per colour, LOW; KH-464..466 filed 2026-10-23 from the v3 round-7 handoff §11 — lifecycle_audit missing-input traceback, `is_cross_analysis_ground_name` exact-set policy (SGND/GNDPWR/GND_ISO/VSSA/`/Power/GND` not ground), `analyze_gerbers` exit 0 on a nonexistent dir; all pre-existing, verified at 0490c49, LOW; KH-463 filed 2026-10-23 at the v2.3.2 corpus regen — SPICE testbench `.control` `echo … > <path>` redirect unquoted, every measurement silently skips when the workdir path has whitespace or `,`/`&`/`'`/non-ASCII, the user-facing `analysis/<run>/spice_work/` default inherits the project path, MEDIUM; KH-456..462 filed 2026-10-22 from the SacMap rev2 run-9 soak at the v2.3.2 pre-tag `4701c26` — fab_release_gate counts `G***` logo footprints (false FAIL), silk revision regex misses `rev2`, `capability_mode` `datasheet_coverage_pct` is a hard-coded stub, `audit_pwr_flags` ignores `power_in` pins off named rails (ERC `power_pin_not_driven` ×3 unseen), EMC DC-002 fires on a part-numbered ESD array (dupes UC-001), `cross_domain_signals.needs_level_shifter` stale after KH-424, `datasheet_verify` rc 1 for warnings; riders on KH-431/432/436; all code-verified by the main-repo agent; KH-455 filed 2026-10-22 at the v2.3.2 backport gate — PP-001 `(ref, pin_number)` dedup masks a second symbol's power pin on unannotated `U?` designs, the gate's one residue unit, LOW; KH-454 filed 2026-10-22 at the v2.3.2 backport adoption — RS-001 fires on a bootstrap-only net whose sole `power_in` pin is the BST/BOOT pin, LOW, with the two GitHub #55 riders; KH-450..453 assigned 2026-10-22 FIXED-direct — GitHub #52–#55 / PRs #56–#59 by EldarPolitkin on `main` @ 4701c26, see FIXED.md; KH-449 filed 2026-10-16 at the v3 round-5 full-chain gate — pcb `--full` exceeds the 600 s cap on starshipraider MAXWELL both sides, LOW; KH-447 addendum: LT3514 is a ≥ 20 GB memory blow-up, OOM-killed under the 600 s cap; KH-448 filed 2026-10-16 at the v3 round-4 gate — hierarchy-mode `analyze_schematic.py` ~3 GB RSS on BerkeleyLab/Marble, both sides equal, LOW; KH-446/447 filed 2026-10-15 at the v3 round-2 reply per ruling Q3 — empty-input pcb traceback (hackclub/OnBoard placeholders), schematic 120 s timeouts on three hierarchical roots (discrete-nes ×2, LT3514); KH-445 filed 2026-10-15 at H0 plan 4 — `EQ-042` tags two different equations, LOW; KH-444 assigned 2026-10-14 FIXED-direct — PR #51 AM-001 `<domain>_max` key lookup, imrcly, see FIXED.md; KH-443 filed 2026-10-14 from GitHub #50 — net ties not bridged by RS-001/PP-001 DC-continuity audits, MEDIUM; KH-442 filed 2026-10-06 at the v2.3.1 regen — behavioral opamp model gain 0 false SP-WARN; KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
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
KHPA finding ID). Next TH number: **TH-123** (TH-122 filed 2026-11-19 — BUGFIX-KH-307-02 / -03 lose their anchor at Wave 12c; TH-121 filed and fixed 2026-11-17 — the netlist oracle dropped `(pin "")` nodes / read blind netlists as same; TH-120 filed 2026-11-16 — `run_thermal.py` summary reads pre-harmonization keys; TH-119 filed 2026-11-16 — concurrent runners race on the `units.jsonl` rotation; TH-118 filed 2026-11-16 — `add_repos.py` pre-add not atomic, 13 duplicate pinned lines in repos.md; TH-117 filed and FIXED 2026-11-15 — `validate_candidates` footprint counter missed KiCad 5 `(module`, tab-indented KiCad 8+ and generated boards, see FIXED.md; TH-114 FIXED 2026-11-15 — `--check-updates` keeps a per-row failure reason, retries failures once, and `--github-api` resolves GitHub through gh GraphQL, see FIXED.md; TH-116 filed and FIXED 2026-11-15 at the same batch — `add_repos.py` without `--resume` crashed on its first result, see FIXED.md; TH-115 filed and FIXED 2026-11-15 at the v3.0.3 first corpus batch — the schematic detector summary re-read every corpus output, see FIXED.md; TH-114 filed 2026-11-15 at the v3.0.3 Track H update scan — `--check-updates` reads GitHub throttling as `error`, LOW; TH-113 filed and FIXED 2026-11-13 at the v3.0.2 VALIDATION draft (generator read KH-1000+ as three-digit ids); TH-044 FIXED 2026-11-13 at the v3.0.2 regen (catalog + cross-sections regenerated); TH-112 filed and FIXED 2026-11-13 at the same regen (`seed.py --prune-stale` skipped STRUCT files), see FIXED.md; TH-049 and TH-063 FIXED 2026-11-11, TH-109 and TH-064 FIXED 2026-11-11, see FIXED.md; TH-111 filed 2026-11-11 from the TH-109 triage — check paths cannot reach dotted net names, LOW; TH-110 filed 2026-11-07 at the v3.0.2 Wave 11b-1 registry rescan — `audit_constants.py` reuses retired `CONST-NNN` ids for new constants, LOW; TH-109 filed 2026-11-06 from the TH-105 triage — 144 live FND locks with a check shape that cannot fail or reads the wrong finding; TH-107 / TH-108 filed 2026-11-06 at the v3.0.2 kickoff while classifying the nine standing non-passing locks for VALIDATION.md — 36 assertions never load their output (2 from a doubled `file_pattern` prefix), and the nine standing locks were never reviewed (7 stale, the analyzer now matches KiCad); earlier: TH-106 filed 2026-11-03 — `generate_analytics.py` issue counts read only `### <id>` headings, the TH-104 undercount in a second tool, LOW; TH-105 filed 2026-11-03 at the v3.0.1 regen — 360 FND locks on INCORRECT-marked findings are not aspirational, some pin the reported defect (six caught as Wave 5 KH-484 `aligned` flips); audit + rule recorded, MEDIUM; TH-104 filed and fixed 2026-11-03 at the v3.0.0 release prep — `generate_validation_md.py` counted only `### <id>` headings, so `## <date> — <id>` closures were dropped and the filed total shrank, see FIXED.md; TH-103 filed and fixed 2026-11-03 at the Waves 8c + 8b push — the hash-seed determinism test compared `elapsed_s`, see FIXED.md; TH-102 filed and fixed 2026-11-01 at the 3.0.x Wave 7 close — the fixture set had no multi-unit schematic (a placed symbol with unit > 1), so product `test_model_records` could not pin per-unit records; `tests/fixtures/multi-unit/dual_opamp.kicad_sch` + `tests/test_multi_unit_fixture.py`, see FIXED.md; TH-101 filed 2026-10-31 at the 3.0.x Wave 5 gate — no profile exercises gerber `--full` connectivity, the Task 52 class is gate-blind harness-side, LOW; TH-100 filed 2026-10-29 at the relock rulings — 235 aspirational FND assertions use operators `checks.py` does not know; TH-099 filed 2026-10-29 at the 3.0.x relock — emc / thermal pair a schematic with an orphan pre-hash pcb output; TH-098 filed and fixed 2026-10-26 — tool-gated skips (pdftotext / ngspice) failed the required-tier skip guard on runners without the tools; listed in `tests/known_skips.json`, see FIXED.md; TH-097 filed and fixed 2026-10-26 — `run_spice.py` checked for ngspice before validating the selection, product CI red at pin `bd551df5b41`, see FIXED.md; TH-096 filed 2026-10-26 at the Wave 3 gate — the field comparator holds every delta in memory, ~55 M deltas exhausted the box, MEDIUM; TH-095 filed and fixed 2026-10-26 — `run_netlist_oracle.py` did not resolve a relative `--kicad-happy`, see FIXED.md; TH-093 and TH-094 filed and fixed 2026-10-25 at the wave 10 final review — bare-list assertion files crash the coverage and health report counters; `audit_equations.py untagged` indicator order follows PYTHONHASHSEED, both LOW, see FIXED.md; TH-091 filed and fixed 2026-10-25 during wave 10 planning — `generate_analytics.py` ignores `KICAD_HAPPY_TESTHARNESS_DATA_DIR`, see FIXED.md; TH-092 filed and fixed 2026-10-25 during wave 10 planning — `audit_equations.py` reads sources as UTF-8 text and `find_untagged` swallows `SyntaxError`, see FIXED.md; TH-090 filed and fixed 2026-10-25 during wave 10 planning — `refresh_findings.py` counted drift's no-checkable-items sentinel as an item and reported such findings as current, see FIXED.md; TH-089 filed and fixed 2026-10-25 by the harness audit fix session — `generate_catalog.py` counted the `capability_mode.json` sidecar as a schematic/PCB/EMC/SPICE output, see FIXED.md; TH-080..088 filed 2026-10-25 from the harness external audit round 1 — budgeted-kind worker exceptions, ledgered-timeout coverage, `discover.py --repo` global-manifest shrink, silent assertion-file drop, null/`[]` required-field locks (all HIGH, gate/assertion false-pass paths), constants corpus-hit names, `audit_equations --diff` no-op, `validate_design_intent` multi-repo scope, `analyze_bom_mismatch` layout (LOW); records `docs/audit/0*-harness-*/findings/VERIFICATION.md`, plan `docs/audit/HARNESS-FIX-PLAN.md`; TH-079 filed 2026-10-25 from the external audit round 1 — `generate_validation_md.py` category table and total use different denominators (1,855 = the aspirational count), LOW; TH-078 filed 2026-10-24 at the v3 round-9b gate — no "debt resolved" disposition: a ledgered unit the candidate fixes fails `skips_ok`, `strict_clean` and the strict comparator (`missing_a`), so the structural criterion cannot pass mechanically and the response builder carries a hand-written exception, LOW; TH-065, TH-066 + TH-077 FIXED 2026-10-24, see FIXED.md; TH-077 filed 2026-10-24 at the v3 round-8 spice-offline gate — `run_spice.py` output is not deterministic run-to-run: `simulation_results[*].model_note` flips `lookup:<MPN>` ↔ `cache:<MPN>` for the same product and inputs (132 of 8,829 reports between two baseline passes), LOW; TH-076 fixed-on-discovery 2026-10-23 during the Checklist 11 backlog pass — `audit_constants.py scan` dropped and re-added every constant whose file moved without a `relocate --map` (rounds 2/3), losing 41 verification records incl. `_REGULATOR_VREF` 55/114 and `_CAP_ESL` 7/7; the registry had also not been rescanned since round 5, see FIXED.md; TH-075 fixed-on-discovery 2026-10-23 at the v2.3.2 corpus regen — `run_spice.py` per-unit `--workdir` carried raw repo/file names into ngspice, 18,464 sims silently skipped on 5,198 corpus units, directory name now sanitized + digest, see FIXED.md; TH-074 fixed-on-discovery 2026-10-22 at the v2.3.2 backport gate — long-run waiters stalled on a `pgrep -f` self-match and on a zombie PID; `tools/wait_for_run.py` + RUNBOOK 26k + full-chain `done.json` marker, see FIXED.md; TH-073 fixed-on-discovery 2026-10-17 at the v3 round-6 gate preflight — `run_corpus_gate.py` accepted analyzer-less profiles (`spice-offline`, the new `distributor-offline`) and would have run a zero-unit gate, guard added, see FIXED.md; TH-072 fixed-on-discovery 2026-10-16 at the v3 round-5 gate preflight — `full-chain` profile declared no schematic analyzer, Phase B ran no chained unit, see FIXED.md; TH-071 filed 2026-10-16 at the v3 round-4 gate — `run_corpus_gate.py --jobs` not memory-aware, hierarchy profile at 32 jobs OOMs the box, LOW; TH-070 filed 2026-10-15 at the v3 round-2 reply — scan-coverage identity by line/file yields ~150 false losses per structural round, MEDIUM; TH-069 FIXED 2026-10-15 at the v3 round-3 reply — discover.py regular-file filter + manifest regen, see FIXED.md; TH-068 filed 2026-10-15 at H0 plan 6 — fixture-lane A/A chained envelopes unverifiable after the basetemp move, LOW; TH-067 filed 2026-10-15 — batch-runner pool workers outlive a killed parent (the TH-063 mechanism), MEDIUM; TH-066 filed 2026-10-15 at the H0 plan 4 final review — audit tools walk 58 of the 90 scanner files; TH-065 filed 2026-10-15 at H0 plan 4 — audit_constants function-scope `name:line` identity churns the registry; TH-064 filed 2026-10-15 — emc/thermal/spice `--resume` refused until identity-based resume exists; TH-063 filed 2026-10-14 — mutating runner launched against the live tree from a TDD RED step, 16,909 emc outputs rewritten, no measurable impact; TH-055 and TH-059 (harness half) fixed 2026-10-15 (H0 plan 2), see FIXED.md; TH-062 filed 2026-10-14 — 58 print-and-return vacuous skip paths in required-tier smoke files; TH-061 filed 2026-10-14 — test_datasheet_db_cli.py fallback fixture writes under repos/; TH-060 filed 2026-10-14 — test_kh393_power_rails_threaded premise stale since PR #44, now strict xfail; TH-052/053/058 fixed 2026-10-14 (H0 plan 1, honest pytest collection), see FIXED.md; TH-059 filed 2026-10-06 at the v2.3.1 regen — batch SPICE side effects: spice/ dirs in repos/ + live DigiKey lookups; TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 FIXED 2026-10-15 at H0 plan 5 — generator rewritten as grouped reconciliation, see FIXED.md; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 386 open issues (381 KH + 5 TH).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-1339: `_FIXED_SUFFIX_FAMILIES` gives LM2595 / LM2574 / LM2675 only the "5" code although their datasheets also list 12 V (and 15 V for LM2574) (`fixed-suffix-family-12v-gap`)

**Severity:** LOW (reach 0: the corpus carries only the -5 / -3 forms of these three families)
**File:** `skills/kicad/scripts/kicad_core/parts.py:306-308` (`_FIXED_SUFFIX_FAMILIES` rows LM2595, LM2574, LM2675)
**Discovered:** 2026-11-19, harness agent verifying the Wave 12c constants (`results/v303_w12c_gate_aux/verdicts/consts/verdicts.json`); confirmed by the product in its 12c acceptance (12d)
**Symptom:** the rows carry only `{"5": 5.0}`, while their own comments and the p1 version lists (SNVS122C LM2595: 3.3 / 5 / 12 V + ADJ; SNVS104F LM2574: 3.3 / 5 / 12 / 15 V + ADJ; SNVS129G LM2675: 3.3 / 5 / 12 V + ADJ) include 12 V (and 15 V). LM2596 / LM2575 / LM2576 carry 12 (and 15). A `-12` / `-15` suffix on these three families therefore reads no fixed voltage.
**Fix direction:** add `"12": 12.0` to the three rows and `"15": 15.0` to LM2574, cited to the same p1 lists. Wave 12d.

### KH-1338: VD-003 reads capacitor values on resistor symbols as sub-µΩ resistances and reports dissipations of 10^8-10^11 mW (`harness-vd003-cap-value-on-resistor`)

**Severity:** LOW (pre-existing; error-grade text, 2 records)
**File:** `skills/kicad/scripts/kicad_core/values.py` (`parse_value` for `component_type='resistor'`) and the VD-003 derating check
**Discovered:** 2026-11-19, harness agent verifying the Wave 12c fixed-on-filing `vd003-subohm-series-between-rails`
**Symptom:** Simonhajd/Triton-Float: R3 / R4 on a resistor symbol carry the values `0.1uF` / `10uF`; the parser reads 1e-7 Ω and 1e-5 Ω, and VD-003 reports 108,900,000,000 mW and 1,089,000,000 mW, at `ca59d562` and at `ea5f7fd1`.
**Fix direction:** a resistor value with an F (or H) unit reads none.

### KH-1337: VM-001 reads a negative regulator's EN net as a positive-voltage domain: new false error on loxodes/vna bias_controller `VSS_SW_EN` (`harness-vm001-negative-domain-sign`)

**Severity:** LOW (1 error-grade record, new in Wave 12c)
**File:** `skills/kicad/scripts/signal_detectors.py` (VM-001 voltage-domain check)
**Discovered:** 2026-11-19, harness verification of the Wave 12c close of KH-964 at `ea5f7fd1`
**Symptom:** loxodes/vna `breakouts_bias_controller_bias_controller_bias_controller.kicad_sch`: at `ea5f7fd1` VM-001 error "Net VSS_SW_EN: 6.0V / 3.3V domain crossing without level shifter"; none at `ca59d562`. U601 is a −6 V regulator; once `VSS_SW_EN` stopped reading as ground (Wave 12c `c4c5fd11`, class `g2-names`, KH-925 / KH-964) the domain check took the regulator's domain as +6 V. The record is claimed by `g2-names` (VM-001 is in its rule list) but is not in `known-false-wave12c.md`.
**Fix direction:** carry the sign of a negative regulator's domain into VM-001 (or skip negative domains), the KH-1123 multi-supply area.

**2026-11-19 (product 12c acceptance):** confirmed in the product's own tip run (0 at `ca59d562`, 1 at `ea5f7fd1`); Wave 12d with the VM-001 supply group.

### KH-1336: the SPICE regulator_feedback `out_adj` record reports `vfb_V` as the ADJ voltage while the delta is OUT-ADJ against Vref (`spice-out-adj-vfb-presentation`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 54 `spice-out-adj-vfb-presentation`); checked by the harness at `ea5f7fd1`

 - Symptom: the SPICE regulator_feedback `out_adj` record reports `vfb_V` as the ADJ voltage while the delta is OUT-ADJ against Vref. Jaxc Magna U803 LM350 shows `vfb_V` 1.25 beside a 200 % delta (the fail itself is true). Presentation only, pre-existing.
 - Evidence: `X/task-33-report.md`.

**Harness check (`ea5f7fd1`):** spice_results.py:809/818 report vfb_V as V(ADJ) while :849-852 compute the delta from Vin - V(ADJ) for out_adj. No spice output in D to check Jaxc U803 numbers; code matches the statement.

### KH-1335: DC-DET derating takes its applied voltage only from the regulator Vout, never from the rail name (`3V3`) (`dcdet-derating-rail-name`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 53 `dcdet-derating-rail-name`); checked by the harness at `ea5f7fd1`

 - Symptom: DC-DET derating takes its applied voltage only from the regulator Vout, never from the rail name (`3V3`). With R-P1's 205 Vouts gone, 132 decoupling records lose their derating. Pre-existing.
 - Evidence: `X/task-34-report.md` harness ask 3.

**Harness check (`ea5f7fd1`):** schematic/pipeline.py:700-777 apply_capacitor_derating builds rail_voltage only from power_regulators output_rail + estimated_vout; decoupling_analysis rails without a regulator Vout are skipped. 132/205 not re-measured.

### KH-1334: RS-001's wording split (`signal_detectors.py:5301`) finds power symbols by a `#` reference prefix (`power-symbol-identified-two-ways`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 52 `power-symbol-identified-two-ways`); checked by the harness at `ea5f7fd1`

 - Symptom: RS-001's wording split (`signal_detectors.py:5301`) finds power symbols by a `#` reference prefix; the PWR_FLAG audit finds them by `type == "power_symbol"`. A power symbol whose reference does not start with `#` counts in RS-001 as a part's power input ("carries power_in pins", deterministic). Pre-existing.
 - Fix direction: test the component type in RS-001 too (12j predicate consolidation).
 - Evidence: `D/reviews/final-S.md` M3.

**Harness check (`ea5f7fd1`):** signal_detectors.py:5309-5311 part_power_in excludes components whose ref starts with '#'; audits.py:139 uses type == 'power_symbol'. This is the residue of the KH-1024 close (b58da404 keyed the fix on the '#' prefix); cite KH-1024 in the filing. Note: Line :5311 (part_power_in filter), not :5301.

### KH-1333: on a sub-sheet read alone, `audit_pwr_flags` (`schematic/audits.py:145`) takes only hidden `power_in` pins as global (`audits-visible-power-in-global`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 51 `audits-visible-power-in-global`); checked by the harness at `ea5f7fd1`

 - Symptom: on a sub-sheet read alone, `audit_pwr_flags` (`schematic/audits.py:145`) takes only hidden `power_in` pins as global. `connectivity.py:902` also joins a power-flagged library part's visible pin (`_global_power_part`). Such a net would still warn.
 - Reach: 0 / 400 standalone units.
 - Fix (one line): `(p.get("hidden") or c.get("_global_power_part"))`. It can go in the `pwrflag-standalone-rails` FIXED note instead.
 - Evidence: `D/reviews/final-S.md` M1.

**Harness check (`ea5f7fd1`):** schematic/audits.py:145-147 global_pins (statement starts at :145) takes only power_in pins with p.get('hidden'); connectivity.py:902 joins (pin.get('hidden') or comp.get('_global_power_part')); _global_power_part set at schematic/pipeline.py:1088. Reach 0 not re-measured. Harness (Wave 12c fixed-on-filing check of `pwrflag-standalone-rails`): a second mismatch in the same pair: the audit treats an unnamed hidden `power_in` pin as global, while connectivity joins only named pins.

### KH-1332: a positive family written with a decimal suffix (`LM2596S-5.0`, `LM2575-5.0`) counts as a sign-less suffix, so on a negative input it would be negated (`negative-input-decimal-suffix`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 49 `negative-input-decimal-suffix`); checked by the harness at `ea5f7fd1`

 - Symptom: a positive family written with a decimal suffix (`LM2596S-5.0`, `LM2575-5.0`) counts as a sign-less suffix, so on a negative input it would be negated. Reach 0.
 - Evidence: ledger Task 40 deferred minor.

**Harness check (`ea5f7fd1`):** signal_detectors.py:2310-2315 negates a positive fixed_suffix Vout on a negative input unless fixed_vout_is_table_code; probe: LM2596S-5.0 and LM2575-5.0 table_code False (would negate), LM2596S-5 / LM2575-5 True (none). Reach 0 not re-measured.

### KH-1331: the one-digit arm of the fixed-suffix reader (`kicad_core/parts.py:519-525`, lookahead `(?=[^0-9.]|$)`) accepts a digit followed by any letter, so … (`one-digit-suffix-letter`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 48 `one-digit-suffix-letter`); checked by the harness at `ea5f7fd1`

 - Symptom: the one-digit arm of the fixed-suffix reader (`kicad_core/parts.py:519-525`, lookahead `(?=[^0-9.]|$)`) accepts a digit followed by any letter, so `LM2596_5A` (a current) reads 5.0 V. Probe at `ea5f7fd1`: 5.0 (1.23 lookup at base). Reach 0 per the Task 39 key probe. Guard idea: `(?=[^0-9.A]|$)`.
 - Evidence: `D/reviews/final-B.md` M5.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref('LM2596_5A') = (5.0, fixed_suffix) at ea5f7fd1, (1.23, lookup) at base; one-digit arm parts.py:519-525.

### KH-1330: P-notation after a separator reads a version or a pin-row name as a voltage (`p-notation-version`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 47 `p-notation-version`); checked by the harness at `ea5f7fd1`

 - Symptom: P-notation after a separator reads a version or a pin-row name as a voltage. Introduced in the range by `b5d12338`. `USB_2P0` 2.0, `PCIE_3P0` 3.0, `PMOD_6P2_1` 6.2 (Icenowy elf2: GPIO signal nets), `LED_RGB_4P6028_REVERSE`. `USB3P0` stays none.
 - Reach: 0. No `USB_2P0`-style net in the corpus; elf2 and 32blit have no `rail_voltages` change on a P-named key.
 - Evidence: `X/fix-wave-report.md` item 14; `D/reviews/final-fixwave-rereview.md` (f).

**Harness check (`ea5f7fd1`):** parse_voltage_from_net_name at ea5f7fd1: USB_2P0 2.0, PCIE_3P0 3.0, PMOD_6P2_1 6.2, LED_RGB_4P6028_REVERSE 4.6028, USB3P0 None; all None at base. Side effect of the KH-1086 close (b5d12338).

### KH-1329: a designator-shaped Value (`IC1`, `REG1`, `VR1`, `PS1`, `D1`, `Q1`) counts as another part, so a fixed symbol's voltage is not read (`designator-value-on-fixed-symbol`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 46 `designator-value-on-fixed-symbol`); checked by the harness at `ea5f7fd1`

 - Symptom: a designator-shaped Value (`IC1`, `REG1`, `VR1`, `PS1`, `D1`, `Q1`) counts as another part, so a fixed symbol's voltage is not read. Probe at `ea5f7fd1`: `REG1` on `AMS1117-3.3` → none (3.3 at base). The four loops now agree; 12b's two loops already did this.
 - Reach: 0 records in the census.
 - Fix considered: a letters+digits test. Waited: it cannot tell `U1` / `REG1` from short real parts (`TL431`, `LM78`) without a new heuristic.
 - Evidence: `D/reviews/task-34-review.md` M2.

**Harness check (`ea5f7fd1`):** Probe: 'REG1' / 'IC1' on Regulator_Linear:AMS1117-3.3 -> (None, '') at ea5f7fd1, (3.3, fixed_suffix) at base. Introduced in range (with the KH-1273 close, bb6fc3e0).

### KH-1328: `SPX1117M3-L-3-30` reads 3.0 V fixed through the generic suffix loop (at base too (`suffix-trailing-digit`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 45 `suffix-trailing-digit`); checked by the harness at `ea5f7fd1`

 - Symptom: `SPX1117M3-L-3-30` reads 3.0 V fixed through the generic suffix loop (at base too; probe at `ea5f7fd1` 3.0). Reach not measured.
 - Evidence: ledger Task 33 re-review.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref('SPX1117M3-L-3-30') = (3.0, fixed_suffix) at base and tip.

### KH-1327: positive non-ST 78xx codes read no fixed voltage (`78xx-other-vendor-prefixes`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 44 `78xx-other-vendor-prefixes`); checked by the harness at `ea5f7fd1`

 - Symptom: positive non-ST 78xx codes read no fixed voltage: `(MC|UA|KA|NJM|AIP)78[LM]?\d{2}`. Top forms: MC7815C 12, KA78M05_TO252 11, uA7805 9, MC78L08_TO92 6, MC7805 4, UA78M33 4, UA78M05 4, `7805` / `7815` on uA78xx symbols 4 each. 7 of Task 34's lost same-family Values stay unread (K78 / UA78 / MC78 / AIP78). KA79xx / NJM79xx negatives are also unread (no citable datasheet; corpus 0).
 - Reach: ≤ 111 PR-DET / 95 units (upper bound; some Values name another part).
 - Waited: not surveyed; adding a class at the last task without a budget (ledger ruling).
 - Evidence: `X/task-40-report.md` positive-prefix reach.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref at ea5f7fd1 (and base): MC7815C, KA78M05_TO252, uA7805, MC78L08_TO92, MC7805, UA78M33, UA78M05, AIP7805, NJM7805, KA7905, '7805' on Regulator_Linear:uA7805 -> (None, ''); L7805 and LM7805 -> 5.0.

### KH-1326: channel-style names `V-1`, `VSS-1`, `AVSS-0` read inverting at base and tip (`v-dash-channel-inverting`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 42 `v-dash-channel-inverting`); checked by the harness at `ea5f7fd1`

 - Symptom: channel-style names `V-1`, `VSS-1`, `AVSS-0` read inverting at base and tip. Reach 0.
 - Evidence: ledger Task 36 re-review.

**Harness check (`ea5f7fd1`):** _NEG_SUPPLY_DASH (signal_detectors.py:1744, (?:^|[_\s])(?:V|VEE|AVEE|VSS|AVSS|VNEG)-\d) matches V-1, VSS-1, AVSS-0, so a regulator output net with such a leaf sets inverting (:2265). Reach 0 not re-measured.

### KH-1325: a `<v>_NEG` / `<v>_POS` or `<word>-<v>` / `<word>+<v>` pair can name the two terminals of one input, not a split supply (`neg-pos-terminal-names`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 41 `neg-pos-terminal-names`); checked by the harness at `ea5f7fd1`

 - Symptom: a `<v>_NEG` / `<v>_POS` or `<word>-<v>` / `<word>+<v>` pair can name the two terminals of one input, not a split supply.
   - mfkiwl/KiwiSDR_PCB `kiwi.sch` and `kiwi.BeagleBone.sch` `5V_NEG` is the DC jack's GND / GNDBK return before a choke; it reads +5 (as at base) because the `_NEG` / `_POS` form was dropped (ledger ruling).
   - ExoFlex-Inc/Electrique `CNC-12V` beside `CNC+12V` reads −12 in `split_rail_voltages` (a connector return; not a rail, so no output moves).
   - `V10N` / `V10P` would read ±10 (reach 0).
 - Fix considered: a negative half carrying a ground-named connector pin is a return (needs pin data in `split_rail_voltages`). Waited.
 - Evidence: `X/task-35-report.md` concern 1; `D/reviews/task-35-review.md` M-3, M-4.

**Harness check (`ea5f7fd1`):** Probe at ea5f7fd1: split_rail_voltages(['CNC-12V','CNC+12V']) = {'CNC-12V': -12.0}; ['5V_NEG','5V_POS'] = {} and parse_voltage_from_net_name('5V_NEG') = 5.0 (KiwiSDR ruling); ['V10N','V10P'] = +/-10. Residue of the KH-967 close.

### KH-1324: the power budget's per-IC default currents inflate rail loads, which 12c's thermal and TW-001 now read (`budget-per-ic-default-current`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 40 `budget-per-ic-default-current`); checked by the harness at `ea5f7fd1`

 - Symptom: the power budget's per-IC default currents inflate rail loads, which 12c's thermal and TW-001 now read:
   - tengigabytes/MokyaLora `VCC_1V8` at 0.9 A from 8 ICs budgeted 120 mA each (7 of Task 31's 35 TW-001 adds rest on such inflation);
   - Bulion/MIDI2PWMv2 U35, mahmoud-elghamry thermo40 U402, jumpstarter-dev dutlink U2 thermal errors (flat 10 / 50 mA);
   - the TW-001 max-of-both measurement (KH-1083 addendum): Duet3D Duet2 785 mA (ATSAM4E8E + 74HC125 + 74HCT02 at 250 mA), Churrosoft OpenEFI 13 sensor-connector symbols at 80 mA (1,065 mA), espena doorbell 74LVC2G14 / DS3231M at 200 mA.
 - Evidence: ledger Tasks 30, 31, 39; `D/patches/tw001-budget-fix.patch`.

**Harness check (`ea5f7fd1`):** tengigabytes/MokyaLora hardware_kicad_MokyaLora.kicad_sch power_budget VCC_1V8 = 900 mA, 8 ICs: 7 x 120 (IM69D130, APS6404L, W25Q128JW, TESEO-LIV3FL, LPS22HH, LSM6DSV16X, LIS2MDL) + RP2350B 60. Not KH-1083 (cap proxy) nor KH-432; other examples not re-checked.

### KH-1323: Spark-AE `LED_ARGB_Amicc` (numbered pins) has no budget load at base or tip (a flat 5 mA would be right) (`led-numbered-pin-rgb`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 39 `led-numbered-pin-rgb`); checked by the harness at `ea5f7fd1`

 - Symptom: Spark-AE `LED_ARGB_Amicc` (numbered pins) has no budget load at base or tip (a flat 5 mA would be right). Colourless numbered-pin RGB LEDs default to 2.0 V per die (survey B §B3.5).
 - Evidence: ledger Task 29; `X/task-29-report.md`.

**Harness check (`ea5f7fd1`):** Spark-AE-PCB and -UI: LED1/LED2 'A-SP1943B1GHR6C-C01-2T' (clectric-diy:LED_ARGB_Amicc..., pins 1-4 'unspecified', pin 3 on +3.3V) absent from power_budget at base and tip. Residue of KH-432 (closed this wave: 'addressable at 5 mA'); the KH-432 close should note numbered-pin addressable LEDs are not recognised.

### KH-1322: DNP or not-fitted parts count as EN drivers (`dnp-en-driver`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 37 `dnp-en-driver`); checked by the harness at `ea5f7fd1`

 - Symptom: DNP or not-fitted parts count as EN drivers.
   - 18 flips where every EN resistor is DNP read `always_on` where `floating` is right: Gregification ×9, crsknr ×4, demeter, dimembermatt, dimsumlabs. Base also wrong; the sleep result is the same.
   - tpecar/nl2sch ebaz4205 U72 TPS51200 pulled up through R2617 valued `NC` (and U72 valued `NC`) reads `always_on` (Task 32, declared).
   - arjunven/STM32_Nixie `pcb_STM32_Nixie` and `pcb_usb_conn` U9 TPS2552D `~{EN}`: the pull-up R52 is DNP and the fitted pull-down R53 enables the active-low EN. It reads `controlled` (as base); truly always enabled.
 - Evidence: ledger Task 27; `X/task-32-report.md`; ledger fix-wave rulings.

**Harness check (`ea5f7fd1`):** arjunven/STM32_Nixie pcb_STM32_Nixie U9 TPS2552D ~{EN}: en_source controlled, en_driven_by [R53, R52], R52 'RES_DNP_0603' dnp True. tpecar/nl2sch ebaz4205 U72 (Value 'NC') en_source always_on via R2617 Value 'NC'. 18-flip reach not re-measured. Sibling DNP KHs (KH-1003/1011/1065/1210) are other detectors; not a duplicate.

### KH-1321: the ESD-IC path drops the supply pins of a single-line power-rail TVS IC once its return is ground (`esd-ic-rail-tvs-dropped`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 36 `esd-ic-rail-tvs-dropped`); checked by the harness at `ea5f7fd1`

 - Symptom: the ESD-IC path drops the supply pins of a single-line power-rail TVS IC once its return is ground. brainmachine U2 TVS0500DRV: IN pins on `First SW capacitor set` (a 5 V regulator output), GND on `Earth_Protective`. Its PD-DET record is lost since Task 8 made that net ground (the same as a GND-named twin, which also gives none). Affects GND boards too.
 - Evidence: `X/task-10-report.md` concern 2; ledger Task 10 ruling.

**Harness check (`ea5f7fd1`):** brainmachine U2 'TVS 05V': IN x3 on 'First SW capacitor set', GND x4 on Earth_Protective; base PD-DET esd_ic + DO-DET 'missing decoupling on Earth_Protective' -> tip none. Distinct from KH-1215 (closed this wave: Earth-only return clamp_net).

### KH-1320: a USB-PD controller with an empty Value gives the summary `U2 ()` (Nixie HUSB238 (`ppdet-summary-empty-value`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 34 `ppdet-summary-empty-value`); checked by the harness at `ea5f7fd1`

 - Symptom: a USB-PD controller with an empty Value gives the summary `U2 ()` (Nixie HUSB238; base `U2 (GND)` was also wrong). Fall back to the library name.
 - Evidence: ledger Task 15.

**Harness check (`ea5f7fd1`):** Fish-in-a-Barrel/Nixie (both checkouts) at ea5f7fd1: PP-DET 'Power path U2 () [usb_pd_controller]' on the root and the USB PD sheet; base read 'U2 (GND)' on the root and 'U2 (5.1k)' on the USB PD sheet. U2 Value '' lib_id Interface_USB_:HUSB238. PU-001 descriptions on the same unit read 'on U2 ()' at base and tip (also fsanzeni FSC-BT631D U3). **Correction:** Reach 4 PP-DET records (2 checkouts x root + USB PD sheet). Base was 'U2 (GND)' / 'U2 (5.1k)'. The same empty-Value '()' also appears in PU-001 descriptions (pre-existing); the library-name fallback should cover both.

### KH-1319: an Rd built from two resistors in series is not read as one (`cc-series-rd`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 33 `cc-series-rd`); checked by the harness at `ea5f7fd1`

 - Symptom: an Rd built from two resistors in series is not read as one. obsilab/Quanta75 ×2 (4k99 + 120R) read CC status fail (status only).
 - Fix considered: a series walk. Waited: new reach.
 - Evidence: `D/reviews/task-14-review.md` I1.

**Harness check (`ea5f7fd1`):** obsilab/Quanta75 BareRP2040 and RP2040Stamp units: J1 CC1 R4 4k99 -> R1 120R, CC2 R2 4k99 -> R3 120R; usb_c_cc_status cc*_resistor 4990, to_ground False, status fail (wrong_cc_value).

### KH-1318: the LED current-limit scan (`domain_detectors.py:4902` / `:4908`, earlier `:4923`) is resistor-only but calls `parse_value` untyped (`led-limit-typed-caller`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 32 `led-limit-typed-caller`); checked by the harness at `ea5f7fd1`

 - Symptom: the LED current-limit scan (`domain_detectors.py:4902` / `:4908`, earlier `:4923`) is resistor-only but calls `parse_value` untyped. It was outside the surveyed callers. Base was untyped too; `kR` now reads untyped.
 - Evidence: `D/reviews/task-13-review.md`; `D/reviews/final-VD.md` triage.

**Harness check (`ea5f7fd1`):** domain_detectors.py:4908 (resistor branch) and :4902 (resistor_network) call parse_value untyped. Probe at ea5f7fd1: parse_value('1k_0402') None vs typed 1000; '330R_0603' None vs 330; '10K_0603' None vs 10000; '4k7R' 4700 both. The task-13 review rated the resistor_network call (:4902) correct untyped. **Correction:** Only :4908 (the type == 'resistor' branch) is in scope; :4902 is the resistor_network branch, untyped by design. Effect: footprint-suffixed values the typed path reads (1k_0402, 330R_0603, 10K_0603) stay unread there and set found_unparsed.

### KH-1317: `_BOOTSTRAP_PIN_TOKENS` (`signal_detectors.py:52`) lacks `BTST` (`lc-det-btst-bootstrap`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 31 `lc-det-btst-bootstrap`); checked by the harness at `ea5f7fd1`

 - Symptom: `_BOOTSTRAP_PIN_TOKENS` (`signal_detectors.py:52`) lacks `BTST`. Once Task 11 (`27569ef5`) reads `1uH_4A_5.6A_sat_C5832370` and `47nF/10V`, the LC detector pairs the switch-node inductor with the bootstrap capacitor:
   - AdityaIyer2k7/polar-rover-pcbs `rover-mppt-pcb`: BQ25820 L1 + C7 on BTST1;
   - mx3353672833-debug moto-gps-waveshare ×8 copies: L1 on BQ_SW-SYS, C7 on BQ_SW-BQ_BTST, "LC filter at 734127 Hz".
 - Reach: 9 records, measured in the close A/B (pin nets read for all 9). Declared known-false. The scan also hit OpenVent `VCCB`, which is not a bootstrap pin.
 - Fix: add `BTST` to `_BOOTSTRAP_PIN_TOKENS`. Not fixed in 12c (ledger ruling: no second fix wave).
 - Evidence: ledger Task 11; `D/reviews/final-VD.md`; `D/reconcile-wave12c.md` residual group 2.

**Harness check (`ea5f7fd1`):** All 9 confirmed in both the harness gate tree (results/v303_w12c_gate, baseline 0 LC-DET on all 9) and D/corpus-tip-ea5f7fd: rover-mppt-pcb L1(L8u2)+C7(C47n) 256 kHz, C7 on __unnamed_0 with U1 BTST1/D1 K and VSW (U1 SW1); moto-gps-waveshare 8 units L1+C7 734127 Hz, C7 on BQ_BTST (U2 BTST) / BQ_SW (U2 SW). The 9th moto unit hardware_pcb_moto-gps-rev-a.kicad_sch has 0. _BOOTSTRAP_PIN_TOKENS is at signal_detectors.py:55 = {BST, BOOT, BOOTSTRAP, CBST}. Related: KH-138 (FIXED, bootstrap LC exclusion) and KH-1241 (open: LC-DET never tests the cap's far net is ground; would also catch this). UNDECLARED co-movers on the same 8 moto units: +8 LC-DET L3(68nH)+C31(100pF) at 61 MHz where C31 is a series DC-block (GNSS_ANT_BIASED -> GNSS_RF_MATCH_IN, far node not ground) = KH-1241 class, newly reached by the value reader; rover also +1 L1+C5 (C5 on SR+/GND, plausible output filter). Note: Values: three rev-a0 moto copies read L1 '1uH_4.2A_C492725', the other five '1uH_4A_5.6A_sat_C5832370'; rover reads 'L8u2' / 'C47n'. Line :55 not :52. Add a KH-1241 addendum for the 8 moto L3+C31 records (undeclared false).

### KH-1316: PU-001 "pull-up value too high (470k)" fires on the top resistor of a divider that VD-DET claims as an `enable_threshold` divider (`pu001-divider-top`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 30 `pu001-divider-top` (PU-001 / VD-DET `enable_threshold`)); checked by the harness at `ea5f7fd1`

 - Symptom: PU-001 "pull-up value too high (470k)" fires on the top resistor of a divider that VD-DET claims as an `enable_threshold` divider. demeter-hydroponics/demeter-boards: 8 info records, newly reached by the value reader (an old heuristic; base already emits one, Neptune R802).
 - Fix direction: PU-001 skips a resistor VD-DET claims as an enable-threshold divider.
 - Evidence: `X/task-11-report.md` concern 1; `D/reviews/final-VD.md` triage.

**Harness check (`ea5f7fd1`):** demeter-hydroponics/demeter-boards at ea5f7fd1: 8 PU-001 'value too high' on resistors VD-DET claims as enable dividers (R1/U1 x2, R42/U6 x2 at 470k; R41/U7 x2, R38/U8 x2 at 127k); 0 at base on enable-claimed tops. **Correction:** 8 records: 4 at 470k (Column Controller V2 R1, Column Controller R42) and 4 at 127k (Germination R41, Node Controller R38), each on the root and its power sheet.

### KH-1315: the divider detector does not check that the top net is driven (`vddet-undriven-top`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 29 `vddet-undriven-top`); checked by the harness at `ea5f7fd1`

 - Symptom: the divider detector does not check that the top net is driven. Twisted-Fields/acorn-robot-electronics `previous_revisions_V1_acorn_motherboard.sch` R38 / R41 (top = undriven ADC input A5) gives a VD-DET info, declared.
 - Evidence: `D/reviews/task-3-review.md` I2.

**Harness check (`ea5f7fd1`):** Twisted-Fields acorn previous_revisions_V1_acorn_motherboard.sch: tip VD-DET info R38(1k)/R41(330R), top A5 = [U9 AIN0 input, D18 K, R38], mid VOUT_ISENSE (D5/D6/D7 K), bottom GND; base none. Topology is a series R into the ADC with a burden resistor, not a divider.

### KH-1314: PU-001 asks for a pull-up on a pin whose name ends in `OD` (`validation_detectors.py:279`), so TPS22917 `QOD` (quick output discharge) counts, even on a net … (`pu001-qod-own-power-out`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 28 `pu001-qod-own-power-out`); checked by the harness at `ea5f7fd1`

 - Symptom: PU-001 asks for a pull-up on a pin whose name ends in `OD` (`validation_detectors.py:279`), so TPS22917 `QOD` (quick output discharge) counts, even on a net that the part's own `power_out` drives. Foalyy/silver-kicad `silver.sch` U7: 1 false PU-001, declared. It was hidden at base only because the resistor went to `VBAT_MEAS`, then read as a rail.
 - Evidence: `D/reviews/task-3-review.md` I1.

**Harness check (`ea5f7fd1`):** validation_detectors.py:279-281 pin_upper.endswith('OD') with 'OD' in _PULLUP_PIN_NAMES (:170). Foalyy/silver-kicad silver.sch: tip PU-001 'U7 pin QOD (__unnamed_10) missing pull-up' (0 at base); __unnamed_10 = R11, U7 QOD output, U7 VOUT power_out; U7 = TPS22917.

### KH-1313: power-mux outputs (TPS2115A / 2116 / 2117 / 2121, LM66200, LTC4417, AP2152 OUT2) source a rail unconditionally (~20 RS-001 removals) (`power-mux-output-source`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 26 `power-mux-output-source`); checked by the harness at `ea5f7fd1`

 - Symptom: power-mux outputs (TPS2115A / 2116 / 2117 / 2121, LM66200, LTC4417, AP2152 OUT2) source a rail unconditionally (~20 RS-001 removals). The right model is a switch chain (sourced when an input is sourced); AP2152 belongs on the load-switch list.
 - Evidence: `D/reviews/task-22-review.md` deferred minor.

**Harness check (`ea5f7fd1`):** IImon1293/CMFD-LMSE Power.kicad_sch RS-001: base SYS_5V/USB_5V/VIN -> tip USB_5V/VIN (SYS_5V lost while both mux inputs keep theirs). No mux part list in kicad scripts (grep TPS2115/LM66200/LTC4417/AP2152 = 0). Not a dup of KH-1262 (P-FET).

### KH-1312: PR-DET records a non-regulator output as a regulator output, or the input as the output (`prdet-output-rail-misread`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 25 `prdet-output-rail-misread`); checked by the harness at `ea5f7fd1`

 - Symptom: PR-DET records a non-regulator output as a regulator output, or the input as the output:
   - richardhosking ADF4351 `RF_OUT` (12 PP-001 removals, outcome right; the real ADP150 VOUT is unrecorded);
   - Dashdash v1 U49 `output_rail` = its input (thermal charges it).
 - Evidence: `D/reviews/task-24-review.md`; ledger Task 30.

**Harness check (`ea5f7fd1`):** ADF4351 half reproduced: richardhosking SpectrumAnalyser.sch / SpecAnFrontEnd.sch U15 PR-DET ic_with_internal_regulator output_rail __unnamed_130 / __unnamed_71 = RF_OUT_A+ + L6 + C83; ADP150 U1/U14 have no PR-DET. Dashdash half is not a PR-DET misread: in the source pcb/v1/v1.kicad_sch U49 (MIC2940A-5.0WT on L7805) IN goes to +12V (19.05,172.085) and OUT to a +5V symbol (48.26,172.085); but the analyzer's '+12V' net (73 pins) holds U49 IN and OUT, U50 IN, all 74xx VCC pins and every '+5V' power symbol (#PWR0225/0232/0164/095/0172); no '+5V' net exists in the output (base and tip). A rough wire union-find over all 4 sheets finds no +5V/+12V short. So +5V is merged into +12V by connectivity; PR-DET follows the net. kicad-cli 10.0.8 fails to load the file, so not oracle-confirmed. **Correction:** Keep the ADF4351 case (PR-DET takes an RF output pin RF_OUT_A+ reached through L6 as an internal-regulator output; real ADP150 VOUTs unrecorded). Drop Dashdash from this KH and file it separately as a connectivity defect: Churrosoft Dashdash pcb_v1 v1.kicad_sch merges the +5V rail into +12V (no +5V net in the output; U49 MIC2940A-5.0 IN and OUT on one net), base and tip; merge point not yet found.

### KH-1311: a net carrying a regulator's `power_out` pin is not a PP-001 rail when its name is not a power name and PR-DET did not record it (`_is_dc_rail`) (`pp001-regulator-power-out-unnamed-rail`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 24 `pp001-regulator-power-out-unnamed-rail`); checked by the harness at `ea5f7fd1`

 - Symptom: a net carrying a regulator's `power_out` pin is not a PP-001 rail when its name is not a power name and PR-DET did not record it (`_is_dc_rail`). SCFormula 12 pins on `V5` (L78L05) and Lefty 2 pins on `P5V0` (NCP1117) keep their errors.
 - Evidence: `X/task-24-report.md` concern 1.

**Harness check (`ea5f7fd1`):** At ea5f7fd1: SCFormulaElectric BSPD_2027 history copies: 11 PP-001 on V5 over 4 units (3+3+3+2), V5 carries U1 OUT power_out (L78L05); hwstar Lefty-MOBO: 2 PP-001 on P5V0 on each of 2 units (VR801 OUT power_out). _is_dc_rail (signal_detectors.py:5550) credits a power_out net only through reg_output_nets. **Correction:** SCFormula: 11 PP-001 records on V5 over 4 units (not 12); Lefty: 2 records on P5V0 on each of 2 units (4 records).

### KH-1310: PP-001 does not cross a power switch (`pp001-switch-pass-through`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 23 `pp001-switch-pass-through`); checked by the harness at `ea5f7fd1`

 - Symptom: PP-001 does not cross a power switch. gehel/synth `Noise Toaster_Noise Toaster.kicad_sch`: U1.4, U2.4, U3.6 on `BP`, fed through the on/off switch AR_Mod_On_Off2, still report "no DC path to a power rail" (3 errors, as at base). KH-1237 named `BP` as already false; its three filed supplies are fixed.
 - Evidence: corpus check in `fixes-wave12c.md` (KH-1237 row).

**Harness check (`ea5f7fd1`):** gehel/synth Noise Toaster_Noise Toaster.kicad_sch: PP-001 base 6 -> tip 3, the 3 left are U1.4 / U2.4 / U3.6 on BP; BP holds AR_Mod_On_Off2.B, BT1+ is on __unnamed_0 with AR_Mod_On_Off2.A (SPDT). KH-1237 text names BP as already false; KH-1237 closes for its 3 supplies, so file this residue new.

### KH-1309: our net-level `no_connect` on multi-pin nets does not match KiCad's grouping (`pwrflag-no-connect-grouping`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 22 `pwrflag-no-connect-grouping`); checked by the harness at `ea5f7fd1`

 - Symptom: our net-level `no_connect` on multi-pin nets does not match KiCad's grouping. kicad-cli 10.0.8 still flags 18 of the survey's 49 checkable no-connect nets (e.g. BerkeleyLab Obsidian `+3V3_USB`, BeeMS `+3.3V` / `GND`, CM5 carriers `GND`). The audit therefore skips per pin (−16 / 12 units, not −50), and non-rail no-connect nets stay unreported (16 multi-pin adds held back). KiCad master's `erc.cpp` skips any net with a no-connect subgraph, yet 10.0.8 flags these; cause not identified.
 - Evidence: `X/task-26-report.md` concern 1.

**Harness check (`ea5f7fd1`):** audits.py:149-176 at ea5f7fd1 matches: non-rail no_connect nets skipped, rail NC nets still checked, NC power_in pins skipped per pin. Obsidian +3V3_USB (no_connect, 21 pins) still warns on the root unit (1 base, 1 tip). kicad-cli 18/49 not re-run. Near KH-738 (ERC NC-suppression residue) but different surface (pwr_flag audit); keep separate.

### KH-1308: single-pin "Net" warnings on unwired copies of a shared (common-unit) power pin on a second unit (`pwrflag-unit-shared-power-pin`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 21 `pwrflag-unit-shared-power-pin`); checked by the harness at `ea5f7fd1`

 - Symptom: single-pin "Net" warnings on unwired copies of a shared (common-unit) power pin on a second unit. ~584 adds / 132 units. KiCad flags 7 / 10 sampled on that exact pin; not flagged: MatthewATaylor VCA_Single U101.4, triglav voltage_processor U4.4, RobertPHeller STM32F767ZI_LCC_Repeater U201.8 (`different_unit_net` only). About 25 % false.
 - Evidence: `D/reviews/task-26-review.md` M-1.

**Harness check (`ea5f7fd1`):** MatthewATaylor VCA_Single VCA.kicad_sch at ea5f7fd1: 6 single-pin 'Net' warnings, e.g. __unnamed_24 = [U101.4 V- power_in] only, __unnamed_25 = [U101.8 V+]; also U103. Base had only the 3 rail warnings. 584/132 reach not re-measured. Not a duplicate (KH-459 residue).

### KH-1307: `detect_sub_sheet` (`schematic/reader.py:1445`) reads two kinds of sub-sheet as roots (`sub-sheet-read-as-root`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` B item 20 `sub-sheet-read-as-root`); checked by the harness at `ea5f7fd1`

 - Symptom: `detect_sub_sheet` (`schematic/reader.py:1445`) reads two kinds of sub-sheet as roots:
   - KiCad 6 sub-sheets saved with `symbol_instances` (williamweatherholtz/kicad_subs `DRV602_3V3.kicad_sch`);
   - leaf sheets with only global labels and no same-stem `.kicad_pro` (NexusGPT openring `ring_controls.kicad_sch`, KiCad 10).
   So `standalone_sheet` is False there, and the PWR_FLAG audit warns on nets that leave the sheet.
 - Reach: ~148 units / 450 adds from files another sheet names as a Sheetfile; 171 on labelled nets; ≥ 5 / 14 sampled not flagged by root ERC.
 - Fix considered: fix the detection. Waited: it moves `hierarchy_warning` output (out of scope).
 - Evidence: `D/reviews/task-26-review.md` I-1.

**Harness check (`ea5f7fd1`):** detect_sub_sheet probe at ea5f7fd1 (schematic/reader.py:1445): kicad_subs/DRV602_3V3.kicad_sch (version 20211123, has symbol_instances, 18 hier labels, named as Sheetfile by RN52_.kicad_sch) -> False (root, tier 1); pwr_flag_warnings 0 -> 3 (3V3, GND, __unnamed_2). openring live ring/ring_controls.kicad_sch -> True (sub-sheet: ring.kicad_pro in the dir, tier 3) and gets 0 warnings; only the evidence copies with NO .kicad_pro in their dir read root: evidence/v7/before/ring_controls and pcb/evidence/r3/before/sch/ring_controls (2 warnings each: GND, VBAT). Not in ISSUES/FIXED; residue of the KH-459 close. **Correction:** Kind 2 is a leaf sheet in a directory with no .kicad_pro at all (tier 5 default); a different-stem .kicad_pro already makes tier 3 say sub-sheet. Example: NexusGPT openring evidence copies design/ecad/ring/evidence/v7/before/ring_controls.kicad_sch and ring/pcb/evidence/r3/before/sch/ring_controls.kicad_sch (GND, VBAT); the live ring/ring_controls.kicad_sch is read as a sub-sheet. Also tier 1's docstring says 'KiCad 7+ roots always have symbol_instances', but it is a KiCad 6 key that a reusable sub-sheet saved as root also keeps.

### KH-1306: an EN / CE pin is read by its name, without its polarity or its role (`en-name-polarity`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 19 `en-name-polarity`); checked by the harness at `ea5f7fd1`

 - Symptom: an EN / CE pin is read by its name, without its polarity or its role.
   - Active-low without an overbar (BQ25628 CE, XL7015 EN).
   - Charger mode pins named EN: owltunes U101 BQ24073 `EN2` (100k to VIN_CHG) reads `always_on` (Task 32, declared).
   - The direct-tie branch (`system_analyses.py:1893`) keeps its old reading for an overbar EN tied straight to a rail. The pull-up case was fixed in the fix wave (`2e5d0cc9`).
   - Lane B's classifier reads a resistor from EN to a negative power net (a regulator-driven VSS, `-12V`) as a pull-up (integration side note).
 - Addendum, switched rails: a rail switched by a relay or load switch is not known as disableable, so its power LED reads always conducting in the sleep audit (IoT12 `24V_SWITCHED`, Speaker-PCB `24VSW`; 2-3 units).
 - Evidence: `D/surveys/survey-B.md` asks; `X/task-32-report.md`; `D/reviews/task-28-review.md`; `X/integration-report.md`.

**Harness check (`ea5f7fd1`):** system_analyses.py:1892-1894 at tip: `elif is_power_net(en_net): en_source = 'always_on'` with no is_active_low_enable test (the ground branch above it has one), so an overbar EN tied straight to a rail reads always_on. Other sub-items not re-probed. Related: KH-428 (closed in 12c: pull-up / pull-down classification) - the 'resistor from EN to a negative power net read as a pull-up' sub-item is a KH-428 residue; KH-439 for the sleep audit.

### KH-1305: the power budget charges an ESD array (USBLC6, …) as a 50 mA IC. 12c's thermal now reads the budget, so (`budget-esd-array-load`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 18 `budget-esd-array-load`); checked by the harness at `ea5f7fd1`

 - Symptom: the power budget charges an ESD array (USBLC6, …) as a 50 mA IC. 12c's thermal now reads the budget, so:
   - Bastardkb/Dilemma `3x5_3_dilemma` and `3x5_3_procyon_dilemma` U3 / U5001 XC6210 get TS-002 errors (215 mA; no finding at base);
   - Twisted-Fields rp2040-motor-controller U24 (switcher, 540 mA) gets TS-001;
   - U32 TLV1117LV33 carries 5 × USBLC6-4SC6 = 250 of 495 mA (its TS-004 was present at base).
 - Reach: 882 / 686 units carry such a load (survey B).
 - Waited: the budget model is outside 12c (B-1).
 - Evidence: `D/surveys/survey-B.md` asks; `X/task-30-report.md`.

**Harness check (`ea5f7fd1`):** Tip schematic Twisted-Fields/rp2040-motor-controller RP2040_base: power_budget +3V3 lists U43 USBLC6-4SC6 estimated_mA 50 (power_budget keyword match on value + full lib_id, system_analyses.py:1630-1637). Thermal TS-001/TS-002 records not checked (no thermal tree in the product corpus dirs). No existing KH on ESD arrays in the budget (KH-432 closed; KH-1219 is nicknames).

### KH-1304: `OKI-78SR-5/1.5-W36H-C` reads 7.8 V from `-78` (a bare code, not explicit) (`oki-78sr-bare-code`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 17 `oki-78sr-bare-code`); checked by the harness at `ea5f7fd1`

 - Symptom: `OKI-78SR-5/1.5-W36H-C` reads 7.8 V from `-78` (a bare code, not explicit). Still 7.8 at `ea5f7fd1` (probe). 1 key.
 - Evidence: `D/surveys/survey-R.md` ask 4.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref('OKI-78SR-5/1.5-W36H-C') = (7.8,'fixed_suffix') at both clones, with or without the Converter_DCDC:OKI-78SR-5_1.5-W36H-C lib_id. No KH mentions OKI-78SR.

### KH-1303: a label Value that names no part lets the symbol's decoded fixed voltage count (`label-voltage-vs-symbol`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 16 `label-voltage-vs-symbol`); checked by the harness at `ea5f7fd1`

 - Symptom: a label Value that names no part lets the symbol's decoded fixed voltage count. 9 records, declared known-false:
   - jkominek/adcstudy `3.3V Reg` on L7805 ×3 (+3V3 → 5.0);
   - fordp2002 `3V3 PSU` on L7805 (+3V3 → 5.0);
   - formulaslug `LF33CV 3.3v linear reg` on L78L09_SOT89 ×2 (+3.3V → 9.0);
   - kanengomibako `7833` on L7805 (+3V3 → 5.0);
   - Akku-Craft/schematics `Schaltplan.kicad_sch` U8 `Amperemeter` (an ACS712) on LM2596S-5 → 5.0 on `__unnamed_53`;
   - Fescron diy-logging-volt-ampmeter `5Vout-50V`: U? `DC/DC 5V out` on `OKI-78SR-3.3_1.5-W36-C` → 3.3 (the rail is 5 V).
 - Fix considered: reading the label's voltage. Waited: label text is against C-P4 (R-P5).
 - Evidence: `D/surveys/survey-R.md` R-P5; `X/task-39-report.md` concern 1; ledger ruling on `19bc3fa0`.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref base -> tip: '3.3V Reg' on L7805 None -> 5.0; '3V3 PSU' on L7805 None -> 5.0; '7833' on L7805 None -> 5.0; 'LF33CV 3.3v linear reg' on L78L09_SOT89 None -> 9.0; 'Amperemeter' on LM2596S-5 (1.23 lookup) -> 5.0; 'DC/DC 5V out' on OKI-78SR-3.3 3.3 both. Corpus: jkominek main-board / Power.kicad_sch / adc-board U3/U13 '3.3V Reg' estimated_vout None -> 5.0 on +3V3. So 5 of 6 cases are new in the range (the KH-1273 close, ledger ruling 19bc3fa0), not pre-existing. **Correction:** Add: introduced in the range by the KH-1273 change (19bc3fa0): at base these Values gave no voltage (Amperemeter 1.23 V lookup); only Fescron 'DC/DC 5V out' -> 3.3 is as at base. Related: KH-1273 (closed in 12c).

### KH-1302: many LDO families carry their voltage in their own order code and read none (`ldo-voltage-code-families`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 15 `ldo-voltage-code-families`); checked by the harness at `ea5f7fd1`

 - Symptom: many LDO families carry their voltage in their own order code and read none: Torex XC6206 / XC6210 / XC6220, Microne ME6211, HX6306, TI TLV1117LV / TLV755 / TLV757 / TLV743, Holtek HT73xx, MaxLinear SPX3819, LM4040.
 - Same-part respellings dropped by R-P1: `AMS1117-3_3` on AMS1117-3.3, `NCP1117-5v` on NCP1117-5.0_SOT223, `LP5912Q3.3DRVRQ1` on LP5912-3.3DRV (the Value writes its voltage with `_`, a lower-case `v`, or `Q` before the digits). `AMS1117-5` reads the AMS1117 adjustable reference 1.25 V, not 5 V.
 - Reach: about 440 component-unit hits (E); this would bring back most of R-P1's 103 right-by-luck Vouts with real evidence.
 - Waited: one cited datasheet per family (R12b-3).
 - Evidence: `D/surveys/survey-R.md` ask 4; `X/task-34-report.md` harness ask 2.

**Harness check (`ea5f7fd1`):** lookup_regulator_vref at both clones: XC6206P332MR, XC6210B332MR, XC6220B331MR, ME6211C33M5G, HX6306, TLV1117LV33, TLV75533PDBVR, TLV75733P, TLV74333P, HT7333, SPX3819M5-L-3-3, LM4040 -> (None,'') both sides. Respellings base -> tip: 'AMS1117-3_3' on AMS1117-3.3 (3.3 fixed_suffix) -> (1.25,'lookup'); 'NCP1117-5v' on NCP1117-5.0_SOT223 (5.0) -> (1.25,'lookup'); 'LP5912Q3.3DRVRQ1' on LP5912-3.3DRV (3.3) -> None; 'AMS1117-5' 1.25 both. No duplicate (KH-1212 MIC23050 and KH-1284 LD1117/NCP1117 are single families). **Correction:** Say the R-P1 respellings now take the family's adjustable reference, not none: AMS1117-3_3 and NCP1117-5v return (1.25, 'lookup') at ea5f7fd1 (3.3 / 5.0 fixed_suffix at base), only LP5912Q3.3DRVRQ1 returns none. That is the KH-1284 shape (a fixed member read as the 1.25 V ADJ reference); cross-reference KH-1284.

### KH-1301: an output pin strapped to a rail now sources it (S-P1) (`rs001-output-pin-strap`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 14 `rs001-output-pin-strap`); checked by the harness at `ea5f7fd1`

 - Symptom: an output pin strapped to a rail now sources it (S-P1).
   - Kinds seen: MCP2551 Vref, TUSB2036 `~OVRCUR`, USB3343 CLKOUT (tiliqua; ButterStick r1.0 `ULIP_VDDIO` via NT1, which loses 2 true RS-003 infos), BNO086 CLKSEL1, TPS2330 VSENSE.
   - The kind list for the fix: EN / OE / CLR / RESET / LATCH / SEL, PGFB / `*OD`, CLKOUT / CLKSEL, VSENSE, FLG, ULN2003 COM, opto / SSR terminals, prefixed `PLL_VCC` / `LVDS_VCC`.
 - **RS-002 reach (close A/B, class `x-rs002-logic-output-jumper`):** a logic output behind an open jumper now counts as the rail's source, and the RS-002 jumper audit upgrades the base RS-001 warning to an **error** "VCC has no source unless user solders a jumper". 3 records, all false, declared known-false:
   - Kris-Sekula mgh80 `KiCad_v1.1_mgh80.sch` and `KiCad_v1.2_mgh80.sch`: U1 74HC00 pin 3 (output) on `__unnamed_3`, tied to VCC only through JP6 `Jumper_NC_Small` "Inpu_to_VCC";
   - jotego jtcores `cores_kiwi_sch_insectx_cpu.kicad_sch`: U15 74LS174 Q4 on `__unnamed_9`, behind JP2 `Jumper_3_Open` (pin 3 = VCC).
 - Reach: ~35 of 1,123 RS-001 removals (3.1 %), the 2 ButterStick RS-003, and RS-002 +3 (no other RS-002 add besides Churrosoft ×2).
 - Fix considered: widen `_SUPPLY_INPUT_PIN`. Waited: that is a new ruling, not the ruled S-P1 form. For the RS-002 half: the jumper path accepts only a power source on the far side (power_out pin, regulator output, connector, battery), not a logic or signal output. Not fixed in 12c: 3 records against the one-fix-wave rule (ledger ruling).
 - Evidence: `X/task-22-report.md` concerns 1-2; `D/reviews/task-22-review.md` I1; `D/reconcile-wave12c.md` residual group 1.

**Harness check (`ea5f7fd1`):** RS-002 half reproduced at tip (none at base): Kris-Sekula/mgh80 KiCad_v1.1_mgh80.sch and KiCad_v1.2_mgh80.sch 'VCC has no source unless user solders a jumper (__unnamed_3 via JP6)'; jotego/jtcores cores_kiwi_sch_insectx_cpu.kicad_sch '(__unnamed_9 via JP2)', all severity error. RS-001 removal reach (~35) not re-measured. KH-724 (the S-P1 rule's parent) closed in 12c; no duplicate.

### KH-1300: Churrosoft/uEFI-v6.x `hw_v1_connector.kicad_sch` and `hw_v1_hw_v1.kicad_sch` get RS-002 on `+12VA` (`rs002-input-behind-open-jumper`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 13 `rs002-input-behind-open-jumper`); checked by the harness at `ea5f7fd1`

 - Symptom: Churrosoft/uEFI-v6.x `hw_v1_connector.kicad_sch` and `hw_v1_hw_v1.kicad_sch` get RS-002 on `+12VA`. `+12VA` is the J1 input; `+12V` is now sourced by the LM74800 OUT across the open JP14, so the input reads as a rail behind an open jumper. 2 records, declared known-false.
 - Evidence: `X/task-22-report.md`.

**Harness check (`ea5f7fd1`):** Churrosoft/uEFI-v6.x hw_v1_connector + hw_v1_hw_v1: base RS-001 '+12V has no declared source' and '+12VA has no declared source' (warnings); tip only RS-002 error '+12VA has no source unless user solders a jumper (+12V via JP14)'. +12V is fed by U12 pin 9 (typed output, the LM74800 OUT) and Q3.3; +12VA holds J1.26/27 (passive), U12.2/3, Q3.1, JP14.1. So the input rail is upgraded warning -> error because the ideal-diode controller's OUT pin now counts as a source (the S-P1 output-pin rule) and the connector does not. Consider folding into rs001-output-pin-strap / power-mux-output-source (the LM74800 OUT is a sense pin; the real path is Q3).

### KH-1299: TUSB32x, HD3SS3220, AP33772, IP2721, CH22x, HUSB237, STUSB4700, TPS2573x / 5x and PTN5110 are not recognised as CC controllers, so UC-003 "missing … (`usb-cc-controller-list`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 12 `usb-cc-controller-list`); checked by the harness at `ea5f7fd1`

 - Symptom: TUSB32x, HD3SS3220, AP33772, IP2721, CH22x, HUSB237, STUSB4700, TPS2573x / 5x and PTN5110 are not recognised as CC controllers, so UC-003 "missing pull-down" stays beside a real controller.
 - Reach: ~70 units (E).
 - Waited: each needs a datasheet citation (V-6).

**Harness check (`ea5f7fd1`):** Tip lists: system_analyses.py:2583-2587 _PD_CONTROLLER_KEYWORDS (fusb302, fusb303, stusb4500, cypd317, husb238, tps65987/8, ccg3, ccg6, max77958, max20342); domain_detectors.py:2796-2799 _USB_PD_KEYWORDS (no fusb303). None of TUSB32x/HD3SS3220/AP33772/IP2721/CH22x/HUSB237/STUSB4700/TPS257x/PTN5110 (stusb4500 substring does not match STUSB4700). This is the KH-804 (d) residue. Side note: the two lists still differ (fusb303, max20342).

### KH-1298: a Type-C Rd to the connector's own GND-pin net is not read as returning to ground when that net is not ground by name (`cc-rd-earth-batt`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 11 `cc-rd-earth-batt`); checked by the harness at `ea5f7fd1`

 - Symptom: a Type-C Rd to the connector's own GND-pin net is not read as returning to ground when that net is not ground by name. After integration, 12 connectors still read CC status fail (status field only; findings as at base):
   - 10 Earth nets with no ground symbol that hold the connector GND pins: 0xjmux iot_led_strip J3; RivasMario PublicSecurity96 J1; ebastler E80-1800 J4; galopago iot-badge, old_iot-badge-433, old_iot-badge-915 J1; hackclub/OnBoard Tiny4FSK J3; hackclub/reflow phase-interferometer J1; xboxoneresearch ASPECT2, facet_conn J6;
   - hackclub/OnBoard `projects_LucidVRHapticGloves_src_lucidGloves.kicad_sch` J1, J2 (`__unnamed_21` / `__unnamed_27`).
   - The 11 `-BATT` cases are right after lane N; tubbytwins bumwings fails correctly (Rd to the shield).
 - Rd bands differ: `system_analyses._RD_BAND` is 4800-5600 Ω, PP-DET (`domain_detectors.py` ~2966) 4590-5610 Ω, so a 4.7 kΩ Rd is "Rd" in PP-DET and "not Rd" in `usb_compliance` (as at base; final-VD M4). Unify with this fix.
 - Fix considered: "the net holding the connector's own GND pins is the Rd return" fits all 12 and keeps bumwings failing. Waited: it touches ruling A4 (Earth is a return for ESD arrays only).
 - Evidence: `X/integration-report.md` Task 14 re-check; `D/reviews/task-14-review.md` I1; `D/reviews/final-VD.md` M4.

**Harness check (`ea5f7fd1`):** hackclub/OnBoard projects_LucidVRHapticGloves_src_lucidGloves.kicad_sch tip: usb_c_cc_status fail ['wrong_cc_value'] x2 for R1 / R2 5100 Ω, to_ground false; R1.2 on __unnamed_21 with J1 A12/B12 (GND pins), R2.2 on __unnamed_27 with J2 A12/B12. Rd bands confirmed: system_analyses.py:2448 _RD_BAND = (4800, 5600); domain_detectors.py:2966 4590 <= r <= 5610. KH-804 (closed in 12c) named neither; no duplicate.

### KH-1297: `R_100`, `49.9_1%`, `100_0402` plain-number fields are not read (≈ 260 parts) (`plain-number-field`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 10 `plain-number-field`); checked by the harness at `ea5f7fd1`

 - Symptom: `R_100`, `49.9_1%`, `100_0402` plain-number fields are not read (≈ 260 parts). `49.9_1%` read 49.91 at base and none now (the underscore guard, V-2): 4 RC-DET lost in 2 units.
 - Evidence: `D/surveys/survey-V.md`; `X/task-11-report.md` concern 4.

**Harness check (`ea5f7fd1`):** parse_value(...,'resistor') base -> tip: 'R_100' None -> None; '49.9_1%' 49.91 -> None (the underscore guard); '100_0402' 1000402.0 -> None. Add for accuracy: at base '100_0402' read 1,000,402 Ω (wrong), so that form went wrong -> none, not right -> none. RC-DET loss (4 / 2 units) not re-measured.

### KH-1296: `100E` = 100 Ω is unread (938 parts / 116 units) (`e-ohm-notation`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 9 `e-ohm-notation`); checked by the harness at `ea5f7fd1`

- Symptom: `100E` = 100 Ω is unread (938 parts / 116 units); `4E7` reads 4e7, not 4.7 Ω (2 parts). Sarbf1 mixes `R10K` (10 kΩ, read) with `R470` / `R220` / `R100` (European 0.47 / 0.22 / 0.1 Ω, base reading kept).
- Evidence: `D/surveys/survey-V.md` harness asks; `X/task-11-report.md` concern 3.

**Harness check (`ea5f7fd1`):** parse_value('100E','resistor') None both sides; 'R470' 0.47 both; 'R10K' None -> 10000.0 (tip). '4E7' = 4e7 both sides - but FIXED.md 2026-10-27 KH-664 closed exactly this ('values with E as the decimal mark (4E7, 0E12) parse as exponents') as CONFORMANT: KiCad reads 4E7 as an exponent (ruling entry 31) and a product test pins it. **Correction:** Drop the '4E7 reads 4e7, not 4.7 Ω' half (KH-664, closed as conformant to KiCad, ruling entry 31); keep '100E = 100 Ω is unread (938 parts / 116 units)' and the Sarbf1 R470 note. If the harness wants 4E7 reopened it needs a new ruling.

### KH-1295: a primary-side or shield return is read as a supply rail, so its IC return pins get "missing decoupling" (`primary-return-rail`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 8 `primary-return-rail`); checked by the harness at `ea5f7fd1`

- Symptom: a primary-side or shield return is read as a supply rail, so its IC return pins get "missing decoupling".
  - SimMonitor `-Vin` (REC5A primary 0 V): 3 adds + 2 changes;
  - AnotherMike KiCadBlocks Si3402 `VNEG` / `VNEG_EP` (PoE PD primary return): 4;
  - Gherkin netdaq `ETH_SHIELD`: 1 change.
  All are declared known-false in `d2-exposed-ground-rails`. Before 12c, the Y-cap across the barrier made them look decoupled.
- Also: Earth used as circuit ground (0xPolybit LM7805 VI ×2 via a 1k bleeder to Earth; outcome right; rev-t24).
- Reach: base 492 / 173 units carry "missing decoupling on Earth" (KH-925 earth addendum count); 12c adds 26 / changes 3.
- Fix considered: none in 12c: G2 keeps Earth out of grounds (R6). → 12j.
- Evidence: `D/surveys/survey-D.md`; `X/task-18-report.md` d2-exposed-ground-rails.

**Harness check (`ea5f7fd1`):** corpus base vs tip: Demetrius-Ross/SimMonitor board_MKIV / signal-board / legacy optocoupler / Mk2: base already has DO-DET 'IC U2 missing decoupling on -Vin' on signal-board and 'Decoupling coverage on -Vin' elsewhere; tip turns board_MKIV and legacy_schematic_vers into 'IC U2 missing decoupling on -Vin'. AnotherMike-exe/KiCadBlocks Si3402 units: base 'Decoupling coverage on VNEG' -> tip 'IC U1/U2/U5 missing decoupling on VNEG' (4 units). Gherkin ETH_SHIELD not checked. KH-1093 (Y-cap) closed in 12c; KH-1090 is COM; not a duplicate of KH-925 (Earth names).

### KH-1294: `spice_results.py:745` `evaluate_decoupling` always writes `model_note` "generic ESR + parasitic L …", even when the bench took ESR / ESL from `pdn_impedance` (`decoupling-bench-model-note`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 7 `decoupling-bench-model-note` (12g)); checked by the harness at `ea5f7fd1`

- Symptom: `spice_results.py:745` `evaluate_decoupling` always writes `model_note` "generic ESR + parasitic L …", even when the bench took ESR / ESL from `pdn_impedance`. It moves `model_note` on most decoupling sims.
- Waited: 12g, with KH-716.
- Evidence: `D/surveys/survey-D.md`.

**Harness check (`ea5f7fd1`):** spice_results.py:745 evaluate_decoupling hard-codes result['model_note'] = 'generic ESR + parasitic L from self-resonant frequency' (ea5f7fd1); the bench template computes the real note at spice_templates.py:1461-1467 ('ESR/ESL from pdn_impedance ...' / mixed / estimated) and only writes it into the netlist comment (:1472). Not a duplicate: KH-1003 (closed) covered the netlist note; KH-716 is presence-only criteria. **Correction:** Say: the decoupling result record's model_note is a constant 'generic ESR + parasitic L from self-resonant frequency' even when the bench took ESR / ESL from pdn_impedance (the template's own note, spice_templates.py:1461-1467, reaches only the netlist comment). A fix would change model_note on every decoupling record whose caps come from pdn_impedance. ('It moves model_note on most decoupling sims' reads as a current movement.)

### KH-1293: other detectors keep DNP / off-board passives (records whose components include one) (`dnp-other-detectors`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 6 `dnp-other-detectors`); checked by the harness at `ea5f7fd1`

- Symptom: other detectors keep DNP / off-board passives (records whose components include one): VD-DET 853 / 330 units, VD-004 105 / 33, VD-001 34 / 12, LC-DET 117 / 62 (`detect_lc_filters` `:798`, the same `group_reps` call as RC-DET), RM-DET 60 / 51, CS-DET 10 / 5, XT-001 6 / 6. Some may be meant (NT-001 1,855, SS-001 158 list DNP parts by design): survey per detector.
- Also from 12c:
  - `parallel_groups` reads only `dnp`, so an off-board part can stay in a group and be its representative (0 records seen; rev-t17);
  - inline unfitted tests not switched to `is_fitted`: `system_analyses.py:101` and `:2640`, `is_protection_part`, `cross_analysis.py:374`, and the VBUS cap loop from `370de1da` (same semantics; final-VD);
  - Not-fitted Values (`NC`) on parts other than capacitors: ebaz4205 U72 (see `dnp-en-driver`).
- Evidence: `D/surveys/survey-D.md`; `X/task-17-report.md` concerns.

**Harness check (`ea5f7fd1`):** Same scan (records whose components include a DNP ref): VD-DET 957 (claim 853; my ref-level match is looser), VD-004 105, VD-001 34, LC-DET 117, RM-DET 60, CS-DET 11 (claim 10), XT-001 6 - all others match the claim. Residue also seen: RC-DET 6 and DC-DET 1, which are shared-ref cases (chatelao xDuinoRail-Debug C301/R301, cristobalcuevas 'C?') = the KH-483 addendum, not this item. No existing KH for these detectors.

### KH-1292: `ic_pin_analysis[].decoupling_caps_by_rail` lists DNP caps (`ipa-dnp-decaps`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 5 `ipa-dnp-decaps`); checked by the harness at `ea5f7fd1`

- Symptom: `ic_pin_analysis[].decoupling_caps_by_rail` lists DNP caps.
- Reach: 3,736 rail entries / 531 units.
- Evidence: `D/surveys/survey-D.md`.

**Harness check (`ea5f7fd1`):** Same scan: 3,822 ic_pin_analysis decoupling_caps_by_rail entries / 543 units hold a DNP cap (claim 3,736 / 531); e.g. CIRCUITSTATE/Mitayi-Pico-D1 r0.5 U3 '+1V1' lists DNP C3 (the KH-1003 example cap, now out of DC-DET). No existing KH.

### KH-1291: PR-DET `input_capacitors` / `output_capacitors` list DNP and off-board caps (`prdet-dnp-caps`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 4 `prdet-dnp-caps`); checked by the harness at `ea5f7fd1`

- Symptom: PR-DET `input_capacitors` / `output_capacitors` list DNP and off-board caps. They feed the load proxy (`signal_detectors.py:2638-2660`), derating, cross TW-001 and EMC.
- Reach: 312 records / 155 units.
- Waited: belongs with the load model (PR-D5); its EMC / thermal reach is unmeasured.
- Evidence: `D/surveys/survey-D.md` item map.

**Harness check (`ea5f7fd1`):** Scan of the product tip corpus (corpus-tip-ea5f7fd, DNP by reference = dnp or on_board False): 318 PR-DET records / 158 units list a DNP cap in input_/output_capacitors (claim 312 / 155), e.g. slimcdk/wisweep electronics_driver-board U1 with C20, C23. Not covered by KH-1003/1011/1210 (closed in 12c for DC-DET, inrush, RC-DET).

### KH-1290: legacy nets carrying a GND symbol take the name of a local label (`legacy-label-vs-power-name`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 3 `legacy-label-vs-power-name` (12e)); checked by the harness at `ea5f7fd1`

- Symptom: legacy nets carrying a GND symbol take the name of a local label: gpgreen `CAP-PLATE-2`, Spooky 8Q `DP_HDMI_HPD`, aosodoev `AMP_R`. KiCad 5's priority between a power pin and a local label has not been checked.
- Fix considered: none; no kicad-cli oracle for `.sch`, use the corpus `.net` files.
- Evidence: `D/surveys/survey-G2.md` ask 4.

**Harness check (`ea5f7fd1`):** Tip outputs: gpgreen/fuel_capacity_sensor fuel_capacity_sensor.sch net CAP-PLATE-2 (43 pins) carries #PWR022/#PWR023/#PWR025/#PWR033; Spooky-Manufacturing/8Q 8Q_8Q.sch and 8Q_cpu.sch DP_HDMI_HPD (407 / 179 pins) carry #PWR0200..; aosodoev/esp8266-doorphone extra_kicad_handset_handset.sch AMP_R (38 pins) carries #PWR07..#PWR020. No existing KH on power-pin vs local-label naming priority (KH-879 is sheet-index tie-break, KH-690 bus members).

### KH-1289: in some legacy `.sch` files every ground symbol sits on its own `__unnamed` net, and no net is named GND: Sierra-Lobo revA-proto (#GND0124), 4ms … (`legacy-stranded-power-symbol`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 2 `legacy-stranded-power-symbol` (12e)); checked by the harness at `ea5f7fd1`

- Symptom: in some legacy `.sch` files every ground symbol sits on its own `__unnamed` net, and no net is named GND: Sierra-Lobo revA-proto (#GND0124), 4ms openventilator (`#U$` refs), LibreSolar mppt-2420-hc, GeeWizWow Jalapeno, eez-open. 12c's evidence rule (G2-1) makes those nets ground, but their naming stays wrong (910 stranded evidence nets, rev-t8).
- Addendum case, a ground symbol on the wrong net: ISSUIUC/ISS-PCB `archive_TARS-MK2_COTS.sch` places #PWR03 (GND) on `TM_POWER_POSITIVE` (KiCad's COTS.net: A2.1 + J9.1), so the battery positive reads ground and gets a 0 V key (declared known-false, 1 unit).
- Reach: ~37 union units + E ~53.
- Fix considered: none in 12c; needs the legacy reader. Check against the corpus `.net` files.
- Evidence: `D/surveys/survey-G2.md` ask 4; `D/reviews/task-8-review.md` I1.

**Harness check (`ea5f7fd1`):** Reproduced the mechanism: Sierra-Lobo/mainboard-hardware revA-proto_mainboard.sch has 71 __unnamed nets carrying a #GND symbol pin, its KiCad 6 twin revA-proto_mainboard.kicad_sch 0; LibreSolar/mppt-2420-hc kicad_dcdc.sch 10 and kicad_power-supply.sch 13 such nets and no GND-named net. But Sierra-Lobo's legacy units DO have a GND net (116 pins on mainboard.sch), and #GND0124 sits on the label-named '/61D3502C/SW_COM' with SW200.2, not on an __unnamed net. GeeWizWow/Jalapeno matrix/logos/underglow.sch: 0 such nets (other Jalapeno units not checked). Addendum case confirmed: ISSUIUC/ISS-PCB archive_TARS-MK2_COTS.sch TM_POWER_POSITIVE = A2.1 (POSITIVE) + #PWR03.1 (GND), rail_voltages TM_POWER_POSITIVE 0. No existing KH covers it (KH-1073/1031/879 are other legacy reader gaps). **Correction:** Say 'in some legacy .sch files many ground symbols each sit on their own __unnamed net (Sierra-Lobo revA-proto mainboard.sch 71 such nets beside a 116-pin GND net; the .kicad_sch twin has 0; LibreSolar mppt-2420-hc kicad_dcdc.sch 10 with no GND-named net)'. Drop 'no net is named GND' as a general statement. #GND0124 sits on the label net /61D3502C/SW_COM (a ground symbol on a labelled switch net: the item-3 / TARS-MK2 shape), not on an unnamed net.

### KH-1288: signal tails that R6 did not name still read as rails (`power-name-signal-tail-residue`)

**Severity:** LOW
**Discovered:** 2026-11-19, product v3.0.3 Wave 12c handoff (`kh-filings-wave12c.md` A item 1 `power-name-signal-tail-residue`); checked by the harness at `ea5f7fd1`

- Symptom: signal tails that R6 did not name still read as rails: `PWR_BUT` 40, `PWR_BUTTON` 20, `PWR_BTN` 11, `PWR_KEY` 14, `PWR_HOLD` 15, `PWR_WAKEUP` / `WKUP` 19, `VBAT_ALRT` 43, `5V_SCL` / `SDA` 44, `VBUS_INHIBIT` 15, `VIN_UVLO` 10, efuse pin nets `ITIMER` / `DVDT` / `ILM` / `PGTH` 72, `10V_ADC` / `32V_ADC` ESP32 taps 20 (about 330 unit-nets, almost all without power pins; survey P ask 3).
- Exposed in 12c (declared known-false):
  - P-notation switch and status nodes: daisho `V1P1_SW` / `V1P2_SW` / `V1P8_SW` / `V1P8_PH` (10 rail values), drewsum `POS1P2_PGOOD_VREG` (2), Lucas-Poulos `V1P8_SEL` (2 + VD-004 ×2), Gherkin netdaq `V3P3_VIN` (3 rail values + 6 VD-004: it is the buck input at ~5 V);
  - names read as pull-up rails: Duet3D Duet2 `5venjump` (2 units), kmahabeer `3V3_~{SHDN}` / `28V_~{SHDN}` (4 records, 2 units);
  - descriptive spaced phrases (P-R3's 5-8 % share): `2.5v unbuffered`, `12V AC (L)`, `vout AND potentiometer…`, `5v to 3v3`, `3.3V PIN`, `120VAC H` / `N` (~6 RS-001 / DO-DET). AC-mains names (`120VAC H/N`, `12V AC (L)`) also deserve a mains-name rule;
  - names right by rule but carrying a supply pin: `VIN_DIV` (underglow2 ×2, 1 true DO-DET lost) and `12V_SENSED` (berkeleyauv).
- Also: annegautham `P*P*V_VCC` LMR33610 bias-pin nets read the name literally (2.0 / 8.0 / 3.0 → 1.2 / 1.8 / 3.3; wrong before and after, 12 records). `cross_analysis.py:29` keeps its own `RAIL_SIGNAL_SUFFIXES` copy, so `VBAT_ADC` / `5V_FAULT` still read as power there (rev-t3 deferred; the 12j retire-the-copies item).
- Fix considered: widen the tail words. Waited: R6 named its words, and widening removes ~330 unit-nets unmeasured (P-R5).
- Evidence: `D/surveys/survey-P.md` ask 3; `X/task-3-report.md` concerns 3; `X/task-5-report.md`; `X/task-27-report.md` concern 1; `X/task-35-report.md` known-false.
- Wave: 12j with R7, or a later 3.0.3 name wave.

**Harness check (`ea5f7fd1`):** is_power_net_name at ea5f7fd1 (base 7ed10f3 same): PWR_BUT/PWR_BUTTON/PWR_BTN/PWR_KEY/PWR_HOLD/PWR_WAKEUP/PWR_WKUP/VBAT_ALRT/5V_SCL/5V_SDA/VBUS_INHIBIT/VIN_UVLO/10V_ADC/32V_ADC True both sides. 12c exposures: V1P1_SW/V1P8_PH/V1P8_SEL/V3P3_VIN/POS1P2_PGOOD_VREG parse_voltage None -> 1.1/1.8/1.8/3.3/1.2 (P-notation, new in range); spaced phrases '2.5v unbuffered','12V AC (L)','5v to 3v3','3.3V PIN','120VAC H' is_power False -> True; VIN_DIV/12V_SENSED True -> False. BUT efuse pin nets: bare ITIMER/DVDT/PGTH and the corpus forms SENSOR_POWER_AUX_DVDT, /power-in/DVDT are is_power_net_name False on both sides, and a scan of 60 tip units carrying them finds no RS-001/DO-DET/rail_voltages entry on those nets (only VD-DET/NT-001 records). 3V3_~{SHDN} is power True at base, False at tip (its pull-up-rail reading comes from the 3.3 V name parse, not the rail predicate). Not a duplicate: KH-717 (a) (the six named suffixes) is closed by 12c and KH-1139 is the glued no-underscore branch. **Correction:** Drop 'efuse pin nets ITIMER / DVDT / ILM / PGTH 72' from the tail list (not power names on either side; their reach must come from another path, not measured) or say how they read as rails; say kmahabeer 3V3_~{SHDN} / 28V_~{SHDN} are no longer power names at tip and read as pull-up rails through the name voltage (3.3 / 28). Note the P-notation and spaced-phrase cases are new in the range (name readers widened by 12c). Related: KH-717 (b)/(c), KH-1139.

### KH-1283: KiCad 5 Edge.Cuts arc with a near-zero sweep reads as a zero-length arc; KiCad makes it a full circle

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H9`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/reader.py:236-248` (`_legacy_arc_points`), at `de28149d`.
**Symptom:** kb_snak `snak_30.kicad_pcb:6219-6221` (`angle -0.0000032`); the upgrade writes 360° arcs, and PM-002 adds TP1.
**Reach:** 16 arcs in 5 boards.

**KH-NEW-H10 (LOW, or a KH-1129 addendum): an undefined bus alias used as a `{X}` group label**
On the alias-stripped 007785, KiCad joins M25 with S30 and V20 in `/Registers/HSIZE`; we don't. 1 lane unit; corpus reach unknown. To settle, use a kicad-cli fixture.

**KH-1129 addendum:** reach is now 40 non-empty `schematic.bus_aliases` projects (not 2). 22 of them use project-only aliases on ≥ 20250925 sheets (heuristic). Fixture confirmed: `wavenumber-eng/kicad_monkey/tests/cases/project_bus_alias_hierarchy` (2 kicad-cli nets → 4 of ours, +2 false NT-001).

**KH-1050 addendum:** apply the same predicate to PM-002. The H2 fix otherwise adds 204 false PM-002 errors on KiKit / mousebite footprints and 19 on net-less NPTH footprints (prototype, 62 boards).

**KH-687 addendum:** the pin *number* `~` → `""` half (`sch_io_kicad_sexpr_parser.cpp:2172`). It accounts for 5 of the 16 "KiCad same, partition moves" lane units (AlexCAB ×3, Churrosoft, gregdavill). R13 should name it.

**TH-NEW (harness): `lane_oracle.py` reports `kicad_same` where the netlist is blind**
`regression/netlist_oracle.py:38-40` `NODE_RE` needs a non-empty pin, so every `(pin "")` node is dropped (jotego: all 4 units vacuous, while KiCad's netlist really changed by 24-30 nets). The board netlist also omits `on_board no` symbols (baldengineer, chatelao: 0 nets). Fix: accept `(pin "")` and key such nodes by `pinfunction`, and mark units whose KiCad netlist has 0 nodes, or drops symbols our output has, as `oracle_blind` rather than `kicad_same`.
**Harness check (`7ed10f3e`):** pcb/reader.py:236-249 _legacy_arc_points: angle -3.2e-6 gives start = mid = end; snak_30.kicad_pcb:6219-6221 hold three such Edge.Cuts arcs (-2.87e-6, -1.23e-6, -3.20e-6).

### KH-1282: PM-002 / PM-001 truncation keeps file-order ties

**Severity:** LOW (output depends on footprint order)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H8`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/assembly.py:531, :554` (`[:20]`), `:433, :551` (`[:50]`), at `de28149d`.
**Symptom:** thpoll83 poly_kb keeps 20 different 0.18 mm references after the upgrade re-sorts footprints. Seen on 6 lane units.
**Reach:** 1,402 outputs at the PM-002 cap, 253 at the PM-001 cap. Fix: a deterministic tie-break.
**Harness check (`7ed10f3e`):** pcb/assembly.py:433 sorts overlaps by overlap_mm2 only and :531 edge_close by edge_clearance_mm only; truncations [:50] :551 and [:20] :554. Related, not dup: KH-957 (PM-001 pair layer chosen by file order).

### KH-1281: KiCad 5 overbar notation `~X~` in board net names is not converted to `~{X}`

**Severity:** LOW (names; misses active-low readings)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H7`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/reader.py` net table / pads / texts (no conversion), at `de28149d`. KiCad: `pcb_io_kicad_sexpr_parser.cpp:331-334`.
**Symptom:** `/LVL_~SHDN~` (UAH-IREC); 1:1 renames on 5 lane units.
**Reach (static):** 566 boards / 251 repos / 3,777 names. Check the schematic side (< 20210606 and legacy `.sch`) in the same task.
**Harness check (`7ed10f3e`):** No overbar conversion anywhere in the candidate's PCB reader (grep 'overbar' finds only pin-name helpers); classify.py:27-30 expects ~{...}. No dup.

### KH-1280: NPTH pads, aperture (non-copper) pads and non-copper zones keep their nets; KiCad clears them on load

**Severity:** MEDIUM (false RT-001 / TS-DET)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H5`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/reader.py:447-539` (pads), `:1288-1292` (zones); RT-001 at `pcb/routing.py:44-67`; at `de28149d`. KiCad: `pad.cpp:1602-1605`, `pcb_io_kicad_sexpr_parser.cpp:7997-8002, :10358`, `connectivity_algo.cpp:145`.
**Symptom:** Secalot BGA balls (copper + mask-only + paste-only pads on one net) give `Unrouted net … (3 pads)` ×96/99; MountingHole NPTH pads on GND give `Unrouted net GND (6 pads)`; `B.Mask` zones with a net give TS-DET.
**Reach (static):** aperture 252 boards / 69,149 pads; NPTH 63 / 317; non-copper zones ≥ 252 / 2,159. Prototype (pads only): 26 boards, RT-001 −220 nets, 0 added, 89 pad-count rewordings.
**Fix:** no number and no net for NPTH and aperture pads; no net for non-copper zones.
**Harness check (`7ed10f3e`):** pcb/routing.py:36-41 counts every pad with net_number > 0 for RT-001; reader keeps nets on np_thru_hole and non-copper pads (:514 only adds NPTH copper props). KH-417 (fixed) and KH-156 are different. No open dup.

### KH-1279: legacy bare `locked` before an `fp_text` / `gr_text` value is read as the text

**Severity:** LOW-MEDIUM (wrong references)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H3`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/reader.py:392, 394, 1752, 1811, 2084` (+ `gr_text` at `:1710, :1727`), at `de28149d`. KiCad: `pcb_io_kicad_sexpr_parser.cpp:4625-4630`.
**Symptom:** `(fp_text reference locked "RV7")` gives the reference `locked` (adeboni synth, freznel10 Chunky2040); horychen dimensions read `"locked"`.
**Reach (measured):** 58 boards / 46 repos; 76 references, 35 values and 161 user texts. The prototype changes findings on 17 boards (renames; CP-002 −12 net).
**Fix:** skip the token. Budget: renames.

**KH-590 addendum (H4): signed-integer KiCad 10 net names are taken as net ids**
`_net_id("+12")` = 12 (`pcb/reader.py:286-289`, pads `:538-539`), and `-12` passes the `lstrip("-").isdigit()` tests (`:855, :878, :1084, :1202, :1413`). Native corpus case: `cristobalcuevas/Kicad@be9ed64/HornSystem/MainBoard.kicad_pcb`, where the 54 `+5` segments are reported on `+5V` (64 tracks). Corpus: 5 KiCad 10 boards / 2 repos (`+5` ×4, `0` ×1). Upgrade lane: 11 horychen boards (CC-DET −10, RT-001 and TS-DET moves). The KH-590 fix has to treat every ≥ 20251028 `(net X)` as a name, signed or not.
**Harness check (`7ed10f3e`):** pcb/reader.py:386-394 takes ft[2] as the text; adeboni math-camp-synth synth.kicad_pcb has 6 '(fp_text reference locked' and the baseline output has 6 footprints with reference 'locked' ('No opposite-layer copper under locked'). No dup.

### KH-1278: `outline_loops` closes a chain before extending it; near-coincident Edge.Cuts ends make the outline depend on edge order

**Severity:** MEDIUM (bbox fallback on panels; results change when KiCad re-sorts)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H2`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/pcb/geometry.py:245-262` (closure test at `:254` precedes `_nearest`), at `de28149d`. KiCad: `convert_shape_list_to_polygon.cpp:936-962`.
**Symptom:** the KiKit LED BAr Panel (tab ends 0.002 mm apart) gives None on file order and 31 loops after the upgrade's re-sort; KiCad's area is 5,964.714 mm² either way.
**Reach (measured):** 62 boards / 42 repos differ between the current and an extend-first prototype. The prototype is KiCad-exact on 35, wrong on 1 (pwm-esc-littlebee), and 21 boards have no KiCad outline at all. PM-002 net +300 on 35 boards, including 223 false adds on mousebite or net-less NPTH footprints (needs the KH-1050 predicate on PM-002).
**Fix:** port KiCad's chaining (available-first, both directions, consumed → reject). Oracle: `kicad-cli pcb export stats` area.
**Harness check (`7ed10f3e`):** pcb/geometry.py:252-262 at 7ed10f3: closure test (:254) runs before _nearest and the chain grows only from the tail. ISSUES 'outline_loops' hit is the EMC area KH, not this.

### KH-1277: a placed symbol with no `(unit)` and no instance unit reads every unit's pins; KiCad uses unit 1

**Severity:** LOW-MEDIUM (phantom pins on wrong nets in standalone KiCad 6 sub-sheets)
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (Track H survey `survey-H-lane-triage.md` section 3, `KH-NEW-H1`; ruled RULINGS-12b section 4); checked by the harness at `7ed10f3e`
**File:** `skills/kicad/scripts/schematic/reader.py:869` (`unit_num = None`), `:291` and `:276` (`compute_pin_positions` falls back to all pins), at `de28149d`. KiCad: `sch_symbol.cpp:839`.
**Symptom:** Sunrise-clock `Storage.kicad_sch` puts U8 (4066) pins 2/3/9/10 on one net; the upgrade (which writes `(unit 1)`) and kicad-cli give pin 2 only.
**Reach (measured, prototype):** 20 files / 9 repos change nets; NT-001 −74, RC-DET +16 (all 16 false: op-amp feedback caps whose "ground" is the op-amp output; land with a KH-1108-family guard or budget them), DO-DET +1, RS-001 −2, DC-DET −1.
**Fix:** default unit 1. Gate: kicad-cli netlist parity on the 20 files.
**Harness check (`7ed10f3e`):** schematic/reader.py:869 at 7ed10f3 still unit_num = None when no (unit); instance overrides at :914/:936/:952 only when present; compute_pin_positions falls to all pins (:291, body>=3 branch :272-276). No dup.

### KH-1276: `skills/kicad/SKILL.md:662` lists RS-001's accepted rail sources as "no power_out pin, no PWR_FLAG, no bridged-jumper or regulator output". It already left …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 73 `skill-md-rs001-source-list`); checked by the harness at `7ed10f3e`

- Symptom: `skills/kicad/SKILL.md:662` lists RS-001's accepted rail sources as "no power_out pin, no PWR_FLAG, no bridged-jumper or regulator output". It already left out load switches at the range base, and it now also leaves out P-channel switches (`bab60583`). SKILL.md is at its 850-line ceiling.
- Evidence: `D/reviews/fixwave-review.md` Minor 3.
- Wave: 12k (docs).

**Harness check (`7ed10f3e`):** skills/kicad/SKILL.md:662 lists 'no power_out pin, no PWR_FLAG, no bridged-jumper or regulator output'; SKILL.md is 850 lines.

### KH-1274: NC pins count toward the `ic_with_internal_regulator` pin ratio (`signal_detectors.py`)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 71 `internal-regulator-ratio-counts-nc-pins`); checked by the harness at `7ed10f3e`

- Symptom: NC pins count toward the `ic_with_internal_regulator` pin ratio (`signal_detectors.py`). LM2574HVM-5.0 (SO-14, 8 NC; RobertPHeller CommonMCULCCBoard) lands as `ic_with_internal_regulator`, so it has no switching frequency and no SW-001; LM2675-5-WSON-16 (acastles91 x3) stays there too, so Task 22's 260 kHz never applies.
- Reach: 4 units (pre-existing logic exposed by the switch-output rule).
- Evidence: `D/reviews/final-R.md` M5.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** signal_detectors.py:2218-2228 counts every pin (NC included) in total_pins. acastles91 LM2675-5-WSON-16 x3 is ic_with_internal_regulator at base. But RobertPHeller CommonMCULCCBoard U? (LM2574N-3.3 on LM2574HVM-5.0, SO-14) is switching 52 kHz in a --no-hierarchy run of PowerSupply.sch; it turns ic_with_internal_regulator only in the hierarchical root run, where it shares 'U?' with TCAN332DR and ic_pins (keyed by ref + pin number) collide. **Correction:** Drop the RobertPHeller case (that one is KH-483 unannotated-duplicate merging, not NC pins: VIN/OUT/FB = 3 of 14 passes the 20 % test on its own). Reach is the 3 acastles91 units.

### KH-1273: a borrowed symbol's fixed voltage still wins in the LM78xx loop and in the `-3.3` / `3V3` / family-suffix loop (`parts.py`) when the Value names another part

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 70 `fixed-voltage-from-borrowed-symbol`); checked by the harness at `7ed10f3e`

- Symptom: a borrowed symbol's fixed voltage still wins in the LM78xx loop and in the `-3.3` / `3V3` / family-suffix loop (`parts.py`) when the Value names another part. With the divider pick (`signal_detectors.py`), the symbol voltage now also outranks a divider: `LM2596S-ADJ` on an `LM2596S-12` symbol reads 12 V with the divider ignored (at base the divider set Vout). Cases: LF33CV / LD1117V33C / K78L03 on LM7805 (5 V on +3V3 / V_BUCK); CJ78M09 and MC7809CTG on LM78M05 / LM7805 (5 V on +9V); AMS1117-5 on AMS1117-3.3 (3.3 V on +5V, x2); LM323-K on LM7812 (12 V on +5V); TPS7A0309 on MIC5365-1.8; CL9293A33 on AP2127K-1.2; mic5233 / NCP167 on MIC5205-2.5.
- Reach: 82 symbol-only fixed reads in the base sample, about 19 contradicting the value or rail (all pre-existing); 2 records with a divider changed (Insight-Wisconsin LM2586S 4.9 -> 5.0).
- Note for the `vref-from-borrowed-symbol` FIXED entry: it covers the Vref table and the fixed-output part table only.
- Evidence: `D/reviews/final-R.md` M1.
- Wave: 12c.

**Harness check (`7ed10f3e`):** lookup_regulator_vref identical on both sides: LF33CV / LD1117V33C / CJ78M09 on LM7805/LM78M05 symbols 5.0, AMS1117-5 on AMS1117-3.3 3.3, LM323-K on LM7812 12.0, TPS7A0309 on MIC5365-1.8 1.8, LM2596S-ADJ on LM2596S-12 12.0 (all fixed_suffix).

**2026-11-19 addendum (Wave 12c, `bb6fc3e0`): the product claimed a close; the harness keeps it open.** The Wave 12c filing `value-vs-symbol-precedence` (folded in here by the harness as a duplicate) shows the defect: Symptom: a bare 79xx Value loses to an LM78 / 79 symbol code. `79L05` on `Regulator_Linear:LM7812_TO220` reads +12 (probe at `ea5f7fd1`). Reach 0. Evidence: `D/reviews/task-40-review.md` M2.
  Harness check (`ea5f7fd1`): lookup_regulator_vref('79L05', 'Regulator_Linear:LM7812_TO220') = (12.0, fixed_suffix) at base and tip. KH-1273 ('a borrowed symbol's fixed voltage still wins in the LM78xx loop ... when the Value names another part') is closed in this wave (bb6fc3e0); this is the same symptom for a bare-code Value the fix does not treat as naming another part.

### KH-1271: a diode named by a TVS series (`SMF5.0A`, `SM6T...`, `P4KE...`) or described "TVS" is a TVS for PD-DET, EP-AUD, EG-001 and UC-002, but not for the diff-pair …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 68 `protection-part-tvs-diode`); checked by the harness at `7ed10f3e`

- Symptom: a diode named by a TVS series (`SMF5.0A`, `SM6T...`, `P4KE...`) or described "TVS" is a TVS for PD-DET, EP-AUD, EG-001 and UC-002, but not for the diff-pair ESD check, which uses `detector_helpers.is_protection_part` (`_PROTECTION_KEYWORDS` only). The Task 9 commit subject ("recognised the same way by every protection check") over-claims; the CHANGELOG bullet is scoped correctly.
- Fix direction: `is_protection_part` accepts `is_tvs_diode` for diodes. Output-changing on diff-pair records. Related: item 8.
- Evidence: `D/reviews/final-P.md` Minor 7.
- Wave: 12d.

**Harness check (`7ed10f3e`):** detector_helpers.py:175-197 is_protection_part matches only _PROTECTION_KEYWORDS (no _TVS_FAMILIES, no description words), while is_tvs_diode (:412) has both. Related KH-733 (diff-pair ESD over-credit, opposite direction). KH-1075's close should be scoped to PD-DET/EP-AUD/EG-001/UC-002.

### KH-1270: `_symbol_designator` reads a transistor word anywhere in the symbol name (a search, not a match): `DRV1 MyLib:IR2110_MOSFET_Driver` -> `transistor` (diode …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 67 `symbol-designator-transistor-word-anywhere`); checked by the harness at `7ed10f3e`

- Symptom: `_symbol_designator` reads a transistor word anywhere in the symbol name (a search, not a match): `DRV1 MyLib:IR2110_MOSFET_Driver` -> `transistor` (diode at base; wrong both ways).
- Reach: 0 in the 7,801 units.
- Fix direction: anchor the word forms to the start, or skip names containing `driver` / `array`.
- Evidence: `D/reviews/final-P.md` Minor 6.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** Probe: DRV1 MyLib:IR2110_MOSFET_Driver 'IR2110' = transistor at BOTH f254cb2 and 7ed10f3. **Correction:** It is not diode at base: the base also gives transistor, so this is pre-existing, not a 12b change.

### KH-1269: a two-pin TVS on a bare V reference with a custom symbol loses its protection record: `V1 MyLib:SMAJ5.0A` -> `other`; `V1 MyLib:ESD5Z5.0T1G` / `PESD5V0S1BL` …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 66 `tvs-on-bare-v-reference`); checked by the harness at `7ed10f3e`

- Symptom: a two-pin TVS on a bare V reference with a custom symbol loses its protection record: `V1 MyLib:SMAJ5.0A` -> `other`; `V1 MyLib:ESD5Z5.0T1G` / `PESD5V0S1BL` -> `ic`. Neither type enters the PD-DET diode loop, and `esd5z` is not in the IC loop's keywords.
- Reach: 0 in the 7,801 units.
- Fix direction: in `_v_letter_part`, a part that `is_tvs_diode` names with at most 2 pins -> `D`; keep ESD arrays `ic`.
- Evidence: `D/reviews/final-P.md` Minor 5.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** Probe at candidate: V1 MyLib:SMAJ5.0A = other, V1 MyLib:ESD5Z5.0T1G = ic, V1 MyLib:PESD5V0S1BL = ic (all varistor at base).

### KH-1268: `classify._symbol_name` does not strip the KiCad 4/5 `-RESCUE-<project>` form: `RC1` on `C-RESCUE-proj` stays `resistor`, while `proj-rescue:C-Device` reads …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 65 `rescue-stripper-project-form`); checked by the harness at `7ed10f3e`

- Symptom: `classify._symbol_name` does not strip the KiCad 4/5 `-RESCUE-<project>` form: `RC1` on `C-RESCUE-proj` stays `resistor`, while `proj-rescue:C-Device` reads capacitor. `detector_helpers.symbol_name` handles it. This is the "two rescue strippers to unify" cost. Related: the prefix form in item 13.
- Fix direction: strip `-rescue-<proj>` in `_symbol_name` (no import across the layer), with one test row.
- Evidence: `D/reviews/final-P.md` Minor 3.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** classify._symbol_name (classify.py:101-106) strips only '-device' or a '-rescue' nickname's last dash part: 'RC1 C-RESCUE-proj' and 'proj-rescue:C-RESCUE-proj' = resistor; 'proj-rescue:C-Device' = capacitor; detector_helpers.symbol_name (:106-118) handles -RESCUE-. Remainder of KH-1021 (closing).

### KH-1267: a regulator on a bare V reference is typed `other`: `78L05`, `KA78L05`, `AP7384-50`, `AP1231-33` (OLinuXino x3), `LM3940IMP-3.3` (jeevan9s, GiovanniRaseraF …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 64 `vr-regulator-typed-other`); checked by the harness at `7ed10f3e`

- Symptom: a regulator on a bare V reference is typed `other`: `78L05`, `KA78L05`, `AP7384-50`, `AP1231-33` (OLinuXino x3), `LM3940IMP-3.3` (jeevan9s, GiovanniRaseraF x4), `LM320K-5`, `TPSM861253RDXR`. They were varistors at base, so the false PD-DET record goes, and none was a regulator before.
- Fix direction: `_v_letter_part`: VR + a regulator value, or a VREG footprint, gives `ic`.
- Evidence: `D/reviews/final-P.md` Minor 2.
- Wave: 12c.

**Harness check (`7ed10f3e`):** Probe: VR1 MyLib:KA78L05, x:AP7384-50, x:LM320K-5 varistor -> other at candidate; on Regulator_Linear: lib they are ic. This is KH-1033's 11c addendum (KH-new-vr-regulator-varistor: map VR to a regulator), which the KH-1033 fix b66c8bae does not deliver.

### KH-1266: `Device:L_Core_Ferrite` (and L_Core_Iron) is typed `ferrite_bead` through the `ferrite` lib word in the inductor branch (`classify.py`)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 63 `ferrite-core-symbol-bead`); checked by the harness at `7ed10f3e`

- Symptom: `Device:L_Core_Ferrite` (and L_Core_Iron) is typed `ferrite_bead` through the `ferrite` lib word in the inductor branch (`classify.py`). `RF-L1`, `L1` or `L?` with a value like `22 uH` is a power inductor with a ferrite core. At base: 86 `L` refs plus 2 `FB` in 27 units. Task 6 adds 24 `RF-L` parts that were typed `resistor` at base (also wrong).
- Fix direction: only a bead / ferrite word in the value or a `Ferrite_Bead` symbol makes a bead; a value stating an inductance is an inductor. Output-changing on 27+ units.
- Evidence: `D/reviews/final-P.md` Minor 1.
- Wave: 12c.

**Harness check (`7ed10f3e`):** Probe: L1 Device:L_Core_Ferrite '22uH' = ferrite_bead on both sides; RF-L1 Device:L_Core_Ferrite '22 uH' resistor -> ferrite_bead (12b); L2 Device:L_Core_Iron = inductor.

### KH-1264: the LD-DET pull-up guard treats the far net of a drain pull-up as a supply only when it has a power name

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 60 `lddet-pullup-unnamed-supply`); checked by the harness at `7ed10f3e`

- Symptom: the LD-DET pull-up guard treats the far net of a drain pull-up as a supply only when it has a power name. A supply rail without one is missed: cbwhickstein Flipper_Zero_DIY VT5 (DMN313DLT) has R44 10k from its drain to SYS and is credited with VD4, the SYS power LED; VT5 really drives DD6.8.
- Reach: 1 record.
- Fix direction: count the IC power-input pins on the net (a net with an IC VDD / VCC pin is a supply).
- Evidence: `D/reconcile-wave12b.md` (LD-DET).
- Wave: 12d.

**Harness check (`7ed10f3e`):** Candidate hierarchical run of Flipper_Zero_DIY root: 'LD-DET LED driver VT5' with led_ref VD4 via R44 10k; R44 goes from VT5 drain to SYS, which is neither power-named nor a topology rail, so the pull-up guard (:4103-4107) passes it.

### KH-1263: LD-DET credits an LED on a P-FET's drain rail when that rail has its own source (VBUS)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 59 `lddet-pfet-drain-rail-sourced`); checked by the harness at `7ed10f3e`

- Symptom: LD-DET credits an LED on a P-FET's drain rail when that rail has its own source (VBUS). The FET switches nothing: the drain is the input. Cases: rh1tech frank_mini Q2 and frank_pga2 Q1 (AO3401A) credited with LD3 / LD4, the CH217K over-current flag LEDs on USB_OC; icl-rocketry Hardware_PDU Q6 credited with USBLED1, which sits on VBUS itself; icl-rocketry Hardware_PickleRick Q10 (DMP3099L, power mux) credited with USBLED1.
- Reach: 4 records (introduced by the lane P retypes x Task 24's P-channel reading).
- Fix direction: skip a P-FET whose drain rail has its own source (the guard `fix-rs-pfet-drain-source` builds for RS-001), or share its input-side guard. Related: item 27.
- Evidence: `D/reconcile-wave12b.md` (LD-DET), `E/progress.md` fix-wave rulings.
- Wave: 12d.

**Harness check (`7ed10f3e`):** signal_detectors.py:4070-4072 exempts a P-channel drain on a power net ('may be a switched rail') with no test that the drain rail has its own source. Units not re-run.

### KH-1262: RS-001 did not credit a rail switched by a high-side P-FET as sourced

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 58 `rs001-pfet-switched-rail`); checked by the harness at `7ed10f3e`

- Symptom: RS-001 did not credit a rail switched by a high-side P-FET as sourced. Charading Saturn60 `+5V_LED_RAIL` via Q4 AO3401A; LC* caps typed inductor used to bridge it.
- Fixed half (`bab60583`, class `fix-rs-pfet-drain-source`): a P-channel MOSFET whose source rail is sourced now sources its drain rail. RS-001 -54 / 35 units and RS-002 -2 / 1 unit (Twisted-Fields cm4) removed. Measured reach is 54 + 2, not the brief's ~507: only drains whose source rail is itself sourced can change.
- Open half: the input-side guard skips a FET (its drain stays unsourced, so RS-001 stays) when its gate is tied or pulled to ground or a rail, an IC pin named GATE drives the gate, or the drain is USB VBUS. The guard keeps all 16 hand-checked reverse-polarity / ideal-diode / USB-selector FETs and costs about 20 right removals: Benjamin-girard VBUS_USB_SW x2, greatscott hackrf VBUS_SAFE x2, frank_pga2 VBUS_USB_F x2, siderakb EXT_VCC, the gate-on-rail power muxes (tor1kk, brainsmoke, henriknelson), joeheinz Q9 x2, Jaxc x2, Wet-Lettuce, dddrrreee, tzarc x2 (direction ambiguous). Fix direction: read the gate drive (a pull-up to the source rail means a high-side switch; a pull-down to ground means a default-on input FET).
- Charading Saturn60 `+5V_LED_RAIL`: not moved. Q4's source rail `+5V_LED_SRC` is itself unsourced, so the rail keeps its RS-001.
- Evidence: `E/task-6-report.md` Minor 2; `E/fixwave-report.md` (b), with the census at `/tmp/claude-1000/w12b-fix/b/census.tsv`.
- Wave: 12c (RS-001 evidence).

**Harness check (`7ed10f3e`):** bab60583 adds the P-FET drain-source rule with the input-side guard as described (gate on ground/rail, pulled down, IC GATE pin, VBUS drain). The open half (gate-drive reading) stands; the ~20 right removals not re-measured. File alongside the straight-to-FIXED rs001-pfet-drain-source.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
the gate-drive rule moves 0 records over all 1,796 candidate units: none of the ~20 cases has a pull-up to the source without a pull-down (dividers, gates on a rail, GPIO + pull-down). A default-on high-side switch and a reverse-polarity FET have the same gate drive. Seed line for 3.1: "P-FET direction needs an input-side model (connector / battery / fuse side), not gate drive alone." (Survey S §D.)
  Harness check (`ea5f7fd1`): Not re-measured (needs the RS-001 census). Consistent with KH-1262's text; note it refutes KH-1262's own fix direction ('read the gate drive'), so the entry's fix-direction line should be superseded rather than kept beside it.

**2026-11-19 (Wave 12c plan move, handoff ask 5):** the open half → 3.1 (section C addendum above).

### KH-1261: the multi-FB pin choice in `fb_divided` (`signal_detectors.py:2289`) and the boost `output_rail` from the first FB divider (`:2371`) still use every FB …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 57 `fb-reader-dc-path-neighbours`); checked by the harness at `7ed10f3e`

- Symptom: the multi-FB pin choice in `fb_divided` (`signal_detectors.py:2289`) and the boost `output_rail` from the first FB divider (`:2371`) still use every FB divider, without Task 17's DC-path filter. A compensation leg could pick the pin or name a boost's rail.
- Reach: 0 measured.
- Evidence: `D/reviews/task-17-review.md` Minor 3.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** At candidate fb_divided (signal_detectors.py:2301-2307) and the boost output_rail loop (:2384-2392) match any divider on the FB net; only fb_vds (:2332-2334) applies _top_has_dc_path. **Correction:** Lines at 7ed10f3 are :2301 and :2384, not :2289 / :2371.

### KH-1260: an in-amp recognised only by an RG pin pair leaves OA-DET but does not join ML-001's sensitive set, because analyzer `components` carry no pin names

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 55 `inamp-predicate-residue`); checked by the harness at `7ed10f3e`

- Symptom (a): an in-amp recognised only by an RG pin pair leaves OA-DET but does not join ML-001's sensitive set, because analyzer `components` carry no pin names.
- Symptom (b): the description words match an op amp described as *for* in-amps, and `\bin-amp\b` matches "built-in-amp".
- Reach: 0.
- Evidence: `E/task-30-report.md` Fix round 1 Minors 1-2.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** parts.py:850 _INAMP_WORDS: 'built-in-amp' and 'op amp for instrumentation amplifiers' both match. (a) not re-run.

### KH-1259: the ferrite regex never accepts `kOhm`, so `FB 1kOhm@100MHz` stays an inductor (a miss)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 54 `ferrite-kohm`); checked by the harness at `7ed10f3e`

- Symptom: the ferrite regex never accepts `kOhm`, so `FB 1kOhm@100MHz` stays an inductor (a miss).
- Evidence: ledger Task 5 deferred minor.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** classify at candidate: L3 Device:L '600Ohm@100MHz' = ferrite_bead (KH-1022 fix b0bf44c8) but '1kOhm@100MHz' and '1KOHM@100MHZ' = inductor; an FB reference still gives ferrite_bead. Remainder of KH-1022 (closing).

### KH-1258: `AD7606C_18` / `AD7606C 18` (separator other than `-`) reads 16 bits via the `ad7606` stem

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 53 `adc-resolution-separator`); checked by the harness at `7ed10f3e`

- Symptom: `AD7606C_18` / `AD7606C 18` (separator other than `-`) reads 16 bits via the `ad7606` stem. MAX11606-09 (10-bit) have no row either.
- Reach: 0 in the corpus.
- Evidence: `D/reviews/task-28-review.md`, `E/task-28-report.md` follow-up 2.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** _infer_adc_resolution (domain_detectors.py:3100) at candidate: AD7606C-18 18, AD7606C_18 16, 'AD7606C 18' 16; MAX11606 / MAX11609 None (map starts at max11610).

### KH-1256: a positive buck part wired as an inverting buck-boost (GND pin on Vout, FB on GND, L from OUT to GND) gets no output rail and is not marked inverting

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 51 `inverting-buck-boost-output`); checked by the harness at `7ed10f3e`

- Symptom: a positive buck part wired as an inverting buck-boost (GND pin on Vout, FB on GND, L from OUT to GND) gets no output rail and is not marked inverting. Task 14 removed the wrong switch-node rail; the true negative output is not inferred. Case: Erhannis U1_IR12V1 LM2575HVS-12 ×2.
- Evidence: `E/task-14-report.md` hand-checks, `E/task-19-report.md` families.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** Candidate run on Erhannis inverted_regulator_12v.kicad_sch: U1_IR12V1 switching, output_rail None, inverting None, estimated_vout +12.0; U1 GND pin on net 'Vout', FB on GND, L1 OUT->GND.

### KH-1254: R-78 modules on symbols with an FB pin are typed `unknown`, because they take the FB-pin branch and the R-78 switching rule is only on the vout-pin branch

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 49 `r78-fb-pin-unknown`); checked by the harness at `7ed10f3e`

- Symptom: R-78 modules on symbols with an FB pin are typed `unknown`, because they take the FB-pin branch and the R-78 switching rule is only on the vout-pin branch. Cases: GKeyMaster regulator-daisy, williamweatherholtz 24V_to_3v3 / 24V_to_5V, entropia VXO7803-1000 on an R-78C symbol.
- Reach: 4 records.
- Evidence: `E/task-19-report.md` Fix round 1.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** signal_detectors.py:2212-2213: the 'fb_pin and not sw_pin' branch sets 'unknown' with no is_r78_module test (that test is only on the vout branch, :2199). Baseline outputs: GKeyMaster regulator-daisy U1, williamweatherholtz U4/U2, sublimelight-5g U5 VXO7803-1000 all topology unknown (4).

### KH-1250: no finding names an LDO whose set point exceeds its input rail (or VSUP − 100 mV for the HX711, datasheet p.4)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 44 `regulator-vout-vs-input-sanity`); checked by the harness at `7ed10f3e`

- Symptom (a): no finding names an LDO whose set point exceeds its input rail (or VSUP − 100 mV for the HX711, datasheet p.4). Eleven HX711 records: DPIclimate ×3 at 4.157 V, houseofbigseals ×2 and janc18 ×6 at 4.299 V, all from a 3.3 V VSUP.
- Symptom (b): no finding names a boost whose fixed Vout is at or below its input. FES_Hardware LM2586S ×2 on an `LM2586S-5.0_NOPB` symbol, boosting from +5V, now reads a deterministic 5.0 V.
- This would be new behaviour.
- Evidence: `D/reviews/task-16-review.md` Minor 3, `D/reviews/task-17-review.md` Minor 2.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** No Vout >= Vin (LDO) or Vout <= Vin (boost) check exists at 7ed10f3; the dropout block (signal_detectors.py:2636) only skips such parts. A new-behaviour request.

### KH-1249: sense amps and monitors named by neither the old keyword list nor `_SENSE_AMP_PN`:

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 43 `sense-amp-families-missing`); checked by the harness at `7ed10f3e`

- Symptom: sense amps and monitors named by neither the old keyword list nor `_SENSE_AMP_PN`:
  - AD8418 / AD8410
  - LT6106
  - MAX9918
  - MAX4372
  - NCS21671 / NCS214
  - TSC101
  - MCP6C02
  - PAC19xx (≈ 23)
  - LTC294x (≈ 11)
  - ACS37xxx (7)
- Fix direction: widen with one datasheet citation per family.
- Evidence: `D/reviews/task-29-review.md`.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** names_sense_amp() False at 7ed10f3 for AD8418, AD8410, LT6106, MAX9918, MAX4372, NCS21671, NCS214, TSC101, MCP6C02, PAC1934, LTC2944, ACS37002 (INA219/INA240 True).

### KH-1248: RF-DET types HMC1001 / HMC1002 (Honeywell magnetoresistive sensors) as `power_detector`

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 42 `rfdet-magnetometer-power-detector`); checked by the harness at `7ed10f3e`

- Symptom: RF-DET types HMC1001 / HMC1002 (Honeywell magnetoresistive sensors) as `power_detector`. The FCC suggestion on Benjamin-girard magnetometer-node ×2 now names them (Task 27 made the list visible).
- Evidence: `E/task-27-report.md` Unexpected.
- Wave: 12d.

**Harness check (`7ed10f3e`):** rf_power_detector_keywords (domain_detectors.py:1067-1068) holds 'hmc10', meant for Hittite HMC1010/1020/1030, and it also matches Honeywell HMC1001/HMC1002.

### KH-1247: a diode lib_id named after its SMA package (`D_SMA`, `1SMA…`, `SMA6J`) still seeds RM-DET by the `sma` word

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 41 `rmdet-sma-package-diode-seed`); checked by the harness at `7ed10f3e`

- Symptom: a diode lib_id named after its SMA package (`D_SMA`, `1SMA…`, `SMA6J`) still seeds RM-DET by the `sma` word.
- Reach: 0 in the corpus.
- Fix direction: require `type == connector` for the word seed.
- Evidence: `D/reviews/task-3-review.md` Minor 2.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** _SMA_WORD (domain_detectors.py:1340) matches 'd_sma', 'diode:1sma5913', 'sma6j' (probe True); the seed has no type test.

### KH-1246: RM-DET labels GNSS active-antenna bias tees (27 nH + 10 nF / 47 p from VCC_RF at MAX-M8Q / M10S / NEO-M8/M9) as `L_match`

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 40 `rmdet-bias-tee`); checked by the harness at `7ed10f3e`

- Symptom: RM-DET labels GNSS active-antenna bias tees (27 nH + 10 nF / 47 p from VCC_RF at MAX-M8Q / M10S / NEO-M8/M9) as `L_match`. The classifier has no bias-feed notion.
- Reach: 16 of the 106 coax-seed adds, plus the same shape on existing seeds.
- Evidence: `D/reviews/task-3-review.md` Minor 1.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** RM-DET topology labels (domain_detectors.py:~1501) have no bias-feed case; an L to a power net counts as a matching element. Count not re-measured.

### KH-1245: on the legacy `.sch` Alimach MiniElectronicClock `Часы ЧЭМ-1.sch`, VCC and GND merge

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 39 `legacy-net-merge-alimach`); checked by the harness at `7ed10f3e`

- Symptom: on the legacy `.sch` Alimach MiniElectronicClock `Часы ЧЭМ-1.sch`, VCC and GND merge. C4 and now VD6 get false SP-001 "both pins on VCC"; the PCB has them on VCC/GND.
- Reach: 1 unit.
- Evidence: `E/task-7-report.md` known-false 1.
- Wave: 12e (legacy reader).

**Harness check (`7ed10f3e`):** 365aea9 output 'Часы ЧЭМ-1.sch': SP-001 'C4 (100n) has both pins on net VCC'. No open KH names this board. **Correction:** VCC and GND do not merge: C4 pin 2 and VD6's second pin are read onto VCC instead of GND (a per-pin legacy wire/junction read), the two nets stay distinct.

### KH-1244: the snubber detector reads a gate RC delay as a snubber (Flipper DIY R44 10 k / C68 10 µF on VT5; the R603/C602 τ 0.47 s warn in Task 2's A/B), so SPICE warns

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 38 `snubber-on-gate-rc`); checked by the harness at `7ed10f3e`

- Symptom: the snubber detector reads a gate RC delay as a snubber (Flipper DIY R44 10 k / C68 10 µF on VT5; the R603/C602 τ 0.47 s warn in Task 2's A/B), so SPICE warns.
- Evidence: `E/task-7-report.md` known-weak 3, `E/task-2-report.md` SPICE hand-check.
- Wave: 12g.

**Harness check (`7ed10f3e`):** signal_detectors.py:3806-3830: any R from the drain to a node with a C to the source is a snubber, with no value or tau bound. **Correction:** R44/C68 is not a gate RC delay: it is a drain pull-up to the unnamed SYS supply plus that supply's bulk cap. The defect is that the snubber test accepts an R to any non-power-named net (a supply rail) and a cap from there to the source.

### KH-1243: the `VC` full prefix types grid-referenced 74LS chips as capacitors; their VA/VB/VD neighbours are now ic

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 37 `vc-prefix-logic-as-cap`); checked by the harness at `7ed10f3e`

- Symptom: the `VC` full prefix types grid-referenced 74LS chips as capacitors; their VA/VB/VD neighbours are now ic. They show up as fake caps in DO-DET decoupling lists.
- Reach: 162 parts / 11 jotego units.
- Evidence: `E/task-7-report.md` KH (a).
- Wave: later 3.0.3 (with the V-letter follow-ups).

**Harness check (`7ed10f3e`):** cc('VC4','74xx:74LS00','74LS00') = capacitor; VA1/VB2/VD3 on the same symbol = ic at 7ed10f3 (type_map 'VC': capacitor, classify.py:193).

### KH-1242: RC-DET pairs a gate resistor with a cap whose far node is not ground (SOLENOIDR4/C1 "5.3 MHz")

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 36 `rcdet-nonground-cap`); checked by the harness at `7ed10f3e`

- Symptom: RC-DET pairs a gate resistor with a cap whose far node is not ground (SOLENOIDR4/C1 "5.3 MHz").
- Related: KH-1108 and H1's output-pin guard.
- Evidence: `E/task-6-report.md` known-false 8.
- Wave: 12j.

**Harness check (`7ed10f3e`):** detect_rc_filters emits a cap with a non-ground far end on purpose as filter_type 'RC-network' (signal_detectors.py:713-719). The R4/C1 record is not in the 365aea9 solenoid outputs (candidate-side only). **Correction:** A non-ground far node alone is by design; the KH must say what is wrong (a gate resistor paired with a gate-to-drain/source cap) and give the repo and file (SOLENOIDR4 reads like a run-together repo + ref). Frame it as the 'RC-network' branch accepting any non-ground cap far node (gate R + cap, op-amp output), not as a missing ground check in the low-pass path.

### KH-1241: LC-DET reads a series coupling capacitor as the shunt capacitor of a filter, because it does not check that the cap's far node is ground (Wii-Mini-Hacking …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 35 `lcdet-series-coupling-cap`); checked by the harness at `7ed10f3e`

- Symptom: LC-DET reads a series coupling capacitor as the shunt capacitor of a filter, because it does not check that the cap's far node is ground (Wii-Mini-Hacking miniRGBii FIL15 + C69 220 µF, "17 kHz").
- Evidence: `E/task-6-report.md` Minor 2.
- Wave: 12g or 3.1.

**Harness check (`7ed10f3e`):** detect_lc_filters (signal_detectors.py:818-900) never tests that the cap's far net is ground; summary 'LC filter at N Hz'.

**2026-11-19 addendum (Wave 12c gate, harness find):** the 8 moto-gps-waveshare copies that gain the declared BTST LC-DET (`lc-det-btst-bootstrap`) also gain 8 undeclared false LC-DET records, L3 + C31 at 61 MHz: C31 is a series DC-block whose far side is not ground. Both read once `27569ef5` (`v-value-forms`) reads the symbol-name values. Harness check (`ea5f7fd1`): All 9 confirmed in both the harness gate tree (results/v303_w12c_gate, baseline 0 LC-DET on all 9) and D/corpus-tip-ea5f7fd: rover-mppt-pcb L1(L8u2)+C7(C47n) 256 kHz, C7 on __unnamed_0 with U1 BTST1/D1 K and VSW (U1 SW1); moto-gps-waveshare 8 units L1+C7 734127 Hz, C7 on BQ_BTST (U2 BTST) / BQ_SW (U2 SW). The 9th moto unit hardware_pcb_moto-gps-rev-a.kicad_sch has 0. _BOOTSTRAP_PIN_TOKENS is at signal_detectors.py:55 = {BST, BOOT, BOOTSTRAP, CBST}. Related: KH-138 (FIXED, bootstrap LC exclusion) and KH-1241 (open: LC-DET never tests the cap's far net is ground; would also catch this). UNDECLARED co-movers on the same 8 moto units: +8 LC-DET L3(68nH)+C31(100pF) at 61 MHz where C31 is a series DC-block (GNSS_ANT_BIASED -> GNSS_RF_MATCH_IN, far node not ground) = KH-1241 class, newly reached by the value reader; rover also +1 L1+C5 (C5 on SR+/GND, plausible output filter).

**2026-11-19 (product 12c acceptance):** the moto-gps L3 + C31 records (on `GNSS_ANT_BIASED`) confirmed; the product's hand check had read only the L1 / C7 record. Wave 12d, with KH-1317.

### KH-1240: the regulator inductor pick does not require the inductor to sit on the switch net

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 34 `regulator-inductor-off-sw-net`); checked by the harness at `7ed10f3e`

- Symptom: the regulator inductor pick does not require the inductor to sit on the switch net. Obsidian U11/U4/U6 (no-hierarchy) moved from LED LD2 to ferrite L11, which is not on the sw net; wrong before and after.
- Reach: 3 records.
- Evidence: `E/task-6-report.md` known-false 7.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** signal_detectors.py:2162-2167: when the sw net has no inductor, the fallback calls ctx.nq.trace_through(sw_net, ref) with the regulator's own ref, which returns every other net of the regulator (netlist_queries.py:109-116), and takes the first one with an inductor. **Correction:** Name the cause: the '1-hop through connectors' fallback traces through the regulator itself, so any inductor/ferrite on any of its nets (VIN filter) is picked. Name the mechanism: the '1-hop through connectors' fallback passes the regulator itself to trace_through, so it scans all the regulator's pin nets, not a connector hop.

### KH-1239: the full-prefix `A` map types `A_`-prefixed passives on `Device` R/C symbols as ic (jotego twin16 A_C43 100 nF, A_R52 / A_R53 3.3 k), so they count as ICs …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 33 `full-prefix-a-passives-ic`); checked by the harness at `7ed10f3e`

- Symptom: the full-prefix `A` map types `A_`-prefixed passives on `Device` R/C symbols as ic (jotego twin16 A_C43 100 nF, A_R52 / A_R53 3.3 k), so they count as ICs in DA-001 and DO-DET.
- Reach: 2 DA-001 records measured.
- Evidence: `E/task-6-report.md` Minor 2.
- Wave: later 3.0.3 (with unmapped-letter-symbol).

**Harness check (`7ed10f3e`):** cc('A_C43','Device:C','100nF') and cc('A_R52','Device:R','3.3k') = ic at 7ed10f3 (type_map 'A': 'ic', classify.py:209).

### KH-1238: PU-001 reads a 0 Ω strap to a rail (Board-Folk NeoGeoAES PAL1 tying INT to VCC) as a "pull-up value too low (0R)"

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 32 `pu001-zero-ohm-tie`); checked by the harness at `7ed10f3e`

- Symptom: PU-001 reads a 0 Ω strap to a rail (Board-Folk NeoGeoAES PAL1 tying INT to VCC) as a "pull-up value too low (0R)".
- Reach: 4 records.
- Evidence: `E/task-6-report.md` Minor 2.
- Wave: 12d.

**Harness check (`7ed10f3e`):** validation_detectors.py:366-372: pu['ohms'] < pu_min with ohms 0 gives 'value too low (0R)'; no zero-ohm skip.

### KH-1236: STEF4S (ST eFuse) is recorded as PD-DET `esd_ic` through the `Power_Protection:` library rule (dynamium sBMS ×2)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 30 `efuse-as-esd-ic`); checked by the harness at `7ed10f3e`

- Symptom: STEF4S (ST eFuse) is recorded as PD-DET `esd_ic` through the `Power_Protection:` library rule (dynamium sBMS ×2).
- Evidence: `E/task-10-report.md` "still null".
- Wave: 12d.

**Harness check (`7ed10f3e`):** signal_detectors.py:3011 is_protection_lib = 'power_protection:' in lib admits any IC. 365aea9: dynamium/sbms U58/U59 STEF4S = esd_ic on kicad_sBMS and kicad_PowerManagement (2 per unit).

### KH-1235: an SD103AWS Schottky ("Schottky Barrier Diode") drawn on `Diode:1.5KExxA` is read as a TVS by the `1.5ke` protection name in the lib_id, so it credits VBUS …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 29 `protection-name-from-lib-over-value`); checked by the harness at `7ed10f3e`

- Symptom: an SD103AWS Schottky ("Schottky Barrier Diode") drawn on `Diode:1.5KExxA` is read as a TVS by the `1.5ke` protection name in the lib_id, so it credits VBUS ESD protection.
- Reach: 1 record (known-false).
- Evidence: `D/reviews/task-9-review.md` Minor 1.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** is_tvs_diode({'value':'SD103AWS','lib_id':'Diode:1.5KExxA','description':'Schottky Barrier Diode'}) = True at 7ed10f3 (detector_helpers.py:412-420 reads value + full lib_id).

### KH-1234: bcflight's `bus_analysis` lists a net named GND as an I2C SDA / SPI MOSI line

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 28 `bus-net-ground`); checked by the harness at `7ed10f3e`

- Symptom: bcflight's `bus_analysis` lists a net named GND as an I2C SDA / SPI MOSI line. It also lists antennas AE1/AE2 as bus devices, and after Task 4 DC1 as well.
- Reach: pre-existing, not sized.
- Evidence: `E/task-4-report.md` bus_analysis.
- Wave: 12d (I2C names).

**Harness check (`7ed10f3e`):** 365aea9 dridri/bcflight cm4_drone: design_analysis.bus_analysis.i2c has net 'GND' line SDA with devices incl. AE1/AE2 (each device once per pin, 68 entries); spi lists AE1/AE2. Not covered by KH-976/878/735.

### KH-1233: LD-DET credits a P-channel reverse-polarity, power-path or ORing FET whose drain is the input rail as the driver of that rail's power LED. The netlist alone …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 27 `lddet-pfet-input-rail`); checked by the harness at `7ed10f3e`

- Symptom: LD-DET credits a P-channel reverse-polarity, power-path or ORing FET whose drain is the input rail as the driver of that rail's power LED. The netlist alone cannot tell it from a high-side switch; the gate drive can.
- Reach: 31 listed records, plus an estimated 20-25 of the 73 unclassified P-channel rail-drain records.
- Evidence: `E/task-26-report.md` known-false 3-4.
- Wave: 12d.

**Harness check (`7ed10f3e`):** The guard at signal_detectors.py:4071-4073 exempts P-channel drains on a rail; no gate-drive or input-rail test follows.

### KH-1232: an LED sitting directly on a transistor's drain, collector or emitter (no resistor on that net) is not credited as transistor-driven, because the enrichment …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 26 `led-on-transistor-terminal-not-credited`); checked by the harness at `7ed10f3e`

- Symptom: an LED sitting directly on a transistor's drain, collector or emitter (no resistor on that net) is not credited as transistor-driven, because the enrichment follows only a resistor on the drain net. The LED audit then calls the drive `ic_direct`.
- Reach: 22 LA-AUD records (listed in known-false).
- Related: KH-740.
- Evidence: `E/task-26-report.md` known-false 1.
- Wave: 12d.

**Harness check (`7ed10f3e`):** enrich_transistor_led_drivers (signal_detectors.py:4079-4115) only follows a resistor on the load net to an LED; an LED pin directly on the drain/collector/emitter is never credited. Distinct from KH-740.

### KH-1231: TR-DET records carry no NPN/PNP reading, although lib_id, keywords and description carry it (on the remainder: 74 NPN / 9 PNP / 34 unread)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 25 `bjt-polarity-unread`); checked by the harness at `7ed10f3e`

- Symptom: TR-DET records carry no NPN/PNP reading, although lib_id, keywords and description carry it (on the remainder: 74 NPN / 9 PNP / 34 unread). With it, the Task 26 N/NPN-on-rail rule would remove about 74 more false LD-DET: jotego TR1-3, emitter followers, phototransistors.
- Reach: 117 BJT LD-DET with a collector on a rail (198-unit census).
- Partly fixed in this wave (`35e61947`, class `fix-lddet-npn-collector`): a BJT that reads NPN from the symbol, keywords, description or one of 50 cited part numbers, with its collector on a supply rail, is an emitter follower. 102 LD-DET records are relabelled TR-DET. Open: BJTs whose polarity is not read, and the PNP side (which keeps today's reading).
- Evidence: `E/task-26-report.md` known-false item 5, Fix round 2 KH 2.
- Wave: 12d.

**Harness check (`7ed10f3e`):** 35e61947/7ed10f3e add _names_npn (signal_detectors.py:3659-3671, 50 NPN part numbers in parts.py:789) used only in the LED enrichment; TR-DET records still carry no NPN/PNP field. Wording matches.

**2026-11-19 addendum (Wave 12c filing `spice-pnp-by-part-name`, `kh-filings-wave12c.md` B item 43, folded in by the harness as a duplicate):** Symptom: the SPICE transistor bench treats a PNP named only by its part number (BC857, 2N3906) as NPN. Pre-existing. Check KH-1231 first. Evidence: `D/reviews/task-37-review.md`.
  Harness check (`ea5f7fd1`): spice_templates.py:1193 is_pnp = 'PNP' in lib_id only (also spice_results.py:541); Transistor_BJT:BC857 / 2N3906 lib_ids carry no 'PNP', so the bench uses NPN_GENERIC. KH-1231 (open) is the missing NPN/PNP reading on TR-DET; the bench is its consumer and would take the TR-DET field once it exists. Addendum to KH-1231: the SPICE transistor bench (spice_templates.py:1193, spice_results.py:541) reads polarity from 'PNP' in lib_id only, so a PNP on a part-number symbol (Transistor_BJT:BC857, 2N3906) is benched as NPN; it should read the TR-DET polarity once KH-1231 adds it.

### KH-1228: `_PCHANNEL_FET_RE` allows only letters after the entry, so onsemi orderables `NTR4171PT1G`, `NTR2101PT1G`, `NTD25P03LT4G` and `BSS84LT1G` read N. This is a …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 22 `pchannel-onsemi-orderable-tail`); checked by the harness at `7ed10f3e`

- Symptom: `_PCHANNEL_FET_RE` allows only letters after the entry, so onsemi orderables `NTR4171PT1G`, `NTR2101PT1G`, `NTD25P03LT4G` and `BSS84LT1G` read N. This is a false negative only.
- Reach: 9 schematic files.
- Fix direction: allow an optional `T\dG` tail, with a test.
- Evidence: `D/reviews/task-24-review.md` Minor 1.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** names_pchannel_fet('NTR4171PT1G'/'NTR2101PT1G'/'NTD25P03LT4G'/'BSS84LT1G') = False, bare stems True (parts.py:776-778 tail [A-Z]{0,6}(?![A-Z0-9])).

### KH-1227: TR-DET `drain_is_power` = `is_power(drain) or (is_pchannel and is_power(source))`, and `is_power_net` includes ground

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 21 `trdet-drain-is-power-ground-source`); checked by the harness at `7ed10f3e`

- Symptom: TR-DET `drain_is_power` = `is_power(drain) or (is_pchannel and is_power(source))`, and `is_power_net` includes ground. So a P-channel FET with its source on GND reports `drain_is_power: true`.
- Reach: 25 of the 620 Task 24 flips (7 F-P6 2N7002 + 18 real P parts: eddyem stm32samples AO3407 ×8, michelkeijzers fraxis AO3401A ×8, artseyio, guanix). Library P symbols already showed it at `de28149d`.
- Fix direction: add `and not ctx.is_ground(source_net)`. This needs a budget for library P parts.
- Evidence: `E/task-24-report.md` Concern 1.
- Wave: 12d.

**Harness check (`7ed10f3e`):** signal_detectors.py:3894 drain_is_power = is_power_net(drain) or (is_pchannel and is_power_net(source)); is_power_net_name('GND'/'AGND'/'VSS') = True at 7ed10f3.

### KH-1226: a KiCad 6 sub-sheet analysed on its own reads a placed symbol's Value as `''`, although the sub-sheet file holds it (`(property "Value" …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 20 `subsheet-value-dropped`); checked by the harness at `7ed10f3e`

- Symptom: a KiCad 6 sub-sheet analysed on its own reads a placed symbol's Value as `''`, although the sub-sheet file holds it (`(property "Value" "LP5907MFX-1.2/NOPB")`, `fpga.kicad_sch:4085`) and so does the root's `symbol_instances`. CapableRobot capable_jetson_carrier `fpga.kicad_sch` U13 then gets a false PP-DET `load_switch` from its MIC20XX symbol.
- Reach: not sized.
- Evidence: `D/reviews/task-12-review.md` Minor 1.
- Wave: 12e.

**Harness check (`7ed10f3e`):** 7ed10f3 --no-hierarchy run on CapableRobot fpga.kicad_sch: U13 value '' (file :4085 and root symbol_instances :1843 both say LP5907MFX-1.2/NOPB), lib MIC20XX; PP-DET load_switch + DO-DET on U13. No open KH covers it.

### KH-1225: CERT-001 suggests CE RED only for an RF chain, never for a wireless module

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 19 `cert-ce-red-modules`); checked by the harness at `7ed10f3e`

- Symptom: CERT-001 suggests CE RED only for an RF chain, never for a wireless module. A lone ESP32-WROOM board (LoRa-PV after Task 1) gets FCC Part 15 without CE RED.
- The CE RED `reason` also says "RF transceiver detected" for a chain with no transceiver.
- Evidence: `E/task-1-report.md` Concern 2, `D/reviews/task-27-review.md`.
- Wave: 12d.

**Harness check (`7ed10f3e`):** domain_detectors.py:5626-5675 at 7ed10f3: CE RED only in the rf_chains branch, with reason 'RF transceiver detected' even when parts come from chain components (no transceivers); the module branch adds FCC Part 15 only. Residue of KH-999/1000 (closed in 12b).

### KH-1224: the Fanstel BT840 / BT840F nRF52840 module is in no WL-001 / CERT-001 radio list

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` B item 18 `bt840-radio-family`); checked by the harness at `7ed10f3e`

- Symptom: the Fanstel BT840 / BT840F nRF52840 module is in no WL-001 / CERT-001 radio list. On FreeSK8 NRF52 dongle U1, the board's only FCC hint came from a crystal's rescue name, and Task 1 removed that.
- Evidence: `E/task-1-report.md` Concern 1.
- Wave: 12d.

**Harness check (`7ed10f3e`):** No 'bt840'/'fanstel' in any product list. FreeSK8 NRF52 Dongle at 365aea9: CERT-001 'Wireless module detected: Y1' (crystal's rescue name carries the project's nRF52); symbol_name now strips that suffix, so U1 BT840F leaves no hint.

### KH-1223: difference amps (`Amplifier_Difference:AD8276`, INA105/117/13x/14x) fall to `comparator_or_open_loop` in OA-DET, for the same reason as KH-1018

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 17 `difference-amp-opamp`); checked by the harness at `7ed10f3e`

- Symptom: difference amps (`Amplifier_Difference:AD8276`, INA105/117/13x/14x) fall to `comparator_or_open_loop` in OA-DET, for the same reason as KH-1018.
- Reach: E 15-40 records.
- Evidence: `D/surveys/survey-E.md`.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** is_instrumentation_amp('AD8276', library='Amplifier_Difference') and INA105/117/133/149 = False at 7ed10f3 (parts.py:841-866 cover Amplifier_Instrumentation and in-amp PNs only). Same shape as KH-1018 (closed in 12b).

### KH-1222: a feedback chain with a two-resistor bottom arm, or FB behind a series resistor, is not read as a divider

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 16 `fb-series-chain`); checked by the harness at `7ed10f3e`

- Symptom: a feedback chain with a two-resistor bottom arm, or FB behind a series resistor, is not read as a divider. KH-1007 removed the 82 partial series-arm records; reading the full chain would add divider records and estimates. KH-1005 (`_merge_series_dividers`) is its home.
- Evidence: `D/surveys/survey-D1.md`, `E/task-20-report.md` reach split.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** _merge_series_dividers (signal_detectors.py:399) extends only through pass-through nodes with no IC pin, so a bottom arm whose junction is the FB pin, or FB behind a series R, is not chained. task-20 report items 6-13 list the shapes. Distinct from KH-1005 (duplicate sub-pair record), which is only the fix site.

### KH-1221: some real RF networks were found only from a wrong `sma`-in-word seed, and the seed fix loses them

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 15 `rm-det-seed-gaps`); checked by the harness at `7ed10f3e`

- Symptom: some real RF networks were found only from a wrong `sma`-in-word seed, and the seed fix loses them. Causes:
  - an antenna typed `ic` becomes the walk's target IC (OtterCam AE1 U.FL);
  - a 0R series resistor stops the walk (mikoto R11);
  - the RF-IC word list lacks AP62xx;
  - CONSMA / BWSMA connector part numbers are missed.
- Reach: E 300-370 lost true records. Examples: brendose RFM69, JFI12 nRF24, OLIMEX SX1276, EnhancedRadioDevices RFM95, GoodEarthWeather HF LPF.
- Evidence: `D/surveys/survey-E.md`, `E/task-3-report.md` hand-checks.
- Wave: 3.1.

**Harness check (`7ed10f3e`):** detect_rf_matching (domain_detectors.py:1346-1460): the BFS admits only capacitor/inductor/ferrite_bead (the 'ohms' field is dead); the first `ic` met becomes target_ic; _rf_keywords lack ap62; _SMA_WORD misses 'consma' / 'bwsma-kwe' (probe False). **Correction:** Any series resistor stops the walk, not only a 0R one (resistors are never admitted).

### KH-1220: `tools/tests/test_extraction_binding.py::MergeLocalPath::test_pdf_outside_datasheets_is_kept_as_given` fails when the tree lives under `/tmp`

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 14 `extraction-test-path`); checked by the harness at `7ed10f3e`

- Symptom: `tools/tests/test_extraction_binding.py::MergeLocalPath::test_pdf_outside_datasheets_is_kept_as_given` fails when the tree lives under `/tmp`.
- Evidence: `D/surveys/survey-D2.md`.
- Wave: 12k or any test-hygiene slot.

**Harness check (`7ed10f3e`):** merge_results.py:148-155 _local_path resolves the relative 'x.pdf' against the cwd and relativises it to cache.parent (= the TemporaryDirectory's parent, $TMPDIR). **Correction:** It fails when the test's cwd is under $TMPDIR (the temp cache's parent), not because the tree lives under /tmp as such. A product test-hygiene item.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
still reproduces. `test_pdf_outside_datasheets_is_kept_as_given` gives `'claude-1000/w12c-final/rerev/<sha>/x.pdf' != 'x.pdf'` on `git archive` exports of `79bce2e3` and `ea5f7fd1` under `/tmp`, and passes in the worktree.
  Harness check (`ea5f7fd1`): Reproduced at ea5f7fd1: git archive of skills/ + tools/ into a dir under /tmp, pytest from tools/tests: AssertionError 'claude-1000/.../tools/tests/x.pdf' != 'x.pdf' (1 failed). TMPDIR unset, so the temp cache's parent is /tmp and the cwd is under it. **Correction:** Keep 'still reproduces at 79bce2e3 / ea5f7fd1', but word the trigger as in the harness correction already on KH-1220: it fails when the test's cwd is under $TMPDIR (the temp cache's parent), not because the tree is a git-archive export under /tmp as such.

### KH-1219: these detectors still build `combined = value + full lib_id`, so a library nickname can admit a part:

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 13 `nickname-readers`); checked by the harness at `7ed10f3e`

- Symptom: these detectors still build `combined = value + full lib_id`, so a library nickname can admit a part:
  - eleven domain detectors (`domain_detectors.py:2416, 2605, 2827, 3647, 3834, 4148, 4255, 4382, 4557, 4685, 5136` at `de28149d`);
  - RS-001's load-switch set;
  - the PR power-dissipation sub-topology;
  - `_non_reg_ic_keywords`;
  - PS-001's `match_ic_keywords`. Task 13 measured AP2112 in an `Adafruit ESP32 Feather` library listed as its own sequencing load; Task 15's self-load guard hides it but does not remove the nickname read.
- Also: the prefix rescue form `<proj>-rescue_<sym>-<lib>` (about 100 parts) is not stripped by `symbol_name`.
- Evidence: `D/surveys/survey-D2.md`, `E/task-13-report.md` Concern 1, `D/reviews/task-1-review.md` Minor 3.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** The 11 cited lines at f254cb2 are all 'combined = val + " " + lib' with lib = full lib_id (at 7ed10f3 they sit at :2431, :2621, :2843, ...). symbol_name('x-rescue:x-rescue_AMS1117-Regulator_Linear') is returned unchanged (detector_helpers.py:106-120). **Correction:** The list is not complete: domain_detectors.py at 7ed10f3 has at least 14 more value + full-lib_id reads (val_lib at :311, 456, 623, 693, 721, 886, 943, 1097, 1234, 1568, 1779, 1851, 1906, 2053). symbol_name also leaves the once-rescued '<name>-<library>' form in a '<project>-rescue' library that its own docstring claims to strip.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
`power_budget` keyword matching also reads project-library nicknames (`RetroWiFiModem`, `Custom_ESP32`). The KiCad stock nicknames (`Amplifier_Operational`, `Interface_USB`) are useful category words there: 11,669 estimates / 4,729 units use them. Strip only non-stock nicknames. (Survey B.)
  Harness check (`ea5f7fd1`): system_analyses.py:1630-1637 (analyze_power_budget): search_str = value.lower() + ' ' + lib_id.lower() (full lib_id incl. nickname) matched against ic_current_estimates. KH-1219's list does not name power_budget, so this adds a consumer; no contradiction. 11,669 / 4,729 not re-measured.

### KH-1217: thermal TP-001 reports "0.0 mm from Ux" for every MLCC on a PCB whose footprints all sit at the origin

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 11 `thermal-unplaced-tp001`); checked by the harness at `7ed10f3e`

- Symptom: thermal TP-001 reports "0.0 mm from Ux" for every MLCC on a PCB whose footprints all sit at the origin. oihdesigns Isolated_ADS1256 gives 73 records in 2 units; Task 13's restored TPS7A4901 adds 62 of them.
- Evidence: `D/surveys/survey-D2.md`, `E/task-13-report.md` thermal.
- Wave: 12f.

**Harness check (`7ed10f3e`):** analyze_thermal.py:695-745 has no unplaced-board test. Micro-DMM Isolated_ADS1256: 75/75 footprints at (0,0); 7ed10f3 sch+pcb+thermal run gives 62 TP-001, all 'is 0.0mm from U2 (TPS7A4901DGNR)' (0 at 365aea9).

### KH-1216: DRV8874 / DRV8876 / DRV8245 motor-driver pins `OUT1`/`OUT2` strip to `OUT` and read as a regulator output (PR-DET `ic_with_internal_regulator` on a motor net)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 10 `motor-driver-out-pins`); checked by the harness at `7ed10f3e`; part list corrected by the product's 12b acceptance reply (2026-11-17)

- Symptom: the pin-role parse strips trailing digits (`signal_detectors.py:1877`), so `OUT1`/`OUT2` read as `OUT` (Vout) and `IN1`/`IN2` as `IN` (Vin). DRV8874 / DRV8876 / DRV8245 motor drivers then get a PR-DET `ic_with_internal_regulator` record whose rail is a motor output net, plus a DO-DET "missing capacitors" twin.
- Reach (product list, re-counted by the harness on the 12b std candidate snaps): 17 PR-DET records + 17 DO-DET twins in 10 units: edwindertien/foundscape anarchitechno-box U11/U12/U20/U21 (DRV8245); humanlab-network/bionico U5; bismarx-v1/Sumec-MiniSumo-HW MK IV IC2/IC3, MK V Pro U2/U3, MK V IC2/IC3 (DRV8874); airsoftak25/NeoSumec MK3 v1.5 IC1/IC2 (DRV8874); brown-studios/minuet v3 + v4 U6 and MadsRudolph/curtain-drive (both revs) U2 (DRV8876). Also Filip83 BuildingBlocks U45 DRV8837 (PR-DET LDO, input rail `IN1`). DRV8301 / DRV8302 / DRV8323 records on +5V / VDD / VCC are right (real internal regulators) and stay.
- Evidence: `D/surveys/survey-D2.md` "New KHs" (it named DRV8871 / DRV8243 / DRV883x, the wrong parts: 0 PR-DET on 63 such files).
- Wave: 12d.

### KH-1214: `usb_esd_ic` (`schematic/system_analyses.py:2652`) and EMC IO-001's PCB value list (`emc_rules.py:966`) keep their own ESD word lists, separate from the new …

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 8 `usb-esd-ic-list`); checked by the harness at `7ed10f3e`

- Symptom: `usb_esd_ic` (`schematic/system_analyses.py:2652`) and EMC IO-001's PCB value list (`emc_rules.py:966`) keep their own ESD word lists, separate from the new `detector_helpers.is_tvs_diode`.
- Evidence: `D/surveys/survey-F.md`.
- Wave: later 3.0.3.

**Harness check (`7ed10f3e`):** system_analyses.py:2651-2662 at 7ed10f3 (usb_esd_ic loop over esd_keywords, value + full lib_id) and emc_rules.py:966-968 (own ESD word tuple) do not call detector_helpers.is_tvs_diode (:412). No open KH covers it (KH-1075 lists other word lists).

### KH-1213: LM2676 and LM2678 run at 260 kHz (SNVS031N / SNVS029L p1) but have no `_KNOWN_FREQS` row

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 6 `lm2676-lm2678-frequency`); checked by the harness at `7ed10f3e`

- Symptom: LM2676 and LM2678 run at 260 kHz (SNVS031N / SNVS029L p1) but have no `_KNOWN_FREQS` row. 1 LM2676 is typed LDO, and about 7 LM2678 records sit at the 500 kHz default.
- Evidence: `D/surveys/survey-C.md` C-P5.
- Wave: 12g or a table follow-up.

**Harness check (`7ed10f3e`):** lookup_switching_freq('LM2676'/'LM2678'/'LM2678S-12') = None at 7ed10f3 (no _KNOWN_FREQS row, parts.py:500). 365aea9 outputs: LM2678 x6 at 500 kHz topology_default (SAP-Extended x2, Medulla x4) + LM2676SX-12 x1; 7 more LM2678 records are topology unknown with no frequency. alorenzo175 isensor_olinuxino LM2676: LDO at 365aea9, switching/500 kHz default at 7ed10f3 (run). **Correction:** '1 LM2676 is typed LDO' is stale at the candidate (now switching at the 500 kHz default). The 500 kHz count is 6 LM2678 + 1 LM2676, plus 7 LM2678 typed unknown.

### KH-1211: stepper/bridge-driver sense pins `BRA`/`BRB` (TMC7300, TMC22xx) are not read as sense pins

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 4 `driver-bridge-sense`); checked by the harness at `7ed10f3e`

- Symptom: stepper/bridge-driver sense pins `BRA`/`BRB` (TMC7300, TMC22xx) are not read as sense pins. Their shunts are real sense resistors, but they only matched by luck before; RCMgames RCM-Hardware-BYTE R3-R10 (−8 CS-DET) is lost by design under E-P4.
- Reach: 95 units carry BRA/BRB pins (rg).
- Evidence: `D/surveys/survey-E.md`, `E/task-29-report.md`.
- Wave: 12d.

**Harness check (`7ed10f3e`):** BRA/BRB in neither _SENSE_PIN_PREFIXES (signal_detectors.py:1433) nor _integrated_csa_pins (:1614). Follow-on to KH-1025 (closed in 12b; its Corpus note ISSUES.md:1076 already records the BRA/BRB luck). Reach 95 units not re-measured.

### KH-1209: `RV` + `Device:R_Trim` is typed varistor (21 parts / 11 units)

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 2 `rv-trim-varistor`); checked by the harness at `7ed10f3e`

- Symptom (a): `RV` + `Device:R_Trim` is typed varistor (21 parts / 11 units).
- Symptom (b): a trimmer on a V reference whose pot evidence sits only in the footprint (`Potentiometer_*`) or the description ("trim pot") is typed `other`, not resistor. About 25 parts: Anteater 3296Y ×12, GoodEarthWeather and JavQuiroga 3296W, mighty-mppt PV36W.
- Fix direction: the pot override reads footprint + description too.
- Evidence: `D/surveys/survey-B.md`, `E/task-7-report.md` Minor 5.
- Wave: 12c or a later 3.0.3 wave.

**Harness check (`7ed10f3e`):** (a) cc('RV1','Device:R_Trim','10k') = varistor both sides (the pot override at classify.py:251 tests 'r_pot'/'pot'/'potentiometer', and 'r_trim' has none). (b) Anteater BSPD VR1 (3296Y-11-103LF, fp Potentiometer_THT:..., desc '...TRIM POT'): varistor at f254cb2 -> other at 7ed10f3. **Correction:** The (b) parts are on `VR` references (Anteater VR1/VR2), not bare `V`; a bare V1 with a Potentiometer_ footprint or 'trim pot' description already reads resistor at the candidate.

### KH-1208: a part whose reference starts with an unmapped first letter (`MT.C1`, `BC1`, `bC*`), drawn on a `Device` R/C/L/D/Q symbol, is typed `other`

**Severity:** LOW
**Discovered:** 2026-11-17, product v3.0.3 Wave 12b handoff (`kh-filings-wave12b.md` A item 1 `unmapped-letter-symbol`); checked by the harness at `7ed10f3e`

- Symptom: a part whose reference starts with an unmapped first letter (`MT.C1`, `BC1`, `bC*`), drawn on a `Device` R/C/L/D/Q symbol, is typed `other`. The passives next to correctly typed regulators therefore vanish. Task 4 produced about 12 false DO-DET "missing capacitors / decoupling" and 1 false PU-001 this way: Antigo89 MT.U1, Charading Saturn60 BU1, FEASTorg / williamweatherholtz R-78 blocks.
- Reach: 3,242 parts / 380 units, adds-dominant.
- Evidence: `D/surveys/survey-B.md`, `E/task-4-report.md` Concerns 2.
- Wave: a later 3.0.3 wave with its own budget.

**Harness check (`7ed10f3e`):** kicad_core/classify.py:156-340 at 7ed10f3: classify_component('MT.C1'|'BC1'|'bC3','Device:C',...) = other on both sides; no full-prefix row, no Device-symbol fallback. Distinct from KH-1084 (Regulator_Switching on unmapped prefix, closed in 12b) and KH-1054/1033 (closed). Reach 3,242/380 not re-measured.

### KH-1194: `analysis_cache._gerber_inputs_changed` checks a relative Gerber hash key only from the cwd `analyze_gerbers` ran in

**Severity:** LOW
**File:** `skills/kicad/scripts/analysis_cache.py:584-605` (`_gerber_inputs_changed` opens each `source_hashes` key as written); `analyze_gerbers` records the hash keys as the paths were given
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** harness probe at `08879e2d`: with an absolute key a changed Gerber is detected from any cwd; with a relative key (`analyze_gerbers` run on `gerbers/` from the project folder) the same change is not detected from another cwd, so the KH-805 cache refresh keeps a stale `gerber.json`. Split from KH-805 on the product's ruling (a bug, not a 3.1 feature).
**Fix direction:** record absolute (or analysis-folder-relative) keys, or resolve them against the recorded working folder.

### KH-1192: `analysis_cache._gerber_inputs_changed` raises on a NUL or lone-surrogate path in `gerber.json` (catches OSError only)

**Severity:** LOW
**File:** `skills/kicad/scripts/analysis_cache.py:584-605` (`except OSError` at `:602-603`; callers `:734`, `:842`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** a `source_hashes` key `"a\x00b.gbr"` raises `ValueError: embedded null byte`; `"\ud800.gbr"` raises `UnicodeEncodeError` (hand-edited `gerber.json`).
**Fix direction:** treat any path error as "changed".

### KH-1191: `.kicad_dru` text variables whose value holds `${…}`, nested empty values and nested built-ins load where KiCad refuses

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_core/project.py:1093-1101` (`resolve()` returns `'\0'`, read as resolved, for built-in names and for any value containing `${` / `@{`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** kicad-cli 10.0.8 refuses, ours loads: `${${FOO}}` with `FOO=${BAR}`; `${${FOO}}` with `FOO=""`; `${${TITLE}}` with title "T" and with no title block; also a plain `${FOO}` with `FOO=${BAR}` (not in the handoff; the product's own `nested2.tsv` shows it). Control: `FOO=BAR`, `BAR=x` loads in both.
**Fix direction:** follow KiCad's single expansion pass. Related KH-924.

### KH-1190: `what_if --spice` silently produces no SPICE deltas when LTspice or Xyce is the selected backend

**Severity:** LOW
**File:** `skills/kicad/scripts/what_if.py:404-408` (checks only "no backend"), `:419-428` (`{}` for an empty report); `spice/scripts/simulate_subcircuits.py:127-133` (empty report + diagnostic, never read by what_if)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** code read: with `SPICE_SIMULATOR=ltspice` / `xyce`, or with only one of them installed, the run ends `spice_verified: false` and nothing on stderr.
**Fix direction:** surface the refusal diagnostic.

### KH-1189: lookup checks (AM / OV / TJ / FT / EX / PM) skip an extraction scored below 60, or not scored, without a diagnostic

**Severity:** LOW
**File:** `skills/datasheets/datasheet_types/trust_gating.py:124-128` (`facts_trusted`); silent `continue` at `skills/kicad/scripts/lookup_detectors.py:112`, `:213`, `:328`, `:419`, `:517`, `:626`; only staleness is recorded (`lookup_helpers.py:65-72`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** a low-score or unscored (`quality` None / non-finite) extraction is skipped with nothing in `diagnostics[]`; the stale skip names it once. (The handoff named only the below-60 case.)
**Fix direction:** record the skip once per MPN, as the stale case does. KH-554 residue.

### KH-1188: cross_verify decoupling measures every rail cap against an IC, so caps serving a connector or module show as far caps

**Severity:** LOW
**File:** `skills/kicad/scripts/cross_verify.py:464-465`, `:474-475` (loads are only `type == "ic"`), `:510-513` (centre-distance info branch)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** code read: a cap serving a connector or module is measured against the nearest IC and lands in the centre-distance info rows (product count 6,385 over 10,920 pairs, not re-measured), mixing real far caps with connector caps.
**Fix direction:** treat connector / module supply pins as rail consumers, or label the row.

### KH-1187: DS-003's datasheet walk counts PDFs in dot-folders, including a `.sync-*` stage left by a killed sync

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/audits.py:308-309` (`os.walk` prunes only `extracted`); stage made at `datasheets/distributor_core/sync.py:435`, removed in `finally` at `:441-442`
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** code read: a SIGKILLed sync leaves the stage, and its files feed the DS-003 summary "(N files)" (`:349`) and `datasheet_file_count` (`:357`); any other dot-folder is counted too.
**Fix direction:** prune dot-folders in the walk.

### KH-1186: lifecycle `--delay 1.0` (default) allows 60-120 Mouser calls a minute against the 30 / min quota; each alternative adds requests

**Severity:** LOW
**File:** `skills/kicad/scripts/lifecycle_audit.py:69` (`--delay` default 1.0); `lifecycle_engine.py:788` (one sleep per source), `:793` (PN call), `:797-798` (MPN fallback), `:302-305` (per alternative), `:851` (`find_alternatives`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** about 60 calls / min on a PN hit or a row without a PN, about 120 / min when the PN misses and the MPN fallback runs; a multi-alternative field repeats it per alternative. (The handoff's "≈ 120" is the PN-miss case.) KH-824 fixed only the sync provider's default.
**Fix direction:** a per-provider minimum interval (Mouser 2.0 s) shared by every call.

### KH-1185: `sync_datasheet_urls` / `edit_properties` match Value / Datasheet / Footprint / Description in exact case only; the BOM reads any case, so they miss fields and add duplicates

**Severity:** LOW
**File:** `skills/bom/scripts/sync_datasheet_urls.py:83`, `:101`, `:121-122`; `edit_properties.py:75`, `:94`, `:172`; the BOM reads through `kicad_core/fields.py:128-143` `symbol_field_map`
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** lowercase `value` / `datasheet`: `extract_symbols` gives `{'datasheet': '', 'keys': []}`, and `apply_updates({"R1": {"Datasheet": …}})` adds a second `Datasheet` property beside `datasheet`. (Reference is exact-case in the BOM too, so it is not a divergence; the handoff listed it.)
**Fix direction:** read and edit through `symbol_field_map`.

### KH-1184: `-o /dev/stdout` makes the analyzers take `/dev` as the analysis folder and try to write `capability_mode.json` there

**Severity:** LOW
**File:** `analyze_pcb.py:86-87` (`Path(args.output).parent`), same pattern `analyze_schematic.py:90`, `analyze_gerbers.py:2232`, `analyze_thermal.py:1040`, `cross_analysis.py:1420`, `emc/scripts/analyze_emc.py:470`
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** `analyze_pcb.py … -o /dev/stdout` prints "PermissionError: '/dev/.capmode-….tmp' — capability_mode.json not written", rc 0.
**Fix direction:** treat a non-regular output path as "no analysis folder". Related KH-793.

### KH-1183: non-finite PCB numeric fields write NaN / Infinity into the JSON; `1.2.3` (and a schematic `1e400`) still trace back

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/reader.py:849-851` (no finiteness guard on `float(width)` / point coordinates); `kicad_core/sexp.py:227`, `:256-262` (`_fix_point` skips tokens ending in a digit or `.`); `kicad_core/coords.py:14`
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** `(width nan)`: rc 0, `width_distribution {"NaN": 1}`, `min_track_width_mm: NaN`. PCB point `1e400`: rc 0, writes `Infinity` (`total_track_length_mm` …). `1.2.3`: ValueError traceback on the PCB (`reader.py:849`) and the schematic. Schematic `1e400`: OverflowError at `coords.py:14`. (The handoff said `1e400` traces back on the PCB; it writes Infinity there.)
**Fix direction:** the rest of KH-494 item 1: one finiteness check on every numeric field the readers keep.

### KH-1182: `diff_analysis --analysis-dir --type deep_review` looks for a per-run `deep_review.json` that the gate never writes, and exits 1

**Severity:** LOW
**File:** `skills/kicad/scripts/diff_analysis.py:502-505`; `analysis_cache.py:40-49` (`CANONICAL_OUTPUTS` has no `deep_review`, so the name falls back to `<type>.json`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** a manifest with 2 runs plus a root `deep_review.json`: exit 1, "Error reading base file …/2026-11-01_0900/deep_review.json: No such file". (The handoff said the tool reads the root file; it is the reverse: the gate writes only the root file, the tool reads only per-run files. Survey F has it right.)
**Fix direction:** either the gate writes into the run folder or the tool reads the root file with a run guard.

### KH-1181: `.kicad_dru` grammar check skipped for a condition or bound holding `${` / `@{`; `(min "")` says "Syntax error" where KiCad says "Missing min value."

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_core/project.py:1191-1193` (condition), `:872` (bounds), `:974-975` (`(min "")`)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** `A.NetClass == '${FOO}' &&` with `FOO=x`: KiCad refuses, ours loads (the same condition without a variable gives "Could not parse expression."), so the exemption can only under-refuse. `(min "")`: KiCad 10.0.7 `drc_rule_parser.cpp:728-732` reports "Missing min value." when the expression parses empty; ours "Syntax error".
**Fix direction:** check the grammar after variable expansion; match KiCad's message for an empty bound.

### KH-1180: `.kicad_dru` quoted `(layer "outer")` / `(layer "inner")` loads where kicad-cli 10.0.8 refuses it

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_core/project.py:1142-1147` (`_dru_layer_known` accepts `outer` / `inner` without knowing they were quoted)
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** quoted forms: KiCad refuses, ours loads; unquoted `(layer outer)` loads in both. Corpus reach 0 of 727 `.kicad_dru` files.
**Fix direction:** keep the quoted flag through to the layer check.

### KH-1179: `.kicad_dru` conditions naming an unknown property, function or item load where KiCad refuses the file

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_core/project.py:1002-1007` (`_dru_condition_error`: "Property and function names are not judged")
**Discovered:** 2026-11-16, product v3.0.3 Wave 12a handoff (product verified); re-verified by the harness at `08879e2d`
**Symptom:** `A.Bogus == 'x'`, `A.bogusFn('x')`, `Q.Type == 'track'`: kicad-cli 10.0.8 refuses the file, ours loads (`custom_rules_error` None).
**Fix direction:** needs KiCad's property / function registry (product R-B4). Related KH-924.

### KH-1123: VM-001 picks one supply on a multi-supply IC, so pins on a second rail read as level crossings

**Severity:** MEDIUM (false voltage-mismatch findings)
**File:** VM-001 (`skills/kicad/scripts/validation_detectors.py`, the per-IC supply choice), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** jabr-control-v2: U302 PCI11010 (VDDRGMII on +1V8) and U701 LAN8870 (VDDIO on +1V8) get 14 false 3.3 V / 1.8 V crossings once the bus-alias fix (KH-1129) lands.
**Fix direction:** judge each signal pin against the supply of its own I/O bank / VDDIO pin when the IC has more than one supply. Group with KH-667 / KH-876.
**Gate budget (when fixed):** VM-001 removals on multi-supply ICs.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, VM-001 multi-supply; RULINGS-12c §E called it a new 12d KH):**
12c exposes, declared known-false:
- greatscottgadgets/daisho VM-001 +36 (P-notation; main_board 14, `HDMI_OUT_*_SHIFTED` 8 + 8, de2-115 HDMI clocks 4, gige `VRAW_SW_5V` 2);
- spaced rail names +16 / −2 (PENDA Daisy Seed 9 V domain 7 on 1 unit, capstone-pcb, BlueJay wsg3.0, LED workshop SK9822);
- survey P puts the tail class at +4.
- **Pin direction:** GhanmiIyed/Beehive-Monitoring `CAN_interrupt` and `TDX_CAN_output`. The TJA1040 STB / TXD pins are inputs driven by the 3.3 V ESP32; VM-001 assumes the higher domain drives.
  Harness check (`ea5f7fd1`): Counts reproduced (corpus base -> tip VM-001): greatscottgadgets/daisho 0 -> 36 (e.g. hdmi_output HDMI_OUT_*_SHIFTED '5.0V / 3.3V domain crossing'); GhanmiIyed/Beehive-Monitoring Pins_config 0 -> 4: Mic_CLK 3.3/1.8, CAN_interrupt, RDX_CAN_input, TDX_CAN_output 5.0/3.3. The addendum names only CAN_interrupt and TDX_CAN_output; RDX_CAN_input (TJA1040 RXD, a 5 V output into the ESP32) is a true crossing. **Correction:** State that Beehive gets 4 VM-001 at tip (0 at base): CAN_interrupt and TDX_CAN_output are false (inputs driven by the 3.3 V ESP32), RDX_CAN_input is true, Mic_CLK unjudged. The pin-direction and P-notation / spaced-name exposures are not multi-supply-IC cases: they fit KH-667 (VM-001 domain heuristics) better than KH-1123; file the direction bullet on KH-667 if the harness keeps KH-1123 to multi-supply ICs.

### KH-1124: DP-001 gives an untyped differential pair the 50 ps default skew budget

**Severity:** MEDIUM (false errors once the #61 pair fix widens reach)
**File:** `skills/emc/scripts/emc_rules.py:2324` (default budget); `emc_formulas.py:739` (USB-FS = 10,000 ps), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (guarded A/B with the #61 fix)
**Symptom:** bare USB D+/D- DP-001 goes 4 → 40 after the #61 fix; generic pairs 30 → 439.
**Fix direction:** skip pairs typed only `differential` with no protocol and no budget (ruling R2 (a)); give USB D+/D- the USB-FS budget. With KH-487.
**Gate budget (when fixed):** DP-001 on the #61-widened pairs.

### KH-1125: `power_budget` ignores net ties (GitHub #50 gaps A + B)

**Severity:** LOW-MEDIUM
**File:** `skills/kicad/scripts/system_analyses.py:1462-1507`, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (issue #50)
**Symptom:** (A) a regulator is not attributed across a net tie: 20 regulators / 18 units / 11 repos; (B) an IC is counted on every tied rail: 30 units / 18 repos.
**Fix direction:** treat a net-tie group as one rail through the shared `conductor_of` predicate (ruling R3 (a)).
**Gate budget (when fixed):** `power_budget` values on ≤ 48 units.

### KH-1126: rail voltages are not shared across a net tie (GitHub #50 gap C)

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/pipeline.py:323-375` (`build_rail_map`), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (issue #50)
**Symptom:** 180 tie groups / 156 units / 74 repos, 376 nets miss the voltage of their tied rail; 13 groups conflict.
**Fix direction:** propagate a rail voltage across a tie group; report the 13 conflicting groups instead of picking one.
**Gate budget (when fixed):** `rail_voltages` gains on 376 nets / 156 units.

### KH-1127: 1,926 single-layer zones report `fill_ratio` > 1.0

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/` zone fill area (PCB `--full`), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (PCB `--full` outputs dated 2026-11-14)
**Symptom:** 1,926 single-layer zones with `fill_ratio` above 1.0 (silk / mask ~1,660, copper ~266). A different cause from KH-644 (multi-layer zones).
**Fix direction:** find why the filled area exceeds the outline area on one layer (overlapping fill polygons counted twice, or outline area of the wrong layer).
**Gate budget (when fixed):** `fill_ratio` values on those zones; GP-004 where it reads them.

### KH-1128: ES-002 reports errors on devices that have no ground pad at all

**Severity:** LOW-MEDIUM (22 false errors)
**File:** `skills/emc/scripts/emc_rules.py` (ES-002), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (EMC regen 2)
**Symptom:** 22 ES-002 errors on devices with no ground pad.
**Fix direction:** skip (or report as not applicable) a device with no ground pad instead of measuring a ground distance.
**Gate budget (when fixed):** 22 ES-002 removals.

### KH-1129: KiCad 10 project bus aliases (`.kicad_pro` `schematic.bus_aliases`) are not read

**Severity:** MEDIUM (split nets on projects that use them)
**File:** `skills/kicad/scripts/schematic/reader.py:1258-1267` (reads only the sheet `bus_alias`), at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey; verified there against kicad-src `6fbb4b0f5f` and kicad-cli 10.0.8
**Symptom:** jabr-control-v2: 80 split nets; a prototype matches kicad-cli 10.0.8 on 399/399 nets and findings go 350 → 239. 2 non-empty corpus `.kicad_pro` today.
**Fix direction:** read the project-level aliases and merge them with the sheet aliases (KiCad 10 moved them to the project file).
**Gate budget (when fixed):** nets and findings on the 2 projects.

**2026-11-17 addendum (Wave 12b Track H, survey-H; ruled RULINGS-12b section 4):** reach is 40 non-empty `schematic.bus_aliases` projects, not 2. Fixture: kicad_monkey `project_bus_alias_hierarchy`. Harness check: Scan of 14,962 corpus .kicad_pro: 40 projects / 24 repos with non-empty schematic.bus_aliases (KH-1129 says 2). Candidate reader still reads only sheet bus_alias (schematic/reader.py:1292-1306). kicad_monkey project_bus_alias_hierarchy fixture exists. The '22 heuristic' split not re-checked.

**2026-11-17 addendum (Wave 12b Track H `H10`, folded in by the harness, LOW):** undefined bus alias used as a `{X}` group label reads differently from KiCad. In the original 007785 the alias is defined (registers.kicad_sch:802 bus_alias HSIZE); the residue appears only once that definition is gone, which natively happens exactly when a KiCad 10 project keeps its aliases in .kicad_pro (KH-1129). Not isolated; reach unknown.

### KH-1130: KiCad 10 rounded-rect Edge.Cuts / `fp_rect` `(radius)` is read as a sharp rectangle

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/reader.py:1559-1567`, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** 8 KiCad 10 boards; PM-002 moves on 6.
**Fix direction:** represent it as 4 lines + 4 arcs (ruling R14 (b); `board_outline.edge_count` 14 → 84 on KTHFS; no new key; same representation as KH-666).
**Gate budget (when fixed):** outline edges / area on the 8 boards, PM-002 on 6.

### KH-1131: KiCad 10 schematic rule-area `dnp` / `in_bom` / `on_board` / `exclude_from_sim` flags are not applied

**Severity:** LOW (corpus 0)
**File:** schematic reader rule areas, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** kicad-cli 10.0.8 marks C703 / C704 / FL701 DNP on a scratch copy with a DNP rule area; we mark none. Corpus: 0 non-default flags.
**Fix direction:** apply the rule area's flags to the symbols inside it, as KiCad 10 does.
**Gate budget (when fixed):** none on the corpus.

### KH-1132: KiCad 10 backdrill / post-machining zone knockouts are not modelled

**Severity:** LOW (corpus 0)
**File:** PCB connectivity / zone model, at `6b9767e1`; KiCad `connectivity_algo.cpp:904-919`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** a backdrilled via / post-machined hole still connects the zone layers KiCad knocks out. Corpus 0.
**Fix direction:** model the knockout as KiCad does.
**Gate budget (when fixed):** none on the corpus.

### KH-1133: KiCad 11 footprint `(transform)` replaces `(at)`; every footprint is read at (0, 0, 0°)

**Severity:** HIGH (KiCad 11 boards; placement, every geometry check and run time)
**File:** `skills/kicad/scripts/pcb/reader.py:377`, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (387 / 387 misplaced on 10 nightly-upgraded corpus boards); harness Track H nightly lane the same day (`results/v303_refresh/REPORT.md` §3f)
**Symptom:** the nightly (10.99.0, format 20261025) writes `(transform (translate x y) (rotate a) (scale 1 1))` in place of the footprint `(at …)`. Harness lane over quick_200: 265,902 of 269,799 footprints (98.6 %) at the origin, 3,588 of 3,614 boards all at the origin; 8 boards time out at 120 s (0.8–22 s before); pcb time p90 8.1×. KiCad's own QA files at `6fbb4b0f5f`: all 632 footprints on the 49 boards that use `(transform` at the origin, with no diagnostic. Corpus `(transform` count today: 0 (`tools/corpus_marker_scan.py`).
**Fix direction:** read `translate` / `rotate` (and `scale`) from `(transform)` when `(at)` is absent.
**Gate budget (when fixed):** none on the corpus (no file uses it); the nightly lane and the KiCad QA files are the check.

**Addendum 2026-11-16 (corpus batch 2):** the gate budget above no longer holds. Corpus batches 1 + 2
(KiCad 11-dev repos) bring 135 boards / 21 repos / 12,099 footprints written with `(transform)`
(list `results/v303_b2_gate_aux/transform_boards.txt`), every footprint read at (0, 0). Run-time
consequence: with all courtyards stacked, `pcb/assembly.py::analyze_placement` refines every
pair (`geometry._refined_overlap_mm2` 208,335 calls → 240 M `_point_in_polys`, 125 s of a 150 s
profile on alxgmpr/sierra-to-usb `appliance.kicad_pcb`, 663 footprints). Plain pcb standalone:
appliance 97.2 / 99.0 s, hookprobe-sbc (945 footprints) 104.9 / 105.1 s at 365aea9 / f254cb23;
both time out at 120 s under the 32-job std gate on both sides (ledgered in 365aea9.json /
f254cb2.json). When fixed, the budget is placement / geometry on these 135 boards, and the two
timeout debts should resolve.

### KH-1134: KiCad 11 `gr_ellipse` / `fp_ellipse` (and `_arc`) are ignored

**Severity:** LOW (corpus / qa 0)
**File:** PCB reader graphics, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** an elliptical board outline gives no outline.
**Fix direction:** read the ellipse primitives (outline as segmented curve).
**Gate budget (when fixed):** none on the corpus.

### KH-1135: KiCad 11 pin-to-pad maps (`pin_maps` / `associated_footprints` / `pin_map_override`) are ignored

**Severity:** LOW-MEDIUM (wrong pad per pin where used; corpus 0)
**File:** schematic reader pin numbering, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey (nightly netlist puts D1 K on pad 2; we keep pin 1)
**Symptom:** under a pin map, our `pin_number` is the symbol pin, not the pad KiCad connects.
**Fix direction:** ruling R14 (a): `nets[].pins[].pin_number` = the effective pad, `pin_name` stays the symbol's; token-gated.
**Gate budget (when fixed):** none on the corpus (≤ 10 unchanged).

### KH-1136: KiCad 11 escaped stacked-pin notation is misread

**Severity:** LOW (corpus 0)
**File:** `skills/kicad/scripts/schematic/reader.py:57-79`, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** an escaped stacked-pin name splits (or does not split) differently from KiCad 11.
**Fix direction:** follow KiCad 11's unescape rule before splitting stacked pins.
**Gate budget (when fixed):** none on the corpus.

### KH-1137: KiCad 11 variant `symbol_override` (swaps the library symbol) is ignored under `--variant`

**Severity:** LOW (corpus 0)
**File:** schematic variant handling, at `6b9767e1`
**Discovered:** 2026-11-15, product v3.0.3 triage survey
**Symptom:** `--variant` keeps the base symbol where the variant swaps it.
**Fix direction:** apply `symbol_override` when the variant is selected.
**Gate budget (when fixed):** none on the corpus.

### KH-1114: `silkscreen_completeness` status `warning` never becomes a finding, and the fab gate does not read it

**Severity:** LOW (v3.0.3)
**File:** `skills/kicad/scripts/pcb/reader.py:2000-2017` (`ref_designators_visible` = visible / total >= 0.9; a failed check only sets `silkscreen_completeness.status = "warning"`); `skills/kicad/scripts/fab_release_gate.py:164-188` (`check_documentation` reads only `documentation_warnings` `missing_revision` / `missing_board_name`), at `365aea94`
**Discovered:** 2026-11-15, SacMap rev2 soak runs 12 (Claude Opus 5.5) + 13 (Codex) at the v3.0.2 release (`2c645996`, analyzer code = `365aea94`; product report), verified by code read at `365aea94`
**Symptom:** SacMap: 10 hidden reference designators, `silkscreen_completeness.status` warning, no finding emitted, fab gate PASS. Connector-label and polarity-marker misses are rollup-only the same way.
**Fix direction:** emit an info / warning finding per missing silkscreen check (or a fab-gate `warn` row) from `silkscreen_completeness.missing`.
**Gate budget (when fixed):** new PCB findings on every board under the 90 % visible-refdes threshold (a large corpus count: measure first).

### KH-1120: PM-002 emits a finding for an edge-mount part the rule itself calls by-design

**Severity:** LOW (v3.0.3; finding noise)
**File:** `skills/kicad/scripts/pcb/assembly.py:472-474` (`elif is_edge_mount: severity = 'info'`, suffix "edge-mount footprint — by-design at board edge"; the RF-module branch at `:468` is the same), `:510-527` (the part is still added to `edge_close` and emitted), at `365aea94`
**Discovered:** 2026-11-15, SacMap rev2 soak runs 12 (Claude Opus 5.5) + 13 (Codex) at the v3.0.2 release (`2c645996`, analyzer code = `365aea94`; product report), verified by code read at `365aea94`
**Symptom:** the soak's PM-002 reads as a by-design info finding on a part inside the outline; it pads the finding counts with something the rule already knows is intended.
**Caveat:** if the soak's part is not in the edge-mount keyword list, this is KH-753 instead.
**Fix direction:** for an edge-mount / RF part at clearance >= 0, record a placement observation (or count) instead of a finding; keep a finding for an overhang or an antenna-clearance problem.
**Gate budget (when fixed):** PM-002 info findings removed on edge-mount / RF parts inside the outline (measure).

### KH-1121: DC-002 passes an IC when any of its pins has a cap, so a supply pin that is not recognised as one (U4 `VBUS`, typed `passive`) loses its check

**Severity:** LOW-MEDIUM (v3.0.3; missed decoupling; mechanism inferred from code)
**File:** `skills/emc/scripts/emc_rules.py:774` (`ics_with_caps = {e.get('ic', '') for e in decoupling}`, per IC) and `:797`; `skills/kicad/scripts/pcb/assembly.py:85-92` (`_ic_signal_nets`: a pad is a rail only by power-like net name, `power_in` / `power_out` type or `_SUPPLY_PIN_NAME` `:15-16`, which has no `VBUS`), at `365aea94`
**Discovered:** 2026-11-15, SacMap rev2 soak runs 12 (Claude Opus 5.5) + 13 (Codex) at the v3.0.2 release (`2c645996`, analyzer code = `365aea94`; product report), verified by code read at `365aea94`
**Symptom:** SacMap U4: DC-002 does not flag its passive-typed VBUS supply pin. Reading the code, the check is satisfied for the whole part by a cap on any other pin, and a `passive` VBUS pin is neither rail nor signal. Not reproduced (design not accessible).
**Fix direction:** check coverage per supply pin and recognise a `passive` pin as a supply by full name (the schematic's `_SUPPLY_PIN_FULL_NAME`, `schematic/net_analysis.py:302`, already matches VBUS; sharing it would also help KH-926).
**Gate budget (when fixed):** DC-002 additions on ICs with an uncovered supply pin (measure).

### KH-1108: RC junction-load rule trusts library pin types; RC direction wrong when the resistor's far end is the source

**Severity:** LOW (v3.0.3)
**File:** `skills/kicad/scripts/signal_detectors.py:527-542` (`_feeds_inputs_only`: an IC pin counts as a filtered input when its library `pin_type` reads `input`), `:719-727` (`detect_rc_filters` direction: `in_net, out_net` assigned from the R and C far ends without asking which end is driven), at 365aea94
**Discovered:** 2026-11-13, product v3.0.2 Wave 11e handoff (peer review of the junction-load rule, item 4), re-read by the harness at `365aea94`
**Symptom:** (1) Wave 11e frees a divider top resistor for RC pairing when its far net holds only caps and IC pins typed `input`. A reference or output pin that a library types `input` (VREF, TS, RFout) passes the same test, so the feeding resistor of a reference or output node is freed and paired as an input filter. (2) Pre-existing, for every non-divider resistor: when the resistor's far end is the source, the filter is reported backwards. Example: Quansheng UV-K5 R20, reported as a low-pass with input `__unnamed_130` and output `LM2904A_OUT` (the op-amp output). The handoff named R77, but R77 pairs no RC filter at 206403e, at the A / A+C steps or at 365aea94.
**Measured at the Wave 11e gate (2026-11-13):** 132 B additions on 65 units in the std gate: 125 real, 7 false. The 7 false ones land on a pin the library types `input` that is not a filtered input. These are BQ24650 VREF (R9 / C16, Dodokamel2005/EPS-, "low-pass -> VREF" at 30 Hz: C16 is the reference's bypass cap) and MAAM-011100 RFout x1 / RFin x5 (loxodes/vna, R + C "RC-network" at 15.9 MHz on an RF amplifier's ports: bias / match parts). The other 125 read as real filters (76 on op-amp + inputs, ADC AIN, enable / reset / standby delays, INA219 IN-). Record: `results/v302_w11e_gate_aux/b_adds_review.json`.
**Fix direction:** (1) require the pin's name or role to read as a signal input (not REF / TS / OUT / RF*), or check that no other pin on the node drives it; (2) orient the filter from the driving side (an IC output / power pin on one end) before naming input and output.
**Gate budget (when fixed):** RC-DET removals on junction-load pairs whose far pin is a reference or output (expected few); RC-DET input_net / output_net swaps on the source-at-far-end class (measure).

### KH-1106: a merge conflict whose two sides are whole lists parses cleanly with no `diagnostics` record
**Severity:** LOW (v3.0.3)
**File:** `skills/kicad/scripts/kicad_core/sexp.py:104` (`parse_checked` reports only an open list or over-deep nesting), `kicad_core/project.py` (`parse_input_problem`), at 206403e8
**Discovered:** 2026-11-13, product CHANGELOG accuracy pass for v3.0.2 Wave 11d (handoff), re-read by the harness at `206403e8`
**Symptom:** probe: a `.kicad_sch` with `<<<<<<< HEAD` / `=======` / `>>>>>>> branch` around two complete `(wire ...)` lists runs to rc 0 with `diagnostics: []`; the markers become bare atoms and both sides are read. An unbalanced conflict is caught (open list); a balanced one is not.
**Fix direction:** flag a line-leading `<<<<<<<` / `=======` / `>>>>>>>` atom run as a merge-conflict problem in `parse_checked` (or `parse_input_problem`) and emit the `diagnostics` record.
**Gate budget (when fixed):** `diagnostics` additions on files with conflict markers (expected ~0 on the corpus; measure).
**Addendum 2026-11-15 (v3.0.3 Track H, corpus census `tools/corpus_marker_scan.py`, outputs at v3.0.2 = `365aea94` analyzer):** corpus fixture: `clovisf/Keychain-thermometer/keychain-thermometer.kicad_pcb:4380` (one balanced `<<<<<<<` / `=======` / `>>>>>>>` block, lines 4380 / 4383 / 4419); v3.0.2 exits 0 with only `BT1: courtyard outline is not closed` in `diagnostics`, while kicad-cli 10.0.8 and the nightly both exit 3. Census of 92,752 corpus KiCad files (`.kicad_sch`, `.kicad_pcb`, EESchema `.sch` / `.lib`, `.kicad_sym`): 1,492 line-leading markers in 23 files (`results/v303_refresh/conflict-markers.tsv`), 20 of them analyzer inputs (12 schematic incl. 1 legacy `.sch`, 8 boards) and 3 libraries. What v3.0.2 says today on the 20: 5 whole-file conflicts get "is not a KiCad schematic/board: it starts with '<<<<<<<'"; 9 unbalanced ones get the generic "the file ends inside an open list"; 6 balanced ones get no conflict diagnostic (Keychain-thermometer, both `Pistol_Camera_Driver(crushed).kicad_sch`, `AoToS/Adacus` ADACUS.kicad_pcb, `DBXYD/2526_Projet1AB_Khess` PCB_Module_Payement.kicad_pcb, legacy `matt-chv/electronics-design-patterns` marx generator.sch — the legacy line reader needs the same check). Budget (when fixed): new `diagnostics` records on those 6 units, message changes on up to 14 more, and their downstream emc / thermal units; not ~0.

### KH-1102: KO-001 never checks a rule area's `pads` or `tracks` restriction
**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/assembly.py:1287`, `:1311` (only `footprints` and `vias` are tested; `_prohibits` at `:1210`)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey K §1 "out of scope, noted")
**Symptom:** kicad-cli reports 725 track and 87 pad items on the KO A/B boards that KO-001 does not report. A pad is judged by its own shape in KiCad, not by its footprint's courtyard.
**Fix direction:** add pad-shape and track-segment tests against the area outline for areas that prohibit them; measure against kicad-cli on the same boards.
**Gate budget (when fixed):** KO-001 additions (new reach), pcb lanes.

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

**Severity:** LOW (cosmetic)
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

**2026-11-17 addendum (Wave 12b, `7fdfe2c4`): partly fixed, stays open.** classify.py:388-390 types a 'regulator_*' library nickname as 'ic' before the 'switch' substring test. Corpus: of the 25 Regulator_Switching parts typed switch at baseline (22 units, the KH's exact count), 24 become ic. POW1_85B1 LM27313 and dridri DC1 LM22676 gain a PR-DET 'switching' record. Horticulture-LED VR1 TPS560430 (lib 'Horticulture-rescue:TPS560430X3FDBV-Regulator_Switching') is still 'switch' with no PR-DET on both sides. Still open: One of the block's named examples (Horticulture-LED VR1) is not fixed. The test reads only the library nickname, so a KiCad 5 rescue name whose suffix carries Regulator_Switching still matches 'switch'. The suggested 'VR' regulator prefix was not added: VR1 on a custom TPS560430 symbol is now 'other' (was varistor). (harness agents at `7ed10f3e` vs `f254cb23`.)

### KH-1083: regulator current is estimated from output capacitance (10 mA per µF, cap 1 A / 2 A), so bulk caps make a 7 W LDO and a TS-001 Tj 445 °C error

**Severity:** MEDIUM (error-severity thermal false positive; the schematic output contradicts its own power_budget)
**File:** `skills/kicad/scripts/signal_detectors.py:2445-2448` (LDO: `min(total_cout * 1e4, 1.0)`), `:2466-2468` (switching: cap 2.0 A); consumer `skills/kicad/scripts/analyze_thermal.py:239-260` (LDO `estimated_pdiss_W` taken as is)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey G ask 3; exposed by KH-925's `DVSS` ground)

**Symptom:** HelveticaScenario/eurorack-kicad teensy_dc_interface U10 NCP1117-5.0 (+12 V → AVDD): once `DVSS` reads as ground, C52-C55 (4 × 47 µF) count as output capacitors. `estimated_iout_A` goes 0.1 → 1.0 and `estimated_pdiss_W` 0.7 → 7.0. Thermal then reports TS-001 error "estimated Tj 445°C exceeds abs max 125°C", plus TS-004 7.00 W and TP-001 ×2. The same output's `power_budget.rails.AVDD` gives 10 mA and 70 mW for U10.
**Fix direction:** estimate a regulator's load from the rail's `power_budget` load (as thermal already does for switchers), not from its capacitance. When there is no load estimate, give no dissipation (thermal `skipped: no_load_estimate`) rather than an error-grade Tj. If a proxy stays, it should only be able to raise an info.
**Gate budget (when fixed):** `power_dissipation.estimated_iout_A` / `estimated_pdiss_W` on every regulator with output caps; thermal TS-001..005 / TP-001 / TH-DET moves; power_tree / inrush where they read it.

**2026-11-17 addendum (Wave 12b handoff, `kh-filings-wave12b.md` section C):** (regulator current from output capacitance). This is the survey A `ldo-iout-cap-proxy` slug. 12b drags: dtnking MIC5219 Tj 68 → 110 °C (TS-002 + TP-001 ×10, Task 2); roybaer sduino_mb / sduino_uno NCP1117 0.80 W (TS-004, TS-005, TP-001 ×2 each, Task 6); Task 19's TS-001 ×3 / TS-004 ×7 on now-known Vouts.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, load model):**
Thermal is fixed (thermal reads the budget; the proxy is capped at info), so KH-1083 stays open for the other consumers:
- **TW-001 prefers the cap guess.** When a regulator's Iout is the output-cap proxy, TW-001 takes it over the rail's power-budget load (`cross_analysis` `check_trace_width_power`, pre-existing precedence). AL-255/Flora2 `+3.3V` shows it: a true TW-001 (0.13 mm for ~0.7 A), added by the budget fallback (`90a75cac`), is removed again once the LD1117S33 decodes and carries a 15 mA proxy (`4aad4d9d`). Against `ca59d562` the net change is 0 (a transient), but the warning stays hidden.
- The max-of-both fix was measured and held. Of 5,835 PCB units, 399 could move (100-unit control 0). TW-001 +13 / −8 in 13 units: 5 new warnings, 8 changed. Of the 13 hand-checked, 2 were wrong and 1 doubtful: OpenEFI 13 sensor connectors at 80 mA, Duet2 74HC logic at 250 mA, doorbell 74LVC2G14 / DS3231M at 200 mA. All are the budget's per-IC defaults (`budget-per-ic-default-current`).
- Patch: `D/patches/tw001-budget-fix.patch`. It waits for the per-IC default currents.
- **EMC PD-001 reads the proxy with no info cap.** jasonsbeer/Amiga-2000-EATX `2000ATX` `-5V`: PD-001 error, transient 0.952 A, `transient_source: output_cap_proxy` (2 × 0.476 A).
- **Thermal at info.** On a 0 mA budget rail the proxy remains as an info fallback. anchorz Olivetti M20 VR2 79L05 ×2 (Tj 683 °C, TS-001 ×2, TS-004 ×2) and the same Amiga U9000 MC7905 (TS-002, TS-004 ×2), each with an info TH-DET. 411 census units have no `power_budget` block and always take the proxy (dtnking MIC5219 10 TP-001, info).
- **Budget notes from Task 30:**
- a shared output rail charges each regulator the full load (30 rails);
- a dual-rail IC is charged in full on each rail (dutlink, Twisted-Fields);
- `ic_with_internal_regulator` also holds MCUs, chargers and eFuses, so costing it as a downstream LDO is latent beyond LT304x / LT3094 / MPM3840.
- The PR-DET `power_dissipation.estimated_iout_A` field itself still comes from the capacitance.
- Evidence: ledger Tasks 30, 39, 40; `D/reviews/task-39-review.md` I-1; `D/reviews/task-40-review.md` I1.
  Harness check (`ea5f7fd1`): cross_analysis.py:991-1008 check_trace_width_power: a regulator's _reg_iout (cap proxy) sets net_current first; the power-budget load is used only for regulators in `unestimated` (iout <= 0), so the proxy wins whenever present. emc_rules.py:3781-3787 PD-001: i_transient = min(estimated_iout_A * 2, 5.0), transient_source 'output_cap_proxy', no severity cap. signal_detectors.py:2683/2739 still tag power_dissipation source 'output_cap_proxy'. No contradiction with KH-1083's text (it asks for budget-first + info-only proxy). Amiga / OpenEFI / Duet2 numbers not re-measured.

**2026-11-19 addendum (Wave 12c, stays open):** Thermal fixed in Wave 12c (`125b0a02`, `c336e6a5`); open for TW-001 and EMC PD-001 (section C above).
  Harness check (`ea5f7fd1`): Thermal fixed. Filed HelveticaScenario teensy_dc_interface U10: base TS-001 error 445 C + TS-004 7.00 W + TP-001 x2 -> cand none, budget AVDD 10 mA. Remainder confirmed: schematic PR-DET U10 still {estimated_iout_A 1.0, estimated_pdiss_W 7.0, source output_cap_proxy} on both sides (signal_detectors.py:2675 / :2695 caps 1 A / 2 A). cross_analysis _reg_iout :117 prefers it, and the budget is used only for regulators with no estimate (:1001-1008). EMC emc_rules.py:3781-3784 makes i_transient = 2 x proxy ('output_cap_proxy'), and PD-001 emits HIGH (= error) at :3838. Harness asks section 8 re-run with each clone's analyze_thermal on the gate's own schematic + pcb snaps: mickdassive reflow U5 TS-001 error 137 C + TS-004 2.79 W + TP-001 x2 -> none; U4 TS-001 error 242 C / 5.43 W -> TS-002 error 116 C / 2.26 W, TS-004 warning, TP-001 x3 info; dtnking MIC5219 U1 TS-002 error -> info, 10 TP-001 info; roybaer sduino_mb + sduino_uno U2 TS-004 warning -> info, TS-005 + TP-001 x2 info; TS-001 error -> info on Anteater FOCB U11 / PCC U8 / ROC U2, jasonalexander PicoChainReference U3, forGGe demo U1; their TS-004 now info. All 5 rows match section 8. **Correction to the product's remainder:** Remainder text is right. Optional precision: the PR-DET record keeps estimated_pdiss_W as well as estimated_iout_A (teensy U10 1.0 A / 7.0 W at ea5f7fd). Note for the gate: Anteater 26-27 PCC U8 TS-001 is info at ea5f7fd but its proxy reading went 0.70 W / 130 C -> 3.99 W / 624 C (the info still says it exceeds abs max).

**2026-11-19 addendum (Wave 12c gate, harness check):** Anteater PCC U8 TS-001 is now info, but its estimate rose from 0.70 W / 130 °C to 3.99 W / 624 °C and the info text still says it exceeds abs max. The PR-DET record also keeps the capacitance-proxy `estimated_pdiss_W` beside `estimated_iout_A`.

### KH-1082: VM-001 reads an analog switch's channel pins (COM / NO / NC / X / D) as logic I/O at the switch supply

**Severity:** MEDIUM (error-severity false positive; 69 errors / 24 units / 13 repos at db551674)
**File:** `skills/kicad/scripts/validation_detectors.py:497-506` (`_ic_rail_voltage`), `:680-741` (`validate_voltage_levels`: every IC endpoint is a logic endpoint)
**Discovered:** 2026-11-13, harness, verifying the Wave 11c handoff at db551674 (survey G ask 3; exposed further by ruling P-G1)

**Symptom:** bec5-group/pid-controller: 14 errors "15.0V / 5.0V domain crossing" between LM7171 / LMH6505 pins (±5 V) and DG467 / DG468 / DG469 `COM` / `NO` (±15 V). 11 predate Wave 11c. 3 `COM` nets are new, because P-G1 made `COM` a signal. Corpus (candidate snaps): 69 such errors with a CD4051B / TMUX4051 / DG2xx / DG46x / ADG / CD74HC4067 / TS5A channel pin on 24 units (PolySynth 24, pid-controller 14, Esp32_patch_bay 11).
**Fix direction:** an analog switch / multiplexer passes its channel pins' signal and drives no logic level. Skip its channel pins in VM-001. Recognise the part by function (lib / value family, plus control-pin evidence: IN / EN / S0-S2 beside COM / NO / NC / X / Y / Z). Pin types will not do it: legacy libraries type every pin `input`. Control pins keep the KH-667 logic-supply rule.
**Gate budget (when fixed):** VM-001 error removals on the 24 units (69 findings) plus any unnamed-pin cases the function test reaches.

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

### KH-1070: `kicad_version` is `unknown` for every file without a `generator_version` token (KiCad 6 / 7 files and KiCad 5 boards), about a third of schematic and two thirds of PCB outputs

**Severity:** LOW (metadata; any consumer that keys on `kicad_version` loses the version for those files, while legacy `.sch` reports `5 (legacy)`)
**File:** `skills/kicad/scripts/pcb/pipeline.py:332` and `schematic/hierarchy.py:230` (`get_value(root, "generator_version") or "unknown"`), surfaced as `kicad_version` in `pcb/presentation.py:268` / `schematic/presentation.py:280`
**Discovered:** 2026-11-11, harness, TH-109 triage (FND-00001904-AST-05, FND-00002289-AST-03); corpus census of today's outputs

**Symptom:** only KiCad 8+ writes `(generator_version ...)`. Corpus: schematic 11,146 / 36,463 outputs `unknown` (file_version 20230121 5,807, 20211123 4,511, ...); pcb 12,114 / 18,684 (20171130 4,127, 20221018 2,730, 20211014 2,521, legacy `4` 1,950, `3` 252, ...). The file's `version` token is in the output as `file_version` and identifies the KiCad major version.

**Fix direction:** when `generator_version` is absent, derive `kicad_version` from `file_version` (the KiCad format-date table: 2017xxxx → 5, 2020-2021 → 6, 2022-2023 → 7, ...; pcb `3` / `4` → legacy), or rename the field to what it holds. Output-changing on ~23 k units; budget class at the gate.

### KH-1068: EMC reads DNP only from the PCB footprint, so a connector marked DNP only in the schematic is still listed by IO-001 and the test plan

**Severity:** LOW (KiCad 6/7 boards whose DNP lives only on the schematic symbol; reach not measured)
**File:** `skills/kicad/scripts/pcb/reader.py:414` (`is_dnp` from the footprint `(attr ... dnp)` flag only); `skills/emc/scripts/emc_rules.py:312-317` `_connector_refs` (skips `fp['dnp']`; the schematic's `dnp` is not consulted), feeding IO-001, IO-002, ES-001 / ES-002, CK-003 and `test_plan.interface_risks`
**Discovered:** 2026-11-08, harness, verifying the KH-755 closure at `6138b126` (code read)

**Symptom:** KH-755 made EMC skip DNP connectors, using the PCB footprint flag. KiCad 7 added the footprint DNP attribute; on older boards, and wherever the user marks DNP on the schematic symbol only, the footprint carries no flag, so the connector still counts as a fitted external connector. The opposite case also exists in the gate: DavidRajchman SmartMPPTSolarCharger BCHW has connectors DNP on the board but not in the schematic, and those are skipped correctly.

**Fix direction:** when a schematic is given, treat a connector as DNP if either side says so (the schematic `dnp` by reference). Budget IO-001 / IO-002 / test-plan removals on those boards.

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

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
easy-smart `poe.kicad_sch` (duplicate C1 / C133 in the sheet read alone): the decoupling bench reports "device already exists", on both sides of Task 18's A/B. Only the message text moved with the record.
  Harness check (`ea5f7fd1`): Tip easy-smart/stm32f4_uno_poe poe.kicad_sch: C1 x4, C133 x10, C125 x2, C? x12 references; DC-DET VDD_PRI+ capacitors ['C1','C1'], so the bench emits R_esr_C1 twice. SPICE output not checked (not in the corpus dirs). Same mechanism as KH-1051's symptom (99 decoupling benches with a repeated reference); this is an instance, no new mechanism.

### KH-1050: CP-002 reports "no opposite-layer copper" on mousebite / panel footprints that carry only holes

**Severity:** LOW (info noise on panels)
**File:** `skills/kicad/scripts/pcb/copper.py:1051` `analyze_copper_presence` (every footprint with pads is classified, `:1082-1133`; no test for `board_only` / `virtual`, NPTH-only pads or net-less footprints), CP-002 `:1222-1229` (only the passive-ref regex is excluded)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-cp002-virtual-footprints`; ruling D1 concern 2)

**Symptom:** D1 (mixed-token footprints read) adds 68 CP-002 on KiKit mousebites on 2 panels. The class is older and wider. The 11b-1 std PCB snaps already have 318 CP-002 on mousebite footprints on 42 units (fc 86 / 6), from Keebio-Parts `breakaway-mousebites` 70, a `10-My-Footprints:mousebite` 56, `Panelization:MouseBite3-2mm` 48, `local-libraries:mousebite` 28 and others. Of the 318, 268 are typed `through_hole` with no `board_only` / `exclude_from_pos` flag, and none has a pad net. The attribute test alone would miss them.

**Fix direction:** skip footprints with no copper pad (NPTH only) or no pad net, plus `board_only` / virtual ones. Budget CP-002 removals.

**2026-11-17 addendum (Wave 12b Track H, survey-H; ruled RULINGS-12b section 4):** apply the predicate to PM-002 (otherwise the H2 fix adds 204 + 19 false PM-002). Harness check: KH-1050 (open) asks to skip NPTH-only / net-less / board_only footprints in CP-002; PM-002 (pcb/assembly.py:445-447) skips only reference-less footprints, so the same predicate applies.

### KH-1048: VS-002 replaces its 100 MHz default with any known frequency, however low, so a 500 kHz default or a 32.768 kHz crystal sets a stitching spacing of metres

**Severity:** LOW (recommendation text and the sparse-grid finding on `--full` boards)
**File:** `skills/kicad/scripts/cross_analysis.py:215-230` `_get_highest_frequency` (max over crystal `frequency` and PR-DET `switching_frequency_hz`, including `topology_default` 500 kHz), `:1123` `check_via_stitching_density`, `:1141-1145` (100 MHz only when nothing is known)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-vs002-low-frequency-spacing`; ruling G1 concern 1)

**Symptom:** the slug says "lowest known frequency". The code takes the highest known one, but any known value wins over the 100 MHz default even when it is far below it. λ/20 then grows with it: 500 kHz gives 14,639 mm, a 32.768 kHz crystal 223,366 mm. 11b-1 full-chain cross snaps: 682 VS-002, 44 with a recommended spacing > 73 mm (λ/20 at 100 MHz), 22 > 1 m, most on "No ground stitching vias found". Examples: farmerbriantee Ace ×3, kaminaris GigaESC at 14,639 mm, the hackpad Wio LR1121 module at 223,366 mm. IMU_V100 moves 73 → 14,639 mm at this gate when its MIC23050 becomes a PR-DET (see KH-1049). EMC VS-001 does the opposite: it starts at 50 MHz and only raises it (`emc_rules.py:1505-1514`).

**Fix direction:** take `max(default, known)`, as VS-001 does, and ignore `topology_default` frequencies. Budget VS-002 recommendation text and sparse-grid findings on full-chain units.

**2026-11-17 addendum (Wave 12b filing `vs002-lost-large-stitching-grid`, folded in by the harness):** Symptom: VS-002 ("via stitching sparse") disappears when the switching frequency found for a board makes the lambda/20 stitching grid larger than the board. Task 14 now finds the 260-500 kHz switch frequency of regulators, which becomes `_get_highest_frequency` (`cross_analysis.py`). Lost: horychen inverter x4, robotbits featheresc, BeanBike (7 records). Reach: 7 records (pre-existing logic exposed by a right change). Fix direction: bound the highest frequency used for the grid by the board's fast edges / clocks, not a regulator switch frequency, or cap the grid at the board size and still report. Evidence: `D/reconcile-wave12b.md` section 5. Wave: 12g. Harness check (`7ed10f3e`): cross_analysis.py:205-220 + :1136-1140: any known crystal or PR-DET switching frequency replaces the 100 MHz default, so lambda/20 grows past the board. KH-1048 is exactly this defect (open, not in the close list). Not new: 12b's frequency reads (Task 14/22) widen KH-1048's reach by these 7 records.

### KH-1047: a regulator enable without a datasheet threshold is accepted for any driving voltage, so a 1.8 V output into an EN with VIH ≈ 2 V is not reported

**Severity:** LOW (missed weak-drive case; needs datasheet data to judge)
**File:** `skills/kicad/scripts/validation_detectors.py:547-565` `_en_endpoint_compatible` (datasheet path `:556-563`; otherwise an EN-named pin on a regulator-like part is compatible whatever `v_min` is, `:564-566`)
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-en-vih-low-drive`; survey G2 item 5)
**Target:** 3.1 (datasheet-backed)

**Symptom:** after G2, VM-001 correctly drops "overdrive" on load-switch enables. On 4 of the removed nets, though, the driver is a 1.8 V output (TUSB1210 / USB3320 CPEN) into an enable whose VIH is about 2 V (TPS2051B, MIC2025). With no extraction the code returns compatible from the pin name alone, so the under-drive goes unseen.

**Fix direction:** when the lowest domain on the net is below a conservative EN VIH (or below the extracted `en_v_ih_max`), emit an info / warning for under-drive instead of accepting by name. Datasheet-backed in 3.1.

### KH-1045: VM-001's regulator-likeness is a part-number prefix list that misses most regulators PR-DET finds, so their enables are checked as logic inputs

**Severity:** LOW (false VM-001 / `needs_level_shifter` on EN pins of unlisted regulator families; it also blocks KH-1036)
**File:** `skills/kicad/scripts/validation_detectors.py:531-544` `_is_regulator_like` (prefixes `TPS6`, `TPS5`, `LM25`, … `REG`, or `type == 'power_regulator'`); used by `_en_endpoint_compatible` `:547-565` and the cross-domain pass `schematic/net_analysis.py:578`
**Discovered:** 2026-11-08, harness, v3.0.2 Wave 11b-2 gate (from the product handoff slug `KH-new-reglike-from-prdet`; survey G3 item 5, ruling P3)
**Target:** v3.0.3 (with KH-1036)

**Symptom:** census of the gate candidate schematic snaps: 9,431 of 13,578 PR-DET records (6,047 units) are not regulator-like by this test. The largest groups are LM1117, L7805, XC6206, MCP170x, TLV625, LD1117, AZ1117, AP6320, MCP182x, MIC550x and LP2985. Survey G found 239 VM-001 endpoints on an EN pin of a non-regulator-like part. In dpmj lora-payload, the LP5912 EN behind a TPS62912 PG is judged against a 1.8 V domain. That is the existing "Net PG_3V6RF: 3.6V / 1.8V" error, and it is why the KH-1036 fix alone adds 3 false `needs_level_shifter`.

**Fix direction:** treat a part with a PR-DET record as regulator-like (pass the detector result into the context). Budget VM-001 removals and `needs_level_shifter` flips. Land it with KH-1036.

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

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present: U3 TPS61023 reads `tj_max` `default_125` with a cached extraction (`_get_datasheet_thermal`, `analyze_thermal.py:173-205`, `find_extraction(..., v14_first=False)` reads only the v1.3 `junction_temp_max_c`). Package / RθJA half: KH-430.

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

**2026-11-17 addendum (Wave 12b, `b66c8bae`): partly fixed, stays open.** classify.py:114 _v_letter_part (b66c8bae). Probe base→cand: VD100 D_Bridge, VD1 D, VD2 Zener, VD4 D_Schottky → diode; VT1 Q_NPN_BEC, gost VT_NPN_EBC, VT Q_NPN, V BSP89, V Q_NMOS → transistor; VD/V 74LS → ic; V Device:LED → led; varistor symbols/07D471K/RV stay varistor. Units: bobbycar-graz hh_bridge V3/V4 BSP89 varistor→transistor; stereopi StereoPi_Power.sch 3 varistor → 1 diode + 2 transistor. Still open: the 2026-11-13 VR addendum. Couby/OpenBCI_hardware_KiCAD OpenBCI.sch VR1 TPS72325 goes varistor → other and still has no PR-DET record (PR-DET is U3/U4 only on both sides). Still open: The VR-regulator addendum is not fixed. Ruling B-P2 (task-7-report:79) types a VR with no regulator word as 'other', so TPS72325/HT7533/ME6211/NCP1117 on a VR ref are still not regulators. Close the V[DTSU]/plain-V part and keep the VR addendum open (or file it new). (harness agents at `7ed10f3e` vs `f254cb23`.)

### KH-1031: a legacy symbol whose library is missing falls back to the built-in `D` (pin 1 = K), reversing a project diode whose pin 1 is the anode

**Severity:** LOW (diode A/K names swapped on legacy boards with a missing rescue / cache library; consumers that read pin names get the orientation backwards)
**File:** `skills/kicad/scripts/schematic/legacy_reader.py:117-124` (built-in `D` / `D_Schottky`: 1 = K, 2 = A), `:584-600` (built-ins added for any missing name); `skills/kicad/scripts/schematic/pipeline.py:1016-1038` (`nick:D` → bare `D` → built-in, `_pin_source: builtin`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey B1 (harness ask 5); verified by the harness at `f53d107e` (code read)

**Symptom:** crazyflie rescue-backup D1: the rescue cache library is not found, so `…-rescue:D` takes the built-in pin map and reads A on +BATT; the project's KiCad 5 `.net` and main `.sch` give pin 1 (A) on the drain, pin 2 (K) on +BATT. TR-DET now ignores built-in pin names for flyback orientation (Wave 11b-1), so that detector is unchanged; other pin-name readers are not guarded. Visible only as `legacy_analysis_quality` `builtin_fallback` counts.

**Fix direction:** for polarized built-in fallbacks, do not assert A/K names (leave the pins unnamed), or take the orientation from the project's `.net` when present.

### KH-1029: a KiCad 5 `.sch` sub-sheet whose file is missing is dropped silently (the legacy twin of KH-481)

**Severity:** LOW (provenance; 82 corpus files / 255 sheet refs per survey A)
**File:** `skills/kicad/scripts/schematic/legacy_reader.py:1067-1070` (`if sub_path.exists()` with no else; no `missing_sheets`, no backslash replace); compare `schematic/reader.py:1345-1366` and `schematic/hierarchy.py:341-347`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey A (harness ask 5); verified by the harness at `f53d107e` (code read)

**Symptom:** the `.kicad_sch` reader now records "sheet file X named in Y does not exist" (missing sheet skipped). The legacy reader appends only sheets that exist and records nothing, so the design is analysed without the sheet and `diagnostics` stays empty. It also joins `base_dir / sheet_file` without the backslash replace.

**Fix direction:** collect missing legacy sheets the same way and record them through `parse_all_sheets`; normalize backslashes. Budget: `diagnostics[]` additions on the legacy units (v3.0.3).

### KH-1027: `ic_pin_analysis[*].pins[*].connected_to` lists every other pin on the net for every IC pin, so output grows with pins × net size (4.2 GB on discrete-nes row_group)

**Severity:** MEDIUM (output size; with the sheet cache, row_group reaches serialization inside the 120 s cap and needs > 8 GB to encode, MemoryError under an 8 GB limit)
**File:** `skills/kicad/scripts/schematic/ic_analysis.py:309-335` (`neighbor_summary` built from every `get_net_neighbors` entry, stored as `connected_to`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b survey A (harness ask 5); verified by the harness at `f53d107e` (code read + gate status)

**Symptom:** each IC pin on a shared bus or rail carries a dict per neighbour (ref, value, type, pin, pin name), so N ICs on one net give N² entries. Survey A measured row_group's output at 4.2 GB, 3.9 GB of it `connected_to`. The running Wave 11b-1 gate still records `AlexColello/discrete-nes/boards_ram_row_group.kicad_sch` as a timeout on both sides.

**Fix direction:** cap or summarize `connected_to` (counts by type plus the first few neighbours, or neighbour refs only). Output-changing; needs its own budget (3.1 / v3.0.3).

**Addendum 2026-11-16 (v3.0.3 Wave 12a gate, harness):** after the KH-1028 index fix (b6c6c34b) the discrete-nes `boards/ram` project still does not finish under the corpus profiles. Standard (32 jobs, 120 s): `boards_ram_ram` and `boards_ram_row_group` still time out on the candidate (the product's 68.5 s / 2.43 GB for `row_group` was measured alone); `boards_ram_row` 13.5 s -> 7.9 s. Hierarchy (discrete-nes alone, 2 jobs, 300 s, 16 GB per-unit ceiling): all 9 `boards/ram` units (8 sub-sheets + `ram` root) go from a 300 s timeout at `365aea94` to MemoryError at the 16 GB ceiling after ~110 s at `08879e2d`; the 7 `ram-prototype` units pass (RSS 436 -> 222-357 MB). Records `results/v303_w12a_gate_hier/`.

### KH-1021: KiCad 5 rescue symbol names carry the old library or project name, so family matching on the symbol name still reads a library name

**Severity:** LOW (false WL-001 "wifi/ble module" on rescue-symbol parts; a few corpus units)
**File:** `skills/kicad/scripts/detector_helpers.py:105-122` `match_family` (symbol name after `:`, rescue suffix kept); WL-001 `skills/kicad/scripts/domain_detectors.py:5781-5786`; full-lib_id readers `domain_detectors.py:306-307` (isolation keywords) and `skills/kicad/scripts/validation_detectors.py:538-539` (`_is_regulator_like` load-switch match)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** rescue symbols are named `<sym>-<lib>-rescue` or `<sym>-RESCUE-<project>`, and a legacy lib_id may have no `:`. Stripping the nickname therefore leaves the library or project name in the text.
- **WL-001:** on OLIMEX ESP32-EVB Rev B and Rev C, U1 `MCP73833(MSOP10)` (lib_id `MCP73833(MSOP10)-RESCUE-ESP32-EVB_Rev_B`) is "wifi/ble module U1". On ccadic/TI92-revive (×2), IC1 TCA8418 (`kb5-rescue:TCA8418-tca8418-ESP32-S2-WROOM-rescue`) is the same.
- **CERT-001:** the fallback that named `#PWR042` / KXKM J9 is fixed at `f53d107e`; OLIMEX GATEWAY Rev I now names U3.
- **Full lib_id:** the isolation-part and load-switch readers still match the whole lib_id, nickname included. The load-switch match can only remove findings (0 seen).

**Fix direction:** strip a trailing `-<lib>-rescue` / `-RESCUE-<project>` from the symbol name in `match_family`, and use symbol-name matching in the two full-lib_id readers.

**2026-11-17 addendum (Wave 12b, `1ff162b7`): partly fixed, stays open.** WL-001 fixed: OLIMEX ESP32-EVB Rev B and Rev C lose 'wifi/ble module U1 (MCP73833)' (U3 ESP-WROOM-32 kept); TI92-revive ti92revive + keyboard lose WL-001 IC1 TCA8418 plus the CERT-001 / RF-DET 86- and 82-part 'RF chain' of rescue-named keyswitches. symbol_name() at detector_helpers.py:105; the load-switch reader (validation_detectors.py:542) now reads the symbol name. The isolation reader (domain_detectors.py:298-312) still matches category words (isolated, murata, recom, traco, optocoupl...) against the whole lib_id. On oihdesigns/Micro-DMM Isolated_ADS1256 (project library nickname 'Isolated_ADS1256'), IB-DET still lists U2/U3 TPS7A4901 LDOs and U6 ADS1256 as isolation components on both sides. Still open: Not fully fixed. The isolation-part reader's category words still read the library nickname (the block's 'Full lib_id' item). Only the part-number stems moved to the symbol name. (harness agents at `7ed10f3e` vs `f254cb23`.)

### KH-1019: TR-DET reads P-channel MOSFETs as N-channel unless the lib_id, keywords, value or description spells out the channel

**Severity:** LOW (flyback, gate-drive and drain/source readings on P-FETs are inverted; about 100 TR-DET records on 58 units in a third of the corpus for a short list of common P-FET MPNs)
**File:** `skills/kicad/scripts/signal_detectors.py:3433-3444` (transistor analysis, `is_pchannel`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus read)

**Symptom:** P-channel is decided only from the words `pmos` / `p-channel` / `p_channel` / `pchannel` (plus `dmp` in the value and `p-mos` / `p-mosfet` in the description). An MPN on a part-named symbol is read N-channel:
- `alexreinert/PCB` HB-RF-USB.sch Q1/Q2 `Transistor_FET:IRLML6402` (source on +3V3), and `0Prashant/Kicad` H-Bridge Q4/Q7 IRF9540N.
- gitdoalberto dosimetro Q1 `DMG2305UX-13`, whose description "MOSFET P-CH 20V…" uses `P-CH`, which is not in the list.
- The survey's AO3401A cases are the same.

**Fix direction:** add a P-channel MPN family table (IRLML64, IRF9, AO340x, DMG23, SI23xx P parts…) and accept `p-ch` in descriptions, or read the symbol's pin order or arrow where available.

**2026-11-17 addendum (Wave 12b, `83bc936d`): partly fixed, stays open.** All named parts now read P: alexreinert HB-RF-USB Q1/Q2 IRLML6402, 0Prashant H-Bridge Q4/Q7 IRF9540N, gitdoalberto power Q1 DMG2305UX-13 (False -> True). Corpus scan of baseline TR-DET N records with P-looking names: candidate _names_pchannel recognises 513 of 584. About 56 true-P records stay N, e.g. DMG3415UFY/UQ, SSM3J358R/SSM3J133TU, PMV28XPEAR, AOD417/AOD403/AOD4185, SQJ407EP/SQJ479EP, SI2347DS. Run: fiskebolle30 Microcontroller Q1 SSM3J358R and dcuccia handbell Q3 still N at the candidate. Still open: The fix is a whole-PN table limited by ruling F-P4 (KiCad P symbols plus cited PNs), not a family table. Open and not filed: (1) uncited P MPNs (list above); (2) _PCH_NAME `mosfet[_-]p\b` misses generic symbols `MOSFET-P_DFN2015` and `MOSFET-PTO252`, because there is no word boundary before `_` or a letter. Only the onsemi orderable-tail gap is filed (new item `pchannel-onsemi-orderable-tail`). (harness agents at `7ed10f3e` vs `f254cb23`.)

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

### KH-1009: KiCad 5 `.sch` analysis runs no system-level analyses: no inrush, power budget, PDN, voltage derating, sequencing, sleep, USB / protocol compliance, test coverage, BOM optimization or assembly complexity

**Severity:** MEDIUM (whole analysis families are silently absent on every legacy schematic; 10,843 of 36,433 corpus schematic units are `.sch`; SKILL.md / methodology do not say so)
**File:** `skills/kicad/scripts/schematic/pipeline.py:930-1128` `analyze_legacy_schematic` (only `analyze_signal_paths` + `analyze_design_rules`, `:1096-1100`) vs `:1170-1281` `run_analyses` (the system-level calls, `:1227-1241`), which only the `.kicad_sch` path reaches (`:1427`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates, filed as an inrush cap-to-ground gap); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `analyze_schematic.py` on jherkenhoff/STM `Electronics/Supply-Board/Supply-Board.sch` (LM317 / LM337 ×2 each, output caps to `analog_gnd` / `piezo_gnd`) gives no `inrush_analysis`, `power_budget`, `pdn_impedance`, `power_sequencing`, `usb_compliance`, `protocol_compliance`. Findings carry no VD-001/002/004, DS-*, SS-*, ERC-label or PWR_FLAG audits. A wrapper on `analyze_inrush_current` is never called. The handoff's 7 regulators on 4 units (loxodes TPS72301 ×3, jherkenhoff LM337 ×2, blthree LM337, Fescron "DC/DC 5V out") are all `.sch`; their caps do resolve to ground.

**Fix direction:** run `run_analyses` (or the shared system-level subset) on the legacy context, behind its own corpus budget. Until then, document the reduced scope and record one `diagnostics` note.

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

### KH-1001: `connector_layout` never sees the footprint, and reads the library nickname: opaque-symbol dual-row parts read `single`, a `_2x5` nickname reads `dual`

**Severity:** LOW (`components[].connector_layout` only; no reader in the product)
**File:** `skills/kicad/scripts/kicad_core/classify.py:557-566` `_row_layout`, `:569-593` `classify_connector(lib_id, value, pin_count)` (no footprint argument; `_row_layout(lib_id.lower())` reads the whole lib_id); caller `schematic/reader.py:1033`
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + probe)

**Symptom:** probe: `classify_connector("43650-0400", "Conn_01x04")` → `single`, though the part sits on `Molex_Micro-Fit_3.0_43045-0400_2x02_P3.00mm_Horizontal` (DRILLTEAM `Drill V2/DRILLTEAMYMchanges.kicad_sch`: LC1-3, ENC1, ENC2, Servo1, Stepper1, 7 parts). `classify_connector("Proj_2x5:Header", "HDR")` → `dual` from the nickname.

**Fix direction:** pass the footprint and let a footprint row count outrank the value. Read only the symbol name of the lib_id.

### KH-999: CERT-001 and WL-001 miss a wireless module valued `WROOM32` (no `esp` in value or symbol name)

**Severity:** LOW (a true "Wireless module detected" FCC Part 15 suggestion is lost)
**File:** `skills/kicad/scripts/domain_detectors.py:5629-5631` `suggest_certifications` `radio_words`; WL-001 `_WIFI_BLE_KEYWORDS` (same file, after `:5740`)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read + corpus)

**Symptom:** the fallback now reads value + symbol name only (the nickname is dropped), and neither list has a bare `wroom`. ep-infosec `makerspace-partsbin` `iot-button/esp32_button.sch` and `esp_module.sch`, M401 `WROOM32` (lib `esp32:WROOM32`): the baseline 5510006 says "FCC Part 15: Wireless module detected: M401"; the candidate has no CERT-001 there.

**Fix direction:** add `wroom` (and `wrover`) to both word lists, as words that name Espressif modules.

**2026-11-17 addendum (Wave 12b, `cd3160d1`): partly fixed, stays open.** cd3160d1 adds wroom/wrover to radio_words and _WIFI_BLE_KEYWORDS. Run: ep-infosec iot-button esp32_button.sch and esp_module.sch, M401 WROOM32: CERT-001 'FCC Part 15: Wireless module detected: M401' goes from absent to present. Still open: The WL-001 half still misses M401. M401 is typed 'other' (ref M), and detect_wireless_modules walks get_unique_ics (type=='ic' only), so WL-001 is [] on both named units at the candidate. The keyword helps only IC-typed WROOM parts (reconcile: WL-001 +6). (harness agents at `7ed10f3e` vs `f254cb23`.)

### KH-998: the headless-browser download fallback runs only with `datasheets.allow_private_hosts`; fetch through the pinned opener so it can run by default

**Severity:** LOW (about 2 % of downloads for users with Playwright, e.g. Broadcom `docs.broadcom.com` and Espressif, fall back to "give the user the URL")
**File:** `skills/datasheets/distributor_core/download.py:469` (`if _sync_playwright is not None and not addresses`), `:517-520` (once-per-process note), `:844-877` `_policy_route` (`route.fetch` resolves in the browser)
**Discovered:** 2026-11-07, product v3.0.2 Wave 11b-1 handoff (new-KH candidates); verified by the harness at `f53d107e` (code read)

**Symptom:** with the default policy (addresses checked), `download_pdf` never adds the Playwright method, because the browser would resolve each host itself (the DNS-rebinding gap KH-647 closed by refusal). Sites that need JavaScript no longer auto-download.

**Fix direction:** fetch each routed hop in Python through the pinned urllib opener and answer it with `route.fulfill(status, headers, body)`. Launch Chromium with `--host-resolver-rules="MAP * ~NOTFOUND"` so the browser resolves nothing itself. Cookies, encoding and redirects need a real-browser test (`RealPlaywrightTest`). Target 3.1.

### KH-985: Deep Review `find_pdf` falls back to `<MPN>_*.pdf` when the manifest marks the part `not_found`, so `LM317` gets the LM317/NOPB datasheet

**Severity:** LOW
**File:** `skills/kicad/review/scripts/deep_review_gate.py:261-315` (`_manifest_pdf`, `find_pdf`)
**Discovered:** 2026-11-06, product v3.0.2 Wave 11a handoff (new-KH candidates); verified by the harness at `5510006a` (code read + probe)

**Symptom:** `_manifest_pdf` stops only on `status: ok` + `verification: wrong`; `not_found` returns `(None, False)` and the single-hit prefix fallback runs. Probe: manifest `LM317: not_found`, `LM317/NOPB: ok → LM317_NOPB_Linear_Regulator.pdf`; `find_pdf(d, 'LM317')` returns that PDF. The fallback also runs with no manifest entry at all; `not_found` is the case where it is plainly wrong. The fallback came in with the KH-429 fix.

**Fix direction:** a manifest entry other than `ok` stops the lookup; the prefix fallback only for parts the manifest does not list, and only when the sibling is not itself a manifest key.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by fc88e9c9):** fixed: a prefix hit that the manifest lists for another part is dropped, so `LM317` no longer takes `LM317_NOPB_*.pdf` (`deep_review_gate.py:281-283`, `:318-319`). Still open: a `not_found` part still falls back to an unlisted `<MPN>_*.pdf` (`:302-320`), as does a stray sibling PDF whose manifest entry has no `file`. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** 307f7856 / f702ad19 (after fc88e9c9) stop a `not_found` part falling back to an unlisted `LM317_*.pdf` (base returned it, candidate None; a hand-placed `LM317.pdf` is still used). **Still open:** (1) the addendum's case: LM317 not in the manifest, `LM317/NOPB: not_found` with no `file`, a stray `LM317_NOPB_Lin.pdf` — `find_pdf('LM317')` still returns it on both sides, because `others` (`deep_review_gate.py:283`) collects file names, not sibling keys; (2) an `ok` entry whose file is missing still takes the prefix fallback (`:288-294`); the fix direction limits the fallback to parts the manifest does not list.

### KH-989: VM-001 reports an open-drain status output pulled up to a lower rail (a charger's STAT / CHG) as a domain crossing at the IC's supply voltage

**Severity:** MEDIUM (error-severity false positive)
**File:** `skills/kicad/scripts/validation_detectors.py:528-553`, `:576-700`
**Discovered:** 2026-11-06, product v3.0.2 Wave 11a handoff (new-KH candidates); verified by the harness at `5510006a` (code read + probe)

**Symptom:** each IC endpoint's domain is its supply estimate (`_estimate_rail_voltage_for_ic`); pin type (open collector / open drain) and the pull-up rail are never consulted. The only exemptions are USB D± and `_en_endpoint_compatible` (EN/PG names on regulator-like parts; no chargers such as BQ24/MCP738/TP4056, and no `STAT`/`CHG`/`CHRG`/`FAULT`). A 28 V charger's STAT reaching a 3.3 V MCU gives v_max 28 V > abs max → error. Reported by the PR #68 author once comma bus groups join the nets; not reproduced here (no design), plausible by code read.

**Fix direction:** exempt open-collector / open-drain output pins whose net has a pull-up to the receiving rail; size it on the corpus. Family: KH-667, KH-721. Lands with PR #68 (Wave 11b) if the join exposes it.

**Addendum 2026-11-07 (v3.0.2 Wave 11b-1, candidate `f53d107e`, partly fixed by 3cf931c4):** fixed: open-collector and charger STAT/CHG/CHRG pins are judged at their pull-up rail (`validation_detectors.py:582`, `:593-603`, `:677-684`). Still open: `FAULT` / `nFAULT` (named in the symptom) is not in `_OD_STATUS_NAMES` (`:582`); charger PG / STDBY pins typed `output` are still judged at the IC supply. The fixed half is gated in the Wave 11b-1 gate (results/v302_w11b1_gate*).

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

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** the band-edge double count is 9,887 of 11,883 SW-001 (ruling R10 (a): half-open bands now; `--standard` keeps selecting coverage labels only).

### KH-630: SPICE net-name sanitiser maps distinct nets to one node and does not reserve the testbench's own node names

**Severity:** LOW (rare collisions; usually a silently dropped run)
**File:** `skills/spice/scripts/spice_models.py:166-167` (char-replace loop); guard `spice_templates.py:177-178`
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F10)

**Symptom:** `IN/1` and `IN?1` map to the same node; nothing reserves `ac_in`, `sig_in`, `VCC`, `VEE`, `fb_net`, `port`; ngspice node names are case-insensitive. Result: a guarded `None` (run dropped without a record) or, rarely, a short between nets.

**Fix direction / budget:** an injective, case-folded name map with the reserved names excluded. Budget: changes only on colliding designs (size first; expected tiny).

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
`_sanitize_net` (`spice_models.py:165`) does not replace `-`. The bench writes `let vout_sim = v(usb1-vbus)`, which parses as `v(usb1) - vbus`; ngspice says `Error: RHS "v(usb1-vbus)" invalid`. 20 voltage_divider benches skip with "ngspice operating point failed" (1 at base). Their mid nets hold `-`, `/`, a space or parentheses (`usb1-vbus`, `ETH_CLK-`, UUID sheet paths, `UART_RX (HM-10)`). Newly reached by the read dividers; an honest skip. (`X/task-11-report.md` concern 2.)
  Harness check (`ea5f7fd1`): spice_models.py:177-180 _sanitize_net replace set ' (){}[]!@#$%^&*=+|\;:'",<>?/' has no '-'; spice_templates.py:358 / :1017 write ('vout_sim','let', f'v({mid_net})'). ngspice -b on a 3-line deck with net usb1-vbus: 'Error: RHS "v(usb1-vbus)" invalid' (reproduced). 20-bench count not re-measured. KH-630 is about collisions / reserved names, KH-1051 about duplicates / keywords; the '-' case is new content for either.

### KH-629: SPICE LTspice and Xyce backends lose their measurements — the LTspice `.log` is overwritten by the capture, and `let` / `extra_vars` / rise-fall are never emitted

**Severity:** MEDIUM (LTspice is the auto-detected engine when ngspice is absent, common on Windows/macOS; results skip rather than mislead, except the crystal bench)
**File:** `skills/spice/scripts/simulate_subcircuits.py:238-239`, `:269` (`<label>.log` opened "w" after `run()`); `spice_simulator.py:304-305` (`parse_results` derives `<label>.log` from `<label>.out`), `:317` (`encoding="utf-8", errors="replace"`), `:288-290` and `:400-402` (`elif func == "let": pass`), `:416-417` (Xyce `<label>.mt0`), `:473-477` (auto-detect falls through to LTspice)
**Discovered:** 2026-10-25, external audit round 1 at `07b7fb1` (`docs/audit/03-v3-skills-code/findings/VERIFICATION.md` sk/R2-F7, sk/R2-F8)

**Symptom:** on LTspice the native `.meas` log is replaced by the subprocess capture before parsing, so every measurement is lost → skip; native logs are commonly UTF-16LE, which defeats the `^(\w+):` regex even after a rename. On both alt backends every `let`-only result (divider `vout_sim`, `error_pct`, LC `f_peak`, op-amp `target`, …) is absent, `extra_vars` is accepted and dropped, rise/fall is dropped, and `when … =target_lo` names undefined values. The crystal bench passes on `{}` (KH-612). Xyce names measure files `<netlist>.cir.mt0` (convention, unverified here). Static reading only — no LTspice/Xyce installed.

**Fix direction / budget:** write the capture to a different file and decode UTF-16; translate lets to `.meas … param=` or compute them outside the simulator; or reject the alt backends explicitly until fixed. Waits on ruling: fix or reject. Budget: LTspice/Xyce users only; outside the ngspice-only spice-offline gate.

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** e1357434 makes `simulate_subcircuits` (and `what_if --spice`, which goes through it) refuse LTspice / Xyce with exit 1, which removes the `.log` overwrite, the lost `let` / `extra_vars` / rise-fall values and the crystal bench passing on `{}` there. **Still open:** `spice_simulator.py` is unchanged in the range and `analyze_emc --spice` still auto-detects LTspice / Xyce or takes `SPICE_SIMULATOR` (`emc_spice.py:33`, `:182`, `:596`), running the generated PDN benches through `LtspiceBackend.parse_results`, which still reads the native log as UTF-8 (`spice_simulator.py:333`). The product's close-by-refusal covers the subcircuit benches only.

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

**2026-11-17 addendum (Wave 12b, `ae203e6b`): partly fixed, stays open.** Single-letter fallback fixed (classify.py:516-523): RF-C20 on myproj-rescue:CP-Device is now capacitor (was resistor); RF-L10 on L_Core_Ferrite is ferrite_bead (as an L ref gives); L_Core_Iron is inductor; LD4 on Device:LED / LED_Small / LED_RGB with values '' / Green / CAPS is led (was inductor). Refs whose whole prefix is in type_map skip the symbol check. RS.C3 / RS.C2 on Device:C_Small 100nF (Antigo89/KiCAD-libraries) is still resistor on both sides, as are RS1 Device:C, CR1 Device:C (diode), RT1 Device:C (thermistor) and RN1/RA1 Device:C. Value-unit evidence is unused: RF-C10 with no lib or mylib:CAP_0402, value 5pF, stays resistor. Still open: The named examples are fixed. The block's principle (symbol or capacitance unit outranks the R prefix) still fails for full-prefix refs (RS.C3 is a corpus case) and for value-unit evidence. Either keep the KH open with an addendum, or close it and file the full-prefix case new. (harness agents at `7ed10f3e` vs `f254cb23`.)

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

### KH-1139: the no-underscore power-name branch (`5VEN`, `5VPGOOD`) still uses the old suffix set

**Severity:** LOW
**File:** `skills/kicad/scripts/kicad_core/netnames.py:229-231` (`_VOLTAGE_SIGNAL_SUFFIXES`)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (b) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the no-underscore branch uses the old suffix set, so `5VPGOOD` reads as a rail.
**Fix direction:** share `RAIL_SIGNAL_SUFFIXES` in the no-underscore branch.
**Status at `6b9767e1`:** probe `is_power_net_name('5VPGOOD')` True.

### KH-1140: LB-001 `label_count` counts instance-qualified entries and fires once per instance on legacy port renames

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (c) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** LB-001 `label_count` counts instance-qualified entries, and LB-001 fires on legacy port renames once per instance.
**Status at `6b9767e1`:** not individually re-verified (code untouched since filing).

### KH-1141: a repeated legacy sheet with no `AR` record gives every instance the same references

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/legacy_reader.py`
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (d) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a repeated legacy sheet with no `AR` record gives every instance the same references.
**Status at `6b9767e1`:** not individually re-verified.

### KH-1142: legacy sheet-pin labels are always angle 0; an escaped quote in a sheet-pin name truncates it

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/legacy_reader.py`
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (e) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** legacy sheet-pin labels are always angle 0; an escaped quote in a sheet-pin name truncates it.
**Status at `6b9767e1`:** not individually re-verified.

### KH-1143: inverting-regulator output rails stay positive in `rail_voltages`; what_if drops the fix suggestion for inverting rails

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (f) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `rail_voltages` sign is inconsistent across sources (inverting-regulator output rails stay positive); what_if drops the fix suggestion for inverting rails (see also KH-675 / KH-719).
**Status at `6b9767e1`:** the `/Analog/-5V` part is fixed (a0c24476: reads -5.0); the inverting-regulator and what_if parts not re-verified.

### KH-1145: a full-circle `gr_arc` (|angle| ≥ 360) is treated as a point by bbox / NR-001 / EMC

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/`
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (h) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a full-circle `gr_arc` (|angle| ≥ 360) is treated as a point by bbox / NR-001 / EMC.
**Status at `6b9767e1`:** not individually re-verified.

### KH-1146: courtyard doubling: duplicate `fp_circle` / `fp_rect` not checked; F/B outlines interfere in PM-001; a side doubled on one layer drops both sides

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/reader.py`, PM-001
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (i) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** duplicate `fp_circle` / `fp_rect` courtyards are not checked for doubling; different F/B outlines still interfere in PM-001; a side doubled on one layer drops both sides.
**Status at `6b9767e1`:** not individually re-verified.

### KH-1147: contact model: trapezoid / chamfered pads measured as their full box; explicit F.Cu/B.Cu THT pads get no inner layers; slow track-track bbox query; unguarded `roundrect_rratio`

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/connectivity.py`, `pcb/geometry.py`
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (j) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** trapezoid / chamfered pads are measured as their full box in the contact model; explicit `F.Cu` / `B.Cu` THT pads get no inner layers (unverified); the track-track overlap query scans a whole bbox (slow on long diagonals); `float(roundrect_rratio)` is unguarded.
**Status at `6b9767e1`:** not individually re-verified; contact-model items belong with the C14 wave (KH-751).

### KH-1148: sheet pins use the label rule (1 IU on a wire) where KiCad may join them only at wire ends

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (k) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** sheet pins use the label rule (1 IU on a wire) where KiCad may join them only at wire ends (unmeasured); `SEG::SquaredDistance` rounding ported from KiCad master.
**Status at `6b9767e1`:** not individually re-verified.

### KH-1149: three outline / pad distance helpers duplicate geometry

**Severity:** LOW (code health)
**File:** `skills/kicad/scripts/pcb/geometry.py` and callers
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (l) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the Wave 3 outline / pad distance helpers duplicate geometry.
**Fix direction:** consolidate.

### KH-1150: a courtyard side with only degenerate (< 0.01 mm) segments loses the whole `courtyard_poly`

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/reader.py:713` (tests `crtyd_segs[_side]`)
**Discovered:** 2026-10-26, product 3.0.x Wave 3 (handoff §Asks 4 a-l, r); split from KH-674 item (r) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a side with only degenerate segments gives an empty `_unique` and the whole courtyard is marked not closed; PM-001 falls back to the AABB.
**Fix direction:** `if not _unique: continue` (one token).
**Status at `6b9767e1`:** code read confirms.

**2026-11-19 (Wave 12c plan move, handoff ask 5):** → 12f.

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

**Addendum 2026-11-15 (v3.0.3 Track H synthetic upgrade lane, kicad-cli 10.0.8 over quick_200, record `results/v303_refresh/REPORT.md` §3e):** KiCad 10 itself writes an empty pin name as `""` (≤ 9 wrote `~`), so the same design re-saved by KiCad 10 already reads `""`. On units whose connectivity KiCad's own netlist shows unchanged, OA-DET loses 1,817 detections in 365 units when the op-amp output pin name goes `~` → `""` (verified dragonlock2/kicadboards `6wire/guard.kicad_sch` U6 MAX4238, pin 1), with RC-DET +874 / 147 units as the cascade, and NT-001 / EP-AUD / PU-001 / LR-001 / PP-001 / SJ-DET findings rename 1:1 (NT-001 14,401 in 757 units). The ruling R13 normalization (`~` → `""` everywhere) would move the OA-DET loss onto every pre-10 file too unless the op-amp detector stops depending on a non-empty output pin name; land both together and use the lane as the check (findings identical between a file and its KiCad 10 re-save).

**2026-11-17 addendum (Wave 12b Track H, survey-H; ruled RULINGS-12b section 4):** the pin *number* `~` → `""` half (`sch_io_kicad_sexpr_parser.cpp:2172`; 5 lane units: AlexCAB ×3, Churrosoft, gregdavill). R13 should name it. Harness check: KH-687 open, title names pin number; schematic/reader.py:99 keeps number verbatim, tilde_empty only on _alt_base name (:114) at 7ed10f3.

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

**2026-11-17 addendum (Wave 12b, `af7eedb4`): partly fixed, stays open.** item (h) is fixed (`1 000k` → 1e6, `4 700R` → 4700, `100nF,50V` on a typed capacitor → 1e-7; `1000 000` → 1000 stays, deliberately, `values.py:162-163`). Item (m) was already fixed before the range. Items (a)-(g) and (i)-(l) are untouched by the range and stay open (e.g. (b) `reader.py:1166` still tests `pins[0]`). (harness agents at `7ed10f3e` vs `f254cb23`.)

**2026-11-19 (Wave 12c plan move, handoff ask 5):** (a) → 12g; (b)-(g) and (i)-(l) → 12e (no value-reader item left open; (h) fixed in 12b, (m) earlier).

### KH-701: net-less copper never takes a net — KiCad's `PropagateNets` joins pads through a net-less or `(net 0)` copper shape

**Severity:** LOW (pre-existing; conformance)
**File:** `pcb/reader.py` (`read_board`), `pcb/connectivity.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B (ruling R25); filed by the harness from the handoff §Asks 4

**Symptom:** KiCad propagates nets onto net-less copper (`connectivity_algo.cpp:665-724`: net-agnostic clusters, zones excluded; tracks, arcs, `PCB_SHAPE` and non-free vias take the cluster's net unless the cluster has pads of two nets; it never merges nets). kicad-cli 10 joins two pads through a net-less or `(net 0)` copper `gr_poly` or segment with 0 unconnected. We keep "no net joins nothing". Reach upper bounds: ≈ 430 boards with net-less copper `gr_*`, ≈ 570 with net-0 tracks.

**Fix direction / budget:** the pass belongs in `read_board` (the graph is per net) and moves default-path track nets (`net_lengths`, RT-001), so it needs its own survey, oracle and budget. When it lands, flip the product tests `tools/tests/test_pcb_graphic_copper.py::test_graphic_without_net_joins_nothing` (:105) and `::test_graphic_net_zero_joins_nothing` (:110).

**Addendum 2026-10-29 (3.0.x Wave 4 Part B):** stays open; home is the C14 umbrella KH-751 (rerun Task 111's residual when it lands).

**2026-11-08 (v3.0.2 Wave 11b-2, ruling D1 concern 1):** the converse case. KiCad also re-nets a segment that carries a net in the file, taking the net of the pads it joins, while the analyzer keeps the file's net. JackMatanky kb_snak `snak_28` (2 boards) exposes it now that D1 reads its mixed-token footprints (the candidate PCB snap has 172 footprints, incl. `PWR1` / `JST1` / `PAD1`). The product reports fc CK-003 +2 and 4 RT-001 extras, false by KiCad's reading, budgeted under d6-mixed-tokens. Not re-run against kicad-cli here. Same `read_board` net pass; flip the snak_28 items when it lands.

**2026-11-17 addendum (Wave 12b Track H `KH-NEW-H6`, folded in by the harness):** KiCad's net propagation onto unnetted or mis-netted copper is not modelled. Severity: MEDIUM (false RT-001 on generated and imported boards; missing CC-DET / TS-DET). File: `skills/kicad/scripts/pcb/reader.py:845-853` (segments, arcs, vias keep the stored net), copper graphics, `pcb/routing.py:44-67`; at `de28149d`. KiCad: `connectivity_algo.cpp:684-736` (`propagateConnections`, skips conflicting clusters). Symptom: kb_snak (192 of 204 segments without a net) gives `Unrouted net C1 (9 pads)` ×46; Churrosoft tracks stored on net 144 touch C19 pad 1 (net 152); CRImier copper `gr_arc` traces with no net; a `(net 0)` via in a GND zone. Reach: lane 22 units (RT-001 −359 net, i.e. the lane −558 minus the 199 from H5; CC-DET +12, TS-DET +6); static upper bound 2,096 boards / 267,334 unnetted tracks and vias. Fix: assign single-net cluster nets at read time and leave conflicting clusters alone. Oracle: the board's own `kicad-cli pcb upgrade` output. Ruling H-3: fix in 12f with KiCad's conflicting-cluster rule; fallback 3.1 + declare.

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

### KH-1151: CP-001 `layer` names the footprint's layer when only a cross-side SMD pad fires it

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (a) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the CP-001 finding's `layer` field still names the footprint's layer when only a cross-side SMD pad fires it (0 seen in 100 boards).
**Fix direction:** fold into the next CP-001 edit.

### KH-1152: a hatch fill on a copper graphic counts as solid

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (b) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a hatch fill on a copper graphic counts as solid (KiCad's effective shape leaves holes; could join both ways). Reach 0.

### KH-1153: a zone with no `min_thickness` on a stroked-fill board is not inflated (KiCad uses 0.25 mm)

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (c) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a zone with no `min_thickness` on a stroked-fill board is not inflated; KiCad uses the 0.25 mm default (corpus ≈ 0; harness fixture `tests/fixtures/kh392-antipad/board.kicad_pcb` has this shape and would move).

### KH-1154: VP-001 does not read KiCad 9 via `(filling)` / `(capping)` protection

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (e) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** VP-001 does not read KiCad 9 via `(filling)` / `(capping)` protection.
**Status at `6b9767e1`:** unreachable on the corpus (reach 0, AD-B9).

### KH-1155: `--variant` overrides Value / Footprint / Datasheet / Description (and Reference) even when the symbol lacks the property

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/reader.py:925-929`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (f) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the analyzer applies a variant `(field (name "Reference") …)` and overrides Value / Footprint / Datasheet / Description even when the symbol lacks the property; bom_manager and KiCad's `GetFieldText` do neither (KiCad never writes a Reference override).
**Status at `6b9767e1`:** unreachable on the corpus: only Description on pre-8 symbols can hit it (variants are KiCad 10; the others are mandatory fields).

### KH-1156: malformed polygon arcs are skipped silently (KiCad raises)

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (g) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** malformed polygon arcs are skipped silently (KiCad raises).

### KH-1157: a modern board with drill-less vias and no `(net_class)` uses 0.3 / 0.1 mm, not the `.kicad_pro` Default class

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/reader.py:1152-1157`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (h) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a modern board with drill-less vias and no `(net_class)` uses KiCad's 0.3 / 0.1 mm default; KiCad would use the `.kicad_pro` Default class, which the reader does not read (1 corpus board).

### KH-1158: the connectivity graph places every pad's copper at the hole centre (KiCad uses `ShapePos`)

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/connectivity.py`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (i) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the pad drill offset decides NPTH copper only; the graph still places every pad's copper at the hole centre (KiCad uses `ShapePos`; pre-existing for all pads, W3-15).
**Fix direction:** contact-model change with the C14 wave (KH-751); rerun `rc_conf_g.py`.

### KH-1159: bom_manager names the project from the input stem and walks only the named root of a multi-root project

**Severity:** LOW
**File:** `skills/bom/scripts/bom_manager.py:685`
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (j) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** bom_manager names the project from the input stem, not the `.kicad_pro` stem or a KiCad 10 declared root; it walks only the named root of a multi-root project (KH-692 family).

### KH-1160: `copper._mask_opening_size` reads only the pad-local mask margin

**Severity:** LOW
**File:** `skills/kicad/scripts/pcb/copper.py` (`_mask_opening_size`)
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (rider 1) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** reads only the pad-local margin (KiCad: pad → footprint → board `pad_to_mask_clearance` → DRC rule) and its docstring overclaims.

### KH-1161: VP-001 `_via_exposed_by_pad` ignores a negative mask margin and one-side tenting (TV-001 and VP-001 disagree)

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (rider 2) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** VP-001 `_via_exposed_by_pad` ignores a negative margin and one-side tenting, so TV-001 and VP-001 disagree.

### KH-1162: a heatsink pad without a TV-001 entry gets no wicking feedback

**Severity:** LOW
**File:** see the item
**Discovered:** 2026-10-27, product 3.0.x Wave 3b Part B; filed by the harness; split from KH-710 item (rider 3) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** a heatsink pad without a TV-001 entry gets no wicking feedback (ruling R53 cost).

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

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present: three SacMap decoupling / PDN benches report `pass` with `expected: {}` (`skills/spice/scripts/spice_results.py:742`, `:762-773`: pass on a generic `z_at_1m < 10.0`, else pass "Decoupling caps present").

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

**2026-11-19 addendum (Wave 12c, stays open):** (a) fixed in Wave 12c (`7d62c136`): `PWR_OK2`, `5V_FAULT`, `VBAT_ADC`, `5V_ISENSE`, `12V_{FBM}`, `PWR_LED` are not power names; `VDD_ADC`, `3V3_LED`, `*_FLT` stay rails. Open: (b) a labelled rail-named node stops a divider chain → 3.1; (c) plane identity → 12j (R7).
  Harness check (`ea5f7fd1`): (a) is_power_net_name base->cand: PWR_OK2, 5V_FAULT, VBAT_ADC, 5V_ISENSE, 12V_{FBM}, PWR_LED T->F; VDD_ADC, 3V3_LED, 5V_FLT, 12V_{FLT} stay T (A1). Corpus mlab-modules/USBPDSINK01: LA-AUD D3 supply_net PWR_OK2 -> +3V3, RS-001 'PWR_OK2 has no declared source' and the DO-DET PWR_OK2 decoupling gone. (b) 3.1 and (c) 12j per RULINGS-12c D.

### KH-719: readers that lose a rail's sign (fixed 79xx estimate +5 V on `-5V`, boost with a negative divider top, `-VCC_5V`, op-amp `-VBAT`, SPICE `_infer_voltage`)

**Severity:** LOW-MEDIUM (KH-675 sibling)
**File:** `signal_detectors.py` (`_lookup_vref` `LM7[89]…`, boost path, `_rail_name_voltage`), op-amp rail read, `skills/spice/scripts/spice_templates.py` (`_infer_voltage`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness (KH-675 remainder)

**Symptom:** fixed 79xx regulators estimate +5 V on `-5V` (james-l-key U204 LM7905, `rail_voltages['-5V'] = 5.0`); a boost path with a `V-`/`VEE`/leading-minus divider top reads positive (no test); `_rail_name_voltage` reads `-VCC_5V` as 5; op-amp `-VBAT` → +3.7; SPICE `_infer_voltage` has no sign (negative-rail transistor benches run at +3.3 V, results info/warn, never pass) and reads `0V…` names (`0VCC`, `0V_SENSE`) as 0 V (`test_spice_zero_span.py` pins the no-sign quirk and must flip with the fix); op-amp rails on sheet paths (`/sheet/-12V`) are not parsed (lost criterion → info).

**Fix direction / budget:** keep the sign in every reader; budget `rail_voltages` / regulator estimates and the affected benches.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, candidate db551674; slug KH-new-negative-fixed-suffix):** the fixed-suffix reader keeps a sign only for `LM79xx` (`kicad_core/parts.py:238-240`). `[-_](\d+\.\d+)` (`:252-255`) reads other negative fixed parts as positive: `LM2990SX-5.0` → +5.0, `ADP7182AUJZ-5.0` → +5.0. `L7905CV` / `MC7912` → no value. skumlos bkm-129x IC050 LM2990SX-5.0 (input `-6V`) shows `estimated_vout` +5.0 beside `output_rail` `VSSA` now that KH-964 restored the output rail. `rail_voltages` is protected by the VSS guard (`schematic/pipeline.py:342`), but the regulator record is not. The `LM7905` example in the symptom is already −5.0 (fixed before 6138b126). Fix: a negative-regulator family or an input-rail sign (negative Vin, not `inverting`) negates the suffix.

**Addendum 2026-11-13 (Wave 11c, verified at db551674; handoff note "LM317 F+15V info vs LM337 F-15V fail"):** SPICE `_rail_name_voltage` (`skills/spice/scripts/spice_templates.py:894-912`) reads `F-15V` as +15 (a `-` after a letter is not a sign) and cannot read `F+15V` (a `+` inside the token). On jaromir-sukuba/nvm MARGE `nvm_pmain_fpsu`, U16/U17 LM337 are compared against |15| / |8| V and fail (6.7 %, true: the dividers set 16.08 / 7.5 V). U14/U15 LM317, with the same dividers on `F+15V` / `F+8V`, fall to info ("the rail's name carries no voltage"), so two true fails are missed. Fix with the KH-719 sign work: take a `+`/`-` before the number inside a token as the sign. Kicad-side half: KH-new-net-voltage-mid-minus. Gate budget: SPICE regulator_feedback info → fail on the nvm LM317 twins (2 per MARGE sheet).

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, stays open):):**
the `-VBAT` readers.
- An op-amp on `+5V` / `-VBAT` reads V− +3.7 V, unflagged and not repaired (3.7 < 5), at base and tip.
- `_signed_supply_voltage('-VBAT')` gives −3.7 for the MOSFET / BJT benches (added in the range by `e38f67a4`).
- Both disagree with `-VBAT` as a ground return (lane N, `c4c5fd11`). `VBAT` / `-VBAT` reads (3.7, 0) repaired, which agrees with the ground.
- Also: `-VCC_12V` reads (12, −12) with `rails_named` False.
- Reach 0 (no `-VBAT` net in the corpus). Fix direction: return the default for `is_ground_name(net)` in `_signed_supply_voltage` and in the op-amp fallback.
- Evidence: `D/reviews/final-fixwave-rereview.md` m2 and observations 2-3.
  Harness check (`ea5f7fd1`): spice_templates._infer_opamp_rails probe (V+ / V- pins) base -> tip: (+5V, -VBAT) (5.0, 3.7) unrepaired both; (VBAT, -VBAT) (3.7, 0) vee_repaired both; (+12V, -VCC_12V) (12, 0) repaired -> (12.0, -12.0) rails_named False (new in range). _signed_supply_voltage('-VBAT') = -3.7 at tip, function absent at base. is_ground_name('-VBAT') False -> True. Note: 'op-amp -VBAT -> +3.7' is already in KH-719's symptom; the new content is the bench reader, the ground conflict and -VCC_12V (which changed in the range).

**2026-11-19 addendum (Wave 12c, stays open):** Fixed in Wave 12c: L7905CV −5, MC7912 −12, 79L05 −5, MC79M05CDTG −5, bare-suffix fixed parts on a negative input negative, positive codes on a negative input no estimate, the negative-divider boost test, SPICE `_rail_name_voltage` `-VCC_5V` none, transistor benches on a negative supply skip with the reason. Open: the `-VBAT` readers (section C above).
  Harness check (`ea5f7fd1`): Fixed as claimed: L7905CV None->-5, MC7912 None->-12, 79L05 None->-5, MC79M05CDTG None->-5; LM7905 -5 both sides. skumlos bkm-129x IC050 LM2990SX-5.0 on -6V: estimated_vout +5.0 -> -5.0 and rail_voltages VSSA None -> -5.0 (R-G1-7); lookup_regulator_vref('LM2990SX-5.0') stays +5 as stated. james-l-key U204 -5V -5 both sides. SPICE _rail_name_voltage: '-VCC_5V' 5.0 -> None, 'F+15V' None -> 15, 'F+8V' None -> 8. _signed_supply_voltage: '-12V' -12, '-VBAT' -3.7, used by the MOSFET and BJT benches (spice_templates.py:1087/1090/1204). Op-amp rails on /s/+12V and /s/-12V give (12, -12) at both SHAs. Open as stated: _infer_opamp_rails with V+ = +5V and V- = -VBAT gives (5.0, 3.7) at both SHAs (unflagged). **Correction to the product's remainder:** The remainder text should also name two sub-items that are not fixed and not closed by a RULINGS-12c entry. (1) The filed '0V… names read 0 V' item: _infer_voltage('0VCC') and _infer_voltage('0V_SENSE') still give 0.0. It is closed only by the survey G1 recommendation, not by a RULINGS-12c row, and ruling G2-3 calls 0VCC a supply. (2) _infer_voltage is still unsigned at its other SPICE callers: the divider/RC top_net at :339 and :991, the protected_net at :1366 and the power_net at :1749. A '-12V' top net falls back to the default vin. The filed text names _infer_voltage in its title. Minor: SPICE _rail_name_voltage('F-15V') is still +15. This is consistent with R6 and has no effect on the magnitude-only feedback bench, so no action is needed.

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

**2026-11-19 addendum (Wave 12c, `68f422cc + 9ce0d18f`): partly fixed, stays open.** harness agents at `ea5f7fd1` vs `ca59d562`: Output-pin rule landed (_has_direct_source :5111-5133; _SUPPLY_INPUT_PIN :4227). But the 11c addendum's open names are not all output-pin nets. REV2V5 at rjhelms/compe6502 Hardware_io_card_io_card.sch + Hardware_io_card_CassetteModem.sch is a divider tap (R9 to +5V, R10 + C6 to GND, VD-DET detects it), no IC/diode pin: RS-001 'no declared source' fires on both sides. Same for 2.5V divider/bias taps: adeboni drum_trigger_adapter (R1 +5V / R2 GND), bread-modular 4_mix (op-amp + input bias), kanengomibako Sodium: RS-001 unchanged. Only emdotnet/stmbl 11ua 2.5V went away. No 12c ruling closes divider-made bias nodes. **Still open:** Fixed: an IC or reference-diode output pin sources the rail (except load-switch outputs and supply-named output pins, S-P1). Still open: passive-only bias nodes named like rails (REV2V5 on rjhelms/compe6502 io_card + CassetteModem, a VD-DET +5V/GND divider tap; 2.5V on adeboni drum_trigger_adapter, bread-modular 4_mix, kanengomibako Sodium) still get RS-001. Keep KH-724 open for that (or file it as a new KH, e.g. rs001-divider-tap-bias-node: a net whose only part pins are passives and which is a VD-DET mid-point needs no declared source), or close it by an explicit ruling.

### KH-730: half-bridge detections on logic nets

**Severity:** LOW
**File:** half-bridge detection
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** tmarhguy `W6`, joewing `DBUS11` are detected as half bridges; their benches are info now (generic model).

**Fix direction / budget:** budget half-bridge records and benches.

**2026-11-17 addendum (Wave 12b, `24c87781`): partly fixed, stays open.** signal_detectors.py:3353-3359 (24c87781): the pair needs the mid node to have a label or a third part. Named pairs gone: joewing q2.kicad_sch Q1/Q2 (DBUS11) and tmarhguy main_logic Q3802/Q3803 (W6); main_logic 9->0, add_sub 19->0, gate_nand 1->0. Real ESC bridges kept: GrBLDC3 V3.3 3/3, xESC MOSFET 1/1. Corpus mid-node classes: bare 285 (removed, = the ruling's -283), label 685, other part 203, only other transistors 160. Still open: Logic gates are not all gone. When the mid node reaches another FET of the same gate (series-parallel NMOS logic), the pair still counts as a half bridge: joewing q2.kicad_sch goes 287->128, all 128 'only transistors'. Corpus: 160 such pairs (q2 147, csBlueChip CPU_HowTo 12, 0Prashant 1). Close only for the named W6/DBUS11 class. Track the transistor-only mid node as the remaining part. (harness agents at `7ed10f3e` vs `f254cb23`.)

### KH-731: DO-DET observations carry no `divider_plus_rail_name` provenance

**Severity:** LOW
**File:** DO-DET record provenance
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** only PR-DET carries the provenance, so what_if cannot tell a manufactured agreement.

**Fix direction:** carry the provenance on DO-DET observations.

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** the e1357434 refusal removes these from `simulate_subcircuits` only. **Still open** through EMC's PDN benches on LTspice / Xyce (`find` / `when` measures): the parser still takes the first `=` (`spice_simulator.py:343`), `let` is still skipped (`:304`, `:416`) and the phase unit is still not established. Same gap as KH-629.

### KH-744: op-amp library `supply_min` values look high (OPA1612, TL07x, NE5532)

**Severity:** LOW
**File:** op-amp model library (`supply_min`)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** OPA1612 9 V vs 4.5 V datasheet; TL07x vs TL07xH; NE5532. They decide S2's below-minimum warns/infos.

**Fix direction / budget:** verify against datasheets before editing; budget op-amp bench status.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 21f27d74):** fixed: TL072 / TL074 `supply_min` 7 -> 4.5 V (`spice_part_library.py:35-38`); confirmed harness-side against SLOS080W §5.3 (local datasheets/TL072-019ed851.pdf): VS min 4.5 V for all devices except NS/PS packages and TL07xM (10 V). Still open: OPA1612 `supply_min` 9 V (`spice_part_library.py:55`) against the 4.5 V the KH cites, and NE5532 8 V (`:41`) are unchanged; not scheduled in the handoff. TL082/TL084 also still carry 7 V (`:39-40`), outside the KH's list. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** NE5532 `supply_min` is too LOW (8 V in the table vs 10 V in the datasheet), not too high.

### KH-746: SPICE bench-input residue — a regulator divider holding a pot leaves no record; op-amp ground-leg filter matches refs by prefix

**Severity:** LOW
**File:** `skills/spice/scripts/` (regulator pot guard, op-amp ground-leg filter)
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff (R34 M6, M8); filed by the harness

**Symptom:** a regulator whose divider holds a pot/trimmer (pot guard) leaves no SPICE record at all; the op-amp ground-leg filter matches refs by prefix (`R1` drops an `R10…` line).

**Fix direction / budget:** report the pot case as info/skip with a reason; match refs exactly.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 21f27d74):** fixed: (b) the op-amp ground-leg move drops the input resistor's line by exact element token, not prefix (`spice_templates.py:470-471`); product test `GroundLegElementTest` (R1 vs R10). Still open: (a) is not touched by this wave: an LM317-family (three-terminal ADJ) regulator with a trimmer in its divider still breaks out before a `feedback_divider` is set (`signal_detectors.py:2141-2145`), so `generate_regulator_feedback` returns None (`spice_templates.py:1469-1471`) and `simulate_subcircuits.py:238-239` / `:304-305` write no record at all. Non-three-terminal regulators with a trimmer already get the info 'divider arm X is adjustable' (`spice_results.py:845`, since 4438e8bd). No schedule in the handoff. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

### KH-748: crystal residue — frequency misparse, no sanity range, CL omits stray capacitance, duplicated leg grouping

**Severity:** LOW
**File:** `detect_crystal_circuits`, SPICE crystal bench
**Discovered:** 2026-10-28, product 3.0.x Wave 4 Part A handoff; filed by the harness

**Symptom:** frequency misparse (`32768_1206_12.5pF` → 0.0328 Hz, `32.768` → Hz, jotego Y2 400 Hz); no sanity range; the expected CL omits the 3 pF stray; leg grouping is duplicated between the kicad and spice skills.

**Fix direction / budget:** add a sanity range (outside 1 kHz-200 MHz → warn "frequency not a crystal value"); include the stray; share the leg grouping.

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** the stray-capacitance item is not a bug.

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

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** KH-364 merged here as item (c) (fill-only zone nodes): `pcb/connectivity.py:567-592` joins a fill only to its member nodes (pads, vias, track ends, graphics); no fill-region node exists, so a fill touched by nothing else never counts. KH-364's arcs / track-track (6f99b5cb) and track-in-zone (1c71826e, f38aceb7) halves were already fixed. Carried in the C14 contact-model wave (ruling R1).

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

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** the "6 mil" item is not a bug: kicad-cli 10.0.8 loads it.

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

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** `CSENSE` also classifies as `chip_select`.

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** ecb59dbc fixes `datasheet_verify` (`datasheet_verify.py:66-100` picks the 25 °C DC entry, else the lowest: [125 °C: 4.0, 25 °C: 5.0] 4.0 -> 5.0; [pulse: 7, no condition: 6] 7 -> 6). **Still open:** the lookup detectors still read the first entry through `best()` (`lookup_detectors.py:137`, `:144`, and TJ / EX); the product's survey D says the helper covers only `datasheet_verify`.

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

### KH-808: the ruling W5-3 family match accepts a digit continuation (`LM358` → `LM3580`), and strict identity drops correct base-part datasheets

**Severity:** LOW
**File:** `skills/datasheets/distributor_core/` identity / family match (`c64acde`, `4b5f2d6`; KH-605)
**Discovered:** 2026-10-31, product 3.0.x Wave 5 handoff follow-up 19; not verified harness-side

**Symptom:** a family match for a Value-named part accepts a hit whose next character is a digit, so `LM358` can take `LM3580`'s datasheet. The W5-3 user cost: strict mode drops correct base-part datasheets when the MPN property names a base part (TPS61023 → TPS61023DRLR is now `not_found`).

**Fix direction / budget:** require a non-digit boundary after the family stem; accept an ordering-code extension of a base part named in the MPN property. Distributor-offline re-freeze if the fixture BOM carries such parts (the `sync-identity` runs).

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d` and `f254cb23`):** 166125df made `same_part('LM358','LM3580', allow_family=True)` False. The Value-name half's boundary rule also refused voltage-coded orderables the baseline accepted (TLV755 -> TLV75533PDBVR …, KH-1193), so f254cb23 reverts 166125df: `distributor_core/verify.py` is byte-identical to `6b9767e1` again and `LM358` -> `LM3580` (allow_family) is True once more. **Still open, both halves:** the strict half (`same_part('TPS61023','TPS61023DRLR')` False) and the digit-continued family case (LM358 -> LM3580 taken as a family member), which a fix must separate from TLV755 -> TLV75533PDBVR.

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

### KH-858: the two PCB point-to-segment distance helpers are not merged — they are not bit-identical

**Severity:** LOW (architecture, deferred by ruling)
**File:** `skills/kicad/scripts/pcb/geometry.py:81` vs `:576` (audit ar/R2-F4)
**Discovered:** 2026-11-01, product 3.0.x Wave 7 survey (slug KH-new-pcb-point-to-segment-dedup)

**Symptom:** the merge is fixture-neutral (`check_refactor quick` OK) but not floating-point identical: 80,477 of 200,000 random inputs differ, by up to 2.95e-10 relative (product measurement). Ruled not worth a corpus round for about −10 LOC.

**Fix direction / budget:** merge in a wave that runs a corpus gate over the families the helpers feed (board-edge / BV-001 / clearance), empty budget or a float-noise class measured with a both-direction walk.

### KH-874: bus labels are never net-name candidates, so a net reached only through a bus member takes a child-sheet name

**Severity:** LOW (net naming on bus-heavy hierarchical designs; the jotego s18 regression waived in Wave 8b)
**File:** `skills/kicad/scripts/schematic/connectivity.py:758-759` (`if idx in bus_label_idx: continue`); bus member slots `("bus", sheet, cluster, member)` at `:885-889` carry no `point_info`, so the naming loop at `:1095-1135` never ranks them
**Discovered:** 2026-11-03, product 3.0.x Wave 8b (from KH-800 follow-ups); verified harness-side at `0efc012` (code reading; the s18 numbers 331/279 → 281 are the product's measurement, not re-run)

**Symptom:** KiCad names a bus member net after the bus label's member (on the shallower sheet first). The analyzer drops bus labels from the label pass, so a net whose shallowest driver is a bus member is named by a deeper hierarchical label instead. The skip applies to bus labels on every sheet; the handoff's "root-level" is the case where it changes the winner.

**Fix direction / budget:** give each bus member slot a candidate entry (priority of the bus label's type, the bus label's sheet) so the depth/full-name tie-break sees it. Output-changing: net renames on bus designs (standard + full-chain); measure against `regression/netlist_oracle.py`. Post-3.0.

**Addendum 2026-11-15 (product v3.0.3 triage survey at `6b9767e1`):** mostly fixed by 20fb4d5e (Wave 11b-1, credited to KH-690); hierarchical labels remain.

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

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present: SacMap `--only lcsc` with no network gives `sources_available` []. Trust / evidence / count half: KH-1113.

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** 89e410a1 adds one stderr line per source that never answered, with the reason ("…_API_KEY not set" / "every request failed"). **Still open:** the JSON envelope: `sources_available` (`lifecycle_engine.py:1280`) is still built from matched data and stays `[]`, and there is no `sources_attempted` / `sources_failed` / `diagnostics` record, so a saved `lifecycle.json` cannot tell "not configured" from "failed". Product ruling 2026-11-16 (user): partly fixed; the `sources_attempted` / failed envelope record is 3.1 (tracked on the product roadmap and 3.1 seed).

### KH-900: `spice.json` `simulator` is the ngspice path with no version, beside `total_elapsed_s` — a reviewer read the elapsed time as the version

**Severity:** LOW (provenance: the simulator version is not recorded)
**File:** `skills/spice/scripts/simulate_subcircuits.py:398-400` (`5687ee1`; :385-387 at `07b7fb1`) — `report["simulator"] = find_ngspice()` (path), `report["ngspice"]` alias, no version field.
**Discovered:** 2026-11-03, SacMap rev2 soak run 10 (as KH-895); reviewer-agent claim, verified by code read at `07b7fb1` and `5687ee1`

**Fix direction / budget:** add `simulator_version` (from `ngspice --version` / the batch banner, once per run). Additive SPICE envelope key; spice-offline comparator must mask or allow it. Post-3.0.

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`): NOT fixed.** e1357434 sets `simulator` to the path of the backend that actually ran and refuses LTspice / Xyce (`simulate_subcircuits.py:428-430`); the product calls that the "path half". The filed item is that no simulator VERSION is recorded, and it remains whole: no `simulator_version` field from `ngspice --version` or the batch banner.

### KH-901: one run carries two unrelated ids — analysis folder `2026-11-03_0917` (local time) and provenance `run_id` `20261103T171710Z-581a02` (UTC) — and no output links them

**Severity:** LOW (cross-referencing a report to its envelopes; the two timestamps also differ by the UTC offset)
**File:** `skills/kicad/scripts/analysis_cache.py:226` `generate_run_folder_name` (local `%Y-%m-%d_%H%M`) vs `skills/kicad/scripts/run_id.py:44` `generate_run_id` (UTC `%Y%m%dT%H%M%SZ-<hex>`) at `5687ee1` (:287 / :40 at `07b7fb1`); the manifest does not record the `run_id`. The `5687ee1` docstrings name the distinction; outputs do not.
**Discovered:** 2026-11-03, SacMap rev2 soak run 10 (as KH-895); reviewer-agent claim, verified by code read at `07b7fb1` and `5687ee1`

**Fix direction / budget:** record the provenance `run_id` per run in the manifest (and the folder name in `capability_mode.json`), or derive one from the other. Additive manifest / envelope key. Post-3.0.

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d` with kicad-cli 10.0.8):** fixed (b6d84770, 86ef95da): (a) `"A.Type == "` -> "Could not parse expression."; (b) `${FOO}` in a condition -> "Unresolved text variable." (the PCB pipeline passes the text variables); (c) `solder_paste_rel_margin (opt -0.1)` loads; (d) `min_resolved_spokes (min 2)` -> "Unrecognized item."; (f) `0.1MM` -> "Syntax error"; (g) a tab in an expression refused. (e) `track_angle (min 45deg)` is refused by kicad-cli 10.0.8 but loads on purpose (`project.py:977-979`, test `test_track_angle_with_units_loads`): product ruling 2026-11-16 (user): KiCad 11 wins (3.0.3 reads early KiCad 11 constructs, ceiling KiCad 10), closed as by design. **Still open:** the chained-`.` condition (`A.Net.Name == 'A'`, refused by kicad-cli 10.0.8, loads here) → 12f. Related new rows: KH-1179 (unknown property / function names), KH-1180 (quoted `outer` / `inner`), KH-1181 (`${` / `@{` conditions, `(min "")`), KH-1191 (nested text variables).

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

**2026-11-17 addendum (Wave 12b handoff, `kh-filings-wave12b.md` section C):** (is_ground_name holes): A leading-minus return (`-BATT`, `-SOLAR`) is not read as ground. Two P-channel catch-diode flyback credits are lost: kaminaris GigaESC Q3 and sclmoss MiniSolarMesh Q2 (E 4-5). `0VCC` reads as ground by the same `0V…` rule that takes `0V_10V` (jericholab Q2).

**2026-11-17 addendum (Wave 12b filing `regulator-gnd-on-signal-net`, folded in by the harness):** Symptom: Envious-Data EnvOpenTorch has regulators whose GND pins sit on `THERMISTOR_B`. Since `d2-regcaps-unnamed`, a cap to that net counts as an output cap. Reach: census only, 1 repo. Evidence: `E/task-15-report.md` Fix round 1 residue. Wave: later 3.0.3. Harness check: EnvOpenTorch MainBoard mcu.kicad_sch: the net THERMISTOR_B holds U4/U5 GND pins, caps and the power:GND symbols #PWR032-035; there is no net named GND on that sheet (global label THERMISTOR_B names the ground net, as KiCad's driver priority allows). is_ground is name-only (kicad_types.py:171).

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, earth):):**
- base count of "missing decoupling on Earth": 492 records / 173 units (survey D);
- 12c adds 19 on OLIMEX ESP32-PoE-ISO (Earth), plus the primary-return family (filed new);
- `GND_NRST` / `GND_ENABLE_N` still read ground: the control-tail word set was left as surveyed; corpus has only `GND_DET` 12, `GND-detect` 8 and `GND_EN` 4, all handled.
- Earth / CHASSIS / PE / Earth_Protective and `230V_PE` → 12j.
  Harness check (`ea5f7fd1`): Full product corpus count of DO-DET 'missing decoupling on ... Earth' records: base ca59d562 487 / 168 units (claim 492 / 173; my regex is stricter), tip ea5f7fd1 435 / 171 (net -52 overall). OLIMEX ESP32-PoE-ISO units 0 -> 19 at tip (matches '12c adds 19'). is_ground_name at tip: GND_NRST True, GND_ENABLE_N True (still ground, as stated); GND_DET, GND-detect, GND_EN False (handled, as stated); Earth, 230V_PE not ground and power with a symbol (-> 12j). No contradiction with KH-925's text.

**2026-11-19 addendum (Wave 12c, stays open):** Retag 12j (the Earth family: Earth / CHASSIS / PE / Earth_Protective as ground, `230V_PE` reading 230 V). Fixed in Wave 12c (`c4c5fd11`, `8f3e9445`, `b0b85c70`, `e47817d2`, `55d4f55c`): `-BATT` / `-VBAT` ground; `0VCC` / `0VDD` supplies; `GND_EN`, `GNDDETECT`, `VSS_SW_EN`, `+12V_F19_BKGND` not ground; tokens split on `-`; `0V_24V` ground when a power symbol names it; THERMISTOR_B ground by its GND symbol. Closed by ruling (RULINGS-12c §D): escaped-slash `AUDIO{slash}VGND`, BAT- / BATT- PCB domains; `AGND_SENSE` (G2-5).
  Harness check (`ea5f7fd1`): Probe base->cand is_ground_name: -BATT/-VBAT F->T (kaminaris GigaESC AP64200/LT8609A Q3 flyback D2 back); 0VCC/0VDD T->F (jericholab 0VCC rail 0 V removed); GND_EN, GNDDETECT, /GNDDetect, VSS_SW_EN, USB_GND_EN, GROUND_FAULT, +12V_F19_BKGND, HP-VGND T->F; 0V_24V/0V_5V ground only with a power symbol; EnvOpenTorch mcu THERMISTOR_B RS-001 + 2 DO-DET gone, rail 0. Unchanged: Earth/EARTH/CHASSIS/PE/Earth_Protective not ground, power with a symbol; 230V_PE 230 V; GND_NRST/GND_ENABLE_N ground; AUDIO{slash}VGND ground (G2-4); AGND_SENSE ground (G2-5); GND_OR_5V ground (5.0 -> 0); -SOLAR not ground. **Correction to the product's remainder:** Remainder should read: open -> 12j: Earth / EARTH / CHASSIS / PE / Earth_Protective as ground (and power once a symbol names them; EMC is_emc_ground_name lacks chassis), 230V_PE reads 230 V. Open, unassigned: GND_NRST / GND_ENABLE_N read ground; GND_OR_5V (11c gate addendum, machinekoder/bb-parallel-port-cape bbb-parallel-cape.sch, jumper-selected net) still reads ground / 0 V, not mentioned by the product. Closed by ruling: AUDIO{slash}VGND (G2-4), AGND_SENSE (G2-5, add to the list), BAT-/BATT- PCB domains. -SOLAR: the ruling's premise 'no corpus net' is wrong: sclmoss/MiniSolarMesh and aresta/MiniSolarMesh MiniSolarMesh.kicad_sch carry -SOLAR (3 power:GND2 symbols valued -SOLAR, D2 Schottky anode, Q3 S, 5 caps); Q2 AO3401 has_flyback_diode False both sides (the 12b addendum's lost credit). Either re-rule or keep -SOLAR open (2 units).

**2026-11-19 addendum (Wave 12c filing `fhgnd-ground-name`, `kh-filings-wave12c.md` B item 35, folded in by the harness as a duplicate):** Symptom: brainmachine `FHGND` is a signal (Arduino D6 → ULN2002A I5, global label) but reads ground by the `*GND` suffix rule (since before `ca59d562`). Candidate rule: a `*GND` name whose net carries only signal pins and no ground pin. Evidence: `X/task-10-report.md` concern 1.
  Harness check (`ea5f7fd1`): is_ground_name('FHGND') True at base and tip; brainmachine FHGND = D39 K, A1 D6 bidirectional, R58, U14 I5 input, global label. KH-925 is the open is_ground_name umbrella (stays open, 12j) and already has the 11c addendum 'control and sense signals read as ground' and the R4 ruling on *GND names. Addendum to KH-925: a *GND-suffixed signal (brainmachine FHGND: Arduino D6 -> ULN2002A I5) reads ground by the suffix rule; candidate rule: a *GND name whose net carries only signal pins and no ground pin.

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

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present: SW-003 builds a buck input loop on the TPS61023 boost. Lines moved: `pcb/assembly.py:842-845` (skip list has no boost), `:849-874`; `kicad_core/hotloop.py:50-57` unchanged.

### KH-933: ES-001 gives ESD-path wording to surge TVS parts on power inputs

**Severity:** LOW (finding text; ES-001 on surge parts)
**File:** `skills/emc/scripts/emc_rules.py:3234` (`diode`-typed TVS accepted, 9c T3), `:3256-3277` (ES-001 text: "8kV ESD strike", "dI/dt = 37.5 GA/s" for every part), at `8c42799`
**Discovered:** 2026-11-04, product 3.0.x Waves 9b + 9c handoff (`L9C/task-3-5-report.md` :10-13; `L9C/progress.md` Task 3)

**Symptom:** 36 of the 100 added ES rows are SMAJ / SMBJ surge TVS parts on power inputs (SMAJ58CA on OpenEFI, SMBJ16CA/26CA on 12 V, SMAJ24A on +24V). They get the connector-ESD distance and overshoot wording, which is not the part's job there.

**Fix direction / budget:** recognise surge TVS on a power input (series / package family, clamp net a rail) and either skip ES-001 or word it for surge. Output-changing: ES-001 count / text and EMC score on those boards.

**2026-11-17 addendum (Wave 12b filing `es001-rail-clamp`, folded in by the harness):** Symptom: ES-001 judges a TVS on a supply rail by its distance to the nearest connector. Task 9's one TVS recogniser widens the reach: 15 of 51 ES-001 adds on 299 units sit on rail-named nets (Vdd_in_fuse ×2, +5V, −5V, BAT+ ×2, +12V, +3V3 ×6 BSD5C031V, VBAT, 12V_MR). Reach: corpus E 22-26. Evidence: `E/task-9-report.md`, `D/surveys/survey-F.md` F-P5. Wave: 12g. Harness check (`7ed10f3e`): ES-001 (emc_rules.py:3240-3295 at 7ed10f3) takes every protection type incl. 'diode' and judges distance to the nearest connector with no clamp-net / rail test, the same site and fix as KH-933 (key on the clamp net being a rail). Task 9's recogniser widens it: task-9 report :55 lists 15 rail-net adds incl. +3V3 x6 BSD5C031V (an ESD diode, not a surge part). Same defect as KH-933, wider reach: KH-933's 'surge TVS (SMAJ/SMBJ)' scope should become 'any TVS whose clamp net is a supply rail'.

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

**2026-11-19 addendum (Wave 12c, `af470804 + 4b66cc85 + f4972020`): partly fixed, stays open.** harness agents at `ea5f7fd1` vs `ca59d562`: Fixed: ctx.is_ground excludes vss_supply_rails (kicad_types.py:246-250); EN-site name guards gone (system_analyses.py / domain_detectors.py no longer import is_vss_name; base :1695 / :5385); config override < 0 now marks VSS a supply (kicad_types.py:365-367). Corpus skumlos/bkm-129x bkm-129x.sch VSSA rail absent->-5.0, DC-DET/DO-DET 'Decoupling on VSSA' added, PR-DET Vout 5.0->-5.0. loxodes/vna bias_controller power sub-sheet U601 EN 'floating' both sides. **Still open:** Still open (11c addendum, last bullet; no ruling in RULINGS-12c): a negative power symbol on a VSS net is not used as negative-voltage evidence (product: no corpus case). Either a ruling or keep that line open. Side note on the filed unit: loxodes/vna bias_controller root sheet gains a new VM-001 error 'Net VSS_SW_EN: 6.0V / 3.3V domain crossing' (U601 -6 V LDO EN read as a +6.0 V domain) now that VSS_SW_EN is no longer ground; that is a VM-001 sign/domain issue, not this KH.

### KH-968: keepouts / rule areas inside a library footprint are never read — KO-001 and the antenna checks see only board-level zones

**Severity:** MEDIUM (false negative that turns into wrong advice: two earlier soak reviews told the user to add an ESP32 antenna keepout that the module footprint already carries)
**File:** `skills/kicad/scripts/pcb/reader.py:1261` (`extract_zones`: `find_all(root, "zone")`, direct children of the board only; `kicad_core/sexp.py:227` `find_all` is not recursive) and `:1432` (`_extract_keepout_zones` filters that list); `pcb/assembly.py:1216` (`analyze_keepout_violations` gets nothing else), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** the ESP32-S3-WROOM-1 footprint defines its antenna keepout as a footprint zone on both copper layers; KiCad DRC enforces it (0 violations), while the analyzer reports no keepout near the module. No other `"zone"` reader exists in the PCB analyzer.

**Fix direction / budget:** read `(zone …)` children of each `(footprint …)`, transform the outline by the footprint position, rotation and side (flip the layer set for back-side parts), tag the entry with the owning reference, and feed KO-001 and the antenna / RF checks. Output-changing: new `keepout_zones` entries and KO-001 findings on boards whose footprints carry rule areas (measure the corpus count first). v3.0.2 or later. Belongs with KH-972.

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present (ESP32-S3-WROOM antenna rule area unread). Lines moved: `pcb/reader.py:1289` (`find_all(root, "zone")`), `kicad_core/sexp.py:263-270`, `_extract_keepout_zones` `pcb/reader.py:1469`, `analyze_keepout_violations` `pcb/assembly.py:1258`.

### KH-969: GP-001 skips a net once its coverage is ≥ 95 %, so only some of the nets crossing one gap are reported, and the finding gives no gap location

**Severity:** LOW (incomplete and hard-to-act-on finding)
**File:** `skills/emc/scripts/emc_rules.py:509` (`elif coverage < 95` … `else: continue`) and `:516` (finding fields: `signal_net`, `coverage_pct`, `trace_mm`, no coordinates), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** five nets cross the same unpoured patch under U1; GP-001 reports three. By code read the threshold is per net and by percentage, so a net with long routing elsewhere passes 95 % with the same crossing (the soak's "unexplained" two). The finding names no gap, so the user cannot tell that the three findings are one void.

**Fix direction / budget:** add the gap location (x, y, layer, and the uncovered length) to the finding, and group the nets that cross the same gap (or add a per-gap finding listing every crossing net). Output-changing (GP-001 fields; GP-001 count if grouping changes the threshold). v3.0.2 or later.

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present: GP-001 reports 3 of 5 nets, no gap coordinates. Lines moved: `emc/scripts/emc_rules.py:513-517` (`elif coverage < 95:` ... `else: continue`), finding at `:519-537`.

### KH-971: XV-004 skips a part whose MPN is blank on either side and never compares distributor part numbers

**Severity:** LOW (the parity check is silent on the cases most likely to be wrong at assembly)
**File:** `skills/kicad/scripts/cross_analysis.py:670` (`if not sch_mpn or not pcb_mpn: continue` in `check_mpn_parity`, :656), at `7d9d4d9f`
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** on SacMap 14 footprints have no MPN; they are skipped without a count or a finding. F1's PCB DigiKey PN `F2084CT-ND` does not resolve, and distributor PNs are not compared between schematic and PCB at all. (XV-004 itself works: it caught Q1–Q3 BSS138 vs BSS138LT1G, the KH-426 case.)

**Fix direction / budget:** report as their own sub-cases (a) MPN blank on the PCB but set on the symbol (or the reverse), (b) distributor PN differs between symbol and footprint; keep (c) the both-set mismatch as today. Resolving a PN online belongs to the BOM / lifecycle tools, not here. Output-changing (new XV-004 sub-case findings on corpus boards with blank footprint MPNs; measure first). v3.0.2 or later.

**Addendum 2026-11-08 (v3.0.2 Wave 11b-2, candidate `6138b126`, partly fixed by 1f31409f):** fixed: `cross_analysis.py:757`, `:772-773` count pairs with a blank MPN on either side; `main` prints `XV-004: N paired part(s) not compared ...` to stderr (`:1443`); SKILL.md:242 says XV-004 compares where both sides carry one. Still open: Sub-case (a) is only a stderr line; there is no JSON count or finding (the JSON field is scheduled for 3.1, ruling F1 P5). Sub-case (b), comparing distributor part numbers between symbol and footprint, is not done and is not scheduled anywhere: `check_mpn_parity` (`cross_analysis.py:740-776`) compares MPN only. The fixed half is gated in the Wave 11b-2 gate (results/v302_w11b2_gate*).

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present at v3.0.2: XV-004 skipped 35 parts on SacMap (run 11: 14), reported on stderr only; the `checks_run` entry has no `skipped` field (`cross_analysis.py:739-762`, `:1435-1450`).

### KH-972: silent capability loss is not listed in `diagnostics[]` — a distrusted extraction, an unread footprint keepout, a part skipped by a check

**Severity:** LOW (umbrella; report trust: the soak meta report's top trust item)
**File:** several producers at `7d9d4d9f`: `datasheet_types/cache_reader.py` (`lookup` marks `pdf_missing` with no record), `pcb/reader.py` (KH-968), `cross_analysis.py:670` (KH-971 skips), lifecycle (KH-896 / KH-474)
**Discovered:** 2026-11-06, SacMap rev2 soak run 11 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/11/`, v3.0.1 release `7d9d4d9f`, post-release; design files byte-identical to run 10); verified by code read at `7d9d4d9f`

**Symptom:** each loss above changes what the review can claim, but nothing in the output says it happened; the reviewer reads "no finding" as "checked and fine".

**Fix direction / budget:** one diagnostic per lost capability (code, affected refs / MPNs, reason), emitted where the loss happens. Group the fixes: KH-433 + KH-905 (extraction distrust), KH-968 (footprint keepouts), KH-971 (skipped parts), KH-896 / KH-474 (lifecycle sources). Additive `diagnostics` entries; corpus effect depends on the member fixes. v3.0.2 or later.

**Addendum 2026-11-13 (v3.0.2 Wave 11c, verified at `db551674`):** KO-001 now skips a footprint with no readable courtyard on the side the area covers (ruling K-R1, as KiCad does), and leaves nothing in `diagnostics[]` for it (`pcb/assembly.py:1229-1247`). Same silent-capability class.

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** the cross_verify half is fixed (95d9891c; the DA-001 IC half came earlier in 92c7e36b): excluded-from-board parts are no longer "missing", DNP is compared with the footprint `dnp` attribute (KiCad 8+ board files), unfitted caps are skipped in its decoupling check (missing `['R5']` -> `[]`; two "DNP but placed" warnings -> none). **Still open:** `cross_analysis.py:479` counts DNP caps in DA-001 (`caps = rail.get('capacitors')`, no DNP filter) → 12g (product: 37 units / +38 DA-001).

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

**2026-11-17 addendum (Wave 12b Track H, survey-H; ruled RULINGS-12b section 4):** signed-integer KiCad 10 net names (`+12`, `-12`, `+5`, `0`) are taken as net ids. Corpus: 5 boards / 2 repos, e.g. cristobalcuevas HornSystem MainBoard; the upgrade lane adds 11 horychen boards. Harness check: KH-590 open (numeric-only KiCad 10 net names). pcb/reader.py:286-289 int(val) accepts '+12'/'-12'; lstrip('-').isdigit() at :855/:878/:1084/:1202/:1413. cristobalcuevas MainBoard.kicad_pcb: 54 '+5' and 10 '+5V' segments; baseline net_name_to_id {+5: 3, +5V: 5}, connectivity '+5' 47 islands.

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

**2026-11-17 addendum (Wave 12b, `71e3dd6b`): partly fixed, stays open.** signal_detectors.py:3597-3626 (71e3dd6b). D-S diodes are now orientation-checked and skip zener/TVS; P-channel credit needs ground->drain. Run: Charading Saturn60 Q1 AO3401A, reversed D2 to PWR_IN, goes from True to False. _diode_terminal_nets is unchanged: it returns None unless the pins are named A/K, and then credit is still orientation-blind (declared in the task-25 report). Still open: The addendum's third open item is not fixed: unnamed-pin, builtin or snapped diodes are still credited in either orientation. 124 of 1,283 corpus flyback credits (56 units) use a diode without A+K pin names, e.g. joseluizmendonca ph_driver D7/D13/D17 named A/C (a 'C' cathode is not read) and esynr3z nixie-ps D2 with blank names. Keep it open for that part. (harness agents at `7ed10f3e` vs `f254cb23`.)

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

### KH-1164: `is_real_mpn` passes generic values (`4k7`, `100nF 50V`, `SOT-23`, `MH1`, `Conn_01x02`)

**Severity:** LOW
**File:** `skills/datasheets/distributor_core/inputs.py:17-44`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (is_real_mpn) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `is_real_mpn` passes `4k7`, `2k2`, `100nF 50V`, `4.7uF 0805`, `10K 1%`, `1uF/16V`, `100nF X7R`, `SOT-23`, `MH1`, `Conn_01x02` (the regex covers only a bare value+unit). Since Wave 5 (KH-488) generic symbol names are searched by providers that lack their own part number.
**Fix direction:** tighten; a distributor-oracle re-freeze (size against `tools/tests/fixtures/distributor/` first).

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** 5ba4bceb rejects `4k7`, `2k2`, `100nF 50V`, `4.7uF 0805`, `10K 1%`, `1uF/16V`, `100nF X7R` in `inputs.is_real_mpn`. **Still open:** `SOT-23`, `MH1`, `Conn_01x02` still pass: product ruling 2026-11-16 (user): stays open as a real bug; RULINGS-v3.0.3 keep 3.0.3 to value-combination patterns with no symbol-name tightening (KH-488 conflict). The twin `lifecycle_engine._is_real_mpn` is unchanged, so all of the values above still pass in the lifecycle audit: one predicate, fixed together under this entry.

### KH-1165: `--spice-enhanced` without a simulator only warns on stderr

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 1) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `--spice-enhanced` without a simulator only warns on stderr (maintainer's list, not checked harness-side).

### KH-1166: the run manifest `scripts` entry keeps only the last analyzer

**Severity:** LOW
**File:** `skills/kicad/scripts/analysis_cache.py:747`, `:810-862`; `output_io.py:72-77`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 2) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `create_run` stores only this call's `{analyzer: entry}` and does not merge the previous run's scripts (it merges `outputs` and `source_hashes`); `overwrite_current` and `write_derived_output` never touch `scripts`. SacMap's manifest lists only the schematic analyzer.
**Status at `6b9767e1`:** confirmed 2026-11-15 by code read at `365aea94` (soak runs 12 + 13).

### KH-1167: `--add-distributor` silently drops unknown names

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 3) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `--add-distributor` silently drops unknown names (maintainer's list).

### KH-1168: LCSC order quantities

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 4) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** LCSC order quantities (maintainer's list; no detail recorded).

### KH-1169: `verify.py` error coverage

**Severity:** LOW (unverified rider)
**File:** `skills/datasheets/distributor_core/verify.py`
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 5) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `verify.py` error coverage (maintainer's list; no detail recorded).

### KH-1170: `format-report --severity` is loose

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 6) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `format-report --severity` is loose (maintainer's list).

### KH-1171: `detect_project.sh` zero-file exit

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 7) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `detect_project.sh` exit status when it finds zero files (maintainer's list).

### KH-1172: `_smoke_v14_roundtrip --help`

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 8) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** `_smoke_v14_roundtrip --help` (maintainer's list; no detail recorded).

### KH-1173: sub-sheet redirect provenance

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 9) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** provenance of a sub-sheet redirect (maintainer's list; no detail recorded).

### KH-1174: the `datasheet_verify` flag message

**Severity:** LOW (unverified rider)
**File:** see the item
**Discovered:** 2026-10-24, v3 round-9b handoff §7 items 11/16 (review B); split from KH-495 item (rider 10) on 2026-11-15 (tracker edit approved by the user 2026-11-15; product v3.0.3 survey at `6b9767e1`)
**Symptom:** the `datasheet_verify` flag message (maintainer's list; no detail recorded).

### KH-1175: a `V<number>` rail name with a rail word glued on (`V12PWR`, `V5SYS`, `V3LDO`, `V5MAIN`, `V5BUS`, `V12CORE`) reads as a signal by name

**Severity:** LOW (generalization gap; corpus reach measured 0 for the named words)
**File:** `skills/kicad/scripts/kicad_core/netnames.py:108-151` (`_V_NUMBER_RAIL_WORDS = {V, REG, SW, USB, BAT, SB, AUX}`, `_V_NUMBER_VOLTAGE_SUFFIXES`, `_is_v_number_rail`), reached from `is_power_net_name` `:221`
**Discovered:** 2026-11-16, maintainer question on the v3.0.2 release notes' `V24.RX` example; measured by the product agent at `6b9767e1` (v3.0.2 code) over the regen-2 outputs
**Symptom:** since v3.0.2, a word glued directly onto `V<number>` makes the name a rail only when the word is on a short list. `is_power_net_name` returns False for `V12PWR`, `V5SYS`, `V3LDO`, `V5MAIN`, `V5BUS`, `V12CORE`, `V33LDO`, `V12PDC`, `V5N` (single digit + `N`), while the separated forms (`V5_MAIN`, `V5_SYS`, `V12_PWR`) and `V5REG` / `V33IO` read as rails. A net a power symbol names is unaffected (the `power_rails` set wins); the miss is on rails built from plain labels, and on name-only callers. Effect: fewer rail-source, decoupling and trace-width checks on such a rail (missed checks, not false findings).
**Measured reach** (regen-2 schematic outputs, 39,146 files, mtime >= 2026-11-13; grep of the pcb and emc outputs for the words):
- 370 unique (repo, net) `V<number><letters…>` names read as signals, in 25 repos; almost all are channel or electrode names and correctly signals (`V1COL0`, `V1PAL1`, `V1FREQ1`, `V1AMP1`, `V1ANODE` / `V1GRID` / `V1CATHODE`, `V1OUT`, `V10FB`).
- Glued `PWR|POWER|SYS|MAIN|BUS|LDO|CORE|SUPPLY|RAIL|PLUS`: **0 nets** in schematic, pcb or emc outputs (`V33LDO` / `V12CORE` occur only as IC pin names in `SdtElectronics/crispy`).
- Nets with power evidence that read as signals by name: `jdbrinton/uberclock` `V5N` (7 power_in pins, 4 caps; a power symbol names it, so rail through the set), `jonathan-tooley/903` `V1H+`…`V8H-` (16 valve-heater nets named after the tube refs, 1-2 power_in pins each; arguably not rails), `Tecnologic/unimoc_jacobi` `/logic/controller/analog/V12PDC` (3 pins, 1 cap; unclear).
**Fix direction / budget:** add the common rail words (`PWR`, `POWER`, `SYS`, `MAIN`, `BUS`, `LDO`, `CORE`, `SUPPLY`, `RAIL`) to `_V_NUMBER_RAIL_WORDS`, with unit tests for each and over-reach guards for the channel names above. Measured corpus reach 0 → output-neutral (verify with the same scan at the fix commit). `V5N` / `V12PDC` / the valve-heater nets are a separate call (they would move corpus output); leave them out of the neutral fix.

### KH-494: core minors from the review-period bug hunt (review A) — NaN/non-numeric coordinates traceback, `--no-hierarchy` still merges top-level sheets, `--text` drops `--output`, no PCB duplicate-reference check, and eight unverified items

**Severity:** LOW
**File:** `skills/kicad/scripts/schematic/connectivity.py:323` (`(at nan 100.33 0)` on a placed symbol → `ValueError: cannot convert float NaN to integer`, traceback exit 1; `(at abc …)` → `kicad_core/sexp.py:195` `could not convert string to float`; no guard around `get_at` / `get_xy` in `schematic/reader.py:471-621` or `pcb/reader.py:52-374`); `schematic/pipeline.py:1281` (`merge_top_level_sheets` runs unconditionally — `hierarchy.py:197-198` says so by design — while `analyze_schematic.py:33` `--no-hierarchy` help says "treat file as standalone root"); `analyze_schematic.py:114-117` / `analyze_pcb.py:140-143` (`--text` prints and returns before the `--output` / `--analysis-dir` branches, no warning; EMC has the opposite precedence at `analyze_emc.py:628-640`); `pcb/*.py` (no duplicate-reference audit; the schematic has one at `schematic/audits.py:29`)
**Discovered:** 2026-10-24, v3 round-9b handoff §7 item 15 (review A minors); the four named items verified at `07b7fb1` (the NaN and `abc` cases by running the analyzer on an edited fixture)

**Unverified riders (maintainer's list):** datasheet index shape crashes; silent datasheet-manifest and sym-lib-table failures; missing `lib_symbols` gives no diagnostic; `--project-root` traceback; the `--stage` wording; zip-only gerber dirs; invalid numeric args accepted; thermal/cross exit-code mismatch.

**Fix direction / budget:** coordinate guards, `--text`+`--output` precedence and the unverified riders are neutral (malformed input / CLI only). The `--no-hierarchy` item is a `--help` text change (text oracle) if the doc is fixed, or neutral for the corpus if the behaviour is (the harness never passes the flag outside the standard profile, where it is on for every unit — a behaviour change there WOULD move sub-sheet-redirect units: size before choosing). A PCB duplicate-reference check is a **new finding** = corpus-output class on every board with duplicate footprint refs (size with a corpus scan of `footprints[].reference`).

#### Addendum to KH-494 (core minors, review A)
**Added:** 2026-10-25, external audit round 1 (`docs/audit/02-v3-kicad-code/findings/VERIFICATION.md` part a, Empirical: "R1: diagnostics newline")
`skills/kicad/scripts/kicad_core/diagnostics.py:31`, `:38`: the stderr `Warning:` line embeds `str(exc)[:200]` unescaped, so an exception message containing a newline breaks the one-line-per-diagnostic stderr contract. Escape or replace newlines. Neutral for the envelope, stderr only.

**Addendum 2026-11-16 (v3.0.3 Wave 12a, verified at `08879e2d`):** items 1-3 and the newline addendum are fixed (a250cbcf, f4ba9047, 3fc871da): `(at nan …)` / `(at abc …)` / `(at inf …)` (schematic) and nan / abc (PCB) go from a traceback to rc 0 with an "invalid coordinate" diagnostic; the `--no-hierarchy` help matches the behaviour (text oracle `help__analyze_schematic`, declared); `--text --output` writes both outputs on sch and pcb; `diagnostics.record` escapes `\r` / `\n`. **Still open:** the PCB duplicate-reference check and the unverified riders. The rest of item 1 (`(width nan)`, `1e400` / `1.2.3` point tokens) is KH-1183.

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a handoff):** product ruling: roadmap (3.1). The `suppressed` / `suppression_reason` keys are in no envelope schema; the `config-reference.md:67` sentence and two stale comments go to 12k.

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

**2026-11-17 addendum (Wave 12b handoff, `kh-filings-wave12b.md` section C):** (unannotated duplicate references): unnumbered duplicates without `?` (27 caps all `PC`, msinger wideboy) merge pins and give a false SP-001 "both pins on one net". SP-001 skips only `?`. A digit-less guard would also drop doflagie `C_E`.

**2026-11-19 addendum (Wave 12c handoff, `kh-filings-wave12c.md` section C, :):**
- dewayne57/GPSDO `Hardware_power.kicad_sch`: LM7912, LM2596T-12 and LM2596T-5, all `U?`, collapse into one PR-DET record carrying the LM2596T-5 Value and the LM2596T-12 output net. It now reads 5.0 on `Reg_Pos_12_Out` (the name has no `V`, so the name rule gives nothing). 1 record, declared.
- chatelao R301 and jonaheinke C19 RC-DET name an unfitted ref because a fitted part shares the ref.
- An unannotated `C?` shared by several caps passes the two-pin guard through the merged `ref_pins` (GMMan; true there).
  Harness check (`ea5f7fd1`): Tip dewayne57/GPSDO Hardware_power.kicad_sch: components U? LM7912, U? LM2596T-12, U? LM2596T-5; one PR-DET record U? value LM2596T-5, output_rail Reg_Pos_12_Out, estimated_vout 5.0; rail_voltages Reg_Pos_12_Out 5.0 (the root GPSDO sheet reads U203 12.0). chatelao xDuinoRail-Debug RC-DET with C301/R301 where R301 is DNP by ref (my DNP scan). jonaheinke / GMMan not checked.

**2026-11-19 addendum (Wave 12c filing `standalone-duplicate-refs`, `kh-filings-wave12c.md` B item 27, folded in by the harness as a duplicate):** Symptom: a sheet read alone pools parts that share a reference, from a repeated sheet's instances or from two symbols annotated alike: BlaatSchaapCode/party_hat_kicad `power.kicad_sch` (two U1: TPS7A05, LTC4054) gives the new PWR rail a PR-DET and a DO-DET carrying the LTC4054 Value / 4.2 V (2 records, declared); 11 sub-sheets read CC status fail on duplicate or unannotated refs: mSCKee, Brytec ×3, lil-flight, FrameworkDock ×2, Ricardo, ESP32_A7670, spork-8 ×2; duplicated R refs pool their pins in PP-001 (33 removals, outcome right); GenerateNU/Concrete FufuPot U8: two symbols annotated C17 merge 4 nodes (1 "missing decoupling" possibly lost); easy-smart `poe.kicad_sch`: duplicate C1 / C133 make the decoupling bench fail with "device already exists" (KH-1051, both sides). Related: KH-483 (unannotated `U?`), the survey-H S5 sentence (a standalone sub-sheet takes its first listed instance's reference). Evidence: `D/reviews/task-6-review.md`, `task-14-review.md`, `task-24-review.md`, `task-20-review.md`; `X/task-18-report.md` concern 3.
  Harness check (`ea5f7fd1`): party_hat_kicad power.kicad_sch: two U1 ('LDO 3V3', 'LTC4054ES5-4.2'); tip adds PR-DET U1 LTC4054ES5-4.2 output_rail +3V3 est 4.2 V plus DO-DET twins (none at base). Root cause is KH-483's: comp_lookup keyed by reference, last wins (kicad_types.py); KH-483's 12b addendum already covers unnumbered duplicates (PC caps), so annotated duplicates are the same mechanism. Fold into KH-483 as an addendum and widen its title to 'duplicate references (unannotated, unnumbered or annotated alike) collapse in the detector context'. Keep the examples (party_hat U1, 11 CC-status sub-sheets, PP-001 pooled R pins, FufuPot C17, easy-smart poe C1/C133 with the KH-1051 note).

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

**2026-11-17 addendum (Wave 12b handoff, `kh-filings-wave12b.md` section C):** (stays 3.1): STPMIC1 (joeperri95 ×2) now carries `sw_net` from VLX1 while `output_rail` comes from VOUT4.

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

**Addendum 2026-11-15 (SacMap rev2 soak runs 12 + 13, v3.0.2 `2c645996`, code read at `365aea94`):** still present. A second SacMap part: U3 TPS61023 (SOT-563) reads package unknown, 150 °C/W default, although a cached extraction exists (`analyze_thermal.py:422-436`, `:131-147`: package and RθJA come from the footprint library string only). The `**File:**` line above should read `skills/kicad/scripts/analyze_thermal.py`. Tj max half: KH-1042.

### KH-431: `lifecycle_audit` findings carry no `finding_id` (40/40) and the script has no `--analysis-dir`; not in the analysis manifest (LC-007 still emitted by the schematic analyzer)

**Severity:** LOW-MEDIUM (Layer 2 merge keys on `finding_id`; lifecycle is the one analyzer outside the manifest/cache contract)
**File:** `skills/kicad/scripts/lifecycle_audit.py`
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** every lifecycle finding on the soak board lacks `finding_id`; the script cannot write into `analysis/`; `analysis_manifest` has no lifecycle entry while `analyze_schematic` still emits LC-007 itself.

**Fix direction:** route findings through `finding_schema.assign_finding_ids('lifecycle', …)`, add `--analysis-dir` + manifest registration like the other analyzers, and decide the LC-007 ownership (one emitter).

**Gate budget (when fixed):** additive `finding_id` on every lifecycle finding; LC-007 single-source.

**Rider (2026-10-22, soak run 9):** the manifest's `outputs` also never lists `drc.json`, `erc.json`, `parasitics.json` or `fab_release_gate.json` written into the run folder, and `LC-007` "Lifecycle audit not run — --lifecycle flag not passed" remains in `schematic.json` after the standalone `lifecycle_audit.py` wrote `<run>/lifecycle.json`. Same fix family: register side outputs; drop LC-007 when `lifecycle.json` exists for the current run.

### KH-434: PD-001 is silent when evaluated with no peaks — no `checks_run`-style line in `category_summary`

**Severity:** LOW (observability: a board with zero PDN peaks is indistinguishable from a board where the PDN check did not run)
**File:** `skills/emc/scripts/emc_rules.py` (PD-001 / `category_summary`)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap's EMC output has no PDN entry at all; nothing says the check ran and found 0 peaks.

**Fix direction:** emit a `category_summary.pdn` (or `checks_run`) record with `peaks_total: 0` when the check runs and finds nothing, matching the `checks_run` convention in cross_analysis.

**Gate budget (when fixed):** additive `category_summary` entry on every EMC unit with a PDN evaluation.

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

**2026-11-19 addendum (Wave 12c, stays open):** Items (1), (3), (5) fixed in Wave 12c (`8d4e9ea4`, `46347a19`, `607a261c`); items (2) and (4) → 3.1 (B-7).
  Harness check (`ea5f7fd1`): (1) system_analyses.py:727-735: an always-on regulator with an EN pin now reads 'estimated Iq (always-on, EN not switched)'. (3) _battery_value_voltage :270: 2xAA 3.0 V, 3xAA 4.5, AAA 1.5, 18650 3.7, CR2032 3.0, 2S 7.4, 9V 9.0; 'BATT' gives None, so the 3.7 V default applies. (5) addendum :566 / :709-719: an LED is hardwired only if its far side is ground and neither the LED nor its resistor is DNP / off-board; only non-hardwired LEDs get realistic 0. Items (2) Iq from extraction and (4) MCU deep-sleep go to 3.1 by RULINGS-12c D (B-7 / as planned).

**2026-11-19 addendum (Wave 12c filing `sleep-audit-en-reading`, `kh-filings-wave12c.md` B item 38, folded in by the harness as a duplicate):** Symptom: the sleep audit's EN-pin list (`EN, ENABLE, ON/OFF, ON, SHDN, CE`) is narrower than sequencing's (`~{EN}`, `~{SHDN}`, `EN<n>`, `CHIP_ENABLE`): 97 `regulator_iq` entries read "can be disabled via EN" beside "always-on, no EN pin detected" (136 at base). A regulator whose EN is tied to ground keeps sleep `likely_state` "always-on" (42 notes). An EN tied straight to a non-power-named VIN stays controlled (`supply_nets` could serve it). Evidence: `X/task-27-report.md` concerns 2-3; ledger Task 27.
  Harness check (`ea5f7fd1`): Count over D/corpus-tip-ea5f7fd: 109 regulator_iq entries have has_enable_pin False, note 'estimated Iq (always-on, no EN pin detected)' and likely_state 'can be disabled via EN' with realistic_uA 0.0 (e.g. LT3467A U801, U1401). That is KH-439 item (1)'s symptom (contradictory EN note vs always-on), which fixes-wave12c row 27/28 marks fixed by 8d4e9ea4. File as a KH-439 addendum and treat KH-439 item (1) as partial: 109 regulator_iq entries (not 97) at ea5f7fd1 still pair 'always-on, no EN pin detected' with 'can be disabled via EN' because the sleep EN list (EN, ENABLE, ON/OFF, ON, SHDN, CE) is narrower than sequencing's (~{EN}, ~{SHDN}, EN<n>, CHIP_ENABLE); plus the EN-tied-to-ground (42 notes) and EN-tied-to-non-power-VIN cases.

## Test Harness Issues

### TH-122: BUGFIX-KH-307-02 / -03 anchor lost — the bluepylons Thinkpad keyboard U8 TS-003 / TS-004 findings are gone at Wave 12c

**Severity:** LOW (regression guard for a fixed evidence-source bug; same shape as TH-047 / TH-056)
**File:** `regression/bugfix_registry.json` (KH-307 entry); `reference/bluepylons/A-Thinkpad-USB-keyboard/PCB_Thinkpad-USB-keyboard-PCB/assertions/thermal/Thinkpad-USB-keyboard-PCB_thermal_bugfix.json`
**Discovered:** 2026-11-19, v3.0.3 Wave 12c gate lock preview (`results/v303_w12c_gate_aux/lock_preview_thermal.json`)
**Symptom:** BUGFIX-KH-307-02 (TS-004 `evidence_source` = `geometry`) and BUGFIX-KH-307-03 (TS-003 `evidence_source` = `heuristic_rule`) pass at `ca59d562` and fail at `ea5f7fd1`: the unit's only TS-003 / TS-004 (U8) are gone because thermal now takes the regulator load from the power budget (Wave 12c `125b0a02` / `c336e6a5`, class `b4-thermal`). The KH-307 fix itself is not regressed; the locks have nothing to match. Not declared in the 12c handoff.
**Fix:** at the v3.0.3 regen, re-anchor both locks on a corpus thermal unit that still carries TS-003 / TS-004 at the regen tip (registry entry + assertion file), as for KH-198 (TH-047); retire the pair if no unit shows the KH-307 behaviour (product ruling, 12c acceptance 2026-11-19).

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

**Addendum 2026-11-16 (v3.0.3 Wave 12a handoff):** the product's rf_chains shape test landed in the range; the `summary.categories_checked` half moves to 12g with KH-434. Stays open for the harness-side KH-313 re-anchor on a contract fixture.

### TH-118: `add_repos.py` pre-add is not atomic — a second entry whose URL has two pinned lines in repos.md aborts the run after earlier rows were already written

**Severity:** LOW (operator recovery by hand; no corpus data lost)
**File:** `tools/add_repos.py` (`append_to_repos_md` raises at :139-140; phase 1 pre-add loop :383-404); `repos.md`
**Discovered:** 2026-11-16, corpus batch 2 (50 KiCad 9 → 10 upgrade pairs)

**Symptom:** phase 1 writes each candidate into repos.md one at a time. A second entry
(`- URL @ sha (as owner/repo@sha7)`) needs exactly one pinned line for its URL; for
emertcakir/OpenAirScope repos.md has two identical pinned lines (324 / 328), so the
21st pair raised `ValueError: ... expected one pinned entry ... found 2` with 20 pairs
already pre-added and no pipeline run for them. Re-running then skips nothing and
re-inserts, so recovery meant deleting the 20 `(as …)` lines by hand and replacing the pair.

**Data half:** 13 URLs carry a duplicated pinned line in repos.md (20 at the 2026-04-06
expansion `c793abfdb03`), e.g. mikelawrence/RPi-pHat-Thermocouple, red-scorp/RP2040-DebugProbe,
alicjamusial/meteo-station-pcb, JordanAceto/micro_ox, radioelf/OpenPlc.

**Fix direction:** validate every candidate's insertion point before phase 1 writes
anything (or treat identical duplicate pinned lines as one); make the pre-add idempotent
on rerun; drop the 13 duplicate lines from repos.md.

### TH-119: batch runners sharing one output root race on the `units.jsonl` rotation — `add_repos.py --jobs N` loses a stage

**Severity:** LOW (rare; the stage fails loudly and re-runs clean)
**File:** `harnesslib/batch.py:212-214` (`exists()` then `os.replace(out_root / UNITS_NAME, ...)`); `tools/add_repos.py` phase 2 (8 parallel repos, each running every runner on the shared `results/outputs/<type>/`)
**Discovered:** 2026-11-16, corpus batch 2 (22 KiCad 11-dev repos)

**Symptom:** two concurrent runners on the same output root both see a prior manifest
with a different run_id and both rotate `units.jsonl`; the second `os.replace` raises
`FileNotFoundError: .../results/outputs/schematic/units.jsonl -> .../units.<uuid>.jsonl`
and the stage fails (lk-ek/esphome-unni-co2-sniffer schematic, TheJoboReal/self_watering_pot
spice). Re-running the remaining stages per repo recovered both (checks 100 %). 0 hits in
batch 1 (150 repos) or the batch-2 new100 / pairs50 adds. The shared `manifest.json` is
rewritten by every concurrent runner too, so its run_id / census only describe the last writer.

**Fix direction:** tolerate a missing source in the rotation (`FileNotFoundError` → already
rotated), and either serialise the runners per output root in `add_repos.py` or give
`--repo` runs their own manifest/units scope.

### TH-120: `run_thermal.py` summary and `_aggregate.json` always report 0 findings — they read the pre-harmonization summary keys

**Severity:** LOW (display / aggregate only; per-unit thermal outputs are correct)
**File:** `run/run_thermal.py:229-235` (`summary.get("total_checks")`, `summary.get(sev.lower())`)
**Discovered:** 2026-11-16, corpus batch 2 thermal pass

**Symptom:** "Files with findings: 0 / Total findings: 0" and every row "(no findings)"
over 928 pairs (batch 1: 810, same), while the outputs carry findings
(hookprobe-sbc `summary.total_findings` 1, parsnip 1). The analyzer's summary is
`{"total_findings", "by_severity": {...}}`; the runner still reads `total_checks` and
flat severity keys, so the console summary and `results/outputs/thermal/_aggregate.json`
undercount to zero.

**Fix direction:** read `total_findings` and `by_severity` (with the analyzer's severity
vocabulary), plus a unit test on a real thermal output.

## Priority Queue

_35 open KH-* + 16 open TH-* issues (2026-10-14: TH-052/053/058 FIXED (H0 plan 1), +TH-060/061/062 filed. Earlier: 2026-10-06: v2.3.1 shipped @ 0684046 and the corpus regen ran CLEAN. Closed this cycle, all in FIXED.md: KH-408..415, KH-418/420 (v2.3.1 batch + follow-up), KH-419/424/425 (SacMap soak fixes), TH-054 (run_emc crash masking). Open KH: 328..334 datasheets-infra backlog; 355/364/365 audit remainder; 403/404 HIGH connectivity over-unions; 416/417 v2.3.1 riders; 421 Marble hash-seed nondeterminism; 422 `--full` point-in-polygon cost; 423 legacy `.sch` empty fields; 426..440 SacMap soak long tail; 441 via_in_pad attribution; 442 behavioral opamp gain 0. Open TH: 037..042/044/047 legacy; 049 contamination tripwire; 055 timeout-class v1.3-era pcb outputs (191 boards); 056 KH-313 anchor; 057 bugfix generator merge-by-id; 059 batch SPICE hermeticity; 060 kh393 power-rails test premise stale (strict xfail); 061 test_datasheet_db_cli writes repos/.test_fallback; 062 print-and-return vacuous skips in smoke files. Earlier history: 19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
