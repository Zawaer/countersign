#!/usr/bin/env python3
"""Build the judge-facing static site (site/*.html) from the repo's own files.

Stdlib only, no network. Every number on the pages is read here, at build time, from:
  measurement/results.json            replay over the four changes and the seeded defects
  measurement/mutants/mutants.json    the seeded-defect catalogue
  evidence/<change>[-mutK]/facts.json build and test results
  reviews/<change>/*.json             the AI reviews (v1 and v2)
  packs/<change>/pack.json, pack.html the evidence packs (copied to site/packs/)
  measurement/history/results.json    historical replay over real upstream PRs (+ labels.yaml)
  ledger/ledger.jsonl, keys/*.pub     the signed ledger, for the in-browser tamper check
  mandate/messagepack.mandate.yaml    areas, owners and clearance rights
  docs/pitch/deck.md                  the pitch deck

Run:  python3 site/build.py      (then: python3 -m http.server 3472 --bind 0.0.0.0 --directory site)
Missing inputs never become invented numbers: the page says "not recorded yet" instead.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REPO_URL = "https://github.com/Zawaer/countersign"
BLOB = REPO_URL + "/blob/main/"
UPSTREAM = "https://github.com/MessagePack-CSharp/MessagePack-CSharp"
CHANGES = ["2234", "2283", "2129", "2297"]  # order shown on the pages (the story change first)
HUMAN_TIERS = {"ask", "block"}


# ---------------------------------------------------------------- helpers

def rj(rel: str):
    p = ROOT / rel
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def rt(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except OSError:
        return ""


def e(s) -> str:
    return html.escape(str(s), quote=True)


def src(rel: str, label: str | None = None) -> str:
    """A link to a repo file: every number on the page cites one."""
    return f'<a class="src" href="{BLOB}{e(rel)}">{e(label or rel)}</a>'


def code(s) -> str:
    return f'<code{" class=nwc" if len(str(s)) <= 28 else ""}>{e(s)}</code>'


def num(pattern: str, text: str | None, group: int = 1):
    m = re.search(pattern, text or "")
    return int(m.group(group)) if m else None


def short_test(name: str) -> str:
    return name.split(".")[-1]


TIER_GLYPH = {"silent": "✓", "notify": "✓", "ask": "?", "block": "✗"}
TIER_CLASS = {"silent": "ok", "notify": "ok", "ask": "warn", "block": "bad"}


def tier(t: str | None, owner: str | None = None) -> str:
    if not t:
        return '<span class="badge">not routed yet</span>'
    o = f" → {e(owner)}" if owner and t in HUMAN_TIERS else ""
    return f'<span class="badge {TIER_CLASS.get(t, "")}">{TIER_GLYPH.get(t, "")} {e(t.upper())}{o}</span>'


def status(s: str | None, word: str | None = None) -> str:
    s = s or "not run"
    cls = {"pass": "ok", "passed": "ok", "met": "ok", "fail": "bad", "failed": "bad", "not_met": "bad",
           "error": "warn", "cannot_determine": "warn"}.get(s, "")
    glyph = {"ok": "✓", "bad": "✗", "warn": "?"}.get(cls, "–")
    word = word or {"not_met": "not met", "cannot_determine": "can't tell"}.get(s, s)
    return f'<span class="st {cls}">{glyph} {e(word)}</span>'


def table(head: list[str], rows: list[list[str]], num_cols: tuple[int, ...] = (), cls: str = "stack") -> str:
    th = "".join(f'<th{" class=n" if i in num_cols else ""}>{h}</th>' for i, h in enumerate(head))
    labels = [re.sub(r"<[^>]+>", "", h) for h in head]
    trs = "".join("<tr>" + "".join(f'<td{" class=n" if i in num_cols else ""} data-label="{e(labels[i]) if i < len(labels) else ""}">{c}</td>'
                                   for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def git(*args) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


# ---------------------------------------------------------------- data

class Data:
    def __init__(self):
        self.results = rj("measurement/results.json") or {}
        self.metrics = self.results.get("metrics", {})
        self.catalogue = {m["id"]: m for m in (rj("measurement/mutants/mutants.json") or {}).get("mutants", [])}
        self.facts = {}
        for d in sorted((ROOT / "evidence").glob("*/facts.json")):
            self.facts[d.parent.name] = json.loads(d.read_text(encoding="utf-8"))
        self.packs = {c: rj(f"packs/{c}/pack.json") for c in CHANGES}
        self.history = rj("measurement/history/results.json")
        self.labels = parse_labels(rt("measurement/history/labels.yaml"))
        self.ledger = [json.loads(x) for x in rt("ledger/ledger.jsonl").splitlines() if x.strip()]
        self.pubkeys = {p.stem: p.read_text().strip() for p in sorted((ROOT / "keys").glob("*.pub"))}
        self.areas = parse_areas(rt("mandate/messagepack.mandate.yaml"))
        self.trust_cfg = parse_block(rt("mandate/messagepack.mandate.yaml"), "trust")
        self.reviews = {}
        for c in CHANGES:
            for p in sorted((ROOT / "reviews" / c).glob("*.json")):
                self.reviews[(c, p.stem)] = json.loads(p.read_text(encoding="utf-8"))
        self.mutants = self._mutants()

    def metric(self, key):
        m = self.metrics.get(key)
        return m.get("value") if isinstance(m, dict) else None

    def change_rows(self):
        """Real changes: results.json first, pack.json as fallback."""
        by = {r["change"]: r for r in self.results.get("changes", []) if not r.get("mutant")}
        out = []
        for c in CHANGES:
            p = self.packs.get(c) or {}
            r = by.get(c, {})
            out.append({"change": c, "tier": r.get("tier") or p.get("tier"), "owner": r.get("owner") or p.get("owner"),
                        "diff": p.get("diff") or (self.facts.get(c) or {}).get("diff", {}),
                        "reasons": [x["text"] for x in (p.get("card") or {}).get("reasons", [])],
                        "headline": (p.get("story") or {}).get("headline", ""), "score": r.get("score") or (p.get("risk") or {}).get("score")})
        return out

    def _mutants(self):
        rows = {r["change"]: r for r in self.results.get("mutants", [])}
        out = []
        for mid, f in self.facts.items():
            if "-mut" not in mid:
                continue
            m = f.get("mutation", {})
            cat = self.catalogue.get(mid, {})
            checks = {c["id"]: c for c in f.get("checks", [])}
            r = rows.get(mid, {})
            out.append({
                "id": mid, "of": mid.split("-mut")[0], "kind": m.get("kind") or cat.get("kind") or "",
                "file": m.get("file") or cat.get("file"), "line": m.get("line") or cat.get("line"),
                "before": m.get("before"), "after": m.get("after"),
                "description": m.get("description") or cat.get("description"), "effect": m.get("intended_effect"),
                "checks": [{"id": c["id"], "status": c["status"], "summary": c.get("summary", ""),
                            "failing": [short_test(t["name"]) for t in c.get("tests", []) if t.get("outcome") == "failed"]}
                           for c in f.get("checks", [])],
                "caught_by_tests": m.get("caught_by") or [], "caught_by_full": m.get("caught_by_full_suite") or [],
                "any_check": bool(m.get("caught_by_any_deterministic_check")) or any(c["status"] == "fail" for c in checks.values()),
                "tier": r.get("tier"), "original_tier": r.get("original_tier"), "attributable": r.get("attributable", []),
                "routed": r.get("routed_to_human"), "reviews": r.get("reviews"),
                "owner": (self.packs.get(mid.split("-mut")[0]) or {}).get("owner"),
            })
        order = {c: i for i, c in enumerate(CHANGES)}
        return sorted(out, key=lambda x: (order.get(x["of"], 9), int(x["id"].split("-mut")[1])))


def parse_labels(text: str) -> dict:
    """Minimal reader for measurement/history/labels.yaml: pr -> first evidence line."""
    out, pr, in_esc = {}, None, False
    for line in text.splitlines():
        if re.match(r"^escapes:", line):
            in_esc = True
            continue
        if in_esc and re.match(r"^\S", line):
            in_esc = False
        if not in_esc:
            continue
        m = re.match(r"\s+- pr: (\d+)", line)
        if m:
            pr = int(m.group(1))
            continue
        m = re.match(r'\s+- "(.*)"\s*$', line)
        if m and pr and pr not in out:
            out[pr] = m.group(1).replace("\\'", "'")
    return out


def parse_areas(text: str) -> list[dict]:
    areas, cur, inside = [], None, False
    for line in text.splitlines():
        if line.startswith("areas:"):
            inside = True
            continue
        if inside and line and not line.startswith(" "):
            break
        if not inside:
            continue
        m = re.match(r"^  ([\w-]+):\s*$", line)
        if m:
            cur = {"name": m.group(1)}
            areas.append(cur)
            continue
        m = re.match(r"^    (\w+):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    return areas


def parse_block(text: str, name: str) -> dict:
    out, inside = {}, False
    for line in text.splitlines():
        if line.startswith(f"{name}:"):
            inside = True
            continue
        if inside and line and not line.startswith(" "):
            break
        m = re.match(r"^  (\w+):\s*([^#]*)", line) if inside else None
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


# ---------------------------------------------------------------- numbers used on several pages

def numbers(D: Data) -> dict:
    rows = D.change_rows()
    n = {"changes": len(rows),
         "cleared": sum(r["tier"] not in HUMAN_TIERS for r in rows if r["tier"]),
         "ask": sum(r["tier"] == "ask" for r in rows), "block": sum(r["tier"] == "block" for r in rows)}
    cba = D.metric("caught_by_checks_alone") or {}
    n["mut_total"] = cba.get("of") or len(D.mutants) or None
    n["mut_checks"] = cba.get("caught")
    srh = D.metric("seeded_routed_to_human_before_review") or {}
    n["mut_routed"], n["mut_attrib"] = srh.get("routed"), srh.get("attributable")
    hm = ((D.history or {}).get("modes") or {}).get("ci-credited")
    if hm:
        n.update(h_n=hm["n"], h_esc=hm["escapes"], h_esc_cleared=len(hm["escapes_cleared"]), h_routed=hm["routed_to_humans"],
                 h_cleared=hm["confusion"]["clean_cleared"] + hm["confusion"]["escape_cleared"])
    # Codex: first pass vs second pass (with the deterministic facts)
    def tally(stem):
        met = tot = fnd = 0
        for c in CHANGES:
            r = D.reviews.get((c, stem))
            if not r:
                return None
            v = [x["verdict"] for x in r.get("requirement_verdicts", [])]
            met += v.count("met")
            tot += len(v)
            fnd += len(r.get("findings", []))
        return {"met": met, "of": tot, "findings": fnd}
    n["codex_v1"], n["codex_v2"], n["claude_v2"] = tally("codex.v1"), tally("codex"), tally("claude")
    cc = (D.metric("reviewer_cross_check") or {}).get("codex") or {}
    n["codex_missed_major"] = cc.get("missed_others_verified_major")
    return n


def hero_line(n: dict) -> str:
    parts = [f'<b>{n["changes"]} agent-written changes: {n["cleared"]} cleared, {n["ask"]} routed to their owner, {n["block"]} blocked</b>; '
             "it caught one that passes CI and fixes the wrong bug."]
    if n.get("mut_checks") is not None:
        parts.append(f' <b>{n["mut_checks"]} of {n["mut_total"]}</b> seeded one-line bugs failed a check.')
    if n.get("h_esc") is not None:
        parts.append(f' Replayed on {n["h_n"]} real upstream PRs, it would have cleared <b>{n["h_esc_cleared"]} of the {n["h_esc"]}</b> that later had to be reverted or fixed.')
    return "".join(parts)


def hero_text(n: dict) -> str:
    return re.sub(r"<[^>]+>", "", hero_line(n))


# ---------------------------------------------------------------- shared page shell

NAV = [("index.html", "Overview"), ("attack.html", "Sneak a bug past it"), ("tour.html", "Guided tour"),
       ("pitch.html", "Pitch"), ("packs/2234/pack.html", "Evidence pack")]


def page(fname: str, title: str, body: str, js: str = "", cls: str = "", desc: str = "") -> str:
    depth = fname.count("/")
    up = "../" * depth
    nav = "".join(f'<a href="{up}{h}"{" aria-current=page" if h == fname else ""}>{e(t)}</a>' for h, t in NAV)
    sha = git("rev-parse", "--short", "HEAD")
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'Countersign: AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it cannot, and a named human countersigns the rest.')}">
<link rel="stylesheet" href="{up}style.css">
<script>try{{var t=localStorage.getItem("cs-theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
</head><body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar">
<a class="mark" href="{up}index.html"><span class="sig">✓</span>Countersign</a>
<nav aria-label="Site">{nav}</nav>
<button class="theme" type="button" aria-label="Switch light or dark theme" onclick="csTheme()">◐</button>
</div></header>
<main id="main">{body}</main>
<footer class="foot"><div class="wrap">
<p>Junction 2026 · Tieto: Earned Trust in AI Code · <a href="{REPO_URL}">{REPO_URL.replace('https://', '')}</a></p>
<p>Generated by {src('site/build.py')} from the repo's own files{f' at commit <code>{e(sha)}</code>' if sha else ''}, {e(built)}. Every number links to the file it was read from.</p>
</div></footer>
<script>function csTheme(){{var d=document.documentElement,c=d.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),n=c==="dark"?"light":"dark";d.dataset.theme=n;try{{localStorage.setItem("cs-theme",n)}}catch(_){{}}}}</script>
{f'<script>{js}</script>' if js else ''}
</body></html>
"""


