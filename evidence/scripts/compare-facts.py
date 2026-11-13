"""Compare a reproduced facts.json with the committed one: a Markdown table of check statuses (CI job summary).
usage: python3 compare-facts.py <committed facts.json> <reproduced facts.json>   (exit 0 always; the table says it)"""
import json
import sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
ca, cb = ({c["id"]: c for c in f.get("checks", [])} for f in (a, b))
same = 0
print(f"## Stage 1 reproduced on CRACI: change {b.get('change')} (head {b.get('head')}, SDK {b.get('environment', {}).get('sdk')} "
      f"+ {b.get('environment', {}).get('sdk_execution_tests', '-')})\n")
print("| Check | Committed (local run) | This run | Same? | This run's summary |\n|---|---|---|---|---|")
for cid in list(dict.fromkeys([*ca, *cb])):
    x, y = ca.get(cid, {}), cb.get(cid, {})
    ok = x.get("status") == y.get("status")
    same += ok
    print(f"| {cid} | {x.get('status', 'absent')} | {y.get('status', 'absent')} | {'yes' if ok else '**NO**'} | {(y.get('summary') or '').replace('|', '/')[:160]} |")
print(f"\n{same} of {len(set(ca) | set(cb))} check statuses match the committed evidence.")
