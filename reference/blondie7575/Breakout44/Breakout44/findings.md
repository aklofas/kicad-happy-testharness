# Findings: Breakout44 / Breakout44

## FND-00000437: SPI bus not detected despite MOSI/MISO/SCLK/SS pins present on ATmega32U4-A; UART not detected despite TXD/RXD pins present on ATmega32U4-A; All component refs are null in the components array desp...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breakout44.sch.json
- **Created**: 2026-03-23

### Correct
- The KiCad 5 legacy schematic has clear reference designators: U1 (ATmega32U4-A), P1 (CONN_01X22), P2 (CONN_01X22), P3 (CONN_02X03). These refs appear correctly in statistics.missing_mpn, the BOM entries, net pin entries (e.g. nets reference 'U1', 'P1', 'P2', 'P3'), and subcircuits. However every entry in the top-level components array has ref=null. The KiCad 5 legacy parser correctly extracts refs for nets and BOM but fails to populate them in the structured components list.

### Incorrect
(none)

### Missed
- The ATmega32U4-A has SPI pins connected to P2: PB2 named '(PDI/MOSI/PCINT2)PB2', PB3 named '(PDO/MISO/PCINT3)PB3', PB1 named '(SCLK/PCINT1)PB1', and PB0 named '(SS/PCINT0)PB0'. All four SPI signals are routed to P2 connector pins. The I2C detector correctly finds 'SCL' within '(OC0B/SCL/INT0)PD0' and 'SDA' within '(SDA/INT1)PD1' using substring matching, but the SPI detector fails to find 'MOSI', 'MISO', 'SCLK', and 'SS' within the same style of composite ATmega pin names. bus_analysis.spi is empty.
  (design_analysis)
- The ATmega32U4-A has UART pins connected to P2: PD3 named '(TXD/INT3)PD3' and PD2 named '(RXD/INT2)PD2'. Both are routed to P2 connector pins. The I2C detector works by substring matching pin names, but the UART detector misses 'TXD' within '(TXD/INT3)PD3' and 'RXD' within '(RXD/INT2)PD2'. bus_analysis.uart is empty.
  (design_analysis)

### Suggestions
(none)

---