# ---------------------------------------------------------------- the 2234 story (used on index, tour, pitch)

def story_2234(D: Data, compact: bool = False) -> str:
    f = D.facts.get("2234") or {}
    p = D.packs.get("2234") or {}
    ch = {c["id"]: c for c in f.get("checks", [])}
    tgt, full, fwf, efwf = (ch.get(k, {}) for k in ("tests.targeted", "tests.full_suite", "tests.fail_without_fix", "tests.execution_fail_without_fix"))
    t_pass, t_new = num(r"(\d+) passed", tgt.get("summary")), num(r"\((\d+) new tests", tgt.get("summary"))
    s_pass, s_tot = num(r"(\d+) passed", full.get("summary")), num(r"(\d+) tests", full.get("summary"))
    fwf_tests = fwf.get("tests", [])
    still_pass = sum(t["outcome"] == "passed" for t in fwf_tests)
    e_tests = efwf.get("tests", [])
    e_fail = sum(t["outcome"] == "failed" for t in e_tests)

    codex = D.reviews.get(("2234", "codex")) or {}
    cv = codex.get("requirement_verdicts", [])
    c_met = sum(v["verdict"] == "met" for v in cv)
    n1 = next((v for v in cv if v["req"].endswith("N1")), None)
    others = [r for r in (p.get("panel") or {}).get("rows", []) if r["reviewer"] not in ("claude", "codex")]
    other_line = ""
    for r in others:
        vs = list(r.get("verdicts", {}).values())
        other_line += f'<li>{status("met")} {e(r["reviewer"].capitalize())} ({e(r.get("vendor", ""))}) also says met on {vs.count("met")} of {len(vs)}</li>'

    find = next((x for x in p.get("findings", []) if x.get("reviewer") == "claude" and x.get("id") == "C1"), None)
    ev_html = ""
    if find:
        for ev in find.get("evidence", []):
            if ev["kind"] == "code":
                rev = ev["rev"] if len(ev["rev"]) < 12 else ev["rev"][:8]
                ok = "verified" if ev.get("verified") else "rejected"
                ev_html += (f'<li><span class="st {"ok" if ev.get("verified") else "bad"}">{"✓" if ev.get("verified") else "✗"} {ok}</span> '
                            f'<code>{e(ev["file"].split("/")[-1])}:{ev["line"]} @{e(rev)}</code><pre class="q">{e(ev["quote"])}</pre></li>')
    card_c = f"""
<li>{status('fail')} <b>Fixes a different bug than the issue reports.</b> The 3.1.1 regression in #2234 comes from an upstream commit that is not in this branch's base; the agent fixed another, older crash.</li>
<li>{status('fail')} Revert the source, rerun the new tests: <b>{still_pass} of {len(fwf_tests)}</b> analyzer tests still pass on the old code{f', and <b>{len(e_tests) - e_fail} of {len(e_tests)}</b> runtime test results' if e_tests else ''}. They don't test the change.</li>"""
    ev_block = "" if compact else f'<p class="ev-h">Claude&#39;s finding C1; the engine re-read each cited line at that commit:</p><ul class="ev">{ev_html}</ul>'
    return f"""
<ol class="story{' compact' if compact else ''}" aria-label="Change 2234 in three steps">
<li class="card">
 <div class="card-h"><span class="step">1 · CI</span>{status('pass')}</div>
 <ul class="rows">
  <li>{status(ch.get('build', {}).get('status'))} Build: {e(ch.get('build', {}).get('summary', 'not run'))}</li>
  <li>{status(tgt.get('status'))} New tests: {t_pass} of {t_new} pass</li>
  <li>{status(full.get('status'))} Generator suite: {s_pass} of {s_tot} pass</li>
 </ul>
 <p class="foot-note">{src('evidence/2234/facts.json')}</p>
</li>
<li class="card">
 <div class="card-h"><span class="step">2 · AI reviewer</span>{status('pass')}</div>
 <ul class="rows">
  <li>{status('met')} Codex (OpenAI): <b>{c_met} of {len(cv)}</b> requirement clauses met, {len(codex.get('findings', []))} findings</li>
  {other_line}
 </ul>
 {f'<blockquote>“{e(n1["confidence_basis"])}”</blockquote>' if n1 and not compact else ''}
 <p class="foot-note">{src('reviews/2234/codex.json')}</p>
</li>
<li class="card bad">
 <div class="card-h"><span class="step">3 · Countersign</span>{tier(p.get('tier'), p.get('owner'))}</div>
 <ul class="rows">{card_c}</ul>
 {ev_block}
 <p class="foot-note">{src('packs/2234/pack.json')} · <a href="packs/2234/pack.html">open the pack</a></p>
</li>
</ol>"""


# ---------------------------------------------------------------- index.html

