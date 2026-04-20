"""Test fixture helpers for A3/A4 datasheet consumer API tests.

See docs/superpowers/specs/2026-04-19-a3-a4-joint-test-plan.md for the
full plan these fixtures support.
"""
import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent.parent.parent
KICAD_HAPPY_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", HARNESS_DIR.parent / "kicad-happy"))
DATASHEETS_SKILL = KICAD_HAPPY_DIR / "skills" / "datasheets"

if str(DATASHEETS_SKILL) not in sys.path:
    sys.path.insert(0, str(DATASHEETS_SKILL))
if str(DATASHEETS_SKILL / "scripts") not in sys.path:
    sys.path.insert(0, str(DATASHEETS_SKILL / "scripts"))

FIXTURE_DIR = DATASHEETS_SKILL / "schemas" / "fixtures"
