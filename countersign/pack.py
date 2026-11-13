"""Stage 5: the evidence pack (pack.json, pack.md, pack.html) a named owner signs.

pack.json is deterministic for the same inputs, mandate and trust state (no timestamps inside), so its
sha256 identifies exactly what the owner saw. The renderers only format what is in pack.json.
"""

from __future__ import annotations

import html
from pathlib import Path

from . import __version__, decide as decide_mod, ledger, mandate as mandate_mod, trust, verify
from .common import HUMAN_TIERS, Workspace, now_iso, read_json, sha256_hex, write_json

SCHEMA = "countersign.pack/v1"


def _file_ref(path: Path, root: Path) -> dict:
    p = Path(path)
    shown = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
    return {"path": shown, "sha256": sha256_hex(p.read_bytes())}


def build(ws: Workspace, change: str, use_trust: bool = True) -> dict:
    """verify + decide + assemble. Reads facts, reviews, requirements, mandate and the ledger; writes nothing.
    use_trust=False ignores trust events (caps = mandate), so a replay measures the reviewer, not the ledger state."""
    facts_path = ws.facts_path(change)
    if not facts_path.exists():
        raise FileNotFoundError(f"no {facts_path}: run the deterministic checks first (stage 1)")
    facts = read_json(facts_path)
    reqs = ws.requirements(change)
    m = mandate_mod.load(ws)
    msig = mandate_mod.signature_status(ws, m)
    state = trust.derive(m, ledger.read(ws) if use_trust else [])

    v = verify.Verifier(ws.repo, facts, reqs, m["decision"]["code_line_tolerance"])
    raw_reviews = ws.reviews(change)
    reviews = {name: verify.verify_review(r, v) for name, r in raw_reviews.items()}
    d = decide_mod.decide(facts, reviews, reqs, m, msig, trust.caps(state))
    # What the AI would recommend under the mandate's own caps. During probation this is what spot-checks grade.
    ai_alone = decide_mod.decide(facts, reviews, reqs, m, msig, {})["tier"]

    req_file = ws.root / reqs["_path"] if not Path(reqs["_path"]).is_absolute() else Path(reqs["_path"])
    inputs = {"facts": _file_ref(facts_path, ws.root), "requirements": _file_ref(req_file, ws.root),
              "reviews": {n: _file_ref(ws.inputs / "reviews" / change / f"{n}.json", ws.root) for n in raw_reviews}}
    simulated = bool(facts.get("simulated")) or any(r.get("simulated") for r in raw_reviews.values())

    tools = [{k: c.get(k) for k in ("id", "tool", "tool_version", "status", "summary", "duration_s", "log")} for c in facts.get("checks", [])]
    reviewers = []
    for name, r in reviews.items():
        fs = r.get("findings", [])
        reviewers.append({"reviewer": name, "model": r.get("model"), "vendor": r.get("vendor"),
                          "prompt_version": r.get("prompt_version"), "reviewed_at": r.get("reviewed_at"),
                          "inputs": r.get("inputs", []), "findings": len(fs),
                          "verified": sum(f["status"] == "verified" for f in fs),
                          "rejected": sum(f["status"] == "rejected" for f in fs),
                          "refusals": len(r.get("refusals", []))})

    not_checked = [{"id": n["id"], "reason": n["reason"], "source": "facts.json not_run"} for n in facts.get("not_run", [])]
    not_checked += [{"id": c["id"], "reason": f"{c['status']}: {c.get('summary', '')}", "source": "check did not pass or fail"}
                    for c in facts.get("checks", []) if c["status"] in ("skipped", "error")]
    known = {c["id"] for c in facts.get("checks", [])}
    for a in d["areas"]:
        not_checked += [{"id": c, "reason": f"mandated by area {a['name']} but absent from facts.json", "source": "mandate"}
                        for c in a["checks"] if c not in known and c not in {x["id"] for x in not_checked}]
    not_checked += [{"id": g["id"], "reason": g["reason"], "source": "mandate known gap"} for g in m["known_gaps"]]

    verified = [f for f in d["findings"] if f["status"] == "verified"]
    rejected = [f for f in d["findings"] if f["status"] == "rejected"]
    residual = [f"{c['id']} not proven: " + _codes(c) for c in d["clauses"] if c["status"] == "refused"]
    residual += [f"Reviewer refusal ({r['reviewer']}): {r['topic']}" for r in d["reviewer_refusals"]]
    residual += [f"Open {f['severity']} finding {f['reviewer']}:{f['id']}: {f['title']}" for f in verified if f["severity"] in ("blocker", "major")]
    residual += [f"Unsupported {f['severity']} claim {f['reviewer']}:{f['id']} was rejected for lack of evidence, not disproven: {f['title']}"
                 for f in rejected if f["severity"] in ("blocker", "major")]
    residual += [f"{x['id']} not run ({x['reason']})" for x in not_checked if x["source"] != "mandate known gap"]
    residual += [f"Area {a['name']} is on probation: {a['cap_reason']}" for a in d["areas"] if state[a["name"]]["probation"]]
    residual.append(f"Standing gaps of this pipeline: {', '.join(g['id'] for g in m['known_gaps'])} (see not checked)")

    tier = d["tier"]
    return {
        "schema": SCHEMA,
        "change": change,
        "branch": facts.get("branch"), "base": facts.get("base"), "head": facts.get("head"),
        "commit_message": facts.get("commit_message"), "author": facts.get("author"), "agent_written": facts.get("agent_written"),
        "diff": {k: facts.get("diff", {}).get(k) for k in ("files", "insertions", "deletions")},
        "simulated": simulated,
        "mutation": facts.get("mutation"),
        "engine": {"name": "countersign", "version": __version__},
        "mandate": m.summary(ws),
        "inputs": inputs,
        "requirement_set": {"source": reqs.get("source"), "official": reqs.get("official", False)},
        "tier": tier,
        "ai_recommendation": ai_alone,
        "why": d["decisive"],
        "drivers": d["drivers"],
        "owner": d["owner"],
        "primary_area": d["primary_area"],
        "notify": d["notify"],
        "areas": [{k: a[k] for k in ("name", "owner", "sensitivity", "max_ai_tier", "cap", "cap_reason", "files")} for a in d["areas"]],
        "requirements": d["clauses"],
        "checked_by": {"tools": tools, "reviewers": reviewers,
                       "engine": f"countersign {__version__} under mandate {m['id']} v{m.version} ({m.sha256[:12]})"},
        "findings": verified,
        "refused": {"clauses": [c for c in d["clauses"] if c["status"] == "refused"], "reviewer_refusals": d["reviewer_refusals"]},
        "rejected_claims": rejected,
        "not_checked": not_checked,
        "residual_risk": residual,
        "risk": d["risk"],
        "rules_fired": d["rules_fired"],
        "signoff": {
            "required": tier in HUMAN_TIERS,
            "owner": d["owner"],
            "allowed_decisions": ["reject", "request-changes"] if tier == "block" else ["accept", "reject", "request-changes"],
            "command": f"countersign sign {change} --as {d['owner']} --decision <accept|reject|request-changes> --note \"...\"",
            "statement": (f"I, {d['owner']}, have read what was checked and by whom, what was not checked and why, "
                          "and the residual risk listed in this pack, and I own this decision."),
        },
    }


