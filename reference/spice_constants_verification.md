# SPICE Part Library Constants Verification

Verification of `spice_part_library.py` constants against external authoritative sources.

## Verification Sources

1. **DigiKey Product Information API v4** (Phase 1, 2026-03-31) — parametric search for GBW, slew rate
2. **Manufacturer PDF datasheets** (Phase 2, 2026-03-31) — 31 PDFs downloaded and read, electrical characteristics tables
3. **DigiKey datasheet downloads** (Phase 3, 2026-03-31) — 11 MOSFET datasheets downloaded via DigiKey API

## Status Summary

### OPAMP_SPECS (49 entries)
- **Datasheet-verified**: 30 (GBW + slew confirmed from PDF or DigiKey parametric)
- **Fixed in Phase 2**: 8 additional errors found and corrected from datasheet reading
- **Acceptable**: 6 (within typ/min/max spread across manufacturers)
- **Unverifiable**: 5 (EOL/special parts)

### LDO_SPECS (35 entries)
- **Datasheet-verified**: 2 (MCP1700, AP2112 — all params confirmed)
- **Fixed in Phase 2**: 3 errors (AMS1117 dropout, LP5907 Iq, TPS7A20 Iq/Iout)
- **Unverified**: 30 (78xx family assumed correct, others need datasheets)

### COMPARATOR_SPECS (9 entries)
- **Datasheet-verified**: 2 (LM311, LM339)
- **Fixed in Phase 2**: LM311 prop_delay (200→165ns), supply (5-36→3.5-30V)
- **Unverified**: 7

### VREF_SPECS (10 entries)
- **Datasheet-verified**: 3 (TL431, REF5050, LM4040)
- **Fixed in Phase 2**: LM4040 vref (2.048V→2.5V, added 3.0/3.3V, removed 10V), TL431 zout
- **Unverified**: 7

### MOSFET_SPECS (10 entries, was 12)
- **Datasheet-verified**: 10 (all Vth, Rdson, Ciss, Vds, Id confirmed from downloaded PDFs)
- **Fixed in Phase 3**: 26 value corrections across 10 parts (Ciss systematically wrong)
- **Removed**: 2 (DMP3150 fictitious part, NTR4101 unverifiable)

### RF/Capacitor tables — unchanged from Phase 1

---

## Phase 2: Datasheet PDF Verification (2026-03-31)

### Errors Found and Fixed

| Part | Parameter | Old Value | New Value | Datasheet | Page |
|------|-----------|-----------|-----------|-----------|------|
| TL072 | slew_vus | 13 | **8** | SLOS080W | p16 §5.9 |
| TL074 | slew_vus | 13 | **8** | SLOS080W | p16 §5.9 |
| LM324 | slew_vus | 0.4 | **0.5** | SLOS066AE | p13 §6.10 |
| OPA2134 | vos_mv | 0.5 | **1.0** | SBOS058B | p7 §5.7 |
| OP07 | vos_mv | 0.075 | **0.06** | SLOS099H | p5 §6.5 |
| OP07 | supply_min | 8 | **6** | SLOS099H | p4 §6.3 |
| OPA1602 | vos_mv | 0.12 | **0.1** | SBOS474B | p3 |
| OPA1602 | supply_min | 9 | **4.5** | SBOS474B | p4 |
| OPA1604 | vos_mv | 0.12 | **0.1** | SBOS474B | p3 (same family) |
| OPA1604 | supply_min | 9 | **4.5** | SBOS474B | p4 |
| TLV9151 | slew_vus | 20 | **21** | SBOS952 | p12 §6.7 |
| AMS1117 | dropout_mv | 1000 | **1300** | AMS1117 DS | p4 |
| LP5907 | iq_ua | 7 | **12** | SNVS543 | p5 §5.5 |
| TPS7A20 | iq_ua | 1 | **6.5** | SLVSDS2 | p6 §5.5 |
| TPS7A20 | iout_max_ma | 200 | **300** | SLVSDS2 | p5 §5.3 |
| LM311 | prop_delay_ns | 200 | **165** | SLCS007K | p6 (H→L typ) |
| LM311 | supply_min | 5 | **3.5** | SLCS007K | p4 §6.3 |
| LM311 | supply_max | 36 | **30** | SLCS007K | p4 §6.3 (36 is abs max) |
| TL431 | zout_ohms | 0.22 | **0.2** | SLVS543S | p6 §6.5 |
| LM4040 | vref default | 2.048 | **2.5** | DS33195 | p1 (no 2.048V variant exists) |
| LM4040 | vref options | 2.5/4.1/5.0/10.0 | **2.5/3.0/3.3/4.1/5.0** | DS33195 | p1 (no 10V, added 3.0/3.3) |
| LM4040 | zout_ohms | 1.0 | **0.5** | DS33195 | p3 (typ for 5.0V) |
| LM4040 | iq_ua | 100 | **60** | DS33195 | p3 (recommended min I_R) |

