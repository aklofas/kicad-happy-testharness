# Findings: mlab-modules/AMUX01 / hw_sch_pcb_AMUX01

## FND-00000343: pwr_flag_warnings fires for GND and +3V3 despite both having PWR_FLAG symbols connected; D1 (BZV55C-5.6V Zener) not detected as a protection device

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_AMUX01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic has two power:PWR_FLAG symbols: one connected to the GND net (at 246.38,38.1 via wire to junction at 246.38,36.83) and one to the +3V3 net (at 246.38,25.4 via wire to junction at 246.38,26.67). The analyzer lists both PWR_FLAG symbols under a separate 'PWR_FLAG' power net entry in power_symbols rather than resolving them to their connected rails, then incorrectly warns that GND and +3V3 each lack a power_out driver or PWR_FLAG. Both warnings are false positives.
  (pwr_flag_warnings)

### Missed
- D1 is a Zener diode (BZV55C-5.6V, SMA package) with its cathode on the +3V3 rail and anode on GND. This is a standard overvoltage/reverse-polarity protection clamp for the power supply — especially relevant because the MAX4734 is rated for 1.6V–3.6V supply and D1 clamps overvoltage at 5.6V. The signal_analysis.protection_devices list is empty; D1 should be identified as a power supply protection device.
  (signal_analysis)

### Suggestions
(none)

---
