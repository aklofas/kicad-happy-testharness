# Findings: wujique/KicadSchModule / KicadSchModule

## FND-00000753: SPI flash ICs (W25Q128JVS, GD5F1GQ4) not detected as memory_interfaces or SPI bus — signal_analysis.memory_interfaces and bus_analysis.spi are both empty despite SPI0_MOSI/MISO/CLK/CS nets being pr...

- **Status**: new
- **Analyzer**: schematic
- **Source**: KicadSchModule_flash.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic has two SPI flash chips (a NOR flash and a NAND flash) sharing SPI0_* nets. The analyzer correctly identifies SDIO on TF_CARD.sch but misses SPI detection here. bus_analysis.spi is [] and memory_interfaces is []. Net names alone (SPI0_CLK, SPI0_CS, SPI0_MOSI, SPI0_MISO) should be enough to trigger SPI bus detection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000754: EA3036 triple-output LDO (generates +1V2, +2V5, +3.3V from +5V) not detected as a power_regulator — signal_analysis.power_regulators is empty

- **Status**: new
- **Analyzer**: schematic
- **Source**: KicadSchModule_EA3036.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- EA3036 is clearly a multi-output LDO regulator (F4 field says 'LDO'; has inductors L1-L3 for buck outputs, output filtering caps, feedback resistors R6-R11, and power rails +1V2/+2V5/+3.3V sourced from +5V). The analyzer should detect this as a power regulator subcircuit. subcircuits[0].description is blank and signal_analysis.power_regulators is []. Feedback voltage-dividers (R pairs around +1V2/+2V5/+3.3V outputs) are also missed.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000755: Component count mismatch: statistics.total_components=3 but components list has 8 entries (1 IC + 5 caps + 2 connectors), all with unannotated '?' references collapsed incorrectly in BOM

- **Status**: new
- **Analyzer**: schematic
- **Source**: KicadSchModule_RS232_SP3232.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The BOM shows 1 cap entry (C?) covering what are actually 5 separate capacitors, and 1 connector entry (J?) covering 2 connectors. unique_parts=3 but total_components=3 instead of 8. This is caused by KiCad 5 unannotated schematics where all refs are '?' — the statistics counter under-counts because it groups by reference rather than by component instance. The individual components list is correct (8 items) but statistics.total_components is wrong.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000756: CAN bus transceiver (VP230) not fully identified — bus_analysis.can reports net names but no transceiver device linking, and CANH/CANL differential pair is missing entirely

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KicadSchModule_can_vp230.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The VP230 is a CAN transceiver. The schematic has CAN_TX and CAN_RX nets correctly identified in bus_analysis.can, but 'devices' list is empty for both. More critically, the CANH and CANL differential pair (the RS-485-line side of the chip) is absent — only one bus side labeled. For VP230, the physical CAN bus lines would be present as nets but appear to have a no-connect on one pin.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000757: Unannotated stub sheet (USB2514 4-port USB hub IC with no wires) parsed correctly with 0 nets and proper annotation_issues reported

- **Status**: new
- **Analyzer**: schematic
- **Source**: KicadSchModule_USB2514.sch.json
- **Created**: 2026-03-23

### Correct
- Sheet has only a single placed component with no wiring — the analyzer correctly returns 0 nets, 0 wires, and flags unannotated U?. No false positives on signal detection.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000758: SDIO 4-bit SD card interface correctly detected with full signal mapping and has_pullups=false (the pullup resistors are level-shifting, not conventional pullups)

- **Status**: new
- **Analyzer**: schematic
- **Source**: KicadSchModule_TF_CARD.sch.json
- **Created**: 2026-03-23

### Correct
- SDIO bus detection is correct: all 6 SDIO signals identified (CLK, CMD, D0-D3), bus_width=4, has_pullups=false is appropriate since the 47K resistors here are level-shift/protection rather than I2C-style pullups. SDIO_DET net correctly captured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000759: Empty PCB (KiCad 5 legacy, no layout data) correctly parsed as zero-footprint board with kicad_version='unknown' and appropriate copper_presence warning

- **Status**: new
- **Analyzer**: pcb
- **Source**: KicadSchModule_KicadSchModule.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The .kicad_pcb file exists but contains no layout (it's an unstarted KiCad 5 board file). The analyzer returns all zeros with routing_complete=true by default and emits the 'No filled polygon data' warning. The kicad_version='unknown' for a KiCad 5 board where version cannot be inferred is a minor labeling gap (it should likely be '5 (legacy)' to match the schematic parser convention), but the data is otherwise accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
