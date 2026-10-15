"""The one required bridge from the harness to the kicad-happy product checkout.

Every suite that imports product modules or runs product scripts resolves the
product root here. The root comes from ``KICAD_HAPPY_DIR`` and must contain
``skills/kicad/scripts/analyze_schematic.py``. The sibling-directory fallback
(``../kicad-happy``) is an interactive convenience only and requires
``HARNESS_ALLOW_SIBLING_FALLBACK=1``; CI and evidence-producing runs must set
the env var explicitly (review A1).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]

_MARKER = Path("skills") / "kicad" / "scripts" / "analyze_schematic.py"


class ProductRootError(RuntimeError):
    """KICAD_HAPPY_DIR is missing or does not point at a product checkout."""


def resolve_product_root() -> Path:
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        root = Path(env).expanduser().resolve()
        if not (root / _MARKER).is_file():
            raise ProductRootError(
                f"KICAD_HAPPY_DIR={root} does not contain {_MARKER.as_posix()}; "
                "point it at a kicad-happy checkout")
        return root
    if os.environ.get("HARNESS_ALLOW_SIBLING_FALLBACK") == "1":
        sibling = (HARNESS_ROOT.parent / "kicad-happy").resolve()
        if (sibling / _MARKER).is_file():
            print(f"[product_root] WARNING: KICAD_HAPPY_DIR unset; using sibling "
                  f"fallback {sibling} (HARNESS_ALLOW_SIBLING_FALLBACK=1)", file=sys.stderr)
            return sibling
    raise ProductRootError(
        "KICAD_HAPPY_DIR env var not set; required for every harness suite. "
        "Example: KICAD_HAPPY_DIR=/path/to/kicad-happy python -m pytest. "
        "Interactive sibling fallback needs HARNESS_ALLOW_SIBLING_FALLBACK=1.")


PRODUCT_ROOT: Path = resolve_product_root()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def product_sha(root: Path = PRODUCT_ROOT) -> str:
    """Full 40-hex SHA of the product checkout."""
    return _git(root, "rev-parse", "HEAD")


def product_is_dirty(root: Path = PRODUCT_ROOT) -> bool:
    """True iff the product worktree has uncommitted or untracked changes."""
    return bool(_git(root, "status", "--porcelain"))


def script_dir(skill: str) -> Path:
    """``PRODUCT_ROOT/skills/<skill>/scripts`` (``skill`` may be ``kicad/review``)."""
    return PRODUCT_ROOT / "skills" / skill / "scripts"


def ensure_import_paths(*skills: str) -> None:
    """Idempotently put each skill's scripts dir at the front of ``sys.path``."""
    for skill in reversed(skills):
        p = str(script_dir(skill))
        if p not in sys.path:
            sys.path.insert(0, p)
