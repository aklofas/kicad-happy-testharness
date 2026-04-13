# Findings: MbFredys/PCB-Temperature-Controller / KiCAD files_Controlador-temperatura

## FND-00001086: 1.5mm PTH holes misclassified as mounting holes — likely relay K1 contact pins; Complete 9-layer gerber set correctly identified as complete

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Manufacturing
- **Created**: 2026-03-23

### Correct
- All required and recommended layers present: F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts. Board dimensions correctly extracted from Edge.Cuts as 90.81x56.51mm. NPTH drill file with 0 holes is correctly parsed (the file is present but empty, which is valid KiCad behavior).

### Incorrect
- The gerber drill_classification reports 7 x 1.5mm PTH holes as mounting_holes using diameter_heuristic (no X2 attributes in KiCad 5 output). The design has a FINDER-36.11-4301 relay (K1) whose contact pins are typically 1.2-1.5mm. These are component holes, not mounting holes. 1.5mm holes are too small for any standard mounting screw (M1.2 smallest), and the design has no obvious mounting provisions. This is a heuristic failure for KiCad 5 gerbers.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001087: CA56-12EWA 7-segment LED displays (U3, U6) misclassified as 'ic' component type; KiCad 5 legacy parser correctly extracts subcircuits, signal analysis, and voltage dividers; KiCad 5 parser does not...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Controlador-temperatura.sch
- **Created**: 2026-03-23

### Correct
- Despite KiCad 5 format limitations, the analyzer correctly identifies 11 subcircuits (BTM112 BT module, MAX31855 thermocouple, AD623 instrumentation amp, ATmega328P, relay PS module), detects R10/R19 voltage divider (6.8k/100 Ohm ratio 0.014 for op-amp input), RC filter (2k/100nF, 795Hz for reset debounce), SPI bus (MOSI/MISO/SCK nets), and 9 NPN/MOSFET transistors for 7-segment display driving.

### Incorrect
- U3 and U6 are CA56-12EWA common-anode 7-segment LED displays from the Display_7Segment library. They are classified as 'ic' type, inflating the ic count to 11. Display components should have their own type (e.g., 'display'). They are also treated as center_ic in subcircuit analysis, which is inappropriate for passive display elements.
  (signal_analysis)

### Missed
- The KiCad 5 legacy schematic output lacks ic_pin_analysis, connectivity_issues, pwr_flag_warnings, usb_compliance, inrush_analysis, pdn_impedance, sourcing_audit, ground_domains, bus_topology, test_coverage, assembly_complexity, and sleep_current_audit sections — all present for KiCad 6+ schematics. This is a systematic capability gap for KiCad 5 users. The relay K1 also has no confirmed flyback diode (D1 is 1N4007 which may serve this role, but it's not surfaced by connectivity analysis).
  (signal_analysis)

### Suggestions
(none)

---
