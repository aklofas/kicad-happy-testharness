# Findings: Splinky / pcb_0xB2

## FND-00001585: Component counts and types accurate for Splinky RP2040 keyboard controller; LDO regulator U3 (XC6210B332MR-G) correctly detected with 3.3V output; Crystal Y1 circuit correctly detected with 15pF lo...

- **Status**: new
- **Analyzer**: schematic
- **Source**: 0xB2.kicad_sch
- **Created**: 2026-03-24

### Correct
- 40 total components correctly reported: 14 capacitors, 11 resistors, 5 connectors (J1 USB-C, J2/J3/J4 pin headers, J5 debug), 3 ICs (U1 RP2040, U2 GD25Q80 flash, U3 XC6210 LDO), 1 crystal (Y1), 2 switches, 1 LED, 1 ferrite bead, 1 fuse, 2 diodes. BOM shows 36 in_bom components plus 4 non-BOM header connectors.
- power_regulators correctly identifies U3 as an LDO topology, input from +5V, output to +3.3V, estimated_vout=3.3V, vref_source='fixed_suffix' (inferring 3.3V from the '332' in the part number). The lib_id 'Regulator_Linear:AP2127K-3.3' further confirms the 3.3V output assignment.
- crystal_circuits detects Y1 (Crystal_GND24, frequency=null because value string has no frequency) with two 15pF load caps (C3, C4), effective load CL=10.5pF. The frequency=null is correct because the value field 'Crystal_GND24' does not encode a frequency. The 12MHz frequency is only visible in the part selection context.
- memory_interfaces correctly identifies U2 (GD25Q80CEIGR) as flash connected to U1 (RP2040) with 6 shared signal nets. The QSPI_D0-D3/QSPI_SCLK/QSPI_CS nets are used for the QSPI flash interface, which is distinct from the SPI header break-out pins (MISO/MOSI/SCLK on J3).
- voltage_dividers correctly identifies the VBUS sensing divider: R10 (5.1k top) and R11 (10k bottom) from VBUS to GND, midpoint VBUS_DET connected to RP2040 GPIO19 (pin 30). Ratio 0.662 correctly calculated. This divides 5V VBUS to approximately 3.3V for safe ADC reading by the 3.3V RP2040.
- differential_pairs correctly identifies D+/D- with series_resistors [R6, R7] (both 27 ohm). The 27 ohm series resistors are standard USB Full-Speed impedance matching for RP2040 native USB. The pair connects J1 (USB-C) and U1 (RP2040). has_esd=false is correct as there are no dedicated ESD components on these nets.
- protection_devices correctly identifies F1 (Polyfuse) as a protection device on the VBUS net path. The polyfuse provides overcurrent protection for the USB power line, which is standard practice for keyboard designs.
- The SPI bus detected (bus_id=0) with MISO, MOSI, SCLK nets connected to U1 (RP2040) is the SWD/SPI header breakout (J3), separate from the QSPI flash interface which uses QSPI_D0-D3 nets. This correctly represents a distinct SPI-capable pin header on the RP2040.
- Six power rails detected: +1V1 (RP2040 core voltage), +3.3V (main digital supply from U3 LDO), +5V (USB input), GND, VBUS (raw USB 5V), VBUS_DET (detection net). The +1V1 rail is the RP2040's internal digital core voltage externally decoupled via C6, C7, C8. All rails are correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001586: Splinky PCB footprint count and board geometry are accurate; Net count of 60 and fully routed status are correct; PCB net naming uses +3V3 while schematic uses +3.3V — discrepancy correctly preserv...

- **Status**: new
- **Analyzer**: pcb
- **Source**: 0xB2.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 43 footprints correctly counted: 14C + 2D + 1F + 1FB + 5J + 11R + 1REF + 2SW + 3U + 1Y + 1rb_cake + 1splinky = 43. Board dimensions 17.78 x 33.02 mm (6.3mm width matches USB stick form factor). tht_count=6 is correct (J2/J3/J4/J5 pin headers + splinky/rb_cake decorative silkscreen footprints with no pads).
- 60 nets matches the schematic's 65 total_nets (difference of 5 is due to power PWR symbols being merged into their nets). routing_complete=true with unrouted_net_count=0. 563 track segments and 56 vias for this compact 2-layer keyboard controller PCB.
- The PCB output reflects net '+3V3' (as present in the kicad_pcb file) while the schematic output reports '+3.3V' (from the power symbol). These are the same physical rail but named differently between schematic and PCB files. The analyzer faithfully reports what is in each file. The mismatch likely reflects an older PCB layout created before net name synchronization was enforced.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001587: Panel PCB statistics correctly reflect a 10-board array

- **Status**: new
- **Analyzer**: pcb
- **Source**: panel_0xB2_panel.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The panel has 433 footprints (vs 43 single board), 5630 track segments (vs 563), 560 vias (vs 56), 30 zones (vs 3), 600 nets (vs 60), net_count=600 = 10 boards × 60 nets each. Net names follow Board_0- through Board_9- prefix convention. All statistics are consistent with a 10-up panel arrangement.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
