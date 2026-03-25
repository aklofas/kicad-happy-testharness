# Findings: bldc / hardware_Control_control_v1

## FND-00002278: Serial signal nets +RX and +TX misclassified as power rails

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bldc_hardware_Control_control_v1.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer reports power_rails=['+RX', '+TX', 'GND'] for this sheet. The +RX and +TX nets are differential RS-422 signal lines driven by the DS89C21 transceiver — they are not power supply rails. The same misclassification appears in hardware_Operator_Operator.sch which reports power_rails=['+RX', '+Tx', 'GND']. KiCad 5 legacy schematics use PWR_FLAG symbols to mark power nets, but the naming convention (+signal) appears to have triggered a false positive in the power rail heuristic.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002279: 48V, 12V, and 5V power rails not reported in power_rails list

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bldc_hardware_Power_bldc_v1.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The power board is a BLDC motor controller with explicit 48v, 12v, and 5v net names visible in the extracted nets list. Only 'GND' appears in statistics.power_rails. The 5v and 12v nets are outputs of gate driver ICs (UCC27211A) and the AD8410 current sense amplifier operates from a supply net; all three voltage levels are clearly power distribution nets. The analyzer apparently requires PWR symbols or specific naming conventions it did not match for these nets.
  (statistics)

### Suggestions
(none)

---

## FND-00002280: TL2575HV-ADJ buck regulators not detected by voltage regulator detector

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_bldc_hardware_Control_powerconverters.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The power converters sheet contains two TL2575HV-ADJ adjustable step-down switching regulators (U1, U2), each with the classic inductor-diode-capacitor topology. The component type is correctly identified as 'ic', but detectors is empty — no voltage_regulators, switching_regulators, or buck_converter entries. This sheet has 1N5819 Schottky diodes, 680uH and 330uH inductors, and large bulk capacitors (330uF, 1.2mF) that together form a canonical buck regulator circuit. The same design also appears in hardware_Control_control_v1.sch (same components) with the same miss.
  (detectors)

### Suggestions
(none)

---

## FND-00002281: 48V, 12V, and 5V power nets excluded from power_net_routing and current_capacity analysis

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_bldc_hardware_Power_bldc_v1.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The BLDC motor controller PCB has three voltage rails (/48v, /12v, /5v) that all have significant track routing: /48v has 135mm total length with 122 vias and a 4159mm² copper zone (the largest zone on the board), /12v has 146mm total length, and /5v has 160mm total length. Despite this, power_net_routing and current_capacity.power_ground_nets only contain '/GND'. The nets appear correctly in net_lengths, showing the analyzer can parse them but fails to classify them as power nets. The leading slash in KiCad hierarchical net names (/48v vs 48v) likely prevents the power-net heuristic from matching them.
  (power_net_routing)

### Suggestions
(none)

---

## FND-00002282: F.SilkS extends 36mm beyond Edge.Cuts height but alignment reported as True

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_bldc_hardware_Control_Gerber.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The layer extents show Edge.Cuts height = 88.9mm while F.SilkS height = 125.03mm — the silkscreen layer is 36.1mm taller than the board outline. This is a real alignment anomaly (silkscreen text or graphics placed well outside the board boundary), but alignment.aligned is reported as True with an empty issues list. The alignment checker appears to only flag mismatches between copper and edge-cut layers, and silkscreen layers fall outside its comparison scope.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
