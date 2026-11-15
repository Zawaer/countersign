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
import sys
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


sys.path.insert(0, str(ROOT))
from countersign.icons import CSS as ICON_CSS, GLYPH, icon  # noqa: E402  Material Symbols, one mapping for every page

TIER_ICON = {"silent": "silent", "notify": "notify", "ask": "ask", "block": "block"}  # meanings in countersign/icons.py STATUS
TIER_CLASS = {"silent": "ok", "notify": "ok", "ask": "warn", "block": "bad"}


def tier(t: str | None, owner: str | None = None) -> str:
    if not t:
        return '<span class="badge">not routed yet</span>'
    o = f'{icon("arrow_forward", "arr")}{e(owner)}' if owner and t in HUMAN_TIERS else ""
    return f'<span class="badge {TIER_CLASS.get(t, "")}">{icon(TIER_ICON.get(t, "unknown"))}{e(t.upper())}{o}</span>'


def trust_rule(D: "Data") -> str:
    """How clearance is withdrawn and earned back, read from the mandate's trust block (old or staged form)."""
    tc = D.trust_cfg
    if tc.get("restore_after_agreeing_spotchecks"):
        return (f"drops that area to <code>{e(tc.get('escape_cap', 'ask'))}</code> at once: the AI may clear nothing there. "
                f"It earns the right back after {e(tc['restore_after_agreeing_spotchecks'])} human spot-checks of AI-cleared changes in a row agree with the AI.")
    m = re.search(r"^\s+notify:\s*\{agreeing_spotchecks:\s*(\d+)", rt("mandate/messagepack.mandate.yaml"), re.M)
    if m:
        return (f"drops that area one stage (<code>silent</code> → <code>notify</code> → <code>ask</code>), as does a human spot-check that disagrees with the AI. "
                f"Climbing back to <code>notify</code> takes {m.group(1)} agreeing spot-checks in a row.")
    return "drops that area's clearance; see the trust block in the mandate."


def tier_legend() -> str:
    """What the four tiers mean (README.md, docs/PRINCIPLES.md); shown wherever tier badges appear."""
    return (f'<dl class="legend" aria-label="What the tiers mean">'
            f'<div><dt>{tier("silent")} {tier("notify")}</dt><dd>the AI may clear it alone, if the mandate allows (notify also tells the owner)</dd></div>'
            f'<div><dt>{tier("ask")}</dt><dd>the named owner must read the evidence pack and sign</dd></div>'
            f'<div><dt>{tier("block")}</dt><dd>refused, citing the rule; the owner can only reject or request changes</dd></div></dl>')


def status(s: str | None, word: str | None = None) -> str:
    s = s or "not run"
    cls = {"pass": "ok", "passed": "ok", "met": "ok", "fail": "bad", "failed": "bad", "not_met": "bad",
           "error": "warn", "cannot_determine": "warn"}.get(s, "")
    meaning = {"ok": "pass", "bad": "fail", "warn": "unknown"}.get(cls, "pending")
    word = word or {"not_met": "not met", "cannot_determine": "can't tell"}.get(s, s)
    return f'<span class="st {cls}">{icon(meaning)}{e(word)}</span>'


def table(head: list[str], rows: list[list[str]], num_cols: tuple[int, ...] = (), cls: str = "stack", row_ids: list[str] | None = None) -> str:
    th = "".join(f'<th{" class=n" if i in num_cols else ""}>{h}</th>' for i, h in enumerate(head))
    labels = [re.sub(r"<[^>]+>", "", h) for h in head]
    trs = "".join((f'<tr id="{e(row_ids[k])}">' if row_ids else "<tr>") + "".join(f'<td{" class=n" if i in num_cols else ""} data-label="{e(labels[i]) if i < len(labels) else ""}">{c}</td>'
                                   for i, c in enumerate(r)) + "</tr>" for k, r in enumerate(rows))
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def pack_view(p):
    """The pack as its own renderer shows it (countersign.pack_render.view: the adjudicator's ruling in words)."""
    if not p:
        return p
    import sys
    sys.path.insert(0, str(ROOT))
    from countersign.pack_render import view
    return view(p)


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
        self.packs = {c: pack_view(rj(f"packs/{c}/pack.json")) for c in CHANGES}
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
        by = {r["change"]: r for r in self.results.get("changes", []) if not r.get("mutant") and not r["change"].startswith("var-")}
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
        ids = [mid for mid in rows if mid in self.facts] or [mid for mid in self.facts if "-mut" in mid]
        for mid in ids:
            f = self.facts[mid]
            m = f.get("mutation", {})
            cat = self.catalogue.get(mid, {})
            checks = {c["id"]: c for c in f.get("checks", [])}
            r = rows.get(mid, {})
            out.append({
                "id": mid, "of": (r.get("of") or m.get("of") or mid.split("-")[0]), "kind": (m.get("kind") or cat.get("kind") or "").replace("_", " "),
                "file": m.get("file") or cat.get("file") or (m.get("files") or [None])[0], "line": m.get("line") or cat.get("line"),
                "before": m.get("before"), "after": m.get("after"),
                "description": m.get("description") or cat.get("description"), "effect": m.get("intended_effect"),
                "checks": [{"id": c["id"], "status": c["status"], "summary": c.get("summary", ""),
                            "failing": [short_test(t["name"]) for t in c.get("tests", []) if t.get("outcome") == "failed"]}
                           for c in f.get("checks", [])],
                "caught_by_tests": m.get("caught_by") or [], "caught_by_full": m.get("caught_by_full_suite") or [],
                "any_check": bool(m.get("caught_by_any_deterministic_check")) or any(c["status"] == "fail" for c in checks.values()),
                "tier": r.get("tier"), "original_tier": r.get("original_tier"), "attributable": r.get("attributable", []),
                "routed": r.get("routed_to_human"), "reviews": r.get("reviews"),
                "owner": (self.packs.get((r.get("of") or m.get("of") or mid.split("-")[0])) or {}).get("owner"),
            })
        order = {c: i for i, c in enumerate(CHANGES)}
        return sorted(out, key=lambda x: (order.get(x["of"], 9), int(x["id"].split("-mut")[1]) if "-mut" in x["id"] else 99))


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
    try:  # red team totals come from the same place as the docs' numbers (scripts/sync_numbers.py)
        import importlib.util  # noqa: PLC0415
        spec = importlib.util.spec_from_file_location("sync_numbers", ROOT / "scripts/sync_numbers.py")
        sn = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sn)
        sv = sn.values()
        n["rt_total"], n["rt_stopped"] = int(sv["redteam_total"]), int(sv["redteam_stopped"])
    except Exception:  # noqa: BLE001  (the site still builds without the red-team tile)
        pass
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
        parts.append(f' <b>{n["mut_checks"]} of {n["mut_total"]}</b> seeded changes (one-line bugs and planted attacks) failed a check.')
    if n.get("h_esc") is not None:
        parts.append(f' Replayed on {n["h_n"]} real upstream PRs, it would have cleared <b>{n["h_esc_cleared"]} of the {n["h_esc"]}</b> that later had to be reverted or fixed.')
    return "".join(parts)


def whoa_line(D: "Data") -> str:
    """The landing page's first claim: change 2234, read from its facts and pack."""
    p = D.packs.get("2234") or {}
    owner = p.get("owner")
    return ("<b>Change 2234 passes its build, its new tests, the full suite and an AI review. It fixes the wrong bug.</b> "
            f"Countersign sent it to its owner{f', {e(owner)},' if owner else ''} with the reason and the evidence.")


def hero_text(n: dict) -> str:
    return re.sub(r"<[^>]+>", "", hero_line(n))


# ---------------------------------------------------------------- shared page shell

TAGLINE = "AI reviews code; a named human signs."  # same line as site/scene.py and the evidence packs


