# Findings: mlab-modules/ACOMP01 / hw_sch_pcb_ACOMP01

## FND-00000342: Zener clamp D1 (BZV55C-5.6V) not detected in protection_devices; pwr_flag_warnings incorrectly reports +3V3 and GND lack PWR_FLAG; R1 and R2 with value 'DNF' not flagged as do-not-fit/unpopulated

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_ACOMP01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic contains two PWR_FLAG symbols (#FLG0101 at 250.19,25.4 and #FLG0102 at 250.19,38.1) connected in the +3V3/GND supply area. statistics.power_rails lists 'PWR_FLAG', confirming their presence. Despite this, pwr_flag_warnings fires for both +3V3 and GND saying they have no power_out or PWR_FLAG. The analyzer tracks the symbols but does not associate them with the adjacent +3V3/GND nets when issuing warnings.
  (pwr_flag_warnings)

### Missed
- D1 is a BZV55C-5.6V zener diode with its cathode (K, pin 1) on the +3V3 rail and anode (A, pin 2) on GND — a classic power-rail overvoltage clamp. signal_analysis.protection_devices is empty. The diode is correctly typed as 'diode' in components and bom but no protection circuit is inferred.
  (signal_analysis)
- R1 and R2 both have value='DNF' (Do Not Fit), a common schematic convention for components intentionally left unpopulated. The KiCad dnp attribute is not set, but the analyzer does not infer DNP status from value strings like 'DNF', 'DNP', or 'NF'. Both show dnp=false in bom and components, and statistics.dnp_parts=0. These are optional series resistors on the LVDS output lines (TLV_OUT+/- and LMH_OUT+/-).
  (statistics)

### Suggestions
(none)

---
