# Findings: SriramGDev/USB-C-Breakout-PCB / USBCBreakout

## FND-00001559: USB interface not detected for Wurth-632723300011 USB-C connector; U1 (PRTR5V0U2X) pin-to-net mapping is wrong due to KiCad 5 legacy net tracing error; PRTR5V0U2X correctly identified as ESD protec...

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

## FND-00001560: Via count (7) and routing completeness correctly extracted from KiCad 5 PCB

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

## FND-00001561: 21 holes at 0.4mm misclassified as vias; 14 are USB connector THT anchor pads; Gerber set complete and alignment correct for USB-C-Breakout-PCB

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
