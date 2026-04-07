#!/usr/bin/env python3
"""Reclassify repos from 'Miscellaneous KiCad projects' into specific categories.

Uses detector data from repo_catalog.json and GitHub topics from validated.json
to assign more specific categories to repos currently in Miscellaneous.

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

# Rules: (category, detector_rules, topic_rules)
# detector_rules: {detector_name: min_count} — ALL must match
# topic_rules: [topic_strings] — ANY match adds score
# Score = detector_matches + topic_matches. Highest-scoring category wins.

CLASSIFICATION_RULES = [
    # MCU families (strongest signal — specific IC families)
    ("ESP32", {}, ["esp32", "esp8266", "esp-idf", "esphome"]),
    ("STM32", {}, ["stm32", "stm32f", "stm32h", "stm32l", "stm32g"]),
    ("RP2040 / Raspberry Pi", {}, ["rp2040", "raspberry-pi", "pico", "rpi",
                                    "raspberrypi", "raspberry-pi-hat"]),
    ("Arduino recreations", {}, ["arduino", "arduino-shield", "arduino-nano",
                                  "arduino-uno", "arduino-mega", "atmega328",
                                  "atmega328p", "avr"]),
    ("RISC-V / FPGA", {}, ["risc-v", "riscv", "fpga", "ice40", "ecp5",
                            "lattice", "xilinx", "verilog", "vhdl"]),

    # Domain detectors (detector data)
    ("Motor controllers / robotics", {"motor_drivers": 2}, ["robot", "robotics",
                                                             "motor", "stepper",
                                                             "servo", "cnc", "grbl"]),
    ("Synthesizers / audio", {"audio_circuits": 2}, ["synthesizer", "synth",
                                                      "eurorack", "audio", "dac",
                                                      "amplifier", "mixer"]),
    ("Networking / radio / SDR", {"ethernet_interfaces": 1}, ["sdr", "radio",
                                                               "rf", "lora", "lorawan",
                                                               "wifi", "ethernet",
                                                               "can-bus", "canbus"]),
    ("Networking / radio / SDR", {"rf_chains": 1}, []),
    ("Networking / radio / SDR", {"rf_matching": 2, "rf_chains": 1}, []),
    ("Sensor boards / IoT", {"sensor_interfaces": 3}, ["iot", "sensor", "weather",
                                                        "temperature", "humidity",
                                                        "environmental"]),
    ("Power / battery", {"battery_chargers": 1}, ["battery", "charger", "bms",
                                                   "power-supply", "solar"]),
    ("Power / battery", {"bms_systems": 1}, []),
    ("ADC / DAC / measurement", {"adc_circuits": 3}, ["adc", "measurement",
                                                       "oscilloscope", "multimeter",
                                                       "test-equipment"]),
    ("Keyboards", {"key_matrices": 1}, ["keyboard", "mechanical-keyboard",
                                         "qmk", "zmk", "keypad"]),
    ("LED / display", {"display_interfaces": 2}, ["display", "oled", "lcd",
                                                   "e-ink", "led-matrix"]),
    ("LED / display", {"addressable_led_chains": 3}, ["neopixel", "ws2812",
                                                       "led-strip"]),
    ("Retro computing", {}, ["retro", "retro-computing", "z80", "6502",
                              "commodore", "amiga", "atari", "8-bit",
                              "modelrailroad", "dcc", "railcom"]),
    ("CubeSat / aerospace", {}, ["cubesat", "satellite", "aerospace",
                                  "rocket", "flight-controller"]),
    ("Test equipment / debug tools", {}, ["test-equipment", "debug",
                                           "logic-analyzer", "oscilloscope",
                                           "debugger", "jtag", "programmer"]),
    ("USB / interface adapters", {}, ["usb", "usb-c", "usb-hub",
                                      "interface", "adapter", "converter"]),
    ("SBCs / carrier boards", {}, ["single-board-computer", "sbc",
                                    "carrier-board", "compute-module"]),
    ("Smartwatches / wearables", {}, ["smartwatch", "wearable", "watch",
                                      "fitness-tracker"]),
]


def _score_repo(repo_entry, validated_entry, category, detector_rules, topic_rules):
    """Score a repo for a category. Returns (score, reasons)."""
    score = 0
    reasons = []

    # Check detector rules (ALL must match)
    detectors = repo_entry.get("detectors_fired", {})
    if detector_rules:
        all_match = True
        for det, min_count in detector_rules.items():
            actual = detectors.get(det, 0)
            if actual < min_count:
                all_match = False
                break
        if all_match:
            # Score by how strongly the detectors match
            for det, min_count in detector_rules.items():
                actual = detectors.get(det, 0)
                score += actual
                reasons.append(f"{det}={actual}")
        else:
            return 0, []

    # Check topic rules (ANY match)
    if topic_rules and validated_entry:
        topics = [t.lower() for t in validated_entry.get("topics", [])]
        desc = (validated_entry.get("description") or "").lower()
        repo_name = validated_entry.get("repo", "").lower()

        for keyword in topic_rules:
            kw = keyword.lower()
            if kw in topics:
                score += 3
                reasons.append(f"topic:{keyword}")
            elif kw in desc:
                score += 1
                reasons.append(f"desc:{keyword}")
            elif kw in repo_name:
                score += 1
                reasons.append(f"name:{keyword}")

    return score, reasons


def classify_repo(repo_entry, validated_entry):
    """Classify a single repo. Returns (category, score, reasons) or None."""
    best_cat = None
    best_score = 0
    best_reasons = []

    for category, detector_rules, topic_rules in CLASSIFICATION_RULES:
        score, reasons = _score_repo(repo_entry, validated_entry,
                                      category, detector_rules, topic_rules)
        if score > best_score:
            best_score = score
            best_cat = category
            best_reasons = reasons

    if best_score >= 2:  # Minimum threshold
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
        description="Reclassify Miscellaneous repos using detector + topic data")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show proposed changes without editing repos.md")
    parser.add_argument("--apply", action="store_true",
                        help="Apply reclassifications to repos.md")
    parser.add_argument("--stats", action="store_true",
                        help="Show category distribution and exit")
    parser.add_argument("--min-score", type=int, default=2,
                        help="Minimum score to reclassify (default: 2)")
    args = parser.parse_args()

    if not CATALOG_FILE.exists():
        print(f"Error: {CATALOG_FILE} not found. Run generate_catalog.py first.")
        sys.exit(1)

    catalog = json.loads(CATALOG_FILE.read_text())
    misc = [r for r in catalog if r.get("category") == MISC_CATEGORY]

    # Load validated.json for topics
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
    print(f"Repos with topics: {sum(1 for r in misc if r['repo'] in v_map)}")
    print()

    # Classify
    moves = []
    move_counts = Counter()
    for repo_entry in misc:
        v_entry = v_map.get(repo_entry["repo"])
        result = classify_repo(repo_entry, v_entry)
        if result:
            new_cat, score, reasons = result
            if score >= args.min_score:
                moves.append((repo_entry["repo"], new_cat, score, reasons))
                move_counts[new_cat] += 1

    print(f"Proposed reclassifications: {len(moves)}")
    print()

    # Summary by category
    print(f"{'New Category':<40s} {'Count':>6s}")
    print("-" * 48)
    for cat, count in move_counts.most_common():
        print(f"{cat:<40s} {count:>6d}")
    remaining = len(misc) - len(moves)
    print(f"{'(remaining Miscellaneous)':<40s} {remaining:>6d}")
    print()

    if args.dry_run:
        # Show details
        for repo, new_cat, score, reasons in sorted(moves, key=lambda x: -x[2])[:50]:
            print(f"  {repo:<50s} → {new_cat} (score={score}, {', '.join(reasons[:3])})")
        if len(moves) > 50:
            print(f"  ... and {len(moves) - 50} more")
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
        print(f"  python3 generate_catalog.py")
        print(f"  python3 generate_cross_sections.py")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
