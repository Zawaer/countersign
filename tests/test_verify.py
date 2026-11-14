from conftest import GOOD_CODE, SRC, make_facts, make_review

from countersign.verify import Verifier, verify_review

REQS = {"requirements": [{"id": "REQ-9001-F1", "text": "Duplicate keys must be reported without crashing the analyzer."}]}


def verifier(ws):
    return Verifier(ws.repo, make_facts(base=ws.base, head=ws.head), REQS, line_tolerance=3)


def test_code_quote_on_cited_line_is_verified(ws):
    r = verifier(ws).item(GOOD_CODE)
    assert r["verified"] and "quote matches" in r["note"]


def test_code_quote_within_tolerance_records_offset(ws):
    r = verifier(ws).item({**GOOD_CODE, "line": 7})
    assert r["verified"] and "2 off" in r["note"]


def test_code_quote_outside_tolerance_is_rejected(ws):
    r = verifier(ws).item({**GOOD_CODE, "line": 40})
    assert not r["verified"] and "outside tolerance" in r["note"]


def test_code_quote_that_does_not_exist_at_that_rev_is_rejected(ws):
    # The guard only exists at head; citing it at base is a hallucination.
    r = verifier(ws).item({**GOOD_CODE, "rev": "base"})
    assert not r["verified"] and "not found anywhere" in r["note"]


def test_missing_file_is_rejected(ws):
    assert not verifier(ws).item({**GOOD_CODE, "file": "src/Nope.cs"})["verified"]


def test_test_and_check_items_must_match_facts(ws):
    v = verifier(ws)
    assert v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "passed"})["verified"]
    assert not v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "failed"})["verified"]
    assert not v.item({"kind": "test", "name": "CollectorTests.Imaginary"})["verified"]
    assert v.item({"kind": "check", "id": "tests.fail_without_fix"})["verified"]
    assert not v.item({"kind": "check", "id": "tests.fuzz"})["verified"]


def test_requirement_quotes_must_occur_in_the_clause(ws):
    v = verifier(ws)
    assert v.item({"kind": "requirement", "req": "REQ-9001-F1", "quote": "without crashing the analyzer"})["verified"]
    assert not v.item({"kind": "requirement", "req": "REQ-9001-F1", "quote": "must be fast"})["verified"]


def test_issue_links_are_not_counted_as_evidence(ws):
    assert not verifier(ws).item({"kind": "issue", "url": "https://example.com/1", "quote": "x"})["verified"]


def test_finding_without_verified_evidence_is_rejected_but_kept(ws):
    review = make_review("codex", findings=[
        {"id": "X1", "title": "made up", "severity": "blocker", "category": "correctness", "claim": "c",
         "evidence": [{"kind": "code", "file": SRC, "line": 5, "quote": "throw new Exception()"}]},
        {"id": "X2", "title": "real", "severity": "minor", "category": "correctness", "claim": "c", "evidence": [GOOD_CODE]},
    ])
    out = verify_review(review, verifier(ws))
    status = {f["id"]: f["status"] for f in out["findings"]}
    assert status == {"X1": "rejected", "X2": "verified"}
    assert "no cited evidence about the change could be verified" in out["findings"][0]["rejection_reason"]


def test_test_evidence_matches_the_head_run_not_the_fail_without_fix_run(ws):
    facts = make_facts(base=ws.base, head=ws.head)
    # the same test, run again with the source reverted: it fails there by design (listed first on purpose)
    fwf = next(c for c in facts["checks"] if c["id"] == "tests.fail_without_fix")
    fwf["tests"] = [{"name": "CollectorTests.DuplicateKeys", "outcome": "failed", "new": True}]
    facts["checks"].insert(0, facts["checks"].pop(facts["checks"].index(fwf)))
    v = Verifier(ws.repo, facts, REQS)
    ok = v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "passed"})
    assert ok["verified"] and "tests.targeted" in ok["note"]
    # "failed" without pinning the run: only the reverted run failed, so it is not verified, and the note says why
    bad = v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "failed"})
    assert not bad["verified"] and "tests.fail_without_fix" in bad["note"]
    # pinned to the fail_without_fix run, the failure is legitimate evidence
    pinned = v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "failed", "check": "tests.fail_without_fix"})
    assert pinned["verified"]
    assert not v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "check": "tests.full_suite"})["verified"]


# --- R7: review JSON is untrusted model output (docs/security/TRIAGE.md T2, C2, T3, C3) ----------------------------

