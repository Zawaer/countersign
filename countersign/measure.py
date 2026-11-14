"""Measurement: replay the pipeline over every change (real branches and seeded mutants).

Every number carries `simulated: true|false`:
- counts derived from inputs are simulated if any input file says `"simulated": true` (fixtures do);
- review-time minutes are always simulated: they come from the reading-speed model in the mandate, not a stopwatch.
"""

from __future__ import annotations

from copy import deepcopy

from . import decide as decide_mod, ledger, pack as pack_mod
from .common import HUMAN_TIERS, TIERS, Workspace, base_change, is_mutant, read_json, write_json
from .mandate import load, signature_status

INHERITED = ("tests.fail_without_fix", "tests.execution_fail_without_fix", "public_api", "analyzers")  # properties of the tests and the diff, not of the one-line edit

GENERIC_RULES = {"mandated-check-missing", "mandate-not-signed"}
GENERIC_CODES = {"check_not_run", "missing_review"}


def _minutes(p: dict, mm: dict) -> tuple[float, float]:
    """(full read, pack-guided read) minutes for one change, from the mandate's reading model."""
    lines = p["_lines"]
    full = p["diff"]["files"] * mm["full_read_minutes_per_file"]
    full += lines["source"] / mm["full_read_lines_per_minute"] + lines["generated"] / mm["generated_lines_per_minute"]
    guided = mm["pack_minutes"][p["tier"]]
    if p["tier"] in HUMAN_TIERS:
        guided += mm["minutes_per_refused_item"] * (len(p["refused"]["clauses"]) + len(p["refused"]["reviewer_refusals"]))
        guided += mm["minutes_per_verified_finding"] * len(p["findings"])
    return round(full, 1), round(guided, 1)


def _signals(p: dict) -> set[str]:
    """Specific reasons a change went to a human: verified findings, failing checks, hard rules, refused clauses
    (not generic ones such as 'a mandated check is absent' or 'no review')."""
    out = set()
    for w in p["drivers"]:
        if w["tier"] not in HUMAN_TIERS:
            continue
        if w["source"] == "verified finding" or (w["source"] == "mandate rule" and w["id"] not in GENERIC_RULES):
            out.add(f"{w['source']} {w['id']}")
        elif w["source"] == "refused clause" and set(w.get("codes", [])) - GENERIC_CODES:
            out.add(f"refused clause {w['id']} ({', '.join(sorted(set(w['codes']) - GENERIC_CODES))})")
    return out


def _caught_by(mutant: dict, original: dict | None) -> list[str]:
    """Signals the mutant raised that its unmutated original did not: those are attributable to the seeded defect."""
    return sorted(_signals(mutant) - (_signals(original) if original else set()))


def deterministic_route(ws: Workspace, change: str, m=None) -> dict:
    """Tier from facts alone (no reviews, no clauses, mandate caps). For a mutant, the checks a one-line source edit
    cannot change (fail-without-fix, public API, analyzers) are inherited from the unmutated original, so the
    original and the mutant are routed on equal terms; the original is routed the same way for comparison."""
    m = m or load(ws)
    facts = deepcopy(read_json(ws.facts_path(change)))
    if is_mutant(change) and ws.facts_path(base_change(change)).exists():
        orig = read_json(ws.facts_path(base_change(change)))
        have = {c["id"] for c in facts.get("checks", [])}
        facts["checks"] = facts.get("checks", []) + [{**c, "inherited_from": base_change(change)} for c in orig.get("checks", [])
                                                      if c["id"] in INHERITED and c["id"] not in have]
    d = decide_mod.decide(facts, {}, {"requirements": []}, m, signature_status(ws, m), {})
    rules = {r["id"] for r in d["rules_fired"]}
    return {"tier": d["tier"], "score": d["risk"]["score"], "rules": sorted(rules),
            "why": [f"{w['source']}: {w['id']}" for w in d["decisive"]],
            "failed_checks": [c["id"] for c in facts.get("checks", []) if c["status"] == "fail" and c["id"] != "public_api" and "inherited_from" not in c]}


