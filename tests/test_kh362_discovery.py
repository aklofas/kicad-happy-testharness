"""
KH-362: .kicad_pro / .kicad_dru discovery must match by board stem.

`load_kicad_pro` and `load_kicad_dru` in kicad_utils.py used to take
whatever ``*.kicad_pro`` / ``*.kicad_dru`` file `os.listdir` happened to
list first in the directory. In a multi-project directory (several
boards sharing a folder) that silently picks the wrong project's
net classes / design rules depending on OS/filesystem listing order.

Fix: prefer the candidate whose stem matches the input file's stem
(KiCad names project/rules files after the board they belong to). With
exactly one candidate, use it regardless of stem (single-project
directories are the overwhelmingly common case). With multiple
candidates and no stem match, fall back to the first candidate sorted
alphabetically (deterministic) and print a warning to stderr — both
loaders return a bare dict/list (no metadata slot), so the note can
only travel via stderr, not the return value.

`load_kicad_pro` additionally now routes through project_config's
JSONC-tolerant `load_jsonc` (KH-368) instead of raw `json.load`, so a
commented `.kicad_pro` no longer fails discovery outright.
"""

TIER = "unit"

import json
import os
import shutil
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import kicad_utils  # noqa: E402
from analyze_pcb import analyze_pcb, analyze_design_rule_compliance  # noqa: E402

_FIXTURE_DIR = _HARNESS / "tests" / "fixtures" / "simple-project"

_DRU_A = '(rule "Rule A"\n  (constraint track_width (min 0.1mm))\n)\n'
_DRU_B = '(rule "Rule B"\n  (constraint track_width (min 0.2mm))\n)\n'


def _write_pro(path, marker):
    with open(path, "w") as f:
        json.dump({"_marker": marker}, f)


def _write_dru(path, content):
    with open(path, "w") as f:
        f.write(content)


# --- .kicad_pro -------------------------------------------------------

def test_pro_stem_match_picks_correct_project(tmp_path):
    _write_pro(tmp_path / "boardA.kicad_pro", "A")
    _write_pro(tmp_path / "boardB.kicad_pro", "B")
    (tmp_path / "boardB.kicad_pcb").touch()

    result = kicad_utils.load_kicad_pro(str(tmp_path / "boardB.kicad_pcb"))
    assert result == {"_marker": "B"}


def test_pro_single_non_matching_stem_still_returned(tmp_path, capsys):
    _write_pro(tmp_path / "onlyone.kicad_pro", "only")
    (tmp_path / "target.kicad_pcb").touch()

    result = kicad_utils.load_kicad_pro(str(tmp_path / "target.kicad_pcb"))
    assert result == {"_marker": "only"}
    assert capsys.readouterr().err == ""


def test_pro_ambiguous_no_match_warns_and_falls_back(tmp_path, capsys):
    _write_pro(tmp_path / "other1.kicad_pro", "other1")
    _write_pro(tmp_path / "other2.kicad_pro", "other2")
    (tmp_path / "target.kicad_pcb").touch()

    result = kicad_utils.load_kicad_pro(str(tmp_path / "target.kicad_pcb"))
    # Deterministic fallback: alphabetically first candidate.
    assert result == {"_marker": "other1"}
    assert "target" in capsys.readouterr().err


def test_pro_tolerates_commented_json(tmp_path):
    (tmp_path / "commented.kicad_pro").write_text(
        '{\n// a comment\n"_marker": "c",\n}'
    )
    (tmp_path / "commented.kicad_pcb").touch()

    result = kicad_utils.load_kicad_pro(str(tmp_path / "commented.kicad_pcb"))
    assert result == {"_marker": "c"}


def test_pro_no_candidates_returns_none(tmp_path):
    (tmp_path / "target.kicad_pcb").touch()
    assert kicad_utils.load_kicad_pro(str(tmp_path / "target.kicad_pcb")) is None


# --- .kicad_dru ---------------------------------------------------------

def test_dru_stem_match_picks_correct_ruleset(tmp_path):
    _write_dru(tmp_path / "boardA.kicad_dru", _DRU_A)
    _write_dru(tmp_path / "boardB.kicad_dru", _DRU_B)
    (tmp_path / "boardB.kicad_pcb").touch()

    result = kicad_utils.load_kicad_dru(str(tmp_path / "boardB.kicad_pcb"))
    assert result[0]["name"] == "Rule B"


def test_dru_single_non_matching_stem_still_returned(tmp_path, capsys):
    _write_dru(tmp_path / "onlyone.kicad_dru", _DRU_A)
    (tmp_path / "target.kicad_pcb").touch()

    result = kicad_utils.load_kicad_dru(str(tmp_path / "target.kicad_pcb"))
    assert result[0]["name"] == "Rule A"
    assert capsys.readouterr().err == ""


