"""Top-level detector module: literal sites, a wrapper, an enum site, a loop site."""
from finding_schema import make_finding, Det

# EQ-901: ratio = r_bottom / (r_top + r_bottom)
# Source: Ohm's law
def divider_ratio(r_top, r_bottom):
    return r_bottom / (r_top + r_bottom)

PULLUP_MIN_OHMS = 1000
I2C_KEYWORDS = ("SDA", "SCL")


def _make_pu_001(ref):
    return make_finding(
        detector="validate_pullups", rule_id="PU-001", category="validation",
        summary=f"{ref} pull-up", description="x", schema_era="v1.4")


def validate_pullups(ctx):
    return [_make_pu_001("R1")]


def validate_led_resistors(ctx):
    return [make_finding(
        detector="validate_led_resistors", rule_id="LR-001", category="validation",
        summary="led", description="x", schema_era="v1.4")]


def detect_shorted(ctx):
    return [make_finding(
        detector=Det.SHORTED_TWO_PIN, rule_id="SP-001", category="signal",
        summary="short", description="x")]


_UC_SPECS = {"vbus_decoupling": ("UC-001", "no VBUS cap")}


def analyze_usb_compliance(ctx):
    out = []
    for _name, (_rid, _summary) in _UC_SPECS.items():
        out.append(make_finding(
            detector="analyze_usb_compliance", rule_id=_rid, category="usb",
            summary=_summary, description="x"))
    return out
