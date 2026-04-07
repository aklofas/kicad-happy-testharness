# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-04-06

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-204**. Next TH number: **TH-009**.

> All issues resolved as of 2026-04-06.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-201 — power_tree legend always shows green for output rails (LOW)

**Symptom:** The legend at the bottom of power tree figures always shows the first
palette color (green) for "Output Rail" regardless of how many output rails exist
and what colors they actually use in the diagram.

**Root cause:** The legend is hardcoded to use a single color for the output rail
entry rather than reflecting the actual colors assigned via `output_color_map`.

**File:** `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`, render()
legend section (~line 570+).

**Fix:** Either show one legend entry per output rail color used, or show a single
"Output Rails" entry with a multi-color swatch.

**Discovered:** 2026-04-06 via figure_review.py gallery inspection.

---

### KH-202 — power_tree output rail boxes lack context (MEDIUM)

**Symptom:** Output rail boxes on the right side of power tree figures only show the
net name (e.g. "VN_0", "VP_5", "+3V3"). For generic names this provides no useful
context about what the rail powers.

**Root cause:** The `prepare()` method only extracts the rail name and voltage from
regulator data. It does not collect information about what loads are connected to
each output rail (which components draw from it, their types/functions).

**File:** `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`, prepare()
output_rails section (~line 195+).

**Fix:** Enrich output rail data in prepare() with load information from the
schematic analysis — e.g. key ICs, component count, or functional description
of what the rail powers. Display a subtitle in the output box.

**Discovered:** 2026-04-06 via figure_review.py gallery inspection (BUNPC #3).

---

### KH-203 — power_tree regulator boxes have minimal detail (MEDIUM)

**Symptom:** Regulator boxes in the center column show only topology and output
capacitor info (e.g. "LDO, Cout: C2: 4.7uF 25V"). This is too terse to be useful
for design review.

**Root cause:** The regulator box body text only includes topology and cap summary.
Missing: component value/MPN, input→output voltage range, load current rating,
efficiency class, or other datasheet-level context.

**File:** `skills/kidoc/scripts/figures/generators/power_tree/__init__.py`, render()
regulator box section (~line 390+) and prepare() regulator entry building (~line 135+).

**Fix:** Enrich regulator entries in prepare() with value/MPN from component lookup,
voltage range from detector data. Update render() body_lines to show: value/MPN on
first line, voltage conversion on second line, Cout summary on third line.

**Discovered:** 2026-04-06 via figure_review.py gallery inspection.

---

## Priority Queue (open issues, ordered by impact)

1. KH-202 — power_tree output rail boxes lack context (MEDIUM)
2. KH-203 — power_tree regulator boxes have minimal detail (MEDIUM)
3. KH-201 — power_tree legend always shows green for output rails (LOW)
