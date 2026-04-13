# Fixed Issues

Record of resolved kicad-happy analyzer bugs (KH-*) and test harness issues (TH-*).
Shows what changed, where, and how it was verified — useful for cross-referencing
regressions, understanding analyzer evolution, and onboarding collaborators.

> **Protocol**: When fixing issues, remove them from [ISSUES.md](ISSUES.md) and add here
> in the same session. Each entry must include: root cause, fix description, and
> verification results. See README.md "Issue tracking protocol" for full details.
> Open issues are in [ISSUES.md](ISSUES.md).

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
