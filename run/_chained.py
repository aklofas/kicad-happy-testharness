"""Helpers shared by the runners that chain off other analyzers' outputs."""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import utils
from harnesslib.batch import start_run
from harnesslib.execution import recorded_env
from harnesslib.identity import (RunSpec, finish_manifest, git_worktree_ref, input_digest,
                                 sha256_file, unit_is_current)
from utils import resolve_repos_with_source


def expand_selection(args, finder):
    """Resolve the repo selection; return (repo_list, units, selection_source) where units
    gathers finder(repo) results in order, or finder(None) when the selection is every
    repo (repo_list is then None)."""
    repo_list, selection_source = resolve_repos_with_source(
        args, require_explicit_all=True)
    if repo_list is not None:
        inputs = []
        for rn in repo_list:
            inputs.extend(finder(rn))
        return repo_list, inputs, selection_source
    return None, finder(None), selection_source


def err_first_line(err_file):
    """First line of the .err file: the 'status: detail' summary."""
    try:
        lines = err_file.read_text(encoding="utf-8").strip().splitlines()
        return lines[0] if lines else "unknown error"
    except OSError:
        return "unknown error"


def upstream_sha(**paths):
    """Input identity of a chained unit: the upstream outputs it reads, by role
    (None = no output paired for that role)."""
    return input_digest((role, sha256_file(p) if p else "-") for role, p in paths.items())


class ChainedRun:
    """Run manifest + units.jsonl in a chained runner's output root, resumed by identity the
    way run_batch is: a unit is reused only under the matched run, with its upstream outputs
    and its own output unchanged since its ok record. Units are keyed by output path."""

    def __init__(self, out_root, unit_inputs, *, argv, selection_source, product_root, env,
                 resume):
        self.out_root = Path(out_root)
        self.analyzer = self.out_root.name
        self.inputs = {self.unit_id(o): sha for o, sha in unit_inputs.items()}
        spec = RunSpec(kind="batch", profile="standard",
                       harness=git_worktree_ref(utils.HARNESS_DIR), baseline=None,
                       candidate=git_worktree_ref(product_root),
                       argv=tuple(a for a in argv if a != "--resume"),
                       selection_source=selection_source, unit_ids=tuple(sorted(self.inputs)),
                       normalization_policy="volatile-leaves-v1", env=recorded_env(env))
        self.run_id, self.log, self.resume = start_run(
            self.out_root, spec, self.inputs,
            expected_census={self.analyzer: len(self.inputs)}, resume=resume)
        self.totals = Counter()
        self.skipped = 0

    @staticmethod
    def unit_id(output):
        output = Path(output)
        return f"{output.parent.parent.name}/{output.parent.name}/{output.name}"

    def is_current(self, output):
        uid = self.unit_id(output)
        current = self.resume and unit_is_current(self.log, self.analyzer, uid, self.inputs[uid],
                                                  output, run_id=self.run_id)
        self.skipped += bool(current)
        return current

    def record(self, output, exit_code, ok, elapsed):
        output = Path(output)
        status = "ok" if ok else err_first_line(output.with_suffix(".err")).split(":", 1)[0]
        uid = self.unit_id(output)
        self.log.append({"analyzer": self.analyzer, "unit_id": uid, "run_id": self.run_id,
                         "input_sha256": self.inputs[uid], "status": status,
                         "exit_code": exit_code,
                         "output_sha256": sha256_file(output) if ok else None,
                         "elapsed_s": round(elapsed, 3)})
        self.totals[status] += 1

    def finish(self):
        finish_manifest(self.out_root, {**dict(self.totals), "skipped": self.skipped})
