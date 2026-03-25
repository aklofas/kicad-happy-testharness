# Findings: SparkFun_RTK_Facet_mosaic / Hardware_Connector_SparkFun RTK Facet - External Connector

## FND-00001532: Component counts, BOM, and power rail detection are accurate; Three LDO regulators correctly detected with correct topologies and rails; Crystal Y1 (24MHz) detected with correct load capacitor calc...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_RTK_Facet_mosaic.kicad_sch
- **Created**: 2026-03-24

### Correct
- The main schematic correctly reports 134 total components (41 resistors, 28 capacitors, 13 ICs, 6 diodes, 5 transistors, 25 test points, 2 inductors, 1 crystal, 4 fiducials, 5 connectors, 1 jumper, 3 other) and 9 power rails (1.8V, 3.3V, 3.3V_P, GND, VBATT, VBUS_DET, VIN, VRAW, VUSB). The BOM correctly deduplicates multi-unit components and cross-sheet references, showing C3=1.0uF and R3=2.2k from the main sheet.
- U12 (STLQ015-3.3, VBATT→M_BACKUP), U7 (AP7361C-3.3V, VRAW→3.3V_P), and U11 (AP2112K-3.3, VRAW→3.3V) are all correctly identified as LDO regulators with accurate input/output rail assignments and 3.3V output voltage inferred from the part suffix.
- Y1 (24MHz) is correctly detected with two 18pF load capacitors (C14, C15). The effective load capacitance of 12pF is correctly calculated using the series formula (18pF/2 = 9pF per cap in series, effective = 9pF + 3pF stray ≈ 12pF), and the in_typical_range flag is correctly true.
- Three voltage dividers are correctly identified: R19/R20 (100k/100k, VUSB→VBUS_DET) for USB hub VBUS detection, R7/R8 (1k/4.7k, 3.3V→ESP35/DeviceSense) for device sense, and R35/R39 (1k/10k, drain→GND) in the FastOff control circuit. All ratios and mid-point connections are correct.
- D1 (PESD0402) is correctly identified as protecting the MOSAIC_RF_IN net (GNSS RF antenna input) and D2 (DF5A5.6LFU, 4-line ESD array) protecting SD_CLK, SD_CMD, and SD_DATA. Both protection devices have correct clamp nets and protected net lists.
- Q3 (BSS138) is correctly classified as a level_shifter topology: the gate is driven by the 1.8V rail (mosaic-X5 logic), the drain connects to MPPS_3V3 (3.3V-side), and the source connects to MPPS (1.8V-side). Gate resistor R12 (2.2k) is correctly associated.
- The design observation correctly identifies that the ESP21/SDA and ESP22/SCL I2C buses (shared between ESP32 U1, mux U13, and fuel gauge U4) have no dedicated pullup resistors in the schematic. The Qwiic connectors J3 are expected to source pullups externally. The R3 (2.2k) on SDA is a UART/control circuit resistor, not an I2C pullup.

### Incorrect
- The main schematic analysis includes C3 from both sheet 0 (main, 1.0uF on the ESP~{RST} net) and sheet 2 (GNSS subsheet, 0.1uF). The RC filter detector picks up the GNSS subsheet's C3 (0.1uF) for two filter instances involving R1 and R11 on the ESP~{RST} net, when the actual C3 on that net is 1.0uF from the main sheet. This causes incorrect cutoff frequency reporting (159.15 Hz should be 15.92 Hz for 1.0uF). The BOM correctly uses the sheet-0 value (1.0uF), but signal analysis does not.
  (signal_analysis)

### Missed
- The design uses U10 (MCP73833) as a LiPo battery charger (VUSB→VBATT) and U4 (MAX17048) as a fuel gauge (monitoring VBATT). Together with the LiPo battery connector J2 and the STLQ015 backup regulator, this constitutes a battery management system. The bms_systems detector returns an empty list. MCP73833 is also not detected as a power regulator (it is a charger, not a linear regulator, so this may be by design), but the combined charger+gauge system should be flagged.
  (signal_analysis)
- The schematic has explicit SD_CMD, SD_CLK, and SD_DATA nets connected between the mosaic-X5 GNSS receiver (U2), SD card connector (J4), and ESD protection (D2). The memory_interfaces detector returns an empty list. An SPI/SD card interface should be detected from these named nets and the associated pull-up resistors R37 and R38.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001533: USB crystal Y1 (24MHz) and CH340C USB-UART correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_USB.kicad_sch
- **Created**: 2026-03-24

