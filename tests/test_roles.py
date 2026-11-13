"""Reviewer roles: the registry, confidentiality, the 3-reviewer proven rule, and the adjudicator that can never clear."""

from conftest import make_review

from countersign import mandate, pack
from countersign.common import write_json


def reviews_dir(ws):
    return ws.inputs / "reviews" / "9001"


def make_confidential(ws, area="generator-analyzer-core"):
    text = ws.mandate_path.read_text()
    marker = f"  {area}:\n"
    assert marker in text
    ws.mandate_path.write_text(text.replace(marker, marker + "    confidential: true\n", 1))
    mandate.sign(ws, "Toivo")  # the owner re-signs the edited mandate


def test_open_source_repo_uses_all_three_reviewers_and_gemini_as_adjudicator(ws):
    p = pack.build(ws, "9001")
    assert p["reviewer_panel"]["confidential"] is False
    assert p["reviewer_panel"]["reviewers"] == ["claude", "codex", "nemotron"]
    assert p["reviewer_panel"]["adjudicator"] == "gemini"
    assert p["requirements"][0]["status"] == "proven"


def test_proven_needs_every_participating_reviewer(ws):
    (reviews_dir(ws) / "nemotron.json").unlink()
    c = pack.build(ws, "9001")["requirements"][0]
    assert c["status"] == "refused" and [r["code"] for r in c["reasons"]] == ["missing_review"]
    write_json(reviews_dir(ws) / "nemotron.json", make_review("nemotron", verdict="not_met"))
    c = pack.build(ws, "9001")["requirements"][0]
    assert {"not_met", "reviewers_disagree"} <= {r["code"] for r in c["reasons"]}


def test_confidential_area_excludes_claude_codex_and_gemini(ws):
    make_confidential(ws)
    # Claude and Codex reviews exist and even disagree; in a confidential area they must not count at all.
    write_json(reviews_dir(ws) / "codex.json", make_review("codex", verdict="not_met"))
    p = pack.build(ws, "9001")
    panel = p["reviewer_panel"]
    assert panel["confidential"] is True and "generator-analyzer-core" in panel["why"]
    assert panel["reviewers"] == ["nemotron"]
    assert panel["adjudicator"] is None
    assert {x["name"] for x in panel["excluded"]} == {"claude", "codex", "gemini"}
    assert {x["name"] for x in panel["ignored_files"]} == {"claude", "codex"}
    clause = p["requirements"][0]
    assert set(clause["verdicts"]) == {"nemotron"} and clause["status"] == "proven"
    assert [r["reviewer"] for r in p["checked_by"]["reviewers"]] == ["nemotron"]
    assert any("did not read this change" in r and "claude" in r for r in p["residual_risk"])
    assert "Excluded **gemini**" in pack.to_markdown(p)


def test_an_area_can_stay_open_inside_a_confidential_repo(ws):
    text = ws.mandate_path.read_text().replace("\nconfidential: false\n", "\nconfidential: true\n", 1)
    text = text.replace("  generator-analyzer-core:\n", "  generator-analyzer-core:\n    confidential: false\n", 1)
    text = text.replace("  tests:\n", "  tests:\n    confidential: false\n", 1)
    ws.mandate_path.write_text(text)
    mandate.sign(ws, "Toivo")
    assert pack.build(ws, "9001")["reviewer_panel"]["confidential"] is False


# --- the adjudicator ------------------------------------------------------------------------------

def overreaching_ruling(dispute):
    """An adjudicator output that tries everything to clear the clause."""
    return {"reviewer": "gemini", "model": "gemini-test", "vendor": "Google", "prompt_version": "adjudicate-v1",
            "reviewed_at": "2026-11-14T04:00:00+02:00", "status": "proven", "verdict": "met",
            "rulings": [{"dispute": dispute, "verdict": "met", "status": "proven", "clear": True,
                         "supported": [{"reviewer": "claude", "claim": "met", "why": "the guard is there"},
                                       {"reviewer": "codex", "claim": "cannot_determine", "why": "fine"}],
                         "unsupported": [], "evidence_that_would_settle": []}]}


def test_adjudicator_can_never_turn_a_refused_clause_into_proven(ws):
    write_json(reviews_dir(ws) / "codex.json", make_review("codex", verdict="cannot_determine"))
    before = pack.build(ws, "9001")
    assert before["requirements"][0]["status"] == "refused"
    assert [d["id"] for d in before["disputes"]] == ["REQ-9001-F1"]
    write_json(reviews_dir(ws) / "adjudication.gemini.json", overreaching_ruling("REQ-9001-F1"))
    after = pack.build(ws, "9001")
    clause = after["requirements"][0]
    assert clause["status"] == "refused"
    assert "adjudicator_dispute" in {r["code"] for r in clause["reasons"]}
    assert clause["adjudication"]["dispute"] == "REQ-9001-F1"
    assert after["tier"] == before["tier"] == "ask"
    assert any(w["source"] == "adjudicator" for w in after["drivers"])
    assert after["adjudication"]["rulings"][0]["stale"] is False
    assert "inputs" in after and "adjudication" in after["inputs"]


def test_adjudicator_ruling_on_a_proven_clause_only_adds_a_reason(ws):
    # Not a live dispute (everyone said met): the ruling is kept as stale and changes nothing.
    write_json(reviews_dir(ws) / "adjudication.gemini.json", overreaching_ruling("REQ-9001-F1"))
    p = pack.build(ws, "9001")
    assert p["requirements"][0]["status"] == "proven" and p["tier"] == "notify"
    assert p["adjudication"]["rulings"][0]["stale"] is True


def test_adjudication_by_a_non_adjudicator_is_ignored(ws):
    write_json(reviews_dir(ws) / "codex.json", make_review("codex", verdict="cannot_determine"))
    write_json(reviews_dir(ws) / "adjudication.claude.json", {**overreaching_ruling("REQ-9001-F1"), "reviewer": "claude"})
    p = pack.build(ws, "9001")
    assert p["adjudication"] is None
    assert any("not the adjudicator" in x["reason"] for x in p["reviewer_panel"]["ignored_files"])
