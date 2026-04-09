# Findings: GuitarML/FunBox / hardware_funbox_v2_midi_funbox_v2

## ?: Guitar effects pedal platform (FunBox v2) with Electrosmith Daisy Seed DSP module (A1), stereo audio I/O through TL074 quad op-amp buffer, L7805 5V regulator, H11L1 optocoupler for MIDI input. Very similar to v3 but uses TL074 instead of MCP6024 and has no MCP6002 expression buffer. Accurate analysis.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_funbox_v2_midi_funbox_v2.kicad_sch.json

### Correct
- Three voltage dividers (R5/R6, R7/R10, R11/R12 all 1M/1M) correctly detected as virtual ground generators (VCC/2) feeding U1 (TL074) non-inverting inputs for audio biasing
- Two anti-aliasing RC low-pass filters R2/C4 and R1/C3 (3.3k/2.2nF at 21.92 kHz) correctly detected on audio output paths
- Four op-amp buffer circuits correctly identified: U1 units 1-4 (TL074) all in buffer configuration with gain=1.0
- U2 (L7805) correctly detected as LDO regulator with input=VCC, output=5V
- A1 (Electrosmith_Daisy_Seed_Rev7) correctly classified as IC (DSP module)
- D1 (1N5817) reverse polarity protection and D2 (1N4148) correctly classified as diodes
- U5 (H11L1 optocoupler) correctly classified as IC for MIDI input isolation
- 65 total components: 4 ICs, 11 connectors, 22 resistors, 18 capacitors, 6 switches, 2 LEDs, 2 diodes
- Design observation correctly flags missing VCC decoupling and L7805 input/output caps

### Incorrect
(none)

### Missed
- H11L1 (U5) optocoupler not detected as an isolation_barrier for MIDI input galvanic isolation.
  (signal_analysis.isolation_barriers)

### Suggestions
- Optocoupler ICs (H11L1, 6N138, etc.) should be detected as isolation barriers.

---

## FND-00002524: Stereo guitar effects pedal based on Electrosmith Daisy Seed with TL074 quad op-amp audio buffering, L7805 5V regulator, MIDI I/O via H11L1 optocoupler. The analyzer correctly identifies the L7805 regulator, three of four bias voltage dividers, two RC anti-aliasing filters, four op-amp buffer configurations, and LED circuits. However, it misses a fourth voltage divider (R13/R14), the MIDI optocoupler isolation barrier, D1 reverse polarity protection, audio input AC coupling caps, and the MIDI UART bus. It misclassifies the L7805 as LDO, falsely claims missing regulator caps, misclassifies 5V and 3V3_A as signals not power rails, and includes U1 power unit in opamp_circuits.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_funbox_v2_midi_funbox_v2.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- U2 (L7805) correctly identified as a linear regulator with VCC input rail and 5V output rail
- Voltage divider R5 (1M) / R6 (1M) from 5V to GND with 0.5 ratio feeding U1 pin 12 (unit 4 non-inverting input) and C12 bypass
- Voltage divider R7 (1M) / R10 (1M) from 5V to GND with 0.5 ratio feeding U1 pin 5 (unit 2 non-inverting input) and C13 bypass
- Voltage divider R11 (1M) / R12 (1M) from 5V to GND with 0.5 ratio feeding U1 pin 10 (unit 3 non-inverting input) and C14, R3
- RC low-pass filter R2 (3K3) + C4 (2.2nF) on AUDIO_OUT_BUFFER_LEFT with correct cutoff of 21.92 kHz (anti-aliasing)
- RC low-pass filter R1 (3K3) + C3 (2.2nF) on AUDIO_OUT_BUFFER_RIGHT with correct cutoff of 21.92 kHz (anti-aliasing)
- U1 unit 1 (TL074) correctly identified as buffer on AUDIO_IN_BUFFER_LEFT
- U1 unit 3 (TL074) correctly identified as buffer on AUDIO_IN_BUFFER_RIGHT
- U1 unit 2 (TL074) correctly identified as buffer with R16 (100 ohms) - left output buffer
- U1 unit 4 (TL074) correctly identified as buffer with R15 (100 ohms) - right output buffer
- LED1 and LED2 correctly identified with 1K series resistors (R20, R19) driven from A1 (Daisy Seed)
- Duplicate reference POT4 correctly flagged in annotation_issues
- Title block correctly extracted: FunBox by GuitarML, dated 2024-04-30
- Component count of 65 total with correct type breakdown (4 ICs, 22 resistors, 18 capacitors, 2 diodes, 2 LEDs, 6 switches, 11 connectors)
- Power sequencing correctly identifies 5V rail from U2 regulator as always-on
- Single-pin net warning for 3V3_D (A1 pin 38) is correct - unused digital 3.3V output
- ESD coverage audit correctly identifies MIDI IN/OUT jacks (J4, J5) as having no ESD protection