def test_trivially_true_evidence_verifies_but_is_not_substantive(ws):
    v = verifier(ws)
    for item in ({"kind": "requirement", "req": "REQ-9001-F1"},
                 {"kind": "check", "id": "tests.fail_without_fix"},  # no claimed status
                 {"kind": "test", "name": "CollectorTests.DuplicateKeys"}):  # no claimed outcome
        r = v.item(item)
        assert r["verified"] and not r["substantive"], item
    assert v.item({"kind": "check", "id": "tests.fail_without_fix", "status": "pass"})["substantive"]
    assert v.item({"kind": "test", "name": "CollectorTests.DuplicateKeys", "outcome": "passed"})["substantive"]
    assert v.item(GOOD_CODE)["substantive"]


def test_met_citing_only_the_requirement_is_thin_not_proven(ws):
    from countersign import pack
    from countersign.common import write_json
    req_only = [{"kind": "requirement", "req": "REQ-9001-F1", "quote": "without crashing the analyzer"},
                {"kind": "check", "id": "build"}]
    for n in ("claude", "codex", "nemotron"):
        write_json(ws.inputs / "reviews" / "9001" / f"{n}.json", make_review(n, evidence=req_only))
    c = pack.build(ws, "9001")["requirements"][0]
    assert c["status"] == "refused" and {r["code"] for r in c["reasons"]} == {"thin_evidence"}


def test_a_finding_needs_substantive_evidence(ws):
    out = verify_review(make_review("codex", findings=[{"id": "Q", "title": "t", "severity": "blocker", "claim": "c",
                                                        "evidence": [{"kind": "requirement", "req": "REQ-9001-F1"}]}]), verifier(ws))
    assert out["findings"][0]["status"] == "rejected"


def test_rev_is_never_passed_to_git_as_an_option(ws, tmp_path):
    target = tmp_path / "pwned"
    r = verifier(ws).item({**GOOD_CODE, "rev": f"--output={target}", "file": "/x"})
    assert not r["verified"] and "head or base" in r["note"]
    assert not list(tmp_path.glob("pwned*"))
    v = verifier(ws)
    v.facts = {**v.facts, "head": f"--output={target}"}  # even a hostile facts value is refused
    assert not v.item(GOOD_CODE)["verified"] and not list(tmp_path.glob("pwned*"))


def test_code_evidence_must_be_a_relative_path_in_the_change(ws):
    v = verifier(ws)
    for bad in ("/etc/passwd", "../outside.cs", "src/../../x.cs", "-p", "README.md"):
        r = v.item({**GOOD_CODE, "file": bad})
        assert not r["verified"], bad
    assert not v.item({**GOOD_CODE, "rev": "HEAD~1"})["verified"]
    ctx = Verifier(ws.repo, make_facts(base=ws.base, head=ws.head), REQS, 3, base_context_files=["src/Other.cs"])
    assert "not in the change's diff" not in ctx.item({**GOOD_CODE, "rev": "base", "file": "src/Other.cs"})["note"]


def test_malformed_items_are_rejected_not_crashing(ws):
    v = verifier(ws)
    for bad in ({**GOOD_CODE, "line": "abc"}, {**GOOD_CODE, "quote": ["x"]}, {**GOOD_CODE, "line": None},
                {"kind": "test", "name": ["x"]}, {"kind": "requirement", "req": "REQ-9001-F1", "quote": 5}, "just a string", None):
        r = v.item(bad)
        assert r["verified"] is False and r["substantive"] is False, bad
    out = verify_review({"reviewer": "x", "requirement_verdicts": "nope", "findings": [None, {"evidence": 3}]}, v)
    assert out["requirement_verdicts"] == [] and out["findings"][0]["status"] == "rejected"


def test_duplicate_verdicts_for_one_clause_count_as_none(ws):
    from countersign import pack
    from countersign.common import write_json
    r = make_review("codex")
    r["requirement_verdicts"].append({**r["requirement_verdicts"][0], "verdict": "not_met"})
    r["requirement_verdicts"].reverse()  # `met` would win under first-wins either way round
    write_json(ws.inputs / "reviews" / "9001" / "codex.json", r)
    c = pack.build(ws, "9001")["requirements"][0]
    assert c["status"] == "refused" and "codex" not in c["verdicts"]
    assert any(x["code"] == "missing_review" and x.get("duplicate") == 2 for x in c["reasons"])
