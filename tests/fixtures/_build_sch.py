"""KiCad 6+ schematic builder for synthetic test fixtures.

Generates valid .kicad_sch S-expression files from a fluent API.
The analyzer only needs netlist topology (symbols + wires + labels)
to detect circuits — footprints and graphical attributes are optional.

Pin positions for Device:R and Device:C are ±3.81mm from center (vertical).
Power symbols have their pin at (0,0) relative to placement.

Usage:
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 60))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 70))
        .wire((50, 46.19), (50, 40))     # R1 pin1 to +3V3
        .wire((50, 53.81), (50, 56.19))  # R1 pin2 to R2 pin1
        .wire((50, 63.81), (50, 70))     # R2 pin2 to GND
    )
    path = sch.write("/tmp/test.kicad_sch")
"""

from pathlib import Path

# Pin offset from component center for 2-pin passives (R, C, L)
_PIN_OFFSET = 3.81  # mm, from KiCad lib_symbols

_COUNTER = 0


def _uuid():
    """Generate a deterministic UUID-like string."""
    global _COUNTER
    _COUNTER += 1
    return f"00000000-0000-0000-0000-{_COUNTER:012d}"


def _reset_uuids():
    global _COUNTER
    _COUNTER = 0


def pin1(x, y, angle=0):
    """Compute pin 1 (top) absolute position for a 2-pin passive."""
    if angle == 0:    # vertical
        return (x, round(y - _PIN_OFFSET, 4))
    elif angle == 90:  # horizontal (rotated 90 CW)
        return (round(x - _PIN_OFFSET, 4), y)
    elif angle == 180:
        return (x, round(y + _PIN_OFFSET, 4))
    elif angle == 270:
        return (round(x + _PIN_OFFSET, 4), y)
    return (x, round(y - _PIN_OFFSET, 4))


def pin2(x, y, angle=0):
    """Compute pin 2 (bottom) absolute position for a 2-pin passive."""
    if angle == 0:
        return (x, round(y + _PIN_OFFSET, 4))
    elif angle == 90:
        return (round(x + _PIN_OFFSET, 4), y)
    elif angle == 180:
        return (x, round(y - _PIN_OFFSET, 4))
    elif angle == 270:
        return (round(x - _PIN_OFFSET, 4), y)
    return (x, round(y + _PIN_OFFSET, 4))


# --- Lib symbol templates ---

_LIB_DEVICE_R = '''    (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_keywords" "R res resistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_description" "Resistor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )'''

_LIB_DEVICE_C = '''    (symbol "Device:C" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0.635 2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "C" (at 0.635 -2.54 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "" (at 0.9652 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_keywords" "cap capacitor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_description" "Unpolarized capacitor" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1"
        (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
        (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))
      )
      (symbol "C_1_1"
        (pin passive line (at 0 3.81 270) (length 2.794) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 2.794) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )'''


def _lib_power(name):
    """Generate a power symbol lib definition."""
    safe = name.replace("+", "_").replace(".", "_")
    return f'''    (symbol "power:{name}" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#{name}" (at 0 1.016 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "{name}" (at 0 -1.016 0) (effects (font (size 0.762 0.762))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "{name}_0_1"
        (polyline (pts (xy 0 0) (xy 0 -1.27))
          (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "{name}_1_1"
        (pin power_in line (at 0 0 0) (length 0) (name "{name}" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
    )'''


class Schematic:
    """Fluent builder for KiCad 6+ schematic files."""

    def __init__(self, version=20231120):
        _reset_uuids()
        self._version = version
        self._symbols = []      # placed symbol instances
        self._wires = []        # wire segments
        self._labels = []       # net labels
        self._lib_ids = set()   # track which lib_symbols we need
        self._power_names = set()  # track power symbol names

    def resistor(self, ref, value, at=(50, 50), angle=0):
        self._lib_ids.add("Device:R")
        self._symbols.append({
            "lib_id": "Device:R", "ref": ref, "value": value,
            "x": at[0], "y": at[1], "angle": angle,
        })
        return self

    def capacitor(self, ref, value, at=(50, 50), angle=0):
        self._lib_ids.add("Device:C")
        self._symbols.append({
            "lib_id": "Device:C", "ref": ref, "value": value,
            "x": at[0], "y": at[1], "angle": angle,
        })
        return self

    def power(self, name, at=(50, 50)):
        self._power_names.add(name)
        ref = f"#{name}"
        self._symbols.append({
            "lib_id": f"power:{name}", "ref": ref, "value": name,
            "x": at[0], "y": at[1], "angle": 0, "is_power": True,
        })
        return self

    def wire(self, start, end):
        self._wires.append({"x1": start[0], "y1": start[1],
                            "x2": end[0], "y2": end[1]})
        return self

    def label(self, name, at=(50, 50), angle=0):
        self._labels.append({"name": name, "x": at[0], "y": at[1],
                             "angle": angle})
        return self

    def render(self):
        """Render the schematic as KiCad S-expression text."""
        lines = []
        lines.append(f'(kicad_sch (version {self._version}) (generator "test_fixture")')
        lines.append(f'  (uuid "{_uuid()}")')
        lines.append('  (paper "A4")')

        # lib_symbols
        lines.append('  (lib_symbols')
        if "Device:R" in self._lib_ids:
            lines.append(_LIB_DEVICE_R)
        if "Device:C" in self._lib_ids:
            lines.append(_LIB_DEVICE_C)
        for name in sorted(self._power_names):
            lines.append(_lib_power(name))
        lines.append('  )')

        # Wires
        for w in self._wires:
            lines.append(f'  (wire (pts (xy {w["x1"]} {w["y1"]}) (xy {w["x2"]} {w["y2"]}))')
            lines.append(f'    (stroke (width 0) (type default))')
            lines.append(f'    (uuid "{_uuid()}")')
            lines.append(f'  )')

        # Labels
        for lbl in self._labels:
            lines.append(f'  (label "{lbl["name"]}" (at {lbl["x"]} {lbl["y"]} {lbl["angle"]})')
            lines.append(f'    (effects (font (size 1.27 1.27)) (justify left bottom))')
            lines.append(f'    (uuid "{_uuid()}")')
            lines.append(f'  )')

        # Symbol instances
        for sym in self._symbols:
            lid = sym["lib_id"]
            lines.append(f'  (symbol (lib_id "{lid}") (at {sym["x"]} {sym["y"]} {sym["angle"]}) (unit 1)')
            lines.append(f'    (in_bom yes) (on_board yes)')
            lines.append(f'    (uuid "{_uuid()}")')
            lines.append(f'    (property "Reference" "{sym["ref"]}" (at {sym["x"]} {sym["y"]} 0))')
            lines.append(f'    (property "Value" "{sym["value"]}" (at {sym["x"]} {sym["y"]+2} 0))')
            lines.append(f'    (property "Footprint" "" (at {sym["x"]} {sym["y"]} 0)')
            lines.append(f'      (effects (font (size 1.27 1.27)) hide))')
            lines.append(f'    (property "Datasheet" "~" (at {sym["x"]} {sym["y"]} 0)')
            lines.append(f'      (effects (font (size 1.27 1.27)) hide))')
            lines.append(f'    (pin "1" (uuid "{_uuid()}"))')
            lines.append(f'    (pin "2" (uuid "{_uuid()}"))')
            lines.append(f'  )')

        lines.append(')')
        return '\n'.join(lines) + '\n'

    def write(self, path):
        """Write the schematic to a file. Returns the path."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.render(), encoding="utf-8")
        return str(p)
