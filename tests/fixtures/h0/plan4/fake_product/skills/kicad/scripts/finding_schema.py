"""Synthetic finding factory + detector enum (mirrors product shapes)."""


class Det:
    SHORTED_TWO_PIN = 'detect_shorted_two_pin_components'
    LABEL_ALIASES = 'detect_label_aliases'


def make_finding(detector, rule_id, category, summary, description, **kw):
    f = {"detector": detector, "rule_id": rule_id, "category": category,
         "summary": summary, "description": description}
    f.update(kw)
    return f
