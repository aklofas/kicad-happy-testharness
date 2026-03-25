# Findings: kicad_pcb_schematics / mini_projects_others_s6_ece_b_2k22_water_irigation_water_irigation

## FND-00002363: Solenoid valves (U4, U5) and relay (U2) classified as 'ic' instead of actuator/other; Power rails 12v, 9v, 5v_Vin+, and 3.3v not recognized as power rails in statistics

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_pcb_schematics_mini_projects_others_s6_ece_b_2k22_water_irigation_water_irigation.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U4 and U5 use lib_id 's6_projects:Solenoid_Valve', and U2 uses 's6_projects:Realy s6 ec' (a relay). These are electromechanical actuators, not ICs. The analyzer assigns them type 'ic', inflates the ic count (10 vs actual ~2 true ICs: ESP32 + DHT11), and causes both solenoid valves to appear as having 2 unconnected pins each in ic_pin_analysis. The BJT transistors Q1/Q2 that drive them have load_type='ic' as well — a secondary misclassification. The relay U2 is also contributing a single-pin-net for '9v DC-'.
  (statistics)

### Missed
- The design uses multiple named voltage nets: '12v', '9v DC+', '5v_Vin+', and '3.3v'. The statistics.power_rails list contains only ['GND'] — none of the voltage supply nets are recognized. The design_analysis.net_classification also labels '12v', '3.3v', '5v_Vin+', and '9v DC+' as 'signal' rather than 'power'. The power_budget key is entirely absent from the output. This is a missed detection for a multi-rail design (ESP32 3.3V logic, DC motor 12V, solenoid valves 9V).
  (statistics)

### Suggestions
(none)

---

## FND-00002364: Empty PCB layout correctly reported with zero footprints and no board outline

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad_pcb_schematics_mini_projects_others_s6_ece_b_2k22_water_irigation_water_irigation.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The water irrigation .kicad_pcb file is an empty stub (KiCad 9.0, file version 20241229) with no placed footprints, no tracks, no vias, no zones, and no board outline. The analyzer correctly reports footprint_count=0, net_count=0, track_segments=0, board_width=null, and routing_complete=true (vacuously). The copper_presence warning about unfilled zones is appropriate context.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
