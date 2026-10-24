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

Last updated: 2026-10-22

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-469** (KH-468 filed 2026-10-23 during the Checklist 11 ADC-map verification — `_ADC_RESOLUTION_MAP` 15 of 29 part-number prefixes are wrong, span several resolutions, or name parts that do not exist, LOW; KH-467 filed 2026-10-23 during the Checklist 11 backlog pass — three divergent LED forward-voltage tables (`_LED_VF` / `_LED_VF_FLOOR` in domain_detectors, `_LED_VF_BY_COLOR` in validation_detectors) disagree per colour, LOW; KH-464..466 filed 2026-10-23 from the v3 round-7 handoff §11 — lifecycle_audit missing-input traceback, `is_cross_analysis_ground_name` exact-set policy (SGND/GNDPWR/GND_ISO/VSSA/`/Power/GND` not ground), `analyze_gerbers` exit 0 on a nonexistent dir; all pre-existing, verified at 0490c49, LOW; KH-463 filed 2026-10-23 at the v2.3.2 corpus regen — SPICE testbench `.control` `echo … > <path>` redirect unquoted, every measurement silently skips when the workdir path has whitespace or `,`/`&`/`'`/non-ASCII, the user-facing `analysis/<run>/spice_work/` default inherits the project path, MEDIUM; KH-456..462 filed 2026-10-22 from the SacMap rev2 run-9 soak at the v2.3.2 pre-tag `4701c26` — fab_release_gate counts `G***` logo footprints (false FAIL), silk revision regex misses `rev2`, `capability_mode` `datasheet_coverage_pct` is a hard-coded stub, `audit_pwr_flags` ignores `power_in` pins off named rails (ERC `power_pin_not_driven` ×3 unseen), EMC DC-002 fires on a part-numbered ESD array (dupes UC-001), `cross_domain_signals.needs_level_shifter` stale after KH-424, `datasheet_verify` rc 1 for warnings; riders on KH-431/432/436; all code-verified by the main-repo agent; KH-455 filed 2026-10-22 at the v2.3.2 backport gate — PP-001 `(ref, pin_number)` dedup masks a second symbol's power pin on unannotated `U?` designs, the gate's one residue unit, LOW; KH-454 filed 2026-10-22 at the v2.3.2 backport adoption — RS-001 fires on a bootstrap-only net whose sole `power_in` pin is the BST/BOOT pin, LOW, with the two GitHub #55 riders; KH-450..453 assigned 2026-10-22 FIXED-direct — GitHub #52–#55 / PRs #56–#59 by EldarPolitkin on `main` @ 4701c26, see FIXED.md; KH-449 filed 2026-10-16 at the v3 round-5 full-chain gate — pcb `--full` exceeds the 600 s cap on starshipraider MAXWELL both sides, LOW; KH-447 addendum: LT3514 is a ≥ 20 GB memory blow-up, OOM-killed under the 600 s cap; KH-448 filed 2026-10-16 at the v3 round-4 gate — hierarchy-mode `analyze_schematic.py` ~3 GB RSS on BerkeleyLab/Marble, both sides equal, LOW; KH-446/447 filed 2026-10-15 at the v3 round-2 reply per ruling Q3 — empty-input pcb traceback (hackclub/OnBoard placeholders), schematic 120 s timeouts on three hierarchical roots (discrete-nes ×2, LT3514); KH-445 filed 2026-10-15 at H0 plan 4 — `EQ-042` tags two different equations, LOW; KH-444 assigned 2026-10-14 FIXED-direct — PR #51 AM-001 `<domain>_max` key lookup, imrcly, see FIXED.md; KH-443 filed 2026-10-14 from GitHub #50 — net ties not bridged by RS-001/PP-001 DC-continuity audits, MEDIUM; KH-442 filed 2026-10-06 at the v2.3.1 regen — behavioral opamp model gain 0 false SP-WARN; KH-441 filed 2026-10-06 at the soak-fix gate — via_in_pad first-match attribution ambiguity on rotated QFN/DFN; KH-424 VM-001 trusted-extraction EN fallthrough + KH-425 diff_analysis float delta FIXED-direct and KH-419 FIXED at the SacMap soak fixes @ ef6d55c, see FIXED.md; KH-426..440 filed 2026-10-06 from the SacMap rev2 run-8 soak long tail — XV MPN compare, `.kicad_dru` hole_size precedence, has_pull_up sign, find_pdf glob, SOT-563/θJA, lifecycle finding_id, RGB-LED/PTC power budget, extraction local_path staleness, PD-001 silence, DS-003 sidecars, touch-pad test points, trust_summary provenance (Aug B13), datasheet_verification null rules, sleep-audit riders, DRC lib-table doc note; KH-421..423 filed 2026-10-06 at the KH-418/420 follow-up adoption — Marble U54 hash-seed nondeterminism, `--full` `_point_in_polygon` cost, legacy `.sch` empty-field skip; KH-418 + KH-420 FIXED on main @ 9fbbb26, see FIXED.md; KH-420 filed 2026-10-05 at the v2.3.1 gate — KH-413 THT touch-pad sampling 11× slower on a 130-touch-pad board, the only candidate-side timeout in 170,014 units; KH-416..419 filed 2026-10-05 at the v2.3.1 batch adoption — peer-sheet inner-hierarchy sheet-pin tagging, `_pad_on_layer` NPTH wildcard, KH-414 regression: generic `Part#` overrides explicit `MPN` with an LCSC code, KH-413 circle-pad bbox rider; KH-408..415 FIXED in v2.3.1, see FIXED.md; KH-415 filed 2026-10-05 — `capability_mode.get_capability_mode_ref` KeyError on a malformed `capability_mode.json`, LOW, found at the v2.3.0 regen via TH-054; KH-414 filed 2026-10-04 — GitHub #46 `Manufacturer P/N`/`Digikey P/N` alias gap, three divergent MPN alias lists, MEDIUM; KH-408..413 filed 2026-09-13 from the v2.3.0 correctness batch — thermal-pad-via rotation sign, Altium peer-sheet `_sheet` tagging, RP-001 touch-void wording, thermal skip-reason vocabulary, DFM `parameter` pad-drill, THT-only touch pads; KH-373..379/383/386/396..401/405..407 FIXED and KH-395 REFUTED in that batch, see FIXED.md; KH-407 filed 2026-09-13 — `0V<suffix>` ground spellings read as rails after PR #44, gate residue; KH-406 filed 2026-09-12 — `differential_pairs[].esd_protection` set-order nondeterminism, pre-existing, found during PR #44 review; KH-403/404 filed 2026-09-10 — schematic connectivity over-unions on MAXI030 / Olivetti M20 L1, kicad-cli-refuted, surfaced by PR #43's SH-001 sample; KH-405 filed 2026-09-10 — jlcsearch `extra` block gone, lcsc datasheet fetch degraded; KH-402 assigned 2026-09-01 at the
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
KHPA finding ID). Next TH number: **TH-077** (TH-076 fixed-on-discovery 2026-10-23 during the Checklist 11 backlog pass — `audit_constants.py scan` dropped and re-added every constant whose file moved without a `relocate --map` (rounds 2/3), losing 41 verification records incl. `_REGULATOR_VREF` 55/114 and `_CAP_ESL` 7/7; the registry had also not been rescanned since round 5, see FIXED.md; TH-075 fixed-on-discovery 2026-10-23 at the v2.3.2 corpus regen — `run_spice.py` per-unit `--workdir` carried raw repo/file names into ngspice, 18,464 sims silently skipped on 5,198 corpus units, directory name now sanitized + digest, see FIXED.md; TH-074 fixed-on-discovery 2026-10-22 at the v2.3.2 backport gate — long-run waiters stalled on a `pgrep -f` self-match and on a zombie PID; `tools/wait_for_run.py` + RUNBOOK 26k + full-chain `done.json` marker, see FIXED.md; TH-073 fixed-on-discovery 2026-10-17 at the v3 round-6 gate preflight — `run_corpus_gate.py` accepted analyzer-less profiles (`spice-offline`, the new `distributor-offline`) and would have run a zero-unit gate, guard added, see FIXED.md; TH-072 fixed-on-discovery 2026-10-16 at the v3 round-5 gate preflight — `full-chain` profile declared no schematic analyzer, Phase B ran no chained unit, see FIXED.md; TH-071 filed 2026-10-16 at the v3 round-4 gate — `run_corpus_gate.py --jobs` not memory-aware, hierarchy profile at 32 jobs OOMs the box, LOW; TH-070 filed 2026-10-15 at the v3 round-2 reply — scan-coverage identity by line/file yields ~150 false losses per structural round, MEDIUM; TH-069 FIXED 2026-10-15 at the v3 round-3 reply — discover.py regular-file filter + manifest regen, see FIXED.md; TH-068 filed 2026-10-15 at H0 plan 6 — fixture-lane A/A chained envelopes unverifiable after the basetemp move, LOW; TH-067 filed 2026-10-15 — batch-runner pool workers outlive a killed parent (the TH-063 mechanism), MEDIUM; TH-066 filed 2026-10-15 at the H0 plan 4 final review — audit tools walk 58 of the 90 scanner files; TH-065 filed 2026-10-15 at H0 plan 4 — audit_constants function-scope `name:line` identity churns the registry; TH-064 filed 2026-10-15 — emc/thermal/spice `--resume` refused until identity-based resume exists; TH-063 filed 2026-10-14 — mutating runner launched against the live tree from a TDD RED step, 16,909 emc outputs rewritten, no measurable impact; TH-055 and TH-059 (harness half) fixed 2026-10-15 (H0 plan 2), see FIXED.md; TH-062 filed 2026-10-14 — 58 print-and-return vacuous skip paths in required-tier smoke files; TH-061 filed 2026-10-14 — test_datasheet_db_cli.py fallback fixture writes under repos/; TH-060 filed 2026-10-14 — test_kh393_power_rails_threaded premise stale since PR #44, now strict xfail; TH-052/053/058 fixed 2026-10-14 (H0 plan 1, honest pytest collection), see FIXED.md; TH-059 filed 2026-10-06 at the v2.3.1 regen — batch SPICE side effects: spice/ dirs in repos/ + live DigiKey lookups; TH-058 filed 2026-10-06 — `test_kh420_zone_fill_segment_grid.py` wall-clock assertion (< 30 s on the NLoy corpus board) is load-sensitive: 8.5 s idle, 19.5 s with a 32-job gate running, so the pre-push hook can flake under load; TH-057 FIXED 2026-10-15 at H0 plan 5 — generator rewritten as grouped reconciliation, see FIXED.md; TH-056 filed 2026-10-05 — KH-313 corpus-lock anchor lost: TERES never runs check_inductor_leakage's crash path (no PCB pairing, 0 rf_chains) and `categories_checked` semantics changed, lock re-anchored; TH-055 filed 2026-10-05 — the 198 pcb timeout-class units keep v1.3-era outputs (148 schema 1.3.0 / 29 pre-schema / 21 none) under a hard-coded 120 s `ANALYZER_TIMEOUT`, downstream emc/thermal stale too; TH-054 fixed-on-discovery 2026-10-05 at the v2.3.0 regen — run_emc masked analyzer crashes behind stale outputs, EMC corpus stale since 2026-08-20/2026-05-15, see FIXED.md; TH-053 filed 2026-09-13 — pytest vs run_tests.py tier disagreement on 17 files; TH-052 filed 2026-09-13 — 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; TH-051 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — dual-format twins raced on one thermal output, see FIXED.md; TH-050 fixed-on-discovery 2026-09-01 at the v2.2.1 regen — capability_mode.json sidecars fed to spice/emc/thermal runners, see FIXED.md; TH-049 filed 2026-09-01, results/outputs partial-contamination tripwire, found at the v2.2.1 regen before-baseline; TH-048 fixed-on-discovery 2026-08-20, seed.py enum-count gap, see FIXED.md; TH-047 filed 2026-08-20, KH-198 corpus-lock anchor lost at v2.2.0 regen; TH-046 fixed-on-discovery
2026-07-16, see FIXED.md).

