# Findings: arsenal007/STM32-SDR_PCB / LCSDR

## FND-00001263: R4+C7 RC filter misclassified — pull-up to +3V3 parsed as RC-network with inverted input/output nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: AUDIO_OUT.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- R4 (4.7k) connects PTT_IN to +3V3 (pull-up). C7 (100nF) is a bypass cap from PTT_IN to GND. The analyzer classifies this as an 'RC-network' with input_net=PTT_IN and output_net=+3V3, but the resistor is a pull-up not a filter input. The ground_net='__unnamed_2' is a floating net, not GND — likely a connectivity issue with legacy KiCad 5 net parsing.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001264: power_regulators is empty despite U4 (AP1117-33 LDO) and U5/U7 (MC34063 switching regulators)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PowerSupplay.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- PowerSupplay.sch has three power regulation ICs: U4 (AP1117-33, 3.3V LDO in SOT-223), U5 and U7 (MC34063 DC-DC converters). signal_analysis.power_regulators=[] — all three are missed. The AP1117-33 is a well-known part that should be identified as a linear regulator.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001265: I2C bus not detected despite I2C_SDA and I2C_SCL nets present; also only one crystal load cap detected instead of two

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MCU.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- MCU.sch has I2C_SDA and I2C_SCL global labels connecting to STM32F401 (U3) and FM24CL16B FRAM (U2), but bus_analysis.i2c=[] — bus is not detected. Additionally, crystal Y1 (20MHz) shows only one load cap (C30) in crystal_circuits, but C28 (also 22pF) is the second load cap — only half the crystal circuit is captured.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001266: MOSFET Q1 transistor circuit has drain_net == source_net, indicating incorrect net resolution

- **Status**: new
- **Analyzer**: schematic
- **Source**: switching.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Q1 (2N7002 NMOS) is reported with both drain_net and source_net as '__unnamed_1'. For a switching MOSFET these should be different nets. This is likely a pin-mapping error in the legacy KiCad 5 .sch parser where the GSD pinout is not mapped correctly. The gate_net='__unnamed_0' and source_is_ground=false also suggest the source is not properly resolved to GND.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001267: display.sch parses as empty (0 components) — likely a stub/unfinished sheet in the project

- **Status**: new
- **Analyzer**: schematic
- **Source**: display.sch.json
- **Created**: 2026-03-24

### Correct
- The display.sch sheet has 0 components, 0 nets, 0 wires. This is plausible for a placeholder sheet in a work-in-progress design. The analyzer handles this gracefully with no errors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001268: Top-level hierarchical schematic correctly aggregates 6 sub-sheets (108 components, 236 nets)

- **Status**: new
- **Analyzer**: schematic
- **Source**: LCSDR.sch.json
- **Created**: 2026-03-24

### Correct
- LCSDR.sch parses 6 sheets including syntez, AUDIO_OUT, MCU, PowerSupplay, switching. Component counts and power rails (+12V, +3.3V, +3V3, +9V, GND) look correct. Note +3.3V and +3V3 appear as separate rails — this may be intentional (different parts of the design) or a naming inconsistency worth flagging.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001269: PCB correctly identified as work-in-progress with 68/95 nets unrouted, 112 footprints, 2-layer board

- **Status**: new
- **Analyzer**: pcb
- **Source**: LCSDR.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- routing_complete=false with 68 unrouted_net_count is accurate for an in-progress layout. 112 footprints with 108 mostly on B.Cu (back) and 4 on F.Cu is consistent with a design where components are predominantly on one side. Board dimensions 150x95mm correctly extracted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001270: Fully routed production PCB correctly analyzed: 268 footprints, 390 vias, 4621mm tracks, routing_complete=true

- **Status**: new
- **Analyzer**: pcb
- **Source**: PowerSupplay_LCSDR.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PowerSupplay board is correctly identified as fully routed (0 unrouted nets). 217 SMD + 51 THT component count is plausible for this SDR project. 390 vias on a 100x95.9mm 2-layer board is a high but credible density for a complex analog/RF design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001271: Both gerber outputs correctly analyze the same PowerSupplay gerber directory; F.Paste missing_recommended is accurate

- **Status**: new
- **Analyzer**: gerber
- **Source**: PowerSupplay_gerber.json
- **Created**: 2026-03-24

### Correct
- gerber.json and PowerSupplay_gerber.json both point to the same STM32-SDR_PCB/PowerSupplay/gerber directory and produce identical outputs (7 gerber files, 2 drill files, 529 holes). F.Paste flagged as missing_recommended is correct — the board has SMD parts but no paste layer exported. B.SilkS width 118.667mm slightly exceeds board outline 100mm width, which could indicate silk references outside the board edge but is not flagged.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
