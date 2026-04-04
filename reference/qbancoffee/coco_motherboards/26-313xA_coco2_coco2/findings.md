# Findings: coco_motherboards / 26-313xA_coco2_coco2

## FND-00000286: CoCo2 motherboard 26-313xA (KiCad 5, 152 components). Largely accurate. R8+C21 pull-up/termination on VDGCLK misclassified as LP filter. TC1 trimmer not counted as crystal load cap.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 26-313xA_coco2_coco2.sch.json
- **Created**: 2026-03-16

### Correct
- 14.318MHz crystal X1 with C13 (39pF) load cap correct
- Cassette interface RC filters (R5+C26, R23+C32, R22+C33) correct
- R14+C8 LP at 1.59Hz power-on reset RC correctly detected
- Q1 KSD880O driven by SC77527P correctly identified
- Q2 2N3904 with collector=GNDS correctly captured
- R12+C15 and R29+C17 clock filters at 28.42MHz correct

### Incorrect
- R8(10K)+C21(150pF) classified as LP filter at 106kHz on VDGCLK — this is a pull-up/termination bias network from +5V, not a signal-path filter
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- RC filter: resistor connecting from power rail (+5V) to a clock net via cap should be classified as pull-up/bias, not LP filter
- Crystal detector should include variable/trimmer caps as load cap candidates

---
