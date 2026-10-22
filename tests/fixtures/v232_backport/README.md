# Real snap pairs for the v2.3.2 backport budget (product 6a91aaa → 4701c26)

Copied 2026-10-22 from the prototype gate trees that preceded the full gate
(`results/v232_backport_gate_proto{,2}`, harness `c1d2d57947e`, standard profile,
`PYTHONHASHSEED=0`). One pair per budget class, used by
`tests/test_budget_v232_backport.py` as the comparator's real-shape check of
`regression/budgets/v232-backport.json` and its predicate module
`regression/budgets/v232_backport.py`:

- `a_rs001/` — `bluepylons/A-Thinkpad-USB-keyboard` `PCB_BSS138-level-shifter.kicad_sch`:
  one RS-001 on a name-only rail (`pins == []`) flips deterministic → heuristic (PR #58);
  8 strict deltas, no cascade.
- `b_pu001/` — `Jeija/esp8266-smartwatch` `board_v1_rv3029c2.sch`: one PU-001 on a
  single-pin `no_connect` net disappears (PR #57); the index-aligned cascade yields 72 deltas.
- `b_pu001_renumbered/` — `bluerobotics/ping-dev-kit` `48v_boost.kicad_sch`: one PU-001
  disappears (PR #57) and the surviving PU-001 that shared its detection hash is renumbered
  from `…#1` to the bare id, so pairing on the finding_id base + content is required;
  190 deltas including `audience_summary` row shifts.
- `c_pp001/` — `Autonomous-OpenHD-OpenCV-RC-plane/Pi-Flight-Sensor-hat`
  `KICAD PCB_5V_BUCK.kicad_sch`: one PP-001 on a `BST` pin disappears (PR #59); 284 deltas.

Do not edit the `snap.json` files. If they ever need refreshing, copy from a fresh gate
tree and update this README.
