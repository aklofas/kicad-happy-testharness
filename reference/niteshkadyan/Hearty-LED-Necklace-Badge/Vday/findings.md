# Findings: niteshkadyan/Hearty-LED-Necklace-Badge / Vday

## FND-00000593: Component counts and LED array correctly parsed from KiCad 5 legacy format; LDO regulator input/output rails both shown as unnamed nets; SPI bus with 74HC595 shift registers correctly detected; Vol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Vday_Vday.sch.json
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
