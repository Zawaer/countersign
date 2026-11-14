# Countersign

**Demo:** open [site/index.html](site/index.html) in a browser (it goes on GitHub Pages once the repo is public).

> **AI reviews agent-written code under a mandate. It clears what it can prove, refuses what it can't, and a named human countersigns the rest.**

**In numbers:** replayed on 109 real merged MessagePack-CSharp PRs, the signed mandate would have let the AI clear 24 of them, and none of the 11 that later needed a revert or a follow-up fix. On Tieto's four agent-written changes it sent all four to a named owner, each with its reason.

**Three words used throughout:**
- **Mandate:** a signed, versioned file per repo that says, area by area, how far the AI may go alone and who owns each area.
- **Tier:** where a change goes. `silent` (the AI clears it, logged), `notify` (the AI clears it and tells the owner), `ask` (the owner must sign), `block` (fix or split first).
- **Escape:** a change that was merged and later needed a revert or a follow-up fix.

## How it works

0. **A failing check can't be argued away.** If a check the mandate requires fails, no reviewer, adjudicator or trust record can clear the change. This is enforced in code.
1. **Facts first.** Build, tests, "do the new tests fail without the fix?", public API, analyzers, dependency changes and a scan for text planted for AI reviewers run before any model reads the diff.
2. **Three reviewers, unanimity.** Claude, Codex and Nemotron review separately. Every claim must cite a file line, test, check or requirement clause, and the engine re-checks it. A clause is proven only if all three say "met" with verified evidence and its checks pass; anything else is refused, with the reason.
3. **Bugs a reviewer claims are re-run.** A reviewer's probe test becomes a repro check that the pipeline runs on the old and new code.
4. **The change explains itself.** An evidence pack: tier and why, requirement trace, findings, refusals, what was not checked, residual risk.
5. **A named owner countersigns.** An Ed25519 signature over the pack's hash, in a hash-chained ledger.
6. **Trust is earned per area.** An area moves from ask to notify after 20 agreeing spot-checks in a row, and to silent after 40. An escape, a disagreeing spot-check or a missed seeded-bug canary drops the area one stage. A new reviewer model or prompt version starts again at ask.

One page: [docs/CONCEPT_CARD.md](docs/CONCEPT_CARD.md). Rules a team could adopt: [docs/PRINCIPLES.md](docs/PRINCIPLES.md).

## Walkthrough: change 2234

Branch `ju26-issue-2234`, written by an agent: "The analyzer does not work if `SuppressSourceGeneration = true`". 4 files, +262 −4. Requirements `REQ-2234-F1`, `F2`, `N1`, `N2` in [requirements/2234.yaml](requirements/2234.yaml).

1. **Route.** `countersign route --all` prints one line per change. 2234 goes to `ask`, owner Toivo, because of a verified finding: the issue's regression is not on this base, and the change fixes a different crash.
2. **Open the pack.** [packs/2234/pack.md](packs/2234/pack.md) ([html](packs/2234/pack.html)). The first screen is the tier, the owner and why.
3. **Read the facts.** Build passes, the 8 new analyzer tests pass, the suite passes 175 of 175. But with the fix reverted, only 4 of the 8 new tests fail, and 0 of the 4 new runtime tests fail. So clauses F1 and F2 are marked **held before**: met, but already true without this change ([facts.json](evidence/2234/facts.json)).
4. **What the AI found.** Claude C1 (major): the reported regression comes from upstream commit `1a74a620`, which is not in this branch's base. Claude C2 (minor): `Key(null)` on a positional record still crashes the analyzer. The pipeline ran Claude's probe as `repro.claude.C2`: it fails on the new and old code and passes on a control branch, so the crash is reproduced, not just claimed.
5. **What the AI refused to decide.** N1 ("must not crash on invalid contracts"): Claude says not met, Codex and Nemotron say met, so it is not proven. N2: Codex said met without verified evidence. Whether this fixes #2234 for 3.1.x users: nothing was built on that release line, so it is the owner's call.
6. **What was not checked.** Other .NET targets, the runtime library's tests, benchmarks, and the mandate's standing gaps. The risk score prints every point with its reason.
7. **Sign.** `countersign sign 2234 --as Toivo --decision request-changes --note "..."`. Only the named owner's key is accepted, and signing is refused if the pack changed. Toivo's private key is not in the repo.
8. **Try to tamper.** Copy `ledger/` to `/tmp/t`, edit one line, run `countersign verify-ledger --inputs /tmp/t`: `LEDGER INVALID: line 2: content does not match its hash`.

Nobody read 262 lines. The owner still learned that the change fixes a different bug, that half its tests prove nothing, which clause the reviewers disagree on, and what they are signing for.

## All seven real changes

