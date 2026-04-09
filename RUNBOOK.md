# Test Harness Runbook

20 operational checklists for the kicad-happy test harness. Designed for Claude Code
agents working autonomously or with minimal supervision.

**This is the primary operational reference.** Agents MUST follow the relevant
checklist rather than improvising workflows. If a task doesn't fit any checklist,
follow the closest one and add a new checklist for the pattern afterward.

**Checklists are living documents.** Update them when:
- A new tool or script is added to the harness
- An existing step is found to be wrong or incomplete
- A new workflow pattern is established that should be repeatable
- A step caused a problem and needs to be clarified or expanded

**Prerequisites:** `KICAD_HAPPY_DIR` env var set (or `../kicad-happy` exists), repos
checked out via `python3 checkout.py`, manifests built via `python3 discover.py`.

---

## Checklist 1: Validate a kicad-happy code change

Use when the kicad-happy repo has new or modified analyzer code and you need to verify
it doesn't break anything.

### 1a. Determine what changed

```bash
python3 tools/detect_changes.py --since HEAD~1
```

This tells you which analyzer types are affected and what actions to take. If nothing
changed, stop here.

### 1b. Run affected analyzers

Only re-run the types flagged by `tools/detect_changes.py`. Use `--jobs 16` for speed.

```bash
python3 run/run_schematic.py --jobs 16          # if schematic affected
python3 run/run_pcb.py --jobs 16                # if pcb affected
python3 run/run_gerbers.py --jobs 16            # if gerber affected
python3 run/run_spice.py --jobs 16              # if spice affected
python3 run/run_emc.py --jobs 8                 # if emc affected
```

Add `--repo {repo}` to test a single repo first before full corpus.
Add `--cross-section quick_200` to test a balanced 100-repo subset.
Add `--validate` to check output JSON structure.
All tools auto-parallelize (default `--jobs` = cpu count).

### 1c. Run assertions

```bash
python3 regression/run_checks.py --type {type}
```

Compare pass/fail counts against status.md. Any NEW failures (not pre-existing) are
regressions caused by the code change.

### 1d. Run cross-validation

```bash
python3 validate/validate_spice.py --summary    # if spice affected
python3 validate/validate_emc.py --summary      # if emc affected
python3 validate/cross_analyzer.py --summary    # if schematic or pcb affected
```

### 1e. Check for schema drift

```bash
python3 validate/validate_schema.py diff
```

If new fields appeared, run `auto-seed` to generate assertions for them.

### 1f. File issues for any regressions

See Checklist 5 (Issue Management) below.

### 1g. Audit constants and equations

Run after ANY code change to catch new/changed constants that need verification:

```bash
python3 validate/audit_constants.py scan --diff
python3 validate/audit_equations.py scan --diff
```

If new constants or equations appear, follow Checklist 11 to verify them before
merging. New constants without authoritative sources are a hallucination risk.

### 1h. Update status.md

Record what was tested, pass rates, and any new findings.

---

## Checklist 2: Test a new kicad-happy feature

Use when a new feature (e.g., Monte Carlo, thermal analysis, what-if) has been
implemented and needs end-to-end validation.

### 2a. Nominal regression — verify existing outputs unchanged

```bash
python3 regression/run_checks.py --type schematic
python3 regression/run_checks.py --type pcb
python3 regression/run_checks.py --type spice
python3 regression/run_checks.py --type emc
```

All pass counts must match status.md baselines. If a new feature changes existing
analyzer outputs, the affected assertions may need re-seeding (see Checklist 4).

### 2b. Feature-specific testing

If the kicad-happy agent has written a test plan file (`TODO-{feature}-test-plan.md`),
execute it using **Checklist 17** instead of writing your own.

Otherwise, write or execute a test plan covering:
- Nominal operation (does it work on known-good inputs?)
- Edge cases (empty inputs, missing data, boundary values)
- Corpus smoke test (run on 50+ files, verify zero crashes)
- Output structure validation (expected JSON keys present)

### 2c. Integration testing

If the feature touches `format-report.py` or `entrypoint.sh`:
```bash
python3 $KICAD_HAPPY_DIR/action/format-report.py \
    --schematic {sch.json} --severity all --derating-profile commercial \
    --output /tmp/test_report.md --output-summary /tmp/test_summary.json
```

Verify backward compatibility (old flags still work, new flags are optional).

### 2d. Delete the test plan file when done

Test plan files (`TODO-*-test-plan.md`) are temporary — delete after execution.

---

## Checklist 3: Full corpus health check

Use periodically (e.g., weekly) or before a release to verify overall harness health.

### 3a. Run the health report

```bash
python3 tools/generate_health_report.py --log
```

Check for assertion count drops vs last logged entry. Any WARNING lines indicate
regressions.

### 3b. Check assertion staleness

```bash
python3 regression/check_staleness.py
```

If many assertions are stale (outputs newer than assertions), prune then re-seed:
```bash
python3 regression/seed.py --all --type {type} --prune-stale --dry-run  # preview removals
python3 regression/seed.py --all --type {type} --prune-stale            # remove stale
python3 regression/seed.py --all --type {type}
python3 regression/seed_structural.py --all --type {type}
```

### 3c. Run mutation testing

```bash
python3 validate/mutation_test.py --repo {repo} --type schematic --mutations 100
```

Target: 95%+ catch rate. If lower, assertions for that repo/type are too weak —
re-seed with structural assertions.

### 3d. Check detector coverage

```bash
python3 tools/coverage_detector_map.py
```

Any detector with corpus hits but zero assertions needs attention. Any detector
with zero equations or unverified constants is a risk area.

### 3e. Check cross-analyzer consistency

```bash
python3 validate/cross_analyzer.py --summary
```

Agreement should be >90%. Mismatches by check type indicate systematic issues.

### 3f. Check schema drift

```bash
python3 validate/validate_schema.py auto-seed
```

New fields should get assertions. Removed fields should trigger cleanup of stale
assertion references.

### 3g. Run unit tests

```bash
python3 run_tests.py --unit
```

Must be 100% pass. If not, fix before doing anything else.

---

## Checklist 4: Re-seed assertions after analyzer changes

Use when an analyzer change modifies output structure (new fields, changed counts,
renamed detections) and existing assertions are failing legitimately.

### 4a. Verify the change is correct

Before re-seeding, confirm the new output is correct — not a regression. Read the
diff output, check that counts make sense, verify new fields are populated correctly.

**Common trigger:** New additive rules (e.g., EMC PD-003/PD-004) add findings that
change SEED count assertions. This is expected for additive features — the finding
count increased because new rules fire, not because existing rules broke. Verify the
new findings are correct, then re-seed.

### 4b. Re-run analyzers for affected repos

```bash
python3 run/run_{type}.py --jobs 16
```

### 4c. Snapshot new baselines

```bash
python3 regression/snapshot.py --repo {repo}
```

### 4d. Prune stale seed assertions

```bash
python3 regression/seed.py --all --type {type} --prune-stale --dry-run  # preview
python3 regression/seed.py --all --type {type} --prune-stale            # remove
```

Removes seed assertion files whose outputs no longer meet seeding thresholds
(e.g., sub-sheets with <10 components). Do this BEFORE re-seeding to avoid
re-generating assertions that will immediately be stale again.

