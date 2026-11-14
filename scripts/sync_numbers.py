#!/usr/bin/env python3
"""Keep the headline numbers in the docs equal to the files they come from.

Docs mark a number like this:  <!--n:history_cleared-->24<!--/n-->
`python3 scripts/sync_numbers.py` rewrites every marked span from the source files;
`python3 scripts/sync_numbers.py --check` exits 1 (and lists them) if any span is stale, so CI catches drift.
Every value below says where it comes from; nothing is typed by hand.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["README.md", "docs/CONCEPT_CARD.md", "docs/pitch/submission.md", "docs/pitch/qa-prep.md",
        "docs/pitch/deck.md", "docs/SCALING.md", "docs/MEASUREMENT.md", "docs/BENCHMARK.md", "docs/LESSONS.md",
        "docs/security/REDTEAM.md", "docs/PR_FLOW.md", "docs/pitch/video-script.md", "docs/pitch/live.md",
        "docs/tech-challenges/codex.md", "docs/tech-challenges/gemini.md", "docs/tech-challenges/nemotron.md"]
SPAN = re.compile(r"<!--n:([a-z0-9_]+)-->(.*?)<!--/n-->", re.S)


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def values() -> dict[str, str]:
    r = _json("measurement/results.json")["metrics"]
    v = lambda k: r[k]["value"] if isinstance(r[k], dict) and "value" in r[k] else r[k]  # noqa: E731
    h = _json("measurement/history/results.json")
    ci = h["modes"]["ci-credited"]
    mandate = re.search(r"^version:\s*['\"]?(\d+)", (ROOT / "mandate/messagepack.mandate.yaml").read_text(), re.M)
    # red team: every attack in tests/redteam/attacks.py; the strict xfails are the ones still getting through
    attacks_src = (ROOT / "tests/redteam/attacks.py").read_text()
    attack_ids = set(re.findall(r'^\s*\(\s*"([A-Z]+\d+[a-z]?)"', attacks_src, re.M))
    misses = re.search(r"KNOWN_MISSES\s*=\s*(\{[^}]*\}|set\(\))", (ROOT / "tests/redteam/test_redteam_attacks.py").read_text())
    open_ids = set(re.findall(r'"([A-Z]+\d+[a-z]?)"', misses.group(1))) if misses else set()
    checks = v("caught_by_checks_alone")
    signal = v("catch_by_signal")
    ledger = [json.loads(line) for line in (ROOT / "ledger/ledger.jsonl").read_text().splitlines() if line.strip()]
    out = {
        "history_prs": ci["n"],
        "history_cleared": ci["confusion"]["clean_cleared"] + ci["confusion"]["escape_cleared"],
        "history_routed": ci["routed_to_humans"],
        "history_escapes": ci["escapes"],
        "history_escapes_cleared": ci["confusion"]["escape_cleared"],
        "history_mandate": h["mandate"]["version"],
        "mandate_version": mandate.group(1) if mandate else "?",
        "seeded_total": checks["of"],
        "seeded_caught_by_checks": checks["caught"],
        "seeded_reviewed": signal["of"],
        "seeded_reviewer_on_line": signal["reviewer_on_planted_line"],
        "redteam_total": len(attack_ids),
        "redteam_stopped": len(attack_ids - open_ids),
        "redteam_open": len(open_ids),
        "signoffs": v("signoffs"),
        "ledger_entries": len(ledger),
        "share_routed_real_pct": round(100 * v("share_routed_to_humans")),
    }
    out.update(_more(r, v, ci))
    return {k: str(x) for k, x in out.items()}


def _check(change: str, cid: str) -> dict:
    facts = _json(f"evidence/{change}/facts.json")
    return next((c for c in facts["checks"] if c["id"] == cid), {})


def _k(n: float) -> int:
    return round(n / 1000)


def _more(r: dict, v, ci: dict) -> dict:
    """Headline numbers that recur across the docs, beyond the replay/seeded/red-team core."""
    out: dict = {}
    # the history replay: share routed, rule-of-three upper bound on the escape rate among the cleared
    cleared = ci["confusion"]["clean_cleared"] + ci["confusion"]["escape_cleared"]
    out["history_routed_pct"] = round(100 * ci["routed_to_humans"] / ci["n"])
    out["history_cleared_upper_pct"] = int(300 / cleared) if cleared else "?"
    # seeded set: the one-line bugs (-mutK), what checks alone caught, and what got past every check
    checks = v("caught_by_checks_alone")
    det = checks["detail"]
    bugs = [c for c in det if re.search(r"-mut\d+$", c)]
    out["seeded_bugs"] = len(bugs)
    out["seeded_bugs_caught_by_checks"] = sum(det[c] != "no check failed" for c in bugs)
    out["seeded_injections"] = sum(c.endswith("-inject") for c in det)
    survivors = [c for c in det if det[c] == "no check failed"]
    out["seeded_survivors"] = len(survivors)
    plf = v("planted_line_flagged")
    out["seeded_survivors_flagged"] = plf["panel_on_test_survivors"]["flagged"]
    out["seeded_survivors_flagged_new"] = plf["panel_on_test_survivors"]["flagged_new_at_line"]
    nem = plf["per_reviewer"]["nemotron"]
    out["nemotron_survivors_flagged"] = len(nem["flagged_test_survivors"])
    out["nemotron_survivors_reviewed"] = len(nem["reviewed_test_survivors"])
    # the seven real changes
    real = [c for c in _json("measurement/results.json")["changes"] if not c.get("mutant") and not c.get("benchmark") and not c["change"].startswith("var-")]
    agent = [c for c in real if not c["change"].startswith("up-")]
    human = ("ask", "block")
    out["real_changes"] = len(real)
    out["real_routed"] = sum(c["tier"] in human for c in real)
    out["agent_changes"] = len(agent)
    out["agent_routed"] = sum(c["tier"] in human for c in agent)
    # reading-model minutes (simulated), per change and in total
    for ch, t in v("time_per_change").items():
        key = ch.replace("-", "")
        out[f"pack_min_{key}"] = round(t["with_pack_min"])
        out[f"read_min_{key}"] = round(t["full_read_min"])
    out["review_min_full"] = round(v("human_minutes_full_read"))
    out["review_min_pack"] = round(v("human_minutes_with_pack"))
    # reviewers: verified findings, Codex's misses, the owner's ratings, routing overrides
    fpr = v("findings_per_reviewer")
    for rv in ("claude", "nemotron", "codex"):
        out[f"{rv}_verified"] = fpr[rv]["verified"]
    out["nemotron_rejected"], out["nemotron_refusals"] = fpr["nemotron"]["rejected"], fpr["nemotron"]["refusals"]
    nem_plf = v("planted_line_flagged")["per_reviewer"]["nemotron"]
    out["nemotron_seeded_flagged"], out["nemotron_seeded_of"] = nem_plf["flagged"], nem_plf["of_reviewed"]
    out["codex_missed_majors"] = v("reviewer_cross_check")["codex"]["missed_others_verified_major"]
    far = v("findings_accepted_rate")
    for rv in ("claude", "nemotron"):
        out[f"{rv}_accepted"], out[f"{rv}_rated"] = far[rv]["accepted"], far[rv]["rated"]
    ov = v("tier_overrides")
    out["owner_overrode"], out["owner_overrode_of"] = ov["overrode"], ov["of"]
    met = tot = 0
    for ch in [c["change"] for c in agent]:
        vs = [x["verdict"] for x in _json(f"reviews/{ch}/codex.json").get("requirement_verdicts", [])]
        met, tot = met + vs.count("met"), tot + len(vs)
    out["codex_v2_met"], out["codex_v2_clauses"] = met, tot
    # 2234: the new tests, fail-without-fix and mutation testing (evidence/2234/facts.json)
    fwf = _check("2234", "tests.fail_without_fix")
    out["t2234_new_tests"] = fwf["new_total"]
    out["t2234_fail_without_fix"] = fwf["new_failed"]
    out["t2234_pass_without_fix"] = fwf["new_total"] - fwf["new_failed"]
    ex = _check("2234", "tests.execution_fail_without_fix")
    out["t2234_runtime_new"], out["t2234_runtime_fail_without_fix"] = ex["new_total"], ex["new_failed"]
    fs = _check("2234", "tests.full_suite")
    out["t2234_suite_passed"], out["t2234_suite_total"] = fs["passed"], fs["total"]
    mut = _check("2234", "tests.mutation")["mutants"]
    out["t2234_mutants"] = len(mut)
    out["t2234_mutants_killed"] = sum(m["outcome"] == "killed" for m in mut)
    out["t2234_mutants_survived"] = sum(m["outcome"] == "survived" for m in mut)
    # model tokens (measurement/costs.yaml): Gemini's adjudication, Nemotron per review call, all reviewers per change
    # every run row is a one-line JSON flow mapping, so no YAML parser is needed (the CI check stays dependency-free)
    runs = [json.loads(m) for m in re.findall(r"^\s*-\s*(\{.*\})\s*$", (ROOT / "measurement/costs.yaml").read_text(), re.M)]
    gem = [x for x in runs if x["provider"] == "google"]
    out["gemini_adjudicated"] = len({x["change"] for x in gem})
    gem_real = sorted({x["change"] for x in gem if not x["change"].startswith("var-")})
    out["gemini_real_changes"] = " and ".join([", ".join(gem_real[:-1]), gem_real[-1]] if len(gem_real) > 1 else gem_real)
    out["gemini_variants"] = len({x["change"] for x in gem if x["change"].startswith("var-")})
    out["gemini_tokens"] = f'{sum(x["tokens_in"] + x["tokens_out"] for x in gem):,}'
    out["gemini_usd"] = f'{sum(x["usd"] for x in gem):.2f}'
    out["gemini_calls"] = len(gem)
    gtok = [x["tokens_in"] + x["tokens_out"] for x in gem]
    out["gemini_call_tokens_min"], out["gemini_call_tokens_max"] = f"{min(gtok):,}", f"{max(gtok):,}"
    out["gemini_call_usd_min"] = f'{min(x["usd"] for x in gem):.3f}'
    out["gemini_call_usd_max"] = f'{max(x["usd"] for x in gem):.3f}'
    # Codex: the logged runs (docs/CODEX_LOG.md token counts, copied into costs.yaml)
    cdx = [x for x in runs if x["provider"] == "openai"]
    out["codex_runs"] = len(cdx)
    out["codex_tokens_k"] = f'{_k(sum(x["tokens_in"] + x["tokens_out"] for x in cdx)):,}'
    files = {}
    for x in runs:
        ch = x.get("change")
        if x["provider"] == "nvidia" and ch and "repair" not in x["purpose"]:
            fp = ROOT / f"evidence/{ch}/facts.json"
            nf = json.loads(fp.read_text())["diff"].get("files", 0) if fp.exists() else 0
            files.setdefault(ch, []).append((x["tokens_in"] + x["tokens_out"], nf))
    multi = [t for calls in files.values() for t, nf in calls if nf >= 2]  # "from 2 files to 237"
    out["nemotron_call_min_k"], out["nemotron_call_max_k"] = _k(min(multi)), _k(max(multi))
    seeded = [t for ch, calls in files.items() if re.search(r"-(mut\d+|inject|sec\d+|deps)$", ch) for t, _ in calls]
    out["nemotron_seeded_min_k"], out["nemotron_seeded_max_k"] = _k(min(seeded)), _k(max(seeded))
    out.update(_bench())
    tpc = v("model_tokens_per_change")
    ag = [tpc[c["change"]] for c in agent if c["change"] in tpc]
    up = [tpc[c["change"]] for c in real if c["change"].startswith("up-") and c["change"] in tpc]
    out["tokens_agent_min_k"], out["tokens_agent_max_k"] = _k(min(ag)), _k(max(ag))
    out["tokens_control_min_k"], out["tokens_control_max_k"] = _k(min(up)), _k(max(up))
    return out


def _bench() -> dict:
    """Same-issue benchmark (evidence/var-*): fix variants generated by our own agents, plus the hand-seeded
    hidden downgrades. A downgrade counts as flagged when a blind review finding that replay verified
    (measurement/results.json `why`) quotes code within 3 lines of the seeded line (evidence/var-*/facts.json)."""
    rows = {c["change"]: c for c in _json("measurement/results.json")["changes"] if c["change"].startswith("var-")}
    facts = {ch: _json(f"evidence/{ch}/facts.json") for ch in rows}
    downs = {ch: f["seeded"] for ch, f in facts.items() if (f.get("seeded") or {}).get("kind") == "hidden_downgrade"}
    flagged = suite_caught = 0
    for ch, s in downs.items():
        verified = {w.split(" ", 2)[2] for w in rows[ch]["why"] if w.startswith("verified finding ")}
        hit = False
        for rv in sorted((ROOT / "reviews" / ch).glob("*.json")):
            if rv.name.startswith("adjudication"):
                continue
            r = json.loads(rv.read_text())
            for f in r.get("findings", []):
                if f"{r['reviewer']}:{f['id']}" in verified and any(
                        e.get("kind") == "code" and e.get("file") == s["file"] and abs(int(e.get("line", -99)) - s["line"]) <= 3
                        for e in f.get("evidence", [])):
                    hit = True
        flagged += hit
        suite_caught += next((c["status"] for c in facts[ch]["checks"] if c["id"] == "tests.runtime_suite"), "") == "fail"
    return {"bench_variants": len(rows), "bench_agent_variants": len(rows) - len(downs),
            "bench_downgrades": len(downs), "bench_downgrades_flagged": flagged,
            "bench_downgrades_tests_caught": suite_caught}


def sync(check: bool) -> int:
    vals, stale, unknown = values(), [], []
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text()

        def repl(m: re.Match) -> str:
            key, old = m.group(1), m.group(2)
            if key not in vals:
                unknown.append(f"{rel}: {key}")
                return m.group(0)
            if old != vals[key]:
                stale.append(f"{rel}: {key} {old!r} -> {vals[key]!r}")
            return f"<!--n:{key}-->{vals[key]}<!--/n-->"

        new = SPAN.sub(repl, text)
        if new != text and not check:
            p.write_text(new)
    for u in unknown:
        print(f"unknown key: {u}", file=sys.stderr)
    for s in stale:
        print(("stale: " if check else "updated: ") + s)
    if check and (stale or unknown):
        return 1
    return 1 if unknown else 0


if __name__ == "__main__":
    if "--print" in sys.argv:
        print(json.dumps(values(), indent=2))
        sys.exit(0)
    sys.exit(sync("--check" in sys.argv))
