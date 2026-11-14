"""Supply-chain rules (mandate v4: dependency-change, new-advisory, build-egress-violation) and the pack section."""

import json
from pathlib import Path

import pytest
import yaml
from conftest import make_facts

from countersign import decide, mandate, measure, pack
from countersign.common import Workspace, base_change, is_mutant, write_json

ROOT = Path(__file__).resolve().parents[1]
ATTACK = ROOT / "evidence" / "supply-chain" / "attack-2283" / "deps.delta.json"
RULE_IDS = {"dependency-change", "new-advisory", "build-egress-violation"}


def deps_check(new=(), vulns=(), sources=None, status=None):
    c = {"id": "deps.delta", "status": status or ("fail" if new or vulns or sources else "pass"), "summary": "s",
         "new_or_changed": list(new), "packages_added": [], "versions_changed": [], "projects_added": [], "project_references_added": [],
         "build_inputs_changed": {"package_sources": sources} if sources else {},
         "vulnerabilities_new": list(vulns), "vulnerabilities_also_on_base": []}
    return c


def route(ws, *checks, allowed=None):
    if allowed is not None:
        p = ws.mandate_path
        data = yaml.safe_load(p.read_text())
        data["supply_chain"]["allowed_new_dependencies"] = allowed
        p.write_text(yaml.safe_dump(data, sort_keys=False))
        mandate.sign(ws, "Toivo")
    f = make_facts(base=ws.base, head=ws.head)
    f["checks"] += list(checks)
    write_json(ws.facts_path("9001"), f)
    return pack.build(ws, "9001")


def fired(p):
    return {r["id"]: r for r in p["rules_fired"] if r["id"] in RULE_IDS}


def test_the_mandate_routes_supply_chain_but_never_mandates_deps_delta_as_an_area_check():
    m = yaml.safe_load((ROOT / "mandate" / "messagepack.mandate.yaml").read_text())
    assert m["version"] >= 4 and m["supply_chain"]["allowed_new_dependencies"] == []
    rules = {r["id"]: r for r in m["rules"]}
    assert (rules["dependency-change"]["tier"], rules["new-advisory"]["tier"], rules["build-egress-violation"]["tier"]) == ("ask", "block", "block")
    assert all(r["when"] in decide.RULES for r in m["rules"])
    assert not any("deps.delta" in a.get("checks", []) for a in m["areas"].values())


def test_a_clean_dependency_graph_changes_nothing(ws):
    base = route(ws)
    p = route(ws, deps_check(), {"id": "build.egress", "status": "skipped", "summary": "not on CRACI"},
              {"id": "craci.network", "status": "skipped", "summary": "no CRACI_API_TOKEN"})
    assert not fired(p) and p["tier"] == base["tier"] and p["supply_chain"]["status"] == "pass"


def test_unallowed_new_or_moved_package_asks(ws):
    p = route(ws, deps_check(new=["SharpZipLib@1.2.0"]))
    r = fired(p)
    assert set(r) == {"dependency-change"} and "SharpZipLib@1.2.0" in r["dependency-change"]["evidence"]
    assert p["tier"] == "ask" and p["signoff"]["required"]


@pytest.mark.parametrize("allowed", [["sharpziplib"], ["SHARPZIPLIB@1.2.0"]])
def test_allowlist_by_name_or_name_at_version_case_insensitive(ws, allowed):
    p = route(ws, deps_check(new=["SharpZipLib@1.2.0"], status="pass"), allowed=allowed)
    assert "dependency-change" not in fired(p)


def test_allowlist_for_another_version_does_not_allow(ws):
    p = route(ws, deps_check(new=["SharpZipLib@1.2.0"]), allowed=["SharpZipLib@1.3.3"])
    assert "dependency-change" in fired(p)


def test_a_new_package_feed_asks_even_without_new_packages(ws):
    p = route(ws, deps_check(sources={"base": {"nuget.config:nuget": "https://api.nuget.org/v3/index.json"},
                                      "head": {"nuget.config:evil": "https://feed.example.com/v3/index.json"}}))
    assert "dependency-change" in fired(p) and "feed" in fired(p)["dependency-change"]["evidence"]


