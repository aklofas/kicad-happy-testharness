# Findings: V3lectronics/SPIRIT / EDA-kicad_cm5-carrier

## FND-00001327: Complex power sheet with BQ25792, AP3032 boost, and MP3429GL correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: power.kicad_sch
- **Created**: 2026-03-24

### Correct
- 93 components across a complex power management sheet correctly parsed. Three switching regulators correctly identified: AP3032 (22V boost for backlight), BQ25792 (charger), MP3429GL (5V switcher). Battery (BAT1) classified as 'connector' which is a minor type imprecision but acceptable for a JST-connected cell.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001328: FPC screen connector (Hirose FH72) misclassified as type 'diode'

- **Status**: new
- **Analyzer**: schematic
- **Source**: screen.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The screen connector DIS1 (Hirose FH72-31S-0.3SHW, a 31-pin FPC connector) is classified as type 'diode'. Its lib_id likely uses a custom SPIRIT library symbol that the classifier incorrectly maps to diode. This is a false type classification from an unrecognized library part.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001329: FPC camera connector (F52Q-1A7H1-11015) misclassified as type 'ic'

- **Status**: new
- **Analyzer**: schematic
- **Source**: camera.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U9 is a 15-pin FPC connector classified as 'ic' due to its U-prefix reference designator. Custom SPIRIT library footprint with U-reference causes the misclassification. This is a known issue with FPC connectors using IC reference designators in custom libraries.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001330: DNP GSM/GPS module and SIM socket correctly parsed with unique_parts=0

- **Status**: new
- **Analyzer**: schematic
- **Source**: GSM-GPS.kicad_sch
- **Created**: 2026-03-24

### Correct
- Correctly identifies 3 components (J2 SIM socket, U2 EG25GGC modem, U1 GPS module) all as DNP. unique_parts=0 is correct since all are DNP and none have MPNs filled. 229 nets reflects the hierarchical label connectivity from the top-level sheet.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001331: copper_layers_used reports 3 but board has 6 copper layers per stackup

- **Status**: new
- **Analyzer**: pcb
- **Source**: cm5-carrier.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB defines a 6-layer stackup (F.Cu, In1.Cu, In2.Cu, In3.Cu, In4.Cu, B.Cu) and layer definitions include all 6. However, copper_layer_names only lists ['B.Cu', 'F.Cu', 'In1.Cu'] and copper_layers_used=3. The analyzer is likely counting only layers that have routed tracks, missing inner layers that are present as power planes (zones only, no tracks). The board is also heavily unrouted (89 unrouted nets), so inner signal layers may have zero track segments, causing them to be excluded from the count.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001332: Top-level hierarchical sheet with 132 components parsed correctly

- **Status**: new
- **Analyzer**: schematic
- **Source**: cm5-carrier.kicad_sch
- **Created**: 2026-03-24

### Correct
- 132 components across a CM5 carrier design (speaker, vibration motors, capacitors, ICs, FPCs) correctly counted. 41 DNP parts flagged. Power rails AGND, GND, VCC, PWR_FLAG all identified. The 9 missing MPNs and 1 missing footprint (R6) accurately reflect incomplete source data.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
