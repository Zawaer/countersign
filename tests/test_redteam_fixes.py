"""Fixes for red-team misses R1-R4, R7, S2/S3/S6/S7, G4 (docs/security/REDTEAM.md). R6 is in test_engine_rules.py.

Verified is not relevant: towards a requirement verdict, code counts only on a line the change touched and only if it
is real code; a test only if the change adds or edits it or the clause lists it; a check never on its own.
"""

import subprocess

from conftest import GOOD_CODE, GOOD_TEST, SRC, make_facts, make_review

from countersign import decide, mandate, sbom
from countersign.verify import Verifier, verify_review

REQ = "REQ-9001-F1"
REQS = {"requirements": [{"id": REQ, "type": "functional", "text": "Duplicate keys must be reported without crashing the analyzer."}]}


def verifier(ws, reqs=REQS, **over):
    return Verifier(ws.repo, make_facts(base=ws.base, head=ws.head, **over), reqs, line_tolerance=3)


def counted(v, evidence, req=REQ):
    out = verify_review({"reviewer": "claude", "requirement_verdicts": [{"req": req, "verdict": "met", "evidence": evidence}]}, v)
    return out["requirement_verdicts"][0]


# --- R1, R2: code evidence ----------------------------------------------------------------------

def test_a_quote_on_a_changed_line_counts(ws):
    r = verifier(ws).item(GOOD_CODE, REQ)
    assert r["verified"] and r["substantive"] and "context" not in r


def test_r1_punctuation_on_a_changed_line_verifies_but_does_not_count(ws):
    r = verifier(ws).item({"kind": "code", "file": SRC, "line": 6, "rev": "head", "quote": "{"}, REQ)
    assert r["verified"] and not r["substantive"] and "too short" in r["context"]


def test_r2_an_unchanged_line_is_context_only(ws):
    v = verifier(ws)
    for item in ({"kind": "code", "file": SRC, "line": 3, "rev": "head", "quote": "void Add(int key)"},
                 {"kind": "code", "file": SRC, "line": 3, "rev": "base", "quote": "void Add(int key)"}):
        r = v.item(item, REQ)
        assert r["verified"] and not r["substantive"] and "not a line this change touched" in r["context"], item
        assert "context only, not counted" in r["note"]
    assert counted(v, [{"kind": "code", "file": SRC, "line": 3, "rev": "base", "quote": "void Add(int key)"}])["substantive_count"] == 0


def test_a_finding_may_still_cite_an_unchanged_line(ws):
    """A finding only routes stricter ("this unchanged caller now breaks"), so it keeps the wider rule."""
    f = {"id": "X", "severity": "major", "title": "t", "claim": "c",
         "evidence": [{"kind": "code", "file": SRC, "line": 3, "rev": "head", "quote": "void Add(int key)"}]}
    out = verify_review(make_review("codex", findings=[f]), verifier(ws))
    assert out["findings"][0]["status"] == "verified"


def test_a_seeded_mutation_line_counts_as_changed(ws):
    v = verifier(ws, mutation={"file": SRC, "line": 3, "before": "void Add", "after": "void Put"})
    assert v.item({"kind": "code", "file": SRC, "line": 3, "rev": "head", "quote": "void Put(int key)"}, REQ)["substantive"]


# --- R3: checks ---------------------------------------------------------------------------------

def test_r3_a_check_alone_never_satisfies_the_minimum(ws):
    v = verifier(ws)
    alone = counted(v, [{"kind": "check", "id": "build", "status": "pass"}])
    assert alone["substantive_count"] == 0 and "never count on its own" in alone["evidence"][0]["context"]
    assert counted(v, [GOOD_CODE, {"kind": "check", "id": "build", "status": "pass"}])["substantive_count"] == 2


def test_a_check_the_clause_names_counts_on_its_own(ws):
    reqs = {"requirements": [{**REQS["requirements"][0], "checks": ["tests.fail_without_fix"]}]}
    assert counted(verifier(ws, reqs), [{"kind": "check", "id": "tests.fail_without_fix", "status": "pass"}])["substantive_count"] == 1


def test_a_docs_clause_counts_its_mandated_docs_check(ws):
    m = mandate.load(ws)
    facts = make_facts(base=ws.base, head=ws.head)
    facts["checks"].append({"id": "docs.anchors", "status": "pass", "summary": "anchors resolve"})
    for kind, want in (("docs", "proven"), ("functional", "refused")):
        reqs = {"requirements": [{"id": REQ, "type": kind, "text": "t"}]}
        v = Verifier(ws.repo, facts, reqs)
        reviews = {n: verify_review({"reviewer": n, "requirement_verdicts": [{"req": REQ, "verdict": "met", "evidence": [
            {"kind": "check", "id": "docs.anchors", "status": "pass"}]}]}, v) for n in ("claude", "codex")}
        c = decide.decide_clauses(reqs, reviews, facts, m, ["claude", "codex"])[0]
        codes = {r["code"] for r in c["reasons"]}
        assert ("thin_evidence" not in codes) == (want == "proven"), (kind, codes)


