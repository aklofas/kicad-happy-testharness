# Findings: atat-1800 / ATAT1800

## FND-00001982: Component counts correctly parsed for large 1800-layout keyboard; 6x19 keyboard matrix with 101 keys correctly detected; MCP1725-3302E LDO regulator correctly identified as +5V to +3V3; USB Type-C ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ATAT1800.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 342 total components correctly identified: 101 matrix LEDs + 4 THT indicator LEDs = 105 LED total, 52 dual-diode SOT-23 packages for anti-ghosting, 11 ICs (STM32, MCP1725 LDO, 7x MPQ3326 LED drivers, PRTR5V0U2X ESD, 74LVC1G86 XOR). Power rails (+3V3, +5F, +5V, GND) correctly captured. All four power rails including the non-standard +5F (5V filtered for LED drivers via ferrite beads) are present.
- The key matrix detector correctly identified 6 row nets (ROW0-ROW5) and 19 column nets (COL0-COL18), with 101 switches and 101 anti-ghosting diodes on the matrix. SW102 (SW_SPDT slide switch for USB/BT mode select) is correctly excluded from the matrix count. The 1800 layout leaves some of the 6x19=114 positions unfilled, giving 101 actual keys.
- U2 (MCP1725-3302E_SN) correctly identified with topology=LDO, input_rail=+5V, output_rail=+3V3. This is a fixed 3.3V LDO from Microchip that is correctly classified.
- U3 (PRTR5V0U2X) correctly identified as an ESD IC protecting D+ and D- nets. USB compliance checks correctly flag CC1/CC2 5.1k pull-downs as passing, and VBUS decoupling as passing. The vbus_esd_protection=fail is correct — PRTR5V0U2X does not provide VBUS protection.
- Both SCL and SDA I2C buses correctly identified, with R13 (4.7k) and R14 (4.7k) pull-ups to +3V3 detected. The I2C bus connects U1 (STM32F072) to all 7 MPQ3326 LED driver ICs, which is correct for this keyboard design.
- All 8 RC filters are valid: one PWRGD/NRST reset filter (R4+C1, 159Hz cutoff) and seven identical soft-start/enable RC networks (10k + 10uF, 1.59Hz) for the 7 MPQ3326 LED driver ICs. The very low cutoff frequencies are appropriate for slow power sequencing.

### Incorrect
- The PRTR5V0U2X (U3) protects both D+ and D-, as correctly captured in signal_analysis.protection_devices where protected_nets=[D+, D-]. However, the design_observation for USB net D- shows has_esd_protection=false while D+ correctly shows true. The lookup in usb_data observations fails to check the multi-net protected_nets field and only matches D+ by primary protected_net.
  (signal_analysis)
- S1-S7 have value 'MX_stab' and footprints like STAB_MX_6.25u, STAB_MX_2.75u, etc. These are PCB-mounted mechanical keyboard stabilizers (wire guides for long keycaps), not electrical switches. They have no electrical function beyond physical mounting. Classifying them as 'switch' inflates the switch count from 102 real keys to 109.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001983: 4-layer board correctly identified with named power planes; 342 footprints matched to schematic, routing complete

- **Status**: new
- **Analyzer**: pcb
- **Source**: ATAT1800.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB correctly identified as 4-layer (F.Cu, In1.Cu, In2.Cu, B.Cu) with In1.Cu aliased as GND.Cu (power type) and In2.Cu aliased as 5V.Cu (mixed type). Board dimensions 395x122.5mm are correct for an 1800-layout keyboard. All 3 copper zones (GND, +3V3, +5F) are correctly identified as filled.
- Footprint count 342 matches schematic component count. SMD=118, THT=213, exclude_from_pos_files=11 (6 mounting holes H1-H6 + 5 test points TP1-TP5) correctly identified. Routing is complete with 0 unrouted nets across 291 nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
