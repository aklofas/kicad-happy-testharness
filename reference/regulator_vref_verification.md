# _REGULATOR_VREF Table Verification

Verification of `kicad_utils.py` `_REGULATOR_VREF` table against manufacturer datasheets and product pages.
Verified: 2026-03-31. Sources: TI/ADI/Maxim/Richtek/MPS/Diodes/ST/ON/Renesas product pages and datasheets.

## Summary

- **Before**: 96 entries, many unverified or wrong
- **After**: 63 entries, all verified against datasheets or well-established values
- **Fixed**: 7 wrong values corrected
- **Removed**: 33 entries (nonexistent parts, mixed families, fixed-output-only, unverified)

## Value Corrections (7)

| Prefix | Old Value | New Value | Part | Source |
|--------|-----------|-----------|------|--------|
| LM258/LM259 | 1.285V | **1.23V** | LM2596/LM2585 | TI LM2596 datasheet |
| LT361/LT362 | 0.8V | **0.6V** | LTC3610/LTC3620 | ADI LTC3610 datasheet |
| LT871 | 1.0V | **1.213V** | LT8710 | ADI LT8710 datasheet |
| ISL850 | 0.6V | **0.8V** | ISL85003 | Renesas ISL85003 datasheet |
| RT2875 | 0.8V | **0.6V** | RT2875A/B | Richtek RT2875 datasheet |
| NCP1 → NCP1117 | 0.8V | **1.25V** | NCP1117 | ON Semi NCP1117 datasheet (prefix narrowed to avoid matching other NCP1xxx parts) |
| MAX1709 | 1.24V | **1.25V** | MAX1709 | ADI MAX1709 datasheet |

## Removed Entries (33)

### Nonexistent parts (no matching products in manufacturer catalogs)
- `LT801`, `LT802`, `LT872` — no ADI switching regulators match these prefixes

### Mixed families (prefix matches parts with different Vrefs)
- `TPS542` (0.6V) — TPS54240 has 0.8V FB, TPS54200 varies
- `TPS543` (0.6V) — TPS54340 has 0.8V FB
- `TPS544` (0.6V) — architecture varies across family
- `TPS55` (0.6V) — TPS55340 has 1.229V FB (boost/SEPIC)
- `TPS40` (0.6V) — TPS40200 has 0.7V FB, TPS40057 has 0.7V FB
- `TPS6208` (0.6V) — TPS62080 has 0.45V FB
- `TPS6209` (0.6V) — TPS62090 has 0.8V FB
- `TPS6211`-`TPS6215` (0.6V) — TPS62130/62150 have 0.8V FB
- `TPS6102`/`TPS6103` (0.595V) — TPS61020 datasheet shows 0.5V, 0.595V unverified
- `LT364`/`LT365` (1.22V) — LT364x family has 0.8-1.265V; LT365x are battery chargers
- `LTC34` (0.8V) — LTC3400 has 1.23V, family varies widely
- `LTM82` (0.6V) — LTM8025 has 0.79V, LTM8020 has 1.25V
- `MP8` (0.8V) — MP8756 has 0.6V FB
- `AP6` (0.6V) — AP62200=0.8V, AP6502=0.925V, AP64501=0.8V (too broad)
- `LM516` (0.8V) — LM5160 has 2.0V FB

### Fixed-output-only parts (no external FB pin, Vref not applicable)
- `MIC55` (MIC5501-5504), `MCP170` (MCP1700), `NCV4` (NCV4274/75)
- `TPS7B` (TPS7B69), `LM340` (78xx family, redundant with `LM78`)
- `TLV620`/`TLV621` (unverified, uncertain architecture)

### Other
- `LM260`/`LM261` — LM26001 Vref is 1.234V vs our 1.21V, unclear which variant dominates
- `LMZ3` — LMZ31710 uses RSET method, FB reference unclear

## Verified Entries (63 retained)

