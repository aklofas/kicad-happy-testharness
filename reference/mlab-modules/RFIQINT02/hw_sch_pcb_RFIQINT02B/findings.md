# Findings: RFIQINT02 / hw_sch_pcb_RFIQINT02B

## FND-00001111: kicad_version reported as 'unknown' for a KiCad 5 format file (version 20211123); Multiple capacitors in BOM have wrong footprint 'Resistor_SMD:R_0805_2012Metric' — this is a schematic data issue f...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RFIQINT02B.kicad_sch
- **Created**: 2026-03-23

### Correct
- U1 Si53322 is correctly extracted as ic type with QFN-16 footprint and proper datasheet link. The +3V3 rail power budget assigns 10mA to U1, which is a reasonable estimate for a clock buffer IC.

### Incorrect
- The file header has file_version=20211123, which is a KiCad 5.x legacy format. The analyzer outputs kicad_version='unknown' rather than correctly identifying it as KiCad 5. This affects version-dependent parsing paths downstream.
  (signal_analysis)
- In RFIQINT02, C1, C6, C7, C8, C17, etc. have footprint='Resistor_SMD:R_0805_2012Metric' but type='capacitor'. This is a design error in the source schematic (wrong footprint assigned) that the analyzer correctly reads as-is. The analyzer is accurate here — the design itself has the mismatch. Not an analyzer bug.
  (signal_analysis)

### Missed
- Several components have Device:C lib_id but are assigned Resistor_SMD footprints. The analyzer does not generate any warning about this mismatch between symbol type and footprint library name. This is a real actionable design issue that should be surfaced.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001112: Layer completeness, alignment, and board dimensions all correct for RFIQINT02

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-23

### Correct
- 9 gerber files with all expected layers present, board dimensions 40.28x60.6mm from gbrjob match Edge.Cuts. 4 NPTH mounting holes (3.3mm) correctly classified as mounting_holes. 78 vias in two sizes (0.4mm x5, 0.6mm x73) correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001113: kicad_version='unknown' for KiCad 5 PCB format (file_version 20211014)

- **Status**: new
- **Analyzer**: pcb
- **Source**: RFIQINT02B.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Like the schematic, the PCB file uses the legacy KiCad 5 format and the analyzer cannot identify the version. kicad_version='unknown' is emitted. The PCB appears correctly parsed despite this (46 footprints, correct layer structure for legacy format with B.Cu as layer 31).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