def test_a_new_advisory_blocks_and_cites_it(ws):
    v = {"package": "SharpZipLib", "version": "1.2.0", "severity": "high", "advisory": "https://github.com/advisories/GHSA-m22m-h4rf-pwq3"}
    p = route(ws, deps_check(new=["SharpZipLib@1.2.0"], vulns=[v]), allowed=["SharpZipLib"])  # allowed package, still blocks
    assert set(fired(p)) == {"new-advisory"} and p["tier"] == "block"
    assert "GHSA-m22m-h4rf-pwq3" in fired(p)["new-advisory"]["evidence"]
    assert p["signoff"]["allowed_decisions"] == ["reject", "request-changes"]


@pytest.mark.parametrize("cid", ["build.egress", "craci.network"])
def test_an_egress_violation_blocks(ws, cid):
    c = {"id": cid, "status": "fail", "summary": "1 proxy violation(s): the build tried to reach evil.example.com (no_match)",
         "blocked_hosts": ["evil.example.com"], "proxy_violations": [{"host": "evil.example.com", "reason": "no_match"}]}
    p = route(ws, c)
    assert set(fired(p)) == {"build-egress-violation"} and p["tier"] == "block"
    assert "evil.example.com" in fired(p)["build-egress-violation"]["evidence"]


def test_supply_chain_rules_only_make_routing_stricter(ws):
    """Principle 0 stays: a failing deps.delta is never a failed mandated check, and no supply-chain input lowers a tier."""
    base = route(ws)
    for c in (deps_check(new=["A@1"]), deps_check(status="fail"), {"id": "build.egress", "status": "pass", "summary": "ok"}):
        p = route(ws, c)
        assert decide.TIERS.index(p["tier"]) >= decide.TIERS.index(base["tier"])
        assert "mandated-check-failed" not in {r["id"] for r in p["rules_fired"]}


def test_the_seeded_attack_on_2283_blocks_with_its_advisories(ws):
    attack = json.loads(ATTACK.read_text())
    p = route(ws, attack)
    r = fired(p)
    assert set(r) == {"dependency-change", "new-advisory"} and p["tier"] == "block"
    for gh in ("GHSA-m22m-h4rf-pwq3", "GHSA-mm6g-mmq6-53ff"):
        assert gh in r["new-advisory"]["evidence"]
        assert any(gh in w["why"] for w in p["why"])
    assert "FluentAssertions@7.2.0" in r["dependency-change"]["evidence"]
    sc = p["supply_chain"]
    assert [(x["package"], x["base"], x["head"]) for x in sc["deps"]["packages"]] == [("SharpZipLib", None, "1.2.0"), ("FluentAssertions", "7.0.0", "7.2.0")]
    assert [v["id"] for v in sc["deps"]["vulnerabilities_new"]] == ["GHSA-m22m-h4rf-pwq3", "GHSA-mm6g-mmq6-53ff"]
    md, html = pack.to_markdown(p), pack.to_html(p)
    assert "**New advisory** SharpZipLib 1.2.0" in md and "Already on base" in md
    assert 'id="supply-chain"' in html and "GHSA-mm6g-mmq6-53ff" in html and "Supply-chain detail" in html


def test_2283_deps_is_a_routable_seeded_change():
    ws = Workspace.at(ROOT)
    assert is_mutant("2283-deps") and base_change("2283-deps") == "2283"
    f = json.loads(ws.facts_path("2283-deps").read_text())
    assert f["mutation"]["kind"] == "supply_chain" and f["mutation"]["of"] == "2283"
    r = measure.deterministic_route(ws, "2283-deps")
    assert r["tier"] == "block" and {"dependency-change", "new-advisory"} <= set(r["rules"]) and r["failed_checks"] == ["deps.delta"]
    row = next(x for x in measure.mutant_table(ws) if x["change"] == "2283-deps")
    assert row["kind"] == "supply_chain" and row["caught_by_checks"] and row["routed_to_human"]


def test_supply_chain_section_is_deterministic_and_compact(ws):
    real = json.loads((ROOT / "evidence" / "2129" / "facts.json").read_text())
    c = next(x for x in real["checks"] if x["id"] == "deps.delta")
    a, b = route(ws, c), route(ws, c)
    assert a["supply_chain"] == b["supply_chain"]
    sc = a["supply_chain"]
    assert sc["status"] == "pass" and not sc["rules"] and sc["deps"]["projects_added"] and sc["deps"]["project_references_added"]
    assert "1 new project" in sc["line"] and "0 new advisories (6 already on base)" in sc["line"]
    assert sc["egress"] is None and "not recorded" in sc["line"]
    assert len(sc["deps"]["vulnerabilities_also_on_base"]) == 6
