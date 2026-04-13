# Findings: martinberlin/Sharp-LV / S3-silicon-Sharp-Touch

## FND-00001438: Component count and BOM correctly parsed: 53 total, 3 DNP, 5 ICs; I2C bus devices list incomplete: Y3 (RV-3032-C7 RTC) omitted from SDA/SCL observations; USB ESD protection asymmetric: USB_D- repor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Sharp-LV.kicad_sch
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 53 total components with 3 DNP (C13, C17, C18), 21 capacitors, 8 resistors, 8 connectors, 4 inductors, 3 crystals, and 5 ICs (NRF52840, USBLC6-2P6, MCP1700, RT9080, TPS2113). Component type categorization is accurate throughout.

### Incorrect
- The design_observations I2C entries for SDA and SCL both list only 'U1' (NRF52840) as the device. However Y3 (RV-3032-C7) is clearly an I2C RTC connected to both /SDA (pin 2) and /SCL (pin 8). The RTC is a primary I2C device on this bus and should appear in the devices list alongside U1.
  (signal_analysis)
- The design_observations usb_data entries report USB_D- as has_esd_protection=false but USB_D+ as true. Both lines are protected by U2 (USBLC6-2P6), which is a bidirectional TVS that protects both D+ and D- simultaneously. The USBLC6-2P6 explicitly has pads for both I/O1 (D-) and I/O2 (D+). Both should be marked as protected.
  (signal_analysis)

### Missed
- The TPS2113APW (U5) is a power-path multiplexer/selector that switches between VBUS (USB) and BAT+ (battery) to supply VIN. The power_regulators section only lists U3 (MCP1700 LDO) and the TPS2113 is absent. It is not flagged as a power mux, power selector, or switching regulator of any kind. This is a significant topology that should be identified.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001439: 4-layer board correctly identified with full stackup and 53 footprints all on F.Cu; Via-in-pad detection correctly flags J7/MP2 as a potential concern (different net); tht_count is 1 but J2 is the ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Sharp-LV.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The analyzer correctly reports a 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu), 53 footprints with 49 SMD and 1 THT (J2 the programming header), board dimensions of 69.735 x 44.655mm, 649 track segments, 106 vias, and fully routed (0 unrouted). The stackup details (1.6mm total, 0.035mm copper) are also captured.
- The via_in_pad analysis correctly identifies 3 vias near pads: J7/MP2 (different net, flagged), TP3/1 (same net, benign), and U1/T23 (same net, benign fanout via). The J7/MP2 detection is genuinely noteworthy as it is a different-net via near a mounting pad on the JST battery connector.

### Incorrect
- The statistics report tht_count=1 (correctly J2, the pin header) and back_side=0 (all 53 footprints on front). However TP2 in the footprints list is type 'exclude_from_pos_files' and its pcb entry shows layer F.Cu with no exclude_from_bom flag, while TP1 and TP3 both correctly have exclude_from_bom=true. The TP2 footprint is missing the exclude_from_bom field that TP1/TP3 have, representing an inconsistency in test-point attribute extraction.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001440: 4-layer gerber set complete with correct layer count, drill files, and board dimensions; Alignment flagged as false due to variation between mask/silk and copper extents — this is normal behavior, ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: fabrication_1.0
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly identifies 13 gerber files + 2 drill files, a 4-layer board (F.Cu=L1, In1.Cu=L2, In2.Cu=L3, B.Cu=L4), board dimensions of 79.85 x 44.65mm (edge cuts extents), no missing required layers, 163 total holes with 136 vias (22 at 0.2mm, 114 at 0.4mm) and 27 component holes. The completeness check correctly passes.
- The drill_classification correctly identifies 136 via holes (all PTH), 27 component holes (4x0.6mm + 17x1.0mm PTH, 2x0.65mm + 4x2.2mm NPTH), and 0 mounting holes. The NPTH 2.2mm holes are likely the 4 board mounting holes. SMD ratio of 0.9 (233 SMD apertures vs 27 THT holes) correctly reflects an SMD-dominated design.

### Incorrect
- The analyzer reports aligned=false with issues citing 5.7mm width variation and 4.0mm height variation across layers. The differences observed are entirely expected: B.Paste is 0x0 (no back-side paste, all SMD is on front), mask layers are smaller than copper (no pads at board edge), and silkscreen is within bounds. No actual Gerber misalignment exists. The analyzer's threshold for flagging this is too aggressive for normal boards where component-free edges cause extents differences.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
