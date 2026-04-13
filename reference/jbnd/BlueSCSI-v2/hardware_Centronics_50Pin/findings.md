# Findings: jbnd/BlueSCSI-v2 / hardware_Centronics_50Pin

## FND-00000411: RP1 (Raspberry Pi Pico module) classified as 'resistor' due to R-prefix heuristic; SD2 (MicroSD card socket) classified as 'switch' instead of a memory/connector component; AP1117-ADJ regulator Vre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_Centronics_50Pin_Centronics_50Pin.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- RP1 is a custom symbol for a Raspberry Pi Pico/BlackSCSI MCU module (lib_id: custom_symbols:BlackSCSI, footprint: CustomFootprints:BluePillModule, 40 pins). The analyzer classifies it as 'resistor' because its reference designator starts with 'R'. This inflates the resistor count by 1 (38 reported instead of 37 actual discrete resistors) and the component type distribution is incorrect. The same misclassification occurs in all four BlueSCSI-v2 schematics.
  (statistics)
- SD2 (value: MicroSD-TF-06, lib_id: New_Library:MicroSD-TF-06, footprint: Library:TF-06_MicroSD) is a complete MicroSD card socket with SPI interface pins (CLK, MOSI, MISO, CS, DAT1, DAT2) plus card-detect. It is classified as 'switch' — likely because MicroSD sockets contain a card-detect mechanical switch and the symbol lib may include that in the device. The correct classification should be 'connector' or a dedicated 'sd_card' category. The same occurs in all four BlueSCSI-v2 schematics (SD1/SD2). This also contributes to the SPI/SD interface being missed (see false_negative below).
  (statistics)
- The AP1117-ADJ has a documented internal reference voltage of 1.25 V. The analyzer falls back to a 0.6 V heuristic (vref_source: 'heuristic') and reports estimated_vout = 1.068 V. With the correct Vref of 1.25 V and the divider R21=120 Ω (top, Vout→ADJ) / R20=154 Ω (bottom, ADJ→GND), the formula gives Vout = 1.25 × (1 + 120/154) ≈ 2.22 V. The output rail is named '+2V8', and the design_observation already flags a large vout_net_mismatch (61.9% diff), but the root cause is the wrong Vref assumption rather than a design error. The AMS1117-2.85 in the other three schematics is handled correctly as a fixed-output part.
  (signal_analysis)
- U10 (value: Centronics50PinMale, lib_id: custom_symbols:Centronics50PinMale, footprint: Library:Centronics50Male) is the main 50-pin Centronics SCSI connector on this board. It is classified as 'ic' because its reference designator uses the 'U' prefix. While U-prefix for large connectors is an unusual but valid design convention, the component is purely a passive connector and should be classified as 'connector'. This inflates the IC count by 1 (8 reported instead of 7) and under-reports connectors (1 reported instead of 2).
  (statistics)

### Missed
- The schematic has a MicroSD card (SD2) connected via nets named SD_CLK, SD_CMD_MOSI, SD_D0_MISO, SD_D3_CS, SD_D1, SD_D2, forming a clear SPI mode SD card interface. The memory_interfaces list in signal_analysis is empty for all four BlueSCSI-v2 schematics. The net names explicitly contain MOSI/MISO/CLK keywords, which should be sufficient for the analyzer to detect and report a SPI or SD-card memory interface. This is a consistent false negative across all four files.
  (signal_analysis)

### Suggestions
- Fix: RP1 (Raspberry Pi Pico module) classified as 'resistor' due to R-prefix heuristic
- Fix: SD2 (MicroSD card socket) classified as 'switch' instead of a memory/connector component
- Fix: U10 (Centronics 50-pin SCSI connector) classified as 'ic' instead of 'connector'

---

## FND-00000412: RP1 (Raspberry Pi Pico MCU module) classified as 'resistor' due to R-prefix heuristic; SD2 (MicroSD card socket) classified as 'switch' instead of a connector/memory component; SPI/SD card interfac...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_DB25_External_DB25_External.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Same issue as in Centronics_50Pin: RP1 (custom_symbols:BlackSCSI, 40-pin MCU module) is classified as 'resistor' because its reference designator starts with 'R'. The resistor count is reported as 34 instead of 33 actual discrete resistors. The statistics include RP1 in the resistor bucket alongside R1–R56.
  (statistics)
- Same issue as in Centronics_50Pin: SD2 (MicroSD-TF-06) is classified as 'switch' instead of 'connector' or a storage interface. The SD_CLK/SD_CMD_MOSI/SD_D0_MISO/SD_D3_CS nets are present but the SPI interface is not detected.
  (statistics)

### Missed
- Same as Centronics_50Pin: nets SD_CLK, SD_CMD_MOSI, SD_D0_MISO, SD_D3_CS are present but memory_interfaces is empty. The SPI SD card interface connected to the Raspberry Pi Pico (RP1) is not identified.
  (signal_analysis)

### Suggestions
- Fix: RP1 (Raspberry Pi Pico MCU module) classified as 'resistor' due to R-prefix heuristic
- Fix: SD2 (MicroSD card socket) classified as 'switch' instead of a connector/memory component

---

## FND-00000413: RP1 (Raspberry Pi Pico W module) classified as 'resistor' due to R-prefix heuristic; SD1 (MicroSD card socket) classified as 'switch'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_Desktop_50_Pin_Desktop_50_Pin_TopConn.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- RP1 (value: PicoWModule, lib_id: New_Library:PicoWModule) is a Raspberry Pi Pico W MCU module. It is classified as 'resistor' because its reference starts with 'R'. The resistor count is reported as 47 instead of 46 actual discrete resistors. The USB_DM/USB_DP design observations correctly reference RP1 as a USB-capable device, which highlights the inconsistency — it is treated as MCU-like for USB detection but as a resistor for component type statistics.
  (statistics)
- SD1 (value: SOFNG_SD-001, lib_id: custom_symbols:SOFNG_SD-001) is a MicroSD card socket classified as 'switch'. The SPI interface nets (SD_CLK, SD_CMD_MOSI, SD_D0_MISO, SD_D3_CS) are present but memory_interfaces is empty, same as the other three schematics.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: RP1 (Raspberry Pi Pico W module) classified as 'resistor' due to R-prefix heuristic
- Fix: SD1 (MicroSD card socket) classified as 'switch'

---

## FND-00000414: RP1 (Raspberry Pi Pico MCU module) classified as 'resistor' due to R-prefix heuristic; SD2 (MicroSD card socket) classified as 'switch' instead of connector/memory component

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_PowerBook_PowerBook.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- RP1 (value: Pico_Footprint, lib_id: custom_symbols:BlackSCSI, 40-pin MCU module) is classified as 'resistor' because its reference starts with 'R'. The resistor count is 40 instead of 39 actual discrete resistors. Same issue as the other three schematics.
  (statistics)
- SD2 (value: MicroSD-TF-06, lib_id: New_Library:MicroSD-TF-06) is classified as 'switch'. The SPI interface nets are present (SD_CLK, SD_CMD_MOSI, SD_D0_MISO, SD_D3_CS) but memory_interfaces remains empty. Same issue as the other three schematics.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: RP1 (Raspberry Pi Pico MCU module) classified as 'resistor' due to R-prefix heuristic
- Fix: SD2 (MicroSD card socket) classified as 'switch' instead of connector/memory component

---
