"""run_v14_gate.py is a flag-compatible wrapper over run_corpus_gate (H0 §6 rename)."""
TIER = "unit"

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regression import run_v14_gate as wrapper  # noqa: E402
from regression import run_corpus_gate as gate  # noqa: E402


def test_translate_old_flags():
    new = wrapper.translate_argv(["--symmetric", "--v131-dir", "/a", "--v14-dir", "/b",
                                  "--gate-dir", "results/x_gate", "--label", "x",
                                  "--cross-section", "smoke", "--jobs", "4", "--resume"])
    assert new == ["--baseline-dir", "/a", "--candidate-dir", "/b", "--gate-dir", "results/x_gate",
                   "--label", "x", "--cross-section", "smoke", "--jobs", "4", "--resume"]


def test_translate_defaults_and_timeout():
    new = wrapper.translate_argv(["--repo", "o/r", "--timeout", "600"])
    assert new[new.index("--baseline-dir") + 1] == "/tmp/kh-v131"
    assert new[new.index("--candidate-dir") + 1] == "/tmp/kh-v14"
    assert new[new.index("--gate-dir") + 1] == "results/v14_gate"
    assert new[new.index("--profile") + 1] == "long-tail"
    assert "--timeout" not in new


def test_small_timeout_dropped_with_note(capsys):
    new = wrapper.translate_argv(["--all", "--timeout", "120"])
    assert "--profile" not in new and "--timeout" not in new
    err = capsys.readouterr().err
    assert "--timeout" in err and "--symmetric" not in err


def test_symmetric_note_and_equals_forms(capsys):
    new = wrapper.translate_argv(["--symmetric", "--v131-dir=/a", "--v14-dir=/b", "--all"])
    assert new[new.index("--baseline-dir") + 1] == "/a"
    assert new[new.index("--candidate-dir") + 1] == "/b"
    assert "--symmetric" in capsys.readouterr().err


def test_wrapper_reexports_criteria_helpers():
    assert wrapper._compute_pass_criteria is gate._compute_pass_criteria
    assert wrapper._print_summary is gate._print_summary


def test_timeout_equals_form():
    new = wrapper.translate_argv(["--all", "--timeout=600"])
    assert new[new.index("--profile") + 1] == "long-tail" and "--timeout=600" not in new


def test_unknown_flag_passes_through():
    assert "--bogus" in wrapper.translate_argv(["--all", "--bogus"])


def test_missing_value_exits_2():
    import pytest
    for flag in ("--v14-dir", "--timeout", "--baseline-dir", "--gate-dir"):
        with pytest.raises(SystemExit) as e:
            wrapper.translate_argv(["--all", flag])
        assert e.value.code == 2