### 4e. Re-seed assertions

```bash
python3 regression/seed.py --all --type {type}
python3 regression/seed_structural.py --all --type {type}
```

SEED tolerance scales with count: <50 items →10%, 50-200 →5%, >200 →3%.

### 4f. Regenerate and audit bugfix assertions

```bash
python3 regression/generate_bugfix_assertions.py --apply
python3 regression/audit_bugfix_paths.py
```

The first command ensures BUGFIX-* assertions stay in sync with the bugfix registry.
The second verifies all bugfix assertions resolve to actual output files — any
"unmatched" entries indicate wrong `project` or `source_file` paths in the registry.
Fix them before proceeding.

### 4g. Run assertions to verify 100% pass

```bash
python3 regression/run_checks.py --type {type}
```

### 4h. Promote to reference

```bash
python3 regression/promote.py --repo {repo} --apply
```

### 4i. Update status.md and reset health baseline

```bash
python3 tools/generate_health_report.py --reset-baseline "re-seed after {reason}"
```

This sets the new assertion count as the comparison baseline so the next health
report doesn't flag the intentional count change as a regression.

---

## Checklist 5: Issue management

### Filing a new issue

1. Check `ISSUES.md` "Numbering convention" for the next available number
   - KH-* for kicad-happy analyzer bugs
   - TH-* for test harness infrastructure bugs
2. Add the issue to the appropriate section in ISSUES.md using this exact format:

```markdown
### KH-NNN (SEVERITY): One-line title

- **File**: `path/to/file.py` — `function_name()`
- **Symptom**: What goes wrong
- **Impact**: How many files/repos affected (e.g., "44% of schematic outputs")
- **Discovered**: YYYY-MM-DD during {context}
```

3. Increment the "Next KH/TH number" in the numbering section — update the
   `Next KH number: **KH-NNN**` line (or TH equivalent).
4. Update memory files — update `memory/project_issues_kicad_happy.md` or
   `memory/project_issues_testharness.md` with the new next number and open
   issue count.

### Fixing an issue

1. Fix the bug in the appropriate repo
2. **In the same session:**
   - Remove the issue from ISSUES.md
   - Add it to FIXED.md using this exact format:

```markdown
## YYYY-MM-DD — Batch NN: Short description (KH-NNN)

### KH-NNN (SEVERITY): One-line title

- **File**: `path/to/file.py` — `function_name()`
- **Root cause**: Detailed explanation of WHY it broke
- **Fix**: What was changed (numbered steps if multiple)
- **Verified**: Test results proving the fix (files tested, pass rates, edge cases)
```

3. If in kicad-happy: re-run affected analyzer type, verify assertions pass
4. If a BUGFIX assertion is warranted (prevents regression of a fixed analyzer bug):
   - Add entry to `regression/bugfix_registry.json`
   - Run `python3 regression/generate_bugfix_assertions.py`
5. Update the "Next KH/TH number" in ISSUES.md if it was advanced
6. Update memory files — update `memory/project_issues_kicad_happy.md` or
   `memory/project_issues_testharness.md` with new open issue count and next number.

### Issue severity levels

| Severity | Definition | Action |
|----------|-----------|--------|
| CRITICAL | Cascading failures, major data loss, large portions unusable | Fix immediately |
| HIGH | Significant accuracy impact, many false positives/negatives | Fix before next release |
| MEDIUM | Localized false positives or misclassifications, workarounds exist | Fix when convenient |
| LOW | Cosmetic, minor noise, edge cases affecting few files | Fix opportunistically |

---

## Checklist 6: Testing a single repo end-to-end

Use when adding a new repo to the corpus or deep-diving one repo's results.

**Note on Eagle `.sch` files:** If `discover.py --repo {repo}` finds 0 schematic
files, check whether the repo uses Eagle format. `discover.py` filters legacy `.sch`
files by checking headers for "EESchema" — Eagle XML/binary `.sch` files are excluded
automatically. Adafruit repos are all Eagle format. If the repo is Eagle-only, it is
not suitable for the test corpus.

```bash
REPO=MyNewRepo

# 1. Clone (if new)
python3 checkout.py              # or add URL to repos.md first

# 2. Discover files
python3 discover.py --repo $REPO
# Check output — if 0 files found, verify the repo has KiCad files (not Eagle)

# 3. Run all analyzers (check exit codes after each)
python3 run/run_schematic.py --repo $REPO --jobs 4
# Check: any errors reported? Crashes are potential KH-* bugs.
python3 run/run_pcb.py --repo $REPO --jobs 4
# Check: any errors reported?
python3 run/run_gerbers.py --repo $REPO --jobs 4
# Check: any errors reported?
python3 run/run_spice.py --repo $REPO --jobs 16
# Check: any errors reported?
python3 run/run_emc.py --repo $REPO --jobs 8
# Check: any errors reported?

# 4. Snapshot baselines
python3 regression/snapshot.py --repo $REPO

# 5. Seed assertions
python3 regression/seed.py --repo $REPO
python3 regression/seed_structural.py --repo $REPO

# 6. Run assertions (should be 100% on freshly seeded)
python3 regression/run_checks.py --repo $REPO

# 7. Validate outputs
python3 validate/validate_outputs.py --repo $REPO

# 8. Cross-validate
python3 validate/validate_spice.py --repo $REPO
python3 validate/validate_emc.py --repo $REPO
python3 validate/cross_analyzer.py --repo $REPO

# 9. Promote to reference
python3 regression/promote.py --repo $REPO --apply
```

---

## Checklist 7: Upstream kicad-happy monitoring

Use to stay aware of changes in the kicad-happy repo that affect the test harness.

### 7a. Check what changed

```bash
python3 tools/detect_changes.py --since HEAD~5     # or a specific commit range
```

### 7b. Interpret the output

- **Affected types listed:** These analyzer outputs may have changed
- **Functions changed:** Specific detector or utility functions modified
- **Recommended actions:** Follow them in order

### 7c. Verify constants haven't drifted

```bash
python3 validate/audit_constants.py scan
python3 validate/audit_constants.py corpus
```

If the kicad-happy agent added/changed constants, verify them:
```bash
python3 validate/verify_constants_online.py --limit 10    # spot-check via DigiKey
```

### 7d. Verify the change-impact map is current

```bash
python3 tools/detect_changes.py generate-map
```

Checks whether the hand-maintained file-to-types map in `tools/detect_changes.py` matches
what the import graph says. If divergences are reported, the hand-maintained map may
need updating so that `tools/detect_changes.py` correctly identifies which analyzer types
are affected by future changes.

---

## Checklist 8: Generating negative assertions from findings

Use to improve false-positive prevention after Layer 3 reviews have accumulated.

### 8a. Preview candidates

```bash
python3 regression/seed_negative.py --all --dry-run
```

Review the output — candidates with "explicit" checks are high-quality (they have
machine-verifiable check fields from findings). Candidates with "needs review" are
generated from keyword matching and may need manual validation.

### 8b. Apply (after review)

```bash
python3 regression/seed_negative.py --all --apply
```

This writes `{file}_negative.json` assertion files to `reference/`.

### 8c. Verify they pass

```bash
python3 regression/run_checks.py --type schematic
```

Negative assertions are aspirational — failures indicate the analyzer still has the
false positive (which is the point — tracking known issues).

