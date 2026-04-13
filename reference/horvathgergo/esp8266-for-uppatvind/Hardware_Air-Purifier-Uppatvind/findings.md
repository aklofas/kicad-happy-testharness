# Findings: horvathgergo/esp8266-for-uppatvind / Hardware_Air-Purifier-Uppatvind

## FND-00002056: MC34063 switching regulator Vref heuristic uses 0.6V instead of 1.25V, producing a wrong Vout estimate of 1.59V instead of ~3.3V; SPI bus detected as false positive: MISO, MOSI, and SCLK pins on ES...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp8266-for-uppatvind_Hardware_Air-Purifier-Uppatvind.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The MC34063AD (U1) is a step-down regulator generating +3V3 from vin. The feedback divider is R6=3.3kΩ (top) and R5=2kΩ (bottom). The MC34063's internal voltage reference is 1.25V, so Vout = 1.25 * (1 + 3300/2000) = 3.3125V. The analyzer assumes vref=0.6V (a generic heuristic, likely borrowed from TL431 or similar), yielding estimated_vout=1.59V. Both the estimated_vout field and the regulator_voltage design_observation repeat this incorrect value. The lib_id is Regulator_Switching:MC34063AD, which could be used to look up the correct Vref.
  (signal_analysis)
- The bus_analysis reports one SPI bus (bus_id=pin_U2) based on the MISO (pin 10), MOSI (pin 13), and SCLK (pin 14) pin names on U2 (ESP-12F). However, each of these pins connects only to a single-pin unnamed net (__unnamed_0, __unnamed_3, __unnamed_4) with wire_count=0 and no other components. The schematic has 8 no_connect markers and these pins are among them. The SPI signals are internal to the ESP-12F flash memory and are not routed to any external device on this schematic.
  (design_analysis)
- The file carries file_version=20211123 which corresponds to KiCad 6 (KiCad 6 introduced the S-expression .kicad_sch format in late 2021 with this version stamp). The analyzer outputs kicad_version='unknown' instead of detecting this as KiCad 6. This affects downstream reporting of KiCad version compatibility.
  (kicad_version)
- The MC34063AD (U1) has L1 (220uH) as a switching inductor, D1 (Schottky 1N5819WS) as a catch diode, and the input rail is 'vin' while the output rail is '+3V3'. This is a classic buck/step-down topology. The analyzer sets topology='unknown', missing an opportunity to identify the regulator type from the circuit structure (inductor + Schottky diode + input rail name).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
