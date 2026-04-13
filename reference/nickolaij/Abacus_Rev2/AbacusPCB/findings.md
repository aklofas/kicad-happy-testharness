# Findings: nickolaij/Abacus_Rev2 / AbacusPCB

## FND-00000359: KEYSW keyboard switches misclassified as type 'relay' instead of 'switch'; key_matrices switches_on_matrix=0 despite 45 KEYSW switches present on matrix nets; decoupling_analysis is empty despite 1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: AbacusPCB_AbacusPCB.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- All 45 keyboard_parts:KEYSW components (K1–K45) are assigned type 'relay' in the output JSON. The correct type should be 'switch'. This misclassification is triggered because the component value is 'KEYSW' and the library is 'keyboard_parts', yet the analyzer's type-detection heuristic maps it to 'relay'. The downstream effect is that key_matrices detection reports switches_on_matrix=0, because the matrix detector counts type='switch' components on matrix nets — none are found, even though all 45 KEYSW components sit on the ROW/COL matrix nets.
  (statistics)
- The key_matrices detector correctly identifies a 4-row × 12-col matrix with 45 diodes, but reports switches_on_matrix=0. This is a direct consequence of the KEYSW misclassification: K1–K45 are typed 'relay' so they are never counted as switch components on the matrix. The 45 key switches (K1–K45) are all wired to COL0–COL11 and ROW0–ROW3 nets, so the correct value for switches_on_matrix is 45.
  (signal_analysis)

### Missed
- 17 × 100nF capacitors (C1–C17) are placed as local bypass capacitors for the 17 WS2812B addressable LEDs (W1–W17). Each capacitor bridges the +5V and GND rails at the LED location. The signal_analysis.decoupling_analysis array is empty, indicating the analyzer did not associate these capacitors with the WS2812B LED power supply decoupling. Expected: at least one decoupling_analysis entry covering the LED power domain.
  (signal_analysis)

### Suggestions
(none)

---
