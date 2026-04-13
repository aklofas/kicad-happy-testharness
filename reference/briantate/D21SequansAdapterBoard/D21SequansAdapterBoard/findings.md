# Findings: briantate/D21SequansAdapterBoard / D21SequansAdapterBoard

## FND-00000447: Component inventory (22 total, all types) correctly identified; All 4 NPN LED driver circuits correctly detected with proper component mappings; Net connectivity for named signal nets correctly tra...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: D21SequansAdapterBoard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly counts 22 components: 4 LEDs (D1–D4), 8 resistors (R1–R8 with correct 1k/100Ω split), 4 NPN transistors Q1–Q4 (MMBT3904, SOT-23), and 6 connectors (J1–J6). All component types, values, footprints, and BOM groupings match the schematic source exactly.
- The transistor_circuits detector correctly identifies 4 common-emitter NPN LED driver stages: Q1 (base_res=R5/100Ω, collector_res=R1/1k, LED=D1), Q2 (base_res=R6/100Ω, collector_res=R2/1k, LED=D2), Q3 (base_res=R7/100Ω, collector_res=R3/1k, LED=D3), Q4 (base_res=R8/100Ω, collector_res=R4/1k, LED=D4). All emitters are correctly identified as GND, all LED anodes correctly tied to +5V. Base control nets (LED0→R5→Q1, LED1→R6→Q2, LED2→R7→Q3, LED3→R8→Q4) match the schematic.
- All named signal nets are correctly resolved: TX0/TX1 (J1↔J3/J5), RX0/RX1 (J1↔J3/J4/J5/J6), RTS0/RTS1, CTS0/CTS1, 5G_RESET_N (J2↔J3/J5), RING0 (J1↔J4/J6), DEBUG_TX/DEBUG_RX (J4↔J6), CRYPTO_I2C_SCL/SDA (J4↔J6), and LED0–LED3 control nets. The adapter board's pass-through routing between the two MCU connectors is correctly captured.
- All four power rails are correctly identified. The two +1.8V_MCU power symbols correctly use the Value property override (lib_id='power:+3.3V' but Value='+1.8V_MCU') — the analyzer reads the Value property and reports the net name correctly as +1.8V_MCU. No components are misassigned to wrong power rails.
- design_analysis.bus_analysis.uart correctly identifies TX0, TX1, RX0, RX1, DEBUG_TX, DEBUG_RX as UART signals. All are pass-through connector signals, and the detector handles these correctly. The companion flow control signals RTS0, RTS1, CTS0, CTS1 are present in the nets but not included in the uart list — which is acceptable since they are categorized as 'signal' rather than 'data' in net_classification.
- ground_domains correctly shows a single 'signal' domain for GND with 26 connections across Q1, Q2, Q3, Q4, J1, J2, J3, J4, J5, J6. No false isolated ground domains, no multiple-domain false positives. The ground net has 10 unique components contributing pins.
- test_coverage.debug_connectors correctly lists J1, J3, J4, J5, J6 as UART-interfaced debug connectors. J2 (the Sequans NEKTAR connector) is correctly excluded as it lacks any UART-named signals. The uncovered_key_nets list correctly flags +5V, +1.8V_MCU, +3.3V, 5G_RESET_N, TX0, TX1, RX0, RX1, CRYPTO_I2C_SDA, CRYPTO_I2C_SCL, DEBUG_RX, DEBUG_TX as lacking test points.
- statistics.total_no_connects=53 and statistics.total_nets=110 match the actual net dictionary length (110). The large no-connect count is expected: J2 (40-pin) has many unused pins routed through the Sequans module, and J1 (36-pin) also has many unconnected adapter lines. The 110 named/unnamed net split (22 named, 88 unnamed) is consistent with the design: many J2 pass-through lines lack net labels.
- assembly_complexity correctly reports 22 SMD, 0 THT, score=35/100, with 12× 0603 passives, 4× SOT-23 transistors, 6× connector footprints. The 'hand assembly feasible' observation is appropriate for this simple adapter.

### Incorrect
- The schematic has 4 PWR_FLAG instances: #FLG03 wired to GND at (21.59,24.13), #FLG01 wired to +5V at (36.83,21.59), #FLG02 wired to +3.3V at (67.31,21.59), #FLG04 wired to +3.3V at (97.79,21.59). The analyzer incorrectly raises pwr_flag_warnings for GND, +5V, and +3.3V. The root cause is that all 4 PWR_FLAG power symbols are reported with net_name='PWR_FLAG' rather than being resolved to the net they are wired to. As a result their power_out pins do not appear in the GND/+5V/+3.3V net entries, and the pwr_flag checker falsely concludes these nets lack a PWR_FLAG. Only the warning for +1.8V_MCU is correct (it genuinely has no PWR_FLAG).
  (signal_analysis)
- statistics.power_rails includes 'PWR_FLAG' as a fifth power rail alongside +1.8V_MCU, +3.3V, +5V, and GND. This is incorrect — PWR_FLAG is a marker component (power:PWR_FLAG), not a supply rail. There is no net named 'PWR_FLAG' in the nets dictionary, making this an inconsistency: the power_rails list contains an entry with no corresponding net. The real power rails are exactly 4: +1.8V_MCU, +3.3V, +5V, GND.
  (signal_analysis)
- The bus topology section reports: TX width=4 (actual: 2 signals TX0,TX1), RX width=4 (actual: 2), CTS width=4 (actual: 2 CTS0,CTS1), RTS width=4 (actual: 2 RTS0,RTS1), LED width=8 (actual: 4 signals LED0–LED3). Every bus width is exactly 2× the correct signal count. The range fields are correct (e.g. 'TX0..TX1'). This is a systematic doubling error in the width computation — likely counting connector-side duplicated instances (J3/J5 and J4/J6 mirror pairs) rather than counting unique signal names.
  (signal_analysis)

### Missed
- The design has two named I2C nets — CRYPTO_I2C_SCL and CRYPTO_I2C_SDA — both connected to J4 and J6 (pass-through connector pins). design_analysis.bus_analysis.i2c is empty []. By contrast, the UART detector correctly detects TX0, TX1, RX0, RX1, DEBUG_TX, DEBUG_RX even though they too are only on connector pins. The I2C detector appears to require actual IC devices (not connectors) on the SCL/SDA nets, creating an inconsistency with the UART detector. The net_classification section does classify CRYPTO_I2C_SCL as 'clock' and CRYPTO_I2C_SDA as 'data', but no I2C bus detection entry is generated.
  (signal_analysis)

### Suggestions
(none)

---