### TL072/TL074 Slew Rate Note

TI has transitioned the TL07x family to a new die (TL07xH suffix). The current TI datasheet
SLOS080W (rev. July 2025) no longer lists 13 V/µs for any standard variant:
- TL07xC/AC/BC/I: GBW = 3 MHz, **SR = 8 V/µs typ** (p16 §5.9)
- TL07xM (military): GBW = 3 MHz, SR = 5 V/µs typ
- TL07xH (new die): GBW = 5.25 MHz, SR = 20 V/µs typ

The 13 V/µs value was from older TI datasheet revisions. Updated to 8 V/µs to match current
production specs. Affects ~114 SPICE simulation files in the test corpus.

### TL082/TL084 Status — Needs Further Investigation

The TL08x datasheet (SLOS081O) has a complex variant matrix:
- TL08xH: GBW = 5.25 MHz, SR = 20 V/µs typ
- TL08xC standard packages: GBW = 5.25 MHz, SR min = 8, typ = 20 V/µs
- TL08xM / NS/PS: GBW = 3 MHz, SR min = 5

Our current values (GBW = 4 MHz, SR = 13 V/µs) don't appear in the latest TI datasheet.
The traditional 4 MHz spec was from older die revisions. **Not changed yet** — needs manual
review to determine the right representative value since the C-grade now has 5.25 MHz for
most packages.

### NE5532 Slew Rate — Manufacturer Variance

TI's current datasheet (SLOS075K) lists SR = 5 V/µs in the operating characteristics table,
but 9 V/µs appears in the descriptive text. The original Signetics/Philips NE5532 was spec'd
at 9 V/µs. The 5 V/µs may reflect TI's current production die. **Not changed** — 9 V/µs is
the widely used value and matches the original design. Flagged for future manufacturer-specific
variant tables.

---

## Phase 1: DigiKey API Verification (2026-03-31)

### Verified OK via DigiKey (22 entries — GBW + slew match)

| Prefix | Our GBW | DK GBW | Our Slew | DK Slew | DK MPN |
|--------|---------|--------|----------|---------|--------|
| AD817 | 50 MHz | 50 MHz | 350 V/µs | 350 V/µs | AD817ARZ |
| AD8512 | 8 MHz | 8 MHz | 20 V/µs | 20 V/µs | AD8512ARZ |
| AD8605 | 10 MHz | 10 MHz | 5 V/µs | 5 V/µs | AD8605ARTZ |
| AD8676 | 10 MHz | 10 MHz | 2.5 V/µs | 2.5 V/µs | AD8676ARMZ |
| LM741 | 1.5 MHz | 1.5 MHz | 0.5 V/µs | 0.5 V/µs | LM741H |
| LM833 | 15 MHz | 15 MHz | 7 V/µs | 7 V/µs | LM833DR2G |
| MCP6001 | 1 MHz | 1 MHz | 0.6 V/µs | 0.6 V/µs | MCP6001T |
| MCP6002 | 1 MHz | 1 MHz | 0.6 V/µs | 0.6 V/µs | MCP6002T |
| MCP6004 | 1 MHz | 1 MHz | 0.6 V/µs | 0.6 V/µs | MCP6004T |
| MCP601 | 2.8 MHz | 2.8 MHz | 2.3 V/µs | 2.3 V/µs | MCP601T |
| MCP6022 | 10 MHz | 10 MHz | 7 V/µs | 7 V/µs | MCP6022 |
| NE5532 | 10 MHz | 10 MHz | 9 V/µs | 9 V/µs | NE5532DR |
| OP07 | 0.6 MHz | 0.6 MHz | 0.3 V/µs | 0.3 V/µs | OP07CDR |
| OP27 | 8 MHz | 8 MHz | 2.8 V/µs | 2.8 V/µs | OP27GSZ |
| OPA1602 | 35 MHz | 35 MHz | 20 V/µs | 20 V/µs | OPA1602AIDR |
| OPA1612 | 80 MHz | 80 MHz | 27 V/µs | 27 V/µs | OPA1612AIDR |
| OPA2134 | 8 MHz | 8 MHz | 20 V/µs | 20 V/µs | OPA2134UA |
| OPA2333 | 0.35 MHz | 0.35 MHz | 0.16 V/µs | 0.16 V/µs | OPA2333AIDR |
| OPA2340 | 5.5 MHz | 5.5 MHz | 6 V/µs | 6 V/µs | OPA2340UA |
| OPA340 | 5.5 MHz | 5.5 MHz | 6 V/µs | 6 V/µs | OPA340NA |
| RC4558 | 3 MHz | 3 MHz | 1.7 V/µs | 1.7 V/µs | RC4558DR |
| TSV912 | 8 MHz | 8 MHz | 4.5 V/µs | 4.5 V/µs | TSV912IQ2T |

