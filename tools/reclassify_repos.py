#!/usr/bin/env python3
"""Reclassify repos from 'Miscellaneous KiCad projects' into specific categories.

Uses detector data from repo_catalog.json, GitHub topics from validated.json,
and repo name/description keyword matching to assign more specific categories
to repos currently in Miscellaneous.

Scoring approach:
  - Topic match (GitHub topic):     +3
  - Description keyword match:      +2
  - Repo name keyword match:        +2
  - Detector fires (strong signal): +3
  - Detector fires (supporting):    +1
  - Tag match (catalog tag):        +1
  - Combination bonuses:            +1-3 for multi-signal convergence

A repo is reclassified if its best category score >= min_score (default: 2).

Usage:
    python3 reclassify_repos.py --dry-run          # Show proposed changes
    python3 reclassify_repos.py --apply             # Edit repos.md
    python3 reclassify_repos.py --stats             # Show category distribution
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
REPOS_MD = HARNESS_DIR / "repos.md"
CATALOG_FILE = HARNESS_DIR / "reference" / "repo_catalog.json"
VALIDATED_FILE = HARNESS_DIR / "results" / "validated.json"

MISC_CATEGORY = "Miscellaneous KiCad projects"

# --- Classification rules ---
#
# Each rule is a dict with:
#   category:        Target category name (must exist in repos.md)
#   name_patterns:   Regex patterns matched against repo name (owner/name -> name part)
#   desc_patterns:   Regex patterns matched against description text
#   topic_keywords:  GitHub topic strings (exact match, case-insensitive)
#   strong_detectors: {detector: min_count} — distinctive detectors, +3 each
#   support_detectors: {detector: min_count} — common detectors, +1 each
#   tags:            Catalog tags that score +1 each
#   combo_bonus:     List of (required_signals, bonus_points) where required_signals
#                    is a set of signal names that must all be present to get bonus
#
# Signal names used in combo_bonus:
#   "name:X" — name pattern X matched
#   "desc:X" — desc pattern X matched
#   "det:X"  — detector X fired
#   "topic:X" — topic X matched
#   "tag:X"  — tag X matched

CLASSIFICATION_RULES = [
    # --- MCU family categories ---
    {
        "category": "ESP32",
        "name_patterns": [r"esp32|esp8266|esp\d+|esphome"],
        "desc_patterns": [r"esp32|esp8266|esp\-?idf|esphome|espressif"],
        "topic_keywords": ["esp32", "esp8266", "esp-idf", "esphome", "espressif",
                           "esp32-s2", "esp32-s3", "esp32-c3", "esp32-c6"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
    {
        "category": "STM32",
        "name_patterns": [r"stm32|stm\d+[fhgl]"],
        "desc_patterns": [r"stm32|stm\d+[fhgl]"],
        "topic_keywords": ["stm32", "stm32f", "stm32h", "stm32l", "stm32g",
                           "stm32f4", "stm32f1", "stm32h7", "stm8"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
    {
        "category": "RP2040 / Raspberry Pi",
        "name_patterns": [r"rp2040|rp2350|raspberry.?pi|rpi\b|pico\b|pihat|pi.?hat"],
        "desc_patterns": [r"rp2040|rp2350|raspberry.?pi|raspberrypi|rpi\b|pico\b|pi.?hat|pihat"],
        "topic_keywords": ["rp2040", "rp2350", "raspberry-pi", "pico",
                           "raspberrypi", "raspberry-pi-hat", "rpi",
                           "raspberry-pi-pico"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
    {
        "category": "Arduino recreations",
        "name_patterns": [r"arduino|atmega\d+|avr\b"],
        "desc_patterns": [r"arduino|atmega\d+p?\b|avr\b|arduino.?shield|arduino.?nano|arduino.?uno|arduino.?mega"],
        "topic_keywords": ["arduino", "arduino-shield", "arduino-nano",
                           "arduino-uno", "arduino-mega", "atmega328",
                           "atmega328p", "avr", "attiny85", "attiny",
                           "arduino-compatible", "platformio"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
    {
        "category": "RISC-V / FPGA",
        "name_patterns": [r"riscv|risc.?v|fpga|ice40|ecp5|gowin|xilinx|zynq"],
        "desc_patterns": [r"riscv|risc.?v|fpga|ice40|ecp5|gowin|lattice.?fpga|xilinx|zynq|verilog|vhdl|hdl\b"],
        "topic_keywords": ["risc-v", "riscv", "fpga", "ice40", "ecp5",
                           "lattice", "xilinx", "verilog", "vhdl", "gowin",
                           "zynq", "hdl"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },

    # --- Domain categories (detector + keyword driven) ---
    {
        "category": "Keyboards",
        "name_patterns": [r"keyboard|keypad|macropad|keeb|numpad|keyswitch|dactyl|ergodox|corne|sofle|lily"],
        "desc_patterns": [r"keyboard|keypad|macropad|keeb|numpad|mechanical.?key|split.?key|qmk|zmk|cherry.?mx"],
        "topic_keywords": ["keyboard", "mechanical-keyboard", "qmk", "zmk",
                           "keypad", "macropad", "keeb", "split-keyboard",
                           "ergodox", "dactyl", "ortholinear"],
        "strong_detectors": {"key_matrices": 1},
        "support_detectors": {},
        "tags": ["keyboard"],
    },
    {
        "category": "Motor controllers / robotics",
        "name_patterns": [r"motor|robot|stepper|servo|cnc|grbl|drone|quadr?a?copter|bldc|esc\b|gimbal"],
        "desc_patterns": [r"motor|robot|stepper|servo|cnc|grbl|drone|quadr?a?copter|bldc\b|esc\b|gimbal|actuator|h.?bridge"],
        "topic_keywords": ["robot", "robotics", "motor", "stepper",
                           "servo", "cnc", "grbl", "bldc", "drone",
                           "quadcopter", "esc", "motor-controller",
                           "motor-driver", "h-bridge"],
        "strong_detectors": {"motor_drivers": 1},
        "support_detectors": {"bridge_circuits": 1, "current_sense": 1},
        "tags": ["motor_driver"],
    },
    {
        "category": "Synthesizers / audio",
        "name_patterns": [r"synth|eurorack|audio|amplifier|preamp|pre.?amp|mixer|pedal|guitar|headphone|dac\b|codec|i2s\b|\bamp\b|speaker|vocoder|sequencer|drum.?machine"],
        "desc_patterns": [r"synth|synthesizer|eurorack|audio|amplif|preamp|pre.?amp|mixer|pedal|guitar|headphone|hi.?fi|class.?[abd]\b|tube.?amp|valve.?amp|vocoder|sequencer|drum.?machine|music|tone|speaker|sound\b|dac\b|codec|i2s\b"],
        "topic_keywords": ["synthesizer", "synth", "eurorack", "audio",
                           "dac", "amplifier", "mixer", "pedal",
                           "guitar-pedal", "guitar", "music",
                           "headphone-amplifier", "hi-fi", "analog-synth",
                           "modular-synth", "drum-machine", "sequencer"],
        "strong_detectors": {"audio_circuits": 1},
        "support_detectors": {"buzzer_speaker_circuits": 1},
        "tags": [],
        # Bonus: if both audio detector and keyword match, very strong signal
        "combo_bonus": [({"det:audio_circuits", "desc:audio"}, 2),
                        ({"det:audio_circuits", "name:synth"}, 2),
                        ({"det:audio_circuits", "name:pedal"}, 2)],
    },
    {
        "category": "Networking / radio / SDR",
        "name_patterns": [r"radio|sdr|\blora\b|lorawan|rf\b|ham\b|antenna|transceiver|wifi|ethernet|canbus|can.?bus|modem|zigbee|nrf\d+|\bble\b|bluetooth"],
        "desc_patterns": [r"radio|sdr\b|lora\b|lorawan|rf\b|ham\b|ham.?radio|antenna|transceiver|wifi|ethernet|canbus|can.?bus|modem|zigbee|nrf\d+|\bble\b|bluetooth|wireless.?(?:sensor|module|board|comm|link|relay)|gnss|gps.?(?:track|receiv|module|board)|rf.?receiver|rf.?transmitter|beacon"],
        "topic_keywords": ["sdr", "radio", "rf", "lora", "lorawan",
                           "wifi", "ethernet", "can-bus", "canbus",
                           "ham-radio", "amateur-radio", "antenna",
                           "nrf52", "bluetooth-low-energy", "ble",
                           "zigbee", "nordicsemi", "gnss", "gps",
                           "transceiver"],
        "strong_detectors": {"rf_chains": 1, "ethernet_interfaces": 1},
        "support_detectors": {"rf_matching": 2},
        "tags": ["rf"],
    },
    {
        "category": "Sensor boards / IoT",
        "name_patterns": [r"sensor|iot|weather|thermostat|home.?auto|environment|monitor.*temp|temp.*monitor|humidity|air.?quality|smoke|gas.?detect|soil.?moist"],
        "desc_patterns": [r"sensor.?(?:board|module|node|hub|array|network|interface|fusion)|iot\b|weather.?(?:station|monitor|sensor)|thermostat|home.?auto|environment|humidity|air.?quality|smoke.?detect|gas.?detect|soil.?moist|data.?logg|smart.?home|temperature.?(?:sensor|monitor|log)"],
        "topic_keywords": ["iot", "sensor", "weather", "temperature",
                           "humidity", "environmental", "home-automation",
                           "automation", "smart-home", "m5stack"],
        "strong_detectors": {"sensor_interfaces": 1},
        "support_detectors": {"thermocouple_rtd": 1},
        "tags": [],
    },
    {
        "category": "Power / battery",
        "name_patterns": [r"battery|charger|bms|power.?supply|solar|ups\b|inverter|mppt|psu\b|dcdc|dc.?dc|buck|boost|smps|ldo"],
        "desc_patterns": [r"battery|charger|bms|power.?supply|solar|ups\b|inverter|mppt|psu\b|dcdc|dc.?dc|buck.?convert|boost.?convert|smps|ldo\b|power.?board|power.?module|voltage.?regulat|lithium|lipo|lifepo"],
        "topic_keywords": ["battery", "charger", "bms", "power-supply",
                           "solar", "ups", "inverter", "mppt",
                           "voltage-regulator", "dcdc-converter",
                           "lipo", "lithium", "solar-panel", "mosfet"],
        "strong_detectors": {"battery_chargers": 1, "bms_systems": 1},
        "support_detectors": {"power_path": 1, "current_sense": 1},
        "tags": [],
        "combo_bonus": [({"det:power_path", "det:current_sense"}, 2),
                        ({"name:solar", "det:current_sense"}, 1),
                        ({"name:charger", "det:battery_chargers"}, 1)],
    },
    {
        "category": "LED / display",
        "name_patterns": [r"led.?matrix|neopixel|ws2812|led.?strip|led.?driver|led.?board|oled|e.?ink|eink|lcd|display|nixie|vfd|flipdot|flip.?dot|dot.?matrix|rgb\b|pixel|badge"],
        "desc_patterns": [r"led.?matrix|neopixel|ws2812|led.?strip|led.?driver|oled|e.?ink|eink|lcd\b|display|nixie|vfd|flipdot|flip.?dot|dot.?matrix|rgb.?led|pixel|7.?segment|segment.?display|led.?light|led.?torch|led.?lamp|illuminat|led.?panel|led.?ring|led.?bar"],
        "topic_keywords": ["display", "oled", "lcd", "e-ink", "led-matrix",
                           "neopixel", "ws2812", "led-strip", "ws2812b",
                           "nixie", "vfd", "flipdot", "segment-display",
                           "leds", "lighting", "badge", "pcb-art"],
        "strong_detectors": {"display_interfaces": 1, "addressable_led_chains": 1,
                             "led_driver_ics": 1},
        "support_detectors": {},
        "tags": [],
        "combo_bonus": [({"det:addressable_led_chains", "name:led"}, 2),
                        ({"det:led_driver_ics", "name:led"}, 2)],
    },
    {
        "category": "Retro computing",
        "name_patterns": [r"retro|z80|6502|65c02|65816|commodore|amiga|atari|8.?bit|zx.?spectrum|zx81|c64|vic.?20|apple.?ii|cpc464|msx|bbc.?micro|oric|dragon32|rc2014|s100|cp.?m\b|isa.?bus|isa.?card|gameboy|game.?boy|mega.?drive|genesis|sega|snes|nes\b|n64|gamecube|vectrex|coleco"],
        "desc_patterns": [r"retro.?comput|z80|6502|65c02|65816|commodore|amiga|atari\b|8.?bit.?(?:comput|cpu|processor|bus)|zx.?spectrum|zx81|c64|vic.?20|apple.?ii|cpc464|msx\b|bbc.?micro|oric\b|dragon32|rc2014|s100\b|cp/?m\b|vintage.?comput|homebrew.*comput|gameboy|game.?boy|mega.?drive|genesis|sega\b|snes\b|nes\b(?!t)|n64\b|gamecube|vectrex|coleco|classic.?comput|8080\b|6809|68000\b|6800\b|z180|clone.*comput|replica.*comput"],
        "topic_keywords": ["retro", "retro-computing", "retrocomputing",
                           "z80", "6502", "commodore", "amiga", "atari",
                           "8-bit", "zx81", "zx-spectrum", "sinclair",
                           "rc2014", "romwbw", "gameboy", "isa",
                           "retro-computer", "nintendo", "game-boy",
                           "sega", "nes"],
        "strong_detectors": {},
        "support_detectors": {"memory_interfaces": 1},
        "tags": [],
    },
    {
        "category": "ADC / DAC / measurement",
        "name_patterns": [r"adc\b|data.?logger|measurement|instrumentation|acquisition|oscilloscope|voltmeter|ammeter|wattmeter|coulomb|power.?meter|energy.?meter|signal.?gen"],
        "desc_patterns": [r"adc\b|data.?logg|measurement|instrumentation|acquisition|voltmeter|ammeter|wattmeter|coulomb|power.?meter|energy.?meter|signal.?gen|analog.?to.?digital|sampling|precision.?measur"],
        "topic_keywords": ["adc", "measurement", "oscilloscope",
                           "multimeter", "test-equipment",
                           "data-logger", "instrumentation",
                           "signal-generator"],
        "strong_detectors": {"adc_circuits": 1},
        "support_detectors": {"opamp_circuits": 3, "thermocouple_rtd": 1},
        "tags": [],
        "combo_bonus": [({"det:adc_circuits", "det:opamp_circuits"}, 2),
                        ({"det:thermocouple_rtd", "det:adc_circuits"}, 2)],
    },
    {
        "category": "USB / interface adapters",
        "name_patterns": [r"usb.?[chb]|usb.?hub|usb.?adapter|uart.?adapt|rs485|rs232|i2c.?adapt|can.?adapt|spi.?adapt|breakout|pmod\b|adapter|converter|bridge.*usb|usb.*bridge|ftdi|ch340|cp210"],
        "desc_patterns": [r"usb.?[chb]|usb.?hub|usb.?adapter|uart\b|rs485|rs232|i2c.?adapt|can.?adapt|spi.?adapt|breakout.?board|pmod\b|(?:pin|plug|socket|board|signal|level|protocol).?adapt|(?:usb|uart|spi|i2c|can).?(?:convert|bridge)|interface.?board|ftdi|ch340|cp210"],
        "topic_keywords": ["usb", "usb-c", "usb-hub", "interface",
                           "adapter", "converter", "breakout-board",
                           "kicad-breakout-board", "pmod", "uart",
                           "rs485", "i2c", "breakout"],
        "strong_detectors": {},
        "support_detectors": {"level_shifters": 1},
        "tags": [],
    },
    {
        "category": "Test equipment / debug tools",
        "name_patterns": [r"tester|logic.?analyz|oscilloscope|debugger|jtag|programmer|probe|multimeter|rlc.?meter|lcr.?meter|function.?gen|freq.?counter|spectrum.?analyz|pga.?prog|swd\b|stlink|openocd|black.?magic"],
        "desc_patterns": [r"tester|logic.?analyz|oscilloscope|debugger|jtag|programmer|probe|multimeter|rlc.?meter|lcr.?meter|function.?gen|freq.?counter|spectrum.?analyz|debug.?tool|debug.?board|test.?jig|test.?fixture|programming.?tool|flash.*tool|swd\b|stlink|openocd|black.?magic"],
        "topic_keywords": ["test-equipment", "debug", "logic-analyzer",
                           "oscilloscope", "debugger", "jtag",
                           "programmer", "probe", "multimeter",
                           "stlink"],
        "strong_detectors": {},
        "support_detectors": {"debug_interfaces": 3},
        "tags": [],
    },
    {
        "category": "CubeSat / aerospace",
        "name_patterns": [r"cubesat|satellite|aerospace|rocket|flight.?controller|rocketry|sounding|payload|avionics|telemetry.*rocket|altitude.*controller"],
        "desc_patterns": [r"cubesat|satellite|aerospace|rocket|flight.?controller|rocketry|sounding|payload|avionics|high.?altitude|balloon|space|orbital|launch"],
        "topic_keywords": ["cubesat", "satellite", "aerospace",
                           "rocket", "flight-controller", "rocketry",
                           "avionics", "space"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
    {
        "category": "SBCs / carrier boards",
        "name_patterns": [r"carrier.?board|compute.?module|beaglebone|beagleboard|jetson|nanopi|pine64|banana.?pi|orange.?pi|rock\d|radxa|cm4|cm5|sbc\b|single.?board"],
        "desc_patterns": [r"carrier.?board|compute.?module|beaglebone|beagleboard|jetson|nanopi|pine64|banana.?pi|orange.?pi|rock\d|radxa|cm4\b|cm5\b|single.?board.?comput|sbc\b"],
        "topic_keywords": ["single-board-computer", "sbc",
                           "carrier-board", "compute-module",
                           "beaglebone", "jetson", "development-board"],
        "strong_detectors": {},
        "support_detectors": {"memory_interfaces": 2, "hdmi_dvi_interfaces": 1},
        "tags": [],
    },
    {
        "category": "Smartwatches / wearables",
        "name_patterns": [r"smartwatch|wearable|fitness|watch.?pcb|watch.?board|bracelet|ring.?pcb"],
        "desc_patterns": [r"smartwatch|wearable|fitness.?track|watch|bracelet|wrist.?band"],
        "topic_keywords": ["smartwatch", "wearable", "watch",
                           "fitness-tracker", "wristband"],
        "strong_detectors": {},
        "support_detectors": {},
        "tags": [],
    },
]


def _get_text_signals(repo_entry, validated_entry):
    """Extract all searchable text from a repo entry.

    Returns (repo_name, description, topics) all lowercase.
    """
    repo_name = repo_entry["repo"].split("/")[-1].lower()
    # Also include the owner name for matching
    owner = repo_entry["repo"].split("/")[0].lower()

    desc = ""
    topics = []
    if validated_entry:
        desc = (validated_entry.get("description") or "").lower()
        topics = [t.lower() for t in validated_entry.get("topics", [])]

    return repo_name, owner, desc, topics


def _score_repo(repo_entry, validated_entry, rule):
    """Score a repo for a category rule. Returns (score, reasons, signals_set)."""
    score = 0
    reasons = []
    signals = set()  # Track which signals fired for combo bonuses

    repo_name, owner, desc, topics = _get_text_signals(repo_entry, validated_entry)
    detectors = repo_entry.get("detectors_fired", {})
    tags = set(repo_entry.get("tags", []))

    # 1. Topic matches (+3 each, strong signal)
    for kw in rule.get("topic_keywords", []):
        if kw.lower() in topics:
            score += 3
            reasons.append(f"topic:{kw}")
            signals.add(f"topic:{kw}")

    # 2. Name pattern matches (+2 each)
    for pat in rule.get("name_patterns", []):
        m = re.search(pat, repo_name, re.IGNORECASE)
        if m:
            score += 2
            reasons.append(f"name:{m.group()}")
            signals.add(f"name:{pat}")
            break  # Only count one name match per rule

    # 3. Description pattern matches (+2 each, but cap at first match)
    for pat in rule.get("desc_patterns", []):
        m = re.search(pat, desc, re.IGNORECASE)
        if m:
            score += 2
            reasons.append(f"desc:{m.group()}")
            signals.add(f"desc:{pat}")
            break  # Only count one desc match per rule

    # 4. Strong detectors (+3 each — these are distinctive signals)
    for det, min_count in rule.get("strong_detectors", {}).items():
        actual = detectors.get(det, 0)
        if actual >= min_count:
            score += 3
            reasons.append(f"det:{det}={actual}")
            signals.add(f"det:{det}")

    # 5. Supporting detectors (+1 each)
    for det, min_count in rule.get("support_detectors", {}).items():
        actual = detectors.get(det, 0)
        if actual >= min_count:
            score += 1
            reasons.append(f"sup:{det}={actual}")
            signals.add(f"det:{det}")

    # 6. Tag matches (+1 each)
    for tag in rule.get("tags", []):
        if tag in tags:
            score += 1
            reasons.append(f"tag:{tag}")
            signals.add(f"tag:{tag}")

    # 7. Combo bonuses
    for required_signals, bonus in rule.get("combo_bonus", []):
        # Check if all required signals match (using prefix matching for flexibility)
        all_match = True
        for req in required_signals:
            # req is like "det:audio_circuits" or "name:synth" or "tag:power"
            prefix, value = req.split(":", 1)
            found = False
            for s in signals:
                if s.startswith(prefix + ":") and value in s:
                    found = True
                    break
            if not found:
                all_match = False
                break
        if all_match:
            score += bonus
            reasons.append(f"combo+{bonus}")

    return score, reasons


def classify_repo(repo_entry, validated_entry, min_score=1):
    """Classify a single repo. Returns (category, score, reasons) or None."""
    best_cat = None
    best_score = 0
    best_reasons = []

    for rule in CLASSIFICATION_RULES:
        score, reasons = _score_repo(repo_entry, validated_entry, rule)
        if score > best_score:
            best_score = score
            best_cat = rule["category"]
            best_reasons = reasons

    if best_score >= min_score:
        return best_cat, best_score, best_reasons
    return None


def reclassify_in_repos_md(moves):
    """Apply reclassifications to repos.md.

    moves: list of (repo_name, url_line, old_category, new_category)
    """
    lines = REPOS_MD.read_text().splitlines()

    # Build index: category header line numbers
    category_ends = {}  # category -> last entry line index
    current_cat = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            current_cat = stripped[3:].strip()
        elif current_cat and stripped.startswith("- http"):
            category_ends[current_cat] = i

    # Group moves by (old_category, new_category)
    # Process removals first, then insertions
    urls_to_move = {}  # url_substring -> new_category
    for repo_name, url_line, old_cat, new_cat in moves:
        # Extract URL from the line
        urls_to_move[url_line.strip()] = new_cat

    # Remove lines from old positions
    new_lines = []
    removed_lines = {}  # url_line -> (line_content, new_category)
    for line in lines:
        stripped = line.strip()
        if stripped in urls_to_move:
            removed_lines[stripped] = (line, urls_to_move[stripped])
        else:
            new_lines.append(line)

    # Insert into new categories
    for url_stripped, (line_content, new_cat) in removed_lines.items():
        # Find insertion point for new_cat
        in_section = False
        insert_at = None
        for i, l in enumerate(new_lines):
            s = l.strip()
            if s.startswith("## "):
                header = s[3:].strip()
                if header == new_cat:
                    in_section = True
                elif in_section:
                    # Next section — insert before it
                    insert_at = i
                    while insert_at > 0 and not new_lines[insert_at - 1].strip():
                        insert_at -= 1
                    break
            elif in_section and s.startswith("- http"):
                insert_at = i + 1  # After last entry in section

        if insert_at is None and in_section:
            insert_at = len(new_lines)

        if insert_at is not None:
            new_lines.insert(insert_at, line_content)

    REPOS_MD.write_text("\n".join(new_lines) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Reclassify Miscellaneous repos using detector + topic + keyword data")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show proposed changes without editing repos.md")
    parser.add_argument("--apply", action="store_true",
                        help="Apply reclassifications to repos.md")
    parser.add_argument("--stats", action="store_true",
                        help="Show category distribution and exit")
    parser.add_argument("--min-score", type=int, default=2,
                        help="Minimum score to reclassify (default: 2)")
    parser.add_argument("--show-unclassified", action="store_true",
                        help="Show repos that remain Miscellaneous (with --dry-run)")
    args = parser.parse_args()

    if not CATALOG_FILE.exists():
        print(f"Error: {CATALOG_FILE} not found. Run generate_catalog.py first.")
        sys.exit(1)

    catalog = json.loads(CATALOG_FILE.read_text())
    misc = [r for r in catalog if r.get("category") == MISC_CATEGORY]

    # Load validated.json for topics + descriptions
    v_map = {}
    if VALIDATED_FILE.exists():
        validated = json.loads(VALIDATED_FILE.read_text())
        v_map = {f"{r['owner']}/{r['repo']}": r for r in validated}

    if args.stats:
        cats = Counter(r.get("category", "?") for r in catalog)
        print(f"{'Category':<40s} {'Count':>6s}")
        print("-" * 48)
        for cat, count in cats.most_common():
            print(f"{cat:<40s} {count:>6d}")
        print(f"\nTotal: {len(catalog)} repos ({len(misc)} Miscellaneous)")
        return

    print(f"Miscellaneous repos: {len(misc)}")
    v_count = sum(1 for r in misc if r["repo"] in v_map)
    desc_count = sum(1 for r in misc
                     if r["repo"] in v_map and v_map[r["repo"]].get("description"))
    topic_count = sum(1 for r in misc
                      if r["repo"] in v_map and v_map[r["repo"]].get("topics"))
    print(f"  with validated.json entry: {v_count}")
    print(f"  with description:          {desc_count}")
    print(f"  with topics:               {topic_count}")
    print()

    # Classify
    moves = []
    move_counts = Counter()
    unclassified = []
    for repo_entry in misc:
        v_entry = v_map.get(repo_entry["repo"])
        result = classify_repo(repo_entry, v_entry, min_score=args.min_score)
        if result:
            new_cat, score, reasons = result
            moves.append((repo_entry["repo"], new_cat, score, reasons))
            move_counts[new_cat] += 1
        else:
            unclassified.append(repo_entry)

    print(f"Proposed reclassifications: {len(moves)}")
    remaining = len(misc) - len(moves)
    print(f"Remaining Miscellaneous:    {remaining}")
    pct = len(moves) / len(misc) * 100 if misc else 0
    print(f"Reclassification rate:      {pct:.1f}%")
    print()

    # Summary by category
    print(f"{'New Category':<40s} {'Count':>6s}")
    print("-" * 48)
    for cat, count in move_counts.most_common():
        print(f"{cat:<40s} {count:>6d}")
    print(f"{'(remaining Miscellaneous)':<40s} {remaining:>6d}")
    print()

    if args.dry_run:
        # Show details (top 80)
        limit = 80
        for repo, new_cat, score, reasons in sorted(moves, key=lambda x: -x[2])[:limit]:
            reason_str = ", ".join(reasons[:4])
            print(f"  {repo:<50s} -> {new_cat} (score={score}, {reason_str})")
        if len(moves) > limit:
            print(f"  ... and {len(moves) - limit} more")

        if args.show_unclassified and unclassified:
            print(f"\n--- Unclassified repos (sample of 30) ---")
            import random
            random.seed(42)
            sample = random.sample(unclassified, min(30, len(unclassified)))
            for r in sample:
                v = v_map.get(r["repo"])
                desc = (v.get("description", "") if v else "")[:60]
                dets = ", ".join(f"{k}={v}" for k, v in
                                sorted(r.get("detectors_fired", {}).items(),
                                       key=lambda x: -x[1])[:3])
                print(f"  {r['repo']:<50s} dets=[{dets}]  desc={desc}")
        return

    if args.apply:
        # Build move instructions for repos.md
        # Need to find the URL line for each repo
        lines = REPOS_MD.read_text().splitlines()
        repo_to_url = {}
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- http"):
                for repo, new_cat, score, reasons in moves:
                    # Match by owner/repo in URL
                    owner, name = repo.split("/", 1)
                    if f"/{owner}/{name}" in stripped:
                        repo_to_url[repo] = stripped
                        break

        md_moves = []
        for repo, new_cat, score, reasons in moves:
            url_line = repo_to_url.get(repo)
            if url_line:
                md_moves.append((repo, url_line, MISC_CATEGORY, new_cat))

        print(f"Applying {len(md_moves)} reclassifications...")
        reclassify_in_repos_md(md_moves)
        print(f"Done. Updated {REPOS_MD}")
        print(f"\nNext steps:")
        print(f"  python3 tools/generate_catalog.py")
        print(f"  python3 tools/generate_cross_sections.py")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
