# Findings: ravinrabbid/DonCon2040 / pcb_DonConIO

## FND-00000138: Taiko drum game controller with RP2040: voltage dividers over-detected from LED current limiting networks, good power rail identification with +/-12V for piezo amplification

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/DonCon2040/pcb/DonConIO/DonConIO.kicad_sch
- **Created**: 2026-03-14

### Correct
- Power rails correctly identified: +12V, -12V, +5V, +3V3, GND - bipolar supply for analog signal conditioning of piezo sensors
- RC low-pass filters detected at 3.39kHz - appropriate for piezo signal conditioning before ADC sampling
- 24 diodes detected - consistent with protection/clamping diodes on piezo sensor inputs
- PWR_FLAG net correctly listed as power rail

### Incorrect
- Nine voltage dividers detected but most are actually LED current limiting resistor networks with protection diodes, not signal voltage dividers. The 300/1k and 10k/1k combinations connected to diode cathodes (K) are LED drive circuits
  (signal_analysis.voltage_dividers)
- Voltage divider with R11 4.7k / R10 1M (ratio 0.995) is not meaningful as a divider - likely a bias/discharge network for piezo conditioning
  (signal_analysis.voltage_dividers)

### Missed
- Piezo sensor signal conditioning circuit not identified: the design uses op-amps or comparators with bipolar supply (+/-12V) to amplify and condition piezo drum hit signals
  (signal_analysis.opamp_circuits)
- No power regulators detected - the PS1 component and associated circuitry providing +/-12V rails from +5V should be identified
  (signal_analysis.power_regulators)
- LED indicator circuits for button feedback not classified as LED drive circuits
  (signal_analysis)
- USB interface for RP2040 not detected
  (design_analysis.differential_pairs)
- ADC input channels (Don_Right_ADC etc.) not linked to piezo sensor inputs
  (signal_analysis)

### Suggestions
- Filter voltage divider detection to exclude cases where mid-point connects only to diode cathodes (LED circuits)
- Detect bipolar power supplies (+V/-V pairs) as analog signal conditioning indicators
- Identify piezo/sensor conditioning circuits from the combination of protection diodes + RC filters + ADC inputs

---
