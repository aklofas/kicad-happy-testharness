# Findings: airboost-kicad-schematics / airboost-kicad

## FND-00001957: Component count and types correctly identified (8 total: 2 switches, 1 resistor, 1 buzzer, 1 LED, 3 ICs); I2C bus correctly detected on SCL/SDA nets with three devices (SCD30, OLED, Arduino); Missi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: airboost-kicad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies all 8 components. A1 (Arduino Nano), U1 (OLED Display), and U2 (SCD30 CO2 sensor) are classified as 'ic'. R1 is a 150-ohm LED current limiting resistor, BZ1 is a buzzer, D1 is a dual-color LED (LED_Dual_AKA), SW1 and SW2 are push buttons. Component types match the actual schematic.
- The analyzer correctly identifies an I2C bus on I2C.SCL and I2C.SDA with devices U2 (SCD30), U1 (OLED Display), and A1 (Arduino Nano). The has_pullup=False detection is accurate: R1 (150 ohm) is an LED current limiter connected between D1 cathode and GND, not an I2C pull-up resistor. There are genuinely no I2C pull-up resistors in this design.
- The analyzer correctly identifies that R1, BZ1, and D1 have no footprint assigned in the schematic. These three components are in missing_footprint, which matches the source: their footprint fields are empty strings in the .kicad_sch file.
- BZ1 is driven directly from Arduino Nano D8 (pin 11) with no transistor or driver IC in between. The analyzer correctly reports has_transistor_driver=false and direct_gpio_drive=true. The driver_ic is listed as A1 (Arduino Nano).
- The +5V rail is sourced from the Arduino Nano VIN pin (which in PCB net terms appears as a power_in pin type) with no explicit PWR_FLAG symbol. The GND rail similarly lacks a PWR_FLAG. KiCad ERC would flag these, and the analyzer correctly warns about both.

### Incorrect
- The analyzer flags the I2C.SCL and I2C.SDA nets as needing level shifters because U2 (SCD30) is on the 3V3 domain and A1 (Arduino) is on +5V. However, in this design the SCD30 is powered from the Arduino's 3V3 output pin, and the SCD30 datasheet specifies its I2C pins are 5V tolerant (VIH max = VDD+0.5V is a common spec, but the SCD30 is actually 5V tolerant on I2C). The real concern is that SDA/SCL are pulled to neither 3V3 nor 5V (no pull-ups exist), making the level-shifter flag secondary to the missing pull-up issue. The cross-domain flag is technically conservative but misleading for this common Arduino+sensor topology.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001958: PCB correctly identified as unrouted with 5 footprints and no traces; No board outline detected (edge_count=0, null dimensions) — correct for this early-stage PCB; F.Cu layer type reported as 'jump...

- **Status**: new
- **Analyzer**: pcb
- **Source**: airboost-kicad.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 5 footprints (A1, SCD1, U1, SW1, SW2) matching the schematic components that have footprints assigned. The three schematic components without footprints (R1, BZ1, D1) are absent from the PCB. Track segments = 0, routing_complete = false, unrouted_net_count = 6 are all correct for an early-stage layout with no routing done.
- The airboost PCB file has no Edge.Cuts geometry. The analyzer correctly reports edge_count=0 and null board dimensions. This is consistent with a schematic-only design where the PCB layout has not been started beyond placing footprints.
- The airboost .kicad_pcb file stores F.Cu with type 'jumper' (the literal value in the file), which is an unusual but valid KiCad designation. The analyzer faithfully reports this. The copper_layers_used=0 is also correct since there are no track segments.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
