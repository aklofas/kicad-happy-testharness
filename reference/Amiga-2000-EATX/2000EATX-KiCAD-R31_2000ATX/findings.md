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

## FND-00002505: Amiga 2000 EATX motherboard re-implementation (rev 3.1) with 612 components featuring Amiga custom ICs (MC68000, Agnus, Gary, Paula, Denise, Buster, 8520s), Zorro II expansion, ISA slots, and ATX power. Analyzer correctly identifies most signal paths but misclassifies 12 Amiga/ISA bus connector symbols as capacitors, misses LF347/LM339 opamp and comparator circuits.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 2000EATX-KiCAD-R31_2000ATX.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- All Amiga custom ICs correctly identified: U100 MC68000, U101 Agnus, U102 Gary, U200 Paula, U201 Denise, U300/U301 8520 CIAs, U800 Buster, U899 MSM6242 RTC
- 16 power rails correctly detected: +12V, +5V, -12V, -5V, +5VSB, +5VMOUSE, +AUD, +AV, +VID, -AV
- Regulator U9000 (MC7905) correctly identified as LDO converting -12V to -5V
- All 7 transistors correctly classified: Q200/Q201 as JFET (MMBFJ211) audio mute switches, Q300/Q301/Q302/Q9100 as BJTs
- Crystal oscillators correctly detected: Y800 (32.768kHz passive), X1 (28.63636MHz master clock), X2 oscillator
- ATX power-on delay RC networks correctly detected: R9101/C9104 (62ms delay) and R9103/C9103 for +5VSB sense
- 67 RC filters detected including 47 Zorro bus termination networks (1k + 1000pF, fc=159kHz) and 8 audio filters
- UART/RS-232 correctly detected: U304 (SN75188DR driver) and U305 (SN75189DR receiver)
- Bus topology correctly extracted with 486 bus wires and all Zorro/68000 buses: A[1..23], D[0..15], BA[1..23], BD[0..15]
- Three fuses correctly identified: F1 (4A, +5VMOUSE), F3 (+12V), F4 (+5V)
- 13 ferrite beads correctly classified (FB101-104, FB215, FB301-303, FB401, FB900-902, FB907)

### Incorrect
- 12 proprietary Amiga/ISA bus connector symbols misclassified as 'capacitor': CN600 (CPU-Slot), CN601-CN605 (5x Zorro-Slot), CN700-CN702 (3x ISA-16-BIT-Slot), CN203/CN207 (Video-Slot). Inflates capacitor count and understates connector count.
  (statistics.component_types)
- design_observations flags U204 (LF347) as missing decoupling on '+AV' rail, but ic_pin_analysis shows C220 (0.22uF), C222 (47uF), and C900 (0.1uF) on +AV. False positive contradicting its own ic_pin_analysis.
  (signal_analysis.design_observations)

### Missed
- LF347 quad op-amp (U204) not detected in opamp_circuits despite having 4 units with +in/-in/out pins and dual supply +AV/-AV. LM339 comparator (U805) also not detected.
  (signal_analysis.opamp_circuits)
- F2 (4A fuse) missed in protection_devices because both adjacent nets are unnamed. F2 sits between EMI332 feedthrough cap and D400 on +12V Zorro supply.
  (signal_analysis.protection_devices)
- Y800 (32.768kHz crystal) has only one load cap reported (C810). VC800 (22-47pF trimmer on pin 2) not counted as load cap despite serving the same function.
  (signal_analysis.crystal_circuits)

### Suggestions
- Improve connector classification: when lib_id contains 'Slot', 'Connector', or 'Socket', classify as 'connector' regardless of lib_name.
- Fix fuse detection to find fuses where both nets are unnamed but topologically connected to power rails via diodes or ferrite beads.
- Add LF347 and multi-unit op-amp detection via lib_id matching known op-amp families.
- In crystal_circuits, include variable/trim capacitors (VC* prefix) alongside fixed capacitors as load caps.

---
