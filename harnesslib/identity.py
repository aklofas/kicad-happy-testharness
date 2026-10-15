"""Run identity: worktree refs, digests, RunSpec, run manifest (v1), unit log.

Report A3/A6/TH-049: every run is bound to product+harness SHAs, effective
args, env, selection and input digests; resume is by identity, never by path.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

MANIFEST_VERSION = 1
MANIFEST_NAME = "manifest.json"
UNITS_NAME = "units.jsonl"
OK_STATUSES = ("ok", "ok_findings_exit")


@dataclass(frozen=True)
class WorktreeRef:
    sha: str
    path: str
    dirty: bool


def _git(path: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def git_worktree_ref(path: Path) -> WorktreeRef:
    p = Path(path).resolve()
    sha = _git(p, "rev-parse", "HEAD")
    dirty = bool(_git(p, "status", "--porcelain"))
    return WorktreeRef(sha=sha, path=str(p), dirty=dirty)


@dataclass(frozen=True)
class RunSpec:
    kind: str
    profile: str
    harness: WorktreeRef
    baseline: WorktreeRef | None
    candidate: WorktreeRef | None
    argv: tuple[str, ...]
    selection_source: str
    unit_ids: tuple[str, ...]
    normalization_policy: str
    env: tuple[tuple[str, str], ...]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    """Digest of a unit input: a file's bytes, or a directory's content tree.

    Gerber units are directories. The directory digest covers every regular
    file beneath it (symlinks skipped) as sorted "<posix relpath>\t<sha256>"
    lines, so renames and content edits both change it."""
    p = Path(path)
    if not p.is_dir():
        return sha256_file(p)
    lines = []
    for f in p.rglob("*"):
        if f.is_symlink() or not f.is_file():
            continue
        lines.append(f"{f.relative_to(p).as_posix()}\t{sha256_file(f)}")
    return hashlib.sha256("\n".join(sorted(lines)).encode("utf-8")).hexdigest()


def selection_digest(unit_ids: Iterable[str]) -> str:
    return hashlib.sha256("\n".join(sorted(unit_ids)).encode("utf-8")).hexdigest()


def input_digest(pairs: Iterable[tuple[str, str]]) -> str:
    lines = sorted(f"{u}\t{d}" for u, d in pairs)
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def identity_key(spec: RunSpec) -> dict:
    argv = tuple(a for a in spec.argv if a != "--resume")
    return {
        "kind": spec.kind,
        "profile": spec.profile,
        "harness_sha": spec.harness.sha,
        "baseline_sha": spec.baseline.sha if spec.baseline else None,
        "candidate_sha": spec.candidate.sha if spec.candidate else None,
        "argv": list(argv),
        "selection_source": spec.selection_source,
        "selection_digest": selection_digest(spec.unit_ids),
        "normalization_policy": spec.normalization_policy,
        "env": [list(kv) for kv in spec.env],
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_manifest(root: Path, spec: RunSpec, *, run_id: str,
                   expected_census: dict[str, int], input_digest: str,
                   runtime: dict[str, str]) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    doc = {
        "manifest_version": MANIFEST_VERSION,
        "run_id": run_id,
        "kind": spec.kind,
        "profile": spec.profile,
        "harness": asdict(spec.harness),
        "product": {
            "baseline": asdict(spec.baseline) if spec.baseline else None,
            "candidate": asdict(spec.candidate) if spec.candidate else None,
        },
        "runtime": dict(runtime),
        "env": dict(spec.env),
        "argv": list(spec.argv),
        "selection": {"source": spec.selection_source,
                      "unit_count": len(spec.unit_ids),
                      "digest": selection_digest(spec.unit_ids)},
        "input_digest": input_digest,
        "expected_census": dict(expected_census),
        "normalization_policy": spec.normalization_policy,
        "identity": identity_key(spec),
        "started_at": _now(),
        "finished_at": None,
        "totals": None,
    }
    path = root / MANIFEST_NAME
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def read_manifest(root: Path) -> dict:
    return json.loads((Path(root) / MANIFEST_NAME).read_text(encoding="utf-8"))


def finish_manifest(root: Path, totals: dict) -> None:
    path = Path(root) / MANIFEST_NAME
    doc = read_manifest(root)
    doc["finished_at"] = _now()
    doc["totals"] = totals
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def manifests_match(a: dict, b: dict) -> tuple[bool, list[str]]:
    """Identity comparison for resume/gate reuse.

    input_digest is deliberately NOT part of identity: the per-unit
    input_sha256 check in unit_is_current covers input changes and allows
    partial reuse. Dirty worktrees never match (resume would mix code states).
    """
    for m in (a, b):
        if m.get("manifest_version") != MANIFEST_VERSION:
            return False, ["manifest_version mismatch"]
    if not a.get("identity") or not b.get("identity"):
        return False, ["missing identity block"]
    dirty = []
    for m in (a, b):
        for which, ref in (("harness", m.get("harness")),
                           ("baseline", (m.get("product") or {}).get("baseline")),
                           ("candidate", (m.get("product") or {}).get("candidate"))):
            if ref and ref.get("dirty") and which not in dirty:
                dirty.append(which)
    if dirty:
        return False, [f"dirty worktree: {w}" for w in dirty]
    ka, kb = a["identity"], b["identity"]
    reasons = []
    for field in sorted(set(ka) | set(kb)):
        if ka.get(field) != kb.get(field):
            reasons.append(f"{field}: {ka.get(field)} != {kb.get(field)}")
    return (not reasons), reasons


class UnitLog:
    """Append-only JSONL of per-unit records at root/units.jsonl.

    Only the orchestrating process appends (workers return records). The
    latest-per-unit map is cached for the lifetime of the object."""

    def __init__(self, root: Path):
        self.path = Path(root) / UNITS_NAME
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._latest: dict[str, dict] | None = None

    def _truncate_torn_tail(self) -> None:
        """Drop a final segment lacking a trailing newline (tail-only read)."""
        if not self.path.exists():
            return
        with open(self.path, "rb+") as fh:
            size = fh.seek(0, 2)
            if size == 0:
                return
            fh.seek(size - 1)
            if fh.read(1) == b"\n":
                return
            end = size
            cut = 0
            while end > 0:
                start = max(0, end - 4096)
                fh.seek(start)
                idx = fh.read(end - start).rfind(b"\n")
                if idx != -1:
                    cut = start + idx + 1
                    break
                end = start
            fh.truncate(cut)
        print("units.jsonl: ignoring torn trailing line", file=sys.stderr)

    def append(self, record: dict) -> None:
        key = f"{record['analyzer']}/{record['unit_id']}"
        self._truncate_torn_tail()
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        if self._latest is not None:
            self._latest[key] = record

    def __iter__(self) -> Iterator[dict]:
        if not self.path.exists():
            return iter(())
        text = self.path.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):
            text = text[:text.rfind("\n") + 1]
            print("units.jsonl: ignoring torn trailing line", file=sys.stderr)
        return iter([json.loads(ln) for ln in text.split("\n") if ln.strip()])

    def by_unit(self) -> dict[str, dict]:
        if self._latest is None:
            latest: dict[str, dict] = {}
            for rec in self:
                latest[f"{rec['analyzer']}/{rec['unit_id']}"] = rec
            self._latest = latest
        return self._latest


def unit_is_current(log: UnitLog, analyzer: str, unit_id: str,
                    input_sha256: str, output_path: Path,
                    run_id: str | None = None) -> bool:
    """True if the logged record still describes a valid output.

    When run_id is given the record must carry it, so records left by a
    different (e.g. crashed-over) run are never reused."""
    rec = log.by_unit().get(f"{analyzer}/{unit_id}")
    if rec is None or rec.get("status") not in OK_STATUSES:
        return False
    if run_id is not None and rec.get("run_id") != run_id:
        return False
    if rec.get("input_sha256") != input_sha256:
        return False
    out = Path(output_path)
    if not out.exists():
        return False
    return sha256_file(out) == rec.get("output_sha256")
