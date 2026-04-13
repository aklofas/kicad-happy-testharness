# Findings: SdtElectronics/Xassette-Asterisk / hw_XassetteAsterisk

## FND-00001766: Component count 144 matches KiCad 5 schematic source; D3 (Device:LED) correctly classified as led, not diode; Two switching regulators (SY8089AAAC) and one LDO (XC6206) detected; Two crystal circui...

- **Status**: new
- **Analyzer**: schematic
- **Source**: XassetteAsterisk.sch.json
- **Created**: 2026-03-24

### Correct
- Analyzer reports 144 total components. Manual count from $Comp blocks in the KiCad 5 .sch file confirms 144 non-power components: 7 ICs, 13 connectors, 33 resistors, 59 capacitors, 12 diodes, 1 LED, 2 crystals, 4 inductors, 2 switches, 5 mounting holes, 2 resistor networks, 3 jumpers, 1 other.
- The schematic has 12 actual diodes (D1, D2, D4, D5-D13) and one LED (D3 using Device:LED). The analyzer correctly splits these into diode=12 and led=1.
- Analyzer finds 5 power regulators: U3, U4, U5 (SY8089AAAC switching), U6 (SY7201ABC boost), U7 (XC6206PxxxMR LDO). This is consistent with the multi-rail power supply design visible in the schematic.
- Y1 and Y2 are both found with correct load capacitor pairs (18pF each, effective load 12pF). Y2 at 24MHz is the USB PHY crystal. Both crystal circuits correctly identified.
- The analyzer detects the TWI2-SDA net as an I2C signal, correctly identifying U1 (F133 SoC) as the controlling device. The has_pull_up=false is correct — no external I2C pull-ups are visible in the schematic, likely because the camera module supplies them.
- Analyzer reports 238 total nets, consistent with a complex SoC design with LCD parallel bus (24-bit), CSI camera interface, audio, USB, and multiple power rails.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001767: 2-layer 56x56mm board, 145 footprints, fully routed; DFM advanced tier flagged for 0.1mm annular ring

- **Status**: new
- **Analyzer**: pcb
- **Source**: XassetteAsterisk.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Analyzer correctly reports a 56x56mm 2-layer board with 145 footprints (130 SMD, 8 THT), 2044 track segments, 265 vias, routing_complete=true, and 0 unrouted nets.
- The board uses 0.4mm drill with 0.6mm via pads, giving a 0.1mm annular ring which is below the standard 0.125mm limit. The DFM tier correctly escalates to 'advanced' with one violation.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001768: Brk40p breakout board: 4 components, 2 connectors and 2 mounting holes

- **Status**: new
- **Analyzer**: schematic
- **Source**: auxiliary_Brk40p_Brk40p.sch.json
- **Created**: 2026-03-24

### Correct
- Analyzer correctly identifies this simple adapter board: J1 (Conn_01x40 pin header), J2 (TE FFC connector), H1 and H2 (M3 mounting holes). Total 4 components matches source.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001769: Brk40p adapter board correctly shows 1 unrouted net (GND on mounting pin)

- **Status**: new
- **Analyzer**: pcb
- **Source**: auxiliary_Brk40p_Brk40p.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The GND mounting pin (J2.MP) is unrouted in the PCB, resulting in routing_complete=false and unrouted_net_count=1. This matches the actual board design where J2's mounting pad connects to GND but the trace is not drawn.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001770: Complete 9-layer gerber set detected with no missing layers; 124 via holes in drill file matches PCB via count; Gerber front_side=15 disagrees with PCB front_side=14 by 1 component

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-24

### Correct
- Analyzer correctly identifies 9 gerber files (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) plus 2 drill files (PTH, NPTH). completeness.complete=true and no missing_required layers.
- The PTH drill file contains 124 via holes (0.3mm diameter) matching the PCB analyzer's via_count=124 exactly. 4 component holes (0.6mm) and 2 NPTH holes also present.

### Incorrect
- The PCB analyzer reports 14 components on the front side and 42 on the back. The gerber analyzer reports 15 on the front and 41 on the back. The total of 56 agrees, but the per-side count differs by 1. This is likely caused by a component at the boundary of the two analyses (different attribution of a component to F.Cu vs B.Cu). The discrepancy should be investigated.
  (component_analysis)

### Missed
(none)

### Suggestions
(none)

---
