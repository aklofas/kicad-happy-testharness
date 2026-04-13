# Findings: obsilab/Quanta75 / Quanta75_BareRP2040_JLCPCBAoptimized

## FND-00001150: kicad_version reported as 'unknown' for all schematics; file_version 20230121 maps to KiCad 7; USB-C CC resistor fail correctly flagged for BareRP2040 and RP2040Stamp_JLCPCBA; I2C missing pull-up r...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Quanta75_BareRP2040_JLCPCBAoptimized.kicad_sch
- **Created**: 2026-03-23

### Correct
- The 4k99 resistors (R2/R4) in BareRP2040 are part of a VBUS voltage divider with a 120R bottom, not CC pulldowns. The design genuinely lacks 5.1k CC resistors on three USB-C connectors. The Pico/RP2040Stamp variants have proper 5K11 resistors and correctly pass.
- The I2C expansion header (J8) exposes I2C1-SDA and I2C1-SCL via global labels but no pull-up resistors exist in the schematic. The bus_analysis correctly reports has_pull_up=false for both lines.
- All four newer schematics correctly detect a 6-row x 15-column matrix. Row/Column net names are correctly enumerated, and diodes_on_matrix=83 matches the actual diode count for each matrix variant.
- Confirmed by source file inspection: none of the schematics contain PWR_FLAG symbols. The pwr_flag_warnings are legitimate ERC findings. The +1V1 rail in BareRP2040 is the RP2040 internal LDO output, and its warning is accurate.

### Incorrect
- All 5 schematics show kicad_version='unknown' despite file_version=20230121, which is the KiCad 7.x schema version. The analyzer fails to map file version to KiCad major version.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001151: Sourcing audit correctly reports 0/N MPN coverage; LCSC codes present but mpn field empty

- **Status**: new
- **Analyzer**: schematic
- **Source**: Quanta75_Pico_Quanta75_Pico.kicad_sch
- **Created**: 2026-03-23

### Correct
- The BOM entries have empty 'mpn' fields but populated 'lcsc' fields (e.g., RP2040=C2040, SL2.1A=C192893). The sourcing_audit technically reports correct MPN coverage (0%) but does not count LCSC as a sourcing identifier. This is technically accurate but potentially misleading for JLCPCBA-optimized designs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001152: thermal_analysis zone_stitching incorrectly reports signal nets (USB1_D-, Row2, Column9, GPIO0_LED) as zone-stitched

- **Status**: new
- **Analyzer**: pcb
- **Source**: Quanta75_RP2040Stamp_JLCPCBAoptimized_Quanta75_RP2040Stamp_JLCPCBAoptimized.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The zone_stitching list includes signal nets like USB1_D-, Row2, Column9-11, GPIO0_LED, REB, REA alongside power nets. These are small copper fills/polygons used for routing or shielding, not thermal stitching. zone_stitching should be limited to power/ground nets. Only the GND net (area 49343mm², 105 vias) and VBUS_UP qualify as genuine zone stitching.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001153: thermal_pads for U1 (RP2040) pad 57 listed twice — duplicate detection bug; DFM correctly flags board_size violation for all 75% keyboard PCBs (~320x158-165mm exceeds 100x100mm tier threshold); Zon...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Quanta75_BareRP2040_JLCPCBAoptimized.kicad_pcb
- **Created**: 2026-03-23

### Correct
- All five populated PCBs correctly report a single DFM violation: board dimensions (317-320mm wide) exceed the 100x100mm threshold for the 'standard' tier. The remaining DFM metrics (min track 0.2mm, drill 0.35-0.4mm) are properly extracted.

### Incorrect
- BareRP2040 thermal_analysis.thermal_pads contains two identical entries for U1 pad 57 (same layer=B.Cu, same nearby_thermal_vias=9, same pad_area=10.24mm²). The RP2040 has a single exposed pad. This is a duplicate in the analyzer's thermal pad scanning loop.
  (signal_analysis)
- The GND zone spans both F.Cu and B.Cu ('F&B.Cu' layer). The filled_area counts copper on both layers, while outline_area counts the zone boundary once, yielding fill_ratio=1.606. The ratio calculation should be per-layer or the documentation should clarify dual-layer behavior to avoid appearing as a bug.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001154: Connectivity shows U1.16 duplicated in Column1 net — Pico hybrid SMD+THT footprint counted twice; Incomplete routing correctly detected: Pico and RP2040Stamp PCBs have 35 unrouted nets, routing_com...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Quanta75_Pico_Quanta75_Pico.kicad_pcb
- **Created**: 2026-03-23

### Correct
- The Pico and RP2040Stamp variants have only 648 track segments and 16 vias — the keyboard matrix column nets are unrouted. The connectivity analysis correctly identifies 35 unrouted nets and sets routing_complete=false. BareRP2040 and RP2040Stamp_JLCPCBA are fully routed and correctly show routing_complete=true.

### Incorrect
- The RPi Pico footprint has pad 16 defined as both an SMD rect (B.Cu castellated pad) and a THT oval pad. The analyzer counts both physical pads and shows U1.16 twice in the unrouted Column1 net list. The same pattern repeats across other column nets. This is a false duplication from hybrid Pico footprints; the net only needs one connection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001155: Early unfinished PCB (0 tracks, 0 vias, no board outline) correctly parsed without crashing; DFM returns empty metrics

- **Status**: new
- **Analyzer**: pcb
- **Source**: old - KiCad Project Quanta_Quanta-ISO-Pico_01.kicad_pcb
- **Created**: 2026-03-23

### Correct
- The old ISO Pico PCB is a placement-only file with no routing, no copper, and no board edge. The analyzer handles it gracefully: track_segments=0, via_count=0, board_width=null, copper_layers_used=0. DFM returns no violations and no metrics, which is appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
