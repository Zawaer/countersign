from conftest import MODELS, make_review

from countersign import ledger, mandate, pack, trust
from countersign.cli import main
from countersign.common import write_json

AREA = "generator-analyzer-core"


def run(ws, *args):
    return main([*args, "--root", str(ws.root), "--repo", ws.repo])


def state(ws, area=AREA, reviewers=None):
    return trust.derive(mandate.load(ws), ledger.read(ws), reviewers)[area]


def spot(ws, result="agree", n=1, area=AREA):
    for _ in range(n):
        ledger.append(ws, "spotcheck", {"change": "9001", "result": result, "areas": [area], "ai_cleared": True}, "Toivo")


def test_escape_on_ai_cleared_change_withdraws_the_area_cap(ws):
    run(ws, "review", "9001", "-q")
    assert pack.build(ws, "9001")["tier"] == "notify"  # the AI cleared it
    run(ws, "escape", "9001", "--as", "Toivo", "--kind", "revert", "--note", "duplicate key crash in prod")
    s = state(ws)
    assert s["cap"] == "ask" and s["probation"]
    p = pack.build(ws, "9001")
    assert p["tier"] == "ask" and p["ai_recommendation"] == "notify"
    assert any(w["source"] == "trust cap" and "escape on 9001" in w["why"] for w in p["why"])
    assert state(ws)["history"][-1].startswith("ledger #2: escape on AI-cleared 9001")
    # the event records which reviewer versions it grades
    esc = ledger.read(ws)[-1]["payload"]
    assert {r["name"]: r["model"] for r in esc["reviewers"]} == MODELS


def test_climbing_back_needs_the_stage_row_agreeing_spotchecks_and_no_recent_escape(ws):
    run(ws, "review", "9001", "-q")
    run(ws, "escape", "9001", "--as", "Toivo", "--kind", "incident")
    need = trust.stages(mandate.load(ws))["notify"]
    spot(ws, n=need["agreeing_spotchecks"] - 1)
    assert state(ws)["cap"] == "ask"  # one short
    spot(ws)
    s = state(ws)
    assert s["cap"] == "ask" and "changes since the escape" in s["reason"]  # streak met, but the escape is too recent
    for _ in range(need["no_escapes_in_last"]):
        ledger.append(ws, "signoff", {"change": "x", "areas": [AREA], "decision": "accept"}, "Toivo")
    spot(ws)
    s = state(ws)
    assert s["cap"] == "notify" and not s["probation"]
    assert pack.build(ws, "9001")["tier"] == "notify"


def test_disagreeing_spotcheck_drops_one_stage_and_resets_the_streak(ws):
    run(ws, "review", "9001", "-q")
    run(ws, "spotcheck", "9001", "--as", "Toivo", "--result", "disagree")
    s = state(ws)
    assert s["cap"] == "ask" and s["probation"] and s["streak"] == 0


def test_agreement_rate_over_the_window_is_required_too(ws):
    spot(ws, "disagree", n=3)
    spot(ws, n=20)  # 20 in a row, but 3 of the last 23 spot-checks disagreed: 87% < 95%
    assert state(ws)["cap"] == "ask"
    spot(ws, n=18)  # the last 40 now hold 2 disagreements: 95%
    assert state(ws)["cap"] == "notify"


def test_one_escape_drops_one_stage_from_silent(ws):
    ledger.append(ws, "escape", {"change": "d", "kind": "revert", "ai_cleared": True, "areas": ["docs"]}, "Rene")
    assert state(ws, "docs")["cap"] == "notify"


def test_escape_on_a_human_signed_change_leaves_the_ai_cap(ws):
    ledger.append(ws, "escape", {"change": "9001", "kind": "revert", "tier": "ask", "ai_cleared": False, "areas": [AREA]}, "Toivo")
    s = state(ws)
    assert s["cap"] == "notify" and "AI cap unchanged" in s["history"][-1]


def test_a_canary_the_panel_misses_drops_a_stage(ws):
    run(ws, "canary", "--as", "Toivo", "--seeded", "14", "--caught", "13", "--missed", "2283-mut1", "--area", AREA)
    s = state(ws)
    assert s["cap"] == "ask" and "missed 1 of 14" in s["reason"]


def test_a_new_reviewer_version_restarts_at_ask_until_it_passes_the_seeded_set(ws):
    new = make_review("claude")
    new["model"] = "claude-opus-6"
    write_json(ws.inputs / "reviews" / "9001" / "claude.json", new)
    p = pack.build(ws, "9001")
    assert p["tier"] == "ask"
    assert any(w["source"] == "trust cap" and "claude-opus-6/review-v1 has not passed the seeded-defect set" in w["why"] for w in p["why"])
    # a canary run that misses one does not release it
    run(ws, "canary", "--as", "Toivo", "--seeded", "14", "--caught", "13", "--area", "docs", "--reviewer", "claude=claude-opus-6@review-v1")
    assert pack.build(ws, "9001")["tier"] == "ask"
    run(ws, "canary", "--as", "Toivo", "--seeded", "14", "--caught", "14", "--area", "docs", "--reviewer", "claude=claude-opus-6@review-v1")
    assert pack.build(ws, "9001")["tier"] == "notify"
    # a new prompt version is a new reviewer too
    new["prompt_version"] = "review-v9"
    write_json(ws.inputs / "reviews" / "9001" / "claude.json", new)
    assert pack.build(ws, "9001")["tier"] == "ask"


def test_trust_command_prints_the_stage_table(ws, capsys):
    run(ws, "trust")
    out = capsys.readouterr().out
    assert "notify" in out and "agreeing in a row" in out and "released reviewer versions" in out
