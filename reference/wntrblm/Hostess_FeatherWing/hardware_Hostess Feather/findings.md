# Findings: wntrblm/Hostess_FeatherWing / hardware_Hostess Feather

## FND-00000604: Component extraction, subcircuits, crystal circuit with load caps all correct; Crystal Y1 frequency not extracted from MPN (ABS06-32.768KHz-1-T); ESD protection on USB D+/D- falsely credited to U1 ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_Hostess Feather.sch.json
- **Created**: 2026-03-23

### Correct
- All 28 components across 7 types correctly parsed from legacy KiCad 5 .sch. Crystal Y1 load cap analysis (C5/C6 22 pF, effective 14 pF) is correct. Differential pair D+/D- detection correct. VBUS_FILTERED decoupling (100 uF + 100 nF) correctly identified.
- The XOUT global label at schematic Y=3150 mils (80.01 mm) connects to U1 pin 40 (~RESET, input type) and Y1 pin 2 + C6 (passive). The coordinate match is exact. Since no bidirectional or output pin drives this net, the no_driver ERC warning is structurally correct. The naming ('XOUT' for the RESET net) appears to be a schematic design issue in the source.

### Incorrect
- The differential_pairs entry reports has_esd=True with esd_protection=['U1']. U1 is the MCU itself, not a dedicated ESD protection device. The design_observations also correctly flags has_esd_protection=False for the D+ net. These two outputs contradict each other. The correct answer is: no dedicated ESD device is present; the MCU's internal clamps do not qualify.
  (signal_analysis)
- The analyzer flags needs_level_shifter=True for FAULT and VBUSEN because U1 (ATSAMD21, +3V3) and U2 (TPS2051, VBUS_FILTERED ~5V) share these nets with different power domains. However, the TPS2051's FAULT pin is open-drain and its EN pin accepts 3.3V logic at 5V VBUS operation; no level shifter is needed. The cross-domain detection is architecturally correct but the level-shifter flag is wrong for this device class.
  (signal_analysis)

### Missed
- Y1 has value 'Crystal' (generic) and MPN 'ABS06-32.768KHz-1-T', which encodes the 32.768 kHz frequency. The analyzer sets frequency=null because it only parses the value field for numeric frequency. The MPN field contains the frequency unambiguously. The load caps (22 pF) are correct for a 32.768 kHz watch crystal.
  (signal_analysis)

### Suggestions
(none)

---