# --- R4: tests ----------------------------------------------------------------------------------

def test_r4_an_existing_unedited_test_does_not_count(ws):
    facts_tests = [{"name": "CollectorTests.DuplicateKeys", "outcome": "passed", "new": True},
                   {"name": "CollectorTests.Existing", "outcome": "passed", "new": False}]
    over = {"checks": [{"id": "tests.targeted", "status": "pass", "tests": facts_tests}]}
    v = verifier(ws, **over)
    r = v.item({"kind": "test", "name": "CollectorTests.Existing", "outcome": "passed"}, REQ)
    assert r["verified"] and not r["substantive"] and "not added or edited" in r["context"]
    assert v.item(GOOD_TEST, REQ)["substantive"]  # new in the run
    listed = {"requirements": [{**REQS["requirements"][0], "tests": ["CollectorTests.Existing"]}]}
    assert verifier(ws, listed, **over).item({"kind": "test", "name": "CollectorTests.Existing", "outcome": "passed"}, REQ)["substantive"]


def test_an_edited_existing_test_counts(tmp_path):
    repo = tmp_path / "r"
    path = "tests/T/FooTests.cs"
    (repo / "tests" / "T").mkdir(parents=True)
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()  # noqa: E731
    git("init", "-q")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    body = "public class FooTests\n{{\n    [Fact]\n    public void Edited()\n    {{\n        {a}\n    }}\n\n    [Fact]\n    public void Untouched()\n    {{\n        Assert.True(true);\n    }}\n}}\n"
    (repo / path).write_text(body.format(a="Assert.Equal(1, 1);"))
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    (repo / path).write_text(body.format(a="Assert.Equal(2, Run());"))
    git("commit", "-qam", "edit")
    head = git("rev-parse", "HEAD")
    tests = [{"name": f"FooTests.{n}", "outcome": "passed", "new": False} for n in ("Edited", "Untouched")]
    facts = {"base": base, "head": head, "diff": {"by_file": [{"path": path, "kind": "test", "ins": 1, "del": 1}]},
             "checks": [{"id": "tests.targeted", "status": "pass", "tests": tests}]}
    v = Verifier(str(repo), facts, REQS)
    assert v.edited_tests() == {"Edited"}
    assert v.item({"kind": "test", "name": "FooTests.Edited", "outcome": "passed"}, REQ)["substantive"]
    assert not v.item({"kind": "test", "name": "FooTests.Untouched", "outcome": "passed"}, REQ)["substantive"]


# --- R7: held_before ----------------------------------------------------------------------------

def _ev(*names):
    return {"evidence": [{"kind": "test", "name": n, "verified": True, "substantive": True} for n in names]}


FWF = {"checks": [{"id": "tests.fail_without_fix", "tests": [
    {"name": "A", "outcome": "passed", "new": True}, {"name": "B", "outcome": "failed", "new": True}]}]}


def test_r7_one_cited_test_failing_without_the_fix_does_not_hide_one_that_passes():
    held = decide.held_before({"id": "R"}, {"x": _ev("A", "B"), "y": _ev("A", "B")}, FWF)
    assert held is not None and held["tests"] == ["A"]


def test_held_before_uses_only_tests_every_reviewer_cited():
    assert decide.held_before({"id": "R"}, {"x": _ev("A", "B"), "y": _ev("B")}, FWF) is None


def test_held_before_on_clause_tests_ignores_reviewer_citations():
    assert decide.held_before({"id": "R", "tests": ["A"]}, {"x": _ev("B")}, FWF)["tests"] == ["A"]
    assert decide.held_before({"id": "R", "tests": ["A", "B"]}, {"x": _ev("A")}, FWF) is None


# --- S2, S3, S7: dependency signals -------------------------------------------------------------

def _rule(facts):
    return decide.RULES["deps_check_failed"]({"facts": facts}, None)


def test_deps_delta_fail_or_error_fires():
    for status in ("fail", "error"):
        hit, why = _rule({"checks": [{"id": "deps.delta", "status": status, "fail_reasons": ["src/Evil.csproj does not restore"],
                                      "build_inputs_changed": {}}], "diff": {"by_file": []}})
        assert hit and status in why and "Evil" in why
    assert not _rule({"checks": [{"id": "deps.delta", "status": "pass", "build_inputs_changed": {}}], "diff": {"by_file": []}})[0]


def test_new_dotnet_tool_or_msbuild_sdk_fires():
    for k, b, h in (("dotnet_tools", {"t:nbgv": "3.6"}, {"t:nbgv": "3.6", "t:evil": "1.0"}), ("msbuild_sdks", {}, {"Contoso.Sdk": "1.0.3"}),
                    ("sdk", "8.0.402", "9.0.100")):
        hit, why = _rule({"checks": [{"id": "deps.delta", "status": "pass", "build_inputs_changed": {k: {"base": b, "head": h}}}],
                          "diff": {"by_file": []}})
        assert hit and k in why, k


