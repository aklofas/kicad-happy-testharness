#!/usr/bin/env python3
"""Reconcile BUGFIX-* regression assertions with the bugfix registry (TH-057).

Reads regression/bugfix_registry.json and brings every generator-owned
``*_bugfix.json`` under reference/ into agreement with it as ONE grouped
transaction per output file:

  added      id in registry, not in file
  updated    id in both, generator-owned fields differ (exact check diff shown)
  removed    id in file, no longer in registry (scoped by --issue)
  unchanged  identical

Dry-run is the default and prints every bucket with exact check diffs.
``--apply`` writes each file atomically (tmp + os.replace), preserves key
order, keeps non-generator keys (migration_note, schema_era, ...) on
retained records verbatim, and deletes a generator file whose last record
was removed. Hand-authored files at a generator path are never touched
(error). ``--issue KH-nnn`` restricts BOTH the desired set and removals to
that issue; other issues' records in the same file are preserved.

Output: reference/{repo}/{project}/assertions/{type}/{file}_bugfix.json

Usage:
    python3 regression/generate_bugfix_assertions.py                 # dry-run, all
    python3 regression/generate_bugfix_assertions.py --issue KH-150  # dry-run, one issue
    python3 regression/generate_bugfix_assertions.py --apply         # write
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR, _truncate_with_hash  # noqa: E402

REGISTRY_FILE = Path(__file__).resolve().parent / "bugfix_registry.json"
GENERATOR_MARKER = "generate_bugfix_assertions.py"
OWNED_KEYS = ("id", "description", "issue", "fix_type", "check")


class RegistryError(ValueError):
    """The registry cannot be turned into a consistent desired set."""


class HandAuthoredCollision(RuntimeError):
    """A non-generator file sits at a generator output path."""


def load_registry(path: Path = REGISTRY_FILE) -> list[dict]:
    """Load the bugfix registry; raise RegistryError if missing or malformed."""
    if not Path(path).exists():
        raise RegistryError(f"registry not found: {path}")
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RegistryError(f"registry must be a JSON list: {path}")
    return data


def infer_analyzer_type(ast_def: dict) -> str:
    atype = ast_def.get("analyzer_type", "")
    if atype:
        return atype
    source_file = ast_def.get("source_file", "")
    if source_file.endswith(".kicad_pcb"):
        return "pcb"
    return "schematic"


def safe_file_pattern(source_file: str) -> str:
    return _truncate_with_hash(source_file.replace("/", "_").replace("\\", "_"))


def target_path(reference_dir: Path, repo: str, project: str, atype: str,
                file_pattern: str) -> Path:
    return (Path(reference_dir) / repo / project / "assertions" / atype
            / _truncate_with_hash(f"{file_pattern}_bugfix.json"))


@dataclass
class FileGroup:
    path: Path
    file_pattern: str
    analyzer_type: str
    assertions: list[dict] = field(default_factory=list)


def desired_assertions(registry: list[dict], reference_dir: Path,
                       issue_filter: str | None = None) -> dict[Path, FileGroup]:
    """Registry -> {output path: FileGroup of generator-owned records}.

    Ids are ``BUGFIX-<issue>-<nn>`` by 1-based position among the entry's
    unpinned assertions unless the registry assertion pins an explicit ``id``.
    Raises RegistryError on an incomplete assertion, a bad pinned id, or two
    records minting the same id for the same output file.
    """
    groups: dict[Path, FileGroup] = {}
    for entry in registry:
        issue = entry.get("issue")
        if not issue:
            raise RegistryError(f"registry entry without 'issue': {entry!r}")
        if issue_filter and issue != issue_filter:
            continue
        fix_type = entry.get("type", "unknown")
        summary = entry.get("summary", "")
        auto_n = 0
        for i, ast_def in enumerate(entry.get("assertions", []), 1):
            for key in ("repo", "project", "source_file", "check"):
                if not ast_def.get(key):
                    raise RegistryError(
                        f"{issue} assertion #{i} is missing '{key}'")
            aid = ast_def.get("id")
            if not aid:
                auto_n += 1
                aid = f"BUGFIX-{issue}-{auto_n:02d}"
            if not isinstance(aid, str) or not aid.startswith("BUGFIX-"):
                raise RegistryError(
                    f"{issue} assertion #{i}: pinned id {aid!r} must start with 'BUGFIX-'")
            atype = infer_analyzer_type(ast_def)
            pattern = safe_file_pattern(ast_def["source_file"])
            path = target_path(reference_dir, ast_def["repo"], ast_def["project"],
                               atype, pattern)
            group = groups.setdefault(path, FileGroup(path, pattern, atype))
            if any(a["id"] == aid for a in group.assertions):
                raise RegistryError(
                    f"duplicate id {aid} for {path.name} "
                    f"(issue {issue}; pin an explicit 'id' on one of the entries)")
            group.assertions.append({
                "id": aid,
                "description": ast_def.get("description", f"{issue}: {summary}"),
                "issue": issue,
                "fix_type": fix_type,
                "check": ast_def["check"],
            })
    return groups
