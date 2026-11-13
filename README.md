# Countersign

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

Junction 2026 entry for Tieto's challenge **"Earned Trust in AI Code"**. A concept plus a reference implementation (not a product), run on the four agent-written changes to MessagePack-CSharp that Tieto provided.

## The problem

Agents now write more code than people can read line by line, and the person whose name is on the approval still answers for it. "The AI reviewed it" is not something a person can stand behind; evidence they can check, and a written record of what they accepted, is.

## The concept in seven lines

1. **Mandate.** A signed, versioned file per repo and area says what the AI may clear alone (`silent`, `notify`), what goes to a named owner (`ask`) and what is refused (`block`).
2. **Facts first.** Build, tests, "do the new tests fail without the fix?", public-API and analyzer checks run before any model reads the diff.
3. **Independent reviewers.** Models from different vendors review separately; every claim must cite a file line, a test, a check or a requirement clause, and the engine re-checks each citation.
4. **Disagreement means refusal.** A requirement clause is proven only if every reviewer says "met" with verified evidence and its checks pass. Anything else is refused, with the reason.
5. **The change explains itself.** An evidence pack: tier and why, requirement trace, findings, refusals, what wasn't checked, residual risk.
6. **A named owner countersigns.** Ed25519 signature over the pack hash, in a hash-chained ledger.
7. **Trust per area.** Spot-checks earn the AI clearance rights; an escape (revert, incident) withdraws them at once.

One page: [docs/CONCEPT_CARD.md](docs/CONCEPT_CARD.md). Rules a team could adopt: [docs/PRINCIPLES.md](docs/PRINCIPLES.md).

---

## Walkthrough: where the trust comes from (change 2234, about 5 minutes)

**The change.** Branch `ju26-issue-2234`, written by an agent: "The analyzer does not work if `SuppressSourceGeneration = true`". 4 files, +262 −4. Requirements `REQ-2234-F1`, `F2`, `N1`, `N2` ([requirements/2234.yaml](requirements/2234.yaml); our placeholders derived from the upstream issue, marked `official: false`).

### 1. Where does it go? (30 s)

```bash
countersign route --all --repo /tmp/mp    # setup: see "How to run" below
```

One line per change: tier, risk score, owner, and the rule that decided it. 2234 goes to `ask`, owner Toivo. The deciding driver is a verified finding: *the issue's 3.1.1 regression is not on this base; the change fixes a different crash.*

### 2. Open the pack (30 s)

[packs/2234/pack.md](packs/2234/pack.md) (or [pack.html](packs/2234/pack.html), which works on a phone). The first screen is the tier, the owner, and **"Why this tier"**: every driver that put it at `ask`, strictest first. You are checking a story, not hunting through a diff.

### 3. The facts nobody has to trust a model for (1 min)

[evidence/2234/facts.json](evidence/2234/facts.json), shown in the pack under "What was checked, and by whom".

- Build passes; 8 new analyzer tests pass; the full generator suite passes (175 of 175).
- **Fail-without-fix:** revert the source, keep the new tests, run them. Only **4 of the 8** new analyzer tests fail. The other 4 pass on the old code: they test behaviour the base already had.
- The 4 new runtime tests: **0 of 4** fail without the fix (`tests.execution_fail_without_fix: fail`).

Everything is green, but 8 of the 12 new test results pass without the change. That is the first thing that doesn't add up.

### 4. What the AI found, and how you can check it (1 min)

Pack section "What the AI found (verified findings)". Raw reviews: [reviews/2234/claude.md](reviews/2234/claude.md), [reviews/2234/codex.md](reviews/2234/codex.md).

- **claude:C1 (major):** the regression the issue reports was introduced by upstream commit `1a74a620`, which is not in this branch's base. The agent's code is sound, but it fixes a different, pre-existing crash on duplicate or mixed keys. Merged into the release line where users hit the bug, the issue stays open.
- **claude:C2 (minor):** one invalid contract (`Key(null)` on a positional record) still crashes the analyzer.
- Every citation carries `[OK]` or `[REJECTED]`: the engine re-read that file at that commit and found the exact quote, or matched the test name and outcome in facts.json. The link to the GitHub issue is marked rejected because the pipeline runs offline and can't confirm what the page says.

### 5. What the AI refused to decide, and why (1 min)

Pack sections "What the AI refused to decide" and "Requirement trace".

- **REQ-2234-N1** ("must not crash on invalid contracts") is **refused**: Claude says `not_met` (it reproduced the crash), Codex says `met`. Reasons printed: `not_met`, `reviewers_disagree`.
- **Whether this fixes #2234 for 3.1.x users** is refused by the reviewer: nothing was built on that release line, so it is a release decision for the owner.
- TODO(numbers): once the Nemotron reviews and the Gemini adjudication are committed, re-check this section. Today every clause also shows `missing_review: nemotron`, because a reviewer that hasn't run can never silently drop out.

### 6. What wasn't checked, and the risk that is left (30 s)

