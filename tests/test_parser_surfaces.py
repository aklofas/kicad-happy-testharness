"""Pin every runner parser's option surface so shared declarations cannot drift it."""
TIER = "unit"

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "run"))

import utils  # noqa: E402
import run_emc  # noqa: E402
import run_spice  # noqa: E402
import run_thermal  # noqa: E402

GOLDEN = ROOT / "tests" / "fixtures" / "wave10" / "parser_surfaces.json"

BUILDERS = {
    "batch_schematic": lambda: utils.build_batch_parser("schematic"),
    "emc": run_emc.build_parser,
    "thermal": run_thermal.build_parser,
    "spice": run_spice.build_parser,
}


def surface(parser):
    # The parallel-jobs default is the host CPU count; keep the golden machine-independent.
    jobs = str(utils.DEFAULT_JOBS)

    def norm(v):
        return v.replace(jobs, "<DEFAULT_JOBS>") if isinstance(v, str) else v

    actions = [[a.option_strings, a.dest, norm(repr(a.default)), norm(a.help),
                getattr(a.type, "__name__", repr(a.type)),
                list(a.choices) if a.choices is not None else None,
                a.required, type(a).__name__] for a in parser._actions]
    return {"description": parser.description, "actions": actions}


def test_parser_surfaces_match_golden():
    golden = json.loads(GOLDEN.read_text())
    current = {name: surface(build()) for name, build in BUILDERS.items()}
    assert current == golden
