# Findings: keebio/fourier / fourier_fourier-right_fourier-right-bottom

## FND-00002181: 'rowA' appears in both row_nets and col_nets simultaneously; switch count overcounted 56 vs actual 39

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: fourier_fourier-right_fourier-right.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Fourier right has 39 actual key switches and 4 named row nets (rowA–rowD). The topology detector reports 5 rows and 18 columns but places 'rowA' in both row_nets and col_nets — a net cannot be both a row and column driver. switches_on_matrix=56 and diodes_on_matrix=56 significantly exceed the 39 actual switches (44% overcount). This is the same topology detection failure as the left half.
  (findings)

### Missed
(none)

### Suggestions
(none)

---