def write(ws: Workspace, pack: dict) -> Path:
    out = ws.pack_dir(pack["change"])
    write_json(out / "pack.json", pack)
    (out / "pack.md").write_text(to_markdown(pack), encoding="utf-8")
    (out / "pack.html").write_text(to_html(pack), encoding="utf-8")
    return out


# --- one-screen sign-off card (CLI) ---------------------------------------------

def _short(text: str, n: int = 220) -> str:
    return text if len(text) <= n else text[: n - 3] + "..."


def _codes(c: dict) -> str:
    return "; ".join(dict.fromkeys(r["code"] for r in c["reasons"]))

def card(p: dict) -> str:
    lines = [f"Countersign evidence pack: change {p['change']} ({p['branch']}, {p['head']})",
             f"Recommended tier: {p['tier'].upper()}   owner: {p['owner']}   risk score: {p['risk']['score']}",
             "Why:", *(f"  - [{w['source']}] {w['id']}: {_short(w['why'])}" for w in p["why"]), "",
             "Requirements:"]
    lines += [f"  {c['id']:<14} {c['status'].upper():<8} " + (_codes(c) or "both reviewers met, checks pass")
              for c in p["requirements"]]
    lines += ["", "Checked by:"]
    lines += [f"  {t['id']:<24} {t['status']:<8} {t.get('tool') or ''} {t.get('tool_version') or ''}".rstrip() for t in p["checked_by"]["tools"]]
    lines += [f"  reviewer {r['reviewer']:<15} {r['model']} ({r['vendor']}, {r['prompt_version']}): "
              f"{r['verified']} verified, {r['rejected']} rejected findings, {r['refusals']} refusals" for r in p["checked_by"]["reviewers"]]
    lines += ["", "Refused to decide:"]
    lines += [f"  {c['id']}: " + _short("; ".join(f"{r['code']} ({r['detail']})" for r in c["reasons"]), 400) for c in p["refused"]["clauses"]]
    lines += [f"  {r['reviewer']}: {r['topic']} -> {r['who_should_decide']}" for r in p["refused"]["reviewer_refusals"]]
    if not (p["refused"]["clauses"] or p["refused"]["reviewer_refusals"]):
        lines.append("  nothing")
    lines += ["", "Not checked:"] + [f"  {x['id']}: {_short(x['reason'])}" for x in p["not_checked"]]
    lines += ["", "Residual risk:"] + [f"  - {_short(r)}" for r in p["residual_risk"]]
    return "\n".join(lines)


