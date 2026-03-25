# Findings: RGB-LED-and-High-Dencity-CCT-Controller / Kicad Files_RGB_LED_&_High_Dencity_CCT_Controller

## FND-00001147: LM2678T-ADJ (U1) buck regulator detected with topology='unknown' instead of 'buck'; ground_domains.multiple_domains=False even though GND_LOGIC and GND_PWR are separate domains connected by a NetTi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RGB_LED_&_High_Dencity_CCT_Controller.kicad_sch
- **Created**: 2026-03-23

### Correct
- USB-C plug used as device without 5.1k CC pull-downs and without VBUS ESD protection or decoupling — all 4 failures are genuine design gaps. Series resistors on D+/D- correctly pass.
- Q1-Q5 all identified as mosfet type, each switching an LED_*(-) drain net with source to GND_PWR. load_type='connector' is plausible since the LED strips are connected via J connectors.

### Incorrect
- U1 LM2678T-ADJ is a 5A Simple Switcher step-down (buck) converter from Texas Instruments. The analyzer outputs topology='unknown' with fb_net='+5V'. The lib_id is a custom library ('Librería_Global_OK:LM2678T-ADJ') not matching standard KiCad names, which likely causes the topology detection to fail. Should be 'buck' or 'switching'.
  (signal_analysis)
- The board explicitly uses split ground planes (GND_LOGIC for digital circuitry, GND_PWR for power/LED) joined by NT2 (NetTie_4). The analyzer reports multiple_domains=False and classifies both as domain='signal'. This is a missed detection — multiple_domains should be True when separate ground nets are present even if connected via a net tie.
  (signal_analysis)

### Missed
- The I2C bus between U3 (ESP32-C3-WROOM-02) and the TLC59116IRHBR LED driver via Driver_SDA/Driver_SCL is only detected in the control sub-schematic. The main schematic shows bus_analysis.i2c=[] even though the I2C nets and devices are present in its component list.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001148: I2C missing pull-ups correctly identified on Driver_SDA/Driver_SCL; Cross-domain signals correctly flagged for 3.3V/5V level shift on I2C and RESET nets; TLC59116 decoupling missing on +5V rail cor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: control.kicad_sch
- **Created**: 2026-03-23

### Correct
- control sub-schematic detects I2C bus between ESP32-C3 and TLC59116 with has_pull_up=False on both SDA and SCL. This is a genuine design gap — I2C requires pull-up resistors.
- Driver_RESET, Driver_SDA, Driver_SCL connect ESP32 (3.3V) to TLC59116 (5V) with needs_level_shifter=True. This is a real design concern.
- design_observations flags U2 (TLC59116IRHBR) with rails_without_caps=['+5V'] — no bypass capacitor on the 5V supply pin is a real oversight.

### Incorrect
- The control sub-schematic uses a local 'GND' power symbol but this is a hierarchical sub-sheet that inherits net names from the parent through hierarchical labels. The GND pwr_flag warning in the sub-sheet context may be a false alarm — the actual parent defines GND_LOGIC and GND_PWR with their own power sources. This is a known challenge for flat-analyzed sub-sheets.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001149: routed_nets=33 while total_nets_with_pads=42 yet routing_complete=True — contradictory; Separate GND_LOGIC (F.Cu) and GND_PWR (B.Cu) zone pours correctly identified; U3 thermal pad with 12 thermal ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: RGB_LED_&_High_Dencity_CCT_Controller.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Two zones detected: GND_LOGIC on F.Cu (4663 mm² filled, fill_ratio=0.754) and GND_PWR on B.Cu (3982 mm² filled, fill_ratio=0.644). This correctly captures the split ground plane design.
- thermal_pads reports U3 pad '19' (2.9x2.9mm, 8.41mm²) with nearby_thermal_vias=12. This is correct for an ESP32-C3 module's GND pad.

### Incorrect
- 9 nets have pads but no routing tracks, yet the board is marked routing_complete. These are likely GND_LOGIC and GND_PWR nets whose pads are connected via copper zone fills (not tracks). The routed_nets count should include zone-connected nets or the reporting logic should be clarified.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
