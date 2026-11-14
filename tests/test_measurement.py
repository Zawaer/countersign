"""Measurement modules: the simulation is labelled and reproducible; history file kinds match facts.py's rules."""

from pathlib import Path

from countersign import history, simulate
from countersign.common import Workspace

ROOT = Path(__file__).resolve().parent.parent


def test_simulation_is_labelled_and_reproducible():
    ws = Workspace.at(ROOT)
    cfg = {"weeks": 10, "replicates": 3, "drift": {"week": 5, "panel_miss": 1.0}}
    a, b = simulate.simulate(ws, cfg), simulate.simulate(ws, cfg)
    assert a["simulated"] is True and a["summary"]["simulated"] is True
    assert a["scenarios"] == b["scenarios"]
    assert all(w["minutes"] == a["scenarios"]["full-human-review"][0]["minutes"] for w in a["scenarios"]["full-human-review"])
    assert "simulated" in simulate.chart_html(a).lower()


def test_history_file_kinds():
    tt = {"src/X/Template.tt"}
    assert history.kind("src/X/Template.cs", tt) == "generated"
    assert history.kind("src/X/Foo.g.cs", set()) == "generated"
    assert history.kind("tests/A/B.cs", set()) == "test"
    assert history.kind("src/MessagePack/PublicAPI.Unshipped.txt", set()) == "build"
    assert history.kind("doc/x.md", set()) == "doc"
    assert history.kind("src/MessagePack/Foo.cs", set()) == "source"


# --- seeded defects: inherited fail-without-fix, planted-line attribution ------------------------------------

from countersign import measure  # noqa: E402
from countersign.common import read_json  # noqa: E402


def _pack(findings=(), verdicts=None, mutation=None):
    return {"mutation": mutation or {"file": "src/A.cs", "line": 100},
            "checked_by": {"reviewers": [{"reviewer": "r1"}, {"reviewer": "r2"}]},
            "findings": list(findings), "requirements": [{"id": "REQ-1", "verdicts": verdicts or {}}]}


def _code(line, rev="head", verified=True, file="src/A.cs"):
    return {"kind": "code", "file": file, "line": line, "rev": rev, "verified": verified}


def test_planted_line_hits_window_rev_and_verification():
    p = _pack(findings=[{"reviewer": "r1", "id": "F1", "severity": "minor", "evidence": [_code(103)]},
                        {"reviewer": "r1", "id": "F2", "severity": "major", "evidence": [_code(104)]},                # outside +-3
                        {"reviewer": "r2", "id": "F3", "severity": "major", "evidence": [_code(100, rev="base")]},   # base numbering
                        {"reviewer": "r2", "id": "F4", "severity": "major", "evidence": [_code(100, verified=False)]},
                        {"reviewer": "r2", "id": "F5", "severity": "major", "evidence": [_code(100, file="src/B.cs")]}],
              verdicts={"r2": {"verdict": "not_met", "evidence": [_code(98)]}})
    h = measure.planted_line_hits(p)
    assert [x["id"] for x in h["r1"]] == ["F1"]
    assert [(x["via"], x["id"]) for x in h["r2"]] == [("not_met", "REQ-1")]
    met = _pack(verdicts={"r2": {"verdict": "met", "evidence": [_code(100)]}})
    assert measure.planted_line_hits(met) == {"r1": [], "r2": []}


def test_attribution_order_and_inherited_checks_do_not_count():
    facts = {"checks": [{"id": "tests.fail_without_fix", "status": "fail", "inherited_from": "X"}, {"id": "injection_scan", "status": "fail"}]}
    hits = {"r1": [{"via": "finding", "id": "F1"}]}
    a = measure.attribute(facts, ["verified finding r1:F1", "mandate rule R-INJECT"], hits, True)
    assert a["primary"] == "R-INJECT" and "check" not in a["fired"]
    a = measure.attribute({"checks": [{"id": "tests.targeted", "status": "fail"}]}, ["verified finding r1:F1"], hits, True)
    assert a["primary"] == "check" and a["fired"]["reviewer_on_planted_line"] == ["r1:F1"] and "other" not in a["fired"]
    a = measure.attribute({"checks": []}, ["refused clause REQ-2 (cannot_determine)"], {"r1": []}, True, stale={"REQ-2"})
    assert a["primary"] == "none" and a["fired"] == {"artifact": ["refused clause REQ-2 (cannot_determine)"]}
    assert measure.attribute({"checks": []}, [], {}, False)["primary"] == "missed"


def test_stale_fwf_refusal_needs_inherited_check():
    p = {"requirements": [{"id": "REQ-N2", "verdicts": {"r1": {"verdict": "cannot_determine", "basis": "tests.fail_without_fix was not run"}}},
                          {"id": "REQ-F1", "verdicts": {"r1": {"verdict": "cannot_determine", "basis": "runtime behaviour not shown"}}}]}
    inherited = {"checks": [{"id": "tests.fail_without_fix", "status": "pass", "inherited_from": "2283"}]}
    assert measure.stale_fwf_refusals(p, inherited) == {"REQ-N2"}
    assert measure.stale_fwf_refusals(p, {"checks": [{"id": "tests.fail_without_fix", "status": "pass"}]}) == set()


def test_mutants_inherit_fail_without_fix_from_their_original():
    ws = Workspace.at(ROOT)
    for c in [c for c in ws.changes() if "-mut" in c or c.endswith("-inject")]:
        orig = c.rsplit("-", 1)[0]
        mine = {x["id"]: x for x in read_json(ws.facts_path(c))["checks"]}
        theirs = {x["id"]: x for x in read_json(ws.facts_path(orig))["checks"]}
        if "tests.fail_without_fix" not in theirs:
            continue
        fwf = mine["tests.fail_without_fix"]
        assert fwf["inherited_from"] == orig and "byte-identical" in fwf["note"]
        assert {k: v for k, v in fwf.items() if k not in ("inherited_from", "note")} == theirs["tests.fail_without_fix"]
