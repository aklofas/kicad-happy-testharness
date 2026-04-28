"""Promote a gate-passed extraction to gold (A7).

Reads a v1.4 datasheet extraction cache file, re-runs the A6 acceptance gate,
re-runs the sanity-vector diff, validates the cache against the current
extraction schema, prompts the user, and writes gold + meta on confirm.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.1.

Exit codes:
    0  promoted (gold + meta written)
    1  aborted by user at confirmation prompt
    2  blocked: gate failed / sanity-vector mismatch / schema-validation failed
    3  blocked: cache file not found / malformed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# regression/ → harness root
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS_ROOT))

from regression._mpn_slug import mpn_slug  # noqa: E402


def _resolve_kicad_happy_dir() -> Path:
    """Resolve kicad-happy directory from KICAD_HAPPY_DIR env or sibling repo."""
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        return Path(env)
    return _HARNESS_ROOT.parent / "kicad-happy"


def _resolve_cache_dir(arg: Optional[str]) -> Path:
    """Resolve cache dir from --cache-dir or kicad-happy/datasheets/extracted/."""
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "datasheets" / "extracted"


def _load_cache(cache_path: Path) -> dict:
    """Load and parse JSON cache file. Exits 3 on missing or malformed file."""
    if not cache_path.exists():
        print(f"ERROR: cache file not found: {cache_path}", file=sys.stderr)
        sys.exit(3)
    try:
        return json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cache file unreadable: {e}", file=sys.stderr)
        sys.exit(3)


def _resolve_sanity_dir(arg: Optional[Path] = None) -> Path:
    """Sanity-vector directory, with env override hook for tests.

    Priority: HARNESS_SANITY_DIR_OVERRIDE env var → --sanity-dir arg →
    reference/datasheets/sanity_vectors/ (harness default).
    """
    env = os.environ.get("HARNESS_SANITY_DIR_OVERRIDE")
    if env:
        return Path(env)
    if arg:
        return arg
    return _HARNESS_ROOT / "reference" / "datasheets" / "sanity_vectors"


def _run_a6_gate(mpn: str, cache_dir: Path) -> tuple[bool, str]:
    """Re-run A6 acceptance gate against an extraction cache directory.

    Invokes validate/check_acceptance_gate.py as a subprocess and returns
    (all_pass, combined_stdout_stderr). Exit code 0 → all 4 checks passed.
    Any other exit code is treated as a gate failure.
    """
    gate_cli = _HARNESS_ROOT / "validate" / "check_acceptance_gate.py"
    cmd = [sys.executable, str(gate_cli), "--mpn", mpn, "--extract-dir", str(cache_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return (proc.returncode == 0, proc.stdout + proc.stderr)


def _walk_path(obj: Any, path: str) -> Any:
    """Walk a dotted path through nested dicts.

    Returns None if any segment is missing or the traversal hits a non-dict.
    Example: _walk_path(cache, "base.package.pin_count") → 5
    """
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _coerce_specvalue(v: Any) -> Optional[dict]:
    """Coerce a cache field value to a comparable SpecValue-shaped dict.

    Mirrors validate/check_acceptance_gate.py:_resolve_actual to keep
    comparison semantics identical without a cross-module import.

    Coercion rules:
      list  → first element (or None if empty)
      bool  → {"typ": v}  (must precede int check; bool is int subclass)
      int/float → {"typ": v}
      str   → {"name": v, "code": v}
      dict  → returned as-is
      None/other → None
    """
    if v is None:
        return None
    if isinstance(v, list):
        return v[0] if v else None
    if isinstance(v, bool):
        return {"typ": v}
    if isinstance(v, (int, float)):
        return {"typ": v}
    if isinstance(v, str):
        return {"name": v, "code": v}
    if isinstance(v, dict):
        return v
    return None


def _compare_sanity_field(expected: dict, actual: Optional[dict],
                           tolerance_pct: float) -> Optional[str]:
    """Compare a single sanity-vector field against the actual cache value.

    Returns None if within tolerance, or a human-readable reason string if
    the field diverges. Mirrors _compare_field in check_acceptance_gate.py.

    Tolerance: |actual - expected| / |expected| * 100 <= tolerance_pct.
    Unit must match string-equal. Missing expected numeric keys in actual
    are divergences.
    """
    if actual is None:
        return "path not found in cache"
    if "unit" in expected and expected["unit"] != actual.get("unit"):
        return (f"unit_mismatch (expected {expected['unit']!r}, "
                f"got {actual.get('unit')!r})")
    for key in ("min", "typ", "max"):
        if key not in expected:
            continue
        exp = expected[key]
        act = actual.get(key)
        if act is None:
            return f"key_missing_in_cache: {key}"
        if (isinstance(exp, (int, float)) and not isinstance(exp, bool)
                and isinstance(act, (int, float)) and not isinstance(act, bool)):
            if exp == 0:
                if act != 0:
                    return f"nonzero_against_zero: {key}"
                continue
            delta = abs(act - exp) / abs(exp) * 100
            if delta > tolerance_pct:
                return (f"{key}: |{act} - {exp}| / |{exp}| "
                        f"= {delta:.2f}% > {tolerance_pct}%")
        else:
            if exp != act:
                return f"value_mismatch: {key}"
    return None


def _resolve_gold_dir() -> Path:
    """Resolve gold root, with HARNESS_GOLD_DIR_OVERRIDE for tests."""
    env = os.environ.get("HARNESS_GOLD_DIR_OVERRIDE")
    if env:
        return Path(env)
    return _HARNESS_ROOT / "regression" / "reference_extractions"


def _resolve_pdf_dir(arg: Optional[str]) -> Path:
    """Resolve PDF directory from --pdf-dir or kicad-happy/datasheets/pdfs/."""
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "datasheets" / "pdfs"


def _validate_cache_schema(cache: dict, kicad_happy_dir: Path) -> tuple[bool, str]:
    """Validate cache against extraction.schema.json.

    Returns (ok, summary). Tolerates jsonschema absence (returns ok=True with
    'skipping' message) and tolerates a missing schema file (same).
    """
    schema_path = (kicad_happy_dir / "skills" / "datasheets" / "schemas"
                   / "extraction.schema.json")
    if not schema_path.exists():
        return True, "extraction.schema.json not found, skipping validation"
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError as e:
        return True, f"jsonschema not available, skipping ({e})"
    try:
        schema = json.loads(schema_path.read_text())
        registry = Registry()
        for sib in schema_path.parent.glob("*.schema.json"):
            sib_schema = json.loads(sib.read_text())
            sib_id = sib_schema.get("$id", sib.name)
            registry = registry.with_resource(sib_id, Resource.from_contents(sib_schema))
        validator = Draft202012Validator(schema, registry=registry)
        errors = list(validator.iter_errors(cache))
        if errors:
            return False, "; ".join(str(e.message) for e in errors[:3])
        return True, "ok"
    except Exception as e:
        return False, f"validation error: {e}"


def _compute_pdf_sha(pdf_path: Path) -> str:
    """Compute sha256 of a file in 64KB chunks."""
    h = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now_iso() -> str:
    """Return current UTC time in ISO-8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _archive_existing(slug_dir: Path, old_pdf_sha: str) -> None:
    """Move existing gold_v*.json + meta.json into archived_pdf_sha_<old>/."""
    archive = slug_dir / f"archived_pdf_sha_{old_pdf_sha}"
    archive.mkdir(parents=True, exist_ok=True)
    candidates = list(slug_dir.glob("gold_v*.json")) + [slug_dir / "meta.json"]
    for src in candidates:
        if src.exists() and src.is_file():
            shutil.move(str(src), str(archive / src.name))


