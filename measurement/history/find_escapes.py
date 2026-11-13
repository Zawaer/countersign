#!/usr/bin/env python3
"""Propose escape candidates for the historical replay (step 1 of 2; step 2 is a human reading each one).

Input:  raw/prs.json + raw/bodies.json (gh pr list -R MessagePack-CSharp/MessagePack-CSharp --state merged --limit 600 --json ...)
        and a full clone of the upstream repo (default /data/src/mp; read-only: only git log/diff/blame).
Output: candidates.json: for every later fix/revert PR, which earlier PRs it points at, and why.

Three signals, strongest first:
  revert     a later PR titled "Revert ..." whose title quotes the PR's title, or whose body says "This reverts" + a commit of the PR
  reference  a later fix PR whose title/body mentions #<n> of the PR
  szz        SZZ: lines that a later fix PR deletes or modifies under src/ (non-test, non-generated) were last written by the PR
             (`git blame` on the fix's first parent). Pure-addition hunks (e.g. a missing guard) blame the line just above
             (weaker: `szz_adjacent`).
A candidate is NOT a label. labels.yaml records the human decision for each PR, with the link that justifies it.

Usage: python3 -I measurement/history/find_escapes.py [--repo /data/src/mp]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX_TITLE = re.compile(r"\b(fix|fixes|fixed|bug|crash|overflow|revert|regress|workaround|guard|broken|break|incorrect|wrong|prevent)\b", re.I)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=False).stdout


def load_prs():
    prs = {p["number"]: p for p in json.loads((HERE / "raw" / "prs.json").read_text())}
    for b in json.loads((HERE / "raw" / "bodies.json").read_text()):
        if b["number"] in prs:
            prs[b["number"]]["body"] = b.get("body") or ""
            prs[b["number"]]["closes"] = [i["number"] for i in b.get("closingIssuesReferences") or []]
    return prs


def commit_owner(repo, prs):
    """commit sha -> PR number. PRs are processed by merge time, so a sync PR (develop -> master) never claims
    commits an earlier feature PR already brought in."""
    owner = {}
    for p in sorted(prs.values(), key=lambda p: p["mergedAt"]):
        m = (p.get("mergeCommit") or {}).get("oid")
        if not m:
            continue
        parents = git(repo, "rev-list", "--parents", "-n1", m).split()[1:]
        shas = git(repo, "rev-list", f"{parents[0]}..{parents[1]}").split() + [m] if len(parents) == 2 else [m]
        for s in shas:
            owner.setdefault(s, p["number"])
    return owner


def is_src(path):
    return path.startswith("src/") and path.endswith(".cs") and not path.endswith(".g.cs") and "/Tests" not in path


def szz(repo, fix_sha, owner):
    """{pr: (lines blamed, adjacent lines blamed)} for the lines the fix deletes/modifies."""
    parents = git(repo, "rev-list", "--parents", "-n1", fix_sha).split()[1:]
    if not parents:
        return {}
    base = parents[0]
    out = defaultdict(lambda: [0, 0])
    cur = None
    for line in git(repo, "diff", "-U0", base, fix_sha).splitlines():
        if line.startswith("--- "):
            cur = line[6:] if line.startswith("--- a/") else None
            continue
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+", line)
        if not m or not cur or not is_src(cur):
            continue
        start, n = int(m.group(1)), int(m.group(2) or 1)
        adjacent = n == 0
        if adjacent:  # pure addition after line `start`: blame that line (weaker signal)
            n = 1
            if start == 0:
                continue
        blame = git(repo, "blame", "-l", "-s", "-L", f"{start},{start + n - 1}", base, "--", cur)
        for b in blame.splitlines():
            sha = b.split()[0].lstrip("^")
            pr = owner.get(sha)
            if pr:
                out[pr][1 if adjacent else 0] += 1
    return dict(out)


def main(argv):
    repo = argv[argv.index("--repo") + 1] if "--repo" in argv else "/data/src/mp"
    prs = load_prs()
    owner = commit_owner(repo, prs)
    later = sorted((p for p in prs.values() if p["mergedAt"] >= "2023-06"), key=lambda p: p["mergedAt"])
    cands = defaultdict(list)
    for f in later:
        title, body = f["title"], f.get("body", "")
        msha = (f.get("mergeCommit") or {}).get("oid")
        fixy = bool(FIX_TITLE.search(title)) or bool(FIX_TITLE.search(body[:400]))
        if title.lower().startswith("revert"):
            quoted = re.search(r'"(.+)"', title)
            for p in prs.values():
                if p["number"] != f["number"] and p["mergedAt"] < f["mergedAt"] and quoted and p["title"].strip() == quoted.group(1).strip():
                    cands[p["number"]].append({"signal": "revert", "by": f["number"], "title": title})
        for n in {int(x) for x in re.findall(r"#(\d{3,4})\b", title + " " + body)}:
            if n in prs and prs[n]["mergedAt"] < f["mergedAt"] and n != f["number"] and fixy:
                cands[n].append({"signal": "reference", "by": f["number"], "title": title})
        if fixy and msha:
            for pr, (direct, adj) in szz(repo, msha, owner).items():
                if pr != f["number"] and prs.get(pr, {}).get("mergedAt", "") < f["mergedAt"]:
                    cands[pr].append({"signal": "szz" if direct else "szz_adjacent", "by": f["number"], "title": title,
                                      "lines": direct, "adjacent_lines": adj})
    out = {str(k): v for k, v in sorted(cands.items())}
    (HERE / "candidates.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(out)} PRs with at least one escape signal")


if __name__ == "__main__":
    main(sys.argv[1:])
