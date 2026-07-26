"""KH-359 consumer containment: matches_suppression() must match net
suppression patterns against the bare tail of a sheet-qualified net key
(/<sheet>/<name>), not just the raw key, so existing suppression configs
written against bare names keep working after KH-359 (see
test_kh359_kh360_netmap.py for the underlying build_net_map behavior)."""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from project_config import matches_suppression


def _finding(rule_id="RS-001", nets=None):
    return {"rule_id": rule_id, "nets": nets or []}


def _suppression(rule_id="RS-001", nets=None):
    s = {"rule_id": rule_id}
    if nets is not None:
        s["nets"] = nets
    return s


def test_bare_net_matches_bare_pattern_unchanged():
    finding = _finding(nets=["GND"])
    suppression = _suppression(nets=["GND"])
    assert matches_suppression(finding, suppression)


def test_qualified_net_matches_bare_tail_pattern():
    finding = _finding(nets=["/inc8b/GND"])
    suppression = _suppression(nets=["GND"])
    assert matches_suppression(finding, suppression)


def test_qualified_net_matches_bare_tail_glob_pattern():
    finding = _finding(nets=["/inc8b/USB_P"])
    suppression = _suppression(nets=["USB_*"])
    assert matches_suppression(finding, suppression)


def test_qualified_net_still_matches_full_qualified_pattern():
    finding = _finding(nets=["/inc8b/GND"])
    suppression = _suppression(nets=["/inc8b/*"])
    assert matches_suppression(finding, suppression)


def test_qualified_net_does_not_match_unrelated_pattern():
    finding = _finding(nets=["/inc8b/GND"])
    suppression = _suppression(nets=["VCC"])
    assert not matches_suppression(finding, suppression)


def test_single_slash_net_name_not_treated_as_qualified():
    # A literal net name containing exactly one "/" (count < 2) is not a
    # KH-359 sheet-qualified key -- no bare-tail fallback should apply,
    # so it must not spuriously match a pattern for its suffix.
    finding = _finding(nets=["A/B"])
    suppression = _suppression(nets=["B"])
    assert not matches_suppression(finding, suppression)
