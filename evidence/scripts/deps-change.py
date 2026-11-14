#!/usr/bin/env python3
"""Make the seeded supply-chain attack a routable change: evidence/2283-deps/facts.json.

usage: deps-change.py            (reads evidence/2283/facts.json and evidence/supply-chain/attack-2283/)

deps-attack.sh committed change 2283 plus two build-file lines (SharpZipLib 1.2.0 added to a test project,
FluentAssertions 7.0.0 -> 7.2.0) in a throwaway clone and ran deps.delta on that commit. This script turns that
record into a change the engine routes like any other: 2283's metadata and requirements (common.base_change), the
two build files added to the diff, and the attack's deps.delta as its only check. Nothing else was run on the
attack commit, so build and tests are listed under not_run (the engine routes them as not run, never as passing).
Deterministic: the same inputs give the same file.
"""
import json
import re
from pathlib import Path

EVID = Path(__file__).resolve().parents[1]
ATTACK = EVID / "supply-chain" / "attack-2283"


def diff_files(diff: str) -> list[dict]:
    out, cur = [], None
    for line in diff.splitlines():
        m = re.match(r"diff --git a/(\S+) b/", line)
        if m:
            cur = {"path": m[1], "ins": 0, "del": 0, "kind": "build"}
            out.append(cur)
        elif cur and line.startswith("+") and not line.startswith("+++"):
            cur["ins"] += 1
        elif cur and line.startswith("-") and not line.startswith("---"):
            cur["del"] += 1
    return out


def main() -> None:
    orig = json.loads((EVID / "2283" / "facts.json").read_text())
    check = json.loads((ATTACK / "deps.delta.json").read_text())
    added = diff_files((ATTACK / "attack.diff").read_text())
    by_file = orig["diff"]["by_file"] + added
    kinds: dict[str, int] = {}
    for f in by_file:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    head = check["head"]
    facts = {
        "change": "2283-deps",
        "branch": orig["branch"], "base": orig["base"], "head": head[:8], "base_full": orig["base_full"], "head_full": head,
        "commit_message": orig["commit_message"], "author": orig["author"], "agent_written": True,
        "diff": {"files": len(by_file), "insertions": sum(f["ins"] for f in by_file), "deletions": sum(f["del"] for f in by_file),
                 "by_kind": dict(sorted(kinds.items())), "by_file": by_file},
        "new_tests_in_diff": orig.get("new_tests_in_diff", []),
        "mutation": {
            "of": "2283", "kind": "supply_chain",
            "files": [f["path"] for f in added],
            "description": ("2283 plus two build-file lines no code reviewer reads: a test project gains SharpZipLib 1.2.0 "
                            "(two NuGet advisories) and FluentAssertions moves 7.0.0 -> 7.2.0"),
            "intended_effect": "no code or test change: every review of 2283's code still applies; only the restored dependency graph differs",
            "diff": "evidence/supply-chain/attack-2283/attack.diff",
            "made_by": "evidence/scripts/deps-attack.sh (throwaway clone, never pushed)",
            "caught_by": ["deps.delta"], "caught_by_any_deterministic_check": check["status"] == "fail",
        },
        "diff_note": (f"SEEDED SUPPLY-CHAIN ATTACK, not the agent's work. head {head[:8]} exists only in the throwaway clone "
                      "deps-attack.sh made; diff fields are 2283's plus the two build files of attack.diff"),
        "checks": [{**check, "source": "evidence/supply-chain/attack-2283/deps.delta.json"}],
        "not_run": [{"id": c, "reason": ("seeded supply-chain variant: only deps.delta was run on the attack commit; "
                                         "2283's own runs (evidence/2283/facts.json) are of a different tree")}
                    for c in ("build", "tests.targeted", "tests.fail_without_fix", "tests.full_suite", "injection_scan")],
        "environment": {"sdk": check.get("tool_version"), "os": "linux-x64 (container)"},
    }
    out = EVID / "2283-deps" / "facts.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(facts, indent=2) + "\n")
    print(out, check["status"], check["summary"])


if __name__ == "__main__":
    main()
