# Findings: Seeed-Studio/kicad-mcp-server / tests_fixtures_example_pcb

## FND-00002194: dnp_parts counter reports 0 despite R3 having dnp=yes in source; I2C bus not detected despite SCL and SDA named nets present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-mcp-server_tests_fixtures_example_schematic.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The source schematic has R3 marked (dnp yes) and (in_bom no). The component object correctly captures dnp=true and in_bom=false. However, statistics.dnp_parts is 0 instead of 1. The sourcing_audit correctly excludes R3 (total_bom_components=5), but the statistics block does not count it.
  (statistics)

### Missed
- The schematic has hierarchical labels SDA (bidirectional) and SCL (bidirectional) connected to U1 (ESP32-WROOM-32). The net_classification correctly labels SDA as 'data' and SCL as 'clock', but bus_analysis.i2c is empty. The analyzer should detect an I2C bus fragment from these named nets even if pins are not fully resolved due to missing lib_symbols section.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002195: PCB correctly identifies 4 footprints (schematic has 6 symbols, J1 and R3 absent from PCB)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-mcp-server_tests_fixtures_example_pcb.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The source .kicad_pcb file (KiCad 5 format) has exactly 4 modules: R1, R2, C1, U1. J1 (connector) and R3 (DNP 0R jumper) exist only in the schematic and are not placed in the PCB. The analyzer correctly reports footprint_count=4 and smd_count=4. The net count of 2 (GND and +3V3) also matches the PCB source exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
