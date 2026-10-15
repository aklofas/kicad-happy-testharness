"""run_tests.py must fail closed: no phantom passes, no silent timeouts."""
import sys
import textwrap
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import run_tests  # noqa: E402


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def test_has_main_block_detects_runner(tmp_path):
    with_main = _write(tmp_path, "test_a.py", '''
        def test_x():
            assert True
        if __name__ == "__main__":
            print("1 passed, 0 failed (1 total)")
    ''')
    without = _write(tmp_path, "test_b.py", '''
        def test_x():
            assert True
    ''')
    assert run_tests.has_main_block(with_main) is True
    assert run_tests.has_main_block(without) is False


def test_missing_runner_is_no_runner_status(tmp_path):
    f = _write(tmp_path, "test_phantom.py", '''
        def test_x():
            assert True
    ''')
    r = run_tests.run_test_file(f, timeout=30)
    assert r["status"] == "no_runner"
    assert r["passed"] == 0


def test_unparsed_summary_is_failure(tmp_path):
    f = _write(tmp_path, "test_odd.py", '''
        if __name__ == "__main__":
            print("All tests passed!")
    ''')
    r = run_tests.run_test_file(f, timeout=30)
    assert r["status"] == "unparsed"
    assert r["passed"] == 0


def test_parsed_summary_counts(tmp_path):
    f = _write(tmp_path, "test_ok.py", '''
        if __name__ == "__main__":
            print("3 passed, 0 failed, 1 skipped (4 total)")
    ''')
    r = run_tests.run_test_file(f, timeout=30)
    assert (r["status"], r["passed"], r["failed"], r["skipped"]) == ("pass", 3, 0, 1)


def test_nonzero_exit_is_failure_even_with_parsed_summary(tmp_path):
    f = _write(tmp_path, "test_red.py", '''
        import sys
        if __name__ == "__main__":
            print("2 passed, 1 failed (3 total)")
            sys.exit(1)
    ''')
    r = run_tests.run_test_file(f, timeout=30)
    assert r["status"] == "fail"
    assert r["failed"] == 1


def test_timeout_is_failure(tmp_path):
    f = _write(tmp_path, "test_slow.py", '''
        import time
        if __name__ == "__main__":
            time.sleep(5)
            print("1 passed, 0 failed (1 total)")
    ''')
    r = run_tests.run_test_file(f, timeout=1)
    assert r["status"] == "timeout"


def test_exit_code_rules():
    ok = {"status": "pass", "passed": 1, "failed": 0, "skipped": 0}
    assert run_tests.exit_code([ok]) == 0
    assert run_tests.exit_code([ok, {**ok, "status": "no_runner"}]) == 1
    assert run_tests.exit_code([ok, {**ok, "status": "unparsed"}]) == 1
    assert run_tests.exit_code([ok, {**ok, "status": "timeout"}]) == 1
    assert run_tests.exit_code([{**ok, "failed": 2}]) == 1
    assert run_tests.exit_code([]) == 2


def test_has_main_block_ignores_marker_text_in_strings(tmp_path):
    f = _write(tmp_path, "test_meta.py", '''
        SAMPLE = 'if __name__ == "__main__":'
        def test_x():
            assert True
    ''')
    assert run_tests.has_main_block(f) is False
