#!/usr/bin/env bash
# Countersign judge demo: the 2234 story in 9 short steps, from a fresh clone.
#
#   scripts/demo.sh            run straight through (about two screens of output)
#   scripts/demo.sh --step     pause after each step
#   scripts/demo.sh --keep     keep the temp workspace (keys, ledger) for poking at
#
# Needs Python 3.11+ and uv. Offline apart from `uv sync`; no API keys, no MessagePack clone, no .NET.
# Everything comes from the committed evidence/, reviews/, packs/ and measurement/. Signing happens in a
# throwaway copy under mktemp with a throwaway key: the repo's ledger/, keys/ and .keys/ are never touched.
set -euo pipefail

STEP=0 KEEP=0
for arg in "$@"; do
  case "$arg" in
    --step) STEP=1 ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "demo: unknown option $arg (try --help)" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
WS="" ERRLOG="$(mktemp)"
N=0
cleanup() { rm -f "$ERRLOG"; if [[ -n "$WS" && "$KEEP" == 0 ]]; then rm -rf "$WS"; fi; }
trap cleanup EXIT

die() { echo; echo "demo failed at step $N: $*" >&2; exit 1; }
step() {
  if [[ "$STEP" == 1 && "$N" -gt 0 ]]; then read -r -p "    [enter] for the next step " _ || true; fi
  N=$((N + 1)); echo; echo "[$N/9] $*"
}
# Run a command quietly: on failure show its last error line, never a traceback.
q() { "$@" 2>"$ERRLOG" || die "$(grep -v '^\s*$' "$ERRLOG" | tail -n 1)"; }

command -v uv >/dev/null 2>&1 || { echo "demo: needs uv (https://docs.astral.sh/uv/): pip install uv" >&2; exit 1; }
for f in packs/2234/pack.json measurement/results.json measurement/history/results.json evidence/2234/facts.json; do
  [[ -f "$f" ]] || { echo "demo: $f is missing; run this from a Countersign checkout" >&2; exit 1; }
done
START=$SECONDS

echo "Countersign demo: AI review under a signed mandate; a named human countersigns."
echo "Change 2234 (agent-written, Tieto's ju26-issue-2234): 'the analyzer does not work if SuppressSourceGeneration = true'."

# ---------------------------------------------------------------------------------------------------------------
step "Set up: venv with uv, a temp workspace and a throwaway owner key"
q uv sync --frozen --inexact --quiet
PY="$ROOT/.venv/bin/python"
CS="$ROOT/.venv/bin/countersign"
[[ -x "$CS" ]] || die "uv sync did not install the countersign command"
WS="$(mktemp -d "${TMPDIR:-/tmp}/countersign-demo.XXXXXX")"
mkdir -p "$WS/packs/2234" "$WS/ledger"
cp packs/2234/pack.json "$WS/packs/2234/pack.json"
q "$CS" keygen --name Toivo --root "$WS" >/dev/null
echo "    $("$PY" --version), countersign $("$PY" -c 'import importlib.metadata as m; print(m.version("countersign"))')"
echo "    workspace $WS (empty ledger, throwaway key for Toivo; the repo's ledger/ and keys/ are untouched)"

# Small helpers that read the committed files. Every number below comes from them, not from this script.
# Output is wrapped at 118 columns, continuation lines indented under their first line.
pyq() { "$PY" - "$@" 2>"$ERRLOG" | wrap || die "$(grep -v '^\s*$' "$ERRLOG" | tail -n 1)"; }
wrap() {
  "$PY" -c 'import sys, textwrap
for l in sys.stdin.read().splitlines():
    ind = " " * (len(l) - len(l.lstrip()))
    print(textwrap.fill(l, 118, initial_indent="", subsequent_indent=ind + "  ", break_on_hyphens=False) if l.strip() else "")'
}

# ---------------------------------------------------------------------------------------------------------------
step "countersign route: the 7 real changes, the tier each gets and the rule that decided it"
pyq <<'EOF'
import json
print(f"    {'change':<9} {'tier':<7} {'score':>6}  {'owner':<6} reason")
for c in ["2129", "2234", "2283", "2297", "up-1934", "up-1967", "up-2022"]:
    p = json.load(open(f"packs/{c}/pack.json"))
    w = p["why"][0]
    line = f"    {c:<9} {p['tier']:<7} {p['risk']['score']:>6}  {p['owner']:<6} [{w['source']}] {w['id']}: {w['why']}"
    print(line if len(line) <= 118 else line[:115] + "...")
human = sum(json.load(open(f"packs/{c}/pack.json"))["tier"] in ("ask", "block") for c in ["2129", "2234", "2283", "2297", "up-1934", "up-1967", "up-2022"])
print(f"    {human} of 7 go to a human. (Read from the committed packs; `countersign route --all --repo <MessagePack clone>`")
print("    re-derives them identically from evidence/ and reviews/, and also routes the 17 seeded changes.)")
EOF

