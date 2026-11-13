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
    assert "no cited evidence could be verified" in out["findings"][0]["rejection_reason"]


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
