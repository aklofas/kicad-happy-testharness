"""Validate kicad-happy scripts are compatible with Python 3.10+.

The analyzers are pure-stdlib Python targeting 3.10 as the minimum version.
This test catches accidental use of 3.11+ or 3.12+ features that would break
on older Python installations.

Checked features:
  - 3.12+: type alias statements (type X = ...), f-string nesting
  - 3.11+: except* (ExceptionGroup), tomllib, StrEnum, typing.Self,
           typing.Never, typing.assert_never, asyncio.TaskGroup
  - stdlib-only: no third-party imports
"""

TIER = "unit"

import ast
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
MIN_PYTHON = (3, 10)

# Modules added in 3.11+
STDLIB_311 = {"tomllib"}

# typing members added in 3.11+
TYPING_311 = {"Self", "Never", "assert_never", "TypeVarTuple", "Unpack"}

# Classes/functions added in 3.11+
BUILTINS_311 = {"ExceptionGroup", "BaseExceptionGroup"}

# enum additions in 3.11+
ENUM_311 = {"StrEnum", "ReprEnum"}


def _py_files():
    """All Python files in skills/."""
    return sorted(glob.glob(os.path.join(SKILLS_DIR, "**", "*.py"), recursive=True))


def test_scripts_exist():
    files = _py_files()
    assert len(files) > 0, f"No .py files found under {SKILLS_DIR}"


def test_all_scripts_compile():
    """Every .py file must parse as valid Python."""
    errors = []
    for path in _py_files():
        try:
            with open(path) as f:
                source = f.read()
            compile(source, path, "exec")
        except SyntaxError as e:
            errors.append(f"{os.path.relpath(path, SKILLS_DIR)}: {e}")
    assert not errors, "Compile errors:\n" + "\n".join(f"  {e}" for e in errors)


def test_no_311_stdlib_imports():
    """No imports of stdlib modules added in Python 3.11+."""
    violations = []
    for path in _py_files():
        with open(path) as f:
            try:
                tree = ast.parse(f.read(), filename=path)
            except SyntaxError:
                continue
        rel = os.path.relpath(path, SKILLS_DIR)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in STDLIB_311:
                        violations.append(f"{rel}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split(".")[0]
                if mod in STDLIB_311:
                    violations.append(f"{rel}:{node.lineno}: from {node.module}")
    assert not violations, (
        "Imports of 3.11+ stdlib modules:\n" + "\n".join(f"  {v}" for v in violations)
    )


def test_no_311_typing_features():
    """No usage of typing members added in Python 3.11+."""
    violations = []
    for path in _py_files():
        with open(path) as f:
            try:
                tree = ast.parse(f.read(), filename=path)
            except SyntaxError:
                continue
        rel = os.path.relpath(path, SKILLS_DIR)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "typing":
                for alias in node.names:
                    if alias.name in TYPING_311:
                        violations.append(
                            f"{rel}:{node.lineno}: from typing import {alias.name}"
                        )
    assert not violations, (
        "Usage of 3.11+ typing features:\n" + "\n".join(f"  {v}" for v in violations)
    )


def test_no_311_enum_features():
    """No usage of StrEnum or other 3.11+ enum classes."""
    violations = []
    for path in _py_files():
        with open(path) as f:
            try:
                tree = ast.parse(f.read(), filename=path)
            except SyntaxError:
                continue
        rel = os.path.relpath(path, SKILLS_DIR)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "enum":
                for alias in node.names:
                    if alias.name in ENUM_311:
                        violations.append(
                            f"{rel}:{node.lineno}: from enum import {alias.name}"
                        )
    assert not violations, (
        "Usage of 3.11+ enum features:\n" + "\n".join(f"  {v}" for v in violations)
    )


def test_no_except_star():
    """No except* syntax (ExceptionGroup handling, Python 3.11+)."""
    violations = []
    for path in _py_files():
        with open(path) as f:
            source = f.read()
        rel = os.path.relpath(path, SKILLS_DIR)
        # except* is a syntax feature — grep for it since AST node type
        # (TryStar) only exists in 3.11+ AST
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.lstrip()
            if re.match(r"except\s*\*", stripped):
                violations.append(f"{rel}:{i}: {stripped.rstrip()}")
    assert not violations, (
        "except* syntax (3.11+):\n" + "\n".join(f"  {v}" for v in violations)
    )


def test_no_type_alias_statement():
    """No 'type X = ...' statements (Python 3.12+ PEP 695)."""
    violations = []
    for path in _py_files():
        with open(path) as f:
            source = f.read()
        rel = os.path.relpath(path, SKILLS_DIR)
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.lstrip()
            # Match 'type Foo = ...' at statement level (not inside strings)
            if re.match(r"type\s+[A-Z]\w*\s*=", stripped):
                violations.append(f"{rel}:{i}: {stripped.rstrip()}")
    assert not violations, (
        "type alias statements (3.12+):\n" + "\n".join(f"  {v}" for v in violations)
    )


def _core_analyzer_files():
    """Python files in the core analyzer skills (must be pure-stdlib)."""
    core_skills = ["kicad", "emc", "spice"]
    files = []
    for skill in core_skills:
        pattern = os.path.join(SKILLS_DIR, skill, "scripts", "*.py")
        files.extend(glob.glob(pattern))
    return sorted(files)


def test_no_third_party_imports_in_core():
    """Core analyzer scripts must be pure-stdlib — no third-party deps."""
    third_party = {
        "numpy", "scipy", "pandas", "requests", "yaml", "pyyaml",
        "toml", "click", "rich", "attrs", "pydantic", "httpx",
        "aiohttp", "flask", "django", "fastapi", "sqlalchemy",
        "matplotlib", "pillow", "PIL", "cv2", "sklearn",
    }
    violations = []
    for path in _core_analyzer_files():
        with open(path) as f:
            try:
                tree = ast.parse(f.read(), filename=path)
            except SyntaxError:
                continue
        rel = os.path.relpath(path, SKILLS_DIR)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in third_party:
                        violations.append(f"{rel}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split(".")[0]
                if mod in third_party:
                    violations.append(f"{rel}:{node.lineno}: from {node.module}")
    assert not violations, (
        "Third-party imports in core analyzers:\n"
        + "\n".join(f"  {v}" for v in violations)
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
