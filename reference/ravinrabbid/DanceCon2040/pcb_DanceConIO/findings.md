# Findings: ravinrabbid/DanceCon2040 / pcb_DanceConIO

## FND-00000136: Dance pad controller with RP2040 and 3x ADS124S06 precision ADCs: excellent RC filter detection for ADC input conditioning, but missing SPI bus and ADC reference circuit analysis

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/DanceCon2040/pcb/DanceConIO/DanceConIO.kicad_sch
- **Created**: 2026-03-14

### Correct
- RC anti-aliasing filters correctly detected on ADC inputs: 150-ohm series resistors with 22nF differential and 2.2nF common-mode capacitors giving ~48kHz and ~482kHz cutoffs
- Voltage reference dividers for ADC detected: 100k/150-ohm dividers on REFP/REFN pins of ADS124S06 ADCs
- Level translator SN74LVC1T45DCK identified for signal level conversion
- I2C bus detected with SDA/SCL lines (though missing pull-ups flagged correctly)
- 45 RC filter instances detected - reflects the multi-channel ADC input conditioning network accurately

### Incorrect
(none)

### Missed
- SPI bus connecting RP2040 to three ADS124S06 precision ADCs not detected - these are the primary data interfaces
  (design_analysis.bus_analysis)
- ADS124S06 precision delta-sigma ADCs (24-bit) not classified as measurement/instrumentation components
  (signal_analysis)
- No power regulators detected despite the board needing regulated 3.3V and 5V for the RP2040 and ADCs
  (signal_analysis.power_regulators)
- USB interface for the RP2040-Zero module not detected (likely exposed through module pins)
  (design_analysis.differential_pairs)
- Load cell / force sensor application context not identified from the ADC input topology (multiple differential ADC channels with anti-aliasing)
  (signal_analysis)

### Suggestions
- Detect SPI connections to ADCs by matching SCLK/DIN/DOUT/CS pin patterns on ADC ICs
- Identify multi-channel precision ADC architectures as measurement/instrumentation systems
- Recognize that RP2040-Zero is a module and its power regulation is internal

---
