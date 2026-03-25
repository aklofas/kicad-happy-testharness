# Findings: jtcores / cores_wwfss_sch_wwfsstar

## ?: WWF Super Stars arcade PCB (Technos/JOTEGO reverse-engineering) with 68000 CPU, Z80 sound, YM2151/OKI6295 audio, 4x HA17558 opamps; massive varistor misclassification of 128 VIC/VR/V-prefix components (actually 74LS logic ICs and resistors) and false power rail detection of video timing counter signals

- **Status**: new
- **Analyzer**: schematic
- **Source**: cores_wwfss_sch_wwfsstar.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Correctly identified 333 unique components across 20 hierarchical sheets
- Detected 3 crystal circuits: X1 (3.579545 MHz color burst), X2 (1.05 MHz), X3 (20 MHz active oscillator)
- Detected 12 opamp circuit units from 4 HA17558 dual opamps including 7 buffer configurations and 1 transimpedance
- Detected 4 BF457 BJT transistor circuits (TR1-TR4) driving coin counter and lock solenoid outputs
- Detected 7 RC filters in the audio section with reasonable cutoff frequencies (1-10 kHz range)
- Correctly identified M51516L as a power regulator
- Correctly identified key ICs: 68000D CPU, Z80CPU, YM2151 FM synth, YM3012 DAC, OKI6295 ADPCM
- VJ1 and VJ2 (50-pin connectors with V prefix) correctly classified as connectors
- VC4-VC19 capacitors correctly classified as capacitors despite V prefix
- Detected VCC and VSS as power rails
- Detected 20 hierarchical sheets matching the actual referenced sheet hierarchy

### Incorrect
- 128 components classified as varistor are actually 74LS-series logic ICs, SRAMs, ROMs, and resistors. The VIC prefix (Video IC), VR prefix (Video Resistor), V prefix, and VU prefix are section-naming conventions in the original Technos arcade board schematics, not varistor designators. The analyzer should check lib_id (jt74:*, jt_rom:*, Device:R_US) not just the reference prefix
  (statistics.component_types)
- 128 false protection devices reported: all 128 'varistors' in protection_devices are actually misclassified 74LS ICs, SRAMs, and resistors, not actual protection circuits
  (signal_analysis.protection_devices)
- V1* through V128* signals (video vertical counter bits) misidentified as power rails. These are timing counter output nets in the timing sub-sheet, not power supply rails. No power symbols or PWR_FLAG are connected to these nets
  (statistics.power_rails)
- IC85 (BF457, lib_id=Transistor_BJT:BF457) classified as type 'ic' instead of 'transistor'. The IC prefix overrides the lib_id-based classification. Should be counted as a transistor since lib_id clearly indicates BJT
  (statistics.component_types)
- C61 value '25V' parsed as 25 pF capacitance (2.5e-11 F in decoupling analysis). The '25V' is a voltage rating, not a capacitance value. This causes incorrect decoupling analysis for the VCC rail
  (signal_analysis.decoupling_analysis)
- IC count of 95 is drastically undercounted because ~122 ICs with VIC/VU prefixes are misclassified as varistors. True IC count should be approximately 217
  (statistics.component_types)
- Resistor count of 33 is undercounted because 6 resistors with VR/V prefix (Device:R_US, 470 Ohm) are misclassified as varistors. True resistor count should be 39
  (statistics.component_types)

### Missed
- No memory_interfaces detected despite design having multiple RAM (RAM_2016/SRAM2K8B, 6 instances) and ROM (27C1000, 27C256, 24J series, TC534000AP) chips with address/data buses
  (signal_analysis.memory_interfaces)
- No buzzer_speaker_circuits detected despite SPEAKER_H and SPEAKER_L nets driving a speaker through M51516L power amplifier via opamp mixing stage
  (signal_analysis.buzzer_speaker_circuits)

### Suggestions
- Component type classification should prioritize lib_id over reference prefix. Components with lib_id containing '74LS', '74xx:', 'jt74:', 'jt_rom:', 'jt_ram:', 'CPU:', 'Transistor_BJT:' etc. should be classified based on the library, not the V/VIC/VR prefix. This is a common pattern in arcade board reverse-engineering where section prefixes (V=Video, S=Sound, etc.) are prepended to standard IC/R/C designators.
- Power rail detection should require connection to a power symbol (PWR_FLAG, power:VCC, etc.) or have a voltage-like name pattern. Net names like V1*, V4*, V8*, V128* following binary-weighted patterns are almost certainly counter bits, not power rails.
- The varistor classification heuristic based on 'V' prefix is too aggressive. Consider requiring lib_id to contain 'Varistor' or 'Device:Varistor' rather than inferring from the reference designator alone.
- C61 with value '25V' should be flagged as an unparseable capacitance value (voltage rating only) rather than silently converting to 25 pF.

---
