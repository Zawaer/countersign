#!/usr/bin/env python3
"""Seed, build and test the mutants in measurement/mutants/mutants.json that have no evidence yet.

For each new mutant <id> (e.g. 2234-mut5):
  1. scratch worktree /data/src/mp-<id> at origin/ju26-issue-<n> (the checkout in /data/src/mp is never touched)
  2. evidence/scripts/mutate.py applies the one-line edit (asserts the `before` text is on that line)
  3. evidence/scripts/run.sh builds tests/MessagePack.SourceGenerator.Tests (SDK 8.0.402, -m:8), runs the change's
     targeted filter and the full suite -> /data/work/out/<id>/
  4. evidence/<id>/facts.json is assembled with the same functions evidence/scripts/facts.py uses for every other change

Usage: python3 measurement/mutants/seed.py [--only <id>...] [--facts-only]
Mutants carry no AI reviews yet; `countersign replay` lists them as "caught by checks alone" and routes them
deterministically (countersign/measure.py). Reviews dropped into reviews/<id>/ later are picked up automatically.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCRIPTS = ROOT / "evidence" / "scripts"
WORK = Path("/data/work")
SG = "tests/MessagePack.SourceGenerator.Tests/MessagePack.SourceGenerator.Tests.csproj"
FILTERS = {"2283": "FullyQualifiedName~GenericsFormatterTests.", "2234": "FullyQualifiedName~SuppressSourceGenerationAnalyzerTests.",
           "2129": "FullyQualifiedName~GeneratedMessagePackFormatterTests."}


def facts_module():
    spec = importlib.util.spec_from_file_location("cs_facts", SCRIPTS / "facts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.EVID = str(ROOT / "evidence")
    return mod


def seed(m: dict) -> None:
    n = m["id"].split("-")[0]
    wt = Path(f"/data/src/mp-{m['id']}")
    if not wt.exists():
        subprocess.run(["git", "-C", "/data/src/mp", "worktree", "add", "--detach", str(wt), f"origin/ju26-issue-{n}"], check=True)
    dirty = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if not dirty:
        subprocess.run([sys.executable, "-I", str(SCRIPTS / "mutate.py"), m["file"], str(m["line"]), m["before"], m["after"],
                        str(WORK / f"{m['id']}.json")], cwd=wt, check=True)
    subprocess.run([str(SCRIPTS / "run.sh"), m["id"], str(wt), SG, f"{SG}={FILTERS[n]}", "yes"], check=True)


def write_facts(m: dict, F) -> None:
    n = m["id"].split("-")[0]
    rec = json.loads((WORK / f"{m['id']}.json").read_text())
    branch = f"ju26-issue-{n}"
    head = F.git("rev-parse", f"origin/{branch}").strip()
    cd = os.path.join(F.EVID, m["id"])
    os.makedirs(cd, exist_ok=True)
    newset = F.new_tests(head)
    facts = {"change": m["id"], "branch": branch, "base": F.BASE[:8], "head": head[:8], "base_full": F.BASE, "head_full": head,
             "commit_message": F.git("log", "-1", "--format=%B", head).strip(), "author": F.git("log", "-1", "--format=%an", head).strip(),
             "agent_written": True, "diff": F.diff_facts(head), "new_tests_in_diff": sorted(newset),
             "mutation": {"of": n, "kind": m["kind"], "file": m["file"], "line": rec["line"], "before": rec["before"].strip(), "after": rec["after"].strip(),
                          "description": m["description"], "intended_effect": m["intended_effect"]},
             "diff_note": "diff/commit fields describe the unmutated branch; the mutation is applied on top of head as an uncommitted edit"}
    meta = F.read_meta(m["id"])
    base_full = F.parse_trx(os.path.join(F.OUT, "base", "full.trx")) or []
    base_fail = {t["name"] for t in base_full if t["outcome"] == "failed"}
    b, _ = F.build_check(m["id"], cd, meta)
    checks = [b]
    failed, fc = [], None
    if meta.get("build_rc") == "0":
        t = F.targeted_check(m["id"], cd, meta, newset)
        t["filter"], t["project"] = [FILTERS[n]], F.SG
        checks.append(t)
        failed = [x["name"] for x in t["tests"] if x["outcome"] == "failed"]
        facts["mutation"]["targeted_summary"] = t["summary"]
        fc = F.full_check(m["id"], cd, meta, base_fail)
        if fc:
            checks.append(fc)
    ex = exec9_check(m["id"], cd, F)
    if ex:
        checks.append(ex)
        failed += [f"{x['project']}: {x['name']}" for x in ex["tests"] if x["outcome"] == "failed"]
    facts["mutation"]["caught"] = bool(failed)
    facts["mutation"]["caught_by"] = failed
    facts["mutation"]["caught_by_full_suite"] = [x["name"] for x in fc["failures_not_on_base"]] if fc else []
    facts["mutation"]["caught_by_any_deterministic_check"] = bool(failed) or bool(fc and fc["failures_not_on_base"]) or b["status"] == "fail"
    facts["checks"] = checks
    facts["not_run"] = [{"id": "public_api", "reason": "mutant run: single-line internal edit; build + targeted + full suite only"},
                        {"id": "analyzers", "reason": "mutant run"},
                        *([] if Path(F.OUT, f"exec9-{m['id']}").exists() else [{"id": "tests.execution", "reason": "mutant run: SDK 9 ExecutionTests not run for this mutant"}]),
                        {"id": "tests.fail_without_fix", "reason": "mutant run: the mutant keeps the branch's tests, so this is the original's result"}]
    facts["environment"] = {"sdk": F.SDK, "os": "linux-x64 (container)", "configuration": "Debug", "max_cpu": 8}
    Path(cd, "facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    print(m["id"], [(c["id"], c["status"]) for c in checks], "caught" if facts["mutation"]["caught_by_any_deterministic_check"] else "SURVIVED")


def exec9_check(mid: str, cd: str, F) -> dict | None:
    """ExecutionTests + MapModeExecutionTests under SDK 9 (evidence/scripts/exec9.sh <id> /data/src/mp-<id> <filter>), if that run exists."""
    out = Path(F.OUT) / f"exec9-{mid}"
    if not (out / "meta.txt").exists():
        return None
    tests = []
    for proj in ("ExecutionTests", "MapModeExecutionTests"):
        trx = F.parse_trx(str(out / f"{proj}.full.trx")) or []
        tests += [{"project": proj, "name": t["name"], "outcome": t["outcome"]} for t in trx]
        F.copy_log(str(out / f"{proj}.full.log"), os.path.join(cd, "logs", f"execution_{proj}.full.log"))
    bad = [t for t in tests if t["outcome"] == "failed"]
    return {"id": "tests.execution_full_suite", "tool": "dotnet test (ExecutionTests, MapModeExecutionTests)", "tool_version": "9.0.321",
            "tool_version_note": "SDK 9 because the generator needs Roslyn 4.12; the repo pins 8.0.402",
            "status": "fail" if bad else ("pass" if tests else "error"),
            "summary": f"{len(tests) - len(bad)} passed, {len(bad)} failed", "tests": tests}


def main(argv: list[str]) -> None:
    if "--add-exec9" in argv:  # mutants seeded earlier by facts.py: append the SDK 9 execution run to their facts.json
        F = facts_module()
        for mid in argv[argv.index("--add-exec9") + 1:]:
            path = ROOT / "evidence" / mid / "facts.json"
            facts = json.loads(path.read_text())
            ex = exec9_check(mid, str(path.parent), F)
            if ex:
                facts["checks"] = [c for c in facts["checks"] if c["id"] != ex["id"]] + [ex]
                facts["not_run"] = [x for x in facts.get("not_run", []) if x["id"] != "tests.execution"]
                if ex["status"] == "fail":
                    facts["mutation"]["caught_by_any_deterministic_check"] = True
                path.write_text(json.dumps(facts, indent=2) + "\n")
                print(mid, ex["id"], ex["status"], ex["summary"])
        return
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    todo = [m for m in json.loads((HERE / "mutants.json").read_text())["mutants"] if "before" in m and (not only or m["id"] in only)]
    F = facts_module()
    for m in todo:
        if "--facts-only" not in argv:
            seed(m)
        write_facts(m, F)


if __name__ == "__main__":
    main(sys.argv[1:])
