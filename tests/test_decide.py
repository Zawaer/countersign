from conftest import GOOD_CODE, make_facts, make_review

from countersign import pack
from countersign.common import write_json


def set_reviews(ws, claude, codex):
    write_json(ws.inputs / "reviews" / "9001" / "claude.json", claude)
    write_json(ws.inputs / "reviews" / "9001" / "codex.json", codex)


def set_facts(ws, **over):
    write_json(ws.facts_path("9001"), make_facts(base=ws.base, head=ws.head, **over))


def clause(p):
    return p["requirements"][0]


def codes(p):
    return {r["code"] for r in clause(p)["reasons"]}


def test_both_reviewers_met_with_evidence_and_checks_pass_is_proven_and_cleared(ws):
    p = pack.build(ws, "9001")
    assert clause(p)["status"] == "proven"
    assert p["tier"] == "notify"  # generator-analyzer-core may be cleared at most to notify
    assert p["owner"] == "Toivo"


def test_disagreement_is_refused_and_routed_to_owner(ws):
    set_reviews(ws, make_review("claude"), make_review("codex", verdict="cannot_determine"))
    p = pack.build(ws, "9001")
    assert codes(p) == {"reviewers_disagree", "cannot_determine"}
    assert p["tier"] == "ask"
    assert any(w["source"] == "refused clause" for w in p["why"])


def test_met_without_verified_evidence_is_thin(ws):
    fake = [{"kind": "code", "file": GOOD_CODE["file"], "line": 5, "quote": "nothing like this"}]
    set_reviews(ws, make_review("claude"), make_review("codex", evidence=fake))
    assert codes(pack.build(ws, "9001")) == {"thin_evidence"}


def test_skipped_and_failed_checks_refuse_the_clause(ws):
    facts = make_facts(base=ws.base, head=ws.head)
    facts["checks"][0]["status"] = "skipped"  # build
    write_json(ws.facts_path("9001"), facts)
    p = pack.build(ws, "9001")
    assert "check_not_run" in codes(p)
    assert any(r["id"] == "mandated-check-missing" for r in p["rules_fired"])
    facts["checks"][0]["status"] = "fail"
    write_json(ws.facts_path("9001"), facts)
    p = pack.build(ws, "9001")
    assert "check_failed" in codes(p) and p["tier"] == "block"


def test_too_many_files_blocks_with_the_rule_cited(ws):
    facts = make_facts(base=ws.base, head=ws.head)
    facts["diff"]["files"] = 237
    write_json(ws.facts_path("9001"), facts)
    p = pack.build(ws, "9001")
    assert p["tier"] == "block"
    assert p["why"][0]["id"] == "split-large-change" and "237 files" in p["why"][0]["why"]


def test_public_api_change_and_source_without_tests_ask(ws):
    facts = make_facts(base=ws.base, head=ws.head)
    facts["checks"][4]["changed"] = True
    facts["diff"]["by_file"] = facts["diff"]["by_file"][:1]
    write_json(ws.facts_path("9001"), facts)
    fired = {r["id"] for r in pack.build(ws, "9001")["rules_fired"]}
    assert {"public-api-change", "source-without-tests"} <= fired


def test_unsigned_or_edited_mandate_removes_clearance(ws):
    ws.mandate_path.write_text(ws.mandate_path.read_text() + "\n# edited\n")
    p = pack.build(ws, "9001")
    assert p["tier"] == "ask"
    assert p["why"][0]["id"] == "mandate-not-signed" and "changed after it was signed" in p["why"][0]["why"]


def test_blocker_confirmed_by_both_reviewers_blocks(ws):
    blocker = {"id": "B", "title": "guard missing in other branch", "severity": "blocker", "category": "correctness",
               "claim": "c", "evidence": [GOOD_CODE]}
    set_reviews(ws, make_review("claude", findings=[blocker]), make_review("codex"))
    assert pack.build(ws, "9001")["tier"] == "ask"  # one reviewer: ask
    set_reviews(ws, make_review("claude", findings=[blocker]), make_review("codex", findings=[blocker]))
    p = pack.build(ws, "9001")
    assert p["tier"] == "block" and "confirmed by" in p["why"][0]["why"]


def test_unsupported_blocker_does_not_move_the_tier(ws):
    fake = {"id": "F", "title": "imaginary crash", "severity": "blocker", "category": "correctness", "claim": "c",
            "evidence": [{"kind": "test", "name": "CollectorTests.Imaginary", "outcome": "failed"}]}
    set_reviews(ws, make_review("claude"), make_review("codex", findings=[fake]))
    p = pack.build(ws, "9001")
    assert p["tier"] == "notify"
    assert [f["id"] for f in p["rejected_claims"]] == ["F"]
    assert any("rejected for lack of evidence" in r for r in p["residual_risk"])


def test_risk_score_is_the_sum_of_printed_factors(ws):
    risk = pack.build(ws, "9001")["risk"]
    assert risk["score"] == round(sum(f["points"] for f in risk["factors"]), 1)
    assert all(f["reason"] for f in risk["factors"])


def test_pack_is_deterministic_and_renders(ws):
    a, b = pack.build(ws, "9001"), pack.build(ws, "9001")
    assert a == b
    out = pack.write(ws, a)
    html = (out / "pack.html").read_text()
    assert "<script" not in html and "http" not in html.split("<main>")[0]
    assert "refused to decide" in (out / "pack.md").read_text()