### Incorrect
- U2 (L7805) topology labeled as 'LDO' but the L7805 is a classic fixed linear regulator (~2V dropout), not a low-dropout regulator
  (signal_analysis.power_regulators)
- Design observation claims missing regulator input/output caps for U2, but C6 (100uF), C7/C8 (100nF) are on VCC input and C9/C10 (100nF) are on 5V output
  (signal_analysis.design_observations)
- Net classification marks '5V' as 'signal' when it is clearly a power rail (output of L7805). Similarly '3V3_A' classified as 'signal' but is a 3.3V analog power rail
  (design_analysis.net_classification)
- U1 unit 5 (power pins V+/V-) listed as opamp_circuit with configuration 'unknown' - this is the power supply unit, not a signal circuit
  (signal_analysis.opamp_circuits)
- All 6 potentiometer instances reported as POT4 with identical net connections (GND, 3V3_A, POT_6) due to schematic annotation bug propagated without flagging different actual connections per instance
  (components)
- ESD coverage audit lists POT4 as a connector 6 times with identical signal nets, creating redundant entries from the duplicate reference
  (signal_analysis.esd_coverage_audit)
- BOM groups R15 (100 ohm resistor) together with C1/C2 (100pF capacitors) under the same '100' value label, creating ambiguity
  (bom)

### Missed
- Fourth voltage divider R13 (1M) / R14 (1M) from 5V to GND biasing U1 pin 3 (unit 1 non-inverting input) was not detected. Identical topology to the three detected dividers
  (signal_analysis.voltage_dividers)
- MIDI input isolation barrier via U5 (H11L1 optocoupler) not detected. Provides galvanic isolation between MIDI input jack and Daisy Seed UART RX with D2 (1N4148) protection, R30 (220R) current limiting, R31 (470R) pull-up, R32 (10R) output
  (signal_analysis.isolation_barriers)
- D1 (1N5817 Schottky diode) reverse polarity protection in power input path not detected. Standard guitar pedal power protection circuit
  (signal_analysis.protection_devices)
- MIDI interface not detected as UART bus. A1 pins connected to MIDI_OUT and MIDI_IN through MIDI I/O circuitry. Standard MIDI uses 31.25 kbaud UART
  (design_analysis.bus_analysis.uart)
- Audio input AC coupling capacitors C1 and C2 (100pF) not detected as part of audio signal chain
  (signal_analysis.audio_circuits)
- Complete audio signal chain (input jack -> AC coupling -> bias resistor -> buffer -> Daisy Seed -> RC filter -> output buffer -> output jack) not characterized as audio_circuit
  (signal_analysis.audio_circuits)
- Decoupling capacitor C30 (100nF) on 3V3_A rail near U5 not identified in decoupling_analysis
  (signal_analysis.decoupling_analysis)
- I2C bus detected but Daisy Seed I2C pins are not connected to external devices - should note unused bus or not report it
  (design_analysis.bus_analysis.i2c)

### Suggestions
- L7805 should not be classified as 'LDO' - ~2V dropout is distinctly different from true LDOs (<500mV)
- Regulator cap analysis should trace caps on the same power net, not just directly adjacent to the IC
- 5V rail (L7805 output) should be classified as power rail, not signal. Any regulator output with multiple consumers is power
- Detect optocouplers (H11L1, 6N137, etc.) as isolation barriers, especially in MIDI circuits
- 1N5817 Schottky in series with power input should be detected as reverse polarity protection
- MIDI uses UART at 31.25 kbaud - detect when MIDI jacks connected to UART pins
- Potentiometer duplicate reference causes cascading data quality issues - add higher severity warning

---
