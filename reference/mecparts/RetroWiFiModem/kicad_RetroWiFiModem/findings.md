# Findings: mecparts/RetroWiFiModem / kicad_RetroWiFiModem

## FND-00001230: L4931CZ33-AP 3.3V LDO regulator correctly identified with input/output rails; MAX3237CAI+ RS-232 transceiver not identified by function; no serial/UART interface detected; R1 correctly identified a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RetroWiFiModem.kicad_sch
- **Created**: 2026-03-24

### Correct
- U4 (L4931CZ33-AP) is correctly detected as an LDO with +5V input, +3V3 output, and 3.3V estimated output from the part suffix. The lib_id (LM2931AZ-3.3_5.0) differs from the value but the analyzer correctly uses the value suffix for vout estimation.
- R1 is an 8-resistor network in a DIP-16 package used as current-limiting resistors for 8 LEDs. The analyzer correctly parses all 8 units with individual pin UUIDs. The BOM shows 1 R1 entry which is correct for a single network package.
- The +5V rail has only C7 (100nF disc cap) and the 1uF electrolytic C8 on +3V3 after the LDO. The analyzer correctly reports 1 cap, 0.1uF total, has_bulk=false for +5V. This is a real concern for a board running WeMos WiFi and DFPlayer.

### Incorrect
(none)

### Missed
- U1 (MAX3237CAI+) is a 5-driver/3-receiver RS-232 transceiver. The ic_pin_analysis shows function='' (empty) for U1. The WeMos mini (U5) has a UART that connects to the MAX3237, and this serial path is not detected in signal_analysis. U5 and U6 (DFPlayer) also have empty function fields.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001231: DFM annular ring 0.1mm requires advanced process; correctly flagged with tier escalation; 3 courtyard overlaps detected including P1/U5 (38mm2) — real placement issue for WeMos module and pin header

- **Status**: new
- **Analyzer**: pcb
- **Source**: RetroWiFiModem.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Same pattern as Effector board — 0.1mm annular ring below standard 0.125mm limit. dfm_tier='advanced' with one violation is correct.
- The WeMos D1 mini (U5) module courtyard overlaps with pin header P1 by 38mm2. This is a real layout concern. Two additional overlaps (U2/R9 and C8/U6) are also flagged. All are plausible real overlaps.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001232: 2-layer gerber set complete and aligned; all required layers present; Drill classification correctly separates vias (63x0.4mm), component holes (104 holes, 3 sizes), and mounting holes (6x3.2mm NPT...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerbers
- **Created**: 2026-03-24

### Correct
- 11 gerber files + 2 drill files. completeness.complete=true with no missing required or recommended layers. alignment.aligned=true. Board dimensions consistent between gerbers (100x66.14mm) matching PCB output.
- All hole types correctly classified using x2_attributes. Via count (63) matches PCB output. PTH total (167) = vias (63) + component holes (104). NPTH count (6) matches the 6 mounting holes in the schematic.

### Incorrect
- pad_summary.smd_apertures=62 comes from F.Paste flash_count. However, PCB analysis reports only 3 SMD footprints. The 62 flashes in F.Paste are from the WeMos D1 mini module pads (which has many SMD pads). The smd_ratio=0.37 is therefore not meaningful as a 'fraction SMD' metric for this board — it heavily counts module pads. The metric is computed correctly mechanically but may be misinterpreted.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
