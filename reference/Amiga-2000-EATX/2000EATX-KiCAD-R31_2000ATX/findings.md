# Findings: Amiga-2000-EATX / 2000EATX-KiCAD-R31_2000ATX

## FND-00000280: Amiga 2000 EATX recreation (612 components). Two bugs found: Q200/Q201 MMBFJ211 JFETs misclassified as MOSFET (hardcoded type in signal_detectors.py). VC800 trimmer capacitor misclassified as varistor (VC prefix falls through to V->varistor), missing from Y800 crystal load caps. RC filters (67 entries, mostly 1k+1nF Zorro bus snubbers), BJT circuits, voltage dividers, MC7905 regulator, active oscillators all correct.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 2000EATX-KiCAD-R31_2000ATX.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 67 RC filters correctly detected including 60 Zorro bus 1k+1nF snubbers
- Q202 PNP audio transistor, Q300/Q301/Q9100 NPN switches correctly identified
- MC7905 -5V regulator correctly detected
- Y800 32.768kHz RTC crystal correctly identified
- X1/X2 28.63636MHz active oscillators correctly detected

### Incorrect
- Q200/Q201 MMBFJ211 (lib Transistor_FET:BF545C) N-channel JFETs classified as type='mosfet' — signal_detectors.py hardcodes mosfet for all G/D/S transistors
  (signal_analysis.transistor_circuits)
- VC800 (CTRIM 22-47pF trimmer cap, lib 2000ATX-rescue:CTRIM-Device) misclassified as 'varistor' — VC prefix has no entry in type_map, falls to single-char V->varistor. Missing from Y800 crystal load_caps (shows only C810, should be C810+VC800)
  (signal_analysis.protection_devices)

### Missed
(none)

### Suggestions
- Add JFET detection based on lib_id containing 'jfet', 'bf545', 'j310', etc.
- Add VC->capacitor to type_map for variable/trimmer capacitors

---
