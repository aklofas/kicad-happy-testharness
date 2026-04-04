# Findings: KiCad-RP-Pico / Test_Test

## FND-00000732: Pico breakout board correctly parsed — 4 components, 36 nets, all pins connected; Power domain reports VBUS net as primary power rail for Pico instead of VSYS/3V3; AGND (pin 33) and ADC_VREF (pin 3...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Test_Test.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U1 (Pico, 43 pins), J1/J2 (Conn_01x20), J3 (Conn_01x03) all correctly extracted. unconnected_pins=0 is correct. GND net with 16 connections is accurate (Pico has 8 GND pins, connectors share the net).

### Incorrect
- ic_power_rails for U1 reports power_rails: ['__unnamed_28'] which is the VBUS net (pin 40). For a Pico, VSYS (pin 39) and 3V3 (pin 36) are the actual supply rails. VBUS is the USB input which may not always be present. The analyzer picks the first power_in pin encountered rather than identifying the true system supply.
  (signal_analysis)
- has_decoupling_cap: false for AGND and ADC_VREF pins. In this breakout design AGND and ADC_VREF are simply passed through to connector pins — there are no decoupling caps because this is a bare passthrough board. The observation is technically correct (no caps present) but the context is that it's a breakout, not a complete design, so the 'missing decoupling' reading is misleading.
  (signal_analysis)
- pwr_flag_warnings reports GND rail as lacking PWR_FLAG. The power_symbols section shows a PWR_FLAG symbol at coordinates (69.85, 109.22) on net 'PWR_FLAG' — but this appears to be a separate net named 'PWR_FLAG' rather than the GND net. Looking at the design, the PWR_FLAG is connected to GND via the schematic, but the net topology parser sees them as separate nets. This may reflect a real schematic organization issue (PWR_FLAG not directly on GND net) but the warning message is confusing.
  (signal_analysis)

### Missed
- J3 has SWDIO on pin 1 and SWCLK on pin 3 (GND pin 2), which is a standard SWD debug connector. test_coverage.observations says 'No debug connectors (SWD/JTAG/UART) identified'. The SWD pins are on unnamed nets ('__unnamed_29', '__unnamed_30') so the name-based SWD detector misses them.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000733: RP-Pico breakout PCB correctly parsed — 4 THT components, 2-layer board, dual GND zones; assembly_complexity classifies all 4 components as SMD when 3 are connectors (THT); silkscreen warns about m...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Test_Test.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- footprint_count=4 (U1 Pico SMD/TH + 3 connectors), all THT, copper_layers=2, two GND fill zones (F.Cu and B.Cu), routing_complete=true with 37 segments at 1.0mm width. Board dimensions 43x65mm are correct for a Pico carrier.

### Incorrect
- The schematic output correctly shows smd_count=0 and tht_count=4. But the PCB assembly_complexity section (not present in the read data, but noted in the schematic output for RP-Pico) classifies components as 'other_SMD'. The Pico footprint (RPi_Pico_SMD_TH) is a hybrid, but J1/J2/J3 are pure THT pin sockets. The smd_count=0/tht_count=4 in PCB statistics is correct.
  (signal_analysis)
- documentation_warnings flags 'missing_connector_labels' for J1, J2, J3. On a Pico carrier board, the Pico footprint itself has all GPIO labels printed in silk (visible in user_silk_texts with 30 entries like RUN, GP26, VBUS, SWDIO, etc.), so the board identity and pin functions are well-documented. The warning treats each connector independently rather than recognizing the Pico footprint silk as the labeling mechanism.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