---

## Checklist 9: SPICE Monte Carlo testing

Use when testing tolerance analysis features or validating MC outputs.

```bash
# Run MC on a specific repo
python3 run/run_spice.py --repo {repo} --jobs 16 \
    --extra-args "--monte-carlo 100 --mc-seed 42"

# Validate MC output structure
python3 -c "
import json, glob
for f in glob.glob('results/outputs/spice/{repo}/*.json'):
    data = json.load(open(f))
    for r in data.get('simulation_results', []):
        ta = r.get('tolerance_analysis')
        if ta:
            print(f'{r[\"subcircuit_type\"]}: {ta[\"n_converged\"]}/{ta[\"n_samples\"]} converged')
"

# IMPORTANT: Restore nominal outputs after MC testing
python3 run/run_spice.py --repo {repo} --jobs 16
```

MC args: `--monte-carlo N` (trials), `--mc-seed S` (reproducibility),
`--mc-distribution uniform|gaussian`.

---

## Checklist 10: Session wrap-up

Do these at the end of every testing session.

### 10a. Run unit tests

```bash
python3 run_tests.py --unit
```

Must be 270/270 passed. If not, fix before ending.

### 10b. Update documentation

- **status.md** — Add batch entry with what was tested, pass rates, findings
- **ISSUES.md** — File any new issues found, remove any fixed
- **FIXED.md** — Add details for any issues fixed this session
- **TODO-test-improvements.md** — Mark completed items, add new ideas (local file, not git-tracked)

### 10c. Update RUNBOOK.md

If any new workflow pattern was established during the session, add or update a
checklist in this file. Checklists should stay current with actual practice — don't
let the runbook drift from reality.

### 10d. Update memory files if project state changed

Update the relevant memory files under
`~/.claude/projects/-home-aklofas-Projects-kicad-happy-testharness/memory/`:

- **`project_implementation_status.md`** — if assertion counts, unit test counts, or
  corpus size changed significantly
- **`project_issues_kicad_happy.md`** — if KH-* issues were filed or fixed (update
  open count and next number)
- **`project_issues_testharness.md`** — if TH-* issues were filed or fixed
- **`project_repo_expansion.md`** — if repos were added to or removed from the corpus
- **`project_layer3_status.md`** — if Layer 3 reviews were conducted

### 10e. Log health metrics

```bash
python3 tools/generate_health_report.py --log
```

### 10f. Review uncommitted changes

All changes are uncommitted until the user explicitly requests a commit. List what
changed so the user can review:
```bash
git status
git diff --stat
```

---

## Checklist 11: Constants and equations — hallucination prevention

The kicad-happy analyzers contain 292 hardcoded constants (Vref lookup tables, switching
frequencies, component classification keywords, risk scoring weights) and 86 engineering
equations (radiation formulas, impedance calculations, filter frequencies). These are the
highest-risk areas for hallucinated values — an LLM that adds a wrong Vref silently
produces incorrect voltage calculations for every design using that part.

### 11a. Scan for new or changed constants

Run after ANY change to kicad-happy analyzer scripts:

```bash
python3 validate/audit_constants.py scan --diff
```

This AST-scans all analyzer scripts and reports:
- **New constants** — added since last scan. MUST be verified before merging.
- **Changed constants** — content hash differs. Review what changed and why.
- **Removed constants** — may indicate cleanup or regression. Verify intentional.

If new constants are found:
```bash
python3 validate/audit_constants.py list --unverified    # show all unverified
python3 validate/audit_constants.py show CONST-XXX       # detail view of specific constant
```

### 11b. Verify new constants against authoritative sources

**Every new constant MUST have a verification source.** Acceptable sources:

| Source type | Example | Reliability |
|-------------|---------|-------------|
| Manufacturer datasheet | "TI TPS5430 datasheet SLVS632L, Table 7.5" | Highest |
| Distributor parametric | "DigiKey parametric data for TPS5430" | High |
| Industry standard | "IPC-2221B Table 6-1" | High |
| Textbook | "Ott, EMC Engineering (Wiley 2009) Eq. 6.4" | High |
| Application note | "Murata MLCC app note, Table 3" | Medium |
| Self-evident physics | "Ohm's law: V = IR" | N/A (auto-verified) |
| Engineering heuristic | "Empirical threshold from corpus tuning" | Low — document rationale |

**DO NOT accept:** LLM training data, "common knowledge", values without citation,
round numbers that look plausible but have no source.

To verify a constant:
```bash
python3 validate/audit_constants.py verify CONST-XXX --source "TI datasheet SLVS632L"
python3 validate/audit_constants.py verify CONST-XXX --entry TPS5430 --source "datasheet Table 7.5"
```

### 11c. Automated verification via DigiKey API

For constants with part-number-keyed entries (Vref tables, switching frequencies,
quiescent currents):

```bash
python3 validate/verify_constants_online.py --dry-run    # preview what will be checked
python3 validate/verify_constants_online.py --limit 20   # check 20 entries against DigiKey
python3 validate/verify_constants_online.py --constant _REGULATOR_VREF  # one constant only
```

This queries DigiKey parametric data and compares stored values. Review mismatches
carefully — the MPN prefix may match a different variant than intended.

**Currently verifiable constants (102 entries across 3 tables):**
- `_REGULATOR_VREF` — 65 entries (reference voltages for TI/ST/ADI/Diodes/Maxim parts)
- `known_freqs` — 21 entries (switching frequencies)
- `_iq_estimates_uA` — 16 entries (quiescent currents)

### 11d. Cross-reference constants against the corpus

```bash
python3 validate/audit_constants.py corpus
```

This scans all analyzer outputs to determine which constant entries are actually
exercised by the test corpus. Flags:
- **Unused entries** — entries that never fire across 5,829 repos. May be dead weight
  or may indicate the constant was added for a specific project not in the corpus.
- **Low-hit entries** — entries exercised by <3 repos. Harder to validate empirically.
- **High-hit entries** — entries exercised by 100+ repos. High confidence if verified.

### 11e. Scan for new or changed equations

```bash
python3 validate/audit_equations.py scan --diff
```

Reports new EQ tags, changed function bodies (detected via AST hash), and missing tags.

### 11f. Verify new equations

Each equation needs an `# EQ-NNN:` comment tag in the source with:
1. The formula in symbolic form
2. At least one authoritative source citation

```python
# EQ-042: Ztrack = sqrt(L/C) (microstrip characteristic impedance)
# Source: Pozar "Microwave Engineering" (Wiley, 2012) Eq. 3.197
# Source: IPC-2141A Section 4.2.1
```

To verify:
```bash
python3 validate/audit_equations.py verify EQ-042 --source "Pozar Eq. 3.197"
```

### 11g. Find untagged equations

```bash
python3 validate/audit_equations.py untagged
```

Uses heuristics (presence of `math.sqrt`, `math.pi`, `**2`, `math.log`, etc.) to find
functions with engineering math that lack `# EQ-NNN:` tags. These are risks — the
formula may be correct but without a tag it can't be tracked or verified.

### 11h. Risk assessment

```bash
python3 validate/audit_constants.py list --risk critical   # most dangerous constants
python3 validate/audit_constants.py list --risk high       # second tier
python3 validate/audit_constants.py stats                  # overall risk breakdown
```

