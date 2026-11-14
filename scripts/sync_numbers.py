#!/usr/bin/env python3
"""Keep the headline numbers in the docs equal to the files they come from.

Docs mark a number like this:  <!--n:history_cleared-->24<!--/n-->
`python3 scripts/sync_numbers.py` rewrites every marked span from the source files;
`python3 scripts/sync_numbers.py --check` exits 1 (and lists them) if any span is stale, so CI catches drift.
Every value below says where it comes from; nothing is typed by hand.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "docs/CONCEPT_CARD.md", "docs/pitch/submission.md", "docs/pitch/qa-prep.md",
        "docs/pitch/deck.md", "docs/SCALING.md", "docs/MEASUREMENT.md", "docs/LESSONS.md",
        "docs/security/REDTEAM.md", "docs/PR_FLOW.md", "docs/pitch/video-script.md"]
SPAN = re.compile(r"<!--n:([a-z0-9_]+)-->(.*?)<!--/n-->", re.S)


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def values() -> dict[str, str]:
    r = _json("measurement/results.json")["metrics"]
    v = lambda k: r[k]["value"] if isinstance(r[k], dict) and "value" in r[k] else r[k]  # noqa: E731
    h = _json("measurement/history/results.json")
    ci = h["modes"]["ci-credited"]
    mandate = re.search(r"^version:\s*['\"]?(\d+)", (ROOT / "mandate/messagepack.mandate.yaml").read_text(), re.M)
    # red team: every attack in tests/redteam/attacks.py; the strict xfails are the ones still getting through
    attacks_src = (ROOT / "tests/redteam/attacks.py").read_text()
    attack_ids = set(re.findall(r'^\s*\(\s*"([A-Z]+\d+[a-z]?)"', attacks_src, re.M))
    misses = re.search(r"KNOWN_MISSES\s*=\s*(\{[^}]*\}|set\(\))", (ROOT / "tests/redteam/test_redteam_attacks.py").read_text())
    open_ids = set(re.findall(r'"([A-Z]+\d+[a-z]?)"', misses.group(1))) if misses else set()
    checks = v("caught_by_checks_alone")
    signal = v("catch_by_signal")
    ledger = [json.loads(line) for line in (ROOT / "ledger/ledger.jsonl").read_text().splitlines() if line.strip()]
    out = {
        "history_prs": ci["n"],
        "history_cleared": ci["confusion"]["clean_cleared"] + ci["confusion"]["escape_cleared"],
        "history_routed": ci["routed_to_humans"],
        "history_escapes": ci["escapes"],
        "history_escapes_cleared": ci["confusion"]["escape_cleared"],
        "history_mandate": h["mandate"]["version"],
        "mandate_version": mandate.group(1) if mandate else "?",
        "seeded_total": checks["of"],
        "seeded_caught_by_checks": checks["caught"],
        "seeded_reviewed": signal["of"],
        "seeded_reviewer_on_line": signal["reviewer_on_planted_line"],
        "redteam_total": len(attack_ids),
        "redteam_stopped": len(attack_ids - open_ids),
        "redteam_open": len(open_ids),
        "signoffs": v("signoffs"),
        "ledger_entries": len(ledger),
        "share_routed_real_pct": round(100 * v("share_routed_to_humans")),
    }
    return {k: str(x) for k, x in out.items()}


def sync(check: bool) -> int:
    vals, stale, unknown = values(), [], []
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text()

        def repl(m: re.Match) -> str:
            key, old = m.group(1), m.group(2)
            if key not in vals:
                unknown.append(f"{rel}: {key}")
                return m.group(0)
            if old != vals[key]:
                stale.append(f"{rel}: {key} {old!r} -> {vals[key]!r}")
            return f"<!--n:{key}-->{vals[key]}<!--/n-->"

        new = SPAN.sub(repl, text)
        if new != text and not check:
            p.write_text(new)
    for u in unknown:
        print(f"unknown key: {u}", file=sys.stderr)
    for s in stale:
        print(("stale: " if check else "updated: ") + s)
    if check and (stale or unknown):
        return 1
    return 1 if unknown else 0


if __name__ == "__main__":
    if "--print" in sys.argv:
        print(json.dumps(values(), indent=2))
        sys.exit(0)
    sys.exit(sync("--check" in sys.argv))
