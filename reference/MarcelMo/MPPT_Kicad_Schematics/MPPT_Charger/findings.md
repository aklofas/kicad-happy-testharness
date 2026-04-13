# Findings: MarcelMo/MPPT_Kicad_Schematics / MPPT_Charger

## FND-00000923: I2C pullups R29/R30 reported as valid pullups with pullup_rail=GND_J4 — GND_J4 is a ground net; XL7005A U6 estimated_vout=5.375V vs output_rail=+3.3V reported as mismatch — but the vout calculation...

- **Status**: new
- **Analyzer**: schematic
- **Source**: MPPT_Charger.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U3 (AMS1117-5.0 LDO +12V→+5V), U4 (AMS1117-3.3 LDO VBUS→+3.3V), U5 (XL7005A switcher →+12V), U6 (XL7005A switcher →+3.3V) are all correctly detected with appropriate topologies and rail assignments.
- P1 (USB_C_Receptacle_USB2.0_16P): cc1/cc2 5.1k pulldowns pass, VBUS ESD protection fails, VBUS decoupling passes. This is an accurate USB-C compliance check for a device-mode connector.
- The design uses separate ground domains for different subsystems. All five ground variants appear in power_rails and pwr_flag_warnings are raised for each domain without PWR_FLAG, which is the correct behavior.

### Incorrect
- The design_observations report R29 (SDA) and R30 (SCL) as I2C pullup resistors with pullup_rail='GND_J4'. GND_J4 is confirmed to be a ground power symbol. Having resistors from I2C lines to GND would pull-down the bus permanently. The analyzer reports has_pullup=true without raising a warning that the pullup rail is ground rather than a positive supply. This is either a real design bug the analyzer should flag, or the analyzer is wrong about the pullup direction.
  (signal_analysis)
- The XL7005A is a step-down (buck) converter. The feedback divider R18=33k / R19=10k gives ratio=0.2326. With Vref=1.25V (VOUT = Vref*(1+R_top/R_bot)): 1.25*(1+33/10) = 1.25*4.3 = 5.375V. The calculated 5.375V contradicts the +3.3V rail name. The analyzer correctly flags vout_net_mismatch, but the vref assumption of 1.25V for XL7005A should be verified — the XL7005A datasheet specifies Vref=1.25V, so the 5.375V estimate appears correct and the mismatch is real. However, the output is named +3.3V which suggests the divider values may be incorrect in the schematic, not the analyzer.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000924: PCB footprint count (127) vs schematic component count (124) discrepancy is benign

- **Status**: new
- **Analyzer**: pcb
- **Source**: MPPT_Charger.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The 3 extra PCB footprints are REF (4 in PCB, reference designators/fiducials) and HS (1 heatsink) which typically have footprints but no schematic symbols. The NT (net-tie) group shows 16 PCB entries matching the 17 schematic net_ties closely. This is normal.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