### TI Switching Regulators
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| TPS6100 | 0.5V | TPS61000/01 | TI datasheet |
| TPS5430/5450/5410 | 1.221V | TPS543x/541x | TI datasheet |
| TPS54160/54260/54360 | 0.8V | TPS541x0-543x0 | TI datasheet |
| TPS54040/54060 | 0.8V | TPS540x0 | TI datasheet |
| TPS56xx | 0.6V | TPS560200 | TI datasheet |
| TPS6300/6301 | 0.5V | TPS63000/01 | TI datasheet |
| TPS6310 | 0.5V | TPS631000 | TI SLVSEK5 |
| LMR514/516 | 0.8V | LMR51440/60 | TI datasheet |
| LMR336/338 | 1.0V | LMR33630/60 | TI datasheet |
| LMR380 | 1.0V | LMR38010 | TI SNVSB89 |
| LM258/259 | 1.23V | LM2596/2585 | TI datasheet |
| LMZ2 | 0.795V | LMZ23610 | TI datasheet |
| LM614/619 | 1.0V | LM61495 | TI datasheet |

### TI LDOs
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| TLV759 | 0.55V | TLV759P | TI datasheet |
| TPS7A | 1.19V | TPS7A49 | TI datasheet (1.185V typ, 1.19 is approx) |

### Analog Devices / Linear Technology
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| LT361/362 | 0.6V | LTC3610/3620 | ADI datasheet |
| LT810/811 | 0.97V | LT8610/8614 | ADI datasheet |
| LT860/862 | 0.97V | LT8640/8620 | ADI datasheet |
| LT871 | 1.213V | LT8710 | ADI datasheet |
| LTM46 | 0.6V | LTM4600 | ADI datasheet |

### Richtek / MPS / Silergy
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| RT5/RT6 | 0.6V | RT5785/RT6150 | Richtek datasheets |
| RT2875 | 0.6V | RT2875A/B | Richtek datasheet |
| MP1/MP2 | 0.8V | MP1584/MP2315 | MPS datasheets |
| SY8 | 0.6V | SY8089 | Silergy datasheet |

### Microchip / Diodes / ST / ON Semi
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| MIC29 | 1.24V | MIC29150/29300 | Microchip datasheet |
| AP736 | 0.8V | AP7365 adj | Diodes datasheet |
| AP73 | 0.6V | AP7362/63 | Diodes datasheet |
| AP2112 | 0.8V | AP2112 adj | Diodes datasheet |
| AP3015 | 1.23V | AP3015A | Diodes datasheet |
| LD1117/LDL1117/LD33 | 1.25V | LD1117 family | ST datasheet |
| NCP1117 | 1.25V | NCP1117 | ON Semi datasheet |

### Maxim / Renesas
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| MAX5035/5033 | 1.22V | MAX5035/33 | ADI/Maxim datasheet |
| MAX1771 | 1.5V | MAX1771 | ADI/Maxim datasheet |
| MAX1709 | 1.25V | MAX1709 | ADI/Maxim datasheet |
| MAX17760 | 0.8V | MAX17760 | ADI/Maxim datasheet |
| ISL854 | 0.6V | ISL85410 | Renesas datasheet |
| ISL850 | 0.8V | ISL85003 | Renesas datasheet |

### XLSEMI
| Prefix | Vref | Part Family | Source |
|--------|------|-------------|--------|
| XL70 | 1.25V | XL7015 | XLSEMI datasheet |

### Generic (well-established values)
| Prefix | Vref | Notes |
|--------|------|-------|
| LM317/LM337 | 1.25V | Standard 3-terminal adjustable regulator |
| AMS1117/AMS1085 | 1.25V | 1117 family |
| LM78/LM79 | 1.25V | 78xx/79xx internal bandgap |
| LM1117 | 1.25V | TI 1117 family |

## Wave 12b update (2026-11-17, product `7ed10f3e`, table now in `kicad_core/parts.py`)

