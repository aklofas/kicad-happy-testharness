# Findings: brightcloudy/kicad-pcbs / signalgen

## FND-00002255: ADP1715-3.3 LDO regulator has input and output rails swapped; SPI bus to AD9834 DDS chip not detected; ADA4805-1 op-amps classified as comparator_or_open_loop when circuit context suggests buffer/a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-pcbs_signalgen_signalgen.sch.json
- **Created**: 2026-03-24

### Correct
- The top-level signalgen.sch correctly parses all 4 sheets (signalgen.sch, mcu.sch, usbbridge.sch, ddscore.sch) and aggregates 54 total components with the full BOM. The individual sub-sheets are also parsed independently as separate outputs. Component types across all sheets are correctly counted: 10 ICs, 29 capacitors, 12 resistors, 3 connectors.

### Incorrect
- The analyzer reports U2 (ADP1715-3.3) with input_rail='+3.3V' and output_rail='+5V'. This is backwards: the ADP1715-3.3 is a 3.3V LDO linear regulator that takes +5V on its IN pin and outputs +3.3V on its OUT pin. The PCB net list confirms the +3.3V net is driven by U2's OUT pin (power_out type). The analyzer likely confused the voltage suffix in the part name ('-3.3') with the input rail rather than the output voltage.
  (signal_analysis)
- Both U9 and U10 (ADA4805-1 op-amps) are classified as 'comparator_or_open_loop'. U9 has both inverting and non-inverting inputs on the same net (__unnamed_16), which typically indicates a unity-gain buffer or a measurement issue in the net extraction — not an open-loop comparator. U10 has both inputs connected to VOUT. This is likely an artifact of incomplete net tracing rather than genuinely open-loop configurations. The ADA4805-1 is a precision op-amp used here in an analog signal conditioning stage downstream of the AD9834 DDS.
  (signal_analysis)

### Missed
- The design has an AD9834 DDS signal generator (U8) connected via SPI (signals SPI1_SCK, SPI1_MOSI, SPI1_NSS) from the STM32F030F4 MCU (U3), and also an MCP4542 digital potentiometer (U7) on the same SPI bus. The bus_analysis.spi array is empty. These nets have the prefix 'SPI1_' and are connected between the MCU and peripheral ICs, which should be recognizable as an SPI bus.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002256: RC filter detection misidentifies USART1_TX signal net as the ground reference

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-pcbs_signalgen_mcu.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The RC filter detector reports two RC networks (R2/C6 and R3/C6) with ground_net='USART1_TX'. USART1_TX is a hierarchical label connecting to the MCU's UART TX output — it is a signal net, not ground. The capacitor C6 (100n) has one pin on the unnamed node between R2/R3 and the other pin on the USART1_TX net. The MCU subsheet treats USART1_TX as a shared net but the top-level sheet likely uses it as a signal net. The analyzer should not classify a net named 'USART1_TX' as a ground reference.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
