# Findings: OtterCastAudioV2 / OtterCastAudioV2

## FND-00000059: AE1 antenna connector classified as "other"

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- AE reference prefix not recognized. AE1 antenna connector classified as "other" instead of antenna/connector.
  (components)

### Missed
(none)

### Suggestions
- Add AE reference prefix as antenna component type

---

## FND-00000061: RF antenna matching network not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- Pi-match from AP6236 to U.FL connector (C78+L5+C77+C75). rf_chains=[]. RF antenna matching network not detected.
  (signal_analysis.rf_chains)

### Suggestions
- Add RF matching network detection for pi/T/L topologies near antenna connectors

---

## FND-00000062: LC filter falsely merges series+shunt caps as parallel

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- C78 (series DC block) and C77 (shunt to GND) merged as "parallel" in LC filter detection. These are different filter topologies.
  (signal_analysis.lc_filters)

### Missed
(none)

### Suggestions
- Distinguish series DC-blocking caps from shunt-to-ground caps in LC filter topology analysis

---

## FND-00000063: AP6236 WiFi module classified as switching power regulator

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- AP6236 has internal DCDC converter but primary function is WiFi/BT module. Classified as switching power regulator instead of wireless module.
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Prioritize primary function classification — WiFi/BT modules with internal DCDC should be classified as wireless, not power regulators

---

## FND-00000064: SDIO bus protocol not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- WL_SDIO_CLK/CMD/D0-D3 with pull-ups and termination. No SDIO category in bus protocol detection.
  (signal_analysis.bus_protocols)

### Suggestions
- Add SDIO bus protocol detection (CLK/CMD/D0-D3 pattern)

---

## FND-00000066: PCM/I2S audio bus not detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- BT_PCM_CLK/SYNC/DIN/DOUT audio bus signals not detected. No PCM/I2S bus category.
  (signal_analysis.bus_protocols)

### Suggestions
- Add PCM/I2S audio bus detection (CLK/SYNC or BCLK/LRCK + data lines)

---

## FND-00000067: Decoupling caps not assigned per-pin

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- 4 caps on +3V3 counted as one group for 2 separate power pins. Decoupling analysis does not assign caps to specific power pins.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Assign decoupling caps to specific power pins based on proximity or net connectivity

---

## FND-00000069: X1 EN pin unconnected without warning

- **Status**: new
- **Analyzer**: schematic
- **Source**: OtterCastAudioV2.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- X1 EN pin is a single-pin unnamed net not reported in single_pin_nets.
  (single_pin_nets)

### Suggestions
- Report single-pin unnamed nets for all components, including passive/oscillator types

---