def build_index(D: Data, n: dict) -> str:
    rows = D.change_rows()
    ch_rows = [[f'<a href="packs/{r["change"]}/pack.html"><code>{r["change"]}</code></a>',
                f'{r["diff"].get("files", "?")} files, +{r["diff"].get("insertions", "?")} −{r["diff"].get("deletions", "?")}',
                tier(r["tier"], r["owner"]), e(r["reasons"][0] if r["reasons"] else "")] for r in rows]
    v1, v2, cl = n.get("codex_v1"), n.get("codex_v2"), n.get("claude_v2")
    diffs = [
        ("It caught a change that is green everywhere and fixes the wrong bug.",
         "Change 2234 passes its build, its new tests and the full suite, and a reviewer says every requirement is met. "
         "Countersign routes it to its owner with the reason: the reported regression isn't on this base.",
         '<a href="tour.html">Walk through it</a>'),
        ("Tests have to prove they test something.",
         "Fail-without-fix: we revert the source, keep the new tests and run them. A test that still passes on the old code doesn't count as evidence for the change.",
         src("evidence/2234/facts.json", "2234 facts")),
        ("One reviewer can never clear a change.",
         (f"We measured it: given passing test results, Codex went from {v1['met']} of {v1['of']} clauses met to <b>{v2['met']} of {v2['of']}</b>, "
          f"with {v2['findings']} findings. On the same changes Claude raised {cl['findings']}."
          if v1 and v2 and cl else "Given passing tests, one reviewer said met to everything (Codex v2).")
         + " So a clause is proven only when every reviewer agrees with verified citations.",
         src("docs/FAILURE_MODES.md", "failure mode R1")),
        ("We measure what gets through.",
         (f"{n['mut_total']} single-line bugs planted in the agents' branches: {n['mut_checks']} failed a check, "
          f"{n['mut_routed']} reach a human before any AI review. " if n.get("mut_checks") is not None else "")
         + (f"{n['h_n']} real upstream PRs replayed: {n['h_esc_cleared']} of {n['h_esc']} later escapes would have been cleared." if n.get("h_n") else ""),
         '<a href="attack.html">Try it yourself</a>'),
        ("Trust is withdrawn automatically after an escape.",
         f"Each area's clearance right lives in the signed mandate. An escape traced to an AI-cleared change drops the area to "
         f"<code>{e(D.trust_cfg.get('escape_cap', 'ask'))}</code> until {e(D.trust_cfg.get('restore_after_agreeing_spotchecks', '?'))} spot-checks in a row agree.",
         src("mandate/messagepack.mandate.yaml", "mandate")),
    ]
    diff_html = "".join(f'<li><h3>{t}</h3><p>{b}</p><p class="more">{l}</p></li>' for t, b, l in diffs)
    stats = []
    stats.append((f'{n["cleared"]} of {n["changes"]}', "agent-written changes cleared by the AI. "
                  f'{n["ask"]} went to their owner, {n["block"]} were blocked, each with the rule that decided it.', "measurement/results.json"))
    if n.get("mut_checks") is not None:
        stats.append((f'{n["mut_checks"]} of {n["mut_total"]}', "seeded one-line bugs failed a build or test check. "
                      f'Before any AI review, {n["mut_routed"]} of {n["mut_total"]} would reach a human; the other {n["mut_total"] - n["mut_routed"]} are shown, not hidden.',
                      "measurement/results.json"))
    if n.get("h_n"):
        stats.append((f'{n["h_esc_cleared"]} of {n["h_esc"]}', f'real escapes (later reverted or fixed) among {n["h_n"]} upstream MessagePack PRs '
                      f'that the signed mandate would have let the AI clear. It routed {n["h_routed"]} of {n["h_n"]} to a human.',
                      "measurement/history/results.md"))
    stats_html = "".join(f'<div class="stat"><div class="big">{e(a)}</div><div>{b} {src(c, "source")}</div></div>' for a, b, c in stats)
    body = f"""
<section class="wrap hero">
<p class="eyebrow">Junction 2026 · Tieto: Earned Trust in AI Code</p>
<h1>AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.</h1>
<p class="lead">{hero_line(n)}</p>
</section>
<section class="wrap" aria-labelledby="s2234">
<h2 id="s2234" class="h-sm">Change 2234: green everywhere, wrong bug</h2>
{story_2234(D)}
<p class="ctas"><a class="btn primary" href="attack.html">Try to sneak a bug past it</a><a class="btn" href="tour.html">Guided tour, 8 steps</a><a class="btn" href="pitch.html">Pitch deck</a></p>
</section>
<section class="wrap" aria-labelledby="snum"><h2 id="snum">The numbers</h2><div class="stats">{stats_html}</div></section>
<section class="wrap" aria-labelledby="sdiff"><h2 id="sdiff">What it does that a reviewer bot doesn't</h2><ol class="diffs">{diff_html}</ol></section>
<section class="wrap" aria-labelledby="sall"><h2 id="sall">All four agent-written changes</h2>
<p class="prose">The four branches Tieto provided, run end to end. None is cleared: a repo with no track record starts strict. Each row opens its evidence pack.</p>
{table(['Change', 'Size', 'Tier', 'Deciding reason'], ch_rows, cls='stack')}
<p class="foot-note">{src('measurement/results.json')} · {src('packs/2234/pack.json', 'packs/*/pack.json')}</p></section>
<section class="wrap" aria-labelledby="slim"><h2 id="slim">Where it stops</h2>
<ul class="prose list">
<li>It can't judge intent: whether this is the change the product needs.</li>
<li>It is only as good as the requirement text. Ours are placeholders derived from the upstream issues (<code>official: false</code>).</li>
<li>Checks ran on net8.0 / Linux only; other targets are listed as not checked in every pack.</li>
<li>Reviewers share training data, so their independence is partial; seeded bugs measure what they miss together.</li>
<li>Spot-checks, escapes and review minutes in the trust demo are simulated, and labelled so.</li>
</ul></section>
"""
    return page("index.html", "Countersign: earned trust in AI code review", body, desc=hero_text(n))


# ---------------------------------------------------------------- attack.html

EXPLAIN = {
    "2234-mut2": ("No test has <b>fields</b> with mixed int and string keys; the agent's new tests cover properties. "
                  "Both reviewers read the <code>continue</code> as correct.",
                  "A test for the field path. Until one exists, the pack lists this guard under failure mode A3 (untested guard), "
                  "and the change still goes to its owner for its other reasons."),
    "2283-mut1": ("The guard only matters for a type that comes from a project reference (a <code>CompilationReference</code>). "
                  "No test compiles one, so deleting the guard breaks nothing. Both reviewers read the line as correct.",
                  "Only this kind of seeded-defect run exposes it. On facts alone the change would sit at <code>notify</code>, a tier the AI may clear. "
                  "The real 2283 still goes to Toivo, but for a different finding (a silenced warning), not for this bug."),
    "2283-mut5": ("The new tests cover a metadata member with no <code>[Key]</code> (MsgPack004). None covers the keyless-property "
                  "path this line handles (MsgPack003), so the unguarded index is never reached.",
                  "A test with a metadata property that has no key. On facts alone this one would also sit at <code>notify</code>."),
}


def build_attack(D: Data, n: dict) -> str:
    muts = D.mutants
    data = []
    for m in muts:
        failing = [c for c in m["checks"] if c["status"] == "fail"]
        data.append({**m, "failed": [c["id"] for c in failing], "explain": EXPLAIN.get(m["id"])})
    picks = "".join(
        f'<button type="button" class="pick" data-id="{e(m["id"])}" aria-pressed="false">'
        f'<code>{e(m["id"])}</code><span>{e(m["kind"])}</span></button>' for m in muts)
    hist = build_history_section(D, n)
    cba_line = (f'{n["mut_checks"]} of {n["mut_total"]} failed a build or test check; {n["mut_total"] - n["mut_checks"]} got through every test. '
                if n.get("mut_checks") is not None else "")
    body = f"""
<section class="wrap hero small">
<p class="eyebrow">Attack 1 of 2</p>
<h1>Try to sneak a bug past it</h1>
<p class="lead prose">We planted {len(muts)} one-line bugs into the agents' own branches, the kind a careless or hostile agent could slip in: a removed guard, an inverted condition, a swallowed warning, a wrong key kind, an off-by-one. Pick one. You see the line you "sneaked in", then what the pipeline did with it. {cba_line}{src('measurement/mutants/mutants.json', 'catalogue')}</p>
</section>
<section class="wrap attack">
<div class="picker" role="group" aria-label="Seeded defects">{picks}</div>
<div id="verdict" class="verdict" aria-live="polite"><p class="muted">Pick a seeded bug above.</p></div>
</section>
<section class="wrap" aria-labelledby="sall"><h2 id="sall">All {len(muts)} at a glance</h2>
{table(['Seeded bug', 'Kind', 'Failed check', 'Tier before AI review', 'Original'],
       [[f'<code>{e(m["id"])}</code>', e(m["kind"]), (", ".join(code(c) for c in d["failed"]) or '<span class="st warn">– none failed</span>'),
         tier(m["tier"], m["owner"]), tier(m["original_tier"])] for m, d in zip(muts, data)], cls='stack')}
<p class="foot-note">Tier before AI review = facts only, no reviewers, from {src('measurement/results.json')} (<code>mutants</code>). "Original" is the unmutated change routed the same way. AI reviews of the seeded bugs: {e(muts[0]["reviews"] if muts and isinstance(muts[0]["reviews"], str) else "see results.json")}.</p>
</section>
{hist}
<section class="wrap"><h2>Attack 2: forge the record</h2><p class="prose">Every sign-off is an Ed25519 signature in a hash-chained ledger. <a href="tour.html#6">Edit a ledger line in your browser and watch the check fail.</a></p></section>
"""
    js = "var MUTS=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";" + ATTACK_JS
    return page("attack.html", "Try to sneak a bug past Countersign", body, js=js)