> 76 open issues (55 KH + 21 TH).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

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

**Fix direction:** one shared table in `kicad_core` (the round-7 shared-tables
pattern) with a cited source per colour (manufacturer typical-Vf ranges, e.g.
Vishay / Kingbright / Würth colour tables), nominal + floor as two fields of one
entry; both detectors read it. Harness: register the table once and verify it under
Checklist 11b; the three current constants retire.

### KH-466: `analyze_gerbers.py <nonexistent dir>` exits 0 with an empty, well-formed result — a mistyped path looks like a board with no gerbers

**Severity:** LOW (CLI contract; a scripted caller cannot tell "no gerber files" from "no such directory")
**File:** `skills/kicad/scripts/analyze_gerbers.py:1168` (`gerber_dir.glob(...)` on a path that is never existence-checked) → `main` returns 0 at `:1646`
**Discovered:** 2026-10-23, v3 round-7 handoff §11 (pre-existing: identical at `4701c26` and `0490c49`); verified: `analyze_gerbers.py /nonexistent_dir_xyz --compact` → rc 0, `{"analyzer_type": "gerber", "directory": "/nonexistent_dir_xyz", "layer_count": 0, "statistics": {"gerber_files": 0, ...}}`

**Fix direction:** `parser.error` / exit 2 when `args.directory` is not a directory (the usage-error convention the other CLIs follow); no analyzer output moves for real inputs. The round-7 text oracle freezes today's behaviour — refresh its baseline with the fix.