### Verified OK via PDF datasheets (8 additional entries)

| Prefix | GBW | Slew | DS Source | Page |
|--------|-----|------|-----------|------|
| OPA1678 | 16 MHz | 9 V/µs | SBOS862 | p8 §6.7 |
| OPA4991 | 4.5 MHz | 21 V/µs | OPA991 DS | p12 §6.7 |
| OPA4202 | 1 MHz | 0.35 V/µs | OPA4202 DS | p10 §6.7 |
| OPA1604 | 35 MHz | 20 V/µs | SBOS474B | p3 |
| LM2904 | 0.7 MHz | 0.3 V/µs | LM2904V DS | p11 §5.8 |
| TL072 | 3 MHz | 8 V/µs | SLOS080W | p16 §5.9 |
| TL074 | 3 MHz | 8 V/µs | SLOS080W | p16 §5.9 |
| LM324 | 1 MHz | 0.5 V/µs | SLOS066AE | p13 §6.10 |

### Verified OK via PDF — LDO/Comparator/VREF

| Part | Category | Key Params Verified | DS Source |
|------|----------|---------------------|-----------|
| MCP1700 | LDO | dropout=178mV, Iq=1.6µA, Iout=250mA | DS20001826F p3 |
| AP2112 | LDO | dropout=250mV, Iq=55µA, Iout=600mA | AP2112 DS p8 |
| LM339 | Comparator | prop_delay=1300ns, open_collector | SLCS006Z p12 §6.14 |
| REF5050 | VREF | Vref=5.0V, tempco=3ppm/C | SBOS410O p7 §6.5 |

### Previously Fixed Errors (Phase 1 — DigiKey verification)

| Prefix | Issue | Corrected To | Source |
|--------|-------|-------------|--------|
| AD8607 | Confused with AD8605 | GBW=0.4MHz, slew=0.1 | AD8603/8607/8609 DS |
| OPA4202 | Completely wrong (was 20MHz) | GBW=1MHz, slew=0.35 | OPA4202 DS |
| OPA1604 | Swapped with OPA1602 | GBW=35MHz, slew=20 | SBOS493 |
| OPA1678 | Wrong (was 24MHz/13) | GBW=16MHz, slew=9 | SBOS862 |
| OPA4991 | Slew wrong (was 1.3) | slew=21 | OPA991 DS |
| TLV9151 | Both wrong (was 3MHz/1.5) | GBW=4.5MHz, slew=20→21 | SBOS952 |
| LM2904 | Was same as LM358 | GBW=0.7MHz, slew=0.3 | LM2904V DS |

### Minor Discrepancies (acceptable — within typ/min/max spread)

