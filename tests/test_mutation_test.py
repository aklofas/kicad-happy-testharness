"""validate/mutation_test.py: mutation kills are credited only to assertions that hold on
the unmutated output."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_already_failing_assertions_do_not_count_as_kills():
    """code A4-F1: original_data was never evaluated, so an assertion failing on the unmutated
    output (aspirational / known-bug lock) caught every mutation."""
    from validate.mutation_test import run_mutation_test
    original = {"statistics": {"total_components": 10}}
    failing = {"id": "A", "check": {"path": "statistics.total_components", "op": "equals", "value": 99}}
    mutations = [({"statistics": {"total_components": 11}}, "count:+1")]
    assert run_mutation_test(original, [failing], mutations)["caught"] == 0
    holding = {"id": "B", "check": {"path": "statistics.total_components", "op": "equals", "value": 10}}
    assert run_mutation_test(original, [failing, holding], mutations)["caught"] == 1
