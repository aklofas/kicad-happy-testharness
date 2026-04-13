# Findings: peej/for-split-keyboard / for-split

## FND-00002179: Key matrix correctly detected as 5 rows x 12 columns with diode-per-key topology; Key matrix overcounts diodes_on_matrix (36) and switches_on_matrix (34) vs actual 30 each; reset_pin observation in...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_for-split-keyboard_for-split.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies a 5-row, 12-column key matrix using net-name detection (Row0–Row4, Col0–Col11). The design is a single-schematic split keyboard where both halves are described together, with Col6–Col11 fed via the COLS_RH1 connector to the right half. 30 diodes and 30 MX switches are correctly enumerated in the BOM.

### Incorrect
- The schematic has exactly 30 MX key switches and 30 diodes, but the key matrix detection reports switches_on_matrix=34 and diodes_on_matrix=36, with estimated_keys=36. The 6 columns Col6–Col11 are connector-forwarded (right-half columns via COLS_RH1/COLS_LH1) with no actual key switches, but the topology detector counts them as contributing to the matrix, inflating the totals by 4–6 components.
  (signal_analysis)
- The analyzer flags U1 (ProMicro) RST pin connected to Row1 as a potential issue (reset_pin category, no pullup, no filter cap). In this split keyboard design, RST is intentionally wired to a matrix row to enable bootloader entry via a key combination during matrix scan. This is a standard technique for split keyboards using Pro Micro. The observation is technically correct as a factual net connection, but the concern framing is a false positive for this design pattern.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
