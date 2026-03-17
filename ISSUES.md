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
number: **KH-174**. Next TH number: **TH-008**.

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

### KH-163: thermal_pad_vias and thermal_analysis give contradictory via counts (PCB analyzer) [MEDIUM]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: modular-psu

For IC2 (BD00FC0W), `thermal_pad_vias` reports 0 vias (adequacy="none") while `thermal_analysis.thermal_pads` reports 44 nearby thermal vias. Both sections analyze the same component.

**Root cause**: `analyze_thermal_pad_vias()` uses tight pad-boundary containment (within pad + 10% margin), while `analyze_thermal_vias()` uses broader proximity search. When vias are slightly outside the pad boundary but clearly serving thermal relief, the two sections disagree.
**Fix**: Either unify the search radius, or add a note/cross-reference when the two sections disagree on the same component.

---

### KH-164: decoupling_placement absent for boards with ICs and bypass caps (PCB analyzer) [MEDIUM]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: modular-psu

The `decoupling_placement` section is completely absent despite the board having IC1 (MAX31760AEE+) and IC2 (BD00FC0W) with nearby bypass capacitors (C16 at 4.91mm, C13 at 5.38mm from IC1).

**Root cause**: Unknown — needs investigation. Possibly the ICs are not classified as needing decoupling, or the cap search radius is too small for this board layout.
**Fix**: Investigate why the decoupling analysis skips this board. Check component classification and search radius thresholds.

---

### KH-165: Thermal pad detection misses small DFN/QFN exposed pads (PCB analyzer) [MEDIUM]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: cnhardware (ch32v003f4u6_pendant), explorer

Neither `thermal_pad_vias` nor `thermal_analysis.thermal_pads` detect exposed pads on small DFN/QFN packages: WS4518D-6/TR (DFN-6-1EP_2x2mm, pad area ~4mm²) and CH32V003F4U6 (QFN-20-1EP_3x3mm, pad area ~9mm²).

**Root cause**: The 4mm² minimum area threshold for EP pads may be right at the boundary for a 2x2mm DFN. The 3x3mm QFN should be detected (9mm² meets the threshold). Needs investigation — the EP pad may not be parsed correctly, or the net check may be filtering it out.
**Fix**: Verify that the exposed pad is correctly parsed for these footprints and check if the area/net thresholds are too aggressive for small packages.

---

### KH-166: False positive missing_revision silkscreen warning (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: modular-psu

The `documentation_warnings` includes `missing_revision` with severity "warning", but the `board_metadata` section correctly shows `rev: "r3B7"` and the silkscreen text includes "EEZ DIB AUX PS (12/2021 r3B7)".

**Root cause**: The silkscreen warning check does not cross-reference against board_metadata or silkscreen text content.
**Fix**: Skip the `missing_revision` warning if `board_metadata.rev` is non-empty or if silkscreen text contains a revision pattern.

---

### KH-167: ESD/TVS protection devices included in decoupling analysis (PCB analyzer) [LOW]

**Analyzer**: analyze_pcb.py
**Discovered**: 2026-03-17 (PCB Layer 3 review)
**Affected repos**: cnhardware (ch32v305-radioset)

RCLAMP0502N (U3), an ESD protection device, is classified as an IC needing decoupling. Protection/TVS devices do not need bypass capacitors.

**Root cause**: Decoupling analysis includes all U-prefix components without filtering ESD/TVS/protection devices.
**Fix**: Filter out known ESD/TVS families (RCLAMP, PRTR, PESD, USBLC, etc.) or components classified as protection devices from decoupling analysis.

---

### KH-173: SMD ratio uses incommensurate units (Gerber analyzer) [LOW]

**Analyzer**: analyze_gerbers.py
**Discovered**: 2026-03-17 (Gerber Layer 3 review)
**Affected repos**: bitaxe

`smd_apertures` counts unique SMDPad aperture definitions (shapes), while `tht_holes` counts actual hole instances. A board with 45 unique SMD pad shapes but 500 pad placements gets the same count as one with 45 placements. bitaxe reports 0.44 ratio which is misleadingly low for a BGA-based design.

**Root cause**: Lines ~866-893 count unique aperture definitions for SMD but instance counts for THT.
**Fix**: Count SMD pad flash instances (from the gerber flash command count per SMDPad aperture) instead of unique aperture definitions. Or clearly label the metric as `smd_aperture_types` vs `tht_hole_instances`.

---

## Priority Queue (open issues, ordered by impact)

1. **KH-160** [MEDIUM] -- PWR_FLAG skip over-aggressive (Schematic)
2. **KH-163** [MEDIUM] -- thermal_pad_vias vs thermal_analysis contradiction (PCB)
3. **KH-164** [MEDIUM] -- decoupling_placement absent (PCB)
4. **KH-165** [MEDIUM] -- thermal pad misses small DFN/QFN (PCB)
5. **KH-166** [LOW] -- false positive missing_revision warning (PCB)
6. **KH-167** [LOW] -- ESD/TVS in decoupling analysis (PCB)
7. **KH-173** [LOW] -- SMD ratio incommensurate units (Gerber)
