# Findings: jjrh/PGA2311 / pga2311

## FND-00001037: SPI bus not aggregated despite SCLK/SDI/CS/SDO nets being present and classified; -5V net classified as 'signal' instead of 'power'; PGA2311 component types and BOM correctly parsed from KiCad 5 le...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pga2311.sch.json
- **Created**: 2026-03-23

### Correct
- 22 components extracted (1 IC, 6 caps, 8 connectors, 3 LEDs, 3 resistors, 1 jumper). Power rails with analog/digital split (+5V/+5VD, GNDA/GNDD) correctly identified. KiCad 5 legacy format parsed without errors.

### Incorrect
- The -5V net is a negative supply rail powering the PGA2311 analog section (connected to VEE/AVSS). It is classified as 'signal' in net_classification instead of 'power' or 'negative_supply'. This is the same class of V- classification bug seen in PDH_photodiode.
  (signal_analysis)

### Missed
- The PGA2311 is an SPI-controlled stereo volume control. Nets SCLK, SDI, CS, SDO are present and individually classified as clock/data/chip_select/data, but bus_analysis.spi is empty []. The analyzer correctly classifies net types but fails to aggregate them into an SPI bus topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001038: KiCad 4-format PCB (file_version=4) correctly parsed with full statistics

- **Status**: new
- **Analyzer**: pcb
- **Source**: pga2311.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 26 footprints all on front side, mixed SMD/THT (13 each), 2-layer, routing complete. DFM tier classified as advanced due to min track/drill metrics.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
