# Findings: webbbn/KiCad_Schematics / Dual_Inverter

## FND-00000714: MCP1754ST-3302E/MB LDO voltage estimated as 2.3V instead of 3.3V; JUMPER_3-PIN components A1 and A2 misclassified as type 'ic' instead of 'jumper'

- **Status**: new
- **Analyzer**: schematic
- **Source**: Dual_Inverter_Dual_Inverter.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The MCP1754ST-3302E part has '3302' in its name (3.3V fixed LDO). The analyzer parses the suffix and arrives at estimated_vout=2.3V, triggering a false vout_net_mismatch (30% diff vs +3.3V net). The part name encoding '3302' means 3.3V but the parser misreads it. Same false alarm appears in design_observations as regulator_voltage and regulator_caps warnings.
  (signal_analysis)
- All four JUMPER_3-PIN instances (A1, A2, B1, B2) have the same lib_id but A1 and A2 are typed 'ic' while B1 and B2 are typed 'jumper'. The type assignment appears inconsistent — the classification depends on component reference prefix, but 'A' prefix is being mapped to 'ic' instead of 'jumper'. This is minor but affects component_types counts (reports 4 'ic' when 2 should be 'jumper').
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000715: MIC5353-3.3YMT-TR LDO not detected as power_regulator

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: GPS_Diamond_GPS_Diamond.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U1 (MIC5353-3.3YMT-TR) is a 3.3V LDO but power_regulators list is empty. The same miss occurs in LPLink_Nano (also uses MIC5353-3.3YMT-TR as U3). The lib_id is the full part number from a local library, which the analyzer apparently does not match against any regulator pattern. Both designs have this miss.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000716: copper_layers_used=0, front_side=0, back_side=0 for a 4-layer routed board

- **Status**: new
- **Analyzer**: pcb
- **Source**: GPS_Diamond_GPS_Diamond.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- GPS_Diamond uses KiCad 4 with non-standard copper layer names ('Top', 'Bottom', 'Ground', 'Power') instead of standard 'F.Cu'/'B.Cu'. The analyzer counts copper layers and classifies front/back using the standard names, so it reports 0 copper layers and 0 footprints on either side, even though 38 SMD footprints are present and 340 track segments are routed. track_segments and via_count are still parsed correctly.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000717: Correctly reports routing_complete=false with 2 unrouted nets for an in-progress layout

- **Status**: new
- **Analyzer**: pcb
- **Source**: Power_Controller_Power_Controller.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The PCB analyzer correctly detected the incomplete routing state. footprint_count=16 matches schematic component count, board dimensions 15x14mm are plausible for the design size.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000718: Correctly detects I2C bus with pull-up analysis on IMU_SCL/SDA nets, and UART GPS signals

- **Status**: new
- **Analyzer**: schematic
- **Source**: GPS_Diamond_Sensors.sch.json
- **Created**: 2026-03-23

### Correct
- The I2C bus detection found IMU_SCL/SDA connecting U4 and U5, and flagged missing pull-ups. UART detection found GPS_RX connected to U3 (SAM-M8Q GPS). These findings are accurate for a sensor board with IMU + GPS.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000719: Correctly identifies connector-only adapter board with 4 mounting holes, no active components

- **Status**: new
- **Analyzer**: schematic
- **Source**: NanoPiDuo2_Adapter_NanoPiDuo2_Adapter.sch.json
- **Created**: 2026-03-23

### Correct
- component_types shows only connector (3) and mounting_hole (4), total_components=7. The 4 mounting holes (H1-H4) are properly identified as mounting_hole type not counted in missing_mpn. Reasonable characterization of a passive adapter board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000720: Correctly detects MPM3620A switching regulator with voltage divider feedback network

- **Status**: new
- **Analyzer**: schematic
- **Source**: Power_Controller_Power_Controller.sch.json
- **Created**: 2026-03-23

### Correct
- power_regulators correctly identifies U4 (MPM3620A) as a switching topology with fb_net. The associated voltage_divider (R7 100k / R8) for feedback is also correctly detected. This is accurate for a switcher with external feedback resistors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
