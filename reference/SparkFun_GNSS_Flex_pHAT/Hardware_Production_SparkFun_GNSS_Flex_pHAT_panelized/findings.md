# Findings: SparkFun_GNSS_Flex_pHAT / Hardware_Production_SparkFun_GNSS_Flex_pHAT_panelized

## FND-00001424: Component count, multiple LDOs, and USB compliance detection are accurate; USB ESD protection on D+/D- falsely reported as missing when DT1042-04SO is present; Multiple UART channels not enumerated...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_GNSS_Flex_pHAT.kicad_sch
- **Created**: 2026-03-24

### Correct
- 116 total components matches the sum of component_types (15 caps + 31 TPs + 8 mounting + 9 connectors + 14 resistors + 23 jumpers + 2 diodes + 3 ICs + 4 LEDs + 4 fiducials + 1 inductor + 2 other = 116). Two LDO regulators detected: RT9080-3.3 for VBACKUP and AP7361C-3.3V for 3.3V. USB-C compliance analysis correctly identifies CC1/CC2 5.1kΩ pull-downs as passing, and VBUS decoupling as failing. The dnp_parts=1 is correctly reflected.
- 31 test points are correctly enumerated with their net assignments. The design_observations note that RT9080-3.3 (U3) output rail VBACKUP is missing output capacitors — this is accurate since VBACKUP is the battery backup supply and the schematic only connects it to the GNSS module backup pin. The SD card ESD protection (D2, DF5A5.6LFU) protecting SD_CLK, SD_CMD, SD_DAT0, SD_DAT3 is correctly identified.

### Incorrect
- design_observations contains two usb_data entries claiming has_esd_protection=False for D+ and D-. However, D1 (DT1042-04SO 4-line USB ESD IC) is correctly listed in protection_devices with protected_nets ['__unnamed_26', '__unnamed_27', '__unnamed_5', '__unnamed_6']. The USB data lines connect to the transformer TR1 first, then to those unnamed nets. The USB ESD protection IS present but the analyzer fails to correlate the unnamed nets protected by D1 with the named D+ and D- nets that pass through TR1. This is a false negative for ESD protection on USB lines.
  (signal_analysis)

### Missed
- The design has signal nets RXD1, RXD2, RXD3, RXD4, TXD1, TXD2, TXD3, TXD4 (4 UART pairs) connecting to a multi-GNSS receiver HAT. The bus_topology correctly detects RXD/TXD as bus signal groups, but uart_channels in signal_analysis is None (not a list). The test_coverage section identifies 8 uncovered UART nets. No structured UART bus enumeration is produced, which would be useful for this multi-receiver design.
  (statistics)

### Suggestions
(none)

---

## FND-00001425: pHAT board dimensions, layer count, and via count are plausible; Thermal pad analysis correctly identifies U2 heatsink pad on GND net

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_GNSS_Flex_pHAT.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board dimensions 65.0×56.75 mm match the Raspberry Pi pHAT specification (65×56.5 mm) within 0.25 mm tolerance. 4 copper layers are appropriate for a high-density GNSS carrier board with multiple receivers. 266 vias is reasonable for a 65×57 mm 4-layer board with complex routing. DFM violation_count=0 indicates clean design by SparkFun's standards.
- The thermal_pad_vias analysis detects U2's exposed pad (2.35×1.6 mm, 3.76 mm², GND net). This is consistent with the AP7361C-3.3V LDO regulator which has an exposed thermal pad on its package. The identification of this heatsink pad is accurate and important for manufacturing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001426: Drill file reported missing despite being present inside zip archive; Layer alignment, component ref counts, and B.Paste emptiness correctly analyzed

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- alignment.aligned=True with coherent layer extents (~133×118 mm matching a panel of 65×57 mm boards). B.Paste flash_count=0 and aperture_count=0 is correct — the back side of this pHAT has no paste (all back-side paste would be zero for SMT-only back assembly if backside components use reflow wave, or there may be no back-side SMD pads). smd_ratio=1.0 is consistent with no PTH drill file found. 145 unique component refs with ~28 kibuzzard items and the remainder being real refs is consistent with Flex_pHAT's 116-component design.

### Incorrect
- statistics.drill_files=0, has_pth_drill=False, has_npth_drill=False, and drills=[] in the loose-file analysis. However, the zip archive analysis shows drill_files=1 and the zip contains a drill file. Inspection of the Production directory confirms there is no loose .drl file (only .GKO, .GBL, .GTL, etc.). The analyzer correctly reads loose files and separately reads the zip, but the top-level completeness.complete=False and the drill statistics only reflect loose files. This means the board appears to have no drill information from the loose-file perspective, which may mislead consumers. The same issue affects LG580P.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