def mutant_table(ws: Workspace) -> list[dict]:
    """Every seeded defect: what the deterministic checks caught, and where it would be routed before any AI review.
    Hook for reviews: once reviews/<mutant>/<reviewer>.json exist (e.g. the Nemotron CI reviewer), `replay` also
    builds the full pack for that mutant and reports catch_rate / catch_rate_attributable with the reviewers included."""
    m = load(ws)
    catalogue = {}
    cat_path = ws.root / "measurement" / "mutants" / "mutants.json"
    if cat_path.exists():
        catalogue = {x["id"]: x for x in read_json(cat_path)["mutants"]}
    rows, originals = [], {}
    for change in [c for c in ws.changes() if is_mutant(c)]:
        f = read_json(ws.facts_path(change))
        of = base_change(change)
        if of not in originals and ws.facts_path(of).exists():
            originals[of] = deterministic_route(ws, of, m)
        r = deterministic_route(ws, change, m)
        o = originals.get(of)
        new_signals = sorted(set(r["rules"]) - set(o["rules"] if o else []))
        if o and TIERS.index(r["tier"]) > TIERS.index(o["tier"]) and not new_signals:
            new_signals = [f"risk {o['score']} -> {r['score']} (failed: {', '.join(r['failed_checks'])})"]
        rows.append({"change": change, "of": of, "kind": f["mutation"].get("kind") or catalogue.get(change, {}).get("kind"),
                     "description": f["mutation"].get("description"),
                     "caught_by_checks": bool(r["failed_checks"]), "failed_checks": r["failed_checks"],
                     "tier": r["tier"], "original_tier": o["tier"] if o else None, "routed_to_human": r["tier"] in HUMAN_TIERS,
                     "attributable": new_signals, "reviews": sorted(ws.reviews(change)) or "pending",
                     "simulated": bool(f.get("simulated"))})
    return rows


def reviewer_cross_check(packs: dict) -> dict:
    """Per reviewer: blocker/major findings it raised that verified, how many another reviewer also raised (same anchor),
    and how many verified blocker/major findings of OTHER reviewers it did not raise (its misses, as far as the panel knows)."""
    out: dict[str, dict] = {}
    for p in packs.values():
        fs = [f for f in p.get("findings", []) if f.get("severity") in ("blocker", "major")]
        names = {r["reviewer"] for r in p["checked_by"]["reviewers"]}
        for n in names:
            s = out.setdefault(n, {"major_raised_verified": 0, "confirmed_by_another": 0, "missed_others_verified_major": 0})
            mine = [f for f in fs if f["reviewer"] == n and f["status"] == "verified"]
            others = [f for f in fs if f["reviewer"] != n and f["status"] == "verified"]
            s["major_raised_verified"] += len(mine)
            s["confirmed_by_another"] += sum(any(decide_mod._anchors(f) & decide_mod._anchors(g) for g in others) for f in mine)
            s["missed_others_verified_major"] += sum(not any(decide_mod._anchors(f) & decide_mod._anchors(g) for g in mine) for f in others)
    return out


def _tokens_per_change(ws: Workspace) -> dict:
    """Model tokens per change from measurement/costs.yaml (a run covering several changes is split evenly)."""
    import yaml
    p = ws.measurement_dir / "costs.yaml"
    if not p.exists():
        return {}
    out: dict[str, int] = {}
    for r in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("runs", []):
        changes = r.get("changes") or ([r["change"]] if r.get("change") else [])
        tok = r.get("tokens_total") or ((r.get("tokens_in") or 0) + (r.get("tokens_out") or 0))
        for c in changes:
            out[c] = out.get(c, 0) + round(tok / len(changes))
    return out


