# Findings: crazyflie2-exp-template-electronics / ecad_template

## FND-00002308: Blank expansion template correctly parsed: 3 components, 20 unconnected nets, no signal detection; SPI and I2C interfaces exposed on connector pin names not reflected in bus_analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_crazyflie2-exp-template-electronics_ecad_template.sch.json
- **Created**: 2026-03-24

### Correct
- The crazyflie2 expansion board template has only P1 (CF_EXP_LEFT, 10-pin), P2 (CF_EXP_RIGHT, 10-pin), and B1 (bitcraze_200 logo/mechanical). All 20 nets are unconnected (__unnamed_*) because no wires join any pins. The analyzer correctly reports no bus protocols, no signal analysis, and no power rails — appropriate for a template schematic with no routing.

### Incorrect
(none)

### Missed
- P1 (CF_EXP_LEFT) has pins named SDA and SCL; P2 (CF_EXP_RIGHT) has pins named SCK, MISO, MOSI. These are standard I2C and SPI pin names from the Crazyflie expansion connector spec. Since no wires connect them, all nets are unnamed and bus_analysis reports empty lists for i2c and spi. This is expected behavior for an unrouted template, but worth noting that pin-name-based inference (without nets) is not performed.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002309: Unrouted template PCB correctly reports 0 tracks, 0 vias, routing_complete: false

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_crazyflie2-exp-template-electronics_ecad_template.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The crazyflie2 template PCB has 3 footprints, no copper routing (track_segments: 0, via_count: 0), 20 unrouted nets, and routing_complete: false. Board outline is correctly parsed (15 edges) and the file version 4 (KiCad 5 legacy) is handled. kicad_version reports 'unknown' which is acceptable for this older file format.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
