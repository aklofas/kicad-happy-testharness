# Findings: USB_Dongle_KiCad / USB_Dongle_KiCad

## FND-00001759: Total component count correct at 56; Crystal Y2 (24 MHz) detected with correct load caps; LDO and MCU internal regulator both detected as power regulators; USB-C connector J1 compliance checks perf...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB_Dongle_KiCad.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The schematic has 56 non-power components across capacitors (27), resistors (12), ICs (6), crystals (2), LEDs (2), ferrite beads (2), switches (2), and connectors (3). This matches the KiCad source file.
- Y2 (24 MHz Crystal_GND24_Small) is correctly detected with load caps C12 and C14 (both 10 pF), giving an effective load of 8 pF. Y1 (26 MHz) correctly has no load-cap entry because it connects directly to the USB3343 REFCLK pin without discrete load caps.
- U1 (AMS1117-3.3) is correctly identified as an LDO with output rail +3.3V and estimated Vout 3.3 V. U5 (STM32F730R8Tx) is correctly identified as an IC with an internal regulator.
- USB compliance analysis runs on J1 (USB_C_Receptacle_USB2.0): CC1/CC2 5.1k pull-downs pass, VBUS decoupling passes, usb_esd_ic passes. One failure flagged for VBUS ESD protection (no dedicated TVS on VBUS net), and two info items for D+/D- series resistors.
- R8/C20 (10 k/100 n, 159 Hz, BOOT0), R12/C27 (2.2 k/47 n, 1.54 kHz, NRST), and R9/C27 (4.7 k/47 n, 720 Hz, NRST) are correctly identified as low-pass RC filters.

### Incorrect
(none)

### Missed
- U3 (USBULC6-2M6, a 6-line USB ESD protection array) and U4 (ESDA14V2-2BF3, a dual ESD protection diode) are present in the schematic but the signal_analysis.protection_devices array is empty. The USB compliance checker separately recognises them via usb_esd_ic:pass, but the general protection_devices detector does not flag them. These are real protection devices that should appear in protection_devices.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001760: 6-layer board correctly identified with 58 footprints and routing complete; DFM tier correctly classified as advanced with two violations

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB_Dongle_KiCad.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB is a 6-layer design (F.Cu, In1.Cu, In2.Cu, In3.Cu, In4.Cu, B.Cu) with 58 footprints (56 schematic components plus 2 G*** fiducials), 121 vias, 1173 track segments, and zero unrouted nets.
- 0.1 mm track width and 0.15 mm via drill both exceed standard process limits (0.127 mm / 0.2 mm respectively) and correctly trigger advanced-tier DFM violations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001761: VCAI2C01 gerber set is complete and aligned; VCAI2C01 drill classification correctly identifies 162 vias and 54 component holes; VCAI2C02 gerber set is complete and aligned with correct drill class...

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json.json
- **Created**: 2026-03-24

### Correct
- All 9 expected layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) plus PTH and NPTH drill files. Layer extents are consistent and all layers are aligned. 216 total holes: 162 vias (0.4 mm) and 54 component holes (50 x 0.889 mm + 4 x 3.0 mm).
- The x2-attribute-based drill classification correctly separates 162 via holes (0.4 mm, ViaDrill) from 50 component holes (0.889 mm, ComponentDrill) and 4 large mounting holes (3.0 mm, ComponentDrill).
- All 9 expected layers present plus PTH and NPTH drill files. Alignment is confirmed. 84 total holes: 54 vias (0.4 mm), 29 component holes across 6 sizes (0.8, 0.889, 1.2, 1.4, 1.9, 3.0 mm), and 1 NPTH mounting hole (2.7 mm).
- Board dimensions from the .gbrjob file are 70.812 x 30.172 mm, consistent with the PCB analyzer output of 70.612 x 29.972 mm (small rounding difference between outline and keepout margin).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