| Prefix | Issue | Our Value | DK/DS Value | Verdict |
|--------|-------|-----------|-------------|---------|
| ADA4528 | Slew: 0.4 vs 0.5 | slew=0.4 | slew=0.5 | Acceptable — within min/typ spread |
| ADA4610 | Slew: 25 vs 61 | slew=25 | slew=61 | Needs DS — 61 may be max or -2 variant |
| ADA4898 | GBW: 65 vs 50 | GBW=65MHz | GBW=50MHz | Needs DS — 65 may be -1 variant |
| LM358 | Slew: 0.3 vs 0.6 | slew=0.3 | slew=0.6 | Acceptable — varies by manufacturer |
| MC4558 | Slew: 1.7 vs 2.2 | slew=1.7 | slew=2.2 | Acceptable — STMicro vs JRC variant |
| NJM4558 | Slew: 1.7 vs 1.0 | slew=1.7 | slew=1.0 | Needs DS — NJM variant may differ |

### Still Unverified (EOL/special parts)

| Prefix | Notes |
|--------|-------|
| EL2018 | Renesas (formerly Intersil) current feedback amp — EOL. GBW=160MHz, slew=1500. |
| INA219 | TI current/power monitor — not a standard opamp. Internal GBW (0.5MHz). |
| INA226 | TI current/power monitor — same as INA219. |
| LM6361 | National Semi fast opamp — EOL. GBW=50MHz, slew=300. |
| uPC324 | NEC/Renesas LM324 equivalent. GBW=1MHz, slew=0.4. Assumed correct. |

---

## RF_IC_BANDS Verification (CONST-251)

Source: DigiKey parametric data. All 10 verified entries match. 6 unverified (not in DK or returned wrong product).

| Prefix | Our Freq | DK Freq | Status |
|--------|----------|---------|--------|
| cc2500 | 2.4 GHz | 2.4 GHz | OK |
| cc1101 | 868 MHz | 300-928 MHz (multi-band) | OK (868 is default ISM) |
| sx127 | 868 MHz | 137-1020 MHz | OK (868 is LoRa default) |
| sx126 | 868 MHz | 862-930 MHz | OK |
| nrf24 | 2.4 GHz | 2.4 GHz | OK |
| nrf52 | 2.4 GHz | 2.4 GHz | OK |
| esp32 | 2.4 GHz | 2.412-2.484 GHz | OK |
| at86rf | 2.4 GHz | 2.4 GHz | OK |
| si446 | 868 MHz | 142-1050 MHz | OK (868 is default) |
| nrf53 | 2.4 GHz | (same family as nrf52) | OK |
| a7105, bk4819, rfm6, rfm9, si4432, si4463 | various | not checked | Assumed correct |

## RF_ROLE_GAIN_DB Verification (CONST-252)

Engineering heuristics, not datasheet values. All within reasonable ranges.

| Role | Gain | Assessment |
|------|------|-----------|
| amplifier | +15 dB | OK — typical LNA gain 12-20 dB |
| switch | -0.5 dB | OK — typical RF switch IL 0.3-1 dB |
| filter | -1.5 dB | OK — typical SAW/BAW IL 1-3 dB |
| balun | -0.5 dB | OK — typical balun IL 0.3-1 dB |
| mixer | -7 dB | OK — typical passive mixer CL 6-8 dB |
| attenuator | -6 dB | OK — typical fixed pad |
| coupler | -10 dB | OK — typical coupler coupling factor |
| power_detector | -20 dB | OK — sampling loss |
| freq_multiplier | -10 dB | OK — typical CL |
| transceiver | 0 dB | OK — terminal device |

## _CAP_ESL Verification (CONST-190)

All 7 entries verified against Murata GRM / TDK C series typical values. All OK.

| Package | Our ESL | Reference Range | Status |
|---------|---------|-----------------|--------|
| 0402 | 0.3 nH | 0.2-0.5 nH | OK |
| 0603 | 0.5 nH | 0.4-0.8 nH | OK |
| 0805 | 0.7 nH | 0.5-1.0 nH | OK |
| 1206 | 1.0 nH | 0.7-1.5 nH | OK |
| 1210 | 1.0 nH | 0.8-1.5 nH | OK |
| 1812 | 1.2 nH | 1.0-2.0 nH | OK |
| 2220 | 1.5 nH | 1.5-3.0 nH | OK |

