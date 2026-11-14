"""Per-finding acceptance: the owner's verdict on each verified finding is signed into the ledger, and the
measurement reads it back (never simulated; "no sign-offs yet" until an owner signs)."""

import json

import pytest

from countersign import github as gh_mod, ledger, measure, pack as pack_mod
from countersign.cli import main
from countersign.common import canonical, sha256_hex, write_json

from conftest import GOOD_CODE, make_review

MAJOR = {"id": "C1", "title": "other branch still adds duplicates", "severity": "major", "category": "correctness",
         "claim": "c", "evidence": [GOOD_CODE]}
MINOR = {"id": "C2", "title": "naming", "severity": "minor", "category": "style", "claim": "c", "evidence": [GOOD_CODE]}


@pytest.fixture
def ws_findings(ws):
    write_json(ws.inputs / "reviews" / "9001" / "claude.json", make_review("claude", findings=[MAJOR, MINOR]))
    write_json(ws.inputs / "reviews" / "9001" / "nemotron.json",
               make_review("nemotron", findings=[{**MINOR, "id": "N1", "title": "log message"}]))
    return ws


def _review(ws):
    assert main(["review", "9001", "-q", "--root", str(ws.root), "--repo", ws.repo]) == 0
    return json.loads((ws.pack_dir("9001") / "pack.json").read_text())


def _sign(ws, *extra, decision="request-changes"):
    return main(["sign", "9001", "--as", "Toivo", "--decision", decision, "--note", "n",
                 "--root", str(ws.root), "--repo", ws.repo, *extra])


def _signoff(ws):
    return [json.loads(x) for x in ws.ledger_path.read_text().splitlines()][-1]


def test_pack_lists_each_finding_with_its_flag_and_the_full_command(ws_findings):
    p = _review(ws_findings)
    s = p["signoff"]
    assert [r["ref"] for r in s["findings"]] == ["claude:C1", "claude:C2", "nemotron:N1"]
    assert s["findings"][0]["flag"] == "--finding claude:C1=<accepted|rejected|unsure>"
    assert s["command_with_findings"].startswith(s["command"] + " \\\n  --finding claude:C1=")
    md = (ws_findings.pack_dir("9001") / "pack.md").read_text()
    html = (ws_findings.pack_dir("9001") / "pack.html").read_text()
    assert s["command_with_findings"] in md and "--finding nemotron:N1=&lt;accepted|rejected|unsure&gt;" in html
    assert "--finding claude:C1=" in pack_mod.card(p)


def test_signing_records_verdicts_and_unrated(ws_findings, capsys):
    _review(ws_findings)
    assert _sign(ws_findings, "--finding", "claude:C1=accepted", "--finding", "nemotron:N1=rejected:wrong file: not touched") == 0
    fs = _signoff(ws_findings)["payload"]["findings"]
    assert [(f["ref"], f["verdict"], f["reason"]) for f in fs] == [
        ("claude:C1", "accepted", ""), ("claude:C2", "unrated", ""), ("nemotron:N1", "rejected", "wrong file: not touched")]
    assert fs[0]["reviewer"] == "claude" and fs[0]["severity"] == "major"
    assert "1 accepted, 1 rejected, 1 unrated" in capsys.readouterr().out
    assert ledger.verify(ws_findings) == ([], [])


def test_without_finding_flags_signing_is_unchanged_and_never_prompts(ws_findings, monkeypatch):
    _review(ws_findings)
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("prompted"))
    assert _sign(ws_findings) == 0
    pl = _signoff(ws_findings)["payload"]
    assert {f["verdict"] for f in pl["findings"]} == {"unrated"} and pl["decision"] == "request-changes"


@pytest.mark.parametrize("flag,why", [
    ("claude:C9=accepted", "not a verified finding"),
    ("claude:C1=maybe", "verdict must be one of"),
    ("claude:C1", "expected <reviewer:id>="),
])
def test_bad_flags_refuse_before_writing(ws_findings, flag, why):
    _review(ws_findings)
    before = ws_findings.ledger_path.read_text()
    with pytest.raises(SystemExit, match=why):
        _sign(ws_findings, "--finding", flag)
    with pytest.raises(SystemExit, match="given twice"):
        _sign(ws_findings, "--finding", "claude:C1=accepted", "--finding", "claude:C1=rejected")
    assert ws_findings.ledger_path.read_text() == before


