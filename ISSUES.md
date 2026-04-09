# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-04-08 (filed KH-204/205/206 from v1.2 pre-release)

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-207**. Next TH number: **TH-009**.

> All issues resolved as of 2026-04-06.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-204 — power_rails uses UUID sheet paths instead of human-readable names (MEDIUM)

**Symptom:** `statistics.power_rails` contains paths like `/201ab4ae-b835-4fcf-b591-c6b37cf9a2b1/VIN`
instead of `/DC Boost 10v/VIN`. The PCB analyzer's `power_net_routing` correctly uses readable names.

**Root cause:** Schematic analyzer does not resolve hierarchical sheet UUIDs to sheet names
when building the power_rails list.

**File:** `skills/kicad/scripts/analyze_schematic.py`, power rail extraction section.

**Repro:** `Erhannis/VoltageSwitchboard` — `voltage_tests/voltage_tests.kicad_sch`

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

### KH-205 — D+ net lost in KiCad 5 legacy net resolution (MEDIUM)

**Symptom:** In a KiCad 5 schematic with global labels `D+` and `D-` for USB data lines,
`D-` appears correctly in the nets dict but `D+` does not appear at all. This prevents the
differential pair detector from matching USB data pairs.

**Root cause:** The `+` character in `D+` may be causing issues in the legacy .sch net
resolution parser (regex or string matching).

**File:** `skills/kicad/scripts/analyze_schematic.py`, legacy .sch net resolution.

**Repro:** `prashantbhandary/Meshmerize-MicroMouse-` — `Mouse/Mouse.sch`

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

### KH-206 — nearby global labels with different names merged into one net (MEDIUM)

**Symptom:** Two separate global labels `SDA` and `SCL` at two locations each get merged
into a single `SCL` net. All four I2C pins and both pull-up resistors end up on one net.
The PCB analyzer correctly maintains separate SDA and SCL nets.

**Root cause:** KiCad 6+ parser merges nearby global labels with different names. Likely
a proximity-based net assignment bug where pin-to-label association uses position rather
than explicit label name.

**File:** `skills/kicad/scripts/analyze_schematic.py`, KiCad 6+ net resolution.

**Repro:** `cardonabits/haxo-hw` — `haxophone001/haxophone001.kicad_sch`

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

## Priority Queue (open issues, ordered by impact)

1. KH-205 — D+ net lost in KiCad 5 legacy net resolution (MEDIUM)
2. KH-206 — nearby global labels merged into one net (MEDIUM)
3. KH-204 — power_rails uses UUID sheet paths (MEDIUM)