def test_without_deps_delta_the_file_list_decides():
    files = {"by_file": [{"path": ".config/dotnet-tools.json"}]}
    assert _rule({"checks": [], "diff": files})[0]
    assert not _rule({"checks": [], "diff": {"by_file": [{"path": "README.md"}]}})[0]
    # deps.delta ran and saw no build-input change: a global.json edit that pins nothing new doesn't fire
    assert not _rule({"checks": [{"id": "deps.delta", "status": "pass", "build_inputs_changed": {}}],
                      "diff": {"by_file": [{"path": "global.json"}]}})[0]


def test_the_mandate_has_the_dependency_rule(ws):
    assert any(r["when"] == "deps_check_failed" and r["tier"] == "ask" for r in mandate.load(ws)["rules"])


# --- I9, G2: unscannable content, hand-edited generated files -------------------------------------

def _scan(matches):
    return {"checks": [{"id": "injection_scan", "status": "fail", "matches": matches}], "diff": {"by_file": []}}


def test_unscannable_only_asks_and_keeps_reviewers_trusted():
    facts = _scan([{"pattern": "unscannable", "file": "a.bin", "text": "binary file"}])
    assert decide.RULES["injection_unscannable"]({"facts": facts}, None)[0]
    assert not decide.injection_found(facts)  # R-INJECT (block) and reviewers_untrusted are for planted text only
    mixed = _scan([{"pattern": "unscannable", "file": "a.bin"}, {"pattern": "address_ai", "file": "b.json", "text": "Note to AI"}])
    assert decide.injection_found(mixed) and not decide.RULES["injection_unscannable"]({"facts": mixed}, None)[0]


def test_generated_looking_file_classified_as_source_is_a_hand_edit():
    facts = {"diff": {"by_file": [{"path": "src/T/FormatterTemplate.cs", "kind": "source", "looks_generated": True},
                                  {"path": "tests/Shared/Hook.g.cs", "kind": "source"},
                                  {"path": "src/T/Other.g.cs", "kind": "generated"},
                                  {"path": "src/T/Collector.cs", "kind": "source"}]}}
    hit, why = decide.RULES["generated_hand_edited"]({"facts": facts}, None)
    assert hit and "FormatterTemplate.cs" in why and "Hook.g.cs" in why and "Other.g.cs" not in why and "Collector.cs" not in why


def test_the_mandate_routes_the_new_rules_at_ask(ws):
    rules = {r["when"]: r["tier"] for r in mandate.load(ws)["rules"]}
    assert rules["injection_unscannable"] == rules["generated_hand_edited"] == "ask" and rules["injection_found"] == "block"


# --- G4: size grows smoothly; S6: every configuration's graph ---------------------------------

def test_size_points_are_smooth_near_the_split_rule_and_unchanged_for_small_changes(ws):
    w = mandate.load(ws)["risk"]
    files = [decide.size_points(n, w["files"]) for n in range(1, 120)]
    assert all(b >= a for a, b in zip(files, files[1:])) and max(files) == w["files"]["cap"]
    assert abs(files[48] - files[50]) < 2                 # 49 files score close to 51: no cliff to stay under
    assert files[48] + decide.size_points(0.49, w["lines"]) >= w["thresholds"]["ask"]
    assert all(abs(files[n - 1] - n) <= 1.5 for n in range(1, 7))   # small changes: about a point a file, as in v5


def _graph(pkgs, direct):
    return {"projects": {"p/p.csproj": {"name": "p", "tfms": ["net9.0"], "direct": direct, "project_refs": [], "restored": True}},
            "packages": {k: {"sha512": None, "deps": {}, "direct_in": {"p/p.csproj"} if k[0] in direct else set(),
                             "in_projects": {"p/p.csproj"}} for k in pkgs},
            "vulnerabilities": {}}


def test_a_release_only_package_counts_and_says_where():
    common = ("Common", "1.0.0")
    base = sbom.merge_configurations({"Debug": _graph([common], {"Common": "1.0.0"}), "Release": _graph([common], {"Common": "1.0.0"})})
    head = sbom.merge_configurations({"Debug": _graph([common], {"Common": "1.0.0"}),
                                      "Release": _graph([common, ("SharpZipLib", "1.2.0")], {"Common": "1.0.0", "SharpZipLib": "1.2.0"})})
    d = sbom.delta(base, head, {}, {})
    assert d["status"] == "fail" and d["new_or_changed"] == ["SharpZipLib@1.2.0"]
    assert d["packages_added"][0]["configurations"] == ["Release"] and "Release only" in d["summary"]
    doc = sbom.cyclonedx(head, {}, name="t", sha="h", sdk="9")
    props = {c["name"]: c.get("properties", []) for c in doc["components"] if c["type"] == "library"}
    assert {"name": "countersign:configurations", "value": "Release"} in props["SharpZipLib"]
    assert not any(p["name"] == "countersign:configurations" for p in props["Common"])  # in every configuration: as before
