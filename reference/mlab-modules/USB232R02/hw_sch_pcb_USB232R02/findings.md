# Findings: mlab-modules/USB232R02 / hw_sch_pcb_USB232R02

## FND-00001752: Component count of 28 correctly detected with accurate type breakdown; Voltage divider R1/R2 correctly detected as reset pull-up network for FT231X; ESD protection device USBLC6-2SC6 correctly dete...

- **Status**: new
- **Analyzer**: schematic
- **Source**: USB232R02.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 28 total components including 2 ICs (USBLC6-2SC6 ESD protection and FT231XQ USB-UART bridge), 5 connectors, 2 LEDs, 4 resistors, 5 capacitors, 1 fuse, 1 ferrite bead, 1 diode, 1 jumper, 4 mounting holes, and 2 fiducials. All component types match the source schematic.
- The analyzer correctly identifies R1 (4k7) and R2 (10k) forming a voltage divider from +5V to GND with the midpoint connected to U2 pin 11 (~RESET). The ratio of 0.680 is correct (10k/(4.7k+10k)). This is the standard reset pull-up/divider for the FT231XQ.
- The analyzer correctly identifies U1 (USBLC6-2SC6) as an ESD protection IC with protected_nets D+, D-, DN, DP. The protection_devices list correctly captures both F1 (fuse on VBUS path) and U1 as protection devices.
- The design_analysis.bus_analysis.uart array correctly identifies RXD and TXD signal nets connected to U2 (FT231XQ). These are the primary UART interface signals exposed on headers J18 and J19.
- The USB compliance analysis correctly identifies: usb_esd_ic=pass (USBLC6-2SC6 present), vbus_esd_protection=fail (no TVS on VBUS before ESD IC), and vbus_decoupling=fail (no decoupling on VBUS). These are accurate assessments of this design which relies on the ferrite bead FB1 and the fuse F1 rather than a traditional VBUS TVS.
- Three decoupling entries are correctly detected: +5V with C4 (100nF) and C2 (10uF) for 10.1uF total, VCCIO with C5 (100nF), and +3V3 with C3 (100nF). These match the schematic connections to U2 (FT231XQ) power pins.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001753: PCB footprint count, layer count, and routing completeness all correct; Component placement correctly identifies 9 front-side and 19 back-side components

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB232R02.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 28 footprints on a 2-layer board (F.Cu + B.Cu), 219 track segments, 35 vias, routing_complete=true, 0 unrouted nets. Board dimensions 40.13 x 29.97 mm. All values match the KiCad PCB file.
- The PCB has 9 components on F.Cu (connectors J1, J2, J3, J18, J19, fiducials FID1/FID2, mounting holes H1-H4) and 19 components on B.Cu (ICs, passives, LEDs). The gerber analysis independently confirms front=9, back=19, consistent with PCB truth.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001754: Gerber set complete with all expected layers for 2-layer board; Drill classification correctly identifies 35 vias and 46 component holes; F.Paste layer correctly detected as empty (no front-side SM...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-24

### Correct
- All 9 layers present: F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts. Two drill files (PTH and NPTH). completeness.complete=true. Board dimensions consistent with PCB (40.23x30.07mm from gbrjob vs 40.13x29.97mm Edge.Cuts extent).
- Via count of 35 (0.4mm diameter) matches the PCB analyzer's via_count=35. Component holes: 36x 0.889mm + 4x 0.92mm + 2x 2.33mm + 4x 3.0mm = 46 total. Classification uses x2_attributes correctly.
- USB232R02 has all SMD components on the back side (B.Cu). The F.Paste gerber is empty (0 apertures, 0 flashes, 0 draws) and has zero extent, which is correctly captured and consistent with all SMD being on back.
- All 9 expected layers present, PTH and NPTH drill files both present. completeness.complete=true. 62 total holes (11 vias + 48 component holes + 3 NPTH mounting holes). Board dimensions 30.02 x 40.18 mm matches PCB (portrait orientation).
- Gerber drill classification correctly identifies 11 vias using x2_attributes (7x 0.5mm + 4x 0.6mm), matching PCB statistics.via_count=11. Three NPTH mounting holes (2.7mm) are correctly classified as mounting_holes.
- All 9 layers present (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts). completeness.complete=true. The alignment check correctly detects that copper extents (39.1mm wide) are significantly smaller than Edge.Cuts (45.5mm wide) — a 6.4mm variation — and reports aligned=false. This indicates intentional empty keepout area at board edges.
- Drill classification correctly identifies 48 vias (28x 0.3mm + 20x 0.4mm PTH via drills) using x2_attributes, matching PCB statistics.via_count=48. Component holes: 45x 1.0mm + 4x 1.4mm + 4x 3.0mm = 53 PTH component holes. NPTH: 2x 0.65mm (fiducial pads or small NPTH features).

### Incorrect
- The gerber component_analysis reports front_side=15 and back_side=11, but the PCB truth is front=12 (F.Cu THT), back=14 (B.Cu SMD). The gerber derives front count from F.Mask x2_component_count=15, which overcounts because some THT component pads appear in both F.Mask and B.Mask — the analyzer subtracts from total rather than counting from silkscreen or paste layers. The B.Mask x2_component_count=26 includes all 26 components (THT pads through-board), making back_side=26-15=11 also wrong. The PCB-level analysis is authoritative here.
  (component_analysis)
- The gerber component_analysis reports front_side=13, back_side=40 (total 53). The PCB truth is front=12, back=41. The F.Mask x2_component_count=13 is used as the front count, but one component (likely JP2, which is placed on B.Cu but uses a footprint that generates F.Mask openings via through-hole pads) causes the +1 overcount. The back count is correspondingly undercounted by 1. The PCB-level analysis is authoritative.
  (component_analysis)

### Missed
(none)

### Suggestions
(none)

---
