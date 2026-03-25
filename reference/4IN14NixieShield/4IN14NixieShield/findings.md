# Findings: 4IN14NixieShield / 4IN14NixieShield

## FND-00000319: Four WS2812B LEDs in a single daisy-chain reported as 4 separate chains of length 1; WS2812B chain total length should be 4 but each sub-chain reports length 1; IN-14 Nixie tubes (N1–N4) not identi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: tubes.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- D2, D3, D4, and D5 are connected in a single WS2812B chain: NEOPIXEL → R9 → D2 DIN, D2 DOUT → D3 DIN (wire at coords 2100,3900–3700,3900), D3 DOUT → D4 DIN (coords 4300,3900–7400,3900), D4 DOUT → D5 DIN (coords 8000,3900–9600,3900), D5 DOUT NoConnect. The analyzer reports 4 separate chains each with chain_length=1 instead of one chain with chain_length=4. The data-out to data-in connections are made via unlabeled wires that the chain-stitching logic is failing to follow.
  (signal_analysis)

### Missed
- Each of the 4 detected addressable_led_chains has chain_length=1. The correct detection would be a single chain with chain_length=4 covering D2→D3→D4→D5. This means estimated_current_mA is reported as 60mA per pseudo-chain (240mA total spread across 4 entries) rather than as 240mA for the full chain.
  (signal_analysis)
- Four IN-14 Nixie tubes (N1, N2, N3, N4) operate at approximately 170V DC on their anodes (ANODE_1 through ANODE_4 hierarchical labels). The analyzer classifies them as component type 'other' with no design_observation about high-voltage operation. There is no HV rail detected on this sheet (HV supply comes in through the ANODE_* hierarchical labels from another sheet). No protection_devices or high-voltage observations are generated for the Nixie tube circuit.
  (signal_analysis)
- NL1 is an IN-3 neon indicator lamp connected between ANODE_DOT (high voltage) and GND through R8 (4k7 current-limiting resistor). This is a classic neon lamp driver circuit with ballast resistor. The analyzer does not detect this as a protection_device, current_sense, or any other structured circuit. R8 and NL1 are isolated findings with no circuit relationship identified.
  (signal_analysis)

### Suggestions
- Fix: Four WS2812B LEDs in a single daisy-chain reported as 4 separate chains of length 1

---
