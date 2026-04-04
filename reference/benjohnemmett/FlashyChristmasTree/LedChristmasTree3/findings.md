# Findings: FlashyChristmasTree / LedChristmasTree3

## FND-00000552: Component count and BOM extraction accurate; Net topology and pin connectivity correct; RC low-pass filter false positive — this is a 555 astable timing network; PWR net classified as 'signal' inst...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LedChristmasTree3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 16 components (2R, 9LED, 1BAT, 2C, 2IC) correctly identified. BOM grouped correctly. All refs present.
- PWR, GND, CLK, led_1..led_8 nets all correctly mapped. 4017 Q0-Q7 outputs to LEDs D2-D9 correctly traced. CLK net between NE555 pin 3 and 4017 pin 14 correct.

### Incorrect
- R13 (5k1) + C3 (10u) detected as a 3.12 Hz low-pass RC filter. In reality these are the timing components for the NE555P astable oscillator (C3 connected to TR/THR pins 2+6, R13 in timing path). Should be classified as oscillator/timer circuit, not a signal filter.
  (signal_analysis)
- net_classification shows 'PWR': 'signal' but this is the main supply rail from BT1 (battery). The net uses a label named PWR rather than a VCC power symbol, so the analyzer treats it as a signal net. Should be classified as a power rail.
  (signal_analysis)
- erc_warnings reports 'Net PWR has input pins but no output driver' but BT1 (battery) with passive pins IS the driver. The analyzer cannot recognize battery passive pins as a power source, generating a spurious ERC warning.
  (signal_analysis)

### Missed
- U1 pins 9 (Q8), 11 (Q9), and 12 (Cout) are connected only to single-pin unnamed nets (__unnamed_3, __unnamed_4, __unnamed_5) with no other connections. These should appear in connectivity_issues.unconnected_pins or single_pin_nets but both arrays are empty.
  (signal_analysis)
- The NE555P is wired as a classic astable oscillator (pins 2+6 shorted to RC timing network, pin 7 DIS to resistor junction, output on pin 3 drives CLK). No oscillator or clock_generator entry appears in signal_analysis. The 555 timer astable configuration is a common, detectable pattern.
  (signal_analysis)
- D2-D9 anodes connect directly to 4017 Q-outputs (no series resistors), with cathodes to GND. There is only one resistor (R12, 2k7) in the PWR domain, not on LED paths. The analyzer does not flag the missing LED current-limiting resistors, which is a real design concern.
  (signal_analysis)

### Suggestions
(none)

---