def _write_gold(slug_dir: Path, base_version: str, cache: dict) -> Path:
    """Write gold_v<base>.json (cache copy with sorted keys, pretty-printed)."""
    slug_dir.mkdir(parents=True, exist_ok=True)
    gold_path = slug_dir / f"gold_v{base_version}.json"
    gold_path.write_text(json.dumps(cache, indent=2, sort_keys=True))
    return gold_path


def _build_meta(*, mpn: str, cache: dict, pdf_filename: str, pdf_sha: str,
                cache_path: Path, sanity_vector_path: Path,
                sanity_pass: bool, sanity_field_count: int,
                gate_run_id: Optional[str], gate_quality_score: int,
                event: str, prior_meta: Optional[dict] = None,
                from_schema_version: Optional[dict] = None) -> dict:
    """Build a meta.json dict from a cache + curation context.

    Appends to prior_meta['history'] if provided; otherwise creates a fresh
    history list with a single entry. The event field on the new history
    entry is one of: initial / update / pdf_sha_change / recurate_major_bump.
    """
    schema_block = cache["schema_version"]
    now = _now_iso()
    history_entry: dict = {
        "event": event,
        "at": now,
        "pdf_sha256": pdf_sha,
        "schema_version": schema_block,
        "gate_quality_score": gate_quality_score,
    }
    if from_schema_version is not None:
        history_entry["from_schema_version"] = from_schema_version
    if prior_meta:
        history = list(prior_meta.get("history", [])) + [history_entry]
    else:
        history = [history_entry]
    return {
        "mpn": mpn,
        "mpn_slug": mpn_slug(mpn),
        "pdf_sha256": pdf_sha,
        "pdf_filename": pdf_filename,
        "schema_version_at_curation": schema_block,
        "extractor_schema_version_at_curation": cache["extraction"]["extractor_schema_version"],
        "curated_at": now,
        "curated_from": {
            "cache_path": str(cache_path),
            "gate_run_id": gate_run_id,
            "gate_quality_score": gate_quality_score,
            "sanity_vector_path": str(sanity_vector_path),
            "sanity_vector_pass": sanity_pass,
            "sanity_vector_field_count": sanity_field_count,
        },
        "history": history,
    }