Risk scoring combines two axes:
- **Impact** (0.0-1.0) — how bad is it if wrong? Vref values = high, format codes = low.
- **Overfit** (0.0-1.0) — was it added for one project or does it generalize?

A fully verified high-impact constant drops to low risk. An unverified high-impact
constant is critical risk regardless of how many repos exercise it.

### 11i. When to remove vs verify

If a constant cannot be verified from an authoritative source:
- **Remove it** if the analyzer can function without it (use a generic fallback)
- **Flag it** in the registry as `unverified` with a note explaining why
- **Never leave a hallucinated value** — it's better to use a conservative default
  than an incorrect specific value

### 11j. Periodic audit (do monthly or before releases)

```bash
# Full audit pipeline
python3 validate/audit_constants.py scan                   # refresh registry
python3 validate/audit_constants.py corpus                 # refresh corpus hits
python3 validate/audit_constants.py list --unverified      # anything still unverified?
python3 validate/audit_constants.py list --risk critical    # anything critical-risk?
python3 validate/verify_constants_online.py --limit 20     # spot-check against DigiKey
python3 validate/audit_equations.py scan                   # refresh equation registry
python3 validate/audit_equations.py list --unverified      # any unverified equations?
python3 validate/audit_equations.py untagged               # any untagged math?
python3 validate/audit_constants.py render                 # regenerate markdown summary
python3 validate/audit_equations.py render                 # regenerate equation summary
```

---

## Checklist 12: Investigating an assertion failure

Use when `run_checks.py` reports failures. The goal is to determine: is this a real
regression, a stale assertion, or an intentional improvement?

### Decision tree

```
Assertion failed
  │
  ├─ Was the analyzer recently changed?
  │    ├─ YES → Does the new output look correct?
  │    │          ├─ YES → Assertion is stale. Re-seed (Checklist 4).
  │    │          └─ NO  → Real regression. File KH-* issue (Checklist 5).
  │    └─ NO  → Was the test repo recently updated?
  │              ├─ YES → Re-run analyzer, re-seed if output changed.
  │              └─ NO  → Possible intermittent bug. Investigate.
  │
  ├─ Is the failure in a SEED assertion (count-based)?
  │    └─ Check: did the count change slightly (within old tolerance)?
  │         ├─ YES → Tolerance tightened (QW4). Count is correct. Re-seed.
  │         └─ NO  → Significant count change. Investigate root cause.
  │
  ├─ Is the failure in a STRUCT assertion (specific ref)?
  │    └─ Check: does the ref still exist in the output?
  │         ├─ YES but in a different detector → Reclassification. Review.
  │         └─ NO  → Detection dropped. Likely regression. Investigate.
  │
  ├─ Is the failure in an FND assertion (aspirational)?
  │    └─ Aspirational failures are expected. Check if the finding's
  │       underlying issue was fixed — if so, flip aspirational→required.
  │
  └─ Is the failure in a BUGFIX assertion?
       └─ BUGFIX failures are always regressions. The fixed bug has returned.
          File a new KH-* issue referencing the original.
```

### 12a. Quick diagnosis

```bash
# See which assertions failed
python3 regression/run_checks.py --repo {repo} --type {type} 2>&1 | grep "FAIL"

# Check if the output file is valid
python3 -c "import json; json.load(open('results/outputs/{type}/{repo}/{file}.json'))"

# Compare output against baseline
python3 regression/compare.py --repo {repo}
```

### 12b. If re-seeding is the right call

Only re-seed if you've confirmed the new output is correct:

```bash
python3 regression/seed.py --repo {repo} --type {type}
python3 regression/seed_structural.py --repo {repo} --type {type}
python3 regression/run_checks.py --repo {repo} --type {type}   # verify 100%
python3 regression/promote.py --repo {repo} --apply
```

### 12c. If it's a real regression

```bash
# Get the assertion details
python3 regression/run_checks.py --repo {repo} --type {type} --json > /tmp/failures.json
# File an issue (see Checklist 5)
# After fixing, add a BUGFIX assertion to prevent recurrence
```

---

## Checklist 13: Layer 3 — LLM review workflow

Layer 3 uses Claude to review analyzer outputs against source files, discovering
semantic issues that assertions can't catch (wrong detection, missed circuit, incorrect
parameter values).

### 13a. Generate review packets

```bash
# Random selection (good for broad coverage)
python3 regression/packet.py --strategy random --count 5

# Changed repos (good after analyzer updates)
python3 regression/packet.py --strategy changed --repo {repo} --count 3

# Specific file
python3 regression/packet.py --file results/outputs/schematic/{repo}/{file}.json
```

Review packets are written to `results/review_packets/`. Each pairs the source KiCad
file with the analyzer output summary for side-by-side review.

### 13b. Conduct the review

Use `batch_review.py` with Claude Code subagents:

```bash
# List unreviewed repos by complexity
python3 tools/batch_review.py list --count 20

# Generate prompts for N repos
python3 tools/batch_review.py prompts --count 10
```

In a Claude Code session, spawn subagents in parallel with each prompt. Each
subagent reads the source schematic + analyzer JSON and produces a JSON finding.
Launch 3-5 subagents in parallel to maximize throughput.

### 13c. Save findings

Save each subagent's JSON output:

```bash
python3 tools/batch_review.py save --repo {owner/repo} --project {project} --file /tmp/finding.json

# View findings
python3 regression/findings.py list --repo {repo}
python3 regression/findings.py stats
```

Each finding item should have:
- `description` — what was found
- `analyzer_section` — which part of the output is affected
- `status` — `confirmed`, `incorrect`, `missed`, `observation`

### 13d. Auto-generate check fields

```bash
python3 regression/generate_finding_checks.py --repo {repo} --dry-run
python3 regression/generate_finding_checks.py --repo {repo} --apply
```

This adds machine-checkable `check` fields to finding items, enabling automated
drift detection and assertion promotion.

### 13e. Promote findings to assertions

```bash
# Promote a specific finding
python3 regression/findings.py promote FND-00000001

# Promote all eligible findings for a repo
python3 regression/promote.py --repo {repo} --apply
```

Promoted findings become FND-* assertions. Items with `incorrect` tags become
candidates for negative assertions (see Checklist 8).

### 13f. Detect drift

```bash
python3 regression/drift.py --repo {repo}
```

Compares current outputs against finding expectations. Surfaces:
- **Regressions** — something that was correct is now wrong
- **Improvements** — something that was wrong is now correct
- **Possibly fixed** — an `incorrect` item that may have been addressed

### 13g. Clean up stale drift

```bash
python3 regression/cleanup_drift.py
```

Removes drift items from findings that reference outputs no longer present.

---

## Checklist 14: Adding a new repo to the corpus

### 14a. Find the repo

Good candidates:
- Real hardware projects (not tutorials or templates)
- Multiple schematic sheets with analog + digital circuits
- Has a PCB layout (not schematic-only)
- KiCad 5-9 (not Eagle, Altium, or other EDA)
- Open source with a permissive license

### 14b. Add to repos.md

Edit `repos.md` directly. The exact format is:
```
- https://github.com/user/repo @ 40char_commit_hash
- https://github.com/user/large-repo @ 40char_commit_hash (shallow)
```

