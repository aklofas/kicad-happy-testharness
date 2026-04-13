# Findings: BiggiePete/RTLS_VIC / RTLS_VIC

## FND-00001171: Crystal X1 classified as 'connector' type in BOM; Crystal circuit (X1 + load caps C10/C11 + STM32 XIN/XOT) not detected; TPS63900 buck-boost switching regulator correctly detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RTLS_VIC.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U2 TPS63900DSKR identified as switching regulator with inductor L1, input +ESC_5V, output +3V3. Correct topology detection.

### Incorrect
- X1 (XL2EL89COI-111YLC-26M, lib:CRYSTAL-SMD_4P-L3.2-W2.5-BL_SIT8008BI) is typed 'connector' in the BOM section. The component itself is classified 'ic' but BOM entry says type='connector'. Should be 'crystal' or at minimum not 'connector'.
  (signal_analysis)

### Missed
- signal_analysis.crystal_circuits is empty. X1 is a 26MHz SMD crystal with 18pF load caps C10/C11 connected to STM32F411 pins XIN/XOT. The crystal circuit detector missed this, likely because the custom lib_id ('lib:CRYSTAL-SMD_4P-L3.2-W2.5-BL_SIT8008BI') isn't recognized as a crystal symbol.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001172: Antenna AE1 classified as 'ic' type; RF matching networks detected for both U.FL connectors JP1 and JP2; I2C bus with pull-up resistors correctly detected on SCL/SDA

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: radio.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Both U.FL connectors correctly identified as antenna endpoints with matching network components (L1 10nH, C11 47pF) targeting the LoRa antenna AE1. LC filters at GHz-range resonant frequencies are plausible for 915MHz LoRa.
- SCL and SDA detected with 5 devices (U9 STM32, U7 TLV493D, U4 GZP6816D, U3 ICM-42688-P, U1 AHT20) and pull-up resistors R10/R9 to +3V3. Correct.

### Incorrect
- AE1 (value 'Antenna_LoRa 915', footprint '915:915LoRa Antenna') is classified as type='ic' in both BOM and component list. It should be classified as 'antenna' or similar, not 'ic'. This is a library symbol using a custom lib that doesn't match standard patterns.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001173: board_height_mm = 0.0 for circular PCB; 2-layer board with complete routing correctly identified; Back-side component count correct (2 components on B.Cu)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RTLS_VIC.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- routing_complete=true, unrouted_net_count=0, 570 track segments, 144 vias, 76 nets. All consistent with a fully-routed 2-layer design.
- back_side=2 matches the 2 B.Cu footprints visible in the gerber (B.Mask has 17 flash/openings from back-side pads but only 2 footprints reported in PCB analyzer), seems consistent.

### Incorrect
- The PCB has a circular outline (Edge.Cuts contains a single circle with radius ~35mm). The bounding box computes min_y=max_y=92.775 (circle center), giving height=0.0. The correct height should equal the width (35.0mm diameter). The circle endpoint/center extraction is incorrect for bounding box purposes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001174: Spurious alignment warning due to circular board outline being interpreted as zero-height; All required gerber layers present, F.Paste correctly flagged as missing_recommended; Via count (144) and ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: jlcpcb_gerber.json
- **Created**: 2026-03-23

### Correct
- complete=true with all required layers (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts). F.Paste missing_recommended is a valid observation for SMD-heavy boards that may need stencils.
- Drill file shows 144 via holes (0.2997mm) and 58 PTH component holes (1.0008mm) + 3 NPTH, matching PCB via_count=144. Consistent cross-file validation.

### Incorrect
- Edge.Cuts has height=0.0 (the circle is stored as center+endpoint, so the gerber extents only capture one axis), while copper layers have heights ~66-69mm. This triggers 'Height varies by 2.8mm across copper/edge layers' as a false alignment issue. Root cause is the same circle bounding box bug as in PCB analyzer.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