Four were written by an agent (Tieto's branches). Three are small merged upstream PRs we added as controls, to show that a low-risk change can go through.

| Change | Size | Tier | The deciding reason |
|---|---|---|---|
| [2283](packs/2283/pack.md) | 4 files, +225 −3 | `ask` | The fix silences a warning (MsgPack003) that the old code reports. Claude found it; the pipeline reproduced it (`repro.claude.C1`). |
| [2234](packs/2234/pack.md) | 4 files, +262 −4 | `ask` | It fixes a different crash than the issue reports. |
| [2129](packs/2129/pack.md) | 28 files, +1034 −9 | `block` | New public API with no API tracking, a new analyzer warning and a project missing from the solution: two failed checks in a critical area push the risk score into the block band. |
| [2297](packs/2297/pack.md) | 237 files (228 generated), +1383 −9 | `block` | More than 50 files: split it. A reviewer also found a wrong `#if` that leaves .NET Framework and netstandard users without the attribute. |
| [up-2022](packs/up-2022/pack.md) | 2 files, +29 −0 | `ask` | All clauses proven, but Nemotron refused to judge runtime deserialization security, a topic on the mandate's list of terms that always ask. |
| [up-1934](packs/up-1934/pack.md) | 6 test files, +26 −22 | `ask` | All clauses proven, but Nemotron refused to judge the build on other target frameworks, and `build` is a mandated check. |
| [up-1967](packs/up-1967/pack.md) | 1 doc file, +1 −1 | `notify` | A one-line README anchor fix. All three reviewers agree and the anchor check passes, so the AI clears it and tells Rene. |

6 of 7 go to a human. The AI clears only the docs fix.

## Measurement

Details and definitions: [docs/MEASUREMENT.md](docs/MEASUREMENT.md).

- **History (real).** 109 merged upstream PRs, routed from their diffs by the signed mandate. 11 were later reverted or needed a follow-up fix. The AI would have cleared 24 PRs, and **0 of the 11 escapes** ([measurement/history/results.md](measurement/history/results.md)).
- **Seeded bugs (real).** We planted 14 one-line bugs and 2 prompt-injection changes. Checks alone catch 13 of 16 (11 of 14 bugs and both injections; R-INJECT blocks both). Of the 3 bugs every test missed, Nemotron's blind review points at the planted line in 2 and misses the removed `ContainsSyntaxTree` guard on 2283, which reviewers also called fine on the original.
- **Review time (simulated).** A reading model in the mandate, not a stopwatch: about 440 minutes to read all seven diffs, 185 with the packs. On small changes the pack takes longer than the diff.
- **Trust over time (simulated).** When reviewers get worse, the old rule (3 agreeing spot-checks restore clearance) let escapes rise. 20 checks plus weekly canaries brought them back to the full-review level. That result changed the signed mandate (v3).

## What is real, recorded and simulated

- **Real:** branches, diffs, every build and test result in `evidence/` (with logs), repro checks, seeded bugs, verification, routing, packs, signatures, the ledger, the history replay.
- **Recorded:** Claude and Codex reviews, run in agent sessions and saved verbatim in `reviews/`. Nemotron reviews were run live by the CI job on CRACI, with the request and response saved under `reviews/<change>/raw/`.
- **Simulated, and labelled:** spot-checks, escapes and canaries over time, and every review-time number.
- **Placeholder:** the requirement sets. We derived them from each upstream issue and marked them `official: false`.

## Limits

- It can't judge **intent**: whether this is the change the product needs.
- It is only as good as the **requirement text**.
- **Breadth equals the checks.** We have checks for a C# library on net8.0/Linux. Frontend, performance and other targets fall back to humans and are listed as not checked.
- **Reviewers share blind spots.** Claude and Codex both read the untested 2283 guard as fine.
- **The merge gate can be forged in the demo.** Any GitHub Actions workflow in the demo repo can post the required status. The fix is a dedicated GitHub App ([docs/security/TRIAGE.md](docs/security/TRIAGE.md), T1).
- Gemini adjudication has not run, so disputes in the packs say "not adjudicated". Key rotation and revocation are out of scope.

## Tech tracks

- **Codex (OpenAI):** a reviewer on all seven changes. Its second pass, given passing tests, said every clause was met and found nothing; the rules are built so that can't clear a change ([docs/CODEX_LOG.md](docs/CODEX_LOG.md)). Codex also did a security review of our own pipeline; the triage confirmed real issues and fixed them, except the merge-gate one above ([docs/security/TRIAGE.md](docs/security/TRIAGE.md)).
- **Gemini (Google):** the adjudicator. It reads only disputed items with both sides' evidence; the engine never lets it clear anything (`decide.apply_adjudication`). Wired, runs when the key is set; not yet run.
- **Nemotron (NVIDIA, open weights):** the third reviewer, run live in CI on all seven real changes and all 16 seeded changes. It is the only reviewer marked self-hostable, so it is the one a repo marked confidential may use.
- **CRACI:** the pipeline and the reviewer jobs run on CRACI runners under a deny-by-default network policy. The facts job also writes `deps.delta` (a CycloneDX SBOM diff of the NuGet graph, base vs head; passes on all four changes, fails on a seeded attack on 2283) and `build.egress` (copies the build's network policy into the evidence; wired, no committed run yet). See [docs/CI.md](docs/CI.md).

## Run it

Python 3.11+ and git. Offline, no API keys: it reads the recorded facts and reviews.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'
git clone https://github.com/te-industry-tech-office/junction26-messagepack-csharp /tmp/mp
countersign route --all --repo /tmp/mp   # tier per change
countersign review 2234 --repo /tmp/mp   # rebuild packs/2234
countersign verify-ledger                # check every signature
countersign trust                        # trust stage per area
pytest -q
```

More: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PR_FLOW.md](docs/PR_FLOW.md) (GitHub flow: merge blocked until a valid countersignature), [docs/DECISIONS.md](docs/DECISIONS.md), [docs/FAILURE_MODES.md](docs/FAILURE_MODES.md), [docs/LESSONS.md](docs/LESSONS.md), [docs/COSTS.md](docs/COSTS.md).

Team: Toivo and Rene.
