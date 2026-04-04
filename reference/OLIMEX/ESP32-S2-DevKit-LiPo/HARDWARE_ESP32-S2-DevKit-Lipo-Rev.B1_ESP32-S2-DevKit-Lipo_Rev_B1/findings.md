# Findings: ESP32-S2-DevKit-LiPo / HARDWARE_ESP32-S2-DevKit-Lipo-Rev.B1_ESP32-S2-DevKit-Lipo_Rev_B1

## FND-00000542: Component counts and BOM are accurate; Power rails correctly identified: +3.3V, +5V, +5V_USB, GND, VBAT, Vin; Crystal circuits detected correctly: 12 MHz (CH340T) and 32.768 kHz (optional RTC); Add...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_ESP32-S2-DevKit-Lipo-Rev.B1_ESP32-S2-DevKit-Lipo_Rev_B1.sch.json
- **Created**: 2026-03-23

### Correct
- 80 total components, 43 unique parts, correct breakdowns for resistors (25), capacitors (23), diodes (6), crystals (2), etc. All match the source.
- All six named power nets are present and correctly classified.
- Q1 12 MHz with dual 27 pF load caps giving 16.5 pF effective load (correct, within spec). Q4 32.768 kHz without load caps (DNP/optional).
- Chain length 1, single-wire WS2812 protocol, 60 mA estimate. Detection is correct, though the DIN net is wrong (see separate entry).
- Three capacitors flagged with < 50% derating margin on 5 V rails. This is a real design observation worth noting.

### Incorrect
- LED_ENABLE1 has value 'Soldered', lib_id 'ESP32-S2-DevKit-Lipo_Rev_B1:SJ', and footprint 'OLIMEX_Jumpers-FP:SJ_1_SMALLER'. It is a solder jumper, not an LED. The component counter increments 'led' count for it. BAT_SENS_E1 has the same SJ footprint but is typed as 'connector', also wrong — it should be 'jumper' like PWR_SENS_E1.
  (signal_analysis)
- The rf_chains section lists 5 'transceivers': U1, U2, U3, U4, VR1. Only U4 (ESP32-S2 with WiFi) is genuinely an RF transceiver. An LDO regulator, a USB-UART bridge, a LiPo charger, and a power switch have no RF function. This is a systematic false positive in the RF chain detector.
  (signal_analysis)
- The analyzer reports RGB-LED1 pin 2 (DIN) on the GND net. In the actual schematic, the DIN pin is connected through R24 (22R series resistor) to the GPIO18\RGB_LED net. R24 is simultaneously placed on the VCC supply rail (__unnamed_62) and GND, which is also wrong. This appears to be a pin-position computation error for KiCad 5 legacy components with transform matrix (1 0 0 1) — the resulting pin coordinates don't match the wire endpoints in the source. GPIO18 is correctly identified as the RGB_LED control line in labels and net classification.
  (signal_analysis)

### Missed
- VR1 is an LDO regulator converting Vin to +3.3V and is the primary 3.3 V supply for U4 (ESP32-S2). It should appear in power_regulators or a linear_regulators section. The power_regulators list is empty. VR1 does appear in power_domains correctly (linking +3.3V and Vin rails), but no regulator-specific analysis is produced.
  (signal_analysis)
- The design has resistor networks feeding GPIO7 (PWR_SENS) and GPIO8 (BAT_SENS) via solder-jumper enables. R17 (10k) + R18 (1k) + R12 (4.7M) + R13 (470k) feed into the BAT_SENS enable node; R9 (10k) + R10 form another. These are ADC input conditioning/divider networks. voltage_dividers list is empty. The RC filter detector does find some of these resistors paired with C12, but the resistive divider topology is missed.
  (signal_analysis)
- U1 is a single-cell LiPo charge management IC (BL4054B, equivalent to TP4054/MCP73831). It is connected to VBAT and +5V with a programming resistor R6 (2.2k). Neither bms_systems nor any charger-specific detector surfaces this. The subcircuit entry for U1 is minimal (only R6 as neighbor), and no charger observation is generated.
  (signal_analysis)
- The bus_analysis UART section only identifies GPIO43/44 of U4 (ESP32-S2), not the CH340T (U2) as the bridging IC. The UART bridge between USB (U2) and the ESP32-S2 UART0 is the core programming/debug interface and should be explicitly identified as a USB-UART topology.
  (signal_analysis)

### Suggestions
(none)

---
