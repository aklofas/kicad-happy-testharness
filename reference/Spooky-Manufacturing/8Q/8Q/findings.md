# Findings: Spooky-Manufacturing/8Q / 8Q

## FND-00000341: SDRAM chip IS42S16400J-xC with STM32F429BITx not flagged in design_observations despite identifiable lib_ids

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 8Q_preprocessor.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- preprocessor.sch contains IS42S16400J-xC (lib_id: Memory_RAM:IS42S16400J-xC) and STM32F429BITx (MCU_ST_STM32F4:STM32F429BITx, has built-in FMC SDRAM interface). The schematic has 0 nets because it is a stub (components placed but not wired), so memory_interfaces detection correctly fires no circuit-topology match. However, the analyzer could emit a design_observation noting 'SDRAM chip present (IS42S16400J-xC) paired with MCU having SDRAM interface (STM32F429BITx)' based purely on lib_id pattern matching, independent of net connectivity. Currently design_observations is empty for this file. This is a minor gap: lib_id-aware design notes for recognizable chip combinations do not fire when net context is absent.
  (signal_analysis)

### Suggestions
(none)

---
