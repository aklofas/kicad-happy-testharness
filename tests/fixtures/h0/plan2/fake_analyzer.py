"""Fake analyzer for execution tests.

Usage: fake_analyzer.py <mode> -o <out>   (mode is the first positional)
Modes: ok | ok_exit1 | exit2 | nothing | garbage | sleep | ok_wrong_type
"""
import json
import sys
import time

mode = sys.argv[1]
out = sys.argv[sys.argv.index("-o") + 1]
atype = sys.argv[sys.argv.index("--type") + 1] if "--type" in sys.argv else "pcb"

if mode == "sleep":
    with open(out + ".tmp-partial", "w") as fh:
        fh.write("{")
    time.sleep(30)
    sys.exit(0)
if mode == "nothing":
    sys.stderr.write("boom\n")
    sys.exit(2)
if mode == "garbage":
    open(out, "w").write("{not json")
    sys.exit(0)
doc = {"analyzer_type": "thermal" if mode == "ok_wrong_type" else atype,
       "summary": {"total_findings": 0}, "findings": []}
json.dump(doc, open(out, "w"))
if mode == "ok_exit1":
    sys.exit(1)
if mode == "exit2":
    sys.exit(2)
sys.exit(0)
