# Findings: Bastardkb/holder_daughterboard / pcb_daughterboard

## FND-00002126: VBUS power rail not recognized as a power net; listed only as unnamed nets __unnamed_3 and __unnamed_11; USB-C CC pulldown check correctly detects 5.1k CC1 and CC2 pulldowns on both J1 and J4

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_holder_daughterboard_pcb_daughterboard.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- R1/R2/R3/R4 (all 5.1k) serve as CC pulldowns for the two USB-C receptacles. The usb_compliance section correctly reports cc1_pulldown_5k1: pass and cc2_pulldown_5k1: pass for both J1 and J4. The vbus_esd_protection: fail and vbus_decoupling: fail results are accurate — there is no ESD diode or decoupling capacitor on VBUS in this pass-through daughterboard.

### Incorrect
- Both USB-C connectors J1 and J4 have their VBUS pins (A4, A9, B4, B9) connected together into nets __unnamed_3 and __unnamed_11 respectively, because there is no explicit PWR_FLAG or named power label for VBUS in the schematic. The statistics.power_rails list shows only ['GND'], omitting VBUS entirely. The design_analysis.power_domains.ic_power_rails dict is empty, and the power_net_summary only tracks GND. The ferrite beads FB1/FB2 filter VBUS (Net-(FB1-Pad2) and Net-(FB2-Pad2) appear in the PCB nets) but the schematic analyzer cannot infer this relationship because VBUS has no named net.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002127: PCB reports footprint_count=51 including 38 kibuzzard board-only graphics and 4 excluded connectors; misrepresents actual BOM component count of 8

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: holder_daughterboard_pcb_daughterboard.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB contains 39 board_only footprints (38 kibuzzard-* graphics used for PCB artwork/silkscreen decoration + 1 LOGO) and 4 connector footprints J2/J3/J5/J6 marked exclude_from_bom=true. The real BOM-relevant parts are only 8: R1–R4, FB1–FB2, J1, J4. The statistics.footprint_count=51 includes all these decorative elements, which could be misleading. The schematic shows 12 components, but J2/J3/J5/J6 are excluded from BOM in the PCB (they appear to be optional solder points not needed for the primary function). The analyzer correctly sets smd_count=6 and tht_count=6 but the total is inflated.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
