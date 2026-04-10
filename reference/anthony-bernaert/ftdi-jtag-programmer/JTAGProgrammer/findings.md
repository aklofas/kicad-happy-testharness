# Findings: ftdi-jtag-programmer / JTAGProgrammer_JTAGProgrammer

## FND-00002073: FT2232HL JTAG and UART interfaces not detected despite named nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ftdi-jtag-programmer_JTAGProgrammer_FTDI.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The FTDI sub-sheet contains a FT2232HL (U1) with ADBUS0=JTAG_TCK, ADBUS1=JTAG_TDI, ADBUS2=JTAG_TDO, ADBUS3=JTAG_TMS, ADBUS7=JTAG_SRST on channel A, and BDBUS0=UART_TXD, BDBUS1=UART_RXD, BDBUS2=UART_RTS, BDBUS3=UART_CTS on channel B. None of these are detected as JTAG or UART interfaces. The named nets (JTAG_TCK, UART_TXD, etc.) are flagged only as 'single_pin_nets' in design_observations, but no JTAG bus detector or UART bus detector fires. The four 74LVC3G17 buffer/level-shifter ICs (U4-U7) between the FTDI and target connector are also not identified as level shifters.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002074: ESD protection on USB_D+/USB_D- falsely reported absent (has_esd_protection: false); 93LC56B Microwire EEPROM (U3) interface not detected; 17 hierarchical labels incorrectly reported as unconnected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ftdi-jtag-programmer_JTAGProgrammer_JTAGProgrammer.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The design_observations for USB_D+ and USB_D- both report has_esd_protection: false. However, D1 and D2 are PGB1010603MR (Littelfuse TVS diode array), a standard USB ESD protection device. D1 and D2 are explicitly listed in the 'devices' array for those nets, so the analyzer sees them but still sets the flag to false. The ESD protection check does not recognize PGB1010603MR as an ESD/TVS device because it uses a custom lib_id (PGB1010603MR:PGB1010603MR) rather than a standard library name like Diode: or TVS:.
  (signal_analysis)
- The hierarchical_labels section reports 17 unconnected_hierarchical labels: SRST, TCK, TDI, TDO, TMS from the JTAG connector sub-sheet (UUID 0ad90f15) and CTS, RTS, RXD, TXD, VBUS from the UART connector sub-sheet (UUID 58123637). These labels are connected at the top level: the top-level sheet instantiates both the JTAG connector sub-sheet and the FTDI sub-sheet and wires their hierarchical pins. The named nets in the main sheet (e.g. /dc788767.../JTAG_TCK) confirm cross-sheet connectivity is present. The false positive arises because the per-sheet analyzer cannot track connections that pass through the top-level parent sheet.
  (hierarchical_labels)

### Missed
- U3 (93LC56B, Memory_EEPROM:93LCxxBxxOT) is the FT2232HL configuration EEPROM connected via Microwire/SPI. The memory_interfaces and spi_buses detectors both return empty lists. The 93LC56B is a well-known EEPROM part (standard KiCad library symbol) and its presence alongside the FT2232HL is a standard design pattern. The net names for CS/SK/DI/DO are unnamed in the sub-sheet, which may prevent detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002075: 4-layer board correctly identified with GND plane on In1.Cu and power planes on In2.Cu; Courtyard overlaps between U2 (FT2232HL) and neighboring components correctly detected

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_ftdi-jtag-programmer_JTAGProgrammer_JTAGProgrammer.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies the 4-layer stackup (F.Cu, In1.Cu, In2.Cu, B.Cu) and finds the GND fill zone on In1.Cu and multiple power plane fills on In2.Cu (+3V3, +2V5, VIO_JTAG, VIO_UART, VBUS_FILT). This is a proper USB signal-integrity stackup with a continuous ground reference adjacent to the outer copper layers.
- The analyzer identifies three courtyard overlaps all involving U2 (FT2232HL): U5/U2 (1.89mm²), C18/U2 (1.394mm²), R20/U2 (0.454mm²). These represent tightly-packed decoupling capacitors and buffer ICs near the 64-LQFP FT2232HL, consistent with a high-density SMD layout. The overlaps are real DRC-flaggable issues, correctly reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
