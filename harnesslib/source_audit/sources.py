"""Product source discovery and parsing shared by every harness scanner. ast only:
nothing here imports or evals product code."""
from __future__ import annotations

import ast
from pathlib import Path


def iter_product_sources(product_root: Path) -> list[Path]:
    """Every *.py under skills/**/scripts/** (recursive), sorted, no __pycache__."""
    root = Path(product_root)
    out: list[Path] = []
    for scripts_dir in sorted(root.glob("skills/*/scripts")) + sorted(root.glob("skills/*/*/scripts")):
        if not scripts_dir.is_dir():
            continue
        for p in scripts_dir.rglob("*.py"):
            if not p.is_file() or "__pycache__" in p.relative_to(root).parts:
                continue
            out.append(p)
    return sorted(set(out), key=lambda p: rel(root, p))


def rel(product_root: Path, path: Path) -> str:
    """Root-relative POSIX path (the identity used in every scanner output)."""
    return Path(path).resolve().relative_to(Path(product_root).resolve()).as_posix()


def parse_source(path: Path) -> ast.Module:
    """Parse honouring PEP 263 coding cookies / BOM: feed bytes, not text."""
    return ast.parse(Path(path).read_bytes(), filename=str(path))


def str_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None