### KH-465: `cross_analysis.is_cross_analysis_ground_name` matches an exact name set only — `SGND`, `GNDPWR`, `GND_ISO`, `VSSA` and sheet-pathed `/Power/GND` are not ground to cross_analysis

**Severity:** LOW (pre-existing policy, named in round 7; the schematic side already classifies these as ground via `kicad_core.netnames.is_ground_name`, so cross-analysis plane-split / ground-domain checks disagree with the schematic on such designs)
**File:** `skills/kicad/scripts/cross_analysis.py:41` (`is_cross_analysis_ground_name`, formerly `_is_ground_net`; strips `/`, `-`, `_` then matches an exact set; the `GND_D` / `GND_A` entries are unreachable after stripping)
**Discovered:** 2026-10-23, v3 round-7 handoff §11; verified at `0490c49`: `{'GND': True, 'SGND': False, 'GNDPWR': False, 'GND_ISO': False, 'VSSA': False, '/Power/GND': False, '/GND': True, 'EARTH': True}`

**Fix direction:** delegate to `kicad_core.netnames.is_ground_name` (strip the sheet path first) plus the cross-analysis extras (EARTH, CHASSIS). Gate budget at the fixing round: cross_analysis findings on every board whose ground nets use the newly-recognised names — size with a corpus walk before the gate.

