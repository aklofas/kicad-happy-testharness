# Findings: AugustoS97/BMS-BatterySystem / Diseno-Electronico_CAN2Serial

## FND-00000403: Component counts correct (38 real components); SPI bus not detected despite MOSI/MISO/SCK/SS_MCP nets present; U2 (MCP2515) and U4 (TJA1050T) have systematically wrong pin-to-net assignments; desig...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Diseno-Electronico_CAN2Serial_CAN2Serial.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies 38 non-power components: 4 ICs, 2 crystals, 13 capacitors, 7 resistors, 6 connectors, 2 jumpers, 4 mounting holes. Counts match source schematic exactly.

### Incorrect
- U2 MCP2515 pin assignments are incorrectly mapped: the GND net receives pin 18 (VDD) instead of VSS, +5V net receives pin 9 (VSS) instead of VDD, RXCAN net maps to pin 17 (~RESET) instead of pin 2 (RXCAN), SCK net maps to pin 8 (OSC1) instead of pin 13 (SCK), SS_MCP maps to pin 3 (CLKOUT/SOF) instead of pin 16 (~CS), TXCAN maps to pin 6 (~TX2RTS) instead of pin 1 (TXCAN). For U4 (TJA1050T from custom CAN2Serial library): GND has pin 1 (TXD) and pin 3 (VCC), +5V has pin 2 (GND), CANH net has pin 6 named 'CANL' and CANL net has pin 7 named 'CANH'. These are pin coordinate resolution errors for components whose library pins do not match the expected absolute positions after applying the component placement transform.
  (nets)
- The single_pin_nets observation flags U2 pin '~RESET' on net RXCAN as an isolated connection. This is a secondary consequence of the pin coordinate mismatch: the RXCAN net label actually connects to MCP2515 pin 2 (RXCAN), but the analyzer incorrectly maps it to pin 17 (~RESET). Because pin 2 (RXCAN) ends up on an unnamed net, MCP2515's actual RXCAN pin appears unconnected and the RXCAN net appears to have only the ~RESET pin — both observations are artifacts of the mis-mapping.
  (signal_analysis)

### Missed
- The schematic connects ATmega328P (U1) to MCP2515 (U2) via SPI: MOSI, MISO, SCK, and SS_MCP nets are all present and named. The memory_interfaces (or equivalent SPI bus detector) reports no SPI bus detected. The MOSI/MISO nets also partially fail to include U2 pins due to the pin coordinate mismatch described separately.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000404: Component counts correct (46 real components); Crystal circuits not detected despite two crystals (Y1 8MHz, Y2 16MHz) with load caps; 4 RC filters detected that are actually crystal load resistor-c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Diseno-Electronico_EPSolar-CAN_EPSolar-CAN.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies 46 non-power components: 5 ICs (ATmega328P, MCP2515, TJA1050T, MAX485E, MP2307), 2 crystals, 10 capacitors, 15 resistors, 5 connectors, 3 jumpers, 4 mounting holes, 1 LED, 1 fuse. Counts match source schematic exactly.

### Incorrect
- The analyzer detects 4 low-pass RC filters: R4+C6, R4+C5, R1+C3, R1+C4 (all using 1M ohm resistors with 22pF capacitors, cutoff 7.23 kHz). These are crystal bias resistors bridging the two crystal pins with load capacitors to ground — the standard HC-49 crystal oscillator circuit. They should be classified as crystal circuits, not RC filters. This is a direct consequence of crystal_circuits being empty: the 1M resistors and 22pF caps are freed up for RC filter matching.
  (signal_analysis)
- The analyzer reports a voltage divider with R_top=R13(120R)+R14(20k) chained in series from +5V, R_bottom=R15(20k) to GND, mid_net='B', ratio=0.499. In reality these three resistors form the RS-485 bias and termination network on the MAX485E: R13(120R) is the differential line termination between lines A and B, R14(20k) is a pull-up on B to +5V, and R15(20k) is a pull-down on A to GND. The chained-resistor voltage divider detector is treating the termination resistor and bias pull-up as a series R_top, which is a misclassification of RS-485 biasing as a general-purpose voltage divider.
  (signal_analysis)

