#!/usr/bin/env python3
"""Build site/index.html: the code is the scene (see site/DESIGN.md, v2).

The page is the real diff of an agent-written change with a few pins on the exact lines they are about.
Everything shown is resolved here, at build time, from the repo's own records:
  packs/<change>/pack.json        findings, clauses, refusals, rules, verdict, owner
  evidence/<change>/facts.json    checks (fail_without_fix, repro.*, docs.anchors, ...)
  evidence/<change>-mutK/facts.json, measurement/results.json   the seeded bugs
The only editorial text is the short pin label (2-5 words) in SCENES; each one names the record it summarises,
and the card behind it shows that record verbatim. A pin whose record is missing is dropped, never invented.

Code comes from the MessagePack-CSharp checkout (MP_REPO, default /data/src/mp). The extracted lines are cached in
site/scene-cache.json so the page still builds where that checkout is absent.
"""

from __future__ import annotations

import html
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
CTX = 2  # lines of context around a pinned line

TC = "src/MessagePack.SourceGenerator/CodeAnalysis/TypeCollector.cs"

# Each scene: which files to show, the issue title (cites the issue URL in pack.story.issue), a 3-6 word verdict phrase,
# and the pins. Pin kinds: finding (pack.findings), clause (pack.requirements / refused.clauses), test_base_pass /
# test_base_fail (facts tests.fail_without_fix), check (facts.checks), rule (pack.rules_fired), refusal
# (pack.refused.reviewer_refusals). `at` = (file, "head"|"base", line) overrides the line taken from the record.
SCENES = {
    "2234": dict(
        title="The analyzer does not work if SuppressSourceGeneration = true",
        verdict="",
        files=[TC, "tests/MessagePack.SourceGenerator.Tests/SuppressSourceGenerationAnalyzerTests.cs"],
        pins=[
            dict(kind="finding", ref="claude:C1", label="Fixes a different crash"),
            dict(kind="finding", ref="claude:C2", label="Still crashes on Key(null)"),
            dict(kind="test_base_pass", ref="SuppressSourceGenerationAnalyzerTests.MemberWithoutKeyIsReported", label="Passes without the fix"),
            dict(kind="test_base_fail", ref="SuppressSourceGenerationAnalyzerTests.DuplicateIntKeysAreReportedWithoutAnalyzerFailure", label="Fails without the fix"),
        ]),
    "2283": dict(
        title="Generator and analyzer crash with IndexOutOfRangeException on a closed generic struct from a referenced assembly",
        verdict="pin:2",
        files=[TC, "tests/MessagePack.SourceGenerator.Tests/GenericsFormatterTests.cs"],
        pins=[
            dict(kind="clause", ref="REQ-2283-F2", label="Proven: no analyzer crash"),
            dict(kind="finding", ref="claude:C2", label="Hides a null-key warning"),
            dict(kind="finding", ref="claude:C1", label="Drops a real warning"),
            dict(kind="test_base_fail", ref="GenericsFormatterTests.ClosedGenericStruct_FromMetadataReference", label="Fails without the fix"),
        ]),
    "2129": dict(
        title="Allow generation of Formatter for a type in a referenced assembly",
        verdict="public API, failing checks",
        files=["src/MessagePack.Annotations/Attributes.cs", "src/MessagePack.SourceGenerator/MessagePackGenerator.cs",
               "tests/MessagePack.SourceGenerator.ExternalTypes/MessagePack.SourceGenerator.ExternalTypes.csproj",
               "tests/MessagePack.SourceGenerator.Tests/GeneratedMessagePackFormatterTests.cs"],
        pins=[
            dict(kind="finding", ref="claude:C1", label="New public API, untracked"),
            dict(kind="clause", ref="REQ-2129-F1", label="Proven: the feature works"),
            dict(kind="finding", ref="claude:C3", label="New StyleCop warning"),
        ]),
    "2297": dict(
        title="Add ExcludeFromCodeCoverage attribute to generated code.",
        verdict="{files} files: split it",
        files=["src/MessagePack.SourceGenerator/Transforms/ResolverTemplate.tt", "src/MessagePack.SourceGenerator/Transforms/FormatterTemplate.tt",
               "src/MessagePack.SourceGenerator/Transforms/TransformUtilities.cs"],
        pins=[
            dict(kind="finding", ref="claude:C1", label="Older targets lose it"),
            dict(kind="clause", ref="REQ-2297-F1", label="Reviewers disagree"),
            dict(kind="finding", ref="nemotron:N1", label="Unrelated formatting change"),
            dict(kind="finding", ref="claude:C2", label="Generated test resources"),
        ]),
    "up-1967": dict(
        title="Fix AOT README anchor",
        verdict="docs fix, link resolves",
        files=["README.md"],
        pins=[
            dict(kind="check", ref="docs.anchors", label="Link now resolves"),
            dict(kind="finding", ref="claude:C1", label="Next link still broken"),
        ]),
}
ORDER = ["2234", "2283", "2129", "2297", "up-1967"]
NAMES = {"claude": "Claude", "codex": "Codex", "nemotron": "Nemotron", "gemini": "Gemini"}
GLYPH = {"bad": "✗", "weak": "◐", "ok": "✓", "ask": "?"}
TIER_CLS = {"silent": "ok", "notify": "ok", "ask": "warn", "block": "bad"}