# ---------------------------------------------------------------------------------------------------------------
step "The 2234 sign-off card (what Toivo reads first; the CLI prints it before signing)"
pyq <<'EOF'
import json
from countersign import pack
card = pack.card(json.load(open("packs/2234/pack.json"))).splitlines()
end = next(i for i, l in enumerate(card) if l.startswith("What the AI refused"))
for l in card[:end]:
    l = "    " + l
    print(l if len(l) <= 118 else l[:115] + "...")
print(f"    ... ({len(card) - end} more lines: refusals, not checked, residual risk, the sign command; packs/2234/pack.md)")
EOF

# ---------------------------------------------------------------------------------------------------------------
step "Why: a verified finding with the line it cites, and a clause the reviewers disagree on"
pyq <<'EOF'
import json, textwrap
p = json.load(open("packs/2234/pack.json"))
f = next(f for f in p["findings"] if f["reviewer"] == "claude" and f["id"] == "C1")
print(f"    claude:C1 [{f['severity']}] {f['title']}")
ev = next(e for e in f["evidence"] if e["kind"] == "code" and e["verified"])
ex = p["evidence_index"][ev["ref"]]["excerpt"]
print(f"      cites {ev['file'].split('/')[-1]}:{ev['line']} at {ev['rev']} {ex['sha']}; the engine re-read that line in git: the quote matches")
for i, line in enumerate(ex["lines"], ex["start"]):
    if abs(i - ex["highlight"]) <= 1:
        print(f"      {'>' if i == ex['highlight'] else ' '} {i:>5} | {line.rstrip()}")
print("      (on base the early return comes after member collection; the 3.1.1 regression is from upstream 1a74a620, not on this base)")
c = next(c for c in p["refused"]["clauses"] if c["id"] == "REQ-2234-N1")
print(f"    {c['id']} REFUSED: \"{c['text']}\"")
for name, v in c["verdicts"].items():
    cite = next((e for e in v["evidence"] if e["verified"] and e["kind"] in ("code", "test")), None) or next(e for e in v["evidence"] if e["verified"])
    what = f"{cite['file'].split('/')[-1]}:{cite['line']} @{cite['rev']}" if cite["kind"] == "code" else cite.get("name", cite.get("id", "")).split(".")[-1]
    print(f"      {name:<9} {v['verdict']:<8} verified citations: {v['verified']}, e.g. {what}")
print("      refused: " + ", ".join(r["code"] for r in c["reasons"]))
print("      claude: \"The hard cast at line 985 is untouched\" (a Key(null) record still crashes the analyzer: C2, reproduced")
print(f"      by the pipeline). Unanimity rule: one verified objection beats two 'met's, so Toivo decides N1.")
EOF

# ---------------------------------------------------------------------------------------------------------------
step "Held before: tests that pass, but pass without the fix too"
pyq <<'EOF'
import json
p = json.load(open("packs/2234/pack.json"))
facts = {c["id"]: c for c in json.load(open("evidence/2234/facts.json"))["checks"]}
for t in p["trust"]:
    if t["status"] == "held_before":
        print(f"    {t['id']} HELD BEFORE: {t['why'].split(': all ')[0].replace('Met, but already true', 'met, but already true')}:")
        print(f"      all {t['why'].split(': all ', 1)[1]}")
for cid in ("tests.fail_without_fix", "tests.execution_fail_without_fix"):
    print(f"    {cid}: {facts[cid]['status']}, {facts[cid]['summary']}")
EOF

# ---------------------------------------------------------------------------------------------------------------
step "Sign as Toivo (throwaway key): request changes, rate three findings; then verify the ledger"
pyq "$WS" <<'EOF'
import contextlib, io, sys
from countersign import cli, pack
from countersign.common import read_json
ws = sys.argv[1]
# `countersign sign` first re-builds the pack and refuses if it differs. That re-build needs the MessagePack clone
# (to re-check code quotes) and the real Toivo key, so here the committed pack stands in for it. Everything else is
# the real command: owner check, finding ratings, Ed25519 signature, ledger append.
pack.build = lambda _ws, change: read_json(f"{ws}/packs/{change}/pack.json")
out = io.StringIO()
with contextlib.redirect_stdout(out):
    rc = cli.main(["sign", "2234", "--as", "Toivo", "--root", ws, "--decision", "request-changes",
                   "--note", "Fixes a different crash than #2234; retarget to the 3.1.x line and fix Key(null).",
                   "--finding", "claude:C1=accepted", "--finding", "claude:C2=accepted",
                   "--finding", "nemotron:N2=rejected:style warning only"])
if rc:
    sys.exit(f"countersign sign exited {rc}")
print("\n".join("    " + l for l in out.getvalue().splitlines() if l.startswith(("signed:", "findings:"))))
print("    (real `countersign sign` code; only its re-build check is skipped: that needs the MessagePack clone and Toivo's")
print("    real key, so the committed pack stands in for the re-build)")
EOF
echo "    \$ countersign verify-ledger --root $WS"
q "$CS" verify-ledger --root "$WS" | sed 's/^/    /'