# --- Markdown -------------------------------------------------------------------

def _verdicts(c: dict) -> str:
    return ", ".join(f"{n}: {v['verdict']} ({v['verified']}/{v['cited']} verified)" for n, v in c["verdicts"].items()) or "none"


def _ev_md(e: dict) -> str:
    mark = "OK" if e["verified"] else "REJECTED"
    what = {"code": lambda: f"`{e.get('file')}:{e.get('line')}` @{e.get('rev', 'head')}: `{e.get('quote', '')}`",
            "test": lambda: f"test `{e.get('name')}` {e.get('outcome', '')}",
            "check": lambda: f"check `{e.get('id')}`",
            "requirement": lambda: f"{e.get('req')}: \"{e.get('quote', '')}\"",
            "issue": lambda: f"{e.get('url')}"}.get(e.get("kind"), lambda: str(e))()
    return f"    - [{mark}] {what} ({e['note']})"


def to_markdown(p: dict) -> str:
    sim = " (SIMULATED inputs)" if p["simulated"] else ""
    out = [f"# Evidence pack: change {p['change']}{sim}", "",
           f"**Recommended tier: {p['tier'].upper()}** · owner **{p['owner']}** · risk score {p['risk']['score']}", "",
           f"Branch `{p['branch']}` ({p['base']}..{p['head']}), {p['diff']['files']} files, +{p['diff']['insertions']} -{p['diff']['deletions']}. "
           f"Author {p['author']} (agent-written: {p['agent_written']}). Commit: {p['commit_message']}", "",
           f"Mandate `{p['mandate']['id']}` v{p['mandate']['version']} sha256 `{p['mandate']['sha256'][:16]}`, "
           f"signature: {'valid, ' + p['mandate']['signature'].get('signed_by', '') if p['mandate']['signature']['valid'] else 'NOT VALID (' + p['mandate']['signature']['reason'] + ')'}", ""]
    if p.get("mutation"):
        out += [f"> Seeded mutant of {p['mutation'].get('of')}: {p['mutation'].get('description')}", ""]
    out += ["## Why this tier", ""] + [f"- **{w['tier']}** from {w['source']} `{w['id']}`: {w['why']}" for w in p["why"]]
    out += ["", "<details><summary>All tier drivers</summary>", ""] + [f"- {w['tier']}: {w['source']} `{w['id']}`: {w['why']}" for w in p["drivers"]] + ["", "</details>"]
    out += ["", "## What the AI refused to decide, and why", ""]
    out += [f"- **{c['id']}**: " + "; ".join(f"`{r['code']}` {r['detail']}" for r in c["reasons"]) for c in p["refused"]["clauses"]]
    out += [f"- **{r['reviewer']}** refused: {r['topic']}. Why: {r['reason']}. Who should decide: {r['who_should_decide']}" for r in p["refused"]["reviewer_refusals"]]
    if not (p["refused"]["clauses"] or p["refused"]["reviewer_refusals"]):
        out.append("- Nothing: every clause was proven and no reviewer refused a topic.")
    out += ["", "## Requirement trace", "", "| Clause | Status | Verdicts | Checks | Reasons |", "|---|---|---|---|---|"]
    out += [f"| {c['id']} | {c['status']} | {_verdicts(c)} | {', '.join(x['id'] + ': ' + x['status'] for x in c['checks']) or '-'} | "
            f"{_codes(c) or '-'} |" for c in p["requirements"]]
    out += ["", "## What was checked, and by whom", "", "| Check | Status | Tool | Summary |", "|---|---|---|---|"]
    out += [f"| {t['id']} | {t['status']} | {t.get('tool') or ''} {t.get('tool_version') or ''} | {t.get('summary') or ''} |" for t in p["checked_by"]["tools"]]
    out += ["", "| Reviewer | Model | Prompt | Verified findings | Rejected | Refusals |", "|---|---|---|---|---|---|"]
    out += [f"| {r['reviewer']} | {r['model']} ({r['vendor']}) | {r['prompt_version']} | {r['verified']} | {r['rejected']} | {r['refusals']} |" for r in p["checked_by"]["reviewers"]]
    out += ["", f"Decision engine: {p['checked_by']['engine']}", "", "## What the AI found (verified findings)", ""]
    for f in p["findings"]:
        out += [f"- **{f['reviewer']}:{f['id']}** [{f['severity']}, {f['category']}] {f['title']} -> tier {f['tier']}", f"  {f['claim']}"]
        out += [_ev_md(e) for e in f["evidence"]]
    if not p["findings"]:
        out.append("- No verified findings.")
    out += ["", "## Rejected: unsupported claims", ""]
    for f in p["rejected_claims"]:
        out += [f"- **{f['reviewer']}:{f['id']}** [{f['severity']}] {f['title']}: {f['rejection_reason']}"] + [_ev_md(e) for e in f["evidence"]]
    if not p["rejected_claims"]:
        out.append("- None.")
    out += ["", "## What was not checked, and why", ""] + [f"- `{x['id']}` ({x['source']}): {x['reason']}" for x in p["not_checked"]]
    out += ["", "## Residual risk", ""] + [f"- {r}" for r in p["residual_risk"]]
    out += ["", f"## Risk score: {p['risk']['score']} -> {p['risk']['tier']}", "", "| Factor | Points | Reason |", "|---|---:|---|"]
    out += [f"| {f['factor']} | {f['points']} | {f['reason']} |" for f in p["risk"]["factors"]]
    out += [f"| **total** | **{p['risk']['score']}** | bands: {p['risk']['thresholds']} |"]
    s = p["signoff"]
    out += ["", "## Sign-off", "", f"Owner: **{s['owner']}**" + (f" (FYI: {', '.join(p['notify'])})" if p["notify"] else ""),
            f"Sign-off required: {'yes' if s['required'] else 'no (AI-cleared; spot-checks apply)'}; allowed decisions: {', '.join(s['allowed_decisions'])}", "",
            f"> {s['statement']}", "", f"```\n{s['command']}\n```", ""]
    return "\n".join(out)


