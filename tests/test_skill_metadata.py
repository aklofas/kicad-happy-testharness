"""Tests for SKILL.md frontmatter constraints across all kicad-happy skills.

Codex enforces a 1024-character limit on skill description fields.
See kicad-happy 8e6bfa0 for the original fix.
"""

TIER = "unit"

import glob
import os
import re
import sys
from pathlib import Path

KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR",
    str(Path(__file__).resolve().parent.parent.parent / "kicad-happy"),
)
SKILLS_DIR = os.path.join(KICAD_HAPPY, "skills")

CODEX_DESCRIPTION_LIMIT = 1024


def _parse_frontmatter(path):
    """Extract name and description from SKILL.md YAML frontmatter."""
    with open(path) as f:
        text = f.read()
    if not text.startswith("---"):
        return None, None
    end = text.index("---", 3)
    fm = text[3:end]
    # name
    m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    name = m.group(1).strip() if m else None
    # description: >- block (folded scalar)
    m = re.search(r"^description:\s*>-?\s*\n((?:  .+\n)*)", fm, re.MULTILINE)
    if m:
        lines = m.group(1).rstrip("\n").split("\n")
        desc = " ".join(l.strip() for l in lines)
    else:
        # single-line
        m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        desc = m.group(1).strip() if m else None
    return name, desc


def _skill_files():
    """Discover all SKILL.md files in kicad-happy."""
    pattern = os.path.join(SKILLS_DIR, "*", "SKILL.md")
    return sorted(glob.glob(pattern))


def test_skill_files_exist():
    files = _skill_files()
    assert len(files) > 0, f"No SKILL.md files found under {SKILLS_DIR}"


def test_description_under_codex_limit():
    """Every SKILL.md description must fit within Codex's 1024-char limit."""
    violations = []
    for path in _skill_files():
        name, desc = _parse_frontmatter(path)
        if desc and len(desc) > CODEX_DESCRIPTION_LIMIT:
            violations.append(
                f"{name}: {len(desc)} chars (limit {CODEX_DESCRIPTION_LIMIT})"
            )
    assert not violations, (
        "SKILL.md description(s) exceed Codex 1024-char limit:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_frontmatter_has_name_and_description():
    """Every SKILL.md must have both name and description in frontmatter."""
    missing = []
    for path in _skill_files():
        name, desc = _parse_frontmatter(path)
        skill = os.path.basename(os.path.dirname(path))
        if not name:
            missing.append(f"{skill}: missing name")
        if not desc:
            missing.append(f"{skill}: missing description")
    assert not missing, "SKILL.md frontmatter issues:\n" + "\n".join(
        f"  {m}" for m in missing
    )


def test_name_matches_directory():
    """SKILL.md name field should match the containing directory name."""
    mismatches = []
    for path in _skill_files():
        name, _ = _parse_frontmatter(path)
        dirname = os.path.basename(os.path.dirname(path))
        if name and name != dirname:
            mismatches.append(f"{dirname}/SKILL.md: name={name!r}")
    assert not mismatches, "SKILL.md name/directory mismatches:\n" + "\n".join(
        f"  {m}" for m in mismatches
    )


# === Runner ===

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
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
