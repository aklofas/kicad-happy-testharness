# Findings: USB-C-Breakout / USB-C-breakout

## FND-00001553: USB interface not detected for USB4105-GF-A connector; Differential pairs not detected for DP1/DN1 and DP2/DN2 nets; Component count and types correctly extracted

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-C-Breakout_USB-C-breakout.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Three connectors correctly identified: J1 (USB4105-GF-A, qty 1), J2 and J3 (Conn_01x06, qty 2). All 11 nets (GND, VBUS, CC1, CC2, DP1, DN1, DP2, DN2, SBU1, SBU2, Shell) match the schematic source.

### Incorrect
(none)

### Missed
- J1 is a GCT USB4105-GF-A USB-C connector with explicitly USB-C signals (VBUS, GND, CC1, CC2, DP1, DN1, DP2, DN2, SBU1, SBU2, Shell). The analyzer produces an empty usb_interfaces list despite the connector being a named USB-C part. The value 'USB4105-GF-A' and the signal naming are unambiguous USB-C indicators.
  (signal_analysis)
- The schematic has two USB differential pairs: DP1/DN1 (side A) and DP2/DN2 (side B), both directly connected from the USB-C connector J1 to the breakout headers. The analyzer returns an empty differential_pairs list, failing to detect pairs with DP*/DN* naming convention (as opposed to D+/D-).
  (design_analysis)

### Suggestions
(none)

---

## FND-00001554: J1 USB-C connector correctly typed as through_hole; copper_layers_used=1 is accurate — all 36 track segments are on F.Cu; Unrouted Shell net correctly identified

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB-C-Breakout_USB-C-breakout.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- USB4105-GF-A uses a mixed footprint with THT mounting pins. The PCB file declares attr=through_hole for the footprint. The analyzer correctly reports type=through_hole for J1. The 15 total footprints (3 real + 12 kibuzzard decorative) are also counted correctly.
- Confirmed via source file: all 36 segments use layer F.Cu. J2 and J3 are on B.Cu but only have THT pads that span both layers; there are no routing tracks on B.Cu. The analyzer correctly reports copper_layers_used=1 and a layer_distribution of {F.Cu: 36}.
- The Shell net (4 pads: J1.S1–S4) has no routing in the PCB file. The analyzer correctly reports routing_complete=false with unrouted_count=1 and identifies the Shell net with its 4 pads as the unrouted net.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001555: Gerber set is complete and both drill files present; Alignment flagged as failed due to decorative kibuzzard silkscreen elements

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: USB-C-Breakout_gerbers.json
- **Created**: 2026-03-24

### Correct
- All 9 expected layers found (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). Both PTH and NPTH drill files are present. Completeness check passes.

### Incorrect
- The analyzer reports aligned=false with width varying 4.4mm and height 3.6mm across layers. This is caused by the extensive kibuzzard silkscreen graphics (USB-C pinout diagram) extending beyond the board copper area, not by a genuine misalignment. B.Paste is also empty (THT/through-hole board), causing its extent to read 0x0. This is expected behavior for this board type and not a fabrication concern.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001556: USB interface not detected for Wurth-632723300011 USB-C connector; U1 (PRTR5V0U2X) pin-to-net mapping is wrong due to KiCad 5 legacy net tracing error; PRTR5V0U2X correctly identified as ESD protec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-C-Breakout-PCB_USBCBreakout.sch.json
- **Created**: 2026-03-24

### Correct
- Despite the pin-to-net mapping error, the analyzer correctly identifies U1 as an esd_ic protecting D+ and D- differential nets. The fuse F1 is also correctly detected as a protection device on the VCC rail.
- The analyzer correctly identifies one differential pair (D+/D-) with has_esd=true and esd_protection=[U1]. The shared ICs include J1, U1, and USB1 which are all legitimately on the D+/D- nets.

### Incorrect
- The analyzer places U1 pin 1 (named 'GND') on net D+ and U1 pin 4 (named 'VCC') on net D-. Cross-checking with the PCB output confirms the correct mapping: pad1=GND, pad2=D+, pad3=D-, pad4=VCC. This is a net tracing bug in the KiCad 5 .sch parser. As a consequence, U1's GND pin appears on D+ and VCC pin appears on D-, creating incorrect ERC warnings and corrupted net membership for those signals.
  (design_analysis)

### Missed
- USB1 (Wurth-632723300011) is a USB-C connector with named USB signals (VBUS, GND, CC1, CC2, D+, D-, SBU1, SBU2). The analyzer returns an empty usb_interfaces list. The part name 'Wurth-632723300011' and presence of typical USB-C signals should trigger detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001557: Via count (7) and routing completeness correctly extracted from KiCad 5 PCB

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB-C-Breakout-PCB_USBCBreakout.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Confirmed via PCB source: exactly 7 via elements present, all 0.8mm/0.4mm through-vias. The analyzer reports via_count=7 and routing_complete=true, matching the source. The 21 x 0.4mm drills in the gerbers include 14 USB connector THT anchor pads.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001558: 21 holes at 0.4mm misclassified as vias; 14 are USB connector THT anchor pads; Gerber set complete and alignment correct for USB-C-Breakout-PCB

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: USB-C-Breakout-PCB_Gerbers.json
- **Created**: 2026-03-24

