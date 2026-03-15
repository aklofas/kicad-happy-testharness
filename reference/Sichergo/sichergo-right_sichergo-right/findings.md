# Findings: Sichergo / sichergo-right_sichergo-right

## ?: Right-hand half of the Sichergo split ergonomic keyboard with STM32F103C8T (U2), 4x5 key matrix, per-key LEDs, and audio jack for inter-half communication. Simpler than the left half (no USB, no ESD protection). Analyzer produces accurate results.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: sichergo-right_sichergo-right.kicad_sch.json

### Correct
- Voltage divider R5/R6 (4.7k/4.7k) correctly detected feeding U2 (STM32F103C8Tx) BOOT0 pin with 0.5 ratio from +3V3
- RC low-pass filter R2/C3 (4.7k/0.1uF) at 338.63 Hz correctly detected for reset filtering
- Crystal Y1 (Crystal_GND24) with load caps C1 and C2 (10pF each) correctly detected with effective load 8pF
- Key matrix correctly detected: 4 rows x 5 columns, 18 switches (SW1-SW19 minus 1 for power/other), 18 diodes (CD4148W)
- Q1 (2N7002) correctly detected as N-channel MOSFET LED driver with gate pulldown R7 (5.1k), gate driven by U2, LED D20 through R20 (1k)
- +3V3 rail decoupling correctly analyzed: 7 caps totaling 11.5uF (C5,C6,C4,C3,C7,C9=0.1uF + C10=1uF + C8=10uF)
- 100 total components correctly counted: 19 switches, 18 LEDs, 18 diodes, 25 resistors, 10 capacitors
- U3, U4 (SN74LVC1G125DBV single buffer ICs) correctly classified

### Incorrect
- Audio1 (PJ-327E-SMT audio jack) classified as type 'ic'. This is a 3.5mm TRRS audio jack connector for split keyboard communication, not an IC. Should be classified as 'connector'.
  (statistics.component_types)

### Missed
- No power regulator detected. The right half presumably receives power from the left half through the audio jack, but U1 (YTS1C0033BBG01, which appears to be a voltage regulator or charge pump) was not identified as a power regulator.
  (signal_analysis.power_regulators)

### Suggestions
- Audio jack components (PJ-327E-SMT) should be classified as connectors.
- YTS1C0033BBG01 may be a voltage regulator that should be detected -- worth investigating its datasheet.

---
