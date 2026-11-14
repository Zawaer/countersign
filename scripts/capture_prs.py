#!/usr/bin/env python3
"""Capture what a reviewer sees on the demo PRs, for site/prs.html.

The demo repo (Zawaer/countersign-messagepack-demo) is private until Sunday, so the site build (CI, no token) cannot
read it. Run this once with a logged-in `gh`; it writes site/data/pr-capture.json, which site/build.py renders.

Only public-by-design data is kept: PR metadata, the sticky Countersign comment (Markdown), the commit statuses and
the branch protection's required checks. No tokens, headers or other comments.

    python3 scripts/capture_prs.py            # PRs 2 and 4
    python3 scripts/capture_prs.py 1 2 3 4
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

REPO = "Zawaer/countersign-messagepack-demo"
OUT = Path(__file__).resolve().parent.parent / "site" / "data" / "pr-capture.json"
STICKY = "<!-- countersign:sticky -->"


def gh(*args: str):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def capture_pr(n: int) -> dict:
    pr = gh("pr", "view", str(n), "-R", REPO, "--json",
            "number,title,url,author,labels,assignees,state,mergeStateStatus,headRefName,baseRefName,headRefOid,"
            "commits,changedFiles,additions,deletions,createdAt")
    head = pr["headRefOid"]
    # The latest status per context on the PR head (what the merge box shows); the list is newest first and,
    # unlike the combined-status endpoint, names who posted each one.
    statuses, seen = [], set()
    for s in gh("api", f"repos/{REPO}/commits/{head}/statuses"):
        if s["context"] in seen:
            continue
        seen.add(s["context"])
        statuses.append({"context": s["context"], "state": s["state"], "description": s["description"],
                         "creator": (s.get("creator") or {}).get("login"), "updated_at": s["updated_at"], "target_url": s["target_url"]})
    comments = gh("api", "--paginate", f"repos/{REPO}/issues/{n}/comments")
    sticky = next((c for c in comments if c["body"].startswith(STICKY)), None)
    app = (sticky or {}).get("performed_via_github_app") or {}
    return {
        "number": pr["number"], "title": pr["title"], "url": pr["url"], "author": pr["author"]["login"],
        "labels": [{"name": x["name"], "color": x["color"]} for x in pr["labels"]],
        "assignees": [x["login"] for x in pr["assignees"]],
        "state": pr["state"], "mergeStateStatus": pr["mergeStateStatus"],
        "head": pr["headRefName"], "base": pr["baseRefName"], "head_sha": head,
        "commits": len(pr["commits"]), "changed_files": pr["changedFiles"],
        "additions": pr["additions"], "deletions": pr["deletions"], "created_at": pr["createdAt"],
        "statuses": statuses,
        "sticky_comment": None if not sticky else {
            "user": sticky["user"]["login"], "app": {"id": app.get("id"), "name": app.get("name"), "slug": app.get("slug")},
            "updated_at": sticky["updated_at"], "url": sticky["html_url"], "body": sticky["body"]},
    }


def main() -> None:
    prs = [int(x) for x in sys.argv[1:]] or [2, 4]
    prot = gh("api", f"repos/{REPO}/branches/main/protection")
    rsc = prot.get("required_status_checks") or {}
    data = {
        "repo": REPO,
        "captured_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "captured_with": "scripts/capture_prs.py (gh api)",
        "protection": {"branch": "main", "required_checks": [{"context": c["context"], "app_id": c.get("app_id")} for c in rsc.get("checks", [])],
                       "strict": rsc.get("strict"), "enforce_admins": (prot.get("enforce_admins") or {}).get("enabled"),
                       "allow_force_pushes": (prot.get("allow_force_pushes") or {}).get("enabled")},
        "prs": [capture_pr(n) for n in prs],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT, "PRs", prs, "required:", data["protection"]["required_checks"])


if __name__ == "__main__":
    main()
