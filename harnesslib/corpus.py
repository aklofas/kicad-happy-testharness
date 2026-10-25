"""Corpus naming helpers: flat safe names, project keys, manifest filtering.

Pure functions; the repos root is always an explicit argument."""

import hashlib
import os
from pathlib import PurePosixPath

# Filesystem name-length safety (TH-013)
# 143 bytes is the eCryptfs-with-filename-encryption limit; covers plain
# ext4/xfs/btrfs/APFS (255) automatically. Any name longer than this gets
# deterministically truncated with a SHA1[:10] hash suffix.
NAME_MAX_BYTES = 143
_NAME_HASH_LEN = 10


def _truncate_with_hash(name: str, budget: int = NAME_MAX_BYTES) -> str:
    """Truncate a name to fit within `budget` bytes, appending a short stable hash.

    Uses byte-based truncation (not character-based) so that multi-byte UTF-8
    sequences never get cut mid-character. Deterministic — same input always
    produces the same output.
    """
    encoded = name.encode("utf-8")
    if len(encoded) <= budget:
        return name
    digest = hashlib.sha1(encoded).hexdigest()[:_NAME_HASH_LEN]
    # budget = truncated_prefix + "_" + digest
    truncate_to = budget - _NAME_HASH_LEN - 1
    truncated = encoded[:truncate_to].decode("utf-8", errors="ignore")
    return f"{truncated}_{digest}"


def project_key(pdir: str, stem: str) -> str:
    """Flatten a KiCad project's in-repo path + file stem into a safe directory name.

    Used by discover_projects() to build the `reference/{owner}/{repo}/{key}/`
    directory name for each project. Handles three concerns:

    1. **Separator normalization**: turns `/` and `\\` into `_`.
    2. **Stem deduplication**: when the last path component equals the stem
       (KiCad convention — `foo/foo.kicad_pro`), the stem is not re-appended.
       Saves 30-50% on affected names at zero information cost.
    3. **Length cap**: final name is guaranteed to fit within NAME_MAX_BYTES
       via `_truncate_with_hash()`.
    """
    pdir = (pdir or "").replace("\\", "/").strip("/")
    if not pdir or pdir == ".":
        flat = stem
    elif PurePosixPath(pdir).name == stem:
        # Dedupe — directory basename already equals stem
        flat = pdir.replace("/", "_")
    else:
        flat = pdir.replace("/", "_") + "_" + stem
    return _truncate_with_hash(flat)


def project_prefix(project_path: str) -> str:
    """Convert a project path to a filename prefix (e.g., 'sub/dir' → 'sub_dir_').

    Applies the TH-013 length cap to the flattened prefix. The trailing
    underscore is preserved so callers that do `prefix + filename` still work,
    but note: for very long paths the prefix itself may be hash-suffixed, and
    the caller should verify the FINAL concatenated name fits in NAME_MAX_BYTES
    (use `_truncate_with_hash` on the final string if unsure).
    """
    if project_path and project_path != ".":
        flat = project_path.replace("/", "_").replace("\\", "_")
        return _truncate_with_hash(flat, budget=NAME_MAX_BYTES - 1) + "_"
    return ""


def _path_relative_to_repos(path, repos_dir):
    """Get path relative to the repos/ directory.

    Handles both absolute paths under REPOS_DIR and paths containing 'repos/'.
    Returns the relative path string (e.g., 'OpenMower/Hardware/board.kicad_sch').
    """
    path = str(path)
    repos_str = str(repos_dir)
    if path.startswith(repos_str):
        return path[len(repos_str):].lstrip(os.sep)
    idx = path.find("repos" + os.sep)
    if idx >= 0:
        return path[idx + len("repos") + 1:]
    return path


def repo_name_from_path(path, repos_dir):
    """Extract repo name (owner/repo under repos/).

    Given an absolute or relative path like repos/owner/OpenMower/Hardware/...,
    returns 'owner/OpenMower'.
    """
    rel = _path_relative_to_repos(path, repos_dir)
    parts = rel.replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] and parts[1]:
        return f"{parts[0]}/{parts[1]}"
    return parts[0] if parts and parts[0] else None


def within_repo_path(path, repos_dir):
    """Get the path within a repo (everything after the owner/repo).

    Given repos/owner/OpenMower/Hardware/board.kicad_sch,
    returns 'Hardware/board.kicad_sch'.
    """
    rel = _path_relative_to_repos(path, repos_dir)
    parts = rel.replace("\\", "/").split("/", 2)
    return parts[2] if len(parts) > 2 else ""


def safe_name(path, repos_dir):
    """Create a flat safe filename from a within-repo path.

    Replaces path separators with underscores and applies the TH-013 length
    cap. Returned name is guaranteed ≤ NAME_MAX_BYTES.
    """
    flat = within_repo_path(path, repos_dir).replace(os.sep, "_").replace("/", "_")
    return _truncate_with_hash(flat)


def filter_manifest_by_repo(lines, repo_name):
    """Filter manifest lines to only those belonging to a given repo.

    repo_name is 'owner/repo' format. Matches against the repos/ directory path.
    """
    marker = f"repos/{repo_name}/"
    marker_os = f"repos{os.sep}{repo_name.replace('/', os.sep)}{os.sep}"
    # TH-046: a line may be exactly the repo directory with nothing after it
    # (root-level gerber sets) — match it too, on a path-component boundary.
    root = f"/{marker[:-1]}"
    root_os = f"{os.sep}repos{os.sep}{repo_name.replace('/', os.sep)}"
    return [l for l in lines
            if marker in l or marker_os in l
            or l.endswith(root) or l.endswith(root_os)]
