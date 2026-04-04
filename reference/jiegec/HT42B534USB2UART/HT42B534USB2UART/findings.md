# Findings: HT42B534USB2UART / HT42B534USB2UART

## FND-00000582: kicad_version reports 'unknown' for a KiCad 6+ file; RC filter detection misclassifies USB 33Ω series termination resistors + ESD caps as low-pass filters; USB Full Speed protocol not detected in b...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HT42B534USB2UART.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 15 total components (1 IC, 7 caps, 3 connectors, 3 resistors, 1 LED) match the schematic. Net assignments for VDD, GND, VDDA, V33O, TX, RX, D+, D- are all correct.
- D+ / D- pair identified with R1 and R2 (33Ω each) as series resistors, shared on U1, has_esd: true (IC provides internal ESD). This is accurate.
- Net RX has U1 pin 4 (RX, input) and J2 pin 2 (passive). Connector passive pins don't count as drivers, so the no_driver warning is legitimate — the external device driving RX is not modeled in the schematic.

### Incorrect
- File version is 20230121 (KiCad 6/7 format) but the output has kicad_version: 'unknown'. The version string should be resolved to a human-readable KiCad version.
  (signal_analysis)
- R1/R2 (33Ω) with C6/C7 (47pF) on D-/D+ are flagged as low-pass RC filters at 102 MHz. These are USB FS series termination/ESD protection, not intentional RC filters. The 33Ω + 47pF combination is standard USB EMI suppression. Framing them as RC filters is misleading.
  (signal_analysis)
- Pin 3 (VDDIO) has pin_type 'input' in the lib symbol and appears in signal_pins. This pin is the IO ring power supply input, not a signal input. It should be treated as a power pin. This misclassification is inherited from the custom symbol definition where VDDIO is typed as 'input' rather than 'power_in'.
  (signal_analysis)

### Missed
- This is a USB-to-UART bridge (HT42B534) with USB D+/D- differential pair, series resistors, and ESD caps. The design_analysis.bus_analysis has no USB entry — only UART (TX/RX to J2) is detected. A USB FS interface should be identified.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000583: Component counts and LED array correctly parsed from KiCad 5 legacy format; LDO regulator input/output rails both shown as unnamed nets; SPI bus with 74HC595 shift registers correctly detected; Vol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: _home_aklofas_Projects_kicad-happy-testharness_repos_Hearty-LED-Necklace-Badge_Vday_Vday.sch.json
- **Created**: 2026-03-23

### Correct
- 173 total components including 131 LEDs, 7 ICs (ATmega328P, MCP73831, ULN2803A, 2x 74HC595, HM-11BLE, XC6210B332MR), 23 resistors, 6 caps correctly extracted from EESchema v2 format.
- SPI bus found with MISO/MOSI/SCK nets shared across U4 (74HC595), U5 (74HC595), and U1 (ATmega328P). This matches the design: ATmega drives two daisy-chained shift registers to control the LED matrix.
- Y1 (value 'Crystal_GND2') has no numeric frequency in the schematic fields, so frequency: null is the correct output. The crystal is a 2-pad ground-plane type symbol.

### Incorrect
- XC6210B332MR LDO reports input_rail: '__unnamed_100' and output_rail: '__unnamed_103', with those nets containing only the LDO's own pins. The schematic uses a power switch (SW2) and battery (Vbat) but the net topology is unresolved — likely a net tracing gap in the KiCad 5 legacy parser. The LDO's actual VIN comes from Vbat through SW2 but those connections appear disconnected in the output.
  (signal_analysis)
- The voltage divider (R22 10K / R23 20K to GND) reports top_net: 'D1'. This 'D1' is a net label connected to U1 pin (PCINT5/SCK)PB5, not a reference to LED D1. The net name collision between net labels and component references could mislead; the detected divider appears real but its purpose is unclear (possibly a resistor ladder on an ATmega ADC/GPIO pin).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
