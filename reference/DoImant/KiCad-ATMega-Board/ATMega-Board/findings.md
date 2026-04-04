# Findings: KiCad-ATMega-Board / ATMega-Board

## FND-00000730: MCP1703A-5002 LDO correctly identified with accurate input/output rails; Regulator_caps observation falsely reports input cap missing despite C2 (1uF) on VDC_IN; Crystal circuit Y1 (8MHz) detected ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ATMega-Board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- power_regulators correctly reports topology=LDO, input_rail='VDC_IN', output_rail='+5V'. The output rail has 4 decoupling caps (100n x3, 10uF x1) correctly enumerated in decoupling_analysis.
- crystal_circuits correctly identifies Y1, load_caps [C5=22p, C6=22p], effective_load_pF=14.0 with correct formula note. SPI bus lines (MOSI/MISO/SCK via J4) are present in net names. UART detection on D0/RX and D1/TX nets is correct.

### Incorrect
- design_observations flags 'missing_caps: {input: VDC_IN}' for U1. However, ic_pin_analysis for U1 pin 2 (VI/VDC_IN) correctly shows 'has_decoupling_cap: true, decoupling_caps: [C2 1uF]'. The design_observation and the ic_pin_analysis disagree — the design_observations regulator_caps checker appears to be using a stricter threshold or different logic than the pin-level decoupling check.
  (signal_analysis)
- VDC_IN is the input voltage rail fed by VIN connector. The analyzer flags it as 'no_driver' because connector passive pins don't count as drivers. This is expected behavior for a connector-powered rail, not a genuine ERC issue.
  (signal_analysis)

### Missed
- The schematic has explicit MOSI, MISO, SCK net labels connected to ATmega328 PB3/PB4/PB5 and the J4 ISP header. bus_analysis.spi is empty [] despite the named SPI nets being present. The UART detector fired on RX/TX nets but the SPI detector missed the MOSI/MISO/SCK pattern.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000731: 4-layer board with inner power planes correctly detected

- **Status**: new
- **Analyzer**: pcb
- **Source**: ATMega-Board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- copper_layers_used=4, correctly identifies In1.Cu and In2.Cu as 'power' type layers. footprint_count=29, routing_complete=true, via_count=17 are all plausible for this complexity level.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