# --- HTML (self-contained, phone friendly) ----------------------------------------

CSS = """
:root{--fg:#1d2330;--mut:#5b6474;--bg:#fff;--card:#f5f6f8;--line:#dfe2e7;--silent:#4b7a52;--notify:#2f62c9;--ask:#b26a00;--block:#b3261e}
@media (prefers-color-scheme:dark){:root{--fg:#e6e8ec;--mut:#9aa3b2;--bg:#14171c;--card:#1d2128;--line:#2e333c}}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
main{max-width:880px;margin:0 auto;padding:16px}h1{font-size:1.35em;margin:.2em 0}h2{font-size:1.1em;margin:1.6em 0 .5em;border-bottom:1px solid var(--line);padding-bottom:.2em}
.mut{color:var(--mut)}.card{background:var(--card);border-radius:10px;padding:12px 14px;margin:8px 0}
.tier{display:inline-block;color:#fff;border-radius:999px;padding:2px 12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.t-silent{background:var(--silent)}.t-notify{background:var(--notify)}.t-ask{background:var(--ask)}.t-block{background:var(--block)}
.refused{border-left:5px solid var(--ask)}.rejected{border-left:5px solid var(--block)}.found{border-left:5px solid var(--notify)}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.92em}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.n{text-align:right;font-variant-numeric:tabular-nums}code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;word-break:break-word}
.ok{color:var(--silent);font-weight:600}.no{color:var(--block);font-weight:600}ul{padding-left:1.2em}li{margin:.25em 0}
code.nw{white-space:nowrap;word-break:normal}.banner{background:var(--block);color:#fff;padding:6px 12px;border-radius:8px;font-weight:600}
pre{background:var(--card);padding:10px;border-radius:8px;overflow-x:auto;font-size:12.5px}
"""


