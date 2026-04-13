# Findings: eugeniobaglieri/LoRa1276-breakout-board / LoRa

## FND-00000862: RF chain not detected for LoRa module U1 (SX1276-based) despite ANT pin present; Most U1 pins on isolated single-pin unnamed nets — KiCad 5 net resolution problem; SPI bus detected on U1 with SCK/M...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LoRa.sch.json
- **Created**: 2026-03-23

### Correct
- bus_analysis.spi correctly identifies the SPI interface on U1 with SCK, MISO, MOSI signals in full_duplex mode. NSS chip select not counted (0) because it is on an unnamed single-pin net.

### Incorrect
- 14 unnamed nets each containing only 1 pin of U1, indicating the KiCad 5 net tracing failed to connect U1 pins to J1 connector pins despite them being routed together on the PCB. The PCB correctly shows all U1/J1 nets linked. The schematic analyzer loses connectivity for this KiCad 5 file.
  (signal_analysis)

### Missed
- rf_chains is empty. U1 LORA1276 has an ANT pin (pin 14, net __unnamed_5) connected to J1 via PCB trace. The analyzer has no detection for LoRa/SX127x modules as RF chains. This is a coverage gap.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000863: C1 courtyard bounding box has zero width (min_x == max_x = 137.16); Single-layer routing (F.Cu only) correctly identified, routing 100% complete

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: LoRa.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- copper_layers_used=1, all 42 track segments on F.Cu, via_count=0, routing_complete=true. Accurate for this minimal LoRa breakout board.

### Incorrect
- C1 courtyard: min_x=137.16, max_x=137.16, min_y=76.01, max_y=78.76 — a degenerate zero-width bounding box. This indicates the courtyard polygon data for the CP_Radial footprint was not parsed correctly, potentially causing false courtyard overlap analysis.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
