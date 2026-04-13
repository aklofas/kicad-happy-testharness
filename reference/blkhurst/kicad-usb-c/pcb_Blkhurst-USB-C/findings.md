# Findings: blkhurst/kicad-usb-c / pcb_Blkhurst-USB-C

## FND-00002269: USB4215-03-A (USB Type-C connector) incorrectly identified as not USB-C; 5.1k CC pull-down resistors (R1, R2) not recognized as USB-C CC termination

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-usb-c_pcb_Blkhurst-USB-C.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The USB4215-03-A from Amphenol is a USB Type-C connector, as confirmed by its pin names: CC1, CC2, SBU1, SBU2, Dp1, Dn1, Dp2, Dn2, VBUS. The analyzer sets is_type_c=false in the usb_compliance section. The type-C detection relies on value/description string matching but misses this part because the description field is empty and the value 'USB4215-03-A' is not recognized as a USB-C part number pattern.
  (usb_compliance)

### Missed
- In a USB-C UFP (device) implementation, 5.1k resistors on CC1 and CC2 to GND are required by the USB-C spec for role detection. The design has R1 and R2 at 5.1k connected to the CC1 and CC2 pins of USB1. The usb_compliance checks report 'vbus_esd_protection: fail' and 'vbus_decoupling: fail' but never check for or report on CC termination resistors, which is a significant USB-C compliance item.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002270: USB4215-03-A footprint classified as through_hole instead of SMD

- **Status**: new
- **Analyzer**: pcb
- **Source**: kicad-usb-c_pcb_Blkhurst-USB-C.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Amphenol USB4215-03-A is an SMD USB Type-C connector (surface mount with optional through-hole pins for mechanical strength). The PCB analyzer classifies it as type='through_hole', which affects DFM analysis and SMD/THT counts. The schematic assembly_complexity section also reports smd_count=1 and tht_count=11, suggesting the USB connector alone is counted as SMD at the schematic level but the PCB analysis disagrees.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
