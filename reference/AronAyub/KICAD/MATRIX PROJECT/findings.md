# Findings: AronAyub/KICAD / MATRIX PROJECT_MATRIX PROJECT

## FND-00002545: LED matrix display driver with ATmega328PB-AU, five 74HC595 shift registers, eight 2N3055 power transistors for row driving, L78L05 voltage regulator, and a Bluetooth serial module. Analyzer correctly identified the core architecture including transistor circuits and voltage divider for level shifting.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: MATRIX PROJECT_MATRIX PROJECT.sch.json

### Correct
- ATmega328PB-AU (U6) correctly identified as the main MCU IC
- Five 74HC595 shift registers (U1-U5) correctly identified as ICs driving column data
- Eight 2N3055 BJT transistors (Q1-Q8) correctly detected as transistor_circuits with base/collector/emitter nets
- L78L05 (U7) correctly detected as LDO regulator with input_rail=VIN
- Voltage divider R42/R41 (1K/2K) at ratio 0.667 on TX net correctly detected - this is a 5V-to-3.3V level shifter for the Bluetooth module (J6)
- Crystal Y1 with 22pF load caps C1 and C2 giving effective 14pF load correctly detected
- Decoupling analysis shows +5V rail with C6 (10uF) and VIN rail with C3 (10uF) correctly
- 43 resistors (R1-R43) correctly classified - 40x 220 ohm current-limiting resistors for LED columns plus control resistors
- 10 connectors (J1-J10) correctly classified including JST_EH 8-pin for LED rows (J1-J5) and BT sensor (J6)

### Incorrect
- Q1 transistor base_net=GND is incorrect. Q1 base connects to a shift register output (P8 net area), not to GND. The analyzer appears to have confused the global GND net with the transistor's actual base connection
  (signal_analysis.transistor_circuits)
- Q7 and Q8 transistors also show base_net=GND which is incorrect for the same reason
  (signal_analysis.transistor_circuits)
- Q4 shows collector_net=QA and emitter_net=GND with emitter_is_ground=true, but Q2/Q3/Q5/Q6 show base=collector (e.g. Q2 base_net=P7, collector_net=P7) which indicates a pin mapping error - the base and collector pins are being conflated
  (signal_analysis.transistor_circuits)
- U7 output_rail detected as '12_5_S' which is an unusual net name. This appears to be the regulated 5V output rail name in the schematic, but the net name is confusing and may indicate a parsing issue with the original schematic's net naming
  (signal_analysis.power_regulators)
- Regulator caps observation says missing output cap for U7 on '12_5_S' rail, but C5 (100nF) or C4 may be on that rail - need to verify if the analyzer is correctly tracing the output net
  (signal_analysis.design_observations)

### Missed
- LED matrix topology not detected. The design is an 8x40 LED matrix (5 shift registers x 8 outputs = 40 columns, 8 transistor-driven rows) with multiplexed scanning. This is a key_matrices variant for LED displays
  (signal_analysis.key_matrices)
- SPI daisy-chain of 74HC595 shift registers (U1->U2->U3->U4->U5 via QH'->SER) not detected as a bus protocol
  (signal_analysis.design_observations)

### Suggestions
- Fix BJT pin mapping for 2N3055 - the base/collector/emitter detection has errors where base=GND or base=collector
- Consider detecting LED matrix displays as a variant of key_matrices (output matrices vs input matrices)
- Detect 74HC595 daisy-chains as a shift register bus pattern

---