def _e(x) -> str:
    return html.escape("" if x is None else str(x))


def _tier(t: str) -> str:
    return f'<span class="tier t-{_e(t)}">{_e(t)}</span>'


def _table(headers: list[str], rows: list[list[str]], numeric: set[int] = frozenset()) -> str:
    head = "".join(f"<th>{_e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f'<td{" class=n" if i in numeric else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _ev_html(e: dict) -> str:
    what = {"code": f"<code>{_e(e.get('file'))}:{_e(e.get('line'))}</code> @{_e(e.get('rev', 'head'))}: <code>{_e(e.get('quote'))}</code>",
            "test": f"test <code>{_e(e.get('name'))}</code> {_e(e.get('outcome'))}",
            "check": f"check <code>{_e(e.get('id'))}</code>",
            "requirement": f"{_e(e.get('req'))}: &ldquo;{_e(e.get('quote'))}&rdquo;",
            "issue": _e(e.get("url"))}.get(e.get("kind"), _e(e))
    mark = '<span class="ok">verified</span>' if e["verified"] else '<span class="no">not verified</span>'
    return f"<li>{mark} {what}<br><span class=mut>{_e(e['note'])}</span></li>"


def _finding(f: dict, cls: str) -> str:
    extra = f"<p class=mut>Rejected: {_e(f['rejection_reason'])}</p>" if f["status"] == "rejected" else f"<p class=mut>Tier effect: {_tier(f['tier'])} {_e(f.get('tier_reason', ''))}</p>"
    fix = f"<p><b>Suggested fix:</b> {_e(f['suggested_fix'])}</p>" if f.get("suggested_fix") else ""
    return (f'<div class="card {cls}"><b>{_e(f["reviewer"])}:{_e(f["id"])}</b> [{_e(f["severity"])}, {_e(f["category"])}] {_e(f["title"])}'
            f'<p>{_e(f["claim"])}</p><ul>{"".join(_ev_html(e) for e in f["evidence"])}</ul>{fix}{extra}</div>')


def to_html(p: dict) -> str:
    ms = p["mandate"]["signature"]
    s = p["signoff"]
    refused = [f'<div class="card refused"><b>{_e(c["id"])}</b> {_e(c["text"])}<ul>'
               + "".join(f"<li><code>{_e(r['code'])}</code> {_e(r['detail'])}</li>" for r in c["reasons"]) + "</ul></div>"
               for c in p["refused"]["clauses"]]
    refused += [f'<div class="card refused"><b>{_e(r["reviewer"])}</b> ({_e(r["model"])}) refused: {_e(r["topic"])}'
                f'<p>Why: {_e(r["reason"])}<br>Who should decide: <b>{_e(r["who_should_decide"])}</b></p></div>'
                for r in p["refused"]["reviewer_refusals"]]
    req_rows = [[f"<b>{_e(c['id'])}</b><br><span class=mut>{_e(c['text'])}</span>",
                 f"<span class={'ok' if c['status'] == 'proven' else 'no'}>{_e(c['status'])}</span>",
                 "<br>".join(f"{_e(n)}: {_e(v['verdict'])} ({v['verified']}/{v['cited']} verified)" for n, v in c["verdicts"].items()) or "none",
                 "<br>".join(f"{_e(x['id'])}: {_e(x['status'])}" for x in c["checks"]) or "-",
                 "<br>".join(f"<code class=nw>{_e(code)}</code>" for code in dict.fromkeys(r["code"] for r in c["reasons"])) or "-"]
                for c in p["requirements"]]
    tool_rows = [[_e(t["id"]), _e(t["status"]), _e(f"{t.get('tool') or ''} {t.get('tool_version') or ''}"), _e(t.get("summary"))] for t in p["checked_by"]["tools"]]
    rev_rows = [[_e(r["reviewer"]), _e(f"{r['model']} ({r['vendor']})"), _e(r["prompt_version"]), _e(r["reviewed_at"]),
                 str(r["verified"]), str(r["rejected"]), str(r["refusals"])] for r in p["checked_by"]["reviewers"]]
    risk_rows = [[_e(f["factor"]), _e(f["points"]), _e(f["reason"])] for f in p["risk"]["factors"]]
    risk_rows.append(["<b>total</b>", f"<b>{_e(p['risk']['score'])}</b>", f"-> {_tier(p['risk']['tier'])} (bands {_e(p['risk']['thresholds'])})"])
    driver_rows = [[_tier(w["tier"]), _e(w["source"]), f"<code>{_e(w['id'])}</code>", _e(w["why"])] for w in p["drivers"]]
    area_rows = [[_e(a["name"]), _e(a["owner"]), _e(a["sensitivity"]), _tier(a["cap"]), _e(a["cap_reason"]), str(len(a["files"]))] for a in p["areas"]]
    mut = f'<p class="card">Seeded mutant of {_e(p["mutation"].get("of"))}: {_e(p["mutation"].get("description"))}</p>' if p.get("mutation") else ""
    body = f"""
<main>
{'<p class="banner">Simulated inputs: fixture data, not a real run</p>' if p["simulated"] else ""}
<p class=mut>Countersign evidence pack</p>
<h1>Change {_e(p["change"])}: {_e(p["commit_message"])}</h1>
<p>{_tier(p["tier"])} &nbsp; owner <b>{_e(p["owner"])}</b>{" &middot; FYI " + _e(", ".join(p["notify"])) if p["notify"] else ""} &middot; risk score <b>{_e(p["risk"]["score"])}</b></p>
<p class=mut>Branch <code>{_e(p["branch"])}</code> {_e(p["base"])}..{_e(p["head"])} &middot; {_e(p["diff"]["files"])} files, +{_e(p["diff"]["insertions"])} &minus;{_e(p["diff"]["deletions"])}
&middot; author {_e(p["author"])} (agent-written: {_e(p["agent_written"])})<br>
Mandate {_e(p["mandate"]["id"])} v{_e(p["mandate"]["version"])} <code>{_e(p["mandate"]["sha256"][:16])}</code>:
{"signed by " + _e(ms.get("signed_by")) if ms["valid"] else "<b class=no>signature not valid: " + _e(ms["reason"]) + "</b>"}</p>
{mut}
<h2>Why {_e(p["tier"])}</h2>
<ul>{"".join(f"<li>{_tier(w['tier'])} <b>{_e(w['source'])}</b> <code>{_e(w['id'])}</code>: {_e(w['why'])}</li>" for w in p["why"])}</ul>
<details><summary>All tier drivers (tier = strictest)</summary>{_table(["Tier", "Source", "Id", "Why"], driver_rows)}</details>

<h2>What the AI refused to decide, and why</h2>
{"".join(refused) or '<p class="card">Nothing: every clause was proven and no reviewer refused a topic.</p>'}

<h2>Requirement trace</h2>
<p class=mut>Requirement set: {_e(p["requirement_set"]["source"])} (official: {_e(p["requirement_set"]["official"])}). Proven = both reviewers say met with verified evidence and the clause's checks pass.</p>
{_table(["Clause", "Status", "Verdicts", "Checks", "Reasons"], req_rows)}

<h2>What was checked, and by whom</h2>
{_table(["Check", "Status", "Tool", "Summary"], tool_rows)}
{_table(["Reviewer", "Model", "Prompt", "Reviewed", "Verified", "Rejected", "Refusals"], rev_rows, {4, 5, 6})}
<p class=mut>Decision engine: {_e(p["checked_by"]["engine"])}</p>
<h3>Areas touched</h3>
{_table(["Area", "Owner", "Sensitivity", "AI cap", "Cap source", "Files"], area_rows, {5})}

<h2>What the AI found (verified)</h2>
{"".join(_finding(f, "found") for f in p["findings"]) or "<p>No verified findings.</p>"}

<h2>Rejected: unsupported claims</h2>
<p class=mut>Kept for audit and counted against the reviewer. A claim with no verifiable evidence never affects the tier.</p>
{"".join(_finding(f, "rejected") for f in p["rejected_claims"]) or "<p>None.</p>"}

<h2>What was not checked, and why</h2>
<ul>{"".join(f"<li><code>{_e(x['id'])}</code> <span class=mut>({_e(x['source'])})</span>: {_e(x['reason'])}</li>" for x in p["not_checked"])}</ul>

<h2>Residual risk</h2>
<ul>{"".join(f"<li>{_e(r)}</li>" for r in p["residual_risk"])}</ul>

<h2>Risk score</h2>
{_table(["Factor", "Points", "Reason"], risk_rows, {1})}

<h2>Sign-off</h2>
<div class="card">
<p>Owner: <b>{_e(s["owner"])}</b>. Sign-off required: <b>{"yes" if s["required"] else "no (AI-cleared; subject to spot-checks)"}</b>. Allowed decisions: {_e(", ".join(s["allowed_decisions"]))}.</p>
<p><i>{_e(s["statement"])}</i></p>
<pre>{_e(s["command"])}</pre>
<p class=mut>The signature covers sha256 of this pack's canonical JSON, the decision, the time and the signer, and is appended to the hash-chained ledger.</p>
</div>
<p class=mut>Inputs: facts {_e(p["inputs"]["facts"]["path"])} ({_e(p["inputs"]["facts"]["sha256"][:12])}),
requirements {_e(p["inputs"]["requirements"]["path"])}, reviews {_e(", ".join(f"{k} ({v['sha256'][:12]})" for k, v in p["inputs"]["reviews"].items()))}.
Rendered {_e(now_iso())}.</p>
</main>"""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>Countersign pack {_e(p['change'])}: {_e(p['tier'])}</title><style>{CSS}</style></head><body>{body}</body></html>\n")
