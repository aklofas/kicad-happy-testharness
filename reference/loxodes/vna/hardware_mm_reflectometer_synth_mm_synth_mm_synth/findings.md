# Findings: vna / hardware_mm_reflectometer_synth_mm_synth_mm_synth

## FND-00000152: VNA RF output chain with ADRF5042 SP4T switch, ADRF5730 digital attenuator, MAAM-011109 amplifiers, LTC5596 power detector. RF chain detection completely fails due to narrow keyword lists.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_mm_reflectometer_rf_output_mm_rf_output.kicad_sch.json
- **Related**: KH-081, KH-085
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- SMA connectors treated as antennas by rf_matching detector -- SMA in RF test equipment are signal I/O ports, not antennas
  (signal_analysis.rf_matching)

### Missed
- RF chain with 7+ components (ADRF5042, ADRF5730, MAAM-011109 x2, ATS2012, LTC5596, FPC07181) returns empty rf_chains -- keywords miss ADRF/ADMV/MAAM families
  (signal_analysis.rf_chains)
- No attenuator category in RF chain detection -- ATS2012, ADRF5730, HMC424 are common RF attenuators with no detection category
  (signal_analysis.rf_chains)
- Component ki_description field not extracted from lib_symbols -- contains text like 'Wideband Amplifier 10 MHz - 40 GHz' that could enable description-based RF classification
  (components)
- PLL loop filter not detected -- R/C networks on LMX2592/LMX2820 CPout pins form classic passive loop filters detected only as individual rc_filters
  (signal_analysis.rc_filters)

### Suggestions
- Extract ki_description from lib_symbols for classification
- Add ADRF, ADMV, MAAM, HMC3xx to RF keyword lists
- Add attenuator/coupler/power_detector categories to detect_rf_chains
- SMA connectors should require ANT/AE ref prefix or antenna keyword to be treated as antennas

---