ATTACK_JS = r"""
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var TG={silent:"✓",notify:"✓",ask:"?",block:"✗"},TC={silent:"ok",notify:"ok",ask:"warn",block:"bad"};
function tier(t,o){if(!t)return'<span class="badge">not routed yet</span>';return'<span class="badge '+TC[t]+'">'+TG[t]+" "+t.toUpperCase()+((o&&(t=="ask"||t=="block"))?" → "+esc(o):"")+"</span>"}
function st(s){var c=s=="pass"?"ok":s=="fail"?"bad":"warn";return'<span class="st '+c+'">'+(c=="ok"?"✓":c=="bad"?"✗":"?")+" "+esc(s)+"</span>"}
var NAMES={"build":"Build","tests.targeted":"The change's own new tests","tests.full_suite":"Full generator test suite","tests.execution_full_suite":"Runtime (execution) test suite","tests.targeted.execution":"New runtime tests"};
function show(id){
 var m=MUTS.filter(function(x){return x.id==id})[0];if(!m)return;
 document.querySelectorAll(".pick").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.id==id)});
 var caught=m.failed.length>0, h="";
 h+='<div class="diffbox"><div class="diff-h"><code>'+esc(m.file)+":"+esc(m.line)+'</code><span class="muted">'+esc(m.kind)+"</span></div>";
 if(m.before!=null){h+='<pre class="diff"><span class="del">- '+esc(m.before.trim())+'</span><span class="add">+ '+esc(m.after.trim())+"</span></pre>"}
 h+='<p class="what">'+esc(m.description)+(m.effect?'. <span class="muted">Effect: '+esc(m.effect)+"</span>":"")+"</p></div>";
 h+='<ol class="steps">';
 m.checks.forEach(function(c){
  var t=c.failing.length?'<div class="tests">'+c.failing.slice(0,4).map(function(x){return"<code>"+esc(x)+"</code>"}).join(" ")+(c.failing.length>4?" +"+(c.failing.length-4)+" more":"")+"</div>":"";
  h+="<li>"+st(c.status)+" <b>"+esc(NAMES[c.id]||c.id)+"</b> <span class='muted'>"+esc(c.summary)+"</span>"+t+"</li>"});
 h+="<li>"+tier(m.tier,m.owner)+" <b>Routing before any AI review</b> <span class='muted'>"+(m.attributable&&m.attributable.length?"because of this bug: "+esc(m.attributable.join(", ")):"same tier as the unmutated change ("+esc(m.original_tier)+"): nothing new fired")+"</span></li></ol>";
 var verdict;
 if(caught&&m.attributable&&m.attributable.length){verdict='<div class="banner bad"><b>Caught.</b> '+esc(m.failed.join(" and "))+" failed, so the mandate routes it to "+tier(m.tier,m.owner)+". "+esc(m.owner)+" is asked, and the failing test names are in the pack.</div>"}
 else if(caught){verdict='<div class="banner warn"><b>Caught by the tests, not by a rule.</b> '+esc(m.failed.join(" and "))+" failed, but only a suite the area's mandate doesn't require, so the tier stays "+tier(m.tier,m.owner)+" for the change's other reasons. The failure is printed in the pack and adds risk points.</div>"}
 else{verdict='<div class="banner miss"><b>This one got through every test.</b> '+(m.explain?m.explain[0]:"No check failed.")+"</div>"+(m.explain?'<p class="catch"><b>What catches it:</b> '+m.explain[1]+"</p>":"")}
 h=h.replace('<ol class="steps">',verdict+'<ol class="steps">');
 document.getElementById("verdict").innerHTML=h;
 if(history.replaceState)history.replaceState(null,"","#"+id);
}
document.querySelectorAll(".pick").forEach(function(b){b.addEventListener("click",function(){show(b.dataset.id)})});
var start=location.hash.slice(1);show(MUTS.some(function(x){return x.id==start})?start:"2234-mut2");
"""


def build_history_section(D: Data, n: dict) -> str:
    h = D.history
    if not h:
        return ""
    esc_prs = [p for p in h["prs"] if p.get("escape")]
    rows = []
    for p in sorted(esc_prs, key=lambda x: x["merged"]):
        r = p["ci-credited"]
        why = r["why"][0].replace("mandate rule: ", "").replace("risk score: risk", "risk score") if r.get("why") else ""
        rows.append([f'<a href="{e(p["url"])}">#{p["pr"]}</a>', e(p["title"]), e(p.get("confidence") or ""),
                     e(D.labels.get(p["pr"], "")), tier(r["tier"]), f'<span class="mono nw">{e(why)}</span>'])
    hm = h["modes"]["ci-credited"]
    return f"""
<section class="wrap" aria-labelledby="shist"><h2 id="shist">Real escapes from MessagePack's history: would it have caught them?</h2>
<p class="prose">{hm['n']} merged upstream PRs from the v3 era, routed by the signed mandate as written (not tuned to this history), with build and tests credited as passed because they merged green. No AI reviews: reviewers can only add reasons to route to a human, so this is the most lenient Countersign could be. {hm['escapes']} of them were later reverted or needed a fix for a defect they introduced ({hm['escapes_high_confidence']} with high confidence).</p>
<div class="stats"><div class="stat"><div class="big">{hm['confusion']['escape_cleared']} of {hm['escapes']}</div><div>escapes the AI would have cleared</div></div>
<div class="stat"><div class="big">{hm['routed_to_humans']} of {hm['n']}</div><div>PRs routed to a human; the AI could clear {hm['confusion']['clean_cleared'] + hm['confusion']['escape_cleared']}</div></div></div>
{table(['PR', 'Title', 'Confidence', 'What happened later', 'Tier', 'Deciding rule'], rows, cls='dense stack')}
<p class="foot-note">Honest limits: these PRs were written by people, not agents; labels are our judgement by a fixed rule; {hm['confusion']['clean_cleared']} cleared PRs with 0 escapes still allows an escape rate of up to about 12% in that bucket (rule of three). {src('measurement/history/README.md', 'method')} · {src('measurement/history/labels.yaml', 'labels')} · {src('measurement/history/results.md', 'all ' + str(hm['n']) + ' PRs')}</p>
</section>"""


# ---------------------------------------------------------------- tour.html

