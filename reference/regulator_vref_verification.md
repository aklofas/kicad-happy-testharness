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
