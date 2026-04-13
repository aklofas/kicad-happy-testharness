# Findings: Jana-Marie/CH330_Hardware / CH330

## FND-00000421: Net 'D+' incorrectly contains U1 pin 4 (RTS) instead of U1 pin 1 (UD+); Net 'D-' incorrectly contains U1 pin 3 (GND) instead of U1 pin 2 (UD-); Decoupling analysis misses C2 on V3 rail; Differentia...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: CH330.sch.json
- **Created**: 2026-03-23

### Correct
- The schematic has a label 'D+' connected to U1 pin 1 (UD+, bidirectional USB data+). The JSON places U1 pin 4 (RTS, output) into the 'D+' net instead. The analyzer has mis-mapped U1's pin positions, assigning the wrong schematic pins to the D+ net.
- The schematic has a label 'D-' connected to U1 pin 2 (UD-, bidirectional USB data-). The JSON places U1 pin 3 (GND, power_in) into the 'D-' net instead. This is a pin-mapping error caused by incorrect position-to-pin resolution for mirrored components in KiCad 5 legacy format.
- The erc_warnings section flags net 'V3' as having no output driver. However, U1 pin 8 (V3) has pin_type 'power_out' — it IS the driver for the V3 net. The V3 net in the JSON only contains U1 pin 5 (VCC, power_in) and C2 pin 2, omitting U1 pin 8 (power_out) which is the actual driver. This is a consequence of the broader pin-mapping error affecting U1.

### Incorrect
- The differential_pairs entry for D+/D- reports has_esd: true and lists U1 as the esd_protection device. U1 is the CH330 USB-UART bridge IC, not an ESD suppressor. There is no TVS, ESD diode array, or protection component in this design. This contradicts the usb_data design_observation on the same net which correctly reports has_esd_protection: false.
  (design_analysis)
- V3 is the output of U1's internal 3.3V linear regulator (pin 8, type power_out). It powers U1's VCC (pin 5) and is bypassed by C2. It should be classified as a power domain rail. The net_classification assigns it 'signal', and the power_domains section omits it as a standalone rail even though U1 pin 8 (V3, power_out) drives it.
  (design_analysis)

### Missed
- C2 (100n) is connected between the V3 rail (U1 pin 8, internal 3.3V regulator output) and GND, serving as a decoupling capacitor for the V3 power domain. The decoupling_analysis only reports C1 on VBUS; C2 on V3 is entirely absent from the decoupling_analysis section.
  (signal_analysis)

### Suggestions
- Fix: Net 'V3' classified as 'signal' but is a power rail (U1 internal 3.3V regulator output)

---