def build_tour(D: Data, n: dict) -> str:
    p = D.packs.get("2234") or {}
    f = D.facts.get("2234") or {}
    reqs = p.get("requirements", [])
    steps = []

    # 1 the change
    files = [[code(x["path"]), e(x["kind"]), f'+{x["ins"]} −{x["del"]}'] for x in f.get("diff", {}).get("by_file", [])]
    req_rows = [[code(r["id"]), e(r.get("type", "")), e(r.get("text", ""))] for r in reqs]
    steps.append(("The change", f"""
<p class="lead">An agent wrote branch <code>{e(f.get('branch', ''))}</code>: “{e(f.get('commit_message', ''))}”. {f.get('diff', {}).get('files', '?')} files, +{f.get('diff', {}).get('insertions', '?')} −{f.get('diff', {}).get('deletions', '?')}. Nobody on the team will read all of it line by line. The question is what someone can sign for.</p>
{table(['File', 'Kind', 'Lines'], files, num_cols=(2,))}
<h3>What it has to do</h3>
{table(['Clause', 'Type', 'Text'], req_rows)}
<p class="foot-note">Requirement clauses are our placeholders from the upstream issue (<code>official: false</code>). {src('evidence/2234/facts.json')} · {src('requirements/2234.yaml')}</p>"""))

    # 2 the facts
    ch = [[code(c["id"]), e(c.get("tool", "")), status(c["status"]), e(c.get("summary", ""))] for c in f.get("checks", [])]
    fwf = next((c for c in f.get("checks", []) if c["id"] == "tests.fail_without_fix"), {})
    fw_rows = [[code(short_test(t["name"])), status("failed" if t["outcome"] == "failed" else "passed"),
                "tests the change" if t["outcome"] == "failed" else "<b>passes on the old code</b>"] for t in fwf.get("tests", [])]
    steps.append(("The facts, before any model reads it", f"""
<p class="lead">Build, tests, public API and analyzer checks run first, in one controlled environment; nothing in this step is a model's opinion. {sum(c["status"] == "pass" for c in f.get("checks", []))} of {len(f.get("checks", []))} checks pass. {"Failing: " + ", ".join(code(c["id"]) for c in f.get("checks", []) if c["status"] == "fail") + ", a kind of check ordinary CI doesn't run." if any(c["status"] == "fail" for c in f.get("checks", [])) else ""}</p>
{table(['Check', 'Tool', 'Status', 'Result'], ch)}
<h3>Then: do the new tests fail without the fix?</h3>
<p class="prose">We revert the source, keep the new tests, and run them. A test that still passes on the old code doesn't test the change.</p>
{table(['New test', 'Without the fix', 'Meaning'], fw_rows)}
<p class="foot-note">{src('evidence/2234/facts.json')} · logs in {src('evidence/2234/logs', 'evidence/2234/logs/')}</p>"""))

    # 3 the reviewers
    panel = (p.get("panel") or {}).get("rows", [])
    rid = [r["id"] for r in reqs]
    prow = []
    for r in panel:
        prow.append([f'<b>{e(r["reviewer"].capitalize())}</b><br><span class="muted">{e(r.get("vendor", ""))}</span>']
                    + [status(r["verdicts"].get(x)) for x in rid]
                    + [f'{r.get("citations_verified", 0)} / {r.get("citations_rejected", 0)}', str(r.get("findings_verified", 0))])
    v1, v2 = n.get("codex_v1"), n.get("codex_v2")
    steps.append(("Independent reviewers, checked citations", f"""
<p class="lead">Three models from three vendors review separately, with the same brief and the facts. Every claim has to cite a file line, a test outcome or a check, and the engine re-reads each one.</p>
{table(['Reviewer'] + [code(x.replace('REQ-2234-', '')) for x in rid] + ['Citations ok / rejected', 'Findings'], prow, num_cols=(len(rid) + 1, len(rid) + 2), cls='')}
<div class="callout"><b>Why one reviewer can never clear.</b> {f"In its first pass Codex said met on {v1['met']} of {v1['of']} clauses across the four changes. Given the passing tests, its second pass said met on <b>{v2['met']} of {v2['of']}</b> and raised {v2['findings']} findings. " if v1 and v2 else ''}Evidence made it agreeable. So a clause is proven only when <i>every</i> reviewer says met with verified evidence. {src('docs/FAILURE_MODES.md', 'R1')}</div>
<p class="foot-note">{src('packs/2234/pack.json')} (<code>panel</code>) · {src('reviews/2234/claude.json')} · {src('reviews/2234/codex.json')} · {src('reviews/2234/nemotron.json')}</p>"""))

    # 4 found and refused
    find = next((x for x in p.get("findings", []) if x.get("id") == "C1" and x.get("reviewer") == "claude"), {})
    evl = "".join(
        f'<li>{status("pass", "verified") if ev.get("verified") else status("fail", "rejected")} '
        + (f'<code>{e(ev["file"].split("/")[-1])}:{ev["line"]} @{e(ev["rev"][:8])}</code> <code class="q1">{e(ev["quote"])}</code>' if ev["kind"] == "code"
           else f'<code>{e(short_test(ev.get("name", "")))}</code> {e(ev.get("outcome", ""))} without the fix' if ev["kind"] == "test"
           else f'{e(ev["kind"])}: {e(ev.get("url", ""))}')
        + f' <span class="muted">{e(ev.get("note", ""))}</span></li>' for ev in find.get("evidence", []))
    refused = (p.get("card") or {}).get("refused", [])
    ref_rows = [[e(x["topic"]), e(", ".join(x.get("raised_by", []))), e("; ".join(x.get("who_should_decide", [])))] for x in refused]
    n1 = next((r for r in p.get("refused", {}).get("clauses", [])), None)
    n1_html = ""
    if n1:
        vs = " · ".join(f'{e(k.capitalize())} {status(v.get("verdict"))}' for k, v in n1.get("verdicts", {}).items())
        n1_html = f'<div class="callout"><b>Refused: <code>{e(n1["id"])}</code></b> “{e(n1["text"])}” {vs}. Not unanimous, so not proven. Claude reproduced a crash the others missed.</div>'
    steps.append(("What it found, and what it refused to decide", f"""
<p class="lead"><b>Found ({e(find.get('severity', ''))}):</b> {e(find.get('title', ''))}.</p>
<blockquote class="prose">{e(find.get('claim', ''))}</blockquote>
<h3>Its citations, each re-checked by the engine</h3>
<ul class="ev list">{evl}</ul>
{n1_html}
<h3>Questions the AI declined to decide</h3>
{table(['Question', 'Raised by', 'Who should decide'], ref_rows)}
<p class="foot-note">{src('packs/2234/pack.json')} (<code>findings</code>, <code>refused</code>)</p>"""))

    # 5 sign-off card
    card = p.get("card") or {}
    reasons = "".join(f'<li>{e(r["text"])}</li>' for r in card.get("reasons", []))
    trace = "".join(f'<li>{status("pass", "proven") if t["status"] == "proven" else status("fail", "refused")} <code>{e(t["id"])}</code> {e(t["label"])}: <span class="muted">{e(t["why"])}</span></li>'
                    for t in card.get("trace", []))
    steps.append(("The sign-off card", f"""
<p class="lead">The pack's first screen: where the change goes, who decides, and why. You are checking a story, not hunting through a diff.</p>
<div class="signcard"><div class="card-h"><span>Change <code>2234</code> · risk score {e(card.get('risk_score', ''))}</span>{tier(card.get('tier'), card.get('owner'))}</div>
<h3>Why it goes to {e(card.get('owner', 'the owner'))}</h3><ol>{reasons}</ol>
<p class="muted">+ {e(card.get('more_drivers', 0))} more drivers in the pack</p>
<h3>Requirement trace</h3><ul class="rows">{trace}</ul></div>
<p class="ctas"><a class="btn primary" href="packs/2234/pack.html">Open the full 2234 pack</a></p>
<p class="foot-note">{src('packs/2234/pack.json')} (<code>card</code>)</p>"""))

    # 6 countersign + ledger
    so = p.get("signoff") or {}
    steps.append(("The owner countersigns; try to forge it", f"""
<p class="lead">Only the named owner can sign. The signature covers the pack's hash and the mandate's hash, and goes into an append-only, hash-chained ledger.</p>
<blockquote>{e(so.get('statement', ''))}</blockquote>
<pre class="cmd">$ {e(so.get('command', ''))}</pre>
<h3>The ledger, verified in your browser</h3>
<p class="prose">Each line's hash is SHA-256 over its content; each line points to the previous hash; each hash is signed with the signer's Ed25519 key from <code>keys/</code>. Edit anything and re-check.</p>
<div id="ledger" class="ledger"></div>
<p class="ctas"><button class="btn" type="button" id="tamper">1. Tamper: bump the mandate version in the last line</button><button class="btn" type="button" id="rehash">2. Cover it: recompute that line's hash</button><button class="btn" type="button" id="reset">Reset</button></p>
<div id="lstatus" class="banner" aria-live="polite"></div>
<p class="foot-note">{src('ledger/ledger.jsonl')} · {src('countersign/ledger.py')} · same check offline: <code>countersign verify-ledger</code>. {'No sign-off of 2234 is in the ledger yet; it holds the mandate signatures.' if not any(x.get('type') == 'signoff' for x in D.ledger) else ''}</p>"""))

    # 7 trust per area
    arow = [[code(a["name"]), e(a.get("owner", "")), e(a.get("sensitivity", "")), tier(a.get("max_ai_tier")), e(a.get("description", ""))] for a in D.areas]
    escapes = [x for x in D.ledger if x.get("type") == "escape"]
    tc = D.trust_cfg
    steps.append(("Trust is earned per area, and withdrawn", f"""
<p class="lead">The mandate says, per area, the most lenient tier the AI may assign alone. Clearance is never global.</p>
{table(['Area', 'Owner', 'Sensitivity', 'Most lenient tier the AI may give', 'What it is'], arow)}
<div class="callout"><b>After an escape.</b> When a revert or incident is traced to an AI-cleared change, that area drops to <code>{e(tc.get('escape_cap', 'ask'))}</code> at once: the AI may clear nothing there. It earns the right back after {e(tc.get('restore_after_agreeing_spotchecks', '?'))} spot-checks in a row agree with the AI; a disagreeing spot-check tightens the cap by {e(tc.get('disagree_tightens_by', '?'))} step.</div>
<p class="prose">Escapes recorded in the ledger so far: <b>{len(escapes)}</b>. {'Not recorded yet: a simulated escape-and-recovery run (it will be labelled simulated).' if not escapes else ''}</p>
<p class="foot-note">{src('mandate/messagepack.mandate.yaml')} (<code>areas</code>, <code>trust</code>) · {src('countersign/trust.py')} · offline: <code>countersign trust</code></p>"""))

    # 8 what you saw
    steps.append(("What you just saw", f"""
<p class="lead">Nobody read {f.get('diff', {}).get('insertions', '?') + f.get('diff', {}).get('deletions', 0) if f.get('diff') else 'all the'} lines, and the owner still learned that the change's title and its effect don't match, which of its tests prove nothing, where the reviewers disagree, and exactly what they are signing for.</p>
<p class="lead">{hero_line(n)}</p>
<p class="ctas"><a class="btn primary" href="attack.html">Now try to sneak a bug past it</a><a class="btn" href="packs/2283/pack.html">Pack 2283</a><a class="btn" href="packs/2129/pack.html">Pack 2129</a><a class="btn" href="packs/2297/pack.html">Pack 2297</a></p>"""))

    secs = "".join(f'<section class="tstep" id="s{i + 1}" data-n="{i + 1}" aria-labelledby="t{i + 1}"{"" if i == 0 else " hidden"}>'
                   f'<p class="eyebrow">Step {i + 1} of {len(steps)}</p><h1 id="t{i + 1}">{t}</h1>{b}</section>' for i, (t, b) in enumerate(steps))
    dots = "".join(f'<a href="#{i + 1}" class="dot" data-n="{i + 1}" title="{e(t)}">{i + 1}<span>{e(t)}</span></a>' for i, (t, _) in enumerate(steps))
    body = f"""
<div class="wrap tour">
<nav class="dots" aria-label="Tour steps">{dots}</nav>
{secs}
<div class="tnav"><button class="btn" id="prev" type="button">← Back</button><span id="pos" class="muted"></span><button class="btn primary" id="next" type="button">Next →</button></div>
</div>"""
    js = ("var LEDGER=" + json.dumps(D.ledger) + ";var PUB=" + json.dumps(D.pubkeys) + ";" + TOUR_JS + LEDGER_JS)
    return page("tour.html", "Guided tour: where the trust comes from (change 2234)", body, js=js, cls="has-tour")


TOUR_JS = r"""
var steps=document.querySelectorAll(".tstep"),N=steps.length,cur=1;
function go(k,push){k=Math.max(1,Math.min(N,k));cur=k;steps.forEach(function(s){s.hidden=+s.dataset.n!==k});
 document.querySelectorAll(".dot").forEach(function(d){if(+d.dataset.n===k)d.setAttribute("aria-current","step");else d.removeAttribute("aria-current")});
 document.getElementById("pos").textContent=k+" / "+N;document.getElementById("prev").disabled=k===1;
 var nx=document.getElementById("next");nx.textContent=k===N?"Start again":"Next →";
 if(push!==false&&location.hash!=="#"+k)history.replaceState(null,"","#"+k);window.scrollTo(0,0)}
document.getElementById("prev").onclick=function(){go(cur-1)};
document.getElementById("next").onclick=function(){go(cur===N?1:cur+1)};
document.querySelectorAll(".dot").forEach(function(d){d.onclick=function(ev){ev.preventDefault();go(+d.dataset.n)}});
document.addEventListener("keydown",function(ev){if(ev.target.tagName==="TEXTAREA"||ev.target.tagName==="INPUT")return;if(ev.key==="ArrowRight")go(cur+1);if(ev.key==="ArrowLeft")go(cur-1)});
window.addEventListener("hashchange",function(){var k=parseInt(location.hash.slice(1));if(k)go(k,false)});
go(parseInt(location.hash.slice(1))||1,false);
"""

