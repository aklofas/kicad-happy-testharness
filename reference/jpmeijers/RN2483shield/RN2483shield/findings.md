# Findings: jpmeijers/RN2483shield / RN2483shield

## FND-00001175: SHIELD1 (Arduino shield connector) classified as 'switch' instead of 'connector'; BATTERY and 3.3VOLT nets classified as 'signal' instead of 'power'; only GND detected as power rail; UART bus corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RN2483shield.sch.json
- **Created**: 2026-03-23

### Correct
- The design_analysis net_classification correctly marks HW_TX, HW_RX, UART_ARDUINO_TO_RADIO, and UART_RADIO_TO_ARDUINO as 'data'. RN2483 as a LoRaWAN module with UART interface is appropriately represented.
- The RN2483 has many unused GPIO pins; 53 no-connects is consistent with the 47-pad IC having most pins left unconnected. Parsing correctly captures this.

### Incorrect
- The ARDUINO_SHIELD footprint is clearly a multi-pin connector/header, but the component type is inferred as 'switch'. This also propagates into subcircuits where SHIELD1 appears as neighbor type 'switch'. The value 'ARDUINO_SHIELD' and footprint name both indicate connector.
  (signal_analysis)
- The statistics section lists only 'GND' in power_rails. BATTERY (labelled net, acts as supply rail from J1 screw terminal) and 3.3VOLT (supply from SHIELD1) are net_classification 'signal' instead of 'power'. The KiCad 5 legacy format lacks explicit PWR symbol info, but these should be inferred from net names and usage.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001176: Courtyard overlaps between P1/P2 and P1/P3 flagged — these are deliberately stacked headers; Dual GND copper pours on F.Cu and B.Cu correctly detected with fill ratios; P2 connector has all 6 pads ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RN2483shield.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Two filled GND zones found (F.Cu 47.4% fill, B.Cu 70.1% fill) plus one keepout zone. Board dimensions 68.9x53.6mm, 2-layer, fully routed — all correct.
- P2 is a 6-pin header used as a bus for the UART TX signal; all pads share UART_ARDUINO_TO_RADIO. Similarly P3 is all UART_RADIO_TO_ARDUINO. This unusual single-net multi-pad connector is faithfully reported.

### Incorrect
- P1, P2, P3 are three 1x6 socket strip headers placed in a stacked arrangement on the PCB (15.55mm2 overlap each). For a shield board, stacked headers at the same position are intentional (they form a 3-row connector block). This overlap warning is a false positive in context.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
