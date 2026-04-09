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

### KH-206 — nearby global labels with different names merged into one net (MEDIUM)

**Symptom:** Two separate global labels `SDA` and `SCL` at two locations each get merged
into a single `SDA` net. SCL net is never created. All four I2C pins (J3.SDA, J3.SCL,
U2.SDA, U2.SCL) and both pull-up resistors (R1, R2) end up on the `SDA` net.
The PCB analyzer correctly maintains separate SDA and SCL nets.

**Root cause:** KiCad 6+ parser merges nearby global labels with different names. Likely
a proximity-based net assignment bug where pin-to-label association uses position rather
than explicit label name.

**File:** `skills/kicad/scripts/analyze_schematic.py`, KiCad 6+ net resolution.

**Repro:** `cardonabits/haxo-hw` — `haxophone001/haxophone001.kicad_sch`

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

## Priority Queue (open issues, ordered by impact)

1. KH-206 — nearby global labels merged into one net (MEDIUM)
2. KH-204 — power_rails uses UUID sheet paths (MEDIUM)
