# Findings: juanalbapraska/Robot_Velocista / Robot_Velocista-master_PlacaAtras_placadeatras

## FND-00001212: Empty PCB correctly parsed as a KiCad version 4 dummy/stub file; kicad_version reported as 'unknown' instead of 'KiCad 5 (legacy)' for version 4 file

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: placadeatras.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The file contains only '(kicad_pcb (version 4) (host kicad "dummy file") )' — a placeholder with no layout data. The analyzer correctly outputs zeroed statistics and does not crash.

### Incorrect
- Both SensoresForward PCBs (file_version 20171130) also report kicad_version='unknown'. The PCB analyzer is not mapping file_version values to human-readable KiCad version strings the way the schematic analyzer does (it correctly reports '5 (legacy)'). This affects the PlacaAtras PCB (version 4) and both SensoresForward PCBs (version 20171130 = KiCad 5).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001213: PlacaAtras schematic correctly parsed with Arduino Nano, connectors, I2C/UART bus detection, and unannotated ref detection; RESET pin reported on two different nets (DIST_FRONT and DIST_DCHA) — lik...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: placadeatras.sch
- **Created**: 2026-03-24

### Correct
- The 5-component schematic (Arduino Nano, diode, resistor, switch, connector) is correctly parsed. All annotation issues flagged (all refs are unannotated, '?' suffixed). I2C bus (SCL/SDA) and UART (BT_TX/BT_RX) correctly detected. Single-pin nets correctly flagged for unconnected global labels.

### Incorrect
- Arduino_Nano_v3.x has multiple RESET pins in KiCad (pin 28 and pin 3 both named RESET — one is the power-side reset, one is the signal pin). The analyzer maps both to the same pin name 'RESET', causing two reset_pin observations with different nets. The actual design likely only uses one. This causes two spurious reset_pin design_observations that also lack pullup/filter cap.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001214: CNY70 IR reflectance sensor array + CD4053 analog mux correctly identified with subcircuits; Decoupling warnings falsely flagged for CNY70 opto-reflectance sensors; CD4053 analog multiplexer circui...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Robot_Velocista-master_SensoresForward_SensoresForward.sch
- **Created**: 2026-03-24

### Correct
- All 6 CNY70 sensors correctly parsed with subcircuit neighbor analysis showing the 82-ohm LED driver resistors and 10k pull-up resistors. The 4053 triple analog mux with sensor inputs and line select outputs is correctly mapped. Component count (17), net count (28), and BOM all correct.

### Incorrect
- U1, U3, U5 (CNY70) are flagged as needing decoupling caps on +5V. CNY70 is an opto-reflectance sensor (phototransistor + IR LED pair), not a digital IC. It does not require bypass/decoupling capacitors. U2, U4, U6 are correctly excluded since their LED anode is driven through a series resistor, not directly from +5V. The 4053 mux (U7) decoupling warning is valid.
  (signal_analysis)

### Missed
- The CD4053 (triple 2:1 analog mux) driving a 6-sensor array into 3 multiplexed output lines is a recognizable sensor multiplexing pattern. The analyzer has no mux/switch IC detector, so it only appears in subcircuits. Not a critical gap but a missed opportunity for a more informative output.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001215: Fully routed SensoresForward master PCB correctly analyzed: 19 footprints, 2-layer, routing complete, DRC clean; REF** fabrication markers flagged as edge clearance warnings at 0.0mm

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Robot_Velocista-master_SensoresForward_SensoresForward.kicad_pcb
- **Created**: 2026-03-24

### Correct
- All 19 footprints parsed with correct pad-net assignments. Routing complete (18/18 nets routed, 7 vias). Courtyard overlap (J1 vs U7, 10.3 mm²) and U7 edge clearance violation (-0.46mm, outside board edge) correctly detected. DFM tier standard with 0.25mm trace width. Board dimensions 62.23×30.48mm correct.

### Incorrect
- Two 'REF**' entries in edge_clearance_warnings with edge_clearance_mm=0.0 are non-actionable noise. REF** is a KiCad fabrication-layer placeholder reference (not a real component), and 0.0mm edge clearance means it is at the board edge — probably a fab note intentionally placed there. These should be filtered out of placement warnings.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001216: Incomplete SensoresForward root PCB correctly reports 6 unrouted nets with pad lists; Layer transitions without vias flagged for Net-(R1-Pad2) and Net-(R4-Pad2) — likely a micro-segment artifact, n...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SensoresForward_SensoresForward.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 17 footprints, routing_complete=false, 6 unrouted nets (/linea1, /linea2, /linea3, /linea_selec, /sensor3, /sensor5) all listed with correct pad counts and component references. This is an earlier/in-progress version of the design.

### Incorrect
- Both nets show a 0.013mm F.Cu segment alongside larger B.Cu segments with zero vias. A 13-micron segment is almost certainly a routing artifact (sub-pixel segment from pad endpoint alignment) rather than an intentional cross-layer connection. The layer_transitions section surfaces this as if it were a via-less layer crossing, which is misleading for such small segments.
  (signal_analysis)
- The source file has an Edge.Cuts layer but the analyzer reports null dimensions and zero edge_count in board_outline. Checking the file confirms Edge.Cuts exists (grep finds 1 match). The KiCad 5.0 format for this older file may use a different Edge.Cuts representation that the analyzer fails to parse, causing the board outline to be missed.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
