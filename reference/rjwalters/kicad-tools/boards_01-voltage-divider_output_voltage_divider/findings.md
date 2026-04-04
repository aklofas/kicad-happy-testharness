# Findings: kicad-tools / boards_01-voltage-divider_output_voltage_divider

## FND-00002352: Global-label-only schematic: component pins not resolved into named nets, breaking signal path analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-tools_examples_08-label-based-schematic_label_based_mcu.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- This schematic uses only global labels for connectivity (total_wires=0). The analyzer detects 6 components and 9 global labels correctly, but fails to resolve component pin connections through the labels. Net 'VCC_3V3' has point_count=3 (3 label occurrences) but pins=[] — the AMS1117-3.3 output pin is never associated with this net. Consequently U1 shows total_pins=0 in ic_pin_analysis, the power_regulators topology is 'unknown' with null input/output rails, and pwr_flag_warnings fire for +5V and GND rails that are actually driven. The design_observations correctly identify the AMS1117-3.3 as a linear regulator, but the absence of pin-to-net resolution means no decoupling, feedback, or power domain analysis is possible.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002353: U1 MCU placeholder (Connector_Generic:Conn_02x16) classified as 'ic' based on value field, not lib_id

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-tools_boards_03-usb-joystick_output_usb_joystick.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1 has lib_id 'Connector_Generic:Conn_02x16_Counter_Clockwise' (a generic connector symbol used as MCU placeholder) but value='MCU'. The analyzer classifies it as type 'ic' because the value contains 'MCU', overriding the lib_id-based classification. This results in component_types reporting 1 IC and only 2 connectors when there are actually 3 connectors (J1, J2, and U1). The USB detection (USB_D+/USB_D- nets) and crystal circuit detection still work correctly because they rely on net names rather than component type.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002354: PCB correctly identifies incomplete routing in a file named '_routed' (only 2 of 16 nets routed)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad-tools_boards_03-usb-joystick_output_usb_joystick_routed.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The file named 'usb_joystick_routed.kicad_pcb' (implying a routed board) actually has only 2 of 16 nets physically routed, with 14 nets unrouted including GND, VBUS, VCC, and all button/joystick signals. The analyzer correctly reports routing_complete=false with unrouted_count=14. This is a kicad-tools demo board in an intermediate routing state; the analyzer's connectivity analysis correctly captures the partial-routing reality regardless of filename.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
