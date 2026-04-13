# Findings: mlab-modules/ISM01 / hw_sch_pcb_ISM01

## FND-00000626: BOM groups L1/L2 (Device:L_Small, 0R) with R1/R21 (Device:R, 0R) and assigns all type 'inductor'; Crystal frequency not extracted from part values Y1 (ABS07-120-32.768KHZ) and Y2 (ABM3B-30.000MHZ-1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_ISM01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Regulator detection correctly identifies the LM1117-3V3 in SOT-223, extracts the 3.3V output from the fixed suffix, and links VCC→+3V3 power domains. Decoupling analysis correctly finds 10uF+100nF on VCC and extensive caps on +3V3.
- 11 LC filters detected around the Si1060-A-GM RF transceiver antenna matching network using 18nH/39nH inductors and small pF capacitors. Resonant frequencies match expected Sub-GHz ISM band (868/915 MHz range with harmonic filters).
- VCC is sourced from J1 (a 3x2 header/jumper acting as power input). The PWR_FLAG warnings for VCC, +3V3, and GND are technically valid KiCad ERC issues since no PWR_FLAG symbols are placed. These are real ERC warnings, not false positives.

### Incorrect
- When zero-ohm inductors and zero-ohm resistors share identical value ('0R') and footprint ('Mlab_R:SMD-0805'), the BOM grouper merges them into one line and assigns the type from the first item (L1 = inductor). R1 and R21 are definitively Device:R symbols and should be classified as 'resistor', not 'inductor'. Component-level types are correct (R1='resistor', R21='resistor') but the BOM line type='inductor' is wrong.
  (signal_analysis)
- Both crystal values embed the frequency in the part value string: '32.768KHZ' and '30.000MHZ'. The analyzer outputs frequency=null for both. The Si1060-A-GM connects directly to both crystals (32.768kHz RTC, 30MHz RF). Frequency should be parseable from these standard part number patterns.
  (signal_analysis)

### Missed
- The Si1060-A-GM is controlled via SPI but its SPI pins (MOSI, MISO, SCK, /CS) are routed through the GPIO connector header breakout with generic P0.x/P1.x labels rather than named SPI nets. No SPI detection is shown (bus_analysis.spi=[]). This is a genuine miss — the analyzer should ideally cross-reference the IC datasheet or recognize SPI-capable ICs by lib_id. However, unlabeled nets make this hard to detect automatically; the miss is understandable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000627: M4 edge clearance warning correctly flags mounting hole placed 5.33mm outside board outline; U1 LM1117 thermal pad (pad 4, +3V3, 7.43mm²) correctly identified as having zero thermal vias (adequacy=...

- **Status**: new
- **Analyzer**: pcb
- **Source**: hw_sch_pcb_ISM01.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board outline max_x=183.288mm, M4 is at x=188.622mm — 5.33mm outside the board edge. The warning is legitimate: this mounting hole footprint coordinates are outside the PCB boundary, which is almost certainly a design error (should be at or inside the edge). The negative clearance value correctly signals this anomaly.
- The SOT-223 exposed pad for the LM1117 has no vias to the opposite layer for heat dissipation. The PCB analyzer correctly scores this as 'none' with 0 via_count vs recommended minimum of 5. This is a real thermal design concern for a 3A-capable LDO.
- Board statistics are internally consistent: routing_complete=true, 98 footprints total, 60.45x40.13mm dimensions match both PCB and gerber Edge.Cuts. The heavy use of B.Cu (354 of 433 segments) reflects that most SMD components are on the back side.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000628: Old gerber (KiCad 6 RC) misclassifies 12x 0.2mm component drill holes as vias (via count=141 instead of 129); Old gerber correctly flagged as missing F.Paste (recommended layer)

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_CAM_PROFI.json
- **Created**: 2026-03-23

### Correct
- The KiCad 6 RC export omitted F.Paste and B.SilkS. The analyzer correctly reports missing_recommended=['F.Paste'] while still marking complete=true (since F.Paste is not required). With 29 front-side THT connectors and no front-side SMD pads, missing F.Paste is not critical but the detection is accurate.

### Incorrect
- Without X2 aperture function data, the heuristic classifies all holes ≤0.4mm as vias. The new KiCad 8 gerber set correctly identifies the 0.2mm holes as ComponentDrill (via X2 data), giving via_count=129. The old set reports via_count=141. The analyzer's behavior is correct (uses X2 when available), but the old gerber result is misleading — the 12 extra 'vias' are likely SMA connector center-pin holes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000629: New gerber set (KiCad 8) fully complete: 8 layers including B.SilkS and B.Paste, gbrjob-sourced dimensions, all layers aligned

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-23

### Correct
- The new export correctly includes B.Silkscreen and B.Paste (missing from old KiCad 6 export). The gbrjob provides authoritative board dimensions (60.6x40.28mm). All layer extents align within expected margins. SMD ratio=0.69 correctly reflects predominantly SMD assembly. X2 data gives precise component/via/net counts.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
