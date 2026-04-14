"""Extract KiCad component references from finding description strings.

Provides extract_refs() for pulling component designators (R1, C23, U4, etc.)
from free-text descriptions, and REF_FIELD_MAP for mapping detector names
(as they appear in findings[].detector) to the field containing component refs.
"""

import re

# Valid KiCad reference prefixes (sorted longest-first for matching priority)
VALID_PREFIXES = sorted([
    "R", "C", "L", "U", "Q", "D", "J", "P", "K", "F", "Y",
    "TP", "SW", "RV", "VR", "RN", "FB", "FL", "DS", "BT", "LS",
    "M", "T", "A", "X", "H", "CR", "RE",
], key=len, reverse=True)

_PREFIX_SET = set(VALID_PREFIXES)

# False positives — protocol/standard names that look like refs
_FALSE_POSITIVES = {
    "I2C", "I2S", "SPI", "USB", "RS485", "RS232", "RS422",
    "DB9", "DB15", "DB25", "DB37",
    "RP2040", "RP2350",
    "S1", "S2", "S3",  # sheet references, not components
    "V1", "V2", "V3",  # voltage labels
    "N1", "N2", "N3",  # net labels
}

# Regex for a single KiCad reference: 1-3 uppercase letters + digits + optional unit suffix
_REF_PATTERN = re.compile(r'\b([A-Z]{1,3}\d+[a-z]?\d?)\b')

# Slash-separated refs: "R135/R134"
_SLASH_PATTERN = re.compile(r'\b([A-Z]{1,3}\d+(?:/[A-Z]{1,3}\d+)+)\b')

# Range refs: "Q13-Q16" (same prefix)
_RANGE_PATTERN = re.compile(r'\b([A-Z]{1,3})(\d+)\s*[-–]\s*\1(\d+)\b')


def _ref_prefix(ref):
    """Extract the letter prefix from a reference designator."""
    i = 0
    while i < len(ref) and ref[i].isalpha():
        i += 1
    return ref[:i]


def _is_valid_ref(ref):
    """Check if a string is a valid KiCad component reference."""
    if ref in _FALSE_POSITIVES:
        return False
    prefix = _ref_prefix(ref)
    return prefix in _PREFIX_SET


def _extract_refs_set(description):
    """Extract refs as a set (internal helper)."""
    refs = set()
    if not description:
        return refs

    for m in _RANGE_PATTERN.finditer(description):
        prefix = m.group(1)
        start = int(m.group(2))
        end = int(m.group(3))
        if end - start <= 20:
            for n in range(start, end + 1):
                ref = f"{prefix}{n}"
                if _is_valid_ref(ref):
                    refs.add(ref)

    for m in _SLASH_PATTERN.finditer(description):
        parts = m.group(0).split("/")
        for part in parts:
            if _is_valid_ref(part):
                refs.add(part)

    for m in _REF_PATTERN.finditer(description):
        ref = m.group(1)
        if _is_valid_ref(ref):
            refs.add(ref)

    return refs


def extract_refs(description):
    """Extract KiCad component references from a description string.

    Handles:
    - Simple refs: R1, C23, U4
    - Slash-separated: R135/R134
    - Ranges: Q13-Q16
    - Composite values: "R163 442k" (extracts R163)

    Returns sorted list of unique valid refs.
    """
    return sorted(_extract_refs_set(description))


def extract_refs_ordered(description):
    """Extract refs preserving order of first appearance in description.

    Same extraction logic as extract_refs but returns refs in the order
    they first appear in the text, not alphabetically sorted.
    """
    if not description:
        return []

    valid_refs = _extract_refs_set(description)
    if not valid_refs:
        return []

    # Find position of first occurrence of each ref in the description
    ordered = []
    seen = set()
    for m in _REF_PATTERN.finditer(description):
        ref = m.group(1)
        if ref in valid_refs and ref not in seen:
            ordered.append(ref)
            seen.add(ref)

    # Add any refs from ranges/slashes not found by simple pattern
    for ref in sorted(valid_refs - seen):
        ordered.append(ref)

    return ordered


# Maps detector names (as they appear in findings[].detector) to the field(s) containing component refs.
# For composite fields like "R163 442k", the ref is the first token.
REF_FIELD_MAP = {
    "detect_opamp_circuits": "reference",
    "detect_voltage_dividers": "r_top.ref",     # nested dict with ref key
    "detect_protection_devices": "ref",
    "detect_transistor_circuits": "reference",
    "detect_power_regulators": "ref",
    "detect_crystal_circuits": "reference",
    "detect_rc_filters": "resistor.ref",        # nested dict with ref key
    "detect_lc_filters": "inductor.ref",        # nested dict with ref key
    "detect_led_drivers": "ref",
    "detect_current_sense": "shunt.ref",         # nested dict with ref key
    "detect_rf_matching": None,                 # no single ref field — "antenna" is value not ref
    "detect_design_observations": None,          # various categories, no single ref field
    "detect_key_matrices": None,                # no ref field — count-only
    "validate_feedback_stability": "r_top.ref",  # same divider structure as voltage_dividers
    "detect_decoupling": None,                  # rail is a net name, not a ref
    "detect_buzzer_speakers": "reference",
    "detect_bridge_circuits": None,             # topology-based, no single ref
    "detect_isolation_barriers": "ref",
    "detect_ethernet_interfaces": "phy_reference",
    "detect_hdmi_dvi_interfaces": "connector",
    "detect_memory_interfaces": "memory_reference",
    "detect_rf_chains": None,                   # complex structure — count-only
    "detect_bms_systems": "bms_reference",
    "detect_addressable_leds": None,            # first_led is the lead, not a simple ref field
}

# Maps PCB detector/section names to the field containing component refs.
PCB_REF_FIELD_MAP = {
    "decoupling_placement": "ic",
    "analyze_thermal_pad_vias": "component",
    "analyze_tombstoning_risk": "component",
}


def get_ref_from_item(detector_name, item):
    """Extract the component ref from a signal analysis item.

    Uses REF_FIELD_MAP to find the right field. Returns None if
    the detector has no ref field or the item lacks the expected field.
    """
    field_path = REF_FIELD_MAP.get(detector_name)
    if not field_path:
        return None

    # Navigate dotted path (e.g., "r_top.ref")
    val = item
    for part in field_path.split("."):
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None

    if val is None:
        return None

    # Some fields are composite like "R163 442k" — extract first token
    val_str = str(val).strip()
    if " " in val_str:
        val_str = val_str.split()[0]

    if not val_str or "?" in val_str:
        return None
    return val_str if _is_valid_ref(val_str) else None
