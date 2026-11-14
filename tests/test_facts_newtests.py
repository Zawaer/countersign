"""Stage 1 (evidence/scripts/facts.py): new-test detection when test classes live in a namespace.

TRX names are fully qualified (Ns.Class.Method(args)) for a class declared in a namespace, while new_tests() records
Class.Method from the diff. method_of used to keep the namespace, so such tests never counted as new and
tests.fail_without_fix reported "0/0 failed -> fail" (the var-2283-v2..v4 variants hit this).
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS = "tests/MessagePack.SourceGenerator.Tests"

OLD_GLOBAL = """public class OldTests
{
    [Fact]
    public void Existing() { }
}
"""
OLD_NS = """namespace MessagePack.SourceGenerator.Tests;

public class OldNsTests
{
    [Fact]
    public void Existing() { }
}
"""
NEW_FILE_SCOPED = """using Xunit;

namespace MessagePack.SourceGenerator.Tests;

public class FileScopedTests
{
    [Fact]
    public async Task Added() { }

    [Theory]
    [InlineData(1.5)]
    public void AddedTheory(double x) { }
}
"""
NEW_BLOCK = """namespace MessagePack.SourceGenerator.Tests.Nested
{
    public sealed class BlockTests
    {
        [Fact]
        public void Added() { }
    }
}
"""


def _facts_module():
    spec = importlib.util.spec_from_file_location("cs_facts_newtests", ROOT / "evidence" / "scripts" / "facts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()


def _trx(results):
    rows = "".join(f'<UnitTestResult testName="{n}" outcome="{o}" duration="00:00:00.01" />' for n, o in results)
    return ('<?xml version="1.0" encoding="utf-8"?><TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">'
            f"<Results>{rows}</Results></TestRun>")


@pytest.fixture
def stage1(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    for p, c in {f"{TESTS}/OldTests.cs": OLD_GLOBAL, f"{TESTS}/OldNsTests.cs": OLD_NS}.items():
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
        (repo / p).write_text(c)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    F = _facts_module()
    F.REPO, F.BASE, F.OUT, F.EVID = str(repo), _git(repo, "rev-parse", "HEAD"), str(tmp_path / "out"), str(tmp_path / "evidence")
    for p, c in {f"{TESTS}/FileScopedTests.cs": NEW_FILE_SCOPED, f"{TESTS}/BlockTests.cs": NEW_BLOCK}.items():
        (repo / p).write_text(c)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add tests")
    return F, _git(repo, "rev-parse", "HEAD"), tmp_path


@pytest.mark.parametrize("name,expected", [
    ("OldTests.Existing", "OldTests.Existing"),
    ("MessagePack.SourceGenerator.Tests.FileScopedTests.Added", "FileScopedTests.Added"),
    ('MessagePack.SourceGenerator.Tests.FileScopedTests.AddedTheory(x: 1.5, s: "a.b")', "FileScopedTests.AddedTheory"),
    ("A.B.C.BlockTests.Added", "BlockTests.Added"),
    ("Ns.C.M<Ns.T>(x: 1)", "C.M<Ns.T>"),
])
def test_method_of_drops_namespace_and_arguments(name, expected):
    assert _facts_module().method_of(name) == expected


def test_new_tests_in_file_scoped_and_block_namespaces(stage1):
    F, head, _ = stage1
    assert F.new_tests(head) == {"FileScopedTests.Added", "FileScopedTests.AddedTheory", "BlockTests.Added"}


def test_fully_qualified_trx_names_count_as_new(stage1):
    F, head, tmp = stage1
    run = tmp / "out" / "x-fwf"
    run.mkdir(parents=True)
    (run / "meta.txt").write_text("build_rc=0 targeted_1_rc=1 targeted_1_s=1.0\n")
    (run / "targeted.1.trx").write_text(_trx([
        ("MessagePack.SourceGenerator.Tests.FileScopedTests.Added", "Failed"),
        ("MessagePack.SourceGenerator.Tests.FileScopedTests.AddedTheory(x: 1.5)", "Failed"),
        ("MessagePack.SourceGenerator.Tests.Nested.BlockTests.Added", "Passed"),
        ("MessagePack.SourceGenerator.Tests.OldNsTests.Existing", "Passed"),
        ("OldTests.Existing", "Passed"),
    ]))
    newset = F.new_tests(head)
    c = F.targeted_check("x-fwf", str(tmp / "evidence" / "x"), F.read_meta("x-fwf"), newset, id_="tests.fail_without_fix")
    new = {t["name"]: t["new"] for t in c["tests"]}
    assert new == {
        "MessagePack.SourceGenerator.Tests.FileScopedTests.Added": True,
        "MessagePack.SourceGenerator.Tests.FileScopedTests.AddedTheory(x: 1.5)": True,
        "MessagePack.SourceGenerator.Tests.Nested.BlockTests.Added": True,
        "MessagePack.SourceGenerator.Tests.OldNsTests.Existing": False,
        "OldTests.Existing": False,
    }
    assert c["summary"] == "3 passed, 2 failed, 0 skipped (3 new tests in run)"
