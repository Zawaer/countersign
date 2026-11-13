# Countersign: reference pipeline architecture (shared contract)

> AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.

This file is the contract between the pipeline's parts. Every stage reads and writes plain files in this repo, so every step of a review can be replayed and audited.

## Pipeline

```
change (branch + requirement IDs)
  1. facts      deterministic checks: diff stats, areas touched, build, tests, "tests fail without the fix", API surface, analyzers
  2. reviews    two independent AI reviewers (Claude, Codex/GPT) produce structured findings + per-requirement verdicts
  3. verify     the engine checks every cited piece of evidence; no verifiable evidence -> finding rejected (logged)
  4. decide     per requirement clause: proven / refused (with reason); risk score (explainable, additive) -> tier
  5. pack       evidence pack (JSON + Markdown + HTML): what was checked and by whom, what wasn't and why, residual risk
  6. sign       named owner countersigns the pack (Ed25519); append to the hash-chained ledger
  7. trust      per-area trust ledger: spot-checks earn clearance rights, escapes (revert/incident) withdraw them
```

## Repo layout

```
countersign/                Python package (CLI: `python -m countersign ...` or `countersign ...`)
mandate/messagepack.mandate.yaml   the review mandate for the MessagePack-CSharp repo
requirements/<change>.yaml   requirement set with IDs (from Tieto; placeholder until pasted)
evidence/<change>/facts.json deterministic check results (+ raw logs in evidence/<change>/logs/)
reviews/<change>/claude.json, codex.json   structured reviewer output (+ .md raw prose)
packs/<change>/pack.json, pack.md, pack.html   generated evidence pack
ledger/ledger.jsonl          append-only, hash-chained sign-off + trust events
keys/<name>.pub              public keys of named owners (private keys never committed; demo keys in .keys/, gitignored)
measurement/                 replay results (real vs simulated clearly marked)
```

`<change>` is the short id: `2283`, `2234`, `2129`, `2297` (branches `ju26-issue-<n>`), and seeded variants like `2283-mut1`.

## Tiers

- `silent`: meets the standard, cleared by the AI, logged only.
- `notify`: cleared by the AI, FYI to the area owner.
- `ask`: routed to the named owner with the evidence pack; owner must countersign.
- `block`: refused; the rule that fired is cited. Must be fixed or split before review.

The tier is the **strictest** of: the risk tier, any mandate rule that fires, the area's trust cap, and the refusal rule (any refused requirement clause -> at least `ask`).

## facts.json (stage 1, deterministic)

```json
{
  "change": "2283",
  "branch": "ju26-issue-2283",
  "base": "32258fdb", "head": "9df83c38",
  "commit_message": "implementation for #2283",
  "author": "Stelian Vultur", "agent_written": true,
  "diff": {"files": 4, "insertions": 225, "deletions": 3,
           "by_file": [{"path": "src/...TypeCollector.cs", "ins": 26, "del": 3, "kind": "source|test|doc|generated|build"}]},
  "checks": [
    {"id": "build", "tool": "dotnet build", "tool_version": "8.0.402", "status": "pass|fail|skipped|error",
     "summary": "0 errors, 0 warnings", "log": "evidence/2283/logs/build.log", "duration_s": 61.2},
    {"id": "tests.targeted", "tool": "dotnet test", "status": "pass", "summary": "12 passed, 0 failed",
     "tests": [{"name": "Full.Test.Name", "outcome": "passed|failed|skipped", "new": true}], "log": "..."},
    {"id": "tests.fail_without_fix", "tool": "dotnet test (source reverted, tests kept)", "status": "pass",
     "summary": "new tests fail on base source: 5/6 failed -> tests do cover the change"},
    {"id": "tests.full_suite", "status": "pass|fail|skipped", "summary": "..."},
    {"id": "public_api", "status": "pass", "summary": "no public API changes"},
    {"id": "analyzers", "status": "pass", "summary": "no new warnings"}
  ],
  "not_run": [{"id": "benchmarks", "reason": "no perf-sensitive path touched"}]
}
```

`status` meanings: `pass` (check ran and passed), `fail` (ran and failed), `skipped` (deliberately not run; must have a reason), `error` (could not run: the check itself broke). `error` and `skipped` are never treated as `pass`.

## reviews/<change>/<reviewer>.json (stage 2)

