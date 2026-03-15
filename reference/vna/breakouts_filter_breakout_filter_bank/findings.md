# Findings: vna / breakouts_filter_breakout_filter_bank

## FND-00000151: RF filter bank breakout with Mini-Circuits LFCN low-pass filters. FI-prefix filters misclassified as fuses via F->fuse single-char fallback.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: breakouts_filter_breakout_filter_bank.sch.json
- **Related**: KH-081
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- FI-prefix components (LFCN-6000D+, LFCN-4400+, etc.) classified as 'fuse' via F->fuse single-char fallback despite lib_id 'EMI_FILTER'
  (signal_analysis.protection_devices)

### Missed
(none)

### Suggestions
- Add 'FI' prefix to type_map as 'filter'
- Add lib_id fallback: 'EMI_FILTER' or 'FILTER' in lib_id should override fuse classification

---
