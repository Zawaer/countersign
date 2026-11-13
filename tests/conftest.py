"""A tiny, self-contained workspace: a git repo with one fix, facts, two reviews, the real mandate, signed keys."""

import shutil
import subprocess
from pathlib import Path

import pytest

from countersign import keys, mandate
from countersign.common import Workspace, write_json

ROOT = Path(__file__).resolve().parents[1]
SRC = "src/MessagePack.SourceGenerator/Collector.cs"
TEST = "tests/MessagePack.SourceGenerator.Tests/CollectorTests.cs"
BASE_CODE = "class Collector\n{\n    void Add(int key)\n    {\n        members.Add(key, item);\n    }\n}\n"
HEAD_CODE = "class Collector\n{\n    void Add(int key)\n    {\n        if (!members.ContainsKey(key))\n        {\n            members.Add(key, item);\n        }\n    }\n}\n"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def make_facts(**over):
    facts = {
        "change": "9001", "branch": "ju26-issue-9001", "base": over.pop("base", "BASE"), "head": over.pop("head", "HEAD"),
        "commit_message": "fix duplicate keys", "author": "agent", "agent_written": True,
        "diff": {"files": 2, "insertions": 30, "deletions": 1, "by_file": [
            {"path": SRC, "ins": 4, "del": 1, "kind": "source"}, {"path": TEST, "ins": 26, "del": 0, "kind": "test"}]},
        "checks": [
            {"id": "build", "tool": "dotnet build", "tool_version": "8.0.402", "status": "pass", "summary": "0 errors"},
            {"id": "tests.targeted", "tool": "dotnet test", "status": "pass", "summary": "1 passed",
             "tests": [{"name": "CollectorTests.DuplicateKeys", "outcome": "passed", "new": True}]},
            {"id": "tests.fail_without_fix", "status": "pass", "summary": "new test fails on base"},
            {"id": "tests.full_suite", "status": "pass", "summary": "all passed"},
            {"id": "public_api", "status": "pass", "summary": "no public API changes", "changed": False},
        ],
        "not_run": [{"id": "benchmarks", "reason": "no perf-sensitive path"}],
    }
    facts.update(over)
    return facts


GOOD_CODE = {"kind": "code", "file": SRC, "line": 5, "rev": "head", "quote": "if (!members.ContainsKey(key))"}
GOOD_TEST = {"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "passed"}


def make_review(name, verdict="met", evidence=None, findings=(), refusals=()):
    return {"reviewer": name, "model": f"{name}-model", "vendor": name.title(), "prompt_version": "review-v1",
            "reviewed_at": "2026-11-14T03:00:00+02:00", "inputs": ["diff"],
            "requirement_verdicts": [{"req": "REQ-9001-F1", "verdict": verdict, "confidence_basis": "test passes",
                                      "evidence": evidence if evidence is not None else [GOOD_CODE, GOOD_TEST]}],
            "findings": list(findings), "refusals": list(refusals)}


@pytest.fixture
def ws(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    (repo / SRC).parent.mkdir(parents=True)
    (repo / SRC).write_text(BASE_CODE)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / SRC).write_text(HEAD_CODE)
    git(repo, "commit", "-qam", "fix")
    head = git(repo, "rev-parse", "HEAD")

    root = tmp_path / "root"
    shutil.copytree(ROOT / "mandate", root / "mandate", ignore=shutil.ignore_patterns("*.sig"))
    (root / "requirements").mkdir()
    (root / "requirements" / "9001.yaml").write_text(
        'change: "9001"\nrequirements:\n  - id: REQ-9001-F1\n    type: functional\n'
        '    text: "Duplicate keys must be reported without crashing the analyzer."\n')
    w = Workspace.at(root, repo=str(repo))
    w.base, w.head = base, head
    write_json(w.facts_path("9001"), make_facts(base=base, head=head))
    write_json(w.inputs / "reviews" / "9001" / "claude.json", make_review("claude"))
    write_json(w.inputs / "reviews" / "9001" / "codex.json", make_review("codex"))
    write_json(w.inputs / "reviews" / "9001" / "nemotron.json", make_review("nemotron"))
    for name in ("Toivo", "Rene"):
        keys.keygen(w, name)
    mandate.sign(w, "Toivo")
    return w
