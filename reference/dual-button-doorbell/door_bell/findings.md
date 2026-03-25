# Findings: dual-button-doorbell / door_bell

## FND-00002335: UART bus not detected despite MAX3232 RS-232 transceiver and UART debug connector; Cross-domain level-shifter warnings correctly identified for I2S signals

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_dual-button-doorbell_door_bell.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies that ~{SD_MODE}, BCLK, LRCLK, and DOUT signals cross between the 3.3V domain (ESP32-WROVER-B U6) and the 5V domain (MAX98357A audio amplifier U2), flagging all four with needs_level_shifter: true. The MAX98357A datasheet confirms it is a 5V part with I2S inputs accepting 3.3V logic, so whether a level shifter is strictly needed depends on the I2S input threshold, but the cross-domain detection itself is accurate.

### Incorrect
(none)

### Missed
- The schematic contains a MAX3232 RS-232 transceiver (U5) with RXD0/TXD0 signals connecting to the ESP32-WROVER-B (U6), and a dedicated UART debug connector (J4) labeled 'UART'. Despite the debug connector being found in test_coverage.debug_connectors, signal_paths.bus_analysis.uart is empty. The analyzer should detect the UART bus formed by the MAX3232 and ESP32.
  (signal_paths)

### Suggestions
(none)

---

## FND-00002336: Thermal via adequacy correctly assessed for both LDO regulators

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_dual-button-doorbell_door_bell.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies thermal pad vias for both NCP1117 LDOs (U1 on +5V, U3 on +3V3) with 33-34 vias each against recommended minimum of 9 and ideal of 16, grading them 'good'. The custom SOT-223 footprint with extra thermal pads and via stitching is accurately characterized. The analyzer also notes 1 untented via on U1 with appropriate solder-wicking warning.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002337: 4-layer Gerber set correctly validated as complete with all inner copper layers

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_dual-button-doorbell_gerber.json.json
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly finds all 9 expected layers (F.Cu, B.Cu, In1.Cu, In2.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts) with zero missing or extra layers, using the .gbrjob file as the completeness source. Board dimensions match the PCB output (68.81x68.8mm). Alignment is confirmed good.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
