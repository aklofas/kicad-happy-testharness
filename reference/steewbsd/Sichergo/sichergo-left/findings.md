# Findings: steewbsd/Sichergo / sichergo-left_sichergo-left

## FND-00002617: Left-hand half of a split ergonomic keyboard (Sichergo) built around STM32F103C8T (U4) with USB interface, 4x5 key matrix with anti-ghosting diodes, per-key LEDs, ESD protection (TPD4E05U06DQA), 3.3V LDO (AZ1117-3.3), and audio jack for split communication. Comprehensive and accurate analysis.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: sichergo-left_sichergo-left.kicad_sch.json

### Correct
- Voltage divider R6/R7 (4.7k/4.7k) correctly detected feeding U4 (STM32F103C8Tx) BOOT0 pin with 0.5 ratio from +3V3 to GND, used to select boot mode
- RC low-pass filter R3/C5 (4.7k/0.1uF) at 338.63 Hz correctly detected on the NRST line for reset filtering
- Crystal Y1 (Crystal_GND24) with load caps C4 and C3 (10pF each) correctly detected, effective load 8pF calculated
- Key matrix correctly detected: 4 rows x 5 columns, 18 switches, 18 anti-ghosting diodes (CD4148W), matching the physical keyboard layout
- AZ1117-3.3 (U1) correctly identified as LDO regulator with topology=LDO, output_rail=+3V3, estimated_vout=3.3, vref_source=fixed_suffix
- ESD protection: D1 (CPDUR5V0HE-HF) on VBUS correctly detected, U2 (TPD4E05U06DQA) correctly detected as esd_ic protecting USB D+/D- and other lines
- Q1 (2N7002) correctly detected as N-channel MOSFET LED driver with gate resistor R8 (5.1k) as pulldown, gate driven by U4 (STM32F103C8Tx), LED D8 driven through R13 (1k)
- 118 total components correctly counted: 19 switches, 18 LEDs, 18 diodes, 28 resistors, 13 capacitors, 7 ICs
- F1 (1812L050/30PR) correctly classified as fuse, L1 (120 Ohm @ 100 MHz) correctly classified as ferrite_bead
- +3V3, GND, VBUS power rails correctly identified

### Incorrect
- Audio1 (PJ-327E-SMT audio jack) classified as type 'ic'. This is a 3.5mm TRRS audio jack connector used for split keyboard communication, not an IC. Should be classified as 'connector'.
  (statistics.component_types)

### Missed
(none)

### Suggestions
- Audio jack components (PJ-327E-SMT, PJ-320A, etc.) should be classified as connectors rather than ICs.

---
