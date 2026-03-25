# Findings: TOTEM / PCB_totem_0-3_totem_0_3

## FND-00001623: board_width=13.358mm and board_height=48.4mm are far too small; actual component extent is ~237mm x ~78mm

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: TOTEM_PCB_totem_0-3_totem_0_3.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB analyzer reports board_width_mm=13.358, board_height_mm=48.4, derived from the only 14 board-level gr_line Edge.Cuts items (which form a small perforated/mousebite boundary at X:143-157, Y:64-112). The keyboard's actual component span is X:31-269mm (~237mm wide) and Y:50-128mm (~78mm tall), encompassing 38 Kailh PG1350 hotswap sockets and 38 diodes. The true board outline is defined by footprint-level Edge.Cuts (24 fp_line + 32 fp_arc) in the xiao-ble-smd-cutout footprints (U1 at x=41.2, U2 at x=258.8) and mousebite footprints, which the PCB analyzer does not include in board outline computation.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001624: I2C bus detection fires on key-matrix column nets connected to xiao-ble SCL/SDA-capable GPIO pins; key_matrices correctly detects 38-key split keyboard matrix with 8 row-nets and 10 col-nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TOTEM_PCB_totem_0-3_totem_0_3.kicad_sch
- **Created**: 2026-03-24

### Correct
- signal_analysis.key_matrices reports one matrix with rows=8 (ROW0-3_L and ROW0-3_R), columns=10 (COL0-4_L and COL0-4_R), estimated_keys=38, switches_on_matrix=38, diodes_on_matrix=38, detection_method=topology. This accurately models the TOTEM 38-key split wireless keyboard: each half has a 4-row x 5-col submatrix, and the schematic combines L and R sides. The estimated_keys=38 is confirmed by the 38 SWL/SWR key switch instances in the source.

### Incorrect
- design_analysis.bus_analysis.i2c reports four I2C buses: COL1_R (SCL on U2), COL0_L (SDA on U1), COL0_R (SDA on U2), COL1_L (SCL on U1). These are keyboard matrix column signals using GPIO pins on the Seeed XIAO BLE module that are physically capable of I2C but are used here purely as keyboard matrix scan lines. The xiao-ble library symbol labels these GPIO pins as 'SCL' and 'SDA', causing the analyzer to classify connected nets as I2C bus lines. No I2C pull-up resistors are present and no_connects confirm the TOTEM has no I2C devices; the design uses only key matrix, battery, and reset connections.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---
