"""Audit gold files for currency vs current schemas/PDFs/extractor (A7).

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.2.

Severity ladder:
    PDF SHA mismatch                            → ERROR
    base.schema_version major delta             → ERROR
    base.schema_version minor delta             → INFO
    per-category schema_version major delta     → ERROR
    per-category schema_version minor delta     → INFO
    extractor_schema_version mismatch           → INFO
    Malformed gold or meta                      → ERROR (category=malformed)

Exit codes:
    0  no ERROR findings
    1  one or more ERROR findings
    2  malformed gold or meta files
"""
from __future__ import annotations

import argparse
import enum
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

_HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS_ROOT))

from regression._mpn_slug import mpn_slug  # noqa: E402


class Severity(enum.Enum):
    """Four-tier severity ladder for currency findings."""

    OK = "ok"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Finding:
    """Single currency-check finding for one MPN."""

    mpn_slug: str
    severity: Severity
    category: str  # pdf_sha | schema_version_base | schema_version_category | extractor_version | malformed
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def _resolve_kicad_happy_dir() -> Path:
    """Resolve kicad-happy directory from KICAD_HAPPY_DIR env or sibling repo."""
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        return Path(env)
    return _HARNESS_ROOT.parent / "kicad-happy"


def _resolve_gold_dir(arg: Optional[str]) -> Path:
    """Resolve gold root from --gold-dir / env / harness default."""
    if arg:
        return Path(arg)
    env = os.environ.get("HARNESS_GOLD_DIR_OVERRIDE")
    if env:
        return Path(env)
    return _HARNESS_ROOT / "regression" / "reference_extractions"


def _resolve_pdf_dir(arg: Optional[str]) -> Path:
    """Resolve PDF directory from --pdf-dir or kicad-happy/datasheets/pdfs/."""
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "datasheets" / "pdfs"


def _resolve_schemas_dir(arg: Optional[str]) -> Path:
    """Resolve schemas dir from --schemas-dir or kicad-happy default."""
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "skills" / "datasheets" / "schemas"


def _compute_pdf_sha(pdf_path: Path) -> str:
    """Compute sha256 of a file in 64KB chunks."""
    h = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _major(version: str) -> int:
    """Extract major component from `<X>.<Y>` version string."""
    return int(version.split(".")[0])


def _minor(version: str) -> int:
    """Extract minor component from `<X>.<Y>` version string."""
    return int(version.split(".")[1])


def _read_current_schema_version(schemas_dir: Path, name: str,
                                  field_name: str = "version") -> Optional[str]:
    """Read a schema's declared version from its top-level field.

    Returns None if the schema file is absent or has no such field.
    """
    path = schemas_dir / f"{name}.schema.json"
    if not path.exists():
        return None
    try:
        schema = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    return schema.get(field_name)


def _read_current_extractor_version(schemas_dir: Path) -> Optional[str]:
    """Read extractor_schema_version from extraction.schema.json."""
    return _read_current_schema_version(schemas_dir, "extraction",
                                        field_name="extractor_schema_version")


def _audit_one(slug_dir: Path, *, pdf_dir: Path, schemas_dir: Path,
               meta_schema: dict) -> list[Finding]:
    """Audit a single gold dir; return a list of findings.

    Checks in order: meta validity, PDF SHA, base schema version,
    per-category schema versions, extractor version.
    """
    slug = slug_dir.name
    meta_path = slug_dir / "meta.json"

    if not meta_path.exists():
        return [Finding(slug, Severity.ERROR, "malformed",
                        f"meta.json missing in {slug_dir}")]

    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError as e:
        return [Finding(slug, Severity.ERROR, "malformed",
                        f"meta.json malformed: {e}")]

    # Validate meta against schema (if jsonschema available)
    try:
        from jsonschema import Draft202012Validator
        errors = list(Draft202012Validator(meta_schema).iter_errors(meta))
        if errors:
            return [Finding(slug, Severity.ERROR, "malformed",
                            f"meta.json fails _meta.schema.json: "
                            f"{errors[0].message}")]
    except ImportError:
        pass  # tolerate jsonschema absence

    findings: list[Finding] = []

    # PDF SHA check
    pdf_path = pdf_dir / meta["pdf_filename"]
    if not pdf_path.exists():
        findings.append(Finding(slug, Severity.ERROR, "pdf_sha",
                                f"PDF not found: {pdf_path}"))
    else:
        current_sha = _compute_pdf_sha(pdf_path)
        if current_sha != meta["pdf_sha256"]:
            findings.append(Finding(slug, Severity.ERROR, "pdf_sha",
                                    f"PDF SHA mismatch — gold "
                                    f"{meta['pdf_sha256'][:8]}…, "
                                    f"current {current_sha[:8]}…",
                                    details={"gold_sha": meta["pdf_sha256"],
                                             "current_sha": current_sha}))

    # Base schema check
    gold_base = meta["schema_version_at_curation"]["base"]
    current_base = _read_current_schema_version(schemas_dir, "base") or gold_base
    if _major(gold_base) != _major(current_base):
        findings.append(Finding(slug, Severity.ERROR, "schema_version_base",
                                f"base schema major delta — gold {gold_base}, "
                                f"current {current_base}",
                                details={"gold": gold_base, "current": current_base}))
    elif _minor(gold_base) != _minor(current_base):
        findings.append(Finding(slug, Severity.INFO, "schema_version_base",
                                f"base schema minor delta — gold {gold_base}, "
                                f"current {current_base} (gold predates current)",
                                details={"gold": gold_base, "current": current_base}))

    # Per-category schema check
    for cat, gold_ver in meta["schema_version_at_curation"]["categories"].items():
        current_ver = _read_current_schema_version(schemas_dir, cat) or gold_ver
        if _major(gold_ver) != _major(current_ver):
            findings.append(Finding(slug, Severity.ERROR,
                                    "schema_version_category",
                                    f"{cat} schema major delta — gold "
                                    f"{gold_ver}, current {current_ver}",
                                    details={"category": cat,
                                             "gold": gold_ver,
                                             "current": current_ver}))
        elif _minor(gold_ver) != _minor(current_ver):
            findings.append(Finding(slug, Severity.INFO,
                                    "schema_version_category",
                                    f"{cat} schema {gold_ver} → {current_ver} "
                                    f"(gold predates current)",
                                    details={"category": cat,
                                             "gold": gold_ver,
                                             "current": current_ver}))

    # Extractor version check
    gold_extractor = meta["extractor_schema_version_at_curation"]
    current_extractor = (_read_current_extractor_version(schemas_dir)
                         or gold_extractor)
    if gold_extractor != current_extractor:
        findings.append(Finding(slug, Severity.INFO, "extractor_version",
                                f"extractor_schema_version {gold_extractor} "
                                f"→ {current_extractor}",
                                details={"gold": gold_extractor,
                                         "current": current_extractor}))

    return findings


