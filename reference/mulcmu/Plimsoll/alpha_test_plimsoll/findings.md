# Findings: mulcmu/Plimsoll / alpha_test_plimsoll

## FND-00001135: dnp_parts reports 0 but 2 DNP components (C1, C2) are present; same bug in mini_hx717 (2 DNP) and underbed (9 DNP); sourcing_audit reports mpn_percent=0% and all 11 BOM parts as missing_mpn despite...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: mini_ads1220_plimsoll.kicad_sch
- **Created**: 2026-03-23

### Correct
- power_regulators correctly identifies U5 as an LDO with VBUS input and +3.3VADC output. RC filters at 15.9kHz, decoupling caps on +3.3VADC, differential pair Signal+/Signal-, and no_driver ERC warnings for bus signals from J1 all look accurate.

### Incorrect
- statistics.dnp_parts is always 0 across all four Plimsoll schematics even though components clearly have dnp=true and in_bom=false. The dnp count is not computed from the component list.
  (signal_analysis)
- The sourcing_audit.mpn_percent is 0.0 and all components appear in missing_mpn, but 11/12 BOM components have lcsc= populated (e.g., U1=C48263, U5=C379349, R7=C22775). Only J1 truly lacks any part number. The audit correctly identifies missing_lcsc=['J1'] but the mpn_percent metric ignores lcsc as a sourcing alternative.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001136: HX717 ADC falsely detected as 'ic_with_internal_regulator' because its VFB (voltage feedback reference output) pin triggers regulator heuristic

- **Status**: new
- **Analyzer**: schematic
- **Source**: mini_hx717_plimsoll.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- signal_analysis.power_regulators includes U6 (HX717 24-bit weight-scale ADC) with topology 'ic_with_internal_regulator' and fb_net='+3.3VADC'. The HX717 VFB pin is a reference voltage output for external use, not a regulator feedback pin. This is a false positive from the IC-regulator classifier.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001137: SPI bus not detected despite nets named SCLK, DIN, DOUT, ~{CS} connecting ADS131M04

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: underbed_plimsoll.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- design_analysis.bus_analysis.spi is empty even though nets are explicitly named SCLK, DIN, DOUT, ~{CS}, ~{DRDY} — all canonical SPI signal names. The bus detector failed to match these. In contrast, mini_ads1220 correctly has no SPI detection because its SPI nets use generic names (B3, B4, B5).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001138: PCB statistics, layer count, routing completeness, board dimensions, and decoupling placement all appear accurate

- **Status**: new
- **Analyzer**: pcb
- **Source**: mini_ads1220_plimsoll.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 4-layer board (F.Cu, In1.Cu, In2.Cu, B.Cu), 17 footprints, fully routed (0 unrouted), 15.12x29.15mm board. Decoupling placement correctly associates C8/C7/C9/C12 near U1 (ADS1220). DFM metrics (0.2mm min track, 0.3mm min drill) are plausible for JLCPCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001139: Completeness falsely reports In4.Cu and In6.Cu missing; actual inner layers In1.Cu and In2.Cu are present but labeled 'extra'

- **Status**: new
- **Analyzer**: gerber
- **Source**: r0_pcb gerbers
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The gbrjob-based completeness check reads layer function codes (Copper,L5,Inr and Copper,L7,Inr) and translates them to In4.Cu/In6.Cu, but the actual files are plimsoll-In1_Cu.gbr and plimsoll-In2_Cu.gbr (named In1.Cu and In2.Cu per stackup). The analyzer should use the stackup name from the job file, not derive layer names from the L-number in the function field.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001140: Layer completeness, alignment, board dimensions, and 4-layer stack all correctly identified; gerber.role and gerber.layer are None for all files despite layer_type being correctly set

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: mini_ads1220_jlcpcb_gerber
- **Created**: 2026-03-23

### Correct
- 9 gerber files, 2 drill files detected. Found layers match 4-layer stack (F.Cu, B.Cu, In1.Cu, In2.Cu, plus mask/silk/edge). Missing F.Paste noted as recommended (not required). Board dimensions 15.12x29.15mm match PCB output exactly. complete=true is correct.

### Incorrect
(none)

### Missed
- All gerber entries have role=None and layer=None even though layer_type is correctly parsed (e.g., 'B.Cu', 'In1.Cu'). If role/layer are supposed to be populated from X2 attributes or filename mapping, they appear to be missing output fields.
  (signal_analysis)

### Suggestions
(none)

---
