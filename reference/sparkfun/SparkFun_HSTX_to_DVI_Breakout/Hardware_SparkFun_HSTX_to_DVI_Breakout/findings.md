# Findings: sparkfun/SparkFun_HSTX_to_DVI_Breakout / Hardware_SparkFun_HSTX_to_DVI_Breakout

## FND-00001463: Component count of 22 and type breakdown are accurate; AP3602 classified as LDO regulator; it is actually a charge pump; HDMI connector and differential pairs correctly detected; Voltage divider fo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_HSTX_to_DVI_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic reports total_components=22 with: 4 mounting holes (ST1-ST4), 5 resistors (R1-R5, where R1 is a 4-element array and R2/R3 are 4-element arrays), 1 transistor (Q1, BSS138 dual N-MOSFET), 2 fiducials, 3 capacitors (C1, C2, C3), 2 connectors (J1 FPC, J2 HDMI), 2 others (G1 SparkFun logo, G2 OSHW logo), 2 jumpers (JP1 CEC, JP2 HPE), and 1 IC (U1 AP3602). Component list and counts are all consistent with the schematic.
- hdmi_dvi_interfaces correctly identifies J2 as an HDMI connector. The differential_pairs array correctly lists 4 HDMI differential pairs (HDMI_D0+/-, HDMI_D1+/-, HDMI_D2+/-, HDMI_CK+/-) and 4 HSTX source pairs from J1 (D0+/-, D1+/-, D2+/-, CK+/-), all with series resistors identified.
- signal_analysis.voltage_dividers correctly detects the R5/R4 100k/100k divider on the HOTPLUG detect circuit (5V_HOTPLUG to HOTPLUG to GND), with ratio=0.5 and mid_point_connections showing JP2 (HPE jumper). This matches the schematic's hot-plug detect voltage divider feeding the HDMI HPE pin.
- decoupling_analysis correctly detects C3 (10uF) on the 5V rail and C1 (10uF) on the 3.3V rail. C2 (1uF) on 3.3V is not listed as a decoupling cap — examining the schematic, C2 is likely the charge pump flying capacitor for U1, not a rail decoupling cap, so its omission from the decoupling list is correct.

### Incorrect
- The AP3602 (Diodes Inc.) is a 100mA charge pump (voltage doubler) that converts 3.3V input to a 5V output by switching capacitor doubling — not an LDO. The analyzer classifies it as topology='LDO' in both power_regulators and inrush_analysis. The 3.3V-to-5V conversion (boosting voltage) is physically impossible for an LDO which can only regulate downward. The correct topology is 'charge_pump' or 'boost'. Additionally, the inrush_analysis estimated_inrush_A=0.1A and assumed_soft_start_ms=0.5ms are based on LDO assumptions, which are wrong for a charge pump.
  (signal_analysis)
- The transistor_circuits entry for Q1 (BSS138 dual N-MOSFET in SOT-363) reports gate_net='3.3V', drain_net='5V_SDA', source_net='SCL'. This is a level-shifter circuit (3.3V to 5V I2C), but the source/drain assignment appears reversed: an N-MOSFET level-shifter has its source tied to the lower voltage side (3.3V/SCL), gate biased to 3.3V, and drain connecting to the 5V side via pull-up. The reported source_net='SCL' and drain_net='5V_SDA' appear plausible but the gate_net='3.3V' being connected directly to the gate (without pull-up) is unusual — normally the gate is biased from the 3.3V rail through R5/R4 resistors. The gate_driver_ics listing U1 (AP3602 charge pump) as gate driver is incorrect; U1 is the power IC, not a gate driver.
  (signal_analysis)

### Missed
- The design has JP1 (CEC jumper) and JP2 (HPE jumper) which serve as cut-trace isolation points for the CEC and Hot Plug Detect signals. These could be flagged as design protection/isolation features. Additionally, the HDMI GND shields (pins 11, 17, 2, 5, 8, SH) are correctly connected to GND, but no ESD protection devices are detected on the HDMI differential pairs — the resistors R2/R3 serve as series termination, not ESD protection. The has_esd=false in all differential_pairs entries is correct, but an observation about missing ESD protection on HDMI data lines would be valuable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001464: 4-layer board, 25.4x25.4mm, 33 nets, routing complete; GND and 3.3V zone stitching correctly identified across 4 layers; Footprint count of 30 and SMD/THT classification correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_HSTX_to_DVI_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PCB correctly reports copper_layers_used=4 (F.Cu, In1.Cu, In2.Cu, B.Cu), board dimensions 25.4x25.4mm, net_count=33, routing_complete=true, 259 track segments, 58 vias.
- thermal_analysis.zone_stitching correctly identifies two zones: GND spanning B.Cu/F.Cu/In1.Cu with 34 vias, and 3.3V on In2.Cu (a dedicated power plane) with 7 vias. The 3.3V power plane occupying In2.Cu (aliased as L3.Cu) is consistent with a 4-layer stackup where inner layers serve as power/ground planes.
- footprint_count=30, smd_count=18, tht_count=0. The board has all SMD components (FPC connector J1, HDMI J2, resistor arrays R1-R3, resistors R4-R5, capacitors C1-C3, transistor Q1, AP3602 U1, jumpers JP1/JP2, fiducials, standoffs) — no THT components. smd_count=18 accounts for pads-present footprints; the remaining are board-only or exclude-from-bom decorations.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