def _run_sanity_diff(mpn: str, cache: dict,
                      sanity_dir: Path) -> tuple[bool, list[dict]]:
    """Run sanity-vector diff for an MPN against its cached extraction.

    Loads <sanity_dir>/<mpn_slug>.json and evaluates each field against the
    cache. Returns (all_pass, divergences) where divergences is a list of
    dicts with 'path' and 'reason' keys.

    Returns (False, [reason]) if the sanity vector file is not found.
    """
    slug = mpn_slug(mpn)
    vector_path = sanity_dir / f"{slug}.json"
    if not vector_path.exists():
        return False, [{"reason": f"sanity vector not found: {vector_path}"}]
    vector = json.loads(vector_path.read_text())
    divergences: list[dict] = []
    for fld in vector["fields"]:
        actual = _coerce_specvalue(_walk_path(cache, fld["path"]))
        reason = _compare_sanity_field(fld["expected"], actual,
                                        fld.get("tolerance_pct", 0))
        if reason:
            divergences.append({"path": fld["path"], "reason": reason})
    return (len(divergences) == 0, divergences)


def _do_recurate_from(*, args, cache: dict, cache_path: Path) -> int:
    """Execute the --re-curate-from sweep flow.

    Pre-conditions:
      - existing gold + meta exist at the slug dir
      - cache's base schema major != prior gold's base schema major

    Steps:
      1. Validate pre-conditions (prior gold exists, majors differ)
      2. Run gate (unless --no-gate) + sanity diff + cache schema validation
      3. Show A5 differ output (cache vs old gold)
      4. Confirm (or skip with --yes)
      5. Rename existing gold_v<old>.json → gold_v<old>.json.archived in place
      6. Write new gold_v<new>.json
      7. Update meta.json with event='recurate_major_bump' + from_schema_version
    """
    gold_root = _resolve_gold_dir()
    slug_dir = gold_root / mpn_slug(args.mpn)
    prior_gold_path = slug_dir / f"gold_v{args.re_curate_from}.json"
    prior_meta_path = slug_dir / "meta.json"

    if not prior_gold_path.exists() or not prior_meta_path.exists():
        print(f"ERROR: --re-curate-from {args.re_curate_from} but no prior gold "
              f"at {prior_gold_path}", file=sys.stderr)
        return 2

    prior_meta = json.loads(prior_meta_path.read_text())
    prior_base = prior_meta["schema_version_at_curation"]["base"]
    new_base = cache["schema_version"]["base"]

    try:
        prior_major = int(prior_base.split(".")[0])
        new_major = int(new_base.split(".")[0])
    except (ValueError, IndexError):
        print(f"ERROR: malformed schema version (prior {prior_base!r}, "
              f"new {new_base!r})", file=sys.stderr)
        return 2

    if prior_major == new_major:
        print(f"ERROR: --re-curate-from precondition fails — prior base {prior_base} "
              f"and new base {new_base} shares major version {new_major}; "
              f"normal promote handles this case", file=sys.stderr)
        return 2

    # Run gate (unless --no-gate) + sanity diff + cache schema validation
    cache_dir = _resolve_cache_dir(args.cache_dir)
    if not args.no_gate:
        gate_pass, gate_summary = _run_a6_gate(args.mpn, cache_dir)
        if not gate_pass:
            print("ERROR: A6 gate did not pass 4/4. Promotion blocked.",
                  file=sys.stderr)
            print(gate_summary, file=sys.stderr)
            return 2
        print("[ok] A6 gate: 4/4 PASS")

    sanity_dir = _resolve_sanity_dir()
    sanity_pass, divergences = _run_sanity_diff(args.mpn, cache, sanity_dir)
    if not sanity_pass:
        print("ERROR: sanity-vector diff has divergences. Promotion blocked.",
              file=sys.stderr)
        for d in divergences:
            print(f"  - {d.get('path', '<no path>')}: {d['reason']}",
                  file=sys.stderr)
        return 2
    print("[ok] sanity-vector diff: all fields within tolerance")

    kicad_happy_dir = _resolve_kicad_happy_dir()
    schema_ok, schema_summary = _validate_cache_schema(cache, kicad_happy_dir)
    if not schema_ok:
        print(f"ERROR: cache fails extraction.schema.json: {schema_summary}",
              file=sys.stderr)
        return 2
    print(f"[ok] cache schema validation: {schema_summary}")

    # Show A5 differ output (best-effort; non-fatal if differ fails)
    print(f"\n=== Re-curation diff: schema {prior_base} → {new_base} ===")
    differ_cli = _HARNESS_ROOT / "regression" / "extraction_differ.py"
    if differ_cli.exists():
        diff_proc = subprocess.run(
            [sys.executable, str(differ_cli),
             "--gold", str(prior_gold_path),
             "--candidate", str(cache_path)],
            capture_output=True, text=True,
        )
        print(diff_proc.stdout)
    else:
        print(f"(A5 differ not found at {differ_cli}; skipping diff display)")

    # Confirm (or skip with --yes)
    if not args.yes:
        ans = input(f"Re-curate from {prior_base} to {new_base}? [y/N]: ").strip().lower()
        if ans != "y":
            print("Aborted.")
            return 1

    # Rename existing gold in place to .archived (no separate dir)
    archived_path = slug_dir / f"gold_v{prior_base}.json.archived"
    prior_gold_path.rename(archived_path)

    # Write new gold
    _write_gold(slug_dir, new_base, cache)

    # Compute pdf_sha for meta
    pdf_dir = _resolve_pdf_dir(args.pdf_dir)
    local_path = cache["source"].get("local_path") or ""
    pdf_filename = Path(local_path).name if local_path else ""
    cache_pdf_sha = cache["source"]["sha256"].removeprefix("sha256:")
    pdf_path = pdf_dir / pdf_filename if pdf_filename else None
    if pdf_path is None or not pdf_path.exists():
        pdf_sha = cache_pdf_sha
    else:
        pdf_sha = _compute_pdf_sha(pdf_path)

    sanity_vector_path = sanity_dir / f"{mpn_slug(args.mpn)}.json"
    sanity_field_count = len(json.loads(sanity_vector_path.read_text())["fields"])

    meta = _build_meta(
        mpn=args.mpn, cache=cache, pdf_filename=pdf_filename, pdf_sha=pdf_sha,
        cache_path=cache_path, sanity_vector_path=sanity_vector_path,
        sanity_pass=True, sanity_field_count=sanity_field_count,
        gate_run_id=None,
        gate_quality_score=cache["extraction"]["quality_score"],
        event="recurate_major_bump", prior_meta=prior_meta,
        from_schema_version=prior_meta["schema_version_at_curation"],
    )
    prior_meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True))
    print(f"[ok] re-curated to gold_v{new_base}.json "
          f"(archived gold_v{prior_base}.json.archived)")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote a gate-passed extraction to v1.4 gold.",
    )
    parser.add_argument("--mpn", required=True, help="MPN to promote (e.g. LM2596-ADJ)")
    parser.add_argument("--cache-dir", default=None,
                        help="Path to <kicad-happy>/datasheets/extracted/ "
                             "(default: $KICAD_HAPPY_DIR/datasheets/extracted/)")
    parser.add_argument("--pdf-dir", default=None,
                        help="Where PDFs live for SHA computation "
                             "(default: $KICAD_HAPPY_DIR/datasheets/pdfs/)")
    parser.add_argument("--yes", action="store_true",
                        help="Non-interactive; promote without prompt")
    parser.add_argument("--no-gate", action="store_true",
                        help="Skip A6 gate re-run (sanity-vector diff still runs)")
    parser.add_argument("--re-curate-from", default=None,
                        help="Re-curation sweep mode (Q4): previous schema base "
                             "version (e.g. '1.0' when promoting 2.0). Renames "
                             "existing gold in-place to .archived, runs A5 differ "
                             "against archived, prompts user, writes new gold.")
    args = parser.parse_args(argv)

    cache_dir = _resolve_cache_dir(args.cache_dir)
    cache_path = cache_dir / f"{args.mpn}.json"
    cache = _load_cache(cache_path)

    # ─── Re-curate-from mode (Q4 main-repo addition; spec §5.1.1)
    if args.re_curate_from:
        return _do_recurate_from(
            args=args, cache=cache, cache_path=cache_path,
        )

    # ─── Gate re-run (belt-and-suspenders; skipped with --no-gate)
    if not args.no_gate:
        gate_pass, gate_summary = _run_a6_gate(args.mpn, cache_dir)
        if not gate_pass:
            print("ERROR: A6 gate did not pass 4/4. Promotion blocked.",
                  file=sys.stderr)
            print(gate_summary, file=sys.stderr)
            return 2
        print("[ok] A6 gate: 4/4 PASS")

    # ─── Sanity-vector diff
    sanity_dir = _resolve_sanity_dir()
    sanity_pass, divergences = _run_sanity_diff(args.mpn, cache, sanity_dir)
    if not sanity_pass:
        print("ERROR: sanity-vector diff has divergences. Promotion blocked.",
              file=sys.stderr)
        for d in divergences:
            print(f"  - {d.get('path', '<no path>')}: {d['reason']}",
                  file=sys.stderr)
        return 2
    print("[ok] sanity-vector diff: all fields within tolerance")

    # ─── Cache schema validation
    kicad_happy_dir = _resolve_kicad_happy_dir()
    schema_ok, schema_summary = _validate_cache_schema(cache, kicad_happy_dir)
    if not schema_ok:
        print(f"ERROR: cache fails extraction.schema.json: {schema_summary}",
              file=sys.stderr)
        return 2
    print(f"[ok] cache schema validation: {schema_summary}")

    # ─── PDF SHA verification
    pdf_dir = _resolve_pdf_dir(args.pdf_dir)
    local_path = cache["source"].get("local_path") or ""
    pdf_filename = Path(local_path).name if local_path else ""
    cache_sha256_raw = cache["source"]["sha256"]  # "sha256:<hex64>"
    cache_pdf_sha = cache_sha256_raw.removeprefix("sha256:")
    pdf_path = pdf_dir / pdf_filename if pdf_filename else None
    if pdf_path is None or not pdf_path.exists():
        if pdf_path is not None:
            print(f"WARNING: PDF not found at {pdf_path}; using cache sha256")
        pdf_sha = cache_pdf_sha
    else:
        pdf_sha = _compute_pdf_sha(pdf_path)
        if pdf_sha != cache_pdf_sha:
            print(f"ERROR: PDF SHA mismatch — cache says "
                  f"{cache_pdf_sha}, "
                  f"PDF on disk has {pdf_sha}", file=sys.stderr)
            return 2

    # ─── Resolve gold dir + classify event
    gold_root = _resolve_gold_dir()
    slug_dir = gold_root / mpn_slug(args.mpn)
    base_version = cache["schema_version"]["base"]
    gold_path = slug_dir / f"gold_v{base_version}.json"

    sanity_vector_path = sanity_dir / f"{mpn_slug(args.mpn)}.json"
    sanity_field_count = len(json.loads(sanity_vector_path.read_text())["fields"])

    prior_meta = None
    event = "initial"
    if (slug_dir / "meta.json").exists():
        prior_meta = json.loads((slug_dir / "meta.json").read_text())
        if prior_meta["pdf_sha256"] != pdf_sha:
            event = "pdf_sha_change"
            _archive_existing(slug_dir, prior_meta["pdf_sha256"])
            prior_meta = None  # archived → next write starts fresh history
        else:
            event = "update"

    # ─── Confirmation prompt
    if not args.yes:
        print(f"\nReady to write {gold_path} (event: {event})")
        ans = input("Promote? [y/N]: ").strip().lower()
        if ans != "y":
            print("Aborted.")
            return 1

    # ─── Write gold + meta
    _write_gold(slug_dir, base_version, cache)
    meta = _build_meta(
        mpn=args.mpn, cache=cache, pdf_filename=pdf_filename, pdf_sha=pdf_sha,
        cache_path=cache_path, sanity_vector_path=sanity_vector_path,
        sanity_pass=True, sanity_field_count=sanity_field_count,
        gate_run_id=None,
        gate_quality_score=cache["extraction"]["quality_score"],
        event=event, prior_meta=prior_meta,
    )
    (slug_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True))
    print(f"[ok] wrote {gold_path}")
    print(f"[ok] wrote {slug_dir / 'meta.json'}")
    try:
        rel = slug_dir.relative_to(_HARNESS_ROOT)
    except ValueError:
        rel = slug_dir
    print(f"\nNext: git add {rel}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