**Format rules:**
- Every entry must have a `@ 40char_hash` commit pin for reproducibility
- Use `(shallow)` suffix for repos >100MB — all repos use `--depth 1` shallow clones
- The URL must be the full GitHub HTTPS URL
- One repo per line, prefixed with `- `

### 14c. Clone and discover

```bash
python3 checkout.py
python3 discover.py --repo {repo}
```

Verify KiCad files were found. If the repo uses Eagle `.sch` files, they'll be
filtered out automatically.

**Eagle disambiguation:** If `discover.py` finds 0 schematic files for a repo that
you know has `.sch` files, the repo likely uses Eagle format (not KiCad). Check the
file header — KiCad legacy `.sch` files start with "EESchema", while Eagle files are
XML or binary. Adafruit repos are all Eagle format. If the repo is Eagle-only, remove
it from `repos.md` — it is not suitable for the test corpus.

### 14d. Run full analysis pipeline

```bash
python3 run/run_schematic.py --repo {repo} --jobs 4
python3 run/run_pcb.py --repo {repo} --jobs 4
python3 run/run_gerbers.py --repo {repo} --jobs 4
python3 run/run_spice.py --repo {repo} --jobs 16
python3 run/run_emc.py --repo {repo} --jobs 8
```

Check for script errors. Any crashes are potential bugs — file as KH-* issues.

### 14e. Validate outputs

```bash
python3 validate/validate_outputs.py --repo {repo}
python3 validate/validate_spice.py --repo {repo}
python3 validate/validate_emc.py --repo {repo}
python3 validate/cross_analyzer.py --repo {repo}
```

### 14f. Snapshot and seed assertions

```bash
python3 regression/snapshot.py --repo {repo}
python3 regression/seed.py --repo {repo}
python3 regression/seed_structural.py --repo {repo}
python3 regression/run_checks.py --repo {repo}    # should be 100%
```

### 14g. Promote to reference

```bash
python3 regression/promote.py --repo {repo} --apply
```

### 14h. Update tracking

- Add to priority.md in the appropriate complexity tier
- Update corpus count in status.md
- Update `memory/project_repo_expansion.md` with the new repo count

---

## Checklist 15: Adding a new analyzer type

Use when a new analyzer (e.g., `analyze_thermal.py`) is added to kicad-happy and needs
test harness integration. This is a multi-step process that touches many files.

### 15a. Create the batch runner

