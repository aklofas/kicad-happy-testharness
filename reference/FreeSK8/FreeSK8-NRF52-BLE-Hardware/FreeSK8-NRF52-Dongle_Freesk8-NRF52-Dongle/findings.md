# Findings: FreeSK8/FreeSK8-NRF52-BLE-Hardware / FreeSK8-NRF52-Dongle_Freesk8-NRF52-Dongle

## FND-00000555: BT840F (U1) right-side pin-to-net assignments are systematically wrong; Net 'P0.09' assigned to U1 pin 1 (P0.26/SDA) and net 'SDA' assigned to U1 pin 7 (P0.09) — swapped; I2C bus misdetection: GPS-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FreeSK8-NRF52-Dongle_Freesk8-NRF52-Dongle.sch.json
- **Created**: 2026-03-23

### Correct
- The power_regulators section correctly identifies IC1 as an LDO converting +5V to +3.3V, with correct topology='LDO', input_rail='+5V', output_rail='+3V3', estimated_vout=3.3.
- crystal_circuits correctly identifies Y1 (ECS-.327-9-34QCS-TR) with load caps C3 and C4 both 12pF, effective_load_pF=9.0, which is the standard series calculation ((12*12)/(12+12) + ~3pF stray).
- 16 total components: 7 caps, 3 resistors, 2 ICs (BT840F + LP5912), 1 crystal, 1 LED_RGBC, 2 connectors. All match the schematic source.

### Incorrect
- The analyzer connects right-side BT840F pins to the wrong nets. Net 'SWDIO' is assigned U1 pin 10 (GND), net 'SWCLK' gets pin 11 (P0.11), net 'RST' gets pin 12 (P1.00), net 'P0.11' gets pin 15 (SWCLK), net 'P1.00' gets pin 14 (P0.18/RESET). The pin-coordinate-to-wire matching is off by several positions. The symbol has right-side pins ordered by y-coordinate (SWDIO=pin16 at top, GND=pin10 at bottom) but the wires are being mapped to the wrong pin numbers. Specifically, the net 'SWDIO' ends up on U1's GND pin — a critical miswiring that would produce invalid downstream analysis.
  (signal_analysis)
- On the left side of U1 (BT840F), the text label 'P0.09' should connect to the pin named P0.09 (pin 7), and the label 'SDA' should connect to P0.26/SDA (pin 1). The output has them reversed: net 'P0.09' contains pin 1 (P0.26/SDA) and net 'SDA' contains pin 7 (P0.09). This affects the I2C bus detection which reports SDA/SCL on the wrong pins.
  (signal_analysis)
- Because net 'GPS-RX' is mapped to U1 pin 2 (P0.27/SCL) instead of pin 3 (P0.00/XL1), the bus_analysis reports GPS-RX as an I2C SCL line. In reality GPS-RX is a UART signal connected to the GPS TX line, not I2C. The UART detector correctly identifies GPS-RX as UART, but the I2C detector also incorrectly flags it.
  (signal_analysis)

### Missed
- IC1 pin 4 (EN) is on __unnamed_58 with point_count=1 and IC1 pin 3 (PG) is on __unnamed_57 with point_count=1 — both single-point unconnected nets. The LP5912 EN pin floating means enable state is indeterminate; PG floating means the power-good signal is unused. The design_observations section flags some single-pin nets but IC1's floating EN/PG are not specifically called out as a design concern.
  (signal_analysis)
- The schematic has both '+3.3V' and '+3V3' power symbols that refer to the same physical 3.3V rail from IC1, but the analyzer treats them as separate rails. The +3V3 net has IC1 output and C1/C2 (input decoupling), while +3.3V has J2 connector, C7, and BT840F VDD bypass. The +3.3V net does not connect to U1 VDD at all in the net list (U1 VDD is __unnamed_3), suggesting the BT840F VDD connection is also affected by the pin-mapping error.
  (signal_analysis)

### Suggestions
(none)

---