LEDGER_JS = r"""
function sortDeep(v){if(Array.isArray(v))return v.map(sortDeep);if(v&&typeof v==="object"){var o={};Object.keys(v).sort().forEach(function(k){o[k]=sortDeep(v[k])});return o}return v}
function canon(v){if(Array.isArray(v))return"["+v.map(canon).join(",")+"]";if(v&&typeof v==="object")return"{"+Object.keys(v).sort().map(function(k){return JSON.stringify(k)+":"+canon(v[k])}).join(",")+"}";return JSON.stringify(v)}
function sha256js(bytes){var K=[1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298],H=[1779033703,3144134277,1013904242,2773480762,1359893119,2600822924,528734635,1541459225];
 var l=bytes.length,n=((l+9+63)>>6)<<6,m=new Uint8Array(n);m.set(bytes);m[l]=128;var bl=l*8;for(var i=0;i<4;i++)m[n-1-i]=(bl>>>(8*i))&255;m[n-5]=Math.floor(bl/4294967296)&255;
 var w=new Array(64);for(var o=0;o<n;o+=64){for(i=0;i<16;i++)w[i]=(m[o+4*i]<<24)|(m[o+4*i+1]<<16)|(m[o+4*i+2]<<8)|m[o+4*i+3];
 for(i=16;i<64;i++){var a=w[i-15],b=w[i-2],s0=((a>>>7)|(a<<25))^((a>>>18)|(a<<14))^(a>>>3),s1=((b>>>17)|(b<<15))^((b>>>19)|(b<<13))^(b>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)|0}
 var A=H[0],B=H[1],C=H[2],D=H[3],E=H[4],F=H[5],G=H[6],Hh=H[7];
 for(i=0;i<64;i++){var S1=((E>>>6)|(E<<26))^((E>>>11)|(E<<21))^((E>>>25)|(E<<7)),ch=(E&F)^(~E&G),t1=(Hh+S1+ch+K[i]+w[i])|0,S0=((A>>>2)|(A<<30))^((A>>>13)|(A<<19))^((A>>>22)|(A<<10)),mj=(A&B)^(A&C)^(B&C),t2=(S0+mj)|0;Hh=G;G=F;F=E;E=(D+t1)|0;D=C;C=B;B=A;A=(t1+t2)|0}
 H[0]=(H[0]+A)|0;H[1]=(H[1]+B)|0;H[2]=(H[2]+C)|0;H[3]=(H[3]+D)|0;H[4]=(H[4]+E)|0;H[5]=(H[5]+F)|0;H[6]=(H[6]+G)|0;H[7]=(H[7]+Hh)|0}
 return H.map(function(x){return("00000000"+(x>>>0).toString(16)).slice(-8)}).join("")}
function hashOf(entry){var c={};Object.keys(entry).forEach(function(k){if(k!=="hash"&&k!=="sig")c[k]=entry[k]});return sha256js(new TextEncoder().encode(canon(c)))}
function b64(s){var b=atob(s),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u}
async function sigOk(e){try{if(!(window.crypto&&crypto.subtle))return null;var pk=PUB[(e.signer||"").toLowerCase()];if(!pk)return false;
 var key=await crypto.subtle.importKey("raw",b64(pk),{name:"Ed25519"},false,["verify"]);return await crypto.subtle.verify({name:"Ed25519"},key,b64(e.sig),new TextEncoder().encode(String(e.hash)))}catch(err){return null}}
var work=JSON.parse(JSON.stringify(LEDGER));
function render(){var box=document.getElementById("ledger");if(!box)return;box.innerHTML="";
 work.forEach(function(e,i){var d=document.createElement("div");d.className="lline";d.id="l"+i;
  var ta=document.createElement("textarea");ta.spellcheck=false;ta.setAttribute("aria-label","Ledger line "+(i+1));ta.value=JSON.stringify(sortDeep(e),null,1);ta.rows=Math.min(9,ta.value.split("\n").length);
  ta.addEventListener("input",function(){try{work[i]=JSON.parse(ta.value);ta.classList.remove("badjson")}catch(_){ta.classList.add("badjson")}check()});
  var r=document.createElement("div");r.className="lres";d.appendChild(r);d.appendChild(ta);box.appendChild(d)});check()}
async function check(){var prev="0".repeat(64),bad=[],sigNA=false;
 for(var i=0;i<work.length;i++){var e=work[i],p=[],line=i+1;
  if(e.seq!==line)p.push("seq is "+e.seq+", expected "+line);
  if(e.prev!==prev)p.push("prev does not match the hash of line "+(line-1)+" (chain broken)");
  if(hashOf(e)!==e.hash)p.push("content does not match its hash (edited after it was written)");
  var s=await sigOk(e);if(s===false)p.push("signature does not verify against keys/"+String(e.signer).toLowerCase()+".pub");if(s===null)sigNA=true;
  prev=e.hash;var r=document.querySelectorAll(".lres")[i];
  if(r)r.innerHTML=p.length?'<span class="st bad">✗ line '+line+"</span> "+p.join("; "):'<span class="st ok">✓ line '+line+"</span> "+e.type+" by "+e.signer+", "+e.ts+(s?" · signature valid":"");
  p.forEach(function(x){bad.push("line "+line+": "+x)})}
 var st=document.getElementById("lstatus");if(!st)return;
 st.className="banner "+(bad.length?"bad":"ok");
 st.innerHTML=bad.length?"<b>LEDGER INVALID.</b> "+bad.join(". ")+"."+(bad.some(function(x){return x.indexOf("signature")>=0})?" Recomputing the hash is not enough: the new hash needs a signature that only the signer's private key can make, and that key is not in the repo.":bad.some(function(x){return x.indexOf("its hash")>=0})?" Try step 2 to cover it up.":""):"<b>Ledger OK:</b> "+work.length+" entries, hash chain intact"+(sigNA?" (this browser can't check Ed25519 signatures; run countersign verify-ledger)":", every signature verifies")+"."}
function tamper(){var e=work[work.length-1];var p=e.payload||{};var k=("version" in p)?"version":Object.keys(p).filter(function(k){return typeof p[k]==="string"&&k!=="sha256"})[0]||Object.keys(p)[0];
 if(k==="version")p[k]=String(+p[k]+1);else p[k]=p[k]+"-edited";render()}
document.getElementById("tamper").onclick=tamper;
document.getElementById("rehash").onclick=function(){var e=work[work.length-1];e.hash=hashOf(e);render()};
document.getElementById("reset").onclick=function(){work=JSON.parse(JSON.stringify(LEDGER));render()};
render();
"""


# ---------------------------------------------------------------- pitch.html

def md_inline(s: str) -> str:
    s = e(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{BLOB}docs/{m.group(2).replace("../", "")}">{m.group(1)}</a>'
               if not m.group(2).startswith("http") else f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    return s


def md_block(lines: list[str]) -> str:
    out, stack, tbl = [], [], []

    def flush_tbl():
        if not tbl:
            return
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl if not re.match(r"^\s*\|[\s:|-]+\|\s*$", r)]
        out.append(table([md_inline(c) for c in rows[0]], [[md_inline(c) for c in r] for r in rows[1:]]))
        tbl.clear()

    for line in lines:
        if line.strip().startswith("|"):
            tbl.append(line)
            continue
        flush_tbl()
        m = re.match(r"^(\s*)- (.*)$", line)
        if m:
            depth = len(m.group(1)) // 2
            while len(stack) > depth + 1:
                out.append("</li></ul>")
                stack.pop()
            if len(stack) < depth + 1:
                out.append("<ul>")
                stack.append(depth)
            else:
                out.append("</li>")
            out.append("<li>" + md_inline(m.group(2)))
        elif line.strip():
            out.append(f"<p>{md_inline(line.strip())}</p>")
    flush_tbl()
    while stack:
        out.append("</li></ul>")
        stack.pop()
    return "".join(out).replace("<ul></li>", "<ul>")


def parse_deck(text: str) -> list[dict]:
    slides = []
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = chunk.splitlines()
        m = re.match(r"(\d+)\.\s*(.*)", lines[0])
        s = {"n": int(m.group(1)) if m else len(slides) + 1, "title": m.group(2) if m else lines[0], "message": "", "visual": [], "note": ""}
        cur = None
        for line in lines[1:]:
            if line.strip() == "---":
                continue
            mm = re.match(r"^- \*\*(Message|Visual[^:]*|Speaker note):\*\*\s*(.*)$", line)
            if mm:
                cur = mm.group(1).split()[0].lower()
                if cur == "message":
                    s["message"] = mm.group(2)
                elif cur == "speaker":
                    s["note"] = mm.group(2)
                else:
                    s["visual"].append(mm.group(2))
            elif cur == "visual":
                s["visual"].append(line[2:] if line.startswith("  ") else line)
        slides.append(s)
    return slides


