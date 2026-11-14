#!/usr/bin/env python3
"""deps.delta: the supply-chain side of a change, as a stage-1 check (countersign/sbom.py does the work).

usage: deps-delta.py <change> [--summary FILE] [--head SHA --standalone DIR]
  For the base and the head of the change: export the tree (git archive, so no worktree is touched), restore every
  *.csproj in it through a throwaway solution with NuGet Audit on (mode=all), read the restored graph, write a
  CycloneDX SBOM, then diff them. The check is appended to <EVID>/<change>/facts.json (any older deps.delta is
  replaced; every other key and check is left as it was) and the SBOMs go to <EVID>/<change>/sbom.cdx.json
  (head) and <EVID>/base/sbom.cdx.json (base).

--head SHA --standalone DIR: diff base against any commit in CS_REPO (e.g. the seeded supply-chain attack made by
deps-attack.sh) and write DIR/deps.delta.json + DIR/sbom.cdx.json instead of touching a facts.json.

env (defaults = the original local run): CS_REPO (/data/src/mp), WORK (/data/work), CS_EVID (this repo's evidence/),
CS_ALLOWED_DEPS (names or name@version allowed to be new: the mandate's allowed_new_dependencies; empty = none).
dotnet must be on PATH (the SDK in the tree's global.json: 8.0.402).
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from countersign import sbom  # noqa: E402

REPO = os.environ.get("CS_REPO", "/data/src/mp")
WORK = Path(os.environ.get("WORK", "/data/work"))
EVID = Path(os.environ.get("CS_EVID", str(HERE.parent)))
BASE = "32258fdbee4bcd653c79f51b4376b5103c6f4d27"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout


def restored(sha: str) -> tuple[Path, dict, dict, str]:
    """Export + restore one commit once (cached under $WORK/deps/<sha>); returns (root, graph, inputs, sdk)."""
    root = WORK / "deps" / sha
    done = root / ".countersign-restored"
    log = WORK / "deps" / f"{sha}.restore.log"
    if not done.exists():
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True)
        arch = subprocess.run(["git", "-C", REPO, "archive", sha], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(root)], input=arch, check=True)
        projs = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.csproj"))
        (root / "projects.txt").write_text("\n".join(projs) + "\n")
        sln = "countersign-deps.sln"
        subprocess.run(["dotnet", "new", "sln", "-n", "countersign-deps", "-o", str(root)], capture_output=True, check=True)
        subprocess.run(["dotnet", "sln", str(root / sln), "add", *projs], cwd=root, capture_output=True, check=True)
        r = subprocess.run(["dotnet", "restore", sln, "-p:NuGetAudit=true", "-p:NuGetAuditMode=all", "-p:NuGetAuditLevel=low",
                            "-p:TreatWarningsAsErrors=false", "-m:8"], cwd=root, capture_output=True, text=True)
        log.write_text(f"### dotnet restore ({len(projs)} projects) rc={r.returncode}\n{r.stdout}{r.stderr}")
        done.write_text(str(r.returncode))
    projs = (root / "projects.txt").read_text().split()
    graph = sbom.read_graph(root)
    sbom.add_unrestored(graph, projs, sbom.parse_restore_errors(log.read_text(), root))
    sdk = subprocess.run(["dotnet", "--version"], cwd=root, capture_output=True, text=True).stdout.strip()
    return root, graph, sbom.tree_inputs(root), sdk


def main():
    change = sys.argv[1]
    summary = sys.argv[sys.argv.index("--summary") + 1] if "--summary" in sys.argv else None
    n = change.split("-")[0]
    arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None  # noqa: E731
    head = arg("--head") or git("rev-parse", f"origin/ju26-issue-{n}").strip()
    standalone = arg("--standalone")
    cd = Path(standalone) if standalone else EVID / change
    facts_path = cd / "facts.json"
    _, bg, bi, bsdk = restored(BASE)
    _, hg, hi, hsdk = restored(head)
    name = "junction26-messagepack-csharp"
    bdoc = sbom.cyclonedx(bg, bi, name=name, sha=BASE, sdk=bsdk)
    hdoc = sbom.cyclonedx(hg, hi, name=name, sha=head, sdk=hsdk)
    sbom.write_json(EVID / "base" / "sbom.cdx.json", bdoc)  # the same base for every change
    sbom.write_json(cd / "sbom.cdx.json", hdoc)
    check = sbom.delta(bg, hg, bi, hi, allowed=sbom.env_list("CS_ALLOWED_DEPS"))
    rel = os.path.relpath(cd, EVID.parent)
    if standalone:
        rel = os.path.relpath(cd.resolve(), EVID.parent.resolve())
    check["tool_version"] = hsdk
    check["sbom"] = {"base": f"{os.path.relpath(EVID / 'base', EVID.parent)}/sbom.cdx.json", "head": f"{rel}/sbom.cdx.json",
                     "base_serial": bdoc["serialNumber"], "head_serial": hdoc["serialNumber"]}
    check["scope"] = (f"all {len(hg['projects'])} *.csproj in the tree (src, tests, sandbox, benchmark), restored as one throwaway "
                      "solution; the graph is NuGet's restore output (obj/**/project.assets.json)")
    if standalone:
        check["head"] = head
        sbom.write_json(cd / "deps.delta.json", check)
    else:
        facts = json.loads(facts_path.read_text())
        facts["checks"] = [c for c in facts["checks"] if c["id"] != "deps.delta"] + [check]
        facts_path.write_text(json.dumps(facts, indent=2))
    print(change, "deps.delta", check["status"], "-", check["summary"])
    if summary:
        with open(summary, "a") as f:
            f.write(markdown(change, check))


def markdown(change, c):
    out = [f"\n## Supply chain: deps.delta for {change} ({c['status']})\n", c["summary"] + "\n"]
    rows = [(x["package"], "-", x["version"], "direct" if x["direct"] else "transitive", "; ".join(x["via"][:1])) for x in c["packages_added"]]
    rows += [(x["package"], ", ".join(x["from"]), x["to"], "direct" if x["direct"] else "transitive", "; ".join(x["via"][:1]))
             for x in c["versions_changed"]]
    if rows:
        out.append("| Package | Base | Head | Kind | Pulled in by |\n|---|---|---|---|---|")
        out += [f"| {' | '.join(r)} |" for r in rows]
    for v in c["vulnerabilities_new"]:
        out.append(f"- new vulnerability: {v['package']} {v['version']} {v['severity']} {v['advisory']}")
    if c["projects_added"]:
        out.append(f"- new projects: {', '.join(c['projects_added'])}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
