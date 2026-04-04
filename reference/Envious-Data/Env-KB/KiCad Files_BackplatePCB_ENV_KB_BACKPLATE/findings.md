# Findings: Env-KB / KiCad Files_BackplatePCB_ENV_KB_BACKPLATE

## FND-00000560: LED and resistor components misclassified as 'connector' type due to non-standard reference prefixes; Key matrix detection is accurate: 6 rows, 18 columns, 96 switches, 92 matrix diodes; USB Type-C...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCad Files_MainPCB_ENV_KB.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies row0/row2-6 (row1 missing by design) and all 18 col nets via net_name detection. switches_on_matrix=96 (total 97 minus SW-RST0 reset button). diodes_on_matrix=92 (total 93 minus D89 which is on USBVBUS). The 4 difference between switches(96) and diodes(92) corresponds to the 5 alternate-layout keys (K_63B1, K_64B1, K_81A1, K_81A2, K_50A1) which share diodes with their primary positions.
- RESISTOR0 and RESISTOR1 (5.1k, value '5.1k' / '5.1k ') connect to USB1:CC1 and USB1:CC2 respectively, pulled to GND. usb_compliance shows cc1_pulldown_5k1=pass, cc2_pulldown_5k1=pass. The resistors are correctly typed as 'resistor' in the BOM despite non-standard reference names.
- I2CSDA and I2CSCL are routed to GPIO0/GPIO1 on the Pico and exposed via I2CHeader0 (4-pin header for external I2C devices). The analyzer correctly reports has_pullup=false for both lines. No pull-up resistors exist on this PCB; they are expected on the external I2C device.
- D89 (1n4002, a general-purpose rectifier diode) is on the USBVBUS path. usb_compliance correctly sets vbus_esd_protection=fail since a 1n4002 is not an ESD protection device. The USBVBUS net also has a no_driver ERC warning because no power symbol drives it — correct, VBUS comes from USB host.

### Incorrect
- PowerLED0 (value='LED 3mm', Device:LED footprint) is typed 'connector' instead of 'led' or 'diode'. PowerLedResistor0 (value='47K Resistor') is typed 'connector' instead of 'resistor'. The analyzer falls through to 'connector' when the reference prefix doesn't match standard patterns (D, R). Same issue appears in the HS variant: PowerLED0 (LED 3MM) and PowerLED1 (LED 0805) both typed 'connector'. This also inflates statistics.component_types.connector count.
  (signal_analysis)
- bus_topology reports col width=36 for 18 unique col nets, and row width=12 for 6 unique row nets. The 'width' is counting label occurrences (each net has 2 labels in the schematic: one source, one destination), not the number of distinct signals. The 'range' and 'missing' fields are correct, but 'width' is semantically wrong — it should be the number of unique signals (18 and 6 respectively).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000561: Same LED misclassification as 'connector' type appears in the HS variant

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad Files_MainPCB_HS_EnvKB_HS.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- PowerLED0 (LED 3MM) and PowerLED1 (LED 0805) are both typed 'connector' in the HS variant BOM and component_types statistics. The issue is consistent across both schematics — affects any component whose reference prefix doesn't match a standard classifier pattern but whose value/lib_id identifies it as an LED.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
