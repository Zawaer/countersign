"""Stage 4: decide. Every outcome carries the rule that produced it and the evidence it used.

- Per requirement clause: `proven` or `refused` with machine reasons.
- Risk score: additive factors, each with points and a one-line reason; weights come from the mandate.
- Tier: the strictest of every driver (risk band, mandate rules, area trust caps, refusals, verified findings).
"""

from __future__ import annotations

from .common import TIERS, strictest
from .mandate import SENSITIVITY, Mandate, matches

# When several drivers set the same tier, the most specific one is listed first.
SOURCE_ORDER = ["mandate rule", "verified finding", "refused clause", "reviewer refusal", "trust cap", "risk score"]
REFUSAL_REASONS = ["check_failed", "check_not_run", "missing_review", "not_met", "reviewers_disagree", "cannot_determine", "thin_evidence"]


def check_status(facts: dict, check_id: str) -> str:
    """pass | fail | skipped | error | absent. Only `pass` counts as passing."""
    return next((c["status"] for c in facts.get("checks", []) if c["id"] == check_id), "absent")


def public_api_changed(facts: dict) -> bool | None:
    c = next((c for c in facts.get("checks", []) if c["id"] == "public_api"), None)
    if c is None or c["status"] in ("skipped", "error"):
        return None
    return bool(c.get("changed")) or c["status"] == "fail"


def files(facts: dict) -> list[dict]:
    return facts.get("diff", {}).get("by_file", [])


# --- areas ------------------------------------------------------------------

def touched_areas(facts: dict, m: Mandate) -> list[dict]:
    by_area: dict[str, list[str]] = {}
    for f in files(facts):
        by_area.setdefault(m.area_for(f["path"]).name, []).append(f["path"])
    out = []
    for a in m.areas:  # mandate order
        if a.name in by_area:
            out.append({"name": a.name, "owner": a.owner, "sensitivity": a.sensitivity, "max_ai_tier": a.max_ai_tier,
                        "checks": a.checks, "files": by_area[a.name]})
    return out


def primary_area(areas: list[dict]) -> dict | None:
    return max(areas, key=lambda a: SENSITIVITY.index(a["sensitivity"]), default=None)


# --- requirement clauses ------------------------------------------------------

def decide_clauses(reqs: dict, reviews: dict, facts: dict, m: Mandate) -> list[dict]:
    d = m["decision"]
    out = []
    for r in reqs.get("requirements", []):
        needed = list(dict.fromkeys(m["requirement_checks"].get(r.get("type", ""), []) + r.get("checks", [])))
        checks = [{"id": c, "status": check_status(facts, c)} for c in needed]
        reasons = []
        for c in checks:
            if c["status"] == "fail":
                reasons.append({"code": "check_failed", "detail": f"{c['id']} failed"})
            elif c["status"] != "pass":
                reasons.append({"code": "check_not_run", "detail": f"{c['id']} is {c['status']}"})
        verdicts = {}
        for name in d["reviewers_required"]:
            v = next((v for v in reviews.get(name, {}).get("requirement_verdicts", []) if v["req"] == r["id"]), None)
            if v is None:
                reasons.append({"code": "missing_review", "detail": f"{name} gave no verdict"})
                continue
            verdicts[name] = {"verdict": v["verdict"], "basis": v.get("confidence_basis", ""),
                              "verified": v["verified_count"], "cited": len(v["evidence"]), "evidence": v["evidence"]}
        said = {n: v["verdict"] for n, v in verdicts.items()}
        for n, v in said.items():
            if v == "not_met":
                reasons.append({"code": "not_met", "detail": f"{n}: {verdicts[n]['basis']}"})
        if len(set(said.values())) > 1:
            reasons.append({"code": "reviewers_disagree", "detail": ", ".join(f"{n} says {v}" for n, v in said.items())})
        for n, v in said.items():
            if v == "cannot_determine":
                reasons.append({"code": "cannot_determine", "detail": f"{n}: {verdicts[n]['basis']}"})
            if v == "met" and verdicts[n]["verified"] < d["min_verified_evidence"]:
                reasons.append({"code": "thin_evidence", "detail": f"{n} says met with {verdicts[n]['verified']} verified of {verdicts[n]['cited']} cited evidence items"})
        out.append({"id": r["id"], "type": r.get("type", ""), "text": r["text"], "checks": checks, "verdicts": verdicts,
                    "status": "refused" if reasons else "proven", "reasons": reasons})
    return out


# --- findings -----------------------------------------------------------------

