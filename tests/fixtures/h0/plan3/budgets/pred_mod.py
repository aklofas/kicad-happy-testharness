"""Predicate module used by test_field_compare_budget."""


def nets_grew_by_one(delta, a_doc, b_doc):
    return isinstance(delta.before, int) and delta.after == delta.before + 1
