# Findings: eez-open/dib-mio-afe3 / EDA files_KiCad_EEZ DIB AFE3

## FND-00000201: EEZ DIB AFE3 analog front-end board with dual-channel input protection (fuses, relays, clamp circuits), MCP6004 comparators for window detection, OPA376 precision buffer, DG212 analog switches for range selection, 2N7002 MOSFETs, isolated power rails, and optocoupler isolation. Complex analog signal conditioning with 9 isolated power rails. Good opamp and transistor detection; no regulators found (power likely comes from backplane).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: EDA files_KiCad_EEZ DIB AFE3.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 5 opamp circuits correctly identified: IC5 units 1-4 (MCP6004) as comparators for HI_CLAMP/LO_CLAMP window detection, IC7 (OPA376) as unity-gain buffer
- IC7 (OPA376) correctly identified as buffer configuration with gain=1.0 (inverting tied to output)
- IC5 unit 4 correctly identified as comparator with LO_CLAMP on non-inverting and IN4P on inverting
- IC5 unit 3 correctly identified as comparator with HI_CLAMP on non-inverting and IN4P on inverting
- Voltage divider R25/R24 (330R/10K) from -2V5_ISO to GND generating LO_CLAMP reference, ratio=0.968
- Voltage divider R22/R23 (330R/10K) from +2V5_ISO to GND generating HI_CLAMP reference, ratio=0.968
- Voltage divider R20/R13 (100K/100K) correctly detected with ratio=0.5 feeding IN3N
- Q1 and Q2 (2N7002) NMOS transistors correctly identified as switches driven by IC6 (DG212) analog switch
- 9 isolated power rails correctly identified: +15V_ISO, -15V_ISO, +5V_ISO, -5V_ISO, +3V3_ISO, +2V5_ISO, -2V5_ISO, GND, PWR_FLAG
- 3 relays, 4 fuses, 11 diodes, 2 optocouplers correctly classified - consistent with multi-range protected AFE
- RC networks R5/C1 and R6/C1 (10R/8n2, fc=1.94MHz) correctly detected as input EMI filters
- Decoupling on +2V5_ISO (1.2uF across 3 caps) and +3V3_ISO (1.2uF across 3 caps) correctly tallied

### Incorrect
- Design observation for IC6 (DG212) decoupling is repeated 4 times (once per unit) claiming +15V_ISO rail missing caps; should be deduplicated to one observation per component
  (signal_analysis.design_observations)

### Missed
- No isolation_barriers detected despite OK2 optocouplers and isolated power domains (_ISO suffix rails). The optocouplers provide galvanic isolation between measurement and digital domains.
  (signal_analysis.isolation_barriers)
- No power_regulators detected. While power may come from backplane, the isolated DC-DC converters (if present on other sheets) or the power rail structure suggests power regulation should be noted.
  (signal_analysis.power_regulators)

### Suggestions
- Deduplicate per-unit design observations for multi-unit ICs - DG212 has 4 identical switch units but the decoupling warning should appear only once
- Detect isolated power domains from _ISO suffix naming convention and flag optocouplers as isolation barriers
- Consider adding relay detection as a signal analysis category for instrumentation/measurement front-ends

---