### KH-464: `lifecycle_audit.py <missing input>` dies with an unhandled `FileNotFoundError` traceback instead of a usage error

**Severity:** LOW (CLI contract; exit 1 with a traceback where the other CLIs print a usage error)
**File:** `skills/kicad/scripts/lifecycle_audit.py:1048` (`with open(input_path) as f:` with no existence check; `main()` has no `argv`/return seam — the one CLI left bare in round 7 because the frozen text-oracle artefact `neg__lifecycle_audit__missing` quotes this traceback)
**Discovered:** 2026-10-23, v3 round-7 handoff §11; verified at `0490c49`: `lifecycle_audit.py /nonexistent_file.json` → `FileNotFoundError: [Errno 2] No such file or directory`

**Fix direction:** check the path and `parser.error` (exit 2) before opening; then give `main(argv=None) -> int` the same seam as the other eleven CLIs and refresh the text-oracle baseline (the frozen artefact changes by design).

### KH-463: SPICE testbench `.control` block redirects `echo … > <path>` unquoted — every measurement silently reports `skip` when the workdir path contains whitespace or shell-ish punctuation

**Severity:** MEDIUM (silent: no error and no `fail` — the whole subcircuit set reports `skip` with "ngspice … measurement failed"; the user-facing default workdir `analysis/<run>/spice_work/` inherits the project path, so a project under a folder with a space loses every SPICE result)
**File:** `skills/spice/scripts/spice_simulator.py:181` (`lines.append(f'echo "{echo_str}" > {output_path}')`); default workdir `skills/spice/scripts/simulate_subcircuits.py:551` (`os.path.join(run_dir, 'spice_work')`)
**Discovered:** 2026-10-23, v2.3.2 corpus regen at `2fd9aa0` (`results/v232_regen/`) — the harness's per-unit `--workdir` (TH-059 fix) carried raw repo/file names: 18,464 of 19,455 sims skipped on the 5,198 corpus units whose path has whitespace / `,` / `&` / `'` / `µ` / `:`, vs 3.7 % elsewhere (TH-075, harness side fixed by sanitizing the directory name).

**Repro:** `simulate_subcircuits.py "<0Prashant/Kicad LED ARRAY CIRCUIT schematic output>" --workdir "/tmp/ws a" --compact` → `pass 0 / skip 1` ("ngspice DC sweep measurement failed", 0.004 s); `--workdir /tmp/ws_b` → `pass 1`. The ngspice log shows the analysis ran (`vbe_on = 6.54e-01`); the `echo … > /tmp/ws a/transistor-circuit_Q1.out` redirect split at the space and the `.out` file never appeared.

**Fix direction:** run ngspice with `cwd=workdir` and redirect to the bare filename (`echo "…" > transistor-circuit_Q1.out`), so no path reaches the ngspice control language; quoting the path is untested. No corpus output moves once fixed (the harness already feeds a safe path).

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

### KH-455: PP-001 deduplicates on `(ref, pin_number)` — on unannotated / duplicate-ref designs a second symbol's power pin is silently masked

**Severity:** LOW (masked true findings; surfaced as the single residue unit of the v2.3.2 backport gate, 1 unit in 36,465)
**File:** `skills/kicad/scripts/signal_detectors.py` — `audit_power_pin_dc_paths` (`seen: set[tuple[str, str]]` keyed `(ref, pin_num)`, ~line 4575 at `4701c26`)
**Discovered:** 2026-10-22, v2.3.2 backport gate `6a91aaa→4701c26` (`results/v232_gate/adjudication_v232.md` §5)

**Repro:** `Ganesh-Solapure/PCB-Projects` `STM 32 PCB/STM 32 PCB.kicad_sch` (every IC is `U?`). A gate driver's pin 48 (`BST_A`) and the STM32's pin 48 (`VDD`, net `__unnamed_53`) share the key `("U?", "48")`. At `6a91aaa` the BST_A pin is walked first and `U?.48 (VDD)` is never evaluated, although its siblings `U?.19/32/64 (VDD)` on the same net all fire PP-001. At `4701c26` the KH-453 bootstrap skip runs BEFORE the dedup, so the VDD pin is evaluated and PP-001 appears (12 → 9 PP-001 on the unit: −4 bootstrap, +1 unmasked).

**Fix direction:** key the dedup on the pin's identity, not its label — e.g. `(ref, pin_num, net_name)` or the component's uuid / `symbol_id` when the ref is unannotated (`?` suffix) or duplicated. Also applies to any other detector that dedups on `(ref, pin)` strings. Gate budget for the fixing range: PP-001 appearances only, and only on units with duplicate refs.

### KH-454: RS-001 fires "no declared source" on a bootstrap-only net — the net's only `power_in` pin is the gate-drive BST/BOOT pin

**Severity:** LOW (false warning, no crash; 31 units / 8 repos at the v2.3.1-regen outputs per the main-repo pre-scan; found while sizing PR #59 and confirmed by the author's "not in this PR" list)
**File:** `skills/kicad/scripts/signal_detectors.py` — `_power_rail` (admits any net with a `power_in` pin) / `audit_rail_sources` (RS-001)
**Discovered:** 2026-10-22, main-repo handoff for the v2.3.2 backport (`6a91aaa..4701c26`)

**Repro:** `tests/fixtures/kh453/pp001_bootstrap.kicad_sch` — buck U1 with VIN (`power_in`, +5V with PWR_FLAG), GND, SW (`output`), BST (`power_in`), C1 100 nF BST–SW. At `4701c26` the PP-001 is gone (KH-453) but the sheet still gets
`RS-001 warning deterministic: BST has no declared source, pins ['U1.4']`. The `BST` net is a "rail" to `_power_rail` because it carries a `power_in` pin, and it has no source by construction: its supply is the capacitor to the switch node.

**Fix direction:** reuse `_is_bootstrap_pin_name` in `_power_rail` — ignore bootstrap-named pins when deciding whether a net has a `power_in` load, so a net whose `power_in` pins are ALL bootstrap-named is not audited as a rail. v3 round 7 Task 6 folds `_BOOTSTRAP_PIN_TOKENS` into the planned `_BOOTSTRAP_PIN_NAMES` table; the fix should land on the merged table. Gate budget for the fixing range: RS-001 disappearances only, and only where every `power_in` pin on the finding's net is bootstrap-named (31 units / 8 repos expected).

**Riders from GitHub #55 (same entry, not fixed):**
- (a) regulator-output pins typed `power_in` with decoupling only (DRV8412 `VREG`) hit the same PP-001 inversion — needs a name list or datasheet facts, like the existing `VCAP`/`VDDREG` internal-rail demotion.
- (b) #55 asked whether PP-001 should be `warning` while the rule is `heuristic`; severity left at `error` — open question for a batch.

**Harness note:** these RS-001 findings have `pins != []`, so the v2.3.2 budget (class A = `pins == []` flips only) leaves them byte-identical on both sides — they are not gate residue.

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

### KH-447: `analyze_schematic.py` exceeds the 120 s cap on three hierarchical root sheets (standard profile, `--no-hierarchy`)

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

### KH-446: `analyze_pcb.py` crashes with a traceback (exit 1) on an empty `.kicad_pcb`

**Severity:** LOW (corpus placeholders; wrong failure mode, not wrong analysis)
**File:** `skills/kicad/scripts/analyze_pcb.py` (`main` → `sexp_parser.parse`; `sexp_parser.py:93` `_parse_tokens` raises `ValueError("Unexpected end of input at position 0")`, uncaught)
**Discovered:** 2026-10-15, v3 baseline at `6a91aaa` (ledgered as `both_failed` pcb crashes; filed at the round-2 reply per the maintainer's ruling Q3)

**Symptom:** `hackclub/OnBoard` `projects/holy60-3d/src/holy60-3d.kicad_pcb` and
`projects/tofyKeeb/src/tofyKeeb.kicad_pcb` are 2-byte files (`\r\n`; identical
input sha `7eb70257…`). The analyzer lets the parser's `ValueError` escape as a
full traceback with exit 1 and no JSON. The harness accepted-exit table records
`crash` (exit 1, no output). The third ledgered "pcb crash" (`BrettHallen/
Conversion_Boards` `TFC_10-pin 2.kicad_pcb`, exit 2 "No .kicad_pro file found in
directory") is a harness manifest defect, not a product one — see TH-069.

**Expected:** an empty or non-KiCad input yields a one-line diagnostic and a
clean non-zero exit (the existing exit-2 usage path), no traceback. Same class
as KH-415 (unvalidated input read).

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

**Rider (2026-10-22, soak run 9):** the manifest's `outputs` also never lists `drc.json`, `erc.json`, `parasitics.json` or `fab_release_gate.json` written into the run folder, and `LC-007` "Lifecycle audit not run — --lifecycle flag not passed" remains in `schematic.json` after the standalone `lifecycle_audit.py` wrote `<run>/lifecycle.json`. Same fix family: register side outputs; drop LC-007 when `lifecycle.json` exists for the current run.

### KH-432: power_budget counts an RGB LED as a flat 5 mA (cathode resistors R3/R4/R5 ignored, ~48 mA real) and ignores the USB VBUS load behind the PTC — thermal then skips U2 as `below_min_pdiss`

**Severity:** MEDIUM (KH-375 rider: multi-die LEDs and PTC-fed loads are under-counted, so a regulator that really dissipates is skipped by thermal)
**File:** `skills/kicad/scripts/analyze_schematic.py` (power_budget LED load model, KH-375 series-resistor branch; VBUS/PTC path)
**Discovered:** 2026-10-05, SacMap rev2 run-8 fresh-agent soak on 9fbbb26 (`~/Projects/sandbox/Old-Reviews/sacmap-rev2/8/REVIEW-2026-10-05.md`, Appendix B); filed by the harness 2026-10-06

**Symptom:** SacMap RGB LED with three cathode resistors is budgeted at 5 mA total instead of ≈48 mA (three channels × (3.3 − Vf)/R); the VBUS consumer behind the PTC is not attributed to the rail; thermal `skipped_components` lists U2 `below_min_pdiss`.

**Fix direction:** model multi-pin LEDs per channel through each cathode/anode resistor; treat a PTC (fuse-typed, KH-414 F-ref rules) as a pass-through for load attribution; fixture = RGB LED + 3 resistors + PTC-fed consumer.

**Gate budget (when fixed):** `power_budget.rails[*].estimated_load_mA` up on RGB-LED / PTC boards, thermal T3-class downstream (TS-00x/TP-001), `skipped_components` shrink.

**Rider (2026-10-22, soak run 9):** `cross_analysis.py:686-699` TW-001 builds its current map from `detect_power_regulators` findings' `estimated_iout_A` only and skips with "no power regulator current estimates in schematic analysis" while `power_budget.rails[*].regulator` / `estimated_load_mA` exist for both rails — the two scripts disagree about what counts as an estimate. When the budget is fixed, TW-001 should fall back to `power_budget` rail loads.

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

**Rider (2026-10-22, soak run 9):** `FD-001` has the same blind spot — "No fiducials on B.Cu (2 SMD components)" counts the two 15 mm touch pads as the B.Cu SMD components. Whatever CP-003 uses to classify a `TestPoint` symbol as a touch pad should feed `test_coverage` AND the fiducial check.

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

### TH-066: `audit_constants.py` / `audit_equations.py` scan only `skills/{kicad,spice,emc}/scripts` — 58 of the 90 files the shared walker covers

**Severity:** LOW (coverage blind spot; nothing wrong is reported, some things are not reported)
**File:** `validate/audit_constants.py` (`SCAN_ROOTS`, `iter_source_files`), `validate/audit_equations.py` (same), `tools/source_scan.py` (`coverage_snapshot` consumes both)
**Discovered:** 2026-10-15, H0 plan 4 final review (F9)

**Symptom:** `tools/source_scan.iter_product_sources` walks every
`skills/*/scripts/**` and `skills/*/*/scripts/**` file (90 at product
`6a91aaa`), but the two audit tools keep their own three-root walk (58 files).
Constants and `EQ-NNN` tags under `skills/kicad/review/`, `skills/datasheets/`,
`skills/bom/` and the distributor skills never enter the registries or the
coverage baseline (0 EQ tags and roughly 7 module constants today). Documented
in `tools/SCANNER_POLICY.md` and the baseline's `roots` field.

**Fix direction:** make both audit tools consume `source_scan.iter_product_sources`
(one walker, one file identity), re-key the registries once via the existing
`qualify_registry_paths` / relocation path, then re-accept the coverage baseline
(`source_scan.py check --accept-baseline`) in the same commit.

### TH-065: `audit_constants.py` function-scope identity is `name:line`, so a line shift churns the registry

**Severity:** LOW (registry noise; verification evidence survives only for module-scope constants)
**File:** `validate/audit_constants.py` (`ConstantVisitor`: function-scoped constants are keyed with the defining line number in `scope`)
**Discovered:** 2026-10-15, H0 plan 4 Task 4 (recursive rescan: 467 added / 205 updated / 106 removed at product `6a91aaa`)

**Symptom:** a pure line move of a function (any edit above it) renames the
`scope` of every function-local constant, so the registry reports them as
removed + re-added and any `verified` status on them is lost. Part of the 106
"removed" at the 2026-10-15 rescan were exactly this class.

**Fix direction:** key function-scope constants by `(file, enclosing function
qualname, name)` and keep the line only as location metadata; one-time
re-key of existing entries via the `relocate --map` machinery or a dedicated
upgrade in `qualify_registry_paths`.

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

_35 open KH-* + 16 open TH-* issues (2026-10-14: TH-052/053/058 FIXED (H0 plan 1), +TH-060/061/062 filed. Earlier: 2026-10-06: v2.3.1 shipped @ 0684046 and the corpus regen ran CLEAN. Closed this cycle, all in FIXED.md: KH-408..415, KH-418/420 (v2.3.1 batch + follow-up), KH-419/424/425 (SacMap soak fixes), TH-054 (run_emc crash masking). Open KH: 328..334 datasheets-infra backlog; 355/364/365 audit remainder; 403/404 HIGH connectivity over-unions; 416/417 v2.3.1 riders; 421 Marble hash-seed nondeterminism; 422 `--full` point-in-polygon cost; 423 legacy `.sch` empty fields; 426..440 SacMap soak long tail; 441 via_in_pad attribution; 442 behavioral opamp gain 0. Open TH: 037..042/044/047 legacy; 049 contamination tripwire; 055 timeout-class v1.3-era pcb outputs (191 boards); 056 KH-313 anchor; 057 bugfix generator merge-by-id; 059 batch SPICE hermeticity; 060 kh393 power-rails test premise stale (strict xfail); 061 test_datasheet_db_cli writes repos/.test_fallback; 062 print-and-return vacuous skips in smoke files. Earlier history: 19 open KH-* + 10 open TH-* issues (2026-10-04: +KH-414 MEDIUM `Manufacturer P/N`/`Digikey P/N` MPN-alias gap from GitHub #46, needs a budgeted gate — SS-001/DS-001/missing_mpn/PCB mpn move. Earlier: 2026-09-13 v2.3.0 correctness batch: −18 KH FIXED — 373/374/375/376/377/378/379/383/386/396/397/398/399/400/401/405/406/407 — and KH-395 REFUTED by the kicad-cli oracle, all in FIXED.md; +KH-408..413 LOW/MEDIUM follow-ups from the batch; +TH-053 LOW pytest-vs-run_tests tier disagreement. Remaining KH: 403/404 HIGH connectivity over-unions (kicad-cli-refuted, bisect set recorded), 355/364/365 audit remainder, 328..334 datasheets-infra backlog, 408..413 batch follow-ups. Earlier history: 31 open KH-* + 9 open TH-* issues (2026-09-13: +KH-407 LOW `0V<suffix>` grounds read as rails — PR #44 gate residue; +TH-052 MEDIUM 17 root tests/ files without a `__main__` runner, 190 tests silently skipped by the pre-push hook; PR #44/#43/#42 merged and gated CLEAN at 788649f, KH-405 half-closed by #42; 2026-09-12: +KH-406 LOW differential_pairs esd_protection set-order nondeterminism; 2026-09-10: +KH-403/404 HIGH connectivity over-unions, +KH-405 MEDIUM jlcsearch API drift; post v2.2.x batch, 2026-08-31 — 25 fixes moved to FIXED.md, gate CLEAN): NEW: KH-401 MEDIUM (cross_analysis VS-002 crash on bounding_box null — pre-existing, --full-only, found during gate adjudication). 2026-08-31 Task-27 filings — MEDIUM: KH-396 (rf_chains component_roles hash-order — determinism-guard blind spot, needs RF fixture), KH-398 (TH-DET assessment-level confidence "deterministic" for package_table — LIVE twin of fixed KH-387, moves every package_table board when fixed); LOW: KH-395 (bus_alias project-wide merge), KH-397 (GP-001 antipad credit lacks via-layer-span filter — KH-392 rider, stacks with all-zones clearance max), KH-399 (EMC circle-outline edges fall to wrong distance branch), KH-400 (trailing-comma regex not string-aware — KH-368 remainder). 2026-08-20 SacMap-soak remainder — HIGH: KH-373 (CP-003 bbox 0.0mm, 78% corpus FP), KH-374 (sleep audit), KH-375 (power_budget loads; feeds thermal+EMC), KH-376 (datasheet gating dead — no project_dir; also keeps KH-387's fix latent), KH-377 (PD-001 feedforward-cap manufactured errors), KH-379 (DC-001 no-shared-net + DC-002 suppression), KH-383 (pad-drill blindness), KH-386 (thermal silent exclusion); MEDIUM: KH-378 (GP-001 touch-net exemption). The 2026-07-24 audit-batch remainder: KH-364/365 MEDIUM (KH-359/360 closure CONFIRMED by main-repo 2026-08-31 — shipped in v2.2.0, moved to FIXED.md). KH-355 LOW (multi-channel FB-pin selection, needs design — explicitly NOT addressed by the en_net lexicographic pick, see FIXED KH-366/367) + datasheets-infra backlog KH-328..334 (LOW) + harness-side TH items (TH-047 KH-198 lock re-anchor). Audit reference: kicad-happy `docs/2026-07-24-kicad-parser-and-analysis-audit.md`. The v2.2.x maintenance batch KH-357/358/361-363/366-372/380-382/384/385/387-394 was fixed 2026-08-31 (25 fixes, budgeted gate CLEAN, `results/v22x_gate/adjudication_v22x.md`); the v2.1 bug batch KH-338..346 + KH-348..350 was fixed 2026-07-15; gate-adjudication finds KH-354/KH-356 were fixed 2026-07-16 — see FIXED.md._
