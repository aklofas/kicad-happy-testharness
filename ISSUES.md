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

Last updated: 2026-04-12

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-282**. Next TH number: **TH-026**.

> 16 open issues (10 TH-*, 6 KH-*).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-276: RC filter detected with cutoff_hz=0.0 (R=0 or C=0)

**Severity:** LOW
**Discovered:** 2026-04-12 by harness invariant checker during corpus validation
**Where:** `kicad-happy/skills/kicad/scripts/signal_detectors.py` in `detect_rc_filters()`

**Root cause:** The analyzer detects RC filter structures where R=0 or C=0, producing `cutoff_hz=0.0`. These shouldn't be classified as filters — a 0-ohm resistor in series with a cap is a DC block, not a low-pass filter.

**Suggested fix:** Skip RC pairs where either parsed value is zero or missing in the detection loop.

---

### KH-277: API key passed in URL query params (Mouser, element14)

**Severity:** MEDIUM
**Discovered:** 2026-04-12 during code review
**Where:**
- `kicad-happy/skills/mouser/scripts/fetch_datasheet_mouser.py:80`
- `kicad-happy/skills/element14/scripts/sync_datasheets_element14.py`

**Root cause:** Mouser and element14 API keys are embedded in URL query parameters (`?apiKey=...`). Exposed in server logs, proxy caches, referrer headers, browser history.

**Suggested fix:** Move API keys to HTTP headers (`Authorization: Bearer` or `X-API-Key`). Check each distributor's API docs for supported auth methods.

---

### KH-278: EMC GP-001 silently returns empty when PCB data missing

**Severity:** MEDIUM
**Discovered:** 2026-04-12 during code review
**Where:** `kicad-happy/skills/emc/scripts/emc_rules.py:258-299` in `check_return_path_coverage()`

**Root cause:** When `pcb.get('return_path_continuity')` is None (board analyzed without `--full`), the function returns an empty list. No finding reports that the check couldn't run due to missing data.

**Suggested fix:** Emit an INFO-level finding: "Return path data unavailable — run PCB analyzer with --full for GP-001 coverage analysis."

---

### KH-279: emc_formulas divide-by-zero on zero/negative inputs

**Severity:** MEDIUM
**Discovered:** 2026-04-12 during code review
**Where:** `kicad-happy/skills/emc/scripts/emc_formulas.py:127,184,209,461`

**Root cause:** `dm_radiation_v_m()`, `cm_radiation_v_m()`, and `microstrip_impedance()` divide by distance/height without checking for zero. `harmonic_spectrum()` doesn't guard `switching_freq_hz <= 0`. Produces inf/NaN or math domain errors on edge-case inputs.

**Suggested fix:** Add input validation at each function entry. Return 0.0 for unphysical inputs.

---

### KH-280: MPN sanitization creates cache key collisions

**Severity:** MEDIUM
**Discovered:** 2026-04-12 during code review
**Where:** `kicad-happy/skills/kicad/scripts/datasheet_extract_cache.py:122-124`

**Root cause:** `_sanitize_mpn()` replaces all non-alphanumeric chars with `_`. Different MPNs like `STM32F-103RBT6` and `STM32F/103RBT6` produce identical cache keys `STM32F_103RBT6`, overwriting each other's extractions.

**Suggested fix:** Append a short hash of the original MPN: `f"{sanitized}_{hashlib.md5(mpn.encode()).hexdigest()[:6]}"`.

---

### KH-281: analysis_cache copies forward stale outputs without checking source hashes

**Severity:** MEDIUM
**Discovered:** 2026-04-12 during code review
**Where:** `kicad-happy/skills/kicad/scripts/analysis_cache.py:256-266`

**Root cause:** When a new analysis run doesn't produce all output types, the cache copies forward outputs from the previous run. But it doesn't check if the source files (schematic/PCB) changed between runs. If only the schematic analyzer ran but the PCB file changed, the old PCB output carries forward with stale data.

**Suggested fix:** Compare `source_hashes` in the previous manifest against current hashes before copying forward.

---

## Test Harness Issues

### TH-016: validate_outputs.py and validate_invariants.py can't find outputs (owner/repo path bug)

**Severity:** HIGH
**Discovered:** 2026-04-12 code review (finding C1)
**Where:**
- `validate/validate_outputs.py:253` — `split("/", 1)` produces `["owner", "repo/file"]`, looks up `OUTPUTS_DIR / "schematic" / "owner"` (wrong — should be `"owner/repo"`)
- `validate/validate_invariants.py:167` — same bug

**Root cause:** Path construction splits the repo-relative path with `maxsplit=1`, getting only the owner directory. Should split with `maxsplit=2` to get `[owner, repo, within_repo]` and look up outputs under `owner/repo`. `verify_parser.py:456` has the correct pattern.