Pack sections "What was not checked, and why" and "Residual risk": the .NET Framework / netstandard build, the runtime library's own tests, benchmarks, and the mandate's standing gaps (other targets, performance, intent, provenance). The **risk score** table prints every point and its reason; nothing in it is a black box.

### 7. The owner countersigns (30 s)

The pack ends with the sign-off statement and the command:

```bash
countersign sign 2234 --as Toivo --decision request-changes --note "Fixes a real crash, not #2234. Retarget, add a test for Key(null)."
```

`sign` only accepts the pack's named owner, rebuilds the pack first and refuses if it changed, and appends `{pack sha256, mandate sha256, decision, note}` with an Ed25519 signature to [ledger/ledger.jsonl](ledger/ledger.jsonl). Toivo's private key is not in the repo by design, so you can't sign as him. TODO(numbers): link the committed 2234 sign-off entry (`packs/2234/signoff.json`) once Toivo signs.

### 8. Try to tamper with the record (30 s)

```bash
countersign verify-ledger                 # ledger OK: hash chain intact, every signature verifies
mkdir -p /tmp/t && cp -r ledger /tmp/t/
sed -i 's/"version": "2"/"version": "3"/' /tmp/t/ledger/ledger.jsonl
countersign verify-ledger --inputs /tmp/t # LEDGER INVALID: line 2: content does not match its hash
```

### 9. Trust per area (30 s)

```bash
countersign trust
```

Each area's clearance right from the mandate and from the ledger. Generator/analyzer core may be cleared by the AI up to `notify`; an escape traced to an AI-cleared change drops it to `ask` until three spot-checks in a row agree. TODO(numbers): add the simulated escape-and-recovery run once it is recorded.

**What you just saw:** nobody read 262 lines, and the owner still learned that the change's title and its effect don't match, which half of its tests prove nothing, which clause the reviewers disagree on, and exactly what they are signing for.

---

## Results on all four changes

| Change | Size | Tier | Why |
|---|---|---|---|
| [2283](packs/2283/pack.md) | 4 files, +225 −3 | `ask` | A reviewer reproduced a regression: the new filter silences a warning (MsgPack003) that the base reports. And a guard the fix depends on is never tested: a seeded defect that removes it passes the whole suite. |
| [2234](packs/2234/pack.md) | 4 files, +262 −4 | `ask` | Sound code that fixes a different bug than the issue reports; 4 of 8 new tests pass without the change; reviewers disagree on the no-crash clause. |
| [2129](packs/2129/pack.md) | 28 files, +1034 −9 | `block` | New public API in a project without API tracking, a new analyzer warning, a new project not in the solution: two failed checks in a critical area push the risk score past the block band. |
| [2297](packs/2297/pack.md) | 237 files (228 generated), +1383 −9 | `block` | More than 50 files: split it. Inside, a reviewer found a wrong `#if` that leaves .NET Framework and netstandard users without the attribute, and an unrelated whitespace edit rode along with the regenerated snapshots. |

All four route to a human; none is cleared by the AI. That is expected for a repo with no track record yet (the mandate starts strict). Seeded defects: we planted 14 single-line bugs of five kinds (removed guard, inverted condition, swallowed diagnostic, wrong key kind, off-by-one) into the 2283, 2234 and 2129 changes to measure what gets caught ([measurement/mutants/mutants.json](measurement/mutants/mutants.json)). TODO(numbers): how many the checks alone catch, how many the full pipeline routes to a human, the share of real changes routed to humans and the simulated review minutes, all from `measurement/results.md` once the replay is committed.

Failure modes we saw: [docs/FAILURE_MODES.md](docs/FAILURE_MODES.md). Decision log: [docs/DECISIONS.md](docs/DECISIONS.md). Lessons: [docs/LESSONS.md](docs/LESSONS.md).

---

## How to run it

Needs Python 3.11+ and git. Everything except the optional live model calls runs offline with no API keys: it reads the recorded facts and reviews in this repo.

```bash
git clone https://github.com/Zawaer/countersign && cd countersign
python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'

# the code under review, for re-checking code citations
git clone https://github.com/te-industry-tech-office/junction26-messagepack-csharp /tmp/mp   # has the ju26-issue-* branches

countersign route --all --repo /tmp/mp       # tier per change
countersign review 2234 --repo /tmp/mp       # rebuild packs/2234/pack.{json,md,html}
countersign verify-ledger                    # check every signature in the ledger
countersign trust                            # clearance rights per area
countersign replay --repo /tmp/mp            # measurement over changes + seeded defects
pytest -q                                    # engine tests

# optional, needs an API key in the environment: a live model review / adjudication
NVIDIA_API_KEY=... countersign review-llm 2234 --reviewer nemotron --repo /tmp/mp
GEMINI_API_KEY=... countersign adjudicate 2234 --repo /tmp/mp
```

`--inputs tests/fixtures` runs the same commands on a separate, fully simulated world (every file there says `"simulated": true`). Rebuilding the facts themselves (.NET builds and tests) is documented step by step in [evidence/README.md](evidence/README.md).

## Repo map

