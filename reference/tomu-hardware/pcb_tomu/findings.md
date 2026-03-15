# Findings: tomu-hardware / pcb_tomu

## FND-00000143: Minimal USB board (EFM32HG): USB differential pairs detected but very sparse analysis output for 22-component design, many components marked DNP

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/tomu-hardware/pcb/tomu.sch
- **Created**: 2026-03-14

### Correct
- USB differential pairs detected: USB_D+/USB_D- with shared IC P3 (USB connector), and routed USB pair RUSB_D+/RUSB_D-
- Series resistors R3/R4 correctly identified on USB data lines
- UART nets LEU0_TX/LEU0_RX detected in bus analysis
- Power rail +3V3 and GND correctly identified
- 12 DNP parts correctly counted - reflects the minimal BOM approach

### Incorrect
- USB differential pairs list R3/R4 as series resistors on both the USB_D+/- pair AND the RUSB_D+/- pair - they should only appear once in the signal path
  (design_analysis.differential_pairs)
- UART bus shows 0 devices and 0 pin_count for LEU0_TX/LEU0_RX - should at minimum identify the EFM32 MCU
  (design_analysis.bus_analysis)

### Missed
- EFM32HG (Happy Gecko) MCU not identified in IC pin analysis - this is the main and essentially only IC on the board
  (ic_pin_analysis)
- No power regulator detected - the board likely derives 3.3V from USB 5V through the EFM32 internal regulator or an external component
  (signal_analysis.power_regulators)
- Touch/capacitive sensing pads (LEDs used as touch sensors on Tomu) not identified
  (signal_analysis)
- USB device configuration (bus-powered, no external crystal needed for USB on EFM32HG) not noted
  (usb_compliance)
- No decoupling analysis despite capacitors being present
  (signal_analysis.decoupling_analysis)

### Suggestions
- Ensure legacy KiCad 5 .sch parsing extracts IC components for pin analysis
- For minimal designs, ensure all ICs are captured even when there are few components
- Detect bus-powered USB devices that derive power from VBUS

---
