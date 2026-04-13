# Findings: staticintlucas/goldfish / cad_goldfish

## FND-00002105: usb_compliance vbus_esd_protection reports fail despite USBLC6-2P6 being connected to VBUS; Crystal circuit, USB-C CC pulldowns, and decoupling analysis correctly detected for ATmega32U4 USB HID de...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_goldfish_cad_goldfish.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly: identifies the 16 MHz crystal (X1) with two 22 pF load caps (C7, C8) and computes effective load capacitance of 14 pF; detects CC1/CC2 5.1k pulldown resistors (R1, R2) as passing USB-C device compliance; finds decoupling caps on VBUS (C5 0.1uF + C6 4.7uF) and VCC rails; identifies F1 as a fuse protecting the VBUS line from RAW; and correctly counts 26 schematic components matching the BOM.

### Incorrect
- The usb_compliance check passes usb_esd_ic (correctly detects USBLC6-2P6) but fails vbus_esd_protection. The USBLC6-2P6 is a dedicated USB ESD protection IC whose pin 5 is VBUS — it provides bidirectional TVS clamping on VBUS as part of its designed function, not just D+/D- protection. U2 (USBLC6-2P6) pin 5 is confirmed connected to the VBUS net. The vbus_esd_protection check apparently looks for a separate TVS/Zener on VBUS and does not recognize the USBLC6-2P6 VBUS pin as providing that protection. This is a false failure.
  (usb_compliance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002106: PCB correctly reports 27 footprints (26 schematic components + 1 logo) with no routing violations

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_goldfish_cad_goldfish.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The goldfish PCB has 27 footprints versus 26 schematic components. The extra footprint is 'G*** LOGO' — a mechanical/artwork footprint that correctly has no schematic counterpart. Routing is complete (0 unrouted nets), DFM tier is 'standard' with no violations, and 2 copper zones are present (GND pour on both layers, VCC pour on B.Cu). The PCB component count (27) is a correct enumeration of all physical footprints, not an error.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