Every row Wave 12b added or changed was checked by the harness against the manufacturer datasheet for that exact part number (the part number found in the text before the value was read). 48 rows verified, 0 wrong. analog.com was unreachable; the ADI rows were read from ADI's own datasheets fetched through RS / LCSC copies (LT8640: ADI's Japanese edition only). Where the revision read differs from the one the product cites, the values are the same.

**Removed keys** (confirmed absent by import): TPS6102, TPS6103, TPS561, TPS562, TPS5632, LT860, LT810, LT811, LT361, LT362, TPS5654. The mistyped `LT361`/`LT362` (meant LTC3610/LTC3620) and `LT810`/`LT811` (meant LT8610/LT8614) never matched a real part; `LT860` gave 0.97 V to every LT8601-LT8609S part and is replaced by per-member rows.

| Key | Vref (V) | Source |
|-----|----------|--------|
| TPS61020 | 0.5 | TI SLVS451G (Dec 2014) p5 Electrical Characteristics: 'TPS61020, TPS61028 and TPS61029 feedback voltage VFB 490/500/510 mV' |
| TPS61028 | 0.5 | TI SLVS451G (Dec 2014) p5 Electrical Characteristics: 'TPS61020, TPS61028 and TPS61029 feedback voltage VFB 490/500/510 mV' |
| TPS61029 | 0.5 | TI SLVS451G (Dec 2014) p5 Electrical Characteristics: 'TPS61020, TPS61028 and TPS61029 feedback voltage VFB 490/500/510 mV' |
| TPS61021 | 0.795 | TI SLVSDM0 (Jun 2016, TPS61021A; TI's only TPS61021 part) p5: 'VREF Reference voltage at the FB pin, PWM mode 775/795/815 mV' |
| TPS61022 | 0.6 | TI SLVSDX7D (Jul 2021) p5: 'VREF Reference voltage at the FB pin, PWM mode 585/600/615 mV' |
| TPS61023 | 0.595 | TI SLVSF14B p5 (local datasheets/TPS61023-020c107a.pdf): 'VREF Reference voltage at the FB pin, PWM mode 580/595/610 mV' |
| TPS61030 | 0.5 | TI SLUS534G (Mar 2015) p5: 'VFB TPS61030 feedback voltage 490/500/510 mV' |
| TPS561201 | 0.768 | TI SLVSC95A (Apr 2017, TPS561201/TPS561208) p5: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS561208 | 0.768 | TI SLVSC95A (Apr 2017, TPS561201/TPS561208) p5: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS561243 | 0.6 | TI SLUSFG9A (local datasheets/TPS561243DRLR-a3f0fb3d.pdf) p5: 'VFB FB voltage TJ = 25C 591/600/609 mV' |
| TPS562200 | 0.765 | TI SLVSCB0E (May 2023, TPS562200/TPS563200) p7: 'VFB(TH) VFB threshold voltage, TA = 25C, VO = 1.05 V, continuous mode operation 758/765/772 mV' (also SLVSCB0D local) |
| TPS563200 | 0.765 | TI SLVSCB0E (May 2023, TPS562200/TPS563200) p7: 'VFB(TH) VFB threshold voltage, TA = 25C, VO = 1.05 V, continuous mode operation 758/765/772 mV' (also SLVSCB0D local) |
| TPS562201 | 0.768 | TI SLVSD91D (Sep 2024, TPS562201/TPS562208) p5: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS562208 | 0.768 | TI SLVSD91D (Sep 2024, TPS562201/TPS562208) p5: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS562202 | 0.804 | TI SLUSE28 (Sep 2020) p6: 'VFBTH Continuous mode operation at TA = 25C 788/804/820 mV'; TPS562202S SLUSED6 p5: 792/804/816 mV |
| TPS562207 | 0.804 | TI SLUSDR7B (Apr 2021) p6: 'VFBTH VFB threshold voltage TA = 25C 788/804/820 mV' |
| TPS562212 | 0.6 | TI SLUSEI0 (Oct 2021) p5: 'VFB FB voltage TJ = 25C 0.594/0.6/0.606 V' |
| TPS563201 | 0.768 | TI SLVSD90B (Sep 2024, TPS563201/TPS563208) p6: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS563208 | 0.768 | TI SLVSD90B (Sep 2024, TPS563201/TPS563208) p6: 'VFBTH VFB threshold voltage, VO = 1.05 V, continuous mode operation 749/768/787 mV' |
| TPS563202S | 0.806 | TI SLUSED8 (Oct 2020) p6: 'VFBTH VFB threshold voltage, Continuous mode operation at TA = 25C 794/806/818 mV' |
| TPS563240 | 0.6 | TI SLVSE74A (Aug 2019) p5: 'VFB FB voltage, Continuous mode operation, TJ = 25C 594/600/606 mV' |
| TPS563249 | 0.6 | TI SLVSE54A (Dec 2018) p5: 'VFB FB voltage TJ = 25C 594/600/606 mV' |
| TPS564247 | 0.6 | TI SLUSEN2 (Apr 2022) p5: 'VREF FB voltage TJ = 25C 594/600/606 mV' |
| TPS564257 | 0.6 | TI SLUSEQ6A (local datasheets/TPS564257-43a9f2d6.pdf) p5: 'VREF FB voltage TJ = -40C to 125C 591/600/609 mV' |
| TPS5652 | 0.6 | TI SLUSEN1A (TPS565242/TPS565247, local datasheets/TPS565242DRLR-3bcea882.pdf) p5: 'VREF FB voltage TJ = 25C 594/600/606 mV'. Family-prefix key: TPS565201/208 (760 mV) are carved out by their own keys |
| TPS565201 | 0.76 | TI SLVSE71 (Sep 2017) p5: 'VFBTH VFB threshold voltage 753/760/767 mV' |
| TPS565208 | 0.76 | TI SLVSE72B (Jun 2018) p5: 'VFBTH VFB threshold voltage 753/760/767 mV' |
| LMR51606 | 0.8 | TI SLUSEY1B (Dec 2023, LMR51606/LMR51610) p5 §6.5: 'Vfb Reference voltage 0.788/0.8/0.812 V' |
| LMR51610 | 0.8 | TI SLUSEY1B (Dec 2023, LMR51606/LMR51610) p5 §6.5: 'Vfb Reference voltage 0.788/0.8/0.812 V' |
| LMR33640 | 1.0 | TI SNVSB99C (Nov 2020) p6: 'VFB Feedback voltage; ADJ option 0.985/1/1.015 V' (only ADDA/DDDA orderables, both adjustable) |
| LM2731 | 1.23 | TI SNVS217G (Sep 2015) p5: 'VFB Feedback Pin Reference Voltage VIN = 3 V, TJ = 25C 1.230 V (1.205-1.255)' |
| LM27313 | 1.23 | TI SNVS487E (Jan 2015) p5: 'VFB Feedback Pin Reference Voltage VIN = 3 V 1.230 V (1.205-1.255)' |
| HX711 | 1.25 | Avia HX711 English datasheet (local datasheets/HX711-346d43c4.pdf) p3 Table 2 Key Electrical Characteristics: 'Reference bypass (VBG) 1.25 V'; p4: 'VAVDD=VBG*(R1+R2)/R1' |
| LTC3610 | 0.6 | ADI LTC3610 Rev A (3610fa, RS-hosted copy nonprod.docs.rs-online.com/19d1/0900766b80b08a18.pdf; analog.com unreachable) p2: 'VFB Feedback Reference Voltage ITH = 1.2V 0.594/0.600/0.606 V' |
| LTC3620 | 0.6 | ADI LTC3620 Rev A (3620fa, via LCSC C685295) p2: 'VFB Regulated Feedback Voltage LTC3620 0.594/0.6/0.606 V' |
| LT8610 | 0.97 | ADI LT8610 Rev A (8610fa, via LCSC C459711) p2: 'Feedback Reference Voltage VIN = 6V, ILOAD = 0.5A 0.964/0.970/0.976 V'; LT8610A/AB Rev C (local) p3 same |
| LT8614 | 0.97 | ADI LT8614 Rev E (via LCSC C107998) p3: 'Feedback Reference Voltage VIN = 6V, ILOAD = 0.5A 0.964/0.970/0.976 V' |
| LT8640 | 0.97 | ADI LT8640/LT8640-1 Rev A Japanese edition (8640fa, via LCSC C580327; analog.com unreachable) p3: VFB row 'VIN = 6V ILOAD = 0.5A 0.964/0.970/0.976 V'. LT8640A / LT8640S not checked |
| LT862 | 0.97 | ADI LT8620 Rev A (8620fa, via LCSC C580319) p3: 'Feedback Reference Voltage VIN = 6V, ILOAD = 0.5A 0.964/0.970/0.976 V' (row unchanged in 12b; prefix also covers LT8621-LT8629, not checked) |
| LT8606 | 0.778 | ADI LT8606/LT8606B Rev D ($D/datasheets/LT8606EMSE.pdf) p3: 'Feedback Reference Voltage MSOP VIN = 6V, ILOAD = 100mA 0.774/0.778/0.782 V' |
| LT8607 | 0.778 | ADI LT8607/LT8607B Rev D ($D/datasheets/LT8607EMSE.pdf) p3: 'Feedback Reference Voltage LT8607 MSOP 0.774/0.778/0.782 V' |
| LT8608 | 0.778 | ADI LT8608/LT8608B Rev D ($D/datasheets/LT8608EMSE.pdf) p3: 'Feedback Reference Voltage MSOP 0.774/0.778/0.782 V' |
| LT8608S | 0.774 | ADI LT8608S Rev 0 (via LCSC C7455756) p2: 'Feedback Reference Voltage VIN = 6V, ILOAD = 100mA, 25C 0.770/0.774/0.778 V' |
| LT8609 | 0.782 | ADI LT8609/LT8609A/LT8609B Rev J ($D/datasheets/LT8609EMSE.pdf) p4: 'Feedback Reference Voltage LT8609/LT8609A 0.778/0.782/0.786 V; LT8609B 0.772/0.782/0.792 V' |
| LT8609S | 0.774 | ADI LT8609S Rev D (via LCSC C580305) p3: 'Feedback Reference Voltage VIN = 6V, ILOAD = 100mA 0.770/0.774/0.778 V' |
| TPS73101 | 1.204 | TI SBVS034P (Apr 2026) p5: 'VFB TJ = 25C 1.198/1.204/1.210 V' (local SBVS034O same) |
| TPS79301 | 1.225 | TI SLVS348N (Jan 2025): 'VREF Internal reference (TPS79301) 1.201/1.225/1.25 V'; SLVS348K (local) p2: 'VFB Internal reference (TPS79301) 1.201/1.225/1.250 V' |
| LM5122 | 1.2 | TI SNVS954H (Jun 2017) p8: 'VREF FB reference voltage, Measured at FB, VFB = VCOMP 1.188/1.2/1.212 V' |

Other Wave 12b tables verified the same way: `_FIXED_OUTPUT_PARTS` 8/8, `_FIXED_SUFFIX_FAMILIES` additions 7/7, `_NCP1117_VOLTS` 9/9, `_NCP1117LP_VOLTS` 5/5, `_ADI_FIXED_CODES` 4/4, the RECOM R-78 decode (11 series), `_KNOWN_FREQS` LM2675 260 kHz and MIC23050 4 MHz. LM2575 `-12`/`-15` cite SNVS106E only (TI's `lm2575.pdf` link serves SLVS569F, an adjustable-only part).