### Correct
- All 9 expected Gerber layers present (source=defaults, no gbrjob). Alignment is reported as aligned=true. The board has 2 copper layers with 122 segments and 7 vias confirmed from PCB analysis.

### Incorrect
- The gerber drill classification reports vias.count=21 using diameter_heuristic. However, PCB analysis confirms only 7 actual vias exist. The remaining 14 holes at 0.3988mm (~0.4mm) are through-hole anchor/shield pads belonging to the Wurth-632723300011 USB-C connector footprint, which is declared as attr=smd in the PCB file but includes THT mechanical legs. Without X2 aperture attributes in these KiCad 5 gerbers, the heuristic cannot distinguish connector THT holes from vias.
  (drill_classification)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001919: J1 USB4105-GF-A not recognized as USB Type-C connector (is_type_c=False); Correctly identifies all 3 components (1 USB-C connector, 2 pin headers), 11 nets, and correct power rails

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-C-Breakout_USB-C-breakout.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- total_components=3 matches source exactly (J1, J2, J3). Nets GND, VBUS, CC1, CC2, DP1/DP2, DN1/DN2, SBU1/SBU2, Shell all correctly detected and match the 11 nets in the PCB. Power rails [GND, VBUS] correct. kicad_version='unknown' for file_version 20211123 is a known limitation (no version map for KiCad 6.0 early release format).

### Incorrect
- The GCT USB4105-GF-A is a 16-pin USB Type-C receptacle. Its presence of CC1, CC2, DP1, DP2, DN1, DN2, SBU1, SBU2 nets confirms it is Type-C. The analyzer outputs is_type_c=False because the lib_id 'USB4105-GF-A:USB4105-GF-A' does not match the standard 'Connector:USB_C_*' pattern. As a result, the USB-C compliance checks (cc1_pulldown_5k1, cc2_pulldown_5k1) are never run for this connector. This is a generic issue: non-standard-library USB-C footprints will not be recognized.
  (usb_compliance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001920: PCB footprint, net, and track counts correct; Shell net unrouted correctly flagged; copper_layers_used=1 (F.Cu only) but gerber reports layer_count=2 — different measurements, PCB value is correct

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: USB-C-Breakout_USB-C-breakout.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 15 footprints correct (3 real components + 12 kibuzzard board_only graphics). 11 nets correct (PCB defines nets 1-11 = GND/VBUS/CC1/DP1/DN1/SBU1/CC2/DP2/DN2/SBU2/Shell). 36 track segments correct. routing_complete=False with Shell net unrouted is accurate — Shell net has 4 pads (J1.S1-S4) but no copper connections, which is intentional for this breakout. SMD=0, THT=3 correct for this board (USB4105 footprint uses through_hole attr for its mounting pins).

### Incorrect
- The PCB board setup only defines F.Cu as a signal layer. B.Cu references in the PCB file are only back-side pad definitions for the through-hole connectors (J2/J3 pin headers). The PCB analyzer correctly reports 1 copper layer. The gerber analyzer reports 2 because a B.Cu.gbr file exists with 16 THT pad flashes. These measure different things (design layers vs fab output files) and neither is wrong, but the inconsistency between the two outputs may confuse users comparing them.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001921: Layer alignment flagged as False due to differing copper vs outline extents — expected for this design, not a real defect; Gerber layer completeness correctly verified: all 9 expected layers presen...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: USB-C-Breakout_gerbers.json
- **Created**: 2026-03-24

### Correct
- All expected layers found: F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts. Both PTH (12 holes, 1.0mm for J2/J3 pin headers) and NPTH (2 holes, 0.65mm for USB4105 mounting posts) drill files present. completeness.complete=True is correct. The gbrjob file is parsed and board dimensions (24.65×16.4mm) match PCB source.

### Incorrect
- The gerber analyzer reports aligned=False with 'Width varies by 4.4mm' and 'Height varies by 3.6mm' across copper/edge layers. However, this is expected: F.Cu and B.Cu only contain pad flashes (20.13×12.7mm copper extent) while Edge.Cuts defines the full 24.55×16.3mm board outline. Copper not filling the full board area is normal for a passive breakout with only edge-mounted connectors. B.Paste is 0×0 (no back-side paste) and F.Paste is 6.4×0.0 (only the USB-C SMD pads). The alignment check algorithm is too strict — it should not flag copper not reaching the board edges as a misalignment.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
