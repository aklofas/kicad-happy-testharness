# Findings: hahardware / pcb_kicad_antenna_2.4ghz_chip_Chip Antenna_Chip Antenna

## FND-00002163: LM2574 buck switching regulator misclassified as LDO topology; D7 '15AmpTriac' component misclassified as diode type

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hahardware_pcb_kicad_power_PowerSupplyV2.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U3 LM2574 is detected as a power_regulator but assigned topology 'LDO'. The LM2574 is a 500mA Step-Down (Buck) Switching Voltage Regulator with an external inductor on the output — not a linear/LDO regulator. This is a fundamentally different circuit topology. LM317K (U6) is also in this schematic and IS correctly an LDO, which may explain how the LDO logic fired for both.
  (signal_analysis)
- D7 with value '15AmpTriac' is assigned type 'diode' by the component classifier. A TRIAC is a bidirectional thyristor (semiconductor switching device) used in AC power control — it is structurally and functionally entirely different from a diode. The 'D' reference designator prefix caused the misclassification. The schematic uses the TRIAC with a MOC3043M optocoupler (U2) for isolated AC load switching.
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002164: TLV1117LV-3V (LDO regulator, U2) not detected as power_regulator; Dual crystal circuits correctly detected for STBlueNRG-1 BLE SoC

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hahardware_pcb_kicad_button_button.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies both crystal oscillator circuits for U1 STBlueNRG-1: Y2 (XTAL 32MHz, 32000000 Hz system clock) with its 33pF load cap C15, and Y1 (Xtal 32.768kHz, 32768 Hz RTC crystal) with its 27pF load caps. Both frequencies match typical BLE SoC requirements (RF reference and low-power RTC). Multi-sheet parsing also works correctly — components from button_rf.sch and peripherals_button.sch are included in the 3-sheet analysis.

### Incorrect
(none)

### Missed
- U2 is a TLV1117LV-3V (3.3V LDO, lib_id LT1129CST-3.3) but power_regulators list is empty. The same design also appears in button_mkii (same issue). The component is a classic 3-pin LDO in SOT-223 package with IN, GND, OUT pins. The analyzer fails to detect it as a regulator, likely because neither 'TLV1117' nor 'LT1129' appears in the regulator detection pattern set, or because the pin mapping from the KiCad v5 legacy lib entry was not resolved.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002165: STBlueNRG-1 QFN exposed pad (pad 33) reported four times in thermal_pads; Board outline not detected for KiCad v4 boards using 'Margin' layer

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hahardware_pcb_kicad_button_button.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The thermal_pads list for U1 contains four identical entries for pad '33' on F.Cu, all reporting pad_size_mm=[1.73,1.73] and nearby_thermal_vias=0. In the KiCad v4 PCB file, the exposed thermal pad is defined as four separate rectangular sub-pads (one per quadrant) sharing the same pad number 33. The analyzer emits one thermal_pad record per sub-pad definition rather than aggregating them. The same duplication occurs in button_elder, button_mki, and button_mkii (all use the same STBlueNRG-1 footprint).
  (thermal_analysis)

### Missed
- board_width_mm and board_height_mm are null for 28 out of 35 PCBs in this repo. All PCBs are KiCad v4 format and use '(layer Margin)' (layer number 45) for board outline graphics. The PCB analyzer only recognizes 'Edge.Cuts' for board outline extraction. For example, button.kicad_pcb has 4 gr_line elements on the Margin layer forming a 38.35×33.78mm rectangle, but board_outline.edge_count=0 and bounding_box=null. The 7 boards with valid dimensions (mifa_TI variants) are newer exports that use Edge.Cuts.
  (statistics)

### Suggestions
(none)

---

## FND-00002166: GerbTool .gtd proprietary file incorrectly included in gerber file list; Completeness check reports Edge.Cuts missing when Margin.gbr provides board outline

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_hahardware_pcb_kicad_antenna_2.4ghz_chip_Chip Antenna_Gerber.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The file '2.4 GHz Chip Antenna.gtd' is a GerbTool GT-Designer proprietary design archive (header: '$Program GerbTool GT-Designer Service Release 3'). It is not a Gerber/RS-274X file. The analyzer includes it in the gerbers list and counts it in statistics.gerber_files (inflating count to 8 instead of 7). The same issue occurs in pcb_kicad_antenna_2.4ghz_chip_vsma_GerbTool.json and other gerber sets in this repo. The GTD file parses to zero apertures, zero flashes, and zero draws, but is still counted.
  (statistics)
- completeness.missing_required includes 'Edge.Cuts' for chip antenna and vsma gerber sets, but both have a 'Chip Antenna-Margin.gbr' file that IS the board outline (FileFunction: Other,User with 4 draw elements forming the board rectangle). KiCad v4 exported the Margin layer as the board outline — it is functionally equivalent to Edge.Cuts. The analyzer does not recognize Margin.gbr as a board outline substitute, resulting in a false-positive missing layer warning.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002167: Git conflict backup files (*.gbr~HASH) included in gerber analysis

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_hahardware_pcb_kicad_antenna_2.4ghz_chip_vsma_GerbTool.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The vsma GerbTool gerber directory contains git conflict backup files 'Chip Antenna VSMA-B.SilkS.gbr~6162423... Tile uC and antenna boards' and 'Chip Antenna VSMA-B.SilkS.gbr~HEAD'. Both are included in the gerbers list, inflating gerber_files count to 10 (should be 7). These files have the same layer_type (B.SilkS) as the real file, so they triple-count the silkscreen layer. The completeness check falsely reports Edge.Cuts missing partly because the layer detection is confused by these extra files.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002168: Wireless radio modules (SAMB11G18A BLE SoC and XBee-PRO 900HP) not detected as wireless interfaces

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hahardware_pcb_kicad_base_base.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The base board contains U1 SAMB11G18A-edit (Microchip Bluetooth Low Energy SoC) and U2 XBee-PRO_900HP (900MHz proprietary radio module). The signal_analysis.wireless_interfaces list is empty. Both are explicit wireless devices with RF connections (SIG_2.4G net label, antenna connectors). The analyzer detects the UART bus (UART_RX/TX/CTS/RTS nets) for the XBee link but does not detect the BLE SoC or classify either component as a wireless interface.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002169: Patch antenna symbol (AE1 Antenna_Shield) misclassified as IC type

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hahardware_pcb_kicad_antenna_2.4ghz_patch_match_patch_match.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- AE1 with value 'Antenna_Shield' and footprint 'Antennas:Patch_Antenna_2.4GHz' is classified as type 'ic'. This is a PCB patch antenna (a copper structure on the PCB), not an integrated circuit. The component has two pins (feed/ground) and represents the radiating element in a 2.4GHz impedance matching network schematic. Similar misclassification occurs in pcb_kicad_antenna_2.4ghz_patch_balun_patch_balun.sch.json where 'Antenna_Shield' is also classified as IC.
  (components)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002170: DFM analysis correctly reports standard tier for base board despite v4 format

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_hahardware_pcb_kicad_base_base.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly reports dfm_tier='standard' for the base board with min_track_width=0.2032mm and min_drill=0.254mm, no violations. Despite the board being KiCad v4 format and missing board outline detection, the DFM metrics are correctly extracted from track and pad data. The 147 footprints, 308 track segments, 36 vias, and routing completeness (0 unrouted nets) are all accurately reported.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
