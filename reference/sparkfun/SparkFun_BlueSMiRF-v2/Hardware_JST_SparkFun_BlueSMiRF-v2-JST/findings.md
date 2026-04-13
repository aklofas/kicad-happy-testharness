# Findings: sparkfun/SparkFun_BlueSMiRF-v2 / Hardware_JST_SparkFun_BlueSMiRF-v2-JST

## FND-00000216: SparkFun BlueSMiRF-v2 JST Bluetooth module (38 components). Correct: AP2112K-3.3 LDO detection with 3.3V output, BSS138 level-shifter MOSFETs Q1/Q2 correctly identified, BOM counts and component values verified. Minor: gate resistor topology for level shifters not fully characterized, pull-up resistors R9/R10 not identified as part of level-shifting network.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_JST_SparkFun_BlueSMiRF-v2-JST.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- U2 AP2112K-3.3 LDO correctly identified with topology=LDO, estimated_vout=3.3V, input/output rails correct
- Q1 and Q2 BSS138 N-MOSFETs correctly identified with proper gate/drain/source net mapping and connector load type
- All 38 components correctly counted, BOM values verified (C1=10uF, C2=1.0uF, C3=1.0uF, C4=10uF, 10 resistors)
- Input/output decoupling capacitors for U2 correctly identified (C1+C2 input, C3+C4 output)

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Consider characterizing pull-up/pull-down resistors associated with MOSFET level-shifter circuits

---
