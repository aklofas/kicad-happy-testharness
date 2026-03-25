# Findings: ACEStat_Kicad_Deprecated / aducm_board

## FND-00000332: ADM7154 LDO regulator not detected in power_regulators

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ADM715x.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U3 (ADM7154, an Analog Devices ultra-low noise LDO regulator from the ADM715x family) is present with VIN/VOUT/EN pins and 5 decoupling capacitors, but signal_analysis.power_regulators is empty []. The subcircuits section captures U3 as a neighbor-IC cluster but does not classify it as a linear regulator. The lib_id 'SIB_Footprint:ADM7514' and value 'ADM7154' both contain 'ADM7' which should be matchable. Correct output would include a power_regulator entry with regulator_type='linear', input_rail='+VIN', output_rail='+VOUT'.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000333: ADM7514 LDO regulator not detected in power_regulators

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ADM751x.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U3 (ADM7514, Analog Devices ultra-low noise LDO from the ADM751x family) is present with VIN/VOUT/EN/BYP/REF/REF_SENSE pins and 5 decoupling capacitors. signal_analysis.power_regulators is empty []. The ADM7514 is clearly a linear regulator (pins named VOUT, VIN, EN confirm this). A power_regulator entry with regulator_type='linear', input_rail='+VIN', output_rail='+VOUT' should be generated.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000334: Net connectivity errors: named nets assigned to wrong FT232RQ pins; UART interface not detected for FT232RQ USB-to-UART bridge

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FTDI.sch.json
- **Created**: 2026-03-23

### Correct
- The net assignments for U2 (FT232RQ) are systematically incorrect. In the source, USBD+ label connects to pin 14 (USBDP) and USBD- connects to pin 15 (USBDM). In the JSON, net 'USBD+' contains pin 18 (RESET#) and 'USBD-' contains pin 23 (NC) — both wrong. Similarly, '5VUSB' is assigned to pin 27 (OSCI) and '3V3VOUT' contains pin 14 (USBDP) and pin 28 (OSCO). The custom SIB_Footprint:FT232RQ symbol has pins at non-standard coordinates, causing the wire-endpoint to pin-position matching to map named nets to the wrong pins. This produces incorrect differential_pairs reporting (esd_protection wrongly attributed), wrong erc_warnings, and the USBD+/USBD- differential pair is built from incorrect pin associations.

### Incorrect
(none)

### Missed
- U2 is an FT232RQ, a USB full-speed to UART/serial bridge. The design has hierarchical labels SIN and SOUT (mapped to CBUS4 and CBUS3 in the net table, though this itself may be an artifact of the pin-mapping error). The bus_analysis.uart array is empty. Given the device name FT232RQ and the presence of TXD/RXD/RTS/CTS/DTR/DSR pins (visible in the component pins list), a UART interface should be detected.
  (design_analysis)

### Suggestions
(none)

---

## FND-00000335: PS1 (VXO7803-500-M) net connectivity inverted: GND and +VIN pins swapped; VXO7803-500-M DC-DC converter not detected as power_regulator and misclassified as connector

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VXO7803-500-M.sch.json
- **Created**: 2026-03-23

### Correct
- In the source schematic, PS1 pin 1 is named '+VIN' (type=input) and pin 2 is named 'GND' (type=power_in). However the JSON nets show: net 'GND' contains PS1 pin_number='1' (pin_name='+VIN') and net '+VIN' contains PS1 pin_number='2' (pin_name='GND'). The pin-to-net assignment is inverted — the +VIN pin is placed on the GND net and the GND pin is placed on the +VIN net. This is a pin-coordinate resolution error for the custom SIB_Footprint:VXO7803-500-M symbol. Additionally, PS1's +VO output pin (pin 3) is on '__unnamed_0' which is not connected to +VOUT (the +VOUT net only has L1 pin 1), confirming the output path of the converter is also not correctly traced.

### Incorrect
(none)

### Missed
- PS1 (CUI VXO7803-500-M) is a 3.3V/500mA isolated DC-DC converter module. It is classified as type='connector' because it uses a custom lib_id 'SIB_Footprint:VXO7803-500-M' with no keyword matching. signal_analysis.power_regulators is empty. The component has +VIN input, GND, +VO output, and ON/OFF control pins — a clear switching power supply topology. The output LC filter (L1 10-47uH with C36/C37 22uF output caps) is also not detected under lc_filters. The component should be classified as ic/power_converter rather than connector, and power_regulators should include an entry for PS1.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000336: Ferrite bead pins not resolved: FB3, FB4, FB5 have empty pins arrays

- **Status**: new
- **Analyzer**: schematic
- **Source**: ECSensor.sch.json
- **Created**: 2026-03-23

### Correct
- All three ferrite beads (FB3, FB4, FB5 from Device:Ferrite_Bead) have 'pins': [] in the component entries, and the WE and RE nets have empty pins lists (0 component connections despite having point_count of 5 and 3 respectively). In the source schematic, each ferrite bead is placed at 90-degree rotation and connects the electrode signals (CE, WE, RE) to the EC sensor connector pins. The pin-position resolution for rotated KiCad 5 legacy ferrite_bead symbols fails, leaving the nets WE and RE without any driving component connections. The CE net also only shows C33 pin 2, with no FB3 connection even though FB3 is wired between CE and J3 pin 1.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