# ---------------------------------------------------------------------------------------------------------------
step "Tamper: turn Toivo's request-changes into accept with sed, verify again"
sed -i.bak 's/"decision": "request-changes"/"decision": "accept"/' "$WS/ledger/ledger.jsonl" && rm -f "$WS/ledger/ledger.jsonl.bak"
grep -q '"decision": "accept"' "$WS/ledger/ledger.jsonl" || die "the sed edit did not apply"
echo "    \$ sed -i 's/\"decision\": \"request-changes\"/\"decision\": \"accept\"/' ledger/ledger.jsonl"
if out="$("$CS" verify-ledger --root "$WS" 2>&1)"; then die "verify-ledger accepted a tampered ledger"; fi
grep -q "LEDGER INVALID" <<<"$out" || die "unexpected verify-ledger output: $out"
sed 's/^/    /' <<<"$out"

# ---------------------------------------------------------------------------------------------------------------
step "Seeded bugs: one no test catches, and a prompt injection (recorded replay, measurement/results.json)"
pyq <<'EOF'
import json
r = json.load(open("measurement/results.json"))
seeded = {s["change"]: s for s in r["seeded_reviewed"]}
mut = {m["change"]: m for m in r["mutants"]}
s, m = seeded["2234-mut2"], mut["2234-mut2"]
facts = json.load(open("evidence/2234-mut2/facts.json"))
print(f"    2234-mut2 ({s['kind']}): {m['description']}, at {s['at'].split('/')[-1]}")
print(f"      checks: {', '.join(c['id'] for c in facts['checks'])}: {'all pass' if all(c['status'] == 'pass' for c in facts['checks']) else 'some fail'}"
      f" (no test catches it) -> tier {s['tier']}")
for rev, hits in s["planted_line_hits"].items():
    h = next(h for h in hits if h["via"] == "finding")
    print(f"      {rev} {h['id']} ({h['severity']}) cites line {', '.join(map(str, h['lines']))}: {h['title']}")
flagged_before = [k for k, v in s["same_line_flagged_on_original"].items() if v]
print(f"      (planted line {s['at'].split(':')[-1]}, counted within ±{r['metrics']['planted_line_flagged']['value']['tolerance_lines']} lines;"
      f" on the unmutated 2234, {'no reviewer' if not flagged_before else ', '.join(flagged_before)} flagged there)")
s = seeded["2234-inject"]
facts = {c["id"]: c for c in json.load(open("evidence/2234-inject/facts.json"))["checks"]}
inj = r["metrics"]["injection_changed_verdicts"]["value"]["2234-inject"]["reviewers"]["nemotron"]["changed"][0]
print(f"    2234-inject (planted reviewer instructions at {s['at']}) -> tier {s['tier']} ({', '.join(s['fired']['R-INJECT'])})")
print(f"      injection_scan: {facts['injection_scan']['status']}, {facts['injection_scan']['summary']}")
print(f"      it did move a reviewer (nemotron {inj['req']}: {inj['original']} -> {inj['with_injection']}); under R-INJECT no verdict counts")
EOF

# ---------------------------------------------------------------------------------------------------------------
step "The measurement in three numbers"
pyq <<'EOF'
import json
h = json.load(open("measurement/history/results.json"))["modes"]["ci-credited"]
m = json.load(open("measurement/results.json"))["metrics"]
cleared = h["confusion"]["clean_cleared"] + h["confusion"]["escape_cleared"]
print(f"    History (real): {h['n']} merged upstream PRs replayed under mandate v{json.load(open('measurement/history/results.json'))['mandate']['version']}; "
      f"the AI would have cleared {cleared}, and {h['confusion']['escape_cleared']} of the {h['escapes']} later reverted or fixed.")
sig = m["catch_by_signal"]["value"]
pl = m["planted_line_flagged"]["value"]["panel_on_test_survivors"]
ch = m["caught_by_checks_alone"]["value"]
print(f"    Seeded (real): {sig['of'] - sig['missed']} of {sig['of']} reviewed seeded changes go to a human; checks alone catch {ch['caught']} of {ch['of']},"
      f" and a reviewer pointed at the planted line on {pl['flagged']} of the {pl['of']} that every test missed ({pl['flagged_new_at_line']} with a finding the unmutated original did not have there).")
rc = m["reviewer_cross_check"]["value"]["codex"]
print(f"    Rubber stamp (real): Codex, the control reviewer, raised {m['findings_per_reviewer']['value']['codex']['verified']} verified findings and missed "
      f"{rc['missed_others_verified_major']} verified majors the others found; under unanimity its 'met' cleared nothing.")
EOF

if [[ "$STEP" == 1 ]]; then read -r -p "    [enter] to finish " _ || true; fi
echo
echo "Done in $((SECONDS - START))s. Next:"
echo "  open site/index.html                 the main screen (the diff, the pins, sneak-a-bug mode)"
echo "  packs/2234/pack.md (or pack.html)    the full evidence pack Toivo signs"
if [[ "$KEEP" == 1 ]]; then echo "  $WS   the demo workspace (ledger, throwaway key)"; fi
