# Findings: baldengineer/bit-preserve / Amiga_A500.PSU.312503-03_Amiga A500 Power Supply

## FND-00002342: 218 false current_sense detections caused by RF modulator capacitors (330 pF, 68 pF) treated as shunt resistors; RF-prefixed components universally misclassified as 'resistor' type; UART falsely de...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bit-preserve_Commodore_C64_251469_C64B.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The C64 schematic contains an RF modulator subcircuit with components prefixed RF- (e.g., RF-C1 330 pF, RF-C6 68 pF). All 81 RF-prefixed components are classified as 'resistor' regardless of their actual type (capacitor, inductor, transistor, diode). The current_sense detector then treats each RF-C* capacitor as a low-ohm shunt, producing 218 absurd detections with computed max_current values exceeding 100 million amps (e.g., 151,515,152 A for a 330 pF cap). Every single one of the 218 current_sense entries is a false positive.
  (signal_analysis)
- The Commodore C64 RF modulator uses the naming convention RF-C*, RF-L*, RF-Q*, RF-D*, RF-R* for its components. The analyzer classifies all 81 of these as 'resistor', ignoring the actual component type indicator in the sub-reference (C=capacitor, L=inductor, Q=transistor, D=diode). This inflates the statistics resistor count from 115 to 129 (at least 14 non-resistors wrongly counted) and causes cascading false detections in the current_sense, voltage_divider, and other detectors.
  (statistics)
- The bus_analysis.uart array contains one entry for the net POTX, listing U18 (6581 SID chip) and U28 (4066 analog switch) as UART devices. POTX is a paddle/potentiometer input line on the SID audio chip and has no serial protocol characteristics. This is a false positive from the UART detector matching net naming or pin-count heuristics incorrectly.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002343: sheets_parsed and sheet_files are null for a valid KiCad 6 hierarchical schematic

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bit-preserve_Apple_Apple II+_AppleII+_AppleII+.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Apple II+ schematic is a valid KiCad 6 file (version 20230121) with 172 components, 417 nets and 2570 wires successfully parsed. However sheets_parsed is null and sheet_files is null, while kicad_version is reported as 'unknown' despite file_version 20230121 being KiCad 8. The component data was extracted correctly but the sheet metadata fields are not populated, suggesting the sheet tracking logic has a bug for KiCad 6+ single-file schematics.
  (kicad_version)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002344: Gracefully handled a stub placeholder PCB file (version 4, single-line dummy)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_bit-preserve_Apple_Apple II_AppleII_AppleII.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The Apple II PCB file is a single-line stub: (kicad_pcb (version 4) (host kicad "dummy file")). The analyzer correctly returns all-zero statistics rather than crashing, and reports no footprints, tracks, or board outline. The copper_presence warning and silkscreen documentation warnings are appropriate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
