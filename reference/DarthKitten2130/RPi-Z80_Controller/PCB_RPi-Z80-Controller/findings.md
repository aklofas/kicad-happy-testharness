# Findings: RPi-Z80_Controller / PCB_RPi-Z80-Controller

## FND-00001197: Power.sch correctly parsed as empty sub-sheet with no components

- **Status**: new
- **Analyzer**: schematic
- **Source**: Power.sch
- **Created**: 2026-03-23

### Correct
- Power.sch is a sub-sheet referenced by the top-level; it contains only power symbols (no components), so zero components and zero nets is correct. The top-level schematic aggregates it properly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001198: Multi-sheet hierarchical schematic parsed correctly with 91 components across 3 sheets; Q1 transistor incorrectly reported with gate_net='GND'; Q4 transistor incorrectly reported with gate_net='GND...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RPi-Z80-Controller.sch
- **Created**: 2026-03-23

### Correct
- Top-level schematic includes Z80.sch and Power.sch sub-sheets. Component count (91), power rails (+3.3V, +5V, GND), BOM groupings, and i2c bus detection (SCL/SDA with MCP23017 devices) all look accurate.
- Q2 and Q3 (BSS138) are correctly classified as MOSFETs with gate_net on i2C_SCL/i2C_SDA and drain connected to the 5V-side SCL/SDA — correctly reflecting the open-drain level-shifter topology.
- 7 caps on +5V (4.7uF bulk + 5x100nF bypass) and 4 caps on +3.3V (4.7uF + 3x100nF) are accurately enumerated.

### Incorrect
- Q1 (AO3400A N-channel MOSFET) shows gate_net='GND' in transistor_circuits, which would mean it is always off and non-functional. The BZ_GPIO22 net drives the buzzer circuit so Q1's gate should be driven by a GPIO or via a resistor network — 'GND' is almost certainly a net resolution/connectivity bug in the legacy .sch parser rather than the true gate net.
  (signal_analysis)
- Same issue as Q1: Q4 (AO3400A) has gate_net='GND' which makes no functional sense. Likely a net naming/connectivity resolution failure in the legacy KiCad 5 parser for this sheet.
  (signal_analysis)
- design_analysis.bus_analysis.i2c contains four entries — SCL, SDA, GND (classified as SDA line), and +5V (classified as SDA line). GND and +5V are power rails, not i2c signal lines. The BSS138 level-shifter topology (where source connects to +3.3V/+5V and gate to 3.3V-side SDA/SCL) is confusing the bus detector into enumerating power nets as i2c lines.
  (signal_analysis)

### Missed
- Q2+Q3 with R5/R6 form a classic bidirectional i2c level-shifter between 3.3V and 5V domains. The analyzer identifies the individual transistors but does not produce a higher-level 'level_shifter' or 'i2c_level_shifter' detection in design_observations.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001199: Z80 sub-sheet parsed with 59 components (32 LEDs, 8 resistor networks, Z80 CPU) correctly

- **Status**: new
- **Analyzer**: schematic
- **Source**: Z80.sch
- **Created**: 2026-03-23

### Correct
- Component breakdown matches the LED matrix + Z80 CPU + MCP23017 GPIO expanders design. 30 no-connects on Z80 is plausible for unused address/data lines.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001200: PCB parsed correctly: 91 footprints, 2-layer, 89.91x98.05mm, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: RPi-Z80-Controller.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Footprint count matches schematic component count exactly. Board dimensions, via count (539), track length (5102mm), and routing_complete=true are all plausible for a 2-layer RPi hat with Z80 and 32 LEDs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
