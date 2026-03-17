# Findings: zx-sizif-512 / pcb_rev.E_sizif512

## FND-00000266: ZX Spectrum clone rev.E (KiCad 6, 195 components). 10 transistors falsely identified as LED drivers for standalone D1. MOSFET gate_driver_ics inflated by +3.3V power net traversal. Bridge rectifier D2 not detected. LM311/LM386 absent from opamp_circuits. kicad_version='unknown'.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: pcb_rev.E_sizif512.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- EPM1270T144 CPLD and AS6C4008 SRAM correctly classified
- LM2596 switching regulator correctly detected
- RC filters for audio path correctly identified

### Incorrect
- 10 transistors (Q5-Q12 2SA1175 PNP + Q13/Q14 ZVN2106A MOSFET) falsely identified as driving LED D1 — D1 is standalone (anode +5V, cathode through R3 470ohm to GND), no shared nets with any transistor
  (signal_analysis.transistor_circuits)
- Q13/Q14 gate_driver_ics inflated to 19 ICs — gates statically biased at +3.3V, analyzer traverses entire +3.3V power net listing all connected ICs as gate drivers
  (signal_analysis.transistor_circuits)

### Missed
- LM311N comparator (U18) and LM386N audio amplifier (U19) not detected in opamp_circuits — both are central ZX Spectrum functional circuits
  (signal_analysis.opamp_circuits)

### Suggestions
- LED driver detection must require net connectivity between transistor and LED
- Skip power nets when collecting gate_driver_ics for MOSFETs
- Detect D_Bridge library symbols as bridge rectifiers
- Add LM311 and LM386 to opamp/comparator detection
- Fix KiCad 6 version detection for file version 20211123

---