def test_editing_a_verdict_is_detected_even_with_a_recomputed_hash(ws_findings):
    _review(ws_findings)
    _sign(ws_findings, "--finding", "claude:C1=rejected")
    ls = ws_findings.ledger_path.read_text().splitlines()
    e = json.loads(ls[-1])
    e["payload"]["findings"][0]["verdict"] = "accepted"
    ls[-1] = json.dumps(e)
    ws_findings.ledger_path.write_text("\n".join(ls) + "\n")
    assert any("edited after it was written" in p for p in ledger.verify(ws_findings)[0])
    e["hash"] = ledger.entry_hash(e)
    ls[-1] = json.dumps(e)
    ws_findings.ledger_path.write_text("\n".join(ls) + "\n")
    assert any("signature does not verify" in p for p in ledger.verify(ws_findings)[0])


def test_sign_pr_entry_carries_verdicts_and_ci_checks_them(ws_findings):
    p = pack_mod.build(ws_findings, "9001")
    key = (ws_findings.private_keys / "toivo.key").read_text()
    rated = pack_mod.rate_findings(p, ["claude:C1=accepted"])
    e = gh_mod.make_entry(ws_findings, p, "Toivo", "accept", "ok", key, findings=rated)
    sha = sha256_hex(canonical(p))
    assert gh_mod.verify_signed_entry(e, ws_findings, p, sha, "accept", "ok") == []
    assert [f["verdict"] for f in e["payload"]["findings"]] == ["accepted", "unrated", "unrated"]
    dropped = gh_mod.make_entry(ws_findings, p, "Toivo", "accept", "ok", key, findings=rated[:1])
    assert any("payload.findings names" in x for x in gh_mod.verify_signed_entry(dropped, ws_findings, p, sha, "accept", "ok"))


def _entry(change, tier, decision, findings):
    return {"type": "signoff", "payload": {"change": change, "tier": tier, "decision": decision, "findings": findings}}


def _f(ref, verdict, reason=""):
    return {"ref": ref, "reviewer": ref.split(":")[0], "severity": "major", "verdict": verdict, "reason": reason}


def test_metrics_say_no_signoffs_yet_instead_of_zero():
    m = measure.signoff_metrics([{"type": "mandate_change", "payload": {}}])
    assert m["signoffs"] == 0 and m["findings_accepted_rate"] is None and m["tier_overrides"] is None
    assert measure._signoff_text("findings_accepted_rate", None) == "no sign-offs yet"


def test_metrics_from_a_fixture_ledger(ws_findings):
    # a fixture ledger in the temp workspace, written with the real append (signed), not the repo's ledger/
    for pl in (
        _entry("a", "ask", "request-changes", [_f("claude:C1", "accepted"), _f("nemotron:N1", "rejected", "not reachable")]),
        _entry("b", "ask", "accept", [_f("claude:C1", "accepted"), _f("claude:C2", "unsure"), _f("nemotron:N2", "unrated")]),
        _entry("c", "notify", "request-changes", [_f("claude:C1", "rejected")]),
        _entry("c", "notify", "accept", [_f("claude:C1", "accepted")]),  # re-sign replaces the earlier judgement
        {"type": "signoff", "payload": {"change": "d", "tier": "block", "decision": "reject"}},  # signed before verdicts existed
    ):
        ledger.append(ws_findings, "signoff", pl["payload"], "Toivo")
    assert ledger.verify(ws_findings)[0] == []
    m = measure.signoff_metrics(ledger.read(ws_findings))
    assert m["signoffs"] == 4 and m["simulated"] is False
    assert m["findings_rated"] == {"rated": 5, "of": 6, "unrated": 1, "signoffs_before_finding_verdicts": ["d"]}
    assert m["findings_accepted_rate"]["claude"] == {"accepted": 3, "rejected": 0, "unsure": 1, "unrated": 0,
                                                    "rated": 4, "accepted_rate": 0.75}
    assert m["findings_accepted_rate"]["nemotron"]["accepted_rate"] == 0.0
    assert m["findings_rejected"] == [{"change": "a", "ref": "nemotron:N1", "severity": "major", "reason": "not reachable"}]
    t = m["tier_overrides"]
    assert t["accepted_when_routed_to_human"] == ["b"] and t["held_back_when_ai_cleared"] == []
    assert t["overrode"] == 1 and t["of"] == 4 and t["by_tier"]["ask"] == {"request-changes": 1, "accept": 1}
    assert "claude: 3 of 4 accepted (75%)" in measure._signoff_text("findings_accepted_rate", m["findings_accepted_rate"])