def rj(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def e(s) -> str:
    return html.escape(str(s), quote=True)


def short(path: str) -> str:
    return path.rsplit("/", 1)[-1]


# ---------------------------------------------------------------- code (git, with a cache)

class Code:
    def __init__(self):
        self.cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
        self.live = (MP / ".git").exists() or (MP / "HEAD").exists()
        self.used = {}

    def _git(self, *args):
        r = subprocess.run(["git", "-C", str(MP), *args], capture_output=True, text=True, timeout=30)
        return r.stdout if r.returncode == 0 else None

    def _get(self, key, *args):
        if self.live:
            out = self._git(*args)
            if out is not None:
                self.used[key] = out
                return out
        out = self.cache.get(key)
        if out is not None:
            self.used[key] = out
        return out

    def show(self, rev, path):
        t = self._get(f"show {rev}:{path}", "show", f"{rev}:{path}")
        return None if t is None else t.split("\n")[:-1] if t.endswith("\n") else t.split("\n")

    def diff(self, base, head, path):
        return self._get(f"diff {base} {head} {path}", "diff", "-U0", "--no-color", base, head, "--", path) or ""

    def names(self, base, head):
        t = self._get(f"names {base} {head}", "diff", "--name-only", base, head) or ""
        return [x for x in t.splitlines() if x]

    def save(self):
        CACHE.write_text(json.dumps(self.used, indent=0, sort_keys=True) + "\n", encoding="utf-8")


def file_rows(code: Code, base, head, path):
    """Every line of the file at head, with the deleted base lines interleaved: dicts t(ctx|add|del), o, n, s."""
    new = code.show(head, path)
    if new is None:
        return []
    hunks = []
    for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n((?:[-+\\ ].*\n?)*)", code.diff(base, head, path), re.M):
        os_, ol, ns, nl = int(m[1]), int(m[2] if m[2] is not None else 1), int(m[3]), int(m[4] if m[4] is not None else 1)
        body = [x for x in m[5].split("\n") if x and not x.startswith("\\")]
        hunks.append((os_ if ol else os_ + 1, ol, nl, [x[1:] for x in body if x[0] == "-"], [x[1:] for x in body if x[0] == "+"]))
    rows, o, n = [], 1, 1
    for os_, ol, nl, dels, adds in hunks:
        while o < os_:
            rows.append(dict(t="ctx", o=o, n=n, s=new[n - 1])); o += 1; n += 1
        for s in dels:
            rows.append(dict(t="del", o=o, n=None, s=s)); o += 1
        for s in adds:
            rows.append(dict(t="add", o=None, n=n, s=s)); n += 1
    while n <= len(new):
        rows.append(dict(t="ctx", o=o, n=n, s=new[n - 1])); o += 1; n += 1
    return rows


# ---------------------------------------------------------------- syntax colour (subtle)

KW = ("abstract as async await base bool break byte case catch char class const continue default delegate do double else enum "
      "event false finally for foreach get if in init int interface internal is new not null object out override params partial "
      "private protected public readonly record return sealed set static string struct switch this throw true try typeof using "
      "var void when where while yield and or").split()
TOK = re.compile(r'(?P<c>//.*$|<#.*?#>|<!--.*?-->)|(?P<s>\$?@?"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)\')|(?P<k>\b(?:' + "|".join(KW) +
                 r')\b)|(?P<n>\b\d+\b)|(?P<a>\(#[^)]*\))')


def hl(s: str) -> str:
    out, i = [], 0
    for m in TOK.finditer(s):
        out.append(e(s[i:m.start()]))
        out.append(f'<i class="t{m.lastgroup}">{e(m.group())}</i>')
        i = m.end()
    out.append(e(s[i:]))
    return "".join(out)


# ---------------------------------------------------------------- pins

class Ctx:
    def __init__(self, cid):
        self.cid = cid
        self.pack = rj(f"packs/{cid}/pack.json") or {}
        self.facts = rj(f"evidence/{cid}/facts.json") or {}
        self.checks = {c["id"]: c for c in self.facts.get("checks", [])}
        self.panel = (self.pack.get("reviewer_panel") or {}).get("reviewers") or []

    def pack_link(self, anchor=""):
        return f"packs/{self.cid}/pack.html" + (f"#{anchor}" if anchor else "")


def chip(cls, text):
    return f'<span class="chip {cls}">{e(text)}</span>'


def ev_code(path, line, rev, quote):
    return (f'<div class="evl"><span class="loc">{e(short(path))}:{e(line)} @{e(str(rev)[:8])}</span>'
            f'<code>{hl(quote.strip())}</code></div>')


def ev_test(name, outcome, where):
    st = "ok" if outcome == "passed" else "bad"
    return (f'<div class="evl"><span class="loc">{e(where)}</span><code><b class="{st}">{GLYPH[st if st == "ok" else "bad"]} {e(outcome)}</b> '
            f'{e(name.split(".")[-1])}</code></div>')


def resolve(cx: Ctx, spec: dict, fmt: dict):
    """-> dict(status, label, at, say, who, ev, src, link) or None if the record is missing."""
    p, k, ref = cx.pack, spec["kind"], spec["ref"]
    label = spec["label"].format(**fmt)
    if k == "finding":
        rv, fid = ref.split(":")
        f = next((x for x in p.get("findings", []) if x.get("reviewer") == rv and x["id"] == fid and x.get("status") == "verified"), None)
        if not f:
            return None
        found = next((x for x in (p.get("card") or {}).get("found", []) if x["key"] == ref), {})
        agree = {rv, *(f.get("confirmed_by") or []), *(found.get("shared_with") or [])}
        who = [chip("bad", f"{NAMES.get(r, r)} found it") for r in sorted(agree)]
        who += [chip("", f"{NAMES.get(r, r)} did not flag it") for r in cx.panel if r not in agree]
        rp = cx.checks.get(f"repro.{rv}.{fid}")
        if rp and rp.get("status") == "pass":
            who.append(chip("bad", "pipeline reproduced it"))
        at, ev = spec.get("at"), []
        for x in f.get("evidence", []):
            if x.get("kind") == "code" and x.get("verified") and x.get("rev") in ("head", "base"):
                at = at or (x["file"], x["rev"], x["line"])
                if len(ev) < 1:
                    ev.append(ev_code(x["file"], x["line"], x["rev"], x.get("quote", "")))
        for x in f.get("evidence", []):
            if x.get("kind") == "test" and len(ev) < 2:
                where = "without the fix" if x.get("check") == "tests.fail_without_fix" else "test"
                ev.append(ev_test(x["name"], x.get("outcome") or "", where))
        if rp and rp.get("status") == "pass":
            ev.append(f'<div class="evl"><span class="loc">{e(rp["id"])}</span><code>{e(rp.get("summary", ""))}</code></div>')
        status = "bad" if f.get("severity") == "major" or (rp and rp.get("status") == "pass") else "weak"
        if rp and rp.get("status") == "pass":
            label += " · reproduced"
        return dict(status=status, label=label, at=at, say=f["title"], who=who, ev=ev,
                    src=f"packs/{cx.cid}/pack.json → findings {ref}", link=cx.pack_link(found.get("anchor") or f"f-{rv}-{fid}"))
    if k == "clause":
        r = next((x for x in p.get("requirements", []) + (p.get("refused") or {}).get("clauses", []) if x["id"] == ref), None)
        if not r:
            return None
        who = []
        for rv, v in (r.get("verdicts") or {}).items():
            good = v.get("verdict") == "met"
            who.append(chip("ok" if good else "bad", f"{NAMES.get(rv, rv)} {'met' if good else v.get('verdict', '').replace('_', ' ')}"))
        at, ev = spec.get("at"), []
        for v in (r.get("verdicts") or {}).values():
            for x in v.get("evidence", []):
                if x.get("kind") == "code" and x.get("verified") and not ev:
                    at = at or (x["file"], x.get("rev", "head"), x["line"])
                    ev.append(ev_code(x["file"], x["line"], x.get("rev", "head"), x.get("quote", "")))
        for c in r.get("checks", []):
            if len(ev) < 3:
                ev.append(f'<div class="evl"><span class="loc">check</span><code><b class="{"ok" if c["status"] == "pass" else "bad"}">'
                          f'{"✓" if c["status"] == "pass" else "✗"} {e(c["status"])}</b> {e(c["id"])}</code></div>')
        status = {"proven": "ok", "refused": "ask", "held_before": "weak"}.get(r.get("status"), "weak")
        return dict(status=status, label=label, at=at, say=r["text"], who=who, ev=ev,
                    src=f"packs/{cx.cid}/pack.json → requirements {ref} ({r.get('status')})", link=cx.pack_link(f"chain-{ref}"))
    if k in ("test_base_pass", "test_base_fail"):
        c = cx.checks.get("tests.fail_without_fix") or {}
        t = next((x for x in c.get("tests", []) if x["name"] == ref), None)
        want = "passed" if k == "test_base_pass" else "failed"
        if not t or t.get("outcome") != want:
            return None
        head = next((x for x in (cx.checks.get("tests.targeted") or {}).get("tests", []) if x["name"] == ref), {})
        say = ("This new test also passes on the code before the change, so it cannot show the fix works."
               if want == "passed" else "This new test fails on the code before the change and passes after it, so it does test the fix.")
        ev = [ev_test(ref, want, "on base (fix removed)")]
        if head:
            ev.append(ev_test(ref, head.get("outcome", ""), "with the fix"))
        return dict(status="weak" if want == "passed" else "ok", label=label, at=("test", ref), say=say,
                    who=[chip("", "deterministic check, no AI")], ev=ev,
                    src=f"evidence/{cx.cid}/facts.json → checks tests.fail_without_fix", link=cx.pack_link("checks"))
    if k == "check":
        c = cx.checks.get(ref)
        if not c:
            return None
        ok = c["status"] == "pass"
        say = c.get("summary", "")
        at = spec.get("at")
        if ref == "docs.anchors":
            links = c.get("links_on_touched_lines") or []
            if links:
                at = (links[0]["file"], "head", links[0]["line"])
        return dict(status="ok" if ok else "bad", label=label, at=at, say=say[:1].upper() + say[1:],
                    who=[chip("", "deterministic check, no AI")],
                    ev=[f'<div class="evl"><span class="loc">check</span><code><b class="{"ok" if ok else "bad"}">{"✓" if ok else "✗"} {e(c["status"])}</b> {e(ref)}</code></div>'],
                    src=f"evidence/{cx.cid}/facts.json → checks {ref}", link=cx.pack_link("checks"))
    if k == "rule":
        r = next((x for x in p.get("rules_fired", []) if x.get("id") == ref), None)
        if not r:
            return None
        return dict(status="bad", label=label, at=spec.get("at"), say=r.get("message", ""), who=[chip("", "mandate rule, no AI")],
                    ev=[f'<div class="evl"><span class="loc">{e(ref)}</span><code>{e(r.get("evidence", ""))} → {e(str(r.get("tier", "")).upper())}</code></div>'],
                    src=f"mandate/messagepack.mandate.yaml → rules {ref}", link=cx.pack_link("card"))
    if k == "refusal":
        rv, i = ref.split(":")
        rs = [x for x in (p.get("refused") or {}).get("reviewer_refusals", []) if x.get("reviewer") == rv]
        if len(rs) <= int(i):
            return None
        r = rs[int(i)]
        return dict(status="ask", label=label, at=spec.get("at"), say=f"{NAMES.get(rv, rv)} would not decide this: {r['topic']}.",
                    who=[chip("warn", f"{NAMES.get(rv, rv)} refused")],
                    ev=[f'<div class="evl"><span class="loc">why</span><code>{e(r.get("reason", ""))}</code></div>'],
                    src=f"packs/{cx.cid}/pack.json → refused.reviewer_refusals", link=cx.pack_link("refusal-1"))
    return None


def mutant_pin(mid: str, res: dict):
    f = rj(f"evidence/{mid}/facts.json") or {}
    m = f.get("mutation") or {}
    if not m.get("file"):
        return None, None
    failing = list(dict.fromkeys(m.get("caught_by_full_suite") or m.get("caught_by") or []))
    failed_checks = [c["id"] for c in f.get("checks", []) if c.get("status") == "fail"]
    caught = bool(failed_checks)
    n = len(failing)
    label = (f"Caught: {n} test{'s fail' if n != 1 else ' fails'}" if caught and n else "Caught by a check" if caught else "Got past every check")
    ev = [f'<div class="evl"><span class="loc">seeded bug</span><code>{hl(m.get("before", "").strip())}<br>→ {hl(m.get("after", "").strip())}</code></div>']
    for t in failing[:3]:
        ev.append(ev_test(t, "failed", "with the bug"))
    if len(failing) > 3:
        ev.append(f'<div class="evl"><span class="loc"></span><code>+{len(failing) - 3} more failing tests</code></div>')
    ev.append(f'<div class="evl"><span class="loc">checks</span><code>{e(", ".join(failed_checks) or "none failed")}</code></div>')
    tier = res.get("tier")
    who = [chip("", "deterministic checks, no AI")]
    say = (m.get("description") or "").rstrip(".") + "."
    pin = dict(status="bad" if caught else "weak", label=label, at=(m["file"], "head", m["line"]), say=say[:1].upper() + say[1:], who=who, ev=ev,
               src=f"evidence/{mid}/facts.json → mutation; measurement/results.json → mutants {mid}",
               link=f"overview.html#{mid}")
    return pin, m


NEAR = 3  # a finding "points at" the seeded bug when one of its code citations is within this many lines of it


def reviewer_pin(mid: str, m: dict, why: list):
    """A blind reviewer finding that cites the planted line (reviews/<mid>/*.json), or None."""
    for rp in sorted((ROOT / "reviews" / mid).glob("*.json")):
        r = rj(str(rp.relative_to(ROOT))) or {}
        rv = rp.stem
        for f in r.get("findings", []):
            hits = [x for x in f.get("evidence", []) if x.get("kind") == "code" and x.get("file") == m["file"] and abs(int(x.get("line") or 0) - m["line"]) <= NEAR]
            if not hits:
                continue
            routed = f"verified finding {rv}:{f['id']}" in why
            name = NAMES.get(rv, rv)
            sev = f.get("severity", "")
            ev = [ev_code(x["file"], x["line"], x.get("rev", "head"), x.get("quote", "")) for x in sorted(hits, key=lambda x: abs(int(x["line"]) - m["line"]))[:1]]
            who = [chip("bad" if routed else "warn", f"{name} flagged it, {sev}"),
                   chip("", "verified, in the routing reasons" if routed else "not in the routing reasons")]
            return dict(status="bad" if routed else "weak", label=f"{name} flagged it", say=f.get("title", ""), who=who, ev=ev,
                        src=f"reviews/{mid}/{rp.name} → findings {f['id']}", link=f"{BLOB}reviews/{mid}/{rp.stem}.md"), f"{name}"
    return None, None


# ---------------------------------------------------------------- scene rendering

def render_scene(code: Code, cid: str, pins_in: list, verdict: dict, title: str, files: list, mutation=None, sid=None):
    sid = sid or cid
    cx = Ctx(cid)
    p = cx.pack
    base, head = p.get("base"), p.get("head")
    all_files = code.names(base, head)
    shown = [f for f in files if f in all_files]
    rows = {f: file_rows(code, base, head, f) for f in shown}
    if mutation:  # the seeded bug: the head line becomes a deletion, the mutated line an addition
        rr = rows.get(mutation["file"]) or []
        i = next((j for j, r in enumerate(rr) if r["n"] == mutation["line"]), None)
        if i is None or rr[i]["s"].strip() != mutation["before"].strip():
            i = next((j for j, r in enumerate(rr) if r["n"] and r["s"].strip() == mutation["before"].strip()), None)
        if i is not None:
            r = rr[i]
            ind = r["s"][:len(r["s"]) - len(r["s"].lstrip())]
            rr[i:i + 1] = [dict(t="mdel", o=None, n=r["n"], s=r["s"]), dict(t="madd", o=None, n=r["n"], s=ind + mutation["after"].strip())]
            for pin in pins_in:
                pin["at"] = (mutation["file"], "row", i + 1)
    # place pins on rows
    placed = {}  # (file, row index) -> [pin]
    more_pins = []
    for pin in pins_in:
        at = pin.get("at")
        if not at:
            continue
        if at[0] == "+more":
            more_pins.append(pin); continue
        if at[0] == "test":
            name = at[1].split(".")[-1]
            hit = next(((f, j) for f in shown for j, r in enumerate(rows[f]) if r["n"] and re.search(r"\b" + re.escape(name) + r"\s*\(", r["s"])), None)
        else:
            f, rev, ln = at
            rr = rows.get(f) or []
            if rev == "row":
                hit = (f, ln)
            else:
                key = "n" if rev == "head" else "o"
                hit = next(((f, j) for j, r in enumerate(rr) if r[key] == ln and (rev == "head" or r["t"] == "ctx" or r["t"] == "del")), None)
        if hit:
            placed.setdefault(hit, []).append(pin)
    # visible rows
    out = []
    for f in shown:
        rr = rows[f]
        if not rr:
            continue
        vis = set()
        for (pf, j) in placed:
            if pf == f:
                vis.update(range(max(0, j - CTX), min(len(rr), j + CTX + 1)))
        changed = [j for j, r in enumerate(rr) if r["t"] != "ctx"]
        if not vis and not changed:
            continue
        lines = [r["s"] for j, r in enumerate(rr) if j in vis or any(abs(j - c) <= 1 for c in changed[:400]) and r["s"].strip()]
        ind = min((len(s.replace("\t", "    ")) - len(s.replace("\t", "    ").lstrip()) for s in lines if s.strip()), default=0)
        out.append(f'<div class="file">{f"<span>{e(f.rsplit(chr(47), 1)[0])}/</span>" if "/" in f else ""}{e(short(f))}</div>')
        for j in sorted(vis):
            if not rr[j]["s"].strip() and (j - 1 not in vis or j + 1 not in vis) and (f, j) not in placed:
                vis.discard(j)
        j, first = 0, True
        while j < len(rr):
            if j in vis:
                if j == 0 or j - 1 not in vis:  # new window: dedent it on its own
                    k2 = j
                    while k2 < len(rr) and k2 in vis:
                        k2 += 1
                    ws = [r["s"].replace("\t", "    ") for r in rr[j:k2] if r["s"].strip()]
                    wind = min((len(x) - len(x.lstrip()) for x in ws), default=0)
                out.append(row_html(rr[j], wind, placed.get((f, j), []), sid, f"{sid}-{f}-{j}"))
                j += 1; first = False; continue
            k = j
            while k < len(rr) and k not in vis:
                k += 1
            seg = rr[j:k]
            ch = [i for i, r in enumerate(seg) if r["t"] != "ctx"]
            tail = k >= len(rr)
            if ch and mutation:
                pass
            elif ch:
                keep = {i for c in ch for i in range(max(0, c - 1), min(len(seg), c + 2))}
                inner, last = [], -1
                for i in sorted(keep):
                    if last >= 0 and i > last + 1:
                        inner.append('<div class="r gap"><span class="n"></span><span class="c">⋯</span></div>')
                    inner.append(row_html(seg[i], ind, [], sid, ""))
                    last = i
                adds = sum(r["t"] == "add" for r in seg); dels = sum(r["t"] == "del" for r in seg)
                if not vis and len(seg) == len(rr) and adds + dels <= 12:
                    out.extend(inner)  # small unpinned file: show it whole
                else:
                    lab = " ".join(x for x in (f"+{adds}" if adds else "", f"−{dels}" if dels else "") if x)
                    out.append(f'<details class="fold"><summary><span class="n"></span><span class="c">⋯ {lab} lines</span></summary>{"".join(inner)}</details>')
            elif not first and not tail and not mutation:
                if len(seg) <= 3:
                    out.extend(row_html(r, ind, [], sid, "") for r in seg)
                else:
                    out.append(f'<div class="r gap"><span class="n"></span><span class="c">⋯ {len(seg)} lines</span></div>')
            j = k
    rest = [] if mutation else [f for f in all_files if f not in shown]
    if rest:
        names = ", ".join(short(x) for x in rest) if len(rest) <= 3 else ""
        pins_html, cards = pins_for(more_pins, sid, f"{sid}-more")
        out.append(f'<div class="r more"><span class="n"></span><span class="c">+{len(rest)} more file{"s" if len(rest) != 1 else ""}'
                   f'{": " + e(names) if names else ""}{pins_html}</span></div>{cards}')
    vcls = TIER_CLS.get(verdict["tier"], "")
    owner = f" → {e(verdict['owner'])}" if verdict.get("owner") and verdict["tier"] in ("ask", "block") else ""
    phrase_html = f'<span>&nbsp;· {e(verdict["phrase"])}</span>' if verdict["phrase"] else ""
    head_html = (f'<div class="title"><a href="{e(verdict.get("issue") or "#")}">#{e(verdict.get("num"))}</a> {"<span class=ag>agent-written</span> " if verdict.get("agent") else ""}{e(title)}</div>'
                 f'<button class="verdict {vcls}" type="button" aria-expanded="false" aria-controls="v-{sid}" data-card="v-{sid}">'
                 f'<b>{e(verdict["tier"].upper())}{owner}</b>{phrase_html}</button>'
                 f'<div class="card vcard" id="v-{sid}" hidden>{verdict["card"]}</div>')
    return (f'<section class="scene" data-id="{e(sid)}" hidden aria-label="Change {e(sid)}">'
            f'<div class="head">{head_html}</div><div class="code">{"".join(out)}</div></section>')


_N = [0]


def pins_for(pins, sid, key):
    btns, cards = [], []
    for i, pin in enumerate(pins):
        _N[0] += 1
        cid = f"c{_N[0]}"
        btns.append(f'<button class="pin {pin["status"]}" type="button" aria-expanded="false" aria-controls="{cid}" data-card="{cid}">'
                    f'<b aria-hidden="true">{GLYPH[pin["status"]]}</b> {e(pin["label"]).replace(" · ", " <em>· ", 1) + "</em>" if " · " in pin["label"] else e(pin["label"])}</button>')
        cards.append(card_html(pin, cid))
    return "".join(btns), "".join(cards)


def card_html(pin, cid):
    return (f'<div class="card" id="{cid}" hidden><p>{e(pin["say"])}</p>'
            f'<div class="who">{"".join(pin["who"])}</div><div class="ev">{"".join(pin["ev"])}</div>'
            f'<div class="foot"><a href="{e(pin["link"])}">Full evidence →</a><span class="src">{e(pin["src"])}</span></div></div>')


def row_html(r, ind, pins, sid, key):
    s = r["s"].replace("\t", "    ")
    s = s[ind:] if s[:ind].strip() == "" else s.lstrip()
    t = r["t"]
    num = r["n"] if r["n"] is not None else r["o"]
    pcls = (" pinned " + pins[0]["status"]) if pins else ""
    pins_html, cards = pins_for(pins, sid, key)
    mark = {"add": "+", "del": "−", "madd": "+", "mdel": "−"}.get(t, "")
    tag = '<span class="seed">seeded bug</span>' if t == "madd" else ""
    return (f'<div class="r {t}{pcls}"><span class="n" data-m="{mark}">{num or ""}</span>'
            f'<span class="c">{hl(s) if s else " "}{tag}{pins_html}</span></div>{cards}')


def verdict_card(cx: Ctx):
    p = cx.pack
    reasons = [r["text"] for r in (p.get("card") or {}).get("reasons", [])][:1]
    so = p.get("signoff") or {}
    cmd = so.get("command", "")
    who = [chip("warn" if p.get("tier") in ("ask", "block") else "ok", f"{p.get('tier', '').upper()} from the mandate")]
    if so.get("owner"):
        who.append(chip("", f"{so['owner']} signs: {' / '.join(so.get('allowed_decisions', []))}"))
    ev = [f'<div class="evl"><span class="loc">sign</span><code>{e(cmd)}</code></div>'] if cmd else []
    return card_html(dict(say=(reasons[0] if reasons else ""), who=who, ev=ev, link=cx.pack_link("card"),
                          src=f"packs/{cx.cid}/pack.json → card, signoff"), "x")[len('<div class="card" id="x" hidden>'):-len("</div>")]


def build() -> str:
    code = Code()
    scenes, tabs = [], []
    for cid in ORDER:
        spec = SCENES[cid]
        cx = Ctx(cid)
        if not cx.pack:
            continue
        p = cx.pack
        fmt = dict(files=(p.get("diff") or {}).get("files", "?"))
        pins = [x for x in (resolve(cx, s, fmt) for s in spec["pins"]) if x]
        num = re.search(r"(\d+)$", (p.get("story") or {}).get("issue", "")) or re.search(r"(\d+)", cid)
        phrase = spec["verdict"].format(**fmt)
        if phrase.startswith("pin:"):  # the verdict is the label of a pin (from its record); drop to the pack's tier word if missing
            src_pin = resolve(cx, spec["pins"][int(phrase[4:])], fmt)
            phrase = src_pin["label"][:1].lower() + src_pin["label"][1:] if src_pin else ""
        verdict = dict(tier=p.get("tier", ""), owner=p.get("owner"), phrase=phrase, card=verdict_card(cx),
                       issue=(p.get("story") or {}).get("issue"), num=num.group(1) if num else cid, agent=p.get("agent_written"))
        headline = (p.get("story") or {}).get("headline", "")
        title = re.sub(rf"^(?:Agent-written )?change for #{re.escape(cid)}:\s*", "", headline, flags=re.I) or spec["title"]
        scenes.append(render_scene(code, cid, pins, verdict, title, spec["files"]))
        tabs.append(cid)
    # seeded bugs
    R = rj("measurement/results.json") or {}
    res = {r["change"]: r for r in R.get("mutants", [])}
    final = {r["change"]: r for r in R.get("changes", [])}  # routed with the reviews
    bugs = []
    for mid in sorted((x for x in res if "-mut" in x), key=lambda x: (ORDER.index(x.split("-mut")[0]) if x.split("-mut")[0] in ORDER else 9, int(x.split("-mut")[1]))):
        of = mid.split("-mut")[0]
        if of not in SCENES:
            continue
        pin, m = mutant_pin(mid, res[mid])
        if not pin:
            continue
        r = {**res[mid], **{k: v for k, v in final.get(mid, {}).items() if k in ("tier", "routed_to_human", "why")}}
        cx = Ctx(of)
        tier = r.get("tier") or ""
        was = (final.get(of) or {}).get("tier") or r.get("original_tier") or ""
        caught = pin["status"] == "bad"
        routed = bool(r.get("routed_to_human"))
        rpin, rname = reviewer_pin(mid, m, r.get("why") or [])
        phrase = ("caught by the checks" if caught else f"checks missed it; {rname} flagged it" if rname
                  else "got past checks and review")
        vcard = card_html(dict(say=(f"With this bug the change goes to {tier.upper()}; without it, {was.upper()}."
                                    + ("" if caught or rname or tier != was else " Nothing new fired: a human sees the change, not this bug.")),
                               who=[chip("bad" if caught else "warn", "a check failed" if caught else "no check failed"),
                                    chip("bad" if rname else "", f"{rname} flagged the line" if rname else "no reviewer flagged the line"),
                                    chip("", "reaches a human" if routed else "no human sees it")],
                               ev=[], link=f"overview.html#{mid}", src=f"measurement/results.json → changes {mid}, mutants {mid}"), "x")[len('<div class="card" id="x" hidden>'):-len("</div>")]
        num = re.search(r"(\d+)$", (cx.pack.get("story") or {}).get("issue", ""))
        verdict = dict(tier=tier, owner=cx.pack.get("owner") if routed else None, phrase=phrase, card=vcard,
                       issue=(cx.pack.get("story") or {}).get("issue"), num=num.group(1) if num else of, agent=cx.pack.get("agent_written"))
        file_ = m["file"]
        scenes.append(render_scene(code, of, [pin] + ([rpin] if rpin else []), verdict, SCENES[of]["title"], [file_], mutation=m, sid=mid))
        bugs.append((mid, r.get("kind") or m.get("kind") or "seeded bug", caught))
    code.save()
    return page(scenes, tabs, bugs)


PAGE_CSS = r"""
:root{--bg:#fff;--bg2:#f6f8fa;--fg:#1f2328;--muted:#59636e;--border:#d1d9e0;--accent:#0969da;
--ok:#1a7f37;--ok-bg:#dafbe1;--warn:#9a6700;--warn-bg:#fff8c5;--bad:#d1242f;--bad-bg:#ffebe9;
--add:#e6ffec;--del:#ffebe9;--k:#8250df;--s:#0a3069;--cm:#6e7781;--num:#0550ae;
--sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;color-scheme:light}
:root[data-theme=dark]{--bg:#0d1117;--bg2:#151b23;--fg:#e6edf3;--muted:#9198a1;--border:#3d444d;--accent:#4493f8;
--ok:#3fb950;--ok-bg:#12261e;--warn:#d29922;--warn-bg:#272115;--bad:#f85149;--bad-bg:#25171c;
--add:#12261e;--del:#25171c;--k:#d2a8ff;--s:#a5d6ff;--cm:#8b949e;--num:#79c0ff;color-scheme:dark}
[hidden]{display:none!important}*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 var(--sans)}
a{color:var(--accent);text-underline-offset:2px}
button{font:inherit;color:inherit;cursor:pointer}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.top{position:sticky;top:0;z-index:3;background:var(--bg);display:flex;align-items:center;gap:12px;padding:8px 16px 0}
.mark{font-weight:600;color:var(--fg);text-decoration:none;display:flex;align-items:center;gap:6px}
.mark i{font-style:normal;display:inline-grid;place-items:center;width:18px;height:18px;border:1.5px solid currentColor;border-radius:5px;font-size:11px}
.links{margin-left:auto;display:flex;gap:12px;align-items:center;font-size:13px}
.links a{color:var(--muted);text-decoration:none}.links a:hover{color:var(--accent)}
.links button{background:none;border:0;color:var(--muted);padding:2px 4px;font-size:15px}
.head{position:sticky;top:34px;z-index:2;background:var(--bg);padding:6px 16px 10px;border-bottom:1px solid var(--border)}
.title{color:var(--muted);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:6px}
.title a{color:var(--muted);font-family:var(--mono)}.title .ag{border:1px solid var(--border);border-radius:4px;padding:0 5px;font-size:12px}
.verdict{display:inline-flex;align-items:baseline;gap:0;border:1px solid var(--border);border-radius:999px;padding:4px 14px;background:var(--bg2);font-size:15px;max-width:100%}
.verdict span{color:var(--fg);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.verdict.warn{border-color:var(--warn);background:var(--warn-bg)}.verdict.warn b{color:var(--warn)}
.verdict.bad{border-color:var(--bad);background:var(--bad-bg)}.verdict.bad b{color:var(--bad)}
.verdict.ok{border-color:var(--ok);background:var(--ok-bg)}.verdict.ok b{color:var(--ok)}
.verdict b{font-weight:600;white-space:nowrap}
.vcard{margin-top:10px}
.code{font:13px/20px var(--mono);padding:8px 0 96px;min-height:calc(100vh - 126px)}
.file{font:12px/1.4 var(--mono);color:var(--fg);padding:16px 16px 6px;font-weight:600;overflow-wrap:anywhere}.file span{color:var(--muted);font-weight:400}
.r{display:grid;grid-template-columns:52px 1fr;min-height:20px}
.r .n{color:var(--muted);text-align:right;padding-right:12px;user-select:none;opacity:.7;position:relative}
.r .n::after{content:attr(data-m);position:absolute;right:2px;opacity:.9}
.r .c{white-space:pre-wrap;overflow-wrap:anywhere;padding-right:16px}
.r.add,.r.madd{background:var(--add)}.r.del,.r.mdel{background:var(--del)}.r.del .c,.r.mdel .c{color:var(--muted)}
.r.madd{box-shadow:inset 3px 0 var(--bad)}
.r.gap .c,.r.more .c{color:var(--muted)}.r.more{margin-top:12px;padding:4px 0}
.r.pinned.bad{box-shadow:inset 3px 0 var(--bad)}.r.pinned.weak,.r.pinned.ask{box-shadow:inset 3px 0 var(--warn)}.r.pinned.ok{box-shadow:inset 3px 0 var(--ok)}
.fold summary{list-style:none;display:grid;grid-template-columns:52px 1fr;color:var(--accent);cursor:pointer}
.fold summary::-webkit-details-marker{display:none}.fold[open] summary{color:var(--muted)}
i.tk{font-style:normal;color:var(--k)}i.ts,i.ta{font-style:normal;color:var(--s)}i.tc{color:var(--cm)}i.tn{font-style:normal;color:var(--num)}
.pin{display:inline-flex;align-items:center;gap:5px;margin:1px 0 1px 12px;padding:0 9px;border-radius:999px;border:1px solid;font:600 12.5px/20px var(--sans);white-space:nowrap;vertical-align:1px;background:var(--bg)}
.pin b{font-weight:700}.pin em{font-style:normal;font-weight:400}
.pin.bad{color:var(--bad);border-color:var(--bad);background:var(--bad-bg)}
.pin.weak,.pin.ask{color:var(--warn);border-color:var(--warn);background:var(--warn-bg)}
.pin.ok{color:var(--ok);border-color:var(--ok);background:var(--ok-bg)}
.pin[aria-expanded=true]{outline:2px solid currentColor;outline-offset:1px}
.seed{margin-left:10px;font:600 11px var(--sans);color:var(--bad);text-transform:uppercase;letter-spacing:.04em}
.card{font:14px/1.5 var(--sans);margin:6px 16px 10px 52px;max-width:600px;border:1px solid var(--border);border-radius:8px;padding:12px 14px;background:var(--bg)}
.vcard{margin-left:0}
.card p{margin:0 0 8px;font-size:15px}
.who{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}
.chip{font-size:12px;border:1px solid var(--border);border-radius:999px;padding:0 8px;color:var(--muted)}
.chip.bad{color:var(--bad);border-color:var(--bad)}.chip.ok{color:var(--ok);border-color:var(--ok)}.chip.warn{color:var(--warn);border-color:var(--warn)}
.ev{display:grid;gap:4px;margin-bottom:8px}
.evl{display:grid;grid-template-columns:minmax(0,max-content) 1fr;gap:2px 10px;font-size:12px;align-items:baseline}
.evl .loc{color:var(--muted);font-family:var(--mono);white-space:nowrap}
.evl code{font:12px/1.5 var(--mono);background:var(--bg2);border-radius:4px;padding:1px 6px;overflow-wrap:anywhere}
.evl b.ok{color:var(--ok)}.evl b.bad{color:var(--bad)}
.foot{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;font-size:13px}
.foot .src{color:var(--muted);font:11px var(--mono)}
.bar{position:fixed;left:0;right:0;bottom:0;z-index:4;background:var(--bg);border-top:1px solid var(--border);padding:10px 12px calc(10px + env(safe-area-inset-bottom))}
.row{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;max-width:100%;margin:0 auto;width:max-content}
.row::-webkit-scrollbar{display:none}
.row button{flex:none;border:1px solid var(--border);background:var(--bg);border-radius:999px;padding:6px 14px;font-size:14px;white-space:nowrap}
.row button[aria-pressed=true]{border-color:var(--fg);background:var(--fg);color:var(--bg)}
.row button.sneak{border-style:dashed}
.row button small{opacity:.7;font-family:var(--mono);margin-left:6px}
.row .back{border:0;color:var(--muted)}
@media (max-width:600px){.evl{grid-template-columns:1fr}.file span{display:none}.row{gap:4px}.row button{padding:4px 8px;font-size:12.5px}.bar{padding-left:8px;padding-right:8px}.r{grid-template-columns:40px 1fr}.r .n{padding-right:8px;font-size:11px}.code{font-size:12px;line-height:18px;min-height:calc(100vh - 136px)}
.fold summary{grid-template-columns:40px 1fr}.card{margin-left:12px;margin-right:12px}.file{padding-left:12px}
.verdict{font-size:14px;padding:3px 12px}.pin{margin-left:6px}.row{width:auto}.head{padding:6px 12px 8px}.title{white-space:normal;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;line-height:1.35}.top{padding:8px 12px 0}.links{gap:8px;font-size:12px}}
"""

PAGE_JS = r"""
(function(){
var scenes=[].slice.call(document.querySelectorAll('.scene')),bar=document.getElementById('bar'),
 main=document.getElementById('row-main'),bugs=document.getElementById('row-bugs');
function show(id,push){
 var s=scenes.filter(function(x){return x.dataset.id===id})[0]||scenes[0];id=s.dataset.id;
 scenes.forEach(function(x){x.hidden=x!==s});
 var isBug=id.indexOf('-mut')>0;main.hidden=isBug;bugs.hidden=!isBug;
 [].forEach.call(bar.querySelectorAll('[data-go]'),function(b){b.setAttribute('aria-pressed',b.dataset.go===id||(b.dataset.go==='bugs'&&isBug)?'true':'false')});
 var cur=bar.querySelector('#row-bugs [aria-pressed=true]');if(cur&&cur.scrollIntoView)cur.scrollIntoView({block:'nearest',inline:'nearest'});
 if(push!==false)history.replaceState(null,'','#'+id);
 window.scrollTo(0,0);
}
bar.addEventListener('click',function(ev){var b=ev.target.closest('[data-go]');if(!b)return;
var g=b.dataset.go;if(g==='bugs')g=bugs.querySelector('[data-go]:not(.back)').dataset.go;if(g==='back')g=main.querySelector('[data-go]').dataset.go;show(g)});
document.addEventListener('click',function(ev){var b=ev.target.closest('[data-card]');if(!b)return;
 var c=document.getElementById(b.dataset.card),open=b.getAttribute('aria-expanded')==='true';
 [].forEach.call(document.querySelectorAll('[data-card][aria-expanded=true]'),function(o){o.setAttribute('aria-expanded','false');document.getElementById(o.dataset.card).hidden=true});
 if(!open){c.hidden=false;b.setAttribute('aria-expanded','true');var r=c.getBoundingClientRect();if(r.bottom>innerHeight-70)scrollBy({top:r.bottom-innerHeight+90,behavior:'smooth'})}});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'){var o=document.querySelector('[data-card][aria-expanded=true]');if(o)o.click()}});
show(decodeURIComponent(location.hash.slice(1))||'2234',false);
})();
function csTheme(){var d=document.documentElement,c=d.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),n=c==="dark"?"light":"dark";d.dataset.theme=n;try{localStorage.setItem("cs-theme",n)}catch(_){}}
"""


def page(scenes, tabs, bugs) -> str:
    main = "".join(f'<button type="button" data-go="{e(t)}" aria-pressed="false">{e(t)}</button>' for t in tabs)
    if bugs:
        main += '<button type="button" class="sneak" data-go="bugs" aria-pressed="false">sneak a bug in</button>'
    brow = '<button type="button" class="back" data-go="back" aria-label="Back to the changes">←</button>' + "".join(
        f'<button type="button" data-go="{e(mid)}" aria-pressed="false">{e(kind)}<small>{e(mid.replace("-mut", "·"))}</small></button>'
        for mid, kind, caught in bugs)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Countersign · the code is the scene</title>
<meta name="description" content="Countersign: AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it cannot, and a named human countersigns the rest.">
<script>try{{var t=localStorage.getItem("cs-theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
<style>{PAGE_CSS.strip()}</style>
</head><body>
<header class="top"><a class="mark" href="index.html"><i>✓</i>Countersign</a>
<nav class="links" aria-label="More"><a href="tour.html">Tour</a><a href="packs/2234/pack.html">Evidence pack</a><a href="overview.html">Numbers</a><a href="pitch.html">Pitch</a>
<button type="button" aria-label="Switch light or dark theme" onclick="csTheme()">◐</button></nav></header>
<main>{"".join(scenes)}</main>
<nav class="bar" id="bar" aria-label="Choose a change"><div class="row" id="row-main">{main}</div><div class="row" id="row-bugs" hidden>{brow}</div></nav>
<script>{PAGE_JS.strip()}</script>
</body></html>
"""


def main():
    (SITE / "index.html").write_text(build(), encoding="utf-8")
    print("wrote site/index.html")


if __name__ == "__main__":
    main()
