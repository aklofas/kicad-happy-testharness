"""Unit tests for filesystem-safe name helpers in utils.py."""

TIER = "unit"

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import _truncate_with_hash, NAME_MAX_BYTES


def test_short_passthrough():
    assert _truncate_with_hash("foo") == "foo"


def test_exactly_at_budget_passthrough():
    name = "a" * NAME_MAX_BYTES
    assert _truncate_with_hash(name) == name
    assert len(_truncate_with_hash(name).encode("utf-8")) == NAME_MAX_BYTES


def test_one_over_budget_truncated_and_hashed():
    name = "a" * (NAME_MAX_BYTES + 1)
    result = _truncate_with_hash(name)
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES
    assert result != name
    # Hash suffix present: last 10 chars are hex, preceded by underscore
    assert result[-11] == "_"
    assert all(c in "0123456789abcdef" for c in result[-10:])


def test_well_over_budget():
    name = "x" * 500
    result = _truncate_with_hash(name)
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES


def test_cyrillic_truncation_stays_valid_utf8():
    # Ukrainian "Системи автоматизованого проектування" repeated to ~600 bytes
    name = "Системи автоматизованого проектування " * 10
    assert len(name.encode("utf-8")) > NAME_MAX_BYTES
    result = _truncate_with_hash(name)
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES
    # Must still be valid UTF-8 (no half-character at truncation boundary)
    result.encode("utf-8").decode("utf-8")


def test_deterministic():
    name = "b" * 500
    assert _truncate_with_hash(name) == _truncate_with_hash(name)


def test_different_inputs_different_hashes():
    a = _truncate_with_hash("a" * 500)
    b = _truncate_with_hash("b" * 500)
    assert a != b


from utils import project_key


def test_project_key_short_subdir():
    assert project_key("Hardware", "board") == "Hardware_board"


def test_project_key_root_project():
    assert project_key(".", "board") == "board"


def test_project_key_empty_pdir():
    assert project_key("", "board") == "board"


def test_project_key_deep_nested():
    assert project_key("a/b/c", "board") == "a_b_c_board"


def test_project_key_windows_backslash():
    assert project_key("a\\b", "board") == "a_b_board"


def test_project_key_dedupes_trailing_stem():
    # KiCad convention: project dir basename equals .kicad_pro stem
    # Before TH-013: "foo_rev.A01_foo_rev.A01"
    # After TH-013: "foo_rev.A01"
    assert project_key("foo_rev.A01", "foo_rev.A01") == "foo_rev.A01"


def test_project_key_dedupes_nested_trailing_stem():
    # Before: "parent_sub_board_board"  After: "parent_sub_board"
    assert project_key("parent/sub/board", "board") == "parent_sub_board"


def test_project_key_does_not_dedupe_when_different():
    assert project_key("parent/sub", "other") == "parent_sub_other"


def test_project_key_length_cap():
    pdir = "a" * 200
    result = project_key(pdir, "stem")
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES


def test_project_key_cyrillic_length_cap():
    # Cyrillic project directory ~600 bytes
    pdir = "Системи автоматизованого проектування електронних пристроїв " * 10
    result = project_key(pdir, "board")
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES
    result.encode("utf-8").decode("utf-8")  # still valid UTF-8


def test_project_key_deterministic():
    assert project_key("a/b/c", "x") == project_key("a/b/c", "x")


from utils import project_prefix, safe_name


def test_project_prefix_short_unchanged():
    # Existing behavior preserved for short inputs
    assert project_prefix("sub/dir") == "sub_dir_"
    assert project_prefix(".") == ""
    assert project_prefix("") == ""


def test_project_prefix_long_capped():
    pdir = "a" * 200
    result = project_prefix(pdir)
    # Prefix has trailing underscore; capped form should still end with `_`
    assert result.endswith("_")
    # Total length (including trailing underscore) ≤ budget
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES


def test_safe_name_short_unchanged():
    # Existing behavior for a short path: within_repo_path strips owner/repo,
    # then "/" becomes "_"
    result = safe_name("repos/owner/repo/Hardware/board.kicad_sch")
    assert result == "Hardware_board.kicad_sch"


def test_safe_name_long_capped():
    # Construct a path with deep directories → long flat name after flattening
    deep = "repos/owner/repo/" + "/".join(["seg"] * 50) + "/board.kicad_sch"
    result = safe_name(deep)
    assert len(result.encode("utf-8")) <= NAME_MAX_BYTES


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