```json
{
  "reviewer": "claude", "model": "claude-opus-5-5", "vendor": "Anthropic",
  "prompt_version": "review-v1", "reviewed_at": "2026-11-14T01:30:00+02:00",
  "inputs": ["diff", "facts.json", "requirements/2283.yaml"],
  "requirement_verdicts": [
    {"req": "REQ-2283-F1", "verdict": "met|not_met|cannot_determine",
     "confidence_basis": "why, in one sentence, tied to evidence",
     "evidence": [ /* evidence items, see below */ ]}
  ],
  "findings": [
    {"id": "C1", "title": "...", "severity": "blocker|major|minor|info",
     "category": "correctness|security|performance|maintainability|docs|tests|scope",
     "claim": "what is wrong and why it matters",
     "evidence": [ /* at least one item */ ],
     "suggested_fix": "optional"}
  ],
  "refusals": [
    {"topic": "what the reviewer won't decide", "reason": "why (missing evidence, out of competence, needs runtime behaviour, etc.)",
     "who_should_decide": "role, e.g. area owner / security champion"}
  ]
}
```

Evidence item kinds (the engine verifies each one):

```json
{"kind": "code", "file": "src/.../TypeCollector.cs", "line": 1442, "rev": "head|base", "quote": "exact substring of that line"}
{"kind": "test", "name": "Full.Test.Name", "outcome": "passed|failed"}      // must match facts.json
{"kind": "check", "id": "tests.fail_without_fix"}                            // must exist in facts.json
{"kind": "requirement", "req": "REQ-2283-F1", "quote": "clause text"}        // must match requirements file
{"kind": "issue", "url": "https://github.com/MessagePack-CSharp/MessagePack-CSharp/issues/2283", "quote": "..."}
```

## Verification and decision rules (stages 3-4)

- A `code` item is verified if `file` exists at `rev` and `quote` occurs on `line` (±3 lines tolerance, recorded). A `test`/`check` item must exist in facts.json with the same outcome. A `requirement` quote must occur in the requirement text.
- A finding with **zero verified evidence** is rejected (kept in the pack under "rejected: unsupported claims", counted as a hallucination signal for that reviewer).
- Per requirement clause: **proven** only if both reviewers say `met` with verified evidence AND the clause's mandated deterministic checks pass. Otherwise **refused**, with a machine reason: `reviewers_disagree`, `cannot_determine`, `thin_evidence`, `check_failed`, `check_not_run`, `not_met`.
- Severity `blocker` finding verified by any reviewer -> tier at least `ask`; verified by both or backed by a failing check -> `block`.

## Risk score (explainable, additive)

Each factor adds points and a one-line reason; the pack prints the table. Weights live in the mandate, not in code.
Factors: area sensitivity (e.g. generator/analyzer core vs docs), files and lines changed, generated-file count, public API change, test delta (source changed without tests -> points), security-sensitive paths (deserialization, unsafe code), tests-fail-without-fix not shown, reviewer disagreement count.
Score bands map to tiers via mandate thresholds.

## Signing and ledger (stage 6)

- `countersign sign packs/<change>/pack.json --as <owner>` shows the sign-off card (checked by whom, not checked and why, residual risk), requires the owner to type the decision (`accept` / `reject` / `request-changes`) and an optional note, signs `sha256(canonical pack JSON) + decision + timestamp + signer` with the owner's Ed25519 key, and appends to `ledger/ledger.jsonl`.
- Ledger entry: `{"seq", "ts", "type": "signoff|spotcheck|escape|mandate_change", "payload": {...}, "prev": "<sha256 of previous line>", "hash": "<sha256 of this entry without hash>", "sig": "<base64 ed25519>", "signer": "<name>"}`.
- `countersign verify-ledger` re-checks the chain and every signature.

## Trust ledger (stage 7)

Per area (from the mandate), derived purely from ledger events:
- `spotcheck`: a human re-reviews a change the AI cleared (`silent`/`notify`) and records agree / disagree.
- `escape`: a revert or incident traced to a change; if the AI had cleared it, the area's clearance right drops (e.g. `silent` -> `ask`) and a probation counter starts.
- Clearance right is earned back after N consecutive agreeing spot-checks (N in the mandate).
- `countersign trust` prints each area's current cap, with the events that set it.