def replay(ws: Workspace) -> dict:
    mm = load(ws)["measurement"]
    rows, packs = [], {}
    skipped, by_checks = [], {}
    for change in ws.changes():
        if is_mutant(change):  # deterministic checks alone, from facts.json, whether or not reviews exist yet
            f = read_json(ws.facts_path(change))
            by_checks[change] = {"failed": [c["id"] for c in f.get("checks", []) if c["status"] == "fail"], "simulated": bool(f.get("simulated"))}
        if not ws.reviews(change):
            skipped.append({"change": change, "reason": "no reviews yet (stage 2 not run); excluded from every metric"})
            continue
        p = pack_mod.build(ws, change, use_trust=False)
        facts = read_json(ws.facts_path(change))
        bf = facts.get("diff", {}).get("by_file", [])
        p["_lines"] = {"source": sum(f.get("ins", 0) + f.get("del", 0) for f in bf if f.get("kind") != "generated"),
                       "generated": sum(f.get("ins", 0) + f.get("del", 0) for f in bf if f.get("kind") == "generated")}
        full, guided = _minutes(p, mm)
        packs[change] = p
        rows.append({
            "change": change, "mutant": is_mutant(change), "of": base_change(change) if is_mutant(change) else None,
            "mutation": p.get("mutation"), "tier": p["tier"], "score": p["risk"]["score"], "owner": p["owner"],
            "routed_to_human": p["tier"] in HUMAN_TIERS,
            "why": [f"{w['source']} {w['id']}" for w in p["why"]],
            "caught_by": None,
            "proven": sum(c["status"] == "proven" for c in p["requirements"]),
            "refused": len(p["refused"]["clauses"]),
            "full_read_min": full, "guided_min": guided, "simulated": p["simulated"],
        })

    for r in rows:
        if r["mutant"]:
            r["caught_by"] = _caught_by(packs[r["change"]], packs.get(r["of"]))
    real = [r for r in rows if not r["mutant"]]
    mutants = [r for r in rows if r["mutant"]]
    caught = [r for r in mutants if r["routed_to_human"]]
    attributable = [r for r in caught if r["caught_by"]]
    per_reviewer: dict[str, dict] = {}
    for p in packs.values():
        for r in p["checked_by"]["reviewers"]:
            s = per_reviewer.setdefault(r["reviewer"], {"model": r["model"], "verified": 0, "rejected": 0, "refusals": 0})
            s["verified"] += r["verified"]
            s["rejected"] += r["rejected"]
            s["refusals"] += r["refusals"]
    for s in per_reviewer.values():
        total = s["verified"] + s["rejected"]
        s["rejected_share"] = round(s["rejected"] / total, 2) if total else None
    events = ledger.read(ws)
    escapes = [e for e in events if e["type"] == "escape"]
    spots = [e for e in events if e["type"] == "spotcheck"]
    any_sim = lambda rs: any(r["simulated"] for r in rs)  # noqa: E731

    def metric(value, simulated, how):
        return {"value": value, "simulated": simulated, "how": how}

    full_total = sum(r["full_read_min"] for r in real)
    guided_total = sum(r["guided_min"] for r in real)
    metrics = {
        "seeded_defects": metric(len(mutants), any_sim(mutants), "mutants found as evidence/<change>-mutK"),
        "catch_rate": metric(round(len(caught) / len(mutants), 2) if mutants else None, any_sim(mutants),
                             "share of seeded defects routed to a human (ask/block) instead of AI-cleared"),
        "catch_rate_attributable": metric(round(len(attributable) / len(mutants), 2) if mutants else None, any_sim(mutants),
                                          "share routed to a human by a specific signal (failing check, verified finding, hard rule, refused clause) "
                                          "that the unmutated original did not raise"),
        "caught_by_checks_alone": metric(
            {"caught": sum(bool(v["failed"]) for v in by_checks.values()), "of": len(by_checks),
             "detail": {c: v["failed"] or "no check failed" for c, v in by_checks.items()}},
            any(v["simulated"] for v in by_checks.values()), "seeded defects where a deterministic check failed (no AI involved; includes mutants without reviews)"),
        "missed_defects": metric([r["change"] for r in mutants if not r["routed_to_human"]], any_sim(mutants), "seeded defects the AI would have cleared"),
        "share_routed_to_humans": metric(round(sum(r["routed_to_human"] for r in real) / len(real), 2) if real else None, any_sim(real),
                                         "real changes (not mutants) at ask/block"),
        "findings_per_reviewer": metric(per_reviewer, any_sim(rows), "verified vs rejected (unsupported) findings over all replayed changes"),
        "human_minutes_full_read": metric(round(full_total, 1), True, "reading-speed model in the mandate: lines/min + minutes per file"),
        "human_minutes_with_pack": metric(round(guided_total, 1), True, "pack reading time by tier + per refused item + per verified finding"),
        "review_time_saved_share": metric(round(1 - guided_total / full_total, 2) if full_total else None, True, "1 - with_pack / full_read"),
        "escapes_recorded": metric(len(escapes), any(e["payload"].get("simulated") for e in escapes), "escape events in the ledger"),
        "spotcheck_agreement": metric(round(sum(e["payload"]["result"] == "agree" for e in spots) / len(spots), 2) if spots else None,
                                      any(e["payload"].get("simulated") for e in spots), "agreeing spot-checks / all spot-checks in the ledger"),
    }
    mt = mutant_table(ws)
    metrics["seeded_defects_total"] = metric(len(mt), any(r["simulated"] for r in mt), "every evidence/<change>-mutK, with or without reviews")
    metrics["seeded_routed_to_human_before_review"] = metric(
        {"routed": sum(r["routed_to_human"] for r in mt), "attributable": sum(bool(r["attributable"]) for r in mt), "of": len(mt)},
        any(r["simulated"] for r in mt),
        "facts only (no reviews): mutants at ask/block; attributable = a hard rule fired, or the tier rose, versus the unmutated original routed the same way")
    metrics["reviewer_cross_check"] = metric(reviewer_cross_check(packs), any_sim(rows),
                                             "blocker/major findings: raised and verified, confirmed by another reviewer (shared anchor), "
                                             "and other reviewers' verified ones this reviewer did not raise")
    metrics["time_per_change"] = metric({r["change"]: {"full_read_min": r["full_read_min"], "with_pack_min": r["guided_min"],
                                                       "saved_min": round(r["full_read_min"] - r["guided_min"], 1)} for r in real}, True,
                                        "reading model; negative = the pack costs more than reading the diff (small changes)")
    metrics["model_tokens_per_change"] = metric(_tokens_per_change(ws), False, "measurement/costs.yaml; estimates where the row says so")
    out = {"inputs": str(ws.inputs), "changes": rows, "skipped": skipped, "mutants": mt, "metrics": metrics}
    hist = ws.root / "measurement" / "history" / "results.json"
    if hist.exists():
        h = read_json(hist)
        out["history"] = {"simulated": False, "source": "measurement/history/results.json", **{k: {kk: vv for kk, vv in v.items() if kk != "escapes_cleared"}
                          | {"escapes_cleared": [x["pr"] for x in v["escapes_cleared"]]} for k, v in h["modes"].items()}}
    sim = ws.root / "measurement" / "simulation" / "results.json"
    if sim.exists():
        out["simulation"] = {"simulated": True, "source": "measurement/simulation/results.json", "summary": read_json(sim)["summary"]}
    return out


