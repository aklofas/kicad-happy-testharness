# Findings: mlab-modules/VCAI2C02 / hw_sch_pcb_VCAI2C02

## FND-00001764: 43 components correctly counted with transformer and mounting holes recognized; Isolation barrier correctly detected for ADuM3190ARQZ across GNDD/GNDPWR domains; Isolated DC-DC flyback converter (T...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VCAI2C02.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic has 43 components including TR1 (L01ZxxxS05 transformer), MH1-4 (mounting holes), U1 (ADuM3190ARQZ), U2 (MCP3423), D2 (LED), D3 (CDBHM260L-HF rectifier), L1, and 19 resistors. All are correctly counted.
- The isolation_barriers entry correctly identifies U1 (ADuM3190ARQZ) as an isolation component separating the GNDD (digital/secondary) and GNDPWR (primary power) ground domains.

### Incorrect
(none)

### Missed
- The design implements an isolated flyback converter using TR1 (L01ZxxxS05 transformer), U1 (ADuM3190ARQZ isolated error amplifier), D3 (CDBHM260L-HF rectifier), and L1. The power_regulators array is empty. The isolated converter topology should be detected as a power regulator producing the isolated VCC output.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001765: PCB footprint count (43), net count (25), and via count (54) all correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: VCAI2C02.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analysis shows 43 footprints (9 front/34 back), 25 nets, 54 vias (0.4 mm), 2-layer board 70.61 x 29.97 mm, routing complete with 4 copper zones.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
