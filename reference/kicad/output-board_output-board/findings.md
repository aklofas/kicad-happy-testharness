# Findings: kicad / output-board_output-board

## FND-00000196: panStamp relay and 0-10V output board with 8 relay channels (NPN transistor driven), 4 PWM-to-voltage converter channels, LF33 voltage regulator, and panStamp NRG2 module across 3 sheets. Excellent detection of RC filters for PWM smoothing, voltage dividers for op-amp feedback, and NPN relay driver circuits. No regulator detection is a notable gap.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: output-board_output-board.sch.json
- **Created**: 2026-03-15

### Correct
- 3 RC low-pass filters (R31/C8, R32/C9, R26/C7) all correctly detected at fc=3.39Hz with 10K/4.7u for PWM-to-analog smoothing
- Voltage divider R36/R34 (21k/10k, ratio=0.323) and R22/R20 (21k/10k, ratio=0.323) correctly detected for op-amp feedback in PWM-to-voltage converters
- 8 NPN transistor relay drivers (Q1-Q8) all correctly identified with base resistors (2k2) and connector loads (BIN1-BIN8)
- Fuse F1 correctly classified as type 'fuse'
- D1 (DIODESCH) correctly classified as reverse-polarity protection on +12V input
- Decoupling on +12V (C1 47u + C10 100n) and +3.3V (C4 100n + C2 22u + C3 1u) correctly detected with has_bulk/has_bypass flags

### Incorrect
(none)

### Missed
- U2 (LF33/UA78M33) is a 3.3V linear regulator converting +12V to +3.3V via SOT223 package, but was not detected in power_regulators. The lib_id 'LF33' should match regulator detection patterns.
  (signal_analysis.power_regulators)

### Suggestions
- Add LF33 and UA78M33 to the regulator detection pattern list - these are common 3.3V LDOs in SOT-223 packages

---
