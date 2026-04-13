"""Unit tests for tools/add_repos.py — _find_category_insert_point."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from add_repos import _find_category_insert_point


SAMPLE_REPOS_MD = [
    "# KiCad Test Repos",
    "",
    "## ESP32",
    "",
    "- https://github.com/user/esp32-a",
    "- https://github.com/user/esp32-b",
    "",
    "## Keyboards",
    "",
    "- https://github.com/user/kbd-1",
    "",
    "## Miscellaneous KiCad projects",
    "",
    "- https://github.com/user/misc-1",
    "- https://github.com/user/misc-2",
]


def test_insert_into_middle_category():
    # Inserting into ESP32 — should land after the last ESP32 entry, before ## Keyboards
    idx = _find_category_insert_point(SAMPLE_REPOS_MD, "ESP32")
    # Index 5 is "- esp32-b"; idx should be 6 (after it) or before the blank + ## Keyboards
    # The function backs up past blank lines to insert before the next ## header
    inserted = SAMPLE_REPOS_MD[:idx] + ["- https://github.com/user/esp32-c"] + SAMPLE_REPOS_MD[idx:]
    new_line_pos = inserted.index("- https://github.com/user/esp32-c")
    esp32_b_pos = inserted.index("- https://github.com/user/esp32-b")
    keyboards_pos = inserted.index("## Keyboards")
    assert esp32_b_pos < new_line_pos < keyboards_pos


def test_insert_into_last_category():
    # Inserting into Miscellaneous — the last section; should land after misc-2
    idx = _find_category_insert_point(SAMPLE_REPOS_MD, "Miscellaneous KiCad projects")
    # misc-2 is at index 14; insert should be at 15
    assert idx == len(SAMPLE_REPOS_MD)  # last section appends at end


def test_insert_into_single_entry_category():
    # Keyboards has one entry; insert should go after it
    idx = _find_category_insert_point(SAMPLE_REPOS_MD, "Keyboards")
    inserted = SAMPLE_REPOS_MD[:idx] + ["- https://github.com/user/kbd-2"] + SAMPLE_REPOS_MD[idx:]
    kbd1_pos = inserted.index("- https://github.com/user/kbd-1")
    kbd2_pos = inserted.index("- https://github.com/user/kbd-2")
    misc_pos = inserted.index("## Miscellaneous KiCad projects")
    assert kbd1_pos < kbd2_pos < misc_pos


def test_fallback_to_misc_for_unknown_category():
    # Category "RISC-V / FPGA" does not exist in the sample; should fall back to Miscellaneous
    idx = _find_category_insert_point(SAMPLE_REPOS_MD, "RISC-V / FPGA")
    # Insertion index should still land within or at end of the Miscellaneous section
    misc_header_pos = SAMPLE_REPOS_MD.index("## Miscellaneous KiCad projects")
    assert idx > misc_header_pos


def test_empty_category_section():
    # A category that exists but has no entries yet
    lines = [
        "## Arduino recreations",
        "",
        "## ESP32",
        "",
        "- https://github.com/user/esp32-a",
    ]
    idx = _find_category_insert_point(lines, "Arduino recreations")
    # Should insert before ## ESP32 (backing up past blank line)
    inserted = lines[:idx] + ["- https://github.com/user/arduino-x"] + lines[idx:]
    new_pos = inserted.index("- https://github.com/user/arduino-x")
    esp32_header_pos = inserted.index("## ESP32")
    assert new_pos < esp32_header_pos


def test_category_at_very_end_no_entries():
    # Category header is last line with no entries and no trailing section
    lines = [
        "## ESP32",
        "",
        "- https://github.com/user/esp32-a",
        "",
        "## Empty Section",
    ]
    idx = _find_category_insert_point(lines, "Empty Section")
    assert idx == len(lines)


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in globals().items()
             if name.startswith("test_") and callable(obj)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