Create `run/run_{type}.py` following the pattern in `run/run_emc.py`:
- Parse `--repo`, `--jobs` arguments
- Find inputs (usually from another analyzer's outputs)
- Run the analyzer subprocess per file
- Collect aggregate stats and write `_aggregate.json`
- Include timing instrumentation (per-file elapsed, `_timing.json`)

**Note:** Some analyzers require multiple input types. For example,
`analyze_thermal.py` requires both `--schematic` and `--pcb`. The batch runner
must find matching pairs of outputs (use stem matching like `run_emc.py`'s
`find_pcb_output()`), not just iterate one type.

### 15b. Register the type

In `utils.py`, add to `ANALYZER_TYPES`:
```python
ANALYZER_TYPES = ["schematic", "pcb", "gerber", "spice", "emc", "datasheets", "{type}"]
```

### 15c. Add output validation

In `utils.py`, add expected keys to `EXPECTED_KEYS`:
```python
EXPECTED_KEYS = {
    ...
    "{type}": {"findings", "summary"},  # adjust for actual output structure
}
```

### 15d. Create assertion generators

Add `generate_{type}_assertions()` in `regression/seed.py`:
- Count-based assertions for top-level statistics
- Detection-specific assertions for key output sections

Add structural assertions in `regression/seed_structural.py` if the output has
per-component or per-detection data.

### 15e. Add to run_checks.py

The `--type` choices in `regression/run_checks.py` come from `ANALYZER_TYPES`, so
this should work automatically after step 15b.

### 15f. Create a cross-validator (if applicable)

If the new analyzer consumes data from other analyzers, add cross-validation:
- In `validate/cross_analyzer.py`: add a `cross_validate_{type}()` function and
  update `find_paired_outputs()` to locate the new output type's files
- Or create `validate/validate_{type}.py` following the pattern in `validate_emc.py`

### 15g. Add to schema inventory

In `validate/validate_schema.py`, add the new type's sections to the scan functions
so schema drift detection covers the new output format.

### 15h. Add to coverage detector map

Update the `DETECTORS` list in `tools/coverage_detector_map.py` to include any new
detectors introduced by this analyzer type, so they appear in coverage reports.

### 15i. Run full corpus and seed

```bash
python3 run/run_{type}.py --jobs 16
python3 regression/seed.py --all --type {type}
python3 regression/seed_structural.py --all --type {type}
python3 regression/run_checks.py --type {type}
```

### 15j. Write unit tests

Create `tests/test_{type}.py` with at minimum:
- Seed assertion generation from synthetic data
- Structural assertion generation
- Cross-validation function tests (if applicable)

Target: 20+ tests per analyzer type.

### 15k. Create sidecar documentation

Create `{type}.md` sidecar documentation explaining:
- What the analyzer does and how it works
- Input requirements (which other analyzer outputs it reads)
- Output format (JSON structure, key fields)
- Known limitations and edge cases

### 15l. Update documentation

- `CLAUDE.md` — add to directory structure, running commands, regression section
- `README.md` — add to analyzers table, directory structure, validation commands
- `RUNBOOK.md` — mention in relevant checklists
- `status.md` — add corpus summary section for the new type

### 15m. Audit constants and equations

```bash
python3 validate/audit_constants.py scan     # picks up new constants automatically
python3 validate/audit_equations.py scan     # picks up new EQ tags automatically
```

Verify all new constants and equations per Checklist 11.

---

## Checklist 16: Preparing for a kicad-happy release

Full validation sequence before tagging a release. This is the most comprehensive
check — it covers everything.

### 16a. Pre-flight checks

```bash
# Unit tests (must be 100%)
python3 run_tests.py --unit

# Check for open issues
cat ISSUES.md   # should show "No open issues"

# Check upstream changes since last release
python3 tools/detect_changes.py --since {last_release_tag}
```

### 16b. Full corpus analyzer run

Run ALL analyzer types on the full corpus:

```bash
python3 run/run_schematic.py --jobs 16
python3 run/run_pcb.py --jobs 16
python3 run/run_gerbers.py --jobs 16
python3 run/run_spice.py --jobs 16
python3 run/run_emc.py --jobs 8
```

Check all exit 0. Note any error counts.

**Thermal analysis:** No batch runner exists yet. Thermal is validated via the
integration test path (Checklist 2c: `format-report.py --thermal`). If a
`run_thermal.py` batch runner is added, include it here (see Checklist 15).

### 16c. Full assertion suite

```bash
python3 regression/run_checks.py --type schematic
python3 regression/run_checks.py --type pcb
python3 regression/run_checks.py --type gerber
python3 regression/run_checks.py --type spice
python3 regression/run_checks.py --type emc
```

Record pass/fail counts. Compare against status.md baselines. Any NEW failures
must be investigated before release.

### 16d. Cross-validation

```bash
python3 validate/validate_spice.py --summary
python3 validate/validate_emc.py --summary
python3 validate/cross_analyzer.py --summary
```

Agreement rates should match or exceed status.md baselines.

### 16e. Full validation pipeline

```bash
python3 harness.py validate
```

This runs the orchestrated validation suite including output validation, schema
checks, cross-validation, and structural checks. For a faster pre-check during
development, use `python3 harness.py validate --cross-section smoke`.

### 16f. Constants and equations audit

```bash
python3 validate/audit_constants.py scan --diff
python3 validate/audit_constants.py list --unverified
python3 validate/audit_constants.py list --risk critical
python3 validate/audit_equations.py scan --diff
python3 validate/audit_equations.py list --unverified
```

No critical-risk unverified constants. No untagged equations in changed files.

### 16g. Schema inventory refresh

```bash
python3 validate/validate_schema.py scan
```

Refresh the schema inventory to capture any new output fields introduced since
the last release. Review for unexpected field additions or removals.

### 16h. Verify bugfix coverage

```bash
python3 regression/audit_bugfix_coverage.py
```

Ensure all closed KH-* issues have corresponding BUGFIX-* assertions in the
regression suite. Any gaps mean a fixed bug could silently return.

### 16i. Quality assurance

```bash
python3 validate/mutation_test.py --repo {high-complexity-repo} --type schematic --mutations 100
python3 validate/cross_analyzer.py --summary
python3 tools/coverage_detector_map.py --uncovered-only
python3 regression/check_staleness.py --type schematic
```

Mutation catch rate >95%. No detectors with hits but zero assertions.

**v1.1 tool smoke tests** — verify standalone tools don't crash on corpus data:

```bash
# What-if smoke test (20 files, change a resistor, verify no crashes)
python3 -c "
import subprocess, glob, json, sys
errors = 0
for f in sorted(glob.glob('results/outputs/schematic/*/*.json'))[:20]:
    data = json.load(open(f))
    r = next((c['reference'] for c in data.get('components', [])
              if c.get('reference', '').startswith('R')
              and isinstance(c.get('parsed_value'), (int, float, dict))), None)
    if r:
        result = subprocess.run([sys.executable,
            '$KICAD_HAPPY_DIR/skills/kicad/scripts/what_if.py', f, f'{r}=4.7k'],
            capture_output=True, timeout=10)
        if result.returncode != 0 and 'cannot parse' not in result.stderr:
            errors += 1
print(f'What-if smoke: {errors} errors')
"

# Diff smoke test (20 files, self-diff, verify no crashes)
python3 -c "
import subprocess, glob, sys
errors = 0
for f in sorted(glob.glob('results/outputs/schematic/*/*.json'))[:20]:
    result = subprocess.run([sys.executable,
        '$KICAD_HAPPY_DIR/skills/kicad/scripts/diff_analysis.py', f, f],
        capture_output=True, timeout=10)
    if result.returncode not in (0, 1):
        errors += 1
print(f'Diff smoke: {errors} errors')
"
```

### 16j. Health report

```bash
python3 tools/generate_health_report.py --log
```

No assertion count drops. Record the metrics for release notes.

### 16k. Update documentation

- `status.md` — add release entry with all metrics
- `ISSUES.md` — verify all known bugs are filed (check aspirational FND failures)
- `FIXED.md` — all issues fixed this cycle are documented

```bash
# Regenerate VALIDATION.md for the kicad-happy repo
python3 tools/generate_catalog.py                    # refresh catalog first
python3 tools/generate_validation_md.py --output $KICAD_HAPPY_DIR/VALIDATION.md
```

Review the generated file — check assertion counts, issue ranges, and detector
coverage look correct. Commit in kicad-happy (do NOT push — user manages that).

### 16l. Tag the release

Record alongside the tag:
- kicad-happy commit hash
- Assertion counts by type
- Pass rates for each analyzer
- Corpus size
- Unit test count
- Cross-validation agreement rates

---

## Checklist 17: Executing a test plan from the kicad-happy agent

The kicad-happy agent writes test plans as `TODO-{feature}-test-plan.md` files in the
testharness root. These are temporary files — execute the plan, report results, then
delete the file.

### 17a. Read and understand the test plan

```bash
cat TODO-{feature}-test-plan.md
```

Before executing, understand:
- What feature is being tested (source files, what changed)
- How many phases the plan has
- What pass criteria each phase defines
- Whether any phases require specific repos, API credentials, or tools (e.g., ngspice)

### 17b. Check prerequisites

- Does the feature script exist? (`ls $KICAD_HAPPY_DIR/skills/*/scripts/{script}.py`)
- Are required analyzer outputs present? (check `results/outputs/`)
- If the plan mentions `--extra-args` or similar passthrough, does `run_spice.py` support it?
  If not, add it (or invoke the script directly).
- Select test repos: pick repos with good subcircuit diversity and matching output types.
  Check `results/outputs/{type}/` for repos with actual data.

### 17c. Create task list

Create tasks for each phase. This helps track progress and gives the user visibility:

```
Phase 1: Nominal regression
Phase 2: {feature-specific test}
Phase 3: ...
```

### 17d. Execute phases in order

For each phase:
1. Mark the task as `in_progress`
2. Run the commands from the test plan
3. Check pass criteria — all assertions in the plan must pass
4. If a phase fails, investigate before moving on:
   - Is it a bug in the new feature? Note it for the report.
   - Is it a test plan error (wrong assumption, bad test data)? Adapt and continue.
   - Is it a pre-existing issue? Note it separately.
5. Mark the task as `completed` with a short result summary

### 17e. Restore outputs if test modified them

Some test plans (e.g., Monte Carlo) overwrite standard outputs with test-specific data.
After testing, restore nominal outputs:

```bash
python3 run/run_spice.py --repo {repo} --jobs 16    # restore non-MC outputs
```

Clean up any temp files created during testing:
```bash
rm -rf /tmp/{test_dirs}
```

### 17f. File issues for any bugs found

Check ISSUES.md for the next available number, then:

- **KH-*** for bugs in kicad-happy analyzer code (the feature being tested)
- **TH-*** for bugs in test harness infrastructure

Each issue must include: file, symptom, impact, reproduction steps, discovered date.
See Checklist 5 for the full issue management protocol.

If the kicad-happy agent fixes a bug you found, and you verify the fix in a later test
plan, move it from ISSUES.md to FIXED.md in the same session.

### 17g. Write a detailed summary for the kicad-happy agent

After all phases complete, the user will ask you to write a detailed summary for the
kicad-happy agent. This is a critical deliverable — the other agent uses it to fix
bugs, understand test coverage, and decide whether to merge. Write it as a standalone
document that makes sense without conversation context.

**Required sections:**

1. **Header** — feature name, test date, source files tested
2. **Overall verdict** — "All N phases passed" or "N-1 passed, 1 failed"
3. **Per-phase results table** — phase name, PASS/FAIL/SKIPPED, key metrics (numbers,
   percentages, counts). Be specific — "100% catch rate" not "tests passed"
4. **Per-phase detail** — for each phase, a subsection with:
   - What was tested (setup, inputs, expected behavior)
   - Actual results (exact values, not summaries)
   - Why it passed or failed
5. **Bugs found** (if any) — for each bug:
   - File path and line number
   - Root cause explanation (WHY it breaks, not just WHAT breaks)
   - Severity and impact (what % of corpus is affected)
   - Exact error message or traceback
   - Specific repos/files that trigger it
   - Suggested fix with code example
   - How many corpus files would be affected by the fix
6. **Observations** that aren't bugs — edge cases, accuracy notes, performance data,
   things that could be improved but aren't broken
7. **Conclusion** — one paragraph confirming feature readiness or listing blockers

**Quality bar:** The summary should be detailed enough that the kicad-happy agent can
fix any bugs without needing to reproduce the test themselves. If you found a crash,
include the full traceback. If a value was wrong, include expected vs actual. If a
pattern affects many files, include the corpus-wide count.

### 17h. Write test results file

Write a detailed `TEST-{feature}-{date}.md` file with:

1. **Header** — feature name, test date, kicad-happy commit, verdict
2. **Features tested** — bullet list of what was covered
3. **Phase results table** — phase, what, PASS/FAIL/SKIP, key metrics
4. **Phase details** — per-phase subsections with exact values, not summaries
5. **Bugs found** — full details per Checklist 17g format, or "None"
6. **Observations** — non-bug notes (edge cases, coverage gaps, performance)

The filename mirrors the test plan: replace `TODO-` with `TEST-`. For example,
`TODO-v1.2-engine-features-test-plan.md` becomes `TEST-v1.2-engine-features-test-plan.md`.

Test result files are **committed to git** — they serve as permanent records of
what was tested and what was found. Unlike test plan files (TODO-*), they persist.

### 17i. Delete the test plan file

Test plan files are temporary. Delete after execution:

```bash
rm TODO-{feature}-test-plan.md
```

### 17j. Update documentation if needed

If the test plan required harness changes (e.g., adding `--extra-args` to a runner):
- Update CLAUDE.md directory structure and running commands
- Update RUNBOOK.md if a new operational pattern was established
- Update status.md with the test session results
- Update ISSUES.md / FIXED.md as appropriate

### 17k. Update memory files

If the session changed project state (assertion counts, issue tracker numbers,
implementation status), update the relevant memory files under
`~/.claude/projects/-home-aklofas-Projects-kicad-happy-testharness/memory/`:

- **`project_implementation_status.md`** — assertion counts, unit test counts, corpus size
- **`project_issues_kicad_happy.md`** — open KH-* count and next number
- **`project_issues_testharness.md`** — open TH-* count and next number
- **`project_layer3_status.md`** — if Layer 3 reviews were part of the test plan

---

## Checklist 18: Datasheet workflow

The datasheet pipeline has three phases with different automation levels. Use this
checklist when downloading, extracting, or validating datasheets for the test corpus.

### 18a. Check prerequisites

Ensure DigiKey API credentials are set:
```bash
echo $DIGIKEY_CLIENT_ID       # must be non-empty
echo $DIGIKEY_CLIENT_SECRET   # must be non-empty
```

If not set, obtain credentials from the DigiKey API portal and export them in your
shell profile. Datasheet downloading will fail without valid credentials.

### 18b. Download datasheets

```bash
python3 run/run_datasheets.py --repo {repo} --download-only
```

This uses the DigiKey API to download PDFs for all ICs found in schematic outputs.
PDFs are stored in `repos/{repo}/datasheets/` (git-ignored). The downloader is
idempotent — re-running skips already-downloaded files.

For bulk downloading across multiple repos:
```bash
python3 run/run_datasheets.py --jobs 4 --download-only
```

### 18c. Extraction (interactive only)

Structured data extraction from PDFs is done by Claude reading PDF pages during a
kicad skill session. This is NOT automated in batch because it requires LLM inference
(a Claude Code session, not API calls).

When the kicad skill reviews a project, it reads datasheets and caches extractions in
`datasheets/extracted/`. Extraction coverage grows incrementally over time as projects
are reviewed in Claude Code sessions.

**Do not attempt to automate this step** — it requires interactive Claude sessions.

### 18d. Validate extractions

```bash
python3 run/run_datasheets.py --repo {repo} --validate-only
```

This scores existing extractions for completeness and checks for staleness. Reports
are written to `results/outputs/datasheets/`. Review for:
- Low extraction scores (incomplete data)
- Stale extractions (datasheet PDF updated since extraction)
- Missing fields (required data not captured)

### 18e. Check MPN coverage

```bash
python3 validate/extract_mpns.py --repo {repo}
```

Reports which manufacturer part numbers were found in schematic outputs and whether
datasheets exist for them. Low coverage indicates more downloading is needed.

### 18f. Validate MPNs

```bash
python3 validate/validate_mpns.py --limit 50
```

Validates extracted MPNs against distributor APIs (DigiKey, Mouser) to confirm they
are real parts with correct manufacturer attribution. Use `--limit` to control API
call volume.

---

## Checklist 19: Testing a new domain-specific detector

Use when a new signal detector (e.g., `adc_signal_conditioning`) is added to
kicad-happy's `signal_detectors.py`. The harness auto-discovers new detectors
from outputs — no code changes needed for basic seeding. But field-level quality
assertions require a spec entry.

### 19a. Run full schematic batch

```bash
python3 run/run_schematic.py --jobs 16
```

Verify 0 crashes. Check the Detector Summary at the end — the new detector should
appear with corpus hit counts.

### 19b. Check field distributions

```bash
python3 validate/detector_dashboard.py --detector {name}
```

Review field presence %, enum value distributions, and numeric ranges. Flag any
unexpected values or low-presence required fields.

### 19c. Verify auto-seeding works

```bash
python3 regression/seed.py --all --type schematic --dry-run | grep {name}
```

Should show `min_count` assertions being generated for the new detector.

### 19d. Add field spec (if the detector has structured fields)

Edit `regression/seed.py` — add an entry to `_DETECTOR_FIELD_SPECS`:

```python
_DETECTOR_FIELD_SPECS["{name}"] = {
    "required_fields": ["ref", "type"],
    "enum_fields": {"type": ["value1", "value2"]},
}
```

### 19e. Re-seed with field-level quality assertions

```bash
python3 regression/seed.py --all --type schematic
python3 regression/run_checks.py --type schematic   # verify 100%
```

### 19f. Update schema inventory

```bash
python3 validate/validate_schema.py scan
```

### 19g. Run EMC batch (if detector output affects EMC)

```bash
python3 run/run_emc.py --jobs 16
python3 regression/run_checks.py --type emc
```

---

## Checklist 20: Corpus expansion

Use when expanding the corpus by searching for new KiCad repos on GitHub and adding
them in bulk. This automates the Checklist 14 pipeline at scale.

### 20a. Search for candidates

Run the discovery script. For GitHub only (default):

```bash
python3 tools/search_repos.py --all
```

For all platforms (GitHub + GitLab + Codeberg):

```bash
python3 tools/search_repos.py --source all
```

Or individual platforms:

```bash
python3 tools/search_repos.py --source gitlab
python3 tools/search_repos.py --source codeberg
```

GitHub uses code search (size-sharded `extension:kicad_sch`), topic search
(`topic:kicad fork:false`), and keyword search. GitLab and Codeberg use their
public REST APIs. All strategies deduplicate against repos.md automatically.
Writes `results/candidates.json`.

**Estimated time:** GitHub ~10 minutes (rate-limited at 30 req/min), GitLab ~2 min,
Codeberg ~30 seconds. Bitbucket requires auth (not supported).

Review `candidates.json`: check total count, category distribution, and spot-check
a few entries for quality.

### 20b. Validate candidates

Clone each candidate into a temp directory, check for KiCad files, count
components, score quality, then delete the clone. This filters out tools,
libraries, trivial repos, and repos without actual KiCad files.

```bash
python3 tools/validate_candidates.py --jobs 8
python3 tools/validate_candidates.py --jobs 8 --min-components 10   # stricter
python3 tools/validate_candidates.py --jobs 8 --min-score 30        # quality filter
```

This writes `results/validated.json` with only repos that pass. Expect
~20-40% pass rate depending on the source (code-confirmed repos pass at
higher rates than topic/keyword repos).

**Estimated time:** ~3 seconds per repo. 11,000 candidates at --jobs 8 ~ 1 hour.

Use `--resume` to continue after interruption. Use `--limit 100` to test
a sample first and check the pass rate before committing to the full run.

### 20c. Add repos in batches

```bash
python3 tools/add_repos.py --input results/validated.json --batch-size 50
python3 tools/add_repos.py --input results/validated.json --batch-size 50 --skip-spice --skip-emc
```

This runs the full Checklist 14 pipeline for each candidate:
1. Get HEAD hash via `git ls-remote`
2. Append to repos.md under the auto-assigned category
3. Clone via checkout.py
4. Discover files via discover.py
5. Run schematic + PCB + gerber analyzers
6. Snapshot baselines to reference/
7. Seed SEED-* and STRUCT-* assertions
8. Run checks (confirm 100%)

Repos with 0 KiCad files are automatically purged (removed from repos.md, clone
deleted). Progress is saved every `--batch-size` repos.

**Estimated time:** ~30 seconds per repo for clone + analyze + seed.
50-repo batch ~ 25 minutes. Full 1,500 repos ~ 12 hours.

### 20d. Resume after interruption

If the script is interrupted, resume with:

```bash
python3 tools/add_repos.py --resume
```

Progress is tracked in `results/add_repos_progress.json`. Already-completed and
purged repos are skipped on resume.

### 20e. Run deferred analyzers

If SPICE and EMC were skipped during bulk import (`--skip-spice --skip-emc`):

```bash
python3 run/run_spice.py --jobs 16
python3 run/run_emc.py --jobs 8
python3 regression/seed.py --all
python3 regression/seed_structural.py --all
python3 regression/run_checks.py
```

### 20f. Verify corpus integrity

```bash
python3 regression/run_checks.py          # All assertions
python3 validate/cross_analyzer.py --summary
python3 validate/validate_outputs.py
```

Confirm 100% pass rate on assertions. Investigate any failures per Checklist 12.

### 20g. Update tracking

```bash
python3 tools/generate_catalog.py               # Regenerate catalog
python3 tools/generate_health_report.py --log   # Health report + trend
```

Update corpus count in `status.md`. Record the expansion as a new batch entry.

### 20h. Commit

The `reference/` directory will have large diffs (new baselines and assertions
for every new repo). This is expected.

---

## Quick reference: Common commands

| Task | Command |
|------|---------|
| Run all schematic analysis | `python3 run/run_schematic.py --jobs 16` |
| Run all assertions | `python3 regression/run_checks.py` |
| Run assertions for one type | `python3 regression/run_checks.py --type schematic` |
| Run assertions for one repo | `python3 regression/run_checks.py --repo OpenMower` |
| Check assertion staleness | `python3 regression/check_staleness.py` |
| Cross-analyzer consistency | `python3 validate/cross_analyzer.py --summary` |
| Mutation test effectiveness | `python3 validate/mutation_test.py --repo X --type schematic` |
| Detector coverage matrix | `python3 tools/coverage_detector_map.py` |
| Detector field dashboard | `python3 validate/detector_dashboard.py` |
| Upstream change impact | `python3 tools/detect_changes.py` |
| Generate change-impact map | `python3 tools/detect_changes.py generate-map` |
| Schema drift detection | `python3 validate/validate_schema.py auto-seed` |
| Schema inventory scan | `python3 validate/validate_schema.py scan` |
| Negative assertion preview | `python3 regression/seed_negative.py --all --dry-run` |
| DigiKey constant check | `python3 validate/verify_constants_online.py --dry-run` |
| Health report + log | `python3 tools/generate_health_report.py --log` |
| Reset health baseline | `python3 tools/generate_health_report.py --reset-baseline "reason"` |
| Prune stale seed assertions | `python3 regression/seed.py --all --type {type} --prune-stale` |
| Audit bugfix paths | `python3 regression/audit_bugfix_paths.py` |
| Unit tests | `python3 run_tests.py --unit` |
| Unit tests (tier filter) | `python3 run_tests.py --tier unit\|online\|all` |
| Re-seed assertions | `python3 regression/seed.py --all --type {type}` |
| Promote to reference | `python3 regression/promote.py --repo {repo} --apply` |
| Full validation pipeline | `python3 harness.py validate` |
| Quick validation | `python3 harness.py validate --cross-section smoke` |
| Bugfix assertion gen | `python3 regression/generate_bugfix_assertions.py --apply` |
| Bugfix coverage audit | `python3 regression/audit_bugfix_coverage.py` |
| Findings drift | `python3 regression/drift.py --repo {repo}` |
| Finding refresh | `python3 regression/refresh_findings.py` |
| Assertion metrics | `python3 regression/assertion_metrics.py summary` |
| Full corpus run | `python3 harness.py run --full` |
| Smoke corpus run | `python3 harness.py run --smoke` |
| What-if sweep | `python3 $KICAD_HAPPY_DIR/skills/kicad/scripts/what_if.py analysis.json R5=4.7k` |
| Diff two outputs | `python3 $KICAD_HAPPY_DIR/skills/kicad/scripts/diff_analysis.py base.json head.json` |
| Thermal analysis | `python3 $KICAD_HAPPY_DIR/skills/kicad/scripts/analyze_thermal.py -s sch.json -p pcb.json` |

## Key file locations

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Machine instructions (not git-tracked) |
| `RUNBOOK.md` | This file — operational checklists |
| `ISSUES.md` | Open bugs (git-tracked) |
| `FIXED.md` | Closed bugs with details (git-tracked) |
| `status.md` | Batch history, corpus stats (git-tracked) |
| `TODO-test-improvements.md` | Improvement ideas and status (local, not tracked) |
| `reference/` | Known-good baselines + assertions (git-tracked) |
| `results/outputs/` | Current analyzer outputs (git-ignored) |
| `results/outputs/{type}/_timing.json` | Per-type timing data |
| `results/outputs/{type}/_aggregate.json` | Per-type summary stats |
| `reference/smoke_pack.md` | Curated repos for `--smoke` mode |
| `reference/health_log.jsonl` | Health metric history |
| `reference/health_baseline.json` | Health report comparison baseline |
| `reference/constants_registry.json` | Hardcoded constant audit |
| `reference/equation_registry.json` | Equation tracking registry |
| `reference/schema_inventory.json` | Output field inventory |
| `regression/bugfix_registry.json` | KH-* issue to assertion mapping |
| `~/.claude/projects/.../memory/` | Agent memory files (cross-session context) |
