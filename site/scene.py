#!/usr/bin/env python3
"""Build site/index.html (the story, see site/DESIGN.md v3) and site/more.html.

The first screen is one story told in big type: an AI agent wrote this fix; it builds, its tests pass and an AI reviewer
says every requirement is met; it fixes the wrong bug; its owner must decide. Two actions: "Show me where" (one hunk,
one pin, one sentence) and "Try to sneak a bug in" (three planted bugs, one result each).

Everything is resolved here, at build time, from the repo's own records:
  packs/2234/pack.json                   issue title, owner, reviewer verdicts, Claude's finding C1 and its cited line
  evidence/2234/facts.json, scripts/sync_numbers.py   build status, the suite counts
  ledger/ledger.jsonl                    what the owner signed (and how they rated C1)
  evidence/<bug>/facts.json, measurement/results.json, reviews/<bug>/*.json   the planted bugs
A line whose record is missing is dropped, never invented. The short phrases are the only editorial text.

No JavaScript is needed: the views are CSS :target sections and the reveal is a CSS animation.
Code comes from the MessagePack-CSharp checkout (MP_REPO, default /data/src/mp), cached in site/scene-cache.json.
"""

from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
MP = Path(os.environ.get("MP_REPO", "/data/src/mp"))
CACHE = SITE / "scene-cache.json"
BLOB = "https://github.com/Zawaer/countersign/blob/main/"
STORY = "2234"          # the change the first screen tells
FINDING = "claude:C1"   # the finding "Show me where" pins
HUNK = 3                # lines of context either side of the pinned line (<= 12 rows in all)
NEAR = 3                # a finding "points at" a planted bug when it cites a line within this many lines of it
NAMES = {"claude": "Claude", "codex": "Codex", "nemotron": "Nemotron", "gemini": "Gemini"}
# The three "sneak a bug in" cards: (anchor, what you do, planted bug). The result line is derived from its records.
BUGS = [("bug-guard", "Delete a guard", "2234-mut2"),
        ("bug-flip", "Flip a condition", "2234-mut5"),
        ("bug-note", "Hide a note to the AI", "2234-inject")]


