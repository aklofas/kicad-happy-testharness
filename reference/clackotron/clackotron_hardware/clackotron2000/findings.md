# Findings: clackotron/clackotron_hardware / clackotron2000

## FND-00002307: R-78B5.0-1.0 switching regulator estimated_vout is 1.0V instead of 5.0V; RS-485 differential pair (RS485_A / RS485_B) not detected as differential_pairs; All four level-shifter MOSFETs report spuri...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_clackotron_hardware_clackotron2000_clackotron2000.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies PCF85263ATL (RTC, U1) and ESP32-S3-WROOM (U2) on both SCL and SDA nets, with R3 (10k to +3V3) on SCL and R4 (10k to +3V3) on SDA. Both have has_pull_up: true.
- The analyzer correctly identifies D1 as a single-LED WS2812B chain (protocol: 'single-wire (WS2812)', estimated_current_mA: 60) with data input on LED_Data_5V, and correctly classifies the BSN20 transistors as 'level_shifter' topology for the 3.3V-to-5V level translation network.

### Incorrect
- The analyzer reports estimated_vout=1.0 for U4 (R-78B5.0-1.0) with vref_source='fixed_suffix'. The part number encodes both output voltage (5.0V) and current rating (1.0A) separated by dashes. The parser extracted the last numeric token '1.0' (the current rating) instead of the voltage token '5.0'. This triggers a false vout_net_mismatch observation (80% mismatch against the +5V rail) when the regulator is in fact correctly matched to +5V.
  (signal_analysis)
- Each of the four BSN20 transistors (Q1–Q4) is reported with a led_driver field pointing to D1 (WS2812B) with various gate resistors (R15, R16, R17, R18 at 10k each). Only Q4 actually drives the LED data line (LED_Data/LED_Data_5V). Q1, Q2, and Q3 are level-shifters for DataRX, DataEN, and DataTX respectively — not LED drivers. The association appears to be a false match caused by proximity or shared net heuristics.
  (signal_analysis)

### Missed
- The design uses a MAX481E RS-485 transceiver (U6) with nets RS485_A and RS485_B, each protected by SMBJ12CA TVS diodes (D10, D9). The analyzer detects USB D+/D- as a differential pair but does not identify RS485_A/RS485_B as a differential pair, even though they follow standard naming conventions (_A/_B suffix) and are connected to a known RS-485 IC. The bus_analysis section has no CAN or special RS-485 entry for these nets either.
  (design_analysis)

### Suggestions
(none)

---
