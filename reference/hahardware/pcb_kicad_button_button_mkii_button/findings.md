# Findings: hahardware / pcb_kicad_button_button_mkii_button

## ?: BLE button design with STBlueNRG-1: good component/BOM extraction, but U2 LDO pins misassigned to GND net, crystal load caps half-detected, LDO regulator not detected, RF matching missed

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_kicad_button_button_mkii_button.sch.json
- **Created**: 2026-03-23

### Correct
- Total component count of 64 is correct across 3 sheets (main, RF matching, peripherals)
- 25 capacitors correctly identified across all three sheets
- 15 resistors correctly identified
- 2 crystals (Y1 32.768kHz, Y2 32MHz) correctly detected
- 8 test points correctly identified
- 3 sheets parsed (main, button_rf, peripherals_button)
- Battery BT1 correctly identified as battery type
- U1 STBlueNRG-1 subcircuit correctly identifies neighbor components including L1, C10-C14, Y1, R3-R6, R11-R12, R16
- D3 and D4 correctly identified as Schottky diodes (Power thru Battery)
- LC filter correctly detected: L1 (10uH) with parallel C10+C11, resonant at ~159kHz for SMPS filter
- Decoupling analysis on +3.3V rail correctly identifies 5 capacitors (C7, C6, C9, C24, C22) totaling ~1.02uF
- Both +3.3V and +3V3 power rails correctly identified as separate nets
- PB1 pushbutton correctly identified as connector type with SW_PUSH-12mm footprint
- 9 no-connect markers correctly counted (NoConn lines in schematic)
- Both crystal circuits detected with correct frequency values (32MHz and 32.768kHz)

### Incorrect
- U2 (TLV1117LV-3V LDO) pins 2 (OUT) and 3 (VIN) are incorrectly placed on the GND net. The OUT pin should connect to +3V3 rail (via C21) and VIN should connect to the input supply (via C20/J1). Meanwhile U2 pin 1 (GND) is on orphan __unnamed_41 instead of the GND net. This appears to be a pin-mapping mismatch: the schematic uses lib_id LT1129CST-3.3 but the actual part is TLV1117LV-3V.
  (nets.GND)
- Y2 (32MHz crystal) only has 1 load cap detected (C15 33pF) but should have 2: C14 (27pF) on one side and C15 (33pF) on the other side, connected to FXTAL0 and FXTAL1 pins of U1
  (signal_analysis.crystal_circuits)
- Y1 (32.768kHz crystal) only has 1 load cap detected (C12 27pF) but should have 2: C12 (27pF) and C13 (22pF), connected to pins via the crystal oscillator circuit
  (signal_analysis.crystal_circuits)
- U2 subcircuit has zero neighbor_components, but should include at least C20 (input cap), C21 (output cap), and possibly the +3V3 power symbol connections. The empty neighbor list suggests the pin net assignment error prevented proper neighbor detection.
  (subcircuits)
- RC filter with R14/C18 has ground_net listed as +3.3V instead of GND. R14 connects BUTTON signal to C18, and C18's other terminal goes to +3.3V (as a pull-up decoupling). The ground reference for this filter is actually the +3.3V rail, which is technically valid for a high-side filter but the naming is confusing.
  (signal_analysis.rc_filters)

### Missed
- TLV1117LV-3V (U2) is a 3.3V LDO voltage regulator converting battery voltage to 3.3V, but power_regulators is empty. This is the primary power supply for the entire design.
  (signal_analysis.power_regulators)
- RF matching network not detected: BAL1 (STBNR1_balun) with matching components C16, C17 (TBD), L2 connects STBlueNRG-1 RF pins to antenna pad via a balun+filter topology. This is a BLE 2.4GHz RF front-end.
  (signal_analysis.rf_matching)
- Schottky diode protection circuit (D3, D4) providing reverse-current protection for battery charging is not detected as a protection device. These prevent reverse current flow from the supply into the coin cell battery.
  (signal_analysis.protection_devices)
- Multi-stage SMPS input filter not characterized: the VBATT path uses R7-R8-R9-R10 (1k each) as series isolation resistors with parallel decoupling caps (C1/C2/C3, C4/C5/C6, C7/C8/C9, C22/C23/C24) forming a 4-stage pi-filter for the BlueNRG-1 SMPS supply.
  (signal_analysis.rc_filters)
- ADC1 and ADC2 nets have zero component pins listed in the nets section (pins: []) despite having point_count of 4, meaning global labels connect them to U1 ADC pins and J3 connector pins. The analyzer lost the pin connections for these global label nets.
  (nets.ADC1)

### Suggestions
- Investigate the U2 pin-to-net mapping error: the LT1129CST-3.3 library symbol pin numbering may not match the physical pin locations after coordinate-based wire tracing, causing VIN and OUT to appear on GND
- Crystal load cap detection should look for caps on both terminals of the crystal, not just one side
- The RF matching section should detect balun components (BAL1) and their associated matching network (C16, C17, L2) as an RF front-end for BLE designs
- Global label nets (ADC1, ADC2) show point_count=4 but empty pin arrays, suggesting a label-to-pin resolution gap for nets that only connect via global labels across sheets

---
