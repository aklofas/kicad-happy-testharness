# Findings: RPi5-HATplus / HATPlus_HAT+

## FND-00001225: HAT_3V3 and HAT_5V0 nets classified as 'signal' instead of 'power'; I2C bus (GPIO0_ID_SDA0/GPIO1_ID_SCL0) with EEPROM U1/U2 not detected as I2C memory interface; DNP component U2 (AT24CS64-MAHM) co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HAT+.kicad_sch
- **Created**: 2026-03-24

### Correct
- U2 is marked dnp=true in the schematic and the analyzer correctly captures it. R9/R10 are identified as pull-ups on SDA/SCL and R11 as a pull-down on A0, all with correct directions and values (3.9k). PWR_FLAG warning on GND is valid since this hat has no PWR_FLAG symbol.
- The connector J1 has many GPIO pins routed to single-pin nets (GPIO15_RXD, GPIO17, etc.) since this HAT only uses I2C. The connectivity_issues.single_pin_nets list correctly captures all of these, which is useful for design review.

### Incorrect
- The hierarchical nets '/01889de2.../HAT_3V3' and '/01889de2.../HAT_5V0' are clearly power rails (connected to EEPROM VCC and RPi GPIO header power pins) but net_classification labels them as 'signal'. These come via hierarchical labels rather than PWR symbols, but the names and connectivity make the power nature obvious.
  (signal_analysis)
- A0 (SolderJumper_2_Open, lib_id Jumper:SolderJumper_2_Open) is categorized as 'ic' rather than 'jumper'. It is a solder jumper for selecting the EEPROM A0 address bit. This affects component type counts.
  (signal_analysis)

### Missed
- U1/U2 are AT24CS64 I2C EEPROMs with SDA/SCL pins connected through pull-up resistors R9/R10 to the RPi5 ID EEPROM bus. The signal_analysis.memory_interfaces list is empty and design_observations is empty — the I2C EEPROM circuit should be detected. The pull-up resistors (3.9k) on SDA/SCL are present and correctly wired.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001226: power_rails is empty [] — GND is present as 'HAT_GND' in ground_domains but not in statistics.power_rails

- **Status**: new
- **Analyzer**: schematic
- **Source**: HAT_Plus_sch.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The root schematic uses hierarchical labels (HAT_GND, HAT_3V3, HAT_5V0) rather than power symbols. The ground_domains section correctly detects HAT_GND but statistics.power_rails returns [] because no PWR_FLAG or power symbols exist at root level. This is a borderline case but the omission of power rails from statistics could mislead consumers.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001227: 4-layer board correctly identified; GND zone stitching with 20 stitching vias correctly detected; U1/U2 courtyard overlap correctly detected as a real placement concern; J1 edge clearance violation...

- **Status**: new
- **Analyzer**: pcb
- **Source**: HAT+.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Statistics correctly show 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu typed as power planes), 15 footprints, 32 vias, routing complete. Zone stitching detection identifies the GND pour spanning all 4 layers with 20 stitching vias at 0.4mm drill.
- U1 (AT24CS64-SSHM, SOIC-8) and U2 (AT24CS64-MAHM, DFN-8) are alternate-populate EEPROMs sharing the same I2C address space. Their courtyards overlap by 10.92mm2 since they occupy the same PCB area. The PCB does not mark U2 as DNP in footprint attributes — this is a real overlap from alternate-populate design pattern, correctly flagged.
- The Samtec horizontal connector J1 protrudes slightly past the board edge (negative clearance of -0.06mm). This is a real DFM concern for a board meant to plug into a Raspberry Pi, correctly detected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