def test_dru_ambiguous_no_match_warns_and_falls_back(tmp_path, capsys):
    _write_dru(tmp_path / "other1.kicad_dru", _DRU_A)
    _write_dru(tmp_path / "other2.kicad_dru", _DRU_B)
    (tmp_path / "target.kicad_pcb").touch()

    result = kicad_utils.load_kicad_dru(str(tmp_path / "target.kicad_pcb"))
    assert result[0]["name"] == "Rule A"  # sorted first candidate
    assert "target" in capsys.readouterr().err


def test_dru_no_candidates_returns_none(tmp_path):
    (tmp_path / "target.kicad_pcb").touch()
    assert kicad_utils.load_kicad_dru(str(tmp_path / "target.kicad_pcb")) is None


# --- scope-bump: analyze_pcb.py's project_settings['source'] must agree
# with the loader (KH-362 follow-up) --------------------------------------

def test_analyze_pcb_source_field_matches_loaded_settings(tmp_path, monkeypatch):
    """analyze_pcb's project_settings['source'] used to come from its own
    independent, unsorted first-glob rescan — separate from the (now
    stem-matched) load_kicad_pro() call two lines above it. In a
    multi-project directory that could name a DIFFERENT .kicad_pro than
    the one whose net_classes/design_rules were actually loaded: a wrong
    provenance claim, and itself a live filesystem-order nondeterminism
    bug. Both must now derive from the same find_project_settings_file()
    call, so 'source' always names the file whose settings are present.

    `os.listdir` order is filesystem-dependent and can coincidentally
    already agree with alphabetical order (masking the bug), so this
    forces an adversarial listing — the decoy sorted first — rather than
    trusting real FS behavior to expose it.
    """
    shutil.copy(_FIXTURE_DIR / "simple.kicad_pcb", tmp_path / "boardB.kicad_pcb")
    shutil.copy(_FIXTURE_DIR / "simple.kicad_pro", tmp_path / "boardB.kicad_pro")

    # A second, distinguishable .kicad_pro sharing the directory but NOT
    # boardB's stem.
    decoy = json.loads((_FIXTURE_DIR / "simple.kicad_pro").read_text())
    decoy.setdefault("board", {}).setdefault(
        "design_settings", {}).setdefault("rules", {})["min_clearance"] = 0.999
    (tmp_path / "boardA.kicad_pro").write_text(json.dumps(decoy))

    real_listdir = os.listdir

    def _adversarial_listdir(path):
        # Force the decoy (boardA) to head the raw listing regardless of
        # what the real filesystem returns — the worst case for any code
        # path that takes the first `.kicad_pro` hit without sorting.
        return sorted(real_listdir(path), key=lambda f: (f != "boardA.kicad_pro", f))

    monkeypatch.setattr(os, "listdir", _adversarial_listdir)

    result = analyze_pcb(str(tmp_path / "boardB.kicad_pcb"))
    settings = result["project_settings"]
    assert settings["source"] == "boardB.kicad_pro"
    assert settings["design_rules"]["min_clearance"] != 0.999


# --- KH-361: .kicad_dru conditional rules must be skipped, not applied
# board-wide -----------------------------------------------------------
#
# load_kicad_dru() keeps `condition` as a raw, unevaluated string (see its
# docstring above). analyze_design_rule_compliance() used to check every
# custom rule's constraints as an unconditional board-wide minimum, so a
# rule like `(condition "A.isPlated()")` guarding a hole_size constraint
# got enforced against every hole on the board, plated or not — false
# violations on any unplated hole smaller than the plated minimum.

_DRU_CONDITIONAL_AND_UNCONDITIONAL = (
    '(rule "plated hole size"\n'
    '  (condition "A.isPlated()")\n'
    '  (constraint hole_size (min 0.3mm))\n'
    ')\n'
    '(rule "min track width"\n'
    '  (constraint track_width (min 0.25mm))\n'
    ')\n'
)


def test_conditional_rule_skipped_unconditional_still_enforced(tmp_path):
    _write_dru(tmp_path / "board.kicad_dru", _DRU_CONDITIONAL_AND_UNCONDITIONAL)
    (tmp_path / "board.kicad_pcb").touch()

    custom_rules = kicad_utils.load_kicad_dru(str(tmp_path / "board.kicad_pcb"))
    assert custom_rules is not None

    # 0.2mm drill: would violate the conditional plated-hole-size rule
    # (min 0.3mm) if applied board-wide, but the hole is unplated and the
    # rule's condition is never evaluated — it must be skipped, not
    # enforced.
    tracks = {"segments": [{"width": 0.2}], "arcs": []}
    vias = {"vias": [{"size": 0.5, "drill": 0.2}]}
    project_settings = {"custom_rules": custom_rules}

    result = analyze_design_rule_compliance(tracks, vias, project_settings)

    violation_rules = [v["rule"] for v in result.get("violations", [])]
    assert "custom:plated hole size" not in violation_rules
    assert "custom:min track width" in violation_rules

    assert result["conditional_rules_skipped"] == ["plated hole size"]
    assert result["conditional_rules_skipped_count"] == 1
    assert result["conditional_rules_note"] == (
        "1 conditional rule not evaluated (condition support: none) "
        "— not applied board-wide"
    )
