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

Last updated: 2026-05-15

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-327**. Next TH number: **TH-041**.

> 4 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

_None currently open._ See [FIXED.md](FIXED.md) for closed issues.

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

## Priority Queue

_4 open TH-* issues (all LOW)._
