# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev3_left_ErgoSNM_v3_left

## FND-00002189: TPS61220 boost converter feedback network correctly analyzed with accurate Vout estimate

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev3_left_ErgoSNM_v3_left.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The rev3 left schematic uses U2 (TPS61220DCK) as a boost converter for battery voltage (+BATT) to VDD. The analyzer correctly identifies the feedback divider R3=1.2M (top) and R4=220k (bottom) on the FB pin, computes ratio=0.155, and estimates Vout=3.87V using a 0.6V reference (heuristic). The actual TPS61220 Vref is 0.5V which gives ~3.2V, but the output is labeled as 'heuristic' which is honest. The RT9013-33GB LDO (+5V to VDD at 3.3V) is also correctly identified. Both regulators sharing the VDD output rail is correctly captured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