### Correct
- Y1 (24MHz) for the USB251xB USB hub crystal oscillator is correctly detected with 18pF load caps (C14, C15). The USB schematic correctly identifies U3 (CH340C) and U9 (USB251xB) as ICs, and the voltage divider R19/R20 for VBUS detection is correctly found.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001534: PESD0402 ESD protection on GNSS RF input correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_GNSS.kicad_sch
- **Created**: 2026-03-24

### Correct
- D1 (PESD0402) on the MOSAIC_RF_IN net is correctly classified as an ESD protection diode with GND as the clamp net. The mosaic-X5 GNSS receiver (U2) and the RF antenna connector (J1) appear in context.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001535: Fuses F1 and F3 correctly detected as protection devices; USB_DP incorrectly reported as having no ESD protection when D1 connects to it; Component count and types correct for external connector board

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun RTK Facet - External Connector.kicad_sch
- **Created**: 2026-03-24

### Correct
- F1 (6V/0.5A/1A on VBATT line) and F3 (6V/2.0A/4.0A on VUSB line) are correctly detected as fuse-type protection devices. The DT1042-04SO 4-line ESD protector D1 is correctly identified as an esd_ic protecting USB_DM, USB_DP, and the additional VBUS/battery lines.
- 16 total components with accurate type breakdown: 2 resistors (R16, R17 = 5.1k), 7 connectors, 2 fuses, 1 diode (DT1042-04SO ESD), 1 jumper (JP0), 3 other (logos/OSHW). The missing_footprint list correctly identifies G1 and G2 (logo symbols with no footprint).

### Incorrect
- The usb_data design observation for USB_DP reports has_esd_protection=false, but this is wrong. The DT1042-04SO (D1) pin 6 is connected directly to USB_DP as confirmed by net analysis. The protection_devices entry correctly lists USB_DP in D1's protected_nets. There is an inconsistency between the protection_devices detection (correct) and the usb_data observation (incorrect).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001536: OLED reset RC filter and reset pin detection correct; I2C bus SDA lists U1 twice due to dual-pin connection on OLED

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_Display_SparkFun RTK Facet - Display SD.kicad_sch
- **Created**: 2026-03-24

### Correct
- R2 (10k) + C7 (1.0uF) forming a 15.92 Hz low-pass filter on the OLED RESET line is correctly detected. The reset_pin design observation for U1 (OLED) correctly identifies the pullup and filter capacitor. The RC filter cutoff of 15.92 Hz is accurate for 10k/1.0uF.

### Incorrect
- The i2c_bus design observation for the SDA net lists U1 twice in the devices array because the OLED (SSD1306 compatible) has two pins (pin 17 = D1/MOSI and pin 18 = D2) connected to the SDA net in I2C mode. While technically accurate at the pin level, reporting a single component twice in the device list is misleading for I2C bus analysis.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: I2C bus SDA lists U1 twice due to dual-pin connection on OLED

---

## FND-00001537: Footprint count, layer detection, track and via statistics are accurate; Board outline not detected: gr_poly on Edge.Cuts is not parsed; DFM tier correctly classified as standard with no violations...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_RTK_Facet_mosaic.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 173 footprints confirmed (28 front, 145 back; 118 SMD, 14 THT, 39 board-only, 2 special). Four copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu) correctly identified. 1586 track segments, 321 vias, 8 zones, and total track length of 2958.15mm are all plausible for this board complexity. Routing complete with 0 unrouted nets.
- The board uses minimum 0.1778mm (7mil) track width, 0.1524mm (6mil) spacing, 0.3mm drill, and 0.13mm annular ring — all within standard fab tier parameters. Zero DFM violations is correct.
- 10 courtyard overlaps are correctly detected, all involving components on B.Cu overlapping with J3 (JST 1mm Qwiic connector). The overlap magnitude of 1.748mm² per pair is plausible for tightly packed 0402 components near a small connector. This is a real layout concern.
- 34 0402 capacitors on B.Cu are correctly flagged as medium tombstoning risk because one pad is connected to the GND copper zone and the other is not. This thermal imbalance during reflow is a legitimate concern, especially for back-side components.

