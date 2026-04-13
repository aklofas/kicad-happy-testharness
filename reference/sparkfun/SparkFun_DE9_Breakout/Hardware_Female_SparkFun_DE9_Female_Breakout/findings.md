# Findings: sparkfun/SparkFun_DE9_Breakout / Hardware_Female_SparkFun_DE9_Female_Breakout

## FND-00001385: Component count of 9 and net count of 10 are accurate; pwr_flag_warning fires on GND for a passive breakout board — misleading false positive; missing_footprint flags G2 (SparkFun_Logo with on_boar...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_DE9_Female_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic contains exactly 9 components: J1 (DE9 Female), J2 (Conn_01x09), J3/J4 (Conn_01x01 x2), ST1/ST2 (Stand_off x2), G1/G2 (SparkFun_Logo x2), G3 (OSHW_Logo). The 10 nets (GND + pins 1-9) correctly model a DE9 breakout where each signal pin is individually accessible. BOM total quantity of 8 correctly excludes G3 because its in_bom=false, while all signal detectors are empty — appropriate for a purely passive connector breakout.

### Incorrect
- The analyzer emits a PWR_FLAG warning: 'Power rail GND has power_in pins but no power_out or PWR_FLAG'. However, this is a purely passive breakout board with no power supply — GND is just pin 5 of the DE9 connector passed to header pins (J3, J4). The GND symbol is used only for net naming. KiCad ERC would technically flag this too, but for a passthrough connector design this warning carries no actionable meaning and pollutes output. The same false positive fires on the Male variant.
  (pwr_flag_warnings)
- The analyzer flags G2 in missing_footprint because its footprint field is empty. However G2 has on_board=false, meaning it is intentionally not placed on the PCB. A logo-only schematic symbol with no board placement should not be flagged as a footprint problem. This same issue applies to both Female and Male schematics. The warning is technically correct (the field is empty) but semantically wrong for an intentionally off-board decorative symbol.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001386: All 21 signal detectors correctly return empty for a passive connector breakout; Missing MPN flags for all 6 connectors/logos are correct — SparkFun breakout boards carry no MPNs on schematic symbols

- **Status**: new
- **Analyzer**: schematic
- **Source**: Hardware_Male_SparkFun_DE9_Male_Breakout.kicad_sch
- **Created**: 2026-03-24

### Correct
- Both Female and Male schematics have zero findings across all signal_analysis detectors (voltage_dividers, rc_filters, power_regulators, transistor_circuits, etc.). This is exactly correct: the design is a passive DE9-to-header breakout with no active components, no filters, no power conversion. No false positives were triggered. The design_analysis.bus_analysis also correctly reports no I2C/SPI/UART/CAN buses.
- Both Male and Female schematics report all 6 BOM-visible references (J1-J4, G1, G2) in missing_mpn. This is accurate: SparkFun's schematic symbols for breakout boards typically have no MPN/manufacturer fields populated. The analyzer correctly identifies this gap without false negatives. The OSHW logo G3 is not flagged because it is correctly excluded from BOM (in_bom=false).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001387: footprint_count=43 is inflated by 37 decorative footprints; smd_count/tht_count (3/3) are accurate but do not reflect actual schematic component count; edge_clearance_warning for G3 (OSHW logo, -82...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_DE9_Female_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The 22.86 x 31.75mm board (~0.9" x 1.25") is consistent with SparkFun's standard small breakout form factor. 2-layer copper (F.Cu + B.Cu) is correct. All 27 track segments use a uniform 0.3048mm width (12 mil — standard SparkFun design rule). The GND copper zone covers both layers (725.8mm2) with 16 stitching vias. routing_complete=true and unrouted_count=0 confirm fully routed design. The DFM tier of 'standard' with min_track_width=0.3048mm is correctly classified.

### Incorrect
- The PCB contains 36 board_only kibuzzard decorative silkscreen footprints plus 1 exclude_from_bom OSHW logo, inflating footprint_count to 43. Only 6 footprints are electrical: J1 (DE9 Female, SMD, 11 pads), J2 (Conn_01x09, THT, 9 pads), J3/J4 (Conn_01x01, THT, 1 pad each), ST1/ST2 (Stand_off, SMD, 1 pad each). The statistics.footprint_count=43 with front_side=20, back_side=23 all reflect all footprints including decorative ones. front_side/back_side are computed from layer attribute rather than a dedicated 'side' field (footprints all show side=null in the output). The count is technically correct but potentially misleading when compared to the 9 schematic components.
  (statistics)
- The placement_analysis reports G3 (OSHW_Logo, exclude_from_bom) with edge_clearance_mm=-82.93, implying it extends 82.93mm beyond the board edge. This is almost certainly the bounding box of the Creative_Commons_License footprint's courtyard being measured from a reference point far outside the board outline. G3 is a purely decorative/IP silkscreen graphic with no copper pads. Similarly J2 (header, -15.88mm) and J1 (DE9 connector, -5.2mm) also show negative clearance, likely because these components intentionally overhang the board edge. The same pattern appears on the Male PCB (G3 at -76.83mm). These should not be treated as DFM errors.
  (placement_analysis)
- The placement_analysis reports 4 courtyard overlaps: J3/J1 (6.452mm2), J1/J4 (6.452mm2), J1/ST1 (0.0mm2), J1/ST2 (0.0mm2). The two zero-area overlaps for ST1/ST2 (standoffs) are spurious: a zero-area overlap is not a real overlap and should not be counted. The non-zero overlaps between J3, J1, and J4 (the GND header pins flanking the DE9) may also be intentional tight placement in a compact board, though they warrant flagging. The Male PCB shows the same pattern. The overlap_count=4 is inflated by the zero-area entries.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001388: Male PCB correctly shows 4 THT and 2 SMD footprints vs Female's 3 THT and 3 SMD — difference is the DE9 connector body type

- **Status**: new
- **Analyzer**: pcb
- **Source**: Hardware_Male_SparkFun_DE9_Male_Breakout.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The Male variant uses a through-hole DE9 header (J3, type=through_hole, 11 pads) while the Female variant uses a surface-mount DE9 connector (J1, type=smd, 11 pads). This correctly accounts for the difference: Male has smd_count=2 (ST1, ST2 standoffs) and tht_count=4 (J1, J3, J4, J2), Female has smd_count=3 (J1 DE9, ST1, ST2) and tht_count=3 (J2, J3, J4). Both variants share the same board dimensions, track count, and net count, consistent with pin-compatible designs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
