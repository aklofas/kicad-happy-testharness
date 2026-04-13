# Findings: FPGAwars/icezum / src-kicad_icezum

## FND-00002219: LED components with 'LD' prefix misclassified as inductors; ESDUSB TVS diode misclassified as fuse; Multi-sheet hierarchy correctly parsed: 7 sheets with 211 components and complex power topology

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_icezum_src-kicad_icezum.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly follows the 7-sheet hierarchy (icezum.sch + 6 sub-sheets), consolidating 211 components, 464 nets, and 78 no-connects. Power regulators (TPS62133 switching regulator, AP7361 LDO, TLV711 LDO) are all detected, along with SPI, I2C, UART buses, USB differential pair, and crystal oscillator (DSC1001). The multi-domain power analysis correctly identifies 1.2V, 1.8V, 3.3V, and 5V domains.

### Incorrect
- 11 LEDs with references LD0–LD9 and LD10 (footprint Icezum:LED_0603, values 'Green' and 'Yellow') are classified as type 'inductor' instead of 'led'. The reference prefix 'LD' is an abbreviation for 'LED diode' in Spanish (this is a Spanish open-hardware FPGA board). The footprint name explicitly contains 'LED_0603' but the classifier is keying on the 'L' prefix, treating them as inductors. The statistics show only 1 LED (D12) but 15 inductors, whereas there should be 12 LEDs and at most 4 non-bead inductors (L1, L2, L3, L5).
  (statistics)
- F2 (value 'ESDUSB', footprint SOT-563) is classified as type 'fuse' because its reference starts with 'F'. The ESDUSB part is a TVS diode array for USB ESD protection, not a fuse. This propagates to the USB differential pair analysis: the differential_pairs entry shows 'has_esd: false' because the ESD device is never recognized as such — it's treated as a protection device of type 'fuse' rather than an ESD clamp, so the has_esd flag on the USB pair is incorrectly false.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002220: USB differential pair detected per-sheet but 'has_esd' is false despite ESDUSB device on USB lines

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_icezum_src-kicad_usb-communications.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The USB differential pair (USB_P / USB_N) is correctly detected in both the sub-sheet and top-level analysis, but 'has_esd' is false in both cases. F2 (ESDUSB) is physically connected to USB_N and GND, and is a TVS diode array specifically designed for USB ESD protection. Because F2 is classified as 'fuse' instead of an ESD device, the has_esd check fails. The USB pair should show has_esd: true.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002221: 4-layer 218-footprint PCB fully parsed with thermal zone stitching detected

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_icezum_src-kicad_icezum.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies 4 copper layers (F.Cu, B.Cu, In1.Cu, In2.Cu), 218 footprints (192 SMD, 23 THT), 228 vias, 27 zones, and complete routing (0 unrouted nets). Thermal zone stitching is detected for GNDREF with 80 stitching vias across all 4 layers, and for +5V_P and +3V3 fill zones. Board dimensions (68.58×53.34 mm) match the gerber output.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