### Incorrect
(none)

### Missed
- The main PCB board outline is defined as a single gr_poly element on the Edge.Cuts layer with 10 vertices (the board has a notch cutout shape). The analyzer reports edge_count=0 and bounding_box=null because it only processes gr_line and gr_arc elements on Edge.Cuts, not gr_poly. Both board_width_mm and board_height_mm are reported as None. The connector PCB has the same issue.
  (board_outline)

### Suggestions
(none)

---

## FND-00001538: Board outline not detected for connector PCB: gr_poly on Edge.Cuts not parsed

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun RTK Facet - External Connector.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The connector PCB also uses a gr_poly for its board outline on Edge.Cuts. As with the main PCB, the analyzer reports edge_count=0, bounding_box=null, and board dimensions as None. The actual board shape can be inferred from copper extents but is not computed.
  (board_outline)

### Suggestions
(none)

---

## FND-00001539: Display PCB board outline, dimensions, and routing correctly captured

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_Display_SparkFun RTK Facet - Display SD.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The display PCB uses a gr_rect board outline (49.5 x 22.0mm), which is correctly parsed. 38 footprints (24 SMD, 1 THT, board-only components), 223 track segments, 47 vias, 5 zones, and full routing completion are all correctly reported for this small display sub-board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001540: Panelized PCB footprint count, drill holes, and layer count are correct; DFM violation correctly flagged for panel exceeding 100x100mm size threshold

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_Production_SparkFun_RTK_Facet_mosaic_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panelized PCB has 1383 footprints (1220 front+back SMD/THT from 8 boards, plus panel-only fiducials/tooling), 2568 vias + 112 THT = 2680 total drill holes, and 64 zones across 4 copper layers. The DFM correctly flags the 133.2x187.2mm panel as exceeding the 100x100mm standard tier threshold.
- The panelized board (133.2x187.2mm) correctly triggers a DFM violation noting it exceeds the 100x100mm standard pricing tier at JLCPCB. The board size violation is the only DFM issue, which is appropriate for a well-designed panelized board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001541: GKO (board outline) file misidentified as B.Mask, causing false Edge.Cuts missing report; Inner copper layer Gerbers GL2 and GL3 not detected — 4-layer board has only 2 copper layers parsed; Drill ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
- The single combined drill file has 2680 holes: T1 (0.3mm via drill, 2568 holes) and T2 (1.016mm component drill, 112 holes). This exactly matches the panelized PCB analysis (2568 vias + 112 THT holes). The drill classification correctly identifies vias and component holes via X2 aper function attributes.
- The layer_count=4 is correctly inferred from GBL (Copper,L4,Bot) and GTL (Copper,L1,Top), confirming a 4-layer stackup. The board is correctly identified as generated by KiCad 8.0.5. Layer alignment is reported as aligned with no issues, which is correct for a panelized design from a single KiCad project.

### Incorrect
- The GKO file (SparkFun_RTK_Facet_mosaic_panelized.GKO) contains board outline data (1904 draw commands using Profile apertures, TA.AperFunction=Profile) but has an incorrect TF.FileFunction=Soldermask,Bot in its Gerber header. The analyzer trusts TF.FileFunction and classifies GKO as B.Mask. This causes: (1) Edge.Cuts shown as missing in completeness, (2) board_dimensions empty, (3) two B.Mask entries in found_layers. The GKO extension and Profile aperture function should override the file function metadata.
  (completeness)
- Because the GKO file is misidentified as B.Mask (not Edge.Cuts), the board_dimensions field is an empty dict {}. The actual board dimensions from the PCB panelized analysis are 133.2 x 187.2mm. The completeness.complete flag is false as a result of the missing Edge.Cuts detection.
  (completeness)

### Missed
- The Production directory contains 11 Gerber files including GL2 (FileFunction=Copper,L2,Inr) and GL3 (FileFunction=Copper,L3,Inr) for the two inner copper layers of the 4-layer board. The analyzer's uppercase extension list includes *.G2 and *.G3 (Protel style) but not *.GL2 or *.GL3 (KiCad inner layer style). Only 9 Gerber files are parsed; GL2 and GL3 are silently skipped. The found_layers list shows only F.Cu and B.Cu copper layers, not In1.Cu or In2.Cu.
  (statistics)

### Suggestions
(none)

---