def write(ws: Workspace, result: dict) -> None:
    write_json(ws.measurement_dir / "results.json", result)
    (ws.measurement_dir / "results.md").write_text(to_markdown(result), encoding="utf-8")
    update_doc(ws, result)


def to_markdown(r: dict) -> str:
    out = ["# Countersign replay results", "",
           "Every number says whether it is simulated. Minutes are always a model estimate (see the mandate's `measurement` block).", "",
           "| Change | Tier | Score | Routed to human | Proven/refused | Why | Caught by | Full read min | With pack min | Simulated |",
           "|---|---|---:|---|---|---|---|---:|---:|---|"]
    for c in r["changes"]:
        out.append(f"| {c['change']} | {c['tier']} | {c['score']} | {'yes' if c['routed_to_human'] else 'no'} | {c['proven']}/{c['refused']} | "
                   f"{'; '.join(c['why'])} | {'; '.join(c['caught_by']) if c['caught_by'] else ('MISSED' if c['mutant'] else '-')} | "
                   f"{c['full_read_min']} | {c['guided_min']} | {c['simulated']} |")
    if r.get("skipped"):
        out += ["", *(f"- Not replayed: {s['change']}: {s['reason']}" for s in r["skipped"])]
    if r.get("mutants"):
        out += ["", "## Seeded defects (facts only; AI reviews pending)", "",
                "| Mutant | Kind | Caught by checks | Failed checks | Tier (no reviews) | Original's tier | Attributable signal (vs original) | Reviews |",
                "|---|---|---|---|---|---|---|---|"]
        out += [f"| {x['change']} | {x['kind']} | {'yes' if x['caught_by_checks'] else '**no**'} | {', '.join(x['failed_checks']) or '-'} | {x['tier']} | "
                f"{x['original_tier']} | {', '.join(x['attributable']) or '-'} | {x['reviews'] if isinstance(x['reviews'], str) else ', '.join(x['reviews'])} |"
                for x in r["mutants"]]
    out += ["", "| Metric | Value | Simulated | How |", "|---|---|---|---|"]
    for k, m in r["metrics"].items():
        v = m["value"]
        if k in ("caught_by_checks_alone",):
            v = f"{v['caught']} of {v['of']}"
        if k == "findings_per_reviewer":
            v = "; ".join(f"{n}: {s['verified']} verified, {s['rejected']} rejected, {s['refusals']} refusals" for n, s in v.items())
        out.append(f"| {k} | {v} | {m['simulated']} | {m['how']} |")
    return "\n".join(out) + "\n"


