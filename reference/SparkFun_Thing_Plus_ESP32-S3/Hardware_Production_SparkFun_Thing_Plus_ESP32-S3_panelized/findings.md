# Findings: SparkFun_Thing_Plus_ESP32-S3 / Hardware_Production_SparkFun_Thing_Plus_ESP32-S3_panelized

## FND-00001571: ESD protection device U2 (DT1042-04SO) not detected in signal_analysis.protection_devices; LDO regulators U6 and U1 (RT9080-3.3) correctly detected with topology and output rails; WS2812B addressab...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_Thing_Plus_ESP32-S3.kicad_sch
- **Created**: 2026-03-24

### Correct
- signal_analysis.power_regulators correctly identifies both U6 (VIN→3.3V) and U1 (VIN→3.3V_P) as RT9080 LDO regulators with ldo topology. Output rails and input rails are accurately captured.
- signal_analysis.addressable_led_chains correctly identifies D6 as a WS2812B single-LED chain, with the correct chain length of 1 and proper net connections.
- design_analysis.bus_analysis.i2c correctly identifies R15 as a 2.2k SDA pull-up and R12 as a 2.2k SCL pull-up. The pull-up values are appropriate for a 400kHz Qwiic I2C bus.
- annotation_issues.duplicate_references correctly identifies ["C3","G3","R1"] as duplicates arising from the two-sheet hierarchical design (root sheet + Peripherals sheet each having their own C3, G3, R1 instances). This is accurate: separate sheet instances should use unique annotation.
- pwr_flag_warnings correctly identifies that the VIN and GND power nets lack PWR_FLAG symbols to satisfy ERC. This is accurate for the schematic's power architecture where VBUS/VIN enters from a connector without an explicit PWR_FLAG.
- subcircuits correctly captures U5 as an MCP73831 LiPo battery charger with its associated passive components (programming resistor, input/output filtering capacitors). The charger topology and battery/charging net connections are accurate.

### Incorrect
(none)

### Missed
- The schematic contains U2, a DT1042-04SO USB ESD protection IC on the USB D+/D- lines. The signal_analysis.protection_devices array is empty. The DT1042-04SO is a 4-channel TVS array specifically for USB ESD protection and should be recognized as a protection device.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001572: J1 USB-C connector misclassified as through_hole instead of mixed/smd; 4-layer copper stackup with GND and 3.3V internal planes correctly detected; Routing completeness correctly reported as comple...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Hardware_SparkFun_Thing_Plus_ESP32-S3.kicad_pcb
- **Created**: 2026-03-24

### Correct
- thermal_analysis correctly identifies GND zone on F.Cu, In1.Cu, and B.Cu and a 3.3V zone on In2.Cu, accurately reflecting the 4-layer stackup: F.Cu (signal/components), In1.Cu (GND plane), In2.Cu (power plane), B.Cu (signal/GND). routing_complete=true and unrouted_count=0 are accurate for the single-board design file.
- connectivity.routing_complete=true and unrouted_count=0 accurately reflect the single-board PCB design file which is a fully routed production design.

### Incorrect
- J1 is a SparkFun USB-C 16-pin connector that has SMD signal pads on the bottom and THT mounting legs for mechanical retention. The PCB analyzer reports it as through_hole (tht_count includes it) but its primary signal connections are SMD. The correct classification should be 'mixed' or the component should be counted in smd_count since its signal footprint is SMD.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: J1 USB-C connector misclassified as through_hole instead of mixed/smd

---

## FND-00001573: Panelized PCB kicad_version reported as 'unknown' despite file version 20221018 (KiCad 7); Panelized PCB routing_complete=False with 19 unrouted nets is a panelization artifact, not a real issue

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Thing_Plus_ESP32-S3_panelized.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The panelized PCB file begins with '(kicad_pcb (version 20221018) (generator pcbnew)'. Version 20221018 corresponds to KiCad 7. The analyzer outputs kicad_version='unknown' instead of '7' or '20221018'. This is a version-mapping gap for the KiCad 7 file format epoch.
  (kicad_version)
- The panelized board has routing_complete=False and unrouted_net_count=19. This arises because panel rails, tooling strips, and fiducials added during panelization create net stubs that are intentionally not connected in the panel layout. The underlying individual boards are fully routed. The analyzer should indicate this is a panelized design or suppress routing completeness for panel files.
  (connectivity)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001574: Gerber completeness incorrectly reports Edge.Cuts as missing; GKO file is the board outline; GKO file (board outline) misclassified as B.Mask due to incorrect X2 FileFunction attribute; Inner coppe...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware_Production
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- completeness.missing_required includes 'Edge.Cuts' and complete=false. However, the Production/ directory contains SparkFun_Thing_Plus_ESP32-S3_panelized.GKO which IS the board outline/Edge.Cuts layer. The analyzer fails to map the .GKO extension to the Edge.Cuts layer, likely because it relies solely on X2 FileFunction attributes. The GKO file's X2 header says FileFunction=Soldermask,Bot (a KiCad export quirk), but the file content contains the Profile (board outline) aperture function. The analyzer should use aperture function analysis as a fallback when X2 attributes are inconsistent.
  (completeness)
- The GKO file (SparkFun_Thing_Plus_ESP32-S3_panelized.GKO) has X2 attribute %TF.FileFunction,Soldermask,Bot*% (a known KiCad export quirk where .GKO gets an incorrect Soldermask attribute) but its aperture_analysis shows it contains Profile (board outline) geometry. The analyzer classifies it as B.Mask based on the X2 attribute without cross-checking the aperture function, resulting in B.Mask appearing in found_layers while Edge.Cuts is absent. The aperture content should take precedence over or be reconciled with the X2 attribute.
  (found_layers)
- The board is a 4-layer design (F.Cu, In1.Cu, In2.Cu, B.Cu) but GL1 and GL2 inner layer gerbers are not recognized by the analyzer. As a result missing_recommended=[] rather than listing In1.Cu and In2.Cu as missing recommended layers for a 4-layer design. Even if the analyzer cannot read .GL1/.GL2 files, it should infer that inner copper layers are expected given the layer_count=4 and flag them as missing.
  (completeness)

### Missed
- The Production/ directory contains SparkFun_Thing_Plus_ESP32-S3_panelized.GL1 (FileFunction=Copper,L2,Inr) and SparkFun_Thing_Plus_ESP32-S3_panelized.GL2 (FileFunction=Copper,L3,Inr), which are the In1.Cu and In2.Cu inner copper layers of the 4-layer board. These files are completely absent from the gerber analysis output — they do not appear in files_analyzed, found_layers, or any other section. The analyzer apparently does not recognize .GL1/.GL2 as gerber file extensions.
  (found_layers)

### Suggestions
- Fix: GKO file (board outline) misclassified as B.Mask due to incorrect X2 FileFunction attribute

---
