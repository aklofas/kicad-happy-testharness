# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-04-08

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-209**. Next TH number: **TH-009**.

> All issues resolved as of 2026-04-08. See [FIXED.md](FIXED.md) for history.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-207 — Mirrored component pin-to-net mapping wrong in KiCad 5 legacy (HIGH)

**Symptom:** Components placed with mirrored transforms (e.g., -1 X scale) have their
pin-to-net assignments scrambled. GND pins get mapped to signal nets and vice versa.
Affects all mirrored ICs, connectors, and multi-pin components in KiCad 5 `.sch` files.

**Root cause:** The legacy `.sch` parser uses coordinate-based wire-to-pin matching but
does not apply the component's transform matrix before resolving pin positions. When a
component is mirrored, pin coordinates are flipped but the matcher uses unflipped positions.

**Impact:** Propagates into ERC warnings, net classification, power domain analysis,
bus analysis, and signal detectors. Any downstream analysis referencing pin-net assignments
on mirrored components will be wrong.

**File:** `skills/kicad/scripts/analyze_schematic.py`, legacy `.sch` pin-to-net resolution.

**Repro:** `koron/yuiop` — `yuiop60pi/main2/main2.sch` — U1 (PGA2040) placed with
mirror (-1, 0, 0, -1). Pins 11/12 (GND) mapped to COL4/COL5, GPIO pins mapped to GND.
Also affects J1 (USB_B_Micro) and J2 (USB_MON) pin assignments in same file.

**Discovered:** 2026-04-08 via Layer 3 subagent review.

### KH-208 — Component type classification ignores lib_id, over-relies on ref prefix (HIGH)

**Symptom:** Components with non-standard reference prefixes get systematically
misclassified. Examples from corpus reviews:
- `T1`/`T2` (DS18B20, lib_id `Sensor_Temperature:DS18B20`) → transformer (T prefix)
- `CB1`-`CB6` (circuit breakers, lib_id `Device:CircuitBreaker`) → capacitor (C prefix)
- `COMPR` (AC motor, lib_id `Motor:Motor_AC`) → capacitor (C prefix)
- `VR1` (potentiometer, lib_id `Potentiometer_Bourns:3296W`) → varistor (VR prefix)
- `TR7` (MOSFET, lib_id `DuetWifi:BSH105`) → transformer (custom lib)
- `LED1_W+` (connector, lib_id `Connector:Conn_01x01_Pin`) → LED (LED prefix)

**Root cause:** The type classifier prioritizes reference prefix over lib_id. When lib_id
contains unambiguous type info (`Connector:*`, `Sensor_Temperature:*`, `Motor:*`,
`Device:CircuitBreaker`), it should override the prefix heuristic.

**Impact:** Corrupts component_types counts, triggers false ESD audit entries, and
prevents downstream detectors from finding components of the correct type.

**File:** `skills/kicad/scripts/analyze_schematic.py`, component type classification.

**Repro:** `borzeman/PzbElectronics`, `Duet3D/Duet-2-Hardware`, `GoodEarthWeather/myKicadProjects`

**Discovered:** 2026-04-09 via Layer 3 batch review (8 repos, 4 affected).

---

## Deferred

### KH-205 — D+ net lost in KiCad 5 legacy net resolution (MEDIUM)

**Status:** Unreproducible — referenced file `Mouse/Mouse.sch` not found in repo
`prashantbhandary/Meshmerize-MicroMouse-`. No `.sch` files exist in the checked-out
repo (all converted to `.kicad_sch`). Reopen if repro file is located.

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

## Priority Queue (open issues, ordered by impact)

1. KH-208 — Component type classification ignores lib_id (HIGH)
2. KH-207 — Mirrored component pin-to-net mapping wrong in KiCad 5 (HIGH)