def build_pitch(D: Data, n: dict) -> str:
    slides = parse_deck(rt("docs/pitch/deck.md"))
    rows = D.change_rows()
    metrics_html = "<ul class='mlist'>" + "".join(f"<li>{x}</li>" for x in [
        f"Real changes routed to a human: <b>{n['ask'] + n['block']} of {n['changes']}</b>" if n.get("changes") else "",
        f"Seeded one-line bugs that failed a check: <b>{n['mut_checks']} of {n['mut_total']}</b>; reaching a human before any AI review: <b>{n['mut_routed']} of {n['mut_total']}</b>" if n.get("mut_checks") is not None else "",
        f"Real upstream escapes the AI would have cleared: <b>{n['h_esc_cleared']} of {n['h_esc']}</b> ({n['h_n']} PRs replayed)" if n.get("h_n") else "",
        ("Findings verified per reviewer: " + ", ".join(f"{k} {v['verified']} (rejected {v['rejected']})" for k, v in (D.metric('findings_per_reviewer') or {}).items())) if D.metric("findings_per_reviewer") else "",
        (f"Review time with the pack vs reading every line: {D.metric('human_minutes_with_pack')} vs {D.metric('human_minutes_full_read')} min (estimate from a reading-speed model, simulated)") if D.metric("human_minutes_full_read") else "",
    ] if x) + "</ul>" + f"<p class='foot-note'>{src('measurement/results.json')} · {src('measurement/history/results.md')}</p>"
    tiers_table = table(["Change", "Size", "Tier", "Deciding reason"],
                        [[code(r["change"]), f'{r["diff"].get("files", "?")} files', tier(r["tier"], r["owner"]), e(r["reasons"][0] if r["reasons"] else "")] for r in rows], cls="stack")
    pipeline = ("<div class='pipe'>" + "".join(f"<span>{x}</span>" for x in
                ["facts", "independent reviewers", "citation check", "decide", "evidence pack", "owner signs", "ledger", "trust per area"])
                + "</div><div class='tiers'><span class='badge ok'>✓ SILENT</span><span class='badge ok'>✓ NOTIFY</span><span class='muted'>AI may clear, if the mandate allows</span>"
                "<span class='sep'></span><span class='badge warn'>? ASK</span><span class='badge bad'>✗ BLOCK</span><span class='muted'>a named human</span></div>")
    f2234 = (D.facts.get("2234") or {}).get("diff", {})
    signs = ("<div class='two'><div class='greyed'><p class='mono'>ju26-issue-2234</p><p class='big'>"
             f"+{f2234.get('insertions', '?')} −{f2234.get('deletions', '?')}</p><p class='muted'>{f2234.get('files', '?')} files, written by an agent. "
             "Not read line by line.</p></div><div><p class='muted'>What the owner signs instead</p><ol class='signs'>"
             "<li>What was checked, and by whom</li><li>What wasn't, and why</li><li>The residual risk</li></ol></div></div>")
    override = {2: signs, 3: pipeline, 4: story_2234(D, compact=True), 5: tiers_table, 6: metrics_html}
    out = []
    for i, s in enumerate(slides):
        vis = override.get(s["n"])
        if vis is None:
            lines = [re.sub(r"TODO\(numbers\)[^.]*\.?", "", x) for x in s["visual"]]
            if any(x.startswith("- ") for x in lines[1:]):  # first line is a note to the designer; show only its items
                vis = md_block([x for x in lines[1:] if x.startswith("- ")]).replace("<ul>", '<ul class="cols">', 1)
            else:
                vis = md_block(lines)
        if s["n"] == 1:
            out.append(f"""<section class="slide title-slide" data-i="{i}"><div class="sl">
<p class="eyebrow">Junction 2026 · Tieto: Earned Trust in AI Code</p>
<h1><span class="sig">✓</span>Countersign</h1>
<p class="punch">{md_inline(s['message'].replace('Countersign. ', ''))}</p>
<p class="lead">{hero_line(n)}</p>
<p class="muted">{REPO_URL.replace('https://', '')}</p>
</div><aside class="note">{md_inline(s['note'])}</aside></section>""")
            continue
        out.append(f"""<section class="slide" data-i="{i}"><div class="sl">
<p class="eyebrow">{s['n']} · {md_inline(s['title'])}</p>
<h2>{md_inline(s['message'])}</h2>
<div class="vis">{vis}</div>
</div><aside class="note">{md_inline(s['note'])}</aside></section>""")
    body = f"""<div class="deck" id="deck">{''.join(out)}</div>
<div class="deckbar"><button class="btn" id="dprev" type="button" aria-label="Previous slide">←</button><span id="dpos" class="muted"></span>
<button class="btn" id="dnote" type="button">Notes (N)</button><button class="btn" id="dfull" type="button">Full screen (F)</button>
<button class="btn" id="dnext" type="button" aria-label="Next slide">→</button></div>"""
    return page("pitch.html", "Countersign: pitch", body, js=PITCH_JS, cls="pitch")


PITCH_JS = r"""
var sl=document.querySelectorAll(".slide"),N=sl.length,k=0;
function show(i){k=Math.max(0,Math.min(N-1,i));sl.forEach(function(s,j){s.classList.toggle("on",j===k)});document.getElementById("dpos").textContent=(k+1)+" / "+N;history.replaceState(null,"","#"+(k+1))}
document.getElementById("dprev").onclick=function(){show(k-1)};document.getElementById("dnext").onclick=function(){show(k+1)};
document.getElementById("dnote").onclick=function(){document.body.classList.toggle("notes")};
document.getElementById("dfull").onclick=function(){var d=document.documentElement;if(document.fullscreenElement)document.exitFullscreen();else if(d.requestFullscreen)d.requestFullscreen()};
document.addEventListener("keydown",function(e){if(["ArrowRight","PageDown"," "].indexOf(e.key)>=0){e.preventDefault();show(k+1)}if(["ArrowLeft","PageUp"].indexOf(e.key)>=0){e.preventDefault();show(k-1)}
 if(e.key==="Home")show(0);if(e.key==="End")show(N-1);if(e.key==="n"||e.key==="N")document.body.classList.toggle("notes");if(e.key==="f"||e.key==="F")document.getElementById("dfull").click()});
var x0=null,y0=null;document.addEventListener("touchstart",function(e){x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
document.addEventListener("touchend",function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))show(k+(dx<0?1:-1));x0=null},{passive:true});
show((parseInt(location.hash.slice(1))||1)-1);
"""


# ---------------------------------------------------------------- CSS

