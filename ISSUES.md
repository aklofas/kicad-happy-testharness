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

Last updated: 2026-04-16

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-322**. Next TH number: **TH-035**.

> 2 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-320 — LOW — 10 untagged math functions found by `audit_equations.py untagged`

**Symptom:** 10 functions in kicad-happy analyzer scripts use math operations
(`math.sqrt`, `math.pi`, `math.sin`, etc.) without an `# EQ-NNN:` tag. Per
RUNBOOK Checklist 11f, substantive engineering equations need tags for
tracking and verification.

**Untagged functions (found 2026-04-16):**

| File:Function | Math | Notes |
|---|---|---|
| `analyze_pcb.py:_dist_point_to_segment:169` | `math.sqrt` | Euclidean distance |
| `analyze_pcb.py:has_coverage_near:219` | `math.pi`, `math.sqrt`, `math.sin` | Area-coverage check |
| `analyze_pcb.py:extract_board_outline:1185` | `math.atan2`, `math.pi`, `1e-*` | Arc/angle for board outlines |
| `analyze_pcb.py:_min_power_pad_distance:1781` | `math.sqrt` | Euclidean distance |
| `analyze_pcb.py:analyze_copper_presence:5086` | `math.sqrt` | Euclidean distance |
| `analyze_pcb.py:analyze_board_edge_via_clearance:5756` | `math.sqrt` | Euclidean distance |
| `analyze_pcb.py:_pt_seg_dist:5765` | `math.sqrt` | Euclidean distance (helper) |
| `emc_formulas.py:estimate_inductor_h_field:1343` | `math.pi`, `1e-*` | **Substantive EMC physics** |
| `emc_rules.py:check_inductor_leakage:3950` | `math.sqrt`, `1e-*` | **Substantive** |
| `kicad_utils.py:snap_to_e_series:404` | `math.log10`, `math.log` | **E-series math** |

**Root cause:** Tag backlog — functions added during normal analyzer growth
without adding the `# EQ-NNN:` comment block.

**Fix:** For each function, add a comment block above the function body:

```python
# EQ-NNN: <formula in symbolic form>
# Source: <authoritative citation, or "Self-evident: Euclidean distance"
#          for geometric primitives>
def _dist_point_to_segment(...):
    ...
```

Main-repo agent can decide per-function whether to cite a source or mark
as self-evident — both are acceptable per RUNBOOK 11f when documented.

**Workaround:** Harness will continue to flag these as untagged at each
`audit_equations.py untagged` run until the tags land upstream. No impact
on correctness — only on verification tracking.

**Priority:** LOW. Not blocking v1.3 tag (per RUNBOOK 11j, untagged functions
are tracked in the audit but don't fail the release gate). Can land
incrementally in v1.3.x.

**Source:** Pre-v1.3 audit per RUNBOOK 11j, 2026-04-16.

---

### KH-321 — LOW — Two wrong switching frequencies in `_KNOWN_FREQS`

**Symptom:** Two entries in `kicad_utils.py:_KNOWN_FREQS` store switching-frequency
values that disagree with authoritative DigiKey parametric data. Discovered
during the pre-v1.3 DigiKey bulk verification of the 105-entry lookup table.

| MPN | Stored | Correct | Evidence |
|-----|--------|---------|----------|
| `TPS62160` | 2.5 MHz (2500000.0) | **2.25 MHz** (2250000.0) | DigiKey matched TPS62160DSGR variant; TI TPS62160 datasheet SLVSAK8 §7.5 Electrical Characteristics confirms fSW = 2.25 MHz typ |
| `TPS63000` | 2.4 MHz (2400000.0) | **1.5 MHz** (1500000.0) | DigiKey range 1.25–1.5 MHz; TI TPS63000 datasheet SLVS590M §7.5 confirms fS = 1.25 MHz min, 1.5 MHz max. Likely confused with TPS63020/60/70 family (which IS 2.4 MHz) |

**Root cause:** Values were grouped incorrectly by family-prefix assumption.
TPS62160 was grouped with the TPS62130/140/150 family at 2.5 MHz; TPS63000
was grouped with TPS63020/60/70 at 2.4 MHz. Per-part datasheet review
catches these.

**Impact:** The `_default_switching_freq` fallback isn't triggered for these
parts (they ARE in the table), so any downstream analyzer relying on the
switching frequency (parasitic injection, EMC harmonic estimation, etc.)
uses the wrong value by ~10% (TPS62160) or ~60% (TPS63000). Affects any
project using these parts.

**Fix:** In `kicad_utils.py:_KNOWN_FREQS`:

```python
-    'TPS62160': 2.5e6,
+    'TPS62160': 2.25e6,    # TPS62160: 2.25MHz (DigiKey verified; different from TPS62130 family)
...
-    'TPS63000': 2.4e6,
+    'TPS63000': 1.5e6,      # TPS63000: 1.5MHz typical (DigiKey verified; different from TPS63020/60/70)
```

**Related concern (consider addressing together):** The `SY820` key in the
same table is a prefix that potentially collides with `SY8200` parts
(which run at 500 kHz, not 800 kHz). The stored 800 kHz is correct for the
SY8208 part (per inline comment in source) but the prefix is too broad.
Either restrict the key to `SY8208` or add an exclusion for SY8200.

**Harness side:** The 2 entries are flagged `DISCREPANCY` in
`reference/constants_registry.json` so they stay unverified until the
upstream fix lands.

**Priority:** LOW. Wrong defaults produce incorrect simulated/estimated
frequencies for specific downstream analyses but don't crash anything.
Can land in v1.3.x.

**Source:** Pre-v1.3 audit per RUNBOOK 11j, 2026-04-16, DigiKey bulk verify
via `validate/verify_constants_online.py --constant _KNOWN_FREQS`.

---

## Test Harness Issues

_No open test-harness issues._

---

## Priority Queue

2 open issues.

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | KH-320 | LOW | Small — add `# EQ-NNN:` tags to 10 math functions in kicad-happy source |
| 2 | KH-321 | LOW | Tiny — fix 2 values in `_KNOWN_FREQS` + consider restricting `SY820` key |
