# Findings: PublicSecurity96 / PublicSecurity96_PublicSecurity96

## FND-00001123: Keyboard matrix design correctly analyzed: 100 MX switches, 100 diodes, RP2040 MCU, XC6206 LDO, SRV05-4 ESD; USB compliance check fails CC pull-down: 5.1k resistors R1/R2 are correctly placed but m...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PublicSecurity96.kicad_sch
- **Created**: 2026-03-23

### Correct
- 234 total components correctly parsed. Component types match a standard hotswap keyboard PCB design. XC6206PxxxMR correctly identified as LDO regulator with topology='LDO'. USB-C connector (J1) with RP2040 correctly flagged for CC pull-down failures (R1/R2 are 5.1k to VBUS, not to GND). Crystal Y1 (16MHz) and USB ESD (U2=SRV05-4) correctly identified in subcircuits.

### Incorrect
- The USB-C compliance checker reports cc1_pulldown_5k1=fail and cc2_pulldown_5k1=fail. However, R1 and R2 are 5.1k resistors in the design — the checker may be failing to trace these resistors to the CC1/CC2 pins of J1 (USB_C_Receptacle_USB2.0). This needs deeper inspection of the net topology, but given R1/R2 (5.1k) are listed in the subcircuit for U1/U3 neighbors alongside J1, the checker likely failed to associate them with CC pins due to net naming.
  (signal_analysis)
- The test coverage section correctly finds no test_point components and flags 4 uncovered power rails. However, 'No debug connectors (SWD/JTAG/UART) identified' is a missed finding — the RP2040 has SWD debug capability and the RST1/RST2 solder jumpers and the keyboard USB connector serve as debug interfaces. The analyzer could flag RST/BOOT jumpers as debug aids.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001124: 50 courtyard overlaps flagged for MX keyswitch/diode pairs are false positives — intentional in marbastlib footprints; Board dimensions and DFM tier correctly flagged: 364x120mm exceeds JLCPCB 100x...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PublicSecurity96.kicad_pcb
- **Created**: 2026-03-23

### Correct
- The 100-key keyboard PCB is 364.236x120.193mm. DFM correctly reports 1 violation for board size exceeding 100x100mm standard tier. This is a real finding for a full-size keyboard PCB.

### Incorrect
- All 50 courtyard overlaps are between MXnn (keyswitch) and Dnn (diode) pairs on B.Cu. The marbastlib keyboard footprint library intentionally places diode courtyard areas overlapping with the keyswitch footprint to achieve compact keyboard PCB layout. These are design-correct overlaps, not DFM violations. The DFM overlap checker does not understand this keyboard PCB convention.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