def _summary(all_findings: dict[str, list[Finding]]) -> dict[str, int]:
    """Aggregate counts by severity across all MPNs."""
    s = {"ok": 0, "info": 0, "warning": 0, "error": 0}
    for findings in all_findings.values():
        if not findings:
            s["ok"] += 1
            continue
        for f in findings:
            s[f.severity.value] += 1
    return s


def _print_human(all_findings: dict[str, list[Finding]], release: bool) -> None:
    """Print human-readable per-MPN report + summary."""
    print(f"Auditing {len(all_findings)} MPN(s) under "
          f"regression/reference_extractions/")
    print("─" * 60)
    for slug, findings in sorted(all_findings.items()):
        if not findings:
            print(f"[OK]    {slug}")
            continue
        for f in findings:
            sev = f.severity.value.upper()
            print(f"[{sev}]  {slug:25s}  {f.message}")
    print("─" * 60)
    s = _summary(all_findings)
    print(f"Summary: {s['ok']} OK, {s['info']} INFO, "
          f"{s['warning']} WARNING, {s['error']} ERROR")


def _print_json(all_findings: dict[str, list[Finding]]) -> None:
    """Print JSON report to stdout."""
    findings_flat = []
    for slug, findings in sorted(all_findings.items()):
        for f in findings:
            findings_flat.append({
                "mpn": slug,
                "severity": f.severity.value,
                "category": f.category,
                "message": f.message,
                **f.details,
            })
    payload = {
        "audited_count": len(all_findings),
        "summary": _summary(all_findings),
        "findings": findings_flat,
    }
    print(json.dumps(payload, indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point: parse args, audit gold dirs, print report, return exit code."""
    parser = argparse.ArgumentParser(
        description="Audit gold files for currency vs current schemas/PDFs/extractor.",
    )
    parser.add_argument("--mpn", default=None, help="Audit a single MPN's gold")
    parser.add_argument("--all", action="store_true",
                        help="Audit every dir under regression/reference_extractions/")
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable JSON output")
    parser.add_argument("--gold-dir", default=None, help="Override gold root")
    parser.add_argument("--pdf-dir", default=None, help="Where PDFs live")
    parser.add_argument("--schemas-dir", default=None,
                        help="Where current schemas live")
    parser.add_argument("--release", action="store_true",
                        help="Pre-release mode (Task 5: INFO escalates to "
                             "WARNING in human report)")
    parser.add_argument("--known-divergences", default=None,
                        help="Path to _KNOWN_DIVERGENCES.md for cross-reference "
                             "(Task 5)")
    args = parser.parse_args(argv)

    if not args.mpn and not args.all:
        args.all = True

    gold_root = _resolve_gold_dir(args.gold_dir)
    pdf_dir = _resolve_pdf_dir(args.pdf_dir)
    schemas_dir = _resolve_schemas_dir(args.schemas_dir)

    meta_schema_path = gold_root / "_meta.schema.json"
    if not meta_schema_path.exists():
        print(f"ERROR: _meta.schema.json missing at {meta_schema_path}",
              file=sys.stderr)
        return 2
    meta_schema = json.loads(meta_schema_path.read_text())

    # Discover gold dirs
    if args.mpn:
        slug_dirs = [gold_root / mpn_slug(args.mpn)]
    else:
        slug_dirs = [d for d in gold_root.iterdir()
                     if d.is_dir() and not d.name.startswith("_")
                     and not d.name.startswith("archived_")]

    all_findings: dict[str, list[Finding]] = {}
    has_malformed = False
    for slug_dir in sorted(slug_dirs):
        try:
            findings = _audit_one(slug_dir, pdf_dir=pdf_dir,
                                  schemas_dir=schemas_dir,
                                  meta_schema=meta_schema)
        except Exception as e:
            findings = [Finding(slug_dir.name, Severity.ERROR, "malformed",
                                f"audit error: {e}")]
        all_findings[slug_dir.name] = findings
        if any(f.category == "malformed" for f in findings):
            has_malformed = True

    if args.json:
        _print_json(all_findings)
    else:
        _print_human(all_findings, release=args.release)

    if has_malformed:
        return 2
    if any(f.severity is Severity.ERROR for fl in all_findings.values()
           for f in fl):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
