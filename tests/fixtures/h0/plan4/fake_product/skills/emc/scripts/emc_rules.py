"""EMC-style positional factory (legacy exception shape)."""


def _make_finding(category, severity, rule_id, title, description, **extra):
    return {"category": category, "severity": severity, "rule_id": rule_id,
            "detector": f"emc_{category}", "title": title, "description": description}


def check_ground_plane(pcb):
    out = []
    out.append(_make_finding('ground_plane', 'INFO', 'GP-001',
                             title='t', description='d'))
    out.append(_make_finding('decoupling', 'HIGH', 'DC-001',
                             title='t', description='d'))
    # mixed shape: positional category but keyword rule_id — NOT the grandfathered shape
    out.append(_make_finding('shielding', 'LOW', rule_id='SH-009',
                             title='t', description='d'))
    return out
