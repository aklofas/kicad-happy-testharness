# Findings: 1590A / Base_Buffered_Buffered

## FND-00000309: PWR_FLAG symbols not resolved to their connected power nets; pwr_flag_warnings false positive for GND: PWR_FLAG is present but not recognized; LED net classified as 'output_drive' despite having on...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Effect_DaisySeed_DaisySeed.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Two PWR_FLAG symbols exist: #FLG01 at (39.37, 41.91) is on the VIN net (connected via wire to the VIN global label at 45.72/41.91), and #FLG02 at (39.37, 49.53) is on the GND net (connected via wire to the GND symbol at 48.26/49.53). The analyzer assigns net_name 'PWR_FLAG' to both, treating them as a separate power rail rather than recognizing they are on GND and VIN. This causes: (1) 'PWR_FLAG' appears spuriously as a power_rail in statistics.power_rails, (2) pwr_flag_warnings incorrectly fires for GND claiming it has no PWR_FLAG, (3) power_symbols lists two entries with net_name 'PWR_FLAG' instead of 'GND' and 'VIN'.
  (statistics)
- The pwr_flag_warnings section flags GND as missing a PWR_FLAG: 'Power rail GND has power_in pins but no power_out or PWR_FLAG'. However, #FLG02 (power:PWR_FLAG) is physically wired to GND via the wire at y=49.53 (connecting 39.37/49.53 to the GND symbol at 48.26/49.53). The bug is that the analyzer resolves the PWR_FLAG net as 'PWR_FLAG' instead of 'GND', so it never counts the flag as being on GND.
  (pwr_flag_warnings)
- In design_analysis.net_classification, the LED net is classified as 'output_drive'. The LED net has only two pins: U1.29 (LED_1, pin_type=input) and J3.1 (Pin_1, pin_type=passive). There is no output driver on this net in the schematic — the transistor buffer is on the base board. The classification 'output_drive' appears to be based on the net name 'LED' rather than actual pin types, which is inconsistent with the simultaneously reported ERC no_driver warning for this same net.
  (design_analysis)

### Missed
- U1 pin 38 is named '+3V3_D' with pin_type 'power_out' — it is a regulated 3.3V digital output rail from the Daisy Seed's internal regulator. It appears as net '__unnamed_15' (a single-pin unnamed net, no_connect implied). The power_domains.ic_power_rails for U1 lists only ['+3V3_A', 'VIN'] and domain_groups has only '+3V3_A' and 'VIN'. The +3V3_D output rail is entirely absent from power domain tracking, which is a missed rail for a module that exposes two distinct 3.3V rails (+3V3_A analog and +3V3_D digital).
  (design_analysis)
- The subcircuits entry for U1 lists neighbor_components as J2, J3, and J6. J7 (the power input connector) is also electrically connected to U1 via the VIN net (U1.39/V_IN connects to J7.1 and J7.2) and GND net (J7.3 and J7.4 go to GND which also connects to U1.20 and U1.40). J7 should be included as a neighbor of U1 in the subcircuit since it is the power supply connector for the module.
  (subcircuits)

### Suggestions
- Fix: LED net classified as 'output_drive' despite having only input and passive pins

---
