# Findings: YC-Lam/IP5328P-powerbank_design / usbpd_powerbank

## FND-00000662: kicad_version reported as 'unknown' for a valid KiCad 5.99/pre-6 schematic; IP5328 power bank IC correctly identified as switching regulator with inductor L1; USB-C CC resistor fail is correct: R2/...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: usbpd_powerbank.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- signal_analysis.power_regulators detects U1 (IP5328) with topology=ic_with_internal_regulator, inductor=L1, input_rail=VIN, output_rail=VOUT1. Correct.
- usb_compliance check correctly fails cc1_pulldown_5k1 and cc2_pulldown_5k1 for P1 (USB_C_Plug_USB2.0). The design uses 10k resistors on CC1/CC2 instead of the USB-C spec-required 5.1k for a 5V power source.

### Incorrect
- The file has version=20210406 and generator=eeschema but no generator_version field (KiCad 5.99 nightly format). The analyzer reports kicad_version='unknown' instead of inferring 'pre-6' or '5.99' from the version number. Same issue seen in IndiaNavi (file_version=20210406).
  (signal_analysis)

### Missed
- The IP5328 is a USB power bank management IC (battery charging + boost output), but signal_analysis.bms_systems=[] and bms detection is absent. No current-sense detection either (R4=0.01R is the current sense resistor). This is a known limitation for non-library-known ICs.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000663: PCB stats correct: 49 footprints (includes 2 mounting holes as REF**), 2-layer, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: usbpd_powerbank.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- statistics.footprint_count=49 matches the source. The REF** group (2 mounting holes with exclude_from_bom=true) is correctly separated. Thermal pad detection for U1 (QFN-40 with 4.4×4.4mm exposed pad, 2 thermal vias) is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000664: Gerber set complete: 9 files + 1 drill, all layers present, board dimensions correct

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-23

### Correct
- completeness.complete=true, all 9 expected layers found, gbrjob-sourced dimensions 65.31×25.21mm match PCB output. Drill classification via x2_attributes correctly identifies 77 vias and 18 component holes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
