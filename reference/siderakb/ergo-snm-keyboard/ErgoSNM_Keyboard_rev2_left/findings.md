# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev2_left

## FND-00002187: W25Q128JVS QSPI flash memory interface correctly detected and linked to RP2040

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev2_left_RP2040.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies U3 (W25Q128JVS, a 128Mbit SPI NOR flash) connected to U4 (RP2040) with 6 shared signal nets. The memory_interfaces detection properly reports total_pins=8 and the connected processor. The QSPI bus signals (QSPI_D0..D3, QSPI_CLK, QSPI_CS) are also reflected in bus_topology.detected_bus_signals for QSPI_D. The 12MHz crystal circuit (Y1 with 20pF load caps) is correctly detected with calculated effective load of 13pF.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002188: Key matrix correctly detected across the hierarchical schematic (6x8, estimated 29 keys); USB-C CC pulldown check incorrectly reports 'fail' for J2 which may be a host-side port requiring different...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev2_left_left.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The hierarchical rev2 left schematic correctly aggregates all sub-sheets and detects the 6-row x 8-column key matrix using ROW_0..ROW_5 and COL_0..COL_7 net names. The matrix count shows 29 switches (matching actual KEY1..KEY29) and 29 diodes (matching D1..D29). The power regulator (RT9013-33GB LDO converting +5V to +3V3) and the 12MHz crystal circuit are also correctly detected. Total component count of 110 matches the PCB footprint count exactly.

### Incorrect
- J2 (USB_C_Receptacle_USB2.0, HRO TYPE-C-31-M-12) fails cc1_pulldown_5k1 and cc2_pulldown_5k1 checks. The CC pins (A5/B5) of J2 show no 5.1k pulldown resistors in the schematic. The design has two USB-C ports: J1 (passes CC checks, passes D+/D- series resistor checks) and J2 (fails). J2 appears to be used as a power-only or secondary port where CC resistors are omitted—a known design tradeoff for device-to-device connections. The analyzer does not contextually distinguish between primary data ports (requiring CC pulldowns) and auxiliary power-only USB-C ports.
  (usb_compliance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002192: PCB DFM correctly flags board exceeding 100x100mm JLCPCB pricing tier for all rev2/rev3 boards; Courtyard overlaps correctly detected: KEY1/LD2 on F.Cu (LED placed inside key switch courtyard)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: ErgoSNM_Keyboard_rev2_left_left.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- All rev2 and rev3 keyboard PCBs (left, right, receiver, thumb cluster at 115.57x106.68mm) correctly trigger the board_size DFM violation noting the JLCPCB pricing tier boundary. The keyboard plate PCBs (116.25x111.5mm) are also correctly flagged. The routing is reported as complete (routing_complete=true, unrouted_count=0) for all boards. The 2-layer stackup (F.Cu/B.Cu) is correctly identified, and GND+3V3 zone stitching with via density analysis is correctly reported.
- The analyzer correctly identifies a courtyard overlap between KEY1 (key switch) and LD2 (status LED) on F.Cu with 1.776mm2 overlap, and between J3 and D12 on B.Cu with 0.343mm2 overlap. The KEY1/LD2 overlap is noteworthy in a keyboard design—it suggests the LED is intentionally placed within the key switch footprint area, which is a common technique for per-key RGB but requires careful 3D verification. The 22 tombstoning risk flags for 0402 capacitors with GND pour on one pad are also correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
