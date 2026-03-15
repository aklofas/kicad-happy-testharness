# Findings: HadesFCS / Hardware_HadesMicroJLCPCB_HadesMicroJLCPCB

## FND-00000083: HadesMicro JLCPCB edition - 84 components, zero signals due to KH-016; compact flight controller design

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/HadesFCS/Hardware/HadesMicroJLCPCB/HadesMicroJLCPCB.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Component enumeration: 84 total with 7 ICs, 30 caps, 17 resistors, 11 connectors, 2 ferrite beads
- Power rails: +3V3, GND, VCC, VDDA - correct for STM32-based flight controller
- 182 nets and 254 wires parsed, 30 no-connect markers
- 7 other components likely includes power flags or mechanical parts

### Incorrect
(none)

### Missed
- Zero signal analysis results despite 84 components - all signal detection blocked by KH-016 legacy wire-to-pin failure
  (signal_analysis)
- VDDA rail with ferrite bead filtering for ADC reference not analyzed
  (signal_analysis)
- 2 diodes (likely ESD or reverse polarity protection) not detected
  (signal_analysis.protection_devices)
- Fuse not detected as protection device
  (signal_analysis.protection_devices)
- 5 LEDs with likely series resistors not characterized
  (signal_analysis)

### Suggestions
- Fix KH-016 to enable signal analysis
- JLCPCB edition likely has LCSC part numbers in BOM - good test case for MPN extraction after fix

---
