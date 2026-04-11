# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

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

Last updated: 2026-04-10

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-231**. Next TH number: **TH-015**.

> 2 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-230: Empty placed Value silently substituted with lib_symbol default

**Severity:** LOW
**Discovered:** 2026-04-10 by `validate/verify_parser.py` (P1 Parser Verification, full corpus run)
**Repro:** `hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`

The file has two placed `(symbol (lib_id "Device:R") ...)` instances both
annotated as `R1` (a duplicate-annotation design issue independent of this
bug). The second instance has `(property "Value" "")` — explicitly empty —
but the analyzer reports `value: "R"` for it, which is the `Device:R`
lib_symbol's placeholder default Value.

**Expected:** `components[].value` should reflect the placed instance's
property exactly. An empty placed Value should serialize as `""`, not be
silently replaced by the lib_symbol template default. Otherwise downstream
detectors and BOM logic see a fabricated value that doesn't exist in the
source.

**Evidence:**
- sexp parse: R1 instance #2 Value = `""`
- analyzer output: R1 instance #2 value = `"R"` (= lib_symbol default)
- file: `repos/hamster/SAINTCON/CHC/2022/Circuits - Series and Parallel.kicad_sch`
- analyzer output: `results/outputs/schematic/hamster/SAINTCON/CHC_2022_Circuits - Series and Parallel.kicad_sch.json`

Likely in `analyze_schematic.py` symbol parsing path — when the placed
Value property is empty, the code is falling back to `sym_def.get("value")`
or similar instead of preserving the empty string.

Severity is LOW because it requires both a duplicate-annotation defect
AND an empty Value on one of the duplicates, and only 1/25,625 corpus
files hits it.

---



---

## Test Harness Issues

### TH-014: Two test files silently pass — missing `__main__` runner block

**Severity:** MEDIUM
**Discovered:** 2026-04-10 while building the `--smoke` PR-gate subset

The harness uses a stdlib test runner pattern: each `tests/test_*.py` file
ends with `if __name__ == "__main__":` that iterates `def test_*` functions
and reports counts. `run_tests.py` invokes each file via `subprocess.run`
and parses the summary line.

Two files are missing this runner block entirely:
- `tests/test_detection_schema.py` — defines 30 test functions, none execute
- `tests/test_batch_review.py` — defines 6 test functions, none execute

When invoked as `python3 tests/test_detection_schema.py`, the module
imports cleanly, defines all functions, then exits 0 with no output.
`run_tests.py` parses the empty summary, falls through to its "p=1, ok"
fallback at line 188-195, and reports the file as PASS — so the suite
shows green while 36 tests never actually ran.

**Fix:** Add the standard runner block to both files. Pattern from any
working test file (e.g. `tests/test_verify_parser.py:394-410`):

```python
if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
```

After fixing, run `python3 run_tests.py --unit` and verify the file count
in the summary increases by the actual test count (rather than +1 each).

Severity is MEDIUM rather than HIGH because the tests probably DID work
when written and just got copy-pasted from a template that lost the
runner. Also worth a `--detect-silent-passes` audit step in `run_tests.py`
to catch this regression class going forward.

---



---

## Deferred

(none)

---

## Priority Queue (open issues, ordered by impact)

1. **TH-014** — MED — two test files have no `__main__` runner; 36 tests silently never run
2. **KH-230** — LOW — empty placed Value silently replaced with lib_symbol default (1 file in corpus)