def _anchors(f: dict) -> set:
    """What a verified finding points at: (file, line bucket) for code, the id for checks/tests."""
    out = set()
    for e in f["evidence"]:
        if e["verified"]:
            if e["kind"] == "code":
                out |= {(e["file"], e["line"] // 10), (e["file"], (e["line"] + 5) // 10)}
            elif e["kind"] in ("check", "test"):
                out.add((e["kind"], e.get("id") or e.get("name")))
    return out


def grade_findings(reviews: dict, facts: dict, m: Mandate) -> list[dict]:
    d = m["decision"]
    all_f = [f for r in reviews.values() for f in r.get("findings", [])]
    for f in all_f:
        f["tier"] = d["finding_tiers"][f["severity"]] if f["status"] == "verified" else "silent"
        f["confirmed_by"] = []
        if f["status"] != "verified" or f["severity"] != "blocker":
            continue
        others = [g for g in all_f if g["reviewer"] != f["reviewer"] and g["status"] == "verified" and g["severity"] == "blocker"]
        f["confirmed_by"] = sorted({g["reviewer"] for g in others if _anchors(f) & _anchors(g)})
        failing = [e for e in f["evidence"] if e["verified"] and (
            (e["kind"] == "check" and check_status(facts, e["id"]) == "fail") or (e["kind"] == "test" and e.get("outcome") == "failed"))]
        if f["confirmed_by"] or failing:
            f["tier"] = d["blocker_confirmed_tier"]
            f["tier_reason"] = ("confirmed by " + ", ".join(f["confirmed_by"])) if f["confirmed_by"] else "backed by a failing check"
    return all_f


# --- hard rules (predicate name in the mandate -> function) ---------------------

def _mandated(ctx):
    return [(c, a["name"], check_status(ctx["facts"], c)) for a in ctx["areas"] for c in a["checks"]]


RULES = {
    "files_changed_gt": lambda ctx, n: (ctx["facts"]["diff"]["files"] > n, f"{ctx['facts']['diff']['files']} files changed"),
    "generated_files_gt": lambda ctx, n: (len(ctx["generated"]) > n, f"{len(ctx['generated'])} generated files"),
    "public_api_changed": lambda ctx, _: (public_api_changed(ctx["facts"]) is True,
                                          next((c.get("summary", "") for c in ctx["facts"].get("checks", []) if c["id"] == "public_api"), "")),
    "source_without_tests": lambda ctx, _: (bool(ctx["source"]) and not ctx["tests"],
                                            f"{len(ctx['source'])} source files, {len(ctx['tests'])} test files changed"),
    "mandated_check_failed": lambda ctx, _: (any(s == "fail" for *_, s in _mandated(ctx)),
                                             "; ".join(f"{c} ({a}): fail" for c, a, s in _mandated(ctx) if s == "fail")),
    "mandated_check_missing": lambda ctx, _: (any(s not in ("pass", "fail") for *_, s in _mandated(ctx)),
                                              "; ".join(f"{c} ({a}): {s}" for c, a, s in dict.fromkeys(_mandated(ctx)) if s not in ("pass", "fail"))),
    "mandate_unsigned": lambda ctx, _: (not ctx["mandate_sig"]["valid"], ctx["mandate_sig"]["reason"]),
}


def fire_rules(ctx: dict, m: Mandate) -> list[dict]:
    fired = []
    for rule in m["rules"]:
        hit, evidence = RULES[rule["when"]](ctx, rule.get("value"))
        if hit:
            fired.append({**rule, "evidence": evidence})
    return fired


# --- risk score ---------------------------------------------------------------

def risk_score(ctx: dict, clauses: list[dict], m: Mandate) -> dict:
    w, facts = m["risk"], ctx["facts"]
    prim = primary_area(ctx["areas"])
    n_files = facts["diff"]["files"]
    lines = sum(f.get("ins", 0) + f.get("del", 0) for f in files(facts) if f.get("kind") != "generated")
    sec = [f["path"] for f in files(facts) if matches(f["path"], m["security_sensitive_paths"])]
    api = public_api_changed(facts)
    fwf = check_status(facts, "tests.fail_without_fix")
    disagree = [c["id"] for c in clauses if any(r["code"] == "reviewers_disagree" for r in c["reasons"])]
    failed = [c["id"] for c in facts.get("checks", []) if c["status"] == "fail" and c["id"] != "public_api"]

    def capped(points, cap):
        return round(min(points, cap), 1)

    factors = [
        ("area_sensitivity", w["sensitivity_points"][prim["sensitivity"]] if prim else 0,
         f"most sensitive area touched: {prim['name']} ({prim['sensitivity']})" if prim else "no files mapped"),
        ("files_changed", capped(n_files * w["per_file"], w["files_cap"]), f"{n_files} files x {w['per_file']} (cap {w['files_cap']})"),
        ("lines_changed", capped(lines / 100 * w["per_100_lines"], w["lines_cap"]),
         f"{lines} non-generated lines x {w['per_100_lines']}/100 (cap {w['lines_cap']})"),
        ("generated_files", capped(len(ctx["generated"]) * w["per_generated_file"], w["generated_cap"]),
         f"{len(ctx['generated'])} generated files x {w['per_generated_file']} (cap {w['generated_cap']})"),
        ("public_api_change", w["public_api_change"] if api is not False else 0,
         {True: "public API changed", False: "public_api check: no change", None: "public API not checked (counted as changed)"}[api]),
        ("source_without_tests", w["source_without_tests"] if ctx["source"] and not ctx["tests"] else 0,
         "source changed, no test changed" if ctx["source"] and not ctx["tests"] else "tests changed alongside source" if ctx["source"] else "no source changed"),
        ("security_sensitive_paths", w["security_sensitive_path"] if sec else 0, ", ".join(sec) or "none touched"),
        ("fail_without_fix_not_shown", w["fail_without_fix_not_shown"] if fwf != "pass" else 0, f"tests.fail_without_fix: {fwf}"),
        ("reviewer_disagreement", len(disagree) * w["per_reviewer_disagreement"],
         f"{len(disagree)} clause(s) x {w['per_reviewer_disagreement']}" + (f": {', '.join(disagree)}" if disagree else "")),
        ("failed_checks", len(failed) * w["per_failed_check"], f"{len(failed)} failed check(s) x {w['per_failed_check']}" + (f": {', '.join(failed)}" if failed else "")),
    ]
    score = round(sum(p for _, p, _ in factors), 1)
    tier = "silent"
    for t in TIERS[1:]:
        if score >= w["thresholds"][t]:
            tier = t
    return {"score": score, "tier": tier, "thresholds": w["thresholds"],
            "factors": [{"factor": f, "points": p, "reason": r} for f, p, r in factors]}


# --- the whole decision -------------------------------------------------------

def decide(facts: dict, reviews: dict, reqs: dict, m: Mandate, mandate_sig: dict, caps: dict) -> dict:
    """`reviews` are verified reviews; `caps` maps area -> {"cap", "reason"} from the trust ledger."""
    d = m["decision"]
    areas = touched_areas(facts, m)
    by_kind = lambda k: [f["path"] for f in files(facts) if f.get("kind") == k]  # noqa: E731
    ctx = {"facts": facts, "areas": areas, "mandate_sig": mandate_sig,
           "generated": by_kind("generated"), "source": by_kind("source"), "tests": by_kind("test")}
    clauses = decide_clauses(reqs, reviews, facts, m)
    findings = grade_findings(reviews, facts, m)
    rules = fire_rules(ctx, m)
    risk = risk_score(ctx, clauses, m)
    refusals = [{**r, "reviewer": name, "model": rev.get("model")} for name, rev in reviews.items() for r in rev.get("refusals", [])]

    bands = ", ".join(f"{t}>={v}" for t, v in risk["thresholds"].items())
    top = sorted((f for f in risk["factors"] if f["points"]), key=lambda f: -f["points"])[:3]
    top_s = " + ".join(f"{f['factor']} {f['points']}" for f in top)
    drivers = [{"source": "risk score", "id": "risk", "tier": risk["tier"], "why": f"score {risk['score']} ({bands}); largest: {top_s}"}]
    drivers += [{"source": "mandate rule", "id": r["id"], "tier": r["tier"], "why": f"{r['message']} [{r['evidence']}]"} for r in rules]
    for a in areas:
        c = caps.get(a["name"], {"cap": a["max_ai_tier"], "reason": "mandate clearance right"})
        a["cap"], a["cap_reason"] = c["cap"], c["reason"]
        drivers.append({"source": "trust cap", "id": a["name"], "tier": c["cap"], "why": f"{a['name']}: AI may clear at most to {c['cap']} ({c['reason']})"})
    drivers += [{"source": "refused clause", "id": c["id"], "tier": d["refused_clause_tier"], "codes": [r["code"] for r in c["reasons"]],
                 "why": "; ".join(f"{r['code']}: {r['detail']}" for r in c["reasons"])} for c in clauses if c["status"] == "refused"]
    drivers += [{"source": "reviewer refusal", "id": f"{r['reviewer']}", "tier": d["reviewer_refusal_tier"],
                 "why": f"{r['topic']} ({r['reason']})"} for r in refusals]
    drivers += [{"source": "verified finding", "id": f"{f['reviewer']}:{f['id']}", "tier": f["tier"],
                 "why": f"{f['severity']}: {f['title']}" + (f" ({f['tier_reason']})" if f.get("tier_reason") else "")}
                for f in findings if f["status"] == "verified" and f["tier"] != "silent"]

    drivers.sort(key=lambda x: (-TIERS.index(x["tier"]), SOURCE_ORDER.index(x["source"])))
    tier = strictest("silent", *(x["tier"] for x in drivers))
    prim = primary_area(areas)
    return {
        "tier": tier,
        "decisive": [x for x in drivers if x["tier"] == tier],
        "drivers": drivers,
        "primary_area": prim["name"] if prim else None,
        "owner": prim["owner"] if prim else m["owner"],
        "notify": sorted({a["owner"] for a in areas} - {prim["owner"] if prim else m["owner"]}),
        "areas": areas,
        "clauses": clauses,
        "findings": findings,
        "reviewer_refusals": refusals,
        "rules_fired": rules,
        "risk": risk,
    }
