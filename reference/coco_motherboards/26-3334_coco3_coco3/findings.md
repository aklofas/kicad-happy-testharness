# Findings: coco_motherboards / 26-3334_coco3_coco3

## FND-00000284: CoCo3 motherboard (KiCad 5, 218 components). All core circuits correctly identified: 28.636MHz crystal, MC78L08 8V regulator, 7 NPN transistors (RGB video 2SC1815, power 2N6123, BCX38C buffer), cassette RC filters, 86.83MHz clock filters, 3 voltage dividers. TC1 trimmer cap not counted as crystal load cap.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 26-3334_coco3_coco3.sch.json
- **Created**: 2026-03-16

### Correct
- 28.63636MHz crystal X1 with C60 (33pF) load cap correctly detected
- MC78L08 8V LDO regulator correctly identified
- 7 transistor circuits all correctly identified including Q5/Q6/Q7 RGB video output
- Cassette interface RC filters (R14+C24 HP 72Hz, R18+C25 LP 14kHz) correctly detected
- R64+C61 and R10+C10 clock filters at 86.83MHz correct
- 3 voltage dividers including R31+R32 RF modulator video level divider correct

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Crystal circuit detector should recognize Device:C_Variable/trimmer capacitors as load caps

---

## FND-00000285: CoCo3 motherboard (KiCad 6, 214 components). Three bugs vs KiCad 5 version of same design: (1) C61/R64 replaced by unannotated C?/R? placeholders — 86.83MHz clock filter goes undetected. (2) 0 voltage dividers detected vs 3 in KiCad5 — R31+R32 video divider missed, appears as false RC filter instead. (3) Output schema inconsistency (sheets_parsed=None, net count 271 vs 371).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 26-3334_coco3_coco3.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 28.63636MHz crystal X1 with C60 load cap correct
- 7 transistor circuits correctly identified
- MC78L08 8V regulator correct
- Cassette RC filters correct

### Incorrect
- C61 and R64 absent from component list — multi-path shared symbols resolve to unannotated C?/R? instead of root-sheet annotated instances. 86.83MHz ~CTS clock filter entirely missing.
  (components)

### Missed
(none)

### Suggestions
- KiCad6 parser: prefer annotated path instances over unannotated (ref contains '?') instances
- Audit voltage divider detector for KiCad6 net representations
- Unify output schema between KiCad5 and KiCad6

---