def rj(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def e(s) -> str:
    return html.escape(str(s), quote=True)


def short(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def sync_values() -> dict:
    """The headline numbers, from the same function the docs use (scripts/sync_numbers.py)."""
    try:
        spec = importlib.util.spec_from_file_location("sync_numbers", ROOT / "scripts/sync_numbers.py")
        sn = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sn)
        return {k: str(v) for k, v in sn.values().items()}
    except Exception:  # noqa: BLE001  (a missing number drops its line)
        return {}


# ---------------------------------------------------------------- code (git, with a cache)

class Code:
    def __init__(self):
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        self.live = (MP / ".git").exists() or (MP / "HEAD").exists()
        self.used = {}

    def _get(self, key, *args):
        if self.live:
            r = subprocess.run(["git", "-C", str(MP), *args], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                self.used[key] = r.stdout
                return r.stdout
        out = self.cache.get(key)
        if out is not None:
            self.used[key] = out
        return out

    def show(self, rev, path):
        t = self._get(f"show {rev}:{path}", "show", f"{rev}:{path}")
        return None if t is None else t.split("\n")[:-1] if t.endswith("\n") else t.split("\n")

    def diff(self, base, head, path):
        return self._get(f"diff {base} {head} {path}", "diff", "-U0", "--no-color", base, head, "--", path) or ""

    def save(self):
        CACHE.write_text(json.dumps(self.used, indent=0, sort_keys=True) + "\n", encoding="utf-8")


def file_rows(code: Code, base, head, path):
    """Every line of the file at head, with the deleted base lines interleaved: dicts t(ctx|add|del), o, n, s."""
    new = code.show(head, path)
    if new is None:
        return []
    hunks = []
    for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n((?:[-+\\ ].*\n?)*)", code.diff(base, head, path), re.M):
        os_, ol = int(m[1]), int(m[2] if m[2] is not None else 1)
        body = [x for x in m[5].split("\n") if x and not x.startswith("\\")]
        hunks.append((os_ if ol else os_ + 1, [x[1:] for x in body if x[0] == "-"], [x[1:] for x in body if x[0] == "+"]))
    rows, o, n = [], 1, 1
    for os_, dels, adds in hunks:
        while o < os_:
            rows.append(dict(t="ctx", o=o, n=n, s=new[n - 1])); o += 1; n += 1
        for s in dels:
            rows.append(dict(t="del", o=o, n=None, s=s)); o += 1
        for s in adds:
            rows.append(dict(t="add", o=None, n=n, s=s)); n += 1
    while n <= len(new):
        rows.append(dict(t="ctx", o=o, n=n, s=new[n - 1])); o += 1; n += 1
    return rows


KW = ("abstract as async await base bool break byte case catch char class const continue default delegate do double else enum "
      "event false finally for foreach get if in init int interface internal is new not null object out override params partial "
      "private protected public readonly record return sealed set static string struct switch this throw true try typeof using "
      "var void when where while yield and or").split()
TOK = re.compile(r'(?P<c>//.*$|<#.*?#>|<!--.*?-->)|(?P<s>\$?@?"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)\')|(?P<k>\b(?:' + "|".join(KW) +
                 r')\b)|(?P<n>\b\d+\b)')


def hl(s: str) -> str:
    out, i = [], 0
    for m in TOK.finditer(s):
        out.append(e(s[i:m.start()]))
        out.append(f'<i class="t{m.lastgroup}">{e(m.group())}</i>')
        i = m.end()
    out.append(e(s[i:]))
    return "".join(out).replace("​", '<mark class="zw" title="U+200B zero-width space">[hidden character]</mark>')


def dedent(lines: list[str]) -> list[str]:
    lines = [x.replace("\t", "    ") for x in lines]
    ind = min((len(x) - len(x.lstrip()) for x in lines if x.strip()), default=0)
    return [x[ind:] for x in lines]


def reviewer_pin(mid: str, m: dict, why: list):
    """A blind reviewer finding that cites the planted line (reviews/<mid>/*.json): (dict, reviewer name) or (None, None)."""
    for rp in sorted((ROOT / "reviews" / mid).glob("*.json")):
        if "." in rp.stem:
            continue
        r = rj(str(rp.relative_to(ROOT))) or {}
        rv = rp.stem
        for f in r.get("findings", []):
            hits = [x for x in f.get("evidence", []) if x.get("kind") == "code" and x.get("file") == m["file"]
                    and abs(int(x.get("line") or 0) - m["line"]) <= NEAR]
            if not hits:
                continue
            routed = f"verified finding {rv}:{f['id']}" in why
            name = NAMES.get(rv, rv)
            return dict(status="bad" if routed else "weak", label=f"{name} flagged it", say=f.get("title", ""), severity=f.get("severity", ""),
                        src=f"reviews/{mid}/{rp.name} → findings {f['id']}", link=f"{BLOB}reviews/{mid}/{rp.stem}.md"), name
    return None, None


# ---------------------------------------------------------------- the story (change 2234)

def ledger_signoff(change: str) -> dict | None:
    try:
        lines = (ROOT / "ledger/ledger.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    ss = [json.loads(x) for x in lines if x.strip()]
    ss = [x for x in ss if x.get("type") == "signoff" and (x.get("payload") or {}).get("change") == change]
    return ss[-1] if ss else None


def story_data() -> dict:
    """Every line of the first screen, each from its record (None when the record is missing)."""
    p = rj(f"packs/{STORY}/pack.json") or {}
    f = rj(f"evidence/{STORY}/facts.json") or {}
    sv = sync_values()
    checks = {c["id"]: c for c in f.get("checks", [])}
    head = (p.get("story") or {}).get("headline", "")
    title = re.sub(rf"^(?:Agent-written )?change for #{STORY}:\s*", "", head, flags=re.I)
    d = {"title": title, "issue": (p.get("story") or {}).get("issue"), "owner": p.get("owner"), "tier": p.get("tier"),
         "agent": p.get("agent_written")}
    d["builds"] = (checks.get("build") or {}).get("status") == "pass"
    tp, tt = sv.get(f"t{STORY}_suite_passed"), sv.get(f"t{STORY}_suite_total")
    d["tests"] = f"{tp}/{tt}" if tp and tt and tp == tt and (checks.get("tests.full_suite") or {}).get("status") == "pass" else None
    rows = (p.get("panel") or {}).get("rows") or []
    allmet = [r for r in rows if r.get("verdicts") and all(v == "met" for v in r["verdicts"].values())]
    d["allmet"] = NAMES.get(allmet[0]["reviewer"], allmet[0]["reviewer"]) if allmet else None
    d["dissent"] = [NAMES.get(r["reviewer"], r["reviewer"]) for r in rows if r not in allmet]
    rv, fid = FINDING.split(":")
    d["finding"] = next((x for x in p.get("findings", []) if x.get("reviewer") == rv and x.get("id") == fid
                         and x.get("status") == "verified" and x.get("severity") in ("major", "blocker")), None)
    d["finder"] = NAMES.get(rv, rv)
    so = ledger_signoff(STORY)
    pl = (so or {}).get("payload") or {}
    d["signed"] = pl.get("decision", "").replace("-", " ") if so else None
    d["rated"] = next((x.get("verdict") for x in pl.get("findings", []) if x.get("ref") == FINDING), None)
    d["pack"], d["base"], d["head"] = p, p.get("base"), p.get("head")
    return d


def where_hunk(code: Code, d: dict) -> dict | None:
    """The finding's verified code citation, mapped to head, with HUNK lines either side; plus where the fix did edit."""
    f, p = d["finding"], d["pack"]
    if not f:
        return None
    cite = next((x for x in f.get("evidence", []) if x.get("kind") == "code" and x.get("verified") and x.get("rev") in ("base", "head")), None)
    if not cite:
        return None
    rows = file_rows(code, p.get("base"), p.get("head"), cite["file"])
    key = "o" if cite["rev"] == "base" else "n"
    j = next((i for i, r in enumerate(rows) if r[key] == cite["line"]), None)
    if j is None or rows[j]["s"].strip() != (cite.get("quote") or "").strip():
        return None
    win = rows[max(0, j - HUNK):j + HUNK + 2]
    changed = [r["n"] for r in rows if r["t"] == "add"]
    return dict(file=cite["file"], rows=win, pin=rows[j], touched=rows[j]["t"] == "ctx",
                edits=(min(changed), max(changed)) if changed else None, quote=cite.get("quote"))


def bug_data(mid: str) -> dict | None:
    f = rj(f"evidence/{mid}/facts.json") or {}
    m = f.get("mutation") or {}
    if not m.get("file"):
        return None
    R = rj("measurement/results.json") or {}
    fin = next((r for r in R.get("changes", []) if r["change"] == mid), {})
    failed = [c for c in f.get("checks", []) if c.get("status") == "fail"]
    tests = list(dict.fromkeys(m.get("caught_by_full_suite") or m.get("caught_by") or []))
    rpin, rname = reviewer_pin(mid, m, fin.get("why") or [])
    inj = next((c for c in failed if c["id"] == "injection_scan"), None)
    if inj:
        res = ("ok", "✓", "Blocked: instructions to the AI found.",
               f"The injection scan matched {len(inj.get('matches') or [])} patterns before any AI reviewer read it.")
    elif tests:
        res = ("ok", "✓", f"Caught: {len(tests)} test{'s' if len(tests) != 1 else ''} failed.",
               "")
    elif failed:
        res = ("ok", "✓", f"Caught: the {failed[0]['id']} check failed.", failed[0].get("summary", ""))
    elif rpin:
        res = ("ok", "✓", "Caught by a reviewer (tests missed it).", f"{rname}: “{rpin['say']}”")
    else:
        res = ("bad", "✕", "It got past the checks and the reviewers.", "")
    return dict(id=mid, file=m["file"], line=m.get("line"), before=m.get("before", ""), after=m.get("after", ""), res=res,
                tier=fin.get("tier"), routed=fin.get("routed_to_human"))


# ---------------------------------------------------------------- page

def code_rows(rows, pin_row, pin_html) -> str:
    lines = dedent([r["s"] for r in rows])
    out = []
    for r, s in zip(rows, lines):
        mark = {"add": "+", "del": "−"}.get(r["t"], "")
        pinned = r is pin_row
        out.append(f'<div class="r {r["t"]}{" pinned" if pinned else ""}"><span class="n" data-m="{mark}">{r["n"] or r["o"] or ""}</span>'
                   f'<span class="c">{hl(s) if s.strip() else " "}</span></div>' + (pin_html if pinned else ""))
    return "".join(out)


def build() -> tuple[str, str]:
    code = Code()
    d = story_data()
    h = where_hunk(code, d)
    bugs = [(a, label, bug_data(mid)) for a, label, mid in BUGS]
    bugs = [(a, label, b) for a, label, b in bugs if b]
    code.save()
    owner = d["owner"] or "The owner"

    # first screen
    checks = []
    if d["builds"]:
        checks.append("Builds")
    if d["tests"]:
        checks.append(f"{d['tests']} tests pass")
    if d["allmet"]:
        checks.append("AI reviewer: requirements met")
    ticks = "".join(f'<li style="--i:{i}"><span class="g" aria-hidden="true">✓</span>{e(c)}</li>' for i, c in enumerate(checks))
    wrong = ('<p class="wrong reveal r1"><span class="g" aria-hidden="true">✕</span>It fixes the wrong bug.</p>'
             '<p class="caught reveal r1">Countersign caught it with a second AI reviewer.</p>' if d["finding"] else "")
    actions = (f'<p class="decide reveal r2"><span aria-hidden="true">→</span> {e(owner)}, its owner, must decide.</p>'
               '<p class="acts reveal r3"><a class="btn primary" href="#where">Show me where</a>'
               + ('<a class="btn" href="#sneak">Try to sneak a bug in</a>' if bugs else "") + "</p>")
    home = (f'<section class="view home" id="home" aria-labelledby="h-home">'
            f'<h1 id="h-home"><span class="lead">An AI agent wrote this fix.</span>'
            f'<a class="issue" href="{e(d["issue"] or "#")}">#{STORY} {e(d["title"])}</a></h1>'
            f'<ul class="ticks" aria-label="What passed">{ticks}</ul>{wrong}{actions}</section>')

    # show me where
    where = ""
    if h:
        say = "The bug the issue reports isn’t in this code; this fix changes something else."
        edits = (f'<div class="r gap"><span class="n"></span><span class="c">⋯ the fix edits lines {h["edits"][0]}–{h["edits"][1]} instead</span></div>'
                 if h["touched"] and h["edits"] else "")
        pin = (f'<div class="pin" role="note"><span class="g" aria-hidden="true">✕</span>'
               f'{"Untouched by the fix" if h["touched"] else "The fix is here"}</div>')
        by = f'Found by the second AI reviewer, {e(d["finder"])}'
        if d["rated"] == "accepted" and d["signed"]:
            by += f"; {e(owner)} agreed"
        where = (f'<section class="view" id="where" aria-labelledby="h-where"><a class="back" href="#home">← Back</a>'
                 f'<h2 id="h-where" class="sr">Where it goes wrong</h2>'
                 f'<p class="say">{e(say)}</p>'
                 f'<div class="code" aria-label="{e(short(h["file"]))}, the cited lines"><div class="file">{e(short(h["file"]))}</div>'
                 f'{code_rows(h["rows"], h["pin"], pin)}{edits}</div>'
                 f'<p class="by">{by}. <a class="nw" href="packs/{STORY}/pack.html">See all evidence →</a></p></section>')

    # sneak a bug in
    sneak, results = "", ""
    if bugs:
        cards = "".join(f'<li><a class="pick" href="#{a}">{e(label)}</a></li>' for a, label, b in bugs)
        sneak = (f'<section class="view" id="sneak" aria-labelledby="h-sneak"><a class="back" href="#home">← Back</a>'
                 f'<h2 id="h-sneak">Plant a bug in this fix.</h2><ul class="picks">{cards}</ul></section>')
        for a, label, b in bugs:
            cls, g, big, small = b["res"]
            before = f'<div class="r del"><span class="n" data-m="−">{b["line"]}</span><span class="c">{hl(b["before"].strip())}</span></div>' if b["before"].strip() else ""
            after = "" if b["after"].strip().startswith("// (mutant") else f'<div class="r add planted"><span class="n" data-m="+">{b["line"]}</span><span class="c">{hl(b["after"].strip())}</span></div>'
            results += (f'<section class="view" id="{a}" aria-labelledby="h-{a}"><a class="back" href="#sneak">← Try another</a>'
                        f'<p class="you">You chose: {e(label[:1].lower() + label[1:])}.</p>'
                        f'<h2 id="h-{a}" class="result {cls}"><span class="g" aria-hidden="true">{g}</span>{e(big)}</h2>'
                        f'<div class="code"><div class="file">{e(short(b["file"]))}</div>{before}{after}</div>'
                        + (f'<p class="by">{e(small)}</p>' if small else "")
                        + f'<p class="by"><a href="overview.html">All planted bugs →</a></p></section>')

    index = page("Countersign: an AI agent wrote this fix", where + sneak + results + home)
    more = page("Countersign: more", MORE, cls="plain")
    return index, more


MORE = """<section class="view plain-list" aria-labelledby="h-more"><a class="back" href="index.html">← Back</a>
<h1 id="h-more">More</h1><ul class="links">
<li><a href="packs/2234/pack.html">Evidence pack</a><span>what the owner signs</span></li>
<li><a href="tour.html">How it works</a><span>six steps</span></li>
<li><a href="overview.html">Numbers</a><span>three results</span></li>
<li><a href="prs.html">PR flow</a><span>on GitHub</span></li>
<li><a href="pitch.html">Pitch</a><span>the deck</span></li>
</ul></section>"""


TAGLINE = "AI reviews code; a named human signs."

PAGE_CSS = r"""
:root{--bg:#fff;--bg2:#f6f8fa;--fg:#1f2328;--muted:#59636e;--border:#d1d9e0;--accent:#0969da;
--ok:#1a7f37;--ok-bg:#dafbe1;--warn:#9a6700;--warn-bg:#fff8c5;--bad:#d1242f;--bad-bg:#ffebe9;
--add:#e6ffec;--del:#ffebe9;--k:#8250df;--s:#0a3069;--cm:#6e7781;--num:#0550ae;
--sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;color-scheme:light}
:root[data-theme=dark]{--bg:#0d1117;--bg2:#151b23;--fg:#e6edf3;--muted:#9198a1;--border:#3d444d;--accent:#4493f8;
--ok:#3fb950;--ok-bg:#12261e;--warn:#d29922;--warn-bg:#272115;--bad:#f85149;--bad-bg:#25171c;
--add:#12261e;--del:#25171c;--k:#d2a8ff;--s:#a5d6ff;--cm:#8b949e;--num:#79c0ff;color-scheme:dark}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 var(--sans);min-height:100vh;min-height:100svh;display:flex;flex-direction:column}
a{color:var(--accent);text-underline-offset:3px}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px;border-radius:6px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;font-size:15px}
.mark{font-weight:600;color:var(--fg);text-decoration:none}
.brand{margin:0;display:flex;align-items:baseline;gap:0 10px;flex-wrap:wrap;min-width:0}.tag{color:var(--muted);font-size:14px}
.top nav{display:flex;gap:16px;align-items:center}.top nav a{color:var(--muted)}
.top button{background:none;border:0;color:var(--muted);font:inherit;font-size:17px;padding:2px 6px;cursor:pointer}
main{flex:1;display:flex;flex-direction:column}
.view{display:none;flex:1;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:16px 20px 48px;gap:20px}
.view:target{display:flex}.view:target~.home{display:none}.home{display:flex}
.back{align-self:center;font-size:16px}
h1,h2{margin:0;font-weight:700;letter-spacing:-.01em}
.home h1{display:flex;flex-direction:column;gap:8px;align-items:center}
.home .lead{font-size:clamp(30px,6.4vw,56px);line-height:1.1}
.issue{font:400 clamp(14px,2.2vw,17px)/1.4 var(--sans);color:var(--muted);text-decoration:none;max-width:90vw}
h1,h2,.say,.wrong,.decide{text-wrap:balance}
.caught{margin:-8px 0 0;font-size:clamp(16px,2.6vw,20px);color:var(--fg)}
.issue:hover{text-decoration:underline}
.ticks{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 28px;font-size:clamp(19px,3.4vw,28px);font-weight:600}
.ticks li{display:flex;align-items:center;gap:10px;color:var(--fg);opacity:0;animation:in .4s ease-out forwards;animation-delay:calc(.35s + var(--i) * .35s)}
.g{display:inline-grid;place-items:center;width:1.25em;height:1.25em;border-radius:50%;border:2px solid currentColor;font-size:.85em;font-weight:800;flex:none}
.ticks .g{color:var(--ok);background:var(--ok-bg)}
.wrong{margin:12px 0 0;font-size:clamp(32px,7vw,64px);line-height:1.15;font-weight:800;color:var(--bad)}.wrong .g,.result .g{display:inline-grid;vertical-align:.1em;margin-right:.3em}
.wrong .g{background:var(--bad-bg)}
.decide{margin:0;font-size:clamp(22px,4vw,34px);font-weight:600}
.acts{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin:4px 0 0}
.btn{display:inline-block;padding:14px 26px;border-radius:10px;border:2px solid var(--fg);color:var(--fg);text-decoration:none;font-size:18px;font-weight:600;background:var(--bg)}
.btn.primary{background:var(--fg);color:var(--bg)}
.btn:hover{border-color:var(--accent)}
.reveal{opacity:0;animation:in .5s ease-out forwards}
.r1{animation-delay:2s}.r2{animation-delay:3s}.r3{animation-delay:3.4s}
@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.seen .ticks li,.seen .reveal{animation-duration:0s;animation-delay:0s}
@media (prefers-reduced-motion:reduce){.ticks li,.reveal{animation:none;opacity:1}}
.say{font-size:clamp(22px,4vw,32px);font-weight:600;line-height:1.25;max-width:26ch;margin:0}
.code{width:100%;max-width:760px;text-align:left;border:1px solid var(--border);border-radius:10px;padding:8px 0;font:14px/22px var(--mono);background:var(--bg)}
.file{font:600 13px/1.4 var(--mono);color:var(--muted);padding:2px 14px 6px}
.r{display:grid;grid-template-columns:56px 1fr;min-height:22px}
.r .n{color:var(--muted);text-align:right;padding-right:14px;user-select:none;position:relative}
.r .n::after{content:attr(data-m);position:absolute;right:3px}
.r .c{white-space:pre-wrap;overflow-wrap:anywhere;padding-right:14px}
.r.add{background:var(--add)}.r.del{background:var(--del)}.r.del .c{color:var(--muted)}
.r.pinned{background:var(--bad-bg);box-shadow:inset 4px 0 var(--bad);font-weight:600}
.r.planted{box-shadow:inset 4px 0 var(--fg)}
.r.gap .c{color:var(--fg);font-family:var(--sans);font-size:15px;font-weight:600}
.pin{display:flex;align-items:center;gap:8px;margin:4px 14px 8px 56px;color:var(--bad);font:700 16px/1.3 var(--sans)}
.pin .g{background:var(--bad-bg)}
i.tk{font-style:normal;color:var(--k)}i.ts{font-style:normal;color:var(--s)}i.tc{color:var(--cm)}i.tn{font-style:normal;color:var(--num)}
mark.zw{background:var(--warn-bg);color:var(--warn);border-radius:3px;padding:0 2px;white-space:nowrap}
.nw{white-space:nowrap}.by{margin:0;color:var(--muted);font-size:15px;max-width:60ch}
.picks{list-style:none;margin:0;padding:0;display:grid;gap:14px;width:100%;max-width:440px}
.pick{display:block;padding:22px;border:2px solid var(--border);border-radius:12px;font-size:22px;font-weight:600;color:var(--fg);text-decoration:none}
.pick:hover{border-color:var(--accent)}
#h-sneak{font-size:clamp(26px,5vw,40px)}
.you{margin:0;color:var(--muted);font-size:17px}
.result{font-size:clamp(26px,5.4vw,46px);line-height:1.2;max-width:22ch}
.result.ok{color:var(--ok)}.result.ok .g{background:var(--ok-bg)}
.result.warn{color:var(--warn)}.result.warn .g{background:var(--warn-bg)}
.result.bad{color:var(--bad)}.result.bad .g{background:var(--bad-bg)}
.plain-list{display:flex;justify-content:flex-start;align-items:flex-start;text-align:left;max-width:560px;margin:0 auto;width:100%}
.plain-list h1{font-size:32px}
.links{list-style:none;margin:0;padding:0;display:grid;gap:4px;width:100%}
.links li{display:flex;justify-content:space-between;gap:12px;padding:14px 0;border-bottom:1px solid var(--border);font-size:20px}
.links span{color:var(--muted);font-size:16px}
@media (max-width:600px){.r{grid-template-columns:48px 1fr}.r .n{padding-right:12px;font-size:12px}.code{font-size:12.5px;line-height:20px}
.pin{margin-left:48px}.btn{padding:12px 18px;font-size:17px}.view{gap:16px;padding:8px 16px 32px}.ticks{gap:10px 20px}
.acts{flex-direction:column;align-items:stretch;width:100%;max-width:340px}}
"""

SEEN_JS = ("addEventListener('hashchange',function(){document.body.classList.add('seen')});"
           "function csTheme(){var d=document.documentElement,c=d.dataset.theme||'light',n=c==='dark'?'light':'dark';"
           "d.dataset.theme=n;try{localStorage.setItem('cs-theme',n)}catch(_){}}")


def page(title: str, body: str, cls: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="Countersign: an AI agent wrote a fix that builds, passes its tests and an AI review, and fixes the wrong bug. Countersign shows where, and its owner decides.">
<script>try{{var t=localStorage.getItem("cs-theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
<style>{PAGE_CSS.strip()}</style>
</head><body class="{cls}">
<header class="top"><p class="brand"><a class="mark" href="index.html">Countersign</a><span class="tag">{TAGLINE}</span></p>
<nav aria-label="Site"><a href="more.html">More</a><button type="button" aria-label="Switch light or dark theme" onclick="csTheme()">◐</button></nav></header>
<main id="main">{body}</main>
<script>{SEEN_JS}</script>
</body></html>
"""


def main():
    index, more = build()
    (SITE / "index.html").write_text(index, encoding="utf-8")
    (SITE / "more.html").write_text(more, encoding="utf-8")
    print("wrote site/index.html, site/more.html")


if __name__ == "__main__":
    main()
