# Findings: apertus-open-source-cinema/axiom-micro-mainboard / pcb

## FND-00001986: 91 components correctly parsed with 13 distinct power rails; Test point pads SCL1/SDA1/GND1/LED1 classified inconsistently — switch, other, and test_point types all assigned to identical components...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb.sch
- **Created**: 2026-03-24

### Correct
- All 91 schematic components correctly identified: 36 capacitors, 14 resistors, 16 connectors, 7 ICs, 10 ferrite beads (L-prefixed but correctly typed as ferrite_bead based on value 'FB'), 3 WS2812B LEDs. 13 power rails correctly captured including LVDS-related supply rails (VDD_HISPI, VDD_HISPI_TX, etc.) for the camera interface design.
- D1, D2, D3 (ws2812b) are detected as 3 separate chains of length 1. This is consistent with the board layout: three corner status LEDs individually controlled rather than daisy-chained. Each has its own DIN signal, so the chain-length-1 detection is accurate.
- The 10 inductors (L1-L10) with value 'FB' and footprint 'ferrite_bead_0402_handsoldering' are correctly identified as ferrite_bead type despite the 'L' reference prefix. This is correct classification based on value and footprint, not just the reference prefix.
- The design_analysis.differential_pairs detects 17 pairs, consistent with the LVDS and SLVS differential pairs visible in the PCB net list (LVDSn0_P/N through LVDSn5_P/N, LVDSs0_P/N through LVDSs5_P/N, SLVSC_P/N, SLVS2_P/N, SLVS3_P/N). This is a camera interface board connecting a Z-TURN-LITE SOM to an image sensor.

### Incorrect
- SCL1, GND1, SDA1, LED1 all share the same value='TEST', footprint='Test_Point_Pad_2.0x2.0mm', and lib_id='device1:TEST'. Despite being identical components, the analyzer assigns different types: SCL1→switch, SDA1→switch, GND1→other, LED1→test_point. All four should be classified as test_point. The classification is nondeterministic or depends on some per-instance state rather than the component's intrinsic properties.
  (statistics)
- U6 (ADP150-2.8) is a fixed 2.8V LDO from Analog Devices. The analyzer reports topology='unknown', input_rail=null, output_rail=null, estimated_vout=null. From the PCB layout, U6 is connected to +5V input (pin 1) and +2V8 output (pin 5). The value 'ADP150-2.8' encodes the output voltage in its part number (2.8V). The schematic also has +2V8 as an explicit power rail. The LDO topology should be recognized at minimum from the -2.8 suffix.
  (signal_analysis)

### Missed
- The decoupling_analysis correctly finds 10 entries for rails like VAA, VDD, VDDIO_35 etc. However, the +2V8 rail (output of ADP150-2.8) is not represented in decoupling_analysis even though it has bypass capacitors (C10 per the PCB pad_nets). This is likely caused by the LDO output_rail=null failure — without knowing the rail name, decoupling caps on that net cannot be associated.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001987: 4-layer PCB with 96 footprints, routing complete, advanced DFM tier; Advanced DFM tier correctly flagged for sub-0.127mm track widths

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu) correctly parsed with 96 footprints (74 SMD + 9 THT + 13 virtual). The 5 extra footprints vs 91-component schematic are: 4 fiducials + 1 OSHW logo silkscreen. DFM correctly flagged as 'challenging' tier due to 0.125mm tracks below the 0.127mm standard limit. Routing complete with 310 vias.
- The minimum track width 0.125mm is below the standard PCB manufacturing limit of 0.127mm, correctly triggering the 'challenging' DFM tier with a track_width violation. This is appropriate for the camera interface high-speed routing requirements.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