---

### TH-017: validate_spice.py iterates flat directory on two-level owner/repo structure

**Severity:** HIGH
**Discovered:** 2026-04-12 code review (finding C2)
**Where:** `validate/validate_spice.py:247-249`

**Root cause:** `sorted(d.name for d in spice_dir.iterdir() if d.is_dir())` lists owner directories, not `owner/repo` pairs. Looks for JSON files in owner dirs, finds nothing, reports 0 checks. `validate_emc.py` correctly uses the two-level pattern.

---

### TH-018: generate_analytics.py glob patterns miss owner/ level

**Severity:** HIGH
**Discovered:** 2026-04-12 code review (finding C3)
**Where:** `tools/generate_analytics.py:39,74,94,155` — 4 glob patterns + wrong `parts[]` indexing

**Root cause:** Glob patterns use `"*" / "*" / "assertions"` (2 levels) but structure is `owner/repo/project/assertions` (3 levels). Reports ~0.3% of actual data. All analytics charts are nearly empty. Also uses `glob.glob` instead of `Path.rglob`.

---

### TH-019: compare.py --all lists owner dirs not owner/repo pairs

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding C4)
**Where:** `regression/compare.py:223`

**Root cause:** `sorted(d.name for d in DATA_DIR.iterdir() if d.is_dir())` lists owner directories. Should use `list_repos()` like every other tool.

---

### TH-020: promote.py only regenerates schematic seed assertions

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding C5)
**Where:** `regression/promote.py:141`

**Root cause:** `generate_for_repo(repo_name, "schematic", ...)` hardcodes schematic. After promoting changes that include PCB/gerber/SPICE/EMC, those types' seed assertions become stale. Should loop `ANALYZER_TYPES`.

---

### TH-021: harness.py _run() doesn't catch TimeoutExpired

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding B1)
**Where:** `harness.py:37`

**Root cause:** `subprocess.run(cmd, timeout=timeout)` without try/except. Timeout crashes the pipeline instead of returning FAIL. `--continue-on-error` can't recover.

---

### TH-022: run_tests.py fragile summary parsing hides failures

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding B2)
**Where:** `run_tests.py:228-254`

**Root cause:** Falls back to `p=1, status="ok"` when summary line doesn't match expected format. A file with 50 tests and 3 failures could appear as "1p 0f" if the output format changes.

---

### TH-023: cleanup_drift.py silently skips items with check fields

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding B3)
**Where:** `regression/cleanup_drift.py:53-65`

**Root cause:** Matches on description substrings like `"now empty/missing"`. Items with explicit check fields have different descriptions (`"check FAILED"`, `"bug appears fixed"`), so they're never matched. The most precisely targeted items are invisible to cleanup.

---

### TH-024: cleanup_drift.py doesn't regenerate findings.md

**Severity:** LOW
**Discovered:** 2026-04-12 code review (finding B4)
**Where:** `regression/cleanup_drift.py:113`

**Root cause:** Writes JSON directly with `fpath.write_text()` instead of calling `save_findings()`. Findings.md not regenerated after modifications.

---

### TH-025: run_pcb.py defaults --jobs to 1, missing --cross-section

**Severity:** MEDIUM
**Discovered:** 2026-04-12 code review (finding B6)
**Where:** `run/run_pcb.py:28-35`

**Root cause:** Manually defines `--repo` and `--jobs` (defaulting to 1) instead of using `add_repo_filter_args()`. Missing `--cross-section`, `--repo-list`, `--resume`, `--validate`, `--json`. Every other runner uses `DEFAULT_JOBS` (cpu_count).

---

## Priority Queue

**Harness bugs (TH-*):**
1. **TH-016** — HIGH — validate_outputs/invariants owner/repo path bug
2. **TH-017** — HIGH — validate_spice flat directory iteration
3. **TH-018** — HIGH — generate_analytics glob depth
4. **TH-025** — MED — run_pcb.py missing --cross-section, --jobs defaults to 1
5. **TH-019** — MED — compare.py --all owner/repo
6. **TH-020** — MED — promote.py schematic-only regeneration
7. **TH-021** — MED — harness.py TimeoutExpired
8. **TH-022** — MED — run_tests.py fragile parsing
9. **TH-023** — MED — cleanup_drift.py check field skip
10. **TH-024** — LOW — cleanup_drift.py missing md regeneration

**Analyzer bugs (KH-*, main-repo owned):**
1. **KH-277** — MED — API key in URL (security)
2. **KH-279** — MED — Formula divide-by-zero guards
3. **KH-278** — MED — GP-001 missing-data reporting
4. **KH-280** — MED — MPN cache collision
5. **KH-281** — MED — Cache stale output copy-forward
6. **KH-276** — LOW — RC filter cutoff_hz=0.0
