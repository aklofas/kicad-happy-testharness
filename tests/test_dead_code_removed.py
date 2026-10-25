"""Dead code stays deleted: the utils re-export block, the unused timeouts and the
existence-resume plumbing behind the chained runners' --resume refusal (arch A1-F6)."""
import inspect
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "run"))
pytestmark = pytest.mark.unit


def test_utils_has_no_harnesslib_reexports_or_dead_timeouts():
    import utils
    for name in ("run_once", "build_env", "RunSpec", "NoSelection", "filter_units",
                 "GIT_TIMEOUT", "TEST_TIMEOUT", "INTEGRATION_TEST_TIMEOUT"):
        assert not hasattr(utils, name), name


def test_chained_workers_take_no_resume():
    import run_emc, run_thermal
    assert "resume" not in inspect.signature(run_emc._process_one_emc).parameters
    assert "resume" not in inspect.signature(run_thermal._process_one_thermal).parameters
