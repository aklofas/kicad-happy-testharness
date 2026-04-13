# Findings: sjgray/VIC2cr-Reloaded / VIC-Reloaded

## FND-00001748: Total component count (89) and all type breakdowns are accurate; unique_parts=45 matches distinct part values in BOM; total_no_connects=25 matches source schematic NoConn entries; power_rails corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VIC-Reloaded.sch.json.json
- **Created**: 2026-03-24

### Correct
- Source schematic has 89 unique component references (non-power): 24 resistors, 15 capacitors, 13 ferrite beads, 26 ICs, 7 connectors, 2 transistors, 1 crystal, 1 switch. The analyzer reports exactly these counts. Total BOM quantities sum to 89, matching total_components. The 7 connectors includes CN1, CON1, P4, P5, P6B, P6T, and P? (counted as one unique ref despite having 3 unannotated instances).
- The source schematic has exactly 45 distinct part values (verified by extracting unique F1 values per unique reference). The BOM has 45 entries and unique_parts=45.
- Counted 25 NoConn directives in the raw VIC-Reloaded.sch file, matching the reported value. These are expected on legacy Commodore chips like the 6502 (NC pins), 6560 VIC, and 6522 VIA.
- This is a VIC-20cr Commodore computer clone running entirely on a single +5V supply. No negative or other rails are used. The analyzer correctly reports only +5V and GND.
- The 14.31818 MHz crystal (Y1) is the standard NTSC color burst frequency used in Commodore VIC-20 computers. The analyzer correctly identifies it in crystal_circuits with frequency=14318180.0 Hz.
- Q1 (2SC1815) is the audio input buffer with base driven by AUDIO_IN net. Q2 (2SC1815) is the video output driver with collector driving VIDEO_OUT and emitter at +5V (unusual common-collector topology from the original CBM schematic). Both are correctly detected and their pin-net assignments match the physical wire connections in the source schematic.
- The source schematic has three unannotated P? connector instances (CONN_01X20, CONN_02X12, CONN_01X06) all sharing the same P? reference, and FB7 appears twice as a multi-unit or duplicate. The analyzer correctly reports duplicate_references=['FB7', 'P?'] and unannotated=['P?'].
- The 26 ICs include: 1x 6502 CPU, 2x 6522 VIA, 1x 6560 VIC, 1x 7402, 1x 74LS02, 1x 74LS04 (6 units), 1x 74LS06 (6 units), 1x 74LS08 (4 units), 3x 74LS138, 1x 74LS133, 3x 74LS245, 1x 4066, 3x 2114 SRAM, 1x 2332 ROM, 2x 2364 ROM, 2x 2016 SRAM, 1x LM555N.
- The schematic has 13 ferrite bead references (FB1, FB2, FB4, FB5, FB7, FB9, FB10, FB11, FB12, FB13, FB14, FB15, FB16), all with value 'FILTER'. These are used throughout the VIC-20 design for EMI filtering on signal lines. The analyzer correctly classifies all as ferrite_bead type.
- All 24 resistors are present: R1-R3 (2.2K), R5-R6 (330), R7 (560), R8 (1K), R9 (510), R10-R11 (1K/1.8K), R12-R14 (2.7K/270/180), R16 (10K), R17-R19 (1K), R23 (330), R24 (220M), R25 (150K), R26-R28 (1K/360), R41 (240).
- The analyzer correctly identifies 15 capacitors (C9-C17, C20-C21, C41-C42, C47-C48, C50), correctly excluding CN1 and CON1 which start with 'C' but are connectors. The CTRIM (C48) is correctly classified as capacitor type.

### Incorrect
(none)

### Missed
- The crystal oscillator circuit uses UB9 (7402 NOR gate used as inverter) as the amplifier, with C48 (CTRIM trimmer capacitor) and C50 (standard capacitor) as the Pierce oscillator load caps. The UB9 subcircuit correctly shows C48 and C50 as neighbors of Y1. However, the crystal_circuits entry for Y1 reports load_caps=[] instead of identifying C48 and C50. The CTRIM symbol for C48 may be preventing detection since it is not a standard 'C' capacitor symbol.
  (signal_analysis)
- The review prompt requests outputs for three schematic files including sub_schematic_Memory.kicad_sch.json and sub_schematic_VIC2cr-Reloaded_Expansion.kicad_sch.json. However, the VIC2cr-Reloaded repo only contains a single legacy KiCad 5 .sch file (VIC-Reloaded.sch) with no sub-sheets. The repo has no .kicad_sch files at all. The manifest only contains VIC-Reloaded.sch and the rescue-backup schematic. The requested sub-schematic outputs do not exist and cannot be produced from this repository.
  (sheets_parsed)

### Suggestions
(none)

---
