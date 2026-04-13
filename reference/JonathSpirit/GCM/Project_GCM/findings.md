# Findings: JonathSpirit/GCM / Project_GCM

## FND-00000566: Multi-sheet parsing: all 10 sheets discovered and parsed; Voltage divider R1/R2 correctly detected for LTC6994 SET pin; SPI bus not detected despite named SPI_MOSI/MISO/SCLK/CS nets; CLK_SELECT_* n...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Project_GCM.sch.json
- **Created**: 2026-03-23

### Correct
- The top-level schematic has 9 sub-sheet references; the analyzer found and parsed all 10 files correctly, with accurate component counts (126 total), BOM grouping, and sheet_files list.
- R1 (523k) top, R2 (1M) bottom, ratio 0.6566 = 1M/(523k+1M), midpoint connected to U2 SET pin. Values and connections are accurate.

### Incorrect
- CLK_SELECT_0, CLK_SELECT_1, CLK_SELECT_FAST_0/1/2, CLK_SELECT_SLOW_0/1/2 are outputs of the BWRITE1 data register (U4, a 74AHC273 D-latch) that select which clock frequency the mux outputs. They are control/select signals driven by bus data, not clock signals. The name prefix 'CLK_' causes the name-based classifier to incorrectly label them as 'clock'.
  (signal_analysis)
- X1 is labeled 'ECS-2200BX-500' and the output net is named CLK_50MHZ, strongly indicating 50 MHz. The crystal_circuits entry reports frequency: null. The part number and net name together would allow the analyzer to populate this field, but neither heuristic is applied. Same issue in fileClockGenerator.sch output.
  (signal_analysis)

### Missed
- SPI_MOSI, SPI_MISO, SPI_SCLK, SPI_CS nets are all present and individually classified correctly (data/clock/chip_select), but bus_analysis.spi returns []. The SPI detector failed to group them into a bus instance — likely because the signals connect through a hierarchical sheet boundary (connector sub-sheet) rather than to a single master IC.
  (signal_analysis)
- The power_rails list contains both '+3V3' and '+3.3V' as separate entries. These likely refer to the same physical rail but differ by naming convention used in different sub-sheets. The analyzer tracks both separately but does not issue a design_observation warning about possible unintentional rail isolation due to name mismatch.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000567: Clock generator sub-sheet analysis is accurate — oscillator, counters, muxes, and decoupling all correctly identified; CLK_SELECT_* nets misclassified as 'clock' (same issue as top-level); LTC6994 ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: fileClockGenerator.sch.json
- **Created**: 2026-03-23

### Correct
- fileClockGenerator.sch: 2 sheets parsed (itself + filePClockGenerator.sch child), 28 components, 1 oscillator (X1), 4 SN74LV393A binary counters, 6 CD74AC151 8:1 muxes, 1 74AHC273 register, 1 74AHC1G32 OR gate. Net classification for CLK_50MHZ, CLK_50dXXXMHZ divided clocks all labeled 'clock' correctly. Decoupling analysis finds 13 caps on +5V rail.

### Incorrect
- CLK_SELECT_FAST_0/1/2, CLK_SELECT_SLOW_0/1/2, CLK_SELECT_0/1 are data inputs to the CD74AC151 8:1 mux select pins; they are control/address lines driven from the BWRITE1 register, not clock signals. Misclassification propagates from the top-level via name-based heuristic.
  (signal_analysis)

### Missed
- U2 (LTC6994xS6-1) with R1/R2 voltage divider on SET pin and C4 on DIV pin forms a programmable delay for power-on reset sequencing (200ms noted in schematic). The signal_analysis has no 'timer_circuits' or 'delay_circuits' detector, so this notable functional block is invisible in the analysis output.
  (signal_analysis)

### Suggestions
(none)

---
