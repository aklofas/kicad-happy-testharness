# Findings: Jana-Marie/LAEMP-Panel / laemp_base

## FND-00000762: LDO regulator, USB-C compliance, RC filters, LED chain all correctly detected; UART bus detection reports 4 separate single-device nets instead of a paired UART interface between U1 and U2; PWR_FLA...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: laemp_base_laemp_base.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- AMS1117-3.3 (VBUS→+3V3) detected as LDO. USB-C J3 CC pulldown resistors pass, VBUS ESD fail is real (no TVS). Four 100k/100n RC filters on PWM_R/G/B/PWM_1 correctly classified as low-pass. SK6812 chain=1 in this schematic is correct since remaining LEDs are on the LED board.
- VBUS is supplied by USB-C connector J3. GND and VBUS both lack PWR_FLAG symbols. The warnings are accurate and expected for a USB-powered design without explicit PWR_FLAG placement.

### Incorrect
- E75_TX/E75_RX connect to ESP32 (U1) through series resistors R6/R7, creating unnamed intermediate nets. The analyzer lists 4 UART nets each with only one IC device (U2 or U1), missing the U2↔U1 UART interface. The cross-connection through passives is not followed to identify the paired interface.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000763: 44-LED SK6812 chain correctly detected with 2640mA estimated current; ERC no-driver warning on DIN net is accurate — data input comes from base board connector

- **Status**: new
- **Analyzer**: schematic
- **Source**: laemp_led_board_laemp_led_board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Chain from D1 to D44, data_in_net=DIN, protocol=single-wire (WS2812), SK6812 type. The 44×60mA=2640mA estimate is accurate for full-white operation. 44 decoupling 100n caps also correctly inventoried.
- J2 pin 1 (passive) and D1 DIN (input) on DIN net with no output driver in this isolated schematic. This is expected for a daughterboard design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000764: Base PCB thermal analysis, DFM, routing completeness all accurate

- **Status**: new
- **Analyzer**: pcb
- **Source**: laemp_base_laemp_base.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 52 footprints (2 are logo G***), 2-layer fully routed. ESP32 thermal pad detected with 8 nearby vias. GND zone stitching on both copper layers with 76 vias. DFM standard tier, no violations. Tombstoning risk correctly flagged on 0402 caps near GND zones.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000765: VBUS minimum track width (0.2mm) not flagged for high LED current (up to 2640mA); All 44 0402 decoupling caps flagged medium tombstoning risk due to VBUS/GND thermal asymmetry

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: laemp_led_board_laemp_led_board.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Every 100n cap has pad 1 on VBUS (signal) and pad 2 on GND zone, creating thermal asymmetry. The analyzer correctly identifies all 44 as medium risk. No false positives or misses.

### Incorrect
(none)

### Missed
- The LED board carries VBUS to 44 SK6812 LEDs with a maximum current of ~2640mA at full brightness. The PCB has VBUS tracks as narrow as 0.2mm (rated ~0.5A at 1oz Cu). The current_capacity section lists VBUS min=0.2mm but raises no warning. narrow_signal_nets is empty and no current headroom advisory is generated for this power net.
  (signal_analysis)

### Suggestions
(none)

---
