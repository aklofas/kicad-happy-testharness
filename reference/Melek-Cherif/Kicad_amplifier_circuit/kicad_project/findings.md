# Findings: Melek-Cherif/Kicad_amplifier_circuit / kicad_project

## FND-00000798: Op-amp circuit configurations correctly detected: inverting (unit 1), transimpedance/buffer (unit 2), unknown (unit 3 — power unit); Footprint filter warnings for capacitors are false positives — C...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_project_kicad_project.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Device:Opamp_Dual (U3) dual op-amp with three units parsed correctly. Unit 1 detected as inverting, unit 2 as transimpedance_or_buffer. Unit 3 is the power supply unit (VCC/GND pins) so 'unknown' is reasonable.
- Voltage divider R9/R8 with ratio 0.569 feeding U3 pin 6 (inverting input) correctly identified. Multiple RC filter networks detected including the 4.08kHz R2/C2 network and 6.73kHz R7/(C5||C6) filter.

### Incorrect
- C1-C6 are flagged because CP_Radial_D4.0mm_P2.00mm doesn't match filter 'C_*'. However these are correctly assigned radial electrolytic capacitors — the filter mismatch is because KiCad's Device:C symbol allows both polarized and unpolarized footprints and CP_Radial is a valid choice. The warnings for J1/J2/J3 (PinHeader vs TerminalBlock filter) are more legitimate as the screw terminal symbol has been given a pin header footprint.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000799: Alignment failure flagged as issue but is likely a false positive caused by measuring copper pour extents vs board outline; Layer completeness correct: all 9 expected layers present, PTH/NPTH drill...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: kicad_project_production.json
- **Created**: 2026-03-23

### Correct
- All 9 layers (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts) found. 17 vias + 26 component holes classified correctly. ENIG finish detected from gbrjob. 20 unique components on front side only matches PCB output.

### Incorrect
- F.Cu reports width 52.985mm vs Edge.Cuts 44.45mm (8.5mm over), but B.Cu is 43.649mm (within bounds). The 8.5mm F.Cu overage is likely from a copper zone polygon that includes fill geometry extending to the zone boundary before being clipped by Edge.Cuts. The PCB confirms there are 2 ground zones. A genuine 8.5mm misalignment on a 44mm board would be catastrophically obvious. This is a known issue with measuring zone extents before they are clipped to the board outline.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
