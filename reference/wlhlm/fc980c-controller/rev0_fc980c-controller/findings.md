# Findings: wlhlm/fc980c-controller / rev0_fc980c-controller

## FND-00002064: Capacitive keyboard matrix not detected — design uses bit-encoded COL_BIT/ROW_BIT signals via external IC

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fc980c-controller_rev2_fc980c-controller.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The fc980c is a capacitive keyboard controller for the Topre FC980C. The key matrix uses an external matrix-scanning IC connected to the keyboard via a 20-pin 'KEYBOARD' JST connector (J3). Row and column selection is communicated via 3-bit ROW_BIT[0:2] and 4-bit COL_BIT[0:3] encoded addresses, plus KEY_STATE and KEY_ENABLE control signals. The analyzer's key_matrices detector finds nothing because it looks for conventional direct ROW/COL nets with diodes. This is a false negative — the design definitely contains keyboard matrix logic, just at a higher abstraction level. A note in design_observations or a pattern matching 'bit-encoded keyboard matrix' signals would be valuable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002065: SPI flash memory interface correctly detected: W25Q128JVS connected to RP2040 via 6 shared nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fc980c-controller_rev0_fc980c-controller.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- For the rev0 (RP2040-based) design, the analyzer correctly identifies W25Q128JVS (128Mbit SPI flash) connected to RP2040 with 6 shared signal nets — matching the full SPI flash pinout: SCK, MOSI/MISO (QSPI data lines), CS, WP (write protect), and HOLD/RESET. The 12MHz crystal oscillator is also correctly identified with 27pF load capacitors (effective CL = 16.5pF). For rev2 (STM32F401 design), the I2C EEPROM M24C64 is correctly detected sharing 2 nets (SCL, SDA) with the MCU.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002066: routed_nets=32 vs total_nets_with_pads=46 is misleading but not erroneous — gap is no-connect nets

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_fc980c-controller_rev2_fc980c-controller.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The connectivity section reports routing_complete=True and unrouted=0, but routed_nets=32 while total_nets_with_pads=46. The 14-net gap corresponds exactly to pads with 'unconnected-(U2-PadN)' net names — these are intentional no-connect pads on the STM32F401CBUx (unused GPIO pins). These nets have pads but no tracks because they are deliberately unconnected. The displayed 'routed_nets' metric could be confusing to users who see 32 vs 46 alongside routing_complete=True. Adding a 'no_connect_net_count' field or noting this distinction would improve clarity.
  (connectivity)

### Missed
(none)

### Suggestions
(none)

---
