# Findings: ESP8266-Template-for-ESProg / ESProg_ESP8266_Template_Horizontal

## FND-00000505: Net 'RXD' incorrectly contains U1 GPIO15 (pin 16) and P1 pin 3 (VCC); should contain U1 GPIO3/RXD (pin 21) and P1 pin 4 (RXD); Net '+3V3' incorrectly contains U1 MOSI (pin 13) and P1 pin 4 (RXD); b...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ESProg_ESP8266_Template_Horizontal.sch.json
- **Created**: 2026-03-23

### Correct
- The statistics report 10 total components across 6 unique parts: 1 IC (U1 ESP-12E), 1 connector (P1), 3 resistors (R1 4.7k, R2 10k, R3 10k), 1 switch (SW1), and 4 mounting holes (MH1-MH4). All references match the schematic source exactly.
- The schematic has exactly 14 NoConn markers (lines 188-201 in source). The JSON reports total_no_connects: 14, matching the source.
- The schematic contains five +3V3 power symbols (#PWR02, #PWR03, #PWR05, #PWR07 at the top of various net branches) and four GND symbols (#PWR01, #PWR04, #PWR06, #PWR08). The JSON correctly identifies exactly two power rails: +3V3 and GND.

### Incorrect
- The schematic routes net label 'RXD' via wires 5700,3550→6000,3550→6900,3550, connecting U1 pin 21 (GPIO3/RXD) and P1 pin 4 (RXD). Instead the JSON places U1 GPIO15 (pin 16) and P1 pin 3 (VCC) on net 'RXD'. This is a coordinate-based pin resolution error: U1 GPIO15 at position y=92.71 mm and P1 VCC at y=90.17 mm are being mapped to the wrong net. The analyzer appears to be misidentifying which U1 and P1 pins land at the wire endpoint coordinates for the RXD label connection.
  (signal_analysis)
- The schematic shows U1 MOSI (pin 13, right side of ESP-12E at schematic coordinate 5700,3350) connects via wire 5700,3350→6000,3350 and then to +3V3 via R2. However P1 pin 4 (RXD) at y=92.71 mm (schematic y=3550) should be on net 'RXD', not '+3V3'. The '+3V3' net in the JSON lists P1 pin 4 (RXD) as a member, which is wrong. R2 pull-up connects U1 EN (pin 3) to +3V3 via wires 6000,3350→5700,3350, meaning the pin on that node is U1 EN, not MOSI. U1 MOSI (pin 13) is actually at the right side of U1 at schematic coordinate y=3550 and is NoConnect-marked.
  (signal_analysis)
- Wire at 5700,3450→6900,3450 connects U1 GPIO1/TXD (pin 22) to P1 pin 5 (TXD) — this should be net 'TXD'. The JSON instead puts P1 pin 2 (GPIO0) on the TXD net and puts P1 pin 5 (TXD) on the GPIO0 net, while U1 GPIO1/TXD (pin 22) ends up on unnamed net __unnamed_12. Similarly, U1 GPIO0 (pin 18) at schematic coordinate 5700,4250 connects via R3 to GPIO0 label, but the JSON puts U1 GPIO0 on __unnamed_7 (unconnected). This is a systematic mis-pairing of P1 connector pin assignments due to mirror/offset errors in coordinate-to-pin mapping for KiCad 5 legacy components.
  (signal_analysis)
- In the schematic, the RST label connects via wires through 6550,3100→4350,3100→4350,3350 to U1 pin 1 (~RST) at 4500,3350, and also to R1 pin 1 at 3800,3350, and SW1 pin 2 at 3450,3350. The JSON correctly shows R1 and SW1 on net RST but puts U1 ~RST (pin 1) on isolated net __unnamed_0 with only one pin. This means the analyzer failed to trace the wire from the RST label junction at 4350,3350 through to U1 pin 1 at 4500,3350.
  (signal_analysis)
- The schematic shows #PWR03 (+3V3) at position 5100,2700 connecting via wire 5100,2700→5100,3150 to U1 VCC (pin 8) at schematic position 5100,3150. The JSON places U1 VCC (pin 8) in isolated unnamed net __unnamed_18 with only that single pin, and does not include it in the +3V3 net. This means U1 is flagged as having no decoupling on the VCC rail and the power domain analysis is incomplete.
  (signal_analysis)
- U1 pin 15 (GND, power_in) sits at schematic coordinate 5100,3250 (package center y=3950, with GND pin at the bottom of the center row). The #PWR04 GND symbol is at 5100,4650, connected via wire downward to U1 GND. The JSON places U1 GND pin on an isolated __unnamed_5 net rather than the GND net. This is consistent with the broader pattern of coordinate-based pin resolution failures for this mirrored ESP-12E component in KiCad 5 legacy format.
  (signal_analysis)
- The JSON reports an SPI bus on U1 with MOSI on +3V3, MISO on __unnamed_1 (isolated), and SCK on __unnamed_4 (isolated). In the actual schematic, all SPI pins of the ESP-12E (MISO, MOSI, SCLK, CS0) are marked as NoConnect. The SPI bus detection is triggered by pin name matching on U1 but the underlying net assignments are wrong. Since MOSI/MISO/SCK are either on isolated nets or mis-assigned to +3V3, no real SPI bus is wired up — the detection result is a false positive caused by the pin assignment errors.
  (signal_analysis)
- The JSON UART analysis shows net RXD with U1 as the only device (pin_count 2) and net TXD with no devices (pin_count 1). In the actual schematic, U1 GPIO1/TXD (pin 22) connects directly to P1 TXD (pin 5) via the TXD label, and U1 GPIO3/RXD (pin 21) connects to P1 RXD (pin 4). Both U1 and P1 should appear in the UART detection with their respective TX/RX pairing. The erroneous net assignments cause the UART to appear one-sided.
  (signal_analysis)
- The design_observations entry reports rails_without_caps: ['+3V3'] for U1, which is technically accurate in that there are no decoupling capacitors anywhere in the design. However because U1 VCC (pin 8) is incorrectly placed on isolated net __unnamed_18 rather than +3V3, the analyzer is flagging +3V3 as the missing rail while actually not recognizing that the VCC pin itself is disconnected from +3V3 in its own net model. A downstream consumer of this observation would get a misleading picture of where decoupling is missing.
  (signal_analysis)

### Missed
- R2 (10k) connects between +3V3 and the GPIO0 net. This is a classic boot-mode pull-up: GPIO0 must be pulled high for normal boot on ESP8266. R2 performing a pull-up function on GPIO0 is a meaningful signal path observation but the signal_analysis section is empty (no pull-up/pull-down resistor detection). Whether or not pull-up detection is in scope for the analyzer, the voltage_dividers list is also empty, which is correct since R2 has only one leg to a signal net (the other is +3V3 directly, not a divider).
  (signal_analysis)
- R1 (4.7k) connects between +3V3 and the RST/~RST node (via wire from R1 pin 2 at 3700,3550 → +3V3 and R1 pin 1 at 3800,3350 → RST net). The EN pin of U1 also has its own pull-up (the 3700/3550 wire goes to EN via 4500,3550). In the actual schematic, wire 3700,3550→4500,3550 connects the +3V3 rail through R1 to U1 EN (chip enable), making this a standard EN pull-up. This pull-up connection is not reflected in the net assignments (U1 EN appears on isolated __unnamed_13) and is not flagged in signal_analysis.
  (signal_analysis)

### Suggestions
(none)

---
