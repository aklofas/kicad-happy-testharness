# Findings: OLIMEX/DIY-LAPTOP / HARDWARE_A64-TERES_TERES-PCB1-A64-MAIN_Rev.C_TERES_PCB1-A64-MAIN_Rev.C

## FND-00000227: OLIMEX DIY-LAPTOP power supply sheet (152 components, 213 nets). Critical: 0 regulators detected on a POWER SUPPLY sheet containing AXP803 PMIC (8+ internal regulators) and MT3608 boost converter. 0 voltage dividers despite R80/R81 feedback divider on MT3608. RC filter R80+C143 misidentified as filter (actually feedback divider sense network). RC filter duplicates from bidirectional traversal. Crystals correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_A64-TERES_TERES-PCB1-A64-MAIN_Rev.C_Power Supply, Extensions and MiPi-DSI .sch.json
- **Related**: KH-118
- **Created**: 2026-03-16

### Correct
- Q2 32.768kHz RTC crystal and Q3 24MHz main clock correctly detected with accurate load capacitance calculations
- Actual RC filters correctly detected: R82/C176 battery temp sense (7Hz), R85/C190 NMI debounce (16Hz), R89/C156 reset filter (1.6kHz), R92/C178 HSIC power filter (16Hz)

### Incorrect
- R80+C143 misidentified as RC filter (1.93Hz cutoff) — R80 is the upper leg of MT3608 feedback divider (Ra in Vout=0.6*(1+Ra/Rb)). C143 is FB pin sense capacitor, not a signal filter.
  (signal_analysis.rc_filters)
- RC filter duplicates: R82/C176 and R90/C140 each reported twice (forward and reverse direction). Bidirectional traversal artifact inflates 4 real filters to 8 reported.
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Add PMIC detection (AXP, SY8xxx, MP2xxx families) — PMICs are major power sources in laptop/SBC designs
- Add MT3608/boost converter part number patterns to regulator detection
- Distinguish feedback divider sense networks from passive RC filters by checking IC FB pin connectivity
- Deduplicate RC filters: same R-C pair with reversed input/output should be reported once

---