CSS = r"""
:root{--bg:#ffffff;--bg2:#f6f8fa;--fg:#1f2328;--muted:#59636e;--border:#d1d9e0;--accent:#0969da;--accent-bg:#ddf4ff;
--ok:#1a7f37;--ok-bg:#dafbe1;--warn:#9a6700;--warn-bg:#fff8c5;--bad:#d1242f;--bad-bg:#ffebe9;
--sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;color-scheme:light}
:root[data-theme=dark]{--bg:#0d1117;--bg2:#151b23;--fg:#f0f6fc;--muted:#9198a1;--border:#3d444d;--accent:#4493f8;--accent-bg:#121d2f;
--ok:#3fb950;--ok-bg:#12261e;--warn:#d29922;--warn-bg:#272115;--bad:#f85149;--bad-bg:#25171c;color-scheme:dark}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d1117;--bg2:#151b23;--fg:#f0f6fc;--muted:#9198a1;--border:#3d444d;--accent:#4493f8;--accent-bg:#121d2f;
--ok:#3fb950;--ok-bg:#12261e;--warn:#d29922;--warn-bg:#272115;--bad:#f85149;--bad-bg:#25171c;color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 var(--sans);font-variant-numeric:tabular-nums}
a{color:var(--accent);text-underline-offset:2px}a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
code,pre,.mono{font-family:var(--mono);font-size:.875em}
code{background:var(--bg2);border:1px solid var(--border);border-radius:4px;padding:0 4px;word-break:break-word}
pre{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:8px 12px;overflow-x:auto;margin:8px 0}
pre code{border:0;padding:0;background:none}
h1,h2,h3{line-height:1.25;font-weight:600;margin:0 0 8px}
h1{font-size:32px;letter-spacing:-.01em}h2{font-size:24px;margin-top:8px}h3{font-size:16px;margin-top:24px}
p{margin:0 0 16px}ul,ol{margin:0 0 16px;padding-left:24px}
blockquote{margin:8px 0 16px;padding:4px 16px;border-left:3px solid var(--border);color:var(--muted)}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
section.wrap{padding-top:40px}
.prose,.lead{max-width:70ch}.lead{font-size:18px}
.muted{color:var(--muted)}.eyebrow{font:12px/1.5 var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:var(--bg);padding:8px;z-index:9}
.top{border-bottom:1px solid var(--border);background:var(--bg);position:sticky;top:0;z-index:5}
.bar{display:flex;align-items:center;gap:16px;min-height:56px;flex-wrap:wrap}
.mark{font-weight:600;color:var(--fg);text-decoration:none;display:flex;align-items:center;gap:8px}
.sig{display:inline-grid;place-items:center;width:24px;height:24px;border:1.5px solid var(--fg);border-radius:6px;font-size:14px}
.top nav{display:flex;gap:4px;flex:1;overflow-x:auto;scrollbar-width:none}
.top nav a{color:var(--muted);text-decoration:none;padding:6px 8px;border-radius:6px;font-size:14px;white-space:nowrap}
.top nav a:hover{color:var(--fg);background:var(--bg2)}.top nav a[aria-current]{color:var(--fg);font-weight:600;box-shadow:inset 0 -2px 0 var(--accent);border-radius:0}
.theme{background:none;border:1px solid var(--border);color:var(--fg);border-radius:6px;width:32px;height:32px;cursor:pointer}
.hero{padding-top:48px}.hero h1{max-width:34ch}.hero.small h1{max-width:none}
.h-sm{font-size:20px}
.foot{border-top:1px solid var(--border);margin-top:64px;padding:24px 0;color:var(--muted);font-size:14px}.foot p{margin:0 0 8px}
.foot-note{font-size:12px;color:var(--muted);margin-top:8px}
a.src{font-family:var(--mono);font-size:12px;color:var(--muted)}a.src:hover{color:var(--accent)}
/* status */
.st{font:600 12px/1.5 var(--mono);white-space:nowrap;text-transform:uppercase}.st.ok{color:var(--ok)}.st.bad{color:var(--bad)}.st.warn{color:var(--warn)}
.badge{justify-self:start;display:inline-block;font:600 12px/20px var(--mono);padding:0 8px;border:1px solid var(--border);border-radius:999px;white-space:nowrap}
.badge.ok{color:var(--ok);border-color:currentColor;background:var(--ok-bg)}.badge.warn{color:var(--warn);border-color:currentColor;background:var(--warn-bg)}
.badge.bad{color:var(--bad);border-color:currentColor;background:var(--bad-bg)}
/* story cards */
.story{list-style:none;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0;counter-reset:none}
.card{border:1px solid var(--border);border-radius:6px;padding:16px;background:var(--bg);display:flex;flex-direction:column}
.card.bad{border-color:var(--bad);box-shadow:inset 0 3px 0 var(--bad)}
.card-h{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.step{font:600 12px/1.5 var(--mono);text-transform:uppercase;color:var(--muted)}
.rows{list-style:none;padding:0;margin:0 0 8px}.rows li{padding:6px 0;border-top:1px solid var(--border);font-size:14px}.rows li:first-child{border-top:0}
.card blockquote{font-size:14px}.card .foot-note{margin-top:auto;padding-top:8px}
.ev{list-style:none;padding:0;margin:0 0 8px;font-size:14px}.ev li{margin:0 0 8px}
.ev-h{font-size:14px;margin:8px 0 4px;color:var(--muted)}
pre.q{margin:4px 0 0;font-size:12px;padding:4px 8px}
.story.compact .rows li{font-size:15px}
.ctas{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.btn{display:inline-flex;align-items:center;gap:8px;font:500 14px/20px var(--sans);padding:7px 14px;border:1px solid var(--border);border-radius:6px;background:var(--bg2);color:var(--fg);text-decoration:none;cursor:pointer}
.btn:hover{border-color:var(--muted)}.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
:root[data-theme=dark] .btn.primary{color:#0d1117}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .btn.primary{color:#0d1117}}
.btn:disabled{opacity:.5;cursor:default}
/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));border:1px solid var(--border);border-radius:6px;margin:16px 0}
.stat{padding:16px;border-left:1px solid var(--border)}.stat:first-child{border-left:0}
.big{font:600 32px/1.25 var(--mono);margin-bottom:4px}
.stat div:last-child{font-size:14px;color:var(--muted)}
/* differentiators */
.diffs{list-style:none;padding:0;counter-reset:d;max-width:80ch}
.diffs li{counter-increment:d;position:relative;padding:16px 0 8px 48px;border-top:1px solid var(--border)}
.diffs li::before{content:counter(d);position:absolute;left:0;top:16px;font:600 14px/24px var(--mono);width:32px;height:24px;border:1px solid var(--border);border-radius:6px;text-align:center;color:var(--muted)}
.diffs h3{margin:0 0 4px;font-size:18px}.diffs p{margin:0 0 8px;color:var(--fg)}.diffs .more{font-size:14px}
.list li{margin-bottom:8px}
/* tables */
.scroll{overflow-x:auto;border:1px solid var(--border);border-radius:6px;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;font-weight:600;color:var(--muted);background:var(--bg2);font-size:12px;text-transform:uppercase;letter-spacing:.03em}
th,td{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top}tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;white-space:nowrap}
table.dense td{padding:6px 10px}
.callout{border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:6px;padding:12px 16px;margin:16px 0;max-width:80ch;background:var(--bg2)}
/* attack */
.picker{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:16px}
.pick{display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--fg);cursor:pointer;font:14px var(--sans)}
.pick span{font-size:12px;color:var(--muted)}.pick code{border:0;background:none;padding:0;font-weight:600}
.pick:hover{border-color:var(--muted)}.pick[aria-pressed=true]{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent);background:var(--accent-bg)}
.verdict{border:1px solid var(--border);border-radius:6px;padding:16px;min-height:200px}
.banner{border:1px solid var(--border);border-radius:6px;padding:12px 16px;margin-bottom:16px;background:var(--bg2)}
.banner.ok{border-color:var(--ok);background:var(--ok-bg)}.banner.bad{border-color:var(--bad);background:var(--bad-bg)}.banner.warn{border-color:var(--warn);background:var(--warn-bg)}
.banner.miss{border-color:var(--warn);background:var(--warn-bg);border-style:dashed}
.banner:empty{display:none}
.catch{max-width:80ch}
.diffbox{border:1px solid var(--border);border-radius:6px;overflow:hidden;margin-bottom:16px}
.diff-h{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;padding:8px 12px;background:var(--bg2);border-bottom:1px solid var(--border);font-size:14px}
.diff-h code{border:0;background:none;padding:0}
pre.diff{margin:0;border:0;border-radius:0;font-size:13px;line-height:1.6;white-space:pre-wrap;word-break:break-all}
.del{display:block;background:var(--bad-bg);color:var(--fg);box-shadow:inset 3px 0 0 var(--bad);padding-left:4px}
.add{display:block;background:var(--ok-bg);color:var(--fg);box-shadow:inset 3px 0 0 var(--ok);padding-left:4px}
.what{padding:8px 12px;margin:0;font-size:14px}
.steps{list-style:none;padding:0;margin:0}.steps li{padding:8px 0;border-top:1px solid var(--border);font-size:14px}
.tests{margin-top:4px;display:flex;gap:4px;flex-wrap:wrap;font-size:12px}
/* tour */
.tour{padding-top:24px;min-height:70vh}
.dots{display:flex;gap:4px;margin-bottom:24px;overflow-x:auto}
.dot{flex:1;min-width:32px;text-decoration:none;color:var(--muted);font:600 12px/1.5 var(--mono);border-top:3px solid var(--border);padding-top:6px}
.dot span{display:block;font:12px/1.4 var(--sans);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dot[aria-current]{color:var(--fg);border-color:var(--accent)}
.tstep h1{font-size:28px}
.tnav{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:32px;padding-top:16px;border-top:1px solid var(--border);position:sticky;bottom:0;background:var(--bg);padding-bottom:12px}
.signcard{border:1px solid var(--border);border-radius:6px;padding:16px;max-width:80ch}
.signcard h3{margin-top:16px}
.cmd{white-space:pre-wrap;word-break:break-word}
.ledger{display:grid;gap:8px}
.lline textarea{width:100%;font:12px/1.5 var(--mono);background:var(--bg2);color:var(--fg);border:1px solid var(--border);border-radius:6px;padding:8px;resize:vertical}
.lline textarea.badjson{border-color:var(--bad)}
.lres{font-size:14px;margin-bottom:4px;word-break:break-word}
code.q1{font-size:12px}code.nwc{white-space:nowrap}.nw{white-space:nowrap;font-size:12px}
/* pitch */
body.pitch .foot{display:none}body.pitch main{padding:0}
.deck{position:relative}
.slide{display:none;min-height:calc(100vh - 57px - 56px);padding:32px 16px}
.slide.on{display:flex;flex-direction:column;justify-content:center}
.sl{max-width:1040px;width:100%;margin:0 auto}
.slide h2{font-size:clamp(22px,3.2vw,40px);max-width:32ch;margin-bottom:24px}
.slide .vis{font-size:clamp(15px,1.5vw,20px)}
.slide .vis table{font-size:clamp(13px,1.2vw,17px)}
.title-slide h1{font-size:clamp(32px,5vw,64px);display:flex;align-items:center;gap:16px}
.title-slide .sig{width:1.1em;height:1.1em;font-size:.6em;border-width:2px;border-radius:10px}
.punch{font-size:clamp(20px,2.6vw,32px);max-width:36ch;line-height:1.35}
.note{display:none;max-width:1040px;margin:24px auto 0;width:100%;border-top:1px dashed var(--border);padding-top:12px;color:var(--muted);font-size:15px}
body.notes .note{display:block}
.deckbar{position:sticky;bottom:0;display:flex;gap:8px;justify-content:center;align-items:center;padding:8px;border-top:1px solid var(--border);background:var(--bg)}
.pipe{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:16px}
.pipe span{border:1px solid var(--border);border-radius:6px;padding:6px 12px;font:14px var(--mono);background:var(--bg2)}
.pipe span+span::before{content:"→ ";color:var(--muted)}
.tiers{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.tiers .sep{width:16px}
.mlist li{margin-bottom:12px}
ul.cols{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
ul.cols>li{border:1px solid var(--border);border-radius:6px;padding:16px;margin:0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}
.greyed{border:1px dashed var(--border);border-radius:6px;padding:24px;color:var(--muted)}.greyed .big{color:var(--muted)}
.signs{font-size:1.2em}.signs li{margin-bottom:12px;padding-left:4px}
.title-slide .sig{line-height:1}
/* small screens */
@media (max-width:860px){.story{grid-template-columns:1fr}.stat{border-left:0;border-top:1px solid var(--border)}.stat:first-child{border-top:0}}
@media (max-width:600px){.hero{padding-top:24px}.lead{font-size:16px}section.wrap{padding-top:32px}
.top{position:static}.bar{gap:8px;padding:8px 16px;min-height:0}.top nav{order:3;flex-basis:100%}.theme{margin-left:auto}
h1{font-size:22px}.hero h1{font-size:22px}.lead{font-size:15px}.h-sm{font-size:18px}
table.stack thead{display:none}table.stack tr{display:block;border-bottom:1px solid var(--border);padding:8px 0}table.stack tr:last-child{border-bottom:0}
table.stack td{display:grid;grid-template-columns:96px 1fr;gap:8px;border:0;padding:2px 12px}table.stack td::before{content:attr(data-label);padding-top:2px;font:600 11px/1.5 var(--sans);text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
.card{padding:12px}.rows li{padding:4px 0}.picker{grid-template-columns:repeat(3,1fr)}.two{grid-template-columns:1fr;gap:16px}.pick span{display:none}.pick{padding:8px}.verdict{padding:12px}
.big{font-size:24px}.tstep h1{font-size:22px}.dot span{display:none}.slide{padding:24px 16px}.diffs li{padding-left:40px}
th,td{padding:6px 8px}}
@media print{.top,.deckbar,.tnav{display:none}.slide{display:block!important;page-break-after:always;min-height:auto}}
"""


# ---------------------------------------------------------------- main

def copy_packs():
    dst = SITE / "packs"
    if dst.exists():
        shutil.rmtree(dst)
    for c in CHANGES:
        s = ROOT / "packs" / c / "pack.html"
        if s.exists():
            (dst / c).mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dst / c / "pack.html")


def main() -> None:
    D = Data()
    n = numbers(D)
    copy_packs()
    (SITE / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    pages = {"index.html": build_index(D, n), "attack.html": build_attack(D, n), "tour.html": build_tour(D, n), "pitch.html": build_pitch(D, n)}
    for name, htm in pages.items():
        (SITE / name).write_text(htm, encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print("hero:", hero_text(n))
    print("wrote", ", ".join(pages), "+ style.css + packs/")


if __name__ == "__main__":
    main()
