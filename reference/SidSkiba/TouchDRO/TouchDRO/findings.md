# Findings: SidSkiba/TouchDRO / TouchDRO

## FND-00001640: USB compliance correctly identifies J1–J4 (USB_B_Micro) and skips J5–J8 (Conn_01x03); RC filter detection correctly identifies 8 RC paths (4 DATA + 4 CLK) sharing capacitors C1–C4; PWR_FLAG warning...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: TouchDRO.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- J1–J4 use lib_id=Connector:USB_B_Micro (footprint='User Footprint Library:USB Breakout Board') and are correctly flagged in usb_compliance. J5–J8 use lib_id=Connector_Generic:Conn_01x03 (3-pin TTL-scale headers) and are correctly excluded. The vbus_esd_protection=fail finding for J1–J4 is also accurate (no TVS or ESD protection in the design).
- The design uses a wired-OR-style input stage where each scale channel (X, Y, Z, W) has one DATA resistor and one CLK resistor both driving the same SCALE_VIN node through a shared capacitor. The analyzer correctly identifies all 8 R+C pairs (R1+C1 for X_D, R5+C1 for X_CLK, etc.) and their 33.86 Hz cutoff frequency.
- The schematic uses power:GND symbols but no PWR_FLAG symbol. The analyzer correctly issues a warning that GND has power_in pins but no power_out or PWR_FLAG, which would cause KiCad ERC to flag this net.

### Incorrect
- The statistics field counts ic=3 (U1, U2, U4 — unique physical chip packages), while the flat components list contains 15 ic-type entries (U1 × 7 gate-unit instances, U2 × 7 gate-unit instances, U4 × 1). The counting inconsistency exists because statistics deduplicates by ref but the components list includes every gate-unit symbol separately. While statistics.ic=3 is the more useful number (physical part count), the mismatch between total_components=54 and the 66-entry components list may confuse consumers. A clearer distinction between 'physical ICs' and 'gate instances' would help.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001641: zone_count=3 correctly counts copper fill zones and excludes three keepout zones; connectivity.routed_nets=41 vs total_nets_with_pads=59 correctly reflects 18 no-connect pins

- **Status**: new
- **Analyzer**: pcb
- **Source**: TouchDRO.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 6 zone definitions: 3 keepout zones (F.Cu, *.Cu, F&B.Cu with net=0) and 3 copper fill zones (GND on F.Cu, GND on B.Cu, and one net=0 F&B.Cu fill zone). The statistics report zone_count=3 which accurately counts only the fill/pour zones. The keepout zones are properly excluded.
- The schematic has exactly 18 no-connect markers (total_no_connects=18) which correspond to 18 pad nets that have no copper routing. The PCB reports 59 total nets with pads and 41 routed nets (59−41=18), with routing_complete=True and unrouted_count=0. All three figures are self-consistent and accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
