# Findings: brechtve-kicad-things / Templates_brechtve-kicad-arm-template_brechtve-kicad-arm-template

## FND-00002290: SWD interface not detected in bus_analysis despite SWDIO/SWCLK nets present; UART nets (TXD/RXD) correctly detected and classified

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_brechtve-kicad-things_Templates_brechtve-kicad-arm-template_brechtve-kicad-arm-template.sch.json
- **Created**: 2026-03-24

### Correct
- The ARM template includes a UART debug header (J3=DebugHeader_UART_4p) with TXD and RXD nets. The analyzer correctly identifies them in bus_analysis.uart and classifies TXD as 'data' in net_classification. The RC filter on ~RESET (R5=1kΩ, C1=100nF, fc=1.59kHz) is correctly detected as a low-pass filter for debounce/noise filtering on the ARM reset pin.

### Incorrect
(none)

### Missed
- The design has a Cortex-M SWD debug header (J1) with SWDIO and SWCLK nets, both correctly classified in net_classification as 'debug' and 'clock'. However, bus_analysis shows no SWD entry — the analyzer only looks for I2C, SPI, UART, and CAN buses. SWD/JTAG debug interfaces are a common pattern in ARM MCU designs and should be detected.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002291: Empty PCB template correctly reported with zero footprints and tracks

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_brechtve-kicad-things_Templates_brechtve-kicad-arm-template_brechtve-kicad-arm-template.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The ARM template PCB file is intentionally blank (it is a starting template). The analyzer correctly reports footprint_count=0, track_segments=0, net_count=0, routing_complete=true, and board dimensions as null. The board_metadata title 'KiCad Project ARM Template' is correctly extracted from the PCB title block.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
