# Findings: megredondo/KICAD_Boards / Boards_I2c_PnC_I2C_KICAD_power_control_ipe_v1

## FND-00000621: Source file does not exist — repo not checked out or wrong path

- **Status**: new
- **Analyzer**: schematic
- **Source**: AudioAmplifier_AudioAmplifier.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The KICAD_Boards repo checked out at repos/KICAD_Boards/ contains RF/microwave IPE boards, not AudioAmplifier/BatteryManagmentSystem/ESP32 designs. The paths in the review request do not exist on disk and no corresponding outputs were found under results/outputs/schematic/KICAD_Boards/. All 10 source/output pairs are inaccessible.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000622: Source file does not exist — same root cause as AudioAmplifier

- **Status**: new
- **Analyzer**: schematic
- **Source**: BatteryManagmentSystem_BatteryManagmentSystem.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- No subdirectory matching BatteryManagmentSystem, BreakoutSTM32L432KCU, BuckConverter, DCMotorDriveH-Bridge, ESP32_CAM_USB_Programmer, ESP32_Relay_Controller, ESP32_SmartWatch, ESP32_USB_PowerHUB, or FingerprintDoorLock exists under repos/KICAD_Boards/. The repo appears to be a different KICAD_Boards project than what the review packet expects.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000623: Source file does not exist — repo checkout mismatch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: GPS_Tracker_GPS_Tracker.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The KICAD_Boards repo checked out at /home/aklofas/Projects/kicad-happy-testharness/repos/KICAD_Boards/ contains RF/microwave IPE board schematics (KiCad 5 .sch format), not the GPS_Tracker, IR_Remote_Controller, LEDDriver, LiDAR_Scanner, POE_Injector, RS485_LoRa_Gateway, SPI_OLED_Display_Driver, SoilMoistureSensor, StepperMotorDriver, TempSensorNTC, or WeatherStation .kicad_sch files referenced in this review. Neither the source files nor their analyzer output JSON files exist at the specified paths. The review cannot be completed without first obtaining the correct repo checkout.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000624: Source file does not exist — repo checkout mismatch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: IR_Remote_Controller_IR_Remote_Controller.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause as GPS_Tracker: the checked-out KICAD_Boards repo does not contain this file. No output JSON exists either.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000625: Source file does not exist — repo checkout mismatch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LEDDriver_LEDDriver.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause. All 11 files listed in this review request are absent from the local checkout of KICAD_Boards.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000641: Track count (13 segments), via count (19), unrouted nets (19) all match source

- **Status**: new
- **Analyzer**: pcb
- **Source**: HMC_hmcdaughter_dac_hmcdaughter_dac.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Source general header says tracks=32 but that counts graphical lines; actual (segment) count is 13, which the analyzer correctly reports. Unrouted detection is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000642: Zero-footprint module-less board correctly parsed: 0 footprints, 141 tracks, net_count=0

- **Status**: new
- **Analyzer**: pcb
- **Source**: Superconducting_resonator_Superconducting_resonator.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board uses no modules (modules=0 in source general header). All segments are on net 0 (unassigned). The analyzer correctly reports 0 footprints, 0 nets, and no board outline. Board size=None is expected for a design with no Edge.Cuts geometry.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000643: Alignment false-positive correctly detected: Edge.Cuts extent 177x119mm vs copper layers 21x31mm

- **Status**: new
- **Analyzer**: gerber
- **Source**: HMC_hmcdaughter_dac_Gerber.json
- **Created**: 2026-03-23

### Correct
- Edge.Cuts gerber contains large alignment cross-hair marks (+/-250mm) far outside the actual board outline (~22x21mm). The analyzer correctly reports aligned=false with width/height variation of 156mm and 91mm. This is a legitimate flag for a gerber set that includes cross-hair calibration geometry in the Edge.Cuts layer.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000644: Silkscreen layers massively misaligned (B.SilkS 347mm wide, F.SilkS 135mm wide vs 23mm board) but aligned=true reported; Missing B.Mask and F.Mask flagged as incomplete, but this is a bare-die RF b...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: RF_Board_HMC_RF_IPE_Gerber.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer flags missing_required: [B.Mask, F.Mask] and reports complete=false. The RF_Board HMC design is a microwave chip-on-board design where solder mask is intentionally absent (confirmed by the board being a high-frequency RF test fixture). Flagging this as incomplete is a false positive for boards that intentionally omit solder mask. The completeness check uses a fixed required-layers list that doesn't account for bare-die or flex PCB designs.
  (signal_analysis)

### Missed
- The alignment check only considers F.Cu, B.Cu, Edge.Cuts and inner copper layers - silkscreen is excluded. B.SilkS content is offset ~147mm from board origin. This is a real misalignment (silkscreen items are completely outside the board area) but the analyzer reports aligned=true with no issues. The layer_extents output does include the SilkS sizes for reference, but no issue is flagged.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000645: Single Dwgs.User gerber-only export correctly identified as incomplete with all required copper/mask layers missing

- **Status**: new
- **Analyzer**: gerber
- **Source**: HMC_hmcdaughter_dac_Export.json
- **Created**: 2026-03-23

### Correct
- Export folder contains only a single Dwgs.User drawing file. The analyzer correctly identifies layer_count=0, all required layers missing (B.Cu, B.Mask, Edge.Cuts, F.Cu, F.Mask), and complete=false. This is an expected result for an intermediate/partial export.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000646: Single-sided RF resonator correctly parsed: 10 footprints, 123 tracks, 1 GND zone, routing complete

- **Status**: new
- **Analyzer**: pcb
- **Source**: Resonator_coupler_Resonator_coupler.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Custom library footprints (Battery:Short_CPW_20um, Battery:Open_CPW_20um) for CPW resonator stubs are correctly extracted with pad nets. Zone fill ratio 0.748 and net lengths are plausible for this small 10x8mm substrate design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000647: All 9 PCB and 10 Gerber source paths in the review request reference files that do not exist in the KICAD_Boards repo

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: N_A - files listed in review request do not exist.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The review request lists paths like .../repos/KICAD_Boards/BatteryManagmentSystem/BatteryManagmentSystem.kicad_pcb - none of these files exist. The actual KICAD_Boards repo (megredondo) contains RF/microwave boards (HMC DAC, RF_Board, Resonator_coupler, etc.), not the consumer electronics boards listed. The outputs reviewed are for the actual repo contents, not the phantom files in the request.
  (signal_analysis)

### Suggestions
(none)

---
