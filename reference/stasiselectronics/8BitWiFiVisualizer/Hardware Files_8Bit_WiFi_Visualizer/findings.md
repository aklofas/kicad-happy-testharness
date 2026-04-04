# Findings: 8BitWiFiVisualizer / Hardware Files_8Bit_WiFi_Visualizer

## FND-00000325: All 28 components reported as missing_mpn despite having 'Manufacturer PN' custom field populated; U2 (74HC595 shift register) has zero pins extracted, making all connected signal nets appear uncon...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware Files_8Bit_WiFi_Visualizer.sch.json
- **Created**: 2026-03-23

### Correct
- The RC filter detection (R2 10k + C5 1uF, low-pass at 15.92 Hz from +3.3V to ESP_EN, with GND) is accurate — this is the ESP8266 enable pin RC power-on reset network. The decoupling analysis is also correct: +3.3V rail has C3 (10uF bulk), C4 (1uF bypass), C2 (1uF output cap of regulator) totaling 12uF; +5V rail has C1 (1uF input cap of regulator). C5 is correctly excluded from decoupling (it is part of the RC filter). These detections are accurate.

### Incorrect
- Every component in the schematic has a custom field F4 named 'Manufacturer PN' with a valid MPN value (e.g., D1='LTST-C150TBKT', U1='AZ1117CH-3.3TRG1', U2='74HC595D,118', J1='U-F-M5DD-Y-L'). The KiCad 5 legacy parser extracts the 'Manufacturer' field correctly (from F7) but does not map 'Manufacturer PN' to the mpn output field, nor 'LCSC Order Number' to the lcsc field. This results in mpn='' and lcsc='' for all 28 components, and all 28 appear in statistics.missing_mpn. Only J3 and J4 (mounting holes) genuinely lack MPNs.
  (statistics)

### Missed
- U2 (74xx:74HC595) has an empty pins list in the components output. As a result, the CLOCK, DATA, LATCH, and CLEAR nets all show 0 component pins despite having point_count=4 (labels exist, wires exist, but no component endpoints resolved). The LED_1 through LED_8 output nets from U2 are also unresolved. This is a systematic failure of the KiCad 5 legacy parser to extract pin information for the 74HC595 from the standard library. U1 (AMS1117 regulator), SW1, SW2, SW3, J1, J2, J3, J4 are also affected with zero pins each.
  (nets)
- U3 (ESP-WROOM-02D) pin 11 (RXD) is placed on net '__unnamed_2' and pin 12 (TXD) on '__unnamed_3', each with point_count=1. Meanwhile, the named nets 'ESP_RX' and 'ESP_TX' exist with point_count=4 (label pairs from J2 and U3 sides) but show 0 component pins. The net label connectivity resolution fails to merge the U3 pin positions with the ESP_RX/ESP_TX text labels in KiCad 5 legacy format. The same issue affects RST (__unnamed_6), EN (__unnamed_9), and GPIO0 (__unnamed_15). Consequence: bus_analysis.uart reports ESP_RX and ESP_TX with devices=[] and pin_count=0.
  (nets)
- U1 is an AMS1117-3.3 LDO linear regulator converting +5V (from USB via J1) to +3.3V. The analyzer detects the component (lib_id=Regulator_Linear:AMS1117-3.3) but reports topology='unknown', input_rail=null, output_rail=null, and estimated_vout=null. This is caused by U1 having zero pins extracted (same root issue as U2), so the analyzer cannot resolve which rail connects to the input vs output pins. The correct result should be: topology='LDO', input_rail='+5V', output_rail='+3.3V', estimated_vout=3.3V.
  (signal_analysis)

### Suggestions
(none)

---
