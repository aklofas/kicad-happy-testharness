# Findings: IhsanSA/Line-Follower-Analog-Kicad-Design / Line Follower No contoller

## FND-00000861: LM358 comparator configuration and motor-driving NPN transistors correctly detected; Decoupling analysis empty despite C1/C2 (10uF) capacitors present on supply rails; AMS1117-5.0 LDO detected with...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Line Follower No contoller_Line Follower No contoller.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Both LM358 units identified as comparator_or_open_loop with named nets Signal_L/Signal_R and Driver_L/Driver_R. Q1 and Q2 NPN transistors correctly flagged as motor-driving with base pulldowns R3/R11.
- Power regulator detection correctly identifies U2 as AMS1117-5.0, topology=LDO, vout=5.0V via fixed suffix parsing.

### Incorrect
- decoupling_analysis is [] even though C1 and C2 (both 10uF) are present. They connect via unnamed nets to AMS1117 output and +7.5V input rather than directly to a named power rail, so they are invisible to the decoupling detector. The regulator_caps observation also flags missing caps, creating a contradictory picture.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
