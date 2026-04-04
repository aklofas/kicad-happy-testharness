# Findings: car_usb_power_adapter / car_usb_power_adapter

## FND-00002314: MC34063AD buck regulator topology reported as 'unknown' instead of 'buck'; False positive RC low-pass filter: R4+C3 is feedback resistor plus output cap, not a signal filter; R3 (0.22Ω) on MC34063 ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_car_usb_power_adapter_car_usb_power_adapter.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1 (MC34063AD, lib_id Regulator_Switching:MC34063AD) is used as a step-down (buck) converter: input is +12V, output is ~5V (TP1 labeled '5V', J1 is USB_A output). The IC datasheet and pin connectivity (SwE→L1+D2 flyback diode) confirm this is a standard MC34063 buck topology. The power_regulators entry has topology='unknown' instead of 'buck'.
  (signal_analysis)
- The analyzer reports an RC low-pass filter (R4=4.7kΩ, C3=470µF, fc=0.07 Hz) between net __unnamed_3 and __unnamed_0. In reality R4 is the upper feedback resistor (from the MC34063 output to its Vfb pin) and C3 is the bulk output capacitor. These are not in a signal filter topology — the 0.07 Hz cutoff is physically implausible as an intentional filter. This false positive arises because the feedback resistor and output cap share adjacent nodes.
  (signal_analysis)

### Missed
- R3 (0.22Ω) connects between the MC34063 SwC (pin 1) and the Ipk/DC pins (pins 7/8). This is the standard peak-current-limiting sense resistor for the MC34063. The current_sense list is empty. The very low value (0.22Ω) and placement on the switch current path are strong indicators of a current-sense resistor that should have been detected.
  (signal_analysis)
- R2 (1.5kΩ, bottom) and R4 (4.7kΩ, top) form the output voltage feedback divider connected to U1 pin 5 (Vfb). This is a classic feedback network for a switching regulator. The voltage_dividers and feedback_networks lists are both empty. The divider should be detected as a regulator feedback network with mid-point on Vfb.
  (signal_analysis)

### Suggestions
(none)

---
