# Findings: keebio/fourier / fourier_fourier-left_fourier-left-bottom

## FND-00002180: Key matrix topology detector misclassifies rows as columns and vice versa, overcounts switches 54 vs actual 34

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fourier_fourier_fourier-left_fourier-left.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Fourier left keyboard has 4 actual row nets (rowA, rowB, rowC, rowD) and 6 column nets (col1–col6), for 34 actual key switches (excluding SW_RST1). The topology-based detector reports 5 rows and 13 columns, placing 'col2' in row_nets and 'rowB', 'rowC' in col_nets — mixing up rows and columns. The reported switches_on_matrix=54 and diodes_on_matrix=54 are ~59% higher than the actual 34 key switches.
  (findings)

### Missed
(none)

### Suggestions
(none)

---
