# Findings: Otter-Iron / KiCAD_Otter-Iron_TS100C

## FND-00001023: Voltage divider R1+R2 on VBUS/UIN/GND detected with correct ratio 0.1515; LDO regulator U2 (AP2204R-3.3) correctly identified with VBUS input and +3V3 output; ESD IC (U1 USBLC6-4SC6) correctly dete...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TS100C.kicad_sch
- **Created**: 2026-03-23

### Correct
- R1=560k (top), R2=100k (bottom) from VBUS to GND with mid-point UIN feeding STM32 PA2 ADC. Ratio 100k/660k=0.1515 is correct.
- Topology=LDO, input_rail=VBUS, output_rail=+3V3, estimated_vout=3.3V from fixed suffix. All correct.
- Protected_nets includes all four USB signal lines. Correct identification of type=esd_ic.
- Q2: is_pchannel=True, load_type=connector, gate resistor R19=20ohm. Q1: type=bjt, emitter_is_ground=True, base resistor R9=2k37. Both correct.
- Both SCL and SDA correctly show has_pullup=True with R3/R4 as pull-up resistors connected to +3V3.
- R? is a real 2k37 resistor on +3V3 that was left unannotated in the schematic. Correctly flagged in annotation_issues.
- VBUS comes from J1 USB-C connector but has no PWR_FLAG in schematic. The GND PWR_FLAG warning is standard but VBUS is a valid design observation.
- U5 output feeds back via R15 (750k) and C16 (18pF) to the inverting input — this is a PI compensator/integrator topology used for tip temperature measurement signal conditioning. Classification is accurate.

### Incorrect
- design_observations reports rails_without_caps=['+3V3'] for U4, U2, U1, U5, U6, and U3, but C3-C11 and C18 (10 caps, 0.1uF and 1uF) are all on the +3V3/GND net. The analyzer fails to associate shared-rail caps with individual ICs when all ICs and caps connect to the same global +3V3 power net.
  (signal_analysis)
- The STUSB4500QTR (U3) is a USB PD sink controller with built-in CC line 5.1k pull-down resistors. The USB compliance checker expects external discrete resistors and incorrectly fails this check. CC1 and CC2 connect directly to U3's CC pins (CC1DB, CC1, CC2, CC2DB), which is the correct design for an IC-managed PD sink.
  (signal_analysis)
- bus_topology.detected_bus_signals shows prefix='CC', width=6, range='CC1..CC2'. With only CC1 and CC2 present, the width should be 2. The width=6 value appears to be a calculation bug in the bus signal width detection.
  (signal_analysis)
- P1 is a Tag-Connect TC2030 SWD/JTAG programming header, not a USB connector. It is flagged in usb_compliance with vbus_esd_protection=fail. The connector has +3V3 and GND (for target power during programming) but is not USB. The analyzer is incorrectly including non-USB connectors that happen to have power pins in USB compliance checks.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001024: 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu) with 84x10mm form factor, 64 footprints, 79 nets, routing complete; DFM violation correctly flagged: 0.106mm track width requires advanced process (standa...

- **Status**: new
- **Analyzer**: pcb
- **Source**: TS100C.kicad_pcb
- **Created**: 2026-03-23

### Correct
- All statistics consistent with schematic: 64 footprints matches 64 schematic components, 79 nets matches, routing_complete=True, unrouted=0.
- The board uses 0.106mm tracks which is below standard 0.127mm but above advanced 0.1mm limit. dfm_tier='advanced' and one violation reported. This is a real design constraint.
- U4's 5.6x5.6mm exposed pad has 8 vias against recommended minimum of 15. Adequacy='insufficient' with untented warning. This is a real DFM concern for the large QFN package.
- Q2 is a power MOSFET switching current to the heating element. Its 1.71x2.37mm exposed pad has zero thermal vias. For a device switching significant heater current, this is a real thermal concern worth flagging.
- The board is extremely dense (84x10mm with 64 components). Multiple courtyard overlaps are reported and appear to reflect real tight placement on this narrow PCB.
- GND has zones on B.Cu/F.Cu/In2.Cu with 25 stitching vias. VBUS uses B.Cu/F.Cu/In1.Cu with 31 vias. +3V3 uses B.Cu/F.Cu with 19 vias. All consistent with 4-layer stackup.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001025: Main gerber set (v6 KiCad) complete: 4-layer, 11 gerber files, 2 drill files, aligned, all layers present

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber
- **Created**: 2026-03-23

### Correct
- Board is 84x10mm matching PCB analyzer. All required layers found, PTH and NPTH drills present. 108 vias (31x0.2mm + 77x0.3mm) consistent with PCB analysis. No alignment issues.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001026: Production V2.3 X2 panel set (KiCad 5.1.4): 4-layer, 90x42mm panel, mixed inch/mm units handled correctly, alignment=True; NPTH holes in production panel classified as 'component_holes' rather than...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: production_X2_OtterIron-V2.3-X2
- **Created**: 2026-03-23

### Correct
- Layer extents are in inches (3.307in = 84.0mm, 3.543in = 90.0mm) while drill_PTH extents are in mm (85.001mm). Despite the mixed units the analyzer correctly reports alignment=True and board_dimensions in mm.

### Incorrect
- The 0.65mm (4x) holes in the panel set are panel alignment pins/tooling holes and should be classified as mounting holes. They are classified as component_holes because the older KiCad 5 gerbers lack X2 NPTH attributes. The diameter_heuristic classification_method is not distinguishing them properly.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001027: Edgerails panel board marked complete=False due to no PTH drill, but this is a bare panel frame with only one NPTH hole

- **Status**: new
- **Analyzer**: gerber
- **Source**: KiCAD_edgerails
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The 'edgerails' gerber set is a PCB panel edge rail (frame board) with no components — it only has one NPTH mounting hole. The completeness check requires has_pth_drill=True but for a component-less panel frame, absence of PTH drill is correct and expected. This is a false positive.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
