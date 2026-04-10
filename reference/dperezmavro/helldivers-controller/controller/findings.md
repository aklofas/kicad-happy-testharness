# Findings: helldivers-controller / controller_controller

## FND-00002124: Correctly identifies 9 components: 1 SparkFun Pro Micro module, 4 SPDT toggle switches, 4 Cherry MX push buttons; SPDT switches wired as GND↔+5V voltage selectors feeding MCU GPIO not detected as a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_helldivers-controller_controller_controller.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The BOM correctly enumerates SW2/SW3/SW4/SW5 as SW_SPDT and SW8/SW9/SW10/SW11 as SW_Push with their custom footprints. Power rails +5V and GND are correctly identified. The design_observations note correctly flags U1 has no local decoupling cap on the +5V rail.

### Incorrect
(none)

### Missed
- SW2/SW3/SW4/SW5 each have pin A=GND and pin C=+5V with the wiper (pin B) going directly to ATmega32U4 GPIO pins. This makes each switch deliver either 0V or 5V to the GPIO. The analyzer does not detect this SPDT-as-voltage-selector topology. The signal_analysis.voltage_dividers list is empty even though this is effectively a 2-state voltage source. This is also correct because the ATmega32U4 on the Pro Micro is a 5V device so no damage risk, but the pattern is worth flagging as a non-standard switch wiring.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002125: PCB reports 4 copper layers in layer list but only 2 are used; copper_layers_used is correctly 2

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_helldivers-controller_controller_controller.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB stackup defines 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu), which is a 4-layer PCB template. However, no tracks exist on In1.Cu or In2.Cu — all routing uses only F.Cu and B.Cu. The statistics correctly report copper_layers_used=2, but the layers array includes In1.Cu and In2.Cu as signal layers, which could mislead tools expecting an actual 4-layer board. The gerber B.Cu is exported as L4 (confirming a 4-layer stackup was used), so the board order will be for a 4-layer PCB with two unused inner layers. The analyzer does not flag this as a potential unnecessary cost issue.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