| Path | What it is |
|---|---|
| `mandate/messagepack.mandate.yaml` (+ `.sig`) | The review mandate: areas, owners, clearance rights, rules, risk weights, reviewer panel. Signed by Toivo. |
| `requirements/<change>.yaml` | Requirement clauses per change (placeholders from the upstream issues). |
| `evidence/<change>/facts.json` + `logs/` | Stage 1: deterministic checks. `evidence/README.md` says how they were produced. |
| `evidence/<change>-mutK/`, `measurement/mutants/` | Seeded single-line defects and their catalogue, for measuring what gets caught. |
| `measurement/` | Replay results and the spend ledger (`costs.yaml`, rendered as [docs/COSTS.md](docs/COSTS.md)). |
| `prompts/` | The versioned reviewer and adjudicator prompts. |
| `.github/workflows/countersign.yml` | CI on CRACI runners: pipeline job and reviewers job. |
| `reviews/<change>/` | Stage 2: each reviewer's structured JSON and prose. `*.v1.*` are earlier passes, kept for comparison. |
| `packs/<change>/pack.{json,md,html}` | Stages 3-5: verified, decided, rendered evidence pack. |
| `ledger/ledger.jsonl` | Append-only, hash-chained, signed sign-offs, spot-checks, escapes and mandate changes. |
| `keys/*.pub` | Owners' public keys (private keys are never committed). |
| `countersign/` | The Python engine: `verify.py`, `decide.py`, `pack.py`, `ledger.py`, `trust.py`, `measure.py`, `llm.py` (reviewer runner), `cli.py`. |
| `tests/` | Engine tests and a simulated fixture world. |
| `docs/` | Concept card, principles, architecture, decisions, failure modes, lessons, Codex log, pitch material. |

## What is real, recorded, and simulated

- **Real:** the four agent-written branches and their diffs; every build and test result in `evidence/` (run by us with .NET SDK 8.0.402, and 9.0.321 for the execution tests, logs included); the seeded defects and their test outcomes; the engine's verification, routing and packs; the Ed25519 signatures and the ledger.
- **Recorded:** the AI reviews. Claude and Codex reviewed each change in agent sessions; their output is saved verbatim in `reviews/` and ingested by the pipeline, which does not call those models itself. Every Codex run is logged in [docs/CODEX_LOG.md](docs/CODEX_LOG.md). The Nemotron reviews and Gemini adjudication are produced by the CI reviewers job, which calls the APIs live and records exactly what was sent and received under `reviews/<change>/raw/`. TODO(numbers): confirm once that job has run.
- **Simulated, and labelled so:** spot-checks and escapes in the trust demo (there is no production history), and every review-time estimate (it comes from a reading-speed model in the mandate, not a stopwatch).
- **Placeholder:** the requirement sets. We couldn't find Tieto's official set, so ours are derived from each upstream issue and marked `official: false`.

## Limits

- It can't judge **intent**: whether this is the change the product needs.
- It is only as good as the **requirement text**. A clause can already hold before the change (2234 F2), and the trace still says "met".
- **Breadth is as wide as the checks.** We have build, tests, fail-without-fix, public API and analyzers for a C# library. Frontend, performance and security-specific checks would plug into the same facts stage but don't exist here; those areas fall back to humans and are listed as not checked.
- Everything ran on **net8.0 / Linux**. .NET Framework, netstandard, Unity and NativeAOT paths were not built or tested.
- **Reviewer independence is partial.** Models share training data; both reviewers read the untested 2283 guard as fine.
- **Key management** (rotation, revocation) is out of scope.

## Team and tech tracks

Team: Toivo and Rene. Toivo is also the demo's named owner for code areas; Rene owns docs and build.

- **Codex (OpenAI):** the second-vendor reviewer. Two read-only review passes over all four changes (before and after the deterministic facts existed); both kept, and the difference between them is our clearest failure mode (evidence made it agree with everything). Logged in [docs/CODEX_LOG.md](docs/CODEX_LOG.md).
- **Gemini (Google):** the adjudicator in the mandate's reviewer panel. It reads only disputed items with both sides' evidence and says which claims the evidence supports. The engine enforces that it can never clear anything (`decide.apply_adjudication`). TODO(numbers): link `reviews/2234/adjudication.gemini.json` once it is run; today the pack says "2 disputed items, not adjudicated".
- **Nemotron (NVIDIA, open weights):** the third reviewer, and the only one marked `self_hostable` in the mandate, so it is the reviewer a confidential repo would be allowed to use. TODO(numbers): link `reviews/<change>/nemotron.json` once the CI run lands; until then packs show `missing_review: nemotron`.
- **CRACI:** the pipeline runs as a GitHub Actions job on CRACI runners ([.github/workflows/countersign.yml](.github/workflows/countersign.yml)): engine tests, ledger verification, routing, and a check that the committed packs rebuild byte for byte, under a deny-by-default network policy with actions pinned to commit SHAs. A second job (manual) runs the Nemotron reviews and the Gemini adjudication with the API keys as secrets. The first pipeline run on CRACI passed (run 43530101073); the reviewers job had not run yet. TODO(numbers): add the reviewers run and the SBOM/egress trace link once it exists.
