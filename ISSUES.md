# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-03-17

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-161**. Next TH number: **TH-008**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-160: PWR_FLAG skip over-aggressive for single-sheet connector-powered designs [MEDIUM]

**Analyzer**: analyze_schematic.py
**Discovered**: 2026-03-17 (Layer 3 review)

The skip at line ~3706 (`if _is_power_net_name(net_name) or _is_ground_name(net_name): continue`) suppresses PWR_FLAG warnings on well-known power net names (GND, VCC, etc.). This reduces false positives on multi-sheet designs where power port symbols provide the power_out pin, but is over-aggressive for single-sheet designs where power comes from connectors (which have passive pins, not power_out). In those designs, KiCad ERC would flag the missing PWR_FLAG and the analyzer should too.

**Root cause**: The skip unconditionally suppresses warnings on any net with a recognized power/ground name, regardless of whether a power port symbol actually exists on that net.
**Fix**: Gate the skip on whether the net has at least one power port symbol (power_out pin), or on multi-sheet designs. If the only power source on the net is a connector's passive pin, the PWR_FLAG warning should not be suppressed.

---

## Priority Queue (open issues, ordered by impact)

1. **KH-160** [MEDIUM] -- PWR_FLAG skip over-aggressive for connector-powered single-sheet designs
