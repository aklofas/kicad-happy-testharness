# Findings: glr-2024e-display-can-shield / glr-2024e-display-can-shield

## FND-00002104: UART false positive: CAN transceiver TX0/RX0 pins detected as UART bus; design_observations reports IC1 +5V rail has no decoupling caps despite C1 being present on its VS pin; LDO regulator correct...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_glr-2024e-display-can-shield_glr-2024e-display-can-shield.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies IC2 LF80CDT-TR as an LDO with input_rail: +12V and output_rail: +8V. The protection_devices detector correctly finds D1 ESDCAN01-2BLY as an ESD IC protecting CAN H and CAN L nets. The regulator_caps design observation correctly flags that the LDO has no decoupling caps on either its +12V input or +8V output.

### Incorrect
- IC1 is an L9615D013TR 'High Speed CAN Bus Transceiver'. Its TX0 and RX0 pins are the digital-side interface to the MCU (standard CAN transceiver architecture). These connect to nets named 'Tx' and 'Rx'. The bus_analysis detects two UART entries based on these net names (one for 'Tx', one for 'Rx', each crediting IC1). This is a false positive — the TX0/RX0 of a CAN transceiver are not a UART; they are the CAN controller-side logic signals. Meanwhile bus_analysis.can is empty, missing the actual CAN bus that IC1 implements.
  (design_analysis)
- IC1 (L9615D013TR) pin 3 (VS, +5V) shows has_decoupling_cap: true with decoupling_caps: [{C1, 0.1uF 50V}] in the ic_pin_analysis. However, design_observations for IC1 shows rails_without_caps: ['+5V'] and rails_with_caps: []. This is the same inconsistency seen in the BMS shield: the pin-level decoupling detection is correct, but the design_observations aggregator incorrectly reports no caps. The missing regulator caps warning for IC2 (LDO with no input/output caps) is legitimately correct.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
