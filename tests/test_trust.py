from conftest import MODELS, make_review

from countersign import ledger, mandate, pack, trust
from countersign.cli import main
from countersign.common import write_json

AREA = "generator-analyzer-core"


def run(ws, *args):
    return main([*args, "--root", str(ws.root), "--repo", ws.repo])


def state(ws, area=AREA, reviewers=None):
    return trust.derive(mandate.load(ws), ledger.read(ws), reviewers)[area]


def spot(ws, result="agree", n=1, area=AREA, signer="Toivo"):
    """n spot-checks of n distinct packs by the area owner (a spot-check counts once per pack, red team L3)."""
    for _ in range(n):
        k = len(ledger.read(ws))
        ledger.append(ws, "spotcheck", {"change": f"c{k}", "pack_sha256": f"{k:064x}", "result": result, "areas": [area],
                                        "ai_cleared": True}, signer)


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


# --- red team fixes (docs/security/REDTEAM.md G1, G3, L1-L3; mandate v5) ----------------------------------------

def test_build_inputs_ci_and_security_tests_are_areas_capped_at_ask(ws):
    m = mandate.load(ws)
    want = {"src/Directory.Build.props": "build-config",  # G1: not runtime-core, tests or the generator
            "src/MessagePack.SourceGenerator/Directory.Build.props": "build-config",
            "tests/Shared/Directory.Build.targets": "build-config", "src/Directory.Packages.props": "build-config",
            "global.json": "build-config", "nuget.config": "build-config", ".config/dotnet-tools.json": "build-config",
            ".github/workflows/build.yml": "ci",  # G3
            "tests/MessagePack.Tests/MessagePackSecurityTests.cs": "security-tests",
            "src/MessagePack/MessagePack.csproj": "runtime-core", "tests/MessagePack.Tests/Foo.cs": "tests"}
    assert {p: m.area_for(p).name for p in want} == want
    assert {n: (m.area(n).max_ai_tier, m.area(n).owner) for n in ("build-config", "ci", "security-tests")} == {
        "build-config": ("ask", "Rene"), "ci": ("ask", "Toivo"), "security-tests": ("ask", "Toivo")}
    assert mandate.matches("tests/MessagePack.Tests/MessagePackSecurityTests.cs", m["security_sensitive_paths"])


def test_an_invalid_ledger_puts_every_area_at_ask_with_the_reason(ws):
    run(ws, "review", "9001", "-q")
    assert pack.build(ws, "9001")["tier"] == "notify"
    with ws.ledger_path.open("a") as f:  # L1: an unsigned, unchained line
        f.write('{"seq": 99, "type": "canary", "prev": "x", "signer": "Toivo", "hash": "x", "sig": "x", "payload": {}}\n')
    p = pack.build(ws, "9001")
    assert p["tier"] == "ask"
    assert any(w["source"] == "trust cap" and "ledger invalid: line 2" in w["why"] for w in p["why"])
    assert {a["cap"] for a in p["areas"]} == {"ask"}
    assert pack.build(ws, "9001", use_trust=False)["tier"] == "notify"  # replay ignores the ledger altogether


def _new_model(ws):
    new = make_review("claude")
    new["model"] = "claude-opus-6"
    write_json(ws.inputs / "reviews" / "9001" / "claude.json", new)


def test_a_canary_releases_only_if_it_covers_the_whole_seeded_set(ws, capsys):
    _new_model(ws)
    rel = [{"name": "claude", "model": "claude-opus-6", "prompt_version": "review-v1"}]
    ledger.append(ws, "canary", {"areas": [], "seeded": 1, "caught": 1, "reviewers": rel}, "Toivo")  # L2
    some = trust.seeded_set(mandate.load(ws))[:13]
    ledger.append(ws, "canary", {"areas": [], "seeded": 14, "caught": 14, "defects": some, "reviewers": rel}, "Toivo")
    assert pack.build(ws, "9001")["tier"] == "ask"
    run(ws, "trust")
    out = capsys.readouterr().out
    assert "covers 0 of the 14 seeded defects" in out and "covers 13 of the 14" in out
    full = trust.seeded_set(mandate.load(ws))
    ledger.append(ws, "canary", {"areas": [], "seeded": 14, "caught": 13, "missed": [full[0]], "defects": full, "reviewers": rel}, "Toivo")
    assert pack.build(ws, "9001")["tier"] == "ask"  # below min_catch_rate
    run(ws, "canary", "--as", "Toivo", "--seeded", "14", "--caught", "14", "--area", "docs", "--reviewer", "claude=claude-opus-6@review-v1")
    assert ledger.read(ws)[-1]["payload"]["defects"] == full
    assert pack.build(ws, "9001")["tier"] == "notify"


def test_canary_command_refuses_a_set_size_it_does_not_list(ws):
    import pytest
    with pytest.raises(SystemExit):
        run(ws, "canary", "--as", "Toivo", "--seeded", "1", "--caught", "1")


def test_spotchecks_count_once_per_pack_and_only_from_the_area_owner(ws):
    ledger.append(ws, "escape", {"change": "x", "kind": "revert", "ai_cleared": True, "areas": [AREA]}, "Toivo")
    for _ in range(50):  # L3: one pack, replayed by a non-owner
        ledger.append(ws, "spotcheck", {"change": "x", "pack_sha256": "same", "result": "agree", "areas": [AREA]}, "Rene")
    s = state(ws)
    assert s["cap"] == "ask" and s["streak"] == 0 and "Rene is not the owner of generator-analyzer-core" in s["history"][-1]
    for _ in range(3):  # the owner, same pack three times: one spot-check
        ledger.append(ws, "spotcheck", {"change": "x", "pack_sha256": "same", "result": "agree", "areas": [AREA]}, "Toivo")
    s = state(ws)
    assert s["streak"] == 1 and "already spot-checked" in s["history"][-1]
    ledger.append(ws, "spotcheck", {"change": "y", "result": "agree", "areas": [AREA]}, "Toivo")
    assert "names no pack" in state(ws)["history"][-1]
