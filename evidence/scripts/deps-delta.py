#!/usr/bin/env python3
"""deps.delta: the supply-chain side of a change, as a stage-1 check (countersign/sbom.py does the work).

usage: deps-delta.py <change> [--summary FILE] [--head SHA --standalone DIR]
  For the base and the head of the change: export the tree (git archive, so no worktree is touched), restore every
  *.csproj in it through a throwaway solution with NuGet Audit on (mode=all), once per configuration (Debug and
  Release: a PackageReference conditioned on Release is not in a Debug restore), read the union of the restored
  graphs, write a CycloneDX SBOM, then diff them. The check is appended to <EVID>/<change>/facts.json (any older deps.delta is
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


CONFIGURATIONS = ("Debug", "Release")  # red team S6: a PackageReference can be conditioned on the configuration


def restore_configurations(populate, root: Path, log_prefix: Path, *, dotnet: str = "dotnet", env: dict | None = None) -> dict:
    """Restore every *.csproj of one tree once per configuration and return the union of the package graphs
    (sbom.merge_configurations: a package in any configuration counts, and records which). `populate(dir)` fills an
    empty directory with the tree; each configuration gets its own copy under root/<configuration>, because
    obj/project.assets.json does not depend on the configuration and a second restore in place would overwrite the
    first. Each copy is restored once (marker file), so a re-run reads the cached graph."""
    graphs = {}
    for cfg in CONFIGURATIONS:
        tree = root / cfg
        done = tree / ".countersign-restored"
        log = Path(f"{log_prefix}.{cfg}.restore.log")
        if not done.exists():
            shutil.rmtree(tree, ignore_errors=True)
            tree.mkdir(parents=True)
            populate(tree)
            projs = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*.csproj"))
            (tree / "projects.txt").write_text("\n".join(projs) + "\n")
            sln = "countersign-deps.sln"
            subprocess.run([dotnet, "new", "sln", "-n", "countersign-deps", "-o", str(tree)], capture_output=True, check=True, env=env)
            subprocess.run([dotnet, "sln", str(tree / sln), "add", *projs], cwd=tree, capture_output=True, check=True, env=env)
            r = subprocess.run([dotnet, "restore", sln, f"-p:Configuration={cfg}", "-p:NuGetAudit=true", "-p:NuGetAuditMode=all",
                                "-p:NuGetAuditLevel=low", "-p:TreatWarningsAsErrors=false", "-m:8"],
                               cwd=tree, capture_output=True, text=True, env=env)
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(f"### dotnet restore -p:Configuration={cfg} ({len(projs)} projects) rc={r.returncode}\n{r.stdout}{r.stderr}")
            done.write_text(str(r.returncode))
        projs = (tree / "projects.txt").read_text().split()
        g = sbom.read_graph(tree)
        sbom.add_unrestored(g, projs, sbom.parse_restore_errors(log.read_text(), tree))
        graphs[cfg] = g
    return sbom.merge_configurations(graphs)


def restored(sha: str) -> tuple[Path, dict, dict, str]:
    """Export one commit (git archive, no worktree touched) and restore it in every configuration (cached under
    $WORK/deps/<sha>/<configuration>); returns (root of the first configuration's tree, merged graph, inputs, sdk)."""
    root = WORK / "deps" / sha

    def populate(tree: Path) -> None:
        arch = subprocess.run(["git", "-C", REPO, "archive", sha], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(tree)], input=arch, check=True)

    graph = restore_configurations(populate, root, WORK / "deps" / sha)
    tree = root / CONFIGURATIONS[0]
    sdk = subprocess.run(["dotnet", "--version"], cwd=tree, capture_output=True, text=True).stdout.strip()
    return tree, graph, sbom.tree_inputs(tree), sdk


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
