# Findings: SparkFun_RFID_USB-C_Reader / Hardware_SparkFun_USB_RFID_Reader

## FND-00001516: RFID USB-C reader (40 components); component counts and protection devices correct; buzzer transistor driver missed (Q1 collector drives BZ1(-)); UART not detected despite CH340C USB-UART converter

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_USB_RFID_Reader.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Total 40 components with correct breakdown: 9 resistors, 7 connectors, 5 jumpers, 4 capacitors, 4 mounting holes, 2 fiducials, 1 IC (CH340C U3), 1 transistor (Q1 MMBT2222A), 1 fuse (F1), 1 diode (D2 ESD), 1 LED (D1), 1 buzzer (BZ1). All refs verified against schematic.
- D2 (DT1042-04SO) correctly identified as esd_ic protecting USB D+/D- lines. F1 (6V/0.5A/1A) correctly identified as a resettable fuse in series with VBUS. Both accurately captured in protection_devices.
- Three VUSB decoupling capacitors correctly identified: C2 (2.2uF), C3 (0.1uF), C4 (10uF), totalling 12.3uF. has_bulk=true and has_bypass=true accurate. C1 (10nF on V3 internal rail of CH340C) correctly excluded from VUSB.
- Q1 (MMBT2222A) NPN BJT correctly detected with emitter to GND and base resistor R4 (180 ohm). LED driver sub-detection accurately identifies D1 (Green LED) driven via R3 (1k) through Q1 collector: VUSB -> JP2 -> D1(A) -> D1(K) -> R3 -> Q1(C).
- Power rails correctly identified as VUSB and GND only. Board uses USB bus power directly without onboard regulation. No spurious extra rails reported.
- 42 nets correctly identified, matching the PCB net list exactly. Includes functional nets: VUSB, GND, DATA0, DATA1, ANT1, ANT2, TAG_IN_RANGE, CARD_PRESENT, LED, FORMAT, ~{RST}.

### Incorrect
(none)

### Missed
- BZ1 buzzer reports has_transistor_driver=False but Q1 (MMBT2222A) collector is on net __unnamed_2 which also connects to BZ1(-). Q1 drives the buzzer at its negative terminal simultaneously with the LED (D1). Circuit: BZ1(+) -> JP1 -> VUSB; BZ1(-) -> __unnamed_2 <- Q1(C). has_transistor_driver should be True.
  (signal_analysis.buzzer_speaker_circuits)
- UART bus not detected despite CH340C USB-UART converter (U3). U3 TXD (pin 2) connects to J5 test point; U3 RXD (pin 3) connects to DATA0 (Wiegand output line from RFID reader). bus_analysis.uart is empty. The UART interface between CH340C and RFID reader output should be detected.
  (design_analysis.bus_analysis.uart)

### Suggestions
- When detecting buzzer transistor drivers, check all transistor collectors/drains — not just those directly adjacent to the buzzer in the netlist — for cases where a single transistor drives both a buzzer and an LED from the same collector net
- Detect UART interfaces from CH340C/CH341 USB-UART ICs by matching TXD/RXD pin names on known USB-UART converter parts

---

## FND-00001517: RFID USB-C reader PCB (2-layer, 44.45x31.75mm); board dimensions, routing stats, and zone analysis all correct; 67 footprints includes 28 board-only kibuzzard artwork

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_USB_RFID_Reader.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board correctly identified as 2-copper-layer (F.Cu, B.Cu). copper_layers_used=2 accurate.
- Board dimensions 44.45 x 31.75 mm (1.75" x 1.25") correct from edge cuts. 191 track segments, 25 vias, routing_complete=true, unrouted_net_count=0, net_count=42 all match the design.
- footprint_count=67 is correct and accounts for 28 board-only kibuzzard artwork footprints (logos, corner marks) plus 39 real electrical components. smd_count=28 and tht_count=7 refer to real components only, which is consistent internal accounting.
- Single GND zone spanning F.Cu and B.Cu correctly detected as is_filled=true. fill_ratio=1.47 is physically correct: filled_area=2074.4mm2 is the sum of copper fill on F.Cu (949.94mm2) and B.Cu (1124.46mm2), against outline_area=1411.29mm2 (the 2D polygon area). Values > 1 are expected and correct for dual-layer zones.
- Net count=42 matches schematic exactly. All 42 nets have copper pads in the PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
