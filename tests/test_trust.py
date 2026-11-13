from countersign import ledger, mandate, pack, trust
from countersign.cli import main

AREA = "generator-analyzer-core"


def run(ws, *args):
    return main([*args, "--root", str(ws.root), "--repo", ws.repo])


def state(ws):
    return trust.derive(mandate.load(ws), ledger.read(ws))[AREA]


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


def test_agreeing_spotchecks_restore_the_cap(ws):
    run(ws, "review", "9001", "-q")
    run(ws, "escape", "9001", "--as", "Toivo", "--kind", "incident")
    for i in range(3):
        assert state(ws)["probation"]
        run(ws, "review", "9001", "-q")
        run(ws, "spotcheck", "9001", "--as", "Toivo", "--result", "agree")
    s = state(ws)
    assert s["cap"] == "notify" and not s["probation"]
    assert pack.build(ws, "9001")["tier"] == "notify"


def test_disagreeing_spotcheck_tightens_and_resets_the_streak(ws):
    run(ws, "review", "9001", "-q")
    run(ws, "spotcheck", "9001", "--as", "Toivo", "--result", "disagree")
    s = state(ws)
    assert s["cap"] == "ask" and s["probation"] and s["streak"] == 0


def test_escape_on_a_human_signed_change_leaves_the_ai_cap(ws):
    ledger.append(ws, "escape", {"change": "9001", "kind": "revert", "tier": "ask", "ai_cleared": False, "areas": [AREA]}, "Toivo")
    s = state(ws)
    assert s["cap"] == "notify" and "AI cap unchanged" in s["history"][-1]
