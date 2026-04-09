"""Unit tests for detect_sub_sheet() — tiered sub-sheet detection (KH-228)."""

TIER = "unit"

import sys
import os
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
from sexp_parser import parse_file
from analyze_schematic import detect_sub_sheet

_REPOS = _HARNESS / "repos"


# === Tier 1: symbol_instances → root ===

def test_tier1_symbol_instances_means_root():
    """Tree with symbol_instances is definitively a root sheet."""
    tree = ["kicad_sch",
            ["version", "20231120"],
            ["symbol_instances",
             ["path", "/", ["reference", "R1"], ["unit", "1"]]]]
    assert detect_sub_sheet(tree) is False


# === Tier 2: sheet blocks → root ===

def test_tier2_sheet_blocks_mean_root():
    """Tree with sheet blocks (references to sub-sheets) is a root."""
    tree = ["kicad_sch",
            ["version", "20231120"],
            ["sheet",
             ["at", "100", "100"],
             ["size", "50", "50"],
             ["property", "Sheetname", "Power"],
             ["property", "Sheetfile", "power.kicad_sch"]]]
    assert detect_sub_sheet(tree) is False


# === Tier 3: .kicad_pro stem matching (4 real-file tests) ===

_AMP_DIR = _REPOS / "57maker" / "headphone_amplifier_v0"
_AMP_FILES = {
    "root":   _AMP_DIR / "headphone_amplifier_v0.kicad_sch",
    "power":  _AMP_DIR / "power.kicad_sch",
    "op_amp": _AMP_DIR / "op_amplifier_left.kicad_sch",
    "audio":  _AMP_DIR / "audio_jack.kicad_sch",
}


def _skip_if_missing(*paths):
    for p in paths:
        if not p.exists():
            print(f"SKIP: corpus file not found: {p}")
            return True
    return False


def test_tier3_pro_stem_match_root():
    """Root schematic stem matches .kicad_pro → False."""
    if _skip_if_missing(_AMP_FILES["root"]):
        return
    tree = parse_file(str(_AMP_FILES["root"]))
    # Remove symbol_instances and sheet blocks so tier 3 is the deciding tier
    tree_stripped = [e for e in tree
                     if not (isinstance(e, list) and len(e) > 0
                             and e[0] in ("symbol_instances", "sheet"))]
    assert detect_sub_sheet(tree_stripped, file_path=str(_AMP_FILES["root"])) is False


def test_tier3_pro_stem_no_match_power():
    """Sub-sheet 'power' doesn't match .kicad_pro stem → True."""
    if _skip_if_missing(_AMP_FILES["power"]):
        return
    tree = parse_file(str(_AMP_FILES["power"]))
    assert detect_sub_sheet(tree, file_path=str(_AMP_FILES["power"])) is True


def test_tier3_pro_stem_no_match_op_amp():
    """Sub-sheet 'op_amplifier_left' doesn't match → True."""
    if _skip_if_missing(_AMP_FILES["op_amp"]):
        return
    tree = parse_file(str(_AMP_FILES["op_amp"]))
    assert detect_sub_sheet(tree, file_path=str(_AMP_FILES["op_amp"])) is True


def test_tier3_pro_stem_no_match_audio():
    """Sub-sheet 'audio_jack' doesn't match → True."""
    if _skip_if_missing(_AMP_FILES["audio"]):
        return
    tree = parse_file(str(_AMP_FILES["audio"]))
    assert detect_sub_sheet(tree, file_path=str(_AMP_FILES["audio"])) is True


# === Tier 4: hierarchical_label fallback → sub-sheet ===

def test_tier4_hierarchical_label_means_subsheet():
    """Tree with hierarchical_label but no other markers → sub-sheet."""
    tree = ["kicad_sch",
            ["version", "20231120"],
            ["hierarchical_label", "VCC",
             ["shape", "input"],
             ["at", "50", "50", "0"]]]
    assert detect_sub_sheet(tree) is True


# === Tier 5: ambiguous default → False ===

def test_tier5_bare_tree_defaults_false():
    """Bare tree with no markers and no file_path → conservative False."""
    tree = ["kicad_sch", ["version", "20231120"]]
    assert detect_sub_sheet(tree) is False


# === Backward compatibility ===

def test_backward_compat_no_file_path():
    """Calling detect_sub_sheet(tree) without file_path still works on root."""
    if _skip_if_missing(_AMP_FILES["root"]):
        return
    tree = parse_file(str(_AMP_FILES["root"]))
    # Root has symbol_instances → tier 1 returns False even without file_path
    assert detect_sub_sheet(tree) is False


# === Zero false positives on root schematics ===

_ROOT_SCHEMATICS = [
    _REPOS / "57maker" / "headphone_amplifier_v0" / "headphone_amplifier_v0.kicad_sch",
    _REPOS / "bluepylons" / "A-Thinkpad-USB-keyboard" / "PCB" / "Thinkpad-USB-keyboard-PCB.kicad_sch",
    _REPOS / "CIRCUITSTATE" / "Mitayi-Pico-D1" / "Mitayi-Pico-D1.kicad_sch",
    _REPOS / "arnarg" / "nanopi-r4s-spi-flash-board" / "r4s_flash.kicad_sch",
    _REPOS / "arnarg" / "f3_backplane" / "f3_backplane.kicad_sch",
    _REPOS / "CrabikBoards" / "slot-esp32-s3-hardware" / "crabik-slot-esp32-s3.kicad_sch",
]


def test_zero_false_positives_on_roots():
    """Multiple root schematics from different repos all return False."""
    tested = 0
    for sch in _ROOT_SCHEMATICS:
        if not sch.exists():
            print(f"SKIP: {sch}")
            continue
        tree = parse_file(str(sch))
        result = detect_sub_sheet(tree, file_path=str(sch))
        assert result is False, f"False positive on root: {sch}"
        tested += 1
    if tested == 0:
        print("SKIP: no corpus root schematics found")
    else:
        print(f"Verified {tested} root schematics")


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