# --- docs/MEASUREMENT.md: the numbers block is generated, so the page has one source of truth -----------------

START, END = "<!-- numbers:start (generated by `countersign replay`; do not edit by hand) -->", "<!-- numbers:end -->"


def _mutant_counts(ws: Workspace) -> dict:
    """Straight from evidence/*-mutK/facts.json: mutation.caught_by_any_deterministic_check."""
    rows = {c: read_json(ws.facts_path(c))["mutation"] for c in ws.changes() if is_mutant(c)}
    survived = sorted(c for c, m in rows.items() if not m.get("caught_by_any_deterministic_check"))
    return {"total": len(rows), "caught": len(rows) - len(survived), "survived": survived,
            "kinds": sorted({m.get("kind") for m in rows.values() if m.get("kind")})}


def render_numbers(ws: Workspace, result: dict) -> str:
    mm = load(ws)["measurement"]
    met = result["metrics"]
    mc = _mutant_counts(ws)
    mt = {x["change"]: x for x in result.get("mutants", [])}
    cleared_mut = [c for c, x in mt.items() if not x["routed_to_human"]]
    sr = met["seeded_routed_to_human_before_review"]["value"]
    L = ["### Real (`simulated: false`)", "",
         "| Metric | Value | Source |", "|---|---|---|",
         f"| Seeded defects caught by deterministic checks alone | **{mc['caught']} of {mc['total']}**; survived: {', '.join(mc['survived'])} | `evidence/*-mut*/facts.json` (`caught_by_any_deterministic_check`) |",
         f"| Seeded defects routed to a human before any AI review | {sr['routed']} of {sr['of']} ({sr['attributable']} attributable to the defect); "
         f"would be AI-cleared: {', '.join(cleared_mut) or 'none'} | `measurement/results.json` `mutants` |"]
    h = result.get("history")
    if h:
        ci, do = h["ci-credited"], h["diff-only"]
        c = ci["confusion"]
        L += [f"| Historical PRs routed to a human (lenient ci-credited mode) | **{ci['routed_to_humans']} of {ci['n']}** ({ci['share_routed_to_humans']:.0%}); diff-only: {do['routed_to_humans']} of {do['n']} | `measurement/history/results.json` |",
              f"| Real escapes the AI would have cleared | **{c['escape_cleared']} of {ci['escapes']}** ({ci['escapes_high_confidence']} high-confidence); cleared bucket: {c['clean_cleared'] + c['escape_cleared']} PRs | same |",
              f"| Escape rate, routed vs cleared bucket | {ci['escape_rate_routed']} vs {ci['escape_rate_cleared']} | same |",
              f"| Upstream median days from PR opened to merged | cleared bucket {ci['median_days_to_merge_upstream']['cleared']}, routed bucket {ci['median_days_to_merge_upstream']['routed']} | GitHub `createdAt` / `mergedAt` |"]
    per = met["findings_per_reviewer"]["value"]
    cross = met["reviewer_cross_check"]["value"]
    L.append("| Findings per reviewer (verified / rejected as unsupported) | " + "; ".join(
        f"{n}: {s['verified']} / {s['rejected']}" for n, s in per.items()) + " | `measurement/results.json` |")
    L.append("| Blocker/major findings: raised and verified, confirmed by another reviewer, others' verified ones it did not raise | " + "; ".join(
        f"{n}: {s['major_raised_verified']}, {s['confirmed_by_another']}, {s['missed_others_verified_major']}" for n, s in cross.items()) + " | same |")
    L.append(f"| Real changes routed to a human | {met['share_routed_to_humans']['value']:.0%} of {len([r for r in result['changes'] if not r['mutant']])} | same |")
    tok = met["model_tokens_per_change"]["value"]
    if tok:
        L.append(f"| Model tokens per change (estimates, see docs/COSTS.md) | " + ", ".join(f"{c}: {t:,}" for c, t in sorted(tok.items())) + " | `measurement/costs.yaml` |")
    L += ["", "### Simulated review time (reading model in the mandate, `simulated: true`)", "",
          "| Change | Full read (min) | With the pack (min) | Saved (min) |", "|---|---:|---:|---:|"]
    for c, v in met["time_per_change"]["value"].items():
        L.append(f"| {c} | {v['full_read_min']} | {v['with_pack_min']} | {v['saved_min']} |")
    if h:
        rows = read_json(ws.root / "measurement" / "history" / "results.json")["prs"]
        cleared = [p for p in rows if p["ci-credited"]["cleared"]]
        full = sum(p["files"] * mm["full_read_minutes_per_file"] + p["lines"] / mm["full_read_lines_per_minute"] for p in cleared)
        allm = sum(p["files"] * mm["full_read_minutes_per_file"] + p["lines"] / mm["full_read_lines_per_minute"] for p in rows)
        L += ["", f"Routing, on the {len(rows)} historical PRs: the {len(cleared)} the AI would clear (notify) need no human read at all, "
              f"about {full:.0f} of {allm:.0f} full-read minutes ({full / allm:.0%}; same reading model, every line counted as source). "
              "Routed changes still get a full read when the owner wants one."]
    sim = result.get("simulation")
    if sim:
        s = sim["summary"]
        L += ["", f"### Simulated trust over time ({s['replicates']} runs x {s['weeks']} weeks; reviewers degrade at week {s['drift_week']})", "",
              "| Scenario | min/week (wk 9-drift) | escapes/week (wk 9-drift) | min/week after drift | escapes/week after drift |", "|---|---:|---:|---:|---:|"]
        for n in ("full-human-review", "countersign", "no-spot-checks", "no-withdrawal", "countersign+canaries"):
            if n in s:
                v = s[n]
                L.append(f"| {n} | {v['minutes_per_week_before_drift']} | {v['escapes_per_week_before_drift']} | {v['minutes_per_week_after_drift']} | {v['escapes_per_week_after_drift']} |")
    return "\n".join(L)


def update_doc(ws: Workspace, result: dict) -> None:
    p = ws.root / "docs" / "MEASUREMENT.md"
    if not p.exists() or ws.inputs != ws.root:
        return
    text = p.read_text(encoding="utf-8")
    if START in text and END in text:
        head, rest = text.split(START, 1)
        p.write_text(head + START + "\n" + render_numbers(ws, result) + "\n" + END + rest.split(END, 1)[1], encoding="utf-8")
