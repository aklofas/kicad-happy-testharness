"""Manufacturer identification from MPN prefix patterns.

Maps well-known MPN prefixes to manufacturer names. Used by the datasheet
store to enrich records with manufacturer metadata.
"""

# Prefix → manufacturer name. Ordered longest-first for matching priority.
_MFR_PREFIXES = [
    # Texas Instruments
    ("TPS", "Texas Instruments"), ("TLV", "Texas Instruments"),
    ("LM", "Texas Instruments"), ("OPA", "Texas Instruments"),
    ("INA", "Texas Instruments"), ("TXB", "Texas Instruments"),
    ("SN", "Texas Instruments"), ("BQ", "Texas Instruments"),
    ("DRV", "Texas Instruments"), ("ADS", "Texas Instruments"),
    ("MSP", "Texas Instruments"), ("TMS", "Texas Instruments"),
    # STMicroelectronics
    ("STM32", "STMicroelectronics"), ("STM8", "STMicroelectronics"),
    ("ST", "STMicroelectronics"), ("L78", "STMicroelectronics"),
    ("L79", "STMicroelectronics"), ("LD", "STMicroelectronics"),
    # Analog Devices / Maxim
    ("AD", "Analog Devices"), ("ADP", "Analog Devices"),
    ("ADA", "Analog Devices"), ("ADM", "Analog Devices"),
    ("LTC", "Analog Devices"), ("LT", "Analog Devices"),
    ("MAX", "Analog Devices"),
    # Microchip / Atmel
    ("ATMEGA", "Microchip"), ("ATTINY", "Microchip"),
    ("AT", "Microchip"), ("MCP", "Microchip"),
    ("PIC", "Microchip"), ("SAMD", "Microchip"),
    ("SAM", "Microchip"),
    # NXP
    ("NX", "NXP"), ("PCA", "NXP"), ("PCF", "NXP"),
    ("TJA", "NXP"), ("S32", "NXP"),
    # ON Semiconductor / onsemi
    ("NCP", "onsemi"), ("NCV", "onsemi"), ("NCS", "onsemi"),
    ("FAN", "onsemi"), ("CAT", "onsemi"),
    # Infineon / Cypress
    ("IFX", "Infineon"), ("IRF", "Infineon"), ("IR", "Infineon"),
    ("CY", "Infineon"),
    # Renesas / Intersil / IDT
    ("ISL", "Renesas"), ("R5F", "Renesas"), ("RX", "Renesas"),
    # Vishay
    ("SI", "Vishay"), ("SiR", "Vishay"),
    # ROHM
    ("BD", "ROHM"), ("BR", "ROHM"), ("BU", "ROHM"),
    # Diodes Inc
    ("AP", "Diodes Inc"), ("DMP", "Diodes Inc"), ("DMG", "Diodes Inc"),
    # Espressif
    ("ESP32", "Espressif"), ("ESP8266", "Espressif"),
    # Nordic
    ("NRF", "Nordic Semiconductor"),
    # Murata
    ("GRM", "Murata"), ("BLM", "Murata"),
    # TDK
    ("MLZ", "TDK"), ("MPZ", "TDK"),
    # Samsung
    ("CL", "Samsung"), ("S2M", "Samsung"),
    # Wurth
    ("WE-", "Wurth"),
    # Silicon Labs
    ("EFM32", "Silicon Labs"), ("EFR32", "Silicon Labs"),
    ("SI44", "Silicon Labs"), ("SI10", "Silicon Labs"),
    ("CP21", "Silicon Labs"),
    # Bosch
    ("BMP", "Bosch"), ("BMI", "Bosch"), ("BME", "Bosch"),
    # Raspberry Pi
    ("RP2", "Raspberry Pi"),
]


def guess_manufacturer(mpn: str) -> str:
    """Guess manufacturer from MPN prefix. Returns name or None."""
    if not mpn:
        return None
    upper = mpn.upper()
    for prefix, mfr in _MFR_PREFIXES:
        if upper.startswith(prefix.upper()):
            return mfr
    return None


def guess_manufacturers_for_record(record: dict) -> list:
    """Return list of guessed manufacturer names for a manifest record.

    Checks all MPNs in the record. Returns deduplicated list.
    """
    seen = set()
    result = []
    for m in record.get("mpns", []):
        mfr = guess_manufacturer(m.get("mpn", ""))
        if mfr and mfr not in seen:
            result.append(mfr)
            seen.add(mfr)
    return result