### Missed
- EPSolar-CAN.sch contains Y1 (8MHz) and Y2 (16MHz), each with two 22pF load capacitors (C3/C4 and C5/C6) and a 1M bias resistor (R1, R4) — identical topology to CAN2Serial.sch where the analyzer correctly detects two crystal circuits. In EPSolar the crystals use a 'EPSolar-CAN-rescue' library prefix; their pins are empty in the output, so the crystal topology detector finds no connected load caps and produces crystal_circuits=[]. The RC filter detector then picks up the 1M+22pF pairs as low-pass filters instead.
  (signal_analysis)
- Same topology as CAN2Serial: ATmega328P connected to MCP2515 via SPI (MOSI, MISO, SCK, SS_MCP nets visible in the schematic). No SPI/memory_interfaces entry is produced. Additionally the MOSI/MISO/SCK nets show zero component pins because U2 (MCP2515 from EPSolar-CAN-rescue lib) has empty pins in the JSON.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000405: Component counts correct (60 components: 36 resistors, 12 capacitors, 12 transistors); All 12 RC input filter circuits missed (100R + 10nF per cell voltage input); 12 BSS308PE cell-balancing transi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Diseno-Electronico_SmartBMS_Monitoreo y balanceo de las celdas.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies 60 non-power components matching the source: R12-R47 (36 resistors), C13-C24 (12 capacitors), Q2-Q13 (12 BSS308PE transistors). All component types and references match exactly.

### Incorrect
(none)

### Missed
- The schematic has 12 repeated RC low-pass filter cells on the cell voltage sensing inputs: one 100R resistor in series with one 10nF capacitor to the lower cell reference, giving a cutoff of approximately 159 kHz. Examples: R16+C17, R17+C18, R18+C19, etc. None are detected (rc_filters=[]). The root cause is that all components use the 'Nodo_BMS_1_1-rescue:...' library prefix, causing all pin lists to be empty in the JSON output. With no pin-to-net connectivity data, the topology detectors find nothing.
  (signal_analysis)
- The schematic contains 12 BSS308PE PMOS transistors (Q2-Q13), each forming a cell-balancing bypass switch: gate driven via a 1k resistor, drain through a 10R/2W ballast resistor to the cell bottom rail. The transistor_circuits detector returns an empty list. Same root cause as the RC filter miss: rescue library components have empty pin lists, so no transistor topology can be inferred.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000406: Multi-sheet component count correct: 115 total (55 sheet 1 + 60 sheet 2); Crystal circuits not detected for Y1 and Y2; BMS system detection incomplete: LTC6804-2 found but cell_count=0 and balance_...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Diseno-Electronico_SmartBMS_Nodo_BMS_1_1.sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly parses both sheets: sheet 1 (Nodo_BMS_1_1.sch) contributes 55 non-power components and sheet 2 (Monitoreo y balanceo de las celdas.sch) contributes 60, totalling 115. Power rails, unique parts, and net counts are consistent with the hierarchy.

### Incorrect
(none)

### Missed
- Sheet 1 contains Y1 and Y2 crystals (both with rescue-library prefix 'Nodo_BMS_1_1-rescue:...'). Their pin lists are empty in the output, so no connected load capacitors can be found and crystal_circuits=[] even though both crystals exist and have load caps nearby in the schematic.
  (signal_analysis)
- The analyzer correctly identifies U5 as an LTC6804-2 BMS IC. However, cell_voltage_pins=0, cell_count=0, cell_nets=[], and balance_resistors=0 are all reported as zero. The sheet hierarchy connects 13 cell voltage inputs (C0-C12) and 12 cell balancing outputs (B0-B11) to sheet 2 through named net labels, and sheet 2 has 12 balancing switch transistors (Q2-Q13) with 10R ballast resistors. Because the rescue-library components in both sheets have empty pin lists, the BMS detector cannot traverse the cell voltage or balancing connectivity and reports a structurally empty BMS entry.
  (signal_analysis)

### Suggestions
(none)

---
