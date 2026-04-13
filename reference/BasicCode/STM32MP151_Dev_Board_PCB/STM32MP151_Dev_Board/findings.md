# Findings: BasicCode/STM32MP151_Dev_Board_PCB / STM32MP151_Dev_Board

## FND-00001281: AE1 (Antenna_Dipole) classified as type 'ic'; U1 (STM32MP151 SoM compute module) misidentified as power regulator with estimated_vout=6.5V; I2C bus correctly detected with pull-ups R18/R19 (4K7) to...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32MP151_Dev_Board.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Both I2C lines detected with correct pull-up resistors and correct rail. Devices U1 and U4 (PCM3060) correctly identified as bus participants.
- USB1_P/N (J8), USB2_P/N (J13), and USB_P/N (J12 debug port) all correctly found. Series resistors R20/R21, R22/R23, R27/R28 correctly identified. USB_P/N correctly has has_esd=true with TPD2EUSB30 (U5).
- Crystal Y2 detected at 26MHz with correct load capacitors C6 and C7 at 10pF each, effective load 8pF calculated.
- WiFi RF matching network correctly detected with resonant frequency calculation appropriate for 2.4GHz band.
- D2 (TVS on Vdrive bus), D3 (TVS on Earth-GND), and F1 (2A polyfuse) all captured in protection_devices with correct nets.

### Incorrect
- AE1 with lib_id 'antenna:Antenna_Dipole' is assigned type='ic' in both the main and WIFI sheet outputs. Antennas should get a distinct type (e.g., 'antenna') or at minimum not be grouped with ICs. This is a recurring misclassification for dipole antenna symbols.
  (signal_analysis)
- The power_regulators detector identifies U1 (MYC-YA151C-256N256D, a full STM32MP151 SoM) as topology='ic_with_internal_regulator' with estimated_vout=6.5. The '65' in the part number is a temperature suffix (65°C), not a voltage. This is a false positive: a compute module should not be in power_regulators.
  (signal_analysis)

### Missed
- The design has two MMC/SDIO interfaces (MMC1 = SD card J5 with signals MMC1_CK/CMD/D0-D3, MMC3 = WiFi SDIO to U7 with MMC3_CK/CMD/D0-D3). Neither is identified in bus_analysis. A memory_interfaces or sdio detector should capture these.
  (signal_analysis)
- SAI1_FS_B, SAI1_SCK_B, SAI1_SD_A, SAI1_SD_B signals connect U1 to the PCM3060 audio codec (U4). No audio interface or I2S bus is detected. The ERC warnings do flag SAI1_MCLK_B and SAI1_SD_B as no_driver which shows the nets are seen, but the audio bus is not recognized.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001282: WIFI sub-sheet stats correct: 14 components, ESP8285 + crystal + antenna + passives

- **Status**: new
- **Analyzer**: schematic
- **Source**: WIFI.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- All 14 components catalogued correctly by type. Crystal Y2 (26MHz), IC U7 (ESP8285), antenna AE1, inductors, capacitors, resistors, and test points all present with correct quantities.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001283: Audio sub-sheet correctly identifies PCM3060PWR (U4) with coupling caps and 3.5mm jack

- **Status**: new
- **Analyzer**: schematic
- **Source**: audio.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 6 components correctly parsed. PCM3060 classified as 'ic', audio jack J2 as 'connector'. BOM accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001284: MMC sub-sheet correctly identifies 8 components: SD card connector J5 with 6 pull-up resistors and decoupling cap

- **Status**: new
- **Analyzer**: schematic
- **Source**: mmc.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- 8 components parsed correctly. 6 resistors at 47K (pull-ups for MMC1 lines) and 1 capacitor (0.1uF) correctly classified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001285: USB sub-sheet: 6 components with TPS2042D USB power switch correctly parsed

- **Status**: new
- **Analyzer**: schematic
- **Source**: usb.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- USB-A host power management with TPS2042D (U3), USB connectors J8/J13, and decoupling caps correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001286: PCB front/back component count disagrees with gerber: PCB reports 38F/41B, gerber reports 43F/36B; Unrouted net correctly identified: unconnected-(J5-SHIELD-PadP1) with 4 pads unrouted; Board dimen...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32MP151_Dev_Board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB has routing_complete=false with exactly 1 unrouted net on J5 (SD card shield pins). Accurately detected.
- Physical board parameters and routing statistics look accurate and self-consistent.
- Zone named 'Antenna' has is_keepout=true with all copper activities restricted, appropriate for the 2.4GHz dipole antenna area.

### Incorrect
- PCB statistics show front_side=38, back_side=41, but gerber component_analysis (using X2 attribute data) shows front_side=43, back_side=36. The PCB parser likely miscounts components — it counts only SMD footprints by layer but may miss THT or other types in the split. The gerber X2 data is more authoritative.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001287: Gerber set complete: all 9 expected layers present with correct layer functions and polarity; Drill classification correctly identifies 185 vias, 24 component holes, 2 NPTH holes; Stackup correctly...

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-24

### Correct
- F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts all found. PTH and NPTH drill files present. Sourced from gbrjob file. complete=true, missing=[].
- Via drill 0.3988mm (185 count), component drills at 0.95mm and 1.0mm for connectors/headers, 2.301mm for large connector holes, 1.699mm NPTH for mounting slots. Classification_method=x2_attributes is reliable.
- Board thickness 1.6mm, F.Cu/B.Cu at 0.035mm, core dielectric 1.51mm FR4. Design rules show 0.2mm track-to-track clearance, 0.127mm minimum line width.
- Layer extents are all within or close to the 72x106mm board outline. B.SilkS and F.SilkS slightly exceed board edge (normal for silk extending outside outline), alignment=true with no issues.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
