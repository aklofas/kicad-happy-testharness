# Findings: axoulc/hwboard-bike-computer / PCB_hwboard-bike-computer

## FND-00002132: TPS61089 boost converter output voltage estimated as 2.496V instead of ~5V due to wrong Vref assumption

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hwboard-bike-computer_PCB_hwboard-smps.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer estimated Vout = 2.496V using a heuristic Vref of 0.6V with the 316k/100k feedback divider (ratio 0.240385). However, the schematic notes embedded in the design text explicitly state Vref = 1.212V, giving an actual target of 5.04V. The formula 1.212V * (1 + 316k/100k) = 5.04V matches the design intent. The 0.6V Vref heuristic is wrong for TPS61089 by 2x, causing a >100% error in the estimated output voltage. This is significant because the board's output rail (+5V) is used to power downstream circuits.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002133: UART interface on TESEO-LIV3R GNSS module not detected in bus_analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hwboard-bike-computer_PCB_hwboard-gnss.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The TESEO-LIV3R GNSS module (U1) has pins explicitly named UART_TX and UART_RX (pin numbers 2 and 3), and these are present in the ic_pin_analysis. Despite the unambiguous pin names and the nets being present, bus_analysis.uart is empty. The I2C bus on pins 7/8 was correctly detected, but the UART interface was missed entirely. A GNSS module with UART output is a very common use case.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002134: BQ25622 buck charger has missing power rails — no +VBAT or +5V rails detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hwboard-bike-computer_PCB_hwboard-pwr-mgt.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The hwboard-pwr-mgt sheet contains the BQ25622ERYKR battery charger and has zero power_rails listed (only GND). The components and their footprints are present but all 11 components are in missing_mpn and missing_footprint. This is a hierarchical sheet that presumably relies on parent sheet power symbols. The BQ25622 topology was classified correctly as 'battery management' but the output rail resolution failed — the rail name '/8f8a955d-0b0a-425c-a7dd-7b9e4e273caf/V_{IN}' (a UUID-based hierarchical net path) shows the analyzer is passing internal UUID-based net names through to the output rather than resolving them to meaningful rail names.
  (statistics)

### Suggestions
(none)

---

## FND-00002135: Early-stage PCB with single footprint and zero copper tracks correctly reported as unrouted

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hwboard-bike-computer_PCB_hwboard-bike-computer.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The board has footprint_count=1 (the Raspberry Pi CM0 module), copper_layers_used=0, track_segments=0, and routing_complete=false with 3 unrouted nets. This accurately reflects an early-stage PCB file that has the footprint placed but no routing started. The 87 nets are hierarchical net names imported from the schematic. The board outline (277x190mm) is realistic for a bicycle computer PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
