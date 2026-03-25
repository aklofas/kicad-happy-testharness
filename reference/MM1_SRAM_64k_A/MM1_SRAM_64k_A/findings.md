# Findings: MM1_SRAM_64k_A / MM1_SRAM_64k_A

## FND-00000876: Legacy .sch parser misses data pin connections for U1/U2 (IS61LV256AL SRAM) and logic gates U3-U5; single_pin_nets observation for ~MEMADDRESS_15 is a false positive

- **Status**: new
- **Analyzer**: schematic
- **Source**: MM1_SRAM_64k_A.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Same MEMDATA parsing failure. Additionally, U3 (74AHC1G04 inverter), U4/U5 (74AHC1G32 OR gates) show all signal pins as net=None — their connectivity is entirely absent. Only the net-level data partially reflects these: ~MEMADDRESS_15 shows U3 output but MEM1_~CE/MEM2_~CE correctly show U4/U5 output driving SRAM CE pins.
  (signal_analysis)
- The design_observations flags ~MEMADDRESS_15 as a single-pin net (only U3 inverter output). However, this net is correctly used as U3's output — it just does not directly drive the SRAM CE pins (those use MEM1_~CE and MEM2_~CE which are driven by U4/U5 OR gates). The real issue is that the OR gate inputs feeding ~MEMADDRESS_15 are not connected in the net data due to the pin parsing failure. The observation is a consequence of the pin connectivity bug, not a real design issue.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000877: DFM tier 'standard' despite approx_min_spacing_mm=0.184mm (below 0.2mm standard threshold)

- **Status**: new
- **Analyzer**: pcb
- **Source**: MM1_SRAM_64k_A.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- SRAM PCB reports approx_min_spacing_mm=0.184mm but dfm_tier='standard' with violation_count=0. At 0.184mm spacing this should either trigger a DFM violation or escalate to a tighter tier. The FLASH board at 0.2116mm borderline also warrants attention. EEPROM at 0.305mm is clearly fine.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