## _CAP_ESR_TABLE Verification (CONST-184)

9 of 16 entries verified against Murata/TDK typical values. All within range.

| Package | Cap Range | Our ESR | Reference | Status |
|---------|-----------|---------|-----------|--------|
| 0402 | ≤10nF | 5.0 Ω | 2-10 Ω | OK |
| 0402 | ≤100nF | 1.0 Ω | 0.5-2 Ω | OK |
| 0603 | ≤10nF | 2.0 Ω | 1-5 Ω | OK |
| 0603 | ≤100nF | 0.5 Ω | 0.2-1 Ω | OK |
| 0603 | ≤1µF | 0.15 Ω | 0.05-0.3 Ω | OK |
| 0805 | ≤100nF | 0.3 Ω | 0.1-0.5 Ω | OK |
| 0805 | ≤1µF | 0.08 Ω | 0.03-0.15 Ω | OK |
| 1206 | ≤1µF | 0.1 Ω | 0.03-0.2 Ω | OK |
| Others | large C | low mΩ | not checked | Reasonable |

---

## Phase 3: MOSFET_SPECS Verification (2026-03-31)

Source: 11 datasheets downloaded via DigiKey API, read with PDF tool.

### Corrections Applied (26 value fixes across 10 parts)

| Part | Param | Old | New | Datasheet Source |
|------|-------|-----|-----|-----------------|
| BSS138 | rdson | 3.5Ω | **2.5Ω** | ON Semi BSS138, max@Vgs=10V |
| BSS138 | ciss | 30pF | **27pF** | typ |
| BSS138 | id | 0.2A | **0.22A** | |
| AO3400 | vth | 1.4V | **1.05V** | AOS AO3400A, typ |
| AO3400 | rdson | 40mΩ | **27mΩ** | max@Vgs=10V |
| AO3400 | ciss | 800pF | **630pF** | typ |
| SI2302 | vth | 0.7V | **0.63V** | Vishay SI2302CDS, midpoint 0.4-0.85V |
| SI2302 | rdson | 100mΩ | **57mΩ** | max@Vgs=4.5V |
| SI2302 | ciss | 260pF | **340pF** | from graph |
| SI2302 | id | 2.6A | **2.9A** | |
| IRLML2502 | vth | 0.8V | **0.9V** | Infineon, midpoint 0.6-1.2V |
| IRLML2502 | rdson | 40mΩ | **45mΩ** | max@Vgs=4.5V |
| IRLML2502 | ciss | 900pF | **740pF** | typ |
| IRLML6344 | rdson | 30mΩ | **29mΩ** | Infineon, max@Vgs=4.5V |
| IRLML6344 | ciss | 1200pF | **650pF** | typ (was 85% too high) |
| DMN3150 | vth | 1.5V | **0.92V** | Diodes DMN3150L, typ |
| DMN3150 | rdson | 100mΩ | **72mΩ** | max@Vgs=4.5V |
| DMN3150 | ciss | 170pF | **305pF** | typ |
| BSS84 | vth | -1.3V | **-1.6V** | Nexperia BSS84AKW, typ |
| BSS84 | rdson | 10Ω | **7.5Ω** | max@Vgs=-10V |
| BSS84 | ciss | 45pF | **24pF** | typ |
| BSS84 | id | -0.13A | **-0.15A** | |
| SI2301 | rdson | 0.15Ω | **0.112Ω** | Vishay SI2301CDS, max@Vgs=-4.5V |
| SI2301 | ciss | 320pF | **405pF** | typ |
| AO3401 | vth | -1.4V | **-0.9V** | AOS AO3401A, typ |
| AO3401 | ciss | 600pF | **645pF** | typ |

### Removed Entries (2)

| Part | Reason |
|------|--------|
| DMP3150 | Not a real part — no Diodes Inc product with this MPN exists |
| NTR4101 | ON Semi blocks datasheet downloads; cannot verify against authoritative source |

### Convention: Rdson uses max spec

All Rdson values use the datasheet **maximum** at rated Vgs (typically 4.5V for logic-level, 10V for standard). This gives worst-case behavioral model behavior, which is appropriate for SPICE simulation (avoids optimistic switching predictions).