def page(fname: str, title: str, body: str, js: str = "", cls: str = "", desc: str = "") -> str:
    depth = fname.count("/")
    up = "../" * depth
    sha = git("rev-parse", "--short", "HEAD")
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'Countersign: AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it cannot, and a named human countersigns the rest.')}">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{up}favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<link rel="stylesheet" href="{up}style.css">
<script>try{{var t=localStorage.getItem("cs-theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
</head><body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar">
<p class="brand"><a class="mark" href="{up}index.html">Countersign</a><span class="tag">{e(TAGLINE)}</span></p>
<nav aria-label="Site"><a href="{up}more.html"{" aria-current=page" if fname == "more.html" else ""}>More</a>
<button class="theme" type="button" aria-label="Switch light or dark theme" onclick="csTheme()">{icon("contrast")}</button></nav>
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
                ev_html += (f'<li><span class="st {"ok" if ev.get("verified") else "bad"}">{icon("pass" if ev.get("verified") else "fail")}{ok}</span> '
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


# ---------------------------------------------------------------- overview.html (the numbers)

def seeded_rows(D: Data):
    """Each seeded bug with its routing after the reviews and any reviewer finding that cites the planted line."""
    import scene  # site/scene.py: same rule as the main screen's "sneak a bug in" pins
    final = {r["change"]: r for r in D.results.get("changes", [])}
    out = []
    for m in D.mutants:
        f = final.get(m["id"], {})
        mut = {"file": m["file"], "line": m["line"]}
        rpin, rname = scene.reviewer_pin(m["id"], mut, f.get("why") or []) if m.get("file") and m.get("line") else (None, None)
        out.append({**m, "final_tier": f.get("tier") or m["tier"], "final_owner": f.get("owner") or m["owner"],
                    "failed": [c["id"] for c in m["checks"] if c["status"] == "fail"], "rname": rname, "rpin": rpin})
    return out


def new_flags(D: Data, surv: list) -> int:
    """Test survivors where a reviewer flagged the planted line and had not flagged that line on the unmutated
    original (results.json seeded_reviewed): the conservative count, stated next to the by-location one."""
    sr = {r["change"]: r for r in D.results.get("seeded_reviewed", [])}
    def new(s):
        r = sr.get(s["id"], {})
        same = r.get("same_line_flagged_on_original") or {}
        return any(v and not same.get(k) for k, v in (r.get("planted_line_flagged") or {}).items())
    return sum(new(s) for s in surv)


def build_index(D: Data, n: dict) -> str:
    """overview.html: three huge numbers, each with a caption of at most 8 words, each linking to its source."""
    nums = []
    if n.get("h_esc") is not None:
        sent = n["h_esc"] - n["h_esc_cleared"]
        nums.append((f'{sent}<small>/{n["h_esc"]}</small>', "later-reverted real PRs sent to a human",
                     f"{BLOB}measurement/history/results.md", f'{sent} of {n["h_esc"]}'))
    if n.get("mut_checks") is not None:
        nums.append((f'{n["mut_checks"]}<small>/{n["mut_total"]}</small>', "planted bugs caught by tests and checks",
                     f"{BLOB}measurement/results.md", f'{n["mut_checks"]} of {n["mut_total"]}'))
    if n.get("rt_total"):
        nums.append((f'{n["rt_stopped"]}<small>/{n["rt_total"]}</small>', "attacks on its own pipeline stopped",
                     f"{BLOB}docs/security/REDTEAM.md", f'{n["rt_stopped"]} of {n["rt_total"]}'))
    big = "".join(f'<a class="big" href="{h}" aria-label="{e(lab)} {e(cap)}"><b aria-hidden="true">{a}</b><span>{e(cap)}</span></a>' for a, cap, h, lab in nums)
    body = f"""
<section class="wrap bignums" aria-labelledby="h-nums"><h1 id="h-nums" class="sr">The numbers</h1>{big}</section>
"""
    return page("overview.html", "Countersign: the numbers", body, desc=hero_text(n), cls="numbers")


# ---------------------------------------------------------------- attack.html (moved into the main screen)

def build_attack(D: Data, n: dict) -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sneak a bug past Countersign</title>
<meta http-equiv="refresh" content="0; url=index.html#sneak">
</head><body><p><a href="index.html#sneak">Sneak a bug in: it moved to the main screen.</a></p></body></html>
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
        rows.append([f'<a href="{e(p["url"])}">#{p["pr"]}</a>', e(p["title"]), e(D.labels.get(p["pr"], "")), tier(r["tier"]),
                     f'<span class="mono nw">{e(why)}</span>'])
    hm = h["modes"]["ci-credited"]
    return f"""
<section class="wrap" id="history" aria-labelledby="shist"><h2 id="shist">Real escapes from MessagePack's history</h2>
<p class="prose">{hm['n']} merged upstream PRs replayed under the signed mandate (v{e(str((h.get('mandate') or {}).get('version', '?')))}, the version signed when the replay ran), no AI reviews. {hm['escapes']} were later reverted or fixed; the AI would have cleared {hm['confusion']['escape_cleared']} of them and {hm['confusion']['clean_cleared'] + hm['confusion']['escape_cleared']} PRs in all.</p>
{table(['PR', 'Title', 'What happened later', 'Tier', 'Deciding rule'], rows, cls='dense stack')}
<p class="foot-note">Limits: written by people, not agents; build and tests credited as passed; labels are our judgement by a fixed rule; {hm['confusion']['clean_cleared']} cleared PRs with 0 escapes still allows up to about 12% (rule of three). {src('measurement/history/README.md', 'method')} · {src('measurement/history/labels.yaml', 'labels')} · {src('measurement/history/results.md', 'all ' + str(hm['n']) + ' PRs')}</p>
</section>"""


# ---------------------------------------------------------------- tour.html

def more(summary: str, inner: str) -> str:
    return f'<details class="more"><summary>{summary}</summary>{inner}</details>'


def build_tour(D: Data, n: dict) -> str:
    """Six steps, each one sentence and one visual, all read from change 2234's records. Step 6 is the ledger attack."""
    import scene  # site/scene.py: the same cited hunk as the first screen's "Show me where"
    from countersign.pack_render import _marks, _signoff, _why  # the pack's own first-screen card
    p = D.packs.get("2234") or {}
    f = D.facts.get("2234") or {}
    d = f.get("diff", {})
    steps = []

    # 1 the change
    bf = d.get("by_file", [])
    mx = max((x["ins"] + x["del"] for x in bf), default=1) or 1
    dstat = "".join(f'<li><code title="{e(x["path"])}">{e(x["path"].rsplit("/", 1)[-1])}</code><span class="muted">{e(x["kind"])}</span>'
                    f'<span class="nbar"><i style="width:{max(2, round(100 * (x["ins"] + x["del"]) / mx))}%"></i></span><span class="mono">+{x["ins"]} −{x["del"]}</span></li>' for x in bf)
    steps.append(("The change", f'An AI agent wrote this {d.get("files", "?")}-file fix for issue #2234.',
                  f'<ul class="dstat">{dstat}</ul>', src('evidence/2234/facts.json')))

    # 2 do the new tests fail without the fix?
    ft = next((c for c in f.get("checks", []) if c["id"] == "tests.fail_without_fix"), {}).get("tests", [])
    still = sum(t["outcome"] == "passed" for t in ft)
    tiles = "".join(f'<li class="{"weak" if t["outcome"] == "passed" else "ok"}">{icon("partial" if t["outcome"] == "passed" else "pass")}'
                    f'<code>{e(short_test(t["name"]))}</code><span>{"passes without the fix" if t["outcome"] == "passed" else "fails without the fix"}</span></li>'
                    for t in sorted(ft, key=lambda t: t["outcome"] != "passed"))
    steps.append(("The tests", f"Undo the fix and {still} of its {len(ft)} new tests still pass, so they prove nothing.",
                  f'<ul class="tiles">{tiles}</ul>', src('evidence/2234/facts.json')))

    # 3 the reviewers
    rows = (p.get("panel") or {}).get("rows", [])
    def vline(r):
        v = list(r["verdicts"].values())
        no = len(v) - v.count("met")
        return (f'<li class="{"bad" if no else "ok"}">{icon("fail" if no else "pass")}<span class="who">{e(r["reviewer"].capitalize())}</span>'
                f'<span>{f"{no} of {len(v)} not met" if no else f"all {len(v)} met"}</span><span class="muted">{e(r.get("vendor", ""))}</span></li>')
    steps.append(("The reviewers", "Three AI reviewers from three vendors; a requirement counts only if all say met.",
                  f'<ul class="vlist">{"".join(vline(r) for r in rows)}</ul>', src('packs/2234/pack.json')))

    # 4 the finding, on its line
    code = scene.Code()
    sd = scene.story_data()
    h = scene.where_hunk(code, sd)
    vis = ""
    if h:
        pin = f'<div class="pin" role="note">{icon("fail")}<span>Untouched by the fix</span></div>' if h["touched"] else ""
        vis = f'<div class="hunk"><div class="file">{e(h["file"].rsplit("/", 1)[-1])}</div>{scene.code_rows(h["rows"], h["pin"], pin)}</div>'
    steps.append(("The finding", f"{sd['finder']} showed it fixes a different bug than the issue reports, citing the exact line.",
                  vis, src('packs/2234/pack.json')))

    # 5 the owner decides
    so = _signoff(p) if p else None
    marks = "".join(f'<li class="m-{c}">{icon(GLYPH.get(g, "unknown"))}<span>{e(w)}</span></li>' for c, g, w in _marks(p, so)) if p else ""
    owner = p.get("owner") or "The owner"
    steps.append(("The owner", f"{owner} gets one screen and signs the decision under their name.",
                  f'<a class="mini-card" href="packs/2234/pack.html"><span class="pill {e(p.get("tier", ""))}">{icon(TIER_ICON.get(p.get("tier", ""), "unknown"))}<b>{e(str(p.get("tier", "")).upper())}</b>{icon("arrow_forward", "arr")}{e(owner)}</span>'
                  f'<span class="why"><b>Why:</b> {e(_why(p)) if p else ""}</span><ul class="marks">{marks}</ul><span class="open">Open the evidence pack →</span></a>',
                  src('packs/2234/pack.json') + ' · ' + src('ledger/ledger.jsonl')))

    # 6 the ledger: the attack
    steps.append(("Forge it", "Every sign-off is signed and chained: edit one and the check fails.",
                  '<p class="ctas"><button class="btn primary" type="button" id="tamper">1. Tamper</button><button class="btn" type="button" id="rehash">2. Recompute the hash</button><button class="btn" type="button" id="reset">Reset</button></p>'
                  '<div id="lstatus" class="banner" aria-live="polite"></div><div id="ledger" class="ledger"></div>',
                  src('ledger/ledger.jsonl') + ' · ' + src('countersign/ledger.py')))

    secs = "".join(f'<section class="tstep" id="s{i + 1}" data-n="{i + 1}" aria-labelledby="t{i + 1}"{"" if i == 0 else " hidden"}>'
                   f'<p class="kick">{i + 1}. {e(t)}</p><h1 id="t{i + 1}">{s}</h1><div class="tvis">{v}</div>'
                   f'{f"<p class=foot-note>{sr}</p>" if sr else ""}</section>' for i, (t, s, v, sr) in enumerate(steps))
    dots = "".join(f'<a href="#{i + 1}" class="dot" data-n="{i + 1}" title="{e(t)}">{i + 1}<span>{e(t)}</span></a>' for i, (t, *_r) in enumerate(steps))
    body = f"""
<div class="wrap tour">
<nav class="dots" aria-label="Tour steps">{dots}</nav>
{secs}
<div class="tnav"><button class="btn" id="prev" type="button">← Back</button><span id="pos" class="muted"></span><button class="btn primary" id="next" type="button">Next →</button></div>
</div>"""
    ledger_js = LEDGER_JS.replace("@@FAIL@@", icon("fail")).replace("@@PASS@@", icon("pass"))
    js = ("var LEDGER=" + json.dumps(D.ledger) + ";var PUB=" + json.dumps(D.pubkeys) + ";" + TOUR_JS + ledger_js)
    return page("tour.html", "How it works: change 2234 in six steps", body, js=js, cls="has-tour")


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
  var r=document.createElement("div");r.className="lres";var dt=document.createElement("details"),sm=document.createElement("summary");sm.textContent="edit line "+(i+1);dt.appendChild(sm);dt.appendChild(ta);
  if(ledgerOpen[i])dt.open=true;dt.addEventListener("toggle",function(){ledgerOpen[i]=dt.open});d.appendChild(r);d.appendChild(dt);box.appendChild(d)});check()}
var ledgerOpen={};
async function check(){var prev="0".repeat(64),bad=[],sigNA=false;
 for(var i=0;i<work.length;i++){var e=work[i],p=[],line=i+1;
  if(e.seq!==line)p.push("seq is "+e.seq+", expected "+line);
  if(e.prev!==prev)p.push("prev does not match the hash of line "+(line-1)+" (chain broken)");
  if(hashOf(e)!==e.hash)p.push("content does not match its hash (edited after it was written)");
  var s=await sigOk(e);if(s===false)p.push("signature does not verify against keys/"+String(e.signer).toLowerCase()+".pub");if(s===null)sigNA=true;
  prev=e.hash;var r=document.querySelectorAll(".lres")[i];
  if(r)r.innerHTML=p.length?'<span class="st bad">@@FAIL@@line '+line+"</span> "+p.join("; "):'<span class="st ok">@@PASS@@line '+line+"</span> "+e.type+" by "+e.signer+", "+e.ts+(s?" · signature valid":"");
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


DEMO_URL = "https://countersign.toivo.dev/"
# demo PR #11 (demo-docs1, tier notify): opened 14:04:15, merged 14:04:55 UTC, from the GitHub API; docs/MEASUREMENT.md
DOCS_FIX_PR, DOCS_FIX_SECONDS = 11, 40


def build_pitch(D: Data, n: dict) -> str:
    """One idea per slide, in the order the demo video tells it. The deck's own message and speaker note are the notes (N).

    Slots 1, 3 and 5 are also filmed by scripts/video (v2_scenes_*.py): keep the title's repo URL, the mandate's
    heading and .pipe chips (facts first, reviewers second), and the .chg chips with their tier .badge."""
    import scene  # site/scene.py: the same story data and cited hunk as the landing page
    slides = {s["n"]: s for s in parse_deck(rt("docs/pitch/deck.md"))}
    rows = D.change_rows()
    sv = scene.sync_values()
    p = D.packs.get("2234") or {}
    sd = scene.story_data()
    owner = p.get("owner") or "the owner"
    mark = icon("check_box", "sig", fill=1)
    repo, demo = REPO_URL.replace("https://", ""), DEMO_URL.replace("https://", "").rstrip("/")

    def link(url, text):
        return f'<a href="{url}">{e(text)}</a>'

    V = {}
    # 2 green CI, wrong bug
    ticks = []
    if sd["builds"]:
        ticks.append("Builds")
    if sd["tests"]:
        ticks.append(f'{sd["tests"]} tests pass')
    if sd["allmet"]:
        ticks.append("AI reviewer: requirements met")
    V[2] = ("An AI agent wrote this fix.",
            f'<p class="issue">#2234 {e(sd["title"])}</p>'
            '<ul class="ticks">' + "".join(f'<li>{icon("pass", "g")}<span>{e(t)}</span></li>' for t in ticks) + "</ul>"
            + (f'<p class="wrong">{icon("fail", "g")}<span>It fixes the wrong bug.</span></p>' if sd["finding"] else ""))
    # 3 the mandate
    V[3] = ("A signed mandate decides what AI may clear.",
            "<div class='pipe'>" + "".join(f"<span>{x}</span>" for x in ["facts", "three reviewers", "citations re-checked", "decide", "owner signs"]) + "</div>"
            f'<div class="split"><div>{tier("silent")} {tier("notify")}<p>the AI may clear</p></div>'
            f'<div>{tier("ask")} {tier("block")}<p>a named human signs</p></div></div>')
    # 4 the line the fix never touches
    h = scene.where_hunk(scene.Code(), sd)
    vis = ""
    if h:
        pin = f'<div class="pin" role="note">{icon("fail", "g")}<span>Untouched by the fix</span></div>' if h["touched"] else ""
        edits = (f'<div class="r gap"><span class="n"></span><span class="c">⋯ the fix edits lines {h["edits"][0]}–{h["edits"][1]} instead</span></div>'
                 if h["touched"] and h["edits"] else "")
        vis = f'<div class="hunk"><div class="file">{e(h["file"].rsplit("/", 1)[-1])}</div>{scene.code_rows(h["rows"], h["pin"], pin)}{edits}</div>'
    facts = []
    if sv.get("t2234_pass_without_fix") and sv.get("t2234_new_tests"):
        facts.append(("partial", "warn", f'{sv["t2234_pass_without_fix"]} of {sv["t2234_new_tests"]} new tests pass without the fix'))
    if (p.get("reproduced") or {}).get("claude:C2") == "reproduced":
        facts.append(("fail", "bad", "Still crashes on Key(null): reproduced"))
    V[4] = ("The reported bug is on a line the fix never touches.",
            vis + '<ul class="facts">' + "".join(f'<li class="{c}">{icon(g, "g")}<span>{e(t)}</span></li>' for g, c, t in facts) + "</ul>"
            + (f'<p class="out"><span class="pill {e(p["tier"])}">{icon(TIER_ICON.get(p["tier"], "unknown"))}<b>{e(p["tier"].upper())}</b>'
               f'{icon("arrow_forward", "arr")}{e(owner)}</span></p>' if p.get("tier") else ""))
    # 5 depth follows risk; the docs fix that cleared
    real = [r for r in D.results.get("changes", []) if not r.get("mutant") and not r["change"].startswith("var-")] or [{"change": r["change"], "tier": r["tier"]} for r in rows]
    cleared = [r for r in real if r.get("tier") not in HUMAN_TIERS]
    docs = next((r for r in real if r["change"] == "demo-docs1" and r.get("tier") not in HUMAN_TIERS), None)
    V[5] = ("Every change says why. Low risk can clear." if cleared else "Every change reached a human, with a reason.",
            '<div class="tiers">' + "".join(f'<span class="chg"><code>{e(r["change"])}</code>{tier(r.get("tier"))}</span>' for r in real) + "</div>"
            + (f'<p class="out ok">{icon("pass", "g")}<span>A docs fix: cleared by the AI alone, merged in {DOCS_FIX_SECONDS} s</span>'
               f'<span class="src">demo PR #{DOCS_FIX_PR}</span></p>' if docs else ""))
    # 6 the owner signs on GitHub
    cap = rj("site/data/pr-capture.json") or {}
    pr = next((x for x in cap.get("prs", []) if x.get("number") == 2), None)
    if pr:
        app = (pr.get("sticky_comment") or {}).get("app") or {}
        V[6] = (f"{owner} signs on GitHub. The merge is blocked.",
                f'<div class="ghpr"><p class="prt">{e(pr["title"])} <span class="muted">#{pr["number"]}</span></p>'
                f'{pr_merge_box(pr, app.get("name") or "GitHub App")}</div>')
    # 7 the ledger
    nled = len(D.ledger or [])
    V[7] = ("Every sign-off is signed and chained.",
            '<ol class="chain">'
            f'<li class="ok">{icon("pass", "g")}<b>Ledger OK</b><span>{nled} entries, every signature verifies</span></li>'
            f'<li class="bad">{icon("fail", "g")}<b>Edit one line</b><span>invalid: hash mismatch</span></li>'
            f'<li class="bad">{icon("fail", "g")}<b>Recompute the hash</b><span>invalid: signature fails</span></li></ol>')
    # 8 the numbers (the same three as overview.html)
    big = []
    if n.get("h_esc") is not None:
        big.append((n["h_esc"] - n["h_esc_cleared"], n["h_esc"], "later-reverted real PRs sent to a human"))
    if n.get("mut_checks") is not None:
        big.append((n["mut_checks"], n["mut_total"], "planted bugs caught by tests and checks"))
    if n.get("rt_total"):
        big.append((n["rt_stopped"], n["rt_total"], "attacks on its own pipeline stopped"))
    V[8] = ("Measured, not claimed.",
            '<div class="bigs">' + "".join(f'<div><b>{a}<small>/{b}</small></b><span>{e(c)}</span></div>' for a, b, c in big) + "</div>")
    # 9 limits
    V[9] = ("It says where it stops.",
            '<div class="tiers lim">' + "".join(f"<span>{x}</span>" for x in ["can't judge intent", "only as good as the requirement", "net8.0 / Linux only", "trust over time is simulated"]) + "</div>")
    # 10 try it
    V[10] = ("Try it on one repo.",
             '<p class="sub">One area, one owner, one signed mandate.</p>'
             f'<p class="urls stack"><span>Demo {link(DEMO_URL, demo)}</span><span>Code {link(REPO_URL, repo)}</span></p>'
             '<p class="urls"><span>Run <code>scripts/demo.sh</code></span><span>Team <b>Toivo · Rene</b></span></p>')

    out = []
    N = len(slides)
    for i, k in enumerate(sorted(slides)):
        s = slides[k]
        head, vis = V.get(k, (re.sub(r"<[^>]+>", "", md_inline(s["message"])), ""))
        note = f'<p><b>{md_inline(s["message"])}</b></p><p>{md_inline(s["note"])}</p>'
        foot = f'<p class="sfoot"><span>{mark}Countersign</span><span>{e(demo)}</span><span>{i + 1} / {N}</span></p>'
        if k == 1:
            punch = "AI clears what it can prove. A named human signs the rest."
            out.append(f'<section class="slide title-slide" data-i="{i}"><div class="sl"><h1>{mark}Countersign</h1>'
                       f'<p class="punch">{punch}</p><p class="urls"><span>Demo {link(DEMO_URL, demo)}</span><span>Code {link(REPO_URL, repo)}</span></p>'
                       f'<p class="event">Junction 2026 · Tieto: Earned Trust in AI Code</p></div>'
                       f'<aside class="note">{note}<p>{hero_line(n)}</p></aside></section>')
            continue
        if k == max(slides):
            head = f"{mark}{e(head)}"
        else:
            head = e(head)
        out.append(f'<section class="slide s{k}" data-i="{i}"><div class="sl"><h2>{head}</h2><div class="vis">{vis}</div></div>{foot}'
                   f'<aside class="note">{note}</aside></section>')
    body = f"""<div class="deck" id="deck">{''.join(out)}</div>
<div class="deckbar"><button class="btn" id="dprev" type="button" aria-label="Previous slide">{icon("arrow_back")}</button><span id="dpos" class="muted"></span>
<button class="btn" id="dnote" type="button" aria-label="Speaker notes (N)">Notes</button><button class="btn" id="dfull" type="button" aria-label="Full screen (F)">{icon("fullscreen")}</button>
<button class="btn" id="dnext" type="button" aria-label="Next slide">{icon("arrow_forward")}</button></div>"""
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
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 var(--sans);font-variant-numeric:tabular-nums}
a{color:var(--accent);text-underline-offset:2px}a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}.top nav a:focus-visible{outline-offset:-2px}
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
.bar{display:flex;align-items:center;gap:16px;min-height:56px}
.mark{font-weight:600;color:var(--fg);text-decoration:none;display:flex;align-items:center;gap:8px}
.i.sig{color:var(--fg)}
.brand{margin:0;display:flex;align-items:baseline;gap:0 10px;flex-wrap:wrap;flex:1;min-width:0}.tag{color:var(--muted);font-size:14px}
.top nav{display:flex;gap:12px;align-items:center;margin-left:auto}
.top nav a{color:var(--muted);text-decoration:none;padding:6px 8px;border-radius:6px;font-size:14px;white-space:nowrap}
.top nav a:hover{color:var(--fg);background:var(--bg2)}.top nav a[aria-current]{color:var(--fg);font-weight:600;box-shadow:inset 0 -2px 0 var(--accent);border-radius:0}
.theme{display:inline-flex;align-items:center;background:none;border:0;color:var(--muted);font:inherit;font-size:20px;padding:6px;border-radius:6px;cursor:pointer}.theme:hover{color:var(--fg);background:var(--bg2)}
.hero{padding-top:48px}.hero h1{max-width:44ch}.hero .muted{font-size:14px}
.legend{display:flex;flex-wrap:wrap;gap:8px 24px;margin:8px 0 16px;font-size:14px;color:var(--muted)}.legend div{display:flex;gap:8px;align-items:center}.legend dt{white-space:nowrap;display:inline-flex;gap:6px}.legend dd{margin:0}.hero.small h1{max-width:none}
.h-sm{font-size:20px}
.foot{border-top:1px solid var(--border);margin-top:64px;padding:24px 0;color:var(--muted);font-size:14px}.foot p{margin:0 0 8px}
.foot-note{font-size:12px;color:var(--muted);margin-top:8px}
a.src{font-family:var(--mono);font-size:12px;color:var(--muted)}a.src:hover{color:var(--accent)}
/* status */
.st{font:600 12px/1.5 var(--mono);white-space:nowrap;text-transform:uppercase;display:inline-flex;align-items:center;gap:.35em;vertical-align:-.2em}.st .i{width:1.3em;height:1.3em}.st:not(:has(.i)){vertical-align:baseline}
li.gl{list-style:none;display:flex;align-items:flex-start;gap:6px;margin-left:-1.4em}li.gl .i{width:1.15em;height:1.15em;margin-top:.17em}li.gl.ok .i{color:var(--ok)}li.gl.bad .i{color:var(--bad)}li.gl.warn .i{color:var(--warn)}.st.ok{color:var(--ok)}.st.bad{color:var(--bad)}.st.warn{color:var(--warn)}
.badge{justify-self:start;display:inline-flex;align-items:center;gap:4px;vertical-align:middle;font:600 12px/20px var(--mono);padding:1px 10px 1px 6px;border:1px solid var(--border);border-radius:999px;white-space:nowrap}.badge .i{width:15px;height:15px}.badge .i.arr{width:13px;height:13px;opacity:.8}
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
.pick{display:flex;flex-direction:column;align-items:flex-start;text-align:left;gap:2px;padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--fg);cursor:pointer;font:14px var(--sans)}
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
.lres{font-size:14px;word-break:break-word}
.lline{display:grid;grid-template-columns:1fr auto;gap:4px 12px;align-items:baseline;padding:6px 0;border-top:1px solid var(--border)}.lline details{display:contents}
.lline summary{cursor:pointer;color:var(--accent);font-size:13px;white-space:nowrap}.lline textarea{grid-column:1/-1}
code.q1{font-size:12px}code.nwc{white-space:nowrap}.nw{white-space:nowrap;font-size:12px}
/* pitch: one idea per slide, centred, in the landing page's big type */
body.pitch .foot{display:none}body.pitch main{padding:0}
.deck{position:relative}
.slide{display:none;min-height:calc(100vh - 57px - 56px);padding:32px 24px;position:relative}
.slide.on{display:flex;flex-direction:column;justify-content:center}
.sl{max-width:1100px;width:100%;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center}
.slide h2{font-size:clamp(26px,3.6vw,46px);line-height:1.15;max-width:24ch;margin:0 0 28px;text-wrap:balance;display:flex;align-items:center;justify-content:center;gap:.3em}
.slide h2 .i.sig{width:1em;height:1em;flex:none}
.slide .vis{font-size:clamp(16px,1.6vw,22px);width:100%;display:flex;flex-direction:column;align-items:center;gap:22px}
.title-slide h1{font-size:clamp(40px,6.4vw,84px);display:flex;align-items:center;gap:.2em;margin:0 0 12px;letter-spacing:-.02em}
.i.sig{width:1em;height:1em}.deckbar .btn .i{width:18px;height:18px}
.punch{font-size:clamp(22px,2.8vw,36px);max-width:28ch;line-height:1.3;margin:0 0 36px;text-wrap:balance}
.urls{display:flex;flex-wrap:wrap;justify-content:center;gap:12px 40px;margin:0 0 24px;font-size:clamp(16px,1.7vw,22px);color:var(--muted)}
.urls a{font:600 1em var(--mono);margin-left:.4em}
.urls.stack{flex-direction:column;align-items:center;gap:14px;font-size:clamp(18px,2vw,26px);margin:8px 0 0}.urls code{font:600 1em var(--mono);border:0;background:none;color:var(--fg);margin-left:.4em}.urls b{margin-left:.4em;color:var(--fg)}
.event{color:var(--muted);font-size:clamp(14px,1.3vw,17px);margin:0}
.slide .sub{font-size:1.15em;margin:-12px 0 4px;color:var(--muted)}
.sfoot{display:none;position:absolute;left:48px;right:48px;bottom:20px;margin:0;grid-template-columns:1fr auto 1fr;color:var(--muted);font-size:14px}.sfoot span:last-child{text-align:right}
.sfoot span:first-child{display:inline-flex;align-items:center;gap:6px;font-weight:600;color:var(--fg)}.sfoot .i.sig{width:18px;height:18px}
.note{display:none;max-width:1040px;margin:24px auto 0;width:100%;border-top:1px dashed var(--border);padding-top:12px;color:var(--muted);font-size:15px}
body.notes .note{display:block}
.deckbar{position:sticky;bottom:0;display:flex;gap:8px;justify-content:center;align-items:center;padding:8px;border-top:1px solid var(--border);background:var(--bg)}
.pipe{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;align-items:center}
.pipe span{border:1px solid var(--border);border-radius:8px;padding:10px 16px;font:1em var(--mono);background:var(--bg2)}
.pipe span+span::before{content:"→ ";color:var(--muted)}
.split{display:grid;grid-template-columns:1fr 1fr;gap:20px;width:100%;max-width:760px}
.split>div{border:1px solid var(--border);border-radius:10px;padding:18px}.split p{margin:10px 0 0}
.split .badge,.chg .badge{font-size:.8em;line-height:1.6}.split .badge .i,.chg .badge .i{width:1.1em;height:1.1em}
.tiers{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;align-items:center;max-width:960px}
.chg{display:inline-flex;gap:8px;align-items:center;border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:1em}
.lim span{border:1px dashed var(--border);border-radius:8px;padding:12px 20px;font-size:1.1em}
.slide .ticks{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 32px;font-size:1.3em;font-weight:600}
.slide .ticks li{display:inline-flex;align-items:center;gap:.35em}.slide .ticks .g{color:var(--ok)}
.slide .i.g{width:1.15em;height:1.15em;flex:none}
.slide .issue{margin:-14px 0 0;color:var(--muted);font-size:.9em}
.slide .wrong{margin:10px 0 0;font-size:clamp(34px,5vw,64px);font-weight:800;line-height:1.15;color:var(--bad);display:inline-flex;align-items:center;gap:.3em}
.slide .wrong .g{width:1em;height:1em}
.slide .hunk{width:100%;max-width:820px;text-align:left;margin:0}
.facts{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:10px 32px;font-weight:600}
.facts li{display:inline-flex;align-items:center;gap:.35em}.facts .warn .g{color:var(--warn)}.facts .bad .g{color:var(--bad)}
.out{margin:0;display:inline-flex;align-items:center;gap:.4em}.out.ok{font-weight:600}.out.ok .g{color:var(--ok)}
.out .src{color:var(--muted);font-weight:400;font-size:.8em;margin-left:.4em}
.slide .pill{font-size:1.1em}
.ghpr{width:100%;max-width:760px;text-align:left}.ghpr .prt{font-size:1.05em;margin:0 0 4px}.ghpr .ghs{font-size:.8em}.ghpr .ghs .muted{font-size:1em}
.chain{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:16px;width:100%;max-width:1000px;counter-reset:c}
.chain li{display:flex;flex-direction:column;align-items:center;gap:8px;border:1px solid;border-radius:12px;padding:24px 16px}
.chain li .g{width:1.8em;height:1.8em}.chain li b{font-size:1.15em}.chain li span{color:var(--muted);font-size:.9em}
.chain li.ok{border-color:var(--ok);background:var(--ok-bg)}.chain li.ok .g{color:var(--ok)}
.chain li.bad{border-color:var(--bad);background:var(--bad-bg)}.chain li.bad .g{color:var(--bad)}
.bigs{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;width:100%}
.bigs div{display:flex;flex-direction:column;align-items:center;gap:12px}
.bigs b{font:700 clamp(64px,9vw,120px)/1 var(--sans);letter-spacing:-.03em}.bigs b small{font-size:.45em;color:var(--muted);font-weight:600}
.bigs span{color:var(--muted);max-width:20ch;font-size:1.05em}
/* numbers page */
.fold-hero{min-height:calc(100vh - 57px);display:flex;flex-direction:column;justify-content:center;padding-top:0}
.small{font-size:14px}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0 16px}
.num{display:flex;flex-direction:column;gap:4px;padding:20px;border:1px solid var(--border);border-radius:6px;color:var(--fg);text-decoration:none}
.num:hover{border-color:var(--accent)}.num b{font:600 56px/1 var(--mono)}.num b small{font-size:.5em;color:var(--muted);font-weight:400}.num span{color:var(--muted)}.num i{display:block;font-style:normal;font-size:13px;margin-top:2px}
tr:target td{background:var(--accent-bg)}
/* tour visuals */
.tvis{margin:16px 0}.tvis .scroll{max-width:760px}
.dstat{list-style:none;padding:0;margin:0;max-width:720px}
.dstat li{display:grid;grid-template-columns:minmax(0,1fr) 56px 120px 80px;gap:12px;align-items:center;padding:8px 0;border-top:1px solid var(--border);font-size:14px}
.dstat li:first-child{border-top:0}.dstat code{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.dstat .mono{text-align:right}
.nbar{height:8px;background:var(--bg2);border-radius:4px;overflow:hidden}.nbar i{display:block;height:100%;background:var(--muted)}
.tiles{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px}
.tiles li{border:1px solid;border-radius:6px;padding:10px 12px;display:grid;grid-template-columns:20px 1fr;gap:2px 8px;font-size:14px;align-content:start}
.tiles li .i{grid-row:span 2;width:20px;height:20px}.tiles li code{border:0;background:none;padding:0;overflow-wrap:anywhere}.tiles li span{font-size:12px}
.tiles li.ok{border-color:var(--ok);color:var(--ok);background:var(--ok-bg)}.tiles li.weak{border-color:var(--warn);color:var(--warn);background:var(--warn-bg)}
.tiles li code{color:var(--fg)}
.cites li{margin-bottom:12px;max-width:90ch}
details.more{margin:8px 0;max-width:90ch}details.more summary{cursor:pointer;color:var(--accent);font-size:14px;padding:4px 0}
details.more[open] summary{margin-bottom:8px}
.signcard ol{padding-left:20px}.signcard li{margin-bottom:8px}
.tstep .lead{font-size:20px;max-width:60ch}
.ledger{margin-top:8px}
/* pitch visuals */
.tiles3{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;width:100%}
.tile{border:1px solid var(--border);border-radius:10px;padding:20px;display:flex;flex-direction:column;gap:8px;text-align:left}
.tile span{color:var(--muted);font-size:.85em}.tile b{font:600 1.05em/1.3 var(--mono);overflow-wrap:anywhere}.tile b a{color:var(--accent)}
/* small screens */
@media (max-width:860px){.story{grid-template-columns:1fr}.stat{border-left:0;border-top:1px solid var(--border)}.stat:first-child{border-top:0}}
@media (max-width:600px){.hero{padding-top:24px}.lead{font-size:16px}section.wrap{padding-top:32px}
.top{position:static}.bar{gap:8px;padding:8px 16px;min-height:0}
h1{font-size:22px}.hero h1{font-size:22px}.lead{font-size:15px}.h-sm{font-size:18px}
table.stack thead{display:none}table.stack tr{display:block;border-bottom:1px solid var(--border);padding:8px 0}table.stack tr:last-child{border-bottom:0}
table.stack td{display:grid;grid-template-columns:96px 1fr;gap:8px;border:0;padding:2px 12px}table.stack td::before{content:attr(data-label);padding-top:2px;font:600 11px/1.5 var(--sans);text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
.card{padding:12px}.rows li{padding:4px 0}.picker{grid-template-columns:repeat(3,1fr)}.two{grid-template-columns:1fr;gap:16px}.pick{padding:8px}table.stack td.n{text-align:left}.verdict{padding:12px}
.big{font-size:24px}.tstep h1{font-size:22px}.tstep .lead{font-size:17px}.nums{grid-template-columns:1fr;gap:8px}.num{flex-direction:row;align-items:baseline;gap:12px;padding:12px 16px}.num b{font-size:36px;min-width:3.2em}.dstat li{grid-template-columns:minmax(0,1fr) 72px;gap:4px 8px}.dstat li .muted,.dstat .nbar{display:none}.dot span{display:none}.slide{padding:24px 16px}.diffs li{padding-left:40px}
th,td{padding:6px 8px}}
@media print{.top,.deckbar,.tnav{display:none}.slide{display:block!important;page-break-after:always;min-height:auto}}
/* prs.html: a GitHub PR, minimal */
.prs .cap{font-size:14px;margin:24px 0 16px;max-width:none}
.pr-grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:24px;align-items:start}
.pr-t{font-size:24px;font-weight:400;margin:0 0 8px}.pr-t.sm{font-size:16px;font-weight:600}
.pr-meta{font-size:14px;margin:0 0 8px;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.open{display:inline-block;font:600 12px/24px var(--sans);padding:0 10px;border-radius:999px;border:1px solid var(--border);background:var(--bg2)}
.lbl{display:inline-block;font:600 12px/20px var(--sans);padding:0 8px;border-radius:999px;border:1px solid var(--lc);color:var(--fg);background:color-mix(in srgb,var(--lc) 14%,transparent)}
.botl{display:inline-block;font:500 11px/16px var(--sans);padding:0 6px;border:1px solid var(--border);border-radius:999px;color:var(--muted)}
.ghc{border:1px solid var(--border);border-radius:6px;margin:16px 0}
.ghc-h{background:var(--bg2);border-bottom:1px solid var(--border);padding:8px 16px;font-size:14px;border-radius:6px 6px 0 0}
.ghc-b{padding:16px;font-size:14px;overflow-wrap:break-word}.ghc-b code{overflow-wrap:anywhere}
.md h3{font-size:20px;margin:0 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border)}.md h4,.md h5{font-size:16px;margin:16px 0 8px}
.md table th{text-transform:none;letter-spacing:0;font-size:14px}.md table td:first-child{color:var(--muted);width:30%}
.md blockquote{font-size:14px}.md p,.md ul,.md ol{margin-bottom:12px}
.md details{margin:8px 0}.md summary{cursor:pointer}
.fold{border-top:1px solid var(--border);padding-top:12px;margin-top:4px}.fold>summary{color:var(--accent);font-weight:600}
.ghs{border:1px solid var(--border);border-radius:6px;margin:16px 0;font-size:14px}
.ghs-row{display:grid;grid-template-columns:20px minmax(0,1fr) auto;gap:8px;padding:12px 16px;border-top:1px solid var(--border);align-items:start}.ghs-row>.st .i{width:20px;height:20px}
.ghs-row:first-child{border-top:0}.ghs-row.merge{grid-template-columns:20px minmax(0,1fr)}.ghs-row .st{font-size:14px}
.req{font-size:12px;color:var(--muted);border:1px solid var(--border);border-radius:999px;padding:0 8px}
.pr-side{border:1px solid var(--border);border-radius:6px;padding:16px;margin-bottom:16px;font-size:14px}
.pr-side .ghs{margin-bottom:0}.pr-side .ghs-row{grid-template-columns:20px minmax(0,1fr)}.pr-side .req{grid-column:2;justify-self:start}.pr-side h2{margin-top:0}.t1{line-height:1.6;background:var(--bg2);border-radius:6px;padding:8px 12px;font-size:13px}
@media (max-width:860px){.pr-grid{grid-template-columns:1fr}.pr-t{font-size:20px}.ghs-row{grid-template-columns:20px minmax(0,1fr)}.req{grid-column:2;justify-self:start}}
/* v3: one idea per screen */
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.bignums{min-height:calc(100vh - 220px);display:grid;grid-template-columns:repeat(3,1fr);gap:24px;align-content:center}
.big{display:flex;flex-direction:column;align-items:center;text-align:center;gap:12px;padding:32px 16px;color:var(--fg);text-decoration:none;border-radius:12px}
.big:hover{background:var(--bg2)}.big b{font:700 clamp(64px,9vw,112px)/1 var(--sans);letter-spacing:-.03em}.big b small{font-size:.45em;color:var(--muted);font-weight:600}
.big span{font:400 20px/1.35 var(--sans);color:var(--muted);max-width:18ch}
.tstep .kick{font:600 14px/1.5 var(--sans);color:var(--muted);margin:0 0 4px}.tstep h1{font-size:clamp(24px,3.6vw,34px);max-width:30ch;margin-bottom:24px}
.vlist{list-style:none;padding:0;margin:0;display:grid;gap:8px;max-width:560px}
.vlist li{display:grid;grid-template-columns:24px 110px 1fr auto;gap:12px;align-items:center;padding:12px 16px;border:1px solid var(--border);border-radius:8px;font-size:18px}
.vlist .i{width:1.15em;height:1.15em}.vlist li.ok .i{color:var(--ok)}.vlist li.bad{border-color:var(--bad);background:var(--bad-bg)}.vlist li.bad .i{color:var(--bad)}.vlist .who{font-weight:600}.vlist .muted{font-size:13px}
.hunk{max-width:760px;border:1px solid var(--border);border-radius:10px;padding:8px 0;font:14px/22px var(--mono)}
.hunk .file{font-weight:600;font-size:13px;color:var(--muted);padding:2px 14px 6px}
.hunk .r{display:grid;grid-template-columns:56px 1fr}.hunk .n{color:var(--muted);text-align:right;padding-right:14px}.hunk .c{white-space:pre-wrap;overflow-wrap:anywhere}
.hunk .r.pinned{background:var(--bad-bg);box-shadow:inset 4px 0 var(--bad);font-weight:600}.hunk .r.gap .c{color:var(--muted);font-family:var(--sans)}
.hunk i{font-style:normal}.hunk i.tk{color:#8250df}.hunk i.tc{color:var(--muted);font-style:italic}
.hunk .pin{margin:4px 14px 8px 56px;color:var(--bad);font:700 16px/1.3 var(--sans);display:flex;align-items:center;gap:6px}.pin .i{width:1.15em;height:1.15em}
.mini-card{display:grid;gap:12px;justify-items:start;max-width:520px;padding:20px 24px;border:1px solid var(--border);border-radius:12px;color:var(--fg);text-decoration:none}
.mini-card:hover{border-color:var(--accent)}.mini-card .why{font-size:18px}.mini-card .open{color:var(--accent)}
.pill{border:2px solid currentColor;border-radius:999px;padding:4px 16px 4px 10px;font-size:18px;display:inline-flex;align-items:center;gap:6px}.pill .i{width:1.15em;height:1.15em}.pill .i.arr{width:.9em;height:.9em;opacity:.8}.pill.ask{color:var(--warn);background:var(--warn-bg)}.pill.block{color:var(--bad);background:var(--bad-bg)}
.pill.notify,.pill.silent{color:var(--ok);background:var(--ok-bg)}.pill b{font-family:var(--mono)}
.marks{list-style:none;padding:0;margin:0;display:grid;gap:6px;font-size:17px}.marks li{display:flex;gap:8px;align-items:flex-start}.marks .i{width:1.15em;height:1.15em;margin-top:.17em}.marks .m-ok .i{color:var(--ok)}.marks .m-bad .i{color:var(--bad)}.marks .m-warn .i{color:var(--warn)}
@media (max-width:720px){.bignums{grid-template-columns:1fr;gap:8px;min-height:0;padding-top:16px}.big{padding:20px 8px}.big span{font-size:18px}
.vlist li{grid-template-columns:20px 90px 1fr;font-size:16px}.vlist .muted{display:none}.hunk{font-size:12.5px;line-height:20px}.hunk .r{grid-template-columns:40px 1fr}.hunk .pin{margin-left:40px}}
"""


# ---------------------------------------------------------------- main

# ---------------------------------------------------------------- prs.html: the PR flow as a reviewer sees it on GitHub

def gh_inline(s: str, anchor: str = "c-") -> str:
    """GitHub-flavoured inline Markdown, minimal: code spans, bold, italic, links, and the few HTML tags the sticky
    comment uses (b, sub, a id). Everything else is escaped."""
    lk = re.compile(r"\[((?:[^\]`]|`[^`]*`)+)\]\(([^)\s]+)\)")  # links first: their labels may be code spans
    if lk.search(s):
        out, k = [], 0
        for m in lk.finditer(s):
            href = f"#{anchor}{m.group(2)[1:]}" if m.group(2).startswith("#") else m.group(2)
            out += [gh_inline(s[k:m.start()], anchor), f'<a href="{e(href)}">{gh_inline(m.group(1), anchor)}</a>']
            k = m.end()
        return "".join(out) + gh_inline(s[k:], anchor)
    parts = re.split(r"(`[^`]*`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code>{e(p[1:-1])}</code>")
            continue
        t = e(p)
        t = re.sub(r"&lt;(/?)(b|sub)&gt;", r"<\1\2>", t)
        t = re.sub(r"&lt;a id=&quot;([\w-]+)&quot;&gt;&lt;/a&gt;", lambda m: f'<a id="{anchor}{m.group(1)}"></a>', t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?![*\w])", r"<i>\1</i>", t)
        out.append(t)
    return "".join(out)


def gh_markdown(text: str, anchor: str = "c-") -> str:
    """Block-level Markdown for the sticky comment: headings, paragraphs, quotes, lists, tables, fenced code,
    <details>/<summary>. Not a general renderer; it covers what countersign/github.py writes."""
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    para: list[str] = []

    def flush():
        if para:
            out.append(f"<p>{gh_inline(' '.join(para), anchor)}</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("<!--"):
            i += 1
            continue
        if s.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append(f"<pre><code>{e(chr(10).join(lines[i + 1:j]))}</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^<details( open)?>\s*(?:<summary>(.*)</summary>)?\s*$", s)
        if m:
            flush()
            out.append(f"<details{m.group(1) or ''}>" + (f"<summary>{gh_inline(m.group(2), anchor)}</summary>" if m.group(2) is not None else ""))
            i += 1
            continue
        if s == "</details>":
            flush()
            out.append("</details>")
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", s)
        if h:
            flush()
            lv = min(6, len(h.group(1)) + 1)
            out.append(f"<h{lv}>{gh_inline(h.group(2), anchor)}</h{lv}>")
            i += 1
            continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], rows[1:]
            th = "" if not any(head) else "<thead><tr>" + "".join(f"<th>{gh_inline(c, anchor)}</th>" for c in head) + "</tr></thead>"
            tb = "".join("<tr>" + "".join(f"<td>{gh_inline(c, anchor)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="scroll"><table>{th}<tbody>{tb}</tbody></table></div>')
            continue
        if s.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote><p>{gh_inline(' '.join(q), anchor)}</p></blockquote>")
            continue
        lm = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", ln)
        if lm:
            flush()
            tag = "ol" if lm.group(1)[0].isdigit() else "ul"
            items = []
            while i < len(lines):
                mm = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", lines[i])
                if not mm or (mm.group(1)[0].isdigit()) != (tag == "ol"):
                    break
                gm = re.match(r"^(\S)\s+(.*)$", mm.group(2))
                if gm and gm.group(1) in GLYPH:  # the gate comment's status glyphs, drawn as the site's icons
                    meaning = GLYPH[gm.group(1)]
                    cls = {"pass": "ok", "fail": "bad", "warn": "warn", "partial": "warn", "pending": "warn"}.get(meaning, "")
                    items.append(f'<li class="gl {cls}">{icon(meaning)}<span>{gh_inline(gm.group(2), anchor)}</span></li>')
                else:
                    items.append(f"<li>{gh_inline(mm.group(2), anchor)}</li>")
                i += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        para.append(s)
        i += 1
    flush()
    return "".join(out)


def pr_status_line(st: dict, app_name: str) -> str:
    state = st.get("state")
    glyph, cls, word = {"success": ("pass", "ok", "Successful"), "pending": ("pending", "warn", "Pending"),
                        "failure": ("fail", "bad", "Failing"), "error": ("fail", "bad", "Error")}.get(state, ("unknown", "", state or "?"))
    bot = st.get("creator") or ""
    by = f' · by <span title="{e(bot)}">{e(app_name)} <span class="botl">bot</span></span>' if bot.endswith("[bot]") else (f" · by {e(bot)}" if bot else "")
    return (f'<div class="ghs-row"><span class="st {cls}">{icon(glyph)}</span>'
            f'<div><b class="mono">{e(st.get("context"))}</b> <span class="st {cls}">{word}</span>'
            f'<span class="muted"> — {e(st.get("description"))}{by}</span></div><span class="req">Required</span></div>')


def pr_merge_box(pr: dict, app_name: str, why: bool = True) -> str:
    rows = "".join(pr_status_line(s, app_name) for s in pr.get("statuses", []))
    blocked = pr.get("mergeStateStatus") == "BLOCKED"
    tail = (f'<div class="ghs-row merge"><span class="st bad">{icon("fail")}</span><div><b>Merging is blocked</b>'
            + ('<div class="muted">Required status check <code>countersign/tier</code> has not succeeded. The merge button stays grey.</div>' if why else '') + '</div></div>'
            if blocked else f'<div class="ghs-row merge"><div class="muted">mergeStateStatus: {e(pr.get("mergeStateStatus"))}</div></div>')
    return f'<div class="ghs">{rows}{tail}</div>'


def pr_labels(pr: dict) -> str:
    return "".join(f'<span class="lbl" style="--lc:#{e(x["color"])}">{e(x["name"])}</span>' for x in pr.get("labels", []))


def build_prs(D: Data) -> str | None:
    cap = rj("site/data/pr-capture.json")
    if not cap or not cap.get("prs"):
        return None
    when = dt.datetime.strptime(cap["captured_at"], "%Y-%m-%dT%H:%M:%SZ")
    day = f"{when.day} {when:%b %Y}, {when:%H:%M} UTC"
    repo = cap["repo"]
    by_n = {p["number"]: p for p in cap["prs"]}
    main, side = by_n.get(2), by_n.get(4)
    if not main:
        return None
    sc = main.get("sticky_comment") or {}
    app = sc.get("app") or {}
    app_name = app.get("name") or "GitHub App"
    body = sc.get("body", "")
    cut = body.find("\n### How the owner countersigns")
    first, rest = (body[:cut], body[cut:]) if cut > 0 else (body, "")
    rest_kb = round(len(rest.encode()) / 1024)

    def head(pr: dict, big: bool) -> str:
        t = f'{e(pr["title"])} <span class="muted">#{pr["number"]}</span>'
        return (f'<h1 class="pr-t">{t}</h1>' if big else f'<h2 class="pr-t sm">{t}</h2>') + (
            f'<p class="pr-meta"><span class="open">{"Open" if pr["state"] == "OPEN" else e(pr["state"].title())}</span> '
            f'<b>{e(pr["author"])}</b> wants to merge {pr["commits"]} commit{"s" if pr["commits"] != 1 else ""} into <code>{e(pr["base"])}</code> from <code>{e(pr["head"])}</code>'
            f' <span class="muted">· {pr["changed_files"]} files +{pr["additions"]} −{pr["deletions"]}</span></p>'
            f'<p class="pr-meta">{pr_labels(pr)} <span class="muted">Assignee:</span> {e(", ".join(pr["assignees"]) or "none")}</p>')

    comment = (f'<div class="ghc"><div class="ghc-h"><b>{e(sc.get("user", "").replace("[bot]", ""))}</b> <span class="botl">bot</span>'
               f' <span class="muted">commented · sticky, updated on every push</span></div>'
               f'<div class="ghc-b md">{gh_markdown(first)}'
               + (f'<details class="fold"><summary>The rest of the comment: how the owner countersigns, and the evidence pack ({rest_kb} KB)</summary>{gh_markdown(rest)}</details>' if rest else "")
               + "</div></div>")

    prot = cap.get("protection") or {}
    req = next((c for c in prot.get("required_checks", []) if c.get("context") == "countersign/tier"), {})
    app_id = req.get("app_id")
    t1 = (f'<section class="pr-side" aria-labelledby="t1h"><h2 id="t1h" class="h-sm">Who can turn it green</h2>'
          f'<p class="mono t1">main requires <b>countersign/tier</b><br>from app id <b>{e(app_id)}</b>'
          f'{" = " + e(app_name) if app.get("id") == app_id else ""}'
          f'{"<br>enforced for admins" if prot.get("enforce_admins") else ""}</p>'
          f'<p>An agent can add a workflow that posts <code>countersign/tier: success</code>, but it posts as GitHub Actions, not as this App, '
          f'and the App\'s key is only released to workflows running from <code>main</code>, so branch protection ignores it.</p>'
          f'<p class="foot-note">{src("docs/security/TRIAGE.md", "Security triage T1")} · {src("docs/PR_FLOW.md")}</p></section>')

    p4 = ""
    if side:
        p4 = (f'<section class="pr-side" aria-label="PR {side["number"]}"><h2 class="pr-t sm">{e(side["title"])} <span class="muted">#{side["number"]}</span></h2>'
              f'<p class="pr-meta">{pr_labels(side)} <span class="muted">{side["changed_files"]} files +{side["additions"]} −{side["deletions"]}</span></p>'
              f'{pr_merge_box(side, app_name, why=False)}</section>')

    note = (f'<p class="cap"><b>Captured from the private demo repo on {e(day)}</b>; the repo becomes public on Sunday. '
            f'<a href="https://github.com/{e(repo)}/pull/{main["number"]}">{e(repo)}#{main["number"]}</a></p>')
    body_html = f"""
<div class="wrap prs">
{note}
<div class="pr-grid">
<article class="pr-main" aria-label="PR {main['number']}">{head(main, True)}{comment}{pr_merge_box(main, app_name)}</article>
<div class="pr-aside">{p4}{t1}</div>
</div>
<p class="foot-note">From {src('site/data/pr-capture.json')}, written by {src('scripts/capture_prs.py')} with <code>gh api</code>: PR fields, the sticky comment, commit statuses, branch protection.</p>
</div>"""
    return page("prs.html", "PR flow: what the reviewer sees on GitHub", body_html,
                desc="Countersign's pull-request gate, captured from the demo repo: the sticky comment, the countersign/tier status and the blocked merge.")


def copy_packs():
    dst = SITE / "packs"
    if dst.exists():
        shutil.rmtree(dst)
    for c in CHANGES + ["up-1967"]:
        s = ROOT / "packs" / c / "pack.html"
        if s.exists():
            (dst / c).mkdir(parents=True, exist_ok=True)
            htm = s.read_text(encoding="utf-8").replace('<p class="brand">Countersign', '<p class="brand"><a href="../../index.html">← Countersign</a>', 1)
            (dst / c / "pack.html").write_text(htm, encoding="utf-8")


def main() -> None:
    D = Data()
    n = numbers(D)
    copy_packs()
    (SITE / "style.css").write_text(ICON_CSS + "\n" + CSS.strip() + "\n", encoding="utf-8")
    pages = {"overview.html": build_index(D, n), "attack.html": build_attack(D, n), "tour.html": build_tour(D, n), "pitch.html": build_pitch(D, n)}
    prs = build_prs(D)
    if prs:
        pages["prs.html"] = prs
    for name, htm in pages.items():
        (SITE / name).write_text(htm, encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    import scene  # site/scene.py: the landing page, the code is the scene
    scene.main()
    print("hero:", hero_text(n))
    print("wrote", ", ".join(pages), "+ style.css + packs/")


if __name__ == "__main__":
    main()
